import os
from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind = engine))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/users')
def users():
    users = db.execute("SELECT * FROM userss").fetchall()
    return render_template("users.html", users=users)

@app.route('/profile', methods=["POST"])
def profile():
    id =  int(request.form.get("id"))
    user = db.execute("SELECT * FROM userss WHERE id = :id",{"id":id}).fetchone()
    users = db.execute("SELECT * FROM userss").fetchall()
    return render_template("profile.html", user = user, users = users)

@app.route('/transactions', methods=["POST"])
def transactions():
    transferid = int(request.form.get("transferer_id"))
    receiverid = int(request.form.get("receiver_id"))
    creditamount = int(request.form.get("credit"))
    r = db.execute("SELECT name FROM userss WHERE id = :id", {"id": receiverid}).fetchone()
    c = db.execute("SELECT name, credit FROM userss WHERE id = :id", {"id": transferid}).fetchone()
    creditlimit = c.credit

    if(creditamount>creditlimit):
        return render_template("error.html")
    db.execute("UPDATE userss SET credit=credit - :d WHERE id = :id", {"id": transferid, "d": creditamount})
    db.execute("UPDATE userss SET credit=credit + :d WHERE id = :id", {"id": receiverid, "d": creditamount})
    db.commit()

    db.execute("INSERT INTO transactions (sender, receiver, creditamount) VALUES (:sender, :receiver, :creditamount)",{"sender": c.name, "receiver": r.name, "creditamount": creditamount})
    db.commit()

    return render_template("success.html",sender=c.name, receiver=r.name, credit = creditamount)

@app.route('/transactions_list')
def transactions_list():
    list = db.execute("SELECT * FROM transactions").fetchall()
    return render_template("transactions.html", list=list)
