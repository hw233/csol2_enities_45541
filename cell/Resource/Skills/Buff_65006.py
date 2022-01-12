# -*- coding: gb18030 -*-
#
# $Id: Buff_65006.py,v 1.2 2008-09-04 07:46:27 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal


class Buff_65006( Buff_Normal ):
	"""
	背水一战，攻击力提高A，物理易伤A，法术易伤A
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0
		self._p2 = 0
		self._p3 = 0
		
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) 			# 攻击力提高
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )			# 物理易伤
		self._p3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 )			# 法术易伤
		
		
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
		receiver.damage_min_value += self._p1
		receiver.damage_max_value += self._p1
		receiver.calcDamageMin()
		receiver.calcDamageMax()
		receiver.receive_damage_value += self._p2
		receiver.receive_magic_damage_value += self._p3
		
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
		receiver.damage_min_value += self._p1
		receiver.damage_max_value += self._p1
		receiver.receive_damage_value += self._p2
		receiver.receive_magic_damage_value += self._p3
		
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
		receiver.damage_min_value -= self._p1
		receiver.damage_max_value -= self._p1
		receiver.calcDamageMin()
		receiver.calcDamageMax()
		receiver.receive_damage_value -= self._p2
		receiver.receive_magic_damage_value -= self._p3

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/08/30 10:01:12  wangshufeng
# npc相关技能、buff
#
#
#