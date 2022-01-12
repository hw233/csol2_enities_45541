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
	潜能书 by 姜毅
	"""
	def __init__( self, srcData ):
		"""
		"""
		CEquip.__init__( self, srcData )
		
	def getPotential( self ):
		"""
		获得书上潜能
		"""
		temp = self.query( "param2" )
		if temp is None:
			return 0
		return int( temp )
		
	def getPotentialMax( self ):
		"""
		获得书上最大潜能
		"""
		return int( self.queryTemp( "param1", 0 ) )
		
	def getPotentialRate( self ):
		"""
		获得潜能附加率
		"""
		return float( self.queryTemp( "param3", 0 ) )
		
	def isPotentialMax( self ):
		"""
		潜能书是否满了
		"""
		return self.getPotential() >= self.getPotentialMax()

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
		nameDes = PL_Font.getSource( nameDes, fc = self.getQualityColor() )
		self.desFrame.SetDescription("name" , nameDes)
		#是否绑定
		desBind = attrMap["bindType"].description( self, reference )
		if desBind != "":
			self.desFrame.SetDescription("bindType", desBind)
			
		# 显示物品分类，等级需求
		desReqlevel = attrMap["reqLevel"].description( self, reference )
		if reference.level < self.getReqLevel():
			desReqlevel = rds.textFormatMgr.makeDestStr( desReqlevel ,rds.textFormatMgr.reqLevelCode )
			desReqlevel = TextFormatMgr.ItemText( self, desReqlevel ).replaceDesReqlevelCode()
			desReqlevel = PL_Font.getSource( desReqlevel, fc = ( 255, 0, 0 ) )
			desReqlevel += PL_Font.getSource( fc = self.defaultColor )
		self.desFrame.SetDescription("itemreqLevel" , desReqlevel)
		
		# 所存储潜能点
		pot = self.getPotential()
		potMax = self.getPotentialMax()
		desPot = ""
		if pot >=  potMax:
			pot = lbs_CEquip[15]
		desPot = "%s:    %s/%s"%( lbs_EquipEffects[66], pot, potMax )
		self.desFrame.SetDescription( "bookPotential", desPot )
		
		# 取得额外的描述1
		des1 = attrMap["describe1"].description( self, reference )
		if des1 != "":
			des1 = PL_Font.getSource( des1, fc = "c4" )
			self.desFrame.SetDescription( "describe1", des1 )
		# 取得额外的描述2
		des2 = attrMap["describe2"].description( self, reference )
		if des2 != "":
			des2 = PL_Font.getSource( des2, fc = "c40" )
			self.desFrame.SetDescription( "describe2", des2 )
		# 取得额外的描述3
		des3 = attrMap["describe3"].description( self, reference )
		if des3 != "":
			des3 = PL_Font.getSource( des3, fc = "c24" )
			self.desFrame.SetDescription( "describe3", des3 )
			
		return self.desFrame.GetDescription()