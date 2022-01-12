# -*- coding: gb18030 -*-
#

import BigWorld
import csstatus
from PetFormulas import formulas
from Spell_RejuvenescePet import Spell_RejuvenescePet
import csdefine

class Spell_322370001( Spell_RejuvenescePet ) :
	"""
	还童丹
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

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def useableCheck( self, caster, target ) :
		baseStatus = Spell_RejuvenescePet.useableCheck( self, caster, target )
		if baseStatus != csstatus.SKILL_GO_ON :
			return baseStatus
		actPet = caster.pcg_getActPet()
		e = BigWorld.entities.get( actPet.entity.id )
		if not e or not actPet or actPet == "MAILBOX" :
			return csstatus.PET_EVOLVE_FAIL_NOT_CONJURED
		# 由于该技能被确定为不需要选择目标的释放方式 所以他是对自身释放的一种技能， 到 receive的时候receiver才是宠物
		if not formulas.isHierarchy( e.species, csdefine.PET_HIERARCHY_GROWNUP ) and \
			not formulas.isHierarchy( e.species, csdefine.PET_HIERARCHY_INFANCY1 ):
				return csstatus.PET_EVOLVE_FAIL_ERR_HIERARCHY1
		return csstatus.SKILL_GO_ON
