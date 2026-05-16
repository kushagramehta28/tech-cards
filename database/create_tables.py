from database import engine
from models import Base

# Create all tables in the database
Base.metadata.create_all(engine)

print("Tables created successfully.")