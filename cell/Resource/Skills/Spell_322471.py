# -*- coding: gb18030 -*-

from bwdebug import *
from Spell_Magic import Spell_Magic
import csstatus
import csconst
import csdefine
import BigWorld
import random

class Spell_322471( Spell_Magic ):
	"""
	天机剑
	
	30%基础法力。对目标造成一定的法术伤害，同时提高周围10米内所有玩家的物理攻击力。
	持续10秒。10秒冷却。等级越高，伤害越大，同时提高物理攻击力越多。
	"""
	def __init__( self ):
		"""
		"""
		Spell_Magic.__init__( self )
		self._range = 0.0
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		self._range = float( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )
		
	def receiveLinkBuff( self, caster, receiver ):
		"""
		给entity附加buff的效果
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 施展对象
		@type  receiver: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		elist = caster.getAllMemberInRange( self._range )
		if len( elist ) <= 0:
			elist = [ caster ]
			
		for e in elist:
			self._buffLink[0].getBuff().receive( caster, e )
			