# -*- coding: gb18030 -*-
#


import csstatus
from PetFormulas import formulas
from Spell_322370003 import Spell_322370003
import csdefine

class Spell_322370004( Spell_322370003 ) :
	"""
	超级珍稀还童丹
	"""
	def __init__( self ) :
		"""
		"""
		Spell_322370003.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_322370003.init( self, dict )

	def getCatholiconType( self ):
		"""
		获得还童类型
		"""
		return csdefine.PET_GET_SUPER_RARE_CATHOLICON
