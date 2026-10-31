---
summary: Microsoft Windows 安全基础知识（下册），涵盖网络安全防御、无线与物理安全防护、数据加密技术、BitLocker以及PKI证书体系。
---

## 第7章 保护网络

**攻击者无处不在**，持续不断地试图攻击网络。有些使用常见的已知方法，另一些则试图学习并利用新方法。了解当今使用的不同类型的攻击以及可用于保护网络的一些常用方法至关重要。

基于网络的防火墙( Network-based Firewall )通常被具有互联网访问权限的组织使用。它们为内部网络提供网络隔离。防火墙的选择有很多种；然而，许多组织使用提供多层保护的硬件防火墙设备。

网络访问保护( Network Access Protection ,NAP )是 Windows Server 2008 中的一项新技术，用于检查客户端是否健康。管理员可以定义健康客户端的标准，NAP 可以通过隔离或拒绝不健康客户端的访问来提供基本保护。

你可以使用不同的协议安全方法来提供额外的网络保护。例如，IPsec 等协议可以加密流量以确保机密性。本章包含以下主题：

- 识别常见攻击方法
- 探索防火墙
- 探索网络访问保护
- 识别协议安全方法

### 识别常见攻击方法

攻击者使用几种已知的方法试图突破网络。实际攻击在不断演变。尽管个别攻击会有所不同，但它们通常属于本节讨论的常见攻击方法之一。

许多组织部署入侵检测系统( Intrusion Detection System ,IDS )来检测和缓解活跃攻击。至少，IDS 可以检测并向管理员报告攻击。更复杂的 IDS 可以响应攻击并采取措施保护网络环境，阻止攻击。

例如，一个主动 IDS 可能会检测到来自特定 IP 地址的攻击，并更改路由器上的访问控制列表( Access Control List ,ACL )以阻止来自该计算机的所有流量。

更改路由器上的 ACL 也称为实施数据包过滤器( Packet Filter )。

以下各节介绍一些常见的攻击方法。务必牢记，攻击者会不断调整其攻击手段，同时安全专业人员也会持续改进防护方法。攻击者发现新漏洞并发起新攻击，安全专业人员则创建并实施新的防护措施。攻击与防护手段始终处于动态演进之中。

因此，昨日尚能成功的攻击，今日可能已失效。然而，某些攻击方法论仍被沿用，试图突破网络环境。

拒绝服务攻击

*拒绝服务( Denial of Service ,DoS)*攻击是指任何旨在阻止系统提供服务的攻击行为。例如，Web服务器向Internet客户端提供网页服务，针对Web服务器的DoS攻击即试图阻止其向请求客户端提供网页。

DoS攻击可通过多种方式实施。部分DoS攻击试图消耗系统的基础资源，如处理能力或内存。当系统处理DoS攻击时，将无足够资源处理合法请求。更严重的是，DoS攻击可能导致系统崩溃。

常见的DoS攻击是*SYN洪水( SYN flood )*攻击。要理解该攻击原理，需先了解TCP握手过程（参见图7-1）。图中，Joe的计算机正在与服务器建立会话。

**图7-1：** TCP握手过程

![f0701.eps](./image/Chapter%207%20Protecting%20a%20Network/f0701_fmt.webp)

标志位( Flag )本质上是设置为1的单个二进制位。例如，通过将TCP数据包中的特定位置为1来设置SYN标志位。

Joe的计算机首先发送一个设置了同步( SYN )标志位的数据包。服务器收到该数据包后，响应一个同时设置了SYN和ACK（确认）标志位的数据包。随后，Joe的计算机发送第三个设置了ACK标志位的数据包，完成三次握手。

至此，两台计算机已建立TCP会话。双方均确认对方处于运行状态，并能够与之通信。会话建立后，数据即可在两台计算机之间传输。

然而，在 SYN 洪水攻击( SYN Flood Attack )中，攻击者会扣留第三个数据包。想象一下，乔伸出手要与您握手：您也伸手回应，但在最后一刻，乔却把手缩了回去。

SYN 洪水攻击也称为 IP 半扫描攻击( IP Half-Scan Attack )，因为攻击者并非发送两个数据包（SYN 和 ACK 数据包），而是仅发送一个（SYN 数据包）。

更糟糕的是，在 SYN 洪水攻击中，攻击计算机持续发送 SYN 数据包。虽然您或我可能会停止向一个总是缩手的人伸手，但服务器会继续尝试完成这些会话，除非它能识别出这是一次攻击。

大多数入侵检测系统( Intrusion Detection System ,IDS)能够识别 SYN 洪水攻击并予以阻止。

SYN 洪水攻击可在计算机上发起数百个 TCP 会话。如果攻击未被阻止，它将消耗服务器资源，导致服务器无法响应合法请求。在某些情况下，SYN 洪水攻击可能导致系统崩溃。

分布式拒绝服务( Distributed Denial of Service ,DDoS)

分布式拒绝服务( DDoS )攻击是一种由多个客户端发起的拒绝服务( Denial of Service ,DoS)攻击。例如，如果数千台计算机向互联网上的某台服务器发送简单的 Ping 请求，服务器在尝试响应这些请求时可能会不堪重负。在努力响应所有 Ping 请求的同时，服务器对合法请求的响应速度会大幅降低。

互联网上的许多系统会阻止 Ping 请求以防御此类攻击。然而，利用其他协议还可以实施许多其他类型的 DDoS 攻击。

僵尸网络( Botnet )可能包含数千甚至数百万个克隆或僵尸主机。僵尸网络控制器可以指示这些系统在特定时间针对特定系统发起攻击。例如，可以指示每个系统在同一时间对某个系统发起 SYN 洪水攻击。

第 2 章介绍了僵尸网络的概念。僵尸网络由攻击者控制，而僵尸主机则是僵尸网络中受控的计算机。

嗅探攻击( Sniffing Attack )

嗅探攻击会捕获并分析通过网络传输的流量。攻击者使用协议分析器( Protocol Analyzer )（也称为嗅探器( Sniffer )或数据包嗅探器( Packet Sniffer )）来捕获流量。如果流量未加密，攻击者可能查看到正在传输的信息，因为这些信息是以明文形式捕获的。尽管过程可能繁琐，但意志坚定的攻击者仍能从嗅探攻击中获取大量数据。

嗅探攻击( Sniffing Attacks )也称为窃听攻击( Eavesdropping Attacks )。攻击者会监听或窃听通信内容。

攻击者还可能通过无线接入点( Wireless Access Point ,WAP)将嗅探器连接到路由器或交换机。嗅探器捕获流量，WAP 则以无线方式传输该流量。攻击者可以坐在公司停车场内，使用笔记本电脑接收无线传输信号并进行分析。

Microsoft Network Monitor 是嗅探器的一个示例。它可用于合法的故障排除目的，但也常被攻击者用来捕获和分析流量。图 7-2 展示了 Network Monitor 打开并加载已保存捕获文件的状态。

Network Monitor 在《Microsoft Windows 网络基础》(Wiley, 2011)一书中有详细介绍，该书涵盖 98-366 考试。书中包含下载、安装和运行 Network Monitor 的步骤。

**图 7-2：** Network Monitor 捕获公司机密

![f0702.tif](./image/Chapter%207%20Protecting%20a%20Network/f0702_fmt.webp)

在图 7-2中，一名用户通过网络访问了一个名为 Top Secret.txt 的文件。该文件包含文本“Company Secrets”。在“帧摘要”( Frame Summary )区域中，选中了用于访问此文件的一个捕获数据包。“帧详细信息”( Frame Details )区域提供了该数据包的更多细节。“十六进制详细信息”( Hex Details )区域则显示了文件中的实际文本（“Company Secrets”）。

防范此类攻击的方法之一是采用严格的物理安全措施。应将交换机和路由器保护在锁闭的配线间或服务器机房内，以防止攻击者接触它们。

第 9 章将讨论组织内部常用的一些安全方法。

捕获 FTP 和 Telnet 流量

文件传输协议( File Transfer Protocol ,FTP)和 Telnet 等协议会以明文形式通过网络发送数据。如果攻击者能够捕获 FTP 和 Telnet 传输，他们就可以使用 Network Monitor 等嗅探器读取数据。这包括用户名、密码以及传输中发送的任何其他数据。

不过，可以通过加密流量来保护传输安全。例如，FTP 和 Telnet 都可以通过安全外壳( Secure Shell ,SSH)或 Internet 协议安全( Internet Protocol Security ,IPsec)来加以保护。

除了强健的物理安全措施外，还可以通过加密数据来保护其在网络传输过程中的安全。例如，IPsec 可以加密传输中的数据。本章后续将介绍 IPsec。

加密有助于维护数据的机密性。未经授权的人员无法读取加密数据。

嗅探器可在两种模式下运行：非混杂模式或混杂模式：

**非混杂模式( Nonpromiscuous Mode )** 嗅探器仅捕获直接发送至或来自捕获流量系统的数据。每个传输的帧都包含源 IP 地址和目标 IP 地址。如果这两个地址均与执行捕获的计算机 IP 地址不匹配，则该帧不会被记录。换言之，嗅探器不会捕获发送至其他系统或来自其他系统的单播流量。Microsoft Network Monitor 默认在此模式下运行，但可切换至混杂模式。

**混杂模式( Promiscuous Mode )** 嗅探器会捕获到达捕获系统接口卡的任何流量，无论源 IP 地址和目标 IP 地址为何。大多数嗅探器可在混杂模式下运行。尽管旧版 Microsoft Network Monitor 不支持混杂模式，但当前版本已支持。

Network Monitor 将混杂模式称为 P 模式。

欺骗攻击( Spoofing Attack )

*欺骗攻击*是指攻击者试图冒充或伪装成其他人或实体的攻击。在 IP 欺骗攻击中，源 IP 地址可能被修改，使数据包看起来来自其他位置。

第 6 章在电子邮件欺骗的背景下介绍了欺骗，以及 SPF 记录如何帮助防范电子邮件欺骗。

例如，*局域网拒绝服务( LAND )攻击*会伪造 TCP SYN 数据包中的源地址。更具体地说，它会将源 IP 地址修改为与目标地址相同。成功实施 LAND 攻击会导致系统反复向自身回复。

端口扫描( Port Scan )

端口扫描试图发现系统上正在监听的端口。端口 0 至 1023 是用于特定协议的知名端口。例如，端口 80 是 HTTP 的知名端口。如果端口扫描发现端口 80 处于开放状态，攻击者即可推断该系统很可能运行着 HTTP。若 HTTP 正在运行，则极有可能这是一台 Web 服务器。

将知名端口用于不同协议也是可能的。开放端口并不能证明关联协议正在运行，但能提供有力的线索。

攻击者会采取额外步骤来验证 HTTP 流量是否被接受，然后尝试判断运行的是哪种 Web 服务器。例如，可能是运行 Internet 信息服务( Internet Information Services ,IIS)的 Microsoft Web 服务器，也可能是运行 Apache Web 服务器的 Linux 系统。

表 7-1 列出了许多常用端口。如需完整的常用端口列表，可查看由互联网号码分配机构( Internet Assigned Numbers Authority ,IANA)托管的网页，网址为：**[www.iana.org/assignments/port-numbers](http://www.iana.org/assignments/port-numbers)**。

端口与协议的相关内容在《Microsoft Windows 网络基础》( Wiley ,2011)中有详细说明，该书涵盖考试 98-366。

**表 7-1：** 常用端口

| 端口          | 协议                        | 说明                                                         |
| ------------- | --------------------------- | ------------------------------------------------------------ |
| 20, 21        | FTP                         | 文件传输协议( File Transfer Protocol ,FTP)。                 |
| 22            | SSH                         | 安全外壳( Secure Shell ,SSH)。                               |
| 23            | Telnet                      | 可通过 SSH 进行安全加固。                                    |
| 25            | SMTP                        | 简单邮件传输协议( Simple Mail Transfer Protocol ,SMTP)。用于发送电子邮件。 |
| 110           | POP3                        | 邮局协议( Post Office Protocol ,POP3)。用于接收电子邮件。    |
| 143           | IMAP4                       | 互联网消息访问协议( Internet Message Access Protocol ,IMAP4)。用于邮件存储在服务器上的场景。 |
| 80            | HTTP                        | 超文本传输协议( Hypertext Transfer Protocol ,HTTP)。用于网页访问。 |
| 443           | HTTPS                       | 安全 HTTP。通常使用安全套接字层( Secure Sockets Layer ,SSL)进行加密。 |
| 53            | DNS                         | 域名服务( Domain Name Service ,DNS)。用于将名称解析为 IP 地址、将 IP 地址解析为名称等。 |
| 88            | Kerberos                    | 网络身份验证协议，由 Microsoft Active Directory 使用。       |
| 389           | LDAP                        | 轻量级目录访问协议( Lightweight Directory Access Protocol ,LDAP)。用于与 Active Directory 通信的语言。 |
| 636           | SLDAP                       | 安全 LDAP。使用 SSL 或传输层安全性( Transport Layer Security ,TLS)加密的 LDAP 通信。 |
| 137, 138, 139 | NetBIOS                     | 常用于 Microsoft 网络中以访问文件服务器。不在互联网上使用。 |
| 161, 162      | SNMP                        | 简单网络管理协议( Simple Network Management Protocol ,SNMP)。用于管理路由器、交换机等网络设备。 |
| 3389          | 远程桌面服务( Remote Desktop Services ) | 用于在 Microsoft 网络中远程连接到系统。                     |
| 1701          | L2TP                        | 第二层隧道协议( Layer 2 Tunneling Protocol ,L2TP)。用于建立虚拟专用网络( Virtual Private Network ,VPN)连接。 |
| 1723          | PPTP                        | 点对点隧道协议( Point-to-Point Tunneling Protocol ,PPTP)。用于建立 VPN 连接。 |

探索防火墙

控制网络进出流量的主要方法之一是通过防火墙。防火墙使用不同技术过滤流量。以下是一些基本类型的防火墙：

防火墙也在《Microsoft Windows 网络基础》(Wiley, 2011) 中有所涉及，该书涵盖 98-366 考试。

- 数据包过滤( Packet-filtering ,无状态)
- 状态过滤( Stateful-filtering )
- 内容过滤( Content-filtering )
- 应用层过滤( Application-layer-filtering )

高级防火墙可以将所有过滤方法整合到单个防火墙中。

数据包过滤防火墙基于 IP 地址、端口和某些协议过滤数据包。如果希望仅允许来自特定计算机的流量通过防火墙，可以使用这些计算机的 IP 地址创建规则。类似地，也可以基于端口创建规则以允许或阻止流量。例如，HTTP 的知名端口是端口 80。通过阻止端口 80，即可阻止 HTTP 流量。

数据包过滤防火墙的一个问题是，它只能单独检查每个数据包，无法识别流量是否属于正在进行的会话。其漏洞在于，攻击者可以插入符合数据包过滤规则但并非客户端请求的恶意流量。

相比之下，状态过滤防火墙基于网络连接的状态过滤流量。它可以监控流量流，并判断流量是否属于现有连接的一部分。如果数据包不属于已知连接，状态防火墙可以将其阻止。

无状态防火墙通常比状态防火墙更快。然而，状态防火墙能够检测未经授权的流量插入和恶意攻击。

内容过滤防火墙可以根据内容阻止流量。例如，恶意软件通常通过垃圾邮件传播，以 zip 文件或其他附件形式嵌入。内容过滤器可以检测不良内容并将其阻止或移除。内容过滤通常在邮件服务器上执行，以过滤垃圾邮件和不需要的附件。

第 2 章曾提到内容过滤防火墙如何阻止某些恶意软件。

应用层过滤防火墙基于应用程序或服务过滤流量。防火墙为所过滤的每个应用协议（如 HTTP 或 FTP）都设有独立组件。这些防火墙组件检查使用该协议的流量，以允许或阻止特定类型的流量。例如，可允许 HTTP Get 命令（允许检索文档或文件），而阻止 Put 命令（发布文档或文件）。实践中，基于软件的应用层过滤器对 CPU 资源消耗较大，使用较少。另一方面，基于硬件的应用层过滤防火墙性能更佳。

比较基于硬件与基于软件的防火墙

Windows Server 2008 和 Windows 7 包含内置的基于软件的防火墙。*基于软件的防火墙( Software-Based Firewall )*是操作系统的一项附加功能。相比之下，大多数网络防火墙是*基于硬件的防火墙( Hardware-Based Firewall )*。基于硬件的防火墙是一种专用安全设备，提供网络安全，并帮助隔离网络免受不必要的流量侵扰。其内部运行软件，但该软件完全专注于安全。

基于硬件的防火墙是专用安全设备。它比基于软件的防火墙效率更高，提供的保护更全面。

你可能还会听到*基于主机的防火墙( Host-Based Firewall )*和*基于网络的防火墙( Network-Based Firewall )*这两个术语。主机操作系统（如 Windows 7 和 Windows Server 2008）内置的防火墙属于基于主机的防火墙。专用硬件防火墙通常是基于网络的，为整个网络而非单个主机或单台计算机提供保护。

Windows 7 和 Windows Server 2008 中基于主机的 Windows 防火墙默认安装并启用。

例如，图 7-3 展示了放置在 Internet 与 Intranet 边界处的基于硬件的防火墙。图中，进出网络的所有流量均经过基于网络的硬件防火墙。此外，每台服务器和台式计算机均启用了基于软件的防火墙。

许多供应商销售防火墙设备( Firewall Appliance )。防火墙设备简化了防火墙的复杂性。它是一种专用硬件设备，组织可购买后即插即用，无需过多配置。

*Appliance*（设备）一词旨在唤起对微波炉这类简单易用的家用电器的联想。你无需了解微波炉的工作原理即可使用它：将食物放入其中，按下几个按钮，一两分钟后就能享用爆米花。

同样，使用防火墙设备也无需理解其内部复杂性。只需接通电源，输入基本配置（或接受默认设置），它便会开始保护你的网络。防火墙设备操作简单，但切勿低估其能力——它们能以最少的管理干预高效过滤各类流量。

**图 7-3：** 基于硬件的防火墙与基于软件的防火墙

![f0703.eps](./image/Chapter%207%20Protecting%20a%20Network/f0703_fmt.webp)

防火墙与纵深防御

在使用防火墙时，并非要在基于主机的防火墙（保护单个系统）与基于网络的防火墙（保护网络）之间二选一。实际上，大多数组织会同时部署两者，这是纵深防御( Defense in Depth )策略的一部分。

尽管基于网络的防火墙旨在阻止不受欢迎的流量进入网络，但流量仍可能通过其他方式渗透进来。例如，若用户无意间通过 USB 闪存盘带入恶意软件，基于网络的防火墙将无法检测到它。若该恶意软件包含蠕虫组件，试图定位并感染网络中的计算机，基于主机的防火墙便能为这些计算机提供一层保护。

UTM 与 SCM 对比

防火墙的能力与功能持续演进。防火墙设备的一个常见趋势是将多种功能整合到单一硬件防火墙中。近期防火墙领域新增了两类产品：安全内容管理( Secure Content Management ,SCM)防火墙和统一威胁管理( Unified Threat Management ,UTM)防火墙。

SCM 设备主要专注于过滤电子邮件和基于 Web 的流量。它们检查电子邮件，过滤垃圾邮件及可能包含恶意软件的邮件附件。部分 SCM 设备还可充当代理服务器( Proxy Server )。

垃圾邮件是恶意软件的主要传播途径。通过减少垃圾邮件，恶意软件风险也随之降低。

代理服务器代表内部网络中的客户端计算机从 Internet 检索 Web 内容。代理服务器通过缓存已检索的数据来减少 Internet 带宽的使用。当某个用户从 Internet 检索数据时，代理服务器会缓存该数据。当另一用户请求相同数据时，代理服务器会从缓存中发送数据，而无需再次从 Internet 检索。大多数代理服务器可根据组织的安全策略阻止对受限网站的访问。此外，大多数代理服务器还能检查并验证内容以阻止恶意软件。

尽管安全内容管理( Security Content Management ,SCM) 可为电子邮件和代理服务提供出色的保护，但统一威胁管理( Unified Threat Management ,UTM) 将其扩展至涵盖更多功能。UTM 防火墙提供多层保护。例如，Microsoft Forefront 系列包含 Microsoft Forefront 威胁管理网关( Threat Management Gateway ,TMG)。Microsoft Forefront TMG 将以下多项优势整合至单一产品中：

Microsoft 的 Forefront 威胁管理网关是 UTM 防火墙的一个示例。

**路由功能** 路由组件可在内部网络与 Internet 之间提供基本路由。路由器包含数据包筛选功能，并包括网络地址转换( Network Address Translation ,NAT)，用于转换私有 IP 地址和公共 IP 地址。

NAT 将在本章后续的“使用 NAT 隔离网络”一节中深入说明。

**防火墙安全功能** 防火墙元素检查并筛选流量，以防范攻击和恶意软件。它提供反恶意软件保护、内容筛选、状态筛选和应用层筛选。

**入侵检测功能** 入侵检测元素可识别并阻止多种常见攻击。例如，它能检测并阻止 IP 半扫描攻击（SYN 洪泛攻击）、端口扫描等。

**网络性能功能** Web 缓存功能通过代理服务器缓存减少 Internet 带宽使用。当某个用户从 Internet 检索数据时，Forefront TMG 会缓存该数据。当另一用户请求相同数据时，Forefront TMG 会从缓存中发送数据，而无需再次从 Internet 检索。

**远程访问功能** VPN 组件为远程客户端提供内部网络访问。

综上所述，安全内容管理( Secure Content Management ,SCM)主要侧重于过滤电子邮件及其他基于 Web 的内容，而统一威胁管理( Unified Threat Management ,UTM)的范围则广泛得多。此外，由于 UTM 由单一供应商提供，其各组件在保护不同环节时能够相互补充、协同工作。UTM 通常采用相似或统一的界面，从而减少了学习不同组件所需的时间。

#### 通过 VPN 提供远程访问

虚拟专用网络( Virtual Private Network ,VPN)允许客户端通过 Internet 等公共网络访问组织的私有内部网络。客户端首先连接到 Internet，随后再连接到 VPN 服务器。VPN 服务器的通信流量通过点对点隧道协议( Point-to-Point Tunneling Protocol ,PPTP)、第二层隧道协议( Layer 2 Tunneling Protocol ,L2TP)和安全套接字隧道协议( Secure Socket Tunneling Protocol ,SSTP)等隧道协议进行保护。此外，客户端在获得内部网络访问权限之前必须完成身份验证。

尽管 VPN 提供的服务对组织极具价值，但它也带来了显著风险。大多数 VPN 采用多种安全方法，确保未经授权的用户无法使用 VPN 访问内部网络。将 VPN 解决方案与其他防火墙功能集成到统一方案中，有助于将风险降至最低。

#### 在外围网络中隔离服务器

许多组织托管着可从 Internet 访问的服务器。如果将这些服务器直接部署在 Internet 上，它们极易受到攻击者的威胁。而如果将其直接部署在组织的内部网络中，允许对这些面向 Internet 的服务器进行访问，则会增加内部网络其他资源面临的风险。

面向 Internet 的服务器是指任何可从 Internet 访问的服务器。

为帮助缓解这些风险，组织使用*外围网络( Perimeter Network )*来保护面向 Internet 的服务器。外围网络是一种既受 Internet 保护，又不直接位于内部网络( Intranet )中的网络。例如，图 7-4 展示了一个保护 Web 服务器、VPN 服务器和电子邮件服务器的外围网络。这种配置有时也称为*背对背配置( Back-to-Back Configuration )*。

外部防火墙为外围网络中的服务器提供了来自 Internet 的保护层。内部防火墙则为内部网络中的所有系统提供额外保护。被授予访问外围网络中服务器权限的客户端，通常会被阻止访问内部网络中的资源。

Figure 7-4中的 Web 服务器托管可从 Internet 访问的网站。电子邮件服务器则通过 Internet 收发电子邮件。

**图 7-4：** 外围网络

![f0704.eps](./image/Chapter%207%20Protecting%20a%20Network/f0704_fmt.webp)

外围网络( Perimeter Network )也称为非军事区( Demilitarized Zone ,DMZ )。

外围网络通常使用两个基于硬件的防火墙创建，如图 7-4 所示。不过，也可以使用单个防火墙创建外围网络，如图 7-5 所示。

**图 7-5：** 单防火墙创建的外围网络

![f0705.eps](./image/Chapter%207%20Protecting%20a%20Network/f0705_fmt.webp)

在图 7-5 中，单个防火墙配备了三块网络接口卡( Network Interface Card ,NIC )。一块 NIC 连接到 Internet，一块 NIC 连接到外围网络，第三块 NIC 连接到内部网络。这种配置类型通常称为*三叉*或*三腿*防火墙配置。

供应商通常会提供配置最佳实践文档，以协助您完成复杂防火墙的初始配置。

单防火墙外围网络成本较低，因为只需一个硬件防火墙。但其配置更为复杂，有时也更难上手。复杂性增加了出错的可能性。若配置不当，防火墙的安全优势可能完全被绕过。此外，它构成了安全上的单点故障：一旦失效，攻击者便可访问外围网络和内联网。

使用蜜罐

*蜜罐( Honeypot )*是一种用于引诱攻击者的服务器。它看起来像真实的生产服务器，似乎保存着实际数据。然而，其唯一目的就是吸引攻击者。管理员会故意对蜜罐进行部分（甚至草率地）锁定，使其易于被攻击者入侵。

蜜罐( Honeypot )提供两大核心优势。首先，它能将攻击者从真实网络环境中诱离。当攻击者在蜜罐中四处试探时，便无法对真实网络发动攻击。其次，蜜罐允许安全人员记录并观察攻击者的行为，从而深入了解其使用的攻击方法。

蜜网( Honeynet )是由两台或更多服务器组成的网络，用于模拟真实网络环境。蜜网通常由单台物理服务器通过虚拟网络承载。

蜜罐通常部署在外围网络( Perimeter Network )中。虽然也可以将蜜罐部署在内部网络( Internal Network )中，但它在内部网络中被发现并遭受攻击的可能性较低。

使用 NAT 隔离网络

内部网络中的地址使用 RFC 1918 定义的私有 IP 地址( Private IP Address )。这些地址不会分配给互联网上的任何计算机，而是分配给内部网络中的计算机。私有 IP 范围如下：

- 10.0.0.0 至 10.255.255.255
- 172.16.0.0 至 172.31.255.255
- 192.168.0.0 至 192.168.255.255

相比之下，互联网上的所有 IP 地址均为公有 IP 地址( Public IP Address )。如果在互联网与内部网络之间使用防火墙，则需要在这些私有地址与公有地址之间进行转换。大多数防火墙都包含一个支持网络地址转换( Network Address Translation ,NAT)的路由组件。

NAT 将私有 IP 地址转换为公有 IP 地址，并将公有地址转换回私有地址。NAT 有助于隔离内部计算机，因为这些计算机拥有私有 IP 地址，无法通过互联网直接访问。

探索网络访问保护

Windows Server 2008 在网络策略和访问服务( Network Policy and Access Services )服务器角色中包含了网络访问保护( Network Access Protection ,NAP)。NAP 可以检查每个尝试连接到网络的客户端，并在允许其连接之前判断是否满足特定要求。不符合健康策略的客户端将被隔离或拒绝网络访问，而符合健康策略的客户端则被授予访问权限。

NAP 包含四项核心功能，它们协同工作以确保只有符合健康策略的客户端才能连接。具体如下：

- 健康状态验证( Health-State Validation )
- 对不符合健康策略的客户端实施受限访问( Limited Access )
- 对不符合健康策略的客户端自动修复( Automatic Remediation )
- 对符合健康策略的客户端进行定期合规性检查( Periodic Compliance Checking )

管理员定义健康客户端( Healthy Client )的特征，例如确保防火墙已启用、所有当前更新已安装、反恶意软件( Anti-Malware )已安装且为最新。网络访问保护( Network Access Protection ,NAP)在客户端尝试连接时对其进行检查。健康客户端被授予访问权限，而不健康客户端则根据 NAP 策略被断开连接或隔离。

被隔离的客户端仅能访问包含补救服务器( Remediation Server )的受限网络。受限网络中的补救服务器提供客户端满足健康策略所需的资源。例如，补救服务器可能包含客户端需安装的更新，以使其被视为健康。

某些补救步骤较为简单，例如启用并配置防火墙，或连接到受限网络中的特定服务器以下载并安装更新。你可以将 NAP 策略配置为自动补救( Automatic Remediation )。这使得 NAP 能够在无需用户干预的情况下修改和更新不健康客户端。

在客户端被验证为健康后，NAP 会定期检查客户端以确保其保持健康状态。例如，如果 NAP 策略要求客户端启用防火墙，但用户在连接期间禁用了防火墙，NAP 策略将检测到此变化。根据补救策略流程，客户端可能被完全断开连接、访问权限被限制为仅能访问补救服务器网络，或自动重新配置以符合要求。

理解 NAP 组件

NAP 解决方案的多个组件协同工作。以下详细说明：

Windows XP Service Pack 3 之前的客户端不支持 NAP。

**系统健康代理( System Health Agent ,SHA)** Windows XP Service Pack 3、Windows Vista 和 Windows 7 包含系统健康代理( SHA )，这些代理在后台定期运行并检查客户端状态。这些 SHA 识别计算机的状态，例如防病毒软件是否已安装且为最新、系统是否使用自动更新( Automatic Updates )、系统是否已启用防火墙等。SHA 以健康声明( Statement of Health )的形式报告状态。一个系统将包含多个 SHA 检查不同组件，每个 SHA 创建独立的健康声明。Windows Server 2008 服务器不包含 SHA，因此它们不能作为 NAP 客户端。然而，Windows Server 2008 R2 服务器可以作为 NAP 客户端。

**系统健康验证器( System Health Validator ,SHV)** 管理员在 NAP 服务器上的 Windows 安全系统健康验证器( SHV )中定义客户端的健康状态。例如，图 7-6 展示了 Windows Vista 系统的 Windows 安全 SHV。NAP 包含内置 SHV，管理员可根据组织需求创建额外的 SHV 以检查不同要求。随后，SHV 用于定义健康策略( Health Policy )的要求。

不同客户端具有不同的可强制能力。例如，可在 Windows 7 和 Windows Vista 上强制安装间谍软件防护，但无法在 Windows XP Service Pack 3 上执行此操作。

**图 7-6：** NAP 的 SHV

![f0706.tif](./image/Chapter%207%20Protecting%20a%20Network/f0706_fmt.webp)

**健康策略( Health Policy )** 健康策略在健康服务器上创建。它们标识环境中不同客户端应使用哪些 SHV，并定义针对非健康客户端的响应。例如，可将健康策略配置为仅监视模式，或隔离客户端并限制访问。在仅监视模式下，客户端健康状况会被报告和记录，但客户端访问不受限制。这使管理员能在强制执行健康策略前评估其影响。

**系统健康声明( System Statement of Health )** NAP 服务器收集来自客户端的各个健康声明( Statement of Health )，并将其与健康策略中标识的要求进行比对。随后，它会将这些声明编译为每个客户端的单一系统健康声明( System Statement of Health )。此系统健康声明标识客户端是否符合健康策略要求。

**健康注册机构( Health Registration Authority ,HRA)** NAP 的独立组件是健康注册机构( HRA )。如果客户端满足健康策略要求，HRA 会为该客户端检索健康证书( Health Certificate )。

**健康证书( Health Certificate )** 客户端使用健康证书访问网络资源。如果客户端没有健康证书，健康策略可能将其限制在受限网络( Restricted Network )中。

**受限网络( Restricted Network )** 若强制执行健康策略，客户端可能被隔离到包含补救服务器( Remediation Server )的受限网络中。例如，补救服务器可部署操作系统更新，或部署并更新反恶意软件。

你可以将网络策略和访问服务( Network Policy And Access Services )角色添加到 Windows Server 2008 服务器。该角色包含支持网络访问保护( Network Access Protection ,NAP)解决方案所需的所有组件。

#### 使用 VPN 强制评估客户端运行状况

NAP 的一种用法是借助 VPN 强制来验证 VPN 客户端的运行状况。请结合以下描述查看图 7-7。

**图 7-7：** 用于 VPN 强制的 NAP

![f0707.eps](./image/Chapter%207%20Protecting%20a%20Network/f0707_fmt.webp)

NAP 运行状况策略服务器和健康注册机构( Health Registration Authority ,HRA)组件可以部署在同一台服务器上。

VPN 客户端先连接到 Internet，然后使用隧道协议（如安全套接字隧道协议( Secure Socket Tunneling Protocol ,SSTP)）连接到 VPN 服务器。客户端随后将凭据（例如用户名和密码）传递给 VPN 服务器进行身份验证。VPN 服务器通过域控制器验证这些凭据。到此为止，使用 NAP 的 VPN 服务器与普通 VPN 服务器并无区别。

配置了 VPN 强制的 NAP 服务器会执行额外步骤。它会向 NAP 运行状况策略服务器查询系统健康验证器( System Health Validator ,SHV)中记录的运行状况要求（如图 7-6所示）。同时，它还会查询客户端以生成系统运行状况声明( System Statement of Health )。这些信息被传递给 HRA；如果客户端满足要求，HRA 会为该客户端获取运行状况证书( Health Certificate )。随后，客户端被授予网络访问权限。

不符合运行状况要求的客户端的访问权限可被限制在受限网络中，直到它们满足运行状况要求。

#### 使用其他 NAP 强制方法

VPN 强制对许多组织而言很有价值，可确保 VPN 客户端在连接前处于健康状态。但你也可以使用 NAP 强制实施其他要求。其他三种强制方法如下：

**DHCP 强制** 动态主机配置协议( Dynamic Host Configuration Protocol ,DHCP)负责分配 TCP/IP 配置信息，例如 IP 地址、子网掩码等。你可以在分配这些 TCP/IP 信息之前，使用 NAP 验证客户端的运行状况。这样做可以防止不健康的客户端通过 DHCP 分配的 IP 地址访问网络。

**IPsec 强制** IPsec 可在传输流量前要求计算机身份验证，并可要求对传输流量进行加密。IPsec 强制允许你验证客户端是否能够使用 IPsec 进行通信，并已配置为执行此操作。如果客户端的 IPsec 策略符合 NAP IPsec 健康策略，健康注册机构( Health Registration Authority ,HRA)将代表客户端获取健康证书( Health Certificate )。

IPsec 可为数据传输提供机密性、完整性和身份验证。

**802.1x 强制** 802.1x 是一种身份验证协议，可为托管交换机、路由器和无线接入点等网络设备提供基于端口的访问控制。你可以使用 802.1x 强制来控制通过这些网络设备的访问。例如，拥有健康证书的客户端可被授予完全访问权限。没有健康证书的客户端，其访问权限可被限制为仅限特定端口和特定网络。网络设备必须与 802.1x 兼容。

你可以使用 802.1x 强制来控制网络内的路由。这可为子网提供隔离，并防止不健康客户端访问隔离网络。

识别 NAP 要求

NAP 有一些特定要求。某些要求直接与客户端相关，而其他要求则直接与服务器相关。

NAP 支持的客户端操作系统包括 Windows XP（至少需安装 Service Pack 3）、Windows Vista 和 Windows 7。这些客户端包含系统健康代理( System Health Agent ,SHA)，它们通过健康声明( Statement of Health )报告客户端健康状况。运行在 NAP 服务器上的系统健康验证器( System Health Validator ,SHV)会识别操作系统之间的差异，以创建单独的系统健康声明( System Statement of Health )。

客户端无需成为域的成员即可进行 NAP 强制。

多个服务器组件必须运行在 Windows Server 2008 或 Windows Server 2008 R2 上才能支持 NAP。这些组件及其角色和服务在表 7-2中列出。

**表 7-2：** NAP 服务器要求

| NAP 组件                                    | 角色与服务                                                   |
| ------------------------------------------------ | ------------------------------------------------------------ |
| 网络访问保护健康策略服务器                       | 网络策略和访问服务，网络访问保护                             |
| HRA 服务器                                       | 网络策略和访问服务，HRA 服务，Web 服务器(IIS)                |
| 虚拟专用网络( Virtual Private Network ,VPN)强制服务器 | 网络策略和访问服务，路由和远程访问服务                       |
| DHCP 强制服务器                                  | 网络策略和访问服务，DHCP 角色                                |

HRA 可以包含证书颁发机构( Certification Authority ,CA)，或者证书可由运行在不同操作系统上的 CA 颁发。CA 可以运行 Microsoft 或非 Microsoft 操作系统。修正服务器可以运行提供修正服务所需的任何操作系统版本。

当使用 802.1x 强制时，只能使用受管交换机。非受管交换机不支持基于端口身份验证的配置要求。

识别协议安全方法

有多种协议安全方法可用于增强安全性。其中一项措施是在数据穿越网络时对其进行加密，以防范嗅探攻击。此外，DNS 通过安全扩展改进了协议安全性，可用于提升 DNS 安全性。以下各节介绍一些常见方法。

IPsec

Internet 协议安全( Internet Protocol Security ,IPsec)是一种加密协议，用于在网络中两台计算机之间提供安全通信。它可为这些通信提供机密性、完整性和身份验证。

你可以使用 IPsec 在网络会话中的两台计算机之间进行相互身份验证。还可以使用 IPsec 在数据传输前对其进行加密，以防范嗅探攻击。

嗅探器是一种协议分析器，能够捕获通过网络传输的流量。攻击者可以读取以明文形式传输的数据，但无法读取加密数据。

IPsec 包含两种主要机制：

**身份验证标头( Authentication Header ,AH)** AH 用于提供身份验证和完整性。IPsec 传输中的两个系统均使用身份验证方法来证明各自的身份。此外，每个数据包都会被哈希处理，数据包的哈希值被放置在 AH 字段中，并与数据包一同发送。该哈希值为数据包提供完整性保护。IPsec 利用此哈希值判断接收到的数据包是否已被篡改。

哈希值本质上是一个数字。它在源端和目的端分别计算，如果哈希值不同，则表明数据已失去完整性。

**封装安全协议( Encapsulating Security Protocol ,ESP)** ESP 对数据进行加密并提供机密性。使用嗅探器捕获的加密数据无法读取。当使用 ESP 时，也会使用 AH 来为数据提供身份验证和完整性。

你可以将 IPsec 策略分配给单台计算机，或通过组策略( Group Policy )分配给多台计算机。图 7-8 展示了 Windows Server 2008 域控制器上默认域策略( Default Domain Policy )中的 IP 安全策略( IP Security Policies )节点。以下三种 IPsec 策略为默认策略，但默认情况下均未分配：

**图 7-8:** 组策略中的 IPsec 默认策略

![f0708.tif](./image/Chapter%207%20Protecting%20a%20Network/f0708_fmt.webp)

这些默认 IPsec 策略在 Windows Server 2008 上无法通过本地安全策略( Local Security Policy )直接获取。它们仅在域组策略对象( Domain Group Policy Object )中默认可用。

**客户端(仅响应)( Client (Respond Only))** 分配了此策略的计算机可以建立 IPsec 会话。然而，这些客户端从不主动发起 IPsec 会话。

**安全服务器(要求安全)( Secure Server (Require Security))** 分配了此策略的计算机始终要求使用 IPsec 会话。当会话发起时，该计算机会请求建立 IPsec 会话。如果对方系统无法建立 IPsec 会话，则通信会话将被终止。

**服务器(请求安全)( Server (Request Security))** 分配了此策略的计算机始终尝试建立 IPsec 会话。但是，如果对方系统无法建立 IPsec 会话，通信仍可继续进行。分配了此策略的系统可以与任何分配了 IPsec 策略的其他系统成功建立 IPsec 会话。

例如，你可能拥有一台存放专有数据的财务服务器需要保护。当用户通过网络访问该服务器上的数据时，你希望确保数据通过 IPsec 加密。你可以将安全服务器(要求安全)策略分配给该财务服务器。

同时，你还需要将客户端(仅响应) IPsec 策略分配给任何将连接至财务服务器的系统。当客户端连接到财务服务器时，服务器上的 IPsec 策略会尝试与客户端建立 IPsec 会话。如果客户端配置了客户端(仅响应) IPsec 策略或服务器(请求安全) IPsec 策略，它便能响应并创建 IPsec 会话。

配置了客户端(仅响应)策略的系统也可以连接至其他不要求 IPsec 的系统。如果这些其他系统没有 IPsec 策略，则不会使用 IPsec。即便其他系统也分配了客户端(仅响应) IPsec 策略，IPsec 也不会被使用，因为客户端(仅响应)策略永远不会主动发起 IPsec 会话。

你还可以对 IPsec 策略进行微调，使其仅用于特定流量。例如，若要确保 FTP 流量被加密而其他流量不被加密，可以为 IPsec 策略添加筛选器，使其仅加密 FTP 流量。

IPsec 会带来额外开销，因此使用 IPsec 可能加重系统负载。管理员必须在安全需求与性能需求之间取得平衡。

**隧道协议比较**

提醒一下，VPN 提供通过公共网络（如 Internet）访问专用网络的途径。由于 Internet 是公共网络且容易遭受嗅探攻击，因此通过 Internet 以明文传输私密数据并不安全。相反，VPN 允许使用隧道协议来保护数据在 Internet 上传输时的安全。

这些隧道协议会封装并加密发往内部网络的流量。在充当 VPN 服务器的 Windows Server 2008 系统上，主要使用以下三种隧道协议：

**点对点隧道协议( Point-to-Point Tunneling Protocol ,PPTP)** PPTP 是一种较老的隧道协议，存在一些安全漏洞，但在 Microsoft 网络的许多应用中仍被使用。它使用 Microsoft 点对点加密( Microsoft Point-to-Point Encryption ,MPPE)来加密隧道中的数据。

**第 2 层隧道协议( Layer 2 Tunneling Protocol ,L2TP)** L2TP 是由 Microsoft、Cisco 等多家厂商采用的标准协议。它通常与 IPsec 配合使用（表示为 L2TP/IPsec）来加密数据。IPsec 的一个问题是无法穿透使用网络地址转换( Network Address Translation ,NAT)的设备，因为 NAT 会破坏 IPsec 数据包。

NAT 将私有 IP 地址转换为公有 IP 地址，并将公有地址转换回私有地址。许多基于网络的防火墙都内置了 NAT 功能。

**安全套接字隧道协议( Secure Socket Tunneling Protocol ,SSTP)** SSTP 是一种较新的隧道协议，随 Windows Server 2008 引入。它使用安全套接字层( Secure Socket Layer ,SSL)进行加密，这与用于加密 HTTP（即 HTTPS）的加密协议相同。

图 7-9 展示了一个 VPN 连接，其中 VPN 客户端通过 Internet 连接到 VPN 服务器，以访问组织的内部资源。

**图 7-9:** VPN 连接

![f0709.eps](./image/Chapter%207%20Protecting%20a%20Network/f0709_fmt.webp)

DNSSEC

域名系统( Domain Name System ,DNS)服务用于将名称解析为 IP 地址，并识别运行特定服务的服务器。它是 Microsoft 域和 Internet 上的必需服务。虽然 DNS 高效且可靠，但其内置的安全机制较少。

DNS 安全扩展( DNS Security Extensions ,DNSSEC)是一组为 DNS 提供额外安全性的规范。它主要提供以下三项优势：

**数据来源认证** DNS 记录经过数字签名( Digital Signature )。这些数字签名提供了 DNS 服务器之间的身份验证。

第 11 章将介绍证书( Certificate )和数字签名的使用。

**数据完整性** 对 DNS 记录使用哈希( Hashing )来验证记录未被修改。这有助于防止 DNS 缓存中毒攻击( DNS Cache-Poisoning Attack )。

**经身份验证的不存在证明** 这是一种名为 NSEC3 的特殊记录类型，用于指示查询的名称不存在对应记录。然而，NSEC3 记录并非直接包含该名称，而是对响应进行哈希和加密处理。这可以防范区域枚举攻击( Zone-Enumeration Attack )，即攻击者试图枚举或列出区域内所有记录的攻击方式。

DNSSEC 于 2010 年在 Internet 的多个 DNS 密钥服务器上实施。它同样受 Microsoft DNS 服务器支持，包括托管在 Windows Server 2008 和 Windows Server 2008 R2 上的 DNS 服务器。

要点与延伸

本章介绍了若干常见攻击方法。拒绝服务( Denial of Service ,DoS)攻击试图阻止系统提供服务，而分布式拒绝服务( Distributed Denial of Service ,DDoS)攻击则是来自多个系统的同时DoS攻击。其他攻击包括嗅探攻击( Sniffing Attack )、欺骗攻击( Spoofing Attack )和端口扫描( Port Scan )。基于网络的防火墙( Network-based Firewall )通常基于硬件实现，为私有网络提供隔离。统一威胁管理( Unified Threat Management ,UTM)设备提供多层防护，而安全内容管理( Security Content Management ,SCM)设备通常专注于电子邮件内容。网络访问保护( Network Access Protection ,NAP)可检查客户端，确保其符合管理员定义的健康要求；不健康的客户端可被隔离在受限网络中。某些协议可配置以提供额外安全性。IPsec可加密网络内传输的流量。虚拟专用网络( Virtual Private Network ,VPN)使用隧道协议(如PPTP、L2TP和SSTP)配合加密来保护VPN流量。域名系统安全扩展( Domain Name System Security Extensions ,DNSSEC)是DNS的扩展，通过对DNS记录进行数字签名( Digital Signature )来提供额外安全性。

附加练习

- 死亡之 ping ( Ping of Death )是一种DoS攻击。请利用互联网研究并识别其具体内容。
- 识别端口137、138和139的常见用途。
- 绘制一个可保护面向互联网服务器的外围网络( Perimeter Network )示意图。
- 确定DNSSEC何时部署到根域名服务器( Root DNS Server )。

---

## 第8章 理解无线安全

近年来，无线网络( Wireless Network )已变得相当普及。它们相对廉价，且无需铺设线缆即可实现连接。相反，你只需设置一个无线接入点( Wireless Access Point )或无线路由器( Wireless Router )并进行配置，无线客户端( Wireless Client )即可连接到网络。

然而，无线网络的安全性起步并不顺利。如果你不使用最新技术，无线网络将极易受到攻击。虽然无法使无线网络达到100%安全，但仍有多种方法可提升其安全性。实施无线安全最重要的一步是采用无线加密技术( Wireless Encryption Technology )，如WPA或WPA2；此外，通过使用WPA-Enterprise或WPA2-Enterprise，可以进一步增强保护。

本章首先介绍无线设备和网络的基础知识，然后涵盖无线安全的不同要素，主题如下：

- 比较无线设备
- 比较无线安全方法
- 配置无线路由器
- 为无线连接配置Windows 7

### 比较无线设备

无线网络使用四种主要无线标准之一，许多设备支持多种标准。表8-1展示了当前常用的无线标准。

802.11无线标准在《Microsoft Windows网络基础》(Wiley, 2011)中有更深入的介绍，该书涵盖考试98-366。

**表8-1：** IEEE 802.11无线标准

| IEEE标准  | 速度      | 基础频率        |
| --------- | --------- | --------------- |
| 802.11a   | 54 Mbps   | 5 GHz           |
| 802.11b   | 11 Mbps   | 2.4 GHz         |
| 802.11g   | 54 Mbps   | 2.4 GHz         |
| 802.11n   | 300 Mbps  | 2.4 GHz 或 5 GHz |

表8-1中的"速度"列显示了这些标准支持的最大速度。然而，各种类型的干扰可能会降低实际可达的吞吐量。此外，在某些配置下，IEEE 802.11n的速度甚至可超过300 Mbps。IEEE 802.11n采用多输入多输出( Multiple Input Multiple Output ,MIMO)配置中的多天线技术来提高吞吐量，其速度最高可达600 Mbps。

速度的另一种术语是数据速率( Data Rate )。数据速率是连接的总速度，而吞吐量( Throughput )通常低于数据速率。

所选的安全方法与802.11标准无关。换言之，在决定使用何种安全方法时，无论采用802.11g还是802.11n都没有影响。但每个设备都需要支持兼容的标准。同样，每个设备也需要支持通用的安全算法和协议，这些内容将在本章后续部分讨论。

在深入探讨无线安全之前，有必要了解网络中常见的无线设备类型。通常，无线设备只有三种类型：无线适配器( Wireless Adapter )、无线接入点( Wireless Access Point )和无线路由器( Wireless Router )。

无线适配器

具备无线功能的计算机都配有无线适配器。许多移动计算机内置无线适配器，提供原生无线支持。你可以购买无线网络适配器模块并安装在台式计算机中。此外，还有USB无线适配器可供选择：只需插入USB适配器并进行配置，即可获得无线连接。

许多其他设备也包含无线功能，包括Windows Phone 7、iPhone和Droid等手机，以及Xbox 360和Wii等游戏系统。甚至Kindle等部分电子书阅读器也具备无线功能。

当然，你需要连接到某个设备。在大型组织中，你通常会连接到无线接入点。然而，在移动热点和小型组织中，你很可能连接到无线路由器。

无线接入点

无线接入点( Wireless Access Point ,WAP)为无线客户端提供与有线设备的连接。它将无线客户端桥接到有线网络，使其能够访问有线网络中的资源。WAP包含以下组件：

- 至少一个连接到有线网络的接口
- 一个允许 WAP 发送和接收无线信号的收发器
- 用于桥接无线和有线网段的桥接软件

图 8-1 展示了一个组织中的 WAP。无线客户端可以连接到 WAP，以访问网络中的有线资源。

**图 8-1:** 桥接无线客户端的无线接入点

![f0801.eps](./image/Chapter%208%20Understanding%20Wireless%20Security/f0801_fmt.webp)

WAP 至少有一个有线接口，用于连接到有线网络。使用 WAP 的无线网络以基础结构模式( Infrastructure Mode )运行。

也可以在不使用 WAP 的情况下，以临时模式( Ad Hoc Mode )将无线客户端直接相互连接。

大型组织可以使用多个 WAP。这样做可以扩展无线网络的覆盖范围，并允许客户端在网络内漫游而不会失去连接。

无线路由器

小型组织通常使用无线路由器。无线路由器将 WAP 的功能与路由器的功能结合在一起。例如，图 8-2 展示了一个小型网络中的无线路由器。

**图 8-2:** 小型网络中的无线路由器

![f0802.eps](./image/Chapter%208%20Understanding%20Wireless%20Security/f0802_fmt.webp)

在图中可以看到，无线路由器为网络中的所有用户提供对 Internet 的访问。该路由器通常还提供基本的防火墙功能。

无线路由器包含物理端口，有线客户端使用标准双绞线直接连接到这些物理端口。无线路由器的 WAP 组件为无线客户端提供对有线网络的访问。

大多数无线路由器都包含额外的功能，例如网络地址转换( Network Address Translation ,NAT)和动态主机配置协议( Dynamic Host Configuration Protocol ,DHCP)。DHCP组件向客户端发放TCP/IP配置信息，包括IP地址、子网掩码、默认网关（通常是无线路由器）的地址以及域名系统( Domain Name System ,DNS)服务器的地址。NAT组件将内部私有IP地址转换为外部公有IP地址，并将公有IP地址转换回私有IP地址。

### 比较无线安全方法

Wi-Fi保护访问( Wi-Fi Protected Access ,WPA和WPA2)协议是当今无线网络的主要安全手段。然而，WPA和WPA2存在不同版本，你需要了解它们。此外，一种名为有线等效保密( Wired Equivalent Privacy ,WEP)的旧协议存在严重缺陷，不应再使用。但由于WEP仍被许多不知情的用户使用，了解其弱点和缺陷至关重要。

理解加密密钥

不同的无线安全方法使用密钥，因此了解加密密钥的一些基础知识非常重要。无线安全采用*对称加密*( *symmetric encryption* )，这意味着使用单个密钥来加密和解密数据。

第10章将更深入地介绍对称密钥和非对称密钥的使用。

加密使用算法和密钥。算法是一种数学公式，用于打乱或加密数据。密钥提供随机性，使得使用不同密钥时数据被打乱的方式不同。虽然算法始终保持不变，但密钥应定期更换。此外，密钥必须保密。否则，任何人都可以解密数据。

例如，考虑一种基于字母表的基本旋转算法。算法如下：

**加密** 向前移动*X*个位置。

**解密** 向后移动*X*个位置。

在这种情况下，密钥是*X*。假设密钥值为3。那么你可以通过将每个字母向前旋转三个位置来加密单词*Success*。*S*变为*V*，*u*变为*x*，*c*变为*f*，以此类推。当*Success*中的每个字母向前旋转三个字母后，加密后的值为*Vxffhvv*。

加密后的值可以使用相同的密钥 3 将字母向后旋转来解密。*V* 向后旋转三个位置得到 *S*，*x* 向后旋转三个位置得到 *u*，以此类推。如果攻击者截获了文本 *Vxffhvv*，则难以直接阅读。然而，一旦攻击者知晓算法和密钥，解密就变得非常简单。

如今的加密算法并非如此简单的向前或向后旋转，但大多数算法都有详尽的文档记录。任何人都可以通过互联网查阅本章描述的任何无线安全方法的算法。然而，只要加密密钥保持机密并经常更换，攻击者就无法解密加密数据。

当加密密钥未能保密且被频繁重复使用时，安全性就会受到损害。

有线等效保密( Wired Equivalent Privacy ,WEP)

*有线等效保密( Wired Equivalent Privacy ,WEP)* 是一种安全协议，旨在为无线客户端提供与有线客户端同等的隐私保护。遗憾的是，WEP 存在多个问题。攻击者可以轻松入侵受 WEP 保护的网络。

不推荐使用 WEP。大多数支持 WEP 的硬件也支持 WPA。新硬件则支持 WPA2。

WEP 的一些问题包括：

**弱加密** WEP 使用名为 RC4 的流密码( Stream Cipher )结合重复使用的密钥来加密数据。攻击者可以使用广泛可用的软件破解这种组合。流密码将数据作为数据流的一部分进行加密。相比之下，分组密码( Block Cipher )（用于 WPA 和 WPA2）则按特定大小的数据块进行加密。分组密码比流密码强大得多。

**密钥管理不善** WEP 没有安全通道来传输加密密钥。相反，加密密钥在会话开始时以明文形式传输，使得攻击者能够发现密钥。此外，后续的加密密钥是可预测的、重复使用的，且不经常更换。

攻击者可以使用无线嗅探器( Wireless Sniffer )捕获数据并快速发现 WEP 加密密钥。随后，解密并读取数据就变得轻而易举。

**攻击者工具广泛可用** 攻击者可以轻松地从互联网上找到并下载工具。这些工具允许攻击者破解受 WEP 保护的无线网络。

当发现 WEP 的问题后，WPA 被迅速开发并作为临时替代方案发布。随后，WPA2 被采纳为 WEP 的永久替代方案。

Wi-Fi 保护接入( Wi-Fi Protected Access )

*Wi-Fi Protected Access (WPA)* 是一种用于无线传输的安全认证标准。在 WEP 的缺陷被发现后，WPA 作为临时替代方案被引入。其目标之一是在不要求比 WEP 更新硬件的前提下提供纯软件解决方案。相比之下，WPA2 通常需要不同的硬件。

尽管 WPA 不需要比 WEP 更先进的硬件，但它需要不同的固件。现有的 WEP 无线设备可通过刷写 BIOS 进行固件升级，从而支持 WPA。升级后，WEP 硬件即可支持 WPA。

当今制造的无线硬件默认支持 WPA 和 WPA2。只有较旧的硬件才需要升级以支持 WPA。

WPA 相比 WEP 的主要改进之一是加密和密钥保护。WPA 使用临时密钥完整性协议( Temporal Key Integrity Protocol ,TKIP)作为安全算法。加密密钥不以明文形式发送，且会频繁更换，从而纠正了 WEP 的两个安全问题。TKIP 会定期更换密钥，无需用户更改其密码短语。

当前许多版本的 WPA 同时支持 TKIP 和高级加密标准( Advanced Encryption Standard ,AES；参见“理解 AES”边栏)。

尽管 WPA 比 WEP 安全得多，但它仍存在缺陷。攻击者已成功破解 WPA，因此目前建议使用 WPA2 替代 WPA。WPA 的设计者意识到 WPA 并非永久性解决方案，但这并非其设计目标——其目标是支撑到 WPA2 开发并发布为止。

WPA 和 WPA2 各自提供两种保护模式，例如 WPA-个人版( WPA-Personal )和 WPA2-个人版( WPA2-Personal )，以及 WPA-企业版( WPA-Enterprise )和 WPA2-企业版( WPA2-Enterprise )。“Wi-Fi Protected Access 版本 2”部分将介绍个人版与企业版模式之间的差异。

理解 AES

AES 是一种强大且高效的对称加密算法，广泛应用于多种场景。除了与 WPA 和 WPA2 配合使用外，它还用于加密 Kerberos 传输、通过 BitLocker 加密硬盘驱动器，以及通过 BitLocker To Go 加密 USB 闪存驱动器。这些仅是其中几个示例。美国政府已将其广泛用于各类用途。

对称加密( Symmetric Encryption )指使用同一密钥进行数据加密和解密，即采用单一密钥。相比之下，非对称加密( Asymmetric Encryption )使用两个密钥（称为公钥( Public Key )和私钥( Private Key )），公钥与私钥作为匹配对生成。

高级加密标准( Advanced Encryption Standard ,AES)具有不同强度：AES-128使用128位密钥，AES-192使用192位密钥，AES-256使用256位密钥。密钥长度越大，加密强度越高，但可能对性能产生负面影响。

Wi-Fi保护访问版本2

*Wi-Fi保护访问版本2( Wi-Fi Protected Access version 2 ,WPA2)* 是WEP的永久替代方案，用于认证设备或软件符合IEEE 802.11i标准。WPA2默认使用AES，同时向后兼容WPA并可选用临时密钥完整性协议( Temporal Key Integrity Protocol ,TKIP)。WPA2安全性高于WPA，是当前无线网络的推荐方案。

WPA2向后兼容WPA。若硬件支持WPA2，则必然支持WPA。

WPA与WPA2的一个显著区别在于，WPA2默认支持联邦信息处理标准( Federal Information Processing Standards ,FIPS) 140-2。FIPS是美国政府制定的一系列标准，其中FIPS 140-2定义了密码学标准。例如，图8-3展示了Windows 7系统无线连接的“高级设置”页面，以及如何启用FIPS合规性。若安全类型设置为WPA-个人而非WPA2-个人，“高级设置”按钮将不可用，且无法启用FIPS。

如前所述，WPA和WPA2均可用于个人模式( Personal Mode )或企业模式( Enterprise Mode )。*WPA-个人* **与** *WPA2-个人*模式对所有无线设备使用相同的预共享密钥( Pre-Shared Key ,PSK)或密码短语。个人模式适用于小型组织及家庭用户。

**图8-3：** 为无线连接启用FIPS标准

![f0803.tif](./image/Chapter%208%20Understanding%20Wireless%20Security/f0803_fmt.webp)

*WPA2-Enterprise* 模式使用 802.1X 服务器进行身份验证。大型组织采用企业模式以增强安全性。客户端必须单独向 802.1X 服务器进行身份验证；验证通过后，802.1X 服务器会向其分发加密密钥。企业模式包含如图 8-4 所示并在此描述的要素：

WPA-Enterprise 和 WPA2-Enterprise 使用 802.1X 身份验证服务器，比仅使用预共享密钥( Pre-Shared Key ,PSK)的 WPA-Personal 和 WPA2-Personal 提供更强的安全性。

**请求方( Supplicant )** 请求方是请求访问网络的无线客户端。

**验证方( Authenticator )** 无线接入点( Wireless Access Point ,WAP)充当验证方，在请求方通过身份验证服务器验证之前阻止其访问。

**身份验证服务器( Authentication Server )** 该服务器验证无线客户端的凭据。你可以将运行网络策略和访问服务( Network Policy and Access Services )角色的 Windows Server 2008 服务器配置为 802.1X 身份验证服务器。

扩展身份验证协议( Extended Authentication Protocol )

使用 WPA-Enterprise 和 WPA2-Enterprise 时，需使用 802.1X 服务器进行身份验证。配置为 802.1X 服务器的 Windows Server 2008 服务器支持多种身份验证方法。可扩展身份验证协议( Extensible Authentication Protocol ,EAP)提供了框架，用于创建多种附加身份验证方法。这些协议为身份验证过程提供了额外安全性。例如，第 3 章“理解用户身份验证”在 RADIUS 主题中介绍了多种 EAP 协议，包括受保护的可扩展身份验证协议( Protected EAP ,PEAP)和基于传输层安全的可扩展身份验证协议( EAP-Transport Layer Security ,EAP-TLS)。提醒一下，智能卡使用 EAP-TLS。如果希望确保所有无线用户都通过智能卡进行身份验证，可以使用带有 EAP-TLS 的 802.1X 身份验证服务器。

**图 8-4:** 802.1X 身份验证

![f0804.eps](./image/Chapter%208%20Understanding%20Wireless%20Security/f0804_fmt.webp)

Windows Server 2008 802.1X 服务器支持的两种主要 EAP 方法如下：

**EAP-TLS** 基于传输层安全的可扩展身份验证协议使用证书进行身份验证。EAP-TLS 是一种备受推崇且成熟的身份验证标准。它支持使用智能卡进行身份验证。

**PEAP**（受保护的可扩展身份验证协议，Protected EAP）通过封装和加密身份验证通道提供一层保护。PEAP 可使用带证书的智能卡( Smart Card )进行身份验证，也可使用密码。当使用密码时，PEAP 会采用带 Microsoft 质询握手协议版本 2 的 EAP（EAP-MSCHAPv2）。

其他 EAP 方法不断涌现，适用于 802.1X 服务器。随着这些技术日趋成熟并得到广泛采用，后续更新可能会将这些额外的 EAP 协议添加到配置为 802.1X 服务器的 Windows Server 2008 产品中。

查看 Windows 7 无线设置

Windows 7 支持多种不同的无线安全设置，包括 WPA、WPA2，以及个人模式和企业模式。图 8-5 显示了在 Windows 7 系统上可为无线连接选择的安全类型。

**图 8-5：** Windows 7 上的无线安全选项

![f0805.tif](./image/Chapter%208%20Understanding%20Wireless%20Security/f0805_fmt.webp)

本节后续步骤将展示如何在支持无线的 Windows 7 系统上访问此屏幕。

您可能会注意到，图 8-5 中选项的名称与之前列出的无线安全方法略有不同。例如，您看不到 WEP 的设置。但如果您需要回退到 WEP，也是可行的。列表描述了每个选项的含义：

**无身份验证（开放式）** 此设置不使用任何加密，而是以明文形式传输数据，即开放传输。许多公共热点使用此设置来提供免费无线访问。

**共享** 共享模式使用 WEP。无线设备配置了一个预共享密钥( Pre-Shared Key ,PSK)，无线设备上的此密钥必须相同，才能连接到无线网络。

此共享密钥也称为网络安全密钥；WEP 使用它进行加密。攻击者可以窃听无线传输，破解 WEP 加密，并发现共享密钥。

**WPA-Personal / WPA2-Personal**  
WPA-Personal 和 WPA2-Personal 使用预共享密钥( Pre-Shared Key ,PSK)，但两者都比 WEP 安全得多。在大多数无线网络中，PSK 对所有用户相同。不过，部分无线路由器支持多个 PSK。例如，Cisco Valet 无线路由器对大多数设备使用一个 PSK，并允许创建其他 PSK（称为*密码*）与访客共享，而无需透露主 PSK。

**WPA-Enterprise / WPA2-Enterprise**  
WPA-Enterprise 和 WPA2-Enterprise 使用 802.1X 身份验证服务器( 802.1X Authentication Server )。802.1X 服务器在授予无线网络访问权限之前对客户端进行身份验证。

**802.1X**  
此选项适用于支持 802.1X 服务器的 WEP 网络。802.1X 服务器提供身份验证。与其他 WEP 选项一样，如今不推荐使用。需要提醒的是，WPA-Enterprise 和 WPA2-Enterprise 使用 802.1X 服务器。但在 Windows 7 中，此菜单选项仅当客户端使用 WEP 配合 802.1X 服务器时才适用。

以下步骤演示如何查看支持无线的 Windows 7 系统的安全设置。如果 Windows 7 系统不具备无线功能，则不会显示无线菜单选项：

**1.** 单击“开始” ⇒ “控制面板”。

**2.** 在“搜索控制面板”文本框中键入 **Network**，然后选择“网络和共享中心”。如果系统支持无线连接，将显示名为“管理无线网络”的选项，如图 8-6 所示。

**图 8-6：** 在支持无线的 Windows 7 系统上查看网络和共享中心

![f0806.eps](./image/Chapter%208%20Understanding%20Wireless%20Security/f0806_fmt.webp)

在图 8-6 中，Windows 7 系统已连接到名为 MTA Security 的无线网络。“管理无线网络”选项位于左窗格中。

**3.** 单击“管理无线网络”。

**4.** 右键单击无线连接，选择“属性”。如有必要，选择“安全”选项卡。显示界面将类似于图 8-7。图中选定的安全类型为 WPA2-个人( WPA2-Personal )，并采用 AES 加密，但你的无线连接可能使用不同的设置。

**5.** 单击“连接”选项卡。显示界面将类似于图 8-8。图中将连接设置为在无线网络处于范围内时自动连接。

**图 8-7：** 查看无线连接属性页面的“安全”选项卡

![f0807.tif](./image/Chapter%208%20Understanding%20Wireless%20Security/f0807_fmt.webp)

**图 8-8：** 查看无线连接属性页面的“连接”选项卡

![f0808.tif](./image/Chapter%208%20Understanding%20Wireless%20Security/f0808_fmt.webp)

### 配置无线路由器

大多数无线路由器都提供基于 Web 的管理页面。你可以使用 Web 浏览器（如 Internet Explorer）通过路由器的 IP 地址连接到该页面。例如，许多无线路由器使用 IP 地址 192.168.0.1、192.168.1.1 或 192.168.2.1。你可以在地址栏中输入 **http://192.168.0.1**、**http://192.168.1.1** 或 **http://192.168.2.1** 来连接至 Web 管理页面。

随后系统会提示你使用管理员帐户登录。大多数无线路由器都有一个名为 admin 的默认管理员帐户。此外，无线路由器出厂时带有默认密码。表 8-2 列出了不同厂商使用的一些默认 IP 地址和密码。

**表 8-2：** 默认 IP 地址和密码

| 品牌                      | 默认 IP 地址         | 默认密码             |
| ------------------------- | -------------------- | -------------------- |
| Netgear                   | 192.168.0.1          | *admin*              |
| Cisco（含 Linksys）       | 192.168.1.1          | *admin*              |
| 3Com                      | 192.168.1.1          | *admin*              |
| Belkin                    | 192.168.2.1          | 空（无密码）         |

不同型号的厂商可能使用不同的默认值。若上述默认值在路由器上无效，请查阅手册。

大多数无线路由器还支持重置路由器密码。例如，若密码已更改但不再知晓，可将无线路由器重置为出厂默认设置。

更改默认管理员密码

首要的安全措施之一便是更改此默认密码。例如，图 8-9 展示了 Linksys 无线路由器的管理页面。您可在此页面更改密码。若不更改密码且 Web 访问可用，攻击者可能尝试访问路由器、使用默认密码并更改任意设置。换言之，攻击者可将您锁定在自有无线网络之外。

更改 SSID

SSID 是无线网络的名称。它在无线接入点( Wireless Access Point ,WAP)或无线路由器上配置；每个无线设备在连接无线网络时使用相同的 SSID。

战争驾驶

任何拥有可上网笔记本电脑的人都能定位无线网络。部分攻击者驾车四处寻找可攻击的无线网络，此行为称为战争驾驶( War Driving )。若网络不安全，他们便会尝试入侵。

战争驾驶者首先寻找的是未受保护的网络，包括无任何安全措施的网络以及使用 WEP 的网络。在 Windows 7 中，这些网络极易被发现。例如，下图显示了 Windows 7 计算机可检测范围内的无线网络。您可在具备无线功能的 Windows 7 计算机上，通过依次单击“开始”⇒“连接到”来访问此信息。

![g0801.tif](./image/Chapter%208%20Understanding%20Wireless%20Security/g0801_fmt.webp)

然后，你可以将鼠标悬停在任何无线连接上，查看连接的详细信息。例如，在图中，我将鼠标悬停在 54A81 网络上。工具提示显示名称、信号强度、安全类型( WEP )、无线电类型或无线标准( 802.11g )以及服务集标识符( Service Set Identifier ,SSID；54A81)。你可以在自己家中尝试此操作。你可能会惊讶地发现，周围仍有大量无线网络在使用 WEP。

如果攻击者发现正在使用 WEP，他们就可以利用其他工具入侵该无线网络。如果他们在该区域找不到容易攻破的系统，就会驱车前往另一个区域。

一些执着的攻击者会使用改装天线，在特定方向上提供更好的增益。例如，已知有些攻击者会将一个空罐子用导线连接到无线天线上。这充当了定向天线，可以连接到原本不在信号范围内的无线网络。

**图 8-9：** 更改无线路由器的默认密码

![f0809.tif](./image/Chapter%208%20Understanding%20Wireless%20Security/f0809_fmt.webp)

某些无线网络设备在出厂时带有默认的 SSID，你可以对其进行重命名。例如，某些 Linksys 无线路由器的默认 SSID 为 Linksys-g，而某些 Netgear 无线路由器的默认 SSID 为 NETGEAR。较新网络设备的一个趋势是使用随机名称作为 SSID，可能包含也可能不包含品牌名称。某些设备要求你在首次配置时输入 SSID。

出于安全考虑，建议将 SSID 从默认值重命名。

图 8-10 显示了 Linksys 无线路由器的无线设置页面。请注意，该页面上的 SSID 已重命名为 MTA Security。

SSID 的长度必须为 15 个字符或更少。

重命名 SSID 的好处之一是，它不再通过品牌标识路由器。如果 SSID 名称为 Belkin.475E，攻击者就会知道这是一台 Belkin 设备。如果 Belkin 无线路由器存在已知漏洞，攻击者就可以尝试利用这些漏洞。但是，如果 SSID 是 MTA Security，攻击者就无法得知设备的品牌。

**广播还是不广播**

可以将 SSID 设置为广播模式，以便其他设备轻松发现；也可以禁用广播，使其他设备更难定位。例如，回顾图 8-10，其中标识了无线设备的 SSID。在该图中，可以看到无线 SSID 广播( Wireless SSID Broadcast )设置已启用，但可以将其更改为禁用。

**图 8-10：** Linksys 无线设置

![f0810.tif](./image/Chapter%208%20Understanding%20Wireless%20Security/f0810_fmt.webp)

配置为广播模式时，无线路由器会定期发送其名称。其他无线设备利用此信息连接到无线网络。当然，在使用 WPA 和 WPA2 等安全协议时，除非无线客户端配置了预共享密钥( Pre-Shared Key ,PSK)，否则连接将被拒绝。

许多安全专家建议启用 SSID 广播，而另一些则建议禁用。以下是这两种建议的背景分析：

**禁用 SSID 广播** 此建议背后的理念是，禁用广播可增加攻击者定位无线网络的难度。该建议基于一个误解，即禁用 SSID 广播能增强安全性。然而，即使无线路由器不进行定期广播，SSID 仍会包含在传输的数据包中。无线嗅探器（如 Kismet）可以轻松捕获数据包并发现 SSID，即使 SSID 广播已禁用。

Kismet 是一种无线网络检测器、嗅探器和入侵检测系统，可通过互联网免费获取。

由于 SSID 以明文形式传输，禁用其广播并不会增加任何安全性。更糟的是，你必须配置计算机，从而可能使其隐私面临风险。图 8-11 展示了 Windows 7 中的配置页面。请注意，最后一项设置是“即使网络未广播也进行连接”——微软已在其下方添加了警告。由于计算机无法预知何时靠近无线网络，它会定期发送数据包以寻找该网络进行连接。这种情况发生在计算机处于机场、咖啡店或任何其他地点时。如果攻击者使用无线嗅探器，它将轻易捕获计算机宣告自身存在、IP 地址等详细信息。

**图 8-11：** 在 Windows 7 中配置无线连接

![f0811.eps](./image/Chapter%208%20Understanding%20Wireless%20Security/f0811_fmt.webp)

**保持 SSID 广播启用** 安全专家强调，禁用 SSID 广播既无法提供真正的安全性，还会降低可用性。此外，请注意微软建议保持 SSID 广播启用；因此，如果你正在准备微软考试（如安全基础，考试编号 98-367），了解微软的建议会很有帮助。要更深入理解微软对此主题的观点，请参阅 Steve Riley 的博客文章“神话与现实：无线 SSID”，地址如下：

http://blogs.technet.com/b/steriley/archive/2007/10/16/myth-vs-reality-wireless-ssids.aspx

微软建议保持 SSID 广播启用。

务必牢记，无线传输所使用的频率是广为人知的。例如，本章开头已介绍了 802.11a、b、g 和 n 的基础频率。传输频率并非秘密。对于任何使用 Kismet 等免费工具的攻击者而言，即使禁用 SSID 广播，SSID 也并非秘密。抵御这些嗅探工具的主要安全防护措施是使用强安全协议，如 WPA2。

使用 MAC 筛选器

大多数无线路由器还包含一项功能，即 *MAC 筛选器( MAC filtering )*。MAC 筛选器允许你指定要允许或阻止的特定媒体访问控制( Media Access Control ,MAC )地址。

MAC 地址( MAC Address )也称为物理地址( Physical Address )。它由六组十六进制数组成，格式类似于：00-21-6B-B2-13-D6。

例如，图 8-12 展示了 Cisco M20 无线路由器的无线 MAC 筛选( Wireless MAC Filter )页面。该设置当前处于禁用状态。若启用，无线路由器会提供两个选项：可以阻止具有特定 MAC 地址的计算机进行无线访问，同时允许所有其他计算机访问；或者允许除特定 MAC 地址之外的所有计算机进行无线访问。

**图 8-12：** 配置 MAC 筛选

![f0812.tif](./image/Chapter%208%20Understanding%20Wireless%20Security/f0812_fmt.webp)

这听起来不错。由于 MAC 地址在理论上具有唯一性，两个系统拥有相同 MAC 地址的可能性极低。如果创建仅允许自己计算机 MAC 地址的 MAC 筛选器，可能会误以为只有自己的计算机才能访问无线网络。然而，这一理论存在两个重大缺陷。首先，MAC 地址通过无线信号广播，攻击者很容易发现正在使用的 MAC 地址。其次，攻击者相对容易伪造( Spoof )MAC 地址。

需要提醒的是，欺骗攻击( Spoofing Attack )是指攻击者试图冒充或伪装成其他人或实体的任何攻击。在此场景中，攻击者伪造允许访问的计算机的 MAC 地址，从而得以连接网络。尽管 MAC 地址被烧录在网络接口卡( Network Interface Card )中，但在许多操作系统中仍可更改 MAC 地址。攻击者只需将攻击计算机的 MAC 地址更改为允许访问的计算机的 MAC 地址，即可访问网络。

MAC 筛选无法提供任何真正的安全性。最佳保护措施是使用安全协议，例如 WPA2。

### 为无线网络配置 Windows 7

可按以下步骤将 Windows 7 计算机配置为连接到无线网络：

**1.** 单击“开始”，在“搜索程序和文件”文本框中键入 **Network**，然后选择“网络和共享中心”。

2. 在左侧窗格中单击“管理无线网络( Manage Wireless Networks )”。图8-13展示了系统已连接到一个名为 MTA Security 的无线网络。

**图8-13：** Windows 7 网络和共享中心( Network And Sharing Center )显示网络连接状态

![f0813.tif](./image/Chapter%208%20Understanding%20Wireless%20Security/f0813_fmt.webp)

“管理无线网络”链接仅在系统具备无线功能时可用。若该链接未出现，请确认已安装无线适配器( Wireless Adapter )且已启用。

3. 单击“添加( Add )”。选择“手动创建网络配置文件( Manually Create A Network Profile )”。

4. 在“网络名( Network Name )”文本框中输入无线网络的名称（即 SSID）。

5. 选择 WAP 或无线路由器( Wireless Router )所使用的安全类型( Security Type )。

提醒：WPA2 强于 WPA。WPA2-企业版( WPA2-Enterprise )强于 WPA2-个人版( WPA2-Personal )，但前者需要在网络中部署 802.1X 身份验证服务器( 802.1X Authentication Server )。

6. 选择加密类型( Encryption Type )。AES 强于 TKIP。

7. 输入与 WAP 或无线路由器上相同的通行短语( Passphrase )。显示界面将类似于前文所示的图8-11。

请注意，可通过选中“自动启动此连接( Start This Connection Automatically )”复选框，让计算机自动连接此网络。若 WAP 或无线路由器禁用了 SSID 广播( SSID Broadcast )，则可选中“即使网络未广播也连接( Connect Even If The Network Is Not Broadcasting )”。提醒：微软建议保持 SSID 广播开启。

8. 单击“下一步( Next )”。单击“关闭( Close )”。

9. 通过依次单击“开始( Start )”⇒“连接到( Connect To )”并选择相应连接，来连接网络。

### 要点与扩展( The Essentials and Beyond )

在本章中，你学习了无线设备和无线安全的基础知识。配备无线适配器的设备可以连接到无线网络。无线接入点( Wireless Access Point ,WAP)和无线路由器用于将无线设备桥接到有线网络。保护无线网络的首要步骤是使用 WPA 或 WPA2 安全协议。WEP 安全算法存在严重缺陷，不应再使用。WPA-个人版( WPA-Personal )和 WPA2-个人版( WPA2-Personal )使用预共享密钥( Pre-Shared Key ,PSK)，而 WPA-企业版( WPA-Enterprise )和 WPA2-企业版( WPA2-Enterprise )则使用 802.1X 身份验证服务器。WPA-企业版和 WPA2-企业版提供的安全性高于 WPA-个人版和 WPA2-个人版。禁用 SSID 广播并不会增强安全性，微软建议保持 SSID 广播开启。MAC 地址过滤( MAC Filtering )可以根据计算机的 MAC 地址限制访问，但 MAC 地址过滤并不能提供真正的安全性。攻击者相对容易发现无线传输中使用的 MAC 地址并进行欺骗。

### 补充练习

- 列出无线安全算法与协议，从安全性最低到最高排序。
- 如果你拥有无线网络，请确定当前使用的安全类型。
- 如果你的无线网络正在使用 WEP，请重新配置以提升安全性。
- 如果你拥有无线网络，请确定是否可以启用 MAC 地址过滤，并检查该功能是否已启用。

---

## 第9章 理解物理安全

**最基本**的安全措施之一就是限制对系统的物理访问。大多数组织会采用多种不同的方法来实施物理安全，例如锁门、密码锁、警卫等。防止未经授权的人员获得对服务器和网络设备（如路由器和交换机）的物理访问，是任何全面安全计划中不可或缺的一步。

前几章侧重于单个组策略设置，而本章则扩展了对组策略的说明。它将展示如何在组织单位中组织用户、在域内创建组策略，以及修改组策略以管理用户和计算机。你将看到如何利用组策略通过限制系统访问来增强物理安全。例如，你可以使用"拒绝本地登录"组策略设置来阻止用户登录计算机。你还可以创建可移动存储访问策略，以限制用户对不同类型可移动设备（包括 USB 闪存盘）的操作。

本章最后一节将讨论手机等移动设备的安全问题。所有这些概念将在以下主题中涵盖：

- 比较站点安全与计算机安全
- 使用组策略增强计算机安全
- 探索移动设备安全

### 比较站点安全与计算机安全

物理安全包括用于保护设施及设施内信息技术( Information Technology ,IT)资源的所有要素。你可以从两个角度来理解物理安全：

Exam 98-367（安全基础）的考试目标明确将物理安全中的站点安全与计算机安全区分开来。

**站点安全( Site Security )** 这包括用于控制组织内移动的所有要素。站点安全始于组织的边界线。它可以包括围栏、警卫、照明、摄像头、锁门、运动探测器等。

**计算机安全( Computer Security )** 涵盖用于保护 IT 资源（如服务器、台式计算机和网络设备）的所有要素。组织通常会将服务器和网络设备（如路由器和交换机）锁在服务器机房内，甚至锁在服务器机房内的设备机柜（或机架）中。此外，还会实施额外的逻辑控制来限制访问，例如谁可以登录计算机，以及登录后可以使用哪些资源。

组策略( Group Policy )提供了组织可用于增强计算机安全的多种工具。本章后续部分将更深入地介绍组策略。

理解物理安全的重要性

许多 IT 专业人员熟知一句格言：“如果攻击者能够不受限制地物理访问系统，那么该系统就归攻击者所有。” 一旦获得不受限制的访问权限，攻击者几乎可以为所欲为。以下是一些示例：

**重置管理员密码** 如果攻击者能够将系统引导至 DVD 或可启动 USB 闪存盘，他们就可以使用自己的工具启动系统。有许多工具可用于更改内置管理员( Administrator )帐户的密码。攻击者随后重新启动系统，并以管理员帐户身份登录。作为管理员，攻击者可以访问系统上的所有内容。

第 3 章提到了 Ophcrack。这是一个免费工具，攻击者可用来破解系统上的所有密码，包括管理员密码。

**安装未经授权的软件** 攻击者可以安装任何类型的恶意软件。这可能包括病毒等恶意软件，也可能包括用于捕获和记录按键操作的*键盘记录器( Keylogger )*。捕获的数据可以存储在系统中供日后检索，也可以通过 Internet 或电子邮件发送给攻击者。

**窃取系统** 如果攻击者窃取了系统，他们将同时获得所有数据和硬件。虽然服务器可能价值数千美元，但数据往往更有价值，而且攻击者拥有无限的时间来访问这些数据。如果被窃的是域控制器( Domain Controller )，攻击者将能够访问关键的域机密，从而严重危及域的安全。一些组织在域控制器被盗后，不得不从头重建其域。

第 6 章介绍了只读域控制器( Read-Only Domain Controller ,RODC )的使用，此类控制器不存储域机密。当某个位置缺乏强物理安全性时，可以使用 RODC。

**物理破坏系统( Physically Damage the System )** 攻击者可通过破坏系统使其不可用。若系统未受保护，也可能意外受损。例如，若服务器存放在办公桌下，意外泼洒的咖啡可能损坏设备。不过，服务器机房对食物和饮料的限制通常严格得多。值得注意，切勿将服务器放置在办公桌上或桌下。

**修改数据( Modify Data )** 攻击者可修改系统上的关键数据。审核日志( Audit Log )可追踪系统上的所有活动，但技术娴熟的攻击者同样能修改审核日志，从而销毁审计线索。内部人员也可修改数据。例如，心怀不满的员工可能篡改自己的绩效评估、薪资数据或关键项目数据。

第5章介绍了不同类型的审核。Windows 审核日志存储在安全日志( Security log )中。

**窃取数据( Steal Data )** 便携式 USB 闪存盘可在非常小巧的设备上存储 32 GB 或更多数据，极易被窃贼藏匿。窃贼可能盗取专有信息、研发数据、客户数据（如姓名和信用卡号）、员工隐私信息等。

**键盘记录器( Keylogger )对比**

键盘记录器( Keylogger )，又称击键记录器( Keystroke Logger )，用于捕获用户的击键操作。这包括用户输入的任何内容，如用户名和密码、搜索短语、电子邮件等。数据会被存储，攻击者可稍后检索，或直接传输给攻击者。

部分键盘记录器具备高级功能，例如捕获屏幕截图。举例来说，键盘记录器可捕获用户访问的每个网站和启动的每个应用程序的截图。

键盘记录器可分为硬件型( Hardware-based )、软件型( Software-based )或固件型( Firmware-based )。硬件型键盘记录器连接在键盘与计算机之间以捕获击键。软件型键盘记录器是随计算机启动而运行的应用程序，通常采用隐蔽技术以隐藏自身不被用户发现。固件型键盘记录器要么内置于主板，要么通过修改 BIOS 安装到系统中。多年前，许多亚洲国家制造的主板内置了键盘记录器；移除这些键盘记录器的唯一方法是更换主板。

**控制物理访问( Controlling Physical Access )**

物理访问控制( Physical-Access Control )通过不同安全等级来保护组织的各个区域。许多组织采用多层方法控制不同的物理边界。例如，参考图9-1，该图展示了包含多种物理安全元素的多层物理安全体系。

**图9-1：** 建筑物的边界控制

![f0901.eps](./image/Chapter%209%20Understanding%20Physical%20Security/f0901_fmt.webp)

防护从围栏开始，逐步增强安全强度以进入组织的工作区和服务器机房。并非所有组织都会采用此处展示和讨论的全部安全方法，有些组织会使用更多措施。但该示例展示了多种可用的物理安全方法。

第一层是建筑物停车场周围的围栏。停车场应照明充足，通常配备摄像头。摄像头可以是固定式或可移动式。可移动摄像头支持平移、倾斜和变焦( Pan, Tilt, and Zoom ,PTZ)，可聚焦于可疑活动。

下一层是建筑物的前门入口。虽然组织可能允许公众进入建筑物，但这通常仅限于门厅或大堂。组织也可能在此区域安装摄像头进行保护。

员工工作区通常仅限员工进入。人员若要进入组织的工作区，必须通过某种类型的物理访问控制。例如，组织可使用警卫控制访问。安全警卫可能被指示仅允许持有员工ID或身份徽章( Identification Badge )的员工进入工作区。部分组织使用密码锁( Cipher Lock )或感应卡( Proximity Card )控制访问。

密码锁通过数字键盘控制。用户输入正确数字后，门锁即解锁。

使用感应卡和徽章控制访问

感应卡是一种约信用卡大小的卡片，其中嵌入了标识持卡人的数据。用户只需将感应卡靠近（即接近）感应卡读卡器即可。

感应卡( Proximity Card )本身不含电源。其工作原理是：读卡器( Proximity-Card Reader )产生一个能量场，当卡片靠近读卡器时，卡片上的电子元件被充电，随后卡片传输数据。某些加油站和快餐店使用的信用卡读卡器也采用了相同技术——只需将卡片在信用卡读卡器上轻轻一刷，即可读取信息。

部分感应卡兼具身份标识功能，卡片上印有员工照片（如下图所示）。员工在安全区域内活动时佩戴此徽章用于身份识别。任何未佩戴徽章在区域内走动的人员都会迅速引起警觉。当员工需要进入安全区域时，只需将徽章在感应读卡器前刷一下即可解锁门禁。

![g0901.eps](./image/Chapter%209%20Understanding%20Physical%20Security/g0901_fmt.webp)

第3章"了解用户身份验证"已阐释过多因素身份验证( Multi-Factor Authentication ,MFA)的概念，即使用多种身份验证因素。部分感应读卡器还配备数字键盘，要求用户同时具备"所持之物"（感应卡）和"所知之物"（需在密码锁键盘上输入的密码）。

此外，许多读卡器可接入审计系统( Auditing System )记录访问行为。用户进入时，应用程序会记录用户信息及进入时间。对于更高安全级别的区域，还要求用户离开时同样刷卡，系统会记录离开时间。这使得安全人员能够精确掌握人员进入安全空间的时间、停留时长及离开时刻。

第5章已详细讨论审计机制。配备审计功能的读卡器遵循相同原理，可记录"何人、何事、何时、何地"等详细信息。

物理访问控制面临的一大挑战是*尾随攻击( Tailgating )*（又称*蹭卡( Piggybacking )*）。尾随攻击指多人进入安全区域但仅有一人提供凭证的情况。例如，鲍勃用感应卡开门后，玛丽紧随其后进入，鲍勃甚至可能主动为玛丽挡门。在此场景中，玛丽未使用自己的感应卡便进入区域，即构成尾随攻击。

如果在日常培训中未向员工强调物理安全实践，礼貌往往会占据上风。实际上，即使员工接受了安全培训，礼貌仍可能占主导。在工作之外，鲍勃可能从未想过要关上门不让别人跟着他进入房间。为他人扶门是礼貌的，而当着别人的面关门则是粗鲁的。由于礼貌与安全之间的这种冲突，尾随( Tailgating )现象常常发生，即使人们了解安全策略也是如此。

防止尾随的一种方法是使用*防尾随通道( Mantrap )*。防尾随通道是一种物理安全设备，用于控制访问，只允许单个人进入或离开安全区域。在最严格的定义中，防尾随通道具有困住人的能力。例如，个人可以进入一个小房间，在那里验证其凭据，然后被允许离开。有些防尾随通道类似于带有金属栏杆旋转门的笼子。用户在读卡器前刷一下徽章，然后进入笼子，推开旋转门。这些笼子可以锁定，必要时将人困在里面。

然而，使用能困住人的笼子并不总能营造出良好的形象。相反，许多组织使用简单的旋转门( Turnstile )，类似于地铁和公交车站使用的类型。个人刷一下徽章，然后通过旋转门。如果一个人没有徽章，就无法通过。

下班后，组织可能会使用运动检测器( Motion Detector )和摄像头来监控员工区域、服务器机房等。运动检测器可以根据组织需求触发有声或无声警报。

建筑内的其他区域需要更高的安全性。例如，大多数组织将服务器和网络设备（如路由器和交换机）保护在锁定的服务器机房和锁定的设备机柜中。服务器机房的访问仅限于需要访问这些系统的管理人员。例如，组织可以使用接近卡读卡器( Proximity-Card Reader )和键盘( Keypad )来保护服务器机房的访问。由于接近卡读卡器可以识别持卡人的身份，因此可以编程只允许特定员工进入房间。要求员工同时持有接近卡并知道密码才能进入密码锁( Cipher Lock )，通过多因素身份验证( Multi-Factor Authentication ,MFA)提高了安全性：用户必须同时拥有某物( Something )和知道某事( Something )才能获得房间的访问权限。

第7章讨论了嗅探攻击。如果攻击者能够访问路由器和交换机，他们可以连接嗅探器来捕获网络流量。

使用交换机替代集线器

在网络中，计算机通过交换机或集线器相互连接。虽然集线器更便宜，但大多数组织出于安全和性能这两个主要原因选择使用交换机。

请参见图9-2。该图展示了三台台式计算机和一台服务器通过集线器连接。当用户Dawn与文件服务器来回传输数据时，集线器会将相同的数据发送到连接到该集线器的每台其他计算机。如果攻击者正在使用嗅探器，嗅探器将捕获所有数据。

**图9-2：** 通过集线器连接的计算机

![f0902.eps](./image/Chapter%209%20Understanding%20Physical%20Security/f0902_fmt.webp)

然而，请比较这些相同计算机通过交换机连接的情况，如图图9-3所示。交换机具有更高的智能性，仅将流量转发到参与传输的特定计算机。如果Dawn与文件服务器来回传输数据，只有Dawn的计算机和文件服务器会接收数据。

即使攻击者在连接到交换机的另一台计算机上运行嗅探器，也无法捕获该数据。这两台计算机之间传输的流量永远不会到达攻击者计算机所连接的交换机端口。

交换机还通过创建独立的冲突域( Collision Domain )来提升性能。由于流量不会转发到连接到交换机的每台计算机，因此冲突更少。冲突减少意味着整体性能更佳。

交换机、集线器和冲突域在《Microsoft Windows网络基础》（Wiley，2011）中有深入介绍，该书涵盖考试98-366。

**图9-3：** 通过交换机连接的计算机

![f0903.eps](./image/Chapter%209%20Understanding%20Physical%20Security/f0903_fmt.webp)

交换机比集线器提供更高的安全性。同时，由于冲突减少，它们也比集线器提供更好的性能。

### 使用组策略增强计算机安全

组策略包含许多可用于增强计算机安全性的设置。例如，你可以使用某些组策略设置来限制用户可登录的计算机。其他设置则可控制哪些设备（如 USB 闪存驱动器、DVD 驱动器等）可与计算机配合使用。

组策略设置适用于用户和计算机。管理员使用组策略来自动化管理和维护用户与计算机账户。

本书已有多个章节介绍了一些组策略设置。例如，第 3 章介绍了如何使用组策略设置密码策略( Password Policy )和账户锁定策略( Account Lockout Policy )。第 5 章“使用审核策略和网络审核”介绍了如何使用组策略设置审核策略( Audit Policy )。前几章中与组策略相关的目标，是让你了解一些可用的设置。在理解部分组策略设置的基础上，更容易掌握组策略的工作原理。本节将涵盖组策略的宏观概览，以及如何使用组策略在域中管理用户和计算机。

你还将学习一些可用于增强物理安全性的特定组策略设置。

组策略对象( Group Policy Object ,GPO)设置有数千项。你无需全部掌握，但在准备 98-367 考试时，应理解本书所涵盖的 GPO 设置。

理解默认 GPO

提醒一下，Active Directory 是一个包含用户、计算机和组等对象的数据库。组织单位( Organizational Unit ,OU)和组策略对象( GPO )是 Active Directory 中另外两种对象类型。你可以将对象组织到 OU 中，并通过使用 GPO 来管理用户和计算机。

每个域都有两个默认 GPO：

**默认域策略( Default Domain Policy )** 此 GPO 链接到域，适用于域中的所有用户和计算机，并包含若干默认设置。

**默认域控制器策略( Default Domain Controllers Policy )** 此 GPO 链接到域控制器 OU，适用于该 OU 中的所有域控制器。当服务器被提升为域控制器时，它会被放置到域控制器 OU 中。

你不应将任何其他对象添加到域控制器 OU，也不应将域控制器移出此 OU。

设计 OU 和 GPO 以管理用户和计算机

你可以在域中创建组织单位( Organizational Unit ,OU)，将对象组织到所创建的OU中，并创建额外的组策略对象( Group Policy Object ,GPO)来管理这些OU中的用户和计算机。例如，参见图9-4。该图展示了一个包含三个OU的域示意图。两个默认策略链接到域和域控制器OU。另外添加了两个OU，分别命名为Servers OU和Sales OU，并添加了两个额外的GPO，分别命名为Server Security和Sales。Server Security和Sales GPO分别链接到Servers OU和Sales OU。

**图9-4：** 域中链接的GPO

![f0904.eps](./image/Chapter%209%20Understanding%20Physical%20Security/f0904_fmt.webp)

这代表了设计方案，但你需要执行若干步骤才能将设计落实到位。以下高级步骤概述了在Active Directory环境中构建此设计所需执行的操作：

完成这些步骤后，每个GPO中的所有设置将应用于OU内的所有对象。

**1. 创建OU** 例如，如果要使用安全设置管理一组服务器，可以创建一个名为Servers的OU。如果要组织销售部门的用户，可以创建一个名为Sales的OU。使用Active Directory用户和计算机( Active Directory Users and Computers )创建OU。

**2. 将Active Directory对象移入OU** 例如，可以将所有服务器对象移入Servers OU。同样，可以将分配给销售部门的所有用户和计算机对象移入Sales OU。使用Active Directory用户和计算机将对象移入OU。

**3. 创建并链接GPO** 例如，可以创建一个名为Server Security的GPO来保护Servers OU中的服务器。同样，可以创建一个名为Sales的GPO来管理Sales OU中的用户和计算机。使用组策略管理控制台( Group Policy Management console )创建并链接GPO。

**4. 配置GPO** 例如，可以为Servers GPO配置特定设置，阻止普通用户本地登录；并为Sales OU配置设置，限制可移动设备的使用。使用组策略管理编辑器( Group Policy Management Editor )配置GPO，该编辑器可从组策略管理控制台启动。

域控制器默认包含执行这些步骤所需的所有工具；以下各节假定你在域控制器上执行操作。提醒一下，你可以从此处下载实验室步骤以创建自己的虚拟环境：**[www.sybex.com/WileyCDA/redirect/go/securityessentials](http://www.sybex.com/WileyCDA/redirect/go/securityessentials)**。此实验室包括安装 Virtual PC、下载并安装 Windows Server 2008 以及将其提升为域控制器所需的步骤。

在域中创建组织单位( Organizational Unit ,OU)

你可以使用以下步骤创建两个组织单位( OU )。第一个是 Servers OU，用于存放服务器对象。第二个是 Sales OU，用于存放销售部门用户和计算机的用户及计算机对象：

**1.** 通过管理工具( Administrative Tools )菜单启动 Active Directory 用户和计算机( Active Directory Users and Computers )。

**2.** 选择域。右键单击域，然后选择新建( New ) ⇒ 组织单位( Organizational Unit )。

**3.** 输入 **Servers** 作为名称，然后单击确定( OK )。

**4.** 再次右键单击域，然后选择新建( New ) ⇒ 组织单位( Organizational Unit )。

**5.** 输入 **Sales** 作为名称，然后单击确定( OK )。

**6.** 保持 Active Directory 用户和计算机( Active Directory Users and Computers )处于运行状态。

此时，你已创建了组织单位( OU )，但这些组织单位( OU )中没有任何对象。下一步是将适当的对象移动到组织单位( OU )中。

将对象移动到组织单位( OU )

你可以使用以下步骤创建服务器对象并将其移动到 Servers OU：

**1.** 在打开的 Active Directory 用户和计算机( Active Directory Users and Computers )中，选择计算机( Computers )容器。

**2.** 右键单击计算机( Computers )容器，然后选择新建( New ) ⇒ 计算机( Computer )。

**3.** 在计算机名称( Computer name )文本框中输入 **Server1**，然后单击确定( OK )。

通常不需要手动创建计算机对象。当计算机加入域时，计算机帐户默认会在计算机( Computers )容器中创建。

**4.** 右键单击 Server1，然后选择移动( Move )。选择 Servers OU，然后单击确定( OK )。

对于要管理到 Servers OU 中的其他服务器，可以遵循相同步骤。此外，还可以使用相同步骤将用户和计算机移动到 Sales OU。

下一步是创建组策略对象( Group Policy Object ,GPO)并将其链接到每个组织单位( OU )。

创建组策略对象( GPO )以管理用户和计算机

你可以使用以下步骤创建 Server Security GPO 并将其链接到 Servers OU，以及创建 Sales GPO 并将其链接到 Sales OU：

**1.** 通过管理工具( Administrative Tools )菜单启动组策略管理控制台( Group Policy Management Console )。

**2.** 如有必要，展开 Forest ⇒ Domains ⇒ *你的域*。选择 Servers OU。

**3.** 右键单击 Servers OU，选择“在这个域中创建 GPO 并在此处链接”( Create A GPO In This Domain, And Link It Here )。

**4.** 输入 **Server Security** 作为名称，单击“确定”。

**5.** 右键单击 Sales OU，选择“在这个域中创建 GPO 并在此处链接”。

**6.** 输入 **Sales** 作为名称，单击“确定”。

此时，你的显示界面将类似于图 9-5。可以看到，Sales GPO 的安全筛选( Security Filtering )设置为“已认证的用户”( Authenticated Users )。

用户登录时会被自动添加到“已认证的用户”组。换言之，“已认证的用户”组包含域中的所有成员。

**图 9-5：** 包含 OU 和 GPO 的组策略管理( Group Policy Management )

![f0905.tif](./image/Chapter%209%20Understanding%20Physical%20Security/f0905_fmt.webp)

尽管此时已创建了结构，但 Sales 和 Server Security GPO 均为空。在修改 GPO 设置之前，它们不会产生任何影响。相比之下，默认域策略( Default Domain Policy )包含许多默认配置的设置；这些设置将应用于域中的所有用户和计算机。

理解 GPO 中的安全设置

你可以通过右键单击组策略管理工具中的任意 GPO 并选择“编辑”( Edit )来编辑它。这将启动组策略管理编辑器( Group Policy Management Editor )。该编辑器包含组织在两个节点中的设置：计算机配置( Computer Configuration )和用户配置( User Configuration )。

计算机配置节点包含应用于计算机的设置，无论哪个用户登录，这些设置都适用于该计算机及登录到该计算机的用户。用户配置包含应用于用户的设置，无论用户登录到哪台计算机。某些设置同时包含在计算机配置和用户配置中，而其他设置仅包含在其中一个节点中。

图 9-6 显示了组策略管理编辑器，其中展开了 Computer Configuration ⇒ Policies ⇒ Windows Settings ⇒ Security Settings 节点。此节点包含本书中涉及的许多设置。

**图 9-6：** 组策略管理编辑器( Group Policy Management Editor )

![f0906.tif](./image/Chapter%209%20Understanding%20Physical%20Security/f0906_fmt.webp)

大多数 GPO 设置在 GPO 链接到任何组织单位( OU )时生效，但存在一些例外情况。具体而言，帐户策略( Account Policies )（包括密码策略( Password Policy )、帐户锁定策略( Account Lockout Policy )和 Kerberos 策略( Kerberos Policy )）仅在域级别应用。图 9-7 展示了这些设置的位置。

帐户策略设置仅在域级别应用。第 3 章已涵盖密码策略节点和帐户锁定策略节点。

**图 9-7：** 帐户策略( Account Policies )

![f0907.eps](./image/Chapter%209%20Understanding%20Physical%20Security/f0907_fmt.webp)

你仍可在 GPO 中修改这些帐户策略设置，并将该 GPO 链接到某个 OU。但是，除非该 GPO 在域级别链接，否则这些设置不会应用于任何域帐户。

Windows Server 2008 确实提供了一些高级功能，可将密码策略和帐户锁定策略设置应用于特定用户和组。例如，若希望为普通用户设置一个密码策略，同时为管理员设置更强的密码，则可为管理员创建一个密码设置对象( Password Settings Object ,PSO )。PSO 的实现超出了本书及 Security Fundamentals 考试的范围。

所有其他组策略设置（安全设置 ⇒ 帐户策略节点中的设置除外）无论 GPO 链接在何处都会生效。例如，如果在安全设置 ⇒ 本地策略( Local Policies )（而非帐户策略节点）中配置了审核策略( Audit Policy )，并将 GPO 链接到名为 Servers 的 OU，则该策略将应用于 Servers OU 中的对象（如服务器计算机对象）。这些服务器将拥有一个特殊的审核策略，该策略不适用于任何其他系统。

使用组策略禁用本地登录( Log On Locally )

默认情况下，域内用户可以登录到除域控制器之外的任何域计算机。术语“本地登录”指用户坐在计算机前登录到控制台。其他选项包括远程登录（通过网络）或使用终端服务( Terminal Services )或远程桌面服务( Remote Desktop Services )会话登录到计算机。

许多组织会限制用户登录某些计算机的能力。例如，许多组织采取措施防止非管理员登录成员服务器。此外，一些组织更进一步，限制用户只能登录特定计算机，例如其所在部门的计算机。

成员服务器( Member Server )是指作为域成员的服务器，例如文件服务器或数据库服务器，但它不是域控制器。

你可以使用本地安全策略( Local Security Policy )工具或组策略对象( GPO )中的安全设置来控制用户登录服务器的能力。大多数设置是相同的。区别在于：本地安全策略工具仅影响本地计算机，而 GPO 中的安全设置则影响 GPO 范围内的所有用户和计算机，例如域中的所有用户和计算机，或特定组织单位( OU )中的所有用户和计算机。

第 5 章展示了如何创建审核策略( Audit Policy )。在审核策略设置正下方是用户权限分配( User Rights Assignment )设置（如图 9-8所示）。用户权限分配节点包含许多用于授予或拒绝特定用户权限的设置。

权限( Rights )标识用户可以执行的操作，例如更改系统时间或登录计算机。

用户权限分配节点中有两个重要设置影响谁可以登录计算机：

**允许本地登录( Allow Log On Locally )** 此设置标识允许登录的特定用户和组。默认情况下，此设置未对除域控制器外的任何计算机进行配置。当未定义时，任何用户都可以登录计算机。当定义后，只有添加到该设置中的组成员（或添加到该设置中的单个用户）才能登录系统。

**拒绝本地登录( Deny Log On Locally )** 此设置标识被阻止登录系统的特定用户和组。如果某个用户同时出现在允许本地登录设置和拒绝本地登录设置中，则拒绝优先。因此，你需要谨慎处理拒绝本地登录设置。例如，如果将管理员( Administrators )组添加到允许本地登录设置，然后将已验证用户( Authenticated Users )组添加到拒绝本地登录设置，则包括管理员组成员在内的任何人都将无法登录。

拒绝优先。这句话值得牢记，因为它适用于众多安全场景。

图 9-8 展示了应用于域控制器( Domain Controller )的“允许本地登录”设置。此设置来自默认域控制器组策略对象( Default Domain Controllers Group Policy Object )。

域控制器位于域控制器组织单位( Domain Controllers OU )中。默认域控制器组策略链接到域控制器组织单位，因此它适用于所有域控制器。

**图 9-8：** 默认域控制器策略中的“允许本地登录”

![f0908.tif](./image/Chapter%209%20Understanding%20Physical%20Security/f0908_fmt.webp)

图 9-8 中显示的组是内置组。Microsoft 域默认包含这些组。

“允许本地登录”设置默认未定义；当未定义时，允许任何用户登录。然而，当定义后，只有已定义组的成员（或单独添加的用户）才能登录到受该策略影响的计算机。

换句话说，普通用户无法登录域控制器，除非他们被添加到列出的某个组中。你无需显式配置“拒绝本地登录”来阻止用户登录。但是，如果你想阻止这些组中的任何成员登录系统，可以将他们添加到“拒绝本地登录”设置中。

大多数组织会在 Active Directory 中创建额外的组来组织用户，例如为销售部门的所有用户创建“销售”组。第 4 章“使用权限保护访问安全”介绍了通过组来组织用户的概念。你可以将权限和权利分配给一个组，该组的所有成员便拥有这些权限和权利。例如，IT 部门可以有一个“IT 管理员”组，IT 部门的所有 IT 管理员都添加到此组中。如果“IT 管理员”组被添加到此设置中，该组中的任何用户都可以登录到域控制器组织单位中的任何域控制器。

你可以通过修改“服务器安全 GPO”来限制谁可以登录到服务器组织单位中的服务器，具体步骤如下：

**1.** 通过管理工具( Administrative Tools )菜单启动组策略管理控制台( Group Policy Management Console )。

**2.** 如有必要，依次展开 Forest ⇒ Domains ⇒ *your domain* 以及之前创建的 Servers OU。

**3.** 右键单击 Server Security GPO，然后选择“编辑”。

**4.** 依次展开 Computer Configuration ⇒ Policies ⇒ Windows Settings ⇒ Security Settings ⇒ Local Policies，然后选择 User Rights Assignment。

**5.** 双击 Allow Log On Locally。

**6.** 选中 Define These Policy Settings 复选框，然后单击 Add User Or Group。

**7.** 单击 Browse。输入 **Account Operators**，然后两次单击 OK。

**8.** 对以下组重复步骤 7：Administrators、Backup Operators、Print Operators 和 Server Operators。完成后，Allow Log On Locally 的属性将类似于前面所示的图 9-8。

**9.** 双击 Deny Log On Locally 设置。

**10.** 选中 Define These Policy Settings 复选框，然后单击 Add User Or Group。

**11.** 单击 Browse。输入 **Guests**，然后两次单击 OK。您的显示将类似于图 9-9。

**图 9-9：** 默认域控制器策略中的 Deny Log On Locally

![f0909.tif](./image/Chapter%209%20Understanding%20Physical%20Security/f0909_fmt.webp)

您可以将任何组添加到此设置，但不应添加 Everyone、Domain Users 或 Authenticated Users 组。如果添加，则没有人能够本地登录。

通过组策略控制可移动存储访问

您可以使用可移动存储访问( Removable Storage Access )策略来控制可移动设备和驱动器的功能。组策略包含多个设置，允许您拒绝对系统中可移动设备的读取访问或写入访问。

图 9-10 显示了可移动存储访问策略设置。您可以在组策略的以下位置查看它们：Computer Configuration ⇒ Policies ⇒ Administrative Templates ⇒ System ⇒ Removable Storage Access。

设置如下：

**强制重启可移动存储设备的时间(秒)** 访问策略设置需在系统重启后才会生效。你可以配置此设置，在修改任何设置时强制重启。若启用此设置，默认时间为 1800 秒（30 分钟），但可调整此时间。

**CD 和 DVD** 此设置控制所有 CD 和 DVD 驱动器，包括内置和外置的 CD 及 DVD 驱动器。

**自定义类** 你可以使用全局唯一标识符( Globally Unique Identifier ,GUID)识别任何特定类别的可移动介质。例如，可识别特定类型的 USB 闪存盘并予以拒绝。

**图 9-10：** 可移动存储访问策略设置

![f0910.tif](./image/Chapter%209%20Understanding%20Physical%20Security/f0910_fmt.webp)

这些设置可在 Windows Vista、Windows 7、Windows Server 2008 和 Windows Server 2008 R2 上强制执行。

**软盘驱动器** 此设置控制 3.5 英寸软盘驱动器。大多数系统已不再配备软盘驱动器，但外置软盘驱动器仍可使用。

**可移动磁盘** 此类别包括通过 USB 或 IEEE 1394（FireWire）连接的任何外置驱动器，涵盖硬盘和闪存盘。

**所有可移动存储类** 此类别包括以下任何类别的可移动介质：CD 和 DVD 驱动器、软盘驱动器、可移动驱动器、磁带驱动器和 Windows 便携设备( Windows Portable Device ,WPD)。用户在远程会话中通常无法访问可移动设备。但你可以通过“所有可移动存储：允许在远程会话中直接访问”设置授予此权限。

可移动存储访问策略仅在系统启动至 Windows 时生效。若攻击者使用自己的操作系统重启系统，该策略将不适用。

**磁带驱动器** 此类别包括内置和外置磁带驱动器。

**WPD 设备** 你可以通过此设置控制 Windows 便携设备( Windows Portable Device ,WPD)，例如媒体播放器、智能手机等。

可按以下步骤配置可移动存储访问策略。这些步骤将修改链接到销售组织单位( Sales OU )的销售组策略对象( Sales GPO )（本章前面已创建）：

**1.** 通过“管理工具”菜单启动组策略管理控制台( Group Policy Management Console )。

**2.** 如有必要，依次展开“林”⇒“域”⇒*你的域*以及之前创建的销售组织单位( Sales OU )。

**3.** 右键单击销售组策略对象( Sales GPO )，然后选择“编辑”。

**4.** 展开“计算机配置( Computer Configuration )”⇒“策略( Policies )”⇒“管理模板( Administrative Templates )”⇒“系统( System )”⇒“可移动存储访问( Removable Storage Access )”。

**5.** 双击“所有可移动存储类：拒绝所有访问( All Removable Storage Classes: Deny All Access )”设置。

**6.** 选择“已启用( Enabled )”。此时界面应类似于图9-11。

**7.** 单击“确定( OK )”。关闭所有打开的窗口。

**图9-11：** 拒绝所有可移动存储类的访问

![f0911.tif](./image/Chapter%209%20Understanding%20Physical%20Security/f0911_fmt.webp)

探索移动设备安全性( Exploring Mobile Device Security )

移动设备可存储大量个人信息，因此为其纳入一些安全实践是值得的。用户保护移动设备的一个简单步骤是设置密码保护。这样，如果手机丢失，他人轻易窃取个人信息的可能性就会降低。

如今的智能手机具备强大的功能和特性。例如，许多智能手机可使用 Microsoft Outlook 界面收发电子邮件，并与 Microsoft Exchange 服务器集成。由于这些智能手机可接入网络，因此也需要加以保护。当前日益重要的一步是在这些移动设备上安装防病毒软件。某些移动设备面临独特挑战：例如，支持蓝牙( Bluetooth )的智能手机在发现模式( Discovery Mode )下存在特定风险。

保护移动设备免受恶意软件侵害( Protecting Mobile Devices Against Malware )

好消息是，直到最近，移动设备上的恶意软件威胁并不严重。坏消息是，恶意软件已开始在移动设备上出现。由于许多设备现在能够浏览互联网和接收电子邮件，它们面临风险。计算机可能因访问网站或打开恶意附件而感染，移动设备也可能以相同方式感染。

许多银行通过移动设备提供在线服务访问。安装在移动设备上的恶意软件有可能拦截这些交易并捕获数据。

诚然，恶意软件必须针对移动设备上运行的操作系统进行定制。然而，当攻击者意识到可通过移动设备获利时，可以预见针对这些设备的恶意软件将会增多。

移动设备的防病毒( Antivirus ,AV)软件包含了许多与计算机 AV 软件相同的功能，包括实时病毒扫描和自动签名更新。您可以通过在常用搜索引擎中搜索 **移动设备防病毒( mobile device antivirus )** 来查找当前可用的移动设备软件。

#### 降低蓝牙( Bluetooth )设备风险

理解蓝牙漏洞至关重要。蓝牙设备使用无线技术在小型个域网( Personal Area Network ,PAN)中相互连接。设备连接的过程称为*配对( pairing )*。当您连接两个蓝牙设备时，它们必须处于发现模式( Discovery Mode )。发现模式允许两个设备轻松相互连接。

然而，设备连接后，应关闭发现模式。如果发现模式保持开启，蓝牙设备范围内的任何其他人都可以与其配对。例如，攻击者使用 Linux 操作系统上的蓝牙设备，只需一条简单命令即可与处于发现模式的蓝牙设备配对。

两种常见的蓝牙攻击是蓝劫( Bluesnarfing )和蓝扰( Bluejacking )。*蓝劫*是指未经授权访问蓝牙设备上的信息。当然，攻击者访问后即可窃取数据；这些数据可能包括联系人、电子邮件以及设备可存储的任何其他数据。在*蓝扰*攻击中，攻击者劫持蓝牙设备并利用其发送消息。根据蓝牙设备的能力，攻击者可能能够发送短信或带有附件的完整电子邮件。

设备配对后应关闭发现模式。这降低了攻击者在蓝劫或蓝扰攻击中接管设备的可能性。

#### 要点与延伸

在本章中，你学习了物理安全的相关知识。站点会根据组织的需求，通过不同级别的物理安全措施加以保护。物理安全可包括围栏、照明、摄像头、警卫、密码锁( Cipher Lock )、感应卡读卡器( Proximity-Card Reader )、运动探测器( Motion Detector )、陷阱门( Mantrap )等。计算机安全可通过组策略( Group Policy )得到增强。你可以将用户和计算机组织到组织单位( Organizational Unit ,OU )中，并将组策略对象( Group Policy Object ,GPO )链接到这些OU。这些GPO可包含多种设置，其中一些设置可直接增强物理安全。通过组策略，你可以控制哪些用户可以登录到哪些计算机。你还可以通过可移动存储访问策略( Removable Storage Access Policy )控制用户可使用哪些可移动设备。手机等其他移动设备也带来自身风险。如果移动设备上存储了有价值的数据，应使用密码保护该设备。此外，可在移动设备上安装防病毒软件，以防范新兴恶意软件。蓝牙设备应切换至非发现模式( Non-Discovery Mode )，以保护其免受攻击者侵害。

### 补充练习

- 探索你的环境。列出所有已采用的物理安全机制。
- 确定你的环境中是否使用了任何集线器( Hub )。
- 创建一个名为 Testing 的OU。创建一个名为 Restrictions 的GPO。修改该GPO，使得只有管理员才能登录到该OU中的任何计算机。
- 如果你有手机，请确定它是否支持密码保护。

---

## 第10章 使用加密技术强制实现机密性

**安全三要素**（机密性、完整性和可用性）的一个关键组成部分是机密性。身份验证和访问控制有助于保护数据免遭机密性丧失，同时您还可以通过加密数据来保护它。加密数据的两种主要方式是**对称加密( Symmetric Encryption )**和**非对称加密( Asymmetric Encryption )**。您还可以使用**哈希函数( Hashing Functions )**提供单向加密。

加密和密码学方法用于保护许多最终用户在日常工作中使用的各类数据。例如，许多用户经常加密和数字签名电子邮件以提供不同保护。同样，许多用户使用 NTFS 内置功能**加密文件系统( Encrypting File System ,EFS )**来加密重要文件夹和文件。**BitLocker 驱动器加密( BitLocker Drive Encryption )**是一种较新的技术，可加密整个驱动器卷。BitLocker 的扩展是**BitLocker To Go**，它允许用户轻松加密整个 USB 闪存驱动器。本章在以下主题中涵盖这些概念：

- 比较加密方法
- 保护电子邮件安全
- 理解 EFS
- 探索 BitLocker 驱动器加密

### 比较加密方法

第1章"理解核心安全原则"介绍了机密性、完整性和可用性这安全三要素。机密性确保未经授权的个人无法访问数据。用于防止机密性丧失的方法之一是加密。

加密对数据进行打乱处理，使未经授权的用户无法读取。目前使用多种不同类型的加密协议和算法；您已在本书中阅读过其中几种。例如，第8章"理解无线安全"简要介绍了加密。作为提醒，大多数加密包含一个算法和一个密钥。算法提供标识数据如何加密的数学公式。密钥是为加密提供随机化的数字。

大多数加密算法属于以下两类之一：对称加密和非对称加密。哈希函数是另一种用于提供数据单向加密的密码学方法。以下各节将讨论每种方法。

**对称加密( Symmetric Encryption )**使用单个密钥（一个秘密密钥）进行加密和解密。**非对称加密( Asymmetric Encryption )**使用两个密钥（一个公钥和一个私钥）。

尽管存在能够加密数据的硬件设备，但本章重点介绍的加密方法均基于软件实现。换言之，加密过程通过软件完成数据混淆。

理解对称加密( Symmetric Encryption )

*对称加密*使用单一密钥对数据进行加密和解密。具体而言，用于加密数据的密钥与解密时使用的密钥完全相同。例如，若某算法使用密钥 1A2B3C4D5E6F7A8B9C（十六进制数）加密数据，则必须使用同一密钥才能解密。对称加密的关键在于，通信双方必须知晓该对称密钥( Symmetric Key )，且该密钥必须对其他方严格保密。本章后续将介绍非对称加密( Asymmetric Encryption )如何协助解决此问题。

当采用强加密算法时，攻击者在合理时间内无法在缺少密钥的情况下解密数据。

图10-1展示了加密与解密的完整流程。加密算法将明文( Plain-Text )数据转换为密文( Ciphered Text )。通过算法的解密流程，使用与加密时相同的密钥即可还原数据。

密钥为密文提供了随机化因子。当使用不同密钥时，生成的密文将完全不同。

对称加密中使用的密钥通常被称为*秘密密钥( Secret Key )*。该密钥必须在加密和解密数据的双方之间严格保密。若任何第三方获取该密钥，即可解密数据。

**图10-1：** 使用对称加密加密数据

![f1001.eps](./image/Chapter%2010%20Enforcing%20Confidentiality%20with%20Encryption/f1001_fmt.webp)

对称加密算法会频繁更换密钥。例如，某文件可能使用密钥 123 加密，而另一文件则使用密钥 456 加密。即便攻击者破解了密钥 123 并解密第一个文件，也无法使用该密钥解密第二个以密钥 456 加密的文件。

实际使用的密钥远比 123 或 456 复杂得多。密钥长度通常为 128 位或更长。

当使用弱密钥或密钥未保密时，攻击者可能窃取或获取密钥，并利用它们访问已加密的数据。第8章讨论了有线等效保密( Wired Equivalent Privacy ,WEP)及其诸多缺陷。其中一个重大缺陷是加密密钥的一部分以明文形式在空中传输。另一个缺陷是相同的密钥在同一传输中被频繁重复使用。

相比之下，使用256位密钥的单一系统在其生命周期内可能永远不会重复使用相同的密钥。如果使用16位密钥，则只有65,536种可能的密钥可用。将位数增加到40位，可能的密钥数量将超过一万亿。而使用256位密钥时，可能的密钥数量超过1.e+77种（即1后面跟77个零！）。

一些常见的对称加密算法如下：

**高级加密标准( Advanced Encryption Standard ,AES)** 由于其速度和效率，该标准被广泛用于加密各种数据。下一节将对其进行更深入的描述。

**数据加密标准( Data Encryption Standard ,DES)** 作为一种较旧的加密协议，DES已被破解，不建议使用。然而，某些遗留应用程序仍在使用它。

**3DES（三重DES）** 三重DES是为了改进DES而引入的。然而，它占用大量处理器资源，导致加密和解密速度缓慢。AES则更快、更高效。

**国际数据加密算法( International Data Encryption Algorithm ,IDEA)** IDEA曾在一段时间内非常流行。但由于更新的标准（如AES）效率更高，如今其使用已减少。

**Blowfish和Twofish** 这是另外两种强大的加密算法，但由于更高效的AES，它们的使用正在减少。

值得注意的是，最终用户通常不选择加密算法。相反，加密算法由软件或管理员选择。但也有一些例外。例如，在第8章中，你看到了如何为无线连接选择AES。

探索AES

*高级加密标准( Advanced Encryption Standard ,AES)* 是一种非常强大且高效的加密算法，相比其他算法占用更少的计算机资源。它是由美国国家标准与技术研究院( National Institute of Standards and Technology ,NIST)在为期5年的过程中从15个竞争算法中选出的。该标准于2002年被采纳为美国联邦政府标准，并已被多个公共部门组织采用。

AES 也广泛应用于非政府应用程序。例如，Kerberos（微软 Active Directory 中使用的主要网络身份验证协议）使用 AES 加密数据。WPA2（第 8 章中提到的无线加密协议）使用 AES。BitLocker 和 BitLocker To Go 分别使用 AES 加密硬盘和 USB 闪存驱动器。

BitLocker 和 BitLocker To Go 将在本章后续部分介绍。

大多数加密算法（包括 AES）都是公开的，可供任何人研究。例如，如果你想查看 AES 算法，可以使用你喜欢的搜索引擎搜索 **AES algorithm**。你会找到大量高度技术性且复杂的算法解释，以及一些高层概述。简而言之，该算法并非保密。然而，用于加密和解密任何数据的密钥*是*保密的。

如果你是数学家，可能会对 AES 使用的复杂算法感兴趣，该算法通过多轮操作，使用不同的替换、置换和混合运算来移位数据。但在你当前的学习阶段，最重要的一点是认识到 AES 是一种备受推崇的对称加密标准。

AES 可以使用 128 位、194 位或 256 位密钥。当加密密钥使用更多位数时，密钥更难被猜测。换句话说，AES-256 比使用 128 位密钥的 AES 更安全。

AES 可以使用多种不同的密钥长度。然而，只有 AES-256 在名称中包含了密钥长度。AES 可能使用 128 或 194 位，而 AES-256 使用 256 位。

攻击者可以解密加密数据

只要有足够的时间和资源，攻击者即使不知道正确的密钥，也能解密数据。加密的目标之一就是让这种操作变得足够困难，以至于对攻击者来说不值得。你可以确保破解成本高于数据本身的价值，和/或确保破解过程耗时过长。

例如，AES 可以使用 128 位密钥。据估计，破解此密钥并读取数据需要超过两百万兆（18 个零）年。如果攻击者投入数百万美元，将多台超级计算机联网以破解密钥，时间可能会缩短。但在攻击者有生之年发现该密钥的可能性仍然微乎其微。

但如果数据非常重要，可以增大密钥大小。AES 也可使用 192 位或 256 位。若使用 256 位 AES，据估计破解密钥需要超过 10⁵¹ 年（即 10 后面跟 51 个零）。相比之下，许多早期算法仅使用 40 位，有时一周内即可被破解。

同理，考虑互联网上加密的数据，例如信用卡号。即便攻击者投入数百万美元来破解密钥并获取信用卡信息，在其有生之年也无法破解该密钥。而等到这个单一密钥被破解时，该信用卡很可能早已失效。

理解非对称加密( Asymmetric Encryption )

*非对称加密*使用一对匹配的密钥：*公钥( Public Key )*和*私钥( Private Key )*。这两个密钥协同工作，且仅当与配对中的另一个密钥配合使用时才有效。当使用公钥加密数据时，只有私钥能解密数据，反之亦然。当使用私钥加密数据时，只有公钥能解密。

非对称加密也称为公钥加密( Public-Key Encryption )。

公钥可自由分享给他人。然而，私钥必须保密且绝不共享。仅单一实体（如用户或服务器）有权访问私钥。若私钥被共享或泄露，该密钥对将不再安全。

非对称加密使用公钥和私钥组成的匹配密钥对。这两个密钥仅能相互配合使用。

非对称加密的速度约为对称加密的 1,000 分之一。因此，非对称加密不适合加密大量数据，但非常适合加密用于对称加密的密钥。

举例来说，假设要加密一个 10 MB 的文件，并在网络上两个用户之间来回传递。若使用对称加密，假设加密需 1 秒，解密也需 1 秒（1 秒仅为参考值；实际时间会不同，但用 1 秒便于计算）。若对称加密耗时 1 秒，则非对称加密加密数据需 1,000 秒（近 16 分钟），解密数据同样需 1,000 秒。

显然，对称加密速度更快。然而，挑战在于如何让双方知晓对称密钥( Symmetric Key )而不让其他人知道。系统无法直接在网络上“悄悄传递”该密钥。

因此，非对称加密( Asymmetric Encryption )被用于加密对称密钥。即使对称密钥长达256位，使用非对称加密来加密和解密这256位数据也是轻而易举的，尤其是与加密一个10 MB文件相比。

提醒一下，对称加密使用相同的密钥进行加密和解密。为了实现安全加密，该密钥( Secret Key )必须保密，并且需要经常更换。通过使用非对称加密来加密和解密密钥，双方可以在不让他人发现的情况下私下交换该密钥。

在阅读以下描述时，请参阅图10-2。假设Maria的计算机正尝试与服务器建立安全会话。服务器拥有一个私钥( Private Key )，该私钥与一个已共享给Maria计算机的公钥( Public Key )相匹配。请记住，目标是使用非对称加密来私下共享密钥。

密钥（示例中为1A2B）最终将用于对称加密两台机器之间传输的数据。Maria的系统创建密钥，然后使用服务器的公钥对其进行加密。加密后的密钥随后被发送到持有匹配私钥的服务器。如果有人截获了加密后的密钥，这对他们毫无用处，因为它只能用匹配的私钥解密，而该私钥是保密的。

实际密钥会长得多，但此处为了简洁起见缩短为1A2B。同样，公钥和私钥实际上也要长得多。

**图10-2：** 使用非对称加密加密密钥

![f1002.eps](./image/Chapter%2010%20Enforcing%20Confidentiality%20with%20Encryption/f1002_fmt.webp)

Figure 10-3 展示了解密过程。当服务器收到加密的机密密钥后，它会使用匹配密钥对中的私钥来解密该机密密钥。此时，通信双方都知晓机密密钥的内容，而其他任何方均无从得知。随后，两台机器之间传输的数据便可使用该机密密钥，通过对称加密( Symmetric Encryption )进行加密和解密。

**图 10-3：** 使用非对称加密解密机密密钥

![f1003.eps](./image/Chapter%2010%20Enforcing%20Confidentiality%20with%20Encryption/f1003_fmt.webp)

尽管上述过程展示了如何使用公钥加密以及如何使用私钥解密，但非对称加密( Asymmetric Encryption )亦可反向运作。换言之，也可以使用私钥进行加密，然后使用公钥进行解密。本章后续的“保护电子邮件安全”一节将展示如何同时运用这两种过程来加密和数字签名( Digitally Sign )电子邮件。

以下是两种常见的非对称加密算法：

- RSA（以首次描述该算法的三位学者 Rivest、Shamir 和 Adleman 命名）
- Diffie-Hellman（以 Diffie 和 Hellman 命名）

**使用证书共享公钥**

*证书( Certificate )*是包含若干与加密技术相关的关键数据片段的数字文件。证书用途广泛，其中之一便是共享公钥。

第 11 章将更深入地介绍证书和证书颁发机构( Certification Authority ,CA)。

Figure 10-4 展示了一个已选中公钥的证书。你可以通过单击“高级”按钮，从个人证书存储区( Personal Certificate Store )中访问该证书。请注意，此公钥长度为 1,024 位，它使用的是 RSA 算法——一种用于公钥加密( Public-Key Cryptography )的算法。

**图 10-4：** 查看证书中的公钥

![f1004.eps](./image/Chapter%2010%20Enforcing%20Confidentiality%20with%20Encryption/f1004_fmt.webp)

互联网上证书中使用的许多公钥长度均为 2,048 位。

任何拥有匹配密钥对的用户或计算机，都可以通过证书自由共享其公钥。只要私钥保持机密，公钥和私钥便可协同用于加密操作。

**理解哈希**

本书已多次提及哈希。需要明确的一点是，*哈希*本质上就是一个数字。哈希算法( Hashing Algorithm )对一段数据执行计算，从而生成哈希（即该数字）。

你可以使用必应或其他搜索引擎搜索“calculate hash on files”，以查找免费的哈希计算器。

消息摘要 5( Message Digest 5 ,MD5)是当今常用的哈希算法。MD5 生成 128 位哈希，即长度为 128 位的数字。无论 MD5 是对 30 KB 的小邮件还是对 2 GB 的大型 .iso 文件计算哈希，它始终会生成 128 位哈希。安全哈希算法( Secure Hashing Algorithm ,SHA)是另一种流行的哈希算法。SHA 有多个版本，其中 SHA-1 最为常用；它生成 160 位哈希，并被美国政府采用。

哈希通常以十六进制数字而非位的形式显示。每个十六进制数字由 4 位组成；因此，128 位哈希表示为 32 个十六进制数字。

关于哈希的一个关键点是，只要数据内容未被修改，MD5 哈希将始终保持不变。无论对数据执行多少次 MD5 算法，只要数据保持不变，生成的哈希就始终相同。

与对称加密和非对称加密相比，哈希有一些显著区别。与对称加密和非对称加密不同，哈希函数不使用密钥。相反，其计算过程始终固定，不会通过密钥进行随机化。此外，哈希函数是单向的。换言之，你可以使用哈希函数生成哈希，但无法从哈希还原出原始数据。

图 10-5 展示了 MD5 和 SHA-1 的基本哈希过程。哈希函数对文件或消息运行，输出即为哈希。

**图 10-5：** 哈希算法生成哈希。

![f1005.eps](./image/Chapter%2010%20Enforcing%20Confidentiality%20with%20Encryption/f1005_fmt.webp)

哈希常用于验证数据的完整性，或确认数据未被更改。例如，哈希可与电子邮件结合使用，以验证邮件未被篡改。以下步骤概括了此过程：

**1.** 创建一封电子邮件，并为其计算哈希。

**2.** 同时发送邮件和哈希。

**3.** 收到电子邮件后，系统会重新计算哈希值。

如果计算出的哈希值与接收到的哈希值相同，则接收系统可确认消息未被篡改——即保持了完整性( Integrity )。

类似地，你可以使用哈希来验证下载文件的完整性。例如，通过 Microsoft TechNet 订阅，你可以下载完整的 DVD 映像（以 .iso 映像文件形式提供）。这些文件通常超过 1 GB，如果丢失一个比特位，整个文件就会损坏。但 Microsoft 会公布这些文件的哈希值。

图 10-6 展示了一个 Microsoft TechNet 下载页面，其中展开显示了 Windows Server 2008 DVD 映像的详细信息。请注意，详细信息中包含一个 SHA-1 哈希值。TechNet 订阅者可以下载这些文件，并在下载后使用其他工具计算哈希值。然后，他们可以将 TechNet 上显示的哈希值与哈希工具计算出的哈希值进行比较。如果哈希值不同，则说明存在问题。

**图 10-6：** Microsoft TechNet 上显示的 SHA-1 哈希值

![f1006.eps](./image/Chapter%2010%20Enforcing%20Confidentiality%20with%20Encryption/f1006_fmt.webp)

验证文件的哈希值还可以确认该文件是否已被恶意软件感染。例如，防病毒软件可以在周一为未受感染的可执行文件创建哈希值。（可执行文件( Executable File )是指计算机运行或执行的程序，例如 .exe 文件。）它可以在周二扫描这些文件并重新计算哈希值。如果周二的哈希值与周一计算的哈希值相同，则文件未发生更改。如果防病毒软件在周五扫描文件时发现某个文件的哈希值不同，则表明该文件已被修改。某些文件（如 Word 文档）会定期更改。然而，可执行文件在没有经过授权更新的情况下不应发生变化。

保护电子邮件安全

密码学的常见用途之一是保护电子邮件安全。保护电子邮件安全主要有两种方法：加密消息和对其进行数字签名( Digitally Sign )。

加密电子邮件是为了防止机密性( Confidentiality )的丧失。只要数据被安全加密，就无法被读取。即使攻击者使用嗅探器( Sniffer )捕获通过网络或互联网发送的加密电子邮件，攻击者也极不可能读取其内容。

电子邮件加密可防止机密性丢失。

数字签名( Digital Signature )可提供证据，证明某封电子邮件由特定个人发送。例如，公司高管可能希望发送一封电子邮件，并向他人保证该邮件未被伪造。通过对电子邮件进行数字签名，其他人可以明确知道该邮件由该高管发送。

换言之，数字签名提供了对发送方的身份验证( Authentication )。数字签名还提供完整性( Integrity )和不可否认性( Nonrepudiation )。（第5章“使用审核策略和网络审核”介绍了不可否认性。提醒一下，不可否认性提供了个人执行特定操作的证据，并防止该个人可信地否认该操作。）

在本章后面的“对电子邮件进行数字签名”部分，你将看到数字签名如何结合使用哈希( Hashing )和非对称加密( Asymmetric Encryption )。它对邮件进行哈希处理以提供完整性。当通过哈希验证完整性时，收件人便知道内容未被修改。数字签名过程使用非对称加密对哈希进行加密和解密，以提供身份验证和不可否认性。不可否认性可防止电子邮件发送方否认已发送该邮件。值得注意的是，虽然数字签名确实对邮件的哈希进行了加密，但它并不加密实际邮件内容。可以对邮件进行加密，但数字签名本身并不执行此操作。

经过数字签名的电子邮件提供身份验证、完整性和不可否认性。

安全/多用途互联网邮件扩展( Secure/Multipurpose Internet Mail Extensions ,S/MIME )是大多数电子邮件安全所使用的基础标准。它使用公钥( Public Key )和私钥( Private Key )来加密和数字签名电子邮件。发送方必须拥有一个嵌入了公钥的证书( Certificate )，该公钥与仅发送方可以访问的私钥相匹配。在 Active Directory 域中，管理员通常创建证书颁发机构( Certification Authority ,CA)来颁发和管理证书。此外，公共 CA 也颁发和管理常用于互联网及其他场景的证书。

加密电子邮件

大多数电子邮件程序（如 Microsoft Outlook）都包含加密电子邮件的功能。用户会获得包含公钥的证书，该公钥与私钥匹配。公钥在证书中公开可用。私钥则保持私有，仅单个用户可访问。

采用这种方式时，公钥( Public Key )用于加密电子邮件，私钥( Private Key )用于解密。例如，若要对电子邮件加密并发送给他人，你需要获取对方的公钥副本。更具体地说，你需要获取包含对方公钥的数字证书( Digital Certificate )副本。请参阅图10-7和图10-8。图10-7展示了发送方加密电子邮件的过程，图10-8则展示了接收方解密电子邮件的过程。具体步骤如下：

**1.** 发送方创建用于对称加密( Symmetric Encryption )的密钥( Secret Key )。

例如，发送方可以创建一个值为 A1B2 的密钥。此时，只有发送方知道该密钥。

实际密钥会更复杂，此处为简洁起见使用 A1B2。

**2.** 发送方使用该密钥和对称加密算法对电子邮件进行加密。

该电子邮件只能通过此密钥解密，因此发送方还必须安全地将密钥传输给接收方。

**图 10-7：** 发送方加密电子邮件的过程

![f1007.eps](./image/Chapter%2010%20Enforcing%20Confidentiality%20with%20Encryption/f1007_fmt.webp)

**3.** 发送方获取接收方的证书，该证书包含接收方的公钥。

**4.** 发送方使用接收方的公钥对密钥进行加密。

此时，密钥 A1B2 被加密为类似 z1x2c7d@9 的形式。加密后的密钥在解密前无法被任何人使用，且只能通过接收方的私钥进行解密。

**5.** 发送方同时发送加密后的电子邮件和加密后的密钥。

由于电子邮件和密钥均已加密，即使攻击者通过嗅探器( Sniffer )捕获邮件，也无法读取任何内容。

**图 10-8：** 接收方解密电子邮件的过程

![f1008.eps](./image/Chapter%2010%20Enforcing%20Confidentiality%20with%20Encryption/f1008_fmt.webp)

**6.** 接收方收到加密后的电子邮件和加密后的密钥。

**7.** 接收方使用自己的私钥( Private Key )解密会话密钥。

**8.** 接收方使用解密后的会话密钥解密电子邮件内容。

关于此过程，许多人常问的一个问题是：“为什么不全程使用非对称加密( Asymmetric Encryption )？”换句话说，为什么不直接使用公钥( Public Key )加密整封邮件，而是先生成会话密钥（步骤1）、用会话密钥加密数据（步骤2）、再用公钥加密会话密钥（步骤4）？

这个问题问得很好，但请记住，非对称加密的速度比对称加密( Symmetric Encryption )慢 1000 倍甚至更多。使用对称加密来加密数据，仅用非对称加密来加密会话密钥，效率要高得多。此外，每次发送另一封邮件时都可以更换会话密钥。每封邮件的会话密钥都是随机生成的，这进一步增强了传输的安全性。

此过程的妙处在于它是自动化的。在 Microsoft 域内，应用程序可以查询 Active Directory 来查找他人的证书( Certificate )。例如，如果用户使用 Microsoft Outlook，他们可以选中“加密邮件内容和附件”复选框（如图 10-9所示）来加密邮件。Microsoft Outlook 随后会处理所有底层细节。当邮件被接收时，其他用户打开它，解密过程是自动完成的。

对于同一域内的用户，该过程是自动的。然而，当用户位于 Microsoft Active Directory 域之外时，必须手动交换证书。

**图 10-9：** 使用 Microsoft Outlook 加密电子邮件

![f1009.tif](./image/Chapter%2010%20Enforcing%20Confidentiality%20with%20Encryption/f1009_fmt.webp)

如果两个人想要发送电子邮件，他们可以私下交换证书。不同应用程序的流程有所不同；但通常来说，他们各自创建一个证书，交换这些证书，然后将证书安装到各自的计算机上。尽管这需要更多的手动干预才能实现，但其好处是它可以与不同的电子邮件程序配合使用。例如，双方无需都运行 Microsoft Outlook。

**对电子邮件进行数字签名( Digitally Signing Email )**

经过数字签名的电子邮件包含一个数字签名( Digital Signature )。这提供了证据，证明该电子邮件是由特定人员发送的。同时，它还提供了不可否认性( Nonrepudiation )和完整性( Integrity )。

第5章描述了审核日志如何通过记录用户活动来提供不可否认性。数字签名为电子邮件提供了不可否认性。

数字签名使用哈希( Hashing )来提供完整性。哈希值在源端和目标端分别计算；只要两者相同，收件人就能验证邮件未被篡改。

数字签名使用公钥( Public Key )和私钥( Private Key )，但其工作方式与加密电子邮件略有不同。提醒一下，加密电子邮件时，你会获取收件人的公钥并用其加密邮件。相比之下，数字签名由发件人使用发件人的私钥进行签名。

阅读以下步骤时，请参阅图10-10和图10-11。图10-10展示了发件人对电子邮件进行数字签名的过程。图10-11展示了收件人验证数字签名的过程。

**1.** 发件人创建电子邮件。

在此示例中，邮件无需保密。如果需要保密，可以对其进行加密。然而，本示例仅关注数字签名。

可以仅对电子邮件进行数字签名，仅加密电子邮件，或同时进行数字签名和加密。

**2.** 对电子邮件内容进行哈希处理。

在此示例中，哈希值为1A3B5C7E9。如果使用MD5，它将是32个十六进制数字；如果使用SHA-1，它将是40个十六进制数字。此处为简洁起见进行了缩短。

**3.** 使用发件人的私钥对电子邮件的哈希值进行加密。

在示例中，这得到结果43c0lm120p。此加密后的哈希值被用作数字签名。

**图10-10:** 发件人对电子邮件进行数字签名时的处理过程

![f1010.eps](./image/Chapter%2010%20Enforcing%20Confidentiality%20with%20Encryption/f1010_fmt.webp)

**4.** 未加密的电子邮件与加密后的哈希值（即数字签名( Digital Signature )）一同发送给收件人。

**图 10-11：** 收件人验证数字签名的过程

![f1011.eps](./image/Chapter%2010%20Enforcing%20Confidentiality%20with%20Encryption/f1011_fmt.webp)

**5.** 收件人同时收到邮件正文与数字签名。

**6.** 收件人从发件人的数字证书( Digital Certificate )中提取其公钥( Public Key )。

在某些情况下，收件人可能已持有发件人的证书；而在另一些情况下，收件人还需先获取该证书。

**7.** 收件人使用发件人的公钥解密收到的哈希值。

若公钥无法解密该加密哈希值，则表明该哈希值并非使用发件人的私钥( Private Key )加密。反之，若公钥能成功解密，则证明该哈希值确由发件人的私钥加密。这一过程验证了证书中所标识的发件人身份。同时，由于发件人的私钥被用于加密哈希值，发件人无法事后否认曾发送该邮件（实现了不可否认性( Nonrepudiation )）。

在此示例中，解密后的哈希值为 1A3B5C7E9（即发件人计算并加密的原始哈希值）。

若公钥能解密哈希值，则该哈希值必然由与之匹配的私钥加密。这既验证了发件人身份，也提供了不可否认性。

**8.** 对收到的邮件正文进行哈希计算。

在此示例中，计算得到的哈希值为 1A3B5C7E9。

**9.** 将步骤 7 中解密得到的哈希值（1A3B5C7E9）与步骤 8 中重新计算的哈希值（1A3B5C7E9）进行比较。若两者一致，则验证了邮件内容未被篡改，即完整性( Integrity )未遭破坏。

与电子邮件加解密过程类似，数字签名操作对用户而言几乎透明。例如，使用 Microsoft Outlook 的用户只需勾选相应复选框即可为邮件添加数字签名（如前文图 10-9所示）。Outlook 会自动处理所有底层细节。收件人打开邮件时，数字签名即被自动验证；若存在任何问题，收件人将收到相应通知。

了解 EFS

第4章“使用权限保护访问”介绍了 NTFS。NTFS 提供安全功能，例如为文件和文件夹分配权限以限制访问。NTFS 的另一个功能是加密文件系统( Encrypting File System ,EFS)。在 NTFS 卷上，可以使用 EFS 加密 NTFS 文件和文件夹。当使用 EFS 加密文件时，只有特定用户才能访问它。

可以按照以下步骤使用 EFS 加密文件夹和文件：

Microsoft 建议加密文件夹而非单个文件。文件夹内的所有文件将自动加密。

**1.** 启动 Windows 资源管理器( Windows Explorer )，浏览到目标文件夹。

**2.** 右键单击该文件夹，选择“属性”。

**3.** 在“常规”选项卡中，单击“高级”按钮。

**4.** 在“高级属性”页面上，选中“加密内容以便保护数据”复选框，如图 10-12所示。

可以通过配置组策略( Group Policy )设置来移除使用 EFS 加密文件的能力。如果 EFS 未显示，可能是此原因。

**5.** 单击“确定”。在提示时，选择“将更改应用于此文件夹、子文件夹和文件”。

加密的文件夹和文件在 Windows 资源管理器( Windows Explorer )中显示为绿色文本。

当授权用户打开加密文件时，文件会自动解密，无需任何用户交互。以下部分展示了加密和解密文件的步骤。除此之外，在后台还有大量其他活动用于使用 EFS 加密和解密文件。

**图 10-12：** 使用 EFS 加密文件夹

![f1012.tif](./image/Chapter%2010%20Enforcing%20Confidentiality%20with%20Encryption/f1012_fmt.webp)

使用 EFS 加密和解密文件

EFS 结合使用对称加密( Symmetric Encryption )和非对称加密( Asymmetric Encryption )来加密文件。它为每个加密的文件创建一个不同的对称密钥( Symmetric Secret Key )。然后使用非对称加密( Asymmetric Encryption )加密此密钥。以下步骤展示了使用 EFS 加密文件的整体过程：

**1.** EFS 创建一个对称密钥( Symmetric Secret Key )来加密文件。

每个文件使用不同的对称密钥( Symmetric Secret Key )。即使攻击者意外发现某个文件的密钥，也无法使用同一密钥解密其他文件。

**2.** EFS 检索用户的公钥( Public Key )。

用户首次加密文件时，EFS 会与操作系统协同工作，为其创建 EFS 加密证书( EFS Encryption Certificate )。该证书包含用户的公钥( Public Key )，而用户对匹配的私钥( Private Key )拥有独占访问权限。

**3.** EFS 使用用户的公钥加密对称密钥( Symmetric Secret Key )。

**4.** 加密后的对称密钥被写入加密文件的文件头( Header )中。

当用户双击文件打开时，EFS 执行以下步骤：

EFS 的安全性完全取决于用户密码。若用户密码泄露，攻击者可模拟该用户登录并打开加密文件。

**1.** 从文件中提取加密的对称密钥。

**2.** 用户私钥解密对称密钥。

**3.** EFS 使用解密后的对称密钥解密文件。

同样，此过程完全自动执行。只要用户不丢失私钥的访问权限，文件便会自动解密，无需任何额外用户交互。

最终用户极少需要手动操作私钥。但若本地用户（非域用户）的密码被重置，与该账户关联的私钥将丢失，用户将无法解密任何使用原密码加密的文件。此情况仅发生在密码被重置时（例如由管理员执行），而非用户自行更改密码时。此外，与文件类似，最终用户的私钥也可能损坏而无法使用。

第 3 章介绍了如何创建密码重置磁盘( Password Reset Disk )。若已创建该磁盘，用户可在无需管理员协助且不丢失加密文件访问权限的情况下重置密码。

了解恢复代理( Recovery Agent )

若用户私钥丢失或损坏，用户将无法再解密文件。但 EFS 内置了恢复机制以降低数据丢失风险。

默认情况下，系统内置管理员账户( Built-in Administrator Account )被指定为 EFS 的恢复代理( Data Recovery Agent ,DRA )。作为 DRA，管理员可解密文件。在某些组织中，可能由其他人员（而非管理员账户）承担 DRA 角色。

DRA 功能可被禁用。对于某些组织而言，DRA 账户被用于访问加密数据的风险，可能高于因密钥丢失导致数据丢失的风险。在此情况下，DRA 不会被启用；若用户的 EFS 私钥丢失或损坏，数据将永久丢失。

了解文件移动或复制时的行为

第 4 章重点介绍了文件复制或移动时的权限行为。回顾一下，你可以使用两条简单规则来判断移动或复制文件的权限：

- 如果在同一分区内移动文件，则保留最初分配的权限。
- 其他任何情况下，最初分配的权限都会丢失，仅应用继承权限。

EFS 的工作方式略有不同。使用 EFS 时需要记住的一条规则是：*加密始终优先*。

在移动或复制文件时，加密始终优先。只要过程中存在任何加密文件的可能性，文件就会被加密。

其核心理念是：你已认定某个文件足够重要，因此对其加密以保护它。如果你将该文件移动或复制到任何其他 NTFS 驱动器，操作系统不会自动解密它。如果文件最初是加密的，或者目标文件夹已启用加密，则该文件将被加密。

例如，如果 C:\Encrypted 文件夹启用了加密属性，则所有移入或复制到此文件夹的文件都将被加密。如果加密文件从此文件夹移动或复制到 NTFS 文件系统上的任何其他位置，它将保持加密状态。

表 10-1 显示了不同加密状态下的结果。对于加密而言，文件是移动还是复制无关紧要，结果始终相同：加密优先。

**表 10-1:** 文件移动或复制时对加密的影响

| 原始加密状态 | 目标位置加密设置 | 结果       |
| ------------ | ---------------- | ---------- |
| 已启用加密   | 已启用加密       | 已加密     |
| 未加密       | 已启用加密       | 已加密     |
| 已启用加密   | 未加密           | 已加密     |
| 未加密       | 未加密           | 未加密     |

如果你使用的是 FAT（或 FAT32）驱动器，情况则略有不同。回顾一下，FAT 不支持 NTFS 的任何安全功能，包括加密。FAT 没有 NTFS 文件的标头，因此无法存储解密文件所需的密钥。

如果你是文件的授权用户，并将其移动或复制到 FAT 驱动器，EFS 会解密该文件并以未加密格式存储。然而，如果非授权用户将加密文件移动或复制到 FAT 驱动器，文件会以加密格式被复制。此外，由于 FAT 不存储加密密钥，文件的加密密钥会丢失，文件将永久保持加密状态。

探索 BitLocker 驱动器加密

BitLocker 驱动器加密( BitLocker Drive Encryption )使用加密技术保护整个卷上的数据。相比之下，EFS 加密的是单个文件。BitLocker 有两种形式：BitLocker 和 BitLocker To Go。

BitLocker 加密卷或分区。如果单个硬盘配置为两个分区（例如 C: 和 D:），BitLocker 可以加密 D: 而不加密 C:。

你可以在 Windows 7、Windows Vista、Windows Server 2008 和 Windows Server 2008 R2 中使用 BitLocker 加密整个卷。此外，你还可以在 Windows 7 和 Windows Server 2008 R2 系统上使用 BitLocker To Go 加密可移动 USB 闪存驱动器。

BitLocker 仅适用于 Windows 7 和 Windows Vista 的旗舰版( Ultimate )和企业版( Enterprise )。

图 10-13 显示了 Windows 7 系统上控制面板中的 BitLocker 驱动器加密页面。在图中，你可以看到系统卷上未启用 BitLocker。然而，插入计算机的其中一个 USB 闪存驱动器上已启用 BitLocker To Go。

**图 10-13：** 控制面板中的 BitLocker 驱动器加密

![f1013.tif](./image/Chapter%2010%20Enforcing%20Confidentiality%20with%20Encryption/f1013_fmt.webp)

BitLocker 使用 AES 加密磁盘驱动器。

理解 BitLocker 要求

BitLocker 和 BitLocker To Go 在 Windows 7 企业版和旗舰版中默认可用，但在 Windows Server 2008 或 Windows Server 2008 R2 中默认不可用。你可以使用服务器管理器( Server Manager )将 BitLocker 添加为功能。这会在 Windows Server 2008 上启用 BitLocker，并在 Windows Server 2008 R2 上同时启用 BitLocker 和 BitLocker To Go。

BitLocker 可以使用受信任的平台模块( Trusted Platform Module ,TPM ) 1.2 版或可移动 USB 存储设备来锁定和解锁驱动器。TPM 是计算机主板上的一个芯片，包含用于检查系统硬件是否存在可疑修改的程序，并存储和保护用于解锁卷的密钥。TPM 会检查环境的各个方面，例如确保启动文件未被修改。如果这些检查通过，TPM 模块会释放密钥以解锁卷；如果检查未通过，卷将保持锁定状态。尽管 TPM 是硬件，驱动器仍通过软件方法进行加密。TPM 利用硬件（TPM 芯片）在检查失败时保护密钥。

如果计算机被盗且硬盘被移至其他系统，该硬盘将保持锁定状态并受到保护。

并非所有系统都配备 TPM。此外，在许多 BIOS 系统中，TPM 默认未启用。如果系统没有 TPM，可以使用包含启动密钥的 USB 闪存驱动器。系统启动时，插入 USB 闪存驱动器，BitLocker 会读取启动密钥，然后解锁驱动器。强烈建议不要将 USB 闪存驱动器与计算机存放在一起，否则窃贼可能同时盗走计算机和 USB 闪存驱动器。

还可以通过 BitLocker 实施其他身份验证方法来增强安全性。支持以下组合：

**TPM 和个人识别码( Personal Identification Number ,PIN )** 用户必须在启动时输入 PIN。

**TPM 和 USB 闪存驱动器** 系统启动后应移除 USB 设备，当系统需要重新启动时，用户再插入 USB。

**TPM、PIN 和 USB 闪存驱动器** 用户在启动时插入 USB 闪存驱动器，并在提示时输入 PIN。

了解恢复密钥

如果 BitLocker 驱动器被锁定，可以使用恢复密钥恢复数据。例如，如果计算机发生硬件故障，可以将硬盘移至另一台计算机，并使用恢复密钥解锁。

在驱动器上启用 BitLocker 时，系统会提示保存恢复密钥。可以将密钥存储为文件或打印出来。如果存储为文件，需要将其保存在与加密驱动器不同的驱动器上。

若需随时创建恢复密钥的额外副本，可通过控制面板中的"管理 BitLocker"窗口完成操作。但需注意，必须能够解锁驱动器才能创建恢复密钥副本。

使用 BitLocker To Go

BitLocker To Go 是 Windows 7 和 Windows Server 2008 R2 内置的一项便捷功能，可轻松加密 USB 闪存驱动器。在 Windows 7 系统上通过 BitLocker To Go 加密单个 USB 驱动器的步骤如下：

**1.** 将待加密的 USB 闪存驱动器插入计算机 USB 接口。

**2.** 从"开始"菜单启动控制面板。

**3.** 在"搜索控制面板"文本框中输入 **BitLocker**，然后选择"BitLocker 驱动器加密"。

**4.** 在列表中找到 USB 闪存驱动器，选择"启用 BitLocker"。

**5.** 勾选"使用密码解锁驱动器"复选框。

**6.** 在"输入密码"和"重新输入密码"文本框中设置密码，单击"下一步"。

**7.** 在"希望如何存储恢复密钥"页面，选择"将恢复密钥保存到文件"。

**8.** 浏览选择恢复密钥的保存位置，单击"保存"。

**9.** 单击"下一步"，再单击"开始加密"按钮。加密过程随即启动，根据 USB 驱动器容量和系统速度，可能需要一定时间。

**10.** 加密完成后，单击"关闭"。

此时该驱动器上的文件已加密。若拔出 USB 闪存驱动器后重新插入已启用 BitLocker 的 Windows 7 或 Windows Server 2008 R2 系统，系统将提示输入密码。输入密码并单击"解锁"后，即可正常使用驱动器。

此外，还可配置 BitLocker，使其在将可移动驱动器插入已安装 BitLocker 的兼容计算机时自动解锁。

即使系统未启用 BitLocker，也可访问加密文件。例如，将 USB 闪存驱动器插入 Windows XP 系统后，通过 Windows 资源管理器浏览。双击 BitLocker To Go 应用程序后，系统将提示输入密码（如图 10-14 所示），以启动 BitLocker To Go 读取器。输入正确密码并单击"解锁"后，即可访问文件。

**图 10-14：** 使用 BitLocker To Go 读取器

![f1014.tif](./image/Chapter%2010%20Enforcing%20Confidentiality%20with%20Encryption/f1014_fmt.webp)

使用 BitLocker To Go 读取器时，你将无法修改 USB 驱动器上的文件。此外，你也不能通过 BitLocker To Go 读取器将文件复制到 USB 驱动器。不过，BitLocker To Go 读取器允许你将文件从该驱动器复制到另一台计算机的驱动器上。

你只能使用 BitLocker To Go 读取器读取和复制 BitLocker To Go 加密驱动器中的文件。你无法修改这些文件，也无法将文件复制回 USB 驱动器。

基础与进阶

在本章中，你学习了加密数据的不同方法。对称加密( Symmetric Encryption )使用单个密钥来加密和解密数据。非对称加密( Asymmetric Encryption )使用两个密钥（公钥和私钥）来加密和解密数据。非对称加密的速度大约比对称加密慢 1000 倍，通常仅用于加密和解密对称密钥。AES 是一种强大且高效的对称加密算法，广泛应用于多种场景，包括 Kerberos 和 BitLocker。哈希( Hashing )提供单向加密，用于完整性校验。MD5 和 SHA-1 是两种常见的哈希算法。你可以通过加密和数字签名( Digital Signature )来保护电子邮件安全。这两种操作都需要使用数字证书( Digital Certificate )来公开共享公钥。EFS 内置于 NTFS 中，允许用户加密文件夹和文件。EFS 结合使用了非对称加密和对称加密。BitLocker 驱动器加密( BitLocker Drive Encryption )可以加密整个卷。它可以在主板内置 TPM v1.2 模块的情况下使用，也可以在没有该模块的情况下使用。BitLocker To Go 可用于加密 USB 闪存驱动器上的数据。

附加练习

- 列出对称加密算法与非对称加密算法之间的主要区别。
- 确定你的电子邮件是否支持数字签名。
- 在 NTFS 中加密一个文件夹。将一个未加密的文件复制到该文件夹中，并检查它是否已被加密。
- 使用 BitLocker To Go 加密一个 USB 闪存驱动器。

---

## 第11章 理解证书与PKI

**公钥基础结构**( Public Key Infrastructure ,PKI)包含颁发、使用和管理证书所需的所有组件。证书( Certificate ,也称公钥证书)广泛应用于多种场景，以提供不同类型的安全性保障。例如，如第10章"使用加密强制机密性"所述，证书可用于对电子邮件进行数字签名和加密。

证书包含以下详细信息：颁发者、颁发对象、到期时间，以及公钥和序列号等唯一数据。由于证书可用于提供安全保证，每次使用时都会对其进行检查，以确保证书未过期、未被篡改或未被吊销。如果证书未通过这些检查，用户将看到详细说明问题的错误信息。

证书颁发机构( Certification Authority ,CA)是PKI的重要组成部分。CA向用户和计算机颁发证书，并定期响应关于证书的查询以验证其有效性。如果证书遭到泄露，CA还可以吊销证书，从而告知用户该证书存在问题。本章将涵盖以下主题：

- 理解证书
- 探索PKI的组件

### 理解证书

*证书*是一种用于多种安全目的的文件。证书可以颁发给个人并与用户帐户关联。例如，用户可能使用智能卡进行身份验证。证书文件嵌入到智能卡中，使用户能够将证书随身携带到不同系统。证书也可以颁发给服务器、工作站或手机等设备，并在证书有效期内与该设备绑定。在域环境中，证书通常自动颁发给用户，几乎不需要用户交互。然而，管理员通常需要手动在服务器上请求和安装证书。

大多数证书是扩展名为.cer的文件。这些文件采用特殊的X.509格式进行格式化。

证书包含以下几个关键数据项：

- 颁发对象
- 颁发者
- 用途
- 有效期(包括到期时间)
- 唯一序列号
- 公钥

证书中嵌入的公钥与私钥配对使用。私钥保持私密，而公钥则通过证书共享。

例如，图11-1展示了Windows 7计算机上安装的多个证书以及其中一个证书的常规详细信息。请注意，您可以在此处导入或导出证书文件。您还可以选择任意证书并单击"查看"以查看证书的详细信息。

**图11-1：** 查看证书

![f1101.eps](./image/Chapter%2011%20Understanding%20Certificates%20and%20a%20PKI/f1101_fmt.webp)

本章稍后的"查看证书属性"部分将逐步说明如何查看证书的属性。

证书用于多种用途。以下列表展示了一些常见用法：

**身份验证( Authentication )** 证书帮助用户和计算机证明其身份。当证书由受信任实体颁发给个人或服务器时，任何使用该证书作为身份验证来源的系统都能确信对方身份属实。例如，证书可以颁发给互联网Web服务器，如托管戴尔网站的服务器。如果您连接到 **dell.com** 购买产品，Web服务器会向您的浏览器出示证书，以证明它确实是戴尔的Web服务器。

**加密( Encryption )** 证书可用于加密静态数据和传输中的数据，以防止未经授权的数据泄露。加密后的数据除非拥有正确的解密密钥，否则他人无法读取。

第10章介绍了多种加密方法，包括使用证书的方法。

**数字签名( Digital Signature )** 可以在电子邮件中添加数字签名，向收件人证明邮件的发送者身份。它提供了身份验证、完整性( Integrity )和不可否认性( Nonrepudiation )。

第10章解释了如何使用数字签名对电子邮件进行签名。

**代码签名( Code Signing )**  
Internet 网页上使用的活动内容( Active Content )可通过数字签名( Digital Signature )标识作者身份，并验证代码未被篡改。攻击者不愿暴露身份，因此不会对其恶意代码进行签名。然而，合法公司会使用代码签名证书( Code-Signing Certificate )对活动内容进行签名，为代码增加合法性。可以阻止所有未签名代码在 Internet Explorer 等 Web 浏览器中运行。

证书由证书颁发机构( Certification Authority ,CA )颁发和管理。CA 可以是公共组织，也可以是组织内部的私有实体。例如，VeriSign 是一家提供公共 CA 服务的公司，其颁发的证书在 Internet 上广泛使用。不过，你也可以通过向 Windows Server 2008 服务器添加 Active Directory 证书服务( Active Directory Certificate Services ,AD CS )角色来创建私有 CA。管理员随后可在其环境中管理运行 AD CS 的服务器，以颁发和管理证书。

本章后续的“探索 PKI 的组件”一节将更深入地介绍 CA。

**比较公钥与私钥**

公钥( Public Key )和私钥( Private Key )已在第 10 章中介绍。在此提醒，这两个密钥以匹配对的形式创建，用于非对称加密( Asymmetric Encryption )。用公钥加密的任何内容都可用匹配的私钥解密。同样，用私钥加密的任何内容都可用匹配的公钥解密。

密钥对中的两个密钥只能相互配合使用。来自某一密钥对的密钥无法解密用另一匹配对中的密钥加密的数据。

私钥始终保密，绝不共享。如果私钥泄露，未经授权的人员可访问该私钥，则不应再使用该密钥对。当私钥泄露时，CA 可以吊销包含匹配公钥的证书。

与之相反，公钥( Public Key )是自由分发的。公钥嵌入在数字证书( Certificate )中，任何需要的人均可获取该证书。在 Microsoft 域环境中，包含公钥的证书可在需要时自动检索。例如，若用户希望使用 Microsoft Outlook 加密电子邮件，只需单击按钮。Outlook 随后会查询 Active Directory 以定位收件人的证书，并使用检索到的证书中嵌入的用户公钥对邮件进行加密。在互联网上，包含公钥的证书会在需要时发送给收件人。

例如，图 11-2 展示了在互联网上如何使用公钥和私钥( Private Key )来安全共享 HTTPS 会话的密钥( Secret Key )。假设用户已订阅 Microsoft 的 TechNet。在用户登录网站之前，会先建立 HTTPS 会话，以确保用户名和密码在通过互联网发送前被加密。

**图 11-2：** 创建 HTTPS 会话

![f1102.eps](./image/Chapter%2011%20Understanding%20Certificates%20and%20a%20PKI/f1102_fmt.webp)

以下步骤展示了整体流程：

**1.** 客户端单击链接或输入 URL 以发起 HTTPS 会话。尽管此示例展示了安全 TechNet 会话的工作方式，但其原理适用于任何由 HTTPS 保护的会话。

**2.** 服务器在收到请求后，向客户端发送其证书，其中嵌入了公钥。需注意，该公钥与服务器上保持私密的私钥相匹配。

**3.** 客户端创建一个密钥（例如 A1B2C3），该密钥最终将用于加密会话数据。实际密钥会更长，此处为简洁起见进行了缩短。

**4.** 创建密钥后，客户端使用服务器的公钥对其进行加密。密钥现在被加密为密文( Cipher Text )（例如 ac8vt3yui*7ba9nf），只有服务器的私钥才能解密。

**5.** 客户端将加密后的密钥（ac8vt3yui*7ba9nf）发送至 TechNet 服务器。即使互联网上的任何人截获了此加密密钥，也无法读取其内容，因为只有服务器的私钥才能解密。

**6.** 服务器收到加密的机密密钥后，使用其匹配的私钥解密该密钥。此时，客户端和服务器都知道机密密钥是什么，但其他任何人都不知道。

**7.** HTTPS 会话使用机密密钥进行加密和解密。

在此上下文中，机密密钥有时称为会话密钥( Session Key )。它仅用于当前会话。对于其他任何会话，都会使用新的会话密钥重复此过程。

为何要费心使用机密密钥？

一个常见的问题是：“公钥和私钥已经在使用，为什么不直接用它们来加密和解密整个会话？”表面上看，这似乎可能更高效。

然而，如第 10 章所述，使用公钥和私钥的非对称加密( Asymmetric Encryption )比使用单一对称密钥( Symmetric Key )的对称加密( Symmetric Encryption )慢大约 1000 倍（有时甚至更慢）。仅使用非对称过程来私下共享机密密钥要高效得多。当双方都知道机密密钥后，它们便切换为仅使用机密密钥来加密和解密会话。

理解证书错误

在证书被机器接受用于其预期用途之前，可能会执行多项检查以验证证书是否有效。这些检查通常是自动进行的，但如果其中一项检查失败，用户通常会看到错误。

例如，每次将证书传递给客户端时，客户端可能会向证书颁发机构( Certification Authority ,CA)检查，以确保该证书未被吊销。CA 会以证书形式发布证书吊销列表( Certificate Revocation List ,CRL)，如图 11-3所示。CRL 包含所有已吊销证书的序列号以及吊销日期。CRL 始终以称为*版本 2 证书*的特殊证书格式发布。相比之下，其他证书则以称为*版本 3 证书*或较旧的版本 1 证书的不同格式发布。

**图 11-3：** 查看 CRL

![f1103.eps](./image/Chapter%2011%20Understanding%20Certificates%20and%20a%20PKI/f1103_fmt.webp)

客户端验证证书是否已被吊销的一种方式是检索 CRL 副本。如果待验证证书出现在 CRL 上，则表明该证书已被颁发 CA 吊销，不应再被信任。在图中，仅有一张证书被吊销；但 CRL 包含多张证书的情况并不罕见。

客户端还有其他方式验证证书是否已被吊销。然而，最关键的一点是理解证书会被检查这一事实。

图 11-4 展示了客户端验证证书的完整流程：

**1.** 服务器将证书发送给客户端。

**2.** 客户端验证证书是否已过期，并确保证书中的名称与服务器名称匹配。

**3.** 客户端向颁发该证书的 CA 查询，以确定证书是否已被吊销。

**图 11-4:** 检查证书有效性

![f1104.eps](./image/Chapter%2011%20Understanding%20Certificates%20and%20a%20PKI/f1104_fmt.webp)

以下列表显示了可能遇到的证书问题相关错误：

**“此网站的安全证书已被吊销。”** 这表明私钥已泄露或证书被欺诈性使用。如果证书已被吊销，原证书持有者不会使用它，但恶意攻击者可能会欺诈性地使用它。

**“此网站的安全证书已过期。”** 这表明证书已过期。CA 不会验证过期证书，因此不应信任它们。提醒一下，图 11-4 展示了每次使用证书时的验证方式。此证书可能因被盗并被欺诈性使用而被吊销；但由于 CA 未对其进行验证，您将永远无法得知。

**“此网站的安全证书并非来自可信源。”** 这表明证书并非由受信任的 CA 颁发。在恶意钓鱼尝试中常见此错误。

“**Internet Explorer 发现此网站的安全证书存在问题。**”多种问题均会触发此错误。例如，如果证书被修改、篡改或无法读取，就会发生此错误。

“**此网站的安全证书存在问题。**”这表明证书颁发给了一个网站，但另一个网站正在使用它。图 11-5 显示了此验证步骤失败时，在 Internet Explorer 中看到的错误。

所有这些错误均表明证书存在问题，不应使用该证书。

**图 11-5：** 证书错误

![f1105.tif](./image/Chapter%2011%20Understanding%20Certificates%20and%20a%20PKI/f1105_fmt.webp)

您可能还会看到 Web 浏览器的地址栏变为红色，并且安全状态栏（地址栏旁边）中显示“证书错误”消息。当您看到证书存在任何类型的问题时，不建议继续操作。不过，您可以单击“继续浏览此网站(不推荐)”。如果继续操作，则不应输入任何私人信息。如果攻击者欺诈性地使用该证书，即使建立了 HTTPS 会话，他们也能查看您提交的任何私人信息。

查看证书属性

您可以通过以下步骤查看证书及其属性：

这些步骤针对 Internet Explorer 8 编写，但也适用于 Internet Explorer 7。

**1.** 启动 Internet Explorer。

**2.** 选择“工具”⇒“Internet 选项”。

**3.** 选择“内容”选项卡。

**4.** 单击“证书”按钮。

**5.** 选择“受信任的根证书颁发机构”选项卡。您的显示将类似于图 11-6。

**6.** 在受信任的根证书颁发机构存储中选择一个证书。

**7.** 单击“高级”。滚动浏览“证书目的”列表，如图 11-7 所示。请注意，该证书可用于多种不同目的，例如服务器身份验证和代码签名。

**8.** 单击“取消”。

**图 11-6：** 查看受信任的根证书颁发机构( Trusted Root Certification Authorities )存储

![f1106.eps](./image/Chapter%2011%20Understanding%20Certificates%20and%20a%20PKI/f1106_fmt.webp)

由证书颁发机构( Certification Authority ,CA)颁发的证书，若其证书存在于受信任的根证书颁发机构存储中，则会被自动信任。

**图 11-7：** 查看证书的用途

![f1107.eps](./image/Chapter%2011%20Understanding%20Certificates%20and%20a%20PKI/f1107_fmt.webp)

**9.** 单击“查看”按钮。显示界面将类似于图 11-1（本章前文已展示）。请注意，“常规”选项卡以简洁的要点形式显示了证书的用途，同时还显示了证书的颁发对象、颁发者以及证书的有效期。

**10.** 单击“详细信息”选项卡，然后选择“颁发者”。显示界面将类似于图 11-8。在此处还可以查看其他详细信息，例如序列号、公钥( Public Key )等。

**11.** 滚动浏览“详细信息”选项卡中的不同字段和值。选择任意项目时，其值会显示在窗口底部的窗格中。

**12.** 单击“证书路径”选项卡。显示界面将类似于图 11-9。此选项卡显示了通往根 CA 的路径，该路径也称为*证书链( Certificate Chain )*。当证书由根 CA 直接颁发时，链中仅列出一个证书——即颁发该证书的 CA。当列出多个证书时，则显示了通往根 CA 的完整路径。

**图 11-8：** 查看证书的详细信息

![f1108.eps](./image/Chapter%2011%20Understanding%20Certificates%20and%20a%20PKI/f1108_fmt.webp)

**图 11-9：** 查看证书路径

![f1109.tif](./image/Chapter%2011%20Understanding%20Certificates%20and%20a%20PKI/f1109_fmt.webp)

证书路径也称为证书链。本章后续“理解证书链”一节将对证书链进行详细说明。

### 探索 PKI 的组件

公钥基础结构( Public Key Infrastructure ,PKI)包含为不同目的颁发、管理、验证和使用证书所需的所有组件。PKI 包含以下组件：

**公钥/私钥对( Public/Private Key Pairs )** 公钥/私钥对是一组用于数据加密和解密的匹配密钥。这些匹配的密钥对可以相互配合使用，但不能与其他密钥对中的密钥配合使用。通常使用应用程序来生成这些匹配的密钥对。

**证书( Certificates )** 证书是一种电子文件。它包含详细信息，例如颁发者、颁发对象、有效期以及公钥。

**证书颁发机构( Certification Authority ,CA)** CA 负责颁发和管理证书。如果某个证书或私钥遭到泄露，CA 会吊销持有匹配公钥的证书。CA 会响应查询以验证证书的状态。

**注册机构( Registration Authority ,RA)** RA 是可选的，但在大型组织中，它可以分担 CA 的部分负载。RA 接受证书请求并验证请求者的凭据。请求验证通过后，RA 会将请求转发给 CA。RA 从不颁发证书。

**根 CA( Root CA )** 证书链中的第一个 CA 称为根 CA。根 CA 可以向从属 CA( Subordinate CA )颁发证书，这些 CA 被视为属于同一证书链。如果某台计算机信任根 CA，则它信任该证书链中任何 CA 颁发的所有证书。Microsoft 系统将来自许多公共根 CA 的证书存储在 *受信任的根证书颁发机构存储( Trusted Root Certification Authority store )* 中。

### 理解证书链

![f1102.eps](./image/Chapter%2011%20Understanding%20Certificates%20and%20a%20PKI/f1102_fmt.webp) 

展示了证书信任链的一个示例。根 CA 是链中的第一个 CA。它为自己颁发自签名证书( Self-Signed Certificate )。然后，它可以向中间 CA( Intermediate CA )颁发证书。中间 CA 可以向从属 CA 颁发证书。证书由从属 CA 或颁发 CA( Issuing CA )颁发给客户端。

![f1103.eps](./image/Chapter%2011%20Understanding%20Certificates%20and%20a%20PKI/f1103_fmt.webp) 

展示了受信任的根证书颁发机构存储的内容。此存储中的每个证书都代表一个受信任的根 CA。

**图 11-10：** 证书链( Certificate Chain )

![f1110.eps](./image/Chapter%2011%20Understanding%20Certificates%20and%20a%20PKI/f1110_fmt.webp)

证书链的优势在于，如果根证书颁发机构( Root Certification Authority ,根 CA)受信任，则链中任何证书颁发机构( Certification Authority ,CA)颁发的所有证书也自动受信任。根 CA 的信任通过将其根证书( Root Certificate )放入受信任的根证书颁发机构( Trusted Root Certification Authorities )存储区来实现。

微软与众多公共 CA（如 VeriSign）签订了协议，并将这些公共 CA 的证书预置于其操作系统的受信任的根证书颁发机构存储区中。在互联网上进行电子商务的公司从这些公共 CA 购买证书。当电子商务公司向您发送证书时，您的系统会检查该证书是否由受信任的根证书颁发机构存储区中的受信任 CA 颁发。如果证书由受信任 CA 颁发，则视为可信；反之则不可信。例如，当您从 Amazon.com 购买产品时，Amazon 会向您发送其从 VeriSign 购买的证书。由于您信任 VeriSign（它位于受信任的根证书颁发机构存储区中），因此您也信任 Amazon 发送的证书。

这一概念类似于对驾驶执照的信任。当您在银行出示驾驶执照作为身份证明时，该执照会被信任。银行工作人员相信机动车辆管理局( Department of Motor Vehicles ,DMV)已采取充分措施验证您的身份；因为他们信任 DMV，所以也信任您的身份证明有效。反之，如果您从 FlyByNight IDs 购买身份证明，银行很可能不会接受，因为银行与 FlyByNight IDs 之间可能不存在信任关系。

类似地，如果某个电子商务网站从 FlyByNight 证书颁发机构购买证书，该证书默认情况下可能不受信任。由于 FlyByNight 根 CA 的证书默认不在受信任的根证书颁发机构存储区中，因此该 CA 颁发的任何证书也不会被信任。

尽管图 11-10 展示了一条较长的证书链( Certificate Chain )，但这并非必需。例如，图 11-11 展示了一个简单的证书颁发机构( Certificate Authority ,CA)配置。单个 CA 被创建为根 CA( Root CA )，并向客户端颁发证书。

**图 11-11：** 证书链中的单个 CA

![f1111.eps](./image/Chapter%2011%20Understanding%20Certificates%20and%20a%20PKI/f1111_fmt.webp)

图 11-11 展示了在内部组织（如 Microsoft 域）中创建 CA 的常见方式。单个服务器被配置为 CA，用于在组织内颁发证书。

该 CA 的根证书( Root Certificate )通过组策略( Group Policy )或其他自动化方法放置在用户的受信任根证书颁发机构( Trusted Root Certification Authority )存储中。

**比较证书服务**

你可以添加 Microsoft 的 Active Directory 证书服务( Active Directory Certificate Services ,AD CS)来创建 CA。AD CS 作为角色添加到 Windows Server 2008 中；它可以添加为企业 CA( Enterprise CA )或独立 CA( Standalone CA )。通常，企业 CA 仅用于在组织内颁发证书，而独立 CA 可用于在组织内外颁发证书：

当组织创建自己的 CA 时，无需从公共 CA 购买内部使用的证书。

**独立 CA**：该 CA 可用于在组织内或公开颁发证书。CA 不必是 Microsoft Active Directory 域的成员，但也可以加入。证书请求( Certificate Request )需手动提交并手动批准。

**企业 CA**：用于 Microsoft 域内，需要 Active Directory 域服务( Active Directory Domain Services ,AD DS )。企业 CA 仅用于在公司或企业内颁发证书。企业 CA 的优势之一是管理员可以为证书配置自动注册( Autoenrollment )，以便根据 CA 的配置自动颁发证书。凭据( Credential )通过 Active Directory 中的身份验证( Authentication )进行检查。

企业 CA 在域内用于向内部用户和计算机颁发证书。

图11-12展示了一台在 Windows Server 2008 服务器上创建的企业 CA( Enterprise CA )。通过添加 Active Directory 证书服务( Active Directory Certificate Services )角色，即可在 Windows Server 2008 服务器上创建 CA。图中，该 CA 已向一台域控制器颁发了一张用于身份验证( Authentication )的证书。

**图11-12:** Windows Server 2008 中的企业 CA

![f1112.tif](./image/Chapter%2011%20Understanding%20Certificates%20and%20a%20PKI/f1112_fmt.webp)

具体选择取决于证书的用途。例如，如果组织需要为域内用于身份验证的智能卡( Smart Card )生成证书，则创建企业 CA 是合理的选择。

另一方面，如果 CA 将用于向组织外部的用户或计算机颁发证书，则应使用独立 CA( Standalone CA )。

无论采用哪种方式，根 CA( Root CA )的证书都必须位于客户端计算机的受信任根证书颁发机构( Trusted Root Certification Authority )存储中。这确保客户端信任该 CA 颁发的所有证书。

要点与延伸

在本章中，你学习了数字证书( Digital Certificate )以及公钥基础结构( Public Key Infrastructure ,PKI)的组成部分。数字证书用途广泛，包括身份验证、加密、数字签名和代码签名。公钥包含在证书中，而公钥和私钥对用于非对称加密。例如，HTTPS 会话首先通过非对称加密来私下共享一个密钥，然后使用该密钥进行会话的对称加密。在使用证书之前，可能需要完成多项验证检查，以确保证书未过期、未被吊销或未被滥用。如果这些检查失败，用户可能会看到错误提示。你可以查看任何证书的属性，了解其包含的颁发者名称、被颁发者名称、有效期、序列号、公钥等信息。PKI 包含颁发、管理和使用证书所需的所有组件。证书颁发机构( Certification Authority ,CA)负责颁发证书。证书链中的第一个 CA 是根 CA。当根 CA 的证书被放置在受信任的根证书颁发机构( Trusted Root Certification Authority )存储区中时，由该 CA（或证书链中的任何 CA）颁发的所有证书将自动受信任。你可以在 Windows Server 2008 上安装 Active Directory 证书服务( Active Directory Certificate Services )来创建自己的 CA。企业 CA 需要 Active Directory 域服务( Active Directory Domain Services )，但无论是否使用 Active Directory 域服务，你都可以创建独立 CA。

附加练习

- 确定你的系统是否包含来自 Microsoft 的任何根证书。
- 确定你的系统是否包含来自 VeriSign 的任何根证书。
- 访问 **https://woodgrovebank.com**。确定证书是否存在错误。
