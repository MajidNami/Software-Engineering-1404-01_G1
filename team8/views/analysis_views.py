import os, requests, json
from django.shortcuts import render
from django.http import JsonResponse
from groq import Groq
from ..models.ReadingMaterial import ReadingMaterial
from dotenv import load_dotenv
from django.contrib.auth.decorators import login_required

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@login_required 
def text_analysis_page(request):
    return render(request, 'team8/text_analysis.html')

@login_required
def api_get_history(request):
    # Filter by logged-in user
    readings = ReadingMaterial.objects.filter(user=request.user).order_by('-created_at')
    
    data = []
    for r in readings:
        data.append({
            "id": r.id,
            "title": r.title,
            "category": r.category,
            "date": r.created_at.strftime("%Y/%m/%d")
        })
    return JsonResponse({"history": data})

@login_required
def api_perform_analysis(request):
    mode = request.GET.get('mode', 'quick')
    
    # Selection logic
    if mode == 'quick':
        target_readings = ReadingMaterial.objects.filter(user=request.user).order_by('-created_at')[:5]
    else:
        selected_ids = request.GET.getlist('ids[]') 
        target_readings = ReadingMaterial.objects.filter(user=request.user, id__in=selected_ids)

    # Combine text for AI
    combined_text = " ".join([r.content for r in target_readings if r.content])

    # UPDATED PROMPT: Asks for the full list of words using the 'words' key
    prompt = f"""
    Analyze this text: "{combined_text[:3000]}" 
    Extract every difficult or academic vocabulary word and group them strictly by CEFR levels (A1, A2, B1, B2, C1, C2).
    For each level, return the count of words and the COMPLETE list of all extracted words.
    Return ONLY a JSON object like this:
    {{
    "results": [
        {{
            "level": "C1", 
            "count": 5, 
            "words": ["phenomenon", "scrutinize", "anomaly", "elusive", "curvature"]
        }},
        {{
            "level": "B2", 
            "count": 3, 
            "words": ["beckon", "nebulous", "expanse"]
        }}
    ]
    }}
    """

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        ai_response = json.loads(completion.choices[0].message.content)
        return JsonResponse(ai_response)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)