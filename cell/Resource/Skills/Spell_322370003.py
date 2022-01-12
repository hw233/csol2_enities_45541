# -*- coding: gb18030 -*-
#

import csstatus
from PetFormulas import formulas
from Spell_RejuvenescePet import Spell_RejuvenescePet
import csdefine

class Spell_322370003( Spell_RejuvenescePet ) :
	"""
	��ϡ��ͯ��
	"""
	def __init__( self ) :
		"""
		"""
		Spell_RejuvenescePet.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_RejuvenescePet.init( self, dict )

	def getCatholiconType( self ):
		"""
		��û�ͯ���ͣ�Ĭ��Ϊ��ͨ��ͯ��
		"""
		return csdefine.PET_GET_RARE_CATHOLICON

	def useableCheck( self, caster, target ) :
		baseStatus = Spell_RejuvenescePet.useableCheck( self, caster, target )
		if baseStatus != csstatus.SKILL_GO_ON :
			return baseStatus
		# ���ڸü��ܱ�ȷ��Ϊ����Ҫѡ��Ŀ����ͷŷ�ʽ �������Ƕ������ͷŵ�һ�ּ��ܣ� �� receive��ʱ��receiver���ǳ���
		actPet = caster.pcg_getActPet()
		if not actPet or actPet.etype == "MAILBOX" :
			return csstatus.PET_EVOLVE_FAIL_ERR_HIERARCHY2
		if not formulas.isHierarchy( actPet.entity.species, csdefine.PET_HIERARCHY_INFANCY2 ) :
			return csstatus.PET_EVOLVE_FAIL_ERR_HIERARCHY2
		return csstatus.SKILL_GO_ON

