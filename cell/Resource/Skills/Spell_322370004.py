# -*- coding: gb18030 -*-
#


import csstatus
from PetFormulas import formulas
from Spell_322370003 import Spell_322370003
import csdefine

class Spell_322370004( Spell_322370003 ) :
	"""
	������ϡ��ͯ��
	"""
	def __init__( self ) :
		"""
		"""
		Spell_322370003.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_322370003.init( self, dict )

	def getCatholiconType( self ):
		"""
		��û�ͯ����
		"""
		return csdefine.PET_GET_SUPER_RARE_CATHOLICON
