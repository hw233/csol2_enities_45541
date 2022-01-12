# -*- coding: gb18030 -*-
#
# $Id: Spell_512705.py,v 1.4 2008-07-15 04:06:26 kebiao Exp $

"""
"""

from SpellBase import *
from Spell_Magic import Spell_Magic
import random
import csdefine
import csconst
import Const

class Spell_512705( Spell_Magic ):
	"""
	物理技能	法术攻击敌人造成额外伤害，并有30%几率取消对方身上的一个有益BUFF
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Magic.__init__( self )
		self._triggerBuffInterruptCode = []							# 该技能触发这些标志码中断某些BUFF
		
	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		self._dispelRate = int( dict.get( "param1" , 0 ) )			# 可驱散几率
		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )
				
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
		Spell_Magic.onArrive( self, caster, target )
		receiver = target.getObject()
		if not receiver:
			return
			
		#因为该技能为单体技能 所以此处这么做是对的 caster is real
		# 在 Spell_Magic.onArrive( self, caster, receiver ) 可能导致 receiver为real 所以要这么做
		Spell_Magic.receive( self, caster, receiver ) 
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		if random.randint(0,100) > self._dispelRate:
			return
		# 驱散目标身上的buff

		for index, buff in enumerate( receiver.getBuffs() ):
			skill = buff["skill"]
			if skill.getEffectState() == csdefine.SKILL_EFFECT_STATE_BENIGN and skill.getLevel() < self.getLevel():# 只能驱散比自己级别底的BUFF
				receiver.removeBuff( index, self._triggerBuffInterruptCode )
				break
			
# $Log: not supported by cvs2svn $
# Revision 1.3  2008/05/28 05:59:47  kebiao
# 修改BUFF的清除方式
#
# Revision 1.2  2007/12/26 09:03:57  kebiao
# no message
#
# Revision 1.1  2007/12/26 03:54:24  kebiao
# no message
#
#