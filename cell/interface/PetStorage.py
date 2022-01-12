# -*- coding: gb18030 -*-
#
# $Id: PetStorage.py,v 1.10 2008-06-19 07:27:14 fangpengjun Exp $

"""
This module implements the pet entity.

2007/07/01: writen by huangyongwei
2007/10/24: according to new version documents, it is rewriten by huangyongwei
"""

import time
import csdefine
import csconst
import csstatus
from PetFormulas import formulas

class PetStorage :
	def __init__( self ) :
		pass


	# ----------------------------------------------------------------
	# public methods for npc dialog
	# ----------------------------------------------------------------
	def pst_dlgCanBeHired( self ) :
		return self.__status != csdefine.PET_STORE_STATUS_HIRING

	def pst_dlgCanBeOpen( self ) :
		return self.__status != csdefine.PET_STORE_STATUS_NONE

	def pst_dlgOpen( self, npcEntity ) :
		self.base.pst_open()

	# ----------------------------------------------------------------
	# define methods
	# ----------------------------------------------------------------
	def pst_onEndOperating( self ) :
		"""
		defined method
		�� base ���ý�������
		"""
		self.pcg_releaseOperating_()

	def pst_onStatusChanged( self, status ) :
		"""
		defined method
		�� base ���øı�ֿ�״̬
		"""
		self.__status = status


	# ----------------------------------------------------------------
	# exposed methods
	# ----------------------------------------------------------------
	def pst_storePet( self, srcEntityID, dbid ) :
		"""
		</Exposed>
		������ŵ��ֿ�
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if not self.pcg_lockOperation_() : return
		if self.pcg_isTradingPet_( dbid ) : return
		self.base.pst_storePet( dbid )						# ע���������ص���pst_onHired

	def pst_takePet( self, srcEntityID, dbid ) :
		"""
		<Exposed/>
		��ȡ����
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if not self.pcg_lockOperation_() : return
		if self.pcg_isTradingPet_( dbid ) : return
		if self.pcg_isFull() :
			self.statusMessage( csstatus.PET_TAKE_PET_FAIL_FULL )
			self.pst_onEndOperating()
		else :
			self.base.pst_takePet( dbid )					# ע���������ص���pst_onEndOperating
