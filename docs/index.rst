.. Maiduo HTTPAPI documentation master file, created by
   sphinx-quickstart on Thu May  9 13:30:11 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==========================================
Maiduo HTTPAPI's documentation!
==========================================

用户认证
--------

.. http:post:: /api/authentication/

   用户认证，获取用户的token。

   当存在device_token字段时，将登记设备用于接受消息推送。

   **响应**:

   .. sourcecode:: http

      HTTP/1.1 201 OK
      Content-Type: application/json

      {
          "access_token": "a80ba5617b6c4ec6acae2475a9cbdaee",
          "token_type": "bearer",
          "user": {
              "username": "test",
              "first_name": "",
              "id": 1
          },
          "refresh_token": "139881d1e4ad4fb18038287453f951a2"
      }

   :form username: 手机号码
   :form password: 密码
   :form device_token: [可选] iOS设备Token
   :statuscode 201: 创建成功


/api/user/
------------

.. http:post:: /api/user/

   注册新用户

   新版API将会发送验证短信到用户手机，届时一个将会对同一手机的注册严格控制频率。

   :form username: 手机号码
   :form password: 密码
   :statuscode 201: 创建成功

/aps/device/
------------

.. http:post:: /aps/device/

   注册设备，在didRegisterForRemoteNotificationsWithDeviceToken中注册Token
   如果Token更改或者第一次启动应用。

   **响应**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "pk": 1,
         "model": "ios_notifications.device",
         "fields": {
           "deactivated_at": null,
           "users": [],
           "service": 1,
           "platform": "",
           "last_notified_at": null,
           "is_active": true,
           "added_at": "2013-05-09T07:17:39Z",
           "os_version": "",
           "token": "a4faf00f4654246b9fd7e78ae29a49b321673892ae81721b8e74ad9d285b3c27",
           "display": ""
         }
       }

   :form service: 服务的ID，通常是1。
   :form token: iOS设备的Token。
   :statuscode: 201

/aps/push/
-----------

.. http:post:: /aps/push/

  推送消息到iOS设备。

  官方专用API，需要发送Base-Auth验证有权限的账号。

  :form tokens: 设备Token - 逗号分隔多个Token，token1,token2。
  :form message: 推送消息内容。
  :form badge: 推送的badge数量。
  :form sound: 推送的声音。
  :form service: 服务的ID，通常是1。区别不同的推送服务，主要是在开发和生产环
                 境对推送的service是区别开的。
  :form extra: 自定义的推送的内容，JSON格式。
  :form persis: 持久化，数据库中保留该次推送。
  :form no-persist: 不持久化，数据库不保留该次推送。
  :statuscode 201: 发送成功

/api/activity/
--------------

.. http:get:: /api/activity/

   拉取活动列表。

   **响应**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "id": 2,
          "subject": "The second activity."
          "owner": {
            "username": "test",
            "first_name": "",
            "id": 1
           },
          "user": [
            {
              "username": "test",
              "first_name": "",
              "id": 1
            }
          ],
        }
      ]

   :query page: 分页
   :query access_token: Access token
   :statuscode 200: 成功

.. http:post:: /api/activity/

   创建活动，当邀请的用户注册时自动成为活动的成员。

   **响应**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "id": 2,
        "subject": "The second activity."
        "owner": {
          "username": "test",
          "first_name": "",
          "id": 1
         },
        "user": [
          {
            "username": "test",
            "first_name": "",
            "id": 1
          }
        ],
      }

   :form subject: 活动标题
   :form invitations:邀请朋友，格式是手机号码，半角逗号分割多个号码。
   :form access_token: Access token
   :statuscode 200: 成功


消息
----

最新的消息
^^^^^^^^^^

.. http:get:: /api/message/

   **响应**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      }

   :query page: 分页，默认是0。
   :statuscode 200: no error

创建一条新的消息
^^^^^^^^^^^^^^^^
.. http:post:: /api/message/

   创建新的消息，默认为暂存，暂存消息创建时不显示在时间线中，也不会推送内容给设\
   备。

   在上传大量附件的时候可以把消息设置成暂存消息，待所有附件上传完毕后恢复到正常\
   状态，避免用户设备显示不完整的内容。

   **响应**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

   :form stash: 暂存 1 is True 0 is False，default is 1
   :form text: 消息的文本内容。
   :statuscode 201: 创建成功

创建一个消息附件
^^^^^^^^^^^^^^^^

.. http:post:: /api/message/addon/

   消息本身只包含文本数据，图片，视频等其他额外的内容以附件的形式存在。

   **响应**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

   :form message: int
   :form key: 附件的键名
   :form width: int
   :form height: int
   :form size: int
   :form extra: 附件数据

/api/chats/
-----------

.. http:get:: /api/chats/

   获得聊天纪录。

   **响应**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
        {
          "chat_id": 1001,
          "text": "Chat text 1001.",
          "created_at": "",
        },
        {
          "chat_id": 1002,
          "text": "Chat text 1002.",
          "created_at": "",
        }
      ]


   :query page: 分页
   :query access_token: Access token
   :statuscode 200: 成功

/api/chat/
----------

.. http:get:: /api/chat/

   获得聊天内容，当聊天内容超过字数后，需要从这个资源里获得完整的内容。

   **响应**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "id": 1,
          "text": "hello",
          "activity": {
              "id": 1,
              "subject": "Activity subject.",
              "owner": [
                  {
                      "id": 1,
                      "first_name": "CJ"
                  }
              ],
              "users": [
                  {
                      "id": 1,
                      "first_name: "CJ"
                  }
              ]
          },
          "created_at": ""
      }

   :query id: chat ID
   :query access_token: Access token
   :statuscode 200: 成功

.. http:post:: /api/chat/

   发送聊天，成功以后会给该活动下所有成员发送聊天内容（除了发送者本人）。

   :form activity_id: 活动ID
   :form text: 聊天内容
   :form access_token: Access token
   :statuscode 201: 创建成功

Release Notes
-------------

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

