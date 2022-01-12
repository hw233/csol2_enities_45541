# -*- coding: gb18030 -*-
#
# $Id: Buff.py,v 1.26 2008-08-13 07:20:45 kebiao Exp $

"""
���������ࡣ
"""

from bwdebug import *
from Skill import Skill
from EffectState import EffectState
import BigWorld
import RequireDefine
import csconst
import csstatus
import csdefine
import time
import random

RESIST_VALUE_MIN = 0.05
RESIST_VALUE_MAX = 0.95

def checkResistNone( caster, receiver ):
	return False

def getDaoHengEffect( caster, receiver ):
	daohengEffect = pow( caster.getDaoheng() / receiver.getDaoheng(), 2 )
	if daohengEffect > 1.0:
		daohengEffect = 1.0
		
	return daohengEffect

def checkResistYuanLi( caster, receiver ):
	# ���Ԫ���ĵֿ��� ѣ�Ρ���˯������ ��
	if receiver.resist_yuanli == -1:
		return True
		
	buff_hit = getDaoHengEffect( caster, receiver ) - receiver.resist_yuanli
	if buff_hit < RESIST_VALUE_MIN:
		buff_hit = RESIST_VALUE_MIN
		
	if buff_hit > RESIST_VALUE_MAX:
		buff_hit = RESIST_VALUE_MAX
		
	return random.random() > buff_hit

def checkResistLingLi( caster, receiver ):
	# ��������ĵֿ��� �������١���Ĭ ��
	if receiver.resist_lingli == -1:
		return True
		
	buff_hit = getDaoHengEffect( caster, receiver ) - receiver.resist_lingli
	if buff_hit < RESIST_VALUE_MIN:
		buff_hit = RESIST_VALUE_MIN
		
	if buff_hit > RESIST_VALUE_MAX:
		buff_hit = RESIST_VALUE_MAX
		
	return random.random() > buff_hit

def checkResistTipoLi( caster, receiver ):
	# ������ǵĵֿ��� ���� ��
	if receiver.resist_tipo == -1:
		return True
		
	buff_hit = getDaoHengEffect( caster, receiver ) - receiver.resist_tipo
	if buff_hit < RESIST_VALUE_MIN:
		buff_hit = RESIST_VALUE_MIN
		
	if buff_hit > RESIST_VALUE_MAX:
		buff_hit = RESIST_VALUE_MAX
		
	return random.random() > buff_hit
	
CHECK_DICT = {
	csdefine.RESIST_NONE	 : checkResistNone,
	csdefine.RESIST_YUANLI	 : checkResistYuanLi,
	csdefine.RESIST_LINGLI	 : checkResistLingLi,
	csdefine.RESIST_TIPO	 : checkResistTipoLi,
}
class Buff( Skill, EffectState ):
	"""
		���ܵĳ�����Ч��
		����"Buff"�����"Buff_"��ͷ
		ע������Ϊ�ɰ��е�Condition��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Skill.__init__( self )
		EffectState.__init__( self )
		self._buffID = 0 									# BUFFID (����BUFFIDʹ���˼���*N��ɵ�ID ������IDΪ������BUFFID)
		self._sourceSkillID = 0								# Դ���ܵ�ID (��Դ���ܳ�ʼ��)
		self._sourceSkillIdx = 0							# ��BUFF��Դ�������ϵ�λ��(��Դ���ܳ�ʼ��)
		self._level = 0										# BUFF�ȼ�
		self._save = False									# �Ƿ񱣴�
		self._isNotIcon = False								# �Ƿ���ʾbuffͼ��
		self._persistent = 0								# ����ʱ��(��λ����)�����ֵ <= 0 ���ʾһֱ��������������ʽ�ж�
		self._loopSpeed = 0									# ÿ�δ������(��λ����/��)�����Ϊ0�򲻴���ֱ��������
		self._isAppendPrevious = False						# �Ƿ������ͬ���͵�BUFF����׷�Ӳ���
		self._loopRequire = None							# buffѭ��ʱ������
		self._buffType = 0									# buff��� (��������	�������Ա�������	����������������	�ǹ����Ա�������	����)
		self._sourceType = 0								# buffС�� ����Դ���ͣ�
		self._interruptCode = []							# ��BUFF������Щ��־���ж�ֹͣ
		self._triggerInterruptCode = []						# ��BUFF������Щ��־���ж�ĳЩBUFF
		self._baseType = csdefine.BASE_SKILL_TYPE_BUFF		# buff���
		self._stackable = 1									# ��������
		self._isEffectDaoheng = 0							# �Ƿ��ܵ��е�Ӱ��
		self._casterID = 0

	def init( self, dictDat ):
		"""
		��ȡ��������
		@param dictDat: ��������
		@type  dictDat: python dict
		"""
		Skill.init( self, dictDat )
		EffectState.init( self, dictDat )
		self._buffID = self._id
		if dictDat.has_key( "isNotIcon" ) and dictDat["isNotIcon"] != 0:
			self._isNotIcon = True	# ΪTrue��ʾ����ʾBUFFͼ��
		self._persistent = dictDat[ "Persistent" ]
		self._level = dictDat[ "Level" ]
		self._loopSpeed = dictDat[ "LoopSpeed" ]
		self._stackable = dictDat[ "Stackable" ]
		if dictDat.has_key( "Type" ):
			self._buffType = dictDat["Type"]

		self._interruptCode = dictDat[ "InterruptCode" ]
		self._triggerInterruptCode = dictDat[ "triggerInterruptCode" ]
		if dictDat.has_key( "isAppend" ):
			self._isAppendPrevious = bool( dictDat[ "isAppend" ] )
		if dictDat.has_key( "LoopRequire" ):
			self._loopRequire = RequireDefine.newInstance( dictDat["LoopRequire"] )		# ʩ�ŷ������ĵĶ���
			self._loopRequire.load( dictDat["LoopRequire"]["value"] )
		self._sourceType = dictDat[ "SourceType" ]
		
		self._resistEffect = csdefine.RESIST_NONE
		if dictDat.has_key( "ResistEffect" ):
			resistEffect = dictDat[ "ResistEffect" ]
			if isinstance( resistEffect, str ) and hasattr( csdefine, resistEffect ):
				self._resistEffect = getattr( csdefine, resistEffect )
				
		self.param3 = dictDat["Param3"]

	def getLevel( self ):
		"""
		"""
		return self._level

	def getSourceType( self ):
		"""
		��ȡbuffС�� ����Դ���ͣ�
		"""
		return self._sourceType

	def getBuffID( self ):
		"""
		ȡ��BUFF�����ı��
		"""
		return self._buffID

	def getSourceSkillID( self ):
		"""
		��ȡbuff��Դ����ID
		"""
		return self._sourceSkillID

	def getSourceSkillIndex( self ):
		"""
		��ȡbuff��Դ�������ϵ�����λ��
		"""
		return self._sourceSkillIdx

	def setSource( self, sourceSkillID, sourceIndex ):
		"""
		����Դ������Ϣ
		"""
		self._id = ( sourceSkillID * 100 ) + sourceIndex + 1 #sourceIndex + 1 ����ΪBUFF����IDʵ���Ǽ���ID+BUFF���ڵ����� �������1 ��ôskillID+0=skillID
		self._sourceSkillID = sourceSkillID
		self._sourceSkillIdx = sourceIndex

	def doTick( self, tick ):
		"""
		����һ��tick����飬����0��ʾ����doLoop������Ϊtick������

		@param tick: ��ǰtickֵ
		@type  tick: integer
		@return: ��tickֵ
		@rtype:  integer
		"""
		if self._loopSpeed <= 0: return 1		# ��������
		return (tick + 1) % self._loopSpeed

	def isTimeout( self, timeVal ):
		"""
		virtual method.
		����Ƿ��ѳ�ʱ

		@return: BOOL�����condition�ĳ���ʱ�仹û���򷵻�False�����򷵻�True
		@rtype:  BOOL
		"""
		if timeVal == 0: return False		# �޳���ʱ�䣬��������
		return time.time() >= timeVal

	def isSave( self ):
		"""
		"""
		return self._save

	def isNotIcon( self ):
		"""
		�Ƿ���ʾBUFFͼ��
		"""
		return self._isNotIcon

	def checkResist( self, caster, receiver ):
		"""
		���BUFFЧ���Ƿ񱻵ֿ�, True�����ֿ���False��û�ֿ�
		"""
		if receiver.resist_in_affected:
			return False
		
		if CHECK_DICT.has_key( self._resistEffect ):
			return CHECK_DICT[ self._resistEffect ]( caster, receiver )
		
		return False

	def calculateTime( self, caster ):
		"""
		virtual method.
		ȡ�ó���ʱ��
		"""
		if self._persistent <= 0: return 0
		return time.time() + self._persistent

	def cancelBuff( self, reasons ):
		"""
		virtual method.
		ȡ��һ��BUFF
		@param reasons: ȡ����ԭ��
		@rtype  : bool
		"""
		for reason in reasons:
			if reason in self._interruptCode: # �����BUFF�ܹ���������ȡ��
				return True
		return False

	def onAddState( self, receiver, buffData, state ):
		"""
		��BUFF��attrBuffs�е�״̬���л���
		@param buffData: BUFF
		@param state	:���ĵ�״̬
		@type state	:	integer
		"""
		if buffData[ "state" ] & ( csdefine.BUFF_STATE_DISABLED | csdefine.BUFF_STATE_HAND ) == 0 and \
			state & csdefine.BUFF_STATE_DISABLED | csdefine.BUFF_STATE_HAND != 0:
			DEBUG_MSG( "buff %i is disable! changed state to: %i" % ( self.getID(), state ) )
			self.doEnd( receiver, buffData )

	def onRemoveState( self, receiver, buffData, state ):
		"""
		��BUFF��attrBuffs�е�״̬���л���
		@param buffData: BUFF
		@param state	:���ĵ�״̬
		@type state	:	integer
		"""
		if buffData[ "state" ] & ( csdefine.BUFF_STATE_DISABLED | csdefine.BUFF_STATE_HAND ) != 0 and \
			state & ( csdefine.BUFF_STATE_DISABLED | csdefine.BUFF_STATE_HAND ) != 0:
			DEBUG_MSG( "buff %i is enable! changed state to: %i" % ( self.getID(), state ) )
			self.doBegin( receiver, buffData )

	def receive( self, caster, receiver ):
		"""
		���ڸ�Ŀ��ʩ��һ��buff�����е�buff�Ľ��ն�����ͨ���˽ӿڣ�
		�˽ӿڱ����жϽ������Ƿ�ΪrealEntity��
		����������Ҫͨ��receiver.receiveOnReal()�ӿڴ���

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ��ߣ�None��ʾ������
		@type  receiver: Entity
		"""
		if caster is not None:
			casterID = caster.id
		else:
			casterID = 0
		self._casterID = casterID
		
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		if receiver.getState() == csdefine.ENTITY_STATE_DEAD:
			return

		receiver.addBuff( self.getNewBuffData( caster, receiver ) )
	
	def getNewBuffData( self, caster, receiver ):
		newBuffData = {}
		newBuffData[ "skill" ] = self.getNewObj()
		newBuffData[ "persistent" ] = self.calculateTime( caster )
		newBuffData[ "currTick" ] = 0
		
		casterID = 0
		if caster is not None:
			casterID = caster.id
		newBuffData[ "caster" ] = casterID
		
		newBuffData[ "state" ] = 0
		newBuffData[ "index" ] = 0
		newBuffData[ "sourceType" ] = self.getSourceType()
		newBuffData[ "isNotIcon" ] = self.isNotIcon()
		return newBuffData

	def doAppend( self, receiver, buffIndex ):
		"""
		Virtual method.
		��һ�������Ѿ����ڵ�ͬ����BUFF����׷�Ӳ���
		����ʹ������ӿڽ���׷�ӵĲ�������̳�����ӿڵ�ʵ�֣�Ŀǰ��֧������
		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffIndex: �������ͬ���͵�BUFF����attrbuffs��λ��,BUFFDAT ����ͨ�� receiver.getBuff( buffIndex ) ��ȡ
		"""
		buffdata = receiver.getBuff( buffIndex )
		buffdata["persistent"] += self._persistent
		receiver.client.onUpdateBuffData( buffIndex, buffdata )

	def triggerInterruptCode( self, receiver, buffData ):
		"""
		@triggerInterruptCode: buff�����ж���
		@receiver: ��buff�Ľ�����
		@buffData: ��buff�Ĺ����ֵ����ݽṹ
		"""
		
		rmb = []
		for idx, buff in enumerate( receiver.attrBuffs ):
			if buff["index"] != buffData[ "index" ] and buff["skill"].cancelBuff( self._triggerInterruptCode ):
				rmb.append( idx )

		rmb.reverse()	# �Ӻ�����ǰɾ��
		for r in rmb:
			receiver.removeBuff( r, self._triggerInterruptCode )

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
		DEBUG_MSG( "%i: buff % i [%i] idx:%i begin." % ( receiver.id, self.getID(), self._buffID, buffData[ "index" ] ) )
		id = buffData["caster"]
		if BigWorld.entities.has_key( id ):
			self.receiveEnemy( BigWorld.entities[ id ] , receiver )
		self.triggerInterruptCode( receiver, buffData )

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
		DEBUG_MSG( "%i: buff % i [%i] idx:%i loop." % ( receiver.id, self.getID(), self._buffID, buffData[ "index" ] ) )

		if self._loopRequire:
			if self._loopRequire.validObject( receiver , self ) == csstatus.SKILL_GO_ON:
				self._loopRequire.pay( receiver , self )
			else:
				return False	# ���Ĳ�����ʧ��
		return True

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
		DEBUG_MSG( "%i: buff % i [%i] idx:%i reload." % ( receiver.id, self.getID(), self._buffID, buffData[ "index" ] ) )
		self.triggerInterruptCode( receiver, buffData )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		DEBUG_MSG( "%i: buff % i [%i] idx:%i end." % ( receiver.id, self.getID(), self._buffID, buffData[ "index" ] ) )

	def getType( self ):
		"""
		���ؼ������
		"""
		return csdefine.BASE_SKILL_TYPE_BUFF

	def getBuffType( self ):
		"""
		����BUFF���
		"""
		return self._buffType

	def isBuffType( self, buffType ):
		"""
		virtual method.
		�ж��Լ��Ƿ�Ϊĳһ����
		"""
		return self._buffType == type

	def use( self, caster, target ):
		"""
		virtual method.
		����� target/position ʩչһ���������κη�����ʩ������ɴ˽���
		dstEntity��position�ǿ�ѡ�ģ����õĲ�����None���棬���忴���������Ƕ�Ŀ�껹��λ�ã�һ��˷���������client����ͳһ�ӿں���ת������
		Ĭ��ɶ��������ֱ�ӷ��ء�
		ע���˽ӿڼ�ԭ���ɰ��е�cast()�ӿ�
		@param   caster: ʩ����
		@type    caster: Entity

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		ERROR_MSG( "I do not support this the function!" )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		ERROR_MSG( "I do not support this the function!" )
		return csstatus.SKILL_UNKNOW
#
