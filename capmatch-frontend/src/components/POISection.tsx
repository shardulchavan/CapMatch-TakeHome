// src/components/POISection.tsx

import React from 'react';

interface POILocation {
  name: string;
  address: string;
  full_address: string;
  distance_miles: number;
  phone: string;
  category: string;
  line_of_business: string;
  industry: string;
}

interface POIData {
  poi_count: number;
  summary?: {
    personal_services_count: number;
    healthcare_count: number;
    education_count: number;
    banks_count: number;
    closest_poi?: {
      name: string;
      distance_miles: number;
      address: string;
      category: string;
    };
  };
  pois_by_category: {
    'PERSONAL SERVICES': POILocation[];
    'HEALTH CARE SERVICES': POILocation[];
    'EDUCATION': POILocation[];
    'BANKS – FINANCIAL': POILocation[];
  };
  errors?: string[];
}

interface POISectionProps {
  poiData: POIData | null;
}

const POISection: React.FC<POISectionProps> = ({ poiData }) => {
  if (!poiData) {
    return (
      <div className="bg-white rounded-lg shadow-card p-8 text-center">
        <p className="text-gray-500">No nearby services data available</p>
      </div>
    );
  }

  if (poiData.errors && poiData.errors.length > 0) {
    return (
      <div className="bg-white rounded-lg shadow-card p-8 text-center">
        <p className="text-gray-500">Unable to load nearby services</p>
      </div>
    );
  }

  const categories = [
    {
      key: 'PERSONAL SERVICES',
      title: 'Personal Services',
      emoji: '✂️',
      color: 'purple',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
      borderColor: 'border-purple-200',
      count: poiData.summary?.personal_services_count || 0
    },
    {
      key: 'HEALTH CARE SERVICES',
      title: 'Healthcare',
      emoji: '❤️',
      color: 'red',
      bgColor: 'bg-red-50',
      iconColor: 'text-red-600',
      borderColor: 'border-red-200',
      count: poiData.summary?.healthcare_count || 0
    },
    {
      key: 'EDUCATION',
      title: 'Education',
      emoji: '🎓',
      color: 'blue',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
      borderColor: 'border-blue-200',
      count: poiData.summary?.education_count || 0
    },
    {
      key: 'BANKS – FINANCIAL',
      title: 'Financial Services',
      emoji: '💰',
      color: 'green',
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600',
      borderColor: 'border-green-200',
      count: poiData.summary?.banks_count || 0
    }
  ];

  const getGoogleMapsUrl = (address: string) => {
    return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
  };

  const formatDistance = (miles: number) => {
    if (miles < 0.1) {
      return `${(miles * 5280).toFixed(0)} ft`;
    }
    return `${miles.toFixed(1)} mi`;
  };

  const formatPhone = (phone: string) => {
    if (!phone || phone === 'N/A') return null;
    return phone;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {categories.map((category) => {
        const locations = poiData.pois_by_category[category.key as keyof typeof poiData.pois_by_category] || [];
        const topLocations = locations.slice(0, 5); // Show top 5 locations

        return (
          <div
            key={category.key}
            className={`bg-white rounded-lg shadow-card p-6 border ${category.borderColor}`}
          >
            {/* Category Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${category.bgColor} flex items-center justify-center`}>
                  <span className="text-2xl">{category.emoji}</span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{category.title}</h3>
                  <p className="text-sm text-gray-500">{category.count} locations found</p>
                </div>
              </div>
            </div>

            {/* Locations List */}
            {topLocations.length > 0 ? (
              <div className="space-y-3">
                {topLocations.map((location, index) => (
                  <div
                    key={index}
                    className="border-l-2 border-gray-200 pl-4 hover:border-gray-400 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 text-sm">
                          {location.name}
                        </h4>
                        <p className="text-xs text-gray-600 mt-1">
                          {location.industry}
                        </p>
                        <div className="flex items-center space-x-3 mt-2">
                          <span className={`inline-flex items-center text-xs ${category.iconColor} font-medium`}>
                            <span className="mr-1">📍</span>
                            {formatDistance(location.distance_miles)}
                          </span>
                          {formatPhone(location.phone) && (
                            <span className="text-xs text-gray-500">
                              {formatPhone(location.phone)}
                            </span>
                          )}
                        </div>
                      </div>
                      <a
                        href={getGoogleMapsUrl(location.full_address)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-2 p-1 hover:bg-gray-100 rounded transition-colors"
                        title="View on Google Maps"
                      >
                        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                            d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full ${category.bgColor} mb-3`}>
                  <span className="text-3xl opacity-50">{category.emoji}</span>
                </div>
                <p className="text-gray-500 text-sm">No {category.title.toLowerCase()} found within 5 miles</p>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default POISection;