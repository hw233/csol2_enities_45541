# -*- coding: gb18030 -*-
#
# $Id: RoleSwapItem.py,v 1.26 2008-08-13 00:51:13 wangshufeng Exp $

"""
为了保证交易在异步情况下的数据交换安全，需要在销毁玩家cell时做1到2秒的延迟。wsf
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
		交易状态抽象类
		TRADE_SWAP_DEFAULT					= 0		# 交易默认状态
		TRADE_SWAP_INVITE					= 1		# 交易邀请状态
		TRADE_SWAP_WAITING					= 2		# 交易等待状态(状态持续15秒后如果没反应则交易取消)
		TRADE_SWAP_BEING					= 3		# 物品交易开始状态
		TRADE_SWAP_LOCK						= 4		# 物品锁定状态
		TRADE_SWAP_PET_INVITE				= 5		# 宠物交易邀请状态
		TRADE_SWAP_PET_WAITING				= 6		# 宠物交易等待状态
		TRADE_SWAP_PET_BEING				= 7		# 宠物交易开始状态
		TRADE_SWAP_PET_LOCK					= 8		# 宠物交易锁定状态
		TRADE_SWAP_SURE						= 9		# 交易确定状态
		TRADE_SWAP_LOCKAGAIN				= 10	# 双方再次锁定状态
		"""
		pass


	def enter( self, srcEntity, dstEntity ):
		"""
		进入此状态后在此函数中做一些初始化，

		srcEntity: 进入此状态的entity
		dstEntity: 交易对象的entity
		"""
		pass


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	交易状态改变
		@type	state		:	UINT8
		@param	state		:	改变的状态
		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变状态的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		@rtype:	BOOL,能够改变到state状态则返回True，否则返回False
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def onDstStateChanged( self, srcEntity, destEntity, state ):
		"""
		当交易对象状态改变时收到通知

		srcEntity: 进入此状态的entity
		dstEntity: 交易对象的entity
		state: 交易对象的当前交易状态
		"""
		pass


	def onDstItemChanged( self, srcEntity, dstEntity, swapOrder, itemInstance ):
		"""
		当交易对象改变物品时收到通知

		srcEntity: 进入此状态的entity
		dstEntity: 交易对象的entity
		swapOrder: 欲改变的交易栏目标位置
		itemInstance: 物品实例
		"""
		pass


	def onDstItemRemoved( self, srcEntity, dstEntity, swapOrder ):
		"""
		当交易对象移除物品时收到通知

		srcEntity: 进入此状态的entity
		dstEntity: 交易对象的entity
		swapOrder: 欲移除的交易栏目标位置
		"""
		pass


	def onDstMoneyChanged( self, srcEntity, dstEntity, amount ):
		"""
		当交易对象改变金钱时收到通知

		srcEntity: 进入此状态的entity
		dstEntity: 交易对象的entity
		amount: 欲改变的金钱数量
		"""
		pass


	def onDstPetChanged( self, srcEntity, dstEntity, petDBID ):
		"""
		当交易对象改变宠物时收到通知

		srcEntity: 进入此状态的entity
		dstEntity: 交易对象的entity
		petDBID: 欲改变的宠物dbid
		"""
		pass


	def onDstPetRemoved( self, srcEntity, dstEntity ):
		"""
		当交易对象移除宠物时收到通知

		srcEntity: 进入此状态的entity
		dstEntity: 交易对象的entity
		"""
		pass


	def changeItem( self, srcEntity, dstEntity, swapOrder, kitOrder, uid, itemInstance ):
		"""
		virtual method
		交易物品的增加导致状态的改变
		此状态下不能

		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变物品的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		@type	swapOrder	:	改变的交易栏位置
		@param	swapOrder	:	UINT8
		@type	kitOrder	:	背包号
		@param	kitOrder	:	UINT8
		@type	uid			:	物品的uid
		@param	uid			:	INT64
		@type	itemInstance	:	物品实例
		@param	itemInstance	:	ITEM
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		移除一个物品

		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变物品的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		@type	swapOrder	:	改变的交易栏位置
		@param	swapOrder	:	UINT8
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		改变金钱

		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变物品的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		@type	amount	:	金钱数量
		@param	amount	:	UINT32
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapState can't allow to changeMoney" % ( srcEntity.id, dstEntity.id ) )


	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		virtual method
		改变宠物

		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变物品的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		@type	petDBID	:	宠物的dbid
		@param	petDBID	:	INT64
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to changePet" % ( srcEntity.id, dstEntity.id ) )


	def removePet( self, srcEntity, dstEntity ):
		"""
		virtual method
		移除宠物

		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变物品的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this state can't allow to removePet" % ( srcEntity.id, dstEntity.id ) )


class RoleSwapDefaultState( RoleSwapState ):
	"""
	无交易状态类
	csdefine.TRADE_SWAP_DEFAULT
	可以进入csdefine.TRADE_SWAP_WAITING或csdefine.TRADE_SWAP_INVITE状态
	状态机会根据相应的状态设置数据
	"""
	_instance = None
	def __init__( self ):
		assert RoleSwapDefaultState._instance is None
		RoleSwapState.__init__( self )


	def enter( self, srcEntity, dstEntity ):
		"""
		进入此状态后在此函数中做一些初始化

		srcEntity: 进入此状态的entity
		dstEntity: 交易对象的entity
		"""
		srcEntity.si_clearSwapPet()
		srcEntity.statusMessage( csstatus.ROLE_TRADE_CANCEL )
		srcEntity.si_clearSwapData()							# 解锁用于交易的物品
		srcEntity.si_targetID = 0


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	交易状态改变
		@type	state		:	UINT8
		@param	state		:	改变的状态
		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变状态的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
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
		当交易对象状态改变时收到通知，只对影响己方的对方状态处理
		"""
		if dstState == csdefine.TRADE_SWAP_INVITE:	# 对方的状态转变为邀请状态
			srcEntity.si_changeState( csdefine.TRADE_SWAP_WAITING, dstEntity )
			return

		if dstState == csdefine.TRADE_SWAP_PET_INVITE:	# 对方的状态转变为邀请状态
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
		交易物品的增加导致状态的改变
		此状态下不能
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapDefaultState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		交易物品的移除导致状态的改变
		此状态下不能
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapDefaultState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		金钱数量改变
		此状态下不能
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
	请求交易状态
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
		进入此状态后在此函数中做一些初始化
		"""
		srcEntity.si_targetID = dstEntity.id
		swapUID = Function.newUID()
		srcEntity.setTemp( "si_UID", swapUID )
		srcEntity.setTemp( "si_targetNameAndID", dstEntity.getNameAndID())
		dstEntity.si_receiveUID( swapUID, srcEntity.getNameAndID())


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	交易状态改变
		@type	state		:	UINT8
		@param	state		:	改变的状态
		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变状态的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		"""
		if state == csdefine.TRADE_SWAP_BEING:
			return True

		if state == csdefine.TRADE_SWAP_INVITE:		# 在邀请状态还可以变更交易对象
			return True

		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True

		return False


	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		当交易对象状态改变时收到通知，只对影响己方的对方状态处理
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
		交易物品的增加导致状态的改变
		此状态下不能
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapInviteState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )

	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		交易物品的移除导致状态的改变
		此状态下不能
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapInviteState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )

	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		金钱数量改变
		此状态下不能
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
	等待交易状态类
	csdefine.TRADE_SWAP_WAITING
	"""
	_instance = None
	def __init__( self ):
		assert RoleSwapWaitState._instance is None
		RoleSwapState.__init__( self )


	def enter( self, srcEntity, dstEntity ):
		"""
		在等待状态下只设置交易对象
		"""
		srcEntity.si_targetID = dstEntity.id


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	交易状态改变
		@type	state		:	UINT8
		@param	state		:	改变的状态
		@type	srcEntity	:	entity
		@param	srcEntity	:	MAILBOX
		"""
		if state == csdefine.TRADE_SWAP_BEING:
			return True

		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True


	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		当交易对象状态改变时收到通知，只对影响己方的对方状态处理
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
		交易物品的增加导致状态的改变
		此状态下不能
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapWaitState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		交易物品的移除导致状态的改变
		此状态下不能
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapWaitState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		金钱数量改变
		此状态下不能
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
	物品交易进行中状态类
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
		@summary			:	交易状态改变
		@type	state		:	UINT8
		@param	state		:	改变的状态
		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变状态的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		"""
		# 锁定状态
		if state == csdefine.TRADE_SWAP_LOCK:					# 进入此状态不影响对方
			return True

		#if state == csdefine.TRADE_SWAP_PET_BEING:				# 物品交易转换到宠物交易pet
		#	srcEntity.base.si_setTargetID( dstEntity.id )		# 设置BASE的交易对象
		#	srcEntity.si_clearSwapData()						# 清除物品数据，只有在这个地方才知道是否要清除
		#	return True

		if state == csdefine.TRADE_SWAP_DEFAULT:				# 离开交易
			return True

		return False


	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		当交易对象状态改变时收到通知，只对影响己方的对方状态处理
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
		@summary				:	交易物品的改变导致状态的改变
		@type	srcEntity		:	entity
		@param	srcEntity		:	主动改变状态的entity
		@type	dstEntity		:	entity
		@param	dstEntity		:	被影响的entity
		@type	swapOrder		:	UINT8
		@param	swapOrder		:	在交易栏中改变的位置
		@type	kitOrder		:	UINT8
		@param	kitOrder		:	背包序列
		@type	uid				:	INT64
		@param	uid				:	背包物品序列
		@type	itemInstance	:	instance
		@param	itemInstance	:	物品实例
		"""
		srcEntity.si_changeMyItem( swapOrder, kitOrder, uid, itemInstance )
		srcEntity.client.si_meChangeItem( swapOrder, kitOrder, uid )
		dstEntity.si_dstChangeItem( swapOrder, itemInstance.copy(), srcEntity.id )	# 通知对方交易物品改变


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		@summary			:	交易物品的移除导致状态的改变
		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变状态的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		@type	swapOrder	:	UINT8
		@param	swapOrder	:	在交易栏中改变的位置
		"""
		srcEntity.si_removeMyItem( swapOrder, dstEntity )
		dstEntity.si_removeDstItem( swapOrder, srcEntity.id )
		srcEntity.client.si_removeSwapItem( 0, swapOrder )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		@summary			:	金钱数量改变
		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变状态的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		@type	amount		:	UINT32
		@param	amount		:	金钱数量
		"""
		#金钱数量改变时，对方都回到交易中状态
		#通知对方说自己的金钱改变了
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
	物品交易锁定状态类
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
		状态改变
		@summary			:	交易状态改变
		@type	state		:	UINT8
		@param	state		:	改变的状态
		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变状态的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
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
				srcEntity.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# 离开交易
				return False
			return True

		if state == csdefine.TRADE_SWAP_BEING:					# 如果是取消锁定
			return True

		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True

		#if state == csdefine.TRADE_SWAP_PET_BEING:				# 物品交易转换到宠物交易pet
		#	srcEntity.base.si_setTargetID( dstEntity.id )		# 设置BASE的交易对象
		#	srcEntity.si_clearSwapData()						# 清除物品数据，只有在这个地方才知道是否要清除
		#	return True

		return False


	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		当交易对象状态改变时收到通知，只对影响己方的对方状态处理
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
		@summary			:	交易物品的改变导致状态的改变
		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变状态的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		@type	swapOrder	:	UINT8
		@param	swapOrder	:	在交易栏中改变的位置
		@type	kitOrder	:	UINT8
		@param	kitOrder	:	背包序列
		@type	uid			:	INT64
		@param	uid			:	背包物品序列
		@type	itemInstance:	instance
		@param	itemInstance:	物品实例
		"""
		#在这个状态下，如果玩家对交易物品有增加
		#都会转变状态到 csdefine.TRADE_SWAP_BEING(正在交易状态)
		#只要有一方的物品有变动，那么双方都回到交易进行中状态
		srcEntity.si_changeMyItem( swapOrder, kitOrder, uid, itemInstance )
		srcEntity.client.si_meChangeItem( swapOrder, kitOrder, uid )
		srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )
		dstEntity.si_dstChangeItem( swapOrder, itemInstance.copy(), srcEntity.id )	# 通知对方交易物品改变


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		@summary			:	交易物品的移除导致状态的改变
		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变状态的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		@type	swapOrder	:	UINT8
		@param	swapOrder	:	在交易栏中改变的位置
		"""
		# 在这个状态下，如果玩家对交易物品有移除
		# 都会转变状态到 csdefine.TRADE_SWAP_BEING(正在交易状态)
		# 只要有一方的物品有变动，那么双方都回到交易进行中状态
		srcEntity.si_removeMyItem( swapOrder, dstEntity )
		dstEntity.si_removeDstItem( swapOrder, srcEntity.id )
		srcEntity.si_changeState( csdefine.TRADE_SWAP_BEING, dstEntity )
		srcEntity.client.si_removeSwapItem( 0, swapOrder )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		@summary			:	金钱数量改变
		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变状态的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		@type	amount		:	UINT32
		@param	amount		:	金钱数量
		"""
		#金钱数量改变时，双方都回到交易中状态
		#通知对方说自己的金钱改变了
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
	确认交易状态类，物品交易和宠物交易可同时进行
	csdefine.TRADE_SWAP_LOCK
	"""
	_instance = None
	def __init__( self ):
		assert RoleSwapSureState._instance is None
		RoleSwapState.__init__( self )


	def enter( self, srcEntity, dstEntity ):
		"""
		"""
		# 如果对方已经处于确认交易状态，那么就进入2次锁定状态，在本cellApp获得的对方状态可能不准确，但在2次锁定状态中有后续处理
		#if dstEntity.si_myState == csdefine.TRADE_SWAP_SURE:
		#	srcEntity.si_changeState( csdefine.TRADE_SWAP_LOCKAGAIN, dstEntity, False )
		pass


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	交易状态改变
		@type	state		:	UINT8
		@param	state		:	改变的状态
		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变状态的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		"""
		if state == csdefine.TRADE_SWAP_BEING:
			return True

		if state == csdefine.TRADE_SWAP_PET_BEING:
			return True

		if state == csdefine.TRADE_SWAP_DEFAULT:
			if dstEntity and dstEntity.si_myState == csdefine.TRADE_SWAP_LOCKAGAIN:	# 过滤掉对方已经确认交易的情况下玩家请求取消的的消息。
				return False
			return True

		if state == csdefine.TRADE_SWAP_LOCKAGAIN:
			return True

		return False

	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		当交易对象状态改变时收到通知，只对影响己方的对方状态处理
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
		交易物品的增加导致状态的改变
		此状态下不能
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapSureState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		交易物品的移除导致状态的改变
		此状态下不能
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapSureState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		金钱数量改变
		此状态下不能
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
	再次锁定交易状态类，再次锁定是服务器行为
	csdefine.TRADE_SWAP_LOCKAGAIN

	在异步情况下实现2个玩家的安全交易，防止物品复制（前提是服务器不会突然崩溃）。
	在2个玩家都进入csdefine.TRADE_SWAP_SURE状态后，双方必须都进入此状态才能进行交换物品金钱数据的操作。

	例如，己方确认交易，在获得对方已先确认交易的情况下，进入再次锁定状态，并通知对方进入再次锁定状态，
	对方在收到己方要求进入2次交易的消息时，进入2次交易状态，并进行交换数据的操作同时通知己方也进行交换数据的操作。
	如果对方在收到己方要求进入2次交易的消息时已经不在确认交易状态，那么通知己方离开交易。

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
			srcEntity.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# 离开交易
			srcEntity.statusMessage( state )
			dstEntity.client.onStatusMessage( state, "" )
			return
		state = srcEntity.si_checkPetTrading( dstEntity )
		if state != csstatus.ROLE_TRADE_ALLOW_TRADE:
			srcEntity.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# 离开交易
			srcEntity.statusMessage( state )
			dstEntity.client.onStatusMessage( state, "" )
			return
		# 如果对方已经处于TRADE_SWAP_LOCKAGAIN状态，那么对方就不能够改变物品了，虽然对方有可能销毁，但是会在cell销毁时做一个延迟，以便处理这样的异步情况
		if dstEntity.si_myState == csdefine.TRADE_SWAP_LOCKAGAIN:
			srcEntity.si_trading()
			dstEntity.si_trading()

			srcEntity.statusMessage( csstatus.ROLE_TRADE_SUCCESS )
			dstEntity.statusMessage( csstatus.ROLE_TRADE_SUCCESS )

	def changeState( self, state, srcEntity, dstEntity ):	# wsfwsf
		"""
		virtual method
		@summary			:	交易状态改变
		@type	state		:	UINT8
		@param	state		:	改变的状态
		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变状态的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		"""
		# 如果玩家处于TRADE_SWAP_LOCKAGAIN状态，不允许客户端expoed方法改变状态
		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True

	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		当交易对象状态改变时收到通知，只对影响己方的对方状态处理
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
		交易物品的增加导致状态的改变
		此状态下不能
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapLockAgainState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		交易物品的移除导致状态的改变
		此状态下不能
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapLockAgainState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		金钱数量改变
		此状态下不能
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
	请求交易状态
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
		进入此状态后在此函数中做一些初始化
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
		@summary			:	交易状态改变
		@type	state		:	UINT8
		@param	state		:	改变的状态
		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变状态的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		"""
		if state == csdefine.TRADE_SWAP_PET_INVITE:		# 在邀请状态还可以变更交易对象
			return True

		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True

		if state == csdefine.TRADE_SWAP_PET_BEING:
			return True

		return False


	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		当交易对象状态改变时收到通知，只对影响己方的对方状态处理
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
		交易物品的增加导致状态的改变
		此状态下不能
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapPetInviteState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		交易物品的移除导致状态的改变
		此状态下不能
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapPetInviteState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		金钱数量改变
		此状态下不能
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
	等待交易状态类
	csdefine.TRADE_SWAP_WAITING
	"""
	_instance = None
	def __init__( self ):
		assert RoleSwapPetWaitState._instance is None
		RoleSwapState.__init__( self )


	def enter( self, srcEntity, dstEntity ):
		"""
		在等待状态下只设置交易对象
		"""
		srcEntity.si_targetID = dstEntity.id
		srcEntity.base.si_setTargetID( dstEntity.id )


	def changeState( self, state, srcEntity, dstEntity ):
		"""
		virtual method
		@summary			:	交易状态改变
		@type	state		:	UINT8
		@param	state		:	改变的状态
		@type	srcEntity	:	entity
		@param	srcEntity	:	MAILBOX
		"""
		if state == csdefine.TRADE_SWAP_PET_BEING:
			return True

		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True


	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		当交易对象状态改变时收到通知，只对影响己方的对方状态处理
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
		交易物品的增加导致状态的改变
		此状态下不能
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapPetWaitState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		交易物品的移除导致状态的改变
		此状态下不能
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapPetWaitState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		金钱数量改变
		此状态下不能
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
	宠物交易进行状态
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
		@summary			:	交易状态改变
		@type	state		:	UINT8
		@param	state		:	改变的状态
		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变状态的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		@type	flag	:	BOOL
		@param	flag	:	True为服务器更改请求，无条件更改；False为玩家更改请求，需进行甄别
		"""
		if state == csdefine.TRADE_SWAP_PET_LOCK:		# 转为锁定状态
			return True

		#if state == csdefine.TRADE_SWAP_BEING:			# 转为物品交易状态
		#	srcEntity.si_clearSwapPet()
		#	srcEntity.base.si_setTargetID( 0 )			# 清除base数据
		#	return True

		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True

		return False


	def onDstStateChanged( self, srcEntity, dstEntity, dstState ):
		"""
		当交易对象状态改变时收到通知，只对影响己方的对方状态处理
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
		交易物品的增加导致状态的改变
		此状态下不能
		"""
		ERROR_MSG("%s Trade with %s Maybe a error that this RoleSwapLockAgainState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		交易物品的移除导致状态的改变
		此状态下不能
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapLockAgainState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		金钱数量改变
		"""
		srcEntity.si_changeMyMoney( amount, dstEntity )
		dstEntity.si_dstChangeMoney( amount, srcEntity.id )


	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		virtual method
		"""
		srcEntity.si_changeMyPet( petDBID )
		srcEntity.base.si_changeMyPet( petDBID, dstEntity.base )	# 通知base发送宠物数据
		dstEntity.si_dstChangePet( petDBID, srcEntity.id )			# 通知对方交易宠物改变


	def removePet( self, srcEntity, dstEntity ):
		"""
		virtual method
		"""
		srcEntity.si_removeMyPet()
		srcEntity.base.si_removeMyPet( dstEntity.base )				# 通知base移除宠物数据
		dstEntity.si_dstRemovePet( srcEntity.id )					# 通知对方移除交易宠物


	@staticmethod
	def instance():
		if RoleSwapPetBeingState._instance is None:
			RoleSwapPetBeingState._instance = RoleSwapPetBeingState()
		return RoleSwapPetBeingState._instance


class RoleSwapPetLockState( RoleSwapState ):
	"""
	宠物交易锁定状态
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
		@summary			:	交易状态改变
		@type	state		:	UINT8
		@param	state		:	改变的状态
		@type	srcEntity	:	entity
		@param	srcEntity	:	主动改变状态的entity
		@type	dstEntity	:	entity
		@param	dstEntity	:	被影响的entity
		@type	flag	:	BOOL
		@param	flag	:	True为服务器更改请求，无条件更改；False为玩家更改请求，需进行甄别
		"""
		if state == csdefine.TRADE_SWAP_DEFAULT:
			return True

		if state == csdefine.TRADE_SWAP_PET_BEING:			# 在本状态下改变宠物或金钱,转变到正在交易状态
			return True

		if state == csdefine.TRADE_SWAP_SURE:				# 转变到确认状态
			if dstEntity.si_myState < csdefine.TRADE_SWAP_PET_LOCK:					# 对方还没有锁定，不能确认交易
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
		当交易对象状态改变时收到通知，只对影响己方的对方状态处理
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
		交易物品的增加导致状态的改变
		此状态下不能
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapLockAgainState can't allow to changeItem" % ( srcEntity.id, dstEntity.id ) )


	def removeItem( self, srcEntity, dstEntity, swapOrder ):
		"""
		virtual method
		交易物品的移除导致状态的改变
		此状态下不能
		"""
		ERROR_MSG( "%s Trade with %s Maybe a error that this RoleSwapLockAgainState can't allow to removeItem" % ( srcEntity.id, dstEntity.id ) )


	def changeMoney( self, srcEntity, dstEntity, amount ):
		"""
		virtual method
		金钱数量改变
		此状态下不能
		"""
		srcEntity.si_changeMyMoney( amount, dstEntity )
		srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )
		dstEntity.si_dstChangeMoney( amount, srcEntity.id )


	def changePet( self, srcEntity, dstEntity, petDBID ):
		"""
		virtual method
		"""
		srcEntity.si_changeMyPet( petDBID )
		srcEntity.base.si_changeMyPet( petDBID, dstEntity.base )	# 通知base发送宠物数据
		srcEntity.si_changeState( csdefine.TRADE_SWAP_PET_BEING, dstEntity )
		dstEntity.si_dstChangePet( petDBID, srcEntity.id )


	def removePet( self, srcEntity, dstEntity ):
		"""
		virtual method
		"""
		srcEntity.si_removeMyPet()
		srcEntity.base.si_removeMyPet( dstEntity.base )				# 通知base移除宠物数据
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
	玩家间物品交换相关代码
	"""
	def __init__( self ):
		"""
		"""
		pass
		# self.si_myPetDBID = 0	# 用于交易的宠物dbid

	def si_receiveUID( self, swapUID,targetNameAndID ):
		"""
		Define method.
		接收本次交易的交易号，目前交易号的作用仅是标识本次交易

		@param swapUID : 本次交易的唯一标识
		@type swapUID : INT64
		@param targetNameAndID : 交易的对方的名字和ID
		@type targetNameAndID : STRING
		"""
		if self.si_myState == csdefine.TRADE_SWAP_DEFAULT:
			self.setTemp( "si_UID", swapUID )
			self.setTemp( "si_targetNameAndID", targetNameAndID)


	def si_getUID( self ):
		"""
		获得本次交易的uid号
		"""
		si_UID = self.queryTemp( "si_UID", 0 )
		if si_UID == 0:
			ERROR_MSG( "player( %s )'s si_UID had lost." % ( self.getName() ) )
		return si_UID

	def si_getTargetNameAndID( self ):
		"""
		获得本次交易的uid号
		"""
		si_targetNameAndID = self.queryTemp( "si_targetNameAndID", "" )
		if si_targetNameAndID == "":
			ERROR_MSG( "player( %s )'s si_targetNameAndID had lost." % ( self.getName() ) )
		return si_targetNameAndID

	def si_requestSwapFC( self, srcEntityID, dstEntityID, flag ):
		"""
		Exposed method.
		请求与 dstEntityID 交易.根据flag确定是进行宠物交易还是物品交易
		@param dstEntityID: 交易目标entity id
		@type  dstEntityID: OBJECT_ID
		@param flag: 交易的类型，物品/宠物 交易，flag为1表示物品交易，为0表示宠物交易
		@type  flag: UINT8
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src( %i ) calling dst( %i ) method" % ( srcEntityID, self.id ) )
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
			if flag == 1:		# 物品交易时要考虑背包有没有上锁
				self.statusMessage(csstatus.ROLE_TRADE_CANNOT_TRADE)
			elif flag == 0:	# 背包上锁不能进行宠物交易，by姜毅
				self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_PET_TRADE, "" )
			return
		if self.actionSign( csdefine.ACTION_FORBID_TRADE ) or dstEntity.actionSign( csdefine.ACTION_FORBID_TRADE ): #判断交易双方是否有无法交易的标志
			self.statusMessage(csstatus.ROLE_TRADE_FORBID_TRADE)
			return
		if dstEntity.qieCuoState != csdefine.QIECUO_NONE:
			self.statusMessage( csstatus.TARGET_IS_QIECUO )
			return

		# 战斗状态下也可以进行交易。
		#if self.getState() != csdefine.ENTITY_STATE_FREE:
		#	srcEntity.statusMessage( csstatus.ROLE_TRADE_IN_BUSY )
		#	return

		# 必须保证csdefine.TRADE_SWAP_INVITE与csdefine.TRADE_SWAP_PET_INVITE不会是False
		state = flag and csdefine.TRADE_SWAP_INVITE or csdefine.TRADE_SWAP_PET_INVITE
		self.si_changeState( state, dstEntity )


	def si_changeItemFC( self, srcEntityID, swapOrder, kitOrder, uid ):
		"""
		Exposed Method
		在某个位置改变(增加)一个交易物品

		@param   swapOrder: 交易栏里的位置，0为第一个位置
		@type    swapOrder: UINT8
		@param    kitOrder: 自己身上的哪个背包
		@type     kitOrder: UINT8
		@param         uid: 物品在人物身上的唯一标识, 在这里表示要放自己身上的哪个物品
		@type          uid: INT64
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src( %i ) calling dst( %i ) method" % ( srcEntityID, self.id ) )
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

		# 特定物品等级限制不能交易
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
			# 交易目标不存在，取消交易
			dstEntity = None
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# 注意，dstEntity有可能是None
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].changeItem( self, dstEntity, swapOrder, kitOrder, uid, item )


	def si_removeItemFC( self, srcEntityID, swapOrder ):
		"""
		Expose method.
		把某个交易位置置空
		@param srcEntityID: 爆露方法必须的参数, 在这里self.id必须等于srcEntityID
		@type  srcEntityID: OBJECT_ID
		@param   swapOrder: 交易栏里的位置，0为第一个位置
		@type    swapOrder: UINT8
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % ( srcEntityID, self.id ) )
			return

		try:	# 相当参数检察
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
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# 注意，dstEntity有可能是None
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].removeItem( self, dstEntity, swapOrder )


	def si_changeMoneyFC( self, srcEntityID, amount ):
		"""
		Exposed Method
		改变自己的出价金钱数量
		@param srcEntityID: 爆露方法必须的参数, 在这里self.id必须等于srcEntityID
		@type  srcEntityID: OBJECT_ID
		@param      amount: 金钱数量
		@type       amount: UINT32
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % (srcEntityID, self.id) )
			return
		# 验证自己的金钱是否够
		if self.money < amount or amount < 0:
			self.si_myMoney = self.si_myMoney
			self.statusMessage( csstatus.ROLE_TRADE_NOT_ENOUGH_MONEY )
			return

		try:
			dstEntity = BigWorld.entities[ self.si_targetID ]
		except KeyError:
			dstEntity = None
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# 注意，dstEntity有可能是None
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].changeMoney( self, dstEntity, amount )


	def si_changeStateFC( self, srcEntityID, state ):
		"""
		Exposed method
		交易状态改变，这个方法只会在双方都处于交易中才会被调用

		@param  state: si_myState
		@type   state: UINT8
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src( %i ) calling dst( %i ) method" % ( srcEntityID, self.id ) )
			return
		try:
			dstEntity = BigWorld.entities[ self.si_targetID ]
		except KeyError:
			dstEntity = None
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# 注意，dstEntity有可能是None
			return

		# 在客户端判断双方是否在10米之内
		#if self.position.flatDistTo( dstEntity.position ) > csconst.COMMUNICATE_DISTANCE:
		#	TRADE_SWAP_STATE_MAP[ self.si_myState ].SILeaveTrade( self, dstEntity, False )
		#	self.statusMessage( csstatus.ROLE_TRADE_TARGET_TOO_FAR )
		#	return

		if state < csdefine.TRADE_SWAP_BEING or state > csdefine.TRADE_SWAP_SURE:
			ERROR_MSG( "state参数不正确。" )
			return

		if self.iskitbagsLocked():	# 背包上锁，by姜毅
			self.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_PET_TRADE, "" )
			return

		self.si_changeState( state, dstEntity )


	def si_changePetFC( self, srcEntityID, petDBID ):
		"""
		Exposed method.
		改变用于交易的宠物

		@param petDBID:	宠物的dbid
		@type petDBID:	DATABASE_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % ( srcEntityID, self.id ) )
			return

		try:
			dstEntity = BigWorld.entities[ self.si_targetID ]
		except KeyError:
			dstEntity = None
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# 注意，dstEntity有可能是None
			return

		#if self.position.flatDistTo( dstEntity.position ) > csconst.COMMUNICATE_DISTANCE:
		#	TRADE_SWAP_STATE_MAP[ self.si_myState ].SILeaveTrade( self, dstEntity, False )
		#	self.statusMessage( csstatus.ROLE_TRADE_TARGET_TOO_FAR )
		#	return

		if not self.pcg_petDict.has_key( petDBID ):
			HACK_MSG( "错误的宠物databaseID。" )
			return

		if self.pcg_isActPet( petDBID ):
			return

		if self.pcg_isPetBinded( petDBID ):
			self.statusMessage( csstatus.PET_HAD_BEEN_BIND )
			return
		if self.pcg_isConjuring( petDBID ):	# 如果选择正在出征的宠物，那么退出交易
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return

		if self.ptf_procreating( petDBID ):
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].changePet( self, dstEntity, petDBID )


	def si_removePetFC( self, srcEntityID ):
		"""
		Exposed method.
		移除用于交易的宠物
		"""
		if self.id != srcEntityID:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % ( srcEntityID, self.id ) )
			return

		try:
			dstEntity = BigWorld.entities[ self.si_targetID ]
		except KeyError:
			dstEntity = None
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# 注意，dstEntity有可能是None
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].removePet( self, dstEntity )


	def si_changeState( self, state, dstEntity ):
		"""
		统一状态机改变接口，任何状态的改变都应该调用此接口统一处理。
		此状态改变接口不作任何直接的合法性检查，全部都由当前的状态机决定
		"""
		if TRADE_SWAP_STATE_MAP[ self.si_myState ].changeState( state, self, dstEntity ):
			self.si_myState = state
			TRADE_SWAP_STATE_MAP[ self.si_myState ].enter( self, dstEntity )
			if dstEntity is None:	# 如果对方已经不在了，不需要通知对方（这时己方应该离开交易）
				return
			dstEntity.si_onDstStateChanged( self.si_myState, self.id )	# 所有状态变化都需通知


	def si_onDstStateChanged( self, dstState, dstEntityID ):
		"""
		Define method.
		对方改变到dstState状态，通知己方。
		判断交易对象是否正确，然后通知状态机，在状态机中决定是否更改。

		param dstState: 对方的交易状态
		type dstState: UINT8
		param dstEntityID: 对方的entity id
		type dstEntityID: OBJECT_ID
		"""
		# 有一个例外情况，对方在csdefine.TRADE_SWAP_LOCKAGAIN状态，而己方在csdefine.TRADE_SWAP_DEFAULT状态，那么通知对方离开交易
		# 出现这个情况是因为，对方看到己方已经点了交易按钮情况下，对方点击交易，对方将进入csdefine.TRADE_SWAP_LOCKAGAIN状态并通知己方进入同样的状态
		# 由于网络延时，己方的取消交易消息先于服务器要求己方进入csdefine.TRADE_SWAP_LOCKAGAIN状态的消息到达，此时必须通知对方取消交易而不理会TRADE_SWAP_LOCKAGAIN。
		if dstState == csdefine.TRADE_SWAP_LOCKAGAIN and self.si_myState == csdefine.TRADE_SWAP_DEFAULT:
			dstEntity = BigWorld.entities.get( dstEntityID )
			if dstEntity:
				dstState = csdefine.TRADE_SWAP_DEFAULT
				dstEntity.si_onDstStateChanged( dstState, self.id )
			return

		dstEntity = BigWorld.entities.get( dstEntityID )
		if dstEntityID != self.si_targetID and self.si_myState != csdefine.TRADE_SWAP_DEFAULT:	# 过滤掉己方处于default状态没有si_targetID的情况
			if dstState == csdefine.TRADE_SWAP_INVITE:
				if dstEntity is not None:
					dstEntity.statusMessage( csstatus.ROLE_TRADE_TARGET_IN_BUSY )				# 处于繁忙状态
			dstEntity.si_onDstStateChanged( csdefine.TRADE_SWAP_DEFAULT, self.id )				# 通知对方离开交易
			return

		if dstEntity is None:																	# 找不到对方则离开交易
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].onDstStateChanged( self, dstEntity, dstState )
		self.client.si_dstStateChange( dstState )


	def si_changeMyMoney( self, amount, dstEntity ):
		"""
		@param amount	:	amount of money
		@type amount	:	UNIT32
		@param dstEntity	:	交易对象
		@type dstEntity	:	entity
		@return			:	None
		设置自己的交易金钱数量，本地方法
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
		设置对方的交易金钱数量
		"""
		if self.si_targetID != dstEntityID:	# 确定交易对象正确才能进行下面的操作
			HACK_MSG( "id( %i )的交易对象( %i )不正确。" % self.id, dstEntityID )
			return

		dstEntity = BigWorld.entities.get( dstEntityID )
		if dstEntity is None:
			#DEBUG_MSG( "找不到交易对象。id( %i )" % dstEntityID )
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return

		nearMax =  self.testAddMoney( amount )
		if nearMax > 0:							#检测此次交易 会不会使玩家的金钱超过上限
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
		@param	swapOrder		:	在交易栏中改变的位置
		@type	itemInstance	:	instance
		@param	itemInstance	:	物品实例
		@type	dstEntity	:	entity
		@param	dstEntity	:	交易对象
		@return			:	None
		改变/增加自身交易栏的交易物品，本地方法
		"""
		# 如果目标位置已有物品则必须先给原物品解锁
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
		@param	swapOrder		:	在交易栏中改变的位置
		@type	itemInstance	:	instance
		@param	itemInstance	:	物品实例
		@return			:	None
		改变/增加交易对象交易栏的交易物品
		"""
		if self.si_targetID != dstEntityID:	# 确定交易对象正确才能进行下面的操作
			HACK_MSG( "id( %i )的交易对象( %i )不正确。" % self.id, dstEntityID )
			return

		dstEntity = BigWorld.entities.get( dstEntityID )
		if dstEntity is None:
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].onDstItemChanged( self, dstEntity, swapOrder, itemInstance )


	def si_removeMyItem( self, swapOrder, dstEntity ):
		"""
		@type	swapOrder		:	UINT8
		@param	swapOrder		:	在交易栏中改变的位置
		@type	dstEntity	:	entity
		@param	dstEntity	:	交易对象
		@return			:	None
		移除自身交易栏的交易物品
		"""
		del self.si_myItem[ swapOrder ]
		#DEBUG_MSG("%s MySIItem has change--->" % self.id, self.si_myItem )


	def si_removeDstItem( self, swapOrder, dstEntityID ):
		"""
		Define Method
		@type	swapOrder		:	UINT8
		@param	swapOrder		:	在交易栏中改变的位置
		@return			:	None
		移除交易对象交易栏的交易物品
		"""
		if self.si_targetID != dstEntityID:	# 确定交易对象正确才能进行下面的操作
			ERROR_MSG( "交易对象( ID: %i )不正确。" % dstEntityID )
			return

		#DEBUG_MSG( "%s si_dstItem has change--->" % self.id, self.si_dstItem )
		dstEntity = BigWorld.entities.get( dstEntityID )
		if dstEntity is None:
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return
		TRADE_SWAP_STATE_MAP[ self.si_myState ].onDstItemRemoved( self, dstEntity, swapOrder )


	def si_changeMyPet( self, petDBID ):
		"""
		改变己方用于交易的宠物

		@param petDBID:	改变的宠物dbid
		@type petDBID:	DATABASE_ID
		"""
		self.si_myPetDBID = petDBID


	def si_removeMyPet( self ):
		"""
		移除己方用于交易的宠物
		"""
		self.si_myPetDBID = 0


	def si_dstChangePet( self, petDBID, dstEntityID ):
		"""
		Define method.
		对方改变了宠物

		@param petDBID:	改变的宠物dbid
		@type petDBID:	DATABASE_ID
		@param dstEntityID:	对方的entity id
		@type dstEntityID:	OBJECT_ID
		"""
		if dstEntityID != self.si_targetID:
			ERROR_MSG( "交易对象( ID: %i )不正确。" % dstEntityID )
			return

		dstEntity = BigWorld.entities.get( dstEntityID )
		if dstEntity is None:
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return

		TRADE_SWAP_STATE_MAP[ self.si_myState ].onDstPetChanged( self, dstEntity, petDBID )


	def si_dstRemovePet( self, dstEntityID ):
		"""
		Define method.
		对方移除了宠物
		"""
		if dstEntityID != self.si_targetID:
			ERROR_MSG( "交易对象( ID: %i )不正确。" % dstEntityID )
			return

		dstEntity = BigWorld.entities.get( dstEntityID )
		if dstEntity is None:
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )
			return
		TRADE_SWAP_STATE_MAP[ self.si_myState ].onDstPetRemoved( self, dstEntity )


	def si_checkItemTrading( self, dstEntity ):
		"""
		检查是否允许接受交易

		@return: bool
		"""
		if self.si_myMoney > self.money:
			return csstatus.ROLE_TRADE_FAILED_MONEY_CHANGED

		if self.testAddMoney( self.si_dstMoney ) > 0:
			return csstatus.ROLE_TRADE_MONEY_OVERFLOW

		for itemInfo in self.si_myItem.itervalues():
			item = self.getByUid( itemInfo[1] )
			if item is None or item.getAmount() != itemInfo[0]:	# 物品不存在或物品数量不正确
				return csstatus.ROLE_TRADE_ITEM_INVALID

		if csdefine.KITBAG_CAN_HOLD == self.checkItemsPlaceIntoNK_( self.si_dstItem.values() ):		# 判断交易物品可否放入背包 add by gjx 2009-4-1
			return csstatus.ROLE_TRADE_ALLOW_TRADE

		return csstatus.ROLE_TRADE_ITEM_OVERFLOW

	def si_checkPetTrading( self, dstEntity ):
		"""
		检查是否允许接受交易

		@return: bool
		"""
		if self.si_myMoney > self.money:
			return csstatus.ROLE_TRADE_FAILED_MONEY_CHANGED

		if self.testAddMoney( self.si_dstMoney ) > 0:	# 可以获得大于csstatus.ROLE_TRADE_MONEY_OVERFLOW，重上线会扣除，暂时不改，wsf
			return csstatus.ROLE_TRADE_MONEY_OVERFLOW

		# 不能超过宠物的数量最大上限，这个上限应该在coconst中定义,wsf
		if self.pcg_getPetCount() - int( self.si_myPetDBID and 1 or 0 ) + int( self.si_dstPetDBID and 1 or 0 ) > self.pcg_getKeepingCount():
			ERROR_MSG( "玩家宠物超过上限." )
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
		玩家主动取消交易。
		"""
		if srcEntityID != self.id:
			HACK_MSG( "非法使用者, src(%i) calling dst(%i) method" % ( srcEntityID, self.id ) )
			return

		dstEntity = BigWorld.entities.get( self.si_targetID )
		self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )	# 注意，dstEntity有可能是None

	def si_resetData( self ):
		"""
		重置数据为未交易前状态
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
		清除用于物品交易的数据
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
		清除用于交易的宠物，在BASE宠物交易完成后调用此方法设置si_myPetDBID
		避免在异步情况下，交易成功，BASE还没删除此宠物，就能够进行召唤宠物或变换宠物数据的操作。
		"""
		if self.si_myPetDBID or self.si_dstPetDBID:
			self.base.si_clearSwapPet()
		self.si_myPetDBID = 0
		self.si_dstPetDBID = 0

	def isPetInSwap( self, petDBID ):
		"""
		判断dbid为petDBID的宠物是否在交易中。提供给petCage使用
		"""
		return self.si_myPetDBID == petDBID


	def si_trading( self ):
		"""
		Define method.
		玩家交易进行，交换物品、金钱、宠物，交易完毕重置数据。
		目前允许物品和宠物同时进行交易
		"""
		targetPlayer = BigWorld.entities.get( self.si_targetID )
		if self.si_dstPetDBID or self.si_myPetDBID:
			self.base.si_petTrading()	# 存在宠物交易，通知base进行宠物交易
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
		
		self.writeToDB()	# 玩家间交易完成后需立即保存玩家数据到数据库防止回档造成交易不成功，12:57 2009-10-29，wsf
		self.si_resetData()

	def onMoneyChanged( self, value, reason ):
		"""
		玩家金钱改变了
		"""
		if self.si_myState != csdefine.TRADE_SWAP_DEFAULT and self.si_myState != csdefine.TRADE_SWAP_LOCKAGAIN:	# 正在交易状态花费了金钱，那么退出交易
			try:
				dstEntity = BigWorld.entities[ self.si_targetID ]
			except KeyError:
				dstEntity = None
			self.si_changeState( csdefine.TRADE_SWAP_DEFAULT, dstEntity )


#
# $Log: not supported by cvs2svn $
# Revision 1.25  2008/07/01 03:06:24  zhangyuxing
# 增加物品进入背包返回失败的状态
#
# Revision 1.24  2008/06/20 06:59:32  wangshufeng
# 限制双方交易距离的函数修改flatDistTo -> distTo
#
# Revision 1.23  2008/05/31 03:00:39  yangkai
# 物品获取接口改变
#
# Revision 1.22  2008/05/30 05:47:00  wangshufeng
# 修正一处代码错误
#
# Revision 1.21  2008/05/30 03:01:33  yangkai
# 装备栏调整引起的部分修改
#
# Revision 1.20  2008/05/28 08:39:08  wangshufeng
# 分离宠物交易和物品交易，相应调整代码
# 状态机的状态增加，加入了 宠物交易邀请状态 和 宠物交易等待状态
# 并调整状态转换规则。
#
# Revision 1.19  2008/05/27 02:38:15  wangshufeng
# 修正si_onDstStateChanged函数中造成死循环的一处代码错误
#
# Revision 1.18  2008/05/26 09:42:05  wangshufeng
# method modify:si_onDstStateChanged,修正一处代码错误
#
# Revision 1.17  2008/03/19 02:48:23  wangshufeng
# 新版玩家交易系统
#

#
