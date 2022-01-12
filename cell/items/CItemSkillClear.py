# -*- coding: gb18030 -*-

from bwdebug import *
import csdefine
import csstatus
from config.item.CanBackUpSkills import Datas as bkskills
from CItemBase import CItemBase
import Love3

class CItemSkillClear( CItemBase ):
	"""
	洗技能物品(北冥炉)
	"""
	def __init__( self, srcData ):
		"""
		"""
		self.bk_keys = bkskills.keys()
		self.bk_keys.sort()
		CItemBase.__init__( self, srcData )
		
	def use( self, owner, target ):
		"""
		使用物品，获得潜能物品
		"""
		newItemID = int( self.query( "param1" ) )
		if newItemID == 0:
			return csstatus.SKILL_NOT_EXIST
		newItem = Love3.g_itemsDict.createDynamicItem( newItemID )
		if newItem is None:
			return csstatus.SKILL_NOT_EXIST
		potential = self.getPotentialFromLearnedSkills( target )
		newItem.set( "param1", potential )
		target.addItemAndNotify_( newItem, csdefine.ADD_ITEM_SKILL_CLEAR )
		ud = self.getUseDegree()
		if ud > 0:
			ud -= 1
			self.setUseDegree( ud, owner )
		if ud <=0:
			owner.removeItem_( self.getOrder(), 1, csdefine.DELETE_ITEM_USE )
		INFO_MSG( "%s use skill clear item,gain potential:%i,itemUID:%d."%( owner.getName(), potential, self.getUid() ) )
		return csstatus.SKILL_GO_ON
		
	def getPotentialFromLearnedSkills( self, player ):
		"""
		根据玩家所有技能返回总潜能
		"""
		potentialVal = 0
		removeList = []
		for skillID in player.getSkills():
			if skillID in self.bk_keys:
				skTemp = skillID/1000*1000
				sklevel = skillID - skTemp
				removeList.append( skillID )
				for l in xrange(1, (sklevel+1)):
					pv = bkskills.get( skTemp+l )
					if pv is not None:
						potentialVal += pv
		for skillID in removeList:
			player.removeSkill( skillID )
		return potentialVal