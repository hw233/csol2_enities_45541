# -*- coding: gb18030 -*-
"""
�����չ�ԡ��̲���ǵļ��� 2009-01-15 SongPeifang
"""

from SpellBase import *
from bwdebug import *
import csstatus
import csdefine
import items
import random
import BigWorld
import sys

g_items = items.instance()

class Spell_313100006( Spell ):
	"""
	�����չ�ԡ��̲����,���Ŷ����������Ʒ���߲���buffЧ��
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
		self._receiverObject = ReceiverObject.newInstance( 0, self )# �����߶������а��������ߵ�һЩ�Ϸ����ж�
		self._castObjectType = csdefine.SKILL_CAST_OBJECT_TYPE_NONE	# ʩչĿ�����ͣ�see also CAST_OBJECT_TYPE_*
		self._castObject = ObjectDefine.newInstance( self._castObjectType, self )
		eventRatesStr = dict["param1"].split( '|' )	# ���������¼��ĸ��� �����ɫ����ĸ���:pram2|��òʺ籦��ĸ���:pram3|�����Ե����ĸ���:pram4|��ò�ɫ����ĸ���:pram5
		fiveColorPearls = dict["param2"].split( '|' )	# ��ɫ����ļ��� id1|id2|id3|id4|id5
		rainbowPearls = dict["param3"].split( '|' )	# �ʺ籦��ļ��� id1|id2|id3|id4|id5|id6|id7
		friendlyPearls = dict["param4"].split( '|' )	# ��Ե����ļ��� id1|id2
		colorPearls = [ dict["param5"] ]				# ��ɫ���� id
		tempDict = { "param2":fiveColorPearls, "param3":rainbowPearls, "param4":friendlyPearls, "param5":colorPearls }

		self._ratesEvent = {}						# ���ʼ���Ӧ���¼� {����:��Ʒ����} �� {0.15:[50101046,50101047,50101048,50101049,50101050]}
		tempRate = 0								# ����
		for rateStr in eventRatesStr:				# eventRatesStr��������[ "0.15:param2", "0.15:param3", "0.5:param4", "0.25:param5", "0.4:param6" ]
			tempArr = rateStr.split( ':' )			# tempArr��������[����,������] �� [0.5,param3]
			rate = tempRate + int( ( float( tempArr[0] ) + 0.0005 ) * 1000 ) # ����Ҫ��������ΪKey�������Բ����ظ�����Ϊ�������0
			self._ratesEvent[ rate ] = tempDict[ tempArr[1] ]	# {����(����������Ҫ����1000��):��Ʒ����}
			tempRate = rate

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
		# ʩ���߿����Ҳ��� �μ�receiveOnReal�ӿ�
		if not caster:
			return

		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# �ص����������Լ�ִ��ĳЩ����
		receiver.onReceiveSpell( caster, self )
		eventRate = random.random()
		items = []	# String���飬������ƷID���ַ���
		keyArray = self._ratesEvent.keys()
		keyArray.sort()
		for r in keyArray:
			if eventRate <= r/1000.0:
				items = self._ratesEvent[r]
				break
		if len( items ) > 0:
			# �ҵ�����Ʒ�б�˵����������ǵ���Ʒ��
			direction = (0.0, 0.0, 0.0)
			pos = receiver.position					# �����λ��
			propDict = { "ownerIDs": [caster.id] }	# ������ȡ����
			index = random.randint( 0, len( items )-1 )
			itemID = int( items[ index ] )
			# ����ƫ��λ��
			x1 = random.randint( -1, 1 )
			y1 = 1
			z1 = random.randint( -1, 1 )
			# ��ʼ�ŵ���
			amount = 1
			item = g_items.createDynamicItem( itemID , amount )
			tmpList = [ item ]
			x, y, z = x1 + pos[0], y1 + pos[1], z1 + pos[2]	# ��������õ�λ�õ�ƫ��λ��
			bootyOwner = ( caster.id, 0 )
			collide = BigWorld.collide( caster.spaceID, ( x, y + 2, z ), ( x, y - 1, z ) )
			if collide != None:
				# ������Ʒ��ʱ��Ե��������ײ��������Ʒ�������
				y = collide[0].y
			itemBox = receiver.createEntityNearPlanes( "DroppedBox", (x, y, z), direction, {} )
			itemBox.init( bootyOwner, tmpList )
		else:
			# û���ҵ���Ʒ�б�˵��eventRate���ڵ�����Ʒ�ĸ����ڣ������α��ǻ��ͷ�buff
			receiveScript = receiver.getScript()
			skills = receiveScript.param1.split( "|" )
			if len( skills ) == 0:
				ERROR_MSG( "����QuestBox��������,��Ч�ļ���ID!" )
			index = random.randint( 0, len( skills )-1 )
			skill = int( skills[ index ] )
			receiver.spellTarget( skill, caster.id )
