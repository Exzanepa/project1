from django.db import models



from django.contrib.auth import get_user_model

User = get_user_model()

#import---cbcfile to model-------------
class CBCReport(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    cbcrawfile = models.FileField(upload_to='media/cbcrawfile/',null=True,blank=True)
    cbcgrading = models.FileField(upload_to='media/cbcgrading/',null=True,blank=True)
    image = models.ImageField(upload_to='media/images/',default='')
    pdffile = models.FileField(upload_to='media/pdf/',null=True,blank=True)
    created_time = models.DateTimeField('Created Time', auto_now_add=True, null=True)
    updated_time = models.DateTimeField(auto_now=True)
    
    user = models.ForeignKey(User, models.CASCADE)
    
