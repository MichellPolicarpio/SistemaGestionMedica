from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import json
from email_config import EMAIL_CONFIG
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/patient_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text, nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Medical History
    past_illnesses = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    allergies = db.Column(db.Text)
    food_habits = db.Column(db.Text)
    
    # Relationships
    diseases = db.relationship('Disease', backref='patient', lazy=True, cascade='all, delete-orphan')
    medications = db.relationship('Medication', backref='patient', lazy=True, cascade='all, delete-orphan')
    prescriptions = db.relationship('Prescription', backref='patient', lazy=True, cascade='all, delete-orphan')
    diagnoses = db.relationship('Diagnosis', backref='patient', lazy=True, cascade='all, delete-orphan')

class Disease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    diagnosis_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='Active')  # Active, Cured, Chronic
    notes = db.Column(db.Text)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='Active')  # Active, Discontinued
    notes = db.Column(db.Text)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    doctor_name = db.Column(db.String(100), nullable=False)
    professional_license = db.Column(db.String(50), nullable=False)  # Cédula profesional
    diagnosis = db.Column(db.Text, nullable=False)
    medications = db.Column(db.Text, nullable=False)  # JSON string of medications
    instructions = db.Column(db.Text)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Diagnosis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    doctor_name = db.Column(db.String(100), nullable=False)
    professional_license = db.Column(db.String(50), nullable=False)  # Cédula profesional
    symptoms = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    treatment_plan = db.Column(db.Text)
    notes = db.Column(db.Text)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    payment_method = db.Column(db.String(50), nullable=False)  # Cash, Card, Transfer
    service_type = db.Column(db.String(100), nullable=False)  # Consultation, Diagnosis, Prescription, etc.
    status = db.Column(db.String(20), default='Pending')  # Pending, Completed, Cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con paciente
    patient = db.relationship('Patient', backref='payments')

# Routes
@app.route('/')
def index():
    patients = Patient.query.all()
    
    # Calculate statistics
    total_patients = len(patients)
    
    # Count patients with diagnoses
    patients_with_diagnoses = sum(1 for p in patients if p.diagnoses)
    
    # Count patients with prescriptions
    patients_with_prescriptions = sum(1 for p in patients if p.prescriptions)
    
    # Count new patients this month (July 2025)
    from datetime import datetime
    july_start = datetime(2025, 7, 1)
    new_this_month = sum(1 for p in patients if p.created_at >= july_start)
    
    # Payment statistics
    total_revenue = sum(p.amount for p in db.session.query(Payment).filter_by(status='Completed').all())
    pending_payments = sum(p.amount for p in db.session.query(Payment).filter_by(status='Pending').all())
    total_payments = db.session.query(Payment).count()
    
    stats = {
        'total_patients': total_patients,
        'patients_with_diagnoses': patients_with_diagnoses,
        'patients_with_prescriptions': patients_with_prescriptions,
        'new_this_month': new_this_month,
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
        'total_payments': total_payments
    }
    
    return render_template('index.html', patients=patients, stats=stats)

@app.route('/patients')
def all_patients():
    patients = Patient.query.order_by(Patient.created_at.desc()).all()
    return render_template('all_patients.html', patients=patients)

@app.route('/search_patients')
def search_patients():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    # Buscar por nombre, email, teléfono o dirección
    patients = Patient.query.filter(
        db.or_(
            Patient.name.ilike(f'%{query}%'),
            Patient.email.ilike(f'%{query}%'),
            Patient.phone.ilike(f'%{query}%'),
            Patient.address.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    results = []
    for patient in patients:
        results.append({
            'id': patient.id,
            'name': patient.name,
            'email': patient.email,
            'phone': patient.phone,
            'age': ((datetime.now().date() - patient.date_of_birth).days // 365)
        })
    
    return jsonify(results)

# Payment Management Routes
@app.route('/patient/<int:patient_id>/payments')
def patient_payments(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    payments = Payment.query.filter_by(patient_id=patient_id).order_by(Payment.payment_date.desc()).all()
    return render_template('patient_payments.html', patient=patient, payments=payments)

@app.route('/patient/<int:patient_id>/payment/new', methods=['GET', 'POST'])
def new_payment(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        try:
            payment = Payment(
                patient_id=patient_id,
                amount=float(request.form['amount']),
                payment_date=datetime.strptime(request.form['payment_date'], '%Y-%m-%d').date(),
                payment_method=request.form['payment_method'],
                service_type=request.form['service_type'],
                status=request.form['status'],
                notes=request.form['notes']
            )
            db.session.add(payment)
            db.session.commit()
            flash('Pago registrado exitosamente!', 'success')
            return redirect(url_for('patient_payments', patient_id=patient_id))
        except Exception as e:
            flash(f'Error al registrar pago: {str(e)}', 'error')
    
    return render_template('new_payment.html', patient=patient)

@app.route('/payment/<int:payment_id>/delete', methods=['POST'])
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    patient_id = payment.patient_id
    try:
        db.session.delete(payment)
        db.session.commit()
        flash('Pago eliminado exitosamente!', 'success')
    except Exception as e:
        flash(f'Error al eliminar pago: {str(e)}', 'error')
    
    return redirect(url_for('patient_payments', patient_id=patient_id))

@app.route('/payments')
def all_payments():
    payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    total_revenue = sum(p.amount for p in payments if p.status == 'Completed')
    pending_payments = sum(p.amount for p in payments if p.status == 'Pending')
    
    stats = {
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
        'total_payments': len(payments)
    }
    
    return render_template('all_payments.html', payments=payments, stats=stats)

@app.route('/patient/new', methods=['GET', 'POST'])
def new_patient():
    if request.method == 'POST':
        try:
            patient = Patient(
                name=request.form['name'],
                email=request.form['email'],
                phone=request.form['phone'],
                date_of_birth=datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date(),
                address=request.form['address'],
                height=float(request.form['height']),
                weight=float(request.form['weight']),
                past_illnesses=request.form['past_illnesses'],
                current_medications=request.form['current_medications'],
                allergies=request.form['allergies'],
                food_habits=request.form['food_habits']
            )
            db.session.add(patient)
            db.session.commit()
            flash('Patient added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error adding patient: {str(e)}', 'error')
            return redirect(url_for('new_patient'))
    
    return render_template('new_patient.html')

@app.route('/patient/<int:patient_id>')
def view_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template('view_patient.html', patient=patient)

@app.route('/patient/<int:patient_id>/edit', methods=['GET', 'POST'])
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        try:
            patient.name = request.form['name']
            patient.email = request.form['email']
            patient.phone = request.form['phone']
            patient.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            patient.address = request.form['address']
            patient.height = float(request.form['height'])
            patient.weight = float(request.form['weight'])
            patient.past_illnesses = request.form['past_illnesses']
            patient.current_medications = request.form['current_medications']
            patient.allergies = request.form['allergies']
            patient.food_habits = request.form['food_habits']
            
            db.session.commit()
            flash('Patient updated successfully!', 'success')
            return redirect(url_for('view_patient', patient_id=patient.id))
        except Exception as e:
            flash(f'Error updating patient: {str(e)}', 'error')
    
    return render_template('edit_patient.html', patient=patient)

@app.route('/patient/<int:patient_id>/delete', methods=['POST'])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    try:
        db.session.delete(patient)
        db.session.commit()
        flash('Patient deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting patient: {str(e)}', 'error')
    
    return redirect(url_for('index'))

# Disease Management
@app.route('/patient/<int:patient_id>/diseases')
def patient_diseases(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template('diseases.html', patient=patient)

@app.route('/patient/<int:patient_id>/disease/new', methods=['POST'])
def add_disease(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    try:
        disease = Disease(
            name=request.form['name'],
            diagnosis_date=datetime.strptime(request.form['diagnosis_date'], '%Y-%m-%d').date(),
            status=request.form['status'],
            notes=request.form['notes'],
            patient_id=patient_id
        )
        db.session.add(disease)
        db.session.commit()
        flash('Disease added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding disease: {str(e)}', 'error')
    
    return redirect(url_for('patient_diseases', patient_id=patient_id))

@app.route('/disease/<int:disease_id>/delete', methods=['POST'])
def delete_disease(disease_id):
    disease = Disease.query.get_or_404(disease_id)
    patient_id = disease.patient_id
    try:
        db.session.delete(disease)
        db.session.commit()
        flash('Disease deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting disease: {str(e)}', 'error')
    
    return redirect(url_for('patient_diseases', patient_id=patient_id))

# Medication Management
@app.route('/patient/<int:patient_id>/medications')
def patient_medications(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template('medications.html', patient=patient)

@app.route('/patient/<int:patient_id>/medication/new', methods=['POST'])
def add_medication(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    try:
        medication = Medication(
            name=request.form['name'],
            dosage=request.form['dosage'],
            frequency=request.form['frequency'],
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form['end_date'] else None,
            status=request.form['status'],
            notes=request.form['notes'],
            patient_id=patient_id
        )
        db.session.add(medication)
        db.session.commit()
        flash('Medication added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding medication: {str(e)}', 'error')
    
    return redirect(url_for('patient_medications', patient_id=patient_id))

@app.route('/medication/<int:medication_id>/delete', methods=['POST'])
def delete_medication(medication_id):
    medication = Medication.query.get_or_404(medication_id)
    patient_id = medication.patient_id
    try:
        db.session.delete(medication)
        db.session.commit()
        flash('Medication deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting medication: {str(e)}', 'error')
    
    return redirect(url_for('patient_medications', patient_id=patient_id))

# Data Visualization
@app.route('/analytics')
def analytics():
    try:
        # Get data for charts
        patients = Patient.query.all()
        
        # Age distribution
        ages = []
        for patient in patients:
            try:
                age = (datetime.now().date() - patient.date_of_birth).days // 365
                ages.append(age)
            except:
                ages.append(0)  # Default age if calculation fails
        
        # BMI distribution
        bmi_data = []
        for patient in patients:
            try:
                height_m = patient.height / 100  # Convert cm to meters
                bmi = patient.weight / (height_m ** 2)
                bmi_data.append(bmi)
            except:
                bmi_data.append(0)  # Default BMI if calculation fails
        
        # Disease statistics
        diseases = Disease.query.all()
        disease_counts = {}
        for disease in diseases:
            disease_counts[disease.name] = disease_counts.get(disease.name, 0) + 1
        
        # Create charts
        plt.style.use('default')
        
        # Age distribution pie chart
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        age_ranges = ['0-20', '21-40', '41-60', '61+']
        age_counts = [0, 0, 0, 0]
        
        for age in ages:
            if age <= 20:
                age_counts[0] += 1
            elif age <= 40:
                age_counts[1] += 1
            elif age <= 60:
                age_counts[2] += 1
            else:
                age_counts[3] += 1
        
        colors1 = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        ax1.pie(age_counts, labels=age_ranges, autopct='%1.1f%%', colors=colors1)
        ax1.set_title('Age Distribution')
        
        # Save age chart
        age_chart_path = 'static/age_chart.png'
        plt.savefig(age_chart_path, bbox_inches='tight', dpi=300)
        plt.close()
        
        # BMI distribution pie chart
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        bmi_ranges = ['Underweight', 'Normal', 'Overweight', 'Obese']
        bmi_counts = [0, 0, 0, 0]
        
        for bmi in bmi_data:
            if bmi < 18.5:
                bmi_counts[0] += 1
            elif bmi < 25:
                bmi_counts[1] += 1
            elif bmi < 30:
                bmi_counts[2] += 1
            else:
                bmi_counts[3] += 1
        
        colors2 = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
        ax2.pie(bmi_counts, labels=bmi_ranges, autopct='%1.1f%%', colors=colors2)
        ax2.set_title('BMI Distribution')
        
        # Save BMI chart
        bmi_chart_path = 'static/bmi_chart.png'
        plt.savefig(bmi_chart_path, bbox_inches='tight', dpi=300)
        plt.close()
        
        # Disease distribution pie chart
        if disease_counts:
            fig3, ax3 = plt.subplots(figsize=(12, 8))
            disease_names = list(disease_counts.keys())
            disease_values = list(disease_counts.values())
            
            colors3 = plt.cm.Set3(range(len(disease_names)))
            ax3.pie(disease_values, labels=disease_names, autopct='%1.1f%%', colors=colors3)
            ax3.set_title('Disease Distribution')
            
            # Save disease chart
            disease_chart_path = 'static/disease_chart.png'
            plt.savefig(disease_chart_path, bbox_inches='tight', dpi=300)
            plt.close()
        else:
            disease_chart_path = None
        
        return render_template('analytics.html', 
                             age_chart='age_chart.png',
                             bmi_chart='bmi_chart.png',
                             disease_chart='disease_chart.png' if disease_chart_path else None,
                             total_patients=len(patients),
                             total_diseases=len(diseases))
    except Exception as e:
        # Return a simple page if analytics fails
        return render_template('analytics.html', 
                             age_chart=None,
                             bmi_chart=None,
                             disease_chart=None,
                             total_patients=0,
                             total_diseases=0,
                             error=str(e))

def generate_pdf_report(patient):
    """Generate a PDF report for a patient"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        
        # Title
        story.append(Paragraph(f"Patient Report - {patient.name}", title_style))
        story.append(Spacer(1, 12))
        
        # Personal Information
        story.append(Paragraph("Personal Information", styles['Heading2']))
        personal_data = [
            ['Name', patient.name],
            ['Email', patient.email],
            ['Phone', patient.phone],
            ['Date of Birth', patient.date_of_birth.strftime('%B %d, %Y')],
            ['Address', patient.address],
            ['Height', f"{patient.height} cm"],
            ['Weight', f"{patient.weight} kg"],
            ['BMI', f"{patient.weight / ((patient.height/100) ** 2):.1f}"]
        ]
        
        personal_table = Table(personal_data, colWidths=[2*inch, 4*inch])
        personal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(personal_table)
        story.append(Spacer(1, 12))
        
        # Medical History
        story.append(Paragraph("Medical History", styles['Heading2']))
        medical_data = [
            ['Past Illnesses', patient.past_illnesses or 'None'],
            ['Current Medications', patient.current_medications or 'None'],
            ['Allergies', patient.allergies or 'None'],
            ['Food Habits', patient.food_habits or 'None']
        ]
        
        medical_table = Table(medical_data, colWidths=[2*inch, 4*inch])
        medical_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(medical_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Save to file
        report_filename = f"patient_report_{patient.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        report_path = os.path.join('reports', report_filename)
        
        # Create reports directory if it doesn't exist
        os.makedirs('reports', exist_ok=True)
        
        with open(report_path, 'wb') as f:
            f.write(buffer.getvalue())
        
        return report_path
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return None

# Report Generation
@app.route('/patient/<int:patient_id>/report')
def generate_report(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    # Create PDF report
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1
    )
    
    # Title
    story.append(Paragraph(f"Patient Report - {patient.name}", title_style))
    story.append(Spacer(1, 12))
    
    # Personal Information
    story.append(Paragraph("Personal Information", styles['Heading2']))
    personal_data = [
        ['Name', patient.name],
        ['Email', patient.email],
        ['Phone', patient.phone],
        ['Date of Birth', patient.date_of_birth.strftime('%B %d, %Y')],
        ['Address', patient.address],
        ['Height', f"{patient.height} cm"],
        ['Weight', f"{patient.weight} kg"],
        ['BMI', f"{patient.weight / ((patient.height/100) ** 2):.1f}"]
    ]
    
    personal_table = Table(personal_data, colWidths=[2*inch, 4*inch])
    personal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(personal_table)
    story.append(Spacer(1, 12))
    
    # Medical History
    story.append(Paragraph("Medical History", styles['Heading2']))
    medical_data = [
        ['Past Illnesses', patient.past_illnesses or 'None'],
        ['Current Medications', patient.current_medications or 'None'],
        ['Allergies', patient.allergies or 'None'],
        ['Food Habits', patient.food_habits or 'None']
    ]
    
    medical_table = Table(medical_data, colWidths=[2*inch, 4*inch])
    medical_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(medical_table)
    story.append(Spacer(1, 12))
    
    # Diseases
    if patient.diseases:
        story.append(Paragraph("Diseases", styles['Heading2']))
        disease_data = [['Disease', 'Diagnosis Date', 'Status', 'Notes']]
        for disease in patient.diseases:
            disease_data.append([
                disease.name,
                disease.diagnosis_date.strftime('%Y-%m-%d'),
                disease.status,
                disease.notes or ''
            ])
        
        disease_table = Table(disease_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 2*inch])
        disease_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(disease_table)
        story.append(Spacer(1, 12))
    
    # Medications
    if patient.medications:
        story.append(Paragraph("Medications", styles['Heading2']))
        medication_data = [['Medication', 'Dosage', 'Frequency', 'Start Date', 'End Date', 'Status']]
        for medication in patient.medications:
            medication_data.append([
                medication.name,
                medication.dosage,
                medication.frequency,
                medication.start_date.strftime('%Y-%m-%d'),
                medication.end_date.strftime('%Y-%m-%d') if medication.end_date else 'Ongoing',
                medication.status
            ])
        
        medication_table = Table(medication_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
        medication_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(medication_table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"patient_report_{patient.name.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

# Email Report
@app.route('/patient/<int:patient_id>/email_report', methods=['GET', 'POST'])
def email_report(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        recipient_email = request.form['recipient_email']
        
        # Generate PDF report
        report_path = generate_pdf_report(patient)
        
        if report_path:
            try:
                # Create email message
                msg = MIMEMultipart()
                msg['From'] = EMAIL_CONFIG['sender_email']
                msg['To'] = recipient_email
                msg['Subject'] = f'Patient Report - {patient.name}'
                
                body = f"""
                Dear Healthcare Provider,
                
                Please find attached the patient report for {patient.name}.
                
                Patient Information:
                - Name: {patient.name}
                - Email: {patient.email}
                - Phone: {patient.phone}
                - Date of Birth: {patient.date_of_birth.strftime('%B %d, %Y')}
                
                This report contains detailed patient information including medical history, 
                current medications, allergies, and other relevant health data.
                
                Best regards,
                Patient Management System
                """
                
                msg.attach(MIMEText(body, 'plain'))
                
                # Attach PDF
                with open(report_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename=patient_report_{patient.name.replace(" ", "_")}.pdf'
                    )
                    msg.attach(part)
                
                # Send email using configured SMTP settings
                try:
                    print(f"Attempting to send email to: {recipient_email}")
                    print(f"Using SMTP server: {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}")
                    
                    if EMAIL_CONFIG.get('use_ssl', False):
                        server = smtplib.SMTP_SSL(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'], timeout=30)
                    else:
                        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'], timeout=30)
                        if EMAIL_CONFIG.get('use_tls', False):
                            print("Starting TLS...")
                            server.starttls()
                    
                    print("Logging in...")
                    server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
                    print("Login successful!")
                    
                    text = msg.as_string()
                    print("Sending email...")
                    server.sendmail(EMAIL_CONFIG['sender_email'], recipient_email, text)
                    server.quit()
                    
                    flash(f'Report sent successfully to {recipient_email}!', 'success')
                    print(f"Email sent successfully to: {recipient_email}")
                    print(f"Patient: {patient.name}")
                    print(f"Report generated: {report_path}")
                    
                except Exception as email_error:
                    flash(f'Error sending email: {str(email_error)}', 'error')
                    print(f"Email error: {str(email_error)}")
                    print(f"Full error details: {type(email_error).__name__}: {email_error}")
                
                return redirect(url_for('view_patient', patient_id=patient_id))
                
            except Exception as e:
                flash(f'Error generating or sending report: {str(e)}', 'error')
                print(f"General error: {str(e)}")
        else:
            flash('Error generating report', 'error')
    
    return render_template('email_report.html', patient=patient)

@app.route('/patient/<int:patient_id>/prescriptions')
def patient_prescriptions(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    prescriptions = Prescription.query.filter_by(patient_id=patient_id).order_by(Prescription.date.desc()).all()
    return render_template('patient_prescriptions.html', patient=patient, prescriptions=prescriptions)

@app.route('/patient/<int:patient_id>/prescription/new', methods=['GET', 'POST'])
def new_prescription(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        prescription = Prescription(
            doctor_name=request.form['doctor_name'],
            diagnosis=request.form['diagnosis'],
            medications=request.form['medications'],
            instructions=request.form['instructions'],
            patient_id=patient_id
        )
        db.session.add(prescription)
        db.session.commit()
        flash('Prescription created successfully!', 'success')
        return redirect(url_for('patient_prescriptions', patient_id=patient_id))
    
    return render_template('new_prescription.html', patient=patient)

@app.route('/patient/<int:patient_id>/diagnoses')
def patient_diagnoses(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    diagnoses = Diagnosis.query.filter_by(patient_id=patient_id).order_by(Diagnosis.date.desc()).all()
    return render_template('patient_diagnoses.html', patient=patient, diagnoses=diagnoses)

@app.route('/patient/<int:patient_id>/diagnosis/new', methods=['GET', 'POST'])
def new_diagnosis(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        diagnosis = Diagnosis(
            doctor_name=request.form['doctor_name'],
            professional_license=request.form['professional_license'],
            symptoms=request.form['symptoms'],
            diagnosis=request.form['diagnosis'],
            treatment_plan=request.form['treatment_plan'],
            notes=request.form['notes'],
            patient_id=patient_id
        )
        db.session.add(diagnosis)
        db.session.commit()
        
        # Auto-generate prescription if treatment plan is provided
        treatment_plan = request.form['treatment_plan'].strip()
        if treatment_plan:
            # Create prescription based on the diagnosis
            prescription = Prescription(
                doctor_name=request.form['doctor_name'],
                professional_license=request.form['professional_license'],
                diagnosis=request.form['diagnosis'],
                medications=treatment_plan,  # Use treatment plan as medications
                instructions=f"Basado en el diagnóstico: {request.form['diagnosis']}. {treatment_plan}",
                patient_id=patient_id
            )
            db.session.add(prescription)
            db.session.commit()
        
        # Auto-generate payment for the consultation
        consultation_amount = float(request.form.get('consultation_amount', 300.00))  # Default $300
        
        payment = Payment(
            patient_id=patient_id,
            amount=consultation_amount,
            payment_date=datetime.now().date(),
            payment_method=request.form.get('payment_method', 'Cash'),
            service_type='Consulta General',
            status='Completed',
            notes=f"Pago automático por diagnóstico: {request.form['diagnosis']}"
        )
        db.session.add(payment)
        db.session.commit()
        
        if treatment_plan:
            flash('Diagnosis created successfully! Prescription and payment auto-generated.', 'success')
        else:
            flash('Diagnosis created successfully! Payment auto-generated for consultation.', 'success')
        
        return redirect(url_for('patient_diagnoses', patient_id=patient_id))
    
    return render_template('new_diagnosis.html', patient=patient)

@app.route('/diagnosis/<int:diagnosis_id>/delete', methods=['POST'])
def delete_diagnosis(diagnosis_id):
    diagnosis = Diagnosis.query.get_or_404(diagnosis_id)
    patient_id = diagnosis.patient_id
    
    try:
        # Also delete any prescriptions that were auto-generated from this diagnosis
        # Find prescriptions with similar diagnosis and medications
        related_prescriptions = Prescription.query.filter_by(
            patient_id=patient_id,
            diagnosis=diagnosis.diagnosis
        ).all()
        
        deleted_prescriptions = 0
        for prescription in related_prescriptions:
            # Check if this prescription was auto-generated from this diagnosis
            # Look for treatment plan content in medications or instructions
            if (diagnosis.treatment_plan and 
                (diagnosis.treatment_plan in prescription.medications or 
                 diagnosis.treatment_plan in prescription.instructions or
                 f"Basado en el diagnóstico: {diagnosis.diagnosis}" in prescription.instructions)):
                db.session.delete(prescription)
                deleted_prescriptions += 1
        
        # Delete the diagnosis
        db.session.delete(diagnosis)
        db.session.commit()
        
        if deleted_prescriptions > 0:
            flash(f'Diagnosis and {deleted_prescriptions} related prescription(s) deleted successfully!', 'success')
        else:
            flash('Diagnosis deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting diagnosis: {str(e)}', 'error')
    
    return redirect(url_for('patient_diagnoses', patient_id=patient_id))

@app.route('/prescription/<int:prescription_id>/pdf')
def prescription_pdf(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)
    return generate_prescription_pdf(prescription)

@app.route('/diagnosis/<int:diagnosis_id>/pdf')
def diagnosis_pdf(diagnosis_id):
    diagnosis = Diagnosis.query.get_or_404(diagnosis_id)
    return generate_diagnosis_pdf(diagnosis)

def generate_prescription_pdf(prescription):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Header with clinic information
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1,  # Center
        spaceAfter=20
    )
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=18,
        alignment=1,  # Center
        spaceAfter=30,
        textColor=colors.darkblue
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,  # Center
        spaceAfter=15,
        textColor=colors.grey
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=10,
        textColor=colors.darkblue
    )
    
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=5
    )
    
    # Title at the top
    elements.append(Paragraph("RECETA MÉDICA", title_style))
    elements.append(Spacer(1, 15))
    
    # Clinic information aligned to the right
    clinic_info_style = ParagraphStyle(
        'ClinicInfo',
        parent=styles['Normal'],
        fontSize=10,
        alignment=2,  # Right alignment
        spaceAfter=5,
        textColor=colors.grey
    )
    
    elements.append(Paragraph("CLÍNICA MÉDICA INTEGRAL", clinic_info_style))
    elements.append(Paragraph("Especialistas en Medicina General", clinic_info_style))
    elements.append(Paragraph("Av. Independencia No. 123, Centro Histórico", clinic_info_style))
    elements.append(Paragraph("Ciudad de Veracruz, Veracruz, México", clinic_info_style))
    elements.append(Paragraph("Tel: (229) 123-4567 | Cel: (229) 987-6543", clinic_info_style))
    elements.append(Paragraph(f"Cédula Profesional: {prescription.professional_license}", clinic_info_style))
    elements.append(Spacer(1, 20))
    
    # Date and prescription number
    current_date = datetime.now().strftime("%d de %B del %Y")
    prescription_number = f"RX-{prescription.id:04d}-{datetime.now().strftime('%Y%m%d')}"
    
    elements.append(Paragraph(f"<b>Fecha:</b> {current_date}", info_style))
    elements.append(Paragraph(f"<b>No. de Receta:</b> {prescription_number}", info_style))
    elements.append(Spacer(1, 15))
    
    # Patient Information Section
    elements.append(Paragraph("DATOS DEL PACIENTE", section_style))
    elements.append(Paragraph(f"<b>Nombre:</b> {prescription.patient.name}", info_style))
    elements.append(Paragraph(f"<b>Fecha de Nacimiento:</b> {prescription.patient.date_of_birth.strftime('%d de %B de %Y')}", info_style))
    elements.append(Paragraph(f"<b>Edad:</b> {((datetime.now().date() - prescription.patient.date_of_birth).days // 365)} años", info_style))
    elements.append(Paragraph(f"<b>Teléfono:</b> {prescription.patient.phone}", info_style))
    elements.append(Paragraph(f"<b>Dirección:</b> {prescription.patient.address}", info_style))
    elements.append(Spacer(1, 15))
    
    # Doctor Information
    elements.append(Paragraph("DATOS DEL MÉDICO", section_style))
    elements.append(Paragraph(f"<b>Médico Tratante:</b> Dr. {prescription.doctor_name}", info_style))
    elements.append(Paragraph(f"<b>Especialidad:</b> Medicina General", info_style))
    elements.append(Paragraph(f"<b>Consultorio:</b> Consultorio No. 1", info_style))
    elements.append(Spacer(1, 15))
    
    # Get the most recent diagnosis for this patient
    recent_diagnosis = Diagnosis.query.filter_by(patient_id=prescription.patient_id).order_by(Diagnosis.date.desc()).first()
    
    # Diagnosis Section
    elements.append(Paragraph("DIAGNÓSTICO", section_style))
    
    # Format diagnosis with proper spacing
    diagnosis_text = prescription.diagnosis
    if diagnosis_text:
        # Split by common delimiters and format each diagnosis
        diagnosis_list = []
        for delimiter in ['\n', '.', ',', ';']:
            if delimiter in diagnosis_text:
                diagnosis_list = [d.strip() for d in diagnosis_text.split(delimiter) if d.strip()]
                break
        
        if not diagnosis_list:
            diagnosis_list = [diagnosis_text]
        
        # Add each diagnosis as a separate paragraph
        for diag in diagnosis_list:
            if diag:
                elements.append(Paragraph(f"• {diag}", info_style))
    else:
        elements.append(Paragraph("Diagnóstico pendiente de confirmación", info_style))
    
    elements.append(Spacer(1, 15))
    
    # Add recent diagnosis information if available
    if recent_diagnosis:
        elements.append(Paragraph("DIAGNÓSTICO PREVIO", section_style))
        elements.append(Paragraph(f"<b>Fecha del diagnóstico:</b> {recent_diagnosis.date.strftime('%d de %B de %Y')}", info_style))
        elements.append(Paragraph(f"<b>Médico que diagnosticó:</b> Dr. {recent_diagnosis.doctor_name}", info_style))
        
        # Add symptoms from the diagnosis
        if recent_diagnosis.symptoms:
            elements.append(Paragraph("<b>Síntomas referidos:</b>", info_style))
            symptoms_text = recent_diagnosis.symptoms
            symptoms_list = []
            for delimiter in ['\n', '.', ',', ';']:
                if delimiter in symptoms_text:
                    symptoms_list = [s.strip() for s in symptoms_text.split(delimiter) if s.strip()]
                    break
            
            if not symptoms_list:
                symptoms_list = [symptoms_text]
            
            for symptom in symptoms_list:
                if symptom:
                    elements.append(Paragraph(f"  - {symptom}", info_style))
        
        # Add diagnosis details
        if recent_diagnosis.diagnosis:
            elements.append(Paragraph("<b>Diagnóstico clínico:</b>", info_style))
            diag_text = recent_diagnosis.diagnosis
            diag_list = []
            for delimiter in ['\n', '.', ',', ';']:
                if delimiter in diag_text:
                    diag_list = [d.strip() for d in diag_text.split(delimiter) if d.strip()]
                    break
            
            if not diag_list:
                diag_list = [diag_text]
            
            for diag in diag_list:
                if diag:
                    elements.append(Paragraph(f"  - {diag}", info_style))
        
        # Add treatment plan from the diagnosis
        if recent_diagnosis.treatment_plan:
            elements.append(Paragraph("<b>Plan de tratamiento previo:</b>", info_style))
            treatment_text = recent_diagnosis.treatment_plan
            treatment_list = []
            for delimiter in ['\n', '.', ',', ';']:
                if delimiter in treatment_text:
                    treatment_list = [t.strip() for t in treatment_text.split(delimiter) if t.strip()]
                    break
            
            if not treatment_list:
                treatment_list = [treatment_text]
            
            for treatment in treatment_list:
                if treatment:
                    elements.append(Paragraph(f"  - {treatment}", info_style))
        
        # Add notes from the diagnosis
        if recent_diagnosis.notes:
            elements.append(Paragraph("<b>Observaciones previas:</b>", info_style))
            notes_text = recent_diagnosis.notes
            notes_list = []
            for delimiter in ['\n', '.', ',', ';']:
                if delimiter in notes_text:
                    notes_list = [n.strip() for n in notes_text.split(delimiter) if n.strip()]
                    break
            
            if not notes_list:
                notes_list = [notes_text]
            
            for note in notes_list:
                if note:
                    elements.append(Paragraph(f"  - {note}", info_style))
        
        elements.append(Spacer(1, 15))
    
    # Medications Section
    elements.append(Paragraph("MEDICAMENTOS PRESCRITOS", section_style))
    
    # Format medications with proper spacing
    medications_text = prescription.medications
    if medications_text:
        # Split by common delimiters and format each medication
        medications_list = []
        for delimiter in ['\n', '.', ',', ';']:
            if delimiter in medications_text:
                medications_list = [m.strip() for m in medications_text.split(delimiter) if m.strip()]
                break
        
        if not medications_list:
            medications_list = [medications_text]
        
        # Add each medication as a separate paragraph
        for medication in medications_list:
            if medication:
                elements.append(Paragraph(f"• {medication}", info_style))
    else:
        elements.append(Paragraph("Sin medicamentos prescritos", info_style))
    
    elements.append(Spacer(1, 15))
    
    # Instructions Section
    if prescription.instructions:
        elements.append(Paragraph("INSTRUCCIONES DE USO", section_style))
        
        # Format instructions with proper spacing
        instructions_text = prescription.instructions
        if instructions_text:
            # Split by common delimiters and format each instruction
            instructions_list = []
            for delimiter in ['\n', '.', ',', ';']:
                if delimiter in instructions_text:
                    instructions_list = [i.strip() for i in instructions_text.split(delimiter) if i.strip()]
                    break
            
            if not instructions_list:
                instructions_list = [instructions_text]
            
            # Add each instruction as a separate paragraph
            for instruction in instructions_list:
                if instruction:
                    elements.append(Paragraph(f"• {instruction}", info_style))
        else:
            elements.append(Paragraph("Seguir indicaciones del médico", info_style))
        
        elements.append(Spacer(1, 15))
    
    # Additional Information
    elements.append(Paragraph("INFORMACIÓN ADICIONAL", section_style))
    elements.append(Paragraph("• Tomar con alimentos para evitar malestar estomacal", info_style))
    elements.append(Paragraph("• No conducir vehículos bajo efectos de la medicación", info_style))
    elements.append(Paragraph("• Mantener hidratación adecuada", info_style))
    elements.append(Paragraph("• Evitar consumo de alcohol durante el tratamiento", info_style))
    elements.append(Spacer(1, 20))
    
    # Follow-up
    elements.append(Paragraph("CONTROL MÉDICO", section_style))
    elements.append(Paragraph("• Regresar en 7 días para evaluación", info_style))
    elements.append(Paragraph("• En caso de efectos secundarios, consultar inmediatamente", info_style))
    elements.append(Paragraph("• Mantener dieta balanceada y ejercicio moderado", info_style))
    elements.append(Spacer(1, 30))
    
    # Signature Section
    elements.append(Paragraph("_" * 60, info_style))
    elements.append(Paragraph(f"Dr. {prescription.doctor_name}", info_style))
    elements.append(Paragraph("Médico General", info_style))
    elements.append(Paragraph(f"Cédula Profesional: {prescription.professional_license}", info_style))
    elements.append(Paragraph("Clínica Médica Integral", info_style))
    
    # Footer
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Esta receta es válida por 30 días a partir de la fecha de emisión", 
                            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.grey)))
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"receta_medica_{prescription.patient.name}_{prescription.date}.pdf",
        mimetype='application/pdf'
    )

def generate_diagnosis_pdf(diagnosis):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Header with clinic information
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1,  # Center
        spaceAfter=20
    )
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=18,
        alignment=1,  # Center
        spaceAfter=30,
        textColor=colors.darkblue
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,  # Center
        spaceAfter=15,
        textColor=colors.grey
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=10,
        textColor=colors.darkblue
    )
    
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=5
    )
    
    # Title at the top
    elements.append(Paragraph("REPORTE DE DIAGNÓSTICO MÉDICO", title_style))
    elements.append(Spacer(1, 15))
    
    # Clinic information aligned to the right
    clinic_info_style = ParagraphStyle(
        'ClinicInfo',
        parent=styles['Normal'],
        fontSize=10,
        alignment=2,  # Right alignment
        spaceAfter=5,
        textColor=colors.grey
    )
    
    elements.append(Paragraph("CLÍNICA MÉDICA INTEGRAL", clinic_info_style))
    elements.append(Paragraph("Especialistas en Medicina General", clinic_info_style))
    elements.append(Paragraph("Av. Independencia No. 123, Centro Histórico", clinic_info_style))
    elements.append(Paragraph("Ciudad de Veracruz, Veracruz, México", clinic_info_style))
    elements.append(Paragraph("Tel: (229) 123-4567 | Cel: (229) 987-6543", clinic_info_style))
    elements.append(Paragraph(f"Cédula Profesional: {diagnosis.professional_license}", clinic_info_style))
    elements.append(Spacer(1, 20))
    
    # Date and diagnosis number
    current_date = datetime.now().strftime("%d de %B del %Y")
    diagnosis_number = f"DX-{diagnosis.id:04d}-{datetime.now().strftime('%Y%m%d')}"
    
    elements.append(Paragraph(f"<b>Fecha de Consulta:</b> {current_date}", info_style))
    elements.append(Paragraph(f"<b>No. de Diagnóstico:</b> {diagnosis_number}", info_style))
    elements.append(Spacer(1, 15))
    
    # Patient Information Section
    elements.append(Paragraph("DATOS DEL PACIENTE", section_style))
    elements.append(Paragraph(f"<b>Nombre:</b> {diagnosis.patient.name}", info_style))
    elements.append(Paragraph(f"<b>Fecha de Nacimiento:</b> {diagnosis.patient.date_of_birth.strftime('%d de %B de %Y')}", info_style))
    elements.append(Paragraph(f"<b>Edad:</b> {((datetime.now().date() - diagnosis.patient.date_of_birth).days // 365)} años", info_style))
    elements.append(Paragraph(f"<b>Teléfono:</b> {diagnosis.patient.phone}", info_style))
    elements.append(Paragraph(f"<b>Dirección:</b> {diagnosis.patient.address}", info_style))
    elements.append(Paragraph(f"<b>Altura:</b> {diagnosis.patient.height} cm", info_style))
    elements.append(Paragraph(f"<b>Peso:</b> {diagnosis.patient.weight} kg", info_style))
    elements.append(Paragraph(f"<b>IMC:</b> {diagnosis.patient.weight / ((diagnosis.patient.height/100) ** 2):.1f}", info_style))
    elements.append(Spacer(1, 15))
    
    # Doctor Information
    elements.append(Paragraph("DATOS DEL MÉDICO", section_style))
    elements.append(Paragraph(f"<b>Médico Tratante:</b> Dr. {diagnosis.doctor_name}", info_style))
    elements.append(Paragraph(f"<b>Especialidad:</b> Medicina General", info_style))
    elements.append(Paragraph(f"<b>Consultorio:</b> Consultorio No. 1", info_style))
    elements.append(Spacer(1, 15))
    
    # Symptoms Section
    elements.append(Paragraph("SÍNTOMAS REFERIDOS", section_style))
    
    # Format symptoms with proper spacing
    symptoms_text = diagnosis.symptoms
    if symptoms_text:
        # Split by common delimiters and format each symptom
        symptoms_list = []
        for delimiter in ['\n', '.', ',', ';']:
            if delimiter in symptoms_text:
                symptoms_list = [s.strip() for s in symptoms_text.split(delimiter) if s.strip()]
                break
        
        if not symptoms_list:
            symptoms_list = [symptoms_text]
        
        # Add each symptom as a separate paragraph with bullet points
        for symptom in symptoms_list:
            if symptom:
                elements.append(Paragraph(f"• {symptom}", info_style))
    else:
        elements.append(Paragraph("No se reportaron síntomas específicos", info_style))
    
    elements.append(Spacer(1, 15))
    
    # Diagnosis Section
    elements.append(Paragraph("DIAGNÓSTICO CLÍNICO", section_style))
    
    # Format diagnosis with proper spacing
    diagnosis_text = diagnosis.diagnosis
    if diagnosis_text:
        # Split by common delimiters and format each diagnosis
        diagnosis_list = []
        for delimiter in ['\n', '.', ',', ';']:
            if delimiter in diagnosis_text:
                diagnosis_list = [d.strip() for d in diagnosis_text.split(delimiter) if d.strip()]
                break
        
        if not diagnosis_list:
            diagnosis_list = [diagnosis_text]
        
        # Add each diagnosis as a separate paragraph
        for diag in diagnosis_list:
            if diag:
                elements.append(Paragraph(f"• {diag}", info_style))
    else:
        elements.append(Paragraph("Diagnóstico pendiente de confirmación", info_style))
    
    elements.append(Spacer(1, 15))
    
    # Treatment Plan Section
    if diagnosis.treatment_plan:
        elements.append(Paragraph("PLAN DE TRATAMIENTO", section_style))
        
        # Format treatment plan with proper spacing
        treatment_text = diagnosis.treatment_plan
        if treatment_text:
            # Split by common delimiters and format each treatment step
            treatment_list = []
            for delimiter in ['\n', '.', ',', ';']:
                if delimiter in treatment_text:
                    treatment_list = [t.strip() for t in treatment_text.split(delimiter) if t.strip()]
                    break
            
            if not treatment_list:
                treatment_list = [treatment_text]
            
            # Add each treatment step as a separate paragraph
            for treatment in treatment_list:
                if treatment:
                    elements.append(Paragraph(f"• {treatment}", info_style))
        else:
            elements.append(Paragraph("Plan de tratamiento pendiente", info_style))
        
        elements.append(Spacer(1, 15))
    
    # Notes Section
    if diagnosis.notes:
        elements.append(Paragraph("OBSERVACIONES MÉDICAS", section_style))
        
        # Format notes with proper spacing
        notes_text = diagnosis.notes
        if notes_text:
            # Split by common delimiters and format each note
            notes_list = []
            for delimiter in ['\n', '.', ',', ';']:
                if delimiter in notes_text:
                    notes_list = [n.strip() for n in notes_text.split(delimiter) if n.strip()]
                    break
            
            if not notes_list:
                notes_list = [notes_text]
            
            # Add each note as a separate paragraph
            for note in notes_list:
                if note:
                    elements.append(Paragraph(f"• {note}", info_style))
        else:
            elements.append(Paragraph("Sin observaciones adicionales", info_style))
        
        elements.append(Spacer(1, 15))
    
    # Medical History Summary
    elements.append(Paragraph("RESUMEN DE HISTORIAL MÉDICO", section_style))
    elements.append(Paragraph(f"<b>Enfermedades Previas:</b> {diagnosis.patient.past_illnesses or 'Sin antecedentes'}", info_style))
    elements.append(Paragraph(f"<b>Medicamentos Actuales:</b> {diagnosis.patient.current_medications or 'Ninguno'}", info_style))
    elements.append(Paragraph(f"<b>Alergias:</b> {diagnosis.patient.allergies or 'Sin alergias conocidas'}", info_style))
    elements.append(Paragraph(f"<b>Hábitos Alimenticios:</b> {diagnosis.patient.food_habits or 'No especificado'}", info_style))
    elements.append(Spacer(1, 20))
    
    # Recommendations
    elements.append(Paragraph("RECOMENDACIONES GENERALES", section_style))
    elements.append(Paragraph("• Mantener una dieta balanceada y baja en grasas", info_style))
    elements.append(Paragraph("• Realizar ejercicio moderado regularmente", info_style))
    elements.append(Paragraph("• Evitar el consumo de tabaco y alcohol", info_style))
    elements.append(Paragraph("• Mantener una hidratación adecuada", info_style))
    elements.append(Paragraph("• Dormir al menos 7-8 horas diarias", info_style))
    elements.append(Spacer(1, 20))
    
    # Follow-up
    elements.append(Paragraph("CONTROL MÉDICO", section_style))
    elements.append(Paragraph("• Regresar en 15 días para evaluación de progreso", info_style))
    elements.append(Paragraph("• En caso de empeoramiento de síntomas, consultar inmediatamente", info_style))
    elements.append(Paragraph("• Realizar estudios de laboratorio según indicación médica", info_style))
    elements.append(Spacer(1, 30))
    
    # Signature Section
    elements.append(Paragraph("_" * 60, info_style))
    elements.append(Paragraph(f"Dr. {diagnosis.doctor_name}", info_style))
    elements.append(Paragraph("Médico General", info_style))
    elements.append(Paragraph(f"Cédula Profesional: {diagnosis.professional_license}", info_style))
    elements.append(Paragraph("Clínica Médica Integral", info_style))
    
    # Footer
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Este documento es confidencial y solo debe ser compartido con personal médico autorizado", 
                            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.grey)))
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"diagnostico_medico_{diagnosis.patient.name}_{diagnosis.date}.pdf",
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    # Remove the db.create_all() call since tables already exist
    app.run(debug=True, port=5002) 