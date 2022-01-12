# -*- coding: gb18030 -*-
#
# �ٻ������ּ���

from bwdebug import *
from Spell_BuffNormal import Spell_BuffNormal
from ObjectScripts.GameObjectFactory import g_objFactory



class Spell_ProtectedSummon( Spell_BuffNormal ):
	"""
	�ٻ�
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_BuffNormal.__init__( self )
		self.className = "" #������NPC��classname
		self.level = 1	#������NPC�ȼ� Ĭ��1
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )
		self.className = dict["param1"]
		if dict["param2"] != "" :
			self.level = int(dict["param2"])


	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
			
		entity = receiver.createObjectNearPlanes( self.className, tuple( receiver.position ), receiver.direction,{"level":self.level,"spawnPos":tuple( receiver.position ) } )
		entity.targetID = receiver.id
		self.receiveLinkBuff( caster, receiver )
		
