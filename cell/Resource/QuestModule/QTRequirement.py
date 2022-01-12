# -*- coding: gb18030 -*-
#
# $Id: QTRequirement.py,v 1.22 2008/08/12 08:04:10 zhangyuxing Exp $

"""
"""

import csdefine
import cschannel_msgs
import ShareTexts as ST
import csconst
from bwdebug import *
import time
import Language
import BigWorld
from CrondScheme import *

# ӳ������ű���ʵ��������
# ��ӳ����Ҫ���ڴ������г�ʼ��ʵ��ʱʹ��
# key = Ŀ�������ַ�����ȡ�Ը����͵�������;
# value = �̳���QTRequirement���࣬���ڸ�������ʵ��������Ķ���
quest_requirement_type_maps = {}

def MAP_QUEST_REQUIRE_TYPE( classObj ):
	"""
	ӳ������Ŀ��������ʵ��������
	"""
	quest_requirement_type_maps[classObj.__name__] = classObj

def createRequirement( strType ):
	"""
	��������ʵ��

	@return: instance of QTRequirement or derive from it
	@type:   QTRequirement
	"""
	try:
		return quest_requirement_type_maps[strType]()
	except KeyError:
		ERROR_MSG( "can't create instance by %s type." % strType )
		return None

				
#���ڶ���
DAY_MAP = {0:"Monday",1:"Tuesday", 2:"Wednesday", 3:"Thursday", 4:"Friday", 5:"Saturday", 6:"Sunday"}


# ------------------------------------------------------------>
# abstract class
# ------------------------------------------------------------>
class QTRequirement:
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: ��ʼ������,������ʽ��ÿ��ʵ���Լ��涨
		@type  section: pyDataSection
		@return: None
		"""
		pass

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		pass

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		pass


# ------------------------------------------------------------>
# QTRQuestComplete�������ĳ����
# ------------------------------------------------------------>
class QTRQuestComplete( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._questID = section.readInt( "param1" )

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.questIsCompleted( self._questID )

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTROneOfQuestsComplete�������ĳЩ����֮һ
# ------------------------------------------------------------>
class QTROneOfQuestsComplete( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		"""
		questIDs = section.readString( "param1" )
		self.questsList = questIDs.split( "," )

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		for i in self.questsList:
			if playerEntity.questIsCompleted( int(i) ):
				return True
			
		return False

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRQuestHas���Ѿ�����ĳ������
# ------------------------------------------------------------>
class QTRQuestHas( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._questID = section.readInt( "param1" )

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.has_quest( self._questID )

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRQuestNotHas��û�н�ĳЩ�����е��κ�һ��
# ------------------------------------------------------------>
class QTRQuestNotHas( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._questIDs = section.readString( "param1" ).split( ";" )

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		for i in self._questIDs:
			if playerEntity.questIsCompleted( int(i) ) or playerEntity.has_quest( int(i) ):
				return False
		return True

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRLevel
# ------------------------------------------------------------>
class QTRLevel( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: minLevel, maxLevel; maxLevel is optional.
		@type  section: pyDataSection
		@return: None
		"""
		self._minLvl = section.readInt( "param1" )
		self._maxLvl = section.readInt( "param2" )

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if self._maxLvl > 0:
			return (playerEntity.level >= self._minLvl) and (playerEntity.level <= self._maxLvl)
		return playerEntity.level >= self._minLvl

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return cschannel_msgs.QUEST_INFO_1 % ( self._minLvl, self._maxLvl )


# ------------------------------------------------------------>
# QTRClass
# ------------------------------------------------------------>
class QTRClass( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: classValue��ֵΪRACES_MAP���֮һ�������
		@type  section: pyDataSection
		@return: None
		"""
		self._classes = section.readInt( "param1" ) << 4

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.getClass() == self._classes

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return cschannel_msgs.QUEST_INFO_2 % csconst.g_chs_class[self._classes]


# ------------------------------------------------------------>
# QTRSpecialFlag
# ------------------------------------------------------------>
class QTRSpecialFlag( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: flag, value
		@type  section: pyDataSection
		@return: None
		"""
		self._flag = section.readString( "param1" )
		self._value = section.readInt( "param2" )

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		try:
			mapping = playerEntity.getMapping()["questSpecialFlag"]
			value = mapping[self._flag]
		except KeyError:
			value = 0
		return value == self._value

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRTitle
# ------------------------------------------------------------>
class QTRTitle( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: titleID
		@type  section: pyDataSection
		@return: None
		"""
		self._title = section.readInt( "param1" )

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.hasTitle( self._title )

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRItem
# ------------------------------------------------------------>
class QTRItem( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: itemID, amount, isEquiped
		@type  section: pyDataSection
		@return: None
		"""
		self._itemID = section.readInt( "param1" )
		self._amount = section.readInt( "param2" )
		self._isEquiped = section.readBool( "param3" )

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if self._isEquiped:
			item = playerEntity.findItemFromEK_( self._itemID )
		else:
			item = playerEntity.findItemFromNKCK_( self._itemID )
		if item is None: return False
		return item.getAmount() >= self._amount

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRTeam
# ------------------------------------------------------------>
class QTRTeam( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: minMember, maxMember, isCaptain
		@type  section: pyDataSection
		@return: None
		"""
		self._minMember = section.readInt( "param1" )		# 0 ��ʾ������
		self._maxMember = section.readInt( "param2" )		# 0 ��ʾ������
		self._isCaptain = section.readInt( "param3" )		# 0 ��ʾ������

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if self._minMember > 0 and playerEntity.getTeamCount() < self._minMember: return False
		if self._maxMember > 0 and playerEntity.getTeamCount() > self._maxMember: return False
		if self._isCaptain > 0 and not playerEntity.isTeamCaptain(): return False
		return True

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRSkill
# ------------------------------------------------------------>
class QTRSkill( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: skillID
		@type  section: pyDataSection
		@return: None
		"""
		self._skillID = section.readInt( "param1" )

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.hasSkill( self._skillID )

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRBuff
# ------------------------------------------------------------>
class QTRBuff( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: skillID
		@type  section: pyDataSection
		@return: None
		"""
		self._skillID = section.readInt( "param1" )

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return len( playerEntity.findBuffsByBuffID( self._skillID ) ) > 0

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""

# ------------------------------------------------------------>
# QTRWithoutBuff
# ------------------------------------------------------------>
class QTRWithoutBuff( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: skillID
		@type  section: pyDataSection
		@return: None
		"""
		self._buffID = section.readInt( "param1" )

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return not len( playerEntity.findBuffsByBuffID( self._buffID ) ) > 0

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""

# ------------------------------------------------------------>
# QTRPKSwitch
# ------------------------------------------------------------>
class QTRPKSwitch( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: status; 0 == �ر�PK��1 == ��PK
		@type  section: pyDataSection
		@return: None
		"""
		self._status = section.readBool( "param1" )

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.pkSwitch == self._status

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRPKValue
# ------------------------------------------------------------>
class QTRPKValue( QTRequirement ):
	LT = -1		# С��
	EQ = 0		# ����
	BT = 1		# ����
	# �����õ����������˳�����Ҫ
	MAP_STATUS = [
				lambda player, value: player.pkValue < value,
				lambda player, value: player.pkValue == value,
				lambda player, value: player.pkValue > value,
			]
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: value, status; status == 0 ��ȣ�1 ���ڣ�-1 С��
		@type  section: pyDataSection
		@return: None
		"""
		self._value = section.readInt( "param1" )
		self._status = self.EQ
		status = section.readInt( "param2" )
		if status > 0:
			self._status = self.BT
		elif status < 0:
			self._status = self.LT

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return self.MAP_STATUS[self._status + 1]( playerEntity, self._value )

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRGroupQuestHas���Ѿ�����ĳ���������������
# ------------------------------------------------------------>
class QTRGroupQuestHas( QTRQuestHas ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._groupQuestID = section.readInt( "param1" )								#������ID
		self._subQuestID = section.readInt( "param2" )									#������ID

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.has_quest( self._groupQuestID ) and playerEntity.getQuestTasks( self._groupQuestID ).query( "subQuestID" ) == self._subQuestID

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""



class QTRFamily( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	
	
	def query( self, player ):
		"""
		"""
		return player.isJoinFamily()



class QTRNormalDartCount( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	
	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._count = section.readInt( "param1" )								#��ͨ���ڴ���
	
	def query( self, player ):
		"""
		"""
		date = time.localtime()[2]
		if date != player.questNormalDartRecord.date:
			player.questNormalDartRecord.date = date
			player.questNormalDartRecord.dartCount = 0
		return player.questNormalDartRecord.dartCount == self._count

class QTRExpDartCount( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	
	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._count = section.readInt( "param1" )								#�������ڴ���
	
	def query( self, player ):
		"""
		"""
		date = time.localtime()[2]
		if date != player.questExpDartRecord.date:
			player.questExpDartRecord.date = date
			player.questExpDartRecord.dartCount = 0
		return player.questExpDartRecord.dartCount == self._count


class QTRFamilyDartCount( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	
	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._count = section.readInt( "param1" )								#�������ڴ���
	
	def query( self, player ):
		"""
		"""
		date = time.localtime()[2]
		if date != player.questFamilyDartRecord.date:
			player.questFamilyDartRecord.date = date
			player.questFamilyDartRecord.dartCount = 0
		return player.questFamilyDartRecord.dartCount == self._count


class QTRTongDartCount( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	
	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		# ���ÿ����Կ���������ڴ���Ϊ�������������������/10
		pass
	
	def query( self, player ):
		"""
		"""
		if player.tong_dbID <= 0:
			return False
		date = time.localtime()[2]
		if date != player.questTongDartRecord.date:
			player.questTongDartRecord.date = date
			player.questTongDartRecord.dartCount = 0
		return player.questTongDartRecord.dartCount < 1		# CSOL-2118 �������ÿ��ÿ��ֻ�ܽ�һ��


class QTRDartPrestige( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	
	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._param1 = section.readInt( "param1" )								#����ֵ
		self._param2 = section.readInt( "param2" )								#����ֵ
	
	def query( self, player ):
		"""
		"""
		return player.getPrestige( self._param1 ) >= self._param2



class QTRQuestNotComplete( QTRequirement ):
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self._questID = section.readInt( "param1" )

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		quest = playerEntity.getQuest( self._questID )
		if quest.getStyle() == csdefine.QUEST_STYLE_FIXED_LOOP:
			lpLog = playerEntity.getLoopQuestLog( self._questID, True )
			if not lpLog.checkStartTime():
				# �����������뵱ǰʱ�䲻��ͬһ�죬Ҳ�ͱ�ʾ��Ҫ��������״̬
				lpLog.reset()
			if lpLog.getDegree() >= quest._finish_count:
				# ���������������࣬�������ٽ�
				return False
		
		return not playerEntity.questIsCompleted( self._questID )

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""
		

# ���ݲ߻��������������̵ȼ�����ҿ��������Ĵ���û����ϵ
class QTRMerchantTongReq( QTRequirement ):
	def __init__( self ):
		"""
		һ������������
		"""
		pass

	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self.questID = section.readInt( "param1" )					#����ID
		self.merlevel = section.readInt( "param2" )					#���̵ȼ�


	def query( self, playerEntity ):
		"""
		�ж�playerEntity�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if not playerEntity.isJoinTong():
			return False
		return True

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""


class QTRTongDutyReq( QTRequirement ):
	"""
		���ְ������
	"""
	
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: questID
		@type  section: pyDataSection
		@return: None
		"""
		self.tongDuty = section.readInt( "param1" )	# ���ְ��

	def query( self, playerEntity ):
		"""
		�ж�playerEntity�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.isJoinTong() and playerEntity.tong_grade == self.tongDuty

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""


# ------------------------------------------------------------>
# QTRPrestige
# ------------------------------------------------------------>
class QTRPrestige( QTRequirement ):
	def __init__( self ):
		pass


	def init( self, section ):
		"""
		@param section: format: minLevel, maxLevel; maxLevel is optional.
		@type  section: pyDataSection
		@return: None
		"""
		self._factionID = section.readInt( "param1" )	# ����ID
		self._maxValue = section.readInt( "param2" )	# �������ֵ
		self._minValue = section.readInt( "param3" )	# ������Сֵ

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		return playerEntity.getPrestige( self._factionID ) < self._maxValue


# ------------------------------------------------------------>
# QTRFixTime
# ------------------------------------------------------------>
class QTRActivityFixTime( QTRequirement ):
	def __init__( self ):
		pass


	def init( self, section ):
		"""
		@param section: format: minLevel, maxLevel; maxLevel is optional.
		@type  section: pyDataSection
		@return: None
		"""
		self._type = section.readInt( "param1" ) #_type ���� 3(����)��4(����)��5(����)
		self._longM = section.readInt( "param2" ) #����
		
	def query( self, playerEntity ):
		"""
		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if self._type == csdefine.ACTIVITY_EXAMINATION_XIANGSHI:
			return BigWorld.globalData.has_key( "AS_XiangshiActivityStart" )
		if self._type == csdefine.ACTIVITY_EXAMINATION_HUISHI:
			return BigWorld.globalData.has_key( "AS_HuishiActivityStart" )
		if self._type == csdefine.ACTIVITY_EXAMINATION_DIANSHI:
			return BigWorld.globalData.has_key( "AS_DianshiActivityStart" )
		return False
			

class QTRTong( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	

	def query( self, player ):
		"""
		"""
		return player.isJoinTong()



# ------------------------------------------------------------>
# QTRGruopConuntRqt
# ------------------------------------------------------------>
class QTRGruopConuntRqt( QTRequirement ):
	"""
	��Ҫ��������������������ĸû����������������ƾͲ���ʾ��ɫ̾���ˣ�
	"""
	def __init__( self ):
		pass

	def init( self, section ):
		"""
		@param section: format: classValue��ֵΪRACES_MAP���֮һ�������
		@type  section: pyDataSection
		@return: None
		"""
		self._questID = section.readInt( "param1" )
		self._reapeatTime = section.readInt( "param2" )

	def query( self, playerEntity ):
		"""
		�ж�player�Ƿ����Ҫ��

		@param playerEntity: ���entityʵ��
		@type  playerEntity: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		if not playerEntity.checkStartGroupTime( self._questID ):
			return True
		
		if self._reapeatTime <= playerEntity.getGroupQuestCount( self._questID ) and playerEntity.isGroupQuestRecorded( self._questID ):
			playerEntity.resetGroupQuest( self._questID )
			playerEntity.setGroupQuestRecorded( self._questID, False )
		
		if self._reapeatTime <= playerEntity.getGroupQuestCount( self._questID ):
			if not playerEntity.newDataGroupQuest( self._questID ):
				return False
		return True

	def getDetail( self ):
		"""
		����Ҫ����ص�����

		@return: String
		@rtype:  String
		"""
		return ""


class QTRInTongTerritory( QTRequirement ):
	"""
	"""
	def __init__( self, *args ):
		pass
	

	def query( self, player ):
		"""
		"""
		id = player.getCurrentSpaceBase().id
		spaceEntity = BigWorld.entities.get( id )
		if spaceEntity.isReal():
			if "tongDBID" in spaceEntity.params and spaceEntity.params[ "tongDBID" ] == player.tong_dbID:
				return True
		
		return False


class QTRInTime( QTRequirement ):
	"""
	�Ƿ���ָ��ʱ����
	ע����������NPCͷ��������ͨ��AI��������
	"""
	def __init__( self, *args ):
		"""
		"""
		pass


	def init( self, section ):
		"""
		@param section: format: minLevel, maxLevel; maxLevel is optional.
		@type  section: pyDataSection
		@return: None
		"""
		self._cmd = section.readString( "param1" )			# scheme �ַ��� �磺" * * 3 * *" (�μ� CrondScheme.py)
		self._presistMinute = section.readInt( "param2" )	# ����ʱ��
		self.scheme = Scheme()
		self.scheme.init( self._cmd )

	def query( self, player ):
		"""
		"""
		year, month, day, hour, minute = time.localtime( time.time() - self._presistMinute * 60 )[:5]
		nextTime = self.scheme.calculateNext( year, month, day, hour, minute )
		if nextTime < time.time():
			return True
		return False

class QTRCamp( QTRequirement ):
	"""
	�Ƿ�����ĳ��Ӫ
	"""
	def __init__( self, *args ):
		"""
		"""
		self._camp = csdefine.ENTITY_CAMP_NONE

	def init( self, section ):
		"""
		@param section: format: minLevel, maxLevel; maxLevel is optional.
		@type  section: pyDataSection
		@return: None
		"""
		self._camp = section.readInt( "param1" )

	def query( self, player ):
		"""
		"""
		return self._camp == player.getCamp()

#-------------------------------------------------------------
# QTRCampActivityCondition
#-------------------------------------------------------------

class QTRCampActivityCondition( QTRequirement ):
	"""
	��Ӫ������ĵ�ͼ�������Ƿ��������Ҫ��
	"""
	def __init__( self, *args ):
		"""
		"""
		self._spaceName = ""
		self._activityType = ""

	def init( self, section ):
		"""
		@type  section: pyDataSection
		@return: None
		"""
		self._spaceName = section.readString( "param1" )
		self._activityType = section.readString( "param2" )

	def query( self, player ):
		"""
		"""
		if not BigWorld.globalData.has_key( "CampActivityCondition" ):
			return False
			
		temp = BigWorld.globalData["CampActivityCondition"]
		
		if self._spaceName != "" and self._spaceName not in temp[0]:
			return False
		
		if self._activityType != "":
			types = [ int( i ) for i in self._activityType.split( "," ) ]		# ����ƥ����ֻ
			if temp[1] not in types:
				return False
			
		return True


# ע�������
MAP_QUEST_REQUIRE_TYPE( QTRClass )			# CLASS_*
MAP_QUEST_REQUIRE_TYPE( QTRQuestComplete )	# questID
MAP_QUEST_REQUIRE_TYPE( QTRQuestHas )		# questID
MAP_QUEST_REQUIRE_TYPE( QTRQuestNotHas )	# questID
MAP_QUEST_REQUIRE_TYPE( QTRLevel )			# minLevel, maxLevel; maxLevel�ǿ�ѡ��.
MAP_QUEST_REQUIRE_TYPE( QTRSpecialFlag )	# flag, value
MAP_QUEST_REQUIRE_TYPE( QTRTitle )			# titleID
MAP_QUEST_REQUIRE_TYPE( QTRItem )			# itemID, itemAmount, isEquiped; isEquiped eq 0 ��ʾ�жϵ�����ͨ��Ʒ��,�����ʾ�жϵ���װ����.
MAP_QUEST_REQUIRE_TYPE( QTRTeam )			# minMember, maxMember, isCaptain; all param value eq 0 that point to not check.
MAP_QUEST_REQUIRE_TYPE( QTRSkill )			# skillID
MAP_QUEST_REQUIRE_TYPE( QTRBuff )			# skillID
MAP_QUEST_REQUIRE_TYPE( QTRWithoutBuff )	# skillID
MAP_QUEST_REQUIRE_TYPE( QTRPKSwitch )		# status; 0 == �ر�PK��1 == ��PK
MAP_QUEST_REQUIRE_TYPE( QTRPKValue )		# value, status; status == 0 ��ȣ�1 ���ڣ�-1 С��
MAP_QUEST_REQUIRE_TYPE( QTRGroupQuestHas )		# questID
MAP_QUEST_REQUIRE_TYPE(QTRFamily)
MAP_QUEST_REQUIRE_TYPE(QTRNormalDartCount)
MAP_QUEST_REQUIRE_TYPE(QTRExpDartCount)
MAP_QUEST_REQUIRE_TYPE(QTRFamilyDartCount)
MAP_QUEST_REQUIRE_TYPE(QTRTongDartCount)
MAP_QUEST_REQUIRE_TYPE(QTRDartPrestige)
MAP_QUEST_REQUIRE_TYPE(QTRQuestNotComplete)
MAP_QUEST_REQUIRE_TYPE(QTRMerchantTongReq)	# ���̵ȼ������ȼ���Ӧ�����������
MAP_QUEST_REQUIRE_TYPE(QTRPrestige)
MAP_QUEST_REQUIRE_TYPE(QTRActivityFixTime)
MAP_QUEST_REQUIRE_TYPE(QTRTong)				# ��Ҫ������
MAP_QUEST_REQUIRE_TYPE(QTRTongDutyReq)		# ��Ҫ���ְ��
MAP_QUEST_REQUIRE_TYPE( QTROneOfQuestsComplete )	#���һ�������е�����һ���������
MAP_QUEST_REQUIRE_TYPE( QTRGruopConuntRqt )		# ��Ҫ��������������������ĸû����������������ƾͲ���ʾ��ɫ̾���ˣ�
MAP_QUEST_REQUIRE_TYPE( QTRInTongTerritory )	#�Ƿ��������������
MAP_QUEST_REQUIRE_TYPE( QTRInTime )				#�Ƿ���ָ��ʱ�����
MAP_QUEST_REQUIRE_TYPE( QTRCamp )				#�Ƿ�����ĳ��Ӫ
MAP_QUEST_REQUIRE_TYPE( QTRCampActivityCondition )				# ��Ӫ������ĵ�ͼ�������Ƿ��������Ҫ��

#
# $Log: QTRequirement.py,v $
# Revision 1.22  2008/08/12 08:04:10  zhangyuxing
# no message
#
# Revision 1.21  2008/08/12 01:33:57  zhangyuxing
# ���Ӽ������������
#
# Revision 1.20  2008/08/09 01:50:39  wangshufeng
# ��Ʒid���͵�����STRING -> INT32,��Ӧ�������롣
#
# Revision 1.19  2008/07/31 03:45:27  zhangyuxing
# no message
#
# Revision 1.18  2008/07/30 07:30:07  zhangyuxing
# �޸�һ�� self._id �Ĵ������
#
# Revision 1.17  2008/07/30 05:56:36  zhangyuxing
# ���ӻ�������������
#
# Revision 1.16  2008/04/03 06:31:33  phw
# KitbagBase::find2All()����Ϊfind()�������ķ���ֵ��ԭ����( order, toteID, itemInstance )��ΪitemInstance
# KitbagBase::findAll2All()����ΪfindAll()�������ķ���ֵ��ԭ����( order, toteID, itemInstance )��ΪitemInstance
# �������ϵı仯���������ʹ�õ����ϽӿڵĴ���
#
# Revision 1.15  2007/12/06 07:43:05  phw
# �޸��˳�ʼ����ʽ����ԭ�����ַ���������Ϊsectionʵ������
#
# Revision 1.14  2007/11/28 00:38:48  phw
# ����QTRPKValue��MAP_STATUS���﷨����
#
# Revision 1.13  2007/11/27 09:26:58  phw
# class removed: QTRRace, QTRQuest
# class added: QTRQuestComplete, QTRQuestHas, QTRQuestNotHas, QTRBuff, QTRPKSwitch, QTRPKValue,
#
# Revision 1.12  2007/11/27 01:52:00  phw
# ����ְҵ��������ǰ׺'CLASS_'�������Ա��������ǰ׺'GENDER_'����ԭ����սʿ'FIGHTER'��Ϊ'CLASS_FIGHTER'��������ͬ
#
# Revision 1.11  2007/11/02 03:59:51  phw
# ��ԭ����__init__.py�е�ʵ��������Ϊ��ģ���Լ�������
#
# Revision 1.10  2007/06/14 09:59:20  huangyongwei
# ���������˺궨��
#
# Revision 1.9  2006/08/05 08:31:02  phw
# �޸Ľӿڣ�
#     QTRItem::query();
#     from: return item[2].amount >= self._amount
#     to:   return item[2].getAmount() >= self._amount
#
# Revision 1.8  2006/08/02 03:15:15  phw
# �޸Ľӿڣ�
#     QTRSkill::init(); ������û��ת���ַ�������Ϊ������BUG
# ɾ����from Resource.QuestLoader import QuestsFlyweight
#
# Revision 1.7  2006/04/06 06:50:26  phw
# ���뽱�����ܺͼ�����Ҫ�ж�
#
# Revision 1.6  2006/03/28 09:49:23  phw
# �������Һ�ְҵ����ȡֵ����ȷ��BUG
#
# Revision 1.5  2006/03/25 07:36:34  phw
# fix QTRLevel and QTRQuest
#
# Revision 1.4  2006/03/22 02:27:00  phw
# �޸��˶��ѽ������Ĭ��״̬
#
# Revision 1.3  2006/03/10 05:15:14  phw
# �������µ�������
#
# Revision 1.2  2006/03/07 10:00:49  phw
# ����QTRQuest,֧��0 û�н�; 1 �ѽ�; 2 �����
#
# Revision 1.1  2006/01/24 02:20:50  phw
# no message
#
#