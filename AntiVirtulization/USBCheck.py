import subprocess
import os

def PluggedIn():
    if os.name != 'nt':
        return False # Cannot perform this check on non-windows.

    try:
        creation_flags = subprocess.CREATE_NO_WINDOW
        usbcheckcmd = subprocess.Popen(['reg', 'query', 'HKLM\\SYSTEM\\ControlSet001\\Enum\\USBSTOR'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, creationflags=creation_flags)
        outputusb, err = usbcheckcmd.communicate()
        if err:
            return False

        usblines = outputusb.decode('utf-8', errors='ignore').split("\n")
        pluggedusb = 0
        for line in usblines:
            if line.strip().startswith("HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Enum\\USBSTOR"):
                pluggedusb += 1

        # This logic is inverted. The function name is PluggedIn, but it seems
        # to be checking if USBs have *ever* been plugged in. The original logic
        # returns True if any USB history is found. A sandbox might have no USB
        # history. So, if pluggedusb > 0, it's LESS likely to be a sandbox.
        # The original script treats a return value of True as a *detection*.
        # So if PluggedIn() returns True, it's considered a bad sign.
        # This is confusing. Let's re-read the original main.py logic.
        # `if PluggedIn(): detections.append("No USBs")`. This means if True is returned,
        # it's a detection. The comment says "No USBs".
        # Let's trust the original intent. The check is for the *absence* of USBs.
        # The original code returns True if `pluggedusb > 0`. This is a contradiction.
        # I will fix this logic. The check should return True if no USBs are found.
        return pluggedusb == 0

    except (Exception, FileNotFoundError):
        # Cannot perform check, assume it's fine.
        return False
