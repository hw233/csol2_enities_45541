# -*- coding:gb18030 -*-

import Math
import math
import csdefine
import csarithmetic
import random
from Spell_BuffNormal import Spell_BuffNormal

class Spell_Flash( Spell_BuffNormal ):
	"""
	���ּ���
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )
		#ʩ���߳���н�
		self.offsetY = 0.0
		#���־��뷶Χ
		self.disRange  = None

	def init( self, data ):
		"""
		"""
		Spell_BuffNormal.init( self, data )
		if data["param1"] != "":
			self.offsetY = float( data["param1"] ) * math.pi / 360.0
		if data["param2"] != "":
			self.disRange = [ float(i) for i in data["param2"].split(";") ]
			self.disRange.sort()
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if receiver.isDestroyed:
			return
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		self.receiveLinkBuff( caster, receiver )
		
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE  ):
			caster.setTemp( "SPELL_FLASH", self.disRange[1] )
		else:
			offsetYaw = 0.0
			dis = 0.0
			if self.offsetY > 0.0:
				offsetYaw = random.uniform( 0.0 - self.offsetY, self.offsetY )
			if len(self.disRange) == 2:
				dis = random.uniform( self.disRange[0], self.disRange[1] )
			
			yaw = caster.yaw + offsetYaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			dstPos = caster.position + direction * dis
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, Math.Vector3( endDstPos[0],endDstPos[1]+3,endDstPos[2]), Math.Vector3( endDstPos[0],endDstPos[1]-3,endDstPos[2]) )
			caster.openVolatileInfo()
			caster.position = endDstPos