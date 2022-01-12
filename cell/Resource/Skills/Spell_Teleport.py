# -*- coding: gb18030 -*-
#
# $Id: Spell_Teleport.py,v 1.3 2007-12-17 01:36:36 kebiao Exp $

"""
传送技能基础
"""

from SpellBase import *
import csstatus
import BigWorld
import csconst

class Spell_Teleport( Spell ):
	"""
	传送技能基础
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell.__init__( self )
		self._map = "" #地图名称
		self._direction = ( 0.0, 0.0, 0.0 ) #方向
		self._position = ( 0.0, 0.0, 0.0 ) #位置

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._map =  dict[ "param1" ]   	#地图名称
		s = ( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else "" ) .split(";") 	#位置
		self._position = ( float( s[0] ), float( s[1] ), float( s[2] ), ) #这么做 仅仅是统一的配置规则导致的
		s = ( dict[ "param3" ] if len( dict[ "param3" ] ) > 0 else "" ) .split(";") 	#方向
		self._direction =  ( float( s[0] ), float( s[1] ), float( s[2] ), )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		spaceLabel = BigWorld.getSpaceDataFirstForKey( receiver.spaceID, csconst.SPACE_SPACEDATA_KEY )
		if spaceLabel == self._map:
			receiver.position = self._position
			return
		receiver.gotoSpace( self._map, self._position, self._direction )

# $Log: not supported by cvs2svn $
# Revision 1.2  2007/12/06 04:21:33  kebiao
# 修改读取配置方式
#
# Revision 1.1  2007/12/03 06:29:01  kebiao
# no message
#