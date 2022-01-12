# -*- coding: gb18030 -*-
#
# $Id: Buff_8001.py,v 1.6 2008-05-28 02:09:42 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import csstatus

class Buff_8001( Buff_Normal ):
	"""
	example:单位同时免疫定身，昏睡，眩晕3个不良状态，并且免除当前所受的以上状态。
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		
	def springOnImmunityBuff( self, caster, receiver, buffData ):
		"""
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		buff = buffData[ "skill" ]
		bid = buff.getBuffID()
		if bid == 108001 or bid == 108002 or bid == 108003:
			return csstatus.SKILL_BUFF_IS_RESIST
		return csstatus.SKILL_GO_ON
		
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.appendImmunityBuff( buffData[ "skill" ] )
		#receiver.clearBuff( csdefine.BUFF_INTERRUPT_INVINCIBLE_EFFECT ) #删除自身现在所有可以删除的BUFF
		#receiver.removeAllBuffByID( 108001, csdefine.BUFF_INTERRUPT_NONE )
		#receiver.removeAllBuffByID( 108002, csdefine.BUFF_INTERRUPT_NONE )
		#receiver.removeAllBuffByID( 108003, csdefine.BUFF_INTERRUPT_NONE )
		
	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.appendImmunityBuff( buffData[ "skill" ] )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeImmunityBuff( buffData[ "skill" ].getUID() )
		