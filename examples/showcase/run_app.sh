/home/lukas/VoxelViz/vxvenv/bin/gunicorn --workers 3 --bind unix:voxelviz.sock -m 007 this_app:server
