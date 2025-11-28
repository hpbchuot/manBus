// src/config/theme.ts
import { createTheme } from '@mui/material/styles';

// 1. Định nghĩa bảng màu theo design.md
const palette = {
  primary: {
    main: '#00C060', // Xanh lá chủ đạo
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#27AE60', // Màu hover hoặc điểm nhấn
  },
  background: {
    default: '#F5F7FA', // Màu nền Sidebar/App
    paper: '#FFFFFF',   // Màu nền Card/Modal
  },
  text: {
    primary: '#333333', // Đen dịu
    secondary: '#757575', // Xám thông tin phụ
  },
  error: {
    main: '#D32F2F',
  },
};

// 2. Tạo Theme
const theme = createTheme({
  palette,
  typography: {
    fontFamily: "'Roboto', 'Be Vietnam Pro', 'Inter', sans-serif",
    button: {
      textTransform: 'none', // Tắt viết hoa toàn bộ chữ cái
      fontWeight: 500,
    },
    h6: {
      fontWeight: 700, // Bold cho tiêu đề
    },
  },
  components: {
    // Override Button mặc định
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '8px', // Bo góc nhẹ mặc định
          fontWeight: 600,
        },
        // Button "Login" đặc biệt trên Header (dạng Pill, nền trắng)
        containedSecondary: {
            backgroundColor: '#FFFFFF',
            color: '#00C060',
            borderRadius: '20px',
            '&:hover': {
                backgroundColor: '#F0F0F0',
            }
        }
      },
    },
    // Override AppBar (Header)
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#00C060',
          boxShadow: '0px 2px 4px -1px rgba(0,0,0,0.2)', // Bóng nhẹ (elevation 2)
        },
      },
    },
    // Override Card
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        },
      },
    },
  },
});

export default theme;