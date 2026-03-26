"""Tests for AI image parser — uses mocked Claude Vision API."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from promptbim.land.parsers.image_ai import (
    build_parcel_from_ai_data,
    parse_image_ai,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "land_images"

MOCK_AI_RESPONSE = {
    "boundary": [[0, 0], [20, 0], [20, 15], [0, 15]],
    "area_sqm": 300.0,
    "scale": "1:500",
    "orientation": "north_up",
    "annotations": {
        "lot_number": "123-4",
        "dimensions": ["20m", "15m"],
        "zoning": "residential",
    },
    "confidence": 0.85,
    "notes": "Clear rectangular parcel with dimension annotations",
}


class TestBuildParcelFromAIData:
    def test_basic_rectangle(self):
        parcel = build_parcel_from_ai_data(MOCK_AI_RESPONSE)
        assert parcel is not None
        assert parcel.name == "123-4"  # lot_number
        assert parcel.source_type == "ai_image"
        assert parcel.area_sqm == 300.0
        assert parcel.ai_confidence == 0.85
        assert len(parcel.boundary) == 4

    def test_no_boundary(self):
        data = {"confidence": 0.5}
        assert build_parcel_from_ai_data(data) is None

    def test_too_few_points(self):
        data = {"boundary": [[0, 0], [10, 0]], "confidence": 0.5}
        assert build_parcel_from_ai_data(data) is None

    def test_area_computed_if_missing(self):
        data = {
            "boundary": [[0, 0], [10, 0], [10, 10], [0, 10]],
            "confidence": 0.7,
        }
        parcel = build_parcel_from_ai_data(data)
        assert parcel is not None
        assert abs(parcel.area_sqm - 100.0) < 0.01

    def test_annotations_stored(self):
        parcel = build_parcel_from_ai_data(MOCK_AI_RESPONSE)
        assert parcel.ai_annotations is not None
        assert parcel.ai_annotations["zoning"] == "residential"

    def test_source_path_stored(self):
        parcel = build_parcel_from_ai_data(MOCK_AI_RESPONSE, source_path=Path("/tmp/test.jpg"))
        assert parcel.original_image_path == "/tmp/test.jpg"

    def test_default_name_when_no_annotations(self):
        data = {
            "boundary": [[0, 0], [10, 0], [10, 10], [0, 10]],
            "confidence": 0.6,
            "annotations": {},
        }
        parcel = build_parcel_from_ai_data(data)
        assert parcel.name == "AI-Recognized Parcel"


class TestParseImageAI:
    def test_file_not_found(self):
        result = parse_image_ai("/nonexistent/image.jpg")
        assert not result.ok
        assert "not found" in result.error.lower()

    def test_unsupported_format(self, tmp_path):
        p = tmp_path / "data.csv"
        p.write_text("col1,col2")
        result = parse_image_ai(p)
        assert not result.ok
        assert "unsupported" in result.error.lower()

    @patch("promptbim.land.parsers.image_ai.prepare_for_vision_api")
    @patch("promptbim.agents.land_reader.LandReaderAgent")
    def test_successful_recognition(self, MockAgent, mock_prepare, tmp_path):
        """Full flow with mocked API."""
        # Create a real image file
        from PIL import Image

        from promptbim.agents.base import AgentResponse

        img = Image.new("RGB", (100, 100), color=(200, 200, 200))
        img_path = tmp_path / "test_land.jpg"
        img.save(img_path)

        mock_prepare.return_value = ("base64data", "image/jpeg")

        mock_agent = MagicMock()
        mock_agent.analyse_image.return_value = AgentResponse(
            text="", json_data=MOCK_AI_RESPONSE, usage={}
        )
        MockAgent.return_value = mock_agent

        result = parse_image_ai(img_path)
        assert result.ok
        assert len(result.parcels) == 1
        assert result.confidence == 0.85
        parcel = result.parcels[0]
        assert parcel.source_type == "ai_image"
        assert len(parcel.boundary) == 4

    @patch("promptbim.land.parsers.image_ai.prepare_for_vision_api")
    @patch("promptbim.agents.land_reader.LandReaderAgent")
    def test_api_failure(self, MockAgent, mock_prepare, tmp_path):
        from PIL import Image

        from promptbim.agents.base import AgentResponse

        img = Image.new("RGB", (100, 100))
        img_path = tmp_path / "test.jpg"
        img.save(img_path)

        mock_prepare.return_value = ("base64data", "image/jpeg")
        mock_agent = MagicMock()
        mock_agent.analyse_image.return_value = AgentResponse(error="API timeout")
        MockAgent.return_value = mock_agent

        result = parse_image_ai(img_path)
        assert not result.ok
        assert "failed" in result.error.lower()

    @patch("promptbim.land.parsers.image_ai.prepare_for_vision_api")
    @patch("promptbim.agents.land_reader.LandReaderAgent")
    def test_no_boundary_in_response(self, MockAgent, mock_prepare, tmp_path):
        from PIL import Image

        from promptbim.agents.base import AgentResponse

        img = Image.new("RGB", (100, 100))
        img_path = tmp_path / "test.jpg"
        img.save(img_path)

        mock_prepare.return_value = ("b64", "image/jpeg")
        mock_agent = MagicMock()
        mock_agent.analyse_image.return_value = AgentResponse(
            text="", json_data={"confidence": 0.2, "notes": "No land visible"}, usage={}
        )
        MockAgent.return_value = mock_agent

        result = parse_image_ai(img_path)
        assert not result.ok


class TestLandReaderAgent:
    """Test the LandReaderAgent (mocked API)."""

    def test_analyse_image_mock(self):
        import json

        from promptbim.agents.land_reader import LandReaderAgent

        agent = LandReaderAgent()

        mock_text_block = MagicMock()
        mock_text_block.text = json.dumps(MOCK_AI_RESPONSE)

        mock_msg = MagicMock()
        mock_msg.content = [mock_text_block]
        mock_msg.usage.input_tokens = 100
        mock_msg.usage.output_tokens = 200

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_msg
        agent._client = mock_client

        response = agent.analyse_image("b64data", "image/jpeg")
        assert response.ok
        assert response.json_data is not None
        assert response.json_data["confidence"] == 0.85
