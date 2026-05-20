import re
import json
from typing import Dict, Any

def extract_with_rules(text: str, filename: str) -> Dict[str, Any]:
    """Rule-based extraction — ძალიან ზუსტი მსგავსი ინვოისებისთვის"""
    data = {"filename": filename}

    # ინვოისის ნომერი
    if match := re.search(r'2026\s*-\s*(\d+)', text):
        data['invoice_no'] = f"2026-{match.group(1)}"
    elif match := re.search(r'Invoice No[:\s]*([A-Za-z0-9-]+)', text, re.I):
        data['invoice_no'] = match.group(1)

    # თარიღი
    if match := re.search(r'(\d{2}\.\d{2}\.\d{4})', text):
        data['date'] = match.group(1)

    # კომპანიები
    if "ANABEL LOGISTICS" in text.upper():
        data['seller_name'] = "LTD ANABEL LOGISTICS"
        data['seller_id'] = "415106450"

    # სრული თანხა
    if match := re.search(r'TOTAL.*?USD\s*(\d+)', text, re.I):
        data['total_amount'] = float(match.group(1))
        data['currency'] = "USD"

    # წონა
    if match := re.search(r'(\d{3,5})\s*KG', text, re.I):
        data['weight_kg'] = float(match.group(1))

    return data


def extract_data(odl_result: Any, filename: str, selected_keys: list) -> Dict:
    """მთავარი extraction ფუნქცია"""
    try:
        # OpenDataLoader-ის JSON-დან ტექსტის ამოღება
        if isinstance(odl_result, dict) and 'markdown' in odl_result:
            text = odl_result['markdown']
        else:
            text = str(odl_result)

        data = extract_with_rules(text, filename)

        # ყველა მოთხოვნილი ველი დავამატოთ (თუ არ არის — ცარიელი)
        for key in selected_keys:
            if key not in data:
                data[key] = None

        return data

    except Exception as e:
        return {"filename": filename, "error": str(e)}
