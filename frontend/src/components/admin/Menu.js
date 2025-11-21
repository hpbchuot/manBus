import React, { useState, useEffect } from "react";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import InboxIcon from "@mui/icons-material/Inbox";
import MailIcon from "@mui/icons-material/Mail";
import PersonIcon from "@mui/icons-material/Person";
import { Outlet, Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { Autocomplete, TextField } from "@mui/material";
import { useTranslation } from "react-i18next";
import MenuItem from "@mui/material/MenuItem";
import { toast } from "react-toastify";
export default function Menu() {
  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const [language, setLanguage] = useState({
    code: "vi",
    label: "Tiếng Việt",
    flag: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Flag_of_Vietnam.svg/800px-Flag_of_Vietnam.svg.png",
  });

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
  const changeLanguage = (lang) => {
    i18n.changeLanguage(lang);
    localStorage.setItem("i18nextLng", lang);
  };

  const handleChange = (event, newValue) => {
    if (newValue) {
      setLanguage(newValue);
      changeLanguage(newValue.code);
    }
  };
  const handleNavClick = (link) => {
    navigate(link);
  };
  const toggleDrawer = (open) => () => {
    setDrawerOpen(open);
  };

  const handleMenuClick = () => {
    setDrawerOpen(!drawerOpen);
  };
  const onHandleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("role");
    localStorage.removeItem("admin");
    toast.success("Đăng xuất thành công", {
      position: "top-right",
      autoClose: 3000,
    });
    navigate("/login");
  };
  const sideNavItems = [
    { text: t("dashboard"), icon: <InboxIcon />, link: "/admin" },
    { text: t("userManagement"), icon: <PersonIcon />, link: "/admin/qluser" },
  ];

  const renderSideNav = () => (
    <Box
      sx={{ width: 250 }}
      role="presentation"
      onClick={toggleDrawer(false)}
      onKeyDown={toggleDrawer(false)}
    >
      <List>
        {sideNavItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component={Link}
              to={item.link}
              onClick={() => toggleDrawer(false)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: "flex", flexGrow: 1 }}>
      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
      >
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
            onClick={handleMenuClick}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {t("appTitle")}
          </Typography>
          <Box
            sx={{
              width: 200,
              backgroundColor: "rgb(243 243 243 / 80%)",
              border: "1px solid rgba(255, 255, 255, 0.5)",
              borderRadius: "8px",
              color: "white",
            }}
          >
            <Autocomplete
              options={languages}
              getOptionLabel={(option) => option.label}
              renderOption={(props, option) => (
                <MenuItem {...props} key={option.code} sx={{ mt: 1 }}>
                  <Box
                    component="img"
                    src={option.flag}
                    alt={option.label}
                    sx={{ width: 24, height: 10, mr: 1 }}
                  />
                  <Typography>{option.label}</Typography>
                </MenuItem>
              )}
              value={language}
              onChange={handleChange}
              renderInput={(params) => (
                <TextField
                  {...params}
                  variant="outlined"
                  InputProps={{
                    ...params.InputProps,
                    sx: { padding: 0 }, // Remove padding inside the input
                  }}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      padding: 0, // Remove padding from the root
                    },
                  }}
                />
              )}
            />
          </Box>
          <Button
            color="inherit"
            sx={{ minWidth: "100px", textAlign: "center" }}
            onClick={onHandleLogout}
          >
            {t("logout")}
          </Button>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={toggleDrawer(false)}
        sx={{
          "& .MuiDrawer-paper": { top: "3.4rem" }, // Offset below AppBar
        }}
      >
        {renderSideNav()}
      </Drawer>

      {/* Main Content */}
      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
        <Outlet /> {/* Render nội dung từ các route con */}
      </Box>
    </Box>
  );
}
