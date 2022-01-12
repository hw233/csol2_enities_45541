# -*- coding: gb18030 -*-

"""
�ٻ�entity, ��BASE������߿��һ�
"""
import BigWorld
import Math
import random
import math

import csdefine
import csstatus
import csconst
from bwdebug import *

import Const
from Spell_Magic import Spell_Magic
from Spell_Item import Spell_Item

class CallEntityBase:
	def __init__( self ):
		self.lifeTime = 0
		self.radius = 0
		self.spaceEnable = []
		self.waitOwnerInWorld = 0
	
	def receive( self, caster, target ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		dict = self._getEntityDict( caster, target, {} )
		for edata in self.callList:
			eid, enum = edata.split( ":" )
			for i in xrange( eval( enum ) ):
				caster.callEntity( eid, dict, self._getCallPosition( caster ), caster.direction )
		
	def _getEntityDict( self, caster, target, params ):
		# ȡ��entity����
		dict = {}
		dict[ "level" ] = caster.level
		dict[ "lifetime" ] = self.lifeTime
		dict[ "spaceEnable" ] = self.spaceEnable
		dict[ "waitOwnerInWorld" ] = self.waitOwnerInWorld
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

class Spell_CallEntity( Spell_Magic, CallEntityBase ):
	"""
	�ٻ�entity
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Magic.__init__( self )
		CallEntityBase.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		# ���ݸ�ʽ: 30000001:2 | 30000002:3... 
		self.callList = dict[ "param1" ].split( "|" )

		self.lifeTime = int( dict[ "param2" ] )											 #�ٻ�ʱ��
		self.radius = int( dict["param3"] )												 #�ٻ��뾶
		self.spaceEnable = [ int( i ) for i in dict["param4"].split( ";" ) ] if len( dict["param4"] ) else [] 	#�ٻ�����ĵ�ͼ��Ч��
		self.waitOwnerInWorld = int( dict["param5"] )									 #�ٻ��������������ߵ�ʱ��᲻����ʧ
	
	def receive( self, caster, target ):
		# ����������Ҫ��������
		Spell_Magic.cast( self, caster, target )
		CallEntityBase.receive( self, caster, target )

class Spell_CallEntityUseMagicDamage( Spell_CallEntity ):
	# �ٻ�entity�ķ�����������ӳ����˵ķ���������
	def __init__( self ):
		Spell_CallEntity.__init__( self )
	
	def _getEntityDict( self, caster, target, params ):
		dict = Spell_CallEntity._getEntityDict( self, caster, target, params )
		dict[ "magic_damage_value" ] = caster.magic_damage
		return dict

class Spell_CallEntityForItem( Spell_Item, CallEntityBase ):
	# �ٻ�Entity��������Ʒ
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )
		CallEntityBase.__init__( self )
	
	def init( self, dict ):
		# ��ʼ��
		Spell_Item.init( self, dict )
		self.callList = dict[ "param1" ].split( "|" )
		self.lifeTime = int( dict[ "param2" ] )											 #�ٻ�ʱ��
		self.radius = int( dict["param3"] )												 #�ٻ��뾶
		self.spaceEnable = [ int( i ) for i in dict["param4"].split( ";" ) ] if len( dict["param4"] ) else [] 	#�ٻ�����ĵ�ͼ��Ч��
		self.waitOwnerInWorld = int( dict["param5"] )	
	
	def receive( self, caster, target ):
		# ����������Ҫ��������
		CallEntityBase.receive( self, caster, target )

class Spell_CallEntityForItemToOwner( Spell_Item, CallEntityBase ):
	# ���˶Դ�������ʹ�õ��ߣ��ٻ����µĹ���
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )
		CallEntityBase.__init__( self )
		self.hp_less = 0
		self.range_max = 0
		self.range = 0
		self.monsterNo = ""
	
	def init( self, dict ):
		# ��ʼ��
		Spell_Item.init( self, dict )
		callInfos, self.monsterNo = dict[ "param1" ].split( "|" )
		self.callList = [ callInfos, ]
		self.lifeTime = int( dict[ "param2" ] )											 #�ٻ�ʱ��
		self.radius, self.range, self.range_max = [ int(i) for i in dict["param3"].split( "|" ) ]	 #�ٻ��뾶
		self.hp_less = int( dict[ "param4" ] )		
		self.waitOwnerInWorld = int( dict["param5"] )
		
	def useableCheck( self, caster, target ):
		# У�鼼���Ƿ����ʹ�á�
		targetEntity = target.getObject()
		if not targetEntity:
			return 
			
		if self.monsterNo != targetEntity.className:
			caster.statusMessage( csstatus.SKILL_CANT_CAST_ENTITY )
			return False
			
		if caster.id != targetEntity.bootyOwner[0] or caster.getTeamMailbox() and caster.getTeamMailbox().id != targetEntity.bootyOwner[1] :
			caster.statusMessage( csstatus.SKILL_SPELL_NOT_OWNER )
			return False
		
		if targetEntity.HP >= targetEntity.HP_Max * self.hp_less / 100:
			caster.statusMessage( csstatus.SKILL_SPELL_HP_CONDITION, self.hp_less )
			return False
		
		if self.range_max > 0:
			rangeEntities = caster.entitiesInRangeExt( self.range, None, targetEntity.position )
			callClassName = self.callList[ 0 ].split( ":" )[ 1 ]
			call_uname = ""
			rangeNum = 0
			for e in rangeEntities:
				if e.className == callClassName:
					call_uname = e.uname
					rangeNum += 1
			
			if rangeNum >= self.range_max:
				caster.statusMessage( csstatus.SKILL_SPELL_ALREADY_HAS_ENTITY, self.range_max, call_uname )
				return False
				
		return Spell_Item.useableCheck( self, caster, target )
		
	def receive( self, caster, target ):
		# ����������Ҫ��������
		Spell_Item.receive( self, caster, target )
		CallEntityBase.receive( self, caster, target )
