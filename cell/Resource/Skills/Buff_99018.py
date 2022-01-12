# -*- coding: gb18030 -*-
#
# $Id: Buff_99018.py,v 1.2 2009-09-19 08:01:12 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import Const
import csstatus
import csdefine
from Function import newUID
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import time

class Buff_99018( Buff_Normal ):
	"""
	example: 表现良好	在监狱中PK值减少的更快。
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
		self._rate = float( dict[ "Param1" ] ) - 1.0

	def startNewPkValueTimer( self, receiver ):
		"""
		"""
		# 先停止pk值消减timer 
		receiver.endPkValueTimer()
		
		# 使用新的timer速度
		val = Const.PK_VALUE_PRISON_LESS_TIME - ( Const.PK_VALUE_PRISON_LESS_TIME * self._rate )
		DEBUG_MSG( "NewPkValueTimer tick = %i" % val )
		receiver.startPkValueTimer( val, val )
	
	def restorePkValueTimer( self, receiver ):
		"""
		"""
		if receiver.pkValue <= 0:
			return
			
		# 先停止pk值消减timer 
		receiver.endPkValueTimer()
		receiver.startPkValueTimer()
		
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
		self.startNewPkValueTimer( receiver )
		receiver.statusMessage( csstatus.PRISON_BUFF_GOOD )
		
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
		# receiver.setPkValue( receiver.pkValue - 1 )
		spaceKey = receiver.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if spaceKey != "fu_ben_jian_yu":
			return False
		return Buff_Normal.doLoop( self, receiver, buffData )
		
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
		self.startNewPkValueTimer( receiver )
		
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
		self.restorePkValueTimer( receiver )
































