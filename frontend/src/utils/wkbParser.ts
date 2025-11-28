

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export function parseWKBPoint(
  wkb: string | Coordinates | undefined
): Coordinates {
  // Nếu undefined hoặc null
  if (!wkb) {
    console.warn('WKB is undefined or null');
    return { latitude: 0, longitude: 0 };
  }

  // Nếu đã là object với lat/lng
  if (typeof wkb === 'object' && 'latitude' in wkb && 'longitude' in wkb) {
    return {
      latitude: wkb.latitude,
      longitude: wkb.longitude,
    };
  }

  // Parse WKB hex string
  if (typeof wkb === 'string') {
    // Kiểm tra format WKB hex
    if (wkb.startsWith('0101000020')) {
      return parseWKBHex(wkb);
    }

    // Fallback: Thử parse JSON nếu có thể
    try {
      const parsed = JSON.parse(wkb);
      if (parsed.latitude !== undefined && parsed.longitude !== undefined) {
        return parsed;
      }
    } catch {
      // Not JSON
    }

    console.error('Cannot parse WKB:', wkb);
    return { latitude: 0, longitude: 0 };
  }

  console.error('Unknown WKB format:', wkb);
  return { latitude: 0, longitude: 0 };
}

function parseWKBHex(hex: string): Coordinates {
  try {
    // WKB Point format (Little Endian with SRID):
    // 01 - Byte order (Little Endian)
    // 01000020 - Geometry type (Point with SRID)
    // E6100000 - SRID (4326 = WGS84)
    // Next 8 bytes (16 hex chars) - X coordinate (longitude)
    // Next 8 bytes (16 hex chars) - Y coordinate (latitude)

    // Skip first 9 bytes (18 hex chars): 0101000020E6100000
    const lngHex = hex.substring(18, 34); // 16 chars
    const latHex = hex.substring(34, 50); // 16 chars

    const longitude = hexToDouble(lngHex);
    const latitude = hexToDouble(latHex);

    // Validation
    if (
      isNaN(longitude) ||
      isNaN(latitude) ||
      longitude < -180 ||
      longitude > 180 ||
      latitude < -90 ||
      latitude > 90
    ) {
      console.error('Invalid coordinates after parsing:', { latitude, longitude });
      return { latitude: 0, longitude: 0 };
    }

    return { latitude, longitude };
  } catch (error) {
    console.error('Error parsing WKB hex:', error);
    return { latitude: 0, longitude: 0 };
  }
}

function hexToDouble(hex: string): number {
  // Convert hex string to IEEE 754 double precision float
  // Split into bytes (2 hex chars = 1 byte)
  const bytes = hex.match(/.{1,2}/g);
  if (!bytes || bytes.length !== 8) {
    throw new Error('Invalid hex length for double');
  }

  const byteArray = new Uint8Array(bytes.map((byte) => parseInt(byte, 16)));
  const dataView = new DataView(byteArray.buffer);

  // Read as Little Endian double (8 bytes)
  return dataView.getFloat64(0, true);
}

/**
 * Convert coordinates to WKB hex string (reverse operation)
 * Useful for API requests
 */
export function coordinatesToWKB(lat: number, lng: number): string {
  const buffer = new ArrayBuffer(25);
  const view = new DataView(buffer);

  // Byte order (Little Endian)
  view.setUint8(0, 0x01);

  // Geometry type (Point with SRID)
  view.setUint32(1, 0x20000001, true);

  // SRID (4326 = WGS84)
  view.setUint32(5, 4326, true);

  // X coordinate (longitude)
  view.setFloat64(9, lng, true);

  // Y coordinate (latitude)
  view.setFloat64(17, lat, true);

  // Convert to hex string
  const array = new Uint8Array(buffer);
  return Array.from(array)
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('')
    .toUpperCase();
}

/**
 * Test function to verify parsing
 */
export function testWKBParser() {
  // Test case từ API response
  const testWKB = '0101000020E61000009E996038D7755A40FE4465C39A063540';
  const result = parseWKBPoint(testWKB);
  console.log('Test WKB Parser:', result);
  // Expected: latitude ≈ 21.028, longitude ≈ 105.854 (Hà Nội)
}