from results.models import IntrusionResult
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import BlockedIP
from django.shortcuts import render

from django.db.models import Q


def ip_report_view(request):
    # 1. المحظور يدويًا
    manually_blocked = BlockedIP.objects.all().values('ip_address', 'attack_type', 'status')

    # 2. المحظور من النموذج
    model_blocked = IntrusionResult.objects.exclude(result__iexact='NORMAL') \
                                           .exclude(src__isnull=True).exclude(src='N/A') \
                                           .values('src', 'attack_cat').distinct()

    # 3. كل الـ IPs في الشبكة (من قاعدة البيانات)
    all_ips_qs = IntrusionResult.objects.exclude(src__isnull=True).exclude(src='N/A') \
                                        .values_list('src', flat=True).distinct()
    all_ips = set(str(ip) for ip in all_ips_qs)

    # 4. دمج IPs المحظورة في مجموعة واحدة لتسهيل التحقق
    blocked_ip_set = set(ip['ip_address'] for ip in manually_blocked)
    blocked_ip_set.update(ip['src'] for ip in model_blocked)

    # 5. إنشاء قائمة المحظورين
    blocked_ips = []
    for ip in manually_blocked:
        blocked_ips.append({
            'ip_address': ip['ip_address'],
            'attack_type': ip['attack_type'],
            'status': ip['status']
        })
    for ip in model_blocked:
        blocked_ips.append({
            'ip_address': ip['src'],
            'attack_type': ip['attack_cat'],
            'status': 'Detected'
        })

    # 6. الـ IPs غير المحظورة (الطبيعية)
    normal_ips = [ip for ip in all_ips if ip not in blocked_ip_set]

    context = {
        'blocked_ips': blocked_ips,
        'normal_ips': normal_ips,
        'all_ips': sorted(all_ips),  # كل IPs في الشبكة
    }
    return render(request, 'blocked_ips.html', context)

"""
def ip_report_view(request):
    # IPs المحظورة يدويًا
    manually_blocked = BlockedIP.objects.all().values('ip_address', 'attack_type', 'status')

    # IPs المكتشفة كهجوم من النموذج
    model_blocked = IntrusionResult.objects.exclude(result__iexact='NORMAL') \
                                           .exclude(src__isnull=True).exclude(src='N/A') \
                                           .values('src', 'attack_cat') \
                                           .distinct()

    # كل الـ IPs من IntrusionResult التي حالتها طبيعية
    normal_ips_qs = IntrusionResult.objects.filter(result__iexact='NORMAL') \
                                           .exclude(src__isnull=True).exclude(src='N/A') \
                                           .values_list('src', flat=True).distinct()

    # بناء قائمة IPs محظورة فعليًا حتى لا نظهرها في normal_ips
    blocked_ip_set = set(ip['ip_address'] for ip in manually_blocked)
    blocked_ip_set.update(ip['src'] for ip in model_blocked)

    # حذف الـ IPs المحظورة من القائمة النهائية
    normal_ips = [ip for ip in normal_ips_qs if ip not in blocked_ip_set]

    # دمج المحظورين (يدوي + من النموذج)
    blocked_ips = []

    for ip in manually_blocked:
        blocked_ips.append({
            'ip_address': ip['ip_address'],
            'attack_type': ip['attack_type'],
            'status': ip['status']
        })

    for ip in model_blocked:
        blocked_ips.append({
            'ip_address': ip['src'],
            'attack_type': ip['attack_cat'],
            'status': 'Detected'
        })

    context = {
        'blocked_ips': blocked_ips,
        'normal_ips': normal_ips,
    }
    print(f'context: {context}')
    return render(request, 'blocked_ips.html', context)


"""


@csrf_exempt
def unblock_ip(request):
    if request.method == "POST":
        data = json.loads(request.body)
        ip = data.get('ip')
        if not ip:
            return JsonResponse({'error': 'Missing IP'}, status=400)

        try:
            BlockedIP.objects.filter(ip_address=ip).delete()
            return JsonResponse({'message': 'IP unblocked successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
def add_blocked_ip(request):
    if request.method == "POST":
        data = json.loads(request.body)
        ip = data.get('ip')
        attack_type = data.get('attack_type')

        if not ip or not attack_type:
            return JsonResponse({'error': 'Missing fields'}, status=400)

        blocked_ip, created = BlockedIP.objects.get_or_create(
            ip_address=ip,
            defaults={'attack_type': attack_type}
        )

        if not created:
            return JsonResponse({'error': 'IP already blocked'}, status=400)

        # Get all blocked IPs
        all_blocked = list(BlockedIP.objects.values('ip_address', 'attack_type'))

        return JsonResponse({
            'message': 'IP blocked successfully',
            'blocked_ips': all_blocked
        })

    return JsonResponse({'error': 'Invalid method'}, status=405)





from django.http import JsonResponse

def get_blocked_ips(request):
    from .models import BlockedIP  # تأكد من استيراد الموديل الصحيح
    blocked = BlockedIP.objects.all()
    data = [{
        'ip_address': ip.ip_address,
        'attack_type': ip.attack_type,
        'status': ip.status
    } for ip in blocked]
    return JsonResponse({'blocked_ips': data})


def get_all_ips(request):
    from .models import BlockedIP
    # يفترض أنك تحتفظ بقائمة كل IPs مرّت عبر النظام
    # ويمكنك تعديل هذه الفكرة حسب طريقة تخزينك
    all_ips = set(...)  # ضع هنا كل IPs التي تمت مراقبتها مثلاً
    blocked_ips = set(BlockedIP.objects.values_list('ip_address', flat=True))
    normal_ips = list(all_ips - blocked_ips)
    return JsonResponse({'normal_ips': normal_ips})



def blocked_ips_view(request):
    blocked_ips = BlockedIP.objects.all()
    return render(request, 'blocked_ips.html', {
        'blocked_ips': blocked_ips,
    })


def dashboard(request):
    blocked_ips = BlockedIP.objects.all()
    return render(request, 'blocked_ips.html', {'blocked_ips': blocked_ips})
