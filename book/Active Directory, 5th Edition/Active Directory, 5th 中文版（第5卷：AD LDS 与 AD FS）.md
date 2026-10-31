---
summary: Active Directory（第5版·第5卷），全面介绍活动目录轻型目录服务（AD LDS）的应用与部署，以及活动目录联合身份验证服务（AD FS）的企业级单点登录、声明式身份与外部信任体系构建。
---

## 第 20 章 活动目录轻型目录服务

在微软发布 Windows 2000 Active Directory 后不久，开发人员和管理员便开始寻求一种独立的 Microsoft LDAP 服务，该服务应类似于 Active Directory，但无需承担其额外开销（例如 DNS 和 FRS 要求、组策略( Group Policy )，以及 Kerberos 和旧版 SAM 互操作性等其他域组件）——基本上，就是一种轻量级、易于设置、可随意使用并在需要时轻松拆除的服务。虽然使用 Active Directory 也能实现这一目的，但往往需要额外的清理和配置工作，而且与 LDAP 功能无关的组件可能会受到干扰，导致整个系统出现故障。

2003 年 11 月，在 Windows Server 2003 Active Directory 发布后不久，微软在 Web 上发布了活动目录应用程序模式( Active Directory Application Mode ,ADAM )V1.0。这正是开发人员和管理员一直期待的产品：Active Directory Lite。ADAM 允许开发人员和管理员在 Windows XP 或 Windows Server 2003 及更高版本的服务器上使用 Active Directory，而无需将本地主机提升为完整的域控制器( Domain Controller ,DC)。唯一的 DNS 要求是解析主机名。没有 FRS，没有 Kerberos，没有组策略，也没有额外的域组件。事实上，ADAM 可以像普通 Windows 应用程序一样良好运行，既能利用任何可用的 Windows 域身份验证或本地计算机身份验证，也能提供完全特定于应用程序的自身身份验证机制。它在域环境中和独立计算机上同样表现出色。

ADAM 发布后，微软继续对该产品进行投入，从 Windows Server 2003 R2 起，ADAM 开始随 Windows 捆绑提供。在 Windows Server 2008 中，ADAM 被更名为活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS )，并作为服务器角色可从服务器管理器中安装。这一变化显著提升了 AD LDS 作为管理员可用解决方案的可见性。

由于这种增强的可见性，大小公司(包括微软)都在构建和部署基于 AD LDS 的应用程序。由于 AD LDS 除了在编程上与 Active Directory 兼容之外，没有任何历史遗留要求的包袱，因此默认情况下，它的开箱即用锁定程度要高得多。Active Directory 遵循“默认开启/启用/开放”的理念，而 AD LDS 则遵循“默认关闭/禁用/封闭”的方法。从安全角度来看，这很棒。另一个巨大的好处是，由于它们的相似性，许多经验丰富的 Active Directory 管理员和开发人员将能够快速熟悉 AD LDS，从而促进管理、管理和监控以及应用程序开发。

AD LDS 可以适应无数场景，我们可以用一本小书来讨论这些场景。但是，本章仅旨在介绍 AD LDS 工具集。在整个讨论中，我们通常将 Active Directory 轻型目录服务称为 AD LDS，但有时您可能会看到对 ADAM 的引用，即以前的首字母缩略词。

### 20.1. AD LDS 的常见用途

阅读本章时，您会发现 AD LDS 极其灵活。它引入了许多新功能，使您能够实现传统林可能无法完成的用例。为了让您思考 AD LDS 如何帮助您的组织，让我们花点时间讨论几个常见的部署场景。

我们经常看到的第一个场景是将 AD LDS 用作管理员和软件开发人员的测试与开发 LDAP 服务器。AD LDS 可以安装在 Windows 7 上，并以与在服务器上相同的方式使用。管理员通常使用 AD LDS 在模拟 Active Directory 的隔离、可丢弃环境中开发和测试架构扩展。您可以从 [microsoft.com](http://bit.ly/10ePC4z) 下载适用于 Windows 7 的 AD LDS。下载并执行该包后，您可以从控制面板访问“程序和功能”，然后单击“打开或关闭 Windows 功能”来安装 AD LDS，并使本章讨论的管理工具在您的工作站上可用。

您还可以使用 AD LDS 提供一个统一的虚拟目录，将多个受信任域和林中的用户对象抽象为单一视图，供期望所有用户都位于同一位置的应用程序使用。通过使用本章后面讨论的用户代理，您可以为组织中的每个用户创建用户对象，但依赖现有的 Active Directory 域来存储用户密码。由于 AD LDS 可以在单台服务器上安装多次（尽管每个实例侦听不同的端口），您可能可以为每个具有自定义 LDAP 目录需求的应用程序运行一个 AD LDS 实例，而无需大量服务器或昂贵的第三方虚拟目录产品。

最后，一些应用程序开始利用 AD LDS 作为轻量级、可复制的多主机配置存储/目录。我们知道许多第三方正在这样做，此外还有各种 Microsoft 产品，例如 Exchange Server 和 Forefront Threat Management Gateway。

### 20.2. AD LDS 术语

本章通篇会用到若干术语。以下是一些简要定义,帮助你理解相关概念:

- **实例( Instance )**

  实例是 AD LDS 在服务器上的单次安装。每台服务器可以安装多个 AD LDS 实例;这些实例将各自独立管理,并使用不同的 LDAP 和 LDAPS 端口。

- **配置集( Configuration set )**

  一组相互复制、共享同一架构( Schema )和配置容器( Configuration container )的 AD LDS 实例。组成配置集的各实例之间也可以共享应用程序分区。

- **副本( Replica )**

  属于某个配置集、并与其他 AD LDS 实例进行复制的 AD LDS 实例。

- **分区/命名上下文( Partition/naming context )**

  以根 DN 命名的唯一命名空间。每个 AD LDS 实例至少有两个分区:配置分区和架构分区。AD LDS 还可以有多个应用程序分区。

- **应用程序分区( Application partition )**

  一种包含应用程序数据的分区。每个 AD LDS 实例可以有多个应用程序分区。

- **配置分区( Configuration partition )**

  一种包含实例或配置集配置数据的分区。

- **架构分区( Schema partition )**

  一种包含类和属性定义的分区。

- **可绑定对象( Bindable object )**

  从某个 `objectClass` 实例化而来的对象,该 `objectClass` 的架构定义中将 `msDS-BindableObject` 列为静态辅助类。最常见的可绑定对象是 `user` 类。此类型的对象由 AD LDS 直接进行身份验证。

- **可绑定代理对象( Bindable proxy object )**

  从某个 `objectClass` 实例化而来的对象,该 `objectClass` 的架构定义中将 `msDS-BindProxy` 列为静态辅助类。最常见的可绑定代理对象是 `userProxy` 类。此类型的对象由 AD LDS 通过将身份验证请求代理到 Windows 来进行身份验证。

### 20.3. AD 与 AD LDS 的区别

AD LDS 与 AD 颇为相似，但显然也存在差异，否则就没有讨论的必要了。本节并非旨在全面罗列所有差异，而是试图提炼出其中的重大变化与常见陷阱。

#### 独立应用程序服务

最显著的区别在于，AD LDS 被设置为以独立应用程序服务的形式运行；它并非关键的系统级服务。这意味着 LDAP 功能不再由 *lsass.exe* 进程处理，而是从 *dsamain.exe* 进程运行。其不太明显的优势在于，AD LDS 可以按需停止或启动，而无需重启计算机。这也意味着 AD LDS 可以根据需要进行更新（同样无需重启计算机）。

除了可按命令停止和启动这一优势外，新的服务实现方式还允许你在单台计算机上设置多个 AD LDS 实例，每个实例运行在不同的服务之下。因此，与一台计算机上仅有一个 Active Directory 实例在端口 389 上响应请求不同，你可以在单台计算机上运行多个 AD LDS 实例，监听不同的端口，且每个实例拥有完全不同的架构。

#### 可配置的 LDAP 端口

另一个区别是，借助 AD LDS，你实际上可以控制 LDAP 服务所监听的端口。Active Directory 似乎有一些注册表项可供修改以指定端口，但遗憾的是，这不过是个幌子：端口实际上硬编码在二进制文件中，因此你虽然可以在注册表中修改它们，却不会产生任何实际效果。

#### 没有 SRV 记录

活动目录轻型目录服务(Active Directory Lightweight Directory Services, AD LDS)不会像 Active Directory 那样在域名系统(Domain Name System, DNS)中注册 SRV 记录；遗憾的是，即使你代表 AD LDS 注册自己的 SRV 记录，也无法让域控制器(Domain Controller, DC)定位 API 调用找到 AD LDS 实例。网络跟踪显示有两个原因。第一个原因是 DC 定位器服务不会查看 SRV 记录的端口字段，所以如果 AD LDS 运行在不同的端口上，DC 定位器服务就无法连接到它。第二个原因是 DC 定位器服务会向主机发送特殊的 用户数据报协议(User Datagram Protocol, UDP) 轻量目录访问协议(Lightweight Directory Access Protocol, LDAP) ping，而 AD LDS 不知道如何响应该请求。当然，这一切都合情合理，因为 AD LDS 不是域控制器，但如果具备该功能，使应用程序利用 AD LDS 更加无缝，那就更好了。

AD LDS 可以在 Active Directory 中发布 `serviceConnectionPoint` (服务连接点(Service Connection Point, SCP)) 对象以进行资源定位，而不是使用 SRV 记录。这些对象位于 Active Directory 中，通常发布在安装了该服务的计算机对象下（这是可配置的）。`serviceConnectionPoint` 对象在 `keywords` 和 `serviceBindingInformation` 属性中维护有关 AD LDS 安装的关键信息。这些信息的示例在 示例 20-1 中列出。



示例 20-1. AD LDS SCP 示例


```
>keywords: partition:DC=joeware,DC=net
>keywords: 1cf21445-f4f5-4451-bff2-d32f511c478b
>keywords: 42eca3c5-ee95-48c8-ab7d-7524ae887239
>keywords: partition:DC=domain,DC=com
>keywords: 9549ae64-a3ee-461a-918f-828f522b0382
>keywords: partition:CN=newpart
>keywords: 450d8cf9-19de-4c3c-817d-d5443fb968f5
>keywords: partition:CN=user
>keywords: partition:DC=test,DC=etherpunk,DC=local
>keywords: 7547aa81-51ad-416f-9ee6-7bfd1f88853d
>keywords: partition:DC=mytest,DC=com
>keywords: c4d69674-b673-45f9-ad14-b1e488d4a0c8
>keywords: 0a891bbf-1be6-4fe4-9406-3f21355e144e
>keywords: partition:DC=set-con,DC=org
>keywords: 81b58144-7068-410b-bd93-8248109a329b
>keywords: partition:DC=etherpunk,DC=local
>keywords: partition:CN=Configuration,CN={E28AE3C2-1228-4F6B-917C-56B9757DB796}
>keywords: 47abf207-536a-4ea4-9295-9ef3c7f1fb8c
>keywords: fsmo:naming
>keywords: fsmo:schema
>keywords: instance:ADAM1
>keywords: site:Default-First-Site-Name
>keywords: 1.2.840.113556.1.4.1791
>keywords: 1.2.840.113556.1.4.1851
>keywords: 14b5dcce-8584-4100-8d5b-139b1e8a95b1
>serviceBindingInformation: ldaps://adamserver.mycorp.com:636
>serviceBindingInformation: ldap://adamserver.mycorp.com:389
```


正如你在示例中所见，`serviceBindingInformation` 属性显示了实际使用的主机名和端口：




```
>serviceBindingInformation: ldaps://adamserver.mycorp.com:636
>serviceBindingInformation: ldap://adamserver.mycorp.com:389
```


在 `keywords` 属性中，还有更多有用的信息。以下是一些关于可用分区的更有用信息：




```
>keywords: partition:DC=joeware,DC=net
>keywords: partition:DC=domain,DC=com
>keywords: partition:CN=newpart
>keywords: partition:CN=user
>keywords: partition:DC=test,DC=etherpunk,DC=local
>keywords: partition:DC=mytest,DC=com
>keywords: partition:DC=set-con,DC=org
>keywords: partition:DC=etherpunk,DC=local
>keywords: partition:CN=Configuration,CN={E28AE3C2-1228-4F6B-917C-56B9757DB796}
```


以下是此实例持有的灵活单主机操作(Flexible Single Master Operations, FSMO)：




```
>keywords: fsmo:naming
>keywords: fsmo:schema
```


实例所在的站点：




```
>keywords: site:Default-First-Site-Name
```


映射到主机上实际服务名称的实例名称：




```
>keywords: instance:ADAM1
```


以及一些描述实例功能的对象标识符(Object Identifier, OID)：




```
>keywords: 1.2.840.113556.1.4.1791
>keywords: 1.2.840.113556.1.4.1851
```


如果你愿意，可以添加其他关键字，以帮助你的应用程序选择正确的实例或命名上下文。有关为 AD LDS 使用 `serviceConnectionPoint` 对象的更多信息，请参阅以下内容：

- [管理 AD LDS 服务发布](http://bit.ly/YJtzTa)
- [服务连接点(SCP)与 ADAM/AD LDS](http://bit.ly/10ePLF5)
- [复制、基于主机和数据库服务的服务连接点](http://bit.ly/10afIXR)

#### 无全局编录( Global Catalog ,GC)

Active Directory 提供全局编录，使你可以轻松查询整个林( Forest )层次结构中的对象。你向特殊端口发送标准 LDAP 查询，即可访问林中所有对象的属性子集。单个查询就允许你搜索配置容器( Configuration container )、架构( Schema )以及林中的每个默认域分区( default domain partition )。活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)有多个分区，但没有匹配的全局编录功能。幸运的是，Windows LDAP 服务器接受一种特殊的 LDAP 控件设置，允许你使用单个查询扫描 AD LDS 实例的所有分区（或分区子集，如 `DC=com`）。遗憾的是，此功能仅适用于基于 LDAP API 的应用程序，不适用于 Active Directory 服务接口( Active Directory Service Interfaces ,ADSI )脚本和程序。

> **注意**：我们刚刚描述了 `LDAP_SERVER_SEARCH_OPTIONS_OID` LDAP 服务器控件。此控件与 `SERVER_SEARCH_FLAG_PHANTOM_ROOT` 标志结合，可启用特殊的全实例搜索功能。该控件也适用于 Active Directory，但由于全局编录功能，通常并不需要。有关详细信息，请参阅[此链接](http://bit.ly/16YMTm3)。

有一种选项可能适用于 ADSI 以及任何未实现适当 LDAP 控件的第三方应用程序。它涉及自行实现 GC 功能：设置另一个顶级应用程序分区( application partition )，并从其他应用程序分区同步特定对象和属性。然后，向需要查询整个实例的应用程序和用户授予只读访问权限，并向同步应用程序授予完全控制权限。如果你只是想基于几个公共属性（如 `sAMAccountName`）快速查找对象的 DN，此选项可能适合你。

全局编录的缺失还会影响 Outlook 和 Exchange 使用的一种特殊协议，主要用于通讯簿( Address Book )功能。名称服务提供程序接口( Name Service Provider Interface ,NSPI )及后端通讯簿支持功能仅在全局编录代码中提供。移除 GC 功能也会移除 NSPI 和通讯簿功能。

#### 顶级应用程序分区对象类

在 Active Directory 中,所有应用程序分区( Application Partition )都必须是 `domainDNS` 类的对象。而活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)则允许应用程序分区为任意类,只要该对象属于容器类型即可。这意味着应用程序分区可以有多种不同类型,包括 `organizationalUnit`、`container`、`o`、`c`、`l`,甚至 `user`。



#### 组和用户的作用域

AD LDS 组或用户的作用域仅限于其所在的分区;例如,在分区 1 中创建的组或用户,既不能用于为分区 2 中的对象分配权限,也不能添加到分区 2 中的组。不过,你可以将配置分区( Configuration Partition )中的 Windows 安全主体( Security Principal )和 AD LDS 安全主体添加到其他分区的组中。

#### FSMO 角色

在 Active Directory 林中,整个林有两个灵活单主机操作( Flexible Single Master Operations ,FSMO )角色,即架构主机( Schema Master )和域命名主机( Domain Naming Master );而每个域各有三个 FSMO 角色,即 PDC 仿真器( PDC Emulator )、RID 主机( RID Master )和基础结构主机( Infrastructure Master )。单域林的 FSMO 角色总数为五个,双域林为八个,依此类推。而活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS )则不同,无论分区( Partition )数量多少、副本( Replica )数量多少,它都只有两个 FSMO 角色。这两个角色是命名主机( Naming Master )和架构主机,其作用分别对应 Active Directory 的域命名主机和架构主机。与 Active Directory 一样,若要添加新分区,必须联系命名主机;若要更新架构,必须联系架构主机。

考虑到 AD 与 AD LDS 之间的功能差异,少了这几个 FSMO 角色通常并不令人意外。不过,RID 主机角色的缺失可能会让部分管理员感到困惑,因为 AD LDS 仍然使用安全标识符( Security Identifier ,SID ),而 SID 必须唯一才有价值。Active Directory 域中的 RID 主机可确保所创建的每个安全主体( Security Principal )都具有唯一的 SID 值,以便在域内唯一标识该主体。Active Directory 中对此采用众所周知的方式处理:沿用 NT4 所用的基本机制,即 RID 在分发时按顺序递增。AD LDS 改变了这一流程,因此不再需要 RID 主机。

AD LDS 不再使用 RID,而是采用一种基于全局唯一标识符( Globally Unique Identifier ,GUID )生成算法的算法来生成唯一的 SID。SID 中不再只是 RID 唯一,而是为每个用户生成 SID 中的最后四个子授权机构( Subauthority )。尽管其中某个或某几个子授权机构可能与其他组或用户相同,但四个值全部发生冲突的可能性应当不存在,因为 AD LDS 会尽力确保其唯一性。这意味着不再需要 RID 主机。“Windows SID 与 AD LDS SID 之比较”边栏介绍了 AD LDS 安全标识符的差异。有关 Windows SID 的详细信息,请参阅第 2 章中的边栏“安全标识符( SID )中包含什么?”(第 17 页)。



Windows SID 与 AD LDS SID 之比较

正如你在第 2 章中所回想到的,Windows SID 通常由 2 个固定字段和最多 15 个附加字段组成,各字段之间均以短横线分隔,如下所示:




```
S-v-id-s1-s2-s3-s4-s5-s6-s7-s8-s9-s10-s11-s12-s13-s14-s15
```

第一个固定字段( `v` )描述 SID 结构的版本。Microsoft 从未更改过此版本,因此它始终为 1。

第二个固定字段( `id` )称为标识符颁发机构( Identifier Authority )。在 Windows 域和 Windows 计算机中,它唯一标识所涉及的颁发机构,例如 NULL (0)、World (1)、Local (2)、NT Authority (5) 等。

接下来的 15 个字段( `s1–s15` )并非每个 SID 都需要,事实上,大多数 SID 只填充了其中少数几个字段。这些附加字段称为子颁发机构( Subauthority ),有助于唯一标识所引用的对象。大多数 SID 上的最后一个子颁发机构通常称为 RID。域或计算机正是通过递增此值来创建唯一 SID。

AD LDS 对 AD LDS  trustee( Trustee )和安全主体( Security Principal )的 SID 字段用法做了些许改动。新格式如下所示:




```
S-v-id1-id2-r1-r2-r3-r4
```


第一个固定字段( `v` )仍然描述 SID 结构的版本。虽然各字段的用法略有修改,但 SID 结构的二进制格式完全相同;Microsoft 没有更改版本,它仍然始终为 1。

第二个和第三个固定字段( `id1–id2` )是标识符颁发机构,特定于目录分区( Directory Partition )。AD LDS 实例中的每个分区都将具有这两个值的唯一组合。

接下来的四个字段( `r1–r4` )并非每个 SID 都需要。内置组仅填充 `r1` ,并且填充的是众所周知的 RID 值。内置组包括 Readers( `514` )、Users( `513` )和 Administrators( `512` )。任何其他需要 SID 的已创建对象将使用随机生成值的唯一组合填充 `r1–r4` 。

在 AD LDS 中有可能遇到 Windows SID。它们很容易识别,因为它们遵循 Windows SID 格式而非 AD LDS 格式。这些 Windows SID 用于标识 Windows trustee( Trustee )或向 Windows trustee 授予 AD LDS 内部的权限。例如,你可以将某个 Windows 用户的 SID 添加到任意分区的 Administrators 组中,以授予该 Windows 用户对该分区的管理员权限。

#### 架构( Schema )

与默认的 Active Directory (AD) 架构相比，默认的活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)架构非常轻量。最初，它仅包含 44 个类和 268 个属性，相当稀疏。Microsoft 随 AD LDS 提供了几个 LDIF 文件，以便你可以扩充架构，从而实例化一些 Microsoft 标准对象，例如 `inetOrgPerson` 和 `user` 对象。进一步扩展架构完全受支持，其过程与扩展 AD 架构类似。

另一个区别是，使用 AD LDS 时，你可以在单台计算机上拥有多个架构。每个 AD LDS 实例都可以有自己的架构，并且你可以安装多个实例。

#### 服务帐户( Service Account )

AD 在域控制器( Domain Controller ,DC)上以 Local System 身份在 LSASS 进程中运行。AD LDS 服务以 *NT Authority\Network Service* 身份运行，或者你可以指定任何普通的 Windows 用户 ID。

#### 配置/架构分区名称( Configuration/Schema Partition Names )

AD LDS 与 AD 一样，同时具有配置分区( Configuration Partition )和架构分区( Schema Partition )。但不同于 AD 的是，它没有根域或根分区，因此这些关键分区的名称基于随机生成的 GUID，并且与实例中存在的应用程序分区( Application Partition )无关。例如：

```
CN=Configuration,CN={E28AE3C2-1228-4F6B-917C-56B9757DB796}
```

#### 默认目录安全设置( Default Directory Security )

Active Directory 中的默认安全设置极为开放。默认情况下，来自该域或任何受信任域的任何用户都可以查看大多数对象的大多数属性。对 AD 进行锁定加固的尝试可能会令人沮丧、困惑，并导致应用程序无法正常工作。AD LDS 则完全相反。默认情况下，除架构外，普通用户没有任何读取权限。应用程序分区上定义的唯一访问控制项( Access Control Entry ,ACE)是：Readers 组的读取权限、Administrators 组的完全控制权限，以及用于副本的 Instances 组执行复制所需的最低权限。

#### 用户主体名称( User Principal Name ,UPN )

Active Directory 的用户主体名称遵循 RFC 822 电子邮件地址格式规则。AD LDS 没有这种限制；不必使用 *joe@mycorp.com*，只需使用 *joe* 作为 UPN 即可。虽然 Active Directory 不强制 `userPrincipalName` 值的唯一性，但 AD LDS 实际上会强制实施这种唯一性。

#### 身份验证

在身份验证方面，有几处差异必须说明。首先是好消息：您不再受限于可绑定的对象类型。只要对象派生自架构定义中包含 `msDS-BindableObject` 辅助类的类，并且为 `unicodePwd` 设置了有效密码值，任何对象都可用于绑定。

下一处差异是，活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)可绑定对象只能使用简单绑定或摘要身份验证。这意味着，如果要对 AD LDS 用户或其他 AD LDS 可绑定对象进行安全绑定，而又不使用摘要身份验证，则必须设置证书并使用 SSL 加密通信通道。若要在没有 SSL 的情况下使用安全身份验证，必须对 Windows 本地用户或域用户使用简单身份验证和安全层( Simple Authentication and Security Layer ,SASL)绑定。默认情况下，AD LDS 用户可以通过标准 LDAP 端口，使用明文简单绑定进行身份验证。您可以在配置分区中对象 `CN=Directory Service,CN=Windows NT,CN=Services,CN=`*<Instance GUID>* 的 `msDS-Other-Settings` 属性中设置 `RequireSecureSimpleBind=1`，以覆盖此默认行为并强制要求 SSL。

这里要说明的最后一处差异是绑定重定向。AD LDS 允许您配置一个可绑定代理对象，将其链接到 Windows 用户。用户可以对 AD LDS 使用简单绑定，随后 AD LDS 会以安全方式将身份验证请求代理到 Windows。当应用程序无法直接使用 Windows 安全主体，或者您希望伪装后端 Windows 帐户时，可以使用此方式。可绑定代理还会将密码更改代理回 AD。

与 AD LDS 用户简单绑定身份验证不同，对 `userProxy` 对象使用简单绑定时，默认要求 SSL 连接。可以通过在前面所述的 CN=`Directory Service` 对象的 `msDS-Other-Settings` 属性中设置 `RequireSecureProxyBind=0` 来覆盖此默认行为。

#### 配置分区中的用户

活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)允许您在配置分区( Configuration Partition )中创建`user`和`userProxy`对象。随后，可以将这些用户添加到任何分区中的任何组。因此，您可以将用户添加到配置分区的 Administrators 组，该组嵌套在所有应用程序分区( Application Partition )的 Administrators 组中。这一更改使得 AD LDS 用户能够管理 AD LDS 实例，而无需再要求使用 Windows 用户。要启用此新功能，请在前面描述的 CN=`Directory Service`对象的`msDS-Other-Settings`属性中设置`ADAMAllowADAMSecurityPrincipalsInConfigPartition=1`。

#### 新增和更新的工具

早期版本的 AD LDS 面临的最大初始抱怨（也是部署障碍）之一是缺少工具。Microsoft 通过创建*ADSchemaAnalyzer*和*ADAMSync*等新工具，以及更新 AD Sites and Services 和 LDP 等现有 AD 工具以便与 AD LDS 协同工作，帮助解决了这一问题。我们稍后将介绍一些可用的工具。

### 20.4. AD LDS 安装

AD LDS 安装分为两个主要部分：安装基础组件和安装新实例。基础组件安装每台服务器只需执行一次，而每当您要安装新实例或现有实例的副本时，都需要执行新实例安装。



#### 安装服务器角色

基础安装非常简单，只需启动服务器管理器( Server Manager )并添加活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS )角色即可。安装完成后，您可以使用 AD LDS 安装向导在服务器上配置一个或多个实例。

#### 安装新的 AD LDS 实例

完成服务器角色安装后,您可能需要安装新的活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)实例。此过程也相当简单,尽管不如服务器角色安装那么简单。安装新实例时,您需要准备好表 20-1中列出的问题的答案。



表 20-1. 新实例安装问题

| 问题                                                         | 说明                                                         | 示例                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ----------------------------------------------------- |
| 唯一实例还是副本?(图 20-2) | 是要使用现有实例复制配置和架构,还是要创建一个全新的实例? | 唯一实例                                              |
| 实例名称?(图 20-3) | 该值会追加到字符串"ADAM_"之后,用于指定运行此实例的活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)服务名称,此名称会列在"添加/删除程序"对话框中。 | AddressBook                                           |
| LDAP 端口号?(图 20-4) | 用于侦听标准 LDAP 请求的 TCP 端口。                          | 389                                                   |
| SSL 端口号?(图 20-4) | 用于侦听基于 SSL 的安全 LDAP(LDAPS)请求的 TCP 端口。         | 636                                                   |
| 是否创建应用程序目录分区?(图 20-5) | 选择是否希望由实例创建过程创建应用程序分区。首次设置 AD LDS 时建议采用此做法。 | 是                                                    |
| 分区名称?(图 20-5) | 初始应用程序分区要使用的名称,仅当您决定在实例安装期间由 AD LDS 创建初始分区时才需要指定。 | `CN=addressbook`                                      |
| 数据文件位置?(图 20-6) | 您希望将 AD LDS 数据文件放在什么位置?                        | *E:\AD LDS\AddressBook\data*                          |
| 数据恢复文件?(图 20-6) | 您希望将 AD LDS 日志文件放在什么位置?                        | *E:\AD LDS\AddressBook\data*                          |
| 服务帐户?(图 20-7) | 用于运行此 AD LDS 实例的服务帐户。除非服务器是 NT4 域的成员,或者处于工作组中且您需要副本,否则建议使用网络服务( Network Service )。 | 网络服务                                              |
| 初始管理员?(图 20-8) | 最初应将此实例的管理权限分配给哪个组或用户?                  | 当前登录的用户                                        |
| 是否导入 LDIF 文件?(图 20-9) | 指定是否要导入 `user`、`userProxy`、`inetOrgPerson` 以及授权管理器( Authorization Manager )的部分基本 Microsoft 架构定义。 | 导入                                                  |
| 要导入的文件?(图 20-9) | 从显示的 LDIF 文件中选择要导入的文件。                       | *MS-InetOrgPerson.LDF**MS-User.LDF**MS-UserProxy.LDF* |

当你已就绪、能够回答表 20-1中的所有问题后,即可从控制面板或开始菜单的"管理工具"部分选择"活动目录轻型目录服务设置向导"( Active Directory Lightweight Directory Services Setup Wizard ,AD LDS Setup Wizard),启动实例安装(图 20-1)。




![Launching the AD LDS Setup Wizard](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663564.webp)


图 20-1. 启动 AD LDS 设置向导

> **注意**：你也可以运行 *%windir%\ADAM\ADAMinstall.exe* 来启动此向导。

这将启动一个标准的 Windows 安装向导。第一个重要对话框（参见图 20-2）会询问你是要安装活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS )的唯一实例，还是要创建现有实例的副本。副本将在安装 AD LDS 副本一节中介绍；目前，请选择“唯一实例”（默认选项）。当你安装唯一实例时，你创建的实例不与任何其他 AD LDS 实例关联，并且具有全新的 AD LDS 架构和所有默认配置设置。你将无法将此实例配置为与当前存在的任何其他实例进行复制，不过你可以创建另一个新实例并将其安装为此实例的副本。




![Setup Options dialog](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663565.webp)


图 20-2. 安装选项对话框

下一个对话框（参见图 20-3）允许你指定实例的名称。此名称会追加到字符串 `ADAM_` 之后，并用作运行该实例的服务的名称。该名称还会用于“添加/删除程序”对话框，以便你以后在需要时卸载此实例。服务器上安装的第一个实例的默认实例名称为 *Instance1*。如果你使用名称 *Instance1*，则下次默认实例名称将为 *Instance2*，依此类推。




![Instance Name dialog](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663566.webp)


图 20-3. 实例名称对话框

选择实例名称后，将显示一个对话框（参见图 20-4），允许你指定用于标准 LDAP 和 LDAPS 的端口。默认端口为 389 和 636；除非你确认应用程序足够灵活，允许指定其他端口，否则应继续使用这些端口。




![LDAP/LDAPS port selection](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663567.webp)


图 20-4. LDAP/LDAPS 端口选择

默认情况下，活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)中创建的唯一分区是配置分区( Configuration Partition )和架构分区( Schema Partition )。实例安装允许你在“应用程序目录分区( Application Directory Partition )”对话框中创建一个初始应用程序目录分区（请参阅图 20-5）。此对话框的默认选项是“否，不创建应用程序目录分区。”如果你更改默认值，请在“分区名称”（Partition name）字段中输入要创建的分区的可分辨名称( Distinguished Name ,DN)。




![Application Directory Partition dialog](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663568.webp)


图 20-5. 应用程序目录分区对话框

AD LDS 允许你选择数据库和日志文件的存放位置（请参阅图 20-6）。数据库文件位置在“数据文件”（Data files）字段中指定，其中包括 DIT 文件以及临时数据库 EDB 和 CHK 文件。事务日志文件位置在“数据恢复文件”（Data recovery files）字段中指定，其中包括保存数据库事务信息的日志文件。在高性能配置中，根据服务器的磁盘配置，通常建议将这两组文件分散到不同的物理驱动器上。至少，你可能需要将它们从默认位置移走，默认位置位于系统驱动器上的 *Program Files\Microsoft ADAM\<instancename>* 文件夹中。




![File Locations dialog](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663569.webp)


图 20-6. 文件位置对话框

Microsoft 已将 AD LDS 设计为默认以 *Network Service* 帐户运行。这一点很好，通常应坚持使用此默认设置。但是，如果你不想以 *Network Service* 运行，可以选择将安全上下文更改为你选择的任何 Windows 用户（请参阅图 20-7）。只有在以下情况下才需要进行此更改：你运行在 Windows NT4 域中，运行在工作组模式下并希望拥有副本，或者需要为具有共享名称的一组负载均衡的 AD LDS 服务器提供访问权限。在这些情况下，AD LDS 将需要使用专用的 Windows 帐户。




![Service Account Selection dialog](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663570.webp)


图 20-7. 服务帐户选择对话框

接下来遇到的对话框至关重要；你需要在此指定活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)实例的初始管理员（见图 20-8）。默认值为安装该实例的用户，但可考虑改用本地 Administrators 组，或者更好的做法是，创建一个专门用于管理此 AD LDS 实例的域组。

![AD LDS Administrators dialog](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663571.webp)

图 20-8. AD LDS 管理员对话框

与大多数其他 Windows 应用程序截然不同，服务器上的 Administrators 组无法控制 AD LDS 的内部数据或配置，除非将该组专门添加到配置容器( Configuration container )的 Administrators 组（或者，如果你愿意，称为角色）。从安全角度看，这很好；但万一你因某种原因无法访问该组中的用户，一旦如此，你就失去了对该实例的控制。

需要做出决定的最后一个对话框（见图 20-9）涉及 AD LDS 应导入哪些 LDIF 文件。默认不导入任何文件，这样只会提供 AD LDS 基础架构。但是，如果你希望通过这些 LDIF 文件添加功能，则应允许安装程序导入它们。如果稍后决定要合并其中任何架构更新，只需使用 *ldifde.exe* 导入即可。这些 LDIF 文件位于文件夹 *%windir%\ADAM* 中。

表 20-2 说明了这些 LDIF 文件。

表 20-2. AD LDS 实例安装 LDIF 文件

| 文件名 | 包含内容 |
| -------------------------------- | ------------------------------------------------------------ |
| *MS-AdamSyncMetadata.LDF* | 使用活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)同步所需的元数据架构扩展。 |
| *MS-ADLDS-DisplaySpecifiers.LDF* | 将 GUI 工具用于 AD LDS 所需的显示说明符( Display Specifier )架构和数据。 |
| *MS-AZMan.LDF* | Microsoft 授权管理器( Microsoft Authorization Manager ,AZMan)所需的对象和属性。AZMan 是一种基于角色的访问控制框架。 |
| *MS-InetOrgPerson.LDF* | `inetOrgPerson` 对象定义。 |
| *MS-User.LDF* | Active Directory `user` 定义。可绑定对象类,受信者存在于 AD LDS 中。 |
| *MS-UserProxy.LDF* | AD LDS `userProxy` 定义。可绑定对象类,受信者存在于 Windows 中(本地或域中)。 |
| *MS-UserProxyFull.LDF* | 带 `user` 类附加属性的 AD LDS `userProxy` 定义。可绑定对象类,受信者存在于 Windows 中(本地或域中)。 |

![AD LDS LDIF import dialog](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663572.webp)

图 20-9. AD LDS LDIF 导入对话框

完成 LDIF 文件对话框后,将显示一个“准备安装”对话框,其中列出您所做的选择。如果接受这些选择,请单击“下一步”;将创建 AD LDS 实例,并会看到一个对话框,提示您已成功完成 AD LDS 安装向导。单击“完成”以完成安装过程。

#### 安装 AD LDS 副本

安装活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS )副本( replica ),也称加入配置集( configuration set ),与创建全新的独立 AD LDS 实例非常相似。除了创建独立实例时需要回答的那些问题外,你还必须回答以下几个问题:要加入哪个配置集,以及要复制哪些内容。

加入配置集意味着你选择与另一个 AD LDS 实例(或副本)共享配置分区( configuration partition )和架构分区( schema partition ),就像同一林( forest )中的域控制器( Domain Controller ,DC )一样。此外,你还可以选择将全部、部分、一个或零个应用程序分区( application partition )复制到配置集中全部、部分、一个或零个其他副本上。图 20-10展示了在服务器 *SERVER1*、*SERVER2* 和 *SERVER3* 之间共享的一个复杂配置集。




![Complex configuration set](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663573.webp)


图 20-10. 复杂配置集

这看起来可能非常复杂,但实际配置起来却相当简单。你需要先规划好哪些分区应当放在哪里,然后逐个安装每个副本,并为复制配置好相应的应用程序分区。

将副本安装到配置集时,需要额外回答的问题列于表 20-3中。



表 20-3. 副本安装问题

| 问题 | 说明 | 示例 |
| ------------------------------------------------------------ | ------------------------------------------------------------ | -------------------- |
| 源服务器?(图 20-12) | 配置集( Configuration Set )中任意服务器的完全限定域名( Fully Qualified Domain Name ,FQDN),用于从该服务器复制初始配置。 | *k8devlds01* |
| 源服务器 LDAP 端口?(图 20-12) | 要加入的实例的 LDAP 端口。 | 389 |
| 配置集管理凭据?(图 20-13) | 在配置集中具有管理权限的用户的凭据。 | MYCORP\administrator |
| 要复制的应用程序分区?(图 20-14) | 要将哪些应用程序分区( Application Partition )(如果有的话)复制到此特定副本。 | `cn=addressbook` |

准备好表 20-1和表 20-3中各问题的答案后,即可像创建新实例时那样启动实例创建过程。进入设置选项对话框时,选择“现有实例的副本”(参见图 20-11)。




![Setup Options dialog](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663574.webp)


图 20-11. 设置选项( Setup Options )对话框

向导将继续沿用安装唯一实例时的流程,依次显示图 20-3 和图 20-4 中的对话框。此后,向导将开始显示一些新的对话框。第一个新对话框用于指定要加入的配置集中某个 AD LDS 实例的连接信息(见图 20-12)。你需要同时指定该服务器的完全限定域名( Fully Qualified Domain Name ,FQDN)以及该实例侦听 LDAP 连接所使用的端口。




![Configuration set instance information](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663575.webp)


图 20-12. 配置集实例信息

指定配置集实例的连接信息之后,还需要为该配置集指定管理凭据(见图 20-13)。这显然是为了确保你确实有权将新的 AD LDS 实例添加到该配置集中。如果任何人都能随意添加新实例,安全性就无从谈起了。




![Credentials for the configuration set join](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663576.webp)


图 20-13. 用于加入配置集的凭据

最后显示的新对话框如图 20-14 所示,你可以在其中选择希望由该特定副本( Replica )来保留哪些应用程序分区( Application Partition )的副本(如果有的话)。回顾图 20-11 可以看到,你可以选择配置集中存在的任意数量的应用程序分区。在非常简单的配置集中,可能只有一个应用程序分区,且该分区由所有副本共享。而在非常复杂的配置集中,副本数量可以任意多,每个副本既可以复制、也可以不复制任意数量的分区。同样地,复杂配置集的配置过程相当简单;但监控和管理则另当别论了。




![Application partitions to add to the replica](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663577.webp)


图 20-14. 要添加到副本的应用程序分区

此对话框之后,您将返回常规的唯一实例安装过程,下一个对话框是"文件位置"对话框,如图 20-6 所示。逐步完成向导其余的对话框,在向导末尾单击"完成"后,您就拥有了一个新的副本。

AD LDS 还有一些我们尚未提及的额外安装选项。您可以执行无人值守安装,也可以从介质安装应用程序。使用 *ADAMinstall.exe* 从命令行启动安装过程时,可以指定这些选项。键入 **`ADAMinstall /?`** 或参阅 AD LDS 帮助文件以了解更多信息。

> **注意**：配置完副本后，你常会注意到：该副本会立即与你在此前"加入配置集"( Joining a Configuration Set )对话框中指定的实例建立复制连接（图 20-12），但其他副本均未与新副本建立复制连接。这完全正常；新副本的信息传遍整个配置集、并构建出已纳入该新副本的相应复制拓扑，都需要一些时间。

若要加快这一过程，可以使用 *repadmin.exe* 命令行工具来生成这些连接。具体而言，要使用 */AddRepsTo* 开关。键入 *repadmin /experthelp* 即可获得该开关的帮助信息。*repadmin* 是判断复制状况是否健康、并修复所遇问题的最实用工具之一。这一点对活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS )和活动目录( Active Directory ,AD )同样适用。

#### 启用回收站

第 18 章介绍过的活动目录回收站( Active Directory Recycle Bin )，可在运行于 Windows Server 2008 R2 或更高版本 AD LDS 服务器上的 AD LDS 配置集中使用。启用回收站需要执行若干手动步骤。

如果你的 AD LDS 配置集最初是在 Windows Server 2008 R2 之前创建的，则必须先升级配置集架构并提升配置集的功能级别。首先，使用以下命令升级架构：




```
C:\Windows\ADAM> ldifde.exe -i -f MS-ADAM-Upgrade-2.ldf -s server:port -$ ad
amschema.cat
```


接下来，使用 Windows PowerShell 提升配置集的功能级别：




```
Set-ADObject -Identity `
'CN=Partitions,CN=Configuration,CN=<configuration set guid>' `
-Replace @{'msds-Behavior-Version'=4} -Server server:port
```




> **注意**：只有当所有 AD LDS 服务器都运行 Windows Server 2008 R2 或更高版本后，才能提升配置集的功能级别。

最后，即可为配置集启用活动目录回收站：




```
Enable-ADOptionalFeature 'Recycle Bin Feature' -Scope ForestOrConfigurationSet 
-Server server:port -Target 'CN=Configuration,CN=<configuration set guid>'
```




> **警告**：回收站一经启用便无法禁用。启用回收站还会导致无法回退配置集的功能级别。请务必先测试那些利用 DirSync 控制和/或搜索已删除对象的应用程序。

### 20.5. 工具

AD LDS 引入了一些新工具和其他更新工具，大多数 Active Directory 管理员应该对这些工具都很熟悉。仅为了获得这些工具，就值得部署 AD LDS。表 20-4 列出了 AD LDS 附带的所有工具。前四个工具位于 *%windir%\ADAM* 目录中。

表 20-4. AD LDS 工具

| 文件名 | 描述 |
| ------ | ---- |
| *ADAMinstall.exe* | AD LDS 实例安装程序。 |
| *ADAMsync.exe* | 将数据从 Active Directory 同步到 AD LDS。 |
| *ADAMuninstall.exe* | AD LDS 实例移除程序。 |
| *ADSchemaAnalyzer.exe* | 架构比较工具，用于协助进行架构差异分析和同步。可与 AD 和 AD LDS 配合使用。 |
| *dsdbutil.exe* | AD LDS 实例数据库管理工具。 |
| *dsmgmt.exe* | AD LDS 实例配置管理工具。 |

#### ADAM Install

ADAM Install 是通过选择“Active Directory 轻型目录服务安装向导”菜单启动的图形界面工具。您可以选择直接启动该应用程序以启用高级安装对话框，从而允许您从文件安装应用程序分区。如果您希望自动化 AD LDS 实例安装，还可以指定无人参与安装应答文件。

#### ADAM Sync

这是一个命令行工具，提供基本的同步功能，用于从 AD 填充 AD LDS 信息。它面向的是仅需要单向数据馈送、且不需要 Identity Integration Feature Pack（IIFP）或 Microsoft Forefront Identity Manager（FIM）额外开销的管理员，后两者均支持双向同步。

#### ADAM Uninstall

此工具允许您在命令行中从服务器移除 AD LDS 实例。

#### AD 架构分析器

这是一款极为实用的图形界面工具，能够分析两个 LDAP 目录架构(无论来自实时环境还是 LDIF 文件)，并以图形化方式展示它们之间的差异，即所谓的“增量”。该工具还能生成一个包含两个架构间所有差异的 LDIF 文件，便于您导入此 LDIF 文件以同步两者。当遇到供应商未提供显示更改的 LDIF 文件以便于审查的应用程序时，AD 架构分析器尤为有用。此外，您还可以利用 AD 架构分析器将开发环境中的架构更改导出至 LDIF 文件，为在生产环境中实施这些更改做好准备。

#### AD 架构 MMC 管理单元

您可以利用 Active Directory 架构 MMC 管理单元，以与管理 AD 架构相同的方式管理 AD LDS 配置集的架构。要连接到 AD LDS 配置集，请按照以下步骤操作：

1. 启动 AD 架构 MMC 管理单元。

   > **注意**：AD 架构 MMC 管理单元默认已安装但未注册。首次在服务器上使用前，需从提升权限的命令提示符中运行 `regsvr32 schmmgmt.dll`。注册 DLL 后，可通过开始→运行→输入 `mmc`，然后选择文件→添加/删除管理单元，并添加 Active Directory 架构来创建包含该管理单元的 MMC 控制台。

2. 在左侧根节点 Active Directory 架构上右键单击，选择“更改 Active Directory 域控制器”。

3. 选择“此域控制器或 AD LDS 实例”。

4. 双击“<在此处输入目录服务器名称[:端口]>”，并输入您的 AD LDS 服务器的 FQDN 及端口号。

#### ADSI Edit

可以使用 ADSI Edit 连接到 AD LDS 实例，与连接 AD 域非常类似。要连接到 AD LDS 实例，请右键单击左侧的 ADSI Edit 节点，然后单击“连接到”。指定要连接的分区的 DN 以及承载该分区的服务器（和端口），如图 20-15 所示。您还可以选择使用“高级”按钮指定用于连接的显式凭据。




![Connecting ADSI Edit to an AD LDS instance](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663578.webp)


图 20-15. 将 ADSI Edit 连接到 AD LDS 实例

ADSI Edit 包含一个特殊的组成员身份编辑器，在处理 AD LDS 时非常有用，因为它可以解析 SID 以将域用户添加到组中，还允许您在 AD LDS 组中嵌套 AD LDS 安全主体。图 20-16 显示了 ADSI Edit 组成员身份编辑器。




![ADSI Edit group membership editor](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663579.webp)


图 20-16. ADSI Edit 组成员身份编辑器



#### dsdbutil

*dsdbutil* 命令行工具具有 Active Directory *NTDSUTIL* 工具的一部分功能，仅用于管理 AD LDS。AD LDS 服务器可以使用 *ntdsutil* 进行管理，但 *dsdbutil* 是专门为 AD LDS 配置的，不能用于 Active Directory。您可以使用此工具执行所有底层数据库管理任务，例如权威还原、压缩文件、完整性检查等。



#### dsmgmt

与 *dsdbutil* 一样，*dsmgmt* 命令行工具具有 Active Directory *NTDSUTIL* 工具的一部分功能，并且专门配置用于 AD LDS 服务器。您可以使用此工具控制各种 AD LDS 配置设置、对已退役的 AD LDS 实例进行元数据清理，以及创建和删除命名上下文。



#### ldifde

*ldifde* 是一个命令行工具，用于以 LDIF 格式导入或导出 Active Directory 对象。与 *csvde* 不同，*ldifde* 可用于更新以及创建和删除 AD LDS 或 Active Directory 中的对象。LDIF 是用于所有基于 LDAP 的目录的标准格式，通常也是您从需要架构修改的应用程序接收架构更新信息时所采用的格式。对于 AD 和 AD LDS 管理员及开发人员来说，熟悉 LDIF 格式总体以及 *ldifde* 工具本身非常重要。

#### LDP

LDP 是一款图形用户界面( Graphical User Interface ,GUI)工具,用于浏览、搜索或更新活动目录( Active Directory ,AD)或活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)。你可以按树形层次结构查看目录,也可以构造标准轻量目录访问协议( Lightweight Directory Access Protocol ,LDAP)查询。LDP 几乎支持登录任意 LDAP 客户端或服务器控制项,还可用于查找已删除对象或其他需要特殊查询的项。如果你打算在 AD LDS 中管理安全描述符(访问控制列表, Access Control List ,ACL),那就需要熟悉 LDP。



#### repadmin

*repadmin* 命令行工具的基本功能是显示和管理一组目录服务器的复制拓扑。但 *repadmin* 用得越多,你会发现它能做的事也越多:从显示对象元数据到更新服务主体名称( Service Principal Name ,SPN),再到显示信任关系、转换时间戳等等。当你通过运行 *repadmin /?* 所显示的开关弄清了它的全部功能后,就可以进一步研究运行 *repadmin /experthelp* 时显示的额外开关了。

### 20.6. AD LDS 架构

如前所述，初始的活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)架构只是完整 Active Directory 架构的一小部分。不过，你可以像在 Active Directory 中一样扩展架构，因此如果需要，可以完全扩展架构，使其与 AD 架构相同。因此，AD LDS 是测试你希望在 Active Directory 中进行的架构修改的理想场所。由于扩展的工作方式完全相同，并且你可以快速销毁和重新创建 AD LDS 实例，这意味着你可以快速测试新的扩展，不断更改定义，直到获得完全符合需求的结果。你甚至可以在同一台计算机上同时运行多个实例，每个实例使用不同版本的架构，以便轻松进行比较和对比。有关使用架构、AD 和 AD LDS 的详细信息，请参阅第 5 章和第 17 章。

#### 默认安全描述符

与 Active Directory 架构中的情况截然不同，基础 AD LDS 架构的 `classSchema` 对象没有在其 `defaultSecurityDescriptor` 属性中定义任何访问控制项( Access Control Entries ,ACE)。这会导致创建的对象没有任何显式 ACE，除非在创建对象时指定了包含显式 ACE 的安全描述符。这样做的明显好处是，你的所有默认安全设置都基于继承的 ACE。正如你在第 16 章讨论 Active Directory 安全性时会回想起的那样，这使得配置委派变得容易得多。尽管对于添加到 AD LDS 的任何类，并不要求你遵循此模型，但*强烈*建议你这样做。除非有非常充分的理由，否则不应偏离此做法。

#### 可绑定对象与可绑定代理对象

如前所述,导入到 AD LDS 中的任何 `objectClass` 都可以配置为允许在 AD LDS 中执行绑定功能。绑定功能分为两种类型,分别由可绑定对象和可绑定代理对象实现。*可绑定对象*( bindable object )是由 AD LDS 直接进行身份验证的对象。可绑定对象(例如用户)会在 AD LDS 数据库中存储密码。*可绑定代理对象*( bindable proxy object )实际上是由 Windows 进行身份验证的对象。AD LDS 只是将身份验证请求代理到 Windows;`userProxy` 即为一例。

若要实例化给定 `objectClass` 的可绑定对象或可绑定代理对象,必须将 `msDS-BindableObject` 或 `msDS-BindProxy` 类静态关联为给定 `objectClass` 的辅助类。如果同时将这两个类关联到给定 `objectClass`,则 `msDS-BindableObject` 优先。



> **注意**：无法将现有的 `classSchema` 对象配置为具有其中任一辅助类;必须在 AD LDS 架构中最初定义该类时指定这些类。此限制是由于无法向现有的类定义添加强制属性。

### 20.7. 使用 AD LDS

现在您已经了解了什么是活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)以及如何安装它，您可能正面对一个空的 AD LDS，琢磨着：“接下来做什么？”本节将引导您完成一些常见且简单的任务，包括创建应用程序分区( Application Partition )并向其中填充一些数据。这些示例假设您已使用 *MS-User.LDF* 和 *MS-UserProxy.LDF* 文件安装了 AD LDS 实例。所有示例都将使用 LDAP 数据交换格式( LDAP Data Interchange Format ,LDIF) 文件和 *ldifde.exe* 进行更新，因为此工具适用于每个服务器，且无需脚本知识。如果您熟悉脚本编写或其他 LDAP 应用程序，也可以使用它们。



> **注意**：如果您更喜欢使用命令行工具而不是基于 GUI 的工具，请将您的 Web 浏览器指向 [http://www.joeware.net](http://www.joeware.net/) 并下载 *admod* 和 *adfind* 免费实用程序。这些命令行工具专门针对 Active Directory 和 AD LDS 进行了优化，并具有若干内置功能，可利用通过活动目录服务接口( Active Directory Service Interfaces ,ADSI) 无法获得的特殊功能。

#### 创建应用程序分区

通常，使用 AD LDS 并向其中添加数据的首要步骤是创建一个应用程序分区来存储这些数据。如果在实例安装期间已经创建了应用程序分区，那么除非您希望在同一实例中创建额外的应用程序分区，否则无需担心此步骤。

AD LDS 允许您使用任何容器类作为应用程序分区的根。如果您希望应用程序分区的根为 `container`、`domainDNS`、`organizationalUnit`、`c`、`o`，甚至 `user`，都可以轻松设置。创建应用程序分区只需指定三项数据：可分辨名称( Distinguished Name ,DN)、`objectClass` 和 `instanceType`。`instanceType` 属性的值必须始终为 `5`，因此您只需确定两个属性：DN 和 `objectClass`。

可分辨名称是分区根的完全限定名称。这是您访问应用程序分区时将使用的值。`objectClass` 是您希望根对象所属的类型，该选择将影响根的 DN。例如，如果您选择 `organizationalUnit`，则 DN 将以 `OU=` 开头。

以下示例将创建多个具有不同对象类的应用程序分区。如果您只想创建一个分区，请仅复制您希望使用的应用程序分区类型。

创建一个名为 *create_app_parts.ldf* 的 LDIF 文件，内容如下：




```
# Container-type application partition
dn: cn=AddressBook
changetype: add
objectClass: container
instanceType: 5

# Organizational Unit-type application partition
dn: ou=products
changetype: add
objectClass: organizationalUnit
instanceType: 5

# Domain DNS-type application partition
dn: dc=mycorp,dc=com
changetype: add
objectClass: domainDNS
instanceType: 5

# Organization (X.500)-type application partition
dn: o=mycorp,c=us
changetype: add
objectClass: organization
instanceType: 5
```


创建 LDIF 文件后，运行以下命令：




```
> ldifde -i -f create_app_parts.ldf -s <server>:<ldap_port>
```




> **注意**：您也可以使用 *ntdsutil.exe* 创建应用程序分区。



#### 创建容器

在 AD LDS 中创建容器与在 Active Directory 中创建容器完全相同。以下示例将在 *AddressBook* 应用程序分区根下创建多个容器。

创建一个名为 *create_containers.ldf* 的 LDIF 文件，内容如下：




```
# Users container
dn: cn=users,cn=AddressBook
changetype: add
objectClass: container

# User Proxies container
dn: cn=userproxies,cn=AddressBook
changetype: add
objectClass: container

# Groups container
dn: cn=groups,cn=AddressBook
changetype: add
objectClass: container
```


创建 LDIF 文件后，运行以下命令：




```
> ldifde -i -f create_containers.ldf -s <server>:<ldap_port>
```

#### 创建用户

在活动目录轻型目录服务(Active Directory Lightweight Directory Services,AD LDS)中创建用户与在 Active Directory 中创建用户类似。一个较为明显的差异是 AD LDS 用户没有 `sAMAccountName` 属性。尽管可以定义该属性并将其链接到 `user` 类，但它不会具有与 Active Directory 中相同的特殊属性，例如强制唯一性。

以下示例将在之前创建的 Users 容器下创建若干用户。

创建一个名为 *create_users.ldf* 的 LDIF 文件，内容如下：




```
dn: cn=g.washington,cn=users,cn=AddressBook
changetype: add
objectClass: user
userPrincipalName: GWashington
mail: George_Washington@cohovines.com
displayName: Washington, George
telephoneNumber: 202.555.3452
userPassword: SecureInitialPassword1!

dn: cn=j.madison,cn=users,cn=AddressBook
changetype: add
objectClass: user
userPrincipalName: JMadison
mail: James_Madison@cohovines.com
displayName: Madison, James
telephoneNumber: 202.555.3453
userPassword: SecureInitialPassword1!

dn: cn=j.adams,cn=users,cn=AddressBook
changetype: add
objectClass: user
userPrincipalName: JAdams
mail: John_Adams@cohovines.com
displayName: Adams, John
telephoneNumber: 202.555.3455
userPassword: SecureInitialPassword1!

dn: cn=t.jefferson,cn=users,cn=AddressBook
changetype: add
objectClass: user
userPrincipalName: TJefferson
mail: Thomas_Jefferson@cohovines.com
displayName: Jefferson, Thomas
telephoneNumber: 202.555.3454
userPassword: SecureInitialPassword1!
```


创建 LDIF 文件后，运行以下命令：




```
> ldifde -i -f create_users.ldf -s <server>:<ldaps_port>
```




> **警告**：默认情况下，使用 *ldifde.exe* 在 Active Directory 中创建已启用的用户需要 128 位 SSL 连接，并且需要对引号内 Unicode 版本的密码进行 Base64 编码。有关详细信息，请参阅 http://support.microsoft.com/kb/263991。

对于 AD LDS，Microsoft 启用了 `userPassword` 属性，使其可作为 `unicodePwd` 的写入别名，并移除了 `unicodePwd` 所需的特殊格式要求。这样一来，您的 LDIF 文件便可以指定明文密码；不过，除非您已通过 *dsmgmt* 放宽了密码操作对安全连接的要求，否则仍然存在 SSL 要求。



> **注意**：Windows Server 2003 及更高版本的域控制器( Domain Controller ,DC)也能够使用 `userPassword` 属性代替 `unicodePwd`；但您必须通过 `dsheuristics` [属性](http://bit.ly/13ydHe0)启用该功能。

在 AD LDS 和 AD 中，`userPassword` 属性只能用于设置操作；如果您需要更改密码，则必须使用 `unicodePwd`，如 http://support.microsoft.com/kb/263991 所述。

使用 ADSI 脚本、*ldp.exe* 或命令行工具(例如前面提到的免费工具 *admod.exe*)处理密码要方便得多。

#### 创建用户代理

`userProxy objectClass` 是 AD LDS 新增的对象类。这类对象与用户类似,都表示可进行身份验证的受托方( trustee );不同之处在于,它们只是对 Windows 用户的引用,而不是这些用户的直接表示。`userProxy` 对象通过自身的 `objectSID` 属性指向某个 Windows 用户;该属性只能在创建对象时设置。

默认情况下,当某人使用 `userProxy` 进行身份验证时,必须使用该 `userproxy` 对象的可分辨名称( Distinguished Name ,DN)或用户主体名称( User Principal Name ,UPN),通过 SSL 对 AD LDS 执行简单绑定( simple bind )。首先,AD LDS 接受 `userProxy` 的 DN/UPN 和密码,然后从该对象中检索 SID 并将其解析为 Windows 用户(必要时还包括域);最后,使用该用户的安全账户管理器( Security Accounts Manager ,SAM )名称(必要时还包括 NetBIOS 域名)和密码执行安全的 `LogonUser` API 调用,以对该用户进行身份验证。如果用户身份验证成功,系统将生成其安全令牌( security token ),并且他将获得授予下列任一安全主体( security principal )的目录访问权限:

- `userProxy` 对象
- 该 Windows 用户所属的任何组
- 该 `userProxy` 所属的任何组

下面的示例将在前面创建的 userProxies 容器下创建一个 UserProxy 对象。

创建一个名为 *create_userproxies.ldf* 的 LDIF 文件,内容如下:




```
dn: cn=joeproxy,cn=userproxies,cn=AddressBook
changetype: add
objectClass: userProxy
objectSID: S-1-5-21-2571958876-650952397-806722693-1108
userPrincipalName: joeproxy
```


创建 LDIF 文件后,运行以下命令:




```
> ldifde -i -f create_userproxies.ldf -s <server>:<ldap_port>
```


在本示例中,域用户的 `objectSID` 在 *joeproxy* 的 `objectSID` 属性中指定。每当使用 *joeproxy* 用户绑定到 AD LDS 时,它都会通过 `LogonUser` 将该身份验证代理到 Windows,并依据示例中具有该 `objectSID` 的用户来验证所提供的凭据。

##### 特殊注意事项

`userProxy` 对象可以使用任何能够通过该活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)实例所在服务器的信任通道进行身份验证的 Windows 用户。这包括本地计算机用户、域用户和受信任域用户。如果选择使用本地用户，需要牢记：只有该用户所在的计算机才能对该用户进行身份验证。对于复制的 AD LDS 实例而言，这有明显影响；配置集中只有一个实例能够对该用户进行身份验证。如果只希望允许访问单个副本，这可能正是你想要实现的目标，但总体而言，如果让不熟悉此特殊配置的人参与进来，这会令人困惑且难以排查故障。

`userProxy` 对象的另一个特殊注意事项与对象创建有关。如果某个 Windows 用户的 SID 已作为 `foreignSecurityPrincipal` 添加到 AD LDS 实例，则不允许创建具有相同 SID 的 `userProxy` 对象。目录修改会被拒绝，并返回“unwilling to perform”错误。

#### 重命名用户

在任何包含用户信息的通讯簿或其他应用程序中，重命名操作都是一项常见任务。人们可能会结婚、离婚，或因其他原因更改姓名，并且通常希望这些更改能在包含其姓名的目录中得到反映。

以下示例将重命名之前创建的几位用户。

创建一个名为 *rename_users.ldf* 的 LDIF 文件，内容如下：




```
dn: cn=g.washington,cn=users,cn=AddressBook
changetype: modify
replace: userPrincipalName
userPrincipalName: George.Washington
-
replace: mail
mail: george.washington@cohovines.com
-
replace: displayName
displayName: George Washington
-
dn: cn=g.washington,cn=users,cn=AddressBook
changetype: modrdn
newrdn: george.washington
deleteoldrdn: 1
dn: cn=j.adams,cn=users,cn=AddressBook
changetype: modify
replace: userPrincipalName
userPrincipalName: John.Adams
-
replace: mail
mail: john.adams@cohovines.com
-
replace: displayName
displayName: John Adams
-
dn: cn=j.adams,cn=users,cn=AddressBook
changetype: modrdn
newrdn: john.adams
deleteoldrdn: 1
```


创建 LDIF 文件后，运行以下命令：




```
> ldifde -i -f rename_users.ldf -s <server>:<ldap_port>
```


每次重命名包含两个 LDAP 操作。第一个操作是替换几个存放旧名称的属性：具体而言，即 `userPrincipalName`、`mail` 和 `displayName`。第二个操作是重命名对象的相对可分辨名称( Relative Distinguished Name ,RDN )。此更新将强制更改 `user` 对象的 `cn`、`name` 和 `distinguishedName` 属性。



#### 创建组

在 AD LDS 中创建组与在 Active Directory 中创建组类似。与创建用户一样，您无需关注 `sAMAccountName` 属性，因此可以忽略该属性。

以下示例将在之前创建的 Groups 容器中创建多个组。

创建一个名为 *create_groups.ldf* 的 LDIF 文件，内容如下：




```
dn: cn=group1,cn=groups,cn=AddressBook
changetype: add
objectClass: group
dn: cn=group2,cn=groups,cn=AddressBook
changetype: add
objectClass: group
dn: cn=group3,cn=groups,cn=AddressBook
changetype: add
objectClass: group
dn: cn=group4,cn=groups,cn=AddressBook
changetype: add
objectClass: group
```


创建 LDIF 文件后，运行以下命令：




```
> ldifde -i -f rename_users.ldf -s <server>:<ldap_port>
```




#### 将成员添加到组

在 AD LDS 中使用 *ldifde.exe* 将成员添加到组，与 Active Directory 中的过程类似。您有两种选择：

- 在组的 `member` 属性的更新中指定用户、组或其他对象的 DN。
- 以 Base64 编码字符串的形式指定用户、组或其他对象的 SID，格式为 `SID=S-1-`*`xxx-yyyy....`*

遗憾的是，目前 Windows 用户必须以 SID 格式指定，除非该用户已作为 `userProxy` 或 `foreignSecurityPrincipal` 添加到 AD LDS 应用程序分区。一旦作为其中一种对象添加，Windows 用户便可通过该对象的 DN 进行引用。

以下示例将把用户和组作为成员添加到之前创建的组中。

创建一个名为 *add_ users.ldf* 的 LDIF 文件，内容如下：




```
dn: cn=group1,cn=groups,cn=AddressBook
changetype: modify
add: member
member: cn=george.washington,cn=users,cn=AddressBook
-
dn: cn=group2,cn=groups,cn=AddressBook
changetype: modify
add: member
member: cn=george.washington,cn=users,cn=AddressBook
member: cn=john.adams,cn=users,cn=AddressBook
-
dn: cn=group3,cn=groups,cn=AddressBook
changetype: modify
add: member
member: cn=group2,cn=groups,cn=AddressBook
member: cn=john.adams,cn=users,cn=AddressBook
member: cn=james.madison,cn=users,cn=AddressBook
-
dn: cn=group4,cn=groups,cn=AddressBook
changetype: modify
add: member
member: CN=Administrators,CN=Roles,CN=AddressBook
-
```


创建 LDIF 文件后，运行以下命令：




```
> ldifde -i -f add_users.ldf -s <server>:<ldap_port>
```

#### 从组中删除成员

在 AD LDS 中使用 *ldifde.exe* 从组中删除成员的过程与 Active Directory 类似。只需指定当前作为成员、且希望删除的用户、组或其他对象的 DN 即可。

以下示例将从之前创建的组中删除成员。

创建一个名为 *remove_ users.ldf* 的 LDIF 文件,内容如下:




```
dn: cn=group1,cn=groups,cn=AddressBook
changetype: modify
delete: member
member: cn=george.washington,cn=users,cn=AddressBook
-
dn: cn=group2,cn=groups,cn=AddressBook
changetype: modify
delete: member
member: cn=george.washington,cn=users,cn=AddressBook
member: cn=john.adams,cn=users,cn=AddressBook
-
dn: cn=group3,cn=groups,cn=AddressBook
changetype: modify
delete: member
member: cn=group2,cn=groups,cn=AddressBook
member: cn=john.adams,cn=users,cn=AddressBook
member: cn=james.madison,cn=users,cn=AddressBook
-
 dn: cn=group4,cn=groups,cn=AddressBook
changetype: modify
delete: member
member: CN=Administrators,CN=Roles,CN=AddressBook
-
```


创建 LDIF 文件后,运行以下命令:




```
> ldifde -i -f remove_users.ldf -s <server>:<ldap_port>
```




#### 删除对象

使用 *ldifde.exe* 删除对象通常非常简单。只要您拥有删除目标对象的权限,且该对象没有子对象,删除操作应该不会遇到问题。

以下示例将删除之前创建的组和容器对象。

创建一个名为 *remove_ objs.ldf* 的 LDIF 文件,内容如下:




```
dn: cn=group1,cn=groups,cn=AddressBook
changetype: delete
dn: cn=group2,cn=groups,cn=AddressBook
changetype: delete
dn: cn=group3,cn=groups,cn=AddressBook
changetype: delete
dn: cn=group4,cn=groups,cn=AddressBook
changetype: delete
dn: cn=groups,cn=AddressBook
changetype: delete
```


创建 LDIF 文件后,运行以下命令:




```
> ldifde -i -f remove_objs.ldf -s <server>:<ldap_port>
```




#### 删除应用程序分区

以编程方式删除 AD LDS 中的应用程序分区并没那么直观。创建分区时,您只需指定 DN、`objectClass` 和 `instanceType` 即可,别无其他要求。而删除应用程序分区时,则需要查看 `cn=partitions,cn=configuration,cn=`*`<instance GUID>`* 容器中的对象。找到 `nCName` 与要删除的应用程序分区相匹配的对象,并将该对象的 DN 复制到包含删除操作的 LDIF 文件中。

以下示例将删除之前创建的 `cn=AddressBook` 应用程序分区。

创建一个名为 *remove_app_part.ldf* 的 LDIF 文件,内容如下:




```
#>nCName: CN=AddressBook
dn:
  CN=45d599d5-9bd4-41be-9604-b8209db3f866,CN=Partitions,
  CN=Configuration,CN={92B82A0E-CEC4-4720-9035-D0CA9632C20E}
changetype: delete
```


创建 LDIF 文件后,运行以下命令:




```
> ldifde -i -f remove_app_part.ldf -s <server>:<ldap_port>
```




> **注意**：您也可以使用 *ntdsutil.exe* 删除应用程序分区。

#### 控制对对象和属性的访问

我们在第 16 章讨论了 Active Directory 的访问委派，其中讨论的所有概念也适用于活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)。但是，有两个关键区别。第一个，如本章前面简要提到的，与 AD 不同，AD LDS 开箱即用并不授予对目录的任何读取访问权限。这意味着作为管理员，你需要通过将用户和组嵌套到实例的 Readers 组中来授予完全读取访问权限，或者更精细地委派权限。第二个区别是你习惯使用的访问控制列表( Access Control List ,ACL )编辑器和控制委派向导( Delegation of Control Wizard )不能用于 AD LDS。你必须改用 LDP 实用程序中的 ACL 编辑器，不幸的是，它远没有那么用户友好。

可以通过以下步骤访问 LDP 的 ACL 编辑器：

1. 依次单击“开始”→“运行”，然后输入 **`ldp.exe`**，以启动 LDP。

2. 从“连接”→“连接”连接到服务器。输入承载要管理安全性的应用程序分区的 AD LDS 服务器的完全限定域名( Fully Qualified Domain Name ,FQDN )和端口。

3. 从“连接”→“绑定”(Ctrl-B)绑定到实例。可以选择“以当前登录用户身份绑定”以使用域凭据，或者指定备用凭据。

4. 通过选择“视图”→“树”(Ctrl-T)并选择应用程序分区，加载应用程序分区层次结构。

5. 右键单击要编辑 ACL 的对象，然后单击“高级”→“安全描述符”。单击“确定”。
   
   > **注意**：
   > 如果需要编辑审核设置，需要在上述对话框中勾选 SACL 复选框。

6. 在 DACL 列表框中单击，以启用对话框底部的“添加 ACE”、“删除 ACE”和“编辑 ACE”按钮。

图 20-17 展示了一个示例：我们向名为“Property Set Read – MyCorp Personal Information”的组（受托人/Trustee）授予针对所有用户（继承的对象类型/Inherited Object Type）的“MyCorp Personal Information”属性集（对象类型/Object Type）的读取属性权限（访问掩码/Access Mask）。此设置将应用于 People 组织单位（OU），并由该 OU 结构中的所有用户继承。

![Granting Read Property access to a group](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663580.png.webp)

图 20-17. 向组授予读取属性权限

在图 20-18中，我们向名为 People Full Control 的组（受托人( Trustee )）授予对名为 People 的组织单位( Organizational Unit ,OU)中所有用户（对象类型( Object Type )）的大部分权限（访问掩码( Access Mask )）。




![Granting access to users in an OU](./image/20.%20Active%20Directory%20Lightweight%20Directory%20Services/httpatomoreillycomsourceoreillyimages1663581.webp)


图 20-18. 向 OU 中的用户授予访问权限

### 20.8. 总结

AD LDS 是一款极为出色的产品，无疑将在企业环境中为微软及其他应用程序所广泛采用。其提供的灵活性使 Active Directory 管理员能够更频繁地说“我们可以做到”，以支持业务线应用程序及其他功能，而这些在以往是他们绝不允许接近基于域的 Active Directory 网络的。随着越来越多的应用程序开始利用 AD LDS，对 AD LDS 的认识和理解对于所有 Active Directory 管理员而言将变得越来越重要。

本章讨论并探索了 AD LDS 的基本概念以及一些更高级的概念。我们通过截图和表格展示了决策点，详细介绍了 AD LDS 服务器角色的安装过程，以及标准唯一实例和副本实例的安装步骤。此外，还介绍了随 AD LDS 一起提供的新工具和更新工具。最后，提供了许多 *ldifde.exe* 示例，展示创建和删除对象及分区的大多数方面，并进行了讨论，以帮助新的 AD LDS 管理员快速启动并运行新的 AD LDS 实例。

---

## 第 21 章 活动目录联合身份验证服务

随着服务从企业数据中心迁移到“云”中托管的外部平台，对扩展身份验证机制的需求已发生重大演变。微软对此的解决方案是活动目录联合身份验证服务( Active Directory Federation Services ,ADFS )。ADFS 是一项带有 Active Directory 品牌的独立服务，因此自然期望 Active Directory 管理员能够部署和管理 ADFS。

实际上，ADFS 本身就是一个独立的专业技能领域，因此我们将在本章中借此机会介绍该服务，并讨论部署和配置的基本知识。如果你曾经做过任何 Web 开发，你可能会发现 ADFS 及身份联合的许多概念对你来说远比那些纯粹基础设施背景的人更为熟悉。

毫无疑问，无论哪种情况，你都会发现身份联合的许多基本概念与 Active Directory 早期（甚至更早的 NT 域时期）就已存在的概念惊人地相似。如果你探索联合身份领域，你会发现这个领域非常拥挤，众多供应商都有解决此问题的方案。从根本上说，其中许多方案在功能上非常相似。我们将在本章中仅讨论 ADFS，但所讨论的许多概念广泛适用于整个市场。

### 21.1. 联合身份简介

从根本上说，身份联合的核心思想是，一方（*身份提供方* ( Identity Provider ,IdP)，或 IdP）能够向另一方（*信赖方* ( Relying Party ,RP)，或 RP）断言用户就是她所声称的那个人，而双方之间仅需建立一种轻量级的信任关系。在此描述中，“信任”一词非常重要，因为 RP 无法真正知晓 IdP 提供的答案是否完全属实。

为了让这个例子不那么抽象，请考虑这样一个场景：某组织（Coho Vineyard）将其员工薪资处理外包给第三方（Fabrikam Payroll）。为了让员工能够在线访问其薪资和税务信息，他们需要一种登录 Fabrikam Payroll 网站的方式，该网站托管在 Fabrikam 的数据中心。

图 21-1 概述了此场景。在 图 21-1 中，用户存在于 Coho Vineyard 的 Active Directory 中。Coho Vineyard 部署了 ADFS 环境，并且在此案例中是身份提供方。Coho Vineyard 和 Fabrikam Payroll 共同建立了一个*联合信任* ( Federation Trust )。在此案例中，Fabrikam Payroll 网站是信赖方。

![Federation overview](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663582.webp)

图 21-1. 联合身份验证概述

#### 工作原理

归根结底，在身份联合( Identity Federation )场景中，合作伙伴之间交互时会用到几种协议。无论走到哪里，你遇到的很可能都是安全断言标记语言( Security Assertion Markup Language ,SAML，读作“sam-il”)或 WS-Federation(通常缩写为 WS-Fed)。

对于 SAML 和 WS-Fed 而言，其工作原理在概念语义上是相同的，区别只在于数据的格式。在两种情况下，身份提供程序( Identity Provider ,IdP )都会生成一段可扩展标记语言( Extensible Markup Language ,XML)片段，其中包含一系列关于该用户的*声明*( Claim )。声明本质上就是属性/值对，常见的示例包括用户名、电子邮件地址、员工编号等数据点。这一组声明连同 XML 中的辅助数据，共同构成了用户用于访问依赖方( Relying Party ,RP )的*令牌*( Token )。RP 使用令牌中的声明对用户进行授权，并在应用程序中提供必要的功能。

为了保证令牌确由 IdP 签发且未被篡改，IdP 会使用其*令牌签名证书*( token signing certificate )对 XML 进行数字签名。RP 持有 IdP 令牌签名证书公钥的副本。当 RP 收到来自 IdP 的令牌时，会使用该公钥确认令牌是否有效。

讨论了 IdP 签发的令牌之后，下面来看一个端到端示例：用户希望访问 Fabrikam Payroll 网站，如图 21-2 所示。




![Federated application access workflow](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663583.webp)


图 21-2. 联合应用程序访问工作流

在此场景中，用户访问 Fabrikam Payroll 网站需要经过以下步骤：

1. 用户使用自己的 Web 浏览器访问 Fabrikam Payroll 网站，将浏览器指向该站点。在 Fabrikam Payroll 网站上，用户尝试登录，应用程序发现该用户必须通过联合身份验证方式登录。

2. 网站向用户的浏览器发出 HTTP 重定向，指示其访问 Fabrikam Federation 服务 URL 进行身份验证。

3. 用户的浏览器访问 Fabrikam Federation 服务。

   > **注意**：Fabrikam Federation 服务可以是 ADFS 环境，也可以是市面上众多其他联合产品中的任意一种。

4. Fabrikam Federation 服务查找 Coho Vineyard IdP 的 URL，并向用户的浏览器发出 HTTP 重定向。

5. 用户的浏览器访问 Coho Vineyard ADFS 服务器。

6. 用户向 Active Directory 联合身份验证服务( Active Directory Federation Services ,ADFS )服务器进行身份验证,并收到一个由 ADFS 服务器令牌签名证书签名的令牌。ADFS 服务器向用户浏览器发出 HTTP 重定向,将其引导回 Fabrikam 联合身份验证服务。

7. 用户浏览器将该令牌提交给 Fabrikam 联合身份验证服务。

8. Fabrikam 联合身份验证服务验证该令牌,然后为用户签发一个用于 Fabrikam Payroll 网站的新令牌,该令牌由 Fabrikam 的令牌签名证书签名。最后,Fabrikam 联合身份验证服务向用户浏览器发出 HTTP 重定向,将其指回 Fabrikam Payroll 网站。

9. 用户访问 Fabrikam Payroll 网站,并提交由 Fabrikam 联合身份验证服务签发的令牌。网站验证该令牌,对用户进行授权,并授予其访问应用程序的权限。

您可能会想:存在如此多的重定向和往返过程,这一切究竟怎能正常工作?效率又从何谈起?也许出乎意料的是,该流程运行得非常好,而且相当高效。此处描述的流程中,有几点可能不会一眼看明白。

第一点是步骤 2。为什么 Fabrikam Payroll 网站将用户重定向到 Fabrikam 联合身份验证服务,而不是直接重定向到 Coho Vineyard 的 ADFS 服务?答案在于为联合身份构建应用程序的语义。Figure 21-2 中涉及两个信任关系( Trust Relationship )。就网站或一般应用程序而言,应用程序只能信任一个联合身份验证服务。但联合身份验证服务却可以信任许多其他身份提供程序( Identity Provider ,IdP )。由于众多客户都在使用 Fabrikam Payroll 网站,该网站与 Fabrikam 的联合身份验证服务建立了信任,而 Fabrikam 的联合身份验证服务又转而信任每个客户(Coho Vineyard 等)。

> **注意**：在某些情况下，网站或应用程序本身也充当联合身份验证服务( Federation Service )。在这种情况下，信任关系将直接存在于客户的 Active Directory 联合身份验证服务( Active Directory Federation Services ,AD FS )服务器与信赖方( Relying Party ,RP )网站之间。这减少了几次跳转，也稍微简单一些，但在功能上是相同的。

了解这一点后，可能就更容易理解为什么我们需要与 Fabrikam 联合身份验证服务进行两次往返。在第 6 步中，用户会收到一个由 Coho Vineyard 的 AD FS 服务器签名的令牌( Token )。由于 Coho Vineyard 与 Fabrikam Payroll 之间的信任关系建立在联合身份验证服务之间，用户必须将该已签名令牌再出示给 Fabrikam 的联合身份验证服务(第 7 步)。然后，Fabrikam 的联合身份验证服务将验证该令牌；如果一切检查无误，它将颁发一个使用 Fabrikam 证书签名的*新*令牌(第 8 步)。由于 Fabrikam Payroll 应用程序只信任 Fabrikam 的联合身份验证服务，如果该令牌由 Coho Vineyard 的 AD FS 服务器签名，网站将无法验证它。

在继续之前，我们留给你一个可供对比的思考素材。如果你是 Active Directory 管理员，无疑熟悉 Kerberos(第 10 章)。正如我们刚才所讨论的，身份联合( Identity Federation )的工作原理与 Kerberos 非常相似。从功能上讲，你可以将身份提供程序( Identity Provider ,IdP )视为域控制器( Domain Controller ,DC )，将 RP 视为应用程序或服务器(例如，文件服务器)。当用户访问该文件服务器时，她必须向文件服务器出示服务票证( Service Ticket )，也就是联合令牌，才能访问该服务。服务票证使用服务的密钥加密，以确保其不被篡改(类似于对来自联合身份验证服务的令牌进行签名)。

#### SAML

安全断言标记语言( Security Assertion Markup Language ,SAML )2.0 是在不同环境间传递联合令牌的两大主要竞争标准之一。在美国,你会发现 SAML 在教育和政府部门中极为普遍;它也被许多第三方应用程序和云服务所采用。对于外部云服务而言,支持 SAML 是与潜在客户实现广泛兼容性的合乎逻辑的选择。

你可以在 [Wikipedia](http://bit.ly/10BZpD0) 上了解到不少关于 SAML 的知识,这或许出乎你的意料。我们还发现白皮书[《How to Study and Learn SAML》](http://bit.ly/10BZt5M)也非常有帮助。最后,SAML 的规范也[可以在线获取](http://bit.ly/YY7zra)。

在阅读 SAML 相关文档时,你可能会注意到这些文档会大篇幅讨论*断言*( assertion )这一术语。在 SAML 中,断言在功能上等同于本章所使用的“令牌”( token )一词。



#### WS-Federation

WS-Federation 是微软在其应用程序和软件开发工具包( Software Development Kit ,SDK )中选择采用的协议。事实上,第一版 ADFS 只会使用 WS-Federation。这一问题极大地影响了 ADFS 的采用,因为如果没有能够在 SAML 和 WS-Fed 之间进行转换的服务,大部分市场都将无法触及。

如果你与使用 Windows 标识基础( Windows Identity Foundation ,WIF )或 .NET 4.5 Framework 中包含的类来构建 .NET 应用程序的开发人员合作,那么这些应用程序在与标识提供者( Identity Provider ,IdP )交互时通常会使用 WS-Fed。

### 21.2. 了解活动目录联合身份验证服务( Active Directory Federation Services ,ADFS)组件

既然我们已经花了一些时间在概念层面探讨身份联合( Identity Federation )的语义，本章余下内容将深入介绍 ADFS 的部署和配置。在本节中，我们首先讨论构成 ADFS 拓扑的服务器角色。之后，我们将介绍一些适用于不同规模环境的常见部署拓扑。

#### 配置数据库

开始部署活动目录联合身份验证服务( Active Directory Federation Services ,ADFS)之前，首先需要决定将 ADFS 配置存储在何处。ADFS 可以将配置存储在两个位置：复制到每个联合服务器( Federation Server )的 Windows 内部数据库( Windows Internal Database ,WID)实例，或共享的 SQL Server 环境。

两种选项各有优缺点。WID 数据库部署极其简单(WID 随 Windows 一起提供)，且没有额外的许可成本。WID 还消除了分布式 ADFS 环境中的单点故障。使用 WID 时，每个联合服务器都包含配置数据库( Configuration Database )的副本。其中一个联合服务器(通常是部署的第一个联合服务器)被指定为“主”服务器。所有配置更改都在主服务器上进行，并且每五分钟将这些更改复制到所有“辅助”联合服务器。

WID 数据库也有一些限制。首先，在极大规模的 ADFS 部署中，它在性能和容量方面存在限制。此外，将配置数据库存储在 WID 上会移除对安全断言标记语言( Security Assertion Markup Language ,SAML)项目解析和令牌重放检测的支持。

SAML 项目是 SAML 特有的协议功能，而非 WS 联合身份验证( WS-Federation ,WS-Fed )的功能。SAML 项目允许 SAML 令牌(断言)提供指向可独立检索的数据的指针，而不是将该数据嵌入 SAML 断言中。由于检索该项目的请求会在稍后到达，并且该请求可能会

#### 联合服务器( Federation Server )

联合服务器是 Active Directory 联合身份验证服务( Active Directory Federation Services ,ADFS)环境的核心与灵魂。根据具体场景的不同,联合服务器既可充当标识提供者( Identity Provider ,IdP),也可充当信赖方( Relying Party ,RP)。ADFS 所支持的各种协议(例如 SAML 和 WS-Fed)同样由联合服务器发出。

对联合服务器实施妥善的安全防护(包括物理层面和逻辑层面)十分重要。联合服务器与域控制器( Domain Controller ,DC)类似,都控制着对应用程序和服务的访问。任何能够访问联合服务器的人,都可以用联合服务器的令牌签名证书( token signing certificate )签署一个伪造的令牌,从而冒充组织中的任意用户。对信赖方而言,该令牌看上去真实有效,会被当作合法签发的令牌一样处理。



#### 联合服务器代理( Federation Server Proxy )

联合服务器代理是一项可选功能,用于在联合服务器与 Internet 之间提供一层隔离。从功能上说,即使不部署代理,使用 ADFS 也没有做不了的事,但在某些场景中,借助代理会容易处理得多。

联合服务器代理开箱即用即可支持的主要场景,是能够为内部用户和外部用户采用不同的身份验证机制。在内部,当用户在企业网络上连接到联合服务器以获取令牌时,可以依靠 Windows 集成身份验证( Windows Integrated Authentication )(Kerberos 和 NTLM),让用户无需任何额外提示即可通过 ADFS 的身份验证。而在外部,用户可能正在使用家用电脑,或在咖啡店之类的地方连接。此时,你很可能希望显示一个友好的 HTML 表单来进行身份验证。

联合服务器代理还能让外部客户端与联合服务器上相对敏感的数据(用于签署令牌的私钥)相隔离。这提供了许多组织所看重的安全级别。

有些组织选择使用反向代理( reverse proxy )而非联合服务器代理来发布其 ADFS 服务器,还有些组织选择将联合服务器直接发布到 Internet 上。Microsoft 在其全部文档中均建议使用联合服务器代理,我们将在本章后面介绍如何部署它们。

#### ADFS 拓扑结构

部署 ADFS 有多种不同的拓扑结构，从小型简单到大型、复杂且高度冗余，不一而足。我们将介绍几种常见选项，以便你熟悉它们，然后继续逐步演示一个相对简单的部署，并在后续讨论中一直使用该部署。

在审阅本节介绍的设计方案时，请考虑你的环境对可扩展性的需求，更重要的是对高可用性的需求。当你开始与第三方托管的服务建立联合身份验证时，你的环境（此处指 ADFS）对于维持对这些应用程序和服务的访问仍然至关重要。如果你的 ADFS 环境宕机，你的用户将无法访问云解决方案。

这是许多组织容易陷入的陷阱，他们一度庆幸自己无需为外包服务提供高服务水平。虽然你不再需要负责维护外包服务，但你转而需要负责确保 ADFS 环境的高可用性，而该环境控制着对托管服务的访问。

##### 单台联合服务器

最简单的拓扑结构适用于测试和开发，涉及部署单台联合服务器。在此场景中，你只需在服务器上安装 ADFS 服务器角色，然后使用配置向导（如本章后文所述）通过 Windows 内部数据库( Windows Internal Database )部署联合服务器。除测试和开发之外，此拓扑结构的实用性可能相当有限。

##### 单台联合服务器和联合服务器代理

在此场景中，需要两台服务器，如图 21-3所示。一台服务器充当联合服务器和配置数据库的宿主，另一台服务器充当联合服务器代理，并将 ADFS 发布到 Internet。




![No high-availability deployment scenario](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663584.webp)


图 21-3. 无高可用性部署场景

此拓扑结构完全适用于需要与一个或多个合作伙伴和应用程序建立联合身份验证、但不需要服务器级别冗余的组织。ADFS 的体系结构使得日后扩展此拓扑结构以支持多台联合服务器和联合服务器代理变得相对容易。

> **注意**：你也可以选择将配置数据库部署在独立的 SQL 服务器上,但除非确有 SAML 工件解析( SAML Artifact Resolution )或令牌重放检测( Token Replay Detection )方面的需求,否则通常没有必要这样做。

##### 负载均衡的 ADFS 服务器

只要想为 ADFS 实现任何形式的冗余,就必须引入负载均衡。这往往需要你与网络团队的同事紧密协作,才能完成部署。就负载均衡配置而言,ADFS 的配置相当简单:只需为 TCP 端口 80 和 443 配置第 4 层负载均衡即可。除非在基本需求之外还有特殊要求,否则无需服务器关联性( Server Affinity )或 SSL 卸载。不过,你需要在负载均衡器上配置适当的服务器运行状况监视。

> **注意**：尽管可以使用 Windows 自带的 Windows 网络负载均衡( Network Load Balancing ,NLB )服务来替代硬件负载均衡器,但我们强烈建议你改用硬件负载均衡器。

图 21-4 展示了引入负载均衡器后的标准拓扑。在此示例中,我们有一对经过负载均衡的联合服务器代理( Federation Server Proxy ),这些代理连接到一组各自独立进行负载均衡的联合服务器( Federation Server )。这里我们选择继续使用 Windows 内部数据库( Windows Internal Database ,WID )存储配置。不过,如果你的部署规模较大,或者需要 SAML 工件解析、令牌重放检测这类功能,也可以按需将数据库部署在 SQL Server 集群上。随着需求增长,你可以轻松地在负载均衡器后面添加更多联合服务器和联合服务器代理。




![Load-balanced topology with WID](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663585.webp)


图 21-4. 使用 WID 的负载均衡拓扑

> **注意**：尽管图中显示的是独立的负载均衡器( Load Balancer ),但根据你的网络拓扑结构,你可能只需在一个负载均衡器上配置两个虚拟 IP( Virtual IP ,VIP)即可。请与你的网络团队协作,确定最佳架构。

##### 地理冗余的 ADFS 服务器

最后一种、也是最复杂的解决方案,是将 ADFS 服务器部署在多个数据中心( Datacenter )中,以确保最高级别的可用性。在这种情况下,你需要部署多种复杂技术,以确保一个 DNS 名称(即你的 ADFS 服务名称)能够解析到全球多个数据中心中的服务器,并且用户会被引导至距离其最近的数据中心。

若要实现 图 21-5 所示的配置,除了要在每个数据中心内部署负载均衡外,你还需要一个地理负载均衡服务( Geographic Load Balancing Service )。市面上有多种服务和产品可提供此能力,它们通常通过充当全局负载均衡器后方服务的 DNS 服务器来实现。我们熟悉的一种解决方案是 F5 全局流量管理器( Global Traffic Manager ,GTM)。GTM 只是竞争激烈的市场中的一种解决方案,因此你同样应计划与网络团队紧密协作,以确定最佳方案。




![Geographically load-balanced server farms](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663586.webp)


图 21-5. 地理负载均衡的服务器场

除了全局负载均衡解决方案外,你还需要利用 SQL Server 的镜像功能,将配置数据库( Configuration Database )复制到每个承载 ADFS 环境的数据中心中。

### 21.3. 部署 ADFS

在了解了活动目录联合身份验证服务( Active Directory Federation Services ,ADFS )的服务器角色和一些常见拓扑之后，接下来我们将逐步完成 ADFS 环境的部署和初始配置。我们将配置的环境如图 21-3所示。具体来说，我们将安装一台独立的联合服务器( Federation Server )以及一台独立的联合服务器代理( Federation Server Proxy )。配置存储将使用 Windows 内部数据库。

在深入之前，我们需要做出一个配置决策——环境的完全限定域名( Fully Qualified Domain Name ,FQDN )应该是什么？这个名称需要能够在内部和外部均可解析。这是用户进行身份验证时将被重定向到的 URL，也是信赖方( Relying Party )进行联合身份验证时所使用的 URL。从技术上讲，只要该 URL 能够在内部解析到联合服务器、在外部解析到联合服务器代理，选择什么 URL 并无影响，但请记住，这个 URL 日后将无法更改。

我们见过的几个常见示例包括：

- *sts.cohovines.com*

  > **注意**：STS 代表安全令牌服务( Security Token Service )。STS 是身份提供程序( Identity Provider ,IdP )的另一种称呼，联合身份验证领域中的某些产品会使用该术语。

- *fs.cohovines.com*

- *auth.cohovines.com*

- *login.cohovines.com*

在本章的剩余部分中，我们将使用 *sts.cohovines.com* 作为联合身份验证服务的名称。



#### 联合服务器

ADFS 部署的第一步是部署联合服务器。如果运行的是 Windows Server 2008 R2，则需要先[下载并安装 ADFS](http://bit.ly/10j6tEp)。

> **警告**：Windows Server 2008 R2 附带的 Active Directory 联合身份验证服务( Active Directory Federation Services ,ADFS) 版本为 ADFS 1.0。ADFS 1.0 与 ADFS 2.0 显著不同，因此请务必确保部署的是最新版本。

如果运行的是 Windows Server 2012，则 ADFS 2.1 作为可选服务器角色开箱即用。ADFS 2.0 与 ADFS 2.1 的唯一区别在于，后者支持将嵌入 Kerberos 票据中的动态访问控制( Dynamic Access Control ,DAC) 声明作为 ADFS 声明发送。无论运行哪个 ADFS 版本，本章中的说明均适用。

适用于 Windows Server 2008 R2 的可下载安装程序以及 Windows Server 2012 开箱即用的角色安装程序都足够智能，能够自动安装 ADFS 的先决条件。两个安装向导都会询问您是要安装联合服务器( Federation Server ) 还是联合服务器代理( Federation Server Proxy )。在此步骤中，应保留默认选项“联合服务器”。

##### 证书

Active Directory 联合身份验证服务( Active Directory Federation Services ,ADFS )需要多个安全套接字层( Secure Sockets Layer ,SSL )证书才能正常运行。至少，需要为联合身份验证服务( Federation Service )的完全限定域名( Fully Qualified Domain Name ,FQDN )提供一个证书（在我们的示例中是 [*sts.cohovines.com*](http://sts.cohovines.com/)）。请确保访问该服务的客户端信任此证书。

为了获取 SSL 证书，需要生成*证书签名请求* ( Certificate Signing Request ,CSR )，然后将该请求提交给*证书颁发机构* ( Certification Authority ,CA )。生成 CSR 的方法有很多。我们通常使用 DigiCert 提供的免费实用工具，DigiCert 是一家信誉良好的商业 CA，客户服务出色。可以从 https://www.digicert.com/util/ 下载该实用工具，并直接在联合身份验证服务器( Federation Server )上运行。该工具创建的 CSR 可以提交给任何内部或商业 CA。

要创建 CSR，请在联合身份验证服务器上启动该实用工具，然后单击“Create CSR”。根据你的环境填写表单。Common Name 字段应为联合身份验证服务的 FQDN，如图 21-6所示。收到 CSR 后，即可将其提交给 CA。

![DigiCert CSR creation wizard](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663587.webp)

图 21-6. DigiCert 创建 CSR 向导

当 CA 返回证书后，使用该实用工具底部的“Import”按钮导入结果。完成此操作后，应会看到证书带有绿色对勾，类似于图 21-7。如果要部署联合身份验证服务器场( Federation Server Farm )或联合身份验证服务器代理( Federation Server Proxy )，可以使用屏幕底部的“Export”按钮将证书导出为个人信息交换( Personal Information Exchange ,PFX )文件，然后在其他服务器上导入。

![DigiCert certificate](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663588.webp)

图 21-7. DigiCert 证书

联合身份验证服务器上还有两种其他类型的证书——令牌签名证书( Token Signing Certificate )和令牌加密证书( Token Encryption Certificate )。安装联合身份验证服务器时，ADFS 将为此目的生成自签名证书。我们将在服务配置一节中更详细地讨论这些内容。

##### 配置活动目录联合身份验证服务( Active Directory Federation Services ,ADFS )

安装完成后，可以启动 ADFS MMC 管理单元。在控制台中，单击链接以启动 AD FS 联合服务器配置向导以开始。在继续操作之前，请花点时间查看侧栏“ADFS 配置向导权限”，以确保向导在最后不会失败。

ADFS 配置向导权限

如果未以域管理员身份运行，配置向导将失败。这是因为向导必须将一个密钥共享容器发布到 Active Directory 中的 Program Data 容器。

此容器用于联合服务器安全地共享私钥，具体来说是令牌签名和令牌加密证书。如果无法以 Domain Admins 组成员的身份运行配置向导，则有几个选项。

第一种选择是让域管理员提前运行 *Set-ADFSCertSharingContainer* PowerShell cmdlet。这将在 Active Directory 中创建容器，并设置 ADFS 服务帐户管理该容器的权限。

第二种选择是在 Program Data 下预先创建一个名为 Microsoft 的容器，然后在 Microsoft 容器内创建第二个名为 ADFS 的容器。向运行 ADFS 配置向导的用户委派 Active Directory 中 ADFS 容器的完全控制权限。

图 21-8 显示了成功安装 ADFS 后，Active Directory 中发布的密钥共享容器。如果域中有多个 ADFS 场，则会发现多个 ADFS 容器。

![Key sharing container](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663589.webp)

图 21-8. 密钥共享容器

> **注意**：如果要使用 SQL Server 数据库而非 WID 作为配置数据库,则需要使用命令行工具来配置 ADFS。该工具名为 *fsconfig.exe*,位于 *%windir%\ADFS* 中。

首先会询问你是要部署新的联合身份验证服务,还是加入现有服务器场,如图 21-9所示。请选择"Create a new Federation Service"选项。




![Create or join a federation service](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663590.webp)


图 21-9. 创建或加入联合身份验证服务

接下来,你将可以选择创建新的联合服务器场或安装独立服务器,如图 21-10所示。即使你不打算添加其他联合身份验证服务器,我们也建议选择创建单服务器场。

> **警告**：独立服务器( Standalone Server )无法在后续阶段过渡为联合服务器场( Federation Server Farm )。


![Create a standalone server or server farm](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663591.webp)


图 21-10. 创建独立服务器或服务器场

ADFS 要在服务器场环境中运行,还需要一个服务账户( Service Account )。该服务账户应为普通的 Active Directory 用户账户,唯一区别在于需要在其上列出联合身份验证服务( Federation Service )的服务主体名称( Service Principal Name ,SPN )。这些服务主体名称通常类似于 `http/sts` 和 `http/sts.cohovines.com`。

配置向导将提示您选择一个 SSL 证书,用于分配给 ADFS 所使用的 Internet 信息服务( Internet Information Services ,IIS )网站。请确保所选证书与您的联合身份验证服务名称匹配,如图 21-11 所示。如果需要更改,之后可以方便地在 IIS 管理控制台中进行操作。




![Federation service name configuration](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663592.webp)


图 21-11. 联合身份验证服务名称配置

最后,配置向导将显示待执行任务的摘要,供您继续操作前查看。向导完成后,将显示已执行步骤及其结果的摘要,如图 21-12 所示。




![Wizard results summary](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663593.webp)


图 21-12. 向导结果摘要

##### 服务配置

向导完成后,您可以返回 ADFS 管理控制台。首先,右键单击 *Service* 文件夹,然后单击"编辑联合身份验证服务器属性"。在此您可以配置 ADFS 环境的关键详细信息,这些信息将发布给您与之建立联合关系的各方。

在"常规"选项卡上,可以为服务配置显示名称。在"组织"选项卡上,可以发布 ADFS 支持团队的联系信息,这些信息将列在 ADFS 服务器的联合身份验证元数据中。联合身份验证元数据( Federation Metadata )用于自动配置各方之间大部分信任关系。最后,在"事件"选项卡上,可以调整服务的日志记录和审核设置。

> **警告**：初始配置期间，必须设置“常规”选项卡上的“联合身份验证服务名称”和“联合身份验证服务标识符”值。部署 ADFS 后再更改这些值，可能会破坏你与其他各方之间的信任关系！

开始配置联合身份验证之前，应处理好的第二个配置项是令牌签名与令牌加密证书的问题。正如本章前面所述，ADFS 颁发的每个令牌都使用 ADFS 令牌签名证书进行签名。你信任的组织会在本地保留一份 ADFS 服务器公钥的副本，以便验证从你的 ADFS 环境接收的每个令牌。

这里会产生两个问题。第一，令牌签名证书和令牌加密证书是自签名证书。自签名证书在服务器本地生成，并非由受信任的证书颁发机构( Certificate Authority ,CA)颁发。某些联合身份验证平台不认为由不受信任（例如自签名）证书签名的令牌有效，即使该签名在密码学上是有效的。在这些情况下，你必须说服另一方信任你的令牌签名证书，或者使用来自商业 CA 的令牌签名证书。

第二个问题是证书过期。与你建立信任关系的各方必须在本地保留一份令牌签名证书公钥的副本，因此当该证书过期时，他们还需要一种机制来更新该公钥。目前有一种协议，允许依赖方( Relying Party )在令牌签名证书公钥可用时自动获取新公钥，但许多联合身份验证平台（及应用程序）并未实现该协议。因此，当证书过期时，信任关系将失效，对联合应用程序的访问将受到影响。

由于用于令牌签名的证书非常重要，而且日后很难更改，因此我们建议你获取一张商业颁发的令牌签名证书( Token Signing Certificate )，其到期时间尽可能晚。考虑到一两年后轮换证书的成本，预先购买具有三年(或更久)有效期的证书所增加的支出是非常值得的。令牌签名证书上的使用者名称完全不重要。我们通常会在服务证书( Service Certificate )所用的完全限定域名( Fully Qualified Domain Name ,FQDN)后附加“-signing”(例如 *sts-signing.cohovines.com*)。此外，你购买证书的证书颁发机构( Certification Authority ,CA)必须在证书的授权信息访问( Authority Information Access ,AIA)字段中包含证书颁发机构颁发者 OID (有关示例，请参见图 21-13)。这是一项鲜为人知的要求，购买证书前你需要向你的 CA 了解清楚。在本书出版时，我们知道 DigiCert (前文提到过) 和 Entrust 会在其证书中包含这些字段。

![Certificate details](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663594.webp)

图 21-13. 证书详细信息

我们已经提到过令牌加密证书( Token Encryption Certificate )，但到目前为止尚未讨论它。不讨论它的原因很简单——我们不建议你在任何信任关系( Trust Relationship )中启用令牌加密。ADFS 与最终用户或联合方( Federated Party )之间的任何事务(包括令牌)内容，在浏览器中已通过 SSL 受到保护。启用令牌加密后，令牌本身会使用令牌加密证书进行加密。如果你需要对 ADFS 与另一方之间的交互进行故障排除，那么令牌加密会让你几乎无法做到这一点。

#### 联合服务器代理（ Federation Server Proxy ）

部署联合服务器代理非常简单。除了部署向导之外，它没有需要配置的实际设置。涉及的唯一步骤是安装 Active Directory 联合身份验证服务（ Active Directory Federation Services ，ADFS）服务器角色，并在第一步中选择“联合身份验证服务代理（ Federation Service Proxy ）”（图 21-14），然后运行向导。

![Add Roles and Features Wizard](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663595.webp)

图 21-14. 添加角色和功能向导

对于联合服务器（ Federation Server ）角色，你需要导入一个证书，以供 ADFS 使用的 IIS 网站使用。你可以使用前面讨论的 DigiCert 工具完成此操作。实际上，你可以直接导入联合服务器上正在使用的证书副本：只需使用 DigiCert 工具将该证书导出为 PFX 文件，然后将其导入到联合服务器代理上。

导入证书后，启动 Internet Information Services 管理器 MMC 管理单元。在左侧的“连接”窗格中，浏览到 *Sites\Default Web Site*。接下来，在右侧的“操作”窗格中，单击“绑定”，如 图 21-15 所示。单击“添加”，将“类型”改为“https”，然后从“SSL 证书”下拉列表中选择你的证书，如 图 21-16 所示。

![IIS Manager](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663596.webp)

图 21-15. IIS 管理器

![Add Site Binding dialog](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663597.webp)

图 21-16. 添加站点绑定对话框

接下来，必须在联合服务器代理上配置 hosts 文件，以将联合身份验证服务（ Federation Service ）的名称解析为联合服务器或联合服务器前面的负载均衡器 VIP。为此，可以从提升权限的命令提示符中使用记事本打开 *%windir%\system32\drivers\etc* 中的 hosts 文件。

在该文件的底部，输入联合服务器或负载均衡器 VIP 的 IP 地址，按 Tab 键，然后在新行输入联合身份验证服务名称（例如 *sts.cohovines.com*），如 图 21-17 所示。

> **警告**：将 IP 地址与主机名分开时，必须使用制表符，这一点非常重要！




![Editing the hosts file](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663598.webp)


图 21-17. 编辑 hosts 文件

完成 *hosts* 文件的编辑后，启动 AD FS 联合服务器代理配置向导。该向导将根据 IIS 中导入的 SSL 证书自动填充联合服务名称。单击 图 21-18 中所示的"测试连接"按钮，以确保在继续操作之前不存在连接问题（如防火墙或名称解析问题）。




![The AD FS Federation Server Proxy Configuration Wizard](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663599.webp)


图 21-18. AD FS 联合服务器代理配置向导

单击"下一步"后，系统将提示您输入联合服务器场的管理员凭据。这些凭据仅用于建立代理与联合服务器之间的关系。您输入的凭据必须具有联合服务器的本地管理员访问权限。如果凭据有效，系统将显示将要执行的步骤摘要。

图 21-19 显示了联合代理服务器配置成功的结果。完成初始配置无需进一步操作。




![Federation proxy configuration results](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663600.webp)


图 21-19. 联合代理配置结果

### 21.4. 信赖方信任

作为典型的企业用户，您在活动目录联合身份验证服务（Active Directory Federation Services，ADFS）中执行的大部分配置工作很可能都属于信赖方的范畴。术语*信赖方*（Relying Party，RP）是 ADFS 对通常所认为的、依赖您的 ADFS 基础结构进行身份验证的应用程序的称呼。例如，它可以是内部开发的、支持声明（Claims）的应用程序，也可以是 [*salesforce.com*](http://salesforce.com/) 之类的云托管服务，或者外包的人力资源和薪资应用程序。

准备设置 RP 时，会遇到几种情形。最理想的情况是，RP 提供*联合身份验证元数据文档*（Federation Metadata Document）。这是 RP 在其服务器上发布的 XML 文档（有时也直接以文件形式提供给您），其中包含配置信任关系所需的全部详细信息。如果您想查看 ADFS 环境的联合身份验证元数据，请浏览[此链接](http://bit.ly/12p5Leh)，并将完全限定域名（Fully Qualified Domain Name，FQDN）替换为您环境中的相应值。

如果您的 RP 不提供联合身份验证元数据，则需要在“添加信赖方信任向导”中手动输入多个值。为完整起见，我们将通过一个不发布联合身份验证元数据的应用程序来演练此场景。

首先，打开 ADFS 管理控制台，浏览到 *AD FS\信任关系\信赖方信任*。右键单击，然后单击“添加信赖方信任”。启动向导并选择“手动输入有关信赖方的数据”，如图 21-20 所示。




![Adding relying party trust manually](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663601.webp)


图 21-20. 手动添加信赖方信任

接下来，为应用程序提供名称和描述。在此示例中，我们将该应用程序称为“Federation Demo”。我们建议您使用描述字段来跟踪该应用程序的相关信息，例如组织中与该应用程序关系的负责人以及建立信任的日期。

在“选择配置文件”屏幕上，使用默认的 ADFS 配置文件。在“配置证书”屏幕上，可以指定要使用的令牌加密证书（Token Encryption Certificate）。您需要导入信赖方的令牌加密证书的公钥，以便在此处手动配置。如本章前面所述，为便于故障排除，我们不建议使用令牌加密证书。

Figure 21-21 展示了"配置 URL"屏幕。在此处,你需要指定 ADFS 在颁发令牌后应将用户重定向到的 URL。同时,你还必须在此屏幕上指明应用程序支持的是 WS-Federation 还是 SAML 2.0。在本例中,我们的应用程序支持 WS-Federation,用户应被重定向到[此链接](http://bit.ly/Z70CAM)。在开始信任设置流程之前,你需要先向信赖方( Relying Party ,RP )的支持团队获取该 URL。




![Configuring the relying party trust URL](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663602.webp)


图 21-21. 配置信赖方信任 URL

接下来,你需要指定 RP 提供的标识符。ADFS 正是通过它来识别来自某个特定应用程序的请求。默认情况下,你在 Figure 21-21 中提供的 URL 会预先填入此处,如 Figure 21-22 所示。该值本质上可以是任意的,它会被包含在应用程序发出的身份验证请求中。与 URL 一样,你需要提前从 RP 的支持团队处收集此数据。




![Configuring the relying party trust identifier](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663603.webp)


图 21-22. 配置信赖方信任标识符

单击"下一步",并在"选择颁发授权规则"屏幕上选择"允许所有用户访问此信赖方"。我们将在下一节讨论声明规则时简要介绍颁发授权规则。随后出现的确认屏幕将以选项卡形式汇总你在向导中所做的全部选择。所有这些选择日后均可更改,但你应当花点时间复查一遍,确保没有明显的错误。

默认情况下,当你完成向导后,其最后一个屏幕会允许你为新建立的 RP 信任启动声明规则编辑器。我们将在下一节更详细地探讨声明规则;简而言之,它们让你定义应向 RP 发送哪些声明,以及这些声明在传递给 RP 之前是否需要先行转换。

### 21.5. 声明规则( Claims Rules )和声明管道( Claims Pipeline )

上一节中，我们使用示例应用程序创建了一个信赖方( Relying Party ,RP )信任。在该过程结束时，我们建立了一个信任，但未配置 ADFS 向应用程序发送任何声明( Claims )。如果不发送任何声明，RP 信任的价值就相当有限。

在本节中，我们将讨论两个极其重要的概念：声明管道和声明规则。声明管道是 ADFS 处理的每个声明都要经过的过程。声明规则用于在声明通过管道前往信赖方的过程中，对声明进行注入和筛选。

#### 管道

声明在到达依赖方的途中会经过若干环节。为便于讨论,我们假定你使用 Active Directory 作为唯一的声明提供程序。图 21-23 展示了声明管道的示意图。




![The claims pipeline](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663604.webp)


图 21-23. 声明管道

声明提供程序是声明进入管道的入口。声明提供程序向 ADFS 提供声明。你可以使用接受转换规则( Acceptance Transform Rules )来确定声明提供程序中的哪些声明可供依赖方信任( Relying Party Trust )使用。查看 Active Directory 声明提供程序信任的默认接受转换规则(图 21-24),你会发现这份列表相当空。




![Acceptance transform rules for Active Directory claims provider trust](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663605.webp)


图 21-24. Active Directory 声明提供程序信任的接受转换规则

或许有些反直觉的是,AD 声明提供程序并不会提供用户的所有属性——它只提供一些特殊属性,例如组成员身份、SID 和身份验证信息。特定属性必须从 Active Directory 属性存储中请求。稍后我们会进一步讨论这一点。

声明通过声明提供程序的接受转换规则之后,会被提交给相应的依赖方信任。第一步是确认该用户是否有权对给定依赖方进行身份验证。这一授权步骤在 RP 的颁发授权规则( Issuance Authorization Rules )中执行。默认情况下,所有用户都有权使用某个 RP,图 21-25 所示的“Permit Access to All Users”规则便是明证。你可以访问来自声明提供程序信任的任意声明,也可以从属性存储向管道中注入更多声明,以做出授权决策。ADFS 会根据管道中是否存在一个名为 Permit、值为 `true` 的声明来判定用户是否已获授权。




![Issuance authorization rules](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663606.webp)


图 21-25. 颁发授权规则

最后，可以使用信赖方( Relying Party ,RP)信任的颁发转换规则( Issuance Transform Rules )进一步修改或转换声明集( Claims Set )。在颁发转换规则处理结束时存在的声明，就是将发送给 RP 的声明。默认情况下，信赖方信任没有颁发转换规则。这实际上意味着 RP 将不会收到任何有关用户的声明。下面让我们看看如何更改这一点。

#### 通过管道创建和发送声明

生成要发送给信赖方( Relying Party ,RP )的声明主要有两种方式:一是通过声明提供方信任,二是通过信赖方信任的颁发转换规则。在声明提供方信任上定义声明集的好处在于,你可以拥有一组可供所有信赖方信任使用的集中式声明。这有助于减轻管理负担,并在进行故障排除或全局更改时,减少需要检查的位置数量。

要编辑活动目录( Active Directory )声明提供方信任的声明规则,请导航至 *AD FS\信任关系\声明提供方信任*。选择“活动目录”,然后在右侧任务窗格中单击“编辑声明规则”。若要以用户属性的形式向管道添加更多声明,请单击“添加规则”。

你可以从五种声明规则模板中进行选择。以下是对每种模板的简要说明:

- **以声明形式发送 LDAP 属性**

  此规则会将用户的一个或多个属性注入声明管道。除了注入活动目录属性之外,你还可以使用其他基于 LDAP 的属性存储,例如 AD LDS 服务器。

- **以声明形式发送组成员身份**

  如果需要根据用户是否属于某个组来向管道中插入声明,请使用此规则。例如,如果你想要有一个名为 IsSupervisor 的声明,并且组织中的所有主管都属于一个名为 Supervisors 的组,那么你就可以使用此规则。

- **转换传入声明**

  此规则使你能够对管道中已有的声明执行非常基本的转换操作。你可以更改声明的类型、执行基本的字符串替换,或转换电子邮件后缀。在考虑此规则模板时,请注意 图 21-24 中每条声明规则都有编号。规则是按顺序处理的。换句话说,在有序列表中,每条规则都可以访问在其之前(以及整个管道中更早)已添加到管道中的所有声明。

- **传递或筛选传入声明**

此规则本质上与之前的模板类似。你主要会在依赖方信任上使用此模板。你使用传递函数来指示活动目录联合身份验证服务( Active Directory Federation Services ,ADFS)在管道中向依赖方( Relying Party ,RP)发出声明。筛选功能适用于仅当声明与特定值匹配或以特定值开头时才发出声明。如果声明不匹配筛选规则，则不会被传递。

- **使用自定义规则发送声明**

  ADFS 有一种完整的自定义语言，称为 *声明规则语言*。此语言用于表达复杂的自定义表达式，这些表达式决定是否发出声明，使你能够对声明值执行复杂的转换，并能够访问自定义属性存储和结构化查询语言( Structured Query Language ,SQL)属性存储。解释声明规则语言是一个庞大的主题，本章没有足够的篇幅来讨论。Microsoft 已经[在线](http://bit.ly/WWQ1ee)记录了许多常见示例，如果你想采用自定义声明规则，我们鼓励你从那里开始。

现在我们已经讨论了可用的规则模板类型，让我们利用它们向管道中添加一些声明。在向导中，选择“以声明形式发送轻型目录访问协议( Lightweight Directory Access Protocol ,LDAP)属性”规则模板。创建一个规则来发送用户的名称和位置属性，如图 21-26 所示。

在图 21-26 中，我们将用户的名和姓、显示名称以及城市和国家属性作为声明发送。你现在可能已经注意到，下拉列表中的默认选项缺少大多数属性。如果看不到想要的属性，你可以直接键入 Active Directory 属性名称。如果需要添加额外的传出声明类型，则需要为这些属性创建声明说明。有关如何操作的更多信息，请参阅侧边栏“创建声明说明”。

![Send LDAP attributes as claims](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663607.webp)

图 21-26. 以声明形式发送 LDAP 属性

创建声明说明

声明描述( Claim Description )以统一资源标识符( Uniform Resource Identifier ,URI)的形式为声明提供唯一标识符,同时还包含一些标志,用于控制该声明是否会在 AD FS 环境的联合元数据( Federation Metadata )中发布。在联合元数据中发布声明完全可选;它为你提供了一种途径,可用于告知联合伙伴你接受哪些声明(就声明提供方信任( Claims Provider Trust )而言)以及你发布哪些声明(就信赖方信任( Relying Party Trust ,RP trust)而言)。

要创建新的声明描述,请在 ADFS 管理控制台中浏览到 *AD FS\Service\Claim Descriptions*,然后在右侧的任务窗格中单击"添加声明描述"。

根据声明的需要填写图 21-26 中所示的对话框。声明标识符应是格式正确的 URI,但它并不需要真正指向任何目标。该 URI 只是声明的唯一标识符。如果你希望为该声明发布元数据,可以选择选中底部的两个复选框。




![Add claim description dialog](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663608.webp)


图 21-27. 添加声明描述对话框

完成向导后,再次单击"添加规则"。这一次,我们将使用"将组成员身份作为声明发送"模板来为全职员工创建一个声明。图 21-28 展示了如何指定一个组,并在用户是该组成员时设置声明的值。




![Send a claim based on group membership](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663609.webp)


图 21-28. 基于组成员身份发送声明

至此,我们已经添加了一些可供所有 RP 信任使用的声明,接下来配置我们之前创建的那个 RP 信任,使其发出这些声明。在 ADFS 管理控制台中找到 Federation Demo RP 信任,然后单击"编辑声明规则"。在"颁发转换规则"选项卡上,单击"添加规则"。

首先请注意,之前编辑声明提供方信任声明规则时可用的那些模板在这里同样可用。如果你愿意,也可以改为在 RP 信任上执行我们刚刚执行的相同配置步骤。这样做的效果是仅将这些声明提供给此 RP。由于流程中已经有了所需的声明,我们只需将它们传递过去即可。

使用“通过或筛选传入声明( Pass Through or Filter an Incoming Claim )”模板，并将其配置为传递“名”( Given Name )声明，如图 21-29所示。对我们已配置的其他每种声明类型重复此操作：

- 姓氏( Surname )
- 显示名称( Display Name )
- 城市( City )
- 国家/地区( Country )
- 全职员工( FullTimeEmployee )

> **注意**：除非你已自定义过 Active Directory 联合身份验证服务( Active Directory Federation Services ,ADFS )的实现，否则需要完成侧栏创建声明描述( Creating Claim Descriptions )中的步骤，将 Display Name、City、Country 和 FullTimeEmployee 声明添加到 ADFS。




![Passing through the Given Name claim](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663610.webp)


图 21-29. 传递 Given Name 声明

完成后，你的颁发转换规则( Issuance Transform Rules )应与图 21-30类似。




![Issuance transform rules for RP trust](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663611.webp)


图 21-30. RP 信任的颁发转换规则

图 21-31展示了我们刚创建的声明规则的结果。截图展示了可从[此链接](http://bit.ly/YEJGrj)获取的示例应用程序的输出。该应用程序仅输出联合身份验证服务器( Federation Server )发送的所有声明。配置完成后，它是测试 ADFS 声明规则的实用工具。




![Claims sent to demo application](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663612.webp)


图 21-31. 发送到演示应用程序的声明

总结来说，在本节中我们配置了声明提供方信任( Claims Provider Trust )( Active Directory )，将多个声明添加到管道中，供系统中的所有依赖方( Relying Party ,RP )使用。为此，我们首先为每个自定义声明添加了声明描述，然后使用"将 LDAP 属性作为声明发送"( Send LDAP Attributes as Claims )模板将用户属性添加到管道，并使用"将组成员身份作为声明发送"( Send Group Membership as a Claim )模板在用户属于特定组时添加声明。最后，我们向 RP 信任的颁发转换规则添加了直通规则，以将声明发送给 RP。

### 21.6. 自定义 ADFS

只需少量配置，ADFS 即可开箱即用。不过，您很可能希望对使用体验进行一些自定义。根据自定义目标的不同，这项工作涉及的范围可能会有很大差异。组织最常进行的两种主要自定义是：对基于表单的登录（ Forms-Based Logon ）页面和主领域发现（ Home Realm Discovery ）页面进行外观/体验（或功能）调整，以及添加自定义属性存储（ Attribute Store ）。

#### 基于表单的登录页面

当用户通过 ADFS 代理从企业网络外部访问 ADFS 时，默认情况下将使用基于表单的登录页面进行登录。这些页面的默认外观平淡而灰暗。您可能需要与 Web 或市场部门协作，对这些页面进行自定义，使其符合企业品牌形象，并更具视觉吸引力。

Microsoft 提供了一份自定义这些页面的指南，可从 [microsoft.com](http://bit.ly/XHCfti) 获取。您希望进行的修改的复杂程度（例如更改颜色或添加徽标）将决定这项任务是否最好交给 ASP.NET 开发人员来完成。所有可自定义的文件都位于 ADFS 服务器上的 *c:\inetpub\adfs\ls* 目录中。在开始之前，请务必对原始页面进行备份，以备需要回滚时使用。

如果您只是想添加一个徽标，请编辑 *c:\inetpub\adfs\ls* 中的 *web.config* 文件，将 `logo` 设置更改为徽标文件的名称（或者直接将文件保存为 *logo.png*）。Microsoft 建议文件尺寸为宽 600 像素、高 100 像素，以获得最佳效果。

#### 属性存储

属性存储（ Attribute Store ）用于从外部系统提供声明（ Claim ）。在开箱即用的状态下，ADFS 支持从 Active Directory、AD LDS 等 LDAP 服务器以及 SQL 服务器中获取属性。如果您需要从其他系统（例如人力资源系统或 Oracle 数据库）提供声明，则必须开发自定义属性存储来实现。

开发自定义属性存储需要 .NET 开发技能，这超出了本书的讨论范围。入门文档可从 [microsoft.com](http://bit.ly/XHCfti) 获取。请务必对您的实现进行全面测试，尤其是在错误处理和性能方面。

### 21.7. ADFS 故障排除

对 Web 开发者来说，ADFS 的故障排除可能是自然而然的事情，因为所用的一些关键工具都是传统的 Web 调试工具。对于 IT 专业人员来说，学习曲线会高得多，因为从传统事件日志中可以获取的数据量相对有限。

在我们深入研究几个工具之前，您工具箱中的第一个技巧是 Internet Explorer(IE) 的 InPrivate 浏览模式。InPrivate 可阻止访问或保存 Cookie，并掩盖您的浏览历史记录，从而提高安全性。您可以通过按 Ctrl-Shift-P 在 IE 中开启 InPrivate 模式。或者，您可以右键单击任务栏中的 Internet Explorer 图标，然后单击“开始 InPrivate 浏览”。当您处于 InPrivate 模式时，您会在地址栏左侧看到一个 InPrivate 标识符，以及启动页面上的帮助菜单，如图 21-32 所示。

![Internet Explorer InPrivate Mode](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663613.webp)

图 21-32. Internet Explorer InPrivate 模式

#### 事件日志

AD FS 内置了多种事件日志以及一个称为关联标识符( *correlation identifier* )的实用数据点，可协助您排查问题。每当用户在 AD FS Web 应用程序中遇到问题，都会弹出一个类似于图 21-33的错误界面。作为管理员，您需要特别关注其中的引用编号字段。




![Error page with reference number](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663614.webp)


图 21-33. 带引用编号的错误页面

要查看 AD FS 日志并将其与图 21-33中显示的引用编号进行关联，请在联合身份验证服务器上启动事件查看器( Event Viewer )，然后浏览至 *Applications and Services Logs\AD FS\Admin*。接下来，依次点击“查看”→“添加/删除列”。添加“Correlation Id”列并重新排列显示的列，如图 21-34所示。




![Add/remove columns from Event Viewer](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663615.webp)


图 21-34. 在事件查看器中添加/删除列

请注意，图 21-33中显示的引用编号与两个事件的“Correlation Id”列中的值相匹配。具体来说，图 21-35中的事件告诉我们，没有配置与应用程序发送的标识符相匹配的信赖方信任( Relying Party Trust )。




![Error event with Correlation Id](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663616.webp)


图 21-35. 带关联标识符的错误事件

如果 Admin 事件日志中的数据不够充分，您需要为 AD FS 启用跟踪日志( Trace Log )。为此，请依次点击“查看”→“显示分析和调试日志”。浏览至 *Applications and Services Logs\AD FS Tracing\Debug*，然后右键单击 Debug 日志并点击“启用日志”。重现您的错误并刷新视图。图 21-36显示了一个有用的事件，确认了图 21-35中的诊断结论。完成后，请务必右键单击 Debug 日志并点击“禁用日志”。

> **注意**：您需要重复相同的步骤，以将 Correlation Id 列添加到此日志的显示中。




![Tracing events in the Debug log](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663617.webp)


图 21-36. 跟踪调试日志中的事件



#### Fiddler

排查 Active Directory 联合身份验证服务( Active Directory Federation Services ,ADFS )时最重要的工具是一款名为 Fiddler 的免费工具。Fiddler 是一个 HTTP 代理，可让您通过友好的图形用户界面( Graphical User Interface ,GUI )查看 HTTP 流量。如果您以前使用过 Wireshark 或 Netmon 进行网络跟踪，可以将 Fiddler 视为这些工具的应用层版本。获取一份 [Fiddler](http://bit.ly/16Innkb) 并将其安装到您的工作站上。接下来，转到[此链接](http://bit.ly/Xinq3k)，安装 Fiddler 的加载项，以便轻松处理 HTML、XML 等。

最后，从[此站点](http://bit.ly/17hGfrl)下载 Fiddler 联合身份验证检查器。此加载项将使 Fiddler 能够解码 WS-Federation 和 SAML 标记。解压 *.zip* 文件，然后浏览到 *bin\Debug* 文件夹。将 *Thinktecture.FederationInspector.dll* 复制到 *C:\Program Files (x86)\Fiddler2\Inspectors.*，或复制到您计算机上安装 Fiddler 的位置。

若要查看加密的 ADFS 流量，需要将 Fiddler 配置为拦截 HTTPS 流量。为此，请启动 Fiddler，然后转到 Tools→Fiddler Options。在“HTTPS”选项卡上，选中“Capture HTTPS CONNECTs”和“Decrypt HTTPs traffic”。接下来，系统会提示您生成一个证书，以便 Fiddler 拦截 SSL 流量，并配置 Windows 信任该证书，如图 21-37所示。您会收到另一个确认提示，要求导入该证书；最后，在出现用户账户控制( User Account Control ,UAC )提示后，还会收到最后一个确认提示。对所有这些提示都选择“是”。




![Configuring certificate trust in Fiddler](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663618.webp)


图 21-37. 在 Fiddler 中配置证书信任

> **注意**：如果要在 Active Directory 联合身份验证服务( Active Directory Federation Services ,ADFS )服务器上使用 Windows 集成身份验证( Windows Integrated Authentication )，则必须先禁用扩展保护( Extended Protection )，然后才能使用 Fiddler。有关如何操作，请参阅侧栏配置扩展保护。

完成这些步骤后，请浏览到联合应用程序( Federated Application )并登录。你将看到 Fiddler 中发生的每个步骤，如图 21-38 所示。

![Fiddler trace of access to a federated application](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663619.webp)

图 21-38. 访问联合应用程序的 Fiddler 跟踪

具体而言，在图 21-38 中，将发生以下步骤（如“#”列所示）：

1. 用户浏览到 https://fedapp.briandesmond.net/FederationDemo/。

2. 应用程序将用户重定向到该应用程序中配置的 ADFS 服务器。

   > **注意**：状态代码 301 和 302（Result 列）是 HTTP 重定向。

3. ADFS 服务器再执行一次重定向，指向该应用程序正确的身份验证 URL。

4. 系统会提示用户使用 Windows 集成身份验证向 ADFS 服务器进行身份验证。图 21-39 显示了 Fiddler 中正在使用的 Auth 检查器，可用于排查身份验证问题。

   > **注意**：状态代码 401 通知浏览器用户必须向应用程序进行身份验证。

5. 用户成功通过 ADFS 服务器的身份验证。图 21-40 显示了 Federation 检查器对发送到应用程序的 WS-Federation 令牌的解码结果。

   > **注意**：状态代码 200 表示 HTTP 请求已成功完成。

6. ADFS 服务器根据图 21-21 中在信赖方信任( Relying Party Trust )中配置的 URL，将用户重定向回应用程序。

7. 用户成功访问该应用程序。

![Fiddler Federation inspector](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663620.webp)

图 21-39. Fiddler Federation 检查器

配置扩展保护

扩展保护( Extended Protection )是 Windows 安全更新中引入的一项安全功能,如 http://support.microsoft.com/kb/968389 中所述。通常情况下,建议启用它;但是,它会直接影响您使用 Fiddler 进行故障排除。如果启用了扩展保护,ADFS 将不断提示您进行身份验证,并且您将始终无法继续访问应用程序。

如需出于故障排除目的禁用扩展保护,请在联合服务器( federation server )上执行以下步骤:

1. 启动 Internet 信息服务( Internet Information Services ,IIS )管理器。您可以通过转到“开始”→“运行”并输入 **`inetmgr`** 来执行此操作。
2. 在左侧的“连接”窗格中,浏览到 *Sites\Default Web Site\adfs\ls* 节点。
3. 在中间窗格中双击“身份验证”图标。
4. 选择“Windows 身份验证”,然后在右侧的“任务”窗格中单击“高级设置”。
5. 将“扩展保护”更改为“关闭”,如图 21-41 所示。




![Fiddler Auth inspector](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663621.webp)


图 21-40. Fiddler Auth 检查器




![Extended Protection settings](./image/21.%20Active%20Directory%20Federation%20Services/httpatomoreillycomsourceoreillyimages1663622.webp)


图 21-41. 扩展保护设置

### 21.8. 本章小结

在本章中，我们探讨了活动目录联合身份验证服务( Active Directory Federation Services ,ADFS)。ADFS 是微软针对一个竞争激烈的市场领域给出的解决方案，该领域充满了各类供应商和服务，它们提供身份联合选项，用于将您的本地目录与业务合作伙伴以及云中的应用程序连接起来。

由于该产品名称中包含“Active Directory”，人们自然会认为 AD 域管理员能够将 ADFS 作为其职责的延伸来承担。实际上，管理和故障排除 ADFS 所需的技能集与 Web 开发人员的角色更为接近，而非域管理员。本章旨在弥合这一差距，帮助您——域管理员——在组织中顺利使用 ADFS 实现身份联合。
