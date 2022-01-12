# -*- coding: gb18030 -*-
#
# $Id: Spell_HP.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

import Const
from SpellBase import *
from Spell_Magic import Spell_Magic


class Spell_HP( Spell_Magic ):
	"""
	治疗，不走法术完整流程，直接获得配置中的治疗效果的技能大类
	技能加血量=X%角色法力值上限+固定Y点
	
	param1为固定的y值
	param2为法力上限比例，如10则表示10%
	"""
	def __init__( self ):
		"""
		"""
		Spell_Magic.__init__( self )
		self._p1 = 0
		
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		self._p1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 	
		self._p2 = int( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 ) / 100.0
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		cureHP = int( caster.MP_Max * self._p2 + self._p1 )
		changeHP = receiver.addHP( cureHP )
		caster.doCasterOnCure( receiver, changeHP )		# 治疗目标时触发
		receiver.doReceiverOnCure( caster, changeHP )   	# 被治疗时触发
		
		#增加目标是玩家还是宠物或者其他的判断 add by wuxo 2012-5-17
		if caster.getEntityType() == csdefine.ENTITY_TYPE_ROLE:
			caster.client.onAddRoleHP( receiver.id, cureHP )
			#KILL_HP_TARGET_CURE %s的%s恢复了你%i点生命值。
			#SKILL_TARGET_HP_CURE  你的%s恢复了%s%i点生命值。
			#SKILL_HP_CURE     你的%s恢复了你%i点生命值。
			if receiver.isEntityType(csdefine.ENTITY_TYPE_ROLE):#接受者是玩家
				if caster.id != receiver.id: #给别人加血
					#你的%s恢复了%s%i点生命值。
					caster.statusMessage( csstatus.SKILL_TARGET_HP_CURE, self.getName(), receiver.getName(), cureHP )
					#%s的%s恢复了你%i点生命值。
					receiver.statusMessage( csstatus.SKILL_HP_TARGET_CURE, caster.getName(), self.getName(), cureHP )
				else: #给自己加血
					#你的%s恢复了你%i点生命值。
					caster.statusMessage( csstatus.SKILL_HP_CURE, self.getName(), cureHP )
			elif receiver.isEntityType(csdefine.ENTITY_TYPE_PET): #接受者是宠物
				#SKILL_HP_CURE_PET  你的%s为你的宠物恢复了%i点生命值。
				#SKILL_HP_TARGET_CURE_PET %s的%s为你的宠物恢复了%i点生命值。
				#SKILL_HP_CURE_TARGET_PET  (CB):你的%s为%s的宠物恢复了%i点生命值。
				petOwner = receiver.getOwner().entity
				if petOwner.id == caster.id: #给自己的宠物加血
					#你的%s为你的宠物恢复了%i点生命值。
					caster.statusMessage( csstatus.SKILL_HP_CURE_PET, self.getName(), cureHP )
				else:#给别人的宠物加血
					#你的%s为%s的宠物恢复了%i点生命值。
					caster.statusMessage( csstatus.SKILL_HP_CURE_TARGET_PET, self.getName(), petOwner.getName(), cureHP )
					#%s的%s为你的宠物恢复了%i点生命值。
					receiver.statusMessage( csstatus.SKILL_HP_TARGET_CURE_PET, caster.getName(), self.getName(), cureHP )
		
		
		
		
	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		法术抵达目标通告。在默认情况下，此处执行可受术人员的获取，然后调用receive()方法进行对每个可受术者进行处理。
		注：此接口为旧版中的receiveSpell()

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		
		继承来去除对于广范围攻击目标的处理，以避免加血变开战的问题 by 姜毅
		"""
		# 获取所有受术者
		receivers = self.getReceivers( caster, target )
		# 不管有没有击中目标，不管攻击几个目标，攻击几次
		for receiver in receivers:
			# 设置战斗计算模版参数字典,该模版字典的值有可能被其他BUFF技能改变而影响战斗数值
			# 法术接收之前所做的工作
			self.onReceiveBefore_( caster, receiver )
			if receiver.state != csdefine.ENTITY_STATE_DEAD:
				self.receive( caster, receiver )
			# 对接收者而言，不管技能是否命中，不管技能攻击几次
			# 添加仇恨
			self.receiveEnemy( caster, receiver )
			# 在recevei之后可能角色已经死亡了
			if caster.isDestroyed:
				return


		if not caster.isDestroyed:
			caster.onSkillArrive( self, receivers )
		
#$Log: not supported by cvs2svn $
#
#