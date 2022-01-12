# -*- coding: gb18030 -*-
#
# $Id: Buff_60004.py,v 1.3 2008-09-04 07:46:27 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_60004( Buff_Normal ):
	"""
	example:	生命值上限提高加值	生命恢复速度提高加成
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 #生命值上限提高加值
		self._p2 = 0 #生命恢复速度提高加成

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )
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
		receiver.HP_Max_value += self._p1
		receiver.calcHPMax()
		receiver.HP_regen_percent += self._p2
		receiver.calcHPCureSpeed()

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
		receiver.HP_Max_value += self._p1
		receiver.HP_regen_percent += self._p2

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
		receiver.HP_Max_value -= self._p1
		receiver.calcHPMax()
		receiver.HP_regen_percent -= self._p2
		receiver.calcHPCureSpeed()
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/07/16 08:08:55  huangdong
# 修改了BUFF消失后,当前血量仍然可以高于上限的问题
#
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
#
#