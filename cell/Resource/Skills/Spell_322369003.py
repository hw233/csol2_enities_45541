# -*- coding: gb18030 -*-
#


"""
"""

from SpellBase import *
import csdefine
from Spell_CatchPet import Spell_CatchPet

class Spell_322369003( Spell_CatchPet ):
	"""
	���ܲ�����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_CatchPet.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_CatchPet.init( self, dict )

	def getCatchType( self ):
		"""
		��ò������͡�
		"""
		return csdefine.PET_GET_SUPER_CATCH