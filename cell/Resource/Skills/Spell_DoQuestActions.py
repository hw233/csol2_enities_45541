# -*- coding: gb18030 -*-

import random
import copy

from SpellBase import *
import csdefine
import csstatus
from ObjectScripts.GameObjectFactory import g_objFactory

class Spell_DoQuestActions( Spell ):
	"""
	用于完成指定任务，并执行相关动作
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		self.questID = 0
		self.questTaskIndex = 0
		self.spawnList = []
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.questID, self.questTaskIndex   = [ int( i ) for i in dict["param2"].split( ";" ) ]
		spawnInfos = dict["param3"].split( ";" )
		spawnIDs = []
		spawnTimes = []
		for inf in spawnInfos:
			spawnID, lifetime = inf.split( "|" )
			spawnIDs.append( spawnID )
			spawnTimes.append( int( lifetime ) )
			
		spawnPos = dict["param4"].split( ";" )
		spawnDir = dict["param5"].split( ";" )
		for i, c in enumerate( spawnIDs ):
			pos = eval( spawnPos[ i ] )
			dir = eval( spawnDir[ i ] )
			lifetime = spawnTimes[ i ]
			self.spawnList.append( ( c, pos, dir, lifetime ) )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		# NPC创建
		dict = {}
		dict[ "spawnPos" ] = caster.position
		dict[ "ownerVisibleInfos" ] = ( receiver.id, 0 )
		dict[ "bootyOwner" ] = ( receiver.id, 0 )
		for sp in self.spawnList:
			pos = sp[ 1 ]
			direction = sp[ 2 ]
			if pos == 0:
				pos = caster.position + ( random.randint( -2, 2 ), 0, random.randint( -2, 2 ) )
				
			if direction == 0:
				direction = (0, 0, 1)
			
			dict[ "lifetime" ] = sp[ 3 ]
			
			entity = g_objFactory.createEntity( sp[0], caster.spaceID, pos, direction, copy.deepcopy( dict ) )
			entity.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_ID, receiver.id )
			#caster.createNPCObject( sp[0], pos, direction, copy.deepcopy( dict ) )
		
		# 完成任务
		receiver.questTaskIncreaseState( self.questID, self.questTaskIndex )
	
	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if target.getType() == csdefine.SKILL_TARGET_OBJECT_ENTITY:
			if target.getObject().isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				player = target.getObject()
				if not player.has_quest( self.questID ):
					return csstatus.SKILL_CANT_CAST
					
				if player.taskIsCompleted( self.questID, self.questTaskIndex ):
					return csstatus.SKILL_CANT_CAST
			else:
				return csstatus.SKILL_CANT_CAST
		else:
			return csstatus.SKILL_CANT_CAST
				
		return Spell.useableCheck( self, caster, target )