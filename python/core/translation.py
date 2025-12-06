from deep_translator import GoogleTranslator

def translate_to_french(text: str) -> str:
    if not text:
        return ""
    return GoogleTranslator(source="auto", target="fr").translate(text)

def translate_to_english(text: str) -> str:
    if not text:
        return ""
    original = text.strip()
    auto = GoogleTranslator(source="auto", target="en").translate(original)
    auto_stripped = auto.strip() if auto else ""

    if auto_stripped and auto_stripped.lower() != original.lower():
        return auto_stripped

    try:
        forced = GoogleTranslator(source="fr", target="en").translate(original)
        forced_stripped = forced.strip() if forced else ""
        if forced_stripped:
            return forced_stripped
    except Exception:
        pass

    return auto_stripped or original
