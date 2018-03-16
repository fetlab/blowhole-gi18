import os
import sys
import mmapi
from mmRemote import *
import mm

remote = mmRemote()
remote.connect()

scale_size=1;
move_dy=1;
mm.begin_tool(remote, "transform")
mm.set_toolparam(remote, "scale", [scale_size,scale_size,scale_size] )
mm.set_toolparam(remote, "translation", [0,move_dy,0] )
mm.accept_tool(remote)