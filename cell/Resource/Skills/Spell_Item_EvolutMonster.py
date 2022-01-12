# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_Dart_Add_Speed.py,v 1.1 2008-09-05 03:42:03 zhangyuxing Exp $

from SpellBase import *
from Spell_BuffNormal import Spell_ItemBuffNormal
import csstatus
import BigWorld
import csconst
import csdefine
import csarithmetic

class Spell_Item_EvolutMonster( Spell_ItemBuffNormal ):
	"""
	净化怪物
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_ItemBuffNormal.__init__( self )	

			
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_ItemBuffNormal.init( self, dict )
		self.param1 = ( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else "" ) 		#要进化的怪物id

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		receiver.setTemp( "evolute_player_id", caster.id )
		Spell_ItemBuffNormal.receive( self, caster, receiver )
		

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		entity = target.getObject()
		if not entity.getEntityType() in [ csdefine.ENTITY_TYPE_NPC, csdefine.ENTITY_TYPE_MONSTER ] or entity.className != self.param1:
			return csstatus.SKILL_USE_ITEM_CNNOT_EVOLUTE
		return Spell_ItemBuffNormal.useableCheck( self, caster, target )