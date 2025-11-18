# 📦 Advanced Food Barcode Scanner (Streamlit App)

A powerful barcode-scanning application built using **Streamlit**, **OpenCV**, and **Pyzbar**, enhanced with multi-API food product lookup for maximum accuracy.

This application allows users to scan **food barcodes** using a camera and automatically retrieves:

- 🛒 Product Name  
- 🏷 Brand  
- 🍽 Category  
- 🌍 Country of Origin  
- 🍎 Nutrition per 100g  
- 🧪 Ingredients  
- 🖼 Product Image  

---

## 🚀 Features

### 🔍 1. Smart Barcode Detection
The scanner uses multiple image-processing techniques to detect barcodes even in low-light or blurry conditions:

- Grayscale conversion  
- Gaussian blur  
- Adaptive thresholding  
- Otsu thresholding  
- CLAHE enhancement  
- Image sharpening  

### 🌐 2. Multi-API Food Search
To maximize product coverage, the application checks:

1. **OpenFoodFacts API v2**  
2. **OpenFoodFacts API v0**  
3. **OpenFoodFacts Search API**  
4. **OpenFoodFacts India Database**

If any API recognizes the barcode, the product information is displayed instantly.

### 📷 3. Live Camera Scanning
Uses `st.camera_input()` so users can scan from laptop or mobile camera.

### 🧩 4. Clean & Simple UI
No UI changes required — completely user-friendly.

---

## 🛠 Tech Stack

| Component | Technology |
|----------|------------|
| Frontend | Streamlit |
| Computer Vision | OpenCV |
| Barcode Decoding | Pyzbar |
| API | OpenFoodFacts |
| Image Processing | Pillow |
| Language | Python |

---

## 📁 Project Structure

