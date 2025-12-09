import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Activity } from "lucide-react"
import { Suspense } from "react"

import { MatchesService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import { columns } from "@/components/Matches/columns"

function getMatchesQueryOptions() {
    return {
        queryFn: () => MatchesService.readMatches({ skip: 0, limit: 100 }),
        queryKey: ["matches"],
    }
}

export const Route = createFileRoute("/_layout/matches")({
    component: Matches,
})

function MatchesTableContent() {
    const { data: matches } = useSuspenseQuery(getMatchesQueryOptions())

    // Note: MatchesService.readMatches returns Array<Match>, not { data: ... } like items.
    // Check types.gen.ts: MatchesReadMatchesResponse = (Array<Match>);
    // So 'matches' IS the array.

    if (matches.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center text-center py-12">
                <div className="rounded-full bg-muted p-4 mb-4">
                    <Activity className="h-8 w-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-semibold">No matches found</h3>
                <p className="text-muted-foreground">Check back later for upcoming matches.</p>
            </div>
        )
    }

    return <DataTable columns={columns} data={matches} />
}

function MatchesTable() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <MatchesTableContent />
        </Suspense>
    )
}

function Matches() {
    return (
        <div className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Matches</h1>
                    <p className="text-muted-foreground">View upcoming tennis matches and run simulations</p>
                </div>
            </div>
            <MatchesTable />
        </div>
    )
}
