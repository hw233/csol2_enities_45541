# -*- coding: gb18030 -*-
#
# $Id: Buff_16008.py,v 1.10 2008-05-28 02:09:42 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_16008( Buff_Normal ):
	"""
	example:反射不良效果	BUFF		不受到不良效果影响并将其反射回施放者，不良效果包括眩晕、昏睡、沉默、定身、减移动速度、减攻击速度。

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

	def springOnImmunityBuff( self, caster, receiver, buffData ):
		"""
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		buff = buffData[ "skill" ]
		bid = buff.getBuffID()
		if bid == 108001 or bid == 108002 or bid == 108003:
			buff.receive( None, caster ) #此处caster处设为None避免 2个人都有这个抵抗造成循环
			SkillMessage.buff_ReboundEffect( buffData, caster, receiver )
			return csstatus.SKILL_BUFF_IS_RESIST

		return csstatus.SKILL_GO_ON
		
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
		receiver.appendImmunityBuff( buffData[ "skill" ] )
		#receiver.clearBuff( csdefine.BUFF_INTERRUPT_INVINCIBLE_EFFECT ) #删除自身现在所有可以删除的BUFF
		
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
		receiver.appendImmunityBuff( buffData[ "skill" ] )
		
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
		receiver.removeImmunityBuff( buffData[ "skill" ].getUID() )
#
# $Log: not supported by cvs2svn $
# Revision 1.9  2008/02/28 08:25:56  kebiao
# 改变删除技能时的方式
#
# Revision 1.8  2008/02/13 08:41:30  kebiao
# 添加相关提示信息
#
# Revision 1.7  2008/01/30 08:59:11  kebiao
# 修正格式错误
#
# Revision 1.6  2008/01/30 07:07:46  kebiao
# 修改了继承关系
#
# Revision 1.5  2007/12/25 06:42:57  kebiao
# 修改免疫BUFF
#
# Revision 1.4  2007/12/24 09:17:38  kebiao
# 调整springOnImmunityBuff参数
#
# Revision 1.3  2007/12/22 07:36:43  kebiao
# ADD:IMPORT csstatus
#
# Revision 1.2  2007/12/22 02:26:57  kebiao
# 调整免疫相关接口
#
# Revision 1.1  2007/12/21 07:27:45  kebiao
# no message
#
#