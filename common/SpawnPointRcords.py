# -*- coding: gb18030 -*-
class SpawnPointRcords( object ):
	def __init__( self ):
		self.record = {}	
	
	def add( self, planesID, entityID ):
		if not self.record.has_key( planesID ):
			self.record[ planesID ] = []

		self.record[ planesID ].append( entityID )
	
	def get( self, planesID ):
		return self.record.get( planesID, [] )
	
	def getAll( self ):
		result = []
		for v in self.record.values():
			result.extend( v )
			
		return result
	
	def get( self, planesID ):
		return self.record.get( planesID, [] )
	
	def getDictFromObj( self, obj ):
		result = []
		for k, list in obj.record.iteritems():
			d = {}
			d[ "planesID" ] = k
			d[ "spawnList" ] = list
			result.append( d )

		return { "record" : result } 
		
	def createObjFromDict( self, dict ):
		obj = SpawnPointRcords()
		record = dict[ "record" ]
		for r in record: 
			obj.record[ r[ "planesID" ] ] = r[ "spawnList" ]
		return obj
	
	def isSameType( self, obj ):
		return isinstance( obj, SpawnPointRcords )

g_spawnPointRecords= SpawnPointRcords()