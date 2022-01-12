# -*- coding: gb18030 -*-
#

"""
�Զ�ս�����е���Ʒ���ܿ�,�̳���QBItem.�����Զ�ս��������Ʒ���ܿ���Ҫ��������ж�(1��ֻ�ܷż���,2��ֻ�ܷ��շѵĺ�ҩ,3��ֻ�ܷ��շѵ���ҩ),�������϶�
���ֵĽӿ�
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
	�Զ�ս����Item
	"""

	def __init__( self, item, pyBinder = None ) :
		QBItem.__init__( self, item, pyBinder = None )
		self.canDropTypeList = []
		self.canDropWndList = []
		self.qbItemType = csdefine.QB_ITEM_KITBAG
		self.statusID = 0

	def onDrop_( self, pyTarget, pyDropped ) :
		"""
		�϶�
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
			if self.gbIndex in [csdefine.QB_AUTO_SPELL_INDEX + 5,csdefine.QB_AUTO_SPELL_INDEX + 6]: #��ɫ�Զ��ҩ��
				if baseItem.getLevel() > player.getLevel():
					# ��ҩƷ�ȼ�������ȼ���ʱ��ҩƷ�޷��ϵ��Զ�ս����
					player.statusMessage( csstatus.QB_ITEM_CANNOT_USE )
					return False
			if self.gbIndex in [csdefine.QB_AUTO_SPELL_INDEX + 10,csdefine.QB_AUTO_SPELL_INDEX + 11]: #�����Զ��ҩ��
				if baseItem.getLevel() > player.pcg_getActPet().level:# ��ҩƷ�ȼ��ȳ���ȼ���ʱ��ҩƷ�޷��ϵ������Զ�ս����
					player.statusMessage( csstatus.PET_ITEM_CANNOT_USE )
					return False
			if pyDropped.dragMark == DragMark.QUICK_BAR:
				itemID = pyDropped.itemInfo.id
			 	if pyDropped.gbIndex >= csdefine.QB_AUTO_SPELL_INDEX: 					# �Զ�����֮���Ϸ�
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
		�����Զ�ս�����е���Ʒ
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
