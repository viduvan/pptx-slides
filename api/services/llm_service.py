"""
LLM Service — Google Gemini API integration (using google-genai SDK).
Replaces the OpenAI-based llm_ops.py for the API backend.
"""
import json
import logging
import re

from google import genai
from google.genai import types

from ..core.config import settings

logger = logging.getLogger("odin_api.llm")


def _get_client() -> genai.Client:
    """Get a configured Gemini client."""
    if not settings.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. "
            "Please set it to your Google Gemini API key."
        )
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def _extract_json_from_text(text: str) -> str | None:
    """Extract JSON array or object from LLM response text."""
    # Try to find JSON array first
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        return match.group(0)
    # Fallback to JSON object
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return None


async def summarize_content(text: str) -> str:
    """
    Summarize a piece of text using Gemini.

    Args:
        text: The text content to summarize.

    Returns:
        Summarized text string.
    """
    client = _get_client()

    prompt = (
        "You are a document summarizer. Shorten the following article while "
        "capturing all key points. Keep the original format. "
        "Output only the shortened article.\n\n"
        f"Article:\n{text}"
    )

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )
        result = response.text
        logger.debug(f"Summarization result length: {len(result)} chars")
        return result
    except Exception as e:
        logger.error(f"Error during summarization: {e}")
        raise


async def generate_slides(
    prompt: str,
    word_content: str = "",
    existing_slides: list[dict] | None = None,
) -> list[dict]:
    """
    Generate or update slide content using Gemini.

    Args:
        prompt: User's instruction for slide creation/editing.
        word_content: Optional document content to base slides on.
        existing_slides: Optional existing slides for editing.

    Returns:
        List of slide dictionaries with keys: slide_number, title, content, narration.
    """
    client = _get_client()

    if existing_slides is None:
        existing_slides = []

    # Reset narration to default for existing slides
    for slide in existing_slides:
        slide["narration"] = ""

    # Build the system instruction
    system_parts = []

    if word_content:
        system_parts.append(f"Input Article: {word_content}")

    slide_format_instruction = (
        'User will ask you to create or update text content for some slides'
        + (' based on the aforementioned Input Article' if word_content else '')
        + '. The response format should be a valid json format structured as this: '
        '[{"slide_number": <Float>, "title": "<String>", "content": "<String>", "narration": "<String>"},'
        '{"slide_number": <Float>, "title": "<String>", "content": "<String>", "narration": "<String>"}]\n'
        'The content field in the response should be comprehensive enough as it is the main text of each slide.\n'
        'For content use a mix of bullet points and text when applicable.\n'
        'If you are modifying an existing slide leave the slide number unchanged '
        'but if you are adding slides to the existing slides, use decimal digits for the slide number. '
        'For example to add a slide after slide 2, use slide number 2.1, 2.2, ...\n'
        'If user asks to remove a slide, set its slide number to negative of its current value '
        'because slides with negative slide number will be excluded from presentation.\n'
        f'The existing slides are as follows: {json.dumps(existing_slides)}'
    )
    system_parts.append(slide_format_instruction)

    system_parts.append(
        "For each slide the content field is the main body of the slide while "
        "the narration field is just an example transcript of the presentation "
        "of the content field. Never mention the slide number in the transcript."
    )
    system_parts.append(
        "For each slide, the content field should be the default field to modify "
        "if modification is demanded by the user for the slide, not the narration field."
    )
    system_parts.append(
        "For each slide, the narration field should only be populated if explicitly "
        "asked in user prompt, otherwise should be left empty."
    )
    system_parts.append(
        "Response should be valid json in the format described earlier. "
        "slide_number, title, and content are mandatory keys."
    )

    system_instruction = "\n\n".join(system_parts)

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=f"User request: {prompt}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.9,
                top_p=1.0,
            ),
        )
        response_text = response.text
        logger.debug(f"LLM raw response: {response_text[:500]}...")

        # Extract JSON from response
        json_str = _extract_json_from_text(response_text)
        if json_str is None:
            logger.error("Could not extract JSON from LLM response")
            raise ValueError("LLM response did not contain valid JSON slide data")

        parsed = json.loads(json_str)

        # Ensure it's a list
        if isinstance(parsed, dict):
            parsed = [parsed]

        # Process content fields (handle non-string content)
        for slide in parsed:
            if "content" in slide:
                slide["content"] = _process_content(slide["content"])
            if "narration" not in slide:
                slide["narration"] = ""

        return parsed

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        raise ValueError(f"Failed to parse LLM response as JSON: {e}")
    except Exception as e:
        logger.error(f"Error generating slides: {e}")
        raise


def _process_content(input_data) -> str:
    """Process content field which may be string, dict, or list."""
    if isinstance(input_data, str):
        return input_data
    elif isinstance(input_data, dict):
        return '\n'.join(f"{key}: {value}" for key, value in input_data.items())
    elif isinstance(input_data, list):
        output = []
        for item in input_data:
            if isinstance(item, str):
                output.append(item)
            elif isinstance(item, dict):
                output.extend(f"{key}: {value}" for key, value in item.items())
        return '\n'.join(output)
    return str(input_data)
