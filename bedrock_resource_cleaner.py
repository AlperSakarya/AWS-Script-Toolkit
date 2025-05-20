#!/usr/bin/env python3
"""
AWS Bedrock Resource Cleaner

Lists and deletes AWS Bedrock resources (knowledge bases, data sources, guardrails, etc.)
Runs once: fetches resources, prompts for comma-separated selection, then deletes without extra confirmation.
Production-ready: minimal logging, no debug statements.
"""

import boto3
import time
from botocore.exceptions import ClientError

class BedrockResourceCleaner:
    def __init__(self):
        session = boto3.session.Session()
        region = session.region_name or "us-east-1"
        supported = ["us-east-1", "us-west-2", "ap-northeast-1", "ap-southeast-2", "eu-central-1"]
        self.region = region if region in supported else "us-east-1"
        self.bedrock = boto3.client("bedrock", region_name=self.region)
        self.agent   = boto3.client("bedrock-agent", region_name=self.region)

    def print_header(self):
        print("\n" + "="*60)
        print("AWS Bedrock Resource Cleaner".center(60))
        print(f"Region: {self.region}".center(60))
        print("="*60)
        print("This will delete selected resources without further confirmation.\n")

    def fetch_all_resources(self):
        resources = []
        idx = 1

        # Guardrails
        try:
            resp = self.bedrock.list_guardrails()
            while True:
                for g in resp.get("guardrails", []):
                    resources.append({
                        "index": idx,
                        "type": "Guardrail",
                        "name": g.get("name", ""),
                        "id":   g["id"],
                        "status": g.get("status", ""),
                        "delete_fn": self.delete_guardrail
                    })
                    idx += 1
                if "nextToken" in resp:
                    resp = self.bedrock.list_guardrails(nextToken=resp["nextToken"])
                else:
                    break
        except ClientError as e:
            print(f"Error listing guardrails: {e}")

        # Knowledge Bases
        try:
            resp = self.agent.list_knowledge_bases()
            while True:
                for kb in resp.get("knowledgeBaseSummaries", []):
                    ds_list = []
                    try:
                        ds_resp = self.agent.list_data_sources(knowledgeBaseId=kb["knowledgeBaseId"])
                        for ds in ds_resp.get("dataSourceSummaries", []):
                            ds_list.append({
                                "id":   ds["dataSourceId"],
                                "name": ds.get("name", "")
                            })
                    except ClientError:
                        pass
                    resources.append({
                        "index": idx,
                        "type": "Knowledge Base",
                        "name": kb.get("name", ""),
                        "id":   kb["knowledgeBaseId"],
                        "status": kb.get("status", ""),
                        "data_sources": ds_list,
                        "delete_fn": self.delete_knowledge_base
                    })
                    idx += 1
                if "nextToken" in resp:
                    resp = self.agent.list_knowledge_bases(nextToken=resp["nextToken"])
                else:
                    break
        except ClientError as e:
            print(f"Error listing knowledge bases: {e}")

        # Model Customization Jobs
        try:
            paginator = self.bedrock.get_paginator("list_model_customization_jobs")
            for page in paginator.paginate():
                for job in page.get("modelCustomizationJobs", []):
                    resources.append({
                        "index": idx,
                        "type": "Model Customization Job",
                        "name": job.get("jobName", ""),
                        "id":   job["jobArn"],
                        "status": job.get("status", ""),
                        "delete_fn": self.delete_model_customization_job
                    })
                    idx += 1
        except ClientError as e:
            print(f"Error listing model customization jobs: {e}")

        # Agents
        try:
            paginator = self.agent.get_paginator("list_agents")
            for page in paginator.paginate():
                for ag in page.get("agents", []):
                    aliases = []
                    try:
                        alias_pag = self.agent.get_paginator("list_agent_aliases")
                        for ap in alias_pag.paginate(agentId=ag["agentId"]):
                            for a in ap.get("agentAliases", []):
                                aliases.append({
                                    "id":   a["agentAliasId"],
                                    "name": a.get("agentAliasName", "")
                                })
                    except ClientError:
                        pass
                    resources.append({
                        "index": idx,
                        "type": "Agent",
                        "name": ag.get("agentName", ""),
                        "id":   ag["agentId"],
                        "status": ag.get("status", ""),
                        "aliases": aliases,
                        "delete_fn": self.delete_agent
                    })
                    idx += 1
        except ClientError as e:
            print(f"Error listing agents: {e}")

        # Provisioned Model Throughputs
        try:
            paginator = self.bedrock.get_paginator("list_provisioned_model_throughputs")
            for page in paginator.paginate():
                for pt in page.get("provisionedModelSummaries", []):
                    resources.append({
                        "index": idx,
                        "type": "Provisioned Model Throughput",
                        "name": pt.get("provisionedModelName", ""),
                        "id":   pt["provisionedModelArn"],
                        "status": pt.get("status", ""),
                        "delete_fn": self.delete_provisioned_model_throughput
                    })
                    idx += 1
        except ClientError as e:
            print(f"Error listing throughputs: {e}")

        return resources

    def display_resources(self, resources):
        if not resources:
            print("No resources found.")
            return
        print(f"\n{'Idx':<5} {'Type':<25} {'Name':<30} {'ID':<30} {'Status'}")
        print("-"*100)
        for r in resources:
            rid = r["id"] if len(r["id"])<=30 else r["id"][:27]+"..."
            print(f"{r['index']:<5} {r['type']:<25} {r['name']:<30} {rid:<30} {r['status']}")

    def update_data_source_deletion_policy(self, kb_id, ds_id, policy="RETAIN"):
        try:
            resp = self.agent.get_data_source(
                knowledgeBaseId=kb_id,
                dataSourceId=ds_id
            )
            ds = resp.get("dataSource", {})
            config = ds.get("dataSourceConfiguration", {})
            payload = {
                "knowledgeBaseId":           kb_id,
                "dataSourceId":              ds_id,
                "name":                      ds.get("name", ""),
                "dataSourceConfiguration":   config,
                "dataDeletionPolicy":        policy
            }
            desc = ds.get("description")
            if desc:
                payload["description"] = desc
            self.agent.update_data_source(**payload)
            return True
        except ClientError as e:
            print(f"Error updating deletion policy for {ds_id}: {e}")
            return False

    def delete_resources(self, resources):
        # delete knowledge bases last
        resources.sort(key=lambda x: x["type"] == "Knowledge Base")
        for r in resources:
            try:
                r["delete_fn"](r)
            except ClientError as e:
                print(f"Error deleting {r['type']} {r['name']}: {e}")

    def delete_guardrail(self, r):
        print(f"Deleting guardrail {r['name']}...")
        self.bedrock.delete_guardrail(guardrailIdentifier=r["id"])
        self._wait_for_guardrail_deletion(r["id"])

    def delete_knowledge_base(self, r):
        kb_id = r["id"]
        print(f"Deleting knowledge base {r['name']}...")
        for ds in r.get("data_sources", []):
            ds_id = ds["id"]
            try:
                resp = self.agent.get_data_source(knowledgeBaseId=kb_id, dataSourceId=ds_id)
                status = resp.get("dataSource", {}).get("status", "")
            except ClientError:
                status = ""
            if status == "DELETE_UNSUCCESSFUL":
                self.update_data_source_deletion_policy(kb_id, ds_id, policy="RETAIN")
            try:
                self.agent.delete_data_source(knowledgeBaseId=kb_id, dataSourceId=ds_id)
                self._wait_for_data_source_deletion(kb_id, ds_id)
            except ClientError as e:
                print(f"Error deleting data source {ds_id}: {e}")
        try:
            self.agent.delete_knowledge_base(knowledgeBaseId=kb_id)
            self._wait_for_knowledge_base_deletion(kb_id)
        except ClientError as e:
            print(f"Error deleting knowledge base {kb_id}: {e}")

    def delete_model_customization_job(self, r):
        print(f"Stopping model customization job {r['name']}...")
        self.bedrock.stop_model_customization_job(jobIdentifier=r["id"])

    def delete_agent(self, r):
        print(f"Deleting agent {r['name']}...")
        for ali in r.get("aliases", []):
            try:
                self.agent.delete_agent_alias(agentId=r["id"], agentAliasId=ali["id"])
                self._wait_for_agent_alias_deletion(r["id"], ali["id"])
            except ClientError as e:
                print(f"Error deleting alias {ali['id']}: {e}")
        try:
            self.agent.delete_agent(agentId=r["id"])
            self._wait_for_agent_deletion(r["id"])
        except ClientError as e:
            print(f"Error deleting agent {r['id']}: {e}")

    def delete_provisioned_model_throughput(self, r):
        print(f"Deleting provisioned model throughput {r['name']}...")
        try:
            self.bedrock.delete_provisioned_model_throughput(provisionedModelId=r["id"])
        except ClientError as e:
            print(f"Error deleting throughput {r['id']}: {e}")

    def _wait_for_guardrail_deletion(self, gid):
        for _ in range(30):
            try:
                if self.bedrock.get_guardrail(guardrailIdentifier=gid)["status"] != "DELETING":
                    return
            except ClientError:
                return
            time.sleep(5)

    def _wait_for_data_source_deletion(self, kb, ds, max_attempts=60, sleep_time=5):
        for _ in range(max_attempts):
            try:
                status = self.agent.get_data_source(knowledgeBaseId=kb, dataSourceId=ds)\
                                     .get("dataSource", {})\
                                     .get("status", "")
                if status not in ("DELETING", "DELETE_UNSUCCESSFUL"):
                    return
            except ClientError:
                return
            time.sleep(sleep_time)

    def _wait_for_knowledge_base_deletion(self, kb, max_attempts=60, sleep_time=5):
        for _ in range(max_attempts):
            try:
                status = self.agent.get_knowledge_base(knowledgeBaseId=kb)\
                                     .get("dataSource", {})\
                                     .get("status", "")
                if status not in ("DELETING", "DELETE_UNSUCCESSFUL"):
                    return
            except ClientError:
                return
            time.sleep(sleep_time)

    def _wait_for_agent_deletion(self, aid):
        for _ in range(30):
            try:
                if self.agent.get_agent(agentId=aid)["status"] != "DELETING":
                    return
            except ClientError:
                return
            time.sleep(5)

    def _wait_for_agent_alias_deletion(self, aid, alias_id):
        for _ in range(30):
            try:
                if self.agent.get_agent_alias(agentId=aid, agentAliasId=alias_id)["status"] != "DELETING":
                    return
            except ClientError:
                return
            time.sleep(5)

    def run(self):
        self.print_header()
        resources = self.fetch_all_resources()
        self.display_resources(resources)
        if not resources:
            return
        selection = input("\nEnter resource numbers to delete (comma-separated) or 'q' to quit: ")
        if selection.lower() == "q":
            return
        try:
            indices = [int(x.strip()) for x in selection.split(",") if x.strip()]
        except ValueError:
            print("Invalid input.")
            return
        to_delete = [r for r in resources if r["index"] in indices]
        if not to_delete:
            print("No valid resources selected.")
            return
        self.delete_resources(to_delete)
        print("\nCompleted.")

if __name__ == "__main__":
    BedrockResourceCleaner().run()
