import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Alert, LinearProgress, Box, InputAdornment, IconButton
} from '@mui/material';

import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '@/store';
import { login, clearError } from '@/store/slices/authSlice';
import { toast } from 'react-toastify';

interface LoginDialogProps {
  open: boolean;
  onClose: () => void;
  onSwitchToRegister?: () => void;
}

const Login: React.FC<LoginDialogProps> = ({ open, onClose, onSwitchToRegister }) => {
  const dispatch = useAppDispatch();
  const { isLoading, error, user } = useAppSelector((state) => state.auth);

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const [showPassword, setShowPassword] = useState(false);

  // Nếu login thành công thì đóng modal
  useEffect(() => {
    if (user) {
      toast.success(`Xin chào, ${user.fullName || user.username}!`);
      onClose();
    }
  }, [user, onClose]);

  const handleSubmit = () => {
    if (!username || !password) return;
    dispatch(login({ username, password }));
  };

  const handleClose = () => {
    dispatch(clearError());
    setUsername('');
    setPassword('');
    onClose();
  };

  const handleSwitchToRegister = () => {
    handleClose();
    onSwitchToRegister?.();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      {isLoading && <LinearProgress />}

      <DialogTitle sx={{ textAlign: 'center', fontWeight: 'bold', color: 'primary.main' }}>
        ĐĂNG NHẬP HỆ THỐNG
      </DialogTitle>

      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField
            autoFocus
            label="Tên đăng nhập hoặc Email"
            type="text"
            fullWidth
            variant="outlined"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isLoading}
          />

          <TextField
            label="Mật khẩu"
            type={showPassword ? 'text' : 'password'}
            fullWidth
            variant="outlined"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            disabled={isLoading}
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
            {isLoading ? 'Đang xử lý...' : 'Đăng nhập'}
          </Button>
        </Box>

        {onSwitchToRegister && (
          <Button
            onClick={handleSwitchToRegister}
            sx={{ textTransform: 'none' }}
          >
            Chưa có tài khoản? Đăng ký ngay
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default Login;