# -*- coding: utf-8 -*-
import asyncio
import time

import pytest

from dsg_lib.common_functions import async_file_functions, file_functions


# --- delegation tests: prove each async wrapper calls the sync twin with ---
# --- the right positional/keyword args and returns its result unchanged  ---


@pytest.mark.asyncio
async def test_delete_file_delegates_to_sync(mocker):
    mock = mocker.patch.object(
        async_file_functions.file_functions, "delete_file", return_value="complete"
    )
    result = await async_file_functions.delete_file("test.csv", root_folder="/x")
    mock.assert_called_once_with("test.csv", root_folder="/x")
    assert result == "complete"


@pytest.mark.asyncio
async def test_save_json_delegates_to_sync(mocker):
    mock = mocker.patch.object(
        async_file_functions.file_functions,
        "save_json",
        return_value="File saved successfully",
    )
    result = await async_file_functions.save_json(
        "t.json", {"a": 1}, root_folder="/x", indent=2, ensure_ascii=False
    )
    mock.assert_called_once_with(
        "t.json", {"a": 1}, root_folder="/x", indent=2, ensure_ascii=False
    )
    assert result == "File saved successfully"


@pytest.mark.asyncio
async def test_open_json_delegates_to_sync(mocker):
    mock = mocker.patch.object(
        async_file_functions.file_functions, "open_json", return_value={"a": 1}
    )
    result = await async_file_functions.open_json("t.json", root_folder="/x")
    mock.assert_called_once_with("t.json", root_folder="/x")
    assert result == {"a": 1}


@pytest.mark.asyncio
async def test_save_csv_delegates_to_sync(mocker):
    mock = mocker.patch.object(
        async_file_functions.file_functions, "save_csv", return_value="complete"
    )
    data = [["a", "b"], ["1", "2"]]
    result = await async_file_functions.save_csv(
        "t.csv", data, root_folder="/x", delimiter="|", quotechar="'"
    )
    mock.assert_called_once_with(
        "t.csv", data, root_folder="/x", delimiter="|", quotechar="'"
    )
    assert result == "complete"


@pytest.mark.asyncio
async def test_append_csv_delegates_to_sync(mocker):
    mock = mocker.patch.object(
        async_file_functions.file_functions, "append_csv", return_value="appended"
    )
    data = [["1", "2"]]
    result = await async_file_functions.append_csv(
        "t.csv",
        data,
        root_folder="/x",
        delimiter="|",
        quotechar="'",
        columns=["b", "a"],
    )
    mock.assert_called_once_with(
        "t.csv",
        data,
        root_folder="/x",
        delimiter="|",
        quotechar="'",
        columns=["b", "a"],
    )
    assert result == "appended"


@pytest.mark.asyncio
async def test_open_csv_delegates_to_sync(mocker):
    mock = mocker.patch.object(
        async_file_functions.file_functions, "open_csv", return_value=[{"a": "1"}]
    )
    result = await async_file_functions.open_csv(
        "t.csv",
        delimiter="|",
        quote_level="all",
        skip_initial_space=False,
        root_folder="/x",
        quotechar=None,
    )
    mock.assert_called_once_with(
        "t.csv",
        delimiter="|",
        quote_level="all",
        skip_initial_space=False,
        root_folder="/x",
        quotechar=None,
    )
    assert result == [{"a": "1"}]


@pytest.mark.asyncio
async def test_save_text_delegates_to_sync(mocker):
    mock = mocker.patch.object(
        async_file_functions.file_functions, "save_text", return_value="complete"
    )
    result = await async_file_functions.save_text("t.txt", "hello", root_folder="/x")
    mock.assert_called_once_with("t.txt", "hello", root_folder="/x")
    assert result == "complete"


@pytest.mark.asyncio
async def test_open_text_delegates_to_sync(mocker):
    mock = mocker.patch.object(
        async_file_functions.file_functions, "open_text", return_value="hello"
    )
    result = await async_file_functions.open_text("t.txt", root_folder="/x")
    mock.assert_called_once_with("t.txt", root_folder="/x")
    assert result == "hello"


# --- real round-trip tests: exercise actual disk I/O through the async ---
# --- module only, using tmp_path as root_folder                        ---


@pytest.mark.asyncio
async def test_json_roundtrip(tmp_path):
    root = str(tmp_path)
    await async_file_functions.save_json(
        "t.json", {"name": "José"}, root_folder=root, indent=2, ensure_ascii=False
    )
    result = await async_file_functions.open_json("t.json", root_folder=root)
    assert result == {"name": "José"}
    assert (tmp_path / "t.json").is_file()


@pytest.mark.asyncio
async def test_csv_roundtrip_with_append_and_columns(tmp_path):
    root = str(tmp_path)
    await async_file_functions.save_csv(
        "t.csv", [["name", "email"], ["Jane", "jane@example.com"]], root_folder=root
    )
    await async_file_functions.append_csv(
        "t.csv",
        [["joe@example.com", "Joe"]],
        root_folder=root,
        columns=["email", "name"],
    )
    result = await async_file_functions.open_csv("t.csv", root_folder=root)
    assert result == [
        {"name": "Jane", "email": "jane@example.com"},
        {"name": "Joe", "email": "joe@example.com"},
    ]


@pytest.mark.asyncio
async def test_text_roundtrip(tmp_path):
    root = str(tmp_path)
    await async_file_functions.save_text("t.txt", "hello world", root_folder=root)
    result = await async_file_functions.open_text("t.txt", root_folder=root)
    assert result == "hello world"


@pytest.mark.asyncio
async def test_delete_file_roundtrip(tmp_path):
    root = str(tmp_path)
    await async_file_functions.save_text("t.txt", "hello", root_folder=root)
    assert (tmp_path / "t.txt").is_file()
    result = await async_file_functions.delete_file("t.txt", root_folder=root)
    assert result == "complete"
    assert not (tmp_path / "t.txt").is_file()


# --- exception propagation tests: confirm the exact same exception types ---
# --- as the sync functions surface through the awaited call              ---


@pytest.mark.asyncio
async def test_save_json_propagates_type_error(tmp_path):
    with pytest.raises(TypeError):
        await async_file_functions.save_json(
            "t.json", "not-a-list-or-dict", root_folder=str(tmp_path)
        )


@pytest.mark.asyncio
async def test_save_json_propagates_value_error():
    with pytest.raises(ValueError):
        await async_file_functions.save_json("bad/name.json", {"a": 1})


@pytest.mark.asyncio
async def test_open_json_propagates_file_not_found_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        await async_file_functions.open_json("missing.json", root_folder=str(tmp_path))


@pytest.mark.asyncio
async def test_open_json_propagates_type_error():
    with pytest.raises(TypeError):
        await async_file_functions.open_json(123)


@pytest.mark.asyncio
async def test_save_csv_propagates_type_error_for_bad_delimiter(tmp_path):
    with pytest.raises(TypeError):
        await async_file_functions.save_csv(
            "t.csv", [["a"]], root_folder=str(tmp_path), delimiter="::"
        )


@pytest.mark.asyncio
async def test_open_csv_propagates_type_error_for_quotechar(tmp_path):
    await async_file_functions.save_csv("t.csv", [["a"], ["1"]], root_folder=str(tmp_path))
    with pytest.raises(TypeError):
        await async_file_functions.open_csv(
            "t.csv", root_folder=str(tmp_path), quotechar='"'
        )


@pytest.mark.asyncio
async def test_open_csv_propagates_value_error_for_bad_quote_level(tmp_path):
    await async_file_functions.save_csv("t.csv", [["a"], ["1"]], root_folder=str(tmp_path))
    with pytest.raises(ValueError):
        await async_file_functions.open_csv(
            "t.csv", root_folder=str(tmp_path), quote_level="invalid"
        )


@pytest.mark.asyncio
async def test_append_csv_propagates_file_not_found_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        await async_file_functions.append_csv(
            "missing.csv", [["a", "b"], ["1", "2"]], root_folder=str(tmp_path)
        )


@pytest.mark.asyncio
async def test_append_csv_propagates_value_error_for_header_mismatch(tmp_path):
    root = str(tmp_path)
    await async_file_functions.save_csv("t.csv", [["a", "b"], ["1", "2"]], root_folder=root)
    with pytest.raises(ValueError):
        await async_file_functions.append_csv(
            "t.csv", [["x", "y"], ["3", "4"]], root_folder=root
        )


@pytest.mark.asyncio
async def test_save_text_propagates_type_error(tmp_path):
    with pytest.raises(TypeError):
        await async_file_functions.save_text("t.txt", 123, root_folder=str(tmp_path))


@pytest.mark.asyncio
async def test_open_text_propagates_file_not_found_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        await async_file_functions.open_text("missing.txt", root_folder=str(tmp_path))


@pytest.mark.asyncio
async def test_delete_file_propagates_value_error_for_unsupported_extension(tmp_path):
    with pytest.raises(ValueError):
        await async_file_functions.delete_file("t.jpg", root_folder=str(tmp_path))


@pytest.mark.asyncio
async def test_delete_file_propagates_file_not_found_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        await async_file_functions.delete_file("missing.csv", root_folder=str(tmp_path))


# --- concurrency proof: prove the mechanism actually keeps the event loop ---
# --- responsive while a "slow" sync call runs in its worker thread        ---


@pytest.mark.asyncio
async def test_async_file_functions_do_not_block_event_loop(mocker):
    def blocking_save(*args, **kwargs):
        time.sleep(0.3)
        return "complete"

    mocker.patch.object(async_file_functions.file_functions, "save_text", blocking_save)

    start = time.monotonic()
    results = await asyncio.gather(
        async_file_functions.save_text("t.txt", "data", root_folder="/x"),
        asyncio.sleep(0.05, result="loop-was-responsive"),
    )
    elapsed = time.monotonic() - start

    assert results == ["complete", "loop-was-responsive"]
    # If save_text blocked the loop, total elapsed would be roughly additive
    # (~0.35s: 0.3 + 0.05 run sequentially). Running concurrently in a worker
    # thread, it should stay close to the 0.3s of the slower call alone.
    assert elapsed < 0.33


def test_module_has_no_independent_file_functions_reference():
    # The async module must call through to the real file_functions module
    # object (not a copy), so that patching file_functions.<name> directly
    # (as application code testing might do) is also observed here.
    assert async_file_functions.file_functions is file_functions
