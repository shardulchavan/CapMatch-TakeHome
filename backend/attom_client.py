# backend/attom_client.py

import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
import os
import logging
import json 

logger = logging.getLogger(__name__)

class AttomClient:
    """
    Client for ATTOM Data APIs
    Uses Location Lookup API to find geoIdV4, then Community API for demographics
    """
    
    def __init__(self):
        self.api_key = os.getenv("ATTOM_API_KEY", "")
        print("Attom API Key Loaded:", bool(self.api_key))
        if not self.api_key:
            logger.warning("ATTOM_API_KEY not found in environment variables")
        
        self.base_url = "https://api.gateway.attomdata.com"
        self.session = None
        
        # Create auth header
        self.headers = {
            "accept": "application/json",
            "apikey": self.api_key
        }
    
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

    async def get_pois_by_address(self, address: str, radius: int = 10) -> Dict[str, Any]:
        """
        Get Points of Interest for an address using ATTOM's POI API
        
        Args:
            address: Full address string (e.g., "10 Wall St., New York, NY 10005")
            radius: Search radius in miles (default: 5)
            
        Returns:
            Dictionary with POI data grouped by category
        """
        if not self.api_key:
            return {"error": "ATTOM API key not configured"}
        
        await self._ensure_session()
        
        # Static business categories to search
        categories = [
            "PERSONAL SERVICES",
            "HEALTH CARE SERVICES",
            "EDUCATION",
            "BANKS – FINANCIAL"
        ]
        category_string = "|".join(categories)
        
        result = {
            "address": address,
            "radius": radius,
            "categories_searched": categories,
            "data_source": "ATTOM POI API",
            "poi_count": 0,
            "pois_by_category": {
                "PERSONAL SERVICES": [],
                "HEALTH CARE SERVICES": [],
                "EDUCATION": [],
                "BANKS – FINANCIAL": [],
            },
            "raw_response": None,
            "errors": []
        }
        
        try:
            # ATTOM POI endpoint
            url = f"{self.base_url}/v4/neighborhood/poi"
            
            params = {
                "address": address,
                "categoryName": category_string,
                "radius": str(radius)
            }
            
            logger.info(f"Calling ATTOM POI API with params: {params}")
            
            async with self.session.get(url, headers=self.headers, params=params) as response:
                response_text = await response.text()
                logger.info(f"ATTOM POI response status: {response.status}")
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        result["raw_response"] = data
                        
                        # FIXED: POI data is directly in data["poi"], not nested
                        if "poi" in data and isinstance(data["poi"], list):
                            all_pois = data["poi"]
                            
                            # Process each POI
                            for poi in all_pois:
                                # Extract business info
                                business_loc = poi.get("businessLocation", {})
                                category_info = poi.get("category", {})
                                details = poi.get("details", {})
                                
                                # Get category name
                                category = category_info.get("category", "").upper()
                                
                                # Create formatted POI entry
                                poi_entry = {
                                    "name": business_loc.get("businessStandardName", "Unknown"),
                                    "address": business_loc.get("address", ""),
                                    "suite": business_loc.get("suite", ""),
                                    "city": business_loc.get("city", ""),
                                    "state": details.get("state", ""),
                                    "zip": details.get("zip", ""),
                                    "distance_miles": float(details.get("distance", 0)),
                                    "category": category,
                                    "line_of_business": category_info.get("lineOfBusiness", ""),
                                    "industry": category_info.get("industry", ""),
                                    "phone": f"({details.get('areaCode', '')}) {details.get('exchange', '')}-{details.get('phoneNumber', '')}",
                                    "confidence_score": details.get("confidenceScore", ""),
                                    "latitude": details.get("latitude", ""),
                                    "longitude": details.get("longitude", "")
                                }
                                
                                # Clean up phone number
                                if poi_entry["phone"] == "() -":
                                    poi_entry["phone"] = "N/A"
                                
                                # Add full address
                                full_address_parts = [poi_entry["address"]]
                                if poi_entry["suite"]:
                                    full_address_parts.append(poi_entry["suite"])
                                full_address_parts.append(f"{poi_entry['city']}, {poi_entry['state']} {poi_entry['zip']}")
                                poi_entry["full_address"] = " ".join(full_address_parts)
                                
                                # Add to appropriate category if it's one we're tracking
                                if category in result["pois_by_category"]:
                                    result["pois_by_category"][category].append(poi_entry)
                            
                            # Sort each category by distance
                            for category in result["pois_by_category"]:
                                result["pois_by_category"][category].sort(
                                    key=lambda x: x["distance_miles"]
                                )
                            
                            # Calculate total POI count
                            result["poi_count"] = sum(
                                len(pois) for pois in result["pois_by_category"].values()
                            )
                            
                            # Add summary statistics
                            result["summary"] = {
                                "personal_services_count": len(result["pois_by_category"]["PERSONAL SERVICES"]),
                                "healthcare_count": len(result["pois_by_category"]["HEALTH CARE SERVICES"]),
                                "education_count": len(result["pois_by_category"]["EDUCATION"]),
                                "banks_count": len(result["pois_by_category"]["BANKS – FINANCIAL"]),
                                "closest_poi": self._find_closest_poi(result["pois_by_category"])
                            }
                            
                            # Add status from response
                            if "status" in data:
                                result["api_status"] = data["status"]
                        else:
                            result["errors"].append("No POI data found in response")
                    
                    except json.JSONDecodeError as e:
                        result["errors"].append(f"Failed to parse JSON response: {str(e)}")
                        logger.error(f"JSON decode error: {response_text[:500]}")
                
                elif response.status == 404:
                    result["errors"].append(f"No POIs found for address: {address}")
                elif response.status == 401:
                    result["errors"].append("Invalid ATTOM API key")
                else:
                    result["errors"].append(f"API returned status {response.status}: {response_text[:200]}")
                    
        except Exception as e:
            result["errors"].append(f"Error fetching POI data: {str(e)}")
            logger.error(f"ATTOM POI API error: {e}", exc_info=True)
        
        return result
    
    def _find_closest_poi(self, pois_by_category: Dict[str, List[Dict]]) -> Optional[Dict[str, Any]]:
        """Find the closest POI across all categories"""
        closest = None
        min_distance = float('inf')
        
        for category, pois in pois_by_category.items():
            if pois:
                if pois[0]["distance_miles"] < min_distance:
                    min_distance = pois[0]["distance_miles"]
                    closest = {
                        "name": pois[0]["name"],
                        "category": category,
                        "distance_miles": min_distance,
                        "address": pois[0]["full_address"]
                    }
        
        return closest
    
    async def get_community_by_address(self, address: str) -> Dict[str, Any]:
        """
        Get community demographic data for an address using ATTOM's Community API v4
        
        Args:
            address: Full address string (e.g., "10 Wall St., New York, NY 10005")
            
        Returns:
            Dictionary with community demographic data
        """
        if not self.api_key:
            return {"error": "ATTOM API key not configured"}
        
        await self._ensure_session()
        
        # CHANGE #1: Removed "community_data": {} from initial result
        result = {
            "address": address,
            "data_source": "ATTOM Community API v4",
            "selected_geography": {},
            "errors": []
        }
        
        try:
            # Extract location name and type from address
            location_name, geography_type = self._extract_location_from_address(address)
            logger.info(f"Extracted location: '{location_name}' with type: '{geography_type}'")
            
            # CHANGE #2: Removed extraction_info from result (optional cleanup)
            
            # Step 1: Location Lookup to get geoIdV4
            locations = await self._lookup_location(location_name, geography_type)
            
            if not locations:
                result["errors"].append(f"No locations found for: {location_name} (type: {geography_type})")
                return result
            
            # CHANGE #3: Removed location_matches from result
            
            # Select best location (first match for now)
            selected_location = locations[0] if locations else None
            
            if not selected_location:
                result["errors"].append("Could not find suitable location from matches")
                return result
            
            result["selected_geography"] = selected_location
            
            # Step 2: Get community data using geoIdV4
            geo_id_v4 = selected_location.get("geoIdV4")
            if geo_id_v4:
                community_data = await self._get_community_data(geo_id_v4)
                
                if community_data:
                    # CHANGE #4: Only storing formatted data, not raw community_data
                    result["formatted_data"] = self._format_community_response(community_data, selected_location)
                else:
                    result["errors"].append("No community data returned")
            else:
                result["errors"].append("No geoIdV4 found in selected location")
                
        except Exception as e:
            result["errors"].append(f"Error fetching community data: {str(e)}")
            logger.error(f"Community API error: {e}", exc_info=True)
        
        return result
    
    def _extract_location_from_address(self, address: str) -> tuple[str, str]:
        """
        Extract ZIP code or City name from address for location lookup
        
        Returns:
            Tuple of (location_name, geography_type)
            - For ZIP: ("10005", "ZI")
            - For City: ("Boston", "PL")
        """
        import re
        
        # First, try to find a 5-digit ZIP code
        zip_pattern = r'\b(\d{5})\b'
        zip_match = re.search(zip_pattern, address)
        
        if zip_match:
            zip_code = zip_match.group(1)
            logger.info(f"Found ZIP code: {zip_code}")
            return (zip_code, "ZI")
        
        # If no ZIP, extract city name (text before state abbreviation)
        # Common state abbreviations
        state_abbrevs = [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
        ]
        
        # Split by comma and process parts
        parts = [p.strip() for p in address.split(',')]
        
        # Look through parts for city (usually second part)
        for i, part in enumerate(parts):
            # Check if this part contains a state abbreviation
            words = part.split()
            for state in state_abbrevs:
                if state in words:
                    # Found state, so previous part or current part before state is city
                    if i > 0 and not any(char.isdigit() for char in parts[i-1]):
                        # Previous part is likely city
                        city = parts[i-1].strip()
                        logger.info(f"Found city from previous part: {city}")
                        return (city, "PL")
                    else:
                        # Current part has city before state
                        city_words = []
                        for word in words:
                            if word == state:
                                break
                            city_words.append(word)
                        if city_words:
                            city = ' '.join(city_words).strip()
                            logger.info(f"Found city before state: {city}")
                            return (city, "PL")
        
        # Fallback: if address has commas, try second part as city
        if len(parts) >= 2:
            potential_city = parts[1].strip()
            # Remove any numbers or state abbreviations
            city_words = []
            for word in potential_city.split():
                if not word.isdigit() and word not in state_abbrevs and len(word) > 2:
                    city_words.append(word)
            if city_words:
                city = ' '.join(city_words).strip()
                logger.info(f"Found city from second part: {city}")
                return (city, "PL")
        
        # Last resort: return full address for manual lookup
        logger.warning(f"Could not extract city or ZIP from: {address}")
        return (address, "PL")
    
    async def _lookup_location(self, location_name: str, geography_type: str = "PL") -> List[Dict[str, Any]]:
        """
        Use Location Lookup API v4 to find geographic identifiers
        
        Args:
            location_name: Location to search (ZIP, city name, etc.)
            geography_type: Type of geography (ZI, PL, etc.)
            
        Returns:
            List of matching locations with geoIdV4
        """
        try:
            url = f"{self.base_url}/v4/location/lookup"
            
            params = {
                "name": location_name,
                "geographyTypeAbbreviation": geography_type
            }
            
            logger.info(f"Location lookup with params: {params}")
            
            async with self.session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # FIXED: Look for geographies directly in response
                    if "geographies" in data and isinstance(data["geographies"], list):
                        return data["geographies"]
                    else:
                        logger.warning(f"No geographies found in response for {location_name}")
                        return []
                
                else:
                    logger.error(f"Location Lookup failed: {response.status}")
                    if response.status == 401:
                        return [{"error": "Invalid ATTOM API key"}]
                    
        except Exception as e:
            logger.error(f"Error in location lookup: {e}")
        
        return []
    
    def _select_best_location(self, locations: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Select the best location from matches
        For now, just returns the first match since we're being specific with geography types
        """
        if not locations:
            return None
            
        # If there's an error in the first location, return None
        if "error" in locations[0]:
            return None
            
        # Return first valid location with geoIdV4
        for loc in locations:
            if loc.get("geoIdV4"):
                return loc
                
        return None
    
    async def _get_community_data(self, geo_id_v4: str) -> Optional[Dict[str, Any]]:
        """
        Get community data using Community API v4
        
        Args:
            geo_id_v4: The geoIdV4 identifier
            
        Returns:
            Community data dictionary or None
        """
        try:
            url = f"{self.base_url}/v4/neighborhood/community"
            
            params = {
                "geoIdV4": geo_id_v4
            }
            
            logger.info(f"Getting community data for geoIdV4: {geo_id_v4}")
            
            async with self.session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "community" in data:
                        return data["community"]
                    else:
                        logger.warning("No community data found in response")
                        return None
                
                else:
                    logger.error(f"Community API failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error getting community data: {e}")
        
        return None
    
    def _format_community_response(self, community_data: Dict[str, Any], location_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format community API response to extract key demographic data
        
        Args:
            community_data: Raw community API response
            location_info: Location information including geography type
            
        Returns:
            Formatted data dictionary
        """
        # Get geography info from community data if available
        geo_info = community_data.get("geography", {})
        
        formatted = {
            "geography": {
                "type": location_info.get("geographyTypeName", self._get_geo_type_name(location_info.get("geographyTypeAbbreviation", ""))),
                "name": geo_info.get("geographyName", location_info.get("geographyName", "")),
                "geo_id_v4": geo_info.get("geoIdV4", location_info.get("geoIdV4", "")),
                "area_sq_miles": geo_info.get("area_Square_Mile", 0),
                "coordinates": {
                    "latitude": geo_info.get("latitude", 0),
                    "longitude": geo_info.get("longitude", 0)
                }
            },
            "demographics": {},
            # "income": {},
            # "education": {},
            "housing": {},
            "employment": {},
            "climate": {},
            "crime": {},
            "air_quality": {},
            "cost_index": {},
            "summary_stats": {}
        }
        
        # Extract demographics data (already at top level in community_data)
        demo = community_data.get("demographics", {})
        
        if demo:
            # # Population data
            # formatted["demographics"]["population"] = {
            #     "total": demo.get("population", 0),
            #     "density_per_sq_mi": demo.get("population_Density_Sq_Mi", 0),
            #     "median_age": demo.get("median_Age", 0),
            #     "households": demo.get("households", 0),
            #     "growth_5yr_pct": demo.get("population_Chg_Pct_5_Yr_Projection", 0),
            #     "daytime_population": demo.get("population_Daytime", 0)
            # }
            
            # # Income data
            # formatted["income"] = {
            #     "median_household": demo.get("median_Household_Income", 0),
            #     "avg_household": demo.get("avg_Household_Income", 0),
            #     "per_capita": demo.get("household_Income_Per_Capita", 0),
            #     "median_family": demo.get("family_Median_Income", 0),
            #     "high_income_pct": demo.get("households_Income_200000_And_Over_Pct", 0)
            # }
            
            # # Education
            # formatted["education"] = {
            #     "high_school_grad_pct": demo.get("education_Hs_Pct", 0),
            #     "bachelors_degree_pct": demo.get("education_Bach_Degree_Pct", 0),
            #     "masters_degree_pct": demo.get("education_Mast_Degree_Pct", 0),
            #     "graduate_degree_pct": demo.get("education_Grad_Degree_Pct", 0),
            #     "some_college_pct": demo.get("education_Some_College_Pct", 0)
            # }
            
            # Employment
            formatted["employment"] = {
                # "employed_population": demo.get("population_Employed_16P", 0),
                "white_collar_pct": demo.get("occupation_White_Collar_Pct", 0),
                "blue_collar_pct": demo.get("occupation_Blue_Collar_Pct", 0),
                "median_commute_time": demo.get("median_Travel_Time_To_Work_Mi", 0),
                "work_from_home_pct": demo.get("transportation_Work_From_Home_Pct", 0)
            }

            formatted["transportation"] = {
                "drive_alone_pct": demo.get("transportation_Car_Alone_Pct", 0),
                "carpool_pct": demo.get("transportation_Car_Carpool_Pct", 0),
                "public_transit_pct": demo.get("transportation_Public_Pct", 0),
                "walk_pct": demo.get("transportation_Walk_Pct", 0),
                "bicycle_pct": demo.get("transportation_Bicycle_Pct", 0),
                "work_from_home_pct": demo.get("transportation_Work_From_Home_Pct", 0),
                "other_pct": demo.get("transportation_Other_Pct", 0)
            }
            
            # Housing
            formatted["housing"] = {
                "total_units": demo.get("housing_Units", 0),
                "occupied_pct": demo.get("housing_Units_Occupied_Pct", 0),
                "owner_occupied_pct": demo.get("housing_Units_Owner_Occupied_Pct", 0),
                "renter_occupied_pct": demo.get("housing_Units_Renter_Occupied_Pct", 0),
                # "median_home_value": demo.get("housing_Owner_Households_Median_Value", 0),
                "median_rent": demo.get("housing_Median_Rent", 0),
                "median_year_built": demo.get("housing_Median_Built_Yr", 0)
            }
           
            # Demographics breakdown
            formatted["demographics"]["breakdown"] = {
                "male_pct": demo.get("population_Male_Pct", 0),
                "female_pct": demo.get("population_Female_Pct", 0),
                "white_pct": demo.get("population_White_Pct", 0),
                "black_pct": demo.get("population_Black_Pct", 0),
                "asian_pct": demo.get("population_Asian_Pct", 0),
                "hispanic_pct": demo.get("population_Hispanic_Pct", 0)
            }
            
            # Age distribution
            formatted["demographics"]["age_distribution"] = {
                "under_18_pct": sum([
                    demo.get("population_Aged_0_5_Pct", 0),
                    demo.get("population_Aged_6_11_Pct", 0),
                    demo.get("population_Aged_12_17_Pct", 0)
                ]),
                "18_34_pct": sum([
                    demo.get("population_Aged_18_24_Pct", 0),
                    demo.get("population_Aged_25_34_Pct", 0)
                ]),
                "35_64_pct": sum([
                    demo.get("population_Aged_35_44_Pct", 0),
                    demo.get("population_Aged_45_54_Pct", 0),
                    demo.get("population_Aged_55_64_Pct", 0)
                ]),
                "65_plus_pct": sum([
                    demo.get("population_Aged_65_74_Pct", 0),
                    demo.get("population_Aged_75_84_Pct", 0),
                    demo.get("population_Aged_85P_Pct", 0)
                ])
            }
        
        # Extract climate data
        climate = community_data.get("climate", {})
        if climate:
            formatted["climate"] = {
                "avg_temp": climate.get("annual_Avg_Temp", 0),
                "avg_temp_january": climate.get("avg_Jan_Low_Temp", 0),
                "avg_temp_july": climate.get("avg_Jul_High_Temp", 0),
                "annual_rainfall_inches": climate.get("annual_Precip_In", 0),
                "annual_snowfall_inches": climate.get("annual_Snowfall_In", 0),
                "clear_days": climate.get("clear_Day_Mean", 0),
                "rainy_days": climate.get("rainy_Day_Mean", 0)
            }
        
        # Extract crime data
        crime = community_data.get("crime", {})
        if crime:
            formatted["crime"] = {
                "crime_index": crime.get("crime_Index", 0),
                "murder_index": crime.get("murder_Index", 0),
                "robbery_index": crime.get("forcible_Robbery_Index", 0),
                "assault_index": crime.get("aggravated_Assault_Index", 0),
                "burglary_index": crime.get("burglary_Index", 0),
                "theft_index": crime.get("motor_Vehicle_Theft_Index", 0)
            }
        
        # Extract air quality
        air_quality = community_data.get("airQuality", {})
        if air_quality:
            formatted["air_quality"] = {
                "air_pollution_index": air_quality.get("air_Pollution_Index", 0),
                "ozone_index": air_quality.get("ozone_Index", 0),
                "particulate_index": air_quality.get("particulate_Matter_Index", 0),
                "carbon_monoxide_index": air_quality.get("carbon_Monoxide_Index", 0)
            }
        
        # Extract some cost indices
        if demo:
            formatted["cost_index"] = {
                "annual_expenditures": demo.get("costIndex_Annual_Expenditures", 0),
                "housing": demo.get("costIndex_Housing", 0),
                "food": demo.get("costIndex_Food", 0),
                "transportation": demo.get("costIndex_Transportation", 0),
                "healthcare": demo.get("costIndex_Healthcare", 0)
            }
        
        # Generate summary statistics
        formatted["summary_stats"] = self._generate_summary_stats(formatted)
        
        return formatted
    
    def _generate_summary_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary insights from community data"""
        summary = {
            "key_metrics": [],
            "strengths": [],
            "considerations": []
        }
        
        # Check income levels
        # median_income = data["income"].get("median_household", 0)
        # if median_income > 0:
        #     summary["key_metrics"].append(f"Median Income: ${median_income:,}")
        #     if median_income > 75000:
        #         summary["strengths"].append("High median household income")
        
        # # Check education
        # bachelors_pct = data["education"].get("bachelors_degree_pct", 0)
        # if bachelors_pct > 0:
        #     summary["key_metrics"].append(f"College Graduates: {bachelors_pct:.1f}%")
        #     if bachelors_pct > 35:
        #         summary["strengths"].append("Highly educated population")
        
        # Check crime
        crime_index = data["crime"].get("crime_index", 0)
        if crime_index > 0:
            if crime_index < 100:
                summary["strengths"].append("Lower than average crime rates")
            elif crime_index > 150:
                summary["considerations"].append("Higher crime rates than national average")
        
        # # Check housing
        # home_value = data["housing"].get("median_home_value", 0)
        # if home_value > 0:
        #     summary["key_metrics"].append(f"Median Home Value: ${home_value:,}")
        
        return summary
    
    def _get_geo_type_name(self, geo_type: str) -> str:
        """Convert geography type abbreviation to readable name"""
        mapping = {
            "ZI": "ZIP Code",
            "CO": "County",
            "CS": "County Subdivision",
            "PL": "Place",
            "CI": "City",
            "ST": "State",
            "N1": "Macro Neighborhood",
            "N2": "Neighborhood", 
            "N3": "Sub-Neighborhood",
            "N4": "Residential Subdivision",
            "DB": "DataBlock",
            "RS": "Reserved"
        }
        return mapping.get(geo_type, geo_type)
    
    async def close(self):
        """Clean up session"""
        if self.session:
            await self.session.close()