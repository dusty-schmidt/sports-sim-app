import { useState, useEffect } from 'react';
import { useUserOverrides } from '../../store/useUserOverrides';
import clsx from 'clsx'; // Check if clsx is installed, package.json says yes

interface EditableCellProps {
    getValue: () => any;
    row: { original: { id: string } };
    column: { id: string };
    table: any;
}

export function EditableCell({ getValue, row, column }: EditableCellProps) {
    const initialValue = getValue();
    const playerId = row.original.id;
    const { setOverride, getOverride } = useUserOverrides();
    const override = getOverride(playerId);

    // If we have a manual projection in the store, use it. Otherwise use the passed value.
    // Note: For this to work perfectly, the table data needs to reactively update, 
    // but if this cell is purely for the "Projection" column, we might want to prioritize the store value locally.

    const [value, setValue] = useState(initialValue);
    // const [isEditing, setIsEditing] = useState(false); (Unused)

    // Sync with store if it changes externally or on mount
    const storeValue = override?.manual_projection;
    const displayValue = storeValue !== undefined ? storeValue : initialValue;
    const isOverridden = storeValue !== undefined;

    useEffect(() => {
        setValue(displayValue);
    }, [displayValue]);

    const onBlur = () => {
        // setIsEditing(false);
        const numValue = parseFloat(value);
        if (!isNaN(numValue) && numValue !== initialValue) {
            // Assuming this is the 'projection' column
            if (column.id === 'display_projection' || column.id === 'stats_mean_projection') { // Adjust ID as needed
                setOverride(playerId, { manual_projection: numValue });
            }
        } else if (value === '' || value === String(initialValue)) {
            // Reset if cleared or matches original
            setOverride(playerId, { manual_projection: undefined });
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            (e.currentTarget as HTMLInputElement).blur();
        }
    };

    return (
        <input
            value={value}
            onChange={e => setValue(e.target.value)}
            onBlur={onBlur}
            onKeyDown={handleKeyDown}
            className={clsx(
                "w-full bg-transparent p-1 rounded text-right transition-colors",
                isOverridden ? "bg-yellow-100 text-yellow-900 font-medium" : "hover:bg-gray-50",
                "focus:outline-none focus:ring-1 focus:ring-blue-500"
            )}
        />
    );
}
