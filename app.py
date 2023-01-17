from flask import Flask, render_template, request, redirect, url_for, session
from cs50 import SQL
from helpers import apology, login_required, post, view_section, compose_reply, direct_message
import os
from datetime import timedelta

db = SQL("sqlite:///forum.db")

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(weeks=2)
app.secret_key = "whyisthisathing"

section_ids = {"0" : ["General", "general"], "1" : ["Gaming", "gaming"], "2" : ["Homework Help", "homework-help"], "3" : ["CS50 Demo", "cs50"], "4" : ["Clean", "clean"]}

id_for_reply = 0
reply_post_id = 0
section = ""

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_comf = request.form.get("confirmation")

        check_dupes = db.execute(f"SELECT * FROM users WHERE username = '{username}'")
        print(check_dupes)

        if username == '':
            return apology("Please include a username.")

        elif len(check_dupes) == 1:
            return apology("Username already taken. ")

        if password == '':
            return apology("Please input a password")

        elif password == password_comf:
            db.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")

        else:
            return apology("Passwords Do Not Match")

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/general", methods=["GET", "POST"])
def general():
    global section
    section = "0"
    return view_section(section)

@app.route("/gaming", methods=["GET", "POST"])
def gaming():
    global section
    section = "1"
    return view_section(section)

@app.route("/homework-help", methods=["GET", "POST"])
def homeworkhelp():
    global section
    section = "2"
    return view_section(section)
    #return post("me", 0, "thread", "hello world", 0, "hello lmao")

@app.route("/cs50", methods=["GET", "POST"])
def cs50():
    global section
    section = "3"
    return view_section(section)

@app.route("/clean", methods=["GET", "POST"])
def clean():
    global section
    section = "4"
    return view_section(section)

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    session.permanent = True

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("Must provide username")

        elif not request.form.get("password"):
            return apology("Must provide password")

        username = request.form.get("username")
        password = request.form.get("password")
        check_dupes = db.execute(f"SELECT * FROM users WHERE username = '{username}'")

        if len(check_dupes) != 1:
            return apology("Invalid username. ")

        if password != check_dupes[0]["password"]:
            return apology("Wrong Password!")

        session["user_id"] = check_dupes[0]["id"]
        session["username"] = username

        print(f"username: {session.get('user_id')}")

        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/viewpost", methods=["GET", "POST"])
def view_post():
    posts = db.execute("SELECT * FROM threads")
    button = request.form.to_dict()
    print(button)
    for entry in posts:
        print(entry["id"])
        post_id = entry["post_id"]
        print(post_id)
        print(list(button)[0])
        if entry["id"] == int(list(button)[0]):
            info = db.execute(f"SELECT * FROM posts WHERE id = {post_id}")
            info[0]["username"] = db.execute(f"SELECT username FROM users WHERE id = {info[0]['user_id']}")[0]["username"]
            info[0]["title"] = entry["title"]
            print(f"INFO \n \n \n{info} \n \n \n")
            replies = db.execute(f"SELECT * FROM replies WHERE thread_id = {entry['id']}")
            print(f" {session}")

            for reply in replies:
                print(reply)
                reply["content"] = db.execute(f"SELECT content FROM posts WHERE id = {reply['post_id']}")[0]['content']
                reply["username"] = db.execute(f"SELECT username FROM users WHERE id IN (SELECT user_id FROM posts WHERE id = {reply['post_id']})")[0]['username']
                print(reply)

    return render_template("post.html", info=info[0], replies=replies, sect = section_ids[info[0]["section_id"]])

@app.route("/compose", methods=["GET", "POST"])
@login_required
def compose():
    if request.method == "POST":
        id = session.get("user_id")
        username = session.get("username")
        title = request.form.get("title")
        print(title)
        content = request.form.get("content")
        print(content)

        try:
            if content.strip() == "":
                return apology("Add Content")

            if title.strip() == "":
                return apology("You need a title")

        except AttributeError:
            return render_template("compose.html")

        return post(username, section, "thread", content, 0, title)
    else:
        return render_template("compose.html")

@app.route("/reply", methods=["GET", "POST"])
@login_required
def reply():
    global id_for_reply, reply_post_id
    if request.method == "POST":
        key_check = request.form.to_dict()
        print(key_check)
        key_check = list(key_check.keys())
        print("ASd78orsd")
        print(key_check)
        try:
            id_for_reply = int(key_check[0])
            reply_post_id = int(db.execute(f"SELECT id FROM threads WHERE post_id = {id_for_reply}")[0]["id"])
            print(key_check)
            return compose_reply(reply_post_id, section)

        except:
            pass

        print(key_check)
        return compose_reply(reply_post_id, section)

    else:
        return render_template("reply.html")

@app.route("/message", methods=["GET", "POST"])
@login_required
def message():
    if request.method == "POST":
        sender = session.get("user_id")
        receiver = request.form.get("receiver")
        valid = db.execute(f"SELECT * FROM users WHERE username = '{receiver}'")
        print(valid)
        if len(valid) == 0:
            return apology("Invalid User!")
        receiver = db.execute(f"SELECT id FROM users WHERE username = '{receiver}'")[0]["id"]
        title = request.form.get("title")
        content = request.form.get("content")

        valid = db.execute(f"SELECT * FROM users WHERE id = '{receiver}'")
        print(valid)
        if len(valid) == 0:
            return apology("Invalid User!")

        return direct_message(sender, receiver, content, "message", title)

    else:
        return render_template("message.html")