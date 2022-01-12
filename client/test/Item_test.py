# -*- coding: gb18030 -*-

import items
g_itemsDict = items.instance()
from config.item.Items import Datas as ITEM_DATA

import cPickle
import binascii
import Language
import csstatus
import BigWorld

ITEM_CONFIG = "Datas"

g_itemData = { }

def updateItem( floder, ItemID ):
	"""
	"""
	#update some itemcfgs
	g_itemData = { }
	srcEntity = BigWorld.player()
	moduleNames = Language.searchConfigModuleName( "config/ItemTest/" + floder )
	for moduleName in moduleNames:
		if moduleName == str(int ( ItemID )):
			srcEntity.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_ITEM_FIND_CONFIG_IN_CLIENT, str( ( str(ItemID),)) )
			moduleFullName = "config.ItemTest." + floder + "." + moduleName
			compons = moduleFullName.split( "." )
			mod = __import__( moduleFullName )
			for com in compons[1:]:
				mod = getattr( mod, com )
			attrs = dir( mod )
			for attr in attrs:
				if attr == ITEM_CONFIG:
					if g_itemsDict._itemDict.has_key( ItemID ):
						del g_itemsDict._itemDict[ItemID]
						srcEntity.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_ITEM_CLEAN_OLD_SKILL_IN_CLIENT, str( ( str(ItemID),)) )
					item_Dict= getattr( mod, attr ).get(str(ItemID))
					item = g_itemsDict._loadItemConf( ItemID, item_Dict )
					g_itemsDict._itemDict[ItemID] = item
					srcEntity.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_ITEM_OK_IN_CLIENT, str( ( str(ItemID),)) )
	
