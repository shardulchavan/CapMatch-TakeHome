import aiohttp
import asyncio
from typing import Dict, List, Any, Optional, Tuple
import os
from math import radians, sin, cos, sqrt, atan2
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CensusClient:
    """
    Client for US Census Bureau API
    Fetches demographic data for specified coordinates and radii
    Includes historical data for growth calculations
    """
    
    def __init__(self):
        self.api_key = os.getenv("CENSUS_API_KEY", "")  # Optional but recommended
        self.base_url = "https://api.census.gov/data"
        self.session = None
        
        # Current and historical years for ACS 5-year data
        self.current_year = "2022"  # Latest available ACS 5-year
        self.historical_year = "2017"  # For 5-year comparison (2017 vs 2022)
        
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
            "B23025_003E": "employed",
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
    
    async def _get_state_county(self, lat: float, lng: float) -> Optional[Tuple[str, str]]:
        """Get state and county FIPS codes for coordinates"""
        await self._ensure_session()
        
        # Use Census Geocoding API (TIGERweb) to get state/county
        url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
        params = {
            "x": lng,
            "y": lat,
            "benchmark": "Public_AR_Current",
            "vintage": "Current_Current",
            "format": "json"
        }
        
        print(f"[CENSUS GEOCODING] Calling Census geocoder API...")
        print(f"[CENSUS GEOCODING] URL: {url}")
        
        try:
            async with self.session.get(url, params=params) as response:
                print(f"[CENSUS GEOCODING] Response status: {response.status}")
                if response.status != 200:
                    logger.error(f"Census geocoding status: {response.status}")
                    return None
                
                data = await response.json()
                geographies = data.get('result', {}).get('geographies', {})
                
                # Get state and county from Census Tracts
                tracts = geographies.get('Census Tracts', [])
                if tracts:
                    state, county = tracts[0]['STATE'], tracts[0]['COUNTY']
                    print(f"[CENSUS GEOCODING] ✓ Found from tracts - State: {state}, County: {county}")
                    return (state, county)
                
                # Fallback to Counties
                counties = geographies.get('Counties', [])
                if counties:
                    state, county = counties[0]['STATE'], counties[0]['COUNTY']
                    print(f"[CENSUS GEOCODING] ✓ Found from counties - State: {state}, County: {county}")
                    return (state, county)
                
                print("[CENSUS GEOCODING] ✗ No geography data found in response")
                    
        except Exception as e:
            print(f"[CENSUS GEOCODING] ERROR: {str(e)}")
            logger.error(f"Error getting state/county: {e}")
        
        return None
    
    async def _fetch_census_data_for_year(self, state: str, county: str, year: str) -> Dict[str, Any]:
        """Fetch census data for a specific year"""
        await self._ensure_session()
        
        dataset = f"{year}/acs/acs5"
        url = f"{self.base_url}/{dataset}"
        variables = ",".join(self.variables.keys())
        
        params = {
            "get": f"NAME,{variables}",
            "for": f"county:{county}",
            "in": f"state:{state}",
            "key": self.api_key
        }
        
        print(f"[CENSUS API - {year}] Fetching data...")
        print(f"[CENSUS API - {year}] Dataset: {dataset}")
        
        try:
            async with self.session.get(url, params=params) as response:
                print(f"[CENSUS API - {year}] Response status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    
                    if len(data) > 1:
                        headers = data[0]
                        row = data[1]
                        
                        result = {
                            "year": year,
                            "geography_name": row[headers.index("NAME")] if "NAME" in headers else "Unknown"
                        }
                        
                        print(f"[CENSUS API - {year}] Geography: {result['geography_name']}")
                        
                        # Process variables
                        variables_found = 0
                        for census_var, var_name in self.variables.items():
                            if census_var in headers:
                                idx = headers.index(census_var)
                                value = row[idx]
                                if value and value != '-666666666':
                                    try:
                                        result[var_name] = float(value)
                                        variables_found += 1
                                    except (ValueError, TypeError):
                                        result[var_name] = None
                        
                        print(f"[CENSUS API - {year}] ✓ Found {variables_found}/{len(self.variables)} variables")
                        return result
                else:
                    print(f"[CENSUS API - {year}] ✗ API error: Status {response.status}")
                    logger.error(f"Census API error for year {year}: Status {response.status}")
                    return {"year": year, "error": f"API error: {response.status}"}
                    
        except Exception as e:
            print(f"[CENSUS API - {year}] ERROR: {str(e)}")
            logger.error(f"Error fetching data for year {year}: {e}")
            return {"year": year, "error": str(e)}
    
    def _calculate_growth_rate(self, current_value: float, historical_value: float) -> Optional[float]:
        """Calculate 5-year growth rate as a percentage"""
        if historical_value and historical_value > 0 and current_value is not None:
            return ((current_value - historical_value) / historical_value) * 100
        return None
    
    def _calculate_growth_metrics(self, current_data: Dict[str, Any], historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate 5-year growth metrics"""
        growth_metrics = {
            "population_growth": None,
            "income_growth": None,
            "job_growth": None,
            "unemployment_rate_change": None
        }
        
        # Population growth
        if current_data.get("total_population") and historical_data.get("total_population"):
            growth_metrics["population_growth"] = self._calculate_growth_rate(
                current_data["total_population"],
                historical_data["total_population"]
            )
        
        # Income growth
        if current_data.get("median_household_income") and historical_data.get("median_household_income"):
            growth_metrics["income_growth"] = self._calculate_growth_rate(
                current_data["median_household_income"],
                historical_data["median_household_income"]
            )
        
        # Job growth (based on employed population)
        if current_data.get("employed") and historical_data.get("employed"):
            growth_metrics["job_growth"] = self._calculate_growth_rate(
                current_data["employed"],
                historical_data["employed"]
            )
        
        # Calculate unemployment rate change (in percentage points)
        current_unemployment_rate = None
        historical_unemployment_rate = None
        
        if current_data.get("labor_force", 0) > 0:
            current_unemployment_rate = (current_data.get("unemployed", 0) / current_data["labor_force"]) * 100
        
        if historical_data.get("labor_force", 0) > 0:
            historical_unemployment_rate = (historical_data.get("unemployed", 0) / historical_data["labor_force"]) * 100
        
        if current_unemployment_rate is not None and historical_unemployment_rate is not None:
            growth_metrics["unemployment_rate_change"] = current_unemployment_rate - historical_unemployment_rate
        
        return growth_metrics
    
    async def get_demographics_with_history(self, lat: float, lng: float, radii: List[int] = [1, 3, 5]) -> Dict[str, Any]:
        """
        Get demographic data for specified radii around a coordinate
        Includes historical data and growth calculations
        """
        print(f"\n[CENSUS CLIENT] Starting demographics fetch for coordinates: ({lat}, {lng})")
        print(f"[CENSUS CLIENT] Years: Current={self.current_year}, Historical={self.historical_year}")
        
        result = {
            "location": {"lat": lat, "lng": lng},
            "data_source": "US Census Bureau ACS 5-Year Estimates",
            "current_year": self.current_year,
            "historical_year": self.historical_year,
            "radius_data": {},
            "growth_metrics": {},
            "raw_responses": {},
            "errors": []
        }
        
        try:
            await self._ensure_session()
            print("[CENSUS CLIENT] HTTP session ready")
            
            # Get state and county
            print("[CENSUS CLIENT] Getting state/county for coordinates...")
            state_county = await self._get_state_county(lat, lng)
            if not state_county:
                print("[CENSUS CLIENT] ERROR: Could not determine state/county")
                result["errors"].append("Could not determine location")
                return result
            
            state, county = state_county
            print(f"[CENSUS CLIENT] Location found: State={state}, County={county}")
            
            # Try to use radius aggregator for more accurate data
            try:
                from radius_aggregator import RadiusAggregator
                print("[CENSUS CLIENT] Using RadiusAggregator for tract-level data")
                
                async with RadiusAggregator(self.api_key) as aggregator:
                    # Get radius-specific demographics
                    radius_results = await aggregator.get_radius_demographics(
                        lat, lng, radii, state, county, self.variables,
                        self.current_year, self.historical_year
                    )
                    
                    # Process results for each radius
                    for radius in radii:
                        radius_key = f"{radius}_mile"
                        radius_data = radius_results["radius_data"].get(radius_key, {})
                        
                        # Extract current and historical data
                        current_data = radius_data.get("current", {}).get("data", {})
                        historical_data = radius_data.get("historical", {}).get("data", {})
                        
                        # If we got tract-level data, use it
                        if current_data and radius_data.get("current", {}).get("tract_count", 0) > 0:
                            result["radius_data"][radius_key] = {
                                "current": current_data,
                                "historical": historical_data,
                                "geography_level": "tract-aggregated",
                                "tract_count": radius_data.get("tract_count", 0),
                                "aggregation_info": radius_data.get("current", {}).get("coverage", "")
                            }
                            print(f"[CENSUS CLIENT] {radius_key}: Using tract-aggregated data ({radius_data.get('tract_count', 0)} tracts)")
                        else:
                            # Fall back to county data for this radius
                            print(f"[CENSUS CLIENT] {radius_key}: Falling back to county data")
                            # Fetch county data as before
                            current_task = self._fetch_census_data_for_year(state, county, self.current_year)
                            historical_task = self._fetch_census_data_for_year(state, county, self.historical_year)
                            current_county, historical_county = await asyncio.gather(current_task, historical_task)
                            
                            result["radius_data"][radius_key] = {
                                "current": current_county,
                                "historical": historical_county,
                                "geography_level": "county"
                            }
                    
                    # Add map circles data
                    populations = {}
                    for radius_key, data in result["radius_data"].items():
                        pop = data.get("current", {}).get("total_population", 0)
                        populations[radius_key] = int(pop) if pop else 0
                    
                    result["map_circles"] = aggregator.create_map_circles(lat, lng, radii, populations)
                    print(f"[CENSUS CLIENT] Created circles with radii: {[c['properties']['radius_miles'] for c in result['map_circles']]}")    
                    
            except ImportError:
                print("[CENSUS CLIENT] RadiusAggregator not available, using county-level data")
                # Original fallback code
                current_task = self._fetch_census_data_for_year(state, county, self.current_year)
                historical_task = self._fetch_census_data_for_year(state, county, self.historical_year)
                
                current_data, historical_data = await asyncio.gather(current_task, historical_task)
                
                for radius in radii:
                    radius_key = f"{radius}_mile"
                    result["radius_data"][radius_key] = {
                        "current": current_data,
                        "historical": historical_data,
                        "geography_level": "county"
                    }
            
            # Calculate growth metrics based on the largest radius data
            largest_radius = f"{max(radii)}_mile"
            if result["radius_data"].get(largest_radius):
                current = result["radius_data"][largest_radius].get("current", {})
                historical = result["radius_data"][largest_radius].get("historical", {})
                
                print("[CENSUS CLIENT] Calculating growth metrics...")
                result["growth_metrics"] = self._calculate_growth_metrics(current, historical)
                
                # Print growth metrics
                for metric, value in result["growth_metrics"].items():
                    if value is not None:
                        print(f"[CENSUS CLIENT]   {metric}: {value:.2f}%")
            
            # Add formatted data for UI
            print("[CENSUS CLIENT] Formatting data for UI...")
            result["formatted_data"] = self._format_for_demographics_card(result)
            
            # Generate market insights
            try:
                from market_insights import generate_market_insights
                print("[CENSUS CLIENT] Generating market insights...")
                result["market_insights"] = generate_market_insights(result)
                print("[CENSUS CLIENT] ✓ Market insights generated")
            except ImportError:
                print("[CENSUS CLIENT] Market insights module not available")
            except Exception as e:
                print(f"[CENSUS CLIENT] Error generating insights: {e}")
                result["market_insights"] = {
                    "demographic_strengths": ["Data analysis in progress"],
                    "market_opportunities": ["Market evaluation pending"],
                    "target_demographics": ["Demographics being analyzed"]
                }
            
            print("[CENSUS CLIENT] ✓ Demographics processing complete")
            
        except Exception as e:
            print(f"[CENSUS CLIENT] ERROR: {str(e)}")
            result["errors"].append(f"Error processing demographics: {str(e)}")
        
        return result
    
    def _format_for_demographics_card(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data specifically for the Demographics card UI"""
        formatted = {
            "radius_populations": {},
            "radius_incomes": {},
            "growth_trends": {
                "population_growth": {
                    "value": data["growth_metrics"].get("population_growth"),
                    "formatted": f"{data['growth_metrics'].get('population_growth', 0):.1f}%" if data["growth_metrics"].get("population_growth") else "N/A"
                },
                "income_growth": {
                    "value": data["growth_metrics"].get("income_growth"),
                    "formatted": f"{data['growth_metrics'].get('income_growth', 0):.1f}%" if data["growth_metrics"].get("income_growth") else "N/A"
                },
                "job_growth": {
                    "value": data["growth_metrics"].get("job_growth"),
                    "formatted": f"{data['growth_metrics'].get('job_growth', 0):.1f}%" if data["growth_metrics"].get("job_growth") else "N/A"
                }
            }
        }
        
        # Extract population and income by radius
        for radius in [1, 3, 5]:
            radius_key = f"{radius}_mile"
            if radius_key in data["radius_data"]:
                current = data["radius_data"][radius_key].get("current", {})
                
                # Population
                pop = current.get("total_population", 0)
                formatted["radius_populations"][radius_key] = {
                    "value": int(pop) if pop else 0,
                    "formatted": f"{int(pop):,}" if pop else "0"
                }
                
                # Median income
                income = current.get("median_household_income", 0)
                formatted["radius_incomes"][radius_key] = {
                    "value": int(income) if income else 0,
                    "formatted": f"${int(income):,}" if income else "$0"
                }
        
        # Income distribution (from current data)
        if data["radius_data"]:
            # Use 3-mile radius as primary
            current_data = data["radius_data"].get("3_mile", {}).get("current", {})
            
            formatted["income_distribution"] = {
                "One Mile": [
                    self._calculate_income_bracket_percentage(current_data, "under_50k"),
                    self._calculate_income_bracket_percentage(current_data, "50k_100k"),
                    self._calculate_income_bracket_percentage(current_data, "100k_150k"),
                    self._calculate_income_bracket_percentage(current_data, "150k_plus")
                ],
                "Three Mile": [
                    self._calculate_income_bracket_percentage(current_data, "under_50k"),
                    self._calculate_income_bracket_percentage(current_data, "50k_100k"),
                    self._calculate_income_bracket_percentage(current_data, "100k_150k"),
                    self._calculate_income_bracket_percentage(current_data, "150k_plus")
                ],
                "Five Mile": [
                    self._calculate_income_bracket_percentage(current_data, "under_50k"),
                    self._calculate_income_bracket_percentage(current_data, "50k_100k"),
                    self._calculate_income_bracket_percentage(current_data, "100k_150k"),
                    self._calculate_income_bracket_percentage(current_data, "150k_plus")
                ]
            }
        
        return formatted
    
    def _calculate_income_bracket_percentage(self, data: Dict[str, Any], bracket: str) -> float:
        """Calculate percentage for income bracket"""
        total_households = sum([
            data.get(f"income_{key}", 0) for key in [
                "less_10k", "10k_15k", "15k_20k", "20k_25k", "25k_30k",
                "30k_35k", "35k_40k", "40k_45k", "45k_50k", "50k_60k",
                "60k_75k", "75k_100k", "100k_125k", "125k_150k",
                "150k_200k", "200k_plus"
            ]
        ])
        
        if total_households == 0:
            return 0.0
        
        bracket_count = 0
        
        if bracket == "under_50k":
            bracket_count = sum([
                data.get(f"income_{key}", 0) for key in [
                    "less_10k", "10k_15k", "15k_20k", "20k_25k", "25k_30k",
                    "30k_35k", "35k_40k", "40k_45k", "45k_50k"
                ]
            ])
        elif bracket == "50k_100k":
            bracket_count = sum([
                data.get(f"income_{key}", 0) for key in [
                    "50k_60k", "60k_75k", "75k_100k"
                ]
            ])
        elif bracket == "100k_150k":
            bracket_count = sum([
                data.get(f"income_{key}", 0) for key in [
                    "100k_125k", "125k_150k"
                ]
            ])
        elif bracket == "150k_plus":
            bracket_count = sum([
                data.get(f"income_{key}", 0) for key in [
                    "150k_200k", "200k_plus"
                ]
            ])
        
        return (bracket_count / total_households) * 100
    
    async def get_demographics(self, lat: float, lng: float, radii: List[int] = [1, 3, 5]) -> Dict[str, Any]:
        """
        Wrapper method to maintain backward compatibility
        Calls the new method with historical data
        """
        return await self.get_demographics_with_history(lat, lng, radii)
    
    async def close(self):
        """Clean up session"""
        if self.session:
            await self.session.close()


# Example usage
async def main():
    async with CensusClient() as client:
        # Test with San Francisco coordinates
        result = await client.get_demographics_with_history(
            lat=37.7749,
            lng=-122.4194,
            radii=[1, 3, 5]
        )
        
        print("Population Growth:", result["growth_metrics"]["population_growth"])
        print("Income Growth:", result["growth_metrics"]["income_growth"])
        print("Job Growth:", result["growth_metrics"]["job_growth"])
        print("\nFormatted for UI:", result["formatted_data"]["growth_trends"])

if __name__ == "__main__":
    asyncio.run(main())