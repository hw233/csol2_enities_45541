# -*- coding: gb18030 -*-
"""
藏宝图使用时触发
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
		构造函数。
		"""
		Spell_Item.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self._monsterIDs = ( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else "" ) .split( '|' )		# 要生成的怪物的ID（className），必须填两个（如：11111111,11111112,11111113|22222221,22222222,22222223）
																		# 而且必须按照顺序：盗宝贼1类型的不同ID|盗宝贼2类型的不同ID
		self._reqItemID = int( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 ) 						# 需要的普通物品（铁锹）
		self._goldScoop = int( dict[ "param3" ] if len( dict[ "param3" ] ) > 0 else 0 ) 						# 金锹ID(拥有何种物品就一定会得到宝箱)
		self._rewardItems = ( dict[ "param4" ] if len( dict[ "param4" ] ) > 0 else "" ) .split( '|' )		# 得到的物品id（如宝箱）
		self._situations = ( dict[ "param5" ] if len( dict[ "param5" ] ) > 0 else "" ) .split('|')		# 不同情况的概率(如：70|20|10，加起来必须为100)
		self._treatureLevel = 1											# 藏宝图的级别（级别决定了宝藏地点）
		if len( self._monsterIDs ) != 2:
			ERROR_MSG( "Length of Monster array must be exactly 2! skillID: %s" % self.getID() )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		rateArr = self._situations[self.getSituIndex()].split( ',' )
		if len( rateArr ) != 3:
			ERROR_MSG( "Situation rates lost!" )
			return
		start = 0
		node1 = int( rateArr[0] )
		node2 = node1 + int( rateArr[1] )
		node3 = node2 + int( rateArr[2] )
		item = caster.findItemFromNKCK_( self._goldScoop )	# 判断是否身上有金锹
		if item:
			# 如果有金锹，则node1=100，表示node1会100%发生，也就是100%会生成宝箱
			node1 = 100
		else:
			# 如果没有金锹，要找到身上的铁锹，然后移除掉铁锹
			item = caster.findItemFromNKCK_( self._reqItemID )
		caster.removeItem_( item.order, 1, csdefine.DELETE_ITEM_DIGTREASURE )	# 移除掉铁锹
		situCode = random.randint( 0, 100 )	# 在0-100里随即一个整数
		treasureBoxID = int( self._rewardItems[ self.getRewardIndex() ] )	# 得到的宝箱ID
		if situCode >= start and situCode < node1:
			# 有可能直接挖到宝箱，掉到玩家包裹里
			item = caster.createDynamicItem( treasureBoxID )
			item.set( "level", self._treatureLevel )
			item.set( "aType", csdefine.ACTIVITY_CANG_BAO_TU )
			caster.addItem( item, csdefine.ADD_ITEM_TREASUREMAP )
			caster.statusMessage( csstatus.SKILL_TREASURE_GET_BAOXIANG )
		elif situCode >= node1 and situCode < node2:
			# 有可能直接在原地刷出一个怪物“盗宝贼”
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
			# 有可能在野外随机刷出一个盗宝贼怪物
			# 算法还没定，同FuncTreasureMap里随机生成宝藏地点算法应该相同
			uid = caster.queryTemp( "item_using" )
			item = caster.getByUid( uid )
			if item is None:
				ERROR_MSG( "cannot find the item form uid[%s]." % uid )
				return
			treasureLvl = item.getLevel()
			spaceName = caster.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )	# 获得当前spaceName
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
					# 循环2000次还找不到合适的坐标，就跳出循环。避免陷入死循环
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
					newEntity.setOwner( caster )			# 所有权归该玩家所有
					newEntity.getScript().setBirthTime( newEntity )				# 设置此怪物诞生的时间，给AI来判断何时自行销毁
					newEntity.setTemp( "dropItem", treasureBoxID )	# 设置掉落的物品为与该藏宝图对应的宝箱
			value = cschannel_msgs.SKILL_INFO_5 % ( self.getMapName( spaceName ), int( positions[0][0] ), int( positions[0][2] ), int( positions[1][0] ), int( positions[1][2] ), int( positions[2][0] ), int( positions[2][2] ) )	# 格式如“凤鸣的(100,200)”
			# 广播所有在线玩家这个盗宝贼的位置
			caster.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_NPC_SPEAK, 0, cschannel_msgs.CELL_SPELL_322398002_2, cschannel_msgs.CELL_SPELL_322398002_3, [] )
			msg = cschannel_msgs.CELL_SPELL_322398002_4 % ( caster.playerName, value )
			caster.base.chat_handleMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, "", msg, [] )
			caster.statusMessage( csstatus.SKILL_TREASURE_GET_FAR_MONSTER )
		else:
			# 范围越界了，说明策划的概率填写错了
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

		self._treatureLevel = int( item.getLevel() )	# 用来存储宝图级别
		if caster.level < self._treatureLevel:			# 玩家级别太低
			return csstatus.SKILL_TREASURE_LEVEL_LOW	# 挖宝是有很大风险的，您的能力还不足，努力修炼之后再去吧！

		treasureSpace = item.query( "treasure_space", "" )		# 取出藏宝图中的地图信息
		treasurePosStr = item.query( "treasure_position", None )# 取出藏宝图中的坐标信息
		treasurePosArr = eval( treasurePosStr )
		treasurePos = ( int( treasurePosArr[0] ), int(treasurePosArr[2]) )

		if treasureSpace == "" or treasurePos == None:
			# 如果没取出来，说明当初没有设置这些信息，地图信息和坐标信息是必须要有的，并且是由程序主动设置生成的
			ERROR_MSG( "Your treasure paper has lost location messages!" )
			return csstatus.SKILL_CANT_CAST

		if not self.isTreasurePosValid( caster, treasureSpace, treasurePos, 20 ):
			# 如果不在对应的坐标位置附近则不能挖宝，提示“胡乱挖掘怎么能找到宝物呢？必须在宝图上指示的坐标挖掘才能挖出宝物！”
			return csstatus.SKILL_TREASURE_POS_NOT_VALID

		reqItem = caster.findItemFromNKCK_( self._reqItemID )
		if not reqItem:	# 没有铁锹就不能挖宝,提示“不用铲子挖宝，难道用筷子啊！必须携带铁锹才能挖掘宝物。”
			return csstatus.SKILL_ITEM_NO_SCOOP

		if caster.checkItemsPlaceIntoNK_( [item] ) == csdefine.KITBAG_NO_MORE_SPACE:
			# 背包满，提示“包裹中没有多余的位置啦，挖出宝物放哪去？快整理出一个空的包裹位吧！”
			return csstatus.SKILL_TREASURE_KITBAG_FULL

		if caster.vehicle or getCurrVehicleID( caster ):
			caster.client.onStatusMessage( csstatus.TREASURE_FORBID_VEHICLE, "" )
			return

		return Spell_Item.useableCheck( self, caster, target)

	def isTreasurePosValid( self, player, spaceName, position, offset ):
		"""
		检查玩家挖宝位置是否合法（是否处于某个地图spaceName的坐标position范围内）
		@param 	player		:	被检查的玩家
		@type 	player		:	Role
		@param 	spaceName	:	地图名
		@type 	spaceName	:	STRING
		@param 	position	:	二维坐标位置
		@type 	position	:	Tuple
		@param 	offset		:	允许的范围差距，必须为正值
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
		根据地图spaceName得到地图的汉字名字
		因为得到地图名字的接口只有客户端有，而这里服务器要用来发送系统消息给玩家，所以不得已在这里写一个函数来解析
		如果不妥请及时指出并改正
		"""
		if not g_maps_info.has_key( spaceName ):
			ERROR_MSG( "No such map can be found in map infos, have you missed some datas?" )
			spaceName = "fengming"
		return g_maps_info[spaceName]

	def getSituIndex( self ):
		"""
		获得打开藏宝图后可能发生的情况的索引
		目前策划定的是30级为一段
		"""
		return min( self._treatureLevel / 30, 4 )

	def getRewardIndex( self ):
		"""
		获得打开藏宝图后可能得到的物品的索引
		"""
		# 目前可能得到的物品只有宝箱
		return 0

	def spawnMonsterOnOrigin( self, monsterClassName, caster, treasureBoxID ):
		"""
		原地刷怪
		"""
		#----坐标偏移量---- #
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
			newEntity.setOwner( caster )			# 所有权归该玩家所有
			newEntity.setTemp( "dropItem", treasureBoxID )	# 设置掉落的物品为与该藏宝图对应的宝箱
		return newEntity
