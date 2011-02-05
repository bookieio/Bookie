import unittest


def init_unittest_suite():

    """Gather all *unittests* into one suite.
    """

    from pydelicioustest import __testcases__ as l1

    suites = []
    for testcase in l1:
        suites.append(unittest.TestLoader().loadTestsFromTestCase(testcase))

    return unittest.TestSuite(suites)


def init_blackboxtest_suite():

    """Gather all *blackbox tests* (API against server) into one suite.
    """

    import blackbox_api
    if not (blackbox_api.usr and blackbox_api.pwd):
        print "Skipping Blackbox API tests"
        return []

    from blackbox_api_unicode import ApiUnicodeTest
    from blackbox_api_latin1 import ApiLatin1Test

    suites = []
    for testcase in (
            # turned off: blackbox_api.TestApiCalls,
            ApiUnicodeTest,
            ApiLatin1Test):
        suites.append(unittest.TestLoader().loadTestsFromTestCase(testcase))

    return unittest.TestSuite(suites)


def test_all():
    """Run all tests.
    """
    print "Starting all tests"

    suites = []

    # Load all suites here
    api_suite = init_blackboxtest_suite()
    if api_suite: # user can choose to skip tests which query the server
        suites.append(api_suite)
    suites.append(init_unittest_suite())

    test(suites)


def test_api():
    """Run unittests only
    """
    print "Starting unittests"

    suites = init_unittest_suite()

    test(suites)


def test_server():
    """Run pydelicious against a server and verify results.
    """
    print "Starting server tests..."

    suites = init_blackboxtest_suite()

    test(suites)


def test(suites):
    main_suite = unittest.TestSuite(suites)
    unittest.TextTestRunner(verbosity=2).run(main_suite)


if __name__ == '__main__': 
    import sys
    if not len(sys.argv)>1: run = 'test_api'
    else: run = sys.argv[1]
    sys.exit(getattr(sys.modules[__name__], run)())
