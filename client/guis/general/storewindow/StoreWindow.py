# -*- coding: gb18030 -*-
#
# $Id: StoreWindow.py,v 1.35 2008-08-26 02:19:45 huangyongwei Exp $

# rewrited by ganjinxing 2009-12-14


from guis import *
from bwdebug import *
from guis.common.TrapWindow import UnfixedTrapWindow
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.tooluis.passwordbox.PasswordWindow import PasswordWindow
from guis.tooluis.inputbox.InputBox import AmountInputBox
from guis.tooluis.inputbox.MoneyInputBox import MoneyInputBox
from config.client.msgboxtexts import Datas as mbmsgs
from ItemsPanel import ItemsPanel
from gbref import rds
import csconst
import csdefine
import csstatus
import GUIFacade
from LabelGather import labelGather

class StoreWindow( UnfixedTrapWindow ) :

	def __init__( self ) :
		wnd = GUI.load( "guis/general/storewindow/storewindow.gui" )
		uiFixer.firstLoadFix( wnd )
		UnfixedTrapWindow.__init__( self, wnd )

		self.__initialize( wnd )

		self.__triggers = {}
		self.__registerTriggers()
		self.__isChangeGold = False #�Ƿ�����ڻ�Ԫ��Ʊ

		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TRADE1 )				# ��ӵ�MutexGroup.TRADE1������

	def __initialize( self, wnd ) :
		self.__pyItemsPanel = ItemsPanel( wnd.tc )

		self.__pySaveBtn = self.__createDefButton( wnd.saveBtn, self.__saveMoney )
		self.__pyCodeLock = self.__createDefButton( wnd.lockBtn, self.__onPasswordLock )
		self.__pyExtendBtn = self.__createDefButton( wnd.extendBtn, self.__extendPackage )
		self.__pyExtractBtn = self.__createDefButton( wnd.extractBtn, self.__takeMoney )

		self.__pyStGold = StaticText( wnd.moneyPanel.lbGold )
		self.__pyStGold.text = ""
		self.__pyStSilver = StaticText( wnd.moneyPanel.lbSilver )
		self.__pyStSilver.text = ""
		self.__pyStCopper = StaticText( wnd.moneyPanel.lbCopper )
		self.__pyStCopper.text = ""

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pySaveBtn, "StoreWndRole:main", "saveBtn" )
		labelGather.setPyBgLabel( self.__pyCodeLock, "StoreWndRole:main", "lockBtn" )
		labelGather.setPyBgLabel( self.__pyExtendBtn, "StoreWndRole:main", "extendBtn" )
		labelGather.setPyBgLabel( self.__pyExtractBtn, "StoreWndRole:main", "extractBtn" )
		labelGather.setLabel( wnd.st_moneyText, "StoreWndRole:main", "st_moneyText" )
		labelGather.setLabel( wnd.lbTitle, "StoreWndRole:main", "lbTitle" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __createDefButton( self, btn, handler ) :
		pyBtn = HButtonEx( btn )
		pyBtn.setExStatesMapping( UIState.MODE_R4C1)
		pyBtn.onLClick.bind( handler )
		return pyBtn

	def __registerTriggers( self ) :
		"""
		register all events
		"""
		self.__triggers["EVT_ON_SHOW_STORE_WINDOW"]	 = self.__beginTrade
		self.__triggers["EVT_ON_HIDE_STORE_WINDOW"]	 = self.__endTrade
		#�ֿ�
		self.__triggers["EVT_ON_BANK_ADD_ITEM"] = self.__onAddBagItem				# �����Ʒ
		self.__triggers["EVT_ON_BANK_SWAP_ITEMS"] = self.__onSwapItems				# �����ֿ�����Ʒ
		self.__triggers["EVT_ON_BANK_UPDATE_ITEM"] = self.__onUpdateItem			# ���²ֿ�����Ʒ
		self.__triggers["EVT_ON_BAG_NAME_UPDATED"] = self.__onUpdateBagName	 		# �ı��������
		self.__triggers["EVT_ON_ROLE_OPEN_GOLD_CHANGE"] = self.__onOpenChange 		# ��Ԫ���һ�����
		self.__triggers["EVT_ON_ACTIVATE_BANK_SUCCESS"] = self.__onActivateBag		# ��������ɹ�
		self.__triggers["EVT_ON_ROLE_BANK_MONEY_CHANGED"] = self.__onMoneyChanged	# ��Ǯ�ı�
		#������
		self.__triggers["EVT_ON_ROLE_DEAD"] = self.__endTrade						#��ɫ���������ش���
		self.__triggers["EVT_ONTRADE_STATE_LEAVE"] = self.__onStateLeave
		self.__triggers["EVT_ON_BANKLOCK_FLAG_CHANGE"] = self.__onLockFlagChange
		self.__triggers["EVT_ON_BANKLOCK_TIME_CHANGE"] = self.__onLockTimeChange
		self.__triggers["EVT_ON_BANKLOCK_STATUAS_CHANGE"] = self.__onLockStatusChange

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	# -------------------------------------------------
	# items operation
	# -------------------------------------------------
	def __onActivateBag( self, index ) :
		"""
		����һ���ֿ�λ
		"""
		self.__pyItemsPanel.onBagActivated( index )

	def __onSwapItems( self, srcBank, srcOrder, dstBank, dstOrder ) :
		"""
		�ֿ⽻����Ʒλ��
		"""
		self.__pyItemsPanel.onItemSwaped( srcBank, srcOrder, dstBank, dstOrder )

	def __onUpdateItem( self, packIndex, itemIndex, baseItem ) :
		"""
		������Ʒ���ݣ��ƺ��Ƴ���ƷʱҲ�ߴ˽ӿ�
		"""
		self.__pyItemsPanel.onItemUpdated( packIndex, itemIndex, baseItem )

	def __onUpdateBagName( self, index, name ) :
		"""
		�ֿ����ָ���
		"""
		self.__pyItemsPanel.onBagNameUpdated( index, name )

	def __onAddBagItem( self, kitbagID, orderID, baseItem ) :
		"""
		���һ����Ʒ���ֿ�
		"""
		self.__pyItemsPanel.onItemAdded( kitbagID, orderID, baseItem )

	# -------------------------------------------------
	# function
	# -------------------------------------------------
	def __saveMoney( self ) :
		"""
		��Ǯ����ֿ�
		"""
		def requestInput( res, money ) :
			if res == DialogResult.OK and money > 0 :
				BigWorld.player().bank_storeMoney( money )
		MoneyInputBox().show( requestInput, labelGather.getText( "StoreWndRole:main", "saveAmount" ), self )

	def __takeMoney( self ) :
		"""
		�Ӳֿ�ȡǮ
		"""
		player = BigWorld.player()
		if player.bankMoney == 0 :									# ����ֿ�û��Ǯ��
			player.statusMessage( csstatus.CIB_MSG_NO_BANK_MONEY )
			return
		def requestInput( res, money ) :
			if res == DialogResult.OK and money > 0 :
				bankMoney = player.bankMoney
				if money <= bankMoney :								# ���������㹻��Ǯ����ȡ
					player.bank_fetchMoney( money )
				else:
					def query( rs_id ) :
						if rs_id == RS_OK :
							player.bank_fetchMoney( player.bankMoney )
					gold = bankMoney / 10000
					silver = bankMoney % 10000 / 100
					coin = bankMoney % 100
					# "���Ƿ�Ҫ��Ǯׯ��ʣ��Ĵ��%d��%d��%dͭȫ��ȡ����"
					msg = mbmsgs[0x0841] % ( gold, silver, coin )
					showMessage( msg, "", MB_OK_CANCEL, query, self )
		MoneyInputBox().show( requestInput, labelGather.getText( "StoreWndRole:main", "takeAmount"), self )

	def __extendPackage( self ) :
		"""
		��չ�ֿ�λ
		"""
		nextIndex = BigWorld.player().getNextBagIndex()
		if nextIndex >= csconst.BANK_MAX_COUNT:
			BigWorld.player().statusMessage( csstatus.BANK_CANNOT_OPEN_MORE_BAG )
			return
		def query( rs_id ) :
			if rs_id == RS_OK:
				BigWorld.player().requestOpenNextBag( False )
		# "����Ҫ%d����˿ľ�ſ��Ի����һ�ռ�,ȷ��ô?"
		description = mbmsgs[0x0842] % csconst.NEED_ITEM_COUNT_DICT[nextIndex]
		showMessage( description, "", MB_OK_CANCEL, query, self )

	def __onMoneyChanged( self, oldMoney, newMoney ) :
		"""
		��ҵĽ�Ǯ�ı�ʱ����
		"""
		goldNum = newMoney/10000
		sliverNum = ( newMoney - goldNum*10000 )/100
		copperNum = newMoney - goldNum*10000 - sliverNum*100
		self.__pyStGold.text = arithmetic.toUSValue( goldNum )
		self.__pyStSilver.text = arithmetic.toUSValue( sliverNum )
		self.__pyStCopper.text = arithmetic.toUSValue( copperNum )

	# -------------------------------------------------
	# exchange for bill
	# -------------------------------------------------
	def __onOpenChange( self ) :
		"""
		��Ԫ���һ�Ԫ��Ʊ
		"""
		player = BigWorld.player()
		status = player.bankLockerStatus
		self.__isChangeGold = True
		if status & 0x02 == 0x02: 													# ��������״̬������������
			self.__onPasswordLock()
		else:
			self.__exchangeBillInput()

	def __exchangeBillInput( self ) :
		"""
		Ԫ��Ʊ�һ�����
		"""
		def inputCallback( res, amount ) :
			self.__isChangeGold = False
			if res == DialogResult.OK :
				player = BigWorld.player()
				if amount > 20000 :
					# "һ�οɶһ���Ԫ��Ʊ�������Ϊ%d��"
					showAutoHideMessage( 3.0, mbmsgs[0x084c] % 20000, mbmsgs[0x0c22], pyOwner = self )
				elif amount < 1 :
					# "һ�οɶһ���Ԫ��Ʊ��С����Ϊ%d��"
					showAutoHideMessage( 3.0, mbmsgs[0x084d] % 1, mbmsgs[0x0c22], pyOwner = self )
				elif amount > player.gold :
					# "Ҫ�һ�Ԫ��������Я��Ԫ������"
					showAutoHideMessage( 3.0, 0x084e, mbmsgs[0x0c22], pyOwner = self )
				else :
					def query( rs_id ) :
						if rs_id == RS_OK :
							if amount > player.gold :
								# "Ҫ�һ�Ԫ��������Я��Ԫ������"
								showAutoHideMessage( 3.0, 0x084e, mbmsgs[0x0c22], pyOwner = self )
							else :
								player.bank_changeGoldToItem( amount )
					# "�Ƿ�ȷ����%dԪ���һ�ΪԪ��Ʊ?"
					showMessage( mbmsgs[0x0843] % amount, "", MB_OK_CANCEL, query, pyOwner = self )
		AmountInputBox().show( inputCallback, self, ( 1, 20000 ) )

	# -------------------------------------------------
	# lock about
	# -------------------------------------------------
	def __onLockFlagChange( self, flag, remainTime ):
		if flag == 0:
			# "Ǯׯ�����Ѿ��ɹ��趨�����μ���������"
			showMessage( 0x0844,"", MB_OK )
		elif flag == 1:
			# "Ǯׯ�����Ѿ��ɹ��޸ģ����μ���������"
			showMessage( 0x0845,"", MB_OK )
		elif flag == 2:
			# "����������벻��ȷ������������"
			showMessage( 0x0846,"", MB_OK )
		elif flag == 3:
			# "������ľ����벻��ȷ������������"
			showMessage( 0x0847,"", MB_OK )
		elif flag == 4:
			# "Ǯׯ�����ɹ���"
			showMessage( 0x0848, "", MB_OK )
		elif flag == 5:
			# "Ǯׯ�����ɹ���"
			showMessage( 0x0849, "", MB_OK )
		elif flag == 6 :
			showMessage( mbmsgs[0x084a] % ( remainTime ), "", MB_OK )
		elif flag == 7 :
			showMessage( 0x084b,"", MB_OK )

	def __onLockTimeChange( self, time ):
		if time > 0:
			# "���Ѿ���������������Σ����Ժ�����"
			showMessage( "���Ѿ���������������Σ���60�������","", MB_OK )

	def __onLockStatusChange( self, status ):
		if self.__isChangeGold and status & 0x02 != 0x02 : 							# ��ʱ�ڶһ�Ԫ��Ʊ
			self.__exchangeBillInput()
		pswWindow = PasswordWindow.getInstance()
		if pswWindow is not None :
			pswWindow.updateLockStatus( status, self )

	def __onPasswordLock( self ):
		player = BigWorld.player()
		lockStatus = player.bankLockerStatus
		def operate( result, text ):
			if result == PassResult.LOCK:
				player.bank_lock()
			elif result == PassResult.UNLOCK:
				player.bank_unlock( text )
			elif result == PassResult.FOREUNLOCK:
				player.bank_clearPassword( text )
		PasswordWindow.instance().show( operate, lockStatus, self )

	# -------------------------------------------------
	# window about
	# -------------------------------------------------
	def __beginTrade( self, npcID ) :
		"""
		������֪ͨ�򿪲ֿ����
		"""
		player = BigWorld.player()
		ECenter.fireEvent( "EVT_ONTRADE_STATE_LEAVE", player.tradeState )
		player.tradeState = csdefine.TRADE_INVENTORY
		self.setTrappedEntID( npcID )
		self.show()

	def __endTrade( self ) :
		self.hide()

	def __onStateLeave( self, state ) :
		if state == csdefine.TRADE_INVENTORY :
			player = BigWorld.player()
			player.leaveBank()
			player.tradeState = csdefine.TRADE_NONE
			self.hide()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setPassWord( self, oldPassWord, newPassWord ) :
		"""
		�˺���������PasswordWindow���ص�
		"""
		BigWorld.player().bank_setPassword( oldPassWord, newPassWord )

	def onLeaveWorld( self ) :
		self.__pyItemsPanel.cleanPanel()
		self.hide()

	def show( self ) :
		UnfixedTrapWindow.show( self )
		rds.helper.courseHelper.openWindow( "cangku__chuangkou" )

	def hide( self ) :
		player = BigWorld.player()
		player.leaveBank()
		player.tradeState = csdefine.TRADE_NONE
		UnfixedTrapWindow.hide( self )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )

	def dispose( self ) :
		self.__pyItemsPanel.dispose()
		UnfixedTrapWindow.dispose( self )

	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getCurrSelIndex( self ) :
		return self.__pyItemsPanel.currBagIndex

	currBagIndex = property( _getCurrSelIndex )						# ��ȡ��ǰѡ�еı�������