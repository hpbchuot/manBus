import React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import theme from './config/theme'; 
import MainLayout from './layouts/MainLayout';
import BusMap from './features/map/components/BusMap';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Component tạm để test
const MapPlaceholder = () => (
  <div style={{ width: '100%', height: '100%', background: '#e0e0e0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
    <h2>Khu vực bản đồ (Map Area)</h2>
  </div>
);

function App() {
  return (
    <ThemeProvider theme={theme}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<BusMap />} />
            
          </Route>
        </Routes>
      </BrowserRouter>
      
      <ToastContainer position="top-right" />
    </ThemeProvider>
  );
}

export default App;