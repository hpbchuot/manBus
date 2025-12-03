import React, { useState, useEffect } from 'react';
import { Box, Drawer, IconButton, useMediaQuery, useTheme, Tabs, Tab } from '@mui/material';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import DirectionsBusIcon from '@mui/icons-material/DirectionsBus';
import BusMap from '@/components/map/BusMap';
import StopsList from '@/components/map/StopsList';
import BusList from '@/components/bus/BusList';
import BusInfoPanel from '@/components/bus/BusInfoPanel';
import { useRoute } from '@/hooks/useBusData';
import type { Stop } from '@/types/stop';
import type { Route } from '@/types/route';
import type { Bus } from '@/types/bus';

const SIDEBAR_WIDTH = 380;

const HomePage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);
  const [activeTab, setActiveTab] = useState<'stops' | 'buses'>('stops');
  const [selectedStop, setSelectedStop] = useState<Stop | null>(null);
  const [selectedBus, setSelectedBus] = useState<Bus | null>(null);
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);

  // Fetch route data when a bus is selected
  const { data: routeData } = useRoute(selectedBus?.routeId || 0);

  // Update selectedRoute when route data is fetched
  useEffect(() => {
    if (routeData && selectedBus) {
      setSelectedRoute(routeData);
    } else if (!selectedBus) {
      setSelectedRoute(null);
    }
  }, [routeData, selectedBus]);

  const handleStopSelect = (stop: Stop) => {
    setSelectedStop(stop);
    setSelectedBus(null); // Clear bus selection when stop is selected
    setSelectedRoute(null); // Clear route when stop is selected
    // TODO: Có thể zoom map đến vị trí stop này
    console.log('Selected stop:', stop);
  };

  const handleBusSelect = (bus: Bus) => {
    setSelectedBus(bus);
    setSelectedStop(null); // Clear stop selection when bus is selected
    console.log('Selected bus:', bus);
  };

  const handleBusInfoClose = () => {
    setSelectedBus(null);
  };

  const handleTrackBus = (busId: number) => {
    console.log('Track bus:', busId);
    // TODO: Implement bus tracking - center map on bus and follow it
  };

  const handleViewRoute = (routeId: number) => {
    console.log('View route:', routeId);
    // TODO: Implement route viewing - display route on map
  };

  const handleRouteClick = (route: Route) => {
    setSelectedRoute(route);
    console.log('Selected route:', route);
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: 'stops' | 'buses') => {
    setActiveTab(newValue);
    setSelectedStop(null);
    setSelectedBus(null);
    setSelectedRoute(null);
  };

  return (
    <Box sx={{ display: 'flex', height: '100%', position: 'relative' }}>
      {/* Sidebar với danh sách Stops và Buses */}
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
            display: 'flex',
            flexDirection: 'column',
          },
        }}
      >
        {/* Tabs for switching between Stops and Buses */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="fullWidth"
            sx={{
              minHeight: 48,
              '& .MuiTab-root': {
                minHeight: 48,
                textTransform: 'none',
                fontWeight: 600,
              },
            }}
          >
            <Tab
              label="Điểm dừng"
              value="stops"
              icon={<LocationOnIcon />}
              iconPosition="start"
            />
            <Tab
              label="Xe bus"
              value="buses"
              icon={<DirectionsBusIcon />}
              iconPosition="start"
            />
          </Tabs>
        </Box>

        {/* Content based on active tab */}
        <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
          {activeTab === 'stops' ? (
            <StopsList
              onStopSelect={handleStopSelect}
              selectedStopId={selectedStop?.id}
            />
          ) : (
            <BusList
              onBusSelect={handleBusSelect}
              selectedBusId={selectedBus?.busId}
            />
          )}
        </Box>
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
          position: 'relative',
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

        {/* Bus Info Panel - shown when a bus is selected */}
        {selectedBus && (
          <BusInfoPanel
            busId={selectedBus.busId}
            onClose={handleBusInfoClose}
            onTrackBus={handleTrackBus}
            onViewRoute={handleViewRoute}
          />
        )}
      </Box>
    </Box>
  );
};

export default HomePage;