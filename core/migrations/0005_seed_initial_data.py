import base64

from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from django.db import migrations


SEED_POST_CAPTION = 'Bai viet seed cua testuser'
SEED_MESSAGE_1 = 'Xin chao testuser2, day la tin nhan seed 1.'
SEED_MESSAGE_2 = 'Xin chao testuser, minh da nhan duoc tin nhan seed 1.'
SEED_IMAGE_BYTES = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl0W7sAAAAASUVORK5CYII='
)


def seed_initial_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('core', 'Profile')
    Post = apps.get_model('core', 'Post')
    Message = apps.get_model('core', 'Message')

    admin, _ = User.objects.get_or_create(
        username='admin_root',
        defaults={
            'email': 'admin@uit.edu.vn',
            'is_staff': True,
            'is_superuser': True,
            'password': make_password('admin123'),
        },
    )
    if not admin.password:
        admin.password = make_password('admin123')
        admin.save(update_fields=['password'])
    Profile.objects.get_or_create(user=admin, defaults={'id_user': admin.id})

    test_user, _ = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'testuser@uit.edu.vn', 'password': make_password('test1234')},
    )
    if not test_user.password:
        test_user.password = make_password('test1234')
        test_user.save(update_fields=['password'])
    Profile.objects.get_or_create(user=test_user, defaults={'id_user': test_user.id})

    test_user_2, _ = User.objects.get_or_create(
        username='testuser2',
        defaults={'email': 'testuser2@uit.edu.vn', 'password': make_password('test1234')},
    )
    if not test_user_2.password:
        test_user_2.password = make_password('test1234')
        test_user_2.save(update_fields=['password'])
    Profile.objects.get_or_create(user=test_user_2, defaults={'id_user': test_user_2.id})

    post = Post.objects.filter(user=test_user, caption=SEED_POST_CAPTION).first()
    if not post:
        post = Post(user=test_user, caption=SEED_POST_CAPTION)
        post.image.save('seed-post.png', ContentFile(SEED_IMAGE_BYTES), save=True)

    Message.objects.get_or_create(
        sender=test_user,
        recipient=test_user_2,
        content=SEED_MESSAGE_1,
    )
    Message.objects.get_or_create(
        sender=test_user_2,
        recipient=test_user,
        content=SEED_MESSAGE_2,
    )


def unseed_initial_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('core', 'Profile')
    Post = apps.get_model('core', 'Post')
    Message = apps.get_model('core', 'Message')

    Message.objects.filter(content__in=[SEED_MESSAGE_1, SEED_MESSAGE_2]).delete()
    Post.objects.filter(caption=SEED_POST_CAPTION, user__username='testuser').delete()
    Profile.objects.filter(user__username__in=['admin_root', 'testuser', 'testuser2']).delete()
    User.objects.filter(username__in=['admin_root', 'testuser', 'testuser2']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_comment_id_alter_followerscount_id_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_initial_data, unseed_initial_data),
    ]