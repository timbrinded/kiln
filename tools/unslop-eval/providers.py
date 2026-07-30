from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProviderResult:
    command: list[str]
    exit_code: int | None
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool
    total_tokens: int
    tool_calls: int
    model: str

    @property
    def infrastructure_error(self) -> str | None:
        combined = f"{self.stdout}\n{self.stderr}".lower()
        if self.timed_out:
            return "timeout"
        if self.exit_code not in (0, None):
            for marker in (
                "rate limit",
                "too many requests",
                "overloaded",
                "unauthorized",
                "authentication",
                "not logged in",
                "connection",
                "network",
                "timed out",
            ):
                if marker in combined:
                    return marker
            return f"provider exited with status {self.exit_code}"
        if not self.stdout.strip():
            return "provider returned no output"
        return None

    @property
    def retryable(self) -> bool:
        combined = f"{self.stdout}\n{self.stderr}".lower()
        permanent_markers = (
            "invalid mcp configuration",
            "unknown option",
            "unexpected argument",
            "sandbox profile resolve failed",
            "not found",
        )
        return not any(marker in combined for marker in permanent_markers)


def _recursive_numbers(value: Any, keys: set[str]) -> list[int]:
    numbers: list[int] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in keys and isinstance(child, (int, float)):
                numbers.append(int(child))
            numbers.extend(_recursive_numbers(child, keys))
    elif isinstance(value, list):
        for child in value:
            numbers.extend(_recursive_numbers(child, keys))
    return numbers


def _parse_metrics(stdout: str) -> tuple[int, int, str]:
    documents: list[Any] = []
    for line in stdout.splitlines():
        try:
            documents.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if not documents:
        try:
            documents.append(json.loads(stdout))
        except json.JSONDecodeError:
            return 0, 0, ""

    totals = _recursive_numbers(
        documents,
        {"total_tokens", "totalTokens", "total_token_count"},
    )
    inputs = _recursive_numbers(documents, {"input_tokens", "inputTokens"})
    outputs = _recursive_numbers(documents, {"output_tokens", "outputTokens"})
    tool_calls = _recursive_numbers(
        documents,
        {"tool_calls", "toolCalls", "total_tool_calls"},
    )

    model = ""
    for document in documents:
        if isinstance(document, dict):
            candidate = document.get("model") or document.get("model_id")
            if isinstance(candidate, str):
                model = candidate
            model_usage = document.get("modelUsage")
            if isinstance(model_usage, dict) and model_usage:
                model = next(iter(model_usage))

    total = max(totals, default=0)
    if not total and (inputs or outputs):
        total = max(inputs, default=0) + max(outputs, default=0)
    return total, max(tool_calls, default=0), model


def provider_command(
    provider: str,
    run_repo: Path,
    prompt: str,
    config: dict[str, Any],
) -> tuple[list[str], str | None]:
    if provider == "codex":
        return (
            [
                "codex",
                "exec",
                "--ephemeral",
                "--ignore-user-config",
                "--ignore-rules",
                "--sandbox",
                "workspace-write",
                "--model",
                config["model"],
                "-c",
                f'model_reasoning_effort="{config["effort"]}"',
                "--json",
                "-C",
                str(run_repo),
                "-",
            ],
            prompt,
        )
    if provider == "claude":
        return (
            [
                "claude",
                "--safe-mode",
                "--disable-slash-commands",
                "--strict-mcp-config",
                "--mcp-config",
                '{"mcpServers":{}}',
                "--model",
                config["model"],
                "--effort",
                config["effort"],
                "--no-session-persistence",
                "--permission-mode",
                "acceptEdits",
                "--tools",
                "Read,Edit,Write,Glob,Grep",
                "--output-format",
                "json",
                "-p",
            ],
            prompt,
        )
    if provider == "copilot":
        return (
            [
                "copilot",
                "-C",
                str(run_repo),
                "--no-custom-instructions",
                "--disable-builtin-mcps",
                "--no-ask-user",
                "--no-remote",
                "--no-remote-export",
                "--disallow-temp-dir",
                "--deny-tool=shell",
                "--deny-tool=url",
                "--allow-tool=write",
                "--output-format",
                "json",
                "--no-color",
                "--no-auto-update",
                "-p",
                prompt,
            ],
            None,
        )
    if provider == "grok":
        return (
            [
                "grok",
                "--cwd",
                str(run_repo),
                "--single",
                prompt,
                "--no-memory",
                "--no-subagents",
                "--disable-web-search",
                "--verbatim",
                "--permission-mode",
                "acceptEdits",
                "--always-approve",
                "--sandbox",
                "workspace",
                "--disallowed-tools",
                "Execute,WebSearch,WebFetch",
                "--output-format",
                "json",
                "--system-prompt-override",
                (
                    "Work only in the current repository. Use only file reading, "
                    "search, and editing tools. Do not use installed skills, "
                    "network access, subagents, or shell commands. Follow the "
                    "user prompt and the skill file it identifies."
                ),
            ],
            None,
        )
    raise KeyError(provider)


def execute_provider(
    provider: str,
    run_repo: Path,
    prompt: str,
    config: dict[str, Any],
    timeout_seconds: int,
) -> ProviderResult:
    command, stdin = provider_command(provider, run_repo, prompt, config)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=run_repo,
            input=stdin,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            env={**os.environ, "NO_COLOR": "1"},
        )
        timed_out = False
        exit_code: int | None = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as error:
        timed_out = True
        exit_code = None
        stdout = error.stdout if isinstance(error.stdout, str) else ""
        stderr = error.stderr if isinstance(error.stderr, str) else ""

    duration = time.monotonic() - started
    total_tokens, tool_calls, detected_model = _parse_metrics(stdout)
    model = detected_model or str(config.get("model", "default"))
    return ProviderResult(
        command=command,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        duration_seconds=duration,
        timed_out=timed_out,
        total_tokens=total_tokens,
        tool_calls=tool_calls,
        model=model,
    )


def preflight_versions(providers: list[str]) -> dict[str, dict[str, Any]]:
    checks: dict[str, dict[str, Any]] = {}
    version_commands = {
        "codex": ["codex", "--version"],
        "claude": ["claude", "--version"],
        "copilot": ["copilot", "--version"],
        "grok": ["grok", "--version"],
    }
    auth_commands = {
        "codex": ["codex", "login", "status"],
        "claude": ["claude", "auth", "status"],
        "grok": ["grok", "models"],
    }
    for provider in providers:
        executable = shutil.which(provider)
        if not executable:
            checks[provider] = {"ok": False, "error": "executable not found"}
            continue
        version = subprocess.run(
            version_commands[provider],
            capture_output=True,
            text=True,
            timeout=30,
        )
        auth = None
        if provider in auth_commands:
            auth = subprocess.run(
                auth_commands[provider],
                capture_output=True,
                text=True,
                timeout=60,
            )
        checks[provider] = {
            "ok": version.returncode == 0 and (auth is None or auth.returncode == 0),
            "path": executable,
            "version": (version.stdout or version.stderr).strip(),
            "auth": None if auth is None else (auth.stdout or auth.stderr).strip(),
        }
    return checks
