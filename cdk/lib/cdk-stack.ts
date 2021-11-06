import * as cdk from '@aws-cdk/core';
import * as iam from '@aws-cdk/aws-iam';
import * as s3 from '@aws-cdk/aws-s3';
import * as sqs from '@aws-cdk/aws-sqs';
import * as secretsmanager from '@aws-cdk/aws-secretsmanager';
import {Duration} from '@aws-cdk/core';

export interface CdkStackProps extends cdk.StackProps {
  s3LogBucketName: string
  s3ResultBucketName: string
  s3MailBucketName: string
}

export class CdkStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props: CdkStackProps) {
    super(scope, id, props);

    // S3bucket
    new s3.Bucket(this, `MailAddressBucket`, {
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      bucketName: props.s3MailBucketName
    });

    // SQS
    new sqs.Queue(this, 'BIAthenaSQS', {
      visibilityTimeout: Duration.minutes(3)
    });
    new sqs.Queue(this, 'BIMailSQS', {
      visibilityTimeout: Duration.minutes(3)
    });

    // IAM
    const athenaUser = new iam.User(this, 'BIAthenaUser', {
      userName: `bi-athena-user`,
      managedPolicies: [
        iam.ManagedPolicy.fromManagedPolicyArn(
          this,
          'AWSLambdaBasicExecutionRole',
          'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        ),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonAthenaFullAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSQSFullAccess')
      ]
    });
    // policy
    const s3_policy_input_statement = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['s3:GetObject'],
      resources: [`arn:aws:s3:::${props.s3LogBucketName}/*`]
    })
    const s3_policy_output_statement = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        "s3:GetBucketLocation",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:ListBucketMultipartUploads",
        "s3:AbortMultipartUpload",
        "s3:PutObject",
        "s3:ListMultipartUploadParts"
      ],
      resources: [
        `arn:aws:s3:::${props.s3ResultBucketName}`,
        `arn:aws:s3:::${props.s3ResultBucketName}/*`,
        `arn:aws:s3:::${props.s3MailBucketName}`,
        `arn:aws:s3:::${props.s3MailBucketName}/*`
      ]
    })
    new iam.Policy(this, 'AthenaS3Policy', {
      policyName: 'AthenaS3GetObject',
      statements: [s3_policy_input_statement, s3_policy_output_statement],
      users: [athenaUser]
    })
    // access_key
    const athenaUserKey = new iam.CfnAccessKey(this, 'BiAthenaUserKey', {
      userName: athenaUser.userName
    })
    new secretsmanager.Secret(this, 'BiAthenaSecretManager', {
      secretName: `bi-athena-user-key`,
      description: `bi-athena-user-key`,
      generateSecretString: {
        secretStringTemplate: JSON.stringify({
          access_key_id: athenaUserKey.ref,
          secret_access_key: athenaUserKey.attrSecretAccessKey
        }),
        // generateStringKeyは不要だがエラーになるのでいれる
        generateStringKey: 'password'
      }
    })
  }
}
