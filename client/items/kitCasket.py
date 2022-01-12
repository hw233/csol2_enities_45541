# -*- coding: gb18030 -*-

# $Id: kitCasket.py,v 1.4 2008-10-28	huangdong Exp $

"""
背包类基础模块
"""

from CItemBase import *
from config.client.labels.items import lbs_kitCasket

class kitCasket( CItemBase ):
	"""
	神机匣

	@ivar maxSpace: 默认最大空间
	@type maxSpace: INT8
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )


	def getProDescription( self, reference ):
		"""
		virtual method
		获取物品专有描述信息
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		# 显示物品分类，等级需求
		desType = attrMap["type"].description( self, reference )
		desReqlevel = attrMap["reqLevel"].description( self, reference )
		if reference.level < self.query("reqLevel", 0):
			desReqlevel = rds.textFormatMgr.makeDestStr( desReqlevel ,rds.textFormatMgr.reqLevelCode )
			desReqlevel = TextFormatMgr.ItemText( self, desReqlevel ).replaceDesReqlevelCode()
			desReqlevel = PL_Font.getSource( desReqlevel, fc = ( 255, 0, 0 ) )
			desReqlevel += PL_Font.getSource( fc = self.defaultColor )
		self.desFrame.SetDescription("type" , desType)
		self.desFrame.SetDescription("itemreqLevel" , desReqlevel)

		useDegree = self.getUseDegree()
		cfc = "c3" if useDegree == 0 else "c6"
		tips = PL_Font.getSource( "%s: %i" % ( lbs_kitCasket[1], useDegree ), fc = cfc )
		self.desFrame.SetDescription( "useDegree", tips )
