import os

from typing import Any, Dict, List, Text, Union, Tuple
from typing import Callable as tCallable

from . import load_tool
from . import main
from . import workflow
from .process import Process


class WorkflowStatus(Exception):
    def __init__(self,
                 out,    # type: Union[Dict[Text, Any], List[Dict[Text, Any]], None]
                 status  # type: Text
                 ):  # type: (...) -> None
        super(WorkflowStatus, self).__init__("Completed %s" % status)
        self.out = out
        self.status = status


class Callable(object):
    def __init__(self, t, factory):  # type: (Process, Factory) -> None
        self.t = t
        self.factory = factory

    def __call__(self, **kwargs):
        # type: (**Any) -> Union[Dict[Text, Any], List[Dict[Text, Any]], None]
        execkwargs = self.factory.execkwargs.copy()
        execkwargs["basedir"] = os.getcwd()
        out, status = self.factory.executor(self.t, kwargs, **execkwargs)
        if status != "success":
            raise WorkflowStatus(out, status)
        else:
            return out


class Factory(object):
    def __init__(self,
                 makeTool=workflow.defaultMakeTool,  # type: tCallable[[Any], Process]
                 # should be tCallable[[Dict[Text, Any], Any], Process] ?
                 executor=main.single_job_executor,  # type: tCallable[..., Tuple[Union[Dict[Text, Any], List[Dict[Text, Any]], None], Text]]
                 **execkwargs  # type: Any
                 ):
        # type: (...) -> None
        self.makeTool = makeTool
        self.executor = executor
        self.execkwargs = execkwargs

    def make(self, cwl):  # type: (Union[Text, Dict[Text, Any]]) -> Callable
        """Instantiate a CWL object from a CWl document."""
        load = load_tool.load_tool(cwl, self.makeTool)
        if isinstance(load, int):
            raise Exception("Error loading tool")
        return Callable(load, self)
