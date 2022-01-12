# -*- coding: gb18030 -*-
#
from bwdebug import *
from ObjectScripts.GameObjectFactory import g_objFactory
from Resource.NPCQuestDroppedItemLoader import NPCQuestDroppedItemLoader
from interface.GameObject import GameObject
import csdefine
import csstatus
import random
import BigWorld
import items
import Const
import ItemSystemExp

g_items = items.instance()
g_npcQuestDroppedItems = NPCQuestDroppedItemLoader.instance()

# onTimer 的timerArg
DESTORY_CBID 				= 1																	# 直接销毁
QUERY_DESTORY_CBID  		= 2																	# 判定销毁
PICK_SPEED_CONTROL 			= 3																	# 拾取速度控制
DESTROY_SAVE_CBID			= 4																	# 消失前保护
HANDLE_RESULT_CBID 			= 5																	# ROLL处理
HANDLE_OVERTIME_CBID 		= 6																	# ROLL超时处理


# 箱子的消失时间和箱子中物品品质的关系
DESTORY_TIME = { 1 	:  	60,
				2	:	120,
				3	:	180,
				4	:	240,
				5	:	300,
				}

DESTROY_SAVE_TIME = 2																	# 消失前不允许拾取的时间


class DroppedBox( GameObject ):
	"""
	"""
	def __init__(self):
		"""
		@summary:	初始化
		"""
		GameObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_DROPPED_BOX )
		#self.itemBox = {}																# 包含的普通物品 such { 0:item00, 1:item01,... }
		#self.queryIndexs = []															# 正在获取的普通物品索引
		#self.questItemBox = []															# 包含的任务物品 such { 0:item00, 1:item01,... }
		#self.queryQuestIndexs = []														# 正在获取的任务物品索引
		self.queryOwnersDict = {}														# 玩家查询物品权限记录
		self.pickOwnersDict  = {}														# 玩家拾取物品权限记录
		self.assignOwnersDict= {}														# 玩家分配物品权限记录
		self.rollOwnersDict = {}
		self.membersID = []																# 有效的队员ID列表
		self.pickedItemList = []														# 玩家已经拾取过了的物品列表
		self.isPickedAnyone = False														# 箱子默认非任何人可以拾取

		self.addTimer( 300, 0, QUERY_DESTORY_CBID )										# 这个TIMER用于300秒后，检查一下这个箱子有没有物品，没有就销毁


	def init( self, bootyOwner, itemList ):
		"""
		初始化掉落箱子
		"""
		if bootyOwner == []:		# 如果没有owner，则箱子任何人都能拾取
			self.isPickedAnyone = True
			for iItem in itemList:
				self.__addItem( self.itemBox, iItem )
			self._setBoxDissapperTime()
			return

		entity = BigWorld.entities.get( bootyOwner[0] )

		if entity is None:
			self.destroy()
			return

		if entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
			player = BigWorld.entities.get( entity.ownerID )
		elif not entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):						#既不是宠物也不是角色杀死这个怪物，则直接返回
			self.destroy()
			return
		else:
			player = entity


		if player is None:
			self.destroy()
			return

		self._setBoxDissapperTime()
		for iItem in itemList:
			self.__addItem( self.itemBox, iItem )

		if player.id not in self.membersID:
			self.membersID.append( player.id )

		if bootyOwner[1] == 0:
			indexs = self.__getIndexs( self.itemBox )
			self.setDropItemsQueryOwner( player.id, indexs )
			self.setDropItemsPickOwner( player.id, indexs )
		else:
			players = [ e for e in self.entitiesInRangeExt( Const.TEAM_GAIN_EXP_RANGE, 'Role' ) if e.teamMailbox is not None and e.teamMailbox.id == bootyOwner[1] ]
			if len( players ) > 0:
				players[0].buildBoxOwners( self.id, self.itemBox )

	def queryDropItems( self, srcEntityID ):
		"""
		Exposed method
		查看战利品
		"""
		if not self.isPickedAnyone and not srcEntityID in self.queryOwnersDict:
			return

		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return

		if player.getState() == csdefine.ENTITY_STATE_DEAD:
			return

		pickers = self.queryTemp( 'pickers',[] )
		if player.id in pickers:
			return

		tempList = []															# 这个玩家可以查询的“物品字典”列表
		if self.isPickedAnyone:															# 如果箱子是任何人都可以拾取的
			tempList = self.itemBox
		else:
			for iIndex in self.queryOwnersDict[srcEntityID]:
				for jIndex in self.__getIndexs( self.itemBox ):
					if iIndex == jIndex:
						tempList.append( self.__getItemDict( self.itemBox, jIndex ) )

				for kIndex in self.__getIndexs( self.questItemBox ):
					if iIndex == kIndex:
						tempList.append( self.__getItemDict( self.questItemBox, kIndex ) )
			if tempList == []:
				return
			#处理接取任务物品，不可在完成了该物品对应任务后重复获得的这个物品问题
			tempRemoveList = []
			for i in tempList:
				questID = i.values()[1].getQuestID()
				if  questID != 0 and player.isReal() and player.getQuest( questID ).query( player ) in [csdefine.QUEST_STATE_COMPLETE, csdefine.QUEST_STATE_FINISH, csdefine.QUEST_STATE_NOT_FINISH] :
					tempRemoveList.append( i )
			
			for i in tempList:
				if not self.questItemBox: break
				tempQuestIDs, tempDict  = player.questsTable.getReadQuestID()
				for qid in tempQuestIDs:
					itemID = [ i.values()[1].id ]
					tItemIds = list( set( itemID ) & set( g_npcQuestDroppedItems.getQuestNeedItems( qid ) ) )
					if not tItemIds: continue
					if tempDict.has_key( qid ):
						qid = tempDict[qid]
					questTasks = player.getQuestTasks( qid )
					for tid in tItemIds:
						if tid != i.values()[1].id: continue
						result = questTasks.deliverIsComplete( tid, player )
						if result:
							tempRemoveList.append( i )
				


			for i in tempRemoveList:
				tempList.remove( i )

			for index in self.__getIndexs( tempRemoveList ):
				self.__removeItemByIndex( index )
		
		if tempList == []:
			player.clientEntity( self.id ).receiveDropState( False )
		else:
			player.clientEntity( self.id ).receiveDropItems( tempList )

		pickers.append( srcEntityID )
		self.setTemp( 'pickers', pickers )
		self.addTimer( 2, 0, PICK_SPEED_CONTROL )

		# 记录查看过箱子的人
		queryPickers = self.queryTemp( "queryPickers", [] )
		if not srcEntityID in queryPickers:
			queryPickers.append( srcEntityID )
		self.setTemp( "queryPickers", queryPickers )

	def pickDropItem( self, srcEntityID, index ):
		"""
		Exposed method
		获取战利品
		"""
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return

		if player.getState() == csdefine.ENTITY_STATE_DEAD:
			return

		if index in self.pickedItemList:
			return
		for iList in self.assignOwnersDict.itervalues():
			if index in iList:
				if player.isTeamCaptain():
					BigWorld.entities[srcEntityID].client.allcateDropItem( index )
				else:
					BigWorld.entities[srcEntityID].client.onStatusMessage( csstatus.DROP_BOX_CAPTAIN_FENPEI, "" )
				return
		if self.rollOwnersDict.has_key(srcEntityID) and index in self.rollOwnersDict[srcEntityID]:
			self.rollStart( player, index )
			return

		if not( self.pickOwnersDict.has_key(srcEntityID) and index in self.pickOwnersDict[srcEntityID] ) and not self.isPickedAnyone:
			return

		for iIndex in self.__getIndexs( self.itemBox ):
			if index == iIndex:
				self.queryIndexs.append( iIndex )
				BigWorld.entities[srcEntityID].requestAddItem( self.id, iIndex, self.__getItem( index ), False )
				return

		for iIndex in self.__getIndexs( self.questItemBox ):
			if index == iIndex:
				self.queryQuestIndexs.append( iIndex )
				BigWorld.entities[srcEntityID].requestAddItem( self.id, iIndex, self.__getItem( index ), True)
				return
				
	def pickDropItems( self, srcEntityID, indexs ):
		"""
		Exposed method
		获取多个战利品 by 姜毅
		"""
		for index in indexs:
			self.pickDropItem( srcEntityID, index )

	def pickUpAllItems( self, srcEntityID ):
		"""
		Exposed method.
		申请拾取所有物品，目前仅自动拾取功能用到。15:29 2009-2-10,wsf
		"""
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None:
			return

		if player.getState() == csdefine.ENTITY_STATE_DEAD:
			return

		if self.queryTemp('destroy_save', False ):
			return

		tempItemListInfo = []
		for itemIndex in self.__getIndexs( self.itemBox ):
			for iList in self.assignOwnersDict.itervalues():
				if itemIndex in iList:
					if player.isTeamCaptain():
						player.client.allcateDropItem( itemIndex )
					else:
						player.client.onStatusMessage( csstatus.DROP_BOX_CAPTAIN_FENPEI, "" )
					continue
			if self.rollOwnersDict.has_key(srcEntityID) and itemIndex in self.rollOwnersDict[srcEntityID]:
					self.rollStart( player, itemIndex )
					continue

			if not( self.pickOwnersDict.has_key(srcEntityID) and itemIndex in self.pickOwnersDict[srcEntityID] ) and not self.isPickedAnyone:
					continue
			self.queryIndexs.append( itemIndex )
			tempItemListInfo.append( ( itemIndex, self.__getItem( itemIndex ), False ) )

		for itemIndex in self.__getIndexs( self.questItemBox ):
			self.queryQuestIndexs.append( itemIndex )
			if not self.pickOwnersDict.has_key(srcEntityID) or itemIndex not in self.pickOwnersDict[srcEntityID]:
				continue
			tempItemListInfo.append( ( itemIndex, self.__getItem( itemIndex ), True ) )

		for i in tempItemListInfo:
			BigWorld.entities[ srcEntityID ].requestAddItem( self.id, i[0], i[1], i[2] )

	def receiveItemPickedCB( self, playerID, index, isPicked, isQuestItem, isMoney, databaseID ):
		"""
		define method
		得到玩家拾取物品的确认。
		"""
		player = BigWorld.entities.get( playerID, None )
		if player is None:
			return
		if self.isPickedAnyone:		# 如果箱子任何人都能拾取
			if isPicked:			# 物品被拾取
				self._setBoxDissapperTime()
				for id in self.queryTemp( "queryPickers", [] ):
					if BigWorld.entities.has_key( id ):
						BigWorld.entities[id].clientEntity( self.id ).onBoxItemRemove( index )
				self.__removeItemByIndex( index )
			else:
				if isMoney:
					player.client.onStatusMessage( csstatus.DROP_BOX_MONEY_FULL, "" )
				else:
					#print "DROP_BOX_TOO_MUCH_SUCH_ITEM 1"
					player.client.onStatusMessage( csstatus.DROP_BOX_TOO_MUCH_SUCH_ITEM, "" )
			player.clientEntity( self.id ).receiveDropState( self.displayOnClient( playerID ) )
			return

		indexs = [index]
		if isPicked:															#物品被拾取
			self.pickedItemList.append( index )
			self._setBoxDissapperTime()

			if self.__getItem( index ) == None:
				return

#			if self.__getItem( index ).getOnlyLimit() != 1 and isQuestItem:		#如果是任务物品，而且不是唯一性的,那只掉落一个
#				id = self.__getItem( index ).id
#				indexs.extend( self.__getQuestItemIDsIndexs( id ) )

			for iIndex in indexs:
				for iIndexs in self.queryOwnersDict.itervalues():
					if iIndex in iIndexs:
						iIndexs.remove( iIndex )

				for iIndexs in self.pickOwnersDict.itervalues():
					if iIndex in iIndexs:
						iIndexs.remove( iIndex )

				for iIndexs in self.assignOwnersDict.itervalues():
					if iIndex in iIndexs:
						iIndexs.remove( iIndex )

				for iID in self.queryOwnersDict:
					if BigWorld.entities.has_key( iID ):
						BigWorld.entities[iID].clientEntity( self.id ).onBoxItemRemove( iIndex )

				if iIndex in self.queryIndexs:
					self.queryIndexs.remove( iIndex )
				if iIndex in self.queryQuestIndexs:
					self.queryQuestIndexs.remove( iIndex )

				self.__removeItemByIndex( iIndex )
		else:
			if index in self.queryIndexs:
				self.queryIndexs.remove( index )
			if index in self.queryQuestIndexs:
				self.queryQuestIndexs.remove( index )
			if isMoney:
				player.client.onStatusMessage( csstatus.DROP_BOX_MONEY_FULL, "" )
			else:
				#print "DROP_BOX_TOO_MUCH_SUCH_ITEM 2"
				player.client.onStatusMessage( csstatus.DROP_BOX_TOO_MUCH_SUCH_ITEM, "" )

		player.clientEntity( self.id ).receiveDropState( self.displayOnClient( playerID ) )

	def assignDropItem( self, srcEntityID, index, memberID ):
		"""
		Exposed method
		分配战利品
		"""
		if not BigWorld.entities.has_key( srcEntityID ) or not BigWorld.entities.has_key( memberID ) or \
			BigWorld.entities[srcEntityID].getState() == csdefine.ENTITY_STATE_DEAD or \
			BigWorld.entities[memberID].getState() == csdefine.ENTITY_STATE_DEAD:
			return

		if not srcEntityID in self.assignOwnersDict or index not in self.assignOwnersDict[srcEntityID]:
			ERROR_MSG( "AssignDropItem Error, srcEntityID  not in assignOwnersDict or index not in assignOwnersDict[srcEntityID]" )
			return
		item = None
		gettorName = None
		for iIndex in self.__getIndexs( self.itemBox ):
			if iIndex != index: continue
			item = self.__getItem( iIndex )
			gettor = BigWorld.entities[memberID]
			gettor.requestAddItem( self.id, iIndex, item, True)
			gettorName = gettor.getName()

		for iID in self.queryOwnersDict:		# 增加队长分配物品后对队员的通知信息 by姜毅
			member = BigWorld.entities.get( iID )
			if member is None: continue
			member.client.onStatusMessage( csstatus.TEAM_LEADER_GIVE_ITEM, str( ( gettorName, item.name() ) ) )

	def setDropItemsQueryOwner( self, ownerID, itemsIndexList ):
		"""
		define method
		设置符合查询某些物品的玩家
		"""
		#--------- 以下为防沉迷系统的判断 --------#
		if BigWorld.entities.has_key( ownerID ):
			picker = BigWorld.entities[ownerID]
			itemsIndexList = self.antiIndulgenceFilter( itemsIndexList, picker )

		if self.queryOwnersDict.has_key( ownerID ):
			self.queryOwnersDict[ownerID].extend( itemsIndexList )
		else:
			self.queryOwnersDict[ownerID] = itemsIndexList[:]

	def setDropItemsPickOwner( self, ownerID, itemsIndexList ):
		"""
		define method
		设置符合拾取某些物品的玩家
		"""
		if self.pickOwnersDict.has_key( ownerID ):
			self.pickOwnersDict[ownerID].extend( itemsIndexList )
		else:
			self.pickOwnersDict[ownerID] = itemsIndexList[:]

	def setDropItemsAssignOwner( self, ownerID, itemsIndexList ):
		"""
		define method
		设置符合分配某些物品的玩家
		"""
		if self.assignOwnersDict.has_key( ownerID ):
			self.assignOwnersDict[ownerID].extend( itemsIndexList )
		else:
			self.assignOwnersDict[ownerID] = itemsIndexList[:]

	def onTimer( self, controllerID, userData ):
		"""
		@summary:	定时销毁
		@type	controllerID	:	int32
		@type	userData		:	int32
		@param	controllerID	:	时间控制器ID
		@param	userData		:	用户数据
		"""
		if userData == DESTORY_CBID:
			self.destroy()

		elif userData == QUERY_DESTORY_CBID:
			if len( self.itemBox ) == 0 and len( self.questItemBox ) == 0:
				self.destroy()

		elif userData == PICK_SPEED_CONTROL:
			self.removeTemp( 'pickers' )

		elif userData == DESTROY_SAVE_CBID:
			self.setTemp( 'destroy_save', True )
		elif userData == HANDLE_RESULT_CBID:
			self.onRollCB()
		elif userData == HANDLE_OVERTIME_CBID:
			self.onOverTimeRollCB()

	def _setBoxDissapperTime( self ):
		"""
		设置箱子的消失时间
		"""
		if self.queryTemp('lastDestroyTimerID', -1 ) != -1:
			self.cancel( self.queryTemp('lastDestroyTimerID') )
			self.cancel( self.queryTemp('lastSaveTimerID') )

		quality = 1
		for iItem in self.__getItems( self.itemBox ):
			if iItem.getQuality() > quality:
				quality = iItem.getQuality()
		self.setTemp('lastDestroyTimerID', self.addTimer( DESTORY_TIME[quality], 0, DESTORY_CBID )	)# the first, check pickup time
		self.setTemp('lastSaveTimerID',self.addTimer( DESTORY_TIME[quality] - DESTROY_SAVE_TIME, 0, DESTROY_SAVE_CBID ) )	#消失前2秒内，不允许拾取物品



	def addQuestItems( self, playerID, itemList ):
		"""
		define method
		增加任务物品
		"""
		tempList = {}
		index = 0
		for iItem in itemList:
			index = self.__addItem( self.questItemBox, iItem )
			if self.queryOwnersDict.has_key( playerID ):
				self.queryOwnersDict[playerID].append( index )
			else:
				self.queryOwnersDict[playerID] = [index]
			if self.pickOwnersDict.has_key( playerID ):
				self.pickOwnersDict[playerID].append( index )
			else:
				self.pickOwnersDict[playerID] = [index]

	def abandonBoxItems( self, srcEntityID ):
		"""
		exposed method
		放弃任务箱子的物品权限,就是允许其他人拾取本来分配给我的物品
		"""
		if srcEntityID in self.queryOwnersDict:
			for iMemberID in self.membersID:
				if self.queryOwnersDict.has_key( iMemberID ):
					self.queryOwnersDict[iMemberID].extend( [ e for e in self.queryOwnersDict[srcEntityID] if e not in self.queryOwnersDict[iMemberID] ] )
				else:
					self.queryOwnersDict[iMemberID] = [ e for e in self.queryOwnersDict[srcEntityID] ]

		if srcEntityID in self.pickOwnersDict:
			for iMemberID in self.membersID:
				if self.pickOwnersDict.has_key( iMemberID ):
					self.pickOwnersDict[iMemberID].extend( [ e for e in self.pickOwnersDict[srcEntityID] if e not in self.pickOwnersDict[iMemberID] ] )
				else:
					self.pickOwnersDict[iMemberID] = [ e for e in self.queryOwnersDict[srcEntityID] ]

	def droppedBoxStatus( self, srcEntityID ):
		"""
		exposed method
		客户端缓冲完成后回调已判定箱子是否可见
		"""
		if not self.displayOnClient( srcEntityID ):
			return

		player = BigWorld.entities.get( srcEntityID )

		if player is None:
			return
		player.clientEntity( self.id ).receiveDropState( self.displayOnClient( srcEntityID ) )

	def addTeamMembersID( self, membersID ):
		"""
		define method
		"""
		for i in membersID:
			if i not in self.membersID:
				self.membersID.append( i )

	def displayOnClient( self, srcEntityID ):
		"""
		是否在客户端显示
		"""
		if self.isPickedAnyone:		# 如果箱子任何人都能拾取
			return True
		return self.queryOwnersDict.has_key( srcEntityID ) and len( self.queryOwnersDict[srcEntityID] ) > 0


	def __addItem( self, itemBox, item ):
		"""
		"""
		itemBox.append( {'order' :len( self.itemBox ) + len( self.questItemBox ), 'item' : item })
		return len( self.itemBox ) + len( self.questItemBox ) - 1

	def __getItems( self, itemBox ):
		"""
		"""
		items = []
		for iItemDict in itemBox:
			items.append( iItemDict['item'] )
		print "__getItems:items is %s"%items
		return items

	def __getIndexs( self, itemBox ):
		"""
		"""
		indexs = []
		for iItemDict in itemBox:
			indexs.append( iItemDict['order'] )

		return indexs

	def __getItemDict( self, itemBox, index ):
		"""
		"""
		for iItemDict in itemBox:
			if iItemDict['order'] == index:
				return iItemDict

		return {}

	def __getItem( self, index ):
		"""
		"""
		for iItemDict in self.itemBox:
			if iItemDict['order'] == index:
				return iItemDict['item']
		for iItemDict in self.questItemBox:
			if iItemDict['order'] == index:
				return iItemDict['item']

		return None

	def __removeItemByIndex( self, index ):
		"""
		"""
		for iItemDict in self.itemBox:
			if iItemDict['order'] == index:
				self.itemBox.remove( iItemDict )

		for iItemDict in self.questItemBox:
			if iItemDict['order'] == index:
				self.questItemBox.remove( iItemDict )

		if len( self.questItemBox ) == 0 and len( self.itemBox ) == 0:
			self.addTimer( 0.1, 0, DESTORY_CBID )

	def __getQuestItemIDsIndexs( self, itemID ):
		"""
		"""
		ids=[]
		for iItemDict in self.questItemBox:
			if iItemDict['item'].id == itemID:
				ids.append( iItemDict['order'] )

		return ids

	def antiIndulgenceFilter( self, itemsData, player ):
		"""
		防沉迷系统过滤个人掉落物品（组队不受的掉落不受影响，影响的是分配）
		"""
		if player != None:
			gameYield = player.wallow_getLucreRate()
			newData = []
			if gameYield == 1.0:
				return itemsData
			elif itemsData == 0:
				return newData
			else:
				for i in itemsData:
					if random.random() <= gameYield:
						newData.append( i )
				return newData
		return itemsData


	def setDropItemsRollOwner(  self, ownerID, itemsIndexList ):
		"""
		设置符合要求的roll玩家
		"""
		if not BigWorld.entities[ownerID].rollState:
			return
		if self.rollOwnersDict.has_key( ownerID ):
			self.rollOwnersDict[ownerID].extend( itemsIndexList )
		else:
			self.rollOwnersDict[ownerID] = itemsIndexList

	def rollStart( self, player, index ):
		"""
		启动roll机制
		"""
		rollDict = self.queryTemp( "rollDict", {} )
		rollList = self.queryTemp( "rollList", [] )
		if index in rollDict:
			return

		#members = player.getAllMemberInRange( Const.TEAM_GAIN_EXP_RANGE )
		members = []
		for i in self.rollOwnersDict:
			member = BigWorld.entities.get( i )
			if member != None:
				members.append( member )


		if len(members) == 0:
			for id in self.rollOwnersDict:
				if index in self.rollOwnersDict[id]:
					self.rollOwnersDict[id].remove( index )
					self.setDropItemsPickOwner( id, [index] )
			return

		item = self.__getItem( index )
		itemColor = self.getItemColor( item )
		for iMember in members:
			if index not in self.rollOwnersDict[iMember.id]:
				continue
			iMember.client.showRollInterface( index, item, self.id )


		rollDict[index] = [e.base for e in members]
		rollList.append( index )
		self.setTemp(  "rollDict", rollDict )
		self.setTemp(  "rollList", rollList )

		rollStartPositions = self.queryTemp( "rollStartPositions", [] )
		rollStartPositions.append( index )
		self.setTemp( "rollStartPositions", rollStartPositions )
		self.addTimer( 20.0, 0.0, HANDLE_OVERTIME_CBID )


	def onRollCB( self ):
		"""
		"""
		rollPositions = self.queryTemp( "rollPositions", [] )
		if len( rollPositions ) != 0:
			index = rollPositions.pop(0)
			self.handleRollResult( index )

	def onOverTimeRollCB(  self  ):
		"""
		"""
		rollStartPositions = self.queryTemp( "rollStartPositions", [] )
		if len( rollStartPositions ) != 0:
			index = rollStartPositions.pop(0)
			self.handleRollResult( index )


	def handleRollResult( self, index ):
		"""
		roll机制判定
		"""
		rollList = self.queryTemp(  "rollList", [] )
		if index not in rollList:
			return

		rollDict = self.queryTemp( "rollDict" )

		playerID = 0
		maxPoint = 0
		#index = rollList.pop(0)

		#rollPositions = self.queryTemp( "rollPositions", [] )
		#if len( rollPositions ) == 0:
		#	index = rollList.pop(0)
		#else:
		#	index = rollPositions.pop(0)

		for baseMailbox in rollDict[index]:
			tempPoint = self.queryTemp( "roll_%i_%i"%( index, baseMailbox.id ), -1 )
			if tempPoint >= maxPoint:
				playerID = baseMailbox.id
				maxPoint = tempPoint
			if tempPoint == -1:
				item = self.__getItem( index )
				itemColor = self.getItemColor( item )
				abandomPlayer = BigWorld.entities.get( baseMailbox.id, None )
				if abandomPlayer:
					for id in self.rollOwnersDict:
						player = BigWorld.entities.get( id, None )
						if player:
							player.client.onStatusMessage( csstatus.DROP_BOX_FANGQI,str( ( abandomPlayer.getName(),itemColor,item.name() ) )  )

		for id in self.queryOwnersDict:
			player = BigWorld.entities.get( id, None )
			if player:
				player.clientEntity( self.id ).onBoxItemRemove( index )
			if index in self.queryOwnersDict[id]:
				self.queryOwnersDict[id].remove( index )
		for id in self.rollOwnersDict:
			if index in self.rollOwnersDict[id]:
				self.rollOwnersDict[id].remove( index )
		if maxPoint >= 1 and BigWorld.entities.get( playerID, None ) is not None:
			self.addRollItem( playerID, index )
		else:
			for baseMailbox in rollDict[index]:
				self.setDropItemsQueryOwner( baseMailbox.id,  [index] )
				self.setDropItemsPickOwner( baseMailbox.id, [index] )

		for baseMailbox in rollDict[index]:
			member = BigWorld.entities.get( baseMailbox.id )
			if member:
				member.clientEntity( self.id ).receiveDropState( self.displayOnClient( baseMailbox.id ) )
				#member.clientEntity( self.id ).closeRollInterface( index )
				member.client.closeRollInterface( index, self.id )
		del rollDict[index]
		rollList.remove( index )

	def addRollItem( self, playerID, index ):
		"""
		增加roll 物品
		"""
		player = BigWorld.entities.get( playerID )
		if player == None:
			return

		player.requestAddRollItem( self.id, index, self.__getItem( index ) )


	def receiveAddRollItemCB( self, playerID, index, isPicked ):
		"""
		"""
		player= BigWorld.entities.get( playerID )
		if player is None:
			return
		members = []
		for i in self.rollOwnersDict:
			member = BigWorld.entities.get( i )
			if member != None:
				members.append( member )

		#for maibox in BigWorld.entities[playerID].getAllMemberInRange(20.0):
		for member in members:
			item = self.__getItem( index )
			itemColor = self.getItemColor( item )
			member.client.onStatusMessage( csstatus.DROP_BOX_WIN,str( (player.getName(),itemColor, item.name() )) )
		if isPicked:
			self.__removeItemByIndex( index )
			return
		player.client.onStatusMessage( csstatus.DROP_BOX_TOO_MUCH_SUCH_ITEM, "" )
		self.setDropItemsQueryOwner( playerID,  [index] )
		self.setDropItemsPickOwner( playerID, [index] )
		player.clientEntity( self.id ).receiveDropState( self.displayOnClient( playerID ) )

	def rollRandom( self, playerID, index ):
		"""
		define method
		"""
		player = BigWorld.entities.get( playerID )

		if player is None:
			return
		if not playerID in self.rollOwnersDict:
			return

		if not index in self.rollOwnersDict[playerID]:
			return

		if self.queryTemp( "roll_%i_%i"%( index, player.id ), -1 ) != -1:
			return

		point = random.randint( 1, 100 )

		points = self.queryTemp( "roll_%i_points"%index, [] )

		if point in points:
			point -= 1
		points.append( point )
		self.setTemp( "roll_%i_points"%index, points )

		self.setTemp( "roll_%i_%i"%( index, player.id ), point )
		rollDict = self.queryTemp( "rollDict" )
		item = self.__getItem( index )
		itemColor = self.getItemColor( item )
		player.client.onStatusMessage( csstatus.DROP_BOX_SELECT, str( (itemColor, item.name())) )
		for baseMailbox in rollDict[index]:
			baseMailbox.client.onStatusMessage( csstatus.DROP_BOX_OTHER_SELECT, str( ( point, itemColor, item.name(), player.getName() ) )  )
		#player.clientEntity( self.id ).receiverRollValue( index, point )
		player.client.receiverRollValue( index, point, self.id )

#		player.clientEntity( self.id ).closeRollInterface( index )
		for baseMailbox in rollDict[index]:
			if self.queryTemp( "roll_%i_%i"%( index, baseMailbox.id ), -1 ) == -1:
				return
		rollPositions = self.queryTemp( "rollPositions", [] )
		rollPositions.append( index )
		self.setTemp( "rollPositions", rollPositions )
		self.addTimer( 2.0, 0.0, HANDLE_RESULT_CBID )

	def abandonRoll( self, playerID, index ):
		"""
		define method
		放弃ROLL
		"""
		player = BigWorld.entities.get( playerID )

		if player is None:
			return

		if not playerID in self.rollOwnersDict:
			return

		if not index in self.rollOwnersDict[playerID]:
			return

		if self.queryTemp( "roll_%i_%i"%( index, player.id ), 0 ) != 0:
			return

		point = 0
		self.setTemp( "roll_%i_%i"%( index, player.id ), point )
		rollDict = self.queryTemp( "rollDict" )
		item = self.__getItem( index )
		itemColor = self.getItemColor( item )
		for baseMailbox in rollDict[index]:
			baseMailbox.client.onStatusMessage( csstatus.DROP_BOX_FANGQI, str( (player.getName(),itemColor,item.name() )) )
		#BigWorld.entities[srcEntityID].clientEntity( self.id ).closeRollInterface( index )
		BigWorld.entities[playerID].client.closeRollInterface( index, self.id )
		for baseMailbox in rollDict[index]:
			if self.queryTemp( "roll_%i_%i"%( index, baseMailbox.id ), -1 ) == -1:
				return
		rollPositions = self.queryTemp( "rollPositions", [] )
		rollPositions.append( index )
		self.setTemp( "rollPositions", rollPositions )
		self.addTimer( 0.5, 0.0, HANDLE_RESULT_CBID )


	def getItemColor( self, item ):
		"""
		"""
		return str(ItemSystemExp.EquipQualityExp.instance().getColorByQuality( item.getQuality() ))[1:-1]
		

	def insertItem( self, item, ownerID ):
		"""
		for real
		插入一个物品，此物品仅能够被ownerID查看和获得
		"""
		indexs = [self.__addItem( self.itemBox, item )]
		self.setDropItemsQueryOwner( ownerID, indexs )
		self.setDropItemsPickOwner( ownerID, indexs )

