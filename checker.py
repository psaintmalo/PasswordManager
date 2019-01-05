import hashlib

def warning_msg():
    print("WARNING: Code migh have been tampered")
    print("Download it again from www.github.com/psaintmalo/PasswordManager")
    print("Or continue at your own risk\n")

def check_h():

    BUF_SIZE = 65536  # read stuff in 64kb chunks
    
    md5 = hashlib.md5()

    with open("PassManager.py", 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)

        md5 = md5.hexdigest()

    if md5 != "3a03744cf1b989510700f5d2da86882b" and __name__ != "__main__":
        return True
    elif __name__ == "__main__":
        return md5

if __name__ == "__main__":
    md5 = check_h()
    print(md5)