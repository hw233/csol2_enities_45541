# -*- coding: gb18030 -*-
#

import BigWorld
from bwdebug import *
import csdefine

_g_relationStaticObjClassMap = {}

class RelationStaticObjImpl:
	"""
	实现cell、client部份的RelationStaticObjImpl数据创建、还原
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
		relationObj = _g_relationStaticObjClassMap[ dict["objType"] ]()
		relationObj.loadFromPacket( dict )
		return sk

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return (obj is None) or isinstance( obj, RelationStaticObjImpl )
#--------------------------------------------------------------------------------------------------------------------------------------
class RelationStaticObjCamp( RelationStaticObjImpl ):
	"""
	普通阵营关系
	"""
	type = csdefine.RELATION_STATIC_CAMP
	def __init__( self ):
		self.friendRelationList = []
		self.neutralRelationList = []
		self.antagonizeRelationList = []
		pass

	def init( self, friendRelationList, neutralRelationList, antagonizeRelationList ):
		"""
		virtual method.
		"""
		self.friendRelationList = friendRelationList
		self.neutralRelationList = neutralRelationList
		self.antagonizeRelationList = antagonizeRelationList
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity1, entity2 ):
		"""
		virtual method.
		"""
		camp1 = entity1.getCombatCamp()
		camp2 = entity2.getCombatCamp()
		campList1 = ( camp1, camp2 )
		campList2 = ( camp2, camp1 )
		if campList1 in self.friendRelationList or campList2 in self.friendRelationList:
			return csdefine.RELATION_FRIEND
		elif campList1 in self.neutralRelationList or campList2 in self.neutralRelationList:
			return csdefine.RELATION_NEUTRALLY
		elif campList1 in self.antagonizeRelationList or campList2 in self.antagonizeRelationList:
			return csdefine.RELATION_ANTAGONIZE
		return csdefine.RELATION_NONE
		pass

	def addToPacket( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看RelationStaticObjImpl；
		"""
		return { "objType" : self.getType(), "param" : ( self.friendRelationList, self.neutralRelationList, self.antagonizeRelationList ) }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		self.friendRelationList, self.neutralRelationList, self.antagonizeRelationList = valDict[ "param" ]
		pass

#--------------------------------------------------------------------------------------------------------------------------------------
class RelationStaticObjCampFengHuo( RelationStaticObjImpl ):
	"""
	阵营烽火连天关系
	"""
	type = csdefine.RELATION_STATIC_CAMP_FENG_HUO
	def __init__( self ):
		pass

	def init( self ):
		"""
		virtual method.
		"""
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity1, entity2 ):
		"""
		virtual method.
		"""
		if entity1.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if entity2.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				if entity1.getCombatCamp() == entity2.getCombatCamp():
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
			else:
				if hasattr( entity2, "ownCamp" ) and entity2.ownCamp == entity1.getCombatCamp():
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
		else:
			if entity2.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				if hasattr( entity1, "ownCamp" ) and entity1.ownCamp == entity2.getCombatCamp():
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
			else:
				if hasattr( entity1, "ownCamp" ) and hasattr( entity2, "ownCamp" ) and entity1.ownCamp == entity2.ownCamp:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
		return csdefine.RELATION_NONE
		pass

	def addToPacket( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看RelationStaticObjImpl；
		"""
		return { "objType" : self.getType(), "param" : None }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		pass
		

#--------------------------------------------------------------------------------------------------------------------------------------
class RelationStaticObjTongFengHuoAndTerritory( RelationStaticObjImpl ):
	"""
	帮会烽火连天以及帮会领地关系模式
	"""
	type = csdefine.RELATION_STATIC_TONG_FENG_HUO_AND_TERRITORY
	def __init__( self ):
		pass

	def init( self ):
		"""
		virtual method.
		"""
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity1, entity2 ):
		"""
		virtual method.
		"""
		if entity1.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if entity2.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				if entity1.tong_dbID == entity2.tong_dbID:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
			else:
				if hasattr( entity2, "ownTongDBID" ) and entity2.ownTongDBID == entity1.tong_dbID:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
		else:
			if entity2.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				if hasattr( entity1, "ownTongDBID" ) and entity1.ownTongDBID == entity2.tong_dbID:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
			else:
				if hasattr( entity1, "ownTongDBID" ) and hasattr( entity2, "ownTongDBID" ) and entity1.ownTongDBID == entity2.ownTongDBID:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
		return csdefine.RELATION_NONE
		pass

	def addToPacket( self ): 
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看RelationStaticObjImpl；
		"""
		return { "objType" : self.getType(), "param" : None }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		pass

#--------------------------------------------------------------------------------------------------------------------------------------
class RelationStaticObjTongCityWar( RelationStaticObjImpl ):
	"""
	帮会城战关系
	"""
	type = csdefine.RELATION_STATIC_TONG_CITY_WAR
	def __init__( self ):
		pass

	def init( self ):
		"""
		virtual method.
		"""
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity1, entity2 ):
		"""
		virtual method.
		"""
		if entity1.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if entity2.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				if entity1.tong_dbID == entity2.tong_dbID:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
			else:
				if hasattr( entity2, "belong" ) and entity2.belong == entity1.tong_dbID:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
		else:
			if entity2.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				if hasattr( entity1, "belong" ) and entity1.belong == entity2.tong_dbID:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
			else:
				if hasattr( entity1, "belong" ) and hasattr( entity2, "belong" ) and entity1.belong == entity2.belong:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
		return csdefine.RELATION_NONE
		pass

	def addToPacket( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看RelationStaticObjImpl；
		"""
		return { "objType" : self.getType(), "param" : None }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		pass

#--------------------------------------------------------------------------------------------------------------------------------------
class RelationStaticObjYXLM( RelationStaticObjImpl ):
	"""
	英雄联盟副本关系
	"""
	type = csdefine.RELATION_STATIC_YXLM
	def __init__( self ):
		pass

	def init( self ):
		"""
		virtual method.
		"""
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity1, entity2 ):
		"""
		virtual method.
		"""
		if entity1.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if entity2.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				if hasattr( entity1, "teamID" ) and entity1.teamID and entity2.teamID and entity1.teamID == entity2.teamID:
					return csdefine.RELATION_FRIEND
				elif hasattr( entity1, "getTeamMailbox" ) and entity1.getTeamMailbox() and entity2.getTeamMailbox() and entity1.getTeamMailbox().id == entity2.getTeamMailbox().id:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
			if not entity2.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				if hasattr( entity2, "belong" ) and hasattr( entity1, "teamID" ) and entity2.belong == entity1.teamID:
					return csdefine.RELATION_FRIEND
				elif hasattr( entity2, "belong" ) and hasattr( entity1, "getTeamMailbox" ) and entity1.getTeamMailbox() and entity2.belong == entity1.getTeamMailbox().id:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
		else:
			if entity2.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				if hasattr( entity1, "belong" ) and hasattr( entity1, "teamID" ) and entity1.belong == entity2.teamID:
					return csdefine.RELATION_FRIEND
				elif hasattr( entity1, "belong" ) and hasattr( entity2, "getTeamMailbox" ) and entity2.getTeamMailbox() and entity1.belong == entity2.getTeamMailbox().id:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
			else:
				if hasattr( entity1, "belong" ) and hasattr( entity2, "belong" ) and entity1.belong == entity2.belong:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
		return csdefine.RELATION_NONE
		pass

	def addToPacket( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看RelationStaticObjImpl；
		"""
		return { "objType" : self.getType(), "param" : None }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		pass

#--------------------------------------------------------------------------------------------------------------------------------------
class RelationStaticObjYiJieZhanChang( RelationStaticObjImpl ):
	"""
	异界战场副本关系
	"""
	type = csdefine.RELATION_STATIC_YI_JIE_ZHAN_CHANG
	def __init__( self ):
		pass

	def init( self ):
		"""
		virtual method.
		"""
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity1, entity2 ):
		"""
		virtual method.
		"""
		if entity1.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if entity2.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				if entity1.yiJieFaction == entity2.yiJieFaction or entity1.yiJieAlliance == entity2.yiJieFaction:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
			else:
				if hasattr( entity2, "battleCamp" ) and entity1.yiJieFaction != 0 and entity2.battleCamp == entity1.yiJieFaction:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
		else:
			if entity2.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				if hasattr( entity1, "battleCamp" ) and entity2.yiJieFaction != 0 and entity1.battleCamp == entity2.yiJieFaction:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
			else:
				if hasattr( entity1, "battleCamp" ) and hasattr( entity2, "battleCamp" ) and entity1.battleCamp == entity2.battleCamp:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
		return csdefine.RELATION_NONE
		pass

	def addToPacket( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看RelationStaticObjImpl；
		"""
		return { "objType" : self.getType(), "param" : None }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		pass

#--------------------------------------------------------------------------------------------------------------------------------------
class RelationStaticObjTongCityWarFinal( RelationStaticObjImpl ):
	"""
	帮会城战决赛关系
	"""
	type = csdefine.RELATION_STATIC_TONG_CITY_WAR_FINAL
	def __init__( self ):
		pass

	def init( self ):
		"""
		virtual method.
		"""
		pass

	def getType( self ):
		"""
		virtual method.
		"""
		return self.type

	def queryCombatRelation( self, entity1, entity2 ):
		"""
		virtual method.
		"""
		if entity1.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if entity2.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				if hasattr( entity1, "queryTemp" ) and hasattr( entity2, "queryTemp" ) \
				and entity1.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ) !=0 and entity1.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ) == entity2.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ):
					return csdefine.RELATION_FRIEND
				elif hasattr( entity1, "checkCityWarTongBelong" ) and entity1.checkCityWarTongBelong( entity1.tong_dbID, entity2.tong_dbID ):
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
			else:
				if hasattr( entity2, "belong" ) and hasattr( entity1, "queryTemp" ) \
				and entity1.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ) !=0 and entity1.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ) == entity2.belong:
					return csdefine.RELATION_FRIEND
				elif hasattr( entity2, "belong" ) and hasattr( entity1, "getCityWarTongBelong" ) \
				and entity1.getCityWarTongBelong( entity1.tong_dbID ) == entity2.belong:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
		else:
			if entity2.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				if hasattr( entity1, "belong" ) and hasattr( entity2, "queryTemp" ) \
				and entity2.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ) !=0 and entity2.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ) == entity1.belong:
					return csdefine.RELATION_FRIEND
				elif hasattr( entity1, "belong" ) and hasattr( entity2, "getCityWarTongBelong" ) \
				and entity2.getCityWarTongBelong( entity1.tong_dbID ) == entity1.belong:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
			else:
				if hasattr( entity1, "belong" ) and hasattr( entity2, "belong" ) and entity1.belong == entity2.belong:
					return csdefine.RELATION_FRIEND
				else:
					return csdefine.RELATION_ANTAGONIZE
		return csdefine.RELATION_NONE
		pass

	def addToPacket( self ):
		"""
		virtual method.
		打包自身需要传输的数据，数据必须是一个dict，具体参数详看RelationStaticObjImpl；
		"""
		return { "objType" : self.getType(), "param" : None }

	def loadFromPacket( self, valDict ):
		"""
		load from Item type.

		@param valDict: dict
		@type  valDict: dict
		"""
		pass





# 自定义类型实现实例
instance = RelationStaticObjImpl()


_g_relationStaticObjClassMap[ csdefine.RELATION_STATIC_CAMP ] 									= RelationStaticObjCamp
_g_relationStaticObjClassMap[ csdefine.RELATION_STATIC_CAMP_FENG_HUO ] 							= RelationStaticObjCampFengHuo
_g_relationStaticObjClassMap[ csdefine.RELATION_STATIC_TONG_FENG_HUO_AND_TERRITORY ] 			= RelationStaticObjTongFengHuoAndTerritory
_g_relationStaticObjClassMap[ csdefine.RELATION_STATIC_TONG_CITY_WAR ] 							= RelationStaticObjTongCityWar
_g_relationStaticObjClassMap[ csdefine.RELATION_STATIC_YXLM ] 									= RelationStaticObjYXLM
_g_relationStaticObjClassMap[ csdefine.RELATION_STATIC_YI_JIE_ZHAN_CHANG ] 						= RelationStaticObjYiJieZhanChang
_g_relationStaticObjClassMap[ csdefine.RELATION_STATIC_TONG_CITY_WAR_FINAL ] 					= RelationStaticObjTongCityWarFinal


def createRelationObjCamp( friendRelationList, neutralRelationList, antagonizeRelationList ):
	inst = RelationStaticObjCamp()
	inst.init( friendRelationList, neutralRelationList, antagonizeRelationList )
	return inst
	
def createRelationObjSpace( type ):
	inst = _g_relationStaticObjClassMap[ type ]()
	inst.init()
	return inst
	

