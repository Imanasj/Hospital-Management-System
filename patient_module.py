class Patient:
    def __init__(self, name, dob, health_card, phone, email, emergency_contact=""):
        self.__name = name
        self.__dob = dob
        self.__health_card = health_card
        self.__phone = phone
        self.__email = email
        self.__emergency_contact = emergency_contact

    # Getters
    def get_name(self):
        return self.__name

    def get_dob(self):
        return self.__dob

    def get_health_card(self):
        return self.__health_card

    def get_phone(self):
        return self.__phone

    def get_email(self):
        return self.__email

    def get_emergency_contact(self):
        return self.__emergency_contact

    # Setters
    def set_name(self, name):
        self.__name = name

    def set_phone(self, phone):
        self.__phone = phone

    def set_email(self, email):
        self.__email = email

    def set_emergency_contact(self, ec):
        self.__emergency_contact = ec

    def printPatientInfo(self):
        print(f"Name: {self.__name}")
        print(f"DOB: {self.__dob}")
        print(f"Health Card: {self.__health_card}")
        print(f"Phone: {self.__phone}")
        print(f"Email: {self.__email}")