# -*- coding: gb18030 -*-
# 实现微端后台下载可控制
import csol
import BigWorld
from Function import Functor
import ResMgr
from config.client.path import Datas as pDatas

dllevel = 5

ctime = 0
pathList = []
	
def checkAndDownLoad():
	"""
	微端下载优先级为1~7，7最高，1最低。后台下载优先级设置为1，游戏内容实时下载设置为7
	普通可配置下载为5
	"""
	global ctime
	global pathList
	section = ResMgr.openSection( "downloadsec.xml", True )
	
	if not section.readBool("micro"):return
	
	subSec = section["paths"]
	if subSec:
		for name,sec in subSec.items():
			pathList.append( sec.asString )
	def checkTime():
		global ctime
		section = ResMgr.openSection( "downloadsec.xml", True )
		lt = section.readInt( "losttime" )   # 当前目录已经下载了的时间
		if lt:ctime=lt
		if ctime<section.readInt( "time" ):	# 每个目录下载安排的总时间
			ctime +=1
			section.writeInt( "losttime", ctime )
			section.save()
			BigWorld.callback( 60.0, checkTime )
		else:
			path = section.readString( "currentPath" )
			path = path if path else "universes/feng_ming_20"
			index =	pathList.index( path )
			if index < len( pathList ) - 1:
				newPath = pathList[ index+1 ]
				section.writeString( "currentPath", newPath )
				csol.addDirToQueue( path, dllevel )  # 微端下载优先级
				csol.addDirToQueue( path.replace( "universes","space"), dllevel )
				pp = pDatas.get( newPath )
				if pp:
					for ps in pp:
						csol.addFileToQueue( ps, dllevel )
				ctime = 0
				section.writeInt("losttime",ctime)
				section.save()
				checkTime()
			
	ctime = 0
	
	stPath = section.readString( "currentPath" )
	if not stPath:
		stPath = pathList[0]
		section.writeString( "currentPath", stPath )
	csol.addDirToQueue( stPath, dllevel )
	csol.addDirToQueue( stPath.replace("universes","space"), dllevel )
	splist = pDatas.get( stPath )
	if splist:
		for ps in splist:
			csol.addFileToQueue( ps, dllevel )
	section.save()
	checkTime()