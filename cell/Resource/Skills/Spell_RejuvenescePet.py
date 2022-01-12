# -*- coding: gb18030 -*-
#
# $Id: Spell_322370.py,v 1.7 2008-04-10 03:25:50 kebiao Exp $

"""
implement pet item spell( 还童丹 使用：将成年宠物变成1级的一代宠物。 )
2007/11/30: writen by huangyongwei
"""

import csstatus
from PetFormulas import formulas
from Spell_Item import Spell_Item
import csdefine

class Spell_RejuvenescePet( Spell_Item ) :
	"""
	还童丹技能
	"""
	def __init__( self ) :
		Spell_Item.__init__( self )
		self.__catholiconType = csdefine.PET_GET_CATHOLICON		# 该属性暂时在这里写，它应该是在物品中用 setTemp 设置的

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		#由于现在只有一种还童丹 因此当前不写这个
		#self.__catholiconType = eval( "csdefine." + section.readString( "param0" ) )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def updateItem( self , caster ):
		"""
		更新物品使用
		"""
		pet = caster.pcg_getActPet()
		if pet is None:
			caster.removeTemp( "item_using" )
			return
		Spell_Item.updateItem( self, caster )
		
	def useableCheck( self, caster, target ) :
		baseStatus = Spell_Item.useableCheck( self, caster, target )
		if baseStatus != csstatus.SKILL_GO_ON :
			return baseStatus
		if not caster.pcg_hasActPet() :
			return csstatus.PET_EVOLVE_FAIL_NOT_CONJURED
		return csstatus.SKILL_GO_ON

	def getCatholiconType( self ):
		"""
		获得还童类型，默认为普通还童丹
		"""
		return csdefine.PET_GET_CATHOLICON

	def receive( self, caster, receiver ):
		pet = caster.pcg_getActPet()
		if pet is None:
			return
		receiver.rejuvenesce( self.getCatholiconType() )
		receiver.receiveSpell( caster.id, self.getID(), 0, 0, 0 )