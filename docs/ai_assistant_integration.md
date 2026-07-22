# AI Assistant Integration

`devsetgo_lib` ships packaged, up-to-date integration instructions for AI
coding assistants (GitHub Copilot, Claude/Claude Code, or any other tool) that
are helping you add this library to an application. The instructions live in
code (`dsg_lib/ai_instructions.py`), not only in this documentation site, so
they stay in sync with the actual API and can be generated directly into your
application's repo.

## Generate instructions for your app

Run this from the application repo that depends on `devsetgo_lib` (not from
this repo):

```bash
# Print to stdout
python -m dsg_lib.ai_instructions

# Write to the filename convention each tool looks for by default
python -m dsg_lib.ai_instructions claude --write    # -> ./CLAUDE.md
python -m dsg_lib.ai_instructions copilot --write   # -> ./.github/copilot-instructions.md
python -m dsg_lib.ai_instructions generic --write   # -> ./AI_INSTRUCTIONS.md

# Or write to an explicit path (must resolve inside the current directory)
python -m dsg_lib.ai_instructions claude --output docs/ai/CLAUDE.md
```

The three profiles (`generic`, `copilot`, `claude`) carry the same
instructional content — only the destination filename convention and a
one-line header differ. Common aliases are also accepted (e.g. `anthropic`,
`chatgpt`, `gh-copilot`).

## Use it in-process

```python
from dsg_lib import get_app_instructions, suggested_instruction_filename

text = get_app_instructions("claude")
filename = suggested_instruction_filename("claude")  # 'CLAUDE.md'
```

## What the instructions cover

The generated document walks through every module's import path, its
error-handling model (which functions raise vs. return an error value),
and the non-obvious gotchas verified against the current source — e.g. that
`root_folder` must be repeated identically across `save_*`/`open_*`/
`delete_file` calls, that `folder_functions.make_folder` requires a
`pathlib.Path` (not a `str`) despite its type hint, and that
`DatabaseOperations` methods return a `DatabaseErrorResult` instead of
raising. It also flags which `DatabaseOperations` methods are deprecated
(`create_one`, `create_many`, `update_one`, `delete_one`, `delete_many`) in
favor of `execute_one`/`execute_many`.
