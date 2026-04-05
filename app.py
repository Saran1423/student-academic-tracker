from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- BASE PATH ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- DATA FUNCTIONS ----------
def load_data():
    file_path = os.path.join(BASE_DIR, "data.json")
    if not os.path.exists(file_path):
        return {"tasks": []}
    try:
        with open(file_path) as f:
            return json.load(f)
    except:
        return {"tasks": []}

def save_data(data):
    file_path = os.path.join(BASE_DIR, "data.json")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def load_users():
    file_path = os.path.join(BASE_DIR, "users.json")
    if not os.path.exists(file_path):
        return {"users": []}
    try:
        with open(file_path) as f:
            return json.load(f)
    except:
        return {"users": []}

def save_users(data):
    file_path = os.path.join(BASE_DIR, "users.json")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# ---------- ROUTES ----------

# HOME
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    data = load_data()
    return render_template("index.html", tasks=data["tasks"], user=session["user"])


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()

        for u in users["users"]:
            if u["username"] == request.form["username"] and u["password"] == request.form["password"]:
                session["user"] = u["username"]
                return redirect("/")

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()

        # check duplicate user
        for u in users["users"]:
            if u["username"] == request.form["username"]:
                return render_template("register.html", error="User already exists")

        users["users"].append({
            "username": request.form["username"],
            "password": request.form["password"]
        })

        save_users(users)
        return redirect("/login")

    return render_template("register.html")


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ADD TASK
@app.route("/add", methods=["POST"])
def add():
    if "user" not in session:
        return redirect("/login")

    data = load_data()

    new_task = {
        "id": len(data["tasks"]) + 1,
        "subject": request.form["subject"],
        "title": request.form["title"],
        "type": request.form["type"],
        "date": request.form["date"],
        "status": "Pending"
    }

    data["tasks"].append(new_task)
    save_data(data)

    return redirect("/")


# COMPLETE TASK
@app.route("/complete/<int:id>")
def complete(id):
    data = load_data()

    for t in data["tasks"]:
        if t["id"] == id:
            t["status"] = "Completed"

    save_data(data)
    return redirect("/")


# DELETE TASK
@app.route("/delete/<int:id>")
def delete(id):
    data = load_data()

    data["tasks"] = [t for t in data["tasks"] if t["id"] != id]

    save_data(data)
    return redirect("/")


# FILTER BY DATE
@app.route("/filter", methods=["POST"])
def filter():
    data = load_data()
    date = request.form["date"]

    filtered = [t for t in data["tasks"] if t["date"] == date]

    return render_template("index.html", tasks=filtered, user=session["user"])


# SETTINGS PAGE
@app.route("/settings")
def settings():
    if "user" not in session:
        return redirect("/login")

    return render_template("settings.html", user=session["user"])


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
