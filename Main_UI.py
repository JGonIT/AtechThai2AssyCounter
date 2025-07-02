import tkinter as tk
from tkinter import ttk, font
from datetime import datetime
from PIL import Image, ImageTk
import os
from datetime import datetime, timedelta
import Data  # Data 모듈 임포트
import Plan_UI

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

# 부품 정보 조회 함수
def get_part_info(part_number):
    """부품 정보 조회 함수 (dict 구조 대응)"""
    part_list = Data.get_part_list()
    
    # part_list가 문자열 리스트인 경우 dict로 변환
    if part_list and isinstance(part_list[0], str):
        # 문자열 리스트를 dict 형태로 변환
        formatted_list = [
            {
                "model": "SJ",
                "part_name": "F/GRILLE",
                "part_number": pn
            } for pn in part_list
        ]
        # 변환된 리스트를 Data에 저장 (일시적)
        data = Data.load_data()
        data["part_list"] = formatted_list
        Data.save_data(data)
        part_list = formatted_list
    
    # 부품 정보 검색
    for part in part_list:
        if isinstance(part, dict) and part.get("part_number") == part_number:
            return part
    
    # 없을 경우 기본값 반환
    return {"model": "Unknown", "part_name": "Unknown", "part_number": part_number}

# 현재/다음 작업 조회 함수
def get_current_next_plans():
    plans = Data.get_plans()
    current_plan = None
    next_plan = None
    
    for plan in plans:
        if plan["completed_count"] < plan["plan_count"]:
            if current_plan is None:
                current_plan = plan
            elif next_plan is None:
                next_plan = plan
                break
    
    return current_plan, next_plan

# 이미지 로드 함수
def load_part_image(part_number, label_widget, max_size=(200, 200)):
    image_path = fr"C:\Users\sales07-auto\Desktop\ATS\03.관리및개선\조립라인 카운팅\PYTHONFILE\Image\{part_number}.png"
    
    # 기존 이미지 정리
    if hasattr(label_widget, 'image'):
        label_widget.image = None
    
    if os.path.exists(image_path):
        try:
            img = Image.open(image_path)
            img.thumbnail(max_size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label_widget.config(image=photo)
            label_widget.image = photo  # 참조 유지
            label_widget.config(text="")  # 텍스트 제거
        except Exception as e:
            label_widget.config(image=None, text=f"Image Error: {str(e)}")
    else:
        label_widget.config(image=None, text="Image Not Found")

# 메인 UI 클래스
class ProductionUI(tk.Toplevel):
    def go_back(self):
        if self.master:
            # Plan_UI_Copy 새로고침 실행
            if hasattr(self.master, 'refresh_plans'):
                self.master.refresh_plans()
            self.master.deiconify()
        self.destroy()

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.title("A-Tech Input Line A")
        self.configure(bg="black")
        # self.minsize(1600, 1100)
        # 화면 크기 가져오기
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Plan&Progress 초기화 코드
        self.today_date = datetime.now().date()
        self.tomorrow_date = self.today_date + timedelta(days=1)
        # self.setup_progress_section()
        
        # 창 크기를 화면 크기로 설정
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 동적 폰트 객체 생성
        self.fonts = {
            "header": font.Font(family="Arial", size=26, weight="bold"),
            "title": font.Font(family="Arial", size=32, weight="bold"),
            "section": font.Font(family="Arial", size=13),
            "section_bold": font.Font(family="Arial", size=13, weight="bold")
        }
        
        # 그리드 구성
        self.setup_grid()
        
        # 헤더 생성
        self.setup_header()
        
        # 섹션 생성
        self.setup_current_section()
        self.setup_next_section()
        self.setup_progress_section()
        
        # 구분선 추가
        self.setup_separators()
        
        # 초기 데이터 로드
        self.update_data()
        
        # 주기적 업데이트 설정
        self.after(1000, self.periodic_update)

    def on_closing(self):
        if self.master:
            self.master.deiconify()  # 부모 창 복원
        self.destroy()
    
    def go_back(self):
        if self.master:
            self.master.deiconify()  # 부모 창 복원
        self.destroy()
        Plan_UI.PlanManager.refresh_plans()

    def setup_grid(self):
        # 행 구성
        for i in range(7):
            self.grid_rowconfigure(i, weight=1)
        
        # 열 구성
        self.grid_columnconfigure(0, weight=1, uniform="content")
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1, uniform="content")
        self.grid_columnconfigure(3, weight=0)
        self.grid_columnconfigure(4, weight=1, uniform="content")
    
    def setup_header(self):
        # 헤더 프레임
        header_frame = tk.Frame(self, bg="black")
        header_frame.grid(row=0, column=0, columnspan=5, sticky="ew", pady=8)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=10)
        header_frame.grid_columnconfigure(2, weight=1)
        header_frame.grid_columnconfigure(3, weight=0)  # 뒤로가기 버튼용 컬럼 추가

        # go_back_btn = tk.Button(
        #     header_frame, 
        #     text="← Back", 
        #     command=self.go_back,
        #     bg="#555555",
        #     fg="white",
        #     font=font.Font(family="Arial", size=12)
        # )
        # go_back_btn.grid(row=0, column=0, sticky="w", padx=10)

        # A-Tech 라벨 (중앙으로 조정)
        label_atech = tk.Label(header_frame, text="A-Tech", font=self.fonts["header"], 
                              fg="white", bg="black")
        label_atech.grid(row=0, column=0, sticky="w", padx=10)

        # 타이틀 (중앙)
        label_title = tk.Label(header_frame, text="Input Line A", 
                              font=font.Font(family="Arial", size=40, weight="bold"), 
                              fg="white", bg="black")
        label_title.grid(row=0, column=1, sticky="ew")

        # 시간 표시 (오른쪽)
        self.label_time = tk.Label(header_frame, text=get_time(), 
                                 font=font.Font(family="Arial", size=26, weight="bold"), 
                                 fg="white", bg="black")
        self.label_time.grid(row=0, column=2, sticky="e", padx=10)

    
    def setup_current_section(self):
        # CURRENT PART 타이틀
        self.current_title = tk.Label(self, text="NOW", font=self.fonts["title"], 
                                    fg="black", bg="#ede6d6")
        self.current_title.grid(row=1, column=0, columnspan=5, sticky="ew", padx=8)
        
        # CURRENT PART 내용
        self.current_left = tk.Label(self, text="MODEL : \nPART NAME : \nPART NO. : ", 
                                   font=self.fonts["section"], fg="black", bg="#ede6d6", 
                                   anchor="w", justify="left")
        self.current_left.grid(row=2, column=0, sticky="nsew", padx=(8,0), pady=0)
        
        self.current_center = tk.Label(self, text="", font=self.fonts["section"], 
                                     fg="black", bg="#ede6d6", anchor="center")
        self.current_center.grid(row=2, column=2, sticky="nsew", padx=0, pady=0)
        
        self.current_right = tk.Label(self, text="PLAN : \n\nOK : ", 
                                    font=self.fonts["section"], fg="black", bg="#ede6d6", 
                                    anchor="w", justify="left")
        self.current_right.grid(row=2, column=4, sticky="nsew", padx=(0,8), pady=0)
    
    def setup_next_section(self):
        # NEXT PART 타이틀
        self.next_title = tk.Label(self, text="NEXT", font=self.fonts["title"], 
                                 fg="black", bg="#d7e8f4")
        self.next_title.grid(row=3, column=0, columnspan=5, sticky="ew", padx=8)
        
        # NEXT PART 내용
        self.next_left = tk.Label(self, text="MODEL : \nPART NAME : \nPART NO. : ", 
                                font=self.fonts["section"], fg="black", bg="#d7e8f4", 
                                anchor="w", justify="left")
        self.next_left.grid(row=4, column=0, sticky="nsew", padx=(8,0), pady=0)
        
        self.next_center = tk.Label(self, text="", font=self.fonts["section"], 
                                  fg="black", bg="#d7e8f4", anchor="center")
        self.next_center.grid(row=4, column=2, sticky="nsew", padx=0, pady=0)
        
        self.next_right = tk.Label(self, text="PLAN : ", 
                                 font=self.fonts["section"], fg="black", bg="#d7e8f4", 
                                 anchor="w", justify="left")
        self.next_right.grid(row=4, column=4, sticky="nsew", padx=(0,8), pady=0)
    
    def get_date_sum_counts(self, target_date):
        plans = Data.get_plans()
        completed_sum = 0
        plan_sum = 0
        for plan in plans:
            plan_date = plan['date']
            if plan_date == target_date:
                completed_sum += int(plan['completed_count'])
                plan_sum += int(plan['plan_count'])
        return completed_sum, plan_sum

    def setup_progress_section(self):
        # 날짜 변수 초기화
        self.today_date = datetime.now()
        self.tomorrow_date = self.today_date + timedelta(days=1)

        # PLAN & PROGRESS 통합 프레임
        progress_frame = tk.Frame(self, bg="#ece3f3")
        progress_frame.grid(row=5, column=0, columnspan=5, rowspan=2, sticky="nsew", padx=8, pady=0)
        progress_frame.grid_rowconfigure(0, weight=0)
        progress_frame.grid_rowconfigure(1, weight=1)
        progress_frame.grid_columnconfigure(0, weight=1)
        progress_frame.grid_columnconfigure(1, weight=0)
        progress_frame.grid_columnconfigure(2, weight=1)
        progress_frame.grid_columnconfigure(3, weight=0)
        progress_frame.grid_columnconfigure(4, weight=1)

        # PLAN & PROGRESS 헤더
        self.plan_title = tk.Label(
            progress_frame, text="PLAN & PROGRESS(%)",
            font=self.fonts["title"],
            fg="black", bg="#ece3f3"
        )
        self.plan_title.grid(row=0, column=0, columnspan=5, sticky="ew")

        # 날짜 조작 함수
        def update_dates(days):
            self.today_date += timedelta(days=days)
            self.tomorrow_date = self.today_date + timedelta(days=1)
            self.update_progress_counts()

        # TODAY 프레임
        today_frame = tk.Frame(progress_frame, bg="#ece3f3")
        today_frame.grid(row=1, column=0, sticky="nsew", padx=(8,0), pady=0)
        self.today_label1 = tk.Label(
            today_frame, text="TODAY",
            font=self.fonts["section_bold"],
            fg="black", bg="#ece3f3"
        )
        self.today_label1.pack(pady=(20,5))

        # 날짜 표시 및 +/- 버튼
        date_btn_frame = tk.Frame(today_frame, bg="#ece3f3")
        date_btn_frame.pack(pady=2)
        btn_minus = tk.Button(date_btn_frame, text="-", width=2, command=lambda: update_dates(-1))
        btn_minus.pack(side="left", padx=2)
        self.today_label2 = tk.Label(
            date_btn_frame, text=self.today_date.strftime('%m/%d'),
            font=self.fonts["section"], fg="black", bg="#ece3f3", width=8
        )
        self.today_label2.pack(side="left", padx=2)
        btn_plus = tk.Button(date_btn_frame, text="+", width=2, command=lambda: update_dates(1))
        btn_plus.pack(side="left", padx=2)

        self.today_label3 = tk.Label(
            today_frame, text="",  # 동적으로 표시
            font=self.fonts["section"],
            fg="black", bg="#ece3f3"
        )
        self.today_label3.pack(pady=2)
        self.today_label4 = tk.Label(
            today_frame, text="",  # 동적으로 표시
            font=self.fonts["section"],
            fg="black", bg="#ece3f3"
        )
        self.today_label4.pack(pady=(2,20))

        # TOMORROW 프레임
        tomorrow_frame = tk.Frame(progress_frame, bg="#ece3f3")
        tomorrow_frame.grid(row=1, column=2, sticky="nsew", padx=0, pady=0)
        self.tomorrow_label1 = tk.Label(
            tomorrow_frame, text="TOMORROW",
            font=self.fonts["section_bold"],
            fg="black", bg="#ece3f3"
        )
        self.tomorrow_label1.pack(pady=(20,5))
        self.tomorrow_label2 = tk.Label(
            tomorrow_frame, text=self.tomorrow_date.strftime('%m/%d'),
            font=self.fonts["section"], fg="black", bg="#ece3f3", width=8
        )
        self.tomorrow_label2.pack(pady=2)
        self.tomorrow_label3 = tk.Label(
            tomorrow_frame, text="",  # 동적으로 표시
            font=self.fonts["section"],
            fg="black", bg="#ece3f3"
        )
        self.tomorrow_label3.pack(pady=2)
        self.tomorrow_label4 = tk.Label(
            tomorrow_frame, text="",  # 동적으로 표시
            font=self.fonts["section"],
            fg="black", bg="#ece3f3"
        )
        self.tomorrow_label4.pack(pady=(2,20))

        # TOTAL 프레임
        total_frame = tk.Frame(progress_frame, bg="#ece3f3")
        total_frame.grid(row=1, column=4, sticky="nsew", padx=(0,8), pady=0)
        self.total_label1 = tk.Label(
            total_frame, text="TOTAL",
            font=self.fonts["section_bold"],
            fg="black", bg="#ece3f3"
        )
        self.total_label1.pack(pady=(20,5))
        self.total_label2 = tk.Label(
            total_frame, text="",  # 동적으로 표시
            font=self.fonts["section"], fg="black", bg="#ece3f3"
        )
        self.total_label2.pack(pady=2)
        self.total_label3 = tk.Label(
            total_frame, text="",  # 동적으로 표시
            font=self.fonts["section"], fg="black", bg="#ece3f3"
        )
        self.total_label3.pack(pady=(2,20))

        # 날짜별 합계 및 % 업데이트 함수
        def update_progress_counts():
            today_str = self.today_date.strftime('%m/%d')
            tomorrow_str = self.tomorrow_date.strftime('%m/%d')

            today_completed, today_plan = self.get_date_sum_counts(today_str)
            today_percent = (today_completed / today_plan * 100) if today_plan else 0
            self.today_label2.config(text=today_str)
            self.today_label3.config(text=f"{today_completed} / {today_plan}")
            self.today_label4.config(text=f"{today_percent:.1f} %")

            tomorrow_completed, tomorrow_plan = self.get_date_sum_counts(tomorrow_str)
            tomorrow_percent = (tomorrow_completed / tomorrow_plan * 100) if tomorrow_plan else 0
            self.tomorrow_label2.config(text=tomorrow_str)
            self.tomorrow_label3.config(text=f"{tomorrow_completed} / {tomorrow_plan}")
            self.tomorrow_label4.config(text=f"{tomorrow_percent:.1f} %")

            total_completed = today_completed + tomorrow_completed
            total_plan = today_plan + tomorrow_plan
            total_percent = (total_completed / total_plan * 100) if total_plan else 0
            self.total_label2.config(text=f"{total_completed} / {total_plan}")
            self.total_label3.config(text=f"{total_percent:.1f} %")

        self.update_progress_counts = update_progress_counts
        self.update_progress_counts()

        
    
    def setup_separators(self):
        # 세로 구분선
        sep1 = ttk.Separator(self, orient="vertical")
        sep1.grid(row=1, column=1, rowspan=30, sticky="ns")
        
        sep2 = ttk.Separator(self, orient="vertical")
        sep2.grid(row=1, column=3, rowspan=30, sticky="ns")
    
    def update_data(self):
        # 시간 업데이트
        self.label_time.config(text=get_time())
        
        # 현재/다음 작업 조회
        current_plan, next_plan = get_current_next_plans()
        
        # 현재 작업 업데이트
        if current_plan:
            part_info = get_part_info(current_plan["part"])
            self.current_left.config(
                text=f"MODEL : {part_info['model']}\n"
                     f"PART NAME : {part_info['part_name']}\n"
                     f"PART NO. : {part_info['part_number']}"
            )
            
            load_part_image(current_plan["part"], self.current_center)
            
            plan_count = current_plan["plan_count"]
            completed_count = current_plan["completed_count"]
            percent = (completed_count / plan_count * 100) if plan_count > 0 else 0
            self.current_right.config(
                text=f"PLAN : {plan_count}\n\n"
                     f"OK : {completed_count} (ACH.{percent:.1f}%)"
            )
        else:
            self.current_left.config(text="MODEL : \nPART NAME : \nPART NO. : ")
            self.current_center.config(image=None, text="No Current Plan")
            self.current_right.config(text="PLAN : \n\nOK : ")
        
        # 다음 작업 업데이트
        if next_plan:
            part_info = get_part_info(next_plan["part"])
            self.next_left.config(
                text=f"MODEL : {part_info['model']}\n"
                     f"PART NAME : {part_info['part_name']}\n"
                     f"PART NO. : {part_info['part_number']}"
            )
            
            load_part_image(next_plan["part"], self.next_center)
            
            self.next_right.config(text=f"PLAN : {next_plan['plan_count']}")
        else:
            self.next_left.config(text="MODEL : \nPART NAME : \nPART NO. : ")
            self.next_center.config(image=None, text="No Next Plan")
            self.next_right.config(text="PLAN : ")
    
    def periodic_update(self):
        self.update_data()
        self.after(1000, self.periodic_update)  # 5초마다 업데이트

if __name__ == "__main__":
    # 독립 실행 시 테스트용
    root = tk.Tk()
    root.withdraw()
    app = ProductionUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()