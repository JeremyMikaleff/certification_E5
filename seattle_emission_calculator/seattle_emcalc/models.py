from django.db import models
from django import forms

# Create your models here.

class Buildings(models.Model):
    osebuildingid = models.AutoField(primary_key=True)
    buildingtype = models.CharField(max_length=255, blank=True, null=True)
    primarypropertytype = models.CharField(max_length=255, blank=True, null=True)
    propertyname = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    taxparcelidentificationnumber = models.CharField(max_length=255, blank=True, null=True)
    councildistrictcode = models.IntegerField(blank=True, null=True)
    neighborhood = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    yearbuilt = models.IntegerField(blank=True, null=True)
    numberofbuildings = models.IntegerField(blank=True, null=True)
    numberoffloors = models.IntegerField(blank=True, null=True)
    propertygfatotal = models.FloatField(blank=True, null=True)
    propertygfaparking = models.FloatField(blank=True, null=True)
    propertygfabuilding_s = models.FloatField(blank=True, null=True)
    listofallpropertyusetypes = models.CharField(max_length=255, blank=True, null=True)
    largestpropertyusetype = models.CharField(max_length=255, blank=True, null=True)
    largestpropertyusetypegfa = models.FloatField(blank=True, null=True)
    energystarscore = models.FloatField(blank=True, null=True)
    siteeui_kbtu_sf = models.FloatField(blank=True, null=True)
    siteeuiwn_kbtu_sf = models.FloatField(blank=True, null=True)
    sourceeui_kbtu_sf = models.FloatField(blank=True, null=True)
    sourceeuiwn_kbtu_sf = models.FloatField(blank=True, null=True)
    siteenergyuse_kbtu = models.FloatField(blank=True, null=True)
    siteenergyusewn_kbtu = models.FloatField(blank=True, null=True)
    steamuse_kbtu = models.FloatField(blank=True, null=True)
    electricity_kwh = models.FloatField(blank=True, null=True)
    electricity_kbtu = models.FloatField(blank=True, null=True)
    naturalgas_therms = models.FloatField(blank=True, null=True)
    naturalgas_kbtu = models.FloatField(blank=True, null=True)
    totalghgemissions = models.FloatField(blank=True, null=True)
    ghgemissionsintensity = models.FloatField(blank=True, null=True)
    secondlargestpropertyusetype = models.CharField(max_length=255, blank=True, null=True)
    secondlargestpropertyusetypegfa = models.CharField(max_length=255, blank=True, null=True)
    thirdlargestpropertyusetype = models.CharField(max_length=255, blank=True, null=True)
    thirdlargestpropertyusetypegfa = models.FloatField(blank=True, null=True)
    yearsenergystarcertified = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'buildings'

class NewBuilding(models.Model):
    primarypropertytype = models.CharField(max_length=255, blank=True, null=True)
    yearbuilt = models.IntegerField(blank=True, null=True)
    numberofbuildings = models.IntegerField(blank=True, null=True)
    numberoffloors = models.IntegerField(blank=True, null=True)
    propertygfatotal = models.FloatField(blank=True, null=True)
    propertygfaparking = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'new_building'

class SaveForm(forms.Form):
    primarypropertytype = forms.CharField(max_length=255)
    yearbuilt = forms.IntegerField()
    numberofbuildings = forms.IntegerField()
    numberoffloors = forms.IntegerField()
    propertygfatotal = forms.FloatField()
    propertygfaparking = forms.FloatField()

class UploadFile(forms.Form):
    file_upload = forms.FileField()

class UploadModel(forms.Form):
    model_upload = forms.FileField()

class CalcMultiBat(forms.Form):
    dataset = forms.FileField()
    model = forms.FileField()