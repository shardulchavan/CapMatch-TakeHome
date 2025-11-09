// services/api.ts

import axios from 'axios';
import { API_URL } from '../config';

const API_BASE_URL = API_URL;
// const API_BASE_URL = 'http://localhost:8000';

export interface DemographicsResponse {
  address: string;
  coordinates: {
    lat: number;
    lng: number;
    matched_address: string;
    match_type: string;
    source: string;
  } | null;
  demographics: any; // We'll type this properly later
  performance: {
    geocoding_time?: number;
    demographics_time?: number;
    total_time: number;
  };
  error: string | null;
  timestamp: string;
}

export const api = {
  async getDemographics(address: string): Promise<DemographicsResponse> {
    try {
      const response = await axios.post<DemographicsResponse>(
        `${API_BASE_URL}/demographics`,
        { address }
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Failed to fetch demographics');
      }
      throw error;
    }
  }
};




// const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// // ATTOM Data Types
// export interface AttomDemographics {
//   breakdown: {
//     male_pct: number;
//     female_pct: number;
//     white_pct: number;
//     black_pct: number;
//     asian_pct: number;
//     hispanic_pct: number;
//   };
//   age_distribution: {
//     under_18_pct: number;
//     "18_34_pct": number;
//     "35_64_pct": number;
//     "65_plus_pct": number;
//   };
// }

// export interface AttomHousing {
//   total_units: number;
//   occupied_pct: number;
//   owner_occupied_pct: number;
//   renter_occupied_pct: number;
//   median_rent: number;
//   median_year_built: number;
// }

// export interface AttomEmployment {
//   white_collar_pct: number;
//   blue_collar_pct: number;
//   median_commute_time: number;
//   work_from_home_pct: number;
// }

// export interface AttomTransportation {
//   drive_alone_pct: number;
//   carpool_pct: number;
//   public_transit_pct: number;
//   walk_pct: number;
//   bicycle_pct: number;
//   work_from_home_pct: number;
//   other_pct: number;
// }

// export interface AttomClimate {
//   avg_temp: number;
//   avg_temp_january: number;
//   avg_temp_july: number;
//   annual_rainfall_inches: number;
//   annual_snowfall_inches: number;
//   clear_days: number;
//   rainy_days: number;
// }

// export interface AttomCrime {
//   crime_index: number;
//   murder_index: number;
//   robbery_index: number;
//   assault_index: number;
//   burglary_index: number;
//   theft_index: number;
// }

// export interface AttomAirQuality {
//   air_pollution_index: number;
//   ozone_index: number;
//   particulate_index: number;
//   carbon_monoxide_index: number;
// }

// export interface AttomCostIndex {
//   annual_expenditures: number;
//   housing: number;
//   food: number;
//   transportation: number;
//   healthcare: number;
// }

// export interface AttomFormattedData {
//   geography: {
//     type: string;
//     name: string;
//     geo_id_v4: string;
//     area_sq_miles: number;
//     coordinates: {
//       latitude: number;
//       longitude: number;
//     };
//   };
//   demographics: AttomDemographics;
//   housing: AttomHousing;
//   employment: AttomEmployment;
//   transportation: AttomTransportation;
//   climate: AttomClimate;
//   crime: AttomCrime;
//   air_quality: AttomAirQuality;
//   cost_index: AttomCostIndex;
//   summary_stats: {
//     key_metrics: string[];
//     strengths: string[];
//     considerations: string[];
//   };
// }

// export interface AttomData {
//   address: string;
//   data_source: string;
//   selected_geography: {
//     geoIdV4: string;
//     geographyName: string;
//     geographyTypeName: string;
//     geographyTypeAbbreviation: string;
//     details: {
//       zipCodeTabulationAreaCode?: string;
//       longitude: number;
//       latitude: number;
//       areaSquareMiles: number;
//     };
//   };
//   errors: string[];
//   formatted_data: AttomFormattedData;
// }

// // Census Data Types (existing)
// export interface Coordinates {
//   lat: number;
//   lng: number;
//   matched_address: string;
//   match_type: string;
//   source: string;
// }

// export interface RadiusData {
//   current: {
//     total_population: number;
//     median_household_income: number;
//     median_home_value: number;
//     bachelors_degree: number;
//     masters_degree: number;
//     professional_degree: number;
//     doctorate_degree: number;
//     median_age: number;
//     unemployed: number;
//     labor_force: number;
//     employed: number;
//     unemployment_rate: number;
//     college_grad_percentage: number;
//     [key: string]: any; // For additional fields
//   };
//   historical: {
//     total_population: number;
//     median_household_income: number;
//     median_home_value: number;
//     bachelors_degree: number;
//     masters_degree: number;
//     professional_degree: number;
//     doctorate_degree: number;
//     median_age: number;
//     unemployed: number;
//     labor_force: number;
//     employed: number;
//     unemployment_rate: number;
//     college_grad_percentage: number;
//     [key: string]: any;
//   };
//   geography_level: string;
//   tract_count: number;
//   aggregation_info: string;
// }

// export interface GrowthMetrics {
//   population_growth: number;
//   income_growth: number;
//   job_growth: number;
//   unemployment_rate_change: number;
// }

// export interface MarketInsights {
//   demographic_strengths: string[];
//   market_opportunities: string[];
//   target_demographics: string[];
//   insights_metadata: {
//     generated: boolean;
//     version: string;
//     engine: string;
//     timestamp: string;
//   };
// }

// export interface Demographics {
//   location: {
//     lat: number;
//     lng: number;
//   };
//   data_source: string;
//   current_year: string;
//   historical_year: string;
//   radius_data: {
//     "1_mile": RadiusData;
//     "3_mile": RadiusData;
//     "5_mile": RadiusData;
//   };
//   growth_metrics: GrowthMetrics;
//   raw_responses: any;
//   errors: string[];
//   map_circles: any[];
//   formatted_data: {
//     radius_populations: {
//       [key: string]: {
//         value: number;
//         formatted: string;
//       };
//     };
//     radius_incomes: {
//       [key: string]: {
//         value: number;
//         formatted: string;
//       };
//     };
//     growth_trends: {
//       [key: string]: {
//         value: number;
//         formatted: string;
//       };
//     };
//     income_distribution: {
//       [key: string]: number[];
//     };
//   };
//   market_insights: MarketInsights;
// }

// // Main API Response Interface
// export interface DemographicsResponse {
//   address: string;
//   coordinates: Coordinates | null;
//   demographics: Demographics | null;
//   attom_data: AttomData | null; // New ATTOM data field
//   performance: {
//     geocoding_time: number;
//     demographics_time: number;
//     total_time: number;
//   };
//   error: string | null;
//   timestamp: string;
// }

// // API Error class
// export class APIError extends Error {
//   constructor(message: string, public statusCode?: number) {
//     super(message);
//     this.name = 'APIError';
//   }
// }

// // API service
// export const api = {
//   async getDemographics(address: string): Promise<DemographicsResponse> {
//     try {
//       const response = await fetch(`${API_BASE_URL}/demographics`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ address }),
//       });

//       if (!response.ok) {
//         throw new APIError(
//           `API request failed: ${response.statusText}`,
//           response.status
//         );
//       }

//       const data = await response.json();
//       return data;
//     } catch (error) {
//       if (error instanceof APIError) {
//         throw error;
//       }
      
//       // Network or other errors
//       throw new APIError(
//         error instanceof Error ? error.message : 'An unexpected error occurred'
//       );
//     }
//   },
// };




