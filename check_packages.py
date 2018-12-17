try:
    import pyAesCrypt
    print("pyAesCrypt package found")
except ModuleNotFoundError:
    print("pyAesCrypt package missing")
    print("To install please use pip install pyAesCrypt\n")

try:
    import pandas
    print("pandas package found")
except ModuleNotFoundError:
    print("pyAesCrypt package missing")
    print("To install it please use pip install pandas\n")
