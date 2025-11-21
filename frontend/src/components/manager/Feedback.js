// import React, { useEffect, useState } from "react";
// import { styled } from "@mui/material/styles";
// import TableCell, { tableCellClasses } from "@mui/material/TableCell";
// import TableHead from "@mui/material/TableHead";
// import {
//   Table,
//   TableBody,
//   TableContainer,
//   TableFooter,
//   TablePagination,
//   TableRow,
//   Paper,
// } from "@mui/material";
// import Box from "@mui/material/Box";
// import Button from "@mui/material/Button";
// import Typography from "@mui/material/Typography";
// import Modal from "@mui/material/Modal";
// import Grid2 from "@mui/material/Grid";
// import TextField from "@mui/material/TextField";
// import Autocomplete, { autocompleteClasses } from "@mui/material/Autocomplete";
// import { toast } from "react-toastify";
// import ConfirmDeleteModal from "../common/confirmDeleteModal";
// import { useDispatch } from "react-redux";
// import { Link, useNavigate } from "react-router-dom";
// import * as actions from "../../redux/actions";
// import requestApi from "../../helpers/api";
// import { useTranslation } from "react-i18next";
// import dayjs from "dayjs";
// import { DemoContainer, DemoItem } from "@mui/x-date-pickers/internals/demo";
// import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
// import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";

// import { DateRangePicker } from "@mui/x-date-pickers-pro/DateRangePicker";
// import { Grid } from "@mui/material";
// const StyledTableCell = styled(TableCell)(({ theme }) => ({
//   [`&.${tableCellClasses.head}`]: {
//     backgroundColor: theme.palette.common.black,
//     color: theme.palette.common.white,
//   },
//   [`&.${tableCellClasses.body}`]: {
//     fontSize: 14,
//   },
// }));

// const StyledTableRow = styled(TableRow)(({ theme }) => ({
//   "&:nth-of-type(odd)": {
//     backgroundColor: theme.palette.action.hover,
//   },
//   "&:last-child td, &:last-child th": {
//     border: 0,
//   },
// }));

// const style = {
//   position: "absolute",
//   top: "40%",
//   left: "50%",
//   transform: "translate(-50%, -50%)",
//   width: 550,
//   bgcolor: "background.paper",
//   border: "2px solid #000",
//   boxShadow: 24,
//   p: 4,
// };
// let users = [];
// export default function Feedback() {
//   const { t } = useTranslation();

//   const [rows, setRows] = useState([]);
//   const [page, setPage] = useState(0);
//   const [rowsPerPage, setRowsPerPage] = useState(5);
//   const [totalCount, setTotalCount] = useState(0);

//   const [formErrors, setFormErrors] = useState({});
//   const [selectedManager, setSelectedManager] = useState(null);
//   const [open, setOpen] = React.useState(false);
//   const navigate = useNavigate();
//   const dispatch = useDispatch();
//   const [openRP, setOpenRP] = useState(false);
//   const [dateRange, setDateRange] = useState([null, null]);
//   const [value, setValue] = React.useState([
//     dayjs("2022-04-17"),
//     dayjs("2024-12-18"),
//   ]);
//   const [newData, setNewData] = React.useState({
//     name: "",
//     username: "",
//     password: "",
//     email: "",
//     phone: "",
//   });
//   const [deleteModalOpen, setDeleteModalOpen] = useState(false);
//   const [selectedItem, setSelectedItem] = useState(null);

//   const handleOpen = (man = null) => {
//     setOpen(true);
//     console.log(man);
//     if (man) {
//       // Nếu có manager truyền vào => Chế độ cập nhật
//       console.log("update");
//       setSelectedManager(man);
//       setNewData(man); // Load dữ liệu manager vào form
//       console.log("true", newData);
//     } else {
//       // Nếu không có manager => Chế độ thêm mới
//       console.log("create");
//       setSelectedManager(null);
//       setNewData({
//         name: "",
//         username: "",
//         password: "",
//         email: "",
//         phone: "",
//       });
//     }
//   };
//   const handleClose = () => setOpen(false);
//   const handleOpenRP = () => {
//     setOpenRP(true);
//   };

//   const handleCloseRP = () => {
//     setOpenRP(false);
//   };
//   const handleInputChange = (e) => {
//     const { name, value } = e.target;
//     setNewData({ ...newData, [name]: value });
//   };
//   //fetch data
//   const fetchData = async (page, rowsPerPage) => {
//     try {
//       dispatch(actions.controlLoading(true)); // Bật loading
//       const response = await requestApi(
//         "/feedback/get-all-feed", // endpoint
//         "GET", // method
//         null, // body là null đối với GET request
//         "json", // response type
//         {
//           // params được truyền ở đây
//           page: page + 1, // Trang hiện tại
//           page_size: rowsPerPage, // Số bản ghi mỗi trang
//         }
//       );
//       console.log(response.data.data); // Kiểm tra dữ liệu từ API
//       setRows(response.data.data); // Lưu dữ liệu vào state
//       setTotalCount(response.data.total_count); // Giả sử API trả về tổng số bản ghi
//       dispatch(actions.controlLoading(false)); // Tắt loading
//     } catch (error) {
//       console.error("Error fetching data:", error);
//       dispatch(actions.controlLoading(false)); // Tắt loading khi lỗi xảy ra
//       toast.error("Không thể tải dữ liệu", { position: "top-right" });
//     }
//   };

//   useEffect(() => {
//     fetchData(page, rowsPerPage);
//   }, [page, rowsPerPage]);

//   const handleSearch = (event, value) => {
//     if (!value) {
//       setRows(users); // Reset khi không nhập gì
//       return;
//     }

//     const searchTerm = value.toLowerCase();
//     const filtered = users.filter(
//       (user) =>
//         user.username.toLowerCase().includes(searchTerm) ||
//         user.name.toLowerCase().includes(searchTerm) ||
//         user.phone.includes(searchTerm)
//     );
//     setRows(filtered);
//   };
//   const handleSelect = (event, value) => {
//     if (value) {
//       const { username, name, phone } = value; // Truy cập các biến riêng lẻ
//       const filtered = users.filter(
//         (user) =>
//           user.username === username &&
//           user.name === name &&
//           user.phone === phone
//       );
//       console.log("val", filtered);
//       setRows(filtered);
//     } else {
//       setRows(users); // Reset khi không chọn gì
//     }
//   };
//   const handleRP = () => {};
//   const handleDateRangeChange = (newValue) => {
//     setDateRange(newValue);
//   };

//   const handleGenerateReport = async () => {
//     const [startDate, endDate] = value; // Lấy giá trị từ state value
//     console.log(startDate, endDate);
//     if (!startDate || !endDate) {
//       toast.error("Vui lòng chọn ngày bắt đầu và ngày kết thúc.", {
//         position: "top-right",
//       });
//       return;
//     }

//     try {
//       dispatch(actions.controlLoading(true));

//       // Chuyển đổi startDate và endDate sang ISO string để gửi API
//       const response = await requestApi("/feedback/generate", "POST", {
//         startDate: startDate.format("YYYY-MM-DD"), // Sử dụng format từ Dayjs
//         endDate: endDate.format("YYYY-MM-DD"),
//       });
//       console.log(response);
//       if (response.status === 200) {
//         const fileURL = window.URL.createObjectURL(
//           new Blob([response.data], { type: "application/pdf" })
//         );

//         // Tạo một link giả để tải file
//         const link = document.createElement("a");
//         link.href = fileURL;
//         link.setAttribute("download", "feedback_report.pdf"); // Tên file khi tải về
//         document.body.appendChild(link);
//         link.click(); // Mô phỏng click để tải file
//         document.body.removeChild(link);
//         toast.success("Báo cáo đã được tạo thành công!", {
//           position: "top-right",
//         });
//       } else {
//         toast.error("Lỗi khi tạo báo cáo.", { position: "top-right" });
//       }
//     } catch (error) {
//       console.error("Error generating report:", error);
//       toast.error("Không thể tạo báo cáo", { position: "top-right" });
//     } finally {
//       dispatch(actions.controlLoading(false)); // Đảm bảo tắt loading trong mọi trường hợp
//       handleCloseRP();
//     }
//   };
//   const handleChangePage = (event, newPage) => {
//     setPage(newPage);
//   };

//   const handleChangeRowsPerPage = (event) => {
//     setRowsPerPage(parseInt(event.target.value, 10));
//     setPage(0);
//   };

//   return (
//     <div className="qluser">
//       <Typography variant="h4" component="h2">
//         {t("feedMan")}
//       </Typography>
//       <Box sx={{ display: "flex", justifyContent: "space-between", mt: 2 }}>
//         <Button
//           variant="contained"
//           color="success"
//           sx={{ mt: 2, mb: 2 }}
//           onClick={() => handleOpenRP()}
//         >
//           Export báo cáo
//         </Button>
//         <Autocomplete
//           sx={{ width: 500, mb: 2 }}
//           options={users}
//           getOptionLabel={(option) =>
//             `${option.username} (${option.name}) - ${option.phone}`
//           }
//           onInputChange={handleSearch}
//           onChange={handleSelect} // Xử lý khi chọn
//           renderInput={(params) => (
//             <TextField {...params} label="Tìm feedback" />
//           )}
//         />
//       </Box>
//       <TableContainer component={Paper}>
//         <Table sx={{ minWidth: 700 }} aria-label="customized table">
//           <TableHead>
//             <TableRow>
//               <StyledTableCell>Người gửi</StyledTableCell>
//               <StyledTableCell align="left">Tài xế</StyledTableCell>
//               <StyledTableCell align="right">Xe</StyledTableCell>
//               <StyledTableCell align="right">Nội dung</StyledTableCell>
//               <StyledTableCell align="right">Trạng thái</StyledTableCell>
//               <StyledTableCell align="center">Actions</StyledTableCell>
//             </TableRow>
//           </TableHead>
//           <TableBody>
//             {rows.map((row) => (
//               <StyledTableRow key={row.feedback_id}>
//                 <StyledTableCell component="th" scope="row">
//                   {row.user_name}
//                 </StyledTableCell>
//                 <StyledTableCell align="left">
//                   {row.driver_name}
//                 </StyledTableCell>
//                 <StyledTableCell align="right">
//                   {row.bus_number}
//                 </StyledTableCell>
//                 <StyledTableCell align="right">
//                   {row.feedback_content}
//                 </StyledTableCell>
//                 <StyledTableCell align="right">
//                   {row.feedback_status}
//                 </StyledTableCell>
//                 <StyledTableCell align="center">
//                   <div>
//                     <Button
//                       variant="contained"
//                       color="primary"
//                       size="small"
//                       sx={{ mr: 1 }}
//                       onClick={() => handleOpen(row)}
//                     >
//                       View
//                     </Button>
//                   </div>
//                 </StyledTableCell>
//               </StyledTableRow>
//             ))}
//           </TableBody>
//           <TableFooter>
//             <TableRow>
//               <TablePagination
//                 rowsPerPageOptions={[5, 10, 25]}
//                 colSpan={3}
//                 count={totalCount}
//                 rowsPerPage={rowsPerPage}
//                 page={page}
//                 onPageChange={handleChangePage}
//                 onRowsPerPageChange={handleChangeRowsPerPage}
//               />
//             </TableRow>
//           </TableFooter>
//         </Table>
//       </TableContainer>
//       <Modal
//         open={open}
//         onClose={handleClose}
//         aria-labelledby="modal-modal-title"
//         aria-describedby="modal-modal-description"
//       >
//         <Box sx={style}>
//           <Typography id="modal-modal-title" variant="h6" component="h2">
//             Chi tiết feedback
//           </Typography>
//           <Grid2 container spacing={2} sx={{ mt: 2 }}>
//             <Grid2 item xs={12}>
//               <TextField
//                 fullWidth
//                 label="Người gửi"
//                 name="name"
//                 value={newData.user_name}
//                 onChange={handleInputChange}
//               />
//             </Grid2>
//             <Grid2 item xs={12}>
//               <TextField
//                 fullWidth
//                 label="Tài xế"
//                 name="username"
//                 value={newData.driver_name}
//                 onChange={handleInputChange}
//               />
//             </Grid2>
//             {/* <Grid2 item xs={12}>
//               <TextField
//                 fullWidth
//                 label="Password"
//                 name="password"
//                 value={newData.password}
//                 onChange={handleInputChange}
//               />
//               {formErrors.password && (
//                 <p style={{ color: "red" }}>{formErrors.password}</p>
//               )}
//             </Grid2> */}
//             <Grid2 item xs={12}>
//               <TextField
//                 fullWidth
//                 label="Xe"
//                 name="email"
//                 value={newData.bus_number}
//                 onChange={handleInputChange}
//               />
//             </Grid2>
//             <Grid2 item xs={12}>
//               <TextField
//                 fullWidth
//                 label="Nội dung"
//                 name="phone"
//                 value={newData.feedback_content}
//                 onChange={handleInputChange}
//               />
//             </Grid2>
//             <Grid2 item xs={12}>
//               <TextField
//                 fullWidth
//                 label="Trạng thái"
//                 name="phone"
//                 value={newData.feedback_status}
//                 onChange={handleInputChange}
//               />
//             </Grid2>
//           </Grid2>
//           <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 3 }}>
//             <Button variant="contained" onClick={handleClose}>
//               Cancel
//             </Button>
//           </Box>
//         </Box>
//       </Modal>
//       {/* Modal for generating report */}
//       <Modal
//         open={openRP}
//         onClose={handleCloseRP}
//         aria-labelledby="report-modal-title"
//         aria-describedby="report-modal-description"
//       >
//         <Box sx={style}>
//           <Typography id="report-modal-title" variant="h6" component="h2">
//             Tạo Báo Cáo
//           </Typography>

//           <LocalizationProvider dateAdapter={AdapterDayjs}>
//             <DemoContainer components={["DateRangePicker", "DateRangePicker"]}>
//               <DemoItem label="Controlled picker" component="DateRangePicker">
//                 <DateRangePicker
//                   value={value}
//                   onChange={(newValue) => setValue(newValue)}
//                 />
//               </DemoItem>
//             </DemoContainer>
//           </LocalizationProvider>
//           <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 3 }}>
//             <Button variant="contained" onClick={handleGenerateReport}>
//               Tạo báo cáo
//             </Button>
//             <Button variant="outlined" onClick={handleCloseRP} sx={{ ml: 2 }}>
//               Hủy
//             </Button>
//           </Box>
//         </Box>
//       </Modal>
//     </div>
//   );
// }
import React, { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import {
  Box,
  Button,
  Typography,
  Modal,
  TextField,
  Paper,
  Grid,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { toast } from "react-toastify";
import dayjs from "dayjs";
import { DemoContainer } from "@mui/x-date-pickers/internals/demo";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DateRangePicker } from "@mui/x-date-pickers-pro/DateRangePicker";
import requestApi from "../../helpers/api";

const modalStyle = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: 600,
  bgcolor: "background.paper",
  boxShadow: 24,
  p: 4,
  borderRadius: 2,
};

export default function Feedback() {
  const { t } = useTranslation();
  const [paginationModel, setPaginationModel] = useState({
    page: 0,
    pageSize: 10,
  });
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [selectedFeedback, setSelectedFeedback] = useState(null);
  const [dateRange, setDateRange] = useState([
    dayjs().subtract(1, "month"),
    dayjs(),
  ]);

  // Fetch feedbacks
  const { data, isLoading } = useQuery({
    queryKey: ["feedbacks", paginationModel.page, paginationModel.pageSize],
    queryFn: async () => {
      const response = await requestApi(
        "/feedback/get-all-feed",
        "GET",
        null,
        "json",
        {
          page: paginationModel.page + 1,
          page_size: paginationModel.pageSize,
        }
      );
      return response.data;
    },
    keepPreviousData: true,
  });

  // Generate report mutation
  const generateReportMutation = useMutation({
    mutationFn: async () => {
      const [startDate, endDate] = dateRange;
      return await requestApi("/feedback/generate", "POST", {
        startDate: startDate.format("YYYY-MM-DD"),
        endDate: endDate.format("YYYY-MM-DD"),
      });
    },
    onSuccess: (response) => {
      const fileURL = window.URL.createObjectURL(
        new Blob([response.data], { type: "application/pdf" })
      );
      const link = document.createElement("a");
      link.href = fileURL;
      link.setAttribute("download", "feedback_report.pdf");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(fileURL);

      toast.success("Báo cáo đã được tạo thành công!");
      setIsReportModalOpen(false);
    },
    onError: (error) => {
      console.error("Error generating report:", error);
      toast.error("Không thể tạo báo cáo");
    },
  });

  const handleGenerateReport = () => {
    const [startDate, endDate] = dateRange;
    if (!startDate || !endDate) {
      toast.error("Vui lòng chọn khoảng thời gian");
      return;
    }
    generateReportMutation.mutate();
  };

  const columns = [
    {
      field: "user_name",
      headerName: "Người gửi",
      flex: 1,
      minWidth: 150,
    },
    {
      field: "driver_name",
      headerName: "Tài xế",
      flex: 1,
      minWidth: 150,
    },
    {
      field: "bus_number",
      headerName: "Xe",
      flex: 0.7,
      minWidth: 100,
    },
    {
      field: "feedback_content",
      headerName: "Nội dung",
      flex: 2,
      minWidth: 200,
    },
    {
      field: "feedback_status",
      headerName: "Trạng thái",
      flex: 1,
      minWidth: 120,
    },
    {
      field: "actions",
      headerName: "Actions",
      flex: 0.8,
      minWidth: 100,
      sortable: false,
      renderCell: (params) => (
        <Button
          variant="contained"
          size="small"
          onClick={() => {
            setSelectedFeedback(params.row);
            setIsDetailModalOpen(true);
          }}
        >
          View
        </Button>
      ),
    },
  ];

  return (
    <Box
      sx={{
        padding: 3,
        paddingLeft: { xs: 3, sm: "80px" },
        height: "100%",
        mt: { xs: 3, sm: "80px" },
      }}
    >
      <Typography variant="h4" gutterBottom>
        {t("feedMan")}
      </Typography>

      {/* Actions */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "flex-end",
          gap: 2,
          mb: 3,
        }}
      >
        <Button
          variant="contained"
          color="success"
          onClick={() => setIsReportModalOpen(true)}
        >
          Export báo cáo
        </Button>
      </Box>

      {/* DataGrid */}
      <Paper sx={{ height: 600, width: "100%" }}>
        <DataGrid
          rows={data?.data || []}
          columns={columns}
          rowCount={data?.total || 0}
          loading={isLoading}
          pageSizeOptions={[5, 10, 25]}
          paginationModel={paginationModel}
          paginationMode="server"
          onPaginationModelChange={setPaginationModel}
          disableRowSelectionOnClick
          getRowId={(row) => row.feedback_id}
          sx={{
            border: 0,
            "& .MuiDataGrid-cell:focus": {
              outline: "none",
            },
          }}
        />
      </Paper>

      {/* Detail Modal */}
      <Modal
        open={isDetailModalOpen}
        onClose={() => setIsDetailModalOpen(false)}
      >
        <Box sx={modalStyle}>
          <Typography variant="h6" gutterBottom>
            Chi tiết feedback
          </Typography>
          <Grid container spacing={2}>
            {selectedFeedback && (
              <>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Người gửi"
                    value={selectedFeedback.user_name || ""}
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Tài xế"
                    value={selectedFeedback.driver_name || ""}
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Xe"
                    value={selectedFeedback.bus_number || ""}
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Nội dung"
                    value={selectedFeedback.feedback_content || ""}
                    multiline
                    rows={4}
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Trạng thái"
                    value={selectedFeedback.feedback_status || ""}
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
              </>
            )}
          </Grid>
          <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 3 }}>
            <Button
              variant="contained"
              onClick={() => setIsDetailModalOpen(false)}
            >
              Đóng
            </Button>
          </Box>
        </Box>
      </Modal>

      {/* Report Modal */}
      <Modal
        open={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
      >
        <Box sx={modalStyle}>
          <Typography variant="h6" gutterBottom>
            Tạo Báo Cáo
          </Typography>
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DemoContainer components={["DateRangePicker"]}>
              <DateRangePicker
                value={dateRange}
                onChange={(newValue) => setDateRange(newValue)}
                sx={{ width: "100%" }}
              />
            </DemoContainer>
          </LocalizationProvider>
          <Box
            sx={{ display: "flex", justifyContent: "flex-end", mt: 3, gap: 2 }}
          >
            <Button
              variant="contained"
              onClick={handleGenerateReport}
              disabled={generateReportMutation.isLoading}
            >
              {generateReportMutation.isLoading ? "Đang tạo..." : "Tạo báo cáo"}
            </Button>
            <Button
              variant="outlined"
              onClick={() => setIsReportModalOpen(false)}
            >
              Hủy
            </Button>
          </Box>
        </Box>
      </Modal>
    </Box>
  );
}
