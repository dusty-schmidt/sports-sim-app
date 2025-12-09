import type { ColumnDef } from "@tanstack/react-table"
import type { Match } from "@/client"
import { MatchActionsMenu } from "./MatchActionsMenu"

export const columns: ColumnDef<Match>[] = [
    {
        accessorKey: "player1_name",
        header: "Player 1",
    },
    {
        accessorKey: "player2_name",
        header: "Player 2",
    },
    {
        accessorKey: "start_time",
        header: "Start Time",
        cell: ({ row }) => {
            return new Date(row.original.start_time).toLocaleString()
        }
    },
    {
        header: "Odds (P1/P2)",
        cell: ({ row }) => (
            <span>{row.original.p1_odds} / {row.original.p2_odds}</span>
        )
    },
    {
        header: "Sim Win % (P1)",
        cell: ({ row }) => (
            <span className="font-bold">
                {row.original.sim_win_prob_p1 ? (row.original.sim_win_prob_p1 * 100).toFixed(1) + "%" : "-"}
            </span>
        )
    },
    {
        id: "actions",
        header: () => <span className="sr-only">Actions</span>,
        cell: ({ row }) => (
            <div className="flex justify-end">
                <MatchActionsMenu match={row.original} />
            </div>
        ),
    },
]
