from flask import Flask, render_template, request, redirect, url_for, flash
from forms import RegForm, LoginForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "0bd24ce2ce9d0ac49fea3f26561cc7fa4fe296ef22964a68594b489c804d4f3a"


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


contractors = {
    1: {
        "id": 1,
        "name": "John Smith",
        "rating": 4.8,
        "specialty": "Plumbing",
        "bio": "Experienced plumber with 8 years of residential work."
    },
    2: {
        "id": 2,
        "name": "Sarah Ahmed",
        "rating": 4.5,
        "specialty": "Electrical",
        "bio": "Certified electrician specialising in household repairs."
    },
    3: {
        "id": 3,
        "name": "Michael Brown",
        "rating": 4.2,
        "specialty": "Painting",
        "bio": "Professional painter focused on interior and exterior work."
    }
}

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
            'bids': [],
            'notifications': []
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
    contractor_id = request.form.get('contractor_id')
    bid_amount = request.form.get('bid_amount')
    timeline = request.form.get('timeline')
    explanation = request.form.get('explanation')

    if not all([raw_id, contractor_id, bid_amount, timeline, explanation]):
        flash("Please complete all bid fields.", "danger")
        return redirect(url_for('bidding'))

    job_id = int(raw_id)
    contractor_id = int(contractor_id)

    for job in all_jobs:
        if job['id'] == job_id:
            contractor = contractors.get(contractor_id)

            if contractor:
                new_bid = {
                    'id': len(job['bids']) + 1,
                    'contractor_id': contractor['id'],
                    'contractor_name': contractor['name'],
                    'rating': contractor['rating'],
                    'amount': float(bid_amount),
                    'timeline': timeline,
                    'explanation': explanation,
                    'status': 'Pending'
                }

                job['bids'].append(new_bid)
                job['notifications'].append(
                    f"New bid received from {contractor['name']} for £{bid_amount}"
                )
                flash(f"Bid from {contractor['name']} submitted successfully!", "success")
            else:
                flash("Contractor not found.", "danger")
            break

    return redirect(url_for('bidding'))


@app.route("/job/<int:job_id>")
def view_job_bids(job_id):
    job = next((j for j in all_jobs if j['id'] == job_id), None)

    if job is None:
        flash("Job not found!", "danger")
        return redirect(url_for('bidding'))

    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    timeline = request.args.get('timeline', '').strip().lower()
    min_rating = request.args.get('min_rating', type=float)

    filtered_bids = job['bids']

    if min_price is not None:
        filtered_bids = [b for b in filtered_bids if b['amount'] >= min_price]

    if max_price is not None:
        filtered_bids = [b for b in filtered_bids if b['amount'] <= max_price]

    if timeline:
        filtered_bids = [b for b in filtered_bids if timeline in b['timeline'].lower()]

    if min_rating is not None:
        filtered_bids = [b for b in filtered_bids if b['rating'] >= min_rating]

    return render_template('view_bids.html', job=job, bids=filtered_bids)


@app.route("/update_bid_status", methods=['POST'])
def update_bid_status():
    job_id = request.form.get('job_id', type=int)
    bid_id = request.form.get('bid_id', type=int)
    action = request.form.get('action')

    job = next((j for j in all_jobs if j['id'] == job_id), None)

    if job is None:
        flash("Job not found!", "danger")
        return redirect(url_for('bidding'))

    bid = next((b for b in job['bids'] if b['id'] == bid_id), None)

    if bid is None:
        flash("Bid not found!", "danger")
        return redirect(url_for('view_job_bids', job_id=job_id))

    if action == 'accept':
        bid['status'] = 'Accepted'
        flash(f"Bid from {bid['contractor_name']} accepted.", "success")
    elif action == 'reject':
        bid['status'] = 'Rejected'
        flash(f"Bid from {bid['contractor_name']} rejected.", "warning")
    elif action == 'clarification':
        bid['status'] = 'Clarification Requested'
        flash(f"Clarification requested from {bid['contractor_name']}.", "info")
    else:
        flash("Invalid action.", "danger")

    return redirect(url_for('view_job_bids', job_id=job_id))


@app.route("/contractor/<int:contractor_id>")
def contractor_profile(contractor_id):
    contractor = contractors.get(contractor_id)

    if contractor is None:
        flash("Contractor profile not found.", "danger")
        return redirect(url_for('bidding'))

    return render_template("contractor_profile.html", contractor=contractor)


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