# -*- coding: gb18030 -*-

# $Id: CKaStone.py,v 1.3 2008-05-17 11:42:42 huangyongwei Exp $

"""
����ʯ������
"""
from CEquip import *
from bwdebug import *
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine

class CKaStone( CEquip ):
	"""
	����ʯ������
	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def getProDescription( self, reference ):
		"""
		virtual method
		��ȡװ��ר��������Ϣ
		"""
		CEquip.getProDescription( self, reference )
		attrMap = ItemAttrClass.m_itemAttrMap
		ka_count = attrMap["ka_count"].description( self, reference )
		self.desFrame.SetDescription( "eq_hardiness" , ka_count )

	def set( self, attrName, value, owner = None ):
		"""
		���ö�̬����

		@param owner: ���ֵΪNone����ֻ�������������ֵ(ֻ��)ΪRoleʵ���������entity.client.onItemAttrUpdated()����
		@return: None
		"""
		CEquip.set( self, attrName, value, owner )
		if "ka_count" == attrName:
			ka_count = self.query( "ka_count", 0 )
			if ka_count >= self.query( "ka_totalCount", 1 ):
				#���յĻ�������
				self.onSuckKaFull()

	def onSuckKaFull( self ):
		"""
		���յĻ�������
		���������һЩ���� ��:ͼ�귢��ȹ���
		"""
		pass

	def isFull( self ):
		"""
		�����Ƿ�������
		"""
		return self.query( "ka_count", 0 ) >= self.query( "ka_totalCount", 1 )
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/02/21 03:14:27  kebiao
# add: isFull( self )
#
# Revision 1.1  2008/02/20 08:33:16  kebiao
# no message
#
#
