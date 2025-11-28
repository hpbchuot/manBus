import { type LatLngExpression } from 'leaflet';

export const MAP_CONFIG = {
  // Tọa độ mặc định (Ví dụ: Hà Nội)
  DEFAULT_CENTER: [21.0285, 105.8542] as LatLngExpression,
  DEFAULT_ZOOM: 14,
  // Tile Layer theo phong cách Clean UI (CartoDB Voyager)
  TILE_LAYER: {
    url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
  },
};