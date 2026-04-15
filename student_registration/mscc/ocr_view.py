import re
from PIL import Image
import pytesseract
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def extract_field(regex, text):
    match = re.search(regex, text)
    if match:
        return match.group(1).strip()
    return None

@csrf_exempt
def process_ocr(request):
    if request.method == 'POST' and request.FILES.get('document'):
        document = request.FILES['document']
        try:
            image = Image.open(document)
            
            # Use Arabic and English models
            text = pytesseract.image_to_string(image, lang='eng+ara')
            
            data = {}
            
            # Basic regex patterns for common fields (English)
            data['first_name'] = extract_field(r'(?i)First\s*Name\s*[:\-]?\s*([A-Za-z]+)', text)
            data['last_name'] = extract_field(r'(?i)(?:Last|Family|Surname)\s*Name\s*[:\-]?\s*([A-Za-z]+)', text)
            data['father_name'] = extract_field(r'(?i)Father[\'s]*\s*Name\s*[:\-]?\s*([A-Za-z]+)', text)
            data['mother_fullname'] = extract_field(r'(?i)Mother[\'s]*\s*Name\s*[:\-]?\s*([A-Za-z\s]+?)(?=\n|Date|Sex|DOB|$)', text)
            data['dob'] = extract_field(r'(?i)(?:Date\s*of\s*Birth|DOB)\s*[:\-]?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4})', text)
            data['nationality'] = extract_field(r'(?i)Nationality\s*[:\-]?\s*([A-Za-z]+)', text)

            # Arabic fallbacks
            if not data['first_name']:
                 data['first_name'] = extract_field(r'(?u)الاسم[:\-]?\s*([^\n\r]+)', text)
            if not data['last_name']:
                 data['last_name'] = extract_field(r'(?u)الشهرة[:\-]?\s*([^\n\r]+)', text)
            if not data['father_name']:
                 data['father_name'] = extract_field(r'(?u)اسم الأب[:\-]?\s*([^\n\r]+)', text)
            if not data['mother_fullname']:
                 data['mother_fullname'] = extract_field(r'(?u)اسم الأم[:\-]?\s*([^\n\r]+)', text)
            if not data['dob']:
                 data['dob'] = extract_field(r'(?u)تاريخ الولادة[:\-]?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4})', text)
            if not data['nationality']:
                 data['nationality'] = extract_field(r'(?u)الجنسية[:\-]?\s*([^\n\r]+)', text)
                 
            # filter out Nones
            data = {k: v for k, v in data.items() if v}
                
            return JsonResponse({'success': True, 'data': data, 'raw_text': text})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'No document provided'}, status=400)
