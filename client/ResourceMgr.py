# -*- coding:gb18030 -*-
# 15:35 2012-3-20，written by wangshufeng

import os
import BigWorld
import ResMgr	# 配置文件在res目录下，故不用Language.openConfigSection
from bwdebug import *
import Timer



# 测试用ui
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
	资源数据封装类，目前仅是数据的封装
	"""
	_dlFilePath = "pt.xml"
	def __init__( self ):
		self.resList = None
		self.mainPath = ""
		
	def init( self, mainPath, paths ):
		self.mainPath = mainPath
		self.resList = paths
		# 初始化加载器
		fileSec = ResMgr.openSection( self._dlFilePath, True )	# 下载程序会监控res/pt.xml文件
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
		# 加载进度
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
		
		self.existedRes = set()			# 已经存在的资源，以资源路径表示，因为申请加载时是以文件路径请求的
		self.loadingRes = []			# 资源加载列表[( archive, callback, spaceID ), ...]
		#self.universeStatus = 0xFFFF	# 地图资源加载情况
		self.downloadTimer = None		# 监控下载情况的timer
		
		# { 地图资源路径: [ 和地图资源相关的其他资源路径 ], ... }like as { "universes/feng_ming_20":[ datas/mount.tcpk, ... ], ...}
		self.universesRelyPaths = {}
		
		self.loadBtConfig()
		self.loadResMapConfig()
		
	@classmethod
	def instance( self ):
		if self._inst is None:
			self._inst = ResLoaderMgr()
		return self._inst
		
	def loadBtConfig( self, path = _allResPackPath ):
		# 加载资源配置文件，记录已下载完毕的资源，以备加载资源时不需要再去读配置就能得知是否已经存在资源。
		# 对于没有记录在案的资源，会提交下载申请，仅需不断的查询下载情况即可，如果下载完毕那么会作为已存在资源记录
		fileSec = ResMgr.openSection( path )
		if fileSec is None:
			ERROR_MSG( "cant find any resource:%s!" % path )
			return
		for subSec in fileSec["files"].values():
			if subSec.readFloat( "process" ) < 1:
				continue
				
			# warning：把路径"data/../../*.tcpk"转换为"../../*"，这是约定好的规则，以资源文件的相对路径为标准
			name, ext = os.path.splitext( subSec.readString( "filepath" ) )	# 把扩展名和路径名分开
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
		if progress >= 1:			# 当前下载完成
			DLProgress.instance().reset()
			data = self.loadingRes.pop()
			path = data[0].mainPath
			data[1]( data[2], path )
			for existedPath in data[0].resList:
				self.existedRes.add( existedPath )
			Timer.cancel( self.downloadTimer )
			self.downloadTimer = None
			self.startDownload()	# 启动下个资源下载

resLoaderMgr = ResLoaderMgr.instance()
