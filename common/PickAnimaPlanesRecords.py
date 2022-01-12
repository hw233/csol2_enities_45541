# -*- coding: gb18030 -*-

REPEAT_HAS_ADDITION_TIME = 5.0	#重复拾取有加成时间
REPEAT_HAS_ADDITION_PERCENT= 10.0 #加成百分比

class PickAnimaPlanesRecord( object ):
	def __init__( self ):
		object.__init__( self )
		self.planesID = 0
		self.pickAnimaList = []
		self.pickAddition = 0
		self.potentialCount = 0
		self.pickCount = 0
	
	def pickAnima( self, pickRole, pickTime, rewardPotential ):
		self.pickAnimaList.append( pickTime )
		if pickTime - self.pickAnimaList[ -1 ] <= REPEAT_HAS_ADDITION_TIME:
			self.pickAddition += 1
		else:
			self.pickAddition = 0
		
		addPercent = self.pickAddition * ( REPEAT_HAS_ADDITION_PERCENT / 100 ) #添加加成
		rPotential = rewardPotential * ( 1 + addPercent )
		pickRole.addPotentialPickAnima( rPotential )
		self.potentialCount += rPotential
		self.pickCount +=1
		pickRole.client.pickAnima_upPickInfos( self.pickCount, self.pickAddition )
	
	def resertAddition( self, pickRole ):
		self.pickAddition = 0
	
	def getDictFromObj( self, obj ):
		resultDict = {}
		resultDict[ "planesID" ] = obj.planesID
		resultDict[ "pickAnimaList" ] = obj.pickAnimaList
		resultDict[ "pickAddition" ] = obj.pickAddition
		resultDict[ "potentialCount" ] = obj.potentialCount
		resultDict[ "pickCount" ] = obj.pickCount
		return resultDict
	
	def createObjFromDict( self, objDict ):
		newObj = PickAnimaPlanesRecord()
		newObj.planesID = objDict[ "planesID" ]
		newObj.pickAnimaList = objDict[ "pickAnimaList" ]
		newObj.pickAddition = objDict[ "pickAddition" ]
		newObj.potentialCount = objDict[ "potentialCount" ]
		newObj.pickCount = objDict[ "pickCount" ]
		return newObj
	
	def isSameType( self, obj ):
		return isinstance( obj, PickAnimaPlanesRecord )

class PickAnimaPlanesRecords( object ):
	def __init__( self ):
		self.datas = {}
	
	def pickAnima( self, planesID, pickRole, pickTime, rewardPotential ):
		if not self.datas.has_key( planesID ):
			record = PickAnimaPlanesRecord()
			record.planesID = planesID
			self.datas[ planesID ] = record
			
		self.datas[ planesID ].pickAnima( pickRole, pickTime, rewardPotential )
	
	def resertAddition( self, planesID, pickRole ):
		if not self.datas.has_key( planesID ):
			record = PickAnimaPlanesRecord()
			record.planesID = planesID
			self.datas[ planesID ] = record
			
		self.datas[ planesID ].resertAddition( pickRole )
	
	def getPlanesRecord( self, planesID ):
		return self.datas.get( planesID, None )
	
	def getDictFromObj( self, obj ):
		return { "pickDatas" : obj.datas.values() } 
		
	def createObjFromDict( self, dict ):
		newObj = PickAnimaPlanesRecords()
		for d in dict[ "pickDatas" ]:
			newObj.datas[ d.planesID ] = d
		
		return newObj
	
	def isSameType( self, obj ):
		return isinstance( obj, PickAnimaPlanesRecords )

g_record = PickAnimaPlanesRecord()
g_records = PickAnimaPlanesRecords()