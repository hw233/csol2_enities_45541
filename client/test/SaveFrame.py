# -*- coding: gb18030 -*-

import BigWorld
frames = []




def saveFrame():
	global frames
	fps = int( float(BigWorld.getWatcher( "FPS" ) ))
	frames.append( fps )
	if len( frames ) %30 == 0:
		print "frames:", frames
	BigWorld.callback(1.0, saveFrame )
	
BigWorld.callback(1.0, saveFrame )