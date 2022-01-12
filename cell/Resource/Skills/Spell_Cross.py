# -*- coding: gb18030 -*-

# 系统技能，生成一个AreaRestrictTransducer的entity(陷阱功能entity)，在施放者位置

import BigWorld
import Math
import csdefine
import csstatus
from Spell_PhysSkillImprove import Spell_PhysSkillImprove 

class AreaCross( object ):
	def __init__( self, dictDat ):
		self.width = dictDat["value1"] / 2
		self.length = dictDat["value2"] / 2
	
	def inArea( self, spos, yaw, tpos ):
		"""
		判断是否在区域内。
		"""
		m1 = Math.Matrix()
		m2 = Math.Matrix()
		m1.setRotateY( - yaw )
		m2.setRotateY( - ( yaw + 3.14 / 2 ) )
		v = tpos - spos
		mv1 = m1.applyPoint(v)
		mv2 = m2.applyPoint(v)

		if abs( mv1[0] ) <= self.width and abs( mv1[2] ) <= self.length or abs( mv2[0] ) <= self.width and abs( mv2[2] ) <= self.length:
			return True

		return False
	
	def getObjectList( self, caster, target ):
		return [ e for e in caster.entitiesInRangeExt( self.length, None, target.getObjectPosition() ) if self.inArea( target.getObjectPosition(), target.convertReference( caster ).yaw, e.position ) ]

class Spell_Cross( Spell_PhysSkillImprove ):
	def __init__( self ):
		Spell_PhysSkillImprove.__init__( self )
	
	def init( self, dictDat ):
		Spell_PhysSkillImprove.init( self, dictDat )
		val = dictDat[ "ReceiverCondition" ]
		self._receiverObject._area = AreaCross( val )
