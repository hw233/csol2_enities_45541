# -*- coding: gb18030 -*-
#
# $Id: CellPetDict.py,v 1.6 2008-08-06 07:13:58 huangyongwei Exp $

"""
This module implements the pet entity.

2007/12/04: writen by huangyongwei
"""

import csdefine
from bwdebug import *

# --------------------------------------------------------------------
# implement cell pet epitome class
# --------------------------------------------------------------------
class CellPetEpitome( object ) :
	def __init__( self ) :
		self.databaseID = 0
		self.className = ""
		self.mapMonster = ""
		self.level = 0
		self.takeLevel = 0
		self.ability = 0
		self.stamp = 0
		self.species = csdefine.PET_HIERARCHY_GROWNUP | csdefine.PET_TYPE_STRENGTH
		self.procreated = False
		self.life = 0
		self.gender = csdefine.GENDER_MALE
		self.joyancy = 0
		self.isBinded = False
		
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def hierarchy( self ) :
		return self.species & csdefine.PET_HIERARCHY_MASK

	@property
	def ptype( self ) :
		return self.species & csdefine.PET_TYPE_MASK

	def update( self, attrName, value, owner ):
		"""
		更新某属性值
		"""
		if attrName == "isBinded":
			DEBUG_MSG( "--->>>attrName, value, owner", attrName, value, owner )
		setattr( self, attrName, value )
		owner.pcg_onCellPetChange()

	# ----------------------------------------------------------------
	# methods for packle or unpackle
	# ----------------------------------------------------------------
	def getDictFromObj( self, epitome ) :
		dict = {}
		dict["databaseID"] = epitome.databaseID
		dict["className"] = epitome.className
		dict["mapMonster"] = epitome.mapMonster
		dict["species"] = epitome.species
		dict["level"] = epitome.level
		dict[ "takeLevel" ] = epitome.takeLevel
		dict[ "stamp" ] = epitome.stamp
		dict[ "ability" ] = epitome.ability
		dict[ "procreated" ] = epitome.procreated
		dict[ "life" ] = epitome.life
		dict[ "gender" ] = epitome.gender
		dict[ "joyancy" ] = epitome.joyancy
		dict[ "isBinded" ] = epitome.isBinded
		return dict

	def createObjFromDict( self, dict ) :
		epitome = CellPetEpitome()
		epitome.databaseID = dict["databaseID"]
		epitome.className = dict["className"]
		epitome.mapMonster = dict["mapMonster"]
		epitome.species = dict["species"]
		epitome.level = dict["level"]
		epitome.takeLevel = dict["takeLevel"]
		epitome.stamp = dict["stamp"]
		epitome.ability = dict["ability"]
		epitome.procreated = dict["procreated"]
		epitome.life = dict["life"]
		epitome.gender = dict["gender"]
		epitome.joyancy = dict["joyancy"]
		epitome.isBinded = dict["isBinded"]
		return epitome

	def isSameType( self, obj ) :
		return isinstance( obj, CellPetEpitome )


# --------------------------------------------------------------------
# implement cell pet epitome dict
# --------------------------------------------------------------------
class CellPetDict( object ) :
	def __init__( self ) :
		self.maxCount = 0
		self.petDict = {}


	# ----------------------------------------------------------------
	# methods for packle or unpackle
	# ----------------------------------------------------------------
	def getDictFromObj( self, cellPet ) :
		dict = { "pets" : [] }
		dict["maxCount"] = cellPet.maxCount
		for dbid, pet in cellPet.petDict.items() :
			dict["pets"].append( pet )
		return dict

	def createObjFromDict( self, dict ) :
		cellPets = CellPetDict()
		cellPets.maxCount = dict["maxCount"]
		for pet in dict["pets"] :
			cellPets.petDict[pet.databaseID] = pet
		return cellPets

	def isSameType( self, obj ) :
		return isinstance( obj, CellPetDict )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def count( self ) :
		return len( self.petDict )

	def get( self, dbid ):
		"""
		获取宠物
		"""
		return self.petDict[dbid]

	def has_key( self, dbid ):
		"""
		是否存在dbid的宠物
		"""
		return self.petDict.has_key( dbid )

	def add( self, dbid, petData, owner ):
		"""
		增加一个宠物
		"""
		self.petDict[dbid] = petData
		DEBUG_MSG( "petData", petData )
		owner.pcg_onCellPetChange()

	def remove( self, dbid, owner ):
		"""
		移除一个宠物
		"""
		del self.petDict[dbid]
		owner.pcg_onCellPetChange()

	def update( self, dbid, epitome, owner ):
		"""
		更新宠物数据
		"""
		self.petDict[dbid] = epitome
		owner.pcg_onCellPetChange()

	def getDict( self ):
		"""
		获得宠物数据字典
		"""
		return self.petDict

		
# --------------------------------------------------------------------
# implement instances
# --------------------------------------------------------------------
cellPetInstance = CellPetEpitome()
instance = CellPetDict()
