// src/components/TransportationChart.tsx

import React from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';
import { Pie } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

interface TransportationChartProps {
  attomData: any;
}

const TransportationChart: React.FC<TransportationChartProps> = ({ attomData }) => {
  const transportation = attomData?.formatted_data?.transportation;
  
  if (!transportation) {
    return (
      <div className="bg-white rounded-lg shadow-card p-6">
        <p className="text-gray-500 text-center">No transportation data available</p>
      </div>
    );
  }

  // Prepare data for pie chart - only include non-zero values
  const labels: string[] = [];
  const data: number[] = [];
  const backgroundColors: string[] = [];
  const borderColors: string[] = [];
  
  const transportModes = [
    { label: 'Drive Alone', value: transportation.drive_alone_pct, color: '#3B82F6', icon: '🚗' },
    { label: 'Work from Home', value: transportation.work_from_home_pct, color: '#10B981', icon: '🏠' },
    { label: 'Carpool', value: transportation.carpool_pct, color: '#F59E0B', icon: '🚐' },
    { label: 'Public Transit', value: transportation.public_transit_pct, color: '#EF4444', icon: '🚌' },
    { label: 'Walk', value: transportation.walk_pct, color: '#8B5CF6', icon: '🚶' },
    { label: 'Bicycle', value: transportation.bicycle_pct, color: '#EC4899', icon: '🚴' },
    { label: 'Other', value: transportation.other_pct, color: '#6B7280', icon: '✈️' }
  ];

  transportModes.forEach(mode => {
    if (mode.value > 0) {
      labels.push(`${mode.icon} ${mode.label}`);
      data.push(mode.value);
      backgroundColors.push(mode.color + 'CC'); // Add transparency
      borderColors.push(mode.color);
    }
  });

  const chartData = {
    labels,
    datasets: [
      {
        data,
        backgroundColor: backgroundColors,
        borderColor: borderColors,
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          font: {
            size: 15,
          },
          padding: 10,
          generateLabels: (chart: any) => {
            const data = chart.data;
            if (data.labels.length && data.datasets.length) {
              return data.labels.map((label: string, i: number) => {
                const value = data.datasets[0].data[i];
                return {
                  text: `${label}: ${value}%`,
                  fillStyle: data.datasets[0].backgroundColor[i],
                  strokeStyle: data.datasets[0].borderColor[i],
                  lineWidth: 1,
                  index: i,
                };
              });
            }
            return [];
          },
        },
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            return `${context.label}: ${context.parsed}%`;
          },
        },
      },
    },
  };

  // Find the highest percentage mode
  const dominantMode = transportModes.reduce((prev, current) => 
    (current.value > prev.value) ? current : prev
  );

  return (
    <div className="bg-white rounded-lg shadow-card p-6 h-full flex flex-col">
      <div className="h-72 flex-shrink-0">
        <Pie data={chartData} options={options} />
      </div>
      
      {/* Key Stats */}
      <div className="mt-auto pt-4 border-t border-gray-100 space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Dominant Mode</span>
          <span className="font-medium text-gray-900">
            {dominantMode.icon} {dominantMode.label} ({dominantMode.value}%)
          </span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Remote Workers</span>
          <span className="font-medium text-gray-900">{transportation.work_from_home_pct}%</span>
        </div>
      </div>
    </div>
  );
};

export default TransportationChart;