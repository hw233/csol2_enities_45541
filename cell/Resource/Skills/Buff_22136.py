# -*- coding: gb18030 -*-
#


"""
������Ч��
"""
import random
import Math
import BigWorld
import time
import csstatus
import csdefine
import csconst
from bwdebug import *
from Function import newUID

import Const
from SpellBase import *
from Buff_Normal import Buff_Normal
from VehicleHelper import getCurrVehicleID


class Buff_22136( Buff_Normal ):
	"""
	�����о���Buff
	(Lv^1.5 * 3.5 + 9 ) * self.param1  #ÿ���ӻ�þ��飻
	����480����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.param1 = float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0.0 )
		

	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		����buff����ʾbuff��ÿһ������ʱӦ����ʲô��

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL�������������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		exp = ( pow(receiver.level, 1.5) * 3.5 + 9 ) * self.param1   #ÿ���ӻ�þ���
		receiver.addExp( exp, csdefine.CHANGE_EXP_DANCE_BUFF )
		DEBUG_MSG("Buff_22136 doLoop add exp:%f to playerName:%s"%(exp, receiver.playerName))
		return Buff_Normal.doLoop( self, receiver, buffData )

	def getNewBuffData( self, caster, receiver ):
		newBuffData = {}
		newBuffData[ "skill" ] = self
		newBuffData[ "persistent" ] = self.calculateTime( receiver )
		newBuffData[ "currTick" ] = 0
		newBuffData[ "caster" ] = self._casterID
		newBuffData[ "state" ] = 0
		newBuffData[ "index" ] = 0
		newBuffData[ "sourceType" ] = self.getSourceType()
		newBuffData[ "isNotIcon" ] = self.isNotIcon()
		return newBuffData

	def calculateTime( self, receiver ):
		"""
		"""
		if self._persistent <= 0: return 0
		print "receiver.DanceBuffPersistentTime =",receiver.DanceBuffPersistentTime,"persistent time = ",8 * 3600 -  receiver.DanceBuffPersistentTime
		print "test =",( (time.gmtime(receiver.LastAddDanceBuffTime)[0] == time.localtime()[0]) and (time.gmtime(receiver.LastAddDanceBuffTime)[-2] == time.localtime()[-2]) )
		if ( (time.gmtime(receiver.LastAddDanceBuffTime)[0] == time.localtime()[0]) and (time.gmtime(receiver.LastAddDanceBuffTime)[-2] == time.localtime()[-2]) ):  #ͬһ��
			if receiver.DanceBuffPersistentTime < 8 * 3600 :   #��������buff�ۼ�ʱ�䲻��8��ʱ
				return int(time.time() + 8 * 3600 -  receiver.DanceBuffPersistentTime)   #�����buffʱ�������ʱ��    
			else :
				return 0  #�����buffʱ���Ѿ��ﵽ��,�ٴμӵ�ʱ��û������
		return time.time() + self._persistent

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		#���Լ�����buff�����
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.LastAddDanceBuffTime = time.time() #��¼������buff��ʱ��
		DEBUG_MSG("Buff_22136 doBegin")


	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�����¼��صĴ���
		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		exp = ( pow(receiver.level, 1.5) * 3.5 + 9 ) * self.param1  #ÿ���ӻ�þ���
		receiver.addExp( exp, csdefine.CHANGE_EXP_DANCE_BUFF )	
		DEBUG_MSG("Buff_22136 doReload add exp:%f to playerName:%s"%(exp, receiver.playerName))
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		exp = ( pow(receiver.level, 1.5) * 3.5 + 9 ) * self.param1  #ÿ���ӻ�þ���
		receiver.addExp( exp, csdefine.CHANGE_EXP_DANCE_BUFF )
		DEBUG_MSG("Buff_22136 doEnd add exp:%f to playerName:%s"%(exp, receiver.playerName))
		if receiver.findBuffByBuffID(csconst.DancingKingBuffID):  #������buffʱ�䵽��ʱ��ҲҪȥ������buff
			receiver.removeBuffByID( csconst.DancingKingBuffID,  [csdefine.BUFF_INTERRUPT_NONE] )   #buffʱ�䵽�ˣ��Զ�ȥ������buff		
		Buff_Normal.doEnd( self, receiver, buffData )
		

	def createFromDict( self, data ):
		"""
		virtual method.	
		@type data: dict
		"""
		obj = Buff_22136()
		obj.__dict__.update( self.__dict__ )
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj

