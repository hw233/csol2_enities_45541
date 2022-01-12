# -*- coding: gb18030 -*-

# 系统对某个目标施放的技能，可以认为没有源目标，也可以认为源目标就是系统。

from Spell import Spell
import csstatus
import csdefine


# --------------------------------------------------------------------
# 凡是继承此类的技能都是由系统施放的技能，所有接口中的条件判断都不会和
# 施法者有任何关系，默认为没有施法者。
# --------------------------------------------------------------------
class SystemSpell( Spell ) :

	def __init__( self ) :
		Spell.__init__( self )


	# ----------------------------------------------------------------
	# virtual methods
	# ----------------------------------------------------------------
	def useableCheck( self, caster, target ) :
		"""
		virtual method
		由于是系统施放的技能，因此不会对施法者作任何判断
		可以认为系统对某个目标施放的技能是不可抗拒的。
		"""
		return csstatus.SKILL_GO_ON

	def use( self, caster, target ) :
		"""
		virtual method
		没有吟唱，冷却这些动作
		"""
		self.cast( caster, target )

	def cast( self, caster, target ) :
		"""
		virtual method
		系统施放，没有吟唱体，所以都是瞬发
		"""
		self.onArrive( caster, target )

	def onArrive( self, caster, target ) :
		"""
		virtual method
		法术到达后，获取受术者，系统技能是有受术目标的，
		因此要作一些必要判断
		"""
		receivers = self.getReceivers( caster, target )
		for receiver in receivers:
			receiver.clearBuff( self._triggerBuffInterruptCode )
			self.receive( caster, receiver )

	def getReceivers( self, caster, target ) :
		"""
		virtual method
		默认只对受术目标施放。
		"""
		receivers = []
		targetEntity = target.getObject()
		if not targetEntity.isDestroyed and ( \
		targetEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or \
		targetEntity.isEntityType( csdefine.ENTITY_TYPE_PET ) ):
			receivers.append( targetEntity )
		return receivers