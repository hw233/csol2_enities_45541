# -*- coding: gb18030 -*-
from QuestBox import QuestBox

class QuestBoxFete( QuestBox ):
	
	def __init__( self ):
		QuestBox.__init__( self )
		
	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
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
												
		temp = params.split(";")	 # 物品和物品之间分开
		temp= [ t.split(",") for t in temp ]	# 物品信息分开,格式[[ itemID,amount,rate ],....]
		self.items = [ tuple( self.__toNum( t ) ) for t in temp ] # 该转化为数值的就转化
		self.param6 = eval( self.param6 )
		self.param7 = eval( self.param7 )
		 
	def __toNum( self, itemInfo ):
		"""
		把物品的数量和掉率转化为数字
		"""
		itemInfo[1] = eval( itemInfo[1] )
		itemInfo[2] = eval( itemInfo[2] )
		return itemInfo
		
	def taskStatus( self, selfEntity, playerEntity ):
		"""
		判断玩家和箱子的任务状态
		
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus（ state )
		state == True :  表示有这样的状态，告诉任务箱子可以被选中
		否则: 没有这样的状态，不能被选中
		""" 
		# 必须判断该entity是否为real，否则后面的queryTemp()一类的代码将不能正确执行。
		if selfEntity.isReal() and selfEntity.queryTemp( "tongDBID", 0 ) == playerEntity.tong_dbID:
			QuestBox.taskStatus( self, selfEntity, playerEntity )
			return
				
		playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
		
	def gossipWith(self, selfEntity, playerEntity, dlgKey):
		"""
		@param playerEntity: 玩家实体
		@type  playerEntity: entity
		"""
		if not selfEntity.isReal() or selfEntity.queryTemp( "tongDBID", 0 ) != playerEntity.tong_dbID:
			playerEntity.clientEntity( selfEntity.id ).onTaskStatus( 0 )
			return
			
		QuestBox.gossipWith(self, selfEntity, playerEntity, dlgKey)
		
		
		
		