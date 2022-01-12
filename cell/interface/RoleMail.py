# -*- coding: gb18030 -*-
#
# $Id: RoleMail.py,v 1.3 2008-06-02 01:17:03 yangkai Exp $


import BigWorld
import cPickle
from bwdebug import *
import items
import csconst
import csstatus
import csdefine

g_items = items.instance()	# 在创建一个物品时需要

class RoleMail:
	"""
	邮件系统玩家cell端接口
	"""

	def __init__(self):
		"""
		"""
		pass


	def mail_send(self, receiverName, mailType, title, content, money, uids, hasItem, receiverBase, npcId):
		"""
		define method.
		玩家寄信，此接口由base调用，也就是说发送邮件的过程是client -> base -> cell -> mailmanager,
		使用此流程而不使用client -> cell -> mailmanager是因为发送邮件时需要确认收信者是存在的。

		过程：
		　先判断能否获得邮箱NPC，玩家与邮箱距离是否满足要求。是否携带物品处理。邮费处理。最后是把邮件发送到邮件管理器。

		参数：
		@param receiverName: 收信人名字
		@type  receiverName: string
		@param     mailType: 邮件类型
		@type      mailType: int8
		@param        title: 邮件的标题
		@type         title: string
		@param      content: 邮件的内容
		@type       content: string
		@param        money: 邮件包含的金钱
		@type         money: unit32
		@param         uids: 邮件包含的物品的唯一ID
		@type          uids: int64
		@param      hasItem: 表示是否携带了物品数据
		@type       hasItem: int8
		@param receiverBase: 收信人的base mailBox
		@type  receiverBase: mailbox
		@param        npcID: 寄信用到的邮箱id
		@type         npcID: object_id
		"""

		npc = BigWorld.entities.get( npcId ) #是否能获得该npc
		if npc == None:
			ERROR_MSG( "%s: is not find the MailBox!(mail)" % (self.getName()))
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE: #npc距离判定
			ERROR_MSG( "%s: is too far from the MailBox!(mail)" % (self.getName()))
			return

		itemDatas = []

		if hasItem or money > 0:
			if self.iskitbagsLocked(): # 如果背包已上锁，则返回
				self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
				return
			#查看是否获得了物品
			for uid in set(uids):
				item = self.getItemByUid_( uid )
				if item is None:
					ERROR_MSG( "%s: the position in the item blacket is empty!" % self.getName() )
					return
				if not self.canGiveItem( item.id ):
					self.client.onStatusMessage( csstatus.MAIL_ITEM_NOT_ALLOW_TRADE, "" )
					return
				if item.isBinded():
					self.client.onStatusMessage( csstatus.MAIL_ITEM_NOT_BINDED, "" )
					return
				if item.isFrozen():
					self.client.onStatusMessage( csstatus.MAIL_ITEM_USING, "" )
					return
				if item.reqYinpiao() != 0:
					self.client.onStatusMessage( csstatus.MAIL_ITEM_MERCHANT, "" )
					return

				tempDict = item.addToDict()
				del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
				# phw 2009-09-30: 经测试，在172.16.0.8（as 5.3）上，代码直接dumps出来的数据不正确，
				# 会导致一批物品（如“10101001”）发邮件失败，但在控制台上直接dumps却是正确的，
				# 为了保证数据完整性，暂时使用最低效率但最安全的数据dumps方式。
				itemData = cPickle.dumps( tempDict, 0 )	# old: itemData = cPickle.dumps( tempDict, 2 )
				itemDatas.append( itemData )

		# 计算邮资
		# 代码加入人:姜毅 2009-5-27,判断平邮还是快递,不同邮递方式收费标准不同,mailCost参数是邮件类型的收费倍率
		if mailType == csdefine.MAIL_TYPE_QUICK:	# 快递收费是普通邮件总邮费的2倍
			mailCost = 2
		elif mailType == csdefine.MAIL_TYPE_NORMAL:	# 普通信件
			mailCost = 1
		else:
			return

		value = money + ( money * csconst.MAIL_SEND_MONEY_RATE + csconst.MAIL_FARE ) * mailCost
		if len(itemDatas) != 0:
			value += csconst.MAIL_SEND_ITEM_FARE * len( itemDatas ) * mailCost

		# 付邮资
		if self.payMoney( value, csdefine.CHANGE_MONEY_MAIL_SEND ) == False:
			ERROR_MSG( "%s: not have enough money to mail!(mail)" % (self.getName()))
			return

		if len(itemDatas) != 0:
			for uid in uids:
				item = self.getItemByUid_( uid )
				if item.isAlreadyWield() : # 如果将要删除的物品是穿在身上的装备，则先卸下来
					item.unWield( self )
					self.resetEquipModel( item.order, None )
				self.removeItemByUid_( uid, reason = csdefine.DELETE_ITEM_MAIL_SEND )	# 取走邮寄的物品列表

		BigWorld.globalData["MailMgr"].sendWithMailbox(self.base, receiverBase, receiverName, mailType, csdefine.MAIL_SENDER_TYPE_PLAYER, self.getName(), title, content, money, itemDatas)
		
		self.client.onMail_send_successed()
		
	def mail_send_on_air( self, receiverName, mailType, title, content ):
		"""
		define method
		用于角色在某些条件(例如onLevelUp)需要的自动发送邮件用的接口 by姜毅
		@param receiverName: 收信人名字
		@type  receiverName: string
		@param     mailType: 邮件类型
		@type      mailType: int8
		@param        title: 邮件的标题
		@type         title: string
		@param      content: 邮件的内容
		@type       content: string
		"""
		BigWorld.globalData["MailMgr"].send( None, receiverName, mailType, csdefine.MAIL_SENDER_TYPE_NPC, self.getName(), title, content, 0, [] )
		
	def mail_send_on_air_withItems( self, receiverName, mailType, title, content, items ):
		"""
		用于角色在某些条件(例如onLevelUp)需要的自动发送邮件用的接口 by姜毅
		@param receiverName: 收信人名字
		@type  receiverName: string
		@param     mailType: 邮件类型
		@type      mailType: int8
		@param        title: 邮件的标题
		@type         title: string
		@param      content: 邮件的内容
		@type       content: string
		@param items: 物品
		@type     itemslist: list
		"""
		itemDatas = []
		#查看是否获得了物品
		for item in items:
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
			# phw 2009-09-30: 经测试，在172.16.0.8（as 5.3）上，代码直接dumps出来的数据不正确，
			# 会导致一批物品（如“10101001”）发邮件失败，但在控制台上直接dumps却是正确的，
			# 为了保证数据完整性，暂时使用最低效率但最安全的数据dumps方式。
			itemData = cPickle.dumps( tempDict, 0 )	# old: itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )
		BigWorld.globalData["MailMgr"].send( None, receiverName, mailType, csdefine.MAIL_SENDER_TYPE_NPC, self.getName(), title, content, 0, itemDatas )

	def mail_getItem( self,scrEntityID, mailID, npcId, index ):
		"""
		exposed method
		请求获取邮件附带物品

		过程：判断玩家和邮箱的距离后，还要检查玩家背包是否还有空间，接着就可以把玩家想获取邮件物品的请求发送给玩家的base。

		参数
		@param scrEntityID: 隐含传送的调用此接口的实体ID
		@type  scrEntityID: object_id
		@param      mailID: 邮件的DBID
		@type       mailID: DATABASE_ID
		@param       npcId: 寄信用到的邮箱id
		@type        npcId: object_id


		"""
		if scrEntityID != self.id:
			ERROR_MSG( "%s: cell is call by %i! (mail)" % (self.getName(), scrEntityID))
			return

		npc = BigWorld.entities.get( npcId ) #是否能获得该npc
		if npc == None:
			ERROR_MSG( "%s: is not find the MailBox!(mail)" % (self.getName()))
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE: #npc距离判定
			ERROR_MSG( "%s: is too far from the MailBox!(mail)" % (self.getName()))
			return
			
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		self.base.mail_getItem( mailID, index )

	def mail_getAllItem( self,scrEntityID, mailID, npcId ):
		"""
		exposed method
		请求获取邮件全部物品

		过程：判断玩家和邮箱的距离后，还要检查玩家背包是否还有空间，接着就可以把玩家想获取邮件物品的请求发送给玩家的base。

		参数
		@param scrEntityID: 隐含传送的调用此接口的实体ID
		@type  scrEntityID: object_id
		@param      mailID: 邮件的DBID
		@type       mailID: DATABASE_ID
		@param       npcId: 寄信用到的邮箱id
		@type        npcId: object_id


		"""
		if scrEntityID != self.id:
			ERROR_MSG( "%s: cell is call by %i! (mail)" % (self.getName(), scrEntityID))
			return

		npc = BigWorld.entities.get( npcId ) #是否能获得该npc
		if npc == None:
			ERROR_MSG( "%s: is not find the MailBox!(mail)" % (self.getName()))
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE: #npc距离判定
			ERROR_MSG( "%s: is too far from the MailBox!(mail)" % (self.getName()))
			return
			
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		self.base.mail_getAllItem( mailID )

	def mail_receiveItem( self, mailID, itemData, index ):
		"""
		define method
		获取邮件附带物品


		过程：邮件物品数据是由玩家base发送过来的。接着在这里进行正式获得处理。并且还需要在正式获得后，到base和数据库分别记录。

		@param   mailID: 邮件的DBID
		@type    mailID: DATABASE_ID
		@param itemData: 物品的数据
		@type  itemData: string
		"""
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return
			
		itemDict = cPickle.loads( itemData )
		#itemDict = itemDatas[index]
		if len( itemDict ) == 0:
			self.base.mail_getItemRegister( mailID, 0, index )
			return

		item = g_items.createFromDict( itemDict )
		if self.addItemAndNotify_( item, csdefine.ADD_ITEM_RECEIVEITEM ):
			self.base.mail_getItemRegister( mailID, 1, index )
		else:
			self.base.mail_getItemRegister( mailID, 0, index )

	def mail_receiveAllItem( self, mailID, itemDatas ):
		"""
		define method
		获取邮件附带物品


		过程：邮件物品数据是由玩家base发送过来的。接着在这里进行正式获得处理。并且还需要在正式获得后，到base和数据库分别记录。

		@param   mailID: 邮件的DBID
		@type    mailID: DATABASE_ID
		@param itemDatas: 物品的数据
		@type  itemDatas: list of string
		"""
		
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return
			
		itemCount = 0
		successCount = 0
		failedIndexList = []
		for index in xrange( len( itemDatas ) ):
			itemDict = cPickle.loads( itemDatas[index] )
			if len( itemDict ) != 0:
				itemCount += 1
				item = g_items.createFromDict( itemDict )
				if self.addItemAndNotify_( item, csdefine.ADD_ITEM_RECEIVEITEM ):
					successCount += 1
				else:
					failedIndexList.append( index )

		self.base.mail_getAllItemRegister( mailID, 1, failedIndexList )

	def mail_getMoney(self,scrEntityID, mailID, npcId):
		"""
		exposed method
		请求获取邮件附带金钱

		过程：判断玩家和邮箱的距离后，接着就可以把玩家想获取邮件金钱的请求发送给玩家的base。

		参数
		@param scrEntityID: 隐含传送的调用此接口的实体ID
		@type  scrEntityID: object_id
		@param      mailID: 邮件的DBID
		@type       mailID: DATABASE_ID
		@param       npcId: 寄信用到的邮箱id
		@type        npcId: object_id
		"""
		if scrEntityID != self.id:
			ERROR_MSG( "%s: cell is call by %i! (mail)" % (self.getName(), scrEntityID))
			return

		npc = BigWorld.entities.get( npcId ) #是否能获得该npc
		if npc == None:
			ERROR_MSG( "%s: is not find the MailBox!(mail)" % (self.getName()))
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE: #npc距离判定
			ERROR_MSG( "%s: is too far from the MailBox!(mail)" % (self.getName()))
			return
			
		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		self.base.mail_getMoney(mailID)


	def mail_receiveMoney(self, mailID, money):
		"""
		define method
		获取邮件附带金钱


		过程：邮件金钱数据是由玩家base发送过来的。接着在这里进行正式获得处理。并且还需要在正式获得后，到base和数据库分别记录。

		@param mailID: 邮件的DBID
		@type  mailID: DATABASE_ID
		@param  money: 金钱的数据
		@type   money: string

		"""
		#金钱是否超过最高限定
		if self.gainMoney( money, csdefine.CHANGE_MONEY_MAIL_RECEIVEMONEY ) == False:
			self.base.mail_getMoneyRegister(mailID, 0)
			self.client.onStatusMessage( csstatus.CIB_MONEY_OVERFLOW, "" )
			return
		self.base.mail_getMoneyRegister(mailID, 1)

# RoleMail.py
