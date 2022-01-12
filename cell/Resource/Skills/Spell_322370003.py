# -*- coding: gb18030 -*-
#

import csstatus
from PetFormulas import formulas
from Spell_RejuvenescePet import Spell_RejuvenescePet
import csdefine

class Spell_322370003( Spell_RejuvenescePet ) :
	"""
	珍稀还童丹
	"""
	def __init__( self ) :
		"""
		"""
		Spell_RejuvenescePet.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_RejuvenescePet.init( self, dict )

	def getCatholiconType( self ):
		"""
		获得还童类型，默认为普通还童丹
		"""
		return csdefine.PET_GET_RARE_CATHOLICON

	def useableCheck( self, caster, target ) :
		baseStatus = Spell_RejuvenescePet.useableCheck( self, caster, target )
		if baseStatus != csstatus.SKILL_GO_ON :
			return baseStatus
		# 由于该技能被确定为不需要选择目标的释放方式 所以他是对自身释放的一种技能， 到 receive的时候receiver才是宠物
		actPet = caster.pcg_getActPet()
		if not actPet or actPet.etype == "MAILBOX" :
			return csstatus.PET_EVOLVE_FAIL_ERR_HIERARCHY2
		if not formulas.isHierarchy( actPet.entity.species, csdefine.PET_HIERARCHY_INFANCY2 ) :
			return csstatus.PET_EVOLVE_FAIL_ERR_HIERARCHY2
		return csstatus.SKILL_GO_ON

