import os
import datetime
import mysql.connector
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
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
    password=os.getenv("MYSQL_PASSWORD"),  # Retrieve MySQL password from environment variable
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
    
    from flask import url_for

@app.route("/clientes")
@login_required
def clientes():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers")
    clientes = cursor.fetchall()
    return render_template("clientes.html", clientes=clientes)

@app.route("/clientes/novo", methods=["GET", "POST"])
@login_required
def novo_cliente():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        telefone = request.form["telefone"]
        endereco = request.form["endereco"]
        cursor = db.cursor()
        cursor.execute("INSERT INTO customers (name, email, phone, address) VALUES (%s, %s, %s, %s)", (nome, email, telefone, endereco))
        db.commit()
        return redirect(url_for('clientes'))
    return render_template("cliente_form.html", cliente=None)

@app.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_cliente(id):
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        telefone = request.form["telefone"]
        endereco = request.form["endereco"]
        cursor.execute("UPDATE customers SET name=%s, email=%s, phone=%s, address=%s WHERE id=%s", (nome, email, telefone, endereco, id))
        db.commit()
        return redirect(url_for('clientes'))
    cursor.execute("SELECT * FROM customers WHERE id=%s", (id,))
    cliente = cursor.fetchone()
    return render_template("cliente_form.html", cliente=cliente)

@app.route("/clientes/excluir/<int:id>", methods=["GET", "POST"])
@login_required
def excluir_cliente(id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers WHERE id=%s", (id,))
    cliente = cursor.fetchone()
    if request.method == "POST":
        cursor = db.cursor()
        cursor.execute("DELETE FROM customers WHERE id=%s", (id,))
        db.commit()
        return redirect(url_for('clientes'))
    return render_template("confirmar_exclusao.html", objeto=cliente, voltar_url=url_for('clientes'))

@app.route("/pets")
@login_required
def pets():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pets")
    pets = cursor.fetchall()
    return render_template("pets.html", pets=pets)

@app.route("/pets/novo", methods=["GET", "POST"])
@login_required
def novo_pet():
    if request.method == "POST":
        nome = request.form["nome"]
        especie = request.form["especie"]
        raca = request.form["raca"]
        idade = request.form["idade"]
        dono_id = request.form["dono_id"]
        cursor = db.cursor()
        cursor.execute("INSERT INTO pets (name, species, breed, age, owner_id) VALUES (%s, %s, %s, %s, %s)", (nome, especie, raca, idade, dono_id))
        db.commit()
        return redirect(url_for('pets'))
    # Buscar clientes para selecionar o dono
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM customers")
    clientes = cursor.fetchall()
    return render_template("pet_form.html", pet=None, clientes=clientes)

@app.route("/pets/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_pet(id):
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        nome = request.form["nome"]
        especie = request.form["especie"]
        raca = request.form["raca"]
        idade = request.form["idade"]
        dono_id = request.form["dono_id"]
        cursor.execute("UPDATE pets SET name=%s, species=%s, breed=%s, age=%s, owner_id=%s WHERE id=%s", (nome, especie, raca, idade, dono_id, id))
        db.commit()
        return redirect(url_for('pets'))
    cursor.execute("SELECT * FROM pets WHERE id=%s", (id,))
    pet = cursor.fetchone()
    cursor.execute("SELECT id, name FROM customers")
    clientes = cursor.fetchall()
    return render_template("pet_form.html", pet=pet, clientes=clientes)

@app.route("/pets/excluir/<int:id>", methods=["GET", "POST"])
@login_required
def excluir_pet(id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pets WHERE id=%s", (id,))
    pet = cursor.fetchone()
    if request.method == "POST":
        cursor = db.cursor()
        cursor.execute("DELETE FROM pets WHERE id=%s", (id,))
        db.commit()
        return redirect(url_for('pets'))
    return render_template("confirmar_exclusao.html", objeto=pet, voltar_url=url_for('pets'))

@app.route("/produtos")
@login_required
def produtos():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    produtos = cursor.fetchall()
    # Buscar categorias para cada produto
    for produto in produtos:
        cursor.execute("""
            SELECT pc.name FROM product_categories pc
            JOIN product_category_relation pcr ON pc.id = pcr.category_id
            WHERE pcr.product_id = %s
        """, (produto["id"],))
        categorias = [c["name"] for c in cursor.fetchall()]
        produto["categorias"] = categorias
    return render_template("produtos.html", produtos=produtos)

@app.route("/produtos/novo", methods=["GET", "POST"])
@login_required
def novo_produto():
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        nome = request.form["nome"]
        descricao = request.form["descricao"]
        preco = request.form["preco"]
        estoque = request.form["estoque"]
        categorias = request.form.getlist("categorias")
        cursor2 = db.cursor()
        cursor2.execute("INSERT INTO products (name, description, price, stock) VALUES (%s, %s, %s, %s)", (nome, descricao, preco, estoque))
        db.commit()
        produto_id = cursor2.lastrowid
        for categoria_id in categorias:
            cursor2.execute("INSERT INTO product_category_relation (product_id, category_id) VALUES (%s, %s)", (produto_id, categoria_id))
        db.commit()
        return redirect(url_for('produtos'))
    cursor.execute("SELECT * FROM product_categories")
    categorias = cursor.fetchall()
    return render_template("produto_form.html", produto=None, categorias=categorias, selecionadas=[])

@app.route("/produtos/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_produto(id):
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        nome = request.form["nome"]
        descricao = request.form["descricao"]
        preco = request.form["preco"]
        estoque = request.form["estoque"]
        categorias = request.form.getlist("categorias")
        cursor.execute("UPDATE products SET name=%s, description=%s, price=%s, stock=%s WHERE id=%s", (nome, descricao, preco, estoque, id))
        cursor.execute("DELETE FROM product_category_relation WHERE product_id=%s", (id,))
        for categoria_id in categorias:
            cursor.execute("INSERT INTO product_category_relation (product_id, category_id) VALUES (%s, %s)", (id, categoria_id))
        db.commit()
        return redirect(url_for('produtos'))
    cursor.execute("SELECT * FROM products WHERE id=%s", (id,))
    produto = cursor.fetchone()
    cursor.execute("SELECT * FROM product_categories")
    categorias = cursor.fetchall()
    cursor.execute("SELECT category_id FROM product_category_relation WHERE product_id=%s", (id,))
    selecionadas = [str(c["category_id"]) for c in cursor.fetchall()]
    return render_template("produto_form.html", produto=produto, categorias=categorias, selecionadas=selecionadas)

@app.route("/produtos/excluir/<int:id>", methods=["GET", "POST"])
@login_required
def excluir_produto(id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE id=%s", (id,))
    produto = cursor.fetchone()
    if request.method == "POST":
        cursor2 = db.cursor()
        cursor2.execute("DELETE FROM product_category_relation WHERE product_id=%s", (id,))
        cursor2.execute("DELETE FROM products WHERE id=%s", (id,))
        db.commit()
        return redirect(url_for('produtos'))
    return render_template("confirmar_exclusao.html", objeto=produto, voltar_url=url_for('produtos'))

@app.route("/vendas")
@login_required
def vendas():
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id, s.date, c.name as cliente, e.name as funcionario
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        LEFT JOIN employees e ON s.employee_id = e.id
        ORDER BY s.date DESC
    """)
    vendas = cursor.fetchall()
    return render_template("vendas.html", vendas=vendas)

@app.route("/vendas/novo", methods=["GET", "POST"])
@login_required
def nova_venda():
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        cliente_id = request.form["cliente_id"]
        funcionario_id = request.form["funcionario_id"]
        data = request.form["data"]
        cursor2 = db.cursor()
        cursor2.execute("INSERT INTO sales (customer_id, employee_id, date) VALUES (%s, %s, %s)", (cliente_id, funcionario_id, data))
        db.commit()
        return redirect(url_for('vendas'))
    cursor.execute("SELECT id, name FROM customers")
    clientes = cursor.fetchall()
    cursor.execute("SELECT id, name FROM employees")
    funcionarios = cursor.fetchall()
    return render_template("venda_form.html", venda=None, clientes=clientes, funcionarios=funcionarios)

@app.route("/vendas/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_venda(id):
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        cliente_id = request.form["cliente_id"]
        funcionario_id = request.form["funcionario_id"]
        data = request.form["data"]
        cursor.execute("UPDATE sales SET customer_id=%s, employee_id=%s, date=%s WHERE id=%s", (cliente_id, funcionario_id, data, id))
        db.commit()
        return redirect(url_for('vendas'))
    cursor.execute("SELECT * FROM sales WHERE id=%s", (id,))
    venda = cursor.fetchone()
    cursor.execute("SELECT id, name FROM customers")
    clientes = cursor.fetchall()
    cursor.execute("SELECT id, name FROM employees")
    funcionarios = cursor.fetchall()
    return render_template("venda_form.html", venda=venda, clientes=clientes, funcionarios=funcionarios)

@app.route("/vendas/excluir/<int:id>", methods=["GET", "POST"])
@login_required
def excluir_venda(id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sales WHERE id=%s", (id,))
    venda = cursor.fetchone()
    if request.method == "POST":
        cursor = db.cursor()
        cursor.execute("DELETE FROM sales WHERE id=%s", (id,))
        db.commit()
        return redirect(url_for('vendas'))
    return render_template("confirmar_exclusao.html", objeto=venda, voltar_url=url_for('vendas'))

@app.route("/funcionarios")
@login_required
def funcionarios():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees")
    funcionarios = cursor.fetchall()
    return render_template("funcionarios.html", funcionarios=funcionarios)

@app.route("/funcionarios/novo", methods=["GET", "POST"])
@login_required
def novo_funcionario():
    if request.method == "POST":
        nome = request.form["nome"]
        cargo = request.form["cargo"]
        data_contratacao = request.form["data_contratacao"]
        salario = request.form["salario"]
        cursor = db.cursor()
        cursor.execute("INSERT INTO employees (name, role, hire_date, salary) VALUES (%s, %s, %s, %s)", (nome, cargo, data_contratacao, salario))
        db.commit()
        return redirect(url_for('funcionarios'))
    return render_template("funcionario_form.html", funcionario=None)

@app.route("/funcionarios/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_funcionario(id):
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        nome = request.form["nome"]
        cargo = request.form["cargo"]
        data_contratacao = request.form["data_contratacao"]
        salario = request.form["salario"]
        cursor.execute("UPDATE employees SET name=%s, role=%s, hire_date=%s, salary=%s WHERE id=%s", (nome, cargo, data_contratacao, salario, id))
        db.commit()
        return redirect(url_for('funcionarios'))
    cursor.execute("SELECT * FROM employees WHERE id=%s", (id,))
    funcionario = cursor.fetchone()
    return render_template("funcionario_form.html", funcionario=funcionario)

@app.route("/funcionarios/excluir/<int:id>", methods=["GET", "POST"])
@login_required
def excluir_funcionario(id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees WHERE id=%s", (id,))
    funcionario = cursor.fetchone()
    if request.method == "POST":
        cursor = db.cursor()
        cursor.execute("DELETE FROM employees WHERE id=%s", (id,))
        db.commit()
        return redirect(url_for('funcionarios'))
    return render_template("confirmar_exclusao.html", objeto=funcionario, voltar_url=url_for('funcionarios'))