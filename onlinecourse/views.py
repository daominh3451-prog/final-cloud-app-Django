from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Course, Lesson, Question, Choice, Submission, Enrollment
from datetime import date

# Existing views (if any) go here

# Task 5: Implement submit and show_exam_result

@login_required
def submit(request, course_id):
    """
    Function to handle the exam submission logic.
    """
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    
    # Check if the user is enrolled in the course
    try:
        enrollment = Enrollment.objects.get(user=user, course=course)
    except Enrollment.DoesNotExist:
        # If not enrolled, handle as appropriate for your project (e.g., redirect, error page)
        return redirect('onlinecourse:course_details', pk=course_id)

    # Create a new submission record
    submission = Submission.objects.create(enrollment=enrollment)
    
    # Process the form data
    for key, value in request.POST.items():
        if key.startswith('choice_'):
            choice_id = int(value)
            # Find the choice object and add it to the submission
            try:
                choice = Choice.objects.get(pk=choice_id)
                submission.choices.add(choice)
            except Choice.DoesNotExist:
                pass # Handle the error if a choice is not found

    # Save the submission to update the many-to-many relationship
    submission.save()
    
    # Redirect to the show_exam_result view
    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

@login_required
def show_exam_result(request, course_id, submission_id):
    """
    Function to calculate scores, prepare context, and render the results page.
    """
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Retrieve the selected choices' IDs from the submission
    selected_choices = submission.choices.all()
    selected_ids = [choice.id for choice in selected_choices]
    
    total_score = 0
    max_score = 0
    
    # Iterate through all lessons and questions in the course
    for lesson in course.lesson_set.all():
        for question in lesson.question_set.all():
            max_score += question.grade
            # Use the method from the Question model to calculate the score
            if question.is_get_score(selected_ids):
                total_score += question.grade
                
    # Calculate the grade as a percentage
    grade = int((total_score / max_score) * 100) if max_score > 0 else 0
    
    # Prepare the context for the template
    context = {
        'course': course,
        'grade': grade,
        'total_score': total_score,
        'max_score': max_score,
        'submission': submission,
        'selected_ids': selected_ids
    }
    
    # Render the exam_result_bootstrap.html template with the context
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)



