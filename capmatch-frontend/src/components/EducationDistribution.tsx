import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface EducationDistributionProps {
  radiusData: any;
}

const EducationDistribution: React.FC<EducationDistributionProps> = ({ radiusData }) => {
  // Get 5-mile radius data
  const fiveMileData = radiusData?.['5_mile'];
  const currentData = fiveMileData?.current?.data || fiveMileData?.current || {};
  const historicalData = fiveMileData?.historical?.data || fiveMileData?.historical || {};
  
  // Calculate education numbers for 2022 (current) and 2017 (historical)
  const currentYear = parseInt(radiusData?.['5_mile']?.current?.year || '2022');
  const historicalYear = parseInt(radiusData?.['5_mile']?.historical?.year || '2017');
  
  // Current year data
  const currentBachelors = currentData.bachelors_degree || 0;
  const currentMasters = currentData.masters_degree || 0;
  const currentProfessional = currentData.professional_degree || 0;
  const currentDoctorate = currentData.doctorate_degree || 0;
  const currentTotal = currentBachelors + currentMasters + currentProfessional + currentDoctorate;
  
  // Historical year data
  const historicalBachelors = historicalData.bachelors_degree || 0;
  const historicalMasters = historicalData.masters_degree || 0;
  const historicalProfessional = historicalData.professional_degree || 0;
  const historicalDoctorate = historicalData.doctorate_degree || 0;
  const historicalTotal = historicalBachelors + historicalMasters + historicalProfessional + historicalDoctorate;
  
  // Interpolate data for years between (simple linear interpolation)
  const years = [];
  const bachelorsData = [];
  const advancedData = [];
  const totalData = [];
  
  for (let year = historicalYear; year <= currentYear; year++) {
    years.push(year.toString());
    
    const progress = (year - historicalYear) / (currentYear - historicalYear);
    
    // Interpolate values
    const interpBachelors = historicalBachelors + (currentBachelors - historicalBachelors) * progress;
    const interpAdvanced = (historicalMasters + historicalProfessional + historicalDoctorate) + 
                          ((currentMasters + currentProfessional + currentDoctorate) - 
                           (historicalMasters + historicalProfessional + historicalDoctorate)) * progress;
    const interpTotal = historicalTotal + (currentTotal - historicalTotal) * progress;
    
    bachelorsData.push(Math.round(interpBachelors));
    advancedData.push(Math.round(interpAdvanced));
    totalData.push(Math.round(interpTotal));
  }
  
  const chartData = {
    labels: years,
    datasets: [
      {
        label: "Total College Graduates",
        data: totalData,
        borderColor: 'rgb(69, 183, 209)',
        backgroundColor: 'rgba(69, 183, 209, 0.1)',
        tension: 0.3,
        borderWidth: 2,
      },
      {
        label: "Bachelor's Degrees",
        data: bachelorsData,
        borderColor: 'rgb(78, 205, 196)',
        backgroundColor: 'rgba(78, 205, 196, 0.1)',
        tension: 0.3,
        borderWidth: 2,
      },
      {
        label: "Advanced Degrees",
        data: advancedData,
        borderColor: 'rgb(255, 107, 107)',
        backgroundColor: 'rgba(255, 107, 107, 0.1)',
        tension: 0.3,
        borderWidth: 2,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y || 0;
            return `${label}: ${value.toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          font: {
            size: 11
          }
        }
      },
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(tickValue: string | number) {
            return Number(tickValue).toLocaleString();
          },
          font: {
            size: 11
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      }
    }
  };

  // Calculate growth percentage
  const growthPercent = ((currentTotal - historicalTotal) / historicalTotal * 100).toFixed(1);
  const population = currentData.total_population || 1;
  const educationPercent = ((currentTotal / population) * 100).toFixed(1);

  return (
    <div className="bg-white rounded-lg shadow-card p-6">
      <div className="mb-4 flex justify-between items-start">
        <div>
          <p className="text-sm text-gray-500">Total Graduates in 2022</p>
          <p className="text-2xl font-semibold text-gray-900">{currentTotal.toLocaleString()}</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">Growth Rate</p>
          <p className="text-xl font-semibold text-green-600">+{growthPercent}%</p>
          <p className="text-xs text-gray-500">{educationPercent}% of population</p>
        </div>
      </div>
      
      <div className="h-64">
        <Line data={chartData} options={options} />
      </div>
      
      <div className="mt-4 grid grid-cols-3 gap-4 text-center">
        <div>
          <p className="text-xs text-gray-500">Bachelor's</p>
          <p className="text-sm font-medium">{currentBachelors.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Master's</p>
          <p className="text-sm font-medium">{currentMasters.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">PhD/Professional</p>
          <p className="text-sm font-medium">{(currentProfessional + currentDoctorate).toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
};

export default EducationDistribution;