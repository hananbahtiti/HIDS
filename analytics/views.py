from django.shortcuts import render
from ips.models import BlockedIP
from results.models import IntrusionResult
from django.contrib.auth.decorators import login_required, user_passes_test



def is_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(is_admin)
@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

# Create your views here.
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def dashboard_view(request):
    # IPs المحظورة يدويًا
    manually_blocked = BlockedIP.objects.all().values('ip_address', 'attack_type', 'status')

    # IPs المكتشفة من النموذج
    model_blocked = IntrusionResult.objects.exclude(result__iexact='NORMAL') \
                                           .exclude(src__isnull=True).exclude(src='N/A') \
                                           .values('src', 'attack_cat') \
                                           .distinct()

    # دمجهم في قائمة واحدة
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

    protocol_data = IntrusionResult.objects.order_by('-timestamp')
    network_data = [
        {
            'protocol': entry.proto,
            'src': entry.src,
            'status': entry.result,
            'timestamp': entry.timestamp,
        }
        for entry in protocol_data
    ]
    context = {
        'blocked_ips': blocked_ips,
        'network_data': network_data,
    }
    #print('context', context)

    return render(request, 'dashboard.html', context)




