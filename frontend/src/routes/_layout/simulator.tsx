import { createFileRoute } from '@tanstack/react-router';
import { PlayerGrid } from '../../components/PlayerGrid/PlayerGrid';
import { GlobalFilter } from '../../components/OptimizerConfig/GlobalFilter';
import { VarianceSlider } from '../../components/OptimizerConfig/VarianceSlider';
import { ExposureDashboard } from '../../components/ExposureDashboard/ExposureDashboard';
import { LineupCard } from '../../components/LineupViewer/LineupCard';
// Assuming shadcn tabs exist, if not I will build a simple tab switcher
// I saw "components/ui" earlier, let's assume standard structure or use simple state for now to reduce risk
import { useState } from 'react';
import clsx from 'clsx';

export const Route = createFileRoute('/_layout/simulator')({
    component: SimulatorPage,
})

function SimulatorPage() {
    const [activeTab, setActiveTab] = useState<'pool' | 'exposure'>('pool');

    return (
        <div className="flex h-full min-h-screen bg-gray-50">
            {/* Configuration Sidebar */}
            <aside className="w-80 bg-white border-r flex flex-col hidden md:flex">
                <div className="p-4 border-b">
                    <h2 className="text-xl font-bold text-gray-800">Optimizer</h2>
                </div>
                <div className="p-4 border-b">
                    <VarianceSlider />
                </div>
                <div className="flex-1 overflow-y-auto">
                    <GlobalFilter />
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col overflow-hidden">
                {/* Top Bar / Tabs */}
                <header className="bg-white border-b px-6 py-3 flex items-center justify-between">
                    <div className="flex space-x-4">
                        <button
                            onClick={() => setActiveTab('pool')}
                            className={clsx(
                                "px-4 py-2 text-sm font-medium rounded-md transition-colors",
                                activeTab === 'pool' ? "bg-blue-50 text-blue-700" : "text-gray-600 hover:bg-gray-100"
                            )}
                        >
                            Player Pool
                        </button>
                        <button
                            onClick={() => setActiveTab('exposure')}
                            className={clsx(
                                "px-4 py-2 text-sm font-medium rounded-md transition-colors",
                                activeTab === 'exposure' ? "bg-blue-50 text-blue-700" : "text-gray-600 hover:bg-gray-100"
                            )}
                        >
                            Exposures
                        </button>
                    </div>

                    <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500">Last update: 10:42 AM</span>
                        <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700 transition">
                            Build Lineups
                        </button>
                    </div>
                </header>

                {/* Viewport */}
                <div className="flex-1 overflow-y-auto p-6">
                    {activeTab === 'pool' ? (
                        <PlayerGrid />
                    ) : (
                        <ExposureDashboard />
                    )}
                </div>
            </main>
        </div>
    );
}
