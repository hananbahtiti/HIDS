from django.shortcuts import render
import requests
from django.http import JsonResponse

# Create your views here.


from django.shortcuts import render
from results.models import IntrusionResult  # تأكد من الاستيراد الصحيح للـ model

def protocol_report_view(request):
    # جلب آخر 50 نتيجة (مثلاً)
    result_data = IntrusionResult.objects.order_by('-timestamp')[:50]

    # تجهيز البيانات لعرضها في القالب
    network_data = [
        {
            'protocol': result.proto,
            'src': result.src,
            'status': result.result,
            'timestamp': result.timestamp
        }
        for result in result_data
    ]

    return render(request, 'attacked_protocols.html', {'network_data': network_data})