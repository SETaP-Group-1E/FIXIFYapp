import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app import app, db, Job, Review
from datetime import datetime, timedelta

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def create_completed_job():
    job = Job(
        title="Test Job",
        description="Desc",
        location="Loc",
        category="Cat",
        urgency="Urgent",
        timing_window="Anytime",
        budget=100,
        is_negotiable=True,
        status="completed"
    )
    db.session.add(job)
    db.session.commit()
    return job

def test_homeowner_review_creation(client):
    job = create_completed_job()
    data = {
        'quality_rating': 5,
        'punctuality_rating': 4,
        'communication_rating': 3,
        'comment': 'Great job!'
    }
    response = client.post(f'/review/{job.id}', data=data, follow_redirects=True)
    assert b'Thank you for your review!' in response.data
    review = Review.query.filter_by(job_id=job.id, reviewer_type='homeowner').first()
    assert review is not None
    assert review.quality_rating == 5

def test_provider_review_creation(client):
    job = create_completed_job()
    job.id = 2  # Even ID for provider
    db.session.commit()
    data = {
        'overall_rating': 4,
        'comment': 'Good homeowner.'
    }
    response = client.post('/review/2', data=data, follow_redirects=True)
    assert b'Thank you for your review!' in response.data
    review = Review.query.filter_by(job_id=2, reviewer_type='provider').first()
    assert review is not None
    assert review.overall_rating == 4

def test_duplicate_review_prevention(client):
    job = create_completed_job()
    data = {
        'quality_rating': 5,
        'punctuality_rating': 4,
        'communication_rating': 3,
        'comment': 'Great job!'
    }
    client.post(f'/review/{job.id}', data=data, follow_redirects=True)
    response = client.post(f'/review/{job.id}', data=data, follow_redirects=True)
    assert b'You have already reviewed this job.' in response.data

def test_edit_review_within_24_hours(client):
    job = create_completed_job()
    review = Review(
        job_id=job.id,
        reviewer_type='homeowner',
        quality_rating=3,
        punctuality_rating=3,
        communication_rating=3,
        comment='Initial',
        created_at=datetime.now() - timedelta(hours=1)
    )
    db.session.add(review)
    db.session.commit()
    data = {
        'quality_rating': 5,
        'punctuality_rating': 5,
        'communication_rating': 5,
        'comment': 'Edited'
    }
    response = client.post(f'/review/{job.id}?edit=true', data=data, follow_redirects=True)
    assert b'Review updated successfully!' in response.data
    updated_review = Review.query.get(review.id)
    assert updated_review.comment == 'Edited'

def test_edit_review_expired(client):
    job = create_completed_job()
    review = Review(
        job_id=job.id,
        reviewer_type='homeowner',
        quality_rating=3,
        punctuality_rating=3,
        communication_rating=3,
        comment='Initial',
        created_at=datetime.now() - timedelta(hours=25)
    )
    db.session.add(review)
    db.session.commit()
    data = {
        'quality_rating': 5,
        'punctuality_rating': 5,
        'communication_rating': 5,
        'comment': 'Edited'
    }
    response = client.post(f'/review/{job.id}?edit=true', data=data, follow_redirects=True)
    assert b'Review can only be edited within 24 hours' in response.data
