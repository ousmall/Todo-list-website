from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from datetime import date
from email_info import SMTP_SERVER, SMTP_PORT, MY_EMAIL, MY_PASS
import smtplib

# show the year in footer
year = date.today().year

app = Flask(__name__)
app.config['SECRET_KEY'] = ""


# create database
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo_list.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# table for store data of todo_list
class TodoList(db.Model):
    __tablename__ = 'todo_list'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    schedule = db.Column(String, nullable=False)


def send_email(firstname, lastname, email, message):
    try:
        email_message = (f"Subject: A message comes from Todo-list Website!\n\n"
                         f"You got a message:\n"
                         f"From {firstname} {lastname}, Email:{email} \n"
                         f"For details:\n"
                         f"{message}")

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=MY_PASS)
            connection.sendmail(from_addr=MY_EMAIL,
                                to_addrs=MY_EMAIL,
                                msg=email_message)
            print(f"The message was sent.")
    except smtplib.SMTPServerDisconnected:
        print("ERROR: Could not connect to the SMTP server. "
              "Make sure the SMTP_LOGIN and SMTP_PASS credentials have been set correctly.")


@app.route('/')
def show_list():
    result = db.session.execute(db.select(TodoList))
    lists = result.scalars().all()
    return render_template("index.html", all_lists=lists, current_year=year)


@app.route("/add", methods=["POST"])
def add_list():
    if request.method == "POST":
        content = request.form['content']
        schedule = request.form['schedule']
        new_list = TodoList(content=content, schedule=schedule)
        db.session.add(new_list)
        db.session.commit()
    return redirect(url_for("show_list"))


@app.route("/delete/<int:list_id>")
def delete_plan(list_id):
    plan_to_delete = db.get_or_404(TodoList, list_id)
    db.session.delete(plan_to_delete)
    db.session.commit()
    return redirect(url_for('show_list'))


@app.route("/delete/all")
def delete_all():
    db.session.query(TodoList).delete()
    db.session.commit()
    return redirect(url_for('show_list'))


@app.route("/contact", methods=["POST"])
def contact():
    if request.method == "POST":
        firstname = request.form['firstname'],
        lastname = request.form['lastname'],
        email = request.form['email'],
        message = request.form['message']
        send_email(firstname, lastname, email, message)
        if send_email:
            flash('Successfully sent your message!')
            return redirect(url_for('contact'))
        else:
            flash('Unable to send email, please try again later')

    return render_template("contact.html", current_year=year)


if __name__ == '__main__':
    app.run(debug=True)
