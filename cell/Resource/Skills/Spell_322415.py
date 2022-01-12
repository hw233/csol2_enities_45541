# -*- coding: gb18030 -*-
#
from Spell_BuffNormal import Spell_BuffNormal
import random
import csdefine
import csstatus

class Spell_322415( Spell_BuffNormal ):
	"""
	隐匿技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_BuffNormal.__init__( self )
		self._isCanFight = 0  #是否可战斗状态下使用

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell_BuffNormal.init( self, dict )
		if dict["param1"] != "":
			self._isCanFight = int( dict["param1"] )	

	def useableCheck( self, caster, receiver ):
		"""
		virtual method.
		校验技能是否可以使用
		"""
		if not self._isCanFight: #0 只能在自由状态下使用
			if caster.state != csdefine.ENTITY_STATE_FREE:
				return csstatus.SKILL_NEED_STATE_FREE
		return Spell_BuffNormal.useableCheck( self, caster, receiver )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		self.receiveLinkBuff( caster, receiver )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			actPet = receiver.pcg_getActPet()
			if actPet:
				petEntiy = actPet.entity
				if not petEntiy.isReal():
					petEntiy.receiveOnReal( caster.id, self )
				else:
					self.receiveLinkBuff( caster, petEntiy )
