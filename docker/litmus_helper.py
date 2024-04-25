import requests
import json
import yaml

from jinja2 import PackageLoader, Environment

class LitmusHelper:

    def __init__(self, base_url, user, password):
        self._base_url = base_url
        self._user = user
        self._password = password
        self._session = requests.session()
        self._token = ""
        self.login()
        self._env = Environment(loader=PackageLoader('experiment','templates'))


    def api_get(self, path):
        headers = {
            "Authorization": "Bearer " + self._token
        }
        response = self._session.get(self._base_url + path, headers=headers)
        print(response.status_code)
        return response
    
    def api_post(self, path, data):
        headers = {
            "Authorization": self._token,
            "Content-Type": "application/json"
        }
        response = self._session.post(self._base_url + path, data=json.dumps(data), headers=headers)
        print(response.status_code)
        return response

    def login(self):
        url = f"{self._base_url}/auth/login"
        payload = {
            "username": self._user,
            "password": self._password
        }
        response = self._session.post(url, data=json.dumps(payload))
        if response.status_code == 200:
            self._token = response.json().get("access_token")
        print(response.status_code)

    def _render_experiment_template(self, template_name, params):
        template = self._env.get_template(template_name)
        yaml_str = template.render(params)
        return yaml_str
    
    def _run_workflow(self, template_name, params, weight=0):
        workflow_name = params.get("workflow_name_to_be_replaced")
        experiment_name = params.get("experiment_name_to_be_replaced")

        chaos_yaml_str = self._render_experiment_template(template_name, params)
        data = yaml.load(chaos_yaml_str, Loader=yaml.FullLoader)
        chaos_json_str = json.dumps(data, indent=2)
        print(chaos_json_str)

        path = "/api/query"
        payload = {
            "operationName": "createChaosWorkFlow",
            "variables": {
                "request": {
                    "workflowManifest": chaos_json_str,
                    "cronSyntax": "",
                    "workflowName": workflow_name,
                    "workflowDescription": "Chaos Scenario",
                    "isCustomWorkflow": True,
                    "weightages": [
                        {
                            "experimentName": experiment_name,
                            "weightage": weight
                        }
                    ],
                    "projectID": "55a3b597-eb8f-4a6c-bda8-6cd77a9d91e8",
                    "clusterID": "75da1e99-c09a-439f-a240-cbddce10b65e"
                }
            },
            "query": "mutation createChaosWorkFlow($request: ChaosWorkFlowRequest!) {\n  createChaosWorkFlow(request: $request) {\n    workflowID\n    cronSyntax\n    workflowName\n    workflowDescription\n    isCustomWorkflow\n    __typename\n  }\n}\n"
        }
        print(payload)
        response = self.api_post(path, payload)
    
    def inject_chaos(self, template_name, params, weight):
        self._run_workflow(template_name, params, weight)

    def revert_chaos(self, workflow_name, experiment_name):
        params = {
            "workflow_name_to_be_replaced": workflow_name,
            "experiment_name_to_be_replaced": experiment_name
        }
        self._run_workflow("revert_chaos.yaml", params, 0)
    
    def _debug_chaos(self):
        payload = {
            "operationName": "createChaosWorkFlow",
            "variables": {
                "request": {
                    "workflowManifest": "{\n  \"kind\": \"Workflow\",\n  \"apiVersion\": \"argoproj.io/v1alpha1\",\n  \"metadata\": {\n    \"name\": \"custom-scenario-1691403002-debug\",\n    \"namespace\": \"litmus\",\n    \"creationTimestamp\": null,\n    \"labels\": {\n      \"subject\": \"custom-scenario-1691403002-debug_litmus\"\n    }\n  },\n  \"spec\": {\n    \"templates\": [\n      {\n        \"name\": \"custom-chaos\",\n        \"steps\": [\n          [\n            {\n              \"name\": \"install-chaos-experiments\",\n              \"template\": \"install-chaos-experiments\",\n              \"arguments\": {}\n            }\n          ],\n          [\n            {\n              \"name\": \"pod-delete-yz7\",\n              \"template\": \"pod-delete-yz7\",\n              \"arguments\": {}\n            }\n          ]\n        ]\n      },\n      {\n        \"name\": \"install-chaos-experiments\",\n        \"container\": {\n          \"image\": \"litmuschaos/k8s:latest\",\n          \"command\": [\n            \"sh\",\n            \"-c\"\n          ],\n          \"args\": [\n            \"kubectl apply -f https://hub.litmuschaos.io/api/chaos/2.14.0?file=charts/generic/experiments.yaml -n litmus ; sleep 30\"\n          ]\n        }\n      },\n      {\n        \"name\": \"pod-delete-yz7\",\n        \"inputs\": {\n          \"artifacts\": [\n            {\n              \"name\": \"pod-delete-yz7\",\n              \"path\": \"/tmp/chaosengine-pod-delete-yz7.yaml\",\n              \"raw\": {\n                \"data\": \"apiVersion: litmuschaos.io/v1alpha1\\nkind: ChaosEngine\\nmetadata:\\n  namespace: \\\"litmus\\\"\\n  generateName: pod_delete_yz7\\n  labels:\\n    workflow_run_id: \\\"custom-scenario-1691403002\\\"\\nspec:\\n  appinfo:\\n    appns: datahub\\n    applabel: vsystem.datahub.sap.com/template=vflow-runtime-store\\n    appkind: \\\"\\\"\\n  engineState: active\\n  chaosServiceAccount: litmus-admin\\n  experiments:\\n    - name: pod-delete\\n      spec:\\n        components:\\n          env:\\n            - name: TOTAL_CHAOS_DURATION\\n              value: \\\"30\\\"\\n            - name: CHAOS_INTERVAL\\n              value: \\\"20\\\"\\n            - name: FORCE\\n              value: \\\"false\\\"\\n            - name: PODS_AFFECTED_PERC\\n              value: \\\"\\\"\\n        probe: []\\n\"\n              }\n            }\n          ]\n        },\n        \"outputs\": {},\n        \"metadata\": {\n          \"labels\": {\n            \"weight\": \"10\"\n          }\n        },\n        \"container\": {\n          \"name\": \"\",\n          \"image\": \"litmuschaos/litmus-checker:2.14.0\",\n          \"args\": [\n            \"-file=/tmp/chaosengine-pod-delete-yz7.yaml\",\n            \"-saveName=/tmp/engine-name\"\n          ],\n          \"resources\": {}\n        }\n      }\n    ],\n    \"entrypoint\": \"custom-chaos\",\n    \"arguments\": {\n      \"parameters\": [\n        {\n          \"name\": \"adminModeNamespace\",\n          \"value\": \"litmus\"\n        }\n      ]\n    },\n    \"serviceAccountName\": \"argo-chaos\",\n    \"securityContext\": {\n      \"runAsUser\": 1000,\n      \"runAsNonRoot\": true\n    }\n  }\n}",
                    "cronSyntax": "",
                    "workflowName": "custom-scenario-1691403002-debug",
                    "workflowDescription": "Chaos Scenario",
                    "isCustomWorkflow": True,
                    "weightages": [
                        {
                            "experimentName": "pod_delete_yz7",
                            "weightage": 10
                        }
                    ],
                    "projectID": "55a3b597-eb8f-4a6c-bda8-6cd77a9d91e8",
                    "clusterID": "75da1e99-c09a-439f-a240-cbddce10b65e"
                }
            },
            "query": "mutation createChaosWorkFlow($request: ChaosWorkFlowRequest!) {\n  createChaosWorkFlow(request: $request) {\n    workflowID\n    cronSyntax\n    workflowName\n    workflowDescription\n    isCustomWorkflow\n    __typename\n  }\n}\n"
        }
        print(payload)
        path = "/api/query"
        # response = self.api_post(path, payload)
