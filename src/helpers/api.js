import axios from "axios";

export default function requestApi(
  endpoint,
  method,
  body = null, // Mặc định là null cho các yêu cầu không có body
  responseType = "json",
  params = {} // Thêm params vào đây
) {
  const headers = {
    Accept: "application/json",
    "Content-Type": "application/json",

  };

  const instance = axios.create({ headers });

  // Interceptors request để thêm Authorization token nếu có
  instance.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem("access_token");
      if (token) {
        config.headers["Authorization"] = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Interceptors response để xử lý token hết hạn và refresh token
  instance.interceptors.response.use(
    (response) => {
      return response;
    },
    async (error) => {
      const originalConfig = error.config;
      if (error.response && error.response.status === 401) {
        try {
          const result = await instance.post(
            `${process.env.REACT_APP_API_URL}/auth/refresh-token`,
            {
              refresh_token: localStorage.getItem("refresh_token"),
            }
          );
          const { access_token, refresh_token } = result.data;
          localStorage.setItem("access_token", access_token);
          localStorage.setItem("refresh_token", refresh_token);
          originalConfig.headers["Authorization"] = `Bearer ${access_token}`;

          return instance(originalConfig);
        } catch (err) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
          return Promise.reject(err);
        }
      }
      return Promise.reject(error);
    }
  );

  // Truyền params vào trong config cho yêu cầu GET
  return instance.request({
    method: method,
    url: `${process.env.REACT_APP_API_URL}${endpoint}`,
    data: body, // Dành cho các yêu cầu POST, PUT, PATCH
    params: params, // Dành cho các yêu cầu GET
    responseType: responseType,
  });
}
