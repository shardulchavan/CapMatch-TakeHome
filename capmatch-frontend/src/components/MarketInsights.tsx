// src/components/MarketInsights.tsx

import React from 'react';

interface MarketInsightsProps {
  insights: any;
}

const MarketInsights: React.FC<MarketInsightsProps> = ({ insights }) => {
  const sections = [
    {
      title: 'Demographic Strengths',
      icon: '💪',
      items: insights?.demographic_strengths || [],
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      title: 'Market Opportunities',
      icon: '🎯',
      items: insights?.market_opportunities || [],
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      title: 'Target Demographics',
      icon: '👥',
      items: insights?.target_demographics || [],
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    }
  ];

  return (
    <div className="grid md:grid-cols-3 gap-6">
      {sections.map((section, index) => (
        <div key={index} className="bg-white rounded-lg shadow-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">{section.icon}</span>
            <h3 className="font-semibold text-gray-900">{section.title}</h3>
          </div>
          
          <ul className="space-y-3">
            {section.items.map((item: string, itemIndex: number) => (
              <li key={itemIndex} className="flex items-start gap-2">
                <span className={`w-2 h-2 rounded-full ${section.bgColor} mt-1.5 flex-shrink-0`}></span>
                <span className="text-sm text-gray-700 leading-relaxed">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default MarketInsights;