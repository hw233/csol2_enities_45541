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
	�콵���У��вơ�����
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def description( self, reference ):
		"""
		��������
		@param reference: ���entity,��ʾ��˭����Ϊ���������Ĳ�����
		@type  reference: Entity
		@return:          ��Ʒ���ַ�������
		@rtype:           ARRAY of str
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		# ��ʾ��Ʒ����
		nameDes = attrMap["name"].description( self, reference )
		nameDes = PL_Font.getSource( nameDes, fc = EquipQualityExp.instance().getColorByQuality( self.getQuality() ) )
		self.desFrame.SetDescription("name" , nameDes)
		#�Ƿ��
		desBind = attrMap["bindType"].description( self, reference )
		if desBind != "":
			self.desFrame.SetDescription("bindType", desBind)
		# Ψһ��
		only = attrMap["onlyLimit"].description( self, reference )
		if only == 1:
			self.desFrame.SetDescription( "onlyLimit" , lbs_CLuckyBox[1] )
		# �Ƿ�ɳ���
		if not self.canSell():
			canNotSell = PL_Font.getSource( lbs_CLuckyBox[2], fc = "c6" )
			self.desFrame.SetDescription( "canNotSell" , canNotSell )
		# ȡ�ö��������1
		des1 = attrMap["describe1"].description( self, reference )
		if des1 != "":
			des1 = PL_Font.getSource( des1, fc = "c4" )
			self.desFrame.SetDescription( "describe1", des1 )
		# ȡ�ö��������2
		des2 = attrMap["describe2"].description( self, reference )
		if des2 != "":
			des2 = PL_Font.getSource( des2, fc = "c40" )
			des2 = des2 % self.getLevel()
		#	if des1 != "": des2 = g_newLine + des2
			self.desFrame.SetDescription( "describe2", des2 )
		# ȡ�ö��������3
		des3 = attrMap["describe3"].description( self, reference )
		if des3 != "":
			des3 = PL_Font.getSource( des3, fc = "c24" )
		#	if des1 != "" or des2 != "": des3 = g_newLine + des3
			self.desFrame.SetDescription( "describe3", des3 )

		return self.desFrame.GetDescription()

	def checkUse( self, owner ):
		"""
		�콵���ж���ҵ�ʹ������
		"""
		checkResult = CItemBase.checkUse( self, owner )
		if checkResult != csstatus.SKILL_GO_ON:
			return checkResult

		if self.getLevel() > owner.level + csconst.LUCKY_BOX_USE_LEVEL_CHECK:
			return csstatus.CIB_LUCKYBOX_CANT_USE_LEVEL_LACK

		return csstatus.SKILL_GO_ON