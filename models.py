from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """User model representing nurses in the system"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='nurse')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Patient(db.Model):
    """Patient model for storing patient information"""
    id = db.Column(db.Integer, primary_key=True)
    medical_record_number = db.Column(db.String(20), unique=True, nullable=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    arrival_mode = db.Column(db.String(20), nullable=False)  # 'ambulance' or 'walk-in'
    referral_source = db.Column(db.String(100), nullable=True)  # For ambulance arrivals
    insurance_type = db.Column(db.String(50), nullable=True)
    insurance_number = db.Column(db.String(50), nullable=True)
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    triage = db.relationship('Triage', backref='patient', uselist=False)
    nurse_assessments = db.relationship('NurseAssessment', backref='patient')
    doctor_examinations = db.relationship('DoctorExamination', backref='patient')
    lab_requests = db.relationship('LabRequest', backref='patient')
    prescriptions = db.relationship('Prescription', backref='patient')
    disposition = db.relationship('Disposition', backref='patient', uselist=False)

class Triage(db.Model):
    """Triage categorization model"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    category = db.Column(db.String(10), nullable=False)  # 'red', 'yellow', 'green', 'black'
    reason = db.Column(db.String(200), nullable=False)
    vital_signs = db.Column(db.JSON, nullable=True)
    triaged_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    triaged_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to User who performed triage
    nurse = db.relationship('User', backref='triages')

class NurseAssessment(db.Model):
    """Initial nursing assessment model"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    chief_complaint = db.Column(db.String(200), nullable=False)
    history = db.Column(db.Text, nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    medications = db.Column(db.Text, nullable=True)
    vital_signs = db.Column(db.JSON, nullable=False)
    assessment_details = db.Column(db.Text, nullable=True)
    nurse_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to User who performed assessment
    nurse = db.relationship('User', backref='assessments')

class DoctorExamination(db.Model):
    """Doctor examination and diagnosis model"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    subjective = db.Column(db.Text, nullable=True)  # Patient's reported symptoms
    objective = db.Column(db.Text, nullable=True)  # Observed findings
    assessment = db.Column(db.Text, nullable=False)  # Diagnosis
    plan = db.Column(db.Text, nullable=False)  # Treatment plan
    doctor_name = db.Column(db.String(100), nullable=False)
    requires_lab_tests = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LabRequest(db.Model):
    """Laboratory and radiology request model"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)  # 'laboratory' or 'radiology'
    test_name = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='routine')  # 'stat', 'urgent', 'routine'
    clinical_info = db.Column(db.Text, nullable=True)
    requested_by = db.Column(db.String(100), nullable=False)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Results
    is_completed = db.Column(db.Boolean, default=False)
    result = db.Column(db.Text, nullable=True)
    result_added_by = db.Column(db.String(100), nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # For automatic integration
    external_system_id = db.Column(db.String(100), nullable=True)
    is_auto_imported = db.Column(db.Boolean, default=False)

class Prescription(db.Model):
    """Medication prescription model"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    medication_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    route = db.Column(db.String(50), nullable=False)  # oral, IV, etc.
    frequency = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(50), nullable=True)
    special_instructions = db.Column(db.Text, nullable=True)
    prescribed_by = db.Column(db.String(100), nullable=False)
    prescribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_dispensed = db.Column(db.Boolean, default=False)
    dispensed_at = db.Column(db.DateTime, nullable=True)
    dispensed_by = db.Column(db.String(100), nullable=True)

class Disposition(db.Model):
    """Patient disposition/transfer model"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    disposition_type = db.Column(db.String(20), nullable=False)  # 'discharge', 'outpatient', 'inpatient', 'deceased'
    
    # For discharge
    discharge_instructions = db.Column(db.Text, nullable=True)
    follow_up_plan = db.Column(db.Text, nullable=True)
    
    # For outpatient referral
    clinic_referred_to = db.Column(db.String(100), nullable=True)
    appointment_date = db.Column(db.DateTime, nullable=True)
    
    # For inpatient transfer
    destination_ward = db.Column(db.String(50), nullable=True)
    bed_number = db.Column(db.String(20), nullable=True)
    is_bed_available = db.Column(db.Boolean, nullable=True)
    waiting_list_position = db.Column(db.Integer, nullable=True)
    
    # For deceased patients
    time_of_death = db.Column(db.DateTime, nullable=True)
    cause_of_death = db.Column(db.String(200), nullable=True)
    
    # Common fields
    authorized_by = db.Column(db.String(100), nullable=False)
    disposition_time = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)

class ExternalLabResult(db.Model):
    """Model for storing external lab system results for automatic integration"""
    id = db.Column(db.Integer, primary_key=True)
    external_system_id = db.Column(db.String(100), nullable=False, unique=True)
    patient_mrn = db.Column(db.String(20), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)  # 'laboratory' or 'radiology'
    test_name = db.Column(db.String(100), nullable=False)
    result = db.Column(db.Text, nullable=False)
    result_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_imported = db.Column(db.Boolean, default=False)
    lab_request_id = db.Column(db.Integer, nullable=True)  # Will be filled when imported
