from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Optional
from google.genai import types
from google import genai

log = logging.getLogger(__name__)


class GeminiVideoService:
    def __init__(
        self,
        api_key: str,
        model_name: str = "veo-3.0-fast-generate-001",
        default_aspect_ratio: str = "9:16",
    ) -> None:
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is required")
        self._client = genai.Client(api_key=api_key)
        self.model_name = model_name
        # Model for text-to-video generation
        self.text_to_video_model = "veo-3.0-fast-generate-001"
        self.default_aspect_ratio = default_aspect_ratio

    async def generate_video_from_prompt(
        self,
        prompt: str,
        output_path: str | Path,
        progress_callback=None,
    ) -> Optional[str]:
        """
        Generate a video from a text prompt.
        This is the basic implementation based on the sample code.
        """
        try:
            log.info(
                "Starting video generation with prompt: %s",
                prompt[:100] + "..." if len(prompt) > 100 else prompt,
            )

            video_config = types.GenerateVideosConfig(
                aspect_ratio=self.default_aspect_ratio,
                number_of_videos=1,  # supported values: 1 - 4
                duration_seconds=8,  # supported values: 5 - 8
                resolution="720p",
                person_generation="allow_all",
            )

            operation = self._client.models.generate_videos(
                model=self.text_to_video_model,
                prompt=prompt,
                config=video_config,
            )

            # Poll the operation status until the video is ready.
            wait_count = 0
            max_wait_iterations = 90  # Maximum 30 minutes of waiting (90 * 20 seconds)
            while not operation.done and wait_count < max_wait_iterations:
                await asyncio.sleep(20)
                wait_count += 1

                if progress_callback:
                    elapsed_seconds = wait_count * 20
                    minutes = elapsed_seconds // 60
                    if wait_count % 3 == 0:  # every minute
                        await progress_callback(
                            f"Video generation in progress... ({minutes} minutes elapsed)"
                        )

                operation = self._client.operations.get(operation)

            # Check if we timed out
            if wait_count >= max_wait_iterations:
                log.error(
                    "Video generation timed out after %d minutes",
                    max_wait_iterations * 20 // 60,
                )
                return None

            # Download the generated video.
            if (hasattr(operation, 'response') and
                hasattr(operation.response, 'generated_videos') and
                operation.response.generated_videos):
                generated_video = operation.response.generated_videos[0]

                # Download and save the video
                out_path = Path(output_path)
                self._client.files.download(file=generated_video.video)
                generated_video.video.save(str(out_path))

                log.info("Video generated and saved to: %s", out_path)
                return str(out_path)
            else:
                log.error("No video generated in response")
                return None

        except Exception as exc:
            log.exception("Gemini video generation failed: %s", exc)
            return None

    async def generate_video_from_image_and_prompt(
        self,
        image_path: str | Path,
        video_prompt: str,
        output_path: str | Path,
        progress_callback=None,
    ) -> Optional[str]:
        """
        Generate a video using an uploaded image as reference.
        This uses Veo 3.0's image-to-video capabilities.
        """
        try:
            video_config = types.GenerateVideosConfig(
                aspect_ratio=self.default_aspect_ratio,
                resolution="720p",
                person_generation="allow_adult",
            )

            image_file = Path(image_path)
            if not image_file.exists():
                log.error("Image file does not exist: %s", image_path)
                return None

            log.info("Starting Veo 3.0 video generation with image: %s", image_path)
            
            with open(image_file, "rb") as image_file:
                image_bytes = image_file.read()

            # Try using the image as part of a multimodal prompt for Veo 3.0
            enhanced_prompt = f"Using this reference image to create a video: {video_prompt}"

            operation = self._client.models.generate_videos(
                model=self.model_name,
                prompt=enhanced_prompt,
                image=types.Image(image_bytes=image_bytes,mime_type="image/jpeg"),
                config=video_config,
            )

            # Poll the operation status until the video is ready
            wait_count = 0
            max_wait_iterations = 90
            while not operation.done and wait_count < max_wait_iterations:
                await asyncio.sleep(20)
                wait_count += 1

                if progress_callback:
                    elapsed_seconds = wait_count * 20
                    minutes = elapsed_seconds // 60
                    if wait_count % 3 == 0:
                        await progress_callback(
                            f"Image-to-video generation in progress... ({minutes} minutes elapsed)"
                        )

                operation = self._client.operations.get(operation)

            # Check if we timed out
            if wait_count >= max_wait_iterations:
                log.error(
                    "Image-to-video generation timed out after %d minutes",
                    max_wait_iterations * 20 // 60,
                )
                return None

            # Download the generated video
            if hasattr(operation, 'response') and hasattr(operation.response, 'generated_videos'):
                generated_video = operation.response.generated_videos[0]

                # Download and save the video
                out_path = Path(output_path)
                self._client.files.download(file=generated_video.video)
                generated_video.video.save(str(out_path))

                log.info("Video generated from image and saved to: %s", out_path)
                return str(out_path)
            else:
                log.error("No video generated in response")
                return None

        except Exception as exc:
            log.exception("Veo 3.0 video generation from image failed: %s", exc)
            return None