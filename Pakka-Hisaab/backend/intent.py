"""Explainable multilingual intent parsing; no state mutation happens here."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


NUMBER_WORDS = {
    "one": 1, "first": 1, "1st": 1, "ek": 1, "एक": 1, "वन": 1, "पहला": 1, "पहले": 1,
    "two": 2, "second": 2, "2nd": 2, "do": 2, "दो": 2, "टू": 2, "दूसरा": 2,
    "three": 3, "third": 3, "3rd": 3, "teen": 3, "तीन": 3, "थ्री": 3, "तीसरा": 3,
    "four": 4, "fourth": 4, "4th": 4, "char": 4, "चार": 4, "फोर": 4, "चौथा": 4,
    "five": 5, "fifth": 5, "5th": 5, "paanch": 5, "पांच": 5,
}


@dataclass(frozen=True)
class Intent:
    intent: str
    cart_id: int | None = None
    payment_method: str | None = None
    language: str | None = None
    product_query: str | None = None
    confidence: float = 0.0

    def as_dict(self) -> dict:
        return {"intent": self.intent, "cart_id": self.cart_id, "payment_method": self.payment_method, "language": self.language, "product_query": self.product_query, "confidence": self.confidence}


def _clean(text: str) -> str:
    # Keep combining marks used by Devanagari and Tamil; \w alone drops vowel signs.
    return re.sub(r"[^\w\s₹\-\u0900-\u097F\u0B80-\u0BFF]", " ", unicodedata.normalize("NFKC", text or "").lower().strip(), flags=re.UNICODE)


def _find_cart_id(text: str) -> int | None:
    numeric = re.search(r"(?:\bcart|कार्ट|कार्ड|கார்ட்)\s*(?:number|नंबर)?\s*(\d+)\b", text)
    if numeric:
        return int(numeric.group(1))
    for word, value in NUMBER_WORDS.items():
        token = re.escape(word)
        if re.search(rf"(?:\b{token}\s+(?:cart|customer|bill|order)\b|\b(?:cart)\s+{token}\b)", text) or re.search(rf"{token}\s*(?:कार्ट|कार्ड|ग्राहक|बिल|ऑर्डर)", text) or re.search(rf"(?:कार्ट|कार्ड)\s*{token}", text):
            return value
    return None


def _payment_method(text: str) -> str:
    if re.search(r"(?:\bupi\b|यूपीआई|यू\s*पी\s*आई)", text):
        return "upi"
    if re.search(r"(?:\bcash\b|कैश|नकद|रोकड़|ரொக்கம்)", text):
        return "cash"
    if re.search(r"\bcard\b", text):
        return "card"
    return "upi"


def parse_command(raw_text: str) -> Intent:
    text = _clean(raw_text)
    if not text:
        return Intent("unsupported")

    language_match = re.search(r"\b(?:switch|use|speak|set)\s+(?:to\s+)?(english|hindi|tamil)\b", text)
    if language_match or re.search(r"\b(?:english|hindi|tamil)\s+(?:please|mode)\b", text):
        return Intent("switch_language", language=(language_match.group(1) if language_match else text.split()[0]).lower(), confidence=0.99)
    if re.search(r"\b(?:reset|restore)\b", text) and re.search(r"\b(?:demo|data|database)\b", text):
        return Intent("reset_demo", confidence=0.99)

    cart_id = _find_cart_id(text)
    payment_method = _payment_method(text)
    checkout_markers = r"(?:\bcheckout\b|\bcheck\s*out\b|\bclear\b|\bsettle\b|\bpay\b|\bpayment\b|\bbill\b|\bcustomer\b|क्लियर|भुगतान|पेमेंट|चुकता|निपटाओ|सेटल|बिल|கட்டணம்|செலுத்த|கிளியர்)"
    if re.search(checkout_markers, text) and (cart_id is not None or "cart" in text or "कार्ट" in text or "कार्ड" in text or "கார்ட்" in text):
        return Intent("checkout_cart", cart_id=cart_id, payment_method=payment_method, confidence=0.96)
    if re.search(r"(?:\bshow\b|\bview\b|\bopen\b|what\s+is\s+in|दिखाओ|खोलो)", text) and ("cart" in text or "कार्ट" in text):
        return Intent("view_cart", cart_id=cart_id, confidence=0.94)
    if re.search(r"(?:\bstock\b|\binventory\b|\bleft\b|\bavailable\b|how many|how much|स्टॉक|कितना)", text):
        product_query = next((candidate for candidate in ("britannia", "biscuits", "biscuit", "soap", "milk", "rice", "tea", "sugar", "bread", "shampoo", "toothpaste", "oil") if candidate in text), None)
        return Intent("inventory_query", product_query=product_query, confidence=0.9)
    return Intent("unsupported", cart_id=cart_id, confidence=0.2)
