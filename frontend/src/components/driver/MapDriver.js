import React, { useEffect, useState, useCallback } from "react";
import {
    MapContainer,
    TileLayer,
    Marker,
    Popup,
    useMap,
    ZoomControl,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import "leaflet-routing-machine"; // Sử dụng thư viện này
import "leaflet-routing-machine/dist/leaflet-routing-machine.css"; // Thêm CSS của nó

import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import markerRetina from "leaflet/dist/images/marker-icon-2x.png";
import requestApi from "../../helpers/api";
import { useDispatch, useSelector } from "react-redux";
import * as actions from "../../redux/actions";
import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";

// --- Cấu hình icon (Giữ nguyên) ---
const DefaultIcon = L.icon({
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
    iconRetinaUrl: markerRetina,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

// Component mới để xử lý định tuyến
const RoutingControl = ({ start, end }) => {
    const map = useMap();

    useEffect(() => {
        if (!map || !start || !end) return;

        const routingControl = L.Routing.control({
            waypoints: [L.latLng(start[0], start[1]), L.latLng(end[0], end[1])],
            routeWhileDragging: true,
            createMarker: () => null,
            show: false,
            fitSelectedRoutes: true,
            lineOptions: {
                styles: [{ color: 'blue', opacity: 0.8, weight: 6 }]
            }
        }).addTo(map);

        // Dọn dẹp khi component unmount
        return () => map.removeControl(routingControl);
    }, [map, start, end]);

    return null;
};

// --- Component chính: Đổi tên thành MapDriver ---
const MapDriver = () => { // ĐÃ ĐỔI TÊN
    const { t } = useTranslation();
    const dispatch = useDispatch();
    const mapData = useSelector((state) => state.mapSearch);

    const [routePoints, setRoutePoints] = useState({
        start: null,
        end: null,
    });

    const fetchRouteData = useCallback(async () => {
        if (!mapData.search || !mapData.busNumber) {
            setRoutePoints({ start: null, end: null });
            return;
        }

        try {
            dispatch(actions.controlLoading(true));
            const res = await requestApi(
                `/bus/get-st-end?bus_id=${mapData.busNumber}`,
                "GET"
            );

            const { start, end } = res.data.data;

            if (!start || !end) {
                toast.warn("Dữ liệu điểm đầu/cuối không đầy đủ.");
                setRoutePoints({ start: null, end: null });
            } else {
                setRoutePoints({ start, end });
                toast.success(res.data.message || "Tải tuyến đường thành công");
            }

        } catch (error) {
            setRoutePoints({ start: null, end: null });
            console.log(error);
            if (typeof error.response !== "undefined") {
                if (error.response.status !== 201) {
                    toast.error(error.response.data.message, {
                        position: "top-right",
                        autoClose: 3000,
                    });
                }
            } else {
                toast.error("Server is down. Please try again!", {
                    position: "top-right",
                    autoClose: 3000,
                });
            }
        } finally {
            dispatch(actions.controlLoading(false));
        }
    }, [mapData.search, mapData.busNumber, dispatch]);

    useEffect(() => {
        fetchRouteData();
    }, [fetchRouteData]);

    return (
        <div>
            <MapContainer
                center={[21.0285, 105.8542]}
                zoom={12}
                scrollWheelZoom={true}
                zoomControl={false}
                style={{ height: "100vh", width: "100%" }}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {/* Hiển thị Marker điểm đầu */}
                {routePoints.start && (
                    <Marker position={routePoints.start}>
                        <Popup>{t('map.startPoint') || "Điểm đầu"}</Popup>
                    </Marker>
                )}

                {/* Hiển thị Marker điểm cuối */}
                {routePoints.end && (
                    <Marker position={routePoints.end}>
                        <Popup>{t('map.endPoint') || "Điểm cuối"}</Popup>
                    </Marker>
                )}

                {/* Component RoutingControl */}
                {routePoints.start && routePoints.end && (
                    <RoutingControl start={routePoints.start} end={routePoints.end} />
                )}

                <ZoomControl position="bottomright" />
            </MapContainer>
        </div>
    );
};

export default MapDriver;