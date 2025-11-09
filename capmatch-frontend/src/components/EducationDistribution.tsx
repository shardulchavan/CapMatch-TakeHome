// src/components/EducationDistribution.tsx

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarController,
  LineController
} from 'chart.js';
import { Chart } from 'react-chartjs-2';

// Register everything needed for mixed charts
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarController,
  LineController
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
  
  // Interpolate data for years between
  const years = [];
  const bachelorsData = [];
  const mastersData = [];
  const advancedData = [];
  const totalData = [];
  
  for (let year = historicalYear; year <= currentYear; year++) {
    years.push(year.toString());
    
    const progress = (year - historicalYear) / (currentYear - historicalYear);
    
    // Interpolate values
    const interpBachelors = historicalBachelors + (currentBachelors - historicalBachelors) * progress;
    const interpMasters = historicalMasters + (currentMasters - historicalMasters) * progress;
    const interpAdvanced = (historicalProfessional + historicalDoctorate) + 
                          ((currentProfessional + currentDoctorate) - 
                           (historicalProfessional + historicalDoctorate)) * progress;
    const interpTotal = historicalTotal + (currentTotal - historicalTotal) * progress;
    
    bachelorsData.push(Math.round(interpBachelors));
    mastersData.push(Math.round(interpMasters));
    advancedData.push(Math.round(interpAdvanced));
    totalData.push(Math.round(interpTotal));
  }
  
  const chartData = {
    labels: years,
    datasets: [
      // Bar chart data (stacked)
      {
        type: 'bar' as const,
        label: "Bachelor's Degrees",
        data: bachelorsData,
        backgroundColor: 'rgba(78, 205, 196, 0.7)',
        borderColor: 'rgb(78, 205, 196)',
        borderWidth: 1,
        stack: 'Stack 0',
      },
      {
        type: 'bar' as const,
        label: "Master's Degrees",
        data: mastersData,
        backgroundColor: 'rgba(69, 183, 209, 0.7)',
        borderColor: 'rgb(69, 183, 209)',
        borderWidth: 1,
        stack: 'Stack 0',
      },
      {
        type: 'bar' as const,
        label: "PhD/Professional",
        data: advancedData,
        backgroundColor: 'rgba(255, 107, 107, 0.7)',
        borderColor: 'rgb(255, 107, 107)',
        borderWidth: 1,
        stack: 'Stack 0',
      },
      // Line chart for total
      {
        type: 'line' as const,
        label: 'Total Graduates',
        data: totalData,
        borderColor: 'rgb(99, 102, 241)',
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        borderWidth: 3,
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0.3,
        yAxisID: 'y1',
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          font: {
            size: 11
          },
          usePointStyle: true,
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
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        stacked: true,
        title: {
          display: true,
          text: 'Number of Degrees (Stacked)',
          font: {
            size: 11
          }
        },
        ticks: {
          callback: function(tickValue: string | number) {
            return Number(tickValue).toLocaleString();
          },
          font: {
            size: 10
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'Total Graduates',
          font: {
            size: 11
          }
        },
        ticks: {
          callback: function(tickValue: string | number) {
            return Number(tickValue).toLocaleString();
          },
          font: {
            size: 10
          }
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
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
      
      <div className="h-72">
        <Chart type="bar" data={chartData} options={options} />
      </div>
      
      <div className="mt-4 grid grid-cols-3 gap-4 text-center">
        <div>
          <p className="text-xs text-gray-500">Bachelor's</p>
          <p className="text-sm font-medium text-teal-600">{currentBachelors.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Master's</p>
          <p className="text-sm font-medium text-blue-600">{currentMasters.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">PhD/Professional</p>
          <p className="text-sm font-medium text-red-600">{(currentProfessional + currentDoctorate).toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
};

export default EducationDistribution;