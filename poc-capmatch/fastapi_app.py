from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Import our API clients (to be created next)
from api_clients.census_geocoding_client import CensusGeocodingClient
from api_clients.census_client import CensusClient
from api_clients.attom_client import AttomClient

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="CapMatch Market Data POC")

# Add CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class AddressRequest(BaseModel):
    address: str

class APIResponse(BaseModel):
    address: str
    # census_coordinates includes lat/lng plus some string metadata (matched_address, source, etc.)
    # Use Any for values to accept both floats and strings returned by the geocoder.
    census_coordinates: Optional[Dict[str, Any]]
    census_data: Optional[Dict[str, Any]]
    attom_data: Optional[Dict[str, Any]]
    performance: Dict[str, float]
    errors: Dict[str, Optional[str]]
    timestamp: str

# Initialize API clients
census_geocoding_client = CensusGeocodingClient()
census_client = CensusClient()
attom_client = AttomClient()

@app.get("/")
async def root():
    return {
        "message": "CapMatch Market Data POC API",
        "endpoints": {
            "/analyze-address": "POST - Analyze demographic data for an address",
            "/health": "GET - Check API health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "census_geocoding": "US Census Geocoding Service (Free)",
            "census_data": "US Census API" if os.getenv("CENSUS_API_KEY") else "Not configured",
            "attom": "ATTOM Data API" if os.getenv("ATTOM_API_KEY") else "Not configured"
        }
    }

@app.post("/analyze-address", response_model=APIResponse)
async def analyze_address(request: AddressRequest):
    """
    Main endpoint that:
    1. Geocodes the address using Census Bureau (for Census API)
    2. Fetches data from Census and ATTOM APIs in parallel
    3. ATTOM uses its own address search, Census uses geocoded coordinates
    4. Returns combined results with performance metrics
    """
    start_time = time.time()
    
    # Initialize response structure
    response = {
        "address": request.address,
        "census_coordinates": None,
        "census_data": None,
        "attom_data": None,
        "performance": {},
        "errors": {
            "census_geocoding": None,
            "census": None,
            "attom": None
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        # Define async tasks for parallel and independent execution
        async def fetch_census_data_with_geocoding():
            """Census flow: Geocode first, then fetch demographics"""
            try:
                # Geocode using Census Bureau
                geocoding_start = time.time()
                coordinates = await census_geocoding_client.geocode(request.address)
                response["census_coordinates"] = coordinates
                response["performance"]["census_geocoding_time"] = time.time() - geocoding_start
                
                # Fetch Census demographics
                census_start = time.time()
                data = await census_client.get_demographics(
                    lat=coordinates["lat"],
                    lng=coordinates["lng"],
                    radii=[1, 3, 5]  # miles
                )
                response["performance"]["census_data_time"] = time.time() - census_start
                response["performance"]["census_total_time"] = time.time() - geocoding_start
                return data
            except Exception as e:
                if "coordinates" not in locals():
                    response["errors"]["census_geocoding"] = str(e)
                else:
                    response["errors"]["census"] = str(e)
                return None
        
        async def fetch_attom_data_with_address():
            """ATTOM flow: Use built-in address search"""
            try:
                attom_start = time.time()
                # ATTOM can search by address directly
                data = await attom_client.get_demographics_by_address(
                    address=request.address,
                    radii=[1, 3, 5]  # miles
                )
                response["performance"]["attom_total_time"] = time.time() - attom_start
                return data
            except Exception as e:
                response["errors"]["attom"] = str(e)
                return None
        
        # Execute both API flows completely independently and in parallel
        api_start = time.time()
        
        census_task = asyncio.create_task(fetch_census_data_with_geocoding())
        attom_task = asyncio.create_task(fetch_attom_data_with_address())
        
        # Wait for both to complete
        census_data, attom_data = await asyncio.gather(census_task, attom_task)
        
        response["census_data"] = census_data
        response["attom_data"] = attom_data
        response["performance"]["parallel_execution_time"] = time.time() - api_start
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Calculate total time
    response["performance"]["total_time"] = time.time() - start_time
    
    return APIResponse(**response)

# Additional debug endpoints for testing individual APIs
@app.post("/test-census-geocoding")
async def test_census_geocoding(request: AddressRequest):
    """Test Census Geocoding Service independently"""
    try:
        start = time.time()
        coords = await census_geocoding_client.geocode(request.address)
        return {
            "status": "success", 
            "coordinates": coords,
            "time": time.time() - start
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/test-census-data")
async def test_census_data(lat: float, lng: float):
    """Test Census Data API with coordinates"""
    try:
        start = time.time()
        data = await census_client.get_demographics(
            lat=lat,
            lng=lng,
            radii=[1, 3, 5]
        )
        return {
            "status": "success",
            "data": data,
            "time": time.time() - start
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


    
@app.post("/test-attom-poi")
async def test_attom_poi(request: AddressRequest):
    """
    Test ATTOM POI API with PERSONAL SERVICES and HEALTH CARE SERVICES categories
    
    Example addresses to test:
    - "10 Wall St., New York, NY 10005"
    - "1 Market Street, San Francisco, CA 94105"  
    - "350 5th Avenue, New York, NY 10118"
    """
    try:
        start = time.time()
        
        # Call the POI API
        poi_data = await attom_client.get_pois_by_address(
            address=request.address,
            radius=5  # 5 mile radius
        )
        
        execution_time = time.time() - start
        
        # Add execution time to response
        poi_data["execution_time"] = execution_time
        
        # Format response for easy viewing
        response = {
            "status": "success" if not poi_data.get("errors") else "partial_success",
            "address_searched": request.address,
            "execution_time": f"{execution_time:.2f} seconds",
            "summary": poi_data.get("summary", {}),
            "total_pois_found": poi_data.get("poi_count", 0),
            "pois_by_category": {
                "PERSONAL_SERVICES": {
                    "count": len(poi_data["pois_by_category"].get("PERSONAL SERVICES", [])),
                    "locations": poi_data["pois_by_category"].get("PERSONAL SERVICES", [])[:3]  # Show first 5
                },
                "HEALTH_CARE_SERVICES": {
                    "count": len(poi_data["pois_by_category"].get("HEALTH CARE SERVICES", [])),
                    "locations": poi_data["pois_by_category"].get("HEALTH CARE SERVICES", [])[:3]
                },
                "EDUCATION_SERVICES": {
                    "count": len(poi_data["pois_by_category"].get("EDUCATION", [])),
                    "locations": poi_data["pois_by_category"].get("EDUCATION", [])[:3]
                },
                "FINANCIAL_SERVICES": {
                    "count": len(poi_data["pois_by_category"].get("BANKS – FINANCIAL", [])),
                    "locations": poi_data["pois_by_category"].get("BANKS – FINANCIAL", [])[:3]
                },
            "api_status": poi_data.get("api_status", {}),
            "errors": poi_data.get("errors", []),
            "raw_response_available": poi_data.get("raw_response") is not None
        }
        }
        
        # Add helpful message if no POIs found
        if response["total_pois_found"] == 0 and not response["errors"]:
            response["message"] = "No POIs found in the specified categories within 5 miles of this address."
        
        return response
        
    except Exception as e:
        logger.error(f"Error in test_attom_poi: {str(e)}", exc_info=True)
        return {
            "status": "error", 
            "error": str(e),
            "address_searched": request.address
        }
    
@app.get("/test-attom-poi-simple")
async def test_attom_poi_simple():
    """
    Simple test to check ATTOM POI endpoint directly
    """
    try:
        await attom_client._ensure_session()
        
        # Test with exact parameters from documentation
        url = "https://api.gateway.attomdata.com/v4/neighborhood/poi"
        
        params = {
            "address": "10 Wall St., New York, NY 10005",
            "radius": "5",
            "categoryName": "PERSONAL SERVICES"  # Using exact category from docs
        }
        
        headers = {
            "accept": "application/json",
            "apikey": attom_client.api_key
        }
        
        async with attom_client.session.get(url, headers=headers, params=params) as response:
            status = response.status
            text = await response.text()
            
            try:
                data = await response.json()
            except:
                data = {"raw_text": text}
            
            return {
                "status_code": status,
                "url_called": str(response.url),
                "headers_sent": dict(headers),
                "params_sent": params,
                "response": data
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }

@app.post("/test-attom-community")
async def test_attom_community(request: AddressRequest):
    """
    Test ATTOM Community API v4 - Get demographic data for an address
    
    Example addresses to test:
    - "10 Wall St., New York, NY 10005" (ZIP-based lookup)
    - "Las Vegas, NV" (City-based lookup)
    - "San Francisco, CA 94105" (City + ZIP)
    """
    try:
        start = time.time()
        
        # Call the Community API
        community_data = await attom_client.get_community_by_address(
            address=request.address
        )
        
        execution_time = time.time() - start
        
        # Format response for easy viewing
        response = {
            "status": "success" if not community_data.get("errors") else "partial_success",
            "address_searched": request.address,
            "execution_time": f"{execution_time:.2f} seconds",
            "selected_geography": community_data.get("selected_geography", {}),
            "formatted_data": community_data.get("formatted_data", {}),
            "location_matches_found": len(community_data.get("location_matches", [])),
            "errors": community_data.get("errors", [])
        }
        
        # Add summary if available
        if "formatted_data" in community_data and "summary_stats" in community_data["formatted_data"]:
            response["summary"] = community_data["formatted_data"]["summary_stats"]
        
        # Add helpful message if no data found
        if not community_data.get("formatted_data") and not response["errors"]:
            response["message"] = "No community data found for this address."
        
        return response
        
    except Exception as e:
        logger.error(f"Error in test_attom_community: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "address_searched": request.address

        }
    
@app.get("/test-location-lookup-exact")
async def test_location_lookup_exact():
    """
    Test Location Lookup API with EXACT parameters from documentation
    Documentation example: https://api.gateway.attomdata.com/v4/location/
    """
    try:
        await attom_client._ensure_session()
        
        # Exact URL and params from documentation
        url = "https://api.gateway.attomdata.com/v4/location/lookup"
        
        params = {
            "name": "Union City",
            "geographyTypeAbbreviation": "PL"  # PL = Place (default according to docs)
        }
        
        headers = {
            "accept": "application/json",
            "apikey": attom_client.api_key
        }
        
        async with attom_client.session.get(url, headers=headers, params=params) as response:
            status = response.status
            text = await response.text()
            
            try:
                data = await response.json()
            except:
                data = {"raw_text": text}
            
            return {
                "status_code": status,
                "url_called": str(response.url),
                "headers_sent": dict(headers),
                "params_sent": params,
                "response": data,
                "documentation_example": "https://api.gateway.attomdata.com/v4/location/lookup?name=Las%20Vegas"
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }
    
@app.get("/test-community-api-direct")
async def test_community_api_direct():
    """
    Test Community API directly with static geoIdV4
    Using exact format from API documentation
    """
    try:
        await attom_client._ensure_session()
        
        # Exact endpoint and parameters from documentation
        url = "https://api.gateway.attomdata.com/v4/neighborhood/community"
        
        # Static geoIdV4 for testing
        params = {
            "geoIdV4": "00100fb7c9887068f18cf8b24df3709c"
        }
        
        headers = {
            "accept": "application/json",
            "apikey": attom_client.api_key
        }
        
        print(f"Testing Community API with geoIdV4: {params['geoIdV4']}")
        
        async with attom_client.session.get(url, headers=headers, params=params) as response:
            status = response.status
            text = await response.text()
            
            try:
                data = await response.json()
                
                # Extract key information if successful
                summary = {}
                if status == 200 and "response" in data:
                    result = data.get("response", {}).get("result", {})
                    community = result.get("community", [])
                    
                    if community and isinstance(community, list):
                        first_community = community[0] if community else {}
                        
                        # Extract some key fields to verify data structure
                        summary = {
                            "has_demographics": "demographics" in first_community,
                            "has_crime": "crime" in first_community,
                            "has_climate": "climate" in first_community,
                            "has_air_quality": "airQuality" in first_community,
                            "total_fields": len(first_community),
                            "sample_fields": list(first_community.keys())[:10] if first_community else []
                        }
                
            except:
                data = {"raw_text": text[:500]}
                summary = {"parse_error": "Could not parse JSON response"}
            
            return {
                "status_code": status,
                "url_called": str(response.url),
                "headers_sent": dict(headers),
                "params_sent": params,
                "summary": summary,
                "response": data,
                "documentation_example": "GET /v4/neighborhood/community?geoIdV4=dd4ec3218a89807fc1c63dd7265cc1bc"
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)