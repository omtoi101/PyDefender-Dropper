import subprocess
import os

def TriageCheck():
    if os.name != 'nt':
        return False

    try:
        creation_flags = subprocess.CREATE_NO_WINDOW
        result = subprocess.check_output(['wmic', 'diskdrive', 'get', 'model'], text=True, creationflags=creation_flags)
        if "DADY HARDDISK" in result or "QEMU HARDDISK" in result:
            return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Could not run the check, assume it's fine.
        return False

    return False
