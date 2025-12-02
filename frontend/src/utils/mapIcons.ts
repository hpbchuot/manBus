import L from 'leaflet';

// Bus Stop Icon - Màu xanh primary
export const busStopIcon = L.divIcon({
  className: 'custom-bus-stop-icon',
  html: `
    <div style="
      position: relative;
      width: 32px;
      height: 32px;
    ">
      <div style="
        position: absolute;
        top: 0;
        left: 0;
        width: 32px;
        height: 32px;
        background-color: #00C060;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
      ">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
      </div>
    </div>
  `,
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

// Selected Bus Stop Icon - Màu đỏ để highlight
export const selectedBusStopIcon = L.divIcon({
  className: 'custom-bus-stop-icon-selected',
  html: `
    <div style="
      position: relative;
      width: 40px;
      height: 40px;
    ">
      <div style="
        position: absolute;
        top: 0;
        left: 0;
        width: 40px;
        height: 40px;
        background-color: #D32F2F;
        border-radius: 50%;
        border: 4px solid white;
        box-shadow: 0 4px 12px rgba(211,47,47,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        animation: pulse 2s infinite;
      ">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
      </div>
    </div>
    <style>
      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
      }
    </style>
  `,
  iconSize: [40, 40],
  iconAnchor: [20, 40],
  popupAnchor: [0, -40],
});

// Bus Icon - Cho xe buýt đang chạy
export const busIcon = L.divIcon({
  className: 'custom-bus-icon',
  html: `
    <div style="
      position: relative;
      width: 36px;
      height: 36px;
    ">
      <div style="
        position: absolute;
        top: 0;
        left: 0;
        width: 36px;
        height: 36px;
        background-color: #27AE60;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 2px 10px rgba(39,174,96,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
      ">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
          <path d="M4 16c0 .88.39 1.67 1 2.22V20c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h8v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1.78c.61-.55 1-1.34 1-2.22V6c0-3.5-3.58-4-8-4s-8 .5-8 4v10zm3.5 1c-.83 0-1.5-.67-1.5-1.5S6.67 14 7.5 14s1.5.67 1.5 1.5S8.33 17 7.5 17zm9 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm1.5-6H6V6h12v5z"/>
        </svg>
      </div>
    </div>
  `,
  iconSize: [36, 36],
  iconAnchor: [18, 18],
  popupAnchor: [0, -18],
});

// Selected Bus Icon - When user clicks on a bus
export const selectedBusIcon = L.divIcon({
  className: 'custom-bus-icon-selected',
  html: `
    <div style="
      position: relative;
      width: 44px;
      height: 44px;
    ">
      <div style="
        position: absolute;
        top: 0;
        left: 0;
        width: 44px;
        height: 44px;
        background-color: #2196F3;
        border-radius: 50%;
        border: 4px solid white;
        box-shadow: 0 4px 12px rgba(33,150,243,0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        animation: pulse 2s infinite;
      ">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="white">
          <path d="M4 16c0 .88.39 1.67 1 2.22V20c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h8v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1.78c.61-.55 1-1.34 1-2.22V6c0-3.5-3.58-4-8-4s-8 .5-8 4v10zm3.5 1c-.83 0-1.5-.67-1.5-1.5S6.67 14 7.5 14s1.5.67 1.5 1.5S8.33 17 7.5 17zm9 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm1.5-6H6V6h12v5z"/>
        </svg>
      </div>
    </div>
    <style>
      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
      }
    </style>
  `,
  iconSize: [44, 44],
  iconAnchor: [22, 22],
  popupAnchor: [0, -22],
});

// Tracked Bus Icon - When user is following a bus
export const trackedBusIcon = L.divIcon({
  className: 'custom-bus-icon-tracked',
  html: `
    <div style="
      position: relative;
      width: 48px;
      height: 48px;
    ">
      <div style="
        position: absolute;
        top: 0;
        left: 0;
        width: 48px;
        height: 48px;
        background-color: #FF5722;
        border-radius: 50%;
        border: 4px solid white;
        box-shadow: 0 4px 16px rgba(255,87,34,0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        animation: pulse-strong 1.5s infinite;
      ">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
          <path d="M4 16c0 .88.39 1.67 1 2.22V20c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h8v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1.78c.61-.55 1-1.34 1-2.22V6c0-3.5-3.58-4-8-4s-8 .5-8 4v10zm3.5 1c-.83 0-1.5-.67-1.5-1.5S6.67 14 7.5 14s1.5.67 1.5 1.5S8.33 17 7.5 17zm9 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm1.5-6H6V6h12v5z"/>
        </svg>
      </div>
    </div>
    <style>
      @keyframes pulse-strong {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.15); }
      }
    </style>
  `,
  iconSize: [48, 48],
  iconAnchor: [24, 24],
  popupAnchor: [0, -24],
});

// Cluster Icon - Khi nhiều stops gần nhau
export const createClusterIcon = (count: number) => L.divIcon({
  className: 'custom-cluster-icon',
  html: `
    <div style="
      width: 40px;
      height: 40px;
      background-color: rgba(0,192,96,0.8);
      border-radius: 50%;
      border: 3px solid white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 14px;
      color: white;
    ">
      ${count}
    </div>
  `,
  iconSize: [40, 40],
  iconAnchor: [20, 20],
});