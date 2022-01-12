# -*- coding: gb18030 -*-


from bwdebug import *
import BigWorld
import csconst
import Const
from SpaceCopy import SpaceCopy
import csdefine

DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 10

class SpaceCopyYXLMPVP( SpaceCopy ):
	"""
	英雄联盟副本
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.getScript().initPatrolInfo( self )

	def monster_choosePatrolList( self, monsterEntityID ):
		"""
		define method
		为NPC选择巡逻路线
		"""
		patrolListInfo = self.queryTemp( "spacePatrolLists",[] )
		patrolNpcList = self.queryTemp( "spacePatrolNpcList", [] )
		if len( patrolListInfo ) == 0:
			 DEBUG_MSG( "Hero Alliance has no patrolList for NPC( className : %s ) to choose !"% str( monsterEntity.className ) )
			 return
		monsterEntity = BigWorld.entities.get( monsterEntityID )
		if not monsterEntity:
			return
		for e in patrolNpcList:
			if e == monsterEntity.className:
				try:
					patrolList = patrolListInfo[ patrolNpcList.index( e ) ]
				except IndexError :
					ERROR_MSG( "Hero alliance patrolList index %d out of range"%e.index )
					return
				self.beginPatrol( monsterEntity, patrolList )
				break

	def beginPatrol( self, entity, graphID ):
		"""
		怪物开始巡逻
		"""
		patrolList = BigWorld.PatrolPath( graphID )
		if not patrolList or not patrolList.isReady():
			ERROR_MSG( "Hero alliance patrolList (%s) is not ready or not have such graphID!"%graphID )
			return
		else:
			patrolPathNode, position = patrolList.nearestNode( entity.position )
			entity.patrolPathNode = patrolPathNode
			entity.patrolList = patrolList
			entity.doPatrol( entity.patrolPathNode, entity.patrolList  )

	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method.
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player:
			spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
			player.client.onShowYXLMCopyNPCSign( spaceLabel )
		self.recoverPlayerEquips( baseMailbox, params["playerDBID"] )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		define method.
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		player = BigWorld.entities.get( baseMailbox.id, None )
		if player :
			player.client.onCloseYXLMCopyNPCSign()
		self.removePlayerEquips( baseMailbox, params["playerDBID"] )
		if len( self._players ) == 0:					# 关闭副本
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )

	def onYXLMCopyBossCreated( self, id, className, spawnPos, signType ):
		"""
		Boss创建的时候,通知客户端添加Boss标记
		"""
		if len( self._players ) == 0:
			return
		entity = BigWorld.entities.get( id )
		if not entity:
			DEBUG_MSG( "SpaceEntity %s can't get %s , id is %i " % ( self.className, className, id )  )
			return

		for player in self._players:
			try:
				relation = BigWorld.entities.get( player.id ).queryRelation( entity )
				player.client.onShowYXLMCopyBossSign( id, className, spawnPos, relation, signType )
			except:
				continue

	def onYXLMCopyBossDied( self, id, className, spawnPos, diedPos ):
		"""
		Boss死亡时，通知客户端更新Boss标记
		"""
		if len( self._players ) == 0:
			return
		entity = BigWorld.entities.get( id )
		if not entity:
			DEBUG_MSG( "SpaceEntity %s can't get %s , id is %i " % ( self.className, className, id )  )
			return

		for player in self._players:
			try:
				relation = BigWorld.entities.get( player.id ).queryRelation( entity )
				player.client.onYXLMCopyBossDied( id, className, spawnPos, diedPos, relation )
			except:
				continue

	def updateYXLMCopyBossPos( self, id, className, pos ):
		"""
		更新Boss位置信息
		"""
		if len( self._players ) == 0:
			return
		entity = BigWorld.entities.get( id )
		if not entity:
			DEBUG_MSG( "SpaceEntity %s can't get %s , id is %i " % ( self.className, className, id )  )
			return

		for player in self._players:
			try:
				relation = BigWorld.entities.get( player.id ).queryRelation( entity )
				player.client.onUpdateYXLMCopyBossPos( id, className, pos, relation )
			except:
				continue
	
	def onYXLMMonsterGetDamage( self, id, flashTime ):
		"""
		防御塔、基地受到一定伤害时图标闪烁
		"""
		if len( self._players ) == 0:
			return
		entity = BigWorld.entities.get( id )
		if not entity:
			DEBUG_MSG( "SpaceEntity %s can't get %s , id is %i " % ( self.className, className, id )  )
			return

		for player in self._players:
			try:
				relation = BigWorld.entities.get( player.id ).queryRelation( entity )
				if relation == csdefine.RELATION_FRIEND:
					player.client.onYXLMMonsterGetDamage( id, flashTime )
			except:
				continue

	def shownDetails( self ):
		"""
		shownDetails 副本内容显示规则：
		[ 
			0: 剩余时间
			1: 剩余小怪
			2: 剩余小怪批次
			3: 剩余BOSS
			4: 蒙蒙数量
			5: 剩余魔纹虎数量
			6: 剩余真鬼影狮数量
			7: 下一波剩余时间(拯救猰貐)
		]
		"""
		return [ 0 ]

	# ----------------------------------------------------------------
	# NPC装备交易，将玩家购买到的装备放在副本进行存储
	# 设计思想是：
	# 1、玩家从副本内的NPC购买装备时，除了将装备放在玩家身上，还将装备
	#	存储到副本
	# 2、当玩家退出副本时，会将装备从玩家身上移除，但是不从副本移除
	# 3、当玩家掉线时，玩家身上的装备不会保存到数据库，而当玩家在副本内
	#	重新登录时，如果有先前购买的装备，则将装备重新发送给玩家
	# 4、副本销毁时，装备将自动消失
	# 说明：玩家身上的装备不存入数据库的原因是，玩家再次上线需要判断副本
	# 是否已经销毁，然后决定是让玩家重新将装备穿上还是将装备丢弃，在处理
	# 实现上没有现在这种方式那么简单灵活。
	# ----------------------------------------------------------------
	def onPlayerAddEquip( self, playerDBID, equipItem ) :
		"""
		<Define method>
		玩家获得英雄联盟的装备后，将装备保存到副本里，以便再次登录副本时恢复
		@type	playerDBID : DATABASE_ID
		@param	playerDBID : 玩家的数据库ID
		@type	equipItem : ITEM
		@param	equipItem : 继承于CItemBase的物品实例
		"""
		equipBag = self.getEquipBagOfPlayer( playerDBID, True )
		equipBag[equipItem.uid] = equipItem

	def onPlayerRemoveEquip( self, playerDBID, equipUid ) :
		"""
		<Define method>
		玩家移除英雄联盟副本的装备
		@type	playerDBID : DATABASE_ID
		@param	playerDBID : 玩家的数据库ID
		@type	equipUid : UID
		@param	equipUid : 物品实例的UID
		"""
		equipBag = self.getEquipBagOfPlayer( playerDBID )
		if equipBag and equipUid in equipBag :
			del equipBag[equipUid]

	def recoverPlayerEquips( self, playerBase, playerDBID ) :
		"""
		恢复玩家已购买的英雄联盟副本装备
		"""
		equipBag = self.getEquipBagOfPlayer( playerDBID )
		if equipBag :
			for equipItem in equipBag.itervalues() :
				playerBase.cell.addYXLMEquip( equipItem )

	def removePlayerEquips( self, playerBase, playerDBID ) :
		"""
		移除玩家身上已购买的英雄联盟副本装备
		"""
		equipBag = self.getEquipBagOfPlayer( playerDBID )
		if equipBag :
			for equipUid in equipBag.iterkeys() :
				playerBase.cell.removeYXLMEquip( equipUid )

	def getEquipBagOfPlayer( self, playerDBID, createIfNotExist=False ) :
		"""
		"""
		bags = self.queryTemp( "YXLM_EQUIP_BAGS" )
		if bags :
			if playerDBID in bags :
				return bags[playerDBID]
			elif createIfNotExist :
				bags[playerDBID] = {}
				return bags[playerDBID]
		elif createIfNotExist :
			bags = {}
			bags[playerDBID] = {}
			self.setTemp( "YXLM_EQUIP_BAGS", bags )
			return bags[playerDBID]
		return None
	
	def closeYXLMSpace( self ):
		"""
		define method.
		关闭当前副本
		"""
		self.getScript().contents[ -1 ].onContent( self )
	
	def registMonster( self, className, m ):
		"""
		define method.
		注册一个怪物
		"""
		self.monsterInfos.add( className, m )
	
	def unRegistMonster( self, className, m ):
		"""
		define method.
		删除一个怪物
		"""
		self.monsterInfos.remove( className, m )
	
	def sendSAICommand( self, recvIDs, type, sid, sendEntity ):
		"""
		define mthod.
		往指定的entity发送sai
		"""
		for className in recvIDs:
			for m in self.monsterInfos.get( className ):
				m.mailbox.recvSAICommand( type, sid, sendEntity )
