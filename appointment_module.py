class Appointment:
    def __init__(self, patient_id, doctor, appt_date, appt_time,
                 department, urgency="Medium", reason=""):
        self.__patient_id    = patient_id
        self.__doctor        = doctor
        self.__appt_date     = appt_date
        self.__appt_time     = appt_time
        self.__department    = department
        self.__urgency_level = urgency
        self.__reason        = reason
        self.__status        = "Scheduled"

    # ── Getters ──────────────────────────────────────────────
    def get_patient_id(self):    return self.__patient_id
    def get_doctor(self):        return self.__doctor
    def get_date(self):          return self.__appt_date
    def get_time(self):          return self.__appt_time
    def get_department(self):    return self.__department
    def get_urgency(self):       return self.__urgency_level
    def get_status(self):        return self.__status
    def get_reason(self):        return self.__reason

    # ── Setters ──────────────────────────────────────────────
    def set_status(self, status):    self.__status = status
    def set_urgency(self, urgency):  self.__urgency_level = urgency

    # ── Wait time calculation (innovative feature) ────────────
    def calculateWaitTime(self, queue_size):
        base_time = {'Critical': 5, 'High': 15, 'Medium': 30, 'Low': 45}
        if self.__urgency_level not in base_time:
            return 30 * queue_size
        return base_time[self.__urgency_level] * queue_size

    # ── Print method ─────────────────────────────────────────
    def printAppointmentInfo(self):
        print(f"Doctor:     {self.__doctor}")
        print(f"Date:       {self.__appt_date}  Time: {self.__appt_time}")
        print(f"Department: {self.__department}")
        print(f"Urgency:    {self.__urgency_level}")
        print(f"Status:     {self.__status}")