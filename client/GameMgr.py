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
	���ַ���תΪʮ�����Ƹ�ʽ���ַ���
	����: s = "�����ַ���", �������� 'b2e2cad4d7d6b7fbb4ae'
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
		�����ȡһ������
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

		self.__gbRootSect = None											# ȫ�����ø� section
		self.__gbOptions = {}												# ȫ������
		self.__gbOptions["section"] = None									# ���� section
		self.__gbOptions["historyAccount"] = ""								# ǰһ�ε�¼���˺�

		self.__accountRootSect = None										# �˺����ø� section
		self.__accountOptions = {}											# ��ǰ��¼���˺�����
		self.__accountOptions["section"] = None								# ���� section
		self.__accountOptions["selRoleID"] = 0								# ǰһ�ν�����Ϸ�Ľ�ɫ����

		self.__roleRootSect = None											# ��ɫ���ø� section
		self.__roleOptions = {}												# ��ǰ��ɫ����
		self.__roleOptions["section"] = None								# ���� section
		self.__roleOptions["firstEnter"] = True								# ��¼�ý�ɫ�Ƿ��ǵ�һ�ν�������

		self.__servers = []													# �������б�
		self.__accountInfo = {}												# �˺���Ϣ
		self.__accountInfo["server"] = ""
		self.__accountInfo["accountName"] = ""
		self.__roleInfo = None												# ������Ϸ�Ľ�ɫ��Ϣ( RoleMaker.RoleInfo )

		self.__isInQuery = False											# ��ʱ�������Ƿ���йر�ѯ��
		self.__manualLogoff = False											# ��ʱ��������¼��ǰ�Ͽ��������ֹ��Ļ��Ƿ������߿���

		self.__serverSpaceID = 0											# ����ѡ��ǰ�Ľ�ɫ����ID
		self.__inKickoutStatus = False										# �Ƿ��ڱ��߳�״̬
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
		�˳���Ϸѯ��
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
		�����˺���ص�ȫ��������Ϣ
		"""
		self.__gbRootSect = ResMgr.openSection( "account", True )				# ����ȫ�ָ� section
		try :
			sect = ResMgr.openSection( "account/gbconfig.xml", True )			# ȫ�ֻ�������
			self.__gbOptions["section"] = sect
			historyAccount = sect["historyAccount"]								# ǰһ�ε�¼���˺���
			if historyAccount is None :
				sect.writeString( "historyAccount", "" )
			self.__gbOptions["historyAccount"] = sect.readString( "historyAccount" )
			sect.save()
		except IOError :
			ERROR_MSG( "save gbconfig failed!" )
		except TypeError :														# ����ļ����𻵣����ִ�е�����
			# ɾ�� gbconfig.xml ( Ŀǰû�취 )
			pass

	def __readAccountOptions( self ) :
		"""
		��ȡ��ǰ�˺�������Ϣ
		"""
		accountName = self.__accountInfo["accountName"]							# ��ǰ��¼���˺�����
		root = "account/" + accountName
		self.__accountRootSect = ResMgr.openSection( root, True )				# �����˺����ø� section

		try :
			config = "%s/option.xml" % root										# �˺Ż�������
			sect = ResMgr.openSection( config, True )
			self.__accountOptions["section"] = sect
			selRoleID = sect["selRoleID"]										# ǰһ�ν�����Ϸ�Ľ�ɫ����
			if selRoleID is None :
				sect.writeInt( "selRoleID", 0 )
			self.__accountOptions["selRoleID"] = sect.readInt( "selRoleID" )
			sect.save()
		except IOError :
			ERROR_MSG( "save option config failed!" )
		except TypeError :														# ����ļ����𻵣����ִ�е�����
			# ɾ�� option.xml ( Ŀǰû�취 )
			pass

	def __readRoleOptions( self ) :
		"""
		���ص�ǰ��ɫ������Ϣ
		"""
		accountName = self.__accountInfo["accountName"]							# ���ȵõ���ɫ�������˺���
		playerName = self.getCurrRoleHexName()									# ��ý�ɫ��
		root = "account/%s/%s" % ( accountName, playerName )
		self.__roleRootSect = ResMgr.openSection( root, True )					# ���ؽ�ɫ���ø� section

		try :
			config = "%s/options.xml" % root									# ��ɫ��������
			sect = ResMgr.openSection( config, True )							# ���� section
			self.__roleOptions["section"] = sect								# ���� section
			firstEnter = sect["firstEnter"]										# ��ȡ�Ƿ��һ�ν�����Ϸ����һ̨��������Ч��
			if firstEnter is None :												# ���û�иñ��
				self.__roleOptions["firstEnter" ] = True						# ���ʾ�ǵ�һ�� enterworld
				sect.writeBool( "firstEnter", False )							# д��ñ�ǣ���ʾ�����ǵ�һ�ν�����Ϸ
			else :
				self.__roleOptions["firstEnter" ] = False
			sect.save()
		except IOError :
			ERROR_MSG( "save option config failed!" )
		except TypeError :
			# ɾ�� option.xml ( Ŀǰû�취 )
			pass

	# -------------------------------------------------
	def __onKickout( self, statusID, msg ) :
		"""
		���������߳�ʱ����
		"""
		self.__inKickoutStatus = True


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def init( self ) :
		"""
		��Ϸ����ʱ������
		"""
		for tag, pyDs in rds.userPreferences["login"].items() :		# ��ȡ��Ϸ���� Option.xml �еĵ�¼��Ϣ�������� IP��
			try :
				server = ServerInfo( pyDs )
				self.__servers.append( server )						# ��ȡ�������б�
			except :
				DEBUG_MSG( "can't find server %s!" % tag )
		self.__readGlobalOptions()									# ��ȡ��ʷ��¼�˺�
		rds.resLoader.loadStartResource()
		rds.statusMgr.changeStatus( Define.GST_GAME_INIT )			# ���õ�ǰ����Ϸ״̬Ϊ��Ϸ��ʼ��״̬

	@reimpl_login.deco_gameMgrOnGameStart
	def onGameStart( self ) :
		"""
		��Ϸ�����ɹ��������˺�����ʱ������
		"""
		rds.statusMgr.changeStatus( Define.GST_LOGIN )				# ���õ�ǰ����Ϸ״̬Ϊ��¼״̬
		rds.resLoader.onGameStart()									# ֪ͨ��Դ������
		chatFacade.onGameStart()
		BackDownLoadMgr.checkAndDownLoad()

	# ---------------------------------------
	def onConnected( self ) :
		"""
		��¼�˺ųɹ�ʱ������
		"""
		INFO_MSG( "connect successily!" )

	def onDisconnected( self ) :
		"""
		��¼�˺�ʧ��ʱ������
		"""
		INFO_MSG( "onDisconnected!" )
		printStackTrace()
		if not self.__manualLogoff :										# �������Ͽ�
			rds.worldCamHandler.unfix()										# �Ͽ���ָ����
			rds.resLoader.onOffline()										# ������Դ��������ֹͣ����
			rds.statusMgr.changeStatus( Define.GST_OFFLINE )				# ����״̬
			rds.gameSettingMgr.onPlayerOffline()							# ֪ͨ��Ϸ���ù�����������
		else :																# ������󷵻ص�¼
			rds.statusMgr.changeStatus( Define.GST_LOGIN )					# ��״̬��Ϊ��¼״̬
		self.__manualLogoff = False											# ��������Ϊ���ֹ����ص�¼

	# ---------------------------------------
	@reimpl_login.deco_gameMgrOnLogined
	def onAccountLogined( self ) :
		"""
		�� BigWorld.player() ת��Ϊ Account ʱ������
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
		rds.resLoader.loadLoginSpace( True, readyCallback )						# ���ؽ�ɫѡ�񳡾�

	def onLogout( self ) :
		"""
		���ؽ�ɫѡ��player ��Ϊ Account ʱ������
		"""
		def loadResourceEnd() :													# ���ؽ�ɫѡ�񳡾�����ʱ������
			rds.statusMgr.changeStatus( Define.GST_ROLE_SELECT )
		rds.statusMgr.changeStatus( Define.GST_BACKTO_ROLESELECT_LOADING )
		rds.resLoader.loadLoginSpace( False, loadResourceEnd )
		try:
			BigWorld.releaseServerSpace( self.__serverSpaceID )	# �����ɫԭspace����
			self.__serverSpaceID = 0
		except ValueError, ve:
			print ve

	def getCurrRoleHexName( self ):
		"""
		��ȡ��ǰ��ɫ���ֵ�ʮ�����Ƶı���
		"""
		return _strToHex( self.__roleInfo.getName() )

	# ---------------------------------------
	def onBecomePlayer( self ) :
		"""
		������Ϸ�󴴽���ɫ�ɹ�ʱ������
		"""
		self.__roleOptions["section"].save()

	def onRoleEnterWorld( self ) :
		"""
		��ɫ��������ʱ������
		"""
		rds.resLoader.onRoleEnterWorld()
		rds.helper.courseHelper.onRoleEnterWorld()
		rds.shortcutMgr.onRoleEnterWorld()
		rds.ruisMgr.onRoleEnterWorld()
		chatFacade.onRoleEnterWorld()

	def onRoleLeaveWorld( self ) :
		"""
		��ɫ�뿪����ʱ������
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
		����ɫ�ӽ�ɫѡ�񵽽�������ʱ������
		"""
		rds.worldCamHandler.reset()								# ʹ�������Ĭ������
		rds.helper.courseHelper.onFirstSpaceReady()
		rds.helper.uiopHelper.onFirstSpaceReady()
		rds.helper.pixieHelper.onFirstSpaceReady()
		rds.ruisMgr.onRoleInitialized()							# ֪ͨ UI ������

	def onLeaveSpace( self ) :
		"""
		����ɫҪ�뿪ĳ������ʱ������
		"""
		rds.statusMgr.changeStatus( Define.GST_SPACE_LOADING )
		def readyCallback() :									# Ҫ������µ� space �Ƿ�������
			rds.statusMgr.changeStatus( Define.GST_IN_WORLD )	# ���������ϣ��򽫵�ǰ״̬������Ϊ IN_WORLD ״̬
		rds.resLoader.teleportSpace( readyCallback )			# �˳�ĳ�� space ��ζ��Ҫ����ĳ�� space

	def onLeaveArea( self ) :
		"""
		����ɫ�뿪ĳ������ʱ�����ã�ͬ��ͼ��������תʱ�����ã�
		"""
		rds.statusMgr.changeStatus( Define.GST_SPACE_LOADING )
		def readyCallback() :									# Ҫ������µ� space �Ƿ�������
			rds.statusMgr.changeStatus( Define.GST_IN_WORLD )	# ���������ϣ��򽫵�ǰ״̬������Ϊ IN_WORLD ״̬
		rds.resLoader.teleportArea( readyCallback )				# �˳�ĳ�� space ��ζ��Ҫ����ĳ�� space


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getGlobalRootSect( self ) :
		"""
		��ȡȫ�����ø� section
		"""
		return self.__gbRootSect

	def getAccountRootSect( self ) :
		"""
		��ȡ�˺����ø� section
		"""
		return self.__accountRootSect

	def getRoleRootSect( self ) :
		"""
		��ȡ��ɫ���ø� section
		"""
		return self.__roleRootSect

	# -------------------------------------------------
	def getGlobalOption( self, key ) :
		"""
		��ȡȫ���������ԣ�historyAccount
		"""
		assert key in self.__gbOptions
		return self.__gbOptions[key]

	def setGlobalOption( self, key, value ) :
		"""
		����ȫ����������
		"""
		if key not in self.__gbOptions :
			ERROR_MSG( "global option %s is not exitst!" % key )
		else :
			try:
				self.__gbOptions[key] = value
				self.__gbOptions["section"].writeString( key, str( value ) )
			except:
				self.deldir( "account" )
				ResMgr.purge( "account" )	#��ջ���
				self.__readGlobalOptions()		#ɾ�������´���account�ļ�

	def deldir( self, path):
		path2 = os.path.join("res",path) # ��res�ĵ�Ŀ¼
		if not os.path.exists( path2 ):
			return
		files = os.listdir( path ) #����Ŀ¼���ļ�

		for file in files:
			filedir = os.path.join( path2, file )
			if os.path.isfile( filedir ):
				os.remove( filedir )	#������ļ�ֱ��ɾ��
			else:
				try:
					os.rmdir( filedir )		#ֱ��ɾ����Ŀ¼
				except:
					newfiledir = filedir.split("res\\")[1]
					self.deldir( newfiledir )
		files = os.listdir( path ) #����Ŀ¼���ļ�
		if len( files ) == 0:
			os.rmdir( path2 )

	# --------------------------------------------------
	def getAccountOption( self, key ) :
		"""
		��ȡ�˺��������ԣ�selRoleID
		"""
		assert key in self.__accountOptions
		return self.__accountOptions[key]

	def setAccountOption( self, key, value ) :
		"""
		�����˺���������
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
		��ȡ��ɫ������Ϣ��firstEnter
		"""
		assert key in self.__roleOptions
		return self.__roleOptions.get( key, None )

	def setRoleOption( self, key, value ) :
		"""
		���ý�ɫ������Ϣ
		"""
		if key not in self.__roleOptions :
			ERROR_MSG( "account option %s is not exitst!" % key )
		else :
			self.__roleOptions[key] = value
			self.__roleOptions["section"].writeString( key, str( value ) )

	# -------------------------------------------------
	def getServers( self ) :
		"""
		��ȡ�������б�
		"""
		return self.__servers[:]

	def getCurrAccountInfo( self ) :
		"""
		��ȡ��ǰ��¼���˺���Ϣ: { "server" : ��ǰ������, "accountName" : ��ǰ�˺����� }
		"""
		return self.__accountInfo

	def getCurrRoleInfo( self ) :
		"""
		��ȡ��ǰ�ǽ�����Ϸ��ɫ��Ϣ( RoleMaker.RoleInfo )
		"""
		return self.__roleInfo

	# -------------------------------------------------
	def requestLogin( self, server, uname, psw, callback ) :
		"""
		�����¼�˺�
		"""
		class LoginInfo : pass
		loginInfo = LoginInfo()
		loginInfo.username = uname
		loginInfo.password = psw
		loginInfo.initialPosition   = Math.Vector3( 0, 0, 1 )
		loginInfo.initialDirection  = Math.Vector3( 0, 0, 0 )
		loginInfo.inactivityTimeout = 60.0
		self.__accountInfo["server"] = server						# ���õ�ǰ��¼�ķ�����
		self.__accountInfo["accountName"] = uname					# ���õ�ǰ��¼���˺���
		self.__readAccountOptions()									# ��ȡ��ǰ��¼�˺ŵ�������Ϣ
		self.__gbOptions["section"].save()
		host = server.host
		if host == "" :
			showMessage( 0x0001, "", MB_OK )
		else :
			BigWorld.connect( host, loginInfo, callback )

	# -------------------------------------------------
	def requestEnterGame( self, roleInfo ):
		"""
		���������Ϸ���������������֤
		"""
		self.__roleInfo = roleInfo
		BigWorld.player().requestEnterGame()

	def enterGame( self ) :
		"""
		���������Ϸ
		"""
		INFO_MSG( "enter game after verify!" )
		#self.__roleInfo = roleInfo
		self.__readRoleOptions()
		self.__accountOptions["section"].save()
		rds.statusMgr.changeStatus( Define.GST_ENTER_WORLD_LOADING )
		rds.viewInfoMgr.onRoleEnterWorld()							# ֪ͨ��ɫ��Ϣ���ù�����

		def onResourceReady() :										# ��Դ���ػص�
			rds.statusMgr.changeStatus( Define.GST_IN_WORLD )		# �ı�״̬Ϊ������״̬
			BigWorld.player().onEndInitialized()					# ��֪��ɫ������ʼ��
		rds.resLoader.loadEnterWorldResource( onResourceReady )		# ����������Դ
		rds.loginMgr.leave()

	# ---------------------------------------
	def requestEnterWorld( self ) :
		"""
		������������������
		"""
		BigWorld.player().enterGame( self.__roleInfo.getID(), "" )

	def accountLogoff( self ) :
		"""
		�����˳���¼���ص��˺�����״̬
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
		����Ϸ�������˳����˺��������
		"""
		self.__manualLogoff = True
		BigWorld.disconnect()

	def logout( self ) :
		"""
		�����˳���Ϸ����ɫ�˳����磬�ص���ɫѡ��״̬��
		"""
		self.__serverSpaceID = BigWorld.player().spaceID
		BigWorld.player().base.logout()

	def __canLogout( self ):
		"""
		�Ƿ������˳���Ϸ
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
		�����˳���Ϸ���رտͻ��ˣ�
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
		�Ƿ��ڱ��������߳�״̬
		"""
		return self.__inKickoutStatus

	def changeKickoutStatus( self, isKickout ):
		"""
		�����߳�״̬
		"""
		self.__inKickoutStatus = isKickout

	#���ŵ�½CG���
	def playVideo( self, fileName ):
		"""
		������Ƶ
		@param	fileName:	��Ƶ�ļ�
		@type	fileName��	string
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
		�Ƿ����ڲ���CG
		"""
		return self.__playingVideo
	
	def cancelVideo( self ):
		"""
		ESCȡ��CG����
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
