// components/ControlPanel.jsx
import React from "react";
import { Box, Button } from "@mui/material";
import {
  Stop as StopIcon,
  Feedback as FeedbackIcon,
} from "@mui/icons-material";
import { useTranslation } from "react-i18next";

const ControlPanel = ({ onStopTracking, onFeedback, isLoggedIn }) => {
  const { t } = useTranslation();

  return (
    <Box
      sx={{
        position: "absolute",
        bottom: "20px",
        left: "50%",
        transform: "translateX(-50%)",
        zIndex: 1000,
        display: "flex",
        gap: 2,
        backgroundColor: "rgba(255, 255, 255, 0.9)",
        padding: "8px",
        borderRadius: "4px",
        boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
      }}
    >
      <Button
        variant="contained"
        color="error"
        startIcon={<StopIcon />}
        onClick={onStopTracking}
      >
        {t("Stop")}
      </Button>

      {isLoggedIn && (
        <Button
          variant="contained"
          color="success"
          startIcon={<FeedbackIcon />}
          onClick={onFeedback}
        >
          {t("Feedback")}
        </Button>
      )}
    </Box>
  );
};

export default ControlPanel;
