# -*- coding: gb18030 -*-

# 10 �����鸱�� 
# alienbrain://PROJECTSERVER/����Online/��ɫ�汾/09_��Ϸ����/05_�������/04_���鸱��/10�����鸱��.docx
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
			
		# if ����ǵ�һ�ν��븱�� then ִ��һЩ����	
		if self._firstEntrance:
			self._firstEntrance = False
			self.__onFirstEntrance( baseMailbox, params )
		
	def __onFirstEntrance( self, baseMailbox, params ):
		"""
		����ҵ�һ�ν��븱����ʱ����һЩ����
		"""
		# ��ҵ�һ�ν���򿪻���
		scrollID = params.get( "ScrollIDOnEnter", None )
		if scrollID == None:
			ERROR_MSG( "Can't find scroll ID to open, scroll opening ignored!" )
			return
			
		baseMailbox.client.unfoldScroll( 0, scrollID )
		
	def onLeaveCommon( self, baseMailbox, params ):
		
		# ��ҳ�����֮ǰ�ص���������
		baseMailbox.cell.removeAllBuffByBuffID( SPACE_SKILL_BUFF_ID, [ csdefine.BUFF_INTERRUPT_NONE ] )
		baseMailbox.cell.end_body_changing(baseMailbox.id, "")
		
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		