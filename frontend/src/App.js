import "./App.css";
import "react-toastify/dist/ReactToastify.css";
import { Routes, Route } from "react-router-dom";
import { useEffect, useState } from "react";
import Main from "./layouts/Main";
import Dashboard from "./components/Dashboard";
import Login from "./components/Login";
import Register from "./components/Register";
import PrivateRoutes from "./layouts/PrivateRoutes";
import PublicRoutes from "./layouts/PublicRoutes";
import RoleBasedRoute from "./layouts/RoleBasedRoute";
import ProtectManRoutes from "./layouts/ProtectManRoutes";
import Layout from "./layouts/Layout";
import UserList from "./components/user/UserList";
import Map from "./components/Map";
import ManageUser from "./components/admin/ManageUser";
import QLNguoiDung from "./components/manager/QLNguoiDung";
import Admin from "./components/admin/AdminDashboard";
import Menu from "./components/admin/Menu";
import AdminDashboard from "./components/admin/AdminDashboard";
import QLTaiXe from "./components/manager/QLTaiXe";
import Feedback from "./components/manager/Feedback";
import MapDriver from "./components/driver/MapDriver";
import RouteMap from "./components/test";
function App() {
  useEffect(() => {
    console.log("1111");
  });
  return (
    <Routes>
      <Route element={<Layout />}>
        {/* man route */}



          <Route path="/" element={<Map />} />
          <Route path="/test123" element={<RouteMap />} />
          <Route path="/driver" element={<MapDriver />} />


          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />


        {/* Private Routes */}


        {/* Role-Based Routes */}

      </Route>
    </Routes>
  );
}

export default App;
