# -*- coding: gb18030 -*-

# $Id: CItemPicture.py,v 1.1 2008-08-04 06:30:04 zhangyuxing Exp $

from CItemBase import CItemBase
import ItemAttrClass
from bwdebug import *



from ItemSystemExp import EquipQualityExp
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from gbref import rds
import TextFormatMgr
import CItemDescription

class CItemPicture( CItemBase ):
	"""
	��Ƭ��Ʒ
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def getProDescription( self, reference ):
		"""
		������������Ҫ����client��

		@param reference: ���entity,��ʾ��˭����Ϊ���������Ĳ�����
		@type  reference: Entity
		@return:          ��Ʒ���ַ�������
		@rtype:           ARRAY of str
		"""
		attrMap = ItemAttrClass.m_itemAttrMap

		# ���͵��¼��Ϣ
		teleportRes = attrMap["ch_teleportRecord"].description( self, reference )
		if teleportRes != "":
			teleportRes = PL_Font.getSource( teleportRes, fc = ( 0, 255, 0 ) )
			self.desFrame.SetDescription( "ch_teleportRecord", teleportRes )

		useDegreeDes = attrMap["useDegree"].description( self, reference )
		if useDegreeDes != "":
			self.desFrame.SetDescription( "useDegree", useDegreeDes )

#
# $Log: not supported by cvs2svn $
