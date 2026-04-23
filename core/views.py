from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from .models import FollowersCount, Post, Profile, LikePost, Comment
from .services.message_service import MessageService
from .services.user_service import UserService
from itertools import chain
from django.db.models import Count
from django.db.models import Q
from django.utils import timezone
import random


def _attach_comments_to_posts(posts):
    posts = list(posts)
    post_ids = [post.id for post in posts]

    if not post_ids:
        return posts

    comments_queryset = Comment.objects.filter(post_id__in=post_ids).order_by('-created_at')
    comments_by_post = {}

    for item in comments_queryset:
        comments_by_post.setdefault(item.post_id, []).append(item)

    for post in posts:
        post.comments_list = comments_by_post.get(post.id, [])

    return posts

# Create your views here.
@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.filter(user=user_object).first()

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for user in user_following:
        user_following_list.append(user.user)
    
    for username in user_following_list:
        feed_lists = Post.objects.filter(user=username)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    following_usernames = set(
        FollowersCount.objects.filter(follower=request.user.username)
        .values_list('user', flat=True)
    )

    suggested_users = User.objects.exclude(username=request.user.username).exclude(
        username__in=following_usernames
    )

    suggestions_username_profile_list = list(
        Profile.objects.filter(user__in=suggested_users).select_related('user')
    )
    random.shuffle(suggestions_username_profile_list)

    suggestion_usernames = [profile.user.username for profile in suggestions_username_profile_list]
    suggestion_followers = {
        row['user']: row['total']
        for row in FollowersCount.objects.filter(user__in=suggestion_usernames)
        .values('user')
        .annotate(total=Count('id'))
    }

    for profile in suggestions_username_profile_list:
        profile.followers_count = suggestion_followers.get(profile.user.username, 0)

    feed_list = _attach_comments_to_posts(feed_list)

    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})

@login_required(login_url='signin')
def setting(request):
    user_profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={'id_user': request.user.id}
    )

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
def like_post(request):
    user = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post_id=post_id, username=user).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=user)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')


@login_required(login_url='signin')
def comment_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        comment_body = request.POST.get('comment', '').strip()
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'

        if post_id and comment_body:
            post = Post.objects.filter(id=post_id).first()
            if post:
                Comment.objects.create(
                    post=post,
                    username=request.user.username,
                    body=comment_body,
                )

        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            next_url = '/'

        return redirect(next_url)

    return redirect('/')

@login_required(login_url='signin')
def profile(request, username):
    user_object = User.objects.get(username=username)
    user_profile = Profile.objects.filter(user=user_object).first()
    user_posts = _attach_comments_to_posts(Post.objects.filter(user=username))
    user_post_length = len(user_posts)

    follower = request.user.username
    user = username

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=username))
    user_following = len(FollowersCount.objects.filter(follower=username))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }

    return render(request, 'profile.html', context)

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
    
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/' + user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/' + user)
    else:
        return redirect('/')


@login_required(login_url='signin')
def search(request):
    query = ''

    if request.method == 'POST':
        query = request.POST.get('username', '').strip()
    else:
        query = request.GET.get('q', '').strip()

    matched_profiles = []

    if query:
        matched_users = User.objects.filter(username__icontains=query).order_by('username')
        profiles = Profile.objects.filter(user__in=matched_users).select_related('user')

        usernames = [profile.user.username for profile in profiles]
        follower_counts = {
            row['user']: row['total']
            for row in FollowersCount.objects.filter(user__in=usernames)
            .values('user')
            .annotate(total=Count('id'))
        }

        matched_profiles = [
            {
                'profile': profile,
                'followers': follower_counts.get(profile.user.username, 0),
            }
            for profile in profiles
        ]

    current_user_profile = Profile.objects.filter(user=request.user).first()

    context = {
        'query': query,
        'matched_profiles': matched_profiles,
        'user_profile': current_user_profile,
    }

    return render(request, 'search.html', context)


@login_required(login_url='signin')
def chat(request, username):
    try:
        other_user = UserService.get_user_by_username(username)
    except User.DoesNotExist:
        return redirect('/')

    # initial messages between the two users
    messages_qs = []
    messages_qs = MessageService.get_messages_between(request.user, other_user)

    return render(request, 'chat.html', {'other_user': other_user, 'messages': messages_qs})


@login_required(login_url='signin')
def send_message(request):
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient')
        content = request.POST.get('message', '').strip()

        if not recipient_username or not content:
            return JsonResponse({'ok': False, 'error': 'Missing recipient or content'})

        msg = MessageService.create_message(request.user, recipient_username, content)
        if msg is None:
            return JsonResponse({'ok': False, 'error': 'Recipient not found'})

        return JsonResponse({'ok': True, 'message': MessageService.serialize_message(msg)})

    return JsonResponse({'ok': False, 'error': 'Invalid method'})


@login_required(login_url='signin')
def fetch_messages(request, username):
    other_user = UserService.get_user_by_username(username)
    if not other_user:
        return JsonResponse({'ok': False, 'error': 'User not found'})

    messages_qs = MessageService.get_messages_between(request.user, other_user)
    messages_list = [MessageService.serialize_message(m) for m in messages_qs]

    return JsonResponse({'ok': True, 'messages': messages_list})