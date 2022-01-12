# -*- coding: gb18030 -*-
#
# $Id: Buff_24002.py,v 1.2 2008-02-28 08:25:56 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csdefine
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Shield import Buff_Shield

class Buff_24002( Buff_Shield ):
	"""
	example:受到法术伤害的%i%%转化为生命
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Shield.__init__( self )
		self._p1 = 0 # %i比率
		self._param = 0
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Shield.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0	
		
	def doShield( self, receiver, damageType, damage ):
		"""
		virtual method.
		执行护盾自身功能  如：法术形转化伤害为MP 
		注意: 此接口不可手动删除该护盾
		@param receiver: 受术者
		@param damageType: 伤害类型
		@param damage : 本次伤害值
		@rtype: 返回被消减后的伤害值
		"""
		if damageType != csdefine.DAMAGE_TYPE_MAGIC:
			return damage
			
		val = damage * self._p1
		# 这里必须判断real 否则可能会被设置2次， 具体看shieldConsume机制
		if receiver.isReal():			
			receiver.addHP( val )

		return 0
		
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
		Buff_Shield.doBegin( self, receiver, buffData )
		receiver.appendShield( buffData[ "skill" ] )
		
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
		Buff_Shield.doReload( self, receiver, buffData )
		receiver.appendShield( buffData[ "skill" ] )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Shield.doEnd( self, receiver, buffData )
		receiver.removeShield( buffData[ "skill" ].getUID() )


#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/12/20 03:04:13  kebiao
# no message
#
#