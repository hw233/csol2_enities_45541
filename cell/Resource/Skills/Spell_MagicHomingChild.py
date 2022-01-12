# -*- coding:gb18030 -*-

from Spell_MagicImprove import Spell_MagicImprove
import csconst
import random
import csstatus
import Math
import math
import csarithmetic
import csdefine
import ECBExtend
from Function import newUID
from bwdebug import *
BE_HOMING_MAX_SPEED = 50.0

class Spell_MagicHomingChild( Spell_MagicImprove ):
	"""
	���������Ӽ���
	"""
	def __init__( self ):
		"""
		"""
		Spell_MagicImprove.__init__( self )

		# ʩ����λ������
		self.casterMoveSpeed = 0.0
		self.casterMoveDistance = 0.0
		self.casterMoveFace = False

		# ������λ������
		self.targetMoveSpeed = 0.0
		self.targetMoveDistance = 0.0
		self.targetMoveFace = False
		
		#�����˺�����
		self.extraTBuff = None #Ŀ��������buff���������˺�
		self.extraSBuff = None #����������buff���������˺�
		self.extraSHP   = None #����Ѫ�����ڰٷֱȲ��������˺�
		self.critSBuff  = [] #����������buff���������˺�

	def init( self, data ):
		"""
		"""
		Spell_MagicImprove.init( self, data )
		param2 = data["param2"].split(";")
		if len( param2 ) >= 3:
			self.casterMoveSpeed = float( param2[0] )
			self.casterMoveDistance = float( param2[1] )
			self.casterMoveFace = bool( int( param2[2] ) )
		param3 = data["param3"].split(";")
		if len( param3 ) >= 3:
			self.targetMoveSpeed = float( param3[0] )
			self.targetMoveDistance = float( param3[1] )
			self.targetMoveFace = bool( int( param3[2] ) )
		if data["param5"] != "":
			params = data["param5"].split("|")
			for param5 in params:
				infos = param5.split(";")
				extra_type = int(infos[0])
				if extra_type == 1:
					self.extraTBuff = ( [ int( i ) for i in infos[1].split(",") ], int( infos[2] ) )
				elif extra_type == 2:
					self.extraSBuff = ( [ int( i ) for i in infos[1].split(",") ], int( infos[2] ) )
				elif extra_type == 3:
					self.extraSHP = ( float( infos[1] ), int( infos[2] ) )
				elif extra_type == 4:	
					self.critSBuff =  [ int( i ) for i in infos[1].split(",") ]
	
	def cast( self, caster, target ) :
		"""
		virtual method
		ϵͳʩ�ţ�û�������壬���Զ���˲��
		"""
		# ʩ����λ��
		if self.casterMoveDistance and self.casterMoveSpeed:
			targetObject = target.getObject()
			direction = Math.Vector3( targetObject.position ) - Math.Vector3( caster.position )
			direction.normalise()
			dstPos = caster.position + direction * self.casterMoveDistance
			endDstPos = csarithmetic.getCollidePoint( caster.spaceID, caster.position, dstPos )
			if caster.__class__.__name__ != "Role":
				caster.moveToPosFC( endDstPos, self.casterMoveSpeed, self.casterMoveFace )
			else:
				caster.move_speed = self.casterMoveSpeed
				caster.updateTopSpeed()
				timeData = ( endDstPos - caster.position ).length/self.casterMoveSpeed
				caster.addTimer( timeData, 0, ECBExtend.CHARGE_SPELL_CBID )

		Spell_MagicImprove.cast( self, caster, target )

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
		if caster.isReal():
			Spell_MagicImprove.receive( self, caster, receiver )

		if receiver.isDestroyed:
			return
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# ������λ��
		#�����ǰĿ�괦�ڰ���״̬�����������λ��
		if receiver.effect_state & ( csdefine.EFFECT_STATE_HEGEMONY_BODY | csdefine.EFFECT_STATE_INVINCIBILITY | csdefine.EFFECT_STATE_FIX  ) > 0:
			return

		#�����������������Ǹ��ˣ���ô�����ƶ������ƶ�
		targetID = receiver.queryTemp( "HOMING_TARGET", 0 )
		if targetID != 0 and targetID != caster.id:
			return

		if self.targetMoveDistance and self.targetMoveSpeed:
			direction = caster.queryTemp( "HOMING_DIRECT", None )
			if not direction:
				yaw = caster.yaw
				direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			sourcePos = caster.position
			dstPos = receiver.position + direction * self.targetMoveDistance
			endDstPos = csarithmetic.getCollidePoint( receiver.spaceID, sourcePos, dstPos )
			endDstPos = csarithmetic.getCollidePoint( receiver.spaceID, Math.Vector3( endDstPos[0],endDstPos[1]+5.0,endDstPos[2]), Math.Vector3( endDstPos[0],endDstPos[1]-5.0,endDstPos[2]) )
			if receiver.__class__.__name__ != "Role" :
				receiver.moveToPosFC( endDstPos, self.targetMoveSpeed, self.targetMoveFace )
			else:
				perID = receiver.queryTemp( "HOMING_TIMMER", 0 )
				if perID:
					receiver.cancel( perID )

	def calcHitProbability( self, source, target ):
		"""
		���������ʣ��߻�Ҫ�������Ӽ���������100%
		"""
		return 1.0
	
	def isDoubleHit( self, caster, receiver ):
		"""
		virtual method.
		�жϹ������Ƿ񱬻�
		return type:bool
		"""
		if self.critSBuff :
			for index, buff in enumerate( caster.attrBuffs ):
				spell = buff["skill"]
				if spell.getBuffID() in self.critSBuff:
					return  True
		return random.random() < ( caster.magic_double_hit_probability + ( receiver.be_magic_double_hit_probability - receiver.be_magic_double_hit_probability_reduce ) / csconst.FLOAT_ZIP_PERCENT )	
	
	def calcSkillHitStrength( self, source, receiver, dynPercent, dynValue ):
		"""
		virtual method.
		���㼼�ܹ�����
		��ʽ1�����ܹ��������ܹ�ʽ�еĻ���ֵ��=���ܱ���Ĺ�����+��ɫ����������
		�����ܹ�ʽ�о��ǣ������ܱ���Ĺ�����+��ɫ����������*��1+���������ӳɣ�+����������ֵ
		@param source:	������
		@type  source:	entity
		@param dynPercent:	�ڱ��ι��������п��ܻ����ⲿ�������ܵ��¶���� ���ܹ������ӳ�
		@param  dynValue:	�ڱ��ι��������п��ܻ����ⲿ�������ܵ��¶���� ���ܹ�������ֵ
		"""
		base = random.randint( self._effect_min, self._effect_max )
		extra = self.calcTwoSecondRule( source, source.magic_damage * (1+self.magicPercent) )
		
		#����Ŀ������buff�����˺�
		if self.extraTBuff and not receiver.isDestroyed :
			for index, buff in enumerate( receiver.attrBuffs ):
				spell = buff["skill"]
				if spell.getBuffID() in self.extraTBuff[0]:
					base += self.extraTBuff[1]
		#����ʩ��������buff�����˺�
		if self.extraSBuff:
			for index, buff in enumerate( source.attrBuffs ):
				spell = buff["skill"]
				if spell.getBuffID() in self.extraSBuff[0]:
					base += self.extraSBuff[1]
		#����ʩ����Ѫ�����ڰٷֱȶ����˺�
		if self.extraSHP:
			if float(source.HP)/source.HP_Max <= self.extraSHP[0]:
				base += self.extraSHP[1]
		#����ʩ������������˺�
		extra_snake = source.queryTemp( "SNAKE_EXTRA", 0 )
		base += extra_snake
		
		skilldamage = self.calcProperty( base, extra * self._shareValPercent, dynPercent + source.magic_skill_extra_percent / csconst.FLOAT_ZIP_PERCENT, dynValue + source.magic_skill_extra_value / csconst.FLOAT_ZIP_PERCENT )
		return skilldamage
	

class Spell_FixTargetMagicHomingChild( Spell_MagicHomingChild ):
	"""
	�̶�Ŀ�귨�������Ӽ���
	"""

	def __init__( self ):
		"""
		"""
		Spell_MagicHomingChild.__init__( self )
		self._receivers = []

	def onUse( self, caster, target, receivers ) :
		"""
		"""
		self._receivers = receivers
		data = self.addToDict()
		nSkill = self.createFromDict( data )
		nSkill.cast( caster, target )

	def getReceivers( self, caster, target ):
		"""
		virtual method
		ȡ�����еķ���������������Entity�б�
		���е�onArrive()������Ӧ�õ��ô˷�������ȡ��Ч��entity��
		@return: array of Entity

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		print self, self._receivers
		return self._receivers

	def valid( self, target ):
		"""
		���Ŀ���Ƿ�������
		"""
		spellTarget = target.getObject()
		try:
			if spellTarget.state == csdefine.ENTITY_STATE_DEAD:
				return csstatus.SKILL_CHANGE_TARGET
			return csstatus.SKILL_GO_ON
		except AttributeError, errstr:
			# ֻ������󣬵���Ȼ��Ч���õ�Ҫ�󲻷��ϵĽ��
			# ԭ�������������Ʒ��һ���entity�ǲ����У�����������û�У�isDead()������
			INFO_MSG( errstr )
		return csstatus.SKILL_CHANGE_TARGET

	def addToDict( self ):
		"""
		virtual method.
		���������Ҫ��������ݣ����ݱ�����һ��dict����������꿴SkillTypeImpl��
		�˽ӿ�Ĭ�Ϸ��أ�{ "param": None }������ʾ�޶�̬���ݡ�

		@return: ����һ��SKILL���͵��ֵ䡣SKILL������ϸ���������defs/alias.xml�ļ�
		"""
		return { "param" : { "receivers" : self._receivers } }

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

		obj._receivers = data["param"]["receivers"]

		if not data.has_key( "uid" ) or data[ "uid" ] == 0:
			obj.setUID( newUID() )
		else:
			obj.setUID( data[ "uid" ] )
		return obj
