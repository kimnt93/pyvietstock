import os

from pyvietstock.account import login

print(login(os.environ['VIETSTOCK_LOGIN_EMAIL'], os.environ['VIETSTOCK_LOGIN_PASSWORD']))
