from database import engine

# Test the database connection
connection = engine.connect()
print("Connected successfully.")
connection.close()