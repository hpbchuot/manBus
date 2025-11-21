// src/hooks/useDriverForm.js
import { useState, useEffect } from "react";
import { driverSchema, driverUpdateSchema } from "../validatation/driverSchema";

export const useDriverForm = (initialData, isEditMode = false) => {
  const [formData, setFormData] = useState(initialData);
  const [errors, setErrors] = useState({});
  const [isSubmitted, setIsSubmitted] = useState(false);

  const validateForm = () => {
    try {
      const schema = isEditMode ? driverUpdateSchema : driverSchema;
      const { error } = schema.validate(formData, { abortEarly: false });

      if (error) {
        const validationErrors = {};
        error.details.forEach((detail) => {
          validationErrors[detail.path[0]] = detail.message;
        });
        setErrors(validationErrors);
        return false;
      }

      setErrors({});
      return true;
    } catch (err) {
      console.error("Validation error:", err);
      return false;
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    if (isSubmitted) {
      try {
        const schema = isEditMode ? driverUpdateSchema : driverSchema;
        const { error } = schema.validate(
          { ...formData, [name]: value },
          { abortEarly: false }
        );

        if (error) {
          const fieldError = error.details.find(
            (detail) => detail.path[0] === name
          );
          setErrors((prev) => ({
            ...prev,
            [name]: fieldError ? fieldError.message : undefined,
          }));
        } else {
          setErrors((prev) => ({ ...prev, [name]: undefined }));
        }
      } catch (err) {
        console.error("Field validation error:", err);
      }
    }
  };

  return {
    formData,
    setFormData,
    errors,
    setErrors,
    isSubmitted,
    setIsSubmitted,
    validateForm,
    handleChange,
  };
};
