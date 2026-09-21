import tkinter as tk

class Toolbar(tk.Frame):
    def __init__(self, master):
        super().__init__(master, width=250, bg="#f0f0f0", relief="raised", bd=1) 
        self.canvas = None # 초기에는 연결된 캔버스가 없으므로 None. 나중에 Main이 set_canvas()로 채워줌

        # [1구역] 파일 메뉴 (Main과 소통)
        file_frame = tk.Frame(self, bg="#f0f0f0")
        file_frame.pack(fill="x", padx=10, pady=(20,10)) 

        btn_open = tk.Button(file_frame, text="사진 불러오기", bg="#3b82f6", fg="white", 
                             font=("맑은 고딕",11,"bold"), relief="flat", 
                             command=self.master.file_open)
        btn_open.pack(fill="x", pady=2)
        
        btn_save = tk.Button(file_frame, text="저장하기", bg="#10b981", fg="white", 
                             font=("맑은 고딕", 11,"bold"), relief="flat", 
                             command=self.master.file_save)
        btn_save.pack(fill="x", pady=2)
        
        # [Undo] 실행 취소
        btn_undo = tk.Button(file_frame, text="↩ 실행 취소 (Undo)", bg="#f59e0b", fg="white", 
                             font=("맑은 고딕", 10,"bold"), relief="flat", 
                             command=lambda: self.canvas.apply_filter_to_selected('undo'))
        btn_undo.pack(fill="x", pady=5)

        # [Reset] 초기화
        btn_reset = tk.Button(file_frame, text="선택 사진 초기화", bg="#ef4444", fg="white", 
                              font=("맑은 고딕", 10,"bold"), relief="flat", 
                              command=lambda: self.canvas.apply_filter_to_selected('reset'))
        btn_reset.pack(fill="x", pady=2)

        # [구분선] 얇은 회색 선
        tk.Frame(self, height=2, bg="#d1d5db").pack(fill="x", padx=10, pady=5)

        # [2구역] 레이아웃 모음
        layout_frame = tk.LabelFrame(self, text="레이아웃", bg="#f0f0f0", font=("맑은 고딕",10,"bold"))
        layout_frame.pack(fill="x", padx=10, pady=5)
        
        self.create_flat_button(layout_frame, "2x2 그리드", lambda: self.canvas.set_layout("2x2"))
        self.create_flat_button(layout_frame, "1+2 그리드", lambda: self.canvas.set_layout("1+2"))

        # [3구역] 기본 편집 (반전, 스티커, 밝기)
        edit_frame = tk.LabelFrame(self, text="기본 편집", bg="#f0f0f0", font=("맑은 고딕",10,"bold"))
        edit_frame.pack(fill="x", padx=10, pady=5)
        
        # [좌우반전 & 상하반전] (한 줄에 2개 배치하기 위해 row1 프레임 사용)
        row1 = tk.Frame(edit_frame, bg="#f0f0f0")
        row1.pack(fill="x")
        self.create_half_button(row1, "↔ 좌우", lambda: self.canvas.apply_filter_to_selected('flip_h'))
        self.create_half_button(row1, "↕ 상하", lambda: self.canvas.apply_filter_to_selected('flip_v'))
        
        # [스티커]
        self.create_flat_button(edit_frame, "★ 스티커", lambda: self.canvas.add_sticker_to_selected()) 

        # [밝기 슬라이더]
        lbl_bright = tk.Label(edit_frame, text="밝기 조절", bg="#f0f0f0", font=("맑은 고딕", 9))
        lbl_bright.pack(anchor="w", padx=5, pady=(5,0))
        
        self.scale_bright = tk.Scale(edit_frame, from_=-100, to=100, orient="horizontal", 
                                     bg="#f0f0f0", highlightthickness=0,
                                     command=self.on_brightness_change)
        self.scale_bright.set(0) 
        self.scale_bright.pack(fill="x", padx=5, pady=5)

        # [4구역] 특수 효과 (필터)
        filter_frame = tk.LabelFrame(self, text="특수 효과", bg="#f0f0f0", font=("맑은 고딕",10,"bold"))
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        self.create_flat_button(filter_frame, "스케치 (Edge)", lambda: self.canvas.apply_filter_to_selected('sketch'))
        self.create_flat_button(filter_frame, "블러 (Blur)", lambda: self.canvas.apply_filter_to_selected('blur'))
        self.create_flat_button(filter_frame, "모자이크", lambda: self.canvas.apply_filter_to_selected('mosaic'))
        self.create_flat_button(filter_frame, "세피아", lambda: self.canvas.apply_filter_to_selected('sepia'))
        self.create_flat_button(filter_frame, "흑백 변환", lambda: self.canvas.apply_filter_to_selected('gray'))
        self.create_flat_button(filter_frame, "반전 (Invert)", lambda: self.canvas.apply_filter_to_selected('invert'))
    
    def create_flat_button(self, parent, text, command): 
        # 꽉 찬 버튼 생성 헬퍼 함수
        btn = tk.Button(parent, text=text, command=command, bg="white", fg="black", relief="solid", bd=1, cursor="hand2")
        btn.pack(fill="x", pady=1)
        return btn
    
    def create_half_button(self, parent, text, command):
        # 반쪽 버튼 생성 헬퍼 함수
        btn = tk.Button(parent, text=text, command=command, bg="white", fg="black", relief="solid", bd=1, cursor="hand2", width=12)
        btn.pack(side="left", fill="x", expand=True, padx=1, pady=1)
        return btn

    def on_brightness_change(self, val):
        # Toolbar -> Canvas: 사용자가 마우스로 슬라이더를 드래그할 때마다 실행
        if self.canvas:
            self.canvas.apply_brightness_value(val)

    def update_slider(self, value):
        # Canvas -> Toolbar: 캔버스 쪽에서 상황이 변했을 때(Undo, Reset), 슬라이더 위치를 강제로 맞춤
        self.scale_bright.set(value)

    def set_canvas(self, canvas): 
        # Main -> Toolbar: Main이 실행되자마자 Canvas의 위치(주소)를 알려줌
        self.canvas = canvas