import aiohttp
import asyncio
import datetime
from bs4 import BeautifulSoup
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, _LOGGER

SCAN_INTERVAL = timedelta(hours=3)
BASE_URL = "https://www.aucklandcouncil.govt.nz"

class AucklandRubbishCollectionCoordinator(DataUpdateCoordinator):
    """Fetch rubbish collection data periodically."""
    def __init__(self, hass, address_id, address_name="Address"):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.hass = hass
        self.address_id = address_id
        self.address_name = address_name

    def parse_collection_date(self, text):
        """Convert collection text (e.g., 'Thursday 13 March') into a standardized format."""
        try:
            parts = text.split(" ")
            # Expecting format like "Thursday 13 March"
            day_name, day, month = parts[0], parts[1], parts[2]
            year = datetime.datetime.now().year  # Assume current year
            parsed_date = datetime.datetime.strptime(f"{day} {month} {year}", "%d %B %Y")
            return parsed_date.strftime("%A %d %B")  # Ensure consistent format
        except (ValueError, IndexError):
            return None  # Return None if parsing fails

    async def _async_update_data(self):
        url = f"{BASE_URL}/rubbish-recycling/rubbish-recycling-collections/Pages/collection-day-detail.aspx?an={self.address_id}"
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(url) as response:
                response_text = await response.text()
            soup = BeautifulSoup(response_text, "html.parser")
            collection_info = soup.find_all(attrs={"class": "collectionDayDate"})
            if not collection_info:
                _LOGGER.error("Unexpected response format: no collection data found")
                return {}

            # Extract geolocation address
            address_blocks = soup.find_all(attrs={"class": "m-b-2"})
            geolocation_address = address_blocks[0].string.strip() if address_blocks and address_blocks[0].string else None

            # Initialize collection dates
            rubbish, recycling, food_scraps = None, None, None

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

            # Determine next collection type based on dates
            today = datetime.datetime.now().strftime("%A %d %B")
            if rubbish and recycling:
                if rubbish == recycling:
                    next_collection_type = "Rubbish & Recycling"
                elif rubbish == today:
                    next_collection_type = "Rubbish"
                elif recycling == today:
                    next_collection_type = "Recycling"
                else:
                    # Determine which collection is coming next
                    next_collection_type = "Unknown"
                    try:
                        today_dt = datetime.datetime.strptime(today, "%A %d %B")
                        rubbish_dt = datetime.datetime.strptime(rubbish, "%A %d %B")
                        recycling_dt = datetime.datetime.strptime(recycling, "%A %d %B")
                        
                        # Adjust for dates in next year
                        if rubbish_dt < today_dt:
                            rubbish_dt = rubbish_dt.replace(year=rubbish_dt.year + 1)
                        if recycling_dt < today_dt:
                            recycling_dt = recycling_dt.replace(year=recycling_dt.year + 1)
                            
                        if rubbish_dt < recycling_dt:
                            next_collection_type = "Rubbish"
                        else:
                            next_collection_type = "Recycling"
                    except ValueError:
                        next_collection_type = "Rubbish"  # Default if dates couldn't be parsed
            else:
                next_collection_type = "Unknown"

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
