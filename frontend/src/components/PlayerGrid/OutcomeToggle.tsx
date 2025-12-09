import clsx from 'clsx';

export type ProjectionMode = 'mean' | 'floor' | 'ceiling';

interface OutcomeToggleProps {
    value: ProjectionMode;
    onChange: (value: ProjectionMode) => void;
}

export function OutcomeToggle({ value, onChange }: OutcomeToggleProps) {
    const options: { value: ProjectionMode; label: string }[] = [
        { value: 'floor', label: 'Floor (25th)' },
        { value: 'mean', label: 'Mean' },
        { value: 'ceiling', label: 'Ceil (85th)' },
    ];

    return (
        <div className="flex bg-gray-100 p-1 rounded-lg inline-flex">
            {options.map((option) => (
                <button
                    key={option.value}
                    onClick={() => onChange(option.value)}
                    className={clsx(
                        "px-3 py-1 text-sm font-medium rounded-md transition-all",
                        value === option.value
                            ? "bg-white text-gray-900 shadow-sm"
                            : "text-gray-500 hover:text-gray-900"
                    )}
                >
                    {option.label}
                </button>
            ))}
        </div>
    );
}
