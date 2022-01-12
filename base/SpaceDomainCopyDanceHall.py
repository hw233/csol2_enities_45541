# -*- coding: gb18030 -*-
#


"""
SpaceCopyDanceHall domain class
"""

import time
import Language
import BigWorld
from bwdebug import *
import Function
import csdefine 
from SpaceDomain import SpaceDomain

# ������
class SpaceDomainCopyDanceHall( SpaceDomain ):
	"""
	���˸��������Ӷ������ԣ�
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_DANCE_HALL
		
	def spaceNumberTodbid(self):
		#tmp = {spaceNumber:[dbid,]}
	    tmp  = {}
	    for k, v in self.keyToSpaceNumber.items():
	        if v in tmp.keys():
	            if k not in tmp[v]:
	                tmp[v].append(k)
	        else:
	            tmp[v] = [k]
	    return tmp		

	def spaceNumberLen(self, spaceNumber):
		if self.getSpaceItem(spaceNumber):
			if len(self.spaceNumberTodbid()[spaceNumber]) < csdefine.DANCEHALLPERSONLIMIT:
				return len(self.spaceNumberTodbid()[spaceNumber])
		return 0		
		
	def findFreeSpaceItem(self):
		for spaceNumber, value in self.spaceNumberTodbid().items():
			if self.getSpaceItem(spaceNumber): #��֤ȡ����spaceNumber
				if (BigWorld.globalData["ASDanceMgr"] is None) and len(value) < csdefine.DANCEHALLPERSONLIMIT:
					return self.getSpaceItem(spaceNumber)
				elif BigWorld.globalData["ASDanceMgr"].has_key("personLimit"):
					if len(value) < BigWorld.globalData["ASDanceMgr"]["personLimit"]:
						return self.getSpaceItem(spaceNumber)
		return None
		
	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		define method.
		����һ��entity��ָ����space��
		@type position : VECTOR3, 
		@type direction : VECTOR3, 
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: һЩ���ڸ�entity����space�Ķ�������� (domain����)
		@type params : PY_DICT = None
		"""
		BigWorld.globalData["DanceMgr"].registerDanceHallSpaceDomain(self)
		spaceItem = self.findSpaceItem( params, True )
		try:
			pickData = self.pickToSpaceData( baseMailbox, params )
			spaceItem.enter( baseMailbox, position, direction, pickData )
		except:
			ERROR_MSG( "%s teleportEntity is error." % self.name )
			
	def removeDBIDToSpaceNumber(self, dbid):
		#define method
		if dbid in self.keyToSpaceNumber:
			self.keyToSpaceNumber.pop(dbid)
		
