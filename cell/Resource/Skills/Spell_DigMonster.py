# -*- coding: gb18030 -*-
#
# $Id: Spell_DigMonster.py,v 1.7 2007-12-18 04:15:42 kebiao Exp $

"""
"""

from SpellBase import *
from bwdebug import *
import ECBExtend
import LostItemDistr
from ObjectScripts.GameObjectFactory import g_objFactory

class Spell_DigMonster( Spell ):
	"""
	�ٻ�
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

		summonsSection = dict["Summons"]
		self._npcs = []											# like as [npc_class_key_name, ...]
		self._lifetime = 0										# NPC/MONSTER����ʱ�䣬��λ���룻���Ϊ0���ʾ���Զ���ʧ
		for sec in summonsSection.values():
			if sec.name == "Lifetime":
				self._lifetime = summonsSection.readInt( "Lifetime" )			# ��ȡ���ʱ��
			elif sec.name == "NPC":
				self._npcs.append( sec.asString )

	def getReceivers( self, caster, targetEntity ):
		"""
		ȡ�����еķ���������������Entity�б�
		���е�onArrive()������Ӧ�õ��ô˷�������ȡ��Ч��entity��

		@rtype: list of Entity
		"""
		return []

	def onReceiveBefore_( self, caster, receiver ):
		"""
		virtual method.
		���ܷ���֮ǰ��Ҫ��������
		"""
		assert receiver is not None		# ǿ��ֻ�ܶ�entityʹ��

		# �ٻ�����Ŀ��
		itemDistr = list( LostItemDistr.instance.DefaultItemDistr )		# ���ݵȼ�ȡ�õ�����Ʒ�ֲ�ͼ
		direction = receiver.direction
		pos = receiver.position

		# ��ʼ��NPC
		for keyName in self._npcs:
			x1, z1 = itemDistr.pop(0)										# ȡ��ƫ��λ��
			x, y, z = x1 + pos[0], pos[1], z1 + pos[2]						# ��������õ�λ��
			entity = receiver.createObjectNearPlanes( keyName, (x, y, z), direction, {} )
			entity.spawnPos = (x, y, z)	# �ƶ�����������׷����Χ
			if self._lifetime > 0:
				# ����һ���Զ���ʧ��time
				entity.addTimer( self._lifetime, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )
