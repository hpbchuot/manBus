import React, { useState, useEffect } from 'react';
import { 
  Dialog, DialogTitle, DialogContent, DialogActions, 
  TextField, Button, Alert, LinearProgress 
} from '@mui/material';
import { useAppDispatch, useAppSelector } from '@/store';
import { login, clearError } from '../authSlice';
import { toast } from 'react-toastify';

interface LoginDialogProps {
  open: boolean;
  onClose: () => void;
}

const Login: React.FC<LoginDialogProps> = ({ open, onClose }) => {
  const dispatch = useAppDispatch();
  const { isLoading, error, user } = useAppSelector((state) => state.auth);

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

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
    dispatch(clearError()); // Xóa lỗi cũ nếu có
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      {isLoading && <LinearProgress />}
      <DialogTitle sx={{ textAlign: 'center', fontWeight: 'bold', color: 'primary.main' }}>
        ĐĂNG NHẬP HỆ THỐNG
      </DialogTitle>
      
      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        
        <TextField
          autoFocus
          margin="dense"
          label="Tài khoản"
          type="text"
          fullWidth
          variant="outlined"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <TextField
          margin="dense"
          label="Mật khẩu"
          type="password"
          fullWidth
          variant="outlined"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
        />
      </DialogContent>
      
      <DialogActions sx={{ p: 2, justifyContent: 'center' }}>
        <Button onClick={handleClose} color="inherit">Hủy</Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          disabled={isLoading}
          sx={{ minWidth: 120 }}
        >
          {isLoading ? 'Đang xử lý...' : 'Đăng nhập'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default Login;