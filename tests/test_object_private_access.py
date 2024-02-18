from unittest import TestCase

from pyobject import AccessError, AccessErrors, Object, privatemethod


class TestPrivateFromInside(TestCase):
	def testGetPrivateFromInside(self):
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.private_attribute("private", "[private value]")
				this.assertEqual(self.private, "[private value]", "Private attribute created and defined to '[private value]'")

		A()
	
	def testSetPrivateFromInside(self):
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.private_attribute("private", "[private value]")
				this.assertEqual(self.private, "[private value]", "Private attribute created and defined to '[private value]'")
				self.private = "[private value changed]"
				this.assertEqual(self.private, "[private value changed]", "Private value changed")

		A()


class TestPrivateFromInsideWithChild(TestCase):
	def setUp(self) -> None:
		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.private_attribute("private", "[private value]")
		self._Type = A
		return super().setUp()

	def testGetPrivateFromInsideWithChild(self):
		this = self

		class B(self._Type):
			def __init__(self) -> None:
				super().__init__()
				this.assertEqual(self.private, "[private value]", "Private attribute created and defined to '[private value]'")

		with self.assertRaises(AccessError) as access_error:
			B()
		self.assertEqual(access_error.exception.type, AccessErrors.PRIVATE)
	
	def testSetPrivateFromInsideWithChild(self):
		this = self

		class B(self._Type):
			def __init__(self) -> None:
				super().__init__()
				this.assertEqual(self.private, "[private value]", "Private attribute created and defined to '[private value]'")
				self.private = "[private value changed]"
				this.assertEqual(self.private, "[private value changed]", "Private value changed")

		with self.assertRaises(AccessError) as access_error:
			B()
		self.assertEqual(access_error.exception.type, AccessErrors.PRIVATE)


class TestPrivateFromOutside(TestCase):
	def setUp(self) -> None:
		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.private_attribute("private", "[private value]")
		self._Type = A
		return super().setUp()

	def testGetPrivateFromOutside(self):
		t = self._Type()
		with self.assertRaises(AccessError) as access_error:
			self.assertEqual(t.private, "[private value]", "Private attribute created and defined to '[private value]'")
		self.assertEqual(access_error.exception.type, AccessErrors.PRIVATE)
	
	def testSetPrivateFromOutside(self):	
		t = self._Type()
		with self.assertRaises(AccessError) as access_error:
			self.assertEqual(t.private, "[private value]", "Private attribute created and defined to '[private value]'")
			t.private = "[private value changed]"
			self.assertEqual(t.private, "[private value changed]", "Private value changed")
		self.assertEqual(access_error.exception.type, AccessErrors.PRIVATE)


class TestPrivateFromOutsideWithSameContext(TestCase):
	def setUp(self) -> None:
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.private_attribute("private", "[private value]")
		
		class Get:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
				with this.assertRaises(AccessError) as access_error:
					this.assertEqual(self.a.private, "[private value]", "Private attribute created and defined to '[private value]'")
				this.assertEqual(access_error.exception.type, AccessErrors.PRIVATE)
		
		class Set:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
				with this.assertRaises(AccessError) as access_error:
					this.assertEqual(self.a.private, "[private value]", "Private attribute created and defined to '[private value]'")
					self.a.private = "[private value changed]"
					this.assertEqual(self.a.private, "[private value changed]", "Private value changed")
				this.assertEqual(access_error.exception.type, AccessErrors.PRIVATE)
		
		self._TypeGet = Get
		self._TypeSet = Set
		return super().setUp()

	def testGetPrivateFromOutsideWithSameContext(self):
		self._TypeGet()
	
	def testSetPrivateFromOutsideWithSameContext(self):
		self._TypeSet()


class TestPrivateFromOutsideWithNotSameContext(TestCase):
	def setUp(self) -> None:
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.private_attribute("private", "[private value]")
		
		class B:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
		
		self._Type = B
		return super().setUp()

	def testGetPrivateFromOutsideWithNotSameContext(self):
		t = self._Type()
		with self.assertRaises(AccessError) as access_error:
			self.assertEqual(t.a.private, "[private value]", "Private attribute created and defined to '[private value]'")
		self.assertEqual(access_error.exception.type, AccessErrors.PRIVATE)

	
	def testSetPrivateFromOutsideWithNotSameContext(self):
		t = self._Type()
		with self.assertRaises(AccessError) as access_error:
			self.assertEqual(t.a.private, "[private value]", "Private attribute created and defined to '[private value]'")
			t.a.private = "[private value changed]"
			self.assertEqual(t.a.private, "[private value changed]", "Private value changed")
		self.assertEqual(access_error.exception.type, AccessErrors.PRIVATE)


class TestPrivateMethodFromInside(TestCase):
	def testPrivateMethodFromInside(self):
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				this.assertEqual(self.private(), "[private value]", "Private method created and defined to '[private value]'")
			
			@privatemethod
			def private(self):
				return "[private value]"

		A()


class TestPrivateMethodFromInsideWithChild(TestCase):
	def setUp(self) -> None:
		class A(Object):
			def __init__(self) -> None:
				super().__init__()
			
			@privatemethod
			def private(self):
				return "[private value]"
			
		self._Type = A
		return super().setUp()

	def testPrivateMethodFromInsideWithChild(self):
		this = self

		class B(self._Type):
			def __init__(self) -> None:
				super().__init__()
				this.assertEqual(self.private(), "[private value]", "Private method created and defined to '[private value]'")

		with self.assertRaises(AccessError) as access_error:
			B()
		self.assertEqual(access_error.exception.type, AccessErrors.PRIVATE)


class TestPrivateMethodFromOutside(TestCase):
	def setUp(self) -> None:
		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				
			@privatemethod
			def private(self):
				return "[private value]"
			
		self._Type = A
		return super().setUp()

	def testPrivateMethodFromOutside(self):
		t = self._Type()
		with self.assertRaises(AccessError) as access_error:
			self.assertEqual(t.private(), "[private value]", "Private method created and defined to '[private value]'")
		self.assertEqual(access_error.exception.type, AccessErrors.PRIVATE)


class TestPrivateMethodFromOutsideWithSameContext(TestCase):
	def setUp(self) -> None:
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				
			@privatemethod
			def private(self):
				return "[private value]"
		
		class B:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
				with this.assertRaises(AccessError) as access_error:
					this.assertEqual(self.a.private(), "[private value]", "Private method created and defined to '[private value]'")
				this.assertEqual(access_error.exception.type, AccessErrors.PRIVATE)
		
		self._Type = B
		return super().setUp()

	def testPrivateMethodFromOutsideWithSameContext(self):
		self._Type()


class TestPrivateMethodFromOutsideWithNotSameContext(TestCase):
	def setUp(self) -> None:
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				
			@privatemethod
			def private(self):
				return "[private value]"
		
		class B:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
		
		self._Type = B
		return super().setUp()

	def testPrivateMethodFromOutsideWithNotSameContext(self):
		t = self._Type()
		with self.assertRaises(AccessError) as access_error:
			self.assertEqual(t.a.private(), "[private value]", "Private method created and defined to '[private value]'")
		self.assertEqual(access_error.exception.type, AccessErrors.PRIVATE)
