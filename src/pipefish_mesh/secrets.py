"""Secret broker: resolve names without logging values."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class SecretBackend(Protocol):
    def get(self, name: str) -> str | None: ...


@dataclass(frozen=True, slots=True)
class SecretRef:
    name: str
    backend: str


class EnvBackend:
    def get(self, name: str) -> str | None:
        value = os.environ.get(name)
        return value if value else None


class FileBackend:
    """JSON object or KEY=VALUE file. Missing files are ignored."""

    def __init__(self, path: str | Path | None) -> None:
        self.path = Path(path) if path else None

    def get(self, name: str) -> str | None:
        if not self.path or not self.path.exists():
            return None
        text = self.path.read_text(encoding="utf-8")
        if self.path.suffix == ".json":
            data = json.loads(text)
            value = data.get(name)
            return str(value) if value is not None else None
        for line in text.splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == name:
                return value.strip().strip('"').strip("'")
        return None


class AwsSsmBackend:
    """Optional AWS SSM adapter. Import is deferred so boto3 is not required."""

    def __init__(self, prefix: str = "", region: str | None = None) -> None:
        self.prefix = prefix
        self.region = region

    def get(self, name: str) -> str | None:
        try:
            import boto3  # type: ignore[import-untyped]
        except ImportError:
            return None
        client = boto3.client("ssm", region_name=self.region)
        parameter = f"{self.prefix.rstrip('/')}/{name}" if self.prefix else name
        try:
            response = client.get_parameter(Name=parameter, WithDecryption=True)
        except Exception:  # noqa: BLE001 — backend is optional
            return None
        return response.get("Parameter", {}).get("Value")


class SecretBroker:
    """Resolve secrets from env, then a local file, then AWS SSM."""

    def __init__(
        self,
        *,
        file_path: str | Path | None = None,
        ssm_prefix: str | None = None,
        region: str | None = None,
    ) -> None:
        path = file_path if file_path is not None else os.environ.get("PIPEFISH_SECRET_FILE")
        prefix = ssm_prefix if ssm_prefix is not None else os.environ.get("PIPEFISH_SSM_PREFIX", "")
        aws_region = region or os.environ.get("AWS_REGION")
        self._backends: list[tuple[str, SecretBackend]] = [
            ("env", EnvBackend()),
            ("file", FileBackend(path)),
            ("aws_ssm", AwsSsmBackend(prefix=prefix or "", region=aws_region)),
        ]

    def get(self, name: str, default: str | None = None) -> str:
        for _, backend in self._backends:
            value = backend.get(name)
            if value:
                return value
        if default is not None:
            return default
        raise KeyError(f"secret {name} was not found in any configured backend")

    def source_of(self, name: str) -> SecretRef | None:
        for label, backend in self._backends:
            if backend.get(name):
                return SecretRef(name=name, backend=label)
        return None
