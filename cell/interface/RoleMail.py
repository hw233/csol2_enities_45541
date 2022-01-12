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

g_items = items.instance()	# �ڴ���һ����Ʒʱ��Ҫ

class RoleMail:
	"""
	�ʼ�ϵͳ���cell�˽ӿ�
	"""

	def __init__(self):
		"""
		"""
		pass


	def mail_send(self, receiverName, mailType, title, content, money, uids, hasItem, receiverBase, npcId):
		"""
		define method.
		��Ҽ��ţ��˽ӿ���base���ã�Ҳ����˵�����ʼ��Ĺ�����client -> base -> cell -> mailmanager,
		ʹ�ô����̶���ʹ��client -> cell -> mailmanager����Ϊ�����ʼ�ʱ��Ҫȷ���������Ǵ��ڵġ�

		���̣�
		�����ж��ܷ�������NPC���������������Ƿ�����Ҫ���Ƿ�Я����Ʒ�����ʷѴ�������ǰ��ʼ����͵��ʼ���������

		������
		@param receiverName: ����������
		@type  receiverName: string
		@param     mailType: �ʼ�����
		@type      mailType: int8
		@param        title: �ʼ��ı���
		@type         title: string
		@param      content: �ʼ�������
		@type       content: string
		@param        money: �ʼ������Ľ�Ǯ
		@type         money: unit32
		@param         uids: �ʼ���������Ʒ��ΨһID
		@type          uids: int64
		@param      hasItem: ��ʾ�Ƿ�Я������Ʒ����
		@type       hasItem: int8
		@param receiverBase: �����˵�base mailBox
		@type  receiverBase: mailbox
		@param        npcID: �����õ�������id
		@type         npcID: object_id
		"""

		npc = BigWorld.entities.get( npcId ) #�Ƿ��ܻ�ø�npc
		if npc == None:
			ERROR_MSG( "%s: is not find the MailBox!(mail)" % (self.getName()))
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE: #npc�����ж�
			ERROR_MSG( "%s: is too far from the MailBox!(mail)" % (self.getName()))
			return

		itemDatas = []

		if hasItem or money > 0:
			if self.iskitbagsLocked(): # ����������������򷵻�
				self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
				return
			#�鿴�Ƿ�������Ʒ
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
				del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
				# phw 2009-09-30: �����ԣ���172.16.0.8��as 5.3���ϣ�����ֱ��dumps���������ݲ���ȷ��
				# �ᵼ��һ����Ʒ���硰10101001�������ʼ�ʧ�ܣ����ڿ���̨��ֱ��dumpsȴ����ȷ�ģ�
				# Ϊ�˱�֤���������ԣ���ʱʹ�����Ч�ʵ��ȫ������dumps��ʽ��
				itemData = cPickle.dumps( tempDict, 0 )	# old: itemData = cPickle.dumps( tempDict, 2 )
				itemDatas.append( itemData )

		# ��������
		# ���������:���� 2009-5-27,�ж�ƽ�ʻ��ǿ��,��ͬ�ʵݷ�ʽ�շѱ�׼��ͬ,mailCost�������ʼ����͵��շѱ���
		if mailType == csdefine.MAIL_TYPE_QUICK:	# ����շ�����ͨ�ʼ����ʷѵ�2��
			mailCost = 2
		elif mailType == csdefine.MAIL_TYPE_NORMAL:	# ��ͨ�ż�
			mailCost = 1
		else:
			return

		value = money + ( money * csconst.MAIL_SEND_MONEY_RATE + csconst.MAIL_FARE ) * mailCost
		if len(itemDatas) != 0:
			value += csconst.MAIL_SEND_ITEM_FARE * len( itemDatas ) * mailCost

		# ������
		if self.payMoney( value, csdefine.CHANGE_MONEY_MAIL_SEND ) == False:
			ERROR_MSG( "%s: not have enough money to mail!(mail)" % (self.getName()))
			return

		if len(itemDatas) != 0:
			for uid in uids:
				item = self.getItemByUid_( uid )
				if item.isAlreadyWield() : # �����Ҫɾ������Ʒ�Ǵ������ϵ�װ��������ж����
					item.unWield( self )
					self.resetEquipModel( item.order, None )
				self.removeItemByUid_( uid, reason = csdefine.DELETE_ITEM_MAIL_SEND )	# ȡ���ʼĵ���Ʒ�б�

		BigWorld.globalData["MailMgr"].sendWithMailbox(self.base, receiverBase, receiverName, mailType, csdefine.MAIL_SENDER_TYPE_PLAYER, self.getName(), title, content, money, itemDatas)
		
		self.client.onMail_send_successed()
		
	def mail_send_on_air( self, receiverName, mailType, title, content ):
		"""
		define method
		���ڽ�ɫ��ĳЩ����(����onLevelUp)��Ҫ���Զ������ʼ��õĽӿ� by����
		@param receiverName: ����������
		@type  receiverName: string
		@param     mailType: �ʼ�����
		@type      mailType: int8
		@param        title: �ʼ��ı���
		@type         title: string
		@param      content: �ʼ�������
		@type       content: string
		"""
		BigWorld.globalData["MailMgr"].send( None, receiverName, mailType, csdefine.MAIL_SENDER_TYPE_NPC, self.getName(), title, content, 0, [] )
		
	def mail_send_on_air_withItems( self, receiverName, mailType, title, content, items ):
		"""
		���ڽ�ɫ��ĳЩ����(����onLevelUp)��Ҫ���Զ������ʼ��õĽӿ� by����
		@param receiverName: ����������
		@type  receiverName: string
		@param     mailType: �ʼ�����
		@type      mailType: int8
		@param        title: �ʼ��ı���
		@type         title: string
		@param      content: �ʼ�������
		@type       content: string
		@param items: ��Ʒ
		@type     itemslist: list
		"""
		itemDatas = []
		#�鿴�Ƿ�������Ʒ
		for item in items:
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
			# phw 2009-09-30: �����ԣ���172.16.0.8��as 5.3���ϣ�����ֱ��dumps���������ݲ���ȷ��
			# �ᵼ��һ����Ʒ���硰10101001�������ʼ�ʧ�ܣ����ڿ���̨��ֱ��dumpsȴ����ȷ�ģ�
			# Ϊ�˱�֤���������ԣ���ʱʹ�����Ч�ʵ��ȫ������dumps��ʽ��
			itemData = cPickle.dumps( tempDict, 0 )	# old: itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )
		BigWorld.globalData["MailMgr"].send( None, receiverName, mailType, csdefine.MAIL_SENDER_TYPE_NPC, self.getName(), title, content, 0, itemDatas )

	def mail_getItem( self,scrEntityID, mailID, npcId, index ):
		"""
		exposed method
		�����ȡ�ʼ�������Ʒ

		���̣��ж���Һ�����ľ���󣬻�Ҫ�����ұ����Ƿ��пռ䣬���žͿ��԰�������ȡ�ʼ���Ʒ�������͸���ҵ�base��

		����
		@param scrEntityID: �������͵ĵ��ô˽ӿڵ�ʵ��ID
		@type  scrEntityID: object_id
		@param      mailID: �ʼ���DBID
		@type       mailID: DATABASE_ID
		@param       npcId: �����õ�������id
		@type        npcId: object_id


		"""
		if scrEntityID != self.id:
			ERROR_MSG( "%s: cell is call by %i! (mail)" % (self.getName(), scrEntityID))
			return

		npc = BigWorld.entities.get( npcId ) #�Ƿ��ܻ�ø�npc
		if npc == None:
			ERROR_MSG( "%s: is not find the MailBox!(mail)" % (self.getName()))
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE: #npc�����ж�
			ERROR_MSG( "%s: is too far from the MailBox!(mail)" % (self.getName()))
			return
			
		if self.iskitbagsLocked():	# ����������by����
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		self.base.mail_getItem( mailID, index )

	def mail_getAllItem( self,scrEntityID, mailID, npcId ):
		"""
		exposed method
		�����ȡ�ʼ�ȫ����Ʒ

		���̣��ж���Һ�����ľ���󣬻�Ҫ�����ұ����Ƿ��пռ䣬���žͿ��԰�������ȡ�ʼ���Ʒ�������͸���ҵ�base��

		����
		@param scrEntityID: �������͵ĵ��ô˽ӿڵ�ʵ��ID
		@type  scrEntityID: object_id
		@param      mailID: �ʼ���DBID
		@type       mailID: DATABASE_ID
		@param       npcId: �����õ�������id
		@type        npcId: object_id


		"""
		if scrEntityID != self.id:
			ERROR_MSG( "%s: cell is call by %i! (mail)" % (self.getName(), scrEntityID))
			return

		npc = BigWorld.entities.get( npcId ) #�Ƿ��ܻ�ø�npc
		if npc == None:
			ERROR_MSG( "%s: is not find the MailBox!(mail)" % (self.getName()))
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE: #npc�����ж�
			ERROR_MSG( "%s: is too far from the MailBox!(mail)" % (self.getName()))
			return
			
		if self.iskitbagsLocked():	# ����������by����
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		self.base.mail_getAllItem( mailID )

	def mail_receiveItem( self, mailID, itemData, index ):
		"""
		define method
		��ȡ�ʼ�������Ʒ


		���̣��ʼ���Ʒ�����������base���͹����ġ����������������ʽ��ô������һ���Ҫ����ʽ��ú󣬵�base�����ݿ�ֱ��¼��

		@param   mailID: �ʼ���DBID
		@type    mailID: DATABASE_ID
		@param itemData: ��Ʒ������
		@type  itemData: string
		"""
		if self.iskitbagsLocked():	# ����������by����
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
		��ȡ�ʼ�������Ʒ


		���̣��ʼ���Ʒ�����������base���͹����ġ����������������ʽ��ô������һ���Ҫ����ʽ��ú󣬵�base�����ݿ�ֱ��¼��

		@param   mailID: �ʼ���DBID
		@type    mailID: DATABASE_ID
		@param itemDatas: ��Ʒ������
		@type  itemDatas: list of string
		"""
		
		if self.iskitbagsLocked():	# ����������by����
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
		�����ȡ�ʼ�������Ǯ

		���̣��ж���Һ�����ľ���󣬽��žͿ��԰�������ȡ�ʼ���Ǯ�������͸���ҵ�base��

		����
		@param scrEntityID: �������͵ĵ��ô˽ӿڵ�ʵ��ID
		@type  scrEntityID: object_id
		@param      mailID: �ʼ���DBID
		@type       mailID: DATABASE_ID
		@param       npcId: �����õ�������id
		@type        npcId: object_id
		"""
		if scrEntityID != self.id:
			ERROR_MSG( "%s: cell is call by %i! (mail)" % (self.getName(), scrEntityID))
			return

		npc = BigWorld.entities.get( npcId ) #�Ƿ��ܻ�ø�npc
		if npc == None:
			ERROR_MSG( "%s: is not find the MailBox!(mail)" % (self.getName()))
			return

		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE: #npc�����ж�
			ERROR_MSG( "%s: is too far from the MailBox!(mail)" % (self.getName()))
			return
			
		if self.iskitbagsLocked():	# ����������by����
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED, "" )
			return

		self.base.mail_getMoney(mailID)


	def mail_receiveMoney(self, mailID, money):
		"""
		define method
		��ȡ�ʼ�������Ǯ


		���̣��ʼ���Ǯ�����������base���͹����ġ����������������ʽ��ô������һ���Ҫ����ʽ��ú󣬵�base�����ݿ�ֱ��¼��

		@param mailID: �ʼ���DBID
		@type  mailID: DATABASE_ID
		@param  money: ��Ǯ������
		@type   money: string

		"""
		#��Ǯ�Ƿ񳬹�����޶�
		if self.gainMoney( money, csdefine.CHANGE_MONEY_MAIL_RECEIVEMONEY ) == False:
			self.base.mail_getMoneyRegister(mailID, 0)
			self.client.onStatusMessage( csstatus.CIB_MONEY_OVERFLOW, "" )
			return
		self.base.mail_getMoneyRegister(mailID, 1)

# RoleMail.py
