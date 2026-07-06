# Hospital Management System  
A PyQt6 desktop application connected to a MySQL database that manages patients, appointments, medical records, and the wait queue. The system provides full CRUD operations across all modules and includes a live Analytics Dashboard powered by matplotlib.

## Features
- **Multi‑window PyQt6 interface** (Patients, Appointments, Medical Records, Wait Queue, Analytics)
- **MySQL‑backed CRUD** for all four hospitaldb tables  
- **Live analytics dashboard** with embedded matplotlib charts:
  - Patients waiting per department  
  - Urgency‑level mix  
  - Appointments per department  
- **New business‑process queries**  
  - `get_appointments_by_department()`  
  - `get_appointment_status_breakdown()`  
- **Wait Queue refresh‑timing fix documented for next phase**

## Tech Stack
- Python 3.11  
- PyQt6  
- MySQL + pymysql  
- matplotlib  

## Setup
1. Create the database:  
   `CREATE DATABASE hospitaldb;`
2. Install dependencies:  
   `pip install PyQt6 pymysql matplotlib`
3. Update MySQL credentials in `database_module.py` and `analytics_module.py`
4. Run tests:  
   `python test_main.py`
5. Launch the app:  
   `python hospital_gui.py`

## Project Structure
- `hospital_gui.py` — main GUI + 5 windows  
- `analytics_module.py` — analytics queries + chart data  
- `database_module.py` — CRUD operations  
- `patient_module.py`, `appointment_module.py`, `medical_record_module.py`  
- `test_main.py` — regression + analytics tests  


patient_module.py, appointment_module.py, medical_record_module.py

test_main.py — regression + analytics tests
