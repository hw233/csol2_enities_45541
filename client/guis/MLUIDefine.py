# -*- coding: gb18030 -*-
# 这个定义文件专门用来定义界面上用到的需要区别简繁版本的变量


import Language
import ItemTypeEnum
import ShareTexts

if Language.LANG == Language.LANG_GBK :
	# -------------------------------------------------------------
	# 定义简体版配置
	# -------------------------------------------------------------
	# 简体版界面元素item的品质对应的mapping模式
	ItemQAColorMode = {
		0 : ( 4, 2 ),								# 灰色物品（辅助添加的）
		ItemTypeEnum.CQT_WHITE	: ( 1, 1 ),			# 白色品质
		ItemTypeEnum.CQT_BLUE	: ( 1, 2 ),			# 蓝色品质
		ItemTypeEnum.CQT_GOLD	: ( 2, 1 ),			# 金色品质
		ItemTypeEnum.CQT_PINK	: ( 2, 2 ),			# 粉色品质
		ItemTypeEnum.CQT_GREEN	: ( 3, 1 ),			# 绿色品质
	}
	# 简体版各品质对应的颜色文本
	QAColorText = {
		ItemTypeEnum.CQT_WHITE	: ShareTexts.WHITE,			# 白色
		ItemTypeEnum.CQT_BLUE	: ShareTexts.BLUE,			# 蓝色
		ItemTypeEnum.CQT_GOLD	: ShareTexts.GOLD,			# 金色
		ItemTypeEnum.CQT_PINK	: ShareTexts.PINK,			# 粉色
		ItemTypeEnum.CQT_GREEN	: ShareTexts.GREEN,			# 绿色
	}
elif Language.LANG == Language.LANG_BIG5 :
	# -------------------------------------------------------------
	# 定义繁体版配置
	# -------------------------------------------------------------
	# 繁体版界面元素item的品质对应的mapping模式
	ItemQAColorMode = {
		0 : ( 4, 2 ),								# 灰色物品格
		ItemTypeEnum.CQT_WHITE	: ( 1, 1 ),			# 白色品质
		ItemTypeEnum.CQT_BLUE	: ( 3, 1 ),			# 绿色品质
		ItemTypeEnum.CQT_GOLD	: ( 1, 2 ),			# 蓝色品质
		ItemTypeEnum.CQT_PINK	: ( 3, 2 ),			# 粉色品质
		ItemTypeEnum.CQT_GREEN	: ( 4, 1 )			# 橙色品质
	}
	# 繁体版各品质对应的颜色文本
	QAColorText = {
		ItemTypeEnum.CQT_WHITE	: ShareTexts.WHITE,			# 白色
		ItemTypeEnum.CQT_BLUE	: ShareTexts.GREEN,			# 绿色
		ItemTypeEnum.CQT_GOLD	: ShareTexts.BLUE,			# 蓝色
		ItemTypeEnum.CQT_PINK	: ShareTexts.PINK,			# 粉色
		ItemTypeEnum.CQT_GREEN	: ShareTexts.ORANGE,		# 橙色
	}

# -------------------------------------------------------------
# 物品的品质对应的颜色值
# -------------------------------------------------------------
from ItemSystemExp import EquipQualityExp
QAColorFunc = EquipQualityExp.instance().getColorByQuality
QAColor = {
	0 : ( 255, 255, 255, 0 ),
	ItemTypeEnum.CQT_WHITE	: QAColorFunc( ItemTypeEnum.CQT_WHITE ) + ( 0, ),
	ItemTypeEnum.CQT_BLUE	: QAColorFunc( ItemTypeEnum.CQT_BLUE ) + ( 255, ),
	ItemTypeEnum.CQT_GOLD	: QAColorFunc( ItemTypeEnum.CQT_GOLD ) + ( 255, ),
	ItemTypeEnum.CQT_PINK	: QAColorFunc( ItemTypeEnum.CQT_PINK ) + ( 255, ),
	ItemTypeEnum.CQT_GREEN	: QAColorFunc( ItemTypeEnum.CQT_GREEN ) + ( 255, ),
}