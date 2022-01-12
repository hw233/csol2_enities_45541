# -*- coding: gb18030 -*-
#

import BigWorld
from bwdebug import *
import csdefine

_g_relationDynamicObjClassMap = {}

class RelationDynamicObjImpl:
	"""
	ʵ��cell��client���ݵ�RelationDynamicObjImpl���ݴ�������ԭ
	"""
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		if obj == None:
			return { "objType" : 0, "param" : None }
		return obj.addToPacket()

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		relationObj = _g_relationDynamicObjClassMap[ dict["objType"] ]()
		relationObj.loadFromPacket( dict )
		return relationObj

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return (obj is None) or isinstance( obj, RelationDynamicObjImpl )
#--------------------------------------------------------------------------------------------------------------------------------------
class RelationObjPersonalAntagonizeID( RelationDynamicObjImpl ):
	"""
	�����ж�ID��ϵ
	"""
	type = csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_ID
	def __init__( self ):
		self._enemyID = 0
		pass

	def init( self, enemyID ):
		"""
		virtual method.
		"""
		self._enemyID = enemyID
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity ):
		"""
		virtual method.
		"""
		if entity.id == self._enemyID:
			return csdefine.RELATION_ANTAGONIZE
		return csdefine.RELATION_NONE
		pass

	def getID( self ):
		"""
		��ȡ�ж���ҵ�ID
		"""
		return self._enemyID

	def addToPacket( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTargetObjImpl��
		"""
		return { "objType" : self.getType(), "param" : self._enemyID }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self._enemyID = valDict[ "param" ]
		pass

#--------------------------------------------------------------------------------------------------------------------------------------
class RelationObjPersonalFriendID( RelationDynamicObjImpl ):
	"""
	�����Ѻ�ID��ϵ
	"""
	type = csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID
	def __init__( self ):
		self._friendID = 0
		pass

	def init( self, friendID ):
		"""
		virtual method.
		"""
		self._friendID = friendID
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity ):
		"""
		virtual method.
		"""
		if entity.id == self._friendID:
			return csdefine.RELATION_FRIEND
		return csdefine.RELATION_NONE
		pass

	def getID( self ):
		"""
		��ȡ�ж���ҵ�ID
		"""
		return self._friendID

	def addToPacket( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTargetObjImpl��
		"""
		return { "objType" : self.getType(), "param" : self._friendID }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self._friendID = valDict[ "param" ]
		pass

#--------------------------------------------------------------------------------------------------------------------------------------
class RelationObjPersonalAntagonizeDBID( RelationDynamicObjImpl ):
	"""
	�����ж�DBID��ϵ
	"""
	type = csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_DBID
	def __init__( self ):
		self._antagonizeDBID = 0
		pass

	def init( self, antagonizeDBID ):
		"""
		virtual method.
		"""
		self._antagonizeDBID = antagonizeDBID
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity ):
		"""
		virtual method.
		"""
		if entity.databaseID == self._antagonizeDBID:
			return csdefine.RELATION_ANTAGONIZE
		return csdefine.RELATION_NONE
		pass

	def getID( self ):
		"""
		��ȡ�ж���ҵ�ID
		"""
		return self._antagonizeDBID

	def addToPacket( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTargetObjImpl��
		"""
		return { "objType" : self.getType(), "param" : self._antagonizeDBID }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self._antagonizeDBID = valDict[ "param" ]
		pass

#--------------------------------------------------------------------------------------------------------------------------------------
class RelationObjPersonalFriendDBID( RelationDynamicObjImpl ):
	"""
	�����Ѻ�DBID��ϵ
	"""
	type = csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_DBID
	def __init__( self ):
		self._friendDBID = 0
		pass

	def init( self, friendDBID ):
		"""
		virtual method.
		"""
		self._friendDBID = friendDBID
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity ):
		"""
		virtual method.
		"""
		if entity.databaseID == self._friendDBID:
			return csdefine.RELATION_FRIEND
		return csdefine.RELATION_NONE
		pass

	def getID( self ):
		"""
		��ȡ�ж���ҵ�ID
		"""
		return self._friendDBID

	def addToPacket( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTargetObjImpl��
		"""
		return { "objType" : self.getType(), "param" : self._friendDBID }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self._friendDBID = valDict[ "param" ]
		pass

#--------------------------------------------------------------------------------------------------------------------------------------
class RelationObjTeamAntagonize( RelationDynamicObjImpl ):
	"""
	�жԶ����ϵ
	"""
	type = csdefine.RELATION_DYNAMIC_TEAM_ANTAGONIZE
	def __init__( self ):
		self._teamID = 0
		pass

	def init( self, teamID ):
		"""
		virtual method.
		"""
		self._teamID = teamID
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity ):
		"""
		virtual method.
		"""
		if hasattr( entity, "teamID" ) and entity.teamID and entity.teamID == self._teamID:
			return csdefine.RELATION_ANTAGONIZE
		elif hasattr( entity, "getTeamMailbox" ) and entity.getTeamMailbox() and entity.getTeamMailbox().id == self._teamID:
			return csdefine.RELATION_ANTAGONIZE
		return csdefine.RELATION_NONE
		pass

	def getID( self ):
		"""
		��ȡ�ж���ҵ�ID
		"""
		return self._teamID

	def addToPacket( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTargetObjImpl��
		"""
		return { "objType" : self.getType(), "param" : self._teamID }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self._teamID = valDict[ "param" ]
		pass

#--------------------------------------------------------------------------------------------------------------------------------------
class RelationObjTeamFriend( RelationDynamicObjImpl ):
	"""
	�Ѻö����ϵ
	"""
	type = csdefine.RELATION_DYNAMIC_TEAM_FRIEND
	def __init__( self ):
		self._teamID = 0
		pass

	def init( self, teamID ):
		"""
		virtual method.
		"""
		self._teamID = teamID
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity ):
		"""
		virtual method.
		"""
		if hasattr( entity, "teamID" ) and entity.teamID and entity.teamID == self._teamID:
			return csdefine.RELATION_FRIEND
		elif hasattr( entity, "getTeamMailbox" ) and entity.getTeamMailbox() and entity.getTeamMailbox().id == self._teamID:
			return csdefine.RELATION_FRIEND
		return csdefine.RELATION_NONE
		pass

	def getID( self ):
		"""
		��ȡ�ж���ҵ�ID
		"""
		return self._teamID

	def addToPacket( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTargetObjImpl��
		"""
		return { "objType" : self.getType(), "param" : self._teamID }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self._teamID = valDict[ "param" ]
		pass

#--------------------------------------------------------------------------------------------------------------------------------------
class RelationObjTongAntagonize( RelationDynamicObjImpl ):
	"""
	�ж԰���ϵ
	"""
	type = csdefine.RELATION_DYNAMIC_TONG_ANTAGONIZE
	def __init__( self ):
		self._tongID = 0
		pass

	def init( self, tongID ):
		"""
		virtual method.
		"""
		self._tongID = tongID
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity ):
		"""
		virtual method.
		"""
		if hasattr( entity, "tong_dbID" ) and entity.tong_dbID and entity.tong_dbID == self._tongID:
			return csdefine.RELATION_ANTAGONIZE

		return csdefine.RELATION_NONE
		pass

	def getID( self ):
		"""
		��ȡ�ж���ҵ�ID
		"""
		return self._tongID

	def addToPacket( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTargetObjImpl��
		"""
		return { "objType" : self.getType(), "param" : self._tongID }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self._tongID = valDict[ "param" ]
		pass

#--------------------------------------------------------------------------------------------------------------------------------------
class RelationObjTongFriend( RelationDynamicObjImpl ):
	"""
	�Ѻð���ϵ
	"""
	type = csdefine.RELATION_DYNAMIC_TONG_FRIEND
	def __init__( self ):
		self._tongID = 0
		pass

	def init( self, tongID ):
		"""
		virtual method.
		"""
		self._tongID = tongID
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity ):
		"""
		virtual method.
		"""
		if hasattr( entity, "tong_dbID" ) and entity.tong_dbID and entity.tong_dbID == self._tongID:
			return csdefine.RELATION_FRIEND

		return csdefine.RELATION_NONE
		pass

	def getID( self ):
		"""
		��ȡ�ж���ҵ�ID
		"""
		return self._tongID

	def addToPacket( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTargetObjImpl��
		"""
		return { "objType" : self.getType(), "param" : self._tongID }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self._tongID = valDict[ "param" ]
		pass

#--------------------------------------------------------------------------------------------------------------------------------------
class RelationObjCombatCampAntagonize( RelationDynamicObjImpl ):
	"""
	�ж�ս����Ӫ��ϵ
	"""
	type = csdefine.RELATION_DYNAMIC_COMBAT_CAMP_ANTAGONIZE
	def __init__( self ):
		self._camp = 0
		pass

	def init( self, camp ):
		"""
		virtual method.
		"""
		self._camp = camp
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity ):
		"""
		virtual method.
		"""
		if hasattr( entity, "getCombatCamp" ) and entity.getCombatCamp() and entity.getCombatCamp() == self._camp:
			return csdefine.RELATION_ANTAGONIZE

		return csdefine.RELATION_NONE
		pass

	def getID( self ):
		"""
		��ȡ�ж���ҵ�ID
		"""
		return self._camp

	def addToPacket( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTargetObjImpl��
		"""
		return { "objType" : self.getType(), "param" : self._camp }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self._camp = valDict[ "param" ]

#--------------------------------------------------------------------------------------------------------------------------------------
class RelationObjCombatCampFriend( RelationDynamicObjImpl ):
	"""
	�Ѻ�ս����Ӫ��ϵ
	"""
	type = csdefine.RELATION_DYNAMIC_COMBAT_CAMP_FRIEND
	def __init__( self ):
		self._camp = 0
		pass

	def init( self, camp ):
		"""
		virtual method.
		"""
		self._camp = camp
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity ):
		"""
		virtual method.
		"""
		if hasattr( entity, "getCombatCamp" ) and entity.getCombatCamp() and entity.getCombatCamp() == self._camp:
			return csdefine.RELATION_FRIEND

		return csdefine.RELATION_NONE
		pass

	def getID( self ):
		"""
		��ȡ�ж���ҵ�ID
		"""
		return self._camp

	def addToPacket( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTargetObjImpl��
		"""
		return { "objType" : self.getType(), "param" : self._camp }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self._camp = valDict[ "param" ]
		pass


_g_relationDynamicObjClassMap[ csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_ID ] 			= RelationObjPersonalAntagonizeID
_g_relationDynamicObjClassMap[ csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_ID ] 			= RelationObjPersonalFriendID
_g_relationDynamicObjClassMap[ csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_DBID ] 			= RelationObjPersonalAntagonizeDBID
_g_relationDynamicObjClassMap[ csdefine.RELATION_DYNAMIC_PRESONAL_FRIEND_DBID ] 			= RelationObjPersonalFriendDBID
_g_relationDynamicObjClassMap[ csdefine.RELATION_DYNAMIC_TEAM_ANTAGONIZE ] 			= RelationObjTeamAntagonize
_g_relationDynamicObjClassMap[ csdefine.RELATION_DYNAMIC_TEAM_FRIEND ] 			= RelationObjTeamFriend
_g_relationDynamicObjClassMap[ csdefine.RELATION_DYNAMIC_TONG_ANTAGONIZE ] 			= RelationObjTongAntagonize
_g_relationDynamicObjClassMap[ csdefine.RELATION_DYNAMIC_TONG_FRIEND ] 			= RelationObjTongFriend
_g_relationDynamicObjClassMap[ csdefine.RELATION_DYNAMIC_COMBAT_CAMP_ANTAGONIZE ] 			= RelationObjCombatCampAntagonize
_g_relationDynamicObjClassMap[ csdefine.RELATION_DYNAMIC_COMBAT_CAMP_FRIEND ] 			= RelationObjCombatCampFriend

def createRelationObjSpecial( type, id ):
	inst = _g_relationDynamicObjClassMap[ type ]()
	inst.init( id )
	return inst

# �Զ�������ʵ��ʵ��
instance = RelationDynamicObjImpl()
