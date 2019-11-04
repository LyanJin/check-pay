from app.libs.string_kit import CharOp, RandomString, StringParser, PhoneNumberParser, StringUtils
from tests import TestNoneAppBase


class StringToolsTest(TestNoneAppBase):
    ENABLE_PRINT = False

    def test_random_str(self):
        for l in [2, 32, 64, 128]:
            for op in [CharOp.U, CharOp.L, CharOp.N, CharOp.S]:
                s = RandomString.gen_random_str(l, op)
                self.print(op, l, s)
                assert len(s) == l
                if op == CharOp.U:
                    assert s.isupper()
                if op == CharOp.L:
                    assert s.islower()
                if op == CharOp.N:
                    assert s.isnumeric()
                if op == CharOp.S:
                    assert set(RandomString.specials).issuperset(set([c for c in s]))

            op = [CharOp.U, CharOp.L, CharOp.N, CharOp.S]
            s = RandomString.gen_random_str(l, op)
            self.print(op, l, s)
            assert len(s) == l
            assert s.isascii()

            op = [CharOp.U, CharOp.L, CharOp.N, ]
            s = RandomString.gen_random_str(l, op)
            self.print(op, l, s)
            assert len(s) == l
            assert s.isalnum()

            op = [CharOp.U, CharOp.L, ]
            s = RandomString.gen_random_str(l, op)
            self.print(op, l, s)
            assert len(s) == l
            assert s.isalpha()

    def test_domain_string(self):
        domains = ['video.qq.com', 'doc111.google.com', 'xxx.yyy.zzz.com']
        domain_str = StringParser().join(domains)
        sp_domains = StringParser().split(domain_str)
        self.assertEqual(domains, sp_domains)

    def test_parse_int_string(self):
        int_list = [1222, 2342342, 299999]
        _str = StringParser(to_type=int).join(int_list)
        sp_list = StringParser(to_type=int).split(_str)
        self.assertEqual(int_list, sp_list)

    def test_invalid_number(self):
        self.assertTrue(PhoneNumberParser.is_valid_number("+639166630027"))
        self.assertTrue(PhoneNumberParser.is_valid_number("+8618975532009"))
        self.assertFalse(PhoneNumberParser.is_valid_number("+8633234"))

    def test_md5_string(self):
        s = RandomString.random_md5_string()
        self.assertEqual(len(s), 32)
        i = StringUtils.string_to_int16(s)
        self.assertIsInstance(i, int)

    def test_hide_number(self):
        b = 6
        e = -4

        s = "+8618975532009"
        h_s = PhoneNumberParser.hide_number(s)
        print(s, h_s)
        self.assertEqual('+86189', h_s[:b])
        self.assertEqual('****', h_s[b:e])
        self.assertEqual('2009', h_s[e:])

        s = "+639166630027"
        h_s = PhoneNumberParser.hide_number(s)
        print(s, h_s)
        self.assertEqual('+63916', h_s[:b])
        self.assertEqual('****', h_s[b:e])
        self.assertEqual('0027', h_s[e:])
