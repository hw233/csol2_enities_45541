# -*- coding: gb18030 -*-

"""
实现不同语言版本的登录方式

2010.05.07: writen by huangyongwei
"""

"""
使用注意：
	① 所有关于某个装饰函数内用到的模块，都应该放到装饰类内 import。
	② 装饰函数类内不能使用 from XXX import * 的方式。
	   原因是，装饰器是在编译期（严格来说是 import 期）就使用了的，
	   因此被包装函数所属模块还没完全初始化完毕，不能用“*”来得到
	   它所有的成员。
	③ 对于访问被装饰方法的所属类的私有成员变量时，需要在私有变量的
	   前面加上“_类名”。原则上讲，装饰器应该可以直接访问被装饰方法
	   所属类的私有变量的，但目前还没找到更好的访问方法，因此需要带上
	   下划线和类名前缀。
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
	游戏启动是被引擎调用
	"""
	@staticmethod
	def locale_default() :
		"""
		GBK 版本
		需要在账号登录界面输入账号信息
		"""
		if not deco_l3Start.originalFunc() :
			return
		from GameMgr import gameMgr
		BigWorld.callback( 0.2, gameMgr.onGameStart )	# 直接进入账号登录界面

	@staticmethod
	def locale_big5() :
		"""
		BIG5 版本
		游戏启动完毕后直接进行登录
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
	游戏初始化完毕后通知各个相关模块进行资源加载
	"""
	__triggers = {}


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@classmethod
	def __registerTriggers( SELF ) :
		SELF.__triggers["EVT_ON_LOGIN_FAIL"] = SELF.__onLoginFail		# 登录失败事件
		SELF.__triggers["EVT_ON_LOGIN_WAIT"] = SELF.__onLoginWait		# 排队事件

		from event import EventCenter
		for key in SELF.__triggers :
			EventCenter.registerEvent( key, SELF )
		EventCenter.registerEvent( key, deco_gameMgrOnGameStart )

	# -------------------------------------------------
	@classmethod
	def __onLoginFail( SELF, msg ) :
		"""
		登录失败时被调用
		"""
		from MessageBox import showMessage, MB_OK
		showMessage( msg, "", MB_OK, lambda res : BigWorld.quit() )		# 点击确定按钮后，关闭客户端

	@classmethod
	def __onLoginWait( SELF, waitOrder, waitTime ) :
		"""
		需要排队时被调用
		"""
		from guis.loginuis.logindialog.FellInNotifier import FellInNotifier
		from config.client.msgboxtexts import Datas as mbmsgs

		if waitTime < 60 :
			msg = mbmsgs[0x0b42] % waitOrder							# "已提交您的登入申请。目前你排在第%i位，等待时间少于一分钟。"
		else :
			msg = mbmsgs[0x0b43] % ( waitOrder, int( waitTime / 60 ) )	# "已提交您的登入申请。目前你排在第%i位，大概需要等待%i分钟。"
		FellInNotifier.show( msg, "", lambda res : BigWorld.quit() )	# 放弃排队则关闭客户端


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def onEvent( SELF, eventName, *args ) :
		"""
		登录失败时，消息被触发
		"""
		SELF.__triggers[eventName]( *args )

	@staticmethod
	def locale_big5( gameMgr ) :
		"""
		BIG5 版本
		并不需要转换到登录账号状态
		"""
		from ResourceLoader import resLoader
		from ChatFacade import chatFacade

		resLoader.onGameStart()
		chatFacade.onGameStart()
		deco_gameMgrOnGameStart.__registerTriggers()

class deco_gameMgrOnLogined( MultiLngFuncDecorator ) :
	"""
	账号登录成功时被调用
	"""
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@classmethod
	def __progressNotifier( SELF, endCallback, progress ) :
		"""
		角色选择场景加载进度回调
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
		BIG5 版本
		对该版本的角色选择场景的加载进度放到启动游戏的第一个进度条中
		并且取消 GST_LOGIN 和 GST_ENTER_ROLESELECT_LOADING 这两个状态
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
	RoleSelector 的进入状态装饰
	"""
	@staticmethod
	def locale_big5( rselector, oldStatus ) :
		"""
		BIG5 版本
		对 BIG5 版本，可以允许从 GST_GAME_INIT 状态进入到角色选择状态
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
	断线时提示操作
	"""
	@staticmethod
	def locale_big5( rsbtn ) :
		"""
		BIG5 版本
		对 BIG5 版本，断线确定后，重启客户端
		"""
		BigWorld.quit()
		
# -----------------------------------------------------
class deco_gstOfflineOnEnter( MultiLngFuncDecorator ) :
	"""
	断线时提示改变
	"""
	@staticmethod
	def locale_big5( SELF, oldStatus ) :
		"""
		BIG5 版本
		对 BIG5 版本，断线后提示：伺服器已断线，请重新登入
		"""
		import csstatus
		import csstatus_msgs as StatusMsgs
		from gbref import rds
		from MessageBox import showMessage
		from MessageBox import MB_OK
		from StatusMgr import BaseStatus
		from StatusMgr import Offline
		from config.client.msgboxtexts import Datas as mbmsgs

		msg = mbmsgs[0x0163]															# "伺服器已断线，请重新登入"
		if rds.gameMgr.isInKickoutStatus():
			msg = StatusMsgs.getStatusInfo( csstatus.ACCOUNT_STATE_FORCE_LOGOUT ).msg
			rds.gameMgr.changeKickoutStatus( False )
		title = mbmsgs[0x0162]															# 标题：提示
		showMessage( msg, title, MB_OK, Offline._Offline__offlineQuery )
		SELF.__oldStatus = oldStatus
		BaseStatus.onEnter( SELF, oldStatus )


# --------------------------------------------------------------------
# guis/UIFactory
# --------------------------------------------------------------------
class deco_uiFactorySetLoginRoots( MultiLngFuncDecorator ) :
	"""
	获取登录需要的 UI
	"""
	@staticmethod
	def locale_big5( uiFactory ) :
		"""
		BIG5 版本
		不需要账号输入界面
		"""
		deco_uiFactorySetLoginRoots.originalFunc( uiFactory )
		uiFactory._UIFactory__loginRoots.pop( "loginDialog" )		# 去除登录账号输入界面

# --------------------------------------------------------------------
# guis/loginuis/roleselector
# --------------------------------------------------------------------
class deco_guiRoleSelectorInitialze( MultiLngFuncDecorator ) :
	"""
	初始化角色选择窗口
	"""
	@staticmethod
	def locale_big5( pySelector, wnd ) :
		"""
		BIG5 版本
		不需要“返回上页”按钮
		"""
		deco_guiRoleSelectorInitialze.originalFunc( pySelector, wnd )
		pySelector._RoleSelector__pyBtnOthers.top = pySelector._RoleSelector__pyBtnRename.top	# 下移“下一页”按钮
		pySelector._RoleSelector__pyBtnRename.top = pySelector._RoleSelector__pyBtnBack.top		# 下移“改名”按钮
		pySelector._RoleSelector__pyBtnBack.visible = False

class deco_guiRoleSelectorOnStatusChanged( MultiLngFuncDecorator ) :
	"""
	角色选择界面的状态改变通知
	"""
	@staticmethod
	def locale_big5( pySelector, oldStatus, newStatus ) :
		"""
		BIG5 版本
		对 BIG5 版本，可以允许从 GST_GAME_INIT 状态进入到角色选择状态
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
	繁体版道具商城初始化
	"""
	@staticmethod
	def locale_big5( uiFactory ) :
		from guis.general.specialshop.SpecialShop_Big5 import SpecialShop
		
		deco_uiFactorySetWorldRoots.originalFunc( uiFactory )
		uiFactory._UIFactory__worldRoots["specialShop"]		= ( SpecialShop, True )