# -*- coding: gb18030 -*-
#为了实现位置光效实现的客户端脚本

import BigWorld
import csdefine
from bwdebug import *
from gbref import rds
from SpellBase import *
import SkillTargetObjImpl
import csarithmetic
from config.client.NpcSkillName import Datas as npcSkillName


class Spell_TargetPosition( Spell ):
	def __init__( self ):
		"""
		从sect构造SkillBase
		@param sect:			技能配置文件的XML Root Section
		@type sect:				DataSection
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell.init( self, dict )

	def isTargetPositionSkill( self ):
		"""
		判断是否是位置光效技能
		@return: BOOL
		"""
		return True

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
		self.pose.cast( caster, skillID, targetObject )

		rds.skillEffect.playCastEffects( caster, targetObject, self.getID() )

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
