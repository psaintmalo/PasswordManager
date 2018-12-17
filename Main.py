import os
import csv
import shutil
import smtplib
import platform
import pyAesCrypt
import pandas as pd
from time import sleep
from random import sample
from getpass import getpass
from hashlib import sha3_512
from datetime import datetime


def double_check(promt1="Key for file: ", promt2="Confirm key for file: ", promt3="Keys don't match\n"):
    key1 = getpass(promt1)
    key2 = getpass(promt2)
    while key1 != key2:
        print(promt3)
        key1 = getpass(promt1)
        key2 = getpass(promt2)
    else:
        return key1


def encrypt_file(decrypted_in, encrypted_out, key):
    pyAesCrypt.encryptFile(decrypted_in, encrypted_out, key, 1024*64)


def decrypt_file(encrypted_in, decrypted_out, key):
    pyAesCrypt.decryptFile(encrypted_in, decrypted_out, key, 1024 * 64)


def send_mail_copy(saved_logins, token, key):  # WORK NEEDED TO SEND ATTACHMENT FO FILES -------------------------------
    print("Currently this option only works with gmail, and you have to turn on 'Allow less secure apps' ", end="\n\n")
    en = input("Would you like to send the files encrypted? (Recommended option is Y) Y/n")
    if en.lower() == "y":
        message = "Attached here you have encrypted copies of saved_logins and token files" \
                  "\n\nSent by PasswordManager."
        token_file = "x"
        logins_file = "y"
    elif en.lower() == "n":
        message = "Attached here you have encrypted copies of saved_logins and token files" \
                  "\n\nSent by PasswordManager."
    else:
        print("Didn't recognize that answer, preceding sending encrypted files")
        message = "Attached here you have encrypted copies of saved_logins and token files" \
                  "\n\nSent by PasswordManager."
        token_file = "x"
        logins_file = "y"

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
        key = ""
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
        token.close()
        token = open("token", "r")
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
    return token, logins, key


def hash256(key):  # Hashes a given key with sha512
    key_to_hash = sha3_512(key.encode(encoding="UTF-8")).hexdigest()
    return key_to_hash


def check_key(token_f):  # Compares the stored hash with the user hash
    stored_hash = token_f.read()  # File not readable after creating new token file
    if stored_hash.__len__() != 128:
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
    chars = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNPQRSTUVWXYZ!@#$%^&*()/-_.:?"
    special_chars = "!@#$%^&*()/-_.:?"
    nums = "01234567890"
    x = 0
    y = 0
    while x == 0 or y == 0:  # Makes sure at least one number and one special character is present
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
        option_ = input("Would you like a new random password? Y/n: ")
        if option_.lower() == "n":
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
        new_value = "hfnguiesghnsiouegnsiuepogsgsueignseuigoesnugiose"
        print("That wasn't a valid option")

    if new_value != "hfnguiesghnsiouegnsiuepogsgsueignseuigoesnugiose":
        csv_value_change(record_to_change, field_to_change, new_value, unenc)

    encrypt_file(unenc, "saved_logins", key)
    os.remove(unenc)


def delete_record(logins_f, key):
    readall_passwords(logins_f.name, key)
    record_to_delete = int(input("Which record do you want to delete? "))
    confirm = input("Are you sure you want to delete row number %s ? Y/n: " % record_to_delete)
    record_to_delete += 1
    if confirm.lower() == "y":
        row_c = 0
        temp_file = open("temp", "a")
        decrypt_file(logins_file.name, "unenc", key)
        unenc = open("unenc", "r")
        for row in unenc:
            if row_c != record_to_delete:
                temp_file.write(row)
            row_c += 1
        unenc.close()
        temp_file.close()
        os.remove(unenc.name)
        encrypt_file(temp_file.name, logins_file.name, key)
        # os.remove(temp_file.name)


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
    return new_key


def delete_at_exit_safe():
    if os.path.isfile("unenc"):
        os.remove("unenc")
    elif os.path.isfile("temp"):
        os.remove("temp")


def delete_files(token_f, logins_f, key):
    confirm = input("Are you sure you want to delete the files? Type CONFIRM to continue: ")
    if confirm == "CONFIRM":
        pass_confirm = getpass("Please enter your key to continue: ")
        if pass_confirm == key:
            token_f.close()
            logins_f.close()
            os.remove(logins_f.name)
            os.remove(token_f.name)
            exit(0)
        else:
            print("Keys don't match")
            sleep(1.5)


def move_record(logins_f, key):
    logins_fname = logins_f.name
    readall_passwords(logins_fname, key)
    record_to_move = int(input("Which record would you like to move? ")) + 1
    new_position = int(input("Where would you like to move this record? ")) + 1
    row_c = 0
    decrypt_file(logins_fname, "unenc", key)
    unenc = open("unenc", "r")
    row_to_move = ""
    for row in unenc:  # First loop to find the row we want to move
        if row_c == record_to_move:
            row_to_move = row
            break
        row_c += 1
    unenc.close()
    if row_to_move != "":
        row_c = 0
        temp_file = open("temp", "w", newline="")
        decrypt_file(logins_fname, "unenc", key)
        unenc = open("unenc", "r")
        for row in unenc:
            if row_c == new_position:
                if row_to_move.endswith("\n"):  # Checks if there is already \n to avoid extra blank spaces
                    temp_file.write(row_to_move)
                else:
                    temp_file.write(row_to_move + "\n")
                temp_file.write(row)
            elif row_c != record_to_move and row != "":
                temp_file.write(row)
            print(row)
            row_c += 1
        unenc.close()
        temp_file.close()
        os.remove(unenc.name)
        os.remove(temp_file.name)
        encrypt_file(temp_file.name, logins_file.name, key)
    else:
        print("Couldn't find the selected record")
        sleep(2)


def clear_console():
    try:
        clear()
    except NameError:
        pass


def local_backup(logins_f, token_f, key):
    home_path = os.path.expanduser("~")
    default_path = home_path + "\\Documents\\PasswordManager_Backup\\"
    user_path = input("Please enter the directory for the back up ( C:\\Path\\To\\Folder\\ ) "
                      "or leave blank for default:")
    if user_path == "":
        print("Using default path")
        path2use = default_path
    elif os.path.exists(user_path):
        path2use = user_path
    elif not os.path.exists(user_path):
        print("Could not locate that path. Using default path")
        path2use = default_path
    else:
        print("Unknown error, using default path")
        path2use = default_path

    enc = input("Would you like to save the backup (E)ncrypted or (D)ecrypted (Encrypted is strongly recommended) :")
    datetime_ = (str(datetime.now()).replace(" ", "_").replace(":", "-"))[:-7]
    backup_name = logins_f.name + datetime_

    try:
        os.makedirs(path2use)
    except FileExistsError:
        pass

    if enc.lower() == "e":
        print("Copying files encrypted to " + path2use)
        shutil.copy(logins_f.name, path2use + backup_name)
        shutil.copy(token_f.name, path2use + token_file.name + datetime_)
    elif enc.lower() == "d":
        print("Decrypting files")
        w = 0
        key_conf = getpass("Please confirm your key: ")
        while key_conf != key:
            w += 1
            if w == 3:
                print("Too many tries")
                exit()
            print("Keys dont match")
            key_conf = getpass("Please confirm your key: ")
        decrypt_file(logins_f.name, "temp", key)
        print("Copying decrypted files to " + path2use)
        shutil.copy("temp", path2use + backup_name)
        os.remove("temp")
    else:
        print("Unexpected error, please try again")

    sleep(2)


def import_backup(key):
    confirm = input("This will delete any data present. Are you sure you want to continue? Y/n: ")

    if confirm.lower() == "y":

        w = 0
        key_conf = getpass("Please confirm your key: ")
        while key_conf != key:
            w += 1
            if w == 3:
                print("Too many tries")
                exit()
            print("Keys dont match")
            key_conf = getpass("Please confirm your key: ")

        path_to_backup = input("Please type the path to the logins backup or leave blank for default " 
                               "(C:\\Path\\To\\Folder\\File) ")

        if path_to_backup == "":
            print("No input, trying default folder")
            home_path = os.path.expanduser("~")
            default_path = home_path + "\\Documents\\PasswordManager_Backup\\"
            name = input("Please type the name of the backup file")
            if os.path.exists(default_path + name):
                print("saved_logins file found at default folder")
                saved_logins_file = open(default_path + "saved_logins", "r")
        else:
            saved_logins_file = open(path_to_backup)

        try:
            csv.reader(saved_logins_file)
            decrypted = True
        except UnicodeDecodeError:
            decrypted = False

        if decrypted:
            print("File detected as decrypted, new key required to continue")
            key = double_check("New key: ", "Confirm new key: ", "Keys don't match\n")
            encrypt_file(saved_logins_file.name, "saved_logins", key)
            with open("token", "w") as token:
                token.write(hash256(key))
        elif not decrypted:
            print("File detected as encrypted")
            token_file_name =
        elif os.path.exists(path_to_backup + "token"):
            print("Could not locate token file")
    else:
        print("Exiting")


version = "v0.0.5"
if platform.system() == "Windows":
    def clear(): os.system('cls')  # Windows
elif platform.system() == ("Linux" or "macosx"):
    def clear(): os.system('clear')  # Linux
else:
    print("Could not detect os system. App may not function properly")
    sleep(1)


clear_console()

token_file, logins_file, key_ = sc_files()
if key_ == "":  # ???
    key_ = check_key(token_file)

accepted_options = "1234567890"

while True:  # Main loop
    clear_console()
    print("1) Read saved logins      2) Add new record\n3) Edit existing record   4) Delete record")  # Options
    print("5) Change key             6) Delete all files\n7) Move record            8) Create backup")
    print("9) Import backup")
    print("0) Exit")
    option = input("-> ", )

    if option.isdigit():
        option_is_int = True
        option = int(option)
    else:
        option_is_int = False

    clear_console()

    if str(option) in accepted_options:
        if option_is_int:
            if not 10 > option >= 0:  # Check option is between the acceptable values
                pass
            elif option == 1:  # Run option
                readall_passwords(logins_file.name, key_)
                x = input("\nPress enter to continue")
            elif option == 2:
                add_new_record(logins_file, key_)
            elif option == 3:
                edit_record(logins_file, key_)
            elif option == 4:
                delete_record(logins_file, key_)
            elif option == 5:
                key_ = change_key(key_)
            elif option == 6:
                delete_files(token_file, logins_file, key_)
            elif option == 7:
                move_record(logins_file, key_)
            elif option == 8:
                local_backup(logins_file, token_file, key_)
            elif option == 9:
                import_backup(key_)
            elif option == 0:
                break
        else:
            if option.lower() == "a":
                pass
    else:
        print("%s isn't a supported option" % option)
        x = input("Press Enter to continue")

key_ = ""
clear_console()
