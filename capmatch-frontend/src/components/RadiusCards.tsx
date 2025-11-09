import React from 'react';

interface RadiusCardsProps {
  radiusData: any;
}

const RadiusCards: React.FC<RadiusCardsProps> = ({ radiusData }) => {
  const radii = ['1_mile', '3_mile', '5_mile'] as const;
  const radiusConfig: Record<typeof radii[number], { label: string; icon: string; color: string; bgColor: string }> = {
    '1_mile': { label: '1 Mile Radius', icon: '🎯', color: 'text-red-600', bgColor: 'bg-red-50' },
    '3_mile': { label: '3 Mile Radius', icon: '🔵', color: 'text-teal-600', bgColor: 'bg-teal-50' },
    '5_mile': { label: '5 Mile Radius', icon: '🌐', color: 'text-blue-600', bgColor: 'bg-blue-50' }
  };

  return (
    <div className="grid md:grid-cols-3 gap-6">
      {radii.map((radius) => {
        const config = radiusConfig[radius];
        const data = radiusData[radius];
        const currentData = data?.current?.data || data?.current || {};
        
        // Get population and income, handling aggregated values
        const population = currentData.total_population || 0;
        const medianIncome = currentData.median_household_income || 0;
        const tractCount = data?.tract_count || 1;
        
        // Fix aggregated values
        // const actualIncome = tractCount > 1 ? Math.round(medianIncome / tractCount) : medianIncome;
        
        return (
          <div key={radius} className="bg-white rounded-lg shadow-card p-6 hover:shadow-card-hover transition-shadow">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{config.icon}</span>
                <h3 className="font-semibold text-gray-900">{config.label}</h3>
              </div>
            </div>
            
            {/* Population */}
            <div className="mb-6">
              <p className="text-3xl font-bold text-gray-900">
                {population.toLocaleString()}
              </p>
              <p className="text-sm text-gray-500">Population</p>
            </div>
            
            {/* Additional Metrics */}
            <div className="space-y-3 pt-4 border-t border-gray-100">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Median Income</span>
                <span className="text-sm font-medium text-gray-900">
                  {/* ${actualIncome.toLocaleString()} */}
                  ${Math.round(medianIncome).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default RadiusCards;