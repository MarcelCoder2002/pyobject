from unittest import TestCase

from pyobject import AccessError, AccessErrors, Object, protectedmethod


class TestProtectedFromInside(TestCase):
	def testGetProtectedFromInside(self):
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.protected_attribute("protected", "[protected value]")
				this.assertEqual(self.protected, "[protected value]", "Protected attribute created and defined to '[protected value]'")

		A()
	
	def testSetProtectedFromInside(self):
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.protected_attribute("protected", "[protected value]")
				this.assertEqual(self.protected, "[protected value]", "Protected attribute created and defined to '[protected value]'")
				self.protected = "[protected value changed]"
				this.assertEqual(self.protected, "[protected value changed]", "Protected value changed")

		A()


class TestProtectedFromInsideWithChild(TestCase):
	def setUp(self) -> None:

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.protected_attribute("protected", "[protected value]")

		self._Type = A
		return super().setUp()

	def testGetProtectedFromInsideWithChild(self):
		this = self

		class B(self._Type):
			def __init__(self) -> None:
				super().__init__()
				this.assertEqual(self.protected, "[protected value]", "Protected attribute created and defined to '[protected value]'")

		B()
	
	def testSetProtectedFromInsideWithChild(self):
		this = self

		class B(self._Type):
			def __init__(self) -> None:
				super().__init__()
				this.assertEqual(self.protected, "[protected value]", "Protected attribute created and defined to '[protected value]'")
				self.protected = "[protected value changed]"
				this.assertEqual(self.protected, "[protected value changed]", "Protected value changed")

		B()


class TestProtectedFromOutside(TestCase):
	def setUp(self) -> None:
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.protected_attribute("protected", "[protected value]")
				this.assertEqual(self.protected, "[protected value]", "Protected attribute created and defined to '[protected value]'")
		
		self._Type = A
		return super().setUp()

	def testGetProtectedFromOutside(self):
		t = self._Type()
		with self.assertRaises(AccessError) as access_error:
			self.assertEqual(t.protected, "[protected value]", "Protected attribute created and defined to '[protected value]'")
		self.assertEqual(access_error.exception.type, AccessErrors.PROTECTED)
	
	def testSetProtectedFromOutside(self):	
		t = self._Type()
		with self.assertRaises(AccessError) as access_error:
			self.assertEqual(t.protected, "[protected value]", "Protected attribute created and defined to '[protected value]'")
			t.protected = "[protected value changed]"
			self.assertEqual(t.protected, "[protected value changed]", "Protected value changed")
		self.assertEqual(access_error.exception.type, AccessErrors.PROTECTED)


class TestProtectedFromOutsideWithSameContext(TestCase):
	def setUp(self) -> None:
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.protected_attribute("protected", "[protected value]")
		
		class Get:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
				with this.assertRaises(AccessError) as access_error:
					this.assertEqual(self.a.protected, "[protected value]", "Protected attribute created and defined to '[protected value]'")
				this.assertEqual(access_error.exception.type, AccessErrors.PROTECTED)
		
		class Set:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
				with this.assertRaises(AccessError) as access_error:
					this.assertEqual(self.a.protected, "[protected value]", "Protected attribute created and defined to '[protected value]'")
					self.a.protected = "[protected value changed]"
					this.assertEqual(self.a.protected, "[protected value changed]", "Protected value changed")
				this.assertEqual(access_error.exception.type, AccessErrors.PROTECTED)
		
		self._TypeGet = Get
		self._TypeSet = Set
		return super().setUp()

	def testGetProtectedFromOutsideWithSameContext(self):
		self._TypeGet()
	
	def testSetProtectedFromOutsideWithSameContext(self):
		self._TypeSet()


class TestProtectedFromOutsideWithNotSameContext(TestCase):
	def setUp(self) -> None:
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.protected_attribute("protected", "[protected value]")
		
		class B:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
		
		self._Type = B
		return super().setUp()

	def testGetProtectedFromOutsideWithNotSameContext(self):
		t = self._Type()
		with self.assertRaises(AccessError) as access_error:
			self.assertEqual(t.a.protected, "[protected value]", "Protected attribute created and defined to '[protected value]'")
		self.assertEqual(access_error.exception.type, AccessErrors.PROTECTED)

	
	def testSetProtectedFromOutsideWithNotSameContext(self):
		t = self._Type()
		with self.assertRaises(AccessError) as access_error:
			self.assertEqual(t.a.protected, "[protected value]", "Protected attribute created and defined to '[protected value]'")
			t.a.protected = "[protected value changed]"
			self.assertEqual(t.a.protected, "[protected value changed]", "Protected value changed")
		self.assertEqual(access_error.exception.type, AccessErrors.PROTECTED)


class TestProtectedMethodFromInside(TestCase):
	def testProtectedMethodFromInside(self):
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				this.assertEqual(self.protected(), "[protected value]", "Protected method created and defined to '[protected value]'")
			
			@protectedmethod
			def protected(self):
				return "[protected value]"

		A()


class TestProtectedMethodFromInsideWithChild(TestCase):
	def setUp(self) -> None:
		class A(Object):
			def __init__(self) -> None:
				super().__init__()
			
			@protectedmethod
			def protected(self):
				return "[protected value]"
			
		self._Type = A
		return super().setUp()

	def testProtectedMethodFromInsideWithChild(self):
		this = self

		class B(self._Type):
			def __init__(self) -> None:
				super().__init__()
				this.assertEqual(self.protected(), "[protected value]", "Protected method created and defined to '[protected value]'")

		B()


class TestProtectedMethodFromOutside(TestCase):
	def setUp(self) -> None:
		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				
			@protectedmethod
			def protected(self):
				return "[protected value]"
			
		self._Type = A
		return super().setUp()

	def testProtectedMethodFromOutside(self):
		t = self._Type()
		with self.assertRaises(AccessError) as access_error:
			self.assertEqual(t.protected(), "[protected value]", "Protected method created and defined to '[protected value]'")
		self.assertEqual(access_error.exception.type, AccessErrors.PROTECTED)


class TestProtectedMethodFromOutsideWithSameContext(TestCase):
	def setUp(self) -> None:
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				
			@protectedmethod
			def protected(self):
				return "[protected value]"
		
		class B:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
				with this.assertRaises(AccessError) as access_error:
					this.assertEqual(self.a.protected(), "[protected value]", "Protected method created and defined to '[protected value]'")
				this.assertEqual(access_error.exception.type, AccessErrors.PROTECTED)
		
		self._Type = B
		return super().setUp()

	def testProtectedMethodFromOutsideWithSameContext(self):
		self._Type()


class TestProtectedMethodFromOutsideWithNotSameContext(TestCase):
	def setUp(self) -> None:
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				
			@protectedmethod
			def protected(self):
				return "[protected value]"
		
		class B:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
		
		self._Type = B
		return super().setUp()

	def testProtectedMethodFromOutsideWithNotSameContext(self):
		t = self._Type()
		with self.assertRaises(AccessError) as access_error:
			self.assertEqual(t.a.protected(), "[protected value]", "Protected method created and defined to '[protected value]'")
		self.assertEqual(access_error.exception.type, AccessErrors.PROTECTED)

