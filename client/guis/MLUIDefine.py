# -*- coding: gb18030 -*-
# ��������ļ�ר����������������õ�����Ҫ����򷱰汾�ı���


import Language
import ItemTypeEnum
import ShareTexts

if Language.LANG == Language.LANG_GBK :
	# -------------------------------------------------------------
	# ������������
	# -------------------------------------------------------------
	# ��������Ԫ��item��Ʒ�ʶ�Ӧ��mappingģʽ
	ItemQAColorMode = {
		0 : ( 4, 2 ),								# ��ɫ��Ʒ��������ӵģ�
		ItemTypeEnum.CQT_WHITE	: ( 1, 1 ),			# ��ɫƷ��
		ItemTypeEnum.CQT_BLUE	: ( 1, 2 ),			# ��ɫƷ��
		ItemTypeEnum.CQT_GOLD	: ( 2, 1 ),			# ��ɫƷ��
		ItemTypeEnum.CQT_PINK	: ( 2, 2 ),			# ��ɫƷ��
		ItemTypeEnum.CQT_GREEN	: ( 3, 1 ),			# ��ɫƷ��
	}
	# ������Ʒ�ʶ�Ӧ����ɫ�ı�
	QAColorText = {
		ItemTypeEnum.CQT_WHITE	: ShareTexts.WHITE,			# ��ɫ
		ItemTypeEnum.CQT_BLUE	: ShareTexts.BLUE,			# ��ɫ
		ItemTypeEnum.CQT_GOLD	: ShareTexts.GOLD,			# ��ɫ
		ItemTypeEnum.CQT_PINK	: ShareTexts.PINK,			# ��ɫ
		ItemTypeEnum.CQT_GREEN	: ShareTexts.GREEN,			# ��ɫ
	}
elif Language.LANG == Language.LANG_BIG5 :
	# -------------------------------------------------------------
	# ���己�������
	# -------------------------------------------------------------
	# ��������Ԫ��item��Ʒ�ʶ�Ӧ��mappingģʽ
	ItemQAColorMode = {
		0 : ( 4, 2 ),								# ��ɫ��Ʒ��
		ItemTypeEnum.CQT_WHITE	: ( 1, 1 ),			# ��ɫƷ��
		ItemTypeEnum.CQT_BLUE	: ( 3, 1 ),			# ��ɫƷ��
		ItemTypeEnum.CQT_GOLD	: ( 1, 2 ),			# ��ɫƷ��
		ItemTypeEnum.CQT_PINK	: ( 3, 2 ),			# ��ɫƷ��
		ItemTypeEnum.CQT_GREEN	: ( 4, 1 )			# ��ɫƷ��
	}
	# ������Ʒ�ʶ�Ӧ����ɫ�ı�
	QAColorText = {
		ItemTypeEnum.CQT_WHITE	: ShareTexts.WHITE,			# ��ɫ
		ItemTypeEnum.CQT_BLUE	: ShareTexts.GREEN,			# ��ɫ
		ItemTypeEnum.CQT_GOLD	: ShareTexts.BLUE,			# ��ɫ
		ItemTypeEnum.CQT_PINK	: ShareTexts.PINK,			# ��ɫ
		ItemTypeEnum.CQT_GREEN	: ShareTexts.ORANGE,		# ��ɫ
	}

# -------------------------------------------------------------
# ��Ʒ��Ʒ�ʶ�Ӧ����ɫֵ
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