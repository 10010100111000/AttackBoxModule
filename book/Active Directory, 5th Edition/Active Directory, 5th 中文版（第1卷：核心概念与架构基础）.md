---
summary: Active Directory（第5版·第1卷），系统阐述Active Directory基础概念、对象存储机制、系统管理工具、命名上下文与应用程序分区、Schema架构体系、站点拓扑与复制原理，以及目录高级搜索技术。
---

# Active Directory, 5th Edition（第1卷：核心概念与架构基础）

## 第 1 章 简要介绍

### 1.1. Microsoft NOS 的演进

*网络操作系统*( Network Operating System )，简称“NOS”，是指这样一种网络环境：用户、组和计算机账户等各类资源集中存储于中央存储库中，由管理员统一管控，终端用户可进行访问。通常，NOS 环境由一台或多台提供 NOS 服务（如身份验证、授权和账户管理）的服务器，以及多个访问这些服务的终端用户组成。

Microsoft 首个集成化的 NOS 环境随 Windows NT 3.0 于 1990 年发布，它融合了 LAN Manager 协议和 OS/2 操作系统的诸多特性。此后八年，NT NOS 逐步演进，直至 1997 年 Active Directory 首次以 Beta 版本形式发布。

在 Windows NT 中，引入了“域（domain）”的概念，提供了一种基于 ==管理 和 安全边界== 对资源进行分组的方式。NT 域为扁平结构，对象数量上限约为 40,000 个（包括用户、组和计算机）。对于大型组织而言，这一限制迫使域结构设计不得不划分出人为的边界。此外，域往往还受到地理范围的制约，因为域控制器( Domain Controller ，DC)——即为终端用户提供 NOS 服务的服务器——之间的数据复制在高延迟或低带宽链路上表现不佳。NT NOS 的另一个重大问题是管理委派，在域级别通常呈现为全有或全无的模式。

Microsoft 充分认识到这些局限性，也深知需要将 NOS 模型重新架构为更具可扩展性和灵活性的方案。于是，它将目光投向了基于 LDAP 的目录服务，将其视为可能的解决之道。

#### 目录服务简史

一般来说，*目录服务( Directory Service )*是可供多个应用程序或用户使用的网络、应用程序或 NOS 信息存储库。根据这一定义，Windows NT NOS 也是一种目录服务。事实上，目录有多种不同类型，包括互联网白页、电子邮件系统，甚至域名系统( Domain Name System ,DNS)。尽管这些系统各自都具有目录服务的特征，但 X.500 和轻型目录访问协议( Lightweight Directory Access Protocol ,LDAP)定义了实现和访问真正目录服务的标准。

1988 年，国际电信联盟( International Telecommunication Union ,ITU)和国际标准化组织( International Organization for Standardization ,ISO)共同制定了一系列有关目录服务的标准，这些标准后来被称为 X.500。尽管 X.500 被证明是构建目录的良好模型，并围绕高级操作和安全性提供了大量功能，但实现能够利用它的客户端却很困难。原因之一是 X.500 基于开放系统互连( Open System Interconnection ,OSI)协议栈，而不是已成为互联网标准的 TCP/IP。X.500 目录访问协议( Directory Access Protocol ,DAP)非常复杂，并实现了许多大多数客户端根本不需要的功能。这阻碍了其大规模采用。正因如此，由密歇根大学牵头的一个小组开始开发一种“轻量级”X.500 访问协议，使 X.500 更易于使用。

轻型目录访问协议( Lightweight Directory Access Protocol ,LDAP)的第一个版本于 1993 年作为请求意见稿( Request for Comments ,RFC) [1487](http://www.ietf.org/rfc/rfc1487.txt) 发布，但由于 X.500 提供的许多功能尚不具备，它一直未能真正普及。直到 1995 年 LDAPv2 作为 RFC 1777 发布，LDAP 才开始流行起来。在 LDAPv2 之前，LDAP 主要用作 X.500 服务器之间的网关。简化客户端与 LDAP 网关交互，由网关转换请求并将其提交到 X.500 服务器。密歇根大学团队认为，如果 LDAP 能够提供大多数客户端所需的大部分功能，就可以省去中间环节（网关），并开发支持 LDAP 的目录服务器。该目录服务器可以使用 X.500 的许多概念（包括数据模型），但会舍弃因实现众多功能而产生的全部额外开销。因此，密歇根大学团队于 1995 年末发布了首个 LDAP 目录服务器，它成为后来许多目录服务器的基础。

1997 年，RFC 2251 描述了 LDAP 规范的最后一次重大更新 LDAPv3。它提供了若干新功能，使 LDAP 足够健壮和可扩展，适合大多数供应商实现。此后，Netscape、Sun、Novell、IBM、OpenLDAP 基金会和 Microsoft 等公司纷纷开发了基于 LDAP 的目录服务器。最近，RFC 3377 发布，其中列出了所有主要 LDAP RFC。有关 Microsoft 的 LDAPv3 实现与符合性白皮书，请参阅[此网站](http://bit.ly/11k4B38)。

### 1.2. 总结

现在，我们已经简要介绍了 Active Directory 的起源，接下来就请继续阅读，深入了解 Active Directory。在本书的其余部分，我们将帮助您快速掌握成功支持 Active Directory 以及设计有效 Active Directory 实施方案所需的知识。

---

## 第 2 章 Active Directory 基础

### 2.1. 对象如何存储与标识

Active Directory 中存储的数据以分层方式呈现给用户，类似于数据在文件系统中的存储方式。每个条目称为一个*对象*。在结构层面，对象分为两种类型：*容器*和*非容器*。非容器对象也称为*叶节点*。一个或多个容器从根容器以分层方式分支出来。每个容器可以包含叶节点或其他容器。然而，顾名思义，叶节点不能包含任何其他对象。

> [!NOTE]
>
> 尽管 Active Directory 中的数据以分层方式呈现，但实际上它存储在扁平的数据库行和列中。目录信息树( Directory Information Tree ,DIT)文件是一个可扩展存储引擎( Extensible Storage Engine ,ESE)数据库文件。这回答了“Active Directory 使用 JET 还是 ESE 数据库技术？”这个问题。ESE *就是*一种 JET 技术。

考虑图 2-1中容器和叶节点的父子关系。此树的根有两个子节点：Finance 和 Sales。这两个都是其他对象的容器。Sales 自己有两个子节点：Pre-Sales 和 Post-Sales。图中仅显示 Pre-Sales 容器包含其他子对象。Pre-Sales 容器包含用户、组和计算机对象作为示例。

> [!NOTE]
>
> 用户、组和计算机对象实际上是容器，因为它们可以包含打印机等其他对象。然而，在诸如此类的域图中，它们通常不会绘制为容器。

这些子节点中的每一个都以 Pre-Sales 容器为父节点。图 2-1表示 Active Directory 中称为*域*的内容。




![A hierarchy of objects](./image/2.%20Active%20Directory%20Fundamentals/httpatomoreillycomsourceoreillyimages1663327.png.webp)


图 2-1. 对象层次结构

在 Active Directory 中最常创建的容器类型是组织单位( Organizational Unit ,OU)，但还有其他类型，例如称为“container”的类型。它们各有其用途，我们稍后会展示，但我们将最频繁使用的是组织单位。

#### 对象的唯一标识

在 Active Directory 中可能需要存储数百万个对象，因此每个对象都必须能够被唯一地定位和标识。为此，**系统会在创建对象时为其分配一个全局唯一标识符( Globally Unique Identifier ,GUID)**。这个 128 位的数字是 Microsoft 对 Digital Equipment Corporation 提出的通用唯一标识符( Universally Unique Identifier ,UUID)概念的具体实现。人们常误以为 UUID/GUID 能够保证唯一，事实并非如此；只能说在公元 3400 年之前，该数字出现重复的概率在统计学上微乎其微。在 GUID 创建 API 函数的文档中，Microsoft 称："To a very high degree of certainty, this function returns a unique value."（此函数能以极高的确定性返回一个唯一值。）无论对象在目录信息树( Directory Information Tree ,DIT)中是被重命名还是被移动，其 GUID 都会一直伴随该对象，直到对象被删除。在多域林中跨域移动对象时，对象的 GUID 同样会保留。

使用 Microsoft 活动目录迁移工具( Active Directory Migration Tool ,ADMT)等工具跨林移动安全主体时，不会保留对象的 GUID。

尽管对象的 GUID 具有很强的持久性，但它不易记忆，也不基于目录层次结构。因此，另一种引用对象的方式——可分辨名称( Distinguished Name ,DN)——更为常用。

##### 可分辨名称

Active Directory 中的层次路径称为可分辨名称，可用于唯一地引用对象。可分辨名称在 LDAP 标准中定义，用于引用目录中的任意对象。

Active Directory 对象的可分辨名称通常使用 LDAP 标准中定义的语法和规则来表示。下面来看看指向 图 2-1 中根目录的路径是什么样子：


```
dc=mycorp,dc=com
```


在前面的可分辨名称中，域根 *mycorp.com* 的表示方式是用逗号分隔各个部分，并在每个部分前加上字母 "dc"。如果该域名为 *mydomain.mycorp.com*，则根的可分辨名称如下所示：


```
dc=mydomain,dc=mycorp,dc=com
```

`dc` 代表 *域组件* ，用于指定域或应用程序分区对象。应用程序分区将在第 4 章中介绍。

*相对可分辨名称* (RDN) 是用于在目录中唯一引用其父容器内对象的名称。例如，这是 *mycorp.com* 域中 Users 容器内默认 Administrator 账户的 DN：


```
cn=Administrator,cn=Users,dc=mycorp,dc=com
```


这是该用户的 RDN：


```
cn=Administrator
```


RDN 在其所在容器内必须始终唯一。目录中允许存在两个 `cn=Administrator` 对象；但是，它们必须位于不同的父容器中。在 Users 容器中不能有两个 RDN 为 `cn=Administrator` 的对象。

DN 由名称和前缀组成，二者通过等号 (=) 分隔。另一个您将会非常熟悉的前缀是 `ou`，它代表组织单位。以下是一个示例：


```
cn=Keith Cooper,ou=Northlight IT Ltd,dc=mycorp,dc=com
```


所有 RDN 都使用前缀来指示所引用对象的类。任何没有特定字母代码的对象类都使用默认的 `cn`，它代表通用名称。表 2-1 提供了目录服务器实现中最常见属性类型的完整列表。该列表来自 RFC 2253《轻量级目录访问协议 (v3)：可分辨名称的 UTF-8 字符串表示》，全文可在 http://www.ietf.org/rfc/rfc2253.txt 找到。

表 2-1. RFC 2253 中的属性类型

| 键       | 属性                     |
| -------- | ------------------------ |
| `CN`     | 通用名称                 |
| `L`      | 地点名称                 |
| `ST`     | 州或省名称               |
| `O`      | 组织名称                 |
| `OU`     | 组织单位名称             |
| `C`      | 国家名称                 |
| `STREET` | 街道地址                 |
| `DC`     | 域组件                   |
| `UID`    | 用户 ID                  |

Active Directory 支持使用 `CN`、`L`、`O`、`OU`、`C` 和 `DC`。在大多数情况下使用 `CN` 或 `OU`。

##### 示例

再次回顾图 2-1。如果所有容器都是组织单位( Organizational Unit ,OU),那么售前和售后的可分辨名称( Distinguished Name ,DN)如下所示:


```
ou=Pre-Sales,ou=Sales,dc=mycorp,dc=com
ou=Post-Sales,ou=Sales,dc=mycorp,dc=com
```


如果想在售前 OU 中指定名为 Richard Lang 的用户、名为 My Group 的组以及名为 PC1 的计算机,则应使用以下内容:


```
cn=Richard Lang,ou=Pre-Sales,ou=Sales,dc=mycorp,dc=com
cn=My Group,ou=Pre-Sales,ou=Sales,dc=mycorp,dc=com
cn=PC1,ou=Pre-Sales,ou=Sales,dc=mycorp,dc=com
```

### 2.2. 构建基块

在介绍了对象的结构与引用方式之后，接下来我们来看 Active Directory 背后的核心概念。

#### 域和域树

一个域控制器（Domain Controller，DC）只能对**一个域具有权威性**。单个 DC 无法同时承载多个域。

Active Directory 域可以按照 DNS 命名空间的层次关系组成**域树（domain tree）**。一个域只有在以另一个域作为其父域、加入该域的命名空间后，才成为同一域树中的子域；作为最顶层父域的域，则是该域树的**根域**。

例如：

```
mycorp.com
├── europe.mycorp.com
├── asia.mycorp.com
└── americas.mycorp.com
```

这里，`europe.mycorp.com`、`asia.mycorp.com` 和 `americas.mycorp.com` 都作为 `mycorp.com` 的子域加入，因此共同构成一棵以 `mycorp.com` 为根域的域树。即一棵完整的域树。即使整个环境中只有一个域，它仍然构成一棵域树，只不过这棵域树中只有一个域。




![The mycorp.com domain tree](./image/2.%20Active%20Directory%20Fundamentals/httpatomoreillycomsourceoreillyimages1663328.webp)


图2-2. mycorp.com域树

域树简化了资源的管理和访问,因为域树中的所有域都通过*传递信任( Transitive Trust )*隐式地相互信任。在传递信任中,如果域 A 信任域 B,且域 B 信任域 C,则意味着域 A 也信任域 C。图 2-3展示了这一点。更简单地说,*asia.mycorp.com* 的管理员可以允许域树中的任何用户访问其希望开放的 Asia 域中的任何资源。访问资源的用户不必位于同一个域中。




![The mycorp.com domain tree](./image/2.%20Active%20Directory%20Fundamentals/httpatomoreillycomsourceoreillyimages1663329.webp)


图 2-3. mycorp.com 域树



信任关系( Trust Relationship )不会危及安全；它们只是为允许访问资源创造条件。实际访问权限仍必须由管理员授予。因此，应避免在资源上向 Everyone 或 Authenticated Users 授予访问权限。一旦建立信任，受信任域中的每个人也将能够访问这些资源。



#### 林

现在您已经了解什么是域树( Domain Tree )，我们可以继续介绍 Active Directory 结构的下一部分：林( Forest )。域树是域的集合，而林是一个或多个域树的集合。这些域树共享同一个架构( Schema )和配置容器( Configuration Container )，并且这些域树整体上通过传递信任( Transitive Trust )连接在一起。只要创建一个域，就形成了一个林。如果向初始域树添加任何域，或添加新的域树，仍然只有一个林。

林以创建的第一个域命名，该域也称为*林根域( Forest Root Domain )*。林根域很重要，因为它具有特殊属性。

> [!WARNING]
>
> 在 Active Directory 中，永远不能删除林根域。如果尝试删除，林将被彻底破坏且无法恢复。在 Windows Server 2003 及更新版本的 Active Directory 中，可以重命名林根域，但不能更改其作为林根域的状态，也不能让其他域成为根域。

继续介绍 Mycorp 时，我们发现它有一家名为 Othercorp 的子公司。分配给 Othercorp 并供其使用的 DNS 域名是 *othercorp.com*。对于 Othercorp，只需将 *othercorp.com* 树的根创建为现有林的成员；这样，*othercorp.com* 和 *mycorp.com* 便可以共存并共享资源，如图 2-4所示。包含 *mycorp.com* 和 *othercorp.com* 域树的林称为 *mycorp.com* 林，其中 *mycorp.com* 是林根域。




![Transitive trusts illustrated](./image/2.%20Active%20Directory%20Fundamentals/httpatomoreillycomsourceoreillyimages1663330.webp)


图 2-4. 传递信任示意图

> [!WARNING]
>
> 虽然可以在一个林( Forest )中配置多个域树( Domain Tree )，但在实施此类配置之前，应认真考虑其所有影响。在进行故障排除时，如果正在处理域( Domain ) *othercorp.com* 中的问题，而该林的配置信息却保存在分区 `cn=configuration,dc=mycorp,dc=com` 中，就可能会造成混乱。当引入不熟悉该实现方式的外部资源时，尤其如此。

虽然创建多域树林( Multitree Forest )有正当理由，但我们建议您尽可能简化 Active Directory 设计，并限制为一个域树和尽可能少的域。

新林设计的最佳实践几乎始终是单域林( Single-Domain Forest )。我们在此概述了设计林时的各种多域选项，但通常不建议采用这些选项（包括空根( Empty Root )）。

各个公司通常会实施自己的林。如果 Othercorp 选择将其 Active Directory 作为单独的林进行部署，则需要在 Mycorp 和 Othercorp 之间使用林信任( Forest Trust )，以便在两个公司之间提供无缝的资源访问。

林信任允许管理员在两个林根域( Forest Root Domain )之间创建单个可传递的单向或双向信任。此信任允许一个林中的所有域信任另一个林中的所有域，反之亦然。

如果您的业务部门( Business Unit )相互独立，并且实际上希望彼此隔离，则不得将它们合并到单个林中。如果只是为每个业务部门提供各自的域，这些业务部门会觉得自己是自主的且彼此隔离。但是，在 Active Directory 中，这种级别的自主性和隔离只能通过单独的林来实现。如果您需要遵守法规或法律隔离要求，也是如此。最后，一些组织选择将 Microsoft Exchange 部署在单独的资源林( Resource Forest )中，以便处理单独的管理结构和管理需求。

#### 组织单位( Organizational Unit ,OU)

在介绍完 Active Directory 的大规模视图（域( Domain )、树( Tree )和林( Forest )）后，现在我们来讨论小规模视图。查看 Active Directory 域内部时，你会看到对象的层次结构。该层次结构由可充当容器( Container )的对象和不能充当容器的对象组成。为容纳对象而创建的主要容器类型称为组织单位(OU)。另一种容器类型实际上称为*容器*，也可用于存储对象和容器的层次结构。

尽管二者都能包含庞大的容器和对象层次结构，但组织单位可以对其应用组策略( Group Policy )。（有关组策略的详细信息，请参阅第 11 章。）因此，OU 通常几乎专用于在域内构建对象层次结构。

让我们用一个示例来说明。假设你是 图 2-2 中 *asia.mycorp.com* 域的管理员。该域中有 500 个用户和 500 个计算机账户。多数日常账户和计算机管理都非常简单，但制造部门目前正在进行重组和大规模招聘；人员不断调入或从外部聘用。你希望授予该组对用户对象的有限自治权，允许其中一位高级管理员管理该组在树中的相应部分。不需要完全隔离安全性，并且制造部门所在的树也不够大，不值得再创建一个域并管理其关联的域控制器( Domain Controller ,DC)。你可以改为在层次结构中创建一个名为 Manufacturing 的组织单位。然后，授予高级工程师对该组织单位的权限，以便在 Manufacturing OU 中创建和删除账户、更改密码以及创建其他组织单位。显然，授予该高级工程师的权限应经过适当调整，使其只能控制该组织单位，而不能控制整个 *asia.mycorp.com* 域树。你可以手动完成此操作，也可以使用控制委派向导( Delegation of Control Wizard )来委派控制，第 16 章将对此进行更深入的讨论。

安装 Active Directory 域时，系统会自动创建许多默认容器( Container )和组织单位( Organizational Unit ,OU)，包括 Users 和 Computers 容器以及 Domain Controllers OU。如果尝试新建容器，你会发现，在 Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC) MMC 管理单元中并没有相应的选项。对于组织( Organization )、位置( Locality )和国家/地区( Country )容器对象也是如此。这是有意设计的；在几乎所有情况下，你都应创建组织单位，而不是容器。可以通过脚本和其他 LDAP 工具创建其他类型的容器，但通常并无必要。因此，本书通篇在建议于域内创建层次结构时，始终推荐使用组织单位。毕竟，组织单位只是容器的超集。容器能做的任何事情，组织单位都能做。

#### 全局编录

全局编录( Global Catalog ,GC) 是 Active Directory 中非常重要的一部分，因为它用于执行全林搜索。顾名思义，全局编录是林中所有对象的编录，其中包含每个对象的一部分属性。可以通过端口 3268 上的 LDAP 或端口 3269 上的 LDAP/SSL 访问 GC。全局编录是只读的，不能直接更新。

在多域林中，通常首先需要对 GC 执行查询，以定位目标对象。然后，如果要访问对象上可用的所有属性，可以针对该对象所在域的域控制器( Domain Controller ,DC) 执行更定向的查询。

全局编录中可用的属性是*部分属性集( partial attribute set ,PAS)*的成员。可以使用 Active Directory 架构管理单元等工具，或直接在架构中修改该属性的 `attributeSchema` 对象，来向 PAS 添加属性或从中移除属性。

> [!NOTE]
>
> 在 Windows 2000 中，向 PAS 添加属性会导致林中的所有全局编录重新同步 GC 的全部内容。这可能对复制和网络流量产生重大影响。幸运的是，此问题已在 Windows Server 2003 中解决；向 PAS 添加属性后，不再发生 GC 重新同步。

#### FSMO 角色

尽管 Active Directory 是一种多主机目录,但在某些情况下,某些功能只能由单台域控制器( Domain Controller ,DC )执行。此时,Active Directory 会指定一台服务器充当这些功能的主机。共有五种此类功能只能在一台服务器上执行。负责某一特定功能或角色的服务器,称为灵活单主机操作( Flexible Single Master Operator ,FSMO ,读作"fizmo")角色持有者。

这五种角色中,有三种存在于每个域中,另外两种适用于整个林。如果林中有四个域,则共有 14 个 FSMO 角色:

- 2 个林范围的 FSMO
- 4 组、每组 3 个域范围的 FSMO

不同角色持有者的数量可能千差万别,具体取决于是不是由同一台 DC 承担多个角色——这种情况十分常见。

各种 FSMO 角色如下:

- **架构主机(林范围)**

  架构主机角色的持有者,是唯一有权更新架构的域控制器。其他任何服务器都无法处理架构更改。如果尝试在不持有架构主机 FSMO 的 DC 上更新架构,该 DC 将返回一个指向架构主机角色持有者的参照。默认情况下,架构主机角色的持有者是林中第一台提升为域控制器的服务器。

- **域命名主机(林范围)**

  域命名主机角色的持有者负责控制林范围命名空间的更改。这台服务器负责添加和删除域,而且在林中重命名或移动域,以及授权创建应用程序分区、添加或删除其副本时,都必须由它执行。与架构主机一样,该角色持有者默认为林中提升的第一台 DC。注意有一种常见的误解,认为架构主机和域命名主机不能由林根域之外的服务器承担。事实上,林中的任何域控制器(来自任何域)都可以承担架构主机和域命名主机这两个 FSMO 角色。一般情况下,除非有特殊理由将它们放在别处,否则我们建议将这些 FSMO 角色保留在林根域的域控制器上。

- **PDC 仿真器(域范围)**

出于向后兼容的需要,必须有一台 Active Directory DC 充当 Windows NT 主域控制器( Primary Domain Controller ,PDC)。该服务器同时充当 Windows NT 主浏览器,并作为早期版本客户端( down-level client )的 PDC。尽管 PDC 承担着非常重要的旧版功能,但不要误以为在移除所有旧客户端后它就不再重要。

PDC 仿真器还承担其他重要功能:其一,它负责维护所有账户的最新密码。为此,其他 DC 只要发现账户密码发生更改,就会立即直接转发给 PDC。此功能的意义在于支持 PDC 链接( PDC Chaining )功能。当账户尝试进行身份验证,而本地 DC 认为所提供的密码不正确时,就会发生 PDC 链接。此时本地 DC 会将身份验证请求“链接”到 PDC,以确认 PDC 是否认可该密码。

> [!NOTE]
>
> 通过将 `AvoidPdcOnWan` 注册表值设置为 `1`,可以禁用 PDC 链接,以及跨 Active Directory 站点边界向 PDC 转发密码的相应行为。该值位于注册表项 `HKLM\SYSTEM\CurrentControlSet\Services\Netlogon\Parameters` 中。如果怀疑 PDC 链接未正常工作,请确认未配置此注册表值。有关该注册表设置的详细信息,请参阅[此链接](http://support.microsoft.com/kb/225511)。

PDC 还是大多数组策略管理工具的目标服务器。这样可降低不同管理员同时在不同 DC 上以不同方式修改同一策略的可能性。PDC 的另一项功能是:每个域中的 PDC 均为该域的主要时间源,而林根域的 PDC 则是整个林的主要时间源。第 16 章中介绍的 *AdminSDHolder* 进程同样在 PDC 仿真器上运行。最后,PDC 仿真器负责授权域控制器克隆操作。有关域控制器克隆的详细信息,请参阅第 9 章。

- **RID 主机(域范围)**

每个域都有一个*相对标识符*( Relative Identifier ,RID)主机。域中的每个安全主体都有一个*安全标识符*( Security Identifier ,SID),该标识符由若干组成部分构成,其中就包含 RID。系统借助 SID 在安全权限中唯一标识该对象。在某种程度上,SID 类似于每个对象都拥有的全局唯一标识符( Globally Unique Identifier ,GUID),但 SID 只分配给启用了安全功能的对象,并且仅用于安全验证目的。有关 SID 的详细信息,请参阅侧栏安全标识符( SID )中包含哪些内容?。您可以使用安全账户管理器( Security Accounts Manager ,SAM)账户名或用户主体名称( User Principal Name ,UPN)登录或进行身份验证以引用某个对象,但系统在执行授权功能时,始终通过 SID 来引用您。

在域中,SID 必须在整个域范围内保持唯一。由于每个 DC 都能创建启用了安全功能的对象,因此必须存在某种机制,确保绝不会创建出两个完全相同的 SID。为避免发生冲突,RID 主机维护着一个大型的唯一 RID 值池。当有 DC 加入网络时,会从 RID 池中为其分配 500 个值的子集供其专用。每当 DC 需要创建 SID 时,它便从自己的 RID 池中取用下一个可用值,从而创建出具有唯一值的 SID。

通过这种方式,RID 主机可确保域中所有 SID 都使用唯一的 RID 值。当某台 DC 的 RID 池降至可用池大小的 50% 时,该 DC 会联系 RID 主机再获取一组 RID 值。之所以不将阈值设为 0,是为了确保在 RID 主机短暂无法为其他 DC 提供服务时,不会立即影响对象的创建。RID 主机本身负责生成并维护整个域范围内的唯一值池。

> [!NOTE]
>
> RID 池的大小可以通过在 RID 主机 FSMO 角色持有者上设置注册表项 `HKLM\SYSTEM\CurrentControlSet\``Services\NTDS\RID` 中的 `RID Block Size` 值来配置。可能需要使用此注册表设置的常见场景是:您的环境为分布式环境,域控制器与 RID 主机之间可能出现长时间的连接问题。
> 如果您决定使用此注册表设置,建议在*任何*可能成为 RID 主机的域控制器上设置该值,这样在发生 RID 主机 FSMO 转移后,就不会出现 RID 池大小不一致的情况。

##### 安全标识符( SID )中包含哪些内容?

许多 Windows 管理员都知道 SID 是什么:一种用于标识受托人或安全主体的唯一可变长度标识符。但是,很少有人了解 SID 究竟由哪些组件构成。花一点时间了解 SID 的组成方式,或许有助于管理员理解 Windows 安全性的底层原理。

Windows SID 通常由 2 个固定字段和最多 15 个附加字段组成,所有字段之间均用短横线分隔,如下所示:

`S-v-id-s1-s2-s3-s4-s5-s6-s7-s8-s9-s10-s11-s12-s13-s14-s15`

第一个固定字段( `v` )描述 SID 结构的版本。Microsoft 从未更改过该字段,因此它始终为 1。

第二个固定字段( `id` )称为*标识符颁发机构*( Identifier Authority )。在 Windows 域和 Windows 计算机中,它唯一标识所涉及的颁发机构,例如 NULL(0)、World(1)、Local(2)、NT Authority(5)等。

接下来的 15 个字段( `s1` – `s15` )并非每个 SID 都必须具备;事实上,大多数 SID 只填充了其中少数几个字段。这些附加字段称为*子颁发机构*( Sub-Authority ),用于帮助唯一标识所引用的对象。大多数 SID 上的最后一个子颁发机构通常称为 RID。域或计算机正是通过递增该值来创建唯一的 SID。

掌握这些信息后,您就可以查看诸如 `S-1-5-10` 这样的 SID,并判断出它是由 NT Authority 颁发的版本 1 SID。该 SID 很特殊,称为*已知安全标识符*( Well-Known SID ),表示 *NT Authority\Self*。另一个已知 SID 是 `S-1-1-0`,它是版本 1 的 World SID,表示 *Everyone*。

此外还有若干其他已知 SID,取值各不相同。这些 SID 很容易识别,因为它们不符合普通计算机 SID 和域 SID 的格式。普通 SID 通常如下所示:**`S-1-5-21`**-*`xxx-yyy-zzz`*-**`r`**,其中 *`xxx`*、*`yyy`* 和 *`zzz`* 的值是在创建计算机或域时随机生成的。RID 值 `r` 既可以是 RID 生成例程颁发的连续编号,也可以是为每个域中都存在的某些安全主体分配的已知 RID。已知 RID 的一个示例是 500,它对应内置管理员账户。

- **基础结构主机( Infrastructure Master ,域范围)**

基础结构主机( Infrastructure Master )用于维护对其他域中对象的引用，这些引用称为*幻影*( Phantom )。如果域 B 的三个用户是域 A 中某个组的成员，则域 A 上的基础结构主机将用于维护对幻影域 B 用户成员的引用。这些幻影无法通过常规方式进行管理，甚至不可见；它们是为保持一致性而采用的一种实现构造。基础结构主机的灵活单主机操作( Flexible Single Master Operations ,FSMO)角色所有者用于在幻影所引用的对象在其所属域中发生更改或移动时，持续维护这些幻影。当一个域中的对象引用另一个域中的对象时，它会通过全局唯一标识符( Globally Unique Identifier ,GUID)、安全标识符( Security Identifier ,SID)（用于引用安全主体( Security Principal )）以及被引用对象的可分辨名称( Distinguished Name ,DN)来表示该引用。基础结构主机 FSMO 角色持有者是负责在跨域对象引用中更新对象 SID 和可分辨名称的域控制器( Domain Controller ,DC)。

基础结构主机还负责修复其域中的对象对其他域中对象的陈旧引用（“陈旧”是指对已被移动或重命名的对象的引用，因此远程对象名称的本地副本已过期）。它通过将自己的（可能已陈旧的）命名数据与全局编录( Global Catalog ,GC)的命名数据进行比较来完成此操作；GC 会自动接收所有域中对象的定期复制更新，因此没有陈旧数据。基础结构主机会将它发现的任何更新写入其对象，然后将更新后的信息复制到域中的其他 DC。但是，如果某个 GC 同时承担基础结构主机角色，那么按照定义，承载该 GC 的服务器将始终是最新的，因此不会有任何陈旧引用。如果它从未察觉到有任何内容需要更改，就永远不会通过基础结构更新来更新任何非 GC 服务器。

一旦启用 Active Directory 回收站，基础结构主机的功能就会由林中的每台 DC 独立执行。也就是说，刚才描述的任务不再委派给单台 DC。

此外，升级到 Windows Server 2003 或更高版本时，基础结构主机还负责对域执行更新——必须在基础结构主机上运行命令 *adprep /domainprep*。我们将在第 19 章中讨论 *adprep*。

基础结构主机的放置位置，以及能否将其放在全局编录上而不引发问题，常常令人十分困惑。表 2-2提供了一个矩阵，列出未启用 Active Directory 回收站的林所允许的排列组合。

表 2-2. 基础结构主机( Infrastructure Master )放置规则

|                                       | **单域林**             | **多域林** |      |
| ------------------------------------- | -------------------- | ---------- | ---- |
| 所有域控制器( Domain Controller ,DC)都是 GC        | 所有域控制器都*不是* GC |                            |      |
| 基础结构主机是否相关        | 否                                   | 否                         | 是  |
| 允许基础结构主机位于 GC 上 | 是                                   | 是                         | 否   |

> [!NOTE]
>
> 从技术层面讲，除域之外，林中的每个应用程序分区都存在一个基础结构主机。在 Windows Server 2008 之前，基础结构主机不执行任何应用程序分区功能。不过，Windows Server 2008 及更高版本的安装程序现在会强制执行一致性检查，以确保为每个应用程序分区指定的基础结构主机有效。有关此内容的更多信息，请参阅 [microsoft.com](http://bit.ly/16oUveC)。应用程序分区在第 4 章中详细讲解。

FSMO 角色可以在域控制器之间转移。可以使用“Active Directory 域和信任关系”管理单元转移域命名 FSMO，使用“Active Directory 架构”管理单元转移架构 FSMO，并使用“Active Directory 用户和计算机”管理单元或 Windows PowerShell 转移 RID、基础结构和 PDC 仿真器 FSMO。或者，也可以使用 *ntdsutil* 实用工具从命令行执行转移。有关使用 *NTDSUTIL* 转移 FSMO 角色的更多信息，请参阅第 18 章。

尽管在两台服务器均可用时，AD 管理单元和 *NTDSUTIL* 可以轻松地将角色从一台服务器转移到另一台服务器，但在某些情况下，FSMO 角色所有者会在角色尚未事先转移的情况下变得不可用。在这种情况下，必须使用 *NTDSUTIL* 强制将角色非正常转移到某台服务器，这称为“夺取”角色。夺取 FSMO 角色后，不应使原始角色所有者重新联机。而应执行元数据清理，然后重建域控制器。有关使用 *NTDSUTIL* 夺取 FSMO 角色的更多信息，请参阅第 18 章。

> [!NOTE]
>
> 如果您使用的是 Windows Server 2008 或更高版本的 Active Directory 用户和计算机，则可以从 Domain Controllers 组织单位( Organizational Unit ,OU)中删除域控制器( Domain Controller ,DC)，并执行元数据清理。
>
> 对于早期版本，若在 *dcpromo* 失败后需要从目录中删除元数据，或者域控制器因任何原因无法重新联机，则需使用 *NTDSUTIL*。有关使用 *NTDSUTIL* 执行元数据清理的详细步骤，请参阅 [microsoft.com](http://bit.ly/14OksrL)。
>
> 如果域的某个 FSMO 角色持有者丢失，应始终确保掌控局面，并执行以下操作之一：将新 DC 提升为相关角色持有者、强制将该角色转移到现有 DC，或迅速恢复作为相关角色持有者的 DC。



> [!WARNING]
>
> 如果承载某个角色的服务器变为不可用,系统不会自动将另一台服务器提升以承担该角色。管理员必须手动将该角色转移到新的所有者。

许多 Active Directory 管理员花费大量时间担忧其 FSMO 角色所有者的健康状况,以及"如果某个角色持有者离线,该如何仓促将其恢复服务"的假设场景。值得思考的是,每个 FSMO 角色所有者的即时可用性对您的环境究竟有多重要:

- **架构主机( Schema Master )**

  只有在更改架构时才需要架构主机。此类操作通常会提前充分规划,因此即使架构主机离线,您也完全可以稍后再将其恢复在线。

- **域命名主机( Domain Naming Master )**

  只有在添加域和应用程序分区时才需要域命名主机。这同样是一项会提前充分规划的更改,因此,如果域命名主机离线,您很可能也可以稍后再将其恢复在线。

- **基础结构主机( Infrastructure Master )**

  如果基础结构主机离线,您将无法运行 *adprep /domainprep*,并且跨域的幻影更新( phantom update )将会停止。当然,第一项任务会提前充分规划。第二项乍看之下似乎很重要,但基础结构主机是在几天的时间内更新幻影的,因此如果您稍等片刻再将其恢复在线,多半不会出现问题。如果您启用了 Active Directory 回收站( Active Directory Recycle Bin ),基础结构主机停机将只会影响您运行 *adprep* 的能力。

- **RID 主机( RID Master )**

  如果 RID 主机离线,当域控制器( Domain Controller ,DC)请求 RID 池时,您将无法向其发放。回顾前面对 RID 主机的描述:域控制器会在剩余 RID 数量降至 250 个时,按每批 500 个的方式请求 RID 池。因此,除非您预计域控制器上的 RID 池会非常迅速地耗尽(这里的"迅速"指比您恢复 RID 主机还快),否则 RID 主机离线一段时间很可能不会造成任何问题。RID 主机可用性可能更为重要的一个场景是:您需要预配大量新的安全主体(用户、组或计算机),而预配系统会将此项任务定向到单个域控制器或一组域控制器。有关 RID 池耗尽的详细信息,请参阅[此文](http://bit.ly/Y1uCBy)。

- **PDC 仿真器( PDC Emulator )**

PDC 仿真器( PDC Emulator )可用性的重要程度因环境而异。PDC 仿真器是使用旧版 API 的应用程序经常联系的域控制器( Domain Controller ,DC);它还负责解析信任路径、串联密码更改、作为时间同步层次结构的根,等等。是否需要尽快将 PDC 仿真器恢复联机,很大程度上取决于你的具体环境;但总体而言,在五种灵活单主机操作( Flexible Single Master Operations ,FSMO)角色中,PDC 仿真器可能是你环境中最重要的一种角色持有者。



##### fSMORoleOwner 属性

FSMO 角色持有者的信息存储在 Active Directory 中的不同位置,具体取决于角色。持有该角色的服务器的 DN 实际上存储在各个对象的 `fSMORoleOwner` 属性中。对于 *mycorp.com* 域,各 FSMO 角色对应的属性所在容器如下:

- PDC 仿真器 - `dc=mycorp,dc=com`
- 基础结构主机( Infrastructure Master )- `cn=Infrastructure,dc=mycorp,dc=com`
- RID 主机( RID Master )- `cn=RID Manager$,cn=System,dc=mycorp,dc=com`
- 架构主机( Schema Master )- `cn=Schema,cn=Configuration,dc=mycorp,dc=com`
- 域命名主机( Domain Naming Master )- `cn=Partitions,cn=Configuration,dc=mycorp,dc=com`

fSMORoleOwner 属性中存储的值是一串 DN（专有名称）。这个 DN 并不是直接指向那台域控制器的计算机账户，而是精确指向该域控制器上的 NTDS Settings 对象（代表该服务器上运行的 Active Directory 目录服务实例）。因此,该属性的内容示例可能如下:


```
CN=NTDS Settings, CN=MYSERVER1, CN=Servers, CN=My Site,
CN=Sites, CN=Configuration, DC=mycorp, DC=com
```

> [!NOTE]
>
> 多年来，灵活单主机操作( Flexible Single Master Operations ,FSMO)角色的放置一直存在一些争议。有些管理员主张将每个角色放在不同的域控制器( Domain Controller ,DC)上，而另一些管理员则主张将所有角色放在一起。为简单起见，可以在每个域中将所有角色保留在单个 DC 上，除非 FSMO 角色持有者 DC 上的负载要求将这些角色分散到不同服务器上。如果决定拆分这些角色，请参阅 [Microsoft 支持页面](http://support.microsoft.com/kb/223346)，获取有关如何最佳放置这些角色的最新指南。
>
> 如果担心能够从备份中还原 FSMO 角色持有者，则应相应地拆分角色。尤其不建议从备份中还原 RID 主机，因此，如果希望能够从备份中还原其他 FSMO 角色持有者，应将 RID 主机保留在单独的域控制器上。



#### Active Directory 中的时间同步

Active Directory 高度依赖所有域控制器( Domain Controller ,DC)和域成员拥有同步的时钟。Kerberos(它是 Active Directory 客户端的底层身份验证协议)使用系统时钟来验证 Kerberos 数据包的真实性。默认情况下，Active Directory 允许时钟存在正负五分钟的容差。如果时间偏差超过此设置，客户端可能无法进行身份验证；对于域控制器，复制将不会发生。较新版本的 Windows 可以处理时间偏移而不影响 Kerberos，如[这篇文章](http://bit.ly/Yb6bnr)所述。

幸运的是，Active Directory 和 Windows 共同实现了一个基于*网络时间*协议( Network Time Protocol ,NTP)的时间同步系统，该系统确保林中的每台计算机都具有同步时钟。*w32time* 服务在林中每台 Windows 2000 或更高版本的计算机上实现时间同步。以下列表概述了时间同步层次结构，一种可能有效的层次结构如图 2-5所示：

1. 林根域的 PDC 仿真器( PDC Emulator )将其时钟与可靠的外部时间源(例如硬件时钟、政府时间源或其他可靠的 NTP 服务器)同步。
2. 每个子域的 PDC 仿真器将其时钟与其域或父域中的可靠时间源同步。
3. 每个域控制器将其时钟与其域或父域的 PDC 仿真器同步。
4. 每个域成员将其时钟与其进行身份验证的域控制器同步。

> [!NOTE]
>
> 网络时间协议( Network Time Protocol ,NTP)定义于 RFC 1305，可通过[此链接](http://www.faqs.org/rfcs/rfc1305.html)获取。

除根域的 PDC 模拟器之外，不应在加入域的任何计算机上配置 *w32time* 服务。虽然这样做也是允许的，但根据我们的经验，许多选择使用不同时间同步层次结构(例如使用本地路由器或专用 NTP 服务器)的组织最终都会遇到 Kerberos 问题。有关如何在 PDC 模拟器上配置 *w32time* 服务的信息，请参阅即将介绍的侧栏在 PDC 模拟器上配置 W32Time。

##### 在 PDC 模拟器上配置 W32Time

要配置 PDC 模拟器，需要确定一个或多个权威外部时间源。在本示例中，我们将使用 NTP Pool Project([http://www.pool.ntp.org](http://www.pool.ntp.org/))的 NTP 服务器：


```
w32tm /config /update 
  /manualpeerlist:"0.pool.ntp.org,1.pool.ntp.org,2.pool.ntp.org" 
  /syncfromflags:manual /reliable:YES
w32tm /resync /rediscover /nowait
```


有些组织选择使用路由器或交换机之类的本地网络设备，而不是外部 NTP 服务器。只要该路由器或交换机与权威时间源同步，这就是完全有效的配置。

有关在此场景中配置 *w32time* 服务的详细信息，请参阅[此链接](http://support.microsoft.com/kb/816042)。您也可以订阅 [msdn.com](http://blogs.msdn.com/w32time/) 上的博客。

若要排查时间同步问题，*w32time* 服务会将事件记录到系统事件日志中。

```
w32tm /config /update 
  /manualpeerlist:"0.pool.ntp.org,1.pool.ntp.org,2.pool.ntp.org" 
  /syncfromflags:manual /reliable:YES
w32tm /resync /rediscover /nowait
```

命令通常也有助于故障排除。


![Sample time synchronization hierarchy](./image/2.%20Active%20Directory%20Fundamentals/httpatomoreillycomsourceoreillyimages1663331.webp)


图 2-5. 时间同步层次结构示例



> [!WARNING]
>
> 务必记住，在根域中转移 PDC 模拟器 FSMO 角色时，无论是移入还是移出，都要在相关域控制器上重新配置 *w32time* 服务。
>
> 我们建议您考虑主动将所有可能持有 PDC 模拟器 FSMO 角色的候选服务器提前配置为与可靠的外部时间源同步。这样，在转移该角色时就无需再记住执行手动配置步骤。

#### 域和林功能级别

在 Windows Server 2003 版本的 Active Directory 中，Microsoft 通过引入*功能级别*扩展了域模式概念。域模式仅适用于域，而功能级别同时适用于林和域。与域模式类似，功能级别决定了哪些类型的操作系统可在域或林中充当域控制器( Domain Controller ,DC)角色。每个功能级别还关联了一组功能，当域或林达到该特定功能级别时，这些功能即可使用。我们将在附录 A中介绍各功能级别可用的许多功能。

与域模式类似，功能级别可通过 Active Directory 域和信任关系管理单元设置。对于 Windows Server 2003 和 Windows Server 2008 域功能级别( Domain Functional Level ,DFL)，一旦功能级别“提升”到更高状态，便无法回滚。Windows Server 2008 R2 通过引入可独立于功能级别启用的可选功能，实现了回滚功能级别的能力。

表 2-3和表 2-4列出了各种域功能级别和林功能级别( Forest Functional Level ,FFL)支持的操作系统。



表 2-3. 域功能级别

| 功能级别                    | 功能级别编号            | 支持的域控制器操作系统                                       |
| --------------------------- | ----------------------- | ------------------------------------------------------------ |
| Windows 2000 混合模式       | 不适用                  | Windows NT 4.0Windows 2000Windows Server 2003                |
| Windows 2000 本机模式       | 0                       | Windows 2000Windows Server 2003Windows Server 2008Windows Server 2008 R2 |
| Windows Server 2003 过渡模式 | 1                       | Windows NT 4.0Windows Server 2003                            |
| Windows Server 2003         | 2                       | Windows Server 2003Windows Server 2008Windows Server 2008 R2Windows Server 2012 |
| Windows Server 2008         | 3                       | Windows Server 2008Windows Server 2008 R2Windows Server 2012 |
| Windows Server 2008 R2      | 4                       | Windows Server 2008 R2Windows Server 2012                    |
| Windows Server 2012         | 5                       | Windows Server 2012                                          |



表 2-4. 林功能级别

| 功能级别                    | 功能级别编号            | 支持的域控制器操作系统                                     |
| --------------------------- | ----------------------- | ---------------------------------------------------------- |
| Windows 2000                | 0                       | Windows NT 4.0Windows 2000Windows Server 2003Windows Server 2008Windows Server 2008 R2 |
| Windows Server 2003 过渡模式 | 1                       | Windows NT 4.0Windows Server 2003                          |
| Windows Server 2003         | 2                       | Windows Server 2003Windows Server 2008Windows Server 2008 R2Windows Server 2012 |
| Windows Server 2008         | 3                       | Windows Server 2008Windows Server 2008 R2Windows Server 2012 |
| Windows Server 2008 R2      | 4                       | Windows Server 2008 R2Windows Server 2012                  |
| Windows Server 2012         | 5                       | Windows Server 2012                                        |

> **注意**：

有关升级 Active Directory 的更多信息，请参阅第 19 章。

##### Windows 2000 域模式

每个 Windows 2000 Active Directory 域都运行在两种模式之一：混合模式（默认）或本机模式。混合模式域允许运行早期版本 Windows NT 的服务器作为域控制器存在于该域中。本机模式域仅支持 Windows 2000 或更高版本的域控制器。支持混合模式域是管理员将 Windows NT 域更新到 Active Directory 所必需的。混合模式 Active Directory 域模拟 Windows NT 域的某些行为。请记住，在早期版本的 Windows NT 中，网络通常有一个主域控制器( Primary Domain Controller ,PDC )，用于保存账户数据库的可写副本，以及零个或多个备份域控制器( Backup Domain Controller ,BDC )，用于保存从 PDC 复制的只读账户数据库。为了让 Active Directory 网络支持较旧的 Windows NT 域控制器，其中一台（且仅有一台）Active Directory 服务器必须充当 PDC。Windows NT PDC 在发生更改时通知 BDC，随后 BDC 从 PDC 请求账户数据库的副本，以从 Active Directory 获取相关的用户、组和计算机账户。虽然所有账户都会被复制出去，但每个对象的总属性数量远少于 Active Directory 现在为这些类型的对象所保存的全部属性。

从混合模式切换到本机模式是一个简单但单向的更改。由于这是单向更改，您应在实验室中进行测试并做好相应规划。一旦决定继续执行此过程，只需使用 Active Directory 域和信任关系管理单元连接到 DC，然后在“常规”选项卡下将模式更改为本机模式。完成此操作后，唯一的回退方法是重新安装该域的所有域控制器，并从升级前所做的备份进行还原。

> [!NOTE]
>
> 除非确定该域中任何位置都不需要存在任何备份域控制器( Backup Domain Controller ,BDC)，否则切勿升级到 Windows 2000 本机模式。

混合模式与本机模式的具体区别见表 2-5。

表 2-5. 混合模式与本机模式的区别

| 操作 | Windows 2000 混合模式 | Windows 2000 本机模式 |
| ----------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 复制 | 主域控制器( Primary Domain Controller ,PDC) FSMO 主机向 Windows NT BDC 发送更新；同一台域控制器( Domain Controller ,DC)在与其他 Active Directory DC 通信时，其行为与普通 Active Directory DC 相同。所有 Active Directory DC 之间使用多主机复制。 | 仅允许 Active Directory DC，因此所有 DC 都使用多主机复制。 |
| NetBIOS | 无法禁用。 | 可以禁用。 |
| 组功能 | Windows NT 组嵌套规则；全局组和域本地组不允许进行同作用域组嵌套。域本地组仅限 DC 使用。通用组不能启用为安全组，但可嵌套在其他通用组中。不能在组类型或作用域之间转换。 | Windows AD 组嵌套规则；允许同作用域组嵌套。所有域成员上均可使用域本地组。通用组可以启用为安全组。允许在组类型和作用域之间转换。 |
| 帐户迁移 | 无法使用 `sIDHistory`；不能使用 `Movetree` 或 `ADMT` 将对象移入域中。 | 可以使用 `sIDHistory`。可以使用 `Movetree` 和 `ADMT`。 |

> [!NOTE]
>
> 将任意域从混合模式转换为本机模式，不会以任何方式影响其他任何域。无论转换的是根域还是子域，都没有关系，因为这样做只是移除该域向域内旧版 Windows NT BDC 复制数据的能力，并不会影响其与其他域中的 Windows 2000 域控制器进行复制和交互的能力。

#### 组

Active Directory 支持三种组作用域( Group Scope )：*域本地( Domain Local )*、*全局( Domain Global )*和*通用( Universal )*。这些作用域中的组会根据域功能级别和林功能级别的不同而略有差异。更复杂的是，每个组作用域都可以具有两种类型：*通讯组( Distribution )*和*安全组( Security )*。

类型是最容易定义的部分。如果类型为通讯组，则登录期间不会将该组的 SID 添加到用户的安全令牌中，因此它不能用于 Windows 安全用途。通讯组通常用作通讯列表（一组用户，可以同时向所有用户发送邮件或即时消息），不过也可以将其用作基于轻型目录访问协议( Lightweight Directory Access Protocol ,LDAP)的应用程序或其他不使用标准 Windows 安全模型的应用程序的安全组。Microsoft Exchange 使用 Active Directory 通讯组来表示通讯列表。相比之下，安全组会在登录期间枚举，用户所属的任何组的 SID 都会添加到用户的安全令牌中。Exchange 也可以将安全组用作通讯列表。

如果安全主体( Security Principal )所属的组过多，所有支持 Kerberos 的 Windows 版本都会遇到问题。问题在于，安全主体的令牌会变得过大，以致 Windows 无法处理，用户可能会遇到身份验证问题或其他 Kerberos 问题。这种现象通常称为*令牌膨胀( Token Bloat )*。有关令牌大小问题的详细信息，请参阅[此链接](http://support.microsoft.com/kb/327825)。通讯列表和安全组的三种不同作用域源自 Windows NT 的历史遗留以及全局编录( Global Catalog ,GC )的引入。全局组和域本地组是 Windows NT 组的直接继承者；这些组的成员身份只能从创建它们的域中的域控制器( Domain Controller ,DC )上获取。通用组的成员身份既可以从创建它们的域中的域控制器上获取，也可以从林中的所有全局编录上获取。通用组和全局组可用于林中或信任域中任何资源的访问控制列表( Access Control List ,ACL )中。域本地组只能用于创建它们的域中的 ACL。

为了帮助你全面了解组在 Active Directory 中的工作方式，本节将说明以下内容：

- 每种组类型可以包含哪些安全主体
- 如何跨域边界嵌套组
- 在不同组作用域之间转换时有哪些可用选项

首先，我们来看看域内组嵌套受哪些规则约束。表 2-6 显示了哪些类型的组可以嵌套在其他类型的组中。

表 2-6. 基于组作用域( Group Scope )的组成员身份限制

|                 |                     | 可包含域本地组( Domain Local Group ) | 可包含域全局组( Domain Global Group ) | 可包含通用组( Universal Group ) |                 |                     |                 |
| --------------- | ------------------- | ------------------------ | ------------------------- | --------------------- | --------------- | ------------------- | --------------- |
| 作用域 | 类型 | 通讯组( Distribution Group ) | 安全组( Security Group ) | 通讯组 | 安全组 | 通讯组 | 安全组 |
| 域本地 | 通讯组 | 是 | 是 | 是 | 是 | 是 | 是 |
| 安全组 | **是** | **是** | 是 | 是 | 是 | **是** | |
| 域全局 | 通讯组 | 否 | 否 | 是 | 是 | 否 | 否 |
| 安全组 | 否 | 否 | **是** | **是** | 否 | 否 | |
| 通用 | 通讯组 | 否 | 否 | 是 | 是 | 是 | **是** |
| 安全组 | 否 | 否 | **是** | **是** | **是** | **是** | |

尽管此表已经足够清晰，但还需要考虑另一个复杂因素：跨域组成员身份( Cross-Domain Group Membership )。

##### 跨域边界的组成员身份

所有组的限制如表 2-7 和表 2-8 所示。请注意，尽管通用组可以包含来自不同域的成员，但这些域不能跨越林。所有通用组成员必须来自同一个林。

表 2-7. 基于组作用域的组成员身份限制

| 组作用域 | 可以包含来自以下域的用户和计算机 | | 可以包含来自以下域的域本地组 | |
| --- | --- | --- | --- | --- |
| | 同一域 | 不同域 | 同一域 | 不同域 |
| 域本地组 | 是 | 是 | 是 | 否 |
| 域全局组 | 是 | 否 | 否 | 否 |
| 通用组 | 是 | 是 | 否 | 否 |

表 2-8. 基于域的组成员身份限制

| 组作用域 | 可以包含来自以下域的域全局组 | | 可以包含来自以下域的通用组 | |
| --- | --- | --- | --- | --- |
| | 同一域 | 不同域 | 同一域 | 不同域 |
| 域本地组 | 是 | 是 | 是 | 是 |
| 域全局组 | 是 | 否 | 否 | 否 |
| 通用组 | 是 | 是 | 是 | 是 |

表 2-7 和表 2-8 需要与表 2-6配合使用。通常情况下,你会先查阅表 2-6,确定某个组可以包含哪些成员(如果存在此类限制),然后再对照表 2-7 和 2-8,从而明确跨域边界时可用的选项。

##### 组的转换

组能否转换受到限制，具体取决于组的现有成员以及组的当前类型和作用域。前者应当相当明显，这基于 表 2-6 中所示的现有限制。如果转换完成后，现有组成员不是新组类型的有效成员，则转换过程将无法进行。组间转换的能力取决于以下限制：

- 安全组( Security Group )可以转换为分发组( Distribution Group )。
- 分发组可以转换为安全组。
- 域本地组( Domain Local Group )可以转换为通用组( Universal Group )，前提是该域本地组尚未成为另一个域本地组的成员。
- 域全局组( Domain Global Group )可以转换为通用组，前提是该域全局组不包含任何其他域全局组。
- 通用组可以转换为域全局组，前提是组中的所有成员均为该组原先所在域中的用户。
- 通用组可以转换为域本地组。

> **注意**：

将通讯组转换为安全组的好处显而易见：你可以将该组用于 Windows 安全目的。而将安全组转换为通讯组的好处通常不那么明显。这种转换最有用的一点是，你可以安全地禁用一个安全组，以验证它是否被用于 Windows 安全用途。

以前，如果你不知道某个组是否被用于 Windows 安全用途，你只能删除它，并期望不会出问题。如果真出了问题，你就得设法恢复该组，或者想办法使用一个新组。现在，你只需将该组转换为通讯组；如果出了问题，只需再将组改回安全组，就能恢复原有的功能。

### 2.3. 本章小结

本章介绍了 Active Directory 部分主要内部机制的基础知识,涵盖域( Domain )、树( Tree )、林( Forest )、组织单位( Organizational Unit ,OU )、全局编录( Global Catalog ,GC )、FSMO 角色,以及林和域功能级别等概念。随后深入探讨了 Active Directory 中组的工作方式,以及不同域模式和功能级别下可用的各项功能。

掌握这些内容后,接下来我们将介绍可用于管理 Active Directory 的各类管理工具。

---

## 第 3 章 Active Directory 管理工具

Windows 开箱即用,内置了大量用于管理 Active Directory 的工具。遗憾的是,除非你知道哪种工具适合手头任务,否则不翻遍各种控制台,就很难弄清楚该如何完成某项工作。更糟糕的是,有时执行任务根本没有图形用户界面( Graphical User Interface ,GUI),只能由你自行找出合适的命令行实用工具或 PowerShell 命令。

本章旨在带你概览 Active Directory 附带的各类管理工具,让你对如何完成任务有总体认识。在本书中,你会看到对各种管理工具——包括 GUI 和命令行工具——的引用,以及使用这些工具执行特定任务的说明。对于本书其他章节已充分讲解的工具,本章不再介绍,而会指引你查阅相应章节,以获取所需信息。

### 3.1. 管理工具

Windows 2000 中最初发布的 Active Directory 附带了一系列微软管理控制台( Microsoft Management Console ,MMC)管理单元,支持对目录的大部分内容进行基于 GUI 的管理。随着时间的推移,这些管理单元不断改进,但 Windows 2000 附带的 Active Directory GUI 并未发生重大演变。Windows Server 2008 R2 引入了用于管理 Active Directory 的新一代 GUI 工具的第一个版本:Active Directory 管理中心( Active Directory Administrative Center ,ADAC)。随后在 Windows Server 2012 中,ADAC 得到了进一步改进,增加了更多功能并提升了性能。

我们知道,并非所有人都会在短期内运行 Windows Server 2012,因此本章同时涵盖旧版 MMC 管理单元(如 Active Directory 用户和计算机)和新的 ADAC 控制台。在 ADAC 能够完全取代所有旧版管理单元之前,你很可能会在较长一段时间内同时使用这两套工具。

#### Active Directory 管理中心( Active Directory Administrative Center ,ADAC)

Active Directory 管理中心是 Microsoft 的新 GUI 工具。ADAC 的第一个版本随 Windows Server 2008 R2 和 Windows 7 远程服务器管理工具( Remote Server Administration Tools ,RSAT)一起提供。ADAC 初始版本存在许多不足之处，Microsoft 在 Windows Server 2012 和 Windows 8 RSAT 工具中修正了其中的许多问题。

与旧版 GUI 相比，ADAC 的独特之处在于它构建在 Windows PowerShell 之上。每当在 ADAC 中执行操作时，ADAC 都会调用适用于 Windows PowerShell 的 Active Directory 模块中的 PowerShell cmdlet。这些 Windows PowerShell cmdlet 转而连接到 Windows Server 2008 R2 中引入的 Active Directory Web 服务( Active Directory Web Service ,ADWS)。如果要将 ADAC 用于某个域( domain )，而该域中没有任何 Windows Server 2008 R2 或更高版本的域控制器( Domain Controller ,DC)，则需要下载并安装适用于 Windows Server 2003 或 Windows Server 2008 的 ADWS。我们将在第 9 章中更详细地讨论 ADWS，包括如何将其添加到较旧域控制器的详细信息。

图 3-1 显示了带标注的 ADAC 界面示意图，可帮助你熟悉本节中使用的术语（例如，导航窗格( navigation pane )、任务窗格( task pane )等）。任务窗格中直观的右键菜单和上下文选项可让你轻松快速熟悉该界面，因此我们不会花太多时间介绍使用 ADAC 管理对象( object )的基础知识。相反，我们将重点介绍 ADAC 中一些可能并非显而易见的功能。




![Active Directory Administrative Center diagram](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663332.webp)


图 3-1. Active Directory 管理中心示意图

##### PowerShell 历史记录

Windows Server 2012 中 ADAC 的新增功能之一是能够查看在使用控制台时 ADAC 执行的 Windows PowerShell 命令。这对于学习 PowerShell 极为有用，因为您可以先通过图形界面执行一次任务，然后便可掌握基础，进而高效地将其编写为脚本。




![The PowerShell History pane](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663333.webp)


图 3-2. PowerShell 历史记录窗格

图 3-2 中的 Windows PowerShell 历史记录窗格反映了创建一个名为 North America 的新组织单位( Organizational Unit ,OU),然后将一个用户对象移入 North America OU 的操作。您可以使用左侧的加号/减号按钮展开或折叠某个 cmdlet,以便于阅读。工具栏上的“复制”按钮会将命令复制到剪贴板,方便您稍后在脚本中重用。

如果您想查看 ADAC 执行的所有只读 PowerShell 调用,请勾选“显示全部”(如图 3-2 右上角所示)。例如,这将显示为搜索而执行的命令。该选项默认处于禁用状态,因为呈现的数据量会非常大。

##### 全局搜索

ADAC 中的搜索功能为您提供了一种便捷的方式，让您在搜索活动目录( Active Directory )的同时，还能学习 LDAP 搜索语法。从导航窗格中的“全局搜索”节点进入，您可以选择图形化构建查询，或直接输入 LDAP 过滤器。

若要以图形化方式添加条件，您需要点击搜索文本框最右侧的下箭头以展开搜索区域，如图 3-3 所示。“添加条件”按钮提供了多种常见查询供您选择，继续向下滚动列表还能看到常用的 AD 属性。




![Global Search filter builder](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663334.webp)


图 3-3. 全局搜索过滤器生成器

构建完搜索后，您可以点击“转换为 LDAP”单选按钮（见图 3-3 左上角），查看构成查询的传统 LDAP 语法。在图 3-4 中，ADAC 正在搜索已启用但同时被锁定的用户账户列表。您可以将过滤器复制到剪贴板，然后对其进行修改，或在其他 LDAP 搜索程序中使用。




![Global Search LDAP filter view](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663335.webp)


图 3-4. 全局搜索 LDAP 过滤器视图

全局搜索视图中还有几个值得关注的额外选项，特别是在图 3-3 中。第一个选项是右上角的“范围”下拉菜单。通过“范围”下拉菜单，您可以选择要搜索的域，或者以全局编录( Global Catalog ,GC)为目标搜索整个林。使用带有软盘图标的按钮，您可以保存查询。这些查询将在 ADAC 中供后续使用，无需重新构建。

> [!NOTE]
>
> 如果在“转换为 LDAP”视图中输入自定义 LDAP 筛选器，则无法保存此查询以供日后使用。只有使用条件生成器构建的查询才能保存以供日后使用。

##### 多域支持

与活动目录用户和计算机( Active Directory Users and Computers ,ADUC)相比，活动目录管理中心( Active Directory Administrative Center ,ADAC)的优势之一是支持同时处理林中的多个域。如何将域添加到 ADAC 可能并非一目了然。要添加域，请在导航窗格的空白处右键单击，然后单击“添加导航节点”。

在“添加导航节点”屏幕的右下角（如图 3-5 所示），有一个“连接到其他域”的链接。单击此链接，然后输入要管理的域的完全限定域名( Fully Qualified Domain Name ,FQDN)。




![Add Navigation Nodes dialog](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663336.webp)


图 3-5. 添加导航节点对话框

> [!NOTE]
>
> 还可以使用“添加导航节点”屏幕将组织单位( Organizational Unit ,OU)固定到导航窗格。

##### 可扩展性

如果您以前使用过活动目录用户和计算机( Active Directory Users and Computers ,ADUC)，您可能知道 ADUC 可以扩展以包含其他列和选项卡。遗憾的是，ADAC 并未公开相应的功能。为与 ADUC 一起使用而注册的任何其他选项卡都会有些笨拙地显示在对象属性页的“扩展”部分中，如图 3-6 所示。这里特别令人感兴趣的是“安全性”和“属性编辑器”选项卡，它们在 ADAC 的其他位置没有提供。




![Extensions section of an object in ADAC](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663337.webp)


图 3-6. ADAC 中对象的扩展部分

#### Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC )

ADUC 自 Windows 2000 以来就已存在。图 3-7 展示了 Windows Server 2012 版本。如果您是资深的 Active Directory 管理员，您可能已经注意到，十多年来 ADUC 的变化并不大。尽管如此，尽管引入了 Active Directory 管理中心( Active Directory Administrative Center ,ADAC )，ADUC 仍然是大多数管理员的首选工具。您可以从控制面板或开始菜单的“管理工具”部分启动 ADUC，或者，为了快速启动，只需运行 *dsa.msc*。

![Active Directory Users and Computers (Windows Server 2012 version)](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663338.webp)

图 3-7. Active Directory 用户和计算机（Windows Server 2012 版本）

作为目录管理工具，ADUC 擅长为管理用户和组提供前端，以及搜索和浏览目录、管理层次结构（组织单位( Organizational Unit ,OU )结构）。尽管 ADUC 还有一些其他有用的功能，但一般而言，对于超出此范围的任务，它并不是最佳工具。在本节中，我们不会花太多时间解释如何创建或编辑对象，但会指出一些提示和技巧，帮助您充分利用 ADUC 中的所有功能。

通常，使用 ADUC 查找目录中任何给定部分可用功能的最佳位置是通过右键单击菜单。ADUC 会根据您在目录中的位置以及您在该位置拥有的权限，动态筛选对象创建和管理的选项。当您查看对象的属性时，如果您的权限不允许编辑给定属性，ADUC 也足够智能，会将文本框和其他控件设为只读。例如，在图 3-8中，管理员没有足够的访问权限来修改用户帐户的电子邮件属性，因此 ADUC 已将该字段标记为只读。

![Dynamically disabling fields based on permissions](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663339.webp)

图 3-8. 基于权限动态禁用字段

##### 高级功能

默认情况下，Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC )不会显示其提供的全部功能。要查看全部功能，需要确保已勾选“查看→高级功能”。启用此选项后，你会在域中看到许多额外的容器，并且在对象属性中看到大量额外的选项卡。如果比较图 3-8和图 3-9，你会看到在启用高级功能后，用户帐户上会显示多少额外的选项卡。

![User properties with Advanced Features enabled](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663340.webp)

图 3-9. 启用高级功能后的用户属性

尤其值得关注的是安全( Security )选项卡和属性编辑器( Attribute Editor )选项卡。如图 3-10所示，安全选项卡允许你通过友好的界面编辑给定对象的权限（例如，类似于管理文件系统上的权限）。我们将在第 16 章深入讨论 Active Directory 中的权限管理。属性编辑器选项卡让你可以查看对象的全部属性，无论 ADUC 是否在某个属性页中原生公开它们。我们将在本章的 ADSI Edit 一节中更详细地探讨属性编辑器。

![The ACL editor on the Security tab](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663341.webp)

图 3-10. 安全选项卡上的 ACL 编辑器

##### 保存的查询

如果你需要在目录中处理特定的对象集，或者经常搜索相同的内容，你可能会发现保存的查询功能非常方便。借助保存的查询，你可以创建目录的自定义“视图”，而 Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC )会在不同会话之间记住这些视图。要创建查询，请右键单击“保存的查询”节点（如图 3-7左上角所示），然后单击“新建”→“查询”。

![New Query dialog](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663342.webp)

图 3-11. 新建查询对话框

在新建查询窗口（图 3-11）中，你可以提供名称、查询根( Query Root )以及用于查找所需对象的实际 LDAP 筛选器。查询根仅允许你定义搜索应从目录中的何处开始。默认情况下，查询将搜索整个域，但例如，你可以使用“浏览”按钮将查询范围限定到特定组织单位( Organizational Unit ,OU )。

要构建搜索，请单击“定义查询”。如图 3-12所示，ADUC 提供了一个方便的筛选器生成器，以图形方式定义搜索，因此你无需熟悉手动构建 LDAP 筛选器。如果某个预定义模板不适用，你可以从屏幕顶部的“查找”下拉列表中切换到你要查找的对象类型，或者可以使用该下拉列表中的“自定义搜索”选项直接输入 LDAP 筛选器。我们将在第 7 章中深入讨论构建 LDAP 筛选器。

![LDAP filter builder](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663343.webp)

图 3-12. LDAP 筛选器生成器

保存的查询的定义存储在本地，因此如果你在另一台计算机上打开 ADUC，将看不到你的查询。幸运的是，你可以右键单击任何保存的查询，并使用“导出查询定义”选项将查询保存到 XML 文件。然后，你可以在另一台计算机上导入该 XML 文件，或与同事共享。

##### 控制拖放移动

Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC)中另一个便捷功能，是能够将对象或整个对象层次结构拖放到目录中的新位置。在底层，ADUC 会负责处理实际移动对象或树所需的 LDAP 命令。遗憾的是，此功能的缺点是管理员极容易意外移动对象。为解决此问题，Microsoft 在后续版本的 ADUC 中做了一些更改。

第一项更改是警告消息，它要求管理员确认移动，并告知移动对象可能带来的一些潜在风险（图 3-13）。遗憾的是，许多管理员并不会特别认真地先阅读对话框再单击“确定”。为解决这个问题，可以在 Active Directory 中设置一个选项，从而完全禁用 ADUC 中的拖放移动。




![Drag-and-drop move object confirmation](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663344.webp)


图 3-13. 拖放移动对象确认

要了解如何禁用拖放移动，请参阅 Microsoft 知识库文章 [827687](http://support.microsoft.com/kb/827687)。你需要使用 ADSI Edit 进行更改；如果你还不熟悉此工具，请参阅下一节中关于 ADSI Edit 的讨论。

##### 任务板

Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC )源自 Microsoft 管理控制台( Microsoft Management Console ,MMC )管理单元( Snap-in )，它继承的特性之一是能够创建任务板( Taskpad )。任务板允许您创建具有自定义任务子集的 ADUC 自定义视图。这是一种为帮助台技术人员或委派的组织单位( Organizational Unit ,OU )管理员创建 ADUC 控制台的好方法。

要创建任务板，您需要启动一个新的 MMC 控制台(开始→运行→**`mmc.exe`**)，然后添加 ADUC 管理单元。要添加管理单元，请转到文件→添加/删除管理单元。在左侧找到 Active Directory 用户和计算机，然后单击添加 >。一旦有了新的 MMC 设置，右键单击要启动任务板的位置，然后单击新建任务板视图，如图 图 3-14 所示。




![Context menu in ADUC](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663345.webp)


图 3-14. ADUC 中的上下文菜单

使用向导完成自定义后，请务必通过文件→保存菜单保存控制台。如果您正在寻找一个简单控制台，它从给定的 OU 启动，并且在其他方面与 ADUC 相同，请使用“从这里新建窗口”选项，如图 图 3-14 所示。保存生成的 MMC，每次打开时，ADUC 都将从您指定的位置启动。后一个选项特别有用，可以快速为初级管理员和技术人员提供筛选后的控制台。

#### ADSI Edit

ADSI Edit 是一个管理工具，其历史可追溯到早期用于 Active Directory 的资源工具包( Resource Kit )工具。与许多资源工具包工具一样，ADSI Edit 现在包含在用于 Active Directory 的远程服务器管理工具( Remote Server Administration Tools ,RSAT)中；可通过控制面板的“管理工具”部分访问，或通过启动 *adsiedit.msc* 来打开。

ADSI Edit 的主要优势在于，它允许您以友好（有时是解码后）的方式浏览对象的所有属性，并通过浏览来查找对象，就像使用活动目录用户和计算机( Active Directory Users and Computers ,ADUC)或活动目录管理中心( Active Directory Administrative Center ,ADAC)一样。 ADSI Edit 还允许您通过简单的图形用户界面( Graphical User Interface ,GUI)查看和编辑配置命名上下文( Configuration Naming Context )中的数据。

如果您是第一次启动 ADSI Edit，首先需要做的是转到“操作”→“连接到”。在 图 3-15 所示的“连接设置”对话框中，您可以从“选择已知命名上下文”下拉列表中选择一个命名上下文( Naming Context )，或者如果要连接到活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)实例，则改为输入该命名上下文的可分辨名称( Distinguished Name ,DN)。同样，您可以指定特定的域控制器( Domain Controller ,DC)或 AD LDS 服务器，或者也可以选择让 ADSI Edit 为您选择一个。“高级”按钮允许您连接到全局编录( Global Catalog ,GC)或指定用于绑定的备用凭据。




![ADSI Edit Connection Settings](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663346.webp)


图 3-15. ADSI Edit 连接设置

连接后，您可以像使用任何其他工具一样浏览结构。要查看对象的属性，请右键单击该对象，然后单击“属性”。您将看到类似于 图 3-16 的对话框。




![ADSI Edit Attribute Editor with Filter menu](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663347.webp)


图 3-16. 带筛选器菜单的 ADSI Edit 属性编辑器

> [!NOTE]
>
> 从技术上讲，你应该能够使用 ADSI Edit 连接到第三方 LDAP 服务器并对其进行管理，但根据我们的经验，这通常效果不佳。

请注意“筛选”按钮的菜单，该菜单也显示在 图 3-16 中。你可以使用此菜单限制显示的属性，使 ADSI Edit 的输出更有用。以下是“筛选”菜单中的选项：

- **仅显示有值的属性**

  筛选列表，仅显示已填充数据的属性。

- **仅显示可写属性**

  筛选列表，仅显示 Active Directory 报告当前用户可写的属性。

- **显示属性：必需**

  显示架构中标记为对象类（例如 user）必需（必须填充）的属性。

- **显示属性：可选**

  显示架构中标记为对象类（例如 user）可选（无需填充）的属性。

- **显示只读属性：构造**

  显示由 Active Directory 内部即时计算值的属性。

- **显示只读属性：反向链接**

  显示链接属性关系的反向链接组件。反向链接属性是构造的，不可更改。例如，在组成员关系中，组上的 `member` 属性是可更改的，而反向链接属性——用户上的 `memberOf` 属性——则不可更改。

你还可以通过单击“安全”选项卡来编辑对象的 ACL。ADSI Edit 中的 ACL 编辑器与 ADUC 和 ADAC 中的界面相同。如果右键单击用户，会出现一个用于重置用户密码的上下文界面，这在管理 AD LDS 实例时特别有用。你还可以右键单击并删除对象、移动对象（ADSI Edit 中没有拖放功能）或创建对象。

使用 ADSI Edit 创建对象可能比使用其他原始 LDAP 编辑工具更容易，但也并非特别直观。单击“创建”时，ADSI Edit 首先会向你显示一个列表，其中包含架构中可在所选位置创建的所有对象类。接下来，ADSI Edit 会显示一个页面，用于为架构中所选对象类定义的每个必需属性指定值。最后，你可以选择在最后一页使用“更多属性”按钮指定可选属性。

ADSI Edit 还包含一个 LDAP 查询功能,只需右键单击并依次选择"新建"→"查询"即可访问。你既可以输入原始 LDAP 查询,也可以使用 Windows LDAP 查询生成器以图形化方式构建搜索条件。

#### LDP

有时，深入排查问题最简单的方法就是以原始格式查看支撑数据，而无需借助 GUI 工具通常提供的任何抽象层。自 Windows 2000 起，Microsoft 就在 Active Directory 中内置了一个名为 LDP 的工具。LDP 最初包含在 Windows Resource Kit Tools 中，后来演变为安装 Active Directory RSAT 工具时一并安装的工具。你可以使用 LDP 连接到任何 LDAP 服务器（甚至非 Microsoft 平台），执行搜索、查看数据以及进行修改。

你无法在“开始”菜单中找到 LDP，但可以在命令提示符或“运行”对话框中直接输入 **`ldp`** 来启动它。LDP 启动后，你需要连接到一个域控制器(Domain Controller，DC)（或 AD 轻型目录服务实例，或另一台 LDAP 服务器）。为此，请依次点击 Connection→Connect 打开 Connect 对话框，如图 3-17 所示。如果你想使用 SSL 加密会话，请勾选 SSL 复选框并将端口改为 636。




![LDP Connect dialog](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663348.webp)


图 3-17. LDP Connect 对话框

连接成功后，你会看到一些可匿名访问的目录数据，称为 *RootDSE*。如果你想查看目录中存储的任何数据，通常需要先对连接进行身份验证。为此，请依次点击 Connection→Bind 打开 Bind 对话框，如图 3-18 所示。




![LDP Bind dialog](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663349.webp)


图 3-18. LDP Bind 对话框

Bind 对话框中提供了多个选项可供选择。具体而言，绑定类型包括：

- **Bind as currently logged on user**

  该选项会传递你当前的凭据。如果你登录所使用的域账户在目标服务器/目录上具有足够的权限，通常可以选择此默认选项。

- **Bind with credentials**

  该选项允许你指定一组域凭据来绑定到服务器。如果你当前登录的账户权限不足，需要提升连接权限，该选项会非常有用。

- **Simple bind**

简单绑定( Simple Bind )是许多应用程序使用的方式，如果要连接到第三方轻型目录访问协议( Lightweight Directory Access Protocol ,LDAP )服务器，你很可能会选择这种方式。请记住，简单绑定没有保护凭据的机制——除非使用基于 SSL 的 LDAP，否则在简单绑定中指定的凭据将以明文形式在网络上传输。

就本讨论而言，我们建议你使用默认选项“以当前登录用户身份绑定( Bind as currently logged on user )”。绑定到目录后，LDP 会在右下角的信息窗格中显示绑定尝试的结果。成功的绑定尝试可能会生成类似于以下内容的输出：




```
0 = ldap_set_option(ld, LDAP_OPT_ENCRYPT, 1)
res = ldap_bind_s(ld, NULL, &NtAuthIdentity, NEGOTIATE (1158)); // v.3
    {NtAuthIdentity: User='NULL'; Pwd=<unavailable>; domain = 'NULL'}
Authenticated as: 'COHOVINES\briandesmond'.
-----------
```


绑定尝试失败可能会生成多种不同类型的错误，具体取决于失败原因。如果是凭据错误，你可能会收到类似于以下内容的错误：




```
res = ldap_simple_bind_s(ld, 'BadUsername', <unavailable>); // v.3
Error <49>: ldap_simple_bind_s() failed: Invalid Credentials
Server error: 80090308: LdapErr: DSID-0C0903C5, comment: AcceptSecurityContext 
  error, data 52e, v23f0
Error 0x80090308 The token supplied to the function is invalid
-----------
```


绑定到目录后，就可以开始利用 LDP 的功能了。如果你只是想浏览目录并找到所需的对象，请转到“视图”→“树”，然后输入或选择要从中浏览的根。LDP 将在屏幕左侧构建一棵可浏览的树。




![LDP main view](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663350.webp)


图 3-19. LDP 主视图

若要查看对象的属性，请双击该对象。图 3-19 显示了双击用户对象后的输出。可以看到，LDP 以原始格式显示对象的所有属性。LDP 还会在某些属性旁边提供有用的提示。例如，`userAccountControl` 属性是一个位掩码，用于控制给定对象的多个设置。在图 3-19 中，LDP 解码值(`0x10200`)，并告诉你该对象是普通(已启用)帐户，且配置为密码永不过期。

如果你的目录很大，或者你确切知道要查找什么，可以单击“浏览”→“搜索”，向目录发出轻型目录访问协议( Lightweight Directory Access Protocol ,LDAP )查询。图 3-20 显示了为名为 *COHO-CHI-ADC01* 的计算机构造搜索的过程。你需要指定希望搜索返回的属性，也可以输入星号(*)，以返回所有属性。还可以通过“选项”按钮控制许多高级搜索选项，如排序、超时以及特殊 LDAP 控件的使用。我们将在第 7 章深入讨论活动目录( Active Directory ,AD)搜索时，讨论其中许多选项。




![LDP Search dialog](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663351.webp)


图 3-20. LDP 搜索对话框

若要更改对象，请在 LDP 左侧的树中右键单击该对象，然后单击“修改”。输入属性名称和值，然后单击“Enter”按钮，即可一次修改一个或多个属性，如图 3-21 所示。在图 3-21 中，我们将用户账户( User Account )上的 `title` 属性更改为 `Author`。

操作类型的选择很重要，而且可能有点令人困惑。如果要更新普通属性，请使用“替换”操作。如果要向多值属性( Multivalued Attribute )追加值，请使用“添加”操作。最后，如果要清除属性或从多值属性中删除特定值，请使用“删除”操作。准备好提交更改后，单击“运行”。




![LDP Modify dialog](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663352.webp)


图 3-21. LDP 修改对话框

如果修改成功，LDP 将报告成功，并输出类似以下内容：




```
***Call Modify...
ldap_modify_s(ld, 'CN=Brian Desmond,OU=People,DC=cohovines,DC=com',[1] attrs);
Modified "CN=Brian Desmond,OU=People,DC=cohovines,DC=com".
-----------
```


如果修改失败，LDP 将提供错误代码，你可以重新提交请求。

LDP 工具还提供了许多其他实用功能，包括删除对象或树（Browse→Delete）、重命名对象（Browse→Modify DN）、创建对象（Browse→Add Child）、查看复制元数据（Replication Metadata）（Browse→Replication→Replication Metadata Descriptor，或右键单击该对象并单击 Advanced→Replication Metadata），以及查看对象的 ACL（访问控制列表( Access Control List ,ACL )，即安全描述符( security descriptor )）（Browse→Security→Security Descriptor，或右键单击该对象并单击 Advanced→Security Descriptor）。我们将在第 21 章中更深入地介绍 LDP 的安全描述符功能。

LDP 是一款功能强大的工具，借助它几乎可以完成 LDAP 目录中的任何任务。要充分发挥 LDP 的威力，有时需要深入理解 LDAP 协议；但当你需要查看原始数据，或希望不经任何抽象层直接在目录上执行操作时，LDP 便是工具箱中一件不可多得的好工具。

### 3.2. 自定义活动目录管理单元

遗憾的是,活动目录管理中心( Active Directory Administrative Center ,ADAC)无法针对控制台中可用的数据进行自定义。不过,诸如活动目录用户和计算机( Active Directory Users and Computers ,ADUC)之类的旧版管理单元则具有高度的可扩展性。扩展 ADUC 最常见的示例之一便是显示其他属性,甚至可能是您自行创建的属性。假设您决定向活动目录架构( Active Directory schema )中添加一个名为 `myCorp-LanguagesSpoken` 的属性。相应地,您希望在 ADUC 中显示 `myCorp-LanguagesSpoken`,以便其他人能够查看该用户所说的语言。幸运的是,旧版活动目录管理单元(例如 ADUC 和活动目录站点和服务)可通过修改活动目录中的一个或多个属性进行自定义。您还可以使用 Windows 脚本宿主( Windows Scripting Host ,WSH)、Visual Basic(VB)或任何其他基于 COM 的语言来扩展管理单元的功能。

本节专门回顾活动目录管理单元背后的组件,以及如何修改这些组件以满足您的需求。这些组件包括:

- **显示说明符( Display specifiers )**

  活动目录中包含本地化用户界面信息的对象

- **属性页( Property pages )**

  用于显示信息的选项卡式对话框

- **上下文菜单( Context menus )**

  右键单击某个对象(例如用户)后显示的菜单

- **图标( Icons )**

  查看特定类时显示的图像

- **显示名称( Display names )**

  为属性和类显示的易读名称(例如"姓氏")

- **创建向导( Creation wizard )**

  用于创建对象的向导界面

#### 显示说明符( Display Specifier )

显示说明符是存储在 Active Directory 中的对象，其中包含有关如何通过 Active Directory 管理单元( snap-in )显示和管理特定对象类的对象的信息。这些显示说明符保存在配置命名上下文( Configuration Naming Context )中的 DisplaySpecifiers 容器下。在 DisplaySpecifiers 容器内，每个支持的区域设置( locale )都有一个容器，路径类似于以下内容：

```
LDAP://cn=409,cn=DisplaySpecifiers,cn=Configuration,dc=mycorp,dc=com
```

前面的容器包含 409 的美国/英语区域设置的显示说明符。如果要为其他区域设置创建或管理显示说明符，只需使用该区域设置的相关十六进制代码创建一个新容器，并向其中填充相关显示说明符对象。例如，十六进制的 409 表示十进制的 1,033，而 1,033 是美国/英语区域设置。如果创建 809（十进制 2,057），则会得到英国/英语区域设置；如果创建 40C（十进制 1,036），则会得到法语区域设置。当前安装的区域设置值可在注册表中的 `HKLM\SYSTEM\CurrentControlSet\Control\ContentIndex\Language` 找到。按区域设置提供显示说明符，可让你为地理上分散的客户端群体支持多种语言。

每个特定区域设置的容器都有一系列 `displaySpecifier` 类的对象。对象名称采用 `ObjectClass-Display` 形式。`user` 类有一个名为 `User-Display` 的对象，`computer` 类有一个名为 `Computer-Display` 的对象，依此类推。若要为特定语言扩展特定对象类的界面，只需修改该容器中表示该类的 `displaySpecifier` 对象上的相应属性。

下面是一个简单示例。所有 `displaySpecifier` 对象上都存在 `classDisplayName` 属性。假设我们使用 Support Tools 中的 ADSI Edit 工具打开 `Group-Display` 对象，并将此属性从 `Group` 更改为 `Moose`。如果在 ADUC 工具中右键单击任何容器，通常会显示一个上下文菜单，允许我们新建用户、组或组织单位( Organizational Unit ,OU )（以及其他对象）。进行编辑并重新打开 ADUC 后，它允许我们新建用户、*moose* 或组织单位。`group` 类在界面中的显示方式已更改。如果我们想为法语区域设置更改显示说明符，无论同时更改美国/英语区域设置还是只更改法语区域设置，都应转到（或创建）40C 容器，并将更改应用到 `Group-Display` 对象。

现在，我们来看看你还可以进行哪些其他自定义设置。

#### 属性页( Property Pages )

在 Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC) 中打开任意对象的属性，即可看到现有属性页的数组。你可以向其中添加属性页，并在此显示自己的属性页。不过，要实现这一点，属性页必须作为支持 `IShellExitInit` 和 `IShellPropSheetExt` 接口的组件对象模型( Component Object Model ,COM) 对象存在。这意味着必须先在 Visual Basic、Visual C++ 或类似环境中创建属性页。

创建对象是最困难的部分。而实际上，让系统使用它却很容易。一旦属性页 COM 对象存在，它就会有一个全局唯一标识符( Globally Unique Identifier ,GUID)。然后，你可以使用 ADSI Edit 转到表示要修改的类的显示说明符( Display Specifier )对象，并修改 `adminPropertyPages` 或 `shellPropertyPages` 属性。这些属性是多值的，并按以下形式存储数据：

```
2, {AB4909C2-6BEA-11D2-B1B6-00C04F9914BD}
1, {AB123CDE-ABCD-1124-ABAB-00CC4DD11223}
```

第一项表示属性页应出现顺序的序号。第二项表示 UUID。第三个可选参数可用于存储扩展信息，例如在显示属性页时传递给它的数据。

要将自己的属性页添加到某个类，可以编辑 `Shell` 或 `Admin` 属性页属性，具体取决于希望修改默认（shell）UI 还是管理员 UI，然后按上述格式添加一行。确实就这么简单。你甚至可以修改现有属性页（如果有的话），并按自己的喜好重新排列它们的顺序。

#### 上下文菜单( Context Menus )

在 ADUC 中右键单击某个对象时，会弹出一个上下文菜单。您可以向此上下文菜单添加自己的项。上下文菜单项保存在每个 `displaySpecifier` 对象的 `shellContextMenu` 属性（用于默认 UI）和 `adminContextMenu` 属性（用于管理 UI）中。若某项需同时出现在两者中，则将其放入 `contextMenu` 属性。

添加到上下文菜单的项可以启动应用程序或创建 COM 对象实例。这些数据在相关属性中采用以下形式：




```
1,Extra &Data..., E:\MYPROG.EXE
2,&Extended Attributes...,C:\MYSCRIPT.VBS
3,{DB4909C2-6BEA-11D2-B1B6-00C04F9914BD}
```


请注意，最后一项是 COM 对象，由其 GUID 表示。该 COM 对象必须支持 `IShellExtInit` 和 `IContextMenu` 接口。可以通过将其作为行中的第三个参数包含进来，向 COM 对象传递额外数据。前两项对管理员来说重要得多。可以看到，我们向菜单中添加了两个额外项。这两项分别是一个可执行程序和一个 VBScript 脚本。任何类型的应用程序都可以。第二个参数是希望在上下文菜单中显示的字符串。在字母前使用 & 字符可将该字母指定为加速键( accelerator )。因此，使用前面的代码示例显示菜单时，键入“d”会选择第一个选项，键入“e”会选择第二个选项。

能够将脚本和程序添加到上下文菜单是一项非常强大的功能。将这些脚本和程序与 ADSI 结合使用，即可扩展 Microsoft 提供的管理单元( snap-in )，根据业务或组织需求提供完全自定义的功能。例如，假设您想扩展架构( schema )，并为 `user` 类包含一个新的可选 `myCorp-LanguagesSpoken` 属性。您可以转到相应区域设置( locale )的 `User-Display` 对象，修改 `contextMenu` 属性（使其对用户和管理员均可用），以包含一个在消息框( message box )中显示该属性的 ADSI 脚本。所需的全部代码如下：




```
Option Explicit
Dim wshArgs, objUser
Set wshArgs = WScript.Arguments
Set objUser = GetObject(wshArgs(0))
MsgBox objUser.Get("myCorp-LanguagesSpoken"),,"Languages Spoken"
```


该脚本只是绑定到作为参数传递给程序的对象可分辨名称( distinguished name )，并在 `MsgBox` 中输出该属性，同时显示适当的标题，如图 3-22 所示。




![Viewing the languages spoken by a user](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663353.webp)


图 3-22. 查看用户所使用的语言

在此图中，右键单击了 `guest` 用户对象，弹出一个包含 Languages Spoken 的上下文菜单。如果查看窗口左下角的文本，您可以看到实际显示的是字符串“&Languages Spoken...”。当我们单击该项或按 L 键时，脚本生成的对话框将显示在屏幕上。通常，对话框和上下文菜单不会同时显示，但在此屏幕中我们这样做了，以便向您展示该过程。

您还可以编写一个脚本或程序，允许您修改 `mycorp-LanguagesSpoken` 属性，并使其仅出现在管理员的上下文菜单中。然后，您可以使用 Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC)工具来管理您的用户和此额外属性，如果您不想，就无需实际开发一个全新的界面。

#### 图标

在 Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC)中查看对象容器时，它会为每个对象显示一个适合该对象特定对象类( Object Class )的图标。例如，组织单位( Organizational Unit ,OU)的图标看起来与容器( Container )、用户( User )和打印机( Printer )的图标不同。图标实际上可用于表示该对象的不同状态。例如，如果禁用用户或计算机对象( Computer Object )，图标将更改以指示该对象已禁用。总而言之，可以为任何对象类定义 16 种不同的状态图标( State Icon )。前三种表示关闭（默认状态）、打开和已禁用状态；后 13 种当前未定义，留作自用。

要修改对象类的图标，只需使用 `iconPath` 属性存储以下形式的多值数据：




```
0, c:\windows\system32\myicon.ico
1, c:\windows\system32\myicons.dll, 0
2, c:\windows\system32\myicons.dll, 2
3, c:\windows\system32\myicons.dll, 7
```


这会设置前四个图标值。请记住，0 表示关闭，1 表示打开，2 表示已禁用；3 到 15 未定义。第一行使用带 ICO 扩展名的正确图标文件，因此不需要第三个参数。最后三行分别使用 *myicons.dll* 中的第一个(0)、第三个(2)和第八个(7)图标，使用 DLL 中图标集的索引，从 0 开始。任何客户端要正确显示图标，图标路径必须存在于本地计算机上。请记住要考虑这一点，因为如果企业中的所有客户端要正确显示图标，可能需要将图标文件部署到这些客户端。

#### 显示名称

如前所述，您可以控制类和属性名称在图形用户界面( GUI )中的显示方式。若要更改类名，请修改相关 `displaySpecifier` 对象的 `classDisplayName` 属性中的文本。若要更改属性名称的显示形式，您需要修改多值属性 `attributeDisplayNames`。属性值采用逗号分隔的字符串形式，如下所示：




```
mobile,Mobile Number
physicalDeliveryOfficeName,Office Location
extensionAttribute1,My First Extended Attribute
```


第一个值是对应于架构中属性的 LDAP 名称，第二个值是希望显示的名称。请注意，除非您希望在名称前添加空格，否则不要在逗号和第二个值之间插入空格。



叶子对象或容器对象

在 ADUC 中查看对象时，有些对象显示为容器，有些则显示为叶子对象。您所关注的大多数对象实际上都充当容器的角色，即使它们在界面上显示为叶子对象。以计算机上的打印机为例，如果该打印机作为 `printQueue` 对象发布到 Active Directory，则该对象将在其发布所在的计算机对象中显示为叶子对象。计算机对象充当其发布的任何打印队列的容器，但默认情况下，用户、计算机和组对象不会显示为容器。实际上，ADUC 的“查看”菜单中有一个选项可以更改此行为，称为“将用户、组和计算机视为容器”。然而，这样做会将所有对象都按此方式处理。您也可以通过修改特定 `displaySpecifier` 对象中 `treatAsLeaf` 的布尔值，将其按要求设为 `True` 或 `False`，从而更改该对象的默认设置。

#### 对象创建向导( Object Creation Wizard )

创建用户、组或组织单位( Organizational Unit ,OU )时,Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC )会提供一个简单的向导,允许您为该对象指定相关数据。管理员可以通过以下两种方式之一修改默认行为:如果存在现有向导,可以完全替换它;也可以仅向该向导添加额外页面。向导只能存在一个,因此您要么创建新向导,要么修改现有向导。假设您希望向导请求 `user` 类的 `myCorp-LanguagesSpoken` 属性值。由于现有的用户创建向导不允许为该属性输入数据,因此您可以将整个向导替换为您自己的新向导,也可以在该向导中放置一个新页面来接收该属性的数据。对于属性页( property pages ),我们需要将新向导或创建向导扩展( creation wizard extensions ,即现有向导的额外页面)创建为支持 `IDsAdminNewObjExt` 接口的 COM 对象。替换系统正在使用的默认向导的新向导称为*主扩展( primary extensions )*,它们会替换用于创建对象的核心页面集。主扩展支持创建向导扩展;例如,您可以为所有用户定义一个主扩展,如果之后需要,还可以使用创建向导扩展添加几个额外页面。

如果要用主扩展完全替换该向导,请修改相关 `displaySpecifier` 对象的 `creationWizard` 属性,使其包含该 COM 对象的 GUID。如果仅提供创建向导扩展,则您需要在 `createWizardExt` 多值属性中指定页面应显示的顺序,随后指定 UUID。格式与属性页相同。

### 3.3. Active Directory PowerShell 模块

Active Directory PowerShell 模块首次出现在 Windows Server 2008 R2 中，并在 Windows Server 2012 中得到增强。虽然该模块目前已是第二代迭代版本，但仍有一些任务无法通过它完成。ADAC 的所有任务都使用 AD PowerShell 模块，因此，如果你能在 ADAC 中完成某项操作，那么该任务也能通过 AD PowerShell 模块完成。此外，正如我们在第 6 章中所讨论的，Windows Server 2012 引入了大量用于管理复制( Replication )的 cmdlet。

在本书中，你会发现一些使用 AD PowerShell 模块完成各种任务的小示例；我们鼓励你阅读这些示例，并在此基础上加以扩展，利用 PowerShell 这类脚本语言来更高效地完成日常 Active Directory 任务。Microsoft 已在 PowerShell 上投入了大量资源，尤其是在 Windows Server 2012 中，这显然是未来的发展方向。

即便你从未涉足脚本编写，我们也强烈建议你尝试一下。ADAC 中的 PowerShell 历史记录窗格使发现 AD PowerShell cmdlet 变得极其容易；PowerShell 在过去几年中已大幅成熟，如今在互联网上也有完善的文档。

如果你想寻找一些与学习 PowerShell 相关的资源，我们强烈推荐 Lee Holmes 所著的 [*Windows PowerShell Cookbook, Second Edition*](http://oreil.ly/Win_PowerShell_CB2)(O’Reilly)。

### 3.4. 最佳实践分析器( Best Practices Analyzer ,BPA)

保持 Active Directory 健康是任何管理员都关心的问题，而健康的域控制器( Domain Controller ,DC)或林( Forest )的定义在互联网上是一个众说纷纭的话题。一直以来，Microsoft 在 Windows 中附带了一个名为 *dcdiag* 的工具：*dcdiag* 支持的众多测试可以帮助管理员主动检查域控制器、域( Domain )或林的健康状况，并在出现问题时进行故障排除。

*dcdiag* 的不足之处在于其输出难以阅读，测试预期目标所需的开关列表很长，并且发现问题时通常没有可操作的建议。从 Windows Server 2008 R2 开始，Microsoft 着手解决这些问题，为 Active Directory 创建了最佳实践分析器( BPA )，并将其作为操作系统的一部分。Windows Server 2012 包含 41 项测试，用于分析管理员通常会遇到的许多最常见问题和错误配置。

要访问 BPA，请在左侧的 AD DS 节点下找到服务器管理器( Server Manager )，然后向下滚动到最佳实践分析器。要运行 BPA 扫描，请在右侧单击“任务”→“启动 BPA 扫描”。您可以选择一台或多台域控制器来运行 BPA 扫描，如图 3-23所示。

![Selecting BPA target servers](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663354.webp)

图 3-23. 选择 BPA 目标服务器

扫描完成后，您将看到结果（图 3-24）。每个结果都会显示出现问题的服务器、严重级别、问题名称以及总体类别。如果参考图 3-24，您会看到，当您选择一个问题时，其下方会显示该问题的描述，以及指向更多信息和修正步骤的链接。例如，图 3-24 中选择的问题在服务器管理器中有以下指导：

> **问题：**
>
> 此域( Domain )中的某些组织单位( Organizational Unit ,OU)未启用意外删除保护。
>
> **影响：**
>
> 如果 Active Directory 域中的所有 OU 均未启用意外删除保护，则 Active Directory 环境可能会因意外批量删除对象而中断。
>
> **解决方法：**
>
> 确保此域中的所有 OU 均启用意外删除保护。

![BPA results](./image/3.%20Active%20Directory%20Management%20Tools/httpatomoreillycomsourceoreillyimages1663355.webp)

图 3-24. 最佳实践分析器( Best Practices Analyzer ,BPA)结果

虽然可以在服务器管理器( Server Manager )中按需运行 BPA，但也可以通过 Windows PowerShell 调用 BPA。这对于一次性检查多台服务器，或计划对林( Forest )进行定期 BPA 扫描可能很有用。若要使用 Windows PowerShell 调用 Active Directory BPA，请使用 *Invoke-BpaModel* cmdlet：

```
Invoke-BpaModel "Microsoft/Windows/DirectoryServices"
```

扫描完成后，请使用 *Get-BpaResult* 查看扫描结果：

```
Get-BpaResult "Microsoft/Windows/DirectoryServices"
```

使用 BPA PowerShell cmdlet，可以计划一个任务，用于检查结果中是否存在任何警告或错误，并在发现问题时发送电子邮件警报。除 Active Directory 之外，Windows Server 的许多其他组件也包含 BPA。可以使用 *Get-BpaModel* cmdlet 获取可用 BPA 的完整列表：

```
Get-BpaModel | ft Id,Name
```

### 3.5. 基于活动目录的计算机激活

当微软发布 Windows Vista 和 Windows Server 2008 时，它改变了在企业环境中安装授权 Windows 副本的范式。在此变革之前，企业会收到特殊的“批量许可”安装介质和密钥，无需在线激活。随着密钥管理服务器( Key Management Server ,KMS)的引入，这种情况发生了改变，KMS 通过一个特殊许可证密钥进行激活。随后，网络上的计算机会被引导至 KMS 进行激活。

KMS 模式面临的一些挑战包括缺乏身份验证或安全性——任何具有网络访问权限的计算机都可以针对 KMS 自行激活。此外，企业现在被迫仅为 Windows 和 Microsoft Office 的许可维护额外的服务器和基础设施。

Windows 8 和 Windows Server 2012 客户端支持从存储在活动目录中的数据激活。由于激活数据存储在活动目录中，因此不再依赖专用基础设施，并且客户端还必须加入域(因此隐式通过身份验证)才能激活其 Windows 安装。

您可以使用批量激活管理工具 3.0( Volume Activation Management Tool 3.0 ,VAMT)将激活信息发布到林。VAMT 作为 Windows 自动部署工具包( Windows Automated Deployment Kit ,ADK)的一部分提供，可从[此链接](http://bit.ly/WX8xW2)下载。

### 3.6. 总结

本章的目标是介绍作为活动目录( Active Directory ,AD)管理员可用的各种管理工具，以及这些工具的一些优点和局限性。如果您已经使用活动目录一段时间了，那么您很可能用过活动目录用户和计算机( Active Directory Users and Computers ,ADUC)，但您可能还没有看过新的活动目录管理中心( Active Directory Administrative Center ,ADAC)。如果您觉得 Windows Server 2008 R2 中的 ADAC 令人失望，请查看 Windows Server 2012 版本——它已经得到了大幅改进。

除了基本的用户、组和计算机管理工具( ADUC 和 ADAC)之外，我们还介绍了 LDP 和 ADSI Edit，这两个更深入的工具让您可以在更少抽象的层面上操作目录。没有任何 GUI 工具能比 LDP 提供更原始的目录视图。我们还讨论了利用脚本语言(如 Windows PowerShell)的重要性，以及 Microsoft 在活动目录的 PowerShell 功能方面所做的投资。

最后，我们了解了几个重要的外围可管理性投资，即最佳实践分析器( Best Practices Analyzer ,BPA)，它可以分析您的活动目录环境的健康状况，以及基于 AD 的计算机激活，它可以让您在不使用 KMS 服务器的情况下保持加入域的计算机处于激活状态。

---

## 第 4 章 命名上下文与应用程序分区

由于活动目录( Active Directory )具有分布式特性，因此有必要将数据划分到不同的分区中。如果不使用数据分区，每个域控制器( Domain Controller ,DC )都必须复制林内的所有数据。通常，根据地理或管理需求对数据进行分组是有益的。可以将域视为一个大型数据分区，也称为*命名上下文*( naming context ,NC )。只有对某个域具有权威性的域控制器才需要复制该域内的全部信息，其他域的信息在这些域控制器上并不需要。另一方面，有些活动目录数据必须复制到林内的所有域控制器。活动目录中有三种预定义的命名上下文：

- 每个域的*域命名上下文*( Domain naming context )
- 林的*配置命名上下文*( Configuration naming context )
- 林的*架构命名上下文*( Schema naming context )

每种命名上下文代表不同类型的活动目录数据。配置命名上下文( Configuration NC )保存与林配置（或林级应用程序配置）相关的数据，例如表示命名上下文、LDAP 策略、站点( Site )、子网( Subnet )、Microsoft Exchange 等的对象。架构命名上下文( Schema NC )包含可存储在活动目录中的数据类型所对应的对象类和属性定义集合。林中的每个域还有一个域命名上下文( Domain NC )，其中包含该域特定的数据——例如用户、组、计算机等。

从 Windows Server 2003 活动目录开始，Microsoft 扩展了命名上下文的概念，允许使用称为*应用程序分区*( application partition )的用户自定义分区。应用程序分区可以包含除安全主体( security principal )以外的任何类型的对象。应用程序分区的一大优势在于，管理员可以定义哪些域控制器复制这些分区中包含的数据。与域命名上下文不同，应用程序分区不受域边界的限制；它们可以存在于林中任何运行 Windows Server 2003 或更高版本的域控制器上，无论该域控制器承载的是哪个域。

你可以通过查询特定域控制器( Domain Controller ,DC)的 *RootDSE* 条目，检索该域控制器维护的命名上下文( Naming Context )和应用程序分区( Application Partition )列表。你可以打开 LDP 实用工具查看 *RootDSE* 属性。要了解如何查看 *RootDSE* 信息，请参阅侧边栏 使用 LDP 查询 RootDSE。

使用 LDP 查询 RootDSE

*ldp.exe* 随 Windows Server 2008 及更高版本提供，并且是 Windows 2000、XP 和 2003 的支持工具( Support Tools )的一部分。你可以使用 LDP 查看来自任何 LDAP 服务器的原始数据。在本书中，适用情况下我们将利用 LDP。除非另有说明，你应假定我们使用的 LDP 版本是 Windows Server 2012 附带的版本。

*RootDSE* 可通过匿名绑定到林( Forest )中的任何域控制器进行查看。使用 LDP 查看此信息的步骤如下：

1. 通过运行 *ldp.exe* 启动 LDP。
2. 单击“连接”→“连接”，输入域控制器的名称，然后单击“确定”。图 4-1 显示了连接到端口 389（LDAP 端口）上的域控制器 *k8devdc01*。
3. LDP 将连接到域控制器，并立即显示所有可匿名查看的 *RootDSE* 输出，如图 4-2 所示。

此界面中显示了大量数据，我们此时不会全部介绍。很多信息将在本书中相关时予以介绍。目前我们特别感兴趣的信息是表 4-1 中属性对应的数据。

我们可以看到此林中根域的可分辨名称( Distinguished Name ,DN)（`DC=k8dev01,DC=brianlab,DC=local`）、此域控制器上承载的应用程序分区的 DN（例如 `DC=DomainDnsZones,DC=k8dev01,DC=brianlab,DC=local`），等等。

此输出在编写用于查询 Active Directory 的脚本和程序时尤其有用。通过利用 *RootDSE* 属性，你可以避免在代码中硬编码路径。

![LDP connection dialog](./image/4.%20Naming%20Contexts%20and%20Application%20Partitions/httpatomoreillycomsourceoreillyimages1663356.webp)

图 4-1. LDP 连接对话框

![LDP RootDSE output on a Windows Server 2008 domain controller](./image/4.%20Naming%20Contexts%20and%20Application%20Partitions/httpatomoreillycomsourceoreillyimages1663357.webp)

图 4-2. Windows Server 2008 域控制器上的 LDP RootDSE 输出

表 4-1. 与命名上下文( Naming Context ,NC)相关的 RootDSE 属性

| 属性名称 | 说明 |
| --- | --- |
| `namingContexts` | 由该域控制器( Domain Controller ,DC)维护的所有命名上下文和应用程序分区( Application Partition )的可分辨名称( Distinguished Name ,DN)列表 |
| `defaultNamingContext` | 该 DC 对其具有权威性的域命名上下文( Domain NC )的 DN |
| `configurationNamingContext` | 配置命名上下文( Configuration NC )的 DN |
| `schemaNamingContext` | 架构命名上下文( Schema NC )的 DN |
| `rootNamingContext` | 林根域的域命名上下文( Domain NC )的 DN |

在本章中，我们将逐一介绍这三个预定义的命名上下文，说明每个命名上下文中包含的数据，然后讨论应用程序分区及其示例用法。

### 4.1. 域命名上下文

每个 Active Directory 域都有一个域命名上下文( Domain Naming Context )，其中包含域特定的数据。此命名上下文( Naming Context ,NC )的根由域的可分辨名称( Distinguished Name ,DN )表示，通常称为 *NC 头*。例如，*mycorp.com* 域的 DN 为 `dc=mycorp,dc=com`。域中的每台域控制器( Domain Controller ,DC )都复制域 NC 的一个副本。

表 4-2列出了域 NC 中的默认顶级容器。请注意，若要使用 Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC )管理单元查看所有这些容器，必须选择“视图”->“高级功能”。或者，可以使用 LDP 或 ADSI Edit 浏览所有这些容器。

要启动 ADSI Edit，请依次点击“开始”→“运行”→**`adsiedit.msc`**。

表 4-2. 域命名上下文（Domain NC）的默认顶级容器

| 相对可分辨名称 | 描述 |
| ------------------------------ | ------------------------------------------------------------ |
| `cn=Builtin` | 预定义内置本地安全组的容器。例如，Administrators、Domain Users 和 Account Operators。 |
| `cn=Computers` | 代表成员服务器和工作站的计算机对象的默认容器。您可以使用 *redircmp.exe* 实用工具更改默认容器。 |
| `ou=Domain Controllers` | 代表域控制器的计算机对象的默认组织单位。 |
| `cn=ForeignSecurityPrincipals` | 用于存放占位符对象的容器，这些对象代表域中来自林外部域的组成员。 |
| `cn=LostAndFound` | 孤立对象的容器。孤立对象是在同一复制周期内，在另一个域控制器上已删除的容器中创建的对象。 |
| `cn=Managed ServiceAccounts` | 托管服务账户的容器。托管服务账户是一种特殊类型的安全主体，可以自行轮换密码。有关托管服务账户的详细信息，请参阅第 10 章。 |
| `cn=NTDS Quotas` | 用于存储配额对象的容器，配额对象用于限制安全主体可以在分区或容器中创建的对象数量。 |
| `cn=Program Data` | 供应用程序存储数据的容器，而非使用自定义顶级容器。 |
| `cn=System` | 用于存放各类域配置对象的容器。例如，信任对象、DNS 对象和组策略对象。 |
| `cn=TPM Devices` | 用于存放受信任平台模块（TPM）密钥恢复信息的容器。 |
| `cn=Users` | 用户和组对象的默认容器。您可以使用 *redirusr.exe* 实用工具更改默认容器。 |

### 4.2. 配置命名上下文( Configuration Naming Context ,NC)

配置命名上下文是林( Forest )配置信息的主要存储库，并复制到林中的每台域控制器( Domain Controller ,DC)。此外，林中每台可写域控制器都保留配置命名上下文的*可写*副本。配置命名上下文的根位于配置容器( Configuration container )中，而配置容器是林根域的子容器。例如，*mycorp.com* 林的配置命名上下文位于 `cn=configuration,dc=mycorp,dc=com`。

表 4-3 列出了配置 NC 中的默认顶级容器。

表 4-3. 配置命名上下文的默认顶级容器

| 相对可分辨名称( Relative Distinguished Name ,RDN) | 描述 |
| ---------------------------------- | ------------------------------------------------------------ |
| `cn=DisplaySpecifiers`             | 包含显示说明符( display specifier )对象的容器，这些对象为 Active Directory MMC 管理单元定义各种显示格式。 |
| `cn=Extended-Rights`               | 扩展权限( extended rights )对象(`controlAccessRight`)的容器。 |
| `cn=ForestUpdates`                 | 包含用于表示林功能级别和域功能级别更改状态的对象。 |
| `cn=LostAndFoundConfig`            | 孤立对象( orphaned object )的容器。 |
| `cn=NTDS Quotas`                   | 用于存储配额对象( quota object )的容器，这些对象用于限制安全主体( security principal )可以在分区( partition )或容器中创建的对象数量。 |
| `cn=Partitions`                    | 包含每个命名上下文、应用程序分区( application partition )和外部 LDAP 目录引用的对象。 |
| `cn=Physical Locations`            | 包含位置对象( location object )(`physicalLocation`)，这些对象可以与其他对象关联，以表示该对象的位置。 |
| `cn=Services`                      | 存储有关服务的配置信息，例如文件复制服务( File Replication Service ,FRS)、Exchange 和 Active Directory 自身。 |
| `cn=Sites`                         | 包含所有站点拓扑( site topology )和复制对象。这包括 `site`、`subnet`、`siteLink`、`server` 和 `nTDSConnection` 对象等。 |
| `cn=WellKnown Security Principals` | 包含表示常用外部安全主体( foreign security principal )的对象，例如 Everyone、Interactive 和 Authenticated Users。 |

### 4.3. 架构命名上下文

架构命名上下文（Schema Naming Context，Schema NC）包含代表 Active Directory 所支持的类和属性的对象。架构是在林范围内定义的，因此架构命名上下文会复制到林中的每个域控制器（Domain Controller，DC）。但请回想一下，架构命名上下文**仅**在拥有架构主控 FSMO 角色的域控制器上可写。架构命名上下文的根可以在schema容器中找到，该容器是配置命名上下文（Configuration NC）的子项。例如，在 *mycorp.com* 林中，schema命名上下文位于 `cn=schema,cn=configuration,dc=mycorp,dc=com`。尽管schema容器看起来是配置容器的子项，但它实际上本身就是一个独立的命名上下文。图 4-3 展示了在 ADSI Edit 工具中架构命名上下文与配置命名上下文是如何分离的。




![ADSI Edit view of the Configuration and Schema naming contexts](./image/4.%20Naming%20Contexts%20and%20Application%20Partitions/httpatomoreillycomsourceoreillyimages1663358.webp)


图 4-3. ADSI Edit 中配置与架构命名上下文的视图

你可能会想，为什么架构不直接包含在配置命名上下文中。正如我们在第 2 章中所讨论的，有一个架构主控 FSMO 角色，它是架构对象更新的唯一主控。由于架构高度敏感，这一角色是必要的。架构修改需要在使用架构的任何更新之前进行处理。要在 AD 使用的复制模型下最容易地保证这一点，其机制就是将架构放入它自己的分区，以便它能在其他更改之前单独复制。

与域命名上下文和配置命名上下文不同，架构命名上下文不维护容器或组织单位的层次结构。相反，它是一个包含 `classSchema`、`attributeSchema` 和 `subSchema` 对象的单一容器。`classSchema` 对象定义了不同类型的类及其关联属性。`attributeSchema` 对象定义了作为 `classSchema` 定义一部分使用的所有属性。此外还有一个 `subSchema` 实例，表示 [LDAPv3 RFC](http://www.ietf.org/rfc/rfc2254.txt) 中定义的抽象架构。

> **注意**：

第 5 章和第 17 章将更深入地讨论架构。

### 4.4. 应用程序分区( Application Partitions )

应用程序分区使管理员能够在 Active Directory 中创建区域，将数据存储在自行选择的特定域控制器( Domain Controller ,DC)上，而不是域或林中的每个 DC 上。您可以定义哪些域控制器保留每个应用程序分区的副本，这称为副本( Replica )。不受域或站点成员身份的限制，这意味着您可以将林内任何运行 Windows Server 2003 或更高版本的域控制器配置为保留任意应用程序分区副本。现有站点拓扑( Site Topology )将用于自动创建必要的连接对象( Connection Object )，以便在保留应用程序分区副本的服务器之间进行复制。域控制器还将注册必要的服务位置( Service Location ,SRV)记录（第8章中有更详细说明），以便客户端可以使用 DC 定位器进程为应用程序分区找到最佳域控制器，就像为域执行该操作一样。

关于应用程序分区，有几个限制需要注意：

- 应用程序分区不能包含安全主体( Security Principal )，最值得一提的是包括用户、`inetOrgPerson`、组和计算机对象。可以在应用程序分区中创建任何其他类型的对象。
- 应用程序分区中包含的任何对象都不会复制到全局编录( Global Catalog ,GC)。即使保留应用程序分区副本的域控制器同时也是全局编录服务器，该域控制器在全局编录搜索期间也不会返回应用程序分区中的任何对象。
- 应用程序分区中的对象不能移动到该分区之外。这与域中包含的对象不同，域中的对象可以在域之间移动。

应用程序分区的命名方式与域类似。例如，如果直接在 *mycorp.com* 域下创建名为“apps”的应用程序分区，则 DNS 名称为 *apps.mycorp.com*，可分辨名称( Distinguished Name ,DN)为 `dc=apps,dc=mycorp,dc=com`。应用程序分区可以根植于域下（如前一示例所示），也可以嵌套在其他应用程序分区下（例如 `dc=sales,dc=apps,dc=mycorp,dc=com`），或者成为新域树( Domain Tree )的一部分（例如 `dc=apps,dc=local`）。有关创建和管理应用程序分区的详细信息，请参阅侧栏。

创建应用程序分区

应用程序分区( Application Partition )通常使用 *ntdsutil* 实用工具进行管理。借助 *ntdsutil*，可以管理活动目录( Active Directory ,AD)和活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)中的应用程序分区。可执行的操作类型包括创建和删除新的应用程序分区，以及在应用程序分区的副本( Replica )列表中增加和移除域控制器( Domain Controller ,DC)与 AD LDS 实例。

在本示例中，我们将在 *cohovines.com* 域下创建一个名为 `MyPart` 的应用程序分区。该域处于 Windows Server 2008 功能级别( Functional Level )。我们将使该应用程序分区复制到域控制器 *dc01* 和 *dc02*。

以下是创建该应用程序分区所需的步骤：

1. 在命令提示符下，启动 *ntdsutil*。

2. 输入 **`partition management`** 进入分区管理模式。

3. 输入应用程序分区的可分辨名称( Distinguished Name ,DN)以及要在其上创建该分区的服务器：

   

   
```
   create nc "dc=MyAppPart,dc=cohovines,dc=com" dc01.cohovines.com
```


4. 输入 **`quit`** 退出 `partition management` 菜单，然后再次输入 **`quit`** 退出 *ntdsutil*。

以下是添加 *dc02* 副本的方法：

1. 在命令提示符下，启动 *ntdsutil*。

2. 输入 **`partition management`** 进入分区管理模式。

3. 输入 **`connections`** 转到 `connections` 子菜单。

4. 输入 **`connect to server dc02`**。必须始终连接到要添加副本的服务器。

5. 输入 **`quit`** 返回 `partition management` 菜单。

6. 输入以下命名上下文( Naming Context ,NC )副本命令，以将副本添加到 *dc02*：

   

   
```
   add nc replica "dc=MyAppPart,dc=cohovines,dc=com" dc02.cohovines.com
```


7. 输入 **`quit`** 退出 `partition management` 菜单，然后再次输入 **`quit`** 退出 *ntdsutil*。

在 Windows Server 2003 上，应将 *partition management* 命令替换为 *domain management* 命令。其余语法完全相同。

应用程序分区( Application Partition )通常用于存储动态数据,即生命周期有限的数据(有关此方面的更多内容,请参阅存储动态数据一节)。来自 DNS 和动态主机配置协议( Dynamic Host Configuration Protocol ,DHCP)等网络服务的动态数据可以驻留在活动目录( Active Directory ,AD)中的应用程序分区内。这样一来,应用程序便可通过单一方法实现统一的访问方式,进而使开发人员能够将数据写入仅在特定服务器上可用的专用区域,而不必写入会复制到每个域控制器( Domain Controller ,DC)的域分区。事实上,应用程序分区还能让多个版本的 COM+ 应用程序安装并配置在同一台计算机上,从而更经济高效地管理服务器应用程序。

活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)的出现,为管理员提供了另一种选择:在仍使用 Windows 安全机制和身份验证的前提下,将目录数据存储在常规域命名上下文之外。您可以将此类数据放入专用的 AD LDS 实例,而不必放入应用程序分区。这样,您既可将该信息的管理控制权下放给应用程序所有者或其他管理员,又能降低应用程序对域控制器主要网络操作系统( Network Operating System ,NOS)功能造成负面影响的可能性。我们将在第 20 章中详细讨论 AD LDS 的具体内容。

#### 存储动态数据

尽管应用程序分区( Application Partition )使管理员能够更好地控制应用程序数据的复制方式，但数据清理问题依然存在。也就是说，向 Active Directory 添加数据的应用程序，在数据不再需要时，并不总能妥善地将其清除。正因如此，创建动态数据的能力也作为 Windows Server 2003 Active Directory 的一项特性被引入。动态对象( Dynamic Object )是指具有生存时间( Time-to-Live ,TTL)值的对象，该值决定了它们在 Active Directory 自动删除之前能够存续多久。动态对象的生命周期通常相当短暂（即数天或更短）。动态对象的一个示例用法是电子商务网站需要临时存储用户会话信息。由于用户配置文件信息很可能就存放在目录中，因此将通常生命周期较短的基于会话的信息存储在同一存储中可能颇具优势。为动态对象设置的默认 TTL 为 1 天，但可以配置为短至 15 分钟。

> **注意**：

默认 TTL 和最小 TTL 可通过修改 `CN=``Directory``Service,``CN=WindowsNT,``CN=Services,``CN=Configuration,``DC=...` 对象的 `ms-DS-``Other-``Settings` 属性中的 `Dynamic``Object``Default``TTL``Seconds` 和 `Dynamic``Object``MinTTL``Seconds` 值来更改。

要创建动态对象，只需在创建对象时将 `dynamicObject` 添加到 `objectClass` 属性中即可。出于安全考虑，Microsoft 特意禁用了将其添加到现有对象的功能。这就是为什么你无法将现有静态对象转换为动态对象。还可以在创建时设置 `entryTTL` 属性，将 TTL 设置为除一天默认值之外的其他值。要防止动态对象被自动删除，可以通过将对象的 `entryTTL` 属性重置为新的 TTL 值（以秒为单位指定的时间）来“刷新”该对象。

> **警告**：

动态对象在被删除时不会像普通对象那样被标记为墓碑，它们只是从目录中被移除。由于 TTL 机制允许它们同时从所有域控制器( Domain Controller ,DC )中立即移除，因此无需墓碑。有关墓碑的更多信息，请参阅第 5 章中的在墓碑中保留属性一节。

### 4.5. 小结

本章介绍了如何在较高层面上将对象分组为命名上下文( Naming Context ,NC)和应用程序分区( Application Partition )，并将它们用作复制边界( Replication Boundary )。域 NC 包含特定于域的数据，例如用户、组和计算机。配置 NC 包含林范围的配置数据，例如站点拓扑( Site Topology )对象以及表示命名上下文和应用程序分区的对象。架构 NC 包含所有架构对象( Schema Object )，这些对象定义了数据在 Active Directory 中的结构化和表示方式。

应用程序分区为管理员提供了一种定义自己的对象分组以及后续复制边界的方式。由于应用程序分区能让您更好地控制哪些域控制器( Domain Controller ,DC )复制数据，AD 集成 DNS 区域( AD-integrated DNS Zone )的 DNS 数据存储是使用应用程序分区的经典示例。动态对象( Dynamic Object )允许您创建具有生存时间( Time To Live ,TTL)值的对象。TTL 过期后，Active Directory 会自动删除该对象。

---

## 第5章 Active Directory 架构( Schema )

schema是 Active Directory 中数据存储的蓝图。Active Directory 中的每个对象都是schema中某个类( Class )的实例。例如，用户对象作为 `user` 类的实例存在。属性( Attribute )定义了一个类（以及该类的实例）可以保存的信息片段。语法( Syntax )定义了可以放入属性中的数据类型。例如，如果某个属性定义为布尔( Boolean )语法，它可以存储 `True` 或 `False` 作为其值，或者可以为空值( Null )。空值具有特定于实现的含义；根据使用该值的应用程序，它可能表示 `True` 或 `False`。

Active Directory 在默认schema中包含许多属性和类，其中一些基于标准，另一些是 Microsoft 自己需要的。Active Directory 的每个新版本都包含对默认schema的更新。有关schema版本的背景信息，请参阅侧边栏 schema版本，接下来。此外，Active Directory schema被设计为可扩展的，以便管理员可以添加他们认为必要的类或属性。事实上，扩展schema并不是一项困难的任务；更困难的通常是设计您希望纳入的更改。schema设计问题在第17章中介绍。在本章中，我们只关注schema的基础知识。

schema版本

每当 Microsoft 发布对默认 Active Directory schema的更新时，它都会更新 Active Directory 中的 `schemaVersion` 属性。迄今为止，默认 Active Directory schema已经发布了四个版本，如表5-1所列。当管理员进行自己的自定义更改时，此版本号不会更新，因此虽然版本号从操作系统角度告诉您schema的最低级别，但它并不能证明是否还存在其他特定修改。

您可以使用 *adfind* 命令行工具轻松查询schema版本。使用以下命令执行此操作：

```
adfind -schema -s base objectVersion
```

表5-1. Active Directory 默认schema版本

| schema版本                                                   | 发布版本                                                     |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| 13                                                           | Windows 2000                                                 |
| 30                                                           | Windows Server 2003                                          |
| 31                                                           | Windows Server 2003 R2                                       |
| 39                                                           | Windows Server 2008 Beta schema[a] |
| 44                                                           | Windows Server 2008                                          |
| 47                                                           | Windows Server 2008 R2                                       |
| 56                                                           | Windows Server 2012                                          |
| [a] 有关此schema版本的更多信息，请参考[此链接](http://bit.ly/Y1K9kT)。 |                                                              |

### 5.1. 架构( Schema )的结构

schema容器位于活动目录( Active Directory ,AD)中的配置容器( Configuration container )下。例如，在 *contoso.com* 林( Forest )中，schema容器的可分辨名称( Distinguished Name ,DN)为 `cn=schema,cn=Configuration,dc=contoso,dc=com`。您可以通过将 ADSI Edit 或 LDP 等 AD 查看器指向该容器，直接查看其内容。您还可以使用 Active Directory schema MMC 管理单元，该管理单元将类和属性拆分到单独的容器中，以便于查看（实际上，所有schema对象都直接存储在schema容器中）。

> **注意**：

默认情况下，Active Directory schema( Schema ) MMC 管理单元并未完全启用。若要在域控制器( Domain Controller ,DC )上启用schema管理单元，必须首先注册其依赖的 DLL。为此，请运行以下命令：*regsvr32 schmmgmt.dll*。

schema本身由两种类型的 Active Directory 对象组成：类( Class )和属性( Attribute )。在 Active Directory 中，它们分别称为 `classSchema` (Class-Schema) 和 `attributeSchema` (Attribute-Schema) 对象。同一名称的两种不同形式源于以下事实：类的 `cn` (Common-Name) 属性包含类的带连字符的易读名称，而类的 `lDAPDisplayName` (LDAP-Display-Name) 属性包含使用 LDAP 或 ADSI 查询 Active Directory 时所用的串联字符串格式。在schema中，每个对象的 `lDAPDisplayName` 属性通常通过以下方式生成：将 Common-Name 中每个单词的首字母大写，然后移除连字符并将所有单词串联在一起。最后，将第一个字母改为小写。[1] 这样会生成像 `user` 这样的简单名称，以及更特殊的 `sAMAccountName` 和 `lDAPDisplayName`。从现在起，我们将使用更常见的 LDAP 显示名称格式。

每当需要在 Active Directory 中创建新类型的对象时，必须首先创建一个 `classSchema` 对象，定义对象的类及其包含的属性。一旦类被正确设计并添加到schema中，就可以在 Active Directory 中创建使用该类的对象。如果要添加的类将具有自定义属性，且这些属性在创建该类的新的实例时必须填充，则必须先定义 `attributeSchema` 对象。如果只是要向现有类添加新属性，则必须创建 `attributeSchema` 对象，并将该属性与要使用它的任何类相关联。

在深入探讨 Active Directory 类或属性的构成之前，我们需要解释所创建的每个类如何不仅在你的 Active Directory 基础schema中，而且在全球范围内都是唯一的。

#### X.500 与 OID 命名空间

活动目录( Active Directory ,AD)基于轻型目录访问协议( Lightweight Directory Access Protocol ,LDAP)，而 LDAP 最初基于国际标准化组织( International Organization for Standardization ,ISO)和国际电信联盟( International Telecommunication Union ,ITU)于 1988 年制定的 X.500 标准。要正确理解活动目录schema( schema )的工作原理，确实需要了解 X.500 的一些基础知识；接下来我们将逐一介绍。

X.500 标准规定，组织中的各个对象类( object classes )可以使用一种特殊的标识过程来唯一地定义。该过程必须能够考虑到类之间可以相互继承这一事实，以及世界上任何组织都可能需要定义并导出自己设计的类。

为此，X.500 标准定义了对象标识符( Object Identifier ,OID)，用于唯一标识每个schema对象。该 OID 由两部分组成：

- 第一部分指示在 X.500 树状结构中，包含该对象的分支的唯一路径。
- 第二部分唯一指示该分支中的对象。

OID 表示法对每个分支和对象使用整数，如下面的对象 OID 示例所示：




```
1.3.6.1.4.1.3385.12.497
```


这唯一引用了分支 1.3.6.1.4.1.3385.12 中的对象 497。分支 1.3.6.1.4.1.3385.12 包含在 OID 为 1.3.6.1.4.1.3385 的分支中，依此类推。

> **注意**：

对象标识符( Object Identifier ,OID)编号中的每个分支也都对应一个名称。这意味着，例如点分表示法 1.3.6.1.4.1 等价于 *iso.org.dod.internet.private.enterprise*。由于这些名称对使用 Active Directory 的我们并无实际意义，本书不涉及它们。

这种表示法沿用至今，并用于 Active Directory schema( Schema )。如果要创建schema对象，需要为你的组织获取一个唯一的 OID 分支。将其用作根，随后即可根据组织需要，在根下创建更多分支和叶节点。

互联网号码分配机构( Internet Assigned Numbers Authority ,IANA)维护主要的根分支集合，并将自身定义为“为互联网协议分配唯一参数值的中心协调机构”。IANA 对其使命的说明如下：

> IANA 由互联网协会( Internet Society ,ISOC)和联邦网络委员会( Federal Network Council ,FNC)特许成立，作为信息交换中心，负责分配和协调众多互联网协议参数的使用。由互联网工程任务组( Internet Engineering Task Force ,IETF)及其指导组( Internet Engineering Steering Group ,IESG)定义的互联网协议套件包含众多参数，例如互联网地址、域名、自治系统编号(用于某些路由协议)、协议号、端口号、管理信息库对象标识符(包括私有企业编号)以及许多其他参数。互联网社区对互联网协议的普遍使用，要求这些参数字段中使用的特定值必须唯一分配。IANA 的任务是按请求进行这些唯一分配，并维护当前已分配值的注册表。IANA 位于南加州大学( University of Southern California ,USC)的信息科学研究所( Information Sciences Institute ,ISI)，并由该研究所运营。

你可以在[此链接](http://www.iana.org/)找到 IANA 网站。

如有需要，你可以直接向 IANA 申请 OID 命名空间，即一个根 OID 编号，你可据此创建自己的分支。这些编号称为企业编号( Enterprise Numbers )。完整的企业编号列表可在 [iana.org](http://bit.ly/Z9H9pk) 找到。每次新增编号时，该编号列表都会更新。

在文件顶部可以看到,互联网号码分配机构( Internet Assigned Numbers Authority ,IANA)所使用的根节点为 1.3.6.1.4.1。继续向下浏览该列表,你会发现微软被分配到了这棵目录树中该部分的 311 分支,因此微软的对象标识符( Object Identifier ,OID)命名空间为 1.3.6.1.4.1.311。列表中每个编号旁边还附有联系人的电子邮件地址,因此你可以在该文件中搜索贵组织中已分配到编号的任何成员。凡是已经拥有 X.500 目录,或已开发简单网络管理协议( Simple Network Management Protocol ,SNMP)管理信息库( Management Information Base ,MIB)的大型组织,很可能都已获得了一个 OID。

> **注意**：

除了企业编号( Enterprise Number )之外,还可以购买特定国家/地区的对象标识符( Object Identifier ,OID)。组织的企业编号注册情况与该组织是否已获得可供使用的基于国家/地区的 OID 命名空间( OID namespace )无关。如果在企业编号列表中看不到该公司,不要被误导;该组织仍可能拥有一个编号。

例如,Microsoft 已获得企业编号 1.3.6.1.4.1.311,但其所有新的schema类( schema class )都使用以美国分配的 OID 命名空间 1.2.840.113556 作为根。1.2.840 部分专门分配给美国。换句话说,Microsoft 已获得两个可供使用的 OID 命名空间,但选择只使用美国分配的那个命名空间。

如果要获得企业编号,请填写 http://pen.iana.org/pen/PenApplication.page 处的在线表格。如果此 URL 发生变化,可以从 IANA 主网页导航到该表格。

Microsoft 过去曾根据请求向客户发放唯一的 OID 命名空间;但现在不再这样做。取而代之的是,Microsoft 提供一个脚本,每次运行时都会生成一个统计唯一的 OID 分支。此脚本可从 http://go.microsoft.com/fwlink/?LinkId=100725 获取。虽然该脚本是一种可行的解决方案,但最佳实践要求你获取全局唯一的 OID 命名空间,并改为从该命名空间颁发 OID。

一旦组织拥有 OID 命名空间,它就可以按所需方式在根下添加唯一的分支和叶节点。例如,可以决定根下不设任何分支,直接为根下的每个新对象分配从 1 开始的递增整数。或者,可以决定创建一系列从 1 开始的编号分支,每个分支对应某一组类或属性。因此,第三个分支下的第五个对象的 OID 将以 3.5 结尾。图 5-1 展示了一个组织决定如何构造其 OID 命名空间的示例场景。

> **警告**：

Active Directory schema中，OID 命名空间任意部分的取值范围均为 1 至 268,435,455，即从 2⁰ 到 2²⁸ – 1。

这一限制曾给澳大利亚一些公司的schema扩展带来麻烦。澳大利亚的 OID 为 1.2.36，根据澳大利亚标准文件 MP-75，各公司可以使用其澳大利亚公司编号( Australian Company Number ,ACN )（不含前导零）来构造自己的 OID，无需另行申请。但遗憾的是，ACN 是九位数字，因此很容易超出上述限制。




![Sample OID namespace organizational tree](./image/5.%20Active%20Directory%20Schema/httpatomoreillycomsourceoreillyimages1663359.webp)


图 5-1. OID 命名空间组织结构树示例

为了进一步说明这一点，我们来看几个直接取自 Active Directory schema的示例。如果打开“Active Directory schema”管理单元，就可以非常方便地查看schema类的 OID。浏览各个类时，打开 `printQueue` 类的属性页，会看到图 5-2所示的内容。可以看到，其唯一 OID 为 1.2.840.113556.1.5.23。这说明该编号是 Microsoft 对象类层次结构中已定义的一部分。




![printQueue schema class properties](./image/5.%20Active%20Directory%20Schema/httpatomoreillycomsourceoreillyimages1663360.webp)


图 5-2. printQueue schema类属性

图 5-3显示了 `organizationalPerson` 类的属性页。在这里可以看到，其唯一 OID 为 2.5.6.7，与前者截然不同，这是因为在最初的 X.500 标准中，定义了一组原始类。`organizationalPerson` 就是其中之一，而此处是该类的副本。Microsoft 将整套基础 X.500 类都包含在 Active Directory 中。



#### 说明

OID 编号方式与继承没有任何关系。以某种方式为一组对象编号，除了为你创建一个可供引用这些对象的结构之外，并无其他作用；它并不表示对象之间如何相互继承。

下面我们来剖析一个示例属性和类，看看它们包含哪些内容。掌握这些信息后，你就能了解创建新的schema对象时需要提供哪些内容。




![organizationalPerson schema class properties](./image/5.%20Active%20Directory%20Schema/httpatomoreillycomsourceoreillyimages1663361.webp)


图 5-3. organizationalPerson schema类属性

### 5.2. 属性（attributeSchema 对象）

类信息作为名为 `classSchema` 的类的实例存储在 Active Directory 中,同样,属性由名为 `attributeSchema` 的类的实例来表示。与所有对象一样,`attributeSchema` 类包含若干属性,在指定新实例时可以设置这些属性。`attributeSchema` 类从名为 `top` 的类继承属性。不过,`top` 的大多数属性在此并不相关。`attributeSchema` 类的所有属性均已在此[站点](http://bit.ly/Y1LQie)中记录。

#### 剖析一个 Active Directory 属性示例

`userPrincipalName`（UPN）属性用于用户对象（ User Object ）,以提供一种在整个林（ Forest ）内唯一标识每个用户的方法。如果用户愿意,还可以使用 UPN 登录到林内任意域中的工作站。事实上,UPN 属性可接受符合 RFC 2822（电子邮件）格式的有效地址,因此 *europe.contoso.com* 域中用户 *tpood* 的 UPN 可以是 *tpood@contoso.com* 或 *tpood@europe.contoso.com*,甚至可以是 *tpood@logon.local*。实际上,林内可以使用任何 UPN 后缀,例如 *@contoso.com*。唯一的要求是用户的 UPN 值在林内所有用户中必须唯一。

> **注意**：

Active Directory 在设置用户主体名称( User Principal Name ,UPN)时并不强制其唯一性。如果同一林( Forest )中的两个不同用户被分配了相同的 UPN，则两者都将无法使用该 UPN 登录。检测到重复 UPN 时，域控制器( Domain Controller ,DC)将记录一条来源为密钥分发中心( Key Distribution Center ,KDC)、事件 ID 为 11 的事件。许多大型组织会实施脚本或其他工具，定期扫描其目录以检查重复的 UPN。

若要剖析该属性，我们需要查明已为其设置哪些值。表 5-2 显示了为 `userPrincipalName` `attributeSchema` 实例设置的属性值的一个子集。



表 5-2. userPrincipalName 的属性



<!-- TRANSLATION FAILED: API 返回空内容 -->

| Attribute lDAPDisplayName       | Attribute syntax     | Attribute value                                              |
| ------------------------------- | -------------------- | ------------------------------------------------------------ |
| `adminDescription`              | `CASE_IGNORE_STRING` | `User-Principal-Name`                                        |
| `adminDisplayName`              | `CASE_IGNORE_STRING` | `User-Principal-Name`                                        |
| `attributeID`                   | `CASE_IGNORE_STRING` | `1.2.840.113556.1.4.656`                                     |
| `attributeSyntax`               | `CASE_IGNORE_STRING` | `2.5.5.12`                                                   |
| `cn`                            | `CASE_IGNORE_STRING` | `User-Principal-Name`                                        |
| `isMemberOfPartialAttributeSet` | `BOOLEAN`            | `True`                                                       |
| `isSingleValued`                | `BOOLEAN`            | `True`                                                       |
| `lDAPDisplayName`               | `CASE_IGNORE_STRING` | `userPrincipalName`                                          |
| `name`                          | `CASE_IGNORE_STRING` | `User-Principal-Name`                                        |
| `objectCategory`                | `DN_STRING`          | `cn``=``Attribute-Schema`, `cn``=``Schema`,`a``=``Configuration`, `dc``=``mycorp`,`dc``=``com` |
| `objectClass`                   | `CASE_IGNORE_STRING` | `top``;` `attributeSchema` (two values of a multivalued attribute) |
| `oMSyntax`                      | `INTEGER`            | `64`                                                         |
| `searchFlags`                   | `INTEGER`            | `1` (indexed)                                                |
| `showInAdvancedViewOnly`        | `BOOLEAN`            | `True`                                                       |
| `systemFlags`                   | `INTEGER`            | `18` (category 1 attribute, replicated to GC)                |
| `systemOnly`                    | `BOOLEAN`            | `False`                                                      |

我们可以看到，该属性的名称为 `User-Principal-Name`（`adminDescription, adminDisplayName, cn, name`），它是 `attributeSchema` 类的一个实例（`objectCategory` 和 `objectClass`），它同时从 `top` 和 `attributeSchema` 继承属性（`objectClass`），并且 UPN 属性不会在普通浏览中显示（`showInAdvancedViewOnly`）。

`userPrincipalName` 属性显示了以下内容：

- 它将存储在 GC 中（`isMemberOfPartialAttributeSet` 和 `systemFlags`）。
- 它将被索引（`searchFlags`）。
- 它的 OID 为 1.2.840.113556.1.4.656（`attributeID`）。
- 在使用 ADSI 绑定到它时，应使用 `userPrincipalName`（`lDAPDisplayName`）。
- 任何人都可以创建实例（`systemOnly`）。
- 它存储单值（`isSingleValued`）的 Unicode 字符串（`attributeSyntax` 和 `oMSyntax`）。

在图 5-4中，您可以看到 UPN 属性的许多值。我们通过选中或取消选中每个复选框来指示哪些属性已被更改。




![UserPrincipalName attribute settings](./image/5.%20Active%20Directory%20Schema/httpatomoreillycomsourceoreillyimages1663362.png.webp)


图 5-4. UserPrincipalName 属性设置

### 5.3. 属性特性

属性的若干特性对属性的使用和功能具有重大且多样的影响。在此，我们将对修改schema( Schema )时需要理解的几个属性提供更为详尽的信息。

#### 属性语法( Attribute Syntax )

属性的语法表示其可容纳的数据种类；有编程背景的人可能更熟悉“数据类型( data type )”这一说法。与属性( Attribute )和类( Class )不同，受支持的语法在活动目录( Active Directory ,AD )中并不表示为对象。相反，Microsoft 已将这些语法内部编码到 Active Directory 自身中。因此，在schema( Schema )中创建的任何新属性都必须使用预定义语法之一。

创建新属性时，必须指定其语法。要在全部 22 种语法中唯一标识某个语法，必须指定两项信息：该语法的对象标识符( Object Identifier ,OID )以及所谓的 *OM 语法( OM syntax )*。这对值必须一起设置，并与 表 5-3 正确关联。多个语法具有相同 OID 可能看起来很奇怪；因此，要唯一区分不同语法，还需要第二个标识符。这是因为 Microsoft 需要一些 X.500 未提供的语法。表 5-3 显示了 22 种扩展语法，包括每种语法的名称，并在括号中给出替代名称。

表 5-3. 语法定义

| 语法                                 | OID      | OM 语法 | 描述                                                         |
| ------------------------------------ | -------- | --------- | ------------------------------------------------------------ |
| 地址( Address )                      | 2.5.5.13 | 127       | 由系统内部使用。                                             |
| 布尔值( Boolean )                    | 2.5.5.8  | 1         | 真或假。                                                     |
| 不区分大小写的字符串( Case-Insensitive String ) | 2.5.5.4  | 20        | 不区分大写与小写的字符串。                                   |
| 区分大小写的字符串( Case-Sensitive String ) | 2.5.5.3  | 27        | 区分大写与小写的字符串。                                     |
| 可分辨名称( Distinguished Name ,DN)  | 2.5.5.1  | 127       | Active Directory 中对象的完全限定域名( Fully Qualified Domain Name ,FQDN)。 |
| DN-Binary                            | 2.5.5.7  | 127       | 包含二进制值和 DN 的八位字节字符串。格式:*B:<字符数>:<二进制值>:<对象 DN>*。 |
| DN-String                            | 2.5.5.14 | 127       | 包含字符串值和 DN 的八位字节字符串。格式:*S:<字符数>:<字符串值>:<对象 DN>*。 |
| 通用时间( Generalized-Time )         | 2.5.5.11 | 24        | ASN1.1 时间格式,例如 20040625234417.0Z。                     |
| 整数(枚举)( Integer (enumeration) )  | 2.5.5.9  | 10        | 32 位数字。                                                  |
| 整数( Integer )                      | 2.5.5.9  | 2         | 32 位数字。                                                  |
| 大整数( Large Integer )              | 2.5.5.16 | 65        | 64 位数字。                                                  |
| NT 安全描述符( NT Security Descriptor ) | 2.5.5.15 | 66        | 安全描述符( Security Descriptor ,SD)。                      |
| 数字字符串( Numeric String )         | 2.5.5.6  | 18        | 由数字构成的字符串。                                         |
| 对象标识符( Object ID )              | 2.5.5.2  | 6         | 一个 OID。                                                   |
| 八位字节字符串( Octet String )       | 2.5.5.10 | 4         | 字节字符串。                                                 |
| 可打印字符串( Print Case String ,IA5-String ) | 2.5.5.5  | 22        | 常规的可打印字符串。                                         |
| 可打印字符串( Print Case String ,Printable-String ) | 2.5.5.5  | 19        | 常规的可打印字符串。                                         |
| 副本链接( Replica-Link )             | 2.5.5.10 | 127       | 复制信息。                                                   |
| SID                                  | 2.5.5.17 | 4         | 安全标识符( Security Identifier ,SID)。                     |
| 未定义( Undefined )                  | 2.5.5.0  | 不适用    | 不是有效的语法。                                             |
| Unicode                              | 2.5.5.12 | 64        | 宽字符串。                                                   |
| UTC 时间( UTC-Time )                 | 2.5.5.11 | 23        | 自 1970 年 1 月 1 日以来经过的秒数。                         |

这些大多是标准编程类型。如果不确定使用哪种语法，可以查看一些现有的属性( attribute )，看看能否为要创建的属性找到合适的语法。例如，`userPrincipalName` 属性的 `attributeSyntax` 为 2.5.5.12，`oMSyntax` 为 64，因此它必须包含 Unicode 字符串。

#### systemFlags

`systemFlags` 属性是一个常被忽视但很重要的属性。它是一个位掩码( Bit Mask )，表示应如何处理该属性。有关位掩码的更多信息，请参见即将出现的边栏如何使用位掩码。每当微软更新目录服务二进制文件时，都可以定义新的位值。`systemFlags` 属性既配置在属性和类的schema( Schema )定义上，也配置在整个林( Forest )中的任何实例化对象上。这可能令人困惑，但该属性中的各个位可能表示不同的含义，具体取决于该属性所应用到的对象。表5-4仅列出了 `attributeSchema` 和 `classSchema` 对象上 `systemFlags` 的值。有效 `systemFlags` 设置的完整列表可在[此链接](http://bit.ly/Yu8rjU)获取。

表5-4. 类和属性对象的系统标志值

| 值 | 说明 |
| ----------------------- | ------------------------------------------------------------ |
| 1 (0x0001) | 属性( Attribute )不会被复制。 |
| 2 (0x0002) | 属性将复制到全局编录( Global Catalog ,GC)。此值应仅由 Microsoft 设置；请勿使用。而应使用 `isMemberOfPartialAttributeSet` 属性将属性添加到部分属性集( Partial Attribute Set ,PAS)。 |
| 4 (0x0004) | 该属性为构造属性，不会存储在数据库中。此值应仅由 Microsoft 设置；请勿使用。 |
| 16 (0x0010) | 类别 1 属性或类( Class )。类别 1 对象( Object )是随系统提供的基础架构( base schema )中包含的类和属性。注意：并非基础架构中的所有类和属性都标记为类别 1。 |
| 33554432 (0x02000000) | 删除对象时，不会将其移动到已删除对象容器( Deleted Objects container )。相反，墓碑( tombstone )仍保留在原始容器中。 |
| 134217728 (0x08000000) | schema对象不能重命名。 |
| 268435456 (0x10000000) | 对于配置分区( Configuration Partition )中的对象，如果设置了此标志( flag )，则可以有限制地移动对象；否则，无法移动对象。默认情况下，在配置分区下创建的新对象上不会设置此标志。此标志只能在创建对象期间设置。 |
| 536870912 (0x20000000) | 对于配置分区中的对象，如果设置了此标志，则可以移动对象；否则，无法移动对象。默认情况下，在配置分区下创建的新对象上不会设置此标志。此标志只能在创建对象期间设置。 |
| 1073741824 (0x40000000) | 对于配置分区中的对象，如果设置了此标志，则可以重命名对象；否则，无法重命名对象。默认情况下，在配置分区下创建的新对象上不会设置此标志。此标志只能在创建对象期间设置。 |
| 2147483648 (0x80000000) | 无法删除对象。 |

如何使用位掩码

掩码( Mask )是计算机科学中的一个基本概念，而最常见的掩码类型也许就是位掩码( bit mask )。Active Directory 中有相当多的属性实际上都是位掩码。位掩码是一系列二进制值，通常表示一组设置。位掩码可能会让管理员感到困惑，因为它们有时以十进制数字的形式显示，而实际数据却是一系列位(二进制数据)。

让我们来看下面的位掩码，它描述了一组非常有限的动物：

| 描述         | 存活 | 哺乳动物 | 鸟类 | 猫  | 狗  | 鹦鹉 | 老虎 | 猴子 |
| ---------------------- | ----- | ------ | ---- | ---- | ---- | ------ | ----- | ------ |
| 位编号             | 0     | 1      | 2    | 3    | 4    | 5      | 6     | 7      |
| 位                    | 0     | 1      | 0    | 0    | 0    | 0      | 0     | 1      |
| 十进制表示 | 1     | 2      | 4    | 8    | 16   | 32     | 64    | 128    |

在此例中，我们设置了必要的位，以描述一只当前未存活的猴子。该掩码的二进制表示为 `01000001`，十进制为 `130`(2 + 128)。每一位都表示动物的一种不同特征。为了完整描述这只猴子，需要设置两个位。

现在，如果这只猴子尚未进入生产流程，我们甚至可能不会有一个表示这种状态的猴子掩码；因此，一旦猴子出生，我们就需要更新掩码以反映其“存活”状态(亦即值为 1 的位)。为此，需要执行二进制 OR 运算，这相当于加法：




```
01000001 OR 10000000 = 11000001 (01000001 + 10000000)
```


可以使用 Windows 计算器中的科学型视图来执行二进制算术运算。新的十进制表示为 `131`。

这看起来可能很简单；然而，管理员在修改位掩码属性时，常常会犯一个错误：用另一个十进制值替换管理工具中显示的十进制值。这样做时，可能会无意中丢失或添加数据。例如，假设你正在更新猴子的掩码以表示其存活状态，却复制了一只存活鹦鹉的十进制值——你会将存活猴子的掩码替换为 `37`，这样就会把猴子描述成鹦鹉。

这里的寓意是：应始终将位掩码视为二进制数据，并据此进行修改。

##### 构造属性( Constructed Attributes )

大多数属性直接存储在 Active Directory 数据库中。构造属性则例外，它们由目录服务( Directory Service )处理，以提供特殊功能。这种功能涵盖的范围很广，从大致告知某容器类型对象下直接包含多少对象（`msDS-Approx-Immed-Subordinates`），到告知在给定对象下可实例化的对象类型（`possibleInferiors`），再到告知对给定对象拥有写入访问权限的属性（`allowedAttributesEffective`），以及许多其他内容。这些属性因其特殊性，有一些规则需要了解：

- 构造属性不会被复制。它们由每个目录实例分别构造。
- 构造属性不能用于服务器端排序( Server-Side Sorting )。
- 构造属性通常不能用于查询。`aNR` 属性在此是例外，因为它用于构造特殊的模糊名称解析( Ambiguous Name Resolution ,ANR )查询。ANR 在模糊名称解析一节中有所介绍。
- 在某些情况下，由于构造属性的计算开销，可能需要使用基本范围查询( Base Scope Query )来检索某些构造属性；例如，`tokenGroups` 只能通过基本范围查询返回。

##### 类别 1 对象( Category 1 Objects )

类别 1 对象是活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS )或 Active Directory 附带的属性和类的子集。它们使用特殊的位标志进行标记，以便 Microsoft 可以跟踪它们，并防止它们受到某些类型的修改。

#### schemaFlagsEx

`schemaFlagsEx` 属性自 Windows 2000 起便已存在，但直至 Windows Server 2008 才得以启用。该属性旨在容纳用于进一步定义属性特性的标志位。目前该位掩码中仅实现了一个标志，详情见表 5-5。

表 5-5. schemaFlagsEx 的值

| 位编号 | 值     | 描述                                                         |
| ------ | ------ | ------------------------------------------------------------ |
| 1      | 1 (0x1) | 将属性标记为关键属性。无论 `searchFlags` 属性第十位的值为何，关键属性均不可添加至过滤属性集中。 |

#### searchFlags

`searchFlags` 属性是另一个位掩码，它最广为人知的用途是控制索引，但其作用远不止于此。顾名思义，`searchFlags` 与 `systemFlags` 类似，都是一系列位，表示应如何处理属性。与 `systemFlags` 不同，`searchFlags` 仅在schema属性定义上设置。有关所有值，请参见 表 5-6。



表 5-6. SearchFlags 位

| 位编号 | 值 | 描述 |
| ---------- | ------------ | ------------------------------------------------------------ |
| 1          | 1 (0x0001)   | 为该属性创建索引。所有其他基于索引的标志都要求同时启用此标志。将链接属性标记为可索引不会产生任何效果。 |
| 2          | 2 (0x0002)   | 在每个容器中为该属性创建索引。这仅对单层 LDAP 查询有用。 |
| 3          | 4 (0x0004)   | 将属性添加到模糊名称解析( Ambiguous Name Resolution ,ANR)集。ANR 查询主要用于 Exchange 和其他通讯簿工具。ANR 属性必须已建立索引,并且必须采用 UNICODE 或 Teletex 字符串属性语法。将属性添加到此集可能会影响 Microsoft Exchange 的性能。 |
| 4          | 8 (0x0008)   | 在墓碑对象中保留此属性。此标志用于控制删除对象时保留哪些属性。 |
| 5          | 16 (0x0010)  | 复制对象时复制此值。此标志在 Active Directory 中不起任何作用;诸如 Active Directory 用户和计算机这类复制对象的工具,可以查看此标志来确定应复制哪些属性。 |
| 6          | 32 (0x0020)  | 创建元组索引。元组索引对中间搜索很有用。中间搜索的通配符位于搜索字符串的开头或中间。例如,中间搜索(`drink=*coke`)将匹配 Cherry Coke、Diet Coke 等。 |
| 7          | 64 (0x0040)  | 创建子树索引。此索引旨在提高虚拟列表视图( Virtual List View ,VLV)查询的性能。 |
| 8          | 128 (0x0080) | 将该属性标记为机密。只有对如此标记的属性同时拥有读取属性( Read Property )和控制访问( Control Access )权限的用户,才能查看它。 |
| 9          | 256 (0x0100) | 从不审核对此属性的更改。此标志是 Windows Server 2008 中的新增标志。审核相关内容参见第 16 章。 |
| 10         | 512 (0x0200) | 将此属性包含在只读域控制器( Read-Only Domain Controller ,RODC)筛选属性集中。RODC 和筛选属性集参见第 9 章。 |

##### 索引属性( Indexed Attributes )

属性索引( Attribute Indexing )可用于提升查询性能。当对属性编制索引时，其值会按排序顺序放入一个特殊表中，这样使用该属性的查询只需查看目录中所有信息的一个子集即可完成。所创建索引的类型可以通过在 `searchFlags` 属性中配置的其他位标志进行修改。关于索引，有几点需要了解：

- 对索引属性执行按位操作的查询会降低索引的效用。按位操作无法直接在索引表中查找，必须枚举并测试索引中的整个值集。按位查询是指查询位掩码的查询（例如 `systemFlags` 或 `userAccountControl` 属性）。

- 包含对索引属性进行逻辑非（NOT）的查询会使索引无法用于该部分查询。对属性进行逻辑非操作需要枚举搜索范围内的所有对象，以确定哪些对象不具有该属性，或者哪些对象应用了不允许受信者查看属性值的权限。

- 链接属性( Linked Attribute )是隐式索引的。如果修改该标志，由于隐式索引行为，将不会产生任何效果。

- 人们常认为，对于具有多值或非唯一值的属性，无法构建索引或索引无法很好地工作。这种观点是错误的。在最初的 Active Directory 测试版中，曾对多值和非唯一值存在顾虑，但围绕这些问题已经得到解决。这个话题最常针对 `objectClass` 属性提出，并被说成是 Microsoft 在 Windows Server 2008 之前默认不对该属性编制索引的原因。

  如果在林( Forest )中安装了 Exchange Server 2007 schema扩展( Schema Extension )，则 `objectClass` 会作为此schema扩展的一部分编制索引。

Windows Server 2008 及更高版本的域控制器( Domain Controller ,DC)会实现一种特殊行为：无论 Active Directory 中的 `searchFlags` 设置如何，默认都会为 `objectClass` 建立索引。请注意，这被视为一种特殊行为，因为一旦导入 Windows Server 2008 或更高版本的schema扩展( Schema Extension )，该属性在 Windows 2000 或 Windows Server 2003 域控制器上不会建立索引；但是，在任何更高版本的 DC 上，该属性都会建立索引。这可能会导致随机选择域控制器使用的应用程序出现性能差异。你可以考虑在应用 Windows Server 2008 或更高版本的schema更新时为 `objectClass` 建立索引，这样在引入更高版本的域控制器后，整个企业中就会获得一致的 LDAP 查询体验。

虽然为属性建立索引通常可以显著提高 LDAP 查询性能，但务必认识到索引也会占用磁盘空间。为目录对象中很大比例都填充了值的属性添加索引，可能会占用大量磁盘空间。

生成索引期间，域控制器性能也会受到影响。索引数据不会复制，因此林( Forest )中的每个域控制器在检测到必须创建新的属性索引时，都必须构建自己的索引副本。创建索引的速度取决于必须建立索引的数据量，以及域控制器运行所在的硬件。

Windows Server 2012 DC 支持*延迟索引( Deferred Indexing )*这一概念。启用延迟索引后，DC 不会立即开始索引生成过程，而是直到其重新启动或发出 `UpdateSchemaNow` LDAP 请求时才会生成索引。若要启用延迟索引，必须修改林的 `dsHeuristics` 值，使第 19 个字节等于 `1`。有关编辑 `dsHeuristics` 属性的更多信息，请参阅第 16 章。

##### 模糊名称解析( Ambiguous name resolution ,ANR )

*模糊名称解析*(ANR) 用于通讯簿查找。它允许将单个小型查询扩展为搜索管理员希望搜索的任意多个字段，这样用户只需输入一条信息，就有望找到与其感兴趣的值相关的所有可能“命中项”。当提交诸如 `(anr=Joe Richards)` 这样的 ANR 查询时，活动目录查询处理器( Active Directory Query Processor ) 会将这个简单筛选器扩展为更复杂的 OR 通配符筛选器，其中包含所有标记为 ANR 集的一部分的属性。在安装了 Exchange Server 2010 的 Windows Server 2012 Active Directory 上，指定的筛选器会将这个简单查询扩展为：




```
 (
 (|
   (displayName=joe richards*)
   (givenName=joe richards*)
   (legacyExchangeDN=joe richards)
   (msDS-AdditionalSamAccountName=joe richards*)
   (msDS-PhoneticCompanyName=joe richards*)
   (msDS-PhoneticDepartment=joe richards*)
   (msDS-PhoneticDisplayName=joe richards*)
   (msDS-PhoneticFirstName=joe richards*)
   (msDS-PhoneticLastName=joe richards*)
   (physicalDeliveryOfficeName=joe richards*)
   (proxyAddresses=joe richards*)
   (name=joe richards*)
   (sAMAccountName=joe richards*)
   (sn=joe richards*)
   (&
     (givenName=joe*)
     (sn=richards*)
   )
   (&
     (givenName=richards*)
     (sn=joe*)
   )
 )
 )
```


如你所见，一个非常简单的查询可以迅速扩展成一个非常大的查询。因此，应避免添加额外的 ANR 属性。



##### 在墓碑( tombstone )中保留属性

对象被删除（亦称*墓碑化*( tombstoned )）时保留的属性，是通过 `searchFlags` 设置与一些硬编码的内部功能共同配置的。*保留在墓碑中*( preserve on tombstone ) 的 `searchFlags` 设置可由管理员配置，因此他们可以选择向墓碑对象上保留的内容中添加更多属性。允许目录在墓碑对象上保留的属性越多，在对象重新激活后必须通过其他方式恢复的属性就越少。但是，如果你的林启用了活动目录回收站( Active Directory Recycle Bin )，则在墓碑上保留额外值就没有意义，因为一旦启用回收站，就无法重新激活墓碑。

遗憾的是，即使设置了正确的 `searchFlags` 位，也并非所有属性都能成功添加到墓碑中。最明显的例子是链接属性( linked attributes )，例如组成员身份。目录对链接属性的处理方式不同，因此无法强制保留它们。如果将链接属性配置为要保留，Active Directory 将直接忽略该设置。

有关墓碑和活动目录回收站的详细信息，请参阅第 18 章。

##### 子树索引( Subtree Index )

创建此索引可以显著提高使用特定属性作为排序键的任何虚拟列表视图( Virtual List View ,VLV )操作的效率。它还能防止一个常见故障，该故障会导致 VLV 查询在较大的目录中因“关键扩展不可用”错误而终止。默认情况下，处理 VLV 查询时，目录会执行查询并将结果集存储在一个称为“临时表”的特殊内部表中，以便进行排序。该表的大小可变，但不得超过默认查询策略中`MaxTempTableSize`设置所指定的值。默认情况下，该设置的值为10,000条记录。如果查询结果集超出当前临时表的大小，您将收到“关键扩展不可用”错误，而不是结果。启用子树容器索引可使 AD 避免使用临时表，从而显著提高性能并避免超出临时表大小的问题。

##### 元组索引( Tuple Index )

创建索引时，它会针对直接查找以及(如果属性语法支持)尾部通配符(例如`(name=joe*)`)进行优化。如果使用中间查询——即在字符串末尾以外的任何位置使用通配符的查询，例如`(name=*oe)`——性能往往不太理想。通常情况下，这没有问题，但在某些重要应用程序因中间查询性能不佳而受到严重影响的情况下，您可以考虑为该属性启用元组索引。这与启用普通索引类似；您只需在属性的`searchFlags`掩码上启用另一位，以指定应创建元组索引。

元组索引被视为一种开销较大的索引，它会使 Active Directory 数据库( *ntds.dit* )的大小比“普通”索引增加更多。此外，新属性插入性能也会受到轻微影响。对于单个属性插入，这种性能影响不会很明显，但如果一次性更新大量属性，性能影响可能会更加明显。

##### 机密性

Windows Server 2003 Service Pack 1 为 `searchFlags` 属性定义了一个新位：机密属性( Confidential Attribute )标志。任何启用了此标志的属性，若要由受信者( Trustee )查看，都需要两项权限（*受信者*是被授予权限的安全主体( Security Principal )）：受信者需要对该属性具有读取属性( Read Property )和控制访问( Control Access )权限。此功能主要用于保护敏感的用户属性，例如社会安全号码( Social Security Number ,SSN)和其他个人信息。默认情况下，只有管理员( Administrators )和帐户操作员( Account Operators )对所有用户对象拥有完全控制权限，这意味着他们能够查看任何机密属性。任何其他对用户对象拥有完全控制权限的人也将能够查看机密数据，因此，这是不应在目录中授予不必要权限的又一个原因。如果域中的域控制器( Domain Controller ,DC )（或者林中的全局编录( Global Catalog ,GC )，如果你处理的是部分属性集( Partial Attribute Set ,PAS )中的属性）未运行 Windows Server 2003 Service Pack 1 或更高版本，那么任何标记为机密的属性在这些域控制器或全局编录上仍可在没有特殊访问权限的情况下查看。

机密属性功能是作为针对 Active Directory 当前安全模型中存在的问题的一种变通方法而添加的。遗憾的是，Active Directory 中的对象上存在大量显式的读取属性授予权限，这些权限极难覆盖。借助这个新标志，即使存在所有默认授予权限，你也可以介入并快速拒绝对某个属性的访问。

这项新功能在 Active Directory 社区中受到热烈欢迎，直到管理员开始意识到，Microsoft 有意限制了该功能的适用范围，不允许将类别 1 属性( Category 1 Attribute )设置为机密。类别 1 属性是默认 AD schema( Schema )中定义的许多属性，而该属性列表中包含许多你可能希望设为机密的属性，例如电话号码、地址、员工 ID 等。其意图似乎只是为 AD 管理员提供一种方法，以便更好地保护他们通过schema扩展( Schema Extension )添加到目录中的自定义属性。对于坚持使用默认schema的公司来说，这一限制极大地降低了此功能的实用性。

> **警告**：

严禁修改 `searchFlags` 以在 Category 1 属性上启用机密性。如果尝试更改这些属性之一的 `searchFlags` 以设置机密标志，将收到错误消息。

所有活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS) 基本schema对象上的默认安全描述符配置为没有显式访问控制项( Access Control Entries ,ACEs)。结果是，在对象实例化时，对象上几乎没有显式的读取属性( Read Property ) 授予权限，这意味着您可以更轻松地使用继承的拒绝权限来保护属性，而无需依赖机密属性功能。

接下来，我们需要讨论 Microsoft 从 Windows Server 2003 Service Pack 1 开始提供的用于管理对机密属性访问的工具。答案很简单：*无*。为了授予受信者查看对象上特定机密属性的能力，需要将具有针对该特定属性的控制访问( Control Access ) 权限的授予 ACE 添加到对象的访问控制列表( Access Control List ,ACL) 中。

可用于分配权限的图形用户界面( Graphical User Interface ,GUI) 工具不仅无法分配此类型的权限，而且即使其他工具授予了该权限，它们也无法显示该权限。命令行工具 *dsacls.exe* 只是稍好一些；它可以显示权限，但无法授予权限。GUI 和 *dsacls.exe* 工具能做到的最好的事情是为对象分配完全控制，或者为对象分配 *所有* 控制访问权限，但如果您希望仅授予完成工作所需的最小权限，那么这两种方法都不是最佳选择。

Windows Server 2008（及更高版本）的远程服务器管理工具( Remote Server Administration Tools ,RSAT) 附带的 LDP 版本能够正确修改 ACL，是管理对机密属性访问的最佳方式。即使您的林未运行 Windows Server 2008 或更高版本，您也可以使用此版本的 LDP。有关修改对象 ACL 的详细信息，请参阅 第 16 章。

##### 属性更改审核

从 Windows Server 2008 开始,相较于其早期版本,审核基础结构已进行了大幅更新。在 Windows 2000 和 Windows Server 2003 中,只有一项域范围的目录服务审核设置,称为“审核目录服务访问”。启用此设置后,所有目录服务审核事件都将被启用。在繁忙环境中,这样做的后果是事件日志中产生大量安全审核流量,以至于很容易变得难以管理,因此启用该设置并不切实际。

Windows Server 2008 及更高版本的域控制器( Domain Controller ,DC)将目录服务审核划分为四个子类别:

- 目录服务访问( Directory Service Access )
- 目录服务更改( Directory Service Changes )
- 目录服务复制( Directory Service Replication )
- 详细目录服务复制( Detailed Directory Service Replication )

我们目前特别关注的是目录服务更改子类别。我们将在第 16 章中更详细地讨论新的审核基础结构。

默认情况下,所有属性更改都会继续按*系统访问控制列表*( System Access Control List ,SACL)的要求接受审核。不过,为控制噪音,您可以在属性的 `searchFlags` 掩码上设置位 9,以禁用该属性的所有更改审核。Windows Server 2008 GUI 工具并未提供一种便于设置此位的交互式方法。有关设置此位的说明,请参阅紧接着的侧栏。

控制属性更改审核

若不手动执行二进制运算,GUI 工具并未提供控制属性 `searchFlags` 掩码中位 9 的简便机制。幸运的是,通过组合使用 *adfind* 和 *admod* 工具,即可轻松实现此更改。

在下面的示例中,我们将禁用 `description` 属性的更改审核:




```
adfind -sc s:description searchFlags -adcsv | admod -safety 1 -expand
searchFlags::{{searchFlags:SET:0x0100}}
```


在下面的示例中,我们将启用 `description` 属性的更改审核:




```
adfind -sc s:description searchFlags -adcsv | admod -safety 1 -expand
searchFlags::{{searchFlags:CLR:0x0100}}
```


请注意,您可以将此模式用于切换 Active Directory 中的任意位掩码标志。

##### 筛选属性集( Filtered Attribute Set )

筛选属性集是 Windows Server 2008 Active Directory 中新增的只读域控制器( Read-Only Domain Controller ,RODC )功能的一部分。RODC 可以配置为不复制 Active Directory schema( Schema )中的某些属性。第 9 章对 RODC 进行了深入讨论;不过,我们将在此处结合筛选属性集简要讨论 RODC。

RODC 的设计理念是:默认情况下,运行 RODC 的服务器被视为已遭入侵。因此,有些属性我们可能不希望存储在 RODC 上,因为它们可能包含敏感信息。例如,包含应用程序特定机密的schema扩展、社会安全号码等机密数据,等等。

你可以应用侧栏控制属性更改审核中所示的过程,以控制属性是否包含在筛选属性集中。应切换位 `0x200`,而不是位 `0x100`。

> **警告**：

不能将 `schemaFlagsEx` 属性中定义为关键属性的特性包含在筛选属性集中。

#### 属性集与 attributeSecurityGUID

属性集( Property Set )将在第 16 章讨论 Active Directory 安全性时介绍。这里之所以提及,是因为属性集的创建、修改和标识都涉及schema分区( Schema Partition )。属性集的部分信息保存在配置容器( Configuration Container )的 `cn=extended-rights` 子容器中,其余信息则保存在schema中。

属性集在 `cn=extended-rights` 子容器中定义为 `controlAccessRight` 对象。`controlAccessRight` 对象有两个属性将其与schema关联起来。第一个是 `appliesTo` 属性,第二个是 `rightsGuid`。`appliesTo` 属性是属性集所适用的 `classSchema` 对象的 `schemaIDGUID` 属性的字符串表示形式。`rightsGuid` 则是标记在 `attributeSchema` 对象的 `attributeSecurityGUID` 属性上的二进制 GUID 的字符串表示形式,用于将这些对象标识为该属性集的成员。

#### 链接属性

Microsoft 允许将具有 `attributeSyntax` 值为 `2.5.5.1`、`2.5.5.7` 和 `2.5.5.14` 的可分辨名称属性链接到具有 `attributeSyntax` 值为 `2.5.5.1` 的属性。这些被称为*链接属性*，由正向链接和反向链接组成。一对链接属性的示例是 `member` 和 `memberOf`。

属性通过将两个 `attributeSchema` 对象的 `linkID` 属性设置为有效的链接值来进行链接。这些值对于所有 `attributeSchema` 对象必须是唯一的。正向链接的值是正偶数值，而反向链接的值是正向 `linkID` 值加一，使其成为正奇数值。属性在schema中首次定义时必须进行链接。

只要生成的 `linkID` 对是唯一的，您可以使用任何随机的 `linkID` 值；但是，*强烈* 建议您自动生成链接 ID。如果您需要schema扩展支持 Windows 2000，则不能使用自动生成的链接 ID。如果您需要支持 Windows 2000，应发送电子邮件至 [schemreg@microsoft.com](mailto:schemreg@microsoft.com) 请求唯一的链接 ID。

为了自动生成链接 ID 对，您必须遵循以下四个步骤：

1. 创建正向链接属性，并将 `linkID` 属性填充为值 `1.2.840.113556.1.2.50`。
2. 重新加载schema缓存。
3. 创建反向链接属性，并将 `linkID` 属性填充为在步骤 1 中创建的正向链接属性的 `lDAPDisplayName`。
4. 重新加载schema缓存。

#### MAPI 标识符( MAPI ID )

在 Exchange 全局地址列表( Global Address List ,GAL)中显示的任何属性( Attribute )都必须具有在 Active Directory 中定义的 MAPI ID。为属性定义 MAPI ID 后（方法是将其存储在 `attributeSchema` 对象的 `mAPIId` 属性中），Exchange 管理员便可以使用详细信息模板编辑器( Details Template Editor )（如图 5-5 所示）将该属性添加到通讯簿。MAPI ID 的缺点在于没有负责颁发 MAPI ID 的中央机构，因此可能会出现冲突。幸运的是，如果schema主机( Schema Master )运行的是 Windows Server 2008 或更高版本，则 AD 在创建新属性时可以自动生成 MAPI ID。若要利用自动生成 MAPI ID 的功能，请按以下步骤操作：

1. 创建新属性，并将 `mAPIId` 属性的值设置为 `1.2.840.113556.1.2.49`。
2. 重新加载schema缓存。

AD 将在 `61,440` 和 `65,520` 之间分配下一个可用的 MAPI ID。

![The details Template Editor](./image/5.%20Active%20Directory%20Schema/httpatomoreillycomsourceoreillyimages1663363.png.webp)

图 5-5. 详细信息模板编辑器

> **注意**：

如果尝试创建新属性并显式指定保留范围 `61,440` 到 `65,520` 内的 MAPI ID，则 AD 将返回“Will not perform”错误。

### 5.4. 类( classSchema 对象)

schema类( Schema Class )定义为 `classSchema` 类的实例。`classSchema` 类属性的完整列表可通过[此链接](http://bit.ly/11l2Y1u)获取。

#### 对象类类别( Object Class Category )与继承

类( Class )的特殊之处在于可以相互继承。例如，假设我们希望在schema( Schema )中存储两种新类型的对象，分别表示营销用户和财务用户。这两个用户都需要现有 `user` 类的所有属性( Attribute )作为基础。不过，财务用户需要三个特殊属性，而营销用户需要七个。两个用户所需的额外属性没有任何共同之处。在此示例中，我们可以创建一个 `marketing-user` 类、一个 `finance-user` 类以及 10 个各不相同的新属性。但是，不必逐个指定 `marketing-user` 和 `finance-user` 类拥有原始 `user` 类的每个属性，我们只需将每个新类的 `subClassOf` 属性设置为 `user`，以指定这些新类继承自 `user` 类。这样，两个新类都会继承 `user` 类拥有的每一个属性。然后，我们可以向每个类添加额外的属性，从而得到两个新类。此示例概述见图 5-6。

![Marketing and finance subclasses](./image/5.%20Active%20Directory%20Schema/httpatomoreillycomsourceoreillyimages1663364.webp)

图 5-6. 营销和财务子类

你可以将 Active Directory schema视为树状结构：多个类从顶部的一个基类向下分支或继承，而该基类具有所有对象一开始就需要的属性。不出所料，这个类称为 `top`，最初定义在 X.500 规范中。有些类直接继承自 `top`，而另一些类则位于树中更靠下的位置。在这种布局中，每个类可能只有一个父类，但每个类也可以从其他类继承属性。之所以可行，是因为可以创建三类 `classSchema` 对象，也称为 `objectClassCategory`：

- **结构型( Structural )**

  如果某个类为结构型，则可直接在 Active Directory 中创建其类型的对象。`user` 类和 `group` 类是结构型类的示例。

- **抽象型( Abstract )**

您可能需要创建一个继承自其他类并具有特定属性的类，但您永远不需要直接创建该类的实例。这种类称为*抽象*类( abstract class )。抽象类可以继承自其他类，并且可以直接在其上定义属性。抽象类与结构类( structural class )的唯一区别在于，无法在 Active Directory 中创建抽象类的实例对象。如果您熟悉面向对象编程语言，那么 Active Directory 中的抽象schema类( abstract schema class )类似于编程语言中的抽象类。

- **辅助类( auxiliary class )**

  辅助类用于存储其他类可以继承的属性集。辅助类是一种让结构类和抽象类继承属性集合的方式，这些属性不必直接在类自身内部定义。辅助类主要是一种分组机制。

X.500 规范指出，辅助类不能从结构类继承，而抽象类只能从另一个抽象类继承。

> **注意**：

为符合 X.500 标准，`objectClassCategory` 实际上有四种类型。虽然 1993 年的 X.500 规范要求将对象归类为结构类( structural )、抽象类( abstract )或辅助类( auxiliary )之一，但 1993 年之前使用 1988 版规范定义的对象不必遵循这些类别。此类对象没有对应的 1993 类别，因此在schema( Schema )中定义为具有一种称为 *88-Class* 的特殊类别。

我们来看一下用于在 Active Directory 中创建用户和计算机账户的 `user` 类和 `computer` 类。`computer` 类和 `user` 类都是结构类，这意味着你可以直接在 Active Directory 中实例化这些类的对象。`computer` 类继承自 `user` 类，因此在某种意义上，`computer` 类是一种特殊类型的用户。`user` 类继承自 `organizationalPerson` 这一 Type-88 类。这意味着 `computer` 类对象可用的全部属性不仅包括在 `computer` 和 `user` 类自身上专门定义的属性，还包括从 `organizationalPerson` 类继承的所有属性。`organizationalPerson` 类是 `person` 抽象类的子类，而 `person` 抽象类又是抽象 `top` 类的子类。回想一下，`top` 之上没有类；它是根类。此关系概述见图 5-7。

Microsoft 需要在 Active Directory 中定义的 `user` 类，不能仅仅是 X.500 标准各部分的总和。毕竟，Microsoft 使用安全标识符( Security Identifier ,SID )来标识用户，而最初的 X.500 标准并不包含这些内容。因此，为了扩展构成用户的属性，Microsoft 定义了一些辅助类，并将其纳入 `user` 类的组成中。这些辅助类包括 `mailRecipient`、`securityPrincipal`、`posixAccount` 和 `shadowAccount`。`mailRecipient` 是一组属性，允许用户对象保存与该用户关联的电子邮件地址和邮件账户相关信息。类似地，`securityPrincipal` 类保存 Microsoft 所需的 SID 以及其他与用户相关的安全属性。`shadowAccount` 和 `posixAccount` 辅助类是在 Windows Server 2003 R2 中添加的，用于支持 Microsoft Services for UNIX (SFU)。

如果使用 ADSI Edit 之类的工具，就能相当清晰地看到继承关系和类关系。例如，查看任一用户对象的 `objectClass` 属性，会发现该属性中至少包含 `top`、`person`、`organizationalPerson` 和 `user` 这几个值。换句话说，该属性表明每个用户对象都从上述所有类继承属性。同样，对于任一计算机对象，其 `objectClass` 属性包含 `top`、`person`、`organizationalPerson`、`user` 和 `computer`。如果在schema( Schema )中查看 `computer` 类对象自身的 `subclassOf` 属性，会看到 `user` 类。而 `user` 类的 `subClassOf` 属性又指向 `organizationalPerson`，依此类推。这种关系如图 5-7 所示。




![Inheritance relationships](./image/5.%20Active%20Directory%20Schema/httpatomoreillycomsourceoreillyimages1663365.webp)


图 5-7. 继承关系

#### 剖析一个 Active Directory 类示例

下面我们进一步深入剖析一下 `user` 类。借助 ADSI Edit 之类的工具,我们可以查看 `user` 类 `classSchema` 对象各个属性的值。表 5-7列出了其中部分属性及其值。



表 5-7. `user` 类部分属性及值列表

| 用户属性的 LDAP 显示名称( LDAP-Display-Name ) | 用户属性的语法( Syntax ) | 用户属性中包含的值 |
| ---------------------------------- | ----------------------- | ------------------------------------------------------------ |
| `adminDescription`                 | `CASE_IGNORE_STRING`    | `User`                                                       |
| `adminDisplayName`                 | `CASE_IGNORE_STRING`    | `User`                                                       |
| `auxiliaryClass`                   | `CASE_IGNORE_STRING`    | `posixAccount shadowAccount`                                 |
| `cn`                               | `CASE_IGNORE_STRING`    | `User`                                                       |
| `defaultHidingValue`               | `BOOLEAN`               | `False`                                                      |
| `defaultSecurityDescriptor`        | `CASE_IGNORE_STRING`    | 默认安全描述符( Security Descriptor )的 SDDL 文本编码表示       |
| `governsID`                        | `CASE_IGNORE_STRING`    | `1.2.840.113556.1.5.9`                                       |
| `lDAPDisplayName`                  | `CASE_IGNORE_STRING`    | `user`                                                       |
| `name`                             | `CASE_IGNORE_STRING`    | `User`                                                       |
| `nTSecurityDescriptor`             | `SECURITY_DESCRIPTOR`   | 该类安全描述符的二进制表示                                     |
| `objectCategory`                   | `DN_STRING`             | `cn``=``Class-Schema`,`cn``=``Schema`,`cn``=``Configuration`, `dc``=``mycorp`,`dc``=``com` |
| `objectClass`                      | `CASE_IGNORE_STRING`    | `top; classSchema`(多值属性的两个值)                          |
| `objectClassCategory`              | `INTEGER`               | `1`                                                          |
| `rDNAttID`                         | `CASE_IGNORE_STRING`    | `cn`                                                         |
| `schemaIDGUID`                     | `OCTET_STRING`          | 唯一标识此类的 GUID                                            |
| `showInAdvancedViewOnly`           | `BOOLEAN`               | `True`                                                       |
| `subClassOf`                       | `CASE_IGNORE_STRING`    | `organizationalPerson`                                       |
| `systemAuxiliaryClass`             | `CASE_IGNORE_STRING`    | `securityPrincipal mailRecipient`                            |
| `systemMayContain`                 | `CASE_IGNORE_STRING`    | 各种属性(参见相关讨论)                                        |
| `systemPossSuperiors`              | `CASE_IGNORE_STRING`    | `builtinDomain organizationalUnit domainDNS`                 |

通过检查以下属性值，可以了解 `user` 类的以下信息：

- 类名称为 `User`（`adminDescription`、`adminDisplayName`、`cn`、`name`）。
- 它是 `classSchema` 类的实例（`objectCategory` 和 `objectClass`）。
- 它从 `top` 和 `classSchema` 两者继承属性（`objectClass`）。
- 此对象类( object class )具有一个安全描述符( security descriptor )，用于控制谁可以访问和操作它（`nTSecurityDescriptor`）。
- 如果创建时未指定默认安全描述符，则应对 `user` 类的新实例应用默认安全描述符（`defaultSecurityDescriptor`）。
- `user` 类的实例在正常浏览中可见（`defaultHiding``Value`）。
- `user` 类本身不会从常规浏览中隐藏（`showInAdvancedView``Only`）。
- `user` 类具有对象标识符( Object Identifier ,OID ) 1.2.840.113556.1.5.9（`governsID`）。
- 它不仅从 `top` 和 `classSchema` 继承属性，还从 `security-Principal` 和 `mailRecipient` 继承属性（`objectClass` 和 `systemAuxiliaryClass`）。
- `shadowAccount` 和 `posixAccount` 辅助类( auxiliary class )可以与用户对象关联。
- `user` 类是 `organizationalPerson` 类的直接子类( subclass )（`subClassOf`）。
- 通过轻量目录访问协议( Lightweight Directory Access Protocol ,LDAP )连接到该类的实例时，应使用的两字母前缀为 `cn`（`rDNAttID`）。
- 在 Active Directory 中，此类只能直接创建在三种不同的父对象( parent )下（`systemPossSuperiors`）。
- 该类是结构类( structural )（`objectClassCategory`）。
- `user` 类的实例可以为其大量属性设置值（`systemMayContain`）。

##### 继承如何影响 mustContain、mayContain、possSuperiors 和 auxiliaryClass

让我们来看看 `mustContain`、`mayContain`、`auxiliaryClass`、`possSuperiors` 及其系统属性对。可以看到，仅设置了 `systemPossSuperiors`、`systemMayContain` 和 `systemAuxiliaryClass` 这三个值。这些值是在最初创建 `user` 类时设置的，并且无法更改。由于 `systemMustContain` 属性未列出，可以判断在创建原始类时没有设置任何强制属性。如果之后希望向 `user` 类添加一组额外属性或一个新的可选属性，可以使用 `auxiliaryClass` 或 `mayContain` 来修改基础定义。例如，在林中安装 Exchange schema更新时就可能出现这种情况。如果这样做，`user` 类将被直接修改，在 `auxiliaryClass` 属性中包含以下三个与 Exchange 相关的辅助类：

- `msExchMailStorage`
- `msExchCustomAttributes`
- `msExchCertificateInformation`

创建新用户时所需的属性并未列在 `mustContain` 属性中。这是因为 `objectSID`、`sAMAccountName` 及其他属性是从构成该类的其他类继承而来的。`mustContain` 属性可以直接在 `auxiliaryClass` 或 `systemAuxiliaryClass` 中定义，也可以在其继承树中更高层的类上定义。例如，`sAMAccountName` 和 `objectSID` 都定义在 `securityPrincipal` 类上。

> **警告**：

不要将类必须包含的属性与在对象实例化时必须显式设置的属性混为一谈。遗憾的是,无法通过编程方式有效确定在创建类的实例时需要在对象上设置哪些属性。对象必须包含的某些属性由系统拥有,只能由系统设置;其他属性是可选的,并将自动填充;最后,某些属性实际上需要由对象创建者指定。更令人困惑的是,操作系统( Operating System ,OS)或活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS)的不同版本会改变这些要求。

同样的原则也适用于 `mayContain` 属性。类可能包含的完整属性集,只有在沿树向上递归并标识出所有继承类上的全部继承 `mayContain` 属性时,才能获得。

另一方面,`possSuperiors` 属性只能由直接在该类上定义的项、在该类的 `subClassOf` 属性中标识的类上定义的项,或在该类的 `subClassOf` 属性中沿 `subClassOf` 树继续向上标识的其他类上定义的项组成。如果这太令人困惑,可以这样理解:`user` 类的实例可以具有来自其自身的 `possSuperiors`,来自 `subClassOf` 属性中定义的 `organizationalPerson` 类,来自 `person` 类(`organizationalPerson` 类的 `subClassOf` 属性中标识),以及来自 `top`(`person` 类的 `subClassOf` 属性中标识)。

##### 使用 Active Directory 架构管理单元( Active Directory Schema snap-in )查看 user 类

请查看图 5-8。该图显示了使用 Active Directory 架构管理单元查看的 `user` 类。你可以看到相关的常规用户数据。

![User class schema entry general settings](./image/5.%20Active%20Directory%20Schema/httpatomoreillycomsourceoreillyimages1663366.webp)

图 5-8. user 类架构条目常规设置

请注意，`user` 类的许多内容在初始配置后无法配置，包括：

- `governsID`
- `subClassOf`
- `schemaIDGUID`
- `systemMustContain`
- `rDNAttID`
- `systemPossSuperiors`
- `objectClassCategory`
- `systemMayContain`
- `systemOnly`
- `systemAuxiliaryClass`
- `objectClass`
- `subClassOf`

若要查看所谓的关系设置( relationship settings )（`subClassOf`、`auxiliaryClass`、`possSuperiors`、`systemAuxiliaryClass`、`systemPossSuperiors`），请参阅图 5-9。在此屏幕中，可以看到此架构中的 `user` 类从五个辅助类( auxiliary classes )继承属性。

![User class schema entry relationship settings](./image/5.%20Active%20Directory%20Schema/httpatomoreillycomsourceoreillyimages1663367.webp)

图 5-9. user 类架构条目的关系设置

这里我们关注的第三个也是最后一个屏幕是 `user` 类的“属性”选项卡( Attributes tab )，如图 5-10 所示。其中显示了 `user` 类的 `mustContain`、`systemMustContain`、`mayContain` 和 `systemMayContain` 属性。

> **注意**：

您还可以通过浏览 Active Directory 架构 MMC 管理单元左侧树中的类( class )，来查看附加到该类的属性( attribute )。该类的所有属性都将列在右侧的主窗格中。

#### 动态链接辅助类( Dynamically Linked Auxiliary Classes )

动态地将辅助类分配给单个对象( object )，而不是分配给架构( schema )中某一整类对象，这是许多 LDAP 目录中常见的一项功能。动态辅助类机制为应用程序开发人员提供了更大的灵活性，他们可能希望利用现有的结构类( structural class )和辅助类，但又不想扩展架构来定义此类关系。

![User class schema entry attribute settings](./image/5.%20Active%20Directory%20Schema/httpatomoreillycomsourceoreillyimages1663368.webp)

图 5-10. 用户类架构条目属性设置

> **注意**：

动态链接辅助类( auxiliary class )要求林( forest )运行在 Windows Server 2003 林功能级别( forest functional level )或更高版本。

要将辅助类动态链接到对象，只需修改对象的 `objectClass` 属性，使其包含辅助类的名称。任何辅助类都可以使用，前提是同时设置辅助类中包含的所有 `mustContain` 和 `systemMustContain` 属性。您还可以移除动态链接的辅助类：清除为该辅助类定义的属性设置的任何值，然后从对象的 `objectClass` 属性中移除辅助类名称。

现在让我们说明为什么动态链接辅助类是一个好主意。假设我们有一个林，其中包含多个域( domain )，每个域代表公司内的一个部门。每个部门管理自己的用户对象。其中一个名为 Toasters 的部门想要向其用户对象分配附加属性。这些新属性仅适用于 Toasters 部门内的员工。在 Windows 2000 中，实现此目的的唯一方法是在架构( schema )中创建新属性，创建新的辅助类，并将新属性包含在辅助类中。此时，可以将新的辅助类添加到用户 `classSchema` 对象的 `auxiliaryClass` 属性中。然后，林中包含的每个用户对象都将可以使用新属性。如果每个部门都想做类似的事情，您可以看到林内所有用户对象上的属性数量可能会迅速且不必要地增长。在 Windows Server 2003 中，您仍将在架构中创建新属性和辅助类，但不会修改用户对象的 `auxiliaryClass` 属性。相反，每个部门会将其辅助类动态链接到*其*用户对象。这提供了比 Windows 2000 下更简洁、更高效的实现。

> **警告**：

当您将辅助类动态链接到对象时，该辅助类会列在对象的 `objectClass` 属性中。当辅助类以静态方式链接时，该辅助类不会列在 `objectClass` 属性中。这可能会导致一些问题，对于需要确定对象上可用属性的应用程序，如果它们仅查看对象类( object class )的架构定义或对象本身的 `objectClass` 属性，就会出现问题。

### 5.5. 小结

在本章中,我们展示了 Active Directory 中所有对象的内部蓝图——即架构( Schema )——是如何从 X.500 目录服务衍生而来的。我们解释了 OID 编号系统的用途及其使用方式,以及在 Active Directory 架构扩展( Schema Extension )中必须保持唯一的各种元素(如前缀名称和链接 ID)。

接着,我们以 `userPrincipalName` 属性为例,详细说明了属性及其语法如何在架构中构建为 `attributeSchema` 对象。我们通过详细说明类如何以 `classSchema` 对象的实例形式存储于架构中,展示了如何将属性添加到类。为使其更加清晰,我们深入探讨了 `user` 类的细节,以了解它是如何构建的。最后,我们介绍了从 Windows Server 2003 开始辅助类( Auxiliary Class )如何动态链接,以及这为何具有重要意义。

第 17 章以您在此处学到的内容为基础,演示如何设计和实现架构扩展。

------

[1] X.500 标准定义的名称通常不遵循此方法。例如,Common-Name 属性的 LDAP-Display-Name 为 `cn`,而 Surname 属性的 LDAP-Display-Name 为 `sn`。

---

## 第6章 站点拓扑与 Active Directory 复制

本章介绍 Active Directory 的一个重要功能：多主复制( multimaster replication )。Active Directory 是最早提供多主复制的基于 LDAP 的目录之一。大多数目录将数据从单主服务器复制到从属服务器。例如，Windows NT 4.0 中的复制就是这样工作的。显然，单主复制( single-master replication )方案存在若干潜在问题，包括更新操作的单点故障、主服务器与执行更新的客户端之间的地理距离，以及由于更新只有一个起始位置而导致的复制效率较低。Active Directory 复制解决了这些问题，但需要付出代价。要获得多主复制的好处，你必须首先创建站点拓扑( Site Topology )，用于描述网络并帮助定义域控制器( Domain Controller ,DC)之间应如何相互复制。在大型环境中，构建和维护站点拓扑可能需要大量工作。

本章探讨站点( Site )和复制在 Active Directory 中的基本工作原理。在第14章中，我们将描述使用站点的网络布局的物理基础架构。我们还将该章讨论知识一致性检查器( Knowledge Consistency Checker ,KCC)如何建立和管理复制连接，并详细介绍如何有效地设计和定制 Active Directory 中的站点、站点链路( Site Link )和复制。

### 6.1. 站点拓扑( Site Topology )

Active Directory( AD ) 站点拓扑是描述网络连接、Active Directory 复制指南以及资源位置（相对于 Active Directory 林( Forest )）的映射。此拓扑的主要组件包括站点( Site )、子网( Subnet )、站点链接( Site Link )、站点链接桥( Site Link Bridge )和连接对象( Connection Object )。它们都是 Active Directory 对象，保存在林的配置容器( Configuration Container )中；这样信息可在所有域控制器( Domain Controller ,DC )上本地获取，以便 DC 能够正确通信。

#### 站点和复制管理工具

Microsoft 提供 Active Directory 站点和服务 MMC 管理单元( *dssite.msc* )，帮助管理复制拓扑。此管理单元允许你深入查看站点容器( Sites Container )，其中包含所有站点拓扑对象和连接对象。站点容器在物理上直接位于配置命名上下文( Configuration Naming Context )中的配置容器下。使用站点和服务管理单元，可以创建新站点、子网、链接、桥和连接，还可以设置复制计划、每个链接的度量值等。

除了站点和服务管理单元，*repadmin* 命令行工具也是一个极其有用的工具，应当熟悉。Windows Server 2012 还新增了许多用于管理复制的 PowerShell cmdlet。若要查看所有复制 cmdlet，请在 Windows PowerShell 中运行 *Get-Command \*-adrep**。

> **注意**：

如果要在 Windows 2000 或 Windows Server 2003 上查找 *repadmin*，可以在 Microsoft 提供的 Windows 支持工具( Windows Support Tools )下载中找到它。

#### 子网

子网( Subnet )是网络 IP 空间的一部分。子网由其 IP 网络地址和以位数测量的子网掩码( Subnet Mask )来描述。例如，子网掩码 255.255.255.0 是 24 位子网掩码。如果 10.5.20.0 网络使用 24 位掩码，则子网对象表示为 10.5.20.0/24。Active Directory 中的子网对象是环境中子网的逻辑表示；它们可以反映（但不必一定反映）实际的物理子网定义。例如，某建筑物可能有两个 24 位子网：10.5.20.0 和 10.5.21.0；就 Active Directory 而言，可将它们包含在单个 AD 子网 10.5.20.0/23 中，该子网指定 23 位子网掩码。

> **注意**：

这些示例都表示 IP 版本 4( IPv4 )子网( Subnet )。Windows Server 2008 引入了对 IP 版本 6( IPv6 )子网以及 Active Directory 中域控制器( Domain Controller ,DC)的支持。子网划分的相同概念仍然适用；不过，其地址和子网要大得多。IPv4 使用 32 位寻址，而 IPv6 使用 128 位寻址。

必须在目录中定义子网信息，因为唯一可用于确定网络中相对位置的依据就是计算机的 IP 地址。而子网又与站点( Site )关联。如果没有这些定义，计算机就无法有效确定应尝试使用哪些分布式资源。默认情况下，Active Directory 中未定义任何子网。有关在 Active Directory 中定义子网的详细信息，请参阅后面的侧栏。



向站点添加子网

通过 Active Directory 站点和服务( Active Directory Sites and Services )管理单元向站点添加子网时，必须按 *网络地址/掩码位数( bits masked )* 格式输入子网名称；例如，10.186.149.0/24 是网络地址 10.186.149.0，子网掩码为 255.255.255.0。从 Windows Server 2008 开始，该对话框支持输入 IPv4 和 IPv6 子网。

子网名称中的“掩码位数”部分是指该子网的子网掩码中置位的位数。其值可以介于 0 到 32 之间。子网掩码由四个 *八位组( Octet )* 或字节(四组八位)组成。要将子网掩码转换为位数，请将子网掩码中的每个八位组转换为二进制。子网掩码 255.255.255.0 的二进制表示为 11111111.11111111.11111111.00000000，即使用 8+8+8 位(即 24)来定义子网掩码。子网掩码 255.255.248.0 的二进制表示为 11111111.11111111.11111000.00000000，即 8+8+5，也就是 21。

如果对子网和 IP 地址知之甚少，请查看 Chuck Semeria 的白皮书《Understanding IP Addressing: Everything You Ever Wanted to Know》，网址为 http://holdenweb.com/static/docs/3comip.pdf。该白皮书涵盖 IPv4 和 IPv6。

在任何多站点环境中工作时，确保 Active Directory 中存储的子网信息是最新的非常重要。如果子网信息不准确，当域成员( Domain Member )向其他站点中的域控制器进行身份验证时，可能会产生不必要的广域网( WAN )流量。域控制器还会记录事件，警告缺少子网定义。

解决缺少子网( Subnet )定义的一种策略是使用*超网( Supernet )*。超网是一个术语，用于描述包含一个或多个较小子网的单个子网。例如，你可以定义 10.0.0.0/8 的子网对象( Subnet Object )，以及同一空间内许多子网掩码( Subnet Mask )更大的子网，如 10.1.0.0/16、10.1.2.0/24，甚至 10.1.2.209/32。当 Active Directory 确定某台计算机与哪个子网关联时，它会选择所定义的最具体的子网。因此，如果 IP 地址为 10.1.2.209，则会使用子网 10.1.2.209/32；但如果 IP 地址为 10.2.56.3，则会使用 10.0.0.0/8 子网。

你可能会想，为什么会有人这样做。超网对象可以像任何其他子网对象一样分配到任何站点( Site )。这意味着你可以将这些“兜底”子网分配给中心站点( Hub Site )，供那些来自未另行定义的子网的计算机使用。这样会使这些计算机使用中心资源，而不是随机查找并选择要使用的资源。

图 6-1 展示了一个组织的绝佳示例，其子网设计非常适合在 Active Directory 中部署超网。此拓扑( Topology )中有三个中心站点——芝加哥、圣保罗和伦敦。如果仔细观察，芝加哥下的所有子网可汇总为 10.1.0.0/16，伦敦下的所有子网可汇总为 10.2.0.0/16，圣保罗下的所有子网可汇总为 10.3.0.0/16。通过在 Active Directory 中创建这些子网中的每一个，并将它们关联到各自中心站点，你将为每个位置可能出现的新的子网创建一个安全网。




![Sample site and subnet topology](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663369.webp)


图 6-1. 示例站点和子网拓扑

##### 管理子网( Subnet )

你可以使用 Active Directory 站点和服务( Active Directory Sites and Services )或 Windows PowerShell 创建子网。若要使用 Active Directory 站点和服务创建子网，请浏览到“站点( Site )”下的“子网”容器。右键单击并单击“新建子网”。可以在“Prefix”文本框中输入 IPv4 或 IPv6 子网地址，如图 6-2 所示。还必须将子网与站点关联。在图 6-2 中，我们将子网 172.16.1.0/24 与 Chicago 站点关联。




![Creating a subnet with Active Directory Sites and Services](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663370.webp)


图 6-2. 使用 Active Directory 站点和服务创建子网

若要使用 Windows PowerShell 创建同一子网，需要使用 Windows Server 2012（或 Windows 8）远程服务器管理工具( Remote Server Administration Tools ,RSAT)，或者直接在 Windows Server 2012 服务器上运行命令。要使用的命令为：




```
New-ADReplicationSubnet -Name "172.16.1.0/24" -Site "Chicago"
```


如果需要更改子网关联的站点，可以从子网的属性中更改，也可以使用 *Set-ADReplicationSubnet* cmdlet 更改。



##### 排查子网数据问题

当林( Forest )没有最新的子网信息时，域控制器( Domain Controller ,DC)上会发生一些情况。首先，客户端开始连接到网络上与其逻辑位置不相邻的 DC。这会导致 WAN 流量增加以及客户端性能不佳。接下来，DC 会开始定期在事件日志中记录类似于以下内容的事件：




```
Event ID: 5807
Source: NETLOGON
User: N/A
Computer: DC01
Description:
During the past %1 hours there have been %2 connections to this Domain Controller
from client machines whose IP addresses don't map to any of the existing sites in 
the enterprise. Those clients, therefore, have undefined sites and may connect to 
any Domain Controller including those that are in far distant locations from the 
clients.

A client's site is determined by the mapping of its subnet to one of the existing
sites. To move the above clients to one of the sites, please consider creating sub-
net object(s) covering the above IP addresses with mapping to one of the existing 
sites.

The names and IP addresses of the clients in question have been logged on this
computer in the following log file '%SystemRoot%\debug\Netlogon.log' and, poten-
tially, in the log file '%SystemRoot%\debug etlogon.bak' created if the former log 
becomes full. The log(s) may contain additional unrelated debugging information.

To filter out the needed information, please search for lines which contain text 
  'NO_CLIENT_SITE:'. The first word after this string is the client name and the 
second word is the client IP address.
The maximum size of the log(s) is controlled by the following registry DWORD value 
  'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Netlogon\Parameters\
LogFileMaxSize'; the default is %3 bytes. The current maximum size is %4 bytes.

To set a different maximum size, create the above registry value and set the 
desired maximum size in bytes.
```


最后，每个从某个 IP 地址连接到 DC 且该 IP 地址在 AD 中没有对应子网的客户端，都会记录到 DC 的 *netlogon.log* 文件中，该文件位于 *%windir%\debug\netlogon.log*。缺失子网的日志条目将如下所示：




```
11/12 05:45:29 BRIANLAB: NO_CLIENT_SITE: PC06 192.168.4.111
11/12 06:06:12 BRIANLAB: NO_CLIENT_SITE: PC03 192.168.4.113
```


在前面的示例中，两台计算机 PC06 和 PC03 从 IP 地址（192.168.4.111 和 113）连接，而这些 IP 地址在 Active Directory 中没有对应子网。日志条目的格式为 `Date Time Domain: NO_CLIENT_SITE: Machine-Name IP-Address`。

> **注意**：

前面的日志片段中的 IP 地址可能是 IPv4 或 IPv6 地址。

如果已部署 IPv6，并且客户端同时拥有 IPv4 和 IPv6 地址(即双栈)，则必须确保 AD 中包含 IPv4 和 IPv6 子网的子网映射。如果客户端只配置了其中一种，则会定期看到以下事件：

```
Event ID: 5810
Source: NETLOGON
User: N/A
Computer: DC01
Description:
During the past %1 hours, this domain controller has received %2 connections
from dual-stack IPv4/IPv6 clients with partial subnet-site mappings. A client
has a partial subnet-site mapping if its IPv4 address is mapped to a site but
its global IPv6 address is not mapped to a site, or vice versa. To ensure correct
behavior for applications running on member computers and servers that rely on
subnet-site mappings, dual-stack IPv4/IPv6 clients must have both IPv4 and global
IPv6 addresses mapped to the same site. If a partially mapped client attempts
to connect to this domain controller using its unmapped IP address, its mapped
address is used for the client's site mapping.

The log files %SystemRoot%\debug\netlogon.log or %SystemRoot%\debug\netlogon.bak
contain the name, unmapped IP address and mapped IP address for each partially
mapped client. The log files may also contain unrelated debugging information.
To locate the information pertaining to partial-subnet mappings, search for
lines that contain the text 'PARTIAL_CLIENT_SITE_MAPPING:'. The first word after
this text is the client name. Following the client name is the client's unmapped
IP address (the IP address that does not have a subnet-site mapping) and the
client's mapped IP address, which was used to return site information.

USER ACTION
Use the Active Directory Sites and Services management console (MMC) snap-in
to add the subnet mapping for the unmapped IP addresses to the same site being
used by the mapped IP addresses. When adding site mappings for IPv6 addresses,
you should use global IPv6 addresses and not for instance temporary, link-local
or site-local IPv6 addresses.

The default maximum size of the log files is %3 bytes. The current maximum
size is %4 bytes. To set a different maximum size, create the following registry
DWORD value to specify the maximum size in bytes:
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services
  \Netlogon\Parameters\LogFileMaxSize
```

此外，*netlogon.log* 文件中还会出现包含 `PARTIAL_CLIENT_SITE_MAPPING`(而非 `NO_CLIENT_SITE`)字样的条目。该条目会告知您与活动目录( Active Directory )中子网匹配的 IPv4 或 IPv6 地址，以及未匹配的另一类地址。也就是说，如果客户端通过 IPv6 地址建立连接，但该客户端的 IPv4 地址与活动目录中的某个子网匹配，则日志会提示未映射的 IPv6 地址。

> **注意**：

请访问[此网站](http://bit.ly/XsQzpt)，获取可用于排查子网映射问题的示例脚本。

#### 站点

Active Directory *站点*( Site )通常定义为连接良好的 AD 子网( Subnet )集合。可以使用站点将子网分组为逻辑集合，以帮助定义复制流和资源位置边界。Active Directory 直接使用站点生成其复制拓扑，并帮助客户端查找环境中要使用的“最近”分布式资源(如 DFS 共享或域控制器)。客户端 IP 地址用于确定客户端属于哪个 Active Directory 子网，然后该子网信息反过来用于查找 AD 站点。随后，站点信息可用于通过 DC 定位器服务( DC locator service )执行 DNS 查询，以确定最近的域控制器( Domain Controller ,DC)或全局编录( Global Catalog ,GC)。有关 DC 定位器过程的讨论，请参阅方法 8.3。

域的大多数成员在启动时动态确定其站点，并在后台持续验证自己所在的站点。这样，管理员可以修改站点拓扑，并使其在相对较短的时间内以最少的手动操作正确生效。另一方面，域控制器在提升时选择其站点，并且不会自动更改，除非管理员希望它们成为另一个站点的一部分。将域控制器移动到另一个站点是一项管理任务，最简便的方法是使用 Active Directory Sites and Services 工具执行。

默认情况下，Active Directory 中定义了一个站点，即 *Default-First-Site-Name* 站点。如果未定义任何子网对象，则域的所有成员都会“神奇地”被视为属于此初始站点；如果您已将默认站点替换为另一个站点，则被视为属于任何其他单个已定义站点。一旦存在多个站点对象，或者在定义并分配子网对象之后，“魔法”功能将消失，并且必须为域成员所在的子网定义子网对象。除了它是创建的第一个站点之外，此初始站点没有特别之处；您可以根据需要重命名它。只要已创建至少一个其他站点，并将 *Default-First-Site-Name* 站点内的任何域控制器移动到另一个站点，甚至可以将其删除。

可以为单个物理位置定义多个站点。这样可以更好地隔离哪些资源用于哪些请求者。例如,在大公司中,一种常见做法是专门构建一个独立的站点,用于容纳 Microsoft Exchange 2000 和 2003 服务器,以及用于响应 Exchange 和 Outlook 查询的全局编录( Global Catalog ,GC )。这样,管理员无需将首选的 GC 设置硬编码到 Exchange 中,就能轻松控制使用哪些 GC。你可以根据需要将子网( Subnet )划分得尽可能小,甚至可以小到单个 IP 地址(32 位子网),以便将服务器放入正确的站点。

> **警告**：

自 Exchange 2007 起，由于 Exchange 邮件路由行为发生了变化，将 Exchange 服务器置于单独站点已不再是推荐的最佳实践。如果你要在环境中部署 Exchange，则需要与 Exchange 管理员密切协作，确保支持 Exchange 的站点中有足够的全局编录( Global Catalog )容量。

##### 管理站点

与子网非常相似，你可以使用名称恰如其分的“Active Directory 站点和服务”MMC 管理单元创建站点，也可以使用 Windows PowerShell 创建站点。创建站点时，如图 6-3所示，系统会提示你选择一个站点链接( Site Link )，用于定义将该站点连接到拓扑其余部分的路径。使用 GUI 时，会有点“第22条军规”式的矛盾：要创建站点，就需要选择一个站点链接；但正如你将看到的，当你准备创建站点链接时，又需要选择要链接的站点。因此，创建站点时，临时选择一个站点链接（例如图 6-3中所示的默认链接）没有问题，等站点链接准备就绪后再进行更改即可。




![Creating a site with AD Sites and Services](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663371.webp)


图 6-3. 使用 AD 站点和服务创建站点

要使用 Windows PowerShell 创建相同的站点，可以运行以下命令：




```
New-ADReplicationSite -Name "Paris"
```


请注意，使用 Windows PowerShell 时，创建站点无需指定站点链接。这种循环依赖是 MMC 管理单元的特性，而不是 Active Directory 的特性。

如果要查看与某个站点关联的子网列表，可以在 AD 站点和服务 MMC 管理单元的站点属性中看到它们。

#### 站点链接( Site Link )

*站点链接*允许您定义哪些站点相互连接以及连接的相对开销。创建站点链接时,您需要指定此链接连接哪些站点,以及在相对开销模型中连接的开销或度量值。例如,三个站点——A、B 和 C——可以相互连接,但由于您了解底层物理网络,您可能认为所有流量都应通过 A 站点路由。这需要您配置两个站点链接:A 到 B 以及 A 到 C,如图 6-4所示。




![Sample site topology](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663372.png.webp)


图 6-4. 示例站点拓扑

如果之后在 B 和 C 之间建立了额外的物理网络连接,您可以再设置一个站点链接,将 B 和 C 连接在一起。如果您将全部三个站点链接配置为相等的开销——比如 100——那么流量就可以通过 B 到 C 的链接传输,而不必从 B 到 A 再到 C。这是因为使用 B 到 C 链接的总开销为 100,而使用 B 到 A 再到 C 路由的总开销为 200,后者开销更大。此场景如图 6-5所示。




![Sample site topology with equal costs](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663373.webp)


图 6-5. 开销相等的示例站点拓扑

如果您希望流量仍通过站点 A 传输,则从 B 到 A 再到 C(以及反向)的总开销应低于从 B 到 C 的开销。因此,您需要将 B 到 C 链接的开销设置为大于 200——例如 300,如图 6-6所示。在此场景中,只有当连接因某种原因无法通过站点 A 时,才会使用 B 到 C 站点链接。




![Sample site topology with unequal costs](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663374.webp)


图 6-6. 开销不等的示例站点拓扑

站点链接有两种复制类型:IP 和 SMTP。IP 站点链接实际上代表远程过程调用( Remote Procedure Call ,RPC )风格的复制连接。这是迄今为止最常用的站点链接类型;事实上,Active Directory 创建的默认站点链接就是一个名为 *DEFAULTIPSITELINK* 的 IP 站点链接。另一种站点链接类型是 SMTP 站点链接。

SMTP 站点链接( SMTP Site Link )是一种特殊的基于 SMTP(简单邮件传输协议( Simple Mail Transfer Protocol ),不妨理解为电子邮件)的复制协议。当某些站点的网络连接质量极差或不可靠(例如延迟极高或可用性无法预测),以至于无法支撑 RPC(远程过程调用)复制连接时,就要用 SMTP 复制与这些站点通信。不过出于安全方面的考虑,只有特定的命名上下文( Naming Context ,NC )才能通过 SMTP 站点链接复制。只有配置命名上下文( Configuration NC )、架构命名上下文( Schema NC )以及只读全局编录命名上下文( read-only Global Catalog NC )可以通过 SMTP 复制。这意味着,域命名上下文( Domain NC )仍必须通过更常见的 IP 复制协议(配合 RPC)来复制。

除了定义应使用哪些复制协议、哪些站点应与哪些其他站点进行复制之外,站点链接还负责控制域控制器( Domain Controller ,DC )和全局编录( Global Catalog ,GC )对本地没有 DC 或 GC 的站点的覆盖范围。此行为称为*自动站点覆盖*( auto site coverage )。

请看图 6-7中的示意图,其中展示了站点 A、B 和 C。站点 A 拥有 Dom1 和 Dom2 的域控制器,但站点 B 只有 Dom1 的 DC,站点 C 只有 Dom2 的 DC。那么,当某个域在本地站点没有域控制器时,客户端如何决定该使用哪个 DC 呢?从逻辑上看,你可以直接判断:"如果有人身处站点 C 却需要登录 Dom1,客户端应该去与站点 A 通信。"但 Active Directory 无法做出这种直觉性的跳跃,它需要依据确凿的数字来计算,而站点链接开销( site link metric )正是为此而生:为目录提供必要信息,以便通过计算确定某个域控制器除自身站点外还应覆盖哪些站点。

Active Directory 会根据站点链接拓扑结构,自动为没有域控制器的站点注册必要的覆盖用 DNS 记录。Active Directory 与 DNS 之间的关系将在第 8 章中详细介绍。关于如何禁用自动站点覆盖,请参见[此网站](http://bit.ly/14arpCV)。




![Sample site topology requiring automatic site coverage](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663375.webp)


图 6-7. 需要自动站点覆盖的示例站点拓扑

##### 管理站点链路

在活动目录站点和服务( Active Directory Sites and Services )MMC 管理单元中,创建站点链路的位置不太容易找到:该选项隐藏在*Sites\Inter-Site Transports\IP*下,如图 6-8所示。

> **注意**：

如果使用 SMTP 复制并且需要创建 SMTP 站点链接( Site Link )，则需要在图 6-8所示的 *SMTP* 文件夹内创建站点链接。

![Managing IP site links with AD Sites and Services](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663376.webp)

图 6-8. 使用 AD 站点和服务( AD Sites and Services )管理 IP 站点链接

找到正确位置后，可以右键单击，然后单击“新建站点链接...”。需要为站点链接指定名称，并选择要包含在该站点链接中的两个或多个站点。虽然 AD 支持在一个链接中包含超过两个站点，但通常建议每个链接只包含两个站点，以便更轻松地进行故障排除并理解预期拓扑( topology )。

在图 6-9中，我们在 Chicago 和 Paris 之间创建了一个站点链接。创建站点链接后，可考虑添加一个与名称顺序相反的描述。例如，在图 6-9中，我们创建了一个名为 *Chicago-Paris* 的站点链接。如果将描述设置为 *Paris-Chicago*，则通过按“名称”或“描述”列排序，就能按站点链接的任一端进行排序（如图 6-8所示）。

要使用 Windows PowerShell 创建相同的站点链接，请运行以下命令：

```
New-ADReplicationSiteLink -Name "Chicago-Paris" -Description "Paris-Chicago" `
-SitesIncluded @("Chicago","Paris") -Cost 100 -ReplicationFrequencyInMinutes 15
```

这里有一处语法您可能还不熟悉。在 *SitesIncluded* 参数中，必须向 PowerShell 提供一个*数组*( array )。数组使您能够将列表传递给特定实参。PowerShell 提供了一种创建数组的快捷方式，即如本例所示，将列表包裹在 *@()* 语法中。

创建站点链接( Site Link )之后,你很可能需要设置该站点链接的一些属性,例如开销、复制频率,或者计划。图 6-10 显示了 Chicago-Paris 站点链接的属性。在本场景中,我们将开销设置为 100,将复制间隔设置为 15 分钟。你可以使用图 6-10 中所示的"更改计划( Change Schedule )"按钮来管理计划。请记住,站点链接的计划定义的是复制可以*开始*的时间。一旦复制开始,就会一直持续到完成为止。




![Creating a site link between Chicago and Paris](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663377.webp)


图 6-9. 在 Chicago 和 Paris 之间创建站点链接




![Site link properties](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663378.webp)


图 6-10. 站点链接属性

#### 站点链接桥

默认情况下，Active Directory 假定所有站点之间的网络路径具有传递性。换言之，参照图 6-4，Active Directory 假定站点 C 中的域控制器( Domain Controller ,DC )能够与站点 A 中的域控制器*直接*通信。但在某些网络中，由于网络本身不允许这种传递性，这种默认行为并不适用。人们在讨论网络问题时，有时会将这种情况称为网络*未完全路由*( not fully routed )。当你遇到此类场景时，可能需要为林禁用"桥接所有站点链接"选项。该选项可通过在"Active Directory 站点和服务"中右键单击 *Sites\Inter-Site Transports\IP* 文件夹并打开属性来访问。SMTP 复制传输也有独立的相同设置。

如果已禁用"桥接所有站点链接"，你可能需要在目录中定义站点链接桥( Site Link )。( Site Link Bridge )。站点链接桥包含一组可视为具有传递性的站点链接。换言之，你所桥接的站点链接列表中的任何站点都可以直接通信。再次参照图 6-4，如果 A 到 C 以及 A 到 B 的站点链接被桥接，我们就是在告知 Active Directory：站点 C 中的域控制器与站点 B 中的域控制器之间的直接通信是允许的。

我们将在第 14 章中更详细地讨论站点链接桥。你可以在与创建站点链接相同的位置创建站点链接桥。Windows PowerShell 提供了 *New-ADReplicationSiteLinkBridge* cmdlet，可用于通过脚本创建站点链接桥。

#### 连接对象( Connection Object )

拓扑拼图的最后一块是*连接对象*。连接对象指定哪些域控制器( Domain Controller ,DC )与哪些其他域控制器进行复制、复制频率以及涉及哪些命名上下文( Naming Context )。与通常需要手动配置的站点( Site )、子网( Subnet )和站点链路( Site Link )不同，连接对象通常由域控制器自身管理。其理念是：应通过为站点、子网和站点链路提供明确定义来在逻辑上构建站点拓扑，而 Active Directory 将能够确定在站点内部和站点之间互连实际域控制器的最佳方式。

有时可能无法让 AD 管理所有这些连接，但这是一个非常值得努力实现的目标；除非别无选择，否则应尽量避免修改或补充连接对象。早期版本的 Active Directory 无法正确地对域控制器之间的复制连接进行负载平衡，因此中心站点( Hub Site )中的域控制器可能会被来自分支站点( Spoke Site )域控制器的复制流量压垮。这种情况常常导致管理员选择手动管理复制连接，或使用 Active Directory 负载平衡工具( Active Directory Load Balancing ,ADLB )进行管理。幸运的是，从 Windows Server 2008 开始，Active Directory 获得了自动对到只读域控制器( Read-Only Domain Controller ,RODC )的复制连接进行负载平衡的能力。Windows Server

#### 知识一致性检查器( Knowledge Consistency Checker ,KCC)

除最小型部署（如小型企业服务器( Small Business Server ,SBS)或其他单站点环境）外，管理员都应在 Active Directory 中创建与物理网络紧密对应的站点拓扑( Site Topology )。遗憾的是，Active Directory 并不足够智能，无法通过查看网络来为每家安装 Active Directory 的公司构建其自己的复杂拓扑，以优化复制和资源定位——它需要你的帮助。创建站点拓扑的详细内容参见第 14 章。

设置好站点、子网和站点链路( Site Link )对象后，一个名为 *知识一致性检查器( Knowledge Consistency Checker ,KCC)* 的 Active Directory 进程会获取这些信息，并自动生成和维护连接对象( Connection Object )，这些对象描述了应在哪些域控制器( Domain Controller ,DC)之间复制哪些命名上下文( Naming Context ,NC)，以及如何复制和何时复制。KCC 使用两种独立算法来确定需要哪些连接对象：站点内和站点间。

站点内算法( Intrasite Algorithm )旨在*为每个命名上下文*创建最小延迟环形拓扑，保证站点内任意两个域控制器之间的跳数不超过三跳。在站点内添加和删除 DC、全局编录服务器( Global Catalog Server ,GC)和域时，KCC 会根据需要添加和删除域控制器之间的连接，以维持这种最小跳数拓扑。处理单个域和少量域控制器时，这种拓扑非常容易可视化，但随着添加大量域控制器和其他域，可视化会变得极其困难。

另一方面，站点间算法( Intersite Algorithm )不是最小跳数算法；它尝试通过生成树算法( Spanning-Tree Algorithm )保持站点连接，以便复制能够进行，然后仅根据站点链路度量值来建立这些连接。KCC 完全可能生成一种复制拓扑( Replication Topology )，使得更改必须经过八个站点才能从拓扑一端复制到另一端。如果你不满意 KCC 为站点间拓扑创建的站点连接，因为这些连接与你的网络连接不一致，那么问题几乎可以肯定与站点链路的配置方式有关。精心设计的站点拓扑有助于 KCC 生成智能且高效的复制连接对象集合。



### 6.2. 复制的工作原理

微软为 Active Directory 复制引入了一系列新术语，对于初次接触 Active Directory 的人来说，其中大多数术语可能完全陌生。为了正确设计复制拓扑，您不仅需要理解复制的基本工作原理，还需要理解这些新术语在复制过程中的含义——微软的文档和管理工具中通篇都在使用这些术语。在阅读本章后续内容时，请根据需要随时回顾此处给出的术语定义。即使第一遍甚至第五遍阅读时未能完全消化，也不必沮丧。即便是经验丰富的管理员，也会就复制机制的运作方式以及各种结构和流程的恰当术语展开讨论。

本节讨论将使用图 6-11中的示例复制拓扑。




![Sample replication topology for “How Replication Works” discussion](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663379.webp)


图 6-11. “复制的工作原理”讨论所用的示例复制拓扑



#### 元数据背景知识

*复制元数据( Replication Metadata )*是管控复制过程的数据。Active Directory 复制能够在不同域控制器( Domain Controller ,DC)上的命名上下文( Naming Context ,NC)之间传输数据，同时避免陷入无限复制循环或丢失任何数据。为了实现这一过程，每个 NC 都保存了大量与该特定 NC 内复制直接相关的信息。这意味着架构 NC 的复制数据存储在架构 NC 中，配置 NC 的复制数据存储在配置 NC 中，与前者相互独立，依此类推。之所以采用这种方式，是因为所有复制都是基于命名上下文的。当域控制器从另一台域控制器拉取变更时，它按命名上下文逐个串行执行。

> **警告**：

尽管时间不是 Active Directory 中复制的基础，但它仍然极其重要。域控制器( Domain Controller ,DC)之间用于复制的所有身份验证都基于 Kerberos，并且 Kerberos 对主机之间的最大时间偏差( time-skew )有要求。在采用默认设置的域中，如果某个域控制器与其他所有域控制器的公共时间偏差超过五分钟，则该域控制器将无法再与其他域控制器进行复制。

##### 更新序列号( Update Sequence Number ,USN )与 highestCommittedUSN

每个域控制器( Domain Controller ,DC )都维护自己单独的更新序列号( USN )。每当对 Active Directory 中的对象进行更改(新建对象、更新、删除等)时,就会发生一个事务。USN 是一个 64 位值,分配给每个原子更新事务,并且仅在与其执行更新的域控制器相关时才有意义。每个单独的更新事务都会生成一个递增的 USN 值。单个 USN 可以表示对象上每个属性的更改或单个对象上单个属性的更改。如果我们检查域控制器的最高提交 USN,发现它是 1,000,然后 10 分钟后回来,发现最高提交 USN 现在是 1,056,我们就会知道在过去 20 分钟内,该域控制器上发生了 56 个事务。

虽然某些目录系统使用时间戳来控制复制以及需要在服务器之间传播的内容,但 Microsoft 选择使用 USN 值。这些值按顺序递增,这一事实完全避免了域控制器的时钟被设置为向后或与其复制伙伴不同步的问题。虽然 USN 独立于域控制器上的时钟,但 USN 只能向前移动这一点至关重要。当域控制器上的 USN 被递减时(通常是通过还原虚拟机快照),您会发现自己处于通常称为 *USN 回滚* ( *USN rollback* )的情况中。每个域控制器都在 `RootDSE` 的 `highestCommittedUSN` 值中为每个命名上下文( Naming Context )维护其最高组合 USN。有关查看 `highestCommittedUSN` 值的步骤,请参阅 第 4 章 中的侧栏 使用 LDP 查询 RootDSE。

更新序列号( Update Sequence Number ,USN )用于唯一标识特定域控制器( Domain Controller ,DC )的某个命名上下文( Naming Context )中已发生的每一次更新，无论更新类型如何。同一个 USN 值在两个不同的域控制器上表示同一更改的可能性极低。这意味着，你可以根据特定 USN 从特定域控制器请求单个更改，但这不允许基于相近的 USN 值在不同 DC 之间进行直接比较。将名为 *Cerberus* 的计算机帐户( Computer Account )的描述更改为“joe’s computer”这一更改，在一个域控制器上可能是 USN 23865，在另一个域控制器上可能是 USN 4078，在又一个域控制器上则可能是 USN 673459234。

##### 原始更新与复制更新

复制过程区分两种类型的更新：

- **原始更新（写入）**

  此术语定义特定更新的起始点——即该更改最初发生在哪个域控制器上。

- **复制更新（写入）**

  此术语定义与原始更新相对的情形——即所涉更改并非源自本地，而是从另一个域控制器复制而来。

如果你使用“Active Directory 用户和计算机”管理单元在 DC A 上创建五个用户，DC A 的 USN 将递增五次，每进行一次原始更新就递增一次。这些更改随后会被复制到 DC B，使 DC B 的 USN 递增五次。同样，如果 DC A 收到来自 DC B 的更改，DC A 的 USN 将递增一次。此行为在表 6-1中有所概述。

> **注意**：

如果某个 Active Directory 数据库事务被中止（即未能完成），则关联的 USN 值不会分配给任何对象，也不会以任何方式重用。随着更改的发生，USN 会继续递增。



表 6-1. USN 递增示例

| 操作                                                         | 命名上下文     | 发起域控制器                  | 域控制器          | USN  |
| ------------------------------------------------------------ | -------------- | ----------------------------- | ----------------- | ---- |
| 初始 USN 值                                                  | 域 NC          | 不适用                        | DC A              | 1000 |
| 初始 USN 值                                                  | 域 NC          | 不适用                        | DC B              | 2500 |
| 创建 5 个新用户（发起更新）                                  | 域 NC          | DC A                          | DC A              | 1005 |
| 接收 5 个新用户（复制更新）                                  | 域 NC          | DC A                          | DC B              | 2505 |
| 修改用户描述属性（发起更新）                                 | 域 NC          | DC B                          | DC B              | 2506 |
| 接收修改后的用户描述属性（复制更新）                         | 域 NC          | DC B                          | DC A              | 1006 |

##### DSA GUID 和调用 ID

每个域控制器都有一个称为目录服务代理（Directory Service Agent，*DSA*）GUID 的 GUID。此 DSA GUID 用于唯一标识域控制器，并且是“Active Directory 站点和服务”中域控制器下可见的 NTDS Settings 对象的 `objectGUID`。除非域控制器被降级并重新提升，否则此 GUID 不会更改。

Active Directory 数据库（*ntds.dit*）也有一个 GUID。后一个 GUID 用于在复制调用中标识服务器的 Active Directory 数据库，称为*调用 ID*；它存储在域控制器的 NTDS Settings 对象的 `invocationId` 属性中。每当在该 DC 上还原 Active Directory 时，或每当 DSA GUID 更改时，调用 ID 都会更改。Windows Server 2012 DC 在检测到其虚拟机生成 ID 发生更改时，也会重置其调用 ID。有关虚拟机生成 ID（VM gen ID）更改过程的详细信息，请参阅第 9 章。

> **注意**：

更改 GUID 可确保网络上的其他域控制器( Domain Controller ,DC )识别出这是一个新的数据库实例,并为此在各自的表中创建新的高水位矢量( High-Watermark Vector )和最新性矢量( Up-to-Dateness Vector )条目。

这样一来,备份之后发生的更改便可复制回新还原的数据库,使其正确达到最新状态。若缺少此步骤,凡是在备份完成后源自该还原 DC 并已复制到目录其余部分的更改,在该 DC 还原后将永远不会再复制回该 DC。这是因为复制伙伴会认为该 DC 已拥有这些更改,毕竟它原本就是这些更改的源头。

表 6-2汇总了 DSA GUID 和调用 ID 的取值。

表 6-2. DSA GUID 与调用 ID 汇总

| 对象          | 属性           | 描述                                                         |
| ------------- | -------------- | ------------------------------------------------------------ |
| NTDS Settings | `objectGUID`   | 在域控制器的整个生命周期内唯一标识该域控制器。此属性值称为 DSA GUID。 |
| NTDS Settings | `invocationID` | 唯一标识域控制器上的 Active Directory 数据库。此属性值称为调用 ID。当域控制器从备份还原或检测到虚拟机代 ID( VM Gen ID )发生变化时,调用 ID 会被重置。 |

##### 高水位标记向量(直接最新性向量)

高水位标记向量( High-Watermark Vector ,HWMV)是由每个域控制器( Domain Controller ,DC)独立维护的一个表,用于帮助高效复制命名上下文( Naming Context ,NC)。具体而言,它用于帮助域控制器确定在与特定复制伙伴复制命名上下文时上次复制到的位置。

域控制器为它所维护副本的每个命名上下文都维护一个此类表,因此每个域控制器至少会有三个 HWMV 表:分别用于架构、配置和域命名上下文。每个表都存储域控制器针对给定命名上下文从每个直接复制伙伴那里收到的更新的最高 USN。这些 USN 值用于确定下一个复制周期中与每个伙伴应从何处开始复制。这允许域控制器针对每个命名上下文从给定复制伙伴请求最新更新。

当本地域控制器针对某个命名上下文与其某个伙伴启动复制时,该域控制器的该命名上下文高水位标记向量中针对该伙伴的最高 USN 是发送给复制伙伴的信息之一。复制伙伴将该值与其针对该命名上下文的当前最高 USN 进行比较,以帮助确定应向该域控制器发送哪些更改。如下一节所述,该逻辑由最新性向量( Up-to-Dateness Vector )进一步细化。

继续前面的示例,DC A 和 DC B 的 HWMV 表在表 6-3和表 6-4中列出。



表 6-3. DC A 的高水位标记向量表

| 命名上下文 | 复制伙伴 | 高水位标记向量(收到的上次更新的 USN) |
| -------------- | ------------------- | -------------------------------------------------- |
| 域命名上下文      | DC B 调用 ID  | 2506                                               |
| 域命名上下文      | DC C 调用 ID  | 3606                                               |



表 6-4. DC B 的高水位标记向量表

| 命名上下文( Naming Context ) | 复制伙伴( Replication Partner ) | 高水位向量( High-Watermark Vector,即上次接收更新的 USN) |
| -------------- | ------------------- | -------------------------------------------------- |
| 域命名上下文( Domain NC ) | DC A 调用 ID( Invocation ID ) | 1006 |
| 域命名上下文 | DC C 调用 ID | 3606 |

##### 最新性向量

最新性向量( Up-to-Dateness Vector ,UTDV)是每台域控制器( Domain Controller ,DC)独立维护的一张表，用于协助高效复制命名上下文( Naming Context )。具体而言，它用于复制抑制( Replication Dampening )，以减少不必要的复制流量和无休止的复制循环。

域控制器为其维护副本的每个命名上下文都有一张表，因此，同样地，每台域控制器至少会有三张这样的表。每张表存储该域控制器从林( Forest )中曾经存在过的所有其他域控制器收到的最高原始更新( Originating Update ) USN，以及该域控制器最后一次成功完成与给定复制伙伴( Replication Partner )和命名上下文的复制周期( Replication Cycle )的日期/时间。

最新性向量与高水位标记向量( High-Watermark Vector )结合使用，以减少复制流量。当命名上下文的复制请求传递给复制伙伴时，目标域控制器针对该命名上下文的最新性向量也会包含在请求中。源伙伴随后可以聚焦于它此前尚未发送的更改，并进一步筛选掉目标域控制器可能已从其他复制伙伴收到的任何更改。这样，它可确保单个更改不会多次复制到同一域控制器；这称为*传播抑制( Propagation Dampening )*。

让我们再次审视示例复制场景；不过，这次会在场景中加入 DC C。表 6-5 显示了每一步之后的 USN 值。

表 6-5. 包含 DC C 的 USN 值

| 操作                                                         | 命名上下文     | 起始域控制器                  | 域控制器          | USN  |
| ------------------------------------------------------------ | -------------- | ----------------------------- | ----------------- | ---- |
| 初始 USN 值                                                  | 域 NC          | 不适用                        | DC A              | 1000 |
| 初始 USN 值                                                  | 域 NC          | 不适用                        | DC B              | 2500 |
| 初始 USN 值                                                  | 域 NC          | 不适用                        | DC C              | 3750 |
| 创建 5 个新用户（起始更新）                                  | 域 NC          | DC A                          | DC A              | 1005 |
| 接收 5 个新用户（复制更新）                                  | 域 NC          | DC A                          | DC B              | 2505 |
| 接收 5 个新用户（复制更新）                                  | 域 NC          | DC A                          | DC C              | 3755 |
| 修改用户描述属性（起始更新）                                 | 域 NC          | DC B                          | DC B              | 2506 |
| 接收已修改的用户描述属性（复制更新）                         | 域 NC          | DC B                          | DC A              | 1006 |
| 接收已修改的用户描述属性（复制更新）                         | 域 NC          | DC B                          | DC C              | 3756 |

一旦 DC C 接收到由 DC A 发起的更新，它会尝试将这些更新复制到 DC B；然而，DC B 已经从 DC A 直接接收了这些更新。为防止无休止的复制循环，DC C 会检查 DC B 的最新性向量表，从而知道不应发送这些更新。

现在 DC C 也包含在内，让我们再次查看高水位标记向量表。表 6-6、6-7 和 6-8 展示了 DC A、DC B 和 DC C 的 HWMV 和 UTDV 表。



表 6-6. DC A 的高水位标记和最新性向量表

| 命名上下文 | 复制伙伴 | 高水位向量（上次更新的 USN ） | 最新向量 |
| -------------- | ------------------- | ----------------------------------------- | --------------------- |
| 域 NC      | DC B 调用 ID  | 2506                                      | 2506                  |
| 域 NC      | DC C 调用 ID  | 3756                                      | 3756                  |



表 6-7. DC B 的高水位向量和最新向量表

| 命名上下文 | 复制伙伴 | 高水位向量（上次更新的 USN ） | 最新向量 |
| -------------- | ------------------- | ----------------------------------------- | --------------------- |
| 域 NC      | DC A 调用 ID  | 1006                                      | 1006                  |
| 域 NC      | DC C 调用 ID  | 3756                                      | 3756                  |



表 6-8. DC C 的高水位向量和最新向量表

| 命名上下文 | 复制伙伴 | 高水位向量（上次更新的 USN ） | 最新向量 |
| -------------- | ------------------- | ----------------------------------------- | --------------------- |
| 域 NC      | DC A 调用 ID  | 1006                                      | 1006                  |
| 域 NC      | DC B 调用 ID  | 2506                                      | 2506                  |

请注意，现在每个域控制器( Domain Controller ，DC )都为其复制的每个域控制器维护一个最新向量。当 DC B 从 DC C 拉取更改时，它会在请求中包含其最新向量表。DC C 随后会检查此表，并发现 DC B 已经从 DC A 接收了该更改。此功能可防止原本可能发生的无限循环，同时还能消除网络上不必要的复制流量。

##### 回顾

以下列表总结了本节的重要要点：

- Active Directory 拆分为多个独立的命名上下文( naming context ,NC)，每个 NC 均独立复制。

- 在每个 NC 内，存储着多种元数据( metadata )。

  对于给定域控制器( Domain Controller ,DC)上的每个 NC，维护一个高水位向量( high-watermark vector )，其中包含其每个复制伙伴( replication partners )的一个条目。此表中针对复制伙伴的值仅在复制周期( replication cycle )期间更新。

  对于给定 DC 上的每个 NC，维护一个最新程度向量( up-to-dateness vector )，其中包含曾在此 NC 内执行过原始写入( originating write )的每个 DC 的一个条目。每个条目包含三个值：

  - 原始服务器( originating server )的 DSA GUID
  - 原始服务器的 USN
  - 一个时间戳，指示与原始域控制器( originating domain controller )上次成功复制的日期和时间

这些值仅在复制周期期间更新。

#### 复制过程中对象元数据的修改方式

> **注意**：

为尽量减少缩写，本节中术语 *域控制器( Domain Controller ,DC)* 和 *服务器( server )* 可互换使用。术语 *属性( property )* 和 *特性( attribute )* 在此也可互换使用。

要了解复制过程中实际数据是如何修改的，请考虑一个四步示例：

1. 在 DC A 上创建一个对象（一个用户）。
2. 该对象被复制到 DC B。
3. 该对象随后在 DC B 上被修改。
4. 对该对象的新更改被复制回 DC A。

此四步过程如 图 6-12 所示。该图描绘了在代表每个步骤的四个时间段内，用户对象在 DC A 和 DC B 上的状态。

现在，请结合 图 6-12 来阅读对每个步骤的讨论。

##### 步骤 1：在服务器 A 上初始创建用户

当在域控制器( Domain Controller ,DC ) A 上创建用户时，DC A 就是源服务器( originating server )。在 Active Directory 数据库中表示在 DC A 上创建新用户的事务期间，会为该事务分配一个更新序列号( Update Sequence Number ,USN )，其值为 1000。该用户的 `uSNCreated` 和 `uSNChanged` 属性会自动设置为 `1000`（对应用户创建事务的 USN）。该用户的所有属性也会用一组数据进行初始化，如下所示：

- 该属性的值（一个或多个）根据系统默认值或创建用户时给定的参数进行设置。
- 该属性的 USN 设置为 1000（此事务的 USN）。
- 该属性的版本号设置为 1。
- 该属性的时间戳设置为对象的创建时间。
- 该属性的源服务器全局唯一标识符( Globally Unique Identifier ,GUID )设置为 DC A 的 GUID。
- 该属性的源服务器 USN 设置为 1000（此事务的 USN）。

这些信息可以说明有关该用户的几件事：

- 该用户是在此域控制器上的事务 1000 期间创建的（`uSNCreated` `= 1000`）。
- 该用户最后一次更改是在事务 1000 期间（`uSNChanged` `= 1000`）。
- 该用户的属性从未修改过其原始值（属性版本号 = 1），并且这些值是在事务 1000 期间设置的（各属性的 USN = 1000）。
- 每个属性最后一次由源服务器 DC A 在事务 1000 期间设置（源服务器 GUID 和源服务器 USN）。

前面的讨论展示了两个对象级值( per-object values )和五个属性级值( per-attribute values )发生了更改。虽然 `uSNChanged` 和 `uSNCreated` 是 Active Directory 中每个对象上的实际属性，但对象的属性只能拥有值，不能包含其他属性，例如版本号。

实际上，对于任意给定对象的每个属性，所有按属性的复制元数据( replication metadata )（属性版本号( Property Version Number )、更改时间( Time-Changed )、源 DC GUID( Originating-DC-GUID )、源 USN( Originating-USN )、属性 USN( Property-USN )）会一起编码为单个字节字符串，并作为对象的非复制属性( nonreplicated attribute ) `replPropertyMetaData` 存储。

> **注意**：

可使用 PowerShell、*repadmin*、*adfind*、ADSI Edit 或 LDP 查看属性元数据。有关如何查看复制元数据的示例，请参阅侧边栏查看复制元数据。



查看复制元数据

复制元数据( Replication Metadata )可通过多种工具轻松查看，并且可能是故障排除过程中的关键组成部分，尤其是在尝试确定活动目录( Active Directory ,AD)中的数据何时何处发生更改时。在本示例中，我们将使用 *repadmin* 显示 Administrator 帐户的复制元数据：




```
repadmin /showobjmeta "DC01" "CN=Administrator,CN=Users,DC=contoso,DC=com"
```


*repadmin* 在此示例中需要两个参数：

- 要在其上查询元数据的域控制器( Domain Controller ,DC)
- 要显示其元数据的对象的可分辨名称( Distinguished Name ,DN)

下面显示了部分结果输出。您将注意到，每个复制的属性都存储本地 USN 和原始 USN、原始域控制器、更改的日期和时间以及版本号。




```
Loc.USN  Originating DSA Org.USN   Org.Time/Date        Ver Attribute
=======  =============== ========= ===================  === ============
8194     SiteA\DC01      8194      2008-03-24 21:27:24   1  objectClass
8194     SiteA\DC01      8194      2008-03-24 21:27:24   1  cn
8194     SiteA\DC01      8194      2008-03-24 21:27:24   1  description
8194     SiteA\DC01      8194      2008-03-24 21:27:24   1  instanceType
8194     SiteA\DC01      8194      2008-03-24 21:27:24   1  whenCreated
8194     SiteA\DC01      8194      2008-03-24 21:27:24   1  displayName
8194     SiteA\DC01      8194      2008-03-24 21:27:24   1  name
15987    SiteA\DC02      12117     2008-04-14 11:07:42   2  pwdLastSet
```


您还可以使用 *Get-ADReplicationAttributeMetadata* cmdlet 通过 Windows PowerShell 检索相同信息。Windows PowerShell 为处理此类数据提供了更强大的接口。以下命令（全部在一行中输入）对数据进行排序，以匹配 *repadmin* 的输出：




```
Get-ADReplicationAttributeMetadata `
-Object "CN=Administrator,CN=Users,DC=contoso,DC=com" `
-Server dc01 | Select LocalChangeUsn, `
LastOriginatingChangeDirectoryServerIdentity, `
LastOriginatingChangeUsn, LastOriginatingChangeTime, `
Version, AttributeName | ft
```




##### 步骤 2：将原始写入复制到 DC B

稍后，当此对象复制到 DC B 时，DC B 会将该用户作为复制写入添加到其 Active Directory 副本中。在此事务期间，将分配 USN 2500，并且用户的 `uSNCreated` 和 `uSNChanged` 属性会修改为对应于 DC B 的事务 USN (2500)。

由此我们可以了解到几个关键点：

- 该用户是在此服务器上的事务 2500 期间创建的（`uSNCreated` `= 2500`）。
- 该用户上次更改是在事务 2500 期间（`uSNChanged` `= 2500`）。
- 该用户的属性从未修改过其原始值（属性版本号 = 1），并且这些值是在事务 2500 期间设置的（属性的 USN = 2500）。
- 每个属性上次由原始服务器 DC A 在事务 1000 期间设置（原始服务器 GUID 和原始服务器 USN）。




![How metadata is modified during replication](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663380.webp)


图 6-12. 复制期间元数据如何修改

##### 步骤 3:在域控制器 B( Domain Controller B ,DC B )上更改用户密码

现在，DC B 上已复制且可写的用户对象发生了一次原始写入( Originating Write )，即密码更改。由于距最初创建该用户已过去一段时间，因此分配给此密码更改事务的更新序列号( Update Sequence Number ,USN )为 3777。更改密码时，用户的 `uSNChanged` 属性被修改为 `3777`。此外，密码属性(且仅密码属性)按以下方式修改:

- 设置密码值。
- 该属性的 USN 设置为 3777(此事务的 USN)。
- 该属性的版本号设置为 2。
- 该属性的时间戳设置为事务 3777 发生的日期/时间。
- 该属性发起服务器的全局唯一标识符( Globally Unique Identifier ,GUID )设置为服务器 B 的 GUID。
- 该属性的发起服务器 USN 设置为 3777(此事务的 USN)。

查看该用户对象时，现在可以看到该对象上次更改是在事务 3777 期间，并且该事务表示一次源自 DC B 的密码更改。

##### 步骤 4:将密码更改复制到 DC A

此步骤与步骤 2 类似。当 DC A 在复制期间收到密码更新时，它会为该更改事务分配 USN 1333。

> **注意**：

请记住，更新发生在属性级别而非对象级别，因此仅发送密码，而不发送整个用户对象。

在事务 1333 期间，用户的 `uSNChanged` 属性被修改为与服务器 A 的事务 USN 相对应。

> **注意**：

如果你在实际的域控制器上重现此分步演练，你会注意到两处差异。

第一处差异是，在从 DC A 复制到 DC B 之后，`cn` 属性实际上会显示始发写入来自 DC B。这是一个影响任何给定对象的 RDN 属性的后端实现细节，也是此类差异唯一出现的情况。

第二处差异是，密码更改实际上会更新多个属性，而不仅仅是一个。涉及的属性包括 `dBCSPwd`、`unicodePwd`、`pwdLastSet`、`ntPwdHistory` 和 `lmPwdHistory`。这是另一个后端实现细节。对于大多数属性，当你专门更新单个属性时，只有该属性会被修改和复制；密码则作为特殊情况处理。

由此，我们可以了解到以下几点:

- 该用户是在此服务器上的事务 1000 期间创建的(`uSNCreated` `= 1000`)。
- 该用户最后一次更改是在事务 1333 期间(`uSNChanged` `= 1333`)。
- 除一个属性外，该用户的所有属性都保留了其原始值(属性版本号 = 1)，并且这些值是在事务 1000 时设置的(属性的 USN = 1000)。
- 除一个属性外，所有属性最后一次均由始发服务器 DC A 在事务 1000 期间设置(始发服务器 GUID 和始发服务器 USN)。
- 密码自创建以来首次被修改(密码版本号 = 2)是在事务 1333 期间(密码的 USN = 1333)，并且它是在 DC B 上的事务 3777 期间被修改的(始发服务器 GUID 和始发服务器 USN)。

以上就是复制期间对象和属性元数据的修改方式。现在让我们来看看复制究竟是如何发生的。

#### 两个服务器之间命名上下文( Naming Context ,NC)的复制

在以下示例中,一个域中有五台服务器:服务器 A、服务器 B、服务器 C、服务器 D 和服务器 E。它们复制的是哪个 NC、哪些服务器与哪些其他服务器进行复制都无关紧要(因为它们不必都彼此直接复制),因为任意两个服务器的复制过程仍然相同。复制过程分为五个步骤:

1. 启动与伙伴的复制。
2. 伙伴确定要发送哪些更新。
3. 伙伴将更新发送到发起服务器。
4. 发起服务器处理这些更新。
5. 发起服务器检查自身是否已是最新。

##### 步骤 1:启动与复制伙伴( Replication Partner )的复制

复制在任何时候都只在两台服务器之间进行。因此,我们以服务器 A 和服务器 B 为例,它们是复制伙伴。

在服务器 A 上的复制计划( Replication Schedule )所指示的某个时间点,服务器 A 针对特定命名上下文( Naming Context ,NC )启动与服务器 B 的复制,并请求其尚未拥有的任何更新。这是一次从服务器 B 到服务器 A 的单向更新传输。在此复制周期( Replication Cycle )中,不会向服务器 B 传递任何新更新,因为若要进行此类传递,需要由服务器 B 发起复制。

服务器 A 通过向服务器 B 发送复制请求以及五条重要的复制元数据( Replication Metadata )(即与复制过程本身相关的数据),来启动复制。这五条元数据如下:

- 服务器 A 希望接收其更新的 NC 的名称
- 在此复制周期中,服务器 A 希望接收的最大对象更新数
- 在此复制周期中,服务器 A 希望接收的最大值数量
- 服务器 B 的更新序列号( Update Sequence Number ,USN ),该值来自服务器 A 针对此 NC 的高水位矢量( High-Watermark Vector )
- 服务器 A 针对此 NC 的最新性矢量( Up-to-Dateness Vector )

指定最大对象更新数和属性值数对于限制网络带宽消耗非常重要。如果某台服务器自上一个复制周期以来产生了大量更新,则限制单个复制数据包( Replication Packet )中复制出的对象数量,意味着不会因在一个巨型数据包中复制这些对象而过度占用网络带宽。相反,复制会在整个复制周期内分解为更小的数据包。一旦某个命名上下文的复制周期已启动,它就会复制所有更改,无论需要多少个数据包或花费多长时间,除非域控制器( Domain Controller ,DC )之间的连接彻底失败。

> **警告**：

上一段中关于复制计划行为的表述看似微妙，实则至关重要。计划仅定义复制可以*开始*的时间。一旦复制周期开始，它就不会停止，直至完成（或连接中断）。即使计划时间已过，情况依然如此。

此步骤如图 6-13所示，图中表明：虽然复制的发起发生在服务器 A 上名为 xxxx 的命名上下文（ NC ）（其中 xxxx 可表示架构 NC、配置 NC、应用程序分区或任何域 NC），但实际复制稍后将从服务器 B 到服务器 A 进行。




![Initiating replication with Server B for NC xxxx](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663381.webp)


图 6-13. 为 NC xxxx 发起与服务器 B 的复制

##### 步骤 2:复制伙伴( Replication Partner )确定要发送哪些更新

服务器 B 接收所有这些元数据，并确定需要针对此命名上下文( Naming Context ,NC)发回哪些更新。首先，服务器 B 确定其 NC 副本自身的最高已提交更新序列号( Update Sequence Number ,USN)，并将其与服务器 A 从其高水位标记向量表( High-Watermark Vector Table ,HWMV)提交的 USN 进行比较。假设已有一些更新发生，服务器 B 就能立即知道自服务器 A 上次与服务器 B 复制以来发生了多少更新。这必然成立，因为在上一复制周期中，服务器 A 的 HWMV 已使用服务器 B 针对该 NC 的最高已提交 USN 进行了更新。因此，两个 USN

假设服务器 B 有四项要发送给服务器 A 的更新：一项原始写入( originating write )（服务器 B 的更新序列号( Update Sequence Number ,USN) 为 1111），以及三项复制写入( replicated writes )（服务器 B 的 USN 分别为 1109、1110 和 1112）。之所以是四项，是因为在此示例中，1112 是服务器 B 上最后一次更新，而 图 6-13 中服务器 A 针对服务器 B 上 xxxx 的高水位标记向量( High-Watermark Vector ,HWMV) 中的 USN 为 1108。因此，我们从 1109 开始查找更新，一直到服务器 B 上的最后一次更新，即 1112。前两项复制写入（服务器 B 的 USN 1109 和 1110）源自服务器 E（服务器 E 的 USN 567 和 788），还有一项（服务器 B 的 USN 1112）源自服务器 D（服务器 D 的 USN 2345）。如 表 6-9 所示。

表 6-9. 可能要发送的更新

| 服务器 B USN | 发起域控制器( Domain Controller ,DC)的全局唯一标识符( Globally Unique Identifier ,GUID) | 发起域控制器 USN |
| ------------ | ---------------------------------------------------------------------------------------------- | ------------------ |
| 1109         | 服务器 E 的 GUID                                                                               | 567                |
| 1110         | 服务器 E 的 GUID                                                                               | 788                |
| 1111         | 服务器 B 的 GUID                                                                               | 1111               |
| 1112         | 服务器 D 的 GUID                                                                               | 2345               |

根据 图 6-13，服务器 A 已经有服务器 D 的 2345 更新，因为服务器 A 针对服务器 D 的最新性向量( Up-to-Dateness Vector ,UTDV) 中的 USN 为 2350。因此，服务器 A 和服务器 B 都已经有服务器 D 的 2345 更新，无需再次通过网络发送该更新来浪费带宽。（如前所述，过滤之前已见过的更新以防止它们在服务器之间持续发送的做法称为“传播抑制( propagation dampening )”。）

既然你已经了解高水位标记向量和最新性向量如何帮助服务器 B 确定需要发送哪些更新，下面来看看服务器 B 用于确定所需数据的确切过程。

当服务器 B 收到来自服务器 A 的更新请求时，将发生以下步骤：

1. 服务器 B 复制其针对服务器 A 的最新性向量( up-to-dateness vector )。
2. 可以这么说,服务器 B 将该表暂时搁置一旁,并在整个命名上下文( naming context )中搜索 `uSNChanged` 值大于服务器 A 的高水位向量( high-watermark vector )条目中针对服务器 B 的 USN 值的所有对象。随后,将该列表按 `uSNChanged` 升序排序。
3. 服务器 B 初始化一个空的输出缓冲区,用于添加要发送给服务器 A 的更新条目。它还初始化一个名为 Last-Object-USN-Changed 的值,用于表示此特定复制会话中发送的最后一个对象的 USN。该值并非任何特定对象的属性,只是一段简单的复制元数据。
4. 服务器 B 按 `uSNChanged` 升序枚举对象列表,并对每个对象使用以下算法:
   - 如果该对象已被添加到输出缓冲区,服务器 B 将 Last-Object-USN-Changed 设置为当前对象的 `uSNChanged` 属性值,并继续枚举下一个对象。
   - 如果该对象尚未被添加到输出缓冲区,服务器 B 将测试该对象是否包含需要发送到目标端的更改。对于当前对象的每个属性,服务器 B 获取该属性的 Originating-DC-GUID ,并从服务器 A 的 UTDV 中查找与该 GUID 对应的 USN。根据该条目,服务器 B 查看 Originating-USN。如果服务器 B 上该属性的 Originating-USN 大于服务器 A 的 UTDV 条目值,则该属性需要发送。
   - 如果需要发送更改,则将更新条目添加到输出缓冲区。服务器 B 将 Last-Object-USN-Changed 设置为当前对象的 `uSNChanged` 属性值,并继续枚举下一个对象。
   - 如果不需要发送更改,服务器 B 将 Last-Object-USN-Changed 设置为当前对象的 `uSNChanged` 值,并继续枚举下一个对象。

> **注意**：

枚举过程中，如果达到所请求的对象更新条目或值的限制，枚举将提前终止，并将名为 `More-Data` 的标志设置为 `True`。如果枚举完成时未触及任一限制，则 `More-Data` 设置为 `False`。

##### 步骤 3：伙伴服务器向发起服务器发送更新

服务器 B 根据服务器 A 尚未从其他来源看到的更新，确定应发回的更新列表。然后，服务器 B 将此数据发送到服务器 A。此外，如果 `More-Data` 设置为 `False`，还会返回一项额外的元数据。服务器 B 返回的信息包括：

- 来自服务器 B 的输出缓冲区更新
- 服务器 B 的 Last-Object-USN-Changed 值（即服务器 A 要为服务器 B 的命名上下文( Naming Context ,NC )插入到高水位标记向量( High-Watermark Vector ,HWMV )中的值）
- `More-Data` 标志
- 服务器 B 针对此 NC 的最新性向量( Up-to-Dateness Vector )（仅在 `More-Data` 设置为 `False` 时发送）

如图 6-14所示。

![Server B sends the updates to Server A for NC xxxx](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663382.webp)

图 6-14. 服务器 B 向服务器 A 发送 NC xxxx 的更新

如果服务器 B 计算出服务器 A 已是最新状态且不需要更新，则仅向服务器 A 返回最后两项元数据。这种情况可能在以下情形下发生：服务器 B 上该 NC 的最高已提交更新序列号( Update Sequence Number ,USN )与服务器 A 传递的 HWMV 条目相同（即自上次复制周期以来未发生更新），

##### 步骤 4：发起服务器处理更新

服务器 A 接收数据。对于接收到的每个更新条目，服务器 A 分配一个更新序列号( Update Sequence Number ,USN )，并启动一个数据库事务，以更新其自身副本的活动目录( Active Directory ,AD )数据库中的相关对象。该对象的 `uSNChanged` 属性设置为该事务的 USN。然后提交数据库事务。对接收到的每个更新条目重复此过程。

处理完所有更新条目后，服务器 A 针对服务器 B 的高水位矢量( high-watermark vector )中的 USN 设置为从服务器 B 收到的最后更改对象的 USN（Last-Object-USN-Changed）。换句话说，服务器 A 现在知道，它与服务器 B 保持同步，直到刚刚发送过来的最后一个更改。

服务器 A 收到的 Last-Object-USN-Changed 使其能够知道服务器 B 所做的最后更新。这将在下一个复制周期( replication cycle )中使用。在前面的示例中，发送到服务器 A 的最高更新是 USN 1111。服务器 B 的 USN 1112 更新实际上并未发送，因为服务器 A 已经看到它。但是，服务器 B 随数据返回的 Last-Object-USN-Changed 仍然是 1112，而不是 1111。

##### 步骤 5:发起方服务器检查自身是否已是最新

服务器 A 现在检查 `More-Data` 标志。如果 `More-Data` 设置为 `True`,服务器 A 返回步骤 1,再次与服务器 B 开始复制并请求更多更新。如果 `More-Data` 设置为 `False`,则说明所有更新都已从服务器 B 接收完毕,最后服务器 A 的最新性矢量( Up-to-Dateness Vector ,UTDV )本身也会被更新。

最新性矢量使服务器 A 能够识别服务器 B 已见到哪些原始更新( Originating Update ),从而通过复制得知它自己现在已见到哪些原始更新。服务器 A 不会用收到的矢量直接替换自身的最新性矢量,而是逐项检查接收到的表中的条目,并执行以下两种操作之一。如果某台服务器的条目未出现在自己的 UTDV 中,就将其添加到表中,这样服务器 A 便知道,对于一台新服务器而言,它现在已经更新到了某个特定层级;如果某台服务器的条目已列在服务器 A 的 UTDV 中,而收到的值更高,就用该更高的值修改自己保存的表副本——毕竟它现在已经由那台服务器更新到了这个新层级,所以最好把这一事实记录下来。

表 6-10 展示了步骤 1 之前和步骤 5 之后,服务器 A 在 xxxx 命名上下文( Naming Context )中的最新性矢量和高水印矢量( High-Watermark Vector ,HWMV )。

表 6-10. 更新前后服务器 A 的 UTDV 与 HWMV 状态

|               | 服务器 B 的 HWMV | 服务器 B UTDV | 服务器 C UTDV | 服务器 D UTDV | 服务器 E UTDV |
| ------------- | ----------------- | ------------- | ------------- | ------------- | ------------- |
| 步骤 1 之前 | 1108              | 1108          | 100           | 2350          | 540           |
| 步骤 5 之后  | 1112              | 1111          | 100           | 2350          | 790           |

##### 小结

以下要点总结了命名上下文之间的复制:

- 高水印矢量用于检测需要在复制伙伴之间发送的更新。
- 最新性矢量用于传播抑制( Propagation Dampening ),对更新进行筛选,使伙伴只传输发起方服务器尚未见到的更新。
- 每个对象上的 `uSNChanged` 属性用于确定哪些对象可能需要作为更新发送给发起方服务器。

> **注意**：

如果需要，您可以使用 Active Directory 站点和服务管理单元强制手动复制域控制器( Domain Controller ,DC) 上的特定命名上下文( Naming Context ,NC)。浏览到要通过其进行复制的连接对象，右键单击该对象，然后选择“立即复制”。也可以使用 *repadmin* 实用工具从命令行执行此操作。

使用 Windows PowerShell，您可以使用 *Sync-ADObject* cmdlet 强制复制特定对象。不过，没有可一次性同步整个分区的 cmdlet。

#### 复制冲突( Replication Conflict )的协调方式

尽管复制过程( replication process )通常本身能够正常进行，但有时在两个复制周期( replication cycle )之间，两台服务器执行了无法调和的操作，因此可能会发生冲突。例如，假设服务器 A 创建了一个具有特定名称的对象( object )，而大约同一时间服务器 B 在同一父容器( parent container )下创建了一个同名对象。这两个对象不能同时存在于 Active Directory 中，那么这两个对象会发生什么？是删除或重命名其中一个对象？还是两个对象都会被删除或重命名？

如果管理员在服务器 D 上将某个对象移动到某个组织单位( Organizational Unit ,OU )，而与此同时在服务器 B 上该组织单位正被删除，又会怎样？这个即将成为孤立对象( orphaned object )的对象会发生什么？它会随该组织单位一起被删除，还是会被完全移动到其他位置？

再看最后一个示例：如果服务器 B 上的管理员更改了某个用户的密码，而该用户自己在服务器 C 上更改了自己的密码，那么该用户最终使用哪个密码？

所有这些冲突都需要在下一个复制周期中在 Active Directory 内解决。确切的协调( reconciliation )过程以及最终决定如何复制回去，取决于所发生的具体冲突。

##### 由相同属性( attribute )更改导致的冲突

此场景发生在同一对象上的某个属性在大约同一时间于两台不同的域控制器( Domain Controller ,DC )上被更新时。在复制期间，每个域控制器都会遵循以下过程来解决冲突：

1. 服务器通过查看两个属性的版本号( version number )来开始协调。版本号较高的属性将在冲突中胜出。
2. 如果属性版本号相等，服务器会检查两个属性的时间戳( timestamp )。更改时间较晚的属性将在冲突中胜出。
3. 如果属性时间戳相等，则检查来自两台发起服务器( originating server )的全局唯一标识符( Globally Unique Identifier ,GUID )。由于 GUID 必须唯一，这两个值必然彼此不同，因此服务器会将 GUID 按数学比较更高的发起服务器所做的属性更改判定为冲突的胜出者。

> **注意**：

Active Directory 的所有复制元数据时间戳均以协调世界时( Universal Time Coordinated ,UTC)存储，它更常被称为格林尼治标准时间( Greenwich Mean Time ,GMT)或祖鲁时间。

##### 因移动对象或在现已删除的父级下创建对象而导致的冲突

此情境是指，在一台服务器上的特定组织单位( Organizational Unit ,OU)或容器( Container )下创建对象（例如，一个名为 People 的 OU），同时，在另一台服务器上大约同一时间删除了该 OU。

这是一种比较容易解决的冲突。在这种情况下，父级（People OU）保持删除状态，但该对象会被移动到命名上下文( Naming Context )的“丢失和找到( Lost and Found )”容器中，该容器是专门为此情境设置的。mycorp.com 域的丢失和找到容器的可分辨名称( Distinguished Name ,DN)为：

```
cn=LostAndFound,dc=mycorp,dc=com
```

除了域中的丢失和找到容器之外，每个林( Forest )都有一个用于配置分区( Configuration Partition )的丢失和找到容器。对于 mycorp.com 林，该容器位于：

```
cn=LostAndFoundConfig,cn=Configuration,dc=mycorp,dc=com
```

##### 因创建名称冲突的对象而导致的冲突

请回想一下，对象的相对可分辨名称( Relative Distinguished Name ,RDN)在其父容器的上下文中必须唯一。当在两台不同的服务器上创建了两个具有相同 RDN 的对象时，就会发生这种特定冲突。在复制期间，域控制器( Domain Controller ,DC )会采取以下步骤来解决此冲突：

1. 服务器通过查看两个对象的版本号来开始协调。版本号较高的对象将在冲突中胜出。
2. 如果对象版本号相同，服务器将检查两个对象的时间戳。更改时间较晚的对象将在冲突中胜出。
3. 如果两个对象的时间戳也相同，则检查来自两台发起服务器的 GUID。服务器再次将来自具有更高 GUID 的发起服务器的对象更改视为冲突的胜出者。

但在这种情况下，冲突解决中落败的对象并不会丢失或被删除；而是会将冲突属性修改为一个已知的唯一值。这样一来，在解决过程结束时，两个对象都会存在，其中一个对象的冲突名称会改为唯一值。该唯一名称采用以下格式：*<ObjectName><LineFeed>CNF:<ObjectGUID>*。

> **警告**：

此逻辑仅用于对象的相对可分辨名称( Relative Distinguished Name ,RDN)命名值（通常是 `cn` 属性）。它不用于清理其他通常要求唯一的值，例如代表用户用户名或计算机名的 `sAMAccountName` 属性。有关如何处理重复 `sAMAccountName` 值的详细信息，请参阅即将出现的侧栏 Active Directory 如何处理重复的帐户值。

在以下示例中，一台名为 *PC04* 的计算机因冲突而被重命名。这很可能发生在管理员在将该计算机加入域时遇到错误，然后随后再次尝试之后。在随后的尝试中，管理员在复制发生之前连接到了另一台域控制器( Domain Controller ,DC)：




```
CN=PC04\0ACNF:41968ad2-717e-4ffc-a876-04798d288ede,CN=Computers,DC=contoso,DC=com
```




Active Directory 如何处理重复的帐户值

虽然复制引擎通过使用对象的 GUID 篡改 RDN 来处理重复的 RDN，但 Active Directory 处理重复 `sAMAccountName` 和 `objectSID` 安全标识符( Security Identifier ,SID)值的过程是完全独立的。这些类型重复项的检测发生在各种操作（如登录或对象名称解析）期间，当域控制器搜索对象并发现多个匹配项时。

首先，让我们看看重复的 `sAMAccountName` 值。当发现重复的用户或计算机 `sAMAccountName` 时，最新的对象保持原样。其他对象的 `sAMAccountName` 值将更改为模式 `$DUPLICATE-`*`<RID>`*，其中 *`<RID>`* 是对象 SID 的相对标识符( Relative Identifier ,RID)组件。

第二种情况是重复的 `objectSID` 值。这不应该发生，因为系统会生成 SID，但域控制器回滚场景可能会导致重复的 SID，因为 RID 会被重用。当域控制器遇到重复的 SID 时，具有该 SID 的所有用户或计算机将立即从域中删除。

在这两种情况下，都会在发现并解决重复项的域控制器的系统事件日志中记录一个事件。有关这些事件的信息，请参阅以下链接：

- http://technet.microsoft.com/en-us/library/ee410964(v=ws.10).aspx
- http://technet.microsoft.com/en-us/library/ee410964(v=ws.10).aspx

##### 复制冲突解决方案

假设服务器 A 启动了一个复制周期。首先，它向服务器 B 请求更改并接收更新。然后，服务器 A 向服务器 C 请求更改并接收更新。但是，当服务器 A 按顺序应用服务器 C 的更新时，它确定这些更新与服务器 B 最近应用的更新之间发生了冲突。服务器 A 根据前面的准则解决了冲突，并判定服务器 C 胜出。现在，虽然服务器 A 和服务器 C 是正确的，但服务器 B 仍需要使用服务器 C 的值进行更新。

为此，当服务器 B 下次向服务器 A 请求更新时，它会收到(除其他更新外)源自服务器 C 的更新。然后，服务器 B 按顺序应用它收到的更新，当它处理到源自服务器 C 的更新时，它会检测到相同的冲突。随后，服务器 B 执行与服务器 A 相同的冲突解决过程，并得出相同的结果。因此，它会修改自己对该对象的副本以适应更改。

当在服务器上进行更改后，该服务器在复制更改之前宕机，可能会出现其他问题。如果该服务器始终未重新启动以复制更改，则这些更改显然会丢失。

> **注意**：

另一种情况是，如果该服务器很久之后才重新上线，并尝试将这些更改复制回 Active Directory，那么发生冲突解决的可能性就会大得多（如果该服务器上所做的许多更改，后来在其他服务器上以更近的时间点已对 Active Directory 做了相同更改，则该服务器会在冲突中失败）。这不是什么问题，但属于您需要了解的情况。

### 6.3. 常见复制问题

在实际环境中或有关活动目录( Active Directory )复制的讨论中，常常会遇到几个问题。虽然这些问题你都不希望碰上，但了解它们仍然很重要，这样你就能识别其症状并准备好应对措施。

#### 残留对象( Lingering Objects )

*残留对象* 会在以下情况出现:域控制器( Domain Controller ,DC)离线时间超过林( forest )的墓碑生存时间( tombstone lifetime )后重新上线并再次开始复制( replication )。我们将在第 18 章详细讨论墓碑生存时间的概念,但简而言之,它是指已删除对象的记录在 Active Directory 数据库中保留多长时间,以确保删除操作能够复制。根据林创建时间的不同,如果未修改默认值,墓碑生存时间很可能是 60 天或 180 天。

当域控制器离线时间超过墓碑生存时间后又重新连接时,它将永远不会收到离线期间已删除对象的通知。因此,除了重新上线的那个域控制器之外,林中任何其他域控制器上都不会存在这些对象。这可能以多种方式引发问题。首先,如果目标指向该特定域控制器,已删除的用户帐户( user account )将再次可供使用(可能是因为员工被解雇)。其次,如果你使用 Exchange,则显示在全局地址列表( Global Address List ,GAL)中的用户和联系人等旧对象,可能会对某些用户重新出现,因为这些用户从所涉域控制器获取其 GAL 视图。发布到 Active Directory 的打印机是另一个常见示例。打印队列( print queue )会按正常操作随时发布到目录中或从目录中删除。最终用户在包含存在残留对象的域控制器的站点( site )中搜索 AD 中的打印机时,可能会尝试连接到已不存在的打印机。

除这些情况外,在其他域控制器上,你经常会看到与复制相关的事件日志条目( event log entry ),其中提到林中可能存在残留对象。你可以采取几个步骤来控制残留对象的传播( propagation ),并清理存在残留对象的域控制器。

首先,在所有域控制器( Domain Controller ,DC)上启用*严格复制一致性*( Strict Replication Consistency )。此设置的作用是:当域控制器检测到有尝试复制残留对象( Lingering Object )的行为时,它会隔离相应的复制伙伴( Replication Partner )。当残留对象被复制回林( Forest )中时,删除操作实际上会被撤销,该对象将还原为残留对象所在域控制器上的状态。这种行为并非我们所期望的。若要启用严格复制一致性,请设置以下注册表设置:




```
Path: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\NTDS\Parameters
Value Name: Strict Replication Consistency
Value Type: REG_DWORD
Value: 1
```

> **注意**：

可以使用 *repadmin* 在林的每台域控制器( Domain Controller ,DC )上启用严格复制一致性。为此，请运行以下命令：*repadmin /regkey \* +strict*。

若要清理域控制器上的残留对象( Lingering Object )，最简便的方法是先降级该域控制器，然后再将其重新提升。如果无法这样做，可以利用 *repadmin* 中的残留对象清理功能。此时需要选择一台域控制器作为权威源，Active Directory 将检查你正在清理的域控制器上的每个对象是否也存在于你的“权威源”DC 上。

若要对照 *DC05* 检查 *DC17* 的域分区( Domain Partition )（*contoso.com*）中是否存在残留对象，请执行以下步骤：

1. 通过运行以下命令解析 *DC05* 的 DSA GUID（以粗体显示）：*repadmin /showrepl DC05*。这会生成如下输出：

   

   
```
   SiteA\DC05
   DSA Options: IS_GC
   Site Options: (none)
   DSA object GUID: 67c1ee19-4706-4c56-b1cb-3a299541376e
   DSA invocationID: 54770948-f0d3-44ed-ae26-291ab6200ed4
```


2. 在咨询模式下对 *DC17* 运行“删除残留对象命令”，以获取将要删除的对象列表：

   

   
```
   repadmin /removelingeringobjects DC17 67c1ee19-4706-4c56-b1cb-3a299541376e 
   dc=contoso,dc=com /advisory_mode
```


   上述命令包含三个参数：要检查的域控制器（*DC17*）、源域控制器的 DSA GUID（*67c1*...）以及要验证的分区的 DN（*dc=contoso,dc=com*）。

3. 查看 *DC17* 事件日志( Event Log )中记录的事件（事件 1938、1946 和 1942），以获取将要删除的对象列表。

4. 再次运行删除残留对象命令，但不要使用 */advisory_mode* 开关，以从 *DC17* 的域分区中删除残留对象：

   

   
```
   repadmin /removelingeringobjects DC17 67c1ee19-4706-4c56-b1cb-3a299541376e 
   dc=contoso,dc=com
```


需要对 *DC17* 承载的每个命名上下文( Naming Context ,NC )重复上述步骤。这包括配置命名上下文、DNS 命名上下文以及任何全局编录( Global Catalog ,GC )分区。

#### USN 回滚

随着虚拟化在 IT 中变得普遍，*USN 回滚*的概念已成为许多 Active Directory 管理员讨论的话题和恐惧。USN 回滚是一种危险的情况，可能导致复制黑洞、重复 SID 以及其他问题。遇到 USN 回滚的最常见途径是回滚虚拟机快照以及使用基于映像的磁盘备份程序。Microsoft 已在每个版本的 Active Directory 中采取措施，试图减轻这些操作的影响，而 Windows Server 2012 最终正面解决了该问题的许多方面。我们将在第 9 章中讨论 Windows Server 2012 所做的改进，但现在我们将重点讨论对复制的影响，而不考虑这些特定改进。

正如我们之前讨论的，USN 只应向前移动。每当域控制器( Domain Controller ,DC )启动一个事务时，它都会递增本地 USN 计数器，以便可以标识该事务。考虑 USN 的另一种方式是将其视为逻辑时钟。如果你想想时钟，时钟从不倒转。考虑一个虚拟化域控制器，其 USN 类似于图 6-15：

1. 在 USN 为 5 时，管理员创建虚拟机( Virtual Machine ,VM )的快照。
2. 在本地进行多次更改，USN 递增到 9。
3. 接下来，管理员回滚快照。USN 现在为 5。
4. 再次进行多次更改，它们被分配 USN 6 到 9。

第 4 步是关键。管理员所做的更改与之前的更改具有相同的 USN。这导致其他 DC 无法在其 HWMV 表中进行跟踪。




![Active Directory’s logical clock—the USN](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663383.webp)


图 6-15. Active Directory 的逻辑时钟——USN

为了更好地理解，回想一下我们之前讨论过，DC 会在其高水位标记向量表( high-watermark vector tables )中跟踪它们从其他 DC 复制的更改。让我们再次审视前面的场景，考虑图 6-16中所示的复制过程：

1. 在 T1，DC-A 的 `highestCommittedUSN` 为 `100`。DC-B 的高水位标记向量( High-Watermark Vector ,HWMV )反映了这一点，且这两个 DC 处于同步状态。
2. 在 T2，管理员在虚拟机监控程序( Hypervisor )中对 DC-A 创建快照。
3. 在 T3，管理员在 DC-A 上创建 75 个用户，使 DC-A 的 `highestCommittedUSN` 增加到 `175`。DC-B 复制这些更改并更新其 HWMV，以反映它已从 DC-A 复制到更改 175。
4. 在 T4，管理员将 DC-A 回滚到创建快照之前的状态。DC-A 的 `highestCommittedUSN` 现在再次为 `100`。
5. 在 T5，管理员在 DC-A 上创建 15 个用户，使 DC-A 的 `highestCommittedUSN` 增加到 115。DC-B 通过检查其 HWMV 并向 DC-A 请求更新序列号( Update Sequence Number ,USN ) 175 之后的任何更改，开始与 DC-A 进行复制周期。DC-A 回复称没有更改可发送。

T5 之后的最终结果是，DC-A 上存在一组永远不会复制到 DC-B 的对象。在 DC-A 达到 USN 175 之前，在 DC-A 上所做的*任何*更改都*绝不会*复制到 DC-B。自 Windows Server 2003 起，Active Directory 一直尝试检测这种情况，并在其发生时隔离复制，以便可以强制降级该域控制器( Domain Controller ,DC )，然后重新提升它，使其与林( Forest )中的其余部分重新同步。好消息是，从 Windows Server 2012 开始，在向虚拟机提供虚拟机生成 ID( VM Generation ID )的虚拟机监控程序上运行的虚拟化 DC，不会遭受在该虚拟机监控程序的状态模型中发生的任何回滚场景的影响。不过，在虚拟机监控程序不知情的情况下发生的任何“手动”快照仍可能产生回滚场景，例如还原磁盘子系统中的底层文件。

![Active Directory replication with USN rollback](./image/6.%20Site%20Topology%20and%20Active%20Directory%20Replication/httpatomoreillycomsourceoreillyimages1663384.webp)

图 6-16. USN 回滚时的 Active Directory 复制

### 6.4. 小结

在本章中,我们探讨了站点拓扑( Site Topology )在 Active Directory 中的重要性,以及它与物理网络之间的关系。我们还讨论了管理复制过程的元数据、系统如何自动跟踪对象和属性的变更、数据在服务器之间的复制方式(包括传播抑制),以及冲突的解决机制。

在第 14 章中,我们将进一步拓展这些知识,介绍 Active Directory 如何管理并自动生成站点内部及站点之间的复制连接。掌握这些内容后,我们便可以继续探讨 Active Directory 中站点和链路( Site Link )的设计原则。

---

## 第7章 搜索活动目录

存储在活动目录( Active Directory )中的数据对于生成准确报告和支持关键业务应用往往至关重要。通过查询目录，您可以直接收集满足需求的数据，无论是用于一次性报告、周期性流程，还是支持与AD集成的应用程序。为了实现这一目标，您需要熟练掌握为搜索开发*LDAP筛选器*的技能。

LDAP筛选器的构建和理解相对直接，因为其语法简单，运算符数量非常有限。但除了简单地构造LDAP筛选器外，能够优化查询以提高效率，并且不对AD性能产生负面影响，是一项关键技能。同样，能够分析应用程序的查询并修改架构以提升性能，是一项基本的故障排除技能。

### 7.1. 目录信息树

Active Directory 将其数据库存储在每个域控制器( Domain Controller ,DC)上的 *ntds.dit* 文件中，该文件通常简称为“DIT”。DIT 是*目录信息树*( Directory Information Tree ,DIT)的缩写——这是 AD 数据库的一个花哨别称。DIT 中数据的结构出奇简单；如果你有数据库背景，熟悉将数据优化到多个表和多个范式迭代中，那么你可能会对 AD 存储数据的方式感到震惊。

#### 数据库结构

从根本上说，DIT 组织为三个关键表：

- 数据表( Data Table )
- 链接表( Link Table )
- 隐藏表( Hidden Table )

此外，Windows Server 2003 及更高版本的域控制器还有几个表，用于 ACL 的单实例存储（安全描述符表( Security Descriptor Table )）以及跟踪对象配额。

##### 隐藏表

隐藏表是一个单行表，Active Directory 在启动时使用它来查找数据表中与配置相关的信息。也就是说，隐藏表包含一个指向数据表中该域控制器的 NTDS Settings 对象的指针。此外，这里还存储了一些其他与配置相关的项。

##### 数据表

数据表保存 Active Directory 数据库中的大部分数据。无论其类别如何（例如，用户还是组织单位( Organizational Unit ,OU)），目录中的每个对象（包括架构( Schema )）都存储在此表中的单独行内。架构中定义的每个属性都构成数据表中的一列，如图 7-1 所示。




![The data table](./image/7.%20Searching%20Active%20Directory/httpatomoreillycomsourceoreillyimages1663385.webp)


图 7-1. 数据表

> **注意**：

你可能会认为，如果对象在架构( schema )中未定义某个属性，却仍为该属性列存储空值，就会带来存储开销。幸运的是，活动目录( Active Directory ,AD) 使用的数据库引擎——可扩展存储引擎( Extensible Storage Engine ,ESE)——非常擅长存储空值，因此以这种方式存储数据并不会产生额外开销。

除了在 AD 中常见的标识符（例如安全主体( security principal )的 SID 或目录中每个对象的 `objectGUID`）之外，数据表还会为表中的每一行使用一个特殊的唯一标识符。该标识符称为*可分辨名称标记( distinguished name tag ,DNT)*，如图 7-1的第一列所示。创建新对象时，会分配下一个可用的 DNT。对象的 DNT 不会被复制，因此同一对象很可能在每个域控制器( Domain Controller ,DC)上具有不同的 DNT。此外，对象被删除后，DNT 不会被重用。

> **注意**：

给定数据库中，活动目录( Active Directory ,AD)最多可包含 2,147,483,393（2^31 – 255）个可分辨名称标记( Distinguished Name Tag ,DNT)。因此，如果某个域控制器( Domain Controller ,DC)在其生命周期内已累计存储了这么多对象，那么该 DC 上可能无法再创建新对象。

除 DNT 列之外，图 7-1 中还显示了若干引用。父 DNT( Parent DNT ,PDNT) 列存储的是父 DNT。它是指向数据库中该对象直接父行的指针。在目录中移动对象时，其 PDNT 列项会更新，以匹配对象的新父级。命名上下文 DNT( Naming Context DNT ,NCDNT) 列包含与对象所在的命名上下文( Naming Context ,NC)匹配的命名上下文头( naming context head )的 DNT。NCDNT 列有助于说明应用程序分区( application partition )只是逻辑分区。你会看到，在图 7-1 中，配置( Configuration )和架构( Schema )命名上下文与域( Domain )命名上下文存储在一起。这些 NC 中对象的 NCDNT 项仅指向相关对象的 DNT。

图 7-1 还包括一个祖先( Ancestors )列。祖先列在搜索期间使用，它只是列出了数据库根与该对象之间的所有 DNT。换言之，祖先列表示域中的层次结构。与 PDNT 列一样，移动对象时，祖先列也会相应更新。

如前所述，每个属性的数据都作为数据库中的单独列存储，如 A1 到 A3 等列所示。需要注意的一个细节是，RDNType 列实际上存储对象架构中相对可分辨名称( Relative Distinguished Name ,RDN )属性的 DNT。为了更便于理解图示，我们移除了这一层抽象。

##### 链接表

接下来的这张表——链接表( Link Table ),如图 7-2 所示——负责存储链接属性( Linked Attribute )中的数据。组成员身份就是链接属性数据的一个常见例子。链接的存储方式为:引用正向链接( Forward Link )所指向对象的 DNT、被链接对象的 DNT,以及架构( Schema )中正向链接属性的链接 ID。此外,表中还有若干此处未展示的其他列,分别用于跟踪链接值复制( Linked Value Replication ,LVR )的复制元数据、跟踪在使用回收站( Recycle Bin )时链接是否已被停用,以及为采用 DN-Binary 或 DN-String 语法的属性存储可选的链接数据。




![The link table](./image/7.%20Searching%20Active%20Directory/httpatomoreillycomsourceoreillyimages1663386.webp)


图 7-2. 链接表

> **注意**：

严格来说,LinkBase 列中的值并不是直接指向该属性的正向链接 ID 值。我们在图中简化了这一细节,因为它与本文的讨论无关。

图 7-3 中链接表的图示使内容解释起来更为容易。在本例中,我们可以看到所显示的行正在跟踪 Domain Admins 组中的一个成员身份。具体来说,用户 Brian Desmond(DNT 9601)是 Domain Admins(DNT 5615)的成员。LinkBase 列告诉我们,对应属性的链接 ID 为 2。




![Link table references to the data table](./image/7.%20Searching%20Active%20Directory/httpatomoreillycomsourceoreillyimages1663387.webp)


图 7-3. 链接表对数据表的引用

##### 安全描述符表

最后,安全描述符表用于在 AD 中实现访问控制列表( Access Control List ,ACL)的单实例存储。该表是在 Windows Server 2003 中引入的,旨在减小 AD 数据库的大小,因为许多组织发现其 AD 数据库的很大一部分被重复的 ACL 所占用。该表的工作原理是存储 `ntSecurityDescriptor` 属性的值以及这些值的校验和。数据表为每个对象存储指向 ACL 的指针(指向安全描述符表中的相应行),因此对于共享同一 ACL 的对象,该 ACL 只需存储一次。

### 7.2. 搜索数据库

Active Directory( AD )数据库通常使用轻型目录访问协议( Lightweight Directory Access Protocol ,LDAP )筛选器进行搜索。你提供给 AD 的 LDAP 筛选器会由查询处理器转换为实际从目录信息树( Directory Information Tree ,DIT )中查找和检索记录所需的命令。用于构造 LDAP 筛选器的语言简单得令人惊讶，本节将介绍从目录中取出数据需要做些什么。

你可以使用任意数量的工具来实际执行搜索。我们推荐 [AdFind](http://bit.ly/10zCBE7) 以及 Windows 附带的 LDP。我们在第 3 章中介绍了 LDP，因此这里假定你在使用 LDP 之前已花几分钟复习了第 3 章。

#### 筛选器运算符

最基本的查询只是要求 AD 返回所有包含特定值属性的对象。例如，如果要返回会计部门中的所有对象，可以使用以下筛选器：`(department=Accounting)`。这里我们指定了属性名 `department` 和值 `Accounting`。除了相等（`=`）运算符之外，还有许多其他运算符可以利用。常用运算符如表 7-1所示。

表 7-1. LDAP 筛选器运算符

| 运算符 | 描述              |
| -------- | ------------------------ |
| `=`      | 等于                 |
| `<=`     | 小于或等于    |
| `>=`     | 大于或等于 |
| `!`      | 非（取反）           |

当你搜索已锁定的账户时，可能就会用到表 7-1中所示的大于或等于运算符。你可以构造诸如 `(pwdLastSet>=1)` 之类的筛选器，以查找至少设置过一次密码的对象。否定或非运算符可用于查找一组不匹配给定条件的对象。例如，如果要查找所有不在会计部门中的对象，可以搜索 `(!(department=Accounting))`。

> **注意**：

使用 `!` 运算符时，活动目录( Active Directory )需要扫描整个数据库以查找符合筛选条件的对象，即使所搜索的属性(如 `department` )已建立索引也不例外。在开发查询时，应考虑这一限制，以确保获得最佳性能。

除了表 7-1中列出的运算符外，您还可以使用 `*` 字符来查找具有特定属性值的任何对象。例如，筛选器 `(description=*)` 将返回目录中所有为 `description` 属性设置了值的对象。相反，筛选器 `(!(description=*))` 将返回任何未为 `description` 属性填充值的对象。

您还可以使用 `*` 字符执行通配符匹配和中间搜索。在通配符搜索的情况下，您可以执行 `(givenName=a*)` 搜索，以查找名字以字母 *A* 开头的所有对象。如果您想查找职位名称中包含字符串 *vice*(如副总裁)的所有对象，可以执行 `(title=*vice*)` 搜索。这称为中间搜索( medial search )。

#### 连接筛选器组件

我们目前所看到的示例都相当简单，它们只是针对单个属性搜索单个值或条件。但实际上，你不太可能经常遇到如此简单的需求。相反，你很可能需要将多个筛选器组合起来，构成布尔 AND 或布尔 OR 表达式（或两者兼有）。表 7-2 列出了可用于实现这一目标的运算符。



表 7-2. 布尔运算符

| 运算符 | 说明 |
| -------- | ----------- |
| `&`      | 布尔 AND |
| `|`      | 布尔 OR  |

上一节中，我们搜索了会计部门中的所有对象。除了用户之外，`(department=Accounting)` 筛选器还会返回其他具有该 `department` 属性值的对象类型，例如联系人和组。为了将搜索范围限定为仅返回会计部门中的用户，我们需要指定要筛选的对象类。为此，我们可以使用类似 `(&(objectClass=user)(department=Accounting))` 的筛选器。这里，我们向 Active Directory 请求的是类为 `user` 且 `department` 值为 `Accounting` 的对象。

我们也可以用同样的方式使用 OR 运算符。例如，如果你想查找隶属于会计部门或市场部门的对象，可以执行 `(|(department=Accounting)(department=Marketing))` 搜索。

最后，如果你想把搜索范围限定为在会计部门或市场部门工作的用户，可以同时使用 AND 和 OR 运算符。为此，你可以使用这样的筛选器：`(&(objectClass=user)(|(department=Accounting)(department=Marketing))`。按线性顺序阅读时，这可能有点难以理解。处理复杂 LDAP 筛选器的一个技巧是将其展开为多行并缩进，类似下面这个示例：




```
(&
    (objectClass=user)
    (|
          (department=Accounting)
          (department=Marketing)
    )
)
```


这里我们构造的是同一个筛选器，但通过将每个组件放在单独一行并缩进表达式，使其可读性大大提高。如果你有一个复杂的查询，想快速将其整理成更易读的格式，可以使用 AdFind。要格式化前面的查询，可以运行以下命令：




```
adfind -filterbreakdown
 (&(objectClass=user)(|(department=Accounting)(department=Marketing))
```


再举一个示例，展示将 AND 和 OR 运算符与 NOT 运算符叠加使用的另一种复杂查询，请看下面这个例子：




```
(|
    (&
          (objectClass=user)
          (|
               (department=Sales)
               (department=Marketing)
          )
          (!
               (employeeType=Contractor)
          )
    )
    (&
          (objectClass=contact)
          (|
               (company=Coho Vines)
               (company=Tailspin Toys)
          )
    )
)
```

在此查询中，我们要求 Active Directory 返回满足以下条件的对象：

- 位于 Sales 或 Marketing 部门的用户。
- 来自 Coho Vines 或 Tailspin Toys 公司的联系人对象( Contact Object )。

供参考，此查询写成一行时如下：`(|(&(objectClass=user)(|(department=Sales)(department=Marketing))(!(employeeType=Contractor))(&(objectClass=contact)(|(company=Coho Vines)(company=Tailspin Toys))))`。

#### 搜索基点( Search Base )

在 LDAP 搜索中,你可以指定一个*搜索基点*( search base ),以告知 Active Directory 从层次结构中的哪个位置开始搜索。搜索范围共有三种类型:基级( base )、单层级( one-level )和子树级( subtree ),如图 7-4 所示。默认情况下,通常执行的是子树搜索。




![Search bases](./image/7.%20Searching%20Active%20Directory/httpatomoreillycomsourceoreillyimages1663388.webp)


图 7-4. 搜索基点

子树搜索会查找指定搜索基点下的每一条记录。如果指定单层级搜索,则只会返回特定搜索基点(例如某个组织单位)直接下辖的记录,其中也可能包括搜索基点本身。而基级搜索只返回所指定的那一个对象。

如果你花点时间回顾一下图 7-1,就会发现 PDNT(父 DNT)和 Ancestors 这两列是如何让这些搜索变得高效的,因为 Active Directory 可以依据这些值进行筛选。

要用 AdFind 指定搜索基点,请使用 *-b* 参数。如果你想对 People OU 中的用户执行子树搜索(默认方式),可以使用以下语法:




```
adfind -f "(objectClass=user)" -b "OU=People,DC=cohovines,DC=com"
```


如果你只想对 USA OU 根部的用户执行单层级搜索,可以使用类似下面这样的语法(全部写在一行):




```
adfind -f "(objectClass=user)" -b "OU=USA,OU=People,DC=cohovines,DC=com" 
  -s onelevel
```

#### 使用 LDAP 控件修改行为

除了直接提交 LDAP 查询之外，您可能还想修改域控制器( Domain Controller ,DC )返回结果的方式。通常，您可以通过使用 *LDAP 控件( LDAP Controls )* 来执行这些修改。LDAP 控件是会话选项，通过 LDAP 协议作为查询的一部分发送。请求中的控件以唯一对象标识符( object identifier ,OID )字符串的形式表示。您可以使用 LDAP 控件执行常见任务，例如在服务器上对结果集( Result Set )排序、对结果集分页等。

大多数情况下，您实际上可能并未意识到在进行查询时已加载了 LDAP 控件。例如，AdFind 通常会包含启用分页结果集的 LDAP 控件。以下列表列出了 Active Directory 支持的许多与搜索相关的 LDAP 控件，以及如何将较常用的控件与 AdFind 一起使用：

- **`LDAP_PAGED_RESULT_OID_STRING` (1.2.840.113556.1.4.319)**

  指定此 LDAP 控件会告知域控制器它可以返回超过单页所能容纳数量的结果。这在搜索大型结果集时很有用，通常应始终包含在 Active Directory 搜索中。

- **`LDAP_SERVER_DIRSYNC_OID` (1.2.840.113556.1.4.841)**

  DirSync 是一项 LDAP 功能，允许您向 Active Directory 请求给定命名上下文( Naming Context )中自上次执行搜索以来发生更改的所有对象。更改通过服务器返回的 Cookie 进行跟踪。DirSync 控件仅返回修改过的属性。如果希望当对象的任何属性已修改时返回完整对象，并且运行的是 Windows Server 2012 或更高版本，请改用此控件的 `LDAP_SERVER_DIRSYNC_EX_OID` (1.2.840.113556.1.4.2090) 版本。Microsoft Forefront Identity Manager (FIM) 等应用程序使用 DirSync LDAP 功能来跟踪更改。有关此功能的详细信息，请参阅[此链接](http://bit.ly/11pKMDX)。

- **`LDAP_SERVER_DOMAIN_SCOPE_OID` (1.2.840.113556.1.4.1339)**

  为确保域控制器不返回对其他服务器上存储的结果集的引用( Referral )，请在请求中包含此 LDAP 控件。

- **`LDAP_SERVER_EXTENDED_DN_OID` (1.2.840.113556.1.4.529)**

  启用此 LDAP 控件后，Active Directory 会将每个结果的 SID 和 `objectGUID` 作为结果集中对象 DN 的前缀返回。有关详细信息，请参阅[此链接](http://bit.ly/ZZKTUa)。

- **`LDAP_SERVER_GET_STATS_OID` (1.2.840.113556.1.4.970)**

  这个极为实用的 LDAP 控件可指示 Active Directory 返回查询处理器将如何执行所请求搜索的统计信息,以及结果的性能统计信息。本章稍后会详细讨论此功能。

- **`LDAP_SERVER_NOTIFICATION_OID` (1.2.840.113556.1.4.528)**

  指定此控件后,在请求的对象被修改之前,Active Directory 不会返回结果。这对于跟踪目录中特定对象的更改并对其做出响应很有用。有关详细信息,请参阅[此链接](http://bit.ly/YKqVeY)。

- **`LDAP_SERVER_RANGE_OPTION_OID` (1.2.840.113556.1.4.802)**

  与前面提到的分页结果控件类似,通常您始终需要指定此控件。当您需要检索多值属性中超过域控制器( Domain Controller ,DC)默认返回的最大值数量的值时,可使用范围结果控件。您可以使用此 LDAP 控件的替代实现 `LDAP_SERVER_RANGE_RETRIEVAL_NOERR_OID` (1.2.840.113556.1.4.1948),以确保在请求的值超出可用数量时不返回错误。

- **`LDAP_SERVER_SD_FLAGS_OID` (1.2.840.113556.1.4.801)**

  使用此控件可告知域控制器检索对象 `ntSecurityDescriptor`(即访问控制列表( Access Control List ,ACL))的哪些组件。根据执行查询的用户的权限,ACL 的某些组件可能无法读取。有关详细信息,请参阅[此链接](http://bit.ly/14hwg5y)。

- **`LDAP_SERVER_SEARCH_OPTIONS_OID` (1.2.840.113556.1.4.1340)**

  此通用控件最实用的功能称为*虚拟根*( phantom root )。虚拟根功能使您能够搜索全局编录( Global Catalog ,GC)上托管的所有命名上下文( Naming Context ,NC)(应用程序 NC 除外)。如果您的多域林具有互不相连的命名空间,可使用此控件一次性搜索所有域。在 AdFind 中,使用 *-pr* 开关启用此功能。

- **`LDAP_SERVER_SHOW_DELETED_OID` (1.2.840.113556.1.4.417)**

此控件指示域控制器将已删除对象和墓碑包含在结果集中。如果已启用活动目录回收站，则仅包含当前可恢复的对象。若要包含已从回收站移出的对象，还必须包含 `LDAP_SERVER_SHOW_RECYCLED_OID` (1.2.840.113556.1.4.2064) 控件。活动目录对已停用的链接值（指向回收站中对象的链接）的处理方式有所不同。如果希望在结果中包含已停用的链接，请添加 `LDAP_SERVER_SHOW_DEACTIVATED_LINK_OID` (1.2.840.113556.1.4.2065) 控件。若要在 AdFind 中包含已删除对象，请追加 *-showdel* 开关。如果还希望包含已从回收站移出的对象，请同时追加 -showrecycled 开关。若要包含已停用的链接，请追加 *-showdelobjlinks*。

- **`LDAP_SERVER_SORT_OID` (1.2.840.113556.1.4.473)**

  此控件指示服务器在返回结果集之前，基于某一属性对结果进行排序。您可以使用 *-sort* 和 *-rsort*（反向排序）参数，通过 AdFind 请求对搜索结果进行排序。[本文档](http://bit.ly/Y49LNX)提供了关于排序的更多详细信息，特别是关于结果集的语言特定排序以及日语域控制器上的语音排序功能。警告当排序所依据的属性未编制索引时，服务器端排序需要在活动目录数据库中使用临时表。临时表的大小有限。因此，对包含未索引属性的大型结果集进行服务器端排序，很可能因临时表的大小限制而失败。

- **`LDAP_CONTROL_VLVREQUEST` (2.16.840.1.113730.3.4.9)**

  虚拟列表视图（ Virtual List View ，VLV）搜索适用于以类似于滚动浏览通讯簿或电话簿的格式分页浏览的大型搜索。事实上，某些版本的 Microsoft Exchange 使用 VLV 来构建电子邮件客户端中显示的通讯簿。有关详细信息，请参阅[此链接](http://bit.ly/Z7Y1sw)。

- **`LDAP_SERVER_ASQ_OID` (1.2.840.113556.1.4.1504)**

  当您希望基于链接属性的值执行查询时，属性范围查询（ Attribute Scoped Query ，ASQ）非常有用。例如，您可能希望返回名为 *All Users* 的组中的所有成员用户。您可以使用 AdFind 通过以下语法实现此目的：` adfind -asq member -b "cn=All Users,ou=Groups,dc=cohovines,dc=com"   -f "objectClass=user"`

对于前文列表中未借助 AdFind 演示的 LDAP 控件( LDAP Control ),可以改用 LDP 来测试其中的许多控件。大多数情况下,请依次单击"浏览"( Browse )→"搜索"( Search ),然后单击"选项"( Options )。在"选项"界面中单击"控件"( Controls ),如图 7-5 所示。在屏幕左侧完成控件的配置后,单击"登记"( Check In )按钮即可将该控件添加到请求中。虚拟列表视图( Virtual List View ,VLV)搜索可通过"浏览"( Browse )→"虚拟列表视图"( Virtual List View )下的专用 VLV 选项来执行。




![LDP Controls dialog](./image/7.%20Searching%20Active%20Directory/httpatomoreillycomsourceoreillyimages1663389.webp)


图 7-5. LDP"控件"对话框

### 7.3. 属性数据类型

某些类型的属性比我们目前所见的属性更难处理。这些类型的属性包括日期和时间（例如 `pwdLastSet` 属性）以及位掩码（例如 `userAccountControl` 属性）。活动目录( Active Directory )支持查询这些属性，只是需要额外花费一点功夫。



#### 日期和时间

当您需要查找密码已过期的用户，或查找在某个时间点之前创建的对象时，就需要处理活动目录存储时间的格式。这些格式因属性而异。最常见的两种是 64 位 NT `FILETIME` 格式，以及更符合标准的通用时间语法。

NT `FILETIME` 是一种整数，表示自 1601 年 1 月 1 日以来经过的 100 纳秒间隔数。而通用时间则以一种更易读的格式存储时间戳：*`YYMMDDHHMMSS[.fffZ]`*。该格式依次为年、月、日、时、分、秒。可选的三位小数值表示秒的小数部分。末尾的 `Z` 表示该时间为协调世界时( Universal Time )或*祖鲁时间( Zulu Time )*。如果没有 `Z`，则表示本地时间。

为筛选条件编码时间值时，可以采用几种方式。对于 `pwdLastSet` 这类以 `FILETIME` 格式存储的属性，您可以请 AdFind 替您完成转换。例如，若要检索所有密码最后更改时间早于 2012 年 10 月 1 日的计算机，可以使用以下 AdFind 命令：




```
adfind -f "(&(objectClass=computer)(pwdLastSet<={{LOCAL:2012/10/01-12:00:00}}))"
 -binenc
```


如果您使用 AdFind 以外的工具执行搜索，则需要提前转换时间戳。您可以使用 Windows PowerShell 执行转换：*[DateTime]::Parse("10/01/2012").ToFileTime()*。得到结果后（在此例中为 `129935412000000000`），按如下方式构造筛选条件：




```
(&(objectClass=computer)(pwdLastSet<=129935412000000000))
```


针对 `whenCreated` 和 `whenChanged` 等通用时间属性的搜索，应使用前述语法（*`YYMMDDHHMMSS.fffZ`*）进行格式化。

返回结果时，所用的格式将与活动目录要求提供值的格式相同。使用 AdFind 时，可以用 *-tdcs* 参数解码 `FILETIME` 字段（例如 `pwdLastSet`），用 *-tdcgts* 参数解码通用时间字段（例如 `whenChanged` 和 `whenCreated`）。

与使用 PowerShell 将值转换为 `FILETIME` 格式类似，您也可以运行以下命令将 `FILETIME` 转换回可读格式：*[DateTime]::FromFileTime(129935412000000000)*。

#### 位掩码( Bit Mask )

在搜索筛选器( Search Filter )中使用位掩码的最常见示例，无疑是查找已启用或已禁用的用户。该标志位记录在 `userAccountControl` 属性的第二位。活动目录( Active Directory ,AD)在 LDAP 筛选器中支持两种特殊匹配规则( Special Matching Rule )，用于在筛选器中执行 AND 和 OR 运算。

例如，要查找已禁用的用户，请使用以下筛选器：




```
(&
    (objectCategory=person)
    (objectClass=user)
    (userAccountControl:1.2.840.113556.1.4.803:=2)
)
```


相反，要查找已启用的用户，需要使用 NOT 运算符：




```
(&
    (objectCategory=person)
    (objectClass=user)
    (!
          (userAccountControl:1.2.840.113556.1.4.803:=2)
    )
)
```




> **注意**：

通过在该筛选器中指定 OID `1.2.840.113556.1.4.804`，即可使用 OR 运算符。

如果使用 AdFind，可以通过 *-bit* 参数大幅简化这些搜索。更具体地说，可以执行以下命令查找所有已禁用的用户：




```
 adfind -f
  "(&(objectCategory=person)(objectClass=user)(userAccountControl:AND:=2))" -bit
```




#### 链内匹配规则( In-Chain Matching Rule )

最后值得一提的一个 LDAP 筛选器技巧是*链内匹配规则*。此修饰符可要求 Active Directory 沿组的成员身份链向前或向后遍历，以确定用户所属的所有组，或判断用户是否间接属于某个组（例如，通过组嵌套( Group Nesting )）。

链内匹配规则的使用方式与前面讨论的 AND 和 OR 运算符匹配规则非常相似。例如，要查明用户是否是 *Important People* 组的成员，可对用户的 `memberOf` 属性执行基础搜索( Base Search )。可以使用 AdFind，通过类似以下语法执行此操作（全部写在一行）：




```
adfind -s base -b "cn=Brian,OU=People,DC=cohovines,DC=com" `
  -f (memberof:INCHAIN:=(cn=Important People,OU=Groups,DC=cohovines,DC=com)) `
  -bit
```


也可以执行实际上相反的操作，使用类似搜索返回用户 *Brian* 直接或间接所属的所有组：




```
adfind -f (member:INCHAIN:=(cn=Brian,OU=People,DC=cohovines,DC=com)) -bit
```


AdFind 中的 `INCHAIN` 快捷方式只是代替了实际的匹配规则 OID：`1.2.840.113556.1.4.1941`。

### 7.4. 优化搜索

至此，我们已经探讨了通过 LDAP 请求 Active Directory 返回数据的多种方式。此任务中一个尚未探讨但非常重要的方面是性能。提交一个使域控制器( Domain Controller ,DC)不堪重负的搜索，显然会适得其反。然而，经验丰富的 Active Directory 管理员不可避免地会讲述不止一个事件，其中域控制器因某个应用程序而瘫痪。该应用程序通过低效查询产生了巨大负载，导致服务器的 CPU 资源被完全耗尽。

#### 高效搜索

至少，高效搜索归根结底在于了解筛选器( Filter )是否会使用索引( Index )，以及服务器能否快速找到满足请求的结果这一实际可行性。*索引*是高效搜索的关键组成部分。索引是一种数据库级功能，使服务器能够快速找到与某个值匹配的结果。如果没有可用的索引，服务器必须扫描整个数据库，以查找与请求匹配的行。

在第 5 章中，我们详细讨论了如何为属性( Attribute )编制索引，以及可用的不同索引类型。为简便起见，我们在表 7-3中复现了第 5 章中某个表的一部分，其中详细说明了可添加到属性的不同索引类型。

表 7-3. searchFlags 位

| 位编号 | 值       | 描述                                                  |
| ---------- | ----------- | ------------------------------------------------------------ |
| 1          | 1 (0x0001)  | 为该属性创建索引。所有其他基于索引的标志也需要启用此标志。将链接属性( Linked Attribute )标记为要编制索引不会产生任何效果。 |
| 2          | 2 (0x0002)  | 在每个容器( Container )中为该属性创建索引。这仅对单级 LDAP 查询有用。 |
| 6          | 32 (0x0020) | 创建元组索引( Tuple Index )。元组索引对中间搜索( Medial Search )有用。中间搜索的通配符位于搜索字符串的开头或中间。例如，中间搜索 (`drink=*coke`) 将匹配 Cherry Coke、Diet Coke 等。 |
| 7          | 64 (0x0040) | 创建子树索引( Subtree Index )。此索引旨在提高虚拟列表视图( Virtual List View ,VLV )查询的性能。 |

一般来说，最常添加的索引类型是表 7-3 中列出的第一种标准索引。如果要执行中间搜索，应考虑添加元组索引(第 6 位)。诸如 `(title=``*vice*)` 的中间搜索会查找职务名称中包含 *vice* 一词的任何对象(例如副总裁)。

如果你是域管理员( Domain Administrator )，或者在目标域控制器( Domain Controller ,DC)上拥有调试特权，则可使用 `stats` LDAP 控件。访问 `stats` 控件的最佳方式是使用 AdFind 并结合 *-stats+* 开关。

> **注意**：

请确保在提升权限的命令提示符下运行 AdFind，以便使用 `stats` 控制。

`stats` 控制将在输出中提供多个数据点，包括用于处理搜索的索引、必须单独扫描的记录数（与返回的记录数相比），以及计时信息。请考虑以下针对运行 Windows XP 的计算机进行搜索的输出：




```
Statistics
=================================
Elapsed Time: 156 (ms)
Returned 1267 entries of 3630 visited - (34.90%)

Used Filter:
 ( & (objectClass=computer) (operatingSystem=*XP*) )

Used Indices:
 idx_objectClass:3798:N

Pages Referenced          : 83092
Pages Read From Disk      : 1
Pages Pre-read From Disk  : 0
Pages Dirtied             : 0
Pages Re-Dirtied          : 21
Log Records Generated     : 0
Log Record Bytes Generated: 0


Analysis
---------------------------------
Hit Rate of 34.90% is Ok

Indices used:

Index Name  : idx_objectClass
Record Count: 3798  (estimate)
Index Type  : Normal Attribute Index


Filter Breakdown:

(
 (&
   (objectClass=computer)
   (operatingSystem=*XP*)
 )
)
```


从这个列表中，我们可以了解到关于所提交搜索查询的很多信息：

- **Elapsed Time**

  域控制器处理搜索花了多长时间？

- **Returned X entries of Y visited**

  这告诉我们域控制器必须扫描多少条记录，与实际返回的结果数相比。这里的百分比低表明我们的查询没有良好的索引覆盖。

- **Used Indices**

  使用了哪些属性索引来筛选结果集？在本例中，域控制器根据 `objectClass` 索引对域中的所有计算机对象筛选结果。一旦使用了该索引，域控制器就必须扫描每台计算机，以检查其 `operatingSystem` 属性是否与搜索筛选器匹配。

- **Pages Referenced, etc.**

  这些统计信息告诉我们检查了多少个数据库页（4 KB 存储单元）。Pages Read From Disk 指标告诉我们有多少数据缓存在 RAM 中。在本例中，几乎所有数据都缓存在 RAM 中，这大大提高了搜索速度。

希望您能从本例中看到，在调整查询时，`stats` 控制有多么有价值。返回的数据告诉您，仅通过索引就能定位多少百分比的数据，以及必须逐条评估多少记录。引用的页数和从磁盘读取的页数统计信息可以很好地反映与硬件相关的性能。在本例中，几乎所有结果集都已经缓存在内存中，从而带来了更好的性能。

在这个示例中，域相对较小，只有几千台计算机。在大型域中，此查询的处理时间会长得多，而在 `operatingSystem` 属性上添加元组索引可能会提高性能。

建议您花几分钟时间,在启用 `stats` 控件的情况下运行本章中的示例查询。观察查询结果,并思考查询的各个组成部分可能如何影响了活动目录( Active Directory )的处理选择。在思考这一问题时,请回顾本章前面关于活动目录数据库结构的讨论。

#### objectClass 与 objectCategory 的对比

坊间流传着一个可追溯至 Active Directory 早期时代的误解，其核心问题是：为何 `objectClass` 属性直到 Windows Server 2008 才默认建立索引。最初人们认为，为多值属性（如 `objectClass`）建立索引会导致性能低下。因此，Windows 2000 发布时，`objectClass` 属性未建立索引，同时新增了一个名为 `objectCategory` 的单值属性并为其建立了索引。

这一决定也引发了许多与仅使用 `objectClass` 属性的查询相关的性能问题，于是大量的建议涌现出来，主张查询应始终同时使用 `objectClass` *和* `objectCategory` 属性，以确保获得最佳性能。如果你希望确保查询在所有版本的 Active Directory 上都能良好执行，我们建议你同时使用 `objectClass` 和 `objectCategory`。如果你已在目录中为 `objectClass` 建立了索引，或者你所有的域控制器( Domain Controller ，DC )都运行 Windows Server 2008 或更高版本，那么你可以放心地单独使用 `objectClass`，无需担心性能方面的负面影响。

### 7.5. 小结

在本章中，我们介绍了用于从 Active Directory 检索数据的查询语言：LDAP。首先，我们探讨了数据库的组织结构，为理解 Active Directory 如何检索数据奠定基础；随后，我们深入介绍了 LDAP 筛选器语法以及特殊数据类型的处理方式。最后，我们讨论了性能问题，以及如何向域控制器请求与所提交查询相关的性能信息。所有 Active Directory 管理员在职业生涯中迟早都需要创建目录数据报告或集成应用程序，希望本章内容能帮助您顺利完成这些任务。
