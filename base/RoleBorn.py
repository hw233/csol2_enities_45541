# -*- coding: gb18030 -*-

# $Id: RoleBorn.py,v 1.7 2008-05-30 03:03:05 yangkai Exp $

"""
角色出生配置给予的物品、金钱等配置
"""

import BigWorld
from bwdebug import *
import csdefine
import Const
import ItemBagRole
import items
import ItemTypeEnum
from RoleCreateEquipsLoader import equipsLoader

g_items = items.instance()


def generateMoney( roleEntity, value ):
	"""
	角色初始化属性数据：产生技能属性值

	@param roleEntity: instance of role entity.
	@param skillIDs: int list or tuple
	"""
	roleEntity.cellData["money"] = value

def generatePotential( roleEntity, value ):
	"""
	角色初始化属性数据：产生技能属性值

	@param roleEntity: instance of role entity.
	@param skillIDs: int list or tuple
	"""
	roleEntity.cellData["potential"] = value

def generateSkill( roleEntity, skillIDs ):
	"""
	角色初始化属性数据：产生技能属性值

	@param roleEntity: instance of role entity.
	@param skillIDs: int list or tuple
	"""
	roleEntity.cellData["attrSkillBox"] = list( skillIDs )

def generateItem( roleEntity, items ):
	"""
	角色初始化属性数据：产生技能属性值

	@param roleEntity: instance of role entity.
	@param items: like as [(itemID, amount), ...]
	"""
	kitbag = roleEntity.cellData["itemsBag"]
	orderID = csdefine.KB_COMMON_ID * csdefine.KB_MAX_SPACE
	for itemID, amount in items:
		assert orderID is not None
		item = g_items.createDynamicItem( itemID, amount )
		kitbag.add( orderID, item )
		orderID += 1

def generateEquip( roleEntity, equips ):
	"""
	增加装备
	"""
	kitbag = roleEntity.cellData["itemsBag"]
	for order, itemID in equips.iteritems():
		item = g_items.createDynamicItem( itemID )
		kitbag.add( order, item )
		if order == ItemTypeEnum.CEL_FASHION1:
			if item == None: data = 0
			else: data = item.getFDict()
			roleEntity.cellData["fashionNum"] = data
		elif order == ItemTypeEnum.CEL_TALISMAN:
			if item == None: data = 0
			else: data = item.getFDict()
			roleEntity.cellData["talismanNum"] = data
		elif order == ItemTypeEnum.CEL_BODY:
			if item is None: data = { "modelNum" : 0, "iLevel" : 0 }
			else: data = item.getFDict()
			roleEntity.cellData["bodyFDict"] = data
		elif order == ItemTypeEnum.CEL_BREECH:
			if item is None: data = { "modelNum" : 0, "iLevel" : 0 }
			else: data = item.getFDict()
			roleEntity.cellData["breechFDict"] = data
		elif order == ItemTypeEnum.CEL_VOLA:
			if item is None: data = { "modelNum" : 0, "iLevel" : 0 }
			else: data = item.getFDict()
			roleEntity.cellData["volaFDict"] = data
		elif order == ItemTypeEnum.CEL_FEET:
			if item is None: data = { "modelNum" : 0, "iLevel" : 0 }
			else: data = item.getFDict()
			roleEntity.cellData["feetFDict"] = data
		elif order == ItemTypeEnum.CEL_LEFTHAND:
			# 盾牌是防具...
			if item is None:
				roleEntity.cellData["lefthandFDict"] = { "modelNum" : 0, "iLevel" : 0, "stAmount" : 0 }
			else:
				roleEntity.cellData["lefthandFDict"] = {	"modelNum"		: item.model(),
														"iLevel"		: item.getIntensifyLevel(),
														"stAmount"		: item.getBjExtraEffectCount(),
													}
		elif order == ItemTypeEnum.CEL_RIGHTHAND:
			if item is None:
				data = { "modelNum" : 0, "iLevel" : 0, "stAmount" : 0 }
			else:
				data = item.getFDict()
			profession = roleEntity.cellData["raceclass"] & csdefine.RCMASK_CLASS
			if profession == csdefine.CLASS_ARCHER:
				roleEntity.cellData["lefthandFDict"] = data
			elif profession == csdefine.CLASS_SWORDMAN:
				if item is None or item.getType() == ItemTypeEnum.ITEM_WEAPON_TWOSWORD :
					roleEntity.cellData["lefthandFDict"] = roleEntity.cellData["righthandFDict"] = data
				elif item.getType() == ItemTypeEnum.ITEM_WEAPON_SWORD1:
					roleEntity.cellData["righthandFDict"] = data
					roleEntity.cellData["lefthandFDict"] = { "modelNum" : 0, "iLevel" : 0, "stAmount" : 0 }
			else:
				roleEntity.cellData["righthandFDict"] = data

def generateAll( roleEntity ):
	"""
	角色初始化属性数据，给角色一些物品或技能等

	@param	roleEntity	: instance of role entity
	@type	roleEntity	: Entity
	"""
	funcs = {
				"skills"	: generateSkill,
				"items"		: generateItem,
				"money"		: generateMoney,
				"potential"	: generatePotential,
			}
	classes = roleEntity.cellData["raceclass"] & csdefine.RCMASK_CLASS
	for key, value in Const.g_newBornGratuities[classes].iteritems():
		funcs[key]( roleEntity, value )
	equips = equipsLoader.getEuipsByClass( classes )
	generateEquip( roleEntity, equips )

	roleEntity.qb_initializeOnCreateRole( classes )
