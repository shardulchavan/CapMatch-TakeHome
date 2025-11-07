import React, { useEffect, useState } from 'react';

interface MapCircle {
  type: string;
  properties: {
    radius_miles: number;
    population: number;
    population_formatted: string;
    color: string;
  };
  geometry: {
    coordinates: number[][][];
  };
}

interface MiniMapProps {
  circles: MapCircle[];
  center: [number, number];
}

const MiniMap: React.FC<MiniMapProps> = ({ circles, center }) => {
  const [hoveredRadius, setHoveredRadius] = useState<number | null>(null);
  const [animationComplete, setAnimationComplete] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setAnimationComplete(true), 500);
    return () => clearTimeout(timer);
  }, []);

  // Simple SVG-based map for lightweight rendering
  const mapWidth = 300;
  const mapHeight = 200;
  const centerX = mapWidth / 2;
  const centerY = mapHeight / 2;

  // Calculate scale based on largest radius
//   const maxRadius = 5; // 5 miles
  const scale = 60; // pixels per mile

  return (
    <div className="relative w-full h-48 bg-gray-50 rounded-lg overflow-hidden">
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${mapWidth} ${mapHeight}`}
        className="absolute inset-0"
      >
        {/* Grid pattern for map background */}
        <defs>
          <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#E5E7EB" strokeWidth="0.5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />

        {/* Radius circles */}
        {circles.map((circle, index) => {
          const radius = circle.properties.radius_miles * scale;
          const isHovered = hoveredRadius === circle.properties.radius_miles;
          
          return (
            <g key={index}>
              <circle
                cx={centerX}
                cy={centerY}
                r={animationComplete ? radius : 0}
                fill={circle.properties.color}
                fillOpacity={isHovered ? 0.25 : 0.15}
                stroke={circle.properties.color}
                strokeWidth="1.5"
                strokeOpacity={0.8}
                onMouseEnter={() => setHoveredRadius(circle.properties.radius_miles)}
                onMouseLeave={() => setHoveredRadius(null)}
                className="cursor-pointer transition-all duration-300"
                style={{
                  transition: 'r 0.5s ease-out, fill-opacity 0.2s ease'
                }}
              />
              
              {/* Show population on hover */}
              {isHovered && (
                <text
                  x={centerX}
                  y={centerY - radius - 10}
                  textAnchor="middle"
                  className="text-sm font-medium fill-gray-700"
                >
                  {circle.properties.population_formatted}
                </text>
              )}
            </g>
          );
        })}

        {/* Center marker */}
        <circle
          cx={centerX}
          cy={centerY}
          r="4"
          fill="#1F2937"
          className="animate-pulse"
        />
        <circle
          cx={centerX}
          cy={centerY}
          r="2"
          fill="white"
        />

        {/* Radius labels */}
        {animationComplete && circles.map((circle, index) => {
          const radius = circle.properties.radius_miles * scale;
          return (
            <text
              key={`label-${index}`}
              x={centerX + radius + 5}
              y={centerY}
              className="text-xs fill-gray-500"
              alignmentBaseline="middle"
            >
              {circle.properties.radius_miles}mi
            </text>
          );
        })}
      </svg>
    </div>
  );
};

export default MiniMap;