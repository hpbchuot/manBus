import React, { useState } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  CssBaseline,
  useMediaQuery,
  useTheme,
  Button,
  Menu,
  MenuItem,
  Avatar,
  Divider,
  ListItemIcon,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import LanguageIcon from '@mui/icons-material/Language';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LogoutIcon from '@mui/icons-material/Logout';
import PersonIcon from '@mui/icons-material/Person';
import { Outlet } from 'react-router-dom';
import Login from '@/components/auth/Login';
import Register from '@/components/auth/Register';
import { useAuth } from '@/hooks/useAuth';

const DRAWER_WIDTH = 380;

const MainLayout: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [open, setOpen] = useState(!isMobile);
  const [loginOpen, setLoginOpen] = useState(false);
  const [registerOpen, setRegisterOpen] = useState(false);
  const [anchorElUser, setAnchorElUser] = useState<null | HTMLElement>(null);
  const [anchorElLang, setAnchorElLang] = useState<null | HTMLElement>(null);

  const { user, isAuthenticated, logout } = useAuth();

  const handleDrawerToggle = () => {
    setOpen(!open);
  };

  const handleOpenLogin = () => {
    setLoginOpen(true);
  };

  const handleCloseLogin = () => {
    setLoginOpen(false);
  };

  const handleOpenRegister = () => {
    setRegisterOpen(true);
  };

  const handleCloseRegister = () => {
    setRegisterOpen(false);
  };

  const handleSwitchToRegister = () => {
    setLoginOpen(false);
    setRegisterOpen(true);
  };

  const handleSwitchToLogin = () => {
    setRegisterOpen(false);
    setLoginOpen(true);
  };

  const handleOpenUserMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setAnchorElUser(null);
  };

  const handleOpenLangMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorElLang(event.currentTarget);
  };

  const handleCloseLangMenu = () => {
    setAnchorElLang(null);
  };

  const handleLogout = () => {
    logout();
    handleCloseUserMenu();
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <CssBaseline />
      
      {/* --- GLOBAL HEADER --- */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          {/* Menu Toggle */}
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          {/* Logo/Title */}
          <Typography 
            variant="h6" 
            noWrap 
            component="div" 
            sx={{ flexGrow: 1, fontWeight: 'bold' }}
          >
            BUSMAP
          </Typography>

          {/* Language Switcher */}
          <IconButton 
            color="inherit" 
            sx={{ mr: 2 }}
            onClick={handleOpenLangMenu}
          >
            <LanguageIcon />
          </IconButton>
          <Menu
            anchorEl={anchorElLang}
            open={Boolean(anchorElLang)}
            onClose={handleCloseLangMenu}
          >
            <MenuItem onClick={handleCloseLangMenu}>
              Tiếng Việt
            </MenuItem>
            <MenuItem onClick={handleCloseLangMenu}>
              English
            </MenuItem>
          </Menu>

          {/* Authentication Section */}
          {isAuthenticated ? (
            <>
              {/* User Avatar & Name */}
              <Box 
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  cursor: 'pointer',
                  '&:hover': { opacity: 0.8 }
                }}
                onClick={handleOpenUserMenu}
              >
                <Avatar 
                  src={user?.avatar}
                  sx={{ 
                    width: 32, 
                    height: 32, 
                    mr: 1,
                    bgcolor: 'secondary.main'
                  }}
                >
                  {user?.fullName?.charAt(0) || user?.username?.charAt(0)}
                </Avatar>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    display: { xs: 'none', sm: 'block' },
                    fontWeight: 500
                  }}
                >
                  {user?.fullName || user?.username}
                </Typography>
              </Box>

              {/* User Menu Dropdown */}
              <Menu
                anchorEl={anchorElUser}
                open={Boolean(anchorElUser)}
                onClose={handleCloseUserMenu}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                sx={{ mt: 1 }}
              >
                <MenuItem disabled>
                  <ListItemIcon>
                    <PersonIcon fontSize="small" />
                  </ListItemIcon>
                  <Box>
                    <Typography variant="body2" fontWeight={600}>
                      {user?.fullName}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {user?.role === 'admin' ? 'Quản trị viên' : 
                       user?.role === 'driver' ? 'Tài xế' : 'Người dùng'}
                    </Typography>
                  </Box>
                </MenuItem>
                <Divider />
                <MenuItem onClick={handleLogout}>
                  <ListItemIcon>
                    <LogoutIcon fontSize="small" />
                  </ListItemIcon>
                  Đăng xuất
                </MenuItem>
              </Menu>
            </>
          ) : (
            /* Login Button - Pill Shape */
            <Button
              variant="contained"
              color="secondary"
              onClick={handleOpenLogin}
              startIcon={<AccountCircleIcon />}
              sx={{
                borderRadius: '20px',
                px: 3,
                fontWeight: 600,
                textTransform: 'none',
              }}
            >
              Đăng nhập
            </Button>
          )}
        </Toolbar>
      </AppBar>

      {/* --- SIDEBAR (DRAWER) --- */}
      <Drawer
        variant="persistent"
        anchor="left"
        open={open}
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            backgroundColor: 'background.default',
            borderRight: '1px solid rgba(0,0,0,0.05)',
            top: '64px',
            height: 'calc(100% - 64px)',
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="subtitle2" color="textSecondary">
            Sidebar Content
          </Typography>
        </Box>
      </Drawer>

      {/* --- MAP AREA (MAIN CONTENT) --- */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          height: '100vh',
          pt: '64px',
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          marginLeft: open ? 0 : `-${DRAWER_WIDTH}px`,
          ...(open && {
            transition: theme.transitions.create('margin', {
              easing: theme.transitions.easing.easeOut,
              duration: theme.transitions.duration.enteringScreen,
            }),
            marginLeft: 0,
          }),
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Outlet />
      </Box>

      {/* --- LOGIN & REGISTER DIALOGS --- */}
      <Login 
        open={loginOpen} 
        onClose={handleCloseLogin}
        onSwitchToRegister={handleSwitchToRegister}
      />
      <Register 
        open={registerOpen} 
        onClose={handleCloseRegister}
        onSwitchToLogin={handleSwitchToLogin}
      />
    </Box>
  );
};

export default MainLayout;