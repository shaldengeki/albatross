from nose.tools import *
import albatross

class testAlbatrossClass(object):
  @classmethod
  def setUpClass(self):
    self.testString = """<a href="test.php?id=58&topic=23">This is a test<a href="test.php?id=62&topic=13"> string for getEnclosed</a>String</a>.\n<span class='secondLine'>This is the second line of the test string.\nThis is the third line!</span>\n<span></span>"""
  def testGetNonexistentEnclosedString(self):
    assert albatross.getEnclosedString(self.testString, r"<span>", "this ending doesn't exist") == False
    assert albatross.getEnclosedString(self.testString, r"This beginning doesn't exist", "</span>") == False

  def testGetBeginningEndEnclosedString(self):
    print "Start: " + str(albatross.getEnclosedString(self.testString, "<span>", ""))
    assert albatross.getEnclosedString(self.testString, "<span>", "") == "</span>"
    print "Start: " + str(albatross.getEnclosedString(self.testString, "", "</a>"))
    assert albatross.getEnclosedString(self.testString, "", "</a>") == """<a href="test.php?id=58&topic=23">This is a test<a href="test.php?id=62&topic=13"> string for getEnclosed"""

  def testGetEmptyEnclosedString(self):
    assert albatross.getEnclosedString(self.testString, "<span>", "</span>") == ""

  def testGetNormalEnclosedString(self):
    assert albatross.getEnclosedString(self.testString, r'">', r'<a') == "This is a test"
    assert albatross.getEnclosedString(self.testString, r"""<a href="test.php\?id=[0-9]+&topic=[0-9]+">""", r"</a>") == """This is a test<a href="test.php?id=62&topic=13"> string for getEnclosed"""

  def testGetGreedyEnclosedString(self):
    assert albatross.getEnclosedString(self.testString, r"""<a href="test.php\?id=[0-9]+&topic=[0-9]+">""", r"</a>", greedy=True) == """This is a test<a href="test.php?id=62&topic=13"> string for getEnclosed</a>String"""

  def testGetMultilineEnclosedString(self):
    assert albatross.getEnclosedString(self.testString, r"""<span class='secondLine'>""", r"</span>", multiLine=True) == """This is the second line of the test string.
This is the third line!"""
