import unittest
import os

from di_qa_e2e.cluster import Cluster
from di_qa_e2e.models.graph import GraphStatus
from di_qa_e2e.connections.connection_data import ConnectionData

from litmus_helper import LitmusHelper


class ChaosTest(unittest.TestCase):
    
    CLUSTER = os.getenv("CLUSTER", "CHAOS")
    
    @classmethod
    def setUpClass(cls):
        # connect to cluster
        connectiondata_path = os.path.join(os.path.dirname(__file__), 'connectiondata')

        connection_data = ConnectionData.for_cluster(cls.CLUSTER, connectiondata_path)
        cls.cluster: Cluster = Cluster.connect_to(connection_data)
        cls.litmus_api = LitmusHelper("https://litmus.ingress.dh-2xvdwr3o.dh-testing.shoot.canary.k8s-hana.ondemand.com", "admin", "litmus")

    def setUp(self) -> None:
        self._workflow_name = ""
        self._experiment_name = ""
    
    def tearDown(self) -> None:
        self.litmus_api.revert_chaos(self._workflow_name, self._experiment_name)

    def test_inject_chaos_by_api(self):
        # get graph util
        graphs = self.cluster.modeler.graphs
        
        # stop graph if chaos graph is running
        graph_full_name = "com.sap.demo.datagenerator"
        graph_run_name = "chaos-graph"
        executions = graphs.get_executions(run_name=graph_run_name)
        for execution in executions:
            if execution.status == GraphStatus.RUNNING:
                execution.stop()
            
        # run the graph
        execution = graphs.run_graph(graph_full_name, graph_run_name)
        execution.wait_until_running()


        template_name = 'pod_delete.yaml'
        self._workflow_name = "call-chaos-in-tf-debug"
        self._experiment_name = "pod-delete-in-tf-debug"
        params = {
            "workflow_name_to_be_replaced": self._workflow_name,
            "experiment_name_to_be_replaced": self._experiment_name,
            "service_namespace_to_be_replaced": "datahub",
            "service_applabel_to_be_replaced": "vsystem.datahub.sap.com/template=vflow-runtime-store",
            "duration_to_be_replaced": 30
        }
        self.litmus_api.inject_chaos(template_name, params, 10)
    
    @unittest.skip("Ignore")
    def test_start_graph_keep_running_if_vflow_service_pod_delete(self):
        # get graph util
        graphs = self.cluster.modeler.graphs
        
        # stop graph if chaos graph is running
        graph_full_name = "com.sap.demo.datagenerator"
        graph_run_name = "chaos-graph"
        executions = graphs.get_executions(run_name=graph_run_name)
        for execution in executions:
            if execution.status == GraphStatus.RUNNING:
                execution.stop()
            
        # run the graph
        execution = graphs.run_graph(graph_full_name, graph_run_name)
        execution.wait_until_running()
        
    # @unittest.skip("Ignore")
    def test_validation_graph_keep_running_if_vflow_service_pod_delete(self):
        # get graph util
        graphs = self.cluster.modeler.graphs
        
        # check graph status
        graph_run_name = "chaos-graph"
        executions = graphs.get_executions(run_name=graph_run_name)
        actual_status = executions[0].status if len(executions) > 0 else None
        self.assertEqual(GraphStatus.RUNNING, actual_status, 
                         f"The graph should keep running. But the graph is {actual_status}.")

