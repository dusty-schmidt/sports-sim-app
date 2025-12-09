import { useState, useMemo } from 'react';
import {
    useReactTable,
    getCoreRowModel,
    getSortedRowModel,
    getFilteredRowModel,
    flexRender,
    ColumnDef,
    SortingState,
} from '@tanstack/react-table';
import { GridRow, PlayerModelData } from '../../types/player';
import { ActionCell } from './ActionCell';
import { EditableCell } from './EditableCell';
import { DistributionSparkline } from './DistributionSparkline';
import { OutcomeToggle, ProjectionMode } from './OutcomeToggle';
import { useUserOverrides } from '../../store/useUserOverrides';
// import { useVirtualizer } from '@tanstack/react-virtual'; // If needed for performance later

// Mock data generator (temporary)
const MOCK_PLAYERS: PlayerModelData[] = Array.from({ length: 50 }, (_, i) => ({
    id: `p-${i}`,
    name: `Player ${i + 1}`,
    team: ['NYG', 'DAL', 'PHI', 'WAS'][i % 4],
    salary: 3000 + (i * 100),
    stats: {
        mean_projection: 10 + Math.random() * 15,
        floor_25: 5 + Math.random() * 5,
        ceiling_85: 20 + Math.random() * 20,
        win_probability: 0.5,
    },
    status: 'ACTIVE',
}));

export function PlayerGrid() {
    const [projectionMode, setProjectionMode] = useState<ProjectionMode>('mean');
    const [sorting, setSorting] = useState<SortingState>([]);
    const { overrides } = useUserOverrides();

    // Merge raw data with overrides
    const data = useMemo<GridRow[]>(() => {
        return MOCK_PLAYERS.map(player => {
            const override = overrides[player.id];
            let displayProj = player.stats.mean_projection;

            if (override?.manual_projection !== undefined) {
                displayProj = override.manual_projection;
            } else {
                switch (projectionMode) {
                    case 'floor': displayProj = player.stats.floor_25; break;
                    case 'ceiling': displayProj = player.stats.ceiling_85; break;
                    default: displayProj = player.stats.mean_projection;
                }
            }

            return {
                ...player,
                user_override: override,
                is_edited: !!override?.manual_projection,
                display_projection: displayProj,
            };
        });
    }, [overrides, projectionMode]);

    const columns = useMemo<ColumnDef<GridRow>[]>(() => [
        {
            accessorKey: 'name',
            header: 'Player',
            cell: info => <div className="font-medium">{info.getValue() as string}</div>,
        },
        {
            accessorKey: 'team',
            header: 'Team',
        },
        {
            accessorKey: 'salary',
            header: 'Salary',
            cell: info => `$${(info.getValue() as number).toLocaleString()}`,
        },
        {
            accessorKey: 'display_projection',
            header: 'Proj',
            cell: props => <EditableCell {...props} />,
        },
        {
            id: 'actions',
            header: 'Actions',
            cell: props => <ActionCell playerId={props.row.original.id} />,
        },
        {
            id: 'distribution',
            header: 'Range',
            cell: props => (
                <DistributionSparkline
                    mean={props.row.original.stats.mean_projection}
                    floor={props.row.original.stats.floor_25}
                    ceiling={props.row.original.stats.ceiling_85}
                />
            ),
        },
    ], []);

    const table = useReactTable({
        data,
        columns,
        state: {
            sorting,
        },
        onSortingChange: setSorting,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
    });

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h2 className="text-lg font-semibold">Player Pool</h2>
                <OutcomeToggle value={projectionMode} onChange={setProjectionMode} />
            </div>

            <div className="border rounded-md overflow-hidden">
                <table className="w-full text-sm text-left">
                    <thead className="bg-gray-50 text-gray-700 font-medium">
                        {table.getHeaderGroups().map(headerGroup => (
                            <tr key={headerGroup.id}>
                                {headerGroup.headers.map(header => (
                                    <th key={header.id} className="px-4 py-2 border-b">
                                        {header.isPlaceholder
                                            ? null
                                            : flexRender(header.column.columnDef.header, header.getContext())}
                                    </th>
                                ))}
                            </tr>
                        ))}
                    </thead>
                    <tbody>
                        {table.getRowModel().rows.map(row => (
                            <tr key={row.id} className="hover:bg-gray-50 border-b last:border-0 bg-white">
                                {row.getVisibleCells().map(cell => (
                                    <td key={cell.id} className="px-4 py-2">
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
