#!/usr/bin/env python3
"""
library-management-system
Complete Library Management System with CRUD operations,
member management, borrowing system, fines, and search.

Author: Sameer Bansal
Reg No: RA2311032010061
College: SRM Institute of Science and Technology
Branch: B.Tech CSE (IoT) | Batch: 2023-2027
"""

import os
import json
import datetime
import random
import string
from typing import Optional

# ── Constants ─────────────────────────────────────────────
DATA_FILE = "output/library_data.json"
BORROW_DAYS = 14  # Default borrow period
FINE_PER_DAY = 5.0  # ₹ per day overdue
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"


# ── ID Generator ──────────────────────────────────────────
def generate_id(prefix, length=6):
    return prefix + "".join(random.choices(string.digits, k=length))


# ── Book Class ────────────────────────────────────────────
class Book:
    def __init__(self, book_id, title, author, genre, year, copies=1):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.year = year
        self.total_copies = copies
        self.available_copies = copies

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "year": self.year,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
        }

    @classmethod
    def from_dict(cls, d):
        b = cls(
            d["book_id"],
            d["title"],
            d["author"],
            d["genre"],
            d["year"],
            d["total_copies"],
        )
        b.available_copies = d["available_copies"]
        return b

    def display(self):
        status = (
            f"{GREEN}Available ({self.available_copies}/{self.total_copies}){RESET}"
            if self.available_copies > 0
            else f"{RED}Unavailable{RESET}"
        )
        print(f"  📚 [{self.book_id}] {BOLD}{self.title}{RESET}")
        print(
            f"       Author : {self.author}  |  Genre: {self.genre}  |  Year: {self.year}"
        )
        print(f"       Status : {status}")


# ── Member Class ──────────────────────────────────────────
class Member:
    def __init__(self, member_id, name, email, phone, member_type="Student"):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.phone = phone
        self.member_type = member_type
        self.join_date = datetime.date.today().isoformat()
        self.borrowed = []  # list of transaction IDs
        self.total_fines = 0.0
        self.fines_paid = 0.0

    @property
    def pending_fines(self):
        return round(self.total_fines - self.fines_paid, 2)

    def to_dict(self):
        return {
            "member_id": self.member_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "member_type": self.member_type,
            "join_date": self.join_date,
            "borrowed": self.borrowed,
            "total_fines": self.total_fines,
            "fines_paid": self.fines_paid,
        }

    @classmethod
    def from_dict(cls, d):
        m = cls(d["member_id"], d["name"], d["email"], d["phone"], d["member_type"])
        m.join_date = d["join_date"]
        m.borrowed = d["borrowed"]
        m.total_fines = d["total_fines"]
        m.fines_paid = d["fines_paid"]
        return m

    def display(self):
        fine_str = (
            f"{RED}₹{self.pending_fines:.2f} pending{RESET}"
            if self.pending_fines > 0
            else f"{GREEN}No fines{RESET}"
        )
        print(f"  👤 [{self.member_id}] {BOLD}{self.name}{RESET}")
        print(f"       Email : {self.email}  |  Phone: {self.phone}")
        print(f"       Type  : {self.member_type}  |  Joined: {self.join_date}")
        print(f"       Books : {len(self.borrowed)} borrowed  |  Fines: {fine_str}")


# ── Transaction Class ─────────────────────────────────────
class Transaction:
    def __init__(self, txn_id, book_id, member_id, book_title, member_name):
        self.txn_id = txn_id
        self.book_id = book_id
        self.member_id = member_id
        self.book_title = book_title
        self.member_name = member_name
        self.borrow_date = datetime.date.today().isoformat()
        self.due_date = (
            datetime.date.today() + datetime.timedelta(days=BORROW_DAYS)
        ).isoformat()
        self.return_date: Optional[str] = None
        self.fine = 0.0
        self.status = "BORROWED"

    @property
    def is_overdue(self):
        if self.status == "BORROWED":
            return datetime.date.today() > datetime.date.fromisoformat(self.due_date)
        return False

    @property
    def days_overdue(self):
        if self.is_overdue:
            return (
                datetime.date.today() - datetime.date.fromisoformat(self.due_date)
            ).days
        return 0

    def calculate_fine(self):
        if self.is_overdue:
            self.fine = round(self.days_overdue * FINE_PER_DAY, 2)
        return self.fine

    def to_dict(self):
        return {
            "txn_id": self.txn_id,
            "book_id": self.book_id,
            "member_id": self.member_id,
            "book_title": self.book_title,
            "member_name": self.member_name,
            "borrow_date": self.borrow_date,
            "due_date": self.due_date,
            "return_date": self.return_date,
            "fine": self.fine,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, d):
        t = cls(
            d["txn_id"], d["book_id"], d["member_id"], d["book_title"], d["member_name"]
        )
        t.borrow_date = d["borrow_date"]
        t.due_date = d["due_date"]
        t.return_date = d["return_date"]
        t.fine = d["fine"]
        t.status = d["status"]
        return t

    def display(self):
        overdue_str = (
            f"{RED}⚠️  OVERDUE by {self.days_overdue} days "
            f"(₹{self.calculate_fine():.2f}){RESET}"
            if self.is_overdue
            else f"{GREEN}On time{RESET}"
        )
        status_str = (
            f"{GREEN}{self.status}{RESET}"
            if self.status == "RETURNED"
            else f"{YELLOW}{self.status}{RESET}"
        )
        print(f"  🔖 [{self.txn_id}]  Status: {status_str}")
        print(f"       Book   : {self.book_title} ({self.book_id})")
        print(f"       Member : {self.member_name} ({self.member_id})")
        print(f"       Borrow : {self.borrow_date}  |  Due: {self.due_date}")
        if self.status == "RETURNED":
            print(f"       Returned: {self.return_date}  |  Fine: ₹{self.fine:.2f}")
        else:
            print(f"       {overdue_str}")


# ── Library Class ─────────────────────────────────────────
class Library:
    def __init__(self):
        self.books = {}
        self.members = {}
        self.transactions = {}
        os.makedirs("output", exist_ok=True)
        self._load()
        if not self.books:
            self._seed_data()

    # ── Persistence ───────────────────────────────────────
    def _save(self):
        data = {
            "books": {k: v.to_dict() for k, v in self.books.items()},
            "members": {k: v.to_dict() for k, v in self.members.items()},
            "transactions": {k: v.to_dict() for k, v in self.transactions.items()},
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def _load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE) as f:
                    data = json.load(f)
                self.books = {
                    k: Book.from_dict(v) for k, v in data.get("books", {}).items()
                }
                self.members = {
                    k: Member.from_dict(v) for k, v in data.get("members", {}).items()
                }
                self.transactions = {
                    k: Transaction.from_dict(v)
                    for k, v in data.get("transactions", {}).items()
                }
                print(f"  {GREEN}✅ Data loaded from {DATA_FILE}{RESET}")
            except Exception as e:
                print(f"  {YELLOW}⚠️  Could not load data: {e}. Starting fresh.{RESET}")

    def _seed_data(self):
        """Pre-populate with sample books and members"""
        sample_books = [
            (
                "Introduction to Algorithms",
                "Cormen et al.",
                "Computer Science",
                2022,
                3,
            ),
            ("Clean Code", "Robert C. Martin", "Software Engg.", 2008, 2),
            ("The IoT Handbook", "Charles Bell", "IoT", 2021, 2),
            ("Python Crash Course", "Eric Matthes", "Programming", 2023, 4),
            (
                "Data Structures in Python",
                "Goodrich et al.",
                "Computer Science",
                2020,
                2,
            ),
            ("Artificial Intelligence: A MA", "Stuart Russell", "AI/ML", 2020, 2),
            ("Operating System Concepts", "Silberschatz et al.", "Systems", 2021, 3),
            ("Computer Networks", "Andrew Tanenbaum", "Networking", 2021, 2),
            ("Database System Concepts", "Silberschatz et al.", "Databases", 2020, 2),
            ("The Pragmatic Programmer", "Hunt & Thomas", "Software Engg.", 2019, 1),
        ]
        for title, author, genre, year, copies in sample_books:
            bid = generate_id("BK")
            self.books[bid] = Book(bid, title, author, genre, year, copies)

        sample_members = [
            ("Sameer Bansal", "sb0295@srmist.edu.in", "9999999999", "Student"),
            ("Arjun Sharma", "arjun@srmist.edu.in", "8888888888", "Student"),
            ("Priya Nair", "priya@srmist.edu.in", "7777777777", "Student"),
            ("Dr. Kumar", "kumar@srmist.edu.in", "6666666666", "Faculty"),
        ]
        for name, email, phone, mtype in sample_members:
            mid = generate_id("MBR")
            self.members[mid] = Member(mid, name, email, phone, mtype)

        self._save()
        print(
            f"  {GREEN}✅ Library seeded with {len(self.books)} books "
            f"and {len(self.members)} members{RESET}"
        )

    # ── Book CRUD ─────────────────────────────────────────
    def add_book(self, title, author, genre, year, copies=1):
        bid = generate_id("BK")
        self.books[bid] = Book(bid, title, author, genre, year, copies)
        self._save()
        return bid, f"{GREEN}✅ Book added: [{bid}] {title}{RESET}"

    def update_book(self, book_id, **kwargs):
        if book_id not in self.books:
            return f"{RED}❌ Book not found: {book_id}{RESET}"
        book = self.books[book_id]
        for key, val in kwargs.items():
            if hasattr(book, key):
                setattr(book, key, val)
        self._save()
        return f"{GREEN}✅ Book updated: {book_id}{RESET}"

    def delete_book(self, book_id):
        if book_id not in self.books:
            return f"{RED}❌ Book not found: {book_id}{RESET}"
        if self.books[book_id].available_copies < self.books[book_id].total_copies:
            return f"{RED}❌ Cannot delete: some copies are currently borrowed.{RESET}"
        title = self.books[book_id].title
        del self.books[book_id]
        self._save()
        return f"{GREEN}✅ Book deleted: {title}{RESET}"

    def search_books(self, query):
        query = query.lower()
        results = [
            b
            for b in self.books.values()
            if query in b.title.lower()
            or query in b.author.lower()
            or query in b.genre.lower()
        ]
        return results

    # ── Member CRUD ───────────────────────────────────────
    def add_member(self, name, email, phone, member_type="Student"):
        mid = generate_id("MBR")
        self.members[mid] = Member(mid, name, email, phone, member_type)
        self._save()
        return mid, f"{GREEN}✅ Member added: [{mid}] {name}{RESET}"

    def search_members(self, query):
        query = query.lower()
        return [
            m
            for m in self.members.values()
            if query in m.name.lower()
            or query in m.email.lower()
            or query in m.member_id.lower()
        ]

    # ── Borrowing System ──────────────────────────────────
    def borrow_book(self, book_id, member_id):
        if book_id not in self.books:
            return False, f"{RED}❌ Book not found: {book_id}{RESET}"
        if member_id not in self.members:
            return False, f"{RED}❌ Member not found: {member_id}{RESET}"

        book = self.books[book_id]
        member = self.members[member_id]

        if book.available_copies <= 0:
            return False, f"{RED}❌ No copies available for: {book.title}{RESET}"
        if len(member.borrowed) >= 3:
            return (
                False,
                f"{RED}❌ {member.name} has reached max borrow limit (3 books).{RESET}",
            )
        if member.pending_fines > 0:
            return False, (
                f"{RED}❌ {member.name} has pending fines of "
                f"₹{member.pending_fines:.2f}. Please clear before borrowing.{RESET}"
            )

        txn_id = generate_id("TXN")
        txn = Transaction(txn_id, book_id, member_id, book.title, member.name)
        self.transactions[txn_id] = txn

        book.available_copies -= 1
        member.borrowed.append(txn_id)
        self._save()

        return True, (
            f"{GREEN}✅ Book borrowed!\n"
            f"   Transaction : {txn_id}\n"
            f"   Book        : {book.title}\n"
            f"   Member      : {member.name}\n"
            f"   Due Date    : {txn.due_date}{RESET}"
        )

    def return_book(self, txn_id):
        if txn_id not in self.transactions:
            return False, f"{RED}❌ Transaction not found: {txn_id}{RESET}"

        txn = self.transactions[txn_id]
        if txn.status == "RETURNED":
            return False, f"{YELLOW}⚠️  Book already returned.{RESET}"

        book = self.books.get(txn.book_id)
        member = self.members.get(txn.member_id)

        fine = txn.calculate_fine()
        txn.return_date = datetime.date.today().isoformat()
        txn.status = "RETURNED"

        if book:
            book.available_copies = min(book.available_copies + 1, book.total_copies)
        if member and txn_id in member.borrowed:
            member.borrowed.remove(txn_id)
            if fine > 0:
                member.total_fines += fine

        self._save()

        fine_msg = (
            f"\n   {RED}⚠️  Fine: ₹{fine:.2f} ({txn.days_overdue} days overdue){RESET}"
            if fine > 0
            else f"\n   {GREEN}No fine — returned on time!{RESET}"
        )
        return True, (
            f"{GREEN}✅ Book returned!\n"
            f"   Book   : {txn.book_title}\n"
            f"   Member : {txn.member_name}{fine_msg}{RESET}"
        )

    def pay_fine(self, member_id, amount):
        if member_id not in self.members:
            return f"{RED}❌ Member not found.{RESET}"
        member = self.members[member_id]
        if member.pending_fines <= 0:
            return f"{GREEN}✅ No pending fines for {member.name}.{RESET}"
        paid = min(amount, member.pending_fines)
        member.fines_paid += paid
        self._save()
        return (
            f"{GREEN}✅ ₹{paid:.2f} paid. "
            f"Remaining fine: ₹{member.pending_fines:.2f}{RESET}"
        )

    # ── Reports ───────────────────────────────────────────
    def get_overdue(self):
        return [
            t
            for t in self.transactions.values()
            if t.status == "BORROWED" and t.is_overdue
        ]

    def dashboard(self):
        total_books = sum(b.total_copies for b in self.books.values())
        borrowed_books = sum(
            1 for t in self.transactions.values() if t.status == "BORROWED"
        )
        overdue = self.get_overdue()
        total_fines = sum(m.total_fines for m in self.members.values())

        print(f"\n  {'─' * 50}")
        print(f"  {BOLD}📊 LIBRARY DASHBOARD{RESET}")
        print(f"  {'─' * 50}")
        print(
            f"  📚 Total Books       : {len(self.books)} titles ({total_books} copies)"
        )
        print(f"  👤 Total Members     : {len(self.members)}")
        print(f"  🔖 Active Borrows    : {borrowed_books}")
        print(f"  ⚠️  Overdue Books     : {len(overdue)}")
        print(f"  💰 Total Fines       : ₹{total_fines:.2f}")
        print(f"  📅 Today             : {datetime.date.today()}")
        print(f"  {'─' * 50}")


# ── Display Menu ──────────────────────────────────────────
def display_banner():
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 56)
    print("      📖 LIBRARY MANAGEMENT SYSTEM")
    print("      Author : Sameer Bansal | RA2311032010061")
    print("      College: SRMIST Kattankulathur")
    print("=" * 56)


def display_menu():
    print(f"""
  {BOLD}BOOKS{RESET}
  [1]  Add book          [2]  Search books
  [3]  List all books    [4]  Delete book

  {BOLD}MEMBERS{RESET}
  [5]  Add member        [6]  Search members
  [7]  List all members

  {BOLD}BORROWING{RESET}
  [8]  Borrow book       [9]  Return book
  [10] View overdue      [11] Pay fine

  {BOLD}REPORTS{RESET}
  [12] Dashboard         [13] All transactions

  [q]  Quit
""")


def list_all_books(lib):
    print(f"\n  📚 ALL BOOKS ({len(lib.books)} titles)")
    print("  " + "─" * 50)
    for book in lib.books.values():
        book.display()
        print()


def list_all_members(lib):
    print(f"\n  👤 ALL MEMBERS ({len(lib.members)})")
    print("  " + "─" * 50)
    for member in lib.members.values():
        member.display()
        print()


def list_transactions(lib):
    txns = list(lib.transactions.values())
    print(f"\n  🔖 ALL TRANSACTIONS ({len(txns)})")
    print("  " + "─" * 50)
    if not txns:
        print("  No transactions yet.")
        return
    for txn in txns[-20:]:
        txn.display()
        print()


# ── Main ──────────────────────────────────────────────────
def main():
    display_banner()
    lib = Library()
    lib.dashboard()
    display_menu()

    while True:
        try:
            choice = input("\n  Enter option: ").strip().lower()

            if choice == "q":
                print(f"\n  👋 Goodbye! Library data saved to {DATA_FILE}")
                break

            elif choice == "1":
                print(f"\n  {BOLD}➕ ADD BOOK{RESET}")
                title = input("  Title   : ").strip()
                author = input("  Author  : ").strip()
                genre = input("  Genre   : ").strip()
                year = input("  Year    : ").strip()
                copies = input("  Copies  : ").strip()
                _, msg = lib.add_book(
                    title, author, genre, int(year or 2024), int(copies or 1)
                )
                print(f"  {msg}")

            elif choice == "2":
                query = input("\n  Search books (title/author/genre): ").strip()
                results = lib.search_books(query)
                print(f"\n  Found {len(results)} result(s):")
                for b in results:
                    b.display()
                    print()

            elif choice == "3":
                list_all_books(lib)

            elif choice == "4":
                book_id = input("\n  Enter Book ID to delete: ").strip()
                print(f"  {lib.delete_book(book_id)}")

            elif choice == "5":
                print(f"\n  {BOLD}➕ ADD MEMBER{RESET}")
                name = input("  Name        : ").strip()
                email = input("  Email       : ").strip()
                phone = input("  Phone       : ").strip()
                mtype = input("  Type (Student/Faculty): ").strip().title() or "Student"
                _, msg = lib.add_member(name, email, phone, mtype)
                print(f"  {msg}")

            elif choice == "6":
                query = input("\n  Search members (name/email/ID): ").strip()
                results = lib.search_members(query)
                print(f"\n  Found {len(results)} result(s):")
                for m in results:
                    m.display()
                    print()

            elif choice == "7":
                list_all_members(lib)

            elif choice == "8":
                print(f"\n  {BOLD}📤 BORROW BOOK{RESET}")
                book_id = input("  Book ID   : ").strip()
                member_id = input("  Member ID : ").strip()
                _, msg = lib.borrow_book(book_id, member_id)
                print(f"\n  {msg}")

            elif choice == "9":
                print(f"\n  {BOLD}📥 RETURN BOOK{RESET}")
                txn_id = input("  Transaction ID: ").strip()
                _, msg = lib.return_book(txn_id)
                print(f"\n  {msg}")

            elif choice == "10":
                overdue = lib.get_overdue()
                print(f"\n  {RED}⚠️  OVERDUE BOOKS ({len(overdue)}){RESET}")
                print("  " + "─" * 50)
                if not overdue:
                    print(f"  {GREEN}✅ No overdue books!{RESET}")
                for txn in overdue:
                    txn.display()
                    print()

            elif choice == "11":
                member_id = input("\n  Member ID  : ").strip()
                amount = input("  Amount (₹): ").strip()
                print(f"  {lib.pay_fine(member_id, float(amount or 0))}")

            elif choice == "12":
                lib.dashboard()

            elif choice == "13":
                list_transactions(lib)

            elif choice == "menu":
                display_menu()

            else:
                print("  ⚠️  Invalid option. Type 'menu' to see all options.")

        except KeyboardInterrupt:
            print(f"\n\n  👋 Goodbye!")
            break
        except ValueError as e:
            print(f"  {RED}⚠️  Invalid input: {e}{RESET}")


if __name__ == "__main__":
    main()
