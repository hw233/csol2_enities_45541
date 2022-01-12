# -*- coding: gb18030 -*-
#
# $Id: Spell_PlayerTeleport.py,v 1.1 2008-07-24 08:40:51 huangdong Exp $

"""
Spell技能类。
"""
import BigWorld
from bwdebug import *
from SpellBase import *
from gbref import rds
from config.client.labels.skills import lbs_Spell_PlayerTeleport

#ReliveBindNPCList = { "feng_ming":"" }
class Spell_PlayerTeleport( Spell ):
	def __init__( self ):
		"""
		从sect构造SkillBase
		@param sect:			技能配置文件的XML Root Section
		@type sect:				DataSection
		"""
		Spell.__init__( self )


	def getDescription( self ):
		"""
		传送技能需要单独的描述,用以增加当前复活点记录地区的信息
		"""
		player = BigWorld.player()
		spaceLabel = player.reviveSpace
		position = player.revivePosition
		try:
			areaStr = rds.mapMgr.getArea( spaceLabel, position ).name
		except AttributeError:
			return lbs_Spell_PlayerTeleport[1]
		return self._datas[ "Description" ] % (player.getWholeAreaBySpaceLabel(spaceLabel),areaStr)
