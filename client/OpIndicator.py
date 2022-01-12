# -*- coding: gb18030 -*-

# config
from config.client.help.OpIndications import Datas as OpIDTDatas
# common
from bwdebug import INFO_MSG
from AbstractTemplates import Singleton
# client
import BigWorld
import GUIFacade
import event.EventCenter as ECenter
from gbref import rds
import csdefine

class OpIndicator( Singleton ) :

	def __init__( self ) :
		self.__regIndications = {}					# {id:indication}
		self.__interactionParams = {}				# 某个事件发生时交互的参数
		self.__classificIndications = {}			# {cmd:(idtId1,idtId2,idtId3...)}
		self.__classifyIndications()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __classifyIndications( self ) :
		"""
		将指引按触发条件相同的归为一类
		"""
		for indications in OpIDTDatas.itervalues() :
			for ID, indication in indications.iteritems() :
				condition = CDetector.fetchCondition( indication )
				if condition in self.__classificIndications :
					self.__classificIndications[condition].append( (ID,indication) )
				else :
					self.__classificIndications[condition] = [(ID,indication)]

	def __validIndications( self, indications ) :
		"""
		"""
		result = []
		for idtId, indication in indications.iteritems() :		
			if CDetector.valid( indication ) :
				result.append( ( idtId, indication ) )
		return result

	def __registerIndication( self, idtId, indication ) :
		"""
		"""
		self.__regIndications[idtId] = indication

	def __deregisterIndication( self, idtId ) :
		"""
		"""
		del self.__regIndications[idtId]

	def __triggerIndications( self, indications ) :
		"""
		"""
		for idtId, indication in indications :
			self.__registerIndication( idtId, indication )
			Trigger.fire( idtId, indication )

	def __updateInteraction( self, key, value ) :
		"""
		"""
		self.__interactionParams[key] = value

	def __removeInteraction( self, key ) :
		"""
		"""
		del self.__interactionParams[key]

	def __filterTrigger( self, indications, trigger ) :
		"""
		根据触发条件进行筛选
		"""
		result = []
		for idtId, indication in indications :
			if Trigger.match( indication, trigger ) :
				result.append( ( idtId, indication ) )
		return result


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def idtIdsOfCmd( self, condition, trigger ) :
		"""
		根据触发条件和触发方式获取对应的指引
		"""
		indications = self.__classificIndications.get( condition, () )
		return tuple( i[0] for i in self.__filterTrigger( indications, trigger ) )

	def regIdtsOfTrigger( self, trigger ) :
		"""
		"""
		return self.__filterTrigger( self.__regIndications.iteritems(), trigger )

	def validIdtsOfNpcTalking( self ) :
		"""根据任务ID查找对应的指示"""
		return self.__validIndications( OpIDTDatas["TRIGGER_ON_TALKING_WITH_NPC"] )

	def validIdtsOfQuestAdded( self ) :
		"""
		"""
		return self.__validIndications( OpIDTDatas["TRIGGER_ON_ADDED_QUEST"] )

	def validIdtsOfQuestStateChanged( self ) :
		"""
		"""
		return self.__validIndications( OpIDTDatas["TRIGGER_ON_QUEST_STATE_CHANGED"] )

	def validIdtsOfItemAdded( self ) :
		"""
		"""
		return self.__validIndications( OpIDTDatas["TRIGGER_ON_ADDED_ITEM"] )

	# -------------------------------------------------
	# indications operatte
	# -------------------------------------------------
	def cleanRegIndications( self ) :
		"""
		清理已注册的无效指引
		"""
		for idtId, indication in self.__regIndications.items() :
			if not CDetector.valid( indication ) :
				self.__deregisterIndication( idtId )

	def fireRegIdtsOfTrigger( self, trigger ) :
		"""
		根据触发标记在pyGui上显示新手指引
		"""
		indications = self.regIdtsOfTrigger( trigger )
		for idtId, indication in indications :
			Trigger.fire( idtId, indication )

	def getRegIdtsOfTrigger( self, trigger, guiName,btnName ):
		"""
		根据触发方式的值，查找指引
		"""
		idtIds = []
		indications = self.regIdtsOfTrigger( trigger )
		for idtId, indication in indications :
			triggers = indication["triggers"]
			gui = triggers["gui_visible"][0]
			btn = triggers["gui_visible"][1][0]
			if gui == guiName and btn == btnName:
				idtIds.append( idtId )
		return idtIds
	
	def clear( self ) :
		self.__interactionParams.clear()
		self.__regIndications.clear()

	# -------------------------------------------------
	# function methods
	# -------------------------------------------------
	def onPlayerTalkToNPC( self, npcId ) :
		"""
		"""
		self.__updateInteraction( CD_TalkingNPC.label, GUIFacade.getGossipTargetClassNameInt() )
		self.cleanRegIndications()
		self.__triggerIndications( self.validIdtsOfNpcTalking() )

	def onPlayerEndGossiping( self ) :
		"""
		"""
		self.cleanRegIndications()

	def onPlayerAddedQuest( self, questId ) :
		"""
		player添加了一个任务
		"""
		self.__updateInteraction( CD_AddingQuest.label, questId )
		self.cleanRegIndications()
		self.__triggerIndications( self.validIdtsOfQuestAdded() )

	def onPlayerRemovedQuest( self, questId ) :
		"""
		"""
		self.cleanRegIndications()

	def onPlayerQuestStateChanged( self, questId, taskIndex ) :
		"""
		"""
		self.__updateInteraction( CD_UpdatingQuest.label, ( questId, taskIndex ) )
		self.cleanRegIndications()
		self.__triggerIndications( self.validIdtsOfQuestStateChanged() )

	def onPlayerAddedItem( self, itemId ) :
		"""
		"""
		self.__updateInteraction( CD_AddingItem.label, itemId )
		self.cleanRegIndications()
		self.__triggerIndications( self.validIdtsOfItemAdded() )
		
	def onPlayerAddedVehicle( self, vehicleData ):
		"""
		玩家获得骑宠回调
		"""
		self.__updateInteraction( CD_CheckHasVehicle.label, vehicleData["srcItemID"] )
		self.cleanRegIndications()
		self.__triggerIndications( self.validIdtsOfItemAdded() )
		
	def registerValidQuestIdts( self ):
		self.cleanRegIndications()
		indications = self.validIdtsOfQuestAdded()
		for idtId, indication in indications :
			self.__registerIndication( idtId, indication )

	def hasRegIndication( self, idtId ) :
		"""
		"""
		return idtId in self.__regIndications

	def indicationsAmount( self ) :
		"""
		"""
		return len( self.__regIndications )

	def regIndications( self ) :
		"""
		返回注册的指引
		"""
		return self.__regIndications.copy()

	def idtsBindedTo( self, guiHookName ) :
		"""
		"""
		pass

	def interaction( self, label ) :
		"""
		"""
		return self.__interactionParams.get( label )


# ----------------------------------------------------------------
# condition detectors
# ----------------------------------------------------------------
class CD_TalkingQuest :
	"""检查当前对话任务"""
	label = "talking_quest"
	@classmethod
	def valid( CLS, questId ) :
		return questId == GUIFacade.getQuestID()

class CD_HasQuest :
	"""检查是否拥有某任务"""
	label = "has_quest"
	@classmethod
	def valid( CLS, questId ) :
		return GUIFacade.hasQuestLog( questId )

class CD_HasNoQuest :
	"""检查是否没有某任务"""
	label = "has_no_quest"
	@classmethod
	def valid( CLS, questId ) :
		return not GUIFacade.hasQuestLog( questId )

class CD_QuestCompleted :
	"""检查任务是否已完成"""
	label = "quest_completed"
	@classmethod
	def valid( CLS, questId ) :
		return GUIFacade.hasQuestLog( questId ) and GUIFacade.questIsCompleted( questId )

class CD_QuestHadBeenCompleted :
	"""该任务在过去已经完成"""
	label = "quest_had_been_completed"
	@classmethod
	def valid( CLS, questId ) :
		return BigWorld.player().isQuestCompleted( questId )

class CD_QuestUncompleted :
	"""检查任务是否未完成"""
	label = "quest_uncompleted"
	@classmethod
	def valid( CLS, questId ) :
		return GUIFacade.hasQuestLog( questId ) and not GUIFacade.questIsCompleted( questId )

class CD_QTaskCompleted :
	"""检查任务目标是否已完成"""
	label = "qtask_completed"
	@classmethod
	def valid( CLS, qtask ) :
		return GUIFacade.hasQuestLog( qtask[0] ) and GUIFacade.isTaskCompleted( qtask[0], qtask[1] )

class CD_ItemInKitbag :
	"""检查背包中有某件物品"""
	label = "item_in_kitbag"
	@classmethod
	def valid( CLS, itemId ) :
		return BigWorld.player().findItemFromNKCK_( itemId ) is not None

class CD_AddingItem :
	"""检查是否刚刚获得某个物品"""
	label = "adding_item"
	@classmethod
	def valid( CLS, itemId ) :
		return opIndicator.interaction( CLS.label ) == itemId

class CD_AddingQuest :
	"""检查是否刚刚添加了某个任务"""
	label = "adding_quest"
	@classmethod
	def valid( CLS, questId ) :
		return opIndicator.interaction( CLS.label ) == questId

class CD_UpdatingQuest :
	"""检查是否刚刚更新了某个任务"""
	label = "updating_quest"
	@classmethod
	def valid( CLS, tupleQT ) :
		return opIndicator.interaction( CLS.label ) == tupleQT

class CD_TalkingNPC :
	"""检查当前对话目标"""
	label = "talking_npc"
	@classmethod
	def valid( CLS, npcId ) :
		return opIndicator.interaction( CLS.label ) == npcId
		
class CD_CheckHasVehicle :
	"""检查玩家是否有某个骑宠"""
	label = "checkHasVehicle"
	@classmethod
	def valid( CLS, srcItemID ) :
		player = BigWorld.player()
		for vehicleData in player.vehicleDatas.itervalues():
			if vehicleData["srcItemID"] == srcItemID:
				return True
		return False

class CD_CheckNotHasVehicle :
	"""检查玩家是否没有有某个骑宠"""
	label = "checkNotHasVehicle"
	@classmethod
	def valid( CLS, srcItemID ) :
		player = BigWorld.player()
		for vehicleData in player.vehicleDatas.itervalues():
			if vehicleData["srcItemID"] == srcItemID:
				return False
		return True

class CDetector :
	_DETECTORS = {
		CD_TalkingQuest.label	: CD_TalkingQuest,
		CD_HasQuest.label		: CD_HasQuest,
		CD_HasNoQuest.label		: CD_HasNoQuest,
		CD_QuestCompleted.label	: CD_QuestCompleted,
		CD_QTaskCompleted.label	: CD_QTaskCompleted,
		CD_ItemInKitbag.label	: CD_ItemInKitbag,
		CD_TalkingNPC.label		: CD_TalkingNPC,
		CD_AddingItem.label		: CD_AddingItem,
		CD_AddingQuest.label	: CD_AddingQuest,
		CD_UpdatingQuest.label	: CD_UpdatingQuest,
		CD_QuestUncompleted.label	: CD_QuestUncompleted,
		CD_QuestHadBeenCompleted.label	: CD_QuestHadBeenCompleted,
		CD_CheckHasVehicle.label : CD_CheckHasVehicle,
		CD_CheckNotHasVehicle.label : CD_CheckNotHasVehicle,
	}
	@classmethod
	def valid( CLS, indication ) :
		for d, v in indication["conditions"] :
			if CDetector._DETECTORS[d].valid( v ) is False :
				return False
		return True

	@classmethod
	def fetchCondition( self, indication ) :
		"""
		提取条件关键字元组
		"""
		return tuple( c[0] for c in indication["conditions"] )


# ----------------------------------------------------------------
# triggers
# ----------------------------------------------------------------
class TG_GuiVisible :
	"""
	触发窗口绑定的指引
	"""
	label = "gui_visible"
	@classmethod
	def fire( CLS, idtId, indication ) :
		guiHookName, args = indication["triggers"][CLS.label]
		pyGui = getattr( rds.ruisMgr, guiHookName, None )
		if hasattr( pyGui, "showOpIndication" ) and pyGui.rvisible :
			pyGui.showOpIndication( idtId, *args )
		else :
			INFO_MSG( "--------->>>Show indication of %s fails." % guiHookName )
			
	@classmethod
	def match( CLS, indication, args ) :
		t = indication["triggers"]
		return CLS.label in t and t[CLS.label][0] == args		# 触发界面的匹配判断只判断界面是否匹配，不判断其他参数
			
class TG_Gui_SubPanel_Visible :
	"""
	触发窗口绑定的指引( 必须是继承与TabCtrl)
	"""
	label = "gui_sub_panel_visible"
	@classmethod
	def fire( CLS, idtId, indication ) :
		guiHookName, args = indication["triggers"][CLS.label]
		selIndex = args[0]
		pyGui = getattr( rds.ruisMgr, guiHookName, None )
		subPanel = pyGui.pyPanels[selIndex]
		if hasattr( pyGui, "showOpIndication" ) and subPanel.rvisible :
			pyGui.showOpIndication( idtId, *args )
		else :
			INFO_MSG( "--------->>>Show indication of %s fails." % guiHookName )

	@classmethod
	def match( CLS, indication, args ) :
		t = indication["triggers"]
		return CLS.label in t and t[CLS.label][0] == args		# 触发界面的匹配判断只判断界面是否匹配，不判断其他参数

class TG_FireQuestTrace :
	"""
	触发任务追踪的指引
	"""
	label = "fire_quest_trace"
	@classmethod
	def fire( CLS, idtId, indication ) :
		args = indication["triggers"][CLS.label]
		ECenter.fireEvent( "EVT_ON_INDICATE_QUEST_TRACE", idtId, *args )

	@classmethod
	def match( CLS, indication, args ) :
		t = indication["triggers"]
		if not CLS.label in t :
			return False
		elif args is not None :									# 如果要匹配具体的参数
			return t[CLS.label] == args							# 则判断触发参数是否匹配
		else :													# 走到这里说明只需判断触发方式
			return True

class TG_WieldEquip :
	"""
	触发使用装备的指引
	"""
	label = "wield_equip"
	@classmethod
	def fire( CLS, idtId, indication ) :
		equipId = indication["triggers"][CLS.label]
		ECenter.fireEvent( "EVT_ON_TRIGGER_WIELDTIP_WND", equipId, idtId )

	@classmethod
	def match( CLS, indication, args ) :
		t = indication["triggers"]
		if not CLS.label in t :
			return False
		elif args is not None :									# 如果要匹配具体的参数
			return t[CLS.label] == args							# 则判断触发参数是否匹配
		else :													# 走到这里说明只需判断触发方式
			return True


class Trigger :
	_TRIGGER_UNITS = {
	TG_GuiVisible.label : TG_GuiVisible,
	TG_WieldEquip.label : TG_WieldEquip,
	TG_FireQuestTrace.label : TG_FireQuestTrace,
	TG_Gui_SubPanel_Visible.label : TG_Gui_SubPanel_Visible
	}
	@classmethod
	def fire( CLS, idtId, indication ) :
		for tk in indication["triggers"].iterkeys() :
			Trigger._TRIGGER_UNITS[tk].fire( idtId, indication )

	@classmethod
	def match( CLS, indication, trigger ) :
		return Trigger._TRIGGER_UNITS[trigger[0]].match( indication, trigger[1] )


opIndicator = OpIndicator()