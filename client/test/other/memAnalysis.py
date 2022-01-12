# -*- coding: gb18030 -*-
import gc
import Timer

g_tick = 60

class ObjCount( object ):
	"""
	1. 间隔 10分钟 取一次对象的数目
	2. 比较前后两次的对象差异
		将数量比较大的
		两次间隔产生的数量比较大的
	3. 最后一次都和前面的每次进行比较（ 把间隔数目大的输出 ）
	"""
	
	def __init__( self ):
		self.objects_dict = {}
		self.objects_diff = {}
		self.objects_large = {}
		self.checkTimer = None
		self.objectNumList = []
	
		
	def analysis( self ):
		gc.collect()
		
		f_num 		= "num.log"   			# 所有的对象的数目的日志文件
		f_diff 		= "diff.log"			# 个数差距比较大的对象的日志文件
		f_disLarge 	= "disLarge.log" # 最后一次都和前面的每次进行比较
		
		dic = {}
		inst_obj_counts = 0		#类实例对象数量
		all_obj_counts = 0
		
		for o in gc.get_objects():
			all_obj_counts  += 1
			if "type" in str(type(o)) or "Weaker" in str(type(o)) or "weakref" in str(type(o)):
				continue
			inst_obj_counts += 1
			if dic.has_key( str(type(o)) ):
				dic[ str( type( o ) ) ] = dic[ str( type( o ) ) ] + 1
			else:
				dic[ str( type( o ) ) ] = 1
		
		self.objectNumList.append( (inst_obj_counts, all_obj_counts ) )

		# 总对象
		for k, v in dic.items():
			if self.objects_dict.has_key(k):
				self.objects_dict[k].append(v)
			else:
				self.objects_dict[k] = [v]
	
		# 最后一次都和前面的每次进行比较（ 把间隔数目大的（差距）输出 ）
		for k, v in dic.items():
			la = self.objects_dict[k]
			
			max = 0
			for i in la:
				temp = abs( v -i )
				if temp > max:
					max = temp
			
			if self.objects_large.has_key( k ):
				self.objects_large[k].append( max )
			else:
				self.objects_large[k] = [v]
			
		# 比较前后两次的对象差异,如果差值大于0则输出（差距）
		for k, v in dic.items():
			la = self.objects_dict[k]
			
			if len(la) >= 2:
				diff = la[-1] - la[-2]
				self.objects_diff[k].append( diff )
			else:
				self.objects_diff[k] = [v]
					 
			
		self.save( f_num, self.objects_dict )
		self.save( f_diff, self.objects_diff )
		self.save( f_disLarge, self.objects_large )
		
	
	def save( self, log, _dict ):
		"""
		保存进文件
		"""
		f = open( log, "w" )
		
		l = []
		dist = ""
		
		for key,value in _dict.items():
			t = ( value, key )
			l.append(t)
			
		l.sort()
		
		for i in l:
			dist += str( i[1] ) + "   " + str( i[0] ) + "\n"
			
		f.write( dist )
		f.close()
		
	
	def start( self ):
		"""
		开始收集数据
		"""
		print "python object count in memAnalysis module start work!............"
		self.checkTimer = Timer.addTimer( 1, g_tick, self.analysis )
		
	def cancel( self ):
		"""
		结束收集数据
		"""
		self.objects_dict		 = {}
		self.objects_diff		 = {}
		self.objects_large 		 = {}
		
		self.objectNumList = []
		
		Timer.cancel( self.checkTimer )
		self.checkTimer = None 
		print "work has done!"
		
	def changeIntevalTime( self, time ):
		"""
		调整输出到日志的间隔时间
		"""
		global g_tick
		g_tick = time
		
		Timer.cancel( self.checkTimer )
		self.checkTimer = None
		
		self.checkTimer = Timer.addTimer( 1, time, self.analysis )
		
ocInst = ObjCount()
