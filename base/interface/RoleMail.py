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
		# ��ҵ��ʼ��б������ɿ��ĺͲ��ɿ��ģ���
		# key = databaseID of mail
		# value = [ sm_title, sm_content, sm_item0, sm_item1, sm_item2, sm_item3, sm_item4, sm_item5, sm_item6, sm_item7, sm_item8, sm_item9,sm_money, sm_senderName, sm_receiverName, sm_senderType, sm_receiveTime, sm_readedTime ]
		self.mail_allInfo = {}
		self.mail_initingCtrlID = 0		# ��ʼ���ʼ����ݵ��ͻ���ʱ��timerID
		self.mail_initingmailIDs = []	# ��ʼ���ʼ����ݵ��ͻ���ʱ���ʼ�ID�б�ʹ�ô��б��ԭ�����ڳ�ʼ���Ĺ����кܿ��ܻ������µ��ʼ���������ֻ��ҡ�

		self.mail_sendInfo = {}			# ��ʱ�洢Ҫ���͵��ʼ�����Ϣ
		self.mail_sending = False		# ��ʱ��ǣ�������ֹ�������Ͷ���ʼ��������ʼ����ݵĲ���ȷ
		self.mail_returnInfo = {}       # ��ʱ�洢Ҫ���ŵ��ʼ�����Ϣ by����


	def mail_send(self, receiverName, mailType, title, content, money, uids, hasItem, npcID):
		"""
		exposed method.
		��Ҽ��ţ���Ҫ���ڸ��ͻ��˵���

		���̣�
		�����ж��ʼ����ⳤ�ȣ��ʼ����ݳ����Ƿ�ϸ��ڼ�¼�ʼ�����Ϣ������ʼ����������ҿ��Ƿ���ڡ�

		������
		@param receiverName:����������
		@type receiverName:	string
		@param mailType:	�ʼ�����
		@type mailType:		int8
		@param title:		�ʼ��ı���
		@type title:		string
		@param content:		�ʼ�������
		@type content:		string
		@param money:		�ʼ������Ľ�Ǯ
		@type money:		unit32
		@param uids:		�ʼ���������Ʒ��ΨһID
		@type uids:			int64
		@param hasItem:		��ʾ�Ƿ�Я������Ʒ����
		@type hasItem:		int8
		@param npcID:		�����õ�������id
		@type npcID:		object_id
		"""

		# ������ͬʱ���Ͷ���ż����Ա�����ֺ������ż����ݸ���ǰ����ż�����
		if self.mail_sending:
			return

		# ��������Լ�����
		if receiverName == self.getName():
			return

		if len(title) > csconst.MAIL_TITLE_LENGTH_MAX:		# ���ⳤ��С��20���ּ��
			return

		if len(content) > csconst.MAIL_CONTENT_LENGTH_MAX:	# ���ⳤ��С��400���ּ��
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
		���Ź�����ͨ�����������ֲ����������Ƿ���ڣ��Լ���������Ļص�����

		ǰ�����ͬ sendItemSuccess

		@param callResult:	BigWorld.lookUpBaseByName�Ĳ��ҽ��,mailbox��True��False���п���
		@type callResult:	MAILBOX OR BOOL
		"""
		# ����һ��mailboxʱ,��ʾ�ҵ����������
		if not isinstance( callResult, bool ):		# isinstance������python�ֲ�
			playerBase = callResult
		elif callResult == True:
			playerBase = None
		else:
			self.client.onStatusMessage( csstatus.MAIL_RECEIVER_NOT_FOUND, "" )
			self.mail_sending = False
			return

		# ��ѯ����ʼ�����
		query = "select count(*) from custom_MailTable where sm_receiverName = '%s' and sm_senderType != %i" % ( BigWorld.escape_string( self.mail_sendInfo["receiverName"] ), csdefine.MAIL_SENDER_TYPE_RETURN )
		BigWorld.executeRawDatabaseCommand( query, Functor(self._mail_queryCountForCheckCb, playerBase) )

	def _mailReturn_getPlayerMailboxCb( self, callResult ):
		"""
		���Ź�����ͨ�����������ֲ����������Ƿ���ڣ��Լ���������Ļص�����

		ǰ�����ͬ sendItemSuccess

		@param callResult:	BigWorld.lookUpBaseByName�Ĳ��ҽ��,mailbox��True��False���п���
		@type callResult:	MAILBOX OR BOOL
		"""
		if not isinstance( callResult, bool ):		# isinstance������python�ֲ�
			playerBase = callResult
		elif callResult == True:
			playerBase = None
		else:
			self.client.onStatusMessage( csstatus.MAIL_RECEIVER_NOT_FOUND, "" )
			self.mail_sending = False
			return

		# ��ѯ����ʼ����� �˺���modified by����
		query = "select count(*) from custom_MailTable where sm_receiverName = '%s'" % (BigWorld.escape_string( self.mail_returnInfo["senderName"] ) )
		BigWorld.executeRawDatabaseCommand( query, Functor(self._mail_queryCountForReturnCheckCb, playerBase) )

	def _mail_queryCountForCheckCb(self, playerBaseMailBox, result, dummy, errstr):
		"""
		��ѯ�ռ����ʼ���Ŀ�Ļص������������������ĵ����ʼ���ĿҲ�������涨��Ŀ�� ��������ʼ����͵���ҵ�cell

		@param playerBaseMailBox:	�����˵�base MailBox
		@type playerBaseMailBox:	mailbox
		"""
		self.mail_sending = False
		
	
		if int(result[0][0]) >= csconst.MAIL_UPPER_LIMIT:
			self.client.onStatusMessage( csstatus.MAIL_RECEIVER_MAILBOX_FULL, "" ) # �ռ�������������֪ͨ
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
		��ѯ�ռ����ʼ���Ŀ�Ļص������������������ĵ����ʼ���ĿҲ�������涨��Ŀ�� ��������ʼ����͵���ҵ�cell

		@param playerBaseMailBox:	�����˵�base MailBox
		@type playerBaseMailBox:	mailbox
		"""
		self.mail_sending = False
		#�˺���modified by����
		if int(result[0][0]) >= csconst.MAIL_UPPER_LIMIT:
			self.client.onStatusMessage( csstatus.MAIL_RECEIVER_MAILBOX_FULL, "" ) # �ռ�������������֪ͨ
			self.client.onStatusMessage( csstatus.MAIL_RETURN_FAILED, "" ) # ����ʧ��			
			return
		BigWorld.globalData["MailMgr"].returnMail( self, self.getName(), self.mail_returnInfo["id"] )

		#����������ʾ by����
		mailInfo = self.mail_returnInfo
		if mailInfo["senderType"] == csdefine.MAIL_SENDER_TYPE_RETURN:
			return
		self.client.onStatusMessage( csstatus.MAIL_RETURN_TO, str(( mailInfo["senderName"], )) ) # ���ųɹ�

	def mail_queryAll(self):
		"""
		exposed method
		��ѯ�ʼ�����Ҫ������ҵ�½����ʱ��һ���Բ�ѯ�����ʼ����á�
		"""
		# ��ѯ��������������ҵķ��������ͼ�����������ҵ��������͵��ż�
		self.mail_allInfo = {}
		query = "select id, sm_title, sm_content, sm_item0, sm_item1, sm_item2, sm_item3, sm_item4, sm_item5, sm_item6, sm_item7, sm_item8, sm_item9, sm_money, sm_senderName, sm_receiverName, sm_senderType, UNIX_TIMESTAMP(sm_receiveTime), UNIX_TIMESTAMP(sm_readedTime), UNIX_TIMESTAMP(sm_readedHintTime) from custom_MailTable where (sm_receiverName = '%s' and sm_senderType != %i) or (sm_senderName = '%s' and sm_senderType = %i)" % (BigWorld.escape_string( self.getName() ), csdefine.MAIL_SENDER_TYPE_RETURN, BigWorld.escape_string( self.getName() ), csdefine.MAIL_SENDER_TYPE_RETURN)
		BigWorld.executeRawDatabaseCommand( query, self._mail_queryAllCb )


	def _mail_queryAllCb(self, result, dummy, errstr):
		"""
		��ѯ�����ʼ����ݵĻص���������������ʼ�����֮�󣬱��ر���һ�ݡ�ͬʱ��ÿ���ʼ��Ĳ������ݷ��͵��ͻ��ˡ�
		�����ʼ����ݰ����� �ʼ�DBID�� �ʼ����⣬ �ʼ����ݣ� �ʼ�������Ʒ�� �ʼ�������Ǯ�� �����˵����֣� �����˵����֡�
						   �ʼ���Ʒ�Ƿ���ȡ�� �ʼ���Ǯ�Ƿ���ȡ�� �ʼ�ʱ�䣬 ����ʱ�䡣
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
						"itemTaken"		: 0,				# ������ʱ��¼��ǰ�Ƿ�������ȡ�ʼ���Ʒ
						"moneyTaken"	: 0,				# ������ʱ��¼��ǰ�Ƿ�������ȡ�ʼ���Ǯ
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
				# ��ҷ��͵��ż��ѳ���7��δ����ֱ�Ӻ��ԣ���mail managerͳһ�������Ŵ���
				# ������Ҫ��������Ϊ�����Ƕ��ڵ�ִ����Ϊ��ÿ��һ��ʱ��ִ��һ�Σ�
				continue
			self.mail_allInfo[id] = mail

		if len( self.mail_allInfo ):
			self.mail_initingmailIDs = self.mail_allInfo.keys()
			self.mail_initingmailIDs.sort()
			# ÿ0.1�뷢һ���ż����ͻ���
			self.mail_initingCtrlID = self.addTimer( 1, 0.1, ECBExtend.INIT_MAIL_TO_CLIENT_TIMER_CBID )

	def mail_delete(self, mailID):
		"""
		exposed method
		ɾ��ĳ���ʼ��ʼ�

		ɾ���ʼ����˵����ݿ���ȥɾ��֮�⣬��Ҫɾ��base����ĸ÷��ʼ���Ϣ��

		@param mailID: �ʼ���dbid
		@type  mailID: DATABASE_ID
		"""
		try:
			senderName = self.mail_allInfo[mailID]["senderName"]
			receiverName = self.mail_allInfo[mailID]["receiverName"]
			title = self.mail_allInfo[mailID]["title"]
			del self.mail_allInfo[mailID]
			# ֪ͨ�ͻ���ɾ������
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
		ɾ��ĳ���ʼ��ص����������ɾ��ʧ��ֻ������־�м�¼���ʧ�ܵĲ�������û�������ر���
		"""
		if errstr:
			ERROR_MSG(errstr)


	def mail_newNotify(self, senderName, timeFlag):
		"""
		define method
		֪ͨ�����ʼ������ǵ����˸���ǰ��Ҽ��ŵ�ʱ�򱻵��á�һ����MailManager���á�
		�ӵ����ʼ�֪ͨ��ʱ��,��ǰ��ҵ����ݿ���ȥ�����µ��ʼ���
		phw: ע���Ժ�����и��õĻ�ȡ���ʼ��ķ���������Ҫ�޸�

		@param senderName: �����ߵ����ƣ����ڲ��ҹ���
		@type  senderName: STRING
		@param   timeFlag: ����ʱ���ǣ����ڲ��ҹ���
		@type    timeFlag: INT32
		"""
		# ���������ҵ��ʼ����ҷ�������senderName������ʱ��ΪtimeFlag���ż���
		# ��Ȼ���������ڼ��̵�������п��ܻ��ж��������ڻص��û���д���
		query = "select id, sm_title, sm_content, sm_item0, sm_item1, sm_item2, sm_item3, sm_item4, sm_item5, sm_item6, sm_item7, sm_item8, sm_item9, sm_money, sm_senderName, sm_receiverName, sm_senderType, UNIX_TIMESTAMP(sm_receiveTime), UNIX_TIMESTAMP(sm_readedTime), UNIX_TIMESTAMP(sm_readedHintTime) from custom_MailTable where sm_receiverName = '%s' and sm_senderName = '%s' and sm_timeFlag = %i;" % (BigWorld.escape_string( self.getName() ), BigWorld.escape_string( senderName ), timeFlag)
		INFO_MSG( "%s(%i): sql cmd: %s" % ( self.getName(), self.id, query ) )
		BigWorld.executeRawDatabaseCommand( query, self._mail_newNotifyCb ) # ��¼�����ݿ�

	def _mail_newNotifyCb(self, result, dummy, errstr):
		"""
		֪ͨ�����ʼ��ص�����.
		����ص������Ѵ����ݿ��ȡ�������ʼ����뵽base���ʼ���Ϣ�С�
		ͬʱ�������ʼ��������ݷ��͵��ͻ��ˡ�
		"""
		if errstr:
			ERROR_MSG( "%s(%i): %s" % ( self.getName(), self.id, errstr ) )
			return

		for m in result:
			id = long( m[0] )
			if id in self.mail_allInfo:
				continue	# �����Ѿ��������б��е��ʼ������ǲ�ȡ����̬�ȣ���������ڼ��˵�״̬�ǻᷢ���ģ�
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
										"itemTaken"		: 0,				# ������ʱ��¼��ǰ�Ƿ�������ȡ�ʼ���Ʒ
										"moneyTaken"	: 0,				# ������ʱ��¼��ǰ�Ƿ�������ȡ�ʼ���Ǯ
									}
			mail = self.mail_allInfo[id]
			# id, title, senderName, senderType, receiveTime, readedTime, content, money, itemDatas
			self.client.mail_receive( id, mail["title"], mail["senderName"], mail["receiverName"],
										mail["senderType"], mail["receiveTime"], mail["readedTime"],
										mail["content"], mail["money"], mail["itemDatas"], mail["readedHintTime"] )

	def mail_addReturnMail(self, id, title, content, itemDatasStr, money, senderName, receiverName, senderType, receiveTime, readedTime, readedHintTime):
		"""
		define method
		�յ����Ŵ���
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
									"itemTaken"		: 0,				# ������ʱ��¼��ǰ�Ƿ�������ȡ�ʼ���Ʒ
									"moneyTaken"	: 0,				# ������ʱ��¼��ǰ�Ƿ�������ȡ�ʼ���Ǯ
								}
		#id, title, senderName, senderType, receiveTime, readedTime, content, money, itemDatas

		self.client.mail_receive( id, title, senderName, receiverName, senderType, receiveTime, readedTime, content, money, itemDatas, readedHintTime )
		#del self.mail_allInfo[mailID]
		#del self.mail_returnInfo[mailID]
		
	
	def mail_readedNotify( self, mailID ):
		"""
		exposed method
		�ʼ����Ķ�֪ͨ���˷����ɿͻ��˵��ã������Լ���ĳһ���ʼ��Ѷ���

		������
		@param mailID: �ʼ���dbid
		@type  mailID: DATABASE_ID
		"""
		if mailID not in self.mail_allInfo:
			ERROR_MSG( "error: %s(%i)No such mailID! the id is: %i " % ( self.getName(), self.id, mailID ))
			return

		mailInfo = self.mail_allInfo[mailID]
		if mailInfo["receiveTime"] > time(): # ��û���Ķ�ʱ��
			ERROR_MSG( "error: The mail is not come! the id is: %i " % ( mailID ))
			return

		if mailInfo["readedTime"] == 0:		# û�п����������ݵĲ鿴ʱ��
			mailInfo["readedTime"] = time()
			mailInfo["readedHintTime"] = time()
			query = "update custom_MailTable set sm_readedTime = now(), sm_readedHintTime = now() where id = %i." % (mailID)
			BigWorld.executeRawDatabaseCommand( query, Functor(self._mail_readedCb, mailID) )
	

	def mailHint_readedNotify( self, mailID ) :
		"""
		exposed method
		�ʼ���ʾ���Ķ�֪ͨ���˷����ɿͻ��˵��ã������Լ���ĳһ���ʼ��Ѷ���

		������
		@param mailID: �ʼ���dbid
		@type  mailID: DATABASE_ID
		"""	
		mailInfo = self.mail_allInfo[mailID]
		if mailID not in self.mail_allInfo:
			ERROR_MSG( "error: %s(%i)No such mailID! the id is: %i " % ( self.getName(), self.id, mailID ))
			return

		if mailInfo["readedHintTime"] == 0 :		# û�п����ʼ���ʾ�������ݵĲ鿴ʱ��
			mailInfo["readedHintTime"] = time()
			query = "update custom_MailTable set  sm_readedHintTime = now() where id = %i." % ( mailID )
			BigWorld.executeRawDatabaseCommand( query, Functor(self._mailHint_readedCb, mailID) )		
	
	def _mail_readedCb(self, mailID, result, dummy, errstr):
		"""
		�Ķ��ʼ��ص�������
		���������Ҫ��˵���Ķ��ʼ���д���ݿ��Ƿ�������������������Ѳ��������ʼ�ID��¼������
		����û��ʲô����
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
		�Ķ��ʼ���ʾ�ص�������
		���������Ҫ��˵���Ķ��ʼ���ʾ��д���ݿ��Ƿ�������������������Ѳ��������ʼ�ID��¼������
		����û��ʲô����
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
		���ȡ�ʼ���Ʒ��

		���̣����ȡ�ʼ�������Ʒ���ߵ���һ��������ֱ�Ӵ����base���ʼ�������ȡ���ʼ���Ʒ��������Ʒ���͸�
		���cell��

		������
		@param mailID: �ʼ���dbid
		@type  mailID: DATABASE_ID
		"""
		if mailID not in self.mail_allInfo:
			ERROR_MSG( "error: No such mailID! the id is: %i " % ( mailID ))
			return

		mailInfo = self.mail_allInfo[mailID]
		if mailInfo["receiveTime"] > time():		# ��û���Ķ�ʱ��
			ERROR_MSG( "error: The mail is not come! the id is: %i " % ( mailID ))
			return

		if len( mailInfo["itemDatas"] ) == 0:				# ���ʼ�û����Ʒ
			ERROR_MSG( "error: The mail has no item ! the id is: %i " % ( mailID ))
			return

		if mailInfo["itemTaken"] == 1:				# ��Ʒ����ȡ����
			ERROR_MSG( "error: The item has been Taken! the id is: %i " % ( mailID ))
			return

		if len( mailInfo["itemDatas"] ) < index:
			return

		# ����ȡ��ǣ��Է�ֹͬһʱ���������յ�ͬ������Ϣ
		# ����ǰ�����������ݿ��sm_item����Ϊ""�������cell�ص�֪ͨ�ɹ�ʱ�Ż��������á�
		mailInfo["itemTaken"] = 1
		self.cell.mail_receiveItem( mailID, mailInfo["itemDatas"][index], index )

	def mail_getAllItem( self, mailID ):
		"""
		define method
		���ȡ�ʼ���Ʒ��

		���̣����ȡ�ʼ�������Ʒ���ߵ���һ��������ֱ�Ӵ����base���ʼ�������ȡ���ʼ���Ʒ��������Ʒ���͸�
		���cell��

		������
		@param mailID: �ʼ���dbid
		@type  mailID: DATABASE_ID
		"""
		if mailID not in self.mail_allInfo:
			ERROR_MSG( "error: No such mailID! the id is: %i " % ( mailID ))
			return

		mailInfo = self.mail_allInfo[mailID]
		if mailInfo["receiveTime"] > time():		# ��û���Ķ�ʱ��
			ERROR_MSG( "error: The mail is not come! the id is: %i " % ( mailID ))
			return

		if len( mailInfo["itemDatas"] ) == 0:				# ���ʼ�û����Ʒ
			ERROR_MSG( "error: The mail has no item ! the id is: %i " % ( mailID ))
			return
		#����ط����������ƻ�ȡ��Ʒ̫������²������Ƶ�����
		#��Ҫ����������ƣ��������ˢ��Ʒ
		if mailInfo["itemTaken"] == 1:				# ��Ʒ����ȡ����
			ERROR_MSG( "error: The item has been Taken! the id is: %i " % ( mailID ))
			return

		# ����ȡ��ǣ��Է�ֹͬһʱ���������յ�ͬ������Ϣ
		# ����ǰ�����������ݿ��sm_item����Ϊ""�������cell�ص�֪ͨ�ɹ�ʱ�Ż��������á�
		mailInfo["itemTaken"] = 1
		self.cell.mail_receiveAllItem( mailID, mailInfo["itemDatas"] )

	def mail_getItemRegister( self, mailID, status, index ):
		"""
		define method
		���ȡ����Ʒ�󣬵�base����ȷ�ϡ�ͬʱҲ���޸����ݿ⡣��ҵ�cell���á�

		������
		@param mailID: �ʼ���dbid
		@type  mailID: DATABASE_ID
		@param status: ��ȡ״̬��0 ��ʾ��ȡʧ�ܣ�1��ʾ��ȡ�ɹ�
		@type  status: INT8
		"""
		if status:
			fieldStr = "sm_item%s" % index
			itemDatas = self.mail_allInfo[mailID]["itemDatas"]
			itemDatas[ index ] = BigWorld.escape_string( cPickle.dumps( {}, 2 ) )
			query = "update custom_MailTable set %s = '%s' where id = %i" % ( fieldStr, itemDatas[index], mailID )
			#query = "update custom_MailTable ( sm_item0, sm_item1, sm_item2, sm_item3, sm_item4, sm_item5, sm_item6, sm_item7, sm_item8, sm_item9 ) values ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ) where id = %i" % ( itemDatas[0], itemDatas[1], itemDatas[2], itemDatas[3], itemDatas[4], itemDatas[5], itemDatas[6], itemDatas[7], itemDatas[8], itemDatas[9], mailID )
			BigWorld.executeRawDatabaseCommand( query, Functor( self._mail_getItemRegisterCb, mailID, itemDatas ) )#��¼�����ݿ�
			self.client.mail_itemHasGotten( mailID, index )

		#if len( self.mail_allInfo[mailID]["itemDatas"]) != 0:
		self.mail_allInfo[mailID]["itemTaken"] = 0	# ��ȡʧ�ܺ���Ҫ����״̬��������ҽ��޷�������ȡ

	def mail_getAllItemRegister( self, mailID, status, failedIndexList = [] ):
		"""
		define method
		���ȡ����Ʒ�󣬵�base����ȷ�ϡ�ͬʱҲ���޸����ݿ⡣��ҵ�cell���á�

		������
		@param mailID: �ʼ���dbid
		@type  mailID: DATABASE_ID
		@param status: ��ȡ״̬��0 ��ʾ��ȡʧ�ܣ�1��ʾ��ȡ�ɹ�
		@type  status: INT8
		"""
		if status:
			# �и�����Ʒ���ʧ����
			itemDatas = self.mail_allInfo[mailID]["itemDatas"]
			itemsString = []
			for index in xrange( 0, len( itemDatas ) ):
				if not index in failedIndexList:
					itemDatas[index] = cPickle.dumps( {}, 2 )
				#itemDatas[index] = BigWorld.escape_string( itemDatas[index] )
				itemsString.append( BigWorld.escape_string( itemDatas[index] ) )
			query = "update custom_MailTable set sm_item0='%s', sm_item1='%s', sm_item2='%s', sm_item3='%s', sm_item4='%s', sm_item5='%s', sm_item6='%s', sm_item7='%s', sm_item8='%s', sm_item9='%s' where id = %i" % ( itemsString[0], itemsString[1], itemsString[2], itemsString[3], itemsString[4], itemsString[5], itemsString[6], itemsString[7], itemsString[8], itemsString[9], mailID )
			BigWorld.executeRawDatabaseCommand( query, Functor( self._mail_getAllItemRegisterCb, mailID, itemDatas ) )	#��¼�����ݿ�
			self.client.mail_itemAllHasGotten( mailID, failedIndexList )

		self.mail_allInfo[mailID]["itemTaken"] = 0

	def _mail_getItemRegisterCb(self, mailID, itemDatas, result, dummy, errstr):
		"""
		�����ݿ��¼��Ʒ�Ѿ���ȡ�ߺ�Ļص�������

		���������Ҫ��˵��ȡ����Ʒ��д���ݿ��Ƿ�������������������Ѳ��������ʼ�ID��¼������
		����û��ʲô����

		������
		@param mailID: �ʼ���dbid
		@type  mailID: DATABASE_ID
		"""
		if errstr:
			ERROR_MSG( "%s(%i): set mail item be taken note error! the id is: %i " % ( self.getName(), self.id, mailID ), errstr )# , repr( itemData )

	def _mail_getAllItemRegisterCb(self, mailID, itemDatas, result, dummy, errstr):
		"""
		�����ݿ��¼������Ʒ�Ѿ���ȡ�ߺ�Ļص�������
		���������Ҫ��˵��ȡ����Ʒ��д���ݿ��Ƿ�������������������Ѳ��������ʼ�ID��¼������
		����û��ʲô����
		������
		@param mailID: �ʼ���dbid
		@type  mailID: DATABASE_ID
		"""
		if errstr:
			ERROR_MSG( "%s(%i): set mail item be taken note error! the id is: %i " % ( self.getName(), self.id, mailID ), errstr )

	def mail_getMoney(self, mailID):
		"""
		define method
		���ȡ�ʼ���Ǯ��

		���̣����ȡ�ʼ�������Ǯ���ߵ���һ��������ֱ�Ӵ����base���ʼ�������ȡ���ʼ���Ǯ�����ѽ�Ǯ���͸�
		���cell��

		������
		@param mailID: �ʼ���dbid
		@type  mailID: DATABASE_ID
		"""
		if mailID not in self.mail_allInfo:
			ERROR_MSG( "error: No such mailID! the id is: %i " % ( mailID ))
			return

		mailInfo = self.mail_allInfo[mailID]
		if float(mailInfo["receiveTime"]) > time(): # ��û���Ķ�ʱ��
			ERROR_MSG( "error: The mail is not come! the id is: %i " % ( mailID ))
			return
		if mailInfo["money"] == 0:		# ���ʼ�û�н�Ǯ
			ERROR_MSG( "error: The mail has no money ! the id is: %i " % ( mailID ))
			return
		if mailInfo["moneyTaken"] == 1:  # ��Ǯ����ȡ����
			ERROR_MSG( "error: The money has been Taken! the id is: %i " % ( mailID ))
			return

		# ����ȡ��ǣ��Է�ֹͬһʱ���������յ�ͬ������Ϣ
		# ����ǰ�����������ݿ�sm_moneyΪ0�������cell�ص�֪ͨ�ɹ�ʱ�Ż��������á�
		mailInfo["moneyTaken"] = 1
		self.cell.mail_receiveMoney(mailID, int(mailInfo["money"]))
		return

	def mail_getMoneyRegister(self, mailID, status):
		"""
		define method
		���ȡ�ý�Ǯ�󣬵�base����ȷ�ϡ�ͬʱҲ���޸����ݿ⡣��ҵ�cell���á�
		������
		@param mailID: �ʼ���dbid
		@type  mailID: DATABASE_ID
		@param status: ��ȡ״̬��0 ��ʾ��ȡʧ�ܣ�1��ʾ��ȡ�ɹ�
		@type  status: INT8
		"""
		if status:
			query = "update custom_MailTable set sm_money = 0 where id = %i" % (mailID)
			BigWorld.executeRawDatabaseCommand( query, Functor( self._mail_getMoneyRegisterCb, mailID, self.mail_allInfo[mailID]["money"] ) )#��¼�����ݿ�
			self.mail_allInfo[mailID]["money"] = 0
			self.client.mail_moneyHasGotten( mailID )
		else:
			self.mail_allInfo[mailID]["moneyTaken"] = 0	# ��ȡʧ�ܺ���Ҫ����״̬��������ҽ��޷�������ȡ

	def _mail_getMoneyRegisterCb(self, mailID, moneyAmount, result, dummy, errstr):
		"""
		�����ݿ��¼��Ǯ�Ѿ���ȡ�ߺ�Ļص�������

		���������Ҫ��˵��ȡ�߽�Ǯ��д���ݿ��Ƿ�������������������Ѳ��������ʼ�ID��¼������
		����û��ʲô����

		������
		@param mailID: �ʼ���dbid
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
		#���ű����ʽ���� ��Ӳ��� recieverName by����
		# id, title, senderName, senderType, receiveTime, readedTime, content, money, itemData
		self.client.mail_receive( k, m["title"], m["senderName"], m["receiverName"], m["senderType"], m["receiveTime"], m["readedTime"], m["content"], m["money"], m["itemDatas"], m["readedHintTime"] )

	def mail_returnNotifyFC( self, mailID ):
		"""
		exposed method.
		�ɿͻ��˵��ã�֪ͨ�������š�

		@param mailID: �ʼ�Ψһ��ʶ(dbid)
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
			# �����������ż�û�ж������ҳ�����7�죬���Ҹ���������ҷ��͹�����

			# ����ʽ��Ϊ��ͳһ�������ţ�������������ʲô��������
			# �����Ǵ���ʱ������ɾ������˵����ţ�����Ľ����ʼ��������Լ�ͳһ��ʱ�Ĵ���
			del self.mail_allInfo[mailID]
		else:
			ERROR_MSG( "%s(%i): invalid mail! the id is: %i " % ( self.getName(), self.id, mailID ) )
			return

	def mail_systemReturn( self, mailID ):
		"""
		define method
		��ʱ�ż�������ϵͳ�Զ�����,�����������ֻ�Ǵ��������˵Ľ�����Ϣ��client��base�ϱ������Ϣ�ĸ��£�����������ɾ�����ݿ���ż�
		"""
		if mailID not in self.mail_allInfo:
			ERROR_MSG( "error: No such mailID! the id is: %i " % ( mailID ))
			return
		del self.mail_allInfo[mailID]  #ɾ��base�ϱ����˸��ʼ���Ϣ
		self.client.mail_systemReturn( mailID )	#���¿ͻ��˵��ʼ��б�	
		
	def mail_playerReturn( self, mailID ):
		"""
		exposed method
		�����������
		@param mailID: �ʼ���Ψһ��ʶ��(dbid)
		"""
		if mailID not in self.mail_allInfo:
			ERROR_MSG( "error: No such mailID! the id is: %i " % ( mailID ))
			return

		#���Է������Ƿ����� ��������ʧ�� modified by����
		mailInfo = self.mail_allInfo[mailID]
		
		
		#��ҵ���ʼ������ϵ��������Ĵ���Ҫ�޸����ŵ��ż��Ĳ鿴ʱ����ʼ���ʾ�鿴ʱ��
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
									"itemTaken"		: mailInfo["itemTaken"],				# ������ʱ��¼��ǰ�Ƿ�������ȡ�ʼ���Ʒ
									"moneyTaken"	: mailInfo["moneyTaken"],				# ������ʱ��¼��ǰ�Ƿ�������ȡ�ʼ���Ǯ
								}
		receiverName = mailInfo["receiverName"]
		#self.mail_send(self, receiverName, mailType, title, content, money, uids, hasItem, selfnpcID):
		"""
		#ֱ����npc�õķ��Žӿڴ�����������
		itemDatas = [] #����һ�ݣ����������ɾ��ʱ��������ô��󣬴Ӷ�ʹ���ռ���ȡ������Ʒ
		itemDatas = mailInfo["itemDatas"]
		mailInfo["title"] = lbDatas.WITHDRAW_TITLE % ( mailInfo["receiverName"], mailInfo["title"] )
		BigWorld.globalData["MailMgr"].send( None, mailInfo["senderName"], 1, csdefine.MAIL_SENDER_TYPE_RETURN, mailInfo["receiverName"], mailInfo["title"], mailInfo["content"], mailInfo["money"], itemDatas )
		del self.mail_allInfo[mailID]
		self.client.onMailDeleted( mailID )
		#����ɾ���ˣ��յ�����ŵ��˾�ȡ������Ʒ�ˣ��������Ʒ����ֱ��ʹ��mailInfo��������õ��ã�ʵ��Щ��Ʒֻ��һ�ݣ�ֻ�����������ŵ�ʱ��������һ�ݣ�������ô��󣬴�ʱ��Ҫ��
		self.client.mail_delete( mailID )
		"""
		BigWorld.lookUpBaseByName( "Role", receiverName, self._mailReturn_getPlayerMailboxCb)

	def onReturnMail( self, mailID ):
		"""
		define method
		"""
		# �����˻ظ�������
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
		�����ʼ�ʱ��ص�������
		���������Ҫ��˵���Ķ��ʼ���д���ݿ��Ƿ�������������������Ѳ��������ʼ�ID��¼������
		����û��ʲô����
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
		�����ʼ�ʱ��ص�������
		���������Ҫ��˵���Ķ��ʼ���д���ݿ��Ƿ�������������������Ѳ��������ʼ�ID��¼������
		����û��ʲô����
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
		���ұ������߻ص�
		@param		mailID		: �����ʼ���ID
		@type		mailID		: DATABASE_ID
		@param		callResult	: BigWorld.lookUpBaseByName�Ĳ��ҽ��,mailbox��True��False���п���
		@type		callResult	: bool or mailbox
		"""
		if isinstance( callResult, bool ) : return
		# ��������������ߣ���֪ͨ�����������ʼ�
		#print callResult
		#callResult.mail_queryAll()
		#return
		#print "_findReceiverCallback", mailID, callResult
		query = "select id, sm_title, sm_content, sm_item0, sm_item1, sm_item2, sm_item3, sm_item4, sm_item5, sm_item6, sm_item7, sm_item8, sm_item9, sm_money, sm_senderName, sm_receiverName, sm_senderType, UNIX_TIMESTAMP(sm_receiveTime), UNIX_TIMESTAMP(sm_readedTime), UNIX_TIMESTAMP(sm_readedHintTime) from custom_MailTable where id = %i " % mailID
		BigWorld.executeRawDatabaseCommand( query, Functor( self._mail_queryReturnMailCB, callResult ) )

	def _mail_queryReturnMailCB( self, receiver, result, dummy, errstr ) :
		"""
		֪ͨ�������߽����ʼ�
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
		itemsString = cPickle.dumps( itemDatas, 2 ) #��������Ʒ�����string��ʽ�ַ���	
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
