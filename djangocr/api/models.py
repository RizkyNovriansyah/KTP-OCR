from django.db import models
# from coofis.storage_backends import AttachmentStorage
from datetime import datetime
from django.core.files.storage import FileSystemStorage
import os

class AttachmentStorage(FileSystemStorage):
    location = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media/files/attachments')
    file_overwrite = False
    
def upload_to_relative(instance, filename):
    date = datetime.now().date()
    return '%s/%s/%s/%s' % (str(date.year), str(date.month), str(date.day), filename)

# Create your models here.
class Attachment(models.Model):
    files = models.FileField(storage=AttachmentStorage(), upload_to=upload_to_relative)
    uploaded_at = models.DateTimeField(auto_now_add=True)