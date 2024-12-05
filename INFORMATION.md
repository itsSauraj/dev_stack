# INFORMATION FOR DEVELOPERS

This project contains a default database `db.sqlite3` which has some demo data in it.

The related demo image files are in `/static/images/avatars/*`, `/static/images/posters/*` and 
`/static/images/django-summernote/*`

<font color="#F00">Note: </font>Do not delete the `**/defalut.*` files from any folder


## Information related to users
You can see `usernames` in the databse using any of the sqlite-viewer and `password` for all the users are `qwer@1234`

Two users are
```bash
username::password
saurabh::qwer@1234
myteam::qwer@1234
```

You need to run the application using:
```bash
gunicorn dev_stack.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
So, that the application runs as a `ASGI` application. So, that it can user `WebSockets`(implemented using `Django Channels`).