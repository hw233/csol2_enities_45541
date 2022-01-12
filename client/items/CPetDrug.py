# -*- coding: gb18030 -*-

import Define
from CItemBase import CItemBase
import csstatus
import BigWorld
from Time import Time
import ItemAttrClass
import TextFormatMgr
from gbref import rds
from guis.tooluis.richtext_plugins.PL_Font import PL_Font

class CPetDrug( CItemBase ) :
	"""
	宠物一次性消耗品
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def checkUse( self, owner ):
		"""
		virtual method.
		"""
		pet = owner.pcg_getActPet()
		if pet is None:
			return csstatus.SKILL_PET_NO_CONJURED

		if pet.level < self.getReqLevel():
			return csstatus.SKILL_PET_NEED_LEVEL

		isLifeType = self.getLifeType()
		hasLifeTime = self.getLifeTime()
		if isLifeType and not hasLifeTime:
			return csstatus.CIB_MSG_ITEM_NO_USE_TIME

		if not self.query( "spell", 0 ):
			return csstatus.CIB_MSG_ITEM_NOT_USED

		springUsedCD = self.query( "springUsedCD", {} )
		player = BigWorld.player()
		for cd in springUsedCD:
			endTime = player.getCooldown( cd )[3]
			if endTime > Time.time():
				return csstatus.SKILL_ITEM_NOT_READY

		return csstatus.SKILL_GO_ON

	def checkUseStatus( self, owner ) :
		"""
		检查物品的使用情况
		"""
		pet = owner.pcg_getActPet()
		if pet and pet.level < self.getReqLevel():
			return Define.ITEM_STATUS_USELESSNESS
		return Define.ITEM_STATUS_NATURAL

	def getProDescription( self, reference ):
		"""
		virtual method
		获取物品专有描述信息
		"""
		CItemBase.getProDescription( self, reference )

		attrMap = ItemAttrClass.m_itemAttrMap
		# 显示物品分类，等级需求
		desReqlevel = attrMap["reqLevel"].description_pet( self, reference )
		pet = reference.pcg_getActPet()
		if pet and pet.level < self.getReqLevel():
			desReqlevel = rds.textFormatMgr.makeDestStr( desReqlevel ,rds.textFormatMgr.reqLevelCode )
			desReqlevel = TextFormatMgr.ItemText( self, desReqlevel ).replaceDesReqlevelCode()
			desReqlevel = PL_Font.getSource( desReqlevel, fc = ( 255, 0, 0 ) )
			desReqlevel += PL_Font.getSource( fc = self.defaultColor )
		self.desFrame.SetDescription("itemreqLevel" , desReqlevel)