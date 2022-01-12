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
	�ʼ�ϵͳ���cell�˽ӿ�
	"""

	def __init__( self ):
		"""
		"""
		self.mails = {}				# �ͻ��˱���������ʼ��б�
		self.singleMail = {}		#һ���ʼ�������
		self.currentmailID = 0		#��ǰ�鿴���ʼ�mailID
		self.npcID = 0
		self.__delaySendCBID = {}	# ��ǰδ����ȡʱ����Ҫ��ʱ���͵��ʼ���callback ID
		self.mailIndex = -1
		self.mail_checkTimerID = -1

	def enterMailWithNPC( self, objectID ):
		"""
		Define Method
		�����ʼ�
		@param   objectID: ����Ŀ��
		@type    objectID: OBJECT_ID
		@return: ��
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The trade NPC  %s has not exist " % objectID )
			return
		# ȡ���ʼ��б�
		self.mail_checkOutDated()
		ECenter.fireEvent( "EVT_ON_TOGGLE_MAIL_BOX", entity )
		self.npcID = objectID # �˴ζԻ�npcID

	def mailOverWithNPC( self ):
		player = BigWorld.player()
		self.npcID = 0

	def mail_send( self, receiverName, mailtype, title, content, money, uids ):
		"""
		���̣�
		�����ж��ʼ����ⳤ��,�ʼ����ݳ����Ƿ�ϸ��ڼ�¼�ʼ�����Ϣ,����ʼ����������ҿ��Ƿ���ڡ�

		������
		@param receiverName:	����������
		@type receiverName:		string
		@param mailtype:		�ʼ�����
		@type mailtype:			int8
		@param title:			�ʼ��ı���
		@type title:			string
		@param content:			�ʼ�������
		@type content:			string
		@param money:			�ʼ������Ľ�Ǯ
		@type money:			unit32
		@param uids:			�ʼ���������Ʒ��ΨһID�����û����Ʒ����[]
		@type uids:				int64
		@param npcId:			�����õ�������id
		@type npcId:			object_id
		"""
		npc = BigWorld.entities.get( self.npcID ) #�Ƿ��ܻ�ø�npc
		if npc == None:
			self.statusMessage(csstatus.MAIL_MAILBOX_NOT_EXIST)
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE: #npc�����ж�
			self.statusMessage(csstatus.MAIL_MAILBOX_IS_TOO_FAR)
			ECenter.fireEvent( "EVT_ON_MAIL_SEND_SUCCED", False )
			return

		if len(title) > csconst.MAIL_TITLE_LENGTH_MAX: #���ⳤ��С��13���ּ��
			self.statusMessage(csstatus.MAIL_TITLE_TOO_LONG)
			ECenter.fireEvent( "EVT_ON_MAIL_SEND_SUCCED", False )
			return
		
		if rds.wordsProfanity.searchMsgProfanity( title ) is not None:
			self.statusMessage( csstatus.TITLE_HAS_PROFANITY )
			return
		
		if len(content) > csconst.MAIL_CONTENT_LENGTH_MAX: #���ݳ���С��250���ּ��
			self.statusMessage(csstatus.MAIL_CONTENT_TOO_LONG)
			ECenter.fireEvent( "EVT_ON_MAIL_SEND_SUCCED", False )
			return

		if rds.wordsProfanity.searchMsgProfanity( content ) is not None:
			self.statusMessage( csstatus.CONTENT_HAS_PROFANITY )
			return

		hasItem = False

		#tempOrders = []
		if uids != []:			# ��ʾ����Ʒ
			hasItem = True

		self.base.mail_send( receiverName, mailtype, title, content, money, uids, hasItem, self.npcID )

	def mail_checkOutDated( self ):
		"""
		ɾ����ʱ��GM,npc�ʼ�
		���Ѿ��Ķ�����������Сʱ���ʼ�
		"""
		if self is not BigWorld.player():
			return
		t = Time.Time.time()
		deleteMailIDs = []
		returnMailIDs = []
		newMailDeleted = False
		for id, mail in self.mails.iteritems():		# ע������������ֱ��ɾ��self.mails�е�item����Ϊ����˲�����ʹ��iteritems()
			if ( mail["readedTime"] == 0 ) and ( t - mail["receiveTime"] > csconst.MAIL_NPC_OUTTIMED ):
				# ��������7��δ�����ż���Ҫ����ɾ�����������š�NPC�ż���GM�ż���
				if mail["senderType"] != csdefine.MAIL_SENDER_TYPE_PLAYER:
					# ����ҷ��͵��ʼ�
					deleteMailIDs.append( id )
				else:
					# ����ҷ��͵��ż�������Ҫ��������
					# ��Ȼ�������ɷ�����ͳһ����ģ������ڷ����������ż����һ����ʱ����
					# �����Ҫ׼ȷ�����ż����ڵ�������ɿͻ�������֪ͨһ�·�����
					# �����ڱ�֤���ݵ�һ���ԣ�������Σ�������������Ҫ����ʱ�б���ɾ������ŵģ�
					returnMailIDs.append( id )


				# ����Ҫ�����δ���ʼ�
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

#				ECenter.fireEvent( "EVT_ON_MAIL_DEL_LETTER", id ) # ɾ�����ڵ��ż�
		for id in deleteMailIDs:
			self.mail_delete( id )

		for id in returnMailIDs:
			self.base.mail_returnNotifyFC( id )
			del self.mails[id]
			# to do, ���ﻹ��Ҫ����һ��������Ϣ���Ը��½������ʾ��ʾ������Ϣ
			ECenter.fireEvent( "EVT_ON_MAIL_DEL_LETTER", id ) #�����������

		# ����Ƿ���δ���ʼ�
		if newMailDeleted and self.hasReadAllMailsHints() :
			ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_HINT_NOTIFY" )  #�Ѿ��Ķ���ȫ���ʼ���ʾ��ͼ��ͼ����˸��ʧ
		if newMailDeleted and self.hasReadAllMails()  :
			ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_NOTIFY" )

	def mail_read( self, mailID ):
		"""
		�Ķ�һ���ʼ�

		@param mailID: �ʼ���DBID
		@type  mailID: uint32
		@param  npcId: �����õ�������id
		@type   npcId: object_id
		"""
		npc = BigWorld.entities.get( self.npcID ) #�Ƿ��ܻ�ø�npc
		if npc == None:
			self.statusMessage(csstatus.MAIL_MAILBOX_NOT_EXIST)
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE: #npc�����ж�
			self.statusMessage(csstatus.MAIL_MAILBOX_IS_TOO_FAR)
			return

		if not self.mails.has_key( mailID ):
			self.statusMessage( csstatus.MAIL_NOT_EXIST )
			return

		if self.mails[mailID]["receiveTime"] > Time.Time.time():
			self.statusMessage( csstatus.MAIL_NOT_EXIST )			# ��û�е�����ʱ�䣬���Ų�����
			return
		isNewMail = False
		if not self.hasReadAllMails() :
			isNewMail = True
		isNewMailHint = False
		if not self.hasReadAllMailsHints() :
			isNewMailHint = True 
		if isNewMail :												# ��ȡ��һ��δ��ȡ�����ʼ�
			self.mails[mailID]["readedTime"] = Time.Time.time()
			self.base.mail_readedNotify( mailID )
			self.mails[mailID]["readedHintTime"] =Time.Time.time()
			self.base.mailHint_readedNotify( mailID )
		ECenter.fireEvent( "EVT_ON_MAIL_READ_LETTER", mailID ) 		# �Ķ��ʼ�
		
		if isNewMail and self.hasReadAllMails() :        #�Ѿ��Ķ���ȫ���ʼ����ʼ�ͼ����ʧ
			ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_NOTIFY" )
			ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_HINT_NOTIFY" )  #�Ѿ��Ķ���ȫ���ʼ���ʾ��ͼ��ͼ����˸��ʧ
		if isNewMail and self.hasReadAllMailsHints() :
			ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_HINT_NOTIFY" )  #�Ѿ��Ķ���ȫ���ʼ���ʾ��ͼ��ͼ����˸��ʧ
			
			
			
		# to do, ��������봦�������ȡ�ʼ��Ĵ���
		# ���Կ��Ǵ���һ���յ��ʼ����ݵ���Ϣ��
		# ��ı�һ�º�����(�磺mail_get())��ֱ�ӷ����ʼ����ݡ�
		return
	
	
	"""
	def mailHint_readedNotify ( self, mailID ) :
		self.base.mailHint_readedNotify( mailID )
	"""
	def mail_query( self ):
		"""
		�鿴�����ʼ�������Ϣ
		�ʼ������ݶ����ڱ���,���Բ鿴��ʱ��,ֱ�Ӹ�����Ҫ�� ��� self.mails{}
		"""
		self.mails= {}
		self.base.mail_queryAll()	#���߼���������ʼ��ļ�Ҫ��Ϣ

	def mail_delete(self, mailID):
		"""
		@param mailID: �ʼ���DBID
		@type  mailID: DATABASE_ID
		"""
		if not self.mails.has_key( mailID ):
			return

		self.base.mail_delete(mailID)

	def mail_getItem( self, mailID, index ):
		"""
		�����ȡ�ʼ���Ʒ
		@param mailID: �ʼ���DBID
		@type  mailID: DATABASE_ID
		@param  npcId: �����õ�������id
		@type   npcId: object_id
		"""
		npc = BigWorld.entities.get( self.npcID ) #�Ƿ��ܻ�ø�npc
		if npc == None:
			self.statusMessage(csstatus.MAIL_MAILBOX_NOT_EXIST)
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:	# npc�����ж�
			self.statusMessage(csstatus.MAIL_MAILBOX_IS_TOO_FAR)
			return

		if not self.mails.has_key( mailID ):
			self.statusMessage(csstatus.MAIL_NOT_EXIST)
			return

		if self.getNormalKitbagFreeOrderCount() < 1:
			self.statusMessage( csstatus.PCU_NOT_ENOUGH_GRID )
			return

		if self.mailHasItemConut( mailID ) == 0:
			# ���ʼ�û����Ʒ
			return

		self.cell.mail_getItem( mailID, self.npcID, index )

	def mail_getAllItem( self, mailID ):
		"""
		���ʼ���Ʒ���� ȫ����ȡ
		@param mailID: �ʼ���DBID
		@type  mailID: DATABASE_ID
		@param  npcId: �����õ�������id
		@type   npcId: object_id
		"""
		npc = BigWorld.entities.get( self.npcID ) #�Ƿ��ܻ�ø�npc
		if npc == None:
			self.statusMessage(csstatus.MAIL_MAILBOX_NOT_EXIST)
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:	# npc�����ж�
			self.statusMessage(csstatus.MAIL_MAILBOX_IS_TOO_FAR)
			return

		if not self.mails.has_key( mailID ):
			self.statusMessage(csstatus.MAIL_NOT_EXIST)
			return

		mailItemNum = self.mailHasItemConut( mailID )
		if mailItemNum == 0:
			# ���ʼ�û����Ʒ
			return

		if self.getNormalKitbagFreeOrderCount() < mailItemNum:
			self.statusMessage( csstatus.PCU_NOT_ENOUGH_GRID )
			return

		self.cell.mail_getAllItem( mailID, self.npcID )

	def mail_getMoney( self, mailID ):
		"""
		������ȡ�ʼ���Ǯ
		@param mailID: �ʼ���DBID
		@type  mailID: DATABASE_ID
		@param  npcId: �����õ�������id
		@type   npcId: object_id
		"""
		npc = BigWorld.entities.get( self.npcID ) #�Ƿ��ܻ�ø�npc
		if npc == None:
			self.statusMessage(csstatus.MAIL_MAILBOX_NOT_EXIST)
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE: #npc�����ж�
			self.statusMessage(csstatus.MAIL_MAILBOX_IS_TOO_FAR)
			return

		if not self.mails.has_key( mailID ):
			self.statusMessage(csstatus.MAIL_NOT_EXIST)
			return

		if self.mails[mailID]["money"] <= 0:
			# ���ʼ�û�н�Ǯ
			return

		self.cell.mail_getMoney( mailID, self.npcID )
		self.mails[mailID]["money"] = 0

	def mail_receive( self, mailID, title, senderName, receiverName, senderType, receiveTime, readedTime, content, money, itemDatas, readedHintTime ):
		"""
		define method
		��ȡ�ʼ�
		���ã���ҵ�½��ʱ��,ͨ�������� self.base.mail_queryAll()���������ʼ�����,����������������ڽ����ʼ����ݵġ�
		���������������ʼ���ʱ��,Ҳͨ��������������ʼ�֪ͨ��ҡ�

		���ǣ�	������һ��������ڣ�����������ߵ�ʱ���ʸ������Ƿ�������ʱ�䣬���Ѿ����͸��ͻ��ˣ�
				Ҳ����˵���������ƽ��˿ͻ��˾Ϳ�������ʱ��鿴�ż����ݡ��ҵ��뷨�ǣ��ʼ���Ҫ��������
				�����Է��ͽ�Ǯ����Ʒ����������Է��ͽ�Ǯ����Ʒ����ôӦ��û��ʲô�˻�����ȥ���ʼ�����Ȼ
				��ˣ���ô����ֻҪ��֤��Ǯ����Ʒ�Ļ�ȡʱ����ȷ����ô����ڿͻ����Ƿ��ܿ��ü��ʼ����ݲ�
				���Ǻ���Ҫ�����ݷ��ڿͻ��˷��������ӿͻ��˵ı����ԡ�

		@param      mailID: �ʼ���DBID
		@type       mailID: DATABASE_ID
		@param       title: �����õ�������id
		@type        title: string
		@param  senderName: ������
		@type   senderName: string
		@param  senderType: �����õ�������id
		@type   senderType: string
		@param receiveTime: ����ʱ��
		@type  receiveTime: string
		@param  readedTime: �ż���ȡʱ��
		@type   readedTime: string
		@param     content: �ʼ�������
		@type      content: string
		@param       money: �ʼ������Ľ�Ǯ��Ŀ
		@type        money: string
		@param    itemDatas: �ʼ�������Ʒ�б������
		@type     itemDatas: array of string
		"""
		#���ű����ʽ���� ��Ӳ��� recieverName by����
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
		#���ű��⴦�� by����
		if self.mails[mailID]["senderType"]  == csdefine.MAIL_SENDER_TYPE_RETURN:
			self.mails[mailID]["title"] = lbDatas.WITHDRAW_TITLE % ( receiverName, self.mails[mailID]["title"] )
			#self.mails[mailID]["readedTime"] = 0
			#self.mails[mailID]["readedHintTime"] = 0
			#self.base.mail_returnNotifyFC( mailID ) #����ʱ���޸�readedTime��readedHintTime
		self.mailIndex += 1
		#
		ECenter.fireEvent( "EVT_ON_MAIL_ADD_LETTER", self.mailIndex, mail )# ����淢���ʼ�ʵ��
		if mail["readedTime"] == 0 :
			ECenter.fireEvent( "EVT_ON_NOTIFY_NEW_MAIL" )
	
	
	
	
	def mail_moneyHasGotten( self, mailID ):
		"""
		define method.
		�ɷ��������ã�֪ͨ�ͻ��ˣ�ĳ���ʼ��Ľ�Ǯ�ѳɹ�ȡ��
		"""
		if mailID not in self.mails:
			return
		self.mails[mailID]["money"] = 0
		# to do, ���ﴥ����Ǯȡ�ߵ���Ϣ���Ը��½���
		ECenter.fireEvent( "EVT_ON_MAIL_HAS_GETTTEN_MONEY", mailID )
		ECenter.fireEvent( "EVT_ON_MAIL_UPDATE_LETTER", mailID )
	#	ECenter.fireEvent( "EVT_ON_MAIL_HAS_GETTEN_ALL_ITEMS", mailID)

	def mail_itemHasGotten( self, mailID, index ):
		"""
		define method.
		�ɷ��������ã�֪ͨ�ͻ��ˣ�ĳ���ʼ�����Ʒ�ѳɹ�ȡ��
		"""
		if mailID not in self.mails:
			return
		#if len(self.mails[mailID]["items"]) < index:
		#	return
		self.mails[mailID]["items"][index] = None
		# to do, ���ﴥ����Ʒȡ�ߵ���Ϣ���Ը��½���
		ECenter.fireEvent( "EVT_ON_MAIL_HAS_GETTEN_ITEM", mailID, index )

	def mail_itemAllHasGotten( self, mailID, failedIndexList ):
		"""
		define method.
		�ɷ��������ã�֪ͨ�ͻ��ˣ��ʼ���������Ʒ���ѳɹ�ȡ��
		"""
		if mailID not in self.mails:
			return

		#itemList = self.mails[mailID]["items"]

		if self.mailHasItemConut( mailID ) == 0:
			# ����ʼ���û����Ʒ
			return
		newItemList = []
		for index in xrange( 10 ):
			if not index in failedIndexList:
				self.mails[mailID]["items"][index] = None
		# to do, ���ﴥ����Ʒȡ�ߵ���Ϣ���Ը��½���
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
		��ʱ�ż�������ϵͳ�Զ�����,�����������ֻ�Ǵ��������˵Ľ�����Ϣ��client��base�ϱ������Ϣ�ĸ��£�����������ɾ�����ݿ���ż�
		"""
		self.onMailDeleted( mailID )
		
	def onMailDeleted( self, mailID ):
		"""
		define method
		������ɾ���ʼ��ɹ���֪ͨ�ͻ���ɾ����Ӧ�ʼ�
		"""
		# to do, �����ﴥ��һ��ĳ���ʼ���ɾ������Ϣ�����ý������
		# ����ɽ����������õ���ʵ���Բ���Ҫ���������Ϣ��
		# �����ǻ�����������Ϊ�ᵼ���ż���ɾ���������Ҫ�����ﴥ����Ϣ

		isNewMail = self.mails[mailID]["readedTime"] == 0
		del self.mails[mailID]
		ECenter.fireEvent( "EVT_ON_MAIL_DEL_LETTER", mailID ) # �������ɾ���ʼ�
		self.mailIndex -= 1
		if isNewMail and self.hasReadAllMails() :
			ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_NOTIFY" )
			ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_HINT_NOTIFY" )  #�Ѿ��Ķ���ȫ���ʼ���ʾ��ͼ��ͼ����˸��ʧ			

	def hasReadAllMails( self ) :
		"""
		����Ƿ��Ѷ�ȡȫ���ʼ�
		"""
		for mail in self.mails.itervalues() :
			if mail["readedTime"] == 0 :				# ����δ���ʼ�
				return False
		return True
	
	def hasReadAllMailsHints( self ) :
		"""
		����Ƿ��Ѷ�ȡȫ���ʼ�����
		"""
		for mail in self.mails.itervalues() :
			if mail["readedHintTime"] == 0 :				# ����δ���ʼ�
				return False
		return True

	def clearMailbox( self ) :
		"""
		��ɫ�뿪��Ϸʱ����
		"""
		ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_NOTIFY" )
		#ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_HINT_NOTIFY" )  
		self.__clearDelaySendCBID()
		self.mailIndex = -1
		if self.mail_checkTimerID != -1:
			BigWorld.cancelCallback( self.mail_checkTimerID )

	def initMailbox( self ) :
		"""
		����������������ʼ���������Ϸʱ����
		"""
		self.mail_query() 								# �����ʼ�
		self.mail_checkTimerID = BigWorld.callback( csconst.MAIL_CHECK_OUTDATED_REPEAT_TIME, self.mail_checkOutDated )
		
		#��¼ʱ�ʼ�ͼ����ʾ��״̬	
		player = BigWorld.player()
		if not player.hasReadAllMails() :
			if player.hasReadAllMailsHint() :
				ECenter.fireEvent( "EVT_ON_CANCEL_MAIL_HINT_NOTIFY" ) 
	


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __clearDelaySendCBID( self ) :
		"""
		ȡ��������ʱ�����ʼ���Callback ID, ���ٷ���
		"""
		for CBID in self.__delaySendCBID.itervalues() :
			BigWorld.cancelCallback( CBID )
		self.__delaySendCBID = {}

	def mailHasItemConut( self, mailID ):
		"""
		�ʼ����ж��ٸ���Ʒ
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