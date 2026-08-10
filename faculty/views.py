from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from . models import faculty_profile
from django.contrib import messages



# Create your views here.
@login_required(login_url='login_p')
def dashboard(request):
    return render(request,'faculty/faculty_dash.html')

@login_required(login_url='login_p')
def f_profile(request):
    profile = faculty_profile.objects.get(user=request.user)
    return render(request,'faculty/faculty_myprofile.html',{'profile':profile})


@login_required(login_url='login_p')
def f_edit_profile(request):

    profile = faculty_profile.objects.get(user=request.user)

    if request.method == "POST":

        fullname = request.POST.get("fullname")
        if profile:
            profile.fullname=fullname
        
        
        
        department = request.POST.get("department")
        if department:
            profile.department=department
        else:
            profile.department=None

        designation = request.POST.get("designation")
        if designation:
            profile.designation=designation
        else:
            profile.designation=None

        ph_no = request.POST.get("phone_number")
        if ph_no:
            profile.ph_no=ph_no
        else:
            profile.ph_no=None

        if request.FILES.get("profile_image"):
            profile.profile_image=request.FILES.get("profile_image")
        profile.save()

        email = request.POST.get("email")
        if email:
            request.user.email = email
            request.user.save()

        messages.success(request, "Profile updated successfully!")

        return redirect("facu_profile")

    return redirect("facu_profile")