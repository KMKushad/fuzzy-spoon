from flask import redirect, render_template, request, session
from functools import wraps
from cs50 import SQL
from sqlite3 import *
import os
import datetime

section_ids = {"0" : ["General", "general"], "1" : ["Gaming", "gaming"], "2" : ["Homework Help", "homework-help"], "3" : ["CS50 Demo", "cs50"]}

db = SQL("sqlite:///forum.db")

def login_required(f):

    # From https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/, was also used in CS50.

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def apology(message, code=400):
    """Render message as an apology to user. Was also used in CS50."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def post(username, section, type, content, thread_id = 0, title = 0):
    user_id = db.execute(f"SELECT id FROM users WHERE username LIKE '{username}'")[0]["id"]
    print(user_id)
    db.execute(f"INSERT INTO posts (user_id, section_id, positives, negatives, type, content) VALUES ({user_id}, {section}, 0, 0, '{type}', '{content}')")
    post_id = db.execute("SELECT id FROM posts ORDER BY id DESC LIMIT 1")[0]["id"]
    if type == "thread":
        db.execute(f"INSERT INTO threads (post_id, replies, title) VALUES ({post_id}, 0, '{title}')")
        thread = db.execute("SELECT id FROM threads ORDER BY id DESC LIMIT 1")
        reply_num = db.execute(f"SELECT COUNT(id) FROM replies WHERE thread_id IN (SELECT id FROM threads WHERE post_id = {post_id})")
        info = db.execute(f"SELECT * FROM posts WHERE id = {post_id}")
        info[0]["username"] = db.execute(f"SELECT username FROM users WHERE id = {info[0]['user_id']}")[0]["username"]
        info[0]["title"] = title
        print(info)
        return render_template("post.html", info=info[0], sect = section_ids[section])

    else:
        db.execute(f"INSERT INTO replies (post_id, thread_id) VALUES ({post_id}, {thread_id})")
        thread_post_id = db.execute(f"SELECT post_id FROM threads WHERE id = {thread_id}")
        print("adgsdfgseadaefe7wfg7wef \n\n\n")
        print(thread_post_id)
        info = db.execute(f"SELECT * FROM posts WHERE id = {thread_post_id[0]['post_id']}")
        print(info)
        info[0]["username"] = db.execute(f"SELECT username FROM users WHERE id = {info[0]['user_id']}")[0]["username"]
        info[0]["title"] = db.execute(f"SELECT title FROM threads WHERE id = {thread_id}")[0]["title"]
        print(info)
        replies = db.execute(f"SELECT * FROM replies WHERE thread_id = {thread_id}")

        for reply in replies:
                print(reply)
                reply["content"] = db.execute(f"SELECT content FROM posts WHERE id = {reply['post_id']}")[0]['content']
                reply["username"] = db.execute(f"SELECT username FROM users WHERE id IN (SELECT user_id FROM posts WHERE id = {reply['post_id']})")[0]['username']
                print(reply)

        return render_template("post.html", info=info[0], replies=replies, sect = section_ids[section])

def view_section(section_id):
    posts = db.execute(f"SELECT * FROM threads WHERE post_id IN (SELECT id FROM posts WHERE section_id = {section_id}) ORDER BY id DESC")
    for row in posts:
        row["username"] = db.execute(f"SELECT username FROM users WHERE id IN (SELECT user_id FROM posts WHERE id IN (SELECT post_id FROM threads WHERE id = {int(row['id'])}))")[0]["username"]
        row["title"] = db.execute(f"SELECT title FROM threads WHERE id = '{int(row['''id'''])}'")
        row["time"] = db.execute(f"SELECT timestamp FROM posts WHERE id IN ({int(row['post_id'])})")[0]['timestamp']
        time_convert = int(row["time"][12])
        day = int(row["time"][9])
        new_time = []
        if time_convert < 4:
            time_convert = 24 - 4 + time_convert
            day = day - 1

        else:
            time_convert = time_convert - 4

        for i in range(len(row["time"])):
            if i == 12 and time_convert > 9:
                new_time[11] = time_convert // 10
                new_time.append(str(time_convert % (new_time[11] * 10)))

            elif i == 12:
                new_time.append(str(time_convert))

            elif i == 9:
                new_time.append(str(day))

            else:
                new_time.append(row["time"][i])

        print(new_time)
        row["time"] = f"{new_time[0]}{new_time[1]}{new_time[2]}{new_time[3]}{new_time[4]}{new_time[5]}{new_time[6]}{new_time[7]}{new_time[8]}{new_time[9]}{new_time[10]}{new_time[11]}{new_time[12]}{new_time[13]}{new_time[14]}{new_time[15]}{new_time[16]}{new_time[17]}{new_time[18]}"
    return render_template("threads.html", posts=posts)

def compose_reply(post_id, section):
    username = session.get("username")
    print(username)
    username = session.get("username")
    print(username)
    content = request.form.get("content")
    print(content)
    try:
        if content.strip() == "":
            return apology("Add Content")

    except AttributeError:
        return render_template("reply.html")

    reply_num = db.execute(f"SELECT replies FROM threads WHERE id = {post_id}")[0]["replies"]
    print(reply_num)
    db.execute(f"UPDATE threads SET replies = {reply_num + 1} WHERE id = {post_id}")

    return post(username, section, "reply", content, post_id, "I HATE THIS STUPID FUNCTION WHY IS IT LIKE THIS THIS IS FILLER")

def direct_message(sender, receiver, content, type, title = "", msg_id = 0):
    if type == "message":
        db.execute(f"INSERT INTO posts (user_id, section_id, type, content) VALUES ({sender}, 'dm', 'thread', '{content}')")
        post_id = db.execute("SELECT id FROM posts ORDER BY id DESC LIMIT 1")[0]["id"]
        db.execute(f"INSERT INTO threads (replies, title, post_id) VALUES (0, '{title}', {post_id})")
        db.execute(f"INSERT INTO dms (sender, receiver, post_id) VALUES ({sender}, {receiver}, {post_id})")
        info = db.execute(f"SELECT * FROM posts WHERE id = {post_id}")
        info[0]["username"] = db.execute(f"SELECT username FROM users WHERE id = {sender}")
        info[0]["title"] = title

        return render_template("post.html", info = info, sect = ["Home", ""])

    return render_template("post.html")
