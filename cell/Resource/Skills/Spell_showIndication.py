# -*- coding: gb18030 -*-

import csdefine
from SpellBase import SystemSpell


class Spell_showIndication( SystemSpell ) :
	"""
	��ʾ��Ļ�м�ĵ���/����ʹ����ʾ
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		SystemSpell.__init__( self )
		self.indicationIds = []										# ��ʾ��ID

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		SystemSpell.init( self, dict )
		self.indicationIds = [eval( idtId ) for idtId in dict["param1"].split(" ")]	# ��ȡ��ʾID

	def receive( self, caster, receiver ) :
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):		# ֻ�����ʩ�ţ����������
			return
			
		for idtIdList in self.indicationIds :
			receiver.client.showCastIndicator( idtIdList )
