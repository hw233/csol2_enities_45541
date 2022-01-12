# -*- coding: gb18030 -*-
#
# $Id: Buff_1003.py,v 1.2 2007-12-13 04:59:55 huangyongwei Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_22100( Buff_Normal ):
	"""
	日光浴中使用清爽饮料使得经验翻倍
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
						# 使用这个饮料能够翻的倍率( 比如是双倍还是1.5倍 )
		self._p1 = 1.0	# 默认为1倍经验，也就是不翻倍
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0.0 ) 		# 翻多少倍
		if self._p1 == 0.0:
			self._p1 = 1.0
		
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
		receiver.setTemp( "has_cleanlily_drink", 1 )		# 设置标记标示玩家使用了清爽饮料
		receiver.setTemp( "drink_exp_rate", self._p1 )		# 设置标记标示清爽饮料能翻的倍率
	
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
		receiver.setTemp( "has_cleanlily_drink", 1 )		# 设置标记标示玩家使用了清爽饮料
		receiver.setTemp( "drink_exp_rate", self._p1 )		# 设置标记标示清爽饮料能翻的倍率
		
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
		receiver.removeTemp( "has_cleanlily_drink" )		# 清除标示
		receiver.removeTemp( "drink_exp_rate" )