import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';
import { MapPin, Star, Globe, Phone, ExternalLink } from 'lucide-react';

// Custom Blue Pin for Citizen / Searched Location
const LocationIcon = L.divIcon({
  className: 'custom-location-pin',
  html: `<div style="
    background-color: #2563eb;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 3px solid #ffffff;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.45), 0 3px 8px rgba(0,0,0,0.35);
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  "><div style="
    width: 8px;
    height: 8px;
    background-color: #ffffff;
    border-radius: 50%;
  "></div></div>`,
  iconSize: [24, 24],
  iconAnchor: [12, 12],
  popupAnchor: [0, -14]
});

// Custom Saffron/Orange Pin for Official NagrikSetu Training Centres
const OfficialCentreIcon = L.divIcon({
  className: 'custom-official-centre-pin',
  html: `<div style="
    background-color: #ea580c;
    width: 28px;
    height: 28px;
    border-radius: 50% 50% 50% 0;
    transform: rotate(-45deg);
    border: 2px solid #ffffff;
    box-shadow: 0 3px 8px rgba(0,0,0,0.35);
    display: flex;
    align-items: center;
    justify-content: center;
  "><div style="
    width: 10px;
    height: 10px;
    background-color: #ffffff;
    border-radius: 50%;
    transform: rotate(45deg);
  "></div></div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 28],
  popupAnchor: [0, -28]
});

// Custom Teal Pin for External Discovered Real-World Institutes
const DiscoveredInstituteIcon = L.divIcon({
  className: 'custom-discovered-pin',
  html: `<div style="
    background-color: #0d9488;
    width: 26px;
    height: 26px;
    border-radius: 50% 50% 50% 0;
    transform: rotate(-45deg);
    border: 2px solid #ffffff;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    justify-content: center;
  "><div style="
    width: 8px;
    height: 8px;
    background-color: #ffffff;
    border-radius: 50%;
    transform: rotate(45deg);
  "></div></div>`,
  iconSize: [26, 26],
  iconAnchor: [13, 26],
  popupAnchor: [0, -26]
});

// Custom Highlighted Pin when a centre is selected from the list
const HighlightedIcon = L.divIcon({
  className: 'custom-highlighted-pin',
  html: `<div style="
    background-color: #b91c1c;
    width: 32px;
    height: 32px;
    border-radius: 50% 50% 50% 0;
    transform: rotate(-45deg);
    border: 3px solid #fef08a;
    box-shadow: 0 0 0 4px rgba(185,28,28,0.4), 0 4px 10px rgba(0,0,0,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
  "><div style="
    width: 12px;
    height: 12px;
    background-color: #ffffff;
    border-radius: 50%;
    transform: rotate(45deg);
  "></div></div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
});

interface CentreLocationMapProps {
  userLocation: { latitude: number; longitude: number } | null;
  locationLabel?: string;
  centres: any[];
  radiusKm: number;
  selectedCentreId?: string | null;
  onSelectCentre?: (centre: any) => void;
}

// Controller component to smoothly fit map view to markers and selected location
function MapRecenter({
  center,
  bounds,
  selectedLocation
}: {
  center: [number, number];
  bounds?: L.LatLngBoundsExpression;
  selectedLocation?: [number, number] | null;
}) {
  const map = useMap();
  useEffect(() => {
    if (selectedLocation) {
      map.setView(selectedLocation, 15, { animate: true });
    } else if (bounds) {
      try {
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14, animate: true });
      } catch (e) {
        map.setView(center, 12);
      }
    } else {
      map.setView(center, 12);
    }
  }, [center, bounds, selectedLocation, map]);
  return null;
}

export const CentreLocationMap: React.FC<CentreLocationMapProps> = ({
  userLocation,
  locationLabel,
  centres,
  radiusKm,
  selectedCentreId,
  onSelectCentre
}) => {
  const centerLat = userLocation ? userLocation.latitude : 12.9716;
  const centerLon = userLocation ? userLocation.longitude : 77.5946;
  const centerCoords: [number, number] = [centerLat, centerLon];
  const markerRefs = useRef<Record<string, L.Marker>>({});

  // Collect all points for bounds calculation
  const validPoints: [number, number][] = [];
  if (userLocation) {
    validPoints.push([userLocation.latitude, userLocation.longitude]);
  }
  centres.forEach((c) => {
    if (c.latitude != null && c.longitude != null) {
      validPoints.push([Number(c.latitude), Number(c.longitude)]);
    }
  });

  const bounds: L.LatLngBoundsExpression | undefined =
    validPoints.length > 1 ? (validPoints as [number, number][]) : undefined;

  // Selected item position if user clicked on list card
  const selectedCentre = centres.find(
    (c) => (c.id === selectedCentreId || c.code === selectedCentreId)
  );
  const selectedLocation: [number, number] | null =
    selectedCentre && selectedCentre.latitude != null && selectedCentre.longitude != null
      ? [Number(selectedCentre.latitude), Number(selectedCentre.longitude)]
      : null;

  // Automatically open the popup of the selected marker
  useEffect(() => {
    if (selectedCentreId && markerRefs.current[selectedCentreId]) {
      markerRefs.current[selectedCentreId].openPopup();
    }
  }, [selectedCentreId]);

  return (
    <div style={{ height: '440px', width: '100%', borderRadius: '12px', overflow: 'hidden', border: '1px solid #cbd5e1', position: 'relative', zIndex: 1, boxShadow: '0 2px 6px rgba(0,0,0,0.06)' }}>
      <MapContainer
        center={centerCoords}
        zoom={userLocation ? 12 : 7}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapRecenter center={centerCoords} bounds={bounds} selectedLocation={selectedLocation} />

        {/* Selected Search / GPS Location Pin */}
        {userLocation && (
          <>
            <Marker position={[userLocation.latitude, userLocation.longitude]} icon={LocationIcon}>
              <Popup>
                <div style={{ fontSize: '0.85rem', lineHeight: '1.4' }}>
                  <strong style={{ color: '#1e3a8a' }}>Searched Origin</strong>
                  <div style={{ fontSize: '0.78rem', color: '#475569', marginTop: '2px' }}>
                    {locationLabel || 'Target Search Coordinates'}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '2px' }}>
                    {userLocation.latitude.toFixed(5)}, {userLocation.longitude.toFixed(5)}
                  </div>
                </div>
              </Popup>
            </Marker>

            {/* Dynamic Radius Visual Circle */}
            <Circle
              center={[userLocation.latitude, userLocation.longitude]}
              radius={radiusKm * 1000}
              pathOptions={{
                color: '#2563eb',
                fillColor: '#3b82f6',
                fillOpacity: 0.08,
                weight: 1.5,
                dashArray: '5, 5'
              }}
            />
          </>
        )}

        {/* Training Centre & Real-World Discovered Markers */}
        {centres.map((c) => {
          if (c.latitude == null || c.longitude == null) return null;
          const centreKey = c.id || c.code;
          const isSelected = (c.id === selectedCentreId || c.code === selectedCentreId);
          let markerIcon = c.is_official_centre ? OfficialCentreIcon : DiscoveredInstituteIcon;
          if (isSelected) {
            markerIcon = HighlightedIcon;
          }

          return (
            <Marker
              key={centreKey}
              position={[Number(c.latitude), Number(c.longitude)]}
              icon={markerIcon}
              ref={(ref) => {
                if (ref) {
                  markerRefs.current[centreKey] = ref;
                } else {
                  delete markerRefs.current[centreKey];
                }
              }}
              eventHandlers={{
                click: () => {
                  if (onSelectCentre) onSelectCentre(c);
                }
              }}
            >
              <Popup>
                <div style={{ maxWidth: '290px', fontSize: '0.82rem', lineHeight: '1.4' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span
                      style={{
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        color: c.is_official_centre ? '#ea580c' : '#0d9488',
                        backgroundColor: c.is_official_centre ? '#fff7ed' : '#f0fdfa',
                        padding: '2px 6px',
                        borderRadius: '4px'
                      }}
                    >
                      {c.is_official_centre ? (c.code || 'Official NagrikSetu Hub') : (c.category || 'Training Institute')}
                    </span>
                    {c.distance_km != null && (
                      <span style={{ fontSize: '0.72rem', fontWeight: 600, color: '#0f766e', backgroundColor: '#ccfbf1', padding: '2px 6px', borderRadius: '4px' }}>
                        {c.distance_km} km
                      </span>
                    )}
                  </div>
                  <h4 style={{ margin: '2px 0 4px 0', fontSize: '0.94rem', color: '#0f172a', fontWeight: 700 }}>
                    {c.name}
                  </h4>
                  <p style={{ margin: '0 0 6px 0', fontSize: '0.76rem', color: '#475569' }}>
                    {c.address}
                  </p>

                  {/* Genuine Rating / Reviews only if provided */}
                  {c.rating && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', color: '#d97706', marginBottom: '4px' }}>
                      <Star size={12} fill="#d97706" color="#d97706" />
                      <strong>{c.rating}</strong>
                      {c.review_count && (
                        <span style={{ color: '#64748b' }}>({c.review_count} reviews)</span>
                      )}
                    </div>
                  )}

                  {/* Contact Info */}
                  <div style={{ fontSize: '0.75rem', color: '#334155', marginBottom: '6px' }}>
                    {c.phone && <div><strong>Phone:</strong> {c.phone}</div>}
                    {c.website && (
                      <div style={{ marginTop: '2px' }}>
                        <a href={c.website} target="_blank" rel="noopener noreferrer" style={{ color: '#2563eb', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
                          <Globe size={11} /> Visit Website
                        </a>
                      </div>
                    )}
                  </div>

                  {/* Active Selection Badge inside Popup */}
                  {isSelected && (
                    <div style={{ marginTop: '6px', fontSize: '0.72rem', fontWeight: 700, color: '#b91c1c', backgroundColor: '#fef2f2', padding: '3px 8px', borderRadius: '4px', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      <MapPin size={11} /> Selected Training Centre
                    </div>
                  )}
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};
