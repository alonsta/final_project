import sys
import os
import win32serviceutil
import win32service
import win32event
import servicemanager

class FileSyncService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FileSyncService"
    _svc_display_name_ = "File Sync Service"
    _svc_description_ = "service that periodiclly tries to update files from a remote storage server and vice versa"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        # Main service logic here
        while True:
            # Implement file sync logic here, running continuously
            pass
    
    @staticmethod
    def install_service():
        try:
            win32serviceutil.InstallService(
                __file__,  # This will run this file as a service
                serviceName=FileSyncService._svc_name_,
                displayName=FileSyncService._svc_display_name_,
                description=FileSyncService._svc_description_,
                startType=win32service.SERVICE_AUTO_START
            )
            print("Service installed successfully.")
        except Exception as e:
            print(f"Failed to install service: {e}")

    @staticmethod
    def start_service():
        try:
            win32serviceutil.StartService(FileSyncService._svc_name_)
            print("Service started successfully.")
        except Exception as e:
            print(f"Failed to start service: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Run as service
        win32serviceutil.HandleCommandLine(FileSyncService)
    elif sys.argv[1] == 'install':
        FileSyncService.install_service()
    elif sys.argv[1] == 'start':
        FileSyncService.start_service()
