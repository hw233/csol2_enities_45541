# -*- coding: gb18030 -*-
"""
定向蛀虫
"""
import ItemAttrClass
from gbref import rds
from CItemBase import CItemBase
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from config.client.labels.items import lbs_CTeleport


class CTeleport( CItemBase ):
	"""
	定向蛀虫
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def getProDescription( self, reference ):
		"""
		virtual method
		获取物品专有描述信息
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		# 显示物品分类，等级需求
		desReqlevel = attrMap["reqLevel"].description( self, reference )
		if reference.level < self.query("reqLevel", 0):
			desReqlevel = rds.textFormatMgr.makeDestStr( desReqlevel ,rds.textFormatMgr.reqLevelCode )
			desReqlevel = rds.textFormatMgr.ItemText( self, desReqlevel ).replaceDesReqlevelCode()
			desReqlevel = PL_Font.getSource( desReqlevel, fc = ( 255, 0, 0 ) )
			desReqlevel += PL_Font.getSource( fc = self.defaultColor )
		self.desFrame.SetDescription("itemreqLevel" , desReqlevel)
		useDegreeDes = attrMap["useDegree"].description( self, reference )
		if useDegreeDes != "":
			self.desFrame.SetDescription( "useDegree", useDegreeDes )

		# 传送点记录信息
		teleportRes = attrMap["ch_teleportRecord"].description( self, reference )
		if teleportRes != "":
			teleportRes = PL_Font.getSource( teleportRes, fc = ( 0, 255, 0 ) )
			teleportRes = lbs_CTeleport[1] + teleportRes
			self.desFrame.SetDescription( "ch_teleportRecord",  teleportRes )
