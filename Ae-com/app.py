from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flash messages; set to a secure random key in production

# Database connection function
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='ecomDB',
            user='root',
            password=''
        )
        if conn.is_connected():
            print("Database connected successfully.")
        return conn
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

# Route to check if the database connection works
@app.route('/check_connection', methods=['GET'])
def check_connection():
    conn = get_db_connection()
    if conn:
        conn.close()  # Close connection after checking
        return jsonify({"message": "Connection successful"})
    else:
        return jsonify({"message": "Connection failed"}), 500

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error")
            return redirect(url_for('login'))
        
        try:
            email = request.form.get('email')
            password = request.form.get('password')

            # Validate required fields
            if not email or not password:
                flash("Both email and password are required")
                return redirect(url_for('login'))

            cursor = conn.cursor()

            # Fetch the user data
            query = "SELECT password, role FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            if user:
                # Print the stored password for debugging purposes
                print(f"Stored Password: {user[0]}")  # Debug line
                # Check if the password matches
                if user[0] == password:  # Compare plain text passwords directly
                    role = user[1]
                    if role == 'admin':
                        return redirect(url_for('admin_page'))
                    elif role == 'superadmin':
                        return redirect(url_for('superadmin_page'))
                    elif role == 'user':
                        return redirect(url_for('user_page'))
                    else:
                        flash("Unknown role encountered")
                        return redirect(url_for('login'))
                else:
                    flash("Invalid email or password")
                    return redirect(url_for('login'))
            else:
                flash("Invalid email or password")
                return redirect(url_for('login'))

        except Error as e:
            print(f"Login error: {e}")
            flash("An internal database error occurred")
            return redirect(url_for('login'))
        finally:
            if conn:
                conn.close()  # Ensure connection is closed

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        conn = get_db_connection()
        if conn is None:
            flash("Failed to connect to the database")
            return redirect(url_for('signup'))

        try:
            email = request.form.get('email')
            password = request.form.get('password')
            role = 'user'  # Default role is 'user'

            # Validate required fields
            if not email or not password:
                flash("Email and password are required")
                return redirect(url_for('signup'))

            cursor = conn.cursor()

            # Insert the user into the 'users' table
            query = "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)"
            cursor.execute(query, (email, password, role))  # Store plain text password
            conn.commit()
            flash("User registered successfully!")  # Success message
            return redirect(url_for('signup'))  # Redirect back to the signup page

        except Error as e:
            print(f"Error while inserting user data: {e}")
            flash("Failed to register user")
            return redirect(url_for('signup'))
        finally:
            if conn:
                conn.close()  # Ensure connection is closed

    return render_template('signup.html')

@app.route('/admin_page', methods=['GET'])
def admin_page():
    return render_template('admin_page.html')

@app.route('/superadmin_page', methods=['GET'])
def superadmin_page():
    return render_template('superadmin_page.html')

@app.route('/user_page', methods=['GET'])
def user_page():
    return render_template('user_page.html')



@app.route('/user_data')
def user_data():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    cursor.close()
    connection.close()
    sidebar1 = "sidebar1.html"
    return render_template('user_data.html', users=users, sidebar = sidebar1)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    connection = get_db_connection()
    if not connection:
        flash("Database connection failed.")
        return redirect(url_for('user_data'))

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        flash("User deleted successfully!")
    except Error as e:
        print(f"Error while deleting user: {e}")
        flash("Failed to delete user.")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('user_data'))

@app.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    new_email = request.form.get('email')

    if not new_email:
        flash("Email is required for updating user.")
        return redirect(url_for('user_data'))

    connection = get_db_connection()
    if not connection:
        flash("Database connection failed.")
        return redirect(url_for('user_data'))

    try:
        cursor = connection.cursor()
        # Only update the email, without modifying the role
        cursor.execute("UPDATE users SET email = %s WHERE id = %s", (new_email, user_id))
        connection.commit()
        flash("User email updated successfully!")
    except Error as e:
        print(f"Error while updating user: {e}")
        flash("Failed to update user.")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('user_data'))

if __name__ == '__main__':
    app.run(debug=True)  # Optional: Set debug=True for helpful error messages
