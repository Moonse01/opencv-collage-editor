import cv2
import numpy as np

def apply_flip_horizontal(img):
    #좌우 반전
    return cv2.flip(img, 1)

def apply_flip_vertical(img):
    #상하 반전
    return cv2.flip(img, 0)

def apply_brightness(img, value):
    # int16 변환 후 clip으로 안전하게 밝기 조절
    img_big = img.astype(np.int16)
    img_big = img_big + value
    img_big = np.clip(img_big, 0, 255)
    return img_big.astype(np.uint8)

# 스티커 합성
def apply_sticker(background, sticker_path, center_x, center_y):
    sticker = cv2.imread(sticker_path, cv2.IMREAD_UNCHANGED) #1.스티커 이미지 읽기
    if sticker is None: return background

    #2.배경의 30% 크기로 조절
    bg_h, bg_w = background.shape[:2]
    sticker_h, sticker_w = sticker.shape[:2]
    
    scale_factor = 0.3 
    new_w = int(bg_w * scale_factor)
    if new_w == 0: new_w = 1
    new_h = int(sticker_h * (new_w / sticker_w))
    
    #화질 저하 최소화
    sticker_resized = cv2.resize(sticker, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    #3.클릭한 좌표(center)가 스티커 중앙에 오도록 계산
    tl_x = center_x - (new_w // 2)
    tl_y = center_y - (new_h // 2)

    #4.경계 검사 및 잘라내기 (Slicing)
    x1, x2 = max(0, tl_x), min(bg_w, tl_x + new_w)
    y1, y2 = max(0, tl_y), min(bg_h, tl_y + new_h)
    
    st_x1 = max(0, -tl_x)
    st_x2 = st_x1 + (x2 - x1)
    st_y1 = max(0, -tl_y)
    st_y2 = st_y1 + (y2 - y1)
    
    if x2 <= x1 or y2 <= y1: return background

    out = background.copy()
    sticker_crop = sticker_resized[st_y1:st_y2, st_x1:st_x2]
    bg_crop = out[y1:y2, x1:x2]
    
    # 알파 블렌딩 (투명 합성)
    if sticker_crop.shape[2] == 4:
        alpha_s = sticker_crop[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        for c in range(0, 3):
            bg_crop[:, :, c] = (alpha_s * sticker_crop[:, :, c] + alpha_l * bg_crop[:, :, c])
        out[y1:y2, x1:x2] = bg_crop
    else:
        out[y1:y2, x1:x2] = sticker_crop
        
    return out

def apply_sketch(img):
    #1.흑백 변환>2.블러>3.canny엣지 검출
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 30, 100)
    edges_inv = cv2.bitwise_not(edges)
    return cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)

def apply_mosaic(img):
    h, w = img.shape[:2]
    scale_factor = 0.05 
    new_w = int(w * scale_factor)
    new_h = int(h * scale_factor)
    if new_w < 1: new_w = 1
    if new_h < 1: new_h = 1
    small = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    mosaic = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    return mosaic

def apply_grayscale(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

def apply_invert(img):
    return cv2.bitwise_not(img)

def apply_sepia(img):
    img_float = img.astype(np.float32)
    kernel = np.array([[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]])
    sepia_img = cv2.transform(img_float, kernel)
    sepia_img = np.clip(sepia_img, 0, 255)
    return sepia_img.astype(np.uint8)

def apply_blur(img):
    return cv2.GaussianBlur(img, (15, 15), 0)
