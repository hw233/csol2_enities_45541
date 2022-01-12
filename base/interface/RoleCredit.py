# -*- coding: gb18030 -*-
#
# $Id: RoleCredit.py,v 1.1 2008-07-19 01:51:18 wangshufeng Exp $


import BigWorld
from bwdebug import *
import csdefine
import csconst
import csstatus


class RoleCredit:
	"""
	角色的声望、称号、荣誉interface
	"""
	def __init__( self ):
		"""
		"""
		pass
		
	def sendTitleName( self, titleID ):
		"""
		Define method.
		发送师傅的名字给cell
		"""
		titleString = ""
		if titleID == csdefine.TITLE_TEACH_PRENTICE_ID and self.teach_masterItem:
			titleString = self.teach_masterItem.playerName
		elif titleID == csdefine.TITLE_ALLY_ID:
			titleString = self.allyTitle
		elif titleID == csdefine.TITLE_COUPLE_MALE_ID or titleID == csdefine.TITLE_COUPLE_FEMALE_ID:
			titleString = self.couple_lover.playerName
		self.cell.receiveTitleName( titleID, titleString )
		
#
# $Log: not supported by cvs2svn $
#
#