import tkinter as tk
from tkinter import ttk, messagebox
import re
import os
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import Data  # Data.py에서 데이터 불러오기
import Main_UI  # Main_UI 모듈 임포트
import threading
import arduino_google_sheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import serial.tools.list_ports
import time

class PlanManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Production Plan Management System")
        self.geometry("1100x700")
        self.configure(bg="#f0f0f0")
        
        # Data.py에서 데이터 불러오기
        self.part_list = Data.get_part_list()
        self.plans = Data.get_plans()
        
        # Input Section
        input_frame = tk.LabelFrame(self, text="Plan Information Input", bg="#f0f0f0", padx=10, pady=10)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        left_frame = tk.Frame(input_frame, bg="#f0f0f0")
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Date entry + plus/minus buttons
        tk.Label(left_frame, text="Date (MM/DD)", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = tk.Entry(left_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=(5,0), pady=5, sticky="w")
        today_str = datetime.now().strftime("%m/%d")
        self.date_entry.insert(0, today_str)
        btn_frame = tk.Frame(left_frame, bg="#f0f0f0")
        btn_frame.grid(row=0, column=2, padx=(2,0), pady=5, sticky="w")
        tk.Button(btn_frame, text="+", width=2, command=self.increment_date).pack(side="left")
        tk.Button(btn_frame, text="-", width=2, command=self.decrement_date).pack(side="left")
        
        tk.Label(left_frame, text="Part Number (Last 4 digits)", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.part_entry = tk.Entry(left_frame, width=30)
        self.part_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew", columnspan=2)
        self.part_entry.bind("<FocusOut>", self.auto_complete_part)
        self.part_entry.bind("<Return>", lambda e: self.plan_count_entry.focus())
        
        tk.Label(left_frame, text="Today's Plan Count", bg="#f0f0f0").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.plan_count_entry = tk.Entry(left_frame, width=30)
        self.plan_count_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew", columnspan=2)
        self.plan_count_entry.bind("<Return>", lambda e: self.completed_count_entry.focus())
        
        tk.Label(left_frame, text="Completed Count", bg="#f0f0f0").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.completed_count_entry = tk.Entry(left_frame, width=30)
        self.completed_count_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew", columnspan=2)
        self.completed_count_entry.insert(0, "0")
        self.completed_count_entry.bind("<Return>", lambda e: self.add_plan())
        
        # Image display section
        self.image_frame = tk.Frame(input_frame, bg="#f0f0f0")
        self.image_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        self.image_label = tk.Label(self.image_frame, bg="#f0f0f0", text="Image will be displayed here")
        self.image_label.pack()
        
        # Button Section with Checkbox
        button_frame = tk.Frame(self, bg="#f0f0f0")
        button_frame.pack(fill="x", padx=20, pady=5)
        tk.Button(button_frame, text="Add Plan", command=self.add_plan, 
                 bg="#4CAF50", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(button_frame, text="Edit Plan", command=self.edit_plan, 
                 bg="#2196F3", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(button_frame, text="Delete Plan", command=self.delete_plan, 
                 bg="#f44336", fg="white", width=12).pack(side="left", padx=5)
        clear_all_btn = tk.Button(button_frame, text="Clear All", command=self.clear_all_plans, 
                          bg="#FF0000", fg="white", width=12)
        clear_all_btn.pack(side="left", padx=5)
        
        # Change Plan 체크박스 추가
        self.change_plan_mode = tk.BooleanVar()
        change_plan_check = tk.Checkbutton(
            button_frame, text="Change Plan", 
            variable=self.change_plan_mode,
            bg="#f0f0f0",
            command=self.toggle_change_mode
        )
        change_plan_check.pack(side="left", padx=10)
        
        # START RUN 버튼 추가 (오른쪽 끝에 위치)
        tk.Button(button_frame, text="START RUN", command=self.start_run, 
                 bg="#FFA500", fg="white", width=12).pack(side="right", padx=5)
        
        # Plan List Section
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview with custom style for red text
        self.tree = ttk.Treeview(tree_frame, columns=("No", "Date", "Part", "Plan", "Completed"), 
                                show="headings", yscrollcommand=scrollbar.set)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure("Treeview", rowheight=25)
        self.style.map("Treeview", background=[("selected", "#347083")])
        self.style.configure("Red.Treeview", foreground="red", font=("TkDefaultFont", 10, "bold"))
        
        # Configure row colors
        self.tree.tag_configure('evenrow', background='#f2f2f2')
        
        columns = [
            ("No", "No."), 
            ("Date", "Date (MM/DD)"), 
            ("Part", "Part Number"),
            ("Plan", "Plan Count"), 
            ("Completed", "Completed Count")
        ]
        for col_id, col_name in columns:
            self.tree.heading(col_id, text=col_name)
            self.tree.column(col_id, width=100 if col_id=="No" else 150, anchor="center")
        self.tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Double-click event for editing
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Drag & drop events
        self.tree.bind("<ButtonPress-1>", self.on_treeview_press)
        self.tree.bind("<B1-Motion>", self.on_treeview_motion)
        self.tree.bind("<ButtonRelease-1>", self.on_treeview_release)
        self._dragging_item = None
        self._drag_start_y = 0
        self._drag_line = None
        self._drag_after_id = None
        
        # 초기 트리뷰 갱신
        self.refresh_tree()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.main_ui = None  # Main_UI 참조용

    def clear_all_plans(self):
        if messagebox.askyesno("Confirm", "모든 생산 계획 데이터를 삭제하시겠습니까?"):
            Data.update_plans([])  # 모든 계획 데이터 삭제
            self.plans = Data.get_plans()
            self.refresh_tree()
            messagebox.showinfo("Success", "모든 생산 계획 데이터가 삭제되었습니다.")

    def on_closing(self):
        if self.main_ui:
            self.main_ui.destroy()
        self.destroy()

    def start_run(self):
        """Google Sheet 초기 동기화 + Main_UI 실행"""
        # Google Sheet 초기 동기화 수행
        self.initial_google_sheet_sync()
        
        # # 아두이노 초기화 추가
        # self.sync_arduino_count()

        # 아두이노 데이터 처리 스레드 시작
        arduino_thread = threading.Thread(target=arduino_google_sheet.run_arduino_google_sheet, daemon=True)
        arduino_thread.start()
        
        # Main_UI 실행
        self.withdraw()
        self.main_ui = Main_UI.ProductionUI(self)
        self.main_ui.protocol("WM_DELETE_WINDOW", lambda: self.on_main_ui_close(self.main_ui))
        self.main_ui.mainloop()

    def initial_google_sheet_sync(self):
        """완료된 계획을 Google Sheet에 초기 동기화 (완료된 행 건너뛰기)"""
        # Google Sheets 인증
        cred_path = r"C:\Users\sales07-auto\Desktop\ATS\03.관리및개선\조립라인 카운팅\PYTHONFILE\credentials.json.json"
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
        client = gspread.authorize(creds)
        sheet = client.open("IR_COUNTER").sheet1
        
        def find_available_row(part_number, date_str):
            """100% 완료되지 않은 첫 번째 행 찾기"""
            j_column = sheet.col_values(10)
            row2_values = sheet.row_values(2)
            
            # 날짜 열 찾기
            target_col = None
            for idx, value in enumerate(row2_values, 1):
                if '/' in value:
                    try:
                        sheet_date_str = value.strip().replace('. ', '-').replace('.', '')
                        sheet_dt = datetime.datetime.strptime(sheet_date_str, "%Y-%m-%d")
                        sheet_mmdd = sheet_dt.strftime("%m/%d")
                    except:
                        sheet_mmdd = value.strip()
                    
                    if sheet_mmdd == date_str:
                        target_col = idx
                        break
                else:
                    if value.strip() == date_str:
                        target_col = idx
                        break
            
            if target_col is None:
                return None, None
            
            # Part Number가 일치하는 행들 중 100% 완료되지 않은 첫 번째 행 찾기
            for idx, value in enumerate(j_column, 1):
                if value.strip() == part_number:
                    percent_col = target_col + 2
                    try:
                        percent_value = sheet.cell(idx, percent_col).value
                        if not percent_value or '100.00%' not in str(percent_value):
                            return idx, target_col
                    except:
                        return idx, target_col
            
            return None, target_col
        
        # Data에서 completed_count가 1 이상인 플랜 조회
        plans = Data.get_plans()
        completed_plans = [p for p in plans if p['completed_count'] >= 1]
        
        for plan in completed_plans:
            part_number = plan['part']
            date_str = plan['date']
            completed_count = plan['completed_count']
            plan_count = plan['plan_count']
            percentage = (completed_count / plan_count * 100) if plan_count else 0
            
            # 사용 가능한 행 찾기
            target_row, target_col = find_available_row(part_number, date_str)
            
            if target_row is None or target_col is None:
                print(f"No available row found for {part_number} on {date_str}")
                continue
            
            # 데이터 업데이트
            sheet.update_cell(target_row, target_col + 1, completed_count)
            sheet.update_cell(target_row, target_col + 2, f"{percentage:.1f}%")
            
            print(f"Initial sync - Row {target_row}: {part_number} | {date_str} | "
                f"Count: {completed_count} | Percent: {percentage:.1f}%")

        """Main_UI 실행 및 플랜 데이터 출력"""
        # 플랜 데이터 출력
        print("\n" + "="*50)
        print("현재 등록된 생산 계획 (Plan 데이터):")
        print("No. | Date       | Part Number     | Plan | Completed")
        print("-"*50)
        
        plans = Data.get_plans()
        for i, plan in enumerate(plans, 1):
            print(f"{i:3} | {plan['date']:10} | {plan['part']:15} | {plan['plan_count']:4} | {plan['completed_count']:9}")
        
        if not plans:
            print("등록된 생산 계획이 없습니다.")
        
        print("="*50 + "\n")
        
        # Main_UI 실행
        self.withdraw()
        self.main_ui = Main_UI.ProductionUI(self)
        self.main_ui.protocol("WM_DELETE_WINDOW", 
                            lambda: self.on_main_ui_close(self.main_ui))
        self.main_ui.mainloop()

    def on_main_ui_close(self, main_ui):
        main_ui.destroy()
        self.deiconify()
        self.main_ui = None
        
    def toggle_change_mode(self):
        """Change Plan 모드 토글 시 상태 표시"""
        if self.change_plan_mode.get():
            messagebox.showinfo("Info", "Drag mode activated. Double-click disabled.")
        else:
            messagebox.showinfo("Info", "Edit mode activated. Double-click enabled.")
        
    def validate_date(self, date_str):
        pattern = r"^(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])$"
        return bool(re.match(pattern, date_str))
        
    def increment_date(self):
        date_str = self.date_entry.get().strip()
        try:
            date_obj = datetime.strptime(date_str, "%m/%d")
            new_date = date_obj + timedelta(days=1)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, new_date.strftime("%m/%d"))
        except Exception:
            messagebox.showwarning("Warning", "Invalid date format. Please use MM/DD.")
        
    def decrement_date(self):
        date_str = self.date_entry.get().strip()
        try:
            date_obj = datetime.strptime(date_str, "%m/%d")
            new_date = date_obj - timedelta(days=1)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, new_date.strftime("%m/%d"))
        except Exception:
            messagebox.showwarning("Warning", "Invalid date format. Please use MM/DD.")
        
    def auto_complete_part(self, event):
        part_input = self.part_entry.get().strip()
        self.display_image("")
        
        # 부품 목록 가져오기
        part_list_data = Data.get_part_list()
        
        # 데이터 형식에 따른 처리
        if not part_list_data:
            part_numbers = []
        elif isinstance(part_list_data[0], dict):  # 딕셔너리 리스트
            part_numbers = [p["part_number"] for p in part_list_data]
        else:  # 문자열 리스트
            part_numbers = part_list_data
        
        # 입력이 4자리 숫자인 경우 (마지막 4자리 검색)
        if len(part_input) == 4 and part_input.isdigit():
            # 대소문자 구분 없이 마지막 4자리 비교
            matches = [pn for pn in part_numbers if pn[-4:].lower() == part_input.lower()]
            
            if not matches:
                messagebox.showwarning("경고", "부품 번호를 찾을 수 없습니다")
                self.part_entry.delete(0, tk.END)
                return
            elif len(matches) > 1:
                messagebox.showwarning("경고", "여러 부품 번호가 일치합니다:\n" + "\n".join(matches))
                self.part_entry.delete(0, tk.END)
                return
                
            matched = matches[0]
            self.part_entry.delete(0, tk.END)
            self.part_entry.insert(0, matched)
            self.display_image(matched)
            
        # 입력이 전체 부품 번호인 경우
        elif len(part_input) == 11:
            # 대소문자 구분 없이 전체 비교
            matches = [pn for pn in part_numbers if pn.lower() == part_input.lower()]
            
            if matches:
                self.display_image(matches[0])
            else:
                self.display_image("")
                messagebox.showwarning("경고", "부품 번호를 찾을 수 없습니다")
        
        # 기타 경우
        else:
            self.display_image("")
        
    def display_image(self, part_number):
        for widget in self.image_frame.winfo_children():
            widget.destroy()
        if not part_number:
            self.image_label = tk.Label(self.image_frame, bg="#f0f0f0", text="Image will be displayed here")
            self.image_label.pack()
            return
        image_path = fr"C:\Users\sales07-auto\Desktop\ATS\03.관리및개선\조립라인 카운팅\PYTHONFILE\Image\{part_number}.png"
        if os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                max_size = (400, 400)
                img.thumbnail(max_size, Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.image_label = tk.Label(self.image_frame, image=photo, bg="#f0f0f0")
                self.image_label.image = photo
                self.image_label.pack()
                self.image_frame.config(width=img.width, height=img.height)
            except Exception as e:
                self.image_label = tk.Label(self.image_frame, bg="#f0f0f0", text=f"Image load error: {str(e)}")
                self.image_label.pack()
        else:
            self.image_label = tk.Label(self.image_frame, bg="#f0f0f0", text="Image not found")
            self.image_label.pack()
        
    def add_plan(self):
        data = self.get_input_data()
        if not data:
            return
        
        # Data.py에 계획 추가
        Data.add_plan(data)
        self.plans = Data.get_plans()  # 데이터 갱신
        self.refresh_tree()
        
        # 입력 필드 초기화
        self.part_entry.delete(0, tk.END)
        self.plan_count_entry.delete(0, tk.END)
        self.completed_count_entry.delete(0, tk.END)
        self.completed_count_entry.insert(0, "0")
        self.display_image("")
        self.part_entry.focus_set()
        messagebox.showinfo("Success", "생산 계획이 추가되었습니다.")
        
    def edit_plan(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "수정할 계획을 선택해주세요")
            return
            
        data = self.get_input_data()
        if not data:
            return
            
        # 선택한 계획 인덱스 찾기 (트리뷰 인덱스 사용)
        selected_item = selected[0]
        item_index = self.tree.index(selected_item)
        
        # Data.py에서 계획 업데이트
        new_plans = self.plans.copy()
        new_plans[item_index] = {
            "date": data["date"],
            "part": data["part"],
            "plan_count": data["plan_count"],
            "completed_count": data["completed_count"]
        }
        Data.update_plans(new_plans)
        self.plans = Data.get_plans()
        self.refresh_tree()
        messagebox.showinfo("Success", "생산 계획이 수정되었습니다.")

        self.part_entry.delete(0, tk.END)
        self.plan_count_entry.delete(0, tk.END)

    def delete_plan(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "삭제할 계획을 선택해주세요")
            return
            
        # 트리뷰 인덱스 기반 삭제
        indices_to_delete = []
        for item in selected:
            item_index = self.tree.index(item)
            indices_to_delete.append(item_index)
        
        # 인덱스 내림차순 정렬 (뒤에서부터 삭제)
        indices_to_delete.sort(reverse=True)
        
        # Data.py에서 계획 삭제
        new_plans = self.plans.copy()
        for idx in indices_to_delete:
            if 0 <= idx < len(new_plans):
                del new_plans[idx]
                
        Data.update_plans(new_plans)
        self.plans = Data.get_plans()
        self.refresh_tree()
        
    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        plans = Data.get_plans()
        for i, plan in enumerate(plans, 1):
            tag = 'evenrow' if i % 2 == 0 else ''
            
            part_text = plan["part"]
            last4 = part_text[-4:] if len(part_text) > 4 else part_text
            prefix = part_text[:-4] if len(part_text) > 4 else ""
            
            item_id = self.tree.insert(
                "", "end",
                values=(i, plan["date"], part_text, plan["plan_count"], plan["completed_count"]),
                tags=(tag,)
            )
            
            if len(part_text) > 4:
                self.tree.item(item_id, values=(
                    i, 
                    plan["date"], 
                    prefix + last4,
                    plan["plan_count"], 
                    plan["completed_count"]
                ))
                self.tree.item(item_id, tags=(tag, "Red.Treeview"))
        
    def get_input_data(self):
        date = self.date_entry.get().strip()
        part = self.part_entry.get().strip()
        plan_count = self.plan_count_entry.get().strip()
        completed_count = self.completed_count_entry.get().strip()
        if not completed_count:
            completed_count = "0"
        if not self.validate_date(date):
            messagebox.showwarning("Warning", "날짜 형식은 MM/DD로 입력해주세요 (예: 06/30)")
            return None
        if not all([date, part, plan_count]):
            messagebox.showwarning("Warning", "날짜, 부품 번호, 계획 수량은 필수 입력 항목입니다")
            return None
        try:
            plan_count = int(plan_count)
            completed_count = int(completed_count)
        except ValueError:
            messagebox.showwarning("Warning", "수량은 숫자로 입력해주세요")
            return None
        return {
            "date": date,
            "part": part,
            "plan_count": plan_count,
            "completed_count": completed_count
        }
        
    def clear_fields(self):
        self.part_entry.delete(0, tk.END)
        self.plan_count_entry.delete(0, tk.END)
        self.completed_count_entry.delete(0, tk.END)
        self.completed_count_entry.insert(0, "0")
        self.display_image("")
        
    def on_double_click(self, event):
        # Change Plan 모드가 활성화된 경우 편집 금지
        if self.change_plan_mode.get():
            return
            
        item = self.tree.selection()
        if not item:
            return
        values = self.tree.item(item[0], "values")
        self.clear_fields()
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, values[1])
        self.part_entry.insert(0, values[2])
        self.plan_count_entry.insert(0, values[3])
        self.completed_count_entry.insert(0, values[4])
        self.display_image(values[2])
        
    def on_treeview_press(self, event):
        # Change Plan 모드가 아닌 경우 드래그 비활성화
        if not self.change_plan_mode.get():
            return
            
        item = self.tree.identify_row(event.y)
        if item:
            self._dragging_item = item
            self._drag_start_y = event.y
            
            # 강조 효과
            self.tree.selection_set(item)
            
            # 드래그 라인 초기화
            if self._drag_line:
                self.tree.delete(self._drag_line)
            self._drag_line = self.tree.create_line(
                0, event.y, self.tree.winfo_width(), event.y,
                fill="blue", dash=(4, 2), width=2
            )
            
            # 더블클릭 방지 딜레이
            self._drag_after_id = self.after(300, lambda: None)
    
    def on_treeview_motion(self, event):
        # Change Plan 모드가 아니거나 드래그 아이템이 없는 경우 무시
        if not self.change_plan_mode.get() or self._dragging_item is None:
            return
            
        y = event.y
        
        # 라인 위치 업데이트
        if self._drag_line:
            self.tree.coords(self._drag_line, 0, y, self.tree.winfo_width(), y)
        
        # 행 이동
        target_item = self.tree.identify_row(y)
        if target_item and target_item != self._dragging_item:
            # 이동 전에 드래그 아이템 저장
            dragging_item = self._dragging_item
            
            # 아이템 이동
            self.tree.move(dragging_item, '', self.tree.index(target_item))
            
            # 이동 후 아이템 업데이트
            self._dragging_item = dragging_item
            self.tree.selection_set(dragging_item)
    
    def on_treeview_release(self, event):
        # Change Plan 모드가 아니거나 드래그 아이템이 없는 경우 무시
        if not self.change_plan_mode.get() or self._dragging_item is None:
            return
            
        # 드래그 라인 제거
        if self._drag_line:
            self.tree.delete(self._drag_line)
            self._drag_line = None
            
        # 새 순서 적용
        new_order = []
        for item in self.tree.get_children():
            vals = self.tree.item(item, "values")
            new_order.append({
                "date": vals[1],
                "part": vals[2],
                "plan_count": vals[3],
                "completed_count": vals[4]
            })
            
        # Data.py에 업데이트
        Data.update_plans(new_order)
        self.plans = Data.get_plans()
        
        self._dragging_item = None
        self._drag_start_y = 0
        
        # 더블클릭 방지 딜레이 취소
        if self._drag_after_id:
            self.after_cancel(self._drag_after_id)
            self._drag_after_id = None

    def refresh_plans(self):
        """데이터 새로고침 및 UI 업데이트"""
        self.plans = Data.get_plans()
        self.refresh_tree()
        print("Plan UI refreshed with latest data")
    
    def on_main_ui_close(self, main_ui):
        main_ui.destroy()
        self.deiconify()
        self.refresh_plans()  # 새로고침 추가
        self.main_ui = None

    def sync_arduino_count(self):
        """아두이노와 Data 동기화"""
        plans = Data.get_plans()
        current_plan = next((p for p in plans if p['completed_count'] < p['plan_count']), None)
        
        if current_plan:
            completed_count = current_plan['completed_count']
            try:
                # 아두이노에 명령 전송
                ser = serial.Serial('COM4', 9600, timeout=1)
                ser.write(f"SET:{completed_count}\n".encode())
                time.sleep(0.5)
                print(f"아두이노 초기값 설정: {completed_count}")
            except Exception as e:
                print(f"아두이노 초기화 오류: {e}")

if __name__ == "__main__":
    app = PlanManager()
    app.mainloop()