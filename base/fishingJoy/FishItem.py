# -*- coding:gb18030 -*-

class FishingItem:
	def __init__( self, data ):
		self.type = data[ "type" ]
		
	def getType( self ):
		return self.type
		
	def attach( self, owner ):
		pass
		
	def detach( self ):
		pass
		
class MagnificationCard( FishingItem ):
	def __init__( self, data ):
		FishingItem.__init__( self, data ) 
		self.persistent = data[ "persistent" ]
		self.magnification = data[ "magnification" ] - 1	# 配置为倍数，增加的时候需要减去1
		self.amount = data[ "amount" ]
		
	def getMagnification( self ):
		return self.magnification
		
	def getPersistent( self ):
		return self.persistent
		
	def getAmount( self ):
		return self.amount
		
	def attach( self, fisher ):
		fisher.fish_addMagnification( self.magnification )
		
	def detach( self, fisher ):
		fisher.fish_addMagnification( -self.magnification )
		