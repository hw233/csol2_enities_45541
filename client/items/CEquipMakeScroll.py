# -*- coding: gb18030 -*-

# $Id: CEquipMakeScroll.py,v 1.1 2008-10-23  huangdong Exp $


import ItemAttrClass
import csconst
from bwdebug import *
from CEquip import CEquip
from ItemDataList import ItemDataList
from ItemSystemExp import EquipQualityExp
from ItemSystemExp import SpecialComposeExp

from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.richtext_plugins.PL_Align import PL_Align

from config.client.labels.items import lbs_CEquipMakeScroll
import utils


class CEquipMakeScroll( CEquip ):
	"""
	制作卷
	"""
	"""
	具有大额数值能使用多次的补药
	"""

	def __init__( self, srcData ):
		"""
		"""
		CEquip.__init__( self, srcData )

	def getProDescription( self, reference ):
		"""
		virtual method
		获取物品专有描述信息
		"""
		CEquip.getProDescription( self, reference )
		des = ""
		attrMap = ItemAttrClass.m_itemAttrMap
		#获取需要的材料
		materials = attrMap["em_material"].descriptionList( self, reference )

		if materials is None:
			des = lbs_CEquipMakeScroll[1]
		else:
			for id, count in materials:
				#获取描述语言 如 五级铁x3
				if count == 0:continue
				tempdes = ItemDataList._instance.id2name(id) + "x%s"%count
				#获取材料品质
				quality = ItemDataList._instance.id2quality(id)
				#设定颜色
				tempdes = PL_Font.getSource( "%s%s"%( tempdes, g_newLine ), fc = EquipQualityExp.instance().getColorByQuality( quality ) )
				des += tempdes

		introduce = PL_Font.getSource( lbs_CEquipMakeScroll[2], fc = "c8" )
		self.desFrame.SetDesSeveral( "em_material" , [ [ introduce ], [ des ] ] )

		money = self.getPrice() *csconst.INVBUYPERCENT
		if money > int(money):
			money = int(money) + 1
		money = int(money)
		msg = lbs_CEquipMakeScroll[3] + utils.currencyToViewText( money )
		msg = PL_Align.getSource( lineFlat = "M" ) + msg + PL_Align.getSource( "L" )

		itemid = SpecialComposeExp._instance.getDstItemID( self.id )	#获取合成后的物品ID
		item   = ItemDataList._instance.createDynamicItem( itemid )		#动态加载该物品
		if not item:
			ERROR_MSG("can not find item %s,CEquipMakeScroll id = %s" % ( itemid, self.id)  )
			return
		des2 = item.description( reference )							#获取合成后物品的描述
		des2.insert( 0,[ g_newLine + PL_Font.getSource( lbs_CEquipMakeScroll[4], fc = "c8" ) ] )
		des2.insert( 0, [ msg ] )

		"""	策划要求不显示合成物品的价格,先只是注释掉，避免他们反悔
		money = item.getPrice() *csconst.INVBUYPERCENT
		if money > int(money):
			money = int(money) + 1
		money = int(money)
		msg = lbs_CEquipMakeScroll[3] + utils.currencyToViewText( money )
		msg = PL_Align.getSource( lineFlat = "M" ) + g_newLine + msg + PL_Align.getSource( "L" )
		des2.append( [ g_newLine + msg ] )
		"""
		self.desFrame.SetDesSeveral( "cp_itemDes" , des2 )

