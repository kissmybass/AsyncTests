import StringIO
import threading
import unittest

import sys



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
        thread_id = self._get_current_thread_id()

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


    def _get_current_thread_id(self):
        return threading.currentThread().ident



class AsyncTestSuite(unittest.TestSuite):

    lock = threading.Lock()

    def run(self, result, debug=False):

        if getattr(result, '_testRunEntered', False) is False:
            result._testRunEntered = True

        test_cases = self._tests

        threads = []
        _stdout = sys.stdout
        _stream = result.stream

        batched_stream = ThreadBatchedOutput(_stream)
        try:
            # here we substitute standard output with thread-batched version,
            # so that our tests prints will be in one peace
            result.stream = batched_stream
            sys.stdout = batched_stream

            for test_case in test_cases:
                #self._handleModuleFixture(test_case, result)
                thread = threading.Thread(target=self._run_test_case, args=[test_case, result, debug])
                thread.start()
                threads.append(thread)

            for t in threads:
                t.join()
                batched_stream.flush_thread(t.ident)

      #      self._handleModuleTearDown(result)
            result._testRunEntered = False

            batched_stream.flush_all_threads()

        finally:
            result.stream = _stream
            sys.stdout = _stdout

        return result



    def _run_test_case(self, test, result, debug):

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
        try:
            self.lock.acquire()
            result._previousTestClass = test.__class__
            self._tearDownPreviousClass(self, result)
        finally:
            self.lock.release()
