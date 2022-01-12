# -*- coding: utf_8 -*-
#
# $Id: Buff_62004.py,v 1.2 2008-09-04 07:46:27 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_99019( Buff_Normal ):
	"""
	example:物理攻击力提高40 * 怪物数量%,法术攻击力提高40 * 怪物数量%。
				<Param1>	40	</Param1>
				<Param2>	怪物className	</Param3>
				<Param3>	寻找范围	</Param4>
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100
		self._p2 = str( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )
		self._p3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 )

	def addEffect( self, receiver ):
		"""
		"""
		num = 0
		monsterList = receiver.entitiesInRangeExt( self._p3, "Monster", receiver.position )
		for e in monsterList:
			if e.className == self._p2:
				num += 1
		
		receiver.damage_min_percent += self._p1 * ( num - receiver.queryTemp( "99019Num", 0 ) )
		receiver.damage_max_percent += self._p1 * ( num - receiver.queryTemp( "99019Num", 0 ) )
		receiver.magic_damage_percent += self._p1 * ( num - receiver.queryTemp( "99019Num", 0 ) )
		receiver.calcDamageMin()
		receiver.calcDamageMax()
		receiver.calcMagicDamage()
		receiver.setTemp( "99019Num", num )		# 记录目前怪物的数量

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
		self.addEffect( receiver )
		
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
		self.addEffect( receiver )
		
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
		self.addEffect( receiver )

	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		用于buff，表示buff在每一次心跳时应该做什么。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL；如果允许继续则返回True，否则返回False
		@rtype:  BOOL
		"""
		self.addEffect( receiver )
		return Buff_Normal.doLoop( self, receiver, buffData )

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/07/14 04:05:32  kebiao
# no message
#
# 
#