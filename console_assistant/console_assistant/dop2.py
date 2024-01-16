from collections import UserDict
from datetime import datetime
from pickle import dump, load
from os import path
from os import getcwd, makedirs

from rich.console import Console
from rich.table import Table

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from re import fullmatch
from re import IGNORECASE

EMAIL_REGULAR = r"[a-z][a-z0-9_.]+[@][a-z.]+[.][a-z]{2,}"

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    # реалізація класу
    def __init__(self, value):
        self.value = value

    # getter
    @property
    def value(self):
        return self._value

    # setter
    @value.setter
    def value(self, new_value):
        self._value = new_value

class Phone(Field):
    def __init__(self, value):
        if not self.is_valid_phone(value):
            raise ValueError("Invalid phone number format")
        super().__init__(value)

    @staticmethod
    def is_valid_phone(value):
        return len(value) == 10 and value.isdigit()
    
    # getter
    @property
    def value(self):
        return self._value
    
    # setter
    @value.setter
    def value(self, new_value):
        self._value = new_value

    def __str__(self):
        return str(self._value)

class Email(Field):
    def __init__(self, value):
        if not self.is_valid_email(value):
            raise ValueError('Invalid email format')
        super().__init__(value)

    @staticmethod
    def is_valid_email(value):
        return fullmatch(EMAIL_REGULAR, value, flags = IGNORECASE) is not None
    
    # getter
    @property
    def value(self):
        return self._value
    
    # setter
    @value.setter
    def value(self, new_value):
        if not self.is_valid_email(new_value):
            raise ValueError('Invalid email format')
        self._value = new_value

    def __str__(self):
        return str(self._value)
class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)

    # getter
    @property
    def value(self):
        return self._value
    
    # setter
    @value.setter
    def value(self, new_value):
        self._value = new_value

class Address(Field):
    def __init__(self, value):
        super().__init__(value)

    # getter
    @property
    def value(self):
        return self._value
    
    # setter
    @value.setter
    def value(self, new_value):
        self._value = new_value

class Notes:
    def __init__(self, text, author, tags=None):
        self.text = text
        self.author = author
        self.tags = tags if tags is not None else []

    def __str__(self):
        tags_str = ', '.join(self.tags) if hasattr(self, 'tags') else ''
        return f"{self.text} (by {self.author}, Tags: {tags_str})"
    
class NoteManager:
    def __init__(self):
        self.notes = []

    def add_note_with_tags(self, author, text, tags):
        note = Notes(text, author, tags)
        self.notes.append(note)

    def print_notes(self):
        if self.notes:
            console = Console()
            table = Table(title="Wish list", show_header=True, header_style="bold magenta")
            table.title_align = "center"
            table.title_style = "bold yellow"
            table.add_column("Index", style="cyan", width=5, justify="center")
            table.add_column("Note", style="green")
            table.add_column("Author", style="blue")
            table.add_column("Tags", style="magenta")  # Додавання стовпця для тегів

            for i, note in enumerate(self.notes, start=1):
                # Перевірка, чи note має атрибут tags перед його використанням
                tags_str = ', '.join(note.tags) if hasattr(note, 'tags') else ''
                table.add_row(str(i), note.text, note.author, tags_str)

            console.print(table)
        else:
            print("No notes available.")

    def save_notes(self, filename):
        with open(filename, 'wb') as file:
            dump(self.notes, file)

    def load_notes(self, filename):
        try:
            with open(filename, 'rb') as file:
                self.notes = load(file)
        except FileNotFoundError:
            self.notes = []

    def edit_note(self, index, new_text=None, new_tags=None):
        # Редагує нотатку з вказаним індексом.
        # index: Індекс нотатки для редагування
        # new_text: Новий текст нотатки
        # new_tags: Нові теги нотатки
        
        if 1 <= index <= len(self.notes):
            note = self.notes[index - 1]
            note.text = new_text
            note.tags = new_tags
            print(f"Note {index} edited successfully.")
        else:
            print("Invalid note index.")

    def delete_note(self, index):
        if 1 <= index <= len(self.notes):
            deleted_note = self.notes.pop(index - 1)
            print(f"Note {index} deleted: {deleted_note}")
        else:
            print("Invalid note index.")

    def update_notes_author(self, old_author, new_author, filename):
        for note in self.notes:
            if note.author == old_author:
                note.author = new_author

        # Збереження оновленного нотатка у файл
        self.save_notes(filename)
        
class AddressBookIterator:
    def __init__(self, address_book, items_per_page):
        self.address_book = address_book
        self.items_per_page = items_per_page
        # Визначається поточна сторінка, починаючи з нуля (перша сторінка)
        self.current_page = 0

    def __iter__(self):
        return self

    def __next__(self):
        # Метод обчислює індекс початку (start) і кінця (end) діапазону записів, які повинні бути виведені на поточній сторінці. 
        # Наприклад, якщо items_per_page дорівнює 5, то на першій сторінці будуть виводитися записи з індексами 0 до 4, 
        # на другій сторінці - з 5 до 9, і так далі.
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        records = list(self.address_book.data.values())[start:end]

        if not records:
            raise StopIteration

        self.current_page += 1
        return records