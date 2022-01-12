# -*- coding: gb18030 -*-

# 系统技能，生成一个AreaRestrictTransducer的entity(陷阱功能entity)，在接受者位置

import BigWorld
import csdefine
import csstatus
from SpellBase import *
from Spell_DirectDamage import Spell_DirectPhyDamage

class Spell_311129( Spell_DirectPhyDamage ):
	"""
	同上直接伤害，另增加使目标法力减少
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_DirectPhyDamage.__init__( self )
		self.mpVal = 0				# 使法力减少值

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_DirectPhyDamage.init( self, dict )
		self.mpVal = int( dict[ "param1" ] )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		技能实现的目的
		"""
		Spell_DirectPhyDamage.receive( self, caster, receiver )
		val = min(receiver.MP, self.mpVal)
		receiver.MP -= val
