print("\n")
x = 0

try:
    import pandas
    print("pandas package found\n")
    x += 1
except ModuleNotFoundError:
    print("pandas package missing")
    print("To install please use pip3 install pandas\n")


try:
    import pyAesCrypt
    print("pyAesCrypt package found\n")
    x += 1
except ModuleNotFoundError:
    print("pyAesCrypt package missing")
    print("To install please use pip3 install pyAesCrypt\n")


try:
    pass
    # import urwid
    # print("urwid package found\n")
    # x += 1
except ModuleNotFoundError:
    pass
    # print("urwid package missing")
    # print("To install please use pip3 install urwid\n")
    # x += 1

    
if x != 2:
    print("Some packages are missing, without them the app may not work.\n")
else:
    print("All packages present.\n")