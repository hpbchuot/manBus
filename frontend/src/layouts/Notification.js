import React, { useState, useEffect } from "react";
import {
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from "@mui/material";
import {
  Notifications as NotificationsIcon,
  NotificationsNone as NotificationsNoneIcon,
  Circle as CircleIcon,
} from "@mui/icons-material";
import { useQuery } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import { vi, enUS } from "date-fns/locale";
import requestApi from "../helpers/api";
import { useTranslation } from "react-i18next";

const NotificationMenu = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const { t, i18n } = useTranslation();

  // Fetch notifications
  const { data: notifications = [], refetch } = useQuery({
    queryKey: ["notifications"],
    queryFn: async () => {
      const response = await requestApi("/notifications/get-list", "GET");
      return response.data;
    },
    refetchInterval: 30000, // Poll every 30 seconds
  });

  // Calculate unread notifications
  useEffect(() => {
    const count = notifications.filter((notif) => !notif.read).length;
    setUnreadCount(count);
  }, [notifications]);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationClick = async (notificationId) => {
    try {
      await requestApi(`/notifications/${notificationId}/read`, "PUT");
      refetch(); // Refresh notifications
    } catch (error) {
      console.error("Error marking notification as read:", error);
    }
  };

  const formatDate = (date) => {
    return formatDistanceToNow(new Date(date), {
      addSuffix: true,
      locale: i18n.language === "vi" ? vi : enUS,
    });
  };

  return (
    <>
      <IconButton
        onClick={handleClick}
        sx={{
          color: "#5f6368",
          backgroundColor: "rgba(255, 255, 255, 1)",
          "&:hover": {
            backgroundColor: "rgba(255, 255, 255, 0.95)",
          },
        }}
      >
        <Badge badgeContent={unreadCount} color="error">
          {unreadCount > 0 ? <NotificationsIcon /> : <NotificationsNoneIcon />}
        </Badge>
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        PaperProps={{
          sx: {
            maxHeight: 400,
            width: "350px",
          },
        }}
        transformOrigin={{ horizontal: "right", vertical: "top" }}
        anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
      >
        <Box sx={{ p: 2, borderBottom: 1, borderColor: "divider" }}>
          <Typography variant="h6" component="div">
            {t("notifications")}
          </Typography>
        </Box>

        {notifications.length === 0 ? (
          <MenuItem>
            <Typography variant="body2" color="text.secondary">
              {t("noNotifications")}
            </Typography>
          </MenuItem>
        ) : (
          <List sx={{ p: 0 }}>
            {notifications.map((notification) => (
              <React.Fragment key={notification.id}>
                <ListItem
                  button
                  onClick={() => handleNotificationClick(notification.id)}
                  sx={{
                    backgroundColor: notification.read
                      ? "inherit"
                      : "action.hover",
                  }}
                >
                  <ListItemIcon>
                    {!notification.read && (
                      <CircleIcon color="primary" sx={{ fontSize: 12 }} />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={notification.message}
                    secondary={formatDate(notification.created_at)}
                    primaryTypographyProps={{
                      variant: "body2",
                      color: notification.read
                        ? "text.secondary"
                        : "text.primary",
                    }}
                    secondaryTypographyProps={{
                      variant: "caption",
                    }}
                  />
                </ListItem>
                <Divider />
              </React.Fragment>
            ))}
          </List>
        )}
      </Menu>
    </>
  );
};

export default NotificationMenu;
