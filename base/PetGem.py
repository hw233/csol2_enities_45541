# -*- coding: gb18030 -*-
#
# $Id: PetGem.py,v 1.1 2007-11-17 02:18:36 huangyongwei Exp $

"""
implement gem used by pet

2007/11/14: writen by huangyongwei
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
