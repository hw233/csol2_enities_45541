# -*- coding: gb18030 -*-
#

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_7005( Buff_Normal ):
	"""
	恢复目标：生命，法力，百分比
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
		self._p1 = float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) / 100	# hp的百分比
		self._p2 = float( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 ) / 100	# mp的百分比
		
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
		if self._p1 > 0:
			hp_value = receiver.HP_Max * self._p1
			receiver.addHP( int( hp_value ) )
		if self._p2 > 0:
			mp_value = receiver.MP_Max * self._p2
			receiver.addMP( int( mp_value ) )

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
		if self._p1 > 0:
			hp_value = receiver.HP_Max * self._p1
			receiver.addHP( int( hp_value ) )
		if self._p2 > 0:
			mp_value = receiver.MP_Max * self._p2
			receiver.addMP( int( mp_value ) )

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
		if self._p1 > 0:
			hp_value = receiver.HP_Max * self._p1
			receiver.addHP( int( hp_value ) )
		if self._p2 > 0:
			mp_value = receiver.MP_Max * self._p2
			receiver.addMP( int( mp_value ) )
		return Buff_Normal.doLoop( self, receiver, buffData )
#