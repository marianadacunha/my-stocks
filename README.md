# CS50 Finance
Implement a website via which users can “buy” and “sell” stocks, a la the below.

![C$50 Finance](https://cs50.harvard.edu/x/2020/tracks/web/finance/finance.png)

# Setup
To run this project, you will nedd to install Flask locally using the pip command.
You can run this command from your command prompt window.
```
$ pip install flask
```
Then run the python script and go to the URL https://127.0.0.1:5000/ from a web browser.
```
$ python "application.py"
```

# Preview
![Screenshot](https://i.ibb.co/Pcr0B2H/Captura-de-tela-2020-09-11-18-07-58.png)

# Background
You’re about to implement a web app via which you can manage portfolios of stocks. Not only will this tool allow you to check real stocks’ actual prices and portfolios’ values, it will also let you “buy” and "sell" stocks by querying IEX for stocks’ prices.

Indeed, IEX lets you download stock quotes via their API (application programming interface) using URLs like https://cloud-sse.iexapis.com/stable/stock/nflx/quote?token=API_KEY. Notice how Netflix’s symbol (NFLX) is embedded in this URL; that’s how IEX knows whose data to return. That link won’t actually return any data because IEX requires you to use an API key, but if it did, you’d see a response in JSON (JavaScript Object Notation) format like this:
```
 {  
    "symbol": "NFLX",</br>
    "companyName": "Netflix, Inc.",</br>
    "primaryExchange": "NASDAQ",</br>
    "calculationPrice": "close",</br>
    "open": 317.49,</br>
    "openTime": 1564752600327,</br>
    "close": 318.83,</br>
    "closeTime": 1564776000616,</br>
    "high": 319.41,</br>
    "low": 311.8,</br>
    "latestPrice": 318.83,</br>
    "latestSource": "Close",</br>
    "latestTime": "August 2, 2019",</br>
    "latestUpdate": 1564776000616,</br>
    "latestVolume": 6232279,</br>
    "iexRealtimePrice": null,</br>
    "iexRealtimeSize": null,</br>
    "iexLastUpdated": null,</br>
    "delayedPrice": 318.83,</br>
    "delayedPriceTime": 1564776000616,</br>
    "extendedPrice": 319.37,</br>
    "extendedChange": 0.54,</br>
    "extendedChangePercent": 0.00169,</br>
    "extendedPriceTime": 1564876784244,</br>
    "previousClose": 319.5,</br>
    "previousVolume": 6563156,</br>
    "change": -0.67,</br>
    "changePercent": -0.0021,</br>
    "volume": 6232279,</br>
    "iexMarketPercent": null,</br>
    "iexVolume": null,</br>
    "avgTotalVolume": 7998833,</br>
    "iexBidPrice": null,</br>
    "iexBidSize": null,</br>
    "iexAskPrice": null,</br>
    "iexAskSize": null,</br>
    "marketCap": 139594933050,</br>
    "peRatio": 120.77,</br>
    "week52High": 386.79,</br>
    "week52Low": 231.23,</br>
    "ytdChange": 0.18907500000000002,</br>
    "lastTradeTime": 1564776000616</br>
 }
```

Notice how, between the curly braces, there’s a comma-separated list of key-value pairs, with a colon separating each key from its value.

Let’s turn our attention now to this problem’s distribution code!

# Specification

### register
Complete the implementation of register in such a way that it allows a user to register for an account via a form.

* Require that a user input a username, implemented as a text field whose name is username. Render an apology if the user’s input is blank or the username already exists.
* Require that a user input a password, implemented as a text field whose name is password, and then that same password again, implemented as a text field whose name is confirmation. Render an apology if either input is blank or the passwords do not match.
* Submit the user’s input via POST to /register.
* INSERT the new user into users, storing a hash of the user’s password, not the password itself. Hash the user’s password with generate_password_hash Odds are you’ll want to create a new template (e.g., register.html) that’s quite similar to login.html.

Once you’ve implemented register correctly, you should be able to register for an account and log in (since login and logout already work)! And you should be able to see your rows via phpLiteAdmin or sqlite3.

### quote
Complete the implementation of quote in such a way that it allows a user to look up a stock’s current price.

* Require that a user input a stock’s symbol, implemented as a text field whose name is symbol.
* Submit the user’s input via POST to /quote.
* Odds are you’ll want to create two new templates (e.g., quote.html and quoted.html). When a user visits /quote via GET, render one of those templates, inside of which should be an HTML form that submits to /quote via POST. In response to a POST, quote can render that second template, embedding within it one or more values from lookup.

### buy
Complete the implementation of buy in such a way that it enables a user to buy stocks.

* Require that a user input a stock’s symbol, implemented as a text field whose name is symbol. Render an apology if the input is blank or the symbol does not exist (as per the return value of lookup).
* Require that a user input a number of shares, implemented as a text field whose name is shares. Render an apology if the input is not a positive integer.
* Submit the user’s input via POST to /buy.
* Odds are you’ll want to call lookup to look up a stock’s current price.
*Odds are you’ll want to SELECT how much cash the user currently has in users.
* Add one or more new tables to finance.db via which to keep track of the purchase. Store enough information so that you know who bought what at what price and when.
  * Use appropriate SQLite types.
  * Define UNIQUE indexes on any fields that should be unique.
  * Define (non-UNIQUE) indexes on any fields via which you will search (as via SELECT with WHERE).
* Render an apology, without completing a purchase, if the user cannot afford the number of shares at the current price.
* You don’t need to worry about race conditions (or use transactions).

Once you’ve implemented buy correctly, you should be able to see users’ purchases in your new table(s) via phpLiteAdmin or sqlite3

### index
Complete the implementation of index in such a way that it displays an HTML table summarizing, for the user currently logged in, which stocks the user owns, the numbers of shares owned, the current price of each stock, and the total value of each holding (i.e., shares times price). Also display the user’s current cash balance along with a grand total (i.e., stocks’ total value plus cash).

* Odds are you’ll want to execute multiple SELECTs. Depending on how you implement your table(s), you might find GROUP BY HAVING SUM and/or WHERE of interest.
* Odds are you’ll want to call lookup for each stock.

### sell
Complete the implementation of sell in such a way that it enables a user to sell shares of a stock (that he or she owns).

* Require that a user input a stock’s symbol, implemented as a select menu whose name is symbol. Render an apology if the user fails to select a stock or if (somehow, once submitted) the user does not own any shares of that stock.
* Require that a user input a number of shares, implemented as a text field whose name is shares. Render an apology if the input is not a positive integer or if the user does not own that many shares of the stock.
* Submit the user’s input via POST to /sell.
* You don’t need to worry about race conditions (or use transactions).

### history
Complete the implementation of history in such a way that it displays an HTML table summarizing all of a user’s transactions ever, listing row by row each and every buy and every sell.

* For each row, make clear whether a stock was bought or sold and include the stock’s symbol, the (purchase or sale) price, the number of shares bought or sold, and the date and time at which the transaction occurred.
* You might need to alter the table you created for buy or supplement it with an additional table. Try to minimize redundancies.

### personal touch

Implement at least one personal touch of your choice:

* Allow users to change their passwords.
* Allow users to add additional cash to their account.
* Allow users to buy more shares or sell shares of stocks they already own via index itself, without having to type stocks’ symbols manually.
* Require users’ passwords to have some number of letters, numbers, and/or symbols.
* Implement some other feature of comparable scope.

# Testing
Be sure to test your web app manually too, as by

* inputting alpabetical strings into forms when only numbers are expected,
* inputting zero or negative numbers into forms when only positive numbers are expected,
* inputting floating-point values into forms when only integers are expected,
* trying to spend more cash than a user has,
* trying to sell more shares than a user has,
* inputting an invalid stock symbol, and
* including potentially dangerous characters like ' and ; in SQL queries.
