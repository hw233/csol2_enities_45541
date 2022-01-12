# -*- coding: gb18030 -*-
#
# $Id: DartNPC.py,v 1.2 2008-09-05 03:49:51 zhangyuxing Exp $



from NPC import NPC
import BigWorld

class DartNPC( NPC ):
	"""
	NPC基类
	"""
	def __init__( self ):
		"""
		"""
		NPC.__init__( self )




	def queryDartMessage( self ):
		"""
		"""
		BigWorld.globalBases[ "DartManager" ].query(  "sm_dartCreditXinglong", 10, self.cell )
		BigWorld.globalBases[ "DartManager" ].query(  "sm_dartCreditChangping", 10, self.cell )
		BigWorld.globalBases[ "DartManager" ].query(  "sm_dartNotoriousXinglong", 10, self.cell )
		BigWorld.globalBases[ "DartManager" ].query(  "sm_dartNotoriousChangping", 10, self.cell )
		
		
		

