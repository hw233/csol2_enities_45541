# -*- coding: gb18030 -*-

import csdefine
import csstatus
from CItemBase import CItemBase

class CItemAFTime( CItemBase ):
	"""
	�Զ�ս����ֵʱ����Ʒ(˾��ɳ©)
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )
		
	def use( self, owner, target ):
		"""
		��ֵ�����Զ�ս��ʱ��
		"""
		timeAdd = int( self.query( "param1", 0 ) )
		target.base.autoFightExtraTimeCharge( timeAdd )
		ud = self.getUseDegree()
		if ud > 0:
			ud -= 1
			self.setUseDegree( ud, owner )
		if ud <=0:
			owner.removeItem_( self.getOrder(), 1, csdefine.DELETE_ITEM_USE )
		return csstatus.SKILL_GO_ON