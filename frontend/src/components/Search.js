import React, { useState } from "react";
import {
  Paper,
  InputBase,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from "@mui/material";
import {
  Search as SearchIcon,
  MyLocation as MyLocationIcon,
  History as HistoryIcon,
} from "@mui/icons-material";
import { styled } from "@mui/material/styles";

// Custom styled Paper component
const SearchContainer = styled(Paper)(({ theme }) => ({
  padding: "2px 4px",
  display: "flex",
  alignItems: "center",
  width: "100%",
  maxWidth: 400,
  boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
  borderRadius: 8,
  margin: "8px auto",
}));

const SearchBox = () => {
  const [searchValue, setSearchValue] = useState("");
  const [showResults, setShowResults] = useState(false);

  // Mock recent searches
  const recentSearches = [
    "10 Phố Phạm Văn Bạch Dịch Vọng, Cầu Giấy",
    "CIT Building Phố Duy Tân, Dịch Vọng Hậu",
    "113 Phố Kim Hoa Phương Liên, Đống Đa",
  ];

  const handleFocus = () => {
    setShowResults(true);
  };

  return (
    <div style={{ position: "relative", maxWidth: 400, margin: "0 auto" }}>
      <SearchContainer elevation={1}>
        <IconButton sx={{ p: "10px" }}>
          <SearchIcon />
        </IconButton>
        <InputBase
          sx={{ ml: 1, flex: 1 }}
          placeholder="Tìm kiếm trên Google Maps"
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          onFocus={handleFocus}
        />
        <IconButton sx={{ p: "10px" }}>
          <MyLocationIcon color="primary" />
        </IconButton>
      </SearchContainer>

      {showResults && (
        <Paper
          sx={{
            position: "absolute",
            top: "100%",
            left: 0,
            right: 0,
            mt: 1,
            maxHeight: 400,
            overflow: "auto",
            borderRadius: 2,
            boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
          }}
        >
          <List>
            {recentSearches.map((search, index) => (
              <React.Fragment key={index}>
                <ListItem button>
                  <ListItemIcon>
                    <HistoryIcon />
                  </ListItemIcon>
                  <ListItemText primary={search} />
                </ListItem>
                {index < recentSearches.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Paper>
      )}
    </div>
  );
};

export default SearchBox;
