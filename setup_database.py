from app import app, db
from models import User, Patient, Triage
from datetime import datetime, timedelta
import random

def setup_test_data():
    """Create test users and some basic data for testing"""
    with app.app_context():
        print("Creating test data...")
        
        # Create test user if it doesn't exist
        if not User.query.filter_by(username='nurse1').first():
            test_user = User(
                username='nurse1',
                email='nurse1@example.com',
                full_name='Test Nurse',
                role='nurse'
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.commit()
            print("Created test user: nurse1/password123")
        else:
            print("Test user already exists")
            
        # Create test patient if there are no patients
        if Patient.query.count() == 0:
            for i in range(5):
                patient = Patient(
                    first_name=f"Patient{i+1}",
                    last_name=f"Test{i+1}",
                    date_of_birth=datetime.now() - timedelta(days=365*random.randint(20, 80)),
                    gender=random.choice(['Male', 'Female']),
                    arrival_mode=random.choice(['ambulance', 'walk-in']),
                    medical_record_number=f"MRN{1000+i}"
                )
                db.session.add(patient)
            db.session.commit()
            print("Created 5 test patients")
            
            # Create triage for a couple of patients
            triage_categories = ['red', 'yellow', 'green', 'black']
            for i in range(1, 3):
                patient = Patient.query.get(i)
                if patient and not Triage.query.filter_by(patient_id=patient.id).first():
                    triage = Triage(
                        patient_id=patient.id,
                        category=random.choice(triage_categories),
                        reason="Test triage reason",
                        vital_signs={
                            'temperature': '37.0',
                            'heart_rate': '80',
                            'respiratory_rate': '16',
                            'blood_pressure': '120/80',
                            'oxygen_saturation': '98',
                            'pain_level': '2'
                        },
                        triaged_by=1,  # Assuming user ID 1 exists
                        triaged_at=datetime.now() - timedelta(hours=random.randint(1, 24))
                    )
                    db.session.add(triage)
            db.session.commit()
            print("Created triage for test patients")
        
        print("Test data setup complete!")

if __name__ == "__main__":
    setup_test_data()