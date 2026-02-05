from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Course

# -----------------------------
# Permission Class
# -----------------------------
class IsStudent(permissions.BasePermission):
    """
    Custom permission: only authenticated users with role='student' can access.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "student"
        )

    def has_object_permission(self, request, view, obj):
        """
        Optional: Ensure the student is enrolled in the specific course object.
        """
        return obj.students.filter(id=request.user.id).exists()


# -----------------------------
# Validation Helper
# -----------------------------
def validate_enrollment_status(student, course):
    """
    Ensure the student is enrolled in the given course.
    """
    if not course.students.filter(id=student.id).exists():
        raise ValidationError("Student is not enrolled in this course.")


# -----------------------------
# Example API Endpoint
# -----------------------------
class CourseProgressView(APIView):
    """
    GET: Returns progress for a student in a specific course.
    Requires student authentication and enrollment.
    """
    permission_classes = [IsStudent]

    def get(self, request, course_id):
        # Fetch course or return 404
        course = get_object_or_404(Course, id=course_id)

        # Validate enrollment
        validate_enrollment_status(request.user, course)

        # Assuming your Course model has:
        # def get_progress_for_student(self, student): ...
        progress = course.get_progress_for_student(request.user)

        return Response({"progress": progress}, status=status.HTTP_200_OK)