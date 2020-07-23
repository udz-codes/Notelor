import sqlite3
from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from tempfile import mkdtemp

from helpers import login_required

app = Flask(__name__)

database = sqlite3.connect("notelor.db", check_same_thread = False)
db = database.cursor()

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANANET"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/", methods = ["GET", "POST"])
@login_required
def main():

    if request.method == "POST":

        if not request.form.get("heading"):
            return render_template("apology.html", apology = "Heading field can not be empty")

        elif not request.form.get("note-text"):
            return render_template("apology.html", apology = "Notes body field can not be empty")

        else:

            heading = request.form.get("heading")
            text = request.form.get("note-text")

            db.execute("INSERT INTO notes(user_id, heading, text) VALUES (:user_id, :heading, :text)",
                {"user_id": session["user_id"], "heading": heading, "text": text })
            database.commit()

            return redirect("/")

    else:
        
        db.execute("SELECT * FROM notes WHERE user_id = :user_id ORDER BY date DESC", {"user_id": session["user_id"]})
        database.commit()

        notes = db.fetchall()

        return render_template("index.html", notes = notes)


@app.route("/delete", methods=["GET","POST"])
@login_required
def delete():

    if request.method == "POST":
        
        note_id = request.form.get("note_id")
        
        db.execute("DELETE FROM notes WHERE note_id = :note_id", {"note_id": note_id})
        database.commit()

        return redirect("/")
    else:
        return redirect("/")

@app.route("/update", methods=["GET","POST"])
@login_required
def update():

    if request.method == "POST":
        
        if not request.form.get("updateHeading"):
            return render_template("apology.html", apology = "Heading field can not be empty")
        
        elif not request.form.get("updateText"):
            return render_template("apology.html", apology = "Notes body field can not be empty")
        
        elif not request.form.get("note_id"):
            return render_template("apology.html", apology = "Unsuccessfull, try again.")

        else:

            upHead = request.form.get("updateHeading")
            upText = request.form.get("updateText")
            note_id = request.form.get("note_id")

            db.execute("UPDATE notes SET heading = :upHead, text = :upText WHERE note_id = :note_id AND user_id = :user_id",
                { "upHead": upHead, "upText": upText, "note_id": note_id ,"user_id": session["user_id"]} )
            database.commit()

            return redirect("/")

        db.execute("DELETE FROM notes WHERE note_id = :note_id", {"note_id": note_id})
        database.commit()

        return redirect("/")

@app.route("/register", methods = ["GET","POST"])
def register():

    if request.method == "GET":
        if session.get("user_id") is not None:
            return redirect("/")
        else:
            return render_template("register.html")
    
    elif request.method == "POST":

        if not request.form.get("username"):
            return render_template("apology.html", apology = "Username field can not be empty")

        elif not request.form.get("password"):
            return render_template("apology.html", apology = "Password field can not be empty")

        elif not request.form.get("confirmation"):
            return render_template("apology.html", apology = "Please confirm password")

        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("apology.html", apology = "Password and Confirmation password do not match")
        
        else:

            username = request.form.get("username")
            password = request.form.get("password")

            h = generate_password_hash(password)

            db.execute("SELECT * FROM users WHERE username = :user", {"user" : username})
            database.commit()

            rows = db.fetchall()

            if len(rows) == 0:
                db.execute("INSERT INTO users (username, hash) VALUES (:user, :hsh)", {"user": username, "hsh": h})
                return redirect("/login")
            else:
                return render_template("apology.html", apology = "User may already exist.")


@app.route("/login", methods = ["GET","POST"])
def login():

    if request.method == "GET":
        if session.get("user_id") is not None:
            return redirect("/")
        else:
            return render_template("login.html")

    elif request.method == "POST":
        if not request.form.get("username"):
            return render_template("apology.html", apology = "Username field can not be empty")
        
        elif not request.form.get("password"):
            return render_template("apology.html", apology = "Password field can not be empty")

        else:

            db.execute("SELECT * FROM users WHERE username = :user", {"user" : request.form.get("username")})
            database.commit()

            rows = db.fetchall()

            # print(rows)

            if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
                return render_template("apology.html", apology = "Invalid username or password")
            
            else:
                session["user_id"] = rows[0][1]
                return redirect("/")

@app.route("/logout")
@login_required
def logout():
    
    session.clear()

    return redirect("/")


if __name__ == "__main__":
    app.run()