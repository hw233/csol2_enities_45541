# -*- coding: gb18030 -*-

"""
实现不同语言版本的装备打造界面

2010.05.11: writen by pengju
"""

from AbstractTemplates import MultiLngFuncDecorator
from LabelGather import labelGather
import ItemTypeEnum
from RatioItem import RatioItem

ratio_colors = {ItemTypeEnum.CQT_GREEN:( labelGather.getText( "EquipProduce:main", "ratio_orange" ),( 255, 128, 0,255 ) ),
					ItemTypeEnum.CQT_PINK:( labelGather.getText( "EquipProduce:main", "ratio_purple" ), ( 192, 0, 192, 255 ) ),
					ItemTypeEnum.CQT_GOLD:( labelGather.getText( "EquipProduce:main", "ratio_blue" ), ( 0, 229, 233, 255 ) ),
					ItemTypeEnum.CQT_BLUE:( labelGather.getText( "EquipProduce:main", "ratio_green" ),( 0, 255, 0, 255 ) ),
					ItemTypeEnum.CQT_WHITE:( labelGather.getText( "EquipProduce:main", "ratio_white" ), ( 255, 255, 255, 255 ) )
			}
class deco_equipProInit( MultiLngFuncDecorator ) :
	"""
	初始化打造装备品质
	"""
	@staticmethod
	def locale_big5( SELF, pyStRatios, wnd ) :
		"""
		BIG5 版本
		"""
		for name, item in wnd.children:
			if "quality_" not in name:continue
			quality = int( name.split("_")[1] )
			ratioColor = ratio_colors.get( quality, None )
			if ratioColor is None:continue
			pyRatioText = RatioItem( item )
			pyRatioText.title = ratioColor[0]
			pyRatioText.titleColor = ratioColor[1]
			pyRatioText.text = ""
			pyStRatios[quality] = pyRatioText

class deco_equipProSet( MultiLngFuncDecorator ) :
	"""
	设置装备品质
	"""
	
	@staticmethod
	def locale_big5( SELF, pyStQuality, quality ) :
		"""
		BIG5 版本
		"""
		pyStQuality.text = ratio_colors[quality][0]
		pyStQuality.color = ratio_colors[quality][1]