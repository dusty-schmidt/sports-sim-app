import { ExposureRow } from './ExposureRow';

// Mock Data
const EXPOSURE_DATA = [
    { playerName: 'Josh Allen', team: 'BUF', currentExposure: 85.0 },
    { playerName: 'Stefon Diggs', team: 'BUF', currentExposure: 70.0 },
    { playerName: 'Saquon Barkley', team: 'NYG', currentExposure: 60.0 },
    { playerName: 'CeeDee Lamb', team: 'DAL', currentExposure: 40.0 },
    { playerName: 'Jalen Hurts', team: 'PHI', currentExposure: 15.0 },
];

export function ExposureDashboard() {
    return (
        <div className="space-y-4">
            <h2 className="text-lg font-semibold">Exposure Management</h2>
            <div className="bg-white border rounded-md p-4">
                <div className="space-y-2">
                    {EXPOSURE_DATA.map(p => (
                        <ExposureRow
                            key={p.playerName}
                            playerName={p.playerName}
                            team={p.team}
                            currentExposure={p.currentExposure}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
}
