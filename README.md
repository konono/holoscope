# holoscope
hololive schdule export to calendar.

## 概要

holoscopeはholoviveの所属タレント(ホロメン)の予定をgoogle calendarに転送できるアプリです。

動作環境は以下になります。
  - Python3.9 on Linux/Mac(Windowsは未確認)
    - git
    - pipenv
  - Python3.9 on AWS Lambda
    - git
    - pipenv
    - terraform

### アーキテクチャー

このアプリの構成要素は大まかに以下の3つです。
  - importer: youtubeの動画IDを取得してくる役割を持っています、デフォルトは[holodule](https://schedule.hololive.tv/simple)から取得してきます。
  - exporter: 受け取ったLiveEventオブジェクトを使って予定を作成します、デフォルトはgoogle calendarが指定されています。
  - core:　importer/exporterのプラグイン管理、動画IDを使って動画の詳細情報を取得し、LiveEventオブジェクトを生成する役割を持っています。

### configuration

以下はconfigurationサンプル
```
[general]
loglevel = "INFO"　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 # loglevel - 変更不要
logdir = "log"　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 # logを出力するディレクトリ - 変更不要
logfile = "holoscope.log"            # logfile名 -  変更不要
importer_plugin = "holodule"　　　　　　　　　　　　　　　　 #　import_pluginの指定(現在はholoduleのみ) - 変更不要
exporter_plugin = "google_calendar"  #　exporter_pluginの指定(現在はgoogle_calendarのみ) - 変更不要

[google_calendar]
calendar_id = "YOUR CALENDAR ID"     # google calendar id(e.x xxx@group.calendar.google.com) - 要変更

[holodule]
holomenbers = ['猫又おかゆ', 'さくらみこ', '桃鈴ねね']       # 予定を取得したいホロメンを正式名称で記述　 - 要変更
holodule_url = 'https://schedule.hololive.tv/simple'  # holoduleのURLを記載　　- 変更不要

[youtube]
api_key = "YOUR YOUTUBE API KEY"　# YoutubeのAPI　KEY - 要変更

# AWS Lambdaで動作させる場合記述
[aws]
access_key_id = 'YOUR AWS ACCESS KEY'　　　　　　　　　　　　# YoutubeのACCESS　KEY - 要変更
secret_access_key = 'YOUR AWS SECRET KEY'　　　　# YoutubeのSECRET　KEY - 要変更
dynamodb_table = 'holoscope'　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　#　　　dynamodbのtable名　　- 変更不要
dynamodb_hash_key_name = 'hashKey'         #　　　dynamodbのhash key　　- 変更不要
```

## Linux/Mac 環境　QuickStart

#### 1. ソースコードのダウンロード
```
git clone https://github.com/konono/holoscope.git
```

#### 2. pipenv sync
```
cd holoscope
pipenv sync
```

#### 3. youtube API keyとgoogle calendarのcredentialダウンロード
  - [youtube API KEYの作成方法](https://qiita.com/shinkai_/items/10a400c25de270cb02e4)
  - [Google Calendar API client jsonのダウンロード（Step1まで）](https://dev.classmethod.jp/articles/google-calendar-api-get-start/)

ダウンロードしたclient_secret_xxxx.apps.googleusercontent.com.jsonをgit cloneしたディレクトリに「**credentials.json**」の名前に変更しコピーしてください。

#### 4. google calendar APIのtoken取得
```
pipenv run python3 set_token2dynamodb.py

e.g.
[INFO][set_token2dynamodb][<module>] Token was not found in dynamodb
[INFO][__init__][autodetect] file_cache is only supported with oauth2client<4.0.0
[INFO][set_token2dynamodb][<module>] Create token
[INFO][set_token2dynamodb][<module>] Success validation token
```

#### 5. 実行
```
pipenv run python3 run.py
```

## Python3.9 on AWS Lambda

#### 1. ソースコードのダウンロード
```
git clone https://github.com/konono/holoscope.git
```


#### 2. pipenv sync
```
cd holoscope
pipenv sync
```


#### 3. youtube API keyとgoogle calendarのcredentialダウンロード
  - [youtube API KEYの作成方法](https://qiita.com/shinkai_/items/10a400c25de270cb02e4)
  - [Google Calendar API client jsonのダウンロード（Step1まで）](https://dev.classmethod.jp/articles/google-calendar-api-get-start/)

ダウンロードしたclient_secret_xxxx.apps.googleusercontent.com.jsonをgit cloneしたディレクトリに「**credentials.json**」の名前に変更しコピーしてください。

#### 4. AWSにterraform用のユーザー作成

##### 1. IAMを使ってユーザーを作成
![IAMでのユーザー作成](https://user-images.githubusercontent.com/8939854/153006422-8a958b75-2c50-4ba9-8471-e72fbbaf4079.png)

##### 2. 必要な権限の付与(ざっくり権限です、詳しい方はしっかりポリシー作ってください)
EventBridgeのfull access
![EventBridge](https://user-images.githubusercontent.com/8939854/153007070-35335d1e-c808-4914-b372-b4b76e29bbad.png)

dynamodbのfull access
![dynamodb](https://user-images.githubusercontent.com/8939854/153007514-4f7e0174-e4fb-4044-b489-fb5ec70e3afd.png)

Lambdaのfull access
![Lambda](https://user-images.githubusercontent.com/8939854/153007657-21e35d3d-1d47-4cb8-9ec8-7f90ada2f862.png)

Cloud Watchのfull access
![Cloud Watch](https://user-images.githubusercontent.com/8939854/153007775-0ece6a30-66ca-4422-a4f4-1fb0923e2a25.png)

IAMのfull access
![IAM](https://user-images.githubusercontent.com/8939854/153008138-6b1c8174-6e69-428f-b700-c084e4980f9e.png)

##### 3. タグの追加
![タグの追加](https://user-images.githubusercontent.com/8939854/153008421-7c4c83e7-e666-4a81-8a9f-199e9d2f8b34.png)

##### 4.　ユーザーの作成確認画面
![ユーザーの作成確認画面](https://user-images.githubusercontent.com/8939854/153008593-f22b53d7-c72f-486b-9538-4f162a914420.png)

##### 5.　Access Key IDとSecret key ID
ユーザーが作成できたら表示されているAccessIDとSecretIDをconfig.tomlに記述してください。
![　Access IDとSecret ID](https://user-images.githubusercontent.com/8939854/153008766-f9840b32-a0d0-4dc3-b7ed-d9b9e653369a.png)

#### 5. AWS CLIのインストール
以下の手順に従ってAWS CLIをインストールしてください。

[AWS CLIのインストール](https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/install-cliv2.html)

#### 6. AWSのプロファイルの登録
aws configure commandを使ってholoscope profileを登録します。

**terraformではprofileを固定しているため--profileの値はholoscopeのままでお願いします。**
```
aws configure --profile holoscope　
AWS Access Key ID [None]: YOUR ACCESS KEY
AWS Secret Access Key [None]: YOUR SECRET ACCRSS KEY
Default region name [None]: ap-northeast-1
Default output format [None]:
```

#### 7. terraformを使ってdynamodbの作成
```
cd ./terraform/dynamodb
terraform init
terraform apply

e.g.
❯ terraform apply

An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # aws_dynamodb_table.holoscope will be created
  + resource "aws_dynamodb_table" "holoscope" {
      + arn              = (known after apply)
      + billing_mode     = "PROVISIONED"
      + hash_key         = "hashKey"
      + id               = (known after apply)
      + name             = "holoscope"
      + read_capacity    = 1
      + stream_arn       = (known after apply)
      + stream_label     = (known after apply)
      + stream_view_type = (known after apply)
      + tags_all         = (known after apply)
      + write_capacity   = 1

      + attribute {
          + name = "hashKey"
          + type = "S"
        }

      + point_in_time_recovery {
          + enabled = (known after apply)
        }

      + server_side_encryption {
          + enabled     = (known after apply)
          + kms_key_arn = (known after apply)
        }

      + ttl {
          + attribute_name = (known after apply)
          + enabled        = (known after apply)
        }
    }

Plan: 1 to add, 0 to change, 0 to destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

aws_dynamodb_table.holoscope: Creating...
aws_dynamodb_table.holoscope: Creation complete after 8s [id=holoscope]
```

##### 8. tokenをdynamodbに登録
```
pipenv run python3 set_token2dynamodb.py

e.g.
❯ pipenv run python3 set_token2dynamodb.py
[INFO][set_token2dynamodb][<module>] Token was not found in dynamodb
[INFO][__init__][autodetect] file_cache is only supported with oauth2client<4.0.0
Getting the upcoming 10 events
2022-xx-xxTxx:00:00+09:00 XXXXXXXXXX
2022-yy-yyTyy:00:00+09:00 YYYYYYYYYY
2022-zz-zzTzz:00:00+09:00 ZZZZZZZZZZ
[INFO][set_token2dynamodb][<module>] Insert token to dynamodb
[INFO][set_token2dynamodb][<module>] Success get token from dynamodb
```

##### 9. lambdaにソースコードを登録

```
cd ./terraform/lambda
bash build_lambda.sh
terraform init
terraform apply

e.g.
❯ terraform apply

An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # aws_cloudwatch_event_rule.holoscope_event_rule will be created
  + resource "aws_cloudwatch_event_rule" "holoscope_event_rule" {
      + arn                 = (known after apply)
      + description         = "Run holoscope every 15 minutes"
      + event_bus_name      = "default"
      + id                  = (known after apply)
      + is_enabled          = true
      + name                = "holoscope_scheduler"
      + name_prefix         = (known after apply)
      + schedule_expression = "cron(0/15 * * * ? *)"
      + tags_all            = (known after apply)
    }

  # aws_cloudwatch_event_target.holoscope_event_target will be created
  + resource "aws_cloudwatch_event_target" "holoscope_event_target" {
      + arn            = (known after apply)
      + event_bus_name = "default"
      + id             = (known after apply)
      + rule           = "holoscope_scheduler"
      + target_id      = "holoscope"
    }

  # aws_iam_role.lambda_iam_role will be created
  + resource "aws_iam_role" "lambda_iam_role" {
      + arn                   = (known after apply)
      + assume_role_policy    = jsonencode(
            {
              + Statement = [
                  + {
                      + Action    = "sts:AssumeRole"
                      + Effect    = "Allow"
                      + Principal = {
                          + Service = "lambda.amazonaws.com"
                        }
                      + Sid       = ""
                    },
                ]
              + Version   = "2012-10-17"
            }
        )
      + create_date           = (known after apply)
      + force_detach_policies = false
      + id                    = (known after apply)
      + managed_policy_arns   = (known after apply)
      + max_session_duration  = 3600
      + name                  = "terraform-lambda-deployment_iam_role"
      + name_prefix           = (known after apply)
      + path                  = "/"
      + tags_all              = (known after apply)
      + unique_id             = (known after apply)

      + inline_policy {
          + name   = (known after apply)
          + policy = (known after apply)
        }
    }

  # aws_iam_role_policy.lambda_access_policy will be created
  + resource "aws_iam_role_policy" "lambda_access_policy" {
      + id     = (known after apply)
      + name   = "terraform-lambda-deployment_lambda_access_policy"
      + policy = jsonencode(
            {
              + Statement = [
                  + {
                      + Action   = [
                          + "dynamodb:ListTables",
                          + "dynamodb:DeleteItem",
                          + "dynamodb:DescribeContributorInsights",
                          + "dynamodb:ListTagsOfResource",
                          + "dynamodb:DeleteTable",
                          + "dynamodb:DescribeReservedCapacityOfferings",
                          + "dynamodb:PartiQLSelect",
                          + "dynamodb:DescribeTable",
                          + "dynamodb:GetItem",
                          + "dynamodb:DescribeContinuousBackups",
                          + "dynamodb:DescribeExport",
                          + "dynamodb:DescribeKinesisStreamingDestination",
                          + "dynamodb:DescribeLimits",
                          + "dynamodb:BatchGetItem",
                          + "dynamodb:ConditionCheckItem",
                          + "dynamodb:Scan",
                          + "dynamodb:Query",
                          + "dynamodb:DescribeStream",
                          + "dynamodb:UpdateItem",
                          + "dynamodb:DescribeTimeToLive",
                          + "dynamodb:ListStreams",
                          + "dynamodb:CreateTable",
                          + "dynamodb:DescribeGlobalTableSettings",
                          + "dynamodb:GetShardIterator",
                          + "dynamodb:DescribeGlobalTable",
                          + "dynamodb:DescribeReservedCapacity",
                          + "dynamodb:DescribeBackup",
                          + "dynamodb:UpdateTable",
                          + "dynamodb:GetRecords",
                          + "dynamodb:DescribeTableReplicaAutoScaling",
                          + "kms:GetPublicKey",
                          + "kms:ListResourceTags",
                          + "kms:GetParametersForImport",
                          + "kms:DescribeCustomKeyStores",
                          + "kms:GetKeyRotationStatus",
                          + "kms:DescribeKey",
                          + "kms:ListKeyPolicies",
                          + "kms:ListRetirableGrants",
                          + "kms:GetKeyPolicy",
                          + "kms:ListGrants",
                          + "kms:ListKeys",
                          + "kms:ListAliases",
                          + "logs:CreateLogStream",
                          + "logs:CreateLogGroup",
                          + "logs:PutLogEvents",
                        ]
                      + Effect   = "Allow"
                      + Resource = "arn:aws:logs:*:*:*"
                    },
                ]
              + Version   = "2012-10-17"
            }
        )
      + role   = (known after apply)
    }

  # aws_lambda_function.holoscope will be created
  + resource "aws_lambda_function" "holoscope" {
      + architectures                  = (known after apply)
      + arn                            = (known after apply)
      + filename                       = "lambda/function.zip"
      + function_name                  = "terraform-lambda-deployment_holoscope"
      + handler                        = "run.lambda_handler"
      + id                             = (known after apply)
      + invoke_arn                     = (known after apply)
      + last_modified                  = (known after apply)
      + layers                         = (known after apply)
      + memory_size                    = 128
      + package_type                   = "Zip"
      + publish                        = false
      + qualified_arn                  = (known after apply)
      + reserved_concurrent_executions = -1
      + role                           = (known after apply)
      + runtime                        = "python3.9"
      + signing_job_arn                = (known after apply)
      + signing_profile_version_arn    = (known after apply)
      + source_code_hash               = "0HN5SrYD/Ivt0k0k/GuAT+vAqboEy+4ZZlWvawbEhgY="
      + source_code_size               = (known after apply)
      + tags_all                       = (known after apply)
      + timeout                        = 30
      + version                        = (known after apply)

      + tracing_config {
          + mode = (known after apply)
        }
    }

  # aws_lambda_layer_version.lambda_layer will be created
  + resource "aws_lambda_layer_version" "lambda_layer" {
      + arn                         = (known after apply)
      + created_date                = (known after apply)
      + filename                    = "lambda/layer.zip"
      + id                          = (known after apply)
      + layer_arn                   = (known after apply)
      + layer_name                  = "terraform-lambda-deployment_lambda_layer"
      + signing_job_arn             = (known after apply)
      + signing_profile_version_arn = (known after apply)
      + skip_destroy                = false
      + source_code_hash            = "WgYSZUda4FUo3A+wIV6wx223hsAR4tRolGGj2M2lRqs="
      + source_code_size            = (known after apply)
      + version                     = (known after apply)
    }

  # aws_lambda_permission.allow_cloudwatch_to_call_holoscope will be created
  + resource "aws_lambda_permission" "allow_cloudwatch_to_call_holoscope" {
      + action        = "lambda:InvokeFunction"
      + function_name = "terraform-lambda-deployment_holoscope"
      + id            = (known after apply)
      + principal     = "events.amazonaws.com"
      + source_arn    = (known after apply)
      + statement_id  = "AllowExecutionFromCloudWatch"
    }

Plan: 7 to add, 0 to change, 0 to destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

aws_lambda_layer_version.lambda_layer: Creating...
aws_iam_role.lambda_iam_role: Creating...
aws_cloudwatch_event_rule.holoscope_event_rule: Creating...
aws_cloudwatch_event_rule.holoscope_event_rule: Creation complete after 1s [id=holoscope_scheduler]
aws_iam_role.lambda_iam_role: Creation complete after 4s [id=terraform-lambda-deployment_iam_role]
aws_iam_role_policy.lambda_access_policy: Creating...
aws_iam_role_policy.lambda_access_policy: Creation complete after 2s [id=terraform-lambda-deployment_iam_role:terraform-lambda-deployment_lambda_access_policy]
aws_lambda_layer_version.lambda_layer: Creation complete after 10s [id=arn:aws:lambda:ap-northeast-1:012152018325:layer:terraform-lambda-deployment_lambda_layer:23]
aws_lambda_function.holoscope: Creating...
aws_lambda_function.holoscope: Still creating... [10s elapsed]
aws_lambda_function.holoscope: Creation complete after 11s [id=terraform-lambda-deployment_holoscope]
aws_cloudwatch_event_target.holoscope_event_target: Creating...
aws_lambda_permission.allow_cloudwatch_to_call_holoscope: Creating...
aws_lambda_permission.allow_cloudwatch_to_call_holoscope: Creation complete after 1s [id=AllowExecutionFromCloudWatch]
aws_cloudwatch_event_target.holoscope_event_target: Creation complete after 1s [id=holoscope_scheduler-holoscope]

Apply complete! Resources: 7 added, 0 changed, 0 destroyed.
```
以上です！お疲れさまでした！

Author Information
------------------

Yuki Yamashita(@konono)
