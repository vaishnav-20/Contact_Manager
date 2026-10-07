contacts = []
next_id = 1

def display_contact(contact):
    print("----------------------------------------")
    print(f"ID: {contact['id']}")
    print(f"Name: {contact['name']}")
    print(f"Phone: {contact['phone']}")
    print(f"Email: {contact['email']}")
    print("----------------------------------------")

def find_contact_by_id(contact_id):
    for c in contacts:
        if c["id"] == contact_id:
            return c
    return None

def add_contact():
    global next_id
    name = input("Enter name: ")
    phone = input("Enter phone: ")
    email = input("Enter email: ")
    contact = {
        "id": next_id,
        "name": name,
        "phone": phone,
        "email": email
    }
    contacts.append(contact)
    print(f"Contact '{name}' added successfully with ID {next_id}!\n")
    next_id += 1

def view_contacts():
    if not contacts:
        print("No contacts available.\n")
    else:
        print("========================================")
        print("              CONTACTS")
        print("========================================")
        for c in contacts:
            display_contact(c)
        print()

def search_contact():
    print("Search by:")
    print("1. ID")
    print("2. Name")
    print("3. Phone")
    print("4. Email")
    choice = input("Enter choice: ")

    if choice == "1":
        try:
            cid = int(input("Enter ID: "))
            contact = find_contact_by_id(cid)
            if contact:
                display_contact(contact)
            else:
                print("Contact not found.\n")
        except ValueError:
            print("Invalid ID.\n")

    elif choice == "2":
        name = input("Enter name: ")
        found = False
        for c in contacts:
            if name.lower() in c["name"].lower():
                display_contact(c)
                found = True
        if not found:
            print("Contact not found.\n")

    elif choice == "3":
        phone = input("Enter phone: ")
        for c in contacts:
            if phone in c["phone"]:  
                display_contact(c)
                return
        print("Contact not found.\n")

    elif choice == "4":
        email = input("Enter email: ")
        for c in contacts:
            if email.lower() in c["email"].lower():
                display_contact(c)
                return
        print("Contact not found.\n")

    else:
        print("Invalid choice.\n")

def update_contact():
    try:
        cid = int(input("Enter Contact ID to update: "))
        contact = find_contact_by_id(cid)
        if contact:
            print("Current contact:")
            display_contact(contact)
            print("\nWhat do you want to update?")
            print("1. Name\n2. Phone\n3. Email\n4. Cancel")
            choice = input("Enter choice: ")
            if choice == "1":
                contact["name"] = input("Enter new name: ")
            elif choice == "2":
                contact["phone"] = input("Enter new phone: ")
            elif choice == "3":
                contact["email"] = input("Enter new email: ")
            elif choice == "4":
                print("Update cancelled.\n")
                return
            print("Contact updated successfully!\n")
        else:
            print("Contact ID not found.\n")
    except ValueError:
        print("Invalid ID.\n")

def delete_contact():
    try:
        cid = int(input("Enter Contact ID to delete: "))
        contact = find_contact_by_id(cid)
        if contact:
            print("Contact:")
            display_contact(contact)
            confirm = input("Are you sure? (y/n): ")
            if confirm.lower() == "y":
                contacts.remove(contact)
                print("Contact deleted successfully.\n")
            else:
                print("Delete cancelled.\n")
        else:
            print("Contact ID not found.\n")
    except ValueError:
        print("Invalid ID.\n")

def main():
    while True:
        print("CONTACT MANAGER PRO")
        print("1. Add Contact")
        print("2. View Contacts")
        print("3. Search Contact")
        print("4. Update Contact")
        print("5. Delete Contact")
        print("6. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            add_contact()
        elif choice == "2":
            view_contacts()
        elif choice == "3":
            search_contact()
        elif choice == "4":
            update_contact()
        elif choice == "5":
            delete_contact()
        elif choice == "6":
            print("Exiting Contact Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.\n")

if __name__ == "__main__":
    main()