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
		self.__sect = sect								# �������� section
		self.__id = sect.readInt( "id" )				# ���� ID
		self.__index = sect.readInt( "index" )			# �������������ڱ��˳���ϵ��
		self.__parentID = sect.readInt( "parentID" )	# ���ڵ�ID

		self.__parent = None							# ������ڵ�
		self.__children = []							# ������


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def id( self ) :
		"""
		�������� ID
		"""
		return self.__id

	@property
	def index( self ) :
		"""
		��������˳������
		"""
		return self.__index

	@property
	def parentID( self ) :
		"""
		����ĸ����� ID��û����Ϊ -1
		"""
		return self.__parentID

	@property
	def parent( self ) :
		"""
		�����⣬û����Ϊ None
		"""
		return self.__parent

	@property
	def children( self ) :
		"""
		�������б�
		"""
		return self.__children[:]

	@property
	def title( self ) :
		"""
		�����ı�
		"""
		return self.__sect.readString( "title" )

	@property
	def keys( self ) :
		"""
		�����Ӧ�����������������ü�������Ӵ��������ҵ������⣩
		"""
		return self.__sect["keys"].readStrings( "item" )

	@property
	def content( self ) :
		"""
		�����Ӧ������
		"""
		return self.__sect.readString( "content" )


	# ----------------------------------------------------------------
	# friend methods of helper
	# ----------------------------------------------------------------
	def addChild( self, topic ) :
		"""
		����ӽڵ�
		"""
		if topic not in self.__children :
			self.__children.append( topic )
			topic.__parent = self


# --------------------------------------------------------------------
# implement base helper class
# --------------------------------------------------------------------
class _BaseHelper( Singleton ) :
	"""
	��������
	"""
	def __init__( self ) :
		assert self.__class__ != _BaseHelper, "The _BaseHelper type cannot be instantiated"
		self.__topics = []							# ���ж�����������


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def loadConfigs_( self, config ) :
		"""
		���ذ�������
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
		��ȡ���ж����������
		"""
		return self.__topics[:]

	def getTopic( self, id ) :
		"""
		��ȡָ�� id �İ�������
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
	ϵͳ����
	"""
	__cc_config = "config/client/help/SystemHelper.xml"		# ϵͳ����������

	def __init__( self ) :
		_BaseHelper.__init__( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def initialize( self ) :
		"""
		��ȡ���ó�ʼ�����а�������
		"""
		self.loadConfigs_( self.__cc_config )

	# -------------------------------------------------
	def searchTopics( self, key ) :
		"""
		����ָ���Ĺؼ��֣�������������
		@type				key : str
		@param				key : ָ���Ĺؼ��ֹؼ���
		@rtype					: list
		@return					: ���ذ���ָ���ؼ��ֵ����а�������
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
	���̰���
	"""

	__cc_config			= "config/client/help/CourseHelper.xml"		# ���̰���������
	__cc_trigger_config = "config/client/help/HelpTrigger.xml"		# ���̰�������

	def __init__( self ) :
		_BaseHelper.__init__( self )

		self.__triggers = {}										# ���й��̰����Ĵ�����: { ( ��������, �������� ) : �������� }
		self.__histories = set()									# ������ʷ����
		self.__newHelps = []										# �µģ�δ�鿴�ģ���������( instance of Topic, ...)
		self.__closeTrigger = False									# �رհ�����ʾ

		self.__hintItems = {}										# Ҫ��ʾ�Ļ����Ʒ: { ��ƷID : �������� }


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __loadTriggers( self ) :
		"""
		�������а�����������ֵ
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

			# �����ǡ������Ʒ��������
			if ttype == "huodedaoju" :								# Ҫ��ʾ�Ļ�õ���
				itemsIDs = arg.split( ";" )							# ��ֵ����б�
				for itemID in itemsIDs :
					self.__hintItems[int( itemID )] = arg

	# -------------------------------------------------
	def __getTriggerTopics( self, key ) :
		"""
		��ȡ��������
		"""
		topics = []
		for topic in self.__triggers.get( key, [] ) :
			if topic.id not in self.__histories :
				topics.append( topic )
		return topics

	def __saveHistory( self, topic ) :
		"""
		����ǰ��ʾ����Ϊ��ʷ����
		"""
		parent = topic.parent
		while parent :												# ĳ�ڵ��Ѿ���ʾ��
			self.__histories.add( parent.id )						# �������и��ڵ㶼���Ϊ��ʾ��
			parent = parent.parent
		self.__histories.add( topic.id )
		BigWorld.player().base.addCourseHelpHistory( topic.id )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onRoleEnterWorld( self ) :
		"""
		����ҽ�������ʱ���ú��������ã�����������Ӧ��ɫ����ʷ��ʾ
		"""
		records = BigWorld.player().courseHelpRecords[:]					# ��ȡ��ʷ��¼
		if -1 in records :													# ������� -1
			self.__closeTrigger = True										# ����ζ�Ų��������̰���
			records.remove( -1 )											# �Ƴ���ǣ�ʣ�µľ��ǰ�����ʷ
		else :																# ��������� -1
			self.__closeTrigger = False										# ���ʾ�������̰���
		self.__histories = set( records )									# �����ʷ��¼
		ECenter.fireEvent( "EVT_ON_COURSE_HELP_TRIGGER_CHANGED", self.__closeTrigger )

	def onRoleLeaveWorld( self ) :
		"""
		����ɫ�뿪����ʱ�������ʾ��ʷ
		"""
		self.__historySect = None
		self.__histories.clear()
		self.__newHelps = []

	def onFirstSpaceReady( self ) :
		"""
		����ɫ�ӡ���ɫѡ�񡱵�������Ϸʱ������
		ע�����ﴥ����ɫ��һ�ν�����Ϸʱ��Ҫ��ʾ�İ���
		"""
		triggerKeys = [
			( "xitongxingwei", "denglu" ), 							# ��һ�ε�¼
			( "juesedengji", "1" ),									# һ����ʾ
			]
		for topic in self.__newHelps[:] :							# ȥ���Ѿ���ʾ��������
			if topic.id in self.__histories :
				self.__newHelps.remove( topic )
		for triggerKey in reversed( triggerKeys ) :
			topics = self.__getTriggerTopics( triggerKey )
			self.__newHelps = topics + self.__newHelps
		for topic in self.__newHelps :								# ��������дһ��ѭ���е�����
			self.__saveHistory( topic )								# ����Ԫ�ز��Ǻܶ࣬���Ϊ�˼����
			if not self.__closeTrigger :							# ���������Щ����
				ECenter.fireEvent( "EVT_ON_NEW_COURSE_HELP_ADDED", topic )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def initialize( self ) :
		"""
		��ȡ���ó�ʼ�����̰���( ResourseLoader �е��ó�ʼ�� )
		"""
		self.loadConfigs_( self.__cc_config )						# ���ع��̰�������
		self.__loadTriggers()										# ���ع��̰���������

	# -------------------------------------------------
	def getHistories( self ) :
		"""
		��ȡ������ʷ��ʾ����
		@rtype					: list
		@return					: ��������
		"""
		topicList = []
		for topicID in self.__histories :
			topic = self.getTopic( topicID )
			if not topic : continue
			topicList.append( topic )
		return topicList

	def getNewHelps( self ) :
		"""
		��ȡ�°�����ʾ
		@type					: list
		@return					: �µģ�δ�鿴�ģ���ʾ��������
		"""
		return self.__newHelps[:]

	def getFirstNewHelp( self ) :
		"""
		��ȡ����ʾ���������еĵ�һ����ʾ
		@type					: Topic
		@return					: ��ʾ��������
		"""
		if len( self.__newHelps ) :
			return self.__newHelps[0]
		return None

	# -------------------------------------------------
	def toggleTrigger( self ) :
		"""
		�����Ƿ񴥷�������ʾ
		"""
		self.__closeTrigger = not self.__closeTrigger
		BigWorld.player().base.addCourseHelpHistory( -1 )
		ECenter.fireEvent( "EVT_ON_COURSE_HELP_TRIGGER_CHANGED", self.__closeTrigger )

	def trigger( self, ttype, arg = "" ) :
		"""
		����һ����ʾ����
		@type			ttype : str
		@param			ttype : ���̰�����������
		@type			arg	  : str
		@param			arg	  : ��������
		@return				  : None
		"""
		triggerKey = ttype, str( arg )
		topics = self.__getTriggerTopics( triggerKey )
		if rds.statusMgr.isInWorld() :
			for topic in topics :
				self.__newHelps.append( topic )								# ׷��һ��Ϊ�鿴��ʾ
				self.__saveHistory( topic )									# ���浽��ʷ�б�
				if not self.__closeTrigger :								# �����ʾû�йر�
					ECenter.fireEvent( "EVT_ON_NEW_COURSE_HELP_ADDED", topic )
		else :
			for topic in topics :
				if topic not in self.__newHelps :
					self.__newHelps.append( topic )							# ׷��һ��Ϊ�鿴��ʾ

	def sinkNewHelp( self, topic ) :
		"""
		����Ҳ鿴��ĳ�����󣬵��øú���������������Ϊ��ʷ���⣬�Ӵ˲�����ʾ
		@type			topic : Topic
		@param			topic : Ҫ���µ��°�������
		@return				  : None
		"""
		if topic in self.__newHelps :
			self.__newHelps.remove( topic )
		else :
			DEBUG_MSG( "sink help fail, topic %d is not in new help!" % topic.id )


	# ----------------------------------------------------------------
	# ���������ӿ�
	# ----------------------------------------------------------------
	def roleUpgrade( self, level ) :
		"""
		��ɫ������ʾ
		@type				level : int
		@param					  : �ȼ�
		"""
		if ( "juesedengji", str( level ) ) in self.__triggers :
			courseHelper.trigger( "juesedengji", str( level ))

	def openWindow( self, wndName ) :
		"""
		�򿪴���
		@type				wndName : str
		@param				wndName : ��������
		@return						: None
		"""
		courseHelper.trigger( "dakaijiemian", wndName )

	def systemAction( self, action ) :
		"""
		ϵͳ��Ϊ
		�򿪴���
		@type				action : str
		@param				action : ��Ϊ����
		"""
		courseHelper.trigger( "xitongxingwei", action )

	def tongFamilyTrigger( self, arg ) :
		"""
		�����ᴥ����
		@type				arg : str
		@param				arg : ����
		"""
		courseHelper.trigger( "jiazubanghui", arg )

	def roleOperate( self, arg ) :
		"""
		��ɫ����
		@type				arg : str
		@param				arg : ����
		"""
		courseHelper.trigger( "juesecaozuo", arg )

	def interactive( self, target ) :
		"""
		NPC ����
		@type				target : str
		@param				target : ��������
		"""
		courseHelper.trigger( "npcjiaohu", target )

	def addItem( self, itemType ) :
		"""
		�����Ʒ������:���������ߡ�ҩƷ��������ߡ����������
		@type				itemType : int
		@param				itemType : ����
		"""
		arg = self.__hintItems.get( itemType, None )
		if arg is None : return
		courseHelper.trigger( "huodedaoju", arg )

	def petAction( self, action ) :
		"""
		������Ϊ
		@type				action : str
		@param				action : ��Ϊ����
		"""
		courseHelper.trigger( "chongwu", action )



# --------------------------------------------------------------------
# implement ui opertion helper
# --------------------------------------------------------------------
class UIOpHelper( _BaseHelper ) :
	"""
	UI ��������
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
		�ж�ָ���Ĳ�����ʾ�Ƿ����
		"""
		return rds.statusMgr.isInWorld() and \
			self.__tipsInfos.has_key( id )

	def getTips( self, id ) :
		"""
		��ȡһ��������ʾ
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

	__cc_quest_config = "config/client/help/QuestData.xml"				# �ȼ���������������

	class _Quest( object ) :											# ��ʱ������
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
		�����ҿ��Խ��ܵ�����ID�б�
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
		��ѯָ�����͵Ŀɽ�����
		"""
		quests = []
		strTypes = [ str( t ) for t in types ]
		_Quest = QuestHelper._Quest
		def handler( level, qSect ) :
			"""
			"""
			qType = str( qSect.readInt( "id" ) )[:3]						# ��������ID�ĳ����ǲ��̶��ģ����Բ���ʹ�ó���������
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
		�����ҿ��Խ��ܵ��������ͣ�Ĭ��������IDǰ��λΪ�������ͣ�
		@return		set of string
		"""
		types = set()
		def handler( level, qSect ) :
			"""
			"""
			qType = int( str( qSect.readInt( "id" ) )[:3] )					# ����ܱ���...�������õ�����ID�п������㿪ͷ����ID���Ȳ�ͳһ
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
		��ѯ�ɽ�����
		ע������ȼ���Χ��Ӧ���������еĵȼ���������������ĵȼ�
		@param		minLV		: ����ȼ�����
		@param		maxLV		: ����ȼ�����
		@param		profession	: ��������ְҵ
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
		��������ID��ѯ������Ϣ
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
		��������ID��ѯ������Ϣ
		@param		questIDs : iterable obj, ���������Ӱ��Ч�ʣ�
							   ��Ŀǰ��֪����set����������
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
		����ǰ������
		@param		quest		: ���ѯ������
		@param		profession	: ְҵҪ���ƺ��Ѿ�������
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
		������һ������
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
		����ָ���ȼ���Χ�ڵ�����
		ע������� queryAcceptableQuests �ӿڲ�ͬ������ȼ���Χ��Ӧ����
		������ĵȼ��������������еĵȼ�
		@param		minLV		: ����ȼ�����
		@param		maxLV		: ����ȼ�����
		@param		profession	: ְҵҪ���ƺ��Ѿ�������
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
		����������Ҫ������
		ע������ȼ���Χ��Ӧ���������еĵȼ���������������ĵȼ�
		@param		minLV		: ����ȼ�����
		@param		maxLV		: ����ȼ�����
		@param		handler		: �����������ĺ���
		"""
		sects = Language.openConfigSection( self.__cc_quest_config )
		if sects is None :
			ERROR_MSG( "open %s fail, check whether it is exist please!" % self.__cc_quest_config )
		else :
			LVList = range( minLV, maxLV + 1 )
			if 0 not in LVList : LVList.append( 0 )							# 0�����ǿɱ�ȼ�������Ҫ�ӽ�ȥ
			for level in LVList :
				qSubSects = sects[ str( level ) ]
				if qSubSects is None : continue
				for qSect in qSubSects.values() :
					if qSect.readString( "npcClassName" ) == "" : continue	# û�н�����NPC�����ú��ԣ���Ϊ������ĳ������õ�������ã����Բ����ڹ�������˵���ֻ�������ﴦ��
					if handler( level, qSect ) : return						# ֻҪ����������True���ͽ���

	def __checkAcceptable( self, qSect ) :
		"""
		���������Ƿ�ɽ���
		@param		qSect : ������Ϣ
		@type		qSect : PyDataSection
		"""
		# �������ID
		player = BigWorld.player()
		qID = qSect.readInt( 'id' )
		if player.isQuestCompleted( qID ) : return False
		if GUIFacade.hasQuestLog( qID ) : return False								# �����ɫ�����Ѿ��д�����
		strTypes = [ "60101","60207" ]
		if str( qID )[:5] in strTypes : return False								# ���ΰ���ճ����񡢰�ḱ�����񡢼����ճ����� --pj
		# ���ǰ������
		preQID = qSect.readInt( 'needFinishQuestID' )
		if preQID and not player.isQuestCompleted( preQID ) : return False
		# ���ְҵҪ��
		validClass = qSect.readInt( "player_class" )
		if validClass and validClass != ( player.getClass() >> 4 ) : return False
		# ���ǰ������
		qPreIDs = qSect.readString( 'needFinishOneOfThem' )
		if qPreIDs != "" :
			for idStr in qPreIDs.split(",") :
				if player.isQuestCompleted( int( idStr ) ) :
					break
			else :
				return False
		# �����������ȼ�Ҫ��
		maxLevel = qSect.readInt( "maxLevel" )
		if maxLevel and player.level > maxLevel : return False
		reqCamp = qSect.readInt( "reqCamp" )
		rCamp = player.getCamp()
		if reqCamp and rCamp != reqCamp: return False
		# ��黥������
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
	С�������
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
			��Ӻ��Ӱ�������
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
		��ʼ��С����ͻ�������
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
		��ȡĳ����������
		"""
		return self.__topics.get( topicID )

	def triggerSection( self, topicID ) :
		"""
		����ĳ����������
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
		����ĳ����������
		"""
		self.sinkTopicsLink()											# ����һ���µ�����ʱ�Ѿɵ�����ɾ��
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
	# С�������߹������
	# -------------------------------------------------
	def enableDirection( self, enable ) :
		"""
		����/�رվ���ָ��
		"""
		if self.__settingSect is None :
			ERROR_MSG( "Pixie setting section is None!" )
			return
		self.__settingSect.writeBool( "pixie_direct", enable )

	def enableGossip( self, enable ) :
		"""
		����/�رվ����л�
		"""
		if self.__settingSect is None :
			ERROR_MSG( "Pixie setting section is None!" )
			return
		self.__settingSect.writeBool( "pixie_gossip", enable )

	def visibleVIPFlag( self, visible ) :
		"""
		��ʾ/�ر�VIP��ʶ
		"""
		if self.__settingSect is None :
			ERROR_MSG( "Pixie setting section is None!" )
			return
		self.__settingSect.writeBool( "show_vip_flag", visible )

	# -------------------------------------------------
	def isInDirecting( self ) :
		"""
		�Ƿ�������ָ��
		"""
		if self.__settingSect is None :
			ERROR_MSG( "Pixie setting section is None!" )
			return
		return self.__settingSect.readBool( "pixie_direct", True )

	def isInGossipping( self ) :
		"""
		�Ƿ�����������
		"""
		if self.__settingSect is None :
			ERROR_MSG( "Pixie setting section is None!" )
			return
		return self.__settingSect.readBool( "pixie_gossip", True )

	def isVipFlagShow( self ) :
		"""
		�Ƿ���ʾVIP��ʶ
		"""
		if self.__settingSect is None :
			ERROR_MSG( "Pixie setting section is None!" )
			return
		return self.__settingSect.readBool( "show_vip_flag", True )

	# -------------------------------------------------
	def onRoleLeaveWorld( self ) :
		"""
		�������
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

