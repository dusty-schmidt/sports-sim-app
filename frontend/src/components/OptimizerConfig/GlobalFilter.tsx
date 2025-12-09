
// If not available, I'll use standard HTML input

export function GlobalFilter() {
    return (
        <div className="space-y-4 p-4 border-r h-full bg-white w-64">
            <h3 className="font-semibold text-gray-900">Global Settings</h3>

            <div className="space-y-2">
                <label className="text-sm font-medium">Game Time</label>
                <div className="space-y-1">
                    {/* Mock Data */}
                    {['1:00 PM', '4:05 PM', '4:25 PM', '8:20 PM'].map(time => (
                        <label key={time} className="flex items-center space-x-2 text-sm text-gray-600">
                            <input type="checkbox" className="rounded border-gray-300" defaultChecked />
                            <span>{time}</span>
                        </label>
                    ))}
                </div>
            </div>

            <div className="space-y-2">
                <label className="text-sm font-medium">Teams</label>
                <div className="h-40 overflow-y-auto border rounded p-2 space-y-1">
                    {/* Mock Data */}
                    {['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN'].map(team => (
                        <label key={team} className="flex items-center space-x-2 text-sm text-gray-600">
                            <input type="checkbox" className="rounded border-gray-300" defaultChecked />
                            <span>{team}</span>
                        </label>
                    ))}
                </div>
            </div>

            <div className="space-y-2">
                <label className="text-sm font-medium">Status</label>
                <div className="space-y-1">
                    {['Active', 'Questionable', 'Out', 'PPD'].map(status => (
                        <label key={status} className="flex items-center space-x-2 text-sm text-gray-600">
                            <input type="checkbox" className="rounded border-gray-300" defaultChecked={status === 'Active' || status === 'Questionable'} />
                            <span>{status}</span>
                        </label>
                    ))}
                </div>
            </div>

        </div>
    );
}
