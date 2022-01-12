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
	照片物品
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def canGive( self ):
		"""
		判断是否能给(玩家与玩家之间的物品交换)
		当该物品为绑定状态时，该物品不能交易

		@return: bool
		@rtype:  bool
		"""
		return False

