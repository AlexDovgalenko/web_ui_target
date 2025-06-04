import atexit
import os
import sys

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from models import create_default_user, create_sample_articles, get_db_connection, init_db

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

def cleanup_users():
    """Remove all users except the default test user on shutdown"""
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE email != 'test.user@example.com'")
    conn.commit()
    conn.close()
    print("Cleaned up users except default test user")

# Register cleanup function to run on app shutdown
atexit.register(cleanup_users)

@app.route('/')
def home():
    search_query = request.args.get('search', '')
    
    conn = get_db_connection()
    
    if search_query:
        articles = conn.execute(
            "SELECT * FROM articles WHERE title LIKE ? ORDER BY id",
            (f'%{search_query}%',)
        ).fetchall()
    else:
        articles = conn.execute("SELECT * FROM articles ORDER BY id").fetchall()
    
    conn.close()
    
    is_logged_in = 'user_id' in session
    
    return render_template('home.html', 
                         articles=articles, 
                         is_logged_in=is_logged_in,
                         search_query=search_query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = f"{user['first_name']} {user['last_name']}"
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        
        # Check if user already exists
        existing_user = conn.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()
        
        if existing_user:
            flash('User with this email already exists!', 'error')
        else:
            # Create new user
            hashed_password = generate_password_hash(password)
            conn.execute(
                "INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
                (first_name, last_name, email, hashed_password)
            )
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            conn.close()
            return redirect(url_for('login'))
        
        conn.close()
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("Starting Flask application...")
    
    # Check CSV file before initializing
    csv_path = 'data/articles.csv'
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found at {csv_path}")
        print("Please create the data directory and add articles.csv file.")
        sys.exit(1)
    
    # Initialize application
    try:
        init_db()
        create_default_user()
        create_sample_articles()  # This will exit if CSV loading fails
        
        print("✓ Application initialized successfully")
        print(f"✓ Articles loaded from {csv_path}")
        print("✓ Default test user available: test.user@example.com / qwerty12345")
        print("Starting server...")
        
        app.run(debug=True)
        
    except Exception as e:
        print(f"FATAL ERROR: Failed to start application: {e}")
        sys.exit(1)
