from django.db import models
from django.utils import timezone
from datetime import datetime



class TrainingResult(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=255)
    rows = models.IntegerField(null=True, blank=True)
    auc = models.FloatField(null=True, blank=True)
    f1 = models.FloatField(null=True, blank=True)
    report = models.TextField(null=True, blank=True)

    confusion_matrix = models.CharField(max_length=255, null=True, blank=True)
    training_loss = models.CharField(max_length=255, null=True, blank=True)
    error_distribution = models.CharField(max_length=255, null=True, blank=True)
    csv_result = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Training at {self.timestamp} -  {self.message} -  {self.rows} -  {self.auc} - {self.f1} - {self.report}  - {self.confusion_matrix}  -  {self.training_loss}  - {self.error_distribution} -  {self.csv_result}"



class IntrusionResult(models.Model):
    row_index = models.IntegerField()
    attack_cat = models.CharField(max_length=100)
    mse = models.FloatField()
    result = models.CharField(max_length=50)
    ct_src_dport_ltm = models.CharField(max_length=50, default='N/A')
    rate = models.CharField(max_length=50, default='N/A')
    dwin = models.CharField(max_length=50, default='N/A')
    dload = models.CharField(max_length=50, default='N/A')
    swin = models.CharField(max_length=50, default='N/A')
    ct_dst_sport_ltm = models.CharField(max_length=50, default='N/A')
    ct_state_ttl = models.CharField(max_length=50, default='N/A')
    sttl = models.CharField(max_length=50, default='N/A')
    timestamp = models.DateTimeField(default=timezone.now)
    src = models.GenericIPAddressField( null=True, blank=True)
    proto = models.CharField(max_length=20, default='N/A')
    state = models.FloatField(default=0.0)





    def __str__(self):
        return f"Row {self.row_index} - {self.attack_cat} - {self.mse} - {self.result} - {self.ct_src_dport_ltm} - {self.rate} - {self.dwin} - {self.dload} - {self.swin} - {self.ct_dst_sport_ltm} - {self.ct_state_ttl} - {self.sttl}  -  {self.timestamp} - {self.src} - {self.proto} - {self.state} " 