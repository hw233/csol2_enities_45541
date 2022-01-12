# -*- coding:gb18030 -*-

from SpellBase import Spell
from bwdebug import *
import random
import Math
import math
import csarithmetic

class Spell_CatchEntity( Spell ):
	"""
	NPC技能，冰爪（抓取玩家到施法者所在位置）
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		self.offYaw = 0.0
		self.radius = []
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		if dict["param1"] != "":
			self.offYaw = float( dict["param1"] )
		if dict["param2"] != "":
			self.radius = [ float(i) for i in dict["param2"].split(";") ]
			self.radius.sort()

	def receive( self, caster, receiver ):
		offsetYaw = 0.0
		dis = 0.0
		if self.offYaw > 0.0:
			offsetYaw = random.uniform( 0.0 - self.offYaw, self.offYaw )
		if len(self.radius) == 2:
			dis = random.uniform( self.radius[0], self.radius[1] )
		
		yaw = caster.yaw + offsetYaw
		direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
		dstPos = caster.position + direction * dis
		endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
		endDstPos = csarithmetic.getCollidePoint( caster.spaceID, Math.Vector3( endDstPos[0],endDstPos[1]+3,endDstPos[2]), Math.Vector3( endDstPos[0],endDstPos[1]-3,endDstPos[2]) )
		
		receiver.position = endDstPos
		self.receiveLinkBuff( caster, receiver )
	