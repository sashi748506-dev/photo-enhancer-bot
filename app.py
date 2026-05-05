import cv2
import numpy as np
import torch
from PIL import Image, ImageFilter, ImageEnhance

# 1. Depth Map Load karne ke liye Torch Hub se free MiDaS model use karenge
print("AI Depth Model load ho raha hai...")
model_type = "MiDaS_small"  # Lightweight aur fast processing ke liye
midas = torch.hub.load("intel-isl/MiDaS", model_type)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
midas.to(device)
midas.eval()

# MiDaS transforms load karna
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
transform = midas_transforms.small_transform if model_type == "MiDaS_small" else midas_transforms.dpt_transform

def enhance_photo_with_depth(image_path, output_path):
    # Original Image ko OpenCV aur PIL dono mein load karna
    img_cv = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    
    h, w, _ = img_cv.shape

    # ---- STEP 1: AI DEPTH MAP GENERATION ----
    input_batch = transform(img_rgb).to(device)
    with torch.no_grad():
        prediction = midas(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img_cv.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()
    
    depth_map = prediction.cpu().numpy()
    depth_map = cv2.normalize(depth_map, None, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    # ---- STEP 2: SUBJECT SHARPENING (HD TEXTURE) ----
    # Subject ko clear karne ke liye sharpening filter
    sharpener = ImageEnhance.Sharpness(pil_img)
    sharpened_img = sharpener.enhance(2.0)  # Details ko double sharp karna
    
    # ---- STEP 3: DEPTH-DEPENDENT GRADIENT BLUR ----
    # Hum original image ko bohot zyada blur karenge (Lens blur effect ke liye)
    fully_blurred_img = sharpened_img.filter(ImageFilter.GaussianBlur(radius=15))
    
    # Depth map ko use karke blurred aur sharp image ko blend karna (Edge Protection)
    mask = Image.fromarray(depth_map).convert("L")
    # Mask ko invert kar rahe hain taaki background blur ho aur foreground saaf rahe
    mask_inverted = Image.eval(mask, lambda x: 255 - x) 
    
    # Dono images ko mix karna mask ke aadhar par
    final_blend = Image.composite(fully_blurred_img, sharpened_img, mask_inverted)
    
    # ---- STEP 4: GRAIN MATCHING (REALISM) ----
    # Halka sa digital grain add karna taaki original lage
    blend_np = np.array(final_blend)
    noise = np.random.normal(0, 3, blend_np.shape).astype(np.uint8) # 3 units ka mild noise
    real_hd_img = cv2.add(blend_np, noise)
    
    # Save processed image
    output_rgb = cv2.cvtColor(real_hd_img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, output_rgb)
    print("Photo Enhance Ho Gayi!")

# Test karne ke liye (Aap local test kar sakte hain):
# enhance_photo_with_depth("input.jpg", "output.jpg")
