from deep_translator import GoogleTranslator

def translate_to_french(text: str) -> str:
    if not text:
        return ""
    return GoogleTranslator(source="auto", target="fr").translate(text)

def translate_to_english(text: str) -> str:
    if not text:
        return ""
    return GoogleTranslator(source="auto", target="en").translate(text)
