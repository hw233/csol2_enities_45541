# -*- coding: gb18030 -*-

"""
垃圾分析工具，用于分析收集到的垃圾数据之关的依赖关系。

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

# bound method 也属于 types.UnboundMethodType 类型，所以不能忽略
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
		self.key = None		# 用于标识它的唯一属性名称——如果有的话。
		self.pyobj_ = pyobj
		self.links = set()		# 自身类型包函的其它类型
		self.parents = set()	# 记录指向自己的对象，用于删除自身时能快速的更新parent的指向列表

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
		获取uid
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
		返回引用的pyobj的引用计数
		"""
		# 减2的原因是self.pyobj_引用了一次，在调用sys.getrefcount()时参数又引用了一次
		return sys.getrefcount( self.pyobj_ ) - 2

	def generateSubNodes( self ):
		"""
		virtual method.
		创建当前类型引用的实例的子类型
		@return: 子类型列表
		"""
		return []

	def getName( self ):
		"""
		取得pyobj的真实名称

		@return: string
		"""
		return "error"

class GBProcessGeneral( GBProcess ):
	"""
	常用的类型处理
	"""
	def generateSubNodes( self ):
		"""
		virtual method.
		创建当前类型引用的实例的子类型
		@return: 子类型列表
		"""
		s = [ self.newNode( pyobj ) for pyobj in self.getLinks() ]
		return [ e for e in s if e is not None and e.uid() != 0 ]

	def getLinks( self ):
		"""
		template method.
		收集自身关联的类型

		@return: 类型列表
		"""
		return []

	def getName( self ):
		"""
		取得pyobj的真实名称

		@return: string
		"""
		return "ref %i; %s<0x%x> %s -> %s" % ( self.objRefCount(), self.pyobj_.__class__.__name__, self.uid(), self.key, str( self.pyobj_ ) )

class GBProcessFunction( GBProcessGeneral ):
	def getLinks( self ):
		"""
		收集自身关联的类型

		@return: 类型列表
		"""
		if self.pyobj_.func_closure is None:
			return []
		return [ self.pyobj_.func_closure, ]

	def getName( self ):
		"""
		取得pyobj的真实名称

		@return: string
		"""
		return "ref %i; function<0x%x>: %s -> %s, %s, func_closure: %s, func_code: %s" % ( self.objRefCount(), self.uid(), self.key, self.pyobj_.__name__, str( self.pyobj_ ), str( self.pyobj_.func_closure ), str( self.pyobj_.func_code ) )

class GBProcessArray( GBProcessGeneral ):
	def getLinks( self ):
		"""
		收集自身关联的类型

		@return: 类型列表
		"""
		return list( self.pyobj_ )

	def getName( self ):
		"""
		取得pyobj的真实名称

		@return: string
		"""
		return "ref %i; array<0x%x>: %s -> %s; value %s" % ( self.objRefCount(), self.uid(), self.key, self.pyobj_.__class__.__name__, str( self.pyobj_ ) )

class GBProcessDict( GBProcess ):
	def generateSubNodes( self ):
		"""
		创建当前类型引用的实例的子类型
		@return: 子类型列表
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
		收集自身关联的类型

		@return: 类型列表
		"""
		assert False

	def getName( self ):
		"""
		取得pyobj的真实名称

		@return: string
		"""
		return "ref %i; dict<0x%x>: %s -> %s" % ( self.objRefCount(), self.uid(), self.key, self.pyobj_.__class__.__name__ )

class GBProcessMethod( GBProcessGeneral ):
	def getLinks( self ):
		"""
		收集自身关联的类型

		@return: 类型列表
		"""
		return [ self.pyobj_.im_self, ]

	def getName( self ):
		"""
		取得pyobj的真实名称

		@return: string
		"""
		return "ref %i; method<0x%x>: %s -> %s; class %s, func %s, self %s" % ( self.objRefCount(), self.uid(), self.key, str( self.pyobj_ ), str( self.pyobj_.im_class ), str( self.pyobj_.im_func ), str( self.pyobj_.im_self ) )

class GBProcessInstance( GBProcessGeneral ):
	def generateSubNodes( self ):
		"""
		创建当前类型引用的实例的子类型
		@return: 子类型列表
		"""
		node = self.newNode( self.pyobj_.__dict__ )
		if node is None:
			return []
		node.key = self.pyobj_.__class__.__name__
		return [ node, ]

	def getLinks( self ):
		"""
		收集自身关联的类型

		@return: 类型列表
		"""
		assert False

	def getName( self ):
		"""
		取得pyobj的真实名称

		@return: string
		"""
		return "ref %i; class<0x%x>: %s -> %s.%s" % ( self.objRefCount(), self.uid(), self.key, self.pyobj_.__module__, self.pyobj_.__class__.__name__ )

class GBProcessInstance_slots( GBProcess ):
	"""
	一个被定义了 __slots__ 的类实例的特殊处理。
	它不像普通的实例那样会有一个__dict__与之对应，
	它的属性只能通过obj.__slots__来获取，
	因此需要直接把所有属性取出来。
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
		创建当前类型引用的实例的子类型
		@return: 子类型列表
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
		取得pyobj的真实名称

		@return: string
		"""
		return "ref %i; class_slots<0x%x>: %s -> %s.%s" % ( self.objRefCount(), self.uid(), self.key, self.pyobj_.__module__, self.pyobj_.__class__.__name__ )


class GBProcessCell( GBProcessGeneral ):
	def getLinks( self ):
		"""
		收集自身关联的类型

		@return: 类型列表
		"""
		return [ self.pyobj_.cell_contents, ]

	def getName( self ):
		"""
		取得pyobj的真实名称

		@return: string
		"""
		return "ref %i; cell<0x%x>: %s -> %s" % ( self.objRefCount(), self.uid(), self.key, repr( self.pyobj_.cell_contents ) )

class GBProcessWeakref( GBProcess ):
	"""
	有可能引用里面的对像在互相引用，但在外面不一定能捕获。
	因此，需要把引用的pyobj取出来，并取该pyobj下一层级的数据
	"""
	def __init__( self, pyobj ):
		GBProcess.__init__( self, pyobj )
		self._realObj = pyobj()

	def uid( self ):
		"""
		virtual method.
		获取uid
		"""
		return id( self._realObj )

	def onRelease( self ):
		"""
		template method.
		"""
		self._realObj = None

	def generateSubNodes( self ):
		"""
		创建当前类型引用的实例的子类型
		@return: 子类型列表
		"""
		realNode = None
		if self._realObj is not None:
			realNode = self.newNode( self._realObj )

		if realNode is None:
			return []

		s = realNode.generateSubNodes()
		#s.append( realNode )	由于uid()使用的是real pyobj的地址，因此这里不需要再加进去。
		return s

	def getName( self ):
		"""
		取得pyobj的真实名称

		@return: string
		"""
		return "ref %i; Weakref<0x%x>: %s -> %s; ref %i; realObj %s" % ( self.objRefCount(), self.uid(), self.key, str( self.pyobj_ ), sys.getrefcount( self.pyobj_() ), str( self.pyobj_() ) )

class GBProcessWeakproxy( GBProcess ):
	"""
	有可能引用里面的对像在互相引用，但在外面不一定能捕获。
	因此，需要把引用的pyobj取出来，并取该pyobj下一层级的数据
	但是，当前我不知道怎么取proxy指向的实例，因此这个处理暂时不能实现。
	"""
	def __init__( self, pyobj ):
		GBProcess.__init__( self, pyobj )
		assert False

	def generateSubNodes( self ):
		"""
		创建当前类型引用的实例的子类型
		@return: 子类型列表
		"""
		s = []
		# 当前我不知道怎么取proxy指向的实例，因此这个处理暂时不能实现。
		return s

	def getName( self ):
		"""
		取得pyobj的真实名称

		@return: string
		"""
		return "ref %i; Weakproxy<0x%x>: %s -> %s" % ( self.objRefCount(), self.uid(), self.key, str( self.pyobj ) )

class GBProcessTypeType( GBProcessGeneral ):
	"""
	类型，如实例的原始类等等。
	经测试证明，直接返回self.pyobj_.__dict__并不能检查出 classobj 类型的交叉引用
	所以需要把 __dict__ 里面的数据收集过来
	"""
	def generateSubNodes( self ):
		"""
		创建当前类型引用的实例的子类型
		@return: 子类型列表
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
		取得pyobj的真实名称

		@return: string
		"""
		return "ref %i; classobj<0x%x>: %s -> %s" % ( self.objRefCount(), self.uid(), self.key, str( self.pyobj_ ) )

class GBProcessBWGUI( GBProcessGeneral ):
	def generateSubNodes( self ):
		"""
		创建当前类型引用的实例的子类型
		@return: 子类型列表
		"""
		node = self.newNode( self.pyobj_.script )
		if node is None:
			return []
		node.key = "%s.script" % self.pyobj_.__class__.__name__
		return [ node, ]

	def getLinks( self ):
		"""
		收集自身关联的类型

		@return: 类型列表
		"""
		assert False

	def getName( self ):
		"""
		取得pyobj的真实名称

		@return: string
		"""
		return "ref %i; BW.GUI.window<0x%x>: %s -> %s, script %s" % ( self.objRefCount(), self.uid(), self.key, str( self.pyobj_ ), repr( self.pyobj_.script ) )

class GBProcessUnknowType( GBProcess ):
	"""
	未知类型
	"""
	def uid( self ):
		"""
		virtual method.
		获取uid
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
		# 一些不好直接用类型定位的类型特例
		"<type 'weakref'>"						: GBProcessWeakref,		# 这个类型的地址竟然与weakref.ref的不一样，不知道是怎么弄来的
		"instance"								: GBProcessInstance,
		"instance_slots"						: GBProcessInstance_slots,
		# bigworld特有
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
		收集、过滤gc.garbage里的元素，并生成交叉引用数据。
		@param recursive: 递归搜索次数，极慢，正常情况下都不需要使用。
		@param recursive: int
		"""
		self._instanceDict.clear()

		# 首先，从gc.garbage收集所有的未释放元素
		if garbageList is None:
			garbageList = gc.garbage
			
		for g in garbageList:
			node = GBProcess.newNode( g )
			if node and node.uid() != 0:
				self._instanceDict[node.uid()] = node
				#print "Node:", node.uid(), node.__class__.__name__, "-->", node.getName()

		# 然后，从所有收集自gc.garbage的元素中收集子元素
		print "info: collectting garbage..."
		allNodes = self._instanceDict.values()
		searchTime = 0
		while len( allNodes ):
			validNodes = []
			for node in allNodes:	# 为了避免中间插入改变状态，不能使用itervalues()
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
					node.links.add( subNode.uid() )					# 加入到链接表中
					existedSubNode.parents.add( node.uid() )		# 加入到父类列表中
					# 如果已存在的node中没有有效的key，则更新
					if subNode.key and not existedSubNode.key:
						existedSubNode.key = subNode.key
					# 如果这个异常出现了，则表示代码有bug
					assert subNode.uid() != node.uid(), "%s" % subNode.uid()

			# 检查是否要递归搜索
			if recursiveTimes > 0:
				if searchTime >= recursiveTimes:
					break
				searchTime += 1
				allNodes = validNodes
				print "recursive ... %s" % len( allNodes )
			else:
				allNodes = []

		# 接着，清除所有没有下层（交叉）引用的元素
		print "info: processing depend..."
		self.calculateDepend()

		# 最后，把有交叉引用的数据写到日志中
		self.writeLog( self.makeNodeUIDTracks )

	def writeLog( self, collectStrategy ):
		"""
		@param collectStrategy: 一个用于生成uid轨迹的策略，当前可用的为makeNodeUIDTracks()和makeNodeUIDTracksEx（）
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
		产生与uid相对应的实例及其子节点关联的日志
		注：为了效率的考虑，此函数只返回第1个链接的日志，
		    如果想返回所有的日志，请使用makeNodeUIDTracksEx()。
		@param tracksOut: 结果; like as [ [uid1, uid2, ...], ... ]
		@param trackTmp: 一个用于中转的临时list实例，不使用默认值“[]”，
		                 原因是参数中的trackTmp = []永远都只使用同一个实例，
		                 这样容易误使列表存在多余的内容
		"""
		uids = set( [uid,] )
		trackTmp.append( uid )
		node = self._instanceDict[uid]
		while 1:
			assert len( node.links ) > 0
			node = self._instanceDict[list( node.links )[0]]	# 只取第0个链接的node，其余的忽略
			if node.uid() in uids:
				break
			uids.add( node.uid() )
			trackTmp.append( node.uid() )
		trackTmp.append( node.uid() )
		tracksOut.append( trackTmp )

	def makeNodeUIDTracksEx( self, uid, tracksOut, trackTmp ):
		"""
		比makeNodeUIDTracks()更详细的搜索所有的轨迹，但需要更长的时间。
		@param tracksOut: 结果; like as [ [uid1, uid2, ...], ... ]
		@param trackTmp: 一个用于中转的临时list实例，不使用默认值“[]”，
		                 原因是参数中的trackTmp = []永远都只使用同一个实例，
		                 这样容易误使列表存在多余的内容
		"""
		if uid in trackTmp:
			t = list( trackTmp )
			t.append( uid )
			tracksOut.append( t )
			return
		
		trackTmp.append( uid )		# 把自己加入到轨迹表中
		for e in self._instanceDict[uid].links:
			self.makeNodeUIDTracksEx( e, tracksOut, trackTmp )
		trackTmp.pop()				# 任务已完成，把自己从轨迹表中移除


	def generateLogByUIDs( self, uids ):
		"""
		@param uids: list of uid
		"""
		logs = []
		for uid in uids:
			node = self._instanceDict[uid]
			logs.append( node.getName() )
			logs.append( "\n\t-->\t" )
		logs.pop()	# 去掉最后一个"\n\t-->\t"
		logs.append( "\n\n" )
		
		return "".join( logs )

	def calculateDepend( self ):
		"""
		检查依赖关系，把不需要的处理掉
		"""
		count = 1
		while count != 0:	# 一直循环，直到把所有不相关节点都清理干净
			count = 0
			for key in self._instanceDict.keys():	# 不能用iterkeys()，因为下面在执行删除操作
				#if key not in self._instanceDict:
				#	continue	# 这个是可能的，因为下面在执行一些关联删除操作
				node = self._instanceDict[key]
				if len( node.links ) == 0:						# 没有下层链接
					self._instanceDict.pop( key )				# 就可以把它从列表中去除
					count += 1
					for k in node.parents:
						pnode = self._instanceDict[k]
						pnode.links.remove( node.uid() )		# 并通知链接它的父节点
					node.release()
				"""有这个也许会不利于问题的查找
				elif len( node.parents ) == 0:					# 如果没有上层链接
					print "remove parents", node.pyobj_
					self._instanceDict.pop( key )				# 就可以把它从列表中去除，这样可以使生成的链接更简短，但可能会给定位问题带来麻烦
					count += 1
					for k in node.links:
						pnode = self._instanceDict[k]
						pnode.parents.remove( node.uid() )		# 并通知链接它的子节点
					node.release()
				"""

# garbage.py
