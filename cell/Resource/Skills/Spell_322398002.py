# -*- coding: gb18030 -*-
"""
�ر�ͼʹ��ʱ����
"""

from Spell_Item import Spell_Item
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *
from csconst import g_maps_info
from Love3 import g_TreasurePositions
import csstatus
import csdefine
import Math
import math
import random
import csconst
import BigWorld
import sys
from VehicleHelper import getCurrVehicleID

class Spell_322398002( Spell_Item ):
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
		self._monsterIDs = ( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else "" ) .split( '|' )		# Ҫ���ɵĹ����ID��className�����������������磺11111111,11111112,11111113|22222221,22222222,22222223��
																		# ���ұ��밴��˳�򣺵�����1���͵Ĳ�ͬID|������2���͵Ĳ�ͬID
		self._reqItemID = int( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 ) 						# ��Ҫ����ͨ��Ʒ�����£�
		self._goldScoop = int( dict[ "param3" ] if len( dict[ "param3" ] ) > 0 else 0 ) 						# ����ID(ӵ�к�����Ʒ��һ����õ�����)
		self._rewardItems = ( dict[ "param4" ] if len( dict[ "param4" ] ) > 0 else "" ) .split( '|' )		# �õ�����Ʒid���籦�䣩
		self._situations = ( dict[ "param5" ] if len( dict[ "param5" ] ) > 0 else "" ) .split('|')		# ��ͬ����ĸ���(�磺70|20|10������������Ϊ100)
		self._treatureLevel = 1											# �ر�ͼ�ļ��𣨼�������˱��صص㣩
		if len( self._monsterIDs ) != 2:
			ERROR_MSG( "Length of Monster array must be exactly 2! skillID: %s" % self.getID() )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		rateArr = self._situations[self.getSituIndex()].split( ',' )
		if len( rateArr ) != 3:
			ERROR_MSG( "Situation rates lost!" )
			return
		start = 0
		node1 = int( rateArr[0] )
		node2 = node1 + int( rateArr[1] )
		node3 = node2 + int( rateArr[2] )
		item = caster.findItemFromNKCK_( self._goldScoop )	# �ж��Ƿ������н���
		if item:
			# ����н��£���node1=100����ʾnode1��100%������Ҳ����100%�����ɱ���
			node1 = 100
		else:
			# ���û�н��£�Ҫ�ҵ����ϵ����£�Ȼ���Ƴ�������
			item = caster.findItemFromNKCK_( self._reqItemID )
		caster.removeItem_( item.order, 1, csdefine.DELETE_ITEM_DIGTREASURE )	# �Ƴ�������
		situCode = random.randint( 0, 100 )	# ��0-100���漴һ������
		treasureBoxID = int( self._rewardItems[ self.getRewardIndex() ] )	# �õ��ı���ID
		if situCode >= start and situCode < node1:
			# �п���ֱ���ڵ����䣬������Ұ�����
			item = caster.createDynamicItem( treasureBoxID )
			item.set( "level", self._treatureLevel )
			item.set( "aType", csdefine.ACTIVITY_CANG_BAO_TU )
			caster.addItem( item, csdefine.ADD_ITEM_TREASUREMAP )
			caster.statusMessage( csstatus.SKILL_TREASURE_GET_BAOXIANG )
		elif situCode >= node1 and situCode < node2:
			# �п���ֱ����ԭ��ˢ��һ�������������
			monsters = self._monsterIDs[0].split( ',' )
			m_index = random.randint( 0, len( monsters ) - 1 )
			monsterClassName = monsters[m_index]
			mons1 = self.spawnMonsterOnOrigin( monsterClassName, caster, treasureBoxID )
			m_index = random.randint( 0, len( monsters ) - 1 )
			monsterClassName = monsters[m_index]
			mons2 = self.spawnMonsterOnOrigin( monsterClassName, caster, treasureBoxID )
			mons2.say( cschannel_msgs.CELL_SPELL_322398002_1 )
			caster.statusMessage( csstatus.SKILL_TREASURE_GET_MONSTER )
		elif situCode >= node2 and situCode <= node3:
			# �п�����Ұ�����ˢ��һ������������
			# �㷨��û����ͬFuncTreasureMap��������ɱ��صص��㷨Ӧ����ͬ
			uid = caster.queryTemp( "item_using" )
			item = caster.getByUid( uid )
			if item is None:
				ERROR_MSG( "cannot find the item form uid[%s]." % uid )
				return
			treasureLvl = item.getLevel()
			spaceName = caster.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )	# ��õ�ǰspaceName
			levelList = g_TreasurePositions.getTreasureLevelPointsBySpace( spaceName )
			levelList.sort()
			l_index = 0
			if treasureLvl in levelList:
				l_index = levelList.index( treasureLvl )
			positions = []
			while len( positions ) < 3:
				level = self._treatureLevel
				levelIndex = random.randint( 0, l_index )
				if len( levelList ) > levelIndex:
					level = levelList[ levelIndex ]
				monsPos = item.genTreaturePosition( spaceName, level )
				loopTime = 0
				while monsPos in positions and loopTime <= 2000:
					# ѭ��2000�λ��Ҳ������ʵ����꣬������ѭ��������������ѭ��
					monsPos = item.genTreaturePosition( spaceName )
					loopTime += 1
				positions.append( monsPos )
				monsters = self._monsterIDs[1].split( ',' )
				m_index = random.randint( 0, len( monsters ) - 1 )
				( x, y, z ) = monsPos
				collide = BigWorld.collide( caster.spaceID, ( x, y + 2, z ), ( x, y - 2, z ) )
				if collide != None:
					y = collide[0].y
				monsPos = ( x, y, z )
				newEntity = caster.createObjectNearPlanes( monsters[m_index], monsPos, caster.direction, { "spawnPos" : tuple( monsPos ), "level":self._treatureLevel  } )
				if newEntity.isEntityType( csdefine.ENTITY_TYPE_TREASURE_MONSTER ):
					newEntity.setOwner( caster )			# ����Ȩ����������
					newEntity.getScript().setBirthTime( newEntity )				# ���ô˹��ﵮ����ʱ�䣬��AI���жϺ�ʱ��������
					newEntity.setTemp( "dropItem", treasureBoxID )	# ���õ������ƷΪ��òر�ͼ��Ӧ�ı���
			value = cschannel_msgs.SKILL_INFO_5 % ( self.getMapName( spaceName ), int( positions[0][0] ), int( positions[0][2] ), int( positions[1][0] ), int( positions[1][2] ), int( positions[2][0] ), int( positions[2][2] ) )	# ��ʽ�硰������(100,200)��
			# �㲥����������������������λ��
			caster.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.CELL_SPELL_322398002_2, cschannel_msgs.CELL_SPELL_322398002_3, [] )
			msg = cschannel_msgs.CELL_SPELL_322398002_4 % ( caster.playerName, value )
			caster.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "", msg, [] )
			caster.statusMessage( csstatus.SKILL_TREASURE_GET_FAR_MONSTER )
		else:
			# ��ΧԽ���ˣ�˵���߻��ĸ�����д����
			ERROR_MSG( "Situation rates is not correct!" )
			return
		Spell_Item.receive( self, caster, receiver )
		
	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "Cannot find the item form uid[%s]." % uid )
			return csstatus.SKILL_TREASURE_POS_NOT_VALID

		self._treatureLevel = int( item.getLevel() )	# �����洢��ͼ����
		if caster.level < self._treatureLevel:			# ��Ҽ���̫��
			return csstatus.SKILL_TREASURE_LEVEL_LOW	# �ڱ����кܴ���յģ��������������㣬Ŭ������֮����ȥ�ɣ�

		treasureSpace = item.query( "treasure_space", "" )		# ȡ���ر�ͼ�еĵ�ͼ��Ϣ
		treasurePosStr = item.query( "treasure_position", None )# ȡ���ر�ͼ�е�������Ϣ
		treasurePosArr = eval( treasurePosStr )
		treasurePos = ( int( treasurePosArr[0] ), int(treasurePosArr[2]) )

		if treasureSpace == "" or treasurePos == None:
			# ���ûȡ������˵������û��������Щ��Ϣ����ͼ��Ϣ��������Ϣ�Ǳ���Ҫ�еģ��������ɳ��������������ɵ�
			ERROR_MSG( "Your treasure paper has lost location messages!" )
			return csstatus.SKILL_CANT_CAST

		if not self.isTreasurePosValid( caster, treasureSpace, treasurePos, 20 ):
			# ������ڶ�Ӧ������λ�ø��������ڱ�����ʾ�������ھ���ô���ҵ������أ������ڱ�ͼ��ָʾ�������ھ�����ڳ������
			return csstatus.SKILL_TREASURE_POS_NOT_VALID

		reqItem = caster.findItemFromNKCK_( self._reqItemID )
		if not reqItem:	# û�����¾Ͳ����ڱ�,��ʾ�����ò����ڱ����ѵ��ÿ��Ӱ�������Я�����²����ھ����
			return csstatus.SKILL_ITEM_NO_SCOOP

		if caster.checkItemsPlaceIntoNK_( [item] ) == csdefine.KITBAG_NO_MORE_SPACE:
			# ����������ʾ��������û�ж����λ�������ڳ��������ȥ���������һ���յİ���λ�ɣ���
			return csstatus.SKILL_TREASURE_KITBAG_FULL

		if caster.vehicle or getCurrVehicleID( caster ):
			caster.client.onStatusMessage( csstatus.TREASURE_FORBID_VEHICLE, "" )
			return

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

	def getMapName( self, spaceName ):
		"""
		���ݵ�ͼspaceName�õ���ͼ�ĺ�������
		��Ϊ�õ���ͼ���ֵĽӿ�ֻ�пͻ����У������������Ҫ��������ϵͳ��Ϣ����ң����Բ�����������дһ������������
		��������뼰ʱָ��������
		"""
		if not g_maps_info.has_key( spaceName ):
			ERROR_MSG( "No such map can be found in map infos, have you missed some datas?" )
			spaceName = "fengming"
		return g_maps_info[spaceName]

	def getSituIndex( self ):
		"""
		��ô򿪲ر�ͼ����ܷ��������������
		Ŀǰ�߻�������30��Ϊһ��
		"""
		return min( self._treatureLevel / 30, 4 )

	def getRewardIndex( self ):
		"""
		��ô򿪲ر�ͼ����ܵõ�����Ʒ������
		"""
		# Ŀǰ���ܵõ�����Ʒֻ�б���
		return 0

	def spawnMonsterOnOrigin( self, monsterClassName, caster, treasureBoxID ):
		"""
		ԭ��ˢ��
		"""
		#----����ƫ����---- #
		rad = math.pi * 2.0 * random.random()
		pos = Math.Vector3( caster.position )
		distance = 2 + 2 * random.random()
		pos.x += distance * math.sin( rad )
		pos.z += distance * math.cos( rad )
		# ----------------- #
		( x, y, z ) = pos
		collide = BigWorld.collide( caster.spaceID, ( x, y + 2, z ), ( x, y - 2, z ) )
		if collide != None:
			y = collide[0].y
		pos = ( x, y, z )
		newEntity = caster.createObjectNearPlanes( monsterClassName, pos, caster.direction, { "spawnPos" : tuple( pos ), "level":self._treatureLevel  } )
		if newEntity.isEntityType( csdefine.ENTITY_TYPE_TREASURE_MONSTER ):
			newEntity.setOwner( caster )			# ����Ȩ����������
			newEntity.setTemp( "dropItem", treasureBoxID )	# ���õ������ƷΪ��òر�ͼ��Ӧ�ı���
		return newEntity
