# -*- coding: gb18030 -*-

class BuffOddsData( object ):
	def __init__( self ):
		self.datas = {}
	
	def getOdds( self, skillID ):
		return self.datas.get( skillID, 0.0 )
	
	def setOdds( self, skillID, odds ):
		self.datas[ skillID ] = odds
	
	def addOdds( self, skillID, odds ):
		if not self.datas.has_key( skillID ):
			self.datas[ skillID ] = 0
		
		self.datas[ skillID ] += odds
	
	def removeOdds( self, skillID ):
		self.datas.pop( skillID, 0.0 )
	
	def decOdds( self, skillID, odds ):
		if self.datas.has_key( skillID ):
			self.datas[ skillID ] -= odds

	def getDictFromObj( self, obj ):
		dataList = []
		for skill, odds in self.datas.iteritems():
			newDict = {}
			newDict[ "skillID" ] = skill
			newDict[ "odds" ] = odds
			dataList.append( newDict )
		
		return { "datas" : dataList }
		
	def createObjFromDict( self, dict ):
		newObj = BuffOddsData()
		oddsData = dict[ "datas" ]
		for data in oddsData:
			newObj.setOdds( data[ "skillID" ], data[ "odds" ] )
		return newObj
	
	def isSameType( self, obj ):
		return isinstance( obj, BuffOddsData )

g_buffOddsData = BuffOddsData()