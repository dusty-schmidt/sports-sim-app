import { EllipsisVertical, Play } from "lucide-react"
import { useState } from "react"
import type { Match } from "@/client"
import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { MatchesService } from "@/client"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

interface MatchActionsMenuProps {
    match: Match
}

export const MatchActionsMenu = ({ match }: MatchActionsMenuProps) => {
    const [open, setOpen] = useState(false)
    const queryClient = useQueryClient()

    const mutation = useMutation({
        mutationFn: async () => {
            await MatchesService.triggerSimulation({ matchId: match.id! })
        },
        onSuccess: () => {
            toast.success("Simulation triggered")
            setOpen(false)
            queryClient.invalidateQueries({ queryKey: ["matches"] })
        },
        onError: (err) => {
            toast.error("Failed to trigger simulation")
            console.error(err)
        }
    })

    return (
        <DropdownMenu open={open} onOpenChange={setOpen}>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon">
                    <EllipsisVertical />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => mutation.mutate()}>
                    <Play className="mr-2 size-4" />
                    Run Sim
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}
