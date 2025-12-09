import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from app.core.db import engine
from app.models import Player, PlayerStats

def main():
    print("Verifying DB Content...")
    try:
        with Session(engine) as session:
            print("Searching for 'Sinner'...")
            players = session.exec(select(Player).where(Player.name.like("%Sinner%"))).all()
            for p in players:
                print(f"ID: {p.id} | Name: '{p.name}' | Elo: {p.elo_overall}")
                stats_direct = session.exec(select(PlayerStats).where(PlayerStats.player_id == p.id)).all()
                print(f"  > Stats Count: {len(stats_direct)}")
                for s in stats_direct:
                     print(f"    Surface: {s.surface} | 1st%: {s.serve_1_in_pct}")
                
                
            # Cleanup Bad Rows
            print("Cleaning up old 'dirty' records...")
            dirty_players = session.exec(select(Player).where(Player.name.like("%[%"))).all()
            for dp in dirty_players:
                print(f"Deleting dirty player: {dp.name}")
                # Explicitly delete stats first to avoid FK issues if cascade isn't set up perfectly
                stats_to_delete = session.exec(select(PlayerStats).where(PlayerStats.player_id == dp.id)).all()
                for s in stats_to_delete:
                    session.delete(s)
                session.delete(dp)
            session.commit()
            
            # Count totals
            p_count = session.exec(select(Player)).all()
            print(f"Total Players: {len(p_count)}")
            
            s_count = session.exec(select(PlayerStats)).all()
            print(f"Total Stats Rows: {len(s_count)}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
