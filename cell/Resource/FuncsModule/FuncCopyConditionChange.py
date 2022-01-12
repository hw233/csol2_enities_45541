# -*- coding: gb18030 -*-

# �Ի�������ǰ���������ı�
# by ganjinxing 2011-12-7

# bigworld
import BigWorld
# common
from bwdebug import EXCEHOOK_MSG
# cell
from Function import Function


class FuncCopyConditionChange( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self._conditon = section.readString( 'param1' )
		self._value = section.readString( 'param2' )

	def do( self, player, talkEntity = None ) :
		"""
		"""
		try:
			spaceEntity = BigWorld.entities[ player.getCurrentSpaceBase().id ]
		except KeyError, errStr :
			EXCEHOOK_MSG( errStr )
			return
		spaceEntity.onConditionChange( { self._conditon : self._value } )	# ���spaceEntity��None���Ǿ���������

	def valid( self, player, talkEntity = None ) :
		"""
		"""
		return True
