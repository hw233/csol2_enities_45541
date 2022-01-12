# -*- coding: gb18030 -*-
#
# $Id: Spell_311413.py,v 1.7 2008-07-15 04:06:26 kebiao Exp $

"""
技能对物品施展法术基础。
"""

from SpellBase import *
from Spell_PhysSkill import Spell_PhysSkill2
import utils
import csstatus
import csdefine
from VehicleHelper import getCurrVehicleID
import ECBExtend

class Spell_311413( Spell_PhysSkill2 ):
	"""
	冲锋 冲向敌人，快速靠近目标，造成一定的伤害，8米之内，20米之外不能冲锋
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_PhysSkill2.__init__( self )
		self._triggerBuffInterruptCode = []							# 该技能触发这些标志码中断某些BUFF
		self.config_movespeed = 0
		self.delay_time = 1.0

	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhysSkill2.init( self, dict )
		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )
		if dict[ "param2" ] == "":
			self.config_movespeed = self.getFlySpeed()
		else :
			self.config_movespeed = float( dict[ "param2" ] )
		self.delay_time = float ( dict[ "param3" ] )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if getCurrVehicleID( caster ):
			return csstatus.SKILL_CANT_USE_ON_VEHICLE
		return Spell_PhysSkill2.useableCheck( self, caster, target )

	def getCastRange( self, caster ):
		"""
		法术释放距离
		"""
		return self.getRangeMax( caster ) + 5

	def cast( self, caster, target ):
		"""
		virtual method.
		正式向一个目标或位置施放（或叫发射）法术，此接口通常直接（或间接）由intonate()方法调用。

		注：此接口即原来旧版中的castSpell()接口

		@param     caster: 使用技能的实体
		@type      caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		caster.move_speed = self.config_movespeed
		caster.updateTopSpeed()
		caster.clearBuff( self._triggerBuffInterruptCode ) #删除自身现在所有可以删除的BUFF
		#通知所有客户端播放动作/做其他事情
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )
		self.setCooldownInIntonateOver( caster )
		# 处理消耗
		self.doRequire_( caster )
		#保证客户端和服务器端处理的受术者一致
		delay = self.calcDelay( caster, target )
		# 延迟
		caster.addCastQueue( self, target, delay + 0.35 )
		# 法术施放完毕通知，不一定能打中人哦(是否能打中已经和施法没任何关系了)！
		# 如果是channel法术(未实现)，只有等法术结束后才能调用
		self.onSkillCastOver_( caster, target )

	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		法术抵达目标通告。在默认情况下，此处执行可受术人员的获取，然后调用receive()方法进行对每个可受术者进行处理。
		注：此接口为旧版中的receiveSpell()

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell_PhysSkill2.onArrive( self, caster, target )
		dist = caster.distanceBB( target.getObject() )
		delayTime = dist / caster.move_speed * self.delay_time
		caster.addTimer( delayTime, 0, ECBExtend.CHARGE_SPELL_CBID )
	#	caster.client.onAssaultEnd()    此行注释掉，目的是取消服务器端对冲锋停止的判断

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		distanceBB = caster.distanceBB( receiver )
	#	if distanceBB > 3.5:       此行注释掉，目的是使得技能都可以产生效果
	#		return

		Spell_PhysSkill2.receive( self, caster, receiver )


# $Log: not supported by cvs2svn $
# Revision 1.6  2008/05/28 05:59:47  kebiao
# 修改BUFF的清除方式
#
# Revision 1.5  2008/05/27 08:36:02  kebiao
# 修正了冲锋
#
# Revision 1.4  2008/03/04 08:38:55  kebiao
# 增加最小距离的判断
#
# Revision 1.3  2007/12/29 09:07:28  kebiao
# no message
#
# Revision 1.2  2007/12/29 03:48:06  kebiao
# 增加冲锋支持
#
# Revision 1.1  2007/11/26 08:45:44  kebiao
# 该技能1期代码， 冲锋表现需要支持
#
# Revision 1.1  2007/11/24 08:35:30  kebiao
# no message
#