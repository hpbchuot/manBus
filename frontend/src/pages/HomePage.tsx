import React, { useState } from 'react';
import { Box, Drawer, IconButton, useMediaQuery, useTheme } from '@mui/material';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import BusMap from '@/components/map/BusMap';
import StopsList from '@/components/map/StopsList';
import type { Stop } from '@/types/stop';
import type { Route } from '@/types/route';

const SIDEBAR_WIDTH = 380;

const HomePage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);
  const [selectedStop, setSelectedStop] = useState<Stop | null>(null);
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);

  const handleStopSelect = (stop: Stop) => {
    setSelectedStop(stop);
    // TODO: Có thể zoom map đến vị trí stop này
    console.log('Selected stop:', stop);
  };

  const handleRouteClick = (route: Route) => {
    setSelectedRoute(route);
    console.log('Selected route:', route);
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex', height: '100%', position: 'relative' }}>
      {/* Sidebar với danh sách Stops */}
      <Drawer
        variant="persistent"
        anchor="left"
        open={sidebarOpen}
        sx={{
          width: sidebarOpen ? SIDEBAR_WIDTH : 0,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: SIDEBAR_WIDTH,
            boxSizing: 'border-box',
            position: 'relative',
            border: 'none',
            bgcolor: 'background.default',
          },
        }}
      >
        <StopsList
          onStopSelect={handleStopSelect}
          selectedStopId={selectedStop?.id}
        />
      </Drawer>

      {/* Toggle Button */}
      <IconButton
        onClick={toggleSidebar}
        sx={{
          position: 'absolute',
          left: sidebarOpen ? SIDEBAR_WIDTH : 0,
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 1001,
          bgcolor: 'background.paper',
          boxShadow: 2,
          '&:hover': {
            bgcolor: 'background.paper',
            boxShadow: 4,
          },
          transition: theme.transitions.create('left', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        }}
      >
        {sidebarOpen ? <ChevronLeftIcon /> : <ChevronRightIcon />}
      </IconButton>

      {/* Map Area */}
      <Box
        sx={{
          flexGrow: 1,
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          marginLeft: sidebarOpen ? 0 : 0,
        }}
      >
        <BusMap
          selectedRoute={selectedRoute}
          onStopClick={handleStopSelect}
          onRouteClick={handleRouteClick}
        />
      </Box>
    </Box>
  );
};

export default HomePage;