# -*- coding: gb18030 -*-
#
# $Id: Bank.py,v 1.19 2008-08-09 06:33:34 fangpengjun Exp $

from bwdebug import *
import BigWorld
import items
import csdefine
import csstatus
import csconst
import event.EventCenter as ECenter
from MessageBox import showMessage
from MessageBox import MB_YES_NO
from MessageBox import RS_YES
from config.client.msgboxtexts import Datas as mbmsgs
import ShareTexts
#from Time import Time


g_item = items.instance()

TIME_TO_GET_BANK_ITEMS = 1

class Bank:
	"""
	Ǯׯϵͳ�ӿ�

	bankLockerStatus��ʾǮׯ������״̬�����ݣ���������״̬���Է����ɴ����ݲ�ѯ�ó�������Ҫ��def��������������ݡ��������£�
	bankLockerStatusλ��Ϊ8��ʹ�����ֽ�ģʽ�ұߵĵ�һλ����ʾǮׯ�Ƿ����������״̬����λ�ֽ�ģʽΪ0ʱ��ʾ��������Ϊ1ʱ��ʾ������
	ʹ���ұߵڶ�λ����ʾǮׯ�Ƿ�������״̬���ݣ�������Ϊ0������Ϊ1���ұߵ�������λ�����Ժ���չ��Ҫ��
	ʹ�����ұߵ��塢������λ����ʾǮׯ��������ʧ�ܴ������ݣ������Ա�ʾ7��ʧ�ܣ����ֽ�ģʽΪ111��bankLockerStatus����4λ�������ɵò������ݣ�
	ÿʧ��һ�ο�����λ�����+1��10�������㡣

		Ǯׯ������״̬����bankLockerStatus��״̬���£�����ʵ��ʱ�ɲο�����
		0000 0000:������״̬
		0000 0001:������״̬
		0000 0010:����״̬
		0111 0000:Ǯׯ����ʧ�ܴ���
	"""
	_instance = None
	def __init__( self ):
		"""
		"""
		self.Bank = None				# Ǯׯ��Ʒ����
		self.bankMoney = 0					# Ǯׯ�洢�Ľ�Ǯ
		self._flag = False					# Ǯׯ���ݽ���״̬
		self.entityID = -1
		self.bagIDList = []
		self.__pyMsgBox = None
#		self.bankBags = {}

		self.bankNameDict = {}			# ����λ�������ݣ�keyΪ����index��valueΪ��������
		self._openStyle = None 			#������������ֿ�ķ�ʽ�ı���

	def _setDataFlag( self, flag ):
		"""
		����Ǯׯ���ݽ���״̬

		type flag:	BOOL
		"""
		self._flag = flag


	def _getDataFlag( self ):
		"""
		���Ǯׯ���ݽ���״̬
		"""
		return self._flag


	def enterBank( self, entityID ):
		"""
		Define method.
		�ṩ��cell�򿪿ͻ��˽���Ľӿ�

		���ܣ��򿪽��沢���Ǯׯ���������־�����ݱ�־�����Ƿ����������������
		"""
		self.entityID = entityID
		if not self._getDataFlag():
			self._setDataFlag( True )
			for i in xrange( len( self.bankNameList ) ):
				self.bagIDList.append( i )
			self.bagIDList.reverse()
			self.bank_requestBankBag()
		for i,j in enumerate( self.bankNameList ):
			self.bankNameDict[ i ] = j	# ���������Ϊ�˷���������
			ECenter.fireEvent( "EVT_ON_BAG_NAME_UPDATED", i, self.bankNameDict[i] )
		ECenter.fireEvent( "EVT_ON_SHOW_STORE_WINDOW", entityID )

	def leaveBank( self ):
		"""
		�˳��ֿ�
		"""
		self.base.leaveBank()

	def bank_requestBankBag( self ):
		"""
		����һ���ֿ���Ʒ
		"""
		length = len( self.bagIDList )
		if length > 0:
			self.base.bank_requestBankBag( self.bagIDList.pop() )
			BigWorld.callback( TIME_TO_GET_BANK_ITEMS, self.bank_requestBankBag )

	def bank_receiveBaseData( self, bagID, itemList ): 	# ���²ֿ���������Ʒ
		"""
		Define method.
		�ṩ��base�ĸ�client����Ǯׯ��Ʒ���ݵĽӿ�

		param bankBags:	Ǯׯ�д洢����Ʒ����
		type bankBags:	KITBAGS
		"""
		for item in itemList:
			order = item.order
			bankBagNum = order/csdefine.KB_MAX_SPACE
			ECenter.fireEvent( "EVT_ON_BANK_ADD_ITEM", bankBagNum, order, item ) # ���¸��ֿ����Ʒ

	def hasEnoughItems( self, amount ):
		items = self.findItemsByIDFromNKCK( csdefine.ID_OF_ITEM_OPEN_BAG )
		count = 0
		for item in items:
			count += item.amount
		if count < amount:return False
		return True

	def requestOpenNextBag( self, isUseItemOpen):

		#@param isUseItemOpen�� ��ͨ���ֿ���滹��ֱ�ӵ����˿����ֿ� 0���ֿ���� 1�������˿ľ
		# ����������Ϊ�߻�Ҫ���ڲ�ͬ�ķ�ʽ����ʾҲ��һ��
		#@type boolean
		nextIndex = len( self.bankNameList )
		if nextIndex >= csconst.BANK_MAX_COUNT:
			self.statusMessage( csstatus.BANK_CANNOT_OPEN_MORE_BAG )
			return
		self._openStyle  = isUseItemOpen
		if self.hasEnoughItems( csconst.NEED_ITEM_COUNT_DICT[nextIndex] ):
			self.cell.bank_activateBag()
		else:
			self.noticeFailure()

	def getNextBagIndex( self):
		return len( self.bankNameList )

	def noticeFailure( self ):
		"""
		Exposed method.
		�ṩ��baseʧ����Ϣ,��ΪĳЩԭ����noticeSuccess���ܺϲ�
		"""
		dialogID = csstatus.BANK_ITEM_NOT_ENOUGH_1
		if self._openStyle:
			dialogID = csstatus.BANK_ITEM_NOT_ENOUGH_2
		self.statusMessage( dialogID )
		self._openStyle = None		# �ͷű��

	def noticeSuccess( self ):
		if self._openStyle:
			self.statusMessage( csstatus.BANK_KITBAG_OPEN_SUCCESS_2, len( self.bankNameList ) )
		else :
			self.statusMessage( csstatus.BANK_KITBAG_OPEN_SUCCESS_1 )

	def bank_activateBagSuccess( self ):
		"""
		Define method.
		����Ǯׯ������ɹ�
		"""
#		self.statusMessage( csstatus.BANK_ACTIVATE_SUCCESS )
		#bag = g_item.createDynamicItem( "070101005" )
		index = len( self.bankNameList )
		#self.bankBags[ index ] = bag
		self.bankNameList.append( "" )
		self.bankNameDict[ index ] = ""
		self.noticeSuccess( )
		self._openStyle = None
		ECenter.fireEvent( "EVT_ON_ACTIVATE_BANK_SUCCESS", index )

	def bank_bagNameUpdate( self, index, name ):
		"""
		Define method.
		���������º���
		"""
		DEBUG_MSG( "---->>>%i, %s" % ( index, name ) )
		#if self.bankNameDict.has_key( index ):
		#	DEBUG_MSG( "����" )		# ����
		#else:
		#	DEBUG_MSG( "�¼Ӱ���" )	# �¼��˰���
#		self.bankNameList.append( name )
		self.bankNameList[index] = name
		self.bankNameDict[ index ] = name
		ECenter.fireEvent( "EVT_ON_BAG_NAME_UPDATED", index, name )

	#------------------------------------��Ǯׯ�����Ʒ BEGIN------------------------------
	def bank_storeItem2Order( self, kitbagNum, srcOrder, bankBagNum, dstOrder ):
		"""
		��Ǯׯ��洢��Ʒ�Ľӿڣ���֪Ŀ����Ʒ��

		param kitbagNum:��������λ��
		type kitbagNum:	UINT8
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param bankBagNum:Ǯׯ����λ��
		type bankBagNum:	UINT8
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		"""
		srcOrder = kitbagNum * csdefine.KB_MAX_SPACE + srcOrder
		#dstOrder = bankBagNum * csdefine.KB_MAX_SPACE + dstOrder
		item = self.getItem_( srcOrder )
		if item is None:
			ERROR_MSG( "------>>>can not find item.order:%i." % srcOrder )
			return
		if not item.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return
		self.cell.bank_storeItem2Order( srcOrder, dstOrder, self.entityID )

	def bank_storeItem2Bank( self, kitbagNum, srcOrder ):
		"""
		��Ǯׯ��洢��Ʒ�Ľӿڣ���ָ������λ��Ŀ����ӣ���Ǯׯ����ҵ�һ����λ

		param kitbagNum:��������λ��
		type kitbagNum:	UINT8
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param bankBagNum:Ǯׯ����λ��
		type bankBagNum:	UINT8
		"""
		srcOrder = kitbagNum * csdefine.KB_MAX_SPACE + srcOrder
		item = self.getItem_( srcOrder )
		if item is None:
			ERROR_MSG( "------>>>can not find item.order:%i." % srcOrder )
			return
		if not item.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return
		self.cell.bank_storeItem2Bank( srcOrder, self.entityID )

	def bank_storeItem2Bag( self, kitbagNum, srcOrder, bankBagNum ):
		"""
		��Ǯׯ��洢��Ʒ�Ľӿڣ���ָ���˰���λ

		param kitbagNum:��������λ��
		type kitbagNum:	UINT8
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param bankBagNum:Ǯׯ����λ��
		type bankBagNum:	UINT8
		"""
		srcOrder = kitbagNum * csdefine.KB_MAX_SPACE + srcOrder
		item = self.getItem_( srcOrder )
		if item is None:
			ERROR_MSG( "------>>>can not find item.order:%i." % srcOrder )
			return
		if not item.canStore():
			self.statusMessage( csstatus.BANK_KITBAG_ITEM_UNSTOREABLE )
			return
		self.cell.bank_storeItem2Bag( srcOrder, bankBagNum, self.entityID )

	# ------------------------��Ǯׯ�����Ʒ END------------------------------------------------------------

	#------------------------------------��Ʒ��Ǯׯȡ�� BEGIN-----------------------------
	def bank_fetchItem2Order( self, srcOrder, kitbagNum, dstOrder ):
		"""
		�����Ǯׯ��Ʒ����Ʒ��ȷ���ı�����Ʒ��

		param bankBagNum:Ǯׯ����λ��
		type bankBagNum:	UINT8
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param kitbagNum:��������λ��
		type kitbagNum:	UINT8
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		"""
		#srcOrder = bankBagNum * csdefine.KB_MAX_SPACE + srcOrder
		dstOrder = kitbagNum * csdefine.KB_MAX_SPACE + dstOrder
		self.cell.bank_fetchItem2Order( srcOrder, dstOrder, self.entityID )


	def moveItemCB( self, bankBagNum, srcOrder, dstBagNum, dstOrder ):
		"""
		Define method.
		�����������ߵ�λ�á�
		"""
		ECenter.fireEvent( "EVT_ON_BANK_SWAP_ITEMS", bankBagNum, srcOrder, dstBagNum, dstOrder )




	def bank_fetchItem2Kitbags( self, bankBagNum, srcOrder ):
		"""
		��Ǯׯ��ȡ����Ʒ�Ľӿڣ���ָ������λ��Ŀ����ӣ��ڱ�������ҵ�һ����λ

		param bankBagNum:Ǯׯ����λ��
		type bankBagNum:UINT8
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		"""
		self.cell.bank_fetchItem2Kitbags( srcOrder, self.entityID )
	#------------------------------------��Ʒ��Ǯׯȡ�� END------------------------------

	def bank_destroyItem( self, bankBagNum, order ):
		"""
		������Ʒ�Ŀͻ��˽ӿ�

		param kitbagNum:Ǯׯ����λ��
		type kitbagNum:UINT8
		param order:	���Ӻ�
		type order:	INT16
		"""
		#order = bankBagNum * csdefine.KB_MAX_SPACE + order
		self.cell.bank_destroyItem( order, self.entityID )

	def bank_moveItem( self, srcBankBagNum, srcOrder, dstBankBagNum, dstOrder ):
		"""
		��ͬһ���������ƶ���Ʒ�Ľӿ�

		param bankBagNum:Ǯׯ����λ��
		type bankBagNum:UINT8
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param srcOrder:	���Ӻ�
		type srcOrder:	INT16
		"""
		#srcOrder = srcBankBagNum * csdefine.KB_MAX_SPACE + srcOrder
		#dstOrder = dstBankBagNum * csdefine.KB_MAX_SPACE + dstOrder
		self.cell.bank_moveItem( srcOrder, dstOrder, self.entityID )

	def bank_storeMoney( self, money ):
		"""
		�����Ǯׯ�洢��Ǯ�Ľӿ�

		param money�����Ҫ��Ǯׯ��Ľ�Ǯ��Ŀ
		type money��UINT32
		"""
		if self.bankMoney >= csconst.BANK_MONEY_LIMIT:		 #���Ǯׯ�Ľ�Ǯ�����ѵ����� ��ô����
			self.statusMessage( csstatus.BANK_MONEY_LIMIT )
			return
		elif self.bankMoney + money >= csconst.BANK_MONEY_LIMIT: #���Ǯׯ�Ľ�Ǯ����Ҫ���Ǯ�������� ��ô������Ϣ
			self.statusMessage( csstatus.BANK_MONEY_LIMIT )
			return
		if self.money < money :
			self.statusMessage( csstatus.BANK_MONEY_NOT_ENOUGH_TO_STORE )
			return
		self.cell.bank_storeMoney( money, self.entityID )

	def bank_fetchMoney( self, money ):
		"""
		��Ҵ�Ǯׯȡ����Ǯ�Ľӿ�

		param money�����Ҫȡ���Ľ�Ǯ��Ŀ
		type money��UINT32
		"""

		if self.testAddMoney( money ) > 0:	#������Я���Ľ�Ǯ��������ȡ����Ǯ�ѵ�����
			self.statusMessage( csstatus.CIB_MSG_MONEY_OVERFLOW )
			if self.ifMoneyMax():	#���������ϵĽ�Ǯ�Ѿ����������� ����
				return

		self.cell.bank_fetchMoney( money, self.entityID )


	def set_bankMoney( self, oldValue ):
		"""
		��Ǯׯ��Ǯ���Ըı�ʱ������
		"""
#		pass	# ����GUIFacade.onRoleMoneyChanged( oldValue, self.money )
		ECenter.fireEvent( "EVT_ON_ROLE_BANK_MONEY_CHANGED", oldValue, self.bankMoney )

	def bank_splitItemUpdate( self, bankBagNum, order, amount ):
		"""
		Define method.
		���һ��Ǯׯ��Ʒ�ĸ��º���,����Դ������Ʒ����Ŀ

		param bankBagNum:Ǯׯ����λ��
		type bankBagNum:UINT8
		param order:	���Ӻ�
		type order:		INT16
		param amount:	��Ʒ��Ŀ
		type amount:	INT16
		"""
		#self.bankBags[bankBagNum][order].setAmount( amount )
		ECenter.fireEvent( "EVT_ON_BANK_SPLIT_ITEMS", bankBagNum, order, amount )


	def bank_storeItemUpdate( self, item ):
		"""
		Define method.
		������Ǯׯ�洢һ����Ʒ�ĸ��º���

		param bankBagNum:Ǯׯ����λ��bank_storeMoney
		type bankBagNum:UINT8
		param order:	���Ӻ�
		type order:		INT16
		param item:	��Ʒʵ��
		type item:	ITEM
		"""
		# ������Ʒ��Ϣ
		order = item.order
		bankBagNum = order/csdefine.KB_MAX_SPACE
		ECenter.fireEvent( "EVT_ON_BANK_ADD_ITEM", bankBagNum, order, item )		# ֪ͨ����

	def bank_delItemUpdate( self, bankBagNum, order ): # ɾ��ԭ���ֿ��еİ�����Ʒ
		"""
		Define method.
		ɾ��һ��Ǯׯ��Ʒ�ĸ��º���
		��base����

		param bankBagNum:	���ݸı�İ�����
		type bankBagNum:	UINT8
		param order:	���Ӻ�
		type order:		INT16
		"""
		#order = order % csdefine.KB_MAX_SPACE
		ECenter.fireEvent( "EVT_ON_BANK_UPDATE_ITEM", bankBagNum, order, None )# ɾ���ض��ֿ��ڵ�ĳһ��Ʒ

	# ------------------------------------------Ǯׯ���������� BEGIN----------------------------------------
		# ------------------call by UI----------------------------------
	def bank_setPassword( self, srcPassword, password ):
		"""
		���á��޸�Ǯׯ���붼ʹ�ô˽ӿڡ�Ǯׯ����Ϊ��ʱ��srcPasswordֵΪ"",�޸�����ʱsrcPasswordֵΪ ��ҵľ�����

		param srcPassword:		Ǯׯԭ����,
		type srcsrcPassword:	STRING
		param password:	������������
		type password:	STRING
		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		self.cell.bank_setPassword( srcPassword, password, self.entityID )

	def bank_lock( self ):
		"""
		��Ǯׯ����������������������һ�û�ж�Ǯׯ������ǰ���£�������˽ӿڵ�ʹ������

		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		self.cell.bank_lock( self.entityID )

	def bank_unlock( self, srcPassword ):
		"""
		��Ǯׯ�����������������Ǯׯ�����Ҹ�Ǯׯ������ǰ���£�������˽ӿڵ�ʹ��������
		ע�⣺�����Ĳ�������ڱ��ε�½�ڼ�ʧ��3�Σ�24Сʱ�ڲ�����Ǯׯ����������

		param srcPassword:		Ǯׯԭ����,
		type srcsrcPassword:	STRING
		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		self.cell.bank_unlock( srcPassword, self.entityID )

	def bank_clearPassword( self, srcPassword ):
		"""
		��Ǯׯ���ý���������Ѿ���Ǯׯ�����������ǰ���£��˽ӿ����������õ����룬��Ǯׯ������Ϊ�ա�
		ע�⣺���ý����Ĳ�������ڱ��ε�½�ڼ�ʧ��3�Σ�24Сʱ�ڲ�����Ǯׯ����������

		param srcPassword:		Ǯׯԭ����,
		type srcsrcPassword:	STRING
		param entityID:	Ǯׯnpc��id
		type entityID:	OBJECT_ID
		"""
		self.cell.bank_clearPassword( srcPassword, self.entityID )

	# -----------------------notify UI-------------------------------------------------
	def _isBankLocked( self ):
		"""
		��֤Ǯׯ�Ƿ�����
		"""
		return ( self.bankLockerStatus >> 1 ) & 0x01 == 1	# ��ʾǮׯ�Ƿ��������״̬λ�Ƿ�Ϊ1

	def set_bankLockerStatus( self, oldValue ):
		"""
		Ǯׯ������״̬���º������Զ����º�����bankLockerStatus���ݽ���������Ǯׯ��������״̬����Ҫ���ݴ�����֪ͨ��ҽ����������ɹ�
		"""
		ECenter.fireEvent( "EVT_ON_BANKLOCK_STATUAS_CHANGE", self.bankLockerStatus )
		# ֪ͨ���棬wsf

	def set_bankUnlockLimitTime( self, oldValue ):
		"""
		Ǯׯ��������ʱ����Զ�֪ͨ����
		"""
		if self.bankUnlockLimitTime > 0:
			# ֪ͨ���棬��Ϊ���bankUnlockLimitTime > 0��˵��bankUnlockLimitTime�ǵ�һ�����ã���Ҫ֪ͨ���������Ϊ�����ˣ�wsf
			ECenter.fireEvent( "EVT_ON_BANKLOCK_TIME_CHANGE", self.bankUnlockLimitTime )

	def bank_lockerNotify( self, flag, remainTime ):
		"""
		Define method.
		Ǯׯ������֪ͨ����

		if flag == 0: ����Ǯׯ����ɹ���֪ͨ
		if flag == 1: Ǯׯ���������ĳɹ���֪ͨ
		if flag == 2: ����������֪ͨ
		if flag == 3: ���������֪ͨ
		if flag == 4: ��Ǯׯ�����ɹ���֪ͨ
		if flag == 5: ��Ǯׯ�����ɹ���֪ͨ
		if flag == 6: �Ѿ������������
		if flag == 7: �ɹ����ý���

		type flag:	UINT8
		"""
		ECenter.fireEvent( "EVT_ON_BANKLOCK_FLAG_CHANGE", flag, remainTime )

	def bank_onConfirmForceUnlock( self ) :
		"""
		Define method.
		ǿ�ƽ�������ȷ��
		"""
		def confirmUnlock( result ) :
			if result == RS_YES :
				self.cell.bank_onForceUnlock()
		# ǿ�ƽ���������Ҫ%s�����������뽫����գ���ȷ��Ҫ������
		needTime = csconst.BANK_FORCE_UNLOCK_LIMIT_TIME
		needHours = needTime / 3600
		needMinutes = needTime % 3600 / 60
		needSeconds = needTime % 60
		needTimeText = ""
		if needHours :
			needTimeText += "%d%s" % ( needHours, ShareTexts.CHTIME_HOUR )
		if needMinutes :
			needTimeText += "%d%s" % ( needMinutes, ShareTexts.CHTIME_MINUTE )
		if needSeconds :
			needTimeText += "%d%s" % ( needSeconds, ShareTexts.CHTIME_SECOND )
		msg = mbmsgs[0x0e81] % needTimeText
		if self.__pyMsgBox is not None:
			self.__pyMsgBox.visible = False
			self.__pyMsgBox = None
		self.__pyMsgBox = showMessage( msg, "", MB_YES_NO, confirmUnlock )

	# ------------------------------------------Ǯׯ���������� END----------------------------------------

	#--------------------���¹������ڽ���ı仯�Ѿ�����-----------------------
	def bank_moveItem2Bag( self, srcBankBagNum, srcOrder, dstBankBagNum ):
		"""
		��Ǯׯ�� ����϶���Ʒ������λ�����еĽӿ�

		param srcBankBagNum:Ǯׯ����λ��
		type srcBankBagNum:UINT8
		param dstOrder:	���Ӻ�
		type dstOrder:	INT16
		param dstBankBagNum:Ǯׯ����λ��
		type dstBankBagNum:UINT8
		"""
		#srcOrder = srcBankBagNum * csdefine.KB_MAX_SPACE + srcOrder
		self.cell.bank_moveItem2Bag( srcOrder, dstBankBagNum, self.entityID )

	# -------------------------���ð��� BEGIN----------------------------------
	def bank_bankLayBank( self, srcBankBagNum, srcOrder, dstBankBagNum ):
		"""
		����ҵ�ǰǮׯ��Ʒ����Ǯׯ����λ���ð����Ľӿ�

		param srcBankBagNum:���Ǯׯ��ǰ������
		type srcBankBagNum:	UINT8
		param srcOrder:		���Ǯׯ��ǰ�����ĸ��Ӻ�
		type srcOrder:		INT16
		param dstBankBagNum:���Ǯׯ�İ���λ
		type dstBankBagNum:	UNIT8
		"""
		pass
		#elf.cell.bank_bankLayBank( srcBankBagNum, srcOrder, dstBankBagNum, self.entityID )


	def bank_kitbagsLayBank( self, kitbagNum, srcOrder, bankBagNum ):
		"""
		����ҵ�ǰ��������Ǯׯ����λ���ð����Ľӿ�
		param kitbagNum:	��ұ�����ǰ������
		type kitbagNum:		UINT8
		param srcOrder:		��ұ�����ǰ�����ĸ��Ӻ�
		type srcOrder:		INT16
		param bankBagNum:	���Ǯׯ�İ���λ
		type bankBagNum:	UNIT8
		"""
		pass
		#srcOrder = kitbagNum * csdefine.KB_MAX_SPACE + srcOrder
		#self.cell.bank_kitbagsLayBank( kitbagNum, srcOrder, bankBagNum, self.entityID )

	# -------------------------���ð��� END----------------------------------
	def bank_changeGoldToItem( self, goldValue ):
		"""
		�һ�Ԫ��Ʊ
		"""
		if self.gold < goldValue:
			self.statusMessage( csstatus.GOLD_NO_ENOUGH )
			return
		if self.getNormalKitbagFreeOrder() == -1:
			self.statusMessage( csstatus.KITBAG_IS_FULL )
			return
		if goldValue < 0 and goldValue > 20000:
			self.statusMessage( csstatus.GOLD_TICKET_MAX_CHANGE )
			return
		self.base.bank_changeGoldToItem( goldValue )

	def openGoldToItemInterface( self ):
		"""
		define method
		֪ͨ��Ԫ��Ʊ����
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_OPEN_GOLD_CHANGE" )


	#------------------------------------------------------------------------
#
# $Log: not supported by cvs2svn $
# Revision 1.18  2008/08/08 07:19:41  fangpengjun
# no message
#
# Revision 1.17  2008/08/08 03:14:06  fangpengjun
# ���������µ����˲ֿ�ϵͳ
#
# Revision 1.16  2008/07/07 11:06:29  wangshufeng
# Ǯׯ�������������ʹ������Ʒ��Ǯׯ�е�ȫ��order����������ģ�����ݡ�
# method modify:onBankBagsInfoReceive,������Ǯׯ�������ݸ��²���ȷ��bug��
#
# Revision 1.15  2008/05/30 03:04:21  yangkai
# װ������������Ĳ����޸�
#
# Revision 1.14  2008/05/13 06:05:38  wangshufeng
# method modify:bank_splitItem,ȥ��Ŀ�������Ŀ����Ӳ��������ұ�����һ����λ���ò�ֺ����Ʒ��
#
# Revision 1.13  2008/05/04 06:43:32  zhangyuxing
# no message
#
# Revision 1.12  2008/04/01 05:17:55  zhangyuxing
# ����Ͳֿ�Ի�״̬
#
# Revision 1.11  2008/03/28 01:13:05  zhangyuxing
# �޸� ��� cell.bank_requireData �ķ�ʽ
#
# Revision 1.10  2008/02/04 00:57:15  zhangyuxing
# �޸Ĳֿ���Ʒ��÷�ʽ
#
# Revision 1.9  2008/01/22 03:58:51  wangshufeng
# �����������self.kitbagsLockerStatus ����self.bankLockerStatus��
#
# Revision 1.8  2008/01/15 01:47:44  kebiao
# onUpdateSkill to onUpdateNormalSkill
#
# Revision 1.7  2007/12/24 01:10:14  fangpengjun
# no message
#
# Revision 1.6  2007/12/22 10:00:26  fangpengjun
# ��ӷ��͸��ͻ�����Ϣ���¼�
#
# Revision 1.4  2007/12/06 06:56:39  huangyongwei
# �� updateSkill ��Ϊ onUpdateSkill
#
# Revision 1.3  2007/12/05 06:45:06  wangshufeng
# no message
#
# Revision 1.2  2007/11/26 02:14:20  wangshufeng
# interface modify:ȥ��bank_receiveCellData�ӿڵĶ������bankMoney
#
# ������Ǯׯ����������
#
# Revision 1.1  2007/11/14 02:54:38  wangshufeng
# �����Ǯׯϵͳ
#
#
#