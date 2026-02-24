# db/__init__.py
# Make the database instance available at the package level

# Import directly to avoid circular import issues
from db.database import Database

# Create a singleton database instance
# This provides a single connection that can be imported everywhere
db = Database()

# Export the database instance 
__all__ = ['db', 'Database']
