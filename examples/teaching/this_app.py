import sys
sys.path.append('../../voxelviz')

from app import vxv
app, server = vxv('/home/lukas/VoxelViz/examples/teaching/config.json', '/home/lukas/VoxelViz/examples/teaching', True)
