# -*- coding: gb18030 -*-
#
# ���ģ�����ڶ�������˲�������ģ��

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
# ģ�庯�����ô�����������ɲ���ʵ��
# ------------------------------------------------

# ģ�� tp_wait_move ��
@register_template("tp_wait_move")
def template_tp_wait_move( datas ):
	"""���͵�ָ����ͼλ�ã��ȴ�һ��ʱ�䣬Ȼ���ߵ�ָ��λ��"""
	tg = SerialTaskGroup()
	tg.addTask(Task.Teleport(*datas["Teleport"]))
	tg.addTask(Task.Wait(*datas["Wait"]))
	tg.addTask(Task.Move(*datas["Move"]))
	return tg


# ģ�� tp_wait_move_detect ��
@register_template("tp_wait_move_detect")
def template_tp_wait_move_detect( datas ):
	"""���͵�ָ����ͼλ�ã��ȴ�һ��ʱ�䣬Ȼ���ߵ�ָ��λ�ã�
	Ȼ�����λ�ü��"""
	tg = template_tp_wait_move(datas)
	tg.addTask(Task.Timeout(
					Task.PositionDetect(*datas["PositionDetect"]),
					*datas["Timeout"]
					))
	return tg


# ģ�� tg_tp_wait_move_detect ��
@register_template("tg_tp_wait_move_detect")
def template_tg_tp_wait_move_detect( datas ):
	"""ִ�ж�δ��͵�ָ����ͼλ�ã��ȴ�һ��ʱ�䣬Ȼ���ߵ�ָ��λ��"""
	tg = SerialTaskGroup()
	for data in datas:
		tg.addTask(template_tp_wait_move_detect(data))
	return tg


# ģ�� timeout��
@register_template("timeout")
def template_timeout( datas ):
	"""��ʱ����ģ��"""
	t, (cls, args) = datas
	return Task.Timeout(_create_task(cls, args), t)


# ģ�� loop��
@register_template("loop")
def template_loop( datas ):
	"""ѭ������ģ��"""
	start, interval, (cls, args) = datas
	return Task.Loop(_create_task(cls, args), start, interval)


# ģ�� repeat��
@register_template("repeat")
def template_repeat( datas ):
	"""�ظ�����ģ��"""
	count, (cls, args) = datas
	return Task.Repeat(_create_task(cls, args), count)


# ģ�� move_and_detect��
@register_template("move_and_detect")
def template_move_and_detect( datas ):
	"""��ʱ����ģ��"""
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


# ģ�� custom_serial ��
@register_template("custom_serial")
def template_custom_serial( datas ):
	"""�Զ���˳��������ģ�壬�������ô����Զ�������ʵ��"""
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


# ģ�� custom_parallel ��
@register_template("custom_parallel")
def template_custom_parallel( datas ):
	"""�Զ��岢��������ģ�壬�������ô����Զ�������ʵ��"""
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


# ģ�� primacy_parallel ��
@register_template("primacy_parallel_combined")
def template_primacy_parallel_combined( datas ):
	"""��������Ĳ���������ģ�壬�������ô����Զ�������ʵ����
	�����������ʱ�������������"""
	tg = ParallelTaskGroup()
	errstr = []

	# ��һ�������������񣬽��������жϷ�����
	# ������������¼������ǵ����������ʱ�ͻ�
	# �ж�����������
	try:
		primacy = ParallelTaskGroup()
		primacy.addTask(_create_task(*datas[0]))

		tg.addTask(primacy)
	except Exception, err:
		errstr.append(err)

	# �����������
	others = ParallelTaskGroup()
	tg.addTask(others)

	# ����������¼������������жϷ���
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


# ģ�� primacy_parallel ��
@register_template("primacy_parallel")
def template_primacy_parallel( datas ):
	"""��������Ĳ���������ģ�壬�������ô����Զ�������ʵ����
	�����������ʱ�������������"""
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
		# ��һ�������������񣬽��������жϷ�����
		# ������������¼������ǵ����������ʱ�ͻ�
		# �ж�����������
		if tg.tasks:
			tg.set_primary_task(tg.tasks[0])

		return tg


# ģ�� reuse_task ��
@register_template("reuse_task")
def template_reuse_task( key ):
	"""�������е�taskapp��������������"""
	import appdata
	return _create_task(*appdata.DATA[key])


# ------------------------------------------------
# Ӧ��ģ�壬���ɶ�Ӧ��ģ�����ʵ��
# ------------------------------------------------
def apply_template( key, datas ):
	try:
		return _create_task(key, datas)
	except Exception, err:
		print "Create task template of key %s failed:" % key
		print err

	return None
