# -*- coding:gb18030 -*-
# downLoadResource.py
import ResMgr
import BigWorld
import sys
import csol

def do():
	sys.path.insert( 0, "entities/locale_default/config/client/spaceResource" )
	player = BigWorld.player()
	spaceName = BigWorld.getSpaceName( player.spaceID )
	s_name = spaceName + r"_s"
	u_name = spaceName + r"_u"
	sDatas = __import__( s_name ).Datas
	uDatas = __import__( u_name ).Datas
	del sys.path[0]
	for i in sDatas:
		csol.addFileToQueue(i)	
	for i in uDatas:
		csol.addFileToQueue(i)

def check():
	sys.path.insert( 0, "entities/client/spaceResource" )
	player = BigWorld.player()
	spaceName = BigWorld.getSpaceName( player.spaceID )
	s_name = spaceName + r"_s"
	u_name = spaceName + r"_u"
	sDatas = __import__( s_name ).Datas
	uDatas = __import__( u_name ).Datas
	del sys.path[0]
	a=b=c=d=0
	for i in sDatas:
		if csol.isFileAtLocal( i ):
			a+=1
		else:
			b+=1
	for i in uDatas:
		if csol.isFileAtLocal( i ):
			c+=1
		else:
			d+=1
			print i
	return a,b,c,d