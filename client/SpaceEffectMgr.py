# -*- coding: gb18030 -*-

import BigWorld
import Define
import Math
import random
import Const
import csdefine
import GUIFacade
from gbref import rds
from bwdebug import *
from config.client.SpaceEffectConditionConfig import Datas as SpaceEffectConditionDatas
from config.client.SpaceEffectEventConfig import Datas as SpaceEffectEventDatas

# ------------------------------------------------------------------------------
# Class SpaceEffectMgr:
# 场景光效管理器
# 用于实现各种场景光效
# ------------------------------------------------------------------------------
class SpaceEffectMgr:
	__instance = None
	def __init__( self ):
		"""
		"""
		assert SpaceEffectMgr.__instance is None
		self.callback = None
		self.currEvent = None

	@classmethod
	def instance( SELF ):
		if SELF.__instance is None:
			SELF.__instance = SpaceEffectMgr()
		return SELF.__instance

	def reload( self ):
		import config.client.SpaceEffectConditionConfig
		reload( config.client.SpaceEffectConditionConfig )
		import config.client.SpaceEffectEventConfig
		reload( config.client.SpaceEffectEventConfig )
		import SpaceEffectMgr
		reload( SpaceEffectMgr )
		rds.SpaceEffectMgr = SpaceEffectMgr.SpaceEffectMgr.instance()

	def check( self, entity, conditionID ):
		"""
		检测entity是否符合条件
		"""
		condition = createCondition( conditionID )
		if condition is None: return False
		return condition.check( entity )

	def trigger( self, eventID, callback = None ):
		"""
		触发
		"""
		event = createEvent( eventID, callback = self.triggerOver )
		if event is None: return
		self.callback = callback
		self.currEvent = event
		self.currEvent.trigger()

	def getEvent( self ):
		"""
		得到事件实例
		"""
		return self.currEvent

	def cancel( self ):
		"""
		取消
		"""
		if self.currEvent is None: return
		self.currEvent.cancel()
		self.triggerOver()

	def triggerOver( self ):
		"""
		结束
		"""
		if callable( self.callback ):
			self.callback()

		self.callback = None
		self.currEvent = None

# ---------------------------------------------
# 光效事件触发条件基类
# ---------------------------------------------
class SpaceEffectCondition:
	"""
	"""
	def __init__( self, dictData ):
		"""
		"""
		pass

	def check( self, entity ):
		"""
		检测entity是否符合条件
		param entity 	: 实体
		type entity		: Entity
		return   		: Bool
		"""
		return True

class EntitySpaceCnd( SpaceEffectCondition ):
	"""
	entity所处空间
	"""
	def __init__( self, dictData ):
		"""
		"""
		SpaceEffectCondition.__init__( self, dictData )
		self._param1 = dictData.get( "param1" )

	def check( self, entity ):
		"""
		检测entity是否符合条件
		param entity 	: 实体
		type entity		: Entity
		return   		: Bool
		"""
		return entity.getSpaceLabel() == self._param1

class EntityStateCnd( SpaceEffectCondition ):
	"""
	entity所处状态
	"""
	def __init__( self, dictData ):
		"""
		"""
		SpaceEffectCondition.__init__( self, dictData )
		self._param1 = eval( dictData.get( "param1" ) )

	def check( self, entity ):
		"""
		检测entity是否符合条件
		param entity 	: 实体
		type entity		: Entity
		return   		: Bool
		"""
		if not hasattr( entity, "state" ):
			return False
		return entity.state == self._param1

class QuestIsCompletedCnd( SpaceEffectCondition ):
	"""
	entity任务完成
	"""
	def __init__( self, dictData ):
		"""
		"""
		SpaceEffectCondition.__init__( self, dictData )
		self._param1 = int( dictData.get( "param1" ) )

	def check( self, entity ):
		"""
		检测entity是否符合条件
		param entity 	: 实体
		type entity		: Entity
		return   		: Bool
		"""
		if GUIFacade.hasQuestLog( self._param1 ):
			return GUIFacade.questIsCompleted( self._param1 )
		return False

class QuestIsNotCompletedCnd( SpaceEffectCondition ):
	"""
	entity任务未完成
	"""
	def __init__( self, dictData ):
		"""
		"""
		SpaceEffectCondition.__init__( self, dictData )
		self._param1 = int( dictData.get( "param1" ) )

	def check( self, entity ):
		"""
		检测entity是否符合条件
		param entity 	: 实体
		type entity		: Entity
		return   		: Bool
		"""
		if GUIFacade.hasQuestLog( self._param1 ):
			return not GUIFacade.questIsCompleted( self._param1 )
		return False

# ---------------------------------------------
# 光效事件基类
# ---------------------------------------------
class BaseEvent:
	"""
	"""
	def __init__( self, dictData, callback ):
		"""
		"""
		self.childEventIDs = list( dictData.get( "childEvents", [] ) )
		self.callback  = callback
		self.isCancel = False
		self.childEvents = []

	def trigger( self ):
		"""
		触发
		"""
		self.triggerChildEvents()

	def cancel( self ):
		"""
		取消
		"""
		self.isCancel = True
		self.triggerOver()

	def triggerOver( self ):
		"""
		结束
		"""
		self.onTriggerChildEventsOver()

	def triggerChildEvents( self ):
		"""
		并发事件
		"""
		for eventID in self.childEventIDs:
			event = createEvent( eventID, None )
			if event is None: continue
			event.trigger()
			self.childEvents.append( event )

	def onTriggerChildEventsOver( self ):
		"""
		整个事件结束
		"""
		if callable( self.callback ):
			self.callback()

		for event in self.childEvents:
			if event is None: continue
			event.cancel()

		self.childEvents = []
		self.childEventIDs = []
		self.callback = None

class PlayEffectEvent( BaseEvent ):
	"""
	播放光效事件
	"""
	def __init__( self, dictData, callback ):
		"""
		"""
		BaseEvent.__init__( self, dictData, callback )
		self.startPosData = dictData.get( "startPos" ).split( ";" )
		self.startPos = Math.Vector3()
		self.endPosData = dictData.get( "endPos" ).split( ";" )
		self.endPos = Math.Vector3()
		self.effectID = dictData.get( "effectID" )
		self.loopTime = dictData.get( "loopTime" )
		self.startKongModel = None
		self.endKongModel = None
		self.effect = None
		self.spaceEffectTimerID = -1

	def trigger( self ):
		"""
		触发
		"""
		BaseEvent.trigger( self )
		self.playEffect()

	def playEffect( self ):
		"""
		播放光效
		"""
		paths = {"start" : Const.EMPTY_MODEL_PATH, "end" : Const.EMPTY_MODEL_PATH}
		rds.modelFetchMgr.fetchModels( 0, self.__onLoadKongModel, paths )

	def __onLoadKongModel( self, modelDict ):
		"""
		空模型加载完成回调
		"""
		player = BigWorld.player()
		if player is None: return

		self.startKongModel = modelDict.get( "start" )
		if self.startKongModel is None: return
		self.endKongModel = modelDict.get( "end" )
		if self.endKongModel is None: return

		player.addModel( self.startKongModel )
		player.addModel( self.endKongModel )
		self.onTimer()

	def onTimer( self ):
		"""
		"""
		if self.isCancel: return

		# 开始坐标
		if self.startPosData != []:
			self.startPos = random.choice( self.startPosData )
			self.startPos = Math.Vector3( eval( self.startPos ) )
		# 结束坐标
		if self.endPosData != []:
			self.endPos = random.choice( self.endPosData )
			self.endPos = Math.Vector3( eval( self.endPos ) )

		# 设置坐标
		self.startKongModel.position = self.startPos
		self.endKongModel.position = self.endPos

		# 播放光效
		effect = rds.skillEffect.createEffectByID( self.effectID, self.startKongModel, self.endKongModel, Define.TYPE_PARTICLE_PLAYER, Define.TYPE_PARTICLE_PLAYER )
		if effect is None: return
		self.effect = effect
		self.effect.start()

		if self.loopTime != 0.0:
			self.spaceEffectTimerID = BigWorld.callback( self.loopTime, self.onTimer )

	def delKongModel( self ):
		"""
		删除空模型
		"""
		player = BigWorld.player()
		if player is None: return

		if self.startKongModel and self.startKongModel in list( player.models ):
			player.delModel( self.startKongModel )
			self.startKongModel = None
		if self.endKongModel and self.endKongModel in list( player.models ):
			player.delModel( self.endKongModel )
			self.endKongModel = None

	def cancel( self ):
		"""
		取消
		"""
		BaseEvent.cancel( self )
		if self.effect:
			self.effect.stop()
		if self.spaceEffectTimerID != -1:
			BigWorld.cancelCallback( self.spaceEffectTimerID )  # 停止循环调用
			self.spaceEffectTimerID = -1

	def onTriggerChildEventsOver( self ):
		"""
		结束
		"""
		BaseEvent.onTriggerChildEventsOver( self )
		self.delKongModel()
		self.startPosData = []
		self.endPosData = []
		self.loopTime = 0.0
		self.effect = None

def createCondition( condition ):
	dictData = SpaceEffectConditionDatas.get( condition )
	if dictData is None: return None
	type = dictData.get( "type" )
	if len( type ) == 0: return None
	condition = eval( type )( dictData )
	return condition

def createEvent( eventID, callback = None ):
	dictData = SpaceEffectEventDatas.get( eventID, None )
	if dictData is None: return None
	type = dictData.get( "type" )
	if len( type ) == 0: return None
	event = eval( type )( dictData, callback )
	return event