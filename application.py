import os
import re

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

def validate(password):
    if len(password) < 8:
        return apology("Password should be at least 8 characters long")
    # This will search for numbers 0-9 inside the password
    elif not re.search("[0-9]", password):
        return apology("Password should contain at least one number")
    elif not re.search("[A-Z]", password):
        return apology("Password should contain at least one capital letter")
    elif not re.search("[!#$%&'()*+,-./:;<=>?@[\]^_`{|}~]", password):
        return apology("Password should contain at least one special character")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Grouping stocks by name
    rows = db.execute("SELECT symbol, sum(SHARES) as totalShares FROM transactions WHERE user_id = :user_id GROUP BY symbol HAVING SUM(shares) > 0;", user_id=session["user_id"])
    myStocks = []
    # Initializing the gains to zero
    stockGains = 0
    for row in rows:
        stock = lookup(row["symbol"])
        # Creating a dictionary for stocks bought
        myStocks.append({
            "symbol": stock["symbol"],
            "name": stock["name"],
            "shares": row["totalShares"],
            "price": usd(stock["price"]),
            "total": usd(row["totalShares"] * stock["price"])
        })
        # Updating the total of cash according to the total of money made/lost in shares
        stockGains += row["totalShares"] * stock["price"]
    rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
    cash = rows[0]["cash"]
    # Adding the money made/lost in stocks to the user's money
    stockGains += cash

    return render_template("index.html", myStocks=myStocks, cash=usd(cash), stockGains=usd(stockGains))


@app.route("/wallet", methods=["GET", "POST"])
@login_required
def wallet():
    """Add additional cash to the account"""
    if request.method == "POST":
        # Ensure the stock name was submitted
        if not request.form.get("cash"):
            return apology("must provide an amount of money to add", 403)

        rows = db.execute("UPDATE users SET cash = cash + :newAmount WHERE id = :user_id", newAmount=request.form.get("cash"), user_id=session["user_id"])
        flash("Money successfully added to account!")
        return redirect("/")

    else:
        return render_template("wallet.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # Ensure the stock name was submitted
        if not request.form.get("symbol"):
            return apology("must provide a stock name", 403)

        # Ensure number of shares was submitted
        elif not request.form.get("shares").isdigit():
            return apology("must provide a valid number of shares", 403)
        symbol = request.form.get("symbol").upper()
        # Look up if there is a stock with this name on the API
        stock = lookup(symbol)

        # Ensure the stock name is valid
        if stock is None:
            return apology("invalid stock name", 403)

        # Subtracting money only from the current user on the session
        rows = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])
        cash = rows[0]["cash"]
        shares = int(request.form.get("shares"))

        # Subtracting money from the user's total
        updatedCash = cash - shares * stock["price"]

        if updatedCash < 0:
            return apology("you can't afford that at the moment", "sorry")

        # Update the total cash from the current user
        db.execute("UPDATE users SET cash=:updatedCash WHERE id=:id", updatedCash=updatedCash, id=session["user_id"])

        # Update the transactions table
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (:user_id, :symbol, :shares, :price)", user_id=session["user_id"], symbol=stock["symbol"], shares=shares, price=stock["price"])
        flash("Congratulations! Your purchase was sucessful.")

        # Redirect user to home page
        return redirect("/")
    else:
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute("SELECT symbol, shares, price, transacted FROM transactions WHERE user_id=:user_id", user_id=session["user_id"])
    # Converting to USD dollars
    for i in range(len(transactions)):
        transactions[i]["price"] = usd(transactions[i]["price"])
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
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
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure the stock name was submitted
        if not request.form.get("symbol"):
            return apology("must provide a stock name", 403)

        symbol = request.form.get("symbol").upper()

        # Look up the users input on the API
        stock = lookup(symbol)

        # Ensure the stock name is valid
        if stock is None:
            return apology("invalid stock name", 403)
        # Return data from API
        return render_template("quoted.html", stock={
            'name': stock['name'],
            'symbol': stock['symbol'],
            'price': usd(stock['price'])
        })
    else:
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure password was submitted two times
        elif not request.form.get("confirmation"):
            return apology("must type your password again", 403)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("both passwords must match", 403)

        falsePassword = validate(request.form.get("password"))
        # If there's a validation error, return the error
        if falsePassword:
            return falsePassword

        # Insert the new username into the database
        try:
            rows = db.execute("INSERT INTO users (username, hash) VALUES(:username, :password)", username=request.form.get("username"), password=generate_password_hash(request.form.get("password")))
        except:
            return apology("username already taken", 403)

        # Remember which session it is
        session["user_id"] = rows

        # Redirect user to home page
        return redirect("/")
    else:
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # Ensure the stock name was submitted
        if not request.form.get("symbol"):
            return apology("must provide a stock name", 403)

        # Ensure number of shares was submitted
        elif not request.form.get("shares").isdigit():
            return apology("must provide a valid number of shares", 403)
        symbol = request.form.get("symbol").upper()

        # Look up if there is a stock with this name on the API
        stock = lookup(symbol)
        shares = int(request.form.get("shares"))

        rows = db.execute("SELECT symbol, SUM(shares) as totalShares FROM transactions WHERE user_id=:user_id GROUP BY symbol HAVING totalShares > 0;", user_id=session["user_id"])
        for row in rows:
            if row["symbol"] == symbol:
                # You can't sell more shares than you have
                if shares > row["totalShares"]:
                    return apology("can't sell more shares than what you have")

        # Adding money only from the current user on the session
        rows = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])
        cash = rows[0]["cash"]

        # Adding money to the user's total
        updatedCash = cash + shares * stock["price"]

        # Update the total cash from the current user
        db.execute("UPDATE users SET cash=:updatedCash WHERE id=:id", updatedCash=updatedCash, id=session["user_id"])

        # Update the transactions table
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (:user_id, :symbol, :shares, :price)", user_id=session["user_id"], symbol=stock["symbol"], shares=shares * -1, price=stock["price"])
        flash("Congratulations! Your sale was sucessful.")

        # Redirect user to home page
        return redirect("/")
    else:
        # User reached route via GET (as by clicking a link or via redirect)
        rows = db.execute("SELECT symbol FROM transactions WHERE user_id=:user_id GROUP BY symbol HAVING SUM(shares) > 0;", user_id=session["user_id"])
        return render_template("sell.html", symbols=[row["symbol"] for row in rows])


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == "__main__":
    app.run()