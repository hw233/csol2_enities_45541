# -*- coding: gb18030 -*-
#
# $Id: RoleSwapItem.py,v 1.2 2008-08-21 08:36:41 qilan Exp $

import BigWorld

from Function import Functor
from bwdebug import *
import csstatus
import csdefine

class RoleSwapItem:
	"""
	"""
	def __init__( self ):
		"""
		"""
		self.si_myPetDBID = 0
		self.dstSwapPetEpitom = None	# 现在一次只能交易一只宠物
		self.si_targetID = 0


	def si_changeMyPet( self, petDBID, dstBaseEntity ):
		"""
		Define method.
		改变己方用于交易的宠物，改变后要通知对方

		@param petDBID:	用于交易的宠物dbid
		@type petDBID:	DATABASE_ID
		@param dstBaseEntity:	交易对象的base mailbox
		@type dstBaseEntity:	MAILBOX
		"""
		if self.si_myPetDBID == petDBID:
			return

		self.si_myPetDBID = petDBID
		dstBaseEntity.si_dstChangePet( self.pcg_getPetEpitome( petDBID ), self.id )	# 把改变的宠物数据发送给对方


	def si_removeMyPet( self, dstBaseEntity ):
		"""
		Define method.
		改变己方用于交易的宠物，改变后要通知对方

		@param dstBaseEntity:	交易对象的base mailbox
		@type dstBaseEntity:	MAILBOX
		"""
		self.si_myPetDBID = 0
		dstBaseEntity.si_dstRemovePet( self.id )


	def si_dstChangePet( self, epitome, dstEntityID ):
		"""
		Define method.
		对方改变用于交易的宠物

		param epitome: 宠物数据
		type epitome: 	PET_EPITOME
		param dstEntityID: 交易对象的entity id
		type dstEntityID: 	OBJECT_ID
		"""
		if self.si_targetID != dstEntityID:		# 确定交易对象正确才能进行下面的操作
			HACK_MSG( "id( %i )的交易对象( %i )不正确。" % self.id, dstEntityID )
			return
		self.dstSwapPetEpitom = epitome
		self.client.si_dstChangePet( epitome )	# 通知客户端


	def si_dstRemovePet( self, dstEntityID ):
		"""
		Define method.
		对方改变用于交易的宠物

		param dstEntityID: 交易对象的entity id
		type dstEntityID: 	OBJECT_ID
		"""
		if self.si_targetID != dstEntityID:		# 确定交易对象正确才能进行下面的操作
			HACK_MSG( "id( %i )的交易对象( %i )不正确。" % self.id, dstEntityID )
			return
		self.dstSwapPetEpitom = None

		self.client.si_dstRemovePet()	# 通知客户端

	def si_clearSwapPet( self ):
		"""
		Define method.
		清除宠物交易数据
		"""
		self.si_myPetDBID = 0
		self.dstSwapPetEpitom = None	# 现在一次只能交易一只宠物
		self.si_targetID = 0

	def si_petTrading( self ):
		"""
		Define method.
		加入对方宠物，删除自己的宠物
		"""
		def callback( epitome, result ):
			"""
			result为写数据库的结果参数
			0表示要更新的记录不存在
			1表示成功操作数据库
			-1表示操作数据库失败
			"""
			if result == 1:
				pass
			if result == 0:
				pass
			if result == -1:
				ERROR_MSG( "更改pet( %i )的ownerDBID为( %i )失败." % ( epitome.databaseID, self.databaseID ) )

		if self.dstSwapPetEpitom:
			self.pcg_addPet_( self.dstSwapPetEpitom, csdefine.ADDPET_PETTRADING )
			self.dstSwapPetEpitom.updateAttr( "ownerDBID", self.databaseID, self, Functor( callback, self.dstSwapPetEpitom ) )
			self.cell.si_clearSwapPet()
			self.statusMessage( csstatus.ROLE_TARGET_PET_GET, self.dstSwapPetEpitom.getDisplayName() )

		if self.si_myPetDBID != 0:
			epitom = self.pcg_getPetEpitome( self.si_myPetDBID )
			self.statusMessage( csstatus.ROLE_TARGET_PET_LOST, epitom.getDisplayName() )
			self.pcg_removePet_( self.si_myPetDBID,csdefine.DELETEPET_PETTRADING )


	def si_setTargetID( self, si_targetID ):
		"""
		Define method.
		设置交易对象，以便在修改交易数据的时候比较，正在交易的对象才能修改交易数据
		如果si_targetID为0,那么退出宠物交易

		param si_targetID: 交易对象的entity id
		type si_targetID: 	OBJECT_ID
		"""
		self.si_targetID = si_targetID

		# 改变交易对象后，所有的数据要重置
		self.si_myPetDBID = 0
		self.dstSwapPetEpitom = None
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/03/19 02:50:59  wangshufeng
# 新版玩家交易系统
#

#
#
