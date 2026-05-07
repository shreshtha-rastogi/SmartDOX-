# services/translator.py
from deep_translator import GoogleTranslator

def translate_text(text, target_lang='hi'):
    if target_lang == 'en':
        return text
    try:
        # 'hi' for Hindi, 'mr' for Marathi, etc.
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated
    except Exception as e:
        return text # Translation fail ho toh original wapis bhej do