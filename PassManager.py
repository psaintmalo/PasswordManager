print("\nLoading packages\n")
print("Loading os")
import os
print("Loading csv")
import csv
print("Loading shutil")
import shutil
print("Loading smtplib")
import smtplib
print("Loading pandas")
import pandas as pd
print("Loading time")
from time import sleep
print("Loading random")
from random import sample
print("Loading getpass")
from getpass import getpass
print("Loading platform")
from platform import system
print("Loading haslib")
from hashlib import sha3_512
print("Loading datetime")
from datetime import datetime
print("Loading checker")
from checker import check_h, warning_msg
print("Loading pyAesCrypt")
from pyAesCrypt import encryptFile, decryptFile
print("Loading complete")


def double_check(first_promnt="Key: ", confirm_promnt="Confirm key: ", dont_match_promt="Keys don't match\n", attempts_limit=3):
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
        new_logins.write("Website,Mail,Password,Notes\n")
    encrypt_file("unenc", "saved_logins", key)
    os.remove("unenc")
    return open("saved_logins", "r")


def new_token():
    key = getpass("Please enter your new key: ")
    key_conf = key
    
    while True:
        if len(key) < 8:
            print("Its recommended to use a password with atleast 8 characters")
            key_conf = getpass("Enter a new key or type the last key again to use it: ")
            if key == key_conf:
                break
            else:
                key = key_conf
                key_conf = ""
                
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
        token.write(hash256(key))
        token.close()
        token = open("token", "r")
        logins = create_logins_file(key)

    elif not os.path.exists("token"):
        option = input("token file is missing, would you like to format all data? Y/n: ")
        if option.lower() == "y":
            key = new_token()
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
            key_c = getpass("Confirm your key: ")
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
    chars = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNPQRSTUVWXYZ!@#$%^&*()/-_.:?+"
    special_chars = "!@#$%^&*()/-_.:?+"
    nums = "01234567890"
    caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    x = 0
    y = 0
    z = 0
    while x == 0 or y == 0 or z == 0:  # Makes sure at least one number and one special character is present
        x = 0
        y = 0
        z = 0
        ran_pass = "".join(sample(chars, length))
        for char in ran_pass:
            if char in special_chars:
                x += 1
            elif char in nums:
                y += 1
            elif char in caps:
                z += 1

    return ran_pass


def add_new_record(logins_f, key, columns):
    values = []
    for field in columns:
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
        if "," in value:
            pos = values.index(value)
            print("\n',' may not be entered into any field")
            value = input("New value for %s: " % (columns[pos]))
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


def edit_record(logins_f, key, columns):
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
        pos = columns.index(field_to_change.lower())
        found = True
    except ValueError:
        print("Column not found")
        
        try:
            pos = int(input("Enter the position of the column (1-%s): " % length(columns))) - 1
            found = True
        except IndexError:
            print("Column not found")
            found = False
        
    if found:
    
        if columns[pos].lower != "password":
            new_value = input("New value for '%s': " % columns[pos])
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
            new_value = input("New value for '%s': " % columns[pos])
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
            exit("Too many attempts")
    new_key = new_token()

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
    pass_confirm = getpass("Are you sure you want to continue? All data will be lost. Type your key to continue: ")
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
    home_path = os.path.expanduser("~")
    if os_sys in ["windows"]:
        path = home_path + "\\Documents\\PasswordManager_Backup\\"

    else:
        path = home_path + "/Documents/PasswordManager_Backup/"

    enc = input("Would you like to save the backup (E)ncrypted or (D)ecrypted: ")
    datetime_ = (str(datetime.now()).replace(" ", "_").replace(":", "-"))[:-7]
    backup_name = logins_f.name + datetime_

    try:
        os.makedirs(path)
    except FileExistsError:
        pass

    if enc.lower() == "e":
        print("Copying token file to " + path)
        shutil.copy(logins_f.name, path + backup_name)
        shutil.copy(token_f.name, path + token_file.name + datetime_)
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
        x = input("Press enter to continue")
    else:
        print("Unexpected error, please try again")

    sleep(2)


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
            
        else: # if os_sys in ["macosx darwin linux"]:
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
            
            else: # if os_sys in ["macosx darwin linux"]:
                path = input("Could not find file, type the location of the file /Path/To/Folder/")
                
            if os.path.exists(saved_logins_path):
                print("saved_logins file found")
                saved_logins_path = path + saved_l_name
                saved_logins_file = open(saved_logins_path, "r")
            
        try:
            for line in saved_logins_file:
                decrypted = True
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
                token.write(hash256(key))
            print("Import succesful")
                
        elif not decrypted:
            print("File detected as encrypted")
            token_path = path + "token" + saved_l_name[-19:]
            
            if not os.path.exists(token_path):
                token_name = input("Please type the name of the token file: ")
                token_path = path + token_name
                if not os.path.exists(token_path):
                    
                    if os_sys in ["windows"]:
                        path = input("Could not find file, type the location of the file C:\\Path\\To\\Folder\\")
            
                    else: # if os_sys in ["macosx darwin linux"]:
                        path = input("Could not find file, type the location of the file /Path/To/Folder/")
                        
                    if not os.path.exists(path + token_name):
                        exit("Could not find file")
                
                
            backup_token = open(token_path, "r").read()
            print("Token file found")
            abc = 0
            backup_key = getpass("Please input the key used in this backup: ")
            while backup_token != hash256(backup_key):
                abc += 1
                backup_key = getpass("Keys dont match, plese try again:")
                print(backup_token, hash256(backup_key))
                if abc == 3:
                    print("If you have forgotten the key type leave to exit the backup import, or type another key to try again.")
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
                print("Import succesful")
        
    x = input("Press enter to continue")


def add_new_column(saved_logins_f, key):
    column_name = input("Name for the new column: ")
    while (not column_name or column_name.isspace()):
        print("Column name cannot be left blank")
        print("To exit type _exit_")
        column_name = input("Name for the new column: ")
        if column_name == "_exit_":
            break
    else:
        decrypt_file(saved_logins_f.name, "unenc", key)
        unenc_f = open("unenc", "r")
        with open("temp", "w") as file:
            x = 0

            for row in unenc_f:
                
                # if "\n" in row:
                   # n = ""
                # else:
                n = "\n"
                
                
                if x == 0:
                    x += 1
                    new_row = (row[:-1] + ",%s" % column_name + n)
                    file.write(new_row)
                else:
                    new_row = row[:-1] + "," + n
                    file.write(new_row)

                file.flush()

        encrypt_file("temp", saved_logins_f.name, key)
        os.remove("temp")
        os.remove("unenc")
    
    
def delete_column(saved_logins_f, key):
    decrypt_file(saved_logins_f.name, "temp", key)
    with open("temp", "r") as file:
        for row in file:
            header = row[:-1]
            break
    
    header_list = header.split(",")
    
    for item in header_list:
        print(item, end = " ")
    else:
        print("")
        
    column_name = input("Name of the column you want to remove: ")
    
    index2remove = header_list.index(column_name)
        
    with open("temp","r") as source:
        rdr = csv.reader( source )
        with open("result","w") as result:
            wtr = csv.writer( result )
            for r in rdr:
                write = r[:(index2remove)] + r[(index2remove + 1):]
                wtr.writerow( write )
            
    encrypt_file("result", "saved_logins", key)
    os.remove("result")
    os.remove("temp")


def get_columns(saved_logins_f, key):
    decrypt_file(saved_logins_f.name, "temp", key)
    with open("temp", "r") as file:
        for row in file:
            header = row[:-1].split(",")
            break
    return [i.lower() for i in header]
    
    

version = "v0.1.0" 

if __name__ == "__main__":

    os_sys = system().lower()
    if os_sys == "windows":
        def clear_console(): os.system('cls')  # Windows
    elif os_sys in "darwin macosx linux":
        def clear_console(): os.system('clear')  # Linux and Mac
    else:
        clear_command = input("Could not detect os, please type your console command to clear the console or type skip ")
        if clear_command.lower() != "skip":
            def clear_console(): os.system(clear_command)
        else:
            print("App may not function propetly without the command.")
            sleep(2)

    clear_console()
    
    warning = check_h()
    if warning:
        warning_msg()
    
    token_file, logins_file, key_ = sc_files()
    if key_ == "":  # Checks that no key was given in the proceses above in result of missing files
        key_ = check_key(token_file)
    
    columns = get_columns(logins_file, key_)
    accepted_options = "1234567890abx"

    while True:  # Main loop
        clear_console()
        
        if warning:
            warning_msg()
        
        print("1) Read saved logins      2) Add new record\n3) Edit existing record   4) Delete record")
        print("5) Change key             6) Delete all files\n7) Move record            8) Create backup")
        print("9) Import backup          A) Add new column\nB) Delete column")
        print("0) Exit")
        option = input("-> ", )

        if option.isdigit():
            option_is_int = True
            option = int(option)
        else:
            option_is_int = False

        clear_console()
        
        if warning:
            warning_msg()

        if str(option).lower() in accepted_options:
            if option_is_int:
                if option == 1:  # Run option
                    readall_passwords(logins_file.name, key_)
                    x = input("\nPress enter to continue")
                elif option == 2:
                    add_new_record(logins_file, key_, columns) # New addition of columns, edit code
                elif option == 3:
                    edit_record(logins_file, key_, columns) # New addition of columns, edit code
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
                    delete_column(logins_file, key_)
                    columns = get_columns(logins_file, key_)
                elif option.lower() == "x":
                    decrypt_file("saved_logins", "debuging", key_)
        else:
            print("'%s' isn't a supported option" % option)
            x = input("\nPress Enter to continue")

    key_ = ""
    clear_console()