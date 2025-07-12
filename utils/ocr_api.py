import os
import json
import requests
from kivy.storage.jsonstore import JsonStore
from kivy.logger import Logger
from utils.feature_flags import OCR_ENABLED

def get_api_key():
    try:
        store_path = os.path.join("app_data", "config.json")
        if os.path.exists(store_path):
            store = JsonStore(store_path)
            if store.exists("ocr_key"):
                return store.get("ocr_key")["value"]
    except Exception as e:
        Logger.error(f"Error getting OCR API key: {str(e)}")
    return None

def process_image_ocr(image_path):
    """
    Process an image through OCR.space API and return the extracted text.
    
    Args:
        image_path: Local path to the image file
        
    Returns:
        Extracted text or None if an error occurred
    """
    api_key = get_api_key()
    if not api_key:
        Logger.error("OCR API key not found. Please set it in Admin Settings.")
        return None
    
    try:
        Logger.info(f"OCR: Processing image: {image_path}")
        url = "https://api.ocr.space/parse/image"
        
        with open(image_path, 'rb') as image_file:
            files = {'file': image_file}
            payload = {
                "apikey": api_key,
                "language": "eng",
                "isTable": True,
                "detectOrientation": True,
                "scale": True,
                "OCREngine": 2
            }
            
            Logger.info("OCR: Sending request to OCR.space API")
            response = requests.post(url, files=files, data=payload)
            
            if response.status_code != 200:
                Logger.error(f"OCR: API request failed with status code {response.status_code}")
                return None
                
            result = response.json()
            
            if result.get("IsErroredOnProcessing", False):
                error_message = result.get("ErrorMessage", ["Unknown error"])[0]
                Logger.error(f"OCR: Processing error: {error_message}")
                return None
                
            if result.get("ParsedResults"):
                extracted_text = result["ParsedResults"][0].get("ParsedText", "")
                Logger.info(f"OCR: Successfully extracted {len(extracted_text)} characters")
                return extracted_text
            
            Logger.error(f"OCR: No parsed results found in the response")
            return None
            
    except Exception as e:
        Logger.error(f"OCR: Error processing image: {str(e)}")
        return None

def extract_menu_from_image(image_path):
    """
    Extract menu data from an image and convert it to CSV format.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        CSV-formatted string or None if extraction failed
    """
    extracted_text = process_image_ocr(image_path)
    if not extracted_text:
        return None
        
    try:
        lines = extracted_text.strip().split('\n')
        processed_lines = []
        
        if not "item" in lines[0].lower() and not "ingredients" in lines[0].lower():
            processed_lines.append("item,ingredients")
            
        for line in lines:
            if not line.strip():
                continue
                
            if '-' in line:
                parts = line.split('-', 1)
                if len(parts) == 2:
                    item = parts[0].strip()
                    ingredients = parts[1].strip()
                    processed_lines.append(f'"{item}","{ingredients}"')
            elif ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    item = parts[0].strip()
                    ingredients = parts[1].strip()
                    processed_lines.append(f'"{item}","{ingredients}"')
            else:
                processed_lines.append(f'"{line.strip()}",""')
                
        return '\n'.join(processed_lines), print(f"OCR: Successfully converted extracted text to CSV: {processed_lines}")
    except Exception as e:
        Logger.error(f"OCR: Error converting extracted text to CSV: {str(e)}")
        return None

if not OCR_ENABLED:
    def extract_menu_from_image(image_path):
        """Stub implementation used when OCR is disabled."""
        Logger.warning("OCR feature flag is disabled. 'extract_menu_from_image' will return None.")
        return None