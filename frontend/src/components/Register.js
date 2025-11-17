import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import requestApi from "../helpers/api";
import * as actions from "../redux/actions";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
const Register = () => {
  const [DKData, setDKData] = useState({});
  const [formErrors, setFormErrors] = useState({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const onChange = (event) => {
    console.log("change:", DKData);
    let target = event.target;
    setDKData({
      ...DKData,
      [target.name]: target.value,
    });
  };
  useEffect(() => {
    if (isSubmitted) {
      validateForm();
    }
    console.log("ef:", DKData);
  }, [DKData]);

  const validateForm = () => {
    let isValid = true;
    const errors = {};
    if (DKData.email === "" || DKData.email === undefined) {
      errors.email = "Hãy nhập email";
    } else {
      let valid = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(
        DKData.email
      );
      if (!valid) {
        errors.email = "Email không hợp lệ";
      }
    }
    const phonePattern = /^[0-9]{10,11}$/;
    if (!DKData.phone) {
      errors.phone = "Hãy nhập số điện thoại";
    } else if (!phonePattern.test(DKData.phone)) {
      errors.phone = "Số điện thoại không hợp lệ";
    }
    if (DKData.username?.length < 8) {
      errors.username = "Username tối thiểu 8 kí tự";
    }
    if (DKData.password === "" || DKData.password === undefined) {
      errors.password = "Hãy nhập mật khẩu";
    }
    if (
      DKData.password === "" ||
      (DKData.password === undefined || DKData.cfpassword) !== DKData.password
    ) {
      errors.cfpassword = "Hãy nhập lại mật khẩu trùng khớp";
    }

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      isValid = false;
    } else {
      setFormErrors({});
    }

    return isValid;
  };

  const onSubmit = () => {
    console.log(DKData);
    let valid = validateForm();
    if (valid) {
      //request register api
      console.log("request register api");
      dispatch(actions.controlLoading(true));
      requestApi("/user/register", "POST", DKData)
        .then((res) => {
          console.log(res);
          console.log("Response:", res);
          dispatch(actions.controlLoading(false));
          toast.success(res.data.message, {
            position: "top-right",
            autoClose: 3000,
          });
          navigate("/login");
        })
        .catch((error) => {
          // Xử lý các lỗi do kết nối hoặc không có phản hồi từ server
          console.error("Request failed:", error);
          dispatch(actions.controlLoading(false));
          toast.error(error.response.data.message, {
            position: "top-center",
            autoClose: 3000,
          });
        });
    }

    setIsSubmitted(true);
  };
  return (
    <div id="layoutAuthentication" className="bg-info">
      <div id="layoutAuthentication_content">
        <main>
          <div className="container">
            <div className="row justify-content-center">
              <div className="col-lg-7">
                <div className="card shadow-lg border-0 rounded-lg mt-5">
                  <div className="card-header">
                    <h3 className="text-center font-weight-light my-4">
                      Đăng ký tài khoản
                    </h3>
                  </div>
                  <div className="card-body">
                    <form>
                      <div className="row mb-3">
                        <div className="col-md-6">
                          <div className="form-floating mb-3 mb-md-0">
                            <input
                              className="form-control"
                              id="inputFirstName"
                              type="text"
                              name="fname"
                              onChange={onChange}
                              placeholder="Enter your first name"
                            />
                            <label htmlFor="inputFirstName">Họ</label>
                          </div>
                        </div>
                        <div className="col-md-6">
                          <div className="form-floating">
                            <input
                              className="form-control"
                              id="inputLastName"
                              type="text"
                              name="lname"
                              onChange={onChange}
                              placeholder="Enter your last name"
                            />
                            <label htmlFor="inputLastName">Tên</label>
                          </div>
                        </div>
                      </div>
                      <div className="form-floating mb-3">
                        <input
                          className="form-control"
                          id="inputusername"
                          type="text"
                          name="username"
                          placeholder="Enter your username"
                          onChange={onChange}
                        />
                        <label htmlFor="inputusername">Username</label>
                        {formErrors.username && (
                          <p style={{ color: "red" }}>{formErrors.username}</p>
                        )}
                      </div>
                      <div className="form-floating mb-3">
                        <input
                          className="form-control"
                          id="inputEmail"
                          type="email"
                          name="email"
                          onChange={onChange}
                          placeholder="name@example.com"
                        />
                        <label htmlFor="inputEmail">Email</label>
                        {formErrors.email && (
                          <p style={{ color: "red" }}>{formErrors.email}</p>
                        )}
                      </div>
                      <div className="form-floating mb-3">
                        <input
                          className="form-control"
                          id="inputsdt"
                          type="text"
                          name="phone"
                          onChange={onChange}
                          placeholder="name@example.com"
                        />
                        <label htmlFor="inputsdt">Số điện thoại</label>
                        {formErrors.phone && (
                          <p style={{ color: "red" }}>{formErrors.phone}</p>
                        )}
                      </div>
                      <div className="row mb-3">
                        <div className="col-md-6">
                          <div className="form-floating mb-3 mb-md-0">
                            <input
                              className="form-control"
                              id="inputPassword"
                              type="password"
                              name="password"
                              onChange={onChange}
                              placeholder="Create a password"
                            />
                            <label htmlFor="inputPassword">Mật khẩu</label>
                            {formErrors.password && (
                              <p style={{ color: "red" }}>
                                {formErrors.password}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="col-md-6">
                          <div className="form-floating mb-3 mb-md-0">
                            <input
                              className="form-control"
                              id="inputPasswordConfirm"
                              type="password"
                              name="cfpassword"
                              onChange={onChange}
                              placeholder="Confirm password"
                            />
                            <label htmlFor="inputPasswordConfirm">
                              Xác nhận mật khẩu
                            </label>
                            {formErrors.cfpassword && (
                              <p style={{ color: "red" }}>
                                {formErrors.cfpassword}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="mt-4 mb-0">
                        <div className="d-grid">
                          <a
                            className="btn btn-primary btn-block"
                            onClick={onSubmit}
                          >
                            Tạo
                          </a>
                        </div>
                      </div>
                    </form>
                  </div>
                  <div className="card-footer text-center py-3">
                    <div className="small">
                      <a href="/login">Đã có tài khoản? Hãy đăng nhập</a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
      <div id="layoutAuthentication_footer">
        <footer className="py-4 bg-light mt-auto">
          <div className="container-fluid px-4">
            <div className="d-flex align-items-center justify-content-between small">
              <div className="text-muted">
                Copyright &copy; Your Website 2023
              </div>
              <div>
                <a href="#">Privacy Policy</a>
                &middot;
                <a href="#">Terms &amp; Conditions</a>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Register;
