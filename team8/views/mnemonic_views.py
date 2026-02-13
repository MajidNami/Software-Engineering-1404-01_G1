# team8/views/mnemonic_views.py

import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from ..ai_utils import AIService

# Optional: import models – if they don't exist yet, code will skip DB gracefully
try:
    from ..models import Word, Mnemonic
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    Word = None
    Mnemonic = None


@require_GET
@csrf_exempt
def get_mnemonic(request):
    """
    API endpoint that returns word info, mnemonic, story, and generated image.
    Expects: ?word=ephemeral
    """
    # ------------------------------------------------------------
    # 1. Get word from query parameter
    # ------------------------------------------------------------
    word_param = request.GET.get('word')
    if not word_param:
        return JsonResponse({"error": "Missing 'word' parameter"}, status=400)
    
    word_param = word_param.lower().strip()
    print(f"🔵 Generating mnemonic for: {word_param}")

    # ------------------------------------------------------------
    # 2. Check database cache (if models are available)
    # ------------------------------------------------------------
    if MODELS_AVAILABLE:
        try:
            word_obj = Word.objects.filter(text=word_param).first()
            if word_obj:
                mnemonic = Mnemonic.objects.filter(word=word_obj).first()
                if mnemonic and mnemonic.mnemonic_text and mnemonic.image_url:
                    print("🟢 Found cached mnemonic – returning instantly")
                    return JsonResponse({
                        "word": word_obj.text,
                        "level": getattr(word_obj, 'level', 'B2'),
                        "definition": getattr(word_obj, 'definition', ''),
                        "phonetic": getattr(word_obj, 'ipa', ''),
                        "image_url": mnemonic.image_url,
                        "mnemonic_text": mnemonic.mnemonic_text,
                        "story_text": mnemonic.story_text,
                    })
        except Exception as e:
            print(f"⚠️ DB cache lookup failed (proceeding with AI): {e}")

    # ------------------------------------------------------------
    # 3. Generate new content using AI
    # ------------------------------------------------------------
    try:
        ai = AIService()

        # 3a. Fetch basic word information (definition, IPA, etc.)
        word_info_raw = ai.fetch_word_info(word=word_param, level="B2")
        word_info = json.loads(word_info_raw)

        # 3b. Generate mnemonic and story
        mnemonic_data = ai.generate_mnemonic_story(word_param)

        # 3c. Generate an image (Pollinations.ai – no key needed)
        image_prompt = f"{word_param}, {mnemonic_data.get('mnemonic_text', '')}, digital art style"
        image_url = ai.generate_image_hf(image_prompt)
        print("🟣 Image URL received:", image_url)

        # 3d. Build the response
        response_data = {
            "word": word_info.get("word", word_param),
            "level": "B2",
            "definition": word_info.get("definition", ""),
            "phonetic": word_info.get("ipa", "/?/"),
            "image_url": image_url,
            "mnemonic_text": mnemonic_data.get("mnemonic_text", ""),
            "story_text": mnemonic_data.get("story_text", ""),
        }

        # ------------------------------------------------------------
        # 4. Save to database for future caching (if models exist)
        # ------------------------------------------------------------
        if MODELS_AVAILABLE:
            try:
                word_obj, _ = Word.objects.get_or_create(
                    text=word_param,
                    defaults={
                        'definition': word_info.get('definition', ''),
                        'ipa': word_info.get('ipa', ''),
                        'level': 'B2',
                    }
                )
                Mnemonic.objects.create(
                    word=word_obj,
                    mnemonic_text=mnemonic_data.get('mnemonic_text', ''),
                    story_text=mnemonic_data.get('story_text', ''),
                    image_url=image_url,
                    image_prompt=image_prompt,
                    ai_service='pollinations'
                )
                print("💾 Saved to database")
            except Exception as e:
                print(f"⚠️ Failed to save to DB: {e}")

        print("📦 Final response data:", response_data)
        return JsonResponse(response_data)

    except Exception as e:
        print(f"❌ Error in get_mnemonic: {e}")
        return JsonResponse({"error": str(e)}, status=500)