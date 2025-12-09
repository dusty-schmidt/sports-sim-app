from sqlmodel import Session, select, create_engine
from app.models import User
from app.core.config import settings

# Force SQLite
settings.USE_SQLITE = True
print(f"Connecting to: {settings.SQLALCHEMY_DATABASE_URI}")

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

def check_users():
    try:
        with Session(engine) as session:
            print("Querying users...")
            statement = select(User)
            users = session.exec(statement).all()
            print(f"Found {len(users)} users.")
            for user in users:
                print(f"User: {user.email} (ID: {user.id})")
                
                # Test Pydantic Conversion
                from app.models import UserPublic
                print("Validating UserPublic...")
                up = UserPublic.model_validate(user)
                print(f"Validated: {up}")

            from sqlmodel import func
            print("Querying count...")
            count_statement = select(func.count()).select_from(User)
            count = session.exec(count_statement).one()
            print(f"Count: {count}")

    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_users()
