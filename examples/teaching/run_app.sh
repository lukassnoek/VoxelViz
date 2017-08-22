/home/lukas/voxelviz/voxelvizenv/bin/gunicorn --workers 3 --bind unix:voxelviz.sock -m 007 app:server
