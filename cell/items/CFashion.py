# -*- coding: gb18030 -*-

from bwdebug import *
import csdefine
from CEquip import CEquip

class CFashion( CEquip ):
	"""
	ʱװ
	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def getFDict( self ):
		"""
		Virtual Method
		��ȡ����Ч�������Զ������ݸ�ʽ
		���ڷ��͵��ͻ���
		return INT32
		"""
		return self.model()

	def wield( self, owner, update = True ):
		"""
		װ��ʱװ

		@param  owner: ʱװӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    True װ���ɹ���False װ��ʧ��
		@return:    BOOL
		"""
		if not CEquip.wield( self, owner, update ):
			return False
		if update: owner.calcDynamicProperties()
		return True

	def unWield( self, owner, update = True ):
		"""
		ж��ʱװ

		@param  owner: ʱװӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    ��
		"""
		# ���û��װ��Ч������unwield
		if not self.isAlreadyWield(): return
		CEquip.unWield( self, owner, update )
		return True