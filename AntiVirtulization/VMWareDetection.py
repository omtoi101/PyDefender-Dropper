import subprocess
import os

def GraphicsCardCheck():
    if os.name != 'nt':
        return False

    try:
        creation_flags = subprocess.CREATE_NO_WINDOW
        cmd = subprocess.Popen(['wmic', 'path', 'win32_VideoController', 'get', 'name'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, creationflags=creation_flags)
        gpu_output, err = cmd.communicate()

        if err:
            return False

        if b"vmware" in gpu_output.lower():
            return True
        else:
            return False

    except (Exception, FileNotFoundError):
        return False
