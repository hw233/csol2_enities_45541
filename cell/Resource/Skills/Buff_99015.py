# -*- coding: gb18030 -*-
#


from bwdebug import *
from Buff_Normal import Buff_Normal
import csconst
import csdefine

class Buff_99015( Buff_Normal ):
	"""
	灵药秘术
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )

	def init( self, pyDict ):
		"""
		"""
		Buff_Normal.init( self, pyDict )

	def receive( self, caster, receiver ):
		"""
		Virtual method.
		"""
		if receiver.getState() == csdefine.ENTITY_STATE_DEAD:
			return

		buffs = receiver.findBuffsByBuffID( self._buffID )
		if len( buffs ) > 0:		# 已存在相同类型的buff
			buffIndex = buffs[0]
			buffdata = receiver.getBuff( buffIndex )
			buffdata["persistent"] += self._persistent
			receiver.client.onUpdateBuffData( buffIndex, buffdata )
		else:
			receiver.addBuff( self.getNewBuffData( caster, receiver ) )

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method.
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.addFlag( csdefine.ROLE_FLAG_ICHOR )

	def doReload( self, receiver, buffData ):
		"""
		Virtual method.
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.addFlag( csdefine.ROLE_FLAG_ICHOR )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method.
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeFlag( csdefine.ROLE_FLAG_ICHOR )
