# -*- coding: gb18030 -*-
#
# $Id: Buff_7001.py,v 1.6 2008-08-14 04:00:15 songpeifang Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_7001( Buff_Normal ):
	"""
	example:生命药效	每秒恢复生命值13点。
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._param = 0 #每秒恢复生命值13点。 这里是总值104 需要除

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._param = int( int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / ( self._persistent / self._loopSpeed ) )	

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
		if not receiver.HP == receiver.HP_Max:
			m_addHp = receiver.addHP( self._param )	#先计算加上的点数  再发送加上的消息 hd
			SkillMessage.buff_CureHP( buffData, receiver, m_addHp )
			casterID = buffData["caster"]
			caster = BigWorld.entities.get( casterID )
			if caster:
				caster.doCasterOnCure( receiver, m_addHp )	#治疗目标时触发
				receiver.doReceiverOnCure( caster, m_addHp )   #被治疗时触发
		return Buff_Normal.doLoop( self, receiver, buffData )

#
# $Log: not supported by cvs2svn $
# Revision 1.5  2008/02/13 08:45:54  kebiao
# 添加相关提示信息
#
# Revision 1.4  2008/01/31 07:06:53  kebiao
# 加入治疗信息
#
# Revision 1.3  2007/12/12 01:38:54  kebiao
# 修改平分总值来作用
#
# Revision 1.2  2007/12/03 02:46:00  kebiao
# 修改治疗方式 直接使用技能治疗力
#
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
#
#