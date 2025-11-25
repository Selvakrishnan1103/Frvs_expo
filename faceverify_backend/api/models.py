from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=100, unique=True)
    student_name = models.CharField(max_length=200)

    parent_id = models.CharField(max_length=100)
    parent_name = models.CharField(max_length=200)

    parent_face_image = models.ImageField(upload_to='parent_faces/')

    def __str__(self):
        return f"{self.student_name} ({self.student_id})"
