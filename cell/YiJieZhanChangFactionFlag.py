# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.6 2008-01-08 06:25:59 yangkai Exp $

from NPCObject import NPCObject
from interface.CombatUnit import CombatUnit
import BigWorld
import csdefine
import ECBExtend
from bwdebug import *
import csstatus
import cschannel_msgs
from QuestBox import QuestBox
import time

FACTION_FLAG_MODEL_TIAN	= "gw99913"		# 天阵营柱模型
FACTION_FLAG_MODEL_DI	= "gw99914"		# 地阵营柱模型
FACTION_FLAG_MODEL_REN	= "gw99915"		# 人阵营柱模型

class YiJieZhanChangFactionFlag( QuestBox ) :
	"""
	异界战场阵营柱
	"""

	def __init__( self ) :
		QuestBox.__init__( self )
	
	def onItemsArrived( self, caster, itemList ):
		"""
		define method
		"""
		if not caster : return
		if not ( BigWorld.entities.has_key( caster.id ) and caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ) ) :
			return
		newFaction = caster.yiJieFaction
		oldFaction = self.ownBattleFaction
		if newFaction != 0 and oldFaction == newFaction :
			caster.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_CANNOT_OCCUPY_AGAIN, "" )
			return
		elif caster.yiJieAlliance != 0 and oldFaction == caster.yiJieAlliance :
			caster.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_CANNOT_OCCUPY_ALLIANCE, "" )
			return
		
		self.onReceiveSpell( caster, None )
		self.getCurrentSpaceBase().cell.onOccupyFactionFlag( self.id, newFaction )
		self.ownBattleFaction = newFaction
		
		factionToModel = {	csdefine.YI_JIE_ZHAN_CHANG_FACTION_TIAN		:	FACTION_FLAG_MODEL_TIAN,
							csdefine.YI_JIE_ZHAN_CHANG_FACTION_DI		:	FACTION_FLAG_MODEL_DI,
							csdefine.YI_JIE_ZHAN_CHANG_FACTION_REN		:	FACTION_FLAG_MODEL_REN,
							}
		self.setModelNumber( factionToModel[ newFaction ] )
