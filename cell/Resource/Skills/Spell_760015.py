# -*- coding: gb18030 -*-
#
#
#

from bwdebug import *
import random
from SpellBase import *
from Spell_Race_Item import Spell_Race_Item
import BigWorld
import csconst
import csdefine
import csstatus
import math
import Math


class Spell_760015( Spell_Race_Item ):
	"""
	产生泥潭
	"""
	def __init__( self ):
		"""
		"""
		Spell_Race_Item.__init__( self )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		position = caster.position
		yaw = caster.yaw
		offset = random.randint( 3, 5 )
		newPos = Math.Vector3( position ) + Math.Vector3( offset * math.sin( yaw + math.pi  ), 0.0, offset * math.cos( yaw + math.pi  ) )
		caster.createNPCObject( "30111324", newPos, caster.direction, {"trapOnly": True}) 
		Spell_Race_Item.receive( self, caster, receiver )