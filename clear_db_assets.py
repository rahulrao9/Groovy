import os
import shutil
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database path from environment variable
DB_PATH = os.getenv("DB_PATH", "hot100.db")

def clear_directory(directory):
    """Delete all files inside a given directory without removing the directory itself."""
    if os.path.exists(directory):
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    # Skip the default image
                    if file_path == "assets/default.jpg":
                        continue
                    os.unlink(file_path)  # Remove file or symbolic link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove directory and its contents
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

def clear_database():
    """Delete all records from the SQLite database but keep the table structure."""
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM hot100")  # Clear all records
            conn.commit()
            print("Database cleared successfully.")
        except sqlite3.Error as e:
            print(f"Error clearing database: {e}")
        finally:
            conn.close()

def clear_assets():
    """Clear all files inside assets/meta, assets/imgs, and assets/music, and reset the database."""
    directories = ["assets/meta", "assets/imgs", "assets/music"]
    
    for directory in directories:
        clear_directory(directory)
        print(f"Cleared: {directory}")
    
    clear_database()  # Clear the database

if __name__ == "__main__":
    clear_assets()
