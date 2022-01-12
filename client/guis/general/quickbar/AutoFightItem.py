# -*- coding: gb18030 -*-
#

"""
自动战斗栏中的物品技能框,继承与QBItem.由于自动战斗栏的物品技能框需要做特殊的判断(1格只能放技能,2格只能放收费的红药,3格只能放收费的蓝药),故重载拖动
部分的接口
2008/10/21: writen by huangdong
"""
from bwdebug import *
from guis import *
from guis.controls.Item import Item
from QBItem import QBItem
import csdefine
import csstatus
import csconst
import ItemTypeEnum
import event.EventCenter as ECenter


class AutoFightItem( QBItem ):
	"""
	自动战斗的Item
	"""

	def __init__( self, item, pyBinder = None ) :
		QBItem.__init__( self, item, pyBinder = None )
		self.canDropTypeList = []
		self.canDropWndList = []
		self.qbItemType = csdefine.QB_ITEM_KITBAG
		self.statusID = 0

	def onDrop_( self, pyTarget, pyDropped ) :
		"""
		拖动
		"""
		if pyDropped.itemInfo is None : return True
		Item.onDrop_( self, pyTarget, pyDropped )
		player = BigWorld.player()
		baseItem = pyDropped.itemInfo.baseItem
		spaceSkills = player.spaceSkillList
		if self.gbCopy:
			if pyDropped.dragMark not in self.canDropWndList :
				return False
			if baseItem.getType() not in self.canDropTypeList:
				player.statusMessage( self.statusID )
				return False
			if self.gbIndex in [csdefine.QB_AUTO_SPELL_INDEX + 5,csdefine.QB_AUTO_SPELL_INDEX + 6]: #角色自动嗑药栏
				if baseItem.getLevel() > player.getLevel():
					# 当药品等级比人物等级高时，药品无法拖到自动战斗栏
					player.statusMessage( csstatus.QB_ITEM_CANNOT_USE )
					return False
			if self.gbIndex in [csdefine.QB_AUTO_SPELL_INDEX + 10,csdefine.QB_AUTO_SPELL_INDEX + 11]: #宠物自动嗑药栏
				if baseItem.getLevel() > player.pcg_getActPet().level:# 当药品等级比宠物等级高时，药品无法拖到宠物自动战斗栏
					player.statusMessage( csstatus.PET_ITEM_CANNOT_USE )
					return False
			if pyDropped.dragMark == DragMark.QUICK_BAR:
				itemID = pyDropped.itemInfo.id
			 	if pyDropped.gbIndex >= csdefine.QB_AUTO_SPELL_INDEX: 					# 自动技能之间拖放
			 		if itemID in spaceSkills:
						if pyTarget.itemInfo is None:
							ECenter.fireEvent( "EVT_ON_QUICKBAR_UPDATE_ITEM", pyTarget.gbIndex, pyDropped.itemInfo )
							ECenter.fireEvent( "EVT_ON_QUICKBAR_UPDATE_ITEM", pyDropped.gbIndex, None )
						else:
							tempInfo = pyTarget.itemInfo
							ECenter.fireEvent( "EVT_ON_QUICKBAR_UPDATE_ITEM", pyTarget.gbIndex, pyDropped.itemInfo )
							ECenter.fireEvent( "EVT_ON_QUICKBAR_UPDATE_ITEM", pyDropped.gbIndex, tempInfo )
					else:
						if self.itemInfo:
							player.qb_exchangeItem( pyDropped.gbIndex, self.gbIndex )
						else:
							player.qb_updateItem( self.gbIndex, self.qbItemType, baseItem )
				else:
			 		if itemID in spaceSkills:
			 			ECenter.fireEvent( "EVT_ON_QUICKBAR_UPDATE_ITEM", pyTarget.gbIndex, pyDropped.itemInfo )
					else:
						player.qb_updateItem( self.gbIndex, self.qbItemType, baseItem )
			else:
				player.qb_updateItem( self.gbIndex, self.qbItemType, baseItem )
		else:
			player.qb_exchangeItem( pyDropped.gbIndex, self.gbIndex )
		return True

	def update( self, itemInfo ) :
		"""
		更新自动战斗框中的物品
		"""
		QBItem.update( self, itemInfo )
		index = self.gbIndex - csdefine.QB_AUTO_SPELL_INDEX

	def _setGBIndex( self, index ):
		if index in range( csdefine.QB_AUTO_SPELL_INDEX, csdefine.QB_AUTO_SPELL_INDEX + 5 ):
			self.canDropTypeList = csconst.BASE_SKILL_INITIA_SPELL_LIST
			self.canDropWndList = [ DragMark.QUICK_BAR, DragMark.SKILL_WND ]
			self.qbItemType = csdefine.QB_ITEM_SKILL
			self.statusID = csstatus.AUTO_FIGHT_CANNOT_PUT_SKILL
		elif index == csdefine.QB_AUTO_SPELL_INDEX + 5:
			self.canDropWndList = [ DragMark.QUICK_BAR, DragMark.KITBAG_WND ]
			self.canDropTypeList = [ ItemTypeEnum.ITEM_SUPER_DRUG_HP, ItemTypeEnum.ITEM_DRUG_ROLE_HP ]
			self.statusID = csstatus.AUTO_FIGHT_CANNOTPUTIT_RED
		elif index == csdefine.QB_AUTO_SPELL_INDEX + 6:
			self.canDropTypeList = [ ItemTypeEnum.ITEM_SUPER_DRUG_MP, ItemTypeEnum.ITEM_DRUG_ROLE_MP ]
			self.canDropWndList = [ DragMark.QUICK_BAR, DragMark.KITBAG_WND ]
			self.statusID = csstatus.AUTO_FIGHT_CANNOTPUTIT_BLUE
		elif index == csdefine.QB_AUTO_SPELL_INDEX + 10:
			self.canDropTypeList = [ ItemTypeEnum.ITEM_PET_SUPER_DRUG_HP, ItemTypeEnum.ITEM_DRUG_PET_HP ]
			self.canDropWndList = [ DragMark.QUICK_BAR, DragMark.KITBAG_WND ]
			self.statusID = csstatus.AUTO_FIGHT_PUT_PET_RED
		elif index == csdefine.QB_AUTO_SPELL_INDEX + 11:
			self.canDropTypeList = [ ItemTypeEnum.ITEM_PET_SUPER_DRUG_MP, ItemTypeEnum.ITEM_DRUG_PET_MP ]
			self.canDropWndList = [ DragMark.QUICK_BAR, DragMark.KITBAG_WND ]
			self.statusID = csstatus.AUTO_FIGHT_PUT_PET_BLUE
		else:
			ERROR_MSG( "Autofight quick bar has no index ( %i )." % index )
		QBItem._setGBIndex( self, index )

	gbIndex = property( QBItem._getGBIndex, _setGBIndex )
