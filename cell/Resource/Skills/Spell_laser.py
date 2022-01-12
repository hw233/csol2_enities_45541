# -*- coding: gb18030 -*-

"""
"""
# ͼ�ڼ���

import BigWorld
import random
from SpellBase import *
import csstatus
import items
import LostItemDistr
import csdefine
import utils

areaToNumList = {
					'a' : [1,2],
					'b' : [2,3],
					'c' : [3,4],
					'd' : [4,5],
					'e' : [5,1]
				}

class Spell_laser( Spell ):
	"""
	ͼ�ڼ���
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
		self.param2 = ( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else "" ) 				# ͼ�����ù����entityType

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

		entityList = receiver.entitiesInRangeExt( self.param1, self.param2, receiver.position )
		if len( entityList ) <= 0:
			receiver.onReceiveSpell( caster, self )
			return
		# �����һ����Χ�ڣ��ҵ�entityType��entity
		findEntity = entityList[0]

		# ת��--����ת��Ŀ��
		y = utils.yawFromPos( receiver.position, findEntity.position )
		receiver.direction = ( 0, 0, y )
		receiver.planesAllClients( "setFilterYaw", ( y, ) )

		area = findEntity.queryTemp( "trapArea", 'a' )		# ȡ��findEntity�ϴ�����������
		numList = areaToNumList[area]					# �ҵ�findEntity�������򣬶�Ӧ�Ļ��ر��

		spaceBase = BigWorld.cellAppData["spaceID.%i" % receiver.spaceID]
		try:
			spaceEntity = BigWorld.entities[ spaceBase.id ]		# �ҵ�����
		except:
			DEBUG_MSG( "not find the spaceEntity!" )

		lastNum = spaceEntity.queryTemp( "lastNum", 0 ) # ȡ��spaceEntity�������ϴμ�¼�Ļ��ر��

		num = int(receiver.getScript().param1)		# ȡ��laser�ı�ţ���ο����Ļ��ر��

		if [lastNum,num] == numList or [num, lastNum] == numList: 		# ������Ⱥ�2�ο����Ļ��� ���Ϲ���
			findEntity.onDestroySelfTimer(0,0)		# ������Ч������findEntity
			spaceEntity.setTemp( "lastNum", 0 )		# ������Ч�󣬰����һ�ε���Ļ��ؼ�¼����Ϊ0�����¿�ʼ��
		else:
			spaceEntity.setTemp( "lastNum", num )	# spaceEntity������û�д�����������һ��ֵ

		receiver.onReceiveSpell( caster, self )
