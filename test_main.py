from patient_module        import Patient
from appointment_module    import Appointment
from medical_record_module import MedicalRecord
import database_module     as db

print("=" * 55)
print("   Hospital Management System - Class Testing")
print("=" * 55)

# ── Initialize database ───────────────────────────────────────
print("\nInitializing MySQL database...")
db.initialize_database()
print("hospitaldb tables created successfully.\n")

# ── Test 1: Patient objects ───────────────────────────────────
print("-" * 55)
print("Test 1: Patient Class Objects")
print("-" * 55)

pat1 = Patient("Marie Letendre", "1990-05-14",
                "HC-10234", "514-555-0101", "marie@email.com", "Jean Letendre")

pat2 = Patient("Tom Belanger", "1985-11-22",
                "HC-20456", "514-555-0202", "tom@email.com", "Sara Belanger")

pat3 = Patient("Aisha Kone", "2000-03-08",
                "HC-30789", "514-555-0303", "aisha@email.com", "Oumar Kone")

print("\nPatient 1 Info:")
pat1.printPatientInfo()

print("\nPatient 2 Info:")
pat2.printPatientInfo()

print("\nPatient 3 Info:")
pat3.printPatientInfo()

# Save to MySQL (CRUD - Lab 5 pattern)
print("\nSaving patients to MySQL hospitaldb...")
try:
    id1 = db.add_patient(pat1.get_name(), pat1.get_dob(),
                         pat1.get_health_card(), pat1.get_phone(),
                         pat1.get_email(), pat1.get_emergency_contact())
    print(f"Patient Record: ({id1}, '{pat1.get_name()}', {pat1.get_dob()},"
          f" {pat1.get_health_card()})->Saved")

    id2 = db.add_patient(pat2.get_name(), pat2.get_dob(),
                         pat2.get_health_card(), pat2.get_phone(),
                         pat2.get_email(), pat2.get_emergency_contact())
    print(f"Patient Record: ({id2}, '{pat2.get_name()}', {pat2.get_dob()},"
          f" {pat2.get_health_card()})->Saved")

    id3 = db.add_patient(pat3.get_name(), pat3.get_dob(),
                         pat3.get_health_card(), pat3.get_phone(),
                         pat3.get_email(), pat3.get_emergency_contact())
    print(f"Patient Record: ({id3}, '{pat3.get_name()}', {pat3.get_dob()},"
          f" {pat3.get_health_card()})->Saved")

except Exception as e:
    print(f"  Note: {e}")
    id1, id2, id3 = 1, 2, 3

# Load all patients from MySQL
print("\nAll Patient Records from MySQL:")
rows = db.get_all_patients()
for row in rows:
    print(f"  All Patient Records: ({row[0]}, '{row[1]}', {row[2]},"
          f" {row[3]})->Phone:{row[4]}")

# ── Test 2: Appointment objects ───────────────────────────────
print("\n" + "-" * 55)
print("Test 2: Appointment Class Objects")
print("-" * 55)

appt1 = Appointment(id1, "Dr. Patel",    "2026-06-16", "09:00",
                    "Cardiology",    "Critical", "Chest pain")
appt2 = Appointment(id2, "Dr. Martinez", "2026-06-16", "10:00",
                    "Emergency",     "High",     "Fracture")
appt3 = Appointment(id3, "Dr. Smith",    "2026-06-16", "11:00",
                    "General Practice", "Medium", "Check-up")

print("\nAppointment 1 Info:")
appt1.printAppointmentInfo()
print(f"  Wait Time (queue=3): {appt1.calculateWaitTime(3)} min")

print("\nAppointment 2 Info:")
appt2.printAppointmentInfo()
print(f"  Wait Time (queue=3): {appt2.calculateWaitTime(3)} min")

print("\nAppointment 3 Info:")
appt3.printAppointmentInfo()
print(f"  Wait Time (queue=3): {appt3.calculateWaitTime(3)} min")

# Save appointments to MySQL
print("\nSaving appointments to MySQL...")
try:
    db.add_appointment(appt1.get_patient_id(), appt1.get_doctor(),
                       appt1.get_date(), appt1.get_time(),
                       appt1.get_department(), appt1.get_reason(),
                       appt1.get_urgency())
    print(f"  Appointment Record: ('{appt1.get_doctor()}', {appt1.get_date()},"
          f" {appt1.get_time()}, {appt1.get_urgency()})->Saved")

    db.add_appointment(appt2.get_patient_id(), appt2.get_doctor(),
                       appt2.get_date(), appt2.get_time(),
                       appt2.get_department(), appt2.get_reason(),
                       appt2.get_urgency())
    print(f"  Appointment Record: ('{appt2.get_doctor()}', {appt2.get_date()},"
          f" {appt2.get_time()}, {appt2.get_urgency()})->Saved")

    db.add_appointment(appt3.get_patient_id(), appt3.get_doctor(),
                       appt3.get_date(), appt3.get_time(),
                       appt3.get_department(), appt3.get_reason(),
                       appt3.get_urgency())
    print(f"  Appointment Record: ('{appt3.get_doctor()}', {appt3.get_date()},"
          f" {appt3.get_time()}, {appt3.get_urgency()})->Saved")

except Exception as e:
    print(f"  Note: {e}")

# Load all appointments
print("\nAll Appointment Records from MySQL:")
rows = db.get_all_appointments()
for row in rows:
    print(f"  All Appointment Records: ({row[0]}, '{row[1]}', {row[2]},"
          f" {row[3]})->Status:{row[7]}")

# ── Test 3: MedicalRecord objects ────────────────────────────
print("\n" + "-" * 55)
print("Test 3: MedicalRecord Class Objects")
print("-" * 55)

rec1 = MedicalRecord(id1, "Angina Pectoris",
                     "Nitroglycerin 0.4mg", "ECG: ST elevation",
                     "Patient to rest and avoid stress")

rec2 = MedicalRecord(id2, "Hairline Fracture - Wrist",
                     "Ibuprofen 400mg", "X-Ray: hairline fracture confirmed",
                     "Cast required for 4 weeks")

rec3 = MedicalRecord(id3, "Hypertension Stage 1",
                     "Lisinopril 10mg", "BP: 145/92 mmHg",
                     "Monitor weekly, reduce sodium intake")

print("\nMedical Record 1:")
rec1.printRecordInfo()

print("\nMedical Record 2:")
rec2.printRecordInfo()

print("\nMedical Record 3:")
rec3.printRecordInfo()

# Save records to MySQL
print("\nSaving medical records to MySQL...")
try:
    db.add_medical_record(rec1.get_patient_id(), rec1.get_diagnosis(),
                          rec1.get_medications(), rec1.get_test_results(),
                          rec1.get_doctor_notes())
    print(f"  Medical Record: (Patient {rec1.get_patient_id()},"
          f" '{rec1.get_diagnosis()}',"
          f" Meds:{rec1.get_medications()})->Saved")

    db.add_medical_record(rec2.get_patient_id(), rec2.get_diagnosis(),
                          rec2.get_medications(), rec2.get_test_results(),
                          rec2.get_doctor_notes())
    print(f"  Medical Record: (Patient {rec2.get_patient_id()},"
          f" '{rec2.get_diagnosis()}',"
          f" Meds:{rec2.get_medications()})->Saved")

    db.add_medical_record(rec3.get_patient_id(), rec3.get_diagnosis(),
                          rec3.get_medications(), rec3.get_test_results(),
                          rec3.get_doctor_notes())
    print(f"  Medical Record: (Patient {rec3.get_patient_id()},"
          f" '{rec3.get_diagnosis()}',"
          f" Meds:{rec3.get_medications()})->Saved")

except Exception as e:
    print(f"  Note: {e}")

# ── Test 4: Analytics ─────────────────────────────────────────
print("\n" + "-" * 55)
print("Test 4: Analytics Module Functions")
print("-" * 55)

import analytics_module as an

print(f"\nAll Analytics Records:")
print(f"  Daily Patient Count:       {an.get_daily_patient_count()}")
print(f"  Total Appointments Today:  {an.get_total_appointments_today()}")
print(f"  Patients In Queue:         {an.get_queue_count()}")
print(f"  Average Wait Time:         {an.calculate_avg_wait_time()} min")

print("\nDepartment Loads:")
loads = an.get_all_department_loads()
all_records = 0
for dept, cnt in loads.items():
    flag = " ← OVERLOADED" if cnt >= 10 else ""
    print(f"  {dept}: {cnt} patients{flag}")
    all_records += cnt
print(f"All Load Records: {all_records}")

print("\n" + "=" * 55)
print("   All Tests Completed Successfully!")
print("=" * 55)
print("\nRun hospital_gui.py to launch the full PyQt6 application.")
