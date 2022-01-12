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
	照片物品
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def getProDescription( self, reference ):
		"""
		产生描述，主要用于client。

		@param reference: 玩家entity,表示以谁来做为生成描述的参照物
		@type  reference: Entity
		@return:          物品的字符串描述
		@rtype:           ARRAY of str
		"""
		attrMap = ItemAttrClass.m_itemAttrMap

		# 传送点记录信息
		teleportRes = attrMap["ch_teleportRecord"].description( self, reference )
		if teleportRes != "":
			teleportRes = PL_Font.getSource( teleportRes, fc = ( 0, 255, 0 ) )
			self.desFrame.SetDescription( "ch_teleportRecord", teleportRes )

		useDegreeDes = attrMap["useDegree"].description( self, reference )
		if useDegreeDes != "":
			self.desFrame.SetDescription( "useDegree", useDegreeDes )

#
# $Log: not supported by cvs2svn $
