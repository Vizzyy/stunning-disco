```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: 'AWS::Serverless-2016-10-31'

Parameters:
  domainName:
    Type: String
  restApiName:
    Type: String
  trustStoreUri:
    Type: String
  apiHostCert:
    Type: String
  s3Credential:
    Type: String
  rootEndpointUri:
    Type: String
  hostedZoneId:
    Type: AWS::Route53::HostedZone::Id

Resources:
  StunningDisco:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: !Ref restApiName
      DisableExecuteApiEndpoint: True
      EndpointConfiguration:
        Types:
          - REGIONAL

  StunningDiscoDomain:
    Type: AWS::ApiGateway::DomainName
    Properties:
      DomainName: !Ref domainName
      EndpointConfiguration:
        Types:
          - REGIONAL
      MutualTlsAuthentication:
        TruststoreUri: !Ref trustStoreUri
      RegionalCertificateArn: !Ref apiHostCert
      SecurityPolicy: TLS_1_2

  StunningDiscoDomainMapping:
    Type: 'AWS::ApiGateway::BasePathMapping'
    Properties:
      DomainName: !Ref StunningDiscoDomain
      RestApiId: !Ref StunningDisco
      Stage: Prod

  StunningDiscoRootEndpoint:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref StunningDisco
      ResourceId: !GetAtt StunningDisco.RootResourceId
      HttpMethod: "GET"
      AuthorizationType: NONE
      OperationName: "Root path"
      Integration:
        Type: "AWS"
        Credentials: !Ref s3Credential
        IntegrationHttpMethod: "GET"
        Uri: !Ref rootEndpointUri
        IntegrationResponses:
          - StatusCode: 200
      MethodResponses:
        - StatusCode: 200
          ResponseModels: { "text/html": "Empty" }

  StunningDiscoDeployment:
    Type: AWS::ApiGateway::Deployment
    DependsOn: StunningDiscoRootEndpoint
    Properties:
      RestApiId: !Ref StunningDisco
      StageName: Prod
      StageDescription:
        LoggingLevel: INFO
        DataTraceEnabled: True

  StunningDiscoDnsRecord:
    Type: AWS::Route53::RecordSet
    Properties:
      HostedZoneId: !Ref 'hostedZoneId'
      Name: !Ref domainName
      Type: A
      AliasTarget:
        HostedZoneId: !GetAtt StunningDiscoDomain.RegionalHostedZoneId
        DNSName: !GetAtt StunningDiscoDomain.RegionalDomainName


```