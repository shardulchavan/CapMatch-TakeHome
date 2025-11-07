import React from 'react';

interface GrowthTrendsProps {
  growthMetrics: any;
}

const GrowthTrends: React.FC<GrowthTrendsProps> = ({ growthMetrics }) => {
  const metrics = [
    {
      label: 'Population Growth',
      value: growthMetrics.population_growth,
      icon: '📊',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      description: '5-year increase'
    },
    {
      label: 'Income Growth',
      value: growthMetrics.income_growth,
      icon: '💰',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      description: '5-year increase'
    },
    {
      label: 'Job Growth',
      value: growthMetrics.job_growth,
      icon: '💼',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      description: '5-year increase'
    }
  ];

  return (
    <div className="grid md:grid-cols-3 gap-6">
      {metrics.map((metric, index) => (
        <div key={index} className="bg-white rounded-lg shadow-card p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">{metric.icon}</span>
                <h3 className="font-medium text-gray-700">{metric.label}</h3>
              </div>
              
              <div className={`text-3xl font-bold ${metric.value > 0 ? metric.color : 'text-red-600'} mb-1`}>
                {metric.value > 0 ? '+' : ''}{metric.value?.toFixed(1) || '0.0'}%
              </div>
              
              <p className="text-sm text-gray-500">{metric.description}</p>
            </div>
            
            {/* Visual indicator */}
            <div className={`w-12 h-12 rounded-full ${metric.bgColor} flex items-center justify-center`}>
              {metric.value > 0 ? (
                <svg className={`w-6 h-6 ${metric.color}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              ) : (
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                </svg>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default GrowthTrends;