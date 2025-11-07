import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

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
