import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Alert,
  LinearProgress,
  Box,
  Typography,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import api from '@/services/api';
import { toast } from 'react-toastify';

interface RegisterDialogProps {
  open: boolean;
  onClose: () => void;
  onSwitchToLogin: () => void;
}

interface RegisterForm {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  name: string;
  phone: string;
}

const Register: React.FC<RegisterDialogProps> = ({ open, onClose, onSwitchToLogin }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [form, setForm] = useState<RegisterForm>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    phone: '',
  });

  const handleChange = (field: keyof RegisterForm) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setForm({ ...form, [field]: e.target.value });
    setError(null);
  };

  const validateForm = (): boolean => {
    if (!form.username || !form.email || !form.password || !form.name || !form.phone) {
      setError('Vui lòng điền đầy đủ thông tin');
      return false;
    }

    if (form.password !== form.confirmPassword) {
      setError('Mật khẩu xác nhận không khớp');
      return false;
    }

    if (form.password.length < 8) {
      setError('Mật khẩu phải có ít nhất 8 ký tự');
      return false;
    }

    if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(form.password)) {
      setError('Mật khẩu phải chứa chữ hoa, chữ thường và số');
      return false;
    }

    if (!/^\S+@\S+\.\S+$/.test(form.email)) {
      setError('Email không hợp lệ');
      return false;
    }

    if (!/^\d{10,11}$/.test(form.phone)) {
      setError('Số điện thoại không hợp lệ (10-11 số)');
      return false;
    }

    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setIsLoading(true);
    setError(null);

    try {
      await api.post('/auth/register', {
        username: form.username,
        email: form.email,
        password: form.password,
        confirm_password: form.confirmPassword,
        name: form.name,
        phone: form.phone,
      });

      toast.success('Đăng ký thành công! Vui lòng đăng nhập.');
      onClose();
      onSwitchToLogin();
    } catch (err: any) {
      const message = err.response?.data?.message || 'Đăng ký thất bại';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setForm({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      name: '',
      phone: '',
    });
    setError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      {isLoading && <LinearProgress />}
      
      <DialogTitle sx={{ textAlign: 'center', fontWeight: 'bold', color: 'primary.main' }}>
        ĐĂNG KÝ TÀI KHOẢN
      </DialogTitle>

      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField
            label="Tên đăng nhập"
            type="text"
            fullWidth
            variant="outlined"
            value={form.username}
            onChange={handleChange('username')}
            required
          />

          <TextField
            label="Email"
            type="email"
            fullWidth
            variant="outlined"
            value={form.email}
            onChange={handleChange('email')}
            required
          />

          <TextField
            label="Họ và tên"
            type="text"
            fullWidth
            variant="outlined"
            value={form.name}
            onChange={handleChange('name')}
            required
          />

          <TextField
            label="Số điện thoại"
            type="tel"
            fullWidth
            variant="outlined"
            value={form.phone}
            onChange={handleChange('phone')}
            placeholder="0123456789"
            required
          />

          <TextField
            label="Mật khẩu"
            type={showPassword ? 'text' : 'password'}
            fullWidth
            variant="outlined"
            value={form.password}
            onChange={handleChange('password')}
            required
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowPassword(!showPassword)}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <TextField
            label="Xác nhận mật khẩu"
            type={showConfirmPassword ? 'text' : 'password'}
            fullWidth
            variant="outlined"
            value={form.confirmPassword}
            onChange={handleChange('confirmPassword')}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            required
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    edge="end"
                  >
                    {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <Typography variant="caption" color="text.secondary">
            Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường và số
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 2, flexDirection: 'column', gap: 1 }}>
        <Box sx={{ display: 'flex', gap: 2, width: '100%' }}>
          <Button onClick={handleClose} color="inherit" fullWidth>
            Hủy
          </Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={isLoading}
            fullWidth
          >
            {isLoading ? 'Đang xử lý...' : 'Đăng ký'}
          </Button>
        </Box>

        <Button
          onClick={() => {
            handleClose();
            onSwitchToLogin();
          }}
          sx={{ textTransform: 'none' }}
        >
          Đã có tài khoản? Đăng nhập ngay
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default Register;