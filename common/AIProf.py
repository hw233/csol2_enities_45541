# -*- coding: gb18030 -*-
# AI ϵͳ��̬�ʷ�ģ�� by mushuang
# ��;��
# 		����ϵͳ�����ļ���Ϣ�ҳ�AIϵͳ���ȵ㡣
# ��ƣ�
#		���������ļ�ͳ��������Ϣ��
#			1��һ��ai�����ٵĹ����ã���Ϊn
#			2����������ai�Ĺ��ж��ٸ�ʵ������Ϊm
#		����ÿ��ai����Ȩ��p = m * n
#		��ͳ�����ݰ�Ȩ�����򣬾Ϳ����ҳ�AIϵͳ���ȵ㡣
# �ӿڣ�
# AIProf��
#	printHotSpot( self, ranking = 10, descr = True, stream = sys.stdout )
#		��ӡ��ͳ�Ƶ��ȵ���Ϣ��stream
#	saveTo( self, fileName, ranking = 10, descr = True )
#		���ȵ���Ϣ�����ļ���ͨ��������ļ�Ӧ���ڡ�trunk\datas\����
# ʹ�÷�����
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
		
		# ����ai����
		self.__loadData()
		
		self.cndRef = {} # cndID:refCount
		self.actRef = {} # actID:refCount
		# �����ÿ��aiԪ�ص���������
		self.__calcRef()
		
		# ����������Ľ��
		self.result = [] # [ (referCount,SortItem) ]
		self.__mergeAndSort()

	
	def printHotSpot( self, ranking = 10, descr = True, stream = sys.stdout ):
		"""
		printHotSpot( self, ranking = 10, descr = True, stream = sys.stdout ):
		@����ȵ���Ϣ��stream
		@ranking:�ȵ���Ϣ������������ָ����������ȵ���Ϣ,ָ��0���ȫ����Ϣ
		@descr:ָ�������Ϣ���Ƿ����������Ϣ
		@stream:ָ�����������Ϣ����
		"""
		# ���������ʽ����Ϣ
		sWithoutDescr = "\"%s:\t%d\"%(script,refCnt)"
		sWithDescr = "\"%s:\t%d\t\t%s\"%(script,refCnt,descr)"
		s = sWithDescr if descr else sWithoutDescr
		
		ranking = len( self.result ) if ranking == 0 else ranking
		
		# ��ͷ
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
		@���ȵ���Ϣ�����ļ�
		@fileName:�ļ���
		@ranking:�ȵ���Ϣ������������ָ��д������ȵ���Ϣ,ָ��0д��ȫ����Ϣ
		@descr:ָ��д����Ϣ���Ƿ����������Ϣ
		"""
		fs = open( fileName, "w" )
		
		self.printHotSpot( ranking, descr, fs )
		
		fs.close()
		
	def __loadData( self ):
		# ��ai������Ϣ�����ڴ�
		section = ResMgr.openSection( AICND_PATH )
		assert section != None
		
		for row in section.values():
			# AIITEM ( ID = 0, script = "", name = "", comment = "" ):
			t = AIItem()
			t.init( row )
			self.cnd[ t.ID ] = t
		
		ResMgr.purge( section )
		
		
		# ��ai��Ϊ��Ϣ�����ڴ�
		section = ResMgr.openSection( AIACT_PATH )
		assert section != None
		
		for row in section.values():
			t = AIItem()
			t.init( row )
			self.act[ t.ID ] = t
			
		ResMgr.purge( section )
		
		
		# ��AI��Ŀ��Ϣ�����ڴ�
		section = ResMgr.openSection( AIDATA_PATH )
		assert section != None
		
		for row in section.values():
			t = AIRecord()
			t.init( row )
			self.AIData[ t.ID ] = t
		
		ResMgr.purge( section )
	
	def __mergeAndSort( self ):
		"""
		act��cnd���������ݹ鲢����ͳһ����
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
		����AI����/��Ϊ����������
		"""
		for record in self.AIData.values():
			multi = record.referCnt
			
			# ����cnd��������
			for cndID in record.cnds:
				if self.cndRef.has_key( cndID ):
					self.cndRef[ cndID ] += 1 * multi
				else :
					self.cndRef[ cndID ] = 1 * multi
			
			# ����act��������
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
