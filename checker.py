import hashlib


def warning_msg():
    print("WARNING: Code migh have been tampered")
    print("Download it again from www.github.com/psaintmalo/PasswordManager")
    print("Or continue at your own risk\n")


def check_h():

    buf_size = 65536  # read stuff in 64kb chunks
    
    md5_ = hashlib.md5()

    with open("PassManager.py", 'rb') as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            md5_.update(data)

        md5_ = md5_.hexdigest()

    if md5_ != "b1bc1067953d736e3d27fefed766c506" and __name__ != "__main__":
        return True
    elif __name__ == "__main__":
        return md5_


if __name__ == "__main__":
    hash_ = check_h()
    print(hash_)
