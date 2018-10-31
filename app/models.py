from django.db import models

# Create your models here.

class MemberBusAlert(models.Model):
    user_key = models.CharField(max_length = 20)
    bus_num = models.CharField(max_length = 4)
    goschool_stn = models.CharField(max_length = 5)
    gohome_stn = models.CharField(max_length = 5)
