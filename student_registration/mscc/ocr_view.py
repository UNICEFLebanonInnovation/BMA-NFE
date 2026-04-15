import re
import logging
from PIL import Image
from PIL import UnidentifiedImageError
import pytesseract
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


def extract_field(regex, text):
    match = re.search(regex, text)
    if match:
        return match.group(1).strip()
    return None


@csrf_exempt
def process_ocr(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    document = request.FILES.get('document')
    if not document:
        return JsonResponse({'success': False, 'error': 'No document provided'}, status=400)

    try:
        image = Image.open(document)
        image.load()

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
    except UnidentifiedImageError:
        return JsonResponse(
            {'success': False, 'error': 'Unsupported document format. Please upload an image file.'},
            status=400
        )
    except pytesseract.TesseractNotFoundError:
        logger.exception('OCR processing failed because the Tesseract binary is not installed or not on PATH.')
        return JsonResponse(
            {
                'success': False,
                'error': 'OCR engine is not configured on the server. Please contact support.'
            },
            status=503
        )
    except pytesseract.TesseractError:
        logger.exception('OCR processing failed due to a Tesseract runtime error.')
        return JsonResponse(
            {'success': False, 'error': 'OCR service is currently unavailable. Please try again later.'},
            status=503
        )
    except Exception:
        logger.exception('Unexpected error while processing OCR document.')
        return JsonResponse({'success': False, 'error': 'Unexpected OCR processing error.'}, status=500)
