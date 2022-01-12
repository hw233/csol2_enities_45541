# -*- coding: gb18030 -*-
#
# $Id:  Exp $


from SpellBase import *
import random
import csdefine
import csstatus
from bwdebug import *
from Spell_Magic import *

class Spell_SunBurn( Spell_MagicVolley ):
	"""
	烈日灼体
	"""
	def __init__( self ):
		"""
		"""
		Spell_MagicVolley.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_MagicVolley.init( self, dict )
		self.param1 = float( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0.0 )
	
	
	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		法术抵达目标通告。在默认情况下，此处执行可受术人员的获取，然后调用receive()方法进行对每个可受术者进行处理。
		注：此接口为旧版中的receiveSpell()

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""

		# 获取所有受术者
		receivers = self.getReceivers( caster, target )
		for receiver in receivers:
			receiver.clearBuff( self._triggerBuffInterruptCode )
			receiver.setTemp( "SunFire_Count", len(receivers) )
			self._skill.cast( caster, SkillTargetObjImpl.createTargetObjEntity( receiver ) )
			self.receiveEnemy( caster, receiver )
		# 恶性技能使用触发
		caster.doOnUseMaligSkill( self )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if caster is not None:
			casterID = caster.id
		else:
			casterID = 0
		if not receiver.isReal():
			receiver.receiveOnReal( casterID, self )
			return
		value = self.param1/receiver.queryTemp( "SunFire_Count", 1.0 )
		#计算御敌、破敌带来的实际减免 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		value *= rm
			
		#receiver.receiveDamage( caster.id, self.getID(), csdefine.DAMAGE_TYPE_MAGIC, value )
		self.persentDamage( caster, receiver, csdefine.DAMAGE_TYPE_MAGIC, value )
		receiver.removeTemp( "SunFire_Count" )