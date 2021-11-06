![logo](logo.svg)

# ChatOps by Chalice

Slackと接続する設定をすることによって、AWSで収集した様々なデータをchatに表示したり、その他ChatOpsを実現するためのサービスです。
（というものになる予定です）

## 現在の機能

- ALBのログをAthenaでクエリして、その結果を集計して表示できます。
- SESでBounce/Complaintを受け取ったメールについて通知をSlackに流し、またエラーになったリストをS3に保存してダウンロードできます。

## 利用しているもの

AWS  
Slack  
いわゆるサーバーレスな作りとなっています。Chaliceの仕組みにより処理はLambdaで実行されるので、コンテナの管理等は考慮する必要がありません。

## 設定手順

1. SlackにAppを登録して、bot tokenを入手し、config.jsonのSLACK_BOT_TOKENに記録します。（xxxx-....）
2. また、デフォルトで投稿するchannelのidをSLACK_CHANNELに記録します。（CXXYYYYYYYYのような英数の形式）
3. config.jsonの内容のうち、以下の項目を設定します。 S3_LOG_BUCKET, S3_RESULT_BUCKET, S3_RESULT_FOLDER, S3_MAIL_BUCKET（S3から始まるもの）
4. aws-cliの設定を行っていない場合は、aws configを実行します。
5. cdkフォルダに移動して、cdk deployを実行します。
6. AWSの管理コンソールより、シークレットマネージャーに記録されているcocha-athena-user-keyのシークレットの値を取得し、
  config.jsonのATHENA_AWS_ACCESS_KEY_ID、ATHENA_AWS_SECRET_ACCESS_KEYに記録します。
7. ALBのログをAthenaで読み取れるようにします。このときに定義したデータベース名、テーブル名をconfig.jsonのATHENA_DATABASE、LOG_TABLE_PREFIXに記録します。
8. AWSの管理コンソールより、cdkで作成されたSQSのURLをATHENA_SQS_URL、MAIL_SQS_URLに設定します。https://...
9. webフォルダに移動して、chalice deployを実行します。
10. deployするとURLが確定するので、SlackのAppのコマンドを登録します。
11. 登録したコマンドを実行して、コマンドが実行されることを確認します。（初回リクエストはタイムアウトする場合があります。）

### Amazon SESのエラーメール通知を有効にするには

まずAmazon SESのSNS通知を有効にします。  
参考：https://docs.aws.amazon.com/ja_jp/ses/latest/DeveloperGuide/notification-contents.html  
次に、MAIL_SQS_URLに設定したSQSを、SESの通知先のSNSトピックに設定します。

## 料金について

Lambda、SQS、s3に関しては通常の無料利用枠内に収まる程度の使用量と思われ、仮に費用が発生した場合も微量と思われます。  
Athenaに関しては、ログの量に応じて費用が発生します。

## LICENSE

MIT
