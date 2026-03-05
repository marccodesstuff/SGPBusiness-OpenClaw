"""
scrape-sgpbusiness skill
Scrapes the SGPBusiness directory (sgbizfile.gov.sg) for UEN and
legal entity details using Scrapling for adaptive stealth scraping.
"""
import json
from typing import Any, Dict
from urllib.parse import quote_plus


SGP_BASE_URL = "https://www.sgbizfile.gov.sg"


def execute(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search SGPBusiness for an entity name and scrape the resulting page
    for UEN, business type, registration date, and address.

    Args:
        inputs: dict with key 'entity_name' (required).

    Returns:
        dict with entity details scraped from SGPBusiness.
    """
    entity_name = inputs.get("entity_name", "")
    if not entity_name:
        return {
            "status": "error",
            "message": "No entity_name provided",
        }

    search_url = f"{SGP_BASE_URL}/search?q={quote_plus(entity_name)}"

    try:
        from scrapling import Fetcher

        fetcher = Fetcher(auto_match=True)
        page = fetcher.get(search_url, timeout=30)

        # Try to locate the first search-result link
        result_link = page.css_first("a.entity-link, table.search-results a, .result a")
        if result_link:
            detail_url = result_link.attrib.get("href", "")
            if detail_url and not detail_url.startswith("http"):
                detail_url = f"{SGP_BASE_URL}{detail_url}"
            detail_page = fetcher.get(detail_url, timeout=30)
            return _parse_entity_page(detail_page, detail_url)

        # Fallback: try to parse the search page itself (single-result pages)
        return _parse_entity_page(page, search_url)

    except ImportError:
        # scrapling not installed — fall back to requests + basic parsing
        return _fallback_scrape(search_url, entity_name)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Scraping failed: {str(e)}",
        }


def _parse_entity_page(page, source_url: str) -> Dict[str, Any]:
    """Extract structured fields from a detail page."""
    def _text(selector: str) -> str:
        el = page.css_first(selector)
        return el.text(strip=True) if el else ""

    entity_name = _text("h1, .entity-name, .company-name, td.entity-name")
    uen = _text(".uen, td.uen, [data-field='uen']")
    business_type = _text(".business-type, td.business-type, [data-field='business_type']")
    registration_date = _text(".registration-date, td.registration-date, [data-field='registration_date']")
    business_address = _text(".address, td.address, [data-field='address']")

    return {
        "entity_name": entity_name or "Not found",
        "uen": uen or "Not found",
        "business_type": business_type or "Not found",
        "registration_date": registration_date or "Not found",
        "business_address": business_address or "Not found",
        "website_url": "",
        "sgbusiness_url": source_url,
    }


def _fallback_scrape(search_url: str, entity_name: str) -> Dict[str, Any]:
    """Minimal fallback when scrapling is not installed."""
    try:
        import requests

        resp = requests.get(search_url, timeout=30)
        resp.raise_for_status()
        # Return a stub with everything we can confirm
        return {
            "entity_name": entity_name,
            "uen": "Not found",
            "business_type": "Not found",
            "registration_date": "Not found",
            "business_address": "Not found",
            "website_url": "",
            "sgbusiness_url": search_url,
            "message": "scrapling not installed; install with: pip install scrapling[fetchers]",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Fallback scrape failed: {str(e)}",
        }
