# -*- coding: gb18030 -*-
#
# 这个模块用于定义机器人测试任务模板

from .. import Task
from ..TaskGroup import SerialTaskGroup, ParallelTaskGroup
from ..TaskGroup import PrimacyParallelGroup

_TEMPLATES = {}

def register_template(name):
	"""Decorator to register new template function
	to global map."""
	def inner(f, name = name):
		global _TEMPLATES
		_TEMPLATES[name] = f

		return f

	return inner


def _create_task(TaskType, args):
	"""create task according to TaskType, TaskType maybe
	a task class type defined in Task.py module or a task
	template created in this module."""
	global _TEMPLATES

	if TaskType in _TEMPLATES:
		return _TEMPLATES[TaskType](args)
	else:
		return eval("Task.%s"%TaskType)(*args)


# ------------------------------------------------
# 模板函数，用传入的数据生成测试实例
# ------------------------------------------------

# 模板 tp_wait_move ：
@register_template("tp_wait_move")
def template_tp_wait_move( datas ):
	"""传送到指定地图位置，等待一段时间，然后走到指定位置"""
	tg = SerialTaskGroup()
	tg.addTask(Task.Teleport(*datas["Teleport"]))
	tg.addTask(Task.Wait(*datas["Wait"]))
	tg.addTask(Task.Move(*datas["Move"]))
	return tg


# 模板 tp_wait_move_detect ：
@register_template("tp_wait_move_detect")
def template_tp_wait_move_detect( datas ):
	"""传送到指定地图位置，等待一段时间，然后走到指定位置，
	然后进行位置检测"""
	tg = template_tp_wait_move(datas)
	tg.addTask(Task.Timeout(
					Task.PositionDetect(*datas["PositionDetect"]),
					*datas["Timeout"]
					))
	return tg


# 模板 tg_tp_wait_move_detect ：
@register_template("tg_tp_wait_move_detect")
def template_tg_tp_wait_move_detect( datas ):
	"""执行多次传送到指定地图位置，等待一段时间，然后走到指定位置"""
	tg = SerialTaskGroup()
	for data in datas:
		tg.addTask(template_tp_wait_move_detect(data))
	return tg


# 模板 timeout：
@register_template("timeout")
def template_timeout( datas ):
	"""超时任务模板"""
	t, (cls, args) = datas
	return Task.Timeout(_create_task(cls, args), t)


# 模板 loop：
@register_template("loop")
def template_loop( datas ):
	"""循环任务模板"""
	start, interval, (cls, args) = datas
	return Task.Loop(_create_task(cls, args), start, interval)


# 模板 repeat：
@register_template("repeat")
def template_repeat( datas ):
	"""重复任务模板"""
	count, (cls, args) = datas
	return Task.Repeat(_create_task(cls, args), count)


# 模板 move_and_detect：
@register_template("move_and_detect")
def template_move_and_detect( datas ):
	"""超时任务模板"""
	tg = SerialTaskGroup()

	dest = datas["destination"]
	range = datas.get("range", 0.5)		# optional arg
	timeout = datas["timeout"]

	tg.addTask(Task.Move(dest))
	tg.addTask(Task.Timeout(
					Task.PositionDetect(dest, range),
					timeout,
					))
	return tg


# 模板 custom_serial ：
@register_template("custom_serial")
def template_custom_serial( datas ):
	"""自定义顺序任务组模板，根据配置创建自定义任务实例"""
	tg = SerialTaskGroup()
	errstr = []

	for cls, args in datas:
		try:
			tg.addTask(_create_task(cls, args))
		except Exception, err:
			errstr.append(err)

	if errstr:
		raise Exception, "\n".join(errstr)
	else:
		return tg


# 模板 custom_parallel ：
@register_template("custom_parallel")
def template_custom_parallel( datas ):
	"""自定义并发任务组模板，根据配置创建自定义任务实例"""
	tg = ParallelTaskGroup()
	errstr = []

	for cls, args in datas:
		try:
			tg.addTask(_create_task(cls, args))
		except Exception, err:
			errstr.append(err)

	if errstr:
		raise Exception, "\n".join(errstr)
	else:
		return tg


# 模板 primacy_parallel ：
@register_template("primacy_parallel_combined")
def template_primacy_parallel_combined( datas ):
	"""有主任务的并发任务组模板，根据配置创建自定义任务实例，
	当主任务结束时整个任务组结束"""
	tg = ParallelTaskGroup()
	errstr = []

	# 第一个任务做主任务，将任务组中断方法绑定
	# 到主任务结束事件，于是当主任务结束时就会
	# 中断整个任务组
	try:
		primacy = ParallelTaskGroup()
		primacy.addTask(_create_task(*datas[0]))

		tg.addTask(primacy)
	except Exception, err:
		errstr.append(err)

	# 添加其它任务
	others = ParallelTaskGroup()
	tg.addTask(others)

	# 主任务结束事件绑定其它任务中断方法
	primacy.doneEvent().bind(others.interrupt)

	for cls, args in datas[1:]:
		try:
			others.addTask(_create_task(cls, args))
		except Exception, err:
			errstr.append(err)

	if errstr:
		raise Exception, "\n".join(errstr)
	else:
		return tg


# 模板 primacy_parallel ：
@register_template("primacy_parallel")
def template_primacy_parallel( datas ):
	"""有主任务的并发任务组模板，根据配置创建自定义任务实例，
	当主任务结束时整个任务组结束"""
	tg = PrimacyParallelGroup()
	errstr = []

	for cls, args in datas:
		try:
			tg.addTask(_create_task(cls, args))
		except Exception, err:
			errstr.append(err)

	if errstr:
		raise Exception, "\n".join(errstr)
	else:
		# 第一个任务做主任务，将任务组中断方法绑定
		# 到主任务结束事件，于是当主任务结束时就会
		# 中断整个任务组
		if tg.tasks:
			tg.set_primary_task(tg.tasks[0])

		return tg


# 模板 reuse_task ：
@register_template("reuse_task")
def template_reuse_task( key ):
	"""利用已有的taskapp数据生成新任务"""
	import appdata
	return _create_task(*appdata.DATA[key])


# ------------------------------------------------
# 应用模板，生成对应的模板测试实例
# ------------------------------------------------
def apply_template( key, datas ):
	try:
		return _create_task(key, datas)
	except Exception, err:
		print "Create task template of key %s failed:" % key
		print err

	return None
