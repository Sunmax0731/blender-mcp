from __future__ import annotations

import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class CodexCliConfig:
    command: str
    model: str
    timeout_seconds: float
    working_directory: Path


class CodexCliError(Exception):
    def __init__(self, code: str, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


def load_codex_cli_config() -> CodexCliConfig:
    default_workdir = Path(tempfile.gettempdir()).resolve()
    default_command = "codex.cmd" if os.name == "nt" else "codex"
    return CodexCliConfig(
        command=os.getenv("BLENDER_MCP_CODEX_COMMAND", default_command).strip() or default_command,
        model=os.getenv("BLENDER_MCP_CODEX_MODEL", "").strip(),
        timeout_seconds=float(os.getenv("BLENDER_MCP_CODEX_TIMEOUT_SECONDS", "45")),
        working_directory=Path(
            os.getenv("BLENDER_MCP_CODEX_WORKDIR", str(default_workdir))
        ).resolve(),
    )


def run_codex_cli_suggestion(
    *,
    config: CodexCliConfig,
    user_prompt: str,
    system_prompt: str,
) -> dict[str, object]:
    prompt = _build_combined_prompt(system_prompt=system_prompt, user_prompt=user_prompt)
    config.working_directory.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="blender-mcp-codex-") as temp_dir:
        output_path = Path(temp_dir) / "last_message.txt"
        command = _build_codex_command(
            config=config,
            output_path=output_path,
            prompt=prompt,
        )
        try:
            completed = subprocess.run(
                command,
                cwd=str(config.working_directory),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=config.timeout_seconds,
                check=False,
            )
        except FileNotFoundError as exc:
            raise CodexCliError(
                "CODEX_CLI_NOT_FOUND",
                f"Codex CLI command was not found: {config.command}",
                retryable=False,
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise CodexCliError(
                "CODEX_CLI_TIMEOUT",
                "Codex CLI suggestion request timed out.",
                retryable=True,
            ) from exc

        if completed.returncode != 0:
            details = _summarize_process_output(completed)
            raise CodexCliError(
                "CODEX_CLI_ERROR",
                f"Codex CLI suggestion request failed. {details}",
                retryable=True,
            )

        if not output_path.exists():
            raise CodexCliError(
                "CODEX_CLI_INVALID_RESPONSE",
                "Codex CLI did not produce an output message file.",
                retryable=True,
            )

        summary = output_path.read_text(encoding="utf-8").strip()
        if not summary:
            raise CodexCliError(
                "CODEX_CLI_INVALID_RESPONSE",
                "Codex CLI response did not contain a valid summary.",
                retryable=True,
            )

        return {
            "provider": "codex-cli",
            "model": config.model or "codex-default",
            "content": summary,
            "raw": {"summary": summary},
        }


def _build_combined_prompt(*, system_prompt: str, user_prompt: str) -> str:
    return (
        "あなたは Blender MCP のバックグラウンド提案生成器です。\n"
        "追加質問、前置き、説明、箇条書きは禁止です。\n"
        "Blender 上で今すぐ実行できる次の一手だけを、日本語 2 文以内で返してください。\n"
        "依頼を完全には満たせない場合でも、制約内で進められる代替案を短く返してください。\n\n"
        "system:\n"
        f"{system_prompt.strip()}\n\n"
        "user:\n"
        f"{user_prompt.strip()}"
    )


def _build_codex_command(
    *,
    config: CodexCliConfig,
    output_path: Path,
    prompt: str,
) -> list[str]:
    command = [
        config.command,
        "exec",
        "--skip-git-repo-check",
        "--ignore-rules",
        "--sandbox",
        "read-only",
        "--output-last-message",
        str(output_path),
        "--color",
        "never",
        prompt,
    ]
    if config.model:
        command[2:2] = ["--model", config.model]
    return command


def _summarize_process_output(completed: subprocess.CompletedProcess[str]) -> str:
    stderr = (completed.stderr or "").strip()
    stdout = (completed.stdout or "").strip()
    if stderr:
        return f"stderr: {stderr.splitlines()[-1]}"
    if stdout:
        return f"stdout: {stdout.splitlines()[-1]}"
    return f"exit code: {completed.returncode}"
