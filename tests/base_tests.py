from nose.tools import *
import albatross

class testBaseClass(object):
  @classmethod
  def setUpClass(self):
    class BaseChild(albatross.Base):
      def __init__(self):
        self._foo = None
      def load(self):
        self._foo = "set"
      @property
      @albatross.loadable
      def foo(self):
        return self._foo
    self.obj = BaseChild()

  @raises(AttributeError)
  def testInvalidAttribute(self):
    self.obj.doesnt_exist

  def testValidAttribute(self):
    assert self.obj.foo == "set"