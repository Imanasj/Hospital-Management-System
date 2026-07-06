import pymysql
from datetime import date

HOST     = 'localhost'
USER     = 'root'
PASSWORD = 'root123'
DATABASE = 'hospitaldb'

OVERLOAD_THRESHOLD = 10

def create_connection():
    return pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DATABASE)

def get_daily_patient_count():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM Patients
        WHERE DATE(registration_date) = %s
    """, (date.today(),))
    count = cursor.fetchone()[0]
    connection.close()
    return count

def calculate_avg_wait_time():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(estimated_wait_min) FROM WaitQueue")
    result = cursor.fetchone()[0]
    connection.close()
    return round(float(result), 1) if result else 0

def get_queue_count():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM WaitQueue")
    count = cursor.fetchone()[0]
    connection.close()
    return count

def get_total_appointments_today():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM Appointments
        WHERE DATE(appt_date) = %s
    """, (date.today(),))
    count = cursor.fetchone()[0]
    connection.close()
    return count

def check_department_overload(department, threshold=OVERLOAD_THRESHOLD):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM WaitQueue WHERE department = %s", (department,)
    )
    count = cursor.fetchone()[0]
    connection.close()
    return count >= threshold, count

def get_all_department_loads():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT department, COUNT(*) as cnt
        FROM WaitQueue GROUP BY department
    """)
    rows = cursor.fetchall()
    connection.close()
    return {r[0]: r[1] for r in rows}

def get_hourly_stats():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT HOUR(registration_date) as hr, COUNT(*) as cnt
        FROM Patients WHERE DATE(registration_date) = %s
        GROUP BY HOUR(registration_date) ORDER BY hr
    """, (date.today(),))
    rows = cursor.fetchall()
    connection.close()
    return {row[0]: row[1] for row in rows}

def get_urgency_breakdown():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT urgency_level, COUNT(*) as cnt
        FROM WaitQueue GROUP BY urgency_level
    """)
    rows = cursor.fetchall()
    connection.close()
    return {r[0]: r[1] for r in rows}

def get_appointments_by_department():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT department, COUNT(*) as cnt
        FROM Appointments
        WHERE status != 'Cancelled'
        GROUP BY department
    """)
    rows = cursor.fetchall()
    connection.close()
    return {r[0]: r[1] for r in rows}

def get_appointment_status_breakdown():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT status, COUNT(*) as cnt
        FROM Appointments
        GROUP BY status
    """)
    rows = cursor.fetchall()
    connection.close()
    return {r[0]: r[1] for r in rows}
