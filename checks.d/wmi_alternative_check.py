'''
Windows Only.

An alternative to Datadog agent WMI check.
'''
# 3rd p
import pywintypes
from win32com.client import Dispatch

# project
from checks import AgentCheck


def WMIAlternativeCheck(AgentCheck):
    def __init__(self, name, init_config, agentConfig, instances):
        AgentCheck.__init__(self, name, init_config, agentConfig, instances)
        self.wmi_conns = {}

    def _get_wmi_conn(self, host, namespace):
        """
        Cache connexions
        """
        key = "{0}:{1}".format(host, namespace)
        if key not in self.wmi_conns:
            server = Dispatch("WbemScripting.SWbemLocator")
            self.wmi_conns[key] = server.ConnectServer(host, namespace)
        return self.wmi_conns[key]

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

    def _query_wmi(self, w, wmi_class, wmi_properties):
        """

        """
        formated_wmi_properties = ",".join(wmi_properties)
        wql = "Select {0} from {1}".format(formated_wmi_properties, wmi_class)
        self.log.debug(u"Querying WMI: {0}".format(wql))

        res = w.ExecQuery(wql)


        return res

    @staticmethod
    def _raise_for_invalid(self, result):
        """

        """
        try:
            len(result)
            return True
        except (pywintypes.com_error):
            self.log.warning(u"Invalid w query")
            return False

    def _extract_metrics(self):
        """
        Extract, parse metrics from WMI query output and submit.
        """
        pass


