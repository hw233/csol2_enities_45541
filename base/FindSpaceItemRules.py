# -*- coding: gb18030 -*-

import csdefine
from bwdebug import *

def findSpaceItemForBigMap( spaceDomain, params, createIfNotExisted = False ):
	"""
	���ͼ���ҿռ����
	"""
	spaceItems = spaceDomain.getAllSpaceItems()
	if len( spaceItems ) == 0:
		spaceDomain.requestCreateSpace( None, {} )
	return spaceItems.values()[0]	#��ͨ��ͼֱ�ӷ���Ĭ�ϵ�ͼ����
	
def findSpaceItemForCommonCopys( spaceDomain, params, createIfNotExisted = False ):
	"""
	��ͨ���� һ�����
	"""
	try:
		spaceKey = params["spaceKey"]
	except KeyError:
		ERROR_MSG( "ObjectScripts %s :packedDomainData return a dict which don't has the spaceKey key." % ( spaceDomain.getScript().__class__.__name__) )
		return None
	spaceItem = spaceDomain.getSpaceItemByKey( spaceKey )
	if not spaceItem and createIfNotExisted:
		spaceItem = spaceDomain.createSpaceItem( params )
		spaceDomain.keyToSpaceNumber[ spaceKey ] = spaceItem.spaceNumber
		
	return spaceItem		
	
def findSpaceItemForMultiLine( spaceDomain, params, createIfNotExisted = False ):
	"""
	�����ั����
	"""
	lineNumber = params.get( "lineNumber" )
	assert lineNumber is not None, "the key lineNumber is necessary."

	if lineNumber <= 0 or lineNumber > spaceDomain.maxLine:
		ERROR_MSG( "space(%s) lineNumber(%i) is not exist!"% ( spaceDomain.name, lineNumber ) )
		lineNumber = spaceDomain.findFreeSpace()
		params[ "lineNumber" ] = lineNumber
	
	spaceItem = spaceDomain.getSpaceItemByKey(lineNumber)
	if spaceItem:
		return spaceItem

	# �����µ�SpaceItemʵ��
	spaceItem = spaceDomain.createSpaceItem( params )
	return spaceItem

def findSpaceItemForPlanes( spaceDomain, params, createIfNotExisted = False ):
	"""
	λ��
	"""
	fullSpaceNumber = params.get( "fullSpaceNumber", 0 )
	if spaceDomain._planesSpaceItemInfos.has_key( fullSpaceNumber ):
		spaceDomain._planesSpaceItemInfos[ fullSpaceNumber ].isFull = True
		spaceDomain.createPlanesSpaceItem( params )
		
	resultNumber = 0
	for sItem in spaceDomain._planesSpaceItemInfos.itervalues(): #�鿴���пռ��Ƿ���Ա
		if not sItem.isFull:
			resultNumber = sItem.spaceNumber
		
	if resultNumber == 0: #��������Ҳ���һ���ܽ���Ŀռ䣬�򴴽�һ���µ�
		spaceItem = spaceDomain.createPlanesSpaceItem( params )
		resultNumber = spaceItem.spaceNumber
		
	return spaceDomain.getSpaceItem( resultNumber )
	
def findSpaceItemForCopyTemp( spaceDomain, params, createIfNotExisted = False ):
	"""
	��ʱ�������ҹ���
	"""
	if not createIfNotExisted:
		return None		# �������µ�
			
	# �����µ�SpaceItemʵ��
	number = spaceDomain.spaceManager.getNewSpaceNumber()
	INFO_MSG("create new space item: %s, %d"%( spaceDomain.name, number ))
	spaceDomain.spaceItems_[number] = SpaceItem( spaceDomain, number, params )
	return spaceDomain.spaceItems_[number]
	
def findSpaceItemForDanceHall( spaceDomain, params, createIfNotExisted = False ):
	"""
	�������ҹ���
	"""
	dbid = params.get( "dbid" )			
	spaceItem = spaceDomain.getSpaceItemByKey( dbid )
	if spaceItem and spaceDomain.spaceNumberLen(spaceItem.spaceNumber) < csdefine.DANCEHALLPERSONLIMIT:
		return spaceItem
		
	#�Ȳ�����û�п�λ��spaceNumber
	if spaceDomain.findFreeSpaceItem():#������������csdefine.DANCEHALLPERSONLIMIT�˵ĸ���
		return spaceDomain.findFreeSpaceItem()
			
	if not spaceItem and createIfNotExisted:
		spaceItem = spaceDomain.createSpaceItem( params )
		spaceDomain.keyToSpaceNumber[ dbid ] = spaceItem.spaceNumber
	return spaceItem	
	
g_findSpaceItemRules = {
		csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS:findSpaceItemForCommonCopys,
		csdefine.FIND_SPACE_ITEM_FOR_BIG_MAP:findSpaceItemForBigMap,
		csdefine.FIND_SPACE_ITEM_FOR_COPY_TEMP:findSpaceItemForCopyTemp,
		csdefine.FIND_SPACE_ITEM_FOR_MULTILINE:findSpaceItemForMultiLine,
		csdefine.FIND_SPACE_ITEM_FOR_PLANES:findSpaceItemForPlanes,
		csdefine.FIND_SPACE_ITEM_FOR_DANCE_HALL:findSpaceItemForDanceHall,
}