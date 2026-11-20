# BrainTF instance deployment — thin wrappers around scripts/deploy.sh and
# scripts/destroy.sh (the same steps deploy-braintf.yml / destroy-braintf.yml run).
#
#   make plan    INSTANCE_ID=vasjr   # dry run: resolve, config, init, plan
#   make deploy  INSTANCE_ID=vasjr   # deploy a personal instance
#   make destroy INSTANCE_ID=vasjr   # tear it down
#
# INSTANCE_ID defaults to your GitHub handle (gh api user / GITHUB_ACTOR),
# then to the current branch. See scripts/deploy.sh for all env toggles
# (CONFIG_SOURCE, TARGET_BRANCH, OWNER_GITHUB, PLAN_ONLY, AUTO_APPROVE).

export INSTANCE_ID TARGET_BRANCH OWNER_GITHUB CONFIG_SOURCE VCS_PROVIDER STATE_BUCKET STATE_REGION AUTO_APPROVE FORCE

.PHONY: deploy plan destroy

plan:
	@PLAN_ONLY=1 ./scripts/deploy.sh

deploy:
	@./scripts/deploy.sh

destroy:
	@./scripts/destroy.sh
