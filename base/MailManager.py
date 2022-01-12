# -*- coding: gb18030 -*-
#

# $ID$

import BigWorld
from bwdebug import *
from MsgLogger import g_logger
import cPickle
import time
import csdefine
import csconst
from Function import Functor
import csstatus

# timer cbid
MAIL_RETURN_CHECK_TIMER_CBID					= 1		# 返回邮件检测
MAIL_RETURN_PROCESS_TIMER_CBID					= 2		# 返回邮件处理

SEND_MAIL_SQL = "insert into custom_MailTable ( sm_title, sm_content, sm_item0, sm_item1, sm_item2, sm_item3, sm_item4, sm_item5, sm_item6, sm_item7, sm_item8, sm_item9, sm_money, sm_senderName, sm_receiverName, sm_senderType, sm_receiveTime, sm_timeFlag) value ( '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', %i, '%s','%s', %i, DATE_ADD(now(),INTERVAL %i SECOND), %i );"

class MailManager( BigWorld.Base ):
	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )

		self.returnMailList = []			# 退信列表
		self.returnMailProcessTimer = 0		# 退信处理timer，如果值不为0则表示当前已经有一个timer在运行中

		# 把自己注册为globalData全局实体
		self.registerGlobally( "MailMgr", self._onRegisterManager )

		# 在数据库中创建寄卖物品表custom_MailTable
		self._createMailTable()

		# 启动退信检查机制
		self.addTimer( 20, csconst.MAIL_RETURN_CHECK_TIME, MAIL_RETURN_CHECK_TIMER_CBID)

	def returnMailProcess(self):
		"""
		退信处理函数，每次只处理一封邮件
		"""
		if len(self.returnMailList) == 0:
			self.delTimer( self.returnMailProcessTimer )
			self.returnMailProcessTimer = 0
			return

		tempReturnMail = self.returnMailList.pop(0)
		#BigWorld.lookUpBaseByName( "Role", tempReturnMail["receiverName"], Functor( self._getPlayerMailboxForReturnCb_receiver, tempReturnMail ) )   #处理收信人在规定时间内没有阅读信件后，由系统自动退信，收信人的信息及界面更新
		BigWorld.lookUpBaseByName( "Role", tempReturnMail["senderName"], Functor( self._getPlayerMailboxForReturnCb, tempReturnMail ) )   #处理发信人在规定时间内没有阅读信件后，由系统自动退信，发信人的收到的退信及界面更新


	def _getPlayerMailboxForReturnCb_receiver( self, returnMail, callResult ):
		"""
		通过玩家名字查找在线情况的回调函数
		如果在线，更新自己的client和base上信息，并更新邮件显示界面
		前面参数同 sendItemSuccess
		@param callResult: BigWorld.lookUpBaseByName的查找结果,mailbox、True、False都有可能
		@type  callResult: MAILBOX OR BOOL
		"""
		# 返回一个mailbox时,表示找到玩家且在线
		if not isinstance( callResult, bool ):		# isinstance函数见python手册
			callResult.mail_systemReturn( returnMail["id"] )  #玩家在线时，更新自己的client和base上信息，并更新邮件显示界面
	
	def _getPlayerMailboxForReturnCb( self, returnMail, callResult ):
		"""
		通过玩家名字查找在线情况的回调函数
		如果在线，把返回的信件插入到玩家信件列表中

		前面参数同 sendItemSuccess
		@param callResult: BigWorld.lookUpBaseByName的查找结果,mailbox、True、False都有可能
		@type  callResult: MAILBOX OR BOOL
		"""
		# 返回一个mailbox时,表示找到玩家且在线
		if not isinstance( callResult, bool ):		# isinstance函数见python手册	
			callResult.mail_addReturnMail(	returnMail["id"],
											returnMail["title"],
											returnMail["content"],
											cPickle.dumps( returnMail["itemDatas"], 2 ),
											returnMail["money"],
											returnMail["senderName"],
											returnMail["receiverName"],
											csdefine.MAIL_SENDER_TYPE_RETURN,
											returnMail["receiveTime"],
											returnMail["readedTime"],
											returnMail["readedHintTime"] )
			BigWorld.lookUpBaseByName( "Role", returnMail["receiverName"], Functor( self._getPlayerMailboxForReturnCb_receiver, returnMail ) )   #处理收信人在规定时间内没有阅读信件后，由系统自动退信，收信人的信息及界面更新
											

	def onTimer( self, id, userData ):
		"""
		定时处理函数
		"""
		if userData == MAIL_RETURN_CHECK_TIMER_CBID:
			self.AutoReturnCheck()
		if userData == MAIL_RETURN_PROCESS_TIMER_CBID:
			self.returnMailProcess()


	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register MailMgr Fail!" )
			# again
			self.registerGlobally( "MailMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["MailMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("MailMgr Create Complete!")


	def _createMailTable( self ):
		"""
		创建邮件数据表
		"""
		# index_senderName 用于在查询时搜索由指定玩家发送的，类型为退信的信件
		# sm_timeFlag 使用当前的指令发送时间作为新邮件通知时过滤的条件
		query = """CREATE TABLE IF NOT EXISTS `custom_MailTable` (
				  `id` bigint(20) unsigned NOT NULL auto_increment,
				  `sm_title` varchar(255) default '',
				  `sm_content` text,
				  `sm_item0` blob,
				  `sm_item1` blob,
				  `sm_item2` blob,
				  `sm_item3` blob,
				  `sm_item4` blob,
				  `sm_item5` blob,
				  `sm_item6` blob,
				  `sm_item7` blob,
				  `sm_item8` blob,
				  `sm_item9` blob,
				  `sm_money` int(11) default '0',
				  `sm_senderName` varchar(255) default '',
				  `sm_receiverName` varchar(255) default '',
				  `sm_senderType` tinyint(4) default '0',
				  `sm_receiveTime` timestamp NOT NULL default '0000-00-00 00:00:00',
				  `sm_readedTime` timestamp NOT NULL default '0000-00-00 00:00:00',
				  `sm_timeFlag` int(10) unsigned NOT NULL default '0',
				  `sm_readedHintTime` timestamp NOT NULL default '0000-00-00 00:00:00',
				  PRIMARY KEY  (`id`),
				  KEY `index_receiverName` (`sm_receiverName`),
				  KEY `index_senderName` (`sm_senderName`)
				) ENGINE=InnoDB;"""
		BigWorld.executeRawDatabaseCommand( query, self._createMailTableCb )
		#######只有初次创建表的时候，上面的创建没问题，由于有的表是已经创建好了，为了解决大部分表custom_MailTable没有字段sm_readedHintTime,
		##下面的报错不用管，这下面的一段代码运行一段时间可以删除
		query = """ALTER TABLE `custom_MailTable` ADD `sm_readedHintTime` timestamp NOT NULL default '0000-00-00 00:00:00';"""
		BigWorld.executeRawDatabaseCommand( query, self._createMailTableCb )


	def _createMailTableCb( self, result, rows, errstr ):
		"""
		创建邮件数据表回调函数
		这个邮件数据表只在服务器第一次运行的时候创建。如果发现这条错误语句，是比较严重的，需要立刻重起服务器。
		"""
		if errstr:
			# 创建邮件数据表错误
			ERROR_MSG("Create custom_MailTable Fail!")
			return

	def AutoReturnCheck( self ):
		"""
		邮件超时退信处理
		当玩家长时间没有看一封信的时候，这封信会被退回。
		@param data: 超时长度设定
		@type  data: int
		"""
		# 找出最前面的50封玩家寄出的，同时没有被阅读过的，而且也超过了指定时间的邮件
		query = "select id, sm_title, sm_content, sm_item0, sm_item1, sm_item2, sm_item3, sm_item4, sm_item5, sm_item6, sm_item7, sm_item8, sm_item9, sm_money, sm_senderName, sm_receiverName, sm_senderType, UNIX_TIMESTAMP(sm_receiveTime), UNIX_TIMESTAMP(sm_readedTime), UNIX_TIMESTAMP(sm_readedHintTime) from custom_MailTable where sm_senderType = 1 and sm_readedTime = \'0000-00-00 00:00:00\' and UNIX_TIMESTAMP(now()) - UNIX_TIMESTAMP(sm_receiveTime) >= %i limit 50" % (csconst.MAIL_RETURN_AFTER_SEND)
		BigWorld.executeRawDatabaseCommand( query, self._AutoReturnCheckCb )


	def _AutoReturnCheckCb(self, result, dummy, errstr):
		"""
		邮件超时退信处理回调函数
		当获得一批需要处理的退件时，先是把他们存储到一个退件列表中。

		"""
		if errstr:
			ERROR_MSG(errstr)
			return

		if len(result) == 0:
			return

		tempMails = []
		t = int( time.time() )
		# id, title, content, item, money, senderName, receiverName, senderType, receiveTime, readedTime
		for m in result:
			tempMails.append( {	"id"			: long( m[0] ),
								"title"			: m[1],
								"content"		: m[2],
								"itemDatas"		: [ m[3], m[4], m[5], m[6], m[7], m[8], m[9], m[10], m[11], m[12] ],
								"money"			: int( m[13] ),
								"senderName"	: m[14],
								"receiverName"	: m[15],
								"senderType"	: int( m[16] ),
								"receiveTime"	: t,					# 置新的收信时间
								"readedTime"	: 0, 					# 重置读信时间
								"readedHintTime": 0                     # 退信重置邮件提示时间
								} )

		tempDbidList = [ x[0] for x in result ]

		# 把找到的过期邮件设为退信状态，并且设置此邮件的接收日期为当前修改的时间，以便重新开始记时（用作删除信件的判断）
		query = "update custom_MailTable set sm_senderType = %i, sm_receiveTime = now(), sm_readedTime = \'0000-00-00 00:00:00\', sm_readedHintTime = \'0000-00-00 00:00:00\' where id in %s" % (csdefine.MAIL_SENDER_TYPE_RETURN, str( tuple( tempDbidList ) ).replace(" ","").replace('L', "").replace(",)", ")"))
		BigWorld.executeRawDatabaseCommand( query, Functor( self._updateReturnMailCB, tempMails ) )

	def _updateReturnMailCB(self, resultMails, result, dummy, errstr):
		"""
		超时邮件记录数据库回调函数。
		"""
		# 当前我们什么都不能做，只写错误日志。
		if errstr:
			ERROR_MSG(errstr)
			return
		# 把退信放到退信列表中，由time统一进行退信处理
		self.returnMailList.extend( resultMails )

		for returnMail in self.returnMailList:
			try:
				g_logger.mailSysReturnLog( returnMail["senderName"], returnMail["receiverName"], returnMail["title"], returnMail["id"] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

		if self.returnMailProcessTimer == 0:
			self.returnMailProcessTimer = self.addTimer( 10, csconst.MAIL_RETURN_PROCESS_TIME, MAIL_RETURN_PROCESS_TIMER_CBID)

	def sendWithMailbox(self, senderMB, receiverBase, receiverName, mailType, senderType, senderName, title, content, money, itemDatas):
		"""
		define method
		有收信者mailbox的发信（该mailbox可能为None，表示不在线），此功能主要用于可以直接找到发信者base mailbox的场合，以提高发信效率。

		过程：玩家寄出的邮件到达这里，就被直接存储到数据库中了。
		同时还会利用receiverBase来把这个信息通知收信人，让他读取新的邮件。

		@param     senderMB: 发件人的MAILBOX，如果发信的是玩家，把玩家的mailbox写上有助于返回发信成功/失败的消息，如果是NPC，可以置None
		@type      senderMB: MAILBOX
		@param receiverBase: 收件人的base
		@type  receiverBase: mailbox
		@param receiverName: 收信人的名字
		@type  receiverName: string
		@param     mailType: 邮件类型
		@type      mailType: int8
		@param   senderType: 寄邮件的类型
		@type    senderType: int8
		@param   senderName: 寄信人的名字
		@type    senderName: string
		@param        title: 邮件的标题
		@type         title: string
		@param      content: 邮件的内容
		@type       content: string
		@param        money: 邮件包含的金钱
		@type         money: uint32
		@param     itemDatas: 邮件包含的物品字符串列表
		@type      itemDatas: array of string
		"""
		if len(title) > csconst.MAIL_TITLE_LENGTH_MAX:		# 标题长度小于20个字检测
			return False

		if len(content) > csconst.MAIL_CONTENT_LENGTH_MAX:	# 标题长度小于400个字检测
			return False

		if mailType == csdefine.MAIL_TYPE_QUICK:	# 快递
			receiveTime = csconst.MAIL_RECEIVE_TIME_QUICK
		elif mailType == csdefine.MAIL_TYPE_NORMAL:	# 普通信件
			receiveTime = csconst.MAIL_RECEIVE_TIME_NORMAL

		# 补全10个物品数据并做字符串转义处理
		itemDataList = []
		for itemStr in itemDatas:
			itemDataList.append( BigWorld.escape_string( itemStr ) )
		itemDataList.reverse()
		itemEmptyCount = 10 - len( itemDatas )
		if itemEmptyCount > 0:
			itemDataList.extend( [ BigWorld.escape_string( cPickle.dumps( {}, 2 ) ) ] * itemEmptyCount )
		convertContent = BigWorld.escape_string( content )
		convertTitle = BigWorld.escape_string( title )

		t = int( time.time() )
		query = SEND_MAIL_SQL % ( convertTitle, convertContent, itemDataList[0], itemDataList[1], itemDataList[2], itemDataList[3], itemDataList[4], itemDataList[5], itemDataList[6], itemDataList[7], itemDataList[8], itemDataList[9], money, BigWorld.escape_string( senderName ), BigWorld.escape_string( receiverName ), senderType, receiveTime, t )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._sendWithMailboxCB, senderMB, receiverBase, senderName, receiverName, convertTitle, itemDatas, money, t ) )	# 记录到数据库

	def _sendWithMailboxCB( self, senderMB, receiverBase, senderName, receiverName, convertTitle, itemDatas, money, timeFlag, result, dummy, errstr ):
		"""
		玩家寄信的回调函数。
		附加的几个参数目的主要是当邮件记录到数据库失败的时候，我们可以看到是谁寄出的邮件，并且该邮件是否有物品和金钱。

		@param     senderMB: 发件人的MAILBOX，如果发信的是玩家，把玩家的mailbox写上有助于返回发信成功/失败的消息，如果是NPC，可以置None
		@type      senderMB: MAILBOX
		@param receiverBase: 收件人的base mailbox
		@type  receiverBase: MAILBOX
		@param   senderName: 寄信人名字
		@type    senderName: STRING
		@param   receiverName:收件人名字
		@type    receiverName:STRING
		@param	 convertTitle:邮件的标题
		@type	 convertTitle:STRING
		@param	   itemDatas: 邮件附带物品列表数据
		@type      itemDatas: ARRAY OF STRING
		@param	      money: 邮件附带物品金钱
		@type         money: UINT32
		@param	   timeFlag: 用于查询过滤的标记
		@type      timeFlag: INT32

		@param result、dummy、errstr: 见api文档
		"""
		if errstr:
			for itemDatasStr in itemDatas:
				ERROR_MSG( "error:%s send an money and item : %i, item data: \'%s\'" % ( senderName, money, repr( itemDatasStr ) ) )
			return
		else:
			# 发信成功，通知在线的收件人
			if receiverBase:
				receiverBase.mail_newNotify(senderName, timeFlag)

			# 有发信人mailbox，通知发信人
			if senderMB:
				senderMB.client.onStatusMessage( csstatus.MAIL_SEND_SUCCESS, "" )

			try:
				g_logger.mailSendLog( senderName, receiverName, convertTitle, len(itemDatas), money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

	def send(self, senderMB, receiverName, mailType, senderType, senderName, title, content, money, itemDatas):
		"""
		define method
		无目标mailbox发信。此功能一般用于不知道收信目标的base mailbox的发信功能。一般来说，使用此方法会比使用sendWithMailbox()的效率低。

		@param     senderMB: 发件人的MAILBOX，如果发信的是玩家，把玩家的mailbox写上有助于返回发信成功/失败的消息，如果是NPC，可以置None
		@type      senderMB: MAILBOX
		@param receiverName: 收信人的名字
		@type  receiverName: string
		@param     mailType: 邮件类型
		@type      mailType: int8
		@param   senderType: 寄邮件的类型
		@type    senderType: int8
		@param   senderName: 寄信人的名字
		@type    senderName: string
		@param        title: 邮件的标题
		@type         title: string
		@param      content: 邮件的内容
		@type       content: string
		@param        money: 邮件包含的金钱
		@type         money: uint32
		@param     itemDatas: 邮件包含的物品字符串
		@type      itemDatas: <of> STRING </of>
		"""
		BigWorld.lookUpBaseByName( "Role", receiverName, Functor( self._getPlayerMailboxForSendMailCb, (senderMB, receiverName, mailType, senderType, senderName, title, content, money, itemDatas) ) )

	def _getPlayerMailboxForSendMailCb( self, mailParams, callResult ):
		"""
		没有目标mailbox发信模式的回调函数

		前面参数同 sendItemSuccess
		@param mailParams: 信件参数,用于发送邮件
		@type  mailParams: tuple
		@param callResult: BigWorld.lookUpBaseByName的查找结果,mailbox、True、False都有可能
		@type  callResult: MAILBOX OR BOOL
		"""
		# 返回一个mailbox时,表示找到玩家且在线
		if not isinstance( callResult, bool ):		# isinstance函数见python手册
			self.sendWithMailbox( mailParams[0], callResult, *mailParams[1:] )		# 目标在线
		elif callResult:
			self.sendWithMailbox( mailParams[0], None, *mailParams[1:] )			# 目标不在线
		else:
			ERROR_MSG( "error for send mail, target not existed.", repr( mailParams ) )


	def returnMail( self, playerBase, playerName, mailID ):
		"""
		define method
		玩家主动退信
		"""
		query = "select sm_senderType, sm_receiverName, sm_senderName, sm_title from custom_MailTable where id = %i" % mailID
		BigWorld.executeRawDatabaseCommand( query, Functor( self._returnMailCB, playerBase, playerName, mailID)  )

	def _returnMailCB( self, playerBase, playerName, mailID, result, dummy, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG(errstr)
			return
		if result[0][0] != '1' or result[0][1] != playerName:
			return

		# 处理退信时要把读信时间重新置零，表示没有读取过该邮件
		query = "update custom_MailTable set sm_senderType = %i, sm_receiveTime = now(), sm_readedTime = \'0000-00-00 00:00:00\', sm_readedHintTime = \'0000-00-00 00:00:00\' where id = %i" % (csdefine.MAIL_SENDER_TYPE_RETURN, mailID )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._returnMailCBCB, playerBase, mailID ) )
		try:
			g_logger.mailReturnLog(  result[0][2], playerName, result[0][3], mailID)
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def _returnMailCBCB(self, playerBase, mailID, result, dummy, errstr):
		"""
		超时邮件记录数据库回调函数。
		"""
		if errstr:
			ERROR_MSG(errstr)
			return

		playerBase.onReturnMail( mailID )


# MailManager.py
