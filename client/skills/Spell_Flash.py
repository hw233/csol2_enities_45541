# -*- coding: gb18030 -*-
#
#edit by wuxo 2013-9-11


"""
闪现脚本
"""

from SpellBase import Spell
import BigWorld
import Math
import math
import csdefine
import csarithmetic
import random

class Spell_Flash( Spell ):
	"""
	闪现脚本
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		#施法者朝向夹角
		self.offsetY = 0.0
		#闪现距离范围
		self.disRange  = None
	
	def init( self, data ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, data )
		if data["param1"] != "":
			self.offsetY = float( data["param1"] ) * math.pi / 360.0
		if data["param2"] != "":
			self.disRange = [ float(i) for i in data["param2"].split(";") ]
			self.disRange.sort()
	
	def cast( self, caster, targetObject ):
		"""
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell.cast( self, caster, targetObject )
		player = BigWorld.player()
		target = targetObject.getObject()
		if target == player:
			offsetYaw = 0.0
			dis = 0.0
			if self.offsetY > 0.0:
				offsetYaw = random.uniform( 0.0 - self.offsetY, self.offsetY )
			if len(self.disRange) == 2:
				dis = random.uniform( self.disRange[0], self.disRange[1] )
			
			yaw = player.yaw + offsetYaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			dstPos = player.position + direction * dis
			endDstPos = csarithmetic.getCollidePoint( player.spaceID, player.position, dstPos )
			endDstPos = csarithmetic.getCollidePoint( player.spaceID, Math.Vector3( endDstPos[0],endDstPos[1]+3,endDstPos[2]), Math.Vector3( endDstPos[0],endDstPos[1]-3,endDstPos[2]) )
			player.cell.requestFlash( endDstPos )
	
