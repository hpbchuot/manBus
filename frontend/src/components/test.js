import React, { useState, useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-routing-machine/dist/leaflet-routing-machine.css";
import "leaflet-routing-machine";

function RoutingMachine({ startPoint, endPoint, onRouteFound }) {
  const map = useMap();
  const routingControlRef = useRef(null);

  useEffect(() => {
    if (!startPoint || !endPoint) return;

    if (routingControlRef.current) {
      map.removeControl(routingControlRef.current);
    }

    routingControlRef.current = L.Routing.control({
      waypoints: [
        L.latLng(startPoint[0], startPoint[1]),
        L.latLng(endPoint[0], endPoint[1]),
      ],
      lineOptions: {
        styles: [{ color: "#6FA1EC", weight: 4 }],
      },
      show: false,
      addWaypoints: false,
      routeWhileDragging: false,
      fitSelectedRoutes: true,
      showAlternatives: false,
    }).addTo(map);

    routingControlRef.current.on("routesfound", (e) => {
      const routes = e.routes[0];
      const coordinates = routes.coordinates;

      // Format data for PostgreSQL
      const routeData = {
        linestring: `LINESTRING(${coordinates
          .map((coord) => `${coord.lng} ${coord.lat}`)
          .join(",")})`,
        stops: `MULTIPOINT(${startPoint[1]} ${startPoint[0]}, ${endPoint[1]} ${endPoint[0]})`,
        coordinates: coordinates.map((coord) => [coord.lat, coord.lng]),
      };

      onRouteFound(routeData);
    });

    return () => {
      if (routingControlRef.current) {
        map.removeControl(routingControlRef.current);
      }
    };
  }, [map, startPoint, endPoint]);

  return null;
}

export default function RouteMap() {
  const [startPoint, setStartPoint] = useState([21.0285, 105.8542]); // Hà Nội
  const [endPoint, setEndPoint] = useState([21.1285, 105.8541]); // Ví dụ điểm khác
  const [routeData, setRouteData] = useState(null);

  const handleRouteFound = (data) => {
    setRouteData(data);
    console.log("PostgreSQL Format:", data);
    // Dữ liệu này có thể được gửi đến API của bạn
  };

  const handleReset = () => {
    setStartPoint([21.0285, 105.8542]); // Reset về Hà Nội
    setEndPoint([21.0285, 105.8542]); // Reset về điểm khác
    setRouteData(null);
  };

  const handleMarkerDrag = (e, markerType) => {
    const newPosition = [e.target.getLatLng().lat, e.target.getLatLng().lng];
    if (markerType === "start") {
      setStartPoint(newPosition);
    } else if (markerType === "end") {
      setEndPoint(newPosition);
    }
  };

  return (
    <div>
      <MapContainer
        center={startPoint} // Dùng startPoint để làm vị trí trung tâm ban đầu
        zoom={13}
        style={{ height: "600px", width: "100%", margin: "20px" }}
        scrollWheelZoom={false}
        touchZoom={false}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {startPoint && endPoint && (
          <RoutingMachine
            startPoint={startPoint}
            endPoint={endPoint}
            onRouteFound={handleRouteFound}
          />
        )}
        {/* Marker for start and end */}
        <Marker
          position={startPoint}
          draggable={true} // Enable dragging
          onDragend={(e) => handleMarkerDrag(e, "start")} // Update start point
        >
          <Popup>Start Point</Popup>
        </Marker>
        <Marker
          position={endPoint}
          draggable={true} // Enable dragging
          onDragend={(e) => handleMarkerDrag(e, "end")} // Update end point
        >
          <Popup>End Point</Popup>
        </Marker>
      </MapContainer>

      <div style={{ marginTop: "20px" }}>
        <button onClick={handleReset}>Reset Route</button>
        {routeData && (
          <div style={{ margin: "50px 50px" }}>
            <h3>SQL Insert Format:</h3>
            <pre
              style={{
                background: "#f5f5f5",
                padding: "10px",
                overflow: "auto",
              }}
            >
              {`INSERT INTO road (name, route_geom, stops, current_segment)
VALUES (
  'Route Name',
  ST_GeomFromText('${routeData.linestring}', 4326),
  ST_GeomFromText('${routeData.stops}', 4326),
  1
);`}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
