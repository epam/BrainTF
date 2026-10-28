#!/bin/bash
# Test for scripts/upload_and_comment.sh (GitHub branch) with stubbed curl and aws.
# Run: bash scripts/tests/test_upload_and_comment.sh

SCRIPT="$(cd "$(dirname "$0")/.." && pwd)/upload_and_comment.sh"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
FAILED=0

mkdir -p "$WORK/bin"
# curl stub: POST (-w) is logged and answered with 201, GET answers come from the STUB_* files
cat > "$WORK/bin/curl" <<'STUB'
#!/bin/bash
URL="${@: -1}"
for a in "$@"; do [ "$a" = "-w" ] && { echo "POST $URL" >> "$WORK/calls.log"; printf '201'; exit 0; }; done
echo "GET $URL" >> "$WORK/calls.log"
case "$URL" in
  */commits/*/pulls) cat "$WORK/commit_pulls.json" ;;
  */pulls/*)         cat "$WORK/pr_state.json" ;;
esac
STUB
cat > "$WORK/bin/aws" <<'STUB'
#!/bin/bash
echo "AWS $*" >> "$WORK/calls.log"
STUB
chmod +x "$WORK/bin/curl" "$WORK/bin/aws"
echo "terraform fmt found issues" > "$WORK/plain.log"
echo "full log" > "$WORK/full.log"

# run_case <name> <PR number passed to the script> <commit pulls json> <PR state json>
run_case() {
  NAME="$1"; PR_ARG="$2"; echo "$3" > "$WORK/commit_pulls.json"; echo "$4" > "$WORK/pr_state.json"
  : > "$WORK/calls.log"
  OUT=$(WORK="$WORK" PATH="$WORK/bin:$PATH" VCS_API_ENDPOINT="https://api.github.com" bash "$SCRIPT" \
    github both "$WORK/full.log" tflint.log my-bucket owner/repo owner feature abc123 token \
    refs/heads/main 1001 "$PR_ARG" role TFLint "$WORK/plain.log" https://job 2>&1)
  RC=$?
}

check() { # check <description> <condition result: 0=ok>
  if [ "$2" -eq 0 ]; then echo "  ✓ $1"; else echo "  ✗ $1"; FAILED=1; fi
}
calls_have() { grep -q -- "$1" "$WORK/calls.log"; }

echo "1. PR number supplied -> comment goes to this PR"
run_case one 45 '[]' '{"state":"open","merged_at":null}'
check "exit code 0" $((RC != 0))
check "comment posted to /issues/45/comments" $(calls_have "POST .*/issues/45/comments"; echo $?)
check "log uploaded to s3://my-bucket/45/" $(calls_have "AWS s3 cp .* s3://my-bucket/45/tflint.log"; echo $?)

echo "2. No PR number, merged PR found by commit -> comment goes to the merged PR"
run_case two "" '[{"number":7,"state":"closed","merged_at":"2026-10-20T10:00:00Z","updated_at":"2026-10-20T10:00:00Z"}]' '{"state":"closed","merged_at":"2026-10-20T10:00:00Z"}'
check "exit code 0" $((RC != 0))
check "PR looked up by commit abc123" $(calls_have "GET .*/commits/abc123/pulls"; echo $?)
check "comment posted to /issues/7/comments" $(calls_have "POST .*/issues/7/comments"; echo $?)
check "log uploaded to s3://my-bucket/7/ (not bucket//)" $(calls_have "AWS s3 cp .* s3://my-bucket/7/tflint.log"; echo $?)

echo "3. No PR number and no PR found -> skip, no error"
run_case three "" '[]' '{}'
check "exit code 0" $((RC != 0))
check "no comment posted" $(calls_have "POST"; test $? -ne 0; echo $?)
check "nothing uploaded to s3" $(calls_have "AWS"; test $? -ne 0; echo $?)

echo "4. PR closed without merge -> skip, no error"
run_case four 9 '[]' '{"state":"closed","merged_at":null}'
check "exit code 0" $((RC != 0))
check "no comment posted" $(calls_have "POST"; test $? -ne 0; echo $?)

echo
if [ "$FAILED" -eq 0 ]; then echo "ALL TESTS PASSED"; else echo "SOME TESTS FAILED"; exit 1; fi
