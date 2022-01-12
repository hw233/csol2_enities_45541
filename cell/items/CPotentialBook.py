# -*- coding: gb18030 -*-

from bwdebug import *
from CEquip import CEquip
import csdefine
import csstatus
import csconst
import ItemTypeEnum

class CPotentialBook( CEquip ):
	"""
	Ǳ���� by ����
	"""
	def __init__( self, srcData ):
		"""
		"""
		CEquip.__init__( self, srcData )
		
	def getPotential( self ):
		"""
		�������Ǳ��
		"""
		temp = self.query( "param2" )
		if temp is None:
			return 0
		return int( temp )
		
	def getPotentialMax( self ):
		"""
		����������Ǳ��
		"""
		return int( self.queryTemp( "param1", 0 ) )
		
	def getPotentialRate( self ):
		"""
		���Ǳ�ܸ�����
		"""
		return float( self.queryTemp( "param3", 0 ) )
		
	def isPotentialMax( self ):
		"""
		Ǳ�����Ƿ�����
		"""
		return self.getPotential() >= self.getPotentialMax()
		
	def use( self, owner, target ):
		"""
		ʹ��Ǳ������
		"""
		if self.getLevel() > target.getLevel():
			return csstatus.KIT_EQUIP_CANT_POTENTIAL_BOOK
		pot = self.getPotential()
		if target.potential + pot > csconst.ROLE_POTENTIAL_UPPER:
			return csstatus.KIT_EQUIP_POTENTIAL_BOOK_LIM
		target.addPotential( pot )
		owner.removeItem_( self.getOrder(), reason = csdefine.DELETE_ITEM_POTENTIAL_BOOK )
		target.statusMessage( csstatus.KIT_EQUIP_POTENTIAL_BOOK_USED, pot )
		return csstatus.SKILL_GO_ON
		
	def addPotential( self, value, owner ):
		"""
		�����鱾Ǳ�ܵ�
		"""
		if self.isPotentialMax():
			return
		pot = self.getPotential()
		potMax = self.getPotentialMax()
		rate = self.getPotentialRate()
		value *= rate
		if ( pot + value ) > potMax:
			value = potMax - pot
		pot += value
		self.setPotential( pot, owner )
		
	def setPotential( self, value, owner ):
		"""
		�����鱾Ǳ�ܵ�
		"""
		self.set( "param2", value, owner )
		
	def getFDict( self ):
		"""
		Virtual Method
		��ȡ����Ч�������Զ������ݸ�ʽ
		���ڷ��͵��ͻ���
		return INT32
		"""
		return 0
		
	def wield( self, owner, update = True ):
		"""
		װ������

		@param  owner: ����ӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    True װ���ɹ���False װ��ʧ��
		@return:    BOOL
		"""
		if not CEquip.wield( self, owner, update ):
			return False

	def unWield( self, owner, update = True ):
		"""
		ж��װ��

		@param  owner: ����ӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    ��
		"""
		CEquip.unWield( self, owner, update )