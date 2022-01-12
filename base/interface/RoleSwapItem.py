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
		self.dstSwapPetEpitom = None	# ����һ��ֻ�ܽ���һֻ����
		self.si_targetID = 0


	def si_changeMyPet( self, petDBID, dstBaseEntity ):
		"""
		Define method.
		�ı伺�����ڽ��׵ĳ���ı��Ҫ֪ͨ�Է�

		@param petDBID:	���ڽ��׵ĳ���dbid
		@type petDBID:	DATABASE_ID
		@param dstBaseEntity:	���׶����base mailbox
		@type dstBaseEntity:	MAILBOX
		"""
		if self.si_myPetDBID == petDBID:
			return

		self.si_myPetDBID = petDBID
		dstBaseEntity.si_dstChangePet( self.pcg_getPetEpitome( petDBID ), self.id )	# �Ѹı�ĳ������ݷ��͸��Է�


	def si_removeMyPet( self, dstBaseEntity ):
		"""
		Define method.
		�ı伺�����ڽ��׵ĳ���ı��Ҫ֪ͨ�Է�

		@param dstBaseEntity:	���׶����base mailbox
		@type dstBaseEntity:	MAILBOX
		"""
		self.si_myPetDBID = 0
		dstBaseEntity.si_dstRemovePet( self.id )


	def si_dstChangePet( self, epitome, dstEntityID ):
		"""
		Define method.
		�Է��ı����ڽ��׵ĳ���

		param epitome: ��������
		type epitome: 	PET_EPITOME
		param dstEntityID: ���׶����entity id
		type dstEntityID: 	OBJECT_ID
		"""
		if self.si_targetID != dstEntityID:		# ȷ�����׶�����ȷ���ܽ�������Ĳ���
			HACK_MSG( "id( %i )�Ľ��׶���( %i )����ȷ��" % self.id, dstEntityID )
			return
		self.dstSwapPetEpitom = epitome
		self.client.si_dstChangePet( epitome )	# ֪ͨ�ͻ���


	def si_dstRemovePet( self, dstEntityID ):
		"""
		Define method.
		�Է��ı����ڽ��׵ĳ���

		param dstEntityID: ���׶����entity id
		type dstEntityID: 	OBJECT_ID
		"""
		if self.si_targetID != dstEntityID:		# ȷ�����׶�����ȷ���ܽ�������Ĳ���
			HACK_MSG( "id( %i )�Ľ��׶���( %i )����ȷ��" % self.id, dstEntityID )
			return
		self.dstSwapPetEpitom = None

		self.client.si_dstRemovePet()	# ֪ͨ�ͻ���

	def si_clearSwapPet( self ):
		"""
		Define method.
		������ｻ������
		"""
		self.si_myPetDBID = 0
		self.dstSwapPetEpitom = None	# ����һ��ֻ�ܽ���һֻ����
		self.si_targetID = 0

	def si_petTrading( self ):
		"""
		Define method.
		����Է����ɾ���Լ��ĳ���
		"""
		def callback( epitome, result ):
			"""
			resultΪд���ݿ�Ľ������
			0��ʾҪ���µļ�¼������
			1��ʾ�ɹ��������ݿ�
			-1��ʾ�������ݿ�ʧ��
			"""
			if result == 1:
				pass
			if result == 0:
				pass
			if result == -1:
				ERROR_MSG( "����pet( %i )��ownerDBIDΪ( %i )ʧ��." % ( epitome.databaseID, self.databaseID ) )

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
		���ý��׶����Ա����޸Ľ������ݵ�ʱ��Ƚϣ����ڽ��׵Ķ�������޸Ľ�������
		���si_targetIDΪ0,��ô�˳����ｻ��

		param si_targetID: ���׶����entity id
		type si_targetID: 	OBJECT_ID
		"""
		self.si_targetID = si_targetID

		# �ı佻�׶�������е�����Ҫ����
		self.si_myPetDBID = 0
		self.dstSwapPetEpitom = None
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/03/19 02:50:59  wangshufeng
# �°���ҽ���ϵͳ
#

#
#
