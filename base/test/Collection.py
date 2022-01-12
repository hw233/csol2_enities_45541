# -*- coding: gb18030 -*-

"""
收购物品base测试脚本
测试功能：
	base/CollectionMgr.py

"""

#注意，与角色有关的测试（就是一些通过接口调用的方法），完全可以通过client完整测试，所以在base测试，重点将集中在类本身功能上。


from CollectionItem import CollectionItem
import BigWorld
import random


cm = BigWorld.entities[BigWorld.globalData["CollectionMgr"].id]

playerDBID = 0

def start():
	cm.startCollection( playerDBID )


def get():
	return cm.getCollectionBag( playerDBID )


def add():
	item 					= CollectionItem()
	item.collectorDBID		= playerDBID
	item.price				= 1000
	item.itemID				= "50101002"
	item.collectAmount		= 100
	collectionBag = cm.getCollectionBag( item.collectorDBID )
	collectionBag.add( item )
	return item


def remove():
	"""
	"""
	uid = add().uid
	collectionBag = cm.getCollectionBag( playerDBID )
	collectionBag.remove( uid )


def update():
	"""
	"""
	uid = add().uid
	collectionBag = cm.getCollectionBag( playerDBID )
	item 					= CollectionItem()
	item.collectorDBID		= playerDBID
	item.price				= 600
	item.itemID				= "50101002"
	item.collectAmount		= 200
	item.uid				= uid
	collectionBag.update( item )


def take():
	"""
	"""
	update()
	return cm.getCollectionBag( playerDBID ).takeItems()


def onTake():
	"""
	"""
	collectionBag = cm.getCollectionBag( playerDBID )
	collectionBag.onTaked()


def test():
	#cm.clear()
	global playerDBID
	playerDBID = random.randint(0,88888888)
	start()
	get()
	add()
	remove()
	update()
	take()
	onTake()
	
