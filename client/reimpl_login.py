# -*- coding: gb18030 -*-

"""
ʵ�ֲ�ͬ���԰汾�ĵ�¼��ʽ

2010.05.07: writen by huangyongwei
"""

"""
ʹ��ע�⣺
	�� ���й���ĳ��װ�κ������õ���ģ�飬��Ӧ�÷ŵ�װ������ import��
	�� װ�κ������ڲ���ʹ�� from XXX import * �ķ�ʽ��
	   ԭ���ǣ�װ�������ڱ����ڣ��ϸ���˵�� import �ڣ���ʹ���˵ģ�
	   ��˱���װ��������ģ�黹û��ȫ��ʼ����ϣ������á�*�����õ�
	   �����еĳ�Ա��
	�� ���ڷ��ʱ�װ�η������������˽�г�Ա����ʱ����Ҫ��˽�б�����
	   ǰ����ϡ�_��������ԭ���Ͻ���װ����Ӧ�ÿ���ֱ�ӷ��ʱ�װ�η���
	   �������˽�б����ģ���Ŀǰ��û�ҵ����õķ��ʷ����������Ҫ����
	   �»��ߺ�����ǰ׺��
"""

import csol
import BigWorld
from bwdebug import *
from AbstractTemplates import MultiLngFuncDecorator
from Function import Functor

# --------------------------------------------------------------------
# love3
# --------------------------------------------------------------------
class deco_l3Start( MultiLngFuncDecorator ) :
	"""
	��Ϸ�����Ǳ��������
	"""
	@staticmethod
	def locale_default() :
		"""
		GBK �汾
		��Ҫ���˺ŵ�¼���������˺���Ϣ
		"""
		if not deco_l3Start.originalFunc() :
			return
		from GameMgr import gameMgr
		BigWorld.callback( 0.2, gameMgr.onGameStart )	# ֱ�ӽ����˺ŵ�¼����

	@staticmethod
	def locale_big5() :
		"""
		BIG5 �汾
		��Ϸ������Ϻ�ֱ�ӽ��е�¼
		"""
		if not deco_l3Start.originalFunc() :
			return
		from LoginMgr import loginer
		from GameMgr import gameMgr
		gameMgr.onGameStart()
		servers = gameMgr.getServers()
		if len( servers ) == 0 :
			ERROR_MSG( "no server to choice for login!" )
			return
		server = servers[0]
		userName = csol.getTwLoginId()
		passwd = csol.getTwLoginKey()
		loginer.requestLogin( server, userName, passwd )


# --------------------------------------------------------------------
# GameMgr
# --------------------------------------------------------------------
class deco_gameMgrOnGameStart( MultiLngFuncDecorator ) :
	"""
	��Ϸ��ʼ����Ϻ�֪ͨ�������ģ�������Դ����
	"""
	__triggers = {}


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@classmethod
	def __registerTriggers( SELF ) :
		SELF.__triggers["EVT_ON_LOGIN_FAIL"] = SELF.__onLoginFail		# ��¼ʧ���¼�
		SELF.__triggers["EVT_ON_LOGIN_WAIT"] = SELF.__onLoginWait		# �Ŷ��¼�

		from event import EventCenter
		for key in SELF.__triggers :
			EventCenter.registerEvent( key, SELF )
		EventCenter.registerEvent( key, deco_gameMgrOnGameStart )

	# -------------------------------------------------
	@classmethod
	def __onLoginFail( SELF, msg ) :
		"""
		��¼ʧ��ʱ������
		"""
		from MessageBox import showMessage, MB_OK
		showMessage( msg, "", MB_OK, lambda res : BigWorld.quit() )		# ���ȷ����ť�󣬹رտͻ���

	@classmethod
	def __onLoginWait( SELF, waitOrder, waitTime ) :
		"""
		��Ҫ�Ŷ�ʱ������
		"""
		from guis.loginuis.logindialog.FellInNotifier import FellInNotifier
		from config.client.msgboxtexts import Datas as mbmsgs

		if waitTime < 60 :
			msg = mbmsgs[0x0b42] % waitOrder							# "���ύ���ĵ������롣Ŀǰ�����ڵ�%iλ���ȴ�ʱ������һ���ӡ�"
		else :
			msg = mbmsgs[0x0b43] % ( waitOrder, int( waitTime / 60 ) )	# "���ύ���ĵ������롣Ŀǰ�����ڵ�%iλ�������Ҫ�ȴ�%i���ӡ�"
		FellInNotifier.show( msg, "", lambda res : BigWorld.quit() )	# �����Ŷ���رտͻ���


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def onEvent( SELF, eventName, *args ) :
		"""
		��¼ʧ��ʱ����Ϣ������
		"""
		SELF.__triggers[eventName]( *args )

	@staticmethod
	def locale_big5( gameMgr ) :
		"""
		BIG5 �汾
		������Ҫת������¼�˺�״̬
		"""
		from ResourceLoader import resLoader
		from ChatFacade import chatFacade

		resLoader.onGameStart()
		chatFacade.onGameStart()
		deco_gameMgrOnGameStart.__registerTriggers()

class deco_gameMgrOnLogined( MultiLngFuncDecorator ) :
	"""
	�˺ŵ�¼�ɹ�ʱ������
	"""
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@classmethod
	def __progressNotifier( SELF, endCallback, progress ) :
		"""
		��ɫѡ�񳡾����ؽ��Ȼص�
		"""
		if progress >= 1.0 :
			endCallback()
			return
		BigWorld.setCustomProgress( progress )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def onEvent( SELF, eventName, resLoader, endCallback ) :
		func = Functor( SELF.__progressNotifier, endCallback )
		resLoader.setNotifier( func )

	# -------------------------------------------------
	@staticmethod
	def locale_big5( gameMgr ) :
		"""
		BIG5 �汾
		�Ըð汾�Ľ�ɫѡ�񳡾��ļ��ؽ��ȷŵ�������Ϸ�ĵ�һ����������
		����ȡ�� GST_LOGIN �� GST_ENTER_ROLESELECT_LOADING ������״̬
		"""
		import Define
		from ResourceLoader import resLoader
		from StatusMgr import statusMgr
		from LoginMgr import loginMgr
		from event import EventCenter as ECenter

		def readyCallback() :
			statusMgr.changeStatus( Define.GST_ROLE_SELECT )
			BigWorld.callback( 0.5, Functor( BigWorld.setCustomProgress, 1.0 ) )
			ECenter.unregisterEvent( "EVT_ON_BEGIN_ENTER_RS_LOADING", deco_gameMgrOnLogined )
			try :
				name = BigWorld.getSpaceName( gameMgr._GameMgr__serverSpaceID )
				BigWorld.releaseServerSpace( gameMgr._GameMgr__serverSpaceID )
				gameMgr._GameMgr__serverSpaceID = 0
			except ValueError :
				pass
		ECenter.registerEvent( "EVT_ON_BEGIN_ENTER_RS_LOADING", deco_gameMgrOnLogined )
		loginMgr.enter()
		resLoader.loadLoginSpace( True, readyCallback )


# --------------------------------------------------------------------
# StatusMgr
# --------------------------------------------------------------------
class deco_gstRSEnter( MultiLngFuncDecorator ) :
	"""
	RoleSelector �Ľ���״̬װ��
	"""
	@staticmethod
	def locale_big5( rselector, oldStatus ) :
		"""
		BIG5 �汾
		�� BIG5 �汾����������� GST_GAME_INIT ״̬���뵽��ɫѡ��״̬
		"""
		import Define
		from LoginMgr import roleSelector
		from StatusMgr import BaseStatus

		assert oldStatus == Define.GST_GAME_INIT or \
			oldStatus == Define.GST_BACKTO_ROLESELECT_LOADING or \
			oldStatus == Define.GST_ROLE_CREATE
		roleSelector.onEnter()
		BaseStatus.onEnter( rselector, oldStatus )

# -----------------------------------------------------
class deco_gstOfflineQuery( MultiLngFuncDecorator ) :
	"""
	����ʱ��ʾ����
	"""
	@staticmethod
	def locale_big5( rsbtn ) :
		"""
		BIG5 �汾
		�� BIG5 �汾������ȷ���������ͻ���
		"""
		BigWorld.quit()
		
# -----------------------------------------------------
class deco_gstOfflineOnEnter( MultiLngFuncDecorator ) :
	"""
	����ʱ��ʾ�ı�
	"""
	@staticmethod
	def locale_big5( SELF, oldStatus ) :
		"""
		BIG5 �汾
		�� BIG5 �汾�����ߺ���ʾ���ŷ����Ѷ��ߣ������µ���
		"""
		import csstatus
		import csstatus_msgs as StatusMsgs
		from gbref import rds
		from MessageBox import showMessage
		from MessageBox import MB_OK
		from StatusMgr import BaseStatus
		from StatusMgr import Offline
		from config.client.msgboxtexts import Datas as mbmsgs

		msg = mbmsgs[0x0163]															# "�ŷ����Ѷ��ߣ������µ���"
		if rds.gameMgr.isInKickoutStatus():
			msg = StatusMsgs.getStatusInfo( csstatus.ACCOUNT_STATE_FORCE_LOGOUT ).msg
			rds.gameMgr.changeKickoutStatus( False )
		title = mbmsgs[0x0162]															# ���⣺��ʾ
		showMessage( msg, title, MB_OK, Offline._Offline__offlineQuery )
		SELF.__oldStatus = oldStatus
		BaseStatus.onEnter( SELF, oldStatus )


# --------------------------------------------------------------------
# guis/UIFactory
# --------------------------------------------------------------------
class deco_uiFactorySetLoginRoots( MultiLngFuncDecorator ) :
	"""
	��ȡ��¼��Ҫ�� UI
	"""
	@staticmethod
	def locale_big5( uiFactory ) :
		"""
		BIG5 �汾
		����Ҫ�˺��������
		"""
		deco_uiFactorySetLoginRoots.originalFunc( uiFactory )
		uiFactory._UIFactory__loginRoots.pop( "loginDialog" )		# ȥ����¼�˺��������

# --------------------------------------------------------------------
# guis/loginuis/roleselector
# --------------------------------------------------------------------
class deco_guiRoleSelectorInitialze( MultiLngFuncDecorator ) :
	"""
	��ʼ����ɫѡ�񴰿�
	"""
	@staticmethod
	def locale_big5( pySelector, wnd ) :
		"""
		BIG5 �汾
		����Ҫ��������ҳ����ť
		"""
		deco_guiRoleSelectorInitialze.originalFunc( pySelector, wnd )
		pySelector._RoleSelector__pyBtnOthers.top = pySelector._RoleSelector__pyBtnRename.top	# ���ơ���һҳ����ť
		pySelector._RoleSelector__pyBtnRename.top = pySelector._RoleSelector__pyBtnBack.top		# ���ơ���������ť
		pySelector._RoleSelector__pyBtnBack.visible = False

class deco_guiRoleSelectorOnStatusChanged( MultiLngFuncDecorator ) :
	"""
	��ɫѡ������״̬�ı�֪ͨ
	"""
	@staticmethod
	def locale_big5( pySelector, oldStatus, newStatus ) :
		"""
		BIG5 �汾
		�� BIG5 �汾����������� GST_GAME_INIT ״̬���뵽��ɫѡ��״̬
		"""
		import Define

		if newStatus == Define.GST_ROLE_SELECT and \
			( oldStatus == Define.GST_GAME_INIT or \
			oldStatus == Define.GST_BACKTO_ROLESELECT_LOADING or \
			oldStatus == Define.GST_ROLE_CREATE ) :
				pySelector.show()
		elif pySelector.visible and newStatus != Define.GST_OFFLINE :
			pySelector.hide()

class deco_uiFactorySetWorldRoots( MultiLngFuncDecorator ):
	"""
	���������̳ǳ�ʼ��
	"""
	@staticmethod
	def locale_big5( uiFactory ) :
		from guis.general.specialshop.SpecialShop_Big5 import SpecialShop
		
		deco_uiFactorySetWorldRoots.originalFunc( uiFactory )
		uiFactory._UIFactory__worldRoots["specialShop"]		= ( SpecialShop, True )