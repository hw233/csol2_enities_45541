# -*- coding: gb18030 -*-
#
# $Id: NameFactory.py,v 1.10 2008-05-28 03:04:16 huangyongwei Exp $

"""
implement float name of the character
2009.02.13��tidy up by huangyongwei
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
		
		#Ԥ�ȴ���ͷ��ʵ��,���Ҵ���������
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
		�ж���Χ���е� NPC �Ƿ���ָ����Χ�ڣ����������ʾ��ͷ�����֣�������ʾ
		"""
		for entity in BigWorld.entities.values() :
			if entity == BigWorld.player(): continue
			pyFloatName = self.__floatNames.get( entity.id, None )
			if pyFloatName is None : continue
			pyFloatName[1].visible = entity in entities

	# -------------------------------------------------
	def __onEntityAttached( self, entity ) :
		"""
		��һ�� entity ��������ʱ������
		"""
		if not SHOW_NAME:return
		player = BigWorld.player()
		if entity == player :
			self.__entityTrapID = player.addTrapExt( \
				Const.SHOW_NPCNAME_RANGE, \
				self.__onEntitiesTrapThrough )						# ��ɫ��������ʱ�����һ�����壬���Լ�� NPC �Ƿ���ָ����Χ��

		entityType = entity.getEntityType()
		if not self.__cc_fnames.has_key( entityType ) : 			# �������Ͳ���Ҫ��ʾͷ�����
			return
		
		if self.__floatNames.has_key( entity.id ):					# �Ѿ�����
			if self.__floatNames[entity.id][0] == entityType : 
				return
			else:						
				pyInfos = self.__floatNames.pop( entity.id )
				entityType = pyInfos[0]
				pyName = pyInfos[1]
				entity.detach( pyName )
				pyName.detachEntity()		#ͷ��ʵ������󶨵�entity
				cls = self.__cc_fnames[entityType]	
				isSucceed = recycleInst( cls, pyName )	#����ʵ��
				if not isSucceed:	#û�гɹ����յ�ʵ��ֱ�����٣���ʱֻ���գ�RoleName, NPCName, MonsterName ��
					pyName.dispose()
				
		if entity.hasFlag( csdefine.ENTITY_FLAG_NPC_NAME ):
			entityType = csdefine.ENTITY_TYPE_NPC
		
		cls = self.__cc_fnames[entityType]	
		pyFName = getInst( cls )
		if pyFName is None:	
			pyFName = self.__cc_fnames[entityType]( )
			
		pyFName.attachEntity( entity )	#ͷ��ʵ����entity
		entity.attach( pyFName )
		
		self.__floatNames[entity.id] = ( entityType, pyFName )

	def __onEntityDetach( self, entity ) :
		"""
		��һ�� entity �뿪����ʱ������
		"""
		if not SHOW_NAME:return
		player = BigWorld.player()
		if entity == player :
			if self.__entityTrapID != 0 :							# �������
				player.delTrap( self.__entityTrapID )
				self.__entityTrapID = 0
		if self.__floatNames.has_key( entity.id ) :
			pyInfos = self.__floatNames.pop( entity.id )
			entityType = pyInfos[0]		
			pyName = pyInfos[1]
			entity.detach( pyName )
			pyName.detachEntity()				#�����entity
			cls = self.__cc_fnames[entityType]	
			isSucceed = recycleInst( cls, pyName)	#����ʵ��
			if not isSucceed:	#û�гɹ����յ�ʵ��ֱ�����٣���ʱֻ���գ�RoleName, NPCName, MonsterName ��
				pyName.dispose()
			

	def __onEntityNpcNameFlag( self, entity ):
		"""
		NPC������ʾ��־
		"""
		if not SHOW_NAME:return
		entityType = entity.getEntityType()
		if not self.__cc_fnames.has_key( entityType ): 	   # �������Ͳ���Ҫ��ʾͷ�����
			return
		if entityType == csdefine.ENTITY_TYPE_NPC: return  # �Ѿ���NPCName��
		if entityType == csdefine.ENTITY_TYPE_DANCE_KING:
			return
			pyFName = self.__cc_fnames[entityType]( entity )
			entity.attach(pyFName)
			pyFName.dispose()
			if pyName.attachNode:   # ���node����ɵĸ���UI
				pyName.attachNode.detach( pyName.guiAttachment )			
		# ���Ƴ��ɵ�
		if self.__floatNames.has_key( entity.id ):
			pyInfos = self.__floatNames.pop( entity.id )
			entityType = pyInfos[0]		
			pyName = pyInfos[1]
			entity.detach( pyName )
			pyName.detachEntity()				#�����entity
			cls = self.__cc_fnames[entityType]	
			isSucceed = recycleInst( cls, pyName)	#����ʵ��
			if not isSucceed:	#û�гɹ����յ�ʵ��ֱ�����٣���ʱֻ���գ�RoleName, NPCName, MonsterName ��
				pyName.dispose()
		# ����µģ�ǿ����ʾΪNPCͷ���ĸ�ʽ
		
		entityType = csdefine.ENTITY_TYPE_NPC
		cls = self.__cc_fnames[entityType]	
		pyFName = getInst( cls )
		if pyFName is None:	
			pyFName = self.__cc_fnames[entityType]()
		
		pyFName.attachEntity( entity )	#ͷ��ʵ����entity
		entity.attach( pyFName )
		
		self.__floatNames[entity.id] = ( entityType, pyFName )
		pyFName.onEnterWorld()
		

	def __onEntityResetNameFlag( self, entity ):
		"""
		��������ͷ����ʾ
		"""
		if not SHOW_NAME:return
		entityType = entity.getEntityType()

		if self.__floatNames.has_key( entity.id ):				# �Ѿ�����
			if self.__floatNames[entity.id][0] == entityType: 
				return
			pyInfos = self.__floatNames.pop( entity.id )
			oldEntityType = pyInfos[0]
			pyName = pyInfos[1]
			entity.detach( pyName )
			pyName.detachEntity()		#ͷ��ʵ������󶨵�entity
			cls = self.__cc_fnames[oldEntityType]	
			isSucceed = recycleInst( cls, pyName )	#����ʵ��
			if not isSucceed:	#û�гɹ����յ�ʵ��ֱ�����٣���ʱֻ���գ�RoleName, NPCName, MonsterName ��
				pyName.dispose()

		if not self.__cc_fnames.has_key( entityType ): 	   	    # �������Ͳ���Ҫ��ʾͷ�����
			return
			
		if entity.hasFlag( csdefine.ENTITY_FLAG_NPC_NAME ):
			entityType = csdefine.ENTITY_TYPE_NPC

		cls = self.__cc_fnames[entityType]
		pyFName = getInst( cls )
		if pyFName is None:	
			pyFName = self.__cc_fnames[entityType]( )
	
		pyFName.attachEntity( entity )	#ͷ��ʵ����entity
		entity.attach( pyFName )
		self.__floatNames[entity.id] = ( entityType, pyFName )
		pyFName.onEnterWorld()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
		
		
#-------------------------------------------------------------------------
#Ԥ�ȴ���ʵ��
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
	if len( insts ) == 0:	#�Ѿ������ˣ���û�й黹�������	
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
