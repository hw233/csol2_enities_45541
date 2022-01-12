# -*- coding: gb18030 -*-
#
## $Id: RoleMail.py,v 1.2 2008-03-06 09:01:16 fangpengjun Exp $
###### modified by lzh 2013-6-11 add param readedHintTime, used to flag the mailHint readed or not 

import BigWorld
from bwdebug import *
from MsgLogger import g_logger
import csstatus
import csconst
import csdefine
import cPickle
from Function import Functor
from time import time
import ECBExtend
import config.client.labels.RoleMail as lbDatas

class RoleMail:


	def __init__(self):
		"""
		"""
		# 玩家的邮件列表（包括可看的和不可看的）；
		# key = databaseID of mail
		# value = [ sm_title, sm_content, sm_item0, sm_item1, sm_item2, sm_item3, sm_item4, sm_item5, sm_item6, sm_item7, sm_item8, sm_item9,sm_money, sm_senderName, sm_receiverName, sm_senderType, sm_receiveTime, sm_readedTime ]
		self.mail_allInfo = {}
		self.mail_initingCtrlID = 0		# 初始化邮件数据到客户端时的timerID
		self.mail_initingmailIDs = []	# 初始化邮件数据到客户端时的邮件ID列表，使用此列表的原因是在初始化的过程中很可能会增加新的邮件，避免出现混乱。

		self.mail_sendInfo = {}			# 临时存储要发送的邮件的信息
		self.mail_sending = False		# 临时标记，用于阻止连续发送多封邮件而导致邮件数据的不正确
		self.mail_returnInfo = {}       # 临时存储要退信的邮件的信息 by姜毅


	def mail_send(self, receiverName, mailType, title, content, money, uids, hasItem, npcID):
		"""
		exposed method.
		玩家寄信，主要用于给客户端调用

		过程：
		　先判断邮件标题长度，邮件内容长度是否合格。在记录邮件的信息，并开始查找收信玩家看是否存在。

		参数：
		@param receiverName:收信人名字
		@type receiverName:	string
		@param mailType:	邮件类型
		@type mailType:		int8
		@param title:		邮件的标题
		@type title:		string
		@param content:		邮件的内容
		@type content:		string
		@param money:		邮件包含的金钱
		@type money:		unit32
		@param uids:		邮件包含的物品的唯一ID
		@type uids:			int64
		@param hasItem:		表示是否携带了物品数据
		@type hasItem:		int8
		@param npcID:		寄信用到的邮箱id
		@type npcID:		object_id
		"""

		# 不允许同时发送多封信件，以避免出现后来的信件内容覆盖前面的信件内容
		if self.mail_sending:
			return

		# 不允许给自己寄信
		if receiverName == self.getName():
			return

		if len(title) > csconst.MAIL_TITLE_LENGTH_MAX:		# 标题长度小于20个字检测
			return

		if len(content) > csconst.MAIL_CONTENT_LENGTH_MAX:	# 标题长度小于400个字检测
			return

		self.mail_sendInfo = {	"receiverName" 	: receiverName,
								"npcID" 		: npcID,
								"mailType" 		: mailType,
								"title" 		: title,
								"content" 		: content,
								"money" 		: money,
								"uids" 			: uids,
								"hasItem" 		: hasItem,
							}

		self.mail_sending = True
		BigWorld.lookUpBaseByName( "Role", receiverName, self._mail_getPlayerMailboxCb)


	def _mail_getPlayerMailboxCb( self, callResult ):
		"""
		寄信过程中通过收信人名字查找收信人是否存在，以及在线情况的回调函数

		前面参数同 sendItemSuccess

		@param callResult:	BigWorld.lookUpBaseByName的查找结果,mailbox、True、False都有可能
		@type callResult:	MAILBOX OR BOOL
		"""
		# 返回一个mailbox时,表示找到玩家且在线
		if not isinstance( callResult, bool ):		# isinstance函数见python手册
			playerBase = callResult
		elif callResult == True:
			playerBase = None
		else:
			self.client.onStatusMessage( csstatus.MAIL_RECEIVER_NOT_FOUND, "" )
			self.mail_sending = False
			return

		# 查询玩家邮件数量
		query = "select count(*) from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % ( BigWorld.escape_string( self.mail_sendInfo["receiverName"] ), csdefine.MAIL_SENDER_TYPE_RETURN )
		BigWorld.executeRawDatabaseCommand( query, Functor(self._mail_queryCountForCheckCb, playerBase) )

	def _mailReturn_getPlayerMailboxCb( self, callResult ):
		"""
		寄信过程中通过收信人名字查找收信人是否存在，以及在线情况的回调函数

		前面参数同 sendItemSuccess

		@param callResult:	BigWorld.lookUpBaseByName的查找结果,mailbox、True、False都有可能
		@type callResult:	MAILBOX OR BOOL
		"""
		if not isinstance( callResult, bool ):		# isinstance函数见python手册
			playerBase = callResult
		elif callResult == True:
			playerBase = None
		else:
			self.client.onStatusMessage( csstatus.MAIL_RECEIVER_NOT_FOUND, "" )
			self.mail_sending = False
			return

		# 查询玩家邮件数量 此函数modified by姜毅
		query = "select count(*) from custom_MailTable where sm_receiverName = '%s'" % (BigWorld.escape_string( self.mail_returnInfo["senderName"] ) )
		BigWorld.executeRawDatabaseCommand( query, Functor(self._mail_queryCountForReturnCheckCb, playerBase) )

	def _mail_queryCountForCheckCb(self, playerBaseMailBox, result, dummy, errstr):
		"""
		查询收件人邮件数目的回调函数。如果这个函数的到的邮件数目也不超过规定数目， 则继续将邮件发送到玩家的cell

		@param playerBaseMailBox:	收信人的base MailBox
		@type playerBaseMailBox:	mailbox
		"""
		self.mail_sending = False
		
	
		if int(result[0][0]) >= csconst.MAIL_UPPER_LIMIT:
			self.client.onStatusMessage( csstatus.MAIL_RECEIVER_MAILBOX_FULL, "" ) # 收件人信箱已满的通知
			return

		self.cell.mail_send(	self.mail_sendInfo["receiverName"], \
								self.mail_sendInfo["mailType"], \
#								self.mail_sendInfo["senderType"], \
								self.mail_sendInfo["title"], \
								self.mail_sendInfo["content"], \
								self.mail_sendInfo["money"], \
								self.mail_sendInfo["uids"], \
								self.mail_sendInfo["hasItem"], \
								playerBaseMailBox,\
								self.mail_sendInfo["npcID"] )

	def _mail_queryCountForReturnCheckCb(self, playerBaseMailBox, result, dummy, errstr):
		"""
		查询收件人邮件数目的回调函数。如果这个函数的到的邮件数目也不超过规定数目， 则继续将邮件发送到玩家的cell

		@param playerBaseMailBox:	收信人的base MailBox
		@type playerBaseMailBox:	mailbox
		"""
		self.mail_sending = False
		#此函数modified by姜毅
		if int(result[0][0]) >= csconst.MAIL_UPPER_LIMIT:
			self.client.onStatusMessage( csstatus.MAIL_RECEIVER_MAILBOX_FULL, "" ) # 收件人信箱已满的通知
			self.client.onStatusMessage( csstatus.MAIL_RETURN_FAILED, "" ) # 退信失败			
			return
		BigWorld.globalData["MailMgr"].returnMail( self, self.getName(), self.mail_returnInfo["id"] )

		#加入退信提示 by姜毅
		mailInfo = self.mail_returnInfo
		if mailInfo["senderType"] == csdefine.MAIL_SENDER_TYPE_RETURN:
			return
		self.client.onStatusMessage( csstatus.MAIL_RETURN_TO, str(( mailInfo["senderName"], )) ) # 退信成功

	def mail_queryAll(self):
		"""
		exposed method
		查询邮件，主要用于玩家登陆上线时，一次性查询所有邮件所用。
		"""
		# 查询所有收信者是玩家的非退信类型及发信者是玩家的退信类型的信件
		self.mail_allInfo = {}
		query = "select id, sm_title, sm_content, sm_item0, sm_item1, sm_item2, sm_item3, sm_item4, sm_item5, sm_item6, sm_item7, sm_item8, sm_item9, sm_money, sm_senderName, sm_receiverName, sm_senderType, UNIX_TIMESTAMP(sm_receiveTime), UNIX_TIMESTAMP(sm_readedTime), UNIX_TIMESTAMP(sm_readedHintTime) from custom_MailTable where (sm_receiverName = '%s' and sm_senderType != %i) or (sm_senderName = '%s' and sm_senderType = %i)" % (BigWorld.escape_string( self.getName() ), csdefine.MAIL_SENDER_TYPE_RETURN, BigWorld.escape_string( self.getName() ), csdefine.MAIL_SENDER_TYPE_RETURN)
		BigWorld.executeRawDatabaseCommand( query, self._mail_queryAllCb )


	def _mail_queryAllCb(self, result, dummy, errstr):
		"""
		查询所有邮件数据的回调函数。获得所有邮件数据之后，本地保留一份。同时把每封邮件的部分数据发送到客户端。
		所有邮件数据包括： 邮件DBID， 邮件标题， 邮件内容， 邮件包含物品， 邮件包含金钱， 寄信人的名字， 收信人的名字。
						   邮件物品是否收取， 邮件金钱是否收取， 邮寄时间， 读信时间。
		"""
		if errstr:
			ERROR_MSG(errstr)
			return

		for	m in result:
			#id, title, content, item, money, senderName, receiverName, senderType, receiveTime, readedTime
			id = long( m[0] )
			mail = {	"title"			: m[1],
						"content"		: m[2],
						"money"			: int( m[13] ),
						"senderName"	: m[14],
						"receiverName"	: m[15],
						"senderType"	: int( m[16] ),
						"receiveTime"	: int( m[17] ),
						"readedTime"	: int( m[18] ),
						"readedHintTime": int( m[19] ),
						"itemTaken"		: 0,				# 用于临时记录当前是否正在拿取邮件物品
						"moneyTaken"	: 0,				# 用于临时记录当前是否正在拿取邮件金钱
					}

			"""
						#"itemDatasStr"	: m[3],
						"itemDataStr0"	: m[3],
						"itemDataStr1"	: m[4],
						"itemDataStr2"	: m[5],
						"itemDataStr3"	: m[6],
						"itemDataStr4"	: m[7],
						"itemDataStr5"	: m[8],
						"itemDataStr6"	: m[9],
						"itemDataStr7"	: m[10],
						"itemDataStr8"	: m[11],
						"itemDataStr9"	: m[12],
			"""

			mail["itemDatas"] =  [ m[3],m[4],m[5],m[6],m[7],m[8],m[9],m[10],m[11],m[12] ]
			if mail["readedTime"] == 0 and \
				time() - mail["receiveTime"] > csconst.MAIL_NPC_OUTTIMED and \
				mail["senderType"] == csdefine.MAIL_SENDER_TYPE_PLAYER:
				# 玩家发送的信件已超过7天未读，直接忽略，由mail manager统一进行退信处理
				# 这里需要忽略是因为退信是定期的执行行为（每隔一段时间执行一次）
				continue
			self.mail_allInfo[id] = mail

		if len( self.mail_allInfo ):
			self.mail_initingmailIDs = self.mail_allInfo.keys()
			self.mail_initingmailIDs.sort()
			# 每0.1秒发一次信件给客户端
			self.mail_initingCtrlID = self.addTimer( 1, 0.1, ECBExtend.INIT_MAIL_TO_CLIENT_TIMER_CBID )

	def mail_delete(self, mailID):
		"""
		exposed method
		删除某封邮件邮件

		删除邮件除了到数据库中去删除之外，还要删除base里面的该封邮件信息。

		@param mailID: 邮件的dbid
		@type  mailID: DATABASE_ID
		"""
		try:
			senderName = self.mail_allInfo[mailID]["senderName"]
			receiverName = self.mail_allInfo[mailID]["receiverName"]
			title = self.mail_allInfo[mailID]["title"]
			del self.mail_allInfo[mailID]
			# 通知客户端删除数据
			self.client.onMailDeleted( mailID )
		except:
			self.client.onStatusMessage(csstatus.MAIL_NOT_EXIST, "")
			return
		try:
			g_logger.mailRemoveLog( senderName, receiverName, title, mailID )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		query = "delete from custom_MailTable where id = %i " %( mailID )
		BigWorld.executeRawDatabaseCommand( query, self._mail_deleteCb )


	def _mail_deleteCb(self, result, dummy, errstr):
		"""
		删除某封邮件回调函数。如果删除失败只是在日志中记录这个失败的操作，并没有其他特别处理。
		"""
		if errstr:
			ERROR_MSG(errstr)


	def mail_newNotify(self, senderName, timeFlag):
		"""
		define method
		通知有新邮件。这是当有人给当前玩家寄信的时候被调用。一般由MailManager调用。
		接到新邮件通知的时候,当前玩家到数据库中去查找新的邮件。
		phw: 注：以后如果有更好的获取新邮件的方法，就需要修改

		@param senderName: 发信者的名称，用于查找过滤
		@type  senderName: STRING
		@param   timeFlag: 发信时间标记，用于查找过滤
		@type    timeFlag: INT32
		"""
		# 搜索属于我的邮件，且发送且是senderName而发送时间为timeFlag的信件，
		# 虽然这样搜索在极短的情况下有可能会有多条，但在回调用会进行处理。
		query = "select id, sm_title, sm_content, sm_item0, sm_item1, sm_item2, sm_item3, sm_item4, sm_item5, sm_item6, sm_item7, sm_item8, sm_item9, sm_money, sm_senderName, sm_receiverName, sm_senderType, UNIX_TIMESTAMP(sm_receiveTime), UNIX_TIMESTAMP(sm_readedTime), UNIX_TIMESTAMP(sm_readedHintTime) from custom_MailTable where sm_receiverName = '%s' and sm_senderName = '%s' and sm_timeFlag = %i;" % (BigWorld.escape_string( self.getName() ), BigWorld.escape_string( senderName ), timeFlag)
		INFO_MSG( "%s(%i): sql cmd: %s" % ( self.getName(), self.id, query ) )
		BigWorld.executeRawDatabaseCommand( query, self._mail_newNotifyCb ) # 记录到数据库

	def _mail_newNotifyCb(self, result, dummy, errstr):
		"""
		通知有新邮件回调函数.
		这个回调函数把从数据库读取到的新邮件放入到base的邮件信息中。
		同时还把新邮件部分数据发送到客户端。
		"""
		if errstr:
			ERROR_MSG( "%s(%i): %s" % ( self.getName(), self.id, errstr ) )
			return

		for m in result:
			id = long( m[0] )
			if id in self.mail_allInfo:
				continue	# 对于已经存在于列表中的邮件，我们采取忽略态度（这种情况在极端的状态是会发生的）
			# m[] == id, title, content, item, money, senderName, receiverName, senderType, receiveTime, readedTime
			self.mail_allInfo[id] = {	"title"			: m[1],
										"content"		: m[2],
										"itemDatas"		: [ m[3], m[4], m[5], m[6], m[7], m[8], m[9], m[10], m[11], m[12] ],
										"money"			: int( m[13] ),
										"senderName"	: m[14],
										"receiverName"	: m[15],
										"senderType"	: int( m[16] ),
										"receiveTime"	: int( m[17] ),
										"readedTime"	: int( m[18] ),
										"readedHintTime": int( m[19] ),
										"itemTaken"		: 0,				# 用于临时记录当前是否正在拿取邮件物品
										"moneyTaken"	: 0,				# 用于临时记录当前是否正在拿取邮件金钱
									}
			mail = self.mail_allInfo[id]
			# id, title, senderName, senderType, receiveTime, readedTime, content, money, itemDatas
			self.client.mail_receive( id, mail["title"], mail["senderName"], mail["receiverName"],
										mail["senderType"], mail["receiveTime"], mail["readedTime"],
										mail["content"], mail["money"], mail["itemDatas"], mail["readedHintTime"] )

	def mail_addReturnMail(self, id, title, content, itemDatasStr, money, senderName, receiverName, senderType, receiveTime, readedTime, readedHintTime):
		"""
		define method
		收到退信处理
		"""
		itemDatas = cPickle.loads( itemDatasStr )
		self.mail_allInfo[id] = {	"title"			: title,
									"content"		: content,
									"itemDatas"		: itemDatas,
									"money"			: money,
									"senderName"	: senderName,
									"receiverName"	: receiverName,
									"senderType"	: senderType,
									"receiveTime"	: receiveTime,
									"readedTime"	: readedTime,
									"readedHintTime": readedHintTime,
									"itemTaken"		: 0,				# 用于临时记录当前是否正在拿取邮件物品
									"moneyTaken"	: 0,				# 用于临时记录当前是否正在拿取邮件金钱
								}
		#id, title, senderName, senderType, receiveTime, readedTime, content, money, itemDatas

		self.client.mail_receive( id, title, senderName, receiverName, senderType, receiveTime, readedTime, content, money, itemDatas, readedHintTime )
		#del self.mail_allInfo[mailID]
		#del self.mail_returnInfo[mailID]
		
	
	def mail_readedNotify( self, mailID ):
		"""
		exposed method
		邮件已阅读通知。此方法由客户端调用，告诉自己，某一封邮件已读过

		参数：
		@param mailID: 邮件的dbid
		@type  mailID: DATABASE_ID
		"""
		if mailID not in self.mail_allInfo:
			ERROR_MSG( "error: %s(%i)No such mailID! the id is: %i " % ( self.getName(), self.id, mailID ))
			return

		mailInfo = self.mail_allInfo[mailID]
		if mailInfo["receiveTime"] > time(): # 还没到阅读时间
			ERROR_MSG( "error: The mail is not come! the id is: %i " % ( mailID ))
			return

		if mailInfo["readedTime"] == 0:		# 没有看过，置数据的查看时间
			mailInfo["readedTime"] = time()
			mailInfo["readedHintTime"] = time()
			query = "update custom_MailTable set sm_readedTime = now(), sm_readedHintTime = now() where id = %i." % (mailID)
			BigWorld.executeRawDatabaseCommand( query, Functor(self._mail_readedCb, mailID) )
	

	def mailHint_readedNotify( self, mailID ) :
		"""
		exposed method
		邮件提示已阅读通知。此方法由客户端调用，告诉自己，某一封邮件已读过

		参数：
		@param mailID: 邮件的dbid
		@type  mailID: DATABASE_ID
		"""	
		mailInfo = self.mail_allInfo[mailID]
		if mailID not in self.mail_allInfo:
			ERROR_MSG( "error: %s(%i)No such mailID! the id is: %i " % ( self.getName(), self.id, mailID ))
			return

		if mailInfo["readedHintTime"] == 0 :		# 没有看过邮件提示，置数据的查看时间
			mailInfo["readedHintTime"] = time()
			query = "update custom_MailTable set  sm_readedHintTime = now() where id = %i." % ( mailID )
			BigWorld.executeRawDatabaseCommand( query, Functor(self._mailHint_readedCb, mailID) )		
	
	def _mail_readedCb(self, mailID, result, dummy, errstr):
		"""
		阅读邮件回调函数。
		这个函数主要是说明阅读邮件后，写数据库是否正常，如果不正常，把不正常的邮件ID记录下来。
		本身并没有什么处理。
		"""
		if errstr:
			ERROR_MSG( "write mail readed flag fault! the id is: %i " % ( mailID ) )
			return 
		
		#print "_mail_readedCb",result
	#	self.client.onReadResult( result )
		
		try:
			g_logger.mailReadLog( self.mail_allInfo[mailID]["senderName"], self.mail_allInfo[mailID]["receiverName"], self.mail_allInfo[mailID]["title"], mailID )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
	
	def _mailHint_readedCb(self, mailID, result, dummy, errstr):
		"""
		阅读邮件提示回调函数。
		这个函数主要是说明阅读邮件提示后，写数据库是否正常，如果不正常，把不正常的邮件ID记录下来。
		本身并没有什么处理。
		"""
		if errstr:
			ERROR_MSG( "write mail readed flag fault! the id is: %i " % ( mailID ) )
		try:
			g_logger.mailReadLog( self.mail_allInfo[mailID]["senderName"], self.mail_allInfo[mailID]["receiverName"], self.mail_allInfo[mailID]["title"], mailID )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def mail_getItem( self, mailID, index ):
		"""
		define method
		玩家取邮件物品。

		过程：玩家取邮件附带物品，走到这一步，就是直接从玩家base的邮件数据中取出邮件物品。并把物品发送给
		玩家cell。

		参数：
		@param mailID: 邮件的dbid
		@type  mailID: DATABASE_ID
		"""
		if mailID not in self.mail_allInfo:
			ERROR_MSG( "error: No such mailID! the id is: %i " % ( mailID ))
			return

		mailInfo = self.mail_allInfo[mailID]
		if mailInfo["receiveTime"] > time():		# 还没到阅读时间
			ERROR_MSG( "error: The mail is not come! the id is: %i " % ( mailID ))
			return

		if len( mailInfo["itemDatas"] ) == 0:				# 该邮件没有物品
			ERROR_MSG( "error: The mail has no item ! the id is: %i " % ( mailID ))
			return

		if mailInfo["itemTaken"] == 1:				# 物品正在取出中
			ERROR_MSG( "error: The item has been Taken! the id is: %i " % ( mailID ))
			return

		if len( mailInfo["itemDatas"] ) < index:
			return

		# 置已取标记，以防止同一时间内连续收到同样的消息
		# 但当前并不设置数据库的sm_item数据为""，必须等cell回调通知成功时才会做此设置。
		mailInfo["itemTaken"] = 1
		self.cell.mail_receiveItem( mailID, mailInfo["itemDatas"][index], index )

	def mail_getAllItem( self, mailID ):
		"""
		define method
		玩家取邮件物品。

		过程：玩家取邮件附带物品，走到这一步，就是直接从玩家base的邮件数据中取出邮件物品。并把物品发送给
		玩家cell。

		参数：
		@param mailID: 邮件的dbid
		@type  mailID: DATABASE_ID
		"""
		if mailID not in self.mail_allInfo:
			ERROR_MSG( "error: No such mailID! the id is: %i " % ( mailID ))
			return

		mailInfo = self.mail_allInfo[mailID]
		if mailInfo["receiveTime"] > time():		# 还没到阅读时间
			ERROR_MSG( "error: The mail is not come! the id is: %i " % ( mailID ))
			return

		if len( mailInfo["itemDatas"] ) == 0:				# 该邮件没有物品
			ERROR_MSG( "error: The mail has no item ! the id is: %i " % ( mailID ))
			return
		#这个地方是用于限制获取物品太快而导致产生复制的问题
		#需要加上这个限制，否则可以刷物品
		if mailInfo["itemTaken"] == 1:				# 物品正在取出中
			ERROR_MSG( "error: The item has been Taken! the id is: %i " % ( mailID ))
			return

		# 置已取标记，以防止同一时间内连续收到同样的消息
		# 但当前并不设置数据库的sm_item数据为""，必须等cell回调通知成功时才会做此设置。
		mailInfo["itemTaken"] = 1
		self.cell.mail_receiveAllItem( mailID, mailInfo["itemDatas"] )

	def mail_getItemRegister( self, mailID, status, index ):
		"""
		define method
		玩家取得物品后，到base来做确认。同时也会修改数据库。玩家的cell调用。

		参数：
		@param mailID: 邮件的dbid
		@type  mailID: DATABASE_ID
		@param status: 获取状态，0 表示获取失败，1表示获取成功
		@type  status: INT8
		"""
		if status:
			fieldStr = "sm_item%s" % index
			itemDatas = self.mail_allInfo[mailID]["itemDatas"]
			itemDatas[ index ] = BigWorld.escape_string( cPickle.dumps( {}, 2 ) )
			query = "update custom_MailTable set %s = '%s' where id = %i" % ( fieldStr, itemDatas[index], mailID )
			#query = "update custom_MailTable ( sm_item0, sm_item1, sm_item2, sm_item3, sm_item4, sm_item5, sm_item6, sm_item7, sm_item8, sm_item9 ) values ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ) where id = %i" % ( itemDatas[0], itemDatas[1], itemDatas[2], itemDatas[3], itemDatas[4], itemDatas[5], itemDatas[6], itemDatas[7], itemDatas[8], itemDatas[9], mailID )
			BigWorld.executeRawDatabaseCommand( query, Functor( self._mail_getItemRegisterCb, mailID, itemDatas ) )#记录到数据库
			self.client.mail_itemHasGotten( mailID, index )

		#if len( self.mail_allInfo[mailID]["itemDatas"]) != 0:
		self.mail_allInfo[mailID]["itemTaken"] = 0	# 获取失败后需要重置状态，否则玩家将无法继续获取

	def mail_getAllItemRegister( self, mailID, status, failedIndexList = [] ):
		"""
		define method
		玩家取得物品后，到base来做确认。同时也会修改数据库。玩家的cell调用。

		参数：
		@param mailID: 邮件的dbid
		@type  mailID: DATABASE_ID
		@param status: 获取状态，0 表示获取失败，1表示获取成功
		@type  status: INT8
		"""
		if status:
			# 有个别物品添加失败了
			itemDatas = self.mail_allInfo[mailID]["itemDatas"]
			itemsString = []
			for index in xrange( 0, len( itemDatas ) ):
				if not index in failedIndexList:
					itemDatas[index] = cPickle.dumps( {}, 2 )
				#itemDatas[index] = BigWorld.escape_string( itemDatas[index] )
				itemsString.append( BigWorld.escape_string( itemDatas[index] ) )
			query = "update custom_MailTable set sm_item0='%s', sm_item1='%s', sm_item2='%s', sm_item3='%s', sm_item4='%s', sm_item5='%s', sm_item6='%s', sm_item7='%s', sm_item8='%s', sm_item9='%s' where id = %i" % ( itemsString[0], itemsString[1], itemsString[2], itemsString[3], itemsString[4], itemsString[5], itemsString[6], itemsString[7], itemsString[8], itemsString[9], mailID )
			BigWorld.executeRawDatabaseCommand( query, Functor( self._mail_getAllItemRegisterCb, mailID, itemDatas ) )	#记录到数据库
			self.client.mail_itemAllHasGotten( mailID, failedIndexList )

		self.mail_allInfo[mailID]["itemTaken"] = 0

	def _mail_getItemRegisterCb(self, mailID, itemDatas, result, dummy, errstr):
		"""
		在数据库记录物品已经被取走后的回调函数。

		这个函数主要是说明取走物品后，写数据库是否正常，如果不正常，把不正常的邮件ID记录下来。
		本身并没有什么处理。

		参数：
		@param mailID: 邮件的dbid
		@type  mailID: DATABASE_ID
		"""
		if errstr:
			ERROR_MSG( "%s(%i): set mail item be taken note error! the id is: %i " % ( self.getName(), self.id, mailID ), errstr )# , repr( itemData )

	def _mail_getAllItemRegisterCb(self, mailID, itemDatas, result, dummy, errstr):
		"""
		在数据库记录所有物品已经被取走后的回调函数。
		这个函数主要是说明取走物品后，写数据库是否正常，如果不正常，把不正常的邮件ID记录下来。
		本身并没有什么处理。
		参数：
		@param mailID: 邮件的dbid
		@type  mailID: DATABASE_ID
		"""
		if errstr:
			ERROR_MSG( "%s(%i): set mail item be taken note error! the id is: %i " % ( self.getName(), self.id, mailID ), errstr )

	def mail_getMoney(self, mailID):
		"""
		define method
		玩家取邮件金钱。

		过程：玩家取邮件附带金钱，走到这一步，就是直接从玩家base的邮件数据中取出邮件金钱。并把金钱发送给
		玩家cell。

		参数：
		@param mailID: 邮件的dbid
		@type  mailID: DATABASE_ID
		"""
		if mailID not in self.mail_allInfo:
			ERROR_MSG( "error: No such mailID! the id is: %i " % ( mailID ))
			return

		mailInfo = self.mail_allInfo[mailID]
		if float(mailInfo["receiveTime"]) > time(): # 还没到阅读时间
			ERROR_MSG( "error: The mail is not come! the id is: %i " % ( mailID ))
			return
		if mailInfo["money"] == 0:		# 该邮件没有金钱
			ERROR_MSG( "error: The mail has no money ! the id is: %i " % ( mailID ))
			return
		if mailInfo["moneyTaken"] == 1:  # 金钱正在取出中
			ERROR_MSG( "error: The money has been Taken! the id is: %i " % ( mailID ))
			return

		# 置已取标记，以防止同一时间内连续收到同样的消息
		# 但当前并不设置数据库sm_money为0，必须等cell回调通知成功时才会做此设置。
		mailInfo["moneyTaken"] = 1
		self.cell.mail_receiveMoney(mailID, int(mailInfo["money"]))
		return

	def mail_getMoneyRegister(self, mailID, status):
		"""
		define method
		玩家取得金钱后，到base来做确认。同时也会修改数据库。玩家的cell调用。
		参数：
		@param mailID: 邮件的dbid
		@type  mailID: DATABASE_ID
		@param status: 获取状态，0 表示获取失败，1表示获取成功
		@type  status: INT8
		"""
		if status:
			query = "update custom_MailTable set sm_money = 0 where id = %i" % (mailID)
			BigWorld.executeRawDatabaseCommand( query, Functor( self._mail_getMoneyRegisterCb, mailID, self.mail_allInfo[mailID]["money"] ) )#记录到数据库
			self.mail_allInfo[mailID]["money"] = 0
			self.client.mail_moneyHasGotten( mailID )
		else:
			self.mail_allInfo[mailID]["moneyTaken"] = 0	# 获取失败后需要重置状态，否则玩家将无法继续获取

	def _mail_getMoneyRegisterCb(self, mailID, moneyAmount, result, dummy, errstr):
		"""
		在数据库记录金钱已经被取走后的回调函数。

		这个函数主要是说明取走金钱后，写数据库是否正常，如果不正常，把不正常的邮件ID记录下来。
		本身并没有什么处理。

		参数：
		@param mailID: 邮件的dbid
		@type  mailID: DATABASE_ID
		"""
		if errstr:
			ERROR_MSG( "%s(%i): set mail money be taken note error! the id is: %i " % ( self.getName(), self.id, mailID, moneyAmount ), errstr )
			pass

	def onTimer_initMailToClient( self, timerID, userData ):
		"""
		"""
		if len( self.mail_initingmailIDs ) == 0:
			self.mail_initingCtrlID = 0
			self.delTimer( timerID )
			return

		k = self.mail_initingmailIDs.pop(0)
		m = self.mail_allInfo[k]
		#退信标题格式处理 添加参数 recieverName by姜毅
		# id, title, senderName, senderType, receiveTime, readedTime, content, money, itemData
		self.client.mail_receive( k, m["title"], m["senderName"], m["receiverName"], m["senderType"], m["receiveTime"], m["readedTime"], m["content"], m["money"], m["itemDatas"], m["readedHintTime"] )

	def mail_returnNotifyFC( self, mailID ):
		"""
		exposed method.
		由客户端调用，通知处理退信。

		@param mailID: 邮件唯一标识(dbid)
		@type  mailID: DATABASE_ID
		"""
		if mailID not in self.mail_allInfo:
			ERROR_MSG( "error: No such mailID! the id is: %i " % ( mailID ))
			return

		mailInfo = self.mail_allInfo[mailID]

		if mailInfo["itemTaken"] != 0:
			WARNING( "%s(%i): I have receive a message that Return mail '%i' To Sender when I processing a taked item request." % ( self.getName(), self.databaseID, mailID ) )
			return

		self.mail_returnInfo = mailInfo
		if mailInfo["readedTime"] == 0 and \
			time() - mailInfo["receiveTime"] > csconst.MAIL_NPC_OUTTIMED and \
			mailInfo["senderType"] == csdefine.MAIL_SENDER_TYPE_PLAYER:
			# 退信条件：信件没有读过，且超过了7天，而且该信是由玩家发送过来的

			# 处理方式：为了统一处理退信，所以我们这里什么都不做，
			# 仅仅是从临时数据中删除这封退掉的信，其余的交由邮件管理器自己统一定时的处理。
			del self.mail_allInfo[mailID]
		else:
			ERROR_MSG( "%s(%i): invalid mail! the id is: %i " % ( self.getName(), self.id, mailID ) )
			return

	def mail_systemReturn( self, mailID ):
		"""
		define method
		超时信件触发的系统自动退信,而且这个退信只是处理收信人的界面信息及client和base上保存的信息的更新，并不会真正删除数据库的信件
		"""
		if mailID not in self.mail_allInfo:
			ERROR_MSG( "error: No such mailID! the id is: %i " % ( mailID ))
			return
		del self.mail_allInfo[mailID]  #删除base上保留了该邮件信息
		self.client.mail_systemReturn( mailID )	#更新客户端的邮件列表	
		
	def mail_playerReturn( self, mailID ):
		"""
		exposed method
		玩家主动退信
		@param mailID: 邮件的唯一标识别(dbid)
		"""
		if mailID not in self.mail_allInfo:
			ERROR_MSG( "error: No such mailID! the id is: %i " % ( mailID ))
			return

		#检测对方邮箱是否已满 满则退信失败 modified by姜毅
		mailInfo = self.mail_allInfo[mailID]
		
		
		#玩家点击邮件界面上的退信做的处理，要修改退信的信件的查看时间和邮件提示查看时间
		mailInfo["readedTime"] = 0
		mailInfo["readedHintTime"] = 0
		query = "update custom_MailTable set sm_readedTime = 0, sm_readedHintTime = 0 where id = %i." % (mailID)
		BigWorld.executeRawDatabaseCommand( query, Functor(self._mail_updateTimeCb2, mailID) )		
		if mailInfo["itemTaken"] != 0:
			WARNING( "%s(%i): I have receive a message that Return mail '%i' To Sender when I processing a taked item request." % ( self.getName(), self.databaseID, mailID ) )
			return

		self.mail_returnInfo = {	"id"			: mailID,
									"title"			: mailInfo["title"],
									"content"		: mailInfo["content"],
									"itemDatas"		: mailInfo["itemDatas"],
									"money"			: mailInfo["money"],
									"senderName"	: mailInfo["senderName"],
									"receiverName"	: mailInfo["receiverName"],
									"senderType"	: mailInfo["senderType"],
									"receiveTime"	: mailInfo["receiveTime"],
									"readedTime"	: mailInfo["readedTime"],
									"readedHintTime": mailInfo["readedHintTime"],
									"itemTaken"		: mailInfo["itemTaken"],				# 用于临时记录当前是否正在拿取邮件物品
									"moneyTaken"	: mailInfo["moneyTaken"],				# 用于临时记录当前是否正在拿取邮件金钱
								}
		receiverName = mailInfo["receiverName"]
		#self.mail_send(self, receiverName, mailType, title, content, money, uids, hasItem, selfnpcID):
		"""
		#直接用npc用的发信接口处理退信问题
		itemDatas = [] #拷贝一份，以免下面的删除时会造成引用错误，从而使用收件人取不到物品
		itemDatas = mailInfo["itemDatas"]
		mailInfo["title"] = lbDatas.WITHDRAW_TITLE % ( mailInfo["receiverName"], mailInfo["title"] )
		BigWorld.globalData["MailMgr"].send( None, mailInfo["senderName"], 1, csdefine.MAIL_SENDER_TYPE_RETURN, mailInfo["receiverName"], mailInfo["title"], mailInfo["content"], mailInfo["money"], itemDatas )
		del self.mail_allInfo[mailID]
		self.client.onMailDeleted( mailID )
		#这里删除了，收到这封信的人就取不到物品了，上面的物品由于直接使用mailInfo，造成引用调用，实际些物品只有一份，只不过后来退信的时候引用了一份，造成引用错误，此时就要用
		self.client.mail_delete( mailID )
		"""
		BigWorld.lookUpBaseByName( "Role", receiverName, self._mailReturn_getPlayerMailboxCb)

	def onReturnMail( self, mailID ):
		"""
		define method
		"""
		# 把信退回给发信者
		receiverName = self.mail_allInfo[mailID]["senderName"]
		self.mail_allInfo[mailID]["readedTime"] = 0
		self.mail_allInfo[mailID]["readedHintTime"] = 0
		#query = "update custom_MailTable set sm_readedTime = 0, sm_readedHintTime = 0 where id = %i." % (mailID)
	#	BigWorld.executeRawDatabaseCommand( query, Functor(self._mail_updateTimeCb1, mailID) )		
		del self.mail_allInfo[mailID]
		self.client.onMailDeleted( mailID )
		BigWorld.lookUpBaseByName( "Role", receiverName, Functor( self._findReceiverCallback, mailID ) )
		
	def _mail_updateTimeCb1(self, mailID, result, dummy, errstr):
		"""
		更新邮件时间回调函数。
		这个函数主要是说明阅读邮件后，写数据库是否正常，如果不正常，把不正常的邮件ID记录下来。
		本身并没有什么处理。
		"""
		#print "_mail_updateTimeCb1",result,errstr
		if errstr:
			ERROR_MSG( "write mail readed flag fault! the id is: %i " % ( mailID ) )
		try:
			g_logger.mailUpTimeLog( self.mail_allInfo[mailID]["readedTime"], self.mail_allInfo[mailID]["readedHintTime"], self.mail_allInfo[mailID]["title"], mailID )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def _mail_updateTimeCb2(self, mailID, result, dummy, errstr):
		"""
		更新邮件时间回调函数。
		这个函数主要是说明阅读邮件后，写数据库是否正常，如果不正常，把不正常的邮件ID记录下来。
		本身并没有什么处理。
		"""
		#print "_mail_updateTimeCb2",result,errstr
		if errstr:
			ERROR_MSG( "write mail readed flag fault! the id is: %i " % ( mailID ) )
		try:
			g_logger.mailUpTimeLog( self.mail_allInfo[mailID]["readedTime"], self.mail_allInfo[mailID]["readedHintTime"], self.mail_allInfo[mailID]["title"], mailID )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def _findReceiverCallback( self, mailID, callResult ) :
		"""
		查找被退信者回调
		@param		mailID		: 退信邮件的ID
		@type		mailID		: DATABASE_ID
		@param		callResult	: BigWorld.lookUpBaseByName的查找结果,mailbox、True、False都有可能
		@type		callResult	: bool or mailbox
		"""
		if isinstance( callResult, bool ) : return
		# 如果被退信者在线，则通知他接收退信邮件
		#print callResult
		#callResult.mail_queryAll()
		#return
		#print "_findReceiverCallback", mailID, callResult
		query = "select id, sm_title, sm_content, sm_item0, sm_item1, sm_item2, sm_item3, sm_item4, sm_item5, sm_item6, sm_item7, sm_item8, sm_item9, sm_money, sm_senderName, sm_receiverName, sm_senderType, UNIX_TIMESTAMP(sm_receiveTime), UNIX_TIMESTAMP(sm_readedTime), UNIX_TIMESTAMP(sm_readedHintTime) from custom_MailTable where id = %i " % mailID
		BigWorld.executeRawDatabaseCommand( query, Functor( self._mail_queryReturnMailCB, callResult ) )

	def _mail_queryReturnMailCB( self, receiver, result, dummy, errstr ) :
		"""
		通知被退信者接收邮件
		"""
		if errstr:
			ERROR_MSG(errstr)
			return

		if len( result ) > 1 :
			ERROR_MSG( "amount of mails which id are %i should not be more than one!" % result[0][0] )
			return
		#print "_mail_queryReturnMailCB",receiver, result, dummy, errstr

		m = result[0]
		#print "_mail_queryReturnMailCB",result[0],receiver
		itemDatas = [ m[3], m[4], m[5], m[6], m[7], m[8], m[9], m[10], m[11], m[12] ]
		itemsString = []         
		itemsString = cPickle.dumps( itemDatas, 2 ) #将退信物品打包成string格式字符串	
		receiver.mail_addReturnMail( 	long( m[0] ),
										m[1],
										m[2],
										itemsString,
										long( m[13] ) ,
										m[14],
										m[15],
										int( m[16] ),
										int( m[17] ),
										int( m[18] ),
										int( m[19] ), 							 
									)
	

# RoleMail.py
