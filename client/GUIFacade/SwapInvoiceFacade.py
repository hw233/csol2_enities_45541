# -*- coding: gb18030 -*-
#
# $Id: SwapInvoiceFacade.py,v 1.17 2008-05-30 09:54:48 fangpengjun Exp $

from bwdebug import *
import BigWorld
from ItemsFactory import ObjectItem
from event.EventCenter import *
import csconst

class SwapInvoiceFacade:
	@staticmethod
	def reset():
		pass



# ------------------------------->
# �����õײ����
# ------------------------------->
def onInviteSwapItem( invitorName, flag ):
	"""
	����������н���

	flagΪ1���ʾ����Ʒ���ף������ǳ��ｻ��
	"""
	if flag:
		fireEvent( "EVT_ON_RSI_INVITE_SWAP_ITEM", invitorName )
	else:
		fireEvent( "EVT_ON_RSI_INVITE_SWAP_PET", invitorName )

def onSwapItemBegin( invitorName ):
	"""
	��ʼ���뽻��
	"""
	# ���뽻��״̬ʱ��Ҫ�����ߵİ�ť��ʼ����Ĭ��״̬
	#onDstSwapStateChanged( False, False )
	#onSelfSwapStateChanged( False, False )
	# ֪ͨ���׿�ʼ
	fireEvent( "EVT_ON_RSI_SWAP_ITEM_BEGIN", invitorName )

def onSwapItemEnd():
	"""
	���׽���
	"""
	fireEvent( "EVT_ON_RSI_SWAP_ITEM_END" )


def onDstSwapItemChanged( swapOrder, item ):
	"""
	����Ŀ����Ʒ�ı�

	@param swapOrder: ��������λ��
	@type  swapOrder: INT
	@param      item: �ı�����Ʒ�������Ϊ������None
	@type       item: CItemBase
	"""
	if item is None:
		itemInfo = None
	else:
		itemInfo = ObjectItem( item )
	fireEvent( "EVT_ON_RSI_DST_ITEM_CHANGED", swapOrder, itemInfo )

def onDstSwapMoneyChanged( quantity ):
	"""
	����Ŀ��ı��Ǯ����
	"""
	fireEvent( "EVT_ON_RSI_DST_MONEY_CHANGED", quantity )

def onSelfSwapItemChanged( swapOrder, item ):
	"""
	�Լ�ĳ��λ�õ���Ʒ��Ϣ�ı�

	@param swapOrder: ��������λ��
	@type  swapOrder: INT
	@param      item: �ı�����Ʒ�������Ϊ������None
	@type       item: CItemBase
	"""
	if item is None:
		itemInfo = None
	else:
		itemInfo = ObjectItem( item )
	fireEvent( "EVT_ON_RSI_SELF_ITEM_CHANGED", swapOrder, itemInfo )

def onSelfSwapMoneyChanged( quantity ):
	"""
	�Լ���Ǯ�����ı�
	"""
	fireEvent( "EVT_ON_RSI_SELF_MONEY_CHANGED", quantity )


# ------------------------------->
# facade interface
# ------------------------------->
def getSwapItemBagSpace():
	"""
	���׿��С
	@return: int
	"""
	return csconst.TRADE_ITEMS_UPPER_LIMIT

def inviteSwapItem( entity, flag ):
	"""
	����Ŀ��entity���н���
	"""
	BigWorld.player().si_requestSwap( entity, flag )

def inviteSwapItemReply( accept = True ):
	"""
	���������

	@param accept: �Ƿ���ܽ���
	@type  accept: BOOL
	"""
	BigWorld.player().si_replySwapItemInvite( accept )

def cancelSwapItem():
	"""
	����ȡ������
	"""
	BigWorld.player().si_tradeCancel()

def changeSwapItem( swapOrder, kitOrder, order ):
	"""
	�ı�ĳ��λ���ϵĽ�����Ʒ

	@param swapOrder: �������е�λ��
	@type  swapOrder: INT
	@param  kitOrder: ��Ʒ���ڵı���
	@type   kitOrder: INT
	@param     order: ��Ʒ���ڵ�λ��
	@type      order: INT
	"""
	BigWorld.player().si_changeItem( swapOrder, kitOrder, order )

def removeSwapItem( swapOrder ):
	"""
	ɾ��ĳ��λ���ϵĽ�����Ʒ

	@param swapOrder: �������е�λ��
	@type  swapOrder: INT
	"""
	BigWorld.player().si_removeItem( swapOrder )

def changeSwapMoney( quantity ):
	"""
	�ı��Ǯ��

	@param quantity: ��Ǯ����
	@type  quantity: INT
	"""
	BigWorld.player().si_changeMoney( quantity )

def swapAccept():
	"""
	��һ��ȷ��
	"""
	BigWorld.player().si_accept()

def swapAccept2():
	"""
	�ڶ���ȷ��
	"""
	BigWorld.player().si_secondAccept( True )

def getDstSwapItemDescription( swapOrder ):
	"""
	��ȡĿ�����Ʒ����

	@return: String
	"""
	player = BigWorld.player()
	try:
		return player.dstSIItem[swapOrder].description( player )
	except KeyError:
		return ""

def getSelfSwapItemDescription( swapOrder ):
	"""
	��ȡ�Լ�����Ʒ����

	@return: String
	"""
	player = BigWorld.player()
	try:
		return player.mySIItem[swapOrder].description( player )
	except KeyError:
		return ""
