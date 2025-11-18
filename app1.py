import streamlit as st
import cv2
import numpy as np
from pyzbar import pyzbar
import requests
from PIL import Image
import io
import time

class EnhancedBarcodeScanner:
    def preprocess_frame(self, frame):
        processed_frames = []
        processed_frames.append(("Original", frame))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        processed_frames.append(("Grayscale", gray))

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        processed_frames.append(("Blurred", blurred))

        adaptive = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        processed_frames.append(("Adaptive Threshold", adaptive))

        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        processed_frames.append(("Binary", binary))

        _, otsu = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        processed_frames.append(("Otsu", otsu))

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_img = clahe.apply(gray)
        processed_frames.append(("CLAHE", clahe_img))

        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(gray, -1, kernel)
        processed_frames.append(("Sharpened", sharpened))

        return processed_frames

    def detect(self, frame):
        processed_frames = self.preprocess_frame(frame)
        unique_barcodes = {}

        for name, processed in processed_frames:
            barcodes = pyzbar.decode(processed)
            for barcode in barcodes:
                data = barcode.data.decode('utf-8', errors='ignore')
                btype = barcode.type
                key = f"{btype}:{data}"

                if key not in unique_barcodes:
                    unique_barcodes[key] = barcode

        return list(unique_barcodes.values())

    def get_product_info(self, barcode):
        info = {"barcode": barcode, "found": False}

        # --- API URLs (fallback order) ---
        urls = [
            f"https://world.openfoodfacts.org/api/v2/product/{barcode}",   # V2 API
            f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json",  # V0 API
            f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={barcode}&search_simple=1&action=process&json=1",  # Search API
            f"https://in.openfoodfacts.org/api/v0/product/{barcode}.json"  # India DB
        ]

        for url in urls:
            try:
                r = requests.get(url, timeout=5)
                data = r.json()

                # Case: product details found (V0/V2)
                if "product" in data and data.get("status") == 1:
                    p = data["product"]
                # Case: search API found items
                elif "products" in data and len(data["products"]) > 0:
                    p = data["products"][0]
                else:
                    continue

                # Fill info
                info.update({
                    "found": True,
                    "name": p.get("product_name", "Unknown"),
                    "brand": p.get("brands", "Unknown"),
                    "category": p.get("categories", "N/A"),
                    "origin": p.get("countries", "N/A"),
                    "ingredients": p.get("ingredients_text", "N/A"),
                    "image": p.get("image_url"),
                    "nutrition": {
                        "energy": p.get("nutriments", {}).get("energy-kcal_100g", "N/A"),
                        "fat": p.get("nutriments", {}).get("fat_100g", "N/A"),
                        "carbs": p.get("nutriments", {}).get("carbohydrates_100g", "N/A"),
                        "protein": p.get("nutriments", {}).get("proteins_100g", "N/A")
                    }
                })

                return info

            except Exception as e:
                print("API Error:", e)
                continue

        return info


scanner = EnhancedBarcodeScanner()

st.title("📷 Advanced Barcode Scanner (Streamlit Version)")
st.write("Scan any **food item** and get its **name, brand, ingredients & nutrition.**")

img = st.camera_input("Capture a barcode")

if img:
    # Convert to numpy array
    bytes_data = img.getvalue()
    pil_img = Image.open(io.BytesIO(bytes_data))
    frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    barcodes = scanner.detect(frame)

    if not barcodes:
        st.warning("❌ No barcode detected. Try again.")
    else:
        st.success(f"✅ Detected {len(barcodes)} barcode(s)")

        for b in barcodes:
            data = b.data.decode('utf-8')
            st.subheader(f"📌 Barcode: {data}")

            info = scanner.get_product_info(data)

            if info["found"]:
                st.write(f"### 🛒 {info['name']}")
                st.write(f"**Brand:** {info['brand']}")
                st.write(f"**Category:** {info['category']}")
                st.write(f"**Origin:** {info['origin']}")

                if info["image"]:
                    st.image(info["image"], width=250)

                st.write("### 🍎 Nutrition per 100g")
                st.json(info["nutrition"])

                if info["ingredients"] != "N/A":
                    st.write("### 🧪 Ingredients")
                    st.write(info["ingredients"])

            else:
                st.error("❌ Product not found in any database.")
