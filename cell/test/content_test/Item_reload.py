# -*- coding: gb18030 -*-

import Resource
import items
g_itemsDict = items.instance()

import cPickle
import binascii
import Language
import csstatus

ITEM_CONFIG = "Datas"

def updateItem( srcEntity, floder, ItemID ):
	"""
	"""
	#update some itemcfgs
	moduleNames = Language.searchConfigModuleName( "config/ItemTest/" + floder )
	for moduleName in moduleNames:
		if moduleName == str(int ( ItemID )):
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_ITEM_FIND_CONFIG_IN_SERVER, str( ( str(ItemID),)) )
			moduleFullName = "config.ItemTest." + floder + "." + moduleName
			compons = moduleFullName.split( "." )
			mod = __import__( moduleFullName )
			for com in compons[1:]:
				mod = getattr( mod, com )
			attrs = dir( mod )
			for attr in attrs:
				if attr == ITEM_CONFIG:
					if g_itemsDict._itemData.has_key( ItemID ):
						del g_itemsDict._itemData[ItemID]
						srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_ITEM_CLEAN_OLD_SKILL_IN_SERVER, str( ( str(ItemID),)) )
					item_Dict= getattr( mod, attr ).get(str(ItemID))
					item = g_itemsDict._loadItemConf( ItemID, item_Dict )
					g_itemsDict._itemDict[ItemID] = item
					srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_UPDATE_ITEM_OK_IN_SERVER, str( ( str(ItemID),)) )

