# -*- coding:gb18030 -*-
# 15:35 2012-3-20��written by wangshufeng

import os
import BigWorld
import ResMgr	# �����ļ���resĿ¼�£��ʲ���Language.openConfigSection
from bwdebug import *
import Timer



# ������ui
from guis import *
from guis.controls.ProgressBar import HProgressBar
from guis.common.RootGUI import RootGUI
from guis import uiFixer

class DLProgress( RootGUI ):
	_inst = None
	def __init__( self ):
		assert self._inst is None, "singleton!!!"
		self._inst = self
		wnd = GUI.load( "guis_v2/otheruis/dlProgress/dlProgress.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.focus = False
		self.moveFocus = False
		self.escHide_ = False
		self.h_dockStyle = "HFILL"
		self.v_dockStyle = "VFILL"
		self.progressBar = HProgressBar( wnd.progress )
		self.progressBar.value = 0
		self.progressBar.speed = 0.6
		self.addToMgr( "wsf_DLProgress" )
		self.posZSegment = ZSegs.L2
		
	def updateProgress( self, path, progressVal ):
		self.progressBar.value = progressVal
		if not self.visible:
			self.show()
			
	def reset( self ):
		self.value = 0
		self.hide()
	
	@classmethod
	def instance( self ):
		if self._inst is None:
			self._inst = DLProgress()
		return self._inst
		

class Archive:
	"""
	��Դ���ݷ�װ�࣬Ŀǰ�������ݵķ�װ
	"""
	_dlFilePath = "pt.xml"
	def __init__( self ):
		self.resList = None
		self.mainPath = ""
		
	def init( self, mainPath, paths ):
		self.mainPath = mainPath
		self.resList = paths
		# ��ʼ��������
		fileSec = ResMgr.openSection( self._dlFilePath, True )	# ���س������res/pt.xml�ļ�
		fileSec.writeFloat( "progress", 0 )
		while ( fileSec.deleteSection( "item" ) ):
			pass
		for path in paths:
			itemSec = fileSec.createSection( "item" )
			itemSec.writeString( "filepath", path )
			itemSec.writeFloat( "progress", 0 )
		fileSec.save()
		ResMgr.purge( self._dlFilePath )
		
	def getLoadStatus( self ):
		# ���ؽ���
		try:
			status = ResMgr.openSection( self._dlFilePath ).readFloat( "progress" )
		except:
			EXCEHOOK_MSG()
			return 0
		ResMgr.purge( self._dlFilePath )
		return status
		
class ResLoaderMgr:
	_inst = None
	_allResPackPath = "bt.xml"
	_resMapFilePath = "resMap.xml"
	def __init__( self ):
		assert self._inst is None, "singleton!!!"
		ResLoaderMgr._inst = self
		
		self.existedRes = set()			# �Ѿ����ڵ���Դ������Դ·����ʾ����Ϊ�������ʱ�����ļ�·�������
		self.loadingRes = []			# ��Դ�����б�[( archive, callback, spaceID ), ...]
		#self.universeStatus = 0xFFFF	# ��ͼ��Դ�������
		self.downloadTimer = None		# ������������timer
		
		# { ��ͼ��Դ·��: [ �͵�ͼ��Դ��ص�������Դ·�� ], ... }like as { "universes/feng_ming_20":[ datas/mount.tcpk, ... ], ...}
		self.universesRelyPaths = {}
		
		self.loadBtConfig()
		self.loadResMapConfig()
		
	@classmethod
	def instance( self ):
		if self._inst is None:
			self._inst = ResLoaderMgr()
		return self._inst
		
	def loadBtConfig( self, path = _allResPackPath ):
		# ������Դ�����ļ�����¼��������ϵ���Դ���Ա�������Դʱ����Ҫ��ȥ�����þ��ܵ�֪�Ƿ��Ѿ�������Դ��
		# ����û�м�¼�ڰ�����Դ�����ύ�������룬���費�ϵĲ�ѯ����������ɣ�������������ô����Ϊ�Ѵ�����Դ��¼
		fileSec = ResMgr.openSection( path )
		if fileSec is None:
			ERROR_MSG( "cant find any resource:%s!" % path )
			return
		for subSec in fileSec["files"].values():
			if subSec.readFloat( "process" ) < 1:
				continue
				
			# warning����·��"data/../../*.tcpk"ת��Ϊ"../../*"������Լ���õĹ�������Դ�ļ������·��Ϊ��׼
			name, ext = os.path.splitext( subSec.readString( "filepath" ) )	# ����չ����·�����ֿ�
			name = "/".join( name.split( "/" )[1:] )
			DEBUG_MSG( "existed resource:%s" % name )
			
			self.existedRes.add( name )
		ResMgr.purge( path )
		
	def loadResMapConfig( self, path = _resMapFilePath ):
		fileSection = ResMgr.openSection( path, True )
		if fileSection is None:
			ERROR_MSG( "cant find resource file %s!" % path )
			return
		for subSec in fileSection.values():
			universPath = subSec.readString( "universePath" )
			tempList = [universPath]
			for itemSection in subSec["item"].values():
				tempList.append( itemSection.asString )
			self.universesRelyPaths[universPath] = tempList
		ResMgr.purge( path )
		
	def getRelativeRes( self, path ):
		return self.universesRelyPaths.get( path, [path] )
		
	def isResExisted( self, resPath ):
		return resPath in self.existedRes
		


	def startDownload( self ):
		if len( self.loadingRes ) == 0:
			DEBUG_MSG( "there is no download request" )
			return
		if self.downloadTimer:
			DEBUG_MSG( "downloading : %s" % self.loadingRes[0][0] )
			return
		self.downloadTimer = Timer.addTimer( 0, 1.5, self.loadResCheck )
		
	def loadResCheck( self ):
		progress = self.loadingRes[0][0].getLoadStatus()
		#INFO_MSG( "%s download progress:%f" % ( self.loadingRes[0][0], progress ) )
		DLProgress.instance().updateProgress( self.loadingRes[0][0], progress )
		if progress >= 1:			# ��ǰ�������
			DLProgress.instance().reset()
			data = self.loadingRes.pop()
			path = data[0].mainPath
			data[1]( data[2], path )
			for existedPath in data[0].resList:
				self.existedRes.add( existedPath )
			Timer.cancel( self.downloadTimer )
			self.downloadTimer = None
			self.startDownload()	# �����¸���Դ����

resLoaderMgr = ResLoaderMgr.instance()
