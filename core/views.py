from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Post, Profile

# Create your views here.
@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    return render(request, 'index.html', {'user_profile': user_profile})

@login_required(login_url='signin')
def setting(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        if request.FILES.get('profileimg') == None:
            profileimg = user_profile.profileimg
            location = request.POST['location']
            bio = request.POST['bio']

            user_profile.profileimg = profileimg
            user_profile.location = location
            user_profile.bio = bio
            user_profile.save()

        if request.FILES.get('profileimg') != None:
            profileimg = request.FILES.get('profileimg')
            location = request.POST['location']
            bio = request.POST['bio']

            user_profile.profileimg = profileimg
            user_profile.location = location
            user_profile.bio = bio
            user_profile.save()
        
        return redirect('setting')

    return render(request, 'setting.html', {'user_profile': user_profile})

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')
    return HttpResponse('Upload')

def signup(request):
    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already used')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already used')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()

                return redirect('setting')
        else: 
            messages.info(request, 'Password not matching')
            return redirect('signup')

    else : return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')

    else :
        return render(request, 'signin.html')
    
def logout(request):
    auth.logout(request)
    return redirect('signin')
