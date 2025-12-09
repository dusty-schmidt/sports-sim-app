import { useState } from 'react';

interface ExposureRowProps {
    playerName: string;
    team: string;
    currentExposure: number; // 0-100
    initMin?: number;
    initMax?: number;
}

export function ExposureRow({ playerName, team, currentExposure, initMin = 0, initMax = 100 }: ExposureRowProps) {
    const [min, setMin] = useState(initMin);
    const [max, setMax] = useState(initMax);

    // Example validation styling
    const isInvalid = max < min;

    return (
        <div className="flex items-center gap-4 py-2 border-b hover:bg-gray-50">
            <div className="w-32 font-medium truncate" title={playerName}>{playerName} <span className="text-xs text-gray-400">{team}</span></div>

            <div className="flex-1 flex flex-col justify-center h-full">
                <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                    <div
                        className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
                        style={{ width: `${currentExposure}%` }}
                    ></div>
                </div>
                <div className="text-xs text-right text-gray-500 mt-1">{currentExposure.toFixed(1)}%</div>
            </div>

            <div className="flex items-center gap-2">
                <input
                    type="number"
                    value={min}
                    onChange={e => setMin(Number(e.target.value))}
                    className="w-16 p-1 border rounded text-center text-sm"
                    placeholder="Min"
                    min={0}
                    max={100}
                />
                <span className="text-gray-400">-</span>
                <input
                    type="number"
                    value={max}
                    onChange={e => setMax(Number(e.target.value))}
                    className={`w-16 p-1 border rounded text-center text-sm ${isInvalid ? 'border-red-500 bg-red-50' : ''}`}
                    placeholder="Max"
                    min={0}
                    max={100}
                />
                <span className="text-xs text-gray-400">%</span>
            </div>
        </div>
    );
}
