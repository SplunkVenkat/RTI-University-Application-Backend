from django.db import models

# Create your models here.

class FirstAppeal(models.Model):
     appeal_date = models.DateField(blank=False)
     appeal_date_receive = models.DateField(blank=False)
     appeal_application_number = models.CharField(max_length=70, blank=False, default='')
     appeal_reason = models.CharField(max_length=100, blank=True, default='')
     appeal_endorsement = models.CharField(max_length=100, blank=True, default='')

class CommissionAppeal(models.Model):
     commission_date = models.DateField(null=True, blank=False)
     notice_date = models.DateField(null=True, blank=False)
     hearing_date = models.DateField(null=True, blank=False)
     commission_application_number = models.CharField(max_length=70, blank=False, default='')
     commission_case_number = models.CharField(max_length=70, blank=False, default='')
     commission_file_number = models.CharField(max_length=70, blank=False, default='')

class Application(models.Model):
    id = models.AutoField(primary_key=True)
    application_number = models.BigIntegerField()
    name = models.CharField(max_length=70, blank=False, default='')
    of_name = models.CharField(max_length=70, blank=False, default='')
    date_created = models.DateField(null=True, blank=True)
    address =  models.CharField(max_length=100, blank=True, default='')
    mobilenumber = models.CharField(max_length=12, blank=True, default='')
    date_receive = models.DateField(null=True, blank=True)
    is_svu =models.CharField(max_length=70,default=False)
    last_date = models.DateField(null=True, blank=True)
    endorsement_date = models.DateField(null=True, blank=True)
    endorsement = models.CharField(max_length=100, blank=True, default='')
    application_related = models.CharField(max_length=100, blank=True, default='')
    address_transmitted = models.CharField(max_length=100, blank=True, default='')
    application_status = models.BooleanField(null=True,default=False)
    first_appeal = models.OneToOneField(
        FirstAppeal,
        on_delete=models.SET_NULL,
        blank=True, null=True
    )
    commission_appeal = models.OneToOneField(
        CommissionAppeal,
        on_delete=models.SET_NULL,
         blank=True, null=True
    )
    description = models.CharField(max_length=200, blank=True, default='')

class ApplicationDropDown(models.Model):
    id = models.AutoField(primary_key=True)
    value_data = models.CharField(max_length=100, blank=False, default='')

