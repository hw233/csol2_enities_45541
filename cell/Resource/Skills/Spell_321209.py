# -*- coding: gb18030 -*-

from bwdebug import *
from Spell_PhysSkill import Spell_PhysSkill
import csstatus
import csconst
import csdefine
import BigWorld
import random

class Spell_321209( Spell_PhysSkill ):
	"""
	单近攻，增物攻，定几率提高自己和队友的暴击几率，持续10秒
	"""
	def __init__( self ):
		"""
		"""
		Spell_PhysSkill.__init__( self )
		self._range = 0.0
		self._rate = 0.0
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )
		self._range = float( dict[ "param1" ] )
		self._rate = int( dict[ "param2" ] )
		
	def receiveLinkBuff( self, caster, receiver ):
		"""
		给entity附加buff的效果
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 施展对象
		@type  receiver: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		if random.randint( 0, 100 ) <= self._rate:
			elist = caster.getAllMemberInRange( self._range )
			if len( elist ) <= 0:
				elist = [ caster ]
				
			for e in elist:
				self._buffLink[0].getBuff().receive( caster, e )	
