import React from 'react';
import { Chip } from '@mui/material';
import type { BusStatus } from '../../types/bus';

interface BusStatusBadgeProps {
  status: BusStatus;
  size?: 'small' | 'medium';
}

const BusStatusBadge: React.FC<BusStatusBadgeProps> = ({ status, size = 'small' }) => {
  const getStatusColor = (status: BusStatus): 'success' | 'default' | 'warning' => {
    switch (status) {
      case 'Active':
        return 'success';
      case 'Inactive':
        return 'default';
      case 'Maintenance':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Chip
      label={status}
      color={getStatusColor(status)}
      size={size}
      sx={{ fontWeight: 500 }}
    />
  );
};

export default BusStatusBadge;
