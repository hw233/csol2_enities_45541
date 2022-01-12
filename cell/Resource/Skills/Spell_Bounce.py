# -*- coding:gb18030 -*-
import math
from Spell_BuffNormal import Spell_BuffNormal
MAX_SPEED = 100.0

class Spell_Bounce( Spell_BuffNormal ):
	"""
	建筑物创建时 需要将玩家弹开
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )

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
		self.onArrive( caster, target )

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
		for receiver in receivers:
			#法术到达时发生的一些事情
			self.receive( caster, receiver )
	
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if receiver.isDestroyed:
			return
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		self.receiveLinkBuff( caster, receiver )
		receiver.move_speed = MAX_SPEED
		receiver.receiveSpell( caster.id, self.getID(), 0, 0, 0 )
	
	def getReceivers( self, caster, target ):
		"""
		virtual method
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity
		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		s1 = caster.getBoundingBox().z / 2
		s2 = caster.getBoundingBox().x / 2
		radius = math.sqrt( s1*s1 + s2*s2 )
		return caster.entitiesInRangeExt( radius, "Role", caster.position )
