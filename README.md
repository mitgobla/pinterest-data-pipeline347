# Pinterest Data Pipeline

Creating a similar system to Pinterest using the AWS Cloud.

## Contents

- [Pinterest Data Pipeline](#pinterest-data-pipeline)
  - [Contents](#contents)
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

## Setup Instructions

### Configuring EC2 Client

#### Saving Private Key for SSH access

1. In AWS, access the Parameter Store to find the `KeyPairId` using your User ID.
2. Click **Show**, and copy the value of this parameter.
3. Paste this into a file ending in the `.pem` extension.
4. Navigate to the EC2 Client, and find the client containing your User ID.
5. Select the instance, and under **Details** make a note of **Key Pair assigned at launch**
6. Set the name of the `.pem` key file to the **Key Pair assigned at launch** value. For example `<user_id>-key-pair.pem`
7. Additionally, make a note of the **Public IPv4 DNS**, this is the addressed used to connect to.

#### Converting to PuTTY `.ppk` private key

1. Open **PuTTYgen** key generator.
2. Click on **Load** and navigate to the location of the `.pem` key. Make sure filter is set to show all files, not `.ppk` files.
3. Once found and selected, make sure **Type of Key to generate** is set to **RSA**
4. Choose **Save private key** and store it in a secure location, with the name set to **Key Pair assigned at launch** noted previously.

#### Connecting to EC2 Client

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

### Setting up Kafka on EC2

#### Kafka Installation

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

#### Installing IAM authentication package

1. Navigate inside the Kafka `libs` directory (`cd kafka/libs`)
2. Download the IAM authentication package

```bash
wget https://github.com/aws/aws-msk-iam-auth/releases/download/v1.1.5/aws-msk-iam-auth-1.1.5-all.jar
```
3. Run `pwd` to get the full path to this directory, and append `aws-msk-iam-auth-1.1.5-all.jar` to the end. Make a note of this full path.

```bash
pwd # /home/ec2-user/kafka/bin/
```

4. This path needs to be added to an environment variable called `CLASSPATH`
   1. Edit the `.bashrc` file by running `nano ~/.bashrc`
   2. At the bottom of the file, add `export CLASSPATH=<full_path_to_iam_jar>`
   3. Save the file, and reload by running `source ~/.bashrc`
   4. Confirm the variable is set with `echo $CLASSPATH`

#### Retrieving IAM authentication information

1. On the AWS console, navigate to **IAM console**
2. Select **Roles** on the left.
3. Find a role in the following format: <UserID>-ec2-access-role
4. Make a note of the **IAM Role ARN** as it will be used later.
5. Go to **Trust Relationships** and select **Edit Trust Policy**
6. On the right click **Add a principal** and select **IAM roles** as the Principal type
7. Replace the value with the copied IAM Role **ARN**

#### Configuring the IAM authentication package

1. Back on the EC2 SSH session, navigate to the `bin` directory in Kafka.
2. Create a file called `client.properties` with `nano client.properties`
3. Paste the following into the file:

```t
# Sets up TLS for encryption and SASL for authN.
security.protocol = SASL_SSL

# Identifies the SASL mechanism to use.
sasl.mechanism = AWS_MSK_IAM

# Binds SASL client implementation.
sasl.jaas.config = software.amazon.msk.auth.iam.IAMLoginModule required awsRoleArn="Your Access Role";

# Encapsulates constructing a SigV4 signature based on extracted credentials.
# The SASL client bound by "sasl.jaas.config" invokes this class.
sasl.client.callback.handler.class = software.amazon.msk.auth.iam.IAMClientCallbackHandler
```

4. Replace `Your Access Role` with the previously copied **IAM Role ARN**
5. Save and exit from the file.


### Creating Kafka Topics

#### Retrieving MSK cluster information

1. On the AWS Console, navigate to **MSK console**
2. Select the cluster, and then click on **Client Information**
3. Copy the **Private endpoint (single-VPC)** string, this is the **Bootstrap Server string**
4. Copy the **Plaintext Apache ZooKeeper connection** string as well, for future use.

#### Creating topics

1. Back on the EC2 SSH session, navigate to the `bin` folder inside the Kafka folder.
2. Using the previously noted **Bootstrap Server string**, run the following command replacing `<BootstrapServerString>` and `<topic_name>`:

```bash
./kafka-topics.sh --bootstrap-server <BootstrapServerString> --command-config client.properties --create --topic <topic_name>
```

In this case, create topics with the following formats, replacing `<UserID>` with your AWS User ID.

- `<UserID>.pin`
- `<UserID>.geo`
- `<UserID>.user`