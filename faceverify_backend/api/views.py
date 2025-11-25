# api/views.py
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Student
from .facepp_utils import compare_faces
from django.conf import settings

class RegisterParent(APIView):
    def post(self, request):
        # expected form fields: student_id, student_name, parent_id, parent_name, parent_face (file)
        print("REGISTER DATA:", request.data)
        print("REGISTER FILES:", request.FILES)

        student_id = request.data.get('student_id')
        student_name = request.data.get('student_name')
        parent_id = request.data.get('parent_id')
        parent_name = request.data.get('parent_name')
        parent_face = request.FILES.get('parent_face') or request.FILES.get('image') or request.FILES.get('face')

        if not (student_id and student_name and parent_id and parent_name and parent_face):
            return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

        student = Student(
            student_id=student_id,
            student_name=student_name,
            parent_id=parent_id,
            parent_name=parent_name,
            parent_face_image=parent_face
        )
        student.save()
        return Response({'message': 'Registered'}, status=status.HTTP_201_CREATED)


class VerifyFace(APIView):
    def post(self, request):
        print("DEBUG — DATA:", request.data)
        print("DEBUG — FILES:", request.FILES)

        student_id = request.data.get('student_id')
        live_photo = request.FILES.get('face') or request.FILES.get('image')  # accept both keys

        if not student_id:
            return Response({'error': 'student_id required'}, status=status.HTTP_400_BAD_REQUEST)
        if not live_photo:
            return Response({'error': 'No image uploaded (face or image field missing)'}, status=status.HTTP_400_BAD_REQUEST)

        student = get_object_or_404(Student, student_id=student_id)
        stored_image_path = student.parent_face_image.path

        # debug info
        print("Selva student:", student)
        print("STORED IMAGE PATH:", stored_image_path)
        print("FILE EXISTS:", os.path.exists(stored_image_path))
        try:
            matched, confidence = compare_faces(stored_image_path, live_photo)
        except Exception as e:
            print("COMPARE ERROR:", str(e))
            return Response({'error': 'Internal error during face comparison', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        print("RESULT:", matched, confidence)
        return Response({
            "matched": matched,
            "confidence": confidence,
            "student_name": student.student_name
        })
