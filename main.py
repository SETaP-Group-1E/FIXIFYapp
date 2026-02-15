from flask import Flask, render_template, url_for, flash, redirect
from forms import RegForm, LoginForm
app = Flask(__name__)
app.config["SECRET_KEY"] = "0bd24ce2ce9d0ac49fea3f26561cc7fa4fe296ef22964a68594b489c804d4f3a"

posts = [
    {
        "name": "Connor Jackson",
        "title": "Test Post",
        "content": "This is some text",
        "date_posted": "15/02/2026"
    },
{
        "name": "John Doe",
        "title": "Test",
        "content": "Test",
        "date_posted": "15/02/2026"
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", posts=posts)

@app.route("/opentabs")
def tabs():
    return render_template("tabs.html", title="Open Tabs")

@app.route("/login")
def login():
    form = LoginForm()
    return render_template("login.html", title="Login", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegForm()
    if form.validate_on_submit():
        return redirect(url_for("home"))
    return render_template("register.html", title="Register", form=form)


if __name__ == "__main__":
    app.run(debug=True)