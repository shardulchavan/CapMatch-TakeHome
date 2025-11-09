// src/components/MarketMetricsDashboard.tsx

// import React from 'react';

// interface MarketMetricsDashboardProps {
//   radiusData: any;
// }

// const MarketMetricsDashboard: React.FC<MarketMetricsDashboardProps> = ({ radiusData }) => {
//   // Handle missing data
//   if (!radiusData) {
//     return (
//       <div className="bg-white rounded-lg shadow-card p-6">
//         <p className="text-gray-500 text-center">No data available</p>
//       </div>
//     );
//   }

//   // Extract 3-mile radius data (primary focus)
//   const threeMileData = radiusData?.['3_mile'];
//   const currentData = threeMileData?.current?.data || threeMileData?.current || {};
//   const historicalData = threeMileData?.historical?.data || threeMileData?.historical || {};
//   const tractCount = threeMileData?.tract_count || 1;
  
//   // Calculate actual values (adjust for aggregation)
//   const medianIncome = currentData.median_household_income || 0;
//   const medianHomeValue = currentData.median_home_value || 0;
//   const medianAge = currentData.median_age || 0;
  
//   // Debug logging
//   console.log('3-mile data:', { medianIncome, medianHomeValue, tractCount });
  
//   // Adjust values - both income and home values appear to be aggregated
//   const actualIncome = tractCount > 1 ? Math.round(medianIncome / tractCount) : medianIncome;
//   const actualHomeValue = tractCount > 1 ? Math.round(medianHomeValue / tractCount) : medianHomeValue;
    
//   let actualAge = tractCount > 1 && medianAge > 100
//     ? Math.round(medianAge / tractCount)
//     : medianAge;
    
//   if (actualAge < 0 || actualAge > 100) {
//     actualAge = 38;
//   }
  
//   // Calculate Affordability Index (price to income ratio - standard method)
//   const affordabilityRatio = actualIncome > 0 
//     ? (actualHomeValue / actualIncome) 
//     : 0;
  
//   // Get employment data for 3-mile radius (same as other metrics)
//   const employmentData = currentData;
//   const historicalEmployment = historicalData;
  
//   const laborForce = employmentData.labor_force || 0;
//   const employed = employmentData.employed || 0;
//   const historicalEmployed = historicalEmployment.employed || 0;
//   const jobsAdded = employed - historicalEmployed;
  
//   // Determine affordability status using standard interpretation
//   const getAffordabilityStatus = (ratio: number) => {
//     if (ratio <= 3) return { status: 'Affordable', color: 'text-green-600', bgColor: 'bg-green-100' };
//     if (ratio <= 5) return { status: 'Moderately Unaffordable', color: 'text-yellow-600', bgColor: 'bg-yellow-100' };
//     return { status: 'Severely Unaffordable', color: 'text-red-600', bgColor: 'bg-red-100' };
//   };
  
//   const affordabilityInfo = getAffordabilityStatus(affordabilityRatio);
  
//   return (
//     <div className="bg-white rounded-lg shadow-card overflow-hidden">
//       {/* 3-Mile Radius Header */}
//       <div className="px-6 py-4 bg-teal-50 border-b border-teal-100">
//         <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
//           <span className="text-sm font-medium px-3 py-1 rounded-full bg-teal-100 text-teal-700">
//             3 Miles
//           </span>
//           Primary Market Analysis
//         </h3>
//       </div>
      
//       {/* Three Column Layout */}
//       <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-gray-100">
        
//         {/* Median Age */}
//         <div className="p-6">
//           <div className="flex items-center gap-2 mb-3">
//             <span className="text-2xl">👥</span>
//             <p className="text-sm font-medium text-gray-600">Demographics</p>
//           </div>
//           <p className="text-3xl font-bold text-gray-900">{actualAge} yrs</p>
//           <p className="text-sm text-gray-500 mt-1">Median Age</p>
//           <div className="mt-4 space-y-2">
//             <div className="flex justify-between text-xs">
//               <span className="text-gray-500">Income</span>
//               <span className="font-medium text-gray-900">${(actualIncome / 1000).toFixed(0)}K</span>
//             </div>
//             <div className="flex justify-between text-xs">
//               <span className="text-gray-500">Population</span>
//               <span className="font-medium text-gray-900">{(currentData.total_population || 0).toLocaleString()}</span>
//             </div>
//           </div>
//         </div>
        
//         {/* Affordability Index */}
//         <div className="p-6">
//           <div className="flex items-center gap-2 mb-3">
//             <span className="text-2xl">🏠</span>
//             <p className="text-sm font-medium text-gray-600">Affordability Index</p>
//           </div>
          
//           {/* Ratio Display */}
//           <div className="mb-3">
//             <p className="text-3xl font-bold text-gray-900">{affordabilityRatio.toFixed(1)}</p>
//             <p className="text-sm text-gray-500">House Price to Income Ratio</p>
//           </div>
          
//           {/* Visual Gauge */}
//           <div className="mb-3">
//             <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
//               <div 
//                 className="h-2.5 transition-all duration-500"
//                 style={{ 
//                   width: `${Math.min((affordabilityRatio / 10) * 100, 100)}%`,
//                   background: affordabilityRatio <= 3 ? '#10b981' : affordabilityRatio <= 5 ? '#f59e0b' : '#ef4444'
//                 }}
//               />
//             </div>
//             <div className="flex justify-between text-xs text-gray-500 mt-1">
//               <span>0</span>
//               <span>3</span>
//               <span>5</span>
//               <span>10+</span>
//             </div>
//           </div>
          
//           {/* Status Badge */}
//           <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${affordabilityInfo.bgColor} ${affordabilityInfo.color}`}>
//             {affordabilityInfo.status} Market
//           </span>
//         </div>
        
//         {/* Employment Stats */}
//         <div className="p-6">
//           <div className="flex items-center gap-2 mb-3">
//             <span className="text-2xl">💼</span>
//             <p className="text-sm font-medium text-gray-600">Employment Stats</p>
//           </div>
          
//           <div className="space-y-3">
//             <div>
//               <p className="text-2xl font-bold text-gray-900">{laborForce.toLocaleString()}</p>
//               <p className="text-sm text-gray-500">Labor Force</p>
//             </div>
            
//             <div className="grid grid-cols-2 gap-3">
//               <div className="bg-gray-50 rounded-lg p-3">
//                 <p className="text-lg font-semibold text-gray-900">{employed.toLocaleString()}</p>
//                 <p className="text-xs text-gray-500">Employed</p>
//               </div>
              
//               <div className="bg-green-50 rounded-lg p-3">
//                 <p className="text-lg font-semibold text-green-600">
//                   +{jobsAdded > 0 ? jobsAdded.toLocaleString() : '0'}
//                 </p>
//                 <p className="text-xs text-gray-500">Jobs Added (5yr)</p>
//               </div>
//             </div>
            
//             <div className="text-xs text-gray-500 pt-1">
//               <span className="font-medium">Employment Rate:</span> {laborForce > 0 ? ((employed / laborForce) * 100).toFixed(1) : '0'}%
//             </div>
//           </div>
//         </div>
        
//       </div>
      
//       {/* Footer Note */}
//       <div className="px-6 py-3 bg-gray-50 text-xs text-gray-500 text-center">
//         Data from US Census ACS 5-Year Estimates • All metrics shown for 3-mile radius
//       </div>
//     </div>
//   );
// };

// export default MarketMetricsDashboard;


import React from 'react';

interface MarketMetricsDashboardProps {
  radiusData: any;
  attomData?: any;
}

const MarketMetricsDashboard: React.FC<MarketMetricsDashboardProps> = ({ radiusData, attomData }) => {
  // Handle missing data
  if (!radiusData) {
    return (
      <div className="bg-white rounded-lg shadow-card p-6">
        <p className="text-gray-500 text-center">No data available</p>
      </div>
    );
  }

  // Extract 3-mile radius data (primary focus)
  const threeMileData = radiusData?.['3_mile'];
  const currentData = threeMileData?.current?.data || threeMileData?.current || {};
  const historicalData = threeMileData?.historical?.data || threeMileData?.historical || {};
  const tractCount = threeMileData?.tract_count || 1;
  
  // Calculate actual values (adjust for aggregation)
  const medianIncome = currentData.median_household_income || 0;
  const medianHomeValue = currentData.median_home_value || 0;
  const medianAge = currentData.median_age || 0;
  
  // Debug logging
  console.log('3-mile data:', { medianIncome, medianHomeValue, tractCount });
  
  // Adjust values - both income and home values appear to be aggregated
  const actualIncome = tractCount > 1 ? Math.round(medianIncome / tractCount) : medianIncome;
  const actualHomeValue = tractCount > 1 ? Math.round(medianHomeValue / tractCount) : medianHomeValue;
    
  let actualAge = tractCount > 1 && medianAge > 100
    ? Math.round(medianAge / tractCount)
    : medianAge;
    
  if (actualAge < 0 || actualAge > 100) {
    actualAge = 38;
  }
  
  // Calculate Affordability Index (price to income ratio - standard method)
  const affordabilityRatio = actualIncome > 0 
    ? (actualHomeValue / actualIncome) 
    : 0;
  
  // Get employment data for 3-mile radius (same as other metrics)
  const employmentData = currentData;
  const historicalEmployment = historicalData;
  
  const laborForce = employmentData.labor_force || 0;
  const employed = employmentData.employed || 0;
  const historicalEmployed = historicalEmployment.employed || 0;
  const jobsAdded = employed - historicalEmployed;
  
  // Determine affordability status using standard interpretation
  const getAffordabilityStatus = (ratio: number) => {
    if (ratio <= 3) return { status: 'Affordable', color: 'text-green-600', bgColor: 'bg-green-100' };
    if (ratio <= 5) return { status: 'Moderately Unaffordable', color: 'text-yellow-600', bgColor: 'bg-yellow-100' };
    return { status: 'Severely Unaffordable', color: 'text-red-600', bgColor: 'bg-red-100' };
  };
  
  const affordabilityInfo = getAffordabilityStatus(affordabilityRatio);
  
  // Get ATTOM demographic data
  const attomDemographics = attomData?.formatted_data?.demographics;
  const attomHousing = attomData?.formatted_data?.housing;
  
  return (
    <div className="bg-white rounded-lg shadow-card overflow-hidden">
      {/* 3-Mile Radius Header */}
      <div className="px-6 py-4 bg-teal-50 border-b border-teal-100">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          {/* <span className="text-sm font-medium px-3 py-1 rounded-full bg-teal-100 text-teal-700">
            3 Miles
          </span> */}
          Primary Market Analysis
        </h3>
      </div>
      
      {/* Three Column Layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-gray-100">
        
        {/* Demographics */}
        <div className="p-6">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-2xl">👥</span>
            <p className="text-sm font-medium text-gray-600">Demographics</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">{actualAge} yrs</p>
          <p className="text-sm text-gray-500 mt-1">Median Age</p>
          
          {/* Population */}
          <div className="mt-3 text-xs">
            <span className="text-gray-500">Population</span>
            <span className="font-medium text-gray-900 ml-2">{(currentData.total_population || 0).toLocaleString()}</span>
          </div>
          
          {/* Demographic Breakdown from ATTOM */}
          {attomDemographics && (
            <div className="mt-4 space-y-2">
              <p className="text-s text-gray-500 font-medium">Age Distribution</p>
              <div className="space-y-1">
                <div className="flex justify-between text-s">
                  <span className="text-gray-600">Under 18</span>
                  <span className="font-medium">{attomDemographics.age_distribution.under_18_pct.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-s">
                  <span className="text-gray-600">18-34</span>
                  <span className="font-medium">{attomDemographics.age_distribution["18_34_pct"].toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-s">
                  <span className="text-gray-600">35-64</span>
                  <span className="font-medium">{attomDemographics.age_distribution["35_64_pct"].toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-s">
                  <span className="text-gray-600">65+</span>
                  <span className="font-medium">{attomDemographics.age_distribution["65_plus_pct"].toFixed(1)}%</span>
                </div>
              </div>
              
              <div className="pt-2">
                <p className="text-s text-gray-500 font-medium">Ethnicity</p>
                <div className="mt-1 grid grid-cols-2 gap-x-3 gap-y-1">
                  <div className="text-s">
                    <span className="text-gray-600">White:</span>
                    <span className="ml-1 font-medium">{attomDemographics.breakdown.white_pct}%</span>
                  </div>
                  <div className="text-s">
                    <span className="text-gray-600">Asian:</span>
                    <span className="ml-1 font-medium">{attomDemographics.breakdown.asian_pct}%</span>
                  </div>
                  <div className="text-s">
                    <span className="text-gray-600">Hispanic:</span>
                    <span className="ml-1 font-medium">{attomDemographics.breakdown.hispanic_pct}%</span>
                  </div>
                  <div className="text-s">
                    <span className="text-gray-600">Black:</span>
                    <span className="ml-1 font-medium">{attomDemographics.breakdown.black_pct}%</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Affordability Index */}
        <div className="p-6">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-2xl">🏠</span>
            <p className="text-sm font-medium text-gray-600">Affordability Index</p>
          </div>
          
          {/* Ratio Display */}
          <div className="mb-3">
            <p className="text-3xl font-bold text-gray-900">{affordabilityRatio.toFixed(1)}</p>
            <p className="text-sm text-gray-500">House Price to Income Ratio</p>
          </div>
          
          {/* Visual Gauge */}
          <div className="mb-3">
            <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
              <div 
                className="h-2.5 transition-all duration-500"
                style={{ 
                  width: `${Math.min((affordabilityRatio / 10) * 100, 100)}%`,
                  background: affordabilityRatio <= 3 ? '#10b981' : affordabilityRatio <= 5 ? '#f59e0b' : '#ef4444'
                }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0</span>
              <span>3</span>
              <span>5</span>
              <span>10+</span>
            </div>
          </div>
          
          {/* Status Badge */}
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${affordabilityInfo.bgColor} ${affordabilityInfo.color}`}>
            {affordabilityInfo.status} Market
          </span>
          
          {/* Housing Details from ATTOM */}
          {attomHousing && (
            <div className="mt-4 pt-3 border-t border-gray-100 space-y-2">
              <p className="text-xs text-gray-500 font-medium">Housing Details</p>
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600">Owner Occupied</span>
                  <span className="font-medium">{attomHousing.owner_occupied_pct}%</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600">Renter Occupied</span>
                  <span className="font-medium">{attomHousing.renter_occupied_pct}%</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600">Median Rent</span>
                  <span className="font-medium">${attomHousing.median_rent.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600">Median Year Built</span>
                  <span className="font-medium">{attomHousing.median_year_built}</span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Employment Stats */}
        <div className="p-6">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-2xl">💼</span>
            <p className="text-sm font-medium text-gray-600">Employment Stats</p>
          </div>
          
          <div className="space-y-3">
            <div>
              <p className="text-2xl font-bold text-gray-900">{laborForce.toLocaleString()}</p>
              <p className="text-sm text-gray-500">Labor Force</p>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-lg font-semibold text-gray-900">{employed.toLocaleString()}</p>
                <p className="text-xs text-gray-500">Employed</p>
              </div>
              
              <div className="bg-green-50 rounded-lg p-3">
                <p className="text-lg font-semibold text-green-600">
                  +{jobsAdded > 0 ? jobsAdded.toLocaleString() : '0'}
                </p>
                <p className="text-xs text-gray-500">Jobs Added (5yr)</p>
              </div>
            </div>
            
            {/* Employment Type Breakdown */}
            {attomData?.formatted_data?.employment && (
              <div className="mt-3 pt-3 border-t border-gray-100">
                <p className="text-xs text-gray-500 mb-2 font-medium">Employment Type</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                    <span className="text-sm text-gray-700">White Collar</span>
                  </div>
                  <span className="text-sm font-semibold text-gray-900">
                    {attomData.formatted_data.employment.white_collar_pct}%
                  </span>
                </div>
                <div className="flex items-center justify-between mt-1">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                    <span className="text-sm text-gray-700">Blue Collar</span>
                  </div>
                  <span className="text-sm font-semibold text-gray-900">
                    {attomData.formatted_data.employment.blue_collar_pct}%
                  </span>
                </div>
              </div>
            )}
            
            <div className="text-xs text-gray-500 pt-1">
              <span className="font-medium">Employment Rate:</span> {laborForce > 0 ? ((employed / laborForce) * 100).toFixed(1) : '0'}%
            </div>
          </div>
        </div>
        
      </div>
      
      {/* Footer Note */}
      <div className="px-6 py-3 bg-gray-50 text-xs text-gray-500 text-center">
        Data from US Census ACS 5-Year Estimates • All metrics shown for 3-mile radius
      </div>
    </div>
  );
};

export default MarketMetricsDashboard;