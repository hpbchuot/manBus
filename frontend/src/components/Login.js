import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import requestApi from "../helpers/api";
import { toast } from "react-toastify";
import { useDispatch } from "react-redux";
import * as actions from "../redux/actions";
import { useTranslation } from "react-i18next";

const Login = () => {
  const { t } = useTranslation();
  //console.log(t("login.title"));
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [loginData, setLoginData] = useState({});
  const [formErrors, setFormErrors] = useState({});
  const [isSubmitted, setIsSubmitted] = useState(false);

  const onChange = (event) => {
    let target = event.target;
    setLoginData({
      ...loginData,
      [target.name]: target.value,
    });
  };

  useEffect(() => {
    if (isSubmitted) {
      validateForm();
    }
  }, [loginData]);

  const validateForm = () => {
    let isValid = true;
    const errors = {};
    if (!loginData.email) {
      errors.email = t("login.errorEmail");
    }
    if (!loginData.password) {
      errors.password = t("login.errorPassword");
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
    let valid = validateForm();
    if (valid) {
      dispatch(actions.controlLoading(true));
      requestApi("/auth/login", "POST", loginData)
        .then((res) => {
          localStorage.setItem("access_token", res.data.Authorization);
          localStorage.setItem("role", res.data.role);
          localStorage.setItem("admin", res.data.admin);
          localStorage.setItem("refresh_token", res.data.refresh_token);
          toast.success(res.data.message, {
            position: "top-right",
            autoClose: 3000,
          });
          dispatch(actions.controlLoading(false));
          if (!res.data.admin) {
            switch (res.data.role) {
              case 4:
                navigate("/driver");
                break;
              default:
                navigate("/");
            }
          } else navigate("/admin");
        })
        .catch((err) => {
          console.log(err);
          dispatch(actions.controlLoading(false));
          if (err.response) {
            if ((err.response.status = "422")) {
              toast.error("Dữ liệu không hợp lệ", {
                position: "top-right",
                autoClose: 3000,
              });
            } else
              toast.error(err.response.data.message, {
                position: "top-right",
                autoClose: 3000,
              });
          } else {
            toast.error(t("serverError"), {
              position: "top-right",
              autoClose: 3000,
            });
          }
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
              <div className="col-lg-5">
                <div className="card shadow-lg border-0 rounded-lg mt-5">
                  <div className="card-header">
                    <h3 className="text-center font-weight-light my-4">
                      {t("login.title")}
                    </h3>
                  </div>
                  <div className="card-body">
                    <form>
                      <div className="form-floating mb-3">
                        <input
                          className="form-control"
                          type="email"
                          name="email"
                          onChange={onChange}
                          placeholder={t("login.email")}
                        />
                        <label>{t("login.email")}</label>
                        {formErrors.email && (
                          <p style={{ color: "red" }}>{formErrors.email}</p>
                        )}
                      </div>
                      <div className="form-floating mb-3">
                        <input
                          className="form-control"
                          name="password"
                          type="password"
                          onChange={onChange}
                          placeholder={t("login.password")}
                        />
                        <label>{t("login.password")}</label>
                        {formErrors.password && (
                          <p style={{ color: "red" }}>{formErrors.password}</p>
                        )}
                      </div>
                      <div className="d-flex align-items-center justify-content-between mt-4 mb-0">
                        <a className="small" href="password.html">
                          {t("login.forgotPassword")}
                        </a>
                        <button
                          className="btn btn-primary"
                          type="button"
                          onClick={onSubmit}
                        >
                          {t("login.loginButton")}
                        </button>
                      </div>
                    </form>
                  </div>
                  <div className="card-footer text-center py-3">
                    <div className="small">
                      <Link to="/register">{t("login.noAccount")}</Link>
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
                <a href="#">{t("privacyPolicy")}</a>
                &middot;
                <a href="#">{t("termsAndConditions")}</a>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Login;
