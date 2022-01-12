# -*- coding: gb18030 -*-
# ʵ��΢�˺�̨���ؿɿ���
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
	΢���������ȼ�Ϊ1~7��7��ߣ�1��͡���̨�������ȼ�����Ϊ1����Ϸ����ʵʱ��������Ϊ7
	��ͨ����������Ϊ5
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
		lt = section.readInt( "losttime" )   # ��ǰĿ¼�Ѿ������˵�ʱ��
		if lt:ctime=lt
		if ctime<section.readInt( "time" ):	# ÿ��Ŀ¼���ذ��ŵ���ʱ��
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
				csol.addDirToQueue( path, dllevel )  # ΢���������ȼ�
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