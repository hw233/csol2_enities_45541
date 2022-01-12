# -*- coding: gb18030 -*-
#

import BigWorld
import csconst
import csstatus
import csdefine
from bwdebug import *
from Buff_Normal import Buff_Normal

class Buff_107014( Buff_Normal ):
	"""
	周期玄元素伤害
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
		self._p1 = int( int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) )
			
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
		# 元素伤害消减
		p = self.calcElemDamageScissorByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_XUAN, self._p1 )
		p = receiver.calcShieldSuck( receiver, p, csdefine.DAMAGE_TYPE_ELEM_XUAN )
		receiver.receiveSpell( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_ELEM_XUAN, p, 0 )
		receiver.receiveDamage( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_ELEM_XUAN, p )
		return Buff_Normal.doLoop( self, receiver, buffData )
