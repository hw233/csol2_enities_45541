# -*- coding: gb18030 -*-
#
# $Id: Pet.py,v 1.7 2007-12-15 11:27:45 huangyongwei Exp $

"""
This module implements the pet entity.

2007/07/14 : wirten by huangyongwei
2007/10/22 : rewriten by huangyongwei
"""

import random
import BigWorld
import csdefine
import math
import csarithmetic
import csdefine
from ObjectScripts.GameObject import GameObject
from NPCObject import NPCObject
from PetFormulas import formulas
from bwdebug import *
from ObjectScripts.GameObjectFactory import g_objFactory
from Resource.SkillLoader import g_skills
from Resource.SkillTeachLoader import g_skillTeachDatas	

class Pet( NPCObject ) :
	def __init__( self ) :
		NPCObject.__init__( self )


	# ----------------------------------------------------------------
	# overrite method / protected
	# ----------------------------------------------------------------
	def onLoadEntityProperties_( self, sect ) :
		"""
		virtual method. template method, called by GameObject::load() when an entity initializes.
		initialize entity's properties from PyDataSection
		note: all properties here must be defined in ".def" file
		@ptype			section : PyDataSection
		@param			section : python data section load from entity's coonfig file
		@return					: None
		"""
		GameObject.onLoadEntityProperties_( self, sect )
		self.setEntityProperty( "defSkill", sect.readString( "defSkill" ) )
				
		sysHierarchyList = [csdefine.PET_HIERARCHY_GROWNUP,csdefine.PET_HIERARCHY_INFANCY1,csdefine.PET_HIERARCHY_INFANCY2]
		sysCountList = [int( count ) for count in sect.readString( "systemPetSkillCount" ).split( ";" )]
		manuCountList = [int( count ) for count in sect.readString( "manuscriptPetSkillCount" ).split( ";" )]
		sysDict = {}
		for hierarchy, count in zip( sysHierarchyList, sysCountList ):
			sysDict[(csdefine.PET_STAMP_SYSTEM, hierarchy)] = count
		for hierarchy, count in zip( sysHierarchyList, manuCountList ):
			sysDict[(csdefine.PET_STAMP_MANUSCRIPT, hierarchy)] = count
		self.setEntityProperty( "petSkillCountLimit", sysDict )
		
		self.setEntityProperty( "infancySkills", sect["infancySkills"].readInts( "item" ) )

	# ----------------------------------------------------------------
	# overrite method / public
	# ----------------------------------------------------------------
	def getDefSkillIDs( self, level ) :
		"""
		获取默认技能
		"""
		preSkillIDs = self.getEntityProperty( "defSkill" ).split( ";" )				# 技能前缀
		skillIDs = []
		for skID in preSkillIDs:
			skillID = long( skID + "001" )
			if g_skills.has( skillID ) :
				cskill = g_skills[skillID]
				lv = cskill.getMaxLevel() - 1
				if g_skillTeachDatas[ skillID + lv ]['ReqLevel'] <= level:
					skillID = skillID + lv
				else:
					for v in xrange( lv ):
						if level < g_skillTeachDatas[ skillID + v + 1 ]['ReqLevel']:
							skillID = skillID + v
							break
				skillIDs.append( skillID )
			else:
				ERROR_MSG("宠物的默认技能配置有误!!!skill(%d) is not exsit in config!" % skillID )
		return skillIDs

	def getSkillCountLimit( self, hierarchy, stamp ):
		"""
		根据宠物的辈份和印记获得宠物的天赋技能上限
		"""
		return self.getEntityProperty( "petSkillCountLimit" )[(stamp, hierarchy)]
		
	def createEntity( self, spaceID, position, direction, param = None ) :
		"""
		create a pet entity
		@type			spaceID	  : INT32
		@param			spaceID	  : space id
		@type			position  : VECTOR3
		@param			position  : position of the entity
		@type			direction : VECTOR3
		@param			direction : direction of the entity
		@type			param	  : dict
		@param			param	  : extra properties distionary
		@rtype					  : Entity
		@return					  : a new NPC Entity
		"""
		NPCObject.createEntity( self, spaceID, position, direction, param )
