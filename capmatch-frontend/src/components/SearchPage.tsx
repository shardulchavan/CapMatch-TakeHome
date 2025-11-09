// src/components/SearchPage.tsx

import React, { useState } from 'react';
import { api, DemographicsResponse } from '../services/api';
import DemographicsCard from './DemographicsCard';

const SearchPage: React.FC = () => {
  const [address, setAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DemographicsResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!address.trim()) {
      setError('Please enter an address');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await api.getDemographics(address);
      
      if (data.error) {
        setError(data.error);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            CapMatch Market Intelligence
          </h1>
          <p className="text-lg text-gray-600">
            Enter an address to generate comprehensive demographic analysis
          </p>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex gap-4">
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="Enter address (e.g., 555 California St, San Francisco, CA)"
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading}
                className="px-8 py-3 bg-primary text-white font-medium rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Analyzing...' : 'Analyze Market'}
              </button>
            </div>
          </div>
        </form>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-8">
            <p className="font-medium">Error</p>
            <p>{error}</p>
          </div>
        )}

        {/* Loading Animation */}
        {loading && (
          <div className="bg-white rounded-lg shadow-card p-12 text-center">
            <div className="inline-flex items-center">
              <svg className="animate-spin h-8 w-8 text-primary mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="text-lg text-gray-700">
                Analyzing market data...
              </span>
            </div>
            <div className="mt-4 text-sm text-gray-500">
              Fetching census data, calculating demographics, and generating insights
            </div>
          </div>
        )}

        {/* Results - Demographics Card */}
        {result && !loading && !result.error && result.demographics && (
          <div className="max-w-2xl mx-auto">
            <DemographicsCard data={result} address={address} />
          </div>
        )}
        
        {/* Debug info - remove this after fixing */}
        {result && !loading && !result.demographics && (
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded-lg mb-8">
            <p className="font-medium">Debug: Demographics data not found</p>
            <pre className="text-xs mt-2">{JSON.stringify(result, null, 2).slice(0, 500)}...</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchPage;