# -*- coding: gb18030 -*-
#

"""
"""

import csstatus
from PetFormulas import formulas
from Spell_322370001 import Spell_322370001
import csdefine


class Spell_322370002( Spell_322370001 ) :
	"""
	超级还童丹
	"""
	def __init__( self ) :
		"""
		"""
		Spell_322370001.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_322370001.init( self, dict )

	def getCatholiconType( self ):
		"""
		"""
		return csdefine.PET_GET_SUPER_CATHOLICON