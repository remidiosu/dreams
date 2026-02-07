import base64
import json

from google import genai
from google.genai import types

from app.config import settings
from app.logger import logger
from app.services.gemini_client import generate_content_with_retry


class MultimodalService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.llm_model

    async def transcribe_audio(self, audio_bytes: bytes, mime_type: str) -> str:
        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)

        response = generate_content_with_retry(
            self.client,
            self.model,
            [
                types.Content(
                    role="user",
                    parts=[
                        audio_part,
                        types.Part(text=(
                            "Transcribe this audio recording of someone describing a dream. "
                            "Output ONLY the transcribed text, nothing else. "
                            "Clean up filler words and false starts but preserve the dream content faithfully."
                        )),
                    ],
                )
            ],
            types.GenerateContentConfig(
                temperature=0.3,
            ),
        )

        transcript = ""
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    transcript += part.text

        return transcript.strip()

    async def analyze_images(
        self, images: list[dict]
    ) -> list[dict]:
        results = []

        for image_data in images:
            image_bytes = base64.b64decode(image_data["base64"])
            image_part = types.Part.from_bytes(
                data=image_bytes, mime_type=image_data["mime_type"]
            )

            caption = image_data.get("caption", "")
            caption_text = f'\nThe user described this image as: "{caption}"' if caption else ""

            response = generate_content_with_retry(
                self.client,
                self.model,
                [
                    types.Content(
                        role="user",
                        parts=[
                            image_part,
                            types.Part(text=(
                                "Analyze this dream-related image (a sketch, painting, or photo representing a dream). "
                                f"{caption_text}\n\n"
                                "Extract dream elements from the visual content. Respond with ONLY valid JSON:\n"
                                "{\n"
                                '  "description": "Brief description of what the image depicts",\n'
                                '  "symbols": [{"name": "symbol_name", "category": "object|place|action|animal|nature|body|other", "context": "how it appears in the image"}],\n'
                                '  "characters": [{"name": "character_name", "character_type": "known_person|unknown_person|self|animal|mythical|abstract", "context": "how they appear"}],\n'
                                '  "themes": ["theme1", "theme2"],\n'
                                '  "emotions": ["emotion1", "emotion2"]\n'
                                "}"
                            )),
                        ],
                    )
                ],
                types.GenerateContentConfig(
                    temperature=0.7,
                    thinking_config=types.ThinkingConfig(thinking_level="high"),
                ),
            )

            raw = ""
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, "text") and part.text:
                        raw += part.text

            try:
                cleaned = raw.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
                    if cleaned.endswith("```"):
                        cleaned = cleaned[:-3]
                    cleaned = cleaned.strip()

                parsed = json.loads(cleaned)
                results.append({
                    "description": parsed.get("description", ""),
                    "symbols": parsed.get("symbols", []),
                    "characters": parsed.get("characters", []),
                    "themes": parsed.get("themes", []),
                    "emotions": parsed.get("emotions", []),
                })
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Failed to parse image analysis response: {e}, raw: {raw[:500]}")
                results.append({
                    "description": raw[:200] if raw else "Could not analyze image",
                    "symbols": [],
                    "characters": [],
                    "themes": [],
                    "emotions": [],
                })

        return results


_multimodal_service: MultimodalService | None = None


def get_multimodal_service() -> MultimodalService:
    global _multimodal_service
    if _multimodal_service is None:
        _multimodal_service = MultimodalService()

    return _multimodal_service
