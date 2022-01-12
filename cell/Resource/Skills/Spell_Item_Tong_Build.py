# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_Tong_Build.py by jy
"""
使用物品改变帮会建设度
"""

from bwdebug import *
from Spell_Item import Spell_Item
import csstatus
import csdefine

class Spell_Item_Tong_Build( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		self._addBuild = int(dict[ "param1" ]) if len( dict[ "param1" ] ) > 0 else 0
		Spell_Item.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if caster.tong_dbID <= 0:
			return
		tong = caster.tong_getTongEntity( caster.tong_dbID )
		if tong is None:
			return
		#tong.addBuildVal( self._addBuild )
		INFO_MSG( "Change tong(%d) build value by %s."%( caster.tong_dbID, caster.getName() ) )
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