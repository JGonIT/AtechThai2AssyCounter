import threading
import Plan_UI
import arduino_google_sheet  # 새로 생성할 아두이노 통합 모듈

if __name__ == "__main__":
    # 아두이노 데이터 처리 스레드 시작
    arduino_thread = threading.Thread(target=arduino_google_sheet.run_arduino_google_sheet, daemon=True)
    arduino_thread.start()
    
    # Plan UI 실행
    app = Plan_UI.PlanManager()
    app.mainloop()
