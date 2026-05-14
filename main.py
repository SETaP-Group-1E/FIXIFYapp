#pip install flask flask-sqlalchemy flask-wtf python-dotenv

#To open db
#Press Ctrl+Shift+P
#Type SQLite: New Query and select it

import os
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from forms import RegForm, LoginForm
from sqlalchemy import text
from werkzeug.utils import secure_filename

# Expanded: session stores the selected user role for this demo app.
app = Flask(__name__)
app.config["SECRET_KEY"] = "0bd24ce2ce9d0ac49fea3f26561cc7fa4fe296ef22964a68594b489c804d4f3a"
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
DEFAULT_DATABASE_URI = os.environ.get("FIXIFY_DATABASE_URI", "sqlite:///jobs.db")
app.config["SQLALCHEMY_DATABASE_URI"] = DEFAULT_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)

def create_app(testing=False):
    if testing:
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app

# Added: database job model is now part of main.py.
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default="")
    location = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    urgency = db.Column(db.String(20), nullable=False)
    timing_window = db.Column(db.String(50), default="Not specified")
    budget = db.Column(db.Float)
    is_negotiable = db.Column(db.Boolean, default=False)
    photo_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default="pending")


# Added: database bid model for contractor offers.
class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    bid_id = db.Column(db.Integer, nullable=False)
    contractor_id = db.Column(db.Integer, nullable=False)
    contractor_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float)
    amount = db.Column(db.Float, nullable=False)
    timeline = db.Column(db.String(100), nullable=False)
    explanation = db.Column(db.Text, default="")
    status = db.Column(db.String(30), default="Pending")
    clarification_response = db.Column(db.Text, default="")
    homeowner_completed = db.Column(db.Boolean, default=False)
    contractor_completed = db.Column(db.Boolean, default=False)
    completion_status = db.Column(db.String(30), default="Job not completed")
    created_at = db.Column(db.DateTime, default=datetime.now)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), default="")
    phone = db.Column(db.String(40), default="")
    bio = db.Column(db.Text, default="")
    specialty = db.Column(db.String(100), default="")
    portfolio = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


# Added: database review model is now part of main.py.
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    bid_id = db.Column(db.Integer)
    contractor_id = db.Column(db.Integer)
    homeowner_id = db.Column(db.Integer)
    reviewer_type = db.Column(db.String(20), nullable=False)
    quality_rating = db.Column(db.Integer)
    punctuality_rating = db.Column(db.Integer)
    communication_rating = db.Column(db.Integer)
    overall_rating = db.Column(db.Integer)
    comment = db.Column(db.String(500))
    photo_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)

    @property
    def can_edit(self):
        # Kept: reviews can only be edited for a short period after posting.
        if self.created_at is None:
            return False
        return datetime.now() - self.created_at < timedelta(minutes=1)


@app.before_request
def create_tables():
    # Added: keep the SQLite tables available when the merged app starts.
    if not should_use_database():
        return
    ensure_database_schema()


@app.route("/")
@app.route("/home")
def home():
    # Expanded: reset the role when returning to the public home page.
    session.pop("role", None)
    session.pop("contractor_id", None)
    return render_template("home.html")


@app.route("/login/<role>")
def login_as(role):
    # Added: simple role selection for the coursework demo.
    if role not in ("homeowner", "contractor"):
        flash("Please choose either homeowner or contractor.", "danger")
        return redirect(url_for("home"))

    session["role"] = role

    if role == "homeowner":
        session.pop("contractor_id", None)
        if profile_needs_setup("homeowner"):
            return redirect(url_for("setup_profile", role="homeowner"))
        return redirect(url_for("homeowner_dashboard"))

    session["contractor_id"] = DEFAULT_CONTRACTOR_ID
    if profile_needs_setup("contractor"):
        return redirect(url_for("setup_profile", role="contractor"))

    # Added: send contractors straight to clarification requests when needed.
    if contractor_has_open_clarification(DEFAULT_CONTRACTOR_ID):
        return redirect(url_for("contractor_bids"))

    return redirect(url_for("contractor_dashboard"))


@app.route("/logout")
def logout():
    # Expanded: clear the selected demo role.
    session.pop("role", None)
    session.pop("contractor_id", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# Kept: contractor sample profiles are still used by bidding and profiles.
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
DEFAULT_HOMEOWNER_ID = 1
DEFAULT_CONTRACTOR_ID = 1
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
VALID_JOB_CATEGORIES = {"Plumbing", "Electrical", "Cleaning", "Gardening"}
VALID_JOB_URGENCIES = {"High", "Medium", "Low"}


def next_job_id():
    # Added: keep ids unique even after jobs are deleted.
    return max((job["id"] for job in all_jobs), default=0) + 1


def allowed_file(filename):
    # Added: only allow common image uploads.
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_photo(photo, prefix):
    # Added: shared upload helper for job and review photos.
    if not photo or not photo.filename or not allowed_file(photo.filename):
        return None

    safe_filename = secure_filename(photo.filename)
    photo_filename = f"{prefix}_{safe_filename}"
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    photo.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))
    return photo_filename


def validate_job_form():
    # Shared validation for posting and editing service jobs.
    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()
    category = request.form.get("category")
    custom_category = request.form.get("custom_category", "").strip()
    urgency = request.form.get("urgency")
    location = (request.form.get("location") or "").strip()
    budget = (request.form.get("budget_amount") or "").strip()
    negotiable = request.form.get("is_negotiable")

    if not title:
        flash("Please enter a job title.", "danger")
        return None
    if len(title) > 100:
        flash("Job title is too long.", "danger")
        return None
    if len(description) > 1000:
        flash("Description is too long.", "danger")
        return None

    if category == "Other" and custom_category:
        category = custom_category
    elif not category:
        flash("Please select a category.", "danger")
        return None
    elif category not in VALID_JOB_CATEGORIES:
        flash("Invalid category.", "danger")
        return None

    if not urgency:
        flash("Please select an urgency.", "danger")
        return None
    if urgency not in VALID_JOB_URGENCIES:
        flash("Invalid urgency.", "danger")
        return None

    if not location:
        flash("Please enter a location.", "danger")
        return None
    if len(location) > 100:
        flash("Location is too long.", "danger")
        return None

    if budget:
        try:
            budget_value = float(budget)
        except ValueError:
            flash("Budget must be a valid positive number.", "danger")
            return None
        if budget_value <= 0:
            flash("Budget must be a valid positive number.", "danger")
            return None

    if negotiable in ("yes", "true", "on"):
        is_negotiable = True
    elif negotiable in ("no", "false", None, ""):
        is_negotiable = False
    else:
        flash("Invalid negotiable value.", "danger")
        return None

    return {
        "title": title,
        "description": description,
        "category": category,
        "urgency": urgency,
        "location": location,
        "budget": budget if budget else "Open",
        "is_negotiable": is_negotiable,
    }


def should_use_database():
    # Added: tests can avoid writing to the real jobs.db file.
    return not (app.config.get("TESTING") and app.config["SQLALCHEMY_DATABASE_URI"] == DEFAULT_DATABASE_URI)


def ensure_database_schema():
    # Added: upgrade older SQLite tables without deleting existing data.
    db.create_all()

    table_columns = {
        "job": {
            "description": "TEXT DEFAULT ''",
            "timing_window": "VARCHAR(50) DEFAULT 'Not specified'",
            "budget": "FLOAT",
            "is_negotiable": "BOOLEAN DEFAULT 0",
            "photo_filename": "VARCHAR(255)",
            "created_at": "DATETIME",
            "status": "VARCHAR(20) DEFAULT 'pending'",
        },
        "bid": {
            "job_id": "INTEGER",
            "bid_id": "INTEGER",
            "contractor_id": "INTEGER",
            "contractor_name": "VARCHAR(100)",
            "rating": "FLOAT",
            "amount": "FLOAT",
            "timeline": "VARCHAR(100)",
            "explanation": "TEXT DEFAULT ''",
            "status": "VARCHAR(30) DEFAULT 'Pending'",
            "clarification_response": "TEXT DEFAULT ''",
            "homeowner_completed": "BOOLEAN DEFAULT 0",
            "contractor_completed": "BOOLEAN DEFAULT 0",
            "completion_status": "VARCHAR(30) DEFAULT 'Job not completed'",
            "created_at": "DATETIME",
        },
        "review": {
            "bid_id": "INTEGER",
            "contractor_id": "INTEGER",
            "homeowner_id": "INTEGER",
            "quality_rating": "INTEGER",
            "punctuality_rating": "INTEGER",
            "communication_rating": "INTEGER",
            "overall_rating": "INTEGER",
            "comment": "VARCHAR(500)",
            "photo_filename": "VARCHAR(255)",
            "created_at": "DATETIME",
        },
        "profile": {
            "role": "VARCHAR(20)",
            "user_id": "INTEGER",
            "display_name": "VARCHAR(100)",
            "location": "VARCHAR(100) DEFAULT ''",
            "phone": "VARCHAR(40) DEFAULT ''",
            "bio": "TEXT DEFAULT ''",
            "specialty": "VARCHAR(100) DEFAULT ''",
            "portfolio": "TEXT DEFAULT ''",
            "created_at": "DATETIME",
            "updated_at": "DATETIME",
        },
    }

    for table_name, expected_columns in table_columns.items():
        existing_columns = {
            row[1] for row in db.session.execute(text(f"PRAGMA table_info({table_name})"))
        }

        for column_name, column_sql in expected_columns.items():
            if column_name not in existing_columns:
                db.session.execute(
                    text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}")
                )

    db.session.commit()


def profile_user_id(role):
    # Keep demo profiles tied to the selected role.
    if role == "contractor":
        return session.get("contractor_id", DEFAULT_CONTRACTOR_ID)
    return DEFAULT_HOMEOWNER_ID


def default_profile(role, user_id=None):
    # Safe fallback when the profile has not been created yet.
    user_id = user_id or (DEFAULT_CONTRACTOR_ID if role == "contractor" else DEFAULT_HOMEOWNER_ID)

    if role == "contractor":
        contractor = contractors.get(user_id, contractors[DEFAULT_CONTRACTOR_ID])
        return {
            "role": "contractor",
            "user_id": contractor["id"],
            "display_name": contractor["name"],
            "location": "Portsmouth",
            "phone": "07890 123456",
            "bio": contractor["bio"],
            "specialty": contractor["specialty"],
            "portfolio": "Kitchen sink repair\nBathroom pipe replacement\nEmergency leak repair",
        }

    return {
        "role": "homeowner",
        "user_id": DEFAULT_HOMEOWNER_ID,
        "display_name": "Fixify Homeowner",
        "location": "Portsmouth",
        "phone": "",
        "bio": "Posts home service jobs and reviews completed work on Fixify.",
        "specialty": "",
        "portfolio": "",
    }


def load_profile(role, user_id=None):
    if not should_use_database():
        return None

    return Profile.query.filter_by(
        role=role,
        user_id=user_id or profile_user_id(role),
    ).first()


def get_profile(role, user_id=None):
    # Return a DB profile when it exists, otherwise show sensible defaults.
    profile = load_profile(role, user_id)
    return profile or default_profile(role, user_id)


def profile_needs_setup(role):
    # Real app users create a profile before entering their dashboard.
    return should_use_database() and load_profile(role) is None


def role_dashboard_endpoint(role):
    return "contractor_dashboard" if role == "contractor" else "homeowner_dashboard"


def sync_contractor_profile(profile):
    # Keep bids using the latest contractor profile details.
    if not profile or profile.role != "contractor":
        return

    contractor = contractors.setdefault(profile.user_id, {
        "id": profile.user_id,
        "rating": 4.8,
        "name": profile.display_name,
        "specialty": profile.specialty or "General Repairs",
        "bio": profile.bio or "",
    })
    contractor["name"] = profile.display_name
    contractor["specialty"] = profile.specialty or contractor.get("specialty", "General Repairs")
    contractor["bio"] = profile.bio or contractor.get("bio", "")


def portfolio_items_for(profile):
    if not profile:
        return []

    portfolio_text = profile.get("portfolio", "") if isinstance(profile, dict) else profile.portfolio
    return [item.strip() for item in portfolio_text.splitlines() if item.strip()]


def review_score(review):
    if review.reviewer_type == "homeowner":
        ratings = [
            review.quality_rating,
            review.punctuality_rating,
            review.communication_rating,
        ]
    else:
        ratings = [review.overall_rating]

    ratings = [rating for rating in ratings if rating is not None]
    return round(sum(ratings) / len(ratings), 1) if ratings else None


def average_review_score(reviews):
    scores = [score for score in (review_score(review) for review in reviews) if score is not None]
    return round(sum(scores) / len(scores), 1) if scores else None


def get_profile_reviews(role, user_id):
    if not should_use_database():
        return []

    query = Review.query.order_by(Review.created_at.desc())
    if role == "contractor":
        return query.filter_by(contractor_id=user_id, reviewer_type="homeowner").all()

    return query.filter_by(homeowner_id=user_id, reviewer_type="provider").all()


def budget_to_float(value):
    # Added: convert the bidding budget text into a DB-friendly number.
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def sync_job_to_db(job, status=None):
    # Added: keep a database copy of jobs created in the bidding workflow.
    if not should_use_database():
        return None

    db_job = db.session.get(Job, job["id"]) or Job(id=job["id"])
    db_job.title = job["title"]
    db_job.description = job.get("description", "")
    db_job.location = job.get("location") or "Not specified"
    db_job.category = job.get("category") or "Other"
    db_job.urgency = job.get("urgency") or "Medium"
    db_job.timing_window = job.get("timing_window") or job.get("urgency") or "Not specified"
    db_job.budget = budget_to_float(job.get("budget"))
    db_job.is_negotiable = bool(job.get("is_negotiable"))
    db_job.photo_filename = job.get("photo_filename")
    db_job.status = status or job.get("status", "pending")
    db.session.add(db_job)
    db.session.commit()
    return db_job


def delete_job_from_db(job_id):
    # Added: remove the database copy when a homeowner deletes a job.
    if not should_use_database():
        return

    db_job = db.session.get(Job, job_id)
    if db_job:
        Bid.query.filter_by(job_id=job_id).delete()
        Review.query.filter_by(job_id=job_id).delete()
        db.session.delete(db_job)
        db.session.commit()


def get_bid_from_db(job_id, bid_id):
    # Added: read a persisted contractor bid from the bid table.
    if not should_use_database():
        return None

    return Bid.query.filter_by(job_id=job_id, bid_id=bid_id).first()


def sync_bid_to_db(job, bid):
    # Added: save contractor bids into the bid table.
    if not should_use_database():
        return None

    homeowner_completed = bool(bid.get("homeowner_completed", False))
    contractor_completed = bool(bid.get("contractor_completed", False))
    sync_job_to_db(
        job,
        status="completed" if homeowner_completed and contractor_completed else job.get("status", "pending"),
    )
    db_bid = get_bid_from_db(job["id"], bid["id"]) or Bid(job_id=job["id"], bid_id=bid["id"])

    db_bid.contractor_id = bid["contractor_id"]
    db_bid.contractor_name = bid["contractor_name"]
    db_bid.rating = bid.get("rating")
    db_bid.amount = bid["amount"]
    db_bid.timeline = bid["timeline"]
    db_bid.explanation = bid.get("explanation", "")
    db_bid.status = bid.get("status", "Pending")
    db_bid.clarification_response = bid.get("clarification_response", "")
    db_bid.homeowner_completed = homeowner_completed
    db_bid.contractor_completed = contractor_completed
    db_bid.completion_status = (
        "Completed" if homeowner_completed and contractor_completed
        else "Job not completed"
    )

    db.session.add(db_bid)
    db.session.commit()
    return db_bid


def save_review_to_db(job, reviewer_type, review_data, bid=None):
    # Added: save completed bidding reviews into the merged review table.
    if not should_use_database():
        return None

    sync_job_to_db(job, status="completed")
    review_query = Review.query.filter_by(job_id=job["id"], reviewer_type=reviewer_type)
    if bid is not None:
        review_query = review_query.filter_by(bid_id=bid.get("id"))

    review = review_query.first()
    if review is None:
        review = Review(job_id=job["id"], reviewer_type=reviewer_type)

    review.bid_id = bid.get("id") if bid is not None else review_data.get("bid_id")
    review.homeowner_id = review_data.get("homeowner_id", DEFAULT_HOMEOWNER_ID)
    review.contractor_id = (
        bid.get("contractor_id") if bid is not None
        else review_data.get("contractor_id", DEFAULT_CONTRACTOR_ID)
    )
    review.comment = review_data.get("comment", "")
    review.photo_filename = review_data.get("photo_filename")

    if reviewer_type == "homeowner":
        review.quality_rating = review_data.get("quality_rating")
        review.punctuality_rating = review_data.get("punctuality_rating")
        review.communication_rating = review_data.get("communication_rating")
    else:
        review.overall_rating = review_data.get("overall_rating")

    db.session.add(review)
    db.session.commit()
    return review


def get_review_from_db(job_id, reviewer_type, bid_id=None):
    # Added: read persisted reviews for bidding pages.
    if not should_use_database():
        return None

    review_query = Review.query.filter_by(job_id=job_id, reviewer_type=reviewer_type)
    if bid_id is not None:
        review_query = review_query.filter_by(bid_id=bid_id)

    return review_query.first()


def get_review_created_at(review):
    # Added: handle both database review objects and in-memory review dictionaries.
    if review is None:
        return None
    if isinstance(review, dict):
        return review.get("created_at")
    return getattr(review, "created_at", None)


def get_review_photo_filename(review):
    # Added: handle review photos from DB objects and in-memory dictionaries.
    if review is None:
        return None
    if isinstance(review, dict):
        return review.get("photo_filename")
    return getattr(review, "photo_filename", None)


def can_edit_review(review):
    # Added: reviews are only editable during the first minute.
    created_at = get_review_created_at(review)
    if created_at is None:
        return True
    return datetime.now() - created_at < timedelta(minutes=1)


def read_rating(field_name):
    # Keep review ratings inside the 1-to-5 star range.
    raw_rating = request.form.get(field_name)
    if raw_rating in (None, ""):
        flash("Rating must be given", "danger")
        return None

    try:
        rating = int(raw_rating)
    except ValueError:
        flash("Rating must be given", "danger")
        return None

    if rating < 1:
        flash("Rating cannot be under 1 star", "danger")
        return None
    if rating > 5:
        flash("Rating cannot be above 5 stars", "danger")
        return None

    return rating


def get_review_for_bid(job, bid, reviewer_type):
    # Added: show saved DB reviews, falling back to the current in-memory bid.
    return get_review_from_db(job["id"], reviewer_type, bid.get("id")) or bid.get("reviews", {}).get(reviewer_type)


def contractor_has_open_clarification(contractor_id):
    # Added: check if a contractor needs to clarify a bid.
    return any(
        bid["contractor_id"] == contractor_id and bid["status"] == "Clarification Requested"
        for job in all_jobs
        for bid in job["bids"]
    )


def find_job_and_bid(job_id, bid_id):
    # Added: shared lookup for bid actions, quick chat, completion, and reviews.
    job = next((j for j in all_jobs if j["id"] == job_id), None)
    if job is None:
        return None, None

    bid = next((b for b in job["bids"] if b["id"] == bid_id), None)
    return job, bid


def ensure_bid_completion_fields(bid):
    # Added: both sides must confirm before the job is complete.
    bid.setdefault("homeowner_completed", False)
    bid.setdefault("contractor_completed", False)
    bid["completion_status"] = (
        "Completed" if bid["homeowner_completed"] and bid["contractor_completed"]
        else "Job not completed"
    )
    return bid


def is_bid_completed(bid):
    # Added: reviews unlock only after both sides complete the job.
    ensure_bid_completion_fields(bid)
    return bid["homeowner_completed"] and bid["contractor_completed"]


def get_accepted_bid(job):
    # Added: return the accepted bid for a job, if one exists.
    bid = next((b for b in job["bids"] if b.get("status") == "Accepted"), None)
    if bid:
        ensure_bid_completion_fields(bid)
    return bid


def get_available_jobs():
    # Added: accepted jobs are no longer available for new bids.
    return [job for job in all_jobs if get_accepted_bid(job) is None]


def get_quick_chat_notifications(target_role, contractor_id=None):
    # Added: build unread quick-chat notifications for dashboards.
    notifications = []

    for job in all_jobs:
        for bid in job["bids"]:
            if bid.get("status") != "Accepted":
                continue

            if target_role == "contractor" and bid.get("contractor_id") != contractor_id:
                continue

            for message in bid.get("chat_messages", []):
                if message.get("unread_for") == target_role:
                    notifications.append({
                        "job_id": job["id"],
                        "bid_id": bid["id"],
                        "job_title": job["title"],
                        "sender": message["sender"],
                        "message": message["message"],
                    })

    return notifications


def mark_quick_chat_notifications_read(bid, target_role):
    # Added: opening quick chat clears unread messages for that role.
    for message in bid.get("chat_messages", []):
        if message.get("unread_for") == target_role:
            message["unread_for"] = None


@app.route("/homeowner-dashboard")
def homeowner_dashboard():
    # Added: homeowner view for posted jobs and bids.
    session["role"] = "homeowner"
    total_bids = sum(len(job["bids"]) for job in all_jobs)
    return render_template(
        "homeowner_dashboard.html",
        jobs=all_jobs,
        total_bids=total_bids,
        chat_notifications=get_quick_chat_notifications("homeowner"),
        get_accepted_bid=get_accepted_bid,
        is_bid_completed=is_bid_completed,
    )


@app.route("/contractor-dashboard")
def contractor_dashboard():
    # Added: contractor view for jobs still open to bids.
    session["role"] = "contractor"
    session.setdefault("contractor_id", DEFAULT_CONTRACTOR_ID)
    current_contractor = contractors.get(session["contractor_id"])
    return render_template(
        "bidding.html",
        title="Contractor Jobs",
        jobs=get_available_jobs(),
        current_contractor=current_contractor,
        chat_notifications=get_quick_chat_notifications("contractor", session["contractor_id"]),
    )


@app.route("/contractor-bids")
def contractor_bids():
    # Added: contractor view for submitted bids and accepted jobs.
    session["role"] = "contractor"
    session.setdefault("contractor_id", DEFAULT_CONTRACTOR_ID)
    contractor_id = session["contractor_id"]
    current_contractor = contractors.get(contractor_id)
    my_bids = []

    for job in all_jobs:
        for bid in job["bids"]:
            if bid["contractor_id"] == contractor_id and bid.get("status") != "Rejected":
                if bid["status"] == "Accepted":
                    ensure_bid_completion_fields(bid)
                my_bids.append({
                    "job": job,
                    "bid": bid,
                    "homeowner_review": get_review_for_bid(job, bid, "homeowner"),
                })

    accepted_jobs = [item for item in my_bids if item["bid"]["status"] == "Accepted"]
    other_bids = [item for item in my_bids if item["bid"]["status"] != "Accepted"]

    status_counts = {
        "Accepted": sum(1 for item in my_bids if item["bid"]["status"] == "Accepted"),
        "Rejected": sum(1 for item in my_bids if item["bid"]["status"] == "Rejected"),
        "Pending": sum(1 for item in my_bids if item["bid"]["status"] == "Pending"),
        "Clarification Requested": sum(
            1 for item in my_bids if item["bid"]["status"] == "Clarification Requested"
        ),
        "Clarification Provided": sum(
            1 for item in my_bids if item["bid"]["status"] == "Clarification Provided"
        ),
        "Completed": sum(1 for item in accepted_jobs if is_bid_completed(item["bid"])),
    }

    return render_template(
        "contractor_bids.html",
        current_contractor=current_contractor,
        accepted_jobs=accepted_jobs,
        other_bids=other_bids,
        status_counts=status_counts,
        chat_notifications=get_quick_chat_notifications("contractor", contractor_id),
        is_bid_completed=is_bid_completed,
    )


@app.route("/profile")
def my_profile():
    role = session.get("role")
    if role not in ("homeowner", "contractor"):
        flash("Please choose a role first.", "warning")
        return redirect(url_for("home"))

    if profile_needs_setup(role):
        return redirect(url_for("setup_profile", role=role))

    if role == "contractor":
        return redirect(url_for("contractor_profile", contractor_id=profile_user_id("contractor")))

    return redirect(url_for("homeowner_profile", homeowner_id=DEFAULT_HOMEOWNER_ID))


@app.route("/profile/setup/<role>", methods=["GET", "POST"])
def setup_profile(role):
    # Create or edit the selected demo role profile.
    if role not in ("homeowner", "contractor"):
        flash("Please choose either homeowner or contractor.", "danger")
        return redirect(url_for("home"))

    session["role"] = role
    if role == "contractor":
        session.setdefault("contractor_id", DEFAULT_CONTRACTOR_ID)
    else:
        session.pop("contractor_id", None)

    user_id = profile_user_id(role)
    existing_profile = load_profile(role, user_id)

    if request.method == "POST":
        display_name = request.form.get("display_name", "").strip()
        location = request.form.get("location", "").strip()
        phone = request.form.get("phone", "").strip()
        bio = request.form.get("bio", "").strip()
        specialty = request.form.get("specialty", "").strip()
        portfolio = request.form.get("portfolio", "").strip()

        if not display_name:
            flash("Please enter your profile name.", "danger")
            return redirect(url_for("setup_profile", role=role))

        if role == "contractor" and not specialty:
            flash("Please enter your contractor specialty.", "danger")
            return redirect(url_for("setup_profile", role=role))

        if not should_use_database():
            flash("Profile saved for this demo session.", "success")
            return redirect(url_for(role_dashboard_endpoint(role)))

        profile = existing_profile or Profile(role=role, user_id=user_id)
        profile.display_name = display_name
        profile.location = location
        profile.phone = phone
        profile.bio = bio
        profile.specialty = specialty if role == "contractor" else ""
        profile.portfolio = portfolio if role == "contractor" else ""
        profile.updated_at = datetime.now()

        db.session.add(profile)
        db.session.commit()
        sync_contractor_profile(profile)
        flash("Profile saved successfully.", "success")
        return redirect(url_for(role_dashboard_endpoint(role)))

    return render_template(
        "profile_setup.html",
        role=role,
        profile=existing_profile or default_profile(role, user_id),
        dashboard_url=url_for(role_dashboard_endpoint(role)),
    )


@app.route("/submit-clarification", methods=["POST"])
def submit_clarification():
    # Added: contractor replies to a homeowner clarification request.
    session["role"] = "contractor"
    session.setdefault("contractor_id", DEFAULT_CONTRACTOR_ID)
    contractor_id = session["contractor_id"]
    job_id = request.form.get("job_id", type=int)
    bid_id = request.form.get("bid_id", type=int)
    clarification_response = request.form.get("clarification_response", "").strip()

    if not clarification_response:
        flash("Please enter a clarification message.", "danger")
        return redirect(url_for("contractor_bids"))

    job = next((j for j in all_jobs if j["id"] == job_id), None)

    if job is None:
        flash("Job not found!", "danger")
        return redirect(url_for("contractor_bids"))

    bid = next((b for b in job["bids"] if b["id"] == bid_id), None)

    if bid is None:
        flash("Bid not found!", "danger")
        return redirect(url_for("contractor_bids"))

    if bid["contractor_id"] != contractor_id:
        flash("You can only clarify your own bids.", "danger")
        return redirect(url_for("contractor_bids"))

    bid["clarification_response"] = clarification_response
    bid["status"] = "Clarification Provided"
    sync_bid_to_db(job, bid)
    job["notifications"].append(
        f"Clarification provided by {bid['contractor_name']} for bid #{bid['id']}"
    )
    flash("Clarification sent to the homeowner.", "success")
    return redirect(url_for("contractor_bids"))


@app.route("/quick-chat/<int:job_id>/<int:bid_id>", methods=["GET", "POST"])
def quick_chat(job_id, bid_id):
    # Added: quick chat is available after a bid is accepted.
    job, bid = find_job_and_bid(job_id, bid_id)

    if job is None:
        flash("Job not found!", "danger")
        return redirect(url_for("home"))

    if bid is None:
        flash("Bid not found!", "danger")
        return redirect(url_for("home"))

    if bid["status"] != "Accepted":
        flash("Quick chat is only available after a bid is accepted.", "warning")
        return redirect(url_for("view_job_bids", job_id=job_id))

    bid.setdefault("chat_messages", [])

    if request.method == "POST":
        message = request.form.get("message", "").strip()

        if not message:
            flash("Please enter a message.", "danger")
            return redirect(url_for("quick_chat", job_id=job_id, bid_id=bid_id))

        role = session.get("role")
        sender = "Homeowner" if role == "homeowner" else bid["contractor_name"]
        # Added: keep the message unread for the opposite side.
        unread_for = "contractor" if role == "homeowner" else "homeowner"
        bid["chat_messages"].append({
            "sender": sender,
            "message": message,
            "unread_for": unread_for,
        })
        flash("Message sent.", "success")
        return redirect(url_for("quick_chat", job_id=job_id, bid_id=bid_id))

    role = session.get("role")
    if role in ("homeowner", "contractor"):
        mark_quick_chat_notifications_read(bid, role)

    return render_template("chat.html", job=job, bid=bid)


@app.route("/post", methods=['GET', 'POST'])
def post():
    if session.get("role") is None:
        flash("Please choose homeowner first.", "danger")
        return redirect(url_for("home"))

    if session.get("role") != "homeowner":
        flash("Only homeowners can post jobs.", "danger")
        return redirect(url_for("home"))

    if request.method == 'POST':
        job_data = validate_job_form()
        if job_data is None:
            return redirect(url_for('post'))

        recurring = request.form.get('recurring')
        recurring_frequency = request.form.get('recurring_frequency')
        if recurring == 'yes' and not recurring_frequency:
            flash("Please select how often the job should recur.", "danger")
            return redirect(url_for('post'))
        job_id = next_job_id()

        # Expanded: save uploaded job photos for contractor cards.
        photo_filename = save_uploaded_photo(request.files.get('photo'), f"job_{job_id}")

        new_job = {
            'id': job_id,
            'title': job_data["title"],
            'description': job_data["description"],
            'category': job_data["category"],
            'urgency': job_data["urgency"],
            'location': job_data["location"],
            'photo_filename': photo_filename,
            'budget': job_data["budget"],
            'is_negotiable': job_data["is_negotiable"],
            'recurring': True if recurring == 'yes' else False,
            'recurring_frequency': recurring_frequency,
            'bids': [],
            'notifications': []
        }

        all_jobs.append(new_job)
        sync_job_to_db(new_job)
        flash("Job posted successfully!", "success")
        return redirect(url_for('homeowner_dashboard'))

    return render_template('post.html', job=None)


@app.route("/job/<int:job_id>/edit", methods=["GET", "POST"])
def edit_job(job_id):
    # Added: homeowner edits a posted job.
    session["role"] = "homeowner"
    job = next((j for j in all_jobs if j["id"] == job_id), None)

    if job is None:
        flash("Job not found!", "danger")
        return redirect(url_for("homeowner_dashboard"))

    if request.method == "POST":
        job_data = validate_job_form()
        if job_data is None:
            return redirect(url_for("edit_job", job_id=job_id))

        job["title"] = job_data["title"]
        job["description"] = job_data["description"]
        job["budget"] = job_data["budget"]
        job["is_negotiable"] = job_data["is_negotiable"]
        job["category"] = job_data["category"]
        job["urgency"] = job_data["urgency"]
        job["location"] = job_data["location"]

        photo_filename = save_uploaded_photo(request.files.get("photo"), f"job_{job_id}")
        if photo_filename:
            job["photo_filename"] = photo_filename

        sync_job_to_db(job)
        flash("Job updated successfully.", "success")
        return redirect(url_for("homeowner_dashboard"))

    return render_template("post.html", job=job)


@app.route("/job/<int:job_id>/delete", methods=["POST"])
def delete_job(job_id):
    # Added: homeowner deletes a posted job.
    session["role"] = "homeowner"
    job = next((j for j in all_jobs if j["id"] == job_id), None)

    if job is None:
        flash("Job not found!", "danger")
        return redirect(url_for("homeowner_dashboard"))

    delete_job_from_db(job_id)
    all_jobs.remove(job)
    flash("Job deleted successfully.", "warning")
    return redirect(url_for("homeowner_dashboard"))


@app.route("/bidding")
def bidding():
    # Expanded: direct visits to bidding are treated as contractor mode.
    session["role"] = "contractor"
    session.setdefault("contractor_id", DEFAULT_CONTRACTOR_ID)
    current_contractor = contractors.get(session["contractor_id"])
    return render_template(
        'bidding.html',
        title='Job Bid',
        jobs=get_available_jobs(),
        current_contractor=current_contractor,
        chat_notifications=get_quick_chat_notifications("contractor", session["contractor_id"]),
    )


@app.route("/submit_bid", methods=['POST'])
def submit_bid():
    raw_id = request.form.get('job_id')
    # Expanded: logged-in contractors bid as themselves.
    contractor_id = session.get("contractor_id") or request.form.get('contractor_id')
    bid_amount = request.form.get('bid_amount')
    timeline = request.form.get('timeline')
    explanation = request.form.get('explanation', '')

    # Expanded: explanation is optional.
    if not all([raw_id, contractor_id, bid_amount, timeline]):
        flash("Please complete all bid fields.", "danger")
        return redirect(url_for('bidding'))

    # Expanded: validate numeric bid input before saving.
    try:
        job_id = int(raw_id)
        contractor_id = int(contractor_id)
        bid_value = float(bid_amount)
    except (TypeError, ValueError):
        flash("Bid amount must be a valid positive number.", "danger")
        return redirect(url_for('bidding'))

    if bid_value <= 0:
        flash("Bid amount must be a valid positive number.", "danger")
        return redirect(url_for('bidding'))

    # Expanded: handle missing jobs or contractors cleanly.
    job = next((j for j in all_jobs if j['id'] == job_id), None)

    if job is None:
        flash("Job not found.", "danger")
        return redirect(url_for('bidding'))

    contractor = contractors.get(contractor_id)

    if contractor:
        new_bid = {
            'id': len(job['bids']) + 1,
            'contractor_id': contractor['id'],
            'contractor_name': contractor['name'],
            'rating': contractor['rating'],
            'amount': bid_value,
            'timeline': timeline,
            'explanation': explanation,
            'status': 'Pending'
        }

        job['bids'].append(new_bid)
        job['notifications'].append(
            f"New bid received from {contractor['name']} for £{bid_value:.2f}"
        )
        sync_bid_to_db(job, new_bid)
        # Expanded: store bid notifications for the homeowner dashboard.
    else:
        flash("Contractor not found.", "danger")

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

    filtered_bids = [bid for bid in job['bids'] if bid.get('status') != 'Rejected']
    for bid in filtered_bids:
        if bid["status"] == "Accepted":
            ensure_bid_completion_fields(bid)

    if min_price is not None:
        filtered_bids = [b for b in filtered_bids if b['amount'] >= min_price]

    if max_price is not None:
        filtered_bids = [b for b in filtered_bids if b['amount'] <= max_price]

    if timeline:
        filtered_bids = [b for b in filtered_bids if timeline in b['timeline'].lower()]

    if min_rating is not None:
        filtered_bids = [b for b in filtered_bids if b['rating'] >= min_rating]

    return render_template(
        'view_bids.html',
        job=job,
        bids=filtered_bids,
        is_bid_completed=is_bid_completed,
    )


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
        # Expanded: accepting a bid opens quick chat.
        bid.setdefault('chat_messages', [])
        # Added: accepted jobs start as not completed.
        ensure_bid_completion_fields(bid)
        flash(f"Bid from {bid['contractor_name']} accepted.", "success")
    elif action == 'reject':
        bid['status'] = 'Rejected'
        flash(f"Bid from {bid['contractor_name']} rejected.", "warning")
    elif action == 'clarification':
        bid['status'] = 'Clarification Requested'
        # Expanded: clear old clarification text when asking again.
        bid['clarification_response'] = ''
        flash(f"Clarification requested from {bid['contractor_name']}.", "info")
    else:
        flash("Invalid action.", "danger")
        return redirect(url_for('view_job_bids', job_id=job_id))

    sync_bid_to_db(job, bid)
    return redirect(url_for('view_job_bids', job_id=job_id))


@app.route("/complete-job/<int:job_id>/<int:bid_id>", methods=["POST"])
def complete_job(job_id, bid_id):
    # Added: both sides must confirm completion before reviews unlock.
    job, bid = find_job_and_bid(job_id, bid_id)

    if job is None or bid is None:
        flash("Job or bid not found.", "danger")
        return redirect(url_for("home"))

    if bid["status"] != "Accepted":
        flash("Only accepted jobs can be marked as completed.", "warning")
        return redirect(url_for("view_job_bids", job_id=job_id))

    role = session.get("role")
    ensure_bid_completion_fields(bid)

    if role == "homeowner":
        bid["homeowner_completed"] = True
        redirect_target = url_for("homeowner_dashboard")
    elif role == "contractor":
        contractor_id = session.get("contractor_id", DEFAULT_CONTRACTOR_ID)
        if bid["contractor_id"] != contractor_id:
            flash("You can only complete your own accepted jobs.", "danger")
            return redirect(url_for("contractor_bids"))
        bid["contractor_completed"] = True
        redirect_target = url_for("contractor_bids")
    else:
        flash("Please choose homeowner or contractor first.", "danger")
        return redirect(url_for("home"))

    ensure_bid_completion_fields(bid)
    sync_bid_to_db(job, bid)
    if is_bid_completed(bid):
        sync_job_to_db(job, status="completed")
        flash("Job completed by both sides. Reviews are now available.", "success")
    else:
        sync_job_to_db(job)
        flash("Completion saved. Waiting for the other side to confirm.", "info")

    return redirect(redirect_target)


@app.route("/db-job/<int:job_id>", endpoint="view_job")
def view_db_job(job_id):
    # Kept: database job detail page for review compatibility.
    job = db.session.get(Job, job_id)
    if job is None:
        flash("Job not found.", "danger")
        return redirect(url_for("home"))

    homeowner_review = Review.query.filter_by(job_id=job_id, reviewer_type="homeowner").first()
    provider_review = Review.query.filter_by(job_id=job_id, reviewer_type="provider").first()
    return render_template(
        "job_detail.html",
        job=job,
        homeowner_review=homeowner_review,
        provider_review=provider_review,
    )


@app.route("/db-complete/<int:job_id>", endpoint="mark_complete")
def mark_db_complete(job_id):
    # Kept: database-only completion route.
    job = db.session.get(Job, job_id)
    if job is None:
        flash("Job not found.", "danger")
        return redirect(url_for("home"))

    job.status = "completed"
    db.session.commit()
    flash("Job marked as completed! You can now leave a review.", "success")
    return redirect(url_for("view_job", job_id=job_id))


@app.route("/review/<int:job_id>/<int:bid_id>", methods=["GET", "POST"])
def submit_review(job_id, bid_id):
    job, bid = find_job_and_bid(job_id, bid_id)

    if job is None or bid is None:
        flash("Job or bid not found.", "danger")
        return redirect(url_for("home"))

    if not is_bid_completed(bid):
        flash("Cannot review until homeowner and contractor both mark the job as completed.", "warning")
        return redirect(url_for("homeowner_dashboard"))

    role = session.get("role", "homeowner")
    if role == "contractor":
        contractor_id = session.get("contractor_id", DEFAULT_CONTRACTOR_ID)
        if bid["contractor_id"] != contractor_id:
            flash("You can only review your own completed jobs.", "danger")
            return redirect(url_for("contractor_bids"))
        is_homeowner = False
        reviewer_type = "provider"
        cancel_url = url_for("contractor_bids")
    else:
        is_homeowner = True
        reviewer_type = "homeowner"
        cancel_url = url_for("view_job_bids", job_id=job_id)

    bid.setdefault("reviews", {})
    db_review = get_review_from_db(job_id, reviewer_type, bid["id"])
    review = db_review or bid["reviews"].get(reviewer_type)

    if request.method == "POST":
        
        # 1. EDITING CHECKS (If a review already exists)
        if review:
            if not can_edit_review(review):
                flash("Review can only be edited within 1 minute of submission.", "warning")
                return redirect(cancel_url)
            
            # Check if it was already edited once
            if review.get("edit_count", 0) >= 1:
                flash("Review cannot be changed more than once", "danger")
                return redirect(cancel_url)
            
            # Check if any changes were actually made
            has_changes = False
            new_comment = request.form.get("comment", "")
            if new_comment != review.get("comment", ""):
                has_changes = True
                
            photo = request.files.get("photo")
            if photo and photo.filename:
                has_changes = True
                
            if is_homeowner:
                q = request.form.get("quality_rating")
                p = request.form.get("punctuality_rating")
                c = request.form.get("communication_rating")
                if str(q) != str(review.get("quality_rating")) or str(p) != str(review.get("punctuality_rating")) or str(c) != str(review.get("communication_rating")):
                    has_changes = True
            else:
                o = request.form.get("overall_rating")
                if str(o) != str(review.get("overall_rating")):
                    has_changes = True
                    
            if not has_changes:
                flash("Edit will not be posted.", "warning")
                return redirect(cancel_url)

        # 2. VALIDATE COMMENT
        comment = request.form.get("comment", "")
        if len(comment) > 500:
            flash("Comment cannot be over 500 characters", "danger")
            return redirect(request.url)

        # 3. VALIDATE IMAGE FORMAT
        photo = request.files.get("photo")
        if photo and photo.filename:
            if not allowed_file(photo.filename):
                flash("Error due to invalid format", "danger")
                return redirect(request.url)

        # 4. VALIDATE RATINGS
        try:
            if is_homeowner:
                q_rating = request.form.get("quality_rating")
                p_rating = request.form.get("punctuality_rating")
                c_rating = request.form.get("communication_rating")
                
                if not all([q_rating, p_rating, c_rating]):
                    flash("Rating must be given", "danger")
                    return redirect(request.url)
                    
                ratings = [int(q_rating), int(p_rating), int(c_rating)]
            else:
                o_rating = request.form.get("overall_rating")
                if not o_rating:
                    flash("Rating must be given", "danger")
                    return redirect(request.url)
                    
                ratings = [int(o_rating)]
                
        except ValueError:
            flash("Rating must be given", "danger")
            return redirect(request.url)

        # Check bounds
        for r in ratings:
            if r < 1:
                flash("Rating cannot be under 1 star", "danger")
                return redirect(request.url)
            if r > 5:
                flash("Rating cannot be above 5 stars", "danger")
                return redirect(request.url)

        # 5. SAVE EVERYTHING TO DB
        photo_filename = save_uploaded_photo(photo, f"review_{job_id}_{bid_id}_{reviewer_type}")
        
        review_data = {
            "reviewer_type": reviewer_type,
            "comment": comment,
            "photo_filename": photo_filename or get_review_photo_filename(review),
            "created_at": get_review_created_at(review) or datetime.now(),
            "homeowner_id": DEFAULT_HOMEOWNER_ID,
            "contractor_id": bid["contractor_id"],
            "bid_id": bid["id"],
            # Increase the edit count if it's an update!
            "edit_count": review.get("edit_count", 0) + 1 if review else 0 
        }

        if is_homeowner:
            review_data["quality_rating"] = ratings[0]
            review_data["punctuality_rating"] = ratings[1]
            review_data["communication_rating"] = ratings[2]
        else:
            review_data["overall_rating"] = ratings[0]

        bid["reviews"][reviewer_type] = review_data
        save_review_to_db(job, reviewer_type, review_data, bid)
        flash("Thank you for your review!", "success")
        return redirect(cancel_url)

    return render_template(
        "review.html",
        job=job,
        bid=bid,
        review=review,
        is_homeowner=is_homeowner,
        cancel_url=cancel_url,
    )

@app.route("/report-review/<int:review_id>")
def report_review(review_id):
    # Kept: database review report route.
    review = db.session.get(Review, review_id)
    if review is None:
        flash("Review not found.", "danger")
        return redirect(url_for("home"))

    flash("Review has been reported to administrators.", "warning")
    return redirect(url_for("view_job", job_id=review.job_id))


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    # Expanded: serve uploaded job and review photos.
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/contractor/<int:contractor_id>")
def contractor_profile(contractor_id):
    contractor = contractors.get(contractor_id)
    profile = load_profile("contractor", contractor_id)

    if contractor is None and profile is None:
        flash("Contractor profile not found.", "danger")
        return redirect(url_for('bidding'))

    if profile:
        sync_contractor_profile(profile)
        contractor = contractors.get(contractor_id)

    reviews = get_profile_reviews("contractor", contractor_id)
    return render_template(
        "contractor_profile.html",
        contractor=contractor,
        profile=profile or default_profile("contractor", contractor_id),
        reviews=reviews,
        average_rating=average_review_score(reviews),
        portfolio_items=portfolio_items_for(profile or default_profile("contractor", contractor_id)),
        review_score=review_score,
    )


@app.route("/homeowner/<int:homeowner_id>")
def homeowner_profile(homeowner_id):
    # Homeowner profile only shows homeowner details and contractor reviews.
    if homeowner_id != DEFAULT_HOMEOWNER_ID:
        flash("Homeowner profile not found.", "danger")
        return redirect(url_for("home"))

    profile = load_profile("homeowner", homeowner_id)
    if profile is None and profile_needs_setup("homeowner") and session.get("role") == "homeowner":
        return redirect(url_for("setup_profile", role="homeowner"))

    reviews = get_profile_reviews("homeowner", homeowner_id)
    return render_template(
        "homeowner_profile.html",
        profile=profile or default_profile("homeowner", homeowner_id),
        reviews=reviews,
        average_rating=average_review_score(reviews),
        review_score=review_score,
    )


@app.route("/login")
def login():
    # Kept: original login page route is still available.
    form = LoginForm()
    return render_template("login.html", title="Login", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    # Kept: original register page route is still available.
    form = RegForm()
    if form.validate_on_submit():
        return redirect(url_for("home"))
    return render_template("register.html", title="Register", form=form)


@app.route("/contractor")
def contractor():
    # Expanded: show the selected contractor profile.
    contractor_id = session.get("contractor_id", DEFAULT_CONTRACTOR_ID)
    return redirect(url_for("contractor_profile", contractor_id=contractor_id))


if __name__ == "__main__":
    app.run(debug=True)