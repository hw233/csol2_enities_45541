# -*- coding: gb18030 -*-

"""
ʵ�ֲ�ͬ���԰汾��װ���������

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
	��ʼ������װ��Ʒ��
	"""
	@staticmethod
	def locale_big5( SELF, pyStRatios, wnd ) :
		"""
		BIG5 �汾
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
	����װ��Ʒ��
	"""
	
	@staticmethod
	def locale_big5( SELF, pyStQuality, quality ) :
		"""
		BIG5 �汾
		"""
		pyStQuality.text = ratio_colors[quality][0]
		pyStQuality.color = ratio_colors[quality][1]