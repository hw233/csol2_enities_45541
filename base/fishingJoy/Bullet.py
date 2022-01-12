# -*- coding:gb18030 -*-

import csdefine
import Love3

class Bullet:
	def __init__( self, type, value ):
		self.type = type
		self.value = value
	
	def getType( self ):
		return self.type
		
	def getValue( self ):
		return self.value
		
	def addFisherEarnings( self, fisher, earnings, loss ):
		pass
		
	def getFishValue( self, fish ):
		return
		
	def fisherHit( self, fisher ):
		pass
		
	def getCaptureRateAmend( self, fisher, fish ):
		return
		
class MoneyBullet( Bullet ):
	def __init__( self, type, value ):
		Bullet.__init__( self, type, value )
		self.moneyType = csdefine.CURRENCY_TYPE_MONEY
		
	def getFishValue( self, fish ):
		return fish.getMoneyValue()
		
	def addFisherEarnings( self, fisher, earnings, loss ):
		fisher.addMoneyEarnings( earnings, loss )
		
	def fisherHit( self, fisher ):
		if fisher.payFishingJoyMoney( self.value * fisher.fish_getMagnification() ):
			return True
		return False
		
	def getCaptureRateAmend( self, fisher, fish ):
		return Love3.g_fishingJoyLoader.getCaptureRateAmend( self.moneyType, fish.getType(), fisher.getMoneyLoss() )
		
	def resetFisherLoss( self, fisher ):
		fisher.resetMoneyLoss()
		
class SilverBullet( Bullet ):
	def __init__( self, type, value ):
		Bullet.__init__( self, type, value )
		self.moneyType = csdefine.CURRENCY_TYPE_SILVER
		
	def getFishValue( self, fish ):
		return fish.getSilverValue()
		
	def addFisherEarnings( self, fisher, earnings, loss ):
		fisher.addSilverEarnings( earnings, loss )
		
	def fisherHit( self, fisher ):
		if fisher.payFishingJoySilver( self.value * fisher.fish_getMagnification() ):
			return True
		return False
		
	def getCaptureRateAmend( self, fisher, fish ):
		return Love3.g_fishingJoyLoader.getCaptureRateAmend( self.moneyType, fish.getType(), fisher.getSilverLoss() )
		
	def resetFisherLoss( self, fisher ):
		fisher.resetSilverLoss()