# BUSMAP CLONE - FRONTEND DESIGN SPECIFICATIONS
src/
├── assets/          # Ảnh xe, icon tĩnh
├── components/      # UI dùng chung (Button, Table, Modal)
├── config/          # Cấu hình biến môi trường, i18n
├── features/        # (Quan trọng) Chia code theo tính năng
│   ├── auth/        # Login, Register
│   ├── map/         # Các component bản đồ
│   └── dashboard/   # Màn hình thống kê
├── hooks/           # useAppDispatch, useBusData...
├── layouts/         # Khung trang (Sidebar, Header)
├── pages/           # Các trang gán vào Router
├── services/        # Axios instance, API endpoints
├── store/           # Redux store setup
├── types/           # Định nghĩa TypeScript interface
└── utils/           # Hàm format ngày tháng, tính toán

## 1. Tổng quan (Overview)
Dự án xây dựng ứng dụng bản đồ xe buýt tập trung vào trải nghiệm người dùng hiện đại, giao diện sạch (Clean UI), lấy cảm hứng từ BusMap.
* **Tech Stack:** React, Material UI (MUI v5+), React-Leaflet, i18next.
* **Phong cách chủ đạo:** Material Design, Flat, Eco-friendly.

## 2. Bảng màu (Color Palette)
Hệ thống màu sắc dựa trên sự tương phản giữa Xanh lá (Chủ đạo) và Trắng/Xám (Nền).

| Role | Hex Code | Mô tả sử dụng |
| :--- | :--- | :--- |
| **Primary** | `#00C060` | Header nền, Icon active, Các nút hành động chính (trừ Header). |
| **Secondary**| `#27AE60` | Màu hover hoặc các điểm nhấn đậm hơn của Primary. |
| **Bg Default**| `#F5F7FA` | Màu nền của Sidebar (Tạo độ nổi cho các Card trắng). |
| **Bg Paper** | `#FFFFFF` | Màu nền của Card, Modal, và các hộp thoại. |
| **Text Primary**| `#333333` | Tiêu đề, tên tuyến xe, nội dung chính (Đen dịu). |
| **Text Secondary**| `#757575` | Thông tin phụ (Giờ, giá vé). |
| **Warning/Error**| `#D32F2F` | Thông báo lỗi hoặc cảnh báo trễ chuyến. |

## 3. Typography (Kiểu chữ)
* **Font Family:** `Roboto` (Mặc định MUI) hoặc `Inter` / `Be Vietnam Pro` (Khuyến nghị cho tiếng Việt).
* **Weights:**
    * **Bold (700):** Dùng cho Tên tuyến xe (trong Card), Tiêu đề Header.
    * **Medium (500):** Dùng cho các nút bấm (Button), Tab navigation.
    * **Regular (400):** Nội dung thông thường.

## 4. Kiến trúc Bố cục (Layout Architecture)
Sử dụng mô hình **App Shell** với 3 vùng chính:

### A. Global Header (AppBar)
* **Vị trí:** `Fixed` (Luôn hiển thị trên cùng), `zIndex` cao nhất.
* **Style:** Background màu `Primary` (#00C060), đổ bóng nhẹ (`elevation={2}`).
* **Thành phần (Trái sang Phải):**
    1.  **Menu Toggle:** Icon Hamburger để đóng/mở Sidebar.
    2.  **Logo/Title:** Chữ trắng, Bold.
    3.  **Language Switcher:** Nút chuyển đổi VI/EN.
    4.  **Login Button (CTA):** * *Style:* Nền Trắng (`#FFF`), Chữ Xanh (`#00C060`).
        * *Shape:* Bo tròn (Pill-shape / `borderRadius: 20px`).
        * *State:* Hover sẽ chuyển sang màu xám rất nhạt (`#F0F0F0`).

### B. Collapsible Sidebar (Drawer)
* **Vị trí:** Bên trái (`anchor="left"`).
* **Hành vi:** `variant="persistent"`. Khi mở sẽ đẩy nội dung bản đồ sang phải. Khi đóng sẽ thu gọn hoàn toàn (`width: 0`).
* **Kích thước:** `width: 350px` - `400px`.
* **Cấu trúc bên trong:**
    * *Top:* Thanh tìm kiếm (`OutlinedInput`, bo tròn, nền trắng).
    * *Nav:* Tabs (Tra cứu / Tìm đường) - Indicator màu xanh.
    * *Body:* Danh sách cuộn dọc (`overflow-y: auto`). Chứa các Route Cards.

### C. Map Area (Main Content)
* **Vị trí:** Chiếm toàn bộ không gian còn lại (`flex-grow: 1`).
* **Xử lý Resize:** Cần gọi `map.invalidateSize()` khi Sidebar đóng/mở để tránh lỗi hiển thị tile.

## 5. UI Components Styling

### Route Card (Thẻ tuyến xe)
* **Component:** `MUI Card`.
* **Visual:** Nền trắng, bo góc `8px`, Shadow nhẹ (`box-shadow: 0 2px 8px rgba(0,0,0,0.08)`).
* **Nội dung:**
    * Icon xe buýt (Avatar tròn, nền xanh nhạt, icon xanh đậm).
    * Tên tuyến (Bold).
    * Lộ trình (Text Regular, cắt dòng nếu quá dài).
    * Giá/Thời gian (Text Secondary, căn phải).

### Map Elements (Leaflet)
* **Tile Layer:** Sử dụng `CartoDB Voyager` hoặc `Mapbox Streets` để có nền bản đồ sáng, sạch, ít chi tiết thừa.
* **Markers:** Custom Marker bằng `L.divIcon` hoặc SVG Icon.
    * *Màu sắc:* Đồng bộ màu xanh Primary.
    * *Shape:* Hình giọt nước hoặc hình tròn có icon xe buýt ở giữa.

## 6. Theme Configuration (MUI Snippet)
Cấu hình nhanh cho `createTheme`:

```javascript
{
  palette: {
    primary: { main: '#00C060', contrastText: '#fff' },
    background: { default: '#F5F7FA', paper: '#fff' },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: '8px', textTransform: 'none', fontWeight: 600 }
      }
    },
    MuiAppBar: {
      styleOverrides: {
        root: { backgroundColor: '#00C060' }
      }
    }
  }
}