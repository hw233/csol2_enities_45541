# -*- coding: gb18030 -*-
#
# $Id: Spell_AlwaysTogether.py,v 1.1 2008-04-09 08:44:24 wangshufeng Exp $

"""
"""
from bwdebug import *
from Spell_Item import Spell_Item
from Spell_TeleportBase import Spell_TeleportBase
import csstatus
import csconst
import csdefine
import BigWorld


class Spell_322361003( Spell_Item, Spell_TeleportBase ):
	"""
	夫妻技能:形影不离,传送到伴侣身边
	只要伴侣在线，且自身满足使用法术的条件，那么就能够使用。
	不管使用的结果如何（如果对方在副本中则不能传送到对方身边），无论传送是否成功，只要使用成功，就开始cooldown
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )
		Spell_TeleportBase.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		Spell_TeleportBase.init( self, dict )

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
		state = Spell_Item.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:	# 先检查cooldown等条件
			return state

		state = Spell_TeleportBase.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		if not caster.hasCouple():
			return csstatus.SKILL_COUPLE_DIVORCE
		loverBaseMB = caster.getCoupleMB()
		if loverBaseMB is None:
			DEBUG_MSG( "玩家( %s )的爱人不在线。" % ( caster.getName() ) )
			return csstatus.SKILL_LOVER_OFFLINE
			
		caster.setTemp( "couple_teleportRequesting", True )
		loverBaseMB.cell.couple_requestPosition()
		return state
		
	def castValidityCheck( self, caster, receiver ):
		"""
		"""
		state = Spell_Item.castValidityCheck( self, caster, receiver )
		if state != csstatus.SKILL_GO_ON:	# 先检查cooldown等条件
			return state
		if caster.queryTemp( "couple_teleportRequesting", False ):
			teleportInfo = caster.queryTemp( "couple_ringTeleport", () )
			if teleportInfo:
				uid = caster.queryTemp( "item_using" )
				item = caster.getByUid( uid )
				if item is None:
					ERROR_MSG( "cannot find the item form uid[%s]." % uid )
					return
				if teleportInfo[4] != item.query( "creator", "" ):
					return csstatus.SKILL_COUPLE_DIVORCE
				else:
					return csstatus.SKILL_GO_ON
			return csstatus.COUPLE_CANT_TELEPORT_SPECIAL_SPACE
		else:
			return state

	def onSpellInterrupted( self, caster ):
		"""
		当施法被打断时的通知；
		打断后需要做一些事情
		"""
		Spell_Item.onSpellInterrupted( self, caster )
		caster.removeTemp( "couple_teleportRequesting" )
		caster.removeTemp( "couple_ringTeleport" )

	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		针对每一个受术者进行受术处理，如计算伤害、改变属性等等。通常情况下此接口是由onArrive()调用，
		但它亦有可能由SpellUnit::receiveOnreal()方法调用，用于处理一些需要在受术者的real entity身上作的事情。
		但对于是否需要在real entity身上接收，由技能设计者在receive()中自行判断，并不提供相关机制。
		注：此接口为旧版中的onReceive()

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		teleportInfo = caster.queryTemp( "couple_ringTeleport", () )
		caster.removeTemp( "couple_teleportRequesting" )
		caster.removeTemp( "couple_ringTeleport" )
		if teleportInfo:
			caster.gotoSpaceLineNumber( teleportInfo[0], teleportInfo[1], teleportInfo[2], teleportInfo[3] )

# $Log: not supported by cvs2svn $
