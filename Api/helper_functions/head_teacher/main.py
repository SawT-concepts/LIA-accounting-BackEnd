from django.db import transaction
from Main.models import Student


def promote_students(school, demoted_students):
    try:
        with transaction.atomic():
            students = Student.objects.filter(school=school)

            for student in students:
                if student in demoted_students:
                    continue  # Skip demoted students

                current_grade = student.grade
                next_class_to_be_promoted_to = current_grade.next_class_to_be_promoted_to

                # Update the student's grade
                student.grade = next_class_to_be_promoted_to
                student.save()

            # Transaction successful, commit changes
            return {"message": "Promotion successful"}
    except Exception as e:
        # Handle exceptions and provide details in the response
        return {"message": f"An error occurred during promotion: {str(e)}"}
