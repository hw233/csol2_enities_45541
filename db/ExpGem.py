# -*- coding: gb18030 -*-
#
# $Id: ExpGem.py,v 1.1 2008-08-01 11:09:49 wangshufeng Exp $

"""
implement gem used by pet

2007/11/14: writen by wsf
"""

import time
import csdefine


class BaseGem :
	def getDictFromObj( self, gem ) :
		return gem

	def createObjFromDict( self, dict ) :
		return dict

	def isSameType( self, gem ) :
		return True



# --------------------------------------------------------------------
# implement common gem class
# --------------------------------------------------------------------
class CommonGem( BaseGem ) :
	def __init__( self ) :
		pass


# --------------------------------------------------------------------
# implement train gem class
# --------------------------------------------------------------------
class TrainGem( BaseGem ) :
	def __init__( self ) :
		pass


# --------------------------------------------------------------------
# instance for packing
# --------------------------------------------------------------------
trainGemInstance = TrainGem()
commonGemInstance = CommonGem()



#
# $Log: not supported by cvs2svn $
#
#