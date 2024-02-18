from unittest import TestCase

from pyobject import Object, publicmethod


class TestPublicFromInside(TestCase):
	def testGetPublicFromInside(self):
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.public_attribute("public", "[public value]")
				this.assertEqual(self.public, "[public value]", "Pulic attribute created and defined to '[public value]'")

		A()
	
	def testSetPublicFromInside(self):
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.public_attribute("public", "[public value]")
				this.assertEqual(self.public, "[public value]", "Pulic attribute created and defined to '[public value]'")
				self.public = "[public value changed]"
				this.assertEqual(self.public, "[public value changed]", "Public value changed")

		A()


class TestPublicFromInsideWithChild(TestCase):
	def setUp(self) -> None:
		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.public_attribute("public", "[public value]")
		self._Type = A
		return super().setUp()

	def testGetPublicFromInsideWithChild(self):
		this = self

		class B(self._Type):
			def __init__(self) -> None:
				super().__init__()
				this.assertEqual(self.public, "[public value]", "Pulic attribute created and defined to '[public value]'")

		B()
	
	def testSetPublicFromInsideWithChild(self):
		this = self

		class B(self._Type):
			def __init__(self) -> None:
				super().__init__()
				this.assertEqual(self.public, "[public value]", "Pulic attribute created and defined to '[public value]'")
				self.public = "[public value changed]"
				this.assertEqual(self.public, "[public value changed]", "Public value changed")

		B()


class TestPublicFromOutside(TestCase):
	def setUp(self) -> None:
		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.public_attribute("public", "[public value]")
		self._Type = A
		return super().setUp()

	def testGetPublicFromOutside(self):
		t = self._Type()
		self.assertEqual(t.public, "[public value]", "Pulic attribute created and defined to '[public value]'")
	
	def testSetPublicFromOutside(self):
		t = self._Type()
		self.assertEqual(t.public, "[public value]", "Pulic attribute created and defined to '[public value]'")
		t.public = "[public value changed]"
		self.assertEqual(t.public, "[public value changed]", "Public value changed")


class TestPublicFromOutsideWithSameContext(TestCase):
	def setUp(self) -> None:
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.public_attribute("public", "[public value]")
		
		class Get:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
				this.assertEqual(self.a.public, "[public value]", "Pulic attribute created and defined to '[public value]'")
		
		class Set:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
				this.assertEqual(self.a.public, "[public value]", "Pulic attribute created and defined to '[public value]'")
				self.a.public = "[public value changed]"
				this.assertEqual(self.a.public, "[public value changed]", "Public value changed")
		
		self._TypeGet = Get
		self._TypeSet = Set
		return super().setUp()

	def testGetPublicFromOutsideWithSameContext(self):
		self._TypeGet()
	
	def testSetPublicFromOutsideWithSameContext(self):
		t = self._TypeSet()


class TestPublicFromOutsideWithNotSameContext(TestCase):
	def setUp(self) -> None:
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.public_attribute("public", "[public value]")
		
		class B:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
		
		self._Type = B
		return super().setUp()

	def testGetPublicFromOutsideWithNotSameContext(self):
		t = self._Type()
		self.assertEqual(t.a.public, "[public value]", "Pulic attribute created and defined to '[public value]'")
	
	def testSetPublicFromOutsideWithNotSameContext(self):
		t = self._Type()
		self.assertEqual(t.a.public, "[public value]", "Pulic attribute created and defined to '[public value]'")
		t.a.public = "[public value changed]"
		self.assertEqual(t.a.public, "[public value changed]", "Public value changed")


class TestPublicMethodFromInside(TestCase):
	def testPublicMethodFromInside(self):
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				this.assertEqual(self.public(), "[public value]", "Public method created and defined to '[public value]'")
			
			@publicmethod
			def public(self):
				return "[public value]"

		A()


class TestPublicMethodFromInsideWithChild(TestCase):
	def setUp(self) -> None:
		class A(Object):
			def __init__(self) -> None:
				super().__init__()
			
			@publicmethod
			def public(self):
				return "[public value]"
			
		self._Type = A
		return super().setUp()

	def testPublicMethodFromInsideWithChild(self):
		this = self

		class B(self._Type):
			def __init__(self) -> None:
				super().__init__()
				this.assertEqual(self.public(), "[public value]", "Public method created and defined to '[public value]'")

		B()


class TestPublicMethodFromOutside(TestCase):
	def setUp(self) -> None:
		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				
			@publicmethod
			def public(self):
				return "[public value]"
			
		self._Type = A
		return super().setUp()

	def testPublicMethodFromOutside(self):
		t = self._Type()
		self.assertEqual(t.public(), "[public value]", "Public method created and defined to '[public value]'")


class TestPublicMethodFromOutsideWithSameContext(TestCase):
	def setUp(self) -> None:
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				
			@publicmethod
			def public(self):
				return "[public value]"
		
		class B:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
				this.assertEqual(self.a.public(), "[public value]", "Public method created and defined to '[public value]'")
		
		self._Type = B
		return super().setUp()

	def testPublicMethodFromOutsideWithSameContext(self):
		self._Type()


class TestPublicMethodFromOutsideWithNotSameContext(TestCase):
	def setUp(self) -> None:
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				
			@publicmethod
			def public(self):
				return "[public value]"
		
		class B:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
		
		self._Type = B
		return super().setUp()

	def testPublicMethodFromOutsideWithNotSameContext(self):
		t = self._Type()
		self.assertEqual(t.a.public(), "[public value]", "Public method created and defined to '[public value]'")
