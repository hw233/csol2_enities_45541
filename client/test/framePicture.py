# -*- coding: gb18030 -*-

import BigWorld




#xin_shou_cun = ([-300, -200, 300, 165], "fu_ben_xin_shou_cun")
#fengming = ([-300, -820, 750, 260], "fengming")

g_rect = None
g_label = ""
g_frame =0

frame_count = 5				#帧的数目
fly_time = 5					#飞行时间
x_move_speed = 20				#移动速度
z_move_speed = -20
frame_time = 1					#取帧数频率

frameList = []
framesInOnePos = []

g_path = []

g_lastPos = None

#增加g_restartIndex此索引，是为了重启客户端后，还能接着原来的数据往下测
#从python.log里，可以查g_frameDict的最大key，把此key赋给g_restartIndex，就行了。
g_restartIndex = 0

#从上往下，从左到右

g_stop = False

g_frameDict = {}

doContinue = False

def start( rect, spaceLabel ):
	global g_rect
	global g_label
	global g_path
	global g_lastPos
	calTime( rect )
	g_rect = rect
	left,bottom,right,top = rect
	g_label = spaceLabel
	p = BigWorld.player()
	
	pos = getStartPos( p )
	"""
	pos = BigWorld.collide( p.spaceID, ( left, 100, top ), ( left, -100, top ) )
	print pos
	if pos is None:
		pos = (left, 300, top)
	else:
		pos = pos[0]
	if doContinue:
		pos = p.position
	"""
	g_path.append( pos )
	p.cell.wizCommand( p.id, "goto", spaceLabel +" " + str(pos[0]) +" " + str(pos[1]) +" " + str(pos[2]) )
	g_lastPos = pos
	BigWorld.callback( fly_time, writeFrame )

def run():
	global g_label
	global g_rect
	global frameList
	global g_path
	global g_stop
	global g_lastPos
	global g_frameDict
	left,bottom,right,top = g_rect
	p = BigWorld.player()
	g_lastPos = ( g_lastPos[0] + x_move_speed, g_lastPos[1], g_lastPos[2] )
	if g_lastPos[0] >= right:
		g_lastPos = ( left, 100, g_lastPos[2] + z_move_speed )
		frameList.append( 999 )
		if g_lastPos[2] < bottom:
			print frameList
			print g_frameDict
			return
	pos = BigWorld.collide( p.spaceID, ( g_lastPos[0], 100, g_lastPos[2] ), ( g_lastPos[0], -100, g_lastPos[2] ) )
	if pos is not None:
		pos = pos[0]
	else:
		pos = g_lastPos
	g_path.append( pos )
	p.cell.wizCommand( p.id, "goto", g_label + " " + str(pos[0]) +" " + str(pos[1]) +" " + str(pos[2]) )
	if g_stop:
		print frameList
		print g_frameDict
		return
	BigWorld.callback( fly_time, writeFrame )

def writeFrame():
	"""
	"""
	global g_frame
	global frame_count
	global framesInOnePos
	global frameList
	global g_frameDict
	g_frame += 1
	print "frame: ", float(BigWorld.getWatcher( "FPS" ))
	framesInOnePos.append( float(BigWorld.getWatcher( "FPS" )) )
	if g_frame > frame_count:
		g_frame = 0
		total = 0
		for i in framesInOnePos:
			total += i
		frameList.append( int(total*1.0/len(framesInOnePos) ))
		g_frameDict[len(g_frameDict)+g_restartIndex] = (BigWorld.player().position, int(total*1.0/len(framesInOnePos) ) )
		framesInOnePos = []
		BigWorld.callback( frame_time, run )
	else:
		BigWorld.callback( frame_time, writeFrame )


g_needTime = 0
def calTime( rect ):
	"""
	"""
	global g_needTime
	left,bottom,right,top = rect
	
	xcount = abs(( right - left ) / x_move_speed)
	zcount = abs(( top - bottom ) / z_move_speed)
	
	print "size: ",xcount, "*",zcount
	
	g_needTime = ( xcount * zcount ) * ( (frame_count * frame_time) + fly_time )
	
	if g_needTime > 3600:
		print "need time:",g_needTime/3600,"hour",g_needTime%3600/60,"minite"
	else:
		print "need time:",g_needTime/60,"minite"

#增加对重启客户端的支持。原来只是直接获取。现在加上向前推进。
def getStartPos(p):
	global g_rect
	global g_lastPos	
	left,bottom,right,top = g_rect
	pos = BigWorld.collide( p.spaceID, ( left, 100, top ), ( left, -100, top ) )
	print pos
	if pos is None:
		pos = (left, 300, top)
	else:
		pos = pos[0]
	if doContinue:
		pos = p.position
	g_lastPos = pos
	if g_restartIndex == 0:
		return pos
	#上面是初始启动时用的，如果是重启后要接着测，还要向前推进一段。
	for i in range(g_restartIndex):
		g_lastPos = ( g_lastPos[0] + x_move_speed, g_lastPos[1], g_lastPos[2] )
		if g_lastPos[0] >= right:
			g_lastPos = ( left, 100, g_lastPos[2] + z_move_speed )

	pos = BigWorld.collide( p.spaceID, ( g_lastPos[0], 100, g_lastPos[2] ), ( g_lastPos[0], -100, g_lastPos[2] ) )
	if pos is not None:
		pos = pos[0]
	else:
		pos = g_lastPos
	return pos
