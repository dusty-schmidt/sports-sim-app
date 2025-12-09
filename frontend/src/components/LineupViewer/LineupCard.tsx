import clsx from 'clsx';
// Assuming basic Lucide icons are used elsewhere
import { TrendingUp, Copy } from 'lucide-react';

interface LineupPlayer {
    id: string;
    name: string;
    position: string;
    salary: number;
    projection: number;
}

interface LineupCardProps {
    id: string;
    players: LineupPlayer[];
    totalSalary: number;
    totalProj: number;
    roi?: number;
}

export function LineupCard({ id, players, totalSalary, totalProj, roi }: LineupCardProps) {
    return (
        <div className="bg-white border rounded-lg shadow-sm hover:shadow-md transition-shadow p-4 w-full md:w-80 flex-shrink-0">
            <div className="flex justify-between items-center mb-3 pb-2 border-b">
                <div className="flex flex-col">
                    <span className="text-xs text-gray-500 font-mono">#{id.slice(0, 6)}</span>
                    <div className="flex items-center gap-1 text-green-600 font-bold">
                        <TrendingUp size={16} />
                        <span>{roi ? `${roi}% ROI` : 'N/A'}</span>
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-sm font-semibold">{totalProj.toFixed(1)} Pts</div>
                    <div className="text-xs text-gray-500">${totalSalary.toLocaleString()}</div>
                </div>
            </div>

            <div className="space-y-1">
                {players.map((p, idx) => (
                    <div key={`${p.id}-${idx}`} className="flex justify-between text-sm py-0.5">
                        <div className="flex gap-2">
                            <span className="font-mono text-gray-400 w-6 text-xs">{p.position}</span>
                            <span className="text-gray-900 truncate w-32">{p.name}</span>
                        </div>
                        <div className="text-gray-600 text-xs">{p.projection.toFixed(1)}</div>
                    </div>
                ))}
            </div>

            <div className="mt-4 pt-2 border-t flex justify-between items-center text-xs text-blue-600 cursor-pointer hover:underline">
                <span className="flex items-center gap-1">
                    <Copy size={12} /> Copy CSV
                </span>
                <span>Edit Lineup &rarr;</span>
            </div>
        </div>
    );
}
