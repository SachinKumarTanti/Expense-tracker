from flask import Flask,render_template,request,redirect,url_for,Response,session,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date,datetime
import csv,io
from sqlalchemy import func
from dotenv import load_dotenv
import os

from flask_login import current_user,LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash



load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
#Database config. setup
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db=SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

# ---------------- MODEL ----------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    expenses = db.relationship("Expense", backref="user", lazy=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- ROUTES ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("User already exists", "signup_error")
            return redirect(url_for("signup"))

        hashed = generate_password_hash(password)
        user = User(username=username, password=hashed)
        db.session.add(user)
        db.session.commit()
        #login user immediately after signup
        login_user(user)
        flash("Account created, login now", "signup_success")
        return redirect("/")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()

        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("home"))

        flash("Invalid credentials", "login_error")
    return render_template("login.html")



@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

#Create a Model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(100), nullable=False)
    amt = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Expense({self.desc},{self.amt},{self.category},{self.date})"



@app.route('/',methods=["POST","GET"])
@login_required
def home():
    total_amount = session.pop("total_amount", 0)
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    sum_all=0
    for expense in expenses:
            sum_all+=expense.amt
    #spending by category
    category_data = (
        db.session.query(Expense.category, func.sum(Expense.amt)) \
    .filter(Expense.user_id == current_user.id)
        .group_by(Expense.category)
        .all()
    )

    category_labels = [c[0] for c in category_data]
    category_values = [float(c[1]) for c in category_data]
    #spending by time
    time_data = (
        db.session.query(Expense.date, func.sum(Expense.amt)) \
    .filter(Expense.user_id == current_user.id)
        .group_by(Expense.date)
        .order_by(Expense.date)
        .all()
    )

    time_labels = [t[0].strftime("%Y-%m-%d") for t in time_data]
    time_values = [float(t[1]) for t in time_data]

    return render_template("index.html", 
                           expenses=expenses[-5:][::-1], 
                           total_amount=total_amount,
                           sum_all=sum_all,
                           category_labels=category_labels,
                           category_values=category_values,
                           time_labels=time_labels,
                           time_values=time_values)  

@app.route('/filter-expense',methods=['POST'])
def filter():
    if request.method=="POST":       
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        print(expenses)
        start_date=request.form.get("startdate")
        end_date=request.form.get("enddate")
        category=request.form.get("category")
        print(start_date,end_date,category)
        filtered_expenses=expenses
        if start_date:
            start_date_obj=datetime.strptime(start_date,"%Y-%m-%d").date()
            filtered_expenses=[expense for expense in filtered_expenses if expense.date>=start_date_obj]
        if end_date:
            end_date_obj=datetime.strptime(end_date,"%Y-%m-%d").date()
            filtered_expenses=[expense for expense in filtered_expenses if expense.date<=end_date_obj]
        if category:
            filtered_expenses=[expense for expense in filtered_expenses if expense.category==category]    
        total_amount=0
        for expense in filtered_expenses:
            total_amount+=expense.amt
        print(total_amount)
        session['total_amount']=total_amount
        session["filtered_expenses"] = [
    {
        "desc": e.desc,
        "amt": e.amt,
        "category": e.category,
        "date": e.date.strftime("%Y-%m-%d")
    }
    for e in filtered_expenses
]
    return redirect(url_for('home'))

@app.route("/export-csv",methods=["GET"])
def export_csv():
    # example: filtered_expenses = [(desc, amt, category, date), ...]
    # filtered_expenses = get_filtered_expenses()  # however you compute it
    filtered_expenses = session.pop('filtered_expenses',[])

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Description", "Amount", "Category", "Date"])

    for e in filtered_expenses:
        writer.writerow([e["desc"], e["amt"], e["category"], e["date"]])


    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=expenses.csv"}
    )
    return "downloaded"
@app.route("/add-expense",methods=["POST"])
def add_expense():
    data=request.form
    if request.method=="POST":
        with app.app_context():
            new_expense = Expense(
                desc=data["desc"],
                amt=data["amt"],
                category=data["category"],
                date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
                user_id=current_user.id
            )
            db.session.add(new_expense)
            db.session.commit()
    return redirect("/")

@app.route("/delete-expense/<int:expense_id>",methods=["DELETE"])
def delete_expense(expense_id):
    with app.app_context():
        expense_to_delete = Expense.query.filter_by(
            id=expense_id,
            user_id=current_user.id
        ).first_or_404()

        db.session.delete(expense_to_delete)
        db.session.commit()
    return redirect("/")



if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0",port=5000)

