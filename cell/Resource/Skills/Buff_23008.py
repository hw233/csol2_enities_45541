# -*- coding:gb18030 -*-

from bwdebug import *
from Buff_Normal import Buff_Normal
import time
from Function import newUID

class Buff_23008( Buff_Normal ):
	"""
	��һ��ʱ�����ܵ��˺���һ���ٷֱ�ת��Ϊ�����������
	"""
	def __init__( self ):
		Buff_Normal.__init__( self )
		self.transferTime = 0		# ת���˺�Ϊ����������ʱ��
		self.transferPercent = 0	# ת���˺�����
		self.transferBeginTime = 0	# ת���˺�Ϊ��������ʼʱ��
		self.transferValue = 0		# ת���ķ���ֵ
		
	def init( self, data ):
		"""
		"""
		Buff_Normal.init( self, data )
		self.transferTime = float( data["Param1"] if len( data["Param1"] ) > 0 else 0 )
		self.transferPercent = float( data["Param2"] if len( data["Param2"] ) > 0 else 0 ) / 100
		
	def doBegin( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		self.transferBeginTime = time.time()
		receiver.appendVictimAfterDamage( buffData[ "skill" ] )

	def doReload( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		self.transferBeginTime = time.time()
		receiver.appendVictimAfterDamage( buffData[ "skill" ] )
		
	def doEnd( self, receiver, buffData ):
		"""
		virtual method.
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeVictimAfterDamage( buffData[ "skill" ].getUID() )
		receiver.armor_value -= self.transferValue
		receiver.calcArmor()
		# ����buff�ҽӵ�receiver����ʱ��ʹ�õĻ�����ͬһ����������buffʵ���������������ֵ
		self.transferBeginTime = 0	# ת���˺�Ϊ��������ʼʱ��
		self.transferValue = 0		# ת���ķ���ֵ
		
	def springOnDamage( self, caster, receiver, skill, damage ):
		"""
		�ܵ��˺�ʱ�Ĵ���
		"""
		if time.time() - self.transferBeginTime > self.transferTime:
			return
			
		defendValue = int( damage * self.transferPercent )
		receiver.armor_value += defendValue
		receiver.calcArmor()
		self.transferValue += defendValue
		
	def addToDict( self ):
		"""
		"""
		return { "param":{"transferValue":self.transferValue, "transferBeginTime":self.transferBeginTime}, "uid":self.getUID() }
		
	def createFromDict( self, data ):
		"""
		"""
		obj = Buff_23008()
		obj.__dict__.update( self.__dict__ )
		paramDict = data["param"]
		obj.transferValue = paramDict["transferValue"]
		obj.transferBeginTime = paramDict["transferBeginTime"]
		try:
			uid = data["uid"]
		except KeyError:
			uid = 0
		if uid == 0:
			uid = newUID()
		obj.setUID( uid )
		return obj
		