// import React, { useState, useEffect } from "react";
// import { useNavigate } from "react-router-dom";
// import { useTranslation } from "react-i18next";
// import {
//   AppBar,
//   Toolbar,
//   Typography,
//   IconButton,
//   Menu,
//   MenuItem,
//   Button,
//   Divider,
//   Box,
//   Autocomplete,
//   TextField,
// } from "@mui/material";
// import {
//   AccountCircle,
//   Menu as MenuIcon,
//   DirectionsBus as DirectionsBusIcon,
// } from "@mui/icons-material";

// const languages = [
//   {
//     code: "vi",
//     label: "Tiếng Việt",
//     flag: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Flag_of_Vietnam.svg/800px-Flag_of_Vietnam.svg.png",
//   },
//   {
//     code: "en",
//     label: "English",
//     flag: "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Flag_of_the_United_Kingdom_%281-2%29.svg/1200px-Flag_of_the_United_Kingdom_%281-2%29.svg.png",
//   },
// ];

// const Header = ({ toggleSidebar }) => {
//   const navigate = useNavigate();
//   const { t, i18n } = useTranslation();
//   const [isLoggedIn, setIsLoggedIn] = useState(false);
//   const [anchorEl, setAnchorEl] = useState(null);
//   const [language, setLanguage] = useState(languages[0]);

//   useEffect(() => {
//     const token = localStorage.getItem("access_token");
//     setIsLoggedIn(!!token);

//     const savedLang = localStorage.getItem("i18nextLng");
//     if (savedLang) {
//       const selectedLanguage = languages.find(
//         (lang) => lang.code === savedLang
//       );
//       if (selectedLanguage) setLanguage(selectedLanguage);
//     }
//   }, []);

//   const handleLogout = () => {
//     ["access_token", "refresh_token", "role", "admin"].forEach((item) =>
//       localStorage.removeItem(item)
//     );
//     navigate("/login");
//   };

//   const handleLanguageChange = (newValue) => {
//     if (newValue) {
//       setLanguage(newValue);
//       i18n.changeLanguage(newValue.code);
//       localStorage.setItem("i18nextLng", newValue.code);
//     }
//   };

//   return (
//     <AppBar
//       position="relative"
//       sx={{
//         backgroundColor: "white",
//         color: "#5f6368",
//         boxShadow: "none",
//         borderBottom: "1px solid #e0e0e0",
//       }}
//     >
//       <Toolbar sx={{ minHeight: "60px !important" }}>
//         {/* Menu Button */}
//         <IconButton
//           edge="start"
//           onClick={toggleSidebar}
//           sx={{ color: "#5f6368", mr: 2 }}
//         >
//           <MenuIcon />
//         </IconButton>

//         {/* Logo and Title */}
//         <Box sx={{ display: "flex", alignItems: "center", mr: 2 }}>
//           <DirectionsBusIcon sx={{ color: "#1a73e8", mr: 1 }} />
//           <Typography
//             variant="h6"
//             sx={{
//               color: "#5f6368",
//               fontWeight: 500,
//               fontSize: "1.2rem",
//               flexGrow: 1,
//             }}
//           >
//             {t("findBus")}
//           </Typography>
//         </Box>

//         {/* Spacer */}
//         <Box sx={{ flexGrow: 1 }} />

//         {/* Language Selector */}
//         <Box
//           sx={{
//             width: 180,
//             mr: 2,
//             backgroundColor: "white",
//             borderRadius: 1,
//             "& .MuiOutlinedInput-root": {
//               "& fieldset": {
//                 borderColor: "#e0e0e0",
//               },
//               "&:hover fieldset": {
//                 borderColor: "#1a73e8",
//               },
//             },
//           }}
//         >
//           <Autocomplete
//             options={languages}
//             value={language}
//             onChange={handleLanguageChange}
//             getOptionLabel={(option) => option.label}
//             renderOption={(props, option) => (
//               <MenuItem {...props} key={option.code}>
//                 <Box
//                   component="img"
//                   src={option.flag}
//                   alt={option.label}
//                   sx={{ width: 24, height: 16, mr: 1 }}
//                 />
//                 <Typography>{option.label}</Typography>
//               </MenuItem>
//             )}
//             renderInput={(params) => (
//               <TextField
//                 {...params}
//                 variant="outlined"
//                 size="small"
//                 sx={{ "& .MuiOutlinedInput-root": { padding: 1 } }}
//               />
//             )}
//           />
//         </Box>

//         {/* Auth Buttons */}
//         {!isLoggedIn ? (
//           <Button
//             variant="contained"
//             onClick={() => navigate("/login")}
//             sx={{
//               backgroundColor: "#1a73e8",
//               textTransform: "none",
//               "&:hover": {
//                 backgroundColor: "#1557b0",
//               },
//             }}
//           >
//             {t("dnhap")}
//           </Button>
//         ) : (
//           <Box>
//             <IconButton
//               onClick={(e) => setAnchorEl(e.currentTarget)}
//               sx={{ color: "#5f6368" }}
//             >
//               <AccountCircle />
//             </IconButton>
//             <Menu
//               anchorEl={anchorEl}
//               open={Boolean(anchorEl)}
//               onClose={() => setAnchorEl(null)}
//               sx={{ mt: 1 }}
//               transformOrigin={{ horizontal: "right", vertical: "top" }}
//               anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
//             >
//               <MenuItem onClick={() => setAnchorEl(null)}>
//                 {t("profile")}
//               </MenuItem>
//               <Divider />
//               <MenuItem onClick={handleLogout}>{t("logout")}</MenuItem>
//             </Menu>
//           </Box>
//         )}
//       </Toolbar>
//     </AppBar>
//   );
// };

// export default Header;
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  AppBar,
  Toolbar,
  IconButton,
  Menu,
  MenuItem,
  Box,
  Autocomplete,
  TextField,
  Paper,
  InputBase,
  Divider,
  Popper,
} from "@mui/material";
import {
  AccountCircle,
  Search as SearchIcon,
  LocationOn as LocationOnIcon,
  DirectionsBus as DirectionsBusIcon,
} from "@mui/icons-material";
import ExpandableSearchPanel from "./Panel";
import requestApi from "../helpers/api";
import { useQuery } from "@tanstack/react-query";
import { useLocation } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import * as actions from "../redux/actions";
import NotificationMenu from "./Notification";
const languages = [
  {
    code: "vi",
    label: "Tiếng Việt",
    flag: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Flag_of_Vietnam.svg/800px-Flag_of_Vietnam.svg.png",
  },
  {
    code: "en",
    label: "English",
    flag: "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Flag_of_the_United_Kingdom_%281-2%29.svg/1200px-Flag_of_the_United_Kingdom_%281-2%29.svg.png",
  },
];
const getBusData = async () => {
  const response = await requestApi("/bus/get-all-bus", "GET");
  return response;
};
const Header = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const isMapRoute =
    location.pathname === "/" || location.pathname === "/driver";
  const { t, i18n } = useTranslation();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [language, setLanguage] = useState(languages[0]);

  const [searchMode, setSearchMode] = useState("location"); // 'location' or 'bus'
  const [searchValue, setSearchValue] = useState("");

  const [selectedBus, setSelectedBus] = useState(null);
  const [showPanel, setShowPanel] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const {
    data: busData,
    error,
    isLoading,
  } = useQuery({
    queryKey: ["fetchBusData"],
    queryFn: getBusData,
  });
  console.log(busData?.data);
  const listBus = busData?.data || [];
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    setIsLoggedIn(!!token);

    const savedLang = localStorage.getItem("i18nextLng");
    if (savedLang) {
      const selectedLanguage = languages.find(
        (lang) => lang.code === savedLang
      );
      if (selectedLanguage) setLanguage(selectedLanguage);
    }
  }, []);

  const handleLogout = () => {
    ["access_token", "refresh_token", "role", "admin"].forEach((item) =>
      localStorage.removeItem(item)
    );
    navigate("/login");
  };

  const handleLanguageChange = (event, newValue) => {
    if (newValue) {
      setLanguage(newValue);
      i18n.changeLanguage(newValue.code);
      localStorage.setItem("i18nextLng", newValue.code);
    }
  };
  const handleBusSelect = (event, newValue) => {
    setSelectedBus(newValue);
    if (newValue) {
      console.log(newValue);
      setExpanded(true);
      const searchData = {
        typeSearch: 1,
        busNumber: newValue.bus_id,
        routeId: newValue.route_id,
        search: true,
      };
      dispatch(actions.setSharedData(searchData));
    }
  };

  const handleSearchValueChange = (value) => {
    setSearchValue(value);
  };

  const handleSearchModeChange = (mode) => {
    setSearchMode(mode);
  };

  return (
    <>
      {isMapRoute && (
        <ExpandableSearchPanel
          expanded={expanded}
          onToggleExpand={() => setExpanded(!expanded)}
          searchMode={searchMode}
          onSearchModeChange={handleSearchModeChange}
          selectedBus={selectedBus}
          listBus={listBus}
          onBusSelect={handleBusSelect}
          searchValue={searchValue}
          onSearchValueChange={handleSearchValueChange}
        />
      )}
      <AppBar
        position="absolute"
        sx={{
          backgroundColor: isMapRoute ? "transparent" : "#1976d2", // Màu blue khi không phải trang map
          backgroundImage: "none",
          boxShadow: isMapRoute ? "none" : undefined,
          color: isMapRoute ? "#5f6368" : "#fff",
          mt: 1,
        }}
      >
        <Toolbar
          sx={{
            minHeight: "48px !important",
            gap: 2,
            px: 1,
          }}
        >
          <Box sx={{ flexGrow: 1 }} />

          {/* Language Selector */}
          <Box sx={{ width: 180 }}>
            <Autocomplete
              disablePortal
              options={languages}
              value={language}
              onChange={handleLanguageChange}
              getOptionLabel={(option) => option.label}
              isOptionEqualToValue={(option, value) =>
                option.code === value.code
              }
              renderOption={(props, option) => (
                <Box component="li" {...props}>
                  <Box
                    component="img"
                    src={option.flag}
                    alt={option.label}
                    sx={{ width: 24, height: 16, mr: 1 }}
                  />
                  {option.label}
                </Box>
              )}
              renderInput={(params) => (
                <TextField
                  {...params}
                  variant="outlined"
                  size="small"
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      backgroundColor: "rgba(255, 255, 255, 1)",
                      fontSize: "14px",
                      "& fieldset": {
                        borderColor: "rgba(0,0,0,0.12)",
                      },
                      "&:hover fieldset": {
                        borderColor: "rgba(0,0,0,0.23)",
                      },
                    },
                  }}
                />
              )}
            />
          </Box>
          {/* Add NotificationMenu before User Menu */}
          {isLoggedIn && <NotificationMenu />}
          {/* User Menu */}
          {isLoggedIn && (
            <Box>
              <IconButton
                onClick={(e) => setAnchorEl(e.currentTarget)}
                sx={{
                  color: "#5f6368",
                  backgroundColor: "rgba(255, 255, 255, 1)",
                  "&:hover": {
                    backgroundColor: "rgba(255, 255, 255, 0.95)",
                  },
                }}
              >
                <AccountCircle />
              </IconButton>
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={() => setAnchorEl(null)}
                transformOrigin={{ horizontal: "right", vertical: "top" }}
                anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
                sx={{
                  "& .MuiPaper-root": {
                    backgroundColor: "rgba(255, 255, 255, 1)",
                    boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
                  },
                }}
              >
                <MenuItem onClick={() => setAnchorEl(null)}>
                  {t("profile")}
                </MenuItem>
                <Divider />
                <MenuItem onClick={handleLogout}>{t("logout")}</MenuItem>
              </Menu>
            </Box>
          )}
        </Toolbar>
      </AppBar>
    </>
  );
};

export default Header;
