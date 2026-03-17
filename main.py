from flask import Flask, render_template, request, redirect, url_for, flash
from forms import RegForm, LoginForm
app = Flask(__name__)
app.config["SECRET_KEY"] = "0bd24ce2ce9d0ac49fea3f26561cc7fa4fe296ef22964a68594b489c804d4f3a"

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

all_jobs = []
@app.route("/post", methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        budget = request.form.get('budget_amount')
        negotiable = request.form.get('is_negotiable')

        new_job = {
            'id': len(all_jobs) + 1,
            'title': title,
            'description': description,
            'budget': budget if budget else "Open",
            'is_negotiable': True if negotiable == 'yes' else False,
            'bids': []
        }
        
        all_jobs.append(new_job)
        flash("Job posted successfully!", "success")
        return redirect(url_for('bidding'))

    return render_template('post.html', job=None)

@app.route("/bidding")
def bidding():
    return render_template('bidding.html', title='Job Bid', jobs=all_jobs)

@app.route("/submit_bid", methods=['POST'])
def submit_bid():
    raw_id = request.form.get('job_id')
    bid_amount = request.form.get('bid_amount')
    
    if raw_id:
        job_id = int(raw_id)
        for job in all_jobs:
            if job['id'] == job_id:
                job['bids'].append(bid_amount)
                flash(f"Bid of ${bid_amount} sent!", "success")
                break
    return redirect(url_for('bidding'))

@app.route("/job/<int:job_id>")
def view_job_bids(job_id):
    job = next((j for j in all_jobs if j['id'] == job_id), None)
    
    if job is None:
        flash("Job not found!", "danger")
        return redirect(url_for('bidding'))
        
    return render_template('view_bids.html', job=job)

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


@app.route("/contractor")
def contractor():
    return render_template("contractor_profile.html")

if __name__ == "__main__":
    app.run(debug=True)