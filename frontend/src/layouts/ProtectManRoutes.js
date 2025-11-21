import { Outlet } from "react-router-dom";

const ProtectManRoutes = () => {
  const role = JSON.parse(localStorage.getItem("role")); // Lấy user từ localStorage

  const ErrorComponent = () => (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Lỗi truy cập</h1>
      <p>Bạn không có quyền truy cập vào trang này.</p>
      <a href="/">Quay về trang chủ</a>
    </div>
  );

  return role == 2 ? <Outlet /> : <ErrorComponent />;
};

export default ProtectManRoutes;
