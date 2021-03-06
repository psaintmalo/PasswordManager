print("\nLoading packages\n")
print("Loading os")
import os
print("Loading csv")
import csv
print("Loading sys")
import sys
print("Loading shutil")
import shutil
# print("Loading smtplib")
# import smtplib
print("Loading pandas")
import pandas as pd
print("Loading FTP")
from ftplib import FTP
print("Loading time")
from time import sleep
print("Loading random")
from random import sample
print("Loading getpass")
from getpass import getpass
print("Loading platform")
from platform import system
print("Loading hashlib")
from hashlib import sha3_512
print("Loading datetime")
from datetime import datetime
print("Loading checker")
from checker import check_h, warning_msg
print("Loading bcrypt")
from bcrypt import gensalt, checkpw, hashpw
print("Loading pyAesCrypt")
from pyAesCrypt import encryptFile, decryptFile

print("Loading complete")


def double_check(first_promnt="Key: ", confirm_promnt="Confirm key: ", dont_match_promt="Keys don't match\n"
                 , attempts_limit=3):
    y = 0
    key1 = getpass(first_promnt)
    key2 = getpass(confirm_promnt)
    while key1 != key2:
        y += 1
        if y == attempts_limit:
            exit("Too many attempts")
        print(dont_match_promt)
        key1 = getpass(first_promnt)
        key2 = getpass(confirm_promnt)
    else:
        return key1


def encrypt_file(decrypted_in, encrypted_out, key):
    encryptFile(decrypted_in, encrypted_out, key, 1024*64)


def decrypt_file(encrypted_in, decrypted_out, key):
    decryptFile(encrypted_in, decrypted_out, key, 1024*64)


'''
def send_mail_copy(saved_logins, token, key):
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
'''


def create_logins_file(key):
    with open("unenc", "w") as new_logins:
        new_logins.write("Website,Mail,User,Password,Notes\n")
    encrypt_file("unenc", "saved_logins", key)
    os.remove("unenc")
    return open("saved_logins", "r")


def new_token():
    key = getpass("\nPlease enter your new key: ")
    
    while True:
        if len(key) < 8:
            print("Its recommended to use a password with atleast 8 characters")
            key_conf = getpass("Enter a new key or type the last key again to use it: ")
            if key == key_conf:
                break
            else:
                key = key_conf
                
        else:
            key_conf = getpass("Confirm your key: ")
            if key == key_conf:
                break
            else:
                print("Key's dont match")
        
    return key


def sc_files():  # Check password files and key_hash present and returns their values

    if os.path.exists("saved_logins") and os.path.exists("token"):
        logins = open("saved_logins", "r")
        token = open("token", "r")
        key = ""
    elif not os.path.exists("saved_logins"):
        print("saved_logins file is missing, creating new logins and token file.")
        key = new_token()
        token = open("token", "w")
        token.write(str(hashpw(key.encode("utf8"), gensalt(11))))
        token.close()
        token = open("token", "r")
        logins = create_logins_file(key)

    elif not os.path.exists("token"):
        option_ = input("token file is missing, would you like to format all data? Y/n: ")
        if option_.lower() == "y":
            key = new_token()
            token = open("token", "w")
            token.write(str(hashpw(key.encode("utf8"), gensalt(11))))
            logins = create_logins_file(key)
            token.close()
        else:
            print("Cannot continue without the token file")
            exit(0)

    # noinspection PyUnboundLocalVariable
    return token, logins, key


def hash256(key):  # Hashes a given key with sha512
    key_to_hash = sha3_512(key.encode(encoding="UTF-8")).hexdigest()
    return key_to_hash


def check_key():  # Compares the stored hash with the user hash
    token_f = open("token", "rb")
    stored_hash = token_f.read()[2:-1]  # File not readable after creating new token file
    # print(stored_hash.__len__())
    if stored_hash.__len__() == 128:
        print("Old hash found, checking...")
        user_key = input("Please enter your key: ")
        hashed_key = hash256(user_key)
        xyz = 1
        while hashed_key != stored_hash:
            if xyz == 3:
                exit("Too many tries.")
            else:
                user_key = getpass("Your key didn't match the saved key. Please try again: ")
                hashed_key = hash256(user_key)
                xyz += 1
        print("Saving new hash")
        tokenf = open("token", "w+")
        tokenf.write(str(hashpw(user_key.encode("utf8"), gensalt(11))))
        tokenf.close()

    elif stored_hash.__len__() != 60:
        print("No compatible key stored. New key needed. (This will format any stored password's)\n")
        token_f.close()
        while True:
            key = getpass(u"Please insert the key you would like to use to lock/unlock the list:  ")
            key_c = getpass(u"Confirm your key: ")
            if key != key_c:
                print("Key's didn't match\n")
            else:
                break
        print("Saving new key")
        open("saved_logins", "w+")
        tokenf = open("token", "w+")
        tokenf.write(str(hashpw(key.encode("utf8"), gensalt(11))))

        user_key = key

    else:
        user_key = getpass("Please enter your key: ")
        xyz = 0
        no_match = True
        while no_match:
            xyz += 1
            if xyz == 3:
                exit("Too many tries.")
            else:
                if checkpw(user_key.encode("utf8"), stored_hash):
                    break
                else:
                    user_key = getpass("Wrong key, please try again: ")

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


def csv_value_change(x_, y, value, file_name):
    f = open(file_name, "r")
    csv_read = csv.reader(f)
    lines = list(csv_read)
    lines[x_ + 1][y] = value
    new_csv_ = open(f.name, "w", newline="")
    writer = csv.writer(new_csv_)
    writer.writerows(lines)


def generate_random_pass(length):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNPQRSTUVWXYZ!@#$%^&*()/-_.:?+"
    special_chars = "!@#$%^&*()/-_.:?+"
    nums = "01234567890"
    caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ran_pass = ""
    x_ = 0
    y = 0
    z = 0
    while x_ == 0 or y == 0 or z == 0:  # Makes sure at least one number and one special character is present
        x_ = 0
        y = 0
        z = 0
        ran_pass = "".join(sample(chars, length))
        for char in ran_pass:
            if char in special_chars:
                x_ += 1
            elif char in nums:
                y += 1
            elif char in caps:
                z += 1

    return ran_pass


def add_new_record(logins_f, key, columns_):
    values = []
    for field in columns_:
        if field.lower() != "password":
            values.append(input("%s: " % field.capitalize()))
        else:
            random_pass_opt = input("Would you like a random generated password? Y/n: ")
            
            if random_pass_opt.lower() == "y":
                length = input("How long would you like the password to be? Leave blank for default length:  ")
                if length == "":
                    length = 14
                password = generate_random_pass(int(length))
                print("Your new password is:\n%s" % password)
                
            elif random_pass_opt.lower() == "n":
                password = getpass("Password: ")
                
            else:
                print("Not an option. Continuing with manual password\n")
                password = getpass("Password: ")
                
            values.append(password)
    
    for value in values:
        while "," in value:
            pos = values.index(value)
            print("\n',' may not be entered into any field")
            value = input("New value for %s: " % (columns_[pos]))
            values[pos] = value
    
    write_str = ""
    for a in values:
        write_str += a + ","
    write_str = write_str[:-1]
    write_str += "\n"
    decrypt_file(logins_f.name, "unenc", key)
    new_file = open("unenc", "a")
    new_file.write(write_str)
    new_file.close()
    encrypt_file(new_file.name, logins_f.name, key)
    os.remove(new_file.name)


def edit_record(logins_f, key, columns_):
    pos = 0
    unenc = "unenc"
    encrypted_logins = logins_f.name
    decrypt_file(encrypted_logins, unenc, key)
    read_csv(unenc)
    record_to_change = input("No of record to edit: ")
    while not record_to_change.isdigit():
        print("\nShould be a number")
        record_to_change = input("No of record to edit: ")
    record_to_change = int(record_to_change)
        
    field_to_change = input("Name of the column to edit: ") 

    try:
        pos = columns_.index(field_to_change.lower())
        found = True
    except ValueError:
        print("Column not found")
        
        try:
            pos = int(input("Enter the position of the column (1-%s): " % len(columns_))) - 1
            found = True
        except IndexError:
            print("Column not found")
            found = False
        
    if found:
    
        if columns_[pos].lower != "password":
            new_value = input("New value for '%s': " % columns_[pos])
        else:
        
            option_ = input("Would you like a new random password? Y/n: ")
            if option_.lower() == "n":
                new_value = getpass("New value for the Password: ")
            else:
                length = input("How long would you like the password to be? Leave blank for default length: ")
                if length == "":
                    length = 12
                else:
                    length = int(length)
                    
                new_value = generate_random_pass(length)
        
        while "," in new_value:
            print("\nValues cannot contain ','")
            new_value = input("New value for '%s': " % columns_[pos])
        csv_value_change(record_to_change, pos, new_value, unenc)

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
        os.remove(temp_file.name)


def change_key(key):
    print("After changing the key, you will have to re-open the program")
    old_key = getpass("Please enter your old key: ")
    counter = 0
    while old_key != key:
        counter += 1
        print("Incorrect key")
        old_key = getpass("\nPlease enter your old key: ")
        if counter == 3:
            exit("Too many attempts")
    new_key = new_token()

    with open("token", "w+") as f:
        f.write(str(hashpw(new_key.encode("utf8"), gensalt(11))))
    decrypt_file("saved_logins", "temp", key)
    encrypt_file("temp", "saved_logins", new_key)
    os.remove("temp")
    return new_key


def delete_files(token_f, logins_f, key):
    print("FTP Files will not be deleted, please do so manually or with option 'J' on the main menu")
    pass_confirm = getpass("All data will be deleted, type your key to continue or 'x' to cancel: ")
    if pass_confirm == key:
        token_f.close()
        logins_f.close()
        os.remove(logins_f.name)
        os.remove(token_f.name)
        if os.path.exists("ftp.conf"):
            os.remove("ftp.conf")
        exit(0)
    elif option.lower() == "x":
        pass
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
            row_c += 1
        unenc.close()
        temp_file.close()
        encrypt_file(temp_file.name, logins_file.name, key)
        os.remove(unenc.name)
        os.remove(temp_file.name)
    else:
        print("Couldn't find the selected record")
        sleep(2)


def local_backup(logins_f, token_f, key):
    global os_sys
    backup_name = ""
    token_back_name = ""
    home_path = os.path.expanduser("~")
    if os_sys in ["windows"]:
        path = home_path + "\\Documents\\PasswordManager_Backup\\"

    else:
        path = home_path + "/Documents/PasswordManager_Backup/"

    enc = input("Would you like to save the backup (E)ncrypted or (D)ecrypted: ")
    custom_name_opt = input("Would you like to save files with (A)utomatically generated names or (C)ustom names: ")
    if custom_name_opt.lower() == "c":
        backup_name = input("Please enter name for saved_logins file: ")
        if enc.lower() == "e":
            token_back_name = input("Please enter name for taken file: ")
    elif custom_name_opt.lower() == "a":
        datetime_ = (str(datetime.now()).replace(" ", "_").replace(":", "-"))[:-7]
        backup_name = logins_f.name + datetime_
        token_back_name = token_f.name + datetime_
    else:
        enc = "a"

    try:
        os.makedirs(path)
    except FileExistsError:
        pass

    if enc.lower() == "e":
        print("Copying token file to " + path)
        shutil.copy(logins_f.name, path + backup_name)
        shutil.copy(token_f.name, path + token_back_name)
    elif enc.lower() == "d":
        print("Decrypting files")
        w = 0
        key_conf = getpass("Please type your key: ")
        while key_conf != key:
            w += 1
            if w == 3:
                exit("To many attempts")
            print("Keys dont match")
            key_conf = getpass("Please confirm your key: ")
        decrypt_file(logins_f.name, "temp", key)
        print("Copying decrypted files to " + path + backup_name)
        shutil.copy("temp", path + backup_name)
        os.remove("temp")
        input("Press enter to continue")
    else:
        print("Unexpected error, please try again")

    input("\nPress enter to continue")


def import_backup(key, token_f, saved_logins_f):
    global os_sys
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
            
        home_path = os.path.expanduser("~")
            
        if os_sys in ["windows"]:
            path = home_path + "\\Documents\\PasswordManager_Backup\\"

        #  if os_sys in ["macosx darwin linux"]:
        else:
            path = home_path + "/Documents/PasswordManager_Backup/"
            
        saved_l_name = input("Please type the name of the saved_logins backup file: ")
        
        if os.path.exists(path + saved_l_name):
            print("saved_logins file found")
            saved_logins_path = path + saved_l_name
            saved_logins_file = open(saved_logins_path, "r")
        else:
            
            print("Could not find file")
            
            if os_sys in ["windows"]:
                path = input("Could not find file, type the location of the file C:\\Path\\To\\Folder\\")
            #  if os_sys in ["macosx darwin linux"]:
            else:
                path = input("Could not find file, type the location of the file /Path/To/Folder/")
                
            if os.path.exists(path):
                print("saved_logins file found")
                saved_logins_path = path + saved_l_name
                saved_logins_file = open(saved_logins_path, "r")
            else:
                exit("Couldn't find path to file")
                saved_logins_file = ""

        decrypted = True
        try:
            for line in saved_logins_file:
                del line
                break

        except UnicodeDecodeError:
            decrypted = False
            
        if decrypted:
            print("File detected as decrypted, new key required to continue")
            key = double_check("New key: ", "Confirm new key: ", "Keys don't match\n", -1)
            encrypt_file(saved_logins_file.name, "saved_logins", key)
            delete_old = input("Do you want to delete the backup file? Y/n: ")
            if delete_old.lower() == "y":
                os.remove(saved_logins_file.name)
            with open("token", "w") as token:
                token.write(str(hashpw(key.encode("utf8"), gensalt(11))))
            print("Import successful")
                
        elif not decrypted:
            print("File detected as encrypted")
            token_path = path + "token" + saved_l_name[-19:]
            
            if not os.path.exists(token_path):
                token_name = input("Please type the name of the token file: ")
                token_path = path + token_name
                if not os.path.exists(token_path):
                    
                    if os_sys in ["windows"]:
                        path = input("Could not find file, type the location of the file C:\\Path\\To\\Folder\\")
                    #  if os_sys in ["macosx darwin linux"]:
                    else:
                        path = input("Could not find file, type the location of the file /Path/To/Folder/")
                        
                    if not os.path.exists(path + token_name):
                        exit("Could not find file")
                
            backup_token = open(token_path, "r").read()
            print("Token file found")
            abc = 0
            backup_key = getpass("Please input the key used in this backup: ")
            while checkpw(backup_token, hashpw(backup_key.encode("utf8"), gensalt(11))):
                abc += 1
                backup_key = getpass("Keys don't match, please try again:")
                # print(backup_token, hashpw(backup_key.encode("utf8"), gensalt(11)))
                if abc == 3:
                    print("If you have forgotten the key type leave to exit the backup import,"
                          " or type another key to try again.")
                    exit_ = getpass(": ")
                    if exit_.lower() != "leave":
                        backup_key = exit_
                    else:
                        break
            else:
                print("Keys match")
                os.remove(token_f.name)
                os.remove(saved_logins_f.name)
                shutil.copy(token_path, "token")
                shutil.copy(saved_logins_path, "saved_logins")
                remove_old = input("Would you like to delete the backup from the old directory? Y/n: ")
                if remove_old.lower() == "y":
                    os.remove(token_path)
                    os.remove(saved_logins_path)
                print("Import successful")
        
    input("Press enter to continue")


def add_new_column(saved_logins_f, key):
    column_name = input("Name for the new column: ")
    while not column_name or column_name.isspace():
        print("Column name cannot be left blank")
        print("To exit type _exit_")
        column_name = input("Name for the new column: ")
        if column_name == "_exit_":
            break
    else:
        decrypt_file(saved_logins_f.name, "unenc", key)
        unenc_f = open("unenc", "r")
        with open("temp", "w") as f:
            x_ = 0

            for row in unenc_f:
                n = "\n"
                if x_ == 0:
                    x_ += 1
                    new_row = (row[:-1] + ",%s" % column_name + n)
                    f.write(new_row)
                else:
                    new_row = row[:-1] + "," + n
                    f.write(new_row)

                del x_
                f.flush()

        encrypt_file("temp", saved_logins_f.name, key)
        os.remove("temp")
        os.remove("unenc")
    
    
def delete_column(saved_logins_f, key, header_list):
    
    for item in header_list:
        print(item.capitalize(), end=" ")
    else:
        print("")
        
    column_name = input("\nName of the column you want to remove: ").lower()

    try:
        index2remove = header_list.index(column_name)
        decrypt_file(saved_logins_f.name, "temp", key)
        with open("temp", "r") as source:
            os.remove("temp")
            rdr = csv.reader(source)
            with open("result", "w") as result:
                wtr = csv.writer(result)
                for r in rdr:
                    write = r[:index2remove] + r[(index2remove + 1):]
                    wtr.writerow(write)

        encrypt_file("result", "saved_logins", key)
        os.remove("result")

    except ValueError:
        print("That wasn't a valid column")
        input("Press enter to continue")


def get_columns(saved_logins_f, key):
    decrypt_file(saved_logins_f.name, "temp", key)
    with open("temp", "r") as file:
        for row in file:
            header = row[:-1].split(",")
            break
    os.remove("temp")
    return [i.lower() for i in header]


'''
def check_appropiate_data(input, data_type, message="That data wasn't appropriate, please type it again",
                          possible_values = ""):
    accepted_types = ("number", "text")
    if data_type in accepted_types:
        if data_type == "number":
            def x(x): return isinstance(x, int)
        elif data_type == "text":
            pass
'''


def search(saved_logins_f, columns_, key):

    try:
        search_mode = int(input("Would you like to search in a column (1) or in all fields (2): "))
    except ValueError:
        while True:
            try:
                search_mode = int(input("Please select to search in a column (1) or in all fields (2): "))
                break
            except ValueError:
                pass

    search_term = input("\nTerm to search: ")

    num_col = len(columns_)

    if search_mode == 2:

        decrypt_file(saved_logins_f.name, "temp", key)
        with open("temp", "r") as temp:
            os.remove("temp")
            print()
            x = -1

            for line in temp:
                if x != -1:
                    if search_term in line:
                        splitted = line.split(",")
                        print("\nMatch found at line %s:" % x)
                        for i in range(num_col):
                            print("{}: {}    ".format(columns[i].capitalize(), splitted[i]), end="")
                x += 1

    elif search_mode == 1:

        print("\n ", end="")
        for i in columns_:
            print(i.capitalize(), end="   ")
        print("")

        column2search = input("\nName of the column to search: ").lower()

        try:
            pos = columns_.index(column2search.lower())
        except ValueError:
            print("Column not found")
            while True:
                try:
                    pos = int(input("Enter the position of the column (1-%s): " % len(columns_))) - 1
                    break
                except IndexError:
                    print("Column not found")

        decrypt_file(saved_logins_f.name, "temp", key)
        with open("temp", "r") as temp:
            os.remove("temp")
            print()
            x = -1
            for line in temp:
                if x != -1:
                    splitted = line.split(",")
                    if search_term in splitted[pos]:
                        print("\nMatch found at line %s:" % x)
                        for i in range(num_col):
                            print("{}: {}    ".format(columns[i].capitalize(), splitted[i]), end="")
                x += 1

    else:
        print("Couldnt find the specified column")

    input("\nPress enter to continue")


def configure_ftp(key):
    configure = True
    if os.path.exists("ftp.conf"):
        override = input("This will override your old ftp configuration file, do you want to continue (Y/n): ")
        if override.lower() == "n":
            configure = False

    if configure:

        config = []

        server = input("Enter IP or domain of the ftp server: ")

        port = input("Enter the port of the ftp server (default = 21): ")
        if port == "":
            port = "21"

        user = input("Enter the username of the ftp server: ")

        passw = getpass("Enter password for the ftp server: ")

        auto_sync = input("Would you like to automatically sync with the FTP Server (May impact performance)"
                          " (Y/n): ").lower()

        if auto_sync == "y":
            auto_sync = True
        else:
            auto_sync = False

        config.append('server=%s\n' % server)
        config.append('port=%s\n' % port)
        config.append('user=%s\n' % user)
        config.append('passw=%s\n' % passw)
        config.append('auto_sync=%s\n' % auto_sync)

        with open("conf", "w+") as conf:
            for line in range(len(config)):
                conf.write(config[line])

        encrypt_file("conf", "ftp.conf", key)
        os.remove("conf")


def pull_ftp(server, port, user, passw):

    try:
        x_ = True
        cancel = False

        print("\nConnecting to server\n")
        ftp = FTP()
        print(ftp.connect(server, int(port)))
        print("\nLogging in\n")
        print(ftp.login(user, passw))
        print("\nChecking token")

        with open("token_f", "wb") as f:
            ftp.retrbinary("RETR " + "token", f.write)

        token = open("token", "r")
        token_f = open("token_f", "r")

        if token.read() != token_f.read():
            yn = input("Seems the key stored on the FTP Server isn't the same as the one locally,"
                       " do you want to continue (Y/n): ").lower()

            if yn == "y":
                cancel = True

        os.remove("token_f")

        if x_:
            with open("token", "wb") as f:
                ftp.retrbinary("RETR " + "token", f.write)

            with open("saved_logins", "wb") as f:
                ftp.retrbinary("RETR " + "saved_logins", f.write)

            ftp.quit()
            print("Files retrieved successfully")
            sleep(1)
    except:
        print("\nUnexpected error: ", sys.exc_info()[0])
        opt = input("Press enter to continue or 'X' to get error details: ")
        if opt.lower() == "x":
            print("\n    -------- Error Info -------- \n")
            raise

    if cancel:
        exit("Its necessary to restart the program")

    return cancel


def push_ftp(server, port, user, passw, token_name="token", saved_logins_name = "saved_logins"):
    try:
        print("Connecting to server")
        ftp = FTP()

        ftp.connect(server, int(port))
        print("Logging in")
        ftp.login(user, passw)
        print("Uploading files")

        with open('token', 'rb') as f:
            ftp.storbinary('STOR %s' % token_name, f)

        with open('saved_logins', 'rb') as f:
            ftp.storbinary('STOR %s' % saved_logins_name, f)

        ftp.quit()
        print("Files sent succesfully")
        sleep(1)
    except:
        print("\nUnexpected error: ", sys.exc_info()[0])
        opt = input("Press enter to continue or 'X' to get error details: ")
        if opt.lower() == "x":
            print("\n    -------- Error Info -------- \n")
            raise


def silent_push(server, port, user, passw):
    try:
        ftp = FTP()
        ftp.connect(server, int(port))
        ftp.login(user, passw)
        with open('token', 'rb') as f:
            ftp.storbinary('STOR %s' % 'token', f)
        with open('saved_logins', 'rb') as f:
            ftp.storbinary('STOR %s' % 'saved_logins', f)
        ftp.quit()
    except:
        pass


def check_ftp(server, port, user, passw):
    try:
        print("Connecting to server\n")
        ftp = FTP()
        print(ftp.connect(server, int(port)))
        print("\nLogging in\n")
        print(ftp.login(user, passw))
        ftp.quit()
        input("\nPress enter to continue")
    except:
        print("\nUnexpected error: ", sys.exc_info()[0])
        opt = input("Press enter to continue or 'X' to get error details: ")
        if opt.lower() == "x":
            print("\n    -------- Error Info -------- \n")
            raise


def load_ftp_config(key):
    if os.path.exists("ftp.conf"):
        print("FTP Configuration detected")
        print("Loading FTP Configuration")
        decrypt_file("ftp.conf", "ftp_conf.py", key)

        # New method for getting the data

        with open("ftp_conf.py", "r") as file:
            for line in file:
                contents = line.split("=")
                contents[1] = contents[1][:-1]
                if "server" in contents:
                    server = contents[1]
                elif "port" in contents:
                    port = contents[1]
                elif "user" in contents:
                    user = contents[1]
                elif "passw" in contents:
                    passw = contents[1]
                elif "auto_sync" in contents:
                    auto = contents[1]
                    if auto == "True":
                        auto_sync = True
                    else:
                        auto_sync = False

        # Old method

        # import ftp_conf
        # server = ftp_conf.server
        # port = ftp_conf.port
        # user = ftp_conf.user
        # passw = ftp_conf.passw
        # auto_sync = ftp_conf.auto_sync
        # del ftp_conf

        os.remove("ftp_conf.py")
    else:
        print("No FTP Configuration file found")

    return server, port, user, passw, auto_sync


def show_ftp_options(server_, port_, user_, passw_, auto_sync_):
    print("Server: {serverx}\nPort: {portx}\nUser: {userx}\nPassword: {passwd} \nAuto Sync: {a_s}".
          format(serverx=server_, portx=port_, userx=user_, a_s=auto_sync_,
                 passwd="*" * len(passw_)), end="\n\n")
    input("Press enter to continue ")


def delete_ftp_files(server_, port_, user_, passw_):
    print("This will not delete any backup files you may have saved there.")
    opt = input("Would you like to remove the FTP Configuration? Y/n: ").lower()
    if opt != "y" and opt != "n":
        print("Not an acceptable option, continuing without deleting configuration")
    cont = input("Are you sure you want to delete the files? Y/n: ").lower()
    if cont != "y" and cont != "n":
        print("That wasn't an acceptable option")
        cont = input("Are you sure you want to delete the files? Y/n: ").lower()

    if cont == "y":
        try:
            print("Connecting to server")
            ftp = FTP()

            ftp.connect(server_, int(port_))
            print("Logging in")
            ftp.login(user_, passw_)
            print("Deleting files")

            ftp.delete("token")
            ftp.delete("saved_logins")

            if opt == "y":
                os.remove("ftp.conf")
            elif opt != "n":
                print("Not an acceptable option, continuing without deleting")

            ftp.quit()
            print("Files deleted")
            sleep(1)
        except:
            print("\nUnexpected error: ", sys.exc_info()[0])
            opt = input("Press enter to continue or 'X' to get error details: ")
            if opt.lower() == "x":
                print("\n    -------- Error Info -------- \n")
                raise


def make_ftp_backup(server_, port_, user_, passw_, key):
    stop = False
    datetime_ = (str(datetime.now()).replace(" ", "_").replace(":", "-"))[:-7]

    enc = input("Would you like the backup to be (E)ncrypted or (D)ecrypted: ")
    custom_name_opt = input("Would you like an (A)utomatically name or a (C)ustom name: ")

    if custom_name_opt.lower() == "a":
        token_backup_name = "token" + datetime_
        backup_name = "saved_logins" + datetime_
        print("\nSaved_logins will be saved as: ", backup_name)
        print("Token will be saved as: %s\n" % token_backup_name)

    elif custom_name_opt.lower() == "c":
        backup_name = input("Name for 'saved_logins' file: ")
        if enc == "e":
            token_backup_name = input("Name for 'token' file: ")
        elif enc != "d":
            stop = True

    else:
        stop = True

    if not stop:
        try:
            ftp = FTP()
            ftp.connect(server_, int(port_))
            ftp.login(user_, passw_)

            if enc == "e":
                with open('saved_logins', 'rb') as f:
                    ftp.storbinary('STOR %s' % backup_name, f)
                with open('token', 'rb') as t:
                    ftp.storbinary('STOR %s' % token_backup_name, t)
            else:
                decrypt_file("saved_logins", "temp", key)
                with open('temp', 'rb') as f:
                    ftp.storbinary('STOR %s' % backup_name, f)

        except:
            print("\nUnexpected error: ", sys.exc_info()[0])
            opt = input("Press enter to continue or 'X' to get error details: ")
            if opt.lower() == "x":
                print("\n    -------- Error Info -------- \n")
                raise

    if stop:
        print("An error has occurred")


def import_ftp_backup(server_, port_, user_, passw_, key):
    stop = False
    enc = input("Is the backup (E)ncrypted or (D)ecrypted: ").lower()
    while enc != "e" and enc != "d":
        print("Unsupported option")
        enc = input("Please select 'E' for encrypted or 'D' for decrypted or 'X' to cancel: ").lower()
        if enc == "x":
            stop = True

    if not stop:
        backup_name = input("Name of the 'saved_logins' file: ")
        if enc == "e":
            token_backup_name = input("Name of the 'token' file: ")

        try:
            cancel = False

            print("\nConnecting to server\n")
            ftp = FTP()
            print(ftp.connect(server_, int(port_)))
            print("\nLogging in\n")
            print(ftp.login(user_, passw_))
            print("\nChecking token")

            if enc == "e":
                with open("token_f", "wb") as f:
                    ftp.retrbinary("RETR " + token_backup_name, f.write)

                token = open("token", "r")
                token_f = open("token_f", "r")

                if token.read() != token_f.read():
                    yn = input("Seems the key stored on the FTP Server isn't the same as the one locally,"
                               " do you want to continue (Y/n): ").lower()

                    if yn == "y":
                        cancel = True

                os.remove("token_f")

                print(backup_name + " " + token_backup_name)
                with open("token", "wb") as f:
                    ftp.retrbinary("RETR " + token_backup_name, f.write)

                with open("saved_logins", "wb") as f:
                    ftp.retrbinary("RETR " + backup_name, f.write)

            else:

                print("This file will be encrypted with the current key")

                with open("temp", "wb") as f:
                    ftp.retrbinary("RETR " + backup_name, f.write)
                encrypt_file("temp", "saved_logins", key)

                ftp.quit()
                print("Files retrieved successfully")
                sleep(1)
        except:
            print("\nUnexpected error: ", sys.exc_info()[0])
            opt = input("Press enter to continue or 'X' to get error details: ")
            if opt.lower() == "x":
                print("\n    -------- Error Info -------- \n")
                raise

        if cancel:
            exit("Its necessary to restart the program")

        input("Press enter to continue ")


def delete_ftp_config():
    cont = input("Are you sure you want to continue? Y/n: ").lower()
    if cont != "y" and cont != "n":
        print("That wasnt a valid option")
        cont = input("Are you sure you want to continue? Y/n: ").lower()
        if cont != "y" and cont != "n":
            print("Not a valid option")
            input("Press enter to continue")
            cont = "n"

    if cont == "y":
        os.remove("ftp.conf")


version = "v0.4.0"

if __name__ == "__main__":

    # Defines command to clear console
    os_sys = system().lower()
    if os_sys == "windows":
        def clear_console(): os.system('cls')  # Windows
    elif os_sys in "darwin macosx linux":
        def clear_console(): os.system('clear')  # Linux and Mac
    else:
        clear_command = input("Could not detect os, type command to clear the console or type skip ")
        if clear_command.lower() != "skip":
            def clear_console(): os.system(clear_command)
        else:
            def clear_console(): pass
            print("App may not function properly without the command.")
            sleep(2)

    clear_console()

    header_msg = ""

    # Checks if code has been tampered, and if so warning function is defined to print the message
    warning = check_h()
    if warning:
        def header(): warning_msg()
    else:
        def header(): print(header_msg)

    header()

    # Loads key and files
    token_file, logins_file, key_ = sc_files()
    if key_ == "":  # Checks that no key was given in the process above in result of missing files
        key_ = check_key()

    # Check and if existent, load the ftp configuration
    try:
        server, port, user, passw, auto_sync = load_ftp_config(key_)
        ftp_ = True
    except:
        auto_sync = False
        ftp_ = False

    # Initial pull if auto sync is enabled
    if auto_sync:  # ---------------------------------------------------------------------------------------------------
        cancel_pull = pull_ftp(server, port, user, passw)
        if cancel_pull:
            print("Canceling auto sync")
            auto_sync = False

    columns = get_columns(logins_file, key_)
    accepted_options = "1234567890abcdefghijkl"
    sync_options = "23457ab"

    option_msg = """ 1) Read saved logins         2) Add new record
 3) Edit existing record      4) Delete record
 5) Change key                6) Delete all files
 7) Move record               8) Create backup
 9) Import backup             A) Add new column
 B) Delete column             C) Search
     """

    configure_ftp_menu = "\n D) Configure FTP Server"

    ftp_full_menu = """       
        --------------- FTP ---------------

 D) Configure FTP Server      E) Test FTP Server
 F) Pull from FTP Client      G) Push to FTP Server 
 H) Print Current FTP Config  I) Delete FTP Files
 J) Backup to FTP Server      K) Import backup from FTP
 L) Delete FTP Configuration"""

    exit_menu = "\n\n 0) Exit \n"

    while True:  # Main loop
        clear_console()

        header()

        if ftp_:
            print(option_msg + ftp_full_menu + exit_menu)
        else:
            print(option_msg + configure_ftp_menu + exit_menu)
        option = input(" -> ").replace(" ", "")

        if option.isdigit():
            option_is_int = True
            option = int(option)
        else:
            option_is_int = False

        clear_console()
        header()

        if str(option).lower() in accepted_options:
            if option_is_int:
                if option == 1:  # Run option
                    readall_passwords(logins_file.name, key_)
                    x = input("\nPress enter to continue")
                elif option == 2:
                    add_new_record(logins_file, key_, columns)  # New addition of columns, edit code
                elif option == 3:
                    edit_record(logins_file, key_, columns)  # New addition of columns, edit code
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
                    import_backup(key_, token_file, logins_file)
                elif option == 0:
                    break
            else:
                if option.lower() == "a":
                    add_new_column(logins_file, key_)
                    columns = get_columns(logins_file, key_)
                elif option.lower() == "b":
                    delete_column(logins_file, key_, columns)
                    columns = get_columns(logins_file, key_)
                elif option.lower() == "c":
                    search(logins_file, columns, key_)
                # elif option.lower() == "x":
                #    decrypt_file("saved_logins", "debugging", key_)
                elif option.lower() == "d":
                    configure_ftp(key_)
                    try:
                        server, port, user, passw, auto_sync = load_ftp_config(key_)
                        ftp_ = True
                    except NameError:
                        ftp_ = False
                elif ftp_:
                    if option.lower() == "g":
                        push_ftp(server, port, user, passw)
                    elif option.lower() == "f":
                        pull_ftp(server, port, user, passw)
                    elif option.lower() == "e":
                        check_ftp(server, port, user, passw)
                    # elif option.lower() == "h":
                    #    server, port, user, passw, auto_sync = load_ftp_config(key_)
                    elif option.lower() == "h":
                        show_ftp_options(server, port, user, passw, auto_sync)
                    elif option.lower() == "i":
                        delete_ftp_files(server, port, user, passw)
                    elif option.lower() == "j":
                        make_ftp_backup(server, port, user, passw, key_)
                    elif option.lower() == "k":
                        import_ftp_backup(server, port, user, passw, key_)
                    elif option.lower() == "l":
                        ftp_ = False
                        auto_sync = False
                        delete_ftp_config()
                else:
                    print("\nPlease configure FTP first")
                    input("\nPress enter to continue ")
        else:
            print("\n'%s' isn't a supported option" % option)
            input("\nPress enter to continue ")

        if str(option).lower() in sync_options and auto_sync and ftp_:
            print("\n Syncing to FTP")
            silent_push(server, port, user, passw)

    del key_
    clear_console()

files = ["temp", "unenc", "results", "conf", "__pycache__"]		
for file in files:		
    if os.path.exists(file):		
        try:		
            os.remove(file)		
        except IsADirectoryError:		
            shutil.rmtree(file)
