# -*- coding: gb18030 -*-
# $Id: PetEpitome.py,v 1.5 2007-12-06 06:39:03 huangyongwei Exp $
#
"""
implement pet epitome type

2007/07/01: writen by huangyongwei
2007/11/17: rewriten by huangyongwei and rename it from "PetEpitomeType.py" to "PetEpitome.py"
"""

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
# implement active pet information class
# --------------------------------------------------------------------
class ActivePet :
	def getDictFromObj( self, actPet ) :
		return actPet

	def createObjFromDict( self, dict ) :
		return dict

	def isSameType( self, obj ) :
		return True


# --------------------------------------------------------------------
# pickle instances
# --------------------------------------------------------------------
instance = PetEpitome()
actPetInstance = ActivePet()
