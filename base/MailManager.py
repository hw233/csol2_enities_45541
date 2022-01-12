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
MAIL_RETURN_CHECK_TIMER_CBID					= 1		# �����ʼ����
MAIL_RETURN_PROCESS_TIMER_CBID					= 2		# �����ʼ�����

SEND_MAIL_SQL = "insert into custom_MailTable ( sm_title, sm_content, sm_item0, sm_item1, sm_item2, sm_item3, sm_item4, sm_item5, sm_item6, sm_item7, sm_item8, sm_item9, sm_money, sm_senderName, sm_receiverName, sm_senderType, sm_receiveTime, sm_timeFlag) value ( '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', %i, '%s','%s', %i, DATE_ADD(now(),INTERVAL %i SECOND), %i );"

class MailManager( BigWorld.Base ):
	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )

		self.returnMailList = []			# �����б�
		self.returnMailProcessTimer = 0		# ���Ŵ���timer�����ֵ��Ϊ0���ʾ��ǰ�Ѿ���һ��timer��������

		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "MailMgr", self._onRegisterManager )

		# �����ݿ��д���������Ʒ��custom_MailTable
		self._createMailTable()

		# �������ż�����
		self.addTimer( 20, csconst.MAIL_RETURN_CHECK_TIME, MAIL_RETURN_CHECK_TIMER_CBID)

	def returnMailProcess(self):
		"""
		���Ŵ�������ÿ��ֻ����һ���ʼ�
		"""
		if len(self.returnMailList) == 0:
			self.delTimer( self.returnMailProcessTimer )
			self.returnMailProcessTimer = 0
			return

		tempReturnMail = self.returnMailList.pop(0)
		#BigWorld.lookUpBaseByName( "Role", tempReturnMail["receiverName"], Functor( self._getPlayerMailboxForReturnCb_receiver, tempReturnMail ) )   #�����������ڹ涨ʱ����û���Ķ��ż�����ϵͳ�Զ����ţ������˵���Ϣ���������
		BigWorld.lookUpBaseByName( "Role", tempReturnMail["senderName"], Functor( self._getPlayerMailboxForReturnCb, tempReturnMail ) )   #���������ڹ涨ʱ����û���Ķ��ż�����ϵͳ�Զ����ţ������˵��յ������ż��������


	def _getPlayerMailboxForReturnCb_receiver( self, returnMail, callResult ):
		"""
		ͨ��������ֲ�����������Ļص�����
		������ߣ������Լ���client��base����Ϣ���������ʼ���ʾ����
		ǰ�����ͬ sendItemSuccess
		@param callResult: BigWorld.lookUpBaseByName�Ĳ��ҽ��,mailbox��True��False���п���
		@type  callResult: MAILBOX OR BOOL
		"""
		# ����һ��mailboxʱ,��ʾ�ҵ����������
		if not isinstance( callResult, bool ):		# isinstance������python�ֲ�
			callResult.mail_systemReturn( returnMail["id"] )  #�������ʱ�������Լ���client��base����Ϣ���������ʼ���ʾ����
	
	def _getPlayerMailboxForReturnCb( self, returnMail, callResult ):
		"""
		ͨ��������ֲ�����������Ļص�����
		������ߣ��ѷ��ص��ż����뵽����ż��б���

		ǰ�����ͬ sendItemSuccess
		@param callResult: BigWorld.lookUpBaseByName�Ĳ��ҽ��,mailbox��True��False���п���
		@type  callResult: MAILBOX OR BOOL
		"""
		# ����һ��mailboxʱ,��ʾ�ҵ����������
		if not isinstance( callResult, bool ):		# isinstance������python�ֲ�	
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
			BigWorld.lookUpBaseByName( "Role", returnMail["receiverName"], Functor( self._getPlayerMailboxForReturnCb_receiver, returnMail ) )   #�����������ڹ涨ʱ����û���Ķ��ż�����ϵͳ�Զ����ţ������˵���Ϣ���������
											

	def onTimer( self, id, userData ):
		"""
		��ʱ������
		"""
		if userData == MAIL_RETURN_CHECK_TIMER_CBID:
			self.AutoReturnCheck()
		if userData == MAIL_RETURN_PROCESS_TIMER_CBID:
			self.returnMailProcess()


	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register MailMgr Fail!" )
			# again
			self.registerGlobally( "MailMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["MailMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("MailMgr Create Complete!")


	def _createMailTable( self ):
		"""
		�����ʼ����ݱ�
		"""
		# index_senderName �����ڲ�ѯʱ������ָ����ҷ��͵ģ�����Ϊ���ŵ��ż�
		# sm_timeFlag ʹ�õ�ǰ��ָ���ʱ����Ϊ���ʼ�֪ͨʱ���˵�����
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
		#######ֻ�г��δ������ʱ������Ĵ���û���⣬�����еı����Ѿ��������ˣ�Ϊ�˽���󲿷ֱ�custom_MailTableû���ֶ�sm_readedHintTime,
		##����ı����ùܣ��������һ�δ�������һ��ʱ�����ɾ��
		query = """ALTER TABLE `custom_MailTable` ADD `sm_readedHintTime` timestamp NOT NULL default '0000-00-00 00:00:00';"""
		BigWorld.executeRawDatabaseCommand( query, self._createMailTableCb )


	def _createMailTableCb( self, result, rows, errstr ):
		"""
		�����ʼ����ݱ�ص�����
		����ʼ����ݱ�ֻ�ڷ�������һ�����е�ʱ�򴴽��������������������䣬�ǱȽ����صģ���Ҫ���������������
		"""
		if errstr:
			# �����ʼ����ݱ����
			ERROR_MSG("Create custom_MailTable Fail!")
			return

	def AutoReturnCheck( self ):
		"""
		�ʼ���ʱ���Ŵ���
		����ҳ�ʱ��û�п�һ���ŵ�ʱ������Żᱻ�˻ء�
		@param data: ��ʱ�����趨
		@type  data: int
		"""
		# �ҳ���ǰ���50����Ҽĳ��ģ�ͬʱû�б��Ķ����ģ�����Ҳ������ָ��ʱ����ʼ�
		query = "select id, sm_title, sm_content, sm_item0, sm_item1, sm_item2, sm_item3, sm_item4, sm_item5, sm_item6, sm_item7, sm_item8, sm_item9, sm_money, sm_senderName, sm_receiverName, sm_senderType, UNIX_TIMESTAMP(sm_receiveTime), UNIX_TIMESTAMP(sm_readedTime), UNIX_TIMESTAMP(sm_readedHintTime) from custom_MailTable where sm_senderType = 1 and sm_readedTime = \'0000-00-00 00:00:00\' and UNIX_TIMESTAMP(now()) - UNIX_TIMESTAMP(sm_receiveTime) >= %i limit 50" % (csconst.MAIL_RETURN_AFTER_SEND)
		BigWorld.executeRawDatabaseCommand( query, self._AutoReturnCheckCb )


	def _AutoReturnCheckCb(self, result, dummy, errstr):
		"""
		�ʼ���ʱ���Ŵ���ص�����
		�����һ����Ҫ������˼�ʱ�����ǰ����Ǵ洢��һ���˼��б��С�

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
								"receiveTime"	: t,					# ���µ�����ʱ��
								"readedTime"	: 0, 					# ���ö���ʱ��
								"readedHintTime": 0                     # ���������ʼ���ʾʱ��
								} )

		tempDbidList = [ x[0] for x in result ]

		# ���ҵ��Ĺ����ʼ���Ϊ����״̬���������ô��ʼ��Ľ�������Ϊ��ǰ�޸ĵ�ʱ�䣬�Ա����¿�ʼ��ʱ������ɾ���ż����жϣ�
		query = "update custom_MailTable set sm_senderType = %i, sm_receiveTime = now(), sm_readedTime = \'0000-00-00 00:00:00\', sm_readedHintTime = \'0000-00-00 00:00:00\' where id in %s" % (csdefine.MAIL_SENDER_TYPE_RETURN, str( tuple( tempDbidList ) ).replace(" ","").replace('L', "").replace(",)", ")"))
		BigWorld.executeRawDatabaseCommand( query, Functor( self._updateReturnMailCB, tempMails ) )

	def _updateReturnMailCB(self, resultMails, result, dummy, errstr):
		"""
		��ʱ�ʼ���¼���ݿ�ص�������
		"""
		# ��ǰ����ʲô����������ֻд������־��
		if errstr:
			ERROR_MSG(errstr)
			return
		# �����ŷŵ������б��У���timeͳһ�������Ŵ���
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
		��������mailbox�ķ��ţ���mailbox����ΪNone����ʾ�����ߣ����˹�����Ҫ���ڿ���ֱ���ҵ�������base mailbox�ĳ��ϣ�����߷���Ч�ʡ�

		���̣���Ҽĳ����ʼ���������ͱ�ֱ�Ӵ洢�����ݿ����ˡ�
		ͬʱ��������receiverBase���������Ϣ֪ͨ�����ˣ�������ȡ�µ��ʼ���

		@param     senderMB: �����˵�MAILBOX��������ŵ�����ң�����ҵ�mailboxд�������ڷ��ط��ųɹ�/ʧ�ܵ���Ϣ�������NPC��������None
		@type      senderMB: MAILBOX
		@param receiverBase: �ռ��˵�base
		@type  receiverBase: mailbox
		@param receiverName: �����˵�����
		@type  receiverName: string
		@param     mailType: �ʼ�����
		@type      mailType: int8
		@param   senderType: ���ʼ�������
		@type    senderType: int8
		@param   senderName: �����˵�����
		@type    senderName: string
		@param        title: �ʼ��ı���
		@type         title: string
		@param      content: �ʼ�������
		@type       content: string
		@param        money: �ʼ������Ľ�Ǯ
		@type         money: uint32
		@param     itemDatas: �ʼ���������Ʒ�ַ����б�
		@type      itemDatas: array of string
		"""
		if len(title) > csconst.MAIL_TITLE_LENGTH_MAX:		# ���ⳤ��С��20���ּ��
			return False

		if len(content) > csconst.MAIL_CONTENT_LENGTH_MAX:	# ���ⳤ��С��400���ּ��
			return False

		if mailType == csdefine.MAIL_TYPE_QUICK:	# ���
			receiveTime = csconst.MAIL_RECEIVE_TIME_QUICK
		elif mailType == csdefine.MAIL_TYPE_NORMAL:	# ��ͨ�ż�
			receiveTime = csconst.MAIL_RECEIVE_TIME_NORMAL

		# ��ȫ10����Ʒ���ݲ����ַ���ת�崦��
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
		BigWorld.executeRawDatabaseCommand( query, Functor( self._sendWithMailboxCB, senderMB, receiverBase, senderName, receiverName, convertTitle, itemDatas, money, t ) )	# ��¼�����ݿ�

	def _sendWithMailboxCB( self, senderMB, receiverBase, senderName, receiverName, convertTitle, itemDatas, money, timeFlag, result, dummy, errstr ):
		"""
		��Ҽ��ŵĻص�������
		���ӵļ�������Ŀ����Ҫ�ǵ��ʼ���¼�����ݿ�ʧ�ܵ�ʱ�����ǿ��Կ�����˭�ĳ����ʼ������Ҹ��ʼ��Ƿ�����Ʒ�ͽ�Ǯ��

		@param     senderMB: �����˵�MAILBOX��������ŵ�����ң�����ҵ�mailboxд�������ڷ��ط��ųɹ�/ʧ�ܵ���Ϣ�������NPC��������None
		@type      senderMB: MAILBOX
		@param receiverBase: �ռ��˵�base mailbox
		@type  receiverBase: MAILBOX
		@param   senderName: ����������
		@type    senderName: STRING
		@param   receiverName:�ռ�������
		@type    receiverName:STRING
		@param	 convertTitle:�ʼ��ı���
		@type	 convertTitle:STRING
		@param	   itemDatas: �ʼ�������Ʒ�б�����
		@type      itemDatas: ARRAY OF STRING
		@param	      money: �ʼ�������Ʒ��Ǯ
		@type         money: UINT32
		@param	   timeFlag: ���ڲ�ѯ���˵ı��
		@type      timeFlag: INT32

		@param result��dummy��errstr: ��api�ĵ�
		"""
		if errstr:
			for itemDatasStr in itemDatas:
				ERROR_MSG( "error:%s send an money and item : %i, item data: \'%s\'" % ( senderName, money, repr( itemDatasStr ) ) )
			return
		else:
			# ���ųɹ���֪ͨ���ߵ��ռ���
			if receiverBase:
				receiverBase.mail_newNotify(senderName, timeFlag)

			# �з�����mailbox��֪ͨ������
			if senderMB:
				senderMB.client.onStatusMessage( csstatus.MAIL_SEND_SUCCESS, "" )

			try:
				g_logger.mailSendLog( senderName, receiverName, convertTitle, len(itemDatas), money )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

	def send(self, senderMB, receiverName, mailType, senderType, senderName, title, content, money, itemDatas):
		"""
		define method
		��Ŀ��mailbox���š��˹���һ�����ڲ�֪������Ŀ���base mailbox�ķ��Ź��ܡ�һ����˵��ʹ�ô˷������ʹ��sendWithMailbox()��Ч�ʵ͡�

		@param     senderMB: �����˵�MAILBOX��������ŵ�����ң�����ҵ�mailboxд�������ڷ��ط��ųɹ�/ʧ�ܵ���Ϣ�������NPC��������None
		@type      senderMB: MAILBOX
		@param receiverName: �����˵�����
		@type  receiverName: string
		@param     mailType: �ʼ�����
		@type      mailType: int8
		@param   senderType: ���ʼ�������
		@type    senderType: int8
		@param   senderName: �����˵�����
		@type    senderName: string
		@param        title: �ʼ��ı���
		@type         title: string
		@param      content: �ʼ�������
		@type       content: string
		@param        money: �ʼ������Ľ�Ǯ
		@type         money: uint32
		@param     itemDatas: �ʼ���������Ʒ�ַ���
		@type      itemDatas: <of> STRING </of>
		"""
		BigWorld.lookUpBaseByName( "Role", receiverName, Functor( self._getPlayerMailboxForSendMailCb, (senderMB, receiverName, mailType, senderType, senderName, title, content, money, itemDatas) ) )

	def _getPlayerMailboxForSendMailCb( self, mailParams, callResult ):
		"""
		û��Ŀ��mailbox����ģʽ�Ļص�����

		ǰ�����ͬ sendItemSuccess
		@param mailParams: �ż�����,���ڷ����ʼ�
		@type  mailParams: tuple
		@param callResult: BigWorld.lookUpBaseByName�Ĳ��ҽ��,mailbox��True��False���п���
		@type  callResult: MAILBOX OR BOOL
		"""
		# ����һ��mailboxʱ,��ʾ�ҵ����������
		if not isinstance( callResult, bool ):		# isinstance������python�ֲ�
			self.sendWithMailbox( mailParams[0], callResult, *mailParams[1:] )		# Ŀ������
		elif callResult:
			self.sendWithMailbox( mailParams[0], None, *mailParams[1:] )			# Ŀ�겻����
		else:
			ERROR_MSG( "error for send mail, target not existed.", repr( mailParams ) )


	def returnMail( self, playerBase, playerName, mailID ):
		"""
		define method
		�����������
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

		# ��������ʱҪ�Ѷ���ʱ���������㣬��ʾû�ж�ȡ�����ʼ�
		query = "update custom_MailTable set sm_senderType = %i, sm_receiveTime = now(), sm_readedTime = \'0000-00-00 00:00:00\', sm_readedHintTime = \'0000-00-00 00:00:00\' where id = %i" % (csdefine.MAIL_SENDER_TYPE_RETURN, mailID )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._returnMailCBCB, playerBase, mailID ) )
		try:
			g_logger.mailReturnLog(  result[0][2], playerName, result[0][3], mailID)
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def _returnMailCBCB(self, playerBase, mailID, result, dummy, errstr):
		"""
		��ʱ�ʼ���¼���ݿ�ص�������
		"""
		if errstr:
			ERROR_MSG(errstr)
			return

		playerBase.onReturnMail( mailID )


# MailManager.py
