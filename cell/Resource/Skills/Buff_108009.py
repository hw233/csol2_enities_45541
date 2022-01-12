# -*- coding: gb18030 -*-
#
"""
������Ч��
"""

import BigWorld
import random
import Math
from Buff_Normal import Buff_Normal
import csdefine
import csstatus
from Function import newUID
import Const

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_JUMP | csdefine.ACTION_FORBID_USE_ITEM | csdefine.ACTION_FORBID_SPELL_PHY | csdefine.ACTION_FORBID_SPELL_MAGIC | csdefine.ACTION_FORBID_VEHICLE | csdefine.ACTION_FORBID_CALL_PET

class Buff_108009( Buff_Normal ):
	"""
	example:�Ӵ�
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self.moveRadius = 0.0
		self.moveSpeed = 0.0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._loopSpeed = 1.0
		self.moveRadius = float( dict["Param1"] if len( dict["Param1"] ) > 0 else 0 )	# �Ӵܰ뾶
		self.moveSpeed = float( dict["Param2"] if len( dict["Param2"] ) > 0 else 0 )	# �Ӵ��ٶ�
		
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

		# ���ʩ��
		if receiver.attrIntonateTimer > 0 and receiver.attrIntonateSkill.getType() in Const.INTERRUPTED_BASE_TYPE or\
			( receiver.attrHomingSpell and receiver.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ):
			receiver.interruptSpell( csstatus.SKILL_IN_BLACKOUT )

		# ִ�и���Ч��
		receiver.move_speed = self.moveSpeed
		receiver.updateTopSpeed()
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_VERTIGO )

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
		centerPos = Math.Vector3( receiver.position )
		receiver.doRandomRun( centerPos, self.moveRadius )
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
		Buff_Normal.doReload( self, receiver, buffData )

		# ִ�и���Ч��
		receiver.move_speed = self.moveSpeed
		receiver.updateTopSpeed()
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
		if receiver.isMoving():		# ֹͣ�ƶ�
			receiver.stopMoving()

		# �Ƴ�����Ч��
		receiver.calcMoveSpeed()
		receiver.updateTopSpeed()
		receiver.actCounterDec( STATES )
		receiver.effectStateDec( csdefine.EFFECT_STATE_VERTIGO )

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{"id":self._id, "param":None}������ʾ�޶�̬���ݡ�
		
		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : { "moveRadius": self.moveRadius, "moveSpeed": self.moveSpeed } }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = Buff_108009()
		obj.__dict__.update( self.__dict__ )
		obj.moveRadius = data["param"]["moveRadius"]
		obj.moveSpeed = data["param"]["moveSpeed"]
		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj