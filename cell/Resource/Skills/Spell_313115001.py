# -*- coding: gb18030 -*-
#

from bwdebug import *
import random
from SpellBase import *
import csstatus
import items
import LostItemDistr
import csdefine
import BigWorld
import sys

g_items = items.instance()

class Spell_313115001( Spell ):
	"""
	���ս��ռ����Ӫ��ʱ���ü���
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
		self._receiverObject = ReceiverObject.newInstance( 0, self )		# �����߶������а��������ߵ�һЩ�Ϸ����ж�
		self._castObjectType = csdefine.SKILL_CAST_OBJECT_TYPE_NONE			# ʩչĿ�����ͣ�see also CAST_OBJECT_TYPE_*
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
		
		if BigWorld.entities.has_key( caster.id ) and caster.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
			if caster.yiJieFaction != 0 and caster.yiJieFaction == target.getObject().ownBattleFaction :
				caster.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_CANNOT_OCCUPY_AGAIN, "" )
				return
			elif caster.yiJieAlliance != 0 and caster.yiJieAlliance == target.getObject().ownBattleFaction :
				caster.client.onStatusMessage( csstatus.YI_JIE_ZHAN_CHANG_CANNOT_OCCUPY_ALLIANCE, "" )
				return
		return Spell.useableCheck( self, caster, target )
		

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

		#receiver.onReceiveSpell( caster, self )

		itemDistr = list( LostItemDistr.instance.DefaultItemDistr )		# ���ݵȼ�ȡ�õ�����Ʒ�ֲ�ͼ
		itemDistr.pop(0)	# ȥ����0λ,��Ϊ��0λ����������,������
		direction = (0.0, 0.0, 0.0)
		pos = receiver.position

		#  ������ȡ����
		propDict = { "ownerIDs": [caster.id] }

		receiveScript = receiver.getScript()
		items = (
			( receiveScript.param1, receiveScript.param2, receiveScript.param3 ),
			( receiveScript.param4, receiveScript.param5, receiveScript.param6 ),
			#( receiveScript.param7, receiveScript.param8, receiveScript.param9 ),
		)

		# ��ʼ�ŵ���
		tempList = []
		for keyName, amount, rate in items:
			if len( keyName ) == 0:
				continue
				
			if not rate:
				continue
				
			if random.random() > float( rate ):
				continue
				
			amount = int( amount )

			item = g_items.createDynamicItem( int( keyName, 10 ), 1 )
			if item is None:
				ERROR_MSG( "Create drop item error: monster's className:%s ,item's ID:%s" % ( receiver.className, int( keyName, 10 ) ) )
				continue
			item.setAmount( amount )
			tempList.append( item )

		receiver.onItemsArrived( caster, tempList )

