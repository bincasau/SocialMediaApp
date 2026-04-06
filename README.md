# SocialMediaApp (Django Project)

## Giới thiệu

**SocialMediaApp** là dự án web xây dựng bằng Django.

* Framework: Django 6.x
* Database: SQLite (mặc định)
* App chính: `core`

---

## Yêu cầu

* Python >= 3.10
* pip

---

## Thiết lập môi trường 

### 1. Tạo môi trường ảo

```bash
python -m venv venv
```

### 2. Kích hoạt môi trường

#### Windows

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
source venv/bin/activate
```

Khi thành công sẽ thấy:

```bash
(venv) ...
```

---

## Cài đặt thư viện

```bash
pip install django
# hoặc nếu có file:
pip install -r requirements.txt
```

---

## Cấu hình Database

---

## Migrate database

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Tạo tài khoản admin

```bash
python manage.py createsuperuser
```

---

## Chạy server

```bash
python manage.py runserver
```

Mở trình duyệt:

```
http://127.0.0.1:8000/
```
