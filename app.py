import atexit
import os
import sys

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from models import create_default_user, create_sample_articles, get_db_connection, init_db

app = Flask(import_name=__name__)
app.secret_key = "your-secret-key-change-this-in-production"

def cleanup_users():
    """Remove all users except the default test user on shutdown"""
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE email != 'test.user@example.com'")
    conn.commit()
    conn.close()
    print("Cleaned up users except default test user")

# Register cleanup function to run on app shutdown
atexit.register(cleanup_users)

@app.route("/")
def home():
    search_query = request.args.get("search", "")
    view_mode = request.args.get("view", "full")

    conn = get_db_connection()

    if search_query:
        articles = conn.execute(
            "SELECT * FROM articles WHERE title LIKE ? ORDER BY id", (f"%{search_query}%",)
        ).fetchall()

        # Add toast for search results
        if articles:
            flash(f'Found {len(articles)} article(s) matching "{search_query}"', "info")
        else:
            flash(f'No articles found for "{search_query}"', "warning")
    else:
        articles = conn.execute("SELECT * FROM articles ORDER BY id").fetchall()

    conn.close()

    is_logged_in = "user_id" in session

    return render_template(
        "home.html", articles=articles, is_logged_in=is_logged_in, search_query=search_query, view_mode=view_mode
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = f"{user['first_name']} {user['last_name']}"
            flash(f"Welcome back, {user['first_name']}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password. Please try again.", "error")

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]

        # Basic validation
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("signup.html")

        conn = get_db_connection()

        # Check if user already exists
        existing_user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()

        if existing_user:
            flash("An account with this email already exists!", "error")
        else:
            # Create new user
            hashed_password = generate_password_hash(password)
            conn.execute(
                "INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
                (first_name, last_name, email, hashed_password),
            )
            conn.commit()
            flash(f"Account created successfully for {first_name}! Please log in.", "success")
            conn.close()
            return redirect(url_for("login"))

        conn.close()

    return render_template("signup.html")

@app.route("/logout")
def logout():
    user_name = session.get("user_name", "User")
    session.clear()
    flash(f"Goodbye, {user_name}! You have been logged out.", "info")
    return redirect(url_for("login"))


# Test route for different toast types (you can remove this in production)
@app.route("/test-toasts")
def test_toasts():
    if "user_id" not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    flash("This is a success message!", "success")
    flash("This is an info message!", "info")
    flash("This is a warning message!", "warning")
    flash("This is an error message!", "error")
    return redirect(url_for("home"))

if __name__ == "__main__":
    print("Starting Flask application...")

    # Check CSV file before initializing
    csv_path = "data/articles.csv"
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found at {csv_path}")
        print("Please create the data directory and add articles.csv file.")
        sys.exit(1)

    # Initialize application
    try:
        init_db()
        create_default_user()
        create_sample_articles()

        print("✓ Application initialized successfully")
        print(f"✓ Articles loaded from {csv_path}")
        print("✓ Default test user available: test.user@example.com / qwerty12345")
        print("✓ Toast notifications enabled")
        print("Starting server...")

        app.run(debug=True)

    except Exception as e:
        print(f"FATAL ERROR: Failed to start application: {e}")
        sys.exit(1)
