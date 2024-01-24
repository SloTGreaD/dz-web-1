from collections import UserDict
from datetime import datetime
from pickle import dump, load
from os import path

from rich.console import Console
from rich.table import Table
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from abc import ABC, abstractmethod

from dop2 import Field
from dop2 import Name
from dop2 import Phone
from dop2 import Email
from dop2 import Birthday
from dop2 import Address
from dop2 import Notes
from dop2 import NoteManager
from dop2 import AddressBookIterator


# Отримання поточного каталогу, в якому знаходиться виконуваний файл
CURRENT_DIRECTORY = path.dirname(path.realpath(__file__))

# Створення повного шляху до файлу "address_book.pkl" в поточному каталозі
FILENAME = path.join(CURRENT_DIRECTORY, 'address_book.pkl')

class UserInterface(ABC):
    @abstractmethod
    def display_contacts(self, contacts):
        pass

    @abstractmethod
    def display_notes(self, notes):
        pass

    @abstractmethod
    def display_commands(self, commands):
        pass

class ConsoleUserInterface(UserInterface):
    def display_contacts(self, contacts):
        print('\nAddress book')

        if not contacts:
            print("Книга порожня.\n")
            return 

        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Contact name", style="magenta", width=20, justify="center")
        table.add_column("Phones", style="cyan", width=40, justify="center")
        table.add_column("Birthday", style="green", width=20, justify="center")
        table.add_column("Address", style="yellow", width=40, justify="center")
        table.add_column("Email", style="red", width=40, justify="center")

        for name, record in contacts.items():
            table.add_row(
                str(record.name.value),
                "; ".join(str(phone.value) for phone in record.phones),
                str(record.birthday) if isinstance(record.birthday, Birthday) else "",
                str(record.address.value) if record.address else "",
                str(record.email.value) if record.email else "",
            )

        console.print(table)
        print()


    def display_notes(self, notes):
        print("Notes:")
        for i, note in enumerate(notes, start=1):
            print(f"{i}. {note}")
        print()

    def display_commands(self, commands):
        print('''All commands:
        - add-contact [name] - add contact with it's name
        - edit-contact       - editing contact information
        - delete-contact     - deleting contact
        - all-contacts       - displays all contacts in the address book
        - upcoming-birthdays - display a list of contacts whose birthday is a specified number of days from the current date
        - add-note           - add a note
        - exit               - enter 'exit' to exit the Assistant
        ''')

class NoteManager:
    def __init__(self):
        self.notes = []

    def add_note(self, text):
        note = Notes(text)
        self.notes.append(note)

    def print_notes(self, ui):
        ui.display_notes(self.notes)

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        self.value = value

class Phone(Field):
    def __init__(self, value):
        if not self.is_valid_phone(value):
            raise ValueError("Invalid phone number format")
        super().__init__(value)

    @staticmethod
    def is_valid_phone(value):
        return len(value) == 10 and value.isdigit()

    def __str__(self):
        return str(self.value)

class Email(Field):
    def __init__(self, value):
        if not self.is_valid_email(value):
            raise ValueError('Invalid email format')
        super().__init__(value)

    @staticmethod
    def is_valid_email(value):
        return '@' in value

    def __str__(self):
        return str(self.value)

class Birthday(Field):
    def __init__(self, value):
        # Убедимся, что value - это объект datetime
        if not isinstance(value, datetime):
            raise ValueError("Invalid birthday format. Use a datetime object.")
        super().__init__(value)
    
    

class Address(Field):
    def __init__(self, value):
        super().__init__(value)

class Notes:
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.email = None
        self.birthday = None
        self.address = Address(None)
        self.notes = []

    def add_phone(self, phone):
        phone = Phone(phone)
        self.phones.append(phone)

    def add_email(self, email):
        email = Email(email)
        self.email = email

    def edit_phone(self, old_phone, new_phone):
        found = False
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                found = True
                break

        if not found:
            raise ValueError(f"Phone {old_phone} not found in the record")

    def edit_email(self, new_email):
        if not Email.is_valid_email(new_email):
            raise ValueError('Invalid email format')
        self.email.value = new_email

    def set_birthday(self, birthday):
        # Преобразуйте строку в объект datetime перед созданием Birthday
        try:
            birthday_datetime = datetime.strptime(birthday,"%Y-%m-%d").date()
            self.birthday = Birthday(birthday_datetime)
        except ValueError:
            raise ValueError("Invalid birthday date format. Use YYYY-MM-DD.")

    def __str__(self):
        contact_info = f"Contact name: {self.name.value}"
        if self.phones:
            contact_info += f", phones: {'; '.join(p.value for p in self.phones)}"
        if self.email is not None:
            contact_info += f", email: {self.email.value}"
        if self.birthday:
            contact_info += f", birthday: {self.birthday.strftime('%Y-%m-%d')}"
        if self.address:
            contact_info += f", address: {self.address.value}"
        if self.notes:
            contact_info += f" \nNotes: \n "
            for i, note in enumerate(self.notes, start=1):
                contact_info += f"{i}.{note}\n"
        return contact_info
    
    def set_address(self, address):
        self.address.value = address


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.notes_manager = NoteManager()

    def add_note(self, text):
        self.notes_manager.add_note(text)

    def print_notes(self, ui):
        self.notes_manager.print_notes(ui)

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def __iter__(self):
        return AddressBookIterator(self, items_per_page=5)

    def save_to_file(self, filename):
        with open(filename, "wb") as file:
            dump(self.data, file)

    def load_from_file(self, filename):
        with open(filename, "rb") as file:
            self.data = load(file)

    def search(self, query):
        results = []
        try:
            int(query[0])
        except Exception:
            for name, record in self.data.items():
                if query.lower() in name.lower():
                    results.append(record)
        else:
            for name, record in self.data.items():
                for phone in record.phones:
                    if query.lower() in phone.value.lower():
                        results.append(record)
        finally:
            return results


class AddressBookIterator:
    def __init__(self, address_book, items_per_page):
        self.address_book = address_book
        self.items_per_page = items_per_page
        self.current_page = 0

    def __iter__(self):
        return self

    def __next__(self):
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        records = list(self.address_book.data.values())[start:end]

        if not records:
            raise StopIteration

        self.current_page += 1
        return records


def main():
    book = load_book(FILENAME)

    print("Hi! I am Santa's Personal Assistant - Mr.Corgi. How can I help you?")

    commands = ['add-contact', 'all-contacts', 'edit-contact', 'delete-contact', 'upcoming-birthdays', 'add-note', 'exit']
    completer = WordCompleter(commands, ignore_case=True)

    ui = ConsoleUserInterface()

    command = prompt('Write a command (help - all commands): ', completer=completer)

    while command != 'exit':
        words_commands = command.split()

        if command == 'help':
            ui.display_commands(commands)

        elif words_commands[0] == 'add-contact':
            while len(words_commands) < 2:
                command = input('Enter command "add-contact [name]": ')
                words_commands = command.split()
            fun_add_contact(book, words_commands[1])

        elif words_commands[0] == 'all-contacts':
            ui.display_contacts(book.data)

        elif words_commands[0] == 'edit-contact':
            fun_edit_contact(book)

        elif words_commands[0] == 'delete-contact':
            fun_delete_contact(book)

        elif words_commands[0] == 'upcoming-birthdays':
            fun_upcoming_birthdays(book)

        elif words_commands[0] == 'add-note':
            fun_add_note(book)

        else:
            print("The command was not found. Please enter another command.")

        command = prompt('Write a command (help - all commands): ', completer=completer)
        save_book(book)

def load_book(filename):
    # Завантаження адресної книги з файлу
    try:
        with open(FILENAME, 'rb') as file: 
            return load(file)
    except FileNotFoundError:
        return AddressBook()
    except Exception as e:
        print("EXCEPTION\n", e)
        return AddressBook()
    
def save_book(address_book):
    # Збереження адресної книги у файл
    with open(FILENAME, 'wb') as file:
        dump(address_book, file)
    
def fun_add_contact(address_book, name):
    record = Record(name)

    # Використовуємо безпосередньо __setitem__ для додавання записів до AddressBook
    address_book[name] = record
    
    phone = input(f'Enter the phone of contact {name} (c - close): ')
    while phone != 'c':
        try:
            record.add_phone(phone)
            phone = input(f'Enter the phone of contact {name} (c - close): ')
        except ValueError:
            phone = input(f'Enter the phone (10 digits) (c - close): ')

    birthday = input(f'Enter the birthday of contact {name} (c - close): ')

    while birthday != 'c':
        try:
            # Встановлює день народження для запису контакту
            birthday = datetime.strptime(birthday, "%Y-%m-%d").date()
            record.set_birthday(birthday)
            break
        except ValueError:
            # Обробка виключення, якщо введено некоректний формат дня народження
            birthday = input(f'Enter the birthday (Year-month-day) (c - close): ')


    email = input(f'Enter the email address (c - close): ')
    while email != 'c':
        try:
            record.add_email(email)
            break
        except ValueError:
            email = input('Enter a valid email format (c - close): ')

    address = input(f'Enter the address of contact {name} (c - close): ')
    if address != 'c':
        record.set_address(address)


def fun_edit_contact(address_book):
    contact_name = input('Write the name of contact in which you want to change something: ')
    if contact_name in address_book.data:
        contact_edit = address_book.data[contact_name]
        print(f'Contact found')
        while True:
            edit = input('Enter what you want to edit(phone, birthday, address, email) (c - close): ')
            if edit.lower() == 'c':
                break
            try:
                if edit == 'phone':
                    new_phone = input("Enter new phone number: ")
                    contact_edit.edit_phone(contact_edit.phones[0].value, new_phone)
                elif edit == 'birthday':
                    new_birthday = datetime.strptime(input('Enter new birthday: '), "%Y-%m-%d").date()
                    contact_edit.set_birthday(new_birthday)
                elif edit == 'address':
                    new_address = input('Enter new address: ')
                    contact_edit.set_address(new_address)
                elif edit == 'email':
                    new_email = input('Enter new email: ')
                    contact_edit.edit_email(new_email)
                else:
                    print('Invalid command, please enter(phone, birthday, address, email) (c - close): ')
            except ValueError:
                print('Invalid command, please enter(phone, birthday, address, email) (c - close): ')
    else:
        print(f'Contact {contact_name} not found')


def fun_delete_contact(address_book):
    contact_name = input('Enter the name of contact you want to delete: ')
    if contact_name in address_book.data:
        question = input(f'Are you sure you want to delete this contact {contact_name}? (yes or no): ')
        if question == 'yes':
            del address_book.data[contact_name]
            print('Contact deleted')
        else:
            print('Deletion canceled')
    else:
        print(f'Contact with the name {contact_name} not found.')


def fun_add_note(address_book):
    note_text = input('Enter your note (c - close): ')
    while note_text.lower() != 'c':
        address_book.notes_manager.add_note(note_text)
        print('Note added successfully')
        note_text = input('Enter your note (c - close): ')


def fun_upcoming_birthdays(address_book):
    days_count = input('Enter the number of days to check upcoming birthdays: ')
    try:
        days_count = int(days_count)
        if days_count < 0:
            raise ValueError("Please enter a non-negative number of days.")
    except ValueError:
        print("Invalid input. Please enter a non-negative integer.")

    upcoming_birthdays = get_upcoming_birthdays(address_book, days_count)
    if upcoming_birthdays:
        print('*' * 10)
        print(f'Upcoming birthdays within the next {days_count} days:')
        for contact in upcoming_birthdays:
            print(contact)
            print('*' * 10)
    else:
        print(f'No upcoming birthdays within the next {days_count} days.')

def get_upcoming_birthdays(address_book, days_count):
    # Список для зберігання записів з найближчими днями народженнями
    upcoming_birthdays = []    

    # Отримання поточної дати та часу                
    today = datetime.today()          

    # Перебір записів у адресній книзі       
    for record in address_book.data.values():
        # Перевірка, чи є в запису вказана дата народження

        if record.birthday:                    
            # Формування дати наступного дня народження
            next_birthday = datetime(today.year, record.birthday.month, record.birthday.day)  

            # Якщо день народження вже минув у поточному році, обчислити для наступного року        
            if next_birthday < today:                                                                  
                next_birthday = datetime(today.year + 1, record.birthday.month, record.birthday.day)  

            # Обчислення різниці в часі між сьогоднішньою датою і наступним днем народження
            delta = next_birthday - today           

            # Перевірка, чи день народження відбудеться в межах визначеної кількості днів                                                   
            if 0 <= delta.days <= days_count:                                                          
                upcoming_birthdays.append(record)

    # Повернення списку з записами, у яких найближчий день народження наступає впродовж зазначеної кількості днів
    return upcoming_birthdays

if __name__ == "__main__":
    main()