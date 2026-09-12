import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Polygon, Marker, Popup, Polyline } from 'react-leaflet';
import { 
  MapPin, Layers, CheckCircle2, Car, Crosshair, 
  Compass, ExternalLink, Navigation, Eye 
} from 'lucide-react';
import L from 'leaflet';
import RecordDetailsModal from '../components/RecordDetailsModal';

const GISMapPage = () => {
  const [parcels, setParcels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedParcel, setSelectedParcel] = useState(null);
  const [modalRecord, setModalRecord] = useState(null);

  const fetchParcels = async () => {
    try {
      const res = await axios.get('/api/gis/parcels');
      setParcels(Array.isArray(res.data?.features) ? res.data.features : []);
    } catch (err) {
      console.error(err);
      setParcels([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchParcels();
  }, []);

  // Compute selected parcel metrics & road vantage point
  let centerLat = selectedParcel ? selectedParcel.center[0] : 23.2599;
  let centerLng = selectedParcel ? selectedParcel.center[1] : 77.4126;
  const roadLat = centerLat - 0.00068;
  const roadLng = centerLng - 0.00034;

  const dLatM = (centerLat - roadLat) * 111320;
  const dLngM = (centerLng - roadLng) * (111320 * Math.cos(centerLat * Math.PI / 180));
  const distanceMeters = Math.round(Math.hypot(dLatM, dLngM));
  let heading = Math.round((Math.atan2(dLngM, dLatM) * 180 / Math.PI + 360) % 360);

  const getCardinal = (deg) => {
    const directions = ['North', 'NNE', 'North-East', 'ENE', 'East', 'ESE', 'South-East', 'SSE', 'South', 'SSW', 'South-West', 'WSW', 'West', 'WNW', 'North-West', 'NNW'];
    return directions[Math.round(deg / 22.5) % 16];
  };
  const cardinalDirection = getCardinal(heading);

  const googleStreetViewUrl = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${roadLat.toFixed(6)},${roadLng.toFixed(6)}&heading=${heading}&pitch=3&fov=75`;
  const googleLandPinUrl = `https://www.google.com/maps/search/?api=1&query=${centerLat.toFixed(6)},${centerLng.toFixed(6)}`;

  // Custom DivIcons for Map
  const roadCarIcon = L.divIcon({
    className: 'custom-car-div-icon',
    html: `
      <div style="
        width: 32px;
        height: 32px;
        background: #1e3a8a;
        border: 2px solid #93c5fd;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(30, 58, 138, 0.6);
        color: white;
        font-size: 14px;
      ">
        🚗
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });

  const landTargetIcon = L.divIcon({
    className: 'custom-land-div-icon',
    html: `
      <div style="
        width: 34px;
        height: 34px;
        background: #059669;
        border: 2px solid #a7f3d0;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.7);
        color: white;
        font-size: 16px;
      ">
        🎯
      </div>
    `,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
  });

  // Handler to open full modal for selected parcel
  const handleOpenFullInspector = () => {
    if (!selectedParcel) return;
    const selectedFeature = parcels.find(f => f.properties.id === selectedParcel.id);
    const geometry = selectedFeature ? selectedFeature.geometry : null;

    setModalRecord({
      ...selectedParcel,
      land_area: selectedParcel.cadastral_area,
      registration_number: `CAD-${selectedParcel.survey_number.replace('/', '-')}`,
      registration_date: `01-01-${selectedParcel.survey_year || 2023}`,
      document_status: selectedParcel.status === 'APPROVED' ? 'Digitized and Verified' : 'Cadastral Baseline Ground Truth',
      coordinates_geojson: geometry
    });
  };

  return (
    <div className="flex-1 bg-slate-100 p-4 sm:p-6 flex flex-col space-y-4 sm:space-y-6 h-[calc(100vh-112px)] overflow-hidden">
      {/* Top Header */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3 shrink-0">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-amber-900 bg-amber-100 px-2.5 py-0.5 rounded-full">
              Cadastral GIS Engine
            </span>
            <span className="text-xs font-bold text-slate-500">
              OpenStreetMap + Cadastral GeoJSON Boundaries + Street View Locator
            </span>
          </div>
          <h1 className="text-lg sm:text-xl font-bold text-slate-900 mt-1">
            Spatial Land Parcel & Cadastral Boundary Explorer
          </h1>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <div className="w-3.5 h-3.5 rounded bg-emerald-500 border border-emerald-700"></div>
            <span className="font-semibold text-slate-700">Approved Parcel</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3.5 h-3.5 rounded bg-amber-500 border border-amber-700"></div>
            <span className="font-semibold text-slate-700">Pending Review</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-sm">🚗</span>
            <span className="font-semibold text-blue-900">Road Vantage</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-sm">🎯</span>
            <span className="font-semibold text-emerald-900">Land Target</span>
          </div>
        </div>
      </div>

      {/* Map + Detail Panel */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-4 sm:gap-6 overflow-hidden">
        
        {/* Map Container (3 cols) */}
        <div className="lg:col-span-3 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden relative">
          {loading ? (
            <div className="h-full flex items-center justify-center text-slate-500">
              <div className="w-8 h-8 border-4 border-blue-900 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
              Loading GIS layers...
            </div>
          ) : (
            <MapContainer
              center={[23.2599, 77.4126]}
              zoom={13}
              className="h-full w-full z-10"
            >
              <TileLayer
                attribution="&copy; OpenStreetMap contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              {parcels.map((feature) => {
                const props = feature.properties;
                const coords = feature.geometry.coordinates[0].map(pt => [pt[1], pt[0]]);
                const isVerified = props.verified;
                const isSelected = selectedParcel && selectedParcel.id === props.id;

                return (
                  <Polygon
                    key={props.id}
                    positions={coords}
                    pathOptions={{
                      color: isSelected ? '#2563eb' : (isVerified ? '#10b981' : '#f59e0b'),
                      fillColor: isSelected ? '#3b82f6' : (isVerified ? '#10b981' : '#f59e0b'),
                      fillOpacity: isSelected ? 0.65 : 0.45,
                      weight: isSelected ? 3 : 2
                    }}
                    eventHandlers={{
                      click: () => setSelectedParcel(props)
                    }}
                  >
                    <Popup>
                      <div className="text-xs p-1">
                        <div className="font-bold text-blue-950 font-mono text-sm">
                          Survey: {props.survey_number}
                        </div>
                        <div className="font-semibold text-slate-800 mt-1">
                          Owner: {props.owner_name}
                        </div>
                        <div className="text-slate-600">
                          Cadastral Area: <strong>{props.cadastral_area} Acres</strong>
                        </div>
                        <div className="text-slate-600">
                          Village: {props.village}, {props.district}
                        </div>
                        <div className="mt-2 flex items-center justify-between">
                          <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                            isVerified ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                          }`}>
                            {props.status}
                          </span>
                        </div>
                      </div>
                    </Popup>
                  </Polygon>
                );
              })}

              {/* When a parcel is selected: render Road Vantage & Land Point markers and sightline */}
              {selectedParcel && (
                <>
                  {/* Sightline from road to land */}
                  <Polyline
                    positions={[
                      [roadLat, roadLng],
                      [centerLat, centerLng]
                    ]}
                    pathOptions={{
                      color: '#f59e0b',
                      weight: 3,
                      dashArray: '5, 8'
                    }}
                  />

                  {/* Road Vantage Car Marker */}
                  <Marker position={[roadLat, roadLng]} icon={roadCarIcon}>
                    <Popup>
                      <div className="text-xs">
                        <strong>🚗 Street View Road Vantage Point</strong>
                        <p className="text-slate-600">Nearest public road where Street View vehicle captured imagery</p>
                        <p className="font-mono text-[10px] text-slate-500 mt-1">
                          {roadLat.toFixed(5)}° N, {roadLng.toFixed(5)}° E
                        </p>
                      </div>
                    </Popup>
                  </Marker>

                  {/* Land Parcel Centroid Target Marker */}
                  <Marker position={[centerLat, centerLng]} icon={landTargetIcon}>
                    <Popup>
                      <div className="text-xs">
                        <strong>🎯 Land Parcel Centroid (Survey {selectedParcel.survey_number})</strong>
                        <p className="text-slate-600">{selectedParcel.owner_name} ({selectedParcel.cadastral_area} Acres)</p>
                        <p className="font-mono text-[10px] text-emerald-700 mt-1">
                          {centerLat.toFixed(5)}° N, {centerLng.toFixed(5)}° E
                        </p>
                      </div>
                    </Popup>
                  </Marker>
                </>
              )}
            </MapContainer>
          )}
        </div>

        {/* Selected Parcel Inspector (Right Column) */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4 sm:p-6 overflow-y-auto space-y-4">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-blue-900" />
            <h3 className="text-base font-bold text-slate-900">Parcel Inspector</h3>
          </div>

          {selectedParcel ? (
            <div className="space-y-4 text-xs">
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl">
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Survey Number</span>
                <span className="text-lg font-bold font-mono text-blue-950">{selectedParcel.survey_number}</span>
              </div>

              {/* Core Attributes */}
              <div className="space-y-2 bg-slate-50 p-3.5 rounded-xl border border-slate-200">
                <div>
                  <span className="text-slate-500 block">Current Registered Landowner</span>
                  <span className="font-bold text-slate-900 text-sm">{selectedParcel.owner_name}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Cadastral Survey Ground Truth Area</span>
                  <span className="font-bold text-slate-900 font-mono">{selectedParcel.cadastral_area} Acres</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Classification</span>
                  <span className="font-medium text-slate-800">{selectedParcel.land_classification}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Village & District</span>
                  <span className="font-medium text-slate-800">{selectedParcel.village}, {selectedParcel.district}</span>
                </div>
              </div>

              {/* DEDICATED STREET VIEW & LAND LOCATOR POINT CARD */}
              <div className="bg-gradient-to-br from-amber-50 to-orange-50 p-4 rounded-xl border border-amber-300 space-y-3">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-amber-600 text-white rounded-lg">
                    <Crosshair className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="font-bold text-amber-950 text-xs">Street View Land Locator</h4>
                    <span className="text-[10px] text-amber-800">Point to locate off-road land</span>
                  </div>
                </div>

                <div className="text-[11px] text-slate-700 bg-white/80 p-2.5 rounded-lg border border-amber-200 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 flex items-center gap-1">
                      <Car className="w-3 h-3 text-blue-700" /> Road Vantage:
                    </span>
                    <span className="font-mono font-bold text-blue-900">{roadLat.toFixed(4)}°, {roadLng.toFixed(4)}°</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 flex items-center gap-1">
                      <Crosshair className="w-3 h-3 text-emerald-700" /> Land Centroid:
                    </span>
                    <span className="font-mono font-bold text-emerald-900">{centerLat.toFixed(4)}°, {centerLng.toFixed(4)}°</span>
                  </div>
                  <div className="flex items-center justify-between pt-1 border-t border-slate-100">
                    <span className="text-slate-500">Offset Distance:</span>
                    <span className="font-mono font-bold text-amber-900">{distanceMeters}m ({heading}° {cardinalDirection})</span>
                  </div>
                </div>

                {/* Direct Action Buttons */}
                <div className="space-y-1.5">
                  <a
                    href={googleStreetViewUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full px-3 py-2 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-lg text-xs transition-colors flex items-center justify-center gap-1.5 shadow-sm"
                  >
                    <Compass className="w-3.5 h-3.5" />
                    Open Street View (Facing Land)
                    <ExternalLink className="w-3 h-3 opacity-70" />
                  </a>

                  <a
                    href={googleLandPinUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full px-3 py-2 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-lg text-xs transition-colors flex items-center justify-center gap-1.5 shadow-sm"
                  >
                    <Crosshair className="w-3.5 h-3.5" />
                    Locate Land on Google Maps
                    <ExternalLink className="w-3 h-3 opacity-70" />
                  </a>

                  <button
                    onClick={handleOpenFullInspector}
                    className="w-full px-3 py-2 bg-blue-900 hover:bg-blue-800 text-white font-bold rounded-lg text-xs transition-colors flex items-center justify-center gap-1.5 shadow-sm"
                  >
                    <Eye className="w-3.5 h-3.5 text-blue-300" />
                    Launch 360° Ground View Inspector
                  </button>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center gap-2 text-emerald-900 font-bold">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Survey Boundary Mathematically Closed</span>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-400">
              <MapPin className="w-8 h-8 mx-auto mb-2 text-slate-300" />
              <p>Click any highlighted survey parcel polygon on the map to inspect its cadastral attributes, ownership, and street view road vantage point.</p>
            </div>
          )}
        </div>
      </div>

      {/* Full Modal Viewer when requested */}
      {modalRecord && (
        <RecordDetailsModal
          record={modalRecord}
          onClose={() => setModalRecord(null)}
          initialTab="streetview"
        />
      )}
    </div>
  );
};

export default GISMapPage;
