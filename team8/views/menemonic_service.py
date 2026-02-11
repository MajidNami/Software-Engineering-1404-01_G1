import os, requests, json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from groq import Groq
from ..models.word import Word
from ..models.menemonic import WordStory
from dotenv import load_dotenv

load_dotenv()
story_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
image_client = None  # TODO: Replace with your image generation client (e.g., OpenAI, Stability, etc.)


def text_analysis_page(request):
    return render(request, 'team8/menemonic_page.html')

def generate_story(request):
    """
    Expects JSON body:
    {
        "word_id": 1
    }
    """
    try:
        data = json.loads(request.body)
        word_id = data.get("word_id")

        if not word_id:
            return JsonResponse({"error": "word_id is required"}, status=400)

        word = Word.objects.get(id=word_id)

        prompt = f"""
        Write a vivid 2–3 paragraph contextual story to help memorize the word: "{word.word}".
        The story must clearly demonstrate the meaning of the word in context.
        Keep it engaging and easy to remember.
        """

        completion = story_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192"
        )

        story_text = completion.choices[0].message.content.strip()

        word_story = WordStory.objects.create(
            word=word,
            story=story_text
        )

        return JsonResponse({
            "word": word.word,
            "story": story_text
        })

    except Word.DoesNotExist:
        return JsonResponse({"error": "Word not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def generate_image(request):
    """
    Expects JSON body:
    {
        "word_story_id": 1
    }
    """
    try:
        data = json.loads(request.body)
        word_story_id = data.get("word_story_id")

        if not word_story_id:
            return JsonResponse({"error": "word_story_id is required"}, status=400)

        word_story = WordStory.objects.get(id=word_story_id)

        prompt = f"Create a memorable illustrative image representing the word '{word_story.word.word}'."

        # ----------------------------
        # Replace this block with your real image generation API
        # ----------------------------
        # Example placeholder logic
        image_url = "https://via.placeholder.com/512x512.png?text=" + word_story.word.word

        # Download and save image locally
        response = requests.get(image_url)
        if response.status_code == 200:
            file_name = f"{word_story.word.word}_{word_story.id}.png"
            file_path = os.path.join("media/word_stories/", file_name)

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(response.content)

            word_story.image = f"word_stories/{file_name}"
            word_story.save()

            return JsonResponse({
                "message": "Image generated successfully",
                "image_url": word_story.image.url
            })
        else:
            return JsonResponse({"error": "Failed to download image"}, status=500)

    except WordStory.DoesNotExist:
        return JsonResponse({"error": "WordStory not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
