import logging
from django.shortcuts import render
from django.conf import settings
from .models import IntrusionResult
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive
import requests
from django.http import JsonResponse
from .models import IntrusionResult
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
import os
import csv
import io
import json
from datetime import datetime
import shutil 
from .models import TrainingResult
from types import SimpleNamespace


logger = logging.getLogger(__name__)


def get_intrusion_data_from_db(request):
    results = IntrusionResult.objects.order_by('-timestamp')[:100]
    rows = [model_to_dict(result) for result in results]
    return JsonResponse({'rows': rows})

def fetch_intrusion_data_api(request):
    fastapi_url = 'https://f640-34-53-119-166.ngrok-free.app:8000/predict_all'
    print(f'fastapi_url: {fastapi_url}')

    try:
        response = requests.get(fastapi_url)
        print(f'response: {response}')

        if response.status_code == 200:
            try:
                data = response.json()
                results = data.get('results', [])

                rows = []
                for result in results:
                    for item in result:
                        row_index = item.get('row_index', -1)
                        attack_cat = item.get('attack_cat', 'N/A')
                        mse = item.get('mse', 0.0)
                        result_val = item.get('result', 'N/A')
                        ct_src_dport_ltm = item.get('ct_src_dport_ltm', 'N/A')
                        rate = item.get('rate', 'N/A')
                        dwin = item.get('dwin', 'N/A')
                        dload = item.get('dload', 'N/A')
                        swin = item.get('swin', 'N/A')
                        ct_dst_sport_ltm = item.get('ct_dst_sport_ltm', 'N/A')
                        ct_state_ttl = item.get('ct_state_ttl', 'N/A')
                        sttl = item.get('sttl', 'N/A')
                        timestamp_raw = item.get('timestamp', None)
                        src = item.get('src', None)
                        proto = item.get('proto', None)
                        state = item.get('state', None)

                        # التعامل مع timestamp
                        ts = parse_datetime(timestamp_raw) if timestamp_raw else None
                        if ts and is_naive(ts):
                            ts = make_aware(ts)

                        # إنشاء السجل

                        # تحقق من وجود السجل مسبقًا
                        exists = IntrusionResult.objects.filter(
                            row_index=row_index,
                            attack_cat=attack_cat,
                            mse=mse,
                            result=result_val,
                            ct_src_dport_ltm=ct_src_dport_ltm,
                            rate=rate,
                            dwin=dwin,
                            dload=dload,
                            swin=swin,
                            ct_dst_sport_ltm=ct_dst_sport_ltm,
                            ct_state_ttl=ct_state_ttl,
                            sttl=sttl,
                            timestamp=ts,
                            src=src,
                            proto=proto,
                            state=state,
                        ).exists()

                        # إذا لم يكن موجودًا أضفه
                        if not exists:
                            IntrusionResult.objects.create(
                                row_index=row_index,
                                attack_cat=attack_cat,
                                mse=mse,
                                result=result_val,
                                ct_src_dport_ltm=ct_src_dport_ltm,
                                rate=rate,
                                dwin=dwin,
                                dload=dload,
                                swin=swin,
                                ct_dst_sport_ltm=ct_dst_sport_ltm,
                                ct_state_ttl=ct_state_ttl,
                                sttl=sttl,
                                timestamp=ts,
                                src=src,
                                proto=proto,
                                state=state,
                            )

                        
                        

                        rows.append({
                            'row_index': row_index,
                            'attack_cat': attack_cat,
                            'mse': mse,
                            'result': result_val,
                            'ct_src_dport_ltm': ct_src_dport_ltm,
                            'rate': rate,
                            'dwin': dwin,
                            'dload': dload,
                            'swin': swin,
                            'ct_dst_sport_ltm': ct_dst_sport_ltm,
                            'ct_state_ttl': ct_state_ttl,
                            'sttl': sttl,
                            'timestamp': timestamp_raw,
                            'src':src,
                            'proto':proto,
                            'state':state,
                        })

                return JsonResponse({'rows': rows})

            except ValueError as e:
                logger.error(f"JSON decode error: {e}")
                return JsonResponse({'error': 'Invalid JSON from FastAPI'}, status=500)
        else:
            return JsonResponse({'error': 'Failed to fetch data from FastAPI'}, status=502)

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return JsonResponse({'error': str(e)}, status=503)




# HTML View: Renders data in template
def fetch_intrusion_data_page(request):
    rows = IntrusionResult.objects.order_by('-timestamp')[:100]
    return render(request, 'predict_result.html', {'rows': rows})







@csrf_exempt
def save_csv(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        data = body.get("data", [])

        if not data:
            return JsonResponse({"status": "failed", "reason": "No data provided"})

        export_dir = os.path.join(settings.MEDIA_ROOT, "exports")
        os.makedirs(export_dir, exist_ok=True)

        filename = f"intrusion_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = os.path.join(export_dir, filename)

        with open(file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        fastapi_url = "http://127.0.0.1:8000/train"

        try:
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f, 'text/csv')}
                response = requests.post(fastapi_url, files=files)
                print(f'response: {response}')

            if response.status_code == 200:
                result = response.json()
                print(f'result: {result}')

                # 🔴 استخراج القيم من نتيجة FastAPI
                message = result.get("message")
                rows = result.get("rows")
                auc = result.get("auc")
                f1 = result.get("f1")
                report = result.get("report")
                images = result.get("images", {})
                confusion_matrix = images.get("confusion_matrix")
                training_loss = images.get("training_loss")
                error_distribution = images.get("error_distribution")
                csv_result = result.get("csv_result")

                # 🟢 حفظ النتائج في قاعدة البيانات
                TrainingResult.objects.create(
                    message=message,
                    rows=rows,
                    auc=auc,
                    f1=f1,
                    report=report,
                    confusion_matrix=confusion_matrix,
                    training_loss=training_loss,
                    error_distribution=error_distribution,
                    csv_result=csv_result
                )
                all_results = TrainingResult.objects.all().order_by('-timestamp')  # الأحدث أولاً


                # 🟢 تحميل محتوى ملف CSV الناتج من FastAPI
                csv_result_url = "http://127.0.0.1:8000" + csv_result
                csv_response = requests.get(csv_result_url)

                if csv_response.status_code == 200:
                    csv_lines = csv_response.content.decode('utf-8').splitlines()
                    reader = csv.DictReader(csv_lines)
                    csv_table_data = list(reader)
                else:
                    csv_table_data = []

                return render(request, 'predict_result.html', {
                    'message': message,
                    'rows': rows,
                    'auc': auc,
                    'f1': f1,
                    'report': report,
                    'confusion_matrix': confusion_matrix,
                    'training_loss': training_loss,
                    'error_distribution': error_distribution,
                    'csv_result': csv_result,
                    'csv_result_link': csv_result_url,
                    'csv_table_data': csv_table_data ,
                    'all_results': all_results,
                })
            else:
                return JsonResponse({
                    "status": "partial_success",
                    "message": "CSV saved but failed to send to FastAPI",
                    "fastapi_response": response.text
                })

        except Exception as e:
            return JsonResponse({
                "status": "partial_success",
                "message": "CSV saved but error sending to FastAPI",
                "error": str(e)
            })

    return JsonResponse({"status": "failed", "reason": "Invalid method"})











def training_results_view(request):
    #results = TrainingResult.objects.all().order_by('-timestamp')
    results = TrainingResult.objects.last()
    print(f'results: {results}')
    csv_data = []
    columns = [
        'ct_src_dport_ltm', 'rate', 'dwin', 'dload', 'swin',
        'ct_dst_sport_ltm', 'state', 'ct_state_ttl', 'sttl',
        'label', 'reconstruction_error', 'predicted'
    ]

    if results and results.csv_result:
        # إزالة "/static/" من البداية للحصول على المسار النسبي للملف
        relative_path = results.csv_result.replace("/static/", "")
        csv_path = os.path.join(settings.BASE_DIR, 'static', *relative_path.split('/'))


        try:
            with open(csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    filtered_row = {col: row.get(col, '') for col in columns}
                    csv_data.append(SimpleNamespace(**filtered_row)) 
                print(f'csv_data: {csv_data}')
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")

    return render(request, 'training_results.html', {
        'results': results,
        'csv_data': csv_data,
        'columns': columns,
    })
    #return render(request, 'training_results.html', {'results': results})

