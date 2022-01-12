# -*- coding: gb18030 -*-

from bwdebug import *
import BigWorld
import Math
import math
import csdefine
from Function import Functor
from gbref import rds
import CamerasMgr
import csarithmetic
from config.client.CameraEventConfig import Datas as CameraEventDatas
import weakref
from StatusMgr import BaseStatus
import MessageBox
import Define
import keys
import skills
import SkillTargetObjImpl
import event.EventCenter as ECenter
from gbref import rds	#add by wuxo 2011-9-5
from guis.ScreenViewer import ScreenViewer,RTScenario6
from CameraEntityFlyMgr import ceFlyMgr 
# ------------------------------------------------------------------------------
# Class CameraEventMgr:
# ��ͷ�¼�����
# ------------------------------------------------------------------------------

class CameraEventMgr:
	__instance = None

	def __init__( self ):
		assert CameraEventMgr.__instance is None
		self.callback = None
		self.currEvent = []
		self.CameraEventStatusInstance = CameraEventStatus()
		self.ESCShowUI = RTScenario6()
		self.isCanESC = True	# ��ͷESCȡ������

	@classmethod
	def instance( SELF ):
		if SELF.__instance is None:
			SELF.__instance = CameraEventMgr()
		return SELF.__instance

	def reload( self ):
		"""
		"""
		import config.client.CameraEventConfig
		reload( config.client.CameraEventConfig )
		import CameraEventMgr
		reload( CameraEventMgr )
		rds.cameraEventMgr = CameraEventMgr.CameraEventMgr.instance()
	
	def loadAllResource( self ):
		"""
		�������е�Ԥ�����¼�
		"""
		for eventID in CameraEventDatas:
			dictData = CameraEventDatas[eventID]
			if dictData["type"] == "PreloadingEvent" : 
				event = eval( "PreloadingEvent" )( dictData,None )
				event.trigger()

	def triggerByClass( self, eventIDL ):
		"""
		���ݲ�ְͬҵ������ͬ�¼�
		"""
		if len( eventIDL ) == 1:
			self.trigger( eventIDL[0] )
		elif len( eventIDL ) >= 4:
			career = BigWorld.player().getClass()
			if career == csdefine.CLASS_FIGHTER:
				self.trigger( eventIDL[0] )
			elif career == csdefine.CLASS_SWORDMAN:
				self.trigger( eventIDL[1] )
			elif career == csdefine.CLASS_ARCHER:
				self.trigger( eventIDL[2] )
			elif career == csdefine.CLASS_MAGE:
				self.trigger( eventIDL[3] )
		else:
			ERROR_MSG( "------>>>method triggerByClass error.%i"%len( eventIDL ) )

	def trigger( self, eventID, datas = {}, cb = None ):#����һ������datas���ڴ�cameramodel��ģ��modify by wuxo 2011-11-3
		"""
		����
		"""
		try:
			event = createEvent( eventID, datas,callback = self.triggerOver )
		except:
			event = None
			ERROR_MSG( "------>>>client camera eventID error.%i" % eventID )
		if event is None:
			ERROR_MSG( "------>>>client camera eventID is not exist.%i" % eventID )
			return
		if hasattr( BigWorld.player(), "stopMove" ):
			BigWorld.player().stopMove()
		#ȡ��������������
		if hasattr( BigWorld.player(), "cameraInHomingID" ) and BigWorld.player().cameraInHomingID >0:
			BigWorld.player().cameraFollowActionOver()
		self.callback = cb
		self.currEvent.append( event )
		event.trigger()
		self.isCanESC = event.isCanESC
		if rds.statusMgr.currStatus() == Define.GST_IN_WORLD: #�ڵ�½ʱ���ܻ���뾵ͷ
			rds.statusMgr.setToSubStatus( Define.GST_IN_WORLD, self.CameraEventStatusInstance )
		#����ESC������ʾ
		if not rds.roleFlyMgr.isFlyState and self.isCanESC:
			self.ESCShowUI.show()

	def triggerOver( self ):
		"""
		��������
		"""
		if callable( self.callback ):
			self.callback()
		self.callback = None
		self.currEvent = []
		self.ESCShowUI.hide()
		if rds.statusMgr.currStatus() == Define.GST_IN_WORLD:
			rds.statusMgr.leaveSubStatus( Define.GST_IN_WORLD, self.CameraEventStatusInstance.__class__ )

	def cancel( self ):
		"""
		ȡ��
		"""
		if len( self.currEvent ) ==0: return
		for event in self.currEvent:
			event.cancel()
		self.triggerOver()
# --------------------------------------------------------------------
# Define.GST_IN_WORLD ״̬�е���״̬����������״̬��
# ��׽������Ϣ��
# --------------------------------------------------------------------
class CameraEventStatus( BaseStatus ) :
	def __init__( self ) :
		BaseStatus.__init__( self )
		self.messageBox = None

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onCheck( self, value ):
		"""
		����ȷ�ϻص�
		"""
		if value == MessageBox.RS_YES:
			rds.cameraEventMgr.cancel()
		self.messageBox = None

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleKeyEvent( self, down, key, mods  ) :
		"""
		"""
		# �ػ�Esc������Ϣ
		if ( not rds.roleFlyMgr.isFlyState and rds.cameraEventMgr.isCanESC ) and key == keys.KEY_ESCAPE and mods == 0:
			if down:
				if self.messageBox:
					self.messageBox.dispose()
					self.messageBox = None
					return True
				self.messageBox = MessageBox.showMessage( 0x0ed1, "", MessageBox.MB_YES_NO, self.__onCheck )
				# ����������ⴰ��
				ScreenViewer().addResistHiddenRoot(self.messageBox)
				self.messageBox.reShow()
				return True
		return False

class BaseEvent:
	"""
	"""
	def __init__( self, dictData, callback ):
		"""
		"""
		self.childEventIDs = list( dictData.get( "childEvents", [] ) )
		self.orderEventIDs = list( dictData.get( "orderEvents", [] ) )
		self.orderEventIDs.reverse()
		self.endSkillID = int( dictData.get( "endSkillID", 0 ) )
		self.extraData = dictData.get( "extraData", {} )
		self.isHideUI = bool( int( dictData.get( "isHideUI", 0 ) ) )
		self.isLostControl = bool( int( dictData.get( "isLostControl", 0 ) ) )
		self.isCameraRecover = bool( int( dictData.get( "isCameraRecover", 0 ) ) )
		self.isCanESC = bool( int( dictData.get( "isCanESC", 0 ) ) )
		self.callback = callback
		self.isCancel = False
		self.childEvents = []
		self.hasPlayOrderEvents = []
		self.disCamera = 0.0 #���������

	def trigger( self ):
		"""
		����
		"""
		rds.cameraEventMgr.currEvent.append( self )
		if self.isHideUI:
			ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", not self.isHideUI )
		self.triggerChildEvents()

		if self.isLostControl:
			player = BigWorld.player()
			if player:
				player.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE,Define.CONTROL_FORBID_ROLE_MOVE_CAMERA_EVENT )
				player.addControlForbid( Define.CONTROL_FORBID_ROLE_CAMERA,Define.CONTROL_FORBID_ROLE_CAMERA_EVENT )
			self.disCamera = BigWorld.camera().pivotMaxDist

	def cancel( self ):
		"""
		ȡ��
		"""
		self.isCancel = True
		self.onTriggerOrderEventsOver()

	def triggerOver( self ):
		"""
		��������
		"""
		if self in rds.cameraEventMgr.currEvent:
			rds.cameraEventMgr.currEvent.remove( self )
		self.triggerOrderEvents()

	def triggerChildEvents( self ):
		"""
		�������¼�
		"""
		for eventID in self.childEventIDs:
			event = createEvent( eventID, self.extraData )
			if event is None:
				ERROR_MSG( "------>>>client camera eventID error.%i" % eventID )
				continue
			event.trigger()
			self.childEvents.append( event )

	def triggerOrderEvents( self ):
		"""
		����˳���¼�
		"""
		event = self.getNextChildEvent()
		if event is None:
			self.onTriggerOrderEventsOver()
			return
		self.hasPlayOrderEvents.append( event )
		event.trigger()

	def getNextChildEvent( self ):
		"""
		��ȡ��һ�����¼�
		"""
		if len( self.orderEventIDs ) == 0: return None
		eventID = self.orderEventIDs.pop()
		event = createEvent( eventID, self.extraData, self.onOrderChildEventOver )
		if event is None:
			ERROR_MSG( "------>>>client camera eventID error.%i" % eventID )
			return
		return event

	def onOrderChildEventOver( self ):
		"""
		���¼����������ص�
		"""
		self.triggerOrderEvents()

	def onTriggerOrderEventsOver( self ):
		"""
		˳���¼�����
		"""
		if callable( self.callback ):
			self.callback()
		screenViewer = ScreenViewer()
		isHide = screenViewer.getHideByShortCut()
		if self.isHideUI and ( not isHide ):
			ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", self.isHideUI )
		if self.isLostControl:
			player = BigWorld.player()
			if player:
				player.clearSourceControlForbid( Define.CONTROL_FORBID_ROLE_MOVE,Define.CONTROL_FORBID_ROLE_MOVE_CAMERA_EVENT )
				player.clearSourceControlForbid( Define.CONTROL_FORBID_ROLE_CAMERA,Define.CONTROL_FORBID_ROLE_CAMERA_EVENT )
		if self.isCameraRecover:
			rds.worldCamHandler.use()
			BigWorld.callback( 0.01, self.resetCamera )


		if self.endSkillID:
			skillInstance = skills.getSkill( self.endSkillID )
			if skillInstance:
				player = BigWorld.player()
				target = SkillTargetObjImpl.createTargetObjEntity( player )
				skillInstance.cast( player, target )

		self.childEventIDs = []
		self.orderEventIDs = []
		self.callback = None
		self.extraData = {}

	def resetCamera( self ):
		rds.worldCamHandler.reset( self.disCamera )


class BlackScreenEvent( BaseEvent ):
	"""
	��Ļ��ɫ�¼�,Ĭ��Ϊ��ɫ
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.lastTime = float( dictData.get( "param1", 0.0 ) )
		self.totalTime = 1.0
		self.totalTime += self.lastTime

	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		ECenter.fireEvent( "EVT_ON_BLACKEN_SCREEN", (0, 0, 0, 255), self.lastTime )
		BigWorld.callback( self.totalTime, self.__onBlackScreenOver )

	def __onBlackScreenOver( self ):
		"""
		��������
		"""
		self.triggerOver()

	def cancel( self ):
		"""
		ȡ��
		"""
		BaseEvent.cancel( self )
		ECenter.fireEvent( "EVT_ON_BRIGHTEN_SCREEN" )


class PlaySubtitleEvent( BaseEvent ):
	"""
	������Ļ�¼�
	add by wuxo 2011-9-5
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.text = str( dictData.get( "param1", "" ) )
		param2 = str(dictData.get( "param2", "" )).split(";")
		self.showTimes = []
		self.color = (0,0,0,255)
		if len(param2) > 0:
			self.showTimes = eval( param2[0] )
		if len(param2) > 1:
			self.color = eval( param2[1] )

		self.endSkillID = None	#��ĻЯ�����ܲ���
		self.endTime    = None
		skillInfos = str(dictData.get( "param3", "" )).split(";")
		if len(skillInfos) == 2:
			self.endSkillID = int(skillInfos[0])
			self.endTime    = int(skillInfos[1])


	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		ECenter.fireEvent( "EVT_ON_SHOW_SCENARIO_TIPS3", self.text, self.showTimes, self.color )
		totalTime = 0
		for i in self.showTimes:
			totalTime += i

		if self.endSkillID:
			BigWorld.callback( self.endTime, self.playSkill )
		BigWorld.callback( totalTime+1, self.__onPlaySubtitleOver )	#����1�����Ļ���浭��ʱ��

	def playSkill(self):
		"""
		���ż���
		"""
		if self.endSkillID:
			skillInstance = skills.getSkill( self.endSkillID )
			if skillInstance:
				player = BigWorld.player()
				target = SkillTargetObjImpl.createTargetObjEntity( player )
				skillInstance.cast( player, target )

	def __onPlaySubtitleOver( self ):
		"""
		��Ļ���Ž���
		"""
		self.triggerOver()


class PlayNodeTextEvent( BaseEvent ):
	"""
	���ž��������¼�
	add by wuxo 2011-9-29
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.text = str( dictData.get( "param1", "" ) )


	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		if len( self.text ):
			ECenter.fireEvent( "EVT_ON_SHOW_SCENARIO_TIPS2", self.text ,self.__onPlayNodeTextOver)

	def __onPlayNodeTextOver( self ):
		"""
		���鲥�Ž���
		"""
		self.triggerOver()



class ScreenBlurEvent( BaseEvent ):
	"""
	��Ļģ���¼�by wuxo 2011-10-17
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.conIDs = []	#�ص����ؾ��

		blurParams = str( dictData.get( "param1", "" ) )
		try:
			self.blurParams = eval(blurParams)
		except:
			self.blurParams = []


	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		BigWorld.setGraphicsSetting("BLOOM_FILTER", False)
		waitTime = 0
		for i in self.blurParams:
			cbID = BigWorld.callback(waitTime,Functor( self.ScreenBlur, i[0]))
			waitTime += i[1]
			self.conIDs.append(cbID)
		if len(self.blurParams) > 0:
			cb2 = BigWorld.callback(waitTime,self.__playOverScreenBlur)
			self.conIDs.append(cb2)

	def ScreenBlur(self, lv):
		"""
		ʵ����Ļģ��
		"""
		BigWorld.switchScreenBlur(lv)

	def __playOverScreenBlur(self):
		"""
		���Ž���
		"""
		BigWorld.switchScreenBlur(-1)
		self.triggerOver()

	def cancel( self ):
		"""
		ȡ��
		"""
		BaseEvent.cancel( self )
		for cb in self.conIDs:
			BigWorld.cancelCallback(cb)
		BigWorld.switchScreenBlur(-1)

	def onTriggerOrderEventsOver( self ):
		"""
		����˳���¼�����
		"""
		BaseEvent.onTriggerOrderEventsOver( self )
		self.conIDs = []
		self.blurParams = []


class ScreenBlurEndEvent( BaseEvent ):
	"""
	��Ļģ�������¼�by wuxo 2011-10-17
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )

	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		BigWorld.setGraphicsSetting("BLOOM_FILTER", True)
		BigWorld.switchScreenBlur(-1)
		BigWorld.callback(0.1, self.triggerOver )

class PlayScrollTextEvent( BaseEvent ):
	"""
	������Ļ�·��������������¼�
	add by wuxo 2012-3-19
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		param1 = dictData.get( "param1", "" ).split("|")
		param2 = dictData.get( "param2", "" ).split("|")
		if len( param1 ) == 4:
			career = BigWorld.player().getClass()
			if career == csdefine.CLASS_FIGHTER:
				self.text      = param1[0]
				self.showTimes = eval(param2[0])
			elif career == csdefine.CLASS_SWORDMAN:
				self.text      = param1[1]
				self.showTimes = eval(param2[1])
			elif career == csdefine.CLASS_ARCHER:
				self.text      = param1[2]
				self.showTimes = eval(param2[2])
			elif career == csdefine.CLASS_MAGE:
				self.text      = param1[3]
				self.showTimes = eval(param2[3])
		else:
			self.text      = param1[0]
			self.showTimes = eval(param2[0])

	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		if len( self.text ):
			ECenter.fireEvent( "EVT_ON_SHOW_SCENARIO_TIPS4", self.text, self.showTimes, self.__onPlayNodeTextOver)
		else:
			self.triggerOver()

	def __onPlayNodeTextOver( self ):
		"""
		���鲥�Ž���
		"""
		self.triggerOver()

class PlaySkillEvent( BaseEvent ):
	"""
	���ż����¼�
	add by wuxo 2012-3-7
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.time    = float( dictData.get( "param1", "0.0" ) )
		self.skillID = int( dictData.get( "param2") )
		self.flag    = bool( dictData.get( "param3") )

	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		BigWorld.callback( self.time, self.__useSkill)

	def __useSkill(self):
		"""
		ʹ�ü���
		"""
		target = SkillTargetObjImpl.createTargetObjEntity( BigWorld.player() )
		if not self.flag :
			skillInstance = skills.getSkill( self.skillID )
			if skillInstance:
				player = BigWorld.player()
				skillInstance.cast( player, target )
		else:
			BigWorld.player().cell.useSpell( self.skillID, target )
		BigWorld.callback( 2.0, self.__onPlayOver) #������ʱ�����������¼�

	def __onPlayOver( self ):
		"""
		���鲥�Ž���
		"""
		self.triggerOver()


class NewPlayActionEvent( BaseEvent ):
	"""
	ģ�Ͳ��Ŷ����¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.actionNameList = []
		self.model = None
		self.entity = None
		param1 = dictData.get( "param1","" ).split("|")
		if len( param1 ) == 1:
			self.actionNameList = param1[0].split(";")
			self.actionName = self.actionNameList[ -1 ]
		elif len( param1 ) > 1:
			career = BigWorld.player().getClass()
			if career == csdefine.CLASS_FIGHTER:
				self.actionNameList = param1[0].split(";")
				self.actionName = self.actionNameList[ -1 ]
			elif career == csdefine.CLASS_SWORDMAN:
				self.actionNameList = param1[1].split(";")
				self.actionName = self.actionNameList[ -1 ]
			elif career == csdefine.CLASS_ARCHER:
				self.actionNameList = param1[2].split(";")
				self.actionName = self.actionNameList[ -1 ]
			elif career == csdefine.CLASS_MAGE:
				self.actionNameList = param1[3].split(";")
				self.actionName = self.actionNameList[ -1 ]
		flagID = -1
		if dictData.get( "param2", "" ) != "":
			flagID = int( dictData.get( "param2" ) )
		if flagID == 0 :
			self.entity = BigWorld.player()
			self.model = self.entity.getModel()
		else:
			self.entity = getCameraEntityByID(flagID)
			if self.entity != None and self.entity.getModel():
				self.model = self.entity.getModel()
				self.model.visible = True
				self.model.visibleAttachments = True
		
		param3 = dictData.get( "param3" ).split(";")
		self.lastTime = 0.0
		self.isStop = 0
		if len(param3) > 0: 
			self.lastTime = float( param3[0] )
		if len(param3) > 1: 
			self.isStop = int( param3[1] )

	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		if self.isStop and self.entity:
			self.entity.stopMove()
		if self.model:
			if self.lastTime > 0.0:
				rds.actionMgr.playActions( self.model, self.actionNameList )
				BigWorld.callback( self.lastTime, self.__onActionOver )
			else:
				cbList = [None] * len( self.actionNameList )
				cbList[-1] = self.__onActionOver
				rds.actionMgr.playActions( self.model, self.actionNameList, callbacks = cbList )
		else:
			self.__onActionOver()


	def __onActionOver( self ):
		"""
		"""
		if self.isCancel: return
		rds.actionMgr.stopAction( self.model, self.actionName )
		self.triggerOver()

	def cancel( self ):
		"""
		ȡ��
		"""
		BaseEvent.cancel( self )
		rds.actionMgr.stopAction( self.model, self.actionName )

	def onTriggerOrderEventsOver( self ):
		"""
		����˳���¼�����
		"""
		BaseEvent.onTriggerOrderEventsOver( self )
		self.actionName = ""
		self.model = None

class NewPlayEffectEvent( BaseEvent ):
	"""
	ģ�Ͳ��Ź�Ч�¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		param1 = dictData.get( "param1", "" ).split("|")
		self.effectID = ""
		if len( param1 ) == 1:
			self.effectID = param1[0]
		elif len( param1 ) > 3:
			career = BigWorld.player().getClass()
			if career == csdefine.CLASS_FIGHTER:
				self.effectID = param1[0]
			elif career == csdefine.CLASS_SWORDMAN:
				self.effectID = param1[1]
			elif career == csdefine.CLASS_ARCHER:
				self.effectID = param1[2]
			elif career == csdefine.CLASS_MAGE:
				self.effectID = param1[3]
		lastTime = dictData.get( "param2", 0.0 )
		if lastTime == "": lastTime = 0.0
		self.lastTime = float( lastTime )

		self.model = None
		self.targetModel = None
		param3 = dictData.get( "param3", "" ).split(";")
		if len( param3 ) >0 :
			if int(param3[0]) == 0:
				self.model = BigWorld.player().getModel()
			else:
				en = getCameraEntityByID( int(param3[0]) )
				if en != None and en.getModel():
					self.model = en.getModel()
					self.model.visible = True
					self.model.visibleAttachments = True
		if len( param3 ) > 1:
			if int(param3[1]) == 0:
				self.targetModel = BigWorld.player().getModel()
			else:
				en1 = getCameraEntityByID( int(param3[1]) )
				if en1 != None and en1.getModel():
					self.targetModel = en1.getModel()
					self.targetModel.visible = True
					self.targetModel.visibleAttachments = True

		if not self.targetModel:
			self.targetModel = self.model
		self.effect = None

	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		BigWorld.callback( self.lastTime, self.__onEffectOver )

		effect = rds.skillEffect.createEffectByID( self.effectID, self.model, self.targetModel, Define.TYPE_PARTICLE_PLAYER, Define.TYPE_PARTICLE_PLAYER )
		if effect is None: return
		self.effect = effect
		self.effect.start()

	def __onEffectOver( self ):
		"""
		��������
		"""
		if self.isCancel: return
		if self.effect:
			self.effect.stop()
		self.triggerOver()

	def cancel( self ):
		"""
		ȡ��
		"""
		if self.effect:
			self.effect.stop()
		BaseEvent.cancel( self )

	def onTriggerOrderEventsOver( self ):
		"""
		����˳���¼�����
		"""
		BaseEvent.onTriggerOrderEventsOver( self )
		self.effectID = 0
		self.model = None
		self.effect = None
		self.targetModel = None
		self.lastTime = 0.0

class NewMoveCameraEvent( BaseEvent ):
	"""
	�µ����߾�ͷ�ƶ��¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.graphID = str( dictData.get( "param1", "" ) )
		self.isReturn = True
		if dictData.get( "param2" ) != "":
			self.isReturn = int( dictData.get( "param2" ) )

	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		rds.cameraFlyMgr.startCameraFly(self.graphID,self.__onMoveOver)

	def __onMoveOver(self):
		if self.isCancel: return
		if BigWorld.player().isPlayer() and self.isReturn:
			rds.worldCamHandler.use()
		self.triggerOver()
		destroyCameraEntity()

	def cancel( self ):
		"""
		ȡ��
		"""
		BaseEvent.cancel( self )
		rds.cameraFlyMgr.stopFly()
		destroyCameraEntity()
		if BigWorld.player().isPlayer() and self.isReturn:
			rds.worldCamHandler.use()

class NewPlaySoundEvent(BaseEvent):
	"""
	���������¼�(2D/3D)
	�߻���ʱҪ��2D
	"""
	def __init__(self, dictData, callback):
		"""
		��ʼ��
		"""
		BaseEvent.__init__(self, dictData, callback)
		
		soundName = None
		param1 = dictData.get( "param1", "" ).split("|")
		if len( param1 ) == 4:
			career = BigWorld.player().getClass()
			if career == csdefine.CLASS_FIGHTER:
				soundName      = param1[0]
			elif career == csdefine.CLASS_SWORDMAN:
				soundName      = param1[1]
			elif career == csdefine.CLASS_ARCHER:
				soundName      = param1[2]
			elif career == csdefine.CLASS_MAGE:
				soundName      = param1[3]
		else:
			soundName      = param1[0]
		soundNameL = soundName.split(";")
		if len( soundNameL ) > 0:
			if BigWorld.player().getGender() == 0:	#��
				self.soundName = soundNameL[0]
			else:
				self.soundName = soundNameL[-1]
		else:
			self.soundName = soundName
		
		self.lastTime = float( dictData.get( "param2", 0.0 ) )
		soundInfo = str( dictData.get( "param3", 2 ) ).split(";")
		if len(soundInfo) >= 2:
			self.soundType = 3

			try:
				flagID = int( soundInfo[1] )
			except:
				flagID = 0
			en = getCameraEntityByID( flagID )
			if en != None:
				self.model = en.getModel()
			else:
				self.model = None

		else:
			self.soundType = 2
			self.model = None

	def trigger(self):
		"""
		�¼�������
		"""
		BaseEvent.trigger(self)
		if self.soundType == 3:
			rds.soundMgr.playVocality(self.soundName,self.model)
		else:
			rds.soundMgr.play2DSound(self.soundName)
		BigWorld.callback( self.lastTime, self.__onPlaySoundOver )

	def __onPlaySoundOver(self):
		"""
		��Ч�¼����Ž���
		"""
		if self.soundType == 3:
			rds.soundMgr.stopVocality(self.soundName,self.model)
		else:
			rds.soundMgr.stop2DSound(self.soundName)
		self.triggerOver()

	def onTriggerOrderEventsOver( self ):
		"""
		����˳���¼�����
		"""
		BaseEvent.onTriggerOrderEventsOver( self )
		self.soundName = None
		self.lastTime = 0.0
		self.model = None

class CreateCameraEntity( BaseEvent ):
	"""
	����CameraEntity
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.moveSpeed = 0
		self.flagID    = 0
		self.isShow    = False
		self.cbid      = 0
		self.modelScale = 1.0
		param1 = dictData.get( "param1" ).split(";")
		self.modelNumber = param1[0]
		if len(param1) > 1 :
			self.modelScale = float( param1[1] )

		param2 = dictData.get( "param2" )
		try:
			param2 = eval( param2 )
			self.moveSpeed = param2[0]
			self.flagID    = param2[1]
			self.isShow    = param2[2]
		except:
			ERROR_MSG( "------>>>CreateCameraEntity, param2 error! param2: %s." % param2 )

		param3 = dictData.get( "param3" )
		try:
			param3 = eval( param3 )
			self.position   = param3[0]
			self.direction  = param3[1]
			self.isFall     = param3[2]
		except:
			ERROR_MSG( "------>>>CreateCameraEntity, param3 error! param3: %s." % param3 )
			self.position   = BigWorld.player().position
			self.direction  = (0,0,0)
			self.isFall     = True
		self.totalTime = 0.0
	
	def trigger(self):
		"""
		�¼�������
		"""
		BaseEvent.trigger(self)
		p = BigWorld.player()
		if p.__class__.__name__ != "PlayerRole":
			spaceID = rds.roleCreator.getSpaceID()
		else:
			spaceID = p.spaceID
		BigWorld.createEntity("CameraEntity", spaceID, 0 ,self.position, self.direction,
				      {"moveSpeed":self.moveSpeed,
				       "flagID":self.flagID,
				       "modelNumber":self.modelNumber,
				       "modelScale":self.modelScale,
				       "isFall":self.isFall,
				       "isShow":self.isShow
				       }  )
		self.checkCreateOver( )
	
	def checkCreateOver( self ):
		"""
		����Ƿ��Ѿ��������
		"""
		en = getCameraEntityByID( self.flagID )
		if en and en.getModel() and en.getPhysics() :
			self.triggerOver()
		else:
			if self.totalTime > 10.0: #���10���ڻ�û�м�����ɣ���Ĭ���¼�����
				self.triggerOver()
			else:
				self.cbid = BigWorld.callback( 0.1, self.checkCreateOver ) #��һ���ӳ�ʱ��
				self.totalTime += 0.1

	def triggerOver( self ):
		"""
		��������
		"""
		BigWorld.cancelCallback( self.cbid )
		BaseEvent.triggerOver( self )

	def cancel( self ):
		"""
		ȡ��
		"""
		BigWorld.cancelCallback( self.cbid )
		BaseEvent.cancel( self )
	
	def onTriggerOrderEventsOver( self ):
		"""
		����˳���¼�����
		"""
		BaseEvent.onTriggerOrderEventsOver( self )
		self.modelNumber = ""
		self.moveSpeed = 0
		self.flagID = 0
		self.isShow = False
		self.position   = (0,0,0)
		self.direction  = (0,0,0)
		self.totalTime = 0.0


class DestroyCameraEntity( BaseEvent ):
	"""
	����CameraEntity��ģ��
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.id = 0
		flagIDs = []
		self.ens = []
		if dictData.get( "param1", "" ) != "":
			flagIDs = [ int(i) for i in dictData.get( "param1" ).split(";")]
		self.isAlways = 0
		if dictData.get( "param2" ) != "":
			self.isAlways  = int( dictData.get( "param2" ) )
		for flagID in flagIDs:
			en = getCameraEntityByID( flagID )
			self.ens.append(en)

	def trigger(self):
		"""
		�¼�������
		"""
		BaseEvent.trigger(self)
		for en in self.ens:
			if self.isAlways == 0:
				en.model.visible = False
				en.model.visibleAttachments = False
			elif self.isAlways == 1:
				en.model.visible = True
				en.model.visibleAttachments = True
			else:
				en.isAlwaysExist = True
		self.triggerOver()


class CameraEntityMoveEvent( BaseEvent ):
	"""
	ʵ��ģ���ƶ��¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )

		self.cameraEntity = None
		self.position = ( 0.0, 0.0, 0.0 )
		self.moveSpeed = 0.0
		self.jumpAction = ""
		self.jumpTime = 0.0
		self.sourceSpeed = 0.0
		self.moveFace = True

		flagID = -1
		if dictData.get( "param1", "" ) != "":
			flagID = int( dictData.get( "param1" ) )
		if flagID == 0:
			self.cameraEntity = BigWorld.player()
		else:
			en = getCameraEntityByID( flagID )
			if en and en.getModel():
				self.cameraEntity = en
				en.model.visible = True
				en.model.visibleAttachments = True

		param2 = dictData.get( "param2" ).split(";")
		if len(param2) > 0:
			self.position = eval( param2[0] )
		if len(param2) > 1:
			self.moveFace = int( param2[1] )

		param3 = dictData.get( "param3" ).split(";")
		if len(param3) == 1:
			self.moveSpeed = float( param3[0] )
		elif len(param3) == 3:
			self.moveSpeed = float( param3[0] )
			self.jumpAction = param3[1]
			self.jumpTime = float( param3[2] )

	def trigger( self ):
		"""
		����
		"""
		if self.cameraEntity == None : return
		BaseEvent.trigger( self )
		if self.cameraEntity == BigWorld.player():
			self.sourceSpeed = self.cameraEntity.move_speed
			self.cameraEntity.move_speed = self.moveSpeed
			self.cameraEntity.setSpeed( self.moveSpeed )
			self.cameraEntity.moveToDirectly(  self.position, self.__onMoveOver1 )
		else:
			self.cameraEntity.moveTo( self.position, self.moveSpeed,self.moveFace,self.jumpAction, self.jumpTime, self.__onMoveOver )


	def __onMoveOver( self ):
		if self.isCancel: return
		self.triggerOver()

	def __onMoveOver1( self, isSucc ):
		if self.isCancel: return
		self.triggerOver()

	def triggerOver( self ):
		"""
		��������
		"""
		if self.cameraEntity == BigWorld.player() and self.sourceSpeed >0.0:
			self.cameraEntity.move_speed = self.sourceSpeed
			self.cameraEntity.setSpeed( self.sourceSpeed )
		self.cameraEntity.stopMove()
		BaseEvent.triggerOver( self )

	def cancel( self ):
		"""
		ȡ��
		"""
		BaseEvent.cancel( self )
		if self.cameraEntity == BigWorld.player() and self.sourceSpeed >0.0:
			self.cameraEntity.move_speed = self.sourceSpeed
			self.cameraEntity.setSpeed( self.sourceSpeed )
		self.cameraEntity.stopMove()
	
	
class ChaseMoveEvent( BaseEvent ):
	"""
	��Ҹ����ƶ��¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.cameraEntity = BigWorld.player()
		self.target = None
		flagID = -1
		if dictData.get( "param1", "" ) != "":
			flagID = int( dictData.get( "param1" ) )
		en = getCameraEntityByID( flagID )		
		if en and en.getModel():
			self.target = en
			en.model.visible = True
			en.model.visibleAttachments = True
		param2 = dictData.get( "param2" ).split(";")
		self.closeDis = 1.0
		self.moveSpeed = 8.0
		if len(param2)>0:
			self.closeDis = float( param2[0] )
		if len(param2)>1:
			self.moveSpeed = float( param2[1] )	
		
		self.sourceSpeed = 0.0

	def trigger( self ):
		"""
		����
		"""
		if self.cameraEntity == None or self.target == None :
			self.triggerOver()
			return
		BaseEvent.trigger( self )
		self.sourceSpeed = self.cameraEntity.move_speed
		self.cameraEntity.move_speed = self.moveSpeed
		self.cameraEntity.setSpeed( self.moveSpeed )
		self.cameraEntity.navigatePursue( self.target, self.closeDis, self.pursueOver )
	
	def pursueOver( self, owner, targetEntity, success ):
		"""
		׷��Ŀ��Ļص�
		"""
		self.triggerOver()

	def triggerOver( self ):
		"""
		��������
		"""
		BaseEvent.triggerOver( self )
		if self.sourceSpeed > 0.0:
			self.cameraEntity.move_speed = self.sourceSpeed
			self.cameraEntity.setSpeed( self.sourceSpeed )
		self.cameraEntity.stopMove()

	def cancel( self ):
		"""
		ȡ��
		"""
		BaseEvent.cancel( self )
		if self.sourceSpeed > 0.0:
			self.cameraEntity.move_speed = self.sourceSpeed
			self.cameraEntity.setSpeed( self.sourceSpeed )
		self.cameraEntity.stopMove()


class CameraEntityCurveEvent( BaseEvent ):
	"""
	ʵ��ģ�������ƶ��¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.cameraEntity = None
		self.graphID = ""
		self.posCount = 0
		self.isLoop   = 0
		flagID = -1
		if dictData.get( "param1", "" ) != "":
			flagID = int( dictData.get( "param1" ) )
		if flagID == 0:
			self.cameraEntity = BigWorld.player()
		else:
			en = getCameraEntityByID( flagID )
			if en and en.getModel():
				self.cameraEntity = en
				en.model.visible = True
				en.model.visibleAttachments = True
		self.graphID = dictData.get( "param2" )
		param3 = dictData.get( "param3" ).split(";")
		if len( param3 )>0:
			self.posCount = int( param3[0] )
		if len( param3 )>1:
			self.isLoop = int( param3[1] )

	def trigger( self ):
		"""
		����
		"""
		if self.cameraEntity == None : return
		BaseEvent.trigger( self )
		if self.cameraEntity == BigWorld.player():
			self.triggerOver()
		else:
			ceFlyMgr.startRoleFly( self.cameraEntity, self.graphID, self.posCount, self.isLoop, callback = self.__onMoveOver )


	def __onMoveOver( self ):
		if self.isCancel: return
		self.triggerOver()


	def triggerOver( self ):
		"""
		��������
		"""
		ceFlyMgr.stopFly()
		BaseEvent.triggerOver( self )

	def cancel( self ):
		"""
		ȡ��
		"""
		BaseEvent.cancel( self )
		ceFlyMgr.stopFly()

class CameraEntityUpVehicelEvent( BaseEvent ):
	"""
	ʵ��ģ���������¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.cameraEntity = None
		self.effectID = ""
		flagID = -1
		if dictData.get( "param1", "" ) != "":
			flagID = int( dictData.get( "param1" ) )
		if flagID > 0:
			en = getCameraEntityByID( flagID )
			if en and en.getModel():
				self.cameraEntity = en
				en.model.visible = True
				en.model.visibleAttachments = True
		self.effectID = dictData.get( "param2" )

	def trigger( self ):
		"""
		����
		"""
		if self.cameraEntity == None : return
		BaseEvent.trigger( self )
		self.cameraEntity.upVehicle( self.effectID, self.triggerOver )
		


class CameraEntityDownVehicelEvent( BaseEvent ):
	"""
	ʵ��ģ���������¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.cameraEntity = None
		flagID = -1
		if dictData.get( "param1", "" ) != "":
			flagID = int( dictData.get( "param1" ) )
		if flagID > 0:
			en = getCameraEntityByID( flagID )
			if en and en.getModel():
				self.cameraEntity = en
				en.model.visible = True
				en.model.visibleAttachments = True
		self.isFall = True
		self.isFall = bool( dictData.get( "param2", "" ))

	def trigger( self ):
		"""
		����
		"""
		if self.cameraEntity == None : return
		BaseEvent.trigger( self )
		self.cameraEntity.downVehicle( self.isFall, self.triggerOver )


class SetCCLodDistance( BaseEvent ):
	"""
	����CameraEntity��physics��lodDistance����
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.ens = []
		self.distance = 120.0
		if dictData.get( "param1", "" ) != "":
			flagIDs = [ int(i) for i in dictData.get( "param1" ).split(";")]
		if dictData.get( "param2" ) != "":
			self.distance  = float( dictData.get( "param2" ) )
		for flagID in flagIDs:
			en = getCameraEntityByID( flagID )
			self.ens.append(en)

	def trigger(self):
		"""
		�¼�������
		"""
		BaseEvent.trigger(self)
		for en in self.ens:
			en.setLodDistance( self.distance )
		self.triggerOver()

class SetCCFall( BaseEvent ):
	"""
	����CameraEntity��physics��fall����
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.ens = []

		if dictData.get( "param1", "" ) != "":
			flagIDs = [ int(i) for i in dictData.get( "param1" ).split(";")]
		param2 = dictData.get( "param2" ).split(";")
		if len(param2) == 2:
			self.isFall           = bool( param2[0] )
			self.canFloatOnWater  = bool( param2[1] )

		self.isStop = bool( dictData.get( "param3" ) )
		for flagID in flagIDs:
			en = getCameraEntityByID( flagID )
			self.ens.append(en)

	def trigger(self):
		"""
		�¼�������
		"""
		BaseEvent.trigger(self)
		for en in self.ens:
			en.setFall( self.isFall )
			en.setFloatOnWater( self.canFloatOnWater )
			if self.isStop:
				en.stopMove( )
		self.triggerOver()


class CameraEntityJumpEvent( BaseEvent ):
	"""
	ʵ��ģ����Ծ�¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.cbid = 0
		self.cameraEntity = None
		self.speed = 0.0
		self.jumpAction = ""
		self.jumpTime = 0.0

		flagID = 0
		if dictData.get( "param1", "" ) != "":
			flagID = int( dictData.get( "param1", "0" ) )
		en = getCameraEntityByID( flagID )
		if en:
			self.cameraEntity = en
			en.model.visible = True
			en.model.visibleAttachments = True

		self.speed  = float( dictData.get( "param2", "0.0" ) )


		param3 = dictData.get( "param3" ).split(";")
		if len(param3) == 3:
			self.jumpAction = str( param3[0] )
			self.jumpTime = float( param3[1] )
			self.jumpEndFall = bool( param3[2] )


	def trigger( self ):
		"""
		����
		"""
		if self.cameraEntity == None : return
		BaseEvent.trigger( self )
		self.cameraEntity.jump( self.speed, self.jumpAction, self.jumpTime )
		self.cbid = BigWorld.callback( self.jumpTime, self.__onMoveOver )


	def __onMoveOver(self):
		if self.isCancel: return
		self.triggerOver()

	def triggerOver( self ):
		"""
		��������
		"""
		self.cameraEntity.stopJump( self.jumpEndFall )
		BaseEvent.triggerOver( self )

	def cancel( self ):
		"""
		ȡ��
		"""
		BaseEvent.cancel( self )
		BigWorld.cancelCallback( self.cbid )
		self.cameraEntity.stopJump( self.jumpEndFall )

class CameraEntityTurnRoundEvent( BaseEvent ):
	"""
	ʵ��ģ��ת���¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.cameraEntity = None
		self.turnEntity   = None
		self.yaw = 0.0
		flagID = -1
		if dictData.get( "param1", "" ) != "":
			flagID = int( dictData.get( "param1" ) )
		if flagID == 0:
			self.cameraEntity = BigWorld.player()
		else:
			en = getCameraEntityByID( flagID )
			if en:
				self.cameraEntity = en
				en.model.visible = True
				en.model.visibleAttachments = True

		yaw =  dictData.get( "param2", "" )
		if yaw != "":
			self.yaw = float( yaw )

		turnFlagID = -1
		if dictData.get( "param3", "" ) != "":
			turnFlagID = int( dictData.get( "param3" ) )
		if turnFlagID == 0:
			self.turnEntity = BigWorld.player()
		else:
			en = getCameraEntityByID( turnFlagID )
			if en:
				self.turnEntity = en


	def trigger( self ):
		"""
		����
		"""
		if self.cameraEntity == None : return
		BaseEvent.trigger( self )
		if self.turnEntity:
			self.cameraEntity.turnaround( self.turnEntity.matrix )
		else:
			if self.cameraEntity ==  BigWorld.player():
				BigWorld.dcursor().yaw = self.yaw
			else:
				self.cameraEntity.turnRound( self.yaw )
		BigWorld.callback( 1.0, self.__onMoveOver )

	def __onMoveOver(self):
		if self.isCancel: return
		self.triggerOver()

	def cancel( self ):
		"""
		ȡ��
		"""
		BaseEvent.cancel( self )
		

class StopMovingEvent( BaseEvent ):
	"""
	�ƶ���ֹ�¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.cameraEntity = None
		flagID = -1
		if dictData.get( "param1", "" ) != "":
			flagID = int( dictData.get( "param1" ) )
		if flagID == 0:
			self.cameraEntity = BigWorld.player()
		else:
			en = getCameraEntityByID( flagID )
			if en:
				self.cameraEntity = en
				en.model.visible = True
				en.model.visibleAttachments = True

	def trigger( self ):
		"""
		����
		"""
		if self.cameraEntity == None : return
		BaseEvent.trigger( self )
		self.cameraEntity.stopMove()
		BigWorld.callback( 0.1, self.__onOver ) #�����ӳٽ���ʱ��

	def __onOver(self):
		if self.isCancel: return
		self.triggerOver()

class RequestTeleportEvent ( BaseEvent ):
	"""
	�ƶ���ֹ�¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )

	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		BigWorld.player().cell.requestTeleport()
		BigWorld.callback( 0.1, self.__onOver ) #�����ӳٽ���ʱ��

	def __onOver(self):
		self.triggerOver()

class SetFlyWaterEvent( BaseEvent ):
	"""
	�����貨΢���¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.cameraEntity = None
		flagID = -1
		if dictData.get( "param1", "" ) != "":
			flagID = int( dictData.get( "param1" ) )
		en = getCameraEntityByID( flagID )
		if en:
			self.cameraEntity = en
			en.model.visible = True
			en.model.visibleAttachments = True

		self.switch = bool( int(dictData.get( "param2", "0" ) ))

	def trigger( self ):
		"""
		����
		"""
		if self.cameraEntity == None : return
		BaseEvent.trigger( self )
		self.cameraEntity.switchFlyWater( self.switch )
		BigWorld.callback( 0.1, self.__onOver ) #�����ӳٽ���ʱ��

	def __onOver(self):
		if self.isCancel: return
		self.triggerOver()


class HideOtherRolesEvent( BaseEvent ):
	"""
	����������Ұ���UI�¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.hideTime = float( dictData.get( "param1", "0.0" ) )
		self.isHidePlayer = False
		if  dictData.get( "param2" ) != "":
			self.isHidePlayer = int( dictData.get( "param2" ) )
		self.isShowEntity = str( dictData.get( "param3" ) ).split(";")

	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		p = BigWorld.player()

		for en in BigWorld.entities.values():
			if hasattr( en, "hasFlag" ) and en.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):
				continue
			if en == p: #�ų����
				continue
			if hasattr( en, "className" ) and en.className != "" and en.className in self.isShowEntity:
				en.setFlasColorEntity( True ) #���������в����صĹ���
				continue
			if hasattr( en, "setIsShowSelf" ):
				en.setIsShowSelf( False ) #���������ս��ʵ������
				continue
			if en.model:
				en.model.visible = False
		if self.isHidePlayer:
			p.setIsShowSelf( False )
		p.isShowOtherRolesAndUI( False )
		BigWorld.callback( self.hideTime, self.__hideOver )


	def __hideOver(self):
		if self.isCancel: return
		p = BigWorld.player()
		p.isShowOtherRolesAndUI( True )
		for en in BigWorld.entities.values():
			if hasattr( en, "hasFlag" ) and en.hasFlag( csdefine.ENTITY_FLAG_UNVISIBLE ):
				continue
			if hasattr( en, "setIsShowSelf" ):
				en.setIsShowSelf( True )
				continue
			if en.model:
				en.model.visible = True
		self.triggerOver()

	def cancel( self ):
		"""
		ȡ��
		"""
		BaseEvent.cancel( self )
		p = BigWorld.player()
		p.isShowOtherRolesAndUI( True )
		for en in BigWorld.entities.values():
			if hasattr( en, "setIsShowSelf" ):
				en.setIsShowSelf( True )
				continue
			if en.model:
				en.model.visible = True


class PlayFilmTextEvent( BaseEvent ):
	"""
	�������º������Ƶ�Ӱ��Ļ�¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.text = str( dictData.get( "param1", "" ) )
		self.showTimes = eval(str( dictData.get( "param2", "[]" ) ))

	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		if len( self.text ):
			ECenter.fireEvent( "EVT_ON_SHOW_SCENARIO_TIPS5", self.text, self.showTimes, self.__onPlayNodeTextOver)

	def __onPlayNodeTextOver( self ):
		"""
		���鲥�Ž���
		"""
		self.triggerOver()


class SetPlayerAoI( BaseEvent ):
	"""
	�������aoi�¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.range = float( dictData.get( "param1", "0.0" ) )
		self.time = float( dictData.get( "param2", "0.0" ) )

	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		p = BigWorld.player()
		p.cell.setAoI( self.range )
		BigWorld.callback( self.time, self.__setOver )


	def __setOver(self):
		if self.isCancel: return
		self.triggerOver()


class SendAICmd( BaseEvent ):
	"""
	����AIָ��
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.className =  dictData.get( "param1" ) 
		self.aicmdID   =  int( dictData.get( "param2" ) )
		self.range     =  float( dictData.get( "param3" ) )

	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		p = BigWorld.player()
		if p.isPlayer():
			entities = p.entitiesInRange( self.range, cnd = lambda ent : hasattr( ent, "className" ) and ent.className == self.className )
			ids = [ en.id for en in entities ]
			p.cell.sendAICmd( ids, self.aicmdID )
		self.__setOver()


	def __setOver(self):
		if self.isCancel: return
		self.triggerOver()
	
class PlayerJumpEvent( BaseEvent ):
	"""
	�����Ծ�¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )

	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		p = BigWorld.player()
		p.jumpBegin()
		BigWorld.callback( 1.2, self.__jumpOver )


	def __jumpOver(self):
		if self.isCancel: return
		self.triggerOver()


class SimulateJumpEvent( BaseEvent ):
	"""
	ģ����Ծ�¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.cbid =  0
		self.height1 =  0.0
		self.height2 =  0.0
		self.yaw     =  0.0
		flagID = -1
		if dictData.get( "param1", "" ) != "":
			flagID = int( dictData.get( "param1" ) )
		if flagID == 0:
			self.cameraEntity = BigWorld.player()
		else:
			en = getCameraEntityByID( flagID )
			if en:
				self.cameraEntity = en
				en.model.visible = True
				en.model.visibleAttachments = True
		height = dictData.get( "param2").split(";")
		if len( height ) == 1:
			self.height1 = float( height[0] )
		elif len( height ) == 2:
			self.height1 = float( height[0] )
			self.height2 = float( height[1] )
		param3 = dictData.get( "param3").split(";")
		if len( param3 ) > 0:
			self.dis    = float( param3[0] )
		if len( param3 ) > 1:
			self.yaw    = float( param3[1] )
	
	def trigger( self ):
		"""
		����
		"""
		if self.cameraEntity == None : return
		BaseEvent.trigger( self )
		self.cameraEntity.simulateJump( self.height1, self.height2, self.dis, self.yaw )
		phy = self.cameraEntity.getPhysics()
		if not phy:
			self.triggerOver()
		t0 = math.sqrt( self.height1 * 2 / phy.gravity ) #����ߵ�����ʱ��
		t1 = math.sqrt( self.height2 * 2 / phy.gravity ) #��������ʱ�� 
		self.cbid = BigWorld.callback( t0 + t1 + 0.2, self.triggerOver )


	def triggerOver(self):
		self.cameraEntity.stopSimulateJump()
		BaseEvent.triggerOver( self )
	
	def cancel( self ):
		"""
		ȡ��
		"""
		BaseEvent.cancel( self )
		BigWorld.cancelCallback( self.cbid )
		self.cameraEntity.stopSimulateJump()

class PlayerJumpPosEvent( BaseEvent ):
	"""
	���ָ������Ծ�¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.time1 = 0.0
		self.time2 = 0.0
		self.pos = None
		self.pos = eval( dictData.get( "param1" ) )
		if dictData.get( "param2", "" ) != "":
			self.time1 = float( dictData.get( "param2" ) )
		if dictData.get( "param3", "" ) != "":
			self.time2 = float( dictData.get( "param3" ) )
	
	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		if self.pos:
			p = BigWorld.player()
			p.simulateJumpToPoint( self.pos, self.time1, self.time2, self.__jumpOver )
		else:
			self.__jumpOver()


	def __jumpOver(self):
		if self.isCancel: return
		self.triggerOver()


class CameraFollowEvent( BaseEvent ):
	"""
	��ͷ�����¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.yaw = 0.0
		self.pitch = 0.0
		self.cameraEntity = None
		self.lastTime = 0.0 #�������
		self.isReduction  = False #������������Ƿ�ԭ���������
		flagID = -1
		if dictData.get( "param1", "" ) != "":
			flagID = int( dictData.get( "param1" ) )
		if flagID == 0:
			self.cameraEntity = BigWorld.player()
		else:
			en = getCameraEntityByID( flagID )
			if en:
				self.cameraEntity = en
				en.model.visible = True
				en.model.visibleAttachments = True
		param2 = dictData.get( "param2").split(";")
		if len( param2 )>0:
			self.yaw = float( param2[0] )
		if len( param2 )>1:
			self.pitch = float( param2[1] )
		param3 = dictData.get( "param3").split(";")
		if len( param3 )>0:
			self.lastTime = float( param3[0] )
		if len( param3 )>1:
			self.isReduction = float( param3[1] )
		self.cbid  = 0
	
	def trigger( self ):
		"""
		����
		"""
		if self.cameraEntity == None :
			self.triggerOver()
			return
		BaseEvent.trigger( self )
		cc = BigWorld.camera()
		cc.target = self.cameraEntity.matrix
		cc.source.setRotateYPR( ( self.yaw * math.pi / 180, self.pitch * math.pi / 180, math.pi ) )
		self.cbid = BigWorld.callback( self.lastTime, self.triggerOver )

	def triggerOver(self):
		if self.isReduction:
			cc = BigWorld.camera()
			cc.target = BigWorld.player().matrix
		BaseEvent.triggerOver( self )
	
	def cancel( self ):
		"""
		ȡ��
		"""
		if self.isReduction:
			cc = BigWorld.camera()
			cc.target = BigWorld.player().matrix
		BigWorld.cancelCallback( self.cbid )
		BaseEvent.cancel( self )
	
class SetCameraParamsEvent( BaseEvent ):
	"""
	ʵ����ҽ��н�ԶЧ��
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.yaw      = float( dictData.get( "param1", "0.0" ) )
		self.pitch    = float( dictData.get( "param2", "0.0" ) )
		param3 = dictData.get( "param3" ).split(";")
		self.turnTime = float( param3[ 0 ] )
		self.lastTime = float( param3[ 1 ] )
	
	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		cc = BigWorld.camera()
		p = BigWorld.player()
		if cc.__class__.__name__ != "CursorCamera" or p.__class__.__name__ != "PlayerRole" :
			self.triggerOver()
			return
		cc.turningHalfLife = self.turnTime
		cc.source.setRotateYPR( ( self.yaw * math.pi / 180, self.pitch * math.pi / 180, math.pi ) )
		ma = Math.Matrix()
		ma.setTranslate( p.position )
		cc.target = ma
		BigWorld.callback( self.lastTime, self.triggerOver )

	def triggerOver(self):
		BaseEvent.triggerOver( self )
		cc = BigWorld.camera()
		p = BigWorld.player()
		if cc.__class__.__name__ != "CursorCamera" or p.__class__.__name__ != "PlayerRole" :
			return
		cc.turningHalfLife = 0.0
		cc.target = p.matrix
	
	def cancel( self ):
		"""
		ȡ��
		"""
		BaseEvent.cancel( self )
		cc = BigWorld.camera()
		p = BigWorld.player()
		if cc.__class__.__name__ != "CursorCamera" or p.__class__.__name__ != "PlayerRole" :
			return
		cc.turningHalfLife = 0.0
		cc.target = p.matrix
	
	def resetCamera( self ):
		rds.worldCamHandler.reset( 11.0 )   # ���ûָ�ʱ��ͷλ��Ϊ11
	
class FixCameraEvent( BaseEvent ):
	"""
	�̶�������ڵ�ǰ������ĳһ��������Χ�¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.className = str( dictData.get( "param1" ) )
		self.offsets = [ ]  #���λ�ü���
		self.alt = [ ] #����λ��֮����ƶ�ʱ�伯��

		param2 = dictData.get( "param2" ).split(";")
		if len( param2 ) > 0:
			self.offsets = eval( param2[0] )
		if len( param2 ) > 1:
			self.alt = eval( param2[1] )

		if dictData.get( "param3" ) != "":
			self.lastTime = float( dictData.get( "param3" ) )
		else:
			self.lastTime = 1

		self.targetPos = None
		self.targetYaw = None
		for en in BigWorld.entities.values():
			if hasattr( en, "className" ) and en.className == self.className:
				self.targetPos = en.position
				self.targetYaw = en.yaw
				break

		self.camera = CamerasMgr.FlyCameraShell()
		self.camera.reset()
		self.camera.camera.positionAcceleration = 0.0
		self.camera.camera.trackingAcceleration = 0.0

		self.cbid = 0


	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		if len(self.offsets) > 0 and self.targetPos and self.targetYaw :
			self.moveToNextPoint( 0 )
		self.cbid = BigWorld.callback( self.lastTime, self.__fixOver )

	def getPosition( self, index ):
		offsetX = self.offsets[index][0]
		offsetY = self.offsets[index][1]
		offsetZ = self.offsets[index][2]

		dir_x = Math.Vector3( math.sin(self.targetYaw), 0.0, math.cos(self.targetYaw) )
		dir_y = Math.Vector3( math.sin(self.targetYaw - math.pi/2), 0.0, math.cos(self.targetYaw - math.pi/2) )
		dpos = self.targetPos +  dir_x * offsetX + dir_y * offsetY + Math.Vector3(0,offsetZ,0)
		#������ײ
		endDstPos = csarithmetic.getCollidePoint( BigWorld.player().spaceID, self.targetPos, dpos )
		return endDstPos

	def moveToNextPoint( self, index ):
		if index >= len(self.offsets):
			return
		alt = 0.1
		endDstPos = self.getPosition(index)
		#�������������
		if index -1 > 0 and index -1 < len(self.alt) :
			alt = self.alt[ index -1 ]
			nextPos = self.getPosition(index-1)
			dis = ( nextPos-endDstPos ).length
			self.camera.camera.positionAcceleration = math.sqrt( 2*dis/alt/alt )
			self.camera.camera.trackingAcceleration = math.sqrt( 2*dis/alt/alt )
		ma = Math.Matrix()
		ma.setTranslate(endDstPos)
		self.camera.setMatrixTarget(ma)

		if index == 0:
			self.camera.setMatrixTarget(ma)
			d =  self.targetPos - endDstPos
			d.normalise()
			self.camera.stareAt( endDstPos + d )
			BigWorld.camera( self.camera.camera )
		BigWorld.callback( alt, Functor( self.moveToNextPoint, index + 1 ) )

	def __fixOver(self):
		if self.isCancel: return
		self.triggerOver()
		rds.worldCamHandler.use()
		self.cbid = 0

	def cancel( self ):
		"""
		ȡ��
		"""
		BaseEvent.cancel( self )
		BigWorld.cancelCallback( self.cbid )
		rds.worldCamHandler.use()


class PreloadingEvent( BaseEvent ):
	"""
	Ԥ������Դ
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.modelPaths = {} #ģ�ͼ���
		self.effectIDs  = {} #��Ч����
		param1 = dictData.get( "param1" ).split("|")
		for param in param1:
			infos = param.split(";")
			modelNum = infos[0]
			effectIDL = []
			if len( infos ) > 1:
				effectIDL = infos[1:]
			self.modelPaths[ modelNum ] = rds.npcModel.getModelSources( modelNum )
			self.effectIDs[ modelNum ] = effectIDL
	
	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		rds.modelFetchMgr.fetchModels( 0, self.__onModelLoad, self.modelPaths )

	def __onModelLoad( self, modelDict ):
		for modelNum in modelDict:
			effectIDs = self.effectIDs[ modelNum ]
			model = modelDict[ modelNum ]
			for effectID in effectIDs:
				effect = rds.skillEffect.createEffectByID( effectID, model, model, Define.TYPE_PARTICLE_PLAYER, Define.TYPE_PARTICLE_PLAYER )
				if effect:
					effect.start()
		BigWorld.callback( 1.0, self.triggerOver )
	
	
	
class FlashColorEvent( BaseEvent ):
	"""
	����Flash�����¼�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.colors = dictData.get( "param1" ).split(";")
		param2 = dictData.get( "param2" ).split(";")
		self.everyTime = float( param2[0] )
		self.lastTime = float( param2[1] )
		self.cbid = 0
		self.flora_density = 1 #������֮ǰ��ֵ

	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		for label, active, options in BigWorld.graphicsSettings():
			if label == "FLORA_DENSITY":
				self.flora_density = active
				break

		BigWorld.setWatcher( "Render/Terrain/draw", 0 ) # ���ص���
		BigWorld.setWatcher( "Chunks/Chunk Model Visible", 0 ) # ���ؾ�̬�������
		BigWorld.setWatcher( "Render/Enviro draw", 0 ) # ���ػ���
		BigWorld.setWatcher( "Client Settings/Water/draw", 0 ) # ����ˮ
		BigWorld.setWatcher( "Chunks/Particles Lod/Enabled", 0 ) # �ر�������Ч
		BigWorld.setGraphicsSetting("FLORA_DENSITY", 4) # ���ػ����ݲ�
		for color in self.colors:
			color = eval( color )
			newColor = ( color[0]/255.0, color[1]/255.0, color[2]/255.0 )
			BigWorld.addFlashColor( newColor ) # ������ɫ

		BigWorld.setFlashFreQuence( self.everyTime*1000 ) # ������ɫ�����˸�������λ����
		BigWorld.setGraphicsSetting("FLASH_COLOR", 1 ) # ����FLASH_COLORЧ��
		self.cbid = BigWorld.callback( self.lastTime, self.__FlashOver )


	def __FlashOver(self):
		if self.isCancel: return
		self.flashOverSetting()
		self.triggerOver()

	def cancel( self ):
		"""
		ȡ��
		"""
		BaseEvent.cancel( self )
		self.flashOverSetting()
		BigWorld.cancelCallback( self.cbid )

	def flashOverSetting( self ):
		"""
		������������
		"""
		BigWorld.setWatcher( "Render/Terrain/draw", 1 ) # ��ʾ����
		BigWorld.setWatcher( "Chunks/Chunk Model Visible", 1 ) # ��ʾ��̬�������
		BigWorld.setWatcher( "Render/Enviro draw", 65535 ) # ��ʾ����
		BigWorld.setWatcher( "Client Settings/Water/draw", 1 ) # ��ʾˮ
		BigWorld.setWatcher( "Chunks/Particles Lod/Enabled", 1) #�������ӹ�Ч
		BigWorld.setGraphicsSetting("FLORA_DENSITY", self.flora_density ) # �ָ������ݲ�
		BigWorld.clearFlashColor() # �����ɫ
		BigWorld.setGraphicsSetting("FLASH_COLOR", 0 ) # �ر�FLASH_COLORЧ��

class ShowHeadPortraitEvent( BaseEvent ):
	"""
	����NPC������Ի�
	"""
	def __init__( self, dictData, callback ):
		BaseEvent.__init__( self, dictData, callback )
		self.showType = 0							#������ʽ��0����ߣ�1���ұ�
		self.showTitle = ""							#����
		self.headTextureID = ""						#��������
		self.text = dictData.get( "param1", "" )
		param2 = dictData.get( "param2", "" )
		param3 = dictData.get( "param3" ).split(";")
		if len( param2 ) > 0:
			self.lastTime = float( param2 )
		if len( param3 ) == 3:
			self.showType = int( param3[0] )
			self.showTitle = param3[1]
			self.headTextureID = param3[2]

	def trigger( self ):
		"""
		����
		"""
		BaseEvent.trigger( self )
		if len( self.text ):
			ECenter.fireEvent( "EVT_ON_SHOW_HEAD_PORTRAIT_AND_TEXT", self.showType, self.showTitle, self.headTextureID, self.text, self.lastTime, self.__onShowHeadPortraitOver )
		else:
			self.triggerOver()

	def __onShowHeadPortraitOver( self ):
		"""
		���鲥�Ž���
		"""
		self.triggerOver()

def getCameraEntityByID( flagID ):
	"""
	��õ�ǰΨһ��ʶID��CameraEntity
	"""
	for en in BigWorld.entities.values():
		if en.__class__.__name__ == "CameraEntity" and en.flagID == flagID:
			return en
	ERROR_MSG( "------>>>can not find CameraEntity, flagID is %i." % flagID )
	return None

def destroyCameraEntity():
	"""
	�������е�CameraEntity
	"""
	for en in BigWorld.entities.values():
		if en.__class__.__name__ == "CameraEntity":
			if en.isAlwaysExist != True:
				BigWorld.destroyEntity( en.id )


def createEvent( eventID, datas = {}, callback = None ):
	dictData = CameraEventDatas.get( eventID, None )
	if dictData is None: return None
	type = dictData.get( "type", "" )
	if len( type ) == 0: return None
	dictData["extraData"] = datas
	event = eval( type )( dictData, callback )
	return event