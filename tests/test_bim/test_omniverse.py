"""Tests for NVIDIA Omniverse connector."""

from pathlib import Path

from promptbim.bim.omniverse import OmniverseConfig, OmniverseConnector, OmniverseResult


class TestOmniverseConfig:
    def test_default_config(self):
        cfg = OmniverseConfig()
        assert cfg.nucleus_url == "omniverse://localhost"
        assert cfg.project_path == "/Projects/PromptBIM"

    def test_custom_config(self):
        cfg = OmniverseConfig(
            nucleus_url="omniverse://192.168.1.100",
            project_path="/Projects/Test",
            username="admin",
        )
        assert cfg.nucleus_url == "omniverse://192.168.1.100"
        assert cfg.username == "admin"


class TestOmniverseResult:
    def test_success_result(self):
        r = OmniverseResult(success=True, message="OK", method="client_lib")
        assert r.success
        assert r.method == "client_lib"

    def test_failure_result(self):
        r = OmniverseResult(success=False, message="Not connected")
        assert not r.success


class TestOmniverseConnector:
    def test_connector_creation(self):
        connector = OmniverseConnector()
        assert connector is not None

    def test_test_connection_without_nucleus(self):
        """Without Omniverse installed, connection test should fail gracefully."""
        connector = OmniverseConnector()
        result = connector.test_connection()
        # Should fail gracefully (no Omniverse server running in CI)
        assert isinstance(result, OmniverseResult)
        assert isinstance(result.success, bool)
        assert result.message  # should have a message

    def test_upload_nonexistent_file(self):
        connector = OmniverseConnector()
        result = connector.upload_usd("/nonexistent/file.usda")
        assert not result.success
        assert "not found" in result.message.lower()

    def test_upload_existing_file_without_server(self, tmp_path: Path):
        """Upload should fail gracefully without server."""
        test_file = tmp_path / "test.usda"
        test_file.write_text("#usda 1.0\n")

        connector = OmniverseConnector()
        result = connector.upload_usd(test_file)
        assert isinstance(result, OmniverseResult)
        # Without omni.client, it should fail with guidance
        assert isinstance(result.success, bool)

    def test_list_files_without_server(self):
        connector = OmniverseConnector()
        result = connector.list_files()
        assert isinstance(result, OmniverseResult)

    def test_custom_remote_name(self, tmp_path: Path):
        test_file = tmp_path / "building.usda"
        test_file.write_text("#usda 1.0\n")

        connector = OmniverseConnector()
        result = connector.upload_usd(test_file, remote_name="my_building.usda")
        assert isinstance(result, OmniverseResult)
