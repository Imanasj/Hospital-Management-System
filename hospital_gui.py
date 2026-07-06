import sys
from datetime import date, datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QTextEdit, QComboBox, QGridLayout, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QMenuBar, QMessageBox, QFrame, QSizePolicy, QScrollArea,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QAction

from patient_module      import Patient
from appointment_module  import Appointment
from medical_record_module import MedicalRecord
import database_module   as db
import analytics_module  as an

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ── Constants ─────────────────────────────────────────────────
DEPARTMENTS    = ["Cardiology", "Emergency", "General Practice",
                  "Neurology", "Orthopedics", "Pediatrics"]
URGENCY_LEVELS = ["Critical", "High", "Medium", "Low"]
DOCTORS = {
    "Cardiology":       ["Dr. Patel",    "Dr. Chen"],
    "Emergency":        ["Dr. Martinez", "Dr. Thompson"],
    "General Practice": ["Dr. Smith",    "Dr. Lee"],
    "Neurology":        ["Dr. Johnson",  "Dr. Kim"],
    "Orthopedics":      ["Dr. Williams", "Dr. Davis"],
    "Pediatrics":       ["Dr. Wilson",   "Dr. Garcia"],
}

# ── Colour palette (refined "clinical navy" theme) ─────────────
BG_DARK  = "#0b1220"   # app background - deep slate navy
BG_CARD  = "#121a2b"   # card / panel surface
BG_PANEL = "#0f1729"   # header / table-header surface
BORDER   = "#23304a"   # hairline borders
BLUE     = "#2563eb"   # primary accent - deep professional blue
BLUE2    = "#5b9dff"   # hover / highlight accent
ACCENT   = "#7dd3fc"   # cool cyan accent for titles
GREEN    = "#22c55e"
AMBER    = "#f5a524"
RED      = "#f43f5e"
TEAL     = "#2dd4bf"
TEXT     = "#eef2f8"
TSUB     = "#8a96ad"   # muted secondary text

URGENCY_COLORS = {"Critical": RED, "High": AMBER, "Medium": BLUE, "Low": GREEN}

STYLESHEET = f"""
QMainWindow, QDialog, QWidget {{
    background-color: {BG_DARK};
    color: {TEXT};
    font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial;
    font-size: 13px;
}}
QLabel {{
    color: {TEXT};
}}
QLineEdit, QComboBox, QTextEdit {{
    background-color: #0e1626;
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 11px;
    font-size: 13px;
    selection-background-color: {BLUE};
}}
QLineEdit:hover, QComboBox:hover, QTextEdit:hover {{
    border: 1px solid #344563;
}}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
    border: 1px solid {BLUE2};
}}
QComboBox::drop-down {{
    border: none;
    width: 22px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    selection-background-color: {BLUE};
    outline: none;
}}
QPushButton {{
    background-color: {BLUE};
    color: #f8fafc;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.2px;
}}
QPushButton:hover  {{ background-color: {BLUE2}; }}
QPushButton:pressed {{ background-color: #1d4ed8; }}
QPushButton#resetBtn {{
    background-color: transparent;
    color: {TSUB};
    border: 1px solid {BORDER};
    font-weight: 500;
}}
QPushButton#resetBtn:hover {{ background-color: #18233a; color: {TEXT}; border: 1px solid #344563; }}
QPushButton#greenBtn  {{ background-color: {GREEN}; color: #04130c; }}
QPushButton#greenBtn:hover  {{ background-color: #34d076; }}
QPushButton#redBtn    {{ background-color: transparent; color: {RED}; border: 1px solid #5a2230; }}
QPushButton#redBtn:hover    {{ background-color: #2a1420; }}
QPushButton#amberBtn  {{ background-color: {AMBER}; color: #1a1304; }}
QPushButton#amberBtn:hover  {{ background-color: #ffb84d; }}
QPushButton#accentBtn {{
    background-color: #16243d;
    color: {BLUE2};
    border: 1px solid #2c4670;
    font-weight: 600;
}}
QPushButton#accentBtn:hover {{ background-color: #1c2e4d; border: 1px solid {BLUE2}; }}
QPushButton#navBtn {{
    background-color: {BG_CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    font-weight: 600;
}}
QPushButton#navBtn:hover {{ background-color: #18233a; border: 1px solid #344563; }}
QFrame#titleStrip {{
    background-color: {BG_PANEL};
    border-bottom: 1px solid {BORDER};
}}
QTableWidget {{
    background-color: {BG_CARD};
    alternate-background-color: #0f1827;
    color: {TEXT};
    gridline-color: {BORDER};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
QTableWidget::item {{
    padding: 6px 4px;
    border-bottom: 1px solid {BORDER};
}}
QTableWidget::item:selected {{
    background-color: #1d4ed8;
    color: #ffffff;
}}
QHeaderView::section {{
    background-color: {BG_PANEL};
    color: {TSUB};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 9px 6px;
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}}
QMenuBar {{
    background-color: {BG_PANEL};
    color: {TEXT};
    border-bottom: 1px solid {BORDER};
    padding: 4px 8px;
    font-weight: 500;
}}
QMenuBar::item {{
    padding: 6px 14px;
    border-radius: 5px;
    margin: 2px;
}}
QMenuBar::item:selected {{ background-color: {BLUE}; color: #ffffff; }}
QMenu {{
    background-color: {BG_CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 24px;
    border-radius: 4px;
}}
QMenu::item:selected {{ background-color: {BLUE}; }}
QScrollArea {{ border: none; }}
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: #344563; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QFrame#card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}
QFrame#separator {{
    background-color: {BORDER};
    max-height: 1px;
}}
QMessageBox {{
    background-color: {BG_CARD};
}}
"""

# =============================================================
# PATIENT WINDOW  (multi-window - )
# =============================================================
class PatientWindow(QWidget):
    """Pop-up window: full CRUD for Patients """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Patient Registration")
        self.setMinimumSize(900, 620)
        self.setStyleSheet(STYLESHEET)
        self._build()
        self._load_table()

    def _build(self):
        # ── Main QHBoxLayout ─────────────────────────────────
        main = QHBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # ── LEFT: QGridLayout form (Lab 4 pattern) ───────────
        form_card = QFrame(); form_card.setObjectName("card")
        grid = QGridLayout(form_card)
        grid.setSpacing(10); grid.setContentsMargins(20, 20, 20, 20)

        title = QLabel("New Patient"); title.setFont(QFont("Segoe UI Semibold", 14))
        title.setStyleSheet(f"color:{BLUE2};"); grid.addWidget(title, 0, 0, 1, 2)

        labels = ["Full Name *", "Date of Birth (YYYY-MM-DD) *",
                  "Health Card Number *", "Phone Number",
                  "Email Address", "Emergency Contact"]
        self.fields = {}
        keys = ["name", "dob", "hc", "phone", "email", "emerg"]
        for i, (lbl, key) in enumerate(zip(labels, keys), start=1):
            grid.addWidget(QLabel(lbl), i, 0)
            e = QLineEdit(); grid.addWidget(e, i, 1); self.fields[key] = e

        self.err_lbl = QLabel(""); self.err_lbl.setStyleSheet(f"color:{RED};")
        self.err_lbl.setWordWrap(True); grid.addWidget(self.err_lbl, 7, 0, 1, 2)

        btn_row = QHBoxLayout()
        save_btn  = QPushButton("Save Patient"); save_btn.setObjectName("greenBtn")
        clear_btn = QPushButton("Reset");         clear_btn.setObjectName("resetBtn")
        save_btn.clicked.connect(self._save)
        clear_btn.clicked.connect(self._clear)
        btn_row.addWidget(save_btn); btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        grid.addLayout(btn_row, 8, 0, 1, 2)
        form_card.setMaximumWidth(380)
        main.addWidget(form_card)

        # ── RIGHT: QVBoxLayout list (Lab 4 pattern) ──────────
        list_card = QFrame(); list_card.setObjectName("card")
        vbox = QVBoxLayout(list_card)
        vbox.setContentsMargins(16, 16, 16, 16); vbox.setSpacing(10)

        hdr = QHBoxLayout()
        lbl = QLabel("All Patients"); lbl.setFont(QFont("Segoe UI Semibold", 12))
        self.search_box = QLineEdit(); self.search_box.setPlaceholderText("Search name or health card...")
        self.search_box.textChanged.connect(self._search)
        hdr.addWidget(lbl); hdr.addStretch(); hdr.addWidget(self.search_box)
        vbox.addLayout(hdr)

        self.table = self._make_table(
            ["ID", "Name", "DOB", "Health Card", "Phone", "Email"],
            [50, 160, 95, 120, 110, 160]
        )
        self.table.itemSelectionChanged.connect(self._on_select)
        vbox.addWidget(self.table)

        # CRUD buttons row
        btn2 = QHBoxLayout()
        self.del_btn = QPushButton("Delete Selected"); self.del_btn.setObjectName("redBtn")
        ref_btn = QPushButton("Refresh"); ref_btn.setObjectName("resetBtn")
        self.del_btn.clicked.connect(self._delete)
        ref_btn.clicked.connect(self._load_table)
        btn2.addWidget(self.del_btn); btn2.addWidget(ref_btn); btn2.addStretch()
        vbox.addLayout(btn2)

        # QTextEdit for patient list display (Lab 5 pattern)
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setMaximumHeight(120)
        self.text_display.setPlaceholderText("Select a patient to view full details.")
        vbox.addWidget(QLabel("Patient Details:"))
        vbox.addWidget(self.text_display)

        main.addWidget(list_card)

    # ── Helpers ───────────────────────────────────────────────
    def _make_table(self, headers, widths):
        t = QTableWidget(); t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        t.verticalHeader().setVisible(False)
        t.horizontalHeader().setStretchLastSection(True)
        for i, w in enumerate(widths): t.setColumnWidth(i, w)
        return t

    def _load_table(self, data=None):
        rows = data or db.get_all_patients()
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row[:6]):
                self.table.setItem(r, c, QTableWidgetItem(str(val) if val else ""))

    def _search(self, text):
        if text.strip():
            self._load_table(db.search_patients(text.strip()))
        else:
            self._load_table()

    def _on_select(self):
        row = self.table.currentRow()
        if row < 0: return
        vals = [self.table.item(row, c).text() for c in range(self.table.columnCount())]
        pid, name, dob, hc, phone, email = vals
        pat = Patient(name, dob, hc, phone, email)
        self.text_display.setHtml(
            f"<b style='color:{BLUE2}'>Patient List - ID {pid}</b><br>"
            f"{pid} // {name} // {dob} // HC: {hc}<br>"
            f"Phone: {phone} | Email: {email}"
        )

    def _save(self):
        self.err_lbl.setText("")
        n  = self.fields["name"].text().strip()
        d  = self.fields["dob"].text().strip()
        hc = self.fields["hc"].text().strip()
        ph = self.fields["phone"].text().strip()
        em = self.fields["email"].text().strip()
        eg = self.fields["emerg"].text().strip()
        if not n:  self.err_lbl.setText("Full name is required."); return
        if not d:  self.err_lbl.setText("Date of birth is required."); return
        if not hc: self.err_lbl.setText("Health card is required."); return
        if db.health_card_exists(hc):
            self.err_lbl.setText("Health card already registered."); return
        try:
            # Instantiate Patient object (Lab 4/5 pattern)
            pat = Patient(n, d, hc, ph, em, eg)
            pid = db.add_patient(
                pat.get_name(), pat.get_dob(), pat.get_health_card(),
                pat.get_phone(), pat.get_email(), pat.get_emergency_contact()
            )
            pat.printPatientInfo()   # Print to console (Lab pattern)
            QMessageBox.information(self, "Success", f"Patient saved! ID: {pid}")
            self._clear(); self._load_table()
        except Exception as ex:
            self.err_lbl.setText(str(ex))

    def _delete(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Select a patient to delete."); return
        pid = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Delete patient ID {pid}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db.delete_patient(pid)
            QMessageBox.information(self, "Deleted", "Patient record deleted.")
            self._load_table()

    def _clear(self):
        for e in self.fields.values(): e.clear()
        self.err_lbl.setText("")


# =============================================================
# APPOINTMENT WINDOW  (multi-window)
# =============================================================
class AppointmentWindow(QWidget):
    """Pop-up window: Appointment scheduling with CRUD"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Appointment Scheduler")
        self.setMinimumSize(1000, 640)
        self.setStyleSheet(STYLESHEET)
        self._build()
        self._load_table()

    def _build(self):
        main = QHBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20); main.setSpacing(16)

        # ── LEFT FORM (QGridLayout) ───────────────────────────
        form_card = QFrame(); form_card.setObjectName("card")
        grid = QGridLayout(form_card)
        grid.setSpacing(10); grid.setContentsMargins(20, 20, 20, 20)

        title = QLabel("New Appointment"); title.setFont(QFont("Segoe UI Semibold", 14))
        title.setStyleSheet(f"color:{BLUE2};"); grid.addWidget(title, 0, 0, 1, 2)

        self.pid_e   = QLineEdit(); grid.addWidget(QLabel("Patient ID *"), 1, 0); grid.addWidget(self.pid_e, 1, 1)
        self.dept_cb = QComboBox(); self.dept_cb.addItems(DEPARTMENTS)
        grid.addWidget(QLabel("Department *"), 2, 0); grid.addWidget(self.dept_cb, 2, 1)
        self.doc_cb  = QComboBox()
        grid.addWidget(QLabel("Doctor *"), 3, 0); grid.addWidget(self.doc_cb, 3, 1)
        self.dept_cb.currentTextChanged.connect(self._update_doctors); self._update_doctors()
        self.date_e  = QLineEdit(date.today().strftime("%Y-%m-%d"))
        grid.addWidget(QLabel("Date (YYYY-MM-DD) *"), 4, 0); grid.addWidget(self.date_e, 4, 1)
        self.time_e  = QLineEdit("09:00")
        grid.addWidget(QLabel("Time (HH:MM) *"), 5, 0); grid.addWidget(self.time_e, 5, 1)
        self.urg_cb  = QComboBox(); self.urg_cb.addItems(URGENCY_LEVELS)
        grid.addWidget(QLabel("Urgency Level"), 6, 0); grid.addWidget(self.urg_cb, 6, 1)
        self.reason_e = QLineEdit()
        grid.addWidget(QLabel("Reason"), 7, 0); grid.addWidget(self.reason_e, 7, 1)

        self.err_lbl = QLabel(""); self.err_lbl.setStyleSheet(f"color:{RED};")
        self.err_lbl.setWordWrap(True); grid.addWidget(self.err_lbl, 8, 0, 1, 2)

        btn_row = QHBoxLayout()
        book_btn  = QPushButton("Book Appointment")
        reset_btn = QPushButton("Reset"); reset_btn.setObjectName("resetBtn")
        book_btn.clicked.connect(self._book)
        reset_btn.clicked.connect(self._clear)
        btn_row.addWidget(book_btn); btn_row.addWidget(reset_btn); btn_row.addStretch()
        grid.addLayout(btn_row, 9, 0, 1, 2)
        form_card.setMaximumWidth(380); main.addWidget(form_card)

        # ── RIGHT LIST (QVBoxLayout) ──────────────────────────
        list_card = QFrame(); list_card.setObjectName("card")
        vbox = QVBoxLayout(list_card)
        vbox.setContentsMargins(16, 16, 16, 16); vbox.setSpacing(10)
        lbl = QLabel("All Appointments"); lbl.setFont(QFont("Segoe UI Semibold", 12))
        vbox.addWidget(lbl)
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Patient", "Doctor", "Date", "Time", "Dept", "Urgency", "Status"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        for i, w in enumerate([40, 130, 110, 90, 60, 110, 70, 80]):
            self.table.setColumnWidth(i, w)
        vbox.addWidget(self.table)

        btn2 = QHBoxLayout()
        done_btn   = QPushButton("Complete"); done_btn.setObjectName("greenBtn")
        cancel_btn = QPushButton("✕ Cancel");   cancel_btn.setObjectName("redBtn")
        del_btn    = QPushButton("Delete");      del_btn.setObjectName("redBtn")
        ref_btn    = QPushButton("Refresh");     ref_btn.setObjectName("resetBtn")
        done_btn.clicked.connect(self._complete)
        cancel_btn.clicked.connect(self._cancel)
        del_btn.clicked.connect(self._delete)
        ref_btn.clicked.connect(self._load_table)
        for b in [done_btn, cancel_btn, del_btn, ref_btn]: btn2.addWidget(b)
        btn2.addStretch(); vbox.addLayout(btn2)

        # QTextEdit display (Lab 5 pattern)
        self.text_display = QTextEdit(); self.text_display.setReadOnly(True)
        self.text_display.setMaximumHeight(110)
        vbox.addWidget(QLabel("Appointment List:")); vbox.addWidget(self.text_display)
        main.addWidget(list_card)

    def _update_doctors(self):
        self.doc_cb.clear()
        self.doc_cb.addItems(DOCTORS.get(self.dept_cb.currentText(), []))

    def _load_table(self):
        rows = db.get_all_appointments()
        self.table.setRowCount(len(rows))
        uc = {"Critical": RED, "High": AMBER, "Medium": BLUE, "Low": GREEN}
        all_text = ""
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val) if val else "")
                if c == 6:   # Urgency color
                    item.setForeground(QColor(uc.get(str(val), TEXT)))
                if c == 7 and str(val) == "Cancelled":
                    item.setForeground(QColor(TSUB))
                self.table.setItem(r, c, item)
            all_text += f"All Appointment Records: ({row[0]}, '{row[1]}', {row[2]}, {row[3]}, {row[4]})->Status:{row[7]}\n"
        self.text_display.setPlainText(all_text)

    def _book(self):
        self.err_lbl.setText("")
        try:   pid = int(self.pid_e.text().strip())
        except: self.err_lbl.setText("Patient ID must be a number."); return
        d2 = self.date_e.text().strip(); t2 = self.time_e.text().strip()
        dept = self.dept_cb.currentText(); doc = self.doc_cb.currentText()
        urg = self.urg_cb.currentText(); reason = self.reason_e.text().strip()
        try:
            # Instantiate Appointment object (Lab 4/5 pattern)
            appt = Appointment(pid, doc, d2, t2, dept, urg, reason)
            queue_size = db.get_queue_count()
            wait = appt.calculateWaitTime(queue_size)
            db.add_appointment(pid, appt.get_doctor(), appt.get_date(),
                               appt.get_time(), appt.get_department(), reason, urg)
            db.add_to_queue(pid, dept, urg, wait)
            appt.printAppointmentInfo()  # Print to console
            QMessageBox.information(self, "Booked",
                f"Appointment booked!\nEstimated wait: ~{wait} min")
            self._clear(); self._load_table()
        except ValueError as ve:
            self.err_lbl.setText(str(ve))
        except Exception as ex:
            self.err_lbl.setText(str(ex))

    def _complete(self):
        row = self.table.currentRow()
        if row < 0: QMessageBox.warning(self, "Warning", "Select an appointment."); return
        aid = int(self.table.item(row, 0).text())
        db.update_appointment_status(aid, "Completed")
        QMessageBox.information(self, "Done", "Marked as Completed.")
        self._load_table()

    def _cancel(self):
        row = self.table.currentRow()
        if row < 0: QMessageBox.warning(self, "Warning", "Select an appointment."); return
        aid = int(self.table.item(row, 0).text())
        r = QMessageBox.question(self, "Confirm", "Cancel this appointment?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            db.cancel_appointment(aid); self._load_table()

    def _delete(self):
        row = self.table.currentRow()
        if row < 0: QMessageBox.warning(self, "Warning", "Select an appointment."); return
        aid = int(self.table.item(row, 0).text())
        r = QMessageBox.question(self, "Confirm Delete", f"Delete appointment ID {aid}?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            db.delete_appointment(aid); self._load_table()

    def _clear(self):
        self.pid_e.clear(); self.reason_e.clear()
        self.date_e.setText(date.today().strftime("%Y-%m-%d"))
        self.time_e.setText("09:00"); self.err_lbl.setText("")


# =============================================================
# MEDICAL RECORDS WINDOW  (multi-window)
# =============================================================
class MedicalRecordsWindow(QWidget):
    """Pop-up window: Medical Records CRUD"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical Records")
        self.setMinimumSize(900, 580)
        self.setStyleSheet(STYLESHEET)
        self._build()

    def _build(self):
        main = QHBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20); main.setSpacing(16)

        # ── LEFT FORM (QGridLayout) ───────────────────────────
        form_card = QFrame(); form_card.setObjectName("card")
        grid = QGridLayout(form_card)
        grid.setSpacing(10); grid.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Add Medical Record")
        title.setFont(QFont("Segoe UI Semibold", 14))
        title.setStyleSheet(f"color:{BLUE2};"); grid.addWidget(title, 0, 0, 1, 2)

        self.pid_e   = QLineEdit(); grid.addWidget(QLabel("Patient ID *"), 1, 0); grid.addWidget(self.pid_e, 1, 1)
        self.diag_e  = QLineEdit(); grid.addWidget(QLabel("Diagnosis *"), 2, 0);  grid.addWidget(self.diag_e, 2, 1)
        self.meds_e  = QLineEdit(); grid.addWidget(QLabel("Medications"), 3, 0);  grid.addWidget(self.meds_e, 3, 1)
        self.tests_e = QLineEdit(); grid.addWidget(QLabel("Test Results"), 4, 0); grid.addWidget(self.tests_e, 4, 1)
        grid.addWidget(QLabel("Doctor Notes"), 5, 0)
        self.notes_e = QTextEdit(); self.notes_e.setMaximumHeight(80)
        grid.addWidget(self.notes_e, 5, 1)

        self.err_lbl = QLabel(""); self.err_lbl.setStyleSheet(f"color:{RED};")
        grid.addWidget(self.err_lbl, 6, 0, 1, 2)

        btn_row = QHBoxLayout()
        save_btn  = QPushButton("Save Record"); save_btn.setObjectName("greenBtn")
        clear_btn = QPushButton("Reset");        clear_btn.setObjectName("resetBtn")
        save_btn.clicked.connect(self._save)
        clear_btn.clicked.connect(self._clear)
        btn_row.addWidget(save_btn); btn_row.addWidget(clear_btn); btn_row.addStretch()
        grid.addLayout(btn_row, 7, 0, 1, 2)

        lkp_lbl = QLabel("Lookup by Patient ID:")
        self.lkp_e  = QLineEdit()
        load_btn    = QPushButton("Load Records")
        load_btn.clicked.connect(self._load_records)
        del_btn     = QPushButton("Delete Record"); del_btn.setObjectName("redBtn")
        del_btn.clicked.connect(self._delete)
        grid.addWidget(lkp_lbl, 8, 0); grid.addWidget(self.lkp_e, 8, 1)
        btn2 = QHBoxLayout()
        btn2.addWidget(load_btn); btn2.addWidget(del_btn)
        grid.addLayout(btn2, 9, 0, 1, 2)
        form_card.setMaximumWidth(380); main.addWidget(form_card)

        # ── RIGHT (QVBoxLayout) ───────────────────────────────
        right_card = QFrame(); right_card.setObjectName("card")
        vbox = QVBoxLayout(right_card)
        vbox.setContentsMargins(16, 16, 16, 16); vbox.setSpacing(10)

        self.rec_table = QTableWidget()
        self.rec_table.setColumnCount(6)
        self.rec_table.setHorizontalHeaderLabels(
            ["ID", "Visit Date", "Diagnosis", "Medications", "Tests", "Notes"])
        self.rec_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.rec_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.rec_table.verticalHeader().setVisible(False)
        self.rec_table.horizontalHeader().setStretchLastSection(True)
        for i, w in enumerate([40, 130, 140, 120, 120, 140]):
            self.rec_table.setColumnWidth(i, w)
        vbox.addWidget(QLabel("Patient Records:"))
        vbox.addWidget(self.rec_table)

        # QTextEdit display (Lab 5 pattern)
        self.text_display = QTextEdit(); self.text_display.setReadOnly(True)
        vbox.addWidget(QLabel("Medical Records List:")); vbox.addWidget(self.text_display)
        main.addWidget(right_card)

    def _save(self):
        self.err_lbl.setText("")
        try:   pid = int(self.pid_e.text().strip())
        except: self.err_lbl.setText("Patient ID must be a number."); return
        diag = self.diag_e.text().strip()
        if not diag: self.err_lbl.setText("Diagnosis is required."); return
        try:

            rec = MedicalRecord(pid, diag, self.meds_e.text().strip(),
                                self.tests_e.text().strip(),
                                self.notes_e.toPlainText().strip())
            db.add_medical_record(pid, rec.get_diagnosis(), rec.get_medications(),
                                  rec.get_test_results(), rec.get_doctor_notes())
            rec.printRecordInfo()  # Print to console
            QMessageBox.information(self, "Saved", "Medical record saved!")
            self._clear()
        except Exception as ex:
            self.err_lbl.setText(str(ex))

    def _load_records(self):
        try:   pid = int(self.lkp_e.text().strip())
        except: QMessageBox.warning(self, "Warning", "Enter a valid Patient ID."); return
        rows = db.get_records_by_patient(pid)
        self.rec_table.setRowCount(len(rows))
        all_text = ""
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.rec_table.setItem(r, c, QTableWidgetItem(str(val) if val else ""))
            all_text += (f"All Medical Records: ({row[0]}, Patient {pid}, '{row[2]}',"
                         f" Meds:{row[3]})->Visit:{row[1]}\n")
        self.text_display.setPlainText(all_text if all_text else "No records found.")

    def _delete(self):
        row = self.rec_table.currentRow()
        if row < 0: QMessageBox.warning(self, "Warning", "Select a record."); return
        rid = int(self.rec_table.item(row, 0).text())
        r = QMessageBox.question(self, "Confirm", f"Delete record ID {rid}?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            db.delete_medical_record(rid)
            try: pid = int(self.lkp_e.text().strip())
            except: pid = None
            if pid: self._load_records()

    def _clear(self):
        self.pid_e.clear(); self.diag_e.clear()
        self.meds_e.clear(); self.tests_e.clear()
        self.notes_e.clear(); self.err_lbl.setText("")


# =============================================================
# ANALYTICS WINDOW  (multi-window -)
# =============================================================
class AnalyticsWindow(QWidget):
    """Pop-up: Daily Analytics Dashboard + Overload Alerts"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analytics Dashboard")
        self.setMinimumSize(780, 580)
        self.setStyleSheet(STYLESHEET)
        self._build()
        self._load()

    def _build(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(20, 20, 20, 20); vbox.setSpacing(14)

        title = QLabel("Daily Analytics Dashboard")
        title.setFont(QFont("Segoe UI Semibold", 16))
        title.setStyleSheet(f"color:{BLUE2};"); vbox.addWidget(title)

        # Stat row (QGridLayout inside QHBoxLayout)
        stat_row = QHBoxLayout()
        self.stat_labels = {}
        for key, lbl_text, color in [
            ("patients",     "Patients Today",     BLUE),
            ("appointments", "Appointments Today",  TEAL),
            ("queue",        "In Queue Now",        AMBER),
            ("avg_wait",     "Avg Wait (min)",      GREEN),
        ]:
            card = QFrame(); card.setObjectName("card")
            g = QGridLayout(card); g.setContentsMargins(16, 14, 16, 14)
            lbl = QLabel(lbl_text); lbl.setStyleSheet(f"color:{TSUB}; font-size:11px;")
            val = QLabel("-"); val.setFont(QFont("Segoe UI Semibold", 22))
            val.setStyleSheet(f"color:{color};")
            g.addWidget(lbl, 0, 0); g.addWidget(val, 1, 0)
            self.stat_labels[key] = val
            stat_row.addWidget(card)
        vbox.addLayout(stat_row)

        # Overload alerts text area
        vbox.addWidget(QLabel("Department Overload Alerts:"))
        self.alert_display = QTextEdit(); self.alert_display.setReadOnly(True)
        self.alert_display.setMaximumHeight(110)
        vbox.addWidget(self.alert_display)

        self.figure = Figure(figsize=(8, 4), facecolor=BG_CARD)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(260)
        vbox.addWidget(self.canvas)

        # All records display (Lab 5 QTextEdit pattern)
        vbox.addWidget(QLabel("All Analytics Records:"))
        self.text_display = QTextEdit(); self.text_display.setReadOnly(True)
        vbox.addWidget(self.text_display)

        ref_btn = QPushButton("↺  Refresh Analytics"); ref_btn.setObjectName("resetBtn")
        ref_btn.clicked.connect(self._load); vbox.addWidget(ref_btn)

    def _draw_charts(self, loads, urgency, appointments):
        self.figure.clear()
        ax1 = self.figure.add_subplot(131)
        ax2 = self.figure.add_subplot(132)
        ax3 = self.figure.add_subplot(133)

        for ax in (ax1, ax2, ax3):
            ax.set_facecolor(BG_CARD)
            ax.tick_params(colors=TEXT, labelsize=8)
            for spine in ax.spines.values():
                spine.set_color(BORDER)

        dept_labels = list(loads.keys()) or ["No Queue"]
        dept_values = list(loads.values()) or [0]
        ax1.bar(dept_labels, dept_values, color=BLUE2)
        ax1.set_title("Queue by Department", color=TEXT, fontsize=10)
        ax1.tick_params(axis="x", rotation=45)

        urg_labels = list(urgency.keys()) or ["No Queue"]
        urg_values = list(urgency.values()) or [1]
        urg_colors = [URGENCY_COLORS.get(u, TEAL) for u in urg_labels]
        ax2.pie(urg_values, labels=urg_labels, autopct="%1.0f%%",
                colors=urg_colors, textprops={"color": TEXT, "fontsize": 8})
        ax2.set_title("Urgency Mix", color=TEXT, fontsize=10)

        appt_labels = list(appointments.keys()) or ["No Appointments"]
        appt_values = list(appointments.values()) or [0]
        ax3.barh(appt_labels, appt_values, color=TEAL)
        ax3.set_title("Appointments by Department", color=TEXT, fontsize=10)

        self.figure.tight_layout()
        self.canvas.draw()

    def _load(self):
        # Update stat cards
        self.stat_labels["patients"].setText(str(an.get_daily_patient_count()))
        self.stat_labels["appointments"].setText(str(an.get_total_appointments_today()))
        self.stat_labels["queue"].setText(str(an.get_queue_count()))
        self.stat_labels["avg_wait"].setText(str(an.calculate_avg_wait_time()))

        # Overload alerts
        loads = an.get_all_department_loads()
        alerts = [(d, n) for d, n in loads.items() if n >= 10]
        if alerts:
            alert_text = ""
            for dept, count in alerts:
                alert_text += f"{dept}: {count} patients - OVERLOADED (threshold: 10)\n"
            self.alert_display.setStyleSheet(f"color:{RED};")
            self.alert_display.setPlainText(alert_text)
        else:
            self.alert_display.setStyleSheet(f"color:{GREEN};")
            self.alert_display.setPlainText("All departments are within capacity.")

        # Full stats text (Lab 5 QTextEdit display pattern)
        hourly = an.get_hourly_stats()
        urgency = an.get_urgency_breakdown()
        appt_depts = an.get_appointments_by_department()
        self._draw_charts(loads, urgency, appt_depts)
        text = f"All Average Records: Avg Wait = {an.calculate_avg_wait_time()} min\n\n"
        text += "Hourly Patient Arrivals:\n"
        for hr, cnt in sorted(hourly.items()):
            text += f"  {hr}:00 → {cnt} patients\n"
        text += "\nUrgency Breakdown:\n"
        for urg in URGENCY_LEVELS:
            text += f"  {urg}: {urgency.get(urg, 0)} patients\n"
        text += "\nDepartment Loads:\n"
        for dept in DEPARTMENTS:
            cnt = loads.get(dept, 0)
            flag = " OVERLOADED" if cnt >= 10 else ""
            text += f"  {dept}: {cnt} patients{flag}\n"
        text += "\nAppointments by Department:\n"
        for dept in DEPARTMENTS:
            text += f"  {dept}: {appt_depts.get(dept, 0)} appointments\n"
        self.text_display.setPlainText(text)


# =============================================================
# WAIT QUEUE WINDOW  (multi-window)
# =============================================================
class QueueWindow(QWidget):
    """Pop-up: Live Wait Queue with discharge"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Wait Queue")
        self.setMinimumSize(820, 520)
        self.setStyleSheet(STYLESHEET)
        self._build()
        self._load()

    def _build(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(20, 20, 20, 20); vbox.setSpacing(12)

        title = QLabel("Live Wait Queue - Sorted by Priority")
        title.setFont(QFont("Segoe UI Semibold", 15))
        title.setStyleSheet(f"color:{BLUE2};"); vbox.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Queue ID", "Patient", "Patient ID", "Department", "Urgency", "Check-In", "Est. Wait"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        vbox.addWidget(self.table)

        btn_row = QHBoxLayout()
        dis_btn = QPushButton("Discharge Selected"); dis_btn.setObjectName("amberBtn")
        ref_btn = QPushButton("Refresh");            ref_btn.setObjectName("resetBtn")
        dis_btn.clicked.connect(self._discharge)
        ref_btn.clicked.connect(self._load)
        btn_row.addWidget(dis_btn); btn_row.addWidget(ref_btn); btn_row.addStretch()
        vbox.addLayout(btn_row)

        # QTextEdit list (Lab 5 pattern)
        self.text_display = QTextEdit(); self.text_display.setReadOnly(True)
        self.text_display.setMaximumHeight(130)
        vbox.addWidget(QLabel("Queue Records:")); vbox.addWidget(self.text_display)

    def _load(self):
        rows = db.get_queue()
        self.table.setRowCount(len(rows))
        all_text = ""
        for r, row in enumerate(rows):
            qid, name, pid, dept, urg, checkin, wait = row
            vals = [qid, name, pid, dept, urg, str(checkin)[11:16] if checkin else "-", f"~{wait} min"]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                if c == 4:
                    item.setForeground(QColor(URGENCY_COLORS.get(urg, TEXT)))
                self.table.setItem(r, c, item)
            all_text += (f"All Queue Records: ({qid}, '{name}', {dept},"
                         f" {urg})->Wait:{wait} min\n")
        self.text_display.setPlainText(all_text if all_text else "Queue is empty.")

    def _discharge(self):
        row = self.table.currentRow()
        if row < 0: QMessageBox.warning(self, "Warning", "Select a patient."); return
        qid = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        r = QMessageBox.question(self, "Discharge", f"Discharge {name}?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            db.remove_from_queue(qid)
            QMessageBox.information(self, "Done", f"{name} discharged.")
            self._load()


# =============================================================
# MAIN WINDOW  (QMainWindow with QMenuBar)
# =============================================================
class MainWindow(QMainWindow):


    def __init__(self):
        super().__init__()
        self.setWindowTitle("MediCore - Hospital Management System")
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(STYLESHEET)

        # Keep references to open windows so they stay alive
        self._patient_win    = None
        self._appt_win       = None
        self._records_win    = None
        self._analytics_win  = None
        self._queue_win      = None

        self._build_menu()
        self._build_dashboard()

        # Auto-refresh timer (innovative feature)
        self.timer = QTimer()
        self.timer.timeout.connect(self._refresh_stats)
        self.timer.start(30000)  # refresh every 30 seconds

    # ── Menu Bar (Lab 5 pattern) ──────────────────────────────
    def _build_menu(self):
        menubar = self.menuBar()

        # Patients menu
        pat_menu = menubar.addMenu("Patients")
        act_reg = QAction("Patient Registration", self)
        act_reg.triggered.connect(self._open_patients)
        pat_menu.addAction(act_reg)

        # Appointments menu
        appt_menu = menubar.addMenu("Appointments")
        act_appt = QAction("Appointment Scheduler", self)
        act_appt.triggered.connect(self._open_appointments)
        appt_menu.addAction(act_appt)

        # Medical Records menu
        rec_menu = menubar.addMenu("Medical Records")
        act_rec = QAction("View / Add Records", self)
        act_rec.triggered.connect(self._open_records)
        rec_menu.addAction(act_rec)

        # Queue menu
        queue_menu = menubar.addMenu("Wait Queue")
        act_queue = QAction("Live Queue", self)
        act_queue.triggered.connect(self._open_queue)
        queue_menu.addAction(act_queue)

        # Analytics menu
        an_menu = menubar.addMenu("Analytics")
        act_an = QAction("Analytics Dashboard", self)
        act_an.triggered.connect(self._open_analytics)
        an_menu.addAction(act_an)

    # ── Dashboard (QGridLayout + QVBoxLayout - Lab 4 pattern) ─
    def _build_dashboard(self):
        central = QWidget(); self.setCentralWidget(central)
        outer_vbox = QVBoxLayout(central)
        outer_vbox.setContentsMargins(0, 0, 0, 0); outer_vbox.setSpacing(0)

        # ── Top title strip ───────────────────────────────────
        strip = QFrame(); strip.setObjectName("titleStrip")
        strip_h = QHBoxLayout(strip)
        strip_h.setContentsMargins(32, 12, 32, 12)
        brand_row = QHBoxLayout(); brand_row.setSpacing(10)
        brand_ico = QLabel("✚"); brand_ico.setStyleSheet(f"font-size:16px; font-weight:bold; color:{BLUE2};")
        brand_lbl = QLabel("MediCore HMS"); brand_lbl.setFont(QFont("Segoe UI Semibold", 14))
        brand_row.addWidget(brand_ico); brand_row.addWidget(brand_lbl)
        strip_h.addLayout(brand_row)
        strip_h.addStretch()
        date_lbl = QLabel(date.today().strftime("%A, %B %d, %Y"))
        date_lbl.setStyleSheet(f"color:{TSUB}; font-size:12.5px;")
        strip_h.addWidget(date_lbl)
        outer_vbox.addWidget(strip)

        # ── Page body ──────────────────────────────────────────
        body = QWidget()
        main_vbox = QVBoxLayout(body)
        main_vbox.setContentsMargins(32, 24, 32, 24); main_vbox.setSpacing(18)
        outer_vbox.addWidget(body)

        # Title
        title_lbl = QLabel("Welcome back")
        title_lbl.setFont(QFont("Segoe UI Semibold", 24))
        title_lbl.setStyleSheet(f"color:{TEXT}; letter-spacing: 0.5px;")
        main_vbox.addWidget(title_lbl)

        # ── Stat cards row (QGridLayout) ─────────────────────
        stat_grid = QGridLayout(); stat_grid.setSpacing(12)
        self.stat_labels = {}
        stats_meta = [
            ("patients",     "Patients Today",      BLUE,  "●", 0, 0),
            ("appointments", "Appointments Today",   TEAL,  "▦", 0, 1),
            ("queue",        "In Queue Now",         AMBER, "▷", 0, 2),
            ("avg_wait",     "Avg Wait (min)",       GREEN, "◔", 0, 3),
        ]
        for key, lbl_text, color, icon, row, col in stats_meta:
            card = QFrame(); card.setObjectName("card")
            card.setMinimumHeight(78)
            h = QHBoxLayout(card); h.setContentsMargins(18, 14, 18, 14); h.setSpacing(14)
            ico = QLabel(icon); ico.setStyleSheet(f"font-size:20px; color:{color};")
            ico.setFixedWidth(24); ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
            h.addWidget(ico)
            text_col = QVBoxLayout(); text_col.setSpacing(2)
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet(f"color:{TSUB}; font-size:11px; font-weight:600; letter-spacing:0.6px; text-transform:uppercase;")
            val = QLabel("-"); val.setFont(QFont("Segoe UI Semibold", 22))
            val.setStyleSheet(f"color:{TEXT};")
            text_col.addWidget(lbl); text_col.addWidget(val)
            h.addLayout(text_col)
            self.stat_labels[key] = val
            stat_grid.addWidget(card, row, col)
        main_vbox.addLayout(stat_grid)

        # ── Navigation buttons (QGridLayout - Lab 4 pattern) ──
        nav_lbl = QLabel("QUICK ACCESS")
        nav_lbl.setStyleSheet(f"color:{TSUB}; font-size:11px; font-weight:600; letter-spacing:1.2px; margin-top: 6px;")
        main_vbox.addWidget(nav_lbl)
        nav_grid = QGridLayout(); nav_grid.setSpacing(12)
        nav_items = [
            ("Patient Registration", self._open_patients,    "accentBtn", 0, 0),
            ("Appointments",         self._open_appointments, "accentBtn", 0, 1),
            ("Medical Records",      self._open_records,      None,        0, 2),
            ("Live Queue",           self._open_queue,        None,        1, 0),
            ("Analytics Dashboard",  self._open_analytics,    None,        1, 1),
        ]
        for text, cmd, obj_name, row, col in nav_items:
            btn = QPushButton(text); btn.setMinimumHeight(58)
            btn.setStyleSheet("font-size: 13.5px;")
            if obj_name: btn.setObjectName(obj_name)
            else: btn.setObjectName("navBtn")
            btn.clicked.connect(cmd)
            nav_grid.addWidget(btn, row, col)
        main_vbox.addLayout(nav_grid)

        # ── QTextEdit display for live queue summary ──────────
        queue_lbl = QLabel("LIVE QUEUE - REAL-TIME WAIT TIMES")
        queue_lbl.setStyleSheet(f"color:{TSUB}; font-size:11px; font-weight:600; letter-spacing:1.2px; margin-top: 6px;")
        main_vbox.addWidget(queue_lbl)
        self.queue_display = QTextEdit(); self.queue_display.setReadOnly(True)
        self.queue_display.setMaximumHeight(160)
        main_vbox.addWidget(self.queue_display)

        # ── Alert area ────────────────────────────────────────
        self.alert_lbl = QLabel("")
        self.alert_lbl.setStyleSheet(f"color:{RED}; font-weight:bold;")
        self.alert_lbl.setWordWrap(True)
        main_vbox.addWidget(self.alert_lbl)

        self._refresh_stats()

    def _refresh_stats(self):
        """Update stat cards and queue display"""
        try:
            self.stat_labels["patients"].setText(str(an.get_daily_patient_count()))
            self.stat_labels["appointments"].setText(str(an.get_total_appointments_today()))
            self.stat_labels["queue"].setText(str(an.get_queue_count()))
            self.stat_labels["avg_wait"].setText(str(an.calculate_avg_wait_time()))

            # Queue summary in QTextEdit (Lab 5 pattern)
            queue_rows = db.get_queue()
            if queue_rows:
                text = ""
                total_wait = 0
                for row in queue_rows:
                    qid, name, pid, dept, urg, checkin, wait = row
                    total_wait += wait if wait else 0
                    text += (f"All Queue Records: ({qid}, '{name}', {dept},"
                             f" {urg})->Wait:{wait} min\n")
                text += f"\nAll Wait Records: {total_wait} min total"
                self.queue_display.setPlainText(text)
            else:
                self.queue_display.setPlainText("Queue is empty.")

            # Overload alerts (innovative feature)
            loads = an.get_all_department_loads()
            alerts = [(d, n) for d, n in loads.items() if n >= 10]
            if alerts:
                msg = "OVERLOAD ALERT: " + ", ".join(
                    f"{d} ({n} patients)" for d, n in alerts)
                self.alert_lbl.setText(msg)
            else:
                self.alert_lbl.setText("")
        except Exception:
            pass  # DB not connected yet - no crash

    # ── Window openers ────────────────────────────────────────
    def _open_patients(self):
        self._patient_win = PatientWindow(); self._patient_win.show()

    def _open_appointments(self):
        self._appt_win = AppointmentWindow(); self._appt_win.show()

    def _open_records(self):
        self._records_win = MedicalRecordsWindow(); self._records_win.show()

    def _open_analytics(self):
        self._analytics_win = AnalyticsWindow(); self._analytics_win.show()

    def _open_queue(self):
        self._queue_win = QueueWindow(); self._queue_win.show()


# =============================================================
# ENTRY POINT
# =============================================================
def main():
    db.initialize_database()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()

