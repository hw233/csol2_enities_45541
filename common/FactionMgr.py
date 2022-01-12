# -*- coding: gb18030 -*-
#
# $Id: FactionMgr.py,v 1.1 2008-08-30 10:05:09 wangshufeng Exp $

import BigWorld
import csdefine
import Language
from config import Faction

class FactionMgr :
	__inst = None

	def __init__( self ) :
		assert FactionMgr.__inst is None
		self.factionDict = Faction.Datas

	@classmethod
	def instance( SELF ) :
		if SELF.__inst is None :
			SELF.__inst = FactionMgr()
		return SELF.__inst

	def getName( self, factionID ):
		try:
			return self.factionDict[factionID]["name"]
		except:
			return ""

	def getPrestige( self, factionID ):
		return self.factionDict[factionID]["prestige"]

	def getForce( self, factionID ):
		return self.factionDict[factionID]["force"]

	def getIDByName( self, name ):
		"""
		根据名字获取ID，目前只用于GM命令
		"""
		for key, factionItem in self.factionDict.items():
			if factionItem["name"] == name:
				return key
		return 0
# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
factionMgr = FactionMgr.instance()


#$Log: not supported by cvs2svn $
#
#