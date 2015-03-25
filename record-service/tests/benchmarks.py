#!/usr/bin/env python
# Copyright 2012 Cloudera Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This contains descriptions of all the benchmarks. They are broken up into
# suites.

import os

def impala_shell_cmd(query):
  return os.environ['IMPALA_HOME'] +\
      "/bin/impala-shell.sh -i LOCALHOST -B -q \"" + query + "\""

def impala_single_thread_cmd(query):
  query = "set num_scanner_threads=1;" + query
  return impala_shell_cmd(query)

def impala_on_rs_cmd(query):
  query = "set use_record_service=true;" + query
  return impala_shell_cmd(query)

def native_client_cmd(query):
  return os.environ['RECORD_SERVICE_HOME'] +\
      "/cpp/build/release/recordservice/record-service-client \"" +\
      query + "\""

def java_client_cmd(query):
  return "java -classpath " + os.environ['RECORD_SERVICE_HOME'] +\
      "/java/sample/target/recordservice-sample-0.1.jar " +\
      "com.cloudera.recordservice.sample.SampleClientLib " +\
      "\"" + query + "\""

def hive_rs_cmd(query, tbl_name, fetch_size):
  # Builds a query string that will run using the RecordService
  rs_query = """
      set hive.input.format=com.cloudera.recordservice.hive.RecordServiceHiveInputFormat;
      set recordservice.table.name={0};
      set recordservice.fetch.size={1};
      {2}""".format(tbl_name, fetch_size, query)
  return hive_cmd(rs_query)

def hive_cmd(query):
  return "hive -e \"" + query + "\""

#TODO: I think this spends a lot of time just starting up spark.
def spark_cmd(cl, query):
  return "java -classpath " + os.environ['RECORD_SERVICE_HOME'] +\
      "/java/spark-benchmark/target/recordservice-spark-benchmark-0.1.jar " + cl +\
      " \"" + query + "\""

def spark_q1(query):
  return spark_cmd("com.cloudera.recordservice.benchmark.Query1", query)

def spark_q2(query):
  return spark_cmd("com.cloudera.recordservice.benchmark.Query2", query)

benchmarks = [
  [
    # Metadata about this suite. "local" indicates this benchmark should only be
    # run on a single node.
    # The first argument is used for file paths so cannot contain characters that
    # need to be escaped.
    "Query1_Text_6GB", "local",
    [
      # Each case to run. The first element is the name of the application and
      # the second is the shell command to run to run the benchmark
      ["impala", impala_shell_cmd("select sum(l_partkey) from tpch6gb.lineitem")],
      ["impala-single-thread", impala_single_thread_cmd(
          "select sum(l_partkey) from tpch6gb.lineitem")],
      ["impala-rs", impala_on_rs_cmd("select sum(l_partkey) from tpch6gb.lineitem")],
      ["native-client", native_client_cmd("select l_partkey from tpch6gb.lineitem")],
      ["java-client", java_client_cmd("select l_partkey from tpch6gb.lineitem")],
      ["spark-rs", spark_q1("select l_partkey from tpch6gb.lineitem")],
      #["hive-rs", hive_rs_cmd(query='select sum(l_partkey) from rs.lineitem_hive_serde',
      #    tbl_name='tpch6gb.lineitem', fetch_size=50000)
      #],
    ]
  ],

  [
    "Query1_Parquet_6GB", "local",
    [
      ["impala", impala_shell_cmd("select sum(l_partkey) from tpch6gb_parquet.lineitem")],
      ["impala-single-thread", impala_single_thread_cmd(
          "select sum(l_partkey) from tpch6gb_parquet.lineitem")],
      ["impala-rs", impala_on_rs_cmd(
          "select sum(l_partkey) from tpch6gb_parquet.lineitem")],
      ["native-client", native_client_cmd(
          "select l_partkey from tpch6gb_parquet.lineitem")],
      ["java-client", java_client_cmd("select l_partkey from tpch6gb_parquet.lineitem")],
      ["spark-rs", spark_q1("select l_partkey from tpch6gb_parquet.lineitem")],
      #["hive-rs", hive_rs_cmd(query='select sum(l_partkey) from rs.lineitem_hive_serde',
      #    tbl_name='tpch6gb_parquet.lineitem', fetch_size=50000)
      #],
    ]
  ],

  [
    "Query1_Avro_6GB", "local",
    [
      ["impala", impala_shell_cmd(
          "select sum(l_partkey) from tpch6gb_avro_snap.lineitem")],
      ["impala-single-thread", impala_single_thread_cmd(
          "select sum(l_partkey) from tpch6gb_avro_snap.lineitem")],
      ["impala-rs", impala_on_rs_cmd(
          "select sum(l_partkey) from tpch6gb_avro_snap.lineitem")],
      ["native-client", native_client_cmd(
          "select l_partkey from tpch6gb_avro_snap.lineitem")],
      ["java-client", java_client_cmd(
          "select l_partkey from tpch6gb_avro_snap.lineitem")],
      ["spark-rs", spark_q1("select l_partkey from tpch6gb_avro_snap.lineitem")],
      #["hive-rs", hive_rs_cmd(query='select sum(l_partkey) from rs.lineitem_hive_serde',
      #    tbl_name='tpch6gb_avro_snap.lineitem', fetch_size=50000)
      #],
    ]
  ],

  [
    "Query2_Parquet_6GB", "local",
    [
      ["impala", impala_shell_cmd(
          "select sum(l_partkey) from tpch6gb_parquet.lineitem group by l_returnflag")],
      ["impala-single-thread", impala_single_thread_cmd(
          "select sum(l_partkey) from tpch6gb_parquet.lineitem group by l_returnflag")],
      ["impala-rs", impala_on_rs_cmd(
          "select sum(l_partkey) from tpch6gb_parquet.lineitem group by l_returnflag")],
      ["native-client", native_client_cmd(
          "select l_partkey, l_returnflag from tpch6gb_parquet.lineitem")],
      ["java-client", java_client_cmd(
          "select l_partkey, l_returnflag from tpch6gb_parquet.lineitem")],
      ["spark-rs", spark_q2(
          "select l_partkey, l_returnflag from tpch6gb_parquet.lineitem")],
    ]
  ],

  [
    "Query2_Avro_6GB", "local",
    [
      ["impala", impala_shell_cmd(
          "select sum(l_partkey) from tpch6gb_avro_snap.lineitem group by l_returnflag")],
      ["impala-single-thread", impala_single_thread_cmd(
          "select sum(l_partkey) from tpch6gb_avro_snap.lineitem group by l_returnflag")],
      ["impala-rs", impala_on_rs_cmd(
          "select sum(l_partkey) from tpch6gb_avro_snap.lineitem group by l_returnflag")],
      ["native-client", native_client_cmd(
          "select l_partkey, l_returnflag from tpch6gb_avro_snap.lineitem")],
      ["java-client", java_client_cmd(
          "select l_partkey, l_returnflag from tpch6gb_avro_snap.lineitem")],
      ["spark-rs", spark_q2(
          "select l_partkey, l_returnflag from tpch6gb_avro_snap.lineitem")],
    ]
  ],

  [
    "Query1_Parquet_500GB", "cluster",
    [
      ["impala", impala_shell_cmd(
          "select count(ss_item_sk) from tpcds500gb_parquet.store_sales")],
      ["impala-rs", impala_on_rs_cmd(
          "select count(ss_item_sk) from tpcds500gb_parquet.store_sales")],
    ]
  ],
]
