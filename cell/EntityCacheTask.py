# -*- coding: gb18030 -*-
#
# $Id: Monster.py,v 1.99 2009-07-14 02:38:42 kebiao Exp $
"""
"""

import BigWorld
import csdefine
from bwdebug import *
import EntityCache

g_entityCache = EntityCache.EntityCache.instance()
REGISTER_ENTITY_CACHE_TASK = g_entityCache.registerTask

class ECTask:
	"""
	���������
	"""
	def __init__( self ):
		self._type = 0

	def getType( self ):
		return self._type

	def setType( self, type ):
		self._type = type

	def do( self, refEntity, targetEntity ):
		"""
		virtual method.
		ִ����Ӧ������
		@param refEntity 	: �ο�entity�� ͨ����player
		@param targetEntity : ���ο�entity
		"""
		return True

class ECTaskNPCObject0( ECTask ):
	"""
	һ����ȡģ����ص�����
	"""
	def __init__( self ):
		ECTask.__init__( self )
		self._type = csdefine.ENTITY_CACHE_TASK_TYPE_NPCOBJECT0

	def do( self, refEntity, targetEntity, isLastTask ):
		"""
		virtual method.
		ִ����Ӧ������
		@param refEntity 	: �ο�entity�� ͨ����player
		@param targetEntity : ���ο�entity
		"""
		client = refEntity.clientEntity( targetEntity.id )
		# client.onSetModelNumber( targetEntity.modelNumber )
		# client.onSetModelScale( targetEntity.modelScale )
		client.onSetName( targetEntity.getName() )

		if targetEntity.attrDistance > 0.0:
			client.onSetAttrDistance( targetEntity.attrDistance )

		title = targetEntity.getTitle()
		if len( title ) > 0:
			client.onSetTitle( title )

		if len( targetEntity.own_familyName ) > 0:
			client.onSetOwnFamilyName( targetEntity.own_familyName )
		if isLastTask:
			client.onCacheCompleted()
		return True

class ECTaskNPCObject1( ECTask ):
	"""
	һ����ȡ������ģ�ͱ����ص�����
	"""
	def __init__( self ):
		ECTask.__init__( self )
		self._type = csdefine.ENTITY_CACHE_TASK_TYPE_NPCOBJECT1

	def do( self, refEntity, targetEntity, isLastTask ):
		"""
		virtual method.
		ִ����Ӧ������
		@param refEntity 	: �ο�entity�� ͨ����player
		@param targetEntity : ���ο�entity
		"""
		client = refEntity.clientEntity( targetEntity.id )
		client.setName( targetEntity.uname )
		client.setTitle( targetEntity.title )
		client.setRaceclass( targetEntity.raceclass )
		client.setHairNumber( targetEntity.hairNumber )
		client.setFaceNumber( targetEntity.faceNumber )
		client.setBodyFDict( targetEntity.bodyFDict )
		client.setVolaFDict( targetEntity.volaFDict )
		client.setBreechFDict( targetEntity.breechFDict )
		client.setFeetFDict( targetEntity.feetFDict )
		client.setLefthandFDict( targetEntity.lefthandFDict )
		client.setRighthandFDict( targetEntity.righthandFDict )
		client.setTalismanNum( targetEntity.talismanNum )
		client.setFashionNum( targetEntity.fashionNum )
		client.setAdornNum( targetEntity.adornNum )
		#client.setAction( targetEntity.playAction )
		client.setModelScale( targetEntity.modelScale )
		client.setTongName( targetEntity.tongName )
		if isLastTask:
			client.onCacheCompleted()
		return True

class ECTaskMonster0( ECTask ):
	"""
	һ����ȡ������ģ�ͱ����ص�����
	"""
	def __init__( self ):
		ECTask.__init__( self )
		self._type = csdefine.ENTITY_CACHE_TASK_TYPE_MONSTER0

	def do( self, refEntity, targetEntity, isLastTask ):
		"""
		virtual method.
		ִ����Ӧ������
		@param refEntity 	: �ο�entity�� ͨ����player
		@param targetEntity : ���ο�entity
		"""
		client = refEntity.clientEntity( targetEntity.id )

		if targetEntity.lefthandNumber > 0:
			client.onSetLeftHandNumber( targetEntity.lefthandNumber )

		if targetEntity.righthandNumber > 0:
			client.onSetRightHandNumber( targetEntity.righthandNumber )
		if isLastTask:
			client.onCacheCompleted()
		return True

class ECTaskCombatUnit0( ECTask ):
	"""
	��ȡ����ʩ������ļ�ֵ
	"""
	def __init__( self ):
		ECTask.__init__( self )
		self._type = csdefine.ENTITY_CACHE_TASK_TYPE_COMBATUNIT0

	def do( self, refEntity, targetEntity, isLastTask ):
		"""
		virtual method.
		ִ����Ӧ������
		@param refEntity 	: �ο�entity�� ͨ����player
		@param targetEntity : ���ο�entity
		"""
		#refEntity.chat_say( "����uname!!" )
		client = refEntity.clientEntity( targetEntity.id )
		if isLastTask:
			client.onCacheCompleted()
		return True

class ECTaskPet0( ECTask ):
	"""
	��ȡpetģ����ص�����
	"""
	def __init__( self ):
		ECTask.__init__( self )
		self._type = csdefine.ENTITY_CACHE_TASK_TYPE_PET0

	def do( self, refEntity, targetEntity, isLastTask ):
		"""
		virtual method.
		ִ����Ӧ������
		@param refEntity 	: �ο�entity�� ͨ����player
		@param targetEntity : ���ο�entity
		"""
		client = refEntity.clientEntity( targetEntity.id )

		client.onSetCorporeity( targetEntity.corporeity )
		client.onSetStrength( targetEntity.strength )
		client.onSetIntellect( targetEntity.intellect )
		client.onSetDexterity( targetEntity.dexterity )

		client.onSetEC_corporeity( targetEntity.ec_corporeity )
		client.onSetEC_strength( targetEntity.ec_strength )
		client.onSetEC_dexterity( targetEntity.ec_dexterity )
		client.onSetEC_intellect( targetEntity.ec_intellect )

		client.onSetE_corporeity( targetEntity.e_corporeity )
		client.onSetE_strength( targetEntity.e_strength )
		client.onSetE_dexterity( targetEntity.e_dexterity )
		client.onSetE_intellect( targetEntity.e_intellect )

		client.onSetEC_free( targetEntity.ec_free )

		client.onSetAbility( targetEntity.ability )
		client.onSetNimbus( targetEntity.nimbus )
		client.onSetCalcaneus( targetEntity.calcaneus )
		client.onSetCharacter( targetEntity.character )
		client.onSetProcreated( targetEntity.procreated )
		client.onSetLife( targetEntity.life )
		client.onSetJoyancy( targetEntity.joyancy )

		client.onSetPhyManaVal_value( targetEntity.phyManaVal_value )
		client.onSetPhyManaVal_percent( targetEntity.phyManaVal_percent )
		client.onSetMagicManaVal_value( targetEntity.magicManaVal_value )
		client.onSetMagicManaVal_percent( targetEntity.magicManaVal_percent )

		client.onSetPhySkillRangeVal_value( targetEntity.phySkillRangeVal_value )
		client.onSetPhySkillRangeVal_percent( targetEntity.phySkillRangeVal_percent )
		client.onSetMagicSkillRangeVal_value( targetEntity.magicSkillRangeVal_value )
		client.onSetMagicSkillRangeVal_percent( targetEntity.magicSkillRangeVal_percent )

		client.onSetDamageMin( targetEntity.damage_min )
		client.onSetDamageMax( targetEntity.damage_max )
		client.onSetMagicDamage( targetEntity.magic_damage )
		client.onSetArmor( targetEntity.armor )
		client.onSetMagicArmor( targetEntity.magic_armor )
		client.onSetDodgeProbability( targetEntity.dodge_probability )
		client.onSetResistHitProbability( targetEntity.resist_hit_probability )
		client.onSetDoubleHitProbability( targetEntity.double_hit_probability )
		client.onSetMagicDoubleHitProbability( targetEntity.magic_double_hit_probability )
		client.onSetResistGiddyProbability( targetEntity.resist_giddy_probability )
		client.onSetResistFixProbability( targetEntity.resist_fix_probability )
		client.onSetResistChenmoProbability( targetEntity.resist_chenmo_probability )
		client.onSetResistSleepProbability( targetEntity.resist_sleep_probability )

		client.onSetRange( targetEntity.range )
		client.onSetHit_speed( targetEntity.hit_speed )

		if isLastTask:
			client.onCacheCompleted()
		return True

# ע������
REGISTER_ENTITY_CACHE_TASK( ECTaskMonster0() )
REGISTER_ENTITY_CACHE_TASK( ECTaskNPCObject0() )
REGISTER_ENTITY_CACHE_TASK( ECTaskNPCObject1() )
REGISTER_ENTITY_CACHE_TASK( ECTaskCombatUnit0() )
REGISTER_ENTITY_CACHE_TASK( ECTaskPet0() )

# EntityCache.py
