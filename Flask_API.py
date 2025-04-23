import logging
import os
import socket
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from log import log_info, log_warning, log_error
from database import get_database 
import re
from scrap import scrape_images,scrape_videos
from flask_mail import Mail,Message

# ✅ Connect to MongoDB
db = get_database()
if db is None:
    log_error("❌ Failed to connect to MongoDB! Flask API will not start.")
    exit()  # ✅ Stop Flask if MongoDB is not available

# Collection for users
users_collection = db["users"]

# ✅ Initialize Flask App
app = Flask(__name__)
app.secret_key = "super_secret_key"
app.config["SESSION_TYPE"] = "filesystem"  # Ensure session storage
Session(app)

# ✅ Home Route
@app.route("/", methods=["GET"])
def home():
    user = session.get("user")
    return render_template("index.html", user=user)

# ✅ Signup Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Registers a new user"""
    if request.method == "POST":
        name=request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        age=request.form.get("age")
        email=request.form.get("email")
        mobile=request.form.get("mobile")
        
        # ✅ Validate Name (Only alphabets, max 30 chars)
        if not re.fullmatch(r"^[A-Za-z ]{1,30}$", name):
            flash("❌ Name must contain only letters and be at most 30 characters!", "danger")
            return redirect(url_for("signup"))
        
         # ✅ Validate Age (Only numbers, max 3 digits)
        if not re.fullmatch(r"^\d{1,3}$", age):
            flash("❌ Age must be a number with a maximum of 3 digits!", "danger")
            return redirect(url_for("signup"))
        
        # ✅ Validate Email (Standard email pattern)
        if not re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            flash("❌ Invalid email format!", "danger")
            return redirect(url_for("signup"))
        
        # ✅ Validate Mobile Number (Only numbers, 10 digits, starting with 6-9)
        if not re.fullmatch(r"^[6789]\d{9}$", mobile):
            flash("❌ Mobile number must be 10 digits and start with 6, 7, 8, or 9!", "danger")
            return redirect(url_for("signup"))
        
        # ✅ Validate Username (Alphanumeric, no special chars)
        if not re.fullmatch(r"^[A-Za-z0-9]+$", username):
            flash("❌ Username must be alphanumeric with no special characters!", "danger")
            return redirect(url_for("signup"))

        # checks user is avaiable or not

        if users_collection.find_one({"username": username}):
            flash("⚠️ OOPS! Username already taken...", "danger")
            log_error(f"❌ User '{username}' already exists!")
            return redirect(url_for("signup"))
        
        # hashed password before storing
        
        hashed_password = generate_password_hash(password)
        
        # store user data in the db
        users_collection.insert_one({"username": username, 
                                     "password": hashed_password,
                                     "email":email,
                                     "name":name,
                                     "mobile":mobile, 
                                     "age":age
                                     }) 
        # send confirmation email
        send_email(email,"Welcome to the image scrapper!",f"Hello {name},\n\nYour account has been successfully created!\n\nHappy Scrapping")

        flash("🎉 Signup Successful! Please log in.", "success")
        log_info(f"✅ New user '{username}' signed up successfully.")
        return redirect(url_for("login"))

    return render_template("signup.html")

# ✅ Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    """Logs in an existing user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password") 

        if not username or not password:
            flash("❌ Please enter both username and password!", "danger")
            log_warning("⚠️ Missing login credentials")
            return redirect(url_for("login"))

        user = users_collection.find_one({"username": username})

        if user and check_password_hash(user["password"], password):
            session["user"] = username
            flash("✅ Login Successful!", "success")
            log_info(f"✅ User '{username}' logged in successfully.")
            return redirect(url_for("home"))

        flash("❌ Invalid username or password!", "danger")
        log_warning(f"⚠️ Failed login attempt for '{username}'")
        return redirect(url_for("login"))

    return render_template("login.html")

# route for scrapping 
@app.route("/scrape", methods=["GET", "POST"]) 
def scrape():
    """Scraping page - Only accessible if logged in"""
    if "user" not in session:
        flash("⚠️ You must be logged in to scrape.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        user_email = users_collection.find_one({"username": session["user"]})["email"]  # Fetch user's email
        choice = request.form.get("choice")
        category = request.form.get("category") 

        if not choice or not category:
            flash("❌ Please select a valid scraping option!", "danger")
            return redirect(url_for("scrape"))

        print(f"📧 Sending email to {user_email} after scraping '{category}'")

        if choice == "images":
            results = scrape_images(category)
            send_email(user_email, "Scraping Completed!", f"Your image scraping for '{category}' is complete!")
            return render_template("results.html", results=results, type="image")

        elif choice == "videos":
            results = scrape_videos(category)
            send_email(user_email, "Scraping Completed!", f"Your video scraping for '{category}' is complete!")
            return render_template("results.html", results=results, type="video")

        flash("⚠️ Invalid choice. Please try again.", "danger")
        return redirect(url_for("scrape"))

    return render_template("scrape.html")  # ✅ Only show scrape page for GET requests


# email configuration
app.config["MAIL_SERVER"]="smtp.gmail.com" #use gmail,outlook, or any smtp provider
app.config["MAIL_PORT"]=587
app.config["MAIL_USE_TLS"]=True
app.config["MAIL_USERNAME"]="ankitnayak7895@gmail.com" #Replace with your email
app.config["MAIL_PASSWORD"]="veyq pvza ntcm eqse" #use app password for security
app.config["MAIL_DEFAULT_SENDER"]="ankitnayak7895@gmail.com"

mail=Mail(app)

# function to send email
def send_email(to_email,subject,body):
    try:
        msg=Message(subject,recipients=[to_email])
        msg.body=body
        mail.send(msg)
        print(f'Mail sent to:- {to_email}')
    except Exception as e:
        print(f'failed to sent email to:-{to_email} to {e}')




# ✅ Logout Route
@app.route("/logout")
def logout():
    """Logs out the user"""  
    session.pop("user", None)
    flash("✅ Logged out successfully.", "info")
    return redirect(url_for("login"))

# ✅ Start Flask Server
if __name__ == "__main__":
    port = 5000
    host_ip = socket.gethostbyname(socket.gethostname())
    log_message = f"\nFlask API is running!\nLocal: http://127.0.0.1:{port}/\nPublic: http://{host_ip}:{port}/\n"
    log_info(log_message)
    print(log_message)
    app.run(debug=True, host="0.0.0.0", port=port)
