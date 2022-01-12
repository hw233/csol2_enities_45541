# -*- coding: gb18030 -*-

# $Id: CKaStone.py,v 1.2 2008-02-21 06:10:53 kebiao Exp $

"""
����ʯ������
"""
from CEquip import *

class CKaStone( CEquip ):
	"""
	����ʯ������
	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )
	
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
		if not self.isFull():
			owner.kaStone_SpellID = self.query( "spell" )
		return True

	def unWield( self, owner, update = True ):
		"""
		ж��װ��

		@param  owner: ����ӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    ��
		"""
		owner.kaStone_SpellID = 0
		CEquip.unWield( self, owner, update )
		
	def _checkHardiness( self ):
		"""
		��鵱ǰ�;ö�

		@return: ����0�򲻴�����������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		return True
		
	def isFull( self ):
		"""
		�����Ƿ�������
		"""
		return self.query( "ka_count", 0 ) >= self.query( "ka_totalCount", 1 )
		
	def addKa( self, owner, kaVal ):
		"""
		��ӻ���
		"""
		self.set( "ka_count", self.query( "ka_count", 0 ) + kaVal, owner )
		self.onKaValueChanged( owner )
	
	def onKaValueChanged( self, owner ):
		"""
		����ֵ���ı���
		"""
		if self.isFull():
			owner.kaStone_SpellID = 0
			
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/02/20 08:32:19  kebiao
# no message
#
#
