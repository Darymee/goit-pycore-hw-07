from collections import UserDict
from datetime import datetime, timedelta
import re


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        self.value = self.validate_number(value)
        super().__init__(value)

    @staticmethod
    def validate_number(value):
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError("Phone number must contain only numbers and 10 digits.")
        return value

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")     
        super().__init__(self.value)   

    def __str__(self):
        return self.value.strftime("%d.%m.%Y") 

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        if phone_number in [p.value for p in self.phones]:
            print(f"Phone number {phone_number} already exists.")
            return
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)
                break
        print(f"{phone_number} not found in list.")

    def edit_phone(self, old_number, new_number):
        if not old_number or not new_number:
            return print("Phone numbers cannot be empty.")

        for phone in self.phones:
            if phone.value == old_number:
                self.phones.remove(phone)
                self.phones.append(Phone(new_number))
                return "Phone updated."
        print(f"{old_number} not found in list.")

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        print(f"{phone_number} not found in list.")


    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday if self.birthday else 'no information'}"


class AddressBook(UserDict):
    def add_record(self, record):
        if not self.data.get(record.name.value):
            self.data[record.name.value] = record
            return
        print(f"Record {record.name.value} already exists.")

    def find(self, name):
        return self.data.get(name, print(f"Record {name} not found."))

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return
        print(f"Record {name} not found.")


    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.today().date() 

        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value.date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1) # birthday was already this year 
        
                if today <= birthday_this_year <= today + timedelta(days=7): # check if birthday is next week
                    if birthday_this_year.weekday() == 5:  # if birthday on Saturday 
                        birthday_this_year += timedelta(days=2)  
                    elif birthday_this_year.weekday() == 6: # if birthday on Sunday
                        birthday_this_year += timedelta(days=1) 
            
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": birthday_this_year.strftime("%d.%m.%Y")
                    })
    
        return upcoming_birthdays


# Створення нової адресної книги
book = AddressBook()

# Створення запису для John
john_record = Record("John")
john_record.add_phone("1234567890")
john_record.add_phone("5555555555")
john_record.add_birthday("29.03.1993")

# Додавання запису John до адресної книги
book.add_record(john_record)

# Створення та додавання нового запису для Jane
jane_record = Record("Jane")
jane_record.add_phone("9876543210")
book.add_record(jane_record)

# Виведення всіх записів у книзі
for name, record in book.data.items():
    print(record)

# Знаходження та редагування телефону для John
john = book.find("John")
john.edit_phone("1234567890", "1112223333")

print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

# Пошук конкретного телефону у записі John
found_phone = john.find_phone("5555555555")
if found_phone:
    print(f"{john.name}: {found_phone}")  # Якщо знайдено, виведе номер
else:
    print("Phone number not found")  # Якщо немає такого номера, не буде помилки

# Видалення запису Jane
book.delete("Jane")

# Виведення всіх записів у книзі після видалення Jane
for name, record in book.data.items():
    print(record)

# Видалення неіснуючого запису
book.delete("Anna")  # Виведення: Record Anna not found.

# Пошук неіснуючого запису
book.find("Anna")  # Виведення: Record Anna not found.

# Пошук не існуючого номеру
john.find_phone("5555555556")  # Виведення: 5555555556 not found in list.

# Спроба змінити номер на порожнє значення
john.edit_phone("", "")  # Виведення: Phone numbers cannot be empty.


for birthday in book.get_upcoming_birthdays():
    print(birthday)