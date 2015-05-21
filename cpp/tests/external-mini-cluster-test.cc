// Copyright 2012 Cloudera Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <gtest/gtest.h>

#include "external-mini-cluster.h"
#include "test-common.h"
#include "subprocess.h"

using namespace boost;
using namespace std;

namespace recordservice {

TEST(ExternalMiniCluster, Basic) {
  ExternalMiniCluster cluster;
  ExternalMiniCluster::Statestored* statestored;
  ExternalMiniCluster::Catalogd* catalogd;

  bool result = cluster.StartStatestored(&statestored);
  EXPECT_TRUE(result);
  EXPECT_TRUE(statestored != NULL);

  result = cluster.StartCatalogd(&catalogd);
  EXPECT_TRUE(result);
  EXPECT_TRUE(catalogd != NULL);

  ExternalMiniCluster::Impalad* recordservice_planner = NULL;

  for (int i = 0; i < 3; ++i) {
    ExternalMiniCluster::Impalad* impalad;
    result = cluster.StartImpalad(true, true, &impalad);
    EXPECT_TRUE(result);
    EXPECT_TRUE(impalad != NULL);
    if (recordservice_planner == NULL) recordservice_planner = impalad;
  }

  // TODO: remove this. This is the time it takes for the daemon to start up
  // and accept connections.
  sleep(10);

  // Run a simple request.
  shared_ptr<RecordServicePlannerClient> planner = CreatePlannerConnection(
      "localhost", recordservice_planner->recordservice_planner_port());

  TPlanRequestResult plan_result;
  TPlanRequestParams plan_params;
  plan_params.request_type = TRequestType::Sql;
  plan_params.__set_sql_stmt("select n_name from tpch.nation");
  planner->PlanRequest(plan_result, plan_params);
  EXPECT_EQ(plan_result.tasks.size(), 1);

  shared_ptr<RecordServiceWorkerClient> worker = CreateWorkerConnection(
      plan_result.tasks[0].local_hosts[0].hostname.c_str(),
      plan_result.tasks[0].local_hosts[0].port);

  vector<string> data = FetchAllStrings(worker.get(), plan_result.tasks[0].task);
  EXPECT_EQ(data.size(), 25);
}

}

int main(int argc, char **argv) {
  const char* env = getenv("RUN_MINI_CLUSTER_TESTS");
  if (env == NULL || strcmp(env, "true") != 0) {
    cout << "Skipping mini cluster test." << endl;
    return 0;
  }
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
