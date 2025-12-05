from transformers import MarianMTModel, MarianTokenizer

tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-fr")
model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-fr")

def translate_to_french(text: str) -> str:
    if not text:
        return ""
    batch = tokenizer([text], return_tensors="pt", truncation=True, max_length=512)
    gen = model.generate(**batch)
    return tokenizer.decode(gen[0], skip_special_tokens=True)
