# -*- coding: gb18030 -*-
#
# $Id: TongNagualResume.py,v 1.0 214:48 2010-4-9 jiangyi Exp $

from MonsterResume import MonsterResume

class TongNagualResume( MonsterResume ):
	def __init__( self ) :
		MonsterResume.__init__( self )

	def doMsg_( self, entity, window ):
		text = MonsterResume.doMsg_( self, entity, window )
		return text

instance = TongNagualResume()