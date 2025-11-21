// src/validations/driverSchema.js
import Joi from "joi";

export const driverSchema = Joi.object({
  name: Joi.string().required().min(2).max(50).messages({
    "string.empty": "Tên không được để trống",
    "string.min": "Tên phải có ít nhất {#limit} ký tự",
    "string.max": "Tên không được vượt quá {#limit} ký tự",
  }),

  username: Joi.string()
    .min(8)
    .max(30)
    .pattern(/^[a-zA-Z0-9_]+$/)
    .required()
    .messages({
      "string.empty": "Username không được để trống",
      "string.min": "Username phải có ít nhất {#limit} ký tự",
      "string.max": "Username không được vượt quá {#limit} ký tự",
      "string.pattern.base":
        "Username chỉ được chứa chữ cái, số và dấu gạch dưới",
    }),

  password: Joi.string()
    .min(8)
    .pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/)
    .required()
    .messages({
      "string.empty": "Mật khẩu không được để trống",
      "string.min": "Mật khẩu phải có ít nhất {#limit} ký tự",
      "string.pattern.base":
        "Mật khẩu phải chứa ít nhất 1 chữ hoa, 1 chữ thường và 1 số",
    }),

  email: Joi.string()
    .email({ tlds: { allow: false } })
    .required()
    .messages({
      "string.empty": "Email không được để trống",
      "string.email": "Email không hợp lệ",
    }),

  phone: Joi.string()
    .pattern(/^[0-9]{10,11}$/)
    .required()
    .messages({
      "string.empty": "Số điện thoại không được để trống",
      "string.pattern.base": "Số điện thoại phải có 10-11 chữ số",
    }),

  blx: Joi.string()
    .required()
    .pattern(/^[A-Z0-9]{8,12}$/)
    .messages({
      "string.empty": "Số bằng lái xe không được để trống",
      "string.pattern.base": "Số bằng lái xe không hợp lệ",
    }),

  bus_id: Joi.string().required().messages({
    "string.empty": "Vui lòng chọn xe",
    "any.required": "Vui lòng chọn xe",
  }),
});

export const driverUpdateSchema = driverSchema.keys({
  password: Joi.string().allow("").optional(),
  username: Joi.string().optional(),
  blx: Joi.string().optional(),
});
