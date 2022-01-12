# -*- coding: gb18030 -*-
#
# $Id: QBShowSpecialChange.py,v 1.47 2009-05-20 09:32:25 jiangyi Exp $

"""
implement special description
2009/05/20: writen by jiangyi
"""

from items.CItemDescription import CItemDescription
from items.EquipEffectLoader import EquipEffectLoader
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from ItemSystemExp import EquipQualityExp

g_equipEffect = EquipEffectLoader.instance()
desr = CItemDescription()

def descriptionChange( checkedItem ) :                        #鼠标description信息的修改
	if checkedItem.itemInfo.baseItem.getType() != 394497 :           #如果类型是骑宠蛋，则把description信息修改成只显示名字和加速度、人数
		return checkedItem.itemInfo.description
	else :
		des0 = checkedItem.itemInfo.baseItem.query("name")
		if des0 != "":
			des0 = des0.split("(")[-1].split(")")[0]
			des0 = PL_Font.getSource( des0, fc = EquipQualityExp.instance().getColorByQuality( checkedItem.itemInfo.baseItem.getQuality() ) )
			desr.SetDescription("name" , des0)

		des1 = checkedItem.itemInfo.baseItem.query("describe2")
		if des1 != "" :
			des1 = PL_Font.getSource( des1, fc = "c40" )
			desr.SetDescription("describe2" , des1)

		des = desr.GetDescription()
		return des
	return ""