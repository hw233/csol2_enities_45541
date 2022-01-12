# -*- coding: gb18030 -*-

# $Id: CSuperDrug.py,v 1.1 2008-08-30 02:39:35 yangkai Exp $

from CItemBase import CItemBase
import ItemAttrClass
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine

class CSuperDrug( CItemBase ):
	"""
	���д����ֵ��ʹ�ö�εĲ�ҩ
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def getMaxPoint( self ):
		"""
		��ȡ��ҩ����ָܻ�����
		"""
		return self.query( "sd_maxPoint", 0 )

	def getCurrPoint( self ):
		"""
		��ȡ��ҩ��ǰ�ָܻ��ĵ���
		"""
		return int(self.query( "sd_currPoint", 0 ))

	def getProDescription( self, reference ):
		"""
		virtual method
		��ȡ��Ʒר��������Ϣ
		"""
		CItemBase.getProDescription( self, reference )
		attrMap = ItemAttrClass.m_itemAttrMap
		pointDes = attrMap["sd_currPoint"].description( self, reference )
		pointDes = PL_Font.getSource( pointDes, fc = ( 0, 255, 0 ) )
		self.desFrame.SetDescription("eq_hardiness" , pointDes)

# $Log: not supported by cvs2svn $
