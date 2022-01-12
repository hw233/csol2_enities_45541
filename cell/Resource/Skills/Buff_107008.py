# -*- coding: gb18030 -*-
#
# $Id: Buff_107008.py,v 1.9 2008-08-11 07:55:59 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csdefine
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal


class Buff_107008( Buff_Normal ):
	"""
	example:损失法力A，受到%法术伤害	DEBUFF	无属性损失法力/法术伤害	按一定数值减少魔法值，并受到一定比例的法术伤害。

	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 # 消耗总hP值 

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / ( self._persistent / self._loopSpeed ) )	
			
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
		SkillMessage.buff_ConsumeMP( buffData, receiver, self._p1 )
		receiver.setMP( receiver.MP - self._p1 )
		damage = self.calcDotDamage( receiver, receiver, csdefine.DAMAGE_TYPE_VOID, int( self._p1 ) )
		receiver.receiveSpell( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_VOID, damage, 0 )
		receiver.receiveDamage( buffData["caster"], self.getID(), csdefine.DAMAGE_TYPE_FLAG_BUFF|csdefine.DAMAGE_TYPE_VOID, damage )
		return Buff_Normal.doLoop( self, receiver, buffData )

#
# $Log: not supported by cvs2svn $
# Revision 1.8  2008/04/10 04:08:26  kebiao
# 改为在接受伤害之前通知客户端接受技能处理
#
# Revision 1.7  2008/04/10 03:25:50  kebiao
# modify to receiveSpell pertinent.
#
# Revision 1.6  2008/03/31 09:04:02  kebiao
# 修改receiveDamage和通知客户端接受某技能结果分开
# 技能通过receiveSpell通知客户端去表现，支持各技能不同的表现
#
# Revision 1.5  2008/02/13 08:41:04  kebiao
# 添加相关提示信息
#
# Revision 1.4  2007/12/21 08:56:32  kebiao
# no message
#
# Revision 1.3  2007/12/21 08:43:14  kebiao
# no message
#
# Revision 1.2  2007/12/21 07:28:00  kebiao
# no message
#
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
# 
#