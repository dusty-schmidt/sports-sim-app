export interface PlayerModelData {
    id: string;
    name: string;
    team: string;
    salary: number;
    stats: {
        mean_projection: number;
        floor_25: number;
        ceiling_85: number;
        win_probability: number;
    };
    status: 'ACTIVE' | 'QUESTIONABLE' | 'OUT' | 'LOCKED';
}

export interface GridRow extends PlayerModelData {
    user_override?: {
        manual_projection?: number;
        lock_status?: 'LOCKED' | 'EXCLUDED' | 'NONE';
        exposure_min?: number;
        exposure_max?: number;
        sentiment_boost?: number;
    };
    is_edited: boolean;
    display_projection: number;
}
