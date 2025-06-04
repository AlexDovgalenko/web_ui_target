import csv
import os
import sqlite3
import sys

from werkzeug.security import generate_password_hash

DATABASE = 'test_app.db'
ARTICLES_CSV_PATH = 'data/articles.csv'
DEFAULT_USER_F_NAME = 'Test'
DEFAULT_USER_L_NAME = 'User'
DEFAULT_USER_EMAIL = 'test.user@example.com'
DEFAULT_USER_PASSWORD = 'qwerty12345'

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(database=DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initialize the database with required tables"""
    conn = get_db_connection()
    
    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Create articles table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def create_default_user() -> None:
    """Create the default test user"""
    conn = get_db_connection()
    
    # Check if default user exists
    existing_user = conn.execute(
        "SELECT id FROM users WHERE email = ?", (DEFAULT_USER_EMAIL,)
    ).fetchone()
    
    if not existing_user:
        hashed_password = generate_password_hash(password=DEFAULT_USER_PASSWORD)
        conn.execute(
            "INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
            (DEFAULT_USER_F_NAME, DEFAULT_USER_L_NAME, DEFAULT_USER_EMAIL, hashed_password)
        )
        conn.commit()
        print("Default test user created successfully.")
    
    conn.close()

def load_articles_from_csv() -> list[tuple[str, str]]:
    """Load articles from CSV file - raises exception if file not found or invalid"""
    articles = []
    
    if not os.path.exists(path=ARTICLES_CSV_PATH):
        raise FileNotFoundError(f"Articles CSV file not found at: {ARTICLES_CSV_PATH}")
    
    try:
        with open(file=ARTICLES_CSV_PATH, mode='r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Validate CSV headers
            if not reader.fieldnames or 'title' not in reader.fieldnames or 'content' not in reader.fieldnames:
                raise ValueError("CSV file must have 'title' and 'content' columns")

            for row_number, row in enumerate(iterable=reader, start=2):  # Omit header
                title = row['title'].strip()
                content = row['content'].strip()
                
                # Validate row data
                if not title or not content:
                    print(f"Warning: Skipping row {row_number} - missing title or content")
                    continue
                
                articles.append((title, content))
        
        if not articles:
            raise ValueError("No valid articles found in CSV file")
            
        print(f"Successfully loaded {len(articles)} articles from CSV file.")
        return articles
        
    except csv.Error as e:
        raise ValueError(f"Error reading CSV file: {e}")
    except UnicodeDecodeError as e:
        raise ValueError(f"Error decoding CSV file: {e}")

def create_sample_articles() -> None:
    """Load programming articles from CSV file into database"""
    conn = get_db_connection()
    
    try:
        # Check if articles already exist
        existing_articles = conn.execute("SELECT COUNT(*) as count FROM articles").fetchone()
        
        if existing_articles['count'] == 0:
            print("No articles found in database. Loading from CSV file...")
            
            # Load articles from CSV - will raise exception if fails
            articles = load_articles_from_csv()
            
            # Insert articles into database
            for title, content in articles:
                conn.execute(
                    "INSERT INTO articles (title, content) VALUES (?, ?)",
                    (title, content)
                )
            
            conn.commit()
            print(f"Successfully inserted {len(articles)} articles into database.")
        else:
            print(f"Found {existing_articles['count']} existing articles in database.")
    
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}")
        print("Application cannot start without articles. Please ensure the CSV file exists and is properly formatted.")
        sys.exit(1)
    except sqlite3.Error as e:
        print(f"Database error while creating articles: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error creating articles: {e}")
        sys.exit(1)
    finally:
        conn.close()
