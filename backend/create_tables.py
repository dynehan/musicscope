from app.core.database import Base, engine
from app.models import *  # noqa: F401,F403

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    init_db()