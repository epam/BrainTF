HELP_MESSAGE: str = """
:information_source: AI Bot message

---

Comment Commands Help

---

This system supports structured comment commands to trigger automation.

Below is a guide to the supported commands:

`bot approve *` or `bot approve all` - triggers the approval of committing **all** files fixed by AI bot.

`bot approve <path/to/file1> [<path/to/file2> ...]` - triggers the approval of committing a **specific file** or **files** fixed by AI bot.

`bot list` - lists **all** files corrected by AI and ready to commit.

`bot show` - shows the content of **all** files corrected by AI and ready to commit.

`bot show <path/to/file1> [<path/to/file2> ...]` - shows the content of a **specific file** or **files** corrected by AI and ready to commit.

`bot diff` - shows colored diffs between **all** files corrected by AI and their current versions in the branch.

`bot diff <path/to/file1> [<path/to/file2> ...]` - shows colored diffs for a **specific file** or **files** corrected by AI.

`bot prompt <user prompt>` - sends custom prompt to AI.

`help` - shows this help information in the {spec_provider}.

---

> :warning: Notes:
>
> All commands must begin with a **context word** (`bot`, `help`, etc.).
>
> Only `bot` context supports nested command logic (e.g. `approve`).
""".lstrip().removesuffix("\n")

LIST_FILES_MESSAGE: str = """
:information_source: AI Bot message

---

List of files corrected by AI bot

---

{files_list}

---

""".lstrip().removesuffix("\n")

SHOW_FILES_MESSAGE: str = """
:information_source: AI Bot message

---

Content of files corrected by AI bot

---

<details>
<summary>Show content of files corrected by AI bot</summary>

<br>

{files_list}
</details>

---

""".lstrip().removesuffix("\n")

DIFF_FILES_MESSAGE: str = """
:information_source: AI Bot message

---

Diff between files corrected by AI bot and files in the branch

---

<details>
<summary>Show diffs of files corrected by AI bot</summary>

<br>

{files_list}
</details>

---

""".lstrip().removesuffix("\n")

UNAVAILABLE_APPROVAL_FILES_MESSAGE: str = """
:information_source: AI Bot message

---
> :no_entry: Not available\\
> The following files are not available for approval: **{unavailable_files}**.\\
> Comment `bot list` to see corrected files currently available for approval.
""".lstrip().removesuffix("\n")

FILES_NOT_IN_REPO_MESSAGE: str = """
:information_source: AI Bot message

---
> :no_entry: Not available\\
> The following files do not exist in the repository: **{files}**.\\
> BrainTF cannot create new files in the repository; it can only modify existing ones.
""".lstrip().removesuffix("\n")

NO_APPROVAL_FILES_MESSAGE: str = """
:information_source: AI Bot message

---
> :no_entry: Not available\\
> There are no corrected files available for approval.\\
> Comment `bot list` to check available files.
""".lstrip().removesuffix("\n")

AI_RESPONSE_MESSAGE: str = """
:information_source: AI Bot message

---

Response from AI

---

<details>
<summary>Show AI suggestions and fixed files</summary>

{ai_response}
</details>

---

<details>
<summary>Show tokens usage</summary>

:arrow_down: **Total tokens:** `{total_tokens}`

:arrow_double_down: Prompt tokens: `{prompt_tokens}`

:arrow_double_up: Completion tokens: `{completion_tokens}`
</details>

""".lstrip().removesuffix("\n")

SYSTEM_ROLE_MESSAGE: str = """
You are a highly skilled assistant specializing in Infrastructure as Code (IaC), cloud automation, and DevOps practices using AWS as the cloud provider. You are proficient in tools such as Terraform, Terragrunt, and TFLint, and your role is to provide accurate, detailed, and practical guidance to system engineers. Follow these principles strictly:

1. **Error Identification and Explanation**:
   - ALWAYS analyze the provided code or configuration files for errors or warnings.
   - Briefly describe each error or warning, including its cause and possible solution.

2. **Code Snippet for Fixes**:
   - ALWAYS provide a code snippet that directly addresses the error or warning.
   - Include only the relevant block of code that needs correction.

3. **Full Corrected File(s)**:
   - ALWAYS provide the full content of every corrected file at the END of your response.
   - Use the following strict format for each corrected file:
     - Start with the line: Corrected file `<relative_path_to_file>` — the path MUST always be enclosed in backticks.
     - ALWAYS add a single blank line immediately after this line, with no other text in between.
     - Then include the full corrected file content inside a code block, using triple backticks (` ``` `) with the `hcl` language identifier.

     The corrected file format MUST look like this:
     Corrected file `<relative_path_to_file>`

     ```hcl
     <file content>
     ```

   - If more than one file needs correction, repeat this exact marker-plus-code-fence pattern once per file, back to back, at the end of your response — one complete block per file.
   - Never wrap your entire response, or any "Corrected file" block, inside an outer code fence, and never let a stray triple-backtick fence appear inside a corrected file's content — either breaks how your response is parsed.

4. **Scope of Correction**:
   - ONLY correct source files directly related to the error or warning messages.
   - Do not modify unrelated parts of the code unless explicitly instructed.

5. **Clarity and Practicality**:
   - Provide concise, actionable solutions that align with best practices in DevOps and AWS.
   - Use clear and consistent formatting to ensure readability.

6. **Proactive Assistance**:
   - If the user’s input is incomplete or ambiguous, ask clarifying questions to ensure accurate guidance.
   - Suggest improvements to the overall configuration or approach when relevant.

Your primary goal is to provide system engineers with reliable, actionable solutions for IaC, cloud automation, and DevOps tasks, ensuring their configurations are error-free and optimized for AWS environments.

Before finishing your response, verify it contains exactly one "Corrected file" block, in the exact format above, for every file that needed a fix.
""".lstrip().removesuffix("\n")
