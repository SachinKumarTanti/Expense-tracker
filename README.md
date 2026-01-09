# 💰 Expense Tracker Web App (Flask)

A **secure, multi-user Expense Tracker** built with **Flask**, **SQLAlchemy**, and **Flask-Login**.
Each user can sign up, log in, and manage **only their own expenses**. The app supports expense analytics, filtering, and CSV export.

---

## 🚀 Features

* 🔐 User Authentication (Signup / Login / Logout)
* 👤 Per-user data isolation (each user sees only their expenses)
* ➕ Add & ❌ Delete expenses
* 📊 Expense analytics

  * Spending by **category**
  * Spending over **time**
* 🔎 Filter expenses by

  * Date range
  * Category
* 📥 Export filtered expenses as **CSV**
* 🌐 Cloud database support (Supabase / Neon / PostgreSQL)
* 🎨 Frontend built with **HTML + Tailwind CSS**

---

## 🛠 Tech Stack

**Backend**

* Flask
* Flask-SQLAlchemy
* Flask-Login
* Werkzeug (password hashing)

**Database**

* SQLite (development)
* PostgreSQL (Supabase / Neon – production)

**Frontend**

* HTML
* Tailwind CSS

---

## 📂 Project Structure

```
.
├── app.py
├── .env
├── requirements.txt
├── templates/
│   ├── login.html
│   ├── signup.html
│   └── index.html
└── README.md
```

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key
URI=postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DATABASE?sslmode=require
```

For local testing, you can use SQLite:

```env
URI=sqlite:///app.db
```

---

## 📦 Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/expense-tracker.git
cd expense-tracker
```

### 2️⃣ Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the app

```bash
python app.py
```

The app will be available at:

```
http://127.0.0.1:5000
```

---

## 🔐 Authentication Flow

* Users **sign up** with username & password
* Passwords are securely hashed
* User is automatically logged in after signup
* All expense routes are protected using `@login_required`

---

## 🧠 Data Model

### User

* `id`
* `username` (unique)
* `password` (hashed)

### Expense

* `id`
* `desc`
* `amt`
* `category`
* `date`
* `user_id` (foreign key → User)

This ensures **strict per-user data isolation**.

---

## 📤 CSV Export

Filtered expenses can be exported as a CSV file containing:

* Description
* Amount
* Category
* Date

---

## 🔒 Security Notes

* Session-based authentication
* Password hashing with Werkzeug
* Users cannot access or delete others’ expenses
* Ready for PostgreSQL Row-Level Security (RLS)

---

## 🌱 Future Enhancements

* Email-based authentication
* Password reset
* Monthly budgets
---

## 📜 License

This project is open-source and available under the **MIT License**.

---

## ⭐ Support

If you like this project, please consider giving it a **star ⭐** on GitHub!

---

**Built with ❤️ using Flask**
