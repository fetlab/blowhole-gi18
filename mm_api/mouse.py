import mmapi
from mmRemote import *;

# initialize connection
remote = mmRemote();
remote.connect();

# construct commands to run
cmd = mmapi.StoredCommands()
bLeftDown=bool()
bMiddleDown=bool()
bRightDown=bool()
bAbsolute=bool()
cmd.AppendMouseDownEvent( bLeftDown, bMiddleDown, bRightDown, x, y, bAbsolute);

while True:
# execute  commands
	remote.runCommand(cmd);
	print(bLeftDown)

#done!
remote.shutdown();