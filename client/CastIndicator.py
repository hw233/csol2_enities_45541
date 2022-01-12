# -*- coding: gb18030 -*-

# common
from bwdebug import ERROR_MSG
from AbstractTemplates import Singleton

# client
import skills
import BigWorld
import GUIFacade
import event.EventCenter as ECenter
from gbref import rds
from ItemsFactory import SkillItem, ObjectItem

# config
from config.client.help.CastIndication import Datas as IDTDatas

class CastIndicator( Singleton ) :
	"""使用物品提示器"""

	def __init__( self ) :
		self.__currTarget = None					# 当前选中的目标
		self.__currIdt = None						# 当前显示的提示
		self.__regIdts = {}							# 注册的提示
		self.__idtsQueue = []						# 触发提示队列

		self.__triggers = {}
		self.__registerTriggers()

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_QUEST_LOG_ADD"]			= self.__onQuestAdd
		self.__triggers["EVT_ON_QUEST_LOG_REMOVED"]		= self.__onQuestRemove
		self.__triggers["EVT_ON_QUEST_TASK_STATE_CHANGED"] = self.__onQuestStateChanged
		self.__triggers["EVT_ON_TARGET_BINDED"]			= self.__onTargetBinded		# 当改变选择目标时被触发
		self.__triggers["EVT_ON_TARGET_UNBINDED"]		= self.__onTargetUnbinded	# 当改变选择目标时被触发
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"]	= self.__onKitbagRemoveItem
		self.__triggers["EVT_ON_ITEM_USE"]				= self.__onUseItem			# 使用物品后被触发
		for evt in self.__triggers.iterkeys() :
			ECenter.registerEvent( evt, self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def PetsWindow( self, idt ) :
		"""加载指示数据"""
		data = idt["data"]
		player = BigWorld.player()
		text = data.get( "text", "" )
		itemID = data.get( "item" )
		if itemID is not None :
			item = player.findItemFromNKCK_( itemID )
			if item is not None :
				return text, ObjectItem( item )
			else :
				ERROR_MSG( "Player dosen't have item %s" % itemID )
		else :
			skillID = data.get( "spell" )
			if player.hasSkill( skillID ) :
				return text, SkillItem( skills.getSkill( skillID ) )
			else :
				ERROR_MSG( "Player dosen't have skill %s" % skillID )
		return "", None

	# -------------------------------------------------
	def __onQuestAdd( self, questId ) :
		"""添加任务"""
		idtIds = self.__searchByQuestId( questId )
		for idtId in idtIds :
			self.register( idtId )

	def __onQuestRemove( self, questId ) :
		"""任务移除"""
		idtIds = self.__searchByQuestId_Reg( questId )
		self.__shutIdts( idtIds )
		for idtId in idtIds :
			self.unregister( idtId )

	def __onQuestStateChanged( self, questId, taskIndex ) :
		"""任务状态改变"""
		if GUIFacade.questIsCompleted( questId ) :
			self.__onQuestRemove( questId )
		else :
			idtIds = self.__searchByQuestId_Reg( questId )
			for idtId in idtIds :
				idt = self.__searchByIdtId_Reg( idtId )
				qtask = idt["condition"].get( "qtask" )
				if qtask and taskIndex == qtask.get( questId ) and\
					GUIFacade.isTaskCompleted( questId, taskIndex ) :
						self.unregister( idtId )
		idtIds = self.__searchByQuestId( questId )
		for idtId in idtIds :
			idt = self.__searchByIdtId( idtId )
			isCompleted = idt.get("isCompleted")
			if isCompleted:
				self.register( idtId )

	def __onTargetBinded( self, target ) :
		"""绑定一个目标"""
		targetId = getattr( target, "className", 0 )
		if targetId == "" : return											# 有些entity的className就是空的...例如炭树
		targetId = int( targetId )
		self.__currTarget = targetId
		for idtId in self.__searchByTargetId_Reg( targetId ) :
			self.indicateCast( [ idtId ] )

	def __onTargetUnbinded( self, target ) :
		"""解除绑定一个目标"""
		idtIds = self.__searchByTargetId_Reg( self.__currTarget )
		self.__shutIdts( idtIds )

	def __onKitbagRemoveItem( self, itemInfo ) :
		"""背包将物品移除"""
		idtIds = self.__searchByItemId_Reg( itemInfo.id )
		self.__shutIdts( idtIds )
		
	def __onUseItem( self, item ):
		"""使用一次物品"""
		idtIds = self.__searchByItemId_Reg( item.id )
		self.__shutIdts( idtIds )

	# --------------------------------------------------
	def __shutIdts( self, idtIds ) :
		"""关掉给定的指示"""
		for idtId in idtIds:
			if self.__currIdt == [idtId]:
				idtIds.remove( idtId )
				idtIds.append( idtId )
		for idtId in idtIds:
			self.shutIndication( [idtId] )

	# -------------------------------------------------
	def __searchByQuestId( self, questId ) :
		"""根据任务ID查找对应的指示"""
		result = []
		for idtId, indication in IDTDatas.iteritems() :
			quest = indication["condition"].get("quest")
			if quest and questId in quest:
				result.append( idtId )
		return result

	def __searchByQuestId_Reg( self, questId ) :
		"""根据任务ID查找对应已注册的指示"""
		result = []
		for idtId, indication in self.__regIdts.iteritems() :
			quest = indication["condition"].get("quest")
			if quest and questId in quest :
				result.append( idtId )
		return result

	def __searchByTargetId( self, targetId ) :
		"""根据触发目标查找指示"""
		result = []
		for idtId, indication in IDTDatas.iteritems() :
			if targetId in indication["condition"].get("target",[]) :
				result.append( idtId )
		return result

	def __searchByTargetId_Reg( self, targetId ) :
		"""根据触发目标查找已注册的指示"""
		result = []
		for idtId, indication in self.__regIdts.iteritems() :
			if targetId in indication["condition"].get("target",[]) :
				result.append( idtId )
		return result

	def __searchByIdtId( self, idtId ) :
		"""根据指示ID查找对应的指示"""
		return IDTDatas.get( idtId )

	def __searchByIdtId_Reg( self, idtId ) :
		"""根据指示ID查找对应已注册的的指示"""
		return self.__regIdts.get( idtId )

	def __searchByItemId_Reg( self, itemId ) :
		"""根据道具ID查找已注册的指示"""
		result = []
		for idtId, indication in self.__regIdts.iteritems() :
			if itemId == indication["data"].get("item") :
				result.append( idtId )
		return result
		
		
	def __getCastId_Reg( self, idtId ) :
		"""获取施放的道具/技能ID"""
		idt = self.__searchByIdtId_Reg( idtId )
		castId = idt["data"].get( "item" )
		if castId is None :
			castId = idt["data"].get( "spell" )
		return castId

	# -------------------------------------------------
	def __showNextIdt( self ) :
		"""显示下一条提示"""
		if len( self.__idtsQueue ) == 0 : return
		self.indicateCast( self.__idtsQueue.pop( 0 ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, evtMacro, *args ) :
		"""注册的事件触发"""
		self.__triggers[evtMacro]( *args )

	def register( self, idtId ) :
		"""注册指示，等待触发"""
		idt = self.__searchByIdtId( idtId )
		if idt is None or not Checker.regCheck( idt["condition"],idt["isCompleted"] ) :
			return
		self.__regIdts[ idtId ] = idt
		if idt.get( "regCast", True ) :
			self.indicateCast( [ idtId ] )

	def unregister( self, idtId ) :
		"""撤销指示，撤销后不能再触发该提示，除非重新注册"""
		self.shutIndication( [idtId] )
		if self.__regIdts.has_key( idtId ) :
			del self.__regIdts[ idtId ]

	# -------------------------------------------------
	def indicateCast( self, idtIdList ) :
		"""提示玩家使用某物品或者技能"""
		if self.__currIdt == idtIdList : return
		idtId = idtIdList[0]
		idt = self.__searchByIdtId( idtId )
		if idt is None:
			return
		questRelated = True
		if idt.has_key( "questRelated" ):
			questRelated = idt["questRelated"]#是否是和任务有关的道具提示		
		if questRelated:
			idt = self.__searchByIdtId_Reg( idtId )
			if idt is None :
				ERROR_MSG( "Indication %s hasn't registered!" % idtId )
				return
			if Checker.castCheck( idt["condition"], idt["isCompleted"] ) :
				if self.__currIdt is not None :								# 当前正在有提示
					self.__idtsQueue.append( idtIdList )
					return
				self.__currIdt = idtIdList
				text, itemInfo = self.PetsWindow( idt )
				rds.ruisMgr.castIndicator.indicate( [( text, itemInfo),] )
			else :
				self.__showNextIdt()
		else:	
			itemInfoArray = []
			for idtId in idtIdList:
				idt = self.__searchByIdtId( idtId )
				if idt is None:
					continue
				text, itemInfo = self.PetsWindow( idt )
				if itemInfo is not None:
					itemInfoArray.append( (text, itemInfo ) )	
			if self.__currIdt is not None :								# 当前正在有提示
				self.__idtsQueue.append( idtIdList )
				return
			self.__currIdt = idtIdList
			rds.ruisMgr.castIndicator.indicate( itemInfoArray )	

	def shutIndication( self, idtIdList ) :
		"""关闭提示，关闭的提示依然能继续触发"""
		if idtIdList in self.__idtsQueue :
			self.__idtsQueue.remove( idtIdList )
		if self.__currIdt is not None and ( len( idtIdList ) == len( self.__currIdt ) ):
			for i in  range( len( idtIdList ) ):
				if idtIdList[i] != self.__currIdt[i]:return
		else:
			return
		rds.ruisMgr.castIndicator.shutdown()
		self.__currIdt = None
		self.__showNextIdt()
		
	def onShutIndication( self ):
		self.__currIdt = None

	# -------------------------------------------------
	def clear( self ) :
		"""清空掉现有数据"""
		self.__regIdts = {}							# 注册的提示
		self.__idtsQueue = []						# 触发提示队列
		self.shutIndication( self.__currIdt )


# --------------------------------------------------------------------
# Checkers
# --------------------------------------------------------------------
class CheckerBase :
	"""所有继承于此类的类（包括间接继承）都是单例类"""
	__insts = {}

	def __init__( self ) :
		assert CheckerBase.__insts.get( self.__class__ ) is None,\
			"Please invoke the class method inst to get instance."
		CheckerBase.__insts[self.__class__] = self

	@classmethod
	def inst( CLS ) :
		if not CLS.__insts.has_key( CLS ) :
			CLS.__insts[CLS] = CLS()
		return CLS.__insts[CLS]

	def __call__( self, data ) :
		return True

class QuestChecker( CheckerBase ) :
	"""任务触发条件检查"""

	def __call__( self, questIds ) :
		for questId in questIds :
			if GUIFacade.hasQuestLog( questId ) \
				and not GUIFacade.questIsCompleted( questId ) :
					return True
		return False

class QTaskChecker( CheckerBase ) :
	"""任务触发条件检查"""

	def __call__( self, taskIdxs ) :
		""""""
		for questId, taskIdx in taskIdxs.iteritems() :
			if GUIFacade.hasQuestLog( questId ) \
				and not GUIFacade.isTaskCompleted( questId, taskIdx ) :
					return True
		return False

class TargetChecker( CheckerBase ) :
	"""目标条件检查"""

	def __call__( self, targets ) :
		""""""
		target = BigWorld.player().targetEntity
		if target is None : return False
		return int( target.className ) in targets

class CompletedQuestChecker( CheckerBase ) :
	"""完成的任务触发条件检查"""

	def __call__( self, questIds ) :
		for questId in questIds :
			if GUIFacade.hasQuestLog( questId ) \
				and GUIFacade.questIsCompleted( questId ) :
					return True
		return False

class CompletedQTaskChecker( CheckerBase ) :
	"""完成的任务触发条件检查"""

	def __call__( self, taskIdxs ) :
		""""""
		for questId, taskIdx in taskIdxs.iteritems() :
			if GUIFacade.hasQuestLog( questId ) \
				and GUIFacade.isTaskCompleted( questId, taskIdx ) :
					return True
		return False
		
class Checker :
	_CHECKER_MAPS = {
		"undoneQuest" : QuestChecker,
		"target" : TargetChecker,
		"undoneQtask" : QTaskChecker,
		"completedQuest":CompletedQuestChecker,
		"completedQtask":CompletedQTaskChecker,
		}

	@classmethod
	def castCheck( CLS, condition, isCompleted ) :
		"""检查触发条件"""
		map_flag = ["undoneQuest","undoneQtask","completedQuest","completedQtask"]
		for flag, data in condition.iteritems() :
			if isCompleted is None or not isCompleted:
				if flag == "quest":
					flag = map_flag[0]
				elif flag == "qtask":
					flag = map_flag[1]
			elif isCompleted :
				if flag == "quest":
					flag = map_flag[2]
					continue
				elif flag == "qtask":
					flag = map_flag[3]
			checker = CLS._CHECKER_MAPS.get( flag )
			if checker is None :
				ERROR_MSG( "Checker %s is not found!" % flag )
				return False
			elif not checker.inst()( data ) :
				return False
		return True

	@classmethod
	def regCheck( CLS, condition, isCompleted ) :
		"""检查注册条件"""
		checkers = ["quest", "qtask"]
		map_flag = ["undoneQuest","undoneQtask","completedQuest","completedQtask"]
		for flag in checkers :
			data = condition.get( flag )
			if data is None : continue
			if isCompleted is None or not isCompleted:
				if flag == "quest":
					flag = map_flag[0]
				elif flag == "qtask":
					flag = map_flag[1]
			elif isCompleted :
				if flag == "quest":
					flag = map_flag[2]
					continue
				elif flag == "qtask":
					flag = map_flag[3]
			if not CLS._CHECKER_MAPS[ flag ].inst()( data ) :
				return False
		return True
