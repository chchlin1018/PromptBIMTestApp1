"""NVIDIA Omniverse connection module.

Provides a connector for pushing USD files to an Omniverse Nucleus server.
Uses the Omniverse Client Library when available, with a fallback
HTTP upload via the Nucleus REST API.

This module is optional — Omniverse is not required for the core workflow.
"""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

DEFAULT_NUCLEUS_URL = "omniverse://localhost"
DEFAULT_PROJECT_PATH = "/Projects/PromptBIM"


@dataclass
class OmniverseConfig:
    """Configuration for Omniverse Nucleus connection."""

    nucleus_url: str = DEFAULT_NUCLEUS_URL
    project_path: str = DEFAULT_PROJECT_PATH
    username: str = ""
    password: str = ""


@dataclass
class OmniverseResult:
    """Result of an Omniverse operation."""

    success: bool
    message: str
    remote_path: str = ""
    method: str = ""  # "client_lib" or "http" or "local_copy"


class OmniverseConnector:
    """Connector for NVIDIA Omniverse Nucleus server.

    Usage:
        connector = OmniverseConnector(config)
        result = connector.test_connection()
        if result.success:
            result = connector.upload_usd(local_path)
    """

    def __init__(self, config: OmniverseConfig | None = None) -> None:
        self._config = config or OmniverseConfig()
        self._client_available = self._check_client_library()

    def _check_client_library(self) -> bool:
        """Check if Omniverse Client Library is available."""
        try:
            import omni.client  # noqa: F401

            return True
        except ImportError:
            return False

    def test_connection(self) -> OmniverseResult:
        """Test connection to Omniverse Nucleus server.

        Returns:
            OmniverseResult with connection status.
        """
        if self._client_available:
            return self._test_connection_client_lib()

        # Try HTTP endpoint
        return self._test_connection_http()

    def upload_usd(
        self,
        local_path: str | Path,
        remote_name: str | None = None,
    ) -> OmniverseResult:
        """Upload a USD file to Omniverse Nucleus.

        Args:
            local_path: Path to the local USD/USDA/USDZ file.
            remote_name: Optional remote filename (defaults to local filename).

        Returns:
            OmniverseResult with upload status.
        """
        local_path = Path(local_path)
        if not local_path.exists():
            return OmniverseResult(
                success=False,
                message=f"File not found: {local_path}",
            )

        remote_name = remote_name or local_path.name
        remote_path = f"{self._config.project_path}/{remote_name}"

        if self._client_available:
            return self._upload_client_lib(local_path, remote_path)

        return self._upload_http(local_path, remote_path)

    def list_files(self, remote_dir: str | None = None) -> OmniverseResult:
        """List files in a Nucleus directory."""
        remote_dir = remote_dir or self._config.project_path

        if self._client_available:
            return self._list_client_lib(remote_dir)

        return OmniverseResult(
            success=False,
            message="Omniverse Client Library not installed. "
                    "Install via: pip install omni-client (requires Omniverse SDK)",
            method="none",
        )

    # --- Client Library methods ---

    def _test_connection_client_lib(self) -> OmniverseResult:
        """Test connection using omni.client."""
        try:
            import omni.client

            result = omni.client.stat(self._config.nucleus_url)
            if result[0] == omni.client.Result.OK:
                return OmniverseResult(
                    success=True,
                    message=f"Connected to {self._config.nucleus_url}",
                    method="client_lib",
                )
            return OmniverseResult(
                success=False,
                message=f"Connection failed: {result[0]}",
                method="client_lib",
            )
        except Exception as exc:
            return OmniverseResult(
                success=False,
                message=f"Client library error: {exc}",
                method="client_lib",
            )

    def _upload_client_lib(self, local_path: Path, remote_path: str) -> OmniverseResult:
        """Upload using omni.client."""
        try:
            import omni.client

            full_url = f"{self._config.nucleus_url}{remote_path}"
            data = local_path.read_bytes()

            result = omni.client.write_file(full_url, data)
            if result == omni.client.Result.OK:
                return OmniverseResult(
                    success=True,
                    message=f"Uploaded to {full_url}",
                    remote_path=full_url,
                    method="client_lib",
                )
            return OmniverseResult(
                success=False,
                message=f"Upload failed: {result}",
                method="client_lib",
            )
        except Exception as exc:
            return OmniverseResult(
                success=False,
                message=f"Upload error: {exc}",
                method="client_lib",
            )

    def _list_client_lib(self, remote_dir: str) -> OmniverseResult:
        """List files using omni.client."""
        try:
            import omni.client

            full_url = f"{self._config.nucleus_url}{remote_dir}"
            result, entries = omni.client.list(full_url)
            if result == omni.client.Result.OK:
                names = [e.relative_path for e in entries]
                return OmniverseResult(
                    success=True,
                    message=json.dumps(names),
                    remote_path=full_url,
                    method="client_lib",
                )
            return OmniverseResult(
                success=False,
                message=f"List failed: {result}",
                method="client_lib",
            )
        except Exception as exc:
            return OmniverseResult(
                success=False,
                message=f"List error: {exc}",
                method="client_lib",
            )

    # --- HTTP fallback methods ---

    def _test_connection_http(self) -> OmniverseResult:
        """Test Nucleus connection via HTTP health endpoint."""
        parsed = urlparse(self._config.nucleus_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 3009  # default Nucleus web port

        try:
            import urllib.request

            url = f"http://{host}:{port}/omni/discovery"
            req = urllib.request.Request(url, method="GET")
            req.add_header("Accept", "application/json")

            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return OmniverseResult(
                        success=True,
                        message=f"Nucleus reachable at {host}:{port}",
                        method="http",
                    )
        except Exception as exc:
            pass

        return OmniverseResult(
            success=False,
            message=f"Omniverse Nucleus not reachable at {host}:{port}. "
                    "Ensure Omniverse Nucleus is running or install omni-client.",
            method="http",
        )

    def _upload_http(self, local_path: Path, remote_path: str) -> OmniverseResult:
        """Upload via Nucleus REST API (simplified)."""
        # Without omni.client, we can't easily upload.
        # Return guidance on how to set up.
        return OmniverseResult(
            success=False,
            message=(
                "HTTP upload requires Omniverse Client Library. "
                "Install via Omniverse Launcher or: pip install omni-client. "
                f"File ready for manual upload: {local_path} -> {remote_path}"
            ),
            remote_path=remote_path,
            method="http",
        )
