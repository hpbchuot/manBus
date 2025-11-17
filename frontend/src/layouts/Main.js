// import React, { useState } from "react";
// import Header from "./Header";
// import Sidebar from "./Sidebar";
// import { Outlet } from "react-router-dom";
// import { Box } from "@mui/material";

// const Main = () => {
//   const [drawerOpen, setDrawerOpen] = useState(false);
//   const [role] = useState(() => {
//     const savedRole = localStorage.getItem("role");
//     switch (savedRole) {
//       case "2":
//         return "manager";
//       case "3":
//         return "admin";
//       case "4":
//         return "driver";
//       default:
//         return "user";
//     }
//   });

//   const toggleDrawer = () => {
//     setDrawerOpen(!drawerOpen);
//   };

//   return (
//     <Box sx={{ height: "100vh", display: "flex", flexDirection: "column" }}>
//       {/* Header với z-index cao hơn để luôn nổi trên cùng */}
//       <Header
//         toggleSidebar={toggleDrawer}
//         sx={{
//           zIndex: 1300,
//           backgroundColor: "white",
//           color: "black",
//           boxShadow: "none",
//           borderBottom: "1px solid #e0e0e0",
//         }}
//       />

//       {/* Container chính */}
//       <Box
//         sx={{
//           display: "flex",
//           flex: 1,
//           position: "relative",
//           overflow: "hidden",
//         }}
//       >
//         {/* Sidebar với position fixed khi mở */}
//         <Sidebar
//           drawerOpen={drawerOpen}
//           toggleDrawer={toggleDrawer}
//           role={role}
//         />

//         {/* Content area */}
//         <Box
//           sx={{
//             flex: 1,
//             position: "relative",
//             overflow: "hidden",
//           }}
//         >
//           <Outlet />
//         </Box>
//       </Box>
//     </Box>
//   );
// };

// export default Main;
import React, { useState } from "react";
import Header from "./Header";
import Sidebar from "./Sidebar";
import { Outlet } from "react-router-dom";
import { Box } from "@mui/material";

const Main = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [role] = useState(() => {
    const savedRole = localStorage.getItem("role");
    switch (savedRole) {
      case "2":
        return "manager";
      case "3":
        return "admin";
      case "4":
        return "driver";
      default:
        return "user";
    }
  });

  const toggleDrawer = () => setDrawerOpen(!drawerOpen);

  return (
    <Box sx={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Header */}
      <Header />

      {/* Main Content */}
      <Box
        sx={{
          position: "relative",
          flex: 1,
          overflow: "hidden",
          display: "flex",
        }}
      >
        {/* Sidebar with Control Bar */}
        <Box>
          <Sidebar
            drawerOpen={drawerOpen}
            toggleDrawer={setDrawerOpen}
            role={role}
          />
        </Box>

        {/* Map Content */}
        <Box
          sx={{
            flex: 1,
            height: "100%",
            overflow: "auto",
          }}
        >
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default Main;
