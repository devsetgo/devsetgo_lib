 AI Assistant Instructions — Implementation Playbook

A portable recipe for shipping packaged, verified AI-assistant integration
instructions with a Python library, distilled from actually building and
hardening this feature in `pydantic-schemaforms`. Swap `<package_name>` /
`<PrimaryEntryPoint>` / etc. for your own library's names.

## 0. What this is, and why it's worth doing

Most libraries tell developers how to integrate them via README prose that an
AI assistant has to rediscover (or guess at) every session. This feature
instead ships the integration instructions **as package data**, with a small
API to read them and a CLI to bootstrap them into an app repo — so:

- The instructions can never drift out of sync with an external copy-pasted
  snippet, because they ship with the version of the library you actually
  installed.
- An AI assistant working in an app repo cold (no prior context) can
  discover the feature itself, if you put the right pointer in the right
  two places (see step 5).
- Onboarding a new app repo is one command instead of a manual
  copy-paste-and-hope.

## 1. File layout

```
<package_name>/
├── ai_instructions.py           # the module below
└── assets/
    └── ai/
        ├── generic_app_instructions.md
        ├── claude_app_instructions.md
        └── copilot_app_instructions.md
tests/
└── test_ai_instructions.py      # the test file below
```

Three profiles (generic / claude / copilot) is the sensible default set —
add more later (e.g. `cursor`) by extending the two dicts in step 2, nothing
else needs to change.

## 2. Core module (copy-paste, then swap `<package_name>`)

```python
"""AI-assistant integration instructions, packaged with the library.

Ships the current, verified integration guidance as package data so it can
never drift out of sync with an external copy-pasted snippet. See the
package's top-level docstring / <PrimaryEntryPoint>'s docstring for the
discoverability hook that points an AI assistant at this without being asked.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path

_PROFILE_ALIASES: dict[str, str] = {
    'generic': 'generic',
    'default': 'generic',
    'copilot': 'copilot',
    'github-copilot': 'copilot',
    'claude': 'claude',
    'anthropic-claude': 'claude',
    # Add more aliases here as needed, e.g. 'cursor': 'cursor'
}

_PROFILE_TO_ASSET: dict[str, str] = {
    'generic': 'assets/ai/generic_app_instructions.md',
    'copilot': 'assets/ai/copilot_app_instructions.md',
    'claude': 'assets/ai/claude_app_instructions.md',
}


def available_instruction_profiles() -> tuple[str, ...]:
    """Return canonical app-integration instruction profiles bundled with the package."""
    return tuple(sorted(_PROFILE_TO_ASSET.keys()))


def suggested_instruction_filename(profile: str = 'generic') -> str:
    """Return a suggested filename for app repositories.

    This is only a recommendation and is not written automatically unless
    the caller opts into --write / --output via the CLI.
    """
    normalized = _normalize_profile(profile)
    if normalized == 'copilot':
        return '.github/copilot-instructions.md'
    if normalized == 'claude':
        return 'CLAUDE.md'
    return 'AI_INSTRUCTIONS.md'


def get_app_instructions(profile: str = 'generic') -> str:
    """Return packaged app-side integration instructions for an AI assistant profile.

    Aliases are accepted (for example: github-copilot, anthropic-claude).
    """
    normalized = _normalize_profile(profile)
    relative_path = _PROFILE_TO_ASSET[normalized]
    package_root = resources.files('<package_name>')
    return (package_root / relative_path).read_text(encoding='utf-8')


def _normalize_profile(profile: str) -> str:
    key = (profile or '').strip().lower()
    normalized = _PROFILE_ALIASES.get(key)
    if normalized:
        return normalized
    supported = ', '.join(available_instruction_profiles())
    raise ValueError(
        f'Unsupported instruction profile: {profile!r}. Supported profiles: {supported}'
    )


def _resolve_output_path(destination: str, *, base_dir: Path) -> Path:
    """Resolve a CLI-supplied destination and confirm it stays within base_dir.

    SECURITY (do not skip this): `--output` is free-form text that may come
    from an LLM-orchestrated invocation of this CLI, not a trusted human
    typing a path by hand. Without this check, a value like
    `--output ../../../etc/cron.d/evil` or an absolute path would let the
    process write outside the project directory it was invoked in.
    Resolving (which also follows symlinks) and requiring the result to be
    a descendant of base_dir closes that off. Tools like SonarCloud flag
    exactly this pattern under rules like pythonsecurity:S8707
    ("agentic workflows should not be vulnerable to path injection") — this
    isn't hypothetical, it's a real, checked-for vulnerability class.
    """
    base = base_dir.resolve()
    candidate = Path(destination)
    if not candidate.is_absolute():
        candidate = base / candidate
    candidate = candidate.resolve()

    # NOTE: use `candidate.parents` containment, not a string-prefix check
    # like str(candidate).startswith(str(base)) — that wrongly treats a
    # sibling directory like "project-evil/" as being inside "project/".
    if candidate != base and base not in candidate.parents:
        raise ValueError(
            f"Refusing to write outside the current directory ({base}): "
            f"{destination!r} resolves to {candidate}"
        )
    return candidate


def main(argv: list[str] | None = None) -> int:
    """CLI: print or write packaged AI-assistant instructions for an app repo.

    Examples::

        python -m <package_name>.ai_instructions claude > CLAUDE.md
        python -m <package_name>.ai_instructions copilot --write
    """
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog='python -m <package_name>.ai_instructions',
        description='Print or write packaged AI-assistant instructions for app integrations.',
    )
    parser.add_argument(
        'profile',
        nargs='?',
        default='generic',
        help=f'Instruction profile (aliases accepted). One of: {", ".join(available_instruction_profiles())}.',
    )
    parser.add_argument(
        '--write',
        action='store_true',
        help='Write to the suggested destination file (e.g. CLAUDE.md) instead of stdout.',
    )
    parser.add_argument(
        '--output',
        metavar='PATH',
        help='Write to an explicit path instead of stdout or the suggested destination.',
    )
    args = parser.parse_args(argv)

    try:
        text = get_app_instructions(args.profile)
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    destination = args.output or (
        suggested_instruction_filename(args.profile) if args.write else None
    )
    if destination is None:
        sys.stdout.write(text)
        return 0

    try:
        path = _resolve_output_path(destination, base_dir=Path.cwd())
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    print(f'Wrote {path}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
```

## 3. Export it from your package's `__init__.py`

```python
from .ai_instructions import (
    available_instruction_profiles,
    get_app_instructions,
    suggested_instruction_filename,
)

__all__ = [
    ...,
    'get_app_instructions',
    'available_instruction_profiles',
    'suggested_instruction_filename',
]
```

## 4. Packaging — make sure the `.md` files actually ship

This is the single easiest thing to get wrong (works fine in an editable
dev install, silently breaks for anyone who `pip install`s the real
package). Add the asset directory to your build backend's include list:

**hatchling** (`pyproject.toml`):
```toml
[tool.hatch.build.targets.wheel]
include = ["<package_name>/assets/**"]
```

**setuptools** (`pyproject.toml` or `setup.cfg`):
```toml
[tool.setuptools.package-data]
"<package_name>" = ["assets/ai/*.md"]
```
(and set `include_package_data = True`, plus a `MANIFEST.in` line
`recursive-include <package_name>/assets *.md` if you build sdists.)

**Verify for real** — don't trust the config, build and install the actual
wheel into a clean venv and call `get_app_instructions()` from there:
```bash
python -m build
pip install --force-reinstall dist/<package_name>-*.whl
python -c "from <package_name> import get_app_instructions; print(len(get_app_instructions('claude')))"
```

## 5. Discoverability — the part that makes this actually get used

An AI assistant helping a developer in a fresh session, with **no prior
prompt telling it to look for this**, will realistically only read two
things when investigating an unfamiliar dependency: the package's top-level
docstring (`import pkg; help(pkg)` or opening `__init__.py`), and the
docstring of whatever central class/function it's about to use. Put the
pointer in *both*.

**Package `__init__.py` docstring** — add near the end, after your normal
usage example:

```
<...your existing module docstring / usage example...>

AI assistant integrating this library into an app repo? Don't guess the
integration pattern from this docstring alone — run::

    python -m <package_name>.ai_instructions claude --write

(swap "claude" for "copilot"/"generic") to generate up-to-date guidance
covering <list 3-5 things your instructions cover — the main construction
pattern, the most commonly-confused setting, any security-sensitive config>.
Same content is available in-process via ``get_app_instructions()``.
```

**Primary class's own docstring** — one or two lines is enough:

```
AI assistants: run `python -m <package_name>.ai_instructions <profile>`
(claude/copilot/generic) for integration guidance before hand-rolling
a route.
```

Do **not** rely on README-only placement — an installed wheel doesn't
necessarily ship the README as a browsable file (check your build config;
many don't), and even if it did, an AI wouldn't think to look there without
already knowing the feature exists. Docstrings ship in the actual Python
source, so they're always there.

## 6. Authoring the profile `.md` files

Structure each profile file as a contract, not a tutorial — an AI reading
it needs rules it can mechanically follow, not prose to interpret:

```markdown
# <Profile> instructions for app teams using <package_name>

Goal: produce complete, runnable integrations without reverse-engineering
package internals.

## Completion contract (always deliver all items)
1. <the core object/class the app must define>
2. <the route/handler pattern>
3. <the render/output call, with its required arguments named explicitly>
4. <the validation loop>
5. <state-preservation on failure, if applicable>
6. A short explanation of any non-obvious mapping choice.

## Core integration pattern
<the one blessed way to use your library — pick ONE if there are several>

## Constraints vs. cosmetic options — do not confuse these
If your library has both "real, enforced" settings and "cosmetic/display
only" settings that look similar, spell out which is which explicitly and
say what breaks if they're swapped. (In pydantic-schemaforms: Field()
constraints like min_length/pattern/ge/le are enforced server-side and
reflected in HTML automatically; ui_options is decoration only with zero
validation effect. Putting a real constraint in the cosmetic bucket
produces a form that *looks* validated but silently isn't — the generic
version of this lesson is: any time your library has two similarly-named
configuration surfaces where only one is actually enforced, that's exactly
where an AI will guess wrong without explicit guidance.)

## Deterministic mapping policy
If your library infers behavior from types/names (e.g. Python type → UI
widget), give an explicit precedence order so repeated runs converge on the
same output instead of drifting between requests.

## Security / config contract (if applicable)
Anything security-sensitive (CSRF, auth, secrets handling) needs to be a
named, mandatory part of the completion contract — not an afterthought —
or an AI will ship functionally-working-but-insecure code by default.

## Advanced features
Document every feature that has more than one way to invoke it, and state
exactly which way is current/recommended. If an older/parallel path exists
purely for backwards compatibility, say so and say not to use it for new
code.

## Common mistakes to avoid
- Do not <thing you've actually seen go wrong, or would go wrong from a
  plausible-but-incorrect reading of the API>.
- ...

## Prompt starters
"<a copy-paste starter prompt a developer can hand to their own assistant
for a simple case>"
"<...and for a complex case>"
```

Write **generic**, **claude**, and **copilot** variants with the same
content in each one's native voice/structure (rule-list vs. contract-list
vs. checklist) — assistants respond better to instructions phrased in the
style they're tuned for, and it costs little to maintain three short
variants once the underlying facts are settled.

## 7. Tests (copy-paste, then swap `<package_name>` / `<PrimaryEntryPoint>`)

```python
from __future__ import annotations

import pytest

from <package_name> import (
    available_instruction_profiles,
    get_app_instructions,
    suggested_instruction_filename,
)
from <package_name>.ai_instructions import main


def test_available_instruction_profiles_contains_expected_profiles() -> None:
    assert available_instruction_profiles() == ('claude', 'copilot', 'generic')


def test_get_app_instructions_contains_core_pattern() -> None:
    text = get_app_instructions('copilot')
    # Assert your library's actual primary entry-point name appears —
    # this is a regression guard against the instructions rotting out of
    # sync with the code as the library evolves.
    assert '<PrimaryEntryPoint>' in text


def test_get_app_instructions_supports_aliases() -> None:
    assert get_app_instructions('github-copilot') == get_app_instructions('copilot')


def test_get_app_instructions_unknown_profile_raises() -> None:
    with pytest.raises(ValueError, match='Unsupported instruction profile'):
        get_app_instructions('unknown-assistant')


def test_suggested_instruction_filename_is_profile_specific() -> None:
    assert suggested_instruction_filename('copilot') == '.github/copilot-instructions.md'
    assert suggested_instruction_filename('claude') == 'CLAUDE.md'
    assert suggested_instruction_filename('generic') == 'AI_INSTRUCTIONS.md'


def test_cli_prints_to_stdout_by_default(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(['claude'])
    assert exit_code == 0
    assert capsys.readouterr().out == get_app_instructions('claude')


def test_cli_write_flag_uses_suggested_filename(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(['copilot', '--write']) == 0
    written = tmp_path / '.github' / 'copilot-instructions.md'
    assert written.read_text(encoding='utf-8') == get_app_instructions('copilot')


def test_cli_output_flag_writes_explicit_path(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    destination = tmp_path / 'nested' / 'INSTRUCTIONS.md'
    assert main(['generic', '--output', str(destination)]) == 0
    assert destination.read_text(encoding='utf-8') == get_app_instructions('generic')


def test_cli_unknown_profile_exits_nonzero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(['unknown-assistant'])
    assert exc_info.value.code == 2
    assert 'Unsupported instruction profile' in capsys.readouterr().err


# --- Security regression tests: do not weaken or remove these. ---

def test_cli_output_flag_rejects_path_traversal_outside_cwd(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    escape_target = tmp_path.parent / 'escaped.md'
    escape_target.unlink(missing_ok=True)
    with pytest.raises(SystemExit) as exc_info:
        main(['generic', '--output', '../escaped.md'])
    assert exc_info.value.code == 2
    assert not escape_target.exists()


def test_cli_output_flag_rejects_absolute_path_outside_cwd(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    outside = tmp_path.parent / 'other-dir'
    outside.mkdir(exist_ok=True)
    escape_target = outside / 'escaped.md'
    escape_target.unlink(missing_ok=True)
    with pytest.raises(SystemExit) as exc_info:
        main(['generic', '--output', str(escape_target)])
    assert exc_info.value.code == 2
    assert not escape_target.exists()


def test_cli_output_flag_allows_dotdot_that_stays_inside_cwd(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'subdir').mkdir()
    assert main(['generic', '--output', 'subdir/../ALLOWED.md']) == 0
    assert (tmp_path / 'ALLOWED.md').read_text(encoding='utf-8') == get_app_instructions('generic')


def test_resolve_output_path_rejects_sibling_directory_with_shared_prefix(tmp_path) -> None:
    from <package_name>.ai_instructions import _resolve_output_path

    base = tmp_path / 'project'
    base.mkdir()
    sibling = tmp_path / 'project-evil' / 'file.md'
    with pytest.raises(ValueError, match='Refusing to write outside'):
        _resolve_output_path(str(sibling), base_dir=base)
```

## 8. README section template

````markdown
### AI Assistant Bootstrap (for app repositories)

If you're using Claude, Copilot, or another AI assistant in your app
project, pull packaged instructions directly from the installed library
into your app repo's instruction file — one command, no manual copy-paste:

```bash
python -m <package_name>.ai_instructions claude --write     # writes ./CLAUDE.md
python -m <package_name>.ai_instructions copilot --write    # writes ./.github/copilot-instructions.md
python -m <package_name>.ai_instructions generic > AI_INSTRUCTIONS.md
```

Or from Python:

```python
from <package_name> import get_app_instructions, suggested_instruction_filename

assistant = 'copilot'  # or 'claude' / 'generic'
print(f'Suggested destination: {suggested_instruction_filename(assistant)}')
print(get_app_instructions(assistant))
```

This avoids having assistants reverse-engineer internals and keeps
generated app code aligned with the library's actual, current API.
````

## 9. Optional polish (do these later, not essential to the core feature)

- **A dedicated docs page**, if you have a docs site — cover the API, the
  CLI, and explicitly what the instructions do *not* yet cover (be honest
  about gaps; an AI assistant reading a doc page will trust silence as
  "not applicable," which is worse than an explicit "not covered yet").
- **A demo page** in your example app that renders each profile's markdown
  as tabs, so `get_app_instructions()` output is easy to eyeball without
  writing a script. Rendering markdown → HTML pulls in a dependency
  (`Markdown` worked fine, MIT-licensed, zero transitive bloat) — keep it
  scoped to your example/dev extras, never your core library dependencies.

## 10. Hard-won lessons (read this before you consider it "done")

These are the mistakes that actually happened building this the first
time, in this exact codebase — not hypothetical advice.

1. **Verify every claim by running it, not by reading the source.**
   Reading code and reasoning "this should work" is not the same as
   confirming it does. In this exact project, purely by executing rather
   than reading, I found: a silently-broken field attribute (several
   `Field()` kwargs were dropped for ordinary fields due to a schema
   assumption that only held for a rarer code path), a dead code branch
   that looked reachable but never was, a documented method name that had
   never existed (`Layout.grid()` vs. the real `Layout.create_grid()`),
   and doc code examples with typographic curly quotes that were a hard
   `SyntaxError` if copy-pasted. All four predated this feature and had
   nothing to do with it — they were only found because the instructions
   forced someone to actually try the described behavior.

2. **Watch for two APIs that do "the same thing."** Libraries accumulate
   a "current" way and a "legacy/parallel" way to do things. If your
   instructions don't say which one to use, an AI will pick unpredictably.
   Worse, if the two paths have quietly diverged (one supports a feature
   the other doesn't), you'll ship inconsistent guidance. Pick one,
   name it, and if the other one turns out to be truly unused, consider
   deleting it from the library rather than documenting around it forever.

3. **Distinguish "enforced" from "cosmetic" configuration explicitly.**
   If your library has two similarly-shaped configuration surfaces where
   only one actually does validation/enforcement, an AI *will* eventually
   put a real constraint in the cosmetic one, producing code that looks
   correct and passes a casual glance but doesn't actually enforce
   anything. Call this out by name in the instructions, with a concrete
   example of what breaks.

4. **Any CLI meant to be invoked by an agent is a security surface.**
   The whole premise of this feature is "an AI will run this command."
   Treat every argument that touches the filesystem as adversarial input —
   not because the AI is malicious, but because a misdirected instruction,
   a bug in its own reasoning, or a prompt injection could produce a bad
   argument, and the blast radius is "arbitrary file write." Validate
   before writing (see `_resolve_output_path` above), and use
   `Path.parents` containment, not string-prefix matching, for the check.

5. **Discoverability is a design decision, not an afterthought.** Decide
   explicitly which artifacts an AI is likely to read *without being
   told to look for this feature*, and put the pointer there. For a
   Python package, that's the top-level `__init__.py` docstring and your
   most central class's docstring — nowhere else is reliable.

6. **Test the instructions' *content*, not just the plumbing.** A test
   that asserts `'FormModel' in text` (or your equivalent) catches the
   instructions silently going stale when the library's actual primary
   API renames or removes something the instructions still reference.

7. **Make updating the instructions a standing rule, not a one-time
   task.** Put a line at the bottom of your docs page (or CONTRIBUTING):
   "if you add a public config kwarg or change how a documented feature
   works, update the corresponding `assets/ai/*.md` file in the same
   change." Otherwise this rots exactly like an external README would
   have, just with extra steps.

8. **Don't overclaim.** If a real feature isn't covered by the
   instructions yet, say so explicitly in the docs page rather than
   letting silence be misread as "doesn't apply here."

## 11. Rollout checklist (suggested order)

1. Write `ai_instructions.py` (module in step 2), swap in your package name.
2. Write the three `assets/ai/*.md` files (structure in step 6) — draft
   them, then go back and verify every concrete claim by actually running
   the described code before finalizing.
3. Export the three public functions from `__init__.py` (step 3).
4. Add the packaging config (step 4) and verify with a real
   build-and-install-into-clean-venv, not just editable-mode testing.
5. Add the discoverability docstring hooks (step 5).
6. Add the test file (step 7) — including the security regression tests,
   don't skip those.
7. Add the README section (step 8).
8. Optional: docs page + demo page (step 9).
9. Set the standing "update instructions alongside API changes" rule
   somewhere durable (step 10, lesson 7).
