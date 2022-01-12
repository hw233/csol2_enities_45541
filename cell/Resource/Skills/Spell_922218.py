# -*- coding: gb18030 -*-
#
# $Id: Spell_BuffNormal.py,v 1.10 2008-07-04 03:50:57 kebiao Exp $

"""
"""

import csdefine
from SpellBase import *
import csstatus
import csconst
from Spell_Item import Spell_Item

class Spell_922218( Spell_Item ):
	"""
	收费道具经验奖励
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self._expHour = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )  	#奖励经验小时数

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
		if caster.takeExpRecord[ "freezeTime" ] > 0:
			return csstatus.TAKE_EXP_NOT_RESUME_FAIL
		
		buffs = caster.findBuffsByBuffID( 22117 )
			
		if len( buffs ) > 0:
			buff = caster.getBuff( buffs[ 0 ] )["skill"]
			if ( buff._persistent + self._expHour ) > 5 * 60 * 60: # 如果叠加到身上将会超过5小时 因此不允许
				return csstatus.TAKE_EXP_HOUR_MAX
				
			sk = caster.getBuff( buffs[ 0 ] )["skill"]
			sexp = str( sk.getPercent() ) + "%"
			selfBuff = self.getBuffLink(0).getBuff()
			
			if sk.getPercent() == selfBuff.getPercent():
				# 免费道具与收费道具只能有一个
				if sk.isCharge != selfBuff.isCharge:
					if selfBuff.isCharge:
						caster.statusMessage( csstatus.TAKE_EXP_BUFF_ITEM_NOUSE, sexp )
					else:
						caster.statusMessage( csstatus.TAKE_EXP_BUFF_EXIST, sexp )
					return csstatus.SKILL_NO_MSG
			elif sk.getPercent() < selfBuff.getPercent():
				# 如果当前要添加的高倍率BUFF是免费的， 身上的底倍率是收费道具， 则不允许覆盖
				if sk.isCharge and not selfBuff.isCharge:
					caster.statusMessage( csstatus.TAKE_EXP_BUFF_ITEM_NOUSE1, sexp )
					return csstatus.SKILL_NO_MSG
			else:
				if selfBuff.isCharge:
					caster.statusMessage( csstatus.TAKE_EXP_BUFF_ITEM_NOUSE, sexp )
				else:
					caster.statusMessage( csstatus.TAKE_EXP_BUFF_EXIST, sexp )
				return csstatus.SKILL_NO_MSG
				
		return Spell_Item.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
			
		receiver.setTemp( "rewardExpHour", self._expHour )
		self.receiveLinkBuff( caster, receiver )		# 接收额外的CombatSpell效果，通常是buff(如果存在的话)
		
#
# $Log: not supported by cvs2svn $#
#
#