# -*- coding: gb18030 -*-


import BigWorld
import Math
import random
import math
import csstatus
import csconst
import utils

from Spell_Item import Spell_Item
from bwdebug import *
from ObjectScripts.GameObjectFactory import g_objFactory

class Spell_Item_Create_Monster( Spell_Item ):
	"""
	ͨ����Ʒ����һ��Monster
	"""
	def init( self, dict ):
		"""
		��ʼ��
		"""
		Spell_Item.init( self, dict )
		self.npcClassName = str( dict[ "param1" ] )										# className
		self.spaceName = str( dict[ "param2" ] )								# ָ���ĵ�ͼ���֣����磺feng_ming
		self.radius = int( dict["param3"] )												# �����ٻ�����İ뾶��������ٻ�λ�ö��Χ���ٻ�
		self.lifeTime = int( dict["param4"] )											# �ٻ��ֵĴ��ʱ��
		self.canCallPositions = dict[ "param5" ].split( "|" )
		self.position = ( 0, 0 ,0 )
		
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
		positionZ = int(caster.position.z)
		flag = 0
		for assignPosition in self.canCallPositions:
			if assignPosition:
				pos = utils.vector3TypeConvert( assignPosition )
				assignPositionX = pos[0]
				assignPositionZ = pos[2]
				if assignPositionX and assignPositionZ and positionX in xrange( assignPositionX - self.radius, assignPositionX + self.radius ) \
				and positionZ in xrange( assignPositionZ - self.radius, assignPositionZ + self.radius ):
					flag = 1
					self.position = tuple( pos )
					break
		if not flag:
			return False
		return Spell_Item.useableCheck( self, caster, target )


	def cast( self, caster, target ):
		"""
		"""
		Spell_Item.cast( self, caster, target )
		newEntity = caster.createObjectNearPlanes( self.npcClassName, self.position, caster.direction, { "spawnPos": self.position, "lifetime" : self.lifeTime } )
		newEntity.firstBruise = 1		# ����Monster�е�һ�����˺���bootyOwner����
		
		teamMailbox = caster.getTeamMailbox()
		if teamMailbox is not None:										# �������ж���
			teamID = caster.getTeamMailbox().id
			bootyOwners = newEntity.searchTeamMember( teamID, Const.TEAM_GAIN_EXP_RANGE )
			newEntity.bootyOwner = ( 0, teamID )						# ���ö���Ϊnpc��ս��Ʒӵ����
			if len( bootyOwners ) == 0:
				newEntity.bootyOwner = ( 0, 0 )
		else:
			newEntity.bootyOwner = ( caster.id, 0 )
		newEntity.setTemp( "bootyOwner", newEntity.bootyOwner )
