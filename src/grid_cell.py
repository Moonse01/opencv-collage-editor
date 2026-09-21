import cv2
import numpy as np
import utils
import filters 

class GridCell:
    def __init__(self, x, y, w, h):
        # 1. 위치와 크기 < cell이 화면이 어디에(x,y) & 얼마나 크게(w,h)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        
        # 2. cv_image < 현재 화면에 보여줄 최종 결과물 & tk_image < cv_image를 Tkinter 화면용으로 변환한 것(refresh_image 함수를 통해서)
        self.cv_image = None   
        self.tk_image = None   
        
        # 3. 비파괴 편집 < 원본 이미지를 건드리지 않고, 투명한 막 위에서 작업하는 것
        # 투명한 막만 치우면 언제든지 깨끗한 원본으로 돌아갈 수 있습니다. < 데이터 손실을 막기 위해서
        self.source_image = None  # 원본 < 초기화용
        self.base_image = None    # 작업용 사본 < undo의 기준 & 스티커나 필터는 여기에 적용됨
        self.brightness_val = 0   # 밝기 조절은 여기서만 일어남
        
        # base_image는 작업 원본(이미지+스티커+필터) vs cv_image 최종 결과물 < 이미지+스티커+필터+밝기
        # base_image를 따로 두지 않고, cv_image에 직접 더하기/빼기를 한다면 색깔 정보가 영구적으로 파괴됩니다.
        
        # 4. 실행 취소(undo)를 위한 stack
        self.history = []  # 과거의 base_image들을 쌓아두는 리스트
        self.max_history = 15  # 15단계까지만 < 메모리 절약

    def contains(self, mx, my):
        return (self.x <= mx <= self.x + self.w) and (self.y <= my <= self.y + self.h)

    def set_image(self, cv_image):
        # 사진을 처음 넣을 때 사용하는 함수
        
        # [안전장치] 이미지가 없으면 중단
        if cv_image is None: 
            print("오류: 빈 이미지가 전달되었습니다.")
            return

        resized_img = utils.resize_and_crop(cv_image, self.w, self.h)
        # 칸에 맞추어 이미지를 미리 줄여서 넣습니다.
        
        # 초기화
        self.source_image = resized_img.copy() # 원본
        self.base_image = resized_img.copy()   # 작업시 사용할 원본
        self.brightness_val = 0
        
        # 히스토리도 깨끗하게 비웁니다.
        self.history = []
        
        self.cv_image = resized_img
        self.refresh_image() # 화면 갱신

    def set_brightness(self, value):
        # 밝기 조절
        self.brightness_val = value # 값 저장
        
        # base_image(원본)을 꺼내와서, 현재 슬라이더 만큼 밝게 만들어서 cv_image에 적용하기
        if self.base_image is not None:
            self.cv_image = filters.apply_brightness(self.base_image, self.brightness_val)
            self.refresh_image() # 화면 갱신

    def apply_destructive_filter(self, new_img):
        # 필터/스티커 확정
        
        # 1. 과거 기록 저장 (백업)
        if self.base_image is not None:
            # 현재 상태(이미지+밝기값)를 딕셔너리로 묶어서 스택에 push
            self.history.append({
                'base_image': self.base_image.copy(),
                'brightness_val': self.brightness_val
            })
            
            # 너무 많이 쌓이면 오래된 것부터 삭제
            if len(self.history) > self.max_history:
                self.history.pop(0)
        
        # 2. 현재 상태 덮어쓰기
        # 혹시 크기가 변했을까봐 리사이즈
        new_img = utils.resize_and_crop(new_img, self.w, self.h)
        
        self.base_image = new_img.copy() 
        self.brightness_val = 0          
        self.cv_image = new_img
        self.refresh_image()

    def reset_to_original(self):
        # 초기화 & 실행 취소
        # 태초의 원본(source_image)으로 싹 다 되돌립니다.
        if self.source_image is not None:
            self.history = []  # 과거 기록도 삭제
            self.base_image = self.source_image.copy()
            self.brightness_val = 0
            self.cv_image = self.source_image.copy()
            self.refresh_image()

    def undo(self):
        # 실행 취소
        # 기록이 비어있으면(stack에) 아무것도 안 함
        if len(self.history) == 0:
            print("더 이상 되돌릴 작업이 없습니다.")
            return
        
        # pop, 스택의 맨 위(가장 최근) 상태를 꺼냅니다.
        prev_state = self.history.pop()
        
        # restore, 꺼낸 상태로 현재 상태를 덮어씁니다.
        self.base_image = prev_state['base_image']
        self.brightness_val = prev_state['brightness_val']
        
        # 복원된 밝기 값이 있다면 다시 적용해서 보여줘야 완벽한 복구
        if self.brightness_val != 0:
            self.cv_image = filters.apply_brightness(self.base_image, self.brightness_val)
        else:
            self.cv_image = self.base_image.copy()
        
        self.refresh_image()

    def refresh_image(self):
        if self.cv_image is None:
            return
        # 데이터(opencv, bgr) > 화면용(tkinter, rgb) 변환
        self.tk_image = utils.convert_cv_to_tk(self.cv_image, fit_size=(self.w, self.h))