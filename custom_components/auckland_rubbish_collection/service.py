import aiohttp
import asyncio
import datetime
from bs4 import BeautifulSoup
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, _LOGGER

SCAN_INTERVAL = timedelta(hours=5)
BASE_URL = "https://www.aucklandcouncil.govt.nz"

class AucklandRubbishCollectionCoordinator(DataUpdateCoordinator):
    """Fetch rubbish collection data periodically."""
    def __init__(self, hass, address_id, address_name="Address"):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.hass = hass
        self.address_id = address_id
        self.address_name = address_name

    def parse_collection_date(self, text: str) -> str | None:
        """Convert collection text (e.g., 'Thursday, 13 March') into ISO 8601 format ('YYYY-MM-DD')"""
        from dateutil import parser

        try:
            parsed = parser.parse(text, dayfirst=True)
            # Year rollover fix:
            # If today is December and the parsed month is January,
            # assume the date refers to next year.
            today = datetime.date.today()
            if today.month == 12 and parsed.month == 1:
                _LOGGER.debug(
                    "Year rollover detected for '%s': parsed month=January while today is in December. "
                    "Adjusting year from %s to %s.",
                    text,
                    parsed.year,
                    parsed.year + 1,
                )
                parsed = parsed.replace(year=today.year + 1)

            return parsed.date().isoformat()
        except Exception:
            return None

    def parse_collection_address(self, soup: BeautifulSoup) -> str:
        """
        Extracts the full address block from the HTML text.
        Returns a string like '100A My Street, Auckland, Auckland 1001'.
        """
        address_block = soup.find("h2")
        if not address_block:
            return "Unknown address"

        street = address_block.find("span", class_="heading")
        suburb = address_block.find("span", class_="subheading")

        if street and suburb:
            return f"{street.get_text(strip=True)}, {suburb.get_text(strip=True)}"
        elif street:
            return street.get_text(strip=True)
        elif suburb:
            return suburb.get_text(strip=True)
        else:
            return address_block.get_text(strip=True)

    async def _async_update_data(self):
        url = f"{BASE_URL}/en/rubbish-recycling/rubbish-recycling-collections/rubbish-recycling-collection-days/{self.address_id}.html"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
            ),
            "Accept-Language": "en-NZ,en;q=0.9",
            "Referer": f"{BASE_URL}/en/rubbish-recycling/"
                       "rubbish-recycling-collections/"
                       "rubbish-recycling-collection-days.html",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
        }
        session = async_get_clientsession(self.hass)
        try:
            _LOGGER.debug("Fetching collection data for entry: %s", self.address_name)
            async with session.get(url, headers=headers) as response:
                response_text = await response.text()
                _LOGGER.debug("Response: (status %s)\n%s",
                    response.status,
                    response_text[:200]
                )
            soup = BeautifulSoup(response_text, "html.parser")

            # Extract geolocation address
            geolocation_address = self.parse_collection_address(soup)

            # Initialize collection dates
            rubbish, recycling, food_scraps = None, None, None

            # Extract collection information
            collection_cards = soup.find_all("div", class_="acpl-schedule-card")
            collection_info = []
            for card in collection_cards:
                bin_entries = card.find_all("p", class_="mb-0 lead")
                for entry in bin_entries:
                    collection_info.append(entry)

            if not collection_info:
                _LOGGER.error("Unexpected response format: no collection data found")

            # Parse each collection entry and assign to the correct type based on keywords
            for entry in collection_info:
                text = entry.get_text(strip=True)
                if "rubbish" in text.lower():
                    raw_date = text.split(":", 1)[-1].strip() if ":" in text else text
                    rubbish = self.parse_collection_date(raw_date)
                elif "recycling" in text.lower():
                    raw_date = text.split(":", 1)[-1].strip() if ":" in text else text
                    recycling = self.parse_collection_date(raw_date)
                elif "food scraps" in text.lower():
                    raw_date = text.split(":", 1)[-1].strip() if ":" in text else text
                    food_scraps = self.parse_collection_date(raw_date)

            # Determine next collection type
            try:
                if rubbish and recycling:
                    if rubbish == recycling:
                        next_collection_type = "Rubbish & Recycling"
                    else:
                        next_collection_type = "Rubbish"
                elif rubbish:
                        next_collection_type = "Rubbish"
                else:
                    next_collection_type = None
            except Exception:
                next_collection_type = None

            return {
                "rubbish": rubbish,
                "recycling": recycling,
                "food_scraps": food_scraps,
                "geolocation_address": geolocation_address,
                "next_collection_type": next_collection_type
            }
        except Exception as e:
            _LOGGER.error("Error fetching rubbish collection data: %s", e)
            return {}

def get_coordinator(hass, entry):
    """Get or create a coordinator for the given entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    if entry.entry_id in hass.data[DOMAIN]:
        return hass.data[DOMAIN][entry.entry_id]

    # Get address_id from options if available, otherwise from data
    address_id = entry.options.get("address_id", entry.data.get("address_id"))
    address_name = entry.data.get("address_name", address_id)

    coordinator = AucklandRubbishCollectionCoordinator(hass, address_id, address_name)
    hass.data[DOMAIN][entry.entry_id] = coordinator

    return coordinator
