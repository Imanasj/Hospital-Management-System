import pymysql

# ── Database connection settings ─────────────────────────────
HOST     = 'localhost'
USER     = 'root'
PASSWORD = 'root123'
DATABASE = 'hospitaldb'

# =============================================================
# CONNECTION
# =============================================================
def create_connection():

    connection = pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        db=DATABASE
    )
    return connection


def initialize_database():
    """Create all tables if they do not exist yet"""
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Patients (
            patient_id   INT AUTO_INCREMENT PRIMARY KEY,
            name         VARCHAR(100) NOT NULL,
            dob          DATE NOT NULL,
            health_card  VARCHAR(20) UNIQUE NOT NULL,
            phone        VARCHAR(20),
            email        VARCHAR(100),
            emergency_contact VARCHAR(100),
            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Appointments (
            appt_id      INT AUTO_INCREMENT PRIMARY KEY,
            patient_id   INT NOT NULL,
            doctor_name  VARCHAR(100) NOT NULL,
            appt_date    DATE NOT NULL,
            appt_time    TIME NOT NULL,
            department   VARCHAR(50) NOT NULL,
            reason       VARCHAR(255),
            urgency_level VARCHAR(20) DEFAULT 'Medium',
            status       VARCHAR(20) DEFAULT 'Scheduled',
            FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS MedicalRecords (
            record_id    INT AUTO_INCREMENT PRIMARY KEY,
            patient_id   INT NOT NULL,
            visit_date   DATETIME DEFAULT CURRENT_TIMESTAMP,
            diagnosis    TEXT,
            medications  TEXT,
            test_results TEXT,
            doctor_notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS WaitQueue (
            queue_id     INT AUTO_INCREMENT PRIMARY KEY,
            patient_id   INT NOT NULL,
            department   VARCHAR(50) NOT NULL,
            urgency_level VARCHAR(20) NOT NULL,
            check_in_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            estimated_wait_min INT,
            FOREIGN KEY (patient_id) REFERENCES Patients(patient_id)
        )
    """)

    connection.commit()
    connection.close()


# =============================================================
# PATIENTS CRUD
# =============================================================
def add_patient(name, dob, health_card, phone, email, emergency_contact=""):
    """INSERT a new patient record"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO Patients (name, dob, health_card, phone, email, emergency_contact)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (name, dob, health_card, phone, email, emergency_contact))
    connection.commit()
    patient_id = cursor.lastrowid
    connection.close()
    return patient_id


def get_all_patients():
    """SELECT all patients"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Patients ORDER BY registration_date DESC")
    rows = cursor.fetchall()
    connection.close()
    return rows


def get_patient_by_id(patient_id):
    """SELECT a single patient by ID"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Patients WHERE patient_id = %s", (patient_id,))
    row = cursor.fetchone()
    connection.close()
    return row


def search_patients(term):
    """SELECT patients matching name or health card"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM Patients
        WHERE name LIKE %s OR health_card LIKE %s
        ORDER BY name
    """, (f'%{term}%', f'%{term}%'))
    rows = cursor.fetchall()
    connection.close()
    return rows


def update_patient(patient_id, phone, email, emergency_contact):
    """UPDATE patient contact info"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE Patients SET phone=%s, email=%s, emergency_contact=%s
        WHERE patient_id=%s
    """, (phone, email, emergency_contact, patient_id))
    connection.commit()
    connection.close()


def delete_patient(patient_id):
    """DELETE a patient record"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Patients WHERE patient_id = %s", (patient_id,))
    connection.commit()
    connection.close()


def health_card_exists(health_card):
    """Check if health card is already registered"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Patients WHERE health_card = %s", (health_card,))
    count = cursor.fetchone()[0]
    connection.close()
    return count > 0


# =============================================================
# APPOINTMENTS CRUD
# =============================================================
def check_double_booking(doctor_name, appt_date, appt_time):
    """Return True if doctor is already booked at that date/time"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM Appointments
        WHERE doctor_name=%s AND appt_date=%s AND appt_time=%s
        AND status != 'Cancelled'
    """, (doctor_name, appt_date, appt_time))
    count = cursor.fetchone()[0]
    connection.close()
    return count > 0


def add_appointment(patient_id, doctor_name, appt_date, appt_time,
                    department, reason="", urgency="Medium"):
    """INSERT a new appointment (with double-booking check)"""
    if check_double_booking(doctor_name, appt_date, appt_time):
        raise ValueError(
            f"Double-booking! {doctor_name} already has an appointment at {appt_date} {appt_time}."
        )
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO Appointments
            (patient_id, doctor_name, appt_date, appt_time, department, reason, urgency_level)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (patient_id, doctor_name, appt_date, appt_time, department, reason, urgency))
    connection.commit()
    connection.close()


def get_all_appointments():
    """SELECT all appointments joined with patient name"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT a.appt_id, p.name, a.doctor_name, a.appt_date, a.appt_time,
               a.department, a.urgency_level, a.status, a.reason
        FROM Appointments a
        JOIN Patients p ON a.patient_id = p.patient_id
        ORDER BY a.appt_date, a.appt_time
    """)
    rows = cursor.fetchall()
    connection.close()
    return rows


def update_appointment_status(appt_id, status):
    """UPDATE appointment status"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE Appointments SET status=%s WHERE appt_id=%s", (status, appt_id))
    connection.commit()
    connection.close()


def cancel_appointment(appt_id):
    update_appointment_status(appt_id, 'Cancelled')


def delete_appointment(appt_id):
    """DELETE an appointment record"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Appointments WHERE appt_id = %s", (appt_id,))
    connection.commit()
    connection.close()


# =============================================================
# MEDICAL RECORDS CRUD
# =============================================================
def add_medical_record(patient_id, diagnosis, medications, test_results, doctor_notes=""):
    """INSERT a new medical record"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO MedicalRecords
            (patient_id, diagnosis, medications, test_results, doctor_notes)
        VALUES (%s, %s, %s, %s, %s)
    """, (patient_id, diagnosis, medications, test_results, doctor_notes))
    connection.commit()
    connection.close()


def get_records_by_patient(patient_id):
    """SELECT all medical records for a patient"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT record_id, visit_date, diagnosis, medications, test_results, doctor_notes
        FROM MedicalRecords
        WHERE patient_id = %s
        ORDER BY visit_date DESC
    """, (patient_id,))
    rows = cursor.fetchall()
    connection.close()
    return rows


def delete_medical_record(record_id):
    """DELETE a medical record"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM MedicalRecords WHERE record_id = %s", (record_id,))
    connection.commit()
    connection.close()


# =============================================================
# WAIT QUEUE CRUD
# =============================================================
def add_to_queue(patient_id, department, urgency, estimated_wait):
    """INSERT patient into wait queue"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO WaitQueue (patient_id, department, urgency_level, estimated_wait_min)
        VALUES (%s, %s, %s, %s)
    """, (patient_id, department, urgency, estimated_wait))
    connection.commit()
    connection.close()


def get_queue():
    """SELECT all patients in the queue sorted by urgency priority"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT w.queue_id, p.name, p.patient_id, w.department,
               w.urgency_level, w.check_in_time, w.estimated_wait_min
        FROM WaitQueue w
        JOIN Patients p ON w.patient_id = p.patient_id
        ORDER BY
            CASE w.urgency_level
                WHEN 'Critical' THEN 1
                WHEN 'High'     THEN 2
                WHEN 'Medium'   THEN 3
                WHEN 'Low'      THEN 4
            END,
            w.check_in_time
    """)
    rows = cursor.fetchall()
    connection.close()
    return rows


def remove_from_queue(queue_id):
    """DELETE patient from queue (discharged)"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM WaitQueue WHERE queue_id = %s", (queue_id,))
    connection.commit()
    connection.close()


def get_queue_count():
    """Return total number of patients in queue"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM WaitQueue")
    count = cursor.fetchone()[0]
    connection.close()
    return count
