import React from 'react';
import BusMarker from './BusMarker';
import type { Bus } from '@/types/bus';

interface BusLayerProps {
  buses: Bus[];
  selectedBusId?: number | null;
  trackedBusId?: number | null;
  onBusClick?: (bus: Bus) => void;
  visible?: boolean;
}

/**
 * BusLayer Component
 *
 * Renders all bus markers on the map.
 * Uses React Query for data fetching (called from parent component).
 * Supports bus selection and tracking states.
 *
 * @example
 * const { data: buses = [] } = useActiveBuses();
 * <BusLayer buses={buses} onBusClick={handleBusClick} />
 */
const BusLayer: React.FC<BusLayerProps> = ({
  buses,
  selectedBusId = null,
  trackedBusId = null,
  onBusClick,
  visible = true,
}) => {
  // Don't render if layer is not visible
  if (!visible) {
    return null;
  }

  // Filter buses that have location data
  const busesWithLocation = buses.filter(
    (bus) => bus.currentLocation && bus.currentLocation.latitude && bus.currentLocation.longitude
  );

  return (
    <>
      {busesWithLocation.map((bus) => (
        <BusMarker
          key={bus.busId}
          bus={bus}
          isSelected={bus.busId === selectedBusId}
          isTracked={bus.busId === trackedBusId}
          onClick={onBusClick}
        />
      ))}
    </>
  );
};

export default BusLayer;
