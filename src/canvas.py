import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import os
from PIL import Image, ImageTk
import numpy as np
import cv2
import utils
import filters
from grid_cell import GridCell

class CollageCanvas(tk.Canvas):
    def __init__(self, master, bg="gray"):
        super().__init__(master, bg=bg)

        # 데이터 관리를 위한 변수들
        self.grid_cells = [] # 화면을 구성하는 칸(GridCell 객체)들을 저장하는 리스트
        self.current_layout = None # 현재 레이아웃 상태를 나타내는 변수("2x2","1+2")

        # 상태 관리 변수들
        self.pending_image = None # main.py에서 파일을 열면 바로 칸에 들어가지 않고 마우스에 이미지가 저장된 상태
        self.selected_cell = None # 사용자가 원하는 그리드를 선택하는, 빨간색 테두리가 쳐진 칸 객체
        self.holding_sticker_path = None # 현재 마우스에 스티커가 붙어있는지 판단
        
        self._resize_timer = None 
        # 창 크기를 움직일 때마다 계산하면 컴퓨터에 부담 -> 움직임이 멈추고 30ms 뒤에 딱 한 번만 계산하기 위한 타이머
        
        self._sticker_thumbnails = [] 
        # 스티커 썸네일을 리스트로 관리하여, 파이썬의 Garbage Collection 때문에 스티커가 지워지는 것을 방지

        # 이벤트 바인딩
        self.bind("<Configure>", self.on_resize) # 창 크기가 변할 때 실행
        self.bind("<Button-1>", self.on_click)   # 마우스 좌클릭 시 실행

    def on_resize(self, event):
        # 창 크기 조절 이벤트가 발생하면 타이머를 재설정
        # 결과적으로 사용자가 드래그를 멈춘 뒤에 perform_resize가 실행됨 (최적화)
        if self._resize_timer is not None:
            self.after_cancel(self._resize_timer)
        self._resize_timer = self.after(30, self.perform_resize)
    
    def perform_resize(self):
        # 창 크기가 변했을 때, 데이터를 날리지 않고 기존 칸들의 좌표와 크기만 업데이트 (리사이징)

        # 예외처리: 리사이징한 창의 크기가 너무 작으면 return
        if self.winfo_width() < 10 or self.winfo_height() < 10:
            return
        # 예외처리: 아직 레이아웃을 정하지 않았다면 return
        if self.current_layout is None or not self.grid_cells:
            return
        
        # 현재 변해버린 창의 너비와 높이를 구하기
        w = self.winfo_width()
        h = self.winfo_height()
        margin = 10

        if self.current_layout == "2x2":
            cell_w = (w - 3*margin)//2
            cell_h = (h - 3*margin)//2

            # 안전장치: 칸이 4개가 확실히 있는지 체크 (4개가 확실히 있을 때만 접근한다)
            if len(self.grid_cells) >= 4:
                self.update_cell_geometry(0, margin, margin, cell_w, cell_h)
                self.update_cell_geometry(1, 2*margin + cell_w, margin, cell_w, cell_h)
                self.update_cell_geometry(2, margin, 2*margin +cell_h, cell_w, cell_h)
                self.update_cell_geometry(3, 2*margin + cell_w, 2*margin + cell_h, cell_w, cell_h)
        
        elif self.current_layout == "1+2":
            cell_w = (w - 3*margin)//2
            h_long = h - 2*margin
            cell_h_short = (h - 3*margin)//2

            if len(self.grid_cells) >= 3:
                self.update_cell_geometry(0, margin, margin, cell_w, h_long)
                self.update_cell_geometry(1, 2*margin + cell_w, margin, cell_w, cell_h_short)
                self.update_cell_geometry(2, 2*margin + cell_w, 2*margin + cell_h_short, cell_w, cell_h_short)

        # 바뀐 대로 다시 그리기
        self.render()

    def update_cell_geometry(self, index, x, y, w, h):
        # 특정 번호(index)의 칸에게 너의 위치(x,y)와 크기(w,h)라고 알려주고,
        # 바뀐 크기에 맞춰서 이미지를 다시 배치시킵니다.
        cell = self.grid_cells[index]
        cell.x = x
        cell.y = y
        cell.w = w
        cell.h = h

        # refresh_image는 grid_cell.py에 있다. (데이터 -> tk_image 변환)
        cell.refresh_image()

    def set_layout(self, layout_name):
        # 툴바 버튼을 통해서 버튼에 명시된 알맞게 그리드를 배치해줍니다. (초기화 로직)
        self.grid_cells = []
        self.current_layout = layout_name
        self.selected_cell = None
        w = self.winfo_width()
        h = self.winfo_height()
        margin = 10

        # 좌표 계산 및 GridCell 객체 생성(append) 코드
        if layout_name == "2x2":
            cell_w = (w - 3*margin)//2
            cell_h = (h - 3*margin)//2
            self.grid_cells.append(GridCell(margin, margin, cell_w, cell_h))
            self.grid_cells.append(GridCell(2*margin + cell_w, margin, cell_w, cell_h))
            self.grid_cells.append(GridCell(margin, 2*margin +cell_h, cell_w, cell_h))
            self.grid_cells.append(GridCell(2*margin + cell_w, 2*margin + cell_h, cell_w, cell_h))

        elif layout_name == "1+2":
            cell_w = (w - 3*margin)//2
            h_long = h - 2*margin
            self.grid_cells.append(GridCell(margin, margin, cell_w, h_long))
            cell_h_short = (h - 3*margin)//2
            self.grid_cells.append(GridCell(2*margin + cell_w, margin, cell_w, cell_h_short))
            self.grid_cells.append(GridCell(2*margin + cell_w, 2*margin + cell_h_short, cell_w, cell_h_short))

        self.render()

    def on_click(self, event):
        # 마우스 클릭 시 모든 판단을 내림

        # 1. 클릭된 좌표가 어느 칸 안인지 찾기
        clicked_cell = None
        for cell in self.grid_cells:
            # cell.contains: 이 좌표(x,y)가 내 구역 안이니? True or False 리턴
            if cell.contains(event.x, event.y):
                clicked_cell = cell
                break
        
        # 여백을 클릭 -> 선택을 해제함
        if clicked_cell is None:
            self.selected_cell = None
            self.holding_sticker_path = None
            self.config(cursor="") # 커서를 기본 모양
            self.render() # 빨간 테두리를 지우기 위해 다시 그리기
            return
        
        # 1순위. 사진 넣기
        if self.pending_image is not None:
            clicked_cell.set_image(self.pending_image)
            self.pending_image = None 
            self.config(cursor="")

        # 2순위. 스티커 붙이기 모드
        elif self.holding_sticker_path is not None:
            # 상대좌표 계산: 전체 창에 대한 좌표가 아닌 해당 칸 기준의 좌표가 필요
            rel_x = event.x - clicked_cell.x
            rel_y = event.y - clicked_cell.y

            # Undo(되돌리기)를 위해 원본을 보호하고, 복사본에 먼저 그려본다.
            img = clicked_cell.cv_image.copy()

            # filters.py의 함수를 호출해 스티커 합성
            img = filters.apply_sticker(img, self.holding_sticker_path, rel_x, rel_y)

            # 확정 단계 -> 변형된 이미지를 저장하고 -> 기존 상태를 History 스택에 넣습니다.
            clicked_cell.apply_destructive_filter(img)
        
            # 이미지가 영구적으로 변했다 -> 밝기 조절 상태도 0으로 초기화해줌
            self.master.toolbar.update_slider(0)

            self.holding_sticker_path = None
            self.config(cursor="")

        # 3순위. 아무것도 안 들고 있을 때 클릭 (일반 선택)
        else:
            self.selected_cell = clicked_cell
            # 현재 선택된 칸의 밝기 값을 읽어와 툴바 슬라이더에 반영
            self.master.toolbar.update_slider(clicked_cell.brightness_val)
        
        self.render()

    def render(self):
        self.delete("all") 

        if not self.grid_cells:
            return
        
        for cell in self.grid_cells:
            # 1. 사진 그리기 (tk_image는 화면 출력용)
            if cell.tk_image is not None:
                self.create_image(cell.x, cell.y, image = cell.tk_image, anchor="nw")
            
            # 2. 테두리 그리기 (선택된 그리드는 빨강, 아니면 파랑)
            if cell == self.selected_cell:
                border_color = "red"
                border_width = 5
            else:
                border_color = "blue"
                border_width = 2
            
            self.create_rectangle(
                cell.x, cell.y,
                cell.x + cell.w, cell.y + cell.h,
                outline = border_color,
                width = border_width,
                fill="" # 내부는 투명하게
            )
                
    def set_pending_image(self, cv_image):
        self.pending_image = cv_image
        self.config(cursor="crosshair") # 장전되었음을 알리기 위해 커서 모양을 바꿈

    def get_final_image(self):
        # 원본 데이터 cv_image를 이용하여 고화질로 재조립한 후 저장하는 데 사용
        h = self.winfo_height()
        w = self.winfo_width()

        # 1. 새하얀 도화지 생성
        final_canvas = np.full((h,w,3), 255, dtype=np.uint8)

        for cell in self.grid_cells:
            if cell.cv_image is not None:
                # 2. 각 칸의 원본 데이터 cv_image를 가져옴
                processed_img = cell.cv_image
                # 3. 안전장치: 이미지 크기가 칸 크기와 다를 경우 오류가 생기므로 대비
                processed_img = cv2.resize(processed_img, (cell.w, cell.h))

                # 4. 좌표 계산
                y_start = cell.y
                y_end = cell.y + cell.h
                x_start = cell.x
                x_end = cell.x + cell.w

                # 도화지의 해당 구역을 이미지 데이터로 덮어씌움
                final_canvas[y_start:y_end, x_start:x_end] = processed_img

        return final_canvas
    
    def apply_filter_to_selected(self, filter_name):
        # 툴바에서 버튼을 누르면 이 함수가 실행 -> Main -> Toolbar -> Canvas 순서로 호출

        if self.selected_cell is None or self.selected_cell.cv_image is None:
            print("선택된 칸이 없거나 이미지가 없습니다.")
            return 
        
        # <초기화> 원본 복구
        if filter_name == 'reset':
            self.selected_cell.reset_to_original() 
            self.master.toolbar.update_slider(0) # 원본이니 밝기도 0으로
            self.render()
            return
        
        # <실행 취소> ~ History 스택 팝
        if filter_name == 'undo':
            self.selected_cell.undo() 
            self.master.toolbar.update_slider(0)
            self.render()
            print("실행 취소 완료")
            return
        
        # 필터 적용
        # 1. 원본 데이터를 복사
        img = self.selected_cell.cv_image.copy()

        # 2. filters.py 모듈을 이용해 이미지 변형
        if filter_name == 'gray': img = filters.apply_grayscale(img)
        elif filter_name == 'invert': img = filters.apply_invert(img)
        elif filter_name == 'sepia': img = filters.apply_sepia(img)
        elif filter_name == 'sketch': img = filters.apply_sketch(img)
        elif filter_name == 'blur': img = filters.apply_blur(img)
        elif filter_name == 'mosaic': img = filters.apply_mosaic(img)
        elif filter_name == 'flip_h': img = filters.apply_flip_horizontal(img)
        elif filter_name == 'flip_v': img = filters.apply_flip_vertical(img)

        # 3. 확정 및 히스토리 저장
        self.selected_cell.apply_destructive_filter(img)
        self.master.toolbar.update_slider(0) # 이미지가 변했으니 밝기 리셋
        self.render()

    def apply_brightness_value(self, value):
        # Toolbar -> Canvas -> GridCell 순으로 밝기 값을 전달합니다.
        if self.selected_cell is None or self.selected_cell.cv_image is None:
            return
        self.selected_cell.set_brightness(int(value))
        self.render()

    def add_sticker_to_selected(self):
        # os 모듈을 이용해 폴더 구조를 읽고, 동적으로 탭과 버튼을 만듭니다.
        folder_path = "stickers"

        # os 모듈이 필요한 이유? 윈도우 탐색기처럼 폴더 존재 여부를 확인하고 생성하기 위함이다.
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path) # 폴더 생성
                messagebox.showinfo("안내", f"'{folder_path}' 폴더가 생성되었습니다.\n안에 카테고리 폴더를 만들고 사진을 넣어주세요!")
            except Exception as e:
                messagebox.showerror("에러", f"폴더 생성 실패: {e}")
            return
        
        # 폴더 목록 읽기
        subfolders = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
        if not subfolders: subfolders = ["."]

        # 팝업창(Toplevel) 생성
        top = tk.Toplevel(self)
        top.title("스티커")
        top.geometry("450x500")
        top.resizable(False, False) # 팝업창 크기 고정

        # 탭 메뉴(Notebook) 생성
        notebook = ttk.Notebook(top)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._sticker_thumbnails = [] 

        # 각 탭마다 버튼 배치
        for sub in subfolders:
            # 탭 역할을 할 프레임 생성
            tab_frame = tk.Frame(notebook, bg="white")

            if sub == ".":
                tab_name = "기본"
                full_path = folder_path
            else:
                tab_name = sub
                full_path = os.path.join(folder_path, sub)
            
            notebook.add(tab_frame, text=tab_name)

            # 파일 찾기
            try:
                files = [f for f in os.listdir(full_path) if f.lower().endswith('.png')]
            except:
                files = []

            if not files:
                tk.Label(tab_frame, text="스티커(.png) 없음", bg="white").pack(pady=20)
                continue
        
            # 한 줄에 4개씩 깔끔하게 정렬된 갤러리
            r, c = 0, 0
            for fname in files:
                path = os.path.join(full_path, fname)
                try:
                    pil_img = Image.open(path)
                    pil_img.thumbnail((70,70))
                    tk_thumb = ImageTk.PhotoImage(pil_img)
                    self._sticker_thumbnails.append(tk_thumb) 
                    btn = tk.Button(tab_frame, image=tk_thumb, bg="white", relief="flat",
                                    command=lambda p = path: self._on_sticker_picked(top, p))
                    # 버튼 배치(한 줄에 4개씩)
                    btn.grid(row=r, column=c, padx=10, pady=10)

                    c += 1
                    if c >= 4: # 4개 차면 다음 줄로
                        c = 0
                        r += 1
                except Exception as e:
                    print(f"로드 실패: {fname}")

    def _on_sticker_picked(self, popup, path):
        # 스티커를 클릭했을 때 실행되는 함수
        print(f"선택된 스티커: {path}")
        self.holding_sticker_path = path # 선택한 경로 저장
        self.config(cursor="tcross") # 커서 모양 변경
        popup.destroy() # 갤러리 창 닫기