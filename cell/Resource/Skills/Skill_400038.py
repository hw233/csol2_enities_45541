# -*- coding:gb18030 -*-
#

from Skill_Posture import Skill_Posture
from bwdebug import *

class Skill_400038( Skill_Posture ):
	"""
	领悟
	每等级提高15点法力上限
	"""
	def init( self, data ):
		"""
		"""
		Skill_Posture.init( self, data )
		self._param2 = float( data[ "param2" ] if len( data[ "param2" ] ) > 0 else 0 )
		
	def attach( self, ownerEntity ):
		"""
		"""
		if not ownerEntity.isPosture( self.getEffectPosture() ):
			return
		ownerEntity.MP_Max_value += self._param2
		ownerEntity.calcMPMax()
		
	def detach( self, ownerEntity ):
		"""
		"""
		if not ownerEntity.isPosture( self.getEffectPosture() ):
			return
		ownerEntity.MP_Max_value -= self._param2
		ownerEntity.calcMPMax()
		
		