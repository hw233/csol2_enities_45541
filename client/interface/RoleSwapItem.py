# -*- coding: gb18030 -*-
#
# $Id: RoleSwapItem.py,v 1.41 2008-06-21 01:34:23 zhangyuxing Exp $

"""
"""

import BigWorld
import csdefine
import csconst
import csstatus
from bwdebug import *
import GUIFacade

from event.EventCenter import *
from ItemsFactory import ObjectItem


class RoleSwapItem:
	"""
	��Ҽ���Ʒ������ش���
	"""
	def __init__( self ):
		"""
		"""
		self.si_dstState = 0	# ���׶����״̬
		self.si_myItem = {}
		self.si_dstItem = {}
		self.si_dstPet = {}
		self.si_targetID = 0

	def si_resetData( self ):
		"""
		�����������ݵ�δ����ǰ״̬
		"""
		self.si_dstState = 0	# ���׶����״̬
		self.si_myItem.clear()
		self.si_dstItem.clear()
		self.si_dstPet.clear()
		self.si_targetID = 0


	def si_dstChangePet( self, epitome ):
		"""
		Define method.
		���׶���ı佻����Ʒ

		param epitome: ��������
		type epitome: PET_EPITOME
		"""
		self.si_dstPet[ epitome.databaseID ] = epitome
		# ֪ͨ���档
		fireEvent( "EVT_ON_RSI_DST_PET_CHANGE", epitome )

	def si_dstChangeItem( self, swapOrder, itemData ):
		"""
		Define method.
		���׶���ı佻����Ʒ

		@param swapOrder: �ĸ�λ�õ���Ʒ�ı�
		@type  swapOrder: UINT8
		@param  itemData: ��Ʒ����
		@type   itemData: ITEM
		"""
		self.si_dstItem[ swapOrder ] = itemData
		GUIFacade.onDstSwapItemChanged( swapOrder, itemData )

	def si_meChangeItem( self, swapOrder, kitOrder, uid ):
		"""
		Define method.
		�ı��Լ��Ľ�����Ʒ

		@param swapOrder: ����λ��
		@param  kitOrder: �ĸ�����
		@param       uid: �ĸ���Ʒ
		"""
		if self.si_myItem.has_key( swapOrder ):
			itemInfo = ObjectItem( self.si_myItem[ swapOrder ] )
			fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", itemInfo.kitbagID, itemInfo.orderID, False ) #������Ʒ
			del self.si_myItem[ swapOrder ] #ɾ�������б��жԸ���Ʒ�ļ�¼
		self.si_myItem[ swapOrder ] = self.getItemByUid_( uid )
		GUIFacade.onSelfSwapItemChanged( swapOrder, self.si_myItem[ swapOrder ] )
		itemInfo = ObjectItem( self.si_myItem[ swapOrder ] )
		fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", itemInfo.kitbagID, itemInfo.orderID, True ) #������Ʒ


	def si_removeSwapItem( self, flag, swapOrder ):
		"""
		Define method.
		���׶���ɾ��һ��������Ʒ

		@param    flag: ɾ���Ľ�����λ, 0 ��ʾɾ���Լ�����λ, 1 ��ʾɾ��Ŀ�����λ
		@type     flag: UINT8
		@param swapOrder: ������λ��
		@type  swapOrder: UINT8
		"""
		if flag == 0:
			#GUIFacade.onSelfSwapItemChanged( swapOrder, self.si_myItem[swapOrder] )
			itemInfo = ObjectItem( self.si_myItem[ swapOrder ] )
			fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", itemInfo.kitbagID, itemInfo.orderID, False ) #������Ʒ
			del self.si_myItem[ swapOrder ] #ɾ�������б��жԸ���Ʒ�ļ�¼
			GUIFacade.onSelfSwapItemChanged( swapOrder, None )
		else:
			del self.si_dstItem[ swapOrder ]
			GUIFacade.onDstSwapItemChanged( swapOrder, None )


	def set_si_myMoney( self, oldValue = 0 ):
		"""
		���Լ��ı佻�׽�ȷ��ʱ
		"""
		#DEBUG_MSG( "oldValue =", oldValue, "newValue =", self.si_myMoney )
		GUIFacade.onSelfSwapMoneyChanged( self.si_myMoney )


	def set_si_dstMoney( self, oldValue = 0 ):
		"""
		�����׶���ı佻�׽��ʱ
		"""
		#DEBUG_MSG( "oldValue =", oldValue, "newValue =", self.si_dstMoney )
		GUIFacade.onDstSwapMoneyChanged( self.si_dstMoney )


	def set_si_myPetDBID( self, oldValue ):
		"""
		�ı����ڽ��׵ĳ���
		"""
		if oldValue != self.si_myPetDBID:
			fireEvent( "EVT_ON_RSI_SELF_PET_CHANGED", self.si_myPetDBID )

	def set_si_myState( self, oldValue = 0 ):
		"""
		������״̬�ı�ʱ
		"""
		DEBUG_MSG( "oldValue =", oldValue, "newValue =", self.si_myState )
		if self.si_myState == csdefine.TRADE_SWAP_DEFAULT:
			if oldValue == csdefine.TRADE_SWAP_INVITE or oldValue == csdefine.TRADE_SWAP_PET_INVITE:
				# �ܾ�����
				BigWorld.player().statusMessage( csstatus.ROLE_TRADE_TARGET_REFUSED )
				return
			if oldValue == csdefine.TRADE_SWAP_WAITING or oldValue == csdefine.TRADE_SWAP_PET_WAITING:
				return
			if oldValue != csdefine.TRADE_SWAP_LOCKAGAIN:
				for order in self.si_myItem:
					itemInfo = ObjectItem( self.si_myItem[ order ] )
					fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", itemInfo.kitbagID, itemInfo.orderID, False ) #������Ʒ
			GUIFacade.onSwapItemEnd()
			self.si_resetData()
		elif self.si_myState == csdefine.TRADE_SWAP_INVITE or self.si_myState == csdefine.TRADE_SWAP_PET_INVITE:
			BigWorld.callback( csconst.TRADE_WAITING_TIME, self.onSwapInviteTimer )
		elif self.si_myState == csdefine.TRADE_SWAP_WAITING or self.si_myState == csdefine.TRADE_SWAP_PET_WAITING:
			if self.si_targetID == 0:
				DEBUG_MSG( "�Է���id��û���¡�" )
				return
			# ������׶����id���ڼ���״̬���£���ô������̸��ѯ���Ƿ��׵Ĵ���
			try:
				name = BigWorld.entities[ self.si_targetID ].getName()
			except KeyError:
				self.si_tradeCancel()
				return
			if not self.allowTrade:	#�ܾ�����
				self.si_tradeCancel()
				return
			flag = self.si_myState == csdefine.TRADE_SWAP_WAITING
			GUIFacade.onInviteSwapItem( name, flag )
		elif self.si_myState == csdefine.TRADE_SWAP_BEING:
			# ��ʾ���״�����ʼ����
			#self.si_dstItem = {}
			#self.si_myItem = {}
			if oldValue == csdefine.TRADE_SWAP_INVITE or oldValue == csdefine.TRADE_SWAP_WAITING:
				GUIFacade.onSwapItemBegin( BigWorld.entities[ self.si_targetID ].getName() )
			#elif oldValue == csdefine.TRADE_SWAP_PET_BEING or oldValue == csdefine.TRADE_SWAP_PET_LOCK:
			#	DEBUG_MSG( "�ӳ��ｻ�׽�����Ʒ���ס�" )
			fireEvent( "EVT_ON_RSI_SELF_SWAP_STATE_CHANGED", self.si_myState )
		elif self.si_myState == csdefine.TRADE_SWAP_LOCK:
			fireEvent( "EVT_ON_RSI_SELF_SWAP_STATE_CHANGED", self.si_myState )
			#GUIFacade.onDstSwapStateChanged( True, False )
			#GUIFacade.onSelfSwapStateChanged( False, True )
		elif self.si_myState == csdefine.TRADE_SWAP_SURE:
			fireEvent( "EVT_ON_RSI_SELF_SWAP_STATE_CHANGED", self.si_myState )
		elif self.si_myState == csdefine.TRADE_SWAP_PET_BEING:
			DEBUG_MSG( "�ı���ｻ�׵����ݣ��ظ��������ڽ���״̬��" )
			fireEvent( "EVT_ON_RSI_SELF_SWAP_STATE_CHANGED", self.si_myState )
			if oldValue == csdefine.TRADE_SWAP_PET_INVITE or oldValue == csdefine.TRADE_SWAP_PET_WAITING:
				fireEvent( "EVT_ON_RSI_SWAP_PET_BEGIN", BigWorld.entities[ self.si_targetID ].getName() )
		elif self.si_myState == csdefine.TRADE_SWAP_PET_LOCK:
			fireEvent( "EVT_ON_RSI_SELF_SWAP_STATE_CHANGED", self.si_myState )
			DEBUG_MSG( "�������ｻ�ס�" )

	def onSwapInviteTimer( self ):
		"""
		����ʱ������
		"""
		if self.si_myState == csdefine.TRADE_SWAP_INVITE or \
		self.si_myState == csdefine.TRADE_SWAP_PET_INVITE:
			self.si_tradeCancel()


	def si_replySwapItemInvite( self, accept = True ):
		"""
		��Ʒ���������

		@param accept: �Ƿ���ܽ���
		@type  accept: BOOL
		"""
		if not self.__canTrade():
			return
		if accept:
			self.cell.si_changeStateFC( csdefine.TRADE_SWAP_BEING )		# ���ܽ���
		else:
			self.si_tradeCancel()				# �����ܽ���


	def si_replySwapPetInvite( self, accept = True ):
		"""
		���ｻ�������

		@param accept: �Ƿ���ܽ���
		@type  accept: BOOL
		"""
		if not self.__canTrade():
			return
		if accept:
			self.cell.si_changeStateFC( csdefine.TRADE_SWAP_PET_BEING )		# ���ܽ���
		else:
			self.si_tradeCancel()				# �����ܽ���


	def set_si_targetID( self, oldValue = 0 ):
		"""
		"""
		DEBUG_MSG( "oldValue =", oldValue, "newValue =", self.si_targetID )

		# ���������״̬���ڽ��׶����id���£���ô������ѯ���Ƿ���н���
		if self.si_targetID != 0 and ( self.si_myState == csdefine.TRADE_SWAP_WAITING or self.si_myState == csdefine.TRADE_SWAP_PET_WAITING ):
			try:
				name = BigWorld.entities[ self.si_targetID ].getName()
			except KeyError:
				self.si_tradeCancel()
				return
			if not self.allowTrade:	#�ܾ�����
				self.si_tradeCancel()
				return
			self.si_swapFlag = True
			flag = self.si_myState == csdefine.TRADE_SWAP_WAITING
			GUIFacade.onInviteSwapItem( name, flag )


	def si_getTargetEntity( self ):
		"""
		��ý��׶����entity
		"""
		return BigWorld.entities.get( self.si_targetID )


	def si_tradeCancel( self ):
		"""
		ȡ������
		"""
		self.cell.si_tradeCancelFC()


	def si_requestSwap( self, entity, flag ):
		"""
		������ĳentity����
		"""
		if not entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_TARGET_REFUSED )
			return

		if self.id == entity.id:
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_CANNOT_TRADE_SELF )
			return
		if self.position.flatDistTo( entity.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.ROLE_TRADE_TARGET_TOO_FAR )
			return

		self.cell.si_requestSwapFC( entity.id, flag )


	def si_changeItem( self, swapOrder, kitOrder, order ):
		"""
		�ı�ĳ��λ���ϵĽ�����Ʒ

		@param swapOrder: �������е�λ��
		@type  swapOrder: INT
		@param  kitOrder: ��Ʒ���ڵı���
		@type   kitOrder: INT
		@param     order: ��Ʒ���ڵ�λ��
		@type      order: INT
		"""
		if not self.__isTrading():	# û���ڽ���״̬���Ѵ���ȷ��״̬
			#ERROR_MSG( "state not allow." )
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_OPERATER_NOT_ALLOW )
			return
		if swapOrder >= csconst.TRADE_ITEMS_UPPER_LIMIT:
			#ERROR_MSG( "swap order overflow." )
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_POS_WRONG )
			return
		try:
			kit = self.kitbags[ kitOrder ]
		except KeyError:
			#ERROR_MSG( "no such kitbag." )
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_KITBAG_INVALID )
			return

		order = kitOrder * csdefine.KB_MAX_SPACE + order
		item = self.getItem_( order )

		if item is None:
			#ERROR_MSG( "item not found." )
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_ITEM_INVALID )
			return

		if not item.canGive():
			#ERROR_MSG( "item can't trade." )
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_ITEM_CANT_TRAEDED )
			return

		if not self.__canTrade():
			return
		uid = self.order2uid( order )
		self.cell.si_changeItemFC( swapOrder, kitOrder, uid )


	def si_removeItem( self, swapOrder ):
		"""
		ɾ��ĳ��λ���ϵĽ�����Ʒ

		@param swapOrder: �������е�λ��
		@type  swapOrder: INT
		"""
		if not self.__isTrading():	# û���ڽ���״̬���Ѵ���ȷ��״̬
			#ERROR_MSG( "state not allow." )
			self.statusMessage( csstatus.ROLE_TRADE_OPERATER_NOT_ALLOW )
			return
		if swapOrder >= csconst.TRADE_ITEMS_UPPER_LIMIT:
			#ERROR_MSG( "swap order overflow." )
			self.statusMessage( csstatus.ROLE_TRADE_POS_WRONG  )
			return
		if not self.si_myItem.has_key( swapOrder ):
			#ERROR_MSG( "swap order item not exist." )
			self.statusMessage( csstatus.ROLE_TRADE_ITEM_INVALID )
			return
		if not self.__canTrade():
			return
		self.cell.si_removeItemFC( swapOrder )


	def si_changeMoney( self, amount ):
		"""
		�ı��Ǯ��
		"""
		if not self.__isTrading():	# û���ڽ���״̬���Ѵ���ȷ��״̬
			#ERROR_MSG( "state not allow." )
			self.statusMessage( csstatus.ROLE_TRADE_OPERATER_NOT_ALLOW )
			return
		if amount > self.money:
			#ERROR_MSG( "money not enough." )
			GUIFacade.onSelfSwapMoneyChanged( self.si_myMoney )
			self.statusMessage( csstatus.ROLE_TRADE_HAVET_SUCH_MONEY, amount )
			return
		if not self.__canTrade():
			return
		self.cell.si_changeMoneyFC( amount )


	def si_changePet( self, petDBID ):
		"""
		�ı����ڽ��׵ĳ���
		"""
		if not self.__isTrading():	# û���ڽ���״̬���Ѵ���ȷ��״̬
			#ERROR_MSG( "state not allow." )
			self.statusMessage( csstatus.ROLE_TRADE_OPERATER_NOT_ALLOW )
			return
		if not self.__canTrade():
			return
		self.cell.si_changePetFC( petDBID )


	def si_removePet( self ):
		"""
		�Ƴ����׳���
		"""
		if not self.__isTrading():	# û���ڽ���״̬���Ѵ���ȷ��״̬
			self.statusMessage( csstatus.ROLE_TRADE_OPERATER_NOT_ALLOW )
			return
		if not self.__canTrade():
			return
		self.cell.si_removePetFC()


	def si_dstRemovePet( self ):
		"""
		Define method.
		���׶����Ƴ����׳���
		"""
		self.si_dstPet.clear()
		# ֪ͨ���棬wsf
		fireEvent( "EVT_ON_RSI_DST_PET_REMOVE" )

	def si_secondAccept( self, accept = True ):
		"""
		��Ʒ�ڶ���ȷ��
		"""
		if accept:
			self.cell.si_changeStateFC( csdefine.TRADE_SWAP_SURE )
		else:
			self.cell.si_changeStateFC( csdefine.TRADE_SWAP_BEING )


	def si_accept( self ):
		"""
		��Ʒ��һ��ȷ��
		"""
		self.cell.si_changeStateFC( csdefine.TRADE_SWAP_LOCK )


	def si_acceptPet( self ):
		"""
		�����һ��ȷ��
		"""
		self.cell.si_changeStateFC( csdefine.TRADE_SWAP_PET_LOCK )

	def si_secondAcceptPet( self, accept = True ):
		"""
		����ڶ���ȷ��
		"""
		if accept:
			self.cell.si_changeStateFC( csdefine.TRADE_SWAP_SURE )
		else:
			self.cell.si_changeStateFC( csdefine.TRADE_SWAP_PET_BEING )


	def si_changeState( self, state ):
		"""
		��Ҹı��Լ�״̬�Ľӿڣ�������ȷ�Ͻ����൱�ڸı�״̬��
		"""
		if not self.__canTrade():
			return
		self.cell.si_changeStateFC( state )

	def __canTrade( self ):
		"""
		�Ƿ��ܹ����н��׻�����򷵻�True�����򷵻�False
		"""
		dstEntity = BigWorld.entities.get( self.si_targetID )
		if dstEntity == None:
			return False
		if self.position.flatDistTo( dstEntity.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.ROLE_TRADE_TARGET_TOO_FAR )
			return False
		return True


	def __isTrading( self ):
		"""
		�ж��Լ��Ƿ��ڽ���״̬��

		@return: bool
		"""
		#�ڿ�ʼ���׵�����ǰ���ж���Ҵ��ڽ���״̬��
		if self.si_myState > csdefine.TRADE_SWAP_WAITING and self.si_myState < csdefine.TRADE_SWAP_SURE:
			return True
		return False


	def si_dstStateChange( self, state ):
		"""
		Define method.
		���׶����״̬�ı�
		"""
		self.si_dstState = state
		fireEvent( "EVT_ON_RSI_DST_SWAP_STATE_CHANGED", state )

#
# $Log: not supported by cvs2svn $
# Revision 1.40  2008/06/05 02:21:47  wangshufeng
# ����״̬ΪTRADE_SWAP_DEFAULTʱ���رս��״���
#
# Revision 1.39  2008/05/31 03:04:38  yangkai
# ��Ʒ��ȡ�ӿڸı�
#
# Revision 1.38  2008/05/30 09:54:15  fangpengjun
# Ϊ���ｻ����Ӳ�����Ϣ
#
# Revision 1.37  2008/05/28 08:36:57  wangshufeng
# ������ｻ�׺���Ʒ���ף���Ӧ��������
#
# Revision 1.36  2008/05/22 08:03:05  wangshufeng
# add method;si_getTargetEntity,���Ŀ�����ʵ��
#
# Revision 1.35  2008/05/04 06:44:28  zhangyuxing
# no message
#
# Revision 1.34  2008/03/19 02:49:00  wangshufeng
# �°���ҽ���ϵͳ
#

#
#
