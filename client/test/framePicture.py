# -*- coding: gb18030 -*-

import BigWorld




#xin_shou_cun = ([-300, -200, 300, 165], "fu_ben_xin_shou_cun")
#fengming = ([-300, -820, 750, 260], "fengming")

g_rect = None
g_label = ""
g_frame =0

frame_count = 5				#֡����Ŀ
fly_time = 5					#����ʱ��
x_move_speed = 20				#�ƶ��ٶ�
z_move_speed = -20
frame_time = 1					#ȡ֡��Ƶ��

frameList = []
framesInOnePos = []

g_path = []

g_lastPos = None

#����g_restartIndex����������Ϊ�������ͻ��˺󣬻��ܽ���ԭ�����������²�
#��python.log����Բ�g_frameDict�����key���Ѵ�key����g_restartIndex�������ˡ�
g_restartIndex = 0

#�������£�������

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

#���Ӷ������ͻ��˵�֧�֡�ԭ��ֻ��ֱ�ӻ�ȡ�����ڼ�����ǰ�ƽ���
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
	#�����ǳ�ʼ����ʱ�õģ������������Ҫ���Ų⣬��Ҫ��ǰ�ƽ�һ�Ρ�
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
