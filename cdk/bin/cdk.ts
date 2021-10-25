#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { CdkStack } from '../lib/cdk-stack';
import {readFileSync} from "fs";

const app = new cdk.App();
const propsBase = JSON.parse(readFileSync('../web/.chalice/config.json', 'utf-8'))
new CdkStack(app, 'BiAthenaStack', {
  s3LogBucketName: propsBase.S3_LOG_BUCKET,
  s3ResultBucketName: propsBase.S3_RESULT_BUCKET
});
