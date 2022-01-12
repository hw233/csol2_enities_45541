# -*- coding: gb18030 -*-
#
# $Id: Skill_Normal.py,v 1.7 2008-08-13 07:55:41 kebiao Exp $

"""
攻击技能类。
"""

from bwdebug import *
from SpellBase.Spell import Spell
import BigWorld
import csconst
import csstatus
import csdefine

class Skill_Normal( Spell ):
	"""
		技能的持续性效果
		所有"Buff"类均由"Buff_"开头
		注：此类为旧版中的Condition类
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )

	def getType( self ):
		"""
		取得基础分类类型
		这些值是BASE_SKILL_TYPE_*之一
		"""
		return csdefine.BASE_SKILL_TYPE_PASSIVE
		
	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		为目标附上一个效果，通常被附上的效果是实例自身，它可以通过detach()去掉这个效果。具体效果由各派生类自行决定。
		
		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		pass

	def detach( self, ownerEntity ):
		"""
		virtual method = 0;
		执行与attach()的反向操作

		@param ownerEntity:	拥有者实体
		@type ownerEntity:	BigWorld.Entity
		"""
		pass
			
	def use( self, caster, receiver, position ):
		"""
		virtual method = 0.
		请求对 target/position 施展一个法术，任何法术的施法入口由此进。
		dstEntity和position是可选的，不用的参数用None代替，具体看法术本身是对目标还是位置，一般此方法都是由client调用统一接口后再转过来。
		默认啥都不做，直接返回。
		注：此接口即原来旧版中的cast()接口
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者，None表示不存在
		@type  receiver: Entity
		@param position: 位置
		@type  position: VECTOR3
		"""
		ERROR_MSG( "I not support this the function!" )
		return

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param   receiver: 目标实体，如果没有接受者则为None
		@type    receiver: Entity
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		ERROR_MSG( "I not support this the function!" )
		return csstatus.SKILL_UNKNOW
		
	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		针对每一个受术者进行受术处理，如计算伤害、改变属性等等。
		通常情况下此接口是由onArrive()调用，但它亦有可能由SpellUnit::receiveOnreal()方法调用，
		用于处理一些需要在受术者的real entity身上作的事情。但对于是否需要在real entity身上接收，
		由技能设计者在receive()中自行关断，并不提供相关机制。
		
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		ERROR_MSG( "I not support this the function!" )
		return

	def newSelf( self ):
		"""
		产生一个新的UID技能实例
		"""
		data = self.addToDict()
		return self.createFromDict( data )

#
# $Log: not supported by cvs2svn $
# Revision 1.6  2008/02/27 07:57:15  kebiao
# add:import csdefine
#
# Revision 1.5  2007/12/25 09:31:59  kebiao
# delete:
# import Effects
#
# Revision 1.4  2007/10/26 07:06:41  kebiao
# 根据全新的策划战斗系统做调整
#
# Revision 1.3  2007/08/15 03:28:41  kebiao
# 新技能系统
#
# Revision 1.2  2007/07/10 07:54:57  kebiao
# 重新调整了整个技能结构因此该模块部分被修改
#
#
#