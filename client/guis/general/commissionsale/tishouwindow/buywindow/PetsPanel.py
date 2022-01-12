# -*- coding: gb18030 -*-

from guis import *
from guis.general.vendwindow.buywindow.PetsPanel import BasePetsPanel


class PetsPanel( BasePetsPanel ) :

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ):
		self.triggers_["EVT_ON_TISHOU_PET_SELLED"] = self.onRemovePet_ 		# ��������ص�
		self.triggers_["EVT_ON_UPDATE_SELLED_PET"] = self.onUpdatePetPrice_ 	# ���³���۸�
		self.triggers_["EVT_ON_TISHOU_RECEIVE_PETEPITOME"] = self.__onReceivePet
		BasePetsPanel.registerTriggers_( self )

	def buyPet_( self ):
		tishouNPC = self.pyBinder.trapEntity
		if tishouNPC is not None :
			selPet = self.pyPagesPanel_.selItem
			if selPet is None :
				print "-------->>> It is stange that none pet is selected..."
				return
			if not tishouNPC.tsState :
				# "��һ�û��ʼ��̯��"
				self.showMsg_( 0x0ae1 )
				return
			tishouNPC.cell.buyTSPet( selPet.databaseID, selPet.vendSellPrice )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onReceivePet( self, epitome, price, ownerDBID ) :
		"""
		���յ�������������
		"""
		tishouNPC = self.pyBinder.trapEntity
		if tishouNPC is None or tishouNPC.ownerDBID != ownerDBID : return	# NPC�����ڻ��߲��Ǹ�NPC�ļ�����Ʒ
		for pEpt in self.pyPagesPanel_.items :							# �����ظ���Ʒ
			if pEpt.databaseID == epitome.databaseID :
				return
		epitome.vendSellPrice = price
		self.pyPagesPanel_.addItem( epitome )
		self.pyStNumber_.text = str( self.pyPagesPanel_.itemCount )

	def __queryTSPetInfo( self ) :
		"""
		�������������۵ĳ�������
		"""
		self.reset()
		def queryInfo() :
			tishouNPC = self.pyBinder.trapEntity
			if tishouNPC is not None :
				tishouNPC.cell.queryTSPets()
		if self.visible :
			queryInfo()
		else :
			BigWorld.callback( 0.5, queryInfo )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onParentShow( self ) :
		self.__queryTSPetInfo()
