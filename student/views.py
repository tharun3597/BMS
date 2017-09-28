from django.shortcuts import render, redirect
import math
from django.conf import settings
from .models import RegisterStudent
from .models import StudentCourses
from faculty.models import Attendance_sheet,Register
from django.core.mail import send_mail
import bluetooth
import random
from datetime import date



def home(request):
    if request.method == 'POST':
        bad = request.POST['baddr']
        mail = request.POST['email']
        sreg = RegisterStudent.objects.filter(bluetooth_addr=bad)
        if sreg.count() == 0:
            sreg = RegisterStudent.objects.filter(email=mail)
            if sreg.count() == 0:
                register = RegisterStudent(
                                    username=request.POST['username'],
                                    email=mail,
                                    studid=request.POST['sid'],
                                    password=request.POST['password'],
                                    bluetooth_addr=bad,
                                    approval=False
                )
                register.save()
                courses = request.POST.getlist('courses')
                for course in courses:
                    sc = StudentCourses(studentid=register,course=course)
                    sc.save()
                return redirect('student:success')
            else:
                nearby_devices = bluetooth.discover_devices()
                dict = {}
                for x in nearby_devices:
                    dict[x] = bluetooth.lookup_name(x)
                return render(request, 'student/register_form.html',
                              {'dict': dict, 'errors':'Email Id already exists'})
        else:
            nearby_devices = bluetooth.discover_devices()
            dict = {}
            for x in nearby_devices:
                dict[x] = bluetooth.lookup_name(x)
            return render(request, 'student/register_form.html', {'dict': dict,'errors': 'Bluetooth Ip address has been already registered'})
    else:
        # First time the form is displayed to student
        nearby_devices = bluetooth.discover_devices()
        dict = {}
        for x in nearby_devices:
            dict[x] = bluetooth.lookup_name(x)
        return render(request, 'student/register_form.html',{'dict': dict})



def slogin(request):
    if request.method == "POST":
        studentid = request.POST['sid']
        password = request.POST['password']
        student = RegisterStudent.objects.filter(studid=studentid, password=password)
        if student.count() == 1:
            for s in student:
                request.session['id'] = s.pk
            r = RegisterStudent.objects.filter(studid=studentid, password=password,approval=True)
            if r.count() == 1:
                return redirect('student:shome')
            else:
                return render(request, 'student/login.html',{'error':'Not Approved Yet'})
        else:
            return render(request, 'student/login.html', {'error': 'Wrong Credentials'})
    else:
        return render(request, 'student/login.html')

def regs(request):
    return render(request,'student/regsuccess.html')


def edit(request):
    if 'id' in request.session:
        student = RegisterStudent.objects.get(pk=request.session['id'])
        if request.method == 'POST':
            student.username = request.POST['name']
            student.password = request.POST['password']
            student.email = request.POST['email']
            student.save()
            return render(request, 'student/edit.html',{'student':student,'error':'Edited'})
        else:
            return render(request, 'student/edit.html', {'student': student})
    else:
        return redirect('student:slogin')

def shome(request):
    if 'id' in request.session:
        student = RegisterStudent.objects.get(pk=request.session['id'])
        s = Attendance_sheet.objects.filter(sid=student.studid)
        sc = StudentCourses.objects.filter(studentid=student)
        f = Register.objects.filter(approval=True)
        ca = {}
        for i in sc:
            curr_day = Attendance_sheet.objects.filter(sid=student.studid,date=date.today(),course=i.course)
            curr = Attendance_sheet.objects.filter(date=date.today(),course=i.course)
            if curr.count() > 0:
                if curr_day.count() == 1:
                    ca[i.course] = 'P'
                else:
                    ca[i.course] = 'A'
            else:
                ca[i.course] = 'N'

        dict = {}
        p = {}
        for i in sc:
            k = Attendance_sheet.objects.filter(sid=student.studid,course=i.course)
            dict[i.course] = k.count()
            s1 = Register.objects.filter(approval=True, course=i.course)
            if s1.count() > 0:
                t = Register.objects.get(approval=True, course=i.course)
                if t.count != 0:
                    p[i.course] = math.ceil((k.count()/t.count)*100)
                else:
                    p[i.course] = 0
            else:
                p[i.course] = 0
        return render(request,'student/studenthome.html',{'student':student,'f':f,'dict':dict,'p':p,'ca':ca})
    else:
        return redirect('student:slogin')

def stud_logout(request):
    del request.session['id']
    return redirect('student:slogin')

def fpass(request):
    return render(request,'student/fpassword.html')

def email(request):
    mail = request.POST['email']
    s = RegisterStudent.objects.filter(email=mail)
    if s.count() > 0:
        student = RegisterStudent.objects.get(email=mail)
        k = random.randint(100000,999999)
        student.password = k
        student.save()
        message = 'password is '+str(k)
        from_mail = settings.EMAIL_HOST_USER
        try:
            send_mail('Forgot password',message,from_mail, [mail])
            return render(request,'student/fpassword.html',{'error':'Password was sent to your registered Email ID'})
        except:
            return render(request,'student/fpassword.html',{'error':'Your Email ID was not Valid'})
    else:
        return render(request, 'student/fpassword.html', {'error': 'Your email id is not registered'})


