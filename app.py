from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, Investor, Stocks, Bonds, RealEstate, GoldBonds, FixedDeposits, InvestsInStocks, InvestsInBonds, InvestsInRealEstate, InvestsInGoldBonds, InvestsInFixedDeposits  # Make sure all models are imported
import re
import psycopg2

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'
db.init_app(app)

# Ensure the tables are created
with app.app_context():
    db.create_all()

@app.route('/')
def page0():
    return render_template('page0.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        dob = request.form.get('dob')
        password = request.form.get('password')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_investor = Investor(name=name, email=email, dob=dob, password=hashed_password)
        try:
            db.session.add(new_investor)
            db.session.commit()
            flash('Account created successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            error_message = str(e)
            if 'Age must be at least 18 years old.' in error_message:
                flash('Age must be at least 18 years old.', 'error')
            else:
                flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('page0'))

        return redirect(url_for('page0'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        investor = Investor.query.filter_by(email=email).first()
        if investor and check_password_hash(investor.password, password):
            session['user_email'] = investor.email
            return redirect(url_for('page1'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('page0'))

    return render_template('login.html')

@app.route('/page1')
def page1():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    return render_template('page1.html')

@app.route('/stocks')
def stocks():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    
    stocks = Stocks.query.all()
    return render_template('stocks1.html', stocks=stocks)

@app.route('/bonds')
def bonds():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    
    bonds = Bonds.query.all()
    return render_template('bonds1.html', bonds=bonds)

@app.route('/realestate')
def realestate():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    
    realestate = RealEstate.query.all()
    return render_template('realestate1.html', realestate=realestate)

@app.route('/goldbonds')
def goldbonds():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    
    goldbonds = GoldBonds.query.all()
    return render_template('goldbonds1.html', goldbonds=goldbonds)

@app.route('/fixeddeposits')
def fixeddeposits():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    
    fixeddeposits = FixedDeposits.query.all()
    return render_template('fixeddeposits1.html', fixeddeposits=fixeddeposits)

@app.route('/newinvestment')
def new_investment():
    if 'user_email' not in session:
        flash('You need to be logged in to view this page.')
        return redirect(url_for('page0'))
    return render_template('newinvestment.html')

@app.route('/newstock', methods=['GET', 'POST'])
def new_stock():
    if 'user_email' not in session:
        flash('You need to be logged in to view this page.')
        return redirect(url_for('page0'))
    
    if request.method == 'POST':
        ticker = request.form['ticker']
        name = request.form['name']
        open_price = request.form['open']
        high = request.form['high']
        low = request.form['low']
        price = request.form['price']
        sector = request.form['sector']
        pe_ratio = request.form['pe_ratio']
        eps = request.form['eps']
        # investment_amount = request.form['investment_amount']
        purchasedate = request.form['purchasedate']
        quantity = request.form['quantity']
        
        # Get the logged-in user's email
        investoremail = session['user_email']
        
        # Create a new stock object
        new_stock = Stocks(
            ticker=ticker, name=name, open=open_price, high=high,
            low=low, price=price, sector=sector, pe_ratio=pe_ratio, eps=eps
        )
        db.session.add(new_stock)
        db.session.commit()
        
        # Create a new investment record
        invests_in_stocks = InvestsInStocks(
            investoremail=investoremail, stockticker=ticker, purchasedate=purchasedate,
            quantity=quantity
        )
        db.session.add(invests_in_stocks)
        db.session.commit()
        
        flash('New stock and investment added successfully.')
        return redirect(url_for('stocks'))

    return render_template('newstock.html')

@app.route('/newbond', methods=['GET', 'POST'])
def new_bond():
    if 'user_email' not in session:
        flash('You need to be logged in to view this page.')
        return redirect(url_for('page0'))
    
    if request.method == 'POST':
        purchaseprice = request.form['purchaseprice']
        issuer = request.form['issuer']
        interestrate = request.form['interestrate']
        maturitydate = request.form['maturitydate']
        maturityamount = request.form['maturityamount']
        purchasedate = request.form['purchasedate']
        quantity = request.form['quantity']
        
        # Get the logged-in user's email
        investoremail = session['user_email']
        
        # Create a new bond object
        new_bond = Bonds(
            purchaseprice=purchaseprice, issuer=issuer, interestrate=interestrate,
            maturitydate=maturitydate, maturityamount=maturityamount
        )
        db.session.add(new_bond)
        db.session.commit()
        
        # Retrieve the bond ID after committing the new bond
        bond_id = new_bond.id
        
        # Create a new investment record
        invests_in_bonds = InvestsInBonds(
            investoremail=investoremail, bondid=bond_id, purchasedate=purchasedate,
            quantity=quantity
        )
        db.session.add(invests_in_bonds)
        db.session.commit()
        
        flash('New bond and investment added successfully.')
        return redirect(url_for('bonds'))

    return render_template('newbond.html')

@app.route('/newrealestate', methods=['GET', 'POST'])
def new_realestate():
    if 'user_email' not in session:
        flash('You need to be logged in to view this page.')
        return redirect(url_for('page0'))
    
    if request.method == 'POST':
        type = request.form['type']
        acreage = request.form['acreage']
        address = request.form['address']
        purchaseprice = request.form['purchaseprice']
        # sellingprice = request.form['sellingprice']
        currentval = request.form['currentval']
        purchasedate = request.form['purchasedate']
        
        # Get the logged-in user's email
        investoremail = session['user_email']
        
        # Create a new real estate object
        new_realestate = RealEstate(
            type=type, acreage=acreage, address=address,
            purchaseprice=purchaseprice, currentval=currentval
        )
        db.session.add(new_realestate)
        db.session.commit()
        
        # Retrieve the property ID after committing the new real estate
        property_id = new_realestate.propertyid
        
        # Create a new investment record
        invests_in_realestate = InvestsInRealEstate(
            investoremail=investoremail, propertyid=property_id, purchasedate=purchasedate
        )
        db.session.add(invests_in_realestate)
        db.session.commit()
        
        flash('New real estate property and investment added successfully.')
        return redirect(url_for('realestate'))

    return render_template('newrealestate.html')


@app.route('/newgoldbond', methods=['GET', 'POST'])
def new_goldbond():
    if 'user_email' not in session:
        flash('You need to be logged in to view this page.')
        return redirect(url_for('page0'))
    
    if request.method == 'POST':
        issueprice = request.form['issueprice']
        maturitydate = request.form['maturitydate']
        maturityamount = request.form['maturityamount']
        interestrate = request.form['interestrate']
        nominee = request.form['nominee']
        purchasedate = request.form['purchasedate']
        quantity = request.form['quantity']
        
        # Get the logged-in user's email
        investoremail = session['user_email']
        
        # Create a new gold bond object
        new_goldbond = GoldBonds(
            issueprice=issueprice, maturitydate=maturitydate,
            maturityamount=maturityamount, interestrate=interestrate, nominee=nominee
        )
        db.session.add(new_goldbond)
        db.session.commit()
        
        # Retrieve the gold bond ID after committing the new gold bond
        goldbond_id = new_goldbond.id
        
        # Create a new investment record
        invests_in_goldbonds = InvestsInGoldBonds(
            investoremail=investoremail, goldbondid=goldbond_id, purchasedate=purchasedate, quantity=quantity
        )
        db.session.add(invests_in_goldbonds)
        db.session.commit()
        
        flash('New gold bond and investment added successfully.')
        return redirect(url_for('goldbonds'))

    return render_template('newgoldbond.html')


@app.route('/newfixeddeposit', methods=['GET', 'POST'])
def new_fixeddeposit():
    if 'user_email' not in session:
        flash('You need to be logged in to view this page.')
        return redirect(url_for('page0'))
    
    if request.method == 'POST':
        accountnumber = request.form['accountnumber']
        principal = request.form['principal']
        interestrate = request.form['interestrate']
        maturityamount = request.form['maturityamount']
        maturitydate = request.form['maturitydate']
        nominee = request.form['nominee']
        penalty = request.form['penalty']
        startdate = request.form['startdate']
        
        # Get the logged-in user's email
        investoremail = session['user_email']
        
        # Create a new fixed deposit object
        new_fixeddeposit = FixedDeposits(
            accountnumber=accountnumber, principal=principal, interestrate=interestrate,
            maturityamount=maturityamount, maturitydate=maturitydate, nominee=nominee, penalty=penalty
        )
        db.session.add(new_fixeddeposit)
        db.session.commit()
        
        # Create a new investment record
        invests_in_fixeddeposits = InvestsInFixedDeposits(
            investoremail=investoremail, accountnumber=accountnumber, startdate=startdate
        )
        db.session.add(invests_in_fixeddeposits)
        db.session.commit()
        
        flash('New fixed deposit and investment added successfully.')
        return redirect(url_for('fixeddeposits'))

    return render_template('newfixeddeposit.html')





@app.route('/reports')
def reports():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    # Add logic to render the reports page
    return render_template('reports.html')

def get_best_stock():
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()
    cur.execute("SELECT * FROM best_stock()")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

def get_best_bond():
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()
    cur.execute("SELECT * FROM best_bond()")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

def get_best_realestate():
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()
    cur.execute("SELECT * FROM best_realestate()")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

def get_best_goldbond():
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()
    cur.execute("SELECT * FROM best_goldbond()")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

def get_best_fixeddeposit():
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()
    cur.execute("SELECT * FROM best_fixeddeposit()")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

@app.route('/best_investment')
def best_investment():
    best_stock = get_best_stock()
    best_bond = get_best_bond()
    best_realestate = get_best_realestate()
    best_goldbond = get_best_goldbond()
    best_fixeddeposit = get_best_fixeddeposit()
    return render_template('best_investment.html', best_stock=best_stock, best_bond=best_bond, best_realestate=best_realestate, best_goldbond=best_goldbond, best_fixeddeposit=best_fixeddeposit)
    # return render_template('best_investment.html', best_stock=best_stock)

@app.route('/self-nominated-investments')
#@login_required
def self_nominated_investments():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    current_user_email = session['user_email']

    # Fetch self-nominated gold bonds
    goldbonds = get_self_nominated_goldbonds(current_user_email)

    # Fetch self-nominated fixed deposits
    fixeddeposits = get_self_nominated_fixeddeposits(current_user_email)

    return render_template('selfnom.html', goldbonds=goldbonds, fixeddeposits=fixeddeposits)

def get_self_nominated_goldbonds(user_email):
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_self_nominated_goldbonds(%s)", (user_email,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def get_self_nominated_fixeddeposits(user_email):
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_self_nominated_fixeddeposits(%s)", (user_email,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

@app.route('/other-nominated-investments')
#@login_required
def other_nominated_investments():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    current_user_email = session['user_email']

    # Fetch self-nominated gold bonds
    goldbonds = get_other_nominated_goldbonds(current_user_email)

    # Fetch self-nominated fixed deposits
    fixeddeposits = get_other_nominated_fixeddeposits(current_user_email)

    return render_template('othernom.html', goldbonds=goldbonds, fixeddeposits=fixeddeposits)

def get_other_nominated_goldbonds(user_email):
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_other_nominated_goldbonds(%s)", (user_email,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def get_other_nominated_fixeddeposits(user_email):
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_other_nominated_fixeddeposits(%s)", (user_email,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

@app.route('/about')
def about():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    return render_template('about.html')

@app.route('/profile')
def profile():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    return render_template('profile.html')

@app.route('/sell_investment')
def sell_investment():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('login'))
    return render_template('sellinvestment.html')

@app.route('/sell_stock')
def sell_stock():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('login'))
    return render_template('sellstock.html')

@app.route('/process_sell_stock', methods=['POST'])
def process_sell_stock():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('login'))

    user_email = session['user_email']
    ticker = request.form['ticker']
    quantity = int(request.form['quantity'])

    # Connect to the database
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()

    # Check if the stock is already purchased by the user and the quantity is sufficient
    cur.execute("SELECT quantity FROM investsinstocks WHERE investoremail = %s AND stockticker = %s", (user_email, ticker))
    result = cur.fetchone()

    if result is None:
        flash('You do not own this stock.', 'error')
        return redirect(url_for('sell_stock'))

    current_quantity = result[0]
    if quantity > current_quantity:
        flash('You do not own enough quantity of this stock.', 'error')
        return redirect(url_for('sell_stock'))

    # Update the database: Deduct quantity and set sale date
    new_quantity = current_quantity - quantity
    cur.execute("""
        UPDATE investsinstocks 
        SET quantity = %s, saledate = CURRENT_DATE 
        WHERE investoremail = %s AND stockticker = %s
    """, (new_quantity, user_email, ticker))

    conn.commit()
    cur.close()
    conn.close()

    flash('Stock sold successfully.', 'success')
    return redirect(url_for('sell_stock'))

@app.route('/sell_bond')
def sell_bond():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('login'))
    return render_template('sellbond.html')

@app.route('/process_sell_bond', methods=['POST'])
def process_sell_bond():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('login'))

    user_email = session['user_email']
    bond_id = int(request.form['bond_id'])
    quantity = int(request.form['quantity'])

    # Connect to the database
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()

    # Check if the bond is already purchased by the user and the quantity is sufficient
    cur.execute("SELECT quantity FROM investsinbonds WHERE investoremail = %s AND bondid = %s", (user_email, bond_id))
    result = cur.fetchone()

    if result is None:
        flash('You do not own this bond.', 'error')
        return redirect(url_for('sell_bond'))

    current_quantity = result[0]
    if quantity > current_quantity:
        flash('You do not own enough quantity of this bond.', 'error')
        return redirect(url_for('sell_bond'))

    # Update the database: Deduct quantity and set sale date
    new_quantity = current_quantity - quantity
    cur.execute("""
        UPDATE investsinbonds 
        SET quantity = %s, saledate = CURRENT_DATE 
        WHERE investoremail = %s AND bondid = %s
    """, (new_quantity, user_email, bond_id))

    conn.commit()
    cur.close()
    conn.close()

    flash('Bond sold successfully.', 'success')
    return redirect(url_for('sell_bond'))


@app.route('/sell_realestate')
def sell_realestate():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('login'))
    return render_template('sellrealestate.html')

@app.route('/process_sell_realestate', methods=['POST'])
def process_sell_realestate():
    # Check if user is logged in
    if 'user_email' not in session:
        flash('You must be logged in to sell real estate.', 'error')
        return redirect(url_for('login'))

    # Retrieve form data
    property_id = request.form['property_id']
    user_email = session['user_email']

    # Connect to the database
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()

    try:
        # Validate if property belongs to user
        cur.execute("SELECT COUNT(*) FROM investsinrealestate WHERE investoremail = %s AND propertyid = %s", (user_email, property_id))
        count = cur.fetchone()[0]
        if count == 0:
            flash('You do not own real estate with the provided property ID.', 'error')
            return redirect(url_for('sell_realestate'))

        # Update sale date in investsinrealestate table
        cur.execute("UPDATE investsinrealestate SET saledate = CURRENT_DATE WHERE investoremail = %s AND propertyid = %s", (user_email, property_id))

        # Delete real estate from realestate table if sale is successful (implemented by trigger)
        conn.commit()
        flash('Real estate sold successfully!', 'success')
        return redirect(url_for('sell_realestate'))

    except psycopg2.Error as e:
        # Handle any database errors
        conn.rollback()
        flash('An error occurred while processing your request. Please try again later.', 'error')
        return redirect(url_for('sell_realestate'))

    finally:
        # Close cursor and connection
        cur.close()
        conn.close()


@app.route('/sell_goldbond')
def sell_goldbond():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('login'))
    return render_template('sellgoldbond.html')

@app.route('/process_sell_goldbond', methods=['POST'])
def process_sell_goldbond():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('login'))

    user_email = session['user_email']
    goldbond_id = int(request.form['goldbond_id'])
    quantity = int(request.form['quantity'])

    # Connect to the database
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()

    # Check if the gold bond is already purchased by the user and the quantity is sufficient
    cur.execute("SELECT quantity FROM investsingoldbonds WHERE investoremail = %s AND goldbondid = %s", (user_email, goldbond_id))
    result = cur.fetchone()

    if result is None:
        flash('You do not own this gold bond.', 'error')
        return redirect(url_for('sell_goldbond'))

    current_quantity = result[0]
    if quantity > current_quantity:
        flash('You do not own enough quantity of this gold bond.', 'error')
        return redirect(url_for('sell_goldbond'))

    # Update the database: Deduct quantity and set sale date
    new_quantity = current_quantity - quantity
    cur.execute("""
        UPDATE investsingoldbonds 
        SET quantity = %s, saledate = CURRENT_DATE 
        WHERE investoremail = %s AND goldbondid = %s
    """, (new_quantity, user_email, goldbond_id))

    conn.commit()
    cur.close()
    conn.close()

    flash('Gold bond sold successfully.', 'success')
    return redirect(url_for('sell_goldbond'))

@app.route('/payment')
def payment():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('login'))
    return render_template('payment.html')

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('page0'))

#@app.route('/best_investment')
#def best_investment():
#    # Implement the logic for best investment report
#    return render_template('best_investment.html')

#@app.route('/self_nominated_investments')
#def self_nominated_investments():
#    # Implement the logic for self-nominated investments report
#    return render_template('self_nominated_investments.html')

#@app.route('/other_nominated_investments')
#def other_nominated_investments():
#    # Implement the logic for other-nominated investments report
#    return render_template('other_nominated_investments.html')

@app.route('/currency_conversions')
def currency_conversions():
    # Implement the logic for currency conversions
    return render_template('currency_conversions.html')

@app.route('/stocks2')
def stocks2():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    
    user_email = session['user_email']
    #print(f"User email from session: {user_email}")  # Debugging line
    # Connect to the database
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()
    
    # Fetch data from the view and filter by the user's email
    cur.execute("SELECT ticker, name, open_usd, high_usd, low_usd, price_usd, sector, pe_ratio, eps FROM stocks_usd WHERE investoremail = %s", (user_email,))
    stocks = cur.fetchall()
    #print(f"Fetched stocks: {stocks}")  # Debugging line
    # Close the cursor and connection
    cur.close()
    conn.close()
    
    return render_template('stocks0.html', stocks=stocks)

@app.route('/bonds2')
def bonds2():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    
    user_email = session['user_email']
    
    # Connect to the database
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()
    
    # Fetch data from the view and filter by the user's email
    cur.execute("SELECT id, purchaseprice_usd, issuer, interestrate, maturitydate, maturityamount_usd FROM bonds_usd WHERE investoremail = %s", (user_email,))
    bonds = cur.fetchall()
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
    return render_template('bonds0.html', bonds=bonds)

@app.route('/realestate2')
def realestate2():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    
    user_email = session['user_email']
    
    # Connect to the database
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()
    
    # Fetch data from the view and filter by the user's email
    cur.execute("SELECT propertyid, type, acreage, address, purchaseprice_usd, sellingprice_usd, currentval_usd FROM realestate_usd WHERE investoremail = %s", (user_email,))
    realestate = cur.fetchall()
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
    return render_template('realestate0.html', realestate=realestate)

@app.route('/goldbonds2')
def goldbonds2():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    
    user_email = session['user_email']
    print(f"User email from session: {user_email}")  # Debugging line
    # Connect to the database
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()
    
    # Fetch data from the view and filter by the user's email
    cur.execute("SELECT id, issueprice_usd, maturitydate, maturityamount_usd, interestrate, nominee FROM goldbonds_usd WHERE investoremail = %s", (user_email,))
    goldbonds = cur.fetchall()
    print(f"Fetched gold bonds: {goldbonds}")  # Debugging line
    # Close the cursor and connection
    cur.close()
    conn.close()
    
    return render_template('goldbonds0.html', goldbonds=goldbonds)

@app.route('/fixeddeposits2')
def fixeddeposits2():
    if 'user_email' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(url_for('page0'))
    
    user_email = session['user_email']
    
    # Connect to the database
    conn = psycopg2.connect("dbname=test user=postgres password=ShaAric@2024 host=localhost")
    cur = conn.cursor()
    
    # Fetch data from the view and filter by the user's email
    cur.execute("SELECT accountnumber, principal_usd, interestrate, maturityamount_usd, maturitydate, nominee, penalty_usd FROM fixeddeposits_usd WHERE investoremail = %s", (user_email,))
    fixeddeposits = cur.fetchall()
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
    return render_template('fixeddeposits0.html', fixeddeposits=fixeddeposits)


if __name__ == '__main__':
    app.run(debug=True)