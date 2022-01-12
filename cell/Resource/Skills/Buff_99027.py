# -*- coding: gb18030 -*-
"""
������Ч��
"""

import BigWorld
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Function import newUID
from Buff_Normal import Buff_Normal
import random
import csconst
import Const
from VehicleHelper import getCurrVehicleID

STATES = csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL_PHY | csdefine.ACTION_FORBID_SPELL_MAGIC | csdefine.ACTION_FORBID_VEHICLE | csdefine.ACTION_FORBID_CALL_PET

class Buff_99027( Buff_Normal ):
	"""
	example:��贫��	BUFF	��ɫ�ڴ��ڼ䲻�ᱻ������ ���ᱻ��ҿ��ƣ� �������ģ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self.patrolPathNode = ""
		self.patrolList = ""
		self.spaceName = ""
		self.pos = ( 0, 0, 0 )
		self.direction = ( 0, 0, 0 )
		self.isSuccess = False
		self.isStop = False
		self.teleportVehicleModelNumber = 0
		self.teleportSpeed = 6.0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._loopSpeed = 1 # ��1�봥��һ��
		self.teleportVehicleModelNumber = int( dict["Param1"] )		# ���ģ�ͱ��
		if dict["Param3"]:
			self.teleportSpeed = float( dict["Param3"] )			# �ƶ��ٶ�

	def continuePatrol( self, receiver ):
		"""
		����Ѳ�� ��ɫ��ת������ ����������ϼ���Ѳ��
		"""
		self.isStop = False
		patrolList = BigWorld.PatrolPath( self.patrolList )
		if patrolList.isReady():
			self.isSuccess = receiver.doPatrol( self.patrolPathNode, patrolList )

	def updateData( self, receiver ):
		"""
		����Ѳ������
		"""
		receiver.stopMoving()
		self.isSuccess = False
		self.patrolPathNode, self.patrolList, self.spaceName, self.pos, self.direction = receiver.queryTemp( "teleportFly_data" )
		patrolList = BigWorld.PatrolPath( self.patrolList )
		if patrolList.isReady():
			self.isSuccess = receiver.doPatrol( self.patrolPathNode, patrolList )
		return


		receiver.stopMoving()
		self.isStop = True
		self.isSuccess = False
		self.patrolPathNode, self.patrolList, self.spaceName, self.pos, self.direction = receiver.queryTemp( "teleportFly_data" )
		receiver.doPatrol( self.patrolPathNode, patrolList )
		receiver.stopMoving()

	def springOnImmunityBuff( self, caster, receiver, buffData ):
		"""
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		buff = buffData[ "skill" ]
		isRayRingEffect = buff.isRayRingEffect()

		if not isRayRingEffect and buff.isMalignant(): #�Ƕ��Ե����ǹ⻷Ч�� ��ô����
			return csstatus.SKILL_BUFF_IS_RESIST
		elif isRayRingEffect:   # �ǹ⻷Ч��
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				if buffData[ "caster" ] != caster.id:
					buffData[ "state" ] |= csdefine.BUFF_STATE_DISABLED
				else:
					return csstatus.SKILL_BUFF_IS_RESIST

		return csstatus.SKILL_GO_ON

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
		actPet = receiver.pcg_getActPet()
		if actPet :
			actPet.entity.changeState( csdefine.ENTITY_STATE_FREE )
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )

		# �������
		if getCurrVehicleID( receiver ):
			receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )

		receiver.vehicleModelNum = self.teleportVehicleModelNumber
		receiver.move_speed = self.teleportSpeed

		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		receiver.effectStateInc( csdefine.EFFECT_STATE_ALL_NO_FIGHT )
		receiver.setTemp( "controlledBy_bck", receiver.controlledBy )

		receiver.controlledBy = None
		patrolPathNode, patrolList, spaceName, pos, direction = receiver.queryTemp( "teleportFly_data" )

		dctData = { "param" : { "patrolPathNode" 	: patrolPathNode, 	"patrolList" 		: patrolList, \
								 "spaceName" 		: spaceName, 		"pos" 				: pos, \
								 "direction" 		: direction,		"isSuccess" 		: False, \
							 	 "isStop"			: False,
							 }
					}

		buffData[ "skill" ] = self.createFromDict( dctData )
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #������ӵֿ�
		patrolPath = BigWorld.PatrolPath( patrolList )

		if patrolPath.isReady():
			buffData[ "skill" ].isSuccess = receiver.doPatrol( patrolPathNode, patrolPath )

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
		if receiver.popTemp( "fly_buff_exit", 0 ) == self.getID():
			return False
		
		#ע�����²��֣����ⰴ��·��Ѱ·ʱ���ֶٿ�����
		#if not self.isStop:
		#	if self.isSuccess:
		#		patrolPathNode = receiver.queryTemp( "patrolPathNode" )
		#		if patrolPathNode is None:
		#			self.isSuccess = False
		#			return Buff_Normal.doLoop( self, receiver, buffData )
		#		self.patrolPathNode = patrolPathNode
		#		patrolList = BigWorld.PatrolPath( self.patrolList )
		#		if patrolList.isReady():
		#			self.isSuccess = receiver.doPatrol( self.patrolPathNode, patrolList )
		#	else:
		#		return False

		return Buff_Normal.doLoop( self, receiver, buffData )

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
		receiver.setTemp( "fly_buff_exit", self.getID() )

		# ��ʱ��ʵ�����ߺ����Ѳ��
		receiver.setTemp( "no_continue", self.getID() )
		receiver.gotoSpace( self.spaceName, self.pos, self.direction )
		return

		receiver.appendImmunityBuff( buffData[ "skill" ] ) #������ӵֿ�
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		receiver.effectStateInc( csdefine.EFFECT_STATE_ALL_NO_FIGHT )

		receiver.setTemp( "controlledBy_bck", receiver.controlledBy )
		receiver.controlledBy = None

		try:
			self.isSuccess = receiver.doPatrol( self.patrolPathNode, BigWorld.PatrolPath( self.patrolList ) )
		except:
			DEBUG_MSG( "%i doPatrol is failed! patrolPathNode=%s, patrolList=%s" % ( receiver.id, self.patrolPathNode, self.patrolList ) )
			receiver.removeBuffByID( self.getID(), [0] )
			receiver.gotoSpace( self.spaceName, self.pos, self.direction )

		Buff_Normal.doReload( self, receiver, buffData )

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
		# ��ʱ��ʵ�����ߺ����Ѳ��
		if receiver.popTemp( "no_continue", 0 ) == self.getID():
			return

		receiver.vehicleModelNum = 0
		receiver.calcMoveSpeed()

		receiver.removeImmunityBuff( buffData[ "skill" ].getUID() )
		receiver.actCounterDec( STATES )
		receiver.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )
		receiver.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		receiver.effectStateDec( csdefine.EFFECT_STATE_ALL_NO_FIGHT )
		receiver.stopMoving()
		receiver.controlledBy = receiver.popTemp( "controlledBy_bck" )

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : { "patrolPathNode" 	: self.patrolPathNode, \
							 "patrolList" 		: self.patrolList, \
							 "spaceName" 		: self.spaceName, \
							 "pos" 				: self.pos, \
							 "direction" 		: self.direction,\
							 "isSuccess" 		: self.isSuccess,\
							 "isStop"			: self.isStop
				 			}
				 }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = Buff_99027()
		obj.__dict__.update( self.__dict__ )

		obj.patrolPathNode = data["param"][ "patrolPathNode" ]
		obj.patrolList = data["param"][ "patrolList" ]
		obj.spaceName = data["param"][ "spaceName" ]
		obj.pos = data["param"][ "pos" ]
		obj.direction = data["param"][ "direction" ]
		obj.isSuccess = data["param"][ "isSuccess" ]
		obj.isStop = data["param"][ "isStop" ]

		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
