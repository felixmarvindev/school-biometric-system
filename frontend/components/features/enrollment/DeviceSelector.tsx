'use client';

import { useState, useEffect } from 'react';
import { Wifi, WifiOff, CheckCircle2, Loader2 } from 'lucide-react';
import { listDevices, type DeviceResponse, DeviceApiError } from '@/lib/api/devices';
import { Badge } from '@/components/ui/badge';
import { useAuthStore } from '@/lib/store/authStore';

interface DeviceSelectorProps {
  onSelect: (device: DeviceResponse) => void;
  selectedDevice?: DeviceResponse | null;
}

export function DeviceSelector({ onSelect, selectedDevice }: DeviceSelectorProps) {
  const { token } = useAuthStore();
  const [devices, setDevices] = useState<DeviceResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;

    setIsLoading(true);
    setError(null);
    listDevices(token, {
      page_size: 100, // Get all devices
    })
      .then((result) => {
        setDevices(result.items);
      })
      .catch((err) => {
        if (err instanceof DeviceApiError) {
          setError(err.message);
        } else {
          setError('Failed to load devices');
        }
        setDevices([]);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [token]);

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-blue-700 dark:text-blue-400">
        Select Device <span className="text-red-500">*</span>
      </label>
      
      {isLoading && (
        <div className="flex items-center justify-center py-4">
          <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
          <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">Loading devices...</span>
        </div>
      )}
      
      {error && (
        <div className="text-sm text-red-600 dark:text-red-400 py-2">{error}</div>
      )}
      
      {!isLoading && !error && devices.length === 0 && (
        <div className="text-sm text-gray-500 dark:text-gray-400 py-2">
          No devices available. Please register a device first.
        </div>
      )}
      
      {!isLoading && !error && devices.length > 0 && (
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg max-h-60 overflow-y-auto">
          {devices.map((device) => {
            const isOnline = device.status === 'online';
            const isSelected = selectedDevice?.id === device.id;
            
            return (
              <div
                key={device.id}
                onClick={() => isOnline && onSelect(device)}
                className={`p-3 cursor-pointer hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors ${
                  isSelected ? 'bg-blue-100 dark:bg-blue-900/30 border-l-4 border-blue-600' : ''
                } ${!isOnline ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900 dark:text-gray-100">
                      {device.name}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {device.location || device.ip_address}
                      {device.port && `:${device.port}`}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {isOnline ? (
                      <Badge variant="default" className="bg-green-500 hover:bg-green-600">
                        <Wifi className="w-3 h-3 mr-1" />
                        Online
                      </Badge>
                    ) : (
                      <Badge variant="secondary" className="bg-gray-500">
                        <WifiOff className="w-3 h-3 mr-1" />
                        Offline
                      </Badge>
                    )}
                    {isSelected && (
                      <CheckCircle2 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {selectedDevice && (
        <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-gray-900 dark:text-gray-100">
                {selectedDevice.name}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {selectedDevice.location || selectedDevice.ip_address}
                {selectedDevice.port && `:${selectedDevice.port}`}
              </div>
            </div>
            {selectedDevice.status === 'online' ? (
              <Badge variant="default" className="bg-green-500 hover:bg-green-600">
                <Wifi className="w-3 h-3 mr-1" />
                Online
              </Badge>
            ) : (
              <Badge variant="secondary" className="bg-gray-500">
                <WifiOff className="w-3 h-3 mr-1" />
                Offline
              </Badge>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
