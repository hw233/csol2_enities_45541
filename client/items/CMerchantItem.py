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

class CMerchantItem( CItemBase ):
	"""
	��Ƭ��Ʒ
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def canGive( self ):
		"""
		�ж��Ƿ��ܸ�(��������֮�����Ʒ����)
		������ƷΪ��״̬ʱ������Ʒ���ܽ���

		@return: bool
		@rtype:  bool
		"""
		return False

