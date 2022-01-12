# -*- coding: gb18030 -*-
#
# $Id: Helper.py,v 1.42 2008-08-07 10:39:50 huangyongwei Exp $

"""
implement helper class
2008/02/15 : writen by huangyongwei
"""

import ResMgr
import BigWorld
import Language
import csdefine
import event.EventCenter as ECenter
import NPCDatasMgr
import GUIFacade
from bwdebug import *
from cscollections import MapList
from cscollections import Stack
from AbstractTemplates import Singleton
from cscustom import Rect
from gbref import rds

# --------------------------------------------------------------------
# implement topic class
# --------------------------------------------------------------------
class Topic( object ) :
	def __init__( self, sect ) :
		self.__sect = sect								# 帮助主题 section
		self.__id = sect.readInt( "id" )				# 主题 ID
		self.__index = sect.readInt( "index" )			# 帮助索引（用于标记顺序关系）
		self.__parentID = sect.readInt( "parentID" )	# 父节点ID

		self.__parent = None							# 父主题节点
		self.__children = []							# 子主题


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def id( self ) :
		"""
		帮助主题 ID
		"""
		return self.__id

	@property
	def index( self ) :
		"""
		帮助主题顺序索引
		"""
		return self.__index

	@property
	def parentID( self ) :
		"""
		主题的父主题 ID，没有则为 -1
		"""
		return self.__parentID

	@property
	def parent( self ) :
		"""
		父主题，没有则为 None
		"""
		return self.__parent

	@property
	def children( self ) :
		"""
		子主题列表
		"""
		return self.__children[:]

	@property
	def title( self ) :
		"""
		主题文本
		"""
		return self.__sect.readString( "title" )

	@property
	def keys( self ) :
		"""
		主题对应的搜索键（即搜索该键或键的子串，可以找到该主题）
		"""
		return self.__sect["keys"].readStrings( "item" )

	@property
	def content( self ) :
		"""
		主题对应的内容
		"""
		return self.__sect.readString( "content" )


	# ----------------------------------------------------------------
	# friend methods of helper
	# ----------------------------------------------------------------
	def addChild( self, topic ) :
		"""
		添加子节点
		"""
		if topic not in self.__children :
			self.__children.append( topic )
			topic.__parent = self


# --------------------------------------------------------------------
# implement base helper class
# --------------------------------------------------------------------
class _BaseHelper( Singleton ) :
	"""
	帮助基类
	"""
	def __init__( self ) :
		assert self.__class__ != _BaseHelper, "The _BaseHelper type cannot be instantiated"
		self.__topics = []							# 所有顶级帮助主题


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def loadConfigs_( self, config ) :
		"""
		加载帮助主题
		"""
		sect = Language.openConfigSection( config )
		if sect is None :
			ERROR_MSG( "load config '%s' fail!" % config )
			return
		topicDict = {}
		for tag, subSect in sect.items() :
			id = subSect.readInt( "id" )
			topicDict[id] = Topic( subSect )
		topics = topicDict.values()
		topics.sort( key = lambda topic : topic.index )
		for topic in topics :
			parent = topicDict.get( topic.parentID, None )
			if parent is None :
				self.__topics.append( topic )
			else :
				parent.addChild( topic )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getTopics( self ) :
		"""
		获取所有顶层帮助主题
		"""
		return self.__topics[:]

	def getTopic( self, id ) :
		"""
		获取指定 id 的帮助主题
		"""
		stack = Stack()
		stack.pushs( self.__topics )
		while stack.size() :
			topic = stack.pop()
			if topic.id == id :
				return topic
			stack.pushs( topic.children )
		return None


# --------------------------------------------------------------------
# implement system helper
# --------------------------------------------------------------------
class SystemHelper( _BaseHelper ) :
	"""
	系统帮助
	"""
	__cc_config = "config/client/help/SystemHelper.xml"		# 系统帮助的配置

	def __init__( self ) :
		_BaseHelper.__init__( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def initialize( self ) :
		"""
		读取配置初始化所有帮助主题
		"""
		self.loadConfigs_( self.__cc_config )

	# -------------------------------------------------
	def searchTopics( self, key ) :
		"""
		根据指定的关键字，搜索帮助主题
		@type				key : str
		@param				key : 指定的关键字关键字
		@rtype					: list
		@return					: 返回包含指定关键字的所有帮助主题
		"""
		topics = []
		stack = Stack()
		stack.pushs( self.getTopics() )
		while stack.size() :
			topic = stack.pop()
			for k in topic.keys :
				if key not in k : continue
				topics.append( topic )
				break
			stack.pushs( topic.children )
		return topics

# --------------------------------------------------------------------
# implement course helper
# --------------------------------------------------------------------
class CourseHelper( _BaseHelper ) :
	"""
	过程帮助
	"""

	__cc_config			= "config/client/help/CourseHelper.xml"		# 过程帮助的配置
	__cc_trigger_config = "config/client/help/HelpTrigger.xml"		# 过程帮助触发

	def __init__( self ) :
		_BaseHelper.__init__( self )

		self.__triggers = {}										# 所有过程帮助的触发器: { ( 触发类型, 触发参数 ) : 帮助主题 }
		self.__histories = set()									# 所有历史帮助
		self.__newHelps = []										# 新的（未查看的）帮助主题( instance of Topic, ...)
		self.__closeTrigger = False									# 关闭帮助提示

		self.__hintItems = {}										# 要提示的获得物品: { 物品ID : 触发参数 }


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __loadTriggers( self ) :
		"""
		加载所有帮助触发键和值
		"""
		sect = Language.openConfigSection( self.__cc_trigger_config )
		if sect is None :
			ERROR_MSG( "load helper triggers fail!" )
			return
		for tag, subSect in sect.items() :
			ttype = subSect.readString( "type" )
			arg = subSect.readString( "argument" )
			topicIDs = subSect["topics"].readInts( "item" )
			topics = []
			for topicID in topicIDs :
				topic = self.getTopic( topicID )
				if topic is None :
					msg = "LoadHelpTriggers: course help topic '%i' of "
					msg += "help trigger '( %s, %s )' is not exist!"
					ERROR_MSG( msg % ( topicID, ttype, arg ) )
				else :
					topics.append( topic )
			if len( topics ) == 0 :
				msg = "LoadHelpTriggers: course help trigger '( %s, %s )' has no topics!"
				WARNING_MSG( msg % ( ttype, arg ) )
			self.__triggers[( ttype, arg )] = topics

			# 下面是“获得物品”的特例
			if ttype == "huodedaoju" :								# 要提示的获得道具
				itemsIDs = arg.split( ";" )							# 拆分道具列表
				for itemID in itemsIDs :
					self.__hintItems[int( itemID )] = arg

	# -------------------------------------------------
	def __getTriggerTopics( self, key ) :
		"""
		获取触发主题
		"""
		topics = []
		for topic in self.__triggers.get( key, [] ) :
			if topic.id not in self.__histories :
				topics.append( topic )
		return topics

	def __saveHistory( self, topic ) :
		"""
		将当前提示保存为历史帮助
		"""
		parent = topic.parent
		while parent :												# 某节点已经提示过
			self.__histories.add( parent.id )						# 则，其所有父节点都标记为提示过
			parent = parent.parent
		self.__histories.add( topic.id )
		BigWorld.player().base.addCourseHelpHistory( topic.id )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onRoleEnterWorld( self ) :
		"""
		当玩家进入世界时，该函数被调用，在这里获得相应角色的历史提示
		"""
		records = BigWorld.player().courseHelpRecords[:]					# 获取历史纪录
		if -1 in records :													# 如果存在 -1
			self.__closeTrigger = True										# 则意味着不触发过程帮助
			records.remove( -1 )											# 移除标记，剩下的就是帮助历史
		else :																# 如果不存在 -1
			self.__closeTrigger = False										# 则表示触发过程帮助
		self.__histories = set( records )									# 获得历史记录
		ECenter.fireEvent( "EVT_ON_COURSE_HELP_TRIGGER_CHANGED", self.__closeTrigger )

	def onRoleLeaveWorld( self ) :
		"""
		当角色离开世界时，清空提示历史
		"""
		self.__historySect = None
		self.__histories.clear()
		self.__newHelps = []

	def onFirstSpaceReady( self ) :
		"""
		当角色从“角色选择”到进入游戏时被调用
		注：这里触发角色第一次进入游戏时需要提示的帮助
		"""
		triggerKeys = [
			( "xitongxingwei", "denglu" ), 							# 第一次登录
			( "juesedengji", "1" ),									# 一级提示
			]
		for topic in self.__newHelps[:] :							# 去除已经提示过的主题
			if topic.id in self.__histories :
				self.__newHelps.remove( topic )
		for triggerKey in reversed( triggerKeys ) :
			topics = self.__getTriggerTopics( triggerKey )
			self.__newHelps = topics + self.__newHelps
		for topic in self.__newHelps :								# 这里重新写一个循环有点冗余
			self.__saveHistory( topic )								# 但因元素不是很多，因此为了简单起见
			if not self.__closeTrigger :							# 这里多做了些工作
				ECenter.fireEvent( "EVT_ON_NEW_COURSE_HELP_ADDED", topic )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def initialize( self ) :
		"""
		读取配置初始化过程帮助( ResourseLoader 中调用初始化 )
		"""
		self.loadConfigs_( self.__cc_config )						# 加载过程帮助主题
		self.__loadTriggers()										# 加载过程帮助触发器

	# -------------------------------------------------
	def getHistories( self ) :
		"""
		获取所有历史提示帮助
		@rtype					: list
		@return					: 帮助主题
		"""
		topicList = []
		for topicID in self.__histories :
			topic = self.getTopic( topicID )
			if not topic : continue
			topicList.append( topic )
		return topicList

	def getNewHelps( self ) :
		"""
		获取新帮助提示
		@type					: list
		@return					: 新的（未查看的）提示帮助主题
		"""
		return self.__newHelps[:]

	def getFirstNewHelp( self ) :
		"""
		获取新提示帮助主题中的第一个提示
		@type					: Topic
		@return					: 提示帮助主题
		"""
		if len( self.__newHelps ) :
			return self.__newHelps[0]
		return None

	# -------------------------------------------------
	def toggleTrigger( self ) :
		"""
		设置是否触发帮助提示
		"""
		self.__closeTrigger = not self.__closeTrigger
		BigWorld.player().base.addCourseHelpHistory( -1 )
		ECenter.fireEvent( "EVT_ON_COURSE_HELP_TRIGGER_CHANGED", self.__closeTrigger )

	def trigger( self, ttype, arg = "" ) :
		"""
		触发一个提示帮助
		@type			ttype : str
		@param			ttype : 过程帮助触发类型
		@type			arg	  : str
		@param			arg	  : 触发参数
		@return				  : None
		"""
		triggerKey = ttype, str( arg )
		topics = self.__getTriggerTopics( triggerKey )
		if rds.statusMgr.isInWorld() :
			for topic in topics :
				self.__newHelps.append( topic )								# 追加一条为查看提示
				self.__saveHistory( topic )									# 保存到历史列表
				if not self.__closeTrigger :								# 如果提示没有关闭
					ECenter.fireEvent( "EVT_ON_NEW_COURSE_HELP_ADDED", topic )
		else :
			for topic in topics :
				if topic not in self.__newHelps :
					self.__newHelps.append( topic )							# 追加一条为查看提示

	def sinkNewHelp( self, topic ) :
		"""
		当玩家查看了某帮助后，调用该函数将该主题设置为历史主题，从此不再提示
		@type			topic : Topic
		@param			topic : 要沉下的新帮助主题
		@return				  : None
		"""
		if topic in self.__newHelps :
			self.__newHelps.remove( topic )
		else :
			DEBUG_MSG( "sink help fail, topic %d is not in new help!" % topic.id )


	# ----------------------------------------------------------------
	# 帮助触发接口
	# ----------------------------------------------------------------
	def roleUpgrade( self, level ) :
		"""
		角色升级提示
		@type				level : int
		@param					  : 等级
		"""
		if ( "juesedengji", str( level ) ) in self.__triggers :
			courseHelper.trigger( "juesedengji", str( level ))

	def openWindow( self, wndName ) :
		"""
		打开窗口
		@type				wndName : str
		@param				wndName : 窗口名称
		@return						: None
		"""
		courseHelper.trigger( "dakaijiemian", wndName )

	def systemAction( self, action ) :
		"""
		系统行为
		打开窗口
		@type				action : str
		@param				action : 行为参数
		"""
		courseHelper.trigger( "xitongxingwei", action )

	def tongFamilyTrigger( self, arg ) :
		"""
		家族帮会触发器
		@type				arg : str
		@param				arg : 参数
		"""
		courseHelper.trigger( "jiazubanghui", arg )

	def roleOperate( self, arg ) :
		"""
		角色操作
		@type				arg : str
		@param				arg : 参数
		"""
		courseHelper.trigger( "juesecaozuo", arg )

	def interactive( self, target ) :
		"""
		NPC 交互
		@type				target : str
		@param				target : 交互对象
		"""
		courseHelper.trigger( "npcjiaohu", target )

	def addItem( self, itemType ) :
		"""
		获得物品（包括:武器、防具、药品、任务道具、法宝、坐骑）
		@type				itemType : int
		@param				itemType : 道具
		"""
		arg = self.__hintItems.get( itemType, None )
		if arg is None : return
		courseHelper.trigger( "huodedaoju", arg )

	def petAction( self, action ) :
		"""
		宠物行为
		@type				action : str
		@param				action : 行为参数
		"""
		courseHelper.trigger( "chongwu", action )



# --------------------------------------------------------------------
# implement ui opertion helper
# --------------------------------------------------------------------
class UIOpHelper( _BaseHelper ) :
	"""
	UI 操作帮助
	"""
	class TipsInfo( object ) :
		__slots__ = ( "id", "text", "style", "bound", "icon", "unframe" )
		def __init__( self, ds ) :
			self.id = int( ds.readString( "id" ), 16 )
			self.text = ds.readString( "text" )
			self.style = ds.readInt( "style" )
			v = ds.readVector4( "bound" )
			self.bound = Rect( v[:2], v[2:] )
			self.icon = ds.readString( "icon" )
			self.unframe = ds.readBool( "unframe" )

	# ----------------------------------------------------------------
	def __init__( self ) :
		self.__tipsInfos = {}


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def initialize( self ) :
		self.__tipsInfos.clear()
		self.__tmpTipsInfos = {}
		path = "config/client/help/UIOpHelper.xml"
		sect = Language.openConfigSection( path )
		if sect is None :
			WARNING_MSG( "config %r is not exist!" % path )
		else :
			Language.purgeConfig( path )
			for ds in sect.values() :
				id = int( ds.readString( "id" ), 16 )
				self.__tmpTipsInfos[id] = ( ds )

	def onFirstSpaceReady( self ) :
		unrecords = BigWorld.player().opr_getUnRecords( csdefine.OPRECORD_UI_TIPS )
		for id, ds in self.__tmpTipsInfos.items() :
			if id not in unrecords : continue
			self.__tipsInfos[id] = UIOpHelper.TipsInfo( ds )
		del self.__tmpTipsInfos

	# -------------------------------------------------
	def hasTips( self, id ) :
		"""
		判断指定的操作提示是否存在
		"""
		return rds.statusMgr.isInWorld() and \
			self.__tipsInfos.has_key( id )

	def getTips( self, id ) :
		"""
		获取一条操作提示
		"""
		if rds.statusMgr.isInWorld() :
			if id in self.__tipsInfos :
				BigWorld.player().opr_saveRecord( csdefine.OPRECORD_UI_TIPS, id )
				return self.__tipsInfos.pop( id )
		return None


# --------------------------------------------------------------------
# QuestHelper
# --------------------------------------------------------------------
class QuestHelper( _BaseHelper ) :
	"""
	QuestHelper provides methods for querying acceptable quests or
	searching quests in range of level limit.
	"""

	__cc_quest_config = "config/client/help/QuestData.xml"				# 等级与可做任务的配置

	class _Quest( object ) :											# 临时任务类
		__slots__ = ( "level", "questLevel", "id", "title", "profession", "npcID",
					"rqQuestTitle", "rqQuestId", "spaceLabel", "npcName", "content", "reqCamp" )
		def __init__( self, level, sect ) :
			self.npcName = ""
			self.spaceLabel = ""
			self.level = level
			self.id = sect.readInt( "id" )
			self.title = sect.readString( "title" )
			self.questLevel = sect.readInt( "questLevel" )
			self.npcID = sect.readString( "npcClassName" )
			self.rqQuestId = sect.readInt( "needFinishQuestID" )
			self.profession = sect.readInt( "player_class" ) << 4
			self.rqQuestTitle = sect.readString( "requirementQuestTitle" )
			self.content = sect.readString( "questContent" )
			self.reqCamp = sect.readInt( "reqCamp" )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def queryAcceptableQuestIdsByTypes( self, types ) :
		"""
		获得玩家可以接受的任务ID列表
		"""
		questIDs = set()
		strTypes = [ str( t ) for t in types ]
		def handler( level, qSect ) :
			"""
			"""
			qID = qSect.readInt( "id" )
			if str( qID )[:3] not in strTypes : return False
			qLV = qSect.readInt( "questLevel" )
			if qLV > 0 and self.__checkAcceptable( qSect ) :
				questIDs.add( qID )
			return False

		upperLV = BigWorld.player().level
		self.__iterConfig( 1, upperLV, handler )
		return questIDs

	def queryAcceptableQuestsByTypes( self, types ) :
		"""
		查询指定类型的可接任务
		"""
		quests = []
		strTypes = [ str( t ) for t in types ]
		_Quest = QuestHelper._Quest
		def handler( level, qSect ) :
			"""
			"""
			qType = str( qSect.readInt( "id" ) )[:3]						# 由于任务ID的长度是不固定的，所以不能使用除法求类型
			if qType not in strTypes : return False
			qLV = qSect.readInt( "questLevel" )
			if qLV > 0 and self.__checkAcceptable( qSect ) :
				quests.append( _Quest( level, qSect ) )
			return False

		upperLV = BigWorld.player().level
		self.__iterConfig( 1, upperLV, handler )
		return quests

	def queryAcceptableQuestTypes( self ) :
		"""
		获得玩家可以接受的任务类型（默认以任务ID前三位为任务类型）
		@return		set of string
		"""
		types = set()
		def handler( level, qSect ) :
			"""
			"""
			qType = int( str( qSect.readInt( "id" ) )[:3] )					# 这里很悲剧...由于配置的任务ID有可能以零开头，且ID长度不统一
			if qType in types : return False
			qLV = qSect.readInt( "questLevel" )
			if qLV > 0 and self.__checkAcceptable( qSect ) :
				types.add( qType )
			return False

		upperLV = BigWorld.player().level
		self.__iterConfig( 1, upperLV, handler )
		return types

	def queryAcceptableQuests( self, minLV, maxLV, profession = None ) :
		"""
		查询可接任务
		注：任务等级范围对应的是配置中的等级，而不是任务本身的等级
		@param		minLV		: 任务等级下限
		@param		maxLV		: 任务等级上限
		@param		profession	: 任务所需职业
		"""
		quests = {}
		_Quest = QuestHelper._Quest
		def handler( level, qSect ) :
			"""
			"""
			qLV = qSect.readInt( "questLevel" )
			if qLV > 0 and self.__checkAcceptable( qSect ) :
				qList = quests.get( level )
				if qList :
					qList.append( _Quest( level, qSect ) )
				else :
					quests[ level ] = [ _Quest( level, qSect ) ]
			return False

		self.__iterConfig( minLV, maxLV, handler )
		return quests

	def queryQuestByID( self, questID ) :
		"""
		根据任务ID查询任务信息
		"""
		quests = []
		_Quest = QuestHelper._Quest
		def handler( level, qSect ) :
			"""
			"""
			qID = qSect.readInt( "id" )
			if qID == questID :
				quests.append( _Quest( level, qSect ) )
				return True
			return False

		self.__iterConfig( 1, 150, handler )
		return quests and quests[0] or None

	def queryQuestsByIDs( self, questIDs ) :
		"""
		根据任务ID查询任务信息
		@param		questIDs : iterable obj, 这个参数很影响效率，
							   据目前所知，传set类型是最快的
		"""
		quests = []
		_Quest = QuestHelper._Quest
		amount = len( questIDs )
		def handler( level, qSect ) :
			"""
			"""
			qID = qSect.readInt( "id" )
			if qID in questIDs :
				quests.append( _Quest( level, qSect ) )
				if len( quests ) == amount :
					return True
			return False

		self.__iterConfig( 1, 150, handler )
		return quests

	def queryPreQuest( self, quest, profession = None ) :
		"""
		查找前置任务
		@param		quest		: 需查询的任务
		@param		profession	: 职业要求，似乎已经废弃？
		"""
		quests = []
		preQID = quest.rqQuestId
		_Quest = QuestHelper._Quest
		def handler( level, qSect ) :
			"""
			"""
			qID = qSect.readInt( "id" )
			if qID == preQID :
				quests.append( _Quest( level, qSect ) )
				return True
			return False

		self.__iterConfig( 1, quest.level, handler )
		return quests and quests[0] or None
		
	def queryNextQuest( self, quest, profession = None ):
		"""
		查找下一个任务
		"""
		quests = []
		_Quest = QuestHelper._Quest
		def hander( level, qSect ) :
			"""
			"""
			qPreIDs = qSect.readString( 'needFinishQuestID' )
			if int( qPreIDs ) == quest.id :
				quests.append( _Quest( level, qSect ) )
				return True
			return False
			
		self.__iterConfig( quest.level, quest.level + 1, hander )
		return quests and quests[0] or None
			

	def queryQuestsInRange( self, minLV, maxLV, profession = None ) :
		"""
		查找指定等级范围内的任务
		注：这里跟 queryAcceptableQuests 接口不同，任务等级范围对应的是
		任务本身的等级，而不是配置中的等级
		@param		minLV		: 任务等级下限
		@param		maxLV		: 任务等级上限
		@param		profession	: 职业要求，似乎已经废弃？
		"""
		quests = {}
		_Quest = QuestHelper._Quest
		def handler( level, qSect ) :
			"""
			"""
			qLV = qSect.readInt( "questLevel" )
			if qLV > maxLV or qLV < minLV : return False
			qList = quests.get( qLV )
			if qList :
				qList.append( _Quest( qLV, qSect ) )
			else :
				quests[ qLV ] = [ _Quest( qLV, qSect ) ]
			return False

		self.__iterConfig( minLV, maxLV, handler )
		return quests


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __iterConfig( self, minLV, maxLV, handler ) :
		"""
		迭代查找需要的任务
		注：任务等级范围对应的是配置中的等级，而不是任务本身的等级
		@param		minLV		: 任务等级下限
		@param		maxLV		: 任务等级上限
		@param		handler		: 处理查找任务的函数
		"""
		sects = Language.openConfigSection( self.__cc_quest_config )
		if sects is None :
			ERROR_MSG( "open %s fail, check whether it is exist please!" % self.__cc_quest_config )
		else :
			LVList = range( minLV, maxLV + 1 )
			if 0 not in LVList : LVList.append( 0 )							# 0里面是可变等级任务，需要加进去
			for level in LVList :
				qSubSects = sects[ str( level ) ]
				if qSubSects is None : continue
				for qSect in qSubSects.values() :
					if qSect.readString( "npcClassName" ) == "" : continue	# 没有接任务NPC的配置忽略，因为交任务的超链接用到这个配置，所以不能在工具里过滤掉，只能在这里处理。
					if handler( level, qSect ) : return						# 只要处理函数返回True，就结束

	def __checkAcceptable( self, qSect ) :
		"""
		检查该任务是否可接受
		@param		qSect : 任务信息
		@type		qSect : PyDataSection
		"""
		# 检查任务ID
		player = BigWorld.player()
		qID = qSect.readInt( 'id' )
		if player.isQuestCompleted( qID ) : return False
		if GUIFacade.hasQuestLog( qID ) : return False								# 如果角色身上已经有此任务
		strTypes = [ "60101","60207" ]
		if str( qID )[:5] in strTypes : return False								# 屏蔽帮会日常任务、帮会副本任务、家族日常任务 --pj
		# 检查前置任务
		preQID = qSect.readInt( 'needFinishQuestID' )
		if preQID and not player.isQuestCompleted( preQID ) : return False
		# 检查职业要求
		validClass = qSect.readInt( "player_class" )
		if validClass and validClass != ( player.getClass() >> 4 ) : return False
		# 检查前提任务
		qPreIDs = qSect.readString( 'needFinishOneOfThem' )
		if qPreIDs != "" :
			for idStr in qPreIDs.split(",") :
				if player.isQuestCompleted( int( idStr ) ) :
					break
			else :
				return False
		# 检查任务任务等级要求
		maxLevel = qSect.readInt( "maxLevel" )
		if maxLevel and player.level > maxLevel : return False
		reqCamp = qSect.readInt( "reqCamp" )
		rCamp = player.getCamp()
		if reqCamp and rCamp != reqCamp: return False
		# 检查互斥任务
		repellentQuests = qSect.readString( 'notHaveOrFinishOneOfThem' )
		if repellentQuests != "" :
			for idStr in repellentQuests.split( ";" ) :
				id = int( idStr )
				if player.isQuestInDoing( id ) or player.isQuestCompleted( id ) :
					return False
		return True

# --------------------------------------------------------------------
# PixieHelper
# --------------------------------------------------------------------
class PixieHelper( Singleton ) :
	"""
	小精灵帮助
	"""
	class _PixieHelpTopic( object ) :
		"""
		"""
		def __init__( self, sect ) :
			self.__sect = sect
			self.__id = sect.readInt( "id" )
			self.__options = []

		@property
		def id( self ) :
			return self.__id

		@property
		def content( self ) :
			return self.__sect.readString( "content" )

		@property
		def options( self ) :
			return self.__options[:]

		@property
		def uioKey( self ) :
			return int( self.__sect.readString( "uioKey" ), 16 )

		def addOption( self, option ) :
			"""
			添加孩子帮助主题
			"""
			if option not in self.__options :
				self.__options.append( option )


	# ----------------------------------------------------------------
	# methods and properties of PixieHelper
	# ----------------------------------------------------------------
	def __init__( self ) :
		self.__topics = {}
		self.__currHTopicID = 0
		self.__settingSect = None
		self.__settingPath = ""

	def __initPixieSetting( self ) :
		"""
		初始化小精灵客户端设置
		"""
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]
		roleName = rds.gameMgr.getCurrRoleHexName()
		self.__settingPath = "account/%s/%s/pixiesetting.xml" % ( accountName, roleName )
		self.__settingSect = ResMgr.openSection( self.__settingPath, True )

	# -------------------------------------------------
	# public
	# -------------------------------------------------
	def initialize( self ) :
		"""
		"""
		self.__topics = {}
		self.__currHTopicID = 0
		path = "config/client/help/PixieHelper.xml"
		sect = Language.openConfigSection( path )
		if sect is None :
			ERROR_MSG( "Can't open %s." % path )
			return
		self.__tempSect = sect
		Language.purgeConfig( path )

	def onFirstSpaceReady( self ) :
		"""
		"""
		pass
#		unrecords = BigWorld.player().opr_getUnRecords( csdefine.OPRECORD_PIXIE_HELP )							# unrecords ????????????????
#		#unrecords = [ 101, 102, 201, 202 ]
#		for subSect in self.__tempSect.values() :
#			id = subSect.readInt( "id" )
#			if id not in unrecords : continue
#			topic = PixieHelper._PixieHelpTopic( subSect )
#			for optionSect in subSect["options"].values() :
#				label = optionSect.readString( "text" )
#				linkID = optionSect.readInt( "linkID" )
#				topic.addOption( ( label, linkID ) )
#			self.__topics[id] = topic
#		del self.__tempSect
#		self.__initPixieSetting()

	# -------------------------------------------------
	def getTopic( self, topicID ) :
		"""
		获取某个帮助主题
		"""
		return self.__topics.get( topicID )

	def triggerSection( self, topicID ) :
		"""
		触发某个帮助环节
		"""
		if topicID == 0 :
			ECenter.fireEvent( "EVT_ON_HIDE_PIXIE_WINDOW" )
			return
		topic = self.getTopic( topicID )
		if topic is None :
			ERROR_MSG( "Topic is not exist! id: %i" % topicID )
			return
		ECenter.fireEvent( "EVT_ON_TRIGGER_PIXIE_HELP", topic.content, topic.options )
		ECenter.fireEvent( "EVT_ON_IMPLEMENT_UI_OPERATION", topic.uioKey )

	def triggerTopic( self, hTopicID ) :
		"""
		触发某个帮助主题
		"""
		self.sinkTopicsLink()											# 弹出一个新的主题时把旧的主题删除
		self.__currHTopicID = hTopicID
		self.triggerSection( hTopicID )

	def sinkTopicsLink( self, hTopicID = None ) :
		"""
		"""
		if hTopicID is None :
			hTopicID = self.__currHTopicID
			self.__currHTopicID = 0
		tpIdsLink = self.searchTopicsLink( hTopicID )
		for id in tpIdsLink :
			BigWorld.player().opr_saveRecord( csdefine.OPRECORD_PIXIE_HELP, id )
			del self.__topics[ id ]
		print "------->>> %s are sinked." % str( tpIdsLink )

	def searchTopicsLink( self, hTopicID ) :
		"""
		"""
		idsLink = []
		stack = Stack()
		stack.push( hTopicID )
		while stack.size() :
			topicID = stack.pop()
			topic = self.getTopic( topicID )
			if topic is None : continue
			idsLink.append( topicID )
			stack.pushs( [ op[-1] for op in topic.options ]  )
		return idsLink


	# -------------------------------------------------
	# 小精灵在线功能相关
	# -------------------------------------------------
	def enableDirection( self, enable ) :
		"""
		开启/关闭精灵指引
		"""
		if self.__settingSect is None :
			ERROR_MSG( "Pixie setting section is None!" )
			return
		self.__settingSect.writeBool( "pixie_direct", enable )

	def enableGossip( self, enable ) :
		"""
		开启/关闭精灵闲话
		"""
		if self.__settingSect is None :
			ERROR_MSG( "Pixie setting section is None!" )
			return
		self.__settingSect.writeBool( "pixie_gossip", enable )

	def visibleVIPFlag( self, visible ) :
		"""
		显示/关闭VIP标识
		"""
		if self.__settingSect is None :
			ERROR_MSG( "Pixie setting section is None!" )
			return
		self.__settingSect.writeBool( "show_vip_flag", visible )

	# -------------------------------------------------
	def isInDirecting( self ) :
		"""
		是否开启精灵指引
		"""
		if self.__settingSect is None :
			ERROR_MSG( "Pixie setting section is None!" )
			return
		return self.__settingSect.readBool( "pixie_direct", True )

	def isInGossipping( self ) :
		"""
		是否开启精灵闲聊
		"""
		if self.__settingSect is None :
			ERROR_MSG( "Pixie setting section is None!" )
			return
		return self.__settingSect.readBool( "pixie_gossip", True )

	def isVipFlagShow( self ) :
		"""
		是否显示VIP标识
		"""
		if self.__settingSect is None :
			ERROR_MSG( "Pixie setting section is None!" )
			return
		return self.__settingSect.readBool( "show_vip_flag", True )

	# -------------------------------------------------
	def onRoleLeaveWorld( self ) :
		"""
		玩家下线
		"""
		if self.__settingSect is None :
			ERROR_MSG( "Pixie setting section is None!" )
			return
		self.__settingSect.save()
		ResMgr.purge( self.__settingPath )
		self.__settingSect = None
		self.__settingPath = ""


# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
systemHelper = SystemHelper()
courseHelper = CourseHelper()
uiopHelper = UIOpHelper()
questHelper = QuestHelper()
pixieHelper = PixieHelper()

