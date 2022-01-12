# -*- coding: gb18030 -*-

from CItemBase import CItemBase
import BigWorld
import ItemTypeEnum
from bwdebug import *
import csstatus
import csconst
import SkillTargetObjImpl
from Resource.SkillLoader import g_skills

class CPositionSpellItem( CItemBase ):
	"""
	位置释放物品
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def use( self, owner, target ):
		"""
		使用物品
		"""
		checkResult = self.checkUse( owner )
		if checkResult != csstatus.SKILL_GO_ON:
			return checkResult

		spell = self.query( "spell" )
		target = SkillTargetObjImpl.createTargetObjPosition( target )
		try:
			spell = g_skills[spell]
		except:
			return  csstatus.SKILL_NOT_EXIST

		value = self.getUid()
		if owner.intonating():
			return csstatus.SKILL_INTONATING
		if owner.inHomingSpell() and ( not self.getType() in ItemTypeEnum.ROLE_DRUG_LIST ):
			return csstatus.SKILL_CANT_CAST
		owner.setTemp( "item_using", value )
		state = spell.useableCheck( owner, target )
		if state != csstatus.SKILL_GO_ON:
			owner.removeTemp( "item_using" )
			return csconst.SKILL_STATE_TO_ITEM_STATE.get( state,state )

		spell.use( owner, target )
		return csstatus.SKILL_GO_ON