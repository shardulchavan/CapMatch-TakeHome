import aiohttp
import asyncio
from typing import Dict, List, Tuple, Optional, Any
from math import radians, sin, cos, sqrt, atan2, pi
import logging
from collections import defaultdict
import random
import statistics

logger = logging.getLogger(__name__)

class RadiusAggregator:
    """
    Aggregates census data by actual radius distances using tract centroids
    Accurate geographic selection instead of tract number approximation
    """
    
    def __init__(self, census_api_key: str = ""):
        self.api_key = census_api_key
        self.base_url = "https://api.census.gov/data"
        self.session = None
        # Cache for tract data to avoid repeated API calls
        self._tract_cache = {}
    
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
        """Calculate distance between two points in miles using Haversine formula"""
        R = 3959  # Earth's radius in miles
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    async def get_all_county_tracts(self, state: str, county: str) -> List[Dict[str, Any]]:
        """Get all tracts in a county"""
        cache_key = f"{state}_{county}_tracts"
        if cache_key in self._tract_cache:
            return self._tract_cache[cache_key]
        
        await self._ensure_session()
        
        dataset = "2022/acs/acs5"
        url = f"{self.base_url}/{dataset}"
        
        params = {
            "get": "NAME",
            "for": "tract:*",
            "in": f"state:{state} county:{county}",
            "key": self.api_key
        }
        
        try:
            print(f"[RADIUS AGG] Fetching all tracts for county {county}")
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                if len(data) <= 1:
                    return []
                
                headers = data[0]
                tracts = []
                
                for row in data[1:]:
                    tract_info = dict(zip(headers, row))
                    tract_info['state'] = state
                    tract_info['county'] = county
                    tracts.append(tract_info)
                
                self._tract_cache[cache_key] = tracts
                print(f"[RADIUS AGG] Found {len(tracts)} tracts in county")
                return tracts
                
        except Exception as e:
            logger.error(f"Error getting tracts: {e}")
            return []
    
    async def get_tract_centroids(self, state: str, county: str) -> Dict[str, Tuple[float, float]]:
        """
        Get centroids (center points) for all tracts in a county
        Returns dict of tract_id: (lat, lng)
        """
        cache_key = f"{state}_{county}_centroids"
        if cache_key in self._tract_cache:
            return self._tract_cache[cache_key]
        
        await self._ensure_session()
        
        # Try Census Gazetteer first (most reliable for centroids)
        centroids = await self._get_centroids_from_gazetteer(state, county)
        
        if centroids:
            self._tract_cache[cache_key] = centroids
            return centroids
        
        # Fallback: Try to get from ACS profile dataset
        dataset = "2022/acs/acs5/profile"
        url = f"{self.base_url}/{dataset}"
        
        params = {
            "get": "NAME,INTPTLAT,INTPTLON",
            "for": "tract:*",
            "in": f"state:{state} county:{county}",
            "key": self.api_key
        }
        
        try:
            print(f"[CENTROIDS] Trying ACS profile dataset for county {county}")
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if len(data) > 1:
                        headers = data[0]
                        
                        # Find indices
                        lat_idx = headers.index('INTPTLAT') if 'INTPTLAT' in headers else None
                        lon_idx = headers.index('INTPTLON') if 'INTPTLON' in headers else None
                        tract_idx = -1  # Last column
                        
                        if lat_idx is not None and lon_idx is not None:
                            centroids = {}
                            for row in data[1:]:
                                tract = row[tract_idx]
                                try:
                                    lat = float(row[lat_idx])
                                    lng = float(row[lon_idx])
                                    if lat != 0 and lng != 0:  # Filter invalid coords
                                        centroids[tract] = (lat, lng)
                                except (ValueError, TypeError, IndexError):
                                    continue
                            
                            if centroids:
                                self._tract_cache[cache_key] = centroids
                                print(f"[CENTROIDS] Got centroids for {len(centroids)} tracts from ACS")
                                return centroids
                    
        except Exception as e:
            print(f"[CENTROIDS] ACS error: {e}")
        
        print(f"[CENTROIDS] No centroid data available for county {county}")
        return {}
    
    async def _get_centroids_from_gazetteer(self, state: str, county: str) -> Dict[str, Tuple[float, float]]:
        """
        Get centroids from Census Gazetteer files (most reliable source)
        """
        # Census Gazetteer provides tract centroids
        gazetteer_url = f"https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2022_Gazetteer/2022_gaz_tracts_{state}.txt"
        
        try:
            print(f"[CENTROIDS] Fetching from gazetteer for state {state}")
            async with self.session.get(gazetteer_url) as response:
                if response.status == 200:
                    text = await response.text()
                    lines = text.strip().split('\n')
                    
                    if not lines:
                        return {}
                    
                    # Parse tab-delimited file
                    headers = lines[0].split('\t')
                    
                    # Find column indices - Gazetteer format
                    geoid_idx = next((i for i, h in enumerate(headers) if 'GEOID' in h), None)
                    lat_idx = next((i for i, h in enumerate(headers) if 'INTPTLAT' in h), None)
                    lon_idx = next((i for i, h in enumerate(headers) if 'INTPTLON' in h or 'INTPTLONG' in h), None)
                    
                    if None in [geoid_idx, lat_idx, lon_idx]:
                        print(f"[CENTROIDS] Missing required columns in gazetteer")
                        return {}
                    
                    centroids = {}
                    target_county_prefix = state + county
                    
                    for line in lines[1:]:
                        parts = line.split('\t')
                        
                        if len(parts) > max(geoid_idx, lat_idx, lon_idx):
                            geoid = parts[geoid_idx].strip()
                            
                            # GEOID format: SSCCCTTTTTT (2 state, 3 county, 6 tract)
                            if geoid.startswith(target_county_prefix):
                                tract = geoid[5:]  # Extract tract part
                                try:
                                    lat = float(parts[lat_idx].strip())
                                    lng = float(parts[lon_idx].strip())
                                    if lat != 0 and lng != 0:
                                        centroids[tract] = (lat, lng)
                                except (ValueError, IndexError):
                                    continue
                    
                    print(f"[CENTROIDS] Got {len(centroids)} centroids from gazetteer")
                    return centroids
                    
        except Exception as e:
            print(f"[CENTROIDS] Gazetteer error: {e}")
        
        return {}
    
    async def _find_tract_for_point(self, lat: float, lng: float, all_tracts: List[Dict]) -> Optional[Dict]:
        """
        Use Census geocoding to find which tract contains the given point
        """
        await self._ensure_session()
        
        url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
        params = {
            "x": lng,
            "y": lat,
            "benchmark": "Public_AR_Current",
            "vintage": "Current_Current",
            "format": "json"
        }
        
        try:
            print(f"[TRACT FINDER] Looking up tract for point ({lat}, {lng})")
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    geographies = data.get('result', {}).get('geographies', {})
                    
                    census_tracts = geographies.get('Census Tracts', [])
                    if census_tracts and len(census_tracts) > 0:
                        tract_info = census_tracts[0]
                        target_tract_number = tract_info.get('TRACT')
                        
                        print(f"[TRACT FINDER] Point is in tract: {target_tract_number}")
                        
                        for tract in all_tracts:
                            if tract.get('tract') == target_tract_number:
                                print(f"[TRACT FINDER] ✓ Found matching tract in county list")
                                tract['is_center_tract'] = True
                                return tract
                        
                        print(f"[TRACT FINDER] ✗ Tract {target_tract_number} not found in county list")
                    else:
                        print(f"[TRACT FINDER] ✗ No tract info in geocoding response")
                        
        except Exception as e:
            print(f"[TRACT FINDER] Error: {str(e)}")
        
        return None
    
    async def _approximate_tract_distribution(self, all_tracts: List[Dict], center_lat: float, 
                                            center_lng: float, radius_miles: float) -> List[Dict[str, Any]]:
        """
        Use actual geographic distance based on tract centroids
        This is the accurate method that replaces the tract number approximation
        """
        print(f"[RADIUS AGG] Using centroid-based selection for {radius_miles} mile radius")
        
        if not all_tracts:
            return []
        
        state = all_tracts[0].get('state')
        county = all_tracts[0].get('county')
        
        # Get centroids for all tracts
        centroids = await self.get_tract_centroids(state, county)
        
        if not centroids:
            print("[RADIUS AGG] WARNING: No centroids available, using fallback method")
            # Fallback to tract number method (less accurate)
            center_tract = await self._find_tract_for_point(center_lat, center_lng, all_tracts)
            return self._estimate_tracts_in_radius_fallback(all_tracts, center_lat, center_lng, radius_miles, center_tract)
        
        # Calculate actual distances and select tracts within radius
        tracts_with_distance = []
        
        for tract in all_tracts:
            tract_id = tract.get('tract')
            if tract_id in centroids:
                centroid_lat, centroid_lng = centroids[tract_id]
                
                # Calculate actual distance
                distance = self._calculate_distance(
                    center_lat, center_lng,
                    centroid_lat, centroid_lng
                )
                
                # Include if within radius (add 10% buffer for edge cases)
                if distance <= radius_miles * 1.1:
                    tract_copy = tract.copy()  # Don't modify original
                    tract_copy['distance'] = distance
                    tract_copy['centroid_lat'] = centroid_lat
                    tract_copy['centroid_lng'] = centroid_lng
                    tract_copy['within_radius'] = distance <= radius_miles
                    tracts_with_distance.append(tract_copy)
        
        # Sort by distance
        tracts_with_distance.sort(key=lambda x: x['distance'])
        
        print(f"[RADIUS AGG] Found {len(tracts_with_distance)} tracts within {radius_miles} miles")
        
        # Log some debug info
        if tracts_with_distance:
            closest = tracts_with_distance[0]
            farthest = tracts_with_distance[-1]
            print(f"[RADIUS AGG] Closest tract: {closest['tract']} at {closest['distance']:.2f} miles")
            print(f"[RADIUS AGG] Farthest tract: {farthest['tract']} at {farthest['distance']:.2f} miles")
            
            # Count strictly within radius
            strictly_within = sum(1 for t in tracts_with_distance if t['within_radius'])
            print(f"[RADIUS AGG] Strictly within radius: {strictly_within}, with buffer: {len(tracts_with_distance)}")
        
        return tracts_with_distance
    
    def _estimate_tracts_in_radius_fallback(self, all_tracts: List[Dict], center_lat: float,
                                          center_lng: float, radius_miles: float, 
                                          center_tract: Optional[Dict] = None) -> List[Dict]:
        """
        Fallback method using tract numbers (less accurate)
        Only used when centroid data is unavailable
        """
        print(f"[RADIUS EST] WARNING: Using tract number approximation (less accurate)")
        
        if center_tract:
            print(f"[RADIUS EST] Using center tract: {center_tract.get('tract')}")
            center_tract_num = str(center_tract.get('tract', ''))
            base_num = center_tract_num.split('.')[0] if '.' in center_tract_num else center_tract_num
            
            def tract_distance(tract):
                tract_num = str(tract.get('tract', ''))
                tract_base = tract_num.split('.')[0] if '.' in tract_num else tract_num
                try:
                    return abs(float(tract_base) - float(base_num))
                except:
                    return 9999
            
            sorted_tracts = sorted(all_tracts, key=tract_distance)
            if center_tract not in sorted_tracts:
                sorted_tracts.insert(0, center_tract)
        else:
            sorted_tracts = sorted(all_tracts, key=lambda t: t.get('tract', '0'))
        
        # Estimate tract count based on typical density
        tract_count_estimate = {
            1: min(10, max(3, len(all_tracts) // 50)),
            3: min(50, max(10, len(all_tracts) // 10)),
            5: min(150, max(20, len(all_tracts) // 3))
        }
        
        count = tract_count_estimate.get(int(radius_miles), 20)
        selected = sorted_tracts[:count]
        
        print(f"[RADIUS EST] Selected {len(selected)} tracts for {radius_miles} mile radius")
        
        for i, tract in enumerate(selected):
            tract_copy = tract.copy()
            if tract.get('is_center_tract'):
                tract_copy['distance'] = 0.1
            else:
                tract_copy['distance'] = (i / len(selected)) * radius_miles * 0.9
            tract_copy['approximated'] = True
            selected[i] = tract_copy
        
        return selected
    
    async def get_radius_demographics(self, lat: float, lng: float, radii: List[int], 
                                    state: str, county: str, variables: Dict[str, str],
                                    current_year: str = "2022", 
                                    historical_year: str = "2017") -> Dict[str, Any]:
        """
        Main method to get demographics for multiple radii
        Process all radii in parallel for performance
        """
        print(f"\n[RADIUS AGG] Starting radius demographics for {lat}, {lng}")
        print(f"[RADIUS AGG] State: {state}, County: {county}")
        
        # Get all tracts in county once
        all_tracts = await self.get_all_county_tracts(state, county)
        
        if not all_tracts:
            print("[RADIUS AGG] No tracts found, returning empty result")
            return {"radius_data": {}, "error": "No tracts found"}
        
        results = {
            "location": {"lat": lat, "lng": lng},
            "state": state,
            "county": county,
            "radius_data": {}
        }
        
        # Create tasks for all radii at once
        print(f"[RADIUS AGG] Processing {len(radii)} radii in parallel...")
        radius_tasks = []
        
        for radius in radii:
            task = self._process_single_radius(
                radius, all_tracts, lat, lng, variables,
                current_year, historical_year, state, county
            )
            radius_tasks.append((radius, task))
        
        # Execute all radius calculations in parallel
        start_time = asyncio.get_event_loop().time()
        radius_results = await asyncio.gather(
            *[task for _, task in radius_tasks],
            return_exceptions=True
        )
        elapsed = asyncio.get_event_loop().time() - start_time
        print(f"[RADIUS AGG] All radii processed in {elapsed:.2f} seconds")
        
        # Combine results
        for i, (radius, _) in enumerate(radius_tasks):
            radius_key = f"{radius}_mile"
            if isinstance(radius_results[i], Exception):
                print(f"[RADIUS AGG] Error for {radius} mile: {radius_results[i]}")
                results["radius_data"][radius_key] = {
                    "error": str(radius_results[i]),
                    "current": {"data": {}, "tract_count": 0},
                    "historical": {"data": {}, "tract_count": 0}
                }
            else:
                results["radius_data"][radius_key] = radius_results[i]
        
        # Generate map circles
        populations = {}
        for radius_key, data in results["radius_data"].items():
            pop = data.get("current", {}).get("data", {}).get("total_population", 0)
            populations[radius_key] = int(pop) if pop else 0
        
        results["map_circles"] = self.create_map_circles(lat, lng, radii, populations)
        
        return results
    
    async def _process_single_radius(self, radius: int, all_tracts: List[Dict],
                                   lat: float, lng: float, variables: Dict[str, str],
                                   current_year: str, historical_year: str,
                                   state: str, county: str) -> Dict[str, Any]:
        """
        Process a single radius - can be run in parallel with other radii
        """
        print(f"[RADIUS AGG] Starting {radius} mile radius processing")
        
        # Get tracts for this radius using accurate centroid method
        radius_tracts = await self._approximate_tract_distribution(all_tracts, lat, lng, radius)
        print(f"[RADIUS AGG] {radius} mile: Selected {len(radius_tracts)} tracts")
        
        # Fetch current and historical data in parallel
        current_task = self._aggregate_tracts_data(
            radius_tracts, current_year, variables
        )
        historical_task = self._aggregate_tracts_data(
            radius_tracts, historical_year, variables
        )
        
        # Execute both year fetches in parallel
        current_data, historical_data = await asyncio.gather(
            current_task, historical_task,
            return_exceptions=True
        )
        
        # Handle errors
        if isinstance(current_data, Exception):
            print(f"[RADIUS AGG] {radius} mile: Current year error: {current_data}")
            current_data = {"data": {}, "tract_count": 0}
        
        if isinstance(historical_data, Exception):
            print(f"[RADIUS AGG] {radius} mile: Historical year error: {historical_data}")
            historical_data = {"data": {}, "tract_count": 0}
        
        print(f"[RADIUS AGG] {radius} mile radius completed")
        
        return {
            "current": current_data,
            "historical": historical_data,
            "tract_count": len(radius_tracts),
            "radius_miles": radius
        }
    
    async def _aggregate_tracts_data(self, tracts: List[Dict], year: str, 
                                   variables: Dict[str, str]) -> Dict[str, Any]:
        """
        Fetch and aggregate data for multiple tracts using batch requests
        Properly handles median values
        """
        if not tracts:
            return {"data": {}, "tract_count": 0}
        
        await self._ensure_session()
        
        print(f"[RADIUS AGG] Aggregating {year} data for {len(tracts)} tracts")
        
        # Initialize aggregated data - separate handling for medians
        aggregated = defaultdict(float)
        median_collections = defaultdict(list)
        successful_tracts = 0
        
        dataset = f"{year}/acs/acs5"
        url = f"{self.base_url}/{dataset}"
        variable_list = ",".join(variables.keys())
        
        # Group tracts by state/county
        tract_groups = defaultdict(list)
        for tract in tracts:
            key = f"{tract['state']}_{tract['county']}"
            tract_groups[key].append(tract['tract'])
        
        # Create batch requests
        batch_tasks = []
        
        for (state_county), tract_list in tract_groups.items():
            state, county = state_county.split('_')
            
            # Request all tracts in county, then filter
            params = {
                "get": f"NAME,{variable_list}",
                "for": "tract:*",
                "in": f"state:{state} county:{county}",
                "key": self.api_key
            }
            
            task = self._fetch_tract_batch(url, params, variables, set(tract_list))
            batch_tasks.append(task)
        
        print(f"[RADIUS AGG] Making {len(batch_tasks)} batch API calls instead of {len(tracts)} individual calls")
        
        # Execute all batch requests in parallel
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Aggregate results from all batches
        for result in batch_results:
            if isinstance(result, Exception):
                print(f"[RADIUS AGG] Batch error: {result}")
                continue
            if result and isinstance(result, dict):
                for tract_data in result.get('tracts', []):
                    successful_tracts += 1
                    for var_name, value in tract_data.items():
                        if var_name not in ["NAME", "tract"] and value is not None:
                            # Handle median values differently
                            if var_name in ["median_household_income", "median_home_value", "median_age"]:
                                median_collections[var_name].append(value)
                            else:
                                # Sum other values normally
                                aggregated[var_name] += value
        
        print(f"[RADIUS AGG] Successfully aggregated {successful_tracts}/{len(tracts)} tracts")
        
        # Convert to regular dict
        result_data = dict(aggregated)
        
        # Calculate proper medians
        for var_name, values in median_collections.items():
            if values:
                # Use median of medians (not perfect but better than sum)
                result_data[var_name] = statistics.median(values)
            else:
                result_data[var_name] = 0
        
        # Calculate derived fields
        if result_data.get("labor_force", 0) > 0:
            unemployed = result_data.get("unemployed", 0)
            result_data["unemployment_rate"] = (unemployed / result_data["labor_force"]) * 100
        
        # Calculate college graduate percentage
        if result_data.get("total_population", 0) > 0:
            college_grads = sum([
                result_data.get("bachelors_degree", 0),
                result_data.get("masters_degree", 0),
                result_data.get("professional_degree", 0),
                result_data.get("doctorate_degree", 0)
            ])
            result_data["college_grad_percentage"] = (college_grads / result_data["total_population"]) * 100
        
        return {
            "data": result_data,
            "tract_count": successful_tracts,
            "aggregation_level": "tract",
            "coverage": f"{successful_tracts}/{len(tracts)} tracts"
        }
    
    async def _fetch_tract_batch(self, url: str, params: Dict, 
                               variables: Dict[str, str], 
                               target_tracts: set) -> Dict[str, Any]:
        """
        Fetch data for multiple tracts in one API call
        """
        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    text = await response.text()
                    return {"tracts": []}
                
                data = await response.json()
                if len(data) <= 1:
                    return {"tracts": []}
                
                headers = data[0]
                
                # Geographic identifiers are always the last columns
                tract_idx = -1  # Last column is tract
                county_idx = -2  # Second to last is county
                state_idx = -3  # Third to last is state
                
                # Process all rows
                result_tracts = []
                
                for row in data[1:]:
                    # Get tract number from the last column
                    tract_number = row[tract_idx]
                    
                    # Check if this tract is in our target list
                    if tract_number in target_tracts:
                        tract_data = {'tract': tract_number}
                        
                        # Extract variables
                        for census_var, var_name in variables.items():
                            if census_var in headers:
                                idx = headers.index(census_var)
                                value = row[idx]
                                if value and value != '-666666666' and value != 'null':
                                    try:
                                        tract_data[var_name] = float(value)
                                    except (ValueError, TypeError):
                                        tract_data[var_name] = None
                        
                        if len(tract_data) > 1:  # Has data beyond just tract number
                            result_tracts.append(tract_data)
                
                return {"tracts": result_tracts}
                
        except Exception as e:
            print(f"[RADIUS AGG] Batch fetch error: {e}")
            return {"tracts": []}
    
    def create_map_circles(self, lat: float, lng: float, radii: List[int], 
                         populations: Dict[str, int]) -> List[Dict[str, Any]]:
        """Create circle data for map visualization"""
        circles = []
        colors = {
            1: "#FF6B6B",  # Red for 1 mile
            3: "#4ECDC4",  # Teal for 3 miles  
            5: "#45B7D1"   # Blue for 5 miles
        }
        
        for radius in radii:
            radius_key = f"{radius}_mile"
            
            # Create circle points
            points = []
            num_points = 64
            
            for i in range(num_points):
                angle = (2 * pi / num_points) * i
                
                # Calculate point on circle
                lat_offset = (radius / 69.0) * sin(angle)
                lng_offset = (radius / (69.0 * cos(radians(lat)))) * cos(angle)
                
                points.append([lng + lng_offset, lat + lat_offset])
            
            points.append(points[0])  # Close the circle
            
            circles.append({
                "type": "Feature",
                "properties": {
                    "radius_miles": radius,
                    "population": populations.get(radius_key, 0),
                    "population_formatted": f"{populations.get(radius_key, 0):,}",
                    "center": [lng, lat],
                    "color": colors.get(radius, "#999999"),
                    "fillOpacity": 0.15,
                    "strokeOpacity": 0.8,
                    "strokeWeight": 2
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [points]
                }
            })
        
        return circles
    
    async def close(self):
        """Clean up session"""
        if self.session:
            await self.session.close()