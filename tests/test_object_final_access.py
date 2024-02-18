from unittest import TestCase

from pyobject import AccessError, AccessErrors, Object


class TestPublicFinalFromInside(TestCase):
	def testGetPublicFinalFromInside(self):
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.public_attribute("public_final", "[public_final value]", True)
				this.assertEqual(self.public_final, "[public_final value]", "Pulic final attribute created and defined to '[public_final value]'")

		A()
	
	def testSetPublicFinalFromInside(self):
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.public_attribute("public_final", "[public_final value]", True)
				this.assertEqual(self.public_final, "[public_final value]", "Pulic final attribute created and defined to '[public_final value]'")
				self.public_final = "[public_final value changed]"
				this.assertEqual(self.public_final, "[public_final value changed]", "public_final value changed")

		with self.assertRaises(AccessError) as access_error:
			A()
		self.assertEqual(access_error.exception.type, AccessErrors.FINAL)


class TestPublicFinalFromInsideWithChild(TestCase):
	def setUp(self) -> None:
		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.public_attribute("public_final", "[public_final value]", True)
		self._Type = A
		return super().setUp()

	def testGetPublicFinalFromInsideWithChild(self):
		this = self

		class B(self._Type):
			def __init__(self) -> None:
				super().__init__()
				this.assertEqual(self.public_final, "[public_final value]", "Pulic final attribute created and defined to '[public_final value]'")

		B()
	
	def testSetPublicFinalFromInsideWithChild(self):
		this = self

		class B(self._Type):
			def __init__(self) -> None:
				super().__init__()
				this.assertEqual(self.public_final, "[public_final value]", "Pulic final attribute created and defined to '[public_final value]'")
				self.public_final = "[public_final value changed]"
				this.assertEqual(self.public_final, "[public_final value changed]", "public_final value changed")

		with self.assertRaises(AccessError) as access_error:
			B()
		self.assertEqual(access_error.exception.type, AccessErrors.FINAL)


class TestPublicFinalFromOutside(TestCase):
	def setUp(self) -> None:
		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.public_attribute("public_final", "[public_final value]", True)
		self._Type = A
		return super().setUp()

	def testGetPublicFinalFromOutside(self):
		t = self._Type()
		self.assertEqual(t.public_final, "[public_final value]", "Pulic final attribute created and defined to '[public_final value]'")
	
	def testSetPublicFinalFromOutside(self):
		with self.assertRaises(AccessError) as access_error:
			t = self._Type()
			self.assertEqual(t.public_final, "[public_final value]", "Pulic final attribute created and defined to '[public_final value]'")
			t.public_final = "[public_final value changed]"
		self.assertEqual(t.public_final, "[public_final value]", "public_final value not changed")
		self.assertEqual(access_error.exception.type, AccessErrors.FINAL)


class TestPublicFinalFromOutsideWithNotSameContext(TestCase):
	def setUp(self) -> None:
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.public_attribute("public_final", "[public_final value]", True)
		
		class B:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
		
		self._Type = B
		return super().setUp()

	def testGetPublicFinalFromOutsideWithNotSameContext(self):
		t = self._Type()
		self.assertEqual(t.a.public_final, "[public_final value]", "Pulic final attribute created and defined to '[public_final value]'")
	
	def testSetPublicFinalFromOutsideWithNotSameContext(self):
		t = self._Type()
		with self.assertRaises(AccessError) as access_error:
			self.assertEqual(t.a.public_final, "[public_final value]", "Pulic final attribute created and defined to '[public_final value]'")
			t.a.public_final = "[public_final value changed]"
		self.assertEqual(t.a.public_final, "[public_final value]", "Public final value not changed")
		self.assertEqual(access_error.exception.type, AccessErrors.FINAL)


class TestPublicFinalFromOutsideWithSameContext(TestCase):
	def setUp(self) -> None:
		this = self

		class A(Object):
			def __init__(self) -> None:
				super().__init__()
				self.public_attribute("public_final", "[public_final value]", True)
		
		class Get:
			def __init__(self) -> None:
				super().__init__()
				self.a = A()
				this.assertEqual(self.a.public_final, "[public_final value]", "Public final attribute created and defined to '[public_final value]'")
		
		class Set:
			def __init__(self) -> None:
				super().__init__()
				with this.assertRaises(AccessError) as access_error:
					self.a = A()
					this.assertEqual(self.a.public_final, "[public_final value]", "Public final attribute created and defined to '[public_final value]'")
					self.a.public_final = "[public value changed]"
				this.assertEqual(self.a.public_final, "[public_final value]", "Public final value not changed")
				this.assertEqual(access_error.exception.type, AccessErrors.FINAL)
		
		self._TypeGet = Get
		self._TypeSet = Set
		return super().setUp()

	def testGetPublicFinalFromOutsideWithSameContext(self):
		self._TypeGet()
	
	def testSetPublicFinalFromOutsideWithSameContext(self):
		self._TypeSet()
