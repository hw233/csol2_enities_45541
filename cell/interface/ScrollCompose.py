# -*- coding: gb18030 -*-
"""
制作卷配方学习
"""
CROLLSKILL_MAX_COUNT = 10

class ScrollCompose:
	"""
	制作卷配方学习操作类
	"""
	def __init__( self ):
		"""
		初始化状态。
		"""
		pass
		
	def sc_canLearnSkill( self ):
		"""
		是否还可以学习配方
		"""
		return len( self.scrollSkill ) < CROLLSKILL_MAX_COUNT
	
	def sc_learnSkill( self, skillInfo ):
		"""
		学习某技能
		"""
		if self.sc_canLearnSkill():
			self.scrollSkill.append( skillInfo )
			self.client.onClientGetScrollSkill( skillInfo )
			
		
	def sc_requestDelSkill( self, srcEntityID, idx ):
		"""
		客户端申请删除已学会配方
		"""
		if not self.hackVerify_( srcEntityID ) : return
		if len( self.scrollSkill ) > idx :
			self.scrollSkill.remove( self.scrollSkill[ idx ] )
			self.client.onDelScrollSkill( idx )
		
	def sc_canUseSkill( self, idx ):
		"""
		是否可以使用此配方
		"""
		if len( self.scrollSkill ) > idx :
			skillInfo = self.scrollSkill[ idx ]
			maxCount  = skillInfo[ "maxCount" ]
			if maxCount > 0:
				return  skillInfo 
		return None
		
		
	def sc_usedSkill( self, idx ):
		"""
		成功使用了一次此配方
		"""
		skillInfo = self.scrollSkill[ idx ]
		skillInfo[ "maxCount" ] -= 1
		if skillInfo[ "maxCount" ] > 0:
			self.client.onClientDecCount( idx )
		else:
			self.client.onDelScrollSkill( idx )
		