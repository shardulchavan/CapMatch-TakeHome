from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="CapMatch Demographics Card API")

# Try to import census clients with error handling
try:
    from census_geocoding_client import CensusGeocodingClient
    from census_client import CensusClient
    CENSUS_CLIENTS_AVAILABLE = True
    print("[STARTUP] ✓ Census clients imported successfully")
except ImportError as e:
    print(f"[STARTUP] WARNING: Could not import census clients: {e}")
    print("[STARTUP] Running in mock mode")
    CENSUS_CLIENTS_AVAILABLE = False
    
    # Create mock clients for testing
    class CensusGeocodingClient:
        async def geocode(self, address):
            print(f"[MOCK] Geocoding address: {address}")
            return {"lat": 37.7749, "lng": -122.4194, "matched_address": address}
    
    class CensusClient:
        async def get_demographics_with_history(self, lat, lng, radii):
            print(f"[MOCK] Getting demographics for ({lat}, {lng})")
            return {
                "growth_metrics": {
                    "population_growth": 14.2,
                    "income_growth": 18.5,
                    "job_growth": 22.3
                },
                "formatted_data": {
                    "radius_populations": {
                        "1_mile": {"value": 45000, "formatted": "45,000"},
                        "3_mile": {"value": 185000, "formatted": "185,000"},
                        "5_mile": {"value": 425000, "formatted": "425,000"}
                    }
                }
            }

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "https://capmatch-takehome-backend.onrender.com",
        "https://cap-match-take-home-git-main-shardulchavans-projects.vercel.app/",
        "https://cap-match-take-home.vercel.app/",
        "https://*.vercel.app"
                   ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class AddressRequest(BaseModel):
    address: str

class DemographicsResponse(BaseModel):
    address: str
    coordinates: Optional[Dict[str, Any]]
    demographics: Optional[Dict[str, Any]]
    performance: Dict[str, float]
    error: Optional[str]
    timestamp: str

# Initialize API clients
census_geocoding_client = CensusGeocodingClient()
census_client = CensusClient()

# Startup event
@app.on_event("startup")
async def startup_event():
    print("\n" + "="*60)
    print("CapMatch Demographics Card API")
    print("="*60)
    print(f"Mode: {'Production' if CENSUS_CLIENTS_AVAILABLE else 'Mock'}")
    print(f"Census API Key: {'Configured' if os.getenv('CENSUS_API_KEY') else 'Not configured'}")
    print(f"Server: http://localhost:8000")
    print(f"Docs: http://localhost:8000/docs")
    print("="*60 + "\n")

@app.get("/")
async def root():
    return {
        "message": "CapMatch Demographics Card API",
        "endpoints": {
            "/demographics": "POST - Get demographic data for an address",
            "/health": "GET - Check API health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "census_api_key": "configured" if os.getenv("CENSUS_API_KEY") else "not configured"
    }

@app.post("/demographics", response_model=DemographicsResponse)
async def get_demographics(request: AddressRequest):
    """
    Main endpoint that:
    1. Geocodes the address using Census Bureau
    2. Fetches demographic data with historical comparison
    3. Returns formatted data for the Demographics card
    """
    start_time = time.time()
    print(f"\n{'='*60}")
    print(f"[{datetime.utcnow().isoformat()}] NEW REQUEST RECEIVED")
    print(f"Address: {request.address}")
    print(f"{'='*60}")
    
    try:
        # Step 1: Geocode the address
        print("\n[STEP 1] Starting geocoding...")
        geocoding_start = time.time()
        coordinates = await census_geocoding_client.geocode(request.address)
        geocoding_time = time.time() - geocoding_start
        print(f"[STEP 1] ✓ Geocoding completed in {geocoding_time:.2f} seconds")
        print(f"         Coordinates: lat={coordinates['lat']}, lng={coordinates['lng']}")
        
        # Step 2: Fetch demographics with history
        print("\n[STEP 2] Fetching demographics data...")
        print(f"         Radii: [1, 3, 5] miles")
        demographics_start = time.time()
        demographics = await census_client.get_demographics_with_history(
            lat=coordinates["lat"],
            lng=coordinates["lng"],
            radii=[1, 3, 5]
        )
        demographics_time = time.time() - demographics_start
        print(f"[STEP 2] ✓ Demographics fetched in {demographics_time:.2f} seconds")
        
        # Check if we got growth metrics
        if demographics.get("growth_metrics"):
            print(f"\n[GROWTH METRICS]")
            print(f"  Population Growth: {demographics['growth_metrics'].get('population_growth', 'N/A')}%")
            print(f"  Income Growth: {demographics['growth_metrics'].get('income_growth', 'N/A')}%")
            print(f"  Job Growth: {demographics['growth_metrics'].get('job_growth', 'N/A')}%")
        
        # Step 3: Return response
        total_time = time.time() - start_time
        print(f"\n[STEP 3] Preparing response...")
        print(f"[SUCCESS] ✓ Total processing time: {total_time:.2f} seconds")
        print(f"{'='*60}\n")
        
        return DemographicsResponse(
            address=request.address,
            coordinates=coordinates,
            demographics=demographics,
            performance={
                "geocoding_time": geocoding_time,
                "demographics_time": demographics_time,
                "total_time": total_time
            },
            error=None,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        # Return error response
        total_time = time.time() - start_time
        print(f"\n[ERROR] ✗ Request failed after {total_time:.2f} seconds")
        print(f"[ERROR] Details: {str(e)}")
        print(f"{'='*60}\n")
        
        return DemographicsResponse(
            address=request.address,
            coordinates=None,
            demographics=None,
            performance={"total_time": total_time},
            error=str(e),
            timestamp=datetime.utcnow().isoformat()
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)