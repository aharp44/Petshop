import os
import datetime
import mysql.connector
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure MySQL database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",           # TROCAR POR SUA SENHA DO MYSQL
    database="petplus"
)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # selects the current user cash
    cash = db.cursor()
    cash.execute("SELECT cash FROM users WHERE id = %s", (session["user_id"],))
    cash = float(cash.fetchone()[0])
    totalCash = cash

    # selects all the stocks owned by that user
    stocks = db.cursor()
    stocks.execute("SELECT * FROM shares WHERE userId = %s", (session["user_id"],))
    stocks = stocks.fetchall()

    # updates the current price of that stock and calculates the total amount of cash owned
    for stock in stocks:
        symbol = stock["symbol"]
        stock_info = lookup(symbol)
        current_price = float(stock_info["price"])
        stock.update({"price": current_price})
        totalCash += float(current_price * stock["quantity"])

    return render_template("index.html", stocks=stocks, cash=cash, totalCash=totalCash)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # Checks if all the infos were inserted correctly
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        elif not request.form.get("shares"):
            return apology("must provide shares", 400)
        else:
            try:
                # Checks if the value of shares inserted is a positive int number bigger than one
                shares = request.form.get("shares")
                shares = int(shares)
                if shares < 0:
                    return apology("shares must be a positive number", 400)
            except ValueError:
                return apology("shares must be an integer")
        found = lookup(request.form.get("symbol"))
        if not found:
            return apology("symbol not found", 400)

        # Calculates the users new cash amount and formats the time
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        symbol = request.form.get("symbol")
        stock = lookup(symbol)
        priceStock = stock["price"]
        priceStock = float(priceStock)
        userCash = db.cursor()
        userCash.execute("SELECT cash FROM users WHERE id = %s", (session["user_id"],))
        userCash = userCash.fetchone()[0]
        newUserCash = userCash - (priceStock * shares)

        # Checks if the user has enough cash to buy the stocks
        if newUserCash < 0:
            return apology("not enough cash", 400)
        else:
            # Updates the users current cash and insert the transaction to the table transactions
            db.cursor().execute("UPDATE users SET cash = %s WHERE id = %s", (newUserCash, session["user_id"]))
            db.cursor().execute("INSERT INTO transactions (symbol, quantity, price, userId, time) VALUES (%s, %s, %s, %s, %s)", (symbol, shares, priceStock, session["user_id"], time))

            # Checks if the user already owns a share of that stock or not
            sharesOwned = db.cursor()
            sharesOwned.execute("SELECT quantity FROM shares WHERE symbol = %s AND userId = %s", (symbol, session["user_id"]))
            sharesOwned = sharesOwned.fetchone()
            if not sharesOwned:
                # Insert a new row on the table shares
                db.cursor().execute("INSERT INTO shares (symbol, quantity, price, userId) VALUES (%s, %s, %s, %s)", (symbol, shares, priceStock, session["user_id"]))
            else:
                # Updates the current number of shares of that row
                sharesOwned = int(sharesOwned[0])
                db.cursor().execute("UPDATE shares SET quantity = %s WHERE symbol = %s AND userId = %s", (sharesOwned + shares, symbol, session["user_id"]))

        return redirect("/")
    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = db.cursor()
    history.execute("SELECT * FROM transactions WHERE userId = %s", (session["user_id"],))
    history = history.fetchall()
    if not history:
        return apology("TODO")
    return render_template("history.html", history=history)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("must provide username", 403)
        elif not password:
            return apology("must provide password", 403)

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user is None or not check_password_hash(user["hash"], password):
            return apology("invalid username and/or password", 403)

        session["user_id"] = user["id"]
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    btnClicked = False
    if request.method == "POST":
        # Checks if all infos were inserted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        btnClicked = True

        # Checks if the symbol provided exists
        found = lookup(request.form.get("symbol"))
        if not found:
            return apology("symbol not found", 400)

        return render_template("quote.html", btnClicked=btnClicked, found=found)

    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate input
        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not confirmation:
            return apology("must confirm password", 400)
        elif password != confirmation:
            return apology("passwords do not match", 400)

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone() is not None:
            return apology("username already taken", 400)

        # Hash password and insert new user
        hash_pw = generate_password_hash(password, method='scrypt', salt_length=16)
        cursor.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", (username, hash_pw))
        
        # Commit the transaction to save the changes
        db.commit()

        # Log the user in immediately after registration
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()["id"]
        session["user_id"] = user_id

        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # Checks if all infos were inserted correctly
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        elif not request.form.get("shares"):
            return apology("must provide shares", 400)
        else:
            try:
                # Checks if the value of shares inserted is a positive int number bigger than one
                shares = request.form.get("shares")
                shares = int(shares)
                if shares < 0:
                    return apology("shares must be a positive number", 403)
            except ValueError:
                return apology("shares must be an integer")

        # Checks if the symbol provided exists or not
        found = lookup(request.form.get("symbol"))
        if not found:
            return apology("symbol not found", 400)

        # Calculates the users new cash amount and formats the time
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        symbol = request.form.get("symbol")
        stock = lookup(symbol)
        priceStock = stock["price"]
        priceStock = float(priceStock)
        userCash = db.cursor()
        userCash.execute("SELECT cash FROM users WHERE id = %s", (session["user_id"],))
        userCash = userCash.fetchone()[0]
        newUserCash = userCash + (priceStock * shares)

        # Checks if user has enough shares of that symbol to be sold
        sharesOwned = db.cursor()
        sharesOwned.execute("SELECT quantity FROM shares WHERE userId = %s AND symbol = %s", (session["user_id"], symbol))
        if not sharesOwned.fetchall():
            return apology("doesnt have any shares to sell", 400)
        else:
            sharesOwned = int(sharesOwned.fetchone()[0])
            if shares > sharesOwned:
                return apology("not enough shares to sell", 400)
            else:
                # Updates users number of shares and cash and insert the transaction to the table transactions
                sharesOwned = sharesOwned - shares
                db.cursor().execute("UPDATE shares SET quantity = %s WHERE userId = %s AND symbol = %s", (sharesOwned, session["user_id"], symbol))
                shares = shares * -1
                db.cursor().execute("UPDATE users SET cash = %s WHERE id = %s", (newUserCash, session["user_id"]))
                db.cursor().execute("INSERT INTO transactions (symbol, quantity, price, userId, time) VALUES (%s, %s, %s, %s, %s)", (symbol, shares, priceStock, session["user_id"], time))

        return redirect("/")
    else:
        # Returns a list with the symbols of the shares owned by that user
        symbols = db.cursor()
        symbols.execute("SELECT symbol FROM shares WHERE userId = %s", (session["user_id"],))
        return render_template("sell.html", symbols=symbols.fetchall())