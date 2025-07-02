import serial
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from serial.tools import list_ports
import time
import Data

def run_arduino_google_sheet():
    # Credentials path
    CRED_PATH = r"C:\Users\sales07-auto\Desktop\ATS\03.관리및개선\조립라인 카운팅\PYTHONFILE\credentials.json.json"
    
    # Google Sheets setup
    SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CRED_PATH, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open("IR_COUNTER").sheet1

    # Serial port setup
    print("Available ports:")
    for port in list_ports.comports():
        print(port.device)
    
    try:
        ser = serial.Serial('COM4', 9600, timeout=1)
        print(f"Connected to {ser.port}")
    except Exception as e:
        print(f"Serial error: {e}")
        return

    # Helper functions
    def sync_arduino():
        """Sync Arduino with Data"""
        plans = Data.get_plans()
        for plan in plans:
            if plan['completed_count'] < plan['plan_count']:
                ser.write(f"SET:{plan['completed_count']}\n".encode())
                print(f"Arduino synced: {plan['completed_count']}")
                return True
        print("No active plan found")
        ser.write(b'RESET\n')
        return False

    def find_date_col(date_values, target_date):
        """Find date column index"""
        for idx, val in enumerate(date_values, 1):
            if '/' in val:
                try:
                    # Handle different date formats
                    clean_val = val.strip().replace('. ', '-').replace('.', '')
                    dt = datetime.datetime.strptime(clean_val, "%Y-%m-%d")
                    if dt.strftime("%m/%d") == target_date:
                        return idx
                except:
                    if val.strip() == target_date:
                        return idx
        return None

    def find_available_row(part_col, part_num, date_col, date_str):
        """Find first non-100% row"""
        for row_idx, part_val in enumerate(part_col, 1):
            if part_val.strip() == part_num:
                percent_val = sheet.cell(row_idx, date_col + 2).value
                if not percent_val or '100.00%' not in percent_val:
                    return row_idx
        return None

    # Initial setup
    time.sleep(2)
    sync_arduino()

    # Pre-fetch static sheet data
    part_column = sheet.col_values(10)  # J column
    date_row = sheet.row_values(2)      # Row 2

    while True:
        try:
            if ser.in_waiting:
                data = ser.readline().decode().strip()
                if data.startswith("COUNT:"):
                    count = int(data.split(":")[1])
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] Count: {count}")
                    
                    # Get current plan
                    plans = Data.get_plans()
                    active_plan = next((p for p in plans if p['completed_count'] < p['plan_count']), None)
                    
                    if not active_plan:
                        print("No active plan. Resetting Arduino.")
                        ser.write(b'RESET\n')
                        continue
                    
                    # Update Data
                    active_plan['completed_count'] = count
                    Data.update_plans(plans)
                    print(f"Updated: {active_plan['part']} | {active_plan['date']} | {count}/{active_plan['plan_count']}")
                    
                    # Find sheet position
                    date_col = find_date_col(date_row, active_plan['date'])
                    if not date_col:
                        print(f"Date not found: {active_plan['date']}")
                        continue
                    
                    target_row = find_available_row(part_column, active_plan['part'], date_col, active_plan['date'])
                    if not target_row:
                        print(f"No available row for {active_plan['part']}")
                        ser.write(b'RESET\n')
                        time.sleep(0.5)
                        sync_arduino()
                        continue
                    
                    # Update Google Sheet
                    sheet.update_cell(target_row, date_col + 1, count)
                    percent = (count / active_plan['plan_count'] * 100) if active_plan['plan_count'] else 0
                    sheet.update_cell(target_row, date_col + 2, f"{percent:.1f}%")
                    print(f"Sheet updated: Row {target_row}, Count: {count}, Percent: {percent:.1f}%")
                    
                    # Reset if 100%
                    if percent >= 100:
                        ser.write(b'RESET\n')
                        print("Plan 100%! Reset Arduino")
                        time.sleep(0.5)
                        sync_arduino()
            
            time.sleep(0.1)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

# import serial
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# import datetime
# from serial.tools import list_ports
# import time
# import Data

# def run_arduino_google_sheet():
#     # Credentials path
#     CRED_PATH = r"C:\Users\sales07-auto\Desktop\ATS\03.관리및개선\조립라인 카운팅\PYTHONFILE\credentials.json.json"
    
#     # Google Sheets setup
#     SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#     creds = ServiceAccountCredentials.from_json_keyfile_name(CRED_PATH, SCOPE)
#     client = gspread.authorize(creds)
#     sheet = client.open("IR_COUNTER").sheet1

#     # Serial port setup
#     print("Available ports:")
#     for port in list_ports.comports():
#         print(port.device)
    
#     try:
#         ser = serial.Serial('COM4', 9600, timeout=1)
#         print(f"Connected to {ser.port}")
#     except Exception as e:
#         print(f"Serial error: {e}")
#         return

#     # Helper functions
#     def sync_arduino():
#         """Sync Arduino with Data"""
#         plans = Data.get_plans()
#         for plan in plans:
#             if plan['completed_count'] < plan['plan_count']:
#                 ser.write(f"SET:{plan['completed_count']}\n".encode())
#                 print(f"Arduino synced: {plan['completed_count']}")
#                 return True
#         print("No active plan found")
#         ser.write(b'RESET\n')
#         return False

#     def find_date_col(date_values, target_date):
#         """Find date column index"""
#         for idx, val in enumerate(date_values, 1):
#             if '/' in val:
#                 try:
#                     clean_val = val.strip().replace('. ', '-').replace('.', '')
#                     dt = datetime.datetime.strptime(clean_val, "%Y-%m-%d")
#                     if dt.strftime("%m/%d") == target_date:
#                         return idx
#                 except:
#                     if val.strip() == target_date:
#                         return idx
#         return None

#     def find_available_row(part_col, part_num, date_col, date_str):
#         """Find first non-100% row"""
#         for row_idx, part_val in enumerate(part_col, 1):
#             if part_val.strip() == part_num:
#                 percent_val = sheet.cell(row_idx, date_col + 2).value
#                 if not percent_val or '100.00%' not in percent_val:
#                     return row_idx
#         return None

#     # Initial setup
#     time.sleep(2)
#     sync_arduino()

#     # Pre-fetch static sheet data
#     part_column = sheet.col_values(10)  # J column
#     date_row = sheet.row_values(2)      # Row 2

#     while True:
#         try:
#             if ser.in_waiting:
#                 data = ser.readline().decode().strip()
#                 if data.startswith("COUNT:"):
#                     count = int(data.split(":")[1])
#                     timestamp = datetime.datetime.now().strftime("%H:%M:%S")
#                     print(f"[{timestamp}] Count: {count}")
                    
#                     # Get current plan
#                     plans = Data.get_plans()
#                     active_plan = next((p for p in plans if p['completed_count'] < p['plan_count']), None)
                    
#                     if not active_plan:
#                         print("No active plan. Resetting Arduino.")
#                         ser.write(b'RESET\n')
#                         continue
                    
#                     # Update Data
#                     active_plan['completed_count'] = count
#                     Data.update_plans(plans)
#                     print(f"Updated: {active_plan['part']} | {active_plan['date']} | {count}/{active_plan['plan_count']}")
                    
#                     # Find sheet position
#                     date_col = find_date_col(date_row, active_plan['date'])
#                     if not date_col:
#                         print(f"Date not found: {active_plan['date']}")
#                         continue
                    
#                     target_row = find_available_row(part_column, active_plan['part'], date_col, active_plan['date'])
#                     if not target_row:
#                         print(f"No available row for {active_plan['part']}")
#                         ser.write(b'RESET\n')
#                         time.sleep(0.5)
#                         sync_arduino()
#                         continue
                    
#                     # Get current cell value and increment
#                     current_value = sheet.cell(target_row, date_col + 1).value
#                     try:
#                         new_value = int(current_value) + 1 if current_value else 1
#                     except ValueError:
#                         new_value = 1
                    
#                     # Update Google Sheet with incremented value
#                     sheet.update_cell(target_row, date_col + 1, new_value)
                    
#                     # Calculate percentage
#                     percent = (new_value / active_plan['plan_count'] * 100) if active_plan['plan_count'] else 0
#                     sheet.update_cell(target_row, date_col + 2, f"{percent:.1f}%")
                    
#                     print(f"Sheet updated: Row {target_row}, New Value: {new_value}, Percent: {percent:.1f}%")
                    
#                     # Reset if 100%
#                     if percent >= 100:
#                         ser.write(b'RESET\n')
#                         print("Plan 100%! Reset Arduino")
#                         time.sleep(0.5)
#                         sync_arduino()
            
#             time.sleep(0.1)
#         except Exception as e:
#             print(f"Error: {e}")
#             time.sleep(5)
