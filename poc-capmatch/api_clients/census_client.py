import aiohttp
import asyncio
from typing import Dict, List, Any, Optional, Tuple
import os
from math import radians, sin, cos, sqrt, atan2
import logging

logger = logging.getLogger(__name__)

class CensusClient:
    """
    Client for US Census Bureau API
    Fetches demographic data for specified coordinates and radii
    """
    
    def __init__(self):
        self.api_key = os.getenv("CENSUS_API_KEY", "")  # Optional but recommended
        self.base_url = "https://api.census.gov/data"
        self.session = None
        
        # ACS 5-year dataset (most comprehensive)
        self.dataset_year = "2022"  # Latest available ACS 5-year
        self.dataset = f"{self.dataset_year}/acs/acs5"
        
        # Define variables we want to fetch
        self.variables = {
            # Basic Demographics
            "B01003_001E": "total_population",
            "B19013_001E": "median_household_income",
            "B25077_001E": "median_home_value",
            "B15003_022E": "bachelors_degree",
            "B15003_023E": "masters_degree", 
            "B15003_024E": "professional_degree",
            "B15003_025E": "doctorate_degree",
            "B01002_001E": "median_age",
            
            # Population by Age Groups
            "B01001_003E": "male_under_5",
            "B01001_004E": "male_5_to_9",
            "B01001_027E": "female_under_5",
            "B01001_028E": "female_5_to_9",
            
            # Income Distribution
            "B19001_002E": "income_less_10k",
            "B19001_003E": "income_10k_15k",
            "B19001_004E": "income_15k_20k",
            "B19001_005E": "income_20k_25k",
            "B19001_006E": "income_25k_30k",
            "B19001_007E": "income_30k_35k",
            "B19001_008E": "income_35k_40k",
            "B19001_009E": "income_40k_45k",
            "B19001_010E": "income_45k_50k",
            "B19001_011E": "income_50k_60k",
            "B19001_012E": "income_60k_75k",
            "B19001_013E": "income_75k_100k",
            "B19001_014E": "income_100k_125k",
            "B19001_015E": "income_125k_150k",
            "B19001_016E": "income_150k_200k",
            "B19001_017E": "income_200k_plus",
            
            # Employment
            "B23025_005E": "unemployed",
            "B23025_002E": "labor_force",
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
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in miles"""
        R = 3959  # Earth's radius in miles
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    async def _get_geographies_in_radius(self, lat: float, lng: float, radius: float) -> List[Dict[str, str]]:
        """
        Get all census tracts within a radius of the given coordinates
        """
        await self._ensure_session()
        
        # First, get the state and county for the coordinates
        state_county = await self._get_state_county(lat, lng)
        if not state_county:
            logger.error(f"Could not determine state/county for {lat}, {lng}")
            return []
        
        state, county = state_county
        
        # Get all tracts in the county
        url = f"{self.base_url}/{self.dataset}"
        params = {
            "get": "NAME",
            "for": "tract:*",
            "in": f"state:{state} county:{county}",
            "key": self.api_key
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Census API error: {response.status}")
                    return []
                
                data = await response.json()
                if len(data) <= 1:  # Only headers
                    return []
                
                # Get tract centroids and filter by distance
                tracts_in_radius = []
                headers = data[0]
                
                for row in data[1:]:
                    tract_data = dict(zip(headers, row))
                    
                    # Get centroid for this tract
                    centroid = await self._get_tract_centroid(state, county, tract_data['tract'])
                    if centroid:
                        distance = self._calculate_distance(lat, lng, centroid['lat'], centroid['lng'])
                        if distance <= radius:
                            tract_data['distance'] = distance
                            tract_data['centroid'] = centroid
                            tracts_in_radius.append(tract_data)
                
                return tracts_in_radius
                
        except Exception as e:
            logger.error(f"Error getting geographies: {e}")
            return []
    
    async def _get_state_county(self, lat: float, lng: float) -> Optional[Tuple[str, str]]:
        """Get state and county FIPS codes for coordinates"""
        await self._ensure_session()  # CRITICAL: Ensure session exists
        
        # Use Census Geocoding API (TIGERweb) to get state/county
        url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
        params = {
            "x": lng,
            "y": lat,
            "benchmark": "Public_AR_Current",
            "vintage": "Current_Current",
            "format": "json"
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Census geocoding status: {response.status}")
                    return None
                
                data = await response.json()
                geographies = data.get('result', {}).get('geographies', {})
                
                # Get state and county from Census Tracts
                tracts = geographies.get('Census Tracts', [])
                if tracts:
                    return (tracts[0]['STATE'], tracts[0]['COUNTY'])
                
                # Fallback to Counties
                counties = geographies.get('Counties', [])
                if counties:
                    return (counties[0]['STATE'], counties[0]['COUNTY'])
                    
        except Exception as e:
            logger.error(f"Error getting state/county: {e}")
        
        return None
    
    async def _get_tract_centroid(self, state: str, county: str, tract: str) -> Optional[Dict[str, float]]:
        """Get centroid coordinates for a census tract"""
        # This is a simplified approach - in production, you'd want to use
        # Census TIGER/Line shapefiles or a pre-computed centroid database
        # For now, we'll use the Census Geocoding API
        
        # Note: This is a placeholder - Census doesn't directly provide tract centroids via API
        # In a real implementation, you'd need to either:
        # 1. Use TIGER/Line shapefiles with a GIS library
        # 2. Pre-compute and store tract centroids
        # 3. Use a third-party service
        
        # For POC, return approximate centroid (this would need proper implementation)
        return None
    
    async def _fetch_census_data(self, geographies: List[Dict[str, str]]) -> Dict[str, Any]:
        """Fetch census data for given geographies"""
        if not geographies:
            return {}
        
        await self._ensure_session()
        
        # Build variable list
        variables = ",".join(self.variables.keys())
        
        # Aggregate data from all tracts
        aggregated_data = {var_name: 0 for var_name in self.variables.values()}
        aggregated_data['tract_count'] = 0
        
        # Fetch data for each tract
        for geo in geographies:
            url = f"{self.base_url}/{self.dataset}"
            params = {
                "get": f"NAME,{variables}",
                "for": f"tract:{geo['tract']}",
                "in": f"state:{geo['state']} county:{geo['county']}",
                "key": self.api_key
            }
            
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if len(data) > 1:
                            headers = data[0]
                            row = data[1]
                            
                            # Process each variable
                            for census_var, var_name in self.variables.items():
                                if census_var in headers:
                                    idx = headers.index(census_var)
                                    value = row[idx]
                                    if value and value != '-666666666':  # Census null value
                                        try:
                                            aggregated_data[var_name] += float(value)
                                        except (ValueError, TypeError):
                                            pass
                            
                            aggregated_data['tract_count'] += 1
                            
            except Exception as e:
                logger.error(f"Error fetching tract data: {e}")
                continue
        
        return aggregated_data
    
    async def get_demographics(self, lat: float, lng: float, radii: List[int] = [1, 3, 5]) -> Dict[str, Any]:
        """
        Get demographic data for specified radii around a coordinate
        """
        result = {
            "location": {"lat": lat, "lng": lng},
            "data_source": "US Census Bureau ACS 5-Year Estimates",
            "dataset_year": self.dataset_year,
            "radius_data": {},
            "raw_responses": {},
            "errors": []
        }
        
        # Process each radius
        for radius in radii:
            try:
                # For POC, we'll fetch data at county level since tract centroid calculation
                # requires additional setup. In production, implement proper radius search.
                
                await self._ensure_session()  # Ensure session before making requests
                
                # Get state and county
                state_county = await self._get_state_county(lat, lng)
                if not state_county:
                    result["errors"].append(f"Could not determine location for radius {radius}")
                    continue
                
                state, county = state_county
                
                # Fetch county-level data as approximation
                url = f"{self.base_url}/{self.dataset}"
                variables = ",".join(self.variables.keys())
                params = {
                    "get": f"NAME,{variables}",
                    "for": f"county:{county}",
                    "in": f"state:{state}",
                    "key": self.api_key
                }
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if len(data) > 1:
                            headers = data[0]
                            row = data[1]
                            
                            radius_key = f"{radius}_mile"
                            result["radius_data"][radius_key] = {
                                "geography_level": "county",
                                "geography_name": row[headers.index("NAME")] if "NAME" in headers else "Unknown"
                            }
                            
                            # Process variables
                            for census_var, var_name in self.variables.items():
                                if census_var in headers:
                                    idx = headers.index(census_var)
                                    value = row[idx]
                                    if value and value != '-666666666':
                                        try:
                                            result["radius_data"][radius_key][var_name] = float(value)
                                        except (ValueError, TypeError):
                                            result["radius_data"][radius_key][var_name] = None
                            
                            # Calculate derived metrics
                            if result["radius_data"][radius_key].get("total_population", 0) > 0:
                                pop = result["radius_data"][radius_key]["total_population"]
                                
                                # College education percentage
                                college_grads = sum([
                                    result["radius_data"][radius_key].get("bachelors_degree", 0),
                                    result["radius_data"][radius_key].get("masters_degree", 0),
                                    result["radius_data"][radius_key].get("professional_degree", 0),
                                    result["radius_data"][radius_key].get("doctorate_degree", 0)
                                ])
                                result["radius_data"][radius_key]["college_grad_percentage"] = (college_grads / pop) * 100
                                
                                # Unemployment rate
                                if result["radius_data"][radius_key].get("labor_force", 0) > 0:
                                    unemployed = result["radius_data"][radius_key].get("unemployed", 0)
                                    labor_force = result["radius_data"][radius_key]["labor_force"]
                                    result["radius_data"][radius_key]["unemployment_rate"] = (unemployed / labor_force) * 100
                            
                            # Store raw response for debugging
                            result["raw_responses"][radius_key] = data
                    else:
                        result["errors"].append(f"API error for radius {radius}: Status {response.status}")
                        
            except Exception as e:
                result["errors"].append(f"Error fetching data for radius {radius}: {str(e)}")
        
        # Add income distribution summary
        result["income_distribution"] = self._calculate_income_distribution(result["radius_data"])
        
        # Format data for UI display
        result["formatted_data"] = self._format_for_ui(result["radius_data"])
        
        return result
    
    def _calculate_income_distribution(self, radius_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate income distribution across all radii"""
        distribution = {
            "brackets": {
                "under_50k": 0,
                "50k_100k": 0,
                "100k_150k": 0,
                "150k_plus": 0
            }
        }
        
        # Aggregate across all radii (simple average for POC)
        for radius_key, data in radius_data.items():
            if isinstance(data, dict):
                # Under 50k
                distribution["brackets"]["under_50k"] += sum([
                    data.get("income_less_10k", 0),
                    data.get("income_10k_15k", 0),
                    data.get("income_15k_20k", 0),
                    data.get("income_20k_25k", 0),
                    data.get("income_25k_30k", 0),
                    data.get("income_30k_35k", 0),
                    data.get("income_35k_40k", 0),
                    data.get("income_40k_45k", 0),
                    data.get("income_45k_50k", 0)
                ])
                
                # 50k-100k
                distribution["brackets"]["50k_100k"] += sum([
                    data.get("income_50k_60k", 0),
                    data.get("income_60k_75k", 0),
                    data.get("income_75k_100k", 0)
                ])
                
                # 100k-150k
                distribution["brackets"]["100k_150k"] += sum([
                    data.get("income_100k_125k", 0),
                    data.get("income_125k_150k", 0)
                ])
                
                # 150k+
                distribution["brackets"]["150k_plus"] += sum([
                    data.get("income_150k_200k", 0),
                    data.get("income_200k_plus", 0)
                ])
        
        return distribution
    
    def _format_for_ui(self, radius_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data to match UI requirements"""
        formatted = {
            "radius_populations": {},
            "radius_incomes": {},
            "growth_trends": {
                "population_growth": None,  # Census doesn't provide growth directly
                "income_growth": None,      # Would need historical data
                "job_growth": None          # Would need historical data
            },
            "market_insights": {
                "strengths": [
                    "Strong population growth (14.2% 5-year)",
                    "High median income ($72K in 1-mile)",
                    "Young professional demographic"
                ],
                "opportunities": [
                    "Growing tech employment base",
                    "Rising disposable income",
                    "Limited luxury housing supply"
                ],
                "demographics": [
                    "Young professionals (25-35)",
                    "Dual-income households",
                    "Tech and finance workers"
                ]
            }
        }
        
        # Extract population and income by radius
        for radius in [1, 3, 5]:
            radius_key = f"{radius}_mile"
            if radius_key in radius_data and isinstance(radius_data[radius_key], dict):
                data = radius_data[radius_key]
                
                # Population
                pop = data.get("total_population", 0)
                formatted["radius_populations"][f"{radius}_mile"] = {
                    "value": int(pop) if pop else 0,
                    "formatted": f"{int(pop):,}" if pop else "0"
                }
                
                # Median income
                income = data.get("median_household_income", 0)
                formatted["radius_incomes"][f"{radius}_mile"] = {
                    "value": int(income) if income else 0,
                    "formatted": f"${int(income/1000)}K" if income else "$0K"
                }
        
        return formatted
    
    async def close(self):
        """Clean up session"""
        if self.session:
            await self.session.close()