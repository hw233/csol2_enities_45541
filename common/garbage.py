# -*- coding: gb18030 -*-

"""
�����������ߣ����ڷ����ռ�������������֮�ص�������ϵ��

import gc
gc.set_debug( gc.DEBUG_LEAK )
gc.enable()
gc.collect()

import garbage
g = garbage.Garbage( "garbage.txt" )
g.collect()

def print_dict( d ):
  for k, v in d.items():
    if v is not None and type( v ) not in ( int, long, str, float, bool ):
      print k, "->", v, "->", type( v )
"""

#from bwdebug import *

import types
import gc
import weakref
import new
import sys

_types = [	'BufferType',		'ClassType',			'DictProxyType',		'DictType',				'DictionaryType',
			'EllipsisType',		'FrameType',			'FunctionType',			'GeneratorType',		'InstanceType',
			'LambdaType',		'ListType',				'MethodType',			'ModuleType',			'NotImplementedType',
			'ObjectType',		'SliceType',			'StringTypes',			'TracebackType',		'TupleType',
			'TypeType',			'UnicodeType',			'XRangeType',
		]

# bound method Ҳ���� types.UnboundMethodType ���ͣ����Բ��ܺ���
_types_ignore = (
			types.BooleanType,		types.BuiltinFunctionType,		types.BuiltinMethodType,
			types.CodeType,			types.ComplexType,				types.FileType,
			types.FloatType,		types.GetSetDescriptorType,		types.MemberDescriptorType,
			types.IntType,			types.LongType,					types.NoneType,
			types.StringType,		types.UnicodeType,
		)

_types_ignore_str = set( [ "<type 'wrapper_descriptor'>",	"<type 'method_descriptor'>",	"<type 'member_descriptor'>",

				"<type 'Math.Vector2'>", 				"<type 'Math.Vector3'>", 			"<type 'Math.Vector4'>",
				"<type 'Math.Matrix'>",					"<type 'Math.MatrixProduct'>",		"<type 'Math.Vector4Animation'>",
				"<type 'Math.Vector4Combiner'>",		"<type 'Math.Vector4LFO'>",			"<type 'Math.Vector4MatrixAdaptor'>",
				"<type 'Math.Vector4Product'>",			"<type 'Math.Vector4Shader'>",		"<type 'Math.Vector4Swizzle'>",
				"<type 'Math.Vector4TimeManipulator'>",	"<type 'BaseEntityMailBox'>", 		"<type 'CellEntityMailBox'>",
			] )

# id( type ) : type name
_original_type_mapping = dict( [ ( id( getattr( types, k ) ), k ) for k in _types ] )
_original_type_mapping["weakref"]					= weakref.ref



class GBProcess:
	def __init__( self, pyobj ):
		self.key = None		# ���ڱ�ʶ����Ψһ�������ơ�������еĻ���
		self.pyobj_ = pyobj
		self.links = set()		# �������Ͱ�������������
		self.parents = set()	# ��¼ָ���Լ��Ķ�������ɾ������ʱ�ܿ��ٵĸ���parent��ָ���б�

	@classmethod
	def newNode( SELF, pyobj ):
		"""
		"""
		if isinstance( pyobj, _types_ignore ):
			return None

		tc = None
		tid = id( type( pyobj ) )
		if tid in _original_type_mapping:
			tc = _type_mapping[_original_type_mapping[tid]]
		else:
			tstr = str( type( pyobj ) )
			if tstr in _type_mapping:
				tc = _type_mapping[tstr]
			elif hasattr( pyobj, "__class__" ):
				if hasattr( pyobj, "__dict__" ):
					tc = _type_mapping["instance"]
				elif hasattr( pyobj, "__slots__" ):
					tc = _type_mapping["instance_slots"]

		if tc is None:
			if tstr not in _types_ignore_str:
				print "unknow py object.", hex( id( pyobj ) ), type( pyobj ), "->", pyobj
			else:
				return None
		else:
			return tc( pyobj )

	def uid( self ):
		"""
		virtual method.
		��ȡuid
		"""
		return id( self.pyobj_ )

	def release( self ):
		self.onRelease()
		self.links.clear()
		self.parents.clear()
		self.pyobj_ = None

	def onRelease( self ):
		"""
		template method.
		"""
		pass

	def objRefCount( self ):
		"""
		�������õ�pyobj�����ü���
		"""
		# ��2��ԭ����self.pyobj_������һ�Σ��ڵ���sys.getrefcount()ʱ������������һ��
		return sys.getrefcount( self.pyobj_ ) - 2

	def generateSubNodes( self ):
		"""
		virtual method.
		������ǰ�������õ�ʵ����������
		@return: �������б�
		"""
		return []

	def getName( self ):
		"""
		ȡ��pyobj����ʵ����

		@return: string
		"""
		return "error"

class GBProcessGeneral( GBProcess ):
	"""
	���õ����ʹ���
	"""
	def generateSubNodes( self ):
		"""
		virtual method.
		������ǰ�������õ�ʵ����������
		@return: �������б�
		"""
		s = [ self.newNode( pyobj ) for pyobj in self.getLinks() ]
		return [ e for e in s if e is not None and e.uid() != 0 ]

	def getLinks( self ):
		"""
		template method.
		�ռ��������������

		@return: �����б�
		"""
		return []

	def getName( self ):
		"""
		ȡ��pyobj����ʵ����

		@return: string
		"""
		return "ref %i; %s<0x%x> %s -> %s" % ( self.objRefCount(), self.pyobj_.__class__.__name__, self.uid(), self.key, str( self.pyobj_ ) )

class GBProcessFunction( GBProcessGeneral ):
	def getLinks( self ):
		"""
		�ռ��������������

		@return: �����б�
		"""
		if self.pyobj_.func_closure is None:
			return []
		return [ self.pyobj_.func_closure, ]

	def getName( self ):
		"""
		ȡ��pyobj����ʵ����

		@return: string
		"""
		return "ref %i; function<0x%x>: %s -> %s, %s, func_closure: %s, func_code: %s" % ( self.objRefCount(), self.uid(), self.key, self.pyobj_.__name__, str( self.pyobj_ ), str( self.pyobj_.func_closure ), str( self.pyobj_.func_code ) )

class GBProcessArray( GBProcessGeneral ):
	def getLinks( self ):
		"""
		�ռ��������������

		@return: �����б�
		"""
		return list( self.pyobj_ )

	def getName( self ):
		"""
		ȡ��pyobj����ʵ����

		@return: string
		"""
		return "ref %i; array<0x%x>: %s -> %s; value %s" % ( self.objRefCount(), self.uid(), self.key, self.pyobj_.__class__.__name__, str( self.pyobj_ ) )

class GBProcessDict( GBProcess ):
	def generateSubNodes( self ):
		"""
		������ǰ�������õ�ʵ����������
		@return: �������б�
		"""
		s = []
		for k, v in self.pyobj_.items():
			n = self.newNode( v )
			if n is None or n.uid() == 0:
				continue
			n.key = k
			s.append( n )

		return s

	def getLinks( self ):
		"""
		�ռ��������������

		@return: �����б�
		"""
		assert False

	def getName( self ):
		"""
		ȡ��pyobj����ʵ����

		@return: string
		"""
		return "ref %i; dict<0x%x>: %s -> %s" % ( self.objRefCount(), self.uid(), self.key, self.pyobj_.__class__.__name__ )

class GBProcessMethod( GBProcessGeneral ):
	def getLinks( self ):
		"""
		�ռ��������������

		@return: �����б�
		"""
		return [ self.pyobj_.im_self, ]

	def getName( self ):
		"""
		ȡ��pyobj����ʵ����

		@return: string
		"""
		return "ref %i; method<0x%x>: %s -> %s; class %s, func %s, self %s" % ( self.objRefCount(), self.uid(), self.key, str( self.pyobj_ ), str( self.pyobj_.im_class ), str( self.pyobj_.im_func ), str( self.pyobj_.im_self ) )

class GBProcessInstance( GBProcessGeneral ):
	def generateSubNodes( self ):
		"""
		������ǰ�������õ�ʵ����������
		@return: �������б�
		"""
		node = self.newNode( self.pyobj_.__dict__ )
		if node is None:
			return []
		node.key = self.pyobj_.__class__.__name__
		return [ node, ]

	def getLinks( self ):
		"""
		�ռ��������������

		@return: �����б�
		"""
		assert False

	def getName( self ):
		"""
		ȡ��pyobj����ʵ����

		@return: string
		"""
		return "ref %i; class<0x%x>: %s -> %s.%s" % ( self.objRefCount(), self.uid(), self.key, self.pyobj_.__module__, self.pyobj_.__class__.__name__ )

class GBProcessInstance_slots( GBProcess ):
	"""
	һ���������� __slots__ ����ʵ�������⴦��
	��������ͨ��ʵ����������һ��__dict__��֮��Ӧ��
	��������ֻ��ͨ��obj.__slots__����ȡ��
	�����Ҫֱ�Ӱ���������ȡ������
	"""
	def __init__( self, pyobj ):
		GBProcess.__init__( self, pyobj )

		self.objDict = {}
		for e in pyobj.__slots__:
			if hasattr( pyobj, e ):
				self.objDict[e] = getattr( pyobj, e )
			else:
				print "AttributeError: object ", pyobj, "has no attribute", e
		#self.objDict = dict( [ ( e, getattr( pyobj, e ) ) for e in pyobj.__slots__ if hasattr( pyobj, e ) ] )

	def generateSubNodes( self ):
		"""
		������ǰ�������õ�ʵ����������
		@return: �������б�
		"""
		s = []
		for key, val in self.objDict.iteritems():
			node = self.newNode( val )
			if node is not None:
				node.key = key
				s.append( node )

		return s

	def getName( self ):
		"""
		ȡ��pyobj����ʵ����

		@return: string
		"""
		return "ref %i; class_slots<0x%x>: %s -> %s.%s" % ( self.objRefCount(), self.uid(), self.key, self.pyobj_.__module__, self.pyobj_.__class__.__name__ )


class GBProcessCell( GBProcessGeneral ):
	def getLinks( self ):
		"""
		�ռ��������������

		@return: �����б�
		"""
		return [ self.pyobj_.cell_contents, ]

	def getName( self ):
		"""
		ȡ��pyobj����ʵ����

		@return: string
		"""
		return "ref %i; cell<0x%x>: %s -> %s" % ( self.objRefCount(), self.uid(), self.key, repr( self.pyobj_.cell_contents ) )

class GBProcessWeakref( GBProcess ):
	"""
	�п�����������Ķ����ڻ������ã��������治һ���ܲ���
	��ˣ���Ҫ�����õ�pyobjȡ��������ȡ��pyobj��һ�㼶������
	"""
	def __init__( self, pyobj ):
		GBProcess.__init__( self, pyobj )
		self._realObj = pyobj()

	def uid( self ):
		"""
		virtual method.
		��ȡuid
		"""
		return id( self._realObj )

	def onRelease( self ):
		"""
		template method.
		"""
		self._realObj = None

	def generateSubNodes( self ):
		"""
		������ǰ�������õ�ʵ����������
		@return: �������б�
		"""
		realNode = None
		if self._realObj is not None:
			realNode = self.newNode( self._realObj )

		if realNode is None:
			return []

		s = realNode.generateSubNodes()
		#s.append( realNode )	����uid()ʹ�õ���real pyobj�ĵ�ַ��������ﲻ��Ҫ�ټӽ�ȥ��
		return s

	def getName( self ):
		"""
		ȡ��pyobj����ʵ����

		@return: string
		"""
		return "ref %i; Weakref<0x%x>: %s -> %s; ref %i; realObj %s" % ( self.objRefCount(), self.uid(), self.key, str( self.pyobj_ ), sys.getrefcount( self.pyobj_() ), str( self.pyobj_() ) )

class GBProcessWeakproxy( GBProcess ):
	"""
	�п�����������Ķ����ڻ������ã��������治һ���ܲ���
	��ˣ���Ҫ�����õ�pyobjȡ��������ȡ��pyobj��һ�㼶������
	���ǣ���ǰ�Ҳ�֪����ôȡproxyָ���ʵ����������������ʱ����ʵ�֡�
	"""
	def __init__( self, pyobj ):
		GBProcess.__init__( self, pyobj )
		assert False

	def generateSubNodes( self ):
		"""
		������ǰ�������õ�ʵ����������
		@return: �������б�
		"""
		s = []
		# ��ǰ�Ҳ�֪����ôȡproxyָ���ʵ����������������ʱ����ʵ�֡�
		return s

	def getName( self ):
		"""
		ȡ��pyobj����ʵ����

		@return: string
		"""
		return "ref %i; Weakproxy<0x%x>: %s -> %s" % ( self.objRefCount(), self.uid(), self.key, str( self.pyobj ) )

class GBProcessTypeType( GBProcessGeneral ):
	"""
	���ͣ���ʵ����ԭʼ��ȵȡ�
	������֤����ֱ�ӷ���self.pyobj_.__dict__�����ܼ��� classobj ���͵Ľ�������
	������Ҫ�� __dict__ ����������ռ�����
	"""
	def generateSubNodes( self ):
		"""
		������ǰ�������õ�ʵ����������
		@return: �������б�
		"""
		s = []
		objDict = dict( [ ( e, getattr( self.pyobj_, e ) ) for e in dir( self.pyobj_ ) ] )
		for key, val in objDict.iteritems():
			node = self.newNode( val )
			if node is not None:
				node.key = key
				s.append( node )

		return s

	def getName( self ):
		"""
		ȡ��pyobj����ʵ����

		@return: string
		"""
		return "ref %i; classobj<0x%x>: %s -> %s" % ( self.objRefCount(), self.uid(), self.key, str( self.pyobj_ ) )

class GBProcessBWGUI( GBProcessGeneral ):
	def generateSubNodes( self ):
		"""
		������ǰ�������õ�ʵ����������
		@return: �������б�
		"""
		node = self.newNode( self.pyobj_.script )
		if node is None:
			return []
		node.key = "%s.script" % self.pyobj_.__class__.__name__
		return [ node, ]

	def getLinks( self ):
		"""
		�ռ��������������

		@return: �����б�
		"""
		assert False

	def getName( self ):
		"""
		ȡ��pyobj����ʵ����

		@return: string
		"""
		return "ref %i; BW.GUI.window<0x%x>: %s -> %s, script %s" % ( self.objRefCount(), self.uid(), self.key, str( self.pyobj_ ), repr( self.pyobj_.script ) )

class GBProcessUnknowType( GBProcess ):
	"""
	δ֪����
	"""
	def uid( self ):
		"""
		virtual method.
		��ȡuid
		"""
		return 0

	def __init__( self, pyobj ):
		GBProcess.__init__( self, pyobj )
		i = id( type( pyobj ) )
		if i in _original_type_mapping:
			print "unknow type:", _original_type_mapping[i], id( pyobj ), type( pyobj ), "->", pyobj
		else:
			print "unknow type:", id( pyobj ), type( pyobj ), i, "->", pyobj






_type_mapping = {
		'BufferType'							: GBProcessUnknowType,
		'ClassType'								: GBProcessTypeType,
		'DictProxyType'							: GBProcessDict,
		'DictType'								: GBProcessDict,
		'DictionaryType'						: GBProcessDict,
		'EllipsisType'							: GBProcessUnknowType,
		'FrameType'								: GBProcessUnknowType,
		'FunctionType'							: GBProcessFunction,
		'GeneratorType'							: GBProcessUnknowType,
		'InstanceType'							: GBProcessInstance,
		'LambdaType'							: GBProcessFunction,
		'ListType'								: GBProcessArray,
		'MethodType'							: GBProcessMethod,
		'ModuleType'							: GBProcessUnknowType,
		'NotImplementedType'					: GBProcessUnknowType,
		'ObjectType'							: GBProcessUnknowType,
		'SliceType'								: GBProcessUnknowType,
		'StringTypes'							: GBProcessUnknowType,
		'TracebackType'							: GBProcessUnknowType,
		'TupleType'								: GBProcessArray,
		'TypeType'								: GBProcessTypeType,
		'UnicodeType'							: GBProcessUnknowType,
		'XRangeType'							: GBProcessUnknowType,
		"weakref"								: GBProcessWeakref,
		# һЩ����ֱ�������Ͷ�λ����������
		"<type 'weakref'>"						: GBProcessWeakref,		# ������͵ĵ�ַ��Ȼ��weakref.ref�Ĳ�һ������֪������ôŪ����
		"instance"								: GBProcessInstance,
		"instance_slots"						: GBProcessInstance_slots,
		# bigworld����
		"<type 'PyArrayDataInstance'>"			: GBProcessArray,
		"<type 'PyFixedDictDataInstance'>"		: GBProcessDict,
		"<type 'PyCellData'>"					: GBProcessDict,
		"<type 'GUI.Window'>"					: GBProcessBWGUI,
		"<type 'GUI.Text'>"						: GBProcessBWGUI,
		"<type 'GUI.TextureFrame'>"				: GBProcessBWGUI,
		"<type 'cell'>"							: GBProcessCell,
	}



class Garbage:
	def __init__( self, outputFile ):
		self._outputFile = outputFile

		# key == GBProcess.uid(), value == instance of GBProcess
		self._instanceDict = {}

	def addInstance( self, instance ):
		self._instanceDict[id( instance )] = instance	# instance of class

	def collect( self, garbageList = None, recursiveTimes = 0 ):
		"""
		�ռ�������gc.garbage���Ԫ�أ������ɽ����������ݡ�
		@param recursive: �ݹ�������������������������¶�����Ҫʹ�á�
		@param recursive: int
		"""
		self._instanceDict.clear()

		# ���ȣ���gc.garbage�ռ����е�δ�ͷ�Ԫ��
		if garbageList is None:
			garbageList = gc.garbage
			
		for g in garbageList:
			node = GBProcess.newNode( g )
			if node and node.uid() != 0:
				self._instanceDict[node.uid()] = node
				#print "Node:", node.uid(), node.__class__.__name__, "-->", node.getName()

		# Ȼ�󣬴������ռ���gc.garbage��Ԫ�����ռ���Ԫ��
		print "info: collectting garbage..."
		allNodes = self._instanceDict.values()
		searchTime = 0
		while len( allNodes ):
			validNodes = []
			for node in allNodes:	# Ϊ�˱����м����ı�״̬������ʹ��itervalues()
				nodes = node.generateSubNodes()
				#print "subNodes:", nodes, "parentNode ->", node.getName()
				for subNode in nodes:
					#print "subNode:", subNode.uid(), subNode.__class__.__name__, "-->", subNode.getName()
					if subNode.uid() == 0:
						continue
					if subNode.uid() not in self._instanceDict:
						self._instanceDict[subNode.uid()] = subNode
						validNodes.append( subNode )
						#print "subNode:", subNode.uid(), subNode.__class__.__name__, "-->", subNode.getName()

					existedSubNode = self._instanceDict[subNode.uid()]
					node.links.add( subNode.uid() )					# ���뵽���ӱ���
					existedSubNode.parents.add( node.uid() )		# ���뵽�����б���
					# ����Ѵ��ڵ�node��û����Ч��key�������
					if subNode.key and not existedSubNode.key:
						existedSubNode.key = subNode.key
					# �������쳣�����ˣ����ʾ������bug
					assert subNode.uid() != node.uid(), "%s" % subNode.uid()

			# ����Ƿ�Ҫ�ݹ�����
			if recursiveTimes > 0:
				if searchTime >= recursiveTimes:
					break
				searchTime += 1
				allNodes = validNodes
				print "recursive ... %s" % len( allNodes )
			else:
				allNodes = []

		# ���ţ��������û���²㣨���棩���õ�Ԫ��
		print "info: processing depend..."
		self.calculateDepend()

		# ��󣬰��н������õ�����д����־��
		self.writeLog( self.makeNodeUIDTracks )

	def writeLog( self, collectStrategy ):
		"""
		@param collectStrategy: һ����������uid�켣�Ĳ��ԣ���ǰ���õ�ΪmakeNodeUIDTracks()��makeNodeUIDTracksEx����
		"""
		f = open( self._outputFile, "wt" )

		print "info: making log... %s" % len( self._instanceDict )
		for key in self._instanceDict.iterkeys():
			print "info: making uids track... %s" % key
			tracks = []
			collectStrategy( key, tracks, [] )
			for track in tracks:
				print track
				log = self.generateLogByUIDs( track )
				f.write( log )
		f.close()

	def makeNodeUIDTracks( self, uid, tracksOut, trackTmp ):
		"""
		������uid���Ӧ��ʵ�������ӽڵ��������־
		ע��Ϊ��Ч�ʵĿ��ǣ��˺���ֻ���ص�1�����ӵ���־��
		    ����뷵�����е���־����ʹ��makeNodeUIDTracksEx()��
		@param tracksOut: ���; like as [ [uid1, uid2, ...], ... ]
		@param trackTmp: һ��������ת����ʱlistʵ������ʹ��Ĭ��ֵ��[]����
		                 ԭ���ǲ����е�trackTmp = []��Զ��ֻʹ��ͬһ��ʵ����
		                 ����������ʹ�б���ڶ��������
		"""
		uids = set( [uid,] )
		trackTmp.append( uid )
		node = self._instanceDict[uid]
		while 1:
			assert len( node.links ) > 0
			node = self._instanceDict[list( node.links )[0]]	# ֻȡ��0�����ӵ�node������ĺ���
			if node.uid() in uids:
				break
			uids.add( node.uid() )
			trackTmp.append( node.uid() )
		trackTmp.append( node.uid() )
		tracksOut.append( trackTmp )

	def makeNodeUIDTracksEx( self, uid, tracksOut, trackTmp ):
		"""
		��makeNodeUIDTracks()����ϸ���������еĹ켣������Ҫ������ʱ�䡣
		@param tracksOut: ���; like as [ [uid1, uid2, ...], ... ]
		@param trackTmp: һ��������ת����ʱlistʵ������ʹ��Ĭ��ֵ��[]����
		                 ԭ���ǲ����е�trackTmp = []��Զ��ֻʹ��ͬһ��ʵ����
		                 ����������ʹ�б���ڶ��������
		"""
		if uid in trackTmp:
			t = list( trackTmp )
			t.append( uid )
			tracksOut.append( t )
			return
		
		trackTmp.append( uid )		# ���Լ����뵽�켣����
		for e in self._instanceDict[uid].links:
			self.makeNodeUIDTracksEx( e, tracksOut, trackTmp )
		trackTmp.pop()				# ��������ɣ����Լ��ӹ켣�����Ƴ�


	def generateLogByUIDs( self, uids ):
		"""
		@param uids: list of uid
		"""
		logs = []
		for uid in uids:
			node = self._instanceDict[uid]
			logs.append( node.getName() )
			logs.append( "\n\t-->\t" )
		logs.pop()	# ȥ�����һ��"\n\t-->\t"
		logs.append( "\n\n" )
		
		return "".join( logs )

	def calculateDepend( self ):
		"""
		���������ϵ���Ѳ���Ҫ�Ĵ����
		"""
		count = 1
		while count != 0:	# һֱѭ����ֱ�������в���ؽڵ㶼����ɾ�
			count = 0
			for key in self._instanceDict.keys():	# ������iterkeys()����Ϊ������ִ��ɾ������
				#if key not in self._instanceDict:
				#	continue	# ����ǿ��ܵģ���Ϊ������ִ��һЩ����ɾ������
				node = self._instanceDict[key]
				if len( node.links ) == 0:						# û���²�����
					self._instanceDict.pop( key )				# �Ϳ��԰������б���ȥ��
					count += 1
					for k in node.parents:
						pnode = self._instanceDict[k]
						pnode.links.remove( node.uid() )		# ��֪ͨ�������ĸ��ڵ�
					node.release()
				"""�����Ҳ��᲻��������Ĳ���
				elif len( node.parents ) == 0:					# ���û���ϲ�����
					print "remove parents", node.pyobj_
					self._instanceDict.pop( key )				# �Ϳ��԰������б���ȥ������������ʹ���ɵ����Ӹ���̣������ܻ����λ��������鷳
					count += 1
					for k in node.links:
						pnode = self._instanceDict[k]
						pnode.parents.remove( node.uid() )		# ��֪ͨ���������ӽڵ�
					node.release()
				"""

# garbage.py
