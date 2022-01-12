# -*- coding: gb18030 -*-
#
# $Id: Spell_BuffNormal.py,v 1.10 2008-07-04 03:50:57 kebiao Exp $

"""
"""

import csdefine
from SpellBase import *
import csstatus
import csconst
from Spell_Item import Spell_Item
import Math

class Spell_Buff( SystemSpell ):
	"""
	主要用于系统要求施放一个BUFF， 有时候系统ENTITY想给玩家添加上系统BUFF， 而可能2个ENTITY不在一个
	CELL bigword.entities都找不到， 系统只需要调用玩家 role.cell.spellTarget 施法者为自己 就可以很方便的的施放BUFF
	到玩家身上， 但这个BUFF不走一些 眩晕之类的判断.
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		SystemSpell.__init__( self )

	def init( self, data ):
		"""
		读取技能配置
		@param data: 配置数据
		@type  data: python dict
		"""
		SystemSpell.init( self, data )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		self.receiveLinkBuff( caster, receiver )

class Spell_BuffNormal( Spell ):
	"""
	法术技能施放BUFF 或者 物理技能施放BUFF，  技能并不做任何事情 只是施放一个BUFF
	主要是不带伤害计算的一个优化，  该技能还需要细分为 物理和法术 继续优化.
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )

	def init( self, data ):
		"""
		读取技能配置
		@param data: 配置数据
		@type  data: python dict
		"""
		Spell.init( self, data )

	def getCastRange( self, caster ):
		"""
		法术释放距离
		"""
		if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS or self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			val1 = caster.magicSkillRangeVal_value
			val2 = caster.magicSkillRangeVal_percent
			if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
				val1 = caster.phySkillRangeVal_value
				val2 = caster.phySkillRangeVal_percent
			return ( self._skillCastRange + val1 ) * ( 1 + val2 / csconst.FLOAT_ZIP_PERCENT )
		return Spell.getCastRange( self, caster )

	def getRangeMax( self, caster ):
		"""
		virtual method.
		@param caster: 施法者，通常某些需要武器射程做为距离的法术就会用到。
		@return: 施法距离
		"""
		if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS or self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			val1 = caster.magicSkillRangeVal_value
			val2 = caster.magicSkillRangeVal_percent
			if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
				val1 = caster.phySkillRangeVal_value
				val2 = caster.phySkillRangeVal_percent
			return ( self._rangeMax + val1 ) * ( 1 + val2 / csconst.FLOAT_ZIP_PERCENT )
		return Spell.getRangeMax( self, caster )

	def calcExtraRequire( self, caster ):
		"""
		virtual method.
		计算技能消耗的额外值， 由其他装备或者技能BUFF影响到技能的消耗
		return : (额外消耗附加值，额外消耗加成)
		"""
		if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS or self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			val1 = caster.magicManaVal_value
			val2 = caster.magicManaVal_percent
			if self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
				val1 = caster.phyManaVal_value
				val2 = caster.phyManaVal_percent
			return ( val1, val2 / csconst.FLOAT_ZIP_PERCENT )
		return ( 0, 0.0 )

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
		#处理沉默等一类技能的施法判断
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO  > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if ( caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ) ) & caster.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ):
			return csstatus.SKILL_CANT_CAST
		if self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
				return csstatus.SKILL_CANT_CAST
		elif self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ):
				return csstatus.SKILL_CANT_CAST
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER

		return Spell.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		self.receiveLinkBuff( caster, receiver )

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
		Spell.onArrive( self, caster, target )
		# 恶性技能使用触发
		if self.isMalignant():
			caster.doOnUseMaligSkill( self )

class Spell_ItemBuffNormal( Spell_Item ):
	"""
	主要用于物品道具相关的技能直接施放一个BUFF用   他是需要进行物品消损特性的
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )

	def init( self, data ):
		"""
		读取技能配置
		@param data: 配置数据
		@type  data: python dict
		"""
		Spell_Item.init( self, data )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		self.receiveLinkBuff( caster, receiver )		# 接收额外的CombatSpell效果，通常是buff(如果存在的话)

class Spell_BuffNormal_With_Homing( Spell_BuffNormal ):
	"""
	可与神器技能兼容的Spell_BuffNormal技能 by 姜毅
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		
	def cast( self, caster, target ):
		"""
		去除父类接口中关于引导技能的检测，话说俺到是觉得引导检测这种东西不适合扔底层咧
		"""
		self.setCooldownInIntonateOver( caster )
		# 处理消耗
		self.doRequire_( caster )
		#通知所有客户端播放动作/做其他事情
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )

		#保证客户端和服务器端处理的受术者一致
		delay = self.calcDelay( caster, target )
		if delay <= 0.1:
			# 瞬发
			caster.addCastQueue( self, target, 0.1 )
		else:
			# 延迟
			caster.addCastQueue( self, target, delay )

		# 法术施放完毕通知，不一定能打中人哦(是否能打中已经和施法没任何关系了)！
		# 如果是channel法术(未实现)，只有等法术结束后才能调用
		self.onSkillCastOver_( caster, target )



class Spell_CertainBuffNormal( Spell_BuffNormal ):
	"""
	无视眩晕、沉默等负面条件影响的技能
	无视自身处于连击状态
	add by wuxo 2012-6-19
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		self._triggerBuffInterruptCode = []
		
	def init( self, data ):
		"""
		"""
		for val in data[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )
		Spell_BuffNormal.init( self, data )
		
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
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		# 检查技能cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY

		# 施法需求检查
		state = self.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 施法者检查
		state = self.castValidityCheck( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# 检查目标是否符合法术施展
		state = self.getCastObject().valid( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state
		return csstatus.SKILL_GO_ON
	
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		receiver.clearBuff( self._triggerBuffInterruptCode ) #中断buff
		self.receiveLinkBuff( caster, receiver )
		
class Spell_SpaceItemBuffNormal( Spell_ItemBuffNormal ):
	
	def __init__( self ):
		"""
		"""
		Spell_ItemBuffNormal.__init__( self )
		self.spaceName = ""
		self.radius = 0.0
		self.position = None
		
	def init( self, data ):
		"""
		"""
		Spell_ItemBuffNormal.init( self, data )
		self.spaceName = str( data[ "param1" ] )
		self.radius = float( data[ "param2" ] )
		self.position = Math.Vector3( eval(data["param3"]) )
	
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
		if self.spaceName != caster.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ):
			return csstatus.SKILL_SPELL_NOT_SPACENNAME
		if ( caster.position - self.position ).length > self.radius:
			return csstatus.SKILL_SPELL_NOT_SPACENNAME
		return Spell_ItemBuffNormal.useableCheck( self, caster, target )


class Spell_DistanceBuffNormal( Spell_BuffNormal ):
	"""
	有距离要求的加buff
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		self._triggerBuffInterruptCode = []
		self.minDistance = 0.0
		self.maxDistance = 0.0
		
	def init( self, data ):
		"""
		"""
		for val in data[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )
		Spell_BuffNormal.init( self, data )
		param1 = data["param1"].split(";")
		if len( param1 ) == 2:
			self.minDistance = float( param1[0] )
			self.maxDistance = float( param1[1] )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		receiver.clearBuff( self._triggerBuffInterruptCode ) #中断buff
		dis = ( caster.position - receiver.position ).length
		if self.minDistance < dis <  self.maxDistance:
			self.receiveLinkBuff( caster, receiver )
		


# $Log: not supported by cvs2svn $
# Revision 1.9  2008/07/03 02:49:39  kebiao
# 改变 睡眠 定身等效果的实现
#
# Revision 1.8  2008/05/20 01:32:01  kebiao
# modify a bug.
#
# Revision 1.7  2008/05/19 08:52:53  kebiao
# 修改spell_buffnormal 继承
#
# Revision 1.6  2007/12/25 03:09:29  kebiao
# 调整效果记录属性为effectLog
#
# Revision 1.5  2007/12/13 00:48:08  kebiao
# 重新修正了状态改变部分，因为底层有相关冲突机制 因此这里就不再关心冲突问题
#
# Revision 1.4  2007/12/12 07:33:04  kebiao
# 添加沉没一类判断方式
#
# Revision 1.3  2007/12/06 02:51:48  kebiao
# 填加判断当前是否允许施法的判定
#
# Revision 1.2  2007/12/03 03:59:46  kebiao
# 加入物品释放BUFF
#
# Revision 1.1  2007/10/26 07:07:52  kebiao
# 根据全新的策划战斗系统做调整
#
# Revision 1.8  2007/08/15 03:28:57  kebiao
# 新技能系统
#
#
#