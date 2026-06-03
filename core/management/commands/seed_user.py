from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Profile

User = get_user_model()

class Command(BaseCommand):
    help = 'Tạo tài khoản superuser và user mặc định theo Report'

    def handle(self, *args, **kwargs):
        # 1. Tạo Superuser
        if not User.objects.filter(username='admin_root').exists():
            admin = User.objects.create_superuser(
                username='admin_root',
                email='admin@uit.edu.vn',
                password='admin123'
            )
            # Tạo Profile đi kèm
            Profile.objects.get_or_create(user=admin, id_user=admin.id)
            self.stdout.write(self.style.SUCCESS('Đã tạo thành công Superuser: admin_root / admin123'))
        else:
            self.stdout.write(self.style.WARNING('Superuser "admin_root" đã tồn tại.'))

        # 2. Tạo Normal User
        if not User.objects.filter(username='testuser').exists():
            test_user = User.objects.create_user(
                username='testuser',
                email='testuser@uit.edu.vn',
                password='test1234'
            )
            # Tạo Profile đi kèm
            Profile.objects.get_or_create(user=test_user, id_user=test_user.id)
            self.stdout.write(self.style.SUCCESS('Đã tạo thành công Normal User: testuser / test1234'))
        else:
            self.stdout.write(self.style.WARNING('User "testuser" đã tồn tại.'))
