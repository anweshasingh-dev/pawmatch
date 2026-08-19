import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import hashlib
from detector import AnimalDetector
from database import create_user, verify_user, save_report, update_report_status, get_db_connection
from matcher import find_matches_for_report
from embeddings import extract_image_vector
from geocoding import get_coordinates
from notifications import send_match_notification

app = Flask(__name__)
app.secret_key = "pawmatch_super_secret_key"
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

detector = AnimalDetector(confidence=0.25)

# Helper function to ensure active session user exists in database
def get_validated_user_id():
    user_id = session.get('user', {}).get('id')
    if not user_id:
        return None
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cursor.fetchone():
                session.pop('user', None)  # Wipe stale session
                return None
    return user_id

# 1. Serve Uploaded Files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 2. Home Feed
@app.route('/')
def index():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM reports ORDER BY id DESC")
            raw_reports = cursor.fetchall()
            
            reports = []
            for r in raw_reports:
                data = dict(r)
                # Safely extract filename on backend
                data['filename'] = os.path.basename(data.get('image_path', ''))
                reports.append(data)
                
    return render_template('index.html', reports=reports)

# 3. Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = verify_user(request.form['email'], request.form['password'])
        if user:
            session['user'] = user
            flash('Successfully logged in!', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if create_user(request.form['name'], request.form['email'], request.form['password']):
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        flash('Email is already registered.', 'error')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

# 4. Report Submission
@app.route('/report/<report_type>', methods=['GET', 'POST'])
def report_pet(report_type):
    report_type = report_type.upper()
    if request.method == 'POST':
        file = request.files.get('image')
        if not file or file.filename == '':
            flash('Please upload an image.', 'error')
            return redirect(request.url)

        # Save image
        filename = secure_filename(f"{report_type.lower()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Generate hash of image to prevent duplicate DB submissions
        with open(filepath, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        # Check for duplicate image in DB
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM reports WHERE image_path LIKE %s LIMIT 1", (f"%{filename}",))
                existing_report = cursor.fetchone()
                if existing_report:
                    flash('A report with this image already exists!', 'info')
                    return redirect(url_for('view_matches', report_id=existing_report['id']))

        # Process image with YOLO
        image = Image.open(filepath).convert("RGB")
        detection = detector.detect(image)

        user_species = request.form.get('species', '').strip().lower()
        detected_species = detection.get('species', 'unknown').lower()

        # Prioritize YOLO detection over manual user selection
        if detected_species in ['dog', 'cat']:
            final_species = detected_species
        else:
            final_species = user_species if user_species else 'unknown'

        # Extract ResNet 128-d vector embedding
        vector = extract_image_vector(filepath)

        # Geocode location
        address_text = request.form.get('address', '')
        lat, lon = get_coordinates(address_text)

        # Retrieve & validate session user ID against Database
        user_id = get_validated_user_id()

        report_data = {
            "user_id": user_id,
            "type": report_type,
            "species": final_species,
            "pet_name": request.form.get('pet_name'),
            "breed": request.form.get('breed'),
            "color": request.form.get('color'),
            "distinctive_marks": request.form.get('distinctive_marks'),
            "contact_name": request.form.get('contact_name'),
            "contact_phone": request.form.get('contact_phone'),
            "contact_email": request.form.get('contact_email'),
            "address": address_text,
            "latitude": lat,
            "longitude": lon,
            "event_date": request.form.get('event_date', str(datetime.now().date())),
            "description": request.form.get('description'),
            "image_path": filepath,
            "image_vector": vector
        }

        report_id = save_report(report_data)
        matches = find_matches_for_report(report_id)

        # Send notification for high-confidence matches
        if matches and matches[0].get('match_score', 0) >= 75:
            top_match = matches[0]
            match_url = url_for('view_matches', report_id=report_id, _external=True)
            send_match_notification(
                user_email=report_data.get('contact_email'),
                pet_name=report_data.get('pet_name'),
                score=top_match['match_score'],
                match_url=match_url
            )

        flash(f'Report #{report_id} successfully created!', 'success')
        return redirect(url_for('view_matches', report_id=report_id))

    return render_template('report_form.html', report_type=report_type)

# 5. Matching Results View
@app.route('/matches/<int:report_id>')
def view_matches(report_id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM reports WHERE id = %s", (report_id,))
            target = cursor.fetchone()

    if not target:
        flash('Report not found.', 'error')
        return redirect(url_for('index'))

    matches = find_matches_for_report(report_id)
    return render_template('matches.html', target=dict(target), matches=matches)

# 6. User Dashboard & Status Management
@app.route('/my-reports')
def my_reports():
    user_id = get_validated_user_id()
    if not user_id:
        flash('Please log in to view your reports.', 'error')
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM reports WHERE user_id = %s ORDER BY id DESC", (user_id,))
            reports = [dict(r) for r in cursor.fetchall()]

    return render_template('my_reports.html', reports=reports)

@app.route('/resolve/<int:report_id>', methods=['POST'])
def resolve_report(report_id):
    user_id = get_validated_user_id()
    if user_id:
        update_report_status(report_id, 'RESOLVED')
        flash(f'Report #{report_id} marked as resolved!', 'success')
    return redirect(url_for('my_reports'))

@app.route('/report/<int:report_id>/status', methods=['POST'])
def change_report_status(report_id):
    user_id = get_validated_user_id()
    if not user_id:
        flash('Please log in to manage your reports.', 'error')
        return redirect(url_for('login'))

    new_status = request.form.get('status', 'ACTIVE').upper()

    query = """
    UPDATE reports 
    SET status = %s 
    WHERE id = %s AND user_id = %s;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (new_status, report_id, user_id))
            conn.commit()

    flash(f'Report #{report_id} status updated to {new_status}!', 'success')
    return redirect(url_for('my_reports'))

# 7. Application Entry Point
if __name__ == '__main__':
    app.run(debug=True, port=5000)