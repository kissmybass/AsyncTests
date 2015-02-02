import StringIO
import threading
import unittest
import sys


class AsyncTestOutput(object):

    outputs = {}

    def write(self, message):
        thread_id = self._get_current_thread_id()

        thread_output = self.outputs.get(thread_id, None)
        if not thread_output:
            thread_output = StringIO.StringIO()
            self.outputs[thread_id] = thread_output

        thread_output.write(message)

    def flush_to_stream(self, stream):
        for thread_id, output in self.outputs.items():
            stream.write(output.getvalue())

    def _get_current_thread_id(self):
        # print threading.currentThread().ident
        return threading.currentThread().ident


class AsyncTestSuite(unittest.TestSuite):

    lock = threading.Lock()

    def run(self, result, debug=False):

        if getattr(result, '_testRunEntered', False) is False:
            result._testRunEntered = True

        test_cases = self._tests

        threads = []
        for test_case in test_cases:
            #self._handleModuleFixture(test_case, result)
            thread = threading.Thread(target=self._run_test_case, args=[test_case, result, debug])
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

  #      self._handleModuleTearDown(result)
        result._testRunEntered = False

        if isinstance(result.output, AsyncTestOutput):
            result.output.flush_to_stream(sys.stdout)

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
        self.lock.acquire()
        result._previousTestClass = test.__class__
        self._tearDownPreviousClass(self, result)
        self.lock.release()
