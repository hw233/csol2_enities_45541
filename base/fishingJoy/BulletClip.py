# -*- coding:gb18030 -*-

import Love3

class BulletClip:
	"""
	一个对捕鱼炮弹的服务器端简单验证。
	根据捕鱼场大小和炮弹速度预估每个玩家同时会在捕鱼场中拥有多少颗炮弹，确定弹夹空间以便验证子弹击中时的合法性
	"""
	def __init__( self, space = 10 ):
		self.lastBulletNumber = 0
		self.space = space
		self.bullets = [None] * self.space	# 弹夹空间
		
	def reset( self ):
		for index in xrange( self.space ):
			self.bullets[index] = None
		self.lastBulletNumber = 0
		
	def fisherHit( self, fisher ):
		"""
		玩家发射炮弹，记录炮弹的相关数据以便击中时验证和捕获处理
		
		@param bulletType : 炮弹类型
		@param magnification : 发射炮弹时的倍率
		@return -1为炮弹无效( 原因可能是没弹药了 )，否则为炮弹的编号
		"""
		self.lastBulletNumber += 1
		bulletType = fisher.fish_getBulletType()
		bullet = Love3.g_fishingJoyLoader.getBullet( bulletType )
		if not bullet.fisherHit( fisher ):
			return - 1
			
		self.bullets.append( ( self.lastBulletNumber, bulletType, fisher.fish_getMagnification() ) )
		self.bullets.pop( 0 )
		return self.lastBulletNumber
		
	def fisherHitFish( self, bulletNumber ):
		"""
		1、验证编号为bulletNumber炮弹是否合法
		2、验证同时处理合法后的炮弹数据清理（炮弹击中后已失效）
		
		if 合法: return bulletData
		else:return None
		"""
		for index, bulletData in enumerate( self.bullets ):
			if bulletData is None:
				continue
			if bulletData[0] == bulletNumber:
				self.bullets[index] = None
				return bulletData
		return None
		