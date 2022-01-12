# -*- coding: gb18030 -*-
# $Id: GameMgr.py,v 1.19 2008-06-26 01:07:57 huangyongwei Exp $
#

"""
locates client definations

2008.01.12 : writen by huangyongwei
"""
import random
import csol
import BigWorld
import csdefine
import csstatus
import ResMgr
import Math
import event.EventCenter as ECenter
import Define
import reimpl_login
from bwdebug import *
from Function import Functor
from gbref import rds
from UnitSelect import UnitSelect
from ChatFacade import chatFacade
from MessageBox import *
from VehicleHelper import isFalling
import os
import BackDownLoadMgr

# --------------------------------------------------------------------
# module global methods
# --------------------------------------------------------------------
def _quitGameQuery() :
	GameMgr.instance().quitGame( True )
	return False

def _strToHex( s ):
	"""
	将字符串转为十六进制格式的字符流
	例如: s = "测试字符串", 则函数返回 'b2e2cad4d7d6b7fbb4ae'
	"""
	if len( s ) == 0:
		return ""
	lst = []
	for ch in s:
		hv = hex( ord( ch ) ).replace( '0x', '' )
		if len(hv) == 1:
			hv = '0'+ hv
		lst.append( hv )
	return reduce( lambda x, y : x + y, lst )

# --------------------------------------------------------------------
# implement game server info class
# --------------------------------------------------------------------
class ServerInfo( object ) :
	def __init__( self, sect ) :
		self.__hosts = sect.readStrings( "host" )
		for host in self.__hosts[:] :
			if host == "" :
				self.__hosts.remove( host )

		self.sect = sect
		self.hostName = sect.asString
		self.userName = sect.readString( "username" )
		self.password = sect.readString( "password" )
		self.inactivityTimeout = sect.readInt( "inactivityTimeout" )

	@property
	def host( self ) :
		"""
		随机获取一个主机
		"""
		if len( self.__hosts ) == 0 :
			ERROR_MSG( "no host to be choice!" )
			return ""
		return random.choice( self.__hosts )

# --------------------------------------------------------------------
# implement game manager class
# --------------------------------------------------------------------
class GameMgr :
	__inst = None

	def __init__( self ) :
		assert GameMgr.__inst is None
		csol.setCloseQuery( _quitGameQuery )

		self.__gbRootSect = None											# 全局配置根 section
		self.__gbOptions = {}												# 全局配置
		self.__gbOptions["section"] = None									# 配置 section
		self.__gbOptions["historyAccount"] = ""								# 前一次登录的账号

		self.__accountRootSect = None										# 账号配置根 section
		self.__accountOptions = {}											# 当前登录的账号配置
		self.__accountOptions["section"] = None								# 配置 section
		self.__accountOptions["selRoleID"] = 0								# 前一次进入游戏的角色索引

		self.__roleRootSect = None											# 角色配置根 section
		self.__roleOptions = {}												# 当前角色配置
		self.__roleOptions["section"] = None								# 配置 section
		self.__roleOptions["firstEnter"] = True								# 记录该角色是否是第一次进入世界

		self.__servers = []													# 服务器列表
		self.__accountInfo = {}												# 账号信息
		self.__accountInfo["server"] = ""
		self.__accountInfo["accountName"] = ""
		self.__roleInfo = None												# 进入游戏的角色信息( RoleMaker.RoleInfo )

		self.__isInQuery = False											# 临时变量，是否进行关闭询问
		self.__manualLogoff = False											# 临时变量，记录当前断开链接是手工的还是服务器踢开的

		self.__serverSpaceID = 0											# 重新选择前的角色场景ID
		self.__inKickoutStatus = False										# 是否处于被踢出状态
		self.__playingVideo = False
		
		chatFacade.bindStatus( csstatus.ACCOUNT_STATE_FORCE_LOGOUT, self.__onKickout )

	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = GameMgr()
		return SELF.__inst


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __quitGameQuery( self ) :
		"""
		退出游戏询问
		"""
		player = BigWorld.player()
		if player and player.isPlayer() :
			ECenter.fireEvent( "EVT_ON_SHOW_GAME_LOG" )
		else :
			if self.__isInQuery : return
			self.__isInQuery = True
			def query( rs_id ) :
				self.__isInQuery = False
				if rs_id == RS_YES :
					BigWorld.savePreferences()
					self.quitGame( False )
				else :
					ECenter.fireEvent( "EVT_ON_GOT_CONTROL" )
			py_msg = showMessage( 0x0000, "", MB_YES_NO, query )
			from guis.ScreenViewer import ScreenViewer
			ScreenViewer().addResistHiddenRoot(py_msg)
			py_msg.visible = True


	# -------------------------------------------------
	def __readGlobalOptions( self ) :
		"""
		加载账号相关的全局配置信息
		"""
		self.__gbRootSect = ResMgr.openSection( "account", True )				# 加载全局根 section
		try :
			sect = ResMgr.openSection( "account/gbconfig.xml", True )			# 全局基本配置
			self.__gbOptions["section"] = sect
			historyAccount = sect["historyAccount"]								# 前一次登录的账号名
			if historyAccount is None :
				sect.writeString( "historyAccount", "" )
			self.__gbOptions["historyAccount"] = sect.readString( "historyAccount" )
			sect.save()
		except IOError :
			ERROR_MSG( "save gbconfig failed!" )
		except TypeError :														# 如果文件被损坏，则会执行到这里
			# 删除 gbconfig.xml ( 目前没办法 )
			pass

	def __readAccountOptions( self ) :
		"""
		获取当前账号配置信息
		"""
		accountName = self.__accountInfo["accountName"]							# 当前登录的账号名称
		root = "account/" + accountName
		self.__accountRootSect = ResMgr.openSection( root, True )				# 加载账号配置根 section

		try :
			config = "%s/option.xml" % root										# 账号基本配置
			sect = ResMgr.openSection( config, True )
			self.__accountOptions["section"] = sect
			selRoleID = sect["selRoleID"]										# 前一次进入游戏的角色索引
			if selRoleID is None :
				sect.writeInt( "selRoleID", 0 )
			self.__accountOptions["selRoleID"] = sect.readInt( "selRoleID" )
			sect.save()
		except IOError :
			ERROR_MSG( "save option config failed!" )
		except TypeError :														# 如果文件被损坏，则会执行到这里
			# 删除 option.xml ( 目前没办法 )
			pass

	def __readRoleOptions( self ) :
		"""
		加载当前角色配置信息
		"""
		accountName = self.__accountInfo["accountName"]							# 首先得到角色所属的账号名
		playerName = self.getCurrRoleHexName()									# 获得角色名
		root = "account/%s/%s" % ( accountName, playerName )
		self.__roleRootSect = ResMgr.openSection( root, True )					# 加载角色配置根 section

		try :
			config = "%s/options.xml" % root									# 角色基本配置
			sect = ResMgr.openSection( config, True )							# 创建 section
			self.__roleOptions["section"] = sect								# 保存 section
			firstEnter = sect["firstEnter"]										# 获取是否第一次进入游戏（换一台机器则不生效）
			if firstEnter is None :												# 如果没有该标记
				self.__roleOptions["firstEnter" ] = True						# 则表示是第一次 enterworld
				sect.writeBool( "firstEnter", False )							# 写入该标记，表示不再是第一次进入游戏
			else :
				self.__roleOptions["firstEnter" ] = False
			sect.save()
		except IOError :
			ERROR_MSG( "save option config failed!" )
		except TypeError :
			# 删除 option.xml ( 目前没办法 )
			pass

	# -------------------------------------------------
	def __onKickout( self, statusID, msg ) :
		"""
		被服务器踢出时调用
		"""
		self.__inKickoutStatus = True


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def init( self ) :
		"""
		游戏启动时被调用
		"""
		for tag, pyDs in rds.userPreferences["login"].items() :		# 获取游戏配置 Option.xml 中的登录信息（服务器 IP）
			try :
				server = ServerInfo( pyDs )
				self.__servers.append( server )						# 获取服务器列表
			except :
				DEBUG_MSG( "can't find server %s!" % tag )
		self.__readGlobalOptions()									# 获取历史登录账号
		rds.resLoader.loadStartResource()
		rds.statusMgr.changeStatus( Define.GST_GAME_INIT )			# 设置当前的游戏状态为游戏初始化状态

	@reimpl_login.deco_gameMgrOnGameStart
	def onGameStart( self ) :
		"""
		游戏启动成功，进入账号输入时被调用
		"""
		rds.statusMgr.changeStatus( Define.GST_LOGIN )				# 设置当前的游戏状态为登录状态
		rds.resLoader.onGameStart()									# 通知资源加载器
		chatFacade.onGameStart()
		BackDownLoadMgr.checkAndDownLoad()

	# ---------------------------------------
	def onConnected( self ) :
		"""
		登录账号成功时被调用
		"""
		INFO_MSG( "connect successily!" )

	def onDisconnected( self ) :
		"""
		登录账号失败时被调用
		"""
		INFO_MSG( "onDisconnected!" )
		printStackTrace()
		if not self.__manualLogoff :										# 服务器断开
			rds.worldCamHandler.unfix()										# 断开后恢复鼠标
			rds.resLoader.onOffline()										# 告诉资源加载器，停止加载
			rds.statusMgr.changeStatus( Define.GST_OFFLINE )				# 更换状态
			rds.gameSettingMgr.onPlayerOffline()							# 通知游戏设置管理器掉线了
		else :																# 玩家请求返回登录
			rds.statusMgr.changeStatus( Define.GST_LOGIN )					# 将状态改为登录状态
		self.__manualLogoff = False											# 重新设置为非手工返回登录

	# ---------------------------------------
	@reimpl_login.deco_gameMgrOnLogined
	def onAccountLogined( self ) :
		"""
		当 BigWorld.player() 转变为 Account 时被调用
		"""
		def readyCallback() :
			rds.statusMgr.changeStatus( Define.GST_ROLE_SELECT )
			try:
				name = BigWorld.getSpaceName( self.__serverSpaceID )
				BigWorld.releaseServerSpace( self.__serverSpaceID )
				self.__serverSpaceID = 0
			except ValueError, ve:
				pass
		rds.statusMgr.changeStatus( Define.GST_ENTER_ROLESELECT_LOADING )
		rds.resLoader.loadLoginSpace( True, readyCallback )						# 加载角色选择场景

	def onLogout( self ) :
		"""
		返回角色选择，player 变为 Account 时被调用
		"""
		def loadResourceEnd() :													# 加载角色选择场景结束时被调用
			rds.statusMgr.changeStatus( Define.GST_ROLE_SELECT )
		rds.statusMgr.changeStatus( Define.GST_BACKTO_ROLESELECT_LOADING )
		rds.resLoader.loadLoginSpace( False, loadResourceEnd )
		try:
			BigWorld.releaseServerSpace( self.__serverSpaceID )	# 清理角色原space数据
			self.__serverSpaceID = 0
		except ValueError, ve:
			print ve

	def getCurrRoleHexName( self ):
		"""
		获取当前角色名字的十六进制的编码
		"""
		return _strToHex( self.__roleInfo.getName() )

	# ---------------------------------------
	def onBecomePlayer( self ) :
		"""
		进入游戏后创建角色成功时被调用
		"""
		self.__roleOptions["section"].save()

	def onRoleEnterWorld( self ) :
		"""
		角色进入世界时被调用
		"""
		rds.resLoader.onRoleEnterWorld()
		rds.helper.courseHelper.onRoleEnterWorld()
		rds.shortcutMgr.onRoleEnterWorld()
		rds.ruisMgr.onRoleEnterWorld()
		chatFacade.onRoleEnterWorld()

	def onRoleLeaveWorld( self ) :
		"""
		角色离开世界时被调用
		"""
		rds.helper.courseHelper.onRoleLeaveWorld()
		rds.helper.pixieHelper.onRoleLeaveWorld()
		rds.viewInfoMgr.onRoleLeaveWorld()
		rds.shortcutMgr.onRoleLeaveWorld()
		rds.ruisMgr.onRoleLeaveWorld()
		rds.resLoader.onRoleLeaveWorld()
		chatFacade.onRoleLeaveWorld()
		UnitSelect().onRoleLeaveWorld()
		rds.castIndicator.clear()
		rds.opIndicator.clear()
		rds.questRelatedNPCVisible.clear()

	def onFirstSpaceReady( self ) :
		"""
		当角色从角色选择到进入世界时被调用
		"""
		rds.worldCamHandler.reset()								# 使用相机的默认配置
		rds.helper.courseHelper.onFirstSpaceReady()
		rds.helper.uiopHelper.onFirstSpaceReady()
		rds.helper.pixieHelper.onFirstSpaceReady()
		rds.ruisMgr.onRoleInitialized()							# 通知 UI 管理器

	def onLeaveSpace( self ) :
		"""
		当角色要离开某个场景时被调用
		"""
		rds.statusMgr.changeStatus( Define.GST_SPACE_LOADING )
		def readyCallback() :									# 要进入的新的 space 是否加载完毕
			rds.statusMgr.changeStatus( Define.GST_IN_WORLD )	# 如果加载完毕，则将当前状态重新置为 IN_WORLD 状态
		rds.resLoader.teleportSpace( readyCallback )			# 退出某个 space 意味着要进入某个 space

	def onLeaveArea( self ) :
		"""
		当角色离开某个区域时被调用（同地图的区域跳转时被调用）
		"""
		rds.statusMgr.changeStatus( Define.GST_SPACE_LOADING )
		def readyCallback() :									# 要进入的新的 space 是否加载完毕
			rds.statusMgr.changeStatus( Define.GST_IN_WORLD )	# 如果加载完毕，则将当前状态重新置为 IN_WORLD 状态
		rds.resLoader.teleportArea( readyCallback )				# 退出某个 space 意味着要进入某个 space


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getGlobalRootSect( self ) :
		"""
		获取全局配置根 section
		"""
		return self.__gbRootSect

	def getAccountRootSect( self ) :
		"""
		获取账号配置根 section
		"""
		return self.__accountRootSect

	def getRoleRootSect( self ) :
		"""
		获取角色配置根 section
		"""
		return self.__roleRootSect

	# -------------------------------------------------
	def getGlobalOption( self, key ) :
		"""
		获取全局配置属性：historyAccount
		"""
		assert key in self.__gbOptions
		return self.__gbOptions[key]

	def setGlobalOption( self, key, value ) :
		"""
		设置全局配置属性
		"""
		if key not in self.__gbOptions :
			ERROR_MSG( "global option %s is not exitst!" % key )
		else :
			try:
				self.__gbOptions[key] = value
				self.__gbOptions["section"].writeString( key, str( value ) )
			except:
				self.deldir( "account" )
				ResMgr.purge( "account" )	#清空缓存
				self.__readGlobalOptions()		#删除后重新创建account文件

	def deldir( self, path):
		path2 = os.path.join("res",path) # 含res的的目录
		if not os.path.exists( path2 ):
			return
		files = os.listdir( path ) #顶层目录和文件

		for file in files:
			filedir = os.path.join( path2, file )
			if os.path.isfile( filedir ):
				os.remove( filedir )	#如果是文件直接删除
			else:
				try:
					os.rmdir( filedir )		#直接删除空目录
				except:
					newfiledir = filedir.split("res\\")[1]
					self.deldir( newfiledir )
		files = os.listdir( path ) #顶层目录和文件
		if len( files ) == 0:
			os.rmdir( path2 )

	# --------------------------------------------------
	def getAccountOption( self, key ) :
		"""
		获取账号配置属性：selRoleID
		"""
		assert key in self.__accountOptions
		return self.__accountOptions[key]

	def setAccountOption( self, key, value ) :
		"""
		设置账号配置属性
		"""
		if key not in self.__accountOptions :
			ERROR_MSG( "account option %s is not exitst!" % key )
		else :
			self.__accountOptions[key] = value
			try :
				self.__accountOptions["section"].writeString( key, str( value ) )
			except :
				EXCEHOOK_MSG( "write account's config file fail! key = %s, value = %s" % ( str( key ), str( value ) ) )

	# ---------------------------------------
	def getRoleOption( self, key ) :
		"""
		获取角色配置信息：firstEnter
		"""
		assert key in self.__roleOptions
		return self.__roleOptions.get( key, None )

	def setRoleOption( self, key, value ) :
		"""
		设置角色配置信息
		"""
		if key not in self.__roleOptions :
			ERROR_MSG( "account option %s is not exitst!" % key )
		else :
			self.__roleOptions[key] = value
			self.__roleOptions["section"].writeString( key, str( value ) )

	# -------------------------------------------------
	def getServers( self ) :
		"""
		获取服务器列表
		"""
		return self.__servers[:]

	def getCurrAccountInfo( self ) :
		"""
		获取当前登录的账号信息: { "server" : 当前服务器, "accountName" : 当前账号名称 }
		"""
		return self.__accountInfo

	def getCurrRoleInfo( self ) :
		"""
		获取当前角进入游戏的色信息( RoleMaker.RoleInfo )
		"""
		return self.__roleInfo

	# -------------------------------------------------
	def requestLogin( self, server, uname, psw, callback ) :
		"""
		请求登录账号
		"""
		class LoginInfo : pass
		loginInfo = LoginInfo()
		loginInfo.username = uname
		loginInfo.password = psw
		loginInfo.initialPosition   = Math.Vector3( 0, 0, 1 )
		loginInfo.initialDirection  = Math.Vector3( 0, 0, 0 )
		loginInfo.inactivityTimeout = 60.0
		self.__accountInfo["server"] = server						# 设置当前登录的服务器
		self.__accountInfo["accountName"] = uname					# 设置当前登录的账号名
		self.__readAccountOptions()									# 读取当前登录账号的配置信息
		self.__gbOptions["section"].save()
		host = server.host
		if host == "" :
			showMessage( 0x0001, "", MB_OK )
		else :
			BigWorld.connect( host, loginInfo, callback )

	# -------------------------------------------------
	def requestEnterGame( self, roleInfo ):
		"""
		请求进入游戏，向服务器请求验证
		"""
		self.__roleInfo = roleInfo
		BigWorld.player().requestEnterGame()

	def enterGame( self ) :
		"""
		请求进入游戏
		"""
		INFO_MSG( "enter game after verify!" )
		#self.__roleInfo = roleInfo
		self.__readRoleOptions()
		self.__accountOptions["section"].save()
		rds.statusMgr.changeStatus( Define.GST_ENTER_WORLD_LOADING )
		rds.viewInfoMgr.onRoleEnterWorld()							# 通知角色信息设置管理器

		def onResourceReady() :										# 资源加载回调
			rds.statusMgr.changeStatus( Define.GST_IN_WORLD )		# 改变状态为在世界状态
			BigWorld.player().onEndInitialized()					# 告知角色结束初始化
		rds.resLoader.loadEnterWorldResource( onResourceReady )		# 加载世界资源
		rds.loginMgr.leave()

	# ---------------------------------------
	def requestEnterWorld( self ) :
		"""
		向服务器请求进入世界
		"""
		BigWorld.player().enterGame( self.__roleInfo.getID(), "" )

	def accountLogoff( self ) :
		"""
		请求退出登录，回到账号输入状态
		"""
		try :
			BigWorld.player().base.logoff()
			BigWorld.disconnect()
			self.__manualLogoff = True
			return True
		except :
			DEBUG_MSG( "accountLogoff fail!" )
		return False

	def roleLogoff( self ) :
		"""
		在游戏中请求退出到账号输入界面
		"""
		self.__manualLogoff = True
		BigWorld.disconnect()

	def logout( self ) :
		"""
		请求退出游戏（角色退出世界，回到角色选择状态）
		"""
		self.__serverSpaceID = BigWorld.player().spaceID
		BigWorld.player().base.logout()

	def __canLogout( self ):
		"""
		是否允许退出游戏
		"""
		player = BigWorld.player()
		if not player: return True

		if rds.statusMgr.isInWorld() and player.getState() == csdefine.ENTITY_STATE_FIGHT:
			player.statusMessage( csstatus.ROLE_QUIT_GAME_ON_FIGHTING )
			return False

		if rds.statusMgr.isInWorld() and isFalling( player ):
			player.statusMessage( csstatus.CANT_LOGOUT_WHEN_FALLING )
			return False

		return True

	def quitGame( self, isQuery = True ) :
		"""
		请求退出游戏（关闭客户端）
		"""
		player = BigWorld.player()

		if not self.__canLogout(): return

		if isQuery :
			self.__quitGameQuery()
			ECenter.fireEvent( "EVT_ON_LOST_CONTROL" )
		elif player is None or player.isPlayer():
			BigWorld.callback( 0.1, BigWorld.quit )
		else :
			self.accountLogoff()
			ECenter.fireEvent( "EVT_ON_BEFORE_GAME_QUIT" )
			BigWorld.callback( 0.1, BigWorld.quit )

	# -------------------------------------------------
	def isInKickoutStatus( self ):
		"""
		是否处于被服务器踢出状态
		"""
		return self.__inKickoutStatus

	def changeKickoutStatus( self, isKickout ):
		"""
		更改踢出状态
		"""
		self.__inKickoutStatus = isKickout

	#播放登陆CG相关
	def playVideo( self, fileName ):
		"""
		播放视频
		@param	fileName:	视频文件
		@type	fileName：	string
		"""
		self.__playingVideo = True
		csol.prepareVideo( fileName )
		csol.playVideo()
		csol.setVideoCallback( self.onVideoEvent )
	
	def onVideoEvent( self, event ):
		if event == "ON_COMPLETE":
			self.__playingVideo = False
			rds.roleCreator.onEnterSelectCamp()
			BigWorld.callback( 0.1, self.clearVideo )
	
	def clearVideo( self ):
		"""
		"""
		csol.clearVideo()
	
	def isInPlayVideo( self ):
		"""
		是否正在播放CG
		"""
		return self.__playingVideo
	
	def cancelVideo( self ):
		"""
		ESC取消CG播放
		"""
		csol.stopVideo()
		self.__playingVideo = False
		BigWorld.callback( 1, self.clearVideo )
		if rds.roleSelector.getLoginRolesCount() == 0:
			rds.roleCreator.onEnterSelectCamp()
	
# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
gameMgr = GameMgr.instance()
