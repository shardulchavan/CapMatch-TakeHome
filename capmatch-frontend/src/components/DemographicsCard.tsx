import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MiniMap from './MiniMap';

interface DemographicsCardProps {
  data: any; // We'll type this properly later
  address: string;
}

const DemographicsCard: React.FC<DemographicsCardProps> = ({ data, address }) => {
  const navigate = useNavigate();
  const [animatedValues, setAnimatedValues] = useState({
    population: 0,
    growthRate: 0,
    collegeGrad: 0
  });

  // Extract key metrics
  const demographics = data.demographics;
  const coordinates = data.coordinates;
  
  // Get 5-mile population (fixing the aggregated value)
  const population5Mile = demographics?.radius_data?.['5_mile']?.current?.total_population || 0;

  
  // Get growth metrics
  const populationGrowth = demographics?.growth_metrics?.population_growth || 0;
  
  // Get college graduation percentage for 3-mile radius
  const collegeGradPercent = demographics?.radius_data?.['3_mile']?.current?.college_grad_percentage || 
    demographics?.radius_data?.['3_mile']?.current?.data?.college_grad_percentage || 0;

  // Animate numbers on mount
  useEffect(() => {
    const duration = 1000; // 1 second
    const steps = 60;
    const stepTime = duration / steps;
    
    let currentStep = 0;
    const timer = setInterval(() => {
      currentStep++;
      const progress = currentStep / steps;
      
      setAnimatedValues({
        population: Math.floor(population5Mile * progress),
        growthRate: parseFloat((populationGrowth * progress).toFixed(1)),
        collegeGrad: Math.floor(collegeGradPercent * progress)
      });
      
      if (currentStep >= steps) {
        clearInterval(timer);
      }
    }, stepTime);
    
    return () => clearInterval(timer);
  }, [population5Mile, populationGrowth, collegeGradPercent]);

  const handleViewDetails = () => {
    navigate(`/analysis/${encodeURIComponent(address)}`, { 
      state: { data: data } 
    });
  };

  // Create simplified circles data for mini map
  const mapCircles = demographics?.map_circles || [];
  const centerCoords: [number, number] = coordinates ? 
    [coordinates.lng, coordinates.lat] : [-122.4194, 37.7749];

  return (
    <div className="bg-white rounded-xl shadow-card hover:shadow-card-hover transition-all duration-300 overflow-hidden group">
      {/* Address Header */}
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <span className="text-lg">📍</span>
          <div>
            <h3 className="font-semibold text-gray-900">
              {coordinates?.matched_address || address}
            </h3>
            <p className="text-sm text-gray-500 flex items-center gap-2 mt-1">
              <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Verified by {coordinates?.source || 'Census Bureau'}
            </p>
          </div>
        </div>
      </div>

      {/* Mini Map */}
      <div className="px-6 py-4">
        <MiniMap circles={mapCircles} center={centerCoords} />
      </div>

      {/* Key Metrics */}
      <div className="px-6 py-4 grid grid-cols-3 gap-4 border-t border-gray-100">
        {/* Population */}
        <div className="text-center">
          <div className="flex items-center justify-center mb-2">
            <span className="text-2xl">👥</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {animatedValues.population.toLocaleString()}
          </div>
          <div className="text-sm text-gray-500">Population</div>
          <div className="text-xs text-gray-400 mt-1">5 mile radius</div>
        </div>

        {/* Growth Rate */}
        <div className="text-center">
          <div className="flex items-center justify-center mb-2">
            <span className="text-2xl">📈</span>
          </div>
          <div className="text-2xl font-bold text-green-600">
            +{animatedValues.growthRate}%
          </div>
          <div className="text-sm text-gray-500">Growth</div>
          <div className="text-xs text-gray-400 mt-1">5-year trend</div>
        </div>

        {/* College Graduates */}
        <div className="text-center">
          <div className="flex items-center justify-center mb-2">
            <span className="text-2xl">🎓</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {animatedValues.collegeGrad}%
          </div>
          <div className="text-sm text-gray-500">College+</div>
          <div className="text-xs text-gray-400 mt-1">3 mile radius</div>
        </div>
      </div>

      {/* View Analysis Button */}
      <div className="px-6 pb-6">
        <button
          onClick={handleViewDetails}
          className="w-full py-3 px-4 bg-primary text-white font-medium rounded-lg hover:bg-blue-600 transition-colors duration-200 flex items-center justify-center gap-2 group"
        >
          <span>View Full Analysis</span>
          <svg 
            className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default DemographicsCard;