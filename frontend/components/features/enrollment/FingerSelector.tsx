'use client';

import React, { useState, useEffect } from 'react';
import { Check } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { motion } from 'framer-motion';

type FingerKey =
  | 'left-thumb'
  | 'left-index'
  | 'left-middle'
  | 'left-ring'
  | 'left-pinky'
  | 'right-thumb'
  | 'right-index'
  | 'right-middle'
  | 'right-ring'
  | 'right-pinky';

interface FingerData {
  id: FingerKey;
  name: string;
  path: string;
  checkPosition: { x: number; y: number };
  fingerId: number; // Map to 0-9 for ZKTeco
}

const leftHandFingers: FingerData[] = [
  {
    id: 'left-thumb',
    name: 'Left Thumb',
    path: 'M 85 180 Q 60 160 50 130 Q 45 110 55 95 Q 65 80 80 85 Q 95 90 100 110 Q 105 130 95 155 Q 90 170 85 180',
    checkPosition: { x: 65, y: 105 },
    fingerId: 5,
  },
  {
    id: 'left-index',
    name: 'Left Index',
    path: 'M 110 170 L 115 80 Q 115 50 130 45 Q 145 40 150 55 Q 155 70 150 85 L 140 170',
    checkPosition: { x: 130, y: 65 },
    fingerId: 6,
  },
  {
    id: 'left-middle',
    name: 'Left Middle',
    path: 'M 145 170 L 155 55 Q 160 25 175 20 Q 190 15 195 35 Q 200 55 195 75 L 180 170',
    checkPosition: { x: 175, y: 45 },
    fingerId: 7,
  },
  {
    id: 'left-ring',
    name: 'Left Ring',
    path: 'M 185 170 L 200 70 Q 205 45 220 40 Q 235 35 240 55 Q 245 75 240 95 L 220 170',
    checkPosition: { x: 220, y: 60 },
    fingerId: 8,
  },
  {
    id: 'left-pinky',
    name: 'Left Pinky',
    path: 'M 225 170 L 245 100 Q 250 75 265 75 Q 280 75 282 95 Q 284 115 275 130 L 255 170',
    checkPosition: { x: 262, y: 95 },
    fingerId: 9,
  },
];

const rightHandFingers: FingerData[] = [
  {
    id: 'right-pinky',
    name: 'Right Pinky',
    path: 'M 45 170 L 25 130 Q 16 115 18 95 Q 20 75 35 75 Q 50 75 55 100 L 75 170',
    checkPosition: { x: 38, y: 95 },
    fingerId: 4,
  },
  {
    id: 'right-ring',
    name: 'Right Ring',
    path: 'M 80 170 L 60 95 Q 55 75 60 55 Q 65 35 80 40 Q 95 45 100 70 L 115 170',
    checkPosition: { x: 80, y: 60 },
    fingerId: 3,
  },
  {
    id: 'right-middle',
    name: 'Right Middle',
    path: 'M 120 170 L 105 75 Q 100 55 105 35 Q 110 15 125 20 Q 140 25 145 55 L 155 170',
    checkPosition: { x: 125, y: 45 },
    fingerId: 2,
  },
  {
    id: 'right-index',
    name: 'Right Index',
    path: 'M 160 170 L 150 85 Q 145 70 150 55 Q 155 40 170 45 Q 185 50 185 80 L 190 170',
    checkPosition: { x: 170, y: 65 },
    fingerId: 1,
  },
  {
    id: 'right-thumb',
    name: 'Right Thumb',
    path: 'M 215 180 Q 210 170 205 155 Q 195 130 200 110 Q 205 90 220 85 Q 235 80 245 95 Q 255 110 250 130 Q 240 160 215 180',
    checkPosition: { x: 235, y: 105 },
    fingerId: 0,
  },
];

interface HandProps {
  fingers: FingerData[];
  selectedFingerId: number | null;
  onFingerClick: (fingerId: number, fingerKey: FingerKey) => void;
  palmPath: string;
  handLabel: string;
}

function Hand({ fingers, selectedFingerId, onFingerClick, palmPath, handLabel }: HandProps) {
  return (
    <div className="flex flex-col items-center">
      <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{handLabel}</div>
      <svg viewBox="0 0 300 350" className="w-full max-w-[280px] h-auto drop-shadow-md">
        {/* Palm */}
        <path d={palmPath} fill="#e5e7eb" className="transition-colors duration-200 dark:fill-gray-700" />
        
        {/* Fingers */}
        <TooltipProvider delayDuration={100}>
          {fingers.map((finger) => {
            const isSelected = selectedFingerId === finger.fingerId;
            return (
              <Tooltip key={finger.id}>
                <TooltipTrigger asChild>
                  <g 
                    onClick={() => onFingerClick(finger.fingerId, finger.id)} 
                    className="cursor-pointer"
                  >
                    <motion.path
                      d={finger.path}
                      fill={isSelected ? '#3b82f6' : '#e5e7eb'}
                      stroke={isSelected ? '#2563eb' : 'transparent'}
                      strokeWidth={isSelected ? 3 : 0}
                      className="transition-all duration-200 hover:fill-[#d1d5db] dark:hover:fill-gray-600"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    />
                    {isSelected && (
                      <motion.g
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transform={`translate(${finger.checkPosition.x - 12}, ${finger.checkPosition.y - 12})`}
                      >
                        <circle cx="12" cy="12" r="12" fill="#3b82f6" />
                        <foreignObject x="4" y="4" width="16" height="16">
                          <Check className="text-white w-4 h-4" />
                        </foreignObject>
                      </motion.g>
                    )}
                  </g>
                </TooltipTrigger>
                <TooltipContent side="top">
                  <p>{finger.name}</p>
                </TooltipContent>
              </Tooltip>
            );
          })}
        </TooltipProvider>
      </svg>
    </div>
  );
}

interface FingerSelectorProps {
  onSelect: (fingerId: number) => void;
  selectedFinger?: number | null;
}

export function FingerSelector({ onSelect, selectedFinger = null }: FingerSelectorProps) {
  const [selectedFingerId, setSelectedFingerId] = useState<number | null>(selectedFinger);

  const handleFingerClick = (fingerId: number, fingerKey: FingerKey) => {
    const newSelection = selectedFingerId === fingerId ? null : fingerId;
    setSelectedFingerId(newSelection);
    onSelect(newSelection !== null ? newSelection : 1); // Default to 1 (Right Index) if deselected
  };

  // Sync with prop changes
  useEffect(() => {
    if (selectedFinger !== undefined && selectedFinger !== null) {
      setSelectedFingerId(selectedFinger);
    }
  }, [selectedFinger]);

  const selectedFingerData = [...leftHandFingers, ...rightHandFingers].find(
    f => f.fingerId === selectedFingerId
  );

  const leftPalmPath =
    'M 95 170 Q 80 200 80 240 Q 80 290 100 320 Q 120 350 160 350 Q 200 350 220 320 Q 240 290 240 240 Q 240 200 225 170 L 95 170';

  const rightPalmPath =
    'M 75 170 Q 60 200 60 240 Q 60 290 80 320 Q 100 350 140 350 Q 180 350 200 320 Q 220 290 220 240 Q 220 200 205 170 L 75 170';

  return (
    <div className="space-y-6">
      <div>
        <label className="text-sm font-medium text-blue-700 dark:text-blue-400">
          Select Finger <span className="text-red-500">*</span>
        </label>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Click on a finger in the hand illustrations below to select it for enrollment. Right Index is recommended.
        </p>
      </div>

      {/* Selected Finger Display */}
      {selectedFingerData && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-lg"
        >
          <div className="flex items-center gap-4">
            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold shadow-lg">
              {selectedFingerId}
            </div>
            <div className="flex-1">
              <div className="font-semibold text-gray-900 dark:text-gray-100">
                {selectedFingerData.name}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Finger ID: {selectedFingerId}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Hand Illustrations */}
      <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16 p-6 bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-gray-200 dark:border-gray-700">
        <Hand
          fingers={leftHandFingers}
          selectedFingerId={selectedFingerId}
          onFingerClick={handleFingerClick}
          palmPath={leftPalmPath}
          handLabel="Left Hand"
        />
        <Hand
          fingers={rightHandFingers}
          selectedFingerId={selectedFingerId}
          onFingerClick={handleFingerClick}
          palmPath={rightPalmPath}
          handLabel="Right Hand"
        />
      </div>

      {!selectedFingerData && (
        <div className="text-center text-sm text-gray-500 dark:text-gray-400 py-4">
          Click on a finger above to select it
        </div>
      )}
    </div>
  );
}
