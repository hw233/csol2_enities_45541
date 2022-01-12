# -*- coding: gb18030 -*-

from CItemBase import CItemBase
import ItemAttrClass
from gbref import rds
import TextFormatMgr
import csstatus
import csconst
import BigWorld
import Define
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from Time import Time
import time

class CVehicleBook( CItemBase ):
	"""
	骑宠技能书
	"""

	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def checkUse( self, owner ):
		"""
		检测使用者是否能使用该物品

		@param owner: 背包拥有者
		@type  owner: Entity
		@return: STATE CODE
		@rtype:  UINT16
		"""
		if owner.getVehicleLevel() < self.getReqLevel():
			return csstatus.CIB_MSG_ITEM_NOT_USED

		return CItemBase.checkUse( self, owner )

	def getProDescription( self, reference ):
		"""
		virtual method
		获取装备专有描述信息
		"""
		attrMap = ItemAttrClass.m_itemAttrMap
		# 等级需求
		desReqlevel = attrMap["reqLevel"].description_vehicle( self, reference )
		level = reference.getVehicleLevel()
		if level != 0 and level < self.getReqLevel():
			desReqlevel = rds.textFormatMgr.makeDestStr( desReqlevel ,rds.textFormatMgr.reqLevelCode )
			desReqlevel = TextFormatMgr.ItemText( self, desReqlevel ).replaceDesReqlevelCode()
			desReqlevel = PL_Font.getSource( desReqlevel, fc = ( 255, 0, 0 ) )
			desReqlevel += PL_Font.getSource( fc = self.defaultColor )
		self.desFrame.SetDescription( "itemreqLevel" , desReqlevel )

	def checkUseStatus( self, owner ) :
		"""
		检查物品的使用情况
		"""
		vehicleData = owner.vehicleDatas.get( owner.vehicleDBID )
		if vehicleData and vehicleData[ "level" ] < self.getReqLevel() :
			return Define.ITEM_STATUS_USELESSNESS
		return Define.ITEM_STATUS_NATURAL