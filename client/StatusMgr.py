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
		self.__subStatus = None						# ��״̬������״̬����̳��� BaseStatus
													# ��״̬�����ڿ���ȫ����ꡢ������Ϣ


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
		���õ�ǰ��״̬
		"""
		if self.__subStatus is not None :
			ERROR_MSG( "current is in %r status, it must be cleared at first!" % self.__subStatus.__class__.__name__ )
		else :
			assert isinstance( subStatus, BaseStatus ), "class of substatus instance must inhires from BaseStatus!"
			self.__subStatus = subStatus
			self.__subStatus.onEnter( None )

	def leaveSubStatus( self, clsSubStatus ) :
		"""
		�뿪��ǰ��״̬
		"""
		if isinstance( self.__subStatus, clsSubStatus ) :
			subStatus = self.__subStatus
			self.__subStatus = None
			subStatus.onLeave( None )

	def isInSubStatus( self, clsSstatus ) :
		"""
		ָ����ǰ�Ƿ���ָ������״̬��
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
		if rds.roleCreator.handleKeyEvent( down, key, mods ) :				# ���
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
		self.__oldArea = None										# �����תǰ����������
		self.__areaDetectTimerID = 0								# ������� callback ID
		self.__areaChanged = False									# ��¼�����Ƿ�ı�
		self.__tmpPos = None										# ��¼����뿪ĳ������ʱ��λ��
		self.__oldSpaceNumber = -1									# ��¼��һ�����ڵĸ���Ψһid
		self.__currArea = None
		self.__mousePressEventList = []								# ��¼��갴���¼��б�


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __resetEntitiesFilter( self ):
		"""
		��������ʵ���Filter
		"""
		for ent in BigWorld.entities.values():
			ent.setFilter()

	# -------------------------------------------------
	def __enterArea( self, newArea ) :
		"""
		����ҽ���������
		"""
		BigWorld.player().onEnterArea( newArea )
		self.__currArea = newArea

	def __detectArea( self ) :
		"""
		�����ҵ�ǰ��������
		"""
		player = BigWorld.player()
		self.__areaDetectTimerID = BigWorld.callback( 2,self.__detectArea )
		if not player or not player.isPlayer() : return
		spaceLabel = BigWorld.player().getSpaceLabel()
		newArea = rds.mapMgr.getArea( spaceLabel, player.position )
		if newArea is None : return										# ���������⣨û�������²�����֣�

		if self.__oldArea is None :										# ��ɫ�ոյ�¼�������磬���ϴ�������任
			self.__areaChanged = False
			self.__enterArea( newArea )									# ֪ͨ��ҽ�����һ���µ�����
			self.__oldArea = newArea									# ����ʱ����������Ϊ��ǰ�����Ա����´��ж�
			return

		if self.__oldArea.spaceLabel != spaceLabel : 					# �����ɫ��ת�� space�����ϴ�������任
			self.__areaChanged = False
			self.__enterArea( newArea )									# ֪ͨ��ҽ�����һ���µ�����
			self.__oldArea = newArea									# ����ʱ����������Ϊ��ǰ�����Ա��´��ж�
			return

		if self.__oldArea.wholeArea == newArea.wholeArea and \
			self.__oldArea.isSubArea() and \
			newArea.isSubArea() and \
			self.__oldArea != newArea and \
			self.__oldArea.name == newArea.name :						# ����¾�������ͬ������( ͬһ���������µ�ͬ��������Ϊͬһ������ )
				self.__areaChanged = False								# ������ı��������Ϊ False����ֹ��һ�� tick ����ʱ���������������任
				self.__oldArea = newArea								# �򣬽���ʱ����������Ϊ��ǰ�����Ա��´��ж�
				return													# �����ͬ������������򲻷�������ת��֪ͨ
																		#�����ǲ߻�Ҫ����Ϊ�п���һ����������飭���������պ����䣩

		if self.__oldArea == newArea :									# �������û���
			sn = BigWorld.getSpaceDataFirstForKey( player.spaceID, \
				csconst.SPACE_SPACEDATA_NUMBER )
			if sn != self.__oldSpaceNumber:								# ����Ѿ�������һ����ͬ��ͼ����
				self.__oldSpaceNumber = sn
				self.__areaChanged = False
				self.__enterArea( newArea )
				self.__oldArea = newArea
			elif not self.__areaChanged :								# �������û�иı�
				self.__tmpPos = Math.Vector3( player.position )			# ���¼����ҵ�λ��
			elif self.__tmpPos.distTo( player.position ) > 15.0 :		# �����ж��Ƿ񳬳����ٽ���
				self.__areaChanged = False
				self.__enterArea( newArea )								# ֪ͨ��ҽ�����һ���µ�����
				self.__oldArea = newArea
		else :															# ���������
			self.__areaChanged = True									# �����Ѿ����������������ϴ�������任����
			self.__oldArea = newArea									# ��ΪҪ�����崦�������ɫ���ٽ��������߶�ʱ��Ƶ���������������


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

		self.__tmpPos = Math.Vector3( player.position )								# ���¼����ҵ�λ��

		BigWorld.dcursor().yaw = player.yaw
		if not rds.worldCamHandler.isYawLocked:
			yaw = player.yaw + math.pi
			rds.worldCamHandler.cameraShell.setYaw( yaw, True )							# ������������ɫ���򱣳�һ��
		self.__resetEntitiesFilter()
		BaseStatus.onEnter( self, oldStatus )
		player.playSpaceCameraEvent()
		self.__areaDetectTimerID = BigWorld.callback( 0.1, self.__detectArea )		# �����������
		player.enterYXLMChangeCamera()            # ����Ӣ�����˸��� �ı侵ͷ
		player.checkTelepoertFly()  #����Ƿ���Ҫ����������贫��
	def onLeave( self, newStatus ) :
		BigWorld.cancelCallback( self.__areaDetectTimerID )
		rds.worldCamHandler.unfix()

	def getCurrArea( self ):
		"""
		��õ�ǰ����Area
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
		if not ( uiHandled or camHandled ): # ���ǰ���߶���������ô����shortcutMgr����
			scHandled = bool( rds.shortcutMgr.handleKeyEvent( down, key, mods ) )

		if not scHandled: rds.shortcutMgr.releaseShortcut( down, key, mods )

		if key in [ KEY_LEFTMOUSE, KEY_RIGHTMOUSE ]:
			pyRoot = rds.ruisMgr.getMouseHitRoot()
			self.__handleMousePressEvent( down, key, mods, pyRoot )
			
		# �κβ��뷽�����ˣ���ô���϶����¼���������
		return uiHandled or camHandled or scHandled

	def __handleMousePressEvent( self, down, key, mods, pyRoot ):
		"""
		������갴���¼�
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
							#�������״̬
							rds.uiHandlerMgr.resetMouseState()
						else:
							#�������״̬
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
		��ȡ��갴���¼��б�
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
		����ѯ��
		"""
		rds.statusMgr.changeStatus( Define.GST_LOGIN )
		try : BigWorld.releaseServerSpace( BigWorld.cameraSpaceID() )
		except ValueError : pass

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@reimpl_login.deco_gstOfflineOnEnter
	def onEnter( self, oldStatus ) :
		msg = mbmsgs[0x0161]															# "�������Ͽ����뷵�ص�¼��"
		if rds.gameMgr.isInKickoutStatus():
			msg = StatusMsgs.getStatusInfo( csstatus.ACCOUNT_STATE_FORCE_LOGOUT ).msg
			rds.gameMgr.changeKickoutStatus( False )

		title = mbmsgs[0x0162]															# ���⣺��ʾ
		py_box = showMessage( msg, title, MB_OK, Offline.__offlineQuery )
		ScreenViewer().addResistHiddenRoot(py_box)										# ��ֹ����״̬��������Ϣ�������������󲻶࣬������ʱ����ʽ
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
		������ǰ״̬
		"""
		if status == self.__currStatus : return						# ��ǰ�Ѿ���������״̬
		self.__lastStatus = self.__currStatus
		self.__beforeStatusChanged( self.__lastStatus, status )
		self.__currStatus = status
		self.statusObjs[self.__lastStatus].onLeave( status )
		self.statusObjs[status].onEnter( self.__lastStatus )
		self.__afterStatusChanged( self.__lastStatus, status )

	# -------------------------------------------------
	def setToSubStatus( self, gstID, subStatus ) :
		"""
		������״̬
		"""
		if gstID == self.__currStatus :
			self.statusObjs[gstID].setToSubStatus( subStatus )
		else :
			raise EnvironmentError( "it is not in status %r currently" % self.__statusLabels[gstID] )

	def leaveSubStatus( self, gstID, clsSubStatus ) :
		"""
		�����ǰ��״̬
		"""
		self.statusObjs[gstID].leaveSubStatus( clsSubStatus )

	def isInSubStatus( self, gstID, clsSstatus ) :
		"""
		��ǰ�Ƿ���ָ������״̬��
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
