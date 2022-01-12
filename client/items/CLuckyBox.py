# -*- coding: gb18030 -*-

import csconst
import csstatus
import ItemAttrClass

from CItemBase import CItemBase
from ItemSystemExp import EquipQualityExp
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from config.client.labels.items import lbs_CLuckyBox

class CLuckyBox( CItemBase ):
	"""
	天降宝盒，招财、进宝
	"""
	def __init__( self, srcData ):
		"""
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
		# 显示物品名字
		nameDes = attrMap["name"].description( self, reference )
		nameDes = PL_Font.getSource( nameDes, fc = EquipQualityExp.instance().getColorByQuality( self.getQuality() ) )
		self.desFrame.SetDescription("name" , nameDes)
		#是否绑定
		desBind = attrMap["bindType"].description( self, reference )
		if desBind != "":
			self.desFrame.SetDescription("bindType", desBind)
		# 唯一性
		only = attrMap["onlyLimit"].description( self, reference )
		if only == 1:
			self.desFrame.SetDescription( "onlyLimit" , lbs_CLuckyBox[1] )
		# 是否可出售
		if not self.canSell():
			canNotSell = PL_Font.getSource( lbs_CLuckyBox[2], fc = "c6" )
			self.desFrame.SetDescription( "canNotSell" , canNotSell )
		# 取得额外的描述1
		des1 = attrMap["describe1"].description( self, reference )
		if des1 != "":
			des1 = PL_Font.getSource( des1, fc = "c4" )
			self.desFrame.SetDescription( "describe1", des1 )
		# 取得额外的描述2
		des2 = attrMap["describe2"].description( self, reference )
		if des2 != "":
			des2 = PL_Font.getSource( des2, fc = "c40" )
			des2 = des2 % self.getLevel()
		#	if des1 != "": des2 = g_newLine + des2
			self.desFrame.SetDescription( "describe2", des2 )
		# 取得额外的描述3
		des3 = attrMap["describe3"].description( self, reference )
		if des3 != "":
			des3 = PL_Font.getSource( des3, fc = "c24" )
		#	if des1 != "" or des2 != "": des3 = g_newLine + des3
			self.desFrame.SetDescription( "describe3", des3 )

		return self.desFrame.GetDescription()

	def checkUse( self, owner ):
		"""
		天降宝盒对玩家的使用限制
		"""
		checkResult = CItemBase.checkUse( self, owner )
		if checkResult != csstatus.SKILL_GO_ON:
			return checkResult

		if self.getLevel() > owner.level + csconst.LUCKY_BOX_USE_LEVEL_CHECK:
			return csstatus.CIB_LUCKYBOX_CANT_USE_LEVEL_LACK

		return csstatus.SKILL_GO_ON