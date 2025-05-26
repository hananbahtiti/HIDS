from django.contrib import admin
from .models import IntrusionResult

from django.contrib import admin
from .models import TrainingResult

from .models import TrainingResult



@admin.register(TrainingResult)
class TrainingResultAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'message', 'rows', 'auc', 'f1')


@admin.register(IntrusionResult)
class IntrusionResultAdmin(admin.ModelAdmin):
    list_display = ('row_index', 'attack_cat', 'mse', 'result', 'timestamp')
    list_filter = ('attack_cat', 'result')
    search_fields = ('row_index', 'attack_cat')
