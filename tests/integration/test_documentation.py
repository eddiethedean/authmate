import asyncio
import re
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any, cast


def _python_blocks(path: Path) -> list[str]:
    return re.findall(r"```python\n(.*?)```", path.read_text(), flags=re.DOTALL)


def test_readme_python_block_executes() -> None:
    namespace: dict[str, Any] = {}
    block = _python_blocks(Path("README.md"))[0]
    exec(compile(block, "README.md", "exec"), namespace)  # noqa: S102
    check_request = cast(Callable[[], Coroutine[Any, Any, Any]], namespace["check_request"])
    decision: Any = asyncio.run(check_request())
    assert decision.allowed


def test_quickstart_python_block_executes() -> None:
    namespace: dict[str, Any] = {}
    block = _python_blocks(Path("docs/quickstart.md"))[0]
    exec(compile(block, "docs/quickstart.md", "exec"), namespace)  # noqa: S102
    assert callable(namespace["require_report"])
