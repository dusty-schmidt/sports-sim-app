from fastapi.testclient import TestClient
from app.api.main import api_router
from fastapi import FastAPI
from app.services.data import PLAYERS_DB

# Use a minimal app with the router
app = FastAPI()
app.include_router(api_router)

client = TestClient(app)

def test_simulation_endpoint():
    print("Testing POST /simulation/ad-hoc ...")
    
    # 1. Ensure Players exist in the Mock DB (data.py)
    # The current PLAYERS_DB likely has "Jannik Sinner" and "Carlos Alcaraz" from the fetch script or hardcoded.
    # Let's check what's actually there by importing.
    
    print(f"Available players in DB: {list(PLAYERS_DB.keys())[:5]}...")
    
    p1 = "Jannik Sinner"
    p2 = "Carlos Alcaraz"
    
    if p1 not in PLAYERS_DB or p2 not in PLAYERS_DB:
        print(f"Skipping test: Players {p1}, {p2} not in PLAYERS_DB. Update the test with valid names.")
        # Try to find valid names
        if len(PLAYERS_DB) >= 2:
            p1 = list(PLAYERS_DB.keys())[0]
            p2 = list(PLAYERS_DB.keys())[1]
            print(f"Falling back to: {p1} vs {p2}")
        else:
            print("Not enough players in DB to test.")
            return

    payload = {
        "player1_name": p1,
        "player2_name": p2,
        "surface": "Hard",
        "n_sims": 10,
        "sets_to_win": 2
    }
    
    response = client.post("/simulation/ad-hoc", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("Success! Response:")
        print(f"Winner P1%: {data['p1_win_pct']}")
        print(f"P1 Avg Fantasy Points: {data['p1_avg_fantasy_points']}")
        print(f"Simulations: {data['simulations']}")
        
        assert data["p1_name"] == p1
        assert data["p2_name"] == p2
        assert data["simulations"] == 10
        assert "p1_avg_fantasy_points" in data
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_simulation_endpoint()
