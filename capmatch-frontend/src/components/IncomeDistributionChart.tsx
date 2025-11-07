import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface IncomeDistributionChartProps {
  incomeData?: any;
  radiusData?: any;
}

const IncomeDistributionChart: React.FC<IncomeDistributionChartProps> = ({ incomeData, radiusData }) => {
  // Calculate income distribution from raw data if available
  const calculateIncomeDistribution = (radius: string) => {
    if (!radiusData || !radiusData[radius]) {
      return [25, 25, 25, 25]; // Default values
    }
    
    const data = radiusData[radius]?.current?.data || radiusData[radius]?.current || {};
    
    // Sum up all income categories
    const incomeCategories = {
      under50k: (data.income_less_10k || 0) + (data.income_10k_15k || 0) + 
                (data.income_15k_20k || 0) + (data.income_20k_25k || 0) + 
                (data.income_25k_30k || 0) + (data.income_30k_35k || 0) + 
                (data.income_35k_40k || 0) + (data.income_40k_45k || 0) + 
                (data.income_45k_50k || 0),
      _50k_100k: (data.income_50k_60k || 0) + (data.income_60k_75k || 0) + 
                 (data.income_75k_100k || 0),
      _100k_150k: (data.income_100k_125k || 0) + (data.income_125k_150k || 0),
      _150k_plus: (data.income_150k_200k || 0) + (data.income_200k_plus || 0)
    };
    
    const total = Object.values(incomeCategories).reduce((sum, val) => sum + val, 0);
    
    if (total === 0) return [25, 25, 25, 25];
    
    return [
      ((incomeCategories.under50k / total) * 100).toFixed(1),
      ((incomeCategories._50k_100k / total) * 100).toFixed(1),
      ((incomeCategories._100k_150k / total) * 100).toFixed(1),
      ((incomeCategories._150k_plus / total) * 100).toFixed(1)
    ];
  };

  // Calculate distribution for each radius
  const oneMileDistribution = calculateIncomeDistribution('1_mile');
  const threeMileDistribution = calculateIncomeDistribution('3_mile');
  const fiveMileDistribution = calculateIncomeDistribution('5_mile');

  const chartData = {
    labels: ['< $50k', '$50k-$100k', '$100k-$150k', '$150k+'],
    datasets: [
      {
        label: 'One Mile',
        data: oneMileDistribution,
        backgroundColor: 'rgba(255, 107, 107, 0.8)',
        borderColor: 'rgba(255, 107, 107, 1)',
        borderWidth: 1,
      },
      {
        label: 'Three Mile',
        data: threeMileDistribution,
        backgroundColor: 'rgba(78, 205, 196, 0.8)',
        borderColor: 'rgba(78, 205, 196, 1)',
        borderWidth: 1,
      },
      {
        label: 'Five Mile',
        data: fiveMileDistribution,
        backgroundColor: 'rgba(69, 183, 209, 0.8)',
        borderColor: 'rgba(69, 183, 209, 1)',
        borderWidth: 1,
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
      title: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y || 0;
            return `${label}: ${value.toFixed(1)}%`;
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
        max: 60,
        ticks: {
          stepSize: 10,
          callback: function(tickValue: string | number) {
            return tickValue + '%';
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

  return (
    <div className="bg-white rounded-lg shadow-card p-6">
      <div className="h-80">
        <Bar data={chartData} options={options} />
      </div>
    </div>
  );
};

export default IncomeDistributionChart;