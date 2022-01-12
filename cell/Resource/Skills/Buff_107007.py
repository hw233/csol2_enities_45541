# -*- coding: gb18030 -*-
#
# $Id: Buff_107007.py,v 1.2 2008-02-13 08:41:04 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal


class Buff_107007( Buff_Normal ):
	"""
	example:失去法力值%	DEBUFF	无属性损失法力	按一定数值缓慢失去法力。
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 # 消耗总MP值 

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		
		Buff_Normal.init( self, dict )
		self._p1 = int( (int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) /100.0) / ( self._persistent / self._loopSpeed ) )	
			
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
		SkillMessage.buff_ConsumeMP( buffData, receiver, receiver.MP_Max * self._p1 )
		receiver.setMP( receiver.MP - receiver.MP_Max * self._p1 )
		return Buff_Normal.doLoop( self, receiver, buffData )

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
# 
#