import React from "react";
import {
  Paper,
  Box,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Button,
  Autocomplete,
  InputBase,
  TextField,
  Popper,
} from "@mui/material";
import {
  Close as CloseIcon,
  DirectionsCar as DirectionsCarIcon,
  Bookmark as BookmarkIcon,
  NearMe as NearMeIcon,
  Share as ShareIcon,
  Edit as EditIcon,
  Add as AddIcon,
  History as HistoryIcon,
  Search as SearchIcon,
  LocationOn as LocationOnIcon,
  DirectionsBus as DirectionsBusIcon,
  ChevronLeft as ChevronLeftIcon,
} from "@mui/icons-material";

const ExpandableSearchPanel = ({
  expanded,
  onToggleExpand,
  searchMode,
  onSearchModeChange,
  selectedBus,
  listBus,
  onBusSelect,
  searchValue,
  onSearchValueChange,
}) => {
  const menuItems = [
    { icon: <EditIcon />, text: "Đề xuất chỉnh sửa về10P. Phạm Văn Bạch" },
    { icon: <AddIcon />, text: "Thêm địa điểm bị thiếu" },
    { icon: <AddIcon />, text: "Thêm doanh nghiệp của bạn" },
    { icon: <AddIcon />, text: "Thêm nhãn" },
    { icon: <HistoryIcon />, text: "Hoạt động của bạn trên Maps" },
  ];
  const handleSearchModeChange = (mode) => {
    if (mode !== searchMode) {
      // Reset các giá trị tìm kiếm
      onSearchValueChange("");
      onBusSelect(null, null);
      // Chuyển mode
      onSearchModeChange(mode);
    }
  };
  return (
    <Paper
      sx={{
        position: "absolute",
        top: 8,
        left: 8,
        width: 400,
        maxHeight: expanded ? "calc(100vh - 16px)" : "auto",
        height: expanded ? "calc(100vh - 16px)" : "auto",
        borderRadius: 2,
        transition: "width 0.3s ease",
        zIndex: 1200,
        ml: "5%",
      }}
    >
      <Box sx={{ display: "flex", alignItems: "flex-start" }}>
        {/* Search Box - Always visible */}
        <Box
          sx={{ flex: 1, p: "2px 4px", display: "flex", alignItems: "center" }}
        >
          <IconButton sx={{ p: "10px", color: "#5f6368" }}>
            <SearchIcon />
          </IconButton>

          <Box sx={{ flex: 1 }}>
            {searchMode === "location" ? (
              <InputBase
                sx={{
                  ml: 1,
                  flex: 1,
                  fontSize: "14px",
                  color: "#3c4043",
                }}
                placeholder="Tìm kiếm địa điểm..."
                value={searchValue}
                onChange={(e) => onSearchValueChange(e.target.value)}
              />
            ) : (
              <Autocomplete
                value={selectedBus}
                onChange={onBusSelect}
                disablePortal
                options={listBus}
                getOptionLabel={(option) =>
                  `${option.bus_id} - ${option.name} (${option.plate_number})`
                }
                renderOption={(props, option) => (
                  <li
                    {...props}
                    style={{
                      padding: "8px 12px",
                      display: "flex",
                      alignItems: "center",
                    }}
                  >
                    <DirectionsBusIcon sx={{ mr: 1, color: "#1a73e8" }} />
                    {`${option.bus_id} - ${option.name} (${option.plate_number})`}
                  </li>
                )}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    variant="standard"
                    placeholder="Tìm kiếm xe bus..."
                    InputProps={{
                      ...params.InputProps,
                      disableUnderline: true,
                      sx: {
                        fontSize: "14px",
                        color: "#3c4043",
                        "& .MuiAutocomplete-input": {
                          padding: "0 !important",
                          ml: 1,
                        },
                      },
                    }}
                  />
                )}
                slots={{
                  popper: (props) => (
                    <Popper
                      {...props}
                      sx={{
                        width: "400px !important",
                        transform: "translateX(1px) translateY(51px)!important",
                        "& .MuiPaper-root": {
                          marginTop: "8px !important",
                        },
                      }}
                      modifiers={[
                        {
                          name: "offset",
                          options: {
                            offset: [0, 8],
                          },
                        },
                      ]}
                      placement="bottom-start"
                    />
                  ),
                }}
                slotProps={{
                  paper: {
                    elevation: 3,
                    sx: {
                      borderRadius: "8px",
                      border: "1px solid rgba(60,64,67,.15)",
                      boxShadow: "0 2px 6px rgba(60,64,67,.15)",
                    },
                  },
                }}
                sx={{
                  width: "100%",
                  "& .MuiAutocomplete-popupIndicator": { display: "none" },
                  "& .MuiAutocomplete-clearIndicator": { display: "none" },
                  "& .MuiAutocomplete-listbox": {
                    padding: "4px 0",
                    "& .MuiAutocomplete-option": {
                      padding: "8px 12px",
                      '&[aria-selected="true"]': {
                        backgroundColor: "rgba(26, 115, 232, 0.08)",
                      },
                      "&.Mui-focused": {
                        backgroundColor: "rgba(26, 115, 232, 0.04)",
                      },
                    },
                  },
                }}
              />
            )}
          </Box>

          <Divider sx={{ height: 28, m: 0.5 }} orientation="vertical" />

          <IconButton
            onClick={() => handleSearchModeChange("location")}
            sx={{
              p: "10px",
              color: searchMode === "location" ? "#1a73e8" : "#5f6368",
            }}
          >
            <LocationOnIcon />
          </IconButton>

          <IconButton
            onClick={() => handleSearchModeChange("bus")}
            sx={{
              p: "10px",
              color: searchMode === "bus" ? "#1a73e8" : "#5f6368",
            }}
          >
            <DirectionsBusIcon />
          </IconButton>
        </Box>

        {/* Toggle Expand Button */}
        <IconButton
          onClick={onToggleExpand}
          sx={{
            p: "10px",
            color: "#5f6368",
            transform: expanded ? "rotate(0deg)" : "rotate(180deg)",
            transition: "transform 0.3s ease",
          }}
        >
          <ChevronLeftIcon />
        </IconButton>
      </Box>

      {/* Expanded Content */}
      {expanded && (
        <>
          <Divider />

          {/* Menu Items */}
          <List sx={{ bgcolor: "white" }}>
            {menuItems.map((item, index) => (
              <React.Fragment key={index}>
                <ListItem button>
                  <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
                  <ListItemText
                    primary={item.text}
                    primaryTypographyProps={{
                      fontSize: "0.875rem",
                      color: "#3c4043",
                    }}
                  />
                </ListItem>
                {index < menuItems.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </>
      )}
    </Paper>
  );
};

export default ExpandableSearchPanel;
