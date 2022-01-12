# -*- coding: gb18030 -*-

#作用效果移动类技能
#允许配置作用生效次数（击中一次后消失还是连续作用）；
#允许配置技能释放角度（以当前目标为基准，与引导技能配合使用）
#edit by wuxo 2012-3-20

import math
import Math
import utils
import csdefine
import csstatus

import SkillTargetObjImpl
from SpellBase import *
from Spell_CastTotem import Spell_CastTotem



class Spell_MoveEffect( Spell ):
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		self._target = None
		self._direction = None
		self._isOnce = None 	#是否是一次性伤害技能,碰到第一个目标就爆破，然后技能结束
		self._offsetYaw = 0
		self.skillID = 0
		self.lastPosition = (0,0,0)
		self.everyDis = 0
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.skillID = int( dict[ "param1" ] )
		if dict[ "param2" ] != "":
			self._offsetYaw = float( dict[ "param2" ] )
		else:
			self._offsetYaw = 0.0
		self._isOnce = bool( int( dict[ "param3" ] ) )
		self.everyDis = dict["ReceiverCondition"]["value2"]
		
		
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
		
		#以下计算朝向
		postion = target.getObjectPosition()
		if caster.position.flatDistTo( postion ) > 0.0:
			y = utils.yawFromPos( caster.position, postion )
			
		else:
			y = caster.yaw
			
		y += self._offsetYaw
		self._direction = Math.Vector3( math.sin(y), 0, math.cos(y) )
		self._direction.normalise()
		
		dPos = caster.position + self._direction * self._rangeMax
		
		self._target = SkillTargetObjImpl.createTargetObjPosition(dPos)
			
		return csstatus.SKILL_GO_ON
		
		
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
		Spell.use( self, caster, self._target )	
		
		
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
		target = self._target
		# 引导技能检测
		caster.delHomingOnCast( self )
		self.setCooldownInIntonateOver( caster )
		# 处理消耗
		self.doRequire_( caster )
		#通知所有客户端播放动作/做其他事情
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )
		
		# 法术施放完毕通知，不一定能打中人哦(是否能打中已经和施法没任何关系了)！
		# 如果是channel法术(未实现)，只有等法术结束后才能调用
		self.onSkillCastOver_( caster, target )
		
		self.lastPosition = caster.position + self._direction*self._rangeMax
		t0 = self.everyDis/self._speed
		n = self._rangeMax / self.everyDis
		n = int( math.ceil(n) )
		for i in range( 1, n + 1 ):
			delay = (i - 1) * t0
				
			dPos = caster.position + self._direction * delay * self._speed
			target0 = SkillTargetObjImpl.createTargetObjPosition(dPos)
			
			if delay <= 0.1:
				# 瞬发
				caster.addCastQueue( self, target0, 0.1 )
			else:
				# 延迟
				caster.addCastQueue( self, target0, delay )
		caster.setTemp( "MOVE_EFFECT_DIS", self._rangeMax )
		
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
		# 获取所有受术者
		receivers = self.getReceivers( caster, target )
		if (target.getObjectPosition() - self.lastPosition).length < 0.1:
			caster.removeTemp( "MOVE_EFFECT_DIS" )
		for e in receivers:
			caster.spellTarget( self.skillID , e.id )
			if self._isOnce:
				caster.cancelSpellMoveEffect( caster.id, self.getID() )
		
		
		