# -*- coding: gb18030 -*-
#
# $Id: NameFactory.py,v 1.10 2008-05-28 03:04:16 huangyongwei Exp $

"""
implement float name of the character
2009.02.13：tidy up by huangyongwei
"""

import csdefine
import Const
import event.EventCenter as ECenter
from guis import *
from RoleName import RoleName
from PetName import PetName
from NPCName import NPCName
from PixieName import PixieName
from TbTreeName import TbTreeName
from MonsterName import MonsterName
from QuestBoxName import QuestBoxName
from DropItemName import DropItemName
from MstAttackBoxName import MstAttackBoxName
from CityMasterName import CityMasterName
from FHLTFlagName import FHLTFlagName
from DanceKingName import DanceKingName

SHOW_NAME = True

class NameFactory( object ) :
	__cc_fnames = {}
	__cc_fnames[csdefine.ENTITY_TYPE_ROLE]			= RoleName
	__cc_fnames[csdefine.ENTITY_TYPE_PET]			= PetName
	__cc_fnames[csdefine.ENTITY_TYPE_NPC]			= NPCName
	__cc_fnames[csdefine.ENTITY_TYPE_EIDOLON_NPC]	= PixieName
	__cc_fnames[csdefine.ENTITY_TYPE_MONSTER]		= MonsterName
	__cc_fnames[csdefine.ENTITY_TYPE_QUEST_BOX]		= QuestBoxName
	__cc_fnames[csdefine.ENTITY_TYPE_DROPPED_ITEM]	= DropItemName
	__cc_fnames[csdefine.ENTITY_TYPE_YAYU]			= MonsterName
	__cc_fnames[csdefine.ENTITY_TYPE_TONG_CITYWAR_MONSTER]	= MonsterName
	__cc_fnames[csdefine.ENTITY_TYPE_MONSTER_ATTACK_BOX]	= MstAttackBoxName
	__cc_fnames[csdefine.ENTITY_TYPE_FRUITTREE]				= TbTreeName
	__cc_fnames[csdefine.ENTITY_TYPE_CITY_MASTER]	= CityMasterName
	__cc_fnames[csdefine.ENTITY_TYPE_CALL_MONSTER]		= MonsterName
	__cc_fnames[csdefine.ENTITY_TYPE_CONVOY_MONSTER]	= NPCName
	__cc_fnames[csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM]	= MonsterName
	__cc_fnames[csdefine.ENTITY_TYPE_TONG_NAGUAL]	= MonsterName
	__cc_fnames[csdefine.ENTITY_TYPE_XIAN_FENG]	= MonsterName
	__cc_fnames[csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_TOWER]	= MonsterName
	__cc_fnames[csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_ALTAR]	= MonsterName
	__cc_fnames[csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_BASE_TOWER]	= MonsterName
	__cc_fnames[csdefine.ENTITY_TYPE_FENG_HUO_LIAN_TIAN_BATTLE_FLAG]	= FHLTFlagName
	__cc_fnames[csdefine.ENTITY_TYPE_VEHICLE_DART]	= MonsterName
	__cc_fnames[csdefine.ENTITY_TYPE_DANCE_KING]	= DanceKingName

	def __init__( self ) :
		self.__entityTrapID = 0
		self.__floatNames = {}
		self.__triggers = {}
		self.__registerTriggers()
		
		#预先创建头顶实例,暂且创建这三类
		createInsts( RoleName, 100 )
		createInsts( MonsterName,100 )
		createInsts( NPCName, 50 )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ENTITY_ENTER_WORLD"] = self.__onEntityAttached
		self.__triggers["EVT_ON_ENTITY_LEAVE_WORLD"] = self.__onEntityDetach
		self.__triggers["EVT_ON_ENTITY_NPC_NAME_FLAG"] = self.__onEntityNpcNameFlag
		self.__triggers["EVT_ON_ENTITY_RESET_NAME_FLAG"] = self.__onEntityResetNameFlag

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
		self.__triggers = {}

	# -------------------------------------------------
	def __onEntitiesTrapThrough( self, entities ) :
		"""
		判断周围所有的 NPC 是否在指定范围内，如果在则显示其头顶名字，否则不显示
		"""
		for entity in BigWorld.entities.values() :
			if entity == BigWorld.player(): continue
			pyFloatName = self.__floatNames.get( entity.id, None )
			if pyFloatName is None : continue
			pyFloatName[1].visible = entity in entities

	# -------------------------------------------------
	def __onEntityAttached( self, entity ) :
		"""
		当一个 entity 进入世界时被调用
		"""
		if not SHOW_NAME:return
		player = BigWorld.player()
		if entity == player :
			self.__entityTrapID = player.addTrapExt( \
				Const.SHOW_NPCNAME_RANGE, \
				self.__onEntitiesTrapThrough )						# 角色进入世界时，添加一个陷阱，用以检测 NPC 是否在指定范围内

		entityType = entity.getEntityType()
		if not self.__cc_fnames.has_key( entityType ) : 			# 这种类型不需要显示头顶标记
			return
		
		if self.__floatNames.has_key( entity.id ):					# 已经存在
			if self.__floatNames[entity.id][0] == entityType : 
				return
			else:						
				pyInfos = self.__floatNames.pop( entity.id )
				entityType = pyInfos[0]
				pyName = pyInfos[1]
				entity.detach( pyName )
				pyName.detachEntity()		#头顶实例解除绑定的entity
				cls = self.__cc_fnames[entityType]	
				isSucceed = recycleInst( cls, pyName )	#回收实例
				if not isSucceed:	#没有成功回收的实例直接销毁，暂时只回收（RoleName, NPCName, MonsterName ）
					pyName.dispose()
				
		if entity.hasFlag( csdefine.ENTITY_FLAG_NPC_NAME ):
			entityType = csdefine.ENTITY_TYPE_NPC
		
		cls = self.__cc_fnames[entityType]	
		pyFName = getInst( cls )
		if pyFName is None:	
			pyFName = self.__cc_fnames[entityType]( )
			
		pyFName.attachEntity( entity )	#头顶实例绑定entity
		entity.attach( pyFName )
		
		self.__floatNames[entity.id] = ( entityType, pyFName )

	def __onEntityDetach( self, entity ) :
		"""
		当一个 entity 离开世界时被调用
		"""
		if not SHOW_NAME:return
		player = BigWorld.player()
		if entity == player :
			if self.__entityTrapID != 0 :							# 清除陷阱
				player.delTrap( self.__entityTrapID )
				self.__entityTrapID = 0
		if self.__floatNames.has_key( entity.id ) :
			pyInfos = self.__floatNames.pop( entity.id )
			entityType = pyInfos[0]		
			pyName = pyInfos[1]
			entity.detach( pyName )
			pyName.detachEntity()				#解除绑定entity
			cls = self.__cc_fnames[entityType]	
			isSucceed = recycleInst( cls, pyName)	#回收实例
			if not isSucceed:	#没有成功回收的实例直接销毁，暂时只回收（RoleName, NPCName, MonsterName ）
				pyName.dispose()
			

	def __onEntityNpcNameFlag( self, entity ):
		"""
		NPC名称显示标志
		"""
		if not SHOW_NAME:return
		entityType = entity.getEntityType()
		if not self.__cc_fnames.has_key( entityType ): 	   # 这种类型不需要显示头顶标记
			return
		if entityType == csdefine.ENTITY_TYPE_NPC: return  # 已经是NPCName了
		if entityType == csdefine.ENTITY_TYPE_DANCE_KING:
			return
			pyFName = self.__cc_fnames[entityType]( entity )
			entity.attach(pyFName)
			pyFName.dispose()
			if pyName.attachNode:   # 清除node上面旧的附加UI
				pyName.attachNode.detach( pyName.guiAttachment )			
		# 先移除旧的
		if self.__floatNames.has_key( entity.id ):
			pyInfos = self.__floatNames.pop( entity.id )
			entityType = pyInfos[0]		
			pyName = pyInfos[1]
			entity.detach( pyName )
			pyName.detachEntity()				#解除绑定entity
			cls = self.__cc_fnames[entityType]	
			isSucceed = recycleInst( cls, pyName)	#回收实例
			if not isSucceed:	#没有成功回收的实例直接销毁，暂时只回收（RoleName, NPCName, MonsterName ）
				pyName.dispose()
		# 添加新的，强制显示为NPC头顶的格式
		
		entityType = csdefine.ENTITY_TYPE_NPC
		cls = self.__cc_fnames[entityType]	
		pyFName = getInst( cls )
		if pyFName is None:	
			pyFName = self.__cc_fnames[entityType]()
		
		pyFName.attachEntity( entity )	#头顶实例绑定entity
		entity.attach( pyFName )
		
		self.__floatNames[entity.id] = ( entityType, pyFName )
		pyFName.onEnterWorld()
		

	def __onEntityResetNameFlag( self, entity ):
		"""
		重新设置头顶显示
		"""
		if not SHOW_NAME:return
		entityType = entity.getEntityType()

		if self.__floatNames.has_key( entity.id ):				# 已经存在
			if self.__floatNames[entity.id][0] == entityType: 
				return
			pyInfos = self.__floatNames.pop( entity.id )
			oldEntityType = pyInfos[0]
			pyName = pyInfos[1]
			entity.detach( pyName )
			pyName.detachEntity()		#头顶实例解除绑定的entity
			cls = self.__cc_fnames[oldEntityType]	
			isSucceed = recycleInst( cls, pyName )	#回收实例
			if not isSucceed:	#没有成功回收的实例直接销毁，暂时只回收（RoleName, NPCName, MonsterName ）
				pyName.dispose()

		if not self.__cc_fnames.has_key( entityType ): 	   	    # 这种类型不需要显示头顶标记
			return
			
		if entity.hasFlag( csdefine.ENTITY_FLAG_NPC_NAME ):
			entityType = csdefine.ENTITY_TYPE_NPC

		cls = self.__cc_fnames[entityType]
		pyFName = getInst( cls )
		if pyFName is None:	
			pyFName = self.__cc_fnames[entityType]( )
	
		pyFName.attachEntity( entity )	#头顶实例绑定entity
		entity.attach( pyFName )
		self.__floatNames[entity.id] = ( entityType, pyFName )
		pyFName.onEnterWorld()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
		
		
#-------------------------------------------------------------------------
#预先创建实例
#-------------------------------------------------------------------------
FloatNames_Poll = {}
def createInsts( CLS, amount ):
	global FloatNames_Poll
	insts = FloatNames_Poll.get( CLS )
	if insts is None:
		insts = []
		FloatNames_Poll[CLS] = insts
	for i in xrange( amount ):
		inst = CLS()
		insts.append( inst )
		
def getInst( CLS ):		
	insts = FloatNames_Poll.get( CLS )
	if insts is	None :
		return None
	if len( insts ) == 0:	#已经用完了，都没有归还的情况下	
		inst = CLS()
		return inst
	return insts.pop()
	
def recycleInst( CLS, inst ):
	global FloatNames_Poll
	insts = FloatNames_Poll.get( CLS )
	if insts is not None:
		insts.append( inst )
		return True
	return False
