class MedicalRecord:
    def __init__(self, patient_id, diagnosis="", medications="", test_results="", doctor_notes=""):
        self.__patient_id = patient_id
        self.__diagnosis = diagnosis
        self.__medications = medications
        self.__test_results = test_results
        self.__doctor_notes = doctor_notes

    # Getters
    def get_patient_id(self):
        return self.__patient_id

    def get_diagnosis(self):
        return self.__diagnosis

    def get_medications(self):
        return self.__medications

    def get_test_results(self):
        return self.__test_results

    def get_doctor_notes(self):
        return self.__doctor_notes

    # Setters
    def updateRecord(self, diagnosis, medications, test_results, doctor_notes=""):
        self.__diagnosis = diagnosis
        self.__medications = medications
        self.__test_results = test_results
        self.__doctor_notes = doctor_notes

    def printRecordInfo(self):
        print(f"Diagnosis:    {self.__diagnosis}")
        print(f"Medications:  {self.__medications}")
        print(f"Test Results: {self.__test_results}")
        print(f"Doctor Notes: {self.__doctor_notes}")