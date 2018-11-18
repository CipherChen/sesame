# SESAME OPEN（芝麻开门）

> Passwords in my own.

## 简介

我们通常有多种密码以及各种密码的变体，来应对临时的、永久的、重要的、不重要的网站的注册和登录。为了记住这些密码，我们煞费苦心，有用键盘位置的，有用诗句的，有用数学公式的，还有用（前）女友名字或者生日的。

但是，何必用人类不擅长的记忆来做这些枯燥的事情呢？

`Sesame` 是一个简洁（到只有一个源文件）的程序，通过这个程序，我们可以很方便地把“网站-用户名-密码”记录到一个文本文件中。再利用其它云盘，比如 [Dropbox](https://www.dropbox.com/)、[Anybox](https://www.qingcloud.com/products/anybox/) 等来实现存储到云端。

`Sesame` 有五大好处，可以完美地满足我对于密码管理的几个偏执的要求：

* 密码必须只有我自己能访问（毕竟都是敏感数据，这也是我一直不用其它商业密码管理平台的原因）
* 不能是明文存储
* 管理方便
* 同步方便（假如换电脑，不需要再重复管理）
* 免费：）

这五大优势，我概括其为 "Passwords in my own."

### 安全性

`Sesame` 默认的文本文件 在 **`~/.sesame/pwd`**，可以通过配置文件 `~/.sesame/config.yaml` 来修改。

那么怎么保证这个文本文件的安全性呢？

`Sesame` 通过 [公钥加密方法](https://en.wikipedia.org/wiki/Public-key_cryptography) 来实现密码的非明文存储以及解密。

除了加解密过程，`Sesame`绝对不会以任何形式运行在后台或读取密钥：）

因此，唯一需要注意的是，**非对称密钥对的私钥绝对要保管好**。一旦丢失，密码就再也找不回了。

## 安装

```
$ wget https://github.com/CipherChen/sesame/archive/master.zip
$ pip install master.zip
```

## 示例

```
$sesame --help
usage: sesame [-h] {E,D,A,R,L,O} ...

positional arguments:
  {E,D,A,R,L,O}
    E            [E]ncode a string.
    D            [D]ecode a string.
    A            [A]dd a user/site/password to pwd file.
    R            [R]emove a user/site from pwd file
    L            [L]ist user/site lists from pwd file.
    O            [O]pen(show) password for user on site.

optional arguments:
  -h, --help     show this help message and exit
```

1. 增加一个网站的密码（**`Add`**）

    ```
    $ sesame A www.sample.com sample_username -W sample_password
    # 目前对于MacOS，要求输入认证用户（默认是当前用户）的密码。
    Password:
    Password for user [sample_username] on site [www.sample.com] has been added successfully.
    Already copyed into system clipboard.
    ```

    密码文件可以查看 `~/.sesame/config.yaml`，默认是在 `~/.sesame/pwd`。
    ```
    $ cat ~/.sesame/pwd
    www.sample.com : sample_username : gAZ141OQEtytnoKCqzD+7UeXc...
    ```

2. 增加一个网站的密码，由系统生成16位包含大小写和数字的随机密码（**`Add`**）

    ```
    $ sesame A www.sample.com sample_username2
    Password:
    Password for user [sample_username2] on site [www.sample.com] has been added successfully.
    Password for user [sample_username2] on site [www.sample.com] is [BDvDcbTrE2HuSIHz].
    ```

3. 获取一个网站的密码（**`Open`**）

    ```
    $ sesame O www.sample.com sample_username
    Password:
    # MacOS做了安全性的优化，默认不会显示在终端上，而是自动把密码拷贝到系统的剪切板中。
    # Password for user [sample_username] on site [www.sample.com] is [sample_password].
    Already copyed into system clipboard.
    ```

4. 删除一个网站的密码（**`Remove`**）

    ```
    $ sesame R www.sample.com sample_username
    Password:
    User [sample_username] for site [www.sample.com] has been removed successfully.
    ```

这个程序还可以利用同样的方式进行编码和解码。

5. 解密（**`Decode`**）

    ```
    $ sesame D vg2tQ3IczdoChJe8FrQPQ8ZuovdnjDQ...  # 从 pwd 文件中查看最后一个字段的加密字符串
    Password:
    BDvDcbTrE2HuSIHz
    ```

6. 加密（**`Encode`**）

    ```
    $ sesame E BDvDcbTrE2HuSIHz
    Password:
    vg2tQ3IczdoChJe8FrQPQ8ZuovdnjDQ...
    ```

## Something more...

此外，还有其它更多功能，欢迎探索和挖掘。

更欢迎geek们提交PR～
