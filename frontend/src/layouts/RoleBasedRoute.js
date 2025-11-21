import { Outlet } from "react-router-dom";

const RoleBasedRoute = () => {
  const user = JSON.parse(localStorage.getItem("admin")); // Lấy user từ localStorage

  const ErrorComponent = () => (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Lỗi truy cập</h1>
      <p>Bạn không có quyền truy cập vào trang này.</p>
      <a href="/">Quay về trang chủ</a>
    </div>
  );

  return user ? <Outlet /> : <ErrorComponent />;
};

export default RoleBasedRoute;
