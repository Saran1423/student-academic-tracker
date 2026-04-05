from flask import Flask, render_template, request, redirect, session
import json

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATA ----------
def load_data():
    with open("data.json") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

def load_users():
    with open("users.json") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

# ---------- ROUTES ----------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    data = load_data()
    return render_template("index.html", tasks=data["tasks"], user=session["user"])

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        users = load_users()
        for u in users["users"]:
            if u["username"] == request.form["username"] and u["password"] == request.form["password"]:
                session["user"] = u["username"]
                return redirect("/")
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
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

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/add", methods=["POST"])
def add():
    data = load_data()
    data["tasks"].append({
        "id": len(data["tasks"]) + 1,
        "subject": request.form["subject"],
        "title": request.form["title"],
        "type": request.form["type"],
        "date": request.form["date"],
        "status": "Pending"
    })
    save_data(data)
    return redirect("/")

@app.route("/complete/<int:id>")
def complete(id):
    data = load_data()
    for t in data["tasks"]:
        if t["id"] == id:
            t["status"] = "Completed"
    save_data(data)
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    data = load_data()
    data["tasks"] = [t for t in data["tasks"] if t["id"] != id]
    save_data(data)
    return redirect("/")

@app.route("/filter", methods=["POST"])
def filter():
    data = load_data()
    date = request.form["date"]
    filtered = [t for t in data["tasks"] if t["date"] == date]
    return render_template("index.html", tasks=filtered, user=session["user"])

@app.route("/settings")
def settings():
    return render_template("settings.html", user=session["user"])

if __name__ == "__main__":
    app.run(debug=True)