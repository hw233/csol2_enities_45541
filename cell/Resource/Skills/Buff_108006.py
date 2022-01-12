# -*- coding: gb18030 -*-
#
# $Id: Buff_108001.py,v 1.12 2008-07-04 03:50:57 kebiao Exp $

"""
������Ч��
"""
import random
import Math
import BigWorld

import csstatus
import csdefine
from bwdebug import *
from Function import newUID

import Const
from SpellBase import *
from Buff_Normal import Buff_Normal
from VehicleHelper import getCurrVehicleID

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_JUMP | csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_SPELL_PHY | csdefine.ACTION_FORBID_SPELL_MAGIC | csdefine.ACTION_FORBID_VEHICLE | csdefine.ACTION_FORBID_CALL_PET

class Buff_108006( Buff_Normal ):
	"""
	example:ʹĿ���Ϊһֻ���ܣ����ܿ��ƣ��޷�ʹ�ü��ܣ��ܵ�����ʱ�ָ�������20�롣�������ڼ䣬Ŀ�꽫ÿ��ָ�10%�������ͷ�����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self.isEnd = False
		self.currModelNumber = ""
		self.currModelScale = 1.0
		#self.__targetPos = () # ��������ʼλ�ã�������ܺ����Գ�ʼλ��Ϊ����һ����Χ������߶���

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = dict[ "Param1" ]
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 ) / 100.0
		self._p3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 ) / 100.0

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
		receiver.setHP( receiver.HP + receiver.HP_Max * self._p3 )
		receiver.setMP( receiver.MP + receiver.MP_Max * self._p3 )
		
		if not ( receiver.effect_state & csdefine.EFFECT_STATE_BE_HOMING ) :
			if not receiver.queryTemp( "BODY_CHANGE_POS", None ):
				receiver.setTemp( "BODY_CHANGE_POS", Math.Vector3( receiver.position ) )
			receiver.doRandomRun( receiver.queryTemp( "BODY_CHANGE_POS" ), 5.0 ) # ��һ����Χ������߶�
		else:
			receiver.removeTemp( "BODY_CHANGE_POS" )
		return Buff_Normal.doLoop( self, receiver, buffData ) and self.isEnd != True

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
		Buff_Normal.doBegin( self, receiver, buffData )

		buffData[ "skill" ] = self.createFromDict( self.addToDict() )
		self = buffData[ "skill" ]
		if receiver.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) and receiver.isRideOwner: # ����ڳ������ˣ�ǿ�������ڳ�
			receiver.disMountEntity( receiver.ownerID, receiver.ownerID )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if receiver.vehicle and receiver.vehicle.isSlaveDart(): # ��������ڳ��ϣ�ǿ�������ڳ�
				receiver.vehicle.disMountEntity( receiver.id, receiver.id )
			if getCurrVehicleID( receiver ): # �����������ϣ�ǿ�������
				receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )
			receiver.setTemp( "BODY_CHANGE_NOT_CHANGE_STATE", True )
			receiver.begin_body_changing( self._p1, self._p2 )
			receiver.setTemp( "BODY_CHANGE_NOT_CHANGE_STATE", False )
		else:
			self.currModelNumber = receiver.modelNumber
			self.currModelScale = receiver.modelScale
			receiver.modelNumber = self._p1
			receiver.planesAllClients( "onSetModelScaleTime", (0.0, ) ) #����Ҫ����ʱ��
			receiver.modelScale = self._p2

		receiver.appendAttackerHit(buffData[ "skill" ])
		if receiver.attrIntonateTimer > 0 and receiver.attrIntonateSkill.getType() in Const.INTERRUPTED_BASE_TYPE or\
			( receiver.attrHomingSpell and receiver.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			receiver.interruptSpell( csstatus.SKILL_IN_BLACKOUT )
		# ִ�и���Ч��
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_VERTIGO )
		

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
		if receiver.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) and receiver.isRideOwner: # ����ڳ������ˣ�ǿ�������ڳ�
			receiver.disMountEntity( receiver.ownerID, receiver.ownerID )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if receiver.vehicle and receiver.vehicle.isSlaveDart(): # ��������ڳ��ϣ�ǿ�������ڳ�
				receiver.vehicle.disMountEntity( receiver.id, receiver.id )
			if getCurrVehicleID( receiver ): # �����������ϣ�ǿ�������
				receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )
			receiver.setTemp( "BODY_CHANGE_NOT_CHANGE_STATE", True )
			receiver.begin_body_changing( self._p1, self._p2 )
			receiver.setTemp( "BODY_CHANGE_NOT_CHANGE_STATE", False )
		else:
			self.currModelNumber = receiver.modelNumber
			self.currModelScale = receiver.modelScale
			receiver.modelNumber = self._p1
			receiver.planesAllClients( "onSetModelScaleTime", (0.0,) ) #����Ҫ����ʱ��
			receiver.modelScale = self._p2

		receiver.appendAttackerHit(buffData[ "skill" ])
		# ִ�и���Ч��
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_VERTIGO )
		

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		if receiver.isMoving(): # ���BUFF����ʱ����������߶�������ֹͣ
			receiver.stopMoving()
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.setTemp( "ROLE_BODY_BUFF_END", True )
			receiver.setTemp( "BODY_CHANGE_NOT_CHANGE_STATE", True )
			receiver.end_body_changing( receiver.id, "" )
			receiver.setTemp( "ROLE_BODY_BUFF_END", False )
			receiver.setTemp( "BODY_CHANGE_NOT_CHANGE_STATE", False )
		else:
			receiver.modelNumber = self.currModelNumber
			receiver.planesAllClients( "onSetModelScaleTime", (0.0,) ) #����Ҫ����ʱ��
			receiver.modelScale = self.currModelScale

		receiver.removeAttackerHit( buffData[ "skill" ].getUID() )
		receiver.effectStateDec( csdefine.EFFECT_STATE_VERTIGO )
		receiver.actCounterDec( STATES )
		
		receiver.removeTemp( "BODY_CHANGE_POS" )
	
	def springOnDamage( self, caster, skill ):
		"""
		�����˺���
		"""
		self.isEnd = True

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�
		
		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : { "isEnd" : self.isEnd, "currModelNumber" : self.currModelNumber, "currModelScale" : self.currModelScale } }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�
		
		@type data: dict
		"""
		obj = Buff_108006()
		obj.__dict__.update( self.__dict__ )
		obj.isEnd = data["param"]["isEnd"]
		self.currModelNumber = data["param"]["currModelNumber"]
		self.currModelScale = data["param"]["currModelScale"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )		
		else:
			obj.setUID( data[ "uid" ] )		
		return obj

#
# $Log: not supported by cvs2svn $
#
# 
#