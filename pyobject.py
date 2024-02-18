from abc import ABCMeta, abstractmethod
from enum import Enum, auto
from inspect import FrameInfo
from types import MethodType
from typing import Any, Callable

from utils import getBase, getBaseByName, stack


class AccessErrors(Enum):
	NONE = auto()
	PROTECTED = auto()
	PRIVATE = auto()
	FINAL = auto()


class AccessError(Exception):
	def __init__(self, *args, type: AccessErrors = AccessErrors.NONE) -> None:
		super().__init__(*args)
		self.type = type


class _Object(metaclass=ABCMeta):
	__slots__ = ()

	@abstractmethod
	def new_attribute(self, name: str, access_mode: str = 'public', value: Any = None, final: bool = False):
		pass

	@abstractmethod
	def public_attribute(self, name: str, value: Any = None, final: bool = False):
		pass

	@abstractmethod
	def protected_attribute(self, name: str, value: Any = None, final: bool = False):
		pass

	@abstractmethod
	def private_attribute(self, name: str, value: Any = None, final: bool = False):
		pass


def _object() -> type[_Object]:
	class Attribute:
		__slots__ = ('name', 'value', 'access_mode', 'final', 'base_class')

		def __init__(
				self, 
				name: str, 
				value: Any = None, 
				access_mode: str = 'public', 
				final: bool = False, 
				base_class: type[_Object] = None
			) -> None:
			self.name = name
			self.value = value
			self.access_mode = access_mode
			self.final = final
			self.base_class = base_class
			# print("Attribute '%s' created with access mode '%s' from class '%s'" % (name, access_mode, base_class.__name__))

	class AccesController(dict):
		__slots__ = ('objects')

		def __init__(self):
			self.objects = {}
		
		def __set__(self, instance, value):
			if not isinstance(value, dict):
				raise TypeError(
					f"__dict__ must be set to a dictionary, not a '{value.__class__.__name__}'"
				)
			self.objects[id(instance)]['dict'] = value
		
		def __get__(self, instance, owner=None):
			o = self.objects.get(id(instance), None)
			if o:
				return (o['dict'], self)
			elif instance is not None:
				o = {
					'attributes': {
						'public': {}, 
						'protected': {}, 
						'private': {}
					},
					'dict': {}
				}
				self.objects[id(instance)] = o
				return (o['dict'], self)
			else:
				return owner.__dict__
		
		def new_object(self, object):
			self.objects[id(object)] = {
				'attributes': {
					'public': {}, 
					'protected': {}, 
					'private': {}
				},
				'dict': {}
			}
		
		def delete_object(self, object):
			self.objects.pop(id(object))
			# print("Object '%s' deleted" % object)
		
		def update_object_id(self, old: int, new: int):
			self.objects[new] = self.objects.pop(old)
		
		def new_attribute(
				self, 
				instance: _Object,
				name: str, 
				value: Any = None,
				access_mode: str = 'public', 
				final: bool = False,
				base_class: type[_Object] = None
			):
			o = self.objects[id(instance)]
			d = o['dict']				
			code = stack(4)[-1].frame.f_code
			class_name = code.co_qualname.removesuffix(f".{code.co_name}").split('.')[-1]
			if class_name != instance.__class__.__name__:
				base_class = getBaseByName(instance, class_name, Object)
			if d.__contains__(name):
				o['attributes'][access_mode][name] = Attribute(name, d.pop(name), access_mode, final, base_class)
			else:
				o['attributes'][access_mode][name] = Attribute(name, value, access_mode, final, base_class)
		
		def get(self, name: str, instance: _Object, frame_info: FrameInfo = None):
			# print("Get attribute '%s' from class '%s'" % (name, instance))
			o = self.objects[id(instance)]
			d = o['dict']
			a = o['attributes']
			error = None
			try:
				return (d[name],)
			except KeyError:
				try:
					return (a['public'][name].value,)
				except KeyError:
					protected = a['protected'].__contains__(name)
					private = protected or a['private'].__contains__(name)
					if protected or private:
						if frame_info is None:
							frame_info = stack(3)[-1]
						fname = frame_info.function
						owner = type(instance)
						function = getattr(owner, fname, None)
						if callable(function):
							same_code = frame_info.frame.f_code.co_code == function.__code__.co_code
							if protected:
								attribute = a['protected'][name]
								if (same_code or 
									(not same_code and not attribute.base_class is owner and 
		  							(attribute.base_class is getBase(instance, Object)))):
									return (attribute.value,)
								else:
									error = AccessError(f"'{name}' is protected", type=AccessErrors.PROTECTED)
							else:
								attribute = a['private'][name]
								same_class = attribute.base_class is owner
								if ((same_code and same_class) or 
									(not same_code and not same_class and 
		  							(attribute.base_class is getBase(instance, Object)))):
									return (attribute.value,)
								else:
									error = AccessError(f"'{name}' is private", type=AccessErrors.PRIVATE)
						else:
							if protected:
								error = AccessError(f"'{name}' is protected", type=AccessErrors.PROTECTED)
							else:
								error = AccessError(f"'{name}' is private", type=AccessErrors.PRIVATE)
			if error:
				raise error
			return ()
		
		def set(self, name: str, value: Any, instance: _Object):
			# print("Set attribute '%s' with '%s' from class '%s'" % (name, value, instance))
			o = self.objects[id(instance)]
			d = o['dict']
			a = o['attributes']
			error = None
			try:
				attribute = a['public'][name]
				if attribute.final:
					error = AccessError(f"'{name}' is final", type=AccessErrors.FINAL)
				else:
					attribute.value = value
					return True
			except KeyError:
				protected = a['protected'].__contains__(name)
				private = protected or a['private'].__contains__(name)
				if protected or private:
					frame_info = stack(3)[-1]
					fname = frame_info.function
					owner = type(instance)
					function = getattr(owner, fname, None)
					if callable(function):
						same_code = frame_info.frame.f_code.co_code == function.__code__.co_code
						if protected:
							attribute = a['protected'][name]
							if (same_code or 
								(not same_code and not attribute.base_class is owner and 
								(attribute.base_class is getBase(instance, Object)))):
								if attribute.final:
									error = AccessError(f"'{name}' is final", type=AccessErrors.FINAL)
								else:
									attribute.value = value
									return True
							else:
								error = AccessError(f"'{name}' is protected", type=AccessErrors.PROTECTED)
						else:
							attribute = a['private'][name]
							same_class = attribute.base_class is owner
							if (same_code and same_class) or \
								(not same_code and not same_class and (attribute.base_class is getBase(instance, Object))):
								if attribute.final:
									error = AccessError(f"'{name}' is final", type=AccessErrors.FINAL)
								else:
									attribute.value = value
									return True
							else:
								error = AccessError(f"'{name}' is private", type=AccessErrors.PRIVATE)
					else:
						if protected:
							error = AccessError(f"'{name}' is protected", type=AccessErrors.PROTECTED)
						else:
							error = AccessError(f"'{name}' is private", type=AccessErrors.PRIVATE)
			if error:
				raise error
			return False
		
		def delete(self, name: str, instance: _Object):
			o = self.objects[id(instance)]
			d = o['dict']
			if name in d:
				del d[name]
				return True
			return False
		
		def reset(self, instance: _Object):
			o = self.objects[id(instance)]
			a = o['attributes']
			o['dict'] = {}


	class _PrivateObject(_Object):
		__dict__ = AccesController()
		
		def __init__(self) -> None:
			super().__init__()
			_, access_controller = super().__getattribute__('__dict__')
			access_controller.new_object(self)
			
		def __init_subclass__(cls, **kwargs) -> None:
			super().__init_subclass__(**kwargs)
			fi = stack(3)[-1]
			cls.__place__ = (fi.lineno, fi.filename)
		
		def __del__(self):
			_, access_controller = super().__getattribute__('__dict__')
			access_controller.delete_object(self)

		def __getattribute__(self, name: str, frame=None) -> Any:
			__dict__, access_controller = super().__getattribute__('__dict__')
			if name == '__dict__':
				return __dict__
			else:
				result = access_controller.get(name, self, frame)
				if result:
					return result[0]
				else:
					return super().__getattribute__(name)
		
		def __setattr__(self, name: str, value: Any) -> None:
			__dict__, access_controller = super().__getattribute__('__dict__')
			if name == '__dict__':
				super().__setattr__(name, value)
			elif not access_controller.set(name, value, self):
				super().__setattr__(name, value)
		
		def __delattr__(self, name: str) -> None:
			__dict__, access_controller = super().__getattribute__('__dict__')
			if name == '__dict__':
				access_controller.reset(self)
			elif not access_controller.delete(name, self):
				super().__delattr__(name)
		
		def new_attribute(self, name: str, access_mode: str = 'public', value: Any = None, final: bool = False):
			_, access_controller = super().__getattribute__('__dict__')
			access_controller.new_attribute(self, name, value, access_mode, final, type(self))
		
		def public_attribute(self, name: str, value: Any = None, final: bool = False):
			self.new_attribute(name=name, access_mode='public', value=value, final=final)

		def protected_attribute(self, name: str, value: Any = None, final: bool = False):
			self.new_attribute(name=name, access_mode='protected', value=value, final=final)

		def private_attribute(self, name: str, value: Any = None, final: bool = False):
			self.new_attribute(name=name, access_mode='private', value=value, final=final)
	
	return _PrivateObject


class Object(_object()):
	pass


def publicmethod(function):
	return function


def protectedmethod(function):
	code = stack(2)[-1].frame.f_code
	place = (code.co_firstlineno, code.co_filename)
	def wrapper(*args, **kwargs):
		frame_info = stack(2)[-1]
		instance = args[0]
		method = frame_info.function
		owner = type(instance)
		method = getattr(owner, method, None)
		if callable(method):
			same_code = frame_info.frame.f_code.co_code == method.__code__.co_code
			if (same_code or 
				(not same_code and not (place == owner.__place__) and 
				(place == getBase(instance, Object).__place__))):
				return function(*args, **kwargs)
		raise AccessError(f"'{function.__name__}' is protected", type=AccessErrors.PROTECTED)
	return wrapper


def privatemethod(function):
	code = stack(2)[-1].frame.f_code
	place = (code.co_firstlineno, code.co_filename)
	def wrapper(*args, **kwargs):
		frame_info = stack(2)[-1]
		instance = args[0]
		method = frame_info.function
		owner = type(instance)
		method = getattr(owner, method, None)
		if callable(method):
			same_code = frame_info.frame.f_code.co_code == method.__code__.co_code
			same_class = place == owner.__place__
			if ((same_code and same_class) or 
				(not same_code and not same_class and 
				(place == getBase(instance, Object).__place__))):
				return function(*args, **kwargs)
		raise AccessError(f"'{function.__name__}' is private", type=AccessErrors.PRIVATE)
	return wrapper


class publicstaticmethod(staticmethod):
	pass


class protectedstaticmethod(staticmethod):
	def __init__(self, function: Callable) -> None:
		super().__init__(function)
		code = stack(2)[-1].frame.f_code
		self.__place = (code.co_firstlineno, code.co_filename)
		self.__owner = None
	
	def __get__(self, instance, owner: type = None):
		self.__owner = owner or type(instance)
		return self

	def __call__(self, *args, **kwargs) -> Any:
		frame_info = stack(2)[-1]
		method = frame_info.function
		owner = self.__owner
		method = getattr(owner, method, None)
		if callable(method):
			same_code = frame_info.frame.f_code.co_code == method.__code__.co_code
			if (same_code or 
				(not same_code and not (self.__place == owner.__place__) and 
				(self.__place == getBase(owner, Object).__place__))):
				return self.__func__(*args, **kwargs)
		raise AccessError(f"'{self.__func__.__name__}' is protected", type=AccessErrors.PROTECTED)


class privatestaticmethod(staticmethod):
	def __init__(self, function: Callable) -> None:
		super().__init__(function)
		code = stack(2)[-1].frame.f_code
		self.__place = (code.co_firstlineno, code.co_filename)
		self.__owner = None
	
	def __get__(self, instance, owner: type = None):
		self.__owner = owner or type(instance)
		return self

	def __call__(self, *args, **kwargs) -> Any:
		frame_info = stack(2)[-1]
		method = frame_info.function
		owner = self.__owner
		method = getattr(owner, method, None)
		if callable(method):
			same_code = frame_info.frame.f_code.co_code == method.__code__.co_code
			same_class = self.__place == owner.__place__
			if ((same_code and same_class) or 
				(not same_code and not same_class and 
				(self.__place == getBase(owner, Object).__place__))):
				return self.__func__(*args, **kwargs)
		raise AccessError(f"'{self.__func__.__name__}' is private", type=AccessErrors.PRIVATE)


class publicclassmethod(classmethod):
	pass


class protectedclassmethod(classmethod):
	def __init__(self, function: Callable) -> None:
		super().__init__(function)
		code = stack(2)[-1].frame.f_code
		self.__place = (code.co_firstlineno, code.co_filename)
	
	def __get__(self, instance, owner: type = None):
		return MethodType(self, owner or type(instance))

	def __call__(self, *args, **kwargs) -> Any:
		frame_info = stack(2)[-1]
		owner = args[0]
		method = frame_info.function
		method = getattr(owner, method, None)
		if callable(method):
			same_code = frame_info.frame.f_code.co_code == method.__code__.co_code
			if (same_code or 
				(not same_code and not (self.__place == owner.__place__) and 
				(self.__place == getBase(owner, Object).__place__))):
				return self.__func__(*args, **kwargs)
		raise AccessError(f"'{self.__func__.__name__}' is protected", type=AccessErrors.PROTECTED)


class privateclassmethod(classmethod):
	def __init__(self, function: Callable) -> None:
		super().__init__(function)
		code = stack(2)[-1].frame.f_code
		self.__place = (code.co_firstlineno, code.co_filename)
	
	def __get__(self, instance, owner: type = None) -> Callable:
		return MethodType(self, owner or type(instance))

	def __call__(self, *args, **kwargs) -> Any:
		frame_info = stack(2)[-1]
		owner = args[0]
		method = frame_info.function
		method = getattr(owner, method, None)
		if callable(method):
			same_code = frame_info.frame.f_code.co_code == method.__code__.co_code
			same_class = self.__place == owner.__place__
			if ((same_code and same_class) or 
				(not same_code and not same_class and 
				(self.__place == getBase(owner, Object).__place__))):
				return self.__func__(*args, **kwargs)
		raise AccessError(f"'{self.__func__.__name__}' is private", type=AccessErrors.PRIVATE)


class publicproperty(property):
	pass


class protectedproperty(property):
	def __init__(self, fget=None, fset=None, fdel=None, doc=None):
		super().__init__(fget, fset, fdel, doc)
		code = stack(2)[-1].frame.f_code
		self.__place = (code.co_firstlineno, code.co_filename)

	def __get__(self, obj, objtype=None):
		if obj is None:
			return self
		if self.fget is None:
			raise AttributeError("can't get attribute")
		frame_info = stack(3)[-1]
		owner = objtype or type(obj)
		method = frame_info.function
		method = getattr(owner, method, None)
		if callable(method):
			same_code = frame_info.frame.f_code.co_code == method.__code__.co_code
			if (same_code or 
				(not same_code and not (self.__place == owner.__place__) and 
				(self.__place == getBase(owner, Object).__place__))):
				return self.fget(obj)
		raise AccessError(f"'{self.fget.__name__}' is protected", type=AccessErrors.PROTECTED)

	def __set__(self, obj, value):
		if self.fset is None:
			raise AttributeError("can't set attribute")
		frame_info = stack(3)[-1]
		owner = type(obj)
		method = frame_info.function
		method = getattr(owner, method, None)
		if callable(method):
			same_code = frame_info.frame.f_code.co_code == method.__code__.co_code
			if (same_code or 
				(not same_code and not (self.__place == owner.__place__) and 
				(self.__place == getBase(owner, Object).__place__))):
				return self.fset(obj, value)
		raise AccessError(f"'{self.fset.__name__}' is protected", type=AccessErrors.PROTECTED)

	def __delete__(self, obj):
		if self.fdel is None:
			raise AttributeError("can't delete attribute")
		frame_info = stack(3)[-1]
		owner = type(obj)
		method = frame_info.function
		method = getattr(owner, method, None)
		if callable(method):
			same_code = frame_info.frame.f_code.co_code == method.__code__.co_code
			if (same_code or 
				(not same_code and not (self.__place == owner.__place__) and 
				(self.__place == getBase(owner, Object).__place__))):
				return self.fdel(obj)
		raise AccessError(f"'{self.fdel.__name__}' is protected", type=AccessErrors.PROTECTED)


class privateproperty(property):
	def __init__(self, fget=None, fset=None, fdel=None, doc=None):
		super().__init__(fget, fset, fdel, doc)
		code = stack(2)[-1].frame.f_code
		self.__place = (code.co_firstlineno, code.co_filename)

	def __get__(self, obj, objtype=None):
		if obj is None:
			return self
		if self.fget is None:
			raise AttributeError("can't get attribute")
		frame_info = stack(3)[-1]
		owner = objtype or type(obj)
		method = frame_info.function
		method = getattr(owner, method, None)
		if callable(method):
			same_code = frame_info.frame.f_code.co_code == method.__code__.co_code
			same_class = self.__place == owner.__place__
			if ((same_code and same_class) or 
				(not same_code and not same_class and 
				(self.__place == getBase(owner, Object).__place__))):
				return self.fget(obj)
		raise AccessError(f"'{self.fget.__name__}' is private", type=AccessErrors.PRIVATE)

	def __set__(self, obj, value):
		if self.fset is None:
			raise AttributeError("can't set attribute")
		frame_info = stack(3)[-1]
		owner = type(obj)
		method = frame_info.function
		method = getattr(owner, method, None)
		if callable(method):
			same_code = frame_info.frame.f_code.co_code == method.__code__.co_code
			same_class = self.__place == owner.__place__
			if ((same_code and same_class) or 
				(not same_code and not same_class and 
				(self.__place == getBase(owner, Object).__place__))):
				return self.fset(obj, value)
		raise AccessError(f"'{self.fset.__name__}' is private", type=AccessErrors.PRIVATE)

	def __delete__(self, obj):
		if self.fdel is None:
			raise AttributeError("can't delete attribute")
		frame_info = stack(3)[-1]
		owner = type(obj)
		method = frame_info.function
		method = getattr(owner, method, None)
		if callable(method):
			same_code = frame_info.frame.f_code.co_code == method.__code__.co_code
			same_class = self.__place == owner.__place__
			if ((same_code and same_class) or 
				(not same_code and not same_class and 
				(self.__place == getBase(owner, Object).__place__))):
				return self.fdel(obj)
		raise AccessError(f"'{self.fdel.__name__}' is private", type=AccessErrors.PRIVATE)


if __name__ == '__main__':
	pass
