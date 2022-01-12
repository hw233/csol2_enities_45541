# -*- coding: gb18030 -*-
#
# $Id: RoleSwapItem.py,v 1.26 2008-08-13 00:51:13 wangshufeng Exp $

"""
Ϊ�˱�֤�������첽����µ����ݽ�����ȫ����Ҫ���������cellʱ��1��2����ӳ١�wsf
"""
import BigWorld
import cschannel_msgs
import ShareTexts as ST
import csdefine
import csconst
import Const
import csstatus
import Function
from bwdebug import *
from MsgLogger import g_logger
from ObjectScripts.GameObjectFactory import g_objFactory
import ItemTypeEnum
import sys

class RoleSwapState:
	"""
	"""
	def __init__( self ):
		"""
		����״̬������
		TRADE_SWAP_DEFAULT					= 0		# ����Ĭ��״̬
		TRADE_SWAP_INVITE					= 1		# ��������״̬
		TRADE_SWAP_WAITING					= 2		# ���׵ȴ�״̬(״̬����15������û��Ӧ����ȡ��)
		TRADE_SWAP_BEING					= 3		# ��Ʒ���׿�ʼ״̬
		TRADE_SWAP_LOCK						= 4		# ��Ʒ����״̬
		TRADE_SWAP_PET_INVITE				= 5		# ���ｻ������״̬
		TRADE_SWAP_PET_WAITING				= 6		# ���ｻ�׵ȴ�״̬
		TRADE_SWAP_PET_BEING				= 7		# ���ｻ�׿�ʼ״̬
		TRADE_SWAP_PET_LOCK					= 8		# ���ｻ������״̬
		TRADE_SWAP_SURE						= 9		# ����ȷ��״̬
		TRADE_SWAP_LOCKAGAIN				= 10	# ˫���ٴ�����״̬
		"""
		pass


	def enter( self, srcEntity, dstEntity ):
		"""
		�����״̬���ڴ˺�������һЩ��ʼ����

		srcEntity: �����״̬��entity
		dstEntity: ���׶����entity
		"""
		pass


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	����״̬�ı�
		@type	state		:	UINT8
		@param	state		:	�ı��״̬
		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı�״̬��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		@rtype:	BOOL,�ܹ��ı䵽state״̬�򷵻�True�����򷵻�False
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def onDstStateChanged( self, srcEntity, destEntity, state ):
		"""
		�����׶���״̬�ı�ʱ�յ�֪ͨ

		srcEntity: �����״̬��entity
		dstEntity: ���׶����entity
		state: ���׶���ĵ�ǰ����״̬
		"""
		pass


	def onDstItemChanged( self, srcEntity, dstEntity, swapOrder, itemInstance ):
		"""
		�����׶���ı���Ʒʱ�յ�֪ͨ

		srcEntity: �����״̬��entity
		dstEntity: ���׶����entity
		swapOrder: ���ı�Ľ�����Ŀ��λ��
		itemInstance: ��Ʒʵ��
		"""
		pass


	def onDstItemRemoved( self, srcEntity, dstEntity, swapOrder ):
		"""
		�����׶����Ƴ���Ʒʱ�յ�֪ͨ

		srcEntity: �����״̬��entity
		dstEntity: ���׶����entity
		swapOrder: ���Ƴ��Ľ�����Ŀ��λ��
		"""
		pass


	def onDstMoneyChanged( self, srcEntity, dstEntity, amount ):
		"""
		�����׶���ı��Ǯʱ�յ�֪ͨ

		srcEntity: �����״̬��entity
		dstEntity: ���׶����entity
		amount: ���ı�Ľ�Ǯ����
		"""
		pass


	def onDstPetChanged( self, srcEntity, dstEntity, petDBID ):
		"""
		�����׶���ı����ʱ�յ�֪ͨ

		srcEntity: �����״̬��entity
		dstEntity: ���׶����entity
		petDBID: ���ı�ĳ���dbid
		"""
		pass


	def onDstPetRemoved( self, srcEntity, dstEntity ):
		"""
		�����׶����Ƴ�����ʱ�յ�֪ͨ

		srcEntity: �����״̬��entity
		dstEntity: ���׶����entity
		"""
		pass


	def changeItem( self, srcEntity, dstEntity, swapOrder, kitOrder, uid, itemInstance ):
		"""
		virtual method
		������Ʒ�����ӵ���״̬�ĸı�
		��״̬�²���

		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı���Ʒ��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		@type	swapOrder	:	�ı�Ľ�����λ��
		@param	swapOrder	:	UINT8
		@type	kitOrder	:	������
		@param	kitOrder	:	UINT8
		@type	uid			:	��Ʒ��uid
		@param	uid			:	INT64
		@type	itemInstance	:	��Ʒʵ��
		@param	itemInstance	:	ITEM
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		�Ƴ�һ����Ʒ

		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı���Ʒ��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		@type	swapOrder	:	�ı�Ľ�����λ��
		@param	swapOrder	:	UINT8
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		�ı��Ǯ

		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı���Ʒ��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		@type	amount	:	��Ǯ����
		@param	amount	:	UINT32
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapState can't allow to changeMoney" % ( srcEntity.id, dstEntity.id ) )


	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		virtual method
		�ı����

		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı���Ʒ��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		@type	petDBID	:	�����dbid
		@param	petDBID	:	INT64
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to changePet" % ( srcEntity.id, dstEntity.id ) )


	def removePet( self, srcEntity, dstEntity ):
		"""
		virtual method
		�Ƴ�����

		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı���Ʒ��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to removePet" % ( srcEntity.id, dstEntity.id ) )


class RoleSwapDefaultState( RoleSwapState ):
	"""
	�޽���״̬��
	csdefine.TRADE_SWAP_DEFAULT
	���Խ���csdefine.TRADE_SWAP_WAITING��csdefine.TRADE_SWAP_INVITE״̬
	״̬���������Ӧ��״̬��������
	"""
	_instance = None
	def __init__( self ):
		assert RoleSwapDefaultState._instance is None
		RoleSwapState.__init__( self )


	def enter( self, srcEntity, dstEntity ):
		"""
		�����״̬���ڴ˺�������һЩ��ʼ��

		srcEntity: �����״̬��entity
		dstEntity: ���׶����entity
		"""
		srcEntity.si_clearSwapPet()
		srcEntity.statusMessage( csstatus.ROLE_TRADE_CANCEL )
		srcEntity.si_clearSwapData()							# �������ڽ��׵���Ʒ
		srcEntity.si_targetID = 0


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	����״̬�ı�
		@type	state		:	UINT8
		@param	state		:	�ı��״̬
		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı�״̬��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		"""
		if state == csdefine.TRADE_SWAP_INVITE:
			return True

		if state == csdefine.TRADE_SWAP_WAITING:
			if srcEntity.iskitbagsLocked():
				if dstEntity.isReal():
					dstEntity.statusMessage( csstatus.ROLE_TRADE_CANNOT_TRADE )
				else:
					dstEntity.remoteCall( "statusMessage", ( csstatus.ROLE_TRADE_CANNOT_TRADE, ) )
				return False
			return True

		if state == csdefine.TRADE_SWAP_PET_INVITE:
			return True

		if state == csdefine.TRADE_SWAP_PET_WAITING:
			return True

		return False

	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		�����׶���״̬�ı�ʱ�յ�֪ͨ��ֻ��Ӱ�켺���ĶԷ�״̬����
		"""
		if dstState == csdefine.TRADE_SWAP_INVITE:	# �Է���״̬ת��Ϊ����״̬
			srcEntity.si_changeState( csdefine.TRADE_SWAP_WAITING, dstEntity )
			return

		if dstState == csdefine.TRADE_SWAP_PET_INVITE:	# �Է���״̬ת��Ϊ����״̬
			srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_WAITING, dstEntity )
			return

	def onDstItemChanged( self, srcEntity, dstEntity, swapOrder, itemInstance ):
		"""
		"""
		pass


	def onDstItemRemoved( self, srcEntity, dstEntity, swapOrder ):
		"""
		"""
		pass


	def onDstMoneyChanged( self, srcEntity, dstEntity, amount ):
		"""
		"""
		pass


	def onDstPetChanged( self, srcEntity, dstEntity, petDBID ):
		"""
		"""
		pass


	def onDstPetRemoved( self, srcEntity, dstEntity ):
		"""
		"""
		pass


	def changeItem( self, srcEntity, dstEntity, swapOrder, kitOrder, uid, itemInstance ):
		"""
		virtual method
		������Ʒ�����ӵ���״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapDefaultState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		������Ʒ���Ƴ�����״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapDefaultState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		��Ǯ�����ı�
		��״̬�²���
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapDefaultState can't allow to changeMoney" % ( srcEntity.id, dstEntity.id ) )


	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		virtual method
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this state can't allow to changePet" % ( srcEntity.id, dstEntity.id ) )


	def removePet( self, srcEntity, dstEntity ):
		"""
		virtual method
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this state can't allow to removePet" % ( srcEntity.id, dstEntity.id ) )


	@staticmethod
	def instance():
		if not RoleSwapDefaultState._instance:
			RoleSwapDefaultState._instance = RoleSwapDefaultState()
		return RoleSwapDefaultState._instance


class RoleSwapInviteState( RoleSwapState ):
	"""
	������״̬
	csdefine.TRADE_SWAP_INVITE
	"""
	_instance = None

	def __init__( self ):
		"""
		"""
		assert RoleSwapInviteState._instance is None
		RoleSwapState.__init__( self )


	@staticmethod
	def instance():
		if not RoleSwapInviteState._instance:
			RoleSwapInviteState._instance = RoleSwapInviteState()
		return RoleSwapInviteState._instance


	def enter( self, srcEntity, dstEntity ):
		"""
		�����״̬���ڴ˺�������һЩ��ʼ��
		"""
		srcEntity.si_targetID = dstEntity.id
		swapUID = Function.newUID()
		srcEntity.setTemp( "si_UID", swapUID )
		srcEntity.setTemp( "si_targetNameAndID", dstEntity.getNameAndID())
		dstEntity.si_receiveUID( swapUID, srcEntity.getNameAndID())


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	����״̬�ı�
		@type	state		:	UINT8
		@param	state		:	�ı��״̬
		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı�״̬��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		"""
		if state == csdefine.TRADE_SWAP_BEING:
			return True

		if state == csdefine.TRADE_SWAP_INVITE:		# ������״̬�����Ա�����׶���
			return True

		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True

		return False


	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		�����׶���״̬�ı�ʱ�յ�֪ͨ��ֻ��Ӱ�켺���ĶԷ�״̬����
		"""
		if dstState == csdefine.TRADE_SWAP_BEING:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )
			return
		if dstState == csdefine.TRADE_SWAP_DEFAULT:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return


	def onDstItemChanged( self, srcEntity, dstEntity, swapOrder, itemInstance ):
		"""
		"""
		pass


	def onDstItemRemoved( self, srcEntity, dstEntity, swapOrder ):
		"""
		"""
		pass


	def onDstMoneyChanged( self, srcEntity, dstEntity, amount ):
		"""
		"""
		pass


	def onDstPetChanged( self, srcEntity, dstEntity, petDBID ):
		"""
		"""
		pass


	def onDstPetRemoved( self, srcEntity, dstEntity ):
		"""
		"""
		pass


	def changeItem( self, srcEntity, dstEntity, swapOrder, kitOrder, uid, itemInstance ):
		"""
		virtual method
		������Ʒ�����ӵ���״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapInviteState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )

	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		������Ʒ���Ƴ�����״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapInviteState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )

	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		��Ǯ�����ı�
		��״̬�²���
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapInviteState can't allow to changeMoney" % ( srcEntity.id, dstEntity.id ) )

	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		virtual method
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to changePet" % ( srcEntity.id, dstEntity.id ) )


	def removePet( self, srcEntity, dstEntity ):
		"""
		virtual method
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to removePet" % ( srcEntity.id, dstEntity.id ) )


class RoleSwapWaitState( RoleSwapState ):
	"""
	�ȴ�����״̬��
	csdefine.TRADE_SWAP_WAITING
	"""
	_instance = None
	def __init__( self ):
		assert RoleSwapWaitState._instance is None
		RoleSwapState.__init__( self )


	def enter( self, srcEntity, dstEntity ):
		"""
		�ڵȴ�״̬��ֻ���ý��׶���
		"""
		srcEntity.si_targetID = dstEntity.id


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	����״̬�ı�
		@type	state		:	UINT8
		@param	state		:	�ı��״̬
		@type	srcEntity	:	entity
		@param	srcEntity	:	MAILBOX
		"""
		if state == csdefine.TRADE_SWAP_BEING:
			return True

		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True


	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		�����׶���״̬�ı�ʱ�յ�֪ͨ��ֻ��Ӱ�켺���ĶԷ�״̬����
		"""
		if dstState == csdefine.TRADE_SWAP_DEFAULT:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return


	def onDstItemChanged( self, srcEntity, dstEntity, swapOrder, itemInstance ):
		"""
		"""
		pass


	def onDstItemRemoved( self, srcEntity, dstEntity, swapOrder ):
		"""
		"""
		pass


	def onDstMoneyChanged( self, srcEntity, dstEntity, amount ):
		"""
		"""
		pass


	def onDstPetChanged( self, srcEntity, dstEntity, petDBID ):
		"""
		"""
		pass

	def onDstPetRemoved( self, srcEntity, dstEntity ):
		"""
		"""
		pass


	def changeItem( self, srcEntity, dstEntity, swapOrder, kitOrder, uid, itemInstance ):
		"""
		virtual method
		������Ʒ�����ӵ���״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapWaitState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		������Ʒ���Ƴ�����״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapWaitState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		��Ǯ�����ı�
		��״̬�²���
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapWaitState can't allow to changeMoney" % ( srcEntity.id, dstEntity.id ) )


	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		virtual method
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to changePet" % ( srcEntity.id, dstEntity.id ) )


	def removePet( self, srcEntity, dstEntity ):
		"""
		virtual method
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to removePet" % ( srcEntity.id, dstEntity.id ) )


	@staticmethod
	def instance():
		if RoleSwapWaitState._instance is None:
			RoleSwapWaitState._instance = RoleSwapWaitState()
		return RoleSwapWaitState._instance


class RoleSwapBeingState( RoleSwapState ):
	"""
	��Ʒ���׽�����״̬��
	csdefine.TRADE_SWAP_BEING
	"""
	_instance = None
	def __init__( self ):
		assert RoleSwapBeingState._instance is None
		RoleSwapState.__init__( self )


	def enter( self, srcEntity, dstEntity ):
		"""
		"""
		pass


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	����״̬�ı�
		@type	state		:	UINT8
		@param	state		:	�ı��״̬
		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı�״̬��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		"""
		# ����״̬
		if state == csdefine.TRADE_SWAP_LOCK:					# �����״̬��Ӱ��Է�
			return True

		#if state == csdefine.TRADE_SWAP_PET_BEING:				# ��Ʒ����ת�������ｻ��pet
		#	srcEntity.base.si_setTargetID( dstEntity.id )		# ����BASE�Ľ��׶���
		#	srcEntity.si_clearSwapData()						# �����Ʒ���ݣ�ֻ��������ط���֪���Ƿ�Ҫ���
		#	return True

		if state == csdefine.TRADE_SWAP_DEFAULT:				# �뿪����
			return True

		return False


	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		�����׶���״̬�ı�ʱ�յ�֪ͨ��ֻ��Ӱ�켺���ĶԷ�״̬����
		"""
		if dstState == csdefine.TRADE_SWAP_DEFAULT:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return

		#if dstState == csdefine.TRADE_SWAP_PET_BEING:
		#	srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )
		#	return

	def onDstItemChanged( self, srcEntity, dstEntity, swapOrder, itemInstance ):
		"""
		"""
		#DEBUG_MSG( "%s si_dstItem has change--->" % srcEntity.getName() )
		srcEntity.si_dstItem[ swapOrder ] = itemInstance
		srcEntity.client.si_dstChangeItem( swapOrder, itemInstance )
		srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )


	def onDstItemRemoved( self, srcEntity, dstEntity, swapOrder ):
		"""
		"""
		del srcEntity.si_dstItem[ swapOrder ]
		srcEntity.client.si_removeSwapItem( 1, swapOrder )
		srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )


	def onDstMoneyChanged( self, srcEntity, dstEntity, amount ):
		"""
		"""
		if srcEntity.si_dstMoney == amount: return
		#DEBUG_MSG( "%i si_dstMoney has Change  %i-------->%i" % ( srcEntity.id, srcEntity.si_dstMoney, amount ) )
		srcEntity.si_dstMoney = amount
		srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )


	def onDstPetChanged( self, srcEntity, dstEntity, petDBID ):
		"""
		"""
		pass


	def onDstPetRemoved( self, srcEntity, dstEntity ):
		"""
		"""
		pass


	def changeItem( self, srcEntity, dstEntity, swapOrder, kitOrder, uid, itemInstance ):
		"""
		virtual method
		@summary				:	������Ʒ�ĸı䵼��״̬�ĸı�
		@type	srcEntity		:	entity
		@param	srcEntity		:	�����ı�״̬��entity
		@type	dstEntity		:	entity
		@param	dstEntity		:	��Ӱ���entity
		@type	swapOrder		:	UINT8
		@param	swapOrder		:	�ڽ������иı��λ��
		@type	kitOrder		:	UINT8
		@param	kitOrder		:	��������
		@type	uid				:	INT64
		@param	uid				:	������Ʒ����
		@type	itemInstance	:	instance
		@param	itemInstance	:	��Ʒʵ��
		"""
		srcEntity.si_changeMyItem( swapOrder, kitOrder, uid, itemInstance )
		srcEntity.client.si_meChangeItem( swapOrder, kitOrder, uid )
		dstEntity.si_dstChangeItem( swapOrder, itemInstance.copy(), srcEntity.id )	# ֪ͨ�Է�������Ʒ�ı�


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		@summary			:	������Ʒ���Ƴ�����״̬�ĸı�
		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı�״̬��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		@type	swapOrder	:	UINT8
		@param	swapOrder	:	�ڽ������иı��λ��
		"""
		srcEntity.si_removeMyItem( swapOrder, dstEntity )
		dstEntity.si_removeDstItem( swapOrder, srcEntity.id )
		srcEntity.client.si_removeSwapItem( 0, swapOrder )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		@summary			:	��Ǯ�����ı�
		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı�״̬��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		@type	amount		:	UINT32
		@param	amount		:	��Ǯ����
		"""
		#��Ǯ�����ı�ʱ���Է����ص�������״̬
		#֪ͨ�Է�˵�Լ��Ľ�Ǯ�ı���
		srcEntity.si_changeMyMoney( amount, dstEntity )
		dstEntity.si_dstChangeMoney( amount, srcEntity.id )


	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		virtual method
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this state can't allow to changePet" % ( srcEntity.id, dstEntity.id ) )


	def removePet( self, srcEntity, dstEntity ):
		"""
		virtual method
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this state can't allow to removePet" % ( srcEntity.id, dstEntity.id ) )


	@staticmethod
	def instance():
		if RoleSwapBeingState._instance is None:
			RoleSwapBeingState._instance = RoleSwapBeingState()
		return RoleSwapBeingState._instance


class RoleSwapLockState( RoleSwapState ):
	"""
	��Ʒ��������״̬��
	csdefine.TRADE_SWAP_SURE
	"""
	_instance = None
	def __init__( self ):
		assert RoleSwapLockState._instance is None
		RoleSwapState.__init__( self )


	def enter( self, srcEntity, dstEntity ):
		"""
		"""
		pass


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		״̬�ı�
		@summary			:	����״̬�ı�
		@type	state		:	UINT8
		@param	state		:	�ı��״̬
		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı�״̬��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		"""
		if state == csdefine.TRADE_SWAP_SURE:
			if dstEntity.si_myState < csdefine.TRADE_SWAP_LOCK:
				return False
			state = srcEntity.si_checkItemTrading( dstEntity )
			if state == csstatus.ROLE_TRADE_ALLOW_TRADE:
				return True
			else:
				srcEntity.statusMessage( state )
				dstEntity.statusMessage( state )
				srcEntity.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# �뿪����
				return False
			return True

		if state == csdefine.TRADE_SWAP_BEING:					# �����ȡ������
			return True

		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True

		#if state == csdefine.TRADE_SWAP_PET_BEING:				# ��Ʒ����ת�������ｻ��pet
		#	srcEntity.base.si_setTargetID( dstEntity.id )		# ����BASE�Ľ��׶���
		#	srcEntity.si_clearSwapData()						# �����Ʒ���ݣ�ֻ��������ط���֪���Ƿ�Ҫ���
		#	return True

		return False


	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		�����׶���״̬�ı�ʱ�յ�֪ͨ��ֻ��Ӱ�켺���ĶԷ�״̬����
		"""
		if dstState == csdefine.TRADE_SWAP_DEFAULT:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return
		if dstState == csdefine.TRADE_SWAP_BEING:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )
			return

		#if dstState == csdefine.TRADE_SWAP_PET_BEING:
		#	srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )
		#	return

	def onDstItemChanged( self, srcEntity, dstEntity, swapOrder, itemInstance ):
		"""
		"""
		srcEntity.si_dstItem[ swapOrder ] = itemInstance
		srcEntity.client.si_dstChangeItem( swapOrder, itemInstance )
		srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )


	def onDstItemRemoved( self, srcEntity, dstEntity, swapOrder ):
		"""
		"""
		del srcEntity.si_dstItem[ swapOrder ]
		srcEntity.client.si_removeSwapItem( 1, swapOrder )
		srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )


	def onDstMoneyChanged( self, srcEntity, dstEntity, amount ):
		"""
		"""
		if srcEntity.si_dstMoney == amount: return
		srcEntity.si_dstMoney = amount
		srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )


	def onDstPetChanged( self, srcEntity, dstEntity, petDBID ):
		"""
		"""
		pass


	def onDstPetRemoved( self, srcEntity, dstEntity ):
		"""
		"""
		pass


	def changeItem( self, srcEntity, dstEntity, swapOrder, kitOrder, uid, itemInstance ):
		"""
		virtual method
		@summary			:	������Ʒ�ĸı䵼��״̬�ĸı�
		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı�״̬��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		@type	swapOrder	:	UINT8
		@param	swapOrder	:	�ڽ������иı��λ��
		@type	kitOrder	:	UINT8
		@param	kitOrder	:	��������
		@type	uid			:	INT64
		@param	uid			:	������Ʒ����
		@type	itemInstance:	instance
		@param	itemInstance:	��Ʒʵ��
		"""
		#�����״̬�£������ҶԽ�����Ʒ������
		#����ת��״̬�� csdefine.TRADE_SWAP_BEING(���ڽ���״̬)
		#ֻҪ��һ������Ʒ�б䶯����ô˫�����ص����׽�����״̬
		srcEntity.si_changeMyItem( swapOrder, kitOrder, uid, itemInstance )
		srcEntity.client.si_meChangeItem( swapOrder, kitOrder, uid )
		srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )
		dstEntity.si_dstChangeItem( swapOrder, itemInstance.copy(), srcEntity.id )	# ֪ͨ�Է�������Ʒ�ı�


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		@summary			:	������Ʒ���Ƴ�����״̬�ĸı�
		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı�״̬��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		@type	swapOrder	:	UINT8
		@param	swapOrder	:	�ڽ������иı��λ��
		"""
		# �����״̬�£������ҶԽ�����Ʒ���Ƴ�
		# ����ת��״̬�� csdefine.TRADE_SWAP_BEING(���ڽ���״̬)
		# ֻҪ��һ������Ʒ�б䶯����ô˫�����ص����׽�����״̬
		srcEntity.si_removeMyItem( swapOrder, dstEntity )
		dstEntity.si_removeDstItem( swapOrder, srcEntity.id )
		srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )
		srcEntity.client.si_removeSwapItem( 0, swapOrder )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		@summary			:	��Ǯ�����ı�
		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı�״̬��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		@type	amount		:	UINT32
		@param	amount		:	��Ǯ����
		"""
		#��Ǯ�����ı�ʱ��˫�����ص�������״̬
		#֪ͨ�Է�˵�Լ��Ľ�Ǯ�ı���
		srcEntity.si_changeMyMoney( amount, dstEntity )
		srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )
		dstEntity.si_dstChangeMoney( amount, srcEntity.id )


	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		virtual method
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to changePet" % ( srcEntity.id, dstEntity.id ) )


	def removePet( self, srcEntity, dstEntity ):
		"""
		virtual method
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to removePet" % ( srcEntity.id, dstEntity.id ) )


	@staticmethod
	def instance():
		if RoleSwapLockState._instance is None:
			RoleSwapLockState._instance = RoleSwapLockState()
		return RoleSwapLockState._instance


class RoleSwapSureState( RoleSwapState ):
	"""
	ȷ�Ͻ���״̬�࣬��Ʒ���׺ͳ��ｻ�׿�ͬʱ����
	csdefine.TRADE_SWAP_LOCK
	"""
	_instance = None
	def __init__( self ):
		assert RoleSwapSureState._instance is None
		RoleSwapState.__init__( self )


	def enter( self, srcEntity, dstEntity ):
		"""
		"""
		# ����Է��Ѿ�����ȷ�Ͻ���״̬����ô�ͽ���2������״̬���ڱ�cellApp��õĶԷ�״̬���ܲ�׼ȷ������2������״̬���к�������
		#if dstEntity.si_myState == csdefine.TRADE_SWAP_SURE:
		#	srcEntity.si_changeState( csdefine.TRADE_SWAP_LOCKAGAIN, dstEntity, False )
		pass


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	����״̬�ı�
		@type	state		:	UINT8
		@param	state		:	�ı��״̬
		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı�״̬��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		"""
		if state == csdefine.TRADE_SWAP_BEING:
			return True

		if state == csdefine.TRADE_SWAP_PET_BEING:
			return True

		if state == csdefine.TRADE_SWAP_DEFAULT:
			if dstEntity and dstEntity.si_myState == csdefine.TRADE_SWAP_LOCKAGAIN:	# ���˵��Է��Ѿ�ȷ�Ͻ��׵�������������ȡ���ĵ���Ϣ��
				return False
			return True

		if state == csdefine.TRADE_SWAP_LOCKAGAIN:
			return True

		return False

	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		�����׶���״̬�ı�ʱ�յ�֪ͨ��ֻ��Ӱ�켺���ĶԷ�״̬����
		"""
		if dstState == csdefine.TRADE_SWAP_DEFAULT:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return
		if dstState == csdefine.TRADE_SWAP_BEING:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )
			return
		if dstState == csdefine.TRADE_SWAP_PET_BEING:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )
			return
		if dstState == csdefine.TRADE_SWAP_SURE:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_LOCKAGAIN, dstEntity )
			return
		if dstState == csdefine.TRADE_SWAP_LOCKAGAIN:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_LOCKAGAIN, dstEntity )
			return

	def onDstItemChanged( self, srcEntity, dstEntity, swapOrder, itemInstance ):
		"""
		"""
		#DEBUG_MSG( "%s si_dstItem has change--->" % srcEntity.getName() )
		srcEntity.si_dstItem[ swapOrder ] = itemInstance
		srcEntity.client.si_dstChangeItem( swapOrder, itemInstance )
		srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )


	def onDstItemRemoved( self, srcEntity, dstEntity, swapOrder ):
		"""
		"""
		del srcEntity.si_dstItem[ swapOrder ]
		srcEntity.client.si_removeSwapItem( 1, swapOrder )
		srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )


	def onDstMoneyChanged( self, srcEntity, dstEntity, amount ):
		"""
		"""
		if srcEntity.si_dstMoney == amount: return
		#DEBUG_MSG( "%i si_dstMoney has Change  %i-------->%i" % ( srcEntity.id, srcEntity.si_dstMoney, amount ) )
		srcEntity.si_dstMoney = amount
		srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )


	def onDstPetChanged( self, srcEntity, dstEntity, petDBID ):
		"""
		"""
		pass


	def onDstPetRemoved( self, srcEntity, dstEntity ):
		"""
		"""
		pass


	def changeItem( self, srcEntity, dstEntity, swapOrder, kitOrder, uid, itemInstance ):
		"""
		virtual method
		������Ʒ�����ӵ���״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapSureState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		������Ʒ���Ƴ�����״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapSureState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		��Ǯ�����ı�
		��״̬�²���
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapSureState can't allow to changeMoney" % ( srcEntity.id, dstEntity.id ) )


	@staticmethod
	def instance():
		if RoleSwapSureState._instance is None:
			RoleSwapSureState._instance = RoleSwapSureState()
		return RoleSwapSureState._instance


	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		virtual method
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to changePet" % ( srcEntity.id, dstEntity.id ) )


	def removePet( self, srcEntity, dstEntity ):
		"""
		virtual method
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to removePet" % ( srcEntity.id, dstEntity.id ) )


class RoleSwapLockAgainState( RoleSwapState ):
	"""
	�ٴ���������״̬�࣬�ٴ������Ƿ�������Ϊ
	csdefine.TRADE_SWAP_LOCKAGAIN

	���첽�����ʵ��2����ҵİ�ȫ���ף���ֹ��Ʒ���ƣ�ǰ���Ƿ���������ͻȻ��������
	��2����Ҷ�����csdefine.TRADE_SWAP_SURE״̬��˫�����붼�����״̬���ܽ��н�����Ʒ��Ǯ���ݵĲ�����

	���磬����ȷ�Ͻ��ף��ڻ�öԷ�����ȷ�Ͻ��׵�����£������ٴ�����״̬����֪ͨ�Է������ٴ�����״̬��
	�Է����յ�����Ҫ�����2�ν��׵���Ϣʱ������2�ν���״̬�������н������ݵĲ���ͬʱ֪ͨ����Ҳ���н������ݵĲ�����
	����Է����յ�����Ҫ�����2�ν��׵���Ϣʱ�Ѿ�����ȷ�Ͻ���״̬����ô֪ͨ�����뿪���ס�

	"""
	_instance = None
	def __init__( self ):
		assert RoleSwapLockAgainState._instance is None
		RoleSwapState.__init__( self )


	def enter( self, srcEntity, dstEntity ):
		"""
		"""
		state = srcEntity.si_checkItemTrading( dstEntity )
		if state != csstatus.ROLE_TRADE_ALLOW_TRADE:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# �뿪����
			srcEntity.statusMessage( state )
			dstEntity.client.onStatusMessage( state, "" )
			return
		state = srcEntity.si_checkPetTrading( dstEntity )
		if state != csstatus.ROLE_TRADE_ALLOW_TRADE:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# �뿪����
			srcEntity.statusMessage( state )
			dstEntity.client.onStatusMessage( state, "" )
			return
		# ����Է��Ѿ�����TRADE_SWAP_LOCKAGAIN״̬����ô�Է��Ͳ��ܹ��ı���Ʒ�ˣ���Ȼ�Է��п������٣����ǻ���cell����ʱ��һ���ӳ٣��Ա㴦���������첽���
		if dstEntity.si_myState == csdefine.TRADE_SWAP_LOCKAGAIN:
			srcEntity.si_trading()
			dstEntity.si_trading()

			srcEntity.statusMessage( csstatus.ROLE_TRADE_SUCCESS )
			dstEntity.statusMessage( csstatus.ROLE_TRADE_SUCCESS )

	def changeState( self, state, srcEntity, dstEntity ):	# wsfwsf
		"""
		virtual method
		@summary			:	����״̬�ı�
		@type	state		:	UINT8
		@param	state		:	�ı��״̬
		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı�״̬��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		"""
		# �����Ҵ���TRADE_SWAP_LOCKAGAIN״̬��������ͻ���expoed�����ı�״̬
		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True

	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		�����׶���״̬�ı�ʱ�յ�֪ͨ��ֻ��Ӱ�켺���ĶԷ�״̬����
		"""
		pass

	def onDstItemChanged( self, srcEntity, dstEntity, swapOrder, itemInstance ):
		"""
		"""
		pass

	def onDstItemRemoved( self, srcEntity, dstEntity, swapOrder ):
		"""
		"""
		pass


	def onDstMoneyChanged( self, srcEntity, dstEntity, amount ):
		"""
		"""
		pass


	def onDstPetChanged( self, srcEntity, dstEntity, petDBID ):
		"""
		"""
		pass


	def onDstPetRemoved( self, srcEntity, dstEntity ):
		"""
		"""
		pass


	def changeItem( self, srcEntity, dstEntity, swapOrder, kitOrder, uid, itemInstance ):
		"""
		virtual method
		������Ʒ�����ӵ���״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapLockAgainState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		������Ʒ���Ƴ�����״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapLockAgainState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		��Ǯ�����ı�
		��״̬�²���
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapLockAgainState can't allow to changeMoney" % ( srcEntity.id, dstEntity.id ) )


	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		virtual method
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to changePet" % ( srcEntity.id, dstEntity.id ) )


	def removePet( self, srcEntity, dstEntity ):
		"""
		virtual method
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to removePet" % ( srcEntity.id, dstEntity.id ) )


	@staticmethod
	def instance():
		if RoleSwapLockAgainState._instance is None:
			RoleSwapLockAgainState._instance = RoleSwapLockAgainState()
		return RoleSwapLockAgainState._instance

class RoleSwapPetInviteState( RoleSwapState ):
	"""
	������״̬
	csdefine.TRADE_SWAP_INVITE
	"""
	_instance = None

	def __init__( self ):
		"""
		"""
		assert RoleSwapPetInviteState._instance is None
		RoleSwapState.__init__( self )


	@staticmethod
	def instance():
		if not RoleSwapPetInviteState._instance:
			RoleSwapPetInviteState._instance = RoleSwapPetInviteState()
		return RoleSwapPetInviteState._instance


	def enter( self, srcEntity, dstEntity ):
		"""
		�����״̬���ڴ˺�������һЩ��ʼ��
		"""
		srcEntity.si_targetID = dstEntity.id
		swapUID = Function.newUID()
		srcEntity.setTemp( "si_UID", swapUID )
		srcEntity.setTemp( "si_targetNameAndID", dstEntity.getNameAndID())
		dstEntity.si_receiveUID( swapUID, srcEntity.getNameAndID())
		srcEntity.base.si_setTargetID( dstEntity.id )


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	����״̬�ı�
		@type	state		:	UINT8
		@param	state		:	�ı��״̬
		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı�״̬��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		"""
		if state == csdefine.TRADE_SWAP_PET_INVITE:		# ������״̬�����Ա�����׶���
			return True

		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True

		if state == csdefine.TRADE_SWAP_PET_BEING:
			return True

		return False


	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		�����׶���״̬�ı�ʱ�յ�֪ͨ��ֻ��Ӱ�켺���ĶԷ�״̬����
		"""
		if dstState == csdefine.TRADE_SWAP_PET_BEING:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )
			return
		if dstState == csdefine.TRADE_SWAP_DEFAULT:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return


	def onDstItemChanged( self, srcEntity, dstEntity, swapOrder, itemInstance ):
		"""
		"""
		pass


	def onDstItemRemoved( self, srcEntity, dstEntity, swapOrder ):
		"""
		"""
		pass


	def onDstMoneyChanged( self, srcEntity, dstEntity, amount ):
		"""
		"""
		pass


	def onDstPetChanged( self, srcEntity, dstEntity, petDBID ):
		"""
		"""
		pass


	def onDstPetRemoved( self, srcEntity, dstEntity ):
		"""
		"""
		pass


	def changeItem( self, srcEntity, dstEntity, swapOrder, kitOrder, uid, itemInstance ):
		"""
		virtual method
		������Ʒ�����ӵ���״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapPetInviteState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		������Ʒ���Ƴ�����״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapPetInviteState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		��Ǯ�����ı�
		��״̬�²���
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapPetInviteState can't allow to changeMoney" % ( srcEntity.id, dstEntity.id ) )


	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		virtual method
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to changePet" % ( srcEntity.id, dstEntity.id ) )


	def removePet( self, srcEntity, dstEntity ):
		"""
		virtual method
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to removePet" % ( srcEntity.id, dstEntity.id ) )


class RoleSwapPetWaitState( RoleSwapState ):
	"""
	�ȴ�����״̬��
	csdefine.TRADE_SWAP_WAITING
	"""
	_instance = None
	def __init__( self ):
		assert RoleSwapPetWaitState._instance is None
		RoleSwapState.__init__( self )


	def enter( self, srcEntity, dstEntity ):
		"""
		�ڵȴ�״̬��ֻ���ý��׶���
		"""
		srcEntity.si_targetID = dstEntity.id
		srcEntity.base.si_setTargetID( dstEntity.id )


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	����״̬�ı�
		@type	state		:	UINT8
		@param	state		:	�ı��״̬
		@type	srcEntity	:	entity
		@param	srcEntity	:	MAILBOX
		"""
		if state == csdefine.TRADE_SWAP_PET_BEING:
			return True

		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True


	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		�����׶���״̬�ı�ʱ�յ�֪ͨ��ֻ��Ӱ�켺���ĶԷ�״̬����
		"""
		if dstState == csdefine.TRADE_SWAP_DEFAULT:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return


	def onDstItemChanged( self, srcEntity, dstEntity, swapOrder, itemInstance ):
		"""
		"""
		pass


	def onDstItemRemoved( self, srcEntity, dstEntity, swapOrder ):
		"""
		"""
		pass


	def onDstMoneyChanged( self, srcEntity, dstEntity, amount ):
		"""
		"""
		pass


	def onDstPetChanged( self, srcEntity, dstEntity, petDBID ):
		"""
		"""
		pass

	def onDstPetRemoved( self, srcEntity, dstEntity ):
		"""
		"""
		pass


	def changeItem( self, srcEntity, dstEntity, swapOrder, kitOrder, uid, itemInstance ):
		"""
		virtual method
		������Ʒ�����ӵ���״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapPetWaitState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		������Ʒ���Ƴ�����״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapPetWaitState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		��Ǯ�����ı�
		��״̬�²���
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapPetWaitState can't allow to changeMoney" % ( srcEntity.id, dstEntity.id ) )


	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		virtual method
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to changePet" % ( srcEntity.id, dstEntity.id ) )


	def removePet( self, srcEntity, dstEntity ):
		"""
		virtual method
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to removePet" % ( srcEntity.id, dstEntity.id ) )


	@staticmethod
	def instance():
		if RoleSwapPetWaitState._instance is None:
			RoleSwapPetWaitState._instance = RoleSwapPetWaitState()
		return RoleSwapPetWaitState._instance

class RoleSwapPetBeingState( RoleSwapState ):
	"""
	���ｻ�׽���״̬
	"""
	_instance = None
	def __init__( self ):
		assert RoleSwapPetBeingState._instance is None
		RoleSwapState.__init__( self )


	def enter( self, srcEntity, dstEntity ):
		"""
		"""
		pass


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	����״̬�ı�
		@type	state		:	UINT8
		@param	state		:	�ı��״̬
		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı�״̬��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		@type	flag	:	BOOL
		@param	flag	:	TrueΪ�����������������������ģ�FalseΪ��Ҹ���������������
		"""
		if state == csdefine.TRADE_SWAP_PET_LOCK:		# תΪ����״̬
			return True

		#if state == csdefine.TRADE_SWAP_BEING:			# תΪ��Ʒ����״̬
		#	srcEntity.si_clearSwapPet()
		#	srcEntity.base.si_setTargetID( 0 )			# ���base����
		#	return True

		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True

		return False


	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		�����׶���״̬�ı�ʱ�յ�֪ͨ��ֻ��Ӱ�켺���ĶԷ�״̬����
		"""
		if dstState == csdefine.TRADE_SWAP_DEFAULT:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return

		#if dstState == csdefine.TRADE_SWAP_BEING:
		#	srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )
		#	return

	def onDstItemChanged( self, srcEntity, dstEntity, swapOrder, itemInstance ):
		"""
		"""
		pass


	def onDstItemRemoved( self, srcEntity, dstEntity, swapOrder ):
		"""
		"""
		pass


	def onDstMoneyChanged( self, srcEntity, dstEntity, amount ):
		"""
		"""
		if srcEntity.si_dstMoney == amount: return
		#DEBUG_MSG( "%i si_dstMoney has Change  %i-------->%i" % ( srcEntity.id, srcEntity.si_dstMoney, amount ) )
		srcEntity.si_dstMoney = amount
		srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )


	def onDstPetChanged( self, srcEntity, dstEntity, petDBID ):
		"""
		"""
		srcEntity.si_dstPetDBID = petDBID
		srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )


	def onDstPetRemoved( self, srcEntity, dstEntity ):
		"""
		"""
		srcEntity.si_dstPetDBID = 0
		srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )


	def changeItem( self, srcEntity, dstEntity, swapOrder, kitOrder, uid, itemInstance ):
		"""
		virtual method
		������Ʒ�����ӵ���״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapLockAgainState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		������Ʒ���Ƴ�����״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapLockAgainState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		��Ǯ�����ı�
		"""
		srcEntity.si_changeMyMoney( amount, dstEntity )
		dstEntity.si_dstChangeMoney( amount, srcEntity.id )


	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		virtual method
		"""
		srcEntity.si_changeMyPet( petDBID )
		srcEntity.base.si_changeMyPet( petDBID, dstEntity.base )	# ֪ͨbase���ͳ�������
		dstEntity.si_dstChangePet( petDBID, srcEntity.id )			# ֪ͨ�Է����׳���ı�


	def removePet( self, srcEntity, dstEntity ):
		"""
		virtual method
		"""
		srcEntity.si_removeMyPet()
		srcEntity.base.si_removeMyPet( dstEntity.base )				# ֪ͨbase�Ƴ���������
		dstEntity.si_dstRemovePet( srcEntity.id )					# ֪ͨ�Է��Ƴ����׳���


	@staticmethod
	def instance():
		if RoleSwapPetBeingState._instance is None:
			RoleSwapPetBeingState._instance = RoleSwapPetBeingState()
		return RoleSwapPetBeingState._instance


class RoleSwapPetLockState( RoleSwapState ):
	"""
	���ｻ������״̬
	"""
	_instance = None
	def __init__( self ):
		assert RoleSwapPetLockState._instance is None
		RoleSwapState.__init__( self )


	def enter( self, srcEntity, dstEntity ):
		"""
		"""
		pass


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	����״̬�ı�
		@type	state		:	UINT8
		@param	state		:	�ı��״̬
		@type	srcEntity	:	entity
		@param	srcEntity	:	�����ı�״̬��entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	��Ӱ���entity
		@type	flag	:	BOOL
		@param	flag	:	TrueΪ�����������������������ģ�FalseΪ��Ҹ���������������
		"""
		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True

		if state == csdefine.TRADE_SWAP_PET_BEING:			# �ڱ�״̬�¸ı������Ǯ,ת�䵽���ڽ���״̬
			return True

		if state == csdefine.TRADE_SWAP_SURE:				# ת�䵽ȷ��״̬
			if dstEntity.si_myState < csdefine.TRADE_SWAP_PET_LOCK:					# �Է���û������������ȷ�Ͻ���
				return False
			state = srcEntity.si_checkPetTrading( dstEntity )
			if state == csstatus.ROLE_TRADE_ALLOW_TRADE:
				return True
			elif state == csstatus.ROLE_TRADE_MONEY_OVERFLOW:
				srcEntity.statusMessage( state )
				return False
			elif state == csstatus.ROLE_TRADE_FAILED_MONEY_CHANGED:
				srcEntity.statusMessage( state )
				return False
			elif state == csstatus.ROLE_PET_AMOUNT_OVERFLOW:
				srcEntity.statusMessage( state )
				dstEntity.statusMessage( csstatus.ROLE_TARGET_PET_AMOUNT_OVERFLOW )
				return False
			elif state == csstatus.ROLE_PET_TAKE_LEVEL_INVALID:
				srcEntity.statusMessage( state )
				dstEntity.statusMessage( csstatus.ROLE_TARGET_LEVEL_INVALID )
				return False
		return False


	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		�����׶���״̬�ı�ʱ�յ�֪ͨ��ֻ��Ӱ�켺���ĶԷ�״̬����
		"""
		if dstState == csdefine.TRADE_SWAP_DEFAULT:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return
		#if dstState == csdefine.TRADE_SWAP_BEING:
		#	srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )
		#	return
		if dstState == csdefine.TRADE_SWAP_PET_BEING:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )
			return


	def onDstItemChanged( self, srcEntity, dstEntity, swapOrder, itemInstance ):
		"""
		"""
		pass


	def onDstItemRemoved( self, srcEntity, dstEntity, swapOrder ):
		"""
		"""
		pass


	def onDstMoneyChanged( self, srcEntity, dstEntity, amount ):
		"""
		"""
		if srcEntity.si_dstMoney == amount: return
		#DEBUG_MSG( "%i si_dstMoney has Change  %i-------->%i" % ( srcEntity.id, srcEntity.si_dstMoney, amount ) )
		srcEntity.si_dstMoney = amount
		srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )


	def onDstPetChanged( self, srcEntity, dstEntity, petDBID ):
		"""
		"""
		srcEntity.si_dstPetDBID = petDBID
		srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )


	def onDstPetRemoved( self, srcEntity, dstEntity ):
		"""
		"""
		srcEntity.si_dstPetDBID = 0
		srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )


	def changeItem( self, srcEntity, dstEntity, swapOrder, kitOrder, uid, itemInstance ):
		"""
		virtual method
		������Ʒ�����ӵ���״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapLockAgainState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		������Ʒ���Ƴ�����״̬�ĸı�
		��״̬�²���
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapLockAgainState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		��Ǯ�����ı�
		��״̬�²���
		"""
		srcEntity.si_changeMyMoney( amount, dstEntity )
		srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )
		dstEntity.si_dstChangeMoney( amount, srcEntity.id )


	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		virtual method
		"""
		srcEntity.si_changeMyPet( petDBID )
		srcEntity.base.si_changeMyPet( petDBID, dstEntity.base )	# ֪ͨbase���ͳ�������
		srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )
		dstEntity.si_dstChangePet( petDBID, srcEntity.id )


	def removePet( self, srcEntity, dstEntity ):
		"""
		virtual method
		"""
		srcEntity.si_removeMyPet()
		srcEntity.base.si_removeMyPet( dstEntity.base )				# ֪ͨbase�Ƴ���������
		srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )
		dstEntity.si_dstRemovePet( srcEntity.id )


	@staticmethod
	def instance():
		if RoleSwapPetLockState._instance is None:
			RoleSwapPetLockState._instance = RoleSwapPetLockState()
		return RoleSwapPetLockState._instance


TRADE_SWAP_STATE_MAP = {
csdefine.TRADE_SWAP_DEFAULT				:	RoleSwapDefaultState.instance(),
csdefine.TRADE_SWAP_INVITE				:	RoleSwapInviteState.instance(),
csdefine.TRADE_SWAP_WAITING				:	RoleSwapWaitState.instance(),
csdefine.TRADE_SWAP_BEING				:	RoleSwapBeingState.instance(),
csdefine.TRADE_SWAP_LOCK				:	RoleSwapLockState.instance(),
csdefine.TRADE_SWAP_SURE				:	RoleSwapSureState.instance(),
csdefine.TRADE_SWAP_LOCKAGAIN			:	RoleSwapLockAgainState.instance(),
csdefine.TRADE_SWAP_PET_INVITE			:	RoleSwapPetInviteState.instance(),
csdefine.TRADE_SWAP_PET_WAITING			:	RoleSwapPetWaitState.instance(),
csdefine.TRADE_SWAP_PET_BEING			:	RoleSwapPetBeingState.instance(),
csdefine.TRADE_SWAP_PET_LOCK			:	RoleSwapPetLockState.instance(),
}


class RoleSwapItem:
	"""
	��Ҽ���Ʒ������ش���
	"""
	def __init__( self ):
		"""
		"""
		pass
		# self.si_myPetDBID = 0	# ���ڽ��׵ĳ���dbid

	def si_receiveUID( self, swapUID,targetNameAndID ):
		"""
		Define method.
		���ձ��ν��׵Ľ��׺ţ�Ŀǰ���׺ŵ����ý��Ǳ�ʶ���ν���

		@param swapUID : ���ν��׵�Ψһ��ʶ
		@type swapUID : INT64
		@param targetNameAndID : ���׵ĶԷ������ֺ�ID
		@type targetNameAndID : STRING
		"""
		if self.si_myState == csdefine.TRADE_SWAP_DEFAULT:
			self.setTemp( "si_UID", swapUID )
			self.setTemp( "si_targetNameAndID", targetNameAndID)


	def si_getUID( self ):
		"""
		��ñ��ν��׵�uid��
		"""
		si_UID = self.queryTemp( "si_UID", 0 )
		if si_UID == 0:
			ERROR_MSG( "player( %s )'s si_UID had lost." % ( self.getName() ) )
		return si_UID

	def si_getTargetNameAndID( self ):
		"""
		��ñ��ν��׵�uid��
		"""
		si_targetNameAndID = self.queryTemp( "si_targetNameAndID", "" )
		if si_targetNameAndID == "":
			ERROR_MSG( "player( %s )'s si_targetNameAndID had lost." % ( self.getName() ) )
		return si_targetNameAndID

	def si_requestSwapFC( self, srcEntityID, dstEntityID, flag ):
		"""
		Exposed method.
		������ dstEntityID ����.����flagȷ���ǽ��г��ｻ�׻�����Ʒ����
		@param dstEntityID: ����Ŀ��entity id
		@type  dstEntityID: OBJECT_ID
		@param flag: ���׵����ͣ���Ʒ/���� ���ף�flagΪ1��ʾ��Ʒ���ף�Ϊ0��ʾ���ｻ��
		@type  flag: UINT8
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src( %i ) calling dst( %i ) method" % ( srcEntityID, self.id ) )
			return
		if srcEntityID == dstEntityID:
			self.statusMessage( csstatus.ROLE_TRADE_CANNOT_TRADE_SELF )
			return

		try:
			dstEntity = BigWorld.entities[ dstEntityID ]
		except KeyError:
			self.statusMessage( csstatus.ROLE_TRADE_TARGET_NOT_FOUND )
			return

		if not dstEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			self.statusMessage( csstatus.ROLE_TRADE_WITH_PLAYER_ONLY )
			return

		if self.position.distTo( dstEntity.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.ROLE_TRADE_TARGET_TOO_FAR )
			return
		if dstEntity.isState( csdefine.ENTITY_STATE_PENDING ):
			return
		if dstEntity.isState( csdefine.ENTITY_STATE_QUIZ_GAME ):
			return
		if self.iskitbagsLocked():
			if flag == 1:		# ��Ʒ����ʱҪ���Ǳ�����û������
				self.statusMessage(csstatus.ROLE_TRADE_CANNOT_TRADE)
			elif flag == 0:	# �����������ܽ��г��ｻ�ף�by����
				self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_PET_TRADE, "" )
			return
		if self.actionSign( csdefine.ACTION_FORBID_TRADE ) or dstEntity.actionSign( csdefine.ACTION_FORBID_TRADE ): #�жϽ���˫���Ƿ����޷����׵ı�־
			self.statusMessage(csstatus.ROLE_TRADE_FORBID_TRADE)
			return
		if dstEntity.qieCuoState != csdefine.QIECUO_NONE:
			self.statusMessage( csstatus.TARGET_IS_QIECUO )
			return

		# ս��״̬��Ҳ���Խ��н��ס�
		#if self.getState() != csdefine.ENTITY_STATE_FREE:
		#	srcEntity.statusMessage( csstatus.ROLE_TRADE_IN_BUSY )
		#	return

		# ���뱣֤csdefine.TRADE_SWAP_INVITE��csdefine.TRADE_SWAP_PET_INVITE������False
		state = flag and csdefine.TRADE_SWAP_INVITE or csdefine.TRADE_SWAP_PET_INVITE
		self.si_changeState( state, dstEntity )


	def si_changeItemFC( self, srcEntityID, swapOrder, kitOrder, uid ):
		"""
		Exposed Method
		��ĳ��λ�øı�(����)һ��������Ʒ

		@param   swapOrder: ���������λ�ã�0Ϊ��һ��λ��
		@type    swapOrder: UINT8
		@param    kitOrder: �Լ����ϵ��ĸ�����
		@type     kitOrder: UINT8
		@param         uid: ��Ʒ���������ϵ�Ψһ��ʶ, �������ʾҪ���Լ����ϵ��ĸ���Ʒ
		@type          uid: INT64
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src( %i ) calling dst( %i ) method" % ( srcEntityID, self.id ) )
			return

		if swapOrder >= csconst.TRADE_ITEMS_UPPER_LIMIT:
			HACK_MSG( "%s( %i ): order overflow, hope lt %i, give %i" % ( self.playerName, self.id, csconst.TRADE_ITEMS_UPPER_LIMIT, swapOrder ) )
			return

		try:
			kit = self.kitbags[ kitOrder ]
		except KeyError:
			HACK_MSG( "%s(%i): no such kitbag. give order %i" % ( self.playerName, self.id, kitOrder ) )
			return

		item = self.getItemByUid_( uid )
		if item is None:
			HACK_MSG( "%s( %i ): no such item. give uid %i" % ( self.playerName, self.id, uid ) )
			return

		# �ض���Ʒ�ȼ����Ʋ��ܽ���
		if not self.canGiveItem( item.id ):
			self.statusMessage( csstatus.LEVEL_RESTRAIN_ITEM_NOT_TRADE, csconst.SPECIFIC_ITEM_GIVE_LEVEL )
			return

		if not item.canGive():
			self.statusMessage( csstatus.ROLE_TRADE_ITEM_NOT_TRADE )
			return

		if not item.canExchange():
			self.statusMessage( csstatus.ROLE_TRADE_ITEM_NOT_TRADE )
			return

		if item.isFrozen():
			INFO_MSG( "frozen item." )
			return
		item.freeze( self )

		try:
			dstEntity = BigWorld.entities[ self.si_targetID ]
		except KeyError:
			# ����Ŀ�겻���ڣ�ȡ������
			dstEntity = None
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# ע�⣬dstEntity�п�����None
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].changeItem( self, dstEntity, swapOrder, kitOrder, uid, item )


	def si_removeItemFC( self, srcEntityID, swapOrder ):
		"""
		Expose method.
		��ĳ������λ���ÿ�
		@param srcEntityID: ��¶��������Ĳ���, ������self.id�������srcEntityID
		@type  srcEntityID: OBJECT_ID
		@param   swapOrder: ���������λ�ã�0Ϊ��һ��λ��
		@type    swapOrder: UINT8
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % ( srcEntityID, self.id ) )
			return

		try:	# �൱�������
			amount, uid = self.si_myItem[ swapOrder ]
		except KeyError:
			return

		item = self.getItemByUid_( uid )
		if item is None:
			ERROR_MSG( "player( %s ) swap item( uid:%i ) is None:" % ( self.getName(), uid ) )
			# don't return
		else:
			item.unfreeze( self )

		try:
			dstEntity = BigWorld.entities[ self.si_targetID ]
		except KeyError:
			dstEntity = None
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# ע�⣬dstEntity�п�����None
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].removeItem( self, dstEntity, swapOrder )


	def si_changeMoneyFC( self, srcEntityID, amount ):
		"""
		Exposed Method
		�ı��Լ��ĳ��۽�Ǯ����
		@param srcEntityID: ��¶��������Ĳ���, ������self.id�������srcEntityID
		@type  srcEntityID: OBJECT_ID
		@param      amount: ��Ǯ����
		@type       amount: UINT32
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		# ��֤�Լ��Ľ�Ǯ�Ƿ�
		if self.money < amount or amount < 0:
			self.si_myMoney = self.si_myMoney
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return

		try:
			dstEntity = BigWorld.entities[ self.si_targetID ]
		except KeyError:
			dstEntity = None
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# ע�⣬dstEntity�п�����None
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].changeMoney( self, dstEntity, amount )


	def si_changeStateFC( self, srcEntityID, state ):
		"""
		Exposed method
		����״̬�ı䣬�������ֻ����˫�������ڽ����вŻᱻ����

		@param  state: si_myState
		@type   state: UINT8
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src( %i ) calling dst( %i ) method" % ( srcEntityID, self.id ) )
			return
		try:
			dstEntity = BigWorld.entities[ self.si_targetID ]
		except KeyError:
			dstEntity = None
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# ע�⣬dstEntity�п�����None
			return

		# �ڿͻ����ж�˫���Ƿ���10��֮��
		#if self.position.flatDistTo( dstEntity.position ) > csconst.COMMUNICATE_DISTANCE:
		#	TRADE_SWAP_STATE_MAP[ self.si_myState ].SILeaveTrade( self, dstEntity, False )
		#	self.statusMessage( csstatus.ROLE_TRADE_TARGET_TOO_FAR )
		#	return

		if state < csdefine.TRADE_SWAP_BEING or state > csdefine.TRADE_SWAP_SURE:
			ERROR_MSG( "state��������ȷ��" )
			return

		if self.iskitbagsLocked():	# ����������by����
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_PET_TRADE, "" )
			return

		self.si_changeState( state, dstEntity )


	def si_changePetFC( self, srcEntityID, petDBID ):
		"""
		Exposed method.
		�ı����ڽ��׵ĳ���

		@param petDBID:	�����dbid
		@type petDBID:	DATABASE_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % ( srcEntityID, self.id ) )
			return

		try:
			dstEntity = BigWorld.entities[ self.si_targetID ]
		except KeyError:
			dstEntity = None
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# ע�⣬dstEntity�п�����None
			return

		#if self.position.flatDistTo( dstEntity.position ) > csconst.COMMUNICATE_DISTANCE:
		#	TRADE_SWAP_STATE_MAP[ self.si_myState ].SILeaveTrade( self, dstEntity, False )
		#	self.statusMessage( csstatus.ROLE_TRADE_TARGET_TOO_FAR )
		#	return

		if not self.pcg_petDict.has_key( petDBID ):
			HACK_MSG( "����ĳ���databaseID��" )
			return

		if self.pcg_isActPet( petDBID ):
			return

		if self.pcg_isPetBinded( petDBID ):
			self.statusMessage( csstatus.PET_HAD_BEEN_BIND )
			return
		if self.pcg_isConjuring( petDBID ):	# ���ѡ�����ڳ����ĳ����ô�˳�����
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return

		if self.ptf_procreating( petDBID ):
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].changePet( self, dstEntity, petDBID )


	def si_removePetFC( self, srcEntityID ):
		"""
		Exposed method.
		�Ƴ����ڽ��׵ĳ���
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % ( srcEntityID, self.id ) )
			return

		try:
			dstEntity = BigWorld.entities[ self.si_targetID ]
		except KeyError:
			dstEntity = None
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# ע�⣬dstEntity�п�����None
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].removePet( self, dstEntity )


	def si_changeState( self, state, dstEntity ):
		"""
		ͳһ״̬���ı�ӿڣ��κ�״̬�ĸı䶼Ӧ�õ��ô˽ӿ�ͳһ����
		��״̬�ı�ӿڲ����κ�ֱ�ӵĺϷ��Լ�飬ȫ�����ɵ�ǰ��״̬������
		"""
		if TRADE_SWAP_STATE_MAP[ self.si_myState ].changeState( state, self, dstEntity ):
			self.si_myState = state
			TRADE_SWAP_STATE_MAP[ self.si_myState ].enter( self, dstEntity )
			if dstEntity is None:	# ����Է��Ѿ������ˣ�����Ҫ֪ͨ�Է�����ʱ����Ӧ���뿪���ף�
				return
			dstEntity.si_onDstStateChanged( self.si_myState, self.id )	# ����״̬�仯����֪ͨ


	def si_onDstStateChanged( self, dstState, dstEntityID ):
		"""
		Define method.
		�Է��ı䵽dstState״̬��֪ͨ������
		�жϽ��׶����Ƿ���ȷ��Ȼ��֪ͨ״̬������״̬���о����Ƿ���ġ�

		param dstState: �Է��Ľ���״̬
		type dstState: UINT8
		param dstEntityID: �Է���entity id
		type dstEntityID: OBJECT_ID
		"""
		# ��һ������������Է���csdefine.TRADE_SWAP_LOCKAGAIN״̬����������csdefine.TRADE_SWAP_DEFAULT״̬����ô֪ͨ�Է��뿪����
		# ��������������Ϊ���Է����������Ѿ����˽��װ�ť����£��Է�������ף��Է�������csdefine.TRADE_SWAP_LOCKAGAIN״̬��֪ͨ��������ͬ����״̬
		# ����������ʱ��������ȡ��������Ϣ���ڷ�����Ҫ�󼺷�����csdefine.TRADE_SWAP_LOCKAGAIN״̬����Ϣ�����ʱ����֪ͨ�Է�ȡ�����׶������TRADE_SWAP_LOCKAGAIN��
		if dstState == csdefine.TRADE_SWAP_LOCKAGAIN and self.si_myState == csdefine.TRADE_SWAP_DEFAULT:
			dstEntity = BigWorld.entities.get( dstEntityID )
			if dstEntity:
				dstState = csdefine.TRADE_SWAP_DEFAULT
				dstEntity.si_onDstStateChanged( dstState, self.id )
			return

		dstEntity = BigWorld.entities.get( dstEntityID )
		if dstEntityID != self.si_targetID and self.si_myState != csdefine.TRADE_SWAP_DEFAULT:	# ���˵���������default״̬û��si_targetID�����
			if dstState == csdefine.TRADE_SWAP_INVITE:
				if dstEntity is not None:
					dstEntity.statusMessage( csstatus.ROLE_TRADE_TARGET_IN_BUSY )				# ���ڷ�æ״̬
			dstEntity.si_onDstStateChanged( csdefine.TRADE_SWAP_DEFAULT, self.id )				# ֪ͨ�Է��뿪����
			return

		if dstEntity is None:																	# �Ҳ����Է����뿪����
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].onDstStateChanged( self, dstEntity, dstState )
		self.client.si_dstStateChange( dstState )


	def si_changeMyMoney( self, amount, dstEntity ):
		"""
		@param amount	:	amount of money
		@type amount	:	UNIT32
		@param dstEntity	:	���׶���
		@type dstEntity	:	entity
		@return			:	None
		�����Լ��Ľ��׽�Ǯ���������ط���
		"""
		if self.si_myMoney == amount: return

		#DEBUG_MSG("%s si_myMoney has Change  %s-------->%s" % ( self.id, self.si_myMoney, amount ) )
		self.si_myMoney = amount


	def si_dstChangeMoney( self, amount, dstEntityID ):
		"""
		Define Method
		@param amount	:	the amount of money
		@type amount	:	UNIT32
		@return			:	None
		���öԷ��Ľ��׽�Ǯ����
		"""
		if self.si_targetID != dstEntityID:	# ȷ�����׶�����ȷ���ܽ�������Ĳ���
			HACK_MSG( "id( %i )�Ľ��׶���( %i )����ȷ��" % self.id, dstEntityID )
			return

		dstEntity = BigWorld.entities.get( dstEntityID )
		if dstEntity is None:
			#DEBUG_MSG( "�Ҳ������׶���id( %i )" % dstEntityID )
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return

		nearMax =  self.testAddMoney( amount )
		if nearMax > 0:							#���˴ν��� �᲻��ʹ��ҵĽ�Ǯ��������
			self.statusMessage( csstatus.CIB_MONEY_OVERFLOW )
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return
		elif  nearMax == 0:
			self.statusMessage( csstatus.CIB_MSG_MONEY_OVERFLOW )
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].onDstMoneyChanged( self, dstEntity, amount )


	def si_changeMyItem( self, swapOrder, kitOrder, uid, itemInstance ):
		"""
		@type	swapOrder		:	UINT8
		@param	swapOrder		:	�ڽ������иı��λ��
		@type	itemInstance	:	instance
		@param	itemInstance	:	��Ʒʵ��
		@type	dstEntity	:	entity
		@param	dstEntity	:	���׶���
		@return			:	None
		�ı�/�������������Ľ�����Ʒ�����ط���
		"""
		# ���Ŀ��λ��������Ʒ������ȸ�ԭ��Ʒ����
		if self.si_myItem.has_key( swapOrder ):
			k, t = self.si_myItem[ swapOrder ]
			self.unfreezeItemByUid_( t )

		itemInstance.freeze( self )
		self.si_myItem[ swapOrder ] = ( itemInstance.getAmount(), uid )
		#DEBUG_MSG( "%s MySIItem has change--->" % self.getName() )


	def si_dstChangeItem( self, swapOrder, itemInstance, dstEntityID ):
		"""
		Define method
		@type	swapOrder		:	UINT8
		@param	swapOrder		:	�ڽ������иı��λ��
		@type	itemInstance	:	instance
		@param	itemInstance	:	��Ʒʵ��
		@return			:	None
		�ı�/���ӽ��׶��������Ľ�����Ʒ
		"""
		if self.si_targetID != dstEntityID:	# ȷ�����׶�����ȷ���ܽ�������Ĳ���
			HACK_MSG( "id( %i )�Ľ��׶���( %i )����ȷ��" % self.id, dstEntityID )
			return

		dstEntity = BigWorld.entities.get( dstEntityID )
		if dstEntity is None:
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].onDstItemChanged( self, dstEntity, swapOrder, itemInstance )


	def si_removeMyItem( self, swapOrder, dstEntity ):
		"""
		@type	swapOrder		:	UINT8
		@param	swapOrder		:	�ڽ������иı��λ��
		@type	dstEntity	:	entity
		@param	dstEntity	:	���׶���
		@return			:	None
		�Ƴ����������Ľ�����Ʒ
		"""
		del self.si_myItem[ swapOrder ]
		#DEBUG_MSG("%s MySIItem has change--->" % self.id, self.si_myItem )


	def si_removeDstItem( self, swapOrder, dstEntityID ):
		"""
		Define Method
		@type	swapOrder		:	UINT8
		@param	swapOrder		:	�ڽ������иı��λ��
		@return			:	None
		�Ƴ����׶��������Ľ�����Ʒ
		"""
		if self.si_targetID != dstEntityID:	# ȷ�����׶�����ȷ���ܽ�������Ĳ���
			ERROR_MSG( "���׶���( ID: %i )����ȷ��" % dstEntityID )
			return

		#DEBUG_MSG( "%s si_dstItem has change--->" % self.id, self.si_dstItem )
		dstEntity = BigWorld.entities.get( dstEntityID )
		if dstEntity is None:
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return
		TRADE_SWAP_STATE_MAP[ self.si_myState ].onDstItemRemoved( self, dstEntity, swapOrder )


	def si_changeMyPet( self, petDBID ):
		"""
		�ı伺�����ڽ��׵ĳ���

		@param petDBID:	�ı�ĳ���dbid
		@type petDBID:	DATABASE_ID
		"""
		self.si_myPetDBID = petDBID


	def si_removeMyPet( self ):
		"""
		�Ƴ��������ڽ��׵ĳ���
		"""
		self.si_myPetDBID = 0


	def si_dstChangePet( self, petDBID, dstEntityID ):
		"""
		Define method.
		�Է��ı��˳���

		@param petDBID:	�ı�ĳ���dbid
		@type petDBID:	DATABASE_ID
		@param dstEntityID:	�Է���entity id
		@type dstEntityID:	OBJECT_ID
		"""
		if dstEntityID != self.si_targetID:
			ERROR_MSG( "���׶���( ID: %i )����ȷ��" % dstEntityID )
			return

		dstEntity = BigWorld.entities.get( dstEntityID )
		if dstEntity is None:
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].onDstPetChanged( self, dstEntity, petDBID )


	def si_dstRemovePet( self, dstEntityID ):
		"""
		Define method.
		�Է��Ƴ��˳���
		"""
		if dstEntityID != self.si_targetID:
			ERROR_MSG( "���׶���( ID: %i )����ȷ��" % dstEntityID )
			return

		dstEntity = BigWorld.entities.get( dstEntityID )
		if dstEntity is None:
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return
		TRADE_SWAP_STATE_MAP[ self.si_myState ].onDstPetRemoved( self, dstEntity )


	def si_checkItemTrading( self, dstEntity ):
		"""
		����Ƿ�������ܽ���

		@return: bool
		"""
		if self.si_myMoney > self.money:
			return csstatus.ROLE_TRADE_FAILED_MONEY_CHANGED

		if self.testAddMoney( self.si_dstMoney ) > 0:
			return csstatus.ROLE_TRADE_MONEY_OVERFLOW

		for itemInfo in self.si_myItem.itervalues():
			item = self.getByUid( itemInfo[1] )
			if item is None or item.getAmount() != itemInfo[0]:	# ��Ʒ�����ڻ���Ʒ��������ȷ
				return csstatus.ROLE_TRADE_ITEM_INVALID

		if csdefine.KITBAG_CAN_HOLD == self.checkItemsPlaceIntoNK_( self.si_dstItem.values() ):		# �жϽ�����Ʒ�ɷ���뱳�� add by gjx 2009-4-1
			return csstatus.ROLE_TRADE_ALLOW_TRADE

		return csstatus.ROLE_TRADE_ITEM_OVERFLOW

	def si_checkPetTrading( self, dstEntity ):
		"""
		����Ƿ�������ܽ���

		@return: bool
		"""
		if self.si_myMoney > self.money:
			return csstatus.ROLE_TRADE_FAILED_MONEY_CHANGED

		if self.testAddMoney( self.si_dstMoney ) > 0:	# ���Ի�ô���csstatus.ROLE_TRADE_MONEY_OVERFLOW�������߻�۳�����ʱ���ģ�wsf
			return csstatus.ROLE_TRADE_MONEY_OVERFLOW

		# ���ܳ������������������ޣ��������Ӧ����coconst�ж���,wsf
		if self.pcg_getPetCount() - int( self.si_myPetDBID and 1 or 0 ) + int( self.si_dstPetDBID and 1 or 0 ) > self.pcg_getKeepingCount():
			ERROR_MSG( "��ҳ��ﳬ������." )
			return csstatus.ROLE_PET_AMOUNT_OVERFLOW

		if self.si_dstPetDBID and dstEntity:
			dstPetTakeLevel = dstEntity.pcg_petDict.get( self.si_dstPetDBID ).takeLevel
			dstPetLevel = dstEntity.pcg_petDict.get( self.si_dstPetDBID ).level
			if dstPetTakeLevel > self.level or dstPetLevel > self.level + Const.PET_EXP_LEVEL_LIMIT_GAP:
				return csstatus.ROLE_PET_TAKE_LEVEL_INVALID

		return csstatus.ROLE_TRADE_ALLOW_TRADE


	def si_tradeCancelFC( self, srcEntityID ):
		"""
		Exposed Method.
		�������ȡ�����ס�
		"""
		if srcEntityID != self.id:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % ( srcEntityID, self.id ) )
			return

		dstEntity = BigWorld.entities.get( self.si_targetID )
		self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# ע�⣬dstEntity�п�����None

	def si_resetData( self ):
		"""
		��������Ϊδ����ǰ״̬
		"""
		self.si_myState = 0
		self.si_targetID = 0
		self.si_myItem.clear()
		self.si_dstItem.clear()
		self.si_myMoney = 0
		self.si_dstMoney = 0
		self.si_clearSwapPet()

	def si_clearSwapData( self ):
		"""
		���������Ʒ���׵�����
		"""
		for amount, uid in self.si_myItem.itervalues():
			self.unfreezeItemByUid_( uid )
		self.si_myItem.clear()
		self.si_dstItem.clear()
		self.si_myMoney = 0
		self.si_dstMoney = 0
		self.removeTemp( "si_UID" )
		self.removeTemp( "si_targetNameAndID")


	def si_clearSwapPet( self ):
		"""
		Define method.
		������ڽ��׵ĳ����BASE���ｻ����ɺ���ô˷�������si_myPetDBID
		�������첽����£����׳ɹ���BASE��ûɾ���˳�����ܹ������ٻ������任�������ݵĲ�����
		"""
		if self.si_myPetDBID or self.si_dstPetDBID:
			self.base.si_clearSwapPet()
		self.si_myPetDBID = 0
		self.si_dstPetDBID = 0

	def isPetInSwap( self, petDBID ):
		"""
		�ж�dbidΪpetDBID�ĳ����Ƿ��ڽ����С��ṩ��petCageʹ��
		"""
		return self.si_myPetDBID == petDBID


	def si_trading( self ):
		"""
		Define method.
		��ҽ��׽��У�������Ʒ����Ǯ�������������������ݡ�
		Ŀǰ������Ʒ�ͳ���ͬʱ���н���
		"""
		targetPlayer = BigWorld.entities.get( self.si_targetID )
		if self.si_dstPetDBID or self.si_myPetDBID:
			self.base.si_petTrading()	# ���ڳ��ｻ�ף�֪ͨbase���г��ｻ��
			try:
				g_logger.tradeRolePetLog( self.databaseID, self.getName(), targetPlayer.databaseID, targetPlayer.getName(), self.si_myPetDBID, self.si_getUID() )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

		self.payMoney( self.si_myMoney, csdefine.CHANGE_MONEY_ROLE_TRADING  )
		self.gainMoney( self.si_dstMoney, csdefine.CHANGE_MONEY_ROLE_TRADING )
		if self.si_myMoney > 0:
			try:
				g_logger.tradeRoleMoneyLog( self.databaseID, self.getName(), targetPlayer.databaseID, targetPlayer.getName(), self.si_myMoney, self.si_getUID() )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG()  )

		for amount, uid in self.si_myItem.itervalues():
			self.removeItemByUid_( uid, reason = csdefine.DELETE_ITEM_ROLETRADING )

		for item in self.si_dstItem.itervalues():
			self.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_PTRADE, reason = csdefine.ADD_ITEM_ROLE_TRADING )
			try:
				g_logger.tradeRoleItemLog( self.databaseID, self.getName(), targetPlayer.databaseID, targetPlayer.getName(), item.uid, item.name(), item.getAmount(), self.si_getUID() )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG()  )
		
		self.writeToDB()	# ��Ҽ佻����ɺ�����������������ݵ����ݿ��ֹ�ص���ɽ��ײ��ɹ���12:57 2009-10-29��wsf
		self.si_resetData()

	def onMoneyChanged( self, value, reason ):
		"""
		��ҽ�Ǯ�ı���
		"""
		if self.si_myState != csdefine.TRADE_SWAP_DEFAULT and self.si_myState != csdefine.TRADE_SWAP_LOCKAGAIN:	# ���ڽ���״̬�����˽�Ǯ����ô�˳�����
			try:
				dstEntity = BigWorld.entities[ self.si_targetID ]
			except KeyError:
				dstEntity = None
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )


#
# $Log: not supported by cvs2svn $
# Revision 1.25  2008/07/01 03:06:24  zhangyuxing
# ������Ʒ���뱳������ʧ�ܵ�״̬
#
# Revision 1.24  2008/06/20 06:59:32  wangshufeng
# ����˫�����׾���ĺ����޸�flatDistTo -> distTo
#
# Revision 1.23  2008/05/31 03:00:39  yangkai
# ��Ʒ��ȡ�ӿڸı�
#
# Revision 1.22  2008/05/30 05:47:00  wangshufeng
# ����һ���������
#
# Revision 1.21  2008/05/30 03:01:33  yangkai
# װ������������Ĳ����޸�
#
# Revision 1.20  2008/05/28 08:39:08  wangshufeng
# ������ｻ�׺���Ʒ���ף���Ӧ��������
# ״̬����״̬���ӣ������� ���ｻ������״̬ �� ���ｻ�׵ȴ�״̬
# ������״̬ת������
#
# Revision 1.19  2008/05/27 02:38:15  wangshufeng
# ����si_onDstStateChanged�����������ѭ����һ���������
#
# Revision 1.18  2008/05/26 09:42:05  wangshufeng
# method modify:si_onDstStateChanged,����һ���������
#
# Revision 1.17  2008/03/19 02:48:23  wangshufeng
# �°���ҽ���ϵͳ
#

#
