from django.db import models

class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField()
    attack_type = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='Blocked')

    def __str__(self):
        return f"{self.ip_address} - {self.attack_type}"