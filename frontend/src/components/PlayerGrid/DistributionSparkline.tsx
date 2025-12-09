import { BarChart, Bar, ResponsiveContainer, Tooltip } from 'recharts';

interface DistributionSparklineProps {
    mean: number;
    floor: number;
    ceiling: number;
}

export function DistributionSparkline({ mean, floor, ceiling }: DistributionSparklineProps) {
    // Creating a simple bell-curve-ish approximation or just 3 bars for now as we don't have full distribution data in the props yet
    const data = [
        { name: 'Floor', value: floor, fill: '#ef4444' }, // red
        { name: 'Mean', value: mean, fill: '#3b82f6' },  // blue
        { name: 'Ceil', value: ceiling, fill: '#22c55e' }, // green
    ];

    return (
        <div className="h-8 w-24">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} barCategoryGap={2}>
                    <Tooltip
                        cursor={{ fill: 'transparent' }}
                        contentStyle={{ fontSize: '10px', padding: '2px 4px' }}
                        itemStyle={{ padding: 0 }}
                    />
                    <Bar dataKey="value" radius={[2, 2, 0, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
