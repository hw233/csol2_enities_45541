# -*- coding: gb18030 -*-


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

class Spell_313100012( Spell ):
	"""
	������	�򿪱����ೡ����������Ŷ�����������Ʒ,������ͷ�BUFF
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
		self._receiverObject = ReceiverObject.newInstance( 0, self )				# �����߶������а��������ߵ�һЩ�Ϸ����ж�
		self._castObjectType = csdefine.SKILL_CAST_OBJECT_TYPE_NONE					# ʩչĿ�����ͣ�see also CAST_OBJECT_TYPE_*
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
		id = target.getObject().queryTemp("gossipingID",0)

		if id != 0 and BigWorld.entities.has_key( id ):
			caster.client.onStatusMessage( csstatus.ITEM_CANNOT_TOUCH, "" )
			return
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
			if len( keyName ) == 0: continue
			if random.random() > float( rate ):	continue
			amount = int( amount )

			item = g_items.createDynamicItem( int( keyName, 10 ), 1 )
			if item is None:
				ERROR_MSG( "Create drop item error: monster's className:%s ,item's ID:%s" % ( receiver.className, int( keyName, 10 ) ) )
				continue
			item.setAmount( amount )
			tempList.append( item )

		receiver.onItemsArrived( caster, tempList )
		caster.spellTarget( int(receiveScript.param7), caster.id )

