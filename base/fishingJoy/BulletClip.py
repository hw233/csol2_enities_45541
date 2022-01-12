# -*- coding:gb18030 -*-

import Love3

class BulletClip:
	"""
	һ���Բ����ڵ��ķ������˼���֤��
	���ݲ��㳡��С���ڵ��ٶ�Ԥ��ÿ�����ͬʱ���ڲ��㳡��ӵ�ж��ٿ��ڵ���ȷ�����пռ��Ա���֤�ӵ�����ʱ�ĺϷ���
	"""
	def __init__( self, space = 10 ):
		self.lastBulletNumber = 0
		self.space = space
		self.bullets = [None] * self.space	# ���пռ�
		
	def reset( self ):
		for index in xrange( self.space ):
			self.bullets[index] = None
		self.lastBulletNumber = 0
		
	def fisherHit( self, fisher ):
		"""
		��ҷ����ڵ�����¼�ڵ�����������Ա����ʱ��֤�Ͳ�����
		
		@param bulletType : �ڵ�����
		@param magnification : �����ڵ�ʱ�ı���
		@return -1Ϊ�ڵ���Ч( ԭ�������û��ҩ�� )������Ϊ�ڵ��ı��
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
		1����֤���ΪbulletNumber�ڵ��Ƿ�Ϸ�
		2����֤ͬʱ����Ϸ�����ڵ����������ڵ����к���ʧЧ��
		
		if �Ϸ�: return bulletData
		else:return None
		"""
		for index, bulletData in enumerate( self.bullets ):
			if bulletData is None:
				continue
			if bulletData[0] == bulletNumber:
				self.bullets[index] = None
				return bulletData
		return None
		