# -*- coding: gb18030 -*-
"""
�������䷽ѧϰ
"""
CROLLSKILL_MAX_COUNT = 10

class ScrollCompose:
	"""
	�������䷽ѧϰ������
	"""
	def __init__( self ):
		"""
		��ʼ��״̬��
		"""
		pass
		
	def sc_canLearnSkill( self ):
		"""
		�Ƿ񻹿���ѧϰ�䷽
		"""
		return len( self.scrollSkill ) < CROLLSKILL_MAX_COUNT
	
	def sc_learnSkill( self, skillInfo ):
		"""
		ѧϰĳ����
		"""
		if self.sc_canLearnSkill():
			self.scrollSkill.append( skillInfo )
			self.client.onClientGetScrollSkill( skillInfo )
			
		
	def sc_requestDelSkill( self, srcEntityID, idx ):
		"""
		�ͻ�������ɾ����ѧ���䷽
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if len( self.scrollSkill ) > idx :
			self.scrollSkill.remove( self.scrollSkill[ idx ] )
			self.client.onDelScrollSkill( idx )
		
	def sc_canUseSkill( self, idx ):
		"""
		�Ƿ����ʹ�ô��䷽
		"""
		if len( self.scrollSkill ) > idx :
			skillInfo = self.scrollSkill[ idx ]
			maxCount  = skillInfo[ "maxCount" ]
			if maxCount > 0:
				return  skillInfo 
		return None
		
		
	def sc_usedSkill( self, idx ):
		"""
		�ɹ�ʹ����һ�δ��䷽
		"""
		skillInfo = self.scrollSkill[ idx ]
		skillInfo[ "maxCount" ] -= 1
		if skillInfo[ "maxCount" ] > 0:
			self.client.onClientDecCount( idx )
		else:
			self.client.onDelScrollSkill( idx )
		