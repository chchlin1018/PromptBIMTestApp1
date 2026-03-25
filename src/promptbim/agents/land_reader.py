"""Land Reader Agent — Claude Vision-based land image analysis.

Analyses photos, screenshots, scanned cadastral maps, and hand-drawn
sketches to extract land boundary polygons and metadata.
"""

from __future__ import annotations

import json
import logging

from promptbim.agents.base import AgentResponse, BaseAgent, _try_extract_json

logger = logging.getLogger(__name__)

LAND_READER_SYSTEM_PROMPT = """\
You are an expert land surveyor and GIS analyst. Your task is to analyse an
image of a land parcel and extract the boundary polygon coordinates.

## INPUT
You will receive an image (photo, map screenshot, scanned document, or sketch)
along with optional context about scale and location.

## OUTPUT
Return a JSON object with the following fields:

```json
{
  "boundary": [[x1,y1], [x2,y2], ...],
  "area_sqm": <estimated area in square metres or null>,
  "scale": "<scale string like '1:500' or null>",
  "orientation": "<'north_up' or rotation angle in degrees or null>",
  "annotations": {
    "lot_number": "<land lot number or null>",
    "dimensions": ["12.5m", "8.3m"],
    "zoning": "<zoning type or null>",
    "address": "<address or null>"
  },
  "confidence": <0.0 to 1.0>,
  "notes": "<any observations about the image>"
}
```

## RULES
1. The boundary MUST be a closed polygon (first and last points can be same or different — the system will close it).
2. Coordinates should be in METRES relative to an arbitrary local origin (bottom-left of the parcel as (0,0)).
3. If the image has a scale bar or dimension annotations, use them to estimate real dimensions.
4. If no scale information exists, estimate based on typical land parcel sizes and any visible context clues.
5. The boundary should trace the outer edge of the land parcel as accurately as possible.
6. Set confidence low (< 0.5) if the image is unclear or the boundary is ambiguous.
7. For hand-drawn sketches, extract the intended shape even if imprecise.
8. Always return valid JSON. Do not include any text outside the JSON object.
"""


class LandReaderAgent(BaseAgent):
    """Analyses land images using Claude Vision to extract boundary data."""

    SYSTEM_PROMPT = LAND_READER_SYSTEM_PROMPT

    def __init__(self, model: str | None = None, max_tokens: int = 4096) -> None:
        super().__init__(model=model, max_tokens=max_tokens)

    def analyse_image(
        self,
        image_b64: str,
        media_type: str = "image/jpeg",
        context: str | None = None,
    ) -> AgentResponse:
        """Analyse a land image and return boundary data.

        Args:
            image_b64: Base64-encoded image data.
            media_type: MIME type (image/jpeg or image/png).
            context: Optional context string (e.g., location, expected size).

        Returns:
            AgentResponse with json_data containing boundary info.
        """
        user_text = (
            "Analyse this land parcel image. Extract the boundary polygon "
            "coordinates and any visible annotations (dimensions, lot number, "
            "scale, zoning). Return the result as a JSON object."
        )
        if context:
            user_text += f"\n\nAdditional context: {context}"

        try:
            message = self.client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=self.SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_b64,
                                },
                            },
                            {"type": "text", "text": user_text},
                        ],
                    }
                ],
            )
            text = message.content[0].text
            usage = {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }
            json_data = _try_extract_json(text)
            return AgentResponse(text=text, json_data=json_data, usage=usage)
        except Exception as exc:
            logger.exception("LandReaderAgent Vision API call failed")
            return AgentResponse(error=str(exc))

    def refine_boundary(
        self,
        image_b64: str,
        media_type: str,
        previous_result: dict,
        feedback: str,
    ) -> AgentResponse:
        """Re-analyse with feedback for multi-round correction.

        Args:
            image_b64: Base64-encoded image data.
            media_type: MIME type.
            previous_result: The previous analysis JSON.
            feedback: User feedback for correction.
        """
        try:
            message = self.client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=self.SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_b64,
                                },
                            },
                            {
                                "type": "text",
                                "text": (
                                    "Analyse this land parcel image and extract "
                                    "boundary coordinates as JSON."
                                ),
                            },
                        ],
                    },
                    {
                        "role": "assistant",
                        "content": json.dumps(previous_result, ensure_ascii=False),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Please adjust the boundary based on this feedback: "
                            f"{feedback}\n\nReturn the corrected JSON."
                        ),
                    },
                ],
            )
            text = message.content[0].text
            usage = {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }
            json_data = _try_extract_json(text)
            return AgentResponse(text=text, json_data=json_data, usage=usage)
        except Exception as exc:
            logger.exception("LandReaderAgent refinement failed")
            return AgentResponse(error=str(exc))
