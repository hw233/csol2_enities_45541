# -*- coding: gb18030 -*-

import csconst
import csstatus
import ItemAttrClass

from gbref import rds
import TextFormatMgr
from CEquip import CEquip
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from config.client.labels.items import lbs_EquipEffects
from config.client.labels.items import lbs_CEquip

class CPotentialBook( CEquip ):
	"""
	Ǳ���� by ����
	"""
	def __init__( self, srcData ):
		"""
		"""
		CEquip.__init__( self, srcData )
		
	def getPotential( self ):
		"""
		�������Ǳ��
		"""
		temp = self.query( "param2" )
		if temp is None:
			return 0
		return int( temp )
		
	def getPotentialMax( self ):
		"""
		����������Ǳ��
		"""
		return int( self.queryTemp( "param1", 0 ) )
		
	def getPotentialRate( self ):
		"""
		���Ǳ�ܸ�����
		"""
		return float( self.queryTemp( "param3", 0 ) )
		
	def isPotentialMax( self ):
		"""
		Ǳ�����Ƿ�����
		"""
		return self.getPotential() >= self.getPotentialMax()

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
		nameDes = PL_Font.getSource( nameDes, fc = self.getQualityColor() )
		self.desFrame.SetDescription("name" , nameDes)
		#�Ƿ��
		desBind = attrMap["bindType"].description( self, reference )
		if desBind != "":
			self.desFrame.SetDescription("bindType", desBind)
			
		# ��ʾ��Ʒ���࣬�ȼ�����
		desReqlevel = attrMap["reqLevel"].description( self, reference )
		if reference.level < self.getReqLevel():
			desReqlevel = rds.textFormatMgr.makeDestStr( desReqlevel ,rds.textFormatMgr.reqLevelCode )
			desReqlevel = TextFormatMgr.ItemText( self, desReqlevel ).replaceDesReqlevelCode()
			desReqlevel = PL_Font.getSource( desReqlevel, fc = ( 255, 0, 0 ) )
			desReqlevel += PL_Font.getSource( fc = self.defaultColor )
		self.desFrame.SetDescription("itemreqLevel" , desReqlevel)
		
		# ���洢Ǳ�ܵ�
		pot = self.getPotential()
		potMax = self.getPotentialMax()
		desPot = ""
		if pot >=  potMax:
			pot = lbs_CEquip[15]
		desPot = "%s:    %s/%s"%( lbs_EquipEffects[66], pot, potMax )
		self.desFrame.SetDescription( "bookPotential", desPot )
		
		# ȡ�ö��������1
		des1 = attrMap["describe1"].description( self, reference )
		if des1 != "":
			des1 = PL_Font.getSource( des1, fc = "c4" )
			self.desFrame.SetDescription( "describe1", des1 )
		# ȡ�ö��������2
		des2 = attrMap["describe2"].description( self, reference )
		if des2 != "":
			des2 = PL_Font.getSource( des2, fc = "c40" )
			self.desFrame.SetDescription( "describe2", des2 )
		# ȡ�ö��������3
		des3 = attrMap["describe3"].description( self, reference )
		if des3 != "":
			des3 = PL_Font.getSource( des3, fc = "c24" )
			self.desFrame.SetDescription( "describe3", des3 )
			
		return self.desFrame.GetDescription()