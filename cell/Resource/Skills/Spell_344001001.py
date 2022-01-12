# -*- coding: gb18030 -*-

from bwdebug import *
from Spell_Item import Spell_Item
from Spell_TeleportBase import Spell_TeleportBase
import csstatus
import csconst
import csdefine
import BigWorld

class Spell_344001001( Spell_Item, Spell_TeleportBase ):
	"""
	唤师指环
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		Spell_TeleportBase.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		Spell_TeleportBase.init( self, dict )
		
	def useableCheck( self, caster, target ):
		"""
		是否可以使用技能
		"""
		state = Spell_Item.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state
		state = Spell_TeleportBase.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state
		if not caster.hasMaster():
			return csstatus.TEACH_RING_CANT_TELEPORT_NOT_MASTER
		if caster.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
			return csstatus.CANT_CALL_MASTER_THIS_MAP
		masterMB = caster.getMasterMB()
		if masterMB is None:
			DEBUG_MSG( "师父不在线" )
			return csstatus.CANT_CALL_MASTER_OFFLINE
		return csstatus.SKILL_GO_ON
		
	def receive( self, caster, target ):
		"""
		"""
		masterMB = caster.getMasterMB()
		if masterMB is None:
			DEBUG_MSG( "师父不在线" )
			self.statusMessage( csstatus.CANT_CALL_MASTER_OFFLINE )
			return
			
		spaceName = caster.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		lineNumber = caster.getCurrentSpaceLineNumber()
		masterMB.cell.teach_prenticeCall( caster.getName(), caster.databaseID, spaceName, lineNumber, caster.position, caster.direction )
		