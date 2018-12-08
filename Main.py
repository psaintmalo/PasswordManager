import os
import smtplib
import pyAesCrypt
import csv
import pandas as pd
from time import sleep
from random import sample
from getpass import getpass
from hashlib import sha3_512


def encrypt_file(decrypted_in, encrypted_out, key):
    pyAesCrypt.encryptFile(decrypted_in, encrypted_out, key, 1024*64)


def decrypt_file(encrypted_in, decrypted_out, key):
    pyAesCrypt.decryptFile(encrypted_in, decrypted_out, key, 1024 * 64)


def send_mail_copy(saved_logins, token):  # WORK NEEDED TO SEND ATTACHMENT FO FILES ------------------------------------
    print("Currently this option only works with gmail, and you have turn on 'Allow less secure apps' ", end="\n\n")
    en = input("Would you like to send the files encrypted? (Recommended option is Y) Y/n")
    if en.lower() == "y":
        token_file = "x"
        logins_file = "y"
    elif en.lower() == "n":
        pass  # Send unencrypted file
    else:
        print("Didn't recognize that answer, preceding sending encrypted files")

    message = ""
    sender_mail = input("Email to send the files: ")
    sender_pass = getpass("Password of mail: ")
    receiver_mail = input("Email to receive files: ")

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_mail, sender_pass)
    server.sendmail(
        sender_mail,
        receiver_mail,
        message)
    server.quit()


def create_logins_file(key):
    with open("unenc", "w") as new_logins:
        new_logins.write("Website,Mail,Password,Notes")
    encrypt_file("unenc", "saved_logins", key)
    os.remove("unenc")
    return open("saved_logins", "r")


def sc_files():  # Check password files and key_hash present and returns their values

    if os.path.exists("saved_logins") and os.path.exists("token"):
        logins = open("saved_logins", "r")
        token = open("token", "r")
    elif not os.path.exists("saved_logins"):
        print("saved_logins file is missing, creating new logins and token file.")
        key = getpass("Please enter your new key: ")
        confirm_key = getpass("Confirm you key: ")
        while key != confirm_key:
            print("Key's dont match\n")
            key = getpass("Please enter your new key: ")
            confirm_key = getpass("Confirm you key: ")
        token = open("token", "w")
        token.write(hash256(key))
        logins = create_logins_file(key)

    elif not os.path.exists("token"):
        option = input("token file is missing, would you like to format all data? Y/n: ")
        if option.lower() == "y":
            key = getpass("Please enter your new key: ")
            confirm_key = getpass("Confirm you key: ")
            while key != confirm_key:
                print("Key's dont match\n")
                key = getpass("Please enter your new key: ")
                confirm_key = getpass("Confirm you key: ")
            token = open("token", "w")
            token.write(hash256(key))
            logins = create_logins_file(key)
            token.close()
        elif option.lower() == "n":
            print("Cannot continue without the token file")
            exit(0)

    # noinspection PyUnboundLocalVariable
    return token, logins


def hash256(key):  # Hashes a given key with sha512
    key_to_hash = sha3_512(key.encode(encoding="UTF-8")).hexdigest()
    return key_to_hash


def check_key(token_f):  # Compares the stored hash with the user hash
    stored_hash = token_f.read()
    if stored_hash == "" or stored_hash.__len__() != 128:
        print("No compatible key stored. New key needed. (This will format any stored password's)\n")
        token_f.close()
        while True:
            key = getpass("Please insert the key you would like to use to lock/unlock the list:  ")
            key_c = getpass("Confirm your key:  ")
            if key != key_c:
                print("Key's didn't match\n")
            else:
                break
        print("Saving new key")
        open("saved_logins", "w+")
        tokenf = open("token", "w+")
        tokenf.write(hash256(key))

        user_key = key

    else:
        user_key = getpass("Please enter your key: ")
        hashed_key = hash256(user_key)
        xyz = 1
        while hashed_key != stored_hash:
            if xyz == 3:
                print("Too many tries.")
                sleep(0.1)
                exit(0)
            else:
                user_key = getpass("Your key didn't match the saved key. Please try again: ")
                hashed_key = hash256(user_key)
                xyz += 1
        print("Correct key")
        sleep(0.1)

    key = user_key

    return key


def read_csv(csv_file):
    df = pd.read_csv(csv_file)
    pd.options.display.max_columns = len(df.columns)
    pd.set_option('display.expand_frame_repr', False)
    print(df)


def readall_passwords(logins_f, key):
    encrypted_logins = logins_f
    temp_fn = "temp"
    decrypt_file(encrypted_logins, temp_fn, key)
    read_csv(temp_fn)
    os.remove(temp_fn)


def csv_value_change(x, y, value, file_name):
    file = open(file_name, "r")
    csv_read = csv.reader(file)
    lines = list(csv_read)
    lines[x + 1][y] = value
    new_csv_ = open(file.name, "w", newline="")
    writer = csv.writer(new_csv_)
    writer.writerows(lines)


def generate_random_pass(length):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNPQRSTUVWXYZ!@#$%^&*()?"
    special_chars = "!@#$%^&*()?"
    nums = "01234567890"
    x = 0
    y = 0
    while x == 0 and y == 0:  # Makes sure at least one number and one special character is present
        x = 0
        y = 0
        ran_pass = "".join(sample(chars, length))
        for char in ran_pass:
            if char in special_chars:
                x += 1
            elif char in nums:
                y += 1

    return ran_pass


def add_new_record(logins_f, key):
    decrypt_file(logins_f.name, "unenc", key)
    website = input("Website: ")
    mail = input("Email: ")
    random_pass_opt = input("Would you like a random generated password? Y/n: ")
    if random_pass_opt.lower() == "y":
        length = input("How long would you like the password to be? Leave blank for default length:  ")
        if length == "":
            length = 14
        password = generate_random_pass(int(length))
        print("Your new password for  %s  is:\n%s" % (website, password))
    elif random_pass_opt.lower() == "n":
        password = getpass("Password: ")
    else:
        print("Not an option. Continuing with standard password\n")
        password = getpass("Password: ")

    note = input("Note: ")

    new_file = open("unenc", "a")
    new_file.write("\n" + website + "," + mail + "," + password + "," + note)
    new_file.close()
    encrypt_file(new_file.name, logins_f.name, key)
    os.remove(new_file.name)


def edit_record(logins_f, key):
    unenc = "unenc"
    encrypted_logins = logins_f.name
    decrypt_file(encrypted_logins, unenc, key)
    read_csv(unenc)
    record_to_change = int(input("Which record to change? "))
    field_to_change = int(input("Which field to edit? Website(0), Mail(1), Password(2), Note(3)"))

    if field_to_change == 0:
        new_value = input("New value for the Website: ")

    elif field_to_change == 1:
        new_value = input("New value for the Email: ")

    elif field_to_change == 2:
        option = input("Would you like a new random password? Y/n: ")
        if option.lower() == "n":
            new_value = getpass("New value for the Password: ")
        else:
            length = input("How long would you like the password to be? Leave blank for default length: ")
            if length == "":
                length = 14
            else:
                length = int(length)
            new_value = generate_random_pass(length)

    elif field_to_change == 3:
        new_value = input("New value for the Note: ")

    else:
        new_value = ""
        print("That wasn't a valid option")

    if new_value != "":
        csv_value_change(record_to_change, field_to_change, new_value, unenc)

    encrypt_file(unenc, "saved_logins", key)
    os.remove(unenc)


def delete_record(logins_f, key):
    readall_passwords(logins_f, key)
    record_to_delete = int(input("Which record do you want to delete? ")) + 1
    row_c = 0
    for row in logins_f:
        if row_c == record_to_delete:
            row = ""
        else:
            row_c += 1


def change_key(key):
    print("After changing the key, you will have to re-open the program")
    old_key = getpass("Please enter your old key: ")
    counter = 0
    while old_key != key:
        counter += 1
        print("Incorrect key")
        old_key = getpass("\nPlease enter your old key: ")
        if counter == 3:
            print("Too many tries.")
            exit(0)
    new_key = getpass("Enter your new key: ")
    confirm_key = getpass("Please confirm your new key: ")
    while new_key != confirm_key:
        print("Keys dont match, please enter them again\n")
        new_key = getpass("Enter your new key: ")
        confirm_key = getpass("Please confirm your new key: ")

    with open("token", "w") as file:
        file.write(hash256(new_key))
    decrypt_file("saved_logins", "temp", key)
    encrypt_file("temp", "saved_logins", new_key)
    os.remove("temp")


def delete_at_exit_safe():
    if os.path.isfile("unenc"):
        os.remove("unenc")
    elif os.path.isfile("temp"):
        os.remove("temp")


clear = lambda: os.system('cls')


clear()
token_file, logins_file = sc_files()
key_ = check_key(token_file)

while True:  # Main loop
    clear()
    print("\n1) Read saved logins      2) Add new record\n3) Edit existing record   4) Delete record")  # Options
    print("5) Change key             6) Delete all files\n0) Exit")
    option = int(input("-> ",))  # Choose option
    clear()
    if not 10 > option >= 0:  # Check option is between the acceptable values
        pass
    elif option == 1:  # Run option
        readall_passwords(logins_file.name, key_)
        x = input("\nPress enter to continue")
    elif option == 2:
        add_new_record(logins_file, key_)
    elif option == 3:
        edit_record(logins_file, key_)
    elif option == 5:
        change_key(key_)  # After changing the key the next error appears: OSError: File "saved_logins" was not found
        print("Key succesfuly change")
        sleep(1)
        exit(0)
    elif option == 0:
        break

key_ = ""
clear()