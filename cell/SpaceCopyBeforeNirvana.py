# -*- coding: gb18030 -*-

# 10 级剧情副本 
# alienbrain://PROJECTSERVER/创世Online/绿色版本/09_游戏世界/05_副本设计/04_剧情副本/10级剧情副本.docx
# by mushuang 

import BigWorld
from SpaceCopy import SpaceCopy
import csdefine
from bwdebug import *

SPACE_SKILL_ID = 122267001
SPACE_SKILL_BUFF_ID = 22019

class SpaceCopyBeforeNirvana( SpaceCopy ) :
	def __init__( self ):
		SpaceCopy.__init__( self )
		self._firstEntrance = True
		
	def onEnterCommon( self, baseMailbox, params ):
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		baseMailbox.cell.enterCopyBeforeNirvanaBodyChanging()
		entity = BigWorld.entities.get( baseMailbox.id, None )
		if entity:
			entity.spellTarget( SPACE_SKILL_ID, entity.id )
		else:
			baseMailbox.cell.spellTarget( SPACE_SKILL_ID, baseMailbox.id )
			
		# if 玩家是第一次进入副本 then 执行一些操作	
		if self._firstEntrance:
			self._firstEntrance = False
			self.__onFirstEntrance( baseMailbox, params )
		
	def __onFirstEntrance( self, baseMailbox, params ):
		"""
		在玩家第一次进入副本的时候做一些工作
		"""
		# 玩家第一次进入打开画卷
		scrollID = params.get( "ScrollIDOnEnter", None )
		if scrollID == None:
			ERROR_MSG( "Can't find scroll ID to open, scroll opening ignored!" )
			return
			
		baseMailbox.client.unfoldScroll( 0, scrollID )
		
	def onLeaveCommon( self, baseMailbox, params ):
		
		# 玩家出副本之前关掉场景技能
		baseMailbox.cell.removeAllBuffByBuffID( SPACE_SKILL_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE ] )
		baseMailbox.cell.end_body_changing(baseMailbox.id, "")
		
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		