import unittest
from logscope import parse_line, normalized_message

class LogScopeTests(unittest.TestCase):
    def test_parse(self):
        r=parse_line(4,"2026-11-23T12:00:00Z ERROR [api] timeout")
        self.assertEqual(r.level,"ERROR"); self.assertEqual(r.source,"api")
    def test_unknown_is_retained(self):
        self.assertEqual(parse_line(1,"unexpected").level,"UNKNOWN")
    def test_normalization(self):
        self.assertEqual(normalized_message("failed after 42ms"),"failed after <n>ms")

if __name__=="__main__": unittest.main()
