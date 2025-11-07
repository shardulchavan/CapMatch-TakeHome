import React from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import RadiusCards from '../components/RadiusCards';
import GrowthTrends from '../components/GrowthTrends';
import MarketMetricsDashboard from '../components/MarketMetricsDashboard'; 
import IncomeDistributionChart from '../components/IncomeDistributionChart';
import EducationDistribution from '../components/EducationDistribution';
import HomeValueGrowthChart from '../components/HomeValue';
import MarketInsights from '../components/MarketInsights';
import InteractiveMap from '../components/InteractiveMap';

const DemographicsDetail: React.FC = () => {
  const { address } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  // Get data from navigation state
  const data = location.state?.data;
  
  if (!data || !data.demographics) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-card p-8 text-center">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">No Data Available</h2>
            <p className="text-gray-600 mb-6">Please search for an address first.</p>
            <button
              onClick={() => navigate('/')}
              className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              Back to Search
            </button>
          </div>
        </div>
      </div>
    );
  }

  const demographics = data.demographics;
  const coordinates = data.coordinates;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <button
            onClick={() => navigate('/')}
            className="flex items-center text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Search
          </button>
          
          <h1 className="text-3xl font-bold text-gray-900">
            {coordinates?.matched_address || decodeURIComponent(address || '')}
          </h1>
          <p className="text-gray-600 mt-2">Market Analysis Dashboard</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Population Overview */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Population Overview</h2>
          <RadiusCards radiusData={demographics.radius_data} />
        </section>

        {/* Growth Metrics */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Growth Metrics</h2>
          <GrowthTrends growthMetrics={demographics.growth_metrics} />
        </section>

        {/* Market Metrics Dashboard - NEW COMPONENT */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Market Analysis</h2>
          <MarketMetricsDashboard radiusData={demographics.radius_data} />
        </section>

        {/* Two Column Layout */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Income Distribution */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Household Income</h2>
            <IncomeDistributionChart 
              incomeData={demographics.formatted_data?.income_distribution} 
              radiusData={demographics.radius_data}
            />
          </section>

          {/* Right Column - Property Values */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Property Values</h2>
            <HomeValueGrowthChart radiusData={demographics.radius_data} />
          </section>
        </div>

        {/* Education Distribution */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Education Levels</h2>
          <EducationDistribution radiusData={demographics.radius_data} />
        </section>

        {/* Market Insights */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Key Insights</h2>
          <MarketInsights insights={demographics.market_insights} />
        </section>

        {/* Interactive Map */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Geographic Coverage</h2>
          <InteractiveMap 
            center={[coordinates.lat, coordinates.lng]}
            circles={demographics.map_circles}
            address={coordinates.matched_address}
          />
        </section>
      </div>
    </div>
  );
};

export default DemographicsDetail;