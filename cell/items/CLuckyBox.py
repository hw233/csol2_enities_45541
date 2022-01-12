# -*- coding: gb18030 -*-

from bwdebug import *
from CItemBase import CItemBase
import csconst
import csstatus

class CLuckyBox( CItemBase ):
	"""
	天降宝盒：招财、进宝
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )
		
	def checkUse( self, owner ):
		"""
		天降宝盒对玩家的使用限制
		"""
		checkResult = CItemBase.checkUse( self, owner )
		if checkResult != csstatus.SKILL_GO_ON:
			return checkResult
			
		if self.getLevel() > owner.level + csconst.LUCKY_BOX_USE_LEVEL_CHECK:
			return csstatus.CIB_LUCKYBOX_CANT_USE_LEVEL_LACK
			
		return csstatus.SKILL_GO_ON
		