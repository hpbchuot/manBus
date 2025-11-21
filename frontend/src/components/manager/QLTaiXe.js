// import React, { useEffect, useState } from "react";
// import { styled } from "@mui/material/styles";
// import {
//   Table,
//   TableBody,
//   TableCell,
//   TableContainer,
//   TableHead,
//   TableRow,
//   Paper,
//   Box,
//   Button,
//   Typography,
//   Modal,
//   TextField,
//   Autocomplete,
//   tableCellClasses,
// } from "@mui/material";
// import Grid2 from "@mui/material/Grid2"; // Grid2 không gộp vì là module riêng
// import { toast } from "react-toastify";
// import { useDispatch } from "react-redux";
// import { Link, useNavigate } from "react-router-dom";
// import ConfirmDeleteModal from "../common/confirmDeleteModal";
// import * as actions from "../../redux/actions";
// import requestApi from "../../helpers/api";

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
//   top: "50%",
//   left: "50%",
//   transform: "translate(-50%, -50%)",
//   width: 550,
//   bgcolor: "background.paper",
//   border: "2px solid #000",
//   boxShadow: 24,
//   p: 4,
// };
// let drivers = [];
// let manager = {
//   name: "Nguyen H P",
//   username: "phunh12345678",
//   password: "12345679",
//   email: "phu2401200@gmail.com",
//   phone: "0987654321",
//   blx: "123-456-789",
//   bus_id: "123",
// };
// let buses = [];
// export default function QLTaiXe() {
//   const [rows, setRows] = useState([]);
//   const [selectedUser, setSelectedUser] = useState(null);
//   const [isModalOpen, setIsModalOpen] = useState(false);
//   const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
//   const [isSubmitted, setIsSubmitted] = useState(false);
//   const [formErrors, setFormErrors] = useState({});
//   const [isEditMode, setIsEditMode] = useState(false); // Xác định modal đang ở chế độ edit hay thêm mới
//   const [selectedManager, setSelectedManager] = useState(null);
//   const [open, setOpen] = React.useState(false);
//   const navigate = useNavigate();
//   const dispatch = useDispatch();
//   const [newData, setNewData] = React.useState({
//     name: "",
//     username: "",
//     password: "",
//     email: "",
//     phone: "",
//     blx: "",
//     bus_id: "",
//   });
//   const [deleteModalOpen, setDeleteModalOpen] = useState(false);
//   const [selectedItem, setSelectedItem] = useState(null);
//   const columns = [
//     {
//       field: "name",
//       headerName: "Full name",
//       flex: 1,
//       minWidth: 150,
//     },
//     {
//       field: "phone",
//       headerName: "Phone number",
//       flex: 1,
//       minWidth: 150,
//     },
//     {
//       field: "email",
//       headerName: "Email",
//       flex: 0.7,
//       minWidth: 100,
//     },
//     {
//       field: "blx",
//       headerName: "Bằng lái xe",
//       flex: 2,
//       minWidth: 200,
//     },
//     {
//       field: "actions",
//       headerName: "Actions",
//       flex: 1,
//       sortable: false,
//       renderCell: (params) => (
//         <Box>
//           <Button
//             variant="contained"
//             color="primary"
//             size="small"
//             sx={{ mr: 1 }}
//             onClick={() => {
//               setSelectedUser(params.row);
//               setIsModalOpen(true);
//             }}
//           >
//             View
//           </Button>
//           <Button
//             variant="contained"
//             color="error"
//             size="small"
//             onClick={() => {
//               setSelectedUser(params.row);
//               setIsDeleteModalOpen(true);
//             }}
//           >
//             Delete
//           </Button>
//         </Box>
//       ),
//     },
//   ];
//   const handleDeleteClick = (item) => {
//     setSelectedItem(item); // Lưu item cần xóa
//     setDeleteModalOpen(true);
//   };

//   const handleConfirmDelete = () => {
//     console.log("Deleted:", selectedItem);
//     try {
//       dispatch(actions.controlLoading(true));
//       requestApi("/manager/delete-driver", "POST", selectedItem).then((res) => {
//         console.log(res);
//         toast.success(res.data.message, {
//           position: "top-right",
//           autoClose: 3000,
//         });
//         fetchData();
//         dispatch(actions.controlLoading(false));
//       });
//     } catch (error) {
//       dispatch(actions.controlLoading(false));
//       console.log(error);
//       if (typeof error.response !== "undefined") {
//         if (error.response.status !== 201) {
//           toast.error(error.response.data.message, {
//             position: "top-right",
//             autoClose: 3000,
//           });
//         }
//       } else {
//         toast.error("Server is down. Please try again!", {
//           position: "top-right",
//           autoClose: 3000,
//         });
//       }
//     }
//     setDeleteModalOpen(false);
//   };

//   const handleOpen = (man = null) => {
//     setOpen(true);
//     console.log(man);
//     if (man) {
//       // Nếu có manager truyền vào => Chế độ cập nhật
//       console.log("update");
//       setIsEditMode(true);
//       setSelectedManager(man);
//       setNewData(man); // Load dữ liệu manager vào form
//       console.log("true", newData);
//     } else {
//       // Nếu không có manager => Chế độ thêm mới
//       console.log("create");
//       setIsEditMode(false);
//       setSelectedManager(null);
//       setNewData({
//         name: "",
//         username: "",
//         password: "",
//         email: "",
//         phone: "",
//         blx: "",
//         bus_id: "",
//       });
//     }
//     setIsSubmitted(false);
//   };
//   const handleClose = () => setOpen(false);

//   const handleInputChange = (e) => {
//     const { name, value } = e.target;
//     setNewData({ ...newData, [name]: value });
//   };
//   useEffect(() => {
//     if (isSubmitted) {
//       validateForm();
//     }
//   }, [isSubmitted, newData]);
//   //fetch data
//   useEffect(() => {
//     fetchData();
//   }, []);
//   const fetchData = async () => {
//     try {
//       dispatch(actions.controlLoading(true));
//       const response = await requestApi("/manager/get-all-driver", "GET");
//       const res2 = await requestApi("/bus/get-all-bus", "GET");
//       console.log(response.data);
//       console.log(res2);
//       drivers = response.data;
//       buses = res2.data.data;
//       setRows(response.data); // Giả sử API trả về một mảng drivers
//       dispatch(actions.controlLoading(false));
//     } catch (error) {
//       console.error("Error fetching data:", error);
//       dispatch(actions.controlLoading(false));
//       toast.error("Không thể tải dữ liệu", { position: "top-right" });
//     }
//   };
//   const validateForm = () => {
//     let isValid = true;
//     const errors = {};
//     if (newData.email === "" || newData.email === undefined) {
//       errors.email = "Hãy nhập email";
//     } else {
//       let valid = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(
//         newData.email
//       );
//       if (!valid) {
//         errors.email = "Email không hợp lệ";
//       }
//     }
//     const phonePattern = /^[0-9]{10,11}$/;
//     if (!newData.phone) {
//       errors.phone = "Hãy nhập số điện thoại";
//     } else if (!phonePattern.test(newData.phone)) {
//       errors.phone = "Số điện thoại không hợp lệ";
//     }
//     if (!isEditMode && newData.username?.length < 8) {
//       errors.username = "Username tối thiểu 8 kí tự";
//     }
//     if (
//       !isEditMode &&
//       (newData.password === "" || newData.password === undefined)
//     ) {
//       errors.password = "Hãy nhập mật khẩu";
//     }
//     if (!isEditMode && (newData.blx === "" || newData.blx === undefined)) {
//       errors.blx = "Hãy nhập số bằng lái xe";
//     }
//     if (newData.bus_id === "" || newData.bus_id === undefined) {
//       errors.bus = "Chọn xe cho tài xế";
//     }

//     if (Object.keys(errors).length > 0) {
//       setFormErrors(errors);
//       isValid = false;
//     } else {
//       setFormErrors({});
//     }

//     return isValid;
//   };

//   const handleSubmit = () => {
//     console.log("TT Tài xế:", newData);
//     let valid = validateForm();
//     console.log(formErrors, valid);
//     if (valid) {
//       if (isEditMode) {
//         // Xử lý cập nhật
//         console.log("Updating tài xe:", newData);
//         console.log("request update tx");
//         dispatch(actions.controlLoading(true));
//         requestApi("/manager/update-driver", "POST", newData)
//           .then((res) => {
//             console.log(res);
//             toast.success(res.data.message, {
//               position: "top-right",
//               autoClose: 3000,
//             });
//             fetchData();
//             dispatch(actions.controlLoading(false));
//             setIsSubmitted(false);
//             setFormErrors({});
//             handleClose();
//             return;
//           })
//           .catch((err) => {
//             dispatch(actions.controlLoading(false));
//             console.log(err);
//             if (typeof err.response !== "undefined") {
//               if (err.response.status !== 201) {
//                 toast.error(err.response.data.message, {
//                   position: "top-right",
//                   autoClose: 3000,
//                 });
//               }
//             } else {
//               toast.error("Server is down. Please try again!", {
//                 position: "top-right",
//                 autoClose: 3000,
//               });
//             }
//           });
//       } else {
//         //xu ly them moi
//         console.log("request thêm mới tài xế api");
//         dispatch(actions.controlLoading(true));
//         requestApi("/manager/create-driver", "POST", newData)
//           .then((res) => {
//             console.log(res);
//             toast.success(res.data.message, {
//               position: "top-right",
//               autoClose: 3000,
//             });
//             fetchData();
//             dispatch(actions.controlLoading(false));
//             setIsSubmitted(false);
//             setFormErrors({});
//             handleClose();
//             return;
//           })
//           .catch((err) => {
//             dispatch(actions.controlLoading(false));
//             console.log(err);
//             if (typeof err.response !== "undefined") {
//               if (err.response.status !== 201) {
//                 toast.error(err.response.data.message, {
//                   position: "top-right",
//                   autoClose: 3000,
//                 });
//               }
//             } else {
//               toast.error("Server is down. Please try again!", {
//                 position: "top-right",
//                 autoClose: 3000,
//               });
//             }
//           });
//       }
//     }
//     setIsSubmitted(true);
//   };
//   const handleSearch = (event, value) => {
//     if (!value) {
//       setRows(drivers); // Reset khi không nhập gì
//       return;
//     }

//     const searchTerm = value.toLowerCase();
//     const filtered = drivers.filter(
//       (driver) =>
//         driver.username.toLowerCase().includes(searchTerm) ||
//         driver.name.toLowerCase().includes(searchTerm) ||
//         driver.phone.includes(searchTerm)
//     );
//     setRows(filtered);
//   };
//   const handleSelect = (event, value) => {
//     if (value) {
//       const { username, name, phone } = value; // Truy cập các biến riêng lẻ
//       const filtered = drivers.filter(
//         (user) =>
//           user.username === username &&
//           user.name === name &&
//           user.phone === phone
//       );
//       console.log("val", filtered);
//       setRows(filtered);
//     } else {
//       setRows(drivers); // Reset khi không chọn gì
//     }
//   };
//   return (
//     <div className="qldriver">
//       <Typography variant="h4" component="h2">
//         Quản lý tài xế
//       </Typography>
//       <Box sx={{ display: "flex", justifyContent: "space-between", mt: 2 }}>
//         <Button
//           variant="contained"
//           color="success"
//           sx={{ mt: 2, mb: 2 }}
//           onClick={() => handleOpen()}
//         >
//           Đăng kí mới tài xế
//         </Button>
//         <Autocomplete
//           sx={{ width: 500 }}
//           options={drivers}
//           getOptionLabel={(option) =>
//             `${option.username} (${option.name}) - ${option.phone}`
//           }
//           onInputChange={handleSearch}
//           onChange={handleSelect} // Xử lý khi chọn
//           renderInput={(params) => (
//             <TextField {...params} label="Tra cứu tài xế" />
//           )}
//         />
//       </Box>
//       <TableContainer component={Paper}>
//         <Table sx={{ minWidth: 700 }} aria-label="customized table">
//           <TableHead>
//             <TableRow>
//               <StyledTableCell>Full name</StyledTableCell>
//               <StyledTableCell align="left">Mail</StyledTableCell>
//               <StyledTableCell align="left">Phone</StyledTableCell>
//               <StyledTableCell align="left">Bằng lái xe</StyledTableCell>
//               <StyledTableCell align="center">Actions</StyledTableCell>
//             </TableRow>
//           </TableHead>
//           <TableBody>
//             {rows.map((row) => (
//               <StyledTableRow key={row.name}>
//                 <StyledTableCell component="th" scope="row">
//                   {row.name}
//                 </StyledTableCell>
//                 <StyledTableCell align="left">{row.email}</StyledTableCell>
//                 <StyledTableCell align="left">{row.phone}</StyledTableCell>
//                 <StyledTableCell align="left">{row.blx}</StyledTableCell>
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
//                     {/* Danh sách */}
//                     <Button
//                       variant="contained"
//                       color="error"
//                       size="small"
//                       onClick={() => handleDeleteClick(row)}
//                     >
//                       Delete
//                     </Button>

//                     {/* Modal delete */}
//                     <ConfirmDeleteModal
//                       open={deleteModalOpen}
//                       onClose={() => setDeleteModalOpen(false)}
//                       onConfirm={handleConfirmDelete}
//                       message={`Bạn có chắc chắn muốn xóa ${selectedItem?.name}?`}
//                     />
//                   </div>
//                 </StyledTableCell>
//               </StyledTableRow>
//             ))}
//           </TableBody>
//         </Table>
//       </TableContainer>
//       <Modal
//         open={open}
//         onClose={handleClose}
//         aria-labelledby="modal-modal-title"
//         aria-describedby="modal-modal-description"
//       >
//         <Box sx={}>
//           <Typography id="modal-modal-title" variant="h6" component="h2">
//             {isEditMode ? "Cập nhật thông tin tài xế" : "Thêm mới tài xế"}
//           </Typography>
//           <Grid2 container spacing={2} sx={{ mt: 2 }}>
//             <Grid2 item xs={12}>
//               <TextField
//                 fullWidth
//                 label="Full Name"
//                 name="name"
//                 value={newData.name}
//                 disabled={isEditMode}
//                 onChange={handleInputChange}
//               />
//             </Grid2>
//             <Grid2 item xs={12}>
//               <TextField
//                 fullWidth
//                 label="Username"
//                 name="username"
//                 value={newData.username}
//                 disabled={isEditMode}
//                 onChange={handleInputChange}
//               />
//               {formErrors.username && (
//                 <p style={{ color: "red" }}>{formErrors.username}</p>
//               )}
//             </Grid2>
//             {!isEditMode && (
//               <Grid2 item xs={12}>
//                 <TextField
//                   fullWidth
//                   label="Password"
//                   name="password"
//                   value={newData.password}
//                   onChange={handleInputChange}
//                 />
//                 {formErrors.password && (
//                   <p style={{ color: "red" }}>{formErrors.password}</p>
//                 )}
//               </Grid2>
//             )}
//             <Grid2 item xs={12}>
//               <TextField
//                 fullWidth
//                 label="Mail"
//                 name="email"
//                 value={newData.email}
//                 onChange={handleInputChange}
//               />
//               {formErrors.email && (
//                 <p style={{ color: "red" }}>{formErrors.email}</p>
//               )}
//             </Grid2>
//             <Grid2 item xs={12}>
//               <TextField
//                 fullWidth
//                 label="Phone"
//                 name="phone"
//                 value={newData.phone}
//                 onChange={handleInputChange}
//               />
//               {formErrors.phone && (
//                 <p style={{ color: "red" }}>{formErrors.phone}</p>
//               )}
//             </Grid2>
//             <Grid2 item xs={12}>
//               <TextField
//                 fullWidth
//                 label="Bằng lái xe"
//                 name="blx"
//                 value={newData.blx}
//                 disabled={isEditMode}
//                 onChange={handleInputChange}
//               />
//               {formErrors.blx && (
//                 <p style={{ color: "red" }}>{formErrors.blx}</p>
//               )}
//             </Grid2>
//             <Grid2 item xs={12}>
//               <Autocomplete
//                 sx={{ width: 550 }}
//                 options={buses} // Assuming buses is an array of objects containing bus information
//                 getOptionLabel={(option) =>
//                   `${option.name} (${option.plate_number})`
//                 } // Displaying name and code
//                 onChange={(event, value) => {
//                   // Update the newData with the selected bus's ID
//                   handleInputChange({
//                     target: {
//                       name: "bus_id", // The name of the field you want to store the bus ID in
//                       value: value ? value.bus_id : "", // Store the ID, or set it to an empty string if no selection
//                     },
//                   });
//                 }}
//                 renderInput={(params) => (
//                   <TextField {...params} label="Chọn xe" />
//                 )}
//                 value={
//                   buses.find((bus) => bus.bus_id === newData.bus_id) || null
//                 } // To ensure the selected bus is displayed
//               />
//               {formErrors.blx && (
//                 <p style={{ color: "red" }}>{formErrors.blx}</p>
//               )}
//             </Grid2>
//           </Grid2>
//           <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 3 }}>
//             <Button variant="outlined" sx={{ mr: 2 }} onClick={handleClose}>
//               Cancel
//             </Button>
//             <Button variant="contained" color="success" onClick={handleSubmit}>
//               {isEditMode ? "Update" : "Save"}
//             </Button>
//           </Box>
//         </Box>
//       </Modal>
//     </div>
//   );
// }
import React, { useState, useEffect } from "react";
import { DataGrid } from "@mui/x-data-grid";
import {
  Box,
  Button,
  Typography,
  Paper,
  TextField,
  Modal,
  Autocomplete,
  Grid2,
} from "@mui/material";
import {
  useDrivers,
  useCreateDriver,
  useUpdateDriver,
  useDeleteDriver,
  useBusInDriver,
} from "../../hooks/useDriver";
import { useDriverForm } from "../../hooks/useDriverForm";
import ConfirmDeleteModal from "../common/confirmDeleteModal";
import { toast } from "react-toastify";
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
  backgroundColor: "white", // Thêm màu nền
};
const DriverForm = ({ isEditMode, initialData, onSubmit, onClose }) => {
  console.log("init", initialData);
  const {
    formData,
    errors,
    isSubmitted,
    setIsSubmitted,
    validateForm,
    handleChange,
  } = useDriverForm(initialData, isEditMode);
  const handleSubmit = (e) => {
    e.preventDefault();
    setIsSubmitted(true);

    if (validateForm()) {
      onSubmit(formData);
    }
  };
  const { data: buses, isLoading } = useBusInDriver();
  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      <Grid2 container spacing={2}>
        <Grid2 item size={{ xs: 6, md: 12 }}>
          <TextField
            fullWidth
            label="Họ tên"
            name="name"
            value={formData.name}
            onChange={handleChange}
            error={!!errors.name}
            helperText={errors.name}
            disabled={isEditMode}
            sx={{ backgroundColor: "white" }}
          />
        </Grid2>
        <Grid2 item size={{ xs: 6, md: 12 }}>
          <TextField
            fullWidth
            label="Username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            error={!!errors.username}
            helperText={errors.username}
            disabled={isEditMode}
            sx={{ backgroundColor: "white" }}
          />
        </Grid2>

        {!isEditMode && (
          <Grid2 item size={{ xs: 6, md: 12 }}>
            <TextField
              fullWidth
              label="Password"
              name="password"
              type="password"
              onChange={handleChange}
              error={!!errors.password}
              helperText={errors.password}
              sx={{ backgroundColor: "white" }}
            />
          </Grid2>
        )}
        <Grid2 item size={{ xs: 6, md: 12 }}>
          <TextField
            fullWidth
            label="Email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            error={!!errors.email}
            helperText={errors.email}
            sx={{ backgroundColor: "white" }}
          />
        </Grid2>
        <Grid2 item size={{ xs: 6, md: 12 }}>
          <TextField
            fullWidth
            label="Số điện thoại"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            error={!!errors.phone}
            helperText={errors.phone}
          />
        </Grid2>

        <Grid2 item size={{ xs: 6, md: 12 }}>
          <TextField
            fullWidth
            label="Bằng lái xe"
            name="blx"
            value={formData.blx}
            onChange={handleChange}
            error={!!errors.blx}
            helperText={errors.blx}
            disabled={isEditMode}
          />
        </Grid2>

        <Grid2 item size={{ xs: 6, md: 12 }}>
          <Autocomplete
            fullWidth
            options={buses || []}
            getOptionLabel={(option) =>
              `${option.name} (${option.plate_number})`
            }
            value={buses?.find((bus) => bus.bus_id === formData.bus_id) || null}
            onChange={(event, newValue) => {
              handleChange({
                target: {
                  name: "bus_id",
                  value: newValue?.bus_id || "",
                },
              });
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Chọn xe"
                error={!!errors.bus_id}
                helperText={errors.bus_id}
              />
            )}
          />
        </Grid2>

        <Grid2 item size={{ xs: 6, md: 12 }}>
          <Box
            sx={{ display: "flex", justifyContent: "flex-end", gap: 2, mt: 2 }}
          >
            <Button variant="outlined" onClick={onClose}>
              Hủy
            </Button>
            <Button variant="contained" type="submit">
              {isEditMode ? "Cập nhật" : "Thêm mới"}
            </Button>
          </Box>
        </Grid2>
      </Grid2>
    </Box>
  );
};

export default function QLTaiXe() {
  const [paginationModel, setPaginationModel] = useState({
    page: 0,
    pageSize: 10,
  });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedDriver, setSelectedDriver] = useState(null);
  const [isEditMode, setIsEditMode] = useState(false);

  const { data: drivers, isLoading } = useDrivers(
    paginationModel.page,
    paginationModel.pageSize
  );
  const createDriver = useCreateDriver();
  const updateDriver = useUpdateDriver();
  const deleteDriver = useDeleteDriver();
  const initialFormData = {
    name: "",
    username: "",
    password: "",
    email: "",
    phone: "",
    blx: "",
    bus_id: "",
  };
  const {
    formData,
    setFormData,
    errors,
    validate,
    handleChange,
    setIsSubmitted,
  } = useDriverForm(initialFormData, isEditMode);

  const handleOpenModal = (driver = null) => {
    console.log("dddd", driver);
    setIsEditMode(!!driver);
    setSelectedDriver(driver);
    setFormData(driver || initialFormData);
    console.log(formData);
    setIsModalOpen(true);
    setIsSubmitted(false);
  };
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedDriver(null);
    setIsEditMode(false);
    setIsSubmitted(false);
  };
  const handleSubmit = async (formData) => {
    try {
      if (isEditMode) {
        await updateDriver.mutateAsync(formData);
      } else {
        await createDriver.mutateAsync(formData);
      }
      setIsModalOpen(false);
      toast.success(
        isEditMode ? "Cập nhật thành công!" : "Thêm mới thành công!"
      );
    } catch (error) {
      toast.error("Có lỗi xảy ra!");
    }
  };

  const handleDelete = async () => {
    if (selectedDriver) {
      await deleteDriver.mutateAsync(selectedDriver);
      setIsDeleteModalOpen(false);
    }
  };

  const columns = [
    { field: "name", headerName: "Họ tên", flex: 1 },
    { field: "email", headerName: "Email", flex: 1 },
    { field: "phone", headerName: "Số điện thoại", flex: 1 },
    { field: "blx", headerName: "Bằng lái xe", flex: 1 },
    {
      field: "actions",
      headerName: "Thao tác",
      flex: 1,
      sortable: false,
      renderCell: (params) => (
        <Box>
          <Button
            variant="contained"
            size="small"
            sx={{ mr: 1 }}
            onClick={() => handleOpenModal(params.row)}
          >
            Sửa
          </Button>
          <Button
            variant="contained"
            color="error"
            size="small"
            onClick={() => {
              setSelectedDriver(params.row);
              setIsDeleteModalOpen(true);
            }}
          >
            Xóa
          </Button>
        </Box>
      ),
    },
  ];

  return (
    <Box
      sx={{
        padding: 3,
        paddingLeft: { xs: 3, sm: "80px" }, // Thêm padding để tránh đè với ControlBar
        paddingTop: { xs: 3, sm: "80px" },
        height: "100%",
        overflow: "auto",
      }}
    >
      <Typography variant="h4" gutterBottom>
        Quản lý tài xế
      </Typography>

      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={() => handleOpenModal()}
        >
          Thêm tài xế mới
        </Button>
      </Box>

      <Paper sx={{ height: 400, width: "100%" }}>
        <DataGrid
          rows={drivers?.data || []}
          columns={columns}
          pagination
          paginationModel={paginationModel}
          rowCount={drivers?.total}
          onPaginationModelChange={setPaginationModel}
          paginationMode="server"
          pageSizeOptions={[5, 10, 25]}
          getRowId={(row) => row.id || row.username}
          loading={isLoading}
          disableSelectionOnClick
        />
      </Paper>

      {/* Driver Form Modal */}
      <Modal open={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <Box sx={modalStyle}>
          <Typography variant="h6" component="h2">
            {isEditMode ? "Cập nhật tài xế" : "Thêm mới tài xế"}
          </Typography>
          <DriverForm
            isEditMode={isEditMode}
            initialData={selectedDriver || initialFormData}
            onSubmit={handleSubmit}
            onClose={handleCloseModal}
          />
        </Box>
      </Modal>

      {/* Delete Confirmation Modal */}
      <ConfirmDeleteModal
        open={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={handleDelete}
        title="Xác nhận xóa"
        message={`Bạn có chắc chắn muốn xóa tài xế ${selectedDriver?.name}?`}
      />
    </Box>
  );
}
