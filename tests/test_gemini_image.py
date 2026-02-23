import pytest
from unittest.mock import MagicMock
from services.gemini_image import GeminiImageService

def test_init(mocker):
    mock_client = mocker.patch('services.gemini_image.genai.Client')
    service = GeminiImageService("fake_key", "fake_model")
    mock_client.assert_called_once_with(api_key="fake_key")
    assert service.model_name == "fake_model"

def test_generate_image_file_success(mocker):
    service = GeminiImageService("fake_key")
    mock_generate = mocker.patch.object(service._client.models, 'generate_images', return_value=MagicMock(
        generated_images=[MagicMock(image=MagicMock(save=lambda path: None))]
    ))
    result = service.generate_image_file("test prompt", "output.jpg", "1:1")
    assert result == "output.jpg"
    mock_generate.assert_called_once_with(
        model=service.model_name,
        prompt="test prompt",
        config=dict(
            number_of_images=1,
            output_mime_type="image/jpeg",
            aspect_ratio="1:1",
            image_size="1K",
        ),
    )

def test_generate_image_from_image_and_text_success(mocker):
    service = GeminiImageService("fake_key")
    mock_generate_stream = mocker.patch.object(service._client.models, 'generate_content_stream', return_value=[
        MagicMock(candidates=[MagicMock(content=MagicMock(parts=[MagicMock(inline_data=MagicMock(data=b'fake_data', mime_type="image/jpeg"))]))])
    ])
    mocker.patch('mimetypes.guess_type', return_value=("image/jpeg", None))
    mocker.patch('mimetypes.guess_extension', return_value=".jpg")

    # Create a temporary JPG file with fake data
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        temp_file.write(b'fake_image_data')  # Write some dummy bytes to simulate an image
        temp_input_path = temp_file.name

    # Mock open to return the fake data (in case the method reads it)
    mocker.patch('builtins.open', mocker.mock_open(read_data=b'fake_image_data'))

    try:
        result = service.generate_image_from_image_and_text(temp_input_path, "test prompt", "output.jpg")
        assert result == "output.jpg"
    finally:
        # Clean up the temp file
        import os
        os.unlink(temp_input_path)