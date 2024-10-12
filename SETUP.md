# Setup Instructions

- [Setup Instructions](#setup-instructions)
  - [Configuring EC2 Client](#configuring-ec2-client)
    - [Saving Private Key for SSH access](#saving-private-key-for-ssh-access)
    - [Converting to PuTTY `.ppk` private key](#converting-to-putty-ppk-private-key)
    - [Connecting to EC2 Client](#connecting-to-ec2-client)
  - [Setting up Kafka on EC2](#setting-up-kafka-on-ec2)
    - [Kafka Installation](#kafka-installation)
    - [Installing IAM authentication package](#installing-iam-authentication-package)
    - [Retrieving IAM authentication information](#retrieving-iam-authentication-information)
    - [Configuring the IAM authentication package](#configuring-the-iam-authentication-package)
  - [Creating Kafka Topics](#creating-kafka-topics)
    - [Retrieving MSK cluster information](#retrieving-msk-cluster-information)
    - [Creating topics](#creating-topics)
  - [Create custom plugin with MSK Connect](#create-custom-plugin-with-msk-connect)
    - [Find S3 Bucket](#find-s3-bucket)
    - [Downloading Connector](#downloading-connector)
    - [Creating custom plugin](#creating-custom-plugin)
  - [Creating a connector with MSK Connect](#creating-a-connector-with-msk-connect)
  - [Kafka REST API configuration](#kafka-rest-api-configuration)
    - [Create a proxy integration](#create-a-proxy-integration)
    - [Integrating the proxy resource](#integrating-the-proxy-resource)
    - [Deploy API](#deploy-api)
  - [Kafka REST proxy on EC2 Client](#kafka-rest-proxy-on-ec2-client)
    - [Start Kafka REST proxy on EC2 Client](#start-kafka-rest-proxy-on-ec2-client)

## Configuring EC2 Client

### Saving Private Key for SSH access

1. In AWS, access the Parameter Store to find the `KeyPairId` using your User ID.
2. Click **Show**, and copy the value of this parameter.
3. Paste this into a file ending in the `.pem` extension.
4. Navigate to the EC2 Client, and find the client containing your User ID.
5. Select the instance, and under **Details** make a note of **Key Pair assigned at launch**
6. Set the name of the `.pem` key file to the **Key Pair assigned at launch** value. For example `<user_id>-key-pair.pem`
7. Additionally, make a note of the **Public IPv4 DNS**, this is the addressed used to connect to.

### Converting to PuTTY `.ppk` private key

1. Open **PuTTYgen** key generator.
2. Click on **Load** and navigate to the location of the `.pem` key. Make sure filter is set to show all files, not `.ppk` files.
3. Once found and selected, make sure **Type of Key to generate** is set to **RSA**
4. Choose **Save private key** and store it in a secure location, with the name set to **Key Pair assigned at launch** noted previously.

### Connecting to EC2 Client

1. Open **PuTTY**
2. In the **Host Name (or IP address)** box, enter the **Public IPv4 DNS** of the EC2 instance from earlier.
3. On the left tree, navigate to **Connection** and then **Data**.
4. Set **Auto-login username** to `ec2-user`, as EC2 warns you should use this name over `root`
5. On  the left tree again, navigate to **Connection**, **SSH**, then **Auth**
6. At the bottom of this page, choose **Browse** under **Private key file for Authentication**
7. Navigate and select the previously created `.ppk` file.
8. On the left tree, head back to the top and select **Session**
9. Under **Saved Session** give a name such as **EC2** and press save. This way, you can load the saved profile in the future without having to reconfigure each time.
10. Finally, press **Open**. You may be requested to confirm connecting to an unknown host with a fingerprint, this occurs on a first connect. Press **Yes** to continue.

## Setting up Kafka on EC2

### Kafka Installation

1. Once connected to the EC2 instance over SSH, first install Java

```bash
sudo yum install java-1.8.0
```

2. Then install and extract Kafka, in this case version `2.12-2.8.1`, with the following:

```bash
wget https://archive.apache.org/dist/kafka/2.8.1/kafka_2.12-2.8.1.tgz
tar -xzf kafka_2.12-2.8.1.tgz
mv kafka_2.12-2.8.1 kafka
```

### Installing IAM authentication package

1. Navigate inside the Kafka `libs` directory (`cd kafka/libs`)
2. Download the IAM authentication package

```bash
wget https://github.com/aws/aws-msk-iam-auth/releases/download/v1.1.5/aws-msk-iam-auth-1.1.5-all.jar
```
3. Run `pwd` to get the full path to this directory, and append `aws-msk-iam-auth-1.1.5-all.jar` to the end. Make a note of this full path.

```bash
pwd  /home/ec2-user/kafka/bin/
```

4. This path needs to be added to an environment variable called `CLASSPATH`
   1. Edit the `.bashrc` file by running `nano ~/.bashrc`
   2. At the bottom of the file, add `export CLASSPATH=<full_path_to_iam_jar>`
   3. Save the file, and reload by running `source ~/.bashrc`
   4. Confirm the variable is set with `echo $CLASSPATH`

### Retrieving IAM authentication information

1. On the AWS console, navigate to **IAM console**
2. Select **Roles** on the left.
3. Find a role in the following format: <UserID>-ec2-access-role
4. Make a note of the **IAM Role ARN** as it will be used later.
5. Go to **Trust Relationships** and select **Edit Trust Policy**
6. On the right click **Add a principal** and select **IAM roles** as the Principal type
7. Replace the value with the copied IAM Role **ARN**

### Configuring the IAM authentication package

1. Back on the EC2 SSH session, navigate to the `bin` directory in Kafka.
2. Create a file called `client.properties` with `nano client.properties`
3. Paste the following into the file:

```t
 Sets up TLS for encryption and SASL for authN.
security.protocol = SASL_SSL

 Identifies the SASL mechanism to use.
sasl.mechanism = AWS_MSK_IAM

 Binds SASL client implementation.
sasl.jaas.config = software.amazon.msk.auth.iam.IAMLoginModule required awsRoleArn="Your Access Role";

 Encapsulates constructing a SigV4 signature based on extracted credentials.
 The SASL client bound by "sasl.jaas.config" invokes this class.
sasl.client.callback.handler.class = software.amazon.msk.auth.iam.IAMClientCallbackHandler
```

4. Replace `Your Access Role` with the previously copied **IAM Role ARN**
5. Save and exit from the file.


## Creating Kafka Topics

### Retrieving MSK cluster information

1. On the AWS Console, navigate to **MSK console**
2. Select the cluster, and then click on **Client Information**
3. Copy the **Private endpoint (single-VPC)** string, this is the **Bootstrap Server string**
4. Copy the **Plaintext Apache ZooKeeper connection** string as well, for future use.

### Creating topics

1. Back on the EC2 SSH session, navigate to the `bin` folder inside the Kafka folder.
2. Using the previously noted **Bootstrap Server string**, run the following command replacing `<BootstrapServerString>` and `<topic_name>`:

```bash
./kafka-topics.sh --bootstrap-server <BootstrapServerString> --command-config client.properties --create --topic <topic_name>
```

In this case, create topics with the following formats, replacing `<UserID>` with your AWS User ID.

- `<UserID>.pin`
- `<UserID>.geo`
- `<UserID>.user`

## Create custom plugin with MSK Connect

### Find S3 Bucket

1. On the AWS Console, navigate to **S3 Console**
2. Search for a bucket that contains your AWS User ID. Make a note of the name of this bucket.

### Downloading Connector

1. Back on the EC2 SSH session, run the following:

```bash
 assume admin user privileges
sudo -u ec2-user -i
 create directory where we will save our connector
mkdir kafka-connect-s3 && cd kafka-connect-s3
```

2. Next, download the Confluent.io Amazon S3 Connector:
```bash
wget https://d2p6pa21dvn84.cloudfront.net/api/plugins/confluentinc/kafka-connect-s3/versions/10.5.13/confluentinc-kafka-connect-s3-10.5.13.zip
```

3. Lastly, copy the downloaded ZIP to the S3 bucket, replacing `<BucketName>` with the previously noted S3 bucket name.
```bash
aws s3 cp ./confluentinc-kafka-connect-s3-10.0.3.zip s3://<BucketName>/kafka-connect-s3/
```

1. On the AWS Console, navigate to the S3 Bucket noted earlier and confirm the file is uploaded under the folder `kafka-connect-s3`

### Creating custom plugin

1. Navigate to the **MSK Console**
2. On the left navigation, choose **Customised plugins** under **MSK Connect**
3. Click **Create customised plugin**
4. Set the **S3 URI - customised plugin object** to the path of the uploaded Confluent.io zip in your S3 bucket.
5. Set the customised plugin name to `<UserID>-plugin` replacing `<UserID>` with your AWS User ID.
6. Finally click the **Create customised plugin** button.

## Creating a connector with MSK Connect

1. In the **MSK Console**, choose **Connectors** under **MSK Connect**
2. Choose **Create connector**
3. Search for the previously crated custom plugin with `<UserID>-plugin` then press **Next**
4. Set the **Connector Name** to `<UserID>-connector`
5. Select the MSK cluster for **Apache Kafka cluster**
6. Under **Configuration settings**, set the following, replacing `<UserID>` with your AWS User ID, and `<BucketName>` with your S3 Bucket:

```conf
connector.class=io.confluent.connect.s3.S3SinkConnector
 Same region as our bucket and cluster
s3.region=us-east-1
flush.size=1
schema.compatibility=NONE
tasks.max=3
 Read all data from topics starting with your User ID.
topics.regex=<UserID>.*
format.class=io.confluent.connect.s3.format.json.JsonFormat
partitioner.class=io.confluent.connect.storage.partitioner.DefaultPartitioner
value.converter.schemas.enable=false
value.converter=org.apache.kafka.connect.json.JsonConverter
storage.class=io.confluent.connect.s3.storage.S3Storage
key.converter=org.apache.kafka.connect.storage.StringConverter
s3.bucket.name=<BucketName>
```

7. Under **Connector capacity** set **Capacity Type** to **Provisioned** and **MCU count per Worker** to `1`
8. Under **Worker Configuration**, select **Use a customised configuration**
   1. In the drop-down menu, choose `confluent-worker`
9. Under **Access Permissions**, set the **IAM role** to your EC2 IAM Role name, which is in the format `<UserID>-ec2-access-role`
10. Press the **Next** button, skipping until the **Review and create** page.
11. Finally at the bottom press **Create connector**

## Kafka REST API configuration

### Create a proxy integration

1. In the AWS Console, navigate to **API Gateway console**
2. Search for the API that contains your AWS User ID.
3. Choose **Create Resource** above the resource tree panel.
4. Enable **Proxy resource** and set the name as `{proxy+}`
5. Enable the **CORS** checkbox too.
6. Press **Create Resource**

### Integrating the proxy resource

1. Under the `{proxy+}` resource, click on **ANY**
2. It will say it is an Undefined Integration. Choose **Edit integration**
3. Set the **Integration Type** to **HTTP**
4. Enable the **HTTP proxy integration** toggle.
5. Set **HTTP method** to **ANY**
6. Set the **Endpoint URL** to the following, replacing <EC2PublicIPv4> with the previously noted **Public IPv4 DNS** address of your EC2 client: `http://<EC2PublicIPv4>:8082/{proxy}`
7. Finally press **Save**

### Deploy API

1. With the same API selected, press the **Deploy API** button.
2. For **Stage**, select `dev`. If it is not present, create it first.
3. Press **Deploy**. Once deployed make a note of the **Invoke URL**

## Kafka REST proxy on EC2 Client

1. On the EC2 SSH session, firstly download the Confluent package:

```bash
sudo wget https://packages.confluent.io/archive/7.2/confluent-7.2.0.tar.gz
tar -xvzf confluent-7.2.0.tar.gz
```

2. Navigate into the extracted Confluent directory, and then into `etc/kafka-rest`
3. Edit the `kafka-rest.properties` with `nano kafka-rest.properties`
4. Uncomment the line `#zookeeper.connect=localhost.2181` and set `zookeeper.connect` to the previously noted **Plaintext ZooKeeper connection** string: `zookeeper.connect=<PlaintextZooKeeperString>`
5. Set `bootstrap.servers` to the previously noted **Bootstrap Server string**: `bootstrap.servers=<BootstrapServerString>`
6. Additionally, add the following to the configuration file at the bottom. This is for surpassing the IAM authentication of the MSK cluster. Replace `Your Access Role` with the **EC2 IAM Access Role ARN** noted earlier.

```bash
 Sets up TLS for encryption and SASL for authN.
client.security.protocol = SASL_SSL

 Identifies the SASL mechanism to use.
client.sasl.mechanism = AWS_MSK_IAM

 Binds SASL client implementation.
client.sasl.jaas.config = software.amazon.msk.auth.iam.IAMLoginModule required awsRoleArn="Your Access Role";

 Encapsulates constructing a SigV4 signature based on extracted credentials.
 The SASL client bound by "sasl.jaas.config" invokes this class.
client.sasl.client.callback.handler.class = software.amazon.msk.auth.iam.IAMClientCallbackHandler
```

### Start Kafka REST proxy on EC2 Client

1. Navigate into the Confluent directory from earlier, and then into the `bin` directory.
2. Start the Kafka REST proxy with `./kafka-rest-start /home/ec2-user/confluent-7.2.0/etc/kafka-rest/kafka-rest.properties`