from Queue import Queue
import StringIO
import threading
import unittest

import sys


class AsyncTeamcityTestResult(object):
    """
    Wraps around TeamcityTestResult, and allows it to be used in multithreaded tests.
    """

    tests = {}

    def __init__(self, test_result):
        self.test_result = test_result

    def __getattr__(self, attr):
        return getattr(self.test_result, attr)


    def addError(self, test, err, *k):
        self._restore_test(test)
        self.test_result.addError(test, err, *k)


    def addFailure(self, test, err, *k):
        self._restore_test(test)
        self.test_result.addFailure(test, err, *k)

    def stopTest(self, test):
        self._restore_test(test)
        self.test_result.stopTest(test)


    def startTest(self, test):
        self.test_result.startTest(test)
        self.tests[test] = { "name": self.test_result.getTestName(test),
                             "start": self.test_result.test_started_datetime}


    def _restore_test(self, test):
        test_record = self.tests[test]
        self.test_result.test_name = test_record["name"]
        self.test_result.test_started_datetime = test_record["start"]



class ThreadBatchedOutput(object):
    """
    Outputs writes from different threads in batches, without mixing them in one common stream.
    """

    def __init__(self, stream):
        self.stream = stream
        self.outputs = {}


    def __getattr__(self, attr):
        return getattr(self.stream, attr)


    def write(self, message):
        thread_id = _get_current_thread_id()

        thread_output = self.outputs.get(thread_id, None)
        if not thread_output:
            thread_output = StringIO.StringIO()
            self.outputs[thread_id] = thread_output

        thread_output.write(message)
        thread_output.flush()


    def writeln(self, arg=None):
        """
        This is an extension method used by test suits and test cases.
        """
        if arg:
            self.write(arg)
        self.write('\n') # text-mode streams translate to \r\n if needed


    def flush(self):
        pass


    def flush_thread(self, thread_ident):
        output = self.outputs.pop(thread_ident, None)
        if output:
            self.stream.write(output.getvalue())
            self.stream.flush()


    def flush_all_threads(self):
        for thread_id, output in self.outputs.items():
            self.stream.write(output.getvalue())
        self.stream.flush()
        self.outputs = {}



class AsyncTestSuite(unittest.TestSuite):

    lock = threading.Lock()

    def run(self, result, debug=False):

        if getattr(result, '_testRunEntered', False) is False:
            result._testRunEntered = True

        test_cases = self._tests

        threads = []
        _stdout = sys.stdout
        _stderr = sys.stderr

        if is_teamcity_result(result):
            _stream = result.output
        else:
            _stream = result.stream

        batched_stream = ThreadBatchedOutput(_stream)
        try:
            # here we substitute standard output with thread-batched version,
            # so that our tests prints will be in one peace
            if is_teamcity_result(result):
                result.output = batched_stream
                result.messages.output = batched_stream
                result = AsyncTeamcityTestResult(result)
            else:
                result.stream = batched_stream

            sys.stdout = batched_stream
            sys.stderr = batched_stream

            wait_queue = Queue()

            for test_case in test_cases:
                #self._handleModuleFixture(test_case, result)
                thread = threading.Thread(target=self._run_test_case, args=[wait_queue, test_case, result, debug])
                thread.start()
                threads.append(thread)

            for _ in threads:
                thread_id = wait_queue.get()
                batched_stream.flush_thread(thread_id)


      #      self._handleModuleTearDown(result)
            result._testRunEntered = False

            batched_stream.flush_all_threads()

        finally:
            if is_teamcity_result(result):
                result.output = _stream
                result.messages.output =_stream
            else:
                result.stream = _stream
            sys.stdout = _stdout
            sys.stderr = _stderr

        return result



    def _run_test_case(self, wait_queue, test, result, debug):

        try:
            self._handleClassSetUp(test, result)
            result._previousTestClass = test.__class__

            if (getattr(test.__class__, '_classSetupFailed', False) or
                    getattr(result, '_moduleSetUpFailed', False)):
                return

            if not debug:
                test(result)
            else:
                test.debug()

            # this is hack, since we pass self as a current TestCase, so that test's classes change will be detected.
            self.lock.acquire()
            try:
                result._previousTestClass = test.__class__
                self._tearDownPreviousClass(self, result)
            finally:
                self.lock.release()

        finally:
            wait_queue.put( _get_current_thread_id() )



def _get_current_thread_id():
    return threading.currentThread().ident



def is_teamcity_result(result):
    return result.__class__.__name__ in ("TeamcityTestResult", "AsyncTeamcityTestResult")