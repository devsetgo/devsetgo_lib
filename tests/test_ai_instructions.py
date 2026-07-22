# -*- coding: utf-8 -*-
import pytest

from dsg_lib import ai_instructions
from dsg_lib.ai_instructions import (
    available_instruction_profiles,
    get_app_instructions,
    main,
    suggested_instruction_filename,
)


class TestAvailableInstructionProfiles:
    def test_returns_canonical_profiles(self):
        assert available_instruction_profiles() == ("generic", "copilot", "claude")


class TestNormalizeProfile:
    def test_canonical_names_pass_through(self):
        for profile in available_instruction_profiles():
            assert ai_instructions._normalize_profile(profile) == profile

    def test_case_and_whitespace_insensitive(self):
        assert ai_instructions._normalize_profile("  Claude  ") == "claude"

    def test_known_aliases_resolve(self):
        assert ai_instructions._normalize_profile("anthropic") == "claude"
        assert ai_instructions._normalize_profile("gh-copilot") == "copilot"
        assert ai_instructions._normalize_profile("chatgpt") == "generic"

    def test_unknown_profile_raises_value_error(self):
        with pytest.raises(ValueError):
            ai_instructions._normalize_profile("bogus-tool")

    def test_non_string_raises_type_error(self):
        with pytest.raises(TypeError):
            ai_instructions._normalize_profile(123)


class TestSuggestedInstructionFilename:
    def test_generic(self):
        assert suggested_instruction_filename("generic") == "AI_INSTRUCTIONS.md"

    def test_copilot(self):
        assert suggested_instruction_filename("copilot") == ".github/copilot-instructions.md"

    def test_claude(self):
        assert suggested_instruction_filename("claude") == "CLAUDE.md"

    def test_defaults_to_generic(self):
        assert suggested_instruction_filename() == "AI_INSTRUCTIONS.md"

    def test_unknown_profile_raises(self):
        with pytest.raises(ValueError):
            suggested_instruction_filename("bogus-tool")


class TestGetAppInstructions:
    def test_each_profile_has_a_distinct_header_but_shared_body(self):
        bodies = {}
        for profile in available_instruction_profiles():
            text = get_app_instructions(profile)
            lines = text.splitlines()
            assert lines[0].startswith("# devsetgo_lib integration instructions")
            bodies[profile] = "\n".join(lines[2:])
        # The substantive content is identical across profiles -- only the
        # header naming the target tool differs.
        assert bodies["generic"] == bodies["copilot"] == bodies["claude"]

    def test_default_profile_is_generic(self):
        assert get_app_instructions() == get_app_instructions("generic")

    def test_content_covers_key_gotchas(self):
        text = get_app_instructions("generic")
        # Spot-check a handful of the non-obvious, verified gotchas that make
        # this document worth having instead of guessing from docstrings.
        assert "root_folder" in text
        assert "DatabaseErrorResult" in text
        assert "make_folder" in text
        assert "pathlib.Path" in text
        assert "deprecated" in text.lower()

    def test_unknown_profile_raises(self):
        with pytest.raises(ValueError):
            get_app_instructions("bogus-tool")


class TestResolveOutputPath:
    def test_relative_path_within_base_dir_resolves(self, tmp_path):
        result = ai_instructions._resolve_output_path("CLAUDE.md", tmp_path)
        assert result == (tmp_path / "CLAUDE.md").resolve()

    def test_nested_relative_path_within_base_dir_resolves(self, tmp_path):
        result = ai_instructions._resolve_output_path(
            ".github/copilot-instructions.md", tmp_path
        )
        assert result == (tmp_path / ".github" / "copilot-instructions.md").resolve()

    def test_traversal_outside_base_dir_raises(self, tmp_path):
        with pytest.raises(ValueError, match="Refusing to write outside"):
            ai_instructions._resolve_output_path("../../etc/passwd", tmp_path)

    def test_absolute_path_outside_base_dir_raises(self, tmp_path):
        with pytest.raises(ValueError, match="Refusing to write outside"):
            ai_instructions._resolve_output_path("/etc/passwd", tmp_path)


class TestMainCli:
    def test_no_args_prints_generic_to_stdout(self, capsys):
        exit_code = main([])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "any AI coding assistant" in captured.out

    def test_profile_arg_selects_profile(self, capsys):
        exit_code = main(["claude"])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "Claude / Claude Code" in captured.out

    def test_unknown_profile_exits_nonzero(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["bogus-tool"])
        assert exc_info.value.code == 2
        assert "Unknown instruction profile" in capsys.readouterr().err

    def test_write_flag_uses_suggested_filename(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        exit_code = main(["claude", "--write"])
        captured = capsys.readouterr()
        assert exit_code == 0
        written = tmp_path / "CLAUDE.md"
        assert written.is_file()
        assert written.read_text(encoding="utf-8") == get_app_instructions("claude")
        assert "CLAUDE.md" in captured.out

    def test_write_flag_creates_nested_directories(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        main(["copilot", "--write"])
        written = tmp_path / ".github" / "copilot-instructions.md"
        assert written.is_file()
        assert written.read_text(encoding="utf-8") == get_app_instructions("copilot")

    def test_output_flag_writes_to_explicit_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        main(["generic", "--output", "docs/ai/AI_INSTRUCTIONS.md"])
        written = tmp_path / "docs" / "ai" / "AI_INSTRUCTIONS.md"
        assert written.is_file()
        assert written.read_text(encoding="utf-8") == get_app_instructions("generic")

    def test_output_flag_outside_cwd_exits_nonzero(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        with pytest.raises(SystemExit) as exc_info:
            main(["claude", "--output", "../escaped.md"])
        assert exc_info.value.code == 2
        assert "Refusing to write outside" in capsys.readouterr().err
