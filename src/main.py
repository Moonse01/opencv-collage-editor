import tkinter as tk
from tkinter import filedialog #'파일 열기'와 '저장하기' 팝업창은 윈도우 창 레벨에서 관리
import cv2
import numpy as np
from toolbar import Toolbar
from canvas import CollageCanvas

#Main.py는 프로그램의 지휘관 역할을 하는 파일이며,전체 구조를 잡고,부품을 조립하고,
#가장 중요한 데이터의 입구(Open)&출구(Save)를 담당한다.

class MainApplication(tk.Tk):
    #프로그램의 본체
    def __init__(self):
        super().__init__()
        self.title("콜라주 에디터 프로그램")
        self.geometry("1200x800") #초기 창 크기 설정, 가로x세로

        #화면 구성/ 전체 화면을 좌측(도구)와 우측(작업장)으로 분할
        
        #1.Toolbar생성 및 배치(좌측 도구를 위한 것)
        self.toolbar = Toolbar(self)
        self.toolbar.pack(side="left",fill="y",padx=0,pady=0)

        #2.Canvas생성 및 배치(오른쪽 캔버스를 위한 것)
        self.canvas = CollageCanvas(self, bg="gray80")
        self.canvas.pack(side="right", fill="both", expand=True, padx=10, pady=10) 
        #expand=True:창 크기를 늘리면 남는 공간을 Canvas가 다 차지함

        #3.객체 연결
        #Toolbar객체와 Canvas객체는 서로를 모른다, Toolbar의 버튼을 눌렀을 때>Canvas가 반응하려면,
        #Toolbar에게 Canvas의 주소를 알려주어야 한다.
        self.toolbar.set_canvas(self.canvas)

    def file_open(self):
        #사진 불러오기
        #1.파일 탐색기를 엽니다.>2.이미지를 읽습니다,>3.캔버스에게 대기("pending")시킵니다.

        #1.윈도우 탐색기 열기
        filepath = filedialog.askopenfilename(
            title="사진 불러오기",
            filetypes=[("이미지 파일","*.jpg;*.jpeg;*.png;*.bmp"),("모든 파일","*.*")]
        )
        if not filepath: return #취소를 누를 때 " "(빈문자열)들어오기에 오류방지를 위해 함수를 끝내게 함

        #2.OpenCV로 이미지 데이터를 읽기(BGR)
        cv_image = cv2.imread(filepath)

        if cv_image is None:
            print("이미지를 읽을 수 없습니다.")
            return
        
        #3.이렇게 받아온 이미지를 바로 배치하는 것이 아닌 사용자가 어느 칸에 사진을 넣을지
        #  정하지 않았기에>일단 마우스에 들고 있는 상태로 만든다.
        self.canvas.set_pending_image(cv_image)

    def file_save(self):
        #사진 저장하기
        #1.저장 경로를 묻습니다.>2.캔버스에게 편집이 된 데이터를 요청합니다.>3.파일로 씁니다.

        #1.저장 경로 받기
        filepath = filedialog.asksaveasfilename(
            title="이미지 저장",
            defaultextension=".jpg",
            filetypes=[("JPG 파일","*.jpg"),("PNG 파일","*.png")]
        )
        if not filepath: return 

        #2.화면 캡쳐가 아닌 데이터의 재구성
        #tk_image로 저장하는 것이 아닌 원본 데이터를 합쳐서 가져오기
        final_image = self.canvas.get_final_image()

        #3.파일 쓰기
        try:
            cv2.imwrite(filepath, final_image)
            print(f"저장 완료: {filepath}")
        except Exception as e:
            print(f"저장 실패: {e}")

#프로그램 진입점
if __name__ == "__main__":
    app = MainApplication()
    app.mainloop() #창을 띄우고 무한 대기