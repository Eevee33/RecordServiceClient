// Copyright 2014 Cloudera Inc.
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

package com.cloudera.recordservice.client;

import java.io.IOException;

import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.cloudera.recordservice.thrift.RecordServicePlanner;
import com.cloudera.recordservice.thrift.TGetSchemaResult;
import com.cloudera.recordservice.thrift.TPlanRequestParams;
import com.cloudera.recordservice.thrift.TPlanRequestResult;
import com.cloudera.recordservice.thrift.TProtocolVersion;
import com.cloudera.recordservice.thrift.TRecordServiceException;

/**
 * Java client for the RecordServicePlanner. This class is not thread safe.
 * TODO: This class should not expose the raw Thrift objects, should use proper logger.
 */
public class RecordServicePlannerClient {
  private final static Logger LOG =
      LoggerFactory.getLogger(RecordServicePlannerClient.class);

  private RecordServicePlanner.Client plannerClient_;
  private TProtocol protocol_;
  private boolean isClosed_ = false;
  private ProtocolVersion protocolVersion_ = null;

  /**
   * Generates a plan for 'request', connecting to the planner service at
   * hostname/port.
   */
  public static TPlanRequestResult planRequest(
      String hostname, int port, Request request)
      throws IOException, TRecordServiceException {
    RecordServicePlannerClient client = null;
    try {
      client = new RecordServicePlannerClient(hostname, port);
      return client.planRequest(request);
    } finally {
      if (client != null) client.close();
    }
  }

  /**
   * Gets the schema for 'request', connecting to the planner service at
   * hostname/port.
   */
  public static TGetSchemaResult getSchema(
      String hostname, int port, Request request)
      throws IOException, TRecordServiceException {
    RecordServicePlannerClient client = null;
    try {
      client = new RecordServicePlannerClient(hostname, port);
      return client.getSchema(request);
    } finally {
      if (client != null) client.close();
    }
  }

  /**
   * Opens a connection to the RecordServicePlanner.
   */
  public RecordServicePlannerClient(String hostname, int port) throws IOException {
    LOG.info("Connecting to RecordServicePlanner at " + hostname + ":" + port);
    TTransport transport = new TSocket(hostname, port);
    try {
      transport.open();
    } catch (TTransportException e) {
      throw new IOException(String.format(
          "Could not connect to RecordServicePlanner: %s:%d", hostname, port), e);
    }
    protocol_ = new TBinaryProtocol(transport);
    plannerClient_ = new RecordServicePlanner.Client(protocol_);
    try {
      protocolVersion_ = ThriftUtils.fromThrift(plannerClient_.GetProtocolVersion());
      LOG.debug("Connected to planner service with version: " + protocolVersion_);
    } catch (TException e) {
      // TODO: this probably means they connected to a thrift service that is not the
      // planner service (i.e. wrong port). Improve this message.
      throw new IOException("Could not get service protocol version.", e);
    }
  }

  /**
   * Closes a connection to the RecordServicePlanner.
   */
  public void close() {
    if (protocol_ != null && !isClosed_) {
      LOG.debug("Closing RecordServicePlanner connection.");
      protocol_.getTransport().close();
      isClosed_ = true;
    }
  }

  /**
   * Returns the protocol version of the connected service.
   */
  public ProtocolVersion getProtocolVersion() throws RuntimeException {
    validateIsConnected();
    return protocolVersion_;
  }

  /**
   * Calls the RecordServicePlanner to generate a new plan - set of tasks that can be
   * executed using a RecordServiceWorker.
   */
  public TPlanRequestResult planRequest(Request request)
      throws IOException, TRecordServiceException {
    validateIsConnected();

    TPlanRequestResult planResult;
    try {
      LOG.info("Planning request: " + request);
      TPlanRequestParams planParams = request.request_;
      planParams.client_version = TProtocolVersion.V1;
      planResult = plannerClient_.PlanRequest(planParams);
    } catch (TRecordServiceException e) {
      throw e;
    } catch (TException e) {
      // TODO: this should mark the connection as bad on some error codes.
      throw new IOException("Could not plan request.", e);
    }
    LOG.debug("PlanRequest generated " + planResult.tasks.size() + " tasks.");
    return planResult;
  }

  /**
   * Calls the RecordServicePlanner to return the schema for a request.
   */
  public TGetSchemaResult getSchema(Request request)
    throws IOException, TRecordServiceException {
    validateIsConnected();
    TGetSchemaResult result;
    try {
      LOG.info("Getting schema for request: " + request);
      TPlanRequestParams planParams = request.request_;
      planParams.client_version = TProtocolVersion.V1;
      result = plannerClient_.GetSchema(planParams);
    } catch (TRecordServiceException e) {
      throw e;
    } catch (TException e) {
      // TODO: this should mark the connection as bad on some error codes.
      throw new IOException("Could not plan request.", e);
    }
    return result;
  }

  private void validateIsConnected() throws RuntimeException {
    if (plannerClient_ == null || isClosed_) {
      throw new RuntimeException("Client not connected.");
    }
  }
}
