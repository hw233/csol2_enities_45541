# -*- coding: gb18030 -*-
#
# $Id: Buff_4014.py,v 1.3 2008-07-17 03:58:05 huangdong Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_4014( Buff_Normal ):
	"""
	物理、法术防御力减少%
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 #降低法术防御力
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100
		
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
		receiver.armor_percent -= self._p1
		receiver.calcArmor()
		receiver.magic_armor_percent -= self._p1
		receiver.calcMagicArmor()

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
		receiver.armor_percent -= self._p1
		receiver.magic_armor_percent -= self._p1
		
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
		receiver.armor_percent += self._p1
		receiver.calcArmor()
		receiver.magic_armor_percent += self._p1
		receiver.calcMagicArmor()
		
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/07/10 03:09:37  wangshufeng
# 修正buff结束时receiver.armor_percent的计算错误。
#
# Revision 1.1  2007/12/20 05:44:03  kebiao
# no message
#
#