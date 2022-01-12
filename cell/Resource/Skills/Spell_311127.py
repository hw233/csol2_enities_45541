# -*- coding: gb18030 -*-
#
from bwdebug import *
import BigWorld
import csconst
from Spell_PhysSkill import Spell_PhysSkill
import time

class Spell_311127( Spell_PhysSkill ):
	"""
	蜂杀物理技能 技能本身的攻击力+角色的物理攻击力  单体
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_PhysSkill.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )

	def calcDamage( self, source, target, skillDamage ):
		"""
		virtual method.
		计算直接伤害
		普通物理伤害（总公式中的基础值）=物理攻击力*（1-被攻击方物理防御减伤）
		技能物理伤害（总公式中的基础值）=技能攻击力*（1-被攻击方物理防御减伤）

		@param source: 攻击方
		@type  source: entity
		@param target: 被攻击方
		@type  target: entity
		@param skillDamage: 技能攻击力
		@return: INT32
		"""
		damagePer = 1.0
		indexs = target.findBuffsByBuffID( 107012 )
		if len( indexs ):
			index = indexs[0]
			buff = target.getBuff( index )
			endTime = buff["persistent"]
			nowTime = time.time()
			skill = buff["skill"]
			lastTime = skill._persistent
			per = ( lastTime - ( endTime - nowTime ) )/( lastTime * 1.0 )
			if per < 0: per = 0
			if per > 1: per = 1
			damagePer += per

		# 计算被攻击方物理防御减伤
		armor = self.calcVictimResist( source, target )
		damage = ( skillDamage * ( 1 - armor ) ) * ( 1 + target.receive_damage_percent / csconst.FLOAT_ZIP_PERCENT ) + target.receive_damage_value
		endDamage = int( damage * damagePer )
		return endDamage
