from collections import UserDict
from datetime import datetime, timedelta
import re


class InvalidValue(Exception):
    pass

class NumberIsNotFound(Exception):
    pass

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError):
            error_messages = {
                "add_contact": "Give me name and phone please.",
                "change_contact": "Give me name, old phone, and new phone please.",
                "show_phone": "Give me name please.",
                "add_birthday": "Give me name please and birthday date.",
                "show_birthday": "Give me name please.",
            }
            return error_messages.get(func.__name__, "Missing required parameters.")
        except KeyError:
            return "Contact is not found."
        except NumberIsNotFound:
            return "Number is not found."           
        except InvalidValue as e:
            return str(e)

    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


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
            raise InvalidValue(
                "Invalid number. It must contain only numbers and 10 digits."
            )
        return value


class Birthday(Field):
    def __init__(self, value):
        try:
            date_value = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(date_value)
        except ValueError:
            raise InvalidValue("Invalid date format. Use DD.MM.YYYY")

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
        raise NumberIsNotFound()

    def edit_phone(self, old_number, new_number):
        for phone in self.phones:
            if phone.value == old_number:
                phone.value = Phone.validate_number(new_number)
                return "Phone updated."
        raise NumberIsNotFound()

    def find_phone(self, phone_number):
        for phone in self.phones:
                if phone.value == phone_number:
                    return phone
        raise NumberIsNotFound()

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        return self.birthday if self.birthday else "no information"

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday if self.birthday else 'no information'}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return "Record deleted."
        return KeyError()

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.today().date()

        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value 
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                if (
                    today <= birthday_this_year <= today + timedelta(days=7)
                ): 
                    if birthday_this_year.weekday() == 5:  
                        birthday_this_year += timedelta(days=2)
                    elif birthday_this_year.weekday() == 6:
                        birthday_this_year += timedelta(days=1)

                    upcoming_birthdays.append(
                        {
                            "name": record.name.value,
                            "congratulation_date": birthday_this_year.strftime("%d.%m.%Y"),
                        }
                    )

        return upcoming_birthdays if upcoming_birthdays else "No upcoming birthdays."



@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if not record:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)

    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact changed."

    raise KeyError()


@input_error
def show_phone(args, book):
    (name,) = args
    record = book.find(name)
    if record is None:
        raise KeyError()
    return f"{record}"


def show_all(book):
    return (
        "\n".join(str(record) for record in book.data.values())
        if book.data
        else "No contacts found."
    )


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        message = "Birthday added."
        if record.birthday:
            message = "Birthday updated."
        record.add_birthday(birthday)
        return message
    raise KeyError()


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return record.show_birthday()
    else:
        raise KeyError()


def birthdays(_, book):
    upcoming = book.get_upcoming_birthdays()
    if isinstance(upcoming, str):
        return upcoming
    return [f"{birthday['name']} - {birthday['congratulation_date']}" for birthday in upcoming]


def show_commands():
    commands = [
        "hello",
        "add [name] [phone]",
        "change [name] [old phone] [new phone]",
        "phone [name]",
        "all",
        "add-birthday [name] [DD.MM.YYYY]",
        "show-birthday [name]",
        "birthdays",
        "commands",
        "close or exit",
    ]
    return "Available commands:\n 👉 " + "\n 👉 ".join(commands)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!🤖")
    print(show_commands())
    while True:
        user_input = input("Enter a command:")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        elif command == "commands":
            print(show_commands())    

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
