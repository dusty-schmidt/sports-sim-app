import { Lock, Unlock, Ban, Zap } from 'lucide-react';
// import { UserOverride } from '../../store/useUserOverrides'; (Unused)
import { useUserOverrides } from '../../store/useUserOverrides';
// Button import removed
// Wait, I don't have shadcn components verified. I'll use standard Tailwind buttons for now to be safe.

interface ActionCellProps {
    playerId: string;
}

export function ActionCell({ playerId }: ActionCellProps) {
    const { setOverride, getOverride } = useUserOverrides();
    const override = getOverride(playerId);
    const status = override?.lock_status || 'NONE';

    const handleLock = () => setOverride(playerId, { lock_status: 'LOCKED' });
    const handleExclude = () => setOverride(playerId, { lock_status: 'EXCLUDED' });
    const handleUnlock = () => setOverride(playerId, { lock_status: 'NONE' });

    // Toggle sentiment boost (example logic)
    const isBoosted = (override?.sentiment_boost || 1) > 1;
    const toggleBoost = () => {
        setOverride(playerId, { sentiment_boost: isBoosted ? 1 : 1.1 });
    };

    return (
        <div className="flex items-center gap-1">
            {status === 'LOCKED' ? (
                <button onClick={handleUnlock} className="p-1 text-green-600 hover:bg-green-50 rounded" title="Unlock">
                    <Lock size={16} />
                </button>
            ) : (
                <button onClick={handleLock} className="p-1 text-gray-400 hover:text-green-600 hover:bg-gray-100 rounded" title="Lock">
                    <Unlock size={16} />
                </button>
            )}

            {status === 'EXCLUDED' ? (
                <button onClick={handleUnlock} className="p-1 text-red-600 hover:bg-red-50 rounded" title="Include">
                    <Ban size={16} />
                </button>
            ) : (
                <button onClick={handleExclude} className="p-1 text-gray-400 hover:text-red-600 hover:bg-gray-100 rounded" title="Exclude">
                    <Ban size={16} />
                </button>
            )}

            <button
                onClick={toggleBoost}
                className={`p-1 rounded ${isBoosted ? 'text-yellow-500 bg-yellow-50' : 'text-gray-400 hover:text-yellow-500 hover:bg-gray-100'}`}
                title="Boost"
            >
                <Zap size={16} fill={isBoosted ? "currentColor" : "none"} />
            </button>
        </div>
    );
}
