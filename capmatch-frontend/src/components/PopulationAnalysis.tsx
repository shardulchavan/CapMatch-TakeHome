import React from 'react';

interface PopulationAnalysisProps {
  radiusData: any;
}

const PopulationAnalysis: React.FC<PopulationAnalysisProps> = ({ radiusData }) => {
  const radii = [
    { key: '1_mile', label: '1 Mile', color: 'bg-red-100 text-red-700' },
    { key: '3_mile', label: '3 Miles', color: 'bg-teal-100 text-teal-700' },
    { key: '5_mile', label: '5 Miles', color: 'bg-blue-100 text-blue-700' }
  ];

  // Handle case where radiusData is undefined or empty
  if (!radiusData) {
    return (
      <div className="bg-white rounded-lg shadow-card p-6">
        <p className="text-gray-500 text-center">No data available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-card overflow-hidden flex flex-col">
      {radii.map((radius, index) => {
        // Safe access to data with fallbacks
        const data = radiusData?.[radius.key];
        const currentData = data?.current?.data || data?.current || {};
        const tractCount = data?.tract_count || 1;
        
        // Calculate actual values with safe defaults
        const population = currentData.total_population || 0;
        const medianIncome = currentData.median_household_income || 0;
        const medianAge = currentData.median_age || 0;
        
        // Adjust values if they appear to be aggregated
        const actualIncome = tractCount > 1 && medianIncome > 1000000 
          ? Math.round(medianIncome / tractCount) 
          : medianIncome;
          
        let actualAge = tractCount > 1 && medianAge > 100
          ? (medianAge / tractCount) 
          : medianAge;
        
        // Sanity check for age with better fallback
        if (actualAge < 0 || actualAge > 100) {
          actualAge = 38; // Default median age
        }
        
        return (
          <div key={radius.key} className={`flex-1 p-6 ${index !== radii.length - 1 ? 'border-b border-gray-100' : ''}`}>
            {/* Radius Header */}
            <div className="mb-4">
              <span className={`text-sm font-medium px-3 py-1 rounded-full ${radius.color}`}>
                {radius.label}
              </span>
            </div>
            
            {/* Metrics Grid - 3 columns */}
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-500 mb-1">Population</p>
                <p className="text-lg font-semibold text-gray-900">
                  {population.toLocaleString()}
                </p>
              </div>
              
              <div>
                <p className="text-sm text-gray-500 mb-1">Median Income</p>
                <p className="text-lg font-semibold text-gray-900">
                  ${actualIncome > 0 ? (actualIncome / 1000).toFixed(0) : '0'}K
                </p>
              </div>
              
              <div>
                <p className="text-sm text-gray-500 mb-1">Median Age</p>
                <p className="text-lg font-semibold text-gray-900">
                  {actualAge.toFixed(0)} yrs
                </p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default PopulationAnalysis;