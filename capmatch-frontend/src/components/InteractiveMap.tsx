import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

interface InteractiveMapProps {
  center: [number, number];
  circles: any[];
  address: string;
}

// Component to fit map bounds
const FitBounds: React.FC<{ circles: any[] }> = ({ circles }) => {
  const map = useMap();
  
  useEffect(() => {
    if (circles && circles.length > 0) {
      // Get the largest circle to determine bounds
      const largestCircle = circles[circles.length - 1];
      const radiusMiles = largestCircle.properties.radius_miles;
      
      // Approximate bounds (1 mile ≈ 0.0145 degrees at this latitude)
      const degreePerMile = 0.0145;
      const buffer = radiusMiles * degreePerMile * 1.2; // 20% buffer
      
      const bounds = L.latLngBounds(
        [map.getCenter().lat - buffer, map.getCenter().lng - buffer],
        [map.getCenter().lat + buffer, map.getCenter().lng + buffer]
      );
      
      map.fitBounds(bounds);
    }
  }, [circles, map]);
  
  return null;
};

const InteractiveMap: React.FC<InteractiveMapProps> = ({ center, circles, address }) => {
  // Style function for GeoJSON circles
  const circleStyle = (feature: any) => {
    return {
      fillColor: feature.properties.color,
      fillOpacity: feature.properties.fillOpacity,
      color: feature.properties.color,
      weight: feature.properties.strokeWeight,
      opacity: feature.properties.strokeOpacity
    };
  };

  // Create popup content for each circle
  const onEachCircle = (feature: any, layer: any) => {
    if (feature.properties && feature.properties.population_formatted) {
      const popupContent = `
        <div style="text-align: center; padding: 8px;">
          <strong>${feature.properties.radius_miles} Mile Radius</strong><br/>
          Population: ${feature.properties.population_formatted}
        </div>
      `;
      layer.bindPopup(popupContent);
      
      // Add hover effect
      layer.on({
        mouseover: (e: any) => {
          e.target.setStyle({
            fillOpacity: feature.properties.fillOpacity * 2
          });
        },
        mouseout: (e: any) => {
          e.target.setStyle({
            fillOpacity: feature.properties.fillOpacity
          });
        }
      });
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-card p-4">
      <div className="h-96 rounded-lg overflow-hidden">
        <MapContainer
          center={center}
          zoom={12}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {/* Add radius circles */}
            {circles.slice().reverse().map((circle, index) => (
            <GeoJSON
                key={`circle-${index}-${circle.properties.radius_miles}`}
                data={circle}
                style={circleStyle}
                onEachFeature={onEachCircle}
            />
            ))}
          
          {/* Center marker */}
          <Marker position={center}>
            <Popup>
              <div className="text-center p-2">
                <strong>{address}</strong><br/>
                <span className="text-sm text-gray-600">Analysis Center Point</span>
              </div>
            </Popup>
          </Marker>
          
          <FitBounds circles={circles} />
        </MapContainer>
      </div>
      
      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-4 text-sm">
        <div className="flex items-center gap-2">
          <span className="w-4 h-4 bg-red-500 opacity-30 rounded"></span>
          <span className="text-gray-600">1 Mile</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-4 bg-teal-500 opacity-30 rounded"></span>
          <span className="text-gray-600">3 Miles</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-4 bg-blue-500 opacity-30 rounded"></span>
          <span className="text-gray-600">5 Miles</span>
        </div>
      </div>
    </div>
  );
};

export default InteractiveMap;