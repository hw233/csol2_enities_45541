# -*- coding: gb18030 -*-
#
# $Id: Pet.py,v 1.19 2008-07-24 06:53:31 huangyongwei Exp $

"""
implement pet base class map script

2007/07/01: writen by huangyongwei
2007/10/24: according to new version documents, it is rewriten by huangyongwei
"""

import random
import csdefine
import csconst
import SkillLoader
import csarithmetic
from bwdebug import *
from ObjectScripts.GameObject import GameObject
from ObjectScripts.NPCObject import NPCObject
from PetFormulas import formulas
from ObjectScripts.GameObjectFactory import g_objFactory
from config.pet import PetInbornSkillNumberRate

class Pet( NPCObject ) :
	def __init__( self ) :
		NPCObject.__init__( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getDefSkill( self, level ) :
		"""
		��ȡĬ�ϼ���
		"""
		preSkillIDs = self.getEntityProperty( "defSkill" ).split( ";" )	# ����ǰ׺
		strLevel = "%03i" % level										# �Եȼ�����Ϊ��λ��
		skillIDs = []
		for skillID in preSkillIDs:
			skillIDs.append( int( skillID + strLevel ) )				# ������ ID ǰ׺��ȼ��ϲ��ó�Ĭ�ϼ���
		return skillIDs

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLoadEntityProperties_( self, sect ) :
		"""
		virtual method. template method, called by GameObject::load() when an entity initializes.
		initialize entity's properties from PyDataSection
		note: all properties here must be defined in ".def" file
		@ptype			sect : PyDataSection
		@param			sect : python data section load from entity's config file
		@return				 : None
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
		
	def getSkillCountLimit( self, hierarchy, stamp ):
		"""
		���ݳ���ı��ݺ�ӡ�ǻ�ó���ļ�������
		"""
		return self.getEntityProperty( "petSkillCountLimit" )[(stamp, hierarchy)]
		
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def createLocalBase( self, param = None ) :
		"""
		create an entity and loacte it in the map
		@ptype				param	   : dict
		@param				param	   : property dictionary
		@rtype						   : Entity
		@return						   : return a new entity
		"""
		return NPCObject.createLocalBase( self, param )

	# -------------------------------------------------
	def catchPet( self, ownerDBID, mclassName, level, modelNumber, callback, defSkillIDs, catchType, isBinded, needResetLevel = False ) :
		monster = g_objFactory.getObject( mclassName )
		if monster is None :
			ERROR_MSG( "monster %s script instance is not exist!" % mclassName )
			callback( None )
			return

		params = {}
		hierarchy = formulas.getCatchedPetHierarchy( catchType )
		params["mapMonster"] = mclassName
		params["modelNumber"] = modelNumber
		params["isBinded"] = isBinded
		if monster.getEntityProperty( "petName" ):	# csol-2044
			params["uname"] = monster.getEntityProperty( "petName" )
		else:
			params["uname"] = monster.getEntityProperty( "uname" )
		profession = monster.getEntityProperty( "raceclass" ) & csdefine.RCMASK_CLASS
		takeLevel = monster.takeLevel
		ptype = profession
		if profession == csdefine.CLASS_PALADIN :
			ptype = csdefine.PET_TYPE_STRENGTH
		species = hierarchy | ptype
		params["species"] = species
		params["gender"] = random.choice( [csdefine.GENDER_MALE, csdefine.GENDER_FEMALE] )		# get gender randomly
		if hierarchy == csdefine.PET_HIERARCHY_INFANCY1 or hierarchy == csdefine.PET_HIERARCHY_INFANCY2 or needResetLevel:			# ����Ǳ���������ǿ�����õȼ�Ϊ1��Ҫ����������ȼ�Ϊ1�������������ȼ�һ�� modify by cwl
			params["level"] = 1
		else:
			params["level"] = level
		params["EXP"] = 0									# set exp

		stamp = formulas.getStamp( catchType )
		params["stamp"] = stamp
		params["ability"]	 = formulas.getAbility( takeLevel, hierarchy, catchType, stamp )
		params["nimbus"] = 0
		params["calcaneus"] = 0
		params["takeLevel"] = takeLevel
		params["character"] = formulas.getCharacter()			# set character randomly
		params["life"] = csconst.PET_LIFE_UPPER_LIMIT			# set default life
		params["joyancy"] = csconst.PET_JOYANCY_UPPER_LIMIT		# set default joyancy

		params["e_corporeity"] = 0
		params["e_strength"] = 0
		params["e_intellect"] = 0
		params["e_dexterity"] = 0

		params["ec_corporeity"] = 0
		params["ec_strength"] = 0
		params["ec_intellect"] = 0
		params["ec_dexterity"] = 0
		params["ec_free"] = 0

		params["procreated"] = False
		attrSkillBox = defSkillIDs

		#������ǰ���ʼ��_qbItems
		qbItems = []
		for idx in xrange( len( defSkillIDs ) ):
			qbItems.append( { "skillID" : defSkillIDs[idx] , "autoUse" : 1 } )
		params["_PetAI__qbItems"] = qbItems		# ��ó������������Ĭ�Ϸ����ڿ�����в��ҿ���

		infancySkills = []
		petInbornSkillNumberRateList = PetInbornSkillNumberRate.Datas.get( (stamp, takeLevel), [] )
		if not petInbornSkillNumberRateList:
			ERROR_MSG( "ȱ�ٳ����츳���ܸ�����ø��ʵ�����: ӡ��Ϊ��%i, Я���ȼ�Ϊ��%i��" % (stamp, takeLevel) )
			inbornSkillNum = 0
		else:
			tempRate = random.random()
			for num, ratePoint in enumerate( petInbornSkillNumberRateList ):	# �˴�list��index��Ӧ���ܸ���
				if tempRate <= ratePoint:
					inbornSkillNum = num
					break
		try:
			infancySkills = random.sample( monster.getInbornSkills(), inbornSkillNum )
		except ValueError:	# ����츳���ܱ���С��inbornSkillNum����ô��ô�������ȫ�츳����
			infancySkills = monster.getInbornSkills()
			ERROR_MSG( "�������( %s )�ɻ�õ��츳���ܸ���( %i )���ڴ��������츳���ܱ�ĳ���( %i )��" % ( monster.getClassName(),inbornSkillNum, len(infancySkills) ) )
			
		attrSkillBox.extend( infancySkills )
		params["attrSkillBox"] = attrSkillBox

		mbPet = self.createLocalBase( params )
		mbPet.ownerDBID = ownerDBID

		def onSavePet( success, pet ) :
			if success :
				pet.initialize()
				epitome = pet.getEpitome()
				pet.destroy( writeToDB = False )
				callback( epitome )
			else :
				callback( None )
		mbPet.writeToDB( onSavePet )

	def procreatePet( self, ownerDBID, father, mother, callback ) :
		progenitor = random.choice( [father, mother] )
		mclassName = progenitor.getAttr( "mapMonster" )

		params = {}
		hierarchy = csdefine.PET_HIERARCHY_INFANCY2
		takeLevel = progenitor.getAttr( "takeLevel" )
		stamp = progenitor.getAttr( "stamp" )
		params["uname"] = progenitor.getAttr( "uname" )
		params["mapMonster"] = mclassName
		params["modelNumber"] = progenitor.getAttr( "modelNumber" )
		params["species"] = hierarchy | progenitor.getAttr( "species" ) & csdefine.PET_TYPE_MASK
		params["gender"] = progenitor.getAttr( "gender" )
		params["takeLevel"] = takeLevel
		params["stamp"] = stamp
		params["level"] = 1
		params["EXP"] = 0

		params["ability"]	 = formulas.getAbility( takeLevel, hierarchy, csdefine.PET_GET_PROPAGATE, stamp )
		params["nimbus"] = 0
		params["calcaneus"] = 0
		params["isBinded"] = progenitor.getAttr( "isBinded" )

		params["character"] = formulas.getCharacter()
		params["life"] = csconst.PET_LIFE_UPPER_LIMIT
		params["joyancy"] = csconst.PET_JOYANCY_UPPER_LIMIT

		params["e_corporeity"] = 0
		params["e_strength"] = 0
		params["e_intellect"] = 0
		params["e_dexterity"] = 0

		params["ec_corporeity"] = 0
		params["ec_strength"] = 0
		params["ec_intellect"] = 0
		params["ec_dexterity"] = 0
		params["ec_free"] = 0

		params["procreated"] = False
		
		FMonsterInbornSkills = g_objFactory.getObject( father.getAttr( "mapMonster" ) ).getInbornSkills() # ���׵������츳����
		MMonsterInbornSkills = g_objFactory.getObject( mother.getAttr( "mapMonster" ) ).getInbornSkills() # ĸ�׵������츳����
		fatherInbornSkills = [skillID / 1000 for skillID in father.getAttr( "attrSkillBox" ) if skillID in FMonsterInbornSkills]
		motherInbornSkills = [skillID / 1000 for skillID in mother.getAttr( "attrSkillBox" ) if skillID in MMonsterInbornSkills]
		attrSkillBox = self.__getDefSkill( params["level"] )
		inbornSkillSet = set( fatherInbornSkills + motherInbornSkills )
		for noLevelSKillID in inbornSkillSet:
			# ����˫�����е��츳���ܱض��Ŵ���������ӵ�е��츳����ֻ��20%�����Ŵ�
			if noLevelSKillID in fatherInbornSkills and noLevelSKillID in motherInbornSkills:
				attrSkillBox.append( noLevelSKillID*1000+1 )
			else:
				if random.random() <= 0.2:
					attrSkillBox.append( noLevelSKillID*1000+1 )
		params["attrSkillBox"] = attrSkillBox
		
		mbPet = self.createLocalBase( params )
		mbPet.ownerDBID = ownerDBID

		def onSavePet( success, pet ) :
			if success :
				pet.initialize()
				epitome = pet.getEpitome()
				pet.destroy( writeToDB = False )
				callback( epitome )
			else :
				callback( None )
		mbPet.writeToDB( onSavePet )