#pip install flask flask-sqlalchemy flask-wtf python-dotenv

#To open db
#Press Ctrl+Shift+P
#Type SQLite: New Query and select it

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Path handling for Windows
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    urgency = db.Column(db.String(20), nullable=False)
    timing_window = db.Column(db.String(50), nullable=False)
    budget = db.Column(db.Float) 
    is_negotiable = db.Column(db.Boolean, default=False) 
    photo_filename = db.Column(db.String(255))  
    created_at = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='pending') 

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    reviewer_type = db.Column(db.String(20), nullable=False)  # 'homeowner' or 'provider'
    quality_rating = db.Column(db.Integer)  # 1-5 stars
    punctuality_rating = db.Column(db.Integer)  # 1-5 stars  
    communication_rating = db.Column(db.Integer)  # 1-5 stars
    overall_rating = db.Column(db.Integer)  # For provider-to-homeowner rating
    comment = db.Column(db.String(500))
    photo_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)

@app.before_request
def create_tables():
    # Don't delete database on every start - just create if needed
    db.create_all()

@app.route('/')
def index():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('index.html', jobs=jobs)

@app.route('/post', methods=['GET', 'POST'])
def post_job():
    job = None
    job_id = request.args.get('job_id')
    
    # If we're editing an existing job, load it
    if job_id:
        job = Job.query.get_or_404(job_id)
    
    if request.method == 'POST':
        # Handle file upload
        photo_filename = None
        if 'photo' in request.files and request.files['photo'].filename != '':
            file = request.files['photo']
            if file and allowed_file(file.filename):
                # Secure the filename and save it
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                photo_filename = filename
                print(f"✅ Saved photo to: {file_path}")
        
        # Process budget fields
        budget = None
        is_negotiable = False
        
        if request.form.get('budget_amount'):
            try:
                budget = float(request.form['budget_amount'])
            except (ValueError, TypeError):
                pass
                
        if request.form.get('is_negotiable') == 'yes':
            is_negotiable = True
        
        # Check if we're creating a new job or updating an existing one
        if 'job_id' in request.form and request.form['job_id']:
            # Update existing job
            job_id = request.form['job_id']
            job = Job.query.get_or_404(job_id)
            
            # Update fields
            job.title = request.form['title']
            job.description = request.form['description']
            job.location = request.form['location']
            job.category = request.form['category']
            job.urgency = request.form['urgency']
            job.timing_window = request.form['timing_window']
            job.budget = budget
            job.is_negotiable = is_negotiable
            
            # Handle new photo upload (keep old if none provided)
            if photo_filename:
                # Remove old photo if it exists
                if job.photo_filename:
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], job.photo_filename))
                    except:
                        pass
                job.photo_filename = photo_filename
                
            db.session.commit()
            print(f"✅ Job updated: {job_id}")
        else:
            # Create new job
            new_job = Job(
                title=request.form['title'],
                description=request.form['description'],
                location=request.form['location'],
                category=request.form['category'],
                urgency=request.form['urgency'],
                timing_window=request.form['timing_window'],
                budget=budget,
                is_negotiable=is_negotiable,
                photo_filename=photo_filename
            )
            db.session.add(new_job)
            db.session.commit()
            print(f"✅ Job posted with budget: ${budget} (negotiable: {is_negotiable})")
            
        return redirect(url_for('index'))
    
    return render_template('post.html', job=job)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_job(id):
    job = Job.query.get_or_404(id)
    # Delete the associated photo file if it exists
    if job.photo_filename:
        try:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], job.photo_filename)
            print(f"🗑️ Deleting photo: {file_path}")
            os.remove(file_path)
        except Exception as e:
            print(f"❌ Error deleting photo: {e}")
    db.session.delete(job)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    # view detailed logs
    app.logger.setLevel("DEBUG")
    print(f"📁 Upload folder path: {app.config['UPLOAD_FOLDER']}")
    app.run(debug=True)

