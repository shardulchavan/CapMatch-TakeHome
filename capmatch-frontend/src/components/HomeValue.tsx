import React from 'react';

interface HomeValueGrowthChartProps {
  radiusData: any;
}

const HomeValueGrowthChart: React.FC<HomeValueGrowthChartProps> = ({ radiusData }) => {
  // Handle missing data
  if (!radiusData) {
    return (
      <div className="bg-white rounded-lg shadow-card p-6">
        <p className="text-gray-500 text-center">No data available</p>
      </div>
    );
  }

  // Extract and calculate data
  const years = ['2017', '2018', '2019', '2020', '2021', '2022'];
  
  // Calculate home values for each radius with safe access
  const getChartData = () => {
    const radii = ['1_mile', '3_mile', '5_mile'] as const;
    const colors: Record<string, string> = {
      '1_mile': '#ef4444',
      '3_mile': '#22c55e', 
      '5_mile': '#3b82f6'
    };
    
    return radii.map(radius => {
      // Safe data access with fallbacks
      const radiusInfo = radiusData?.[radius] || {};
      const current = radiusInfo?.current?.median_home_value || 0;
      const historical = radiusInfo?.historical?.median_home_value || 0;
      const tractCount = radiusInfo?.tract_count || 1;
      
      // Debug log to see actual values
      console.log(`${radius} - Current: ${current}, Historical: ${historical}, Tracts: ${tractCount}`);
      
      // Use the median values directly (backend already handles medians correctly)
      const adjustedCurrent = current;
      const adjustedHistorical = historical;
      
      // Generate interpolated values
      const values = years.map((year, index) => {
        if (adjustedHistorical === 0 || adjustedCurrent === 0) {
          return 0;
        }
        const progress = index / (years.length - 1);
        return adjustedHistorical + (adjustedCurrent - adjustedHistorical) * progress;
      });
      
      // Calculate growth percentage safely
      let growthPercent = '0.0';
      if (adjustedHistorical > 0 && adjustedCurrent > 0) {
        growthPercent = ((adjustedCurrent - adjustedHistorical) / adjustedHistorical * 100).toFixed(1);
      }
      
      return {
        radius,
        label: radius.replace('_', ' ').replace('mile', 'Mile'),
        color: colors[radius],
        values,
        growthPercent
      };
    });
  };
  
  const chartData = getChartData();
  
  // Check if we have valid data to display
  const hasValidData = chartData.some(d => d.values.some(v => v > 0));
  
  if (!hasValidData) {
    return (
      <div className="bg-white rounded-lg shadow-card p-6">
        <p className="text-gray-500 text-center">Insufficient data for visualization</p>
      </div>
    );
  }
  
  // SVG dimensions
  const width = 600;
  const height = 300;
  const padding = { top: 20, right: 80, bottom: 50, left: 80 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  
  // Calculate scales with better range for visualization
  const validValues = chartData.flatMap(d => d.values).filter(v => v > 0);
  const minValue = validValues.length > 0 ? Math.min(...validValues) * 0.95 : 0;
  const maxValue = validValues.length > 0 ? Math.max(...validValues) * 1.05 : 1000000;
  
  const xScale = (index: number) => (index / (years.length - 1)) * chartWidth + padding.left;
  const yScale = (value: number) => {
    if (maxValue === minValue) return height / 2;
    const normalized = (value - minValue) / (maxValue - minValue);
    return height - padding.bottom - normalized * chartHeight;
  };
  
  // Generate path strings for lines
  const generatePath = (values: number[]) => {
    return values.map((value, index) => {
      const x = xScale(index);
      const y = yScale(value);
      return index === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
    }).join(' ');
  };
  
  // Calculate overall growth safely
  const fiveMileData = radiusData?.['5_mile'];
  let homeValueGrowth = 0;
  if (fiveMileData?.current?.median_home_value && fiveMileData?.historical?.median_home_value) {
    const adjustedCurrent = fiveMileData.current.median_home_value;
    const adjustedHistorical = fiveMileData.historical.median_home_value;
    homeValueGrowth = ((adjustedCurrent / adjustedHistorical) - 1) * 100;
  }

  // Format Y-axis value based on scale
  const formatYValue = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `$${Math.round(value / 1000)}K`;
    } else {
      return `$${Math.round(value)}`;
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow-card p-6">
      <div className="mb-4 flex justify-between items-start">
        <div>
          <p className="text-sm text-gray-500">5-Year Growth</p>
          <p className="text-2xl font-semibold text-gray-900">
            Home: {homeValueGrowth > 0 ? '+' : ''}{homeValueGrowth.toFixed(1)}%
          </p>
        </div>
      </div>
      
      <div className="relative">
        <svg 
          viewBox={`0 0 ${width} ${height}`} 
          className="w-full h-auto"
          style={{ maxHeight: '300px' }}
        >
          {/* Grid lines - more granular */}
          {[0, 0.2, 0.4, 0.6, 0.8, 1].map(ratio => {
            const y = padding.top + chartHeight * (1 - ratio);
            const value = minValue + (maxValue - minValue) * ratio;
            return (
              <g key={ratio}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="#e5e7eb"
                  strokeDasharray={ratio === 0 || ratio === 1 ? "0" : "2,2"}
                />
                <text
                  x={padding.left - 10}
                  y={y + 5}
                  textAnchor="end"
                  className="text-xs fill-gray-500"
                >
                  {formatYValue(value)}
                </text>
              </g>
            );
          })}
          
          {/* X-axis labels */}
          {years.map((year, index) => (
            <text
              key={year}
              x={xScale(index)}
              y={height - padding.bottom + 20}
              textAnchor="middle"
              className="text-xs fill-gray-600"
            >
              {year}
            </text>
          ))}
          
          {/* Chart lines - only render if values exist */}
          {chartData.filter(data => data.values.some(v => v > 0)).map((data, index) => (
            <g key={data.radius}>
              {/* Line */}
              <path
                d={generatePath(data.values)}
                fill="none"
                stroke={data.color}
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              
              {/* Data points */}
              {data.values.map((value, pointIndex) => (
                value > 0 && (
                  <circle
                    key={pointIndex}
                    cx={xScale(pointIndex)}
                    cy={yScale(value)}
                    r="4"
                    fill={data.color}
                    stroke="white"
                    strokeWidth="2"
                  />
                )
              ))}
              
              {/* Label at end of line */}
              {data.values[data.values.length - 1] > 0 && (
                <text
                  x={xScale(years.length - 1) + 10}
                  y={yScale(data.values[data.values.length - 1]) + 5}
                  className="text-xs fill-gray-700 font-medium"
                >
                  {data.label}
                </text>
              )}
            </g>
          ))}
          
          {/* Y-axis label */}
          <text
            x={padding.left / 2}
            y={height / 2}
            transform={`rotate(-90, ${padding.left / 2}, ${height / 2})`}
            textAnchor="middle"
            className="text-xs fill-gray-600"
          >
            Home Value
          </text>
        </svg>
      </div>
      
      {/* Legend */}
      <div className="mt-4 flex justify-center gap-6 text-xs">
        {chartData.filter(data => parseFloat(data.growthPercent) !== 0).map(data => (
          <div key={data.radius} className="flex items-center gap-2">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: data.color }}
            />
            <span className="text-gray-600">
              {data.label}: {parseFloat(data.growthPercent) > 0 ? '+' : ''}{data.growthPercent}%
            </span>
          </div>
        ))}
      </div>
      
      <div className="mt-4 text-center text-xs text-gray-500">
        Home values tracked from 2017-2022
      </div>
    </div>
  );
};

export default HomeValueGrowthChart;