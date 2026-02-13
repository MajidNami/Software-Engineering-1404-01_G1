import os
import hashlib
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from gtts import gTTS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_CACHE_DIR = os.path.join(BASE_DIR, 'static', 'team8', 'audio')
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

@require_GET
@csrf_exempt
def generate_speech(request):
    text = request.GET.get('text')
    lang = request.GET.get('lang', 'en')
    if not text:
        return JsonResponse({"error": "Missing 'text'"}, status=400)

    filename = hashlib.md5(f"{text}_{lang}".encode()).hexdigest() + ".mp3"
    filepath = os.path.join(AUDIO_CACHE_DIR, filename)
    audio_url = f"/static/team8/audio/{filename}"

    # 1. Return cached file if exists and not empty
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        return JsonResponse({"audio_url": audio_url, "cached": True})

    # 2. Try gTTS first
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filepath)
        if os.path.getsize(filepath) > 0:
            return JsonResponse({"audio_url": audio_url, "cached": False})
        else:
            raise Exception("gTTS saved empty file")
    except Exception as e:
        print(f"gTTS failed: {e}")

    # 3. Fallback: VoiceRSS (free, no key, but more reliable)
    try:
        fallback_url = "https://api.voicerss.org/"
        params = {
            "key": "c5d63d3a9f004c0cb80ec62d4aeaa9d9",  # public demo key
            "hl": "en-us",
            "src": text,
            "c": "MP3",
            "f": "44khz_16bit_stereo"
        }
        response = requests.get(fallback_url, params=params, timeout=10)
        if response.status_code == 200 and len(response.content) > 1000:
            with open(filepath, "wb") as f:
                f.write(response.content)
            return JsonResponse({"audio_url": audio_url, "cached": False})
        else:
            raise Exception("VoiceRSS returned invalid data")
    except Exception as e2:
        print(f"VoiceRSS fallback also failed: {e2}")

    # 4. Ultimate fallback – return error, frontend will show 🔇
    return JsonResponse({"error": "TTS unavailable"}, status=503)