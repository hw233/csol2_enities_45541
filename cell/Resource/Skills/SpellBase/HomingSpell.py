# -*- coding: gb18030 -*-

# �������ܻ�����
from bwdebug import *
from Spell import Spell
from Function import newUID
import csstatus
import csdefine
import time
import BigWorld
import Math
import random
import SkillTargetObjImpl
import math
import CooldownFlyweight
g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()


##���������ﵽһ��ֵ��������
BATI_COUNT        = 10000
BATI_SKILL        = 122689001

BATI_CANCEL_TIME  = 2.0

#���������жϴ���CD
INTERRUPT_CDS = { 1:1, 199:1 }

# Ϊƫ�ȣ��ɵ��ڲ�����ȡֵ��n�й�
N_OFFSET = { 10:4.8, 9:4.8, 8:4.75, 7:4.75, 6:4.66, 5:4.66, 4:4 }
	
# --------------------------------------------------------------------
# �������ܻ�����
#    ������������������л��м����ȥ�ͷ���һ�����ܣ� ��һ�����ܿ������κ�һ�����������ļ���
#	 ������Ҫ���Ӽ��ܵ���������ȴ����Ч
# --------------------------------------------------------------------
class HomingSpell( Spell ) :
	def __init__( self ) :
		Spell.__init__( self )
		self._childSpellIDs = []
		self._childSpellIDsCopy = []
		self._tickInterval = 0.0
		self._persistent = 0
		self._endTime = 0
		self._target = None
		self._actionMaxSpeed = 0.0
		self._extraSnake = 0

	def init( self, dictData ):
		"""
		��ȡ��������
		@param dictData:	��������
		@type dictData:	python dictData
		"""
		Spell.init( self, dictData )
		self._persistent = float( dictData["param1"] )

		self._childSpellIDs = [int( k ) for k in dictData["param2"].split(",")]
		self._childSpellIDs.reverse()
		self._childSpellIDsCopy = list( self._childSpellIDs )
		if dictData["param4"] != "":
			param4 = dictData["param4"].split(";")
			if len( param4 ) > 0 :
				self._actionMaxSpeed = float( param4[0] )
			if len( param4 ) > 1 :
				self._extraSnake = int( param4[1] )
		self.initHomingSpellSelf( dictData )

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
		#�����Ĭ��һ�༼�ܵ�ʩ���ж�
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO  > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP

		if self.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
				return csstatus.SKILL_CANT_CAST
		elif self.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ):
				return csstatus.SKILL_CANT_CAST
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		
		return Spell.useableCheck( self, caster, target )
	
	def initHomingSpellSelf( self, dictData ):
		"""
		��ʼ��������������
		"""
		self._tickInterval = float( dictData[ "param3" ] )

	# ----------------------------------------------------------------
	# virtual methods
	# ----------------------------------------------------------------
	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		�����ִ�Ŀ��ͨ�档��Ĭ������£��˴�ִ�п�������Ա�Ļ�ȡ��Ȼ�����receive()�������ж�ÿ���������߽��д���
		ע���˽ӿ�Ϊ�ɰ��е�receiveSpell()

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell.onArrive( self, caster, target )
		self._target = target
		if self._persistent > 0:
			self._endTime = time.time() + self._persistent

		data = self.addToDict()
		nSkill = self.createFromDict( data )
		caster.addHomingSpell( nSkill )

	def onTick( self, caster ):
		"""
		virtual method.
		�������ܵļ����Ӧtick
		@return type: ����false����ǰ�����������
		"""
		spell = Spell.skillLoader[ self.getChildSpellID() ]
		if spell is None: return csstatus.SKILL_NOT_EXIST

		#�����Ĭ��һ�༼�ܵ�ʩ���ж�
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO  > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_FIX > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_FIX

		if spell.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
				return csstatus.SKILL_CANT_CAST
		elif spell.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ):
				return csstatus.SKILL_CANT_CAST
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		
		# ʩ�����������
		state = spell.castValidityCheck( caster, self._target  )
		if state != csstatus.SKILL_GO_ON: return state

		# ���ʩ���ߵ������Ƿ��㹻
		state = spell.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON: return state

		# ���Ŀ���Ƿ���Ϸ���ʩչ
		state = spell._castObject.valid( caster, self._target )
		if state != csstatus.SKILL_GO_ON: return state
		
		#����ת��
		caster.rotateToSpellTarget( self._target )	
		spell.cast( caster, self._target )
		return csstatus.SKILL_GO_ON

	def isTimeout( self ):
		"""
		0�޳���ʱ�䣬��������
		"""
		if self._endTime == 0:
			return False
		return time.time() >= self._endTime

	def getPersistent( self ):
		"""
		����������ܵ����õ���ʱ��
		"""
		return self._persistent

	def getEndTime( self ):
		"""
		virtual method.
		����������ܵ����õĽ���ʱ��
		"""
		return self._endTime

	def getChildSpellIDs( self ):
		"""
		����������ܵ������Ӽ���ID
		"""
		return self._childSpellIDs

	def getChildSpellID( self ):
		"""
		��ȡһ���Ӽ���ID
		"""
		if len( self._childSpellIDsCopy ) == 0:
			self._childSpellIDsCopy = list( self._childSpellIDs )

		return self._childSpellIDsCopy.pop()

	def getTickInterval( self ):
		"""
		virtual method.
		����������ܵĴ������ʱ��
		"""
		return self._tickInterval

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{ "param": None }������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : { "endTime" : self._endTime, "target" : self._target, "childSpellIDs": list( self._childSpellIDs ) } }

	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = self.__class__()
		obj.__dict__.update( self.__dict__ )

		obj._endTime = data["param"][ "endTime" ]
		obj._target = data["param"][ "target" ]
		obj._childSpellIDsCopy = list( data["param"][ "childSpellIDs" ] )

		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj

	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		���ÿһ�������߽�����������������˺����ı����Եȵȡ�ͨ������´˽ӿ�����onArrive()���ã�
		�������п�����SpellUnit::receiveOnreal()�������ã����ڴ���һЩ��Ҫ�������ߵ�real entity�����������顣
		�������Ƿ���Ҫ��real entity���Ͻ��գ��ɼ����������receive()�������жϣ������ṩ��ػ��ơ�
		ע���˽ӿ�Ϊ�ɰ��е�onReceive()

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		pass

	def onInterrupted( self, caster, reason ):
		"""
		�������ܱ���ϻص�
		"""
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			notCDResons = [ csstatus.SKILL_INTERRUPTED_BY_SPELL_2, csstatus.SKILL_INTERRUPTED_BY_TIME_OVER, csstatus.SKILL_NO_MSG, csstatus.SKILL_CANT_CAST, csstatus.SKILL_NOT_READY ]
			if reason not in notCDResons: 
				#����ϴ���CD
				for cd, time in INTERRUPT_CDS.items():
					try:
						endTime = g_cooldowns[ cd ].calculateTime( time )
					except:
						EXCEHOOK_MSG("skillID:%d" % self.getID())
					if caster.getCooldown( cd ) < endTime:
						caster.changeCooldown( cd, time, time, endTime )
		caster.updateTopSpeed( )
		caster.removeTemp( "SNAKE_EXTRA" )
		caster.removeTemp( "HOMING_DIRECT" )
		
	def canInterruptSpell( self, reason ):
		"""
		�ɷ񱻸�ԭ����
		"""
		return reason != csstatus.SKILL_INTERRUPTED_BY_AI
	
	def calcHitProbability( self, source, target ):
		"""
		virtual method.
		����������
		������=(����������/�ܻ�������)^2+���������Ҵ�͸-�ܻ������ҿ���
		@param source:	������
		@type  source:	entity
		@param target:	��������
		@type  target:	entity
		return type:	Float
		"""
		hitRate = pow( source.daoheng / target.daoheng, 2 ) + source.chaos_penetrate - target.chaos_resist
		return hitRate
		
	def cast( self, caster, target ) :
		"""
		virtual method
		ϵͳʩ�ţ�û�������壬���Զ���˲��
		"""
		Spell.cast( self, caster, target )
		if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if self._actionMaxSpeed > 0.0: #Ϊ�˷�ֹ����ڲ��Ŷ���ʱ������
				caster.setTemp( "TOP_SPEED", caster.topSpeed )
				caster.setTopSpeed( self._actionMaxSpeed )
		if caster.effect_state & csdefine.EFFECT_STATE_PROWL:	 #Ǳ��װ�������˺�
			caster.setTemp("SNAKE_EXTRA", self._extraSnake )
		#��¼��ǰʩ���߳��� �ܻ�������Ҫ�õ�
		direction = caster.queryTemp( "HOMING_DIRECT", None )
		if not direction:
			yaw = caster.yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			caster.setTemp( "HOMING_DIRECT", direction )

# --------------------------------------------------------------------
# ��������������
#   ������������������л��м���ģ����ʱ�����ɲ߻�����ģ�ȥ�ͷ���һ�����ܣ�
#	��һ�����ܿ������κ�һ�����������ļ���
#	������Ҫ���Ӽ��ܵ���������ȴ����Ч
# --------------------------------------------------------------------
class ActiveHomingSpell( HomingSpell ):
	"""
	"""
	def __init__( self ):
		HomingSpell.__init__( self )
		self._tickInterval = []
		self._tickIntervalCopy = []
		self._receiverBuffs = []  #buff������
		self._comboData = []
		self._daoheng = True
		self._interruptRateList = []

	def initHomingSpellSelf( self, dictData ):
		"""
		��ʼ��
		"""
		self._tickInterval = [float( k ) for k in dictData["param3"].split(",")]
		if dictData["param5"] != "":
			self._comboData = dictData["param5"].split(";")
			self._daoheng = bool( int( self._comboData[0] ) )
			if self._comboData[1] != "":
				self._interruptRateList = [float( k ) for k in self._comboData[1].split(",")]
		self._tickInterval.reverse()
		self._tickIntervalCopy = list( self._tickInterval )

	def getTickInterval( self ):
		"""
		����������ܵĴ������ʱ��
		"""
		if len( self._tickIntervalCopy ) == 0 :
			self._tickIntervalCopy = list( self._tickInterval )

		return self._tickIntervalCopy.pop()

	def cast( self, caster, target ) :
		"""
		virtual method
		ϵͳʩ�ţ�û�������壬���Զ���˲��
		"""
		self._receiverBuffs = [] 
		HomingSpell.cast( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if receiver.isDestroyed:
			return
		self.receiveLinkBuff( caster, receiver )
		self._receiverBuffs.append( receiver.id )
	
	def onInterrupted( self, caster, reason ):
		"""
		�������ܱ���ϻص�
		"""
		HomingSpell.onInterrupted( self, caster, reason )
		if reason == csstatus.SKILL_INTERRUPTED_BY_TIME_OVER:
			self._receiverBuffs = []
			return 
		for entityID in self._receiverBuffs:
			entity = BigWorld.entities.get( entityID, None )
			if entity and not entity.isDestroyed:
				buffIndexList = []
				for buffData in self._buffLink:
					buffs = entity.findBuffsByBuffID( buffData.getBuff()._buffID )
					if len(buffs)>0:
						for buffIndex in buffs:			#�Ӻ���ǰɾ
							buff = entity.getBuff( buffIndex )
							if buff["caster"] == caster.id :
								buffIndexList.append( buff["index"] )
								#entity.removeBuffByID( buffData.getBuff()._id,  [csdefine.BUFF_INTERRUPT_NONE] )
								break
				for buffIndex in buffIndexList:
					entity.removeBuffByIndex( buffIndex, [ csdefine.BUFF_INTERRUPT_NONE ] )
		self._receiverBuffs = []
		
	def onTick( self, caster ):
		"""
		virtual method.
		�������ܵļ����Ӧtick
		@return type: ����false����ǰ�����������
		"""
		if self.onTickDo( caster ) == csstatus.SKILL_GO_ON:
			return csstatus.SKILL_GO_ON
		spell = Spell.skillLoader[ self.getChildSpellID() ]
		if spell is None: return csstatus.SKILL_NOT_EXIST

		#�����Ĭ��һ�༼�ܵ�ʩ���ж�
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO  > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_FIX > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_FIX

		if spell.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
				return csstatus.SKILL_CANT_CAST
		elif spell.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ):
				return csstatus.SKILL_CANT_CAST
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		
		# ʩ�����������
		state = spell.castValidityCheck( caster, self._target  )
		if state != csstatus.SKILL_GO_ON: return state

		# ���ʩ���ߵ������Ƿ��㹻
		state = spell.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON: return state

		# ���Ŀ���Ƿ���Ϸ���ʩչ
		state = spell._castObject.valid( caster, self._target )
		if state != csstatus.SKILL_GO_ON: return state
		
		#����ת��
		caster.rotateToSpellTarget( self._target )	
		spell.cast( caster, self._target )
		
		if self.onTickDo( caster ) == csstatus.SKILL_INTERRUPTED_BY_TIME_OVER:
			return csstatus.SKILL_INTERRUPTED_BY_TIME_OVER
		return csstatus.SKILL_GO_ON

	def onTickDo( self, caster ):
		if len( self._tickIntervalCopy ) == 0 and self._persistent <= 0:
			if self._persistent == -1.0:
				return csstatus.SKILL_INTERRUPTED_BY_TIME_OVER
			caster.planesAllClients( "castSpell", ( self.getID(), self._target ) )
			return csstatus.SKILL_GO_ON
		return None

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{ "param": None }������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : {	"endTime" : self._endTime,
								"tickInterval" : self._tickInterval,
								"target" : self._target,
								"childSpellIDs" : list( self._childSpellIDs ),
								"receiverBuffs" : list( self._receiverBuffs ), }}


	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = self.__class__()
		obj.__dict__.update( self.__dict__ )

		obj._endTime = data["param"][ "endTime" ]
		obj._tickIntervalCopy = list( data["param"][ "tickInterval" ] )
		obj._target = data["param"][ "target" ]
		obj._childSpellIDsCopy = list( data["param"][ "childSpellIDs" ] )
		obj._receiverBuffs = list( data["param"][ "receiverBuffs" ] )

		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj


# --------------------------------------------------------------------
# ��������������
#   ��������������ͷŹ�����ά����һ����Ŀ���BUFF��������������ܻ���
#	�ͷŵ�ʱ��BUFF��һֱ���ڣ����������ܽ�������BUFFҲ������ ��ǰֻ�Ե������ö�����Ч
# --------------------------------------------------------------------
class HomingSpellBuff( ActiveHomingSpell ):
	"""
	"""

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		ActiveHomingSpell.receive( self, caster, receiver )
		caster.setTemp( "HomingSpellReceiverID", receiver.id )
		self.receiveLinkBuff( caster, receiver )


	def onInterrupted( self, caster, reason ):
		"""
		�������ܱ���ϻص�
		"""
		ActiveHomingSpell.onInterrupted( self, caster, reason )
		if self._target.getType() == csdefine.SKILL_TARGET_OBJECT_ENTITY:
			entity = self._target.getObject()
			if entity is not None:
				buffIndexList = []
				for buffData in self._buffLink:
					buffs = entity.findBuffsByBuffID( buffData.getBuff()._buffID )
					if len(buffs)>0:
						for buffIndex in buffs:			#�Ӻ���ǰɾ
							buff = entity.getBuff( buffIndex )
							if buff["caster"] == caster.id :
								buffIndexList.append( buff["index"] )
								#entity.removeBuffByID( buffData.getBuff()._id,  [csdefine.BUFF_INTERRUPT_NONE] )
								break
				for buffIndex in buffIndexList:
					entity.removeBuffByIndex( buffIndex,  [csdefine.BUFF_INTERRUPT_NONE] )


	def onTick( self, caster ):
		"""
		virtual method.
		�������ܵļ����Ӧtick
		@return type: ����false����ǰ�����������
		"""
		if BigWorld.entities.get( caster.queryTemp( "HomingSpellReceiverID", 0 ) ) is None:
			return csstatus.SKILL_TARGET_NOT_EXIST
		return ActiveHomingSpell.onTick( self, caster )

	def onTickDo( self, caster ):
		if len( self._tickIntervalCopy ) == 0 and self._persistent <= 0:
			if self._persistent == -1.0:
				return csstatus.SKILL_INTERRUPTED_BY_TIME_OVER
			caster.planesAllClients( "castSpell", ( self.getID(), self._target ) )
			return csstatus.SKILL_GO_ON
		return None


# --------------------------------------------------------------------
# ��������������
#   ����ཫ����ĸ���ܵ���ЧĿ������Ӽ���
# --------------------------------------------------------------------
class FixTargetActiveHomingSpell( ActiveHomingSpell ):
	"""
	"""
	def __init__( self ):
		ActiveHomingSpell.__init__( self )
		self._receivers = []
		self._comboInter = [] #�����ֿ����� Ŀ��
		
	def cast( self, caster, target ) :
		"""
		virtual method
		ϵͳʩ�ţ�û�������壬���Զ���˲��
		"""
		HomingSpell.cast( self, caster, target )

	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		�����ִ�Ŀ��ͨ�档��Ĭ������£��˴�ִ�п�������Ա�Ļ�ȡ��Ȼ�����receive()�������ж�ÿ���������߽��д���
		ע���˽ӿ�Ϊ�ɰ��е�receiveSpell()

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		# ��ȡ����������
		Spell.onArrive( self, caster, target )
		self._receivers = self.getReceivers( caster, target )
		
		self._target = target
		if self._persistent > 0:
			self._endTime = time.time() + self._persistent

		data = self.addToDict()
		nSkill = self.createFromDict( data )
		caster.addHomingSpell( nSkill )
		

	def onTick( self, caster ):
		"""
		virtual method.
		�������ܵļ����Ӧtick
		@return type: ����false����ǰ�����������
		"""
		if self.onTickDo( caster ) == csstatus.SKILL_GO_ON:
			return csstatus.SKILL_GO_ON

		spell = Spell.skillLoader[ self.getChildSpellID() ]
		if spell is None: return csstatus.SKILL_NOT_EXIST


		#�����Ĭ��һ�༼�ܵ�ʩ���ж�
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO  > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_FIX > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_FIX

		if spell.getType() == csdefine.BASE_SKILL_TYPE_MAGIC:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
				return csstatus.SKILL_CANT_CAST
		elif spell.getType() == csdefine.BASE_SKILL_TYPE_PHYSICS:
			if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
				return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ):
				return csstatus.SKILL_CANT_CAST
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		
		# ʩ�����������
		state = spell.castValidityCheck( caster, self._target  )
		if state != csstatus.SKILL_GO_ON: return state

		# ���ʩ���ߵ������Ƿ��㹻
		state = spell.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON: return state

		# ���Ŀ���Ƿ�������
		if hasattr( spell, "valid" ):
			state = spell.valid( self._target )
		if state == csstatus.SKILL_CHANGE_TARGET:
			self._target = self.__chooseTarget( spell, caster )

		# ���Ŀ���Ƿ���Ϸ���ʩչ
		state = spell._castObject.valid( caster, self._target )
		if state != csstatus.SKILL_GO_ON: return state
		
		#FixTarget����������ÿ���Ӽ����ͷųɹ���ʱ����Ҫ���¼��receivers��������飩
		for enti in self._receivers[:]:
			if enti.isDestroyed:
				self._receivers.remove( enti )
		#����ֿ��ж�
		skillL = self.getChildSpellIDs()
		n = len( skillL ) 
		k = n - len( self._childSpellIDsCopy )
		if k == 1:
			self._comboInter=[]
			for receiver in self._receivers:
				en = receiver
				if en.isDestroyed: continue
				if self._daoheng:
					da = float(caster.daoheng)
					dd = float(en.daoheng)
					if n in N_OFFSET.keys():
						offset = 1 - N_OFFSET[n]/5.0
					else:
						offset = 1 - 4/5.0
					
					if  da + dd != 0:
						p = ( da / ( da + dd ) ) ** offset
					else:
						p = 0
					nJ = reduce(lambda x,y: x*y, range(1,n+1))
					glL = []
					for i in range( 0, n+1 ):
						if i > 0:
							iJ = reduce(lambda x,y: x*y, range(1,i+1))
						else:
							iJ = 1
						if n-i > 0:
							niJ = reduce(lambda x,y: x*y, range(1,n-i+1))
						else:
							niJ = 1
						pnk = (nJ/(iJ*niJ))*(p**i)*((1-p)**(n-i))
						glL.append( pnk )
					#�㵽��һ���Ӽ����ж�
					interR = random.random()
					ls = 0
					for idx in range(len(glL)):
						v2 = ls 
						ls += glL[idx]
						if v2 <= interR < ls:
							self._comboInter.append(( idx + 1 + 1, en ))
							break
				else:
					#��ͨ�����м����ĸ��Ӽ����жϣ�ͨ������������ʵ���Ӽ����ж�
					self.__unDaohengRate( en )
		self._comboInter.sort() #����
		for co in self._comboInter:
			if k == co[0]:
				en = co[1]
				if en and not en.isDestroyed:
					if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
						caster.homingSpellResist( en.id )
					if en.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
						en.homingSpellResist( en.id )
				if en in self._receivers:
					self._receivers.remove( en )
				#�Ƴ����ϵĿ���buff
				for entityID in self._receiverBuffs:
					entity = BigWorld.entities.get( entityID, None )
					if entityID != en.id: break
					if entity and not entity.isDestroyed:
						buffIndexList = []
						for buffData in self._buffLink:
							buffs = entity.findBuffsByBuffID( buffData.getBuff()._buffID )
							if len(buffs)>0:
								for buffIndex in buffs:			#�Ӻ���ǰɾ
									buff = entity.getBuff( buffIndex )
									if buff["caster"] == caster.id :
										buffIndexList.append( buff["index"] )
										#entity.removeBuffByID( buffData.getBuff()._id,  [csdefine.BUFF_INTERRUPT_NONE] )
										break
						for buffIndex in buffIndexList:
							entity.removeBuffByIndex( buffIndex,  [csdefine.BUFF_INTERRUPT_NONE] )
				if en.id == self._target.getObject().id:
					if len(self._receivers)>0:
						self._target = self.__chooseTarget( spell, caster )
					else:
						return csstatus.SKILL_MISS_TARGET
				self._comboInter.remove(co)
				break
		
		#�ж��Ƿ�ʹ������������
		if k != 1:
			avoidanceEntities = []
			for e in self._receivers:
				try :
					flag = e.popTemp( "AVOIDANCE_FLAG",False )
				except:
					flag = False
				if flag:
					avoidanceEntities.append(e)
			for e in avoidanceEntities:
				self._receivers.remove( e )
			if self._target.getObject() in avoidanceEntities :
				if len(self._receivers)>0:
					self._target = self.__chooseTarget( spell, caster )
				else:
					return csstatus.SKILL_MISS_TARGET

			loseEnemys = []
			for re in self._receivers:
				if re.isDestroyed: continue
				if not re.hasEnemy( caster.id ):	# ���ڵ����б�����������б��Ƴ�
					loseEnemys.append( re )
			for en in loseEnemys:
				self._receivers.remove( en )
			if self._target.getObject() in loseEnemys:
				if len( self._receivers ) > 0:
					self._target = self.__chooseTarget( spell, caster )
				else:
					return csstatus.SKILL_MISS_TARGET

		if hasattr( spell, "onUse" ):
			spell.onUse( caster, self._target, self._receivers )
		
		for receiver in self._receivers:
			en = receiver
			if en.isDestroyed:continue
			if caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				#����Ƿ񴥷�����
				bati = en.queryTemp( "HOMINGSPELL_BATI", None )
				if bati:
					if bati[1] < BATI_COUNT:
						if ( time.time() - bati[0] ) < BATI_CANCEL_TIME :
							newBati = ( time.time(), bati[1] + 1 )
						else:
							newBati = ( time.time(), 1 )
					else:
						en.spellTarget( BATI_SKILL, en.id )
						newBati = ( time.time(), 0 )
				else:
					newBati = ( time.time(), 1 )
				en.setTemp( "HOMINGSPELL_BATI", newBati )
		
		state = self.onTickDo( caster )
		if state == csstatus.SKILL_INTERRUPTED_BY_TIME_OVER:
			return state
		#����ת��
		caster.rotateToSpellTarget( self._target )
		return csstatus.SKILL_GO_ON

	def __unDaohengRate( self, en ):
		"""
		��ͨ�����м����ĸ��Ӽ����ж�
		"""
		if self._interruptRateList == []: return
		rateList = self._interruptRateList
		if len( rateList ) != len( self.getChildSpellIDs() ):
			self._comboInter = []
			ERROR_MSG( "%s's childSpell interrupt rate config is wrong!" % self.getID() )
			return
		for index in range( len( rateList ) ):
			inter = random.random()
			if inter <= rateList[index]:
				self._comboInter.append( (index + 1,en) )
				break

	def __chooseTarget( self, spell, caster ):
		"""
		ѡ���µ�Ŀ��
		"""
		for receiver in self._receivers:
			target = SkillTargetObjImpl.createTargetObjEntity( receiver )
			state = spell._castObject.valid( caster, target )
			if state == csstatus.SKILL_GO_ON:
				return target
		return self._target

	def onTickDo( self, caster ):
		if len( self._tickIntervalCopy ) == 0 and self._persistent <= 0:
			if self._persistent == -1.0:
				return csstatus.SKILL_INTERRUPTED_BY_TIME_OVER
			caster.planesAllClients( "castSpell", ( self.getID(), self._target ) )
			return csstatus.SKILL_GO_ON
		return None

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{ "param": None }������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : {	"endTime" : self._endTime,
								"tickInterval" : self._tickInterval,
								"target" : self._target,
								"receiver" : self._receivers,
								"childSpellIDs" : list( self._childSpellIDs ), }}


	def createFromDict( self, data ):
		"""
		virtual method.
		���ݸ������ֵ����ݴ���һ����������ͬid�ŵļ��ܡ���ϸ�ֵ����ݸ�ʽ�����SkillTypeImpl��
		�˺���Ĭ�Ϸ���ʵ������������һЩ����Ҫ���涯̬���ݵļ����о����Ը��ߵ�Ч�ʽ������ݻ�ԭ��
		�����Щ������Ҫ���涯̬���ݣ���ֻҪ���ش˽ӿڼ��ɡ�

		@type data: dict
		"""
		obj = self.__class__()
		obj.__dict__.update( self.__dict__ )

		obj._endTime = data["param"][ "endTime" ]
		obj._tickIntervalCopy = list( data["param"][ "tickInterval" ] )
		obj._target = data["param"][ "target" ]
		obj._receivers = data["param"][ "receiver" ]
		obj._childSpellIDsCopy = list( data["param"][ "childSpellIDs" ] )

		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
	

class FTAHomingSpell_SelfBuff( FixTargetActiveHomingSpell ):
	"""
	buff2���Լ��ӵ�����ĸ���ܽű�
	"""
	def __init__( self ):
		FixTargetActiveHomingSpell.__init__( self )
		
	def cast( self, caster, target ) :
		"""
		virtual method
		ϵͳʩ�ţ�û�������壬���Զ���˲��
		"""
		for buffData in self._buffLink:
			buff = buffData.getBuff()
			buffID = buff.getBuffID()
			if buffID != 108007:
				buff.receive( caster, caster )
		FixTargetActiveHomingSpell.cast( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if receiver.isDestroyed:
			return
		for buffData in self._buffLink:
			buff = buffData.getBuff()
			buffID = buff.getBuffID()
			if buffID == 108007:
				buff.receive( caster, receiver )
		self._receiverBuffs.append( receiver.id )
		caster.setTemp( "HomingSpellReceiverID", receiver.id )
		
class FTAHomingSpell_TeamBuff( FixTargetActiveHomingSpell ):
	"""
	buff2���Լ��Ͷ��Ѽӵ�����ĸ���ܽű�
	"""
	def __init__( self ):
		FixTargetActiveHomingSpell.__init__( self )
		
	def cast( self, caster, target ) :
		"""
		virtual method
		ϵͳʩ�ţ�û�������壬���Զ���˲��
		"""
		for buffData in self._buffLink:
			buff = buffData.getBuff()
			buffID = buff.getBuffID()
			if buffID != 108007:
				elist = caster.getAllMemberInRange( 15.0 )
				if len( elist ) <= 0:
					elist = [ caster ]
				for e in elist:
					buff.receive( caster, e )
		FixTargetActiveHomingSpell.cast( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if receiver.isDestroyed:
			return
		for buffData in self._buffLink:
			buff = buffData.getBuff()
			buffID = buff.getBuffID()
			if buffID == 108007:
				buff.receive( caster, receiver )
		self._receiverBuffs.append( receiver.id )
		caster.setTemp( "HomingSpellReceiverID", receiver.id )