from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Investor(db.Model):
    __tablename__ = 'investor'
    email = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    joindate = db.Column(db.Date, default=db.func.current_date())
    status = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    __table_args__ = (
        db.CheckConstraint("status IN ('paid', 'unpaid')", name='status_check'),
    )

class Stocks(db.Model):
    __tablename__ = 'stocks'
    ticker = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(20))
    open = db.Column(db.Numeric)
    high = db.Column(db.Numeric)
    low = db.Column(db.Numeric)
    price = db.Column(db.Numeric)
    sector = db.Column(db.String(100))
    pe_ratio = db.Column(db.Numeric)
    eps = db.Column(db.Numeric)

class Bonds(db.Model):
    __tablename__ = 'bonds'
    id = db.Column(db.Integer, primary_key=True)
    purchaseprice = db.Column(db.Numeric, nullable=False)
    issuer = db.Column(db.String(100), nullable=False)
    interestrate = db.Column(db.Numeric, nullable=False)
    maturitydate = db.Column(db.Date, nullable=False)
    maturityamount = db.Column(db.Numeric, nullable=False)

class RealEstate(db.Model):
    __tablename__ = 'realestate'
    propertyid = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    acreage = db.Column(db.Numeric, nullable=False)
    address = db.Column(db.Text, nullable=False)
    purchaseprice = db.Column(db.Numeric, nullable=False)
    sellingprice = db.Column(db.Numeric)
    currentval = db.Column(db.Numeric, nullable=False)

class GoldBonds(db.Model):
    __tablename__ = 'goldbonds'
    id = db.Column(db.Integer, primary_key=True)
    issueprice = db.Column(db.Numeric, nullable=False)
    maturitydate = db.Column(db.Date, nullable=False)
    maturityamount = db.Column(db.Numeric, nullable=False)
    interestrate = db.Column(db.Numeric, nullable=False)
    nominee = db.Column(db.String(100), nullable=False)

class FixedDeposits(db.Model):
    __tablename__ = 'fixeddeposits'
    accountnumber = db.Column(db.Integer, primary_key=True)
    principal = db.Column(db.Numeric, nullable=False)
    interestrate = db.Column(db.Numeric, nullable=False)
    maturityamount = db.Column(db.Numeric, nullable=False)
    maturitydate = db.Column(db.Date, nullable=False)
    nominee = db.Column(db.String(100))
    penalty = db.Column(db.Numeric)

class InvestsInStocks(db.Model):
    __tablename__ = 'investsinstocks'
    investoremail = db.Column(db.String(100), db.ForeignKey('investor.email'), primary_key=True)
    stockticker = db.Column(db.String(10), db.ForeignKey('stocks.ticker'), primary_key=True) 
    purchasedate = db.Column(db.Date, nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=True)
    saledate = db.Column(db.Date, nullable=True)
    
    # investor = db.relationship('Investor', backref=db.backref('stock_investments', lazy=True))
    # stock = db.relationship('Stocks', backref=db.backref('investors', lazy=True))

class InvestsInBonds(db.Model):
    __tablename__ = 'investsinbonds'
    investoremail = db.Column(db.String(100), db.ForeignKey('investor.email'), primary_key=True)
    bondid = db.Column(db.Integer, db.ForeignKey('bonds.id'), primary_key=True)
    purchasedate = db.Column(db.Date, nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=True)
    saledate = db.Column(db.Date, nullable=True)
    
    # investor = db.relationship('Investor', backref=db.backref('bond_investments', lazy=True))
    # bond = db.relationship('Bonds', backref=db.backref('investors', lazy=True))

class InvestsInRealEstate(db.Model):
    __tablename__ = 'investsinrealestate'
    investoremail = db.Column(db.String(100), db.ForeignKey('investor.email'), primary_key=True)
    propertyid = db.Column(db.Integer, db.ForeignKey('realestate.propertyid'), primary_key=True)
    purchasedate = db.Column(db.Date, nullable=True)
    saledate = db.Column(db.Date, nullable=True)

    # investor = db.relationship('Investor', backref=db.backref('realestate_investments', lazy=True))
    # property = db.relationship('RealEstate', backref=db.backref('investors', lazy=True))

class InvestsInGoldBonds(db.Model):
    __tablename__ = 'investsingoldbonds'
    investoremail = db.Column(db.String(100), db.ForeignKey('investor.email'), primary_key=True)
    goldbondid = db.Column(db.Integer, db.ForeignKey('goldbonds.id'), primary_key=True)
    purchasedate = db.Column(db.Date, nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=True)
    saledate = db.Column(db.Date, nullable=True)

    # Relationships (optional)
    # investor = db.relationship('Investor', backref=db.backref('goldbond_investments', lazy=True))
    # goldbond = db.relationship('GoldBonds', backref=db.backref('investors', lazy=True))

class InvestsInFixedDeposits(db.Model):
    __tablename__ = 'investsinfixeddeposits'
    investoremail = db.Column(db.String(100), db.ForeignKey('investor.email'), primary_key=True)
    accountnumber = db.Column(db.Integer, db.ForeignKey('fixeddeposits.accountnumber'), primary_key=True)
    startdate = db.Column(db.Date, nullable=False, primary_key=True)

    # Relationships (optional)
    # investor = db.relationship('Investor', backref=db.backref('fixeddeposit_investments', lazy=True))
    # fixeddeposit = db.relationship('FixedDeposits', backref=db.backref('investors', lazy=True))
