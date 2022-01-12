# -*- coding: gb18030 -*-
#


"""
"""

from SpellBase import *
import csdefine
from Spell_CatchPet import Spell_CatchPet

class Spell_322369003( Spell_CatchPet ):
	"""
	万能捕兽器
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_CatchPet.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_CatchPet.init( self, dict )

	def getCatchType( self ):
		"""
		获得捕获类型。
		"""
		return csdefine.PET_GET_SUPER_CATCH