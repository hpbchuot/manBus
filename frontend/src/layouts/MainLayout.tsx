import React, { useState } from 'react';
import { Box, AppBar, Toolbar, Typography, IconButton, Button, Drawer, CssBaseline, useMediaQuery, useTheme } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import LanguageIcon from '@mui/icons-material/Language'; // Giả lập nút đổi ngôn ngữ
import { Outlet } from 'react-router-dom'; // Nơi hiển thị nội dung con (Map)

const DRAWER_WIDTH = 380; // Kích thước Sidebar (theo design 350-400px)




const MainLayout: React.FC = () => {
  const theme = useTheme();
  // Responsive: Tự động ẩn sidebar nếu màn hình nhỏ
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [open, setOpen] = useState(!isMobile); // Mặc định mở trên PC

  const handleDrawerToggle = () => {
    setOpen(!open);
    // Lưu ý: Sau này khi gắn Map, ta cần gọi map.invalidateSize() ở đây
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <CssBaseline />
      
      {/* --- A. GLOBAL HEADER --- */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            BUSMAP
          </Typography>

          {/* Language Switcher */}
          <IconButton color="inherit" sx={{ mr: 1 }}>
            <LanguageIcon />
          </IconButton>


        </Toolbar>
      </AppBar>

      {/* --- B. SIDEBAR (DRAWER) --- */}
      <Drawer
        variant="persistent" // Theo design: persistent (đẩy nội dung)
        anchor="left"
        open={open}
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            backgroundColor: 'background.default', // Màu xám nhạt #F5F7FA
            borderRight: '1px solid rgba(0,0,0,0.05)',
            top: '64px', // Né Header ra (mặc định toolbar cao 64px)
            height: 'calc(100% - 64px)',
          },
        }}
      >
        <Box sx={{ p: 2 }}>
            {/* Placeholder cho Search & List sau này */}
            <Typography variant="subtitle2" color="textSecondary">Sidebar Content</Typography>
        </Box>
      </Drawer>

      {/* --- C. MAP AREA (MAIN CONTENT) --- */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          height: '100vh',
          pt: '64px', // Padding top bằng chiều cao Header
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          marginLeft: open ? 0 : `-${DRAWER_WIDTH}px`, // Logic đẩy sang phải
          ...(open && {
            transition: theme.transitions.create('margin', {
              easing: theme.transitions.easing.easeOut,
              duration: theme.transitions.duration.enteringScreen,
            }),
            marginLeft: 0, 
          }),
          display: 'flex', 
          flexDirection: 'column'
        }}
      >
        {/* Outlet là nơi component Page (chứa Map) sẽ hiển thị */}
        <Outlet /> 
      </Box>
    </Box>
  );
};

export default MainLayout;