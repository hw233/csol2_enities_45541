# -*- coding: gb18030 -*-
from QuestBox import QuestBox

class QuestBoxFete( QuestBox ):
	
	def __init__( self ):
		QuestBox.__init__( self )
		
	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		QuestBox.load( self, section )
		
		params = self.param1.replace( "\r\n",'' )
		if self.param2 != "":
			params += ";" + self.param2.replace( "\r\n",'' )
		if self.param3 != "":
			params += ";" + self.param3.replace( "\r\n",'' )
		if self.param4 != "":
			params += ";" + self.param4.replace( "\r\n",'' )
		if self.param5 != "":
			params += ";" + self.param5.replace( "\r\n",'' )
												
		temp = params.split(";")	 # ��Ʒ����Ʒ֮��ֿ�
		temp= [ t.split(",") for t in temp ]	# ��Ʒ��Ϣ�ֿ�,��ʽ[[ itemID,amount,rate ],....]
		self.items = [ tuple( self.__toNum( t ) ) for t in temp ] # ��ת��Ϊ��ֵ�ľ�ת��
		self.param6 = eval( self.param6 )
		self.param7 = eval( self.param7 )
		 
	def __toNum( self, itemInfo ):
		"""
		����Ʒ�������͵���ת��Ϊ����
		"""
		itemInfo[1] = eval( itemInfo[1] )
		itemInfo[2] = eval( itemInfo[2] )
		return itemInfo
		
	def taskStatus( self, selfEntity, playerEntity ):
		"""
		�ж���Һ����ӵ�����״̬
		
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus�� state )
		state == True :  ��ʾ��������״̬�������������ӿ��Ա�ѡ��
		����: û��������״̬�����ܱ�ѡ��
		""" 
		# �����жϸ�entity�Ƿ�Ϊreal����������queryTemp()һ��Ĵ��뽫������ȷִ�С�
		if selfEntity.isReal() and selfEntity.queryTemp( "tongDBID", 0 ) == playerEntity.tong_dbID:
			QuestBox.taskStatus( self, selfEntity, playerEntity )
			return
				
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
		
	def gossipWith(self, selfEntity, playerEntity, dlgKey):
		"""
		@param playerEntity: ���ʵ��
		@type  playerEntity: entity
		"""
		if not selfEntity.isReal() or selfEntity.queryTemp( "tongDBID", 0 ) != playerEntity.tong_dbID:
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return
			
		QuestBox.gossipWith(self, selfEntity, playerEntity, dlgKey)
		
		
		
		