# -*- coding: gb18030 -*-
#
# $Id: StatusMgr.py,v 1.28 2008-08-25 04:47:48 huangyongwei Exp $

"""
implement status manager

--2008/01/10 : writen by huangyongwei
"""

import BigWorld
import csol
import Math
import GUI
import Define
import csstatus
import csconst
import Const
import event.EventCenter as ECenter
import csstatus_msgs as StatusMsgs
import reimpl_login

from bwdebug import *
from Function import Functor
from keys import *
from gbref import rds

from LoginMgr import loginer
from LoginMgr import roleSelector
from LoginMgr import roleCreator

from MessageBox import *
from guis.ScreenViewer import ScreenViewer
from config.client.msgboxtexts import Datas as mbmsgs

# --------------------------------------------------------------------
# implement status base class
# --------------------------------------------------------------------
class BaseStatus :
	def __init__( self ) :
		self.__subStatus = None						# 子状态，该子状态必需继承于 BaseStatus
													# 子状态常用于控制全局鼠标、键盘消息


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnter( self, oldStatus ) :
		INFO_MSG( "you have entered %r Status!" % self.__class__.__name__ )

	def onLeave( self, newStatus ) :
		pass

	# -------------------------------------------------
	def setToSubStatus( self, subStatus ) :
		"""
		设置当前子状态
		"""
		if self.__subStatus is not None :
			ERROR_MSG( "current is in %r status, it must be cleared at first!" % self.__subStatus.__class__.__name__ )
		else :
			assert isinstance( subStatus, BaseStatus ), "class of substatus instance must inhires from BaseStatus!"
			self.__subStatus = subStatus
			self.__subStatus.onEnter( None )

	def leaveSubStatus( self, clsSubStatus ) :
		"""
		离开当前子状态
		"""
		if isinstance( self.__subStatus, clsSubStatus ) :
			subStatus = self.__subStatus
			self.__subStatus = None
			subStatus.onLeave( None )

	def isInSubStatus( self, clsSstatus ) :
		"""
		指出当前是否处于指定的子状态中
		"""
		return isinstance( self.__subStatus, clsSstatus )

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		if self.__subStatus is None : return False
		return self.__subStatus.handleKeyEvent( down, key, mods )

	def handleMouseEvent( self, dx, dy, dz ) :
		if self.__subStatus is None : return False
		return self.__subStatus.handleMouseEvent( dx, dy, dz )

	def handleAxisEvent( self, axis, value, dTime ) :
		if self.__subStatus is None : return False
		return self.__subStatus.handleAxisEvent( axis, value, dTime )


# --------------------------------------------------------------------
# implement status in login
# --------------------------------------------------------------------
class GameInit( BaseStatus ) :
	def __init__( self ) :
		BaseStatus.__init__( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnter( self, oldStatus ) :
		BaseStatus.onEnter( self, oldStatus )

	def onLeave( self, newStatus ) :
		if rds.loadingScreenGUI in GUI.roots() :
			GUI.delRoot( rds.loadingScreenGUI )
		del rds.loadingScreenGUI

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		if not BaseStatus.handleKeyEvent( self, down, key, mods ) :
			return rds.uiHandlerMgr.handleKeyEvent( down, key, mods )
		return True


# --------------------------------------------------------------------
# implement status in login
# --------------------------------------------------------------------
class Login( BaseStatus ) :
	def __init__( self ) :
		BaseStatus.__init__( self )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnter( self, oldStatus ) :
		rds.soundMgr.switchMusic( "bgm/mainmap_loading" )						# play music in login state
		rds.loginer.onEnter()
		BaseStatus.onEnter( self, oldStatus )

	def onLeave( self, newStatus ) :
		rds.loginer.onLeave()

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		if BaseStatus.handleKeyEvent( self, down, key, mods ) :
			return True

		result = False
		if rds.uiHandlerMgr.handleKeyEvent( down, key, mods ) :				# distribute message to all uis
			result = True
		elif rds.shortcutMgr.handleKeyEvent( down, key, mods ) :			# handle global shortcuts
			result = True
		rds.shortcutMgr.releaseShortcut( down, key, mods )
		return result

	def handleMouseEvent( self, dx, dy, dz ) :
		if BaseStatus.handleMouseEvent( self, dx, dy, dz ) :
			return True

		cursor = GUI.mcursor()
		if cursor.visible and rds.uiHandlerMgr.handleMouseEvent( dx, dy, dz ) :
			return True
		return False


# --------------------------------------------------------------------
# implement enter role select loading status
# --------------------------------------------------------------------
class EnterRoleSelectLoading( BaseStatus ) :
	def __init__( self ) :
		BaseStatus.__init__( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnter( self, oldStatus ) :
		assert oldStatus == Define.GST_LOGIN
		rds.loginMgr.enter()
		BaseStatus.onEnter( self, oldStatus )

	def onLeave( self, newStatus ) :
		pass

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		if BaseStatus.handleKeyEvent( self, down, key, mods ) :
			return True
		return rds.uiHandlerMgr.handleKeyEvent( down, key, mods )


# --------------------------------------------------------------------
# implement status in role selector
# --------------------------------------------------------------------
class RoleSelect( BaseStatus ) :
	def __init__( self ) :
		BaseStatus.__init__( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@reimpl_login.deco_gstRSEnter
	def onEnter( self, oldStatus ) :
		assert oldStatus == Define.GST_ENTER_ROLESELECT_LOADING or \
			oldStatus == Define.GST_BACKTO_ROLESELECT_LOADING or \
			oldStatus == Define.GST_ROLE_CREATE
		rds.roleSelector.onEnter()
		rds.loginer.stopCamera()
		BaseStatus.onEnter( self, oldStatus )
		if roleSelector.getLoginRolesCount() == 0 and ( not rds.roleCreator.onBackToSelector ) :
			rds.gameMgr.playVideo( Define.LOGIN_CG_PATH )
		
	def onLeave( self, newStatus ) :
		if newStatus != Define.GST_ROLE_CREATE and \
			newStatus != Define.GST_OFFLINE :
				rds.loginMgr.leave()
		rds.roleSelector.onLeave( newStatus )

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		if BaseStatus.handleKeyEvent( self, down, key, mods ) :
			return True
		if rds.gameMgr.isInPlayVideo(): 
			if down and key == KEY_ESCAPE:
				BigWorld.callback( 0.2, rds.gameMgr.cancelVideo)
		result = False
		if rds.uiHandlerMgr.handleKeyEvent( down, key, mods ) :				# distribute message to all uis
			result = True
		elif rds.shortcutMgr.handleKeyEvent( down, key, mods ) :			# handle global shortcuts
			result = True
		rds.shortcutMgr.releaseShortcut( down, key, mods )
		
		return result

	def handleMouseEvent( self, dx, dy, dz ) :
		if BaseStatus.handleMouseEvent( self, dx, dy, dz ) :
			return True

		cursor = GUI.mcursor()
		if cursor.visible and rds.uiHandlerMgr.handleMouseEvent( dx, dy, dz ) :
			return True
		return False


# --------------------------------------------------------------------
# implement back to role select loading status
# --------------------------------------------------------------------
class BacktoRoleSelectLoading( BaseStatus ) :
	def __init__( self ) :
		BaseStatus.__init__( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnter( self, oldStatus ) :
		assert oldStatus == Define.GST_IN_WORLD
		rds.loginMgr.enter()
		BaseStatus.onEnter( self, oldStatus )

	def onLeave( self, newStatus ) :
		pass

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		if BaseStatus.handleKeyEvent( self, down, key, mods ) :
			return True
		return rds.uiHandlerMgr.handleKeyEvent( down, key, mods )



# --------------------------------------------------------------------
# implement login status
# --------------------------------------------------------------------
class RoleCreate( BaseStatus ) :
	def __init__( self ) :
		BaseStatus.__init__( self )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnter( self, oldStatus ) :
		assert oldStatus == Define.GST_ROLE_SELECT
		rds.gameMgr.playVideo( Define.LOGIN_CG_PATH )
		rds.roleCreator.onEnterSelectCamp()
		BaseStatus.onEnter( self, oldStatus )

	def onLeave( self, newStatus ) :
		rds.roleCreator.onLeave()

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		if BaseStatus.handleKeyEvent( self, down, key, mods ) :
			return True
		if rds.gameMgr.isInPlayVideo(): 
			if down and key == KEY_ESCAPE:
				BigWorld.callback( 0.2, rds.gameMgr.cancelVideo)
		result = False
		if rds.uiHandlerMgr.handleKeyEvent( down, key, mods ) :				# distribute message to all uis
			result = True
		if rds.roleCreator.handleKeyEvent( down, key, mods ) :				# 相机
			result = True
		elif rds.shortcutMgr.handleKeyEvent( down, key, mods ) :			# handle global shortcuts
			result = True
		rds.shortcutMgr.releaseShortcut( down, key, mods )
		return result

	def handleMouseEvent( self, dx, dy, dz ) :
		if BaseStatus.handleMouseEvent( self, dx, dy, dz ) :
			return True

		cursor = GUI.mcursor()
		if cursor.visible and rds.uiHandlerMgr.handleMouseEvent( dx, dy, dz ) :
			return True
		if rds.roleCreator.handleMouseEvent( dx, dy, dz ) :
			return True
		return False


# --------------------------------------------------------------------
# implement enter world loading status
# --------------------------------------------------------------------
class EnterWorldLoading( BaseStatus ) :
	def __init__( self ) :
		BaseStatus.__init__( self )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnter( self, oldStatus ) :
		BaseStatus.onEnter( self, oldStatus )

	def onLeave( self, newStatus ) :
		BigWorld.callback( 0.2, BigWorld.clearWeaponModelList )

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		if BaseStatus.handleKeyEvent( self, down, key, mods ) :
			return True
		return rds.uiHandlerMgr.handleKeyEvent( down, key, mods )


# --------------------------------------------------------------------
# implement login status
# --------------------------------------------------------------------
class InWorld( BaseStatus ) :
	def __init__( self ) :
		BaseStatus.__init__( self )
		self.__oldArea = None										# 玩家跳转前所处的区域
		self.__areaDetectTimerID = 0								# 区域侦测 callback ID
		self.__areaChanged = False									# 记录区域是否改变
		self.__tmpPos = None										# 记录玩家离开某个区域时的位置
		self.__oldSpaceNumber = -1									# 记录上一次所在的副本唯一id
		self.__currArea = None
		self.__mousePressEventList = []								# 记录鼠标按下事件列表


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __resetEntitiesFilter( self ):
		"""
		设置所有实体的Filter
		"""
		for ent in BigWorld.entities.values():
			ent.setFilter()

	# -------------------------------------------------
	def __enterArea( self, newArea ) :
		"""
		让玩家进入新区域
		"""
		BigWorld.player().onEnterArea( newArea )
		self.__currArea = newArea

	def __detectArea( self ) :
		"""
		侦测玩家当前所在区域
		"""
		player = BigWorld.player()
		self.__areaDetectTimerID = BigWorld.callback( 2,self.__detectArea )
		if not player or not player.isPlayer() : return
		spaceLabel = BigWorld.player().getSpaceLabel()
		newArea = rds.mapMgr.getArea( spaceLabel, player.position )
		if newArea is None : return										# 区域有问题（没错的情况下不会出现）

		if self.__oldArea is None :										# 角色刚刚登录进入世界，马上触发区域变换
			self.__areaChanged = False
			self.__enterArea( newArea )									# 通知玩家进入了一个新的区域
			self.__oldArea = newArea									# 将临时旧区域设置为当前区域，以备被下次判断
			return

		if self.__oldArea.spaceLabel != spaceLabel : 					# 如果角色跳转了 space，马上触发区域变换
			self.__areaChanged = False
			self.__enterArea( newArea )									# 通知玩家进入了一个新的区域
			self.__oldArea = newArea									# 将临时旧区域设置为当前区域，以备下次判断
			return

		if self.__oldArea.wholeArea == newArea.wholeArea and \
			self.__oldArea.isSubArea() and \
			newArea.isSubArea() and \
			self.__oldArea != newArea and \
			self.__oldArea.name == newArea.name :						# 如果新旧区域是同名区域( 同一个大区域下的同名区域视为同一个区域 )
				self.__areaChanged = False								# 将区域改变参数设置为 False，防止下一个 tick 到来时，触发下面的区域变换
				self.__oldArea = newArea								# 则，将临时旧区域设置为当前区域，以备下次判断
				return													# 如果是同名区域更换，则不发送区域转换通知
																		#（这是策划要求，因为有可能一个区域分两块－－即两个闭合区间）

		if self.__oldArea == newArea :									# 如果区域没变更
			sn = BigWorld.getSpaceDataFirstForKey( player.spaceID, \
				csconst.SPACE_SPACEDATA_NUMBER )
			if sn != self.__oldSpaceNumber:								# 如果已经进入另一个相同地图副本
				self.__oldSpaceNumber = sn
				self.__areaChanged = False
				self.__enterArea( newArea )
				self.__oldArea = newArea
			elif not self.__areaChanged :								# 如果区域没有改变
				self.__tmpPos = Math.Vector3( player.position )			# 则记录下玩家的位置
			elif self.__tmpPos.distTo( player.position ) > 15.0 :		# 否则，判断是否超出了临界区
				self.__areaChanged = False
				self.__enterArea( newArea )								# 通知玩家进入了一个新的区域
				self.__oldArea = newArea
		else :															# 如果区域变更
			self.__areaChanged = True									# 区域已经更换，但不能马上触发区域变换函数
			self.__oldArea = newArea									# 因为要做缓冲处理（避免角色在临界区来回走动时，频繁触发区域更换）


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnter( self, oldStatus ) :
		"""
		"""
		player = BigWorld.player()
		if oldStatus == Define.GST_ENTER_WORLD_LOADING:
			player.onFirstSpaceReady()
		elif oldStatus == Define.GST_SPACE_LOADING:
			pass
			#player.onTeleportReady()
		else :
			raise "error old status '%s'" % statusMgr.statusLabel( oldStatus )

		self.__tmpPos = Math.Vector3( player.position )								# 则记录下玩家的位置

		BigWorld.dcursor().yaw = player.yaw
		if not rds.worldCamHandler.isYawLocked:
			yaw = player.yaw + math.pi
			rds.worldCamHandler.cameraShell.setYaw( yaw, True )							# 让相机照向与角色面向保持一致
		self.__resetEntitiesFilter()
		BaseStatus.onEnter( self, oldStatus )
		player.playSpaceCameraEvent()
		self.__areaDetectTimerID = BigWorld.callback( 0.1, self.__detectArea )		# 启动区域侦测
		player.enterYXLMChangeCamera()            # 进入英雄联盟副本 改变镜头
		player.checkTelepoertFly()  #检查是否需要继续进入飞翔传送
	def onLeave( self, newStatus ) :
		BigWorld.cancelCallback( self.__areaDetectTimerID )
		rds.worldCamHandler.unfix()

	def getCurrArea( self ):
		"""
		获得当前场景Area
		"""
		return self.__currArea

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		if BaseStatus.handleKeyEvent( self, down, key, mods ) :
			return True
		if getattr( BigWorld.player(), "playingVideo", False ) == True:
			if down and key == KEY_ESCAPE:
				csol.stopVideo()
				BigWorld.player().playingVideo = False
				BigWorld.player().cell.onCompleteVideo() #add by wuxo 2011-11-26
				BigWorld.callback(0.1, BigWorld.player().clearVideo )
			return True

		uiHandled, camHandled, scHandled = False, False, False
		uiHandled = bool( rds.uiHandlerMgr.handleKeyEvent( down, key, mods ) )
		if not uiHandled:
			camHandled = bool( rds.worldCamHandler.handleKeyEvent( down, key, mods ) )
		if not ( uiHandled or camHandled ): # 如果前两者都不处理，那么交给shortcutMgr处理
			scHandled = bool( rds.shortcutMgr.handleKeyEvent( down, key, mods ) )

		if not scHandled: rds.shortcutMgr.releaseShortcut( down, key, mods )

		if key in [ KEY_LEFTMOUSE, KEY_RIGHTMOUSE ]:
			pyRoot = rds.ruisMgr.getMouseHitRoot()
			self.__handleMousePressEvent( down, key, mods, pyRoot )
			
		# 任何参与方处理了，那么就认定此事件被处理了
		return uiHandled or camHandled or scHandled

	def __handleMousePressEvent( self, down, key, mods, pyRoot ):
		"""
		处理鼠标按下事件
		"""
		if down and key in [ KEY_LEFTMOUSE, KEY_RIGHTMOUSE ]:
			if self.__mousePressEventList:
				length = len( self.__mousePressEventList )
				lastEventTuple = self.__mousePressEventList[ length - 1 ]
				if lastEventTuple:
					lastType = lastEventTuple[ 0 ]
					lastPyRoot = lastEventTuple[ 1 ]
					lastDown = lastEventTuple[ 2 ]
					lastKey = lastEventTuple[ 3 ]
					if lastDown:
						if lastType:
							#重置鼠标状态
							rds.uiHandlerMgr.resetMouseState()
						else:
							#重置鼠标状态
							rds.worldCamHandler.resetMouseState()
					else:
						if lastType and not pyRoot:
							rds.uiHandlerMgr.onLeaveUIArea( lastPyRoot, lastDown, lastKey )
						elif not lastType and pyRoot:
							rds.uiHandlerMgr.onEnterUIArea( pyRoot, down, key )
					del self.__mousePressEventList[ length - 1 ]
			else:
				if pyRoot:
					rds.uiHandlerMgr.onEnterUIArea( pyRoot, down, key )
					
		elif not down and key in [ KEY_LEFTMOUSE, KEY_RIGHTMOUSE ]:
			if self.__mousePressEventList:
				length = len( self.__mousePressEventList )
				lastEventTuple = self.__mousePressEventList[ length - 1 ]
				if lastEventTuple:
					lastType = lastEventTuple[ 0 ]
					lastPyRoot = lastEventTuple[ 1 ]
					lastDown = lastEventTuple[ 2 ]
					lastKey = lastEventTuple[ 3 ]
					if lastDown:
						if lastType and not pyRoot:
							rds.uiHandlerMgr.onLeaveUIArea( lastPyRoot, lastDown, lastKey )
						elif not lastType and pyRoot:
							rds.uiHandlerMgr.onEnterUIArea( pyRoot, down, key )
					del self.__mousePressEventList[ length - 1 ]
			else:
				if pyRoot:
					rds.uiHandlerMgr.onEnterUIArea( pyRoot, down, key )
					
		if pyRoot and pyRoot.hitable:
			eventTuple = ( Const.MOUSE_HAADLED_BY_UI, pyRoot, down, key )
		elif not pyRoot:
			eventTuple = ( Const.MOUSE_HAADLED_BY_NOT_UI, None, down, key )
		self.__mousePressEventList.append( eventTuple )
					
	def handleMouseEvent( self, dx, dy, dz ) :
		if BaseStatus.handleMouseEvent( self, dx, dy, dz ) :
			return True

		if not rds.worldCamHandler.fixed() and \
			rds.uiHandlerMgr.handleMouseEvent( dx, dy, dz ) :
				return True

		return rds.worldCamHandler.handleMouseEvent( dx, dy, dz )

	def handleAxisEvent( self, axis, value, dTime ) :
		if BaseStatus.handleAxisEvent( self, axis, value, dTime ) :
			return True
		return GUI.handleAxisEvent( axis, value, dTime )

	def getMousePressEventList( self ):
		"""
		获取鼠标按下事件列表
		"""
		return self.__mousePressEventList
		
	


# --------------------------------------------------------------------
# implement teleport space status
# --------------------------------------------------------------------
class TeleportSpace( BaseStatus ) :
	def __init__( self ) :
		BaseStatus.__init__( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEnter( self, oldStatus ) :
		assert oldStatus == Define.GST_IN_WORLD, "error old status: %s!" % statusMgr.statusLabel( oldStatus )
		BaseStatus.onEnter( self, oldStatus )

	def onLeave( self, newStatus ) :
		pass

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		if BaseStatus.handleKeyEvent( self, down, key, mods ) :
			return True

		if getattr( BigWorld.player(), "playingVideo", False ) == True: #add by wuxo 2011-12-14
			if down and key == KEY_ESCAPE:
				csol.stopVideo()
				BigWorld.player().playingVideo = False
				BigWorld.player().cell.onCompleteVideo() #add by wuxo 2011-11-26
				BigWorld.callback(0.1, BigWorld.player().clearVideo )
			return True
		result = False
		if rds.uiHandlerMgr.handleKeyEvent( down, key, mods ) :
			result = True
		elif rds.shortcutMgr.handleKeyEvent( down, key, mods ) :
			result = True
		rds.shortcutMgr.releaseShortcut( down, key, mods )
		return result


# --------------------------------------------------------------------
# implement teleport space status
# --------------------------------------------------------------------
class Offline( BaseStatus ) :
	def __init__( self ) :
		BaseStatus.__init__( self )
		self.__oldStatus = Define.GST_NONE


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	@reimpl_login.deco_gstOfflineQuery
	def __offlineQuery( rsbtn ) :
		"""
		断线询问
		"""
		rds.statusMgr.changeStatus( Define.GST_LOGIN )
		try : BigWorld.releaseServerSpace( BigWorld.cameraSpaceID() )
		except ValueError : pass

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@reimpl_login.deco_gstOfflineOnEnter
	def onEnter( self, oldStatus ) :
		msg = mbmsgs[0x0161]															# "服务器断开，请返回登录！"
		if rds.gameMgr.isInKickoutStatus():
			msg = StatusMsgs.getStatusInfo( csstatus.ACCOUNT_STATE_FORCE_LOGOUT ).msg
			rds.gameMgr.changeKickoutStatus( False )

		title = mbmsgs[0x0162]															# 标题：提示
		py_box = showMessage( msg, title, MB_OK, Offline.__offlineQuery )
		ScreenViewer().addResistHiddenRoot(py_box)										# 防止清屏状态看不到消息，由于这种需求不多，这是临时处理方式
		py_box.visible = True

		self.__oldStatus = oldStatus
		BaseStatus.onEnter( self, oldStatus )

	def onLeave( self, newStatus ) :
		if self.__oldStatus == Define.GST_ROLE_SELECT or \
			self.__oldStatus == Define.GST_ROLE_CREATE :
				rds.loginMgr.leave()

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		if BaseStatus.handleKeyEvent( self, down, key, mods ) :
			return True

		result = False
		if rds.uiHandlerMgr.handleKeyEvent( down, key, mods ) :
			result = True
		elif self.__oldStatus == Define.GST_IN_WORLD and \
			rds.shortcutMgr.handleKeyEvent( down, key, mods ) :
				result = True
		rds.shortcutMgr.releaseShortcut( down, key, mods )
		return result

	def handleMouseEvent( self, dx, dy, dz ) :
		if BaseStatus.handleMouseEvent( self, dx, dy, dz ) :
			return True

		cursor = GUI.mcursor()
		if cursor.visible and rds.uiHandlerMgr.handleMouseEvent( dx, dy, dz ) :
			return True
		return False


# --------------------------------------------------------------------
# implement status mamager
# --------------------------------------------------------------------
class StatusMgr :
	__inst = None

	def __init__( self ) :
		self.statusObjs = {}
		self.statusObjs[Define.GST_NONE]						= BaseStatus()
		self.statusObjs[Define.GST_GAME_INIT]					= GameInit()
		self.statusObjs[Define.GST_LOGIN]						= Login()
		self.statusObjs[Define.GST_ENTER_ROLESELECT_LOADING]	= EnterRoleSelectLoading()
		self.statusObjs[Define.GST_ROLE_SELECT]					= RoleSelect()
		self.statusObjs[Define.GST_BACKTO_ROLESELECT_LOADING]	= BacktoRoleSelectLoading()
		self.statusObjs[Define.GST_ROLE_CREATE]					= RoleCreate()
		self.statusObjs[Define.GST_ENTER_WORLD_LOADING]			= EnterWorldLoading()
		self.statusObjs[Define.GST_IN_WORLD]					= InWorld()
		self.statusObjs[Define.GST_SPACE_LOADING]				= TeleportSpace()
		self.statusObjs[Define.GST_OFFLINE]						= Offline()

		self.__statusLabels = {}
		self.__statusLabels[Define.GST_NONE]						= "GST_NONE"
		self.__statusLabels[Define.GST_GAME_INIT]					= "GST_GAME_INIT"
		self.__statusLabels[Define.GST_LOGIN]						= "GST_LOGIN"
		self.__statusLabels[Define.GST_ENTER_ROLESELECT_LOADING] 	= "GST_ENTER_ROLESELECT_LOADING"
		self.__statusLabels[Define.GST_ROLE_SELECT]					= "GST_ROLE_SELECT"
		self.__statusLabels[Define.GST_BACKTO_ROLESELECT_LOADING]	= "GST_BACKTO_ROLESELECT_LOADING"
		self.__statusLabels[Define.GST_ROLE_CREATE]					= "GST_ROLE_CREATE"
		self.__statusLabels[Define.GST_ENTER_WORLD_LOADING]			= "GST_ENTER_WORLD_LOADING"
		self.__statusLabels[Define.GST_IN_WORLD]					= "GST_IN_WORLD"
		self.__statusLabels[Define.GST_SPACE_LOADING]				= "GST_SPACE_LOADING"
		self.__statusLabels[Define.GST_OFFLINE]						= "GST_OFFLINE"

		self.__lastStatus = Define.GST_NONE
		self.__currStatus = Define.GST_NONE

	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = StatusMgr()
		return SELF.__inst


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __beforeStatusChanged( self, oldStatus, status ) :
		rds.ruisMgr.beforeStatusChanged( oldStatus, status )

	def __afterStatusChanged( self, oldStatus, status ) :
		rds.ruisMgr.afterStatusChanged( oldStatus, status )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def currStatus( self ) :
		return self.__currStatus

	def lastStatus( self ) :
		return self.__lastStatus

	def currStatusLabel( self ) :
		return self.__statusLabels[self.__currStatus]

	def statusLabel( self, status ) :
		return self.__statusLabels[status]

	# ---------------------------------------
	def isCurrStatus( self, status ) :
		return status == self.__currStatus

	def isBusy( self ) :
		return self.__currStatus & Define.GST_UNBUSY == 0

	def isOffline( self ):
		return self.__currStatus == Define.GST_OFFLINE

	def isInWorld( self ) :
		return self.__currStatus == Define.GST_IN_WORLD

	# -------------------------------------------------
	def changeStatus( self, status ) :
		"""
		更换当前状态
		"""
		if status == self.__currStatus : return						# 当前已经处于这种状态
		self.__lastStatus = self.__currStatus
		self.__beforeStatusChanged( self.__lastStatus, status )
		self.__currStatus = status
		self.statusObjs[self.__lastStatus].onLeave( status )
		self.statusObjs[status].onEnter( self.__lastStatus )
		self.__afterStatusChanged( self.__lastStatus, status )

	# -------------------------------------------------
	def setToSubStatus( self, gstID, subStatus ) :
		"""
		设置子状态
		"""
		if gstID == self.__currStatus :
			self.statusObjs[gstID].setToSubStatus( subStatus )
		else :
			raise EnvironmentError( "it is not in status %r currently" % self.__statusLabels[gstID] )

	def leaveSubStatus( self, gstID, clsSubStatus ) :
		"""
		清除当前子状态
		"""
		self.statusObjs[gstID].leaveSubStatus( clsSubStatus )

	def isInSubStatus( self, gstID, clsSstatus ) :
		"""
		当前是否处于指定的子状态中
		"""
		if gstID == self.__currStatus :
			return self.statusObjs[gstID].isInSubStatus( clsSstatus )
		return False

	# -------------------------------------------------
	def handleKeyEvent( self, down, key, mods ) :
		statusObj = self.statusObjs.get( self.__currStatus, None )
		if statusObj is None : return False
		return statusObj.handleKeyEvent( down, key, mods )

	def handleMouseEvent( self, dx, dy, dz ) :
		statusObj = self.statusObjs.get( self.__currStatus, None )
		if statusObj is None : return False
		return statusObj.handleMouseEvent( dx, dy, dz )

	def handleAxisEvent( self, axis, value, dTime ) :
		statusObj = self.statusObjs.get( self.__currStatus, None )
		if statusObj is None : return False
		return statusObj.handleAxisEvent( axis, value, dTime )


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
statusMgr = StatusMgr.instance()
