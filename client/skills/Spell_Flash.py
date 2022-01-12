# -*- coding: gb18030 -*-
#
#edit by wuxo 2013-9-11


"""
���ֽű�
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
	���ֽű�
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		#ʩ���߳���н�
		self.offsetY = 0.0
		#���־��뷶Χ
		self.disRange  = None
	
	def init( self, data ):
		"""
		��ȡ��������
		@param dict: ��������
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
		���ż�������������Ч����
		@param caster:			ʩ����Entity
		@type caster:			Entity
		@param targetObject: ʩչ����
		@type  targetObject: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
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
	
