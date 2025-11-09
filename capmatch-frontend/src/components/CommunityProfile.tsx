import React from 'react';

interface CommunityProfileProps {
  attomData: any;
}

const CommunityProfile: React.FC<CommunityProfileProps> = ({ attomData }) => {
  if (!attomData?.formatted_data) {
    return null;
  }

  const { climate, air_quality, crime } = attomData.formatted_data;

  // Calculate overall safety score (inverse of crime index)
  const safetyScore = crime ? (100 - crime.crime_index) : 0;
  
  // Determine safety level
  const getSafetyLevel = (score: number) => {
    if (score >= 70) return { label: 'Very Safe', color: 'text-green-600', bg: 'bg-green-50', dot: 'bg-green-500' };
    if (score >= 50) return { label: 'Moderately Safe', color: 'text-yellow-600', bg: 'bg-yellow-50', dot: 'bg-yellow-500' };
    return { label: 'Needs Attention', color: 'text-red-600', bg: 'bg-red-50', dot: 'bg-red-500' };
  };

  const safetyLevel = getSafetyLevel(safetyScore);

  // Calculate AQI category
  const getAQICategory = (index: number) => {
    if (index <= 50) return { label: 'Good', color: 'text-green-600' };
    if (index <= 100) return { label: 'Moderate', color: 'text-yellow-600' };
    if (index <= 150) return { label: 'Unhealthy for Sensitive', color: 'text-orange-600' };
    return { label: 'Unhealthy', color: 'text-red-600' };
  };

  const aqiCategory = air_quality ? getAQICategory(air_quality.air_pollution_index) : { label: 'N/A', color: 'text-gray-600' };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Climate Card */}
      <div className="bg-white rounded-lg shadow-card p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">🌤️</span>
          <h3 className="text-lg font-semibold text-gray-900">Climate</h3>
        </div>

        {climate && (
          <>
            {/* Temperature Display */}
            <div className="mb-4">
              <div className="text-3xl font-bold text-gray-900">{Math.round(climate.avg_temp)}°F</div>
              <div className="text-sm text-gray-500">Average Temperature</div>
              
              {/* Temperature Range */}
              <div className="mt-3 flex items-center justify-between text-sm">
                <div className="flex items-center gap-1">
                  <span className="text-blue-500">❄️</span>
                  <span className="text-gray-600">Jan: {Math.round(climate.avg_temp_january)}°F</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-orange-500">☀️</span>
                  <span className="text-gray-600">Jul: {Math.round(climate.avg_temp_july)}°F</span>
                </div>
              </div>
            </div>

            {/* Weather Days */}
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Clear Days</span>
                  <span className="font-medium">{climate.clear_days}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${(climate.clear_days / 365) * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Rainy Days</span>
                  <span className="font-medium">{climate.rainy_days}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-700 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${(climate.rainy_days / 365) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Precipitation */}
            <div className="mt-4 pt-4 border-t border-gray-100 flex justify-around text-center">
              <div>
                <div className="text-sm text-gray-500">Annual Rainfall</div>
                <div className="font-semibold">{climate.annual_rainfall_inches}"</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Annual Snow</div>
                <div className="font-semibold flex items-center justify-center gap-1">
                  <span>❄️</span> {climate.annual_snowfall_inches}"
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Air Quality Card */}
      <div className="bg-white rounded-lg shadow-card p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">🌬️</span>
          <h3 className="text-lg font-semibold text-gray-900">Air Quality</h3>
        </div>

        {air_quality && (
          <>
            {/* Overall AQI */}
            <div className="mb-4">
              <div className="text-3xl font-bold text-gray-900">{air_quality.air_pollution_index}</div>
              <div className={`text-sm font-medium ${aqiCategory.color}`}>{aqiCategory.label}</div>
              <div className="text-xs text-gray-500 mt-1">Air Quality Index</div>
            </div>

            {/* Pollutant Indicators */}
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                {/* Ozone */}
                <div className="text-center">
                  <div className="relative inline-flex items-center justify-center">
                    <svg className="w-16 h-16 transform -rotate-90">
                      <circle
                        cx="32"
                        cy="32"
                        r="28"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                        className="text-gray-200"
                      />
                      <circle
                        cx="32"
                        cy="32"
                        r="28"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                        strokeDasharray={`${(air_quality.ozone_index / 100) * 176} 176`}
                        className={air_quality.ozone_index <= 100 ? "text-green-500" : "text-yellow-500"}
                      />
                    </svg>
                    <span className="absolute text-sm font-semibold">{air_quality.ozone_index}</span>
                  </div>
                  <div className="text-xs text-gray-600 mt-1">Ozone</div>
                </div>

                {/* Particulate */}
                <div className="text-center">
                  <div className="relative inline-flex items-center justify-center">
                    <svg className="w-16 h-16 transform -rotate-90">
                      <circle
                        cx="32"
                        cy="32"
                        r="28"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                        className="text-gray-200"
                      />
                      <circle
                        cx="32"
                        cy="32"
                        r="28"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                        strokeDasharray={`${(air_quality.particulate_index / 100) * 176} 176`}
                        className={air_quality.particulate_index <= 100 ? "text-green-500" : "text-yellow-500"}
                      />
                    </svg>
                    <span className="absolute text-sm font-semibold">{air_quality.particulate_index}</span>
                  </div>
                  <div className="text-xs text-gray-600 mt-1">PM2.5</div>
                </div>

                {/* Carbon Monoxide */}
                <div className="text-center">
                  <div className="relative inline-flex items-center justify-center">
                    <svg className="w-16 h-16 transform -rotate-90">
                      <circle
                        cx="32"
                        cy="32"
                        r="28"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                        className="text-gray-200"
                      />
                      <circle
                        cx="32"
                        cy="32"
                        r="28"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                        strokeDasharray={`${(air_quality.carbon_monoxide_index / 100) * 176} 176`}
                        className={air_quality.carbon_monoxide_index <= 100 ? "text-green-500" : "text-yellow-500"}
                      />
                    </svg>
                    <span className="absolute text-sm font-semibold">{air_quality.carbon_monoxide_index}</span>
                  </div>
                  <div className="text-xs text-gray-600 mt-1">CO</div>
                </div>
              </div>
            </div>

            {/* Legend */}
            <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-center gap-4 text-xs">
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-gray-600">Good (≤100)</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span className="text-gray-600">Moderate (&gt;100)</span>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Safety Card */}
      <div className="bg-white rounded-lg shadow-card p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">🛡️</span>
          <h3 className="text-lg font-semibold text-gray-900">Safety</h3>
        </div>

        {crime && (
          <>
            {/* Crime Index Header */}
            <div className="mb-4">
              <div className="text-sm font-medium text-gray-600">Crime Index by Type</div>
              <div className="text-xs text-gray-500 mt-1">Compared to US Average (100)</div>
            </div>

            {/* Crime Categories with Visual Bars */}
            <div className="space-y-3">
              {[
                { label: 'Overall', value: crime.crime_index, icon: '📊', color: 'blue' },
                { label: 'Violent Crime', value: crime.murder_index, icon: '⚠️', color: 'orange' },
                { label: 'Robbery', value: crime.robbery_index, icon: '💰', color: 'yellow' },
                { label: 'Assault', value: crime.assault_index, icon: '👊', color: 'purple' },
                { label: 'Burglary', value: crime.burglary_index, icon: '🏠', color: 'indigo' },
                { label: 'Theft', value: crime.theft_index, icon: '🚗', color: 'pink' }
              ].map((item, index) => (
                <div key={index}>
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2 text-sm">
                      <span>{item.icon}</span>
                      <span className="text-gray-700">{item.label}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className={`font-semibold text-sm ${item.value < 100 ? 'text-green-600' : 'text-red-600'}`}>
                        {item.value}
                      </span>
                      <span className={`text-xs ${item.value < 100 ? 'text-green-500' : 'text-red-500'}`}>
                        {item.value < 100 ? '↓' : '↑'}
                      </span>
                    </div>
                  </div>
                  {/* Progress Bar */}
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div 
                      className={`h-1.5 rounded-full transition-all duration-500 ${
                        item.value < 50 ? 'bg-green-500' : 
                        item.value < 100 ? 'bg-yellow-500' : 
                        item.value < 150 ? 'bg-orange-500' : 
                        'bg-red-500'
                      }`}
                      style={{ width: `${Math.min((item.value / 200) * 100, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Reference Lines */}
            <div className="mt-4 pt-3 border-t border-gray-100">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>0 (Safest)</span>
                <span>100 (US Avg)</span>
                <span>200+</span>
              </div>
            </div>

            <div className="mt-3 text-xs text-gray-500 text-center">
              Lower numbers = Safer community
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default CommunityProfile;