# -*- coding:gb18030 -*-

import csstatus
import csdefine
from bwdebug import *
import Const
from Buff_Normal import Buff_Normal
from Function import newUID

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_JUMP


class Buff_107021( Buff_Normal ):
	"""
	dota�����ŵ�F���������Ӷ�Ŀ�����ѣ��/����/��˯Ч��
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self.effectInterval = 1							# Ч����������ʱ����ע�⣺������ܴ��ڷ�Ч����������
		self.noEffectInterval = 1						# ��Ч����������ʱ��
		self.effect = csdefine.EFFECT_STATE_VERTIGO		# Ĭ�ϵ�Ч��
		self.isEffect = False							# Ч���Ƿ���������
		self.tickCount = 0								# ����Ч��/������Ч��״̬����ʱ����ÿһ��tick��1��
		
	def init( self, data ):
		"""
		"""
		Buff_Normal.init( self, data )
		self.effect = int( data["Param1"] )				# Ĭ�ϵ�Ч��
		self.effectInterval = int( data["Param2"] )		# Ч����������ʱ����ע�⣺������ܴ��ڷ�Ч����������
		self.noEffectInterval = int( data["Param3"] )	# ��Ч����������ʱ��
		
	def doBeginEffect( self, receiver ):
		"""
		��ʼЧ��
		"""
		# �����ƶ����ƣ���ȷ��buff���ƶ�����Ч����Ч by����
		if receiver.isMoving():
			receiver.stopMoving()
		# ִ�и���Ч��
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( self.effect )
		self.isEffect = True
		self.tickCount = 0
		
	def doEndEffect( self, receiver ):
		"""
		����Ч��
		"""
		receiver.effectStateDec( self.effect )
		receiver.actCounterDec( STATES )
		
		self.isEffect = False
		self.tickCount = 0
		
		
	def doBegin( self, receiver, buffData ):
		"""
		"""
		if receiver.attrIntonateTimer > 0 and receiver.attrIntonateSkill.getType() in Const.INTERRUPTED_BASE_TYPE or\
			( receiver.attrHomingSpell and receiver.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			receiver.interruptSpell( csstatus.SKILL_IN_BLACKOUT )
		self.doBeginEffect( receiver )
		
	def doLoop( self, receiver, buffData ):
		"""
		"""
		self.tickCount += 1
		if self.isEffect:
			if self.tickCount == self.effectInterval:
				self.doEndEffect( receiver )
		else:
			if self.tickCount == self.noEffectInterval:
				self.doBeginEffect( receiver )
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def doEnd( self, receiver, buffData ):
		Buff_Normal.doEnd( self, receiver, buffData )
		self.doEndEffect( receiver )
		
	def addToDict( self ):
		"""
		"""
		return { "param": { "isEffect":self.isEffect, "tickCount":self.tickCount } }
		
	def createFromDict( self, data ):
		"""
		"""
		obj = Buff_107021()
		obj.__dict__.update( self.__dict__ )
		obj.isEffect = data["param"]["isEffect"]
		obj.tickCount = data["param"]["tickCount"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
		