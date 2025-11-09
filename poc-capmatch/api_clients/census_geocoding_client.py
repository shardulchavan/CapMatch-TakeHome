import aiohttp
import asyncio
from typing import Dict, Optional, Any
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)

class CensusGeocodingClient:
    """
    Client for US Census Bureau Geocoding API
    Free service, no API key required
    """
    
    def __init__(self):
        self.base_url = "https://geocoding.geo.census.gov/geocoder"
        self.session = None
        
        # Benchmarks: https://www.census.gov/programs-surveys/geography/technical-documentation/complete-technical-documentation/census-geocoder.html
        self.benchmark = "Public_AR_Current"  # Current Address Ranges
        self.vintage = "Current_Current"  # Current vintage
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def geocode(self, address: str) -> Dict[str, float]:
        """
        Geocode an address using Census Bureau Geocoding API
        
        Args:
            address: Full address string (e.g., "555 California St, San Francisco, CA")
            
        Returns:
            Dictionary with 'lat' and 'lng' keys
            
        Raises:
            Exception if geocoding fails
        """
        await self._ensure_session()
        
        # Census geocoding endpoints
        # Using the one-line address endpoint
        url = f"{self.base_url}/locations/onelineaddress"
        
        params = {
            "address": address,
            "benchmark": self.benchmark,
            "vintage": self.vintage,
            "format": "json"
        }
        
        try:
            logger.info(f"Geocoding address: {address}")
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Census Geocoding API returned status {response.status}")
                
                data = await response.json()
                
                # Check if we got results
                if not data.get("result", {}).get("addressMatches"):
                    # Try alternative parsing
                    # Sometimes addresses need to be formatted differently
                    logger.warning(f"No matches found for address: {address}")
                    
                    # Try breaking down the address
                    return await self._geocode_structured(address)
                
                # Get the first match
                matches = data["result"]["addressMatches"]
                if matches:
                    first_match = matches[0]
                    coordinates = first_match.get("coordinates", {})
                    
                    if coordinates.get("x") and coordinates.get("y"):
                        result = {
                            "lat": float(coordinates["y"]),
                            "lng": float(coordinates["x"]),
                            "matched_address": first_match.get("matchedAddress", ""),
                            "match_type": first_match.get("tigerLine", {}).get("side", ""),
                            "source": "US Census Bureau Geocoder"
                        }
                        
                        logger.info(f"Successfully geocoded: {result}")
                        return result
                
                raise Exception(f"No valid coordinates found for address: {address}")
                
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            raise Exception(f"Failed to geocode address: {str(e)}")
    
    async def _geocode_structured(self, address: str) -> Dict[str, float]:
        """
        Try geocoding with structured address format
        This is a fallback method that attempts to parse the address
        """
        await self._ensure_session()
        
        # Attempt to parse address components
        # This is a simple parser - could be enhanced
        parts = [p.strip() for p in address.split(",")]
        
        if len(parts) < 2:
            raise Exception(f"Cannot parse address: {address}")
        
        # Try to identify components
        street = parts[0]
        city = parts[1] if len(parts) > 2 else ""
        state_zip = parts[2] if len(parts) > 2 else parts[1]
        
        # Extract state and zip if present
        state = ""
        zip_code = ""
        
        state_zip_parts = state_zip.split()
        for part in state_zip_parts:
            if part.replace("-", "").isdigit() and len(part.replace("-", "")) >= 5:
                zip_code = part
            elif len(part) == 2 and part.isalpha():
                state = part
        
        # Use the address components endpoint
        url = f"{self.base_url}/locations/address"
        
        params = {
            "street": street,
            "city": city,
            "state": state,
            "zip": zip_code,
            "benchmark": self.benchmark,
            "vintage": self.vintage,
            "format": "json"
        }
        
        # Remove empty parameters
        params = {k: v for k, v in params.items() if v}
        
        try:
            logger.info(f"Trying structured geocoding with params: {params}")
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Census Geocoding API returned status {response.status}")
                
                data = await response.json()
                
                if data.get("result", {}).get("addressMatches"):
                    matches = data["result"]["addressMatches"]
                    first_match = matches[0]
                    coordinates = first_match.get("coordinates", {})
                    
                    if coordinates.get("x") and coordinates.get("y"):
                        result = {
                            "lat": float(coordinates["y"]),
                            "lng": float(coordinates["x"]),
                            "matched_address": first_match.get("matchedAddress", ""),
                            "match_type": first_match.get("tigerLine", {}).get("side", ""),
                            "source": "US Census Bureau Geocoder (structured)"
                        }
                        
                        logger.info(f"Successfully geocoded with structured format: {result}")
                        return result
                
                raise Exception(f"No valid coordinates found for structured address")
                
        except Exception as e:
            logger.error(f"Structured geocoding error: {e}")
            raise Exception(f"Failed to geocode address with structured format: {str(e)}")
    
    async def reverse_geocode(self, lat: float, lng: float) -> Dict[str, Any]:
        """
        Reverse geocode coordinates to get address
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            Dictionary with address components
        """
        await self._ensure_session()
        
        url = f"{self.base_url}/geographies/coordinates"
        
        params = {
            "x": lng,
            "y": lat,
            "benchmark": self.benchmark,
            "vintage": self.vintage,
            "format": "json"
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Census Reverse Geocoding API returned status {response.status}")
                
                data = await response.json()
                
                result = {
                    "lat": lat,
                    "lng": lng,
                    "geographies": data.get("result", {}).get("geographies", {}),
                    "source": "US Census Bureau Reverse Geocoder"
                }
                
                # Extract some useful information
                if "States" in result["geographies"] and result["geographies"]["States"]:
                    result["state"] = result["geographies"]["States"][0].get("NAME", "")
                    result["state_fips"] = result["geographies"]["States"][0].get("STATE", "")
                
                if "Counties" in result["geographies"] and result["geographies"]["Counties"]:
                    result["county"] = result["geographies"]["Counties"][0].get("NAME", "")
                    result["county_fips"] = result["geographies"]["Counties"][0].get("COUNTY", "")
                
                if "Census Tracts" in result["geographies"] and result["geographies"]["Census Tracts"]:
                    result["tract"] = result["geographies"]["Census Tracts"][0].get("TRACT", "")
                
                return result
                
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            raise Exception(f"Failed to reverse geocode coordinates: {str(e)}")
    
    async def batch_geocode(self, addresses: list) -> list:
        """
        Geocode multiple addresses
        Note: Census Bureau also supports batch file upload for large batches
        
        Args:
            addresses: List of address strings
            
        Returns:
            List of geocoded results
        """
        tasks = [self.geocode(addr) for addr in addresses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        geocoded_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                geocoded_results.append({
                    "address": addresses[i],
                    "error": str(result),
                    "lat": None,
                    "lng": None
                })
            else:
                geocoded_results.append({
                    "address": addresses[i],
                    **result
                })
        
        return geocoded_results
    
    async def close(self):
        """Clean up session"""
        if self.session:
            await self.session.close()