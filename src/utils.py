import cv2
import numpy as np
from PIL import Image, ImageTk

def convert_cv_to_tk(cv_image, fit_size=None):
    #빈 이미지가 들어오면 변환 없이 종료 
    if cv_image is None:
        return None 
    
    #크기 맞춤
    if fit_size is not None: 
        target_w, target_h = fit_size
        if target_w>0 and target_h>0:
            cv_image = resize_and_crop(cv_image, target_w,target_h)
    
    #색상 변환
    #opencv기본적으로 bgr순서를 씁니다.
    #tkinter는 rgb순서를 씁니다.
    if cv_image.ndim == 2: 
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_GRAY2RGB)
    else: 
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    
    pil_image = Image.fromarray(rgb_image)
    tk_image = ImageTk.PhotoImage(image=pil_image)

    return tk_image

def resize_and_crop(img, target_w, target_h):
    h, w = img.shape[:2]
    original_ratio = w/h
    target_ratio = target_w/target_h 

    if original_ratio > target_ratio:
        new_h = target_h
        new_w = int(new_h * original_ratio) 
    else:
        new_w = target_w
        new_h = int(new_w / original_ratio )

    img_resized = cv2.resize(img, (new_w,new_h),interpolation=cv2.INTER_LINEAR) 

    start_x = (new_w - target_w)//2
    start_y = (new_h - target_h)//2

    cropped = img_resized[start_y : start_y + target_h, start_x : start_x + target_w] 
    return cropped