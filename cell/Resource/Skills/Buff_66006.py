# -*- coding: gb18030 -*-
#
# $Id: Buff_23003.py,v 1.3 2008-02-28 08:25:56 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_66006( Buff_Normal ):
	"""
	example:禁断之恋	你和你的宠物，不再分彼此。

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
		self._p1 = long( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )

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
		actPet = receiver.pcg_getActPet()
		if actPet and actPet.etype != "MAILBOX":
			if actPet.entity and actPet.entity.state == csdefine.ENTITY_STATE_DEAD:
				receiver.spellTarget( self._p1, receiver.id )
				return False
		return Buff_Normal.doLoop( self, receiver, buffData )

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
#
# $Log: not supported by cvs2svn $
#