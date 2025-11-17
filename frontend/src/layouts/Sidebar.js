// import React, { useEffect, useState } from "react";
// import { Link } from "react-router-dom";
// import { useTranslation } from "react-i18next";
// import {
//   Drawer,
//   List,
//   ListItem,
//   ListItemIcon,
//   ListItemText,
//   Button,
//   Box,
//   Tab,
//   Tabs,
//   TextField,
//   Typography,
// } from "@mui/material";
// import DashboardIcon from "@mui/icons-material/Dashboard";
// import PersonIcon from "@mui/icons-material/Person";
// import LogoutIcon from "@mui/icons-material/Logout";
// import DirectionsBusIcon from "@mui/icons-material/DirectionsBus";
// import PeopleIcon from "@mui/icons-material/People";
// import AltRouteIcon from "@mui/icons-material/AltRoute";
// import LocationOnIcon from "@mui/icons-material/LocationOn";
// import { useDispatch, useSelector } from "react-redux";
// import * as actions from "../redux/actions";
// import Autocomplete from "@mui/material/Autocomplete";
// import { useQuery } from "@tanstack/react-query";
// import requestApi from "../helpers/api";
// const getBusData = async () => {
//   const responseBus = await requestApi("/bus/get-all-bus", "GET");
//   console.log("122222222");
//   return responseBus;
// };
// const Sidebar = ({ drawerOpen, toggleDrawer, role }) => {
//   const { t, i18n } = useTranslation();

//   let listBus;

//   const { data, error, isLoading } = useQuery({
//     queryKey: ["fetchBusData"],
//     queryFn: getBusData,
//   });
//   console.log(drawerOpen);
//   if (isLoading) return <div>{t("Loading...")}</div>;
//   if (error)
//     return (
//       <div>
//         {t("Error")}: {error.message}
//       </div>
//     );
//   if (data) {
//     console.log(data.data);
//     listBus = data.data;
//   }

//   const Search = () => {
//     const dispatch = useDispatch();
//     const [rows, setRows] = useState([]);
//     const [activeTab, setActiveTab] = useState(0);
//     const [startLocation, setStartLocation] = useState("");
//     const [endLocation, setEndLocation] = useState("");
//     const [busNumber, setBusNumber] = useState("");

//     const handleTabChange = (event, newValue) => {
//       setActiveTab(newValue);
//     };

//     const handleSearch = (event, value) => {
//       if (!value) {
//         setRows(listBus);
//         return;
//       }

//       const searchTerm = value.toLowerCase();
//       const filtered = listBus.filter(
//         (bus) =>
//           bus.bus_id.toString().includes(searchTerm) ||
//           bus.name.toLowerCase().includes(searchTerm) ||
//           bus.plate_number.includes(searchTerm)
//       );
//       setRows(filtered);
//     };

//     const handleSelect = (event, value) => {
//       if (value) {
//         const filtered = listBus.filter(
//           (bus) =>
//             bus.bus_id === value.bus_id &&
//             bus.name === value.name &&
//             bus.plate_number === value.plate_number
//         );
//         setRows(filtered);
//         setBusNumber(value.bus_id);
//       } else {
//         setRows(listBus);
//       }
//     };

//     const handleSearch2 = () => {
//       const searchData = {
//         typeSearch: activeTab,
//         st: startLocation,
//         end: endLocation,
//         busNumber: busNumber,
//         search: true,
//       };
//       dispatch(actions.setSharedData(searchData));
//       toggleDrawer(false);
//     };

//     return (
//       <Box
//         sx={{ padding: 2, maxWidth: 600, margin: "auto", textAlign: "center" }}
//       >
//         <Tabs
//           value={activeTab}
//           onChange={handleTabChange}
//           variant="fullWidth"
//           sx={{ marginBottom: 2 }}
//         >
//           <Tab label={t("Tìm theo địa điểm")} />
//           <Tab label={t("Tìm theo xe")} />
//         </Tabs>

//         {activeTab === 0 && (
//           <Box>
//             <TextField
//               label={t("Điểm đi")}
//               variant="outlined"
//               fullWidth
//               sx={{ marginBottom: 2 }}
//               value={startLocation}
//               onChange={(e) => setStartLocation(e.target.value)}
//             />
//             <TextField
//               label={t("Điểm đến")}
//               variant="outlined"
//               fullWidth
//               sx={{ marginBottom: 2 }}
//               value={endLocation}
//               onChange={(e) => setEndLocation(e.target.value)}
//             />
//             <Button
//               variant="contained"
//               color="primary"
//               fullWidth
//               onClick={handleSearch2}
//             >
//               {t("Tìm kiếm")}
//             </Button>
//           </Box>
//         )}

//         {activeTab === 1 && (
//           <Box>
//             <Autocomplete
//               sx={{ width: 208, mb: 2 }}
//               options={listBus}
//               getOptionLabel={(option) =>
//                 `ID ${option.bus_id} (${option.name}) - ${option.plate_number}`
//               }
//               onInputChange={handleSearch}
//               onChange={handleSelect}
//               renderInput={(params) => (
//                 <TextField {...params} label={t("Tìm bus")} />
//               )}
//             />
//             <Button
//               variant="contained"
//               color="primary"
//               fullWidth
//               onClick={handleSearch2}
//             >
//               {t("Tìm kiếm")}
//             </Button>
//           </Box>
//         )}
//       </Box>
//     );
//   };

//   return (
//     <Drawer
//       variant="temporary"
//       anchor="left"
//       open={drawerOpen}
//       onClose={() => toggleDrawer(false)}
//       sx={{
//         "& .MuiDrawer-paper": {
//           width: 240,
//           position: "relative",
//           transition: "width 0.3s ease",
//         },
//       }}
//     >
//       <Box sx={{ paddingTop: "64px" }}>
//         <List>
// {role === "manager" && (
//   <>
// <ListItem button component={Link} to="/">
//   <ListItemIcon>
//     <LocationOnIcon />
//   </ListItemIcon>
//   <ListItemText primary={t("Map")} />
// </ListItem>

// <ListItem button component={Link} to="/manager/user-list">
//   <ListItemIcon>
//     <PersonIcon />
//   </ListItemIcon>
//   <ListItemText primary={t("Danh sách user")} />
// </ListItem>
// <ListItem button component={Link} to="/manager/feedback">
//   <ListItemIcon>
//     <PersonIcon />
//   </ListItemIcon>
//   <ListItemText primary={t("feedMan")} />
// </ListItem>
// <ListItem button component={Link} to="/manager/driver-list">
//   <ListItemIcon>
//     <PeopleIcon />
//   </ListItemIcon>
//   <ListItemText primary={t("Danh sách tài xế")} />
// </ListItem>

// <ListItem button component={Link} to="/manager/bus">
//   <ListItemIcon>
//     <DirectionsBusIcon />
//   </ListItemIcon>
//   <ListItemText primary={t("Quản lý xe")} />
// </ListItem>
//   </>
// )}

//           {role === "user" && <Search />}
//           {/* {role === "driver" && (
//             <>
//               <Button variant="contained" color="primary" fullWidth>
//                 {t("Tìm kiếm")}
//               </Button>
//             </>
//           )} */}
//           <ListItem button component={Link} to="/logout">
//             <ListItemIcon>
//               <LogoutIcon />
//             </ListItemIcon>
//             <ListItemText primary={t("Logout")} />
//           </ListItem>
//         </List>
//       </Box>
//     </Drawer>
//   );
// };

// export default Sidebar;
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
  Tab,
  Tabs,
  TextField,
  IconButton,
  Typography,
  Button,
  Divider,
  Paper,
  Autocomplete,
} from "@mui/material";
import {
  Menu as MenuIcon,
  DirectionsBus,
  Person as PersonIcon,
  People as PeopleIcon,
  LocationOn as LocationOnIcon,
  Logout as LogoutIcon,
  Close as CloseIcon,
  Bookmark as BookmarkIcon,
  History as HistoryIcon,
} from "@mui/icons-material";
import { useDispatch } from "react-redux";
import * as actions from "../redux/actions";
import { useQuery } from "@tanstack/react-query";
import requestApi from "../helpers/api";
const getBusData = async () => {
  const response = await requestApi("/bus/get-all-bus", "GET");
  return response;
};
const ControlBar = ({ onMenuClick }) => (
  <Paper
    elevation={2}
    sx={{
      position: "fixed",
      zIndex: 1200,
      backgroundColor: "white",
      borderRadius: "8px",
      display: "flex",
      maxHeight: "100vh",
      height: "100vh",
      flexDirection: "column",
      "& .MuiIconButton-root": {
        padding: "12px",
        borderRadius: "8px",
        "&:hover": {
          backgroundColor: "rgba(31, 29, 29, 0.04)",
        },
      },
    }}
  >
    <IconButton onClick={onMenuClick}>
      <MenuIcon />
    </IconButton>
    <Divider sx={{ my: 0.5 }} />
    <IconButton>
      <BookmarkIcon />
    </IconButton>
    <IconButton>
      <HistoryIcon />
    </IconButton>
  </Paper>
);
const Sidebar = ({ drawerOpen, toggleDrawer, role }) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { data, error, isLoading } = useQuery({
    queryKey: ["fetchBusData"],
    queryFn: getBusData,
  });

  const listBus = data?.data || [];
  const handleLogout = () => {
    ["access_token", "refresh_token", "role", "admin"].forEach((item) =>
      localStorage.removeItem(item)
    );
    navigate("/login");
  };
  const Search = () => {
    const dispatch = useDispatch();
    const [startLocation, setStartLocation] = useState("");
    const [endLocation, setEndLocation] = useState("");

    const handleSearch = () => {
      const searchData = {
        typeSearch: 0, // Luôn là tìm theo địa điểm
        st: startLocation,
        end: endLocation,
        search: true,
      };
      dispatch(actions.setSharedData(searchData));
      toggleDrawer(false);
    };

    return (
      <Box sx={{ padding: 2, maxWidth: 600, margin: "auto" }}>
        <Typography variant="h6" sx={{ mb: 2, color: "#5f6368" }}>
          {t("Tìm đường")}
        </Typography>
        <Box>
          <TextField
            label={t("Điểm đi")}
            variant="outlined"
            fullWidth
            sx={{ mb: 2 }}
            value={startLocation}
            onChange={(e) => setStartLocation(e.target.value)}
          />
          <TextField
            label={t("Điểm đến")}
            variant="outlined"
            fullWidth
            sx={{ mb: 2 }}
            value={endLocation}
            onChange={(e) => setEndLocation(e.target.value)}
          />
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={handleSearch}
          >
            {t("Tìm đường")}
          </Button>
        </Box>
      </Box>
    );
  };
  return (
    <>
      {/* Control Bar */}
      <ControlBar onMenuClick={() => toggleDrawer(true)} />

      {/* Sidebar Drawer */}
      <Drawer
        variant="temporary"
        anchor="left"
        open={drawerOpen}
        onClose={() => toggleDrawer(false)}
        sx={{
          "& .MuiDrawer-paper": {
            width: 400,
            height: "100%",
            boxSizing: "border-box",
          },
        }}
      >
        {/* Header của Sidebar */}
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            padding: "12px 16px",
            borderBottom: "1px solid #e0e0e0",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <DirectionsBus sx={{ color: "#1a73e8", mr: 1 }} />
            <Typography variant="h6" sx={{ color: "#5f6368" }}>
              {t("findBus")}
            </Typography>
          </Box>
          <Box sx={{ flexGrow: 1 }} />
          <IconButton
            onClick={() => toggleDrawer(false)}
            sx={{
              "&:hover": { backgroundColor: "rgba(0,0,0,0.04)" },
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>

        {/* Content của Sidebar */}
        <Box
          sx={{
            overflow: "auto",
            height: "calc(100% - 64px)",
            backgroundColor: "#fff",
          }}
        >
          {isLoading ? (
            <Box sx={{ p: 2 }}>{t("Loading...")}</Box>
          ) : error ? (
            <Box sx={{ p: 2, color: "error.main" }}>
              {t("Error")}: {error.message}
            </Box>
          ) : (
            <>
              {role === "manager" ? (
                <List>
                  <ListItem button component={Link} to="/">
                    <ListItemIcon>
                      <LocationOnIcon />
                    </ListItemIcon>
                    <ListItemText primary={t("Map")} />
                  </ListItem>
                  <Divider />

                  <ListItem button component={Link} to="/manager/user-list">
                    <ListItemIcon>
                      <PersonIcon />
                    </ListItemIcon>
                    <ListItemText primary={t("Danh sách user")} />
                  </ListItem>
                  <ListItem button component={Link} to="/manager/feedback">
                    <ListItemIcon>
                      <PersonIcon />
                    </ListItemIcon>
                    <ListItemText primary={t("feedMan")} />
                  </ListItem>
                  <ListItem button component={Link} to="/manager/driver-list">
                    <ListItemIcon>
                      <PeopleIcon />
                    </ListItemIcon>
                    <ListItemText primary={t("Danh sách tài xế")} />
                  </ListItem>

                  <ListItem button component={Link} to="/manager/bus">
                    <ListItemIcon>
                      <DirectionsBus />
                    </ListItemIcon>
                    <ListItemText primary={t("Quản lý xe")} />
                  </ListItem>
                </List>
              ) : role === "user" ? (
                <Search />
              ) : null}
              <Divider />
              <List>
                <ListItem button onClick={handleLogout}>
                  <ListItemIcon>
                    <LogoutIcon />
                  </ListItemIcon>
                  <ListItemText primary={t("Logout")} />
                </ListItem>
              </List>
            </>
          )}
        </Box>
      </Drawer>
    </>
  );
};

export default Sidebar;
