# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_Tong_Action.py by jy
"""
ʹ����Ʒ�ı����ж���
"""

from bwdebug import *
from Spell_Item import Spell_Item
import csstatus
import csdefine

class Spell_Item_Tong_Action( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		self._addAction = int(dict[ "param1" ]) if len( dict[ "param1" ] ) > 0 else 0
		Spell_Item.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if caster.tong_dbID <= 0:
			return
		tong = caster.tong_getTongEntity( caster.tong_dbID )
		if tong is None:
			return
		#tong.addActionVal( self._addAction )
		INFO_MSG( "Change tong(%d) aciton value by %s."%( caster.tong_dbID, caster.getName() ) )
		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		if caster.tong_dbID <= 0:
			return csstatus.TONG_NO_TONG
		tong = caster.tong_getTongEntity( caster.tong_dbID )
		if tong is None:
			return csstatus.TONG_TARGET_NOT_EXIST
		
		return Spell_Item.useableCheck( self, caster, target )