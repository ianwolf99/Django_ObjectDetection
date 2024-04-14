from django.db import models
from django.contrib.auth.models import User




class UploadedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/') 
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image uploaded by {self.user.username} at {self.uploaded_at}'

class DetectionResult(models.Model):
    uploaded_image = models.ForeignKey(UploadedImage, on_delete=models.CASCADE)
    label = models.CharField(max_length=255)
    confidence = models.FloatField()
    x1 = models.IntegerField()
    y1 = models.IntegerField()
    x2 = models.IntegerField()
    y2 = models.IntegerField()
    image = models.ImageField(upload_to='detection_results_images/',  default='default_image.jpg')

    def __str__(self):
        return f'Detection of {self.label} in {self.uploaded_image}'

    @property
    def box_coordinates(self):
        return (self.x1, self.y1, self.x2, self.y2)
