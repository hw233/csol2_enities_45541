# -*- coding: gb18030 -*-
#
## $Id: RoleMail.py,v 1.5 2008-05-31 03:02:24 yangkai Exp $
###### modified by lzh 2013-6-11 add param readedHintTime, used to flag the mailHint readed or not 

import BigWorld
from bwdebug import *
import csconst
import csstatus
import csdefine
import Time
import items
import cPickle
import event.EventCenter as ECenter
from Function import Functor
from ItemsFactory import ObjectItem as ItemInfo
from gbref import rds
import config.client.labels.RoleMail as lbDatas

g_items = items.instance()
ITEM_BOX_COUNT = 10

class RoleMail:
	"""
	邮件系统玩家cell端接口
	"""

	def __init__( self ):
		"""
		"""
		self.mails = {}				# 客户端保存的所有邮件列表
		self.singleMail = {}		#一封邮件的内容
		self.currentmailID = 0		#当前查看的邮件mailID
		self.npcID = 0
		self.__delaySendCBID = {}	# 当前未到收取时间需要延时发送的邮件的callback ID
		self.mailIndex = -1
		self.mail_checkTimerID = -1

	def enterMailWithNPC( self, objectID ):
		"""
		Define Method
		请求邮件
		@param   objectID: 交易目标
		@type    objectID: OBJECT_ID
		@return: 无
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The trade NPC  %s has not exist " % objectID )
			return
		# 取得邮件列表
		self.mail_checkOutDated()
		ECenter.fireEvent( "EVT_ON_TOGGLE_MAIL_BOX", entity )
		self.npcID = objectID # 此次对话npcID

	def mailOverWithNPC( self ):
		player = BigWorld.player()
		self.npcID = 0

	def mail_send( self, receiverName, mailtype, title, content, money, uids ):
		"""
		过程：
		　先判断邮件标题长度,邮件内容长度是否合格。在记录邮件的信息,并开始查找收信玩家看是否存在。

		参数：
		@param receiverName:	收信人名字
		@type receiverName:		string
		@param mailtype:		邮件类型
		@type mailtype:			int8
		@param title:			邮件的标题
		@type title:			string
		@param content:			邮件的内容
		@type content:			string
		@param money:			邮件包含的金钱
		@type money:			unit32
		@param uids:			邮件包含的物品的唯一ID，如果没有物品则填[]
		@type uids:				int64
		@param npcId:			寄信用到的邮箱id
		@type npcId:			object_id
		"""
		npc = BigWorld.entities.get( self.npcID ) #是否能获得该npc
		if npc == None:
			self.statusMessage(csstatus.MAIL_MAILBOX_NOT_EXIST)
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE: #npc距离判定
			self.statusMessage(csstatus.MAIL_MAILBOX_IS_TOO_FAR)
			ECenter.fireEvent( "EVT_ON_MAIL_SEND_SUCCED", False )
			return

		if len(title) > csconst.MAIL_TITLE_LENGTH_MAX: #标题长度小于13个字检测
			self.statusMessage(csstatus.MAIL_TITLE_TOO_LONG)
			ECenter.fireEvent( "EVT_ON_MAIL_SEND_SUCCED", False )
			return
		
		if rds.wordsProfanity.searchMsgProfanity( title ) is not None:
			self.statusMessage( csstatus.TITLE_HAS_PROFANITY )
			return
		
		if len(content) > csconst.MAIL_CONTENT_LENGTH_MAX: #内容长度小于250个字检测
			self.statusMessage(csstatus.MAIL_CONTENT_TOO_LONG)
			ECenter.fireEvent( "EVT_ON_MAIL_SEND_SUCCED", False )
			return

		if rds.wordsProfanity.searchMsgProfanity( content ) is not None:
			self.statusMessage( csstatus.CONTENT_HAS_PROFANITY )
			return

		hasItem = False

		#tempOrders = []
		if uids != []:			# 表示有物品
			hasItem = True

		self.base.mail_send( receiverName, mailtype, title, content, money, uids, hasItem, self.npcID )

	def mail_checkOutDated( self ):
		"""
		删除超时的GM,npc邮件
		和已经阅读过超过两个小时的邮件
		"""
		if self is not BigWorld.player():
			return
		t = Time.Time.time()
		deleteMailIDs = []
		returnMailIDs = []
		newMailDeleted = False
		for id, mail in self.mails.iteritems():		# 注：由于下面有直接删除self.mails中的item的行为，因此不可以使用iteritems()
			if ( mail["readedTime"] == 0 ) and ( t - mail["receiveTime"] > csconst.MAIL_NPC_OUTTIMED ):
				# 超过期限7天未读的信件需要立即删除（包括退信、NPC信件、GM信件）
				if mail["senderType"] != csdefine.MAIL_SENDER_TYPE_PLAYER:
					# 非玩家发送的邮件
					deleteMailIDs.append( id )
				else:
					# 是玩家发送的信件，这里要处理退信
					# 虽然退信是由服务器统一处理的，但由于服务器的退信检查有一定的时间间隔
					# 如果想要准确，在信件过期的情况下由客户端主动通知一下服务器
					# 有助于保证数据的一致性（无论如何，服务器总是需要从临时列表中删除这封信的）
					returnMailIDs.append( id )


				# 有需要清理的未读邮件
				newMailDeleted = True

			hasItem 	= False
			hasMoney  	= False
			for iItem in mail["items"].values():
				if iItem != None:
					hasItem = True
					break
			if mail["money"] > 0:
				hasMoney = True
			if ( mail["readedTime"] != 0 ):
				#print "readed how long:",t - mail["readedTime"] > csconst.MAIL_READ_OUTTIMED
				if ( not hasItem ) and ( not hasMoney ) and ( t - mail["readedTime"] > csconst.MAIL_READ_OUTTIMED ):
					deleteMailIDs.append( id )
				#print "receive how long:",t - mail["receiveTime"] > csconst.MAIL_NPC_OUTTIMED
				if ( hasItem or hasMoney )and ( t - mail["receiveTime"] > csconst.MAIL_NPC_OUTTIMED ):
					deleteMailIDs.append( id )

#				ECenter.fireEvent( "EVT_ON_MAIL_DEL_LETTER", id ) # 删除过期的信件
		for id in deleteMailIDs:
			self.mail_delete( id )

		for id in returnMailIDs:
			self.base.mail_returnNotifyFC( id )
			del self.mails[id]
			# to do, 这里还需要触发一个退信消息，以更新界面或显示提示退信信息
			ECenter.fireEvent( "EVT_ON_MAIL_DEL_LETTER", id ) #处理玩家退信

		# 检查是否还有未读邮件
		if newMailDeleted and self.hasReadAllMailsHints() :
			ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_HINT_NOTIFY" )  #已经阅读了全部邮件提示，图件图标闪烁消失
		if newMailDeleted and self.hasReadAllMails()  :
			ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_NOTIFY" )

	def mail_read( self, mailID ):
		"""
		阅读一封邮件

		@param mailID: 邮件的DBID
		@type  mailID: uint32
		@param  npcId: 寄信用到的邮箱id
		@type   npcId: object_id
		"""
		npc = BigWorld.entities.get( self.npcID ) #是否能获得该npc
		if npc == None:
			self.statusMessage(csstatus.MAIL_MAILBOX_NOT_EXIST)
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE: #npc距离判定
			self.statusMessage(csstatus.MAIL_MAILBOX_IS_TOO_FAR)
			return

		if not self.mails.has_key( mailID ):
			self.statusMessage( csstatus.MAIL_NOT_EXIST )
			return

		if self.mails[mailID]["receiveTime"] > Time.Time.time():
			self.statusMessage( csstatus.MAIL_NOT_EXIST )			# 还没有到收信时间，当信不存在
			return
		isNewMail = False
		if not self.hasReadAllMails() :
			isNewMail = True
		isNewMailHint = False
		if not self.hasReadAllMailsHints() :
			isNewMailHint = True 
		if isNewMail :												# 读取了一封未读取过的邮件
			self.mails[mailID]["readedTime"] = Time.Time.time()
			self.base.mail_readedNotify( mailID )
			self.mails[mailID]["readedHintTime"] =Time.Time.time()
			self.base.mailHint_readedNotify( mailID )
		ECenter.fireEvent( "EVT_ON_MAIL_READ_LETTER", mailID ) 		# 阅读邮件
		
		if isNewMail and self.hasReadAllMails() :        #已经阅读了全部邮件，邮件图标消失
			ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_NOTIFY" )
			ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_HINT_NOTIFY" )  #已经阅读了全部邮件提示，图件图标闪烁消失
		if isNewMail and self.hasReadAllMailsHints() :
			ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_HINT_NOTIFY" )  #已经阅读了全部邮件提示，图件图标闪烁消失
			
			
			
		# to do, 在这里加入处理请求读取邮件的代码
		# 可以考虑触发一个收到邮件内容的消息，
		# 或改变一下函数名(如：mail_get())，直接返回邮件内容。
		return
	
	
	"""
	def mailHint_readedNotify ( self, mailID ) :
		self.base.mailHint_readedNotify( mailID )
	"""
	def mail_query( self ):
		"""
		查看所有邮件总体信息
		邮件的内容都放在本地,所以查看的时候,直接根据需要来 解读 self.mails{}
		"""
		self.mails= {}
		self.base.mail_queryAll()	#上线即获得所有邮件的简要信息

	def mail_delete(self, mailID):
		"""
		@param mailID: 邮件的DBID
		@type  mailID: DATABASE_ID
		"""
		if not self.mails.has_key( mailID ):
			return

		self.base.mail_delete(mailID)

	def mail_getItem( self, mailID, index ):
		"""
		申请获取邮件物品
		@param mailID: 邮件的DBID
		@type  mailID: DATABASE_ID
		@param  npcId: 寄信用到的邮箱id
		@type   npcId: object_id
		"""
		npc = BigWorld.entities.get( self.npcID ) #是否能获得该npc
		if npc == None:
			self.statusMessage(csstatus.MAIL_MAILBOX_NOT_EXIST)
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:	# npc距离判定
			self.statusMessage(csstatus.MAIL_MAILBOX_IS_TOO_FAR)
			return

		if not self.mails.has_key( mailID ):
			self.statusMessage(csstatus.MAIL_NOT_EXIST)
			return

		if self.getNormalKitbagFreeOrderCount() < 1:
			self.statusMessage( csstatus.PCU_NOT_ENOUGH_GRID )
			return

		if self.mailHasItemConut( mailID ) == 0:
			# 该邮件没有物品
			return

		self.cell.mail_getItem( mailID, self.npcID, index )

	def mail_getAllItem( self, mailID ):
		"""
		对邮件物品进行 全部领取
		@param mailID: 邮件的DBID
		@type  mailID: DATABASE_ID
		@param  npcId: 寄信用到的邮箱id
		@type   npcId: object_id
		"""
		npc = BigWorld.entities.get( self.npcID ) #是否能获得该npc
		if npc == None:
			self.statusMessage(csstatus.MAIL_MAILBOX_NOT_EXIST)
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:	# npc距离判定
			self.statusMessage(csstatus.MAIL_MAILBOX_IS_TOO_FAR)
			return

		if not self.mails.has_key( mailID ):
			self.statusMessage(csstatus.MAIL_NOT_EXIST)
			return

		mailItemNum = self.mailHasItemConut( mailID )
		if mailItemNum == 0:
			# 该邮件没有物品
			return

		if self.getNormalKitbagFreeOrderCount() < mailItemNum:
			self.statusMessage( csstatus.PCU_NOT_ENOUGH_GRID )
			return

		self.cell.mail_getAllItem( mailID, self.npcID )

	def mail_getMoney( self, mailID ):
		"""
		申请领取邮件金钱
		@param mailID: 邮件的DBID
		@type  mailID: DATABASE_ID
		@param  npcId: 寄信用到的邮箱id
		@type   npcId: object_id
		"""
		npc = BigWorld.entities.get( self.npcID ) #是否能获得该npc
		if npc == None:
			self.statusMessage(csstatus.MAIL_MAILBOX_NOT_EXIST)
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE: #npc距离判定
			self.statusMessage(csstatus.MAIL_MAILBOX_IS_TOO_FAR)
			return

		if not self.mails.has_key( mailID ):
			self.statusMessage(csstatus.MAIL_NOT_EXIST)
			return

		if self.mails[mailID]["money"] <= 0:
			# 该邮件没有金钱
			return

		self.cell.mail_getMoney( mailID, self.npcID )
		self.mails[mailID]["money"] = 0

	def mail_receive( self, mailID, title, senderName, receiverName, senderType, receiveTime, readedTime, content, money, itemDatas, readedHintTime ):
		"""
		define method
		收取邮件
		作用：玩家登陆的时候,通过申请获得 self.base.mail_queryAll()来请求获得邮件数据,而这个函数就是用于接收邮件数据的。
		另外有这个玩家新邮件的时候,也通过这个函数把新邮件通知玩家。

		考虑：	这里有一个问题存在，由于玩家在线的时候，邮个无论是否到了收信时间，都已经发送给客户端，
				也就是说，如果玩家破解了客户端就可以任意时候查看信件内容。我的想法是，邮件主要功能在于
				它可以发送金钱和物品，如果不可以发送金钱和物品，那么应该没有什么人会主动去用邮件，即然
				如此，那么我们只要保证金钱和物品的获取时间正确，那么玩家在客户端是否能看得见邮件内容并
				不是很重要，数据放在客户端反而能增加客户端的表现性。

		@param      mailID: 邮件的DBID
		@type       mailID: DATABASE_ID
		@param       title: 寄信用到的邮箱id
		@type        title: string
		@param  senderName: 发信人
		@type   senderName: string
		@param  senderType: 寄信用到的邮箱id
		@type   senderType: string
		@param receiveTime: 收信时间
		@type  receiveTime: string
		@param  readedTime: 信件读取时间
		@type   readedTime: string
		@param     content: 邮件的内容
		@type      content: string
		@param       money: 邮件附带的金钱数目
		@type        money: string
		@param    itemDatas: 邮件附带物品列表的数据
		@type     itemDatas: array of string
		"""
		#退信标题格式处理 添加参数 recieverName by姜毅
		interval = int( receiveTime - Time.Time.time() )
		if interval > 0 :
			func = Functor( self.mail_receive, mailID, title, senderName, receiverName, senderType, receiveTime, readedTime, content, money, itemDatas, readedHintTime )
			self.__delaySendCBID[mailID] = BigWorld.callback( interval, func )
			return

		if mailID in self.__delaySendCBID :
			del self.__delaySendCBID[mailID]

		items = {}
		itemIndex = 0
		for iItemData in itemDatas:
			itemDict = cPickle.loads( iItemData )
			if len( itemDict ) == 0:
				item = None
			else:
				item = g_items.createFromDict( itemDict )
			items[itemIndex] = item
			itemIndex += 1

		mail = {
				"mailID"		: mailID,
				"title"			: title,
				"senderNamer"	: senderName,
				"senderType"	: int( senderType ),
				"receiveTime"	: int( receiveTime ),
				"readedTime"	: int( readedTime ),				
				"content"		: content,
				"items"			: items,
				"money"			: int( money ),
				"readedHintTime": int( readedHintTime ),
				}
		self.mails[mailID] = mail
		#退信标题处理 by姜毅
		if self.mails[mailID]["senderType"]  == csdefine.MAIL_SENDER_TYPE_RETURN:
			self.mails[mailID]["title"] = lbDatas.WITHDRAW_TITLE % ( receiverName, self.mails[mailID]["title"] )
			#self.mails[mailID]["readedTime"] = 0
			#self.mails[mailID]["readedHintTime"] = 0
			#self.base.mail_returnNotifyFC( mailID ) #退信时，修改readedTime，readedHintTime
		self.mailIndex += 1
		#
		ECenter.fireEvent( "EVT_ON_MAIL_ADD_LETTER", self.mailIndex, mail )# 向界面发送邮件实例
		if mail["readedTime"] == 0 :
			ECenter.fireEvent( "EVT_ON_NOTIFY_NEW_MAIL" )
	
	
	
	
	def mail_moneyHasGotten( self, mailID ):
		"""
		define method.
		由服务器调用，通知客户端，某个邮件的金钱已成功取走
		"""
		if mailID not in self.mails:
			return
		self.mails[mailID]["money"] = 0
		# to do, 这里触发金钱取走的消息，以更新界面
		ECenter.fireEvent( "EVT_ON_MAIL_HAS_GETTTEN_MONEY", mailID )
		ECenter.fireEvent( "EVT_ON_MAIL_UPDATE_LETTER", mailID )
	#	ECenter.fireEvent( "EVT_ON_MAIL_HAS_GETTEN_ALL_ITEMS", mailID)

	def mail_itemHasGotten( self, mailID, index ):
		"""
		define method.
		由服务器调用，通知客户端，某个邮件的物品已成功取走
		"""
		if mailID not in self.mails:
			return
		#if len(self.mails[mailID]["items"]) < index:
		#	return
		self.mails[mailID]["items"][index] = None
		# to do, 这里触发物品取走的消息，以更新界面
		ECenter.fireEvent( "EVT_ON_MAIL_HAS_GETTEN_ITEM", mailID, index )

	def mail_itemAllHasGotten( self, mailID, failedIndexList ):
		"""
		define method.
		由服务器调用，通知客户端，邮件的所有物品都已成功取走
		"""
		if mailID not in self.mails:
			return

		#itemList = self.mails[mailID]["items"]

		if self.mailHasItemConut( mailID ) == 0:
			# 如果邮件中没有物品
			return
		newItemList = []
		for index in xrange( 10 ):
			if not index in failedIndexList:
				self.mails[mailID]["items"][index] = None
		# to do, 这里触发物品取走的消息，以更新界面
		if self.mails[mailID]["money"] != 0 :
			self.mail_moneyHasGotten(mailID)
		ECenter.fireEvent( "EVT_ON_MAIL_HAS_GETTEN_ALL_ITEMS", mailID, failedIndexList )
		#ECenter.fireEvent( "EVT_ON_MAIL_HAS_GETTTEN_MONEY", mailID )

	def addSendItem( self, item ):
		player = BigWorld.player()
		if item is not None:
			kitbagID = item.kitbagID
			orderID = item.gbIndex
			orderID = orderID + kitbagID * csdefine.KB_MAX_SPACE
			item = player.getItem_( orderID )
			itemInfo = ItemInfo( item )
			ECenter.fireEvent( "EVT_ON_MAIL_ADD_SENDITEM", itemInfo )

	def removeSendItem( self ):
		ECenter.fireEvent( "EVT_ON_MAIL_DEL_SENDITEM", None )


	def mail_systemReturn( self, mailID ):
		"""
		exposed method
		超时信件触发的系统自动退信,而且这个退信只是处理收信人的界面信息及client和base上保存的信息的更新，并不会真正删除数据库的信件
		"""
		self.onMailDeleted( mailID )
		
	def onMailDeleted( self, mailID ):
		"""
		define method
		服务器删除邮件成功后通知客户端删除相应邮件
		"""
		# to do, 在这里触发一个某封邮件已删除的消息，以让界面更新
		# 如果由界面主动调用的其实可以不需要这个触发消息，
		# 但我们还有其它的行为会导致信件的删除，因此需要在这里触发消息

		isNewMail = self.mails[mailID]["readedTime"] == 0
		del self.mails[mailID]
		ECenter.fireEvent( "EVT_ON_MAIL_DEL_LETTER", mailID ) # 玩家请求删除邮件
		self.mailIndex -= 1
		if isNewMail and self.hasReadAllMails() :
			ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_NOTIFY" )
			ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_HINT_NOTIFY" )  #已经阅读了全部邮件提示，图件图标闪烁消失			

	def hasReadAllMails( self ) :
		"""
		检查是否已读取全部邮件
		"""
		for mail in self.mails.itervalues() :
			if mail["readedTime"] == 0 :				# 仍有未读邮件
				return False
		return True
	
	def hasReadAllMailsHints( self ) :
		"""
		检查是否已读取全部邮件提醒
		"""
		for mail in self.mails.itervalues() :
			if mail["readedHintTime"] == 0 :				# 仍有未读邮件
				return False
		return True

	def clearMailbox( self ) :
		"""
		角色离开游戏时调用
		"""
		ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_NOTIFY" )
		#ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_HINT_NOTIFY" )  
		self.__clearDelaySendCBID()
		self.mailIndex = -1
		if self.mail_checkTimerID != -1:
			BigWorld.cancelCallback( self.mail_checkTimerID )

	def initMailbox( self ) :
		"""
		向服务器申请所有邮件，进入游戏时调用
		"""
		self.mail_query() 								# 请求邮件
		self.mail_checkTimerID = BigWorld.callback( csconst.MAIL_CHECK_OUTDATED_REPEAT_TIME, self.mail_checkOutDated )
		
		#登录时邮件图标显示的状态	
		player = BigWorld.player()
		if not player.hasReadAllMails() :
			if player.hasReadAllMailsHint() :
				ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_HINT_NOTIFY" ) 
	


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __clearDelaySendCBID( self ) :
		"""
		取消所有延时发送邮件的Callback ID, 不再发送
		"""
		for CBID in self.__delaySendCBID.itervalues() :
			BigWorld.cancelCallback( CBID )
		self.__delaySendCBID = {}

	def mailHasItemConut( self, mailID ):
		"""
		邮件中有多少个物品
		"""
		itemCount = 0
		for item in self.mails[mailID]["items"].itervalues():
			if item is not None:
				itemCount += 1
		return itemCount

	def onMail_send_successed( self ):
		"""
		define method
		"""
		ECenter.fireEvent( "EVT_ON_MAIL_SEND_SUCCED", True )