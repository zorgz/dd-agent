# 3rd p
import pywintypes
from win32com.client import Dispatch

# project
from checks import AgentCheck


class InvalidWMIQuery(Exception):
    """
    Invalid WMI Query.
    """
    pass


class WMIAlternativeCheck(AgentCheck):
    """
    An alternative to Datadog agent WMI check.

    Windows only.
    """
    def __init__(self, name, init_config, agentConfig, instances):
        AgentCheck.__init__(self, name, init_config, agentConfig, instances)
        self.wmi_conns = {}

    def check(self, instance):
        """
        Fetch WMI metrics.
        """
        # Connexion information
        host = instance.get('host', "localhost")
        namespace = instance.get('namespace', "root\\cimv2")

        w = self._get_wmi_conn(host, namespace)

        # WMI specifications
        wmi_class = instance.get('class')
        metrics = instance.get('metrics')
        properties = map(lambda x: x[0], metrics)

        #
        results = self._query_wmi(w, wmi_class, properties)

    def _get_wmi_conn(self, host, namespace):
        """
        Create and cache WMI connexions.
        """
        key = "{0}:{1}".format(host, namespace)
        if key not in self.wmi_conns:
            server = Dispatch("WbemScripting.SWbemLocator")
            self.wmi_conns[key] = server.ConnectServer(host, namespace)
        return self.wmi_conns[key]

    def _query_wmi(self, w, wmi_class, wmi_properties):
        """
        Query WMI using WMI Query Language (WQL).
        """
        formated_wmi_properties = ",".join(wmi_properties)
        wql = "Select {0} from {1}".format(formated_wmi_properties, wmi_class)
        self.log.debug(u"Querying WMI: {0}".format(wql))

        results = w.ExecQuery(wql)

        try:
            self._raise_for_invalid(results)
        except InvalidWMIQuery:
            self.log.warning(u"Invalid WMI query: {0}".format(wql))
            res = []

        return res

    def _extract_metrics(self, results):
        """
        Extract, parse metrics from WMI query output and submit them.
        """
        for res in results:
            for wmi_property in res.Properties_:
                print wmi_property.Name, wmi_property.Value

    @staticmethod
    def _raise_for_invalid(result):
        """
        Raise an InvalidWMIQuery when the result returned by the WMI is invalid.
        """
        try:
            len(result)
        except (pywintypes.com_error):
            raise InvalidWMIQuery
