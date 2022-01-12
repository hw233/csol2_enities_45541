# -*- coding: gb18030 -*-
# $Id: PetEpitome.py,v 1.18 2008-08-12 02:15:44 huangyongwei Exp $
#
"""
implement pet epitome type

2007/07/01: writen by huangyongwei
2007/11/17: rewriten by huangyongwei and rename it from "PetEpitomeType.py" to "PetEpitome.py"
"""

import BigWorld
from bwdebug import *
from PetFormulas import formulas
import csconst

# --------------------------------------------------------------------
# implement pet epitome class
# --------------------------------------------------------------------
class PetEpitome :
	def __init__( self ) :
		pass

	def getDictFromObj( self, epitome ) :
		return epitome

	def createObjFromDict( self, dict ) :
		return dict

	def isSameType( self, obj ) :
		return True


# --------------------------------------------------------------------
# pickle instances
# --------------------------------------------------------------------
instance = PetEpitome()
