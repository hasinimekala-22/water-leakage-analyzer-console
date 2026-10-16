import getpass
from dashboard import show_dashboard

password = getpass.getpass("Enter Oracle password: ")
show_dashboard(password)