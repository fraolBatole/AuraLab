from __future__ import annotations

import base64
import logging
import mimetypes
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types


log = logging.getLogger(__name__)


class GeminiImageService:
    def __init__(self, api_key: str, model_name: str = "models/imagen-4.0-generate-001") -> None:
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is required")
        self._client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_image_file(
        self,
        prompt: str,
        output_path: str | Path,
        aspect_ratio: str = "9:16",
    ) -> Optional[str]:
        try:
            result = self._client.models.generate_images(
                model=self.model_name,
                prompt=prompt,
                config=dict(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio=aspect_ratio,
                    image_size="1K",
                ),
            )
            if not getattr(result, "generated_images", None):
                log.error("No images generated for prompt")
                return None
            if len(result.generated_images) != 1:
                log.warning("Generated %d images; expected 1", len(result.generated_images))
            out = Path(output_path)
            # SDK provides convenience save()
            for idx, generated_image in enumerate(result.generated_images):
                # For single image, write to requested output_path
                if idx == 0:
                    generated_image.image.save(str(out))
                else:
                    generated_image.image.save(str(out.with_name(f"{out.stem}_{idx}{out.suffix}")))
            return str(out)
        except Exception as exc:
            log.exception("Gemini image generation failed: %s", exc)
            return None

    def generate_image_from_image_and_text(
        self,
        image_path: str | Path,
        prompt: str,
        output_path: str | Path,
    ) -> Optional[str]:
        """
        Generate image from input image + text prompt using gemini-2.5-flash-image-preview model.
        Similar to the provided code snippet but reads image from file instead of base64.
        """
        try:
            image_file = Path(image_path)
            if not image_file.exists():
                log.error("Image file does not exist: %s", image_path)
                return None

            log.info("Starting image-to-image generation with image: %s", image_path)
            
            # Read the image file
            with open(image_file, "rb") as f:
                image_bytes = f.read()
            
            # Detect mime type
            mime_type, _ = mimetypes.guess_type(str(image_file))
            if not mime_type or not mime_type.startswith('image/'):
                mime_type = "image/jpeg"  # fallback
            
            # Use the multimodal model for image-to-image generation
            model = "gemini-2.5-flash-image-preview"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(
                            mime_type=mime_type,
                            data=image_bytes,
                        ),
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                response_modalities=[
                    "IMAGE",
                    "TEXT",
                ],
            )

            output_file = Path(output_path)
            file_index = 0
            generated_file = None
            
            for chunk in self._client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue
                
                # Look for image data in the response
                if (chunk.candidates[0].content.parts[0].inline_data and 
                    chunk.candidates[0].content.parts[0].inline_data.data):
                    inline_data = chunk.candidates[0].content.parts[0].inline_data
                    data_buffer = inline_data.data
                    file_extension = mimetypes.guess_extension(inline_data.mime_type)
                    if not file_extension:
                        file_extension = ".jpg"  # fallback
                    
                    # Use the specified output path for the first image
                    if file_index == 0:
                        generated_file = output_file.with_suffix(file_extension)
                    else:
                        generated_file = output_file.with_name(f"{output_file.stem}_{file_index}{file_extension}")
                    
                    # Save the binary file
                    with open(generated_file, "wb") as f:
                        f.write(data_buffer)
                    
                    log.info("Image generated and saved to: %s", generated_file)
                    file_index += 1
                else:
                    # Log text responses (if any)
                    if hasattr(chunk, 'text') and chunk.text:
                        log.debug("Generated text: %s", chunk.text)
            
            return str(generated_file) if generated_file else None

        except Exception as exc:
            log.exception("Gemini image-to-image generation failed: %s", exc)
            return None

