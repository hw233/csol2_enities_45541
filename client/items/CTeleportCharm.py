# -*- coding: gb18030 -*-
"""
定向符物品类。
"""
import ItemAttrClass
from CItemBase import CItemBase
from ItemSystemExp import EquipQualityExp
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from config.client.labels.items import lbs_CTeleportCharm

class CTeleportCharm( CItemBase ):
	"""
	定向符物品类。
	"""
	def __init__( self, srcData ):
		"""
		@param srcData: 物品的原始数据
		"""
		CItemBase.__init__( self, srcData )

	def description( self, reference ):
		"""
		产生描述

		@param reference: 玩家entity,表示以谁来做为生成描述的参照物
		@type  reference: Entity
		@return:          物品的字符串描述
		@rtype:           ARRAY of str
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		# 显示物品名字，根据物品的品质决定物品名字的颜色
		nameDes = attrMap["name"].description( self, reference )
		nameDes = PL_Font.getSource( nameDes, fc = EquipQualityExp.instance().getColorByQuality( self.getQuality() ) )
		self.desFrame.SetDescription("name" , nameDes)
		# 物品类型
		desType = attrMap["type"].description( self, reference )
		self.desFrame.SetDescription( "type", desType )
		# 需求声望
		reqCredits = attrMap["reqCredit"].descriptionDict( self, reference )
		if reqCredits:
			reqCreditsDes = reqCredits.keys()
			for index in xrange( len( reqCreditsDes) ):
				if not reqCredits[ reqCreditsDes[index] ]:
					reqCreditsDes[ index ] = PL_Font.getSource( reqCreditsDes[ index ] , fc = "c3" )
			self.desFrame.SetDesSeveral( "reqCredit", reqCreditsDes )
		#是否绑定
		desBind = attrMap["bindType"].description( self, reference )
		if desBind != "":
			self.desFrame.SetDescription( "bindType", desBind )
		#是否唯一
		only = attrMap["onlyLimit"].description( self, reference )
		if only == 1:
			self.desFrame.SetDescription( "onlyLimit" , lbs_CTeleportCharm[1] )
		# 是否可出售
		if not self.canSell():
			canNotSell = PL_Font.getSource( lbs_CTeleportCharm[2] , fc = "c6" )
			self.desFrame.SetDescription( "canNotSell" , canNotSell )

		# 定向符的坐标信息
		teleportRes = attrMap["ch_teleportRecord"].description( self, reference )

		# 取得额外的描述1
		des1 = attrMap["describe1"].description( self, reference )
		if des1 != "":
			des1 += teleportRes
			des1 = PL_Font.getSource( des1, fc = "c4" )
			self.desFrame.SetDescription( "describe1", des1 )
		# 取得额外的描述2
		des2 = attrMap["describe2"].description( self, reference )
		if des2 != "":
			des2 = PL_Font.getSource( des2, fc = "c40" )
		#	if des1 != "": des2 = g_newLine + des2
			self.desFrame.SetDescription( "describe2", des2 )
		# 取得额外的描述3
		des3 = attrMap["describe3"].description( self, reference )
		if des3 != "":
			des3 = PL_Font.getSource( des3, fc = "c24" )
		#	if des1 != "" or des2 != "": des3 = g_newLine + des3
			self.desFrame.SetDescription( "describe3", des3 )

		return self.desFrame.GetDescription()