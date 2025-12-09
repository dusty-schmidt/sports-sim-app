
# Hardcoded player stats for simulation and mock data

PLAYERS_DB = {
    "Carlos Alcaraz": {
        "name": "Carlos Alcaraz",
        "stats": {
            "hard": {
                "serve_1_in": 0.64,
                "serve_1_won": 0.74,
                "serve_2_won": 0.56,
                "ace_rate": 0.058,
                "df_rate": 0.031,
                "return_won": 0.32
            },
           "clay": {
                "serve_1_in": 0.66,
                "serve_1_won": 0.76,
                "serve_2_won": 0.59,
                "ace_rate": 0.045,
                "df_rate": 0.028,
                "return_won": 0.38
            },
            "grass": {
                "serve_1_in": 0.68,
                "serve_1_won": 0.78,
                "serve_2_won": 0.55,
                "ace_rate": 0.075,
                "df_rate": 0.035,
                "return_won": 0.30
            }
        }
    },
    "Jannik Sinner": {
        "name": "Jannik Sinner",
        "stats": {
            "hard": {
                "serve_1_in": 0.62,
                "serve_1_won": 0.79,
                "serve_2_won": 0.58,
                "ace_rate": 0.082,
                "df_rate": 0.022,
                "return_won": 0.31
            },
            "clay": { "serve_1_in": 0.60, "serve_1_won": 0.74, "serve_2_won": 0.55, "ace_rate": 0.06, "df_rate": 0.03, "return_won": 0.30 },
            "grass": { "serve_1_in": 0.64, "serve_1_won": 0.82, "serve_2_won": 0.60, "ace_rate": 0.10, "df_rate": 0.02, "return_won": 0.28 }
        }
    },
    "Novak Djokovic": {
        "name": "Novak Djokovic",
        "stats": {
             "hard": { "serve_1_in": 0.65, "serve_1_won": 0.77, "serve_2_won": 0.57, "ace_rate": 0.07, "df_rate": 0.025, "return_won": 0.32 },
             "clay": { "serve_1_in": 0.68, "serve_1_won": 0.74, "serve_2_won": 0.54, "ace_rate": 0.04, "df_rate": 0.02, "return_won": 0.34 },
             "grass": { "serve_1_in": 0.66, "serve_1_won": 0.80, "serve_2_won": 0.60, "ace_rate": 0.09, "df_rate": 0.02, "return_won": 0.30 }
        }
    },
    "Daniil Medvedev": {
        "name": "Daniil Medvedev",
        "stats": {
             "hard": { "serve_1_in": 0.64, "serve_1_won": 0.76, "serve_2_won": 0.52, "ace_rate": 0.09, "df_rate": 0.045, "return_won": 0.30 },
             "clay": { "serve_1_in": 0.60, "serve_1_won": 0.70, "serve_2_won": 0.48, "ace_rate": 0.06, "df_rate": 0.05, "return_won": 0.32 },
             "grass": { "serve_1_in": 0.63, "serve_1_won": 0.75, "serve_2_won": 0.50, "ace_rate": 0.11, "df_rate": 0.04, "return_won": 0.28 }
        }
    }
}
