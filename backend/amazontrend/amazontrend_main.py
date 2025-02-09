import os
import re
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

amazontrend_app = FastAPI()

class ProductData(BaseModel):
    raw_text: str

# ✅ Load danh sách niche từ file
def load_niche_list(filepath):
    """ Đọc danh sách niche từ file niche.txt """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Không tìm thấy file: {filepath}")

    with open(filepath, "r", encoding="utf-8") as file:
        niches = {line.strip().lower() for line in file if line.strip()}
    return niches

niche_list = load_niche_list("backend/amazontrend/niche.txt")

# ✅ Loại bỏ từ không cần thiết trong cột Niche
EXCLUDE_WORDS = {"t-shirt", "hoodie", "tees", "sweatshirt", "shirt", "tank", "top", "jacket", 
                 "cotton", "button", "casual", "formal", "printed", "cool", "retro", "funny", 
                 "awesome", "stylish", "trendy", "vintage", "classic", "modern", "cute", "i'm", 
                 "women", "men", "my", "her", "his", "your", "everybody", "in", "be", "aren't", 
                 "isn't", "and", "the", "to", "off", "with", "love", "go", "work", "i", "we", 
                 "tee", "shirts", "hoodie", "a", "an", "-", "&", "@", "one", "two", "three", 
                 "100", "2025", "3000"}

def get_niche_from_title(title):
    """ Xác định Niche từ Title, ưu tiên danh sách niche.txt trước """
    words = title.lower().split()
    found_niche = []

    for word in words:
        clean_word = word.strip(",.!?-")

        if clean_word in niche_list and clean_word not in EXCLUDE_WORDS:
            if clean_word.capitalize() not in found_niche:
                found_niche.append(clean_word.capitalize())

    if len(found_niche) < 3:
        for word in words:
            clean_word = word.strip(",.!?-")

            if clean_word not in EXCLUDE_WORDS and clean_word not in found_niche:
                found_niche.append(clean_word.capitalize())

                if len(found_niche) >= 3:
                    break  

    return ", ".join(found_niche[:3]) if found_niche else "General"

# ✅ Trích xuất dữ liệu từ raw_text
def extract_product_info(raw_text):
    """ Trích xuất thông tin sản phẩm từ dữ liệu thô """
    print("\n🔍 Dữ liệu raw_text nhận từ frontend:\n", repr(raw_text))

    raw_text = raw_text.replace('\xa0', ' ')  
    products = []
    today = datetime.today()
    
    lines = raw_text.strip().split("\n")
    
    temp_product = {
        "Title": "N/A",
        "Niche": "N/A",
        "BSR": "N/A",
        "Sales": "N/A",
        "ASIN": "N/A",
        "Brand": "N/A",
        "Added Date": "N/A",
        "Date Since": "N/A"
    }

    for i, line in enumerate(lines):
        line = line.strip()

        # ✅ XÁC ĐỊNH TITLE (KHÔNG CHỨA DỮ LIỆU CỦA CHỈ SỐ KHÁC)
        if len(line.split()) >= 4 and temp_product["Title"] == "N/A":
            if not any(keyword in line.lower() for keyword in ["estimated sales:", "rank (bsr):", "asin:", "brand:", "added:"]):
                temp_product["Title"] = line
                temp_product["Niche"] = get_niche_from_title(line)
        
        # ✅ XÁC ĐỊNH BSR (LUÔN Ở DƯỚI TITLE)
        if "Rank (BSR):" in line and i + 2 < len(lines) and "#" in lines[i + 1]:
            bsr_match = re.search(r'(\d[\d,]*)', lines[i + 2])
            if bsr_match:
                temp_product["BSR"] = bsr_match.group(1)

        # ✅ XÁC ĐỊNH SALES (LUÔN Ở DƯỚI RANK)
        if "Estimated Sales:" in line and temp_product["BSR"] != "N/A":
            sales_match = re.search(r'Estimated Sales:\s*([\d,]+)', line)
            if sales_match:
                temp_product["Sales"] = sales_match.group(1)

        # ✅ XÁC ĐỊNH ASIN (LUÔN Ở DƯỚI SALES)
        if "ASIN:" in line and temp_product["Sales"] != "N/A":
            asin_match = re.search(r'ASIN:\s*([A-Z0-9]{10})', line)
            if asin_match:
                temp_product["ASIN"] = asin_match.group(1)

        # ✅ XÁC ĐỊNH BRAND (LUÔN Ở DƯỚI ASIN)
        if "Brand:" in line and temp_product["ASIN"] != "N/A":
            temp_product["Brand"] = line.replace("Brand:", "").strip()

        # ✅ XÁC ĐỊNH ADDED DATE (LUÔN Ở DƯỚI BRAND)
        if "Added:" in line and temp_product["Brand"] != "N/A":
            added_date_match = re.search(r'Added:\s*([A-Za-z]+ \d{1,2}, \d{4})', line)
            if added_date_match:
                added_date = added_date_match.group(1)
                temp_product["Added Date"] = added_date
                added_date_dt = datetime.strptime(added_date, '%B %d, %Y')
                temp_product["Date Since"] = (today - added_date_dt).days

        # ✅ GOM NHÓM SẢN PHẨM KHI CÓ ĐỦ THÔNG SỐ
        if all(value != "N/A" for value in temp_product.values()):
            products.append(temp_product.copy())
            temp_product = {key: "N/A" for key in temp_product}

    # ✅ Lọc dữ liệu:
    filtered_products = [
        p for p in products
        if p["Date Since"] != "N/A" and int(p["Date Since"]) <= 4 and p["BSR"] != "N/A"
    ]

    # ✅ Sắp xếp theo Rank (BSR) từ cao xuống thấp
    sorted_products = sorted(
        filtered_products,
        key=lambda x: int(x['BSR'].replace(',', '')) if x['BSR'] != "N/A" else 9999999
    )[:20]

    while len(sorted_products) < 10:
        sorted_products.append({
            "Title": "Ko tìm thấy",
            "Niche": "Ko tìm thấy",
            "BSR": "Ko tìm thấy",
            "Sales": "Ko tìm thấy",
            "ASIN": "Ko tìm thấy",
            "Brand": "Ko tìm thấy",
            "Added Date": "Ko tìm thấy",
            "Date Since": "Ko tìm thấy"
        })

    print("\n✅ Kết quả sản phẩm đã phân tích (TOP 20):\n", sorted_products)

    return sorted_products


@amazontrend_app.post("/analyze/")
def analyze_amazon_data(data: ProductData):
    try:
        result = extract_product_info(data.raw_text)
        if not result:
            return {"error": "Không tìm thấy sản phẩm hợp lệ!"}
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
