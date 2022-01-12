# -*- coding: gb18030 -*-

"""
飞星传送过程中使用技能客户端脚本
"""

import BigWorld
import csdefine
import Define
from gbref import rds
from SpellBase import *
import csconst
import random
#飞翔传送动作匹配
ACTION_MAP_NO_WEAPON = {1:"ride_stand", 2:"crossleg_stand", 3:"float_stand"}
ACTION_MAP_WEAPON = {1:{1:"ride_run_weapon", 2:"ride_run_weapon_chang", 3:"ride_run_weapon_chang_fu",4:"ride_run_weapon_dan",5:"ride_run_weapon_shuang",6:"ride_run_weapon"},
	2:{1:"crossleg_run_weapon", 2:"crossleg_run_weapon_chang", 3:"crossleg_run_weapon_chang_fu",4:"crossleg_run_weapon_dan",5:"crossleg_run_weapon_shuang",6:"crossleg_run_weapon"},
		3:{1:"float_run_weapon", 2:"float_run_weapon_chang", 3:"float_run_weapon_chang_fu",4:"float_run_weapon_dan",5:"float_run_weapon_shuang",6:"float_run_weapon"}
		}

class Spell_PlayerFly( Spell ):
	
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		
	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		caster.hasCast = True
		skillID = self.getID()

		# 对动作而言，我只会播放一次
		self.playCastAction( caster, skillID )
		if hasattr( caster,"isLoadModel" ) and caster.isLoadModel:
			caster.delayCastEffects.append( Functor( rds.skillEffect.playCastEffects, caster, targetObject, skillID ) )
		else:
			rds.skillEffect.playCastEffects( caster, targetObject, skillID )

		# 技能名称显示
		speller = caster  #重新赋值，防止后面调用混乱
		if hasattr( speller, 'getOwner' ):
			speller = speller.getOwner()

		player = BigWorld.player()
		if player is None: return
		if speller is None: return

		if player.position.distTo( speller.position ) > 20: return
		if hasattr( caster, "className" ):
			sk_id = str( skillID )[:-3]
			if not sk_id: return		# 如果为空，直接返回
			orgSkillID = int( sk_id )	# 支持配置表可变等级NPC技能填写
			skillIDs = npcSkillName.get( caster.className, [] )
			if orgSkillID in skillIDs or skillID in skillIDs:
				caster.showSkillName( skillID )
				return
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or caster.isEntityType( csdefine.ENTITY_TYPE_PET ):
			caster.showSkillName( skillID )	
		
	def playCastAction( self, speller, skillID ):
		"""
		@type	speller 	: entity
		@param	speller 	: 动作施放者
		@type	skillID 	: skillID
		@param	skillID 	: 技能ID
		播放施展动作
		"""
		if speller is None: return
		if not speller.inWorld: return

		type = speller.getWeaponType()
		vehicleType = 0
		castsNames = rds.spellEffect.getCastAction( skillID, type, vehicleType )
		if len( castsNames ) == 0: return False
			
		if skillID in csconst.SKILL_ID_PHYSICS_LIST:
			if speller.nAttackOrder >= len( castsNames ):
				speller.nAttackOrder = 0
			castsName = castsNames[speller.nAttackOrder]
			speller.nAttackOrder += 1
		else:
			castsName = random.choice( castsNames )
		#如果有吟唱动作，动作应该已经预先播放了
		#重复播放一个动作前一个动作会算完成播放了
		if hasattr( speller, "stopMove"): speller.stopMove()
		if type == 0:
			addAction = ACTION_MAP_NO_WEAPON[ speller.vehicleType ]
		else:
			addAction = ACTION_MAP_WEAPON[ speller.vehicleType ][type]
		rds.actionMgr.playActions( speller.getModel(), [ castsName, addAction ] )
		return True	