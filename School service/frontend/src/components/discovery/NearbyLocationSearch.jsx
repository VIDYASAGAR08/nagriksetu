import React, { useState } from 'react'

/**
 * Verified Karnataka District & Taluk Reference Centers for accurate manual resolution.
 */
export const KARNATAKA_LOCATION_RESOLVER = {
  'Bengaluru Urban': {
    lat: 12.9716,
    lon: 77.5946,
    taluks: {
      'Bengaluru North / Malleshwaram': { lat: 13.0076, lon: 77.5684 },
      'Bengaluru South / Basavanagudi': { lat: 12.9416, lon: 77.5658 },
      'Bengaluru East / Vasanth Nagar': { lat: 12.9904, lon: 77.5898 },
      'Bengaluru Central / MG Road': { lat: 12.9756, lon: 77.6066 },
      'RR Nagar / Kengeri / Mysore Road': { lat: 12.9237, lon: 77.4987 },
      'Mathikere / MSR Nagar': { lat: 13.0312, lon: 77.5651 },
    }
  },
  'Mysuru': {
    lat: 12.2958,
    lon: 76.6394,
    taluks: {
      'Mysuru City / Gokulam': { lat: 12.3352, lon: 76.6341 },
      'Kuvempunagar': { lat: 12.2856, lon: 76.6267 },
      'Manasagangotri': { lat: 12.3117, lon: 76.6186 },
      'Hunsur': { lat: 12.3082, lon: 76.2872 },
      'Nanjangud': { lat: 12.1197, lon: 76.6806 },
    }
  },
  'Belagavi': {
    lat: 15.8497,
    lon: 74.4977,
    taluks: {
      'Belagavi City / Civil Lines': { lat: 15.8647, lon: 74.5097 },
      'Tilakwadi': { lat: 15.8361, lon: 74.5028 },
      'Chikkodi': { lat: 16.4300, lon: 74.5975 },
      'Gokak': { lat: 16.1667, lon: 74.8333 },
    }
  },
  'Dharwad': {
    lat: 15.4589,
    lon: 75.0078,
    taluks: {
      'Dharwad City / KCD Circle': { lat: 15.4589, lon: 75.0078 },
      'Saptapur': { lat: 15.4526, lon: 74.9924 },
      'Hubballi Vidyanagar': { lat: 15.3686, lon: 75.1219 },
      'Navalgund': { lat: 15.5667, lon: 75.3667 },
    }
  },
  'Vijayapura': {
    lat: 16.8302,
    lon: 75.7100,
    taluks: {
      'Vijayapura City / Station Road': { lat: 16.8302, lon: 75.7100 },
      'Indi': { lat: 17.1833, lon: 75.9667 },
      'Muddebihal': { lat: 16.3333, lon: 76.1333 },
    }
  },
  'Ballari': {
    lat: 15.1394,
    lon: 76.9214,
    taluks: {
      'Ballari Cantonment': { lat: 15.1394, lon: 76.9214 },
      'Infantry Road': { lat: 15.1528, lon: 76.9192 },
      'Siruguppa': { lat: 15.6333, lon: 76.9000 },
      'Hospete': { lat: 15.2689, lon: 76.3909 },
    }
  },
  'Shivamogga': {
    lat: 13.9299,
    lon: 75.5681,
    taluks: {
      'Shivamogga Sagar Road': { lat: 13.9299, lon: 75.5681 },
      'Gopala Gowda Extension': { lat: 13.9142, lon: 75.5847 },
      'Bhadravathi': { lat: 13.8400, lon: 75.7000 },
      'Sagara': { lat: 14.1667, lon: 75.0333 },
    }
  },
  'Udupi': {
    lat: 13.3409,
    lon: 74.7421,
    taluks: {
      'Udupi City Bus Stand': { lat: 13.3409, lon: 74.7421 },
      'Car Street': { lat: 13.3422, lon: 74.7516 },
      'Kundapura': { lat: 13.6267, lon: 74.6933 },
      'Karkala': { lat: 13.2000, lon: 74.9900 },
      'Manipal': { lat: 13.3525, lon: 74.7928 },
    }
  },
  'Tumakuru': {
    lat: 13.3420,
    lon: 77.1017,
    taluks: {
      'Tumakuru BH Road': { lat: 13.3420, lon: 77.1017 },
      'Gandhi Nagar': { lat: 13.3384, lon: 77.1082 },
      'Tiptur': { lat: 13.2600, lon: 76.4800 },
      'Kunigal': { lat: 13.0200, lon: 77.0300 },
    }
  },
  'Kalaburagi': {
    lat: 17.3297,
    lon: 76.8343,
    taluks: {
      'Sedam Road': { lat: 17.3297, lon: 76.8343 },
      'Aiwan-E-Shahi': { lat: 17.3361, lon: 76.8285 },
      'Aland': { lat: 17.5667, lon: 76.5667 },
      'Chittapur': { lat: 17.1167, lon: 77.0833 },
    }
  },
  'Mandya': {
    lat: 12.5242,
    lon: 76.8958,
    taluks: {
      'Mandya VV Road': { lat: 12.5242, lon: 76.8958 },
      'Maddur': { lat: 12.5833, lon: 77.0500 },
      'Srirangapatna': { lat: 12.4181, lon: 76.6947 },
    }
  },
  'Hassan': {
    lat: 13.0072,
    lon: 76.1026,
    taluks: {
      'Hassan BM Road': { lat: 13.0072, lon: 76.1026 },
      'Arsikere': { lat: 13.3100, lon: 76.2600 },
      'Channarayapatna': { lat: 12.9000, lon: 76.3900 },
      'Sakleshpur': { lat: 12.9700, lon: 75.7800 },
    }
  }
}

export default function NearbyLocationSearch({
  locationState,
  onLocationChange,
  radiusKm,
  onRadiusChange,
  onClearLocation,
}) {
  const [mode, setMode] = useState('gps') // 'gps' | 'manual'
  const [detecting, setDetecting] = useState(false)
  const [locationError, setLocationError] = useState(null)
  const [customRadiusInput, setCustomRadiusInput] = useState('')
  const [showCustomInput, setShowCustomInput] = useState(false)

  // Manual Form States
  const [manualState, setManualState] = useState('Karnataka')
  const [manualDistrict, setManualDistrict] = useState('')
  const [manualTaluk, setManualTaluk] = useState('')
  const [manualLocality, setManualLocality] = useState('')

  const radiusPresets = [1, 2, 5, 10, 15, 25]

  // Native GPS Detection using Browser Geolocation API
  function handleUseCurrentLocation() {
    setLocationError(null)

    if (!('geolocation' in navigator)) {
      setLocationError({
        title: 'Geolocation Not Supported',
        message: 'Your current browser or device does not support automatic location detection. Please use Search Manually below.',
        canFallback: true,
      })
      return
    }

    setDetecting(true)

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setDetecting(false)
        const lat = pos.coords.latitude
        const lon = pos.coords.longitude

        // Store only in ephemeral component state (do not persist permanently)
        onLocationChange({
          source: 'gps',
          latitude: lat,
          longitude: lon,
          label: `GPS Device Location (${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E)`,
          accuracy: pos.coords.accuracy ? Math.round(pos.coords.accuracy) : null,
        })
      },
      (err) => {
        setDetecting(false)
        let errorMsg = 'Unable to determine location. Please try again or search manually.'
        if (err.code === 1) { // PERMISSION_DENIED
          errorMsg = 'Location permission was denied. Please allow location access in your browser settings or choose "Search Manually" below.'
        } else if (err.code === 2) { // POSITION_UNAVAILABLE
          errorMsg = 'Device location is currently unavailable. Please check your GPS/network settings or search manually.'
        } else if (err.code === 3) { // TIMEOUT
          errorMsg = 'Location request timed out. Please retry or search manually.'
        }
        setLocationError({
          title: 'Location Request Failed',
          message: errorMsg,
          canFallback: true,
        })
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000,
      }
    )
  }

  // Handle Manual Selection Submission
  function handleManualSearchSubmit(e) {
    e.preventDefault()
    setLocationError(null)

    if (!manualDistrict) {
      setLocationError({
        title: 'District Required',
        message: 'Please select a District to search nearby institutions.',
      })
      return
    }

    const distData = KARNATAKA_LOCATION_RESOLVER[manualDistrict]
    if (!distData) {
      setLocationError({
        title: 'Coordinates Not Found',
        message: `Verified physical coordinates are not available for ${manualDistrict}. Please select another verified district.`,
      })
      return
    }

    let lat = distData.lat
    let lon = distData.lon
    let label = `${manualDistrict}, ${manualState}`

    if (manualTaluk && distData.taluks && distData.taluks[manualTaluk]) {
      lat = distData.taluks[manualTaluk].lat
      lon = distData.taluks[manualTaluk].lon
      label = `${manualTaluk}, ${manualDistrict}`
    } else if (manualLocality.trim()) {
      label = `${manualLocality.trim()}, ${manualDistrict}`
    }

    onLocationChange({
      source: 'manual',
      latitude: lat,
      longitude: lon,
      label,
      district: manualDistrict,
      taluk: manualTaluk || null,
      locality: manualLocality.trim() || null,
    })
  }

  function handleRadiusSelect(val) {
    setShowCustomInput(false)
    onRadiusChange(val)
  }

  function handleCustomRadiusSubmit(e) {
    e.preventDefault()
    const r = parseFloat(customRadiusInput)
    if (!isNaN(r) && r > 0 && r <= 500) {
      onRadiusChange(r)
      setShowCustomInput(false)
    } else {
      setLocationError({
        title: 'Invalid Radius',
        message: 'Please enter a valid search radius between 0.5 km and 500 km.',
      })
    }
  }

  return (
    <div style={{
      background: '#FFFFFF',
      border: '1px solid #D0D5DD',
      borderRadius: '12px',
      padding: '1.5rem',
      marginBottom: '2rem',
      boxShadow: '0 2px 4px rgba(16,43,70,0.06)'
    }}>
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <span style={{ fontSize: '1.35rem' }}>📍</span>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
              Find institutions near you
            </h2>
          </div>
          <p style={{ color: '#475467', margin: 0, fontSize: '0.92rem' }}>
            Discover educational institutions based on your physical location with verified distance calculations.
          </p>
        </div>

        {/* Tab switcher: GPS vs Manual */}
        <div style={{ display: 'inline-flex', background: '#F2F4F7', padding: '0.25rem', borderRadius: '8px' }}>
          <button
            type="button"
            onClick={() => { setMode('gps'); setLocationError(null); }}
            style={{
              padding: '0.4rem 0.85rem',
              borderRadius: '6px',
              border: 'none',
              background: mode === 'gps' ? '#FFFFFF' : 'transparent',
              color: mode === 'gps' ? '#102B46' : '#667085',
              fontWeight: 700,
              fontSize: '0.82rem',
              cursor: 'pointer',
              boxShadow: mode === 'gps' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              transition: 'all 0.15s ease'
            }}
          >
            📡 Use GPS
          </button>
          <button
            type="button"
            onClick={() => { setMode('manual'); setLocationError(null); }}
            style={{
              padding: '0.4rem 0.85rem',
              borderRadius: '6px',
              border: 'none',
              background: mode === 'manual' ? '#FFFFFF' : 'transparent',
              color: mode === 'manual' ? '#102B46' : '#667085',
              fontWeight: 700,
              fontSize: '0.82rem',
              cursor: 'pointer',
              boxShadow: mode === 'manual' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              transition: 'all 0.15s ease'
            }}
          >
            🗺️ Search Manually
          </button>
        </div>
      </div>

      {/* Error / Alert Display */}
      {locationError && (
        <div style={{
          background: '#FEF3F2',
          border: '1px solid #FECDCA',
          borderRadius: '8px',
          padding: '0.75rem 1rem',
          marginBottom: '1rem',
          color: '#B42318',
          fontSize: '0.85rem'
        }}>
          <strong>{locationError.title}: </strong>{locationError.message}
          {locationError.canFallback && mode === 'gps' && (
            <div style={{ marginTop: '0.5rem' }}>
              <button
                type="button"
                onClick={() => { setMode('manual'); setLocationError(null); }}
                style={{
                  background: '#B42318',
                  color: '#FFFFFF',
                  border: 'none',
                  padding: '0.25rem 0.65rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                Switch to Search Manually →
              </button>
            </div>
          )}
        </div>
      )}

      {/* Mode 1: GPS Detection */}
      {mode === 'gps' && (
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
          <button
            type="button"
            disabled={detecting}
            onClick={handleUseCurrentLocation}
            style={{
              background: '#155EEF',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '8px',
              padding: '0.65rem 1.25rem',
              fontSize: '0.92rem',
              fontWeight: 700,
              cursor: detecting ? 'not-allowed' : 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              boxShadow: '0 1px 2px rgba(16,24,40,0.05)'
            }}
          >
            {detecting ? (
              <>⏳ Detecting Device Location...</>
            ) : (
              <>🎯 Use My Current Location</>
            )}
          </button>

          <span style={{ fontSize: '0.82rem', color: '#667085' }}>
            Requires browser location permission. Coordinates are never permanently stored.
          </span>
        </div>
      )}

      {/* Mode 2: Manual Search Form */}
      {mode === 'manual' && (
        <form onSubmit={handleManualSearchSubmit} style={{ marginBottom: '1.25rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem', alignItems: 'end' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#344054', marginBottom: '0.25rem' }}>
                State
              </label>
              <input
                type="text"
                disabled
                value={manualState}
                style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #D0D5DD', background: '#F8F9FA', fontSize: '0.85rem' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#344054', marginBottom: '0.25rem' }}>
                District *
              </label>
              <select
                value={manualDistrict}
                onChange={(e) => {
                  setManualDistrict(e.target.value)
                  setManualTaluk('')
                }}
                required
                style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.85rem', background: '#FFF' }}
              >
                <option value="">Select District...</option>
                {Object.keys(KARNATAKA_LOCATION_RESOLVER).sort().map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#344054', marginBottom: '0.25rem' }}>
                City / Taluk / Zone
              </label>
              <select
                value={manualTaluk}
                disabled={!manualDistrict || !KARNATAKA_LOCATION_RESOLVER[manualDistrict]?.taluks}
                onChange={(e) => setManualTaluk(e.target.value)}
                style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.85rem', background: manualDistrict ? '#FFF' : '#F8F9FA' }}
              >
                <option value="">Select Taluk / Area...</option>
                {manualDistrict && KARNATAKA_LOCATION_RESOLVER[manualDistrict]?.taluks &&
                  Object.keys(KARNATAKA_LOCATION_RESOLVER[manualDistrict].taluks).map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))
                }
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#344054', marginBottom: '0.25rem' }}>
                Locality / Landmark
              </label>
              <input
                type="text"
                placeholder="e.g. Near Bus Stand, Campus"
                value={manualLocality}
                onChange={(e) => setManualLocality(e.target.value)}
                style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.85rem' }}
              />
            </div>

            <div>
              <button
                type="submit"
                style={{
                  width: '100%',
                  background: '#102B46',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '0.6rem 1rem',
                  fontSize: '0.85rem',
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                🔍 Apply Location
              </button>
            </div>
          </div>
        </form>
      )}

      {/* Active Location Info & Radius Controls */}
      {locationState?.latitude != null && (
        <div style={{
          background: '#EFF8FF',
          border: '1px solid #B2DDFF',
          borderRadius: '8px',
          padding: '0.85rem 1rem',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{
                background: '#155EEF',
                color: '#FFF',
                fontSize: '0.68rem',
                fontWeight: 700,
                padding: '0.15rem 0.45rem',
                borderRadius: '4px',
                textTransform: 'uppercase'
              }}>
                {locationState.source === 'gps' ? 'GPS Active' : 'Manual Location'}
              </span>
              <strong style={{ color: '#175CD3', fontSize: '0.92rem' }}>
                {locationState.label}
              </strong>
            </div>
            <div style={{ fontSize: '0.76rem', color: '#475467', marginTop: '0.2rem' }}>
              Latitude: {locationState.latitude.toFixed(4)}°N, Longitude: {locationState.longitude.toFixed(4)}°E
              {locationState.accuracy && ` · Accuracy: ±${locationState.accuracy}m`}
            </div>
          </div>

          {/* Search Radius Controls */}
          <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.4rem' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#344054', marginRight: '0.25rem' }}>
              Search Radius:
            </span>
            {radiusPresets.map(r => (
              <button
                key={r}
                type="button"
                onClick={() => handleRadiusSelect(r)}
                style={{
                  background: radiusKm === r && !showCustomInput ? '#155EEF' : '#FFFFFF',
                  color: radiusKm === r && !showCustomInput ? '#FFFFFF' : '#344054',
                  border: '1px solid #D0D5DD',
                  padding: '0.25rem 0.55rem',
                  borderRadius: '6px',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                {r} km
              </button>
            ))}
            <button
              type="button"
              onClick={() => setShowCustomInput(s => !s)}
              style={{
                background: showCustomInput || !radiusPresets.includes(radiusKm) ? '#102B46' : '#FFFFFF',
                color: showCustomInput || !radiusPresets.includes(radiusKm) ? '#FFFFFF' : '#344054',
                border: '1px solid #D0D5DD',
                padding: '0.25rem 0.55rem',
                borderRadius: '6px',
                fontSize: '0.78rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Custom {!radiusPresets.includes(radiusKm) ? `(${radiusKm} km)` : ''}
            </button>

            {/* Clear Location Button */}
            <button
              type="button"
              onClick={onClearLocation}
              style={{
                background: '#FEE4E2',
                color: '#B42318',
                border: '1px solid #FECDCA',
                padding: '0.25rem 0.65rem',
                borderRadius: '6px',
                fontSize: '0.78rem',
                fontWeight: 600,
                cursor: 'pointer',
                marginLeft: '0.5rem'
              }}
            >
              ✕ Clear Location
            </button>
          </div>
        </div>
      )}

      {/* Custom Radius Modal / Input Drawer */}
      {showCustomInput && (
        <form onSubmit={handleCustomRadiusSubmit} style={{ marginTop: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#344054' }}>
            Enter custom search radius (km):
          </label>
          <input
            type="number"
            min="0.5"
            max="500"
            step="0.5"
            placeholder="e.g. 7.5"
            value={customRadiusInput}
            onChange={(e) => setCustomRadiusInput(e.target.value)}
            style={{ width: '100px', padding: '0.35rem 0.5rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.85rem' }}
          />
          <button
            type="submit"
            style={{
              background: '#155EEF',
              color: '#FFFFFF',
              border: 'none',
              padding: '0.35rem 0.75rem',
              borderRadius: '6px',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Apply Radius
          </button>
        </form>
      )}
    </div>
  )
}
