# -*- coding: gb18030 -*-
#
# $Id: ExpGemDataMgr.py,v 1.1 2008-09-02 01:50:36 wangshufeng Exp $

import BigWorld
import csdefine
import Language
from config.server import ExpGem

class ExpGemDataMgr:
	"""
	"""
	__inst = None
	
	def __init__( self ) :
		assert ExpGemDataMgr.__inst is None
		self._data = ExpGem.Datas

	@classmethod
	def instance( SELF ):
		if SELF.__inst is None :
			SELF.__inst = ExpGemDataMgr()
		return SELF.__inst

	def getExpByLevel( self, level ):
		return self._data[level]
		
# --------------------------------------------------------------------
# global instance
# --------------------------------------------------------------------
expGemDataMgr = ExpGemDataMgr.instance()


#$Log: not supported by cvs2svn $
#
#