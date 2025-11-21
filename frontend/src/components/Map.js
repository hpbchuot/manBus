// import React, { useEffect, useState } from "react";
// import {
//   MapContainer,
//   TileLayer,
//   Marker,
//   Popup,
//   useMap,
//   ZoomControl,
// } from "react-leaflet";
// import "leaflet/dist/leaflet.css";
// import L, { map } from "leaflet";
// import "leaflet-routing-machine";
// import markerIcon from "leaflet/dist/images/marker-icon.png";
// import markerShadow from "leaflet/dist/images/marker-shadow.png";
// import markerRetina from "leaflet/dist/images/marker-icon-2x.png";
// import requestApi from "../helpers/api";
// import { useDispatch, useSelector } from "react-redux";
// import { useQuery, useMutation } from "@tanstack/react-query";
// import * as actions from "../redux/actions";
// import { toast } from "react-toastify";
// import { Modal, Box, Typography, TextField, Button } from "@mui/material";
// import { useTranslation } from "react-i18next";
// // Cấu hình icon cho Marker
// const DefaultIcon = L.icon({
//   iconUrl: markerIcon,
//   shadowUrl: markerShadow,
//   iconRetinaUrl: markerRetina,
//   iconSize: [25, 41],
//   iconAnchor: [12, 41],
//   popupAnchor: [1, -34],
//   shadowSize: [41, 41],
// });
// const busIcon = L.icon({
//   iconUrl: "https://cdn-icons-png.flaticon.com/512/1819/1819616.png", // Đường dẫn đến biểu tượng xe buýt
//   iconSize: [40, 40], // Kích thước icon
//   iconAnchor: [15, 15], // Điểm neo của icon (giữa icon)
//   popupAnchor: [0, -15], // Điểm neo của popup (nếu có)
// });
// L.Marker.prototype.options.icon = DefaultIcon;

// const Routing = ({ startLatLng, endLatLng, bid }) => {
//   const map = useMap();
//   console.log("j", startLatLng, endLatLng);
//   useEffect(() => {
//     const routingControl = L.Routing.control({
//       waypoints: [
//         L.latLng(startLatLng), // Hà Nội
//         L.latLng(endLatLng), // TP.HCM
//       ],
//       routeWhileDragging: true,
//       show: false, // Tắt chỉ dẫn
//     }).addTo(map);

//     let movingMarker;

//     const updateMarkerPosition = async () => {
//       requestApi("/map/get-location", "POST", { id: bid })
//         .then((res) => {
//           if (res.data.lat && res.data.lng) {
//             if (!movingMarker) {
//               // Tạo marker nếu chưa có
//               movingMarker = L.marker([res.data.lat, res.data.lng], {
//                 icon: busIcon,
//               }).addTo(map);
//             } else {
//               // Cập nhật vị trí marker
//               movingMarker.setLatLng([res.data.lat, res.data.lng]);
//               //console.log(res);
//             }
//           } else {
//             console.warn("Dữ liệu API không đầy đủ:", res);
//           }
//         })
//         .catch((err) => {
//           console.log(err);
//         });
//     };

//     // Lặp lại việc gọi API sau mỗi 2 giây
//     const intervalId = setInterval(updateMarkerPosition, 2200);

//     return () => {
//       map.removeControl(routingControl); // Hủy control khi component unmount
//       clearInterval(intervalId); // Dừng lặp khi component unmount
//       if (movingMarker) {
//         map.removeLayer(movingMarker); // Xóa marker khi unmount
//       }
//     };
//   }, [map]);
//   useEffect(() => {
//     if (startLatLng && endLatLng) {
//       const latLngBounds = L.latLngBounds(
//         L.latLng(startLatLng),
//         L.latLng(endLatLng)
//       );
//       map.fitBounds(latLngBounds); // Adjust map to fit bounds
//     }
//   }, [startLatLng, endLatLng]);
//   return null;
// };

// let go = false;
// const Map = () => {
//   const [startLatLng, setStartLatLng] = useState(null);
//   const [endLatLng, setEndLatLng] = useState(null);
//   const [open, setOpen] = useState(false);
//   const [feedback, setFeedback] = useState("");
//   const [isLoggedIn, setIsLoggedIn] = useState(false);

//   const handleOpen = () => setOpen(true);
//   const handleClose = () => setOpen(false);
//   const mapData = useSelector((state) => state.mapSearch);
//   const { t } = useTranslation();
//   //console.log("map", mapData);
//   const dispatch = useDispatch();
//   useEffect(() => {
//     const token = localStorage.getItem("access_token") || false;
//     setIsLoggedIn(!!token);
//     if (mapData.search) {
//       try {
//         dispatch(actions.controlLoading(true));
//         requestApi(`/bus/get-st-end?bus_id=${mapData.busNumber}`, "GET").then(
//           (res) => {
//             console.log(res);
//             go = true;
//             setStartLatLng(res.data.data.start);
//             setEndLatLng(res.data.data.end);
//             console.log("ennd;st", startLatLng, endLatLng);
//             toast.success(res.data.message, {
//               position: "top-right",
//               autoClose: 3000,
//             });
//             dispatch(actions.controlLoading(false));
//           }
//         );
//       } catch (error) {
//         dispatch(actions.controlLoading(false));
//         console.log(error);
//         if (typeof error.response !== "undefined") {
//           if (error.response.status !== 201) {
//             toast.error(error.response.data.message, {
//               position: "top-right",
//               autoClose: 3000,
//             });
//           }
//         } else {
//           toast.error("Server is down. Please try again!", {
//             position: "top-right",
//             autoClose: 3000,
//           });
//         }
//       }
//     }
//   }, [mapData]);
//   // const { data, error, isLoading } = useQuery({
//   //   queryKey: ["getStEndOfBus"],
//   //   queryFn: getStEndOfBus(mapData.busNumber),
//   //   enabled: go,
//   // });
//   const handleStopSearch = () => {
//     go = false;
//     setStartLatLng(null);
//     setEndLatLng(null);
//     const searchData = {
//       search: false,
//     };
//     dispatch(actions.setSharedData(searchData));
//     toast.info("Search stopped.", {
//       position: "top-right",
//       autoClose: 3000,
//     });
//   };

//   const mutation = useMutation({
//     mutationFn: async (data) => {
//       try {
//         const response = await requestApi("/feedback/add", "POST", data);
//         return response; // Ensure this returns the response correctly
//       } catch (error) {
//         throw error; // Rethrow the error to be handled in onError
//       }
//     },
//     onSuccess: (response) => {
//       toast.success(response.data.message, {
//         position: "top-right",
//         autoClose: 3000,
//       });
//       console.log("Feedback gửi thành công:", response);
//       setFeedback(""); // Reset form
//       handleClose();
//     },
//     onError: (error) => {
//       console.error("Lỗi khi gửi feedback:", error);
//     },
//   });

//   const handleSubmit = () => {
//     const data = {
//       content: feedback,
//       bus_id: mapData.busNumber,
//     };
//     mutation.mutate(data);
//   };
//   const modalStyle = {
//     position: "fixed",
//     bottom: 20,
//     right: 20,
//     width: 350,
//     bgcolor: "background.paper",
//     boxShadow: 24,
//     p: 3,
//     borderRadius: "8px",
//   };
//   return (
//     <div>
//       <MapContainer
//         center={[21.0285, 105.8542]} // Trung tâm bản đồ giữa Hà Nội và TP.HCM
//         zoom={12}
//         scrollWheelZoom={true}
//         zoomControl={false}
//         style={{ height: "100vh", width: "100%" }}
//       >
//         <TileLayer
//           attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
//           url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
//         />
//         {/* Routing component */}
//         {go && (
//           <Routing
//             startLatLng={startLatLng}
//             endLatLng={endLatLng}
//             bid={mapData.busNumber}
//           />
//         )}
//         <ZoomControl position="bottomright" />
//       </MapContainer>
//       {go && (
//         <Box
//           sx={{
//             position: "absolute",
//             bottom: "20px",
//             left: "50%",
//             transform: "translateX(-50%)", // Center horizontally
//             zIndex: 1000, // Ensure the button is above the map
//           }}
//         >
//           <Button
//             variant="contained"
//             color="error"
//             onClick={handleStopSearch}
//             sx={{ padding: "10px 20px" }}
//           >
//             {t("Stop")}
//           </Button>
//           {isLoggedIn && (
//             <Button
//               variant="contained"
//               color="success"
//               onClick={handleOpen}
//               sx={{ ml: 1, padding: "10px 20px" }}
//             >
//               {t("Feedback")}
//             </Button>
//           )}
//         </Box>
//       )}

//       <Modal open={open} onClose={handleClose} aria-labelledby="feedback-modal">
//         <Box sx={modalStyle}>
//           <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
//             {t("SendFeedback")}
//           </Typography>
//           <TextField
//             fullWidth
//             multiline
//             rows={4}
//             variant="outlined"
//             placeholder="Nhập đánh giá của bạn..."
//             value={feedback}
//             onChange={(e) => setFeedback(e.target.value)}
//             disabled={mutation.isLoading}
//           />
//           <Box sx={{ mt: 2, textAlign: "right" }}>
//             <Button onClick={handleClose} sx={{ mr: 1 }}>
//               {t("cancel")}
//             </Button>
//             <Button variant="contained" color="success" onClick={handleSubmit}>
//               {mutation.isLoading ? t("isLoading") : t("send")}
//             </Button>
//           </Box>
//         </Box>
//       </Modal>
//     </div>
//   );
// };

// export default Map;
// components/Map.jsx

// import React, { useEffect, useState, useCallback, useMemo } from "react";
// import {
//   MapContainer,
//   TileLayer,
//   Marker,
//   Popup,
//   useMap,
//   ZoomControl,
//   Polyline,
// } from "react-leaflet";
// import ControlPanel from "./ControlPanel";
// import "leaflet/dist/leaflet.css";
// import L from "leaflet";
// import "leaflet-routing-machine";
// import { useDispatch, useSelector } from "react-redux";
// import { useMutation, useQuery } from "@tanstack/react-query";
// import * as actions from "../redux/actions";
// import { toast } from "react-toastify";
// import { Modal, Box, Typography, TextField, Button } from "@mui/material";
// import { useTranslation } from "react-i18next";
// import { ICONS } from "../constansts/mapIcons";
// import requestApi from "../helpers/api";
// // Custom hook để quản lý bus tracking
// const modalStyles = {
//   position: "fixed",
//   bottom: 20,
//   right: 20,
//   width: 350,
//   bgcolor: "background.paper",
//   boxShadow: 24,
//   p: 3,
//   borderRadius: "8px",
// };
// const useBusTracking = (busId, isTracking) => {
//   const [currentPosition, setCurrentPosition] = useState(null);
//   const [routeHistory, setRouteHistory] = useState([]);
//   const [reachedEnd, setReachedEnd] = useState(false);

//   const resetTracking = useCallback(() => {
//     setCurrentPosition(null);
//     setRouteHistory([]);
//     setReachedEnd(false);
//   }, []);
//   useEffect(() => {
//     if (!isTracking || !busId) {
//       resetTracking();
//       return;
//     }

//     const updatePosition = async () => {
//       try {
//         const response = await requestApi("/map/get-location", "POST", {
//           id: busId,
//         });
//         const { lat, lng } = response.data;

//         if (lat && lng) {
//           const newPosition = [lat, lng];
//           setCurrentPosition(newPosition);

//           // Chỉ thêm vào history nếu chưa đến điểm cuối
//           if (!reachedEnd) {
//             setRouteHistory((prev) => [...prev, newPosition]);
//           }
//         }
//       } catch (error) {
//         console.error("Error tracking bus:", error);
//       }
//     };

//     const intervalId = setInterval(updatePosition, 2000);
//     return () => {
//       clearInterval(intervalId);
//     };
//   }, [busId, isTracking, reachedEnd]);

//   return {
//     currentPosition,
//     routeHistory,
//     resetTracking,
//     reachedEnd,
//     setReachedEnd,
//   };
// };
// // BusRoute component để hiển thị đường đi
// const BusRoute = ({
//   startPoint,
//   endPoint,
//   currentPosition,
//   routeHistory,
//   onReset,
// }) => {
//   const map = useMap();
//   const [routingControl, setRoutingControl] = useState(null);
//   const [plannedRoute, setPlannedRoute] = useState([]);
//   const cleanup = useCallback(() => {
//     if (routingControl) {
//       console.log("aaa");
//       map.removeControl(routingControl);
//       setRoutingControl(null);
//     }
//     setPlannedRoute([]);
//   }, [routingControl, map]);
//   // Initialize routing
//   useEffect(() => {
//     if (startPoint && endPoint) {
//       //cleanup(); // Cleanup previous routing
//       const control = L.Routing.control({
//         waypoints: [L.latLng(startPoint), L.latLng(endPoint)],
//         routeWhileDragging: false,
//         addWaypoints: false,
//         draggableWaypoints: false,
//         fitSelectedRoutes: true,
//         show: false,
//         lineOptions: {
//           styles: [
//             { color: "gray", opacity: 0.6, weight: 4, dashArray: "10, 10" },
//           ],
//         },
//       }).addTo(map);

//       control.on("routesfound", (e) => {
//         const coordinates = e.routes[0].coordinates;
//         setPlannedRoute(coordinates);
//       });

//       setRoutingControl(control);

//       // Fit bounds
//       const bounds = L.latLngBounds([startPoint, endPoint]);
//       map.fitBounds(bounds, { padding: [50, 50] });
//     }

//     return cleanup;
//   }, [startPoint, endPoint, map, cleanup]);
//   // Check if bus has reached end point
//   useEffect(() => {
//     if (currentPosition && endPoint) {
//       const distance = L.latLng(currentPosition).distanceTo(L.latLng(endPoint));
//       if (distance < 50) {
//         // 50 meters threshold
//         onReset();
//       }
//     }
//   }, [currentPosition, endPoint, onReset]);
//   // Hiển thị đường đã đi (solid line)
//   const completedRoute = useMemo(
//     () =>
//       routeHistory.length > 0 && (
//         <Polyline positions={routeHistory} color="blue" weight={3} />
//       ),
//     [routeHistory]
//   );

//   // Hiển thị đường chưa đi (dashed line)
//   const remainingRoute = useMemo(() => {
//     if (!currentPosition || !plannedRoute.length) return null;

//     // Tìm điểm gần nhất trên planned route với vị trí hiện tại
//     const currentIndex = plannedRoute.findIndex((point, index) => {
//       if (index === plannedRoute.length - 1) return true;
//       const d1 = L.latLng(currentPosition).distanceTo(L.latLng(point));
//       const d2 = L.latLng(currentPosition).distanceTo(
//         L.latLng(plannedRoute[index + 1])
//       );
//       return d1 < d2;
//     });

//     // Lấy phần route còn lại
//     const remainingPoints = plannedRoute.slice(currentIndex);

//     return (
//       <Polyline
//         positions={remainingPoints}
//         color="blue"
//         weight={4}
//         opacity={0.4}
//         dashArray="10, 10"
//       />
//     );
//   }, [currentPosition, plannedRoute]);
//   return (
//     <>
//       {completedRoute}
//       {remainingRoute}
//       {startPoint && (
//         <Marker position={startPoint} icon={ICONS.START}>
//           <Popup>Điểm đầu</Popup>
//         </Marker>
//       )}
//       {endPoint && (
//         <Marker position={endPoint} icon={ICONS.END}>
//           <Popup>Điểm cuối</Popup>
//         </Marker>
//       )}
//       {currentPosition && (
//         <Marker position={currentPosition} icon={ICONS.BUS}>
//           <Popup>Xe bus</Popup>
//         </Marker>
//       )}
//     </>
//   );
// };

// // FeedbackModal component
// const FeedbackModal = ({ open, onClose, busId }) => {
//   const [feedback, setFeedback] = useState("");
//   const { t } = useTranslation();

//   const mutation = useMutation({
//     mutationFn: (data) => requestApi("/feedback/add", "POST", data),
//     onSuccess: (response) => {
//       toast.success(response.data.message);
//       setFeedback("");
//       onClose();
//     },
//     onError: (error) => {
//       toast.error(error.response?.data?.message || "Error sending feedback");
//     },
//   });

//   return (
//     <Modal open={open} onClose={onClose}>
//       <Box sx={modalStyles.container}>{/* Modal content */}</Box>
//     </Modal>
//   );
// };

// // Main Map component
// const Map = () => {
//   const dispatch = useDispatch();
//   const mapData = useSelector((state) => state.mapSearch);
//   const [routePoints, setRoutePoints] = useState({ start: null, end: null });
//   const [isTracking, setIsTracking] = useState(false);
//   const [showFeedback, setShowFeedback] = useState(false);
//   const { t } = useTranslation();

//   const {
//     currentPosition,
//     routeHistory,
//     resetTracking,
//     reachedEnd,
//     setReachedEnd,
//   } = useBusTracking(mapData.busNumber, isTracking);

//   // Fetch route points
//   const fetchRoutePoints = useCallback(async () => {
//     if (!mapData.search) return;

//     try {
//       dispatch(actions.controlLoading(true));
//       const response = await requestApi(
//         `/bus/get-st-end?bus_id=${mapData.busNumber}`,
//         "GET"
//       );
//       console.log(response);
//       setRoutePoints({
//         start: response.data.start,
//         end: response.data.end,
//       });
//       setIsTracking(true);

//       toast.success(response.data.message);
//     } catch (error) {
//       toast.error(error.response?.data?.message || "Error fetching route");
//     } finally {
//       dispatch(actions.controlLoading(false));
//     }
//   }, [mapData.search, mapData.busNumber]);

//   useEffect(() => {
//     fetchRoutePoints();
//   }, [fetchRoutePoints]);
//   const resetAll = useCallback(() => {
//     setIsTracking(false);
//     setRoutePoints({ start: null, end: null });
//     resetTracking();
//     setReachedEnd(false);
//     dispatch(actions.setSharedData({ search: false }));
//   }, [dispatch, resetTracking, setReachedEnd]);
//   const handleStopTracking = useCallback(() => {
//     resetAll();
//     toast.info(t("SearchStopped"));
//   }, [resetAll, t]);
//   const handleReset = useCallback(() => {
//     setRoutePoints({ start: null, end: null });
//     setIsTracking(false);
//     // Reset other states if needed
//   }, []);

//   return (
//     <div
//       style={{
//         position: "relative",
//         height: "100vh",
//         width: "100vw",
//         overflow: "hidden",
//       }}
//     >
//       <MapContainer
//         center={[21.0285, 105.8542]}
//         zoom={12}
//         scrollWheelZoom={true}
//         zoomControl={false}
//         style={{
//           height: "100%",
//           width: "100%",
//           position: "absolute",
//           top: 0,
//           left: 0,
//         }}
//       >
//         <TileLayer
//           attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
//           url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
//         />
//         {isTracking && (
//           <BusRoute
//             startPoint={routePoints.start}
//             endPoint={routePoints.end}
//             currentPosition={currentPosition}
//             routeHistory={routeHistory}
//             onReset={handleStopTracking}
//           />
//         )}
//         <ZoomControl position="bottomright" />
//       </MapContainer>

//       {isTracking && (
//         <ControlPanel
//           onStopTracking={handleStopTracking}
//           onFeedback={() => setShowFeedback(true)}
//           isLoggedIn={!!localStorage.getItem("access_token")}
//         />
//       )}

//       <FeedbackModal
//         open={showFeedback}
//         onClose={() => setShowFeedback(false)}
//         busId={mapData.busNumber}
//       />
//     </div>
//   );
// };

// export default Map;

import React, { useEffect, useState, useCallback, useMemo } from "react";
import {
    MapContainer,
    TileLayer,
    Marker,
    Popup,
    useMap,
    ZoomControl,
    Polyline,
} from "react-leaflet";
import ControlPanel from "./ControlPanel";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import "leaflet-routing-machine";
import { useDispatch, useSelector } from "react-redux";
import { useMutation, useQuery } from "@tanstack/react-query";
import * as actions from "../redux/actions";
import { toast } from "react-toastify";
import { Modal, Box, Typography, TextField, Button } from "@mui/material";
import { useTranslation } from "react-i18next";
import { ICONS } from "../constansts/mapIcons";
import requestApi from "../helpers/api";
// Custom hook để quản lý bus tracking
const modalStyles = {
    position: "fixed",
    bottom: 20,
    right: 20,
    width: 350,
    bgcolor: "background.paper",
    boxShadow: 24,
    p: 3,
    borderRadius: "8px",
};
const useBusTracking = (route_id, isTracking) => {
    const [currentPosition, setCurrentPosition] = useState(null);
    const [routeHistory, setRouteHistory] = useState([]);

    useEffect(() => {
        if (!isTracking || !route_id) return;

        const updatePosition = async () => {
            try {
                const response = await requestApi("/map/get-location", "POST", {
                    id: route_id,
                });
                const { lat, lng } = response.data;
                // console.log(lat, lng);
                if (lat && lng) {
                    setCurrentPosition([lat, lng]);
                    setRouteHistory((prev) => [...prev, [lat, lng]]);
                }
            } catch (error) {
                console.error("Error tracking bus:", error);
            }
        };

        const intervalId = setInterval(updatePosition, 2000);
        return () => clearInterval(intervalId);
    }, [route_id, isTracking]);
    const resetRouteHistory = () => {
        setRouteHistory([]); // Reset routeHistory
    };
    return { currentPosition, routeHistory, resetRouteHistory };
};

// BusRoute component để hiển thị đường đi
const BusRoute = ({ startPoint, endPoint, currentPosition, routeHistory }) => {
    const map = useMap();
    const [routingControl, setRoutingControl] = useState(null);
    const [plannedRoute, setPlannedRoute] = useState([]);
    // useEffect(() => {
    //   if (startPoint && endPoint) {
    //     const bounds = L.latLngBounds([startPoint, endPoint]);
    //     map.fitBounds(bounds, { padding: [50, 50] });
    //   }
    // }, [startPoint, endPoint, map]);
    useEffect(() => {
        if (startPoint && endPoint) {
            const control = L.Routing.control({
                waypoints: [L.latLng(startPoint), L.latLng(endPoint)],
                routeWhileDragging: false,
                addWaypoints: false,
                draggableWaypoints: false,
                fitSelectedRoutes: true,
                show: false,
                lineOptions: {
                    styles: [
                        { color: "gray", opacity: 0.6, weight: 4, dashArray: "10, 10" },
                    ],
                },
            }).addTo(map);

            // Lưu planned route khi có kết quả routing
            control.on("routesfound", (e) => {
                const coordinates = e.routes[0].coordinates;
                setPlannedRoute(coordinates);
            });

            setRoutingControl(control);

            // Fit bounds
            const bounds = L.latLngBounds([startPoint, endPoint]);
            map.fitBounds(bounds, { padding: [50, 50] });

            return () => {
                map.removeControl(control);
            };
        }
    }, [startPoint, endPoint, map]);
    const completedRoute = useMemo(
        () => <Polyline positions={routeHistory} color="blue" weight={4} />,
        [routeHistory]
    );
    const remainingRoute = useMemo(() => {
        if (!currentPosition || !plannedRoute.length) return null;

        // Tìm điểm gần nhất trên planned route với vị trí hiện tại
        const currentIndex = plannedRoute.findIndex((point, index) => {
            if (index === plannedRoute.length - 1) return true;
            const d1 = L.latLng(currentPosition).distanceTo(L.latLng(point));
            const d2 = L.latLng(currentPosition).distanceTo(
                L.latLng(plannedRoute[index + 1])
            );
            return d1 < d2;
        });

        // Lấy phần route còn lại
        const remainingPoints = plannedRoute.slice(currentIndex);

        return (
            <Polyline
                positions={remainingPoints}
                color="yellow"
                weight={3}
                dashArray="10, 10"
            />
        );
    }, [currentPosition, plannedRoute]);
    return (
        <>
            {completedRoute}
            {/* {remainingRoute} */}
            {startPoint && (
                <Marker position={startPoint} icon={ICONS.START}>
                    <Popup>Điểm đầu</Popup>
                </Marker>
            )}
            {endPoint && (
                <Marker position={endPoint} icon={ICONS.END}>
                    <Popup>Điểm cuối</Popup>
                </Marker>
            )}
            {currentPosition && (
                <Marker position={currentPosition} icon={ICONS.BUS}>
                    <Popup>Xe bus</Popup>
                </Marker>
            )}
        </>
    );
};

// FeedbackModal component
const FeedbackModal = ({ open, onClose, busId }) => {
    const [feedback, setFeedback] = useState("");
    const { t } = useTranslation();

    const mutation = useMutation({
        mutationFn: (data) => requestApi("/feedback/add", "POST", data),
        onSuccess: (response) => {
            toast.success(response.data.message);
            setFeedback("");
            onClose();
        },
        onError: (error) => {
            toast.error(error.response?.data?.message || "Error sending feedback");
        },
    });

    return (
        <Modal open={open} onClose={onClose}>
            <Box sx={modalStyles.container}>{/* Modal content */}</Box>
        </Modal>
    );
};

// Main Map component
const Map = () => {
    const dispatch = useDispatch();
    const mapData = useSelector((state) => state.mapSearch);
    const [routePoints, setRoutePoints] = useState({ start: null, end: null });
    const [isTracking, setIsTracking] = useState(false);
    const [showFeedback, setShowFeedback] = useState(false);
    const { t } = useTranslation();

    const { currentPosition, routeHistory, resetRouteHistory } = useBusTracking(
        mapData.routeId,
        isTracking
    );

    // Fetch route points
    const fetchRoutePoints = useCallback(async () => {
        if (!mapData.search) return;

        try {
            dispatch(actions.controlLoading(true));
            const response = await requestApi(
                `/bus/get-st-end?bus_id=${mapData.busNumber}`,
                "GET"
            );
            console.log(response);
            setRoutePoints({
                start: response.data.start,
                end: response.data.end,
            });
            setIsTracking(true);

            toast.success(response.data.message);
        } catch (error) {
            toast.error(error.response?.data?.message || "Error fetching route");
        } finally {
            dispatch(actions.controlLoading(false));
        }
    }, [mapData.search, mapData.busNumber]);

    useEffect(() => {
        fetchRoutePoints();
    }, [fetchRoutePoints]);
    useEffect(() => {
        if (
            currentPosition &&
            routePoints.end &&
            L.latLng(currentPosition).equals(L.latLng(routePoints.end))
        ) {
            resetRouteHistory(); // Gọi hàm reset khi đến điểm cuối
        }
    }, [currentPosition, routePoints.end, resetRouteHistory]);
    const handleStopTracking = () => {
        setIsTracking(false);
        resetRouteHistory();
        setRoutePoints({ start: null, end: null });
        dispatch(actions.setSharedData({ search: false }));
    };

    return (
        <div
            style={{
                position: "relative",
                height: "100vh",
                width: "100vw",
                overflow: "hidden",
            }}
        >
            <MapContainer
                center={[21.0285, 105.8542]}
                zoom={12}
                scrollWheelZoom={true}
                zoomControl={false}
                style={{
                    height: "100%",
                    width: "100%",
                    position: "absolute",
                    top: 0,
                    left: 0,
                }}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {isTracking && (
                    <BusRoute
                        startPoint={routePoints.start}
                        endPoint={routePoints.end}
                        currentPosition={currentPosition}
                        routeHistory={routeHistory}
                    />
                )}
                <ZoomControl position="bottomright" />
            </MapContainer>

            {isTracking && (
                <ControlPanel
                    onStopTracking={handleStopTracking}
                    onFeedback={() => setShowFeedback(true)}
                    isLoggedIn={!!localStorage.getItem("access_token")}
                />
            )}

            <FeedbackModal
                open={showFeedback}
                onClose={() => setShowFeedback(false)}
                busId={mapData.busNumber}
            />
        </div>
    );
};

export default Map;