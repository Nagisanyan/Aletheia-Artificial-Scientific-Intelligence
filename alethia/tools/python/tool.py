from __future__ import annotations

import ast
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PythonToolResult:
    succeeded: bool
    stdout: str = ""
    stderr: str = ""
    exception: str = ""
    output: str = ""
    runtime_seconds: float = 0.0
    blocked: bool = False
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "succeeded": self.succeeded,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exception": self.exception,
            "output": self.output,
            "runtime_seconds": self.runtime_seconds,
            "blocked": self.blocked,
            "metadata": self.metadata,
        }


class PythonTool:
    """Controlled local Python execution for Aletheia 0.1.

    WARNING: this is not a security sandbox. It is a constrained local execution helper
    designed to prevent the most obvious dangerous patterns, but it does not provide
    process isolation, resource isolation, or a locked-down filesystem.
    """

    FORBIDDEN_IMPORTS = {
        "os",
        "subprocess",
        "socket",
        "requests",
        "urllib",
        "pathlib",
        "shutil",
        "tempfile",
        "multiprocessing",
    }
    FORBIDDEN_CALLS = {"exec", "eval", "compile", "open", "input", "globals", "locals", "getattr", "setattr", "delattr", "__import__"}
    MAX_OUTPUT_CHARS = 20000

    def __init__(self, timeout: float = 10.0, working_directory: str | Path | None = None):
        self.timeout = timeout
        self.working_directory = str(working_directory) if working_directory is not None else None

    def execute(self, code: str) -> PythonToolResult:
        sanitized = textwrap.dedent(code).strip()
        if not sanitized:
            return PythonToolResult(succeeded=False, stderr="No code provided.", blocked=True, metadata={"reason": "empty_code"})
        if len(sanitized) > 5000:
            return PythonToolResult(succeeded=False, stderr="Code too large for execution.", blocked=True, metadata={"reason": "too_large"})

        if self._contains_forbidden_pattern(sanitized):
            return PythonToolResult(
                succeeded=False,
                stderr="Execution blocked by policy.",
                blocked=True,
                metadata={"reason": "dangerous pattern detected"},
            )

        try:
            tree = ast.parse(sanitized, mode="exec")
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.split(".", 1)[0] in self.FORBIDDEN_IMPORTS:
                            raise ValueError(f"Blocked import: {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.split(".", 1)[0] in self.FORBIDDEN_IMPORTS:
                        raise ValueError(f"Blocked import: {node.module}")
                elif isinstance(node, ast.Call):
                    func = node.func
                    if isinstance(func, ast.Name) and func.id in self.FORBIDDEN_CALLS:
                        raise ValueError(f"Blocked call: {func.id}")
                    if isinstance(func, ast.Attribute) and func.attr in self.FORBIDDEN_CALLS:
                        raise ValueError(f"Blocked attribute call: {func.attr}")
        except Exception as exc:  # pragma: no cover - defensive
            return PythonToolResult(succeeded=False, stderr=f"Execution blocked: {exc}", blocked=True, metadata={"reason": "static_analysis_rejected"})

        try:
            completed = subprocess.run(
                [sys.executable, "-c", sanitized],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.working_directory,
                env={
                    **dict(__import__("os").environ),
                    "PYTHONPATH": "",
                    "PYTHONNOUSERSITE": "1",
                },
            )
            stdout = completed.stdout.strip()
            stderr = completed.stderr.strip()
            if len(stdout) > self.MAX_OUTPUT_CHARS or len(stderr) > self.MAX_OUTPUT_CHARS:
                return PythonToolResult(
                    succeeded=False,
                    stderr="Execution output exceeded the maximum allowed size.",
                    blocked=True,
                    metadata={"reason": "output_too_large"},
                )
            output = stdout if stdout else stderr
            return PythonToolResult(
                succeeded=completed.returncode == 0,
                stdout=stdout,
                stderr=stderr,
                output=output,
                runtime_seconds=0.0,
                metadata={"return_code": str(completed.returncode)},
            )
        except subprocess.TimeoutExpired:
            return PythonToolResult(
                succeeded=False,
                stderr="Execution timed out.",
                exception="TimeoutExpired",
                blocked=False,
                metadata={"reason": "timeout"},
            )
        except Exception as exc:  # pragma: no cover - defensive
            return PythonToolResult(
                succeeded=False,
                stderr=str(exc),
                exception=type(exc).__name__,
                blocked=False,
                metadata={"reason": "execution_error"},
            )

    def _contains_forbidden_pattern(self, code: str) -> bool:
        blocked_patterns = [
            "exec(",
            "eval(",
            "compile(",
            "os.system",
            "subprocess.",
            "socket.",
            "import socket",
            "requests.",
            "urllib.",
            "open(",
            "Path(\"/",
            "__import__",
            "file://",
            "http://",
            "https://",
        ]
        lowered = code.lower()
        return any(pattern in lowered for pattern in blocked_patterns)
