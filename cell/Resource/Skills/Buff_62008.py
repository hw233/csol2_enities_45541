# -*- coding: gb18030 -*-
#
# $Id: Buff_62005.py,v 1.2 2007-12-13 04:59:55 zds $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
import Const
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_62008( Buff_Normal ):
	"""
	example:同时增加物理、法术命中 by姜毅
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )  * 100
		
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
		receiver.hitProbability_percent += self._p1
		receiver.calcHitProbability()
		receiver.magic_hitProbability_percent += self._p2
		receiver.calcMagicHitProbability()
	
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
		receiver.hitProbability_percent += self._p1
		receiver.magic_hitProbability_percent += self._p2
	
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
		receiver.hitProbability_percent -= self._p1
		receiver.calcHitProbability()
		receiver.magic_hitProbability_percent -= self._p2
		receiver.calcMagicHitProbability()
		