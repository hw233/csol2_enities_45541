# -*- coding: gb18030 -*-
"""
ģ����ֽ����ģ����ֽ��ʹ��ʱ����
"""
import csstatus
import csdefine
import csconst
import Math
import math
import random
import BigWorld
from Spell_Item import Spell_Item
from ObjectScripts.GameObjectFactory import g_objFactory
from bwdebug import *

class Spell_322398001( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self._monsterIDs = ( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else "" ) .split('|')		# Ҫ���ɵĵ����������ID��className��
		self._monsterDropItemID = int( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 ) 				# ���ɵĹ��ｫ��������Ʒ

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		#----����ƫ����---- #
		rad = math.pi * 2.0 * random.random()
		pos = Math.Vector3( caster.position )
		distance = 2 + 2 * random.random()
		pos.x += distance * math.sin( rad )
		pos.z += distance * math.cos( rad )
		index = random.randint( 0, len( self._monsterIDs ) - 1 )
		( x, y, z ) = pos
		collide = BigWorld.collide( caster.spaceID, ( x, y + 2, z ), ( x, y - 2, z ) )
		if collide != None:
			y = collide[0].y
		pos = ( x, y, z )
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		level = item.query('level')

		newEntity = caster.createObjectNearPlanes( self._monsterIDs[index], pos, caster.direction, { "spawnPos" : tuple( pos ), "level":level } )
		if newEntity.isEntityType( csdefine.ENTITY_TYPE_TREASURE_MONSTER ):
			newEntity.setOwner( caster )					# ����Ȩ����������
			newEntity.setTemp( "dropItem", self._monsterDropItemID )# ���õ������Ʒ���˹ֱص�һ���ر�ͼ
		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "cannot find the item form uid[%s] ." % uid )
			return

		treasureSpace = item.query( "treasure_space", "" )		# ȡ��ģ����ֽ���еĵ�ͼ��Ϣ
		treasurePosStr = item.query( "treasure_position", None )# ȡ��ģ����ֽ���е�������Ϣ
		treasurePosArr = treasurePosStr.split(',')
		treasurePos = ( int( treasurePosArr[0] ), int(treasurePosArr[1]) )
		if treasureSpace == "" or treasurePos == None:
			# ���ûȡ������˵������û��������Щ��Ϣ����ͼ��Ϣ��������Ϣ�Ǳ���Ҫ�еģ��������ɳ��������������ɵ�
			ERROR_MSG( "Your treasure paper has lost location messages!" )
			return csstatus.SKILL_CANT_CAST
		self._treatureLevel = int( item.getLevel() )	# �����洢��ͼ����
		if not self.isTreasurePosValid( caster, treasureSpace, treasurePos, 5 ):
			# ������ڶ�Ӧ������λ�ø��������ڱ�
			return csstatus.SKILL_TREASURE_POS_NOT_VALID
		return Spell_Item.useableCheck( self, caster, target)

	def isTreasurePosValid( self, player, spaceName, position, offset ):
		"""
		�������ڱ�λ���Ƿ�Ϸ����Ƿ���ĳ����ͼspaceName������position��Χ�ڣ�
		@param 	player		:	���������
		@type 	player		:	Role
		@param 	spaceName	:	��ͼ��
		@type 	spaceName	:	STRING
		@param 	position	:	��ά����λ��
		@type 	position	:	Tuple
		@param 	offset		:	����ķ�Χ��࣬����Ϊ��ֵ
		@type 	offset		:	Tuple
		"""
		if player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) != spaceName:
			return False
		negativeOffset = 0 - offset
		currPos = player.position
		x = float(currPos[0]) - float(position[0])
		z = float(currPos[2]) - float(position[1])
		return ( x >= negativeOffset and x <= offset and z >= negativeOffset and z <= offset )