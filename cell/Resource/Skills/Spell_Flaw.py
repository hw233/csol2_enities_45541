# -*- coding: gb18030 -*-
#

from bwdebug import *
from SpellBase import Spell
import csstatus
import csdefine

class Spell_Flaw( Spell ):
	"""
	破绽技能
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.param1 = 0
		self.param2 = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		param1 = dict["param1"]
		if param1 != "": self.param1 = int( param1 )			# 前置BUFFID
		param2 = dict["param2"]
		if param2 != "": self.param2 = int( param2 )			# 前置BUFF等级

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
		return csstatus.SKILL_GO_ON

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		if self.param1 != 0:
			# 查找目标是否有前置BUFF
			buffIndexs = receiver.findBuffsByBuffID( self.param1 )
			buffs = [ k for k in buffIndexs if receiver.getBuff( k )["skill"].getLevel() == self.param2 ]
			if len( buffs ) == 0: return

			receiver.removeAllBuffByBuffID( self.param1, [ csdefine.BUFF_INTERRUPT_NONE ] )
		self.receiveLinkBuff( caster, receiver )