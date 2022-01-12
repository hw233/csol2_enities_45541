# -*- coding:gb18030 -*-

import csdefine
import Const
from Buff_Normal import Buff_Normal
import BigWorld
from bwdebug import *

class Buff_8007( Buff_Normal ):
	"""
	npc�ڿ���Ѳ�ߵĹ���
	
	param1����Ѳ��·����·��id
	param2����Ѳ��·��id
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self.patrolNode = ""
		self.graphID = ""
		
	def init( self, data ):
		"""
		"""
		Buff_Normal.init( self, data )
		self.patrolNode = data["Param1"]	# ��·����·��id
		self.graphID = data["Param2"]		# Ѳ��·��id
		
	def doBegin( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		if self.graphID != "":
			patrolList = BigWorld.PatrolPath( self.graphID )
			receiver.doPatrol( self.patrolNode, patrolList )
		else:
			receiver.doPatrol()
		receiver.addFlag( csdefine.ENTITY_FLAG_MONSTER_FLY )
		
	def doLoop( self, receiver, buffData ):
		"""
		"""
		if not receiver.canPatrol:
			return False
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeFlag( csdefine.ENTITY_FLAG_MONSTER_FLY )
		