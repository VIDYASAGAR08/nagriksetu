import ctypes
from ctypes import wintypes
import os

RmStartSession = ctypes.windll.rstrtmgr.RmStartSession
RmRegisterResources = ctypes.windll.rstrtmgr.RmRegisterResources
RmGetList = ctypes.windll.rstrtmgr.RmGetList
RmEndSession = ctypes.windll.rstrtmgr.RmEndSession

CCH_RM_MAX_APP_NAME = 255
CCH_RM_MAX_SVC_NAME = 63

class RM_UNIQUE_PROCESS(ctypes.Structure):
    _fields_ = [
        ("dwProcessId", wintypes.DWORD),
        ("ProcessStartTime", wintypes.FILETIME)
    ]

class RM_PROCESS_INFO(ctypes.Structure):
    _fields_ = [
        ("Process", RM_UNIQUE_PROCESS),
        ("strAppName", wintypes.WCHAR * (CCH_RM_MAX_APP_NAME + 1)),
        ("strServiceShortName", wintypes.WCHAR * (CCH_RM_MAX_SVC_NAME + 1)),
        ("ApplicationType", wintypes.DWORD),
        ("AppStatus", wintypes.DWORD),
        ("TSSessionId", wintypes.DWORD),
        ("bRestartable", wintypes.BOOL)
    ]

file_path = r"C:\Users\callm\nagriksetu\reports\NagrikSetu_Institution_Wise_Student_Course_Enrollment_Register.xlsx"

session_handle = wintypes.DWORD()
session_key = (wintypes.WCHAR * 256)()

res = RmStartSession(ctypes.byref(session_handle), 0, session_key)
if res == 0:
    path_arr = (wintypes.LPCWSTR * 1)(file_path)
    res = RmRegisterResources(session_handle, 1, path_arr, 0, None, 0, None)
    if res == 0:
        n_proc_info_needed = wintypes.UINT()
        n_proc_info = wintypes.UINT(10)
        proc_info = (RM_PROCESS_INFO * 10)()
        reboot_reasons = wintypes.DWORD()
        res = RmGetList(session_handle, ctypes.byref(n_proc_info_needed), ctypes.byref(n_proc_info), proc_info, ctypes.byref(reboot_reasons))
        if res == 0:
            print(f"Number of locking processes: {n_proc_info.value}")
            for i in range(n_proc_info.value):
                pi = proc_info[i]
                print(f"Locking PID: {pi.Process.dwProcessId}, App Name: {pi.strAppName}")
        else:
            print("RmGetList error:", res)
    RmEndSession(session_handle)
else:
    print("RmStartSession error:", res)
