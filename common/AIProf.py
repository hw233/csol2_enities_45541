# -*- coding: gb18030 -*-
# AI 系统静态剖分模块 by mushuang
# 用途：
# 		根据系统配置文件信息找出AI系统的热点。
# 设计：
#		基于配置文件统计如下信息：
#			1）一条ai被多少的怪引用，设为n
#			2）引用这条ai的怪有多少个实例，设为m
#		对于每条ai，设权重p = m * n
#		将统计数据按权重排序，就可以找出AI系统的热点。
# 接口：
# AIProf：
#	printHotSpot( self, ranking = 10, descr = True, stream = sys.stdout )
#		打印已统计的热点信息到stream
#	saveTo( self, fileName, ranking = 10, descr = True )
#		将热点信息存入文件（通常，这个文件应该在“trunk\datas\”）
# 使用范例：
# >>> prof = AIProf()
# >>> prof.printHotSpot( 100, descr = False )

import BigWorld
import ResMgr
import sys

AICND_PATH = "entities/locale_default/config/server/ai/AICondition.xml"
AIACT_PATH = "entities/locale_default/config/server/ai/AIAction.xml"
AIDATA_PATH = "entities/locale_default/config/server/ai/AIData.xml"

class AIItem:
	def __init__( self ):
		
		
		self.ID = 0
		self.script = ""
		self.name = ""
		self.comment = ""
		
	def init( self, section ):
		self.ID = section["id"].asInt
		self.script = section["scriptName"].asString
		self.name = section["name"].asString
		self.comment = section["comment"].asString		
		return self
		
class AIRecord:
	def __init__( self ):
		self.ID = 0
		self.referCnt = 0
		self.comment = ""
		self.acts = [] 
		self.cnds = [] 
	
	def init( self, section ):
		self.ID = section["id"].asInt
		self.referCnt =section["referCount"].asInt
		self.comment = section["comment"].asString
		
		self.__loadAct( section )
		
		self.__loadCnd( section )
		
		return self
	
		
	def __loadAct( self, section ):
		for item in section["action"].values():
			self.acts.append( item["id"].asInt )
	
	def __loadCnd( self, section ):
		for item in section["condition"].values():
			self.cnds.append( item["id"].asInt )
	
ACTION = "action"
CONDITION = "condition"
class SortItem:
	def __init__( self ):
		self.ID = 0
		self.type = ""
	def init( self, ID, type ):
		self.ID = ID
		self.type = type
	def isAct( self ):
		global ACTION
		return self.type == ACTION
	
	def isCnd( self ):
		global CONDITION
		return self.type == CONDITION


class AIProf:
	def __init__( self ):
		self.cnd = {} # cndID:AIItem
		self.act = {} # actID:AIItem
		self.AIData = {} # aiID:AIRecord
		
		# 载入ai数据
		self.__loadData()
		
		self.cndRef = {} # cndID:refCount
		self.actRef = {} # actID:refCount
		# 计算对每个ai元素的引用数据
		self.__calcRef()
		
		# 生成已排序的结果
		self.result = [] # [ (referCount,SortItem) ]
		self.__mergeAndSort()

	
	def printHotSpot( self, ranking = 10, descr = True, stream = sys.stdout ):
		"""
		printHotSpot( self, ranking = 10, descr = True, stream = sys.stdout ):
		@输出热点信息到stream
		@ranking:热点信息的排名，用于指定输出多少热点信息,指定0输出全部信息
		@descr:指定输出信息中是否包含描述信息
		@stream:指定用来输出信息的流
		"""
		# 数据输出格式化信息
		sWithoutDescr = "\"%s:\t%d\"%(script,refCnt)"
		sWithDescr = "\"%s:\t%d\t\t%s\"%(script,refCnt,descr)"
		s = sWithDescr if descr else sWithoutDescr
		
		ranking = len( self.result ) if ranking == 0 else ranking
		
		# 表头
		hWithoutDescr = "Script:\t\t\tRefCount:"
		hWithDescr = "Script:\t\t\tRefCount:\tDescription:"
		spWithoutDescr = "------\t\t\t------"
		spWithDescr = "------\t\t\t------\t\t------"
		header = hWithDescr if descr else hWithoutDescr
		spliter = spWithDescr if descr else spWithoutDescr
		stream.write( header )
		stream.write( "\n" )
		stream.write( spliter )
		stream.write( "\n" )
		
		for i in xrange( ranking ):
			script = self.__getScript( self.result[i][1] )
			refCnt = self.result[i][0]
			descr = self.__getDescr( self.result[i][1] )
			stream.write( eval( s ) )
			stream.write("\n")
			
	def saveTo( self, fileName, ranking = 10, descr = True ):
		"""
		saveTo( self, fileName, ranking = 10, descr = True )
		@将热点信息存入文件
		@fileName:文件名
		@ranking:热点信息的排名，用于指定写入多少热点信息,指定0写入全部信息
		@descr:指定写入信息中是否包含描述信息
		"""
		fs = open( fileName, "w" )
		
		self.printHotSpot( ranking, descr, fs )
		
		fs.close()
		
	def __loadData( self ):
		# 将ai条件信息载入内存
		section = ResMgr.openSection( AICND_PATH )
		assert section != None
		
		for row in section.values():
			# AIITEM ( ID = 0, script = "", name = "", comment = "" ):
			t = AIItem()
			t.init( row )
			self.cnd[ t.ID ] = t
		
		ResMgr.purge( section )
		
		
		# 将ai行为信息载入内存
		section = ResMgr.openSection( AIACT_PATH )
		assert section != None
		
		for row in section.values():
			t = AIItem()
			t.init( row )
			self.act[ t.ID ] = t
			
		ResMgr.purge( section )
		
		
		# 将AI条目信息载入内存
		section = ResMgr.openSection( AIDATA_PATH )
		assert section != None
		
		for row in section.values():
			t = AIRecord()
			t.init( row )
			self.AIData[ t.ID ] = t
		
		ResMgr.purge( section )
	
	def __mergeAndSort( self ):
		"""
		act和cnd的引用数据归并，并统一排序
		"""
		for id,refCnt in self.actRef.items():
			t = SortItem()
			t.init( id, ACTION )
			self.result.append( ( refCnt, t ) )
		
		for id,refCnt in self.cndRef.items():
			t = SortItem()
			t.init( id, CONDITION )
			self.result.append( ( refCnt, t ) )
		
		self.result.sort( key = lambda x:x[0], reverse = True )
	
	def __calcRef( self ):
		"""
		计算AI条件/行为的引用数量
		"""
		for record in self.AIData.values():
			multi = record.referCnt
			
			# 计算cnd的引用数
			for cndID in record.cnds:
				if self.cndRef.has_key( cndID ):
					self.cndRef[ cndID ] += 1 * multi
				else :
					self.cndRef[ cndID ] = 1 * multi
			
			# 计算act的引用数
			for actID in record.acts:
				if self.actRef.has_key( actID ):
					self.actRef[ actID ] += 1 * multi
				else :
					self.actRef[ actID ] = 1 * multi
			
	def __getScript( self, sortItem ):
		dic = self.act if sortItem.type == ACTION else self.cnd
		try:
			return dic[ sortItem.ID ].script
		except:
			return ""
		
	def __getDescr( self, sortItem ):
		dic = self.act if sortItem.isAct() else self.cnd
		try:
			return dic[ sortItem.ID ].name
		except:
			return ""
