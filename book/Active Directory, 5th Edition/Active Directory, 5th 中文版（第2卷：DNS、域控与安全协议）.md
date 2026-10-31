---
summary: Active Directory（第5版·第2卷），全面剖析Active Directory与DNS集成解析、域控制器架构（可写DC与只读RODC及虚拟化影响），以及Kerberos身份验证、安全协议与托管服务账户。
---



## 第8章 Active Directory 与 DNS

与它的前身 Windows NT 相比，Active Directory 的一大优势在于它依赖域名系统( Domain Name System ,DNS)而非 Windows 互联网命名服务( Windows Internet Naming Service ,WINS)进行名称解析。DNS 是互联网上普遍使用的、基于标准的命名服务。而 WINS 则从未获得业界支持，在许多企业网络中已成为淘汰候选对象。

好消息是，借助 Active Directory，对 WINS 的依赖已被消除；但潜在的坏消息是，Active Directory 对 DNS 基础设施有许多依赖。之所以说"潜在的"，是因为这取决于你的 DNS 环境的灵活性。通常情况下，组织内管理 DNS 和管理 Active Directory 的团队是不同的，由于政治地盘之争或技术冲突，让这两个团队就实施方案达成一致可能很困难。

> **警告**：尽管 Active Directory 不需要 WINS，或者更准确地说，不需要 NetBIOS 名称解析，但其他系统和技术可能需要它。许多管理员急于尝试从其环境中移除 WINS，但一般来说，维护 WINS 基础设施的管理成本远远小于执行 WINS 移除项目所涉及的成本。

本章的目的是让你充分理解 Active Directory 如何使用 DNS，并介绍在组织内设置 DNS 的一些选项。我们会简要涉及一些 DNS 基础知识，但不会深入讨论如何配置和管理 Windows DNS 服务器。有关这些主题的更多信息，我们强烈推荐 Matt Larson、Cricket Liu 和 Robbie Allen 合著的[*DNS on Windows 2003*](http://oreil.ly/DNS_WinServer_2003)(O'Reilly)。

### 8.1. DNS 基础知识

DNS 是一种分层的名称解析系统。它也是已部署的最大的公共目录服务。几乎所有公司都使用 DNS 进行名称解析服务，包括将主机名解析为 IP 地址、将 IP 地址解析为主机名，以及将主机名解析为备用主机名（别名）。DNS 是一项文档完备的标准，自互联网早期便已存在。以下 RFC 涵盖了 DNS 的一些基础知识：

- RFC 1034，“域名——概念与设施”
- RFC 1035，“域名——实现与规范”
- RFC 1912，“常见的 DNS 操作和配置错误”
- RFC 1995，“DNS 中的增量区域传输”
- RFC 1996，“区域变更即时通知机制（DNS NOTIFY）”
- RFC 2181，“DNS 规范澄清”

每位 Active Directory 管理员都必须理解三个重要的 DNS 概念：

- 区域（ Zone ）是 DNS 命名空间中已委派的组成部分。
- 资源记录（ Resource Record ）包含名称解析信息。
- 动态 DNS（ Dynamic DNS ）允许客户端动态添加和删除资源记录。

#### 区域

*区域*是一组分层域名，其根已被*委派*给一台或多台名称服务器。例如，假设 *mycorp.com* 命名空间已委派给名称服务器 *ns1.mycorp.com*。*ns1.mycorp.com* 对其具有权威性的 *mycorp.com* 下的所有域名，都将被视为 *mycorp.com* 区域的一部分。

*mycorp.com* 区域的子集可以委派给另一台服务器；例如，*mycorp.com* 可以将 *subdomain1.mycorp.com* 委派给名称服务器 *ns2.mycorp.com*。此时，*subdomain1.mycorp.com* 便成为其自身的区域，由 *ns2.mycorp.com* 对其具有权威性。

#### 资源记录

*资源记录( Resource Record )* 是域名系统( Domain Name System ,DNS )中的信息单元。区域( Zone )本质上是一组资源记录的集合。有多种资源记录类型，用于定义不同类型的名称查询。表 8-1 列出了一些较常见的资源记录类型。

表 8-1. 常用资源记录类型

| 记录类型 | 名称 | 说明 |
| ----------- | ------------------------- | ------------------------------------------------------------ |
| A           | 地址记录            | 将主机名映射到 IPv4 地址。                          |
| AAAA        | 地址记录            | 将主机名映射到 IPv6 地址。                          |
| CNAME       | 别名记录              | 将别名映射到主机名。                                 |
| MX          | 邮件交换器记录     | 指定域的邮件路由。                         |
| NS          | 名称服务器记录        | 为给定域指定名称服务器。                  |
| PTR         | 指针记录            | 将 IPv4 地址映射到主机名。                          |
| SOA         | 起始授权机构记录 | 包含有关区域的管理数据，其中包括主名称服务器。 |
| SRV         | 服务记录            | 将特定服务（例如 LDAP）映射到一个或多个主机名和端口。 |
| TXT         | 文本记录               | 包含任意文本数据。通常用于利用 DNS 但没有特定 DNS 记录类型的协议。用于垃圾邮件筛选的发件人策略框架( Sender Policy Framework ,SPF )就是一个例子。 |

需要注意的一种重要资源记录是 SRV 记录类型。域控制器( Domain Controller ,DC )和 Active Directory 客户端广泛使用 SRV 记录来定位具有特定服务的服务器。本章后面将更详细地介绍 Active Directory 如何使用这些记录。

同样需要注意的是，SRV 记录依赖于 A 记录。每条 SRV 记录都提供其所代表的每项服务（例如 LDAP）的各种详细信息，包括运行这些服务的计算机。SRV 记录通过维护指向 A 记录的完全限定名称的指针来实现这一点，而这些 A 记录描述了运行服务的计算机。

#### 客户端查找过程

客户端解析域名系统( Domain Name System ,DNS )名称的过程相对简单，但取决于所解析的名称，涉及的跳数可能差异很大。图 8-1 展示了某台计算机使用缓存 DNS 服务器( caching DNS server )（例如来自客户端互联网服务提供商( Internet Service Provider ,ISP )的服务器）解析名称 *www.whitehouse.gov* 时所涉及的跳数。




![Client lookup process](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663390.webp)


图 8-1. 客户端查找过程

图 8-1 所示的查找过程涉及八个步骤：

1. 客户端向其 DNS 服务器发送对 *www.whitehouse.gov* 的请求。
2. 客户端的 DNS 服务器向其中一台根名称服务器( root name server )发出请求，以协助解析该名称。
3. 根名称服务器将客户端转介到 *.gov* 域的名称服务器。
4. 客户端的 DNS 服务器向 *.gov* 名称服务器发出请求，以协助解析该名称。
5. *.gov* 名称服务器将客户端转介到 *whitehouse.gov* 域的名称服务器。
6. 客户端的 DNS 服务器向 *whitehouse.gov* 名称服务器请求 *www.whitehouse.gov*。
7. *whitehouse.gov* 名称服务器返回 *www.whitehouse.gov* 的 A 记录。
8. 客户端的 DNS 服务器将响应返回给客户端。

如你所见，其中涉及多跳。客户端用于解析 Internet 名称的名称服务器通常称为*缓存 DNS 服务器*，因为它们会在一段时间内缓存从其他 DNS 服务器获取的响应副本，以便加快后续查找。根名称服务器与 *.gov* 名称服务器之间，以及 *.gov* 名称服务器与 *whitehouse.gov* 名称服务器之间的链接称为委派( delegation )。我们将在本章后面更详细地讨论委派。简而言之，委派包含将客户端指向负责委派域的名称服务器所必需的名称服务器( Name Server ,NS )记录。

#### 动态 DNS

动态 DNS （ Dynamic DNS ，DDNS）是在 RFC 2136 中定义的一种方法，允许客户端向 DNS 服务器发送请求以添加或删除区域中的资源记录。这一功能的引入极大地提升了 DNS 在大型环境中的支持能力。在 DDNS 出现之前，更新区域的主要手段是直接编辑基于文本的区域文件，或通过供应商提供的图形界面（如 Windows DNS MMC 管理单元）进行操作。

Active Directory 充分利用 DDNS 来减轻维护其所需资源记录的负担。每个域控制器可能关联数十到数百条资源记录，具体数量取决于 Active Directory 站点拓扑的规模。每当站点拓扑发生变化时，一个或多个域控制器可能需要更改先前注册的部分或全部资源记录。正是由于 Active Directory 资源记录的这种动态特性，在大型环境中，手动维护所有记录很容易就需要一名全职员工来完成。有关动态 DNS 安全性的更多信息，请参阅侧边栏保护动态更新安全。



保护动态更新安全

定义动态 DNS 的 RFC 2136 并未提供用于保护客户端更新的安全模型。正如您所料，这是大规模采用的一大严重限制。为解决此问题，RFC 2137《保护动态更新安全》应运而生。遗憾的是，RFC 2137 在实现上并不实用，往往过于复杂。后来，RFC 2535《域名系统安全扩展》定义了一种基于公钥的方法来保护 DNS 请求，通常称为 DNSSEC。随后又制定了 RFC 3007，该文档使 RFC 2137 过时，并更新了 RFC 2535，以提供一种更灵活的方法来保护更新请求。许多 DNS 服务器产品直到最近才开始提供对这些 RFC 的支持，它们能否被广泛采用只有时间才能证明。有关 RFC 2535 和 3007 的更多信息，请查看以下链接：

- http://www.ietf.org/rfc/rfc2535.txt
- http://www.ietf.org/rfc/rfc3007.txt

尽管 Windows Server 2008 支持 RFC 2535 中定义的某些资源记录类型，如 KEY、SIG 和 NXT，但它并未提供完全合规的支持，例如消息签名和验证。

Microsoft 在 Active Directory 中使用访问控制列表( Access Control List ,ACL )来提供安全的动态更新。Active Directory 集成( Active Directory-Integrated )区域( zone )（本章后文将介绍）将其 DNS 数据存储在 Active Directory 中。随后，你可以在 Active Directory 中针对与 DNS 相关的对象设置 ACL，以授予或拒绝安全主体( security principals )添加和/或更新记录的权限。默认情况下，林( forest )中经过身份验证的计算机可以在区域中创建新条目，但只有创建该条目的计算机才允许修改与该条目关联的数据。

> **注意**：可在 http://www.ietf.org/rfc/rfc2136.txt 找到 RFC 2136。

#### 全局名称区域( Global Names Zones )

自 Windows 2000 以来的每个 Windows 版本中，Microsoft 一直持续投入，使某些组织能够更切实地淘汰其 WINS 基础结构。WINS 在某些组织中非常有用，因为它支持短名称解析( short name resolution )——换句话说，与 DNS 不同，你无需指定分层名称即可解析。

可以通过在客户端上配置 DNS 后缀搜索顺序，使用 DNS 缓解此问题：客户端上的 DNS 解析程序会尝试按所列顺序逐个追加每个已定义的 DNS 后缀，从而解析短名称。在拥有众多 DNS 命名空间的大型组织中，此后缀列表可能相当长且难以维护，并且在尝试解析短主机名时还会导致网络流量大幅增加。

Windows Server 2008 引入了称为 *全局名称区域* 的新 DNS 服务器功能，可以配置该功能以通过 DNS 支持短名称解析，而无需在客户端上使用 DNS 后缀搜索列表。任何支持 DNS 解析的客户端都无需额外配置即可使用全局名称区域功能。Windows Server 2008 及更高版本的 DNS 服务器将首先尝试在本地区域中解析查询的名称；如果失败，则会尝试在全局名称区域中解析该名称。

如果你打算在组织中部署 IPv6，全局名称区域可能特别有用，因为 WINS 不支持 IPv6 寻址。在评估是否部署全局名称区域时，请考虑以下事项：

- 你是否正在淘汰 WINS，或计划淘汰它？
- 客户端联系的所有 DNS 服务器是否都运行 Windows Server 2008 或更高版本？Windows Server 2003 及更早版本的 DNS 服务器不实现全局名称区域功能。
- 你能否管理全局名称的静态注册？*不*支持在全局名称区域中动态注册记录，因此你需要手动或通过脚本管理这些注册。
- 你是否需要全局名称区域提供的功能？此功能可能会增加管理开销，因此在投入时间部署它之前，应考虑你是否会从中受益。

> **警告**：尽管 Windows Server 2008 不支持全局名称区域中记录动态注册，但当客户端在其他区域中注册新记录时，它确实会检查唯一性。如果客户端尝试为全局名称区域中已定义的主机名注册新记录，此注册将失败。

部署全局名称区域需分三步进行：

1. 在名为 *GlobalNames* 的 DNS 服务器上创建一个正向查找区域。

2. 对将要承载 *GlobalNames* 区域的每一台 DNS 服务器启用全局名称区域支持：

```
   dnscmd ServerName /config /EnableGlobalNamesSupport 1
```


3. 配置 *GlobalNames* 区域的复制。建议此步骤使用 *ForestDnsZones* 应用程序分区。



> **注意**：若您拥有多个林，并希望维护一个统一的 *GlobalNames* 区域，您需要在其他林中的 *_msdcs*.**`<其他林>`** 区域内配置一个 SRV 记录。此 SRV 记录名为 *_globalnames*，应指向实际承载 *GlobalNames* 区域服务器的 FQDN。

为了其他林中的 DNS 服务器能够识别 `_globalnames` SRV 记录，您需要在其上执行第 2 步操作。

区域创建完毕后，需填充记录以进行名称解析。推荐做法是在 *GlobalNames* 区域中放置 CNAME 记录，并将其别名设置为相关正向查找区域中特定服务器/名称的记录。

### 8.2. DNSSEC

DNS 面临的挑战之一是基础协议中缺乏验证响应真实性和准确性的机制。在客户端计算机与承载特定区域的权威 DNS 服务器之间，通常涉及一个或多个非权威缓存 DNS 服务器。例如，当您在家庭计算机上浏览 *www.whitehouse.gov* 时，您的 DNS 查询很可能会发送到 ISP 的缓存 DNS 服务器。ISP 的 DNS 服务器会递归解析该查询(*www.whitehouse.gov*)，然后将响应返回给您。

DNSSEC 所解决的问题是：如果 ISP 的 DNS 服务器缓存被攻击者投毒会发生什么。如果缓存被投毒，返回的 IP 地址可能并非实际 IP 地址。对于 DNS，客户端无法对返回响应的有效性获得一定程度的保证。DNSSEC 为 DNS 提供了扩展，以确保 DNS 响应的真实性。

> **注意**：如需深入了解 DNSSEC 相关资源，请访问 [http://www.dnssec.net](http://www.dnssec.net/)。

#### DNSSEC 的工作原理是什么？

DNSSEC 依赖于两个关键组件。第一个组件是一条信任链( Trust Chain )，它始于根 DNS 服务器，或者始于部署在内部 DNS 基础设施中的*信任锚( Trust Anchor )*。根 DNS 名称服务器在全球范围内分布，当您要在 Internet 上解析某个名称时，它们负责第一跳。第二个组件是在 DNS 中发布针对单个记录以及整个区域的数字签名。这两个组件结合在一起，使您能够验证给定 DNS 响应的真实性。

验证 DNS 响应真实性的过程可以在两个位置进行。第一个位置是客户端查询以解析名称时所使用的 DNS 服务器。第二个可能的位置是发出查询的计算机上的 DNS 客户端。Windows DNS 客户端(从 Windows 7 和 Windows Server 2008 R2 开始)可识别 DNSSEC，但不执行验证。实际上，这意味着 Windows DNS 客户端依赖上游 DNS 服务器来支持 DNSSEC。如果您考虑使用 DNSSEC 来解析 Internet 上的名称，那么您的 ISP 将需要在其 DNS 服务器上支持 DNSSEC，并且承载您要解析的记录的区域也必须已签名。如果您考虑的是内部 DNS，则可以部署 Windows Server 2012 DNS 服务器和/或 Windows Server 2012 域控制器( Domain Controller ,DC )，以利用 DNSSEC。

##### 资源记录( Resource Records )

域名系统安全扩展( Domain Name System Security Extensions ,DNSSEC )使用多种新的资源记录类型。这些记录类型列于表 8-2。



表 8-2. DNSSEC 记录类型

| 记录类型 | 描述                                                         |
| ----------- | ------------------------------------------------------------ |
| RRSIG       | 存储单个资源记录的数字签名                                   |
| DNSKEY      | 发布对 DNS 数据进行签名时使用的公钥                          |
| DS          | 标识委派 DNS 区域中使用的签名密钥                            |
| NSEC3       | 下一安全响应记录，用于提供经过身份验证的响应，表明某个名称在区域中无法解析（否定响应） |

DNSKEY 记录存储两种公钥：密钥签名密钥( Key Signing Key ,KSK )和区域签名密钥( Zone Signing Key ,ZSK )。KSK 仅用于签署其他密钥，即 ZSK。ZSK 则用于对区域中的记录进行签名。随着时间推移，能够更改用于签署记录的密钥至关重要。Windows Server 2012 提供自动密钥管理，但对于 KSK，当 KSK 更改时，您必须与父区域的所有者协作（例如，*whitehouse.gov* 需要与 .*gov* 的所有者协作）来更新委派签名者( Delegated Signer ,DS )记录。DS 记录包含 KSK 的哈希，用于验证响应的真实性。

##### 查找过程

如果回看图 8-1及相关说明，会发现解析 *www.whitehouse.gov* 这类名称涉及多跳。本章特意选用 *www.whitehouse.gov* 作为示例，因为 *whitehouse.gov* DNS 区域( DNS Zone )已签名并支持域名系统安全扩展( Domain Name System Security Extensions ,DNSSEC)。事实上，在图 8-1的第 7 步中，当 *whitehouse.gov* 名称服务器( Name Server )返回 *www* A 记录( A Record )时，数字签名也会随资源记录签名( Resource Record Signature ,RRSIG )记录一并返回。

验证 *www.whitehouse.gov* A 记录有效性所需的步骤如下：

1. 缓存 DNS 服务器( Caching DNS Server )请求 *whitehouse.gov* 区域的区域签名密钥( Zone Signing Key ,ZSK)的 DNS 密钥( DNS Key ,DNSKEY )记录，以及对应的 RRSIG 记录。
2. *whitehouse.gov* 名称服务器返回 DNSKEY 和 RRSIG 记录。
3. 缓存 DNS 服务器计算 *www.whitehouse.gov* A 记录的哈希。
4. 缓存 DNS 服务器使用 *whitehouse.gov* ZSK 解密 *www.whitehouse.gov* 的 RRSIG 记录，以获得 RRSIG 记录哈希。
5. 缓存 DNS 服务器比较哈希并确保二者匹配。

此时，假设所有检查均通过，我们已对收到的响应完成验证，但仍无法保证其真实性。如果验证过程到此结束，就无法保证 DNS 服务器的缓存没有被无效的 RRSIG 和 DNSKEY 记录一并污染。因此，我们继续：

1. 为了验证响应的真实性，缓存 DNS 服务器请求 *whitehouse.gov* 区域的密钥签名密钥( Key Signing Key ,KSK)。
2. 接下来，通过比较 ZSK 的哈希与 ZSK 的 RRSIG 记录，验证 *whitehouse.gov* ZSK。

> **注意**：与之前不同，区域签名密钥( Zone Signing Key ,ZSK )的 RRSIG 由区域的密钥签名密钥加密。

要完全验证响应，我们需要沿着信任链逐级验证。信任链存在于图 8-1中 DNS 解析过程的逆向路径上：

1. 缓存 DNS 服务器向 *.gov* 名称服务器请求 *whitehouse.gov* 的 DS 记录。
2. *.gov* 名称服务器返回 DS 记录及相应的 RRSIG 记录。
3. 为了验证来自 *whitehouse.gov* 的响应，服务器将 *whitehouse.gov* KSK 的哈希值与 DS 记录中的数据进行比较。

这一验证是可靠的，因为 *.gov* 名称服务器中的 DS 记录是由 *whitehouse.gov* 名称服务器的管理员提供的。稍后我们在配置 DNSSEC 时，你会看到从哪里获取 DS 记录所需的数据副本。遗憾的是，验证尚未结束。我们现在还需要验证从 *.gov* 名称服务器返回的数据的真实性：

1. 缓存 DNS 服务器向根名称服务器请求 *.gov* 的 DS（委派签名者）记录。
2. 根名称服务器返回 DS 记录及相应的 RRSIG 记录。
3. 为了验证来自 *.gov* 的响应，服务器将 *.gov* KSK 的哈希值与根名称服务器返回的 DS 记录中的数据进行比较。

最后，你可能想知道如何验证来自根名称服务器的响应。归根结底，我们需要一个公认的信任点。如果你熟悉公钥基础设施( Public Key Infrastructure ,PKI )和证书，这与 Windows 中的受信任根存储非常类似。DNS 存储信任锚点( Trust Anchor )，其中包含验证根名称服务器以及其他与受信任名称服务器集无关的名称服务器响应所需的数据。

如果你想尝试在启用 DNSSEC 的情况下进行查询，可以使用 Windows 8 和 Windows Server 2012 中新增的 *Resolve-DnsName* PowerShell cmdlet。例如，要解析 *www.whitehouse.gov*，可以运行 `Resolve-DnsName www.whitehouse.gov -DnssecOk`。你将获得类似以下的响应。请注意响应中包含的签名信息：




```
Name                             Type   TTL   Section    NameHost
----                             ----   ---   -------    --------
www.whitehouse.gov               CNAME  0     Answer     www.whitehouse.gov.ed…
www.whitehouse.gov.edgesuite.net CNAME  0     Answer     www.eop-edge-lb.akadns…
www.eop-edge-lb.akadns.net       CNAME  0     Answer     a1128.h.akamai.net

Name        : www.whitehouse.gov
QueryType   : RRSIG
TTL         : 2348
Section     : Answer
TypeCovered : CNAME
Algorithm   : 7
LabelCount  : 3
OriginalTtl : 3600
Expiration  : 8/15/2012 10:23:13 PM
Signed      : 8/12/2012 9:23:13 PM
Signer      : whitehouse.gov
Signature   : {34, 111, 6, 55...}


Name       : a1128.h.akamai.net
QueryType  : A
TTL        : 18
Section    : Answer
IP4Address : 23.62.63.153


Name       : a1128.h.akamai.net
QueryType  : A
TTL        : 18
Section    : Answer
IP4Address : 23.62.63.152


Name      : .
QueryType : OPT
TTL       : 32768
Section   : Additional
Data      : {}
Enforcing DNSSEC Validation
```

如前所述，Windows 中的 DNS 客户端不会在本地对响应执行验证。相反，客户端依赖其 DNS 服务器为其执行验证。配置此功能需要一两个步骤。首先，在客户端 DNS 服务器的属性中，必须确保选中“为远程响应启用 DNSSEC 验证”，如方法 8.8一节中的图 8-16所示。接下来，如果要确保客户端针对某些（或所有）域接收已验证的响应，则需要配置客户端的名称解析策略表( Name Resolution Policy Table ,NRPT)。

配置 NRPT 最简单的方法是使用组策略( Group Policy )。可通过浏览到 *计算机配置\策略\Windows 设置\名称解析策略* 来访问 NRPT。图 8-2显示了 NRPT 中包含一条规则，该规则要求对 *whitehouse.gov* 的 DNS 请求必须已经过验证。




![Name Resolution Policy Table configuration with Group Policy](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663391.webp)


图 8-2. 使用组策略配置名称解析策略表

Windows 无法在本地客户端中执行验证的缺点是，客户端与其 DNS 服务器之间的最后一跳存在漏洞。响应有可能在该最后一跳期间被篡改。因此，要真正实现完整的端到端 DNS 验证，就需要保护最后一跳。此问题的一种可能解决方案是部署 IPSEC，并使用它来验证客户端与 DNS 服务器之间的连接。

#### 为 Active Directory DNS 配置 DNSSEC

到目前为止，我们讨论 DNSSEC 都是在解析互联网名称的语境下进行的。虽然我们讨论的原理完全相同，但 Active Directory DNS 的实现方式略有不同。也就是说，我们将对动态区域进行签名，并将信任锚( Trust Anchor )部署到 Active Directory，而不是依赖前面描述的通过联系父名称服务器进行递归解析的过程。

在完成 DNSSEC 部署之前，你需要将所有 DNS 服务器升级到 Windows Server 2012。Windows Server 2008 R2 DNS 服务器支持 DNSSEC 验证，但不支持 Active Directory 集成的信任锚，也不支持对动态 DNS 区域进行签名。

RRSIG 记录不会存储在 Active Directory 中，因为这会带来大量额外的 Active Directory 复制流量。相反，这些记录会在服务器启动时(以及在记录更新/注册期间)计算，然后存储在内存中。当 DNS 服务器服务启动时，区域中的所有记录都需要进行签名以创建 RRSIG 记录。在大型区域中，这可能需要几分钟时间。根据你选择的哈希算法和密钥长度，速度会有很大差异。这两个因素也会影响 DNS 服务器服务在内存中存储 RRSIG 记录所使用的内存量。

要开始 DNSSEC 签名过程，请右键单击要签名的区域，然后单击 DNSSEC→对区域进行签名。系统首先会询问你是要创建自定义签名参数、复制其他区域的签名参数，还是使用默认值。我们将创建自定义签名参数。

你需要选择一台 DNS 服务器作为该区域的密钥主控服务器( Key Master )，如图 8-3所示。密钥主控服务器负责在请求生成新密钥时或密钥过期时生成新的签名密钥。




![Nominating the DNSSEC key master for the zone](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663392.webp)


图 8-3. 为该区域指定 DNSSEC 密钥主控服务器

接下来，系统会提示你生成一个密钥签名密钥( Key Signing Key ,KSK)，如 图 8-4 所示。KSK 用于对其他类型的签名密钥进行签名。一般来说，除非你有特定的安全要求必须更改默认值，否则你应该能够接受默认值。请记住，使用更长的密钥或更强的加密算法会因数学运算量增加而提高 CPU 要求并延长 DNS 服务器服务的启动时间。

图 8-4 中显示的参数如下：

- **加密算法( Cryptographic Algorithm )**

  这是用于为签名计算的哈希类型。如果需要支持多种算法，你可以定义多个使用不同算法的密钥签名密钥。

- **密钥长度( Key Length )**

  这是组成密钥的位数。选择密钥长度需要在加密强度与计算哈希所需的计算要求之间取得平衡。

- **密钥存储提供程序( Key Storage Provider )**

  这是将存储密钥的位置。对于 Active Directory DNS，你必须使用 Microsoft Software Key Storage Provider。如果你要对静态独立区域进行签名，则可以使用例如硬件安全模块( Hardware Security Module ,HSM)来保护私钥。

- **DNSKEY RRSET 签名有效期( DNSKEY RRSET Signature Validity Period )**

  这是使用此密钥生成的签名有效的时长（以小时为单位）。

- **密钥滚动( Key Rollover )**

  随着时间的推移，你会希望更改用于签名的密钥，以确保它不会被暴力破解攻破。如果要求这样做，Windows Server 2012 将定期自动发布新密钥。如果你滚动更新 KSK，则可能需要协调委派签名者( Delegated Signer ,DS)记录的发布和更新。

![Generating a new key signing key](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663393.webp)


图 8-4. 生成新的密钥签名密钥

您需要配置的下一个密钥是区域签名密钥( Zone Signing Key ,ZSK),如图 8-5 所示。区域签名密钥用于为区域中的 DNS 记录计算数字签名(RRSIG 记录)。图 8-5 中所示的参数与图 8-4 中的参数大致相同。不同之处在于,默认推荐的密钥长度更短,且自动滚动更频繁。默认密钥长度更短是因为 ZSK 的使用频率要高得多(每当创建或更新记录时,或在服务启动时为每条记录)。较短的密钥长度可以减轻 CPU 的影响。较短的密钥长度通过更频繁的滚动来弥补。ZSK 无需在区域之外的任何地方发布,因此 ZSK 滚动涉及的开销要少得多。

![Creating a new zone signing key](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663394.webp)

图 8-5. 创建新的区域签名密钥

接下来,系统将提示您在 NSEC 和 NSEC3 记录之间进行选择,如图 8-6 所示。NSEC 记录用于提供一种真实响应,以否认记录的存在。更具体地说,如果您请求一条记录(例如 *some-record.contoso.com*),但不存在名为 *some-record* 的记录,服务器不会返回错误(错误可能被欺骗),而是以 NSEC 或 NSEC3 记录的形式返回签名响应。一般来说,我们建议使用 NSEC3 而非 NSEC。NSEC 记录的缺点之一是,它们可能引发字典攻击,从而泄露 DNS 区域中的每一条记录。

![Next Secure record configuration](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663395.webp)

图 8-6. NSEC 记录配置

最后,您需要决定是否将区域的信任锚点( Trust Anchor )发布到 Active Directory,如图 8-7 所示。一旦发布信任锚点,所有 DNS 服务器都将开始验证该区域的响应。默认情况下,信任锚点分发处于禁用状态。

> **警告**：除非您对所完成的配置以及环境中客户端和其他 DNS 服务器的配置有充分信心，否则在部署信任锚点之前，建议先在一组有限的 DNS 服务器和客户端上进行测试。




![Configuring trust anchor distribution](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663396.webp)


图 8-7. 配置信任锚点分发

向导将在后续屏幕上提供一份需要存储在父区域 DS 记录中的信息副本。如果您不拥有父区域，且此区域为公共 DNS 区域，则需要将 DS 记录数据提供给父区域的所有者（通常是您的域名注册商）。

最后，向导将在区域首次签名时提供一个进度屏幕。向导完成后，刷新控制台，您将看到类似图 8-8 所示的新记录。DNS 控制台还会在左侧树中该区域上叠加一个锁图标，以指示该区域已签名。




![Signed DNS zone contents](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663397.webp)


图 8-8. 已签名的 DNS 区域内容

如果您想更改该区域 DNSSEC 配置的任何属性，可以通过右键单击该区域并选择 DNSSEC→属性来访问这些安全属性。当您准备好发布信任锚点时，可以勾选“为此区域启用信任锚点分发”，如图 8-9 所示。




![DNSSEC zone properties](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663398.webp)


图 8-9. DNSSEC 区域属性

### 8.3. 域控制器定位器( Domain Controller Locator ,DC Locator )

对于任何环境中的客户端而言，最基本的问题之一就是找到最合适的域控制器( Domain Controller ,DC)来进行身份验证。Windows NT 中的这一过程效率不高，可能导致客户端向位置最不理想的域控制器进行身份验证。在 Active Directory 中，客户端使用 DNS 通过 DC 定位器进程来定位域控制器。为了从较高层面说明 DC 定位器进程的工作原理，我们将描述一个示例：客户端从一个位置移动到另一个位置，并且需要为其所属域查找一台 DC：

1. 原先位于站点 A 的客户端被移动到站点 B。
2. 客户端最初启动时，它认为自己仍在站点 A，因此从缓存中检索其上次使用的 DC——很可能位于站点 A——并继续联系该 DC。
3. 站点 A 中的 DC 收到请求后，判断该 IP 地址属于站点 B，并确定客户端现在应使用为站点 B 提供服务的 DC。如果该服务器不为站点 B 中的客户端提供服务，它将在回复中返回客户端的新站点，并告知客户端自己不是最近的 DC。
4. 然后，客户端将执行 DNS 查找，以找到所有为站点 B 提供服务的 DC。
5. 接着，客户端联系一台为站点 B 提供服务的 DC。此时可能发生三种情况：
   1. 为站点 B 提供服务的 DC 可以响应并对客户端进行身份验证。
   2. 该 DC 可能无法响应（可能已停机），此时客户端将尝试使用站点 B 中的另一台 DC。
   3. 为站点 B 提供服务的所有 DC 都可能无法响应，在这种情况下，客户端将执行 DNS 查找，以找到为该域提供服务的所有 DC，无论它们覆盖哪些站点，并使用其中任意一台 DC 进行身份验证。

要支持高效的 DC 定位器进程，主要需要满足两件事：在 Active Directory 中正确定义站点拓扑( Site Topology )，以及 DNS 中存在所有必要的 Active Directory 相关资源记录。在下一节中，我们将介绍 Active Directory 中使用的资源记录( Resource Record )的用途。

> **注意**：有关 DC 定位器进程工作原理的更详细说明，包括该过程中查询的具体资源记录，请参阅 Microsoft 知识库( Microsoft Knowledge Base ,KB)文章 247811“How Domain Controllers Are Located in Windows”和 Microsoft 知识库文章 314861“How Domain Controllers Are Located in Windows XP”，网址为 [http://support.microsoft.com](http://support.microsoft.com/)。

### 8.4. Active Directory 使用的资源记录

当您将域控制器( Domain Controller ,DC )提升到域中时,会在 *%SystemRoot%\System32\Config\netlogon.dns* 中生成一个文件,其中包含使其在 Active Directory 中正常运行所需的资源记录。

对于 *mycorp.com* 域中名为 *moose.mycorp.com*、IP 地址为 10.1.1.1 的 DC,该文件的内容大致如下所示。我们对文件顺序进行了调整,将用途相似的记录归为一组(请注意,某些行可能因长度而换行):




```
mycorp.com. 600 IN A 10.1.1.1
ec4caf62-31b2-4773-bcce-7b1e31c04d25._msdcs.mycorp.com. 600 IN CNAME 
moose.mycorp.com.
gc._msdcs.mycorp.com. 600 IN A 10.1.1.1
_gc._tcp.mycorp.com. 600 IN SRV 0 100 3268 moose.mycorp.com.
_gc._tcp.Default-First-Site-Name._sites.mycorp.com. 600 IN SRV 0 100 3268 moose.
mycorp.com.
_ldap._tcp.gc._msdcs.mycorp.com. 600 IN SRV 0 100 3268 moose.mycorp.com.
_ldap._tcp.Default-First-Site-Name._sites.gc._msdcs.mycorp.com. 600 IN SRV 0 100
3268
moose.mycorp.com.
_kerberos._tcp.dc._msdcs.mycorp.com. 600 IN SRV 0 100 88 moose.mycorp.com.
_kerberos._tcp.Default-First-Site-Name._sites.dc._msdcs.mycorp.com. 600 IN SRV 0
100
88 moose.mycorp.com.
_kerberos._tcp.mycorp.com. 600 IN SRV 0 100 88 moose.mycorp.com.
_kerberos._tcp.Default-First-Site-Name._sites.mycorp.com. 600 IN SRV 0 100 88
moose.
mycorp.com.
_kerberos._udp.mycorp.com. 600 IN SRV 0 100 88 moose.mycorp.com.
_kpasswd._tcp.mycorp.com. 600 IN SRV 0 100 464 moose.mycorp.com.
_kpasswd._udp.mycorp.com. 600 IN SRV 0 100 464 moose.mycorp.com.
_ldap._tcp.mycorp.com. 600 IN SRV 0 100 389 moose.mycorp.com.
_ldap._tcp.Default-First-Site-Name._sites.mycorp.com. 600 IN SRV 0 100 
389 moose.mycorp.com.
_ldap._tcp.pdc._msdcs.mycorp.com. 600 IN SRV 0 100 389 moose.mycorp.com.
_ldap._tcp.97526bc9-adf7-4ec8-a096-0dbb34a17052.domains._msdcs.mycorp.com. 600 IN
SRV
0 100 389 moose.mycorp.com.
_ldap._tcp.dc._msdcs.mycorp.com. 600 IN SRV 0 100 389 moose.mycorp.com.
_ldap._tcp.Default-First-Site-Name._sites.dc._msdcs.mycorp.com. 600 IN SRV 0 100
389
moose.mycorp.com.
```


尽管看起来可能很复杂,但其实不然。让我们逐一解析这些记录的实际含义,为便于理解,将记录分成几个部分。首先,第一条记录用于域本身:


```
mycorp.com. 600 IN A 10.1.1.1
```


每个 DC 都会尝试为其所在域注册一条指向自身 IP 地址的 A 记录,与前述记录类似。

接下来是以下记录:


```
ec4caf62-31b2-4773-bcce-7b1e31c04d25._msdcs.mycorp.com. 600 IN CNAME
 moose.mycorp.com.
```


这是一条别名或规范名称( Canonical Name ,CNAME )记录。它位于 *_msdcs* 子域下,该子域用于域控制器之间的相互通信。该记录由服务器的 DSA GUID 组成,是服务器本身的别名。当 DC 知道某台服务器的 DSA GUID 并希望确定其 IP 地址时,就会使用此记录。

> **注意**：别名记录( Canonical Name Record ,CNAME)是其他记录的别名。一个 CNAME 可以指向另一个 A 记录( Address Record )，甚至另一个 CNAME。使用 CNAME 的好处在于，当您需要用多个名称指向同一台主机时。

例如，如果您的 Web 服务器可通过 *www.mycorp.com* 访问，并且您还从该 Web 服务器提供 FTP 服务，那么这两个服务的 IP 地址将始终相同。您可以只创建一个 A 记录( *www* )和一个指向 *www* 的 CNAME( *ftp* )，而不是创建两个 A 记录( *www* 和 *ftp* )。

这样做的好处是，如果服务器的 IP 地址发生变化，您只需在一个位置进行更新。

接下来，我们有以下 A 记录：


```
gc._msdcs.mycorp.com. 600 IN A 10.1.1.1
```


仅当域控制器( Domain Controller ,DC)同时也是全局编录( Global Catalog ,GC)服务器时，才会注册此记录。您可以使用 *nslookup* 查询 *gc._msdcs.mycorp.com*，以获取林( Forest )中所有全局编录服务器的列表。

其余的资源记录( Resource Record )均为 SRV 记录( Service Record ,SRV)类型。SRV 记录类型定义于 RFC 2782“A DNS RR for Specifying the Location of Services (DNS SRV)”。完整文本可在 http://tools.ietf.org/html/rfc2782 找到。简而言之，SRV 记录允许您指定网络上用于特定协议的一台或多台服务器。这些记录还允许您为各个协议重新映射端口号，或设置服务器的优先级，从而确定某些服务器的使用顺序。

> **注意**：即便修改了 Active Directory 特定 SRV 记录的端口号，Windows 也不会遵循这些新端口号。

接下来展示一些更多全局编录特定的记录：


```
_gc._tcp.mycorp.com. 600 IN SRV 0 100 3268 moose.mycorp.com.
_gc._tcp.Default-First-Site-Name._sites.mycorp.com. 600 IN SRV 0 100 3268 moose.
mycorp.com.
_ldap._tcp.gc._msdcs.mycorp.com. 600 IN SRV 0 100 3268 moose.mycorp.com.
_ldap._tcp.Default-First-Site-Name._sites.gc._msdcs.mycorp.com. 600 IN SRV 0 100
3268
moose.mycorp.com.
```


关于 SRV 记录，有一点值得注意，即第七个字段，它指定了用于联系该主机上服务的端口。在上述所有情形中，使用的都是 3268，这对应于全局编录端口。你可能也注意到了包含 *Default-First-Site-Name* 的条目。每个全局编录服务器都会注册特定于站点的记录，以便客户端根据其站点成员身份找到最优的全局编录。更多信息，请参阅即将出现的侧边栏 站点覆盖。

接下来的几个 SRV 记录用于 Kerberos 身份验证（端口 88）以及 *kpasswd* 进程（端口 464），该进程允许用户通过 Kerberos 更改密码：


```
_kerberos._tcp.dc._msdcs.mycorp.com. 600 IN SRV 0 100 88 moose.mycorp.com.
_kerberos._tcp.Default-First-Site-Name._sites.dc._msdcs.mycorp.com. 600 IN SRV 0
100
88 moose.mycorp.com.
_kerberos._tcp.mycorp.com. 600 IN SRV 0 100 88 moose.mycorp.com.
_kerberos._tcp.Default-First-Site-Name._sites.mycorp.com. 600 IN SRV 0 100 88
moose.
mycorp.com.
_kerberos._udp.mycorp.com. 600 IN SRV 0 100 88 moose.mycorp.com.
_kpasswd._tcp.mycorp.com. 600 IN SRV 0 100 464 moose.mycorp.com.
_kpasswd._udp.mycorp.com. 600 IN SRV 0 100 464 moose.mycorp.com.
```


站点覆盖

你可以在 Active Directory 站点拓扑中创建不包含域控制器的站点。根据站点链接定义，具有最佳连接的域控制器将为此类站点进行“覆盖”。此功能称为*自动站点覆盖*。

当某个域控制器为某个站点执行覆盖时，它会添加特定于站点的 SRV 记录，将其通告为可以处理该站点中客户端查询的域控制器。要查看特定域控制器正在覆盖的站点列表，请运行以下 *nltest* 命令，将 *`dc01`* 替换为要确定其覆盖范围的域控制器名称：


```
c:\> nltest /dsgetsitecov /server:dc01
```


在某些场景中，你可能会发现有必要通过切换域控制器上的注册表值来禁用自动站点覆盖行为。要禁用自动站点覆盖，请在 `HKLM\System\CurrentControlSet\Services\NetLogon\Parameters` 下创建类型为 `REG_DWORD` 的注册表值 `AutoSiteCoverage`，并将其设置为 **`0`**。分支机构部署尤其常见于这种场景。有关此配置选项的更多信息，请参见[此链接](http://bit.ly/11DW3UV)。

正如全局编录 SRV 记录一样，域控制器所覆盖的任何其他站点可能会有更多特定于站点的 Kerberos 记录。

其余 SRV 记录用于表示特定域和站点的域控制器：


```
_ldap._tcp.mycorp.com. 600 IN SRV 0 100 389 moose.mycorp.com.
_ldap._tcp.Default-First-Site-Name._sites.mycorp.com. 600 IN SRV 0 100 389 moose.
mycorp.com.
_ldap._tcp.pdc._msdcs.mycorp.com. 600 IN SRV 0 100 389 moose.mycorp.com.
_ldap._tcp.97526bc9-adf7-4ec8-a096-0dbb34a17052.domains._msdcs.mycorp.com. 600 IN
SRV
0 100 389 moose.mycorp.com.
_ldap._tcp.dc._msdcs.mycorp.com. 600 IN SRV 0 100 389 moose.mycorp.com.
_ldap._tcp.Default-First-Site-Name._sites.dc._msdcs.mycorp.com. 600 IN SRV 0 100 
389 moose.mycorp.com.
```


需要注意的一条记录是 *_ldap._tcp.pdc._msdcs.mycorp.com*。该条目由充当域 PDC 仿真器的域控制器注册。DNS 中不会注册其他 FSMO 角色。

基于所有这些记录，只需执行简单的 DNS 查询，即可获取 Active Directory 环境的诸多信息。可检索到的信息包括：

- 林( Forest )或特定站点( Site )中的全部全局编录服务器( Global Catalog Server )
- 域( Domain )或特定站点中的全部 Kerberos 服务器
- 域或特定站点中的全部域控制器( Domain Controller ,DC)
- 域中的 PDC 仿真器( PDC Emulator )

#### 覆盖 SRV 记录注册

有时，您可能不希望域控制器( Domain Controller ,DC)或全局编录( Global Catalog ,GC)将其部分或全部记录发布到它们所在的站点( Site )之外，或者可能希望它们完全不发布任何记录。例如，您可能有一些域控制器专用于在域控制器所在站点中运行的应用程序（如 Microsoft Exchange），或者有分支机构的域控制器，或者有专用于仅为备份复制 Active Directory 的域控制器。

您有两个选项可用于配置 SRV 记录注册行为：

- 使用 `DnsAvoidRegisterRecords` 注册表项。有关配置此选项的更多详细信息，请参阅 Microsoft KB 文章 [306602](http://bit.ly/10dtecY)。
- 使用应用于域控制器的组策略( Group Policy )的管理模板中的 NetLogon 系统设置。有关配置此选项的更多详细信息，请参阅 [Active Directory 工具和设置的 DNS 支持](http://bit.ly/16drwvX)。

无论您选择哪种机制，两者都为您提供了指定哪些记录应注册和哪些记录不应注册的选项。在确定采用哪种方式时，请务必考虑可管理性方面，以防以后需要更改设置。

### 8.5. 委派选项

既然我们已经介绍了 Active Directory 使用 DNS 的用途，现在来回顾一些用于设置谁对 Active Directory 相关区域具有权威性的选项。最终，决定归结为是希望现有 DNS 服务器还是其他服务器（如域控制器( Domain Controller ,DC)）对这些区域具有权威性。有许多因素会影响此决定，包括：

- AD 团队与 DNS 团队之间的地盘争夺
- 区域的初始设置和配置
- 区域的支持和维护
- 与现有管理软件和做法的集成问题

我们将结合委派 AD 区域来逐一探讨这些因素。这些选项确实存在其他细微变化，但我们只讨论基本情形。

#### 不委派 AD DNS 区域

任何注重成本的组织的第一反应，都应是确定其现有域名系统( Domain Name System ,DNS)服务器能否作为活动目录( Active Directory ,AD)区域的权威服务器。如果当前 DNS 实现不支持动态更新( Dynamic Update )，就可能需要手动填充每个域控制器( Domain Controller ,DC)所需的所有必要资源记录( Resource Record )。乍看之下，这似乎相当简单，但一旦开始探究相关要求，就会变得绝非如此简单。

##### 政治因素

如果使用现有 DNS 服务器承载 AD DNS 区域，则 Active Directory 管理员可能无法获得与将区域委派给他们并由他们管理时相同级别的控制权。这种职责分离( Separation of Duties )——以及对 DNS 这类关键依赖项缺乏控制——可能会使 AD 管理员难以保证为 AD 提供一定级别的服务。

##### 初始设置和配置

AD 资源记录的初始填充可能非常繁琐，具体取决于你管理资源记录的方式，以及注入新记录的难易程度。例如，域控制器会定期尝试通过动态 DNS( Dynamic DNS ,DDNS)注册其资源记录。由于存在潜在的安全风险，许多组织不允许任意客户端进行 DDNS 更新。因此，你需要配置现有 DNS 服务器，以允许域控制器执行 DDNS 更新。

非 Windows 的 DDNS 实现通常基于 IP 地址限制哪些客户端可以执行 DDNS 注册和更新。考虑到这一点，DNS 管理员需要配置 DDNS，仅允许域控制器更新特定区域，以缓解允许过多客户端更新服务器中任意 DNS 记录所带来的安全风险。这通常不应成为问题，至少在技术层面如此，但你需要确保在添加新域控制器或更改 DC 的 IP 地址时，及时沟通变更并规划好周转时间。

##### 支持与维护

假定现有域名系统( Domain Name System ,DNS )服务器运行稳定且支持良好(多数组织的情况通常如此),那么对于域控制器( Domain Controller ,DC),或尝试通过 DNS 定位 DC 的其他客户端而言,名称解析不应成为问题。

如前所述,DC 资源记录的日常维护可能是个问题。每次在林( Forest )中提升新 DC 时,都需要确保它获准通过动态 DNS( Dynamic DNS ,DDNS )注册其所有记录。这些记录本可手动注册,但鉴于 AD 资源记录的动态特性,就必须以极高的频率进行更新(可能一天多次)。此外,提升一台 DC 还可能导致其他 DC 更新其在 DNS 中需要注册的记录。

还有一种选择:定期以编程方式从每台域控制器检索 *netlogon.dns* 文件,并通过脚本执行 DDNS 更新。在大型环境中,手动方案很可能无法扩展,此时就需要考虑 DDNS 或编程方案。

##### 集成问题

1999 年 Windows 2000 Active Directory 首次发布时,这一问题比现在更严重,但旧版本的 DNS 服务器或管理软件可能不支持 SRV 记录,也不支持区域名或记录名中的下划线(例如 *_msdcs.mycorp.com*)。这种情况下,应优先将 DNS 服务器平台升级到最新版本。

图 8-10 展示了在 AD DNS 区域未委派时,客户端请求过程是多么直接。客户端始终指向它们一直使用的那些 DNS 服务器。

![Active Directory and DNS](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663399.webp)

图 8-10. Active Directory 与 DNS

#### 委派 AD DNS 区域

乍看之下，在现有 DNS 基础设施中支持 AD DNS 区域似乎相当简单，但具体难度可能因环境而异。也许最直接的做法，就是将 Active Directory 将要使用的 DNS 命名空间委派给域控制器( Domain Controller ,DC)，并让它们托管 DNS 区域。如果使用 AD 集成的 DNS 区域，维护工作会变得更加轻松。通过提升域控制器完成区域的初始创建后，记录将存储在 Active Directory 中，并通过复制分发到其他域控制器。

##### 政治因素

组织通常设有集中式 DNS 团队，负责管理和支持名称解析。例如，如果你决定将 AD DNS 区域委派给域控制器，那么客户端名称解析的很大一部分将不再由现有的企业名称服务器完成。这可能会让 DNS 管理员感到不安，而且这种担忧不无道理。请注意，Active Directory 确实允许你非常轻松地将 Active Directory 集成的 DNS 区域中的记录管理权限委派给其他管理员。

##### 初始设置和配置

委派 AD DNS 区域的初始设置很简单。父区域( parent zone )上需要存在名称服务器( Name Server ,NS )记录以及任何必要的粘连记录( glue record )——例如，指向你要委派到的服务器的 A 记录——并指向将成为这些区域权威服务器的服务器。其余配置必须在将要支持 AD DNS 区域的服务器上完成。如果这些服务器是一台或多台运行 Active Directory 集成 DNS 的域控制器，则只需添加 DNS 服务(较新版本的 Windows 允许你在 DC 提升过程中执行此步骤)。

> **注意**：尽管完全可以在域控制器( Domain Controller ,DC )之外的基于 Windows 的 DNS 服务器上运行支持 Active Directory 的 DNS 区域,但考虑到只有将 Windows DNS 运行在域控制器上才能获得增强功能,这样做恐怕没有太大意义。

##### 支持与维护

AD DNS 区域的日常支持与维护工作量极小,尤其是在使用 AD 集成区域的情况下。事实上,由于域控制器可以使用动态 DNS( Dynamic DNS ,DDNS )来更新 DNS,这正是采用此方法的主要优势之一。

##### 集成问题

除非您已经运行 Windows DNS 服务器,否则很可能无法以管理现有 DNS 基础架构的同样方式来管理 AD DNS 区域。图 8-11 展示了如何通过委派 AD DNS 区域,让客户端仍然指向它们目前使用的同一批 DNS 服务器。该方法的一种变体是让客户端指向 AD DNS 服务器并配置转发,详见下一节。

![Client request flow when delegating the AD DNS zones](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663400.webp)

图 8-11. 委派 AD DNS 区域时的客户端请求流

### 8.6. 活动目录集成 DNS( Active Directory-Integrated DNS )

如果您决定将 AD DNS 区域托管在域控制器( Domain Controller ,DC)上,就应该使用 AD 集成区域。本节将介绍使用 AD 集成 DNS 相较于标准主要区域的一些优势。

条件转发( Conditional Forwarding )

条件转发是 Windows Server 2003 及更高版本中提供的一项功能,相比于 Windows 2000 中的转发处理方式,它为管理员提供了更大的灵活性。图 8-12展示了 Windows Server 2003 DNS MMC 管理单元中的转发器配置界面。借助该界面,您可以将本地 DNS 服务器无法处理的所有请求设置为转发至一个或多个 IP 地址。如您所见,我们根据所查询的域名来配置转发:

- 如果查询的是 *foobar.com*,转发至 10.1.1.1。
- 如果查询的是 *example.com*,转发至 10.1.2.1。
- 如果查询的是其他任何区域,转发至 10.1.3.1。

条件转发允许您创建更高效的解析拓扑,尤其适用于使用不相交命名空间的企业网络。它将查询直接发送至负责各个区域的服务器,而非仅使用对 Internet 的递归查询。

Windows Server 2008 通过支持以活动目录复制条件转发器定义的方式,对条件转发器功能进行了大幅改进。而在 Windows Server 2003 中,您需要在每台 DNS 服务器上逐一配置条件转发器,在大型环境中这是一项繁琐的任务,您很可能需要借助脚本来实现自动化。

如今,条件转发器配置已置于 DNS MMC 控制台的显著位置,与正向和反向查找区域文件夹处于同一级别。DNS 服务器上定义的所有条件转发器都会显示在此处,您还可以通过右键单击上下文菜单创建新的条件转发器。图 8-13展示了新的"编辑条件转发器"对话框。请注意屏幕底部的活动目录复制范围选项。




![Forwarders configuration screen in the Windows Server 2003 DNS MMC snap-in](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663401.webp)


图 8-12. Windows Server 2003 DNS MMC 管理单元中的转发器配置界面




![Managing a conditional forwarder in Windows Server 2008](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663402.webp)


图 8-13. 在 Windows Server 2008 中管理条件转发器

在常规的 DNS 世界中，名称服务器( Name Server )分为两种类型：主要名称服务器( Primary Name Server )（有时称为主服务器，即 master）和辅助名称服务器( Secondary Name Server )（又称从服务器，即 slave）。某个区域的主要名称服务器将区域数据保存在主机上的文件里，并从该文件中读取记录条目。每个区域通常只有一个主要名称服务器。辅助名称服务器从对该区域具有权威性的主要名称服务器处获取区域内容。每个主要名称服务器可以有多个辅助名称服务器。辅助名称服务器启动时，会针对其承载的每个区域联系主要名称服务器，并通过区域传送( Zone Transfer )请求相关区域文件的副本。随后，辅助名称服务器上的文件内容会按照既定方案随时间动态更新。这种更新通常是周期性的，或者由主要名称服务器发来的消息自动触发——该消息表明主要名称服务器已收到更新。以上只是一个高度简化的描述，因为每台名称服务器都可以承载多个区域，因此同一台服务器可能对某些区域承担主要角色，而对另一些区域承担辅助角色。

两种类型的服务器都能解析针对其所承载区域的名称查询。但是，如果需要更改 DNS 文件的底层内容，则必须在该区域的主要名称服务器上进行。辅助名称服务器无法接受更新。

Active Directory 和 Windows DNS Server 还提供另一种选择：将 DNS 数据集成到 Active Directory 中。实际上，这意味着可以将区域文件的内容以层次结构的形式存储在 Active Directory 中。将 DNS 与 Active Directory 集成意味着 DNS 结构会在域内的所有域控制器( Domain Controller ,DC)之间复制；每个 DC 都保存一份可写的 DNS 数据副本。存储在 Active Directory 中的 DNS 对象可以在任意 DC 上通过 LDAP 操作更新，也可以通过针对充当 DNS 服务器的 DC 使用动态 DNS( Dynamic DNS ,DDNS)进行更新。这实际上使所有 DC 都如同主要名称服务器一样工作：每个 DC 都可以写入区域，并为该区域给出权威解答。这与"一台主要名称服务器加一台或多台辅助名称服务器"的标准模型相去甚远，后者存在一个明显的缺陷：DNS 更新存在单点故障( Single Point of Failure )。

在 Windows 2000 域控制器( Domain Controller ,DC)上使用集成 DNS( Integrated DNS )时，可能会遇到一个称为“DNS 孤岛( DNS Island )”的问题。Active Directory 需要正确的 DNS 解析才能复制更改，而使用集成 DNS 时，域控制器通过 Active Directory 复制来复制 DNS 更改。这是经典的先有鸡还是先有蛋问题；通过正确配置即可避免。当一台配置为名称服务器( Name Server )的林根域控制器( Forest Root Domain Controller )将其 DNS 解析指向自身时，就会出现此问题。如果该 DC 更改了其 IP 地址，DNS 记录会在本地成功更新。但是，除非其他 DC 将其 DNS 解析指向同一个 DC，否则它们无法解析该 DC 的 IP 地址，因此复制会失败，其他 DC 也不会获得该 IP 地址更改。该林根域控制器实际上已被从林中的其余部分隔离出来，并成为自己的复制孤岛。若要避免此问题，配置为名称服务器的林根域控制器应将其 DNS 解析指向除自身以外的根服务器( Root Server )。

#### 复制影响

尽管与 AD 集成的 DNS 具有诸多优势，但一个潜在的缺点是 DNS 数据在 Active Directory 中的复制方式。在 Windows 2000 中，AD 集成区域存储在域的 System 容器中。这意味着该域中的每个域控制器( Domain Controller ,DC )都会复制该区域数据，无论该域控制器是否为 DNS 服务器。对于不是 DNS 服务器的域控制器而言，复制这些数据没有任何益处。幸运的是，在较新版本的 Windows 中有一个更好的替代方案：使用应用程序分区( Application Partition )，如下一节所述。

> **注意**：如果您最初是在 Windows 2000 下创建 AD 集成 DNS 区域的，它们可能仍通过域中的 System 容器进行复制。

#### 后台区域加载

Windows Server 2008 中新增的一项功能是 DNS 区域的后台加载。在 Windows Server 2008 之前，DNS 服务器服务只有在完成从 Active Directory 加载其托管的所有区域后才会变为可用。在托管大型区域的 DNS 服务器上，加载所有区域可能需要相当长的时间（在某些情况下长达数小时）。通过后台加载，DNS 服务器服务不再等待每个区域加载完毕，而是在后台加载这些区域，并在加载过程完成后立即使其可供查询/更新。



> **注意**：此后台加载行为仅适用于存储在 Active Directory 中的区域。存储在文件系统上的区域仍会在服务可用于处理请求之前按顺序加载。

### 8.7. 使用应用程序分区实现 DNS

如第 4 章所述,应用程序分区( Application Partition )是用户定义的分区,具有自定义的复制范围。只有配置为承载应用程序分区副本的域控制器( Domain Controller ,DC)才会复制该分区中包含的数据。应用程序分区的优势之一是不受域边界的限制。只要域控制器位于同一个林( Forest )中,就可以配置它们复制应用程序分区,即使它们分属完全不同的域。正因如此,应用程序分区非常适合存储 AD 集成 DNS 区域。您不再需要将 DNS 数据存储在域上下文中,并将其复制到域中的每个域控制器——哪怕其中只有少数几台是 DNS 服务器。借助应用程序分区,您可以配置 Active Directory 仅在域或林内运行 DNS 服务的域控制器之间复制 DNS 数据。

每个域和林都有一个默认的应用程序分区。在配置 AD 集成区域时,您有多种存储 DNS 数据的选项。这些选项列于表 8-3中。



表 8-3. Active Directory 集成 DNS 区域存储选项

| 可分辨名称                                                   | 复制范围                                                     |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| `cn=System,`*`<DomainDN>`*示例:`cn=System,dc=amer,dc=mycorp,dc=com` | 复制到域中的所有域控制器。这是 Windows 2000 下唯一可用的存储方式。 |
| `dc=DomainDnsZones,` *`<DomainDN>`*示例:`dc=DomainDnsZones,dc=amer,dc=mycorp,dc=com` | 复制到域中同时充当 DNS 服务器的域控制器。                     |
| `dc=ForestDnsZones,` *`<ForestDN>`*示例:`dc=ForestDnsZones,dc=mycorp,dc=com` | 复制到林中同时充当 DNS 服务器的域控制器。                     |
| `AppPartitionDN`示例:`dc=CampusDnsZones,dc=mycorp,dc=com`   | 复制到已登记复制该应用程序分区的域控制器。                   |

表 8-3中的最后一个选项表明,除了默认的 *DomainDnsZones* 和 *ForestDnsZones* 分区之外,你还可以自定义应用程序分区( Application Partition )。有些组织会选择定义额外的应用程序分区,以控制其他 DNS 区域的复制作用域。例如,你的域控制器( Domain Controller ,DC)可能承载着特定楼宇或园区专用的 DNS 区域,此时你可以定义一个名为 *CampusDnsZones* 的应用程序分区,专门用于承载这些区域。相应地,你只需将该园区内的域控制器配置为承载此应用程序分区,即可限制这些区域的复制作用域。

安装新的 Windows Server 2003 Active Directory 林时,系统会自动创建默认的 DNS 应用程序分区。如果你是从 Windows 2000 升级而来,则可以使用 DNS MMC 管理单元或 *dnscmd.exe* 实用工具手动创建 DNS 应用程序分区。若要使用 DNS MMC 管理单元手动创建 DNS 应用程序分区,请右键单击左侧窗格中的服务器,然后单击"创建默认应用程序目录分区"( Create Default Application Directory Partitions )。创建应用程序分区后,必须逐一修改每个区域的复制作用域,才能利用应用程序分区复制,具体步骤如下:

1. 右键单击要更新的区域,然后单击"属性"。
2. 在"常规"选项卡的"复制"部分旁边,单击"更改"按钮。
3. 选择"到本域中所有在域控制器上运行的 DNS 服务器"(*DomainDnsZones*),或"到本林中所有在域控制器上运行的 DNS 服务器"(*ForestDnsZones*),如图 8-14所示。




![Modifying a DNS zone’s replication scope](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663403.webp)


图 8-14. 修改 DNS 区域的复制作用域

### 8.8. 老化( Aging )与清理( Scavenging )

在客户端能够注册自己记录的 DNS 基础架构中，其复杂性之一在于：随着时间的推移，区域中会为已不存在或可能已更名的客户端积累大量记录。如果网络中只有少量计算机，你可能可以通过 MMC 自行管理这些记录。另一方面，如果有数百台甚至数十万台计算机参与单个 DNS 区域，你很可能无法自行管理这些记录的生命周期。

幸运的是，Windows DNS 实现包含一个称为*清理*的功能，可以提供帮助。清理是一个后台进程，你可以基于每个 DNS 服务器进行配置，用于扫描区域中的所有记录，并删除在特定时间段内未刷新的记录。使用动态 DNS 注册自身的客户端会定期自动刷新其 DNS 注册。Windows DNS 会将此时间戳存储为 DNS 记录的属性。默认情况下，Microsoft DNS 客户端每 24 小时更新和刷新一次其 DNS 注册。

清理配置选项之一是“无刷新间隔( No-Refresh Interval )”，它定义 DNS 服务器接受 DNS 注册刷新并更新 DNS 记录的频率。此功能限制了 DNS 记录时间戳更新所导致的不必要复制量。对于手动创建的记录，刷新时间戳设置为零，从而将该记录排除在清理之外。你还可以编辑动态注册的记录，将其排除在清理之外。

#### 配置清理

配置清理分两步进行：

1. 为特定 DNS 区域启用清理，并定义该区域的刷新间隔。

   > **注意**：如果在 DNS MMC 中右键单击 DNS 服务器节点，会看到一个名为“为所有区域设置老化/清理”的选项，它允许你针对该 DNS 服务器上承载的所有 DNS 区域一次性配置这两个值。

2. 在至少一台承载该区域的 DNS 服务器上启用清理，并定义清理进程的运行频率。

请务必完成这两个步骤。许多管理员会忘记其中一步，然后发现清理并未按预期工作。对于每个已启用清理的区域，只需在至少一台承载该区域的 DNS 服务器上完成步骤 2。有些管理员选择为每台 DNS 服务器配置清理（步骤 2），而另一些管理员则选择仅在特定的域控制器( Domain Controller ,DC)上启用清理进程。通常，直接在每台 DNS 服务器上启用该进程会更简单。

##### 设置区域特定选项

为特定区域启用清理的选项，可通过该区域属性中的“老化”按钮访问（参见图 8-15）。如下一节在 DNS 服务器上启用清理所示，有两个相关配置项：

- **无刷新间隔( No-refresh interval )**

  它表示 DNS 服务器将客户端的时间戳刷新传播到目录或文件系统的频率。默认值为 7 天，通常可以接受。此设置的目的是减少仅因时间戳更新而进行的不必要复制或区域传送活动。

- **刷新间隔( Refresh interval )**

  它表示 DNS 服务器在刷新后必须等待多久，记录才有资格被清理。此处的默认值同样是 7 天。实际上，如果使用此处的默认值，并且客户端在某月的第 7 天刷新其记录，然后离线，则 DNS 服务器不会早于该月的第 14 天清理该记录。

##### 在 DNS 服务器上启用清理




![DNS zone scavenging settings](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663404.webp)


图 8-15. DNS 区域清理设置

要执行清理，必须在一台或多台 DNS 服务器上启用并配置实际的清理过程。一个常见的误解是，认为唯一需要进行的清理配置是在 DNS 区域本身上。

要更改 DNS 服务器清理设置，请在 DNS 管理控制台中访问 DNS 服务器的属性，并选择“高级”选项卡，如图 8-16 所示。您需要启用清理过程，并定义其运行频率的间隔。默认的七天通常是可接受的；但是，您可以将其调整为每小时运行一次。请注意，不要将其设置得过于频繁，以至于 DNS 服务器持续运行清理过程，因为这会适得其反。




![DNS server advanced properties](./image/8.%20Active%20Directory%20and%20DNS/httpatomoreillycomsourceoreillyimages1663405.webp)


图 8-16. DNS 服务器高级属性

### 8.9. 使用 Windows PowerShell 管理 DNS

传统上,若没有一堆复杂的工具搭配使用,想要通过脚本完成涉及 Windows 域名系统( Domain Name System ,DNS)服务器的常见任务一直十分困难。DNS 服务通过 Windows 管理规范( Windows Management Instrumentation ,WMI)公开了多种 API,可从 VBScript 及其他脚本语言中加以访问。而有些任务只能借助 *dnscmd* 命令行工具实现自动化,这就需要进行繁琐的文本抓取与处理。

Windows Server 2012 引入了大量 Windows PowerShell cmdlet,用于管理 Windows Server 2008 及更高版本 DNS 服务器上的 DNS。事实上,有了 Windows Server 2012,你几乎可以用 Windows PowerShell 完成 *dnscmd* 所支持的任何任务。要使 DNS 服务器 cmdlet 可用,并获取用于管理 DNS 的 cmdlet 完整列表,可以使用以下命令:




```
Import-Module DnsServer
Get-Command -Module DnsServer
```


此外,*DnsClient* 和 *DnsConfig* PowerShell 模块提供了管理计算机上的 DNS 配置以及解析名称所需的 cmdlet。*Resolve-DnsName* cmdlet 所具备的功能,以往必须使用 *nslookup* 命令行工具才能实现。

### 8.10. 小结

Active Directory 高度依赖 DNS。事实上，微软已彻底放弃在网络操作系统( Network Operating System ,NOS )中使用 WINS 进行名称解析，转而采用基于标准的 DNS。域控制器定位符( DC Locator )进程是 Active Directory 中一项核心的基于 DNS 的功能，用于帮助域控制器( Domain Controller ,DC )和客户端定位具有特定属性的域控制器，例如位于某个特定站点( Site )中，或者充当全局编录服务器( Global Catalog Server )或 PDC 仿真器( PDC Emulator )。如何管理 AD DNS 区域可能颇为棘手，每种方案都各有优劣。如果将区域委派给域控制器，那么 AD 集成区域( AD-Integrated Zone )可为你省去大量维护与保养工作，还可视需要让你在传统 DNS 管理员与 AD 管理员之间划分 DNS 的管理职责。

---

## 第 9 章 域控制器( Domain Controller ,DC)

本章重点介绍 Active Directory 的基础架构基石——域控制器。域控制器是承载所有 Active Directory 功能与协议的组件。本章将深入探讨部署（提升）新域控制器所需的步骤，以及围绕物理安全( Physical Security )和硬件虚拟化( Hardware Virtualization )的运维注意事项。

确保 Active Directory 域控制器的物理安全，是成功且安全地部署 AD 极为重要的一环。正如 AD 管理员所深知，在许多组织（尤其是大型跨国企业）中，分支机构中托管服务器的场所往往远谈不上安全。只读域控制器( Read-Only Domain Controller ,RODC) 是 Active Directory 针对此问题的解决方案。

硬件虚拟化并非新事物。在 Windows Server 2012 中，Microsoft 解决了诸多技术挑战，并同时引入了快速克隆域控制器的能力，以便横向扩展或满足灾难恢复( Disaster Recovery )需求。

### 9.1. 构建域控制器( Domain Controller ,DC)

部署活动目录( Active Directory ,AD)时，首先要执行的步骤之一就是构建域控制器。根据所部署的域控制器类型以及所采用的方法，该过程可能千差万别。你可能希望部署只读域控制器( Read-Only Domain Controller ,RODC)，或者可能希望使用从媒体安装( Install from Media ,IFM)来减轻网络上的复制负载并快速提升域控制器。将成员服务器( Member Server )转换为域控制器的过程称为*提升*( Promotion )。

#### 使用服务器管理器进行部署

第一步是在要提升为域控制器( Domain Controller ,DC )的服务器上安装 Active Directory 二进制文件。在服务器管理器( Server Manager )中,单击仪表板上的"添加角色和功能"即可完成此操作,如图 9-1所示。继续完成向导操作,并选择要在其上安装 Active Directory 二进制文件的服务器,如图 9-2所示。




![Server Manager Dashboard](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663406.png.webp)


图 9-1. 服务器管理器仪表板

在"选择服务器角色"屏幕上,选择"Active Directory 域服务",如图 9-3所示。服务器管理器会自动找出所选角色的依赖项,并提示你确认是否要安装这些依赖项,如图 9-4所示。继续完成向导的其余步骤,然后单击"安装"以完成该过程。




![Select the destination server](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663407.webp)


图 9-2. 选择目标服务器




![Select server roles to install](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663408.webp)


图 9-3. 选择要安装的服务器角色




![Selected role dependencies](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663409.webp)


图 9-4. 所选角色的依赖项

安装完成后,单击"结果"窗口状态框中的"将此服务器提升为域控制器"链接。这将启动活动目录域服务( Active Directory Domain Services ,AD DS )配置向导。如果你熟悉在 Windows Server 2012 之前的 Windows 版本中提升域控制器的操作,那么该向导正是用于取代 *dcpromo* 的。如果在 Windows Server 2012 上运行 *dcpromo*,将会出现图 9-5所示的错误。




![DCPromo error in Windows Server 2012](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663410.webp)


图 9-5. Windows Server 2012 中的 DCPromo 错误

在本示例中，我们将向现有域( Domain )添加一台额外的域控制器( Domain Controller ,DC)，如 图 9-6 所示。如果您要从头创建新林( Forest )（或新域），则应在 图 9-6 中选择相关选项，而不是默认的“将域控制器添加到现有域”。除向导将询问的几个额外问题外，所有步骤均相同。




![Beginning the AD DS Configuration Wizard](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663411.webp)


图 9-6. 启动 AD DS 配置向导

在 图 9-6 所示的屏幕中，您需要提供具有足够访问权限的凭据，以提升新域控制器。一般来说，这是目标域中的域管理员( Domain Admin )帐户。不过，如果要部署只读域控制器( Read-Only Domain Controller ,RODC)，则可以使用在 Active Directory 中预先创建 RODC 计算机帐户时所用的凭据。

接下来，向导将允许您定义域控制器的关键特征。这些特征包括该 DC 将服务的 Active Directory 站点( Site )，以及目录服务还原模式( Directory Services Restore Mode ,DSRM)密码（在 第 18 章 中讨论）。特别值得关注的是（如 图 9-7 所示），此 DC 是否将承载 DNS、是否将成为全局编录( Global Catalog ,GC)，以及它是否为 RODC。在本示例中，我们将把一台全局编录提升到巴黎站点( Paris Site )中。




![The Domain Controller Options screen](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663412.webp)


图 9-7. 域控制器选项屏幕

在 DNS 选项步骤中，您可能会收到警告，指出无法为 DNS 区域创建委派，如 图 9-8 所示。通常，可以放心忽略此警告。如果您要创建新域或新林，此步骤可以帮助您设置 DNS：它会为您在父 DNS 区域中创建委派。我们在 第 8 章 中讨论了 DNS 委派。如果您在创建新域或新林时跳过此步骤，那么以后如有必要，只需创建新的委派即可。

接下来,如图9-9所示,"其他选项"屏幕允许您选择用于初始复制的源域控制器( Domain Controller ,DC)。如果您需要作为初始复制过程的一部分,控制对其他域控制器的网络影响或负载,这将非常有用。您还可以选择使用从介质安装( Install from Media ,IFM)来加速提升。我们将在第18章深入讨论 IFM。

在下一个屏幕( 图9-10 )上,您将能够指定 Active Directory 数据库、事务日志和 SYSVOL 共享的路径。在本示例中,我们将保留默认值,但这是一个争议颇多的话题。通常,除非您运行的是大型、复杂的 Active Directory 环境,否则坚持使用默认值,或者如果您的策略是不使用系统驱动器存储数据,则简单地将所有路径放在备用驱动器上,可能就足够了。




![DNS delegation warning](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663413.webp)


图9-8. DNS 委派警告




![Replication and IFM settings](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663414.webp)


图9-9. 复制和 IFM 设置




![Data storage paths](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663415.png.webp)


图9-10. 数据存储路径

如果您运行的是更大的环境,您可能需要将这三项分开。Active Directory 数据库主要是一种读取密集型工作负载。通常,对于64位域控制器,如果您能将整个数据库文件缓存在内存中,那么只有在域控制器启动且尚未缓存任何数据时,才会对存储产生较大的读取影响。如果您正在为数据库规划存储,请确保同时考虑数据库的大小以及独立磁盘冗余阵列( Redundant Array of Inexpensive Disks ,RAID)阵列是否能满足读取工作负载的需求。诸如 RAID-5 和 RAID-10 之类的 RAID 类型通常非常适合此类工作负载。

大多数 Active Directory 环境不会对目录产生相应的高变更率。然而,当进行更改时,它们会首先写入事务日志。事务日志永远不会占用太多空间,但在非常繁忙的环境中,它们需要能够跟上写入请求的存储。诸如 RAID-1 和 RAID-10 之类的 RAID 类型通常非常适合事务日志。

最后，SYSVOL 共享( Sysvol Share )主要是一种读取密集型卷。在大量使用组策略( Group Policy )的环境中，SYSVOL 共享可能会占用相当多的空间。ADMX 文件的中央存储( Central Store )功能的出现已在相当程度上帮助缓解了这一问题，但仍应相应地规划存储。更值得考虑的大问题是，SYSVOL 共享可能对 Active Directory 域的整体可用性产生什么影响。

当您委派某个组策略对象( Group Policy Object ,GPO)的控制权时，同时也就授予该管理员在 SYSVOL 中该 GPO 的共享内存储数据的权限。如果被委派的管理员在 SYSVOL 中放入过多数据，以致承载 SYSVOL 的驱动器被填满，就可能会遇到麻烦。可能出现问题的情形是，SYSVOL 与操作系统( OS )安装、Active Directory 数据库或事务日志( Transaction Logs )位于同一驱动器上。如果要委派编辑组策略的访问权限，请考虑将 SYSVOL 放在单独的分区或卷上。

在图 9-11所示的“查看选项”屏幕上，向导以易读的格式汇总您所做的选择。不过，也许更值得一提的是屏幕右下角的“查看脚本”按钮。此按钮提供使用您在向导中选择的选项来提升域控制器( Domain Controller ,DC)所需的 PowerShell 命令。这样，无需尝试弄清使用 PowerShell 提升 DC 所需的所有选项，只需运行一次向导，收集脚本，然后即可快速轻松地使用它构建多个 DC。

![Confirmation and PowerShell script export](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663416.png.webp)

图 9-11. 确认和 PowerShell 脚本导出

向导将检查先决条件，如果服务器通过检查（如图 9-12所示），则可以单击“安装”。单击“安装”后，Active Directory 会将服务器配置为域控制器、执行初始复制，然后自动重新启动。服务器重新启动后，您将拥有一个功能齐全的域控制器。

![Final confirmation](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663417.webp)

图 9-12. 最终确认

#### 在早期 Windows 版本上使用 DCPromo

如果要提升运行 Windows Server 2012 之前 Windows 版本的域控制器( Domain Controller ,DC)，则我们到目前为止讨论的服务器管理器( Server Manager )和 PowerShell 方法将不适用。早期版本的 Windows（可追溯到 Windows 2000）使用名为 *dcpromo* 的工具来安装 Active Directory。您可以通过转到“开始”→“运行”，然后输入 **`dcpromo`** 来启动 *dcpromo*。如果您查看上一节使用服务器管理器部署中的屏幕截图和信息，您会发现 *dcpromo* 向您询问的问题与服务器管理器询问的问题几乎完全相同。

对于 *dcpromo*，我们可以提供的一个提示是：在某些 Windows 版本中，除非以高级模式运行 *dcpromo*，否则诸如“从媒体安装”( Install from Media )之类的选项会被隐藏。为此，请运行 *dcpromo /adv*。

#### 自动化 DC 构建过程

如果要安装大量域控制器，或者只是希望保持一致，可以从 Windows Server 2012 开始使用 Windows PowerShell 自动化构建过程。Active Directory 服务器角色的安装以及提升过程都可以轻松实现自动化。

您要做的第一件事是安装 AD 域服务( AD Domain Services ,AD DS)服务器角色（如果尚未安装）。您可以使用以下 PowerShell 命令完成此操作：

```
Add-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
```

接下来，可以提升域控制器。在以下 PowerShell 命令中，我们根据上一节使用服务器管理器部署中选择的相同参数来提升域控制器：

```
Install-ADDSDomainController `
-NoGlobalCatalog:$false `
-CreateDnsDelegation:$false `
-CriticalReplicationOnly:$false `
-DatabasePath "C:\Windows\NTDS" `
-DomainName "cohovines.com" `
-InstallDns:$true `
-LogPath "C:\Windows\NTDS" `
-NoRebootOnCompletion:$false `
-SiteName "Paris" `
-SysvolPath "C:\Windows\SYSVOL"`
-SafeModeAdministratorPassword ((Get-Credential).Password)
```

> **注意**：在此示例中，系统会提示你输入目录服务还原模式( Directory Services Restore Mode ,DSRM )密码。若要将密码嵌入脚本中，请将 *(Get-Credential).Password* 替换为 *ConvertTo-SecureString -AsPlainText -Force -String “password”*。

若需使用 PowerShell 降级域控制器( Domain Controller ,DC )，可使用 *Uninstall-ADDSDomainController* cmdlet，如下示例所示：


```
Uninstall-ADDSDomainController -LocalAdministratorPassword `
(ConvertTo-SecureString -AsPlainText -Force -String "password") `
-Credential (Get-Credential)
```


`-LocalAdministratorPassword` 参数指定域控制器重启为成员服务器后要设置的本地管理员密码。`-Credential` 参数提供域管理员凭据，用于完成降级操作。

若运行的是早期版本的 Windows（Windows Server 2012 之前），则自动化 DC 构建过程更为复杂。你可以使用无人参与应答文件或 *dcpromo* 的命令行界面。我们通常建议采用应答文件方式，因为 *dcpromo* 的命令行界面并不特别友好。有关应答文件格式的详细信息，请参阅 Microsoft 知识库文章 [947034](http://bit.ly/14mhYAv)。有关从命令行使用 *dcpromo* 的更多信息，请查看[此链接](http://bit.ly/YS3Hng)。

### 9.2. 虚拟化

在微软设计活动目录( Active Directory )时，服务器虚拟化尚未被纳入考量，但随着活动目录的演进及虚拟化技术的应用，一系列问题逐渐浮现。核心问题在于，硬件虚拟化通常支持通过快照及类似技术使虚拟机回滚至先前状态。考虑到复制或分配相对标识符( Relative Identifier ,RID )等任务的性质，活动目录期望域控制器( Domain Controller ,DC )始终随时间向前推进。

随着这些问题的显现，微软自 Windows Server 2003 时代起对活动目录进行了调整，旨在检测可能已恢复快照并因此导致域控制器复制状态回退的情形。描述这一场景的术语“USN 回滚”在活动目录管理员中广为人知，随之而来的是对虚拟化域控制器的顾虑。

幸运的是，域控制器并无不能虚拟化的理由。虽然需要考虑最佳实践和安全策略，但活动目录运行于虚拟硬件平台并无不可。实际上，Windows Server 2012 域控制器能够通过底层虚拟化主机获知多种回滚情况，进而自我隔离于回滚之外，并重新同步至当前状态，而不影响整个环境的健康运行。

#### 何时虚拟化

在确定是否要虚拟化林( forest )中的部分或全部域控制器( Domain Controller ,DC)时，应考虑一些风险。这些风险涉及安全性、冗余，以及主机平台( hypervisor )的稳定性和运维实践。无论你运行 Active Directory 的 Windows 版本是什么，或使用哪种虚拟机监控程序，最终都需要以相同方式评估和规划。

首先，最重要的是，确保所选的虚拟机监控程序已列入 Microsoft 的服务器虚拟化验证计划( Server Virtualization Validation Program ,SVVP )，即 [SVVP](http://bit.ly/XEFj9q)。加入 SVVP 可确保在需要联系 Microsoft 支持时，无论相关服务器是虚拟化还是运行在物理硬件上，都能获得支持。

考虑安全性时，讨论 Active Directory 域控制器时请记住物理安全( physical security )的重要性。通常，你会考虑域控制器的存放位置是否安全（锁闭的门、视频监控等），但当域控制器虚拟化后，这个问题会变得更模糊。如果域控制器已虚拟化，任何有权访问存储虚拟硬盘( virtual hard disk ,VHD )的虚拟机监控程序存储位置的人，实际上都拥有对域控制器的物理访问权限。有些组织选择为 Active Directory 运行专用的虚拟化基础结构( virtualization infrastructure )，而其他组织则接受此风险。另请记住，许多主流虚拟机监控程序可以将虚拟硬盘文件通过网络发送到备用位置，以实现灾难恢复( disaster recovery )和高可用性( high availability )目的。此功能可视为优点，也可视为缺点；可用于灾难恢复而复制的虚拟磁盘文件，也可能被复制用于更险恶的目的。通过网络复制文件比物理移除域控制器要容易得多。

在大型组织中，运行活动目录( Active Directory ,AD)的团队通常是一小群资深管理员，他们拥有多年经验，并高度专注于交付少量关键服务（例如 AD）。同时，大型组织通常还设有独立团队负责运营整个组织的虚拟化平台( virtualization platform )，这些团队可能并不了解 AD。在这种情况下，必须考虑运行虚拟化平台的团队能否持续提供 AD 团队维持 AD 服务级别承诺( service-level commitments )所需的服务级别。还必须考虑是否可以信任虚拟化管理员遵循针对域控制器( Domain Controller ,DC)的特殊处理流程，例如不对域控制器虚拟机( Virtual Machine ,VM)拍摄快照。如果无法获得这类保证，那么可能有必要继续将 AD 运行在物理硬件上。

最后，还要考虑虚拟化域控制器时能够实现的冗余级别。使用物理硬件时，相对容易确保多台硬件在数据中心( datacenter )和网络中合理分布，从而容忍域控制器级别及其他级别（例如电源或网络中断）的中断。虚拟化域控制器后，由于虚拟化主机平台( virtualization host platform )增加了抽象层，理解这些风险会困难得多。至少，应确保将多个虚拟域控制器配置为跨环境中的多台物理主机和数据存储设备( data storage device )进行托管。这通常称为*反亲和性( antiaffinity )*。另外，还要考虑在数据中心级或组织级灾难恢复( disaster recovery ,DR)序列中，恢复 AD 处于什么位置。如果需要在虚拟化主机平台可用之前就让 AD 可用，则必须保留物理域控制器，以便更快地将其上线。

#### 虚拟化对域控制器的影响

探讨虚拟化对域控制器( Domain Controller ,DC )的影响时，通常会涉及两个关键场景。首先是更新序列号回滚( USN rollback )的概念。在第6章讨论虚拟化时，我们提到了更新序列号( Update Sequence Number ,USN )。USN 是 Active Directory 用来跟踪本地数据库每次更改的机制。第二个场景——相对标识符( Relative Identifier ,RID )重用或重复——虽然不太为人所知，但同样存在风险。每当创建安全主体( security principal )时，都会分配一个唯一的 RID 以构造该安全主体的唯一安全标识符( Security Identifier ,SID )。当虚拟机快照被恢复或回滚导致唯一编号( USN 或 RID )被重用时，这两种场景就会显现出来。

##### USN 回滚

USN 回滚的发生是因为域控制器( Domain Controller ,DC )基于已复制的更改所对应的最高 USN，来跟踪它们从另一台域控制器复制的更改。域控制器这样做是为了限制每个复制周期中必须评估的对象数量，并防止在可能从多个源域控制器接收更改时进行不必要的复制。这些值记录在每个域控制器上一个称为*最新状态向量* ( up-to-dateness vector ,UTDV )的表中。每个域控制器的数据库文件( *ntds.dit* )由一个称为*调用 ID* ( invocation ID )的 GUID 标识。在 UTDV 中，域控制器通过其调用 ID 来标识。有关 UTDV 和调用 ID 的更多信息，请参阅第 6 章。

以图 9-13中的场景为例。在此场景中，我们有两台域控制器：DC-A 和 DC-B。DC-A 是虚拟化的。考虑以下时间线中的事件：

1. 在 T1，DC-A 的 `highestCommittedUSN` 为 `100`，其调用 ID 为 `{P}`。DC-B 在其 UTDV 中有一个针对 DC-A 的条目，反映了此数据。此时两台域控制器均已同步。
2. 在 T2，虚拟化管理员创建了 DC-A 的快照。
3. 接下来，在 T3，Active Directory 管理员在 DC-A 上创建了 75 个用户。DC-A 的 `highestCommittedUSN` 现在为 175（因为已对数据库进行了 75 处更改）。
4. 在 T4，虚拟化管理员还原了 DC-A 的快照。DC-A 现在回到了 T2 状态。
5. 在 T5，Active Directory 管理员在 DC-A 上创建了 15 个用户。DC-A 的 `highestCommittedUSN` 现在为 115。当 DC-B 与 DC-A 进行复制时，DC-B 将其 UTDV 提供给 DC-A，DC-A 发现 DC-B 与 DC-A 已同步到更改 175。因此，DC-A 不会向 DC-B 发送任何更改。

这里描述的场景正是构成 USN 回滚的情况。现在 DC-A 上存在一个至少包含 15 处更改的孤岛，这些更改永远不会复制到林( forest )的其余部分。




![USN rollback timeline](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663418.webp)


图 9-13. USN 回滚时间线

从 Windows Server 2003 开始，Active Directory 内置了一些用于检测 USN 回滚的保护机制。这些保护机制能捕获部分场景，但并非全部场景，因此该问题仍可能影响整个林。当 AD 确实检测到回滚场景时，它会隔离该域控制器( Domain Controller ，DC )：禁用入站和出站复制，并暂停 Netlogon 服务。这些措施旨在将环境所受损害降到最低，并让管理员能够将该域控制器降级后再重新提升。发生此情况时，AD 会在事件日志中记录一条类似如下内容的事件(ID 2095，来源为 NTDS Replication)：

> 在一次 Active Directory 域服务复制请求期间，本地域控制器( DC )识别出一个远程 DC，该远程 DC 曾使用已被确认的 USN 跟踪号从本地 DC 接收复制数据。
>
> 由于该远程 DC 认为自己的 Active Directory 域服务数据库比本地 DC 的更新，因此它不会将后续更改应用到自己的 Active Directory 域服务数据库副本，也不会将其复制到源自此本地 DC 的直接和传递复制伙伴。
>
> 如果不立即解决，此场景将导致此源 DC 以及一个或多个直接和传递复制伙伴的 Active Directory 域服务数据库出现不一致。具体而言，用户、计算机和信任关系及其密码、安全组、安全组成员身份以及其他 Active Directory 域服务配置数据的一致性可能会有所差异，从而影响登录、查找目标对象以及执行其他关键操作的能力。
>
> 要确定是否存在此错误配置，请使用 [http://support.microsoft.com](http://support.microsoft.com/) 查询此事件 ID，或联系 Microsoft 产品支持人员。
>
> 此情况最可能的原因是本地域控制器上的 Active Directory 域服务还原方式不当。
>
> 用户操作：
>
> 如果此情况是由于还原不当或意外还原所致，请强制降级该 DC。
>
> 远程 DC：a2c53d4a-0018-4641-b277-eaecd25ec279
>
> 分区：DC=contoso, DC=com
>
> 远程 DC 报告的 USN：1000
>
> 本地 DC 报告的 USN：900

有关 AD 中 USN 回滚检测机制的更多信息，请参阅 Microsoft 知识库文章 [875495](http://support.microsoft.com/kb/875495)。

##### 相对标识符( Relative Identifier ,RID)池重用

与图 9-13中所示场景类似的是重用 RID 的影响。正如我们在第 2 章中所讨论的，RID 是用于为域中每个安全主体（用户、组或计算机）构造唯一的安全标识符( Security Identifier ,SID)的唯一编号。一旦使用了某个 RID，就永远不能重用。如果考虑图 9-13中的 T3 点，RID 100–175 已被使用，那么当域控制器( Domain Controller ,DC)被回滚并在 T5 创建用户时，RID 100–115 将被重用。这带来了安全挑战，因为多个用户具有相同的唯一标识符，该标识符对应于整个林的访问控制列表( Access Control List ,ACL)。为了缓解此问题，当 Active Directory 遇到多个具有相同 RID 的对象时，它会立即从数据库中删除这两个对象。

##### 系统时钟更改

虚拟机至少在启动期间依赖主机平台提供准确的时间信息。默认情况下，大多数虚拟化平台还配置来宾将其时钟与底层主机的时钟同步。当虚拟化主机的时钟不准确时，这两种情况都会带来挑战。

Active Directory 在许多位置包含当前时间。这些位置包括复制元数据以及属性级时间戳，例如 `lastLogonTimeStamp`。如果 DC 的时钟向前跳跃，无效的时间戳将开始出现在 Active Directory 中。对于 `lastLogonTimeStamp`，无效的未来时间戳将保留在原处，直到被取代。例如，如果您的时钟一次向前跳跃数年，那么您的用户和计算机将具有无效的 `lastLogonTimeStamp` 值，以及其他问题。

#### 虚拟化安全还原

随着虚拟化技术日益普及，显然 Active Directory 不能在常见虚拟化场景中面临重大挑战。为了支持虚拟化，Windows Server 2012 域控制器( Domain Controller ,DC)支持*虚拟机生成标识符( virtual machine generation identifier ,VM Gen ID)*的概念。VM Gen ID 是虚拟机状态的唯一标识符，由底层虚拟化主机平台投射到虚拟机中。

> **注意**：在撰写本文时，只有 Microsoft 的 Hyper-V 平台支持虚拟机生成 ID( Virtual Machine Generation ID ,VM Gen ID )，但我们预计随着时间的推移，这会扩展到其他主流虚拟化主机平台( virtualization host platform )。

VM Gen ID 的目标是检测域控制器( Domain Controller ,DC )可能在时间上被还原的情况，例如通过应用快照或复制 VHD 文件。一般来说，VM Gen ID 更新时机的底层原理与时间间隔何时会重演有关。如果将 Active Directory 的 USN 视为逻辑时钟( logical clock )——一个始终向前递增的数字——那么在虚拟化层面上，任何可能导致来宾的 USN 向后回退的情况都需要更新 VM Gen ID。每当 Active Directory 检测到 VM Gen ID 已回滚时，AD 将报告以下事件：

> 事件 ID: 2170
>
> 任务类别: Internal Configuration
>
> 级别: Warning
>
> 描述:
>
> 检测到生成 ID 更改。
>
> DS 中缓存的生成 ID(旧值): 4614786344935980275
>
> VM 中当前的生成 ID(新值): 10595675270371099562
>
> 生成 ID 更改发生在应用虚拟机快照之后、虚拟机导入操作之后或实时迁移操作之后。Active Directory 域服务( Active Directory Domain Services ,AD DS )将创建一个新的调用 ID( invocation ID )以恢复域控制器。不应使用虚拟机快照还原虚拟化域控制器。支持的还原或回滚 AD DS 数据库内容的方法是还原使用可识别 AD DS 的备份应用程序进行的系统状态备份( system state backup )。

Active Directory 将当前 VM Gen ID 保存在内存中(以及 AD 数据库中的非复制属性( nonreplicated attribute ) `msDS-GenerationID` 中)，并在将更改提交到 Active Directory 数据库之前以及启动期间，将该值与虚拟化主机平台报告的当前 VM Gen ID 进行比较。如果 VM Gen ID 已更改，域控制器首先执行以下步骤：

1. 重置域控制器的调用 ID。
2. 释放域控制器的 RID 池。
3. 以非权威方式还原域控制器上的 SYSVOL 共享。
4. 如果域控制器是 FSMO 角色持有者，Active Directory 还会暂停处理与 FSMO 角色相关的功能，直到可以完成一个复制周期( replication cycle )。

这些步骤共同确保域控制器将与整个林( forest )保持一致，并且不会出现时间气泡、重复或在整个林中不一致的数据。

#### 克隆域控制器( Domain Controller ,DC )

虚拟化安全还原功能( Virtualization Safe Restore Functionality )引入的一项有趣新场景是，能够快速克隆虚拟域控制器。此场景使您可以根据需求快速横向扩展（例如在云场景中）、部署新的虚拟域控制器（或许作为升级项目的一部分），或者在灾难恢复场景中快速部署域控制器。从根本上说，您可以复制 Windows Server 2012 域控制器的虚拟硬盘文件，并按需创建任意数量的其他唯一域控制器。

若要利用此功能，需要满足两个先决条件。第一个是，域中的 PDC 仿真器 FSMO 角色持有者必须运行 Windows Server 2012。第二个先决条件是，虚拟化主机平台支持 VM Gen ID 功能。满足这两个先决条件后，即可开始创建克隆。

克隆域控制器时，Active Directory 需要能够判断您是在创建克隆，而不是（例如）回滚快照。为了向 Active Directory 表明这一点，您需要创建一个包含克隆配置的*克隆配置文件( Cloning Configuration File )*，并使其在启动时可供克隆的 VHD 使用。创建克隆配置文件最简单的方法是使用 *New-ADDCCloneConfigFile* PowerShell cmdlet。

克隆配置文件包含将应用于克隆的唯一标识元素，例如计算机名、IP 地址和其他网络信息。配置文件中未提供的任何信息都将在克隆首次启动期间动态生成。例如，如果未指定 IP 信息，将使用 DHCP。如果未指定计算机名，将动态生成一个名称。

> **注意**：动态生成的计算机名格式为源域控制器( Domain Controller ,DC)名称的前八个字符,后跟 *–CL####*。最后四位数字的范围为 0001 至 9999。在克隆授权期间,PDC 仿真器将选取一个可用编号来唯一命名克隆。

如果提供像这样的空白配置文件,那么 AD 将在启动时动态生成所有必要参数:


```
<?xml version="1.0"?>
<d3c:DCCloneConfig xmlns:d3c="uri:microsoft.com:schemas:DCCloneConfig">
</d3c:DCCloneConfig>
```


表 9-1 列出了可以为 *New-ADDCCloneConfigFile* 指定的参数。

表 9-1. 克隆配置文件参数

| 名称                  | 描述                                                  |
| --------------------- | ------------------------------------------------------------ |
| `Path`                | 指示在何处创建 *DCCloneConfig.xml* 文件的路径。如果未指定此参数,该文件将创建在 *DSA 工作目录*文件夹中(通常为存储 *ntds.dit* 文件的位置)。 |
| `CloneComputerName`   | 克隆的域控制器的名称。                    |
| `SiteName`            | 放置克隆的域控制器的 AD 站点。                    |
| `IPv4Address`         | 分配给克隆的静态 IPv4 地址。                      |
| `IPv4SubnetMask`      | 分配给克隆的静态 IPv4 子网掩码。                      |
| `IPv4DefaultGateway`  | 分配给克隆的静态 IPv4 默认网关。                      |
| `IPv4DNSResolver`     | 分配给克隆的 IPv4 DNS 服务器。使用数组语法可指定多个 DNS 服务器——例如:`-IPv4DNSResolver @("10.10.10.1", "10.10.10.2")` |
| `PreferredWINSServer` | 分配给克隆的主 WINS 服务器。              |
| `AlternateWINSServer` | 分配给克隆的辅助 WINS 服务器。            |
| `IPv6DNSResolver`     | 分配给克隆的 IPv6 DNS 服务器。使用数组语法(如 `IPv4DNSResolver` 示例所示)可指定多个。 |
| `Static`              | 如果要指定静态 IP 地址或 DNS 服务器信息,则必须包含此开关。 |
| `Offline`             | 包含此开关可在创建克隆配置文件之前跳过验证检查。 |

> **注意**：在域控制器( Domain Controller ,DC)克隆配置文件中，无法指定静态 IPv6 地址。

可以将 DC 克隆配置文件(*DCCloneConfig.xml*)放置在三个位置。选择哪个位置取决于您对克隆功能的使用方式以及部署策略。这些位置按顺序依次为：

- *DSA 工作目录*( *DSA Working Directory* )文件夹(存储 *ntds.dit* 文件的位置)
- *%windir%\ntds* 文件夹
- 某个已装载可移动介质(例如虚拟软盘)的根目录，按驱动器盘符的字母顺序排列

如果您是按需临时克隆 DC，或者只是想使用空白或通用的克隆配置文件，那么您很可能应选择上面列出的第一个或第二个位置。如果您要从同一源克隆大量 DC，并且希望为每个 DC 使用特定配置，那么您可能需要考虑第三个选项。这样，您可以为每个克隆 DC 创建自定义虚拟软盘( Virtual Floppy Disk ,VFD)文件，其中 *DCCloneConfig.xml* 文件包含该克隆的特定配置设置，然后在首次启动时装载该 VFD 文件。或者，您也可以在首次启动之前装载克隆的 VHD 文件(例如，使用 Hyper-V PowerShell cmdlet *Mount-VHD*)，并将 *DCCloneConfig.xml* 文件注入到第一个或第二个位置。



> **注意**：您也可以在 Windows 资源管理器中手动装载和卸载 VHD 文件。选择该 VHD 文件，然后在“光盘映像工具”上下文功能区选项卡上单击“装载”，如图 9-14所示。完成后，选择已装载的驱动器，然后在功能区上单击“弹出”。




![Mounting a VHD with Windows Explorer](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663419.webp)


图 9-14. 使用 Windows 资源管理器装载 VHD

除了 *DCCloneConfig.xml* 文件之外，Microsoft 还添加了另一项重要防护措施——克隆允许列表( Cloning Allow List )。Microsoft 识别出的实施克隆的风险之一是，要克隆的 DC 上的应用程序或服务(例如备份代理或防病毒软件)可能不支持克隆。为缓解此问题，您必须在 *CustomDCCloneAllowList.xml* 文件中指定这些应用程序和服务，从而明确告知 Active Directory：可以克隆安装了 Windows 基本功能之外的应用程序和服务的 DC。

> **注意**：你可能想知道克隆对 Windows 本身有何影响。克隆域控制器(Domain Controller,DC)时,在首次启动期间,它会运行 *sysprep* 进程的精简版本(该进程在克隆传统服务器或工作站时用于移除源 DC 特有的标识信息)。

你可以通过查看 *%windir%\system32* 中的 *DefaultDCCloneAllowList.xml* 文件,找到所运行的 *sysprep* 提供程序列表以及默认允许的应用程序和服务列表。

首先,在将要克隆的域控制器上运行 *Get-ADDCCloningExcludedApplicationList*。此 PowerShell cmdlet 会对照已批准的列表检查所有服务,以及所有已安装的应用程序。如果发现任何自定义应用程序,它们将打印到 PowerShell 窗口中。从源 DC 移除所有不支持克隆的应用程序后,使用 *-GenerateXml* 开关和 *-Path* 参数再次运行 *Get-ADDC**CloningExcludedApplicationList*。PowerShell 将创建一个允许列表 XML 文件。



> **注意**：虽然可以手动编辑 *DCCloneConfig.xml* 和 *CustomDCCloneAllowList.xml* 文件,但你必须格外小心,不要使 XML 失效。如果 XML 失效,克隆过程将失败。

最后一步是,你必须将源 DC 的计算机帐户添加到 Active Directory 中的可克隆域控制器组。这将授予源 DC 克隆自身的权限。

##### DC 克隆过程

完成先决条件步骤、复制虚拟硬盘文件、创建配置文件,并首次启动克隆的虚拟机后,Active Directory 的克隆过程将开始。此过程涉及多个步骤。许多步骤都具有故障保护流程,以确保在发生故障时,域控制器会重新启动进入目录服务还原模式( Directory Services Restore Mode ,DSRM),从而使故障不会对环境产生负面影响。

在启动期间,Active Directory 将首先检查 VM Gen ID 是否已更改。如果 VM Gen ID 已更改,则 Active Directory 便知道发生了某些情况。根据 *DCCloneConfig.xml* 文件是否存在,Active Directory 便知道需要开始克隆过程。

> **注意**：如果 Active Directory 发现虚拟机生成 ID( Virtual Machine Generation ID ,VM Gen ID)不存在，但存在 *DCCloneConfig.xml* 文件，则域控制器( Domain Controller ,DC)将重命名 *DCCloneConfig.xml* 文件，并重启进入目录服务还原模式( DS Restore Mode )。这样可确保不会将未运行在支持 VM Gen ID 的虚拟化主机平台上的克隆引入网络。

首先，Active Directory 完成虚拟化安全还原( Virtualization Safe Restore )一节中描述的所有步骤。接着，克隆过程开始。Active Directory 执行以下步骤来完成克隆过程：

1. 服务器处理 *DCCloneConfig.xml* 文件。如果配置文件中指定的静态 IP 将导致 IP 地址冲突，则克隆将启动进入目录服务还原模式。
2. 所有网络接口卡( Network Interface Card ,NIC)上的 DNS 注册均被禁用，并停止 NetLogon 服务，以确保不会联系到克隆。
3. 根据内置允许列表以及 *CustomDCCloneAllowList.xml* 文件验证已安装应用程序和服务的列表。如果有未列出的应用程序或服务，则克隆将启动进入目录服务还原模式。
4. 通过 RPC 联系 PDC 模拟器( PDC Emulator ) FSMO，以开始克隆过程。
5. PDC 模拟器确保允许克隆的源虚拟机( Virtual Machine ,VM)克隆自身。如果必要的权限未到位，则克隆将启动进入目录服务还原模式。
6. 更改克隆的计算机名，然后在克隆的 Active Directory 站点中创建必要的服务器和 NTDS Settings 对象。
7. 克隆使用从介质安装( Install from Media ,IFM)提升过程将自己提升为域控制器。这样，克隆即可完成提升，而无需复制除自虚拟硬盘被克隆以来对 AD 或 Sysvol 所做的更改以外的任何内容。
8. 克隆运行 *sysprep* 并自行重启。在 `HKLM\System\CurrentControlSet\Services\NTDS\Parameters\VdcCloningDone` 中设置注册表标志，以指示该 DC 是克隆的域控制器。

如果要克隆的源 DC 是 PDC 模拟器，则在步骤 6 和步骤 7 之间会额外进行一次重启。尽管上述列表对克隆的域控制器上线所涉及的关键步骤提供了高层概述，但还有一份内容远为[详尽描述](http://bit.ly/106wB5y)的资料，其中包含所有细节。

##### 克隆域控制器

为了总结我们关于克隆的讨论，我们将克隆一个名为 *COHO-SFO-ADC01* 的域控制器（ Domain Controller ，DC），并创建一个名为 *COHO-PAR-ADC01* 的新域控制器。为此，我们将复制 *COHO-SFO-ADC01* 的虚拟硬盘文件，挂载该虚拟硬盘，然后注入 *DCCloneConfig.xml* 文件。最后，我们将启动新虚拟机（ *COHO-PAR-ADC01* ）并观察克隆过程的进行。我们的克隆将具有表 9-2 中所示的属性。

表 9-2. 克隆域控制器属性

| 属性              | 值                  |
| --------------------- | ---------------------- |
| 名称                  | COHO-PAR-ADC01         |
| Active Directory 站点 | Paris                  |
| IPv4 地址          | 172.16.4.1             |
| IPv4 子网掩码      | 255.255.255.0          |
| IPv4 默认网关  | 172.16.4.1             |
| IPv4 DNS 服务器      | 172.16.1.21172.16.1.22 |

以下是完成此操作所需执行的步骤：

1. 在 *COHO-SFO-ADC01* 上，运行 *Get-ADDCCloningExcludedApplicationList*。如果列出了任何不支持克隆的应用程序，请将其卸载。

2. 在 *COHO-SFO-ADC01* 上，运行 *Get-ADDCCloningExcludedApplicationList -GenerateXML* 以生成自定义克隆允许列表。

3. 将 *COHO-SFO-ADC01* 添加到可克隆域控制器（ Cloneable Domain Controllers ）组。您可以通过运行以下命令使用 PowerShell 完成此操作：

```
   Add-ADGroupMember "Cloneable Domain Controllers" -Members COHO-SFO-ADC01$
```


4. 关闭 *COHO-SFO-ADC01* 并复制该虚拟机，为 *COHO-PAR-ADC01* 创建虚拟机。

5. 为 *COHO-PAR-ADC01* 创建克隆配置文件。您可以在任何安装了 Active Directory RSAT 工具的计算机上，通过运行以下 PowerShell 命令来完成此操作：

```
   New-ADDCCloneConfigFile -CloneComputerName COHO-PAR-ADC01 `
   -SiteName Paris `
   -IPv4Address 172.16.4.21 `
   -IPv4SubnetMask 255.255.255.0 `
   -IPv4DefaultGateway 172.16.4.1 `
   -IPv4DNSResolver @("172.16.1.21", "172.16.1.22") `
   -Static `
   -Offline `
   -Path .\
```


6. 挂载虚拟硬盘文件，并将新的 *DCCloneConfig.xml* 文件复制到已挂载虚拟硬盘中的 *%windir%\ntds* 目录下。要使用 Hyper-V 完成此操作，请按照以下步骤执行：

```
   Mount-VHD -Path `
    'E:\Hyper-V\Virtual Machines\COHO-PAR-ADC01\COHO-PAR-ADC01.vhdx'
   Dismount-VHD -Path `
    'E:\Hyper-V\Virtual Machines\COHO-PAR-ADC01\COHO-PAR-ADC01.vhdx'
```


7. 启动 *COHO-PAR-ADC01*。如果您观察启动过程，将会看到克隆过程正在执行，类似于图 9-15 和图 9-16 所示。

启动过程完成后，您将获得一个功能完备的克隆域控制器，可随时响应客户端请求。


![Abbreviated sysprep during domain controller cloning](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663420.webp)

图 9-15. 域控制器克隆期间的精简 sysprep


![Domain controller cloning in progress](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663421.webp)


图 9-16. 域控制器克隆正在进行中

### 9.3. 只读域控制器( Read-Only Domain Controllers )

Windows Server 2008 引入的最重要的 Active Directory 功能之一是只读域控制器。将域控制器部署到不受信任的位置一直是 Active Directory 部署中的重大安全风险。域控制器被物理入侵、该域的密码哈希被盗取的风险，以及数据库(*ntds.dit*)被离线修改后重新放回网络的风险，都是必须考虑的重要问题。只读域控制器( Read-Only Domain Controller ,RODC )能够缓解这两种风险。

默认情况下，RODC 不会在其数据库本地存储任何密码。如果用户向 RODC 进行身份验证，RODC 需要联系上游的可写域控制器(有时称为 *RWDC*)来验证该用户的密码。当然，这也适用于其他带有密码的对象，例如计算机账户和信任账户。通过本节后面讨论的密码复制策略，您可以定义哪些密码允许在 RODC 上本地缓存。您还可以查看 RODC 上当前缓存密码的实时视图。

为了确保 RODC 不会影响 Active Directory 林的完整性，所有到 RODC 的复制都是单向的。这意味着，如果有人在 RODC 上进行了更改，Active Directory 不会将该更改复制到其他域控制器。图 9-17 展示了部署了 RODC 的网络中的复制路径。




![RODC replication](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663422.webp)


图 9-17. RODC 复制

一般来说，我们会在几种场景中看到 RODC 的部署。第一种是在分支机构。分支机构通常是较小的设施，通过广域网( Wide Area Network ,WAN )链路连接到数据中心或其他中心站点。这些 WAN 链路的速度和可靠性差异很大。分支机构的第二个关键特征是域控制器的物理安全无法得到保证。通常，分支机构中的服务器机房仅仅是储物间或其他被改作他用的空间，对于谁可以访问该空间的管控措施非常有限。本书中关于 RODC 的大部分讨论都将聚焦于分支机构。

第二个场景是只读域控制器( Read-Only Domain Controller ,RODC)在外围网络( Perimeter Network )中的概念。*外围网络*是网络中相对于其余部分被视为不受信任的一部分。许多组织将其面向 Internet 的服务器放置在外围网络中。为了使这些服务器加入域,必须通过防火墙打开大量端口,以至于防火墙常常(准确地)被比作瑞士奶酪。一些组织可能会选择将 RODC 部署到其外围网络中,以充当外围网络中与其并存的服务器的域控制器( Domain Controller ,DC)。使用 RODC 允许本地网络身份验证,同时降低某人入侵域控制器并进行更改以复制回内部网络上的域控制器的风险。但是,你仍然面临内部信息泄露的风险(例如,电话号码、公司汇报结构以及任何其他内部信息)。

在阅读本节时,请记住 RODC 背后的指导设计原则。该原则是 RODC 默认已失陷这一核心假设。如果你想知道 RODC 的某个功能为何以某种方式运行,请花点时间考虑 RODC 被入侵的场景。

#### 先决条件

在继续操作之前，将只读域控制器( Read-Only Domain Controller ,RODC )部署到 Active Directory 安装中时有几项主要先决条件需要考虑。第一项是，林至少必须处于 Windows Server 2003 林功能级别( Forest Functional Level ,FFL )。接下来，根据 Active Directory 站点链接( Site Link )拓扑的确定结果，你的 RODC 所连接的站点中需要有一台可写 Windows Server 2008 域控制器( Domain Controller ,DC )。

请参考图 9-18。如果在 Active Directory 站点和服务( Active Directory Sites and Services )中启用了“桥接所有站点链接”( Bridge all site links )，则 RODC 与 Windows Server 2008 或更高版本的可写域控制器( Read-Write Domain Controller ,RWDC )之间可以相隔超过一个跃点，因此站点 A 中的 RODC 可以与站点 C 中的 Windows Server 2008 RWDC 通信。但是，如果未启用“桥接所有站点链接”，则你需要创建一个包含站点链接 *A - B* 和 *B - C* 的站点链接桥( Site Link Bridge )，或者在站点 B 中部署一台 Windows Server 2008 或更高版本的 RWDC。




![Sample RODC deployment topology](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663423.webp)


图 9-18. 示例 RODC 部署拓扑

除了这些 Active Directory 要求之外，你还应考虑向客户端部署 RODC 兼容性包( RODC Compatibility Pack )。该程序包可通过 Microsoft 知识库文章 [944043](http://bit.ly/16fQxa1) 下载(该文章中也对其进行了说明)。你可能会遇到 Windows XP 和 Windows Server 2003 客户端及域控制器中的许多兼容性问题和缺陷，而此程序包可解决其中许多问题。在本章中，我们会在适当时提到可能需要此程序包的情形。

> **注意**：在本章中，我们会经常提到 RODC 可以请求复制特定对象的情形。此功能称为*单对象复制*( Replicatesingleobject ,RSO )。单对象复制操作通过修改 `RootDSE` LDAP 条目的 `replicateSingleObject` 操作属性来启动。有关此属性的详细信息，请参阅[此站点](http://bit.ly/WUdAEp)。

#### 密码复制策略

正如我们简要讨论的，只读域控制器( Read-Only Domain Controller ,RODC )默认不缓存密码。这意味着，如果攻击者从 RODC 获取了活动目录( Active Directory ,AD )数据库的副本，也无法破解任何密码，因为其中没有存储任何密码。不存储任何密码的缺点是，RODC 需要调用可写域控制器( Read-Write Domain Controller ,RWDC )（通常通过广域网( Wide Area Network ,WAN )）来对客户端进行身份验证。当 WAN 中断时，即使本地有域控制器，客户端也无法通过身份验证，此时 RODC 的价值就会降低。

此问题的解决方案是使用*密码复制策略*( Password Replication Policies ,PRPs )。密码复制策略允许您定义哪些用户(和计算机)密码在 RODC 本地缓存，以及哪些密码永远不能缓存。PRPs 通过 Active Directory 中 RODC 计算机账户上的一系列四个链接的多值属性( multivalued attribute )来定义。这些属性包括：

- **`msDS-RevealOnDemandGroup`**

  这是 RODC 可以为其缓存密码的主体( principal )列表。此列表通常称为*允许*( allowed )列表。

- **`msDS-NeverRevealGroup`**

  这是 RODC *永远*不允许为其缓存密码的主体列表。此列表通常称为*拒绝*( denied )列表。

- **`msDS-RevealedList`**

  这是密码当前缓存在 RODC 上的主体列表。它通常称为已透露列表( revealed list )。

- **`msDS-AuthenticatedAtDC`**

  这是已通过 RODC 身份验证的主体列表。此列表通常称为 authenticated to 列表或 *Auth-2* 列表。

除了这些属性之外，当您在域中部署第一个 RODC 时，还会向 Active Directory 添加两个新的内置组( built-in group )。它们是*允许 RODC 密码复制组*( Allowed RODC Password Replication Group )和*拒绝 RODC 密码复制组*( Denied RODC Password Replication Group )。默认情况下，允许组会添加到 `msDS-RevealOnDemandGroup` 属性，拒绝组会添加到 `msDS-NeverRevealGroup` 属性。默认情况下，允许组没有成员，但拒绝组有多个成员：

- Cert Publishers
- Domain Admins
- Enterprise Admins
- Enterprise Domain Controllers
- Enterprise Read-Only Domain Controllers
- Schema Admins
- *krbtgt* 账户

除了这些组和账户之外，默认情况下还有几个组会添加到 `msDS-NeverRevealGroup` 属性：

- Account Operators
- Administrators
- Backup Operators
- Denied RODC Password Replication Group
- Server Operators

所有这些组通常都包含高度受信任的用户账户，因此，你不应冒险将这些密码缓存在只读域控制器( Read-Only Domain Controller ,RODC )上，以免密码泄露。因此，我们不建议将这些组从默认拒绝复制组( Default Denied Replication Group )或 `msDS-NeverRevealGroup` 属性中移除。

为了让 RODC 能够在不与可写域控制器( Writable Domain Controller )通信的情况下颁发 Kerberos 服务票证( Kerberos Service Ticket )，RODC 需要在本地缓存所涉及的用户账户和计算机账户的密码。请务必记住这一点，因为你需要同时规划用户账户和计算机账户的密码缓存。除了用户之外，你还需要考虑 RODC 所在站点的服务器或其他计算机上正在使用的任何服务账户( Service Account )。

在规划 RODC 部署时，你需要仔细考虑如何设置密码复制策略( Password Replication Policy ,PRP )。根据你选择的途径，你可能需要投入精力更新用户预配流程( User Provisioning Process )，以使密码复制策略保持最新。在规划密码复制策略时，我们预计大多数组织会采用以下三种策略：

- **不缓存密码**

  在此方案中，RODC 不会缓存任何密码，而只是充当只读目录，在身份验证过程中充当代理。如果你考虑在外围网络( Perimeter Network )方案中部署 RODC，那么在为这些 RODC 定义密码复制策略时，这很可能就是你将采用的途径。这是最安全的配置，也是默认配置。无需管理策略或组。

- **缓存几乎所有密码**

  如果你希望减少管理开销并最大限度地容忍 WAN 故障，那么这可能就是你的密码复制策略应采用的方案。如果你对 RODC 的物理安全有顾虑，我们不建议选择此策略。只有当用户或计算机通过某个特定 RODC 登录后，或者密码被手动复制到该 RODC 后，密码才会缓存在该 RODC 上。

- **有限缓存密码**

在此场景中，你将按每个只读域控制器( Read-Only Domain Controller ,RODC )为单位，定义哪些密码可由 RODC 缓存。该列表通常反映 RODC 所服务站点中的用户和计算机列表。在这种情况下，你需要设计一个流程来管理每个 RODC 的列表。建议将此流程与用户预配流程集成。除了用户预配流程之外，还需要接入一个用于管理计算机帐户的机制。为此场景进行规划时，不要忘记考虑在不同站点之间移动的用户。

##### 管理密码复制策略

活动目录用户和计算机( Active Directory Users and Computers ,ADUC)工具提供了一个属性页,可用于管理只读域控制器( Read-Only Domain Controller ,RODC)的密码复制策略( Password Replication Policy ,PRP),也可用于查看已公开列表和已通过身份验证的列表。图 9-19显示了新 RODC 的默认设置。此处显示的列表可通过在 ADUC 中右键单击该域控制器( Domain Controller ,DC)的计算机帐户并选择"属性"来访问。

![ADUC Password Replication Policy tab](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663424.webp)

图 9-19. ADUC 的密码复制策略选项卡

单击"添加",即可将用户、组和计算机添加到此列表中。单击"添加"后,ADUC 会提示你允许或拒绝所选对象的复制,如图 9-20所示。

![Adding to the password replication policy lists](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663425.webp)

图 9-20. 向密码复制策略列表中添加对象

单击图 9-19中的"高级"按钮,将打开一个对话框,可用于检查 `msDS-RevealedList` 和 `msDS-AuthenticatedAtDC` 属性。图 9-21顶部的下拉列表可在要显示的属性之间切换。"其密码存储在此只读域控制器上的帐户"显示 `msDS-RevealedList` 属性,"已通过此只读域控制器身份验证的帐户"显示 `msDS-AuthenticatedAtDC` 属性。如果单击图 9-21所示对话框左下角的"导出"按钮,可以将所显示的数据保存为逗号分隔值( comma-separated values ,CSV)列表。

图 9-21所示的高级对话框还可以确定哪些帐户的密码可由 RODC 缓存。当某个帐户的密码缓存行为与预期不符时,此功能对故障排除非常有用。图 9-22显示了若干用户的"最终策略"选项卡。

![Viewing the revealed list](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663426.webp)

图 9-21. 查看已透露列表

可为账户显示几种不同的结果策略设置。显示“允许”的账户定义在 `msDS-RevealOnDemandGroup` 列表中。显示“拒绝(显式)”的账户定义在 `msDS-NeverRevealGroup` 列表中。最后，显示“拒绝(隐式)”的账户未定义在任一列表中，因此不允许缓存其密码，因为只读域控制器( Read-Only Domain Controller ,RODC )的默认行为是不缓存给定账户的密码。请注意，如图 9-22所示，可为用户和计算机计算结果策略。




![Resultant password replication policy](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663427.webp)


图 9-22. 结果密码复制策略

##### 管理只读域控制器( Read-Only Domain Controller ,RODC)的丢失

如果 RODC 被盗——或者更具体地说，保存数据库的驱动器遭到物理入侵或被盗——按照最佳做法，你应立即重置在该 RODC 上缓存的密码。

执行此任务所用的 Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC)用户界面，可通过从 Domain Controllers 组织单位( Organizational Unit ,OU)中删除该 RODC 的计算机账户来访问。如果尝试删除该计算机账户，系统会显示图 9-23所示的对话框。在此对话框中，你可以选择重置用户、计算机或两者的密码。虽然该对话框默认只重置用户密码，但请记住，计算机是一种特殊类型的用户账户，它们也有密码。攻击者可以使用计算机的账户和密码向你的域进行身份验证。

> **警告**：务必留意图 9-23中的警告。不重置密码会带来安全风险,因此我们不建议您为了方便而选择不重置密码。不过,我们建议您停下来思考一下,重置站点中所有已缓存用户密码会带来什么影响。这将导致无法登录的用户拨打服务台电话,而对于服务账户,则会导致服务无法启动。

重置计算机密码后,这些计算机将无法通过域身份验证。您需要亲自前往每台工作站,或者如果您能够集中获取每台计算机的本地管理员凭据,则可以使用 *netdom* 或 *nltest* 等工具编写脚本解决方案。




![Deleting an RODC computer account](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663428.webp)


图 9-23. 删除 RODC 计算机账户

虽然并非必须,但我们强烈建议您导出受影响账户的 CSV 列表,以便您跟进服务台和其他支持团队。重置用户和计算机密码无疑会带来巨大的痛苦,因此在规划整体 RODC 部署时,应将此场景纳入规划。

#### 客户端登录过程

至此，我们已经讨论了只读域控制器( Read-Only Domain Controller ,RODC )上的密码缓存以及如何控制此缓存，但尚未探讨 RODC 如何从可写域控制器获取密码并在本地缓存。在本节中，我们将不仅了解密码如何在本地缓存，还会探讨涉及 RODC 时域控制器与客户端之间通信的整体流程。

贯穿本节，你应牢记 RODC 与其可写对应物之间的一个关键区别（我们也会频繁提及）：每个 RODC 都有其独立的 *krbtgt* 账户。域 *krbtgt* 账户是域控制器用于加密 Kerberos 票据的凭据，一旦你掌握了这些凭据，便对森林拥有无穷的控制力。因此，每个 RODC 都维护一个单独的 *krbtgt* 账户，命名格式为 *krbtgt_<编号>*，其中 *<编号>* 是唯一的数字。RODC 仅在本地存储其专属 *krbtgt* 账户的密码。而可写域控制器则在其数据库中存储每个 *krbtgt* 账户的密码。

要确定与特定 RODC 关联的 *krbtgt* 账户，你可以检查 RODC 计算机账户上的 `msDS-KrbTgtLink` 属性，或 *krbtgt* 账户上的 `msDS-krbTgtLinkBL` 属性。

让我们以图 9-24所描述的情形作为后续讨论的基础。图 9-24包含四个角色：

- **RWDC01**

  这是位于数据中心的可写域控制器。

- **RODC01**

  这是位于分支机构的只读域控制器。

- **用户 Brian**

  这是即将登录并访问服务的用户。

- **计算机 PC01**

  这是用户 *Brian* 的工作站。




![Sample network topology](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663429.webp)


图 9-24. 示例网络拓扑

假设第一步是我们的机器 *PC01* 向域进行身份验证。接下来将执行以下步骤：

1. 首先，*PC01* 会联系 *RODC01* 并提供 Kerberos 身份验证服务请求（即 *KRB_AS_REQ* 数据包）。

2. 当 *RODC01* 收到 *KRB_AS_REQ* 后，它会检查本地数据库，看是否已在本地缓存了 *PC01* 的密码。在此示例中，我们假设实际上并未缓存。

3. 由于 *RODC01* 本地未缓存密码，它必须联系 *RWDC01* 并提供其收到的 Kerberos 认证服务请求( Kerberos Authentication Service Request ,KRB_AS_REQ )。

4. *RWDC01* 将生成 Kerberos 认证服务回复( Kerberos Authentication Service Reply ,KRB_AS_REP )，并将其转发回 *RODC01*。

5. *RODC01* 接着会将该回复提供给 *PC01*，完成认证请求。*RWDC01* 还会更新 *RODC01* 的 Auth-2 列表( Auth-2 list )(`msDS-AuthenticatedAtDC`)，以便将 *PC01* 包含在该列表中。

   此时，*PC01* 已拥有由域 *krbtgt* 账户签名的有效 Kerberos 票据授予票据( Ticket-Granting Ticket ,TGT)。在第 5 步之后，*RODC01* 将启动两个额外步骤，以尝试在本地缓存密码：

6. *RODC01* 将向 *RWDC01* 提交请求，以将 *PC01* 的凭据复制到 *RODC01*。

7. *RWDC01* 将验证密码复制策略( Password Replication Policy )是否允许 *RODC01* 缓存 *PC01* 的密码，并将密码复制到 *RODC01*。*RWDC01* 还会更新 *RODC01* 的已揭示列表( revealed list )(`msDS-RevealedList`)，以便将 *PC01* 包含在内。

> **注意**：在查看步骤 7 时，您可能会想：为什么 *RWDC01* 要检查密码复制策略( Password Replication Policy ,PRP)，而不是假定 *RODC01* 既然请求了密码就可以缓存它？原因在于，我们必须假定 *RODC01* 已遭入侵，并且作为该事件的一部分，*RODC01* 上的密码复制策略本地副本可能已被修改，其他账户可能被偷偷添加到 PRP 允许列表中。

现在让我们来看用户 *Brian* 登录其计算机的过程。我们当然假定前七个步骤已成功完成。以下是 Brian 尝试登录其计算机时所采取的步骤：

1. Brian 将其凭据提供给 *PC01*，然后 *PC01* 为用户 *Brian* 向 *RODC01* 发送一个 *KRB_AS_REQ*。
2. 当 *RODC01* 收到该 *KRB_AS_REQ* 时，它会检查本地数据库，看是否已在本地缓存 Brian 的密码。在本例中，我们假定实际上并未缓存。
3. 由于 *RODC01* 未在本地缓存密码，它必须联系 *RWDC01* 并提供其收到的 *KRB_AS_REQ*。
4. *RWDC01* 将生成一个 *KRB_AS_REP* 并将其转发回 *RODC01*。
5. *RODC01* 随后会将该回复提供给 *PC01*，从而完成用户 *Brian* 的身份验证请求。*RWDC01* 还会更新 *RODC01* 的 Auth-2 列表(`msDS-AuthenticatedAtDC`)，将用户 *Brian* 包含在该列表中。

此时，用户 *Brian* 拥有一个由域 *krbtgt* 账户签名的有效 Kerberos 票据授予票据( Ticket-Granting Ticket ,TGT)。在步骤 5 之后，*RODC01* 将启动之前的步骤 6 和步骤 7，只不过这次 *RODC01* 将尝试在本地缓存用户 *Brian* 的密码。

然而，非常重要的一点是，用户 *Brian* 的登录过程尚未完成！在 Brian 可以使用其工作站之前，他必须获取用于 *PC01* 的 Kerberos 服务票据( Service Ticket ,TGS)。继续我们的示例，当 *PC01* 为用户 *Brian* 向 *RODC01* 发送 TGS 票据时，*RODC01* 将无法解密该 TGT，因为该 TGT 是使用域 *krbtgt* 账户加密的，而该账户的密码*从不*缓存在只读域控制器( Read-Only Domain Controller ,RODC)上。以下步骤显示了 *Brian* 获取用于 *PC01* 的 TGS 票据的过程：

1. *PC01* 为用户 *Brian* 访问 *PC01* 向 *RODC01* 发送一个 *KRB_TGS_REQ*。该 *KRB_TGS_REQ* 包含来自上一示例的 *Brian* 的 TGT。

2. *RODC01* 无法解密 TGS 请求中包含的 TGT，因为该 TGT 是使用域 *krbtgt* 账户加密的。

3. *RODC01* 将 *KRB_TGS_REQ* 传输到 *RWDC01*，后者使用 *KRB_TGS_REP* 进行回复。

4. *RODC01* 接收到有效的 *KRB_TGS_REP*。*RODC01* 并不将 *KRB_TGS_REP* 转发给 *PC01*,而是向 *PC01* 发送一个错误。

   > **注意**：*RODC01* 发送给 *PC01* 的特定 Kerberos 错误会告知 *PC01*,用户 *Brian* 的票据授予票据( Ticket-Granting Ticket ,TGT )已过期。

5. *PC01* 为用户 *Brian* 准备新的 *KRB_AS_REQ*,并将其发送给 *RODC01*。

6. 由于 *RODC01* 现在已缓存用户 *Brian* 的凭据,*RODC01* 能够在本地构造新的 *KRB_AS_REP*(从而为 Brian 生成新的 TGT),使用 *RODC01* 本地的 *krbtgt* 账户对其加密,并将其发送给 *PC01*。

7. *PC01* 为用户 *Brian* 向 *RODC01* 发送新的 *KRB_TGS_REQ*,这次包含 *Brian* 的新 TGT。

8. *RODC01* 能够解密 *KRB_TGS_REQ* 中的 TGT,并构造一个 *KRB_TGS_REP*,其中包含允许用户 *Brian* 使用 *PC01* 的服务票据。

> **注意**：你可能想知道，如果读写域控制器( Read-Write Domain Controller ,RWDC)收到由只读域控制器( Read-Only Domain Controller ,RODC)加密的票证授予票证( Ticket Granting Ticket ,TGT)，会发生什么。每个 RODC 的 *krbtgt* 账户都会复制到域中的所有 RWDC，因此 RWDC 可以解密由 RODC 加密的 Kerberos 票证。TGT 的头部包含未加密的信息，使 RWDC 能够确定解密消息时应使用哪个 RODC 的 *krbtgt* 账户。

完成这些步骤后，用户 *Brian* 就能够使用 *PC01*。在用户 *Brian* 后续登录 *PC01* 的过程中，获取服务票证( Service Ticket ,TGS)的步骤要简单得多：

1. *PC01* 向 *RODC01* 发送 *KRB_TGS_REQ*，以便用户 *Brian* 访问 *PC01*。该 *KRB_TGS_REQ* 包含 *Brian* 的 TGT，而该 TGT 已由 *RODC01* 加密。
2. *RODC01* 解密 *KRB_TGS_REQ* 中的 TGT，并构造一个 *KRB_TGS_REP*，其中包含允许用户 *Brian* 使用 *PC01* 的服务票证。

审阅这些示例后，你可能已经开始注意到在 RODC 上同时缓存用户密码和计算机密码的重要性。用户身份验证要成功，RODC 必须同时拥有用户和计算机的密码。如果其中任一密码不存在，RODC 就需要通过广域网( Wide Area Network ,WAN)与可写域控制器( Writable Domain Controller )通信。如果 WAN 不可用，用户登录将失败。

> **警告**：只读域控制器( RODC )联系的可写域控制器( writable domain controller ,DC)必须运行 Windows Server 2008 或更高版本。如果只有 Windows Server 2003 域控制器可用,则登录请求将失败。

##### 填充密码缓存

由于经只读域控制器（Read-Only Domain Controller，RODC）处理的登录能否成功，完全取决于广域网（Wide Area Network，WAN）——更准确地说,是取决于是否有 Windows Server 2008 或更新版本的可写域控制器——是否可用,因此你可能需要预先填充 RODC 的密码缓存。你可以使用图 9-21中所示的"预填充密码"按钮来预先填充密码缓存。单击此按钮后,你可以在 Active Directory 中搜索用户和计算机。选择了要预先填充缓存的用户和计算机之后,系统会显示一个类似于图 9-25的确认对话框。

如果出现任何错误,系统会显示一个类似于图 9-26的对话框,向你提示这些错误。所有密码成功预先填充的安全主体( Principal )都会出现在图 9-21所示的列表中。

使用 repadmin 管理缓存密码

Windows Server 2008 及更新版本附带的 *repadmin* 工具包含多个开关,可用于管理 RODC 的密码缓存。你可以使用 */rodcpwdrepl* 开关来指定一个或多个用户或计算机,让 RODC 立即请求复制其密码。此命令的语法(全部写在一行中)为:**`repadmin /rodcpwdrepl`** *`<RODC> <Hub DC> <user/computer distinguished name 1> <[user/computer distinguished name 2]...`***`>`**

例如,如果你要将用户 *bdesmond* 的密码从名为 *K8DEVDC01* 的可写域控制器(Read-Write Domain Controller,RWDC)复制到名为 *K8DEVRODC01* 的 RODC,可以运行:**`repadmin `****`/rodcpwdrepl`** *`K8DEVRODC01 `**`K8DEVDC01 cn=bdesmond,cn=users,`**`dc=k8dev01,dc=brianlab,`**`dc=local`*

还可以使用 *repadmin* 将 `msDS-AuthenticatedAtDC` 中的所有用户和/或计算机复制到 `msDS-RevealOnDemand` 列表中的某个组( Group )。若要运行此命令，必须使用以下语法指定只读域控制器( Read-Only Domain Controller ,RODC)和组：*repadmin /prp move* *`<RODC> <Group Name>`*。组名属性需要组的 `sAMAccountName` 值；如果找不到该组，将在域中的 Users 容器下创建它。如果要将 *K8DEVRODC01* 的 Auth-2 列表中的所有用户移动到名为 *RODC01-Allow* 的组，可以运行 *repadmin /prp move K8DEVRODC01 RODC01-Allow*。如果只想添加用户或计算机，可以追加 */users_only* 或 */comps_only* 开关。

本章介绍的其他几乎所有密码复制策略( Password Replication Policy ,PRP)管理任务都可以使用 *repadmin* 完成。可以运行 *repadmin /prp /?* 获取 *repadmin* 中与 PRP 相关的功能的完整列表。




![Password cache prepopulation confirmation](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663430.webp)


图 9-25. 密码缓存预填充确认




![Password prepopulation errors](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663431.webp)


图 9-26. 密码预填充错误

#### 只读域控制器( RODC )与写入请求

只读域控制器( RODC )内置了大量特殊逻辑,用于处理其从客户端接收的写入请求。最明显且常见的写入操作示例或许是用户或计算机的密码更改请求。其他常见示例包括动态 DNS 注册以及对登录时间戳信息的更新。

##### 用户密码更改

当用户更改密码时,RODC 的行为取决于用户所使用的密码更改机制(如 Kerberos 或 LDAP)以及客户端的操作系统。我们以最常见的场景为例:用户在工作站上按下 Ctrl-Alt-Delete,并选择“更改密码”选项。

运行 Windows Vista 及更高版本(以及 Windows Server 2008 及更高版本)的客户端将尝试通过 Kerberos 进行密码更改。当 RODC 收到 Kerberos 密码更改请求时,会将其转发至可写域控制器。RODC 还会立即请求该可写域控制器( RWDC )将该用户的密码复制到 RODC。随后,RWDC 将按照前面讨论的常规流程将该密码复制到 RODC。

在运行 Windows XP 或更早版本(以及运行 Windows Server 2003 或更早版本的服务器操作系统)的客户端上,客户端将直接联系可写域控制器,而 RODC 对此密码更改一无所知。当下次 RODC 与可写域控制器进行复制时,它会擦除该用户密码的本地副本。前面讨论的用户身份验证过程可确保,当用户下次尝试登录时,若条件允许,RODC 将再次缓存该用户的密码。

> **注意**：如果已加载先决条件中讨论的只读域控制器( Read-Only Domain Controller ,RODC)修补程序包( hotfix package )，客户端将联系 RODC 更改其密码，RODC 会将该请求链到可写域控制器( writable domain controller ,RWDC)。不过，仍不会请求立即复制该密码。

如果用户帐户密码更改请求是通过 LDAP 发出的（例如针对 Outlook Web Access 更改密码网页），则更改将直接在可写域控制器上进行。RODC 将不会知晓该密码更改，并且下一次 RODC 与可写域控制器进行复制时，它将删除该用户密码的本地副本。前面讨论的用户身份验证过程将确保下一次用户尝试登录时，如果允许，RODC 将再次缓存该用户的密码。

> **注意**：当 RODC 删除其密码的本地副本时，旧密码仍物理存储在活动目录( Active Directory ,AD)数据库中。但是，用户的复制元数据( replication metadata )会更新，使得在查询时，数据库报告该密码字段为 null。

##### 计算机帐户密码更改

当计算机尝试更改其密码时，它将通过其安全通道( secure channel )联系 RODC。RODC 会将该密码更改请求链到可写域控制器，并请求 RWDC 将新密码复制到 RODC。然后，RWDC 将遵循前面讨论的将密码复制到 RODC 的常规过程。

##### lastLogonTimeStampAttribute 属性

`lastLogonTimeStampAttribute` 有时会违背我们在本章中一直介绍的常理。如果用户或计算机的密码缓存在 RODC 上，并且 RODC 确定有必要更新 `lastLogonTimeStampAttribute` 属性，则该 RODC 将在本地向该用户或计算机的 `lastLogonTimeStampAttribute` 写入新时间戳( timestamp )。同时，RODC 会将 `lastLogonTimeStampAttribute` 更新转发到可写域控制器。由于转发的 `lastLogonTimeStampAttribute` 稍新，因此通过常规复制，RODC 中该用户或计算机的 `lastLogonTimeStampAttribute` 值将被覆盖为稍晚的值。

> **注意**：如果广域网( Wide Area Network ,WAN )不可用，或者只读域控制器( Read-Only Domain Controller ,RODC )无法联系可写的 Windows Server 2008 域控制器( Domain Controller ,DC )，则不会转发 `lastLogonTimeStampAttribute` 更新。

##### 上次登录统计信息

如果已按第 16 章所述启用了上次登录统计信息跟踪，RODC 将在本地写入对这些属性的更新。但是，与 `lastLogonTimeStampAttribute` 不同，RODC 将 *不会* 将这些更新转发到可写域控制器。

##### 登录成功/失败信息

当 RODC 成功处理登录时，它将在本地为用户或计算机写入 `last``Logon`、`logonCount` 和 `badPwdCount` 属性的新值。与可写域控制器一样，这些属性更改永远不会复制或链式转发到可写域控制器。如果 RODC 处理登录失败，它将更新 `badPwdTime` 和 `badPwdCount` 属性。同样，这些更改永远不会通过复制或链式转发离开 RODC。

##### NetLogon 安全通道更新

存储在 Active Directory 中的计算机账户的某些属性（例如计算机名称、`dNSHostName` 和操作系统信息）通过计算机的 NetLogon 安全通道提供给域控制器。当 RODC 收到这些更新时，它会将它们链式转发到可写域控制器。RODC 将发起对计算机对象立即复制的请求，如果允许缓存该计算机的密码，则该请求将成功。

##### 复制连接对象

RODC 上的知识一致性检查器( Knowledge Consistency Checker ,KCC )将在本地写入 RODC 为了复制到 RODC 数据库所需的连接对象。这些更改永远不会复制，并且在 RODC 之外不需要。

##### DNS 更新

只读域控制器( Read-Only Domain Controller ,RODC )利用DNS协议中的现有功能，以便向客户端返回一个可写的域控制器。当客户端准备进行动态DNS更新时，它首先会联系DNS服务器(在此情况下为RODC)，并通过访问区域的SOA(授权起始)记录，请求该区域的一个权威名称服务器。

当RODC为只读DNS区域生成SOA记录时，它会尝试寻找一个邻近的、运行Windows Server 2008或更新版本的可写域控制器，该控制器既是该区域的名称服务器，也是可达的。RODC通过域控制器定位器调用来完成这一过程。倘若RODC无法找到合适的Windows Server 2008或更新版本的域控制器，它将从可用名称服务器列表中随机选择一个非RODC本身的名称服务器。RODC在此过程中最终选定的名称服务器将被指定为SOA记录中的主服务器。

为了保持RODC本地DNS区域版本的更新，RODC会将从其在SOA记录中选择的主服务器复制客户端记录的请求排队。这种复制请求的排队是基于尽力而为的原则，意味着如果失败，RODC不会再次尝试为该DNS记录排队复制请求。相反，RODC将在下一个正常复制周期中接收该更新。

> **注意**：如果所涉记录的复制队列中已存在相应条目，则只读域控制器( Read-Only Domain Controller ,RODC )不会再次排队发出复制请求。

默认情况下，RODC 每五分钟处理一次复制队列，并尝试从队列中复制最多 100 个条目。对于队列中的每个条目，RODC 将验证该条目是否已存在至少 30 秒，否则将跳过该条目，并在下一个周期中尝试复制。默认情况下，当队列深度达到 300 个条目时，将不再加入新条目，直至队列深度降到 300 个条目以下。

> **警告**：`DsPollingInterval` 注册表设置除控制 DNS 复制队列处理的频率之外，还控制若干其他活动。这些活动主要包括查询 Active Directory 以获取 DNS 服务器上托管的 AD 集成 DNS 区域的更改。因此，修改此频率时应格外谨慎。

可使用五个注册表设置来控制 RODC DNS 服务复制动态更新 DNS 记录的尝试。所有这些注册表设置均位于 `HKLM\System\CurrentControlSet\Services\DNS\Parameters` 下。表 9-3详细说明了可配置的每个注册表设置。

> **注意**：表 9-3 中的所有注册表设置均为 `REG_DWORD` 值。

表 9-3. 只读 DNS 注册表设置

| 注册表值                         | 说明                                                         | 单位   | 默认值  | 最小值 | 最大值    |
| -------------------------------- | ------------------------------------------------------------ | ------ | ------- | ------ | --------- |
| `DsPollingInterval`              | 控制轮询线程的频率，DNS 服务使用该线程查询活动目录( Active Directory )，以获取所有 AD 集成的 DNS 配置设置。 | 秒     | `180`   | `30`   | `3600`    |
| `EnableRsoForRodc`               | 控制是启用还是禁用特殊的 DNS 记录复制行为。                   | 布尔值 | `TRUE`  | `FALSE` | `TRUE`    |
| `MaximumRodcRsoQueueLength`      | 指定在任意给定时刻复制队列中可包含的最大条目数。             | 条目   | `300`   | `1`    | `1000000` |
| `MaximumRodcRsoAttemptsPerCycle` | 指定只读域控制器( Read-Only Domain Controller ,RODC )在队列的任意一次处理过程中尝试复制的最大记录数。 | 条目   | `100`   | `1`    | `1000000` |
| `DsRemoteReplicationDelay`       | 指示 RODC 在为某条 DNS 记录排队复制请求与处理该请求之间等待的最小秒数。 | 秒     | `30`    | `5`    | `3600`    |

> **警告**：`MaximumRodcRsoAttemptsPerCycle` 设置的主要用途是限制针对可写域控制器( Writable Domain Controller )发动拒绝服务( Denial-of-Service ,DoS)攻击的可能性，此类攻击会通过一次性向该域控制器发送过多复制请求来对其进行洪泛。如果增大此值，请务必测量其对域控制器负载的影响。

在达到最大队列长度(默认 300 个条目)时，只读域控制器( Read-Only Domain Controller ,RODC)将在 DNS 服务器事件日志中记录一个事件(事件 ID 4400，消息为“*DNS 服务器正经历高 SOA 查询负载。这可能由大量执行更新的本地客户端计算机引起。与 SOA 查询对应的 DNS 记录的单对象复制( Single Object Replication )正受到限制。这可能会延迟对此 RODC DNS 服务器的更新复制，但计划复制( Scheduled Replication )不会受到影响*。”)，以指示此情况已发生；在队列得到处理且其深度降低之前，不会再将更多复制请求加入队列。如果频繁遇到此情况，您可能需要通过修改 `MaximumRodcRsoQueueLength` 注册表设置来增加最大队列长度。

> **注意**：该事件日志条目将每 24 小时记录一次。但是，如果重新启动 DNS 服务器服务，则在错误情况下一次出现后，将立即记录该事件。

#### W32Time 服务

通常，只读域控制器( Read-Only Domain Controller ,RODC )会与可写的 Windows Server 2008 及更高版本的域控制器( Domain Controller ,DC )同步时间。RODC 不会与另一个 RODC 同步时间。

当 RODC 收到来自客户端的时间同步请求时，其处理方式会因 RODC 是否缓存了该客户端的密码而有很大差异。如果 RODC 在本地缓存了客户端计算机的密码，则 RODC 能够像标准可写域控制器一样处理并签署时间同步请求。然而，如果 RODC 没有缓存客户端的密码，则必须有可写域控制器参与。

当 RODC 收到无法处理的时间同步请求时，涉及以下多个步骤:

1. RODC 将请求转发到 Windows Server 2008 或更高版本的可写域控制器。
2. 可写域控制器处理该请求，使用客户端计算机的密码对其进行签署，然后将响应返回给 RODC。
3. RODC 依次接收响应并将其转发给客户端，由客户端处理该响应。

为了处理请求和响应的转发，RODC 维护一个已转发客户端时间服务请求的本地表。此表称为*链接表*( chaining table )。该表包含三个字段:

- 客户端的 IP 地址（ IPv4 或 IPv6 ）
- 来自 NTP 请求的时间戳
- 客户端的 RID

当 RODC 收到来自可写域控制器的回复时，它会根据 RID 和请求时间戳在表中搜索匹配的请求。一旦 RODC 找到匹配项，就将响应转发回源 IP。

> **注意**：如果 RODC 在表中找不到匹配项,则 RODC 假定该请求由其自身发起。如果请求使用 RODC 的计算机账户密码进行签名,则 RODC 会根据需要更新其本地时钟。否则,RODC 将丢弃该响应。

默认情况下,RODC 链接表中的任何条目的最长生存时间最长为 4 秒,并且任何给定客户端(由客户端 IP 地址定义)在任何给定时间最多可在链接表中拥有 4 个条目。默认情况下,链接表总共最多可包含 128 个条目。如果超出上述任一上限,新请求将被直接丢弃,直到链接表有额外空间为止。

每次向链接表中添加新条目时,RODC 都会检查链接表并确定是否应删除任何条目。如果已使用的条目数超过最大条目数的 75%(默认情况下为 96 个条目),RODC 将检查链接表中是否存在过期条目。任何早于最长生存时间的条目都将被删除。

所有这些默认值均可通过多个注册表设置进行配置,如表 9-4所示。这些注册表设置位于 `HKLM\System\CurrentControlSet\Services\W32Time\TimeProviders\NtpServer` 下。

表 9-4. 链接表配置设置

| 注册表值              | 描述                                                         | 单位   | 默认值 | 最小值              | 最大值                 |
| --------------------- | ------------------------------------------------------------ | ------ | ------ | ------------------- | ---------------------- |
| `ChainDisable`        | 控制是否启用 RODC 对时间请求的链接。                         | 布尔值 | `0`    | `0`(启用链接)      | `1`(禁用链接)          |
| `ChainEntryTimeout`   | 控制链接表中条目的最长生存时间。                             | 秒     | `4`    | `4`                 | `16`                   |
| `ChainMaxEntries`     | 控制链接表中的最大条目数。                                   | 条目   | `128`  | `128`               | `1024`                 |
| `ChainMaxHostEntries` | 指定任何给定主机可在链接表中拥有的条目数。                   | 条目   | `4`    | `4`                 | `16`                   |

> **警告**：控制链接表大小的目的是确保链接表不会耗尽只读域控制器( Read-Only Domain Controller ,RODC )上的内存资源。如果增加 `ChainMaxEntries` 的值,请将此警告纳入考量。

如果在 RODC 上禁用密码链接行为(通过将 `ChainDisable` 设置为 `1`),则 RODC 除了能够与可写的 Windows Server 2008 及更新版本的域控制器通信外,还能够与下层域控制器(例如 Windows Server 2003)通信。如果进行此配置更改,RODC 将无法再处理客户端时间同步请求。

#### 应用程序兼容性

与对基础结构进行任何重大更改一样,在环境中大规模部署 RODC 之前,需要执行大量测试,以了解与 RODC 相关的应用程序行为问题。

尝试使用 LDAP 写入 Active Directory 的应用程序将从 RODC 收到指向可写域控制器的 LDAP 引用。只要应用程序能够*追踪*该引用,写入就会成功,并且下次 RODC 复制时,该写入将反映到本地。如果 WAN 中断,引用将失败。应用程序需要能够处理这种情况。

> **注意**：通过将 `RODCMode` 注册表值设置为 `1`,即可禁止只读域控制器( Read-Only Domain Controller ,RODC )发出写入引用( Write Referral )。`RODCMode` 注册表值是一个 `REG_DWORD` 类型值,位于 `HKLM\System\CurrentControlSet\Services\NTDS\Parameters`。

应用程序可能失败的另一种情形是:它期望写入结果能够立即在本地域控制器( Domain Controller ,DC )上读取到。只读域控制器兼容包所解决的其中一个问题,就是 Windows 打印后台处理程序( Print Spooler )服务中的一个缺陷。打印后台处理程序会通过 LDAP 将打印机发布到 Active Directory(这会触发指向可写域控制器的引用),随后立即尝试从本地域控制器读取已发布的打印机。如果该打印机不存在于本地域控制器上(本地只读域控制器正是这种情况),后台处理程序服务就会判定打印机发布失败。

如果应用程序使用旧版 RPC 调用来更改 Active Directory,而这些调用指向只读域控制器,那么这些 RPC 调用将会失败。要让写入操作成功,应用程序必须显式指向一台可写域控制器。只读域控制器随后会通过常规复制过程复制这些更改。

此外,如果你已将某些属性添加到筛选属性集( Filtered Attribute Set ,FAS )中,应用程序必须清楚:这些属性无法从只读域控制器上的 Active Directory 中获取。如果应用程序需要访问筛选属性集中的某个属性,就必须与可写域控制器通信。有关筛选属性集的详细信息,请参阅第 5 章。请记住,在多域林中,只有当林的功能级别( Functional Level )达到 Windows Server 2008 或更高时,才能强制实施筛选属性集。这是因为,同时也是全局编录( Global Catalog ,GC )的只读域控制器,可能会从 Windows Server 2003 域控制器复制某个全局编录命名上下文( Naming Context )。Windows Server 2003 域控制器并不识别筛选属性集,因此它们在向只读域控制器复制时,会把被筛选的属性一并包含进来。筛选发生在复制源端,而不是在只读域控制器端,因此只读域控制器会处理这些被筛选属性的入站复制,并将其存储到自己的数据库中。

通常情况下,你要做的最重要的事情就是测试环境中所有可能与只读域控制器( Read-Only Domain Controller ,RODC )通信的应用程序。你很可能会发现有些应用程序需要更新代码或从厂商处获取升级版本。有一个应用程序需要特别留意,即 Microsoft Exchange。Exchange 无法与 RODC 协同工作,因此不应将 Exchange 服务器与 RODC 共置于同一站点中。

> **注意**：Microsoft 已在[此链接](http://bit.ly/16WoHAR)中汇总了一份已知可与 RODC 协同工作的应用程序列表。

#### 只读域控制器( Read-Only Domain Controller ,RODC)放置注意事项

在网络中放置 RODC 时，设计过程中需要遵循一些规则并考虑若干事项。首先要记住的一条规则是：RODC 永远不会与其他 RODC 通信。

如果你打算在给定站点( site )中放置多台 RODC，就必须牢记这条重要规则。设想这样一种情况：某个分支机构为同一域( domain )部署了两台 RODC。我们称它们为 *RODC01* 和 *RODC02*。再假设有一名用户 *Brian* 在该站点工作。在 *RODC01* 上，Brian 的密码已缓存；但在 *RODC02* 上，Brian 的密码未缓存。当该站点的广域网( Wide Area Network ,WAN)不可用，且无法联系到可写域控制器( writable domain controller )时，Brian 尝试登录其工作站。Brian 的工作站联系 *RODC02*，由于广域网不可用且 *RODC02* 未缓存 Brian 的密码，登录失败。Brian 的工作站不会尝试联系其他域控制器，而只会直接告知 Brian 其密码无效。在一个站点中部署多台 RODC 可在必要时提供冗余，但也会带来很大的不可预测性。如果你计划向一个站点部署多台 RODC，我们建议你预先填充每台 RODC 的密码缓存，并通过自动化流程维护该缓存。

当在一组给定域之间创建信任( trust )时，Active Directory 中会创建一个称为 `trustedDomain` 的特殊类型对象，以表示该信任。`trustedDomain` 对象包含一个密码，用于与信任中的远程域通信。RODC 永远不会缓存信任密码，这意味着，只要由 RODC 提供服务的站点中的用户希望与受信任域中的资源通信，该 RODC 就必须转到可写域控制器以获取所需的 Kerberos 票据。即使用户希望访问的资源与用户位于同一站点，也是如此。如果广域网中断，用户将无法访问这些资源，因为无法联系到用户所在域的可写域控制器。

如果你将只读域控制器( Read-Only Domain Controller ,RODC )放置在外围网络( Perimeter Network )中,则需要特别留意需要写入 Active Directory 的应用程序,因为此类写入操作通常都会失败。此场景中的假设是,你将关闭防火墙( Firewall ),使外围网络中的成员服务器( Member Server )无法与受信任网络( Trusted Network )中的可写域控制器( Domain Controller ,DC)通信,因为如果不这样做,一开始在外围网络中部署 RODC 就毫无意义。应用程序将无法写入 Active Directory,因为 RODC 会向客户端无法联系的可写域控制器发出写入引用( Write Referral )。在此场景中,我们建议将之前讨论的 `RODCMode` 注册表设置设为 `1`。

为了使外围网络中的成员服务器能够成功进行动态 DNS 注册,你需要允许外围网络服务器在 TCP 和 UDP 端口 53 上联系可写域控制器。外围网络中的成员服务器进行域加入操作( Domain Join Operation )将失败,除非你在可写域控制器上预先创建计算机账户( Computer Account ),确保允许外围网络中的 RODC 缓存该计算机账户,然后用该计算机账户的密码预先填充 RODC 密码缓存。

> **注意**：为了使计算机账户( Computer Account )密码的预填充成功，你需要在尝试预填充缓存之前将其设置为非标准值。为此，你可以运行 *net user* *<ComputerName>$ <Password>*，在适当的位置替换计算机名称和密码。请确保在计算机名称中包含末尾的 *$*。

#### 管理员角色分离

对域控制器( Domain Controller ,DC)而言,一项常被期盼的功能,就是将域控制器硬件平台与操作系统的管理与 Active Directory 服务的管理分离开来。在可写域控制器( Writable Domain Controller ,RWDC)上,这根本无法实现,因为域控制器上的任何管理员都能做出一些更改,借此提升自己在整个林中的特权,最终导致林被入侵。只读域控制器( Read-Only Domain Controller ,RODC)引入了将操作系统管理控制权委派给第三方的能力,我们强烈建议您将此作为最佳实践,即使您所在的是 Active Directory 管理团队、负责管理 RODC 也不例外!

将 RODC 操作系统的管理权限委派给 Domain Admins 组以外的其他组,您就无需再以域管理员身份登录 RODC。在权衡这一建议时,请牢记"默认将 RODC 视为已被入侵"的思路。如果您使用拥有域管理员权限的帐户登录到一台已被入侵的 RODC,就可能泄露您的域管理员密码;又或者该操作系统已被篡改,会在您以域管理员身份登录时运行登录脚本,通过 RWDC 对目录做出破坏性更改。

您可以在 RODC 上配置多种不同的本地角色;不过我们预计,您最常配置的本地角色是管理员( Administrators )角色。可用角色列表如下:

- 管理员( Administrators )
- 用户( Users )
- 来宾( Guests )
- 远程桌面用户( Remote Desktop Users )
- 网络配置操作员( Network Configuration Operators )
- 性能监视器用户( Performance Monitor Users )
- 性能日志用户( Performance Log Users )
- 分布式 COM 用户( Distributed COM Users )
- IIS_IUSRS
- 加密操作员( Cryptographic Operators )
- 事件日志读取者( Event Log Readers )
- 证书服务 DCOM 访问( Certificate Service DCOM Access )
- 传入林信任构建者( Incoming Forest Trust Builders )
- 终端服务器许可证服务器( Terminal Server License Servers )
- Windows 2000 之前版本兼容访问( Pre-Windows 2000 Compatible Access )
- Windows 授权访问组( Windows Authorization Access Group )
- 服务器操作员( Server Operators )
- 复制器( Replicator )
- 帐户操作员( Account Operators )
- 备份操作员( Backup Operators )
- 打印操作员( Print Operators )

要在 RODC 上配置本地管理员( Administrators )角色,您既可以使用 *ntdsutil*,也可以使用 Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC)工具。ADUC 只允许您通过在 RODC 计算机帐户的 `managedBy` 属性中指定用户或组来配置该角色。图 9-27 展示了这一配置。当更新后的 `managedBy` 属性复制到 RODC 后,该更改即在该 RODC 上生效。

![Configuring RODC local administrators in ADUC](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663432.webp)

图 9-27. 在 ADUC 中配置 RODC 本地管理员

如果要配置 Administrators 角色以外的角色，或者希望通过命令提示符完成此配置，则需要使用 *ntdsutil*。若要将名为 *COHOVINES\RODC01-Admins* 的组添加到 *RODC01* 上的本地 Administrators 角色，可在启动 *ntdsutil* 后运行以下命令：

1. *local roles*
2. *connections*
3. *connect to server RODC01*
4. *quit*
5. *add COHOVINES\RODC01-Admins Administrators*

更改将立即生效，RODC01-Admins 组的成员将能够管理该 RODC，而无需担心他们会获得对域或林的管理访问权限。

> **注意**：作为本地管理员( Administrators )角色成员的用户，可以修改此角色以及其他本地角色的成员。

我们强烈建议你定义一个域组，使其对环境中的每个只读域控制器( Read-Only Domain Controller ,RODC )都具有本地管理员级别的访问权限。此组应仅包含在你的环境中不具备任何提升权限的帐户(即普通用户帐户)。你应使用这些帐户在 RODC 上执行所有管理功能。如果需要执行某项要求域级管理权限的管理任务，请以远程方式执行该任务，因为任何尝试以交互方式登录到 RODC 的行为(无论是在控制台还是通过终端服务)都可能导致系统被攻陷。

#### 提升只读域控制器

将服务器提升为只读域控制器( Read-Only Domain Controller ,RODC )时,需要在提升过程中回答几个额外的问题。图 9-28 展示了提升新的 RODC 时,服务器管理器( Server Manager )向您提出的问题。




![RODC promotion options](./image/9.%20Domain%20Controllers/httpatomoreillycomsourceoreillyimages1663433.webp)


图 9-28. RODC 提升选项

其中三个问题需要特别回答。首先,可以选择性地指定一个组(或用户),将 RODC 的管理权限委派给该组或用户,如管理员角色分离一节所述。如果在提升时还不确定,可以稍后随时进行更改。接下来,可以预先配置允许在 RODC 上缓存其密码的用户组。向导会为您预先配置此列表。同样,向导会预先填充不能缓存密码的用户组列表。当然,您也可以自定义此设置。

如果希望通过 PowerShell 提升 RODC,并使用表 9-5 中列出的参数,可以使用以下命令:


```
Install-ADDSDomainController `
-AllowPasswordReplicationAccountName  `
@("COHOVINES\Allowed RODC Password Replication Group") `
-NoGlobalCatalog:$false `
-CreateDnsDelegation:$false `
-CriticalReplicationOnly:$false `
-DatabasePath "C:\Windows\NTDS" `
-DelegatedAdministratorAccountName "COHOVINES\COHO-TOK-ADC01 Delegated Admins" `
-DenyPasswordReplicationAccountName  `
@("BUILTIN\Administrators", "BUILTIN\Server Operators", `
"BUILTIN\Backup Operators", "BUILTIN\Account Operators", `
"COHOVINES\Denied RODC Password Replication Group") `
-DomainName "cohovines.com" `
-InstallDns:$true `
-LogPath "C:\Windows\NTDS" `
-NoRebootOnCompletion:$false `
-ReadOnlyReplica:$true `
-SiteName "Tokyo" `
-SysvolPath "C:\Windows\SYSVOL" `
-SafeModeAdministratorPassword  `
(ConvertTo-SecureString -AsPlainText -Force -String "password") `
-Credential (Get-Credential)
```


表 9-5. RODC PowerShell 提升参数

| 参数                                  | 描述                                                         |
| ------------------------------------- | ------------------------------------------------------------ |
| `AllowPasswordReplicationAccountName` | 允许在只读域控制器( Read-Only Domain Controller ,RODC )上缓存密码的用户或组数组。 |
| `NoGlobalCatalog`                     | 指示此只读域控制器是否不应被设为全局目录服务器(注意这里的双重否定!)。 |
| `CreateDnsDelegation`                 | 指示是否应创建DNS委派。                                      |
| `CriticalReplicationOnly`             | 指示升级操作是执行所有复制还是仅执行关键复制。若将 `CriticalReplicationOnly` 设置为 `$true`,则一旦活动目录数据库的最低内容在本地完成复制,服务器将立即重启。重启后复制将继续,域控制器会尽快宣告自身可用。 |
| `DatabasePath`                        | *ntds.dit* 文件的存储位置。                                  |
| `DelegatedAdministratorAccountName`   | 被委派管理只读域控制器的用户或组。                           |
| `DenyPasswordReplicationAccountName`  | 不允许在只读域控制器上缓存密码的用户或组数组。               |
| `DomainName`                          | 要将只读域控制器提升到的域。                                 |
| `InstallDns`                          | 指示是否应在本地安装DNS服务器角色。                          |
| `LogPath`                             | 数据库事务日志文件的存储位置。                               |
| `NoRebootOnCompletion`                | 指示升级完成后是否重启服务器。若设置为 `$true`,则服务器在完成后不会重启。 |
| `SiteName`                            | 域控制器应提升到的活动目录站点( Active Directory Site )。   |
| `SysvolPath`                          | Sysvol共享的存储位置。                                       |
| `SafeModeAdministratorPassword`       | 目录服务还原模式( DS Restore Mode )的密码。                 |
| `Credential`                          | 用于访问目标域的凭据。                                       |

##### 预暂存 RODC 域控制器账户

如果考虑本节前面讨论过的默认受损范式,您可能会得出结论:使用域管理员账户提升只读域控制器( Read-Only Domain Controller ,RODC )并非最安全的选择。幸运的是,Active Directory 提供了一种解决方案,即 *Add-ADDSReadOnlyDomainControllerAccount* PowerShell cmdlet。该 cmdlet 会提前以域管理员身份完成所有必要工作,并允许您将 RODC 的提升权限委派给 Active Directory 中的任何用户或组。此功能具有双重优势:提高安全性,并且在您需要依赖初级资源完成 RODC 安装的情况下,允许您委派提升。

以下命令在 *cohovines.com* 域的 Tokyo 站点中为 *COHO-TOK-ADC01* 预创建 RODC 账户。它还将提升职责委派给 COHOVINES\COHO-TOK-ADC01 Delegated Admins 组。


```
Add-ADDSReadOnlyDomainControllerAccount `
 -AllowPasswordReplicationAccountName `
@("COHOVINES\Allowed RODC Password Replication Group") `
 -DomainControllerAccountName COHO-TOK-ADC01 `
 -DomainName cohovines.com `
 -DelegatedAdministratorAccountName "COHOVINES\COHO-TOK-ADC01 Delegated Admins" `
 -SiteName Tokyo `
 -DenyPasswordReplicationAccountName `
@("BUILTIN\Administrators", "BUILTIN\Server Operators", `
 "BUILTIN\Backup Operators", "BUILTIN\Account Operators", `
 "COHOVINES\Denied RODC Password Replication Group")
```


预创建 RODC 的账户后,作为 Delegated Admins 组的成员,您可以运行带有 -UseExistingAccount 开关的 *Install-ADDSDomainController* cmdlet(或服务器管理器向导)来完成 RODC 的提升。

> **注意**：若要在 Windows Server 2012 之前的 Windows 版本中预暂存 RODC 帐户，应改用 Active Directory 用户和计算机。要预暂存该帐户，请在 ADUC 中右键单击 Domain Controllers OU，然后单击“预创建只读域控制器帐户”。

要使用预暂存的帐户，请运行以下命令：*dcpromo /UseExistingAccount:Attach*。

### 9.4. 小结

在本章中，我们重点介绍了如何部署域控制器( Domain Controller ，DC)、域控制器的虚拟化，以及只读域控制器( Read-Only Domain Controller ，RODC)。部署域控制器是构建 Active Directory 安装环境以及林( Forest )迭代生命周期中的关键步骤，因为随着 Windows 新版本的发布，组织会将 Active Directory 升级到最新版本。

多年来，域控制器的虚拟化一直是 Active Directory 管理员们极为关注且争论不休的话题，而在 Windows Server 2012 中，微软正面应对了这些技术挑战。现在，对于托管在支持虚拟机生成 ID 的虚拟化主机平台上的 DC，您可以安全地回滚其快照，而不必担心对 Active Directory 造成影响。您还可以克隆虚拟域控制器，从而快速横向扩展 Active Directory 基础设施。

RODC 是 Active Directory 的一项重要功能，在许多组织的 Active Directory 部署中发挥着关键作用。对于位于物理位置不安全（例如分支机构）的域控制器，RODC 可缓解 Active Directory 所面临的关键安全风险。在本章中，我们探讨了 RODC 与可写域控制器之间的行为差异。

---

## 第 10 章 身份验证和安全协议

Active Directory 是网络上的核心安全组件，其中涉及的关键协议之一是 *Kerberos*，这是一种安全且灵活的身份验证协议，我们将在本章中详细探讨。幸运的是，Active Directory 抽象掉了该协议的大部分复杂性，因此只有少数几个配置场景值得关注。这些场景包括特定于服务的配置和 Kerberos 约束委派。

最后，我们将介绍 Active Directory 提供的一些安全功能，包括身份验证机制保证( Authentication Mechanism Assurance )和托管服务帐户( Managed Service Account )。

### 10.1. Kerberos

在任何基于 Active Directory 运行的网络中，Kerberos 安全协议( Kerberos Security Protocol )都是最基础的支撑之一。Kerberos 提供身份验证机制，为用户登录、应用程序访问以及域控制器( Domain Controller ,DC )之间的通信等提供支持。单独实现 Kerberos 是一项艰巨任务，而 Microsoft 几乎已通过 Active Directory 将其完全抽象化。开箱即用，几乎无需任何配置即可开始使用 Kerberos。事实上，如果你从未遇到需要专门进行 Kerberos 特定配置的应用程序，甚至根本无需知道 Kerberos 正在底层运行。

Kerberos 安全协议的关键优势在于，用户能够安全地证明自己的身份，随后以单点登录( Single Sign-On ,SSO )方式访问其他服务。事实上，借助 Kerberos，密码绝不会以明文或加密格式在网络上传输。取而代之的是，系统会通过各种票据( Ticket )生成会话专用密钥，供短时间内使用。本节将介绍该协议在关键场景中的工作方式。

#### 用户登录

第一个可能令人感兴趣的场景是：当用户坐到办公桌前并按下 Ctrl-Alt-Delete 时，用户登录是如何发生的。我们将专门探讨登录过程中的 Kerberos 层。

Kerberos 的单点登录( Single Sign-On )优势的关键在于登录过程的第一步：获取*票据授予票据*( Ticket Granting Ticket ,TGT)。当用户登录到工作站时，Windows 会缓存 TGT，并使用它获取服务票据( Service Ticket )，这样当用户想要访问网络中的服务时，无需再次提示用户输入凭据。

身份验证过程的第一步是客户端在身份验证服务请求( Authentication Service Request ,AS_REQ)数据包中出示*预身份验证请求*( Preauthentication Request )。图 10-1 显示了 *AS_REQ* 消息的内容。*AS_REQ* 包含必要的详细信息，以向域控制器( Domain Controller ,DC)证明客户端确实是其所声称的身份。这些详细信息包括：

- **客户端名称**

  这是用户的用户名。

- **服务名称**

  这是域控制器上 *krbtgt* 服务的服务主体名称( Service Principal Name ,SPN)。

- **客户端时间**

  为证明用户身份，客户端上的当前时间会使用用户密码的*哈希*进行加密。域控制器会尝试使用存储在 Active Directory 数据库中的密码哈希来解密此字段。随后会检查时间戳，确保其在容差范围内（默认 ±5 分钟），以防止重放攻击。

![The authentication service request packet](./image/10.%20Authentication%20and%20Security%20Protocols/httpatomoreillycomsourceoreillyimages1663434.webp)

图 10-1. 身份验证服务请求数据包

> **注意**：如果用户使用智能卡( Smart Card )而非用户名和密码登录,则会遵循略有不同的加密流程。此时不再使用用户密码的哈希值对时间进行加密,而是使用用户的私钥(存储在智能卡上)对时间戳进行加密。域控制器( Domain Controller ,DC)使用用户的公钥(存储在活动目录( Active Directory ,AD)中)来验证请求上签名的有效性,从而对用户进行身份验证。

一旦 DC 验证了身份验证请求,便准备好颁发票据授予票据( Ticket Granting Ticket ,TGT)。TGT 封装在 *AS_REP*(认证服务响应)数据包中,如图 10-2 所示。TGT 包含用户的访问令牌,以及一份用于此后客户端与 DC 之间通信的会话密钥副本。




![The authentication service response packet](./image/10.%20Authentication%20and%20Security%20Protocols/httpatomoreillycomsourceoreillyimages1663435.webp)


图 10-2. 认证服务响应数据包

*AS_REP* 消息中的字段如下:

- **客户端名称( Client Name )**

  即用户的用户名。

- **会话密钥( Session Key )**

  这是一个随机加密密钥,用于保护此后 DC 与客户端之间的通信。会话密钥使用用户密码的*哈希*进行加密。

- **生存期/过期时间( Lifetime/Expiry )**

  TGT 具有确定的生存期(默认为 10 小时)。10 小时后,必须续订 TGT,或重新发起身份验证请求。此字段同样使用用户密码的哈希进行加密。

- **票据授予票据( Ticket Granting Ticket )**

  TGT 是客户端缓存在内存中的组件,用于请求针对各项服务的票据。整个 TGT 使用密钥分发中心( Key Distribution Center ,KDC)密钥的哈希(具体而言,是 *krbtgt* 账户密码的哈希)进行加密。这意味着 TGT 是不透明的——客户端永远无法查看 TGT 内部。TGT 内部存储了一份会话密钥副本(以便 DC 解密将来与客户端之间的通信),以及一份票据过期信息副本。最重要的是,用户的访问令牌存储在 TGT 中。访问令牌包含重要信息,例如用户所属的组、用户的 NT 权限,以及动态访问控制( Dynamic Access Control ,DAC)声明。

客户端收到 *AS_REP* 消息后,会解密会话密钥,并将其与 TGT 一起缓存在内存中。此时,用户密码已不再必需,因为此后与 DC 的所有 Kerberos 通信都将使用会话密钥进行保护。

#### 服务访问

一旦票据授予票据( Ticket Granting Ticket ,TGT)可用，用户只需为相关服务请求服务票据( Service Ticket )，即可透明地开始访问网络中启用了 Kerberos 的服务。之前获取的 TGT 是域控制器( Domain Controller ,DC)所用的身份验证证明，因此无需用户再次提供其凭据。

启用了 Kerberos 的服务（有时称为 *Kerberos 化* 服务）几乎可以是网络中的任何内容。通常包括文件和打印服务器、网站和数据库，但唯一的限制是应用程序能否通过 Kerberos 接受身份验证。客户端以*服务主体名称* ( Service Principal Name ,SPN)的形式标识要访问的服务。

##### 服务主体名称

正如用户在目录中通过唯一的用户主体名称( User Principal Name ,UPN )来标识一样，服务也通过一个或多个唯一的服务主体名称( Service Principal Name ,SPN )来标识。SPN 是客户端向域控制器( Domain Controller ,DC )请求特定服务票证时使用的标识符。

从根本上讲，SPN 的构造形式为服务标识符后跟主机名 — 例如 `service/host`。服务组件是客户端和服务器预先约定好的字符串 — 例如,访问文件共享使用 `cifs` 服务名称。主机名可以是服务器或服务的短名称,也可以是服务器或服务的完全限定域名( FQDN )。通常,短名称和长名称都会注册。例如,一个名为 *WEB01.cohovines.com* 的 Web 服务器会在 Active Directory 中注册以下 SPN:

- `http/WEB01`
- `http/WEB01.cohovines.com`

如果服务器需要,SPN 还可以包含可选的端口号。Microsoft SQL Server 就是一个将端口号添加到 SPN 中的产品示例。一个名为 *DB01.cohovines.com* 的 SQL 服务器会在 Active Directory 中注册以下 SPN:

- `MSSQLSvc/DB01:1433`
- `MSSQLSvc/DB01.cohovines.com:1433`

关于 SPN 构造,最重要的结论是:SPN 中的服务组件和主机名组件本质上是任意的。客户端应用程序为请求服务票证而构造的 SPN,只需与服务器在 Active Directory 中注册的 SPN 相匹配即可。

SPN 存储在 Active Directory 的 `servicePrincipalName` 多值属性中。用户、计算机和托管服务账户都具有 `servicePrincipalName` 属性。服务的 SPN 必须注册在运行该服务的账户上。如果应用程序在标准用户或托管服务账户下运行,SPN 应注册在该对象上。如果应用程序以*本地系统*或*网络服务*身份运行,SPN 应注册在计算机对象上。

你可以使用 ADSI Edit 或 AD 用户和计算机中的属性编辑器等工具,将 SPN 直接添加到目标对象的 `servicePrincipalName` 属性中来注册 SPN。你也可以使用 *setspn.exe* 命令行工具。

*setspn.exe* 的优势在于,你还可以在注册服务主体名称( Service Principal Name ,SPN)之前搜索是否存在重复项。例如,要在服务器 *DB01* 上注册前面讨论过的 SQL Server SPN,且 SQL Server 正以 *svc.DB01SQL* 用户帐户运行,则可执行以下命令:


```
setspn -s MSSQLSvc/DB01:1433 svc.DB01SQL
setspn -s MSSQLSvc/DB01.cohovines.com:1433 svc.DB01SQL
```


你还可以使用 *setspn.exe* 工具注销(删除)SPN、搜索现有的 SPN 注册信息,或检查整个林( Forest )中是否存在重复的 SPN。如需了解 *setspn.exe* 的完整参数列表,请访问 http://bit.ly/WRjA0A。

> **注意**：有关如何查找重复的服务主体名称( Service Principal Name ,SPN )以及出现重复项时会发生什么情况的讨论，请查看 http://bit.ly/X4KlA9。

##### 服务票证( Service Ticket )

从根本上说，当用户首次决定访问某个服务时，会在票证授予服务请求( Ticket Granting Service Request ,TGS_REQ )数据包中构造一个服务票证请求。*TGS_REQ* 包含图 10-3中所示的字段。这些字段包括：

- **服务主体( Service Principal )**

  这是唯一标识用户尝试连接到的服务的 SPN。

- **客户端名称( Client Name )**

  这是用户的用户名。此字段使用在身份验证过程中建立的会话密钥( session key )加密。

- **时间戳( Timestamp )**

  此字段用于防止重放攻击( replay attack )，确保请求不会在较长时间内被重复使用。默认情况下，请求仅在服务器时钟前后五分钟内有效。此字段也使用会话密钥加密。

- **票证授予票证( Ticket Granting Ticket ,TGT )**

  请求中包含 TGT 的副本。域控制器( Domain Controller ,DC )使用它来为服务构建访问令牌( access token )，并确保用户确实已经过身份验证（且 TGT 尚未过期）。




![The ticket granting service request packet](./image/10.%20Authentication%20and%20Security%20Protocols/httpatomoreillycomsourceoreillyimages1663436.webp)


图 10-3. 票证授予服务请求数据包

当 DC 收到 *TGS_REQ* 消息时，它首先尝试将服务名称( Service Name )字段与 Active Directory 中匹配的 `servicePrincipalName` 值进行匹配。此过程分为两步。首先，执行标准搜索，以确定能否找到显式匹配。如果未找到显式匹配，Active Directory 会检查隐式匹配。

每个具有一个或多个使用 `HOST` 服务名称的 SPN 的帐户（例如 `HOST/SRV01.cohovines.com`）都会通过隐式匹配过程自动获得数十个额外 SPN。此过程的目的是限制重复数据量。如果不存在此隐式匹配过程，表 10-1中的 52 个条目将会在 AD 中的每一个计算机帐户( computer account )上重复出现！

> **注意**：你可以通过编辑配置命名上下文( Configuration NC )中 `CN=Directory Service,CN=Windows NT,CN=Services` 对象的 `sPNMappings` 属性,自定义隐式映射的 SPN 列表。你可以为 `HOST` 服务名称添加额外的映射,也可以为其他服务名称添加隐式映射。

SPN 查找过程可能会产生以下几种结果:

- 找到匹配项,可以颁发服务票证。
- 找到多个匹配项(林内存在重复的 `servicePrincipalName` 属性值)。此时会返回错误,因为 Active Directory 无法确定实际需要的是哪一个匹配项。
- 未找到匹配项。返回错误。

隐式映射到 `HOST` 的默认 SPN 列表见表 10-1。

表 10-1. 隐式 HOST SPN 映射

| `alerter`     | `fax`       | `plugplay`         | `schedule` |
| ------------- | ----------- | ------------------ | ---------- |
| `appmgmt`     | `http`      | `policyagent`      | `scm`      |
| `browser`     | `ias`       | `protectedstorage` | `seclogon` |
| `cifs`        | `iisadmin`  | `rasman`           | `snmp`     |
| `cisvc`       | `messenger` | `remoteaccess`     | `spooler`  |
| `clipsrv`     | `msiserver` | `replicator`       | `tapisrv`  |
| `dcom`        | `mcsvc`     | `rpc`              | `time`     |
| `dhcp`        | `netdde`    | `rpclocator`       | `trksvr`   |
| `dmserver`    | `netddedsm` | `rpcss`            | `trkwks`   |
| `dns`         | `netlogon`  | `rsvp`             | `ups`      |
| `dnscache`    | `netman`    | `samss`            | `w3svc`    |
| `eventlog`    | `nmagent`   | `scardsvr`         | `wins`     |
| `eventsystem` | `oakley`    | `scesrv`           | `www`      |

假设 *TGS_REQ* 中的服务名称( Service Name )字段一切校验通过,域控制器( Domain Controller ,DC)将验证 TGT(例如确认其未过期),然后继续为相关服务向客户端颁发服务票证。该票证通过 *TGS_REP*(票证授予服务响应,Ticket Granting Service Response)数据包颁发,如图 10-4 所示。




![The ticket granting service response packet](./image/10.%20Authentication%20and%20Security%20Protocols/httpatomoreillycomsourceoreillyimages1663437.webp)


图 10-4. 票证授予服务响应数据包

*TGS_REP* 包含以下字段:

- **服务主体**( Service Principal )

这是服务票据所针对服务的 SPN。此字段使用身份验证过程中先前建立的会话密钥进行加密。

- **时间戳( Timestamp )**

  消息的时间戳,用于防止重放攻击。此字段同样使用身份验证过程中先前建立的会话密钥进行加密。

- **服务会话密钥( Service Session Key )**

  这是客户端缓存的第二个密钥,用于加密与特定服务的通信。此字段同样使用身份验证过程中先前建立的会话密钥进行加密。

- **服务票据( Service Ticket )**

  服务票据是客户端向服务出示以请求访问权限的凭证,并会缓存在内存中以供后续访问该服务时使用。与 TGT 类似,服务票据对客户端而言是不透明的——它使用服务密码的哈希进行加密。服务票据包含客户端名称、服务的 SPN 、客户端将用于加密与服务通信的服务会话密钥副本,以及时间戳。服务票据内部包含用户 TGT 最初颁发时所计算出的访问令牌副本。服务可以使用这些信息(例如组成员身份)来授权用户对该服务的访问。与 TGT 一样,服务票据包含到期日期,超过该日期后需要续订票据才能继续使用。

#### 应用程序访问

客户端( Client )一旦拥有针对某个服务( Service )的服务票证( Service Ticket )，便会将该票证出示给服务以请求访问。服务票证通过 *AP_REQ* 消息出示给服务。与到目前为止讨论的消息不同，*AP_REQ* 消息针对每个应用程序以不同方式呈现。例如，对于 Web 应用程序，该消息编码在 HTTP 标头中，而 LDAP 则期望在绑定请求中接收它。

应用程序还可以可选地支持*相互身份验证*( Mutual Authentication )（即服务向客户端证明自身身份），这是通过使用 *AP_REP* 消息实现的。此功能是可选的，并且在大多数情况下未实现。

#### 登录和服务访问摘要

图 10-5 总结了目前为止我们讨论的过程。回顾一下，当用户登录到其工作站并尝试访问服务时，将执行以下步骤：

1. 发送 *AS_REQ* 消息以开始身份验证过程。该消息通过使用用户密码的*哈希( Hash )*加密一条消息来证明用户身份。使用哈希可确保实际密码永远不会通过网络传输。
2. 域控制器( Domain Controller ,DC)验证该请求并生成票证授予票证( Ticket Granting Ticket ,TGT)。TGT 通过 *AS_REP* 消息发回。客户端将 TGT 缓存在内存中，并将其用于后续的服务票证( Service Ticket )请求。
3. 客户端向 DC 发送 *TGS_REQ* 消息，以请求特定服务的服务票证。客户端不再重新提供凭据，而是发送在步骤 2 之后缓存在内存中的 TGT。
4. DC 验证 *TGS_REQ* 并为该服务构造服务票证。该服务票证使用服务密钥的哈希进行加密，并通过 *TGS_REP* 消息发回客户端。客户端将此票证缓存在内存中，以便随后直接对服务进行身份验证时使用。
5. 客户端在 *AP_REQ* 消息中向服务出示服务票证。服务使用该票证对用户进行身份验证。服务还可能使用包含在票证中的用户访问令牌( Access Token )来执行授权，然后再允许访问。
6. 可选地，服务可通过 *AP_REQ* 消息进行响应，以进行服务的相互身份验证( Mutual Authentication )。这并不特别常见，且完全是可选的。

![Kerberos message flow summary](./image/10.%20Authentication%20and%20Security%20Protocols/httpatomoreillycomsourceoreillyimages1663438.webp)

图 10-5. Kerberos 消息流摘要

在遵循此过程时，你可以看到 Kerberos 如何实现单点登录( Single Sign-On ,SSO)以及更高程度的安全性。由于 TGT 缓存在客户端的内存中，用户密码不再必要，可以丢弃。在 TGT 的生存期内，客户端可以根据需要多次向域控制器出示 TGT，以请求网络中特定服务的服务票证。然后，这些服务票证会缓存在客户端的内存中，并在客户端需要向服务进行身份验证时随时出示给服务。

#### 委派与协议转换

应用程序经常使用的一项 Kerberos 功能——尤其是带有数据库层的 Web 应用程序——称为 *Kerberos 约束委派* ( Kerberos Constrained Delegation ,KCD)。稍后我们会看到，KCD 使应用程序能够模拟用户，并以该用户身份向另一服务发出请求。

KCD 的扩展是一项称为 *协议转换* ( Protocol Transition )的功能，单点登录网关( Single Sign-On Gateway )经常使用它。在这两种情况下，配置这些功能都可能有些棘手。

##### 委派( Delegation )

应用程序在需要呈现（或修改）来自另一系统的数据时，通常会使用几种常见模型。第一种模型称为*受信任子系统*( Trusted Subsystem )，如图 10-6所示。在受信任子系统模型中，用户向应用程序（此处为 Web 服务器）进行身份验证，随后对数据的所有授权均由应用程序执行。应用程序使用共享服务账户向数据库发出请求。




![Trusted subsystem model](./image/10.%20Authentication%20and%20Security%20Protocols/httpatomoreillycomsourceoreillyimages1663439.webp)


图 10-6. 受信任子系统模型

受信任子系统模型的缺点是，应用程序负责实现授权模型。另一种方法是依赖后端系统（此处为 SQL 服务器）执行授权，并仅返回允许用户访问的数据，如图 10-7所示。为实现这一点，Web 服务器在连接到后端 SQL 服务器时必须模拟每个用户。




![Delegated access to a backend service](./image/10.%20Authentication%20and%20Security%20Protocols/httpatomoreillycomsourceoreillyimages1663440.webp)


图 10-7. 对后端服务的委派访问

要执行此模拟，Web 服务器需要能够为每个用户请求用于 SQL 服务器的服务票证( Service Ticket )。为了接收服务票证，Web 服务器完成以下步骤（图 10-8）：

1. 用户请求发往前端服务的服务票证。
2. 用户将该服务票证作为请求的一部分提交给前端服务器。
3. 前端服务器将用户的服务票证提交给域控制器( Domain Controller ,DC)，并为用户请求发往后端服务的服务票证。
4. 前端服务器将该服务票证提交给后端服务，并在用户的上下文中与该服务交互。




![Kerberos message flow during delegation](./image/10.%20Authentication%20and%20Security%20Protocols/httpatomoreillycomsourceoreillyimages1663441.webp)


图 10-8. 委派期间的 Kerberos 消息流

此过程称为*委派*。由于第三方服务被授予模拟用户并访问另一服务的权限，因此这是一项敏感操作。因此，服务不能在未经授权的情况下直接执行此操作。

在 Active Directory 中，授权以允许某个服务委派给其他特定服务的形式授予。这称为*约束委派( Constrained Delegation )*。配置委派最简单的方法是通过 AD 用户和计算机( ADUC ) MMC 管理单元中的"委派"选项卡。

委派在前端服务的账户上配置为委派到一个或多个服务主体名称( Service Principal Name ,SPN )的权限。请记住，如果服务以该账户运行，则使用服务账户(或托管服务账户)；如果服务以*本地系统( Local System )*或*网络服务( Network Service )*运行，则使用计算机账户。

假设有一个场景：在 *COHO-CHI-WEB01* 服务器上以*网络服务( Network Service )*运行的 Web 应用程序需要委派到一台 SQL 服务器，该服务器以 *svc.DB01Service* 用户账户运行，SPN 为 `MSSQLSvc/DB01.cohovines.com:1433`。要配置此委派，请在 ADUC 中找到 *COHO-CHI-WEB01* 计算机账户：

1. 选择图 10-9中所示的"委派"选项卡。

   > **注意**：如果在用户账户上配置委派，则仅当该用户上注册了一个或多个 SPN，或者该用户账户已配置为允许委派到某个服务时，"委派"选项卡才可见。您可以向账户添加一个临时的虚假 SPN，也可以将可委派的 SPN 直接添加到 `msDS-AllowedToDelegateTo` 属性。

2. 选择"信任此计算机以委派给指定服务"。

   > **警告**：图 10-9中所示的"信任此计算机以委派给任何服务(仅 Kerberos)"选项称为*无约束委派( Unconstrained Delegation )*。这是 Windows 2000 中唯一受支持的选项，极其危险。如果启用此选项，前端服务可以将经过身份验证的用户模拟到网络上的任何服务！

   未经全面的风险评估，不应使用无约束委派。

3. 单击"添加"，然后单击"用户或计算机"。

4. 找到 *svc.DB01Service*。单击"确定"。

5. 选择要委派到的 SPN，如图 10-10所示。

6. 单击"确定"。




![Service delegation configuration](./image/10.%20Authentication%20and%20Security%20Protocols/httpatomoreillycomsourceoreillyimages1663442.png.webp)


图 10-9. 服务委派配置




![Adding services for delegation](./image/10.%20Authentication%20and%20Security%20Protocols/httpatomoreillycomsourceoreillyimages1663443.png.webp)


图 10-10. 添加委派的服务

要让 *COHO-CHI-WEB01* 服务器能够委派到 `MSSQLSvc/DB01.cohovines.com:1433` 这个 SPN,以上设置就已足够。如果您运行的是 Windows Server 2012 并满足以下要求,还可以使用 Windows PowerShell 以另一种方式配置委派:

- 前端服务运行在 Windows Server 2012 或 Windows 8 计算机上。
- 后端服务运行在 Windows Server 2003 或更高版本的计算机上。
- 前端服务所在域中至少存在一台 Windows Server 2012 域控制器( Domain Controller ,DC)。
- 后端服务所在域中至少存在一台 Windows Server 2012 域控制器。

前面我们讨论过,您需要配置一份主体( Principal )列表,以指定前端服务可以委派到哪些对象;而在新模型中,则是在后端服务上配置一份允许向它进行委派的主体列表。现在,您还可以在 Active Directory 中委派权限来配置约束委派( Constrained Delegation )。

若要配置前面讨论的场景,您可以运行以下 PowerShell 命令:




```
Set-ADUser svc.DB01Service -PrincipalsAllowedToDelegateToAccount COHO-CHI-WEB01$
```


该模型还支持跨域边界实现 Kerberos 约束委派( Kerberos Constrained Delegation ,KCD )。此前,只有当前端服务与后端服务的标识位于同一域中时,才能执行 KCD。

##### 协议转换（Protocol Transition）

协议转换（Protocol Transition）是受约束的 Kerberos 委派（Kerberos Constrained Delegation，KCD）中一种高度敏感的变体，它允许在不向域控制器（Domain Controller，DC）出示用户服务票证以证明用户已通过前端服务身份验证的情况下执行委派。此功能通常被具有友好的基于表单身份验证功能的基于 Web 的单一登录（Single Sign-On，SSO）应用程序所使用。用户无需向应用程序出示服务票证，而是直接向应用程序进行身份验证，例如输入其 Active Directory 凭据或应用程序可识别的另一组凭据。

接下来，应用程序以用户的名义向 Active Directory 请求特定服务的服务票证。由于此操作要求前端服务受信任，以便在不证明用户已通过身份验证的情况下为用户请求服务票证，因此必须授予额外的访问权限。配置 KCD 时，通过在图 10-9中选择“Any Protocol”选项即可授予此访问权限。

### 10.2. 身份验证机制保证(Authentication Mechanism Assurance,AMA)

*身份验证机制保证* (Authentication Mechanism Assurance,AMA)是 Windows Server 2008 R2 中引入的一项功能,用于根据用户访问网络时所使用的智能卡证书,为其提供对资源的条件访问。通常,当依据已确认的用户身份保证级别向用户颁发不同类型的证书时,会使用此功能。例如,一种保证级别可能仅与用户入职时验证其政府签发的带照片身份证件相关联,而另一种保证级别则可能涉及两种形式的身份证件以及一次背景调查。

颁发智能卡证书时,证书会包含标识其各种属性的对象标识符(Object Identifier,OID)。其中一项属性可能就是与证书颁发对象用户相对应的保证级别。

借助 AMA,Active Directory 可以在登录时,根据用户智能卡证书中是否存在某个 OID,动态地将组的 SID 注入到用户的访问令牌中。这样便可动态地保护资源,使其只有在用户使用具有特定属性的证书访问网络时才可被访问。随后,你可以在访问控制列表(Access Control List,ACL)、应用程序等中检查该组是否存在。

由于此功能不常实施,如果你要使用该功能,我们建议你参考 Microsoft 的 AMA 分步实施指南。该指南位于 http://bit.ly/YDlBev。

### 10.3. 托管服务帐户( Managed Service Accounts ,MSA)

服务帐户代表许多组织安全计划中的一个缺口。普通用户帐户通常有定义完善的密码策略以及与之关联的取消预配过程。而服务帐户通常这两项关键安全策略都未应用。IT 组织采取捷径也并非罕见，例如在应用程序之间共享服务帐户，或在多个服务帐户中使用同一密码。

所有这些问题都会导致服务帐户领域出现安全缺口。当 IT 人员离开组织时，关于服务帐户及其密码的知识也随之离开。由于这些密码通常设置为永不过期，而且极少（如果有过）更改，加之服务帐户通常拥有提升的访问权限，因此存在一个明显的安全漏洞：前员工可能仍能访问这些帐户。鉴于服务帐户在组织 IT 基础设施中的角色，它们对攻击者而言也是极具吸引力的目标。

*托管服务帐户( Managed Service Accounts ,MSA)* 是 Microsoft 在 Windows Server 2008 R2 中首次引入的功能，用于帮助缓解此风险。Windows Server 2012 引入了大幅改进的 MSA 版本，称为 *组托管服务帐户( Group Managed Service Accounts ,gMSA)*。在这两种情况下，MSA 都是一种特殊类型的安全主体( Security Principal )，服务、IIS 应用程序池，有时还有计划任务，可以以其身份运行。MSA（和 gMSA）不使用常规密码，而是与目录建立机密，然后默认每 90 天轮换该密码。这缓解了服务帐户涉及的风险。

遗憾的是，Windows Server 2008 R2 中第一版 MSA 有一个关键限制：服务在给定时间只能在一台服务器上运行，因为当时没有在服务器之间传递密码的机制。这限制了 MSA 的实用性，尤其是在群集和负载均衡方案中。幸运的是，Windows Server 2012 中引入的 gMSA 解决了此问题。

#### 为组托管服务帐户做好准备

在开始使用 gMSA 之前，需要准备 Active Directory。要在其中创建 gMSA 的域中，至少需要一台 Windows Server 2012 域控制器( Domain Controller ,DC)。Windows Server 2012 DC 运行新的组密钥分发服务( Group Key Distribution Service ,GKDS)。KDS 负责计算 gMSA 密码，并将这些密码提供给已授权的客户端。

> **注意**：gMSA 可以认证到任意域控制器( Domain Controller ,DC )。密码管理操作仅要求使用 Windows Server 2012 域控制器。

在域中开始使用 gMSA 之前,必须为该域创建密钥分发服务( Key Distribution Service ,KDS )根密钥。可以使用 *Add-KdsRootKey* PowerShell cmdlet 完成此操作。默认情况下,仅运行 *Add-KdsRootKey* 生成的 KDS 根密钥在 10 天内不会生效。这样设计是为了让密钥在生效之前传播到所有 Windows Server 2012 域控制器。

如果希望密钥立即生效,请运行 *Add-KdsRootKey* *-EffectiveImmediately*。您也可以在创建时修改生效日期。例如,如果您知道域将在 8 小时内收敛,可以运行以下命令创建 8 小时后生效的密钥:

```
$effectiveDate = (Get-Date).AddHours(8)
Add-KdsRootKey -EffectiveDate $effectiveDate
```

生成根密钥并使其生效后,即可开始使用 gMSA。

#### 使用组托管服务账户

要使用 gMSA,客户端必须是 Windows 8 或 Windows Server 2012。gMSA 支持传统 Windows 服务、IIS 应用程序池和计划任务。很少有应用程序支持在安装过程中原生指定 gMSA,因此很可能需要使用传统服务账户安装应用程序,然后稍后通过服务 MMC 管理单元更改应用程序的身份。

> **警告**：虽然此技巧对大多数应用程序都应有效，但有些应用程序可能依赖于安装期间指定的服务账户的 SID 或用户名。在这种情况下，使用服务管理单元更改服务账户会导致应用程序无法正常工作。

作为示例，我们将配置一个 Internet 信息服务( Internet Information Services ,IIS)应用程序池以使用新的组托管服务账户( Group Managed Service Account ,gMSA)。第一步是预配 gMSA。目前没有可用的图形用户界面( Graphical User Interface ,GUI)选项，因此必须通过 Windows PowerShell 完成此任务。要创建 gMSA，请运行以下命令：




```
New-ADServiceAccount `
-SamAccountName svc.cohowebsite `
-Name svc.cohowebsite `
-DisplayName "Coho Vines Website" `
-DNSHostName "www.cohovines.com" `
-PrincipalsAllowedToRetrieveManagedPassword `
@("COHO-CHI-WEB01$", "COHO-CHI-WEB02$")
```


在此命令中，我们指定以下参数：

- **SamAccountName**

  要分配给服务账户的用户名。Windows 会自动在账户末尾追加美元符号(*$*)。注意：您可能想知道为什么 Windows 会在您指定的 *SamAccountName* 值末尾追加 *$*。一个可能有助于进一步理解托管服务账户( Managed Service Account ,MSA)(以及 gMSA)的小知识是：它们派生自架构中的 `computer` 对象类。这意味着除了 MSA 对象类特有的属性之外，它们还继承 `computer` 类的所有属性。

- **Name**

  这对应于 Active Directory 中对象的 `name` 属性。对于此字段，我们通常使用与 *SamAccountName* 相同的值。

- **DisplayName**

  在管理工具中显示的友好名称。

- **DNSHostName**

  对应于服务的 DNS FQDN。注意：如果此参数不适用于您的场景，您可以输入一个虚假值。

- **PrincipalsAllowedToRetrievePassword**

  AD 中可检索该账户密码的对象列表。这通常是一个包含运行该服务的计算机的组，或者一个计算机对象列表。在本示例中，我们指定了该服务将在其上运行的计算机。

> **注意**：如果使用组控制对组托管服务账户( Group Managed Service Account ,gMSA)的访问，则需要先重新启动组成员，然后这些成员才能开始使用 gMSA。

除此处列出的参数外，*New-ADServiceAccount* cmdlet 还有许多其他有用的参数。可访问 http://bit.ly/ZQjFll 查看完整列表，或运行 `Get-Help New-ADServiceAccount -Detailed` 查看。

创建托管服务账户( Managed Service Account ,MSA)后，必须将其安装到将使用该 MSA 的服务器上。此过程很简单，可通过 *Install-ADServiceAccount* cmdlet 完成。*Install-ADServiceAccount* cmdlet 是 Active Directory PowerShell 模块的一部分。如果尚未在要安装 MSA 的服务器上安装此模块，请运行 `Install-WindowsFeature RSAT-AD-PowerShell` 进行安装。

若要安装前面创建的 gMSA，请运行 `Install-ADServiceAccount svc.cohowebsite`。接下来，配置 IIS 应用程序池( IIS Application Pool )。为了表明这是 MSA，需要在用户名后追加美元符号( *$* )，并将密码字段留空，如图 10-11所示。




![IIS application pool credential configuration](./image/10.%20Authentication%20and%20Security%20Protocols/httpatomoreillycomsourceoreillyimages1663444.png.webp)


图 10-11. IIS 应用程序池凭据配置

对于服务，也应采用相同方法：指定用户名时在其后附加 *$*，并将密码字段留空。计划任务( Scheduled Task )则略为复杂，因为任务计划程序图形界面( Task Scheduler GUI )不支持 MSA。因此，需要改用命令行创建该计划任务。以下示例创建一个任务，该任务使用 *svc.BatchJob* gMSA 每天凌晨 3 点运行名为 *C:\Scripts\ScheduledBatch.bat* 的虚构批处理脚本（每条命令应位于单行）：


```
$taskAction = New-ScheduledTaskAction -Execute "C:\Scripts\ScheduledBatch.bat"
$taskSchedule = New-ScheduledTaskTrigger -Daily -At 3AM
$taskIdentity = New-ScheduledTaskPrincipal -UserId COHOVINES\svc.BatchJob$ `
-LogonType Password

Register-ScheduledTask -TaskName "Scheduled Batch" -Action $taskAction `
-Trigger $taskSchedule -Principal $taskIdentity
```


有关本示例中使用的每个 cmdlet 的详细信息，请参阅以下链接：

- [New-ScheduledTaskAction](http://bit.ly/16TPLAS)
- [New-ScheduledTaskTrigger](http://bit.ly/108qTid)
- [New-ScheduledTaskPrincipal](http://bit.ly/YaOO3K)
- [Register-ScheduledTask](http://bit.ly/11DMXYq)

在计划任务开始生效之前,你还需要为托管服务账户( Managed Service Account ,MSA)授予"作为批处理作业登录"这一 Windows 权限。可通过组策略或服务器的本地安全策略完成此操作。要在本地服务器上完成更改,请启动本地安全策略编辑器(依次单击"开始"→"运行"→`**`secpol.msc`**`),然后浏览至*本地策略\用户权限分配*,如图 10-12所示。将 MSA 添加到"作为批处理作业登录"权限中。


![Local Security Policy Editor](./image/10.%20Authentication%20and%20Security%20Protocols/httpatomoreillycomsourceoreillyimages1663445.png.webp)


图 10-12. 本地安全策略编辑器

### 10.4. 小结

在本章中,我们探讨了整体活动目录( Active Directory )基础架构的一项关键功能——Kerberos。Kerberos 安全协议用于对网络及网络中的服务进行身份验证。我们还了解了常见的 Kerberos 配置需求——Kerberos 约束委派( Kerberos Constrained Delegation )。最后,我们了解了活动目录的安全功能,例如身份验证机制保证( Authentication Mechanism Assurance )和托管服务账户( Managed Service Account )。
