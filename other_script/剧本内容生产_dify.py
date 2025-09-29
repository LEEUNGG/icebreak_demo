import requests
import json
import os
import re
from typing import Dict, Any


class DifyWorkflowClient:
    def __init__(self, base_url: str = "http://34.126.166.243/v1", api_key: str = "app-cWDpoYo4oq4je2MoU6s7Fgnp"):
        """
        app-cWDpoYo4oq4je2MoU6s7Fgnp
        Initialize the Dify Workflow Client
        """
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json; charset=utf-8'
        }

    def run_workflow(self, inputs: Dict[str, Any] = None, user: str = "python-client") -> Dict[str, Any]:
        """
        Execute a workflow and return the final result
        """
        if inputs is None:
            inputs = {}

        url = f"{self.base_url}/workflows/run"

        payload = {
            "inputs": inputs,
            "response_mode": "blocking",
            "user": user
        }

        try:
            print(f"Making request to: {url}")
            print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=120
            )

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

            response.encoding = 'utf-8'
            result = response.json()

            print("Request completed successfully!")
            return result

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def save_outputs(self, result: Dict[str, Any], base_path: str = "."):
        try:
            outputs = result["data"]["outputs"]

            raw_name = outputs.get("name", "default_name")
            folder_name = re.sub(r"<think>.*?</think>", "", raw_name, flags=re.S).strip()

            folder_path = os.path.join(base_path, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            print(f"📂 Created/using folder: {folder_path}")

            keys_to_save = ["content", "script", "check", "plot1_prompt", "plot2_prompt", "plot3_prompt"]

            for key in keys_to_save:
                if key in outputs:
                    file_path = os.path.join(folder_path, f"{key}.json")

                    # 特殊处理 script -> plot
                    if key == "script":
                        data_to_save = {"plot": outputs[key]}
                    else:
                        data_to_save = {key: outputs[key]}

                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(data_to_save, f, ensure_ascii=False, indent=2)
                    print(f"✅ Saved: {file_path}")

                    if key == "script":
                        script_raw = outputs[key]

                        script_clean = re.sub(r"^```json\n|\n```$", "", script_raw.strip())

                        try:
                            script_dict = json.loads(script_clean)
                            file_path_read = os.path.join(folder_path, "script_read.json")
                            with open(file_path_read, "w", encoding="utf-8") as f:
                                json.dump(script_dict, f, ensure_ascii=False, indent=2)
                            print(f"📖 Saved readable script: {file_path_read}")
                        except Exception as e:
                            print(f"⚠️ Failed to parse script for script_read.json: {e}")

        except Exception as e:
            print(f"Error while saving outputs: {str(e)}")


    def print_workflow_result(self, result: Dict[str, Any]):
        """
        Print workflow results
        """
        print("\n" + "=" * 50)
        print("WORKFLOW EXECUTION COMPLETED")
        print("=" * 50)
        print("\n🔍 Full Response (Raw JSON):")
        print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    client = DifyWorkflowClient()

    try:
        print("Starting workflow execution...")
        result = client.run_workflow()
        client.print_workflow_result(result)

        client.save_outputs(result)

        return result

    except Exception as e:
        print(f"Error executing workflow: {str(e)}")
        return None


if __name__ == "__main__":
    result = main()
