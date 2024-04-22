import os
import sys
import ctypes
import platform #type: ignore
from facesdb import FacesDB

# ANSI escape code for red text
RED = '\033[31m'
# ANSI escape code to reset formatting
RESET = '\033[0m'

# Check if the script is run with higher privileges
if platform.system() == 'Windows':
    # Windows-specific check
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print(f"{RED}This script must be run as Administrator.{RESET}")
        sys.exit()
else:
    # Unix-specific check
    if os.geteuid() != 0:
        print(f"{RED}This script must be run as root or with sudo.{RESET}")
        sys.exit()

if len(sys.argv) < 2:
    print(f"{RED}Usage: python resetdb.py \"/path/to/your/database.db\"\nyou need to provide the path to the database file.{RESET}")
    sys.exit()

db = FacesDB(sys.argv[1])
db.reset_db(sys.argv[1])