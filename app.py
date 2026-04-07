from flask import Flask, render_template, request, redirect, session
import json, os, time

app = Flask(__name__)
app.secret_key = "secret123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

USERS_FILE = os.path.join(BASE_DIR, "users.json")
DATA_FILE = os.path.join(BASE_DIR, "data.json")


# ----------------------------
# INIT FILES
# ----------------------------
def init_files():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({"users": []}, f)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"tasks": []}, f)


init_files()


# ----------------------------
# LOAD / SAVE
# ----------------------------
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": []}


def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_tasks():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"tasks": []}


def save_tasks(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------
# ROUTES
# ----------------------------

# LOGIN PAGE
@app.route("/")
def index():
    return render_template("index.html")


# LOGIN
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    data = load_users()

    for user in data["users"]:
        if user["username"] == username and user["password"] == password:
            session["user"] = username
            session["name"] = user.get("name", username)  # fallback safety
            return redirect("/dashboard")

    return render_template("index.html", error="Invalid credentials")


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")

    data = load_users()

    for user in data["users"]:
        if user["username"] == username:
            return render_template("register.html", error="User already exists")

    data["users"].append({
        "name": name,
        "username": username,
        "password": password
    })

    save_users(data)
    return redirect("/")


# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    data = load_tasks()

    tasks = [t for t in data["tasks"] if t["user"] == session["user"]]

    return render_template(
        "dashboard.html",
        tasks=tasks,
        user=session.get("name")  # show name instead of username
    )


# ADD TASK
@app.route("/add", methods=["POST"])
def add_task():
    if "user" not in session:
        return redirect("/")

    subject = request.form.get("subject")
    title = request.form.get("title")
    type_ = request.form.get("type")
    date = request.form.get("date")

    if not title:
        return redirect("/dashboard")

    data = load_tasks()

    data["tasks"].append({
        "id": str(time.time()),
        "subject": subject,
        "title": title,
        "type": type_,
        "date": date,
        "status": "Pending",
        "user": session["user"]
    })

    save_tasks(data)

    return redirect("/dashboard")


# COMPLETE TASK
@app.route("/complete/<id>")
def complete(id):
    data = load_tasks()

    for t in data["tasks"]:
        if t["id"] == id:
            t["status"] = "Completed"

    save_tasks(data)
    return redirect("/dashboard")


# DELETE TASK
@app.route("/delete/<id>")
def delete(id):
    data = load_tasks()

    data["tasks"] = [t for t in data["tasks"] if t["id"] != id]

    save_tasks(data)
    return redirect("/dashboard")


# FILTER TASK
@app.route("/filter", methods=["POST"])
def filter_tasks():
    if "user" not in session:
        return redirect("/")

    date = request.form.get("date")

    data = load_tasks()

    tasks = [
        t for t in data["tasks"]
        if t["user"] == session["user"] and t["date"] == date
    ]

    return render_template(
        "dashboard.html",
        tasks=tasks,
        user=session.get("name")
    )


# SETTINGS
@app.route("/settings")
def settings():
    if "user" not in session:
        return redirect("/")
    return render_template("settings.html", user=session.get("name"))


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# RUN
if __name__ == "__main__":
    app.run(debug=True)