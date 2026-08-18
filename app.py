import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image

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

# Serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Home & Reports Feed
@app.route('/')
def index():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM reports ORDER BY id DESC")
            reports = [dict(r) for r in cursor.fetchall()]
    return render_template('index.html', reports=reports)

# Auth Routes
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

# Report Submission
@app.route('/report/<report_type>', methods=['GET', 'POST'])
def report_pet(report_type):
    report_type = report_type.upper()
    if request.method == 'POST':
        file = request.files.get('image')
        if not file or file.filename == '':
            flash('Please upload an image.', 'error')
            return redirect(request.url)

        # Save uploaded image
        filename = secure_filename(f"{report_type.lower()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process image with YOLO
        image = Image.open(filepath).convert("RGB")
        detection = detector.detect(image)

        user_species = request.form.get('species', '').strip().lower()

        # Extract ResNet vector embedding
        vector = extract_image_vector(filepath)

        address_text = request.form.get('address', '')
        lat, lon = get_coordinates(address_text)

        user_id = session.get('user', {}).get('id')
        report_data = {
            "user_id": user_id,
            "type": report_type,
            "species": user_species if user_species else detection['species'],
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

        # Trigger email if a strong match is detected
        if matches and matches[0]['match_score'] >= 75:
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

# AI Matching Engine View
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

# User's Personal Dashboard
@app.route('/my-reports')
def my_reports():
    if 'user' not in session:
        flash('Please log in to view your reports.', 'error')
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM reports WHERE user_id = %s ORDER BY id DESC", (session['user']['id'],))
            reports = [dict(r) for r in cursor.fetchall()]

    return render_template('my_reports.html', reports=reports)

@app.route('/resolve/<int:report_id>', methods=['POST'])
def resolve_report(report_id):
    if 'user' in session:
        update_report_status(report_id, 'RESOLVED')
        flash(f'Report #{report_id} marked as resolved!', 'success')
    return redirect(url_for('my_reports'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

@app.route('/report/<int:report_id>/status', methods=['POST'])
def update_report_status(report_id):
    if 'user' not in session:
        flash('Please log in to manage your reports.', 'error')
        return redirect(url_for('login'))

    new_status = request.form.get('status', 'ACTIVE').upper()
    user_id = session['user']['id']

    # Update query ensuring user owns the report
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