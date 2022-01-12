# -*- coding: gb18030 -*-


import BigWorld
import Math
import random
import math
import csstatus
import csconst

from Spell_Item import Spell_Item
from bwdebug import *

class Spell_Item_Create_NPC( Spell_Item ):
	"""
	ͨ����Ʒ����һ��NPC
	"""
	def init( self, dict ):
		"""
		��ʼ��
		"""
		Spell_Item.init( self, dict )
		self.npcClassName = str( dict[ "param1" ] )										# className
		self.spaceNameXY = dict[ "param2" ].split( "|" )								# ָ���ĵ�ͼ����|����|���ٻ��߿ɼ������磺feng_ming|210:-35
		self.radius = int( dict["param3"] )												# �ٻ��뾶
		self.lifeTime = int( dict["param4"] )											# �ٻ��ֵĴ��ʱ��
		self.spaceName = str(self.spaceNameXY[0])
		self.positions = self.spaceNameXY[1]
		if self.positions != "0":
			self.X = int(self.positions.split(":")[0])
			self.Y = int(self.positions.split(":")[1])
		
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
		

	def useableCheck( self, caster, target ):
		"""
		У�鼼���Ƿ����ʹ�á�
		"""
		if caster.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) != self.spaceName:		# ָ����ͼ
			caster.statusMessage( csstatus.SKILL_SPELL_NOT_SPACENNAME )
			return False
		
		positionX = int(caster.position.x)
		positionY = int(caster.position.z)
		if self.positions != "0" and (positionX not in  xrange( self.X-20, self.X+20 ) or positionY not in  xrange( self.Y-20, self.Y+20 )):		# ָ��������Χ20����
			caster.statusMessage( csstatus.SKILL_SPELL_NOT_POSITION )
			return False
		rangeEntities = caster.entitiesInRangeExt( 50, None, caster.position )
		for e in rangeEntities:			# ������Χ50�׷�Χ�ڣ���������ٻ��˸�npc�Ͳ������ٻ���
				if e.className == self.npcClassName:
					caster.statusMessage( csstatus.SKILL_SPELL_SOMEONE_USING, e.getName() )
					return False
		return Spell_Item.useableCheck( self, caster, target )


	def cast( self, caster, target ):
		"""
		"""
		Spell_Item.cast( self, caster, target )
		newEntity = caster.createObjectNearPlanes( self.npcClassName, self._getCallPosition( caster ), caster.direction, { "lifetime" : self.lifeTime } )
		newEntity.setTemp( "npc_ownerBase", caster.base )				# ����ʩ����Ϊ��ǰNPC������ӵ����