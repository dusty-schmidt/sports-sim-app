import { create } from 'zustand';

export interface UserOverride {
    manual_projection?: number;
    lock_status?: 'LOCKED' | 'EXCLUDED' | 'NONE';
    exposure_min?: number;
    exposure_max?: number;
    sentiment_boost?: number;
}

interface UserOverridesState {
    overrides: Record<string, UserOverride>;
    setOverride: (playerId: string, override: Partial<UserOverride>) => void;
    getOverride: (playerId: string) => UserOverride | undefined;
    clearOverrides: () => void;
}

export const useUserOverrides = create<UserOverridesState>((set, get) => ({
    overrides: {},
    setOverride: (playerId, override) =>
        set((state) => {
            const current = state.overrides[playerId] || {};
            const updated = { ...current, ...override };

            // Clean up empty overrides if needed, or keeping them is fine for now
            return {
                overrides: {
                    ...state.overrides,
                    [playerId]: updated,
                },
            };
        }),
    getOverride: (playerId) => get().overrides[playerId],
    clearOverrides: () => set({ overrides: {} }),
}));
