# -*- coding:gb18030 -*-


import csstatus
import csdefine
from bwdebug import *
from Spell_Item import Spell_Item

class Spell_Item_Teleport( Spell_Item ):
	"""
	传送物品类
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		self._map = "" #地图名称
		self._direction = ( 0.0, 0.0, 0.0 ) #方向
		self._position = ( 0.0, 0.0, 0.0 ) #位置

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self._map =  dict[ "param1" ]   	#地图名称
		pos = ( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else "" ) .split(";") 	#位置
		if len( pos ) > 2:
			self._position = ( float( pos[0] ), float( pos[1] ), float( pos[2] ) )
		dir = ( dict[ "param3" ] if len( dict[ "param3" ] ) > 0 else "" ) .split(";") 	#方向
		if len( dir ) > 2:
			self._direction =  ( float( dir[0] ), float( dir[1] ), float( dir[2] ) )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		if receiver.getCurrentSpaceType() in [ csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN, csdefine.SPACE_TYPE_TOWER_DEFENSE, csdefine.SPACE_TYPE_CAMP_FENG_HUO_LIAN_TIAN ]:
			receiver.statusMessage( csstatus.SPACE_COPY_CANNOT_USE_ITEM_TELEPORT )
			return
		receiver.gotoSpace( self._map, self._position, self._direction )