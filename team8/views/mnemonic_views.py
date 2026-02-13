import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from ..ai_utils import AIService

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
    """API endpoint that returns mnemonic, story, and image for a given word."""
    word_param = request.GET.get('word')
    if not word_param:
        return JsonResponse({"error": "Missing 'word' parameter"}, status=400)
    
    word_param = word_param.lower().strip()
    force = request.GET.get('force') == 'true'

    # ----- 1. Check cache -----
    if MODELS_AVAILABLE and not force:
        try:
            word_obj = Word.objects.filter(text=word_param).first()
            if word_obj:
                mnemonic = Mnemonic.objects.filter(word=word_obj).first()
                if mnemonic and mnemonic.mnemonic_text and mnemonic.image_url:
                    return JsonResponse({
                        "word": word_obj.text,
                        "level": getattr(word_obj, 'level', 'B2'),
                        "definition": getattr(word_obj, 'definition', ''),
                        "phonetic": getattr(word_obj, 'ipa', ''),
                        "image_url": mnemonic.image_url,
                        "mnemonic_text": mnemonic.mnemonic_text,
                        "story_text": mnemonic.story_text,
                    })
        except Exception:
            pass # Continue to generation if cache fails

    # ----- 2. Generate new content using AI -----
    try:
        ai = AIService()

        # Fetch word info
        word_info_raw = ai.fetch_word_info(word=word_param)
        word_info = json.loads(word_info_raw)

        # Generate mnemonic and story
        mnemonic_data = ai.generate_mnemonic_story(word_param)

        # Extract prompt from AI response or fallback
        raw_prompt = mnemonic_data.get('image_prompt', '')
        if not raw_prompt:
             # Fallback if AI didn't give a specific 'image_prompt' key
             raw_prompt = ai.extract_image_prompt(mnemonic_data.get('mnemonic_text', ''), word_param)

        # Generate Image (Using the fixed function)
        image_url = ai.generate_image(prompt=raw_prompt, word=word_param)

        # ----- 3. Save to database -----
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
                Mnemonic.objects.update_or_create(
                    word=word_obj,
                    defaults={
                        'mnemonic_text': mnemonic_data.get('mnemonic_text', ''),
                        'story_text': mnemonic_data.get('story_text', ''),
                        'image_url': image_url,
                        'image_prompt': raw_prompt,
                        'ai_service': 'pollinations_flux'
                    }
                )
            except Exception as e:
                print(f"⚠️ DB Save failed: {e}")

        # ----- 4. Build response -----
        response_data = {
            "word": word_info.get("word", word_param),
            "level": "B2",
            "definition": word_info.get("definition", ""),
            "phonetic": word_info.get("ipa", "/?/"),
            "image_url": image_url,
            "mnemonic_text": mnemonic_data.get("mnemonic_text", ""),
            "story_text": mnemonic_data.get("story_text", ""),
        }
        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)