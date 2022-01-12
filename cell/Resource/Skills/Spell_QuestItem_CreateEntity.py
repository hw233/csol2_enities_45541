# -*- coding: gb18030 -*-
"""
��һ������ʹ��һ����Ʒ���ٻ���һ���µĹ���
"""

import BigWorld
from bwdebug import *
from Spell_Item import Spell_Item
import csstatus
import re
import Math
import random

class Spell_QuestItem_CreateEntity( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )
		self._position = ""
		self._direction = ""

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self._isDestroy = int( dict["param1"] )				# �Ƿ�����������
		self._spellClassName = str( dict["param2"] )		# ������ID
		self._newClassName = str( dict["param3"] )			# �ٻ�������ID
		posAndDir = eval( re.sub( "\s*;\s*|\s+", ",", dict[ "param4" ] ) ) if dict[ "param4" ] else 0 		# �ٻ������λ�úͳ���
		if posAndDir:
			self._position,self._direction = posAndDir[:3],posAndDir[3:]	

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		Spell_Item.receive( self, caster, receiver )
		pos = Math.Vector3( receiver.position )
		direction = Math.Vector3( receiver.direction )

		pos.x = pos.x + random.random() * random.randint( -3, 3 )
		pos.z = pos.z + random.random() * random.randint( -3, 3 )

		if self._position:
			pos = Math.Vector3( self._position )
		if self._direction:
			direction = self._direction

		dict = {}
		dict[ "level" ] = caster.level
		dict[ "spawnPos" ] = tuple( pos )
		
		entity = receiver.createObjectNearPlanes( self._newClassName, pos, direction, dict )
			
		if self._isDestroy == 1:
			receiver.destroy()

	def useableCheck( self, caster, target ):
		if target.getObject().className != self._spellClassName:
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET
		
		return Spell_Item.useableCheck( self, caster, target )