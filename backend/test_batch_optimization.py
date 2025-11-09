# test_batch_optimization.py
import asyncio
import time
from radius_aggregator import RadiusAggregator
from census_geocoding_client import CensusGeocodingClient

async def test_batch_performance():
    # Static test address
    TEST_ADDRESS = "7575 Frankford Rd, Dallas, TX 75252"
    
    print(f"Testing with address: {TEST_ADDRESS}")
    
    # Initialize variables outside try block
    lat = None
    lng = None
    state_fips = None
    county_fips = None
    county_name = None
    
    # First, geocode the address to get coordinates AND county info
    async with CensusGeocodingClient() as geocoding_client:
        try:
            # Geocode to get coordinates
            geocoding_result = await geocoding_client.geocode(TEST_ADDRESS)
            lat = geocoding_result['lat']
            lng = geocoding_result['lng']
            print(f"Coordinates: {lat}, {lng}")
            
            # Get county info from reverse geocoding
            reverse_result = await geocoding_client.reverse_geocode(lat, lng)
            
            if 'state_fips' in reverse_result and 'county_fips' in reverse_result:
                state_fips = reverse_result['state_fips']
                county_fips = reverse_result['county_fips']
                county_name = reverse_result.get('county', 'Unknown')
                print(f"Location: {county_name}, State FIPS: {state_fips}, County FIPS: {county_fips}")
            else:
                print("Could not determine county from reverse geocoding")
                raise Exception("No county info in reverse geocoding")
                
        except Exception as e:
            print(f"Geocoding error: {e}")
            print("Using fallback Dallas coordinates")
            lat = 32.997764194807
            lng = -96.773256326953
            state_fips = "48"  # Texas
            county_fips = "085"  # Collin County (where the address actually is)
    
    # Make sure we have all required values
    if not all([lat, lng, state_fips, county_fips]):
        print("ERROR: Missing required location data")
        return
    
    # Now test the radius aggregator with correct county
    async with RadiusAggregator() as aggregator:
        # Time the optimized version
        start = time.time()
        
        # Simple variables for testing
        test_variables = {
            "B01003_001E": "total_population",
            "B19013_001E": "median_household_income"
        }
        
        result = await aggregator.get_radius_demographics(
            lat, lng, [1, 3, 5], 
            state_fips, county_fips, 
            test_variables,
            "2022", "2017"
        )
        
        elapsed = time.time() - start
        
        print(f"\n{'='*50}")
        print(f"Performance Test Results:")
        print(f"Total time: {elapsed:.2f} seconds")
        print(f"{'='*50}")
        
        # Show results for each radius
        for radius in [1, 3, 5]:
            data = result['radius_data'][f'{radius}_mile']
            current = data.get('current', {})
            historical = data.get('historical', {})
            
            print(f"\n{radius} mile radius:")
            print(f"  Tracts processed: {data.get('tract_count', 0)}")
            
            # Current year data
            current_pop = current.get('data', {}).get('total_population', 0)
            current_income = current.get('data', {}).get('median_household_income', 0)
            print(f"  2022 Population: {current_pop:,.0f}")
            print(f"  2022 Median Income: ${current_income:,.0f}")

            print(f"  Selection method: {'Centroid-based' if 'centroid_lat' in data else 'Fallback'}")
            print(f"  Accuracy: Geographic distance calculation")
            
            # Historical comparison
            hist_pop = historical.get('data', {}).get('total_population', 0)
            if hist_pop > 0 and current_pop > 0:
                growth = ((current_pop - hist_pop) / hist_pop) * 100
                print(f"  Population Growth (5yr): {growth:.1f}%")
        
        print(f"\n{'='*50}")
        print("Debug Summary:")
        print(f"{'='*50}")
        
        # Check tract selection
        for radius in [1, 3, 5]:
            tract_count = result['radius_data'][f'{radius}_mile'].get('tract_count', 0)
            success_rate = result['radius_data'][f'{radius}_mile'].get('current', {}).get('coverage', 'N/A')
            print(f"{radius}-mile: {tract_count} tracts, coverage: {success_rate}")

async def test_simple_tract_fetch():
    """Test fetching a single known tract to verify API works"""
    print("\n" + "="*50)
    print("Testing single tract fetch")
    print("="*50)
    
    async with RadiusAggregator() as aggregator:
        # Test with a known tract in Collin County
        test_tract = {
            'tract': '031709',
            'state': '48',
            'county': '085',
            'NAME': 'Test tract'
        }
        
        result = await aggregator._aggregate_tracts_data(
            [test_tract],
            "2022",
            {"B01003_001E": "total_population"}
        )
        
        print(f"Single tract result: {result}")

if __name__ == "__main__":
    # Run main test
    asyncio.run(test_batch_performance())
    
    # Also run simple test
    asyncio.run(test_simple_tract_fetch())