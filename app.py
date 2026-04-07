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

    # Create file if not exists
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump({"tasks": []}, f)

    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except:
        return {"tasks": []}


def save_data(data):
    file_path = os.path.join(BASE_DIR, "data.json")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def load_users():
    file_path = os.path.join(BASE_DIR, "users.json")

    # Create file if not exists
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump({"users": []}, f)

    try:
        with open(file_path, "r") as f:
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
    return render_template("index.html", tasks=data.get("tasks", []), user=session["user"])


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()

        for u in users.get("users", []):
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

        for u in users.get("users", []):
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

    # Ensure "tasks" key exists
    if "tasks" not in data:
        data["tasks"] = []

    new_task = {
        "id": len(data["tasks"]) + 1,
        "subject": request.form.get("subject", ""),
        "title": request.form.get("title", ""),
        "type": request.form.get("type", ""),
        "date": request.form.get("date", ""),
        "status": "Pending"
    }

    data["tasks"].append(new_task)

    save_data(data)

    return redirect("/")


# COMPLETE TASK
@app.route("/complete/<int:id>")
def complete(id):
    data = load_data()

    for t in data.get("tasks", []):
        if t["id"] == id:
            t["status"] = "Completed"

    save_data(data)
    return redirect("/")


# DELETE TASK
@app.route("/delete/<int:id>")
def delete(id):
    data = load_data()

    data["tasks"] = [t for t in data.get("tasks", []) if t["id"] != id]

    save_data(data)
    return redirect("/")


# FILTER BY DATE
@app.route("/filter", methods=["POST"])
def filter():
    if "user" not in session:
        return redirect("/login")

    data = load_data()
    date = request.form.get("date", "")

    filtered = [t for t in data.get("tasks", []) if t["date"] == date]

    return render_template("index.html", tasks=filtered, user=session["user"])


# SETTINGS
@app.route("/settings")
def settings():
    if "user" not in session:
        return redirect("/login")

    return render_template("settings.html", user=session["user"])


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
