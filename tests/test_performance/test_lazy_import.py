# -*- coding: utf-8 -*-
import subprocess
import sys

import pytest

import dsg_lib


def test_import_does_not_load_ai_instructions():
    code = (
        "import sys, dsg_lib; "
        "assert 'dsg_lib.ai_instructions' not in sys.modules; "
        "from dsg_lib import get_app_instructions; "
        "assert 'dsg_lib.ai_instructions' in sys.modules"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


def test_lazy_exports_resolve():
    from dsg_lib import ai_instructions

    assert dsg_lib.get_app_instructions is ai_instructions.get_app_instructions
    assert set(dsg_lib.__all__) >= dsg_lib._LAZY_EXPORTS


def test_unknown_attribute_raises():
    with pytest.raises(AttributeError):
        dsg_lib.does_not_exist  # noqa: B018
