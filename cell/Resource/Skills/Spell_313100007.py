# -*- coding: gb18030 -*-

"""
"""
# ͼ�ڼ���

import random
from SpellBase import *
import csstatus
import items
import LostItemDistr
import csdefine

BUFF_ID1_1		=	13008
BUFF_ID1_2		=	13009
BUFF_ID1_3		=	13010
BUFF_ID2		=	62004
BUFF_ID_S = [BUFF_ID1_1, BUFF_ID1_2, BUFF_ID1_3]

class Spell_313100007( Spell ):
	"""
	������֮Ӱר��ͼ�ڼ���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		
		self.param1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 			# ͼ�����þ���
		self.param2 = ( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else "" ) 		# ͼ�����ù����className
		
		self._receiverObject = ReceiverObject.newInstance( 0, self )		# �����߶������а��������ߵ�һЩ�Ϸ����ж�
		self._castObjectType = csdefine.SKILL_CAST_OBJECT_TYPE_NONE	# ʩչĿ�����ͣ�see also CAST_OBJECT_TYPE_*
		self._castObject = ObjectDefine.newInstance( self._castObjectType, self )
		
	def getIntonateTime( self , caster ):
		"""
		virtual method.
		��ȡ�������������ʱ�䣬������ʱ������б�Ҫ�����Ը��������߾��������ʱ����

		@param caster:	ʹ�ü��ܵ�ʵ�塣�����Ժ���չ����ĳЩ�츳��Ӱ��ĳЩ���ܵ�Ĭ������ʱ�䡣
		@type  caster:	Entity
		@return:		�ͷ�ʱ��
		@rtype:			float
		"""
		return caster.queryTemp( "quest_box_intone_time", 0.0 )

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
		return csstatus.SKILL_GO_ON

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
		entity = target.getObject()
		if entity is None or entity.isDestroyed:
			return []
		return [ entity ]

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		
		isFindBoss = False
		boss = None
		monsterList = receiver.entitiesInRangeExt( self.param1, "Monster", receiver.position )
		for e in monsterList:
			if e.className == self.param2:
				boss = e
				isFindBoss = True
				break
		if boss is None or not isFindBoss:
			receiver.onReceiveSpell( caster, self )
			return
		boss.removeTemp( "buffBeInteruptFromTuteng" )
		# �����һ����Χ�ڣ��ҵ���Ӧ��boss
		# �жϿ�����ͼ���Ƿ���boss��buffһ��
		for buffID in BUFF_ID_S:
			if len( boss.findBuffsByBuffID(buffID) ) <= 0:	# ���boss����û��buff
				continue
			if int( receiver.getScript().param2 ) != buffID:
				boss.addHP( int(boss.HP_Max / 10) )	# ��boss����10%��Ѫ��
				continue
			boss.removeAllBuffByBuffID( buffID, [csdefine.BUFF_INTERRUPT_NONE]  )
			boss.removeAllBuffByBuffID( BUFF_ID2, [csdefine.BUFF_INTERRUPT_NONE]  )
			boss.setTemp("buffBeInteruptFromTuteng",True)
			
		if boss.queryTemp("buffBeInteruptFromTuteng"):
			# �����������󣬼���BOSS����һ�����ܵ�ʹ�ô�������
			skUseCount = boss.queryTemp( "uskCount", 0 )
			boss.setTemp( "uskCount", skUseCount - 1 )
			
		receiver.onReceiveSpell( caster, self )