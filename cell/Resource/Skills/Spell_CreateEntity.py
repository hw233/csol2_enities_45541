# -*- coding: gb18030 -*-
"""
�ٻ�entity, ֻ��cell���ֵĹ���, ��ʩ���߸�������
"""

import random

import BigWorld
import math
import Math

from SpellBase import *

class Spell_CreateEntity( Spell ):
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		self.callList = []										 #�ٻ�ʱ��
		self.radius = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.callList = dict[ "param1" ].split( "|" )
		self.radius = int( dict["param2"] )	
	
	def receive( self, caster, target ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		dict = self._getEntityDict( caster, target, {} )
		for edata in self.callList:
			eid, enum = edata.split( ":" )
			for i in xrange( eval( enum ) ):
				caster.createObjectNear( eid, self._getCallPosition( caster ), caster.direction, dict )
	
	def _getEntityDict( self, caster, target, params ):
		# ȡ��entity����
		dict = {}
		dict[ "level" ] = caster.level
		return dict
		
	def _getCallPosition( self, caster ):
		# ȡ��entity��λ��
		newPos = Math.Vector3()
		if self.radius > 0:		
			castPos = caster.position
			newPos.x = castPos.x + random.randint( -self.radius, self.radius )
			newPos.z = castPos.z + random.randint( -self.radius, self.radius )
			newPos.y = castPos.y
			
			result = BigWorld.collide( caster.spaceID, ( newPos.x, newPos.y + 2, newPos.z ), ( newPos.x, newPos.y - 1, newPos.z ) )
			if result != None:
				newPos.y = result[0].y
		else:
			newPos = caster.position
	
		return newPos