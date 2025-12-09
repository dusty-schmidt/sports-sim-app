import { useState } from 'react';

export function VarianceSlider() {
    const [value, setValue] = useState(50);

    return (
        <div className="space-y-2 bg-white p-4 border rounded-md">
            <div className="flex justify-between">
                <label className="text-sm font-medium text-gray-700">Uniqueness Threshold</label>
                <span className="text-sm text-blue-600 font-bold">{value}%</span>
            </div>
            <input
                type="range"
                min="0"
                max="100"
                value={value}
                onChange={(e) => setValue(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            <p className="text-xs text-gray-500">
                Higher values force more unique players across lineups.
            </p>
        </div>
    );
}
