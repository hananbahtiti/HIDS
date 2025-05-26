
from django.contrib import admin
from django.urls import path
from detection.views import protocol_report_view
from analytics.views import dashboard_view
from ips.views import ip_report_view, add_blocked_ip, get_all_ips, unblock_ip, blocked_ips_view, get_blocked_ips
from results.views import fetch_intrusion_data_api, fetch_intrusion_data_page, get_intrusion_data_from_db, save_csv, training_results_view
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.shortcuts import redirect


urlpatterns = [
    path('', lambda request: redirect('admin_login')),  # إعادة التوجيه للرابط الجذر
    path('admin/', admin.site.urls),
    path('admin-login/', auth_views.LoginView.as_view(template_name='admin_login.html'), name='admin_login'),
    path('protocol-report/',protocol_report_view, name='protocols'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('admin_login')), name='logout'),
    path('dashboard/', dashboard_view,  name='dashboard'),
    path('ip/', ip_report_view, name='ip'),
    path('blocked_ips/', blocked_ips_view, name='blocked_ips'),
    path('api/add_blocked_ip/', add_blocked_ip, name='add_blocked_ip'),
    path('api/get_all_ips/', get_all_ips, name='get_all_ips'),
    path('api/get_blocked_ips/', get_blocked_ips, name='get_blocked_ips'),
    path('api/unblock_ip/', unblock_ip, name='unblock_ip'),
    path('intrusion_results/fetch/', fetch_intrusion_data_api, name='intrusion_results_fetch'),
    path('intrusion_results/', get_intrusion_data_from_db, name='intrusion_results'),
    path('intrusion_results_page/', fetch_intrusion_data_page, name='intrusion_results_page'),
    #path('send-csv/', send_csv_to_fastapi, name='send_csv_to_fastapi'),
    path("save_csv/", save_csv, name="save_csv"),
    path('training-results/', training_results_view, name='training_results'),
    


]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)