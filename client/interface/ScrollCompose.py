# -*- coding: gb18030 -*-
"""
�������䷽ѧϰ
"""
import event.EventCenter as ECenter
from ItemSystemExp import SpecialComposeExp
specom = SpecialComposeExp.instance()

class ScrollCompose:
	"""
	�������䷽ѧϰ������
	"""
	def __init__( self ):
		"""
		��ʼ��״̬��Ҫ��Fight��ʼ��֮ǰ
		"""
		pass
		
	def onClientGetScrollSkill( self, sc ):
		"""
		ѧ��һ���䷽
		"""
		
		ECenter.fireEvent( "EVT_ON_ROLE_GET_SCROLL_SKILL", sc, len( self.scrollSkill ) - 1 )
		
	def delScrollSkill( self, idx ):
		"""
		�����������ɾ��һ���䷽
		"""
		self.cell.sc_requestDelSkill( idx )
		
	def onDelScrollSkill( self, idx ):
		"""
		ɾ��һ���䷽�ɹ�
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_DEL_SCROLL_SKILL", idx )
	
	def onClientDecCount( self, idx ):
		"""
		�䷽ʹ�ô�������
		"""
		pass
	
	def sc_getComposeCost( self, scrollID ):
		"""
		��ȡ�ʽ�����
		"""
		return specom.getRequireMoney( scrollID )