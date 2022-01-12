# -*- coding: gb18030 -*-
#

import BigWorld
import csconst
import csdefine
import csstatus
from bwdebug import *

from SpellBase import *
from Spell_BuffRacehorse import Spell_BuffRacehorse


class Skill_760006( Spell_BuffRacehorse ):
	"""
	产生泥潭
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffRacehorse.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_BuffRacehorse.init( self, dict )
		self.param = ( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else "" )


	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		Spell_BuffRacehorse.receive( self, caster, receiver )

	def updateItem( self , caster ):
		"""
		更新物品使用
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		caster.removeRaceItem( item.getOrder() )
		caster.removeTemp( "item_using" )


	def useableCheck( self, caster, target ):
		"""
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		主要是屏蔽信息，避免不能使用物品时提示使用技能
		"""
		# 检查技能cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_ITEM_NOT_READY

		return csstatus.SKILL_GO_ON