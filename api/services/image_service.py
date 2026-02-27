"""
Image Service — Logic for searching and downloading images via Pixabay API.
Developed by ChimSe (viduvan) - https://github.com/viduvan

Falls back gracefully: returns None if no API key or fetch fails.
"""
import asyncio
import logging
import hashlib
from pathlib import Path

import aiohttp

from ..core.config import settings

logger = logging.getLogger("odin_api.services.image_service")

PIXABAY_API_URL = "https://pixabay.com/api/"


async def _search_and_download(session: aiohttp.ClientSession, keyword: str,
                                api_key: str) -> Path | None:
    """Search Pixabay and download one image for the given keyword."""
    cache_name = hashlib.md5(keyword.encode()).hexdigest() + ".jpg"
    cache_path = settings.IMAGES_DIR / cache_name
    if cache_path.exists():
        logger.debug(f"Cache hit for '{keyword}'")
        return cache_path

    params = {
        "key": api_key,
        "q": keyword,
        "image_type": "photo",
        "orientation": "horizontal",
        "min_width": 640,
        "per_page": 5,
        "safesearch": "true",
    }

    try:
        async with session.get(PIXABAY_API_URL, params=params,
                               timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                logger.warning(f"Pixabay API {resp.status} for '{keyword}'")
                return None
            data = await resp.json()

        hits = data.get("hits", [])
        if not hits:
            logger.info(f"No images for '{keyword}'")
            return None

        image_url = hits[0].get("webformatURL", "")
        if not image_url:
            return None

        async with session.get(image_url,
                               timeout=aiohttp.ClientTimeout(total=15)) as img_resp:
            if img_resp.status != 200:
                logger.warning(f"Image download failed: {img_resp.status}")
                return None

            settings.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
            image_data = await img_resp.read()
            cache_path.write_bytes(image_data)
            logger.info(f"Downloaded '{keyword}' -> {cache_path.name} ({len(image_data)} bytes)")
            return cache_path

    except Exception as e:
        logger.warning(f"Error fetching '{keyword}': {e}")
        return None


def _extract_fallback_keyword(slide_data: dict) -> str:
    """Extract a simple fallback keyword from the slide title."""
    title = slide_data.get("title", "")
    # Take the first 1-2 meaningful words from title
    stop_words = {"the", "a", "an", "of", "and", "in", "for", "to", "on", "is",
                  "are", "was", "with", "by", "at", "from", "as", "các", "và",
                  "cho", "về", "của", "trên", "trong", "để", "là", "có", "được",
                  "một", "những", "này", "với", "không", "theo", "từ", "đến"}
    words = [w for w in title.split() if w.lower() not in stop_words and len(w) > 2]
    return " ".join(words[:2]) if words else "presentation"


async def fetch_images_for_slides(slides: list[dict]) -> dict:
    """
    Fetch images for all slides. Uses a single session to avoid connection issues.
    Falls back to title-derived keywords if image_keyword fails.
    """
    api_key = settings.PIXABAY_API_KEY
    if not api_key:
        logger.debug("No PIXABAY_API_KEY, skipping all image fetches")
        return {}

    image_paths = {}

    async with aiohttp.ClientSession() as session:
        for slide_data in slides:
            slide_num = slide_data.get("slide_number")
            keyword = slide_data.get("image_keyword", "").strip()

            if keyword:
                img_path = await _search_and_download(session, keyword, api_key)
                if img_path:
                    image_paths[slide_num] = str(img_path)
                    await asyncio.sleep(0.3)  # Rate limit buffer
                    continue

            # Fallback: use words from title
            fallback = _extract_fallback_keyword(slide_data)
            if fallback and fallback != keyword:
                logger.info(f"Trying fallback keyword '{fallback}' for slide {slide_num}")
                img_path = await _search_and_download(session, fallback, api_key)
                if img_path:
                    image_paths[slide_num] = str(img_path)

            await asyncio.sleep(0.3)  # Rate limit buffer

    logger.info(f"Fetched {len(image_paths)} images for {len(slides)} slides")
    return image_paths
