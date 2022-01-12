# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from Spell_Item import Spell_Item
import items
import random
import csdefine
import ECBExtend
g_items = items.instance()

class Spell_QuestItem_Catch( Spell_Item ):
	"""
	ץ�����������������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )
		self._monsterID = ""		# ����ID
		self._isAllCatch = False	# �Ƿ�ȫ��ץ��
		self._itemID = 0			# ������ƷID

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self._monsterID = str( dict["param1"] )
		self._isAllCatch = bool( int( dict["param2"] ) )	# ��0ץ��һ������1ȫ��ץ��
		self._itemID = int( dict["param4"] )

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
			self.onArrive( caster, target )
		else:
			# �ӳ�
			caster.addCastQueue( self, target, delay )

		#������Ʒ ֻ����Ʒ�ɹ�ʹ��֮��ſ��Զ���Ʒ���������в���
		self.updateItem( caster )

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
		receivers = self.getReceivers( caster, target )
		usefulReceivers = []
		for receiver in receivers:
			if not hasattr( receiver, "className" ) or receiver.className != self._monsterID:	# ������������������ֱ������
				continue
			receiver.clearBuff( self._triggerBuffInterruptCode )
			usefulReceivers.append( receiver )

		if self._isAllCatch:	# ȫ��ץ��
			for re in usefulReceivers:
				self.receive( caster, re )
				self.receiveEnemy( caster, re )
		else:
			if len( usefulReceivers ):
				en = random.choice( usefulReceivers ) # ���ȡһ��
				self.receive( caster, en )
				self.receiveEnemy( caster, en )

		if not caster.isDestroyed:
			caster.onSkillArrive( self, usefulReceivers )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		Spell_Item.receive( self, caster, receiver )

		receiver.addTimer( 0.1, 0, ECBExtend.MONSTER_CORPSE_DELAY_TIMER_CBID )	# ���ٹ���
		item = g_items.createDynamicItem( self._itemID , 1 )
		caster.addItem( item, csdefine.ADD_ITEM_QTSGIVEITEMS )	# �������