import React from "react";
import { Box, Button, Typography, Modal } from "@mui/material";

const ConfirmDeleteModal = ({ open, onClose, onConfirm, message }) => {
  const style = {
    position: "absolute",
    top: "40%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    width: 400,
    bgcolor: "background.paper",
    border: "2px solid red",
    boxShadow: 10,
    p: 4,
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="confirm-delete-title"
      aria-describedby="confirm-delete-description"
      slotProps={{
        backdrop: {
          style: { backgroundColor: "transparent" },
        },
      }}
    >
      <Box sx={style}>
        <Typography
          id="confirm-delete-title"
          variant="h6"
          component="h2"
          textAlign="center"
        >
          Xác nhận xóa
        </Typography>
        <Typography
          id="confirm-delete-description"
          sx={{ mt: 2, textAlign: "center" }}
        >
          {message || "Bạn có chắc chắn muốn xóa không?"}
        </Typography>
        <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
          <Button
            variant="contained"
            color="error"
            onClick={onConfirm}
            sx={{ mr: 2 }}
          >
            Yes
          </Button>
          <Button variant="outlined" onClick={onClose}>
            No
          </Button>
        </Box>
      </Box>
    </Modal>
  );
};

export default ConfirmDeleteModal;
