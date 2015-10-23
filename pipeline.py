"""Define a pipeline subsystem as per the Pipes and Filters pattern."""
import threading
from Queue import Queue, Empty

class Pipe(object):
    """Define a thread-safe pipe object to transfer data between filters."""
    def __init__(self):
        """Create a Queue and an event to synchronize the filters."""
        self.queue = Queue()
        self.register = threading.Event()

    def open_register(self):
        """Declare that the pipe is open. Simply sets the register event."""
        self.register.set()

    def close_register(self):
        """Declare that the pipe is closed. Simply clears the register event."""
        self.register.clear()

    def push(self, data_packet):
        """Insert data into the pipe."""
        self.queue.put_nowait(data_packet)

    def pull(self):
        """Return data from the pipe."""
        return self.queue.get_nowait()

    def has_flow(self):
        """Return True if there are data items in the pipe."""
        return not self.queue.empty()

    def is_open(self):
        """Return True if the register event is set."""
        return self.register.is_set()


class Filter(threading.Thread):
    """Define a Filter that can be coupled to a Pipeline."""
    def __init__(self, filter_process):
        """Set up the Filter fields. Meant to be called first by subclasses."""
        threading.Thread.__init__(self)
        self.filter_process = filter_process
        self.in_pipe = None
        self.out_pipe = None

    def run(self):
        """
            Process items until the pipe closes or there are still
            items in the pipe.
            Close the pipe when done.
        """
        while self.in_pipe.is_open() or self.in_pipe.has_flow():
            try:
                input_data_packet = self.in_pipe.pull()
                output_data_packet = self.filter_process(input_data_packet)
                self.out_pipe.push(output_data_packet)
            except Empty:
                pass
        self.out_pipe.close_register()

    def set_input_pipe(self, input_pipe):
        """Set the input pipe. The data supplier."""
        self.in_pipe = input_pipe

    def set_output_pipe(self, output_pipe):
        """Set the output pipe. The data consumer."""
        self.out_pipe = output_pipe


class DataSource(Filter):
    """Provide data for the pipeline."""
    def __init__(self):
        Filter.__init__(self)

    def run(self):
        while self.has_next():
            data_packet = self.next()
            self.out_pipe.push(data_packet)

    def has_next(self):
        """Not implemented and meant to be overridden."""
        raise NotImplementedError

    def next(self):
        """Not implemented and meant to be overridden."""
        raise NotImplementedError


class Pipeline(object):
    """Define the structure of a multi-threaded processing pipeline."""
    def __init__(self):
        self.filters = []

    def connect(self, filter_component):
        """Connect a filter to end of the pipeline."""
        self.__connect(self.filters[-1], filter_component)

    @staticmethod
    def __connect(input_filter, output_filter):
        """Join two filters through a pipe."""
        pipe = Pipe()
        input_filter.set_output_pipe(pipe)
        output_filter.set_input_pipe(pipe)

    def set_data_source(self, data_source):
        """Set the data source for the pipeline."""
        self.filters = [data_source] + self.filters
        self.__connect(self.filters[0], self.filters[1])

    def set_data_sink(self, data_sink):
        """Set the data sink for the pipeline."""
        self.filters.append(data_sink)
        self.__connect(self.filters[-2], self.filters[-1])

    def run(self):
        """Execute each filter and wait for them to finish."""
        for filter_component in self.filters:
            filter_component.run()
        for filter_component in self.filters:
            filter_component.join()
