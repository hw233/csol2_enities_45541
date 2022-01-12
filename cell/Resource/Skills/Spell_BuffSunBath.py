# -*- coding: gb18030 -*-
#
# 日光浴的技能

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from SpellBase import *
from Spell_BuffNormal import Spell_BuffNormal


class Spell_BuffSunBath( Spell_BuffNormal ):
	"""
	日光浴buff技能
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )
		
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
		# 能否使用这个技能的条件判断
		# 目前是不管怎样都能用这个技能
		return csstatus.SKILL_GO_ON
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		receiver = caster	# 因为施法者是玩家自己，但是接收者确有可能是npc
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		self.receiveLinkBuff( caster, receiver )