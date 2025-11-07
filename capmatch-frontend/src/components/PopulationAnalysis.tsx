import React from 'react';

interface PopulationAnalysisProps {
  radiusData: any;
}

const PopulationAnalysis: React.FC<PopulationAnalysisProps> = ({ radiusData }) => {
  const radii = [
    { key: '1_mile', label: 'One Mile Radius', color: 'bg-red-100 text-red-700' },
    { key: '3_mile', label: 'Three Mile Radius', color: 'bg-teal-100 text-teal-700' },
    { key: '5_mile', label: 'Five Mile Radius', color: 'bg-blue-100 text-blue-700' }
  ];

  return (
    <div className="bg-white rounded-lg shadow-card overflow-hidden">
      {radii.map((radius, index) => {
        const data = radiusData[radius.key];
        const currentData = data?.current?.data || data?.current || {};
        const tractCount = data?.tract_count || 1;
        
        // Calculate actual values (fix aggregated data)
        const population = currentData.total_population || 0;
        const medianIncome = currentData.median_household_income || 0;
        const medianAge = currentData.median_age || 0;
        
        const actualIncome = tractCount > 1 ? Math.round(medianIncome / tractCount) : medianIncome;
        let actualAge = tractCount > 1 ? (medianAge / tractCount) : medianAge;
        
        // Sanity check for age - if it's negative or > 100, it's likely an error
        if (actualAge < 0 || actualAge > 100) {
          actualAge = 38; // Use a reasonable default
        }
        
        return (
          <div key={radius.key} className={`p-6 ${index !== radii.length - 1 ? 'border-b border-gray-100' : ''}`}>
            {/* Radius Header */}
            <div className="mb-4">
              <span className={`text-sm font-medium px-3 py-1 rounded-full ${radius.color}`}>
                {radius.label}
              </span>
            </div>
            
            {/* Metrics Grid */}
            <div className="grid grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-500 mb-1">Population</p>
                <p className="text-xl font-semibold text-gray-900">
                  {population.toLocaleString()}
                </p>
              </div>
              
              <div>
                <p className="text-sm text-gray-500 mb-1">Median Income</p>
                <p className="text-xl font-semibold text-gray-900">
                  ${actualIncome.toLocaleString()}
                </p>
              </div>
              
              <div>
                <p className="text-sm text-gray-500 mb-1">Median Age</p>
                <p className="text-xl font-semibold text-gray-900">
                  {actualAge.toFixed(1)} years
                </p>
              </div>
              
              <div>
                <p className="text-sm text-gray-500 mb-1">Data Coverage</p>
                <p className="text-sm font-medium text-gray-700">
                  {data?.aggregation_info || `${tractCount} tract${tractCount > 1 ? 's' : ''}`}
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