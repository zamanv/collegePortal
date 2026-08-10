from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages

# Create your views here.
@login_required(login_url='login_p')
def dashboard(request):
    return render(request,'students/student_dash.html')

@login_required(login_url='login_p')
def s_profile(request):
    profile = student_profile.objects.get(user=request.user)
    return render(request,'students/stud_myprofile.html',{'profile':profile})

@login_required(login_url='login_p')
def edit_profile(request):

    profile = student_profile.objects.get(user=request.user)

    if request.method == "POST":

        # Full Name
        fullname = request.POST.get("fullname")
        if fullname:
            profile.fullname = fullname

        # Department
        department = request.POST.get("department")
        if department:
            profile.department = department
        else:
            profile.department = ""

        # KTU ID
        ktu_id = request.POST.get("ktu_id")
        if ktu_id:
            profile.ktu_id = ktu_id
        else:
            profile.ktu_id = None

        # Phone Number
        ph_no = request.POST.get("ph_no")
        if ph_no:
            profile.ph_no = ph_no
        else:
            profile.ph_no = None

        # Roll Number
        roll_no = request.POST.get("roll_no")
        if roll_no:
            profile.roll_no = roll_no
        else:
            profile.roll_no = None

        # Date of Birth
        dob = request.POST.get("dob")
        if dob:
            profile.dob = dob
        else:
            profile.dob = None

        # CGPA
        cgpa = request.POST.get("cgpa")
        if cgpa:
            profile.cgpa = cgpa
        else:
            profile.cgpa = None

        # Profile Image
        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        # Save everything
        profile.save()

        return redirect("stud_profile")

    return redirect("stud_profile")