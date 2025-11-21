import i18next from "i18next";
import { initReactI18next } from "react-i18next";
import Backend from "i18next-http-backend"; // Import i18next-http-backend

// Lấy ngôn ngữ từ localStorage hoặc mặc định là 'vi'
const savedLang = localStorage.getItem("i18nextLng") || "vi";

i18next
  .use(Backend) // Use the backend plugin to load resources
  .use(initReactI18next) // Integrate i18next with react-i18next
  .init({
    lng: savedLang, // Set the language to the saved language or default
    fallbackLng: "en", // Fallback language if the current language is not available
    interpolation: {
      escapeValue: false, // React escapes values by default
    },
    backend: {
      loadPath: "/locales/{{lng}}.json", // Define the path to your translation files
    },
  });

export default i18next;
