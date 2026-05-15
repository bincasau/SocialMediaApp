# Kich ban test Postman

Bo collection nay danh cho app Django SocialMediaApp, co dung session auth va CSRF.

## Cach dung

1. Mo Postman.
2. Import file `postman/SocialMediaApp.postman_collection.json`.
3. Dat bien `base_url` neu app khong chay o `http://127.0.0.1:8000`.
4. Chay request `01 - GET Signup Page` truoc de lay `csrftoken`.
5. Chay `02 - POST Signup` de tao user moi.
6. Chay `03 - GET Signin Page` va `04 - POST Signin` de dang nhap.
7. Sau khi dang nhap, Postman se giu `sessionid` tu cookie jar.

## Bien can chinh

- `base_url`
- `username`
- `email`
- `password`
- `post_id`
- `comment_body`
- `follower`
- `follow_target`
- `recipient`
- `message_body`
- `search_query`
- `profile_username`
- `chat_username`

## Luu y

- Cac request `POST` phai co `X-CSRFToken`.
- Request upload anh `07 - POST Upload Post` can ban chon file trong Postman.
- `post_id` phai la ID that cua Post da tao trong DB, admin, hoac profile page.
- `chat/send/` va `chat/fetch/` tra ve JSON, con cac request khac la HTML hoac redirect.

## Thu tu test goi y

1. Signup
2. Signin
3. Home feed
4. Profile
5. Upload post
6. Like post
7. Comment post
8. Follow user
9. Search
10. Open chat
11. Send message
12. Fetch messages
13. Logout
