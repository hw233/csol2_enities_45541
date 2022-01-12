# -*- coding: gb18030 -*-
#
# $Id: Buff_Normal.py,v 1.23 2008-09-04 06:14:35 kebiao Exp $

"""
攻击技能类。
"""

from bwdebug import *
from SpellBase.Buff import Buff
from SpellBase.SkillAttack import SkillAttack
import BigWorld
import csconst
import csstatus
import csdefine
from Resource.SkillLoader import g_buffLimit


class Buff_Normal( Buff, SkillAttack ):
	"""
		技能的持续性效果
		所有"Buff"类均由"Buff_"开头
		注：此类为旧版中的Condition类
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff.__init__( self )
		SkillAttack.__init__( self )
		self._15SecondRuleTimeval = 15.0 # buff15秒规则中的时间取值 BUFF持续时间大于15 按15算 否则 按持续时间算
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff.init( self, dict )
		SkillAttack.init( self, dict )
		if self._persistent < 15.0:
			self._15SecondRuleTimeval = self._persistent
			
	def _replaceLowLvBuff( self, caster, receiver, newBuff, buffs ):
		"""
		Buff 的 替换子流程  从buffs中替换最低级别的BUFF
		@param receiver: 受击者
		@type  receiver: Entity
		@param newBuff: 新BUFF的数据
		@type  newBuff: BUFF
		@param buffs: 准备用来判断的buff索引列表
		"""
		lowBuffIdx = buffs[ 0 ]
		#第一步 从buffs找出比自己级别低或者等于自己级别的BUFF
		for bIndex in buffs:
			if receiver.getBuff( bIndex )[ "skill" ].getLevel() <= receiver.getBuff( lowBuffIdx )[ "skill" ].getLevel():
				lowBuffIdx = bIndex

		#找出最低级别进行替换
		if self.getLevel() >= receiver.getBuff( lowBuffIdx )[ "skill" ].getLevel():
			receiver.setTemp( "SAME_TYPE_BUFF_REPLACE", True )
			receiver.removeBuff( lowBuffIdx, [ csdefine.BUFF_INTERRUPT_NONE ] )
			receiver.setTemp( "SAME_TYPE_BUFF_REPLACE", False )
			receiver.addBuff( newBuff )
		else:
			#caster.statusMessage( csstatus.SKILL_ADDBUFF_FAIL_LOW_LV )#添加失败
			return
		
	def _addBuffToSameType( self, receiver, newBuff ):
		"""
		向同一类BUFF中添加一个新BUFF （子流程规则）
		@param receiver: 受击者
		@type  receiver: Entity
		@param newBuff: 新BUFF的数据
		@type  newBuff: BUFF
		"""
		# 获取所有同类型同性质的BUFF或DEBUFF
		buffs = receiver.getBuffIndexsByType( self.getBuffType(), self._effectState ) #获取所有的BUFF 或者 DEBUFF
		# 查询该BUFF所对应的类型能够同时存在的数量是否超过  BUFF大类   XXX类型（(buff)3/(debuff)4）
		buffcount = len( buffs )
		receiver.setTemp( "SAME_TYPE_BUFF_REPLACE", True )
		if buffcount > 0:
			if buffcount >= g_buffLimit.getBuffLimit( self.getBuffType(), self._effectState ):
				receiver.removeBuff( receiver.findRemainTimeMinByIndexs( buffs ), [csdefine.BUFF_INTERRUPT_NONE] )
			else:
				# 获取所有同性质（忽略同类型）的BUFF或DEBUFF 是否到上限
				buffs = receiver.getBuffIndexsByEffectType( self._effectState )
				if len( buffs ) >= 16: # buff or debuff
					receiver.removeBuff( receiver.findRemainTimeMinByIndexs( buffs ), [csdefine.BUFF_INTERRUPT_NONE] )
		receiver.setTemp( "SAME_TYPE_BUFF_REPLACE", False )
		receiver.addBuff( newBuff )
	
	def _findAllCanReplaceBySType( self, receiver, buffs ):
		"""
		从buffs 找出所有能够和该BUFF来源类型进行替换操作的BUFF索引
		@param receiver: 受击者
		@type  receiver: Entity
		@param buffs: 准备用来判断的buff索引列表
		"""
		limitSourceTypeList = g_buffLimit.getSourceLimit( self._sourceType )
		replaceList = []
		for bIdx in buffs:
			if receiver.getBuff( bIdx )["skill"].getSourceType() in limitSourceTypeList:
				replaceList.append( bIdx )
		return replaceList

	def calcTwoSecondRule( self, source, skillDamageExtra ):
		"""
		virtual method.
		法术的2秒规则计算 (攻击型 buff or spell)
		"""
		return skillDamageExtra * self._shareValPercent

	def calcBuff15SecondRule( self, damage ):
		"""
		virtual method.
		buff的15秒规则计算 (攻击型 buff)
		@param damage: 角色的攻击力 （物理或法术）
		"""
		return int( damage * self._15SecondRuleTimeval / 15.0 )

	def receive( self, caster, receiver ):
		"""
		用于给目标施加一个buff，所有的buff的接收都必须通过此接口，
		此接口必须判断接收者是否为realEntity，
		如果否则必须要通过receiver.receiveOnReal()接口处理。

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
			
		if receiver.getState() == csdefine.ENTITY_STATE_DEAD:
			return
			
		newBuff = self.getNewBuffData( caster, receiver )
		
		#由于需要免疫的类型非常的多非常的不确定因此使用该处理方式
		#receiver is real,所以可以这么做
		state = receiver.doImmunityBuff( caster, newBuff )
		if state != csstatus.SKILL_GO_ON:
			DEBUG_MSG( "addbuff state is ", state )
			return
		# 处理光环效果
		"""
		光环效果将不在BUFF/DEBUFF的替换判断之列。经效果来源数据特别指出的光环效果
		（光环效果定义为：指定范围——可为固定区域或移动区域——内有效，无持续时间的效果），
		将占有特定的BUFF/DEBUFF位置，不会被其他效果替换，仅可以被更高等级的相同效果替换。
		指定为BUFF或DEBUFF的光环效果分别显示在BUFF或DEBUFF的位置。光环效果不参与可承受数量的计算。
		"""
		if self.isRayRingEffect():
			# 获取所有同类型同性质的光环BUFF或光环DEBUFF
			buffs = receiver.getBuffIndexsByType( self.getBuffType(), self._effectState )
			if len( buffs ) > 0: #不参与可承受数量的计算 有同类光环效果那么 替换等级最底的 否则直接添加
				self._replaceLowLvBuff( caster, receiver, newBuff, buffs )
			else:
				receiver.addBuff( newBuff )
			return
		
		buffs = receiver.findBuffsByBuffID( self._buffID )
		#判断是否有相同的buff
		if len( buffs ) > 0:
			if not self._isAppendPrevious:
				replaceList = self._findAllCanReplaceBySType( receiver, buffs )
				if len( replaceList ) > 0:
					self._replaceLowLvBuff( caster, receiver, newBuff, replaceList )
				else:
					if len( buffs ) >= self._stackable:
						self._replaceLowLvBuff( caster, receiver, newBuff, buffs )
					else:
						self._addBuffToSameType( receiver, newBuff )
			else:
				self.doAppend( receiver, buffs[0] )
		else:
			self._addBuffToSameType( receiver, newBuff )
		
	def use( self, caster, target ):
		"""
		virtual method.
		请求对 target/position 施展一个法术，任何法术的施法入口由此进。
		dstEntity和position是可选的，不用的参数用None代替，具体看法术本身是对目标还是位置，一般此方法都是由client调用统一接口后再转过来。
		默认啥都不做，直接返回。
		注：此接口即原来旧版中的cast()接口
		@param   caster: 施法者
		@type    caster: Entity
		
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		ERROR_MSG( "I do not support this the function!" )

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
		ERROR_MSG( "I do not support this the function!" )
		return csstatus.SKILL_UNKNOW
#
# $Log: not supported by cvs2svn $
# Revision 1.22  2008/08/05 00:26:07  huangdong
# 加入死亡后不接收BUFF的判断
#
# Revision 1.21  2008/05/28 05:59:25  kebiao
# 修改BUFF的清除方式
#
# Revision 1.20  2008/04/25 08:16:10  kebiao
# 新规则 查看是否有相同ID的BUFF 替换他们的规则是 他们其中有一个必须时间已经流失了2/3
#
# Revision 1.19  2008/04/10 03:27:16  kebiao
# 去掉添加BUFF时的一些entity状态判定 由各自的entity模块去重载addBuff
# 根据不同类型的entity自身特定状态决定是否可以添加BUFF
#
# Revision 1.18  2008/01/11 03:24:34  kebiao
# 添加entity一些状态处理
#
# Revision 1.17  2008/01/02 07:47:15  kebiao
# 调整技能部分结构与接口
#
# Revision 1.16  2007/12/24 09:13:17  kebiao
# 添加BUFF状态支持，修正删除BUFF时索引错误BUG
#
# Revision 1.15  2007/12/22 02:26:57  kebiao
# 调整免疫相关接口
#
# Revision 1.14  2007/12/21 02:32:03  kebiao
# 添加光环处理注释和修改一个BUG
#
# Revision 1.13  2007/12/20 07:14:54  kebiao
# 添加光环效果判断
#
# Revision 1.12  2007/12/11 04:05:17  kebiao
# 加入抵抗BUFF支持
#
# Revision 1.11  2007/12/07 09:01:17  kebiao
# 修改注释
#
# Revision 1.10  2007/12/07 04:13:45  kebiao
# 添加 替换同类BUFF失败返回失败信息
#
# Revision 1.9  2007/11/30 08:45:13  kebiao
# csstatus.BUFF_INTERRUPT
# TO：
# csdefine.BUFF_INTERRUPT
#
# Revision 1.8  2007/11/20 08:18:10  kebiao
# 战斗系统第2阶段调整
#
# Revision 1.7  2007/11/02 08:59:26  kebiao
# 修改技能部分接口
#
# Revision 1.6  2007/08/31 08:59:57  kebiao
# 修改一处接口
#
# Revision 1.5  2007/08/18 02:47:23  kebiao
# 修改了叠加方式
#
# Revision 1.4  2007/08/15 03:27:38  kebiao
# 新技能系统
#
# Revision 1.3  2007/07/10 07:54:57  kebiao
# 重新调整了整个技能结构因此该模块部分被修改
#
#
#