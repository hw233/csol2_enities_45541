# -*- coding: gb18030 -*-
#
# $Id: EntityDecoratorMgr.py,v 1.9 2008-06-19 07:55:42 zhangyuxing Exp $

import event.EventCenter as ECenter
import Language
from gbref import rds
import event.EventCenter as ECenter

class EntityDecoratorMgr:

	__inst			= None

	def __init__( self ) :
		assert EntityDecoratorMgr.__inst is None
		#角色
		self.roleHPBarShowState = 1
		self.roleNameShowState = 1
		self.roleMonickerShowState = 1
		self.roleCorpsNameShowState = 1
		self.roleTitleShowState = 1
		#玩家角色
		self.playerRoleHPBarShowState = 1
		self.playerRoleNameShowState = 1
		self.playerRoleMonickerShowState = 1
		self.playerRoleCorpsNameShowState = 1
		#宠物
		self.petHPBarShowState = 1
		self.petNameShowState = 1

		#NPC
		self.npcNameShowState = 1
		self.npcTitleShowState = 1


		#怪物
		self.monsterHPBarShowState = 1
		self.monsterNameShowState = 1
		self.monsterMsgShow = 0

		#questBox
		self.questBoxNameShowState = 1


		#EntityResume
		self.entityResumeShowState = 1

	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = EntityDecoratorMgr()
		return SELF.__inst

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, config ) :
		"""
		读取配置文件
		"""
		sect = Language.openConfigSection( config )
		if sect is None :
			self.doDefaultSetting()
			return
		#角色
		self.roleHPBarShowState = sect["Role_Decorator"]["blood"].asInt
		self.roleNameShowState = sect["Role_Decorator"]["name"].asInt
		self.roleMonickerShowState = sect["Role_Decorator"]["monicker"].asInt
		self.roleCorpsNameShowState = sect["Role_Decorator"]["corps"].asInt
		self.roleTitleShowState = sect["Role_Decorator"]["title"].asInt

		if not sect["Player_Role_Decorator"]:
			sect.createSection( "Player_Role_Decorator/blood" )
			sect.createSection( "Player_Role_Decorator/name" )
			sect.createSection( "Player_Role_Decorator/monicker" )
			sect.createSection( "Player_Role_Decorator/corps" )
			self.playerRoleHPBarShowState = 1
			self.playerRoleNameShowState = 1
			self.playerRoleMonickerShowState = 1
			self.playerRoleCorpsNameShowState = 1
		else:
		#玩家角色
			self.playerRoleHPBarShowState = sect["Player_Role_Decorator"]["blood"].asInt
			self.playerRoleNameShowState = sect["Player_Role_Decorator"]["name"].asInt
			self.playerRoleMonickerShowState = sect["Player_Role_Decorator"]["monicker"].asInt
			self.playerRoleCorpsNameShowState = sect["Player_Role_Decorator"]["corps"].asInt

		#宠物
		self.petHPBarShowState = sect["Pet_Decorator"]["blood"].asInt
		self.petNameShowState = sect["Pet_Decorator"]["name"].asInt

		#NPC
		self.npcNameShowState = sect["NPC_Decorator"]["name"].asInt
		self.npcTitleShowState = sect["NPC_Decorator"]["title"].asInt


		#怪物
		self.monsterHPBarShowState = sect["Monster_Decorator"]["blood"].asInt
		self.monsterNameShowState = sect["Monster_Decorator"]["name"].asInt
		self.monsterMsgShow = sect["Monster_Decorator"]["msgShow"].asInt

		#questBox
		#self.questBoxNameShowState = sect["QuestBox_Decorator"]["name"].asInt


		#EntityResume
		self.entityResumeShowState = sect["EntityResume"]["resume"].asInt

		Language.purgeConfig( sect )

		ECenter.fireEvent("EVT_ON_SET_DECORATOR_SELECT")


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------

	def doDefaultSetting( self ):
		"""
		"""
		#角色
		self.roleHPBarShowState = 1
		self.roleNameShowState = 1
		self.roleMonickerShowState = 1
		self.roleCorpsNameShowState = 1
		self.roleTitleShowState = 1
		#玩家角色
		self.playerRoleHPBarShowState = 1
		self.playerRoleNameShowState = 1
		self.playerRoleMonickerShowState = 1
		self.playerRoleCorpsNameShowState = 1
		self.playerRoleTitleShowState = 1
		#宠物
		self.petHPBarShowState = 1
		self.petNameShowState = 1

		#NPC
		self.npcNameShowState = 1
		self.npcTitleShowState = 1


		#怪物
		self.monsterHPBarShowState = 1
		self.monsterNameShowState = 1
		self.monsterMsgShow = 0

		#questBox
		self.questBoxNameShowState = 1


		#EntityResume
		self.entityResumeShowState = 1

		ECenter.fireEvent("EVT_ON_SET_DECORATOR_SELECT")

	def createConfig( self, config ):
		"""
		"""
		newSect = Language.openConfigSection( config, True )

		newSect.createSection( "Role_Decorator/blood" )
		newSect.createSection( "Role_Decorator/name" )
		newSect.createSection( "Role_Decorator/monicker" )
		newSect.createSection( "Role_Decorator/corps" )

		newSect.createSection( "Player_Role_Decorator/blood" )
		newSect.createSection( "Player_Role_Decorator/name" )
		newSect.createSection( "Player_Role_Decorator/monicker" )
		newSect.createSection( "Player_Role_Decorator/corps" )

		newSect.createSection( "Pet_Decorator/blood" )
		newSect.createSection( "Pet_Decorator/name" )

		newSect.createSection( "NPC_Decorator/name" )
		newSect.createSection( "NPC_Decorator/title" )

		newSect.createSection( "Monster_Decorator/blood" )
		newSect.createSection( "Monster_Decorator/name" )
		newSect.createSection( "Monster_Decorator/msgShow" )

		newSect.createSection( "EntityResume/resume" )

		return newSect

	def save( self ):
		"""
		"""
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]
		roleName = rds.gameMgr.getCurrRoleHexName()
		config = "account/%s/%s/EntityDecorator.xml" % ( accountName, roleName )
		sect = Language.openConfigSection( config )
		if sect is None:
			sect = self.createConfig( config )
		sect["Role_Decorator"].writeInt( "blood", self.roleHPBarShowState )
		sect["Role_Decorator"].writeInt( "name", self.roleNameShowState )
		sect["Role_Decorator"].writeInt( "monicker", self.roleMonickerShowState )
		sect["Role_Decorator"].writeInt( "corps", self.roleCorpsNameShowState )
		sect["Role_Decorator"].writeInt( "title", self.roleTitleShowState )

		if not sect["Player_Role_Decorator"]:
			sect.createSection( "Player_Role_Decorator/blood" )
			sect.createSection( "Player_Role_Decorator/name" )
			sect.createSection( "Player_Role_Decorator/monicker" )
			sect.createSection( "Player_Role_Decorator/corps" )

		sect["Player_Role_Decorator"].writeInt( "blood", self.playerRoleHPBarShowState )
		sect["Player_Role_Decorator"].writeInt( "name", self.playerRoleNameShowState )
		sect["Player_Role_Decorator"].writeInt( "monicker", self.playerRoleMonickerShowState )
		sect["Player_Role_Decorator"].writeInt( "corps", self.playerRoleCorpsNameShowState )
		sect["Player_Role_Decorator"].writeInt( "title", self.playerRoleTitleShowState )

		sect["Pet_Decorator"].writeInt( "blood", self.petHPBarShowState )
		sect["Pet_Decorator"].writeInt( "name", self.petNameShowState  )

		sect["NPC_Decorator"].writeInt( "name", self.npcNameShowState )
		sect["NPC_Decorator"].writeInt( "title", self.npcTitleShowState )

		sect["Monster_Decorator"].writeInt( "blood", self.monsterHPBarShowState )
		sect["Monster_Decorator"].writeInt( "name", self.monsterNameShowState )
		sect["Monster_Decorator"].writeInt( "msgShow", self.monsterMsgShow )

		sect["EntityResume"].writeInt( "resume", self.entityResumeShowState )

		sect.save()
		Language.purgeConfig( sect )

	#角色设置
	def getRoleHPBarShowState( self ):
		return self.roleHPBarShowState

	def getRoleMonickerShowState( self ):
		return self.roleMonickerShowState

	def getRoleCorpsNameShowState( self ):
		return self.roleCorpsNameShowState

	def setRoleHPBarShowState( self, state ):
		self.roleHPBarShowState = state
		ECenter.fireEvent("EVT_ON_ROLE_HPBAR_SET", state )

	def setRoleMonickerShowState( self, state ):
		self.roleMonickerShowState = state
		ECenter.fireEvent("EVT_ON_ROLE_MONICKER_SET", state )

	def setRoleCorpsNameShowState( self, state ):
		self.roleCorpsNameShowState = state
		ECenter.fireEvent("EVT_ON_ROLE_CORPS_SET", state )

	def getRoleNameShowState( self ):
		return self.roleNameShowState


	def getRoleTitleShowState( self ):
		return self.roleTitleShowState

	#自身角色设置
	def getPlayerRoleHPBarShowState( self ):
		return self.playerRoleHPBarShowState

	def getPlayerRoleMonickerShowState( self ):
		return self.playerRoleMonickerShowState

	def getPlayerRoleCorpsNameShowState( self ):
		return self.playerRoleCorpsNameShowState

	def setPlayerRoleHPBarShowState( self, state ):
		self.playerRoleHPBarShowState = state
		ECenter.fireEvent("EVT_ON_PLAYER_ROLE_HPBAR_SET", state )

	def setPlayerRoleMonickerShowState( self, state ):
		self.playerRoleMonickerShowState = state
		ECenter.fireEvent("EVT_ON_PLAYER_ROLE_MONICKER_SET", state )

	def setPlayerRoleCorpsNameShowState( self, state ):
		self.playerRoleCorpsNameShowState = state
		ECenter.fireEvent("EVT_ON_PLAYER_ROLE_CORPS_SET", state )

	def getPlayerRoleNameShowState( self ):
		return self.playerRoleNameShowState

	def setPlayerRoleNameShowState( self, state ):
		self.playerRoleNameShowState = state
		ECenter.fireEvent("EVT_ON_PLAYER_ROLE_NAME_SET", state )

	def getPlayerRoleTitleShowState( self ):
		return self.playerRoleTitleShowState

	def setPlayerRoleTitleShowState( self, state ):
		self.playerRoleTitleShowState = state
		ECenter.fireEvent("EVT_ON_PLAYER_ROLE_TITLE_SET", state )

	#宠物设置

	def getPetNameShowState( self ):
		return self.petNameShowState

	def setPetNameShowState( self, state ):
		self.petNameShowState = state
		ECenter.fireEvent("EVT_ON_PET_NAME_SET", state )

	def getPetHPBarShowState( self ):
		return self.petHPBarShowState

	def setPetHPBarShowState( self, state ):
		self.petHPBarShowState = state
		ECenter.fireEvent("EVT_ON_PET_HPBAR_SET", state )

	#NPC
	def getNpcNameShowState( self ):
		return self.npcNameShowState

	def setNpcTitleShowState( self, state ):
		self.npcTitleShowState = state
		ECenter.fireEvent("EVT_ON_NPC_TITLE_SET", state )

	def getNpcTitleShowState( self ):
		return self.npcTitleShowState

	def setNpcNameShowState( self, state ):
		self.npcNameShowState = state
		ECenter.fireEvent("EVT_ON_NPC_NAME_SET", state )

	#怪物
	def getMonsterNameShowState( self ):
		return self.monsterNameShowState

	def setMonsterNameShowState( self, state ):
		self.monsterNameShowState = state
		ECenter.fireEvent("EVT_ON_MONSTER_NAME_SET", state )

	def getMonsterHPBarShowState( self ):
		return self.monsterHPBarShowState

	def setMonsterHPBarShowState( self, state ):
		self.monsterHPBarShowState = state
		ECenter.fireEvent("EVT_ON_MONSTER_HPBAR_SET", state )

	def getMonsterMsgShow( self ):
		return self.monsterMsgShow

	def setMonsterMsgShow( self, state ):
		self.monsterMsgShow = state
		ECenter.fireEvent("EVT_ON_MONSTER_MSG_SHOW", state )

	#questBox
	def getQuestBoxNameShowState( self ):
		return self.questBoxNameShowState

	def setQuestBoxNameShowState( self, state ):
		self.questBoxNameShowState = state
		ECenter.fireEvent("EVT_ON_QUESTBOX_NAME_SET", state )


	#entityResume
	def getEntityResumeShowState( self ):
		return self.entityResumeShowState

	def setEntityResumeShowState( self, state ):
		self.entityResumeShowState = state
		ECenter.fireEvent("EVT_ON_ENTITY_RESUME_SET", state )

	def onRoleEnterWorld( self ):
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]
		roleName = rds.gameMgr.getCurrRoleHexName()
		config = "account/%s/%s/EntityDecorator.xml" % ( accountName, roleName )
		self.__initialize( config )
