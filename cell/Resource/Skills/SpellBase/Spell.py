# -*- coding: gb18030 -*-
#
# $Id: Spell.py,v 1.47 2008-08-13 07:55:54 kebiao Exp $

"""
������
"""

import Language
import csdefine
import csstatus
import utils
from bwdebug import *
from csdefine import *
from interface.State import State
from Skill import Skill
import ObjectDefine
import AreaDefine
import RequireDefine
import CooldownFlyweight
import SkillTargetObjImpl
from CasterCondition import CasterCondition
import ReceiverObject
from EffectState import EffectState
from random import randint
from SmartImport import smartImport
g_cooldowns = CooldownFlyweight.CooldownFlyweight.instance()

from CPUCal import CPU_CostCal

class BuffData:
	"""
	buffʵ���ļ򵥷�װ
	"""
	def __init__( self ):
		"""
		"""
		self._rate = 100	#��Buff���ӱ���
		self._buff = None	#BUFFʵ��

	def init( self, dictDat, skillID, index ):
		"""
		@param skillID:Դ����ID
		@param index: ��BUFF�ڼ����е�����λ��
		"""
		if dictDat[ "LinkRate" ] > 0.0:
			self._rate = dictDat[ "LinkRate" ]
		script = "Buff_" + str( int( dictDat[ "ID" ] ) )
		self._buff = smartImport( "Resource.Skills." + script + ":" + script )()
		self._buff.init( dictDat )
		self._buff.setSource( skillID, index )
		Skill.register( self._buff.getID(), self._buff )

	def getBuff( self ):
		"""
		ȡ��BUFFʵ��
		"""
		return self._buff

	def getLinkRate( self ):
		"""
		���ظ�BUFF���ӵı���
		"""
		return self._rate

class Spell( Skill, EffectState ):
	def __init__( self ):
		"""
		���캯����
		"""
		Skill.__init__( self )
		EffectState.__init__( self )
		"""
		����CD������
		1:����CD CD��1 ms:8��
		2������CD������ʩ�ſ�ʼʱ�鿴�Ƿ�����ЩCDû����ȴ��ϣ� ������ʩ��
		3������CD������һ��������ȫ��CD ʹ��������Ҳ��ȴ

		self._casterCondition = []		# ʩ���߿���ʩ����Ҫ��(�ж�һ��ʩ�����Ƿ���ʩչ�������)
		self._receiverCondition = []		# ���Ա�ʩ����������Ҫ��(�ж�һ��entity�Ƿ��Ƿ���������������)
		��ս������ʩ�����ɹ�����ħ�����ߵȶ�����Ҫ��
		"""
		self._level = 0												# ���ܵȼ�
		self._maxLevel = 0											# spell max level
		self._casterCondition = CasterCondition()					# ʩ���߿���ʩ����Ҫ��(�ж�һ��ʩ�����Ƿ���ʩչ�������)
		self._receiverObject = ReceiverObject.newInstance( 0, self )		# �����߶������а��������ߵ�һЩ�Ϸ����ж�
		self._baseType = csdefine.BASE_SKILL_TYPE_NONE  			# ���ܻ������࣬see also SkillDefine.BASE_SKILL_TYPE
		self._rangeMax = 0.0										# float; ʩչ���룬�ף�Ĭ��ֵ0����ʾ�޾�������
		self._rangeMin = 0.0										# float; ʩչ���룬�ף�Ĭ��ֵ0����ʾ�޾�������
		self._speed = 0.0											# float; ���������ٶȣ���/�룬Ĭ��ֵ0����ʾ˲��
		self._castObjectType = csdefine.SKILL_CAST_OBJECT_TYPE_NONE	# ʩչĿ�����ͣ�see also CAST_OBJECT_TYPE_*
		self._require = RequireDefine.newInstance( None )			# see also RequireDefine; ʩ�ŷ������ĵĶ���; Ĭ��Ϊ"None"��������
		self._buffLink	= []										# ���ܲ�����BUFF [buffDataInstance...]
		self._springOnUsedCD = []									# �÷�����������CD ����ʹ�ú�
		self._springOnIntonateOverCD = []							# �÷�����������CD ����������
		self._limitCooldown = []									# �÷�������CD
		self._skillCastRange = 0.0									# �����ͷž���
		self._effect_min = 0										# ����Ӱ������Сֵ
		self._effect_max = 0										# ����Ӱ�������ֵ
		self._castTargetLvMin = 0									# ���ܿ�ʩչ������׼�
		self._castTargetLvMax = 0									# ���ܿ�ʩչ������߼�
		self.isNotRotate = False									# ʩ���Ƿ���Ҫת��
		self._receiveDelayTime = 0.0  #����Ч���ӳ�ʱ�� ������ʩ��ǰҡ��
		self._triggerBuffInterruptCode = []

	def init( self, dictDat ):
		"""
		��ȡ��������
		@param dictDat:	��������
		@type dictDat:	python dictDat
		"""
		Skill.init( self, dictDat )
		EffectState.init( self, dictDat)
		self._rangeMax = dictDat[ "RangeMax" ]
		self._rangeMin = dictDat[ "RangeMin" ]
		self._intonateTime = dictDat[ "IntonateTime" ]								# ����ʱ��
		self._baseType = eval( str( dictDat[ "Type" ] ) )
		self.isNotRotate = dictDat.get( "isNotRotate", 0 )
		self._receiveDelayTime = dictDat.get( "receiveDelayTime", 0.0 )
		self._getCombatCount = dictDat.get( "getCombatCount", 0 )
		
		self._skillCastRange = dictDat[ "CastRange" ]								# �����ͷž���
		if self._skillCastRange < self._rangeMax:
			self._skillCastRange = self._rangeMax + 0.1 							#��֤�ͷž��벻С�ڼ���ʩ������

		for i in xrange( len( dictDat[ "SpringUsedCD" ] ) ):
			val = dictDat[ "SpringUsedCD" ][ i ]
			self._springOnUsedCD.append( ( val[ "CDID" ], val[ "CDTime" ] ) )

		for i in xrange( len( dictDat[ "SpringIntonateOverCD" ] ) ):
			val = dictDat[ "SpringIntonateOverCD" ][ i ]
			self._springOnIntonateOverCD.append( ( val[ "CDID" ], val[ "CDTime" ] ) )

		for i in xrange( len( dictDat[ "LimitCD" ] ) ):
			self._limitCooldown.append( dictDat[ "LimitCD" ][ i ] )

		self._level = dictDat[ "Level" ]
		self._maxLevel = dictDat[ "MaxLevel" ]
		self._speed = dictDat[ "Speed" ]											# ���������ٶȣ���/�룬Ϊ0���ʾ˲��
		self._castObjectType = dictDat["CastObjectType"][ "type" ]					# ʩչĿ�����ͣ�see also CAST_OBJECT_TYPE_*
		self._castObject = ObjectDefine.newInstance( self._castObjectType, self )
		self._castObject.init( dictDat[ "CastObjectType" ] )

		if len( dictDat[ "Require" ] ) > 0: #list
			self._require = RequireDefine.newInstance( dictDat[ "Require" ] )		# ʩ�ŷ������ĵĶ���

		if len( dictDat[ "CasterCondition" ] ) > 0: #dict
			self._casterCondition.init( dictDat["CasterCondition"] )

		val = dictDat[ "ReceiverCondition" ]
		if len( val ) > 0: #dict
			conditions = val[ "conditions" ]
			if len( conditions ) > 0:
				self._receiverObject = ReceiverObject.newInstance( eval( conditions ), self )
				self._receiverObject.init( val )

		self._effect_min = dictDat[ "EffectMin" ]									# ����Ӱ������Сֵ
		self._effect_max = dictDat[ "EffectMax" ]									# ����Ӱ�������ֵ
		if self._effect_max < self._effect_min:
			self._effect_max = self._effect_min

		self._castTargetLvMin = dictDat[ "CastObjLevelMin" ]
		self._castTargetLvMax = dictDat[ "CastObjLevelMax" ]
		
		for val in dictDat[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )

		self._param5 = dictDat[ "param5" ]

		if dictDat.has_key( "buff" ):
			for i in xrange( len( dictDat[ "buff" ] ) ):
				dat = dictDat[ "buff" ][ i ]
				inst = BuffData()
				inst.init( dat, self._id, i )
				self._buffLink.append( inst )

	def getLevel( self ):
		"""
		virtual method = 0.
		��ȡ���ܼ���
		"""
		return self._level

	def getMaxLevel( self ):
		"""
		virtual method = 0.
		��ȡ������߼���
		"""
		return self._maxLevel

	def getRangeMax( self, caster ):
		"""
		virtual method.
		@param caster: ʩ���ߣ�ͨ��ĳЩ��Ҫ���������Ϊ����ķ����ͻ��õ���
		@return: ʩ������
		"""
		return self._rangeMax

	def getRangeMin( self, caster ):
		"""
		virtual method.
		@param caster: ʩ���ߣ�ͨ��ĳЩ��Ҫ���������Ϊ����ķ����ͻ��õ���
		@return: ʩ����С����
		"""
		return self._rangeMin

	def getCastRange( self, caster ):
		"""
		�����ͷž���
		"""
		return self._skillCastRange

	def getFlySpeed( self ):
		"""
		@return: �����ķ����ٶ�
		"""
		return self._speed

	def getBuffLink( self, index ):
		"""
		"""
		return self._buffLink[ index ]

	def getBuffsLink( self ):
		"""
		@return: ���м��ܲ�����buff
		"""
		return self._buffLink[:]

	def getCastTargetLevelMin( self ):
		"""
		virtual method = 0.
		���ܿ�ʩչ������׼�
		"""
		return self._castTargetLvMin

	def getCastObject( self ):
		"""
		virtual method.
		ȡ�÷�����ʩ����Ŀ������塣
		@rtype:  ObjectDefine Instance
		"""
		return self._castObject

	def getCastTargetLevelMax( self ):
		"""
		virtual method = 0.
		���ܿ�ʩչ������߼�
		"""
		return self._castTargetLvMax

	def getParam5Data( self ):
		"""
		��ȡparam5���� by����
		"""
		return self._param5

	def getReceiveDelayTime( self ):
		"""
		��ȡ����Ч���ӳ�ʱ��
		"""
		return self._receiveDelayTime

	def calcDelay( self, caster, target ):
		"""
		virtual method.
		ȡ���˺��ӳ�
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: float(��)
		"""
		return target.calcDelay( self, caster )


	def getIntonateTime( self , caster ):
		"""
		virtual method.
		��ȡ�������������ʱ�䣬������ʱ������б�Ҫ�����Ը��������߾��������ʱ����

		@param caster:	ʹ�ü��ܵ�ʵ�塣�����Ժ���չ����ĳЩ�츳��Ӱ��ĳЩ���ܵ�Ĭ������ʱ�䡣
		@type  caster:	Entity
		@return:		�ͷ�ʱ��
		@rtype:			float
		"""
		return ( self._intonateTime + caster.queryTemp( "intonateTime_extra", 0 ) ) * ( 1 + caster.queryTemp( "intonateTime_percent", 0.0 ) ) + caster.queryTemp( "intonateTime_value", 0 )

	def getMaxCooldown( self, caster ):
		"""
		virtual method.
		��ȡ�����������cooldown(Ҳ���Ǹ÷�����ʩչ��ʱ��)
		"""
		maxTimeVal = 0.0
		for cd in self._limitCooldown:
			timeVal = caster.getCooldown( cd )
			maxTimeVal = max( maxTimeVal, timeVal )
		return maxTimeVal

	def isCooldown( self, caster ):
		"""
		virtual method.
		�жϷ��������cooldown�Ƿ��ѹ�

		@return: BOOL
		"""
		for cd in self._limitCooldown:
			timeVal = caster.getCooldown( cd )
			if not g_cooldowns[ cd ].isTimeout( timeVal ):
				return False
		return True

	def setCooldownInUsed( self, caster ):
		"""
		virtual method.
		��ʩ�������÷��������cooldownʱ�� (����ʹ�ú� ������ʼʱ)

		@return: None
		"""
		if len( self._springOnUsedCD ) <= 0: return
		for cd, time in self._springOnUsedCD:
			try:
				endTime = g_cooldowns[ cd ].calculateTime( time )
			except:
				EXCEHOOK_MSG("skillID:%d" % self.getID())
			if caster.getCooldown( cd ) < endTime:
				caster.changeCooldown( cd, time, time, endTime )

	def setCooldownInIntonateOver( self, caster ):
		"""
		virtual method.
		��ʩ�������÷��������cooldownʱ��(������������ʱ)

		@return: None
		"""
		if len( self._springOnIntonateOverCD ) <= 0: return
		for cd, time in self._springOnIntonateOverCD:
			try:
				endTime = g_cooldowns[ cd ].calculateTime( time )
			except:
				EXCEHOOK_MSG("skillID:%d" % self.getID())
			if caster.getCooldown( cd ) < endTime:
				caster.changeCooldown( cd, time, time, endTime )

	def getType( self ):
		"""
		ȡ�û�����������
		��Щֵ��BASE_SKILL_TYPE_*֮һ
		"""
		return self._baseType

	def calcExtraRequire( self, caster ):
		"""
		virtual method.
		���㼼�����ĵĶ���ֵ�� ������װ�����߼���BUFFӰ�쵽���ܵ�����
		return : (�������ĸ���ֵ���������ļӳ�)
		"""
		return ( 0, 0.0 )

	def checkRequire_( self, caster ):
		"""
		virtual method.
		��������Ƿ�
		@return: INT��see also SkillDefine.SKILL_*
		"""
		return self._require.validObject( caster, self )

	def doRequire_( self, caster ):
		"""
		virtual method.
		��������

		@param caster	:	�ͷ���ʵ��
		@type caster	:	Entity
		"""
		self._require.pay( caster, self )

	def getRequire( self ):
		"""
		"""
		return self._require

	def _validCaster( self, caster ):
		"""
		virtual method.
		���ʩ�����Ƿ�������������
		@return: INT��see also SkillDefine.SKILL_*
		"""
		return self._casterCondition.valid( caster )

	def interruptCheck( self, caster, reason ):
		"""
		virtual method.
		����������ʱ����ĳһ���͵��жϣ��ж������Լ���Ҫ�жϵ������������жϣ�����True����
		���ڲ����жϵļ��ܣ�ֱ�ӷ��� False��Ĭ������£�����Ӧ��������������жϼ��ܵ�������
		@param reason: �����ж�ԭ��
		@type  receiver: bool
		"""
		return True

	def onSpellInterrupted( self, caster ):
		"""
		��ʩ�������ʱ��֪ͨ��
		��Ϻ���Ҫ��һЩ����
		"""
		pass

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
		# ��鼼��cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_NOT_READY

		# ʩ��������
		state = self.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ʩ���߼��
		state = self.castValidityCheck( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ���Ŀ���Ƿ���Ϸ���ʩչ
		state = self.getCastObject().valid( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state
			
		#�����������״̬
		if caster.inHomingSpell():
			return csstatus.SKILL_CANT_CAST

		return csstatus.SKILL_GO_ON

	def castValidityCheck( self, caster, target):
		"""
		virtual method.
		У�鼼���Ƿ����ʩչ��
		�˽ӿڽ������ڵ�������������ж��Ƿ��ܶ�Ŀ��ʩչ��
		�����Ҫ�ж�һ�������Ƿ��ܶ�Ŀ��ʹ�ã�Ӧ��ʹ��intonateValidityCheck()������
		�˽ӿڻᱻintonateValidityCheck()�ӿڵ��ã��������ʱĳЩ������Ҫ�������������жϣ�
		��������ش˽ӿڲ���������жϣ�����ֻ������intonateValidityCheck()�ӿڡ�

		ע���˽ӿ��Ǿɰ��е�validCast()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		return self._validCaster( caster )

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
		if not self.isNotRotate:
			caster.rotateToSpellTarget( target )					# ת��

		# ���ü�����ȴʱ��
		self.setCooldownInUsed( caster )

		if self.getIntonateTime( caster ) <= 0.1 and self.getReceiveDelayTime() <= 0.1:
			# û������ʱ�䣬ֱ��ʩ��
			self.cast( caster, target )
			return

		#���ﴫ��target ����������һ��λ����˵����Ȼ��λ�ã���һ��entity��˵ entity�Ѿ�����
		#���cell������ô�������ж� ������Ʒ�Ҳ���ӵ���߷������ж�

		if self.getReceiveDelayTime() > 0.1:
			caster.intonate( self, target, self.getReceiveDelayTime() )
		else:
			caster.intonate( self, target, self.getIntonateTime( caster )  )# ����


	def cast( self, caster, target ):
		"""
		virtual method.
		��ʽ��һ��Ŀ���λ��ʩ�ţ���з��䣩�������˽ӿ�ͨ��ֱ�ӣ����ӣ���intonate()�������á�

		ע���˽ӿڼ�ԭ���ɰ��е�castSpell()�ӿ�

		@param     caster: ʹ�ü��ܵ�ʵ��
		@type      caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		# �������ܼ��
		caster.delHomingOnCast( self )
		self.setCooldownInIntonateOver( caster )
		# ��������
		self.doRequire_( caster )
		#֪ͨ���пͻ��˲��Ŷ���/����������
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )

		# ����ʩ�����֪ͨ����һ���ܴ�����Ŷ(�Ƿ��ܴ����Ѿ���ʩ��û�κι�ϵ��)��
		# �����channel����(δʵ��)��ֻ�еȷ�����������ܵ���
		self.onSkillCastOver_( caster, target )

		#��֤�ͻ��˺ͷ������˴����������һ��
		delay = self.calcDelay( caster, target )
		if delay <= 0.5:
			# ˲��
			#caster.addCastQueue( self, target, 0.1 )
			className = caster.className if caster.className != "" else caster.id
			CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_ARRIVE, self.getID(), className )
			self.onArrive( caster, target )
			CPU_CostCal( csdefine.CPU_COST_SKILL, csdefine.CPU_COST_SKILL_ARRIVE, self.getID(), className )
		else:
			# �ӳ�
			caster.addCastQueue( self, target, delay )
		
		#���ﴦ����Ի�ö��ٸ񶷵���
		if hasattr( caster, "calCombatCount" ) and self._getCombatCount >0 :
			caster.calCombatCount( self._getCombatCount )

	def trapCast( self, caster, target ):
		"""
		virtual method.
		���崥������ר�ý���ӿ�
		"""
		#֪ͨ���пͻ��˲��Ŷ���/����������
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )

		# ����ʩ�����֪ͨ����һ���ܴ�����Ŷ(�Ƿ��ܴ����Ѿ���ʩ��û�κι�ϵ��)��
		# �����channel����(δʵ��)��ֻ�еȷ�����������ܵ���
		self.onSkillCastOver_( caster, target )

		#��֤�ͻ��˺ͷ������˴����������һ��
		delay = self.calcDelay( caster, target )
		if delay <= 0.1:
			# ˲��
			#caster.addCastQueue( self, target, 0.1 )
			self.onArrive( caster, target )
		else:
			# �ӳ�
			caster.addCastQueue( self, target, delay )


	def onSkillCastOver_( self, caster, target ):
		"""
		virtual method.
		����ʩ�����֪ͨ
		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		# ֪ͨʩ����
		# ����һ�μ���ʩ��֪ͨ
		if not caster.isDestroyed:
			caster.onSkillCastOver( self, target )

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
		return self._receiverObject.getReceivers( caster, target )

	def onArrive( self, caster, target ):
		"""
		�����ִ�Ŀ��ͨ�档��Ĭ������£��˴�ִ�п�������Ա�Ļ�ȡ��Ȼ�����receive()�������ж�ÿ���������߽��д���
		ע���˽ӿ�Ϊ�ɰ��е�receiveSpell()
		�ر�ע��:�˷�������ʱ����̳л���Spell�е�onArrive����
		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		# ��ȡ����������
		receivers = self.getReceivers( caster, target )
		for receiver in receivers:
			#��������ʱ������һЩ����
			receiver.clearBuff( self._triggerBuffInterruptCode ) # �������ǰ�棬��Ϊ�ں����п��ܱ����ٵ�
			self.receive( caster, receiver )
			self.receiveEnemy( caster, receiver )

		if not caster.isDestroyed:
			caster.onSkillArrive( self, receivers )


	def springOnHit( self, caster, receiver, damageType ):
		"""
		��������ʱ����Ϣ�ص�
		@param   caster: ʩ����
		@type    caster: Entity
		@param   receiver: ������
		@type    receiver: Entity
		@param   damageType: �˺����
		@type    damageType: uint32
		"""
		caster.spellTarget( self.getID(), receiver.id )


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

	def canLinkBuff( self, caster, receiver, buff ):
		"""
		�ж�buff�Ƿ��ܹ�link
		@param   caster	: ʩ����
		@type    caster	: Entity
		@param   buff	: BUFF����
		@type    buff	: BUFFInstance
		@return 		: BOOL
		"""
		odds = buff.getLinkRate()
		if caster:
			skillID = self.getID()/1000
			odds += caster.skillBuffOdds.getOdds( skillID ) * 100 

		if randint( 1, 100 ) > odds:
			caster.onBuffMiss( receiver, self )
			return False

		if buff.getBuff().checkResist( caster, receiver ):
			caster.onBuffResist( receiver, buff )
			receiver.onBuffResistHit( buff )
			return False

		return True

	def receiveLinkBuff( self, caster, receiver ):
		"""
		��entity����buff��Ч��
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: ʩչ����
		@type  receiver: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		for buff in self._buffLink:
			if self.canLinkBuff( caster, receiver, buff ):
				buff.getBuff().receive( caster, receiver )				# ����buff��receive()���Զ��ж�receiver�Ƿ�ΪrealEntity
				
#
# Spell.py
