---
summary: Active Directory（第5版·第3卷），涵盖组策略（GPO）核心功能与高级管理、细粒度密码策略（FGPP）规划实施、企业Active Directory森林与域结构设计、物理站点拓扑构建以及组策略部署规划。
---

# Active Directory, 5th Edition（第3卷：组策略与目录设计）

## 第11章 组策略( Group Policy )入门

组策略( Group Policy )是一个庞大的主题，本身就需要一整本书(而且确实已有好几本)才能充分讲解。本书将讨论组策略在 Active Directory 安装的设计和管理中的具体应用，但不会讨论其在工作站上的实际设置和操作。

基于策略的管理目标是：管理员只需通过定义策略一次性为用户和计算机定义环境，然后依靠系统强制执行这些策略。本章介绍组策略及其管理方法。第15章介绍如何开始设计组策略以及支持组策略的 OU 结构。

Active Directory 组策略的范围和功能涵盖若干关键点：

- 它们可以针对单个计算机和用户、站点( Site )、域( Domain )以及组织单位( Organizational Unit ,OU )。
- 它们可以应用于用户、计算机，也可以应用于用户组或计算机组。
- 它们可以设置值，并在指定情形下自动撤销这些设置。
- 它们可以在用户登录和注销、计算机启动和关机时运行脚本。
- 它们能做的远不止锁定桌面。

借助组策略，管理员既能控制工作站和服务器的行为，也能在整个组织中管理最终用户体验。实际上，有数以万计的设置可供应用，用于控制从屏幕保护程序超时、桌面背景到工作站电源管理，以及其间几乎所有的内容。本章将探讨应用这些设置的机制，以及组策略在底层是如何工作的，但不会讨论可以应用的具体设置。

### 11.1. 组策略对象( Group Policy Object ,GPO )的功能

组策略管理控制台( Group Policy Management Console ,GPMC )是管理组策略对象( GPO )的最佳工具。除了 GPMC 之外,组策略管理编辑器( Group Policy Management Editor ,GPME ) MMC 管理单元用于编辑 GPO 中的实际设置。GPMC 提供了一个单一界面来管理 GPO 的所有方面,包括编辑(通过 GPME)、查看策略的结果集( Resultant Set of Policies ,RSoP )以及链接到域、站点和组织单位( Organizational Unit ,OU )。如果您仍在使用 Windows XP 或 Windows Server 2003 来管理组策略,则需要在计算机上下载并安装 GPMC。GPMC 安装程序可从 http://bit.ly/YFv199 获取。较新版本的 Windows 将 GPMC 作为可选功能包含在内,或者包含在远程服务器管理工具( Remote Server Administration Tools ,RSAT )下载中。如果您在 Windows 7 或 Windows Server 2008 R2 上使用 GPMC,则 http://support.microsoft.com/kb/2466373 上提供的修补程序可修正在某些情况下影响它的烦人问题。

GPO 支持四种不同的策略领域。这些领域是注册表设置、安全设置、组策略首选项( Group Policy Preferences )和软件安装。GPO 中的大多数注册表设置具有三种状态:已启用、已禁用和未配置。默认情况下,GPO 中的所有设置都是未配置的。任何未配置的设置都会在应用期间被忽略,因此仅当设置实际已配置时,GPO 才会生效。在某些情况下,该设置不需要其他参数,而在其他情况下,必须输入大量信息才能配置该设置;这完全取决于该设置本身的功能。

> **警告**：

启用和禁用大多数设置相当简单。但是,由于 Microsoft 为 GPO 的某些设置选择了名称,您实际上可以选择启用或禁用名称类似于“禁用访问此选项”的选项。默认情况下,此设置未使用,但您可以禁用禁用选项(即启用该选项)或启用禁用选项(即禁用该选项)。请务必小心,并确保在广泛部署 GPO 之前了解该设置的应用方式。

GPO 可以对 Active Directory 中的计算机和用户应用大量更改。这些更改在 GPME 中分组在“策略”和“首选项”标题下。这些标题有两组:一组位于“计算机配置”下,另一组位于“用户配置”下。这两个标题下的项目不同,因为应用于用户和计算机的设置不相同。

#### 组策略存储( Group Policy Storage )

组策略( Group Policy )以多个组件形式存储，这些组件共同在客户端和管理员端实现组策略功能。这些数据会根据组件和平台的不同，采用多种方法进行复制。在本节中，我们将讨论组策略的关键组件、可用的复制引擎以及如何使用它们。

##### ADM 或 ADMX 文件

管理模板( Administrative Templates )下的某些设置如果归入其他某个部分，可能看起来更合理。不过，管理模板部分包含的设置完全由系统卷( SYSVOL )中的管理模板( Administrative Template ,ADM)文件生成，因此将所有 ADM 数据放在一起更合理。ADM 文件包含每个设置可用的全部选项，以及在组策略管理编辑器( Group Policy Management Editor ,GPME)各个属性页中显示的说明。

通常，域的 SYSVOL 所占用的磁盘空间中，很大一部分来自 ADM 文件。ADM 文件不参与组策略的应用，而仅用于填充组策略对象( Group Policy Object ,GPO)编辑器和组策略管理控制台( Group Policy Management Console ,GPMC)报告。Windows Server 2008 及更高版本附带的组策略工具集支持一种新类型的 ADM 文件，其扩展名为 ADMX。ADMX 文件与 ADM 文件用途相同；但它们采用新的 XML 格式，旧版组策略工具无法解析。Microsoft 提供的每个 ADMX 文件都附带 Windows 支持的每种语言对应的 ADML 文件。不同语言的本地化字符串可存储在单独的 ADML 文件中，由随附的 ADMX 文件引用。因此，讲英语的用户可以看到英文的管理模板策略说明，而讲法语的用户查看同一个 GPO 时，会看到这些说明的法文版本。

> **注意**：

Microsoft 提供了一款名为 ADMX Migrator 的免费工具，可用于将自定义 ADM 文件转换为新的 ADMX 格式，也可用于以图形方式创建新的 ADMX 文件。你可以从 http://bit.ly/13tdQiR 获取该工具。

Windows Server 2008 及更高版本的组策略( Group Policy )工具还支持 ADMX 文件的中央存储( Central Store )概念。中央存储消除了在每个组策略中重复存储 ADM 文件的情况，改为每个域仅存储一次。这可以大大减少域的 SYSVOL 共享所需的磁盘空间量，并降低复制要求。你需要手动创建中央存储才能使用此功能。幸运的是，创建中央存储非常简单：

1. 在 SYSVOL 的 policies 子文件夹中创建一个名为 *PolicyDefinitions* 的文件夹。例如，如果你的域名为 *mycorp.com*，则应在 *\\mycorp.com\sysvol\mycorp.com\policies\* 下创建 *PolicyDefinitions*。

2. 将 *%SystemRoot%\PolicyDefinitions* 文件夹的内容复制到你在步骤 1 中创建的 *PolicyDefinitions* 文件夹中。你应从具有最新版 Windows 和最新附带 Service Pack 的计算机上获取 *PolicyDefinitions* 文件夹的内容。

   > **注意**：

   只应使用与 Windows 和 Windows Server 版本对应的组策略工具。例如，如果你使用的是 Windows Server 2012 组策略工具，请不要尝试使用 Windows Server 2008 组策略工具编辑策略。不同版本之间的 ADMX 文件格式存在不兼容性。

3. 重新启动所有已打开的组策略工具。组策略编辑器( Group Policy Editor )和组策略管理控制台( Group Policy Management Console ,GPMC )将自动开始使用中央存储。

请记住，Windows Vista SP1 和 Windows Server 2003 或更早版本的组策略工具集无法利用 ADMX 文件或中央存储，因此要使用中央存储，你必须迁移到使用较新工具编辑组策略。要利用中央存储，只需升级你的组策略管理工具( Group Policy management tools )。你的域控制器( Domain Controller ,DC )运行哪个 Windows 版本并不重要，但如果它们运行的是 Windows Server 2003，则不应再使用 Windows XP 和 Windows Server 2003 附带的组策略工具。

> **注意**：

设置好中央存储( Central Store )后，ADM 文件不会自动清理。你需要手动执行此操作。http://bit.ly/XDRTWl 上的博客文章提供了一个示例脚本，可帮助你清理旧的 ADM 文件。

##### 组策略对象( Group Policy Object ,GPO )如何存储在 Active Directory 中

GPO 本身存储在两个位置：组策略配置( Group Policy Configuration ,GPC )数据存储在 Active Directory 中，而某些关键的组策略模板( Group Policy Template ,GPT )数据则以文件和目录形式存储在系统卷( System Volume )中。之所以将它们分开，是因为如果系统要将 GPO 与目录树中的位置相关联，确实需要将 GPO 存储在 Active Directory 中；但你不希望将所有注册表更改、登录脚本等内容都存储在 Active Directory 本身中。这样做可能会大幅增加 DIT 文件的大小。

为此，每个 GPO 都由一个包含 GPC 数据的对象组成，而该对象本身链接到系统卷中的一个配套目录，该目录中可能存储有 GPT，也可能没有。GPT 数据本质上是一种文件夹结构，用于存储基于管理模板的策略、安全设置、可用于软件安装的应用程序以及脚本文件。GPT 数据存储在域控制器( Domain Controller ,DC )的系统卷( SYSVOL )中的 *policies* 子文件夹内。

> **注意**：

第三方开发者可以通过整合不在常规的组策略模板( Group Policy Template ,GPT)位置中的选项来扩展组策略对象( Group Policy Object ,GPO)。

GPO 对象本身作为 `groupPolicyContainer` 类的实例，保存在 Active Directory 中位于以下位置的单个容器内：`CN=Policies,CN=System,dc=mycorp,dc=com`。

通过称为链接( Linking )的过程，GPO 与树中要应用组策略( Group Policy )的位置相关联。换句话说，一个对象可以链接到树中的多个位置，这解释了一个 GPO 如何能够根据需要应用到任意数量的组织单位( Organizational Unit ,OU)、站点( Site )或域( Domain )。

让我们考虑 `groupPolicyContainer` 类对象本身。请查看图 11-1；我们使用 ADSI Edit 来显示策略容器( Policies Container )及其子项的视图。在这里您可以看到许多 `groupPolicyContainer` 对象，其 `cn` 字段显示为 GUID。这些对象的 `displayName` 属性包含 Active Directory 管理员在使用常规工具查看这些对象时会看到的名称。每个 GPO 还有一个 `gPCFileSysPath` 属性，其中包含系统卷( System Volume )中相应目录的完整路径。

如果您在默认安装中查看策略容器，您只会找到两个子项。这些子项对应于默认域策略( Default Domain Policy )和默认域控制器策略( Default Domain Controllers Policy )，这是系统在安装时自动创建的唯一 GPO。这些 GPO 在所有域中都有固定名称：

- *{31B2F340-016D-11D2-945F-00C04FB984F9}* 始终是默认域策略。
- *{6AC1786C-016F-11D2-945F-00C04fB984F9}* 始终是默认域控制器策略。




![GPOs in the Policies container](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663446.webp)


图 11-1. 策略容器中的 GPO

##### 组策略( Group Policy )复制

长期以来，SYSVOL 容器一直使用 NT 文件复制服务( NT File Replication Service ,NTFRS)进行复制，而该服务可以执行文件共享的多主复制。然而，NTFRS 向来不以灵活性见长，在某些情况下甚至也不以可靠性见长。因此，Windows Server 2008 引入了使用一种新的文件和文件夹复制技术（称为分布式文件系统复制( Distributed File System Replication ,DFS-R)）来复制 Sysvol 文件夹层次结构的功能。DFS-R 的功能得到了大幅增强，可靠性也高得多。只要条件允许，最好将 SYSVOL 复制迁移到该服务。有关 DFS-R 的详尽常见问题解答( FAQ )，请访问 http://bit.ly/11H9Czp。

从 Windows Server 2008 域功能级别( Domain Functional Level )开始构建的域会自动使用 DFS-R 来复制 Sysvol 容器，但在更低功能级别升级或构建的域将继续使用 NTFRS。为了将 Sysvol 迁移到 DFS-R 复制，相关域必须处于 Windows Server 2008 或更高域功能级别。要迁移到 DFS-R，可使用 *dfsrmig* 实用工具。

Microsoft 存储团队博客( Microsoft Storage Team Blog )有一个内容详尽的系列文章，介绍将 Sysvol 迁移到 DFS-R 复制的过程。因此，我们不再尝试复述该内容的细节，而是概述该过程，并直接引导你访问来源：http://bit.ly/13tg2qL。该系列后续每篇博客文章的链接都位于页面底部。概括而言，迁移过程分为四个阶段：

1. 迁移开始
2. Sysvol 已准备状态
3. Sysvol 已重定向状态
4. 已消除状态

在已准备状态中，会在 Active Directory 中创建新的 DFS-R 对象，每个域控制器( Domain Controller ,DC)都会创建一个新的 *Sysvol_DFSR* 文件夹，并将自身 SYSVOL 文件夹的内容复制到其中。随后，DFS-R 服务开始进行初始化。当所有域控制器都达到已准备状态后，即可继续执行步骤 3。

进入已重定向状态时，每个域控制器都会使用自进入已准备状态以来对活动 Sysvol 共享所做的任何更改来更新其 *Sysvol_DFSR* 文件夹。随后，域控制器会修改 Sysvol 共享，使 *Sysvol_DFSR* 文件夹作为 Sysvol 共享出去。当所有域控制器都达到已重定向状态后，即可继续执行步骤 4。

进入已消除状态后，用于复制 Sysvol 的 NTFRS 设置会被移除，旧的 *Sysvol* 文件夹也会从文件系统中删除。至此，将 Sysvol 迁移到 DFS-R 复制的工作即告完成。

> **注意**：

在第 4 步之前的任何时刻，你都可以回滚一步或一直回滚到第 1 步。然而，一旦进入已消除状态，就无法回滚到 NTFRS。

### 11.2. 组策略的工作原理

本章余下部分将深入探讨组策略对象，重点聚焦于两大方面：

- 组策略对象在活动目录中的运作机制
- 如何管理组策略对象

组策略的理解颇为直观，但其应用却可能相当复杂。每个组策略对象由两部分构成：一部分应用于计算机（如启动脚本或对注册表系统部分的修改），另一部分则应用于用户（如注销脚本或对注册表用户部分的修改）。您可以使用仅包含计算机策略、仅包含用户策略，或是两者兼有的组策略对象。

#### 组策略对象与活动目录

任何组策略对象最初都是在活动目录中作为独立对象创建的。随后，每个对象可以一次或多次链接到三种不同的位置：站点、域和组织单位。针对域和组织单位的组策略对象存储在其应用相关的域中，而创建针对站点的组策略对象时，默认情况下会将其存储在森林根域中；如有所需，管理员可对此进行更改。

> **警告**：

不能将组策略( Group Policy ,GPO)链接到容器( Container )。不过,存储在容器中的用户和计算机仍会应用链接到域( Domain )或其所在站点( Site )的策略。

在通常情况下,管理员习惯在组策略管理控制台( Group Policy Management Console ,GPMC)中浏览到某个站点、域或组织单位( Organizational Unit ,OU ),然后创建一个 GPO 并将其链接到该对象。此时,表面上看您似乎是在树中的该位置创建了 GPO,但实际情况并非如此:系统将 GPO 创建为 Policies 容器中的一个独立对象,随后立即将其链接到该容器。

要将 GPO 应用于一组用户或计算机,只需创建一个 GPO 并将其链接到站点、域或组织单位即可。之后,默认情况下,GPO 中的用户部分将应用于树中的所有用户,而计算机部分将应用于树中的所有计算机。

因此,如果我们创建一个策略并将其链接到某个域,则该域中的所有计算机和用户都会处理该策略。如果我们创建一个策略并将其链接到某个 OU,则该 OU 中的所有用户和计算机,以及该 OU 之下各 OU(依此类推直至树的更下层)中的所有用户和计算机,都会处理该策略。

要确定某个 GPO 上的链接,只需查看组策略管理控制台中该 GPO 属性的“作用域( Scope )”选项卡。图 11-2显示了在域中扫描 Desktop Policy 这一 GPO 已链接到的位置所得的结果。在本例中,Desktop Policy 仅链接到 Desktops OU。




![Identifying GPO links](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663447.webp)


图 11-2. 标识 GPO 链接

在此我们要重点说明三点:

- GPO 只能链接到站点、域和组织单位。
- 单个 GPO 可以链接到树中的多个位置。
- 默认情况下,GPO 会影响链接作用域内的所有用户和计算机。

这又引出了更多问题。如果多个策略应用于树中的不同位置,那么多个 GPO 能否应用于同一位置?如果可以,哪一个的优先级更高?您为什么会希望将一个 GPO 应用于树的不同部分?此外,如何才能阻止 GPO 应用于树中的所有用户和计算机?下面我们逐一探讨这些问题,以便更深入地理解策略。

#### 对多策略应用的优先级排序

假设我们为某站点内的所有用户创建并链接了一个组策略对象( Group Policy Object ,GPO )，以便运行一个登录脚本，该脚本加载该站点本地的 Intranet 主页。再假设我们创建并链接了一个域 GPO，用以设定域内每位用户的 *My Documents* 文件夹位置。最后，我们还有两个用户登录脚本，需要按照特定顺序为域内特定组织单位( Organizational Unit ,OU )运行。GPO 的应用遵循一个特定顺序，通常称为 *LSDOU*。首先应用本地策略，接着是站点策略，然后是域策略，最后按照 OU 层级的顺序应用 OU 策略。这一应用顺序在图 11-3中进行了说明。

![Order of policy application](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663448.webp)

图 11-3. 策略应用顺序

如果一个站点、域或组织单位链接了多个 GPO，管理员可以优先排序来自该层级的 GPO 的处理顺序。考虑到这一点，用户所在站点的 GPO 首先按优先级从低到高的顺序应用，其他站点对此无任何影响。随后，用户所在域的 GPO 也按优先级顺序应用。域树中父域应用的 GPO 对树下级域中的对象没有影响。域树对 GPO 的应用完全没有影响。

然而，OU 结构对 GPO 的处理有着显著的影响。GPO 链接沿 OU 树向下继承。因此，尽管子组织单位可以有其自己的 GPO 链接，它也会继承所有父级的 GPO 链接。一旦站点和域 GPO 处理完毕，这些组织单位 GPO 将根据 OU 层级顺序应用。

> **注意**：

存在一些例外情况。您可以阻止继承、强制覆盖，甚至可以在对象上定义 ACL。本节后续内容将逐一介绍这些主题。

例如，Paul Burke 的用户账户具有以下可分辨名称( Distinguished Name ,DN)(参见图 11-4):

```
cn=PaulBurke,ou=Databases,ou=Gurus,ou=Financial Sector,dc=mycorp,dc=com
```

当 Paul 登录其计算机时，首先应用站点( Site )GPO，然后应用 mycorp.com 域( Domain )GPO。接下来依次应用 Financial Sector 组织单位( Organizational Unit ,OU)上的 GPO、Gurus OU 上的 GPO，最后应用 Databases OU 上的 GPO。由此可见，OU 层次结构设计对 GPO 优先级有重大影响。

![Graphical representation of the location of the PaulBurke user](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663449.webp)

图 11-4. PaulBurke 用户位置的图形表示

请记住，GPO 既有计算机部分，也有用户部分。计算机启动时，会按优先级顺序应用包含计算机设置的站点 GPO。随后应用包含计算机设置的域 GPO，依此类推沿 OU 层次结构向下，直至应用计算机所在 OU 上的 GPO。启动过程中，将忽略这些 GPO 的用户部分。之后用户登录时，将按相同过程应用，此时应用的是用户设置。用户登录期间，计算机设置将被忽略。[2]

> **警告**：

有几项策略只能在链接到域的 GPO 上设置。这些策略是影响域用户账户设置的策略，例如 Kerberos、锁定、密码有效期和密码复杂性策略。无论您如何努力尝试，只有在此级别上的设置才能使您在 OU 级别拥有不同的密码和锁定策略。在 OU 级别使用任何锁定和密码策略设置，都只会影响应用该策略的计算机上的本地用户账户。

要将不同的密码或锁定策略应用到不同的用户集，请参阅第 12 章，我们在其中讨论细粒度密码策略。

#### 组织单位中的标准 GPO 继承规则

GPO 中任何未配置的设置都将被忽略，仅继承已配置的设置。存在三种可能的情形：

- 较高级别的 GPO 对某项设置具有值，而较低级别的 GPO 未设置该值。
- 链接至父级 OU 的 GPO 对某项设置具有值，而链接至子级 OU 的 GPO 对同一设置具有非冲突值。
- 链接至父级 OU 的 GPO 对某项设置具有值，而链接至子级 OU 的 GPO 对同一设置具有冲突值。

如果某个 GPO 针对父级组织单位配置了设置，而子级组织单位中相同的策略设置未被配置，则子级将继承父级的 GPO 设置。这是合理的。

如果某个 GPO 针对父级组织单位配置的设置与针对子级组织单位配置的 GPO 中的设置不冲突，则子级组织单位将继承父级 GPO 设置，同时也会应用其自身的 GPO。一个很好的例子是两个登录脚本；这两个脚本不会冲突，因此都会运行。

如果某个 GPO 针对父级组织单位配置的设置与另一个针对子级组织单位配置的 GPO 中的相同设置冲突，则子级组织单位不会从父级组织单位继承这些特定的 GPO 设置。子级策略中 GPO 的设置优先。

> **注意**：

虽然本节中我们仅提及父级组织单位，但父级也可以是站点、域或本地策略。

#### 在组织单位 GPO 中阻止继承和覆盖阻止

可以强制将链接至树中某个 OU 的 GPO 设置作为子级的最终设置应用。

阻止继承是一个相当简单的概念。如果阻止对特定组织单位的继承，则链接至树中上级父级组织单位的 GPO 不会应用于此特定组织单位或其子级中的对象。

> **警告**：

即便勾选了“阻止继承”，本地策略仍会被处理。

请回顾图 11-4。若我们决定在 Databases 组织单位( Organizational Unit ,OU)层面阻止继承，用户 *PaulBurke* 将仅接收直接定义于 Databases 组织单位上的组策略对象( Group Policy Object ,GPO)。若在 Gurus 组织单位层面阻止继承，*PaulBurke* 将接收 Databases 组织单位上的 GPO 以及从 Gurus 组织单位继承而来的 GPO。阻止继承的组织单位会阻断任何更高级别的 GPO 应用于以该被阻止的组织单位为起点的分支。事实上，我们可以对 *mycorp.com* 域内任何组织单位阻止继承。例如，若想阻止域及站点级别的 GPO 应用，对 Financial Sector 组织单位阻止继承是合理的。

若不谨慎管理，此举可能引发问题。例如，假设您已将某组织单位分支的控制权委派给一组管理员，并允许他们操作该分支上的 GPO。您可能正将 GPO 应用于层级中更上层的组织单位，并希望此委派分支接收这些策略。然而，分支管理员有能力阻止继承您这些父组织单位的策略。他们亦能够配置与您在父 GPO 中设置的某项设置相冲突的设置；在冲突时，分支管理员的子级设置将优先。

您可以在组策略管理控制台( Group Policy Management Console ,GPMC)中右键单击域或组织单位，然后选择“阻止继承”来阻止继承，如图 11-5所示。




![Blocking inheritance with the GPMC](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663450.png.webp)


图 11-5. 使用 GPMC 阻止继承

为防止此情况，您可以在单个 GPO 链接上勾选“已强制”选项。这允许管理员强制 GPO 被组织单位的所有子级继承。然而，它还有进一步的效果：阻止子组织单位中的 GPO 设置覆盖父 OU 中的冲突设置。通过右键单击 GPMC 中的组策略链接并选择“已强制”，即可使用“已强制”选项，如图 11-6所示。

![Group policy link context menu](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663451.webp)


图 11-6. 组策略链接上下文菜单

> **注意**：

“强制”设置是基于每个组策略链接配置的。你无法将给定的组策略对象( Group Policy Object ,GPO )设置为在域范围内全局强制。

假设我们通过财务部门组织单位( Organizational Unit ,OU )上的一个组策略对象更改了注册表设置。不幸的是，另一位管理员随后在专家部门组织单位上将相同的注册表设置（以及许多其他设置）设置为冲突值，并且在数据库部门组织单位上阻止了继承。默认情况下，注册表设置只会正确地应用于财务部门组织单位，因为专家部门组织单位接收到不同的设置（由于继承规则，子级在冲突时覆盖父级），而数据库部门组织单位不会继承这两个策略。要解决这两个问题，我们可以将原始的财务部门组织单位组策略对象链接设置为“强制”。这将阻止专家部门组织单位上的组策略对象中的特定设置修改它，而不会影响任何其他组策略设置。我们的组策略对象也将被强制向下传递，越过在数据库部门组织单位上设置的“阻止继承”。

> **注意**：

如果您察觉到在谁有权修改给定策略方面存在

> **注意**：

如果需要在正常计划之外触发组策略刷新( Group Policy Refresh ),可以使用 Windows 附带的 *gpupdate* 工具。如果修改了任何只能在计算机启动或用户登录时应用的策略,*gpupdate* 会询问你是否要重启或注销。Windows 还包含一个名为 *gpresult* 的工具,用于显示已应用策略的详细信息。

Windows 8 客户端包含 Invoke-GPUpdate PowerShell cmdlet,其功能与 *gpupdate* 相同。

对于数天不关闭计算机或从不注销系统的用户,刷新非常有用。在这种情况下,组策略对象( Group Policy Object ,GPO )会以常规方式应用,但会在很长一段时间内以极不规律的间隔应用。设置策略刷新意味着你可以按自己决定的任何时间间隔将那些设置应用于此类用户。

##### 组策略刷新频率

默认情况下,Windows 工作站和成员服务器每 90 分钟刷新一次策略,域控制器( Domain Controller ,DC)则每 5 分钟刷新一次。为避免所有计算机同时从域控制器获取策略,每台计算机都会在刷新周期上叠加一个随机偏移间隔。默认情况下,工作站和成员服务器的该偏移间隔为最大 30 分钟的随机值,域控制器则为 0 分钟。刷新间隔与偏移间隔均可配置。要修改这些设置,既可以修改计算机的注册表,也可以编辑应用于该计算机的组策略对象( Group Policy Object ,GPO)。相关 GPO 设置位于“管理模板”下“系统”部分中的“组策略”节点。

计算机策略的注册表项位于 `HKLM\Software\Policies\Microsoft\Windows\System` 键下。具体值列于表 11-1。



表 11-1. 计算机组策略刷新注册表值

| 注册表值名称                     | 描述                                                         |
| -------------------------------- | ------------------------------------------------------------ |
| `GroupPolicyRefreshTime`         | *说明:*域成员的刷新间隔*数据类型:* `REG_DWORD`*有效范围:* 0 – 64,800 分钟 |
| `GroupPolicyRefreshTimeOffset`   | *说明:*域成员的偏移间隔*数据类型:* `REG_DWORD`*有效范围:* 0 – 1,440 分钟 |
| `GroupPolicyRefreshTimeDC`       | *说明:*域控制器的刷新间隔*数据类型:* `REG_DWORD`*有效范围:* 0 – 64,800 分钟 |
| `GroupPolicyRefreshTimeOffsetDC` | *说明:*域控制器的偏移间隔*数据类型:* `REG_DWORD`*有效范围:* 0 – 1,440 分钟 |

用户策略的注册表项位于 `HKCU\Software\Policies\Microsoft\Windows\System` 键下。具体值列于表 11-2。



表 11-2. 用户组策略刷新注册表值

| 注册表值名称                     | 说明                                                         |
| ------------------------------ | ------------------------------------------------------------ |
| `GroupPolicyRefreshTime`       | *说明:* 用户的刷新间隔*数据类型:* `REG_DWORD`*有效范围:* 0 – 64,800 分钟 |
| `GroupPolicyRefreshTimeOffset` | *说明:* 用户的偏移间隔*数据类型:* `REG_DWORD`*有效范围:* 0 – 1,440 分钟。 |

> **警告**：

尽管我们在此提供了组策略( Group Policy )将使用的注册表值,但我们不建议手动编辑这些注册表值。请始终使用组策略对象( Group Policy Object ,GPO)来配置这些设置。

#### 应对组策略导致的性能下降

将组策略( Group Policy )引入环境会在一定程度上影响计算机启动和用户登录时间。具体影响程度因环境而异，你需要在自己环境中进行测试，以得出具有代表性的数值。我们不建议为了加快启动和登录速度而放弃组策略，但确实建议在规划将应用于特定用户或计算机的策略数量时保持精简。在规划组策略部署时，可以从速度角度考虑以下几个事项。

##### 限制适用的组策略对象( Group Policy Object ,GPO )数量

Microsoft 对于为 GPO 设计 Active Directory 基础结构有自己的看法。建议组织单位( Organizational Unit ,OU )结构的深度不要超过 10 层，以免在登录期间应用策略耗费过多时间。请注意，问题不在于 OU 的数量，而在于链接到 OU 的策略数量。因此，如果有 5 个策略被链接，那么无论这些策略是链接在 3 层 OU 还是 10 层 OU 上，你看到的性能影响都相同。

##### 限制跨域链接

一个域的管理员可以创建 GPO，并将其应用到另一个域中的站点( Site )、域或组织单位。例如，如果 *child.mycorp.com* 的管理员有权访问 *mycorp.com* 中的集中设置 GPO，该管理员就可以将 *mycorp.com* 的 GPO 链接到 *child.mycorp.com* 域中的域或组织单位。

虽然这种设置可行，但通常不建议这样做。为了让 *child.mycorp.com* 域中的客户端应用来自 *mycorp.com* 的策略，它们必须联系 *mycorp.com* 中的域控制器( Domain Controller ,DC )，以便访问 *mycorp.com* 中的 Sysvol 共享。这会减慢登录和启动时间，尤其是在连接速度较慢时。与其在域之间链接策略，我们通常建议在每个域中物理复制这些策略。通过导入/导出来复制策略的方法将在本章后面讨论。

有关 GPO 和广域网( Wide Area Network ,WAN )链接的详细信息，请参阅即将出现的侧栏 GPO 如何在慢速链接上工作。

##### 限制站点策略( Site Policies )的使用

在多域环境中运行时，应用站点策略与跨域链接( Cross-Domain Linking )具有相同的限制。默认情况下，基于站点的策略( Site-Based Policies )存储在林根域( Forest Root Domain )的域控制器( Domain Controller ,DC)上。客户端要应用这些策略，必须联系根域中的域控制器以检索策略。

我们通常建议组织寻求基于站点的策略的替代方案。基于站点的策略往往会让管理员在管理和故障排除时感到困惑，因为管理员除了检查域和组织单位( Organizational Unit ,OU)之外，还必须记得检查站点以查找策略。此外，基于站点的策略通常需要遍历一条或多条广域网( Wide Area Network ,WAN)链路才能检索策略。

组策略对象( Group Policy Object ,GPO)如何跨慢速链路( Slow Link )工作

GPO 甚至用户配置文件( User Profile )仍然可以跨慢速链路工作，而且许多配置都交由管理员掌控。管理员可以指定慢速链路定义中使用的速度。对于计算机和用户，需要关注以下策略区域：

- 策略→计算机配置→管理模板→系统→组策略→组策略慢速链接检测
- 策略→用户配置→管理模板→系统→组策略→组策略慢速链接检测

在这两种情况下，默认设置为 500 KBps，但管理员可以设置任何自己希望的 KBps 连接速度值。该速度会与慢速链路检测算法进行比对；如果速度高于该值，则链路为快速链路；如果速度低于该值，则指示为慢速链路。

以下是 Windows Vista/Windows Server 2008 之前的伪代码算法：

```
Ping server with 0KB of data :
   Receive response#1 as a time in milliseconds (ms)
If response#1 < 10ms Then
   Exit as this is a fast link
Else
   Ping server with 2KB of data :
      Receive response#2 as a time in milliseconds
   Calculate Total-speed as response#2-response#1
End If
Ping server with 0KB of data :
   Receive response#1 as a time in milliseconds
If response#1 < 10ms Then
   Exit as this is a fast link
Else
   Ping server with 2KB of data :
      Receive response#2 as a time in milliseconds
   Calculate Total-speed as Total-speed + (response#2-response#1)
End If
Ping server with 0KB of data :
   Receive response#1 as a time in milliseconds
If response#1 < 10ms Then
   Exit as this is a fast link
Else
   Ping server with 2KB of data :
      Receive response#2 as a time in milliseconds
   Calculate Total-speed as Total-speed + (response#2-response#1)
End If
 'Average the total speed of (response#2-response#1)
Difference-in-milliseconds = Total-Speed/3
'If we know 2KB (16,384 bits) was moved in a certain number
'of milliseconds, then we need to calculate the number
'of bits moved per second (not per ms)
Bits-per-second-value = (16384 * 1000/Difference-in-milliseconds)
'Eight bits is a byte, so calculate bytes/second
bps-value = (Bits-per-second-value * 8)
'Calculate kilobytes/second to compare against GPO value
Kbps-value = bps-value / 1024
```

Windows Vista/Windows Server 2008 及更高版本的客户端依赖网络位置感知( Network Location Awareness ,NLA)服务来确定链路是否缓慢。

以下 GPO 会跨慢速链路应用：

- 当用户在登录屏幕上使用“使用拨号连接登录”复选框登录时，会应用用户策略。
- 当计算机是与远程访问服务器( Remote Access Server ,RAS)属于同一域的成员，或者位于与 RAS 服务器所在域有信任关系( Trust Relationship )的域中时，这两组策略都会应用。

GPO 不会应用于：

- 使用缓存凭据( Cached Credentials )完成登录时
- 对于属于不同域的计算机

在所有这些情况下，默认只应用安全设置( Security Settings )（即 IP 安全( IP Security )、加密文件系统( Encrypting File System ,EFS)恢复等）和管理模板( Administrative Template )设置；而文件夹重定向( Folder Redirection )、磁盘配额( Disk Quota )、脚本( Script )及软件安装策略( Software Installation Policy )不会应用。无法关闭必须应用的注册表设置( Registry Settings )。不过，可以使用这些组策略对象( Group Policy Object ,GPO)中的相关节，更改其他任何设置的默认状态，包括安全设置。

##### 在 WMI 筛选器中使用简单查询

如果某个组策略对象( Group Policy Object ,GPO)应用了 Windows Management Instrumentation (WMI)筛选器,则在将该 GPO 应用于用户或计算机之前,会先运行一条 WMI 查询。如果 WMI 查询非常复杂,可能会显著延长处理该 GPO 所需的时间。如果有多个 GPO 包含 WMI 筛选器,需要特别留意这些查询将产生的影响。如果正在使用 WMI 筛选器,不妨试试免费的 [WMI Filter Validation Utility](http://bit.ly/11HCSG1)。该实用工具可用于测试 WMI 筛选器,还能查看其应用所需的时间。

#### 安全筛选与组策略对象

由于每个组策略对象( Group Policy Object ,GPO )都是 Active Directory 中的对象,而所有对象都关联有访问控制列表( Access Control List ,ACL ),因此,借助该 ACL 来允许或拒绝访问某个 GPO 是可行的。通过 ACL,可以根据安全组成员身份来允许或拒绝应用 GPO。此外,还可以进一步细化粒度,为单台计算机或单个用户设置访问控制。图 11-7 显示,只有一台计算机 *XPCLNT01* 能够应用图中所示的策略。




![Security filtering with the GPMC](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663452.webp)


图 11-7. 使用组策略管理控制台( Group Policy Management Console ,GPMC )进行安全筛选

这是 GPO 的一项重要特性,你可以充分利用它来为己所用。让我们来看一个简单的示例:我们需要确保财务部门的用户应用更为严格的屏幕保护程序超时设置。财务部门的用户与公司其他所有员工一样,都位于 People OU 中。为了确保屏幕保护程序超时策略仅应用于财务部门的用户,我们需要执行以下步骤:

1. 创建一个屏幕保护程序超时 GPO。
2. 配置“屏幕保护程序超时”设置(`User Configuration\Policies\Administrative Templates\Control Panel\Personalization`)。
3. 从该 GPO 的安全筛选器中移除 Authenticated Users,并添加 Finance Users 组。
4. 将该 GPO 链接到 People OU。

完成这些操作后,只有 Finance Users 组的成员才能应用屏幕保护程序超时 GPO。People OU 中的所有其他用户都将忽略该策略。

#### 环回合并模式与环回替换模式

到目前为止,只有当用户位于组策略对象( Group Policy Object ,GPO)所链接的位置之下时,我们才能应用该 GPO 的用户配置( User Configuration )部分。但有时会出现这样的场景:您希望根据用户登录的计算机,而非用户在域的组织单位( Organizational Unit ,OU)结构中的位置,来应用用户配置策略。解决这一问题的组策略功能称为*环回模式*。

环回模式有两种非常常见的应用场景。第一种是自助服务终端机。如果贵公司在公共区域(例如大楼大堂)提供供员工使用的计算机,您可能只希望允许用户从自助服务终端机访问 Internet Explorer,并阻止访问其他程序。另一种场景是远程桌面服务器( Remote Desktop Server ,RDS)和 Citrix 部署。在这些情况下,您通常希望 RDS 服务器的用户在连接时获得受控的桌面环境,但不希望将这种级别的控制应用于用户自己的桌面计算机。

环回模式是一种必须启用的计算机策略。您可以在*计算机配置→策略→系统→组策略→用户组策略环回处理模式*下找到相关设置。如果打开该设置,将看到如图 11-8 所示的对话框,它允许您在两种环回操作模式之间切换:合并模式和替换模式。




![Setting loopback mode](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663453.webp)


图 11-8. 设置环回模式

此时,您可能想知道合并模式和替换模式之间的区别。在*合并模式*中,当用户登录到计算机时,其用户策略首先以正常方式应用,如图 11-3 所示。用户策略应用完毕后,将应用所有适用于该计算机的 GPO 的用户配置部分。任何冲突的设置(即在普通用户策略和应用于计算机的策略中都有定义的设置)将由应用于计算机的策略中的设置覆盖。相比之下,在*替换模式*中,通常在登录期间应用于用户的 GPO 会被忽略,取而代之的是应用所有适用于该计算机的 GPO 的用户配置部分。

当您计划利用环回模式时，务必记住环回模式是计算机的全局设置，而不是每个组策略对象( Group Policy Object ,GPO )的设置。这意味着，如果在应用于某台计算机的*任何* GPO 中启用了环回模式，那么将对该计算机上登录的所有用户启用环回处理，此外，应用于该计算机的所有 GPO 中的用户配置( User Configuration )设置都将被应用。

> **警告**：

认为环回模式( Loopback Mode )是基于每个组策略对象( Group Policy Object ,GPO)启用的，这是 Active Directory 管理员中常见的一种误解。在启用环回模式之前，请务必了解此行为！

#### 组策略应用总结

考虑图 11-9中的组织。该组织使用一个名为 *mycorp.com* 的域，跨越两个站点：Main-Site 和 Second-Site。营销部门的计算机位于 Main-Site，财务部门的计算机位于 Second-Site。策略 A 仅应用于 Main-Site，策略 B 应用于整个域，策略 C、D、E 和 F 按指示应用于相应的组织单位( Organizational Unit ，OU )。策略 G 应用于 Second-Site。




![Sample Group Policy implementation](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663454.webp)


图 11-9. 组策略实现示例

表 11-3总结了在启用和未启用环回模式( Loopback Mode )处理时策略的应用情况。未启用环回模式时，唯一的实际差异来自所应用的站点策略( A 或 G )。当为所有组策略对象( Group Policy Object ，GPO )启用合并模式( Merge Mode )时，结果会更加明显。在每种情况下，与用户相关的策略首先按顺序应用，随后是适用于计算机所在位置用户的全套策略项。以财务部门用户在主站点的营销计算机上登录为例：

1. 应用用户登录所在站点的站点策略( A )中与用户相关的部分。
2. 应用域策略( B )中与用户相关的部分。
3. 应用 Accounting 组织单位策略( E )中与用户相关的部分。
4. 应用 Finance 组织单位策略( F )中与用户相关的部分。
5. 再次应用站点策略( A )中与用户相关的部分。
6. 再次应用域策略( B )中与用户相关的部分。
7. 应用 Business 组织单位策略( C )中与用户相关的部分。
8. 最后，应用 Marketing 组织单位策略( D )中与用户相关的部分。



表 11-3. 可用环回模式的结果策略集

| 使用的环回模式 | 用户所在的组织单位( Organizational Unit ,OU) | 计算机所在的组织单位 | 策略的结果集 |
| -------------------- | ------------------------ | -------------------------- | ------------------------- |
| 否                   | Marketing                | `OU=Marketing` (主站点) | ABCD                      |
| 否                   | Finance                  | `OU=Finance` (第二站点) | GBEF                      |
| 否                   | Marketing                | `OU=Finance` (第二站点) | GBCD                      |
| 否                   | Finance                  | `OU=Marketing` (主站点) | ABEF                      |
| 合并                | Marketing                | `OU=Marketing` (主站点) | ABCDABCD                  |
| 合并                | Finance                  | `OU=Finance` (第二站点) | GBEFGBEF                  |
| 合并                | Marketing                | `OU=Finance` (第二站点) | GBCDGBEF                  |
| 合并                | Finance                  | `OU=Marketing` (主站点) | ABEFABCD                  |
| 替换                | Marketing                | `OU=Marketing` (主站点) | ABCD                      |
| 替换                | Finance                  | `OU=Finance` (第二站点) | GBEF                      |
| 替换                | Marketing                | `OU=Finance` (第二站点) | GBEF                      |
| 替换                | Finance                  | `OU=Marketing` (主站点) | ABCD                      |

请记住，后应用的策略可以覆盖先应用的策略，因此，如果存在冲突，应用于计算机所在位置的策略中的用户部分将始终覆盖先前的策略。对于策略顺序 ABEFABCD，D 可以覆盖 C，C 可以覆盖 B，B 可以覆盖 A，A 可以覆盖 F，依此类推。此外，在所有这些情况下，如果任何计算机组策略对象( Group Policy Object ,GPO)的用户部分未定义任何设置，则忽略这些策略。

当只设置应用于计算机的 GPO 的用户部分时，使用环回替换模式。对于在主站点登录到 Marketing 计算机的 Finance 用户，应用于该用户的唯一策略是 ABCD，即应用于该 Marketing 计算机的 GPO 的用户部分。

> **警告**：

管理员必须意识到，环回模式可能影响登录时间，特别是在使用环回模式的合并模式时。

#### WMI 筛选

Windows 管理接口筛选允许您将 WMI 查询与 GPO 关联，该查询将针对 GPO 应用到的每个用户和计算机运行。WMI 筛选器可以利用客户端计算机上可访问的任何基于 WMI 的信息，包括计算机硬件和配置、用户配置文件和环​​境设置。这为将 GPO 定位到具有特定属性的客户端提供了许多选项。

> **警告**：

WMI 筛选器仅在 Windows XP 及更高版本的操作系统上运行。如果带有 WMI 筛选器的策略应用于 Windows 2000 计算机，则 WMI 筛选器将被忽略。

例如，假设您希望当客户端通过虚拟专用网络 (VPN) 连接访问您的网络时应用某个 GPO。根据客户端运行的 VPN 软件，您的 WMI 查询可以检查进程或服务是否存在，甚至检查 IP 地址范围。如果查询返回 true，则将应用 GPO；如果返回 false，则不会应用。

#### 组策略( Group Policy )

关于组策略对象( Group Policy Object ,GPO)的信息已经很多了。我们来总结一下截至目前所介绍的 GPO 工作原理:

- GPO 处于拆分状态。GPO 的配置数据（简称 *GPC 数据*）保存在 AD 对象自身中。告知 GPO 其功能范围的模板文件和设置（简称 *GPT 数据*）则存储在 SYSVOL 中。
- 单个 GPO 可以根据需要链接到 Active Directory 中的多个站点、域和组织单位。
- GPO 可以包含同时适用于 OU 中计算机和用户的策略。GPO 对容器的默认操作是：在启动期间将 GPO 的计算机部分应用于该容器中的每台计算机，并在登录期间将 GPO 的用户部分应用于该容器中的每个用户。GPO 还可以设置为定期刷新。
- 链接到 Active Directory 中特定容器的多个 GPO 将按照一系列优先级严格排序应用。默认的优先顺序与 GPO 链接到容器的确切顺序一致。管理员可以根据需要调整优先级。
- 虽然 GPO 由于依赖 Active Directory 而仅存在于域环境中，但单个域计算机或工作组计算机可以为其定义本地策略。
- 默认情况下，GPO 沿组织单位层次结构向下继承。可以使用 OU、域或站点的属性来阻止此继承。管理员还可以将策略设置为*强制*。这允许策略覆盖所有较低级别的设置并绕过任何阻止。
- 环回模式允许管理员指定可以按计算机覆盖用户设置。实际上，这意味着通常仅适用于计算机的策略的用户部分也会应用于用户（合并模式），或者替代现有用户策略（替换模式）。
- WMI 筛选允许您配置 WMI 查询，该查询可用作确定是否应应用 GPO 的附加条件。如果筛选器评估为 true，则 GPO 将继续处理；如果评估为 false，则不会处理该 GPO。这是一个强大的功能，因为您有大量 WMI 数据可用于确定是否应应用 GPO。
- 许多因素可能会减慢客户端上的处理速度，包括尝试一个接一个地处理许多策略。使用环回模式（尤其是在合并模式下）可能会显著影响性能。尝试跨域应用 GPO 也可能导致速度下降，具体取决于域之间的网络速度。最后，WMI 筛选器中的复杂查询可能会对 GPO 处理产生负面影响。
- 策略按照称为 LSDOU 的严格顺序应用。此表示法表明先应用本地策略，然后依次是站点 GPO、域 GPO，最后是沿树层次向下应用任何组织单位 GPO。在每一位置，如果存在多个策略，则按优先顺序应用这些策略。
- 当要将策略应用到客户端时，系统会在实际按顺序应用策略之前先识别要应用的完整策略列表。这是为了确定是否已设置任何可能改变策略顺序或应用的阻止、覆盖或环回设置。
- ACL 可用于限制 GPO 仅应用于某些单个用户或计算机，或者用户组或计算机组。具体而言，在 GPO 上设置 ACL 以拒绝或允许访问，意味着您可以调整策略的影响范围，而不必采用将 GPO 应用于容器中所有用户或计算机的常规方法。
- 最后，用户配置文件和策略都可以跨慢速链接应用，但系统用于确定链接是否缓慢的速度可由管理员在单个 GPO 中配置。此外，虽然安全设置和管理模板通常默认应用，但检测到慢速链接时将应用的确切设置可由管理员配置。唯一的例外是管理模板将始终应用；管理员无法控制这一点。

### 11.3. 管理组策略

如前所述，使用组策略时，主要工具是组策略管理控制台( Group Policy Management Console ,GPMC)。GPMC 提供了一个界面，用于查看和编辑策略、了解策略在组织中的应用位置以及排查问题。您可以使用 GPMC 中的组策略建模( Group Policy Modeling )和组策略结果( Group Policy Results )功能来了解策略将如何应用于用户和计算机，并查看最终用户计算机上的实际结果。

#### 使用组策略管理控制台( Group Policy Management Console ,GPMC)

GPMC 是满足您所有组策略对象( Group Policy Object ,GPO )管理需求的一站式平台。您可以浏览林( Forest )并查看 GPO 的应用位置，可以创建和链接 GPO，还可以导入和导出、备份和还原、委派控制以及查看 RSoP 报告，所有这些操作都可以在 GPMC 中完成。

打开 GPMC 时，默认会显示您的用户帐户所在的域( Domain )。如果需要编辑另一个林中的 GPO，请右键单击树中的“组策略管理”节点，然后单击“添加林”。如果需要编辑林中另一个域中的 GPO，请右键单击“域”节点，然后单击“显示域”。

编辑 GPO 时，组策略工具默认会连接并使用主域控制器( Primary Domain Controller ,PDC )仿真器 FSMO 角色所有者。这可以确保不同计算机上的组策略管理编辑器( Group Policy Management Editor ,GPME )的多个副本都集中于同一个域控制器( Domain Controller ,DC )。如果 PDC 不可用，则可能覆盖此行为。如果发生这种情况，GPMC 将显示一个错误对话框，管理员可以选择另一个要使用的 DC。管理员还可以在 GPMC 中手动指定不同的域控制器。

如果在多个 DC 上编辑 GPO，可能会导致不一致，因为最后写入 GPO 的人获胜。因此，应避免在多个 DC 上编辑 GPO。

请回顾图 11-7，了解查看 GPO 时 GPMC 的外观。如左窗格所示，您可以浏览林中的各个域，直至特定的组织单位( Organizational Unit )。如果右键单击某个组织单位，您将看到许多与图 11-6所示的相同选项。

在图 11-7 中,Desktops 组织单位( Organizational Unit ,OU)已展开,表明 Desktop Policy GPO 已链接到该 OU(即带有快捷方式/箭头符号的图标)。一个虚拟的组策略对象( Group Policy Object ,GPO)容器已展开,其中列出了域中已创建的所有 GPO。此外还有一个虚拟的 WMI 筛选器( WMI Filter )容器,用于存放已创建的所有 WMI 筛选器对象。请注意,GPO、WMI 筛选器和入门 GPO( Starter GPO )容器都是虚拟的。所谓虚拟,是指组策略管理控制台( Group Policy Management Console ,GPMC)仅仅是将这些对象显示在专用容器中,以便 GPMC 更易用。实际上,这些对象并未存储在 Active Directory 的专用容器中。

> **注意**：

你还可以右键单击“站点”( Site )容器并选择“显示站点”，以浏览已链接到站点的组策略对象( Group Policy Object ,GPO)。你可以选择要显示哪些站点。

如果我们再次查看图 11-7，可以看到左窗格中选择了 Desktop Policy，右窗格中显示了若干选项和设置。以下列表汇总了每个选项卡上可用的内容：

- **作用域( Scope )**

  在“作用域”选项卡下，可以查看已链接到该 GPO 的域( Domain )、站点或组织单位( Organizational Unit ,OU )，并在需要时将其删除。还可以查看该 GPO 应用于哪些安全组( Security Group )，并在列表中添加或移除组。最后，可以设置应与该 GPO 关联的 WMI 筛选器。

- **详细信息( Details )**

  “详细信息”选项卡包含有关谁创建了该 GPO、其创建日期和上次修改日期，以及当前用户版本和计算机版本的信息。此选项卡上唯一可以设置的是“GPO 状态”( GPO Status )，用于定义是否启用用户设置和/或计算机设置。

- **设置( Settings )**

  “设置”选项卡提供了一种便捷方式，可用于查看 GPO 中已配置哪些设置。与在组策略管理编辑器( Group Policy Management Editor ,GPME )中必须逐层展开每个文件夹才能确定已配置哪些设置不同，你可以在组策略管理控制台( Group Policy Management Console ,GPMC )中查看 GPO 的“设置”选项卡，从而仅查看已设置的选项。

- **委派( Delegation )**

  “委派”选项卡类似于“控制委派向导”( Delegation of Control Wizard )，但它专门针对 GPO。本章稍后将更详细地介绍此界面。

#### 使用组策略管理编辑器( Group Policy Management Editor ,GPME)

虽然组策略管理控制台( Group Policy Management Console ,GPMC)用于创建和管理组策略对象( Group Policy Object ,GPO)的应用，但实际编辑 GPO 的内容需要另一款工具，即组策略管理编辑器(GPME)。对于任何 GPO，都可以在 GPMC 中右键单击并选择“编辑”来启动 GPME，如图 11-10所示。在 GPME 内部，设置分为计算机配置( Computer Configuration )和用户配置( User Configuration )，随后又分为策略( Policies )和首选项( Preferences )。如果你以前使用过组策略( Group Policy )，那么策略就是你熟悉的那些设置。首选项可能对你来说比较陌生——我们将在下一节介绍 Microsoft 于 2006 年收购的组策略首选项( Group Policy Preferences )功能。




![Group Policy Management Editor](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663455.png.webp)


图 11-10. 组策略管理编辑器

我们不会在 GPME 的“策略”部分花费太多时间，因为每个设置在配置方式上都略有不同，但你应该花些时间逐项单击浏览，以熟悉该界面。

你会发现，你可能想要应用的大部分策略都位于界面的“管理模板( Administrative Templates )”部分下。如果不确定在哪里找到所需内容，可以使用几个资源。首先，可以右键单击“管理模板”并选择“筛选选项( Filter Options )”。在此处，可以配置对所有可用设置的关键字搜索，还可以根据它们适用的 Windows 产品或版本进行筛选。在图 11-11中，我们要查找策略中已配置且包含“screensaver”一词的设置。搜索完成后，再次右键单击并清除“Filter On”复选框，或单击 GPME 工具栏中的筛选按钮以移除筛选器。




![Administrative Templates filtering options](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663456.png.webp)


图 11-11. 管理模板筛选选项

如果你只是为了配置某个特定设置或了解其作用而查找它，可能会发现 [http://gps.cloudapp.net](http://gps.cloudapp.net/) 上免费的基于 Web 的组策略搜索( Group Policy Search )工具很有用。此工具允许你进行筛选、执行更复杂的关键字搜索，并查看 ADMX 文件中的所有数据，这些数据也会显示在 GPME 中。

组策略管理编辑器( Group Policy Management Editor ,GPME )中一个相对较新的功能,是能够为管理模板设置附加注释,如图 11-12 所示。以往,你必须在单独的工具中记录自己的组策略选择(或者像许多公司那样,干脆不做任何记录)。有了注释功能,你的组策略就能实现自我说明。你可以为自己留下提醒,说明某项设置为何要如此配置,从而避免让未来的管理员只能靠猜测。

> **注意**：

还可以为单个组策略对象( Group Policy Object ,GPO)添加注释:在 GPME 中右键单击树顶部的组策略,单击“属性”,然后选择“注释”选项卡。




![Adding comments in the GPME](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663457.png.webp)


图 11-12. 在 GPME 中添加注释



#### 组策略首选项

2006 年,Microsoft 收购了 DesktopStandard 公司,并由此获得了一款名为 *PolicyMaker* 的产品。PolicyMaker 后来演变为组策略首选项( Group Policy Preferences ,GPP),并自 Windows Server 2008 起随 Windows 一同发布。借助组策略首选项,你可以通过图形化方式配置许多以往需要复杂的启动和登录脚本才能实现的桌面体验组件。组策略首选项的部分主要功能包括:

- 驱动器映射
- 快捷方式
- 打印机
- 注册表设置
- 电源管理



> **警告**：

组策略首选项提供的某些选项允许你存储用户名和密码(例如用于驱动器映射或计划任务)。这些密码并未以安全方式加密。Microsoft 组策略团队在其[博客](http://bit.ly/16fncfT)中对此进行了讨论。

可以在 GPME 的“首选项”节点下查看并探索组策略首选项支持配置的各种选项。Microsoft 还发布了一份关于组策略首选项的白皮书,可从 http://bit.ly/14lRcbp 下载。

> **注意**：

尽管组策略首选项( Group Policy Preferences ,GPP)最初随 Windows Server 2008 提供，但它并不依赖于您所使用的 Active Directory 版本。只要使用 Windows Server 2008 或更高版本中的组策略( Group Policy )工具，就可以利用组策略首选项。

组策略首选项在应用方式上与普通组策略略有不同。具体来说，这些设置仅在启动和登录期间应用。组策略对象( Group Policy Object ,GPO)的后台刷新不会应用首选项设置。因此，首选项设置不会像普通策略那样被强制执行。用户通常可以绕过或撤销由组策略首选项所做的更改。

对于大多数组策略设置，当从策略中移除某项设置，或将某台计算机从策略作用域中移除时，这些设置会被删除。而组策略首选项则不是这样。例如，如果通过组策略首选项映射驱动器，则需要创建一个首选项项目来取消映射该驱动器，而不是直接删除驱动器映射首选项。此行为由每个首选项项目属性中的“操作”( Action )选项控制，如图 11-13所示。




![Preference action options](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663458.webp)


图 11-13. 首选项操作选项

配置首选项项目的行为时，有四个选项：

- **创建( Create )**

  这将创建新条目。

- **替换( Replace )**

  这将删除客户端计算机上的任何相关设置，并用该首选项项目中配置的设置覆盖它们。对于映射驱动器，这将取消映射匹配的映射驱动器，然后重新映射它。

- **更新( Update )**

  这将使用首选项项目中配置的设置更新现有设置；如果客户端计算机上不存在该设置，则创建它。

- **删除( Delete )**

  这将从客户端计算机上删除匹配的设置。

> **注意**：

通常,如果要确保客户端计算机上的设置与首选项项目( Preference Item )中配置的内容完全一致,我们建议使用替换( Replace )选项。

##### 部署组策略首选项

在开始使用组策略首选项( Group Policy Preferences ,GPP )之前,可能需要向客户端工作站部署一个或多个更新。组策略首选项使用一个名为客户端扩展( Client-Side Extension ,CSE )的特殊组件来处理这些设置。某些版本的 Windows 已包含该客户端扩展,而另一些版本则没有。表 11-4列出了哪些版本的 Windows 需要安装客户端扩展。

> **警告**：

如果你当前正在使用 DesktopStandard ProfileMaker 产品，安装组策略首选项( Group Policy Preferences ,GPP)将卸载 ProfileMaker

##### 项级目标

组策略首选项( Group Policy Preferences )的一个非常强大的功能称为*项级目标*( Item-Level Targeting ,ILT )。ILT 允许您基于细粒度表达式，根据策略所应用于的用户和计算机的数十种属性，按项控制设置的应用。通常，要筛选哪些设置应用于不同的用户或计算机集，您需要创建单独的 GPO，然后应用安全筛选( Security Filtering )或 WMI 筛选器( WMI Filter )。使用 ILT，您可以筛选 GPO 内的单个首选项。

要为某个首选项配置 ILT，请打开“属性”，然后选择“公共”选项卡。在“公共”选项卡上，勾选“项级目标”，如图 11-14所示，然后单击“目标”。




![Mapped drive preference settings](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663459.webp)


图 11-14. 映射驱动器首选项设置

图 11-15显示了 ILT 的示例用法。在此示例中，Executives 组中的用户，以及同时属于 Finance Department 和 Headquarters Employees 的用户将收到该首选项。其他用户则不会。




![Sample item-level targeting](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663460.webp)


图 11-15. 项级目标示例

#### 使用组策略运行脚本

自 Windows NT 以来，登录脚本( Logon Script )一直是 Windows 域中的一项功能。你仍可以在 Active Directory 中的用户账户属性上定义单个登录脚本，Windows 客户端将在登录时运行该脚本；不过，组策略( Group Policy )为登录脚本提供了更为丰富的体验。你可以在登录时运行多个脚本，此外还可以定义在注销、计算机启动和计算机关闭期间运行的脚本。虽然此功能通常统称为“脚本”，但你可以运行批处理文件、Visual Basic (VB) 脚本、可执行文件或 Windows PowerShell 脚本。



> **注意**：

若要在用户登录/注销或计算机启动/关闭时运行 PowerShell 脚本，客户端计算机必须运行 Windows 7/Windows Server 2008 R2 或更高版本。

你可以使用组策略管理编辑器( Group Policy Management Editor ,GPME )在组策略中指定一个或多个登录或注销脚本。登录和注销脚本设置位于 *用户配置\策略\Windows 设置\脚本(登录/注销)* 下。双击“登录”节点即可配置登录脚本。在“脚本”节点上，你可以指定除 Windows PowerShell 脚本之外的任何类型的脚本或可执行文件。PowerShell 脚本则在“PowerShell 脚本”节点上指定。配置 PowerShell 脚本与标准脚本的唯一区别在于，组策略允许你定义 PowerShell 脚本是在“脚本”选项卡上指定的脚本/项目之前还是之后运行。

> **注意**：

你可以在组策略管理编辑器（ Group Policy Management Editor ，GPME ）中，通过浏览到“计算机配置\策略\Windows 设置\脚本（启动/关机）”来找到启动和关机脚本。

图 11-16 展示了一个配置为在登录时运行的单一 VB 脚本。当你配置任何类型的脚本（登录/注销或启动/关机）时，你需要将文件（及其任何依赖项）存储在所有将要执行该脚本的用户或计算机都能访问的位置。一般来说，存储这些文件最简单的位置是 Sysvol 中的组策略模板（ Group Policy template ，GPT ）文件夹内。通过将文件放在 Sysvol 中，你可以确保域中的所有域控制器（ Domain Controller ，DC ）都能够将这些文件与其关联的组策略对象（ Group Policy Object ，GPO ）一起复制。




![Logon script configuration](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663461.webp)


图 11-16. 登录脚本配置

如果你点击 图 11-16 中的“显示文件”按钮，Windows 资源管理器将打开到你正在编辑的 GPO 和脚本类型所对应的脚本文件夹。你可以使用这个便捷的快捷方式将文件拖放到 Sysvol 中的 GPT 位置。

在采用了组策略的组织中，登录（和启动）脚本极为常见。这些脚本通常用于配置常见的用户体验设置，例如驱动器映射或打印机，或者用于更新域中计算机的配置。在登录或计算机启动时运行脚本的缺点在于，它们可能会导致明显的性能问题。

即使编写得最好的脚本也可能遇到脚本编写者未曾想到的场景，而当这种情况发生时，计算机性能可能会受到不利影响。出于这个原因，我们将脚本与组策略这一节放在了组策略首选项（ Group Policy Preferences ）这一节之后。根据我们的经验，管理员使用登录或启动脚本执行的绝大多数任务都可以通过组策略首选项来完成。鉴于此，我们建议尽可能使用组策略首选项，而非登录脚本和启动脚本。

#### 组策略建模( Group Policy Modeling )

组策略结果向导( Group Policy Results Wizard )可让你查看用户和/或计算机的有效设置，但它依赖于该用户之前已登录到相关计算机。组策略管理控制台( Group Policy Management Console ,GPMC )包含第二个向导，可用于为各种场景生成“假设分析”( what-if )报告。你可以指定要建模的特定用户和计算机，或指定组织单位( Organizational Unit ,OU )层次结构中的特定位置，如图 11-17所示。




![Group Policy Modeling Wizard](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663462.webp)


图 11-17. 组策略建模向导( Group Policy Modeling Wizard )

该向导允许你模拟慢速链接( Slow Link )、环回处理( Loopback Processing )或站点亲和性( Site Affinity )等条件，如图 11-18所示。如果例如你正在测试策略的安全筛选( Security Filtering )更改，还可以模拟用户或计算机的安全组成员身份( Security Group Membership )更改。图 11-19显示了 GPMC 创建的报告。“摘要”( Summary )和“设置”( Settings )选项卡与结果报告类似，而“查询”( Query )选项卡显示你在建模向导中指定的参数的摘要。




![Simulating network conditions and loopback processing](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663463.webp)


图 11-18. 模拟网络条件和环回处理




![The Group Policy modeling report](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663464.webp)


图 11-19. 组策略建模报告

与组策略结果报告类似，你可以重新运行和导出建模报告，还可以通过“高级视图”( Advanced View )右键单击选项查看策略的结果集( Resultant Set of Policy ,RSoP ) Microsoft 管理控制台( Microsoft Management Console ,MMC )。

#### 委派与更改控制

在规划组策略部署时，你必须确定一旦开始部署组策略对象( Group Policy Object ,GPO)，将如何对其实施严格控制。具体而言，你需要考虑由谁来管理 GPO，以及如何控制他们所能进行的大范围更改。

##### 更改控制流程的重要性

在组织中跟踪 GPO 的最佳方式是通过一系列更改控制流程。无论 GPO 管理员是否为域管理员，这些流程都很有效。用于组策略的更改控制系统的复杂性因组织而异。有些组织选择在配置管理数据库( Configuration Management Database ,CMDB)中管理其所有组策略；其他组织则实施更简单的系统，如 Word 文档或 Excel 电子表格。由于应用有问题的策略更改可能会导致服务中断，因此在将任何组策略更改应用到生产环境之前，务必先在实验室中测试这些更改。Microsoft 提供了一款名为高级组策略管理( Advanced Group Policy Management ,AGPM)的工具，它是 Microsoft 桌面优化包( Microsoft Desktop Optimization Pack ,MDOP)的组成部分，可帮助实施组策略管理权限和更改控制流程。

##### 设计 GPO 管理的委派

此处可以考虑三种类型的权限：

- 允许一组用户将策略链接到域或组织单位( Organizational Unit ,OU)分支(并管理阻止继承设置)的权限
- 允许一组用户创建 GPO 的权限
- 允许一组用户更改 GPO 本身的权限

链接委派可以轻松地通过控制委派向导( Delegation of Control Wizard )完成，你可以在 Active Directory MMC 中右键单击组织单位、域或站点，然后选择“委派控制”来访问该向导。你将需要使用“管理组策略链接”任务。在此，你实际上是在委派对对象的 `gPLink` 和 `gPOptions` 属性的读写访问权限。如果你有兴趣了解这些属性的工作原理，请在 Active Directory 环境中设置几个 GPO，并使用 ADSI Edit 检查你向其链接 GPO 的 OU 的属性。

> **注意**：

我们将在第 16 章中详细讨论委派控制向导( Delegation Control Wizard )。

默认情况下，创建 GPO 的权限仅限于后续侧边栏默认 GPO 权限中所指明的那些账户。不过，你可以将用户添加到组策略创建者所有者( Group Policy Creator Owners )安全组，该组的成员可以创建新的 GPO。



> **注意**：

有关修改默认 GPO 权限的信息，请参阅 Microsoft 知识库文章 321476，网址为 http://support.microsoft.com/kb/321476。

如果组策略创建者所有者( Group Policy Creator Owners )的成员创建了 GPO，该用户将被设置为该 GPO 的创建者所有者( Creator Owner )[3]，并可继续管理该 GPO。即使该用户被从所有授予 GPO 管理权限的组中移除，GPO 的创建者所有者仍可管理该 GPO。



> **注意**：

Active Directory 中的 GPC 数据（即实际的 Active Directory 对象本身）被配置为不继承其父容器的安全权限。

你可以通过将用户放入组策略创建者所有者( Group Policy Creator Owners )组，来委派新 GPO 创建者的编辑访问权限。如果你还想将编辑访问权限委派给更多用户，或委派给用户并非创建者所有者的 GPO，请使用 GPMC：

1. 导航到包含目标 GPO 的域下的*组策略对象*文件夹。

2. 单击要委派的 GPO，然后在右窗格中打开“委派”选项卡，如图 11-20所示。

   

   
![GPO delegation in the GPMC](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663465.webp)


   图 11-20. GPMC 中的 GPO 委派

3. 单击“添加”按钮，弹出对象选择器。

4. 选择你希望授予访问权限的用户或组。

5. 选择要授予的权限。你有三个选项：

   - 读取
   - 编辑设置
   - 编辑设置、删除、修改安全性

6. 最后，单击“确定”，委派即被应用。

> **警告**：

在结束之前，有一点需要警告：如果应用得当，组策略对象( Group Policy Object ,GPO)对于 Active Directory 环境和整个网络的正常运行至关重要。错误地将策略应用到域根可能会锁定管理员账户或禁止在域控制器( Domain Controller ,DC)上登录。这显然是最坏的情况，但确实发生过。更常见的错误包括：输入错误的注册表值，迫使用户使用无效的代理服务器，从而导致 Internet Explorer 无法工作；或者忘记添加安全筛选，在本应只应用于少数计算机时，却意外地将策略应用到了所有计算机(默认设置)。

这些更改可能会影响整个树中的所有用户或计算机，因此我们提醒您，应将 GPO 管理员限制在极少数选定人员内。如果允许非管理员创建、更改和删除 GPO，他们必须能够对自己的操作负责并承担责任。已经等同于管理员的用户将自动能够管理 GPO，并且应该已经承担相应责任。



默认 GPO 权限

任何用户、计算机或组都需要同时具有读取( Read )和应用组策略( Apply Group Policy )权限，才能应用策略。Active Directory 已为 GPO 预置了某些权限。这些权限包括：

- 经过身份验证的用户( Authenticated Users )组具有读取和应用组策略权限。
- 创建者所有者( Creator Owner )具有完全控制( Full Control )权限，但没有显式的应用组策略权限。
- 本地系统( Local System )组具有完全控制权限，但没有显式的应用组策略权限。
- 域管理员( Domain Admins )组具有完全控制权限，但没有显式的应用组策略权限。
- 企业管理员( Enterprise Admins )组具有完全控制权限，但没有显式的应用组策略权限。
- 组策略创建者所有者( Group Policy Creator Owners )组具有完全控制权限，但没有显式的应用组策略权限。

后三个组中的管理员也属于经过身份验证的用户，因此他们从该组继承读取权限。如果不希望管理员的用户部分在登录时应用 GPO，请为域管理员、企业管理员，可能还有创建者所有者，将应用组策略权限设置为拒绝( Deny )。

#### 使用入门 GPO( Starter GPO )

自 Windows Server 2008 工具集起,组策略( Group Policy )引入了一项新功能:*入门 GPO*。借助入门 GPO,您可以定义一个模板 GPO,随后在组策略管理控制台( Group Policy Management Console ,GPMC )中将其复制。入门 GPO 与普通组策略一同存储在 Sysvol 容器中并一同复制,存放位置是名为 *StarterGPOs* 的新文件夹。

首次访问 GPMC 中的"入门 GPO"节点时,系统会提示您在 Sysvol 中创建 *StarterGPOs* 文件夹。从 Windows Server 2008 R2 开始,系统会自动创建一系列只读入门 GPO。这些入门 GPO 包含实施 Microsoft 的 [Windows XP SP2](http://go.microsoft.com/fwlink/?LinkID=121854) 和 [Windows Vista](http://go.microsoft.com/fwlink/?LinkID=121852) 安全指南所需的设置。在本书编写时,尚无适用于 Windows 7 或 Windows 8 的同类入门 GPO。此外,其中还包含用于通过 Windows 防火墙启用组策略远程管理所需端口的只读入门 GPO。



> **注意**：

在自定义入门 GPO 中可定义的设置,仅限 GPO 的"管理模板"部分中的设置。

创建入门 GPO 与创建普通 GPO 几乎完全相同。只需在 GPMC 中右键单击"入门 GPO"虚拟容器,然后单击"新建"即可。

您可能已经注意到,"新建 GPO"对话框中多了一个用于选择入门 GPO 的选项,如图 11-21 所示。如果此时选择一个入门 GPO,该入门 GPO 中的设置将被导入到新建的 GPO 中,为您提供一个可用作起点的基线。




![New GPO with Starter GPO](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663466.webp)


图 11-21. 带入门 GPO 的新建 GPO

#### 组策略备份与还原

从域控制器( Domain Controller ,DC)的系统状态备份中还原 Sysvol 容器是一个复杂且颇为棘手的过程。幸运的是,随着组策略管理控制台( Group Policy Management Console ,GPMC)的推出,现在有了简便的图形界面和基于脚本的机制,可用于备份和还原部分或全部组策略。若要使用 GPMC 备份域中的所有组策略,请右键单击组策略对象( Group Policy Object ,GPO)虚拟容器,然后选择"全部备份"选项。系统将显示一个类似于图 11-22的对话框。您必须为 GPMC 提供一个空文件夹的路径,用于存放所有 GPO 的备份,并可选择添加一条备份注释。向导完成后,您可以将目标文件夹压缩打包,从而获得一个便携且易于使用的备份。




![Group Policy backup](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663467.webp)


图 11-22. 组策略备份

如果您想备份单个策略,只需在组策略对象容器下右键单击该策略,然后选择"备份"即可。GPMC 仅支持基于单个策略的还原操作。若要还原某个策略,请在组策略对象容器下右键单击该策略,然后选择"从备份还原"。向导将提示您输入备份的路径。您必须将向导指向备份的*父*文件夹。因此,如果您要从图 11-22中创建的备份进行还原,则应将还原向导指向 *C:\GPOBackup*。

如果您需要一次性还原备份中的所有 GPO,可以使用 *RestoreAllGPOs.wsf* 脚本,该脚本包含在本章编写组策略脚本一节所讨论的 GPMC 示例脚本中。同样,您可以使用 *BackupAllGPOs.wsf* 脚本备份域中的所有 GPO。此外,还有分别用于单个组策略备份和还原的脚本,名为 *BackupGPO.wsf* 和 *RestoreGPO.wsf*。除了这些脚本之外,您还可以利用 Windows Server 2008 R2 及更高版本中附带的 *Backup-GPO* 和 *Restore-GPO* cmdlet。

还可以使用组策略管理控制台( Group Policy Management Console ,GPMC)的备份与还原功能，在域之间复制组策略( Group Policy )，或者也可以在测试环境与生产环境之间复制。GPMC 包含一个迁移表编辑器( Migration Table Editor )工具，当您需要修改对源域中安全主体( security principal )的引用，使策略在目标域中仍能正常工作时，将会调用该工具。有关迁移组策略的详细信息，请参阅白皮书[使用 GPMC 跨域迁移 GPO](http://bit.ly/16VQHEG)。

#### 组策略脚本编写

一直以来，在 Active Directory 中高效管理组策略对象( Group Policy Object ,GPO)的障碍之一就是缺乏脚本支持。组策略管理控制台( Group Policy Management Console ,GPMC)通过基于 COM 的对象提供了大量脚本编写功能，这些对象可以从 VB 脚本、PowerShell 等中访问。Windows Server 2008 R2 引入了许多可用于组策略的 PowerShell cmdlet，而 Windows Server 2012 则进一步扩展了这一选择。

Microsoft 在其[网站](http://bit.ly/10fQxCT)上免费分发了许多(超过 30 个)用于操作 GPMC 的实用示例脚本。下载并运行安装程序后，这些脚本将存储在 *%ProgramFiles%\Microsoft Group Policy\GPMC Sample Scripts* 中。

以下是可以通过 GPMC 对象使用脚本执行的部分任务列表：

- 创建具有默认设置的 GPO。
- 复制 GPO。
- 导入 GPO 设置。
- 设置 GPO 权限。
- 删除 GPO。
- 搜索 GPO。
- 列出 GPO。
- 检索 GPO 信息。
- 备份 GPO。
- 还原 GPO。
- 为 GPO 生成 RSoP 报告。

Windows Server 2008 R2 和 Windows Server 2012 附带的 PowerShell cmdlet 使您能够通过脚本创建和管理 GPO，以及报告和编写通过管理模板设置的设置。您无法编写通过客户端扩展设置的设置，例如 Windows 防火墙或受限组。表 11-5 列出了用于组策略的 PowerShell cmdlet 及其用途。



表 11-5. 组策略 PowerShell cmdlet

| PowerShell cmdlet | 用途 |
| ---------------------------- | ------------------------------------------------------------ |
| *Backup-GPO* | 将组策略对象( Group Policy Object ,GPO)或域( Domain )中的所有 GPO 导出到本地文件系统。 |
| *Block-GPInheritance* | 将组织单位( Organizational Unit ,OU)配置为不继承组策略( Group Policy )设置。 |
| *Copy-GPO* | 使用新名称复制 GPO。此 cmdlet 还可用于跨域复制 GPO。 |
| *Get-GPInheritance* | 显示 OU 的组策略继承设置。 |
| *Get-GPO* | 显示有关组策略对象的信息。 |
| *Get-GPOReport* | 生成 HTML 或 XML 格式的报告，详细说明 GPO 的内容。 |
| *Get-GPPermission* | 列出 GPO 上访问控制列表( Access Control List ,ACL)中的权限条目。 |
| *Get-GPPermissions* | 列出 GPO 上指定的权限（例如，用于安全筛选或编辑委派）。 |
| *Get-GPPrefRegistryValue* | 显示 GPO 中指定的组策略首选项( Group Policy Preferences ,GPP)注册表设置。 |
| *Get-GPRegistryValue* | 显示基于注册表的组策略设置。实际上，这等同于 GPO 中管理模板( Administrative Templates )部分的所有设置。 |
| *Get-GPResultantSetOfPolicy* | 运行策略结果集( Resultant Set of Policy ,RSoP)，并显示用户和/或计算机的结果。 |
| *Get-GPStarterGPO* | 显示有关起始 GPO( Starter GPO )的信息。 |
| *Import-GPO* | 将一个或多个已导出的 GPO 从文件系统导入到现有 GPO 中。这些已导出的 GPO 可通过 *Backup-GPO* cmdlet 或组策略管理控制台( Group Policy Management Console ,GPMC)中相应的“备份”选项创建。 |
| *Invoke-GPUpdate* | 在本地计算机上或远程目标计算机上刷新组策略。 |
| *New-GPLink* | 将组策略链接到 OU、域或站点( Site )。 |
| *New-GPO* | 创建新 GPO。 |
| *New-GPStarterGPO* | 创建新的起始 GPO。 |
| *Remove-GPLink* | 从 OU、域或站点中删除组策略链接。 |
| *Remove-GPO* | 从 Active Directory 中删除 GPO。 |
| Remove-GPPrefRegistryValue | 从 GPO 中删除一个或多个组策略首选项注册表设置。 |
| *Remove-GPRegistryValue* | 从组策略中删除一个或多个注册表设置。实际上，这等同于 GPO 中管理模板部分中的任何设置。 |
| *Rename-GPO* | 在 Active Directory 中重命名 GPO。 |
| *Restore-GPO* | 还原使用 *Backup-GPO* 备份的一个或多个 GPO。 |
| *Set-GPInheritance* | 切换 OU 的组策略继承设置。 |
| *Set-GPLink* | 修改 OU、域或站点上组策略链接的链接顺序（优先级）、“强制”标志或链接状态（启用/禁用）。 |
| *Set-GPPermission* | 修改 GPO 上的权限（例如，用于安全筛选或编辑委派）。 |
| *Set-GPPermissions* | 修改 GPO 上指定的权限（例如，用于安全筛选或编辑委派）。 |
| *Set-GPPrefRegistryValue* | 修改 GPO 中的一个或多个组策略首选项注册表设置。 |
| *Set-GPRegistryValue* | 修改组策略中的一个或多个注册表设置。实际上，这等同于 GPO 中管理模板部分中的任何设置。 |

除 Windows 附带的 cmdlet 外，还有大量第三方组策略（ Group Policy ）管理扩展，能带来极大的价值。SDM Software 就是提供多种基于 PowerShell 的解决方案的公司之一，其网址为 [http://www.sdmsoftware.com](http://www.sdmsoftware.com/)。

### 11.4. 组策略故障排除

如果任何时候需要调试组策略,有多种可选方案。这里我们将介绍其中几种,包括策略结果集( Resultant Set of Policy ,RSoP )工具。此外,我们还将了解如何强制更新组策略,并探究各种可用的日志记录选项——具体取决于客户端计算机所运行的 Windows 版本。



#### 组策略基础结构状态

Windows Server 2012 的组策略管理控制台( Group Policy Management Console ,GPMC )新增了一项针对组策略的运行状况报告,重点关注 Active Directory 与 Sysvol 的复制状态。该运行状况报告会检查域中每个组策略的状态,确保策略及其关联元数据在域内所有域控制器( Domain Controller ,DC )上保持一致。为此,GPMC 会选出一个域控制器作为基准,然后将每个域控制器与该基准进行比对。

在 GPMC 中单击某个域,再打开"状态"选项卡,即可访问基础结构状态。图 11-23展示了一个运行状况良好的域的状态。




![Group policy infrastructure status](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663468.webp)


图 11-23. 组策略基础结构状态

#### 组策略结果向导( Group Policy Results Wizard )

组策略结果向导( Group Policy Results Wizard )是策略结果集( Resultant Set of Policy ,RSoP )工具的前端界面。RSoP 是一款非常强大的工具,可识别哪些组策略对象( Group Policy Object ,GPO )设置已应用于用户或计算机。在 RSoP 出现之前,管理员只能自行推测哪些 GPO 具有更高优先级,以及哪些设置实际应用到了用户和计算机上。RSoP 通过易于使用的向导界面,消除了大量猜测工作。

Windows Server 2012 增强了 RSoP 报告功能,新增了若干数据点,包括策略中每个客户端扩展( Client-Side Extension ,CSE )的处理时间、每项设置来自哪个策略、环回处理( Loopback Processing )和链接速度数据,以及继承阻止( Inheritance Blocking )是否为影响最终策略集的因素。

要启动组策略结果向导,请打开组策略管理控制台( Group Policy Management Console ,GPMC ),右键单击 *Group Policy Results* 文件夹,然后启动该向导。图 11-24 显示了初始界面,系统将提示您选择要在其上运行 RSoP 会话的目标计算机。




![Group Policy Results Wizard—target computer selection](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663469.webp)


图 11-24. 组策略结果向导——目标计算机选择

下一个界面如图 11-25所示,允许您选择性地指定要显示其策略设置的特定用户。如果只需查看计算机设置,可以跳过此步骤。该向导仅显示过去曾成功登录目标计算机的用户。




![Group Policy Results Wizard—target user selection](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663470.webp)


图 11-25. 组策略结果向导——目标用户选择

完成向导后,GPMC 将生成一份类似于图 11-26所示的报告。该报告分为三个部分:

- **Summary** 选项卡提供影响策略应用的因素、已应用的筛选器等的总体概览。
- **Details** 选项卡允许您查看所有已应用的设置及其来源 GPO。
- **Policy Events** 选项卡提供与组策略处理相关的事件日志条目的统一视图。




![Group Policy Results report](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663471.webp)


图 11-26. 组策略结果报告

> **注意**：

如果你需要查看策略的结果集视图，而非图 11-26中展示的 HTML 报告样式，请右击报告并点击“高级视图”。

组策略结果工具的一个实用特性是报告会被保存，以便日后参考。你也可以在左侧树中右击报告，重新运行查询或导出报告。

你还可以从命令行运行 RSoP 会话；请参阅侧边栏使用 GPResult 工具。



使用 GPResult 工具

*gpresult* 工具可在任何系统上运行，用于将当前会话或目标机器和/或用户的组策略结果导出到文本文件。*gpresult* 自 Windows XP 起就已可用。

要导出当前会话的组策略设置，请使用以下命令：




```
 gpresult /v
```


如果要针对其他用户，请运行：




```
 gpresult /v /USER otherusername
```


要针对其他机器，请运行：




```
 gpresult /v /S othercomputer
```


你还可以组合这些开关，以针对其他用户和计算机。

从 Windows Vista/Windows Server 2008 开始，你可以使用 */H* 开关导出类似于 GPMC 控制台中 HTML 报告。*/X* 开关将以 XML 格式导出报告。你可以使用 XML 格式的报告，通过脚本自动化处理结果。

如需更多选项，请运行 `gpresult /?`。

#### 强制更新组策略( Group Policy )

有时在排查问题时，您可能不想等待策略在正常时间段内刷新。幸运的是，有一个名为 *gpupdate* 的命令行工具可用于强制更新。只需运行 `gpupdate` 即可更新组策略设置；不过，如果运行 `gpupdate /?`，还会看到其他可用选项的文档。Windows 8 和 Windows Server 2012 客户端还包含 *Invoke-GPUpdate* PowerShell cmdlet，其功能与 *gpupdate* 相同。

Windows Server 2012 附带的组策略管理控制台( Group Policy Management Console ,GPMC)（以及随附的 PowerShell cmdlet）引入了在一台或多台计算机上远程刷新组策略的功能。此功能的工作原理是：在目标计算机上远程创建计划任务，由该任务在本地刷新组策略。此功能可用于运行 Windows Vista 或更高版本的客户端，以及运行 Windows Server 2008 或更高版本的服务器。为了安排该任务，运行 GPMC 的计算机必须能够通过网络（例如穿过防火墙）访问目标计算机，以便向其发出远程过程调用( Remote Procedure Call ,RPC)。如果使用 Windows 防火墙，则需要提前部署“组策略远程更新防火墙端口 Starter GPO”，或者在各客户端上打开该 Starter GPO 中列出的端口和服务。

若要远程刷新特定组织单位( Organizational Unit ,OU)中所有计算机的组策略，可以在 GPMC 中右键单击该 OU，然后单击“组策略更新”。您将收到一个与 图 11-27 类似的确认提示，其中会告知有多少台计算机会受到此请求的影响。请求开始后，GPMC 将提供实时状态报告，如 图 11-28 所示。该状态报告确认组策略刷新已在远程计算机上计划，但并不确认刷新是否已成功。您可以单击“保存”按钮，将结果导出到 CSV 文件，以便使用脚本或 Microsoft Excel 进行处理。




![Remote group policy update confirmation](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663472.webp)


图 11-27. 远程组策略更新确认




![Remote group policy refresh status report](./image/11.%20Group%20Policy%20Primer/httpatomoreillycomsourceoreillyimages1663473.webp)


图 11-28. 远程组策略刷新状态报告

#### 启用额外日志记录

当组策略( Group Policy )正常工作时，它便成为管理员手中极为宝贵的工具。然而，与任何技术一样，有时为了排查组策略问题，您可能需要深入了解其背后的运行机制。幸运的是，组策略提供了大量的诊断日志记录功能，可在您需要解决问题时启用。日志记录的格式及启用方式会根据 Windows 版本的不同而有所差异。

##### Windows 2000、Windows XP 和 Windows Server 2003 中的组策略日志记录

只需设置一个注册表项，即可在事件日志中开启针对组策略相关事件的详细日志记录。一旦该注册表项存在且具有正确的值，日志记录便会自动进行；新值生效无需重启计算机。该值是一个`REG_DWORD`类型，名为`RunDiagnosticLoggingGroupPolicy`，需在`HKLM\Software\Microsoft\Windows NT\CurrentVersion\Diagnostics`项下创建并赋值为`1`。

将值设为`1`会将日志记录设置为详细模式；设为`0`等同于该注册表项不存在，即所谓的正常日志记录。换言之，仅当该值被设为`1`时，注册表项才会产生影响。事实上，操作就是这么简单。

> **注意**：

实际上，此注册表项是当前在此位置支持的四个项之一。您还可以创建以下项：

- `RunDiagnosticLoggingIntellimirror`
- `RunDiagnosticLoggingAppDeploy`
- `RunDiagnosticLoggingGlobal`

如果事件日志中的详细日志记录无法提供足够的信息，另一个选择是启用策略和配置文件处理的调试日志记录。为此，在`HKLM\Software\Microsoft\WindowsNT\CurrentVersion\Winlogon`项下创建一个名为`UserEnvDebugLevel`的`REG_DWORD`类型值，并赋予十六进制格式的值10002。重启计算机后，从此将在计算机上以*%SystemRoot%\Debug\UserMode\Userenv.log*文件记录大量日志信息。有关更多信息，请参阅微软知识库文章221833，网址为http://support.microsoft.com/kb/221833。

*UserEnv*调试日志文件内容极为密集，因此，如果您不习惯阅读此类日志，很可能需要搜索“error”等关键词。请注意，有些错误即使被标记为错误，也可能是正常的。完成排查后，请务必禁用`UserEnvDebugLevel`设置。

> **注意**：

关于组策略日志记录设置的详尽列表，请查阅可从http://bit.ly/Xa5Y30免费下载的ADM文件。

##### Windows Vista/Windows Server 2008及更新版本中的组策略日志记录

较新版本的Windows通过Windows事件跟踪( Event Tracing for Windows ,ETW )直接将组策略诊断信息发布到事件日志中。若要查看Windows Vista/Windows Server 2008或更新版本中的组策略跟踪信息，请启动事件查看器，浏览至*应用程序和服务日志\Microsoft\Windows\GroupPolicy*，并打开操作日志。你将发现大量与组策略实际处理过程及性能相关的信息。

若你正在排查组策略首选项的问题，则需要显式启用日志记录，然后解析生成的跟踪文件。微软有一篇关于启用组策略首选项日志记录的优秀文章，网址为http://bit.ly/Yd8eVH。

#### 组策略诊断最佳实践分析器

微软从其网站提供了一款名为组策略诊断BPA的免费工具。BPA代表*最佳实践分析器*( Best Practices Analyzer )，这是微软在过去几年中针对各种工具和产品发布的一类工具。组策略诊断BPA可以帮助进行故障排除。若要获取最适合你环境的工具版本，请访问http://support.microsoft.com/kb/940122。

#### 第三方故障排除工具

独立软件供应商SDM Software开发了一套组策略故障排除工具集，可以直观地报告客户端上的组策略处理健康状况，并直观地分析本章前面讨论的许多日志记录选项。有关更多信息，请访问http://www.sdmsoftware.com/products/freeware/。

[The GPO Guy](http://www.gpoguy.com/)社区网站也是获取组策略信息的绝佳资源。该网站提供免费工具，并托管了一个关于组策略主题的电子邮件讨论列表。

### 11.5. 小结

Active Directory 一直以来的重要卖点之一就是组策略( Group Policy )。本章详细介绍了组策略在 Active Directory 中的存储方式、客户端处理组策略对象( Group Policy Object ,GPO)的流程、GPO 的优先级顺序、继承机制的影响,以及访问控制列表( Access Control List ,ACL)在其中所起的作用。

可用于管理组策略的工具多种多样。其中最重要的或许当数组策略管理控制台( Group Policy Management Console ,GPMC),它可谓满足全部 GPO 管理需求的一站式工具。借助 GPMC,几乎所有必要的操作都能在单一界面中完成。GPMC 的另一大优势是它会安装若干 COM 对象,让你能够通过脚本实现许多 GPO 管理功能。

本章还介绍了一系列故障排查与诊断工具,用于在出现问题时查明究竟发生了什么。

------

[2] 这是默认情况。有一项设置可用于强制采用不同的操作模式。我们会在后面介绍回环模式( Loopback Mode )时对此加以说明。

[3] 当管理员创建 GPO 时,域管理员组( Domain Admins )会成为创建者所有者( Creator Owner )。

---

## 第 12 章 细粒度密码策略

毫无疑问，Windows Server 2008 Active Directory 中最令人兴奋的新功能之一就是引入了称为细粒度密码策略( Fine-Grained Password Policies ,FGPP )的功能。在 FGPP 出现之前，域帐户策略(具体而言，即密码和锁定策略)只能在每个域的基础上进行设置。如果您需要为不同的用户集设置不同的密码复杂性要求，则可以部署第三方密码筛选器，也可以部署其他域。细粒度密码策略在单个域内即可解决这两个问题，并且一旦您的域运行在 Windows Server 2008 或更高版本的域功能级别，这些策略即可立即使用。

### 12.1. 了解密码设置对象

在活动目录( Active Directory )中,您创建的精益密码策略由*密码设置对象*( Password Settings Objects ,PSO)表示。PSO 是标准的活动目录对象,存储在域分区( Domain Partition )下的 System 容器( System Container )中。

精益密码策略功能从 Windows Server 2008 开始提供,因此 Windows Server 2003 及更早版本的 Windows 域控制器( Domain Controller ,DC)无法实施此功能。一旦域运行在 Windows Server 2008 或更高的域功能级别( Domain Functional Level ),FGPP 即可用。虽然在域运行于该功能级别之前,您可以创建和管理 PSO,但这些策略不会对用户生效。

管理 PSO 的最简便方法是使用 Windows Server 8 活动目录管理中心( Active Directory Administrative Center ,ADAC)、Windows PowerShell 或命令行工具。我们将介绍如何使用 ADAC 以及一个名为 *PSOMgr* 的免费命令行工具来管理 PSO,该工具可在 http://www.joeware.net/freetools/tools/PSOMgr/ 获取。

> **注意**：

如果您不熟悉 ADAC,请参阅第 3 章。

### 12.2. 细粒度密码策略的应用场景

以往，几乎所有的密码策略设置只能在默认域策略中为整个域定义，而现在，这些设置都可以通过密码设置对象来配置。这一规则的例外是 Kerberos 设置，它们仍然必须通过组策略在每域的基础上进行定义。

> **注意**：

如果您的域中使用了一个或多个自定义密码筛选器，您可以在细粒度密码策略之外继续使用这些筛选器。

所讨论的每项设置都作为 `msds-PasswordSettings` 架构类的属性存储，该类是随 Windows Server 2008 架构扩展一同添加的。这些属性概述于表 12-1中。

表 12-1. 必需的密码设置对象属性

| 属性                                       | 描述                                                         |
| ------------------------------------------ | ------------------------------------------------------------ |
| `cn`                                       | 密码设置对象( Password Settings Object ,PSO)的名称           |
| `msDS-PasswordSettingsPrecedence`          | 当多个 PSO 应用于同一用户时，PSO 的优先级顺序                |
| `msDS-PasswordReversibleEncryptionEnabled` | 切换是否使用可逆加密存储密码                                 |
| `msDS-PasswordHistoryLength`               | 活动目录( Active Directory )中存储的历史密码数量            |
| `msDS-PasswordComplexityEnabled`           | 切换密码复杂性检查                                           |
| `msDS-MinimumPasswordLength`               | 密码的最小长度                                               |
| `msDS-MinimumPasswordAge`                  | 密码可以重置之前的最小时间间隔                               |
| `msDS-MaximumPasswordAge`                  | 密码必须重置之前的最大有效期                                 |
| `msDS-LockoutThreshold`                    | 触发锁定所需的失败登录尝试次数                               |
| `msDS-LockoutDuration`                     | 锁定账户的分钟数                                             |
| `msDS-LockoutObservationWindow`            | 维持锁定阈值的时间窗口                                       |

#### 定义密码设置对象

在定义使用密码设置对象( Password Settings Object ,PSO)的策略时,你需要确定实现该策略所需的独立 PSO 数量,以及每个 PSO 的相关值。给定用户的所有设置将来自单个 PSO,因为多个 PSO 的设置不会被合并。这可能意味着你需要在多个 PSO 之间复制某些通用设置。

一般来说,为了实现密码策略,你应尽量定义尽可能少的 PSO。PSO 会增加管理开销,因此每增加一个 PSO 都会为你的环境增添复杂性。我们将在本章后面深入讨论 PSO 的委派选项,但请记住,一般来说,运行该域的团队可能负责管理 PSO;然而,支持人员也需要了解它们,以便能够正确回答用户的问题,例如“我应该输入的密码规则是什么?”有些组织可能会选择将此责任改为委派给信息安全组。

> **注意**：

在开始制定细粒度密码策略( Fine-Grained Password Policy ,FGPP )部署计划时，请记住，作为一般最佳实践，应尽量将域中的密码设置对象( Password Settings Object ,PSO )数量限制为实际所需的最小数目。

##### 定义 PSO 优先级

PSO 与用户的关联方式有两种：直接关联，或通过组成员身份关联。每个 PSO 的 `msDS-PSOAppliesTo` 属性都是一个正向链接( forward link )，可链接到用户或全局组( Global Group )。由于 `msDS-PSOAppliesTo` 属性是多值的，因此单个 PSO 可以同时应用于多个用户或组。`msDS-PSOApplied` 属性是用户和组的反向链接属性( back-linked attribute )，用于定义哪些 PSO 链接到它。由于 `msDS-PSOApplied` 是反向链接( back link )，它也是多值的，因此必须有一种机制来确定哪个 PSO 实际应用于给定用户。

每个 PSO 还有一个 `msDS-PasswordSettingsPrecedence` 属性。这是一个整数属性，必须在每个 PSO 上定义，用于在多个 PSO 应用于给定组时控制该 PSO 的优先级。任何大于或等于 `1` 且小于或等于 `2,147,483,646` 的整数值均有效；建议为域中的每个 PSO 定义唯一的优先级值。发生冲突时，优先级值最低的 PSO 始终胜出。

每个用户对象都有一个名为 `msDS-ResultantPSO` 的附加构造属性。返回此属性时，将返回最终应用于该用户的 PSO。

> **注意**：

由于 `msDS-ResultantPSO` 是构造属性，因此无法在 LDAP 筛选器中直接查询它。如果尝试这样做，将收到一个错误，指出使用了错误的匹配运算符。

当多个 PSO 适用时，域控制器( Domain Controller ,DC )使用以下逻辑计算最终生效的 PSO：

1. 是否有 PSO 直接链接到该用户？这会覆盖链接到该用户所属组的任何 PSO。

2. 是否有 PSO 适用于该用户的任何全局安全组( Global Security Group )成员身份？如果是，则优先级最低的 PSO 胜出。

   > **注意**：

   如果在步骤 2 中发现多个具有相同优先级的 PSO 适用，则对象 GUID 数值最低的 PSO 在冲突中胜出。

3. 如果在步骤 1 和步骤 2 中未匹配到任何 PSO，则应用默认域策略( Default Domain Policy )的设置。

### 12.3. 创建密码设置对象

既然我们已经讨论了密码设置对象( Password Settings Object ,PSO)的基础知识,接下来就在域中预配一个 PSO,以便完整演示整个过程。

密码设置对象存储在域根目录下 System 容器中的 Password Settings 容器内,如图 12-1 所示。要查看 System 容器的内容,需要在活动目录用户和计算机( Active Directory Users and Computers )中选择"查看( View )"→"高级功能( Advanced Features )"。




![Viewing the password settings objects](./image/12.%20Fine-Grained%20Password%20Policies/httpatomoreillycomsourceoreillyimages1663474.webp)


图 12-1. 查看密码设置对象



#### PSO 快速入门

PSOMgr 的一个实用功能,是可以基于域密码策略的副本(通过组策略( Group Policy ,GPO )定义)以及一些常见的 PSO 模板,帮助你快速上手。为简便起见,本章大部分内容都将使用 PSOMgr 创建的常见 PSO 模板。要创建这些 PSO,需要运行以下命令:*PSOMgr -quickstart -forreal*。只要 PSOMgr 会对你的环境做出更改,就必须指定 *-forreal* 开关作为确认。如果省略该开关,PSOMgr 只会打印出在指定 *-forreal* 时将执行的更改。图 12-1 展示了运行 *-quickstart* 选项后的结果。

#### 从零开始构建密码设置对象( Password Settings Object ,PSO)

虽然 PSOMgr 生成的快速入门示例很棒，但您很可能需要定义一个或多个具有自定义设置的 PSO。本节将引导您使用图形用户界面( Graphical User Interface ,GUI)和 PSOMgr 创建在表12-2中定义的具有这些设置的 PSO。

表12-2. 自定义 PSO 设置

| 设置 | 值 |
| --- | --- |
| 名称 | Presidential Policy |
| 优先级 | 11 |
| 启用可逆加密 | 否 |
| 密码历史长度 | 10 个密码 |
| 启用密码复杂性 | 是 |
| 最小密码长度 | 8 个字符 |
| 最小密码使用期限 | 1 天 |
| 最大密码使用期限 | 90 天 |
| 账户锁定阈值 | 15 次登录失败 |
| 账户锁定窗口 | 30 分钟 |
| 账户锁定观察窗口 | 30 分钟 |

##### 使用活动目录管理中心( Active Directory Administrative Center ,ADAC)创建 PSO

为了使用 GUI 创建 PSO，我们需要使用 ADAC。创建 PSO 的功能是在 Windows Server 8 版本的 ADAC 中添加的。以前，要使用 GUI 创建 PSO，必须使用 ADSI Edit。

要开始创建表12-2中所述的 PSO，请启动 ADAC 并导航到 *系统→\密码设置容器*。接下来，右键单击并选择 新建→密码设置。按图12-2所示完成对话框，然后单击确定。




![Creating a new PSO with the Active Directory Administrative Center](./image/12.%20Fine-Grained%20Password%20Policies/httpatomoreillycomsourceoreillyimages1663475.webp)


图12-2. 使用 ADAC 创建新的 PSO

##### 使用 PSOMgr 创建密码设置对象( Password Settings Object ,PSO )

既然我们已经使用活动目录管理中心( Active Directory Administrative Center ,ADAC)创建了一个 PSO,接下来就逐步演示如何用 PSOMgr 创建 表 12-2 中指定的同一个 PSO。要向 PSOMgr 指定相同的数据,有多种不同的方式。其中某些方式的可读性强于其他方式,因此我们选择一种较为啰嗦的写法,而不是尽可能追求简洁。

你可以运行 *PSOMgr -help* 查看 PSOMgr 的完整用法说明,我们将要使用的开关及其参数如下:

- *-add <name>::<precedence>*
- *-lockout <threshold>:<duration>:<observation>*
- *-pwdage <max>:<min>*
- *-pwdlen <minlength>*
- *-pwdhist <historycount>*
- *-pwdcomplex (true|false)*
- *-pwdreverse (true|false)*
- *-forreal*

用于创建 表 12-2 中 PSO 的命令如下:


```
PSOMgr -add "Presidential Policy"::11 -lockout 15:30:30 -pwdage 90:1 -pwdlen 8 
-pwdcomplex true -pwdreverse false -pwdhist 10 -forreal
```


相应地,你会收到类似如下的输出:


```
PSOMgr V01.00.00cpp Joe Richards (joe@joeware.net) April 2007

WARN: Using name Presidential Policy for displayName.

Using host: Chicago\K8DEVDC01.k8dev01.brianlab.local
Retrieving PSOs...
Checking existing policies...

Creating new PSO: CN=CustomPSO1,CN=Password Settings Container,
CN=System,DC=k8dev01,DC=brianlab,DC=local
PSO successfully created.

    Type               : Policy Settings Object
    Domain             : k8dev01.brianlab.local
    Policy Precedence  : 11
    DN                 : CN=Presidential Policy,CN=Password Settings 
                         Container,CN=System,DC=k8dev01,DC=brianlab,DC=local
    Name               : CustomPSO1
    Canonical Name     :
    Display Name       : Presidential policy
    Lockout Threshold  : 15
    Lockout Duration   : 30
    Lockout Observation: 30
    Min Pwd Age        : 1
    Max Pwd Age        : 90
    Min Pwd Length     : 8
    Pwd History        : 10
    Pwd Complexity     : TRUE
    Pwd Reversible     : FALSE

The command completed successfully.
```

> **注意**：

如果使用 PSOMgr 创建密码设置对象( Password Settings Object ,PSO )时指定的优先级值已被占用,该操作仍会成功,但会在控制台输出类似以下内容的警告:


```
WARN: A policy setting object already exists with the same precedence.
WARN: Policy Setting object - DomPol_k8dev01.brianlab.local
WARN: (CN=DomPol_k8dev01.brianlab.local,CN=Password Settings Container,
       CN=System,DC=k8dev01,DC=brianlab,DC=local)
WARN: When a single user has two policies assigned with the same
WARN: precedence at the same scope (i.e. directly applied or
WARN: or applied via group), the policy with the lowest GUID will apply.
```


如果要使用 PSOMgr 编辑现有 PSO,可以用 *-mod* 开关替代 *-add*。其余开关的行为完全相同。

### 12.4. 管理密码设置对象

管理密码设置对象( Password Settings Object ,PSO)最简单的方法是使用 ADAC。ADAC 公开了用于控制密码和锁定策略以及将 PSO 应用于用户和组的所有选项。你还可以使用 ADAC 确定适用于特定用户的策略。如果你无法访问 ADAC,或者需要编写脚本执行管理任务,PSOMgr 是一个出色的命令行替代工具,我们也将对此进行探讨。

#### 控制密码设置对象( Password Settings Object ,PSO)应用的策略

有几种策略可用于管理哪些 PSO 应用于您的用户群体，您必须根据组织决定哪种策略最有效。第一种策略是为每个 PSO 定义一个全局安全组( Global Security Group )，并将该 PSO 应用于该组。反过来，您可以将用户（或嵌套其他全局组）放入该组。第二种策略是将 PSO 直接应用于用户或现有组，第三种策略是在必要时混合应用于组和用户。

##### 将 PSO 应用于组

将 PSO 主要应用于组可能是对许多组织而言最具可伸缩性的策略。这里的策略是：为每个 PSO 创建一个全局组( Global Group )，并将该 PSO 将应用于的用户放入此组。虽然您可以重用现有的全局安全组，但我们建议创建专用于 PSO 应用的新组。这可以确保不会因为将用户添加到控制 PSO 或资源访问的组中或从中删除用户而无意中影响用户。

请务必记住，只有全局安全组适合用于将 PSO 应用于用户。虽然您可以将 PSO 链接到通用组( Universal Group )或域本地组( Domain Local Group )，但在最终的 PSO 计算中，它实际上不会被视为应用于该用户。

如果由于用户是链接到不同 PSO 的多个组的成员，导致多个 PSO 应用于该用户，则优先级( Precedence )数值最低的 PSO 将胜出；如果有多个 PSO 的优先级数值相同，则全局唯一标识符( Globally Unique Identifier ,GUID )最小的 PSO 将胜出。

##### 将 PSO 应用于用户

如果您的组织规模较小，或者打算使用自动化工具管理 PSO 应用，则可能可以将 PSO 直接应用于用户。请注意，将 PSO 应用于用户的操作由有权修改 PSO 的人员控制，而不是由用户控制。与组相同的优先级规则也适用于链接到用户的 PSO。但是，即使可以使用优先级功能，也绝不应将 PSO 直接链接到用户。

##### 混合组应用和用户应用

对用户和组应用 PSO 采用混合方法可能在您的情况下是成功之道。请记住，如果某个用户既有通过组应用的 PSO，也有直接应用到其用户对象( User Object )的 PSO，则应用到用户对象的 PSO 将始终胜出。考虑到这一点，您可以定义规则的例外情况：用户的标准 PSO 通过组实现，而例外用户则直接链接到例外 PSO。

#### 管理密码设置对象( Password Settings Object ,PSO )的应用

可以使用 Active Directory 管理中心( Active Directory Administrative Center ,ADAC )、ADSI Edit、Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC )或 PSOMgr 来管理 PSO 的应用。通过编辑 `msDS-PSOAppliesTo` 属性即可控制 PSO 的应用。下面简要介绍如何使用上述每种工具将 PSO 链接到组。

##### 使用 ADAC 应用 PSO

ADAC 允许从多个位置应用 PSO，包括用户、组以及 PSO 本身的属性。我们将创建一个名为“Presidential Policy PSO Group”的全局组( Global Group )，并将之前创建的 PSO 应用到该组。要将 PSO 应用到组，请打开该组的属性，然后在左侧选择“Password Settings”。在“Directly Associated Password Settings”下，单击“Assign”，然后搜索 *Presidential Policy*。完成后，组属性应类似于图 12-3。也可以使用完全相同的步骤将 PSO 直接应用到用户。




![Assigning a PSO to a global group](./image/12.%20Fine-Grained%20Password%20Policies/httpatomoreillycomsourceoreillyimages1663476.webp)


图 12-3. 将 PSO 分配给全局组

若要从 PSO 的属性应用设置(或查看该 PSO 直接应用到的所有用户和组)，可以使用“Directly Applies To”部分，并将用户或全局组添加到列表中。



##### 使用 ADSI Edit 应用 PSO

在 ADSI Edit 中，通过浏览到默认命名上下文( Default Naming Context )→DC=domain,DC=com→CN=System→CN=Password Settings Container 下的相应位置(或环境中类似适用位置)，打开要应用的 PSO。如果在属性列表中看不到 `msDS-PSOAppliesTo`，请单击“Filter”，并取消选中“Show only attributes that have values”。

编辑 `msDS-PSOAppliesTo` 时，会出现类似图 12-4所示的对话框。该对话框从 Windows Server 2008/Windows Vista 的远程服务器管理工具( Remote Server Administration Tools ,RSAT )开始添加到 ADSI Edit 中，它允许你手动输入可分辨名称( Distinguished Name ,DN )(在早期版本中这是唯一选项)，或使用标准的 Active Directory 对象搜索对话框搜索用户或组。使用“Add Windows Account”按钮搜索 Active Directory。




![ADSI Edit linked value editor](./image/12.%20Fine-Grained%20Password%20Policies/httpatomoreillycomsourceoreillyimages1663477.webp)


图 12-4. ADSI Edit 链接值编辑器

单击“OK”并应用更改后，更改将立即生效(当然，需考虑复制( Replication )的影响)。

可以使用相同过程，选择用户或组，然后单击“Remove”，从而将用户或组从 PSO 的作用范围中移除。

##### 使用 ADUC 应用 PSO

自 Windows Server 2008/Windows Vista 的远程服务器管理工具( Remote Server Administration Tools ,RSAT )起，Microsoft 便在“Active Directory 用户和计算机”中加入了 ADSI Edit 属性编辑器属性页。要在 ADUC 中看到属性编辑器，请选中“查看”→“高级功能”。浏览到域下的 *System→\Password Settings Container* 后，即可打开 PSO 并以与 ADSI Edit 完全相同的方式对其进行编辑。

##### 使用 PSOMgr 应用 PSO

PSOMgr 具有灵活的语法，可用于应用和取消应用 PSO。你可以指定目标对象的用户名(`sAMAccountName`)、用户主体名称( User Principal Name ,UPN)或可分辨名称( Distinguished Name ,DN)。与前文示例相同，我们将把“Presidential Policy”PSO 应用到一个名为“Presidential Policy PSO Group”的组。为此需要使用的开关如下：

- `-applyto (<samname>|<upn>|<dn>)`
- `-pso <psoname>`
- `-forreal`

例如，在此场景中应用 PSO 的语法为 *psomgr -applyto “Presidential Policy PSO Group” -pso “Presidential Policy” -forreal*。运行此命令后，应得到类似如下的输出：

```
PSOMgr V01.00.00cpp Joe Richards (joe@joeware.net) April 2007

Using host: Chicago\K8DEVDC01.k8dev01.brianlab.local
Retrieving PSOs...
Applying PSO cn=Presidental Policy,cn=password settings container,cn=system,
            dc=k8dev01,dc=brianlab,dc=local to object CN=Presidential Policy 
            PSI Group,CN=Users,DC=k8dev01,DC=brianlab,DC=local
PSO successfully updated.

The command completed successfully.
```

如果要取消应用某个 PSO，语法几乎完全相同。只需将 *-applyto* 替换为 *-unapplyto*：

```
psomgr -unapplyto "Presidential Policy PSO Group" -pso "Presidential Policy"
       -forreal
```

##### 查看有效 PSO

查看特定用户的有效 PSO 最简单的方法是使用 ADAC 和 PSOMgr。由于 `msDS-ResultantPso` 属性是计算得出的，因此在用户所有属性的标准列表中不会显示。只有当在搜索中明确请求时，Active Directory 才会返回计算属性的值。此外，您无法构建基于构造属性值进行筛选的 LDAP 筛选器，因此无法搜索 Active Directory 以找出 `msDS-ResultantPso` 属性为某个特定 PSO 的所有用户。

要使用 ADAC 显示特定用户的有效 PSO，请找到该用户，然后右键单击并选择“查看生成的密码设置”。这将打开应用于该用户且有效的 PSO。如果某个 PSO 未应用于特定用户，您将收到类似于图 12-5的错误，表明默认域策略 GPO 中的密码和锁定策略设置对该用户生效。




![Error message when a user does not have an FGPP applied](./image/12.%20Fine-Grained%20Password%20Policies/httpatomoreillycomsourceoreillyimages1663478.webp)


图 12-5. 用户未应用 FGPP 时的错误消息

如果您无法访问 ADAC，或者需要通过脚本获取多个用户的结果 PSO，PSOMgr 将非常有用。幸运的是，使用 PSOMgr 查看结果 PSO 只需要一个开关：




```
-effective (samname|upn|dn)
```


例如，*psomgr -effective* *bdesmond* 是查看用户 *bdesmond* 的结果 PSO 的语法。运行此命令后，您应该会得到类似以下的输出：




```
PSOMgr V01.00.00cpp Joe Richards (joe@joeware.net) April 2007

Using host: Chicago\K8DEVDC01.k8dev01.brianlab.local

User: bdesmond | bdesmond@k8dev01.brianlab.local | CN=Brian
Desmond,CN=Users,DC=k8dev01,DC=brianlab,DC=local
Applied PSOs:
  CN=DomPol_k8dev01.brianlab.local,CN=Password Settings Container,CN=System,
  DC=k8dev01,DC=brianlab,DC=local
Effective PSO: CN=DomPol_k8dev01.brianlab.local,CN=Password Settings Container,
               CN=System,DC=k8dev01,DC=brianlab,DC=local
    Type               : Policy Settings Object
    Domain             : k8dev01.brianlab.local
    Policy Precedence  : 20
    DN                 : CN=DomPol_k8dev01.brianlab.local,CN=Password Settings
                         Container,CN=System,DC=k8dev01,DC=brianlab,DC=local
    Name               : DomPol_k8dev01.brianlab.local
    Canonical Name     : k8dev01.brianlab.local/System/Password Settings 
                         Container/DomPol_k8dev01.brianlab.local
    Display Name       : PSOMGR: Copy of Domain Policy for k8dev01.brianlab.local
    Lockout Threshold  : 0
    Lockout Duration   : 30
    Lockout Observation: 30
    Min Pwd Age        : 1
    Max Pwd Age        : 42
    Min Pwd Length     : 7
    Pwd History        : 24
    Pwd Complexity     : TRUE
    Pwd Reversible     : FALSE

The command completed successfully.
```


输出的第一部分显示了应用于给定用户的每个 PSO，第二部分显示了有效 PSO 的所有详细信息。您还可以通过访问 Active Directory 用户和计算机中用户属性的“属性编辑器”选项卡来查看结果 PSO。要访问“属性编辑器”，您必须确保勾选了“视图”→“高级功能”。此外，在“属性编辑器”选项卡上，您应该勾选“筛选器”→“构造”。这将在列表中显示 `msDS-ResultantPSO` 属性。

### 12.5. 委派 PSO 的管理权限

在规划细粒度密码策略实施时，您很可能需要做出的一项决定是：由谁管理密码设置对象（ Password Settings Object ，PSO）。根据组织情况的不同，这项职责很可能落到几个不同的团队或工具手中。一种可能是由 Active Directory 团队管理 PSO，那样的话本节内容就有些不相关了。另一种可能是 PSO 由信息安全团队控制。第三种可能是 PSO 由身份管理/配置系统间接管理。

如果由 Active Directory 团队端到端地拥有 PSO，那么您很可能无需执行任何安全权限委派即可完成 PSO 的管理。如果由信息安全组之类的独立团队控制 PSO，那么您需要委派必要的权限。在这种情况下，处理委派的方式通常有以下三种：

- **仅委派应用程序组的访问权限**

  在此场景中，您将严格采用基于安全组应用密码策略的设计，无任何例外。信息安全组将被委派这些组的访问权限，并负责管理组的成员身份。当认为有必要创建新的 PSO 时，该组需要联系 Active Directory 团队来创建。这种模式构建了一套制衡机制，确保 PSO 数量的增长得到有效管理。同时，这种模式也要求联系 Active Directory 团队来修改 PSO 上的设置。

- **委派修改 PSO 和应用程序组的访问权限**

  在这种情况下，您将委派修改现有 PSO 以及管理应用程序组成员身份的访问权限。信息安全组将能够修改 PSO 上的特定设置，并控制 PSO 的应用范围。如果您认为经常需要实现将 PSO 直接链接到用户的例外情况，这种模式将使其能够独立于 Active Directory 团队来完成。虽然 PSO 设置的变更很可能相当罕见，但这种模式也免去了为这些变更联系 Active Directory 团队的需要。创建新 PSO 的制衡机制在此仍然存在。

- **委派创建和修改 PSO 及应用程序组的访问权限**

这里我们将前一个模型再推进一步，把修改和新建密码设置对象( Password Settings Object ,PSO )的权限委派给信息安全团队。如果你需要频繁创建 PSO，这或许是最理想的途径。但请记住，这种做法去掉了其他方案中的相互制衡机制，因此 PSO 的数量可能会无限制地增长。

如果你打算使用身份管理系统( Identity Management System )或预配工具( Provisioning Tool )来管理 PSO，就需要向该工具运行所用的账户授予管理 PSO 应用程序所需的权限。这种委派可能涉及允许该工具直接编辑 `msDS-PSOAppliesTo` 属性，和/或允许该工具管理各 PSO 对应的应用程序组成员身份。

> **注意**：

有关实施 Active Directory 权限和委派的详细信息,请参阅第 16 章。

### 12.6. 小结

细粒度密码策略( Fine-Grained Password Policy ,FGPP)是一项重要且期盼已久的功能。FGPP 允许管理员定义密码设置对象( Password Settings Object ,PSO),并将不同的密码策略与账户锁定策略应用于域中的不同用户集合。PSO 既可应用于用户所属的全局安全组( Global Security Group ),也可直接应用于用户。

管理 PSO 可通过活动目录管理中心( Active Directory Administrative Center ,ADAC)、Windows PowerShell 或免费的 PSOMgr 命令行工具实现。PSOMgr 工具提供了诸多增强功能,凡是计划部署 FGPP 的管理员,都至少应当对其加以了解。

由于 PSO 在 Active Directory 中的实现方式,你需要结合本组织的实际情况,考虑这些 PSO 的管理与委派模型。将 PSO 应用于组,可为委派此项职责提供更大的灵活性。

---

## 第 13 章 设计活动目录( Active Directory ,AD)结构

本章重点在于规划 AD 安装的结构。具体来说，我们将探讨林( forest )和域树( domain tree )布局，以及组织单位( Organizational Unit ,OU)结构。当 Windows 2000 问世时，设计包含大量域的林极为常见（且往往很有必要），但这种需求在很大程度上已经消失。我们将探讨如何减少 AD 所需的域( domain )数量，同时利用组织单位获得对 AD 域命名空间( domain namespace )各部分的行政管理控制。本章旨在帮助你创建域命名空间设计。这包括你需要的所有域、林和域树层次结构，以及这些域中包含的组织单位，甚至用户、计算机和组等内容。

设计林时，请记住，对于任何给定公司，林设计通常有多种好答案。并不存在适用于所有情况的“最佳”设计。Microsoft 在可执行的操作方面提供了极大的灵活性，这反过来可能让你在如何实施 AD 上犹豫不决。两名工程师为同一家公司设计出两种截然不同、但都因完全不同原因而合理的方案，这并不罕见。只需记录所有推荐设计，并让决策者共同决定哪一种最适合长期运营。总体而言，最佳解决方案通常是最简单的解决方案。在大多数情况下，你会希望选择单林设计而非多林设计，选择单树设计而非多树设计，选择单域设计而非多域设计。此处展示的设计示例仅仅是一个示例。所讨论的公司本可以以多种方式设计其 AD 基础结构，而这只是其中一种。

在开始 AD 设计时，你必须了解若干限制。我们会在后续内容中结合上下文逐一介绍这些限制，但下面是一些重要限制：

- Active Directory 的安全边界是林，而不是域。在任何域中的任何可写域控制器( Domain Controller ,DC )上拥有高级别访问权限的任何人都可能影响或控制林中的任何其他 DC 或域。
- 删除林根域必然会导致整个林同时被破坏。林根域是整个林的基石。
- 单个 DC 无法承载多个域。设想某个位于美国的根域下有 3 个子域，每个子域分别对应 3 个业务部门之一。再设想在东欧或拉丁美洲有一个 15 人的小型办事处，与美国办事处之间的链路速度很慢。这 15 个用户分为 3 组，每组 5 人；每组 5 个用户分别属于 3 个业务部门/域之一。如果你认为站点间链路速度太慢，希望在该远程站点为这 3 个域安装本地域控制器，则需要安装并维护 3 个独立的域控制器，每个域一个。尽管这可以通过虚拟化实现，但仍然要额外管理、更新和监视 3 个域控制器。
- 组策略对象( Group Policy Object ,GPO )过多往往会导致登录时间变长，因为组策略会应用到站点、域和组织单位。这显然会影响组织单位( Organizational Unit ,OU )结构，因为一个 10 层深的 OU 树如果每个分支都应用 GPO，其 GPO 处理开销会大于一个 5 层深的 OU 树。但是，如果 10 层深和 5 层深的 OU 结构中都只有 2 个层级应用 GPO，那么两者的 GPO 处理开销相同。

### 13.1. 设计的复杂性

活动目录( Active Directory )是一项复杂的服务，为其进行设计并非易事。请查看图 13-1中描绘的名为 PetroCorp 的虚构全球公司。




![The sites and servers of a hypothetical company called PetroCorp](./image/13.%20Designing%20the%20Active%20Directory%20Structure/httpatomoreillycomsourceoreillyimages1663479.webp)


图 13-1. 名为 PetroCorp 的假设公司的站点和服务器

在这里，您可以看到一个庞大的站点网络，通过广域网( Wide Area Network ,WAN )中的各种网络连接相互链接。似乎存在多种域，如 *othercorp.com* 和 *petrocorp.com*，而每个方框代表单个域控制器( Domain Controller ,DC )，因此您可以看到某些服务器需要在那些 WAN 链接上复制数据。例如，*petrocorp.com* 似乎需要复制到所有主要站点，因为它在每个站点都有域控制器。

现在来看图 13-2，它展示了一个更为复杂的层次结构。




![A complex domain tree showing GPOs](./image/13.%20Designing%20the%20Active%20Directory%20Structure/httpatomoreillycomsourceoreillyimages1663480.webp)


图 13-2. 展示 GPO 的复杂域树

在此视图中，可以看到所有组织单位中的用户和计算机，且其结构似乎是为了让组策略对象( Group Policy Object ,GPO )（由梯形表示）能够应用于树的不同部分。以下讨论的原则和流程将帮助您创建类似这样的复杂设计，以映照您自己组织中的复杂性。

### 13.2. 从何处着手

在开始设计之前，你需要获取一些重要的信息。至少，你需要：

- 一份组织结构图的副本，因为这份文档实际上说明了贵组织的业务部门如何在层级结构中协同配合。
- 一份公司地理布局的副本。这既包括大洲和国家层面的宏观图景，也包括你设有业务部门的具体州、县或地区。
- 一份网络拓扑图的副本，标明各站点之间的连接速度。
- 一份需要与 Active Directory 对接的任何系统的图表和信息副本，例如现有的 X.500 和 LDAP 目录以及主要应用程序，以便将其纳入考量。

收集完这些信息后，你就可以着手规划设计了。

### 13.3. 设计过程概述

命名空间设计过程分两个阶段进行：

- **设计域命名空间**

  第一阶段处理命名空间设计本身。这意味着要计算所需的域数量，设计林( Forest )和树结构( Tree Structure )，并定义工作站、服务器以及整个网络的命名方案。

- **设计内部域结构**

  第二阶段需要关注此前记录的每个域的内部结构。你需要将业务模型作为内部结构的模板，然后进而考虑如何委派管理权限和其他权限。内部结构还可以根据你打算如何使用组策略对象( Group Policy Object ,GPO )进行修改；这将在第 15 章中介绍。

> **注意**：

设计完成后，你可以在实验室环境中搭建一个测试林( Test Forest )来实施设计。这将使你能够更好地感受设计的实际运行效果，以及是否有任何遗漏之处。测试环境的重要性无论如何强调都不为过。

在制定生产林( Production Forest )的预算时，也要将测试环境所需的时间、资金和资源纳入其中。这种前期投入无疑会持续为你避免大量后期错误和不确定性。

### 13.4 域命名空间设计

设计的第一阶段是规划网络的域、域树和林配置。最佳做法是先初步设计域，然后将它们组织成单个树或一系列树。不过，在开始之前，让我们先看一下本部分设计的目标。

#### 目标

域命名空间( Domain Namespace )的设计有两个目标：

- 设计 Active Directory，以体现业务结构
- 通过更充分地利用更灵活的组织单位( Organizational Unit ,OU )，尽可能减少域( Domain )的数量

##### 体现业务结构

设计 Active Directory 环境时，你应努力使其既与业务结构( Business Structure )相匹配，又能按 IT 组织( IT Organization )所采用的管理模型( Management Model )进行管理。通常，组织管理其 IT 基础架构( IT Infrastructure )时会采用以下三到四种常见模型之一：

- **集中管理( Centralized Administration )**

  在此模型中，整个 IT 基础架构由一个团队集中管理。

- **分散管理( Decentralized Administration )**

  在此模型中，IT 基础架构通常在每个位置本地管理，或按组织（可能按部门或分部）进行管理。在此模型中很难部署公共 Active Directory 林( Forest )，因为标准往往宽松甚至不存在，而且从基础架构（例如域控制器( Domain Controller ,DC)和林级配置）角度来看，Active Directory 并不特别适合由一个大型团队进行管理。

- **混合集中/分散管理( Hybrid Centralized/Decentralized Administration )**

  在大型组织中，这很可能是最常见的模型。Active Directory 的某些组件集中管理，例如域控制器和企业范围配置( Enterprise-wide Configuration )，而其他组件（例如存储在 OU 中的对象）则由分散的 IT 人员管理。

- **外包管理( Outsourced Administration )**

  在此模型中，第三方会在一定程度上代为管理你的 IT 组织。外包范围因组织而异，但架构和工程决策通常仍由本组织保留，不会交给外包商处理。

当 Active Directory 最初随 Windows 2000 面市时，常见做法是部署多个域( Domain )来模拟现有的 NT4 部署，或出于各种其他原因这样做；许多早期就部署了 Active Directory 的大型公司至今仍采用这种模型。早期最佳实践（例如空根域( Empty Root Domain )或区域域( Regional Domain )）本身并没有错，但如今普遍认为，应尽可能减少域的数量。话虽如此，我们绝不建议你匆忙合并早期创建的域，除非你能实现的成本或管理方面的节省超过此重构的成本。

为林( Forest )添加额外域( Domain )最常见的理由之一，纯粹是出于将管理分离的政治需求。实际上，林中任何域的管理员只要下定决心，无需太多功夫即可将其特权提升到企业管理员( Enterprise Admin )级别。在这种情况下，与其以相对较高的成本创建单独的域（几乎没有任何好处），不如使用组织单位( Organizational Unit ,OU)，并通过它委派必要权限( Permission )。

在完成本章流程时，请记住，尤其是在大型组织中，企业会频繁重组。请制订一种设计，使你认为它能够经受多次重组，而无需在更改 Active Directory 设计方面投入大量成本。我们的经验是，随着组织的发展，更多以地理、位置或支持模型为依据的设计往往表现更好。

#### 步骤 1：确定域( Domain )的数量

首先，假设所有对象( object )都将存储在一个域中。这样管理布局会简单得多。目前域的名称无关紧要；只需将其标记为组织( organization )的主域/唯一域。

现在，通过添加你能给出具体理由的其他域来扩展域的数量。尽管对象数量和管理委派( delegation of administration )并不是创建新域的好理由，但仍有一些理由需要更多域：

- 需要隔离复制( replication )
- 需要采用不同的 Kerberos 域策略( Kerberos Domain Policies )

如果你能满足上述任一标准，请为该区域写下新域。

> **警告**：

向设计中添加域( Domain )有充分理由，但不添加域也有充分理由。你应当将这些理由与前面列出的要求进行权衡，以确定哪些最为重要。

不部署额外域的一些原因包括：

- **林( Forest )复杂性**

  每个域都需要更多域控制器( Domain Controller ,DC)、更多策略管理以及额外成本。

- **应用程序复杂性**

  应用程序可能只能搜索单个域来获取信息。许多基于 Unix 和 Java 的 LDAP 应用程序通常编写为采用单个简单层次结构，并且如果不进行大量工作，可能无法配置为与多域林配合工作。



##### 隔离复制

尽管我们将在下一章更深入地讨论复制，但此时你应从宏观层面开始考虑它，因为它可能会对你最终确定的域设计产生重大影响。许多大型组织选择按照与广域网( Wide Area Network ,WAN )拓扑主要划分相匹配的区域方式来部署域。此类模型通常包含诸如 Americas、AsiaPacific、Europe 或 EMEA 之类的域（EMEA 是欧洲、中东和非洲( Europe, Middle East, and Africa )的常见缩写）。这样做的原因是在较高层面上对复制进行分段。例如，具有大型域的环境并不总能承受将 Americas 域中的所有内容复制到亚洲远程站点所带来的复制开销。

自 Windows 2000 以来，复制已大幅改进（尤其是在压缩方面），并且某些区域的 WAN 链路也变得更快。在探索设计选项时，你需要考虑大型域的复制开销是否可能影响你的 WAN，以及限制这种复制是否有益。请记住，即使按区域对域进行分段，仍然会有一些用于全局编录( Global Catalog ,GC )的区域间复制。

##### 唯一域策略

在第11章和第15章中，我们阐述了组策略的基础知识及其合理设计方法。当前，关键要理解的是，策略是活动目录中的对象，它们引用了一系列可应用于用户或计算机的设置。这些设置包括固定桌面、特定核心应用程序集、用户执行关机操作的能力等。如果你创建了一个名为Finance的组织单位，并决定它需要特殊设置，你可以创建一个组策略对象（GPO）并将其分配给该组织单位。随后，GPO中的计算机设置和用户设置将应用于Finance组织单位下的所有计算机和用户。

现在，我们需要关注哪些设置必须按域逐一应用。以下列出的是只能在整个域范围内设定的设置类型：

- Kerberos策略
- 加密文件系统（EFS）恢复策略
- 公钥加密策略

如果某个特殊部门或地理区域需要特殊的加密、安全防护、证书等，你可能需要为其设立一个独立的域。

> **注意**：

未运行在 Windows Server 2008 或更高功能级别的域，每个域只能有一个密码策略。有关细粒度密码策略的详细信息，请参阅第 12 章。

##### 最后说明

现在，你应该已经有了自己认为需要的域列表初稿。关于这个主题还有非常重要的一点。域非常不灵活且不容变通，而且由于一台域控制器( Domain Controller ,DC)上只能承载一个域，所以你每添加一个域，就意味着至少要多支持一台域控制器。



> **警告**：

为了实现容错，你始终应至少使用两台域控制器来部署新域。如果某个域只有一台域控制器，而该域控制器发生故障，你将被迫从备份进行还原。通过部署第二台域控制器，可以轻松避免这种情况。

根据你必须为一个域部署多少台域控制器，你可以通过限制所支持的域数量，大幅降低 Active Directory 的总拥有成本( Total Cost of Ownership ,TCO)。一般来说，除非有令人信服的技术理由不这样做，否则我们建议对任何新的 Active Directory 林都从单域设计开始。



#### 第 2 步：设计并命名树结构

现在你已经列出了各个域，接下来需要考虑将它们放入什么样的层次结构中。最简单的方法是先从一个域开始，也就是将成为林根域的那个域。

##### 选择林根域

选择林根域有两种方式。第一种模型是部署空根域。空根域仅包含少量域控制器，以及用于林内 Active Directory 管理员的账户。在已经部署 Active Directory 一段时间的大型环境中，空根域是你最可能看到的最常见模型。

> **注意**：

许多组织曾因安全方面的顾虑而部署空根域，但这些问题后来已被证明并不存在。虽然空根模型完全可行，但你不应仅仅为了保企业级组（如 Enterprise Admins 和 Schema Admins）而选择部署带有空根的林。

第二种模型是直接选择一个你确知在林生命周期内都需要的域作为林根域，该域永远无法删除。如果你要部署单域林，这个决定很简单。如果你要部署多个域，在设计层次结构时应牢记命名空间需求，使林根域确实位于树的根部。

如果你计划部署单域林——这也是我们通常推荐的模型——就没有理由仅仅因为空根是一种可选方案而去部署它。将你唯一的域设为林根域是完全可以接受的。

##### 设计命名空间命名方案

由于每个域都有一个域名系统( Domain Name System ,DNS)名称来标识自己，你需要考虑将选择什么名称。你可以使用任何 RFC 1123 标准字符：

- A–Z
- a–z
- 0–9
- \- (短横线字符)

Microsoft 的 DNS 服务器实现支持更广泛的字符，例如 Unicode 字符集，但如果你需要与其他 DNS 实现兼容，允许这些字符时要非常谨慎。

目前，在为 Active Directory 网络选择 DNS 名称方面有两种观点：*根区域( root zone )* 或 *子区域( subzone )*。根区域方法认为，应基于组织的根区域来命名根 Active Directory 域。对于 Coho Vines 林( forest )，这会是 *cohovines.com*。子区域方法建议，从根区域中选择一个新的子域( subdomain )，并将其作为 Active Directory 命名空间( namespace )的基础。对于 Coho Vines，可以是 *ad.cohovines.com*。

如果你选择根区域方法，并希望在根位置使用非 Windows DNS 服务器，则需要启用动态更新( dynamic updates )，或在 DNS 服务器中手动注册若干条记录，如第 8 章所述。如果你选择根区域方法，并希望在根位置使用 Windows DNS 服务器，则需要将现有条目（如果有）迁移到新的 DNS 服务器。两种方法都可以，但都需要在根位置进行配置或迁移。

侵入性更低的方案是，为 Active Directory 网络选择一个新的子区域，并基于该子区域运行网络。采用此设置时，你仍有两种选择，但它们对任何现有结构的干扰更小，也不会影响主根区域。可以说，最简单的解决方案是让网络中的两台服务器运行 Windows DNS Server，并管理此 DNS 区域。这样，你可以拥有一个不允许动态更新的根区域，以及一个允许动态更新的子域。在这种情况下，你现有的主根区域 DNS 服务器会包含针对该子区域的 DNS 委派( DNS delegation )。该子区域将委派给 Active Directory DNS 服务器。另一种方案则允许由非 Windows DNS 服务器管理该区域。

根区域方法的另一种常见扩展做法是，为 Active Directory 网络选择一个并行命名空间( parallel namespace )，例如 *cohovines.net,*。这样，你可以拥有根级命名空间，并且如果 *cohovines.com* 也是你的外部命名空间( external namespace )，则无需迁移现有 DNS 条目或管理拆分 DNS 模型( split-DNS model )。

要继续规划过程，请从林根( Forest Root )开始：在纸上画一个三角形，并为域分配一个DNS名称，将名称写在三角形内或旁边。你应该非常谨慎地选择名称，原因有两个。首先，虽然从Windows Server 2003 Active Directory开始可以重命名域，但这是一个极具侵入性的过程，除非绝对必要，否则通常不建议。其次，你永远无法从Active Directory中删除林根域。如果需要更改其名称，则必须破坏整个林并从头开始。

##### 创建其他树

创建并命名林根( Forest Root )后，需要考虑其他域( Domain )。如果存在两个不同的业务部门( Business Unit )或公司，有些分析师可能认为需要采用非连续名称来匹配该结构。这意味着需要从某个域根( Domain Root )派生两棵树( Tree )。请务必慎重权衡这一决策——林( Forest )中的多个域树( Domain Tree )会增加复杂性，并常常导致支持与应用程序方面的混乱，却没有实际收益。人们常用来表明其主观认为需要多棵树的示例包括：不同的电子邮件地址后缀、不同的用户主体名称( User Principal Name ,UPN )后缀、资源隔离和安全隔离。然而，实现上述任何需求实际上都不需要独立的树。

如果经过慎重考虑后仍认定需要多棵树，请在纸上将你认为需要的所有其他树根域( Tree Root Domain )绘制为位于同一水平线上的独立三角形，并为它们分配有效的域名系统( Domain Name System ,DNS )名称。这些域都是树根域，但不应与林根域( Forest Root Domain )混淆。

此场景的一个真实示例是 Microsoft 品牌名称和 MSN 品牌名称（Microsoft 拥有 MSN）。 *msn.com* 和 *microsoft.com* 都可以作为同一林中的独立树。如果不为它们建立层次链接（即 *msn.microsoft.com*），它们就无法位于同一棵树中。然而，在林中拥有 *msn.com* 和 *microsoft.com*，而不是 *msn.microsoft.com*，唯一真正的好处就是它们在 PowerPoint 演示文稿中的呈现效果。

> **注意**：

如果我们认为 Coho Vines 的财务部门需要一个单独的域( Domain )，我们会创建一个子域( Subdomain )，并将其命名为 *finance.cohovines.com*。在 Active Directory 中，我们完全可以让 *finance.cohovines.com* 本身成为一棵单独的树( Tree )，但由于整个林( Forest )中都存在分层且可传递的信任( Trust )关系，这样做根本不会带来任何好处。唯一的区别在于，是将 Finance 设为新域（我们就是这样做的），还是将其设为一个新林。把它设为一棵新树同样毫无益处。

##### 创建其他林

到目前为止,我们一直在考虑将存在于同一林( Forest )中的域( Domain ),但你可能有需要两个完全独立的林的业务部门。如何判断是否属于这种情况?对此有多种常见场景。

如果组织中的业务部门相互独立,并且实际上希望彼此隔离,那么就不得将它们合并到单个林中。如果只是为每个业务部门提供各自的域,这些业务部门可能会认为自己相互自治且相互隔离。然而,在 Active Directory 中,这种级别的隔离只能通过单独的林来实现。如果你需要满足法规或法律隔离要求,情况同样如此。

这种设计的第一个、也是最常见的原因可能是政治因素:某些业务部门可能决定要尽可能自治。可能出于政治原因,财务部门必须完全独立,因此最终会创建第二个林,并将 *finance.cohovines.com* 作为第二个林的林根域( Forest Root Domain )。实际上,你是将该业务部门视为目录树中一个独立、自治且非连续的部分。

你可能需要两个林的另一个原因涉及:出于法规或其他法律原因,必须分别维护两项业务。同样,如果你有一项业务未来可能被剥离或出售,那么该业务存在于自己的林中会使分离容易得多。

第三个原因源于必要性。请回想第 2 章中提到,命名空间( Namespace )的某些方面具有林范围的作用域。如果要隔离单独的架构( Schema )或配置分区( Configuration Partition ),唯一的解决方案就是创建单独的林。

第四个原因正变得越来越常见,即需要为 Microsoft Exchange 使用单独的林。Exchange 与 Active Directory 紧密集成,并且并不总是允许通过委派( Delegation )实现清晰的职责分离。此外,在单个林中进行多域部署( Multidomain Deployment )时,Exchange 可能面临管理挑战。这两个考虑因素通常会导致为 Exchange 实施单域资源林( Single-Domain Resource Forest ),并将信任( Trust )配置到主林( Primary Forest )中的相应域或主林本身。

最后，第五个原因是隔离特定用户、服务器或应用程序。在外围网络( Perimeter Network )中部署专用林( Dedicated Forest )，并将这些服务器加入主林( Primary Forest )中的某个域( Domain )，这种做法并不少见。从主域( Primary Domain )/主林到外围网络林的单向信任( One-Way Trust )使内部用户能够访问外围网络中的应用程序，但不允许外围网络中的服务器访问内部资源。此模型的一种常见扩展是，为需要访问某个应用程序的外部用户（如业务合作伙伴或客户）使用特定林。

如果这些原因中的任何一个适用，则需要创建第二个林根域( Forest Root Domain )，并为其指定唯一的 DNS 名称，就像为第一个林根域所做的那样。实际上，需要将设计分开，并分别设计每个林。现在最好确定需要多少个林，以及列表中的哪些域将成为林根域。确定之后，为这些根域命名，然后另用一张纸绘制每个林。为每个林维护单独的域列表。现在你正在创建 *x* 个设计，其中 *x* 是你拥有的林数量。

还有一点需要注意。虽然林中的域和域树( Domain Tree )会维护自动信任关系( Automatic Trust Relationship )，但可以与林外部的域建立手动信任关系( Manual Trust Relationship )。因此，可以在林之间建立手动信任关系。这些关系可以是单向信任（A 信任 B，但 B 不信任 A），也可以是双向信任( Two-Way Trust )（A 信任 B，且 B 信任 A）。

> **注意**：

尽管林( Forest )中的所有域( Domain )之间都存在可传递信任( Transitive Trust )，但在大型多域林中创建*快捷信任( Shortcut Trust )*并不少见。快捷信任可提升某些场景下的身份验证( Authentication )性能，这些场景要求一个子域( Child Domain )中的用户访问另一个子域中的资源。如果没有快捷信任，身份验证流量必须遍历域树( Domain Tree )才能到达另一个子域。快捷信任会创建一条直接路径。

第一个选项允许其他域对林中的某个域进行有限访问：这些域是不同林中另一域树的成员，或者不支持 Kerberos 身份验证。只有该域中的资源可见；该域树中的其他资源均不可访问。第二个选项是在两个林之间创建林信任( Forest Trust )。借助林信任，每个林中的所有域将相互建立可传递信任。

##### 排列子域层次结构

现在，你已有一个具有有效 DNS 名称的林根域( Forest Root Domain )。你可能还有其他域，它们充当同一林中独立域树的根；你甚至可能有代表完全独立林的其他林根域。现在，你需要规划域树层次结构。如果第 1 步的纸上还列出了多个剩余域，那么这些就是将要构成域树层次结构的子域。

从第一个林开始。在纸上用三角形表示每个域，将这些域按层次结构排列在林中的某个域树根之下。根据每个域在层次结构中的位置为其适当命名。对此林中的所有域重复此过程，然后转到下一个林(如有必要)并重复。

例如，如果我们以 *cohovines.com* 作为域树根，且北美、欧洲和亚太地区都需要单独的域，可以分别将其命名为 *northamerica.cohovines.com*、*europe.cohovines.com* 和 *asiapacific.cohovines.com*。如果亚太地区需要为日本单独设置一个域，我们会将此域排列在 *AsiaPacific* 之下，即 *japan.asiapacific.cohovines.com*。

### 13.5. 内部域结构的设计

设计好域命名空间后，现在可以专注于每个域的内部结构了。虽然每个域的设计过程相同，但顺序基本上由您决定。您应该设计的第一个域是林根域。之后，遍历该树，在第一个树中设计子域。完成该树后，再继续处理下一棵树，并像之前一样从根开始。

在设计域的内部结构时，您需要考虑组织单位( Organizational Unit ,OU)的层次结构，以及将驻留在这些组织单位中的用户、组、工作站和服务器。让我们依次查看每一项。



> **注意**：

今后，当我们提到层次结构、树或目录树时，指的是域内的组织单位层次结构。我们并非指林中的域树层次结构。

#### 步骤 3:设计组织单位( Organizational Unit ,OU)的层次结构

前面在讨论如何设计域( Domain )时,我们提到过如何尽量减少你拥有的域数。其思路是改用组织单位来表示你对分层管理权限集的需求。

OU 是组织数据的最佳方式,因为它们非常灵活。它们可以重命名,并可在域内轻松移动,还可置于层次结构中的任意位置,而不会影响其内容。这两个特点使管理员能够非常轻松地管理它们。

以有效的层次结构组织数据主要有四个原因:

- **反映业务模型以简化管理**

  将数据划分到一个你一眼就能识别的 OU 结构中,会使管理比将所有用户和计算机都放在一个 OU 中轻松得多。

- **委派管理**

  Active Directory 允许你设置分层管理。如果你有三个分支机构,并且主管理员希望让其中一个分支机构完全自治、拥有自己的管理员,同时又希望继续控制另外两个分支机构,那么这种设置很容易完成。在某种程度上,你在构建 Active Directory 结构时遇到的大多数限制,都是你自己设定的限制:政治需要、组织模型等。Active Directory 其实并不关心你如何组织数据。

- **将策略应用到用户和计算机的子集**

  由于组策略( Group Policy )可以应用到层次结构中的每个单独 OU,因此你可以根据计算机和用户在树中的位置,让不同的计算机和用户获得不同的策略。例如,假设你想在办公室大厅放置交互式展台计算机,并允许人们与你指定的任何应用程序交互,例如公司报告、建筑物地图等。使用 Active Directory 时,如果将组策略应用到某个 OU 层次结构,就可以保证你创建或移动到树中该部分的任何计算机账户和用户账户都将始终实施你设计的展台锁定策略。

创建组织单位时,需要问:

- 组织单位将如何使用?
- 管理员是谁,他们应拥有哪些管理员权限集?
- 将应用哪些组策略?

层次结构应以支持您的管理模型、有效利用组策略( Group Policy )，并允许您将管理权限委派给树的各个部分的方式组织信息。

> **警告**：

在设计组织单元( Organizational Unit ,OU )结构时，应避免将用户或计算机账户嵌套过深，以免应用于这些账户的组策略( Group Policy )在登录过程中造成延迟。微软建议嵌套层级不超过 10 层，但实际上，在设计 OU 结构时，更需要考虑的是组策略的应用行为。这有助于防止启动(启动时应用于计算机账户的策略)和登录(登录时应用于用户账户的策略)过程中的延迟。

过度嵌套 OU 结构还往往会因模型复杂性的增加而导致管理开销显著上升。

##### 重建业务模型

开始设计的最简单方法是考虑创建这些设计时所依据的业务和管理模型。现在，您需要使用 OU 作为构建块，在 Active Directory 中重建该结构。创建一个完整的 OU 结构，精确反映该域所代表的业务模型。换言之，如果您设计的域是财务域，请在该域内实现财务组织结构。您不需要在每个组织单元中创建整个组织的业务模型；只需创建实际适用于该 OU 的那部分模型。将此结构画在纸上。图 13-3 展示了一个直接匹配业务组织结构的示例。为简洁起见，此处仅展开了财务 OU。

![The Mycorp domain’s internal organizational unit structure](./image/13.%20Designing%20the%20Active%20Directory%20Structure/httpatomoreillycomsourceoreillyimages1663481.webp)

图 13-3. Mycorp 域的内部组织单元结构

一旦您绘制出作为域内 Active Directory 层次结构模板的 OU 结构，就可以开始根据具体需求对其进行调整。调整初始 OU 设计的最简单方法是考虑您希望为管理委派创建的层次结构。

##### 委派完全管理权限

首先，确定层次结构中需要授予管理员对其分支进行自主访问权限的任何区域。每个 OU 应至少有两名管理员负责该组织单位。这些管理员将负责组织单位下方的结构，根据需要创建 OU、用户、组等。但他们不会对树的其他任何部分拥有管理访问权限。

对于您确定的每个组织单位，需要记录以下两项信息：

- 谁将担任管理员？
- 他们将管理树的哪个分支？

> **警告**：

必须确保委派管理员( Delegated Administrator )对其操作负责，并且能够被追责。这一点再怎么强调也不为过。低层级组织单位( Organizational Unit ,OU)的管理员完全有可能做出影响他人的更改。

##### 委派其他权限

为所有需要完全管理访问权限的 OU 记下这两项信息后，接下来需要确定哪些 OU 要求某些用户拥有更受限的权限集。你可能希望设置账户管理员，使其能够创建和删除用户账户，以及设置密码和账户详细信息。目前我们只从总体层面关注权限，因此只需记录以下内容：

- 访问权限是什么
- 这些访问权限将应用到树的哪个分支
- 哪些用户或组（从总体层面而言）将拥有这些访问权限

如果需要，可以将任何类型的访问权限细化到特定对象上的单个属性级别。这意味着，如果你愿意，可以允许名为 George Washington 的用户更改名为 James Madison 的用户（且仅限该用户）的密码或电话号码。显然，访问权限越精细，情况可能就越复杂，尤其是因为默认情况下权限会沿树向下继承。为了简化操作，Microsoft 提供了一个简单的控制委派向导( Delegation of Control Wizard )，让你能够以相当轻松的方式设置这些访问权限。Active Directory 权限在第 16 章中有更深入的介绍；在设计阶段，我们在此只关心 OU 级别的控制委派。根据经验，我们可以告诉你，在 OU 级别分配访问权限，始终比跟踪单个对象和属性的权限要容易管理得多。

> **注意**：

设计 OU 结构时，也许最重要的一点是使其保持一致且可重复。如果你正在按位置创建 OU 结构，请开发一个脚本，为每个位置创建该标准结构（以及任何适用的权限委派）。管理那些独立设计和管理的 OU 结构，很快会变得极其困难，甚至无法高效进行。

#### 步骤 4：设计工作站与服务器命名约定

现在，您已拥有一个或多个域树构成的林，以及一个组织单位( OU )结构。接下来，您可以考虑服务器和工作站的命名约定。

> **注意**：

在此讨论命名约定的同时，关于机器在 Active Directory 中的确切位置，我们将在第 15 章中探讨设计组策略对象( Group Policy Objects ,GPO)时详细说明。这是因为 GPO 可依据客户端机器位置对其产生影响。

在 Active Directory 网络环境中，每个客户端工作站或服务器必须在林中的某处拥有一个计算机账户，以便用户通过该客户端登录。当计算机加入林中的某个域时，会在 Active Directory 中创建计算机账户，并在客户端与域之间建立信任关系，从而确认客户端为域的有效成员。

客户端在林中的位置决定了其名称的一部分。成员服务器通常置于承载该服务器大多数用户的域中，而域控制器( Domain Controllers ,DC)则依其本质属性位于各自所宿主的域内。客户端可置于任意位置，但通常放置在其主要用户常规登录的域中。

所有主机命名格式为 *<计算机>.<域>*。例如，位于 *cohovines.com* 域中名为 *SRV01* 的服务器，通常会被命名为 *srv01.cohovines.com*；而位于欧洲域中名为 *SRV02* 的服务器，则通常命名为 *srv02.europe.cohovines.com*。

> **注意**：

虽然通常不会讨论这一点，但给定域中计算机的 DNS 域名并不严格要求与活动目录( Active Directory ,AD) 域名匹配。

这是分离命名空间( Disjoint Namespace )的一个示例，并且是 Microsoft 支持的配置。这种类型的配置有时出现在具有复杂分布式 DNS 配置的大型企业级组织中。例如，您可能会发现一台名为 *srv01.detroit.michigan.us.cohovines.com* 的服务器，它是 AD 域 *northamerica.cohovines.com* 的成员。

部署 Active Directory 不会强制您更改现有的任何主机名。但是，如果您计划合并多个单独的域，则需要确保所有主机名在它们所在的域内是唯一的；或者，如果 WINS 与完全网状复制( Full Mesh Replication )一起使用，则需确保它们在整个公司内是唯一的。

如果您尚未要求为客户端和服务器采用一致的命名方案，那么现在正是创建这种方案的时候。完全限定的域名( Fully Qualified Domain Name ,FQDN)必须在整个林内唯一；这是通过将域组件附加到计算机名上来实现的。这样您只需关注前缀，也就是说计算机名只需在域范围内唯一。

为了保持向后兼容性，名称不能超过 15 个字符。这是因为 Active Directory 仍然对 NetBIOS 名称提供一些旧式支持，并且您选择的主机名将作为客户端上的 NetBIOS 名称并入。NetBIOS 名称限制为 15 个字符。

您需要制定一个林范围的命名约定( Forest-Wide Naming Convention )，确定在 15 个字符限制内如何命名客户端和服务器。该约定由您决定，但我们在本章后面查看示例设计时会提供一些示例。

#### 步骤 5：规划用户和组

在开始本节之前，我们必须明确组( Group )与组织单位( Organizational Unit ,OU)之间的区别。OU 是对象的容器，允许对象在域( Domain )内以层次结构表示。将对象放在此类层次结构中，可以有选择地将管理委派( Delegation of Administration )给这些组织单位，并应用组策略( Group Policy ,GPO )。这些内容我们前面已经介绍过。

另一方面，组仅将用户或计算机(或其他组)作为成员，可用于向成员统一分配权限或权利。假设名为 Finance 的组织单位中有 50 个用户，并且这些用户同时是名为 Finance Users 的组成员。当我们想要授予这 50 个用户对某个共享( Share )的读取权限，或对域层次结构中某些部分的受限访问权限时，我们会将权限分配给 Finance Users 组。当你希望为 OU 内包含的对象分配权限时，用户位于 Finance OU 中这一事实并不会产生影响。但是，如果我们希望委派某人拥有管理这 50 个帐户的权限，我们会将管理委派放在该 OU 上。这里，我们将讨论如何有效地规划用户帐户以及这些用户所属的组。

##### 用户的命名与放置

在规划用户帐户时，唯一真正需要关注的是客户端登录时使用的用户名或用户标识符。每个用户名(用户对象的 `sAMAccountName` 属性)都必须在每个域中唯一。如果你已决定在组织内委派管理，并允许委派管理员创建用户帐户，则需要创建每个管理员都将遵守的命名约定( Naming Convention )，以便为整个林( Forest )中的所有用户生成唯一的用户名。

> **警告**：

若您选择允许委派管理员创建用户账户，请务必仔细考虑其安全影响。当用户账户以分散方式创建时，通常缺乏审计跟踪、明确的归属链路或针对该账户的账号生命周期管理。我们强烈建议您通过请求流程或自动化工具集来集中管理用户创建，以建立并维护此类安全控制措施。

您为所有 Active Directory 用户指定的另一个名称是用户主体名称（即用户对象的`userPrincipalName`属性）。这一属性形式上类似于 RFC 2822 电子邮件地址，例如 *username@cohovines.com*。实际上，该属性并非电子邮件地址，而是用户在整个林中的唯一标识符。其值必须唯一，因为它唯一标识了林内的用户。因此，尽管在 *cohovines.com* 和 *executives.cohovines.com* 中拥有` sAMAccountName `值为 *George.Washington* 的用户是完全可行的，但每个用户账户的用户主体名称（UPN）必须是唯一的。

通常，用户主体名称（UPN）的创建方式是在用户名后直接附加@符号及域名。这样做确保了唯一性，因为用户名在域内已属唯一，而附加域名则强制形成了林范围内唯一的UPN。于是，前例中的两个用户账户的UPN分别为 *George.Washington@cohovines.com* 和 George.Washington@executives.cohovines.com。

然而，尽管按此方式构建UPN是惯例，实际上您可以将用户的UPN设置为任意值，只要遵循RFC 2822规定的格式即可。例如，我们可以为所有用户附加 *@cohovines.com*，完全不必依赖域。但若采取这种做法，则需确保所有用户名（`sAMAccountName`）在林范围内独一无二。在此前示例中，就不能有两个用户使用相同的用户名 *George.Washington*。为了使此类方案可行，需要建立一个中心数据库或分配机构，以唯一生成并分配名称。如果该数据库或机构能通过可靠算法生成唯一用户名，那么您就可以采用更为简洁的UPN。

> **注意**：

我们选择 *@cohovines.com* 作为后缀，并不意味着我们受限于林( Forest )或域( Domain )名称。我们同样可以轻松选择 *@contoso.com*，它与域或林没有任何关系。用户主体名称( User Principal Name ,UPN)只需在林中的每个用户之间保持唯一即可。

正如后缀不必与林或域名匹配一样，用户名部分也不必与 `sAMAccountName` 匹配。事实上，你可以在不指定 `sAMAccountName` 的情况下创建用户。这将自动生成一个类似于 `$KJK000-H4GJL6AQOV1I,` 的 `sAMAccountName`，这实际上并不是一个友好的登录名。但是，你可以随后将 UPN 设置为 *George.Washington@cohovines.com*，并将其用于登录。

UPN 非常重要。设想用户坐在林内任意位置的客户端前，面对登录对话框。此时，用户可以输入其用户名(`sAMAccountName`)、密码和域，然后通过林进行身份验证。然而，使用 UPN 进行身份验证也是完全可行的。如果用户面对同一个登录对话框，在用户名字段中改为键入 UPN，则不再需要指定域。

换句话说，向 Active Directory 进行身份验证只需要 UPN 和密码。这是合理的，因为 UPN 在整个林内是唯一的；除了密码之外，不应需要其他任何内容。你现在应该能够看到，即使林中的域集合非常庞大且复杂，你也可以使用不包含域组件( Domain Component )的简化 UPN 形式，然后只需指示用户使用 UPN 和密码登录。这意味着用户永远无需关心自己位于哪个域中。

许多组织选择使用用户的电子邮件地址作为 UPN。这种策略的好处有两个方面。第一个好处是可以指示用户使用其电子邮件地址登录，因此他们需要记住的信息少了一项。第二个好处是电子邮件地址是唯一标识符，因此 UPN 也将是唯一的。

你选择将用户帐户放置在每个域层次结构中的哪个位置，实际上只受谁将管理这些帐户以及帐户所在组织单位( Organizational Unit ,OU)上将应用哪些组策略对象( Group Policy Object ,GPO)的影响。除此之外，几乎没有区别。

##### 命名组和放置组

组( Group )也需要唯一名称，因此，还应在设计中规划组的命名方案。将组放在何处不那么重要。实际上，组几乎可以放在层次结构中的任何位置。例如，决定用户( User )放置位置的组策略对象( Group Policy Object ,GPO)并不适用于组。

与用户非常相似，组也有一个 `sAMAccountName` 字段，该字段在域( Domain )内必须唯一。如果你委派管理，使被委派的管理员能够创建组，我们建议你设计一种命名约定，在名称中体现拥有该组的部门或组织。例如，你可以为所有组名添加一个两字母或三字母代码作为前缀，用以指明组的所有者。

如果可能，并且如果你打算委派创建和管理组的能力，我们强烈建议你考虑使用外部工具来管理组对象( Group Object )。这样，你就可以为组确立用途、所有权、审核跟踪和生命周期。这有助于限制目录( Directory )中用途或所有者未知的组无序蔓延。Microsoft Forefront Identity Manager (FIM) 就是有助于满足此建议的一种工具示例。

### 13.6. 其他设计注意事项

在许多情况下，你可能需要多次修订设计。当然，组策略对象( Group Policy Object ,GPO)会影响你组织用户和计算机对象的方式，因此我们不认为走一遍设计流程就足够了。

一旦有了基本设计，你完全可以将其暂时搁置一旁，转而着手为 Active Directory 网络确定一个“完美”设计——一个你希望在组织中实施、且忽略所有由 Active Directory 施加的设计约束的设计。然后，你可以评估从前述步骤得出的实用设计迁移到该完美设计会有多困难。你可以考察从一种设计迁移到另一种设计的可行性，随后进行合理化调整，将已列出的因素纳入最终设计。之后，你可以将其作为迭代工具，使最终设计更接近理想目标。

除了 GPO 之外（我们已在第 11 章和第 15 章中介绍），Active Directory 设计中还有其他方面，我们尚未、也不会在本书中介绍。例如，你很可能希望将打印机发布到 Active Directory 中，以便通过简单搜索 Active Directory 就能轻松访问。你可能还想使用分布式文件系统( Distributed File System ,DFS)，它允许你将分散且分布式的共享组织成单一连续的层次结构。当你引用 DFS 持有的共享时，DFS 会使用 Active Directory 站点拓扑( Site Topology )自动将你的请求重定向到最近的共享副本。此外，还涉及设计你希望包含的自定义对象和属性。如果你正在考虑这一点，应关注以下两点：

- 通常而言,Active Directory 应仅保存静态数据或相对静态的数据。最起码,数据的生存期必须长于其复制到组织中所有域控制器( Domain Controller ,DC)所需的时间。在考虑要添加哪些对象时,应排除生存期极短的对象。动态数据——即生存期相对较短的数据——更适合存储在应用程序分区( application partition )或 AD LDS 实例中,或者也可通过使用动态对象功能( dynamic objects feature )来实现。
- 你添加的任何对象,其属性都会保存在全局编录( Global Catalog ,GC)中。对于计划存储在 Active Directory 中的每一种对象类型,都应查看该对象的架构定义( schema definition ),以了解哪些属性会存储在全局编录中。

### 13.7. 设计示例

在探讨了命名空间和OU结构的设计之后，接下来应当展示一些实际的设计示例。我们虚构了几家组织，它们将作为演示设计流程的良好范例。虽然这里没有详尽介绍这些组织的所有细节，但所提供的信息足以让你尝试进行合理的设计。在后续章节中，我们将根据设计的不同部分需求，逐步展开每家公司的相关信息。

我们依据以下标准创建了这些组织：

- 样本旨在代表多样化的组织及其结构。
- 尽管每个组织拥有相当数量的用户和计算机，但设计原则同样适用于规模较小的组织。
- 在这些示例组织中，我们并不关注每家公司拥有的域控制器数量或服务器位置。这些因素将在下一章关于站点拓扑的内容中讨论。我们关注的是用户、组、计算机、域以及所采用的业务和管理模型。

#### Tailspin Toys

Tailspin Toys 是一家在北美地区拥有约 3,000 名员工的组织。Tailspin Toys 各站点共分布有约 4,000 台客户端计算机和数百台服务器。办公人员分布在美国和加拿大的多个城市，以及居家办公场所。制造业务在墨西哥开展。位于旧金山总部办公室的 IT 部门负责管理整个组织的 IT 资产。

##### 第 1 步：确定域( Domain )的数量

鉴于组织规模较小，且存在连接性要求，Tailspin Toys 选择部署单域 Active Directory 林( Forest )。尚未发现任何需要分离复制( Replication )的需求。同样，也不存在任何需要将资源分离到单独的林中的顾虑。

##### 第 2 步：设计和命名树结构( Tree Structure )

此域/林将命名为 *tailspintoys.com*，NetBIOS 名称为 *Tailspin*。鉴于设计简单，除根域( Root Domain )名称外，无需担心树结构或命名问题。

##### 步骤 3：设计组织单位( Organizational Unit ,OU)的层次结构

Tailspin Toys 几乎集中管理活动目录( Active Directory )中的所有对象。由于对复杂权限委托的需求有限，Tailspin Toys 在设计其 OU 结构时将重点放在组策略( Group Policy )上。在审视了组织的需求后，他们开发了一种基于位置和对象的 OU 结构。这样一来，策略既可以针对物理位置，也可以针对特定类型的对象(例如，台式计算机与笔记本电脑)。图 13-4 展示了 Tailspin Toys 的顶层 OU 结构。




![Tailspin Toys top-level OU structure](./image/13.%20Designing%20the%20Active%20Directory%20Structure/httpatomoreillycomsourceoreillyimages1663482.webp)


图 13-4. Tailspin Toys 顶层 OU 结构

由于支持制造活动的计算机具有业务关键性，因此为车间计算机建立了一个单独的 Manufacturing OU 结构，以将其与最终用户计算机的管理隔离开来。

图 13-5 展示了旧金山办事处 Locations OU 下的 OU 结构，以及其父结构。按地理位置以层次结构组织计算机，使 IT 部门能够针对全球、区域或单个位置级别的用户应用组策略。IT 部门还为每个站点分配了位置代码，以便在网络中标识该站点。为简单起见，位置代码由城市的三字母机场代码加上两位数字组成，以防某个城市有多个办事处。




![Tailspin Toys Locations OU](./image/13.%20Designing%20the%20Active%20Directory%20Structure/httpatomoreillycomsourceoreillyimages1663483.webp)


图 13-5. Tailspin Toys Locations OU

为保持管理简单直接，他们为 Manufacturing OU 开发了类似的结构。由于 Manufacturing OU 仅包含用于支持车间活动的计算机，因此开发了 图 13-5 中结构的精简版本，如 图 13-6 所示。制造计算机直接放置在站点的 OU 中。




![Tailspin Toys Manufacturing OU structure](./image/13.%20Designing%20the%20Active%20Directory%20Structure/httpatomoreillycomsourceoreillyimages1663484.webp)


图 13-6. Tailspin Toys Manufacturing OU 结构

在组织单位( Organizational Unit ,OU)结构最终确定后,我们制定了权限委派方案。基于 Tailspin Toys 的集中式 IT 组织模式,Active Directory 中只需委派两组权限:

- 为帮助台分析师重置密码并解锁账户
- 为桌面技术人员将计算机加入域

这两项任务均可借助 Active Directory 用户和计算机( Active Directory Users and Computers )中的控制委派向导( Delegation of Control Wizard )轻松完成委派。

##### 步骤 4：设计工作站与服务器命名约定

由于 Tailspin Toys 会根据计算机的物理位置、计算机类型（例如台式机或笔记本电脑）以及功能（客户端计算机、自助终端或制造用计算机）将工作站放入组织单位( Organizational Unit ,OU)，因此决定在命名约定中纳入所有这些数据点。此外，根据一线桌面技术人员的意见，还会纳入计算机在单个站点中的位置（例如办公室编号或工位）。

Tailspin 的命名约定记录在 图 13-7 中。该命名约定记录了在 Active Directory 规定的 15 个字符最大限制内每个可能的字符。




![Tailspin Toys computer naming convention](./image/13.%20Designing%20the%20Active%20Directory%20Structure/httpatomoreillycomsourceoreillyimages1663485.webp)


图 13-7. Tailspin Toys 计算机命名约定

这些字段包括：

- **站点代码( Site Code )**

  这是分配给每个物理位置的五字符代码。Tailspin 在整个 IT 领域使用这些代码，包括网络设备、服务器、台式机以及 图 13-5 中的 OU 结构。前三个字母是最近主要机场的机场代码，后跟一个两位数字，用于标识给定城市内的具体位置。

- **功能代码( Function Code )**

  该字母标识计算机是客户端计算机（C）、自助终端机（kiosk machine，K）还是制造用计算机（manufacturing machine，M）。

- **类型代码( Type Code )**

  该字母标识计算机是 PC 台式机（D）、PC 笔记本电脑（L）、Macintosh 台式机（M）还是 Macintosh 笔记本电脑（P）。

- **位置代码( Location Code )**

  此字段最多允许五个字符，可由本地桌面技术人员分配。桌面技术人员通常在此字段中编码办公室位置、工位、车间列号或类似信息。

- **索引( Index )**

  这是一个数字字段，从 01 开始，用于区分给定位置中的多台计算机。

基于命名约定与 OU 结构的对应关系，开发了一个脚本，用于自动将默认 Computers 容器中的任何计算机移动到相应 OU。该脚本计划每五分钟运行一次。这样，IT 无需再手动在目录中移动计算机。

图 13-8 中展示的服务器命名约定简单直观,与桌面计算机命名约定相似。

![Tailspin Toys server naming convention](./image/13.%20Designing%20the%20Active%20Directory%20Structure/httpatomoreillycomsourceoreillyimages1663486.webp)

图 13-8. Tailspin Toys 服务器命名约定

各字段说明如下:

- **站点代码( Site Code )**

  这是分配给每个物理位置( physical location )的五字符代码。Tailspin 在整个 IT 环境中沿用这些代码,涵盖网络设备、服务器、桌面计算机以及图 13-5 中的 OU 结构。前三个字母是距离最近的大型机场的机场代码,后接一个两位数字,用于标识给定城市内的具体位置。

- **环境代码( Environment Code )**

  该字母标识服务器处于生产( P )、测试( T )还是开发( D )环境中。

- **服务器类型代码( Server Type Code )**

  此三到四字符字段用于概括性地标识服务器类型。Tailspin Toys 所使用的服务器类型代码列表记录在表 13-1 中。

  > **警告**
  >
  > 我们已在众多场合成功使用了与此处所记录约定非常相似的命名约定。请勿为您能想到的每一种服务器排列组合都定义一个服务器类型代码。如果您不需要通过网络名称来区分不同类型的服务器,那么请坚持使用通用类型代码。
  >
  > 当引入新服务器且未为其定义特定类型代码时,我们通常会使用应用程序服务器类型代码。

- **物理/虚拟/群集指示符( Physical/Virtual/Cluster Indicator )**

  该字母标识服务器是运行在物理硬件( physical hardware ,P)上,还是运行在虚拟化环境( virtualized environment ,V)中,或者该名称代表群集虚拟名称( cluster virtual name ,C)。

- **索引( Index )**

  这是一个数字字段,从 01 开始,用于区分给定站点中同一类型的多台服务器。

表 13-1. 服务器类型代码

| 服务器类型代码 | 描述 |
| ---------------- | ----------------------- |
| ADC              | 域控制器( Domain Controller ,DC) |
| ADM              | 管理工具服务器 |
| APP              | 应用程序服务器 |
| CLN              | 群集节点( Cluster Node ) |
| DBS              | 数据库服务器 |
| RDS              | 远程桌面服务器( Remote Desktop Server ) |
| SRV              | 文件与打印服务器 |
| VMH              | 虚拟化主机 |
| XSV              | Exchange 服务器 |

##### 步骤 5：规划用户和组

鉴于 Tailspin Toys 规模相对较小，因此设计了一种简单的用户名命名约定，即用户名字的首字母加上用户的姓氏。例如，George Washington 的用户名将是 *gwashington*。如果发生冲突，则在用户名末尾追加一个两位数的序号，以保证其唯一性。

由于所有组都将由 IT 部门集中管理，因此组名是根据最符合组用途的原则临时分配的。现行策略要求在每个组的 `notes` 属性中列出组的用途以及两名职能负责人。组的职能负责人负责批准将用户添加到组中，并报告组的用途。

#### Contoso College

Contoso College 是一家高等教育机构，拥有约 3,500 名员工、30,000 名学生和 5,000 台计算机。所有用户和计算机都位于单一园区。IT 资源的管理为分散式，各部门对其区域内的计算机和资源拥有高度自治权。为了提供集中化、可持续且分布式的目录服务，中央 IT 正在部署一个 Active Directory 林( Active Directory forest )，该林支持自动管理的用户账户和组，并能让委派管理员获得组织单位( Organizational Unit ,OU)，从而按需管理其中的资源。

##### 步骤 1:确定域的数量

鉴于 Contoso 计划将学生纳入中央 Active Directory 林，围绕学生账户应置于单独的子域( Child Domain )，还是甚至单独的林中，存在大量争论。由于需要为应用程序交互提供中央目录，并且需要简单直接的管理，单独的学生账户林很快被排除。在审视各项事实(包括子域不会创建安全边界这一现实)后，Contoso College 决定采用包含所有用户账户的单域林。

##### 步骤 2:设计并命名树结构

Contoso 已有运行在 Unix BIND 服务器上的现有 DNS( Domain Name System ,DNS)基础设施。由于 Windows 管理团队将管理 Active Directory，且 Unix BIND 环境未配置为支持动态更新，Active Directory 将部署在 Contoso 根域( Root Domain )(*contoso-college.edu*)的子区域( Subzone )中。该子区域将委派给域控制器( Domain Controller ,DC)，并托管在 Active Directory 集成 DNS 区域( Active Directory–integrated DNS zone )中。为了给域提供通用名称，选择了 DNS 名称 *net.contoso-college.edu*。将使用 NetBIOS 名称( NetBIOS Name )*NET*。

##### 步骤 3：设计组织单位( Organizational Unit ,OU)的层次结构

Contoso 在规划 OU 结构时，需要满足若干有时相互冲突的需求。首先，该域既要能够由中央 IT 资源进行管理，又要足够灵活，以满足学院各系部委派管理员的需求。为了满足这些需求，Contoso 设计了如图 13-9 所示的顶级 OU 结构。




![Contoso College top-level OU structure](./image/13.%20Designing%20the%20Active%20Directory%20Structure/httpatomoreillycomsourceoreillyimages1663487.webp)


图 13-9. Contoso 学院顶级 OU 结构

下面是图 13-9 中每个顶级 OU 的说明：

- **共享资源( Shared Resources )**

  此 OU 包含与整个林( Forest )和网络支持相关的对象。这些资源包括管理账户、集中管理的组以及集中管理的服务器(不包括域控制器( Domain Controller ,DC))。

- **人员( People )**

  由于用户对象将由自动化身份管理解决方案进行管理，因此将这些对象放在集中管理的 OU 中最合理。Contoso 决定不按用户类型(例如员工或学生)或位置来划分用户账户，因为学院中的许多用户具有多重角色，有时还身兼多职。例如，员工选修课程因而同时被视为学生的情况并不罕见。

- **委派的 OU( Delegated OUs )**

  在此 OU 下，将创建系部管理员请求的每个 OU。将 OU 嵌套在委派的 OU 之下，是为了在需要对所有对象应用组策略( Group Policy )或安全委派时，不会影响共享资源、域控制器等。本节稍后会更深入地探讨此结构。

每个委派的 OU 结构都是整个环境中通用的固定结构与委派管理员可在特定位置创建 OU 的灵活性相结合的产物。图 13-10 显示了在每个委派的 OU 下创建的固定结构。




![Contoso College department OU template](./image/13.%20Designing%20the%20Active%20Directory%20Structure/httpatomoreillycomsourceoreillyimages1663488.webp)


图 13-10. Contoso 学院系部 OU 模板

在每个委派的 OU 中，有若干子 OU：

- **组( Groups )**

委派管理员( Delegated Administrators )创建的任何组对象都置于此组织单位( Organizational Unit ,OU)中。此外，随 OU 结构一起创建并委派了权限的若干组也置于此 OU 中。委派管理员随后只需将用户嵌套到正确的组中，即可管理其 OU 结构的权限。对于 Groups OU，会创建一个名为 *<Department Name> - 组管理员* 的组，并委派其创建、删除和管理部门 Groups OU 中所有组的能力。

- **Users**

  与学生和员工对应的用户帐户置于 图 13-9 所示的顶层 People OU 中。委派管理员可以为需要临时

- **Servers**

  Servers 组织单位( Organizational Unit ,OU)包含由该部门管理的服务器。Contoso 的安全策略规定,OU 所有者需对该部门管理的所有服务器的安全负责。

##### 步骤 4：设计工作站( Workstation )和服务器( Server )命名约定

由于 Contoso College 具有分布式特性，整个组织中没有采用明确定义的工作站或服务器命名约定。各部门在收到委派的组织单位( Organizational Unit ,OU )时，必须向中央 IT 组织注册一个由 2 到 5 个字符组成的前缀。所有工作站和服务器名称都必须以此代码为前缀。计算机帐户( Computer Account )将根据计算机对象名称中的前缀，自动移到正确的 OU。

##### 步骤 5：规划用户和组

当每位用户录入全院企业资源规划( Enterprise Resource Planning ,ERP )系统时，Contoso College 会为其分配唯一的用户名。在为用户帐户进行预配时，身份管理系统( Identity Management System )会将该用户名反映到 Active Directory 中。如果用户想要更改其用户名，必须通过人力资源部或学生事务部提出更改请求。如果更改获批，将录入 ERP 系统，然后自动反映到 Active Directory 中。

对于手动创建的帐户，例如来宾帐户( Guest Account )，Contoso 的安全策略规定，来宾帐户用户名必须以 *g-* 为前缀。此外，这些帐户必须在 Active Directory 中定义到期日期。对于未定义到期日期的来宾帐户，中央 IT 会每晚自动将其禁用。

服务帐户( Service Account )必须以 *sa-* 为前缀，并且描述字段必须说明该帐户的用途。

组可由创建者随意命名；但名称必须以申请 OU 时向 IT 注册的 2 到 5 个字符代码为前缀。这可以确保组名不会冲突。

#### Fabrikam

Fabrikam 是一家全球性数十亿美元规模的组织，在全世界 100 多个站点( Site )拥有超过 250,000 名员工和计算机。该企业在芝加哥设有全球总部。另有四个主要站点连接到总部( Headquarters ,HQ )，较小的分支机构( branch office )则连接到这些站点：亚太地区( Asia-Pacific )、北美( North America )、南美( South America )和欧洲( Europe )。小型站点通过速率介于 64 kbps 到 T1 的链路连接到中心站点( hub )；中心站点自身则通过各种更高速链路连接到总部。部分中心站点之间也互连。

Fabrikam 的管理结构按地区划分，每个地理单元作为全球组织的一部分，以独立业务方式运营。管理结构的顶层位于总部，总部处于四个中心站点之上。尽管芝加哥可被视为属于北美地区，但该组织并非按此方式构建。事实上，芝加哥的信息技术( Information Technology ,IT )人员负责监督各中心站点，包括选择管理员以及确定网络的结构方式。公司 IT 策略规定，人数超过 500 的分支机构必须拥有自己的本地管理员、备份支持人员和帮助台( helpdesk )人员。人数少于 500 的分支机构必须由其所连接中心站点的管理员管理（参见图 13-11）。

其他考虑因素包括：

- Fabrikam 最近收购了 Trey Research，这是一家加拿大公司，拥有 Fabrikam 希望保留的强势品牌。Trey Research 仅设于加拿大的一个新分支机构中。
- 南美分支机构与中心站点之间的链路非常不可靠。
- 亚太中心站点与欧洲之间的站点链路( Site Link )经常严重拥塞。

![Fabrikam network topology](./image/13.%20Designing%20the%20Active%20Directory%20Structure/httpatomoreillycomsourceoreillyimages1663489.webp)

图 13-11. Fabrikam 网络拓扑( network topology )

##### 步骤 1:确定域的数量

传统上,如果 Fabrikam 是在 Windows 2000 时代规划其 Active Directory 部署,它很可能会选择部署一个空根域,并在其下按地区组织一系列子域(例如,分别面向北美、欧洲、南美和亚太地区的域)。考虑到目录的规模,以及 Fabrikam 在南美和亚洲面临的网络连接挑战,在某些地区通过部署子域来隔离复制,不失为一种恰当且必要的解决方案。

考虑到部署多域林( multidomain forest )的相对成本和复杂性,以及目前缺乏完整的性能数据和对网络影响的全面分析,Fabrikam 决定采用单域林。在评估复制的影响时,Fabrikam 意识到,在设有域控制器( Domain Controller ,DC)的分支机构中,多域林带来的优势相当有限,因为这些机构仍然需要在本地部署全局编录( Global Catalog ,GC)。倘若日后发现南美或亚洲的性能因采用单一全局域而受到不利影响,Fabrikam 将在该地区部署一个子域,并将用户、计算机和其他资源迁移到该子域中。

Trey Research 是 Fabrikam 旗下的一家独立子公司,Fabrikam 打算将其作为独立公司保留。Trey Research 与 Fabrikam 的竞争对手签有合同,管理层认为 Trey Research 未来有可能被剥离。因此,Trey Research 将继续维护一个独立的林,并通过双向信任( two-way trust )与 Fabrikam 林建立信任关系。

##### 步骤 2:设计并命名树结构

Fabrikam 已有现成的 DNS 基础结构,而要针对 *fabrikam.com* 区域改用拆分式 DNS( split-brain DNS )模型,其成本高得令人望而却步。目前,Fabrikam 拥有 *fabrikam.net* 域名,但该命名空间尚未用于任何用途。因此,Fabrikam 决定将其林根域( forest root domain )部署为 *fabrikam.net* ,NetBIOS 名称为 *FABRIKAM* 。

林投入运行后,将与 *treyresearch.com* 域建立双向林信任( forest trust )。

##### 第 3 步：设计组织单位( Organizational Unit ,OU)的层次结构

鉴于 Fabrikam 采用半分散式的 IT 管理模式，需要将大量权限委派给在分支机构本地管理 IT 资源的技术人员。全公司的所有 IT 人员最终都要对芝加哥总部的 IT 人员负责，因此不会以让本地人员对其各自所在地拥有*全权*访问权限的方式委派控制权。

相反，将为每个位置建立标准化结构。本地人员将有权执行与其工作相关的任务，而总部办公室的 IT 人员将有权访问公司中的所有位置。

图 13-12 显示了 Fabrikam 域( Domain )的顶层结构。

![Fabrikam top-level OU structure](./image/13.%20Designing%20the%20Active%20Directory%20Structure/httpatomoreillycomsourceoreillyimages1663490.webp)

图 13-12. Fabrikam 顶层 OU 结构

以下是每个顶层 OU 的说明：

- **企业支持( Enterprise Support )**

  此 OU 包含与整个林( Forest )和网络支持相关的对象。这些资源主要包括管理账户和服务账户( Service Account )。

- **站点( Sites )**

  此 OU 是表示每个 Fabrikam 办公室的 OU 的父级。我们稍后将介绍此 OU 的结构。

- **组( Groups )**

  Fabrikam 选择通过集中的基于 Web 的组管理工具来管理所有组。因此，所有组都放在一个未对其委派访问权限的 OU 中。

- **服务器( Servers )**

  Fabrikam 的 IT 安全策略规定，特定功能的所有服务器都必须应用相同的策略和设置。服务器按服务器上运行的服务或应用程序类型组织到子 OU 中，以便可以将组策略( Group Policy )应用到该类型的所有服务器。

站点 OU 如 图 13-13 所示。每个特定位置的 OU 按地区、国家/地区，然后按站点组织。这样，管理员便可在层次结构的每一级委派控制权（例如，授予新加坡的帮助台分析师重置亚洲所有用户密码的能力），以及在该层次结构的任何级别应用组策略。

> **注意**：

在开始通过像 Active Directory Users and Computers 这样的图形用户界面( Graphical User Interface ,GUI )构建所有这些内容之前，请从书架上取下 Laura E. Hunter 和 Robbie Allen(O’Reilly) 著的 *Active Directory Cookbook*，并编写一个脚本来构建组织单位( Organizational Unit ,OU )结构和权限。由于这些结构将完全相同，随时间推移保持一致性的最佳机制是将此过程脚本化。管理员不想成为数据录入员，因此构建这样的结构非常适合通过脚本完成。

![Fabrikam site-level OU structure](./image/13.%20Designing%20the%20Active%20Directory%20Structure/httpatomoreillycomsourceoreillyimages1663491.webp)

图 13-13. Fabrikam 站点级 OU 结构

##### 步骤 4：设计工作站和服务器命名约定

Fabrikam 正在使用桌面管理解决方案跟踪其所有台式机和笔记本电脑。计算机在公司内也相当频繁地移动，而且员工往往不会长期受雇于该组织。因此，Fabrikam 不希望在名称中编入计算机位置或使用该计算机的员工信息。同时，Fabrikam 需要确保计算机名称在网络上唯一，并有办法将给定计算机与其在桌面管理数据库中的记录关联起来。

为实现这一点，Fabrikam 决定根据计算机制造商的序列号为每台计算机命名。由于 Fabrikam 的台式机和笔记本电脑有多个供应商，它决定在计算机序列号前加上表示制造商的两个字符代码，如表 13-2所示。这种命名约定便于技术人员实施，无需更改计算机名称，并可确保计算机名称与资产管理数据库关联。

表 13-2. 计算机命名前缀

| 代码 | 制造商 |
| ---- | ---- |
| AP   | Apple |
| DL   | Dell |
| HP   | Hewlett-Packard (HP) |
| IB   | IBM |
| LN   | Lenovo |

对于服务器，Fabrikam 在配置管理数据库( Configuration Management Database ,CMDB )中维护每台服务器及其角色的信息。由于所有这些信息都在 CMDB 中跟踪，Fabrikam 决定根据托管服务器的站点位置代码，后跟一个在该位置唯一标识服务器的连续四位数字来命名服务器。例如，SEA01 站点的一台服务器可能命名为 *SEA01-0096*。

##### 步骤 5：规划用户和组

用户帐户( User Account )将从芝加哥总部维护的中央人力资源( Human Resources ,HR)数据库中自动预配。由于员工数量庞大且可能存在重复，预配系统会为每个用户构造唯一的用户名，该用户名由用户的名字、中间名首字母和姓氏中的部分字符构成。

组( Group )由通过中央组管理系统创建该组的用户任意命名。

### 13.8. 识别理想设计的潜在问题

可以说，设计活动目录( Active Directory )的“最佳”方法有很多种，具体取决于你咨询的对象是谁。我们建议采用迭代式方法，而由于众多相互竞争的因素交织在一起，这种迭代过程往往也是不可避免的。在本章第一遍阅读时，你将获得命名空间( Namespace )的草案设计。在第14章中，你将获得站点和复制设计的草案。随后你会遇到一个问题：基于新的站点和复制设计草案，你的命名空间设计可能需要调整，尤其是在我们刚刚讨论过的域复制和服务器放置方面。修改完命名空间设计之后，你可以坐下来从宏观层面审视组策略对象( Group Policy Object ,GPO )设计（参见第11章和第15章），因为这会影响你之前在命名空间设计中起草的组织单位( Organizational Unit ,OU )结构。

虽然这是设计的正确路径，但你仍会遇到组织中某些部分与你正在做的设计不匹配的情况。关键在于认识到：你的任务是找到适合你组织的*非常优秀的*解决方案，然后决定如何将该方案适配到公司所处的现实环境中。单一域可能是理想选择，但在成本或人力资源方面可能不切实际。你必须经历多个修改设计阶段，才能达成一个令自己满意的折中方案。

最后，我们要强调：本书中的案例研究仅仅是示例！每个案例都可以有多种不同的设计方式。我们选择的设计是基于每个示例组织的有限信息以及本书的篇幅限制，在我们看来是可行的方案。

请不要认为本节中看到的设计就是在指示你应该如何设计自己的目录。我们认为它们是极好的起点，但你需要根据自己的需求，制定最适合你组织的设计方案。

### 13.9. 总结

本章介绍了实现有效命名空间设计的五个步骤:

- 确定域的数量。
- 设计并命名树结构。
- 设计组织单位( Organizational Unit ,OU)的层次结构。
- 设计工作站和服务器的命名约定。
- 为用户和组制定规划。

遵循这些步骤,你便能实现本章的两大主要目标:

- 提出一套 Active Directory 命名空间设计方案,以反映你的业务结构。
- 通过更充分地利用灵活性更高的组织单位,将域的数量降至最低。

尽管我们已经向你展示了如何着手设计 Active Directory 安装,但后续仍有很长的路要走。按照此处给出的指导原则,设计域、树、林的命名空间以及内部 OU 结构,意味着你应该已经获得了一个基线结构模板,它能在前述约束条件下体现你的业务模型和需求。希望此设计对你的组织而言是合理的,并且易于管理。

不过,设计的其余部分仍需完成。你需要审视站点( Site )之间的底层网络链路,以及它们会如何影响你的复制决策。接下来,你需要处理如何根据组策略对象( Group Policy Object ,GPO)、安全委派和审核、架构更改等,修订初始命名空间设计这一课题。随后,我们将转向设计 DC 之间相互通信时所使用的物理站点拓扑。

---

## 第 14 章 创建站点拓扑

正如我们在第 6 章中提到的，复制涉及两个方面：

- 数据如何在域控制器之间现有链接网络中复制
- 知识一致性检查器( Knowledge Consistency Checker )如何生成并维护域控制器之间的复制链接，包括*站点内*和*站点间*

我们已在第 6 章中介绍了前者，这里将介绍后者，并进一步说明如何在 Active Directory 中正确设计组织网络基础设施的表示。

### 14.1. 站点内与站点间拓扑

在活动目录站点中，存在两种截然不同的复制连接类型：*站点内*（站点内部）和*站点间*（站点之间）。活动目录中有一个名为*知识一致性检查器*（Knowledge Consistency Checker，KCC）的服务，负责自动在站点内域控制器之间生成复制连接。KCC 也会自动为你创建站点间连接，但前提是管理员已指定两个站点应通过*站点链接*相连。KCC 及其所创建的连接对象的每一个方面都是可配置的，因此你可以通过调整各种选项来控制哪些内容已自动创建，以及哪些内容将自动创建。

请注意，KCC（每15分钟运行一次并创建复制拓扑的进程）与复制过程本身之间存在显著区别。KCC 不以任何方式参与实际数据的常规复制工作。沿 KCC 所创建连接的站点内复制使用通知过程来宣告变更已发生——每个域控制器负责将其变更通知给其复制伙伴。如果在六小时内完全没有发生任何变更，复制过程会自动启动，以确保没有遗漏任何内容。另一方面，站点间复制默认不使用通知过程。相反，站点间复制依赖计划来传输更新，并使用压缩来减小总流量大小。

#### 知识一致性检查器( Knowledge Consistency Checker ,KCC)

站点内的域控制器( Domain Controller ,DC)之间的连接由 KCC 创建。这些连接使用随机 GUID 作为唯一标识符，并在 Active Directory 中表示为*连接对象*。当必须连接不同站点之间的域控制器时，站点间拓扑生成器( Intersite Topology Generator ,ISTG)会自动在这些域控制器之间于 Active Directory 中创建连接对象。在每个站点内，都会指定一个 ISTG，通过 KCC 进程为该特定站点生成站点间拓扑。

ISTG 需依赖 Active Directory 网络中存在的站点链路( Site Link )，才能在不同站点中的域控制器之间创建连接。站点链路是一种由管理员定义的构造，通常表示 Active Directory 部署所依托的网络拓扑。本章稍后将详细介绍站点链路。ISTG 无法自动在两个站点之间创建链路的原因有两个。首先，ISTG 不知道您希望连接哪些站点。其次，ISTG 不知道您希望使用哪种复制传输协议。

KCC 在每个 DC 上每 15 分钟本地运行一次。默认时间间隔可以更改，如有需要，也可以按需手动启动（请参阅侧边栏“触发 KCC 和 ISTG”）。如果我们在新域中创建两台分别名为 Server A 和 Server B 的域控制器，KCC 将在每台服务器上运行以创建链路。每个 KCC 的任务是创建一条仅定义入站复制的链路。Server A 上的 KCC 将定义来自 Server B 的入站链路，而 Server B 上的 KCC 将定义来自 Server A 的入站链路。KCC 为每个复制伙伴仅创建一条入站链路，因此，例如 Server A 永远不会从 Server B 获得两条自动生成的入站链路。



触发 KCC 和 ISTG

KCC 和 ISTG 都可以使用 *repadmin* 命令行工具按需强制运行。

要强制 KCC 在本地域控制器上运行，请运行以下命令：




```
repadmin /kcc
```


要强制 KCC 在远程域控制器 *coho-chi-adc01.cohovines.com* 上运行，请运行以下命令：




```
repadmin /kcc coho-chi-adc01.cohovines.com
```


要强制 ISTG 在本地域控制器上运行，请运行以下命令：




```
repadmin /istg
```


要强制 ISTG 在远程域控制器 *coho-chi-adc01.cohovines.com* 上运行，请运行以下命令：




```
repadmin /istg coho-chi-adc01.cohovines.com
```

知识一致性检查器( Knowledge Consistency Checker ,KCC)不会为所有命名上下文( Naming Context ,NC)创建一个拓扑,也不会为每个 NC 分别创建一个拓扑。配置命名上下文( Configuration Naming Context )和架构命名上下文( Schema Naming Context )共享一个复制拓扑,因此 KCC 会为这两者一起创建一个拓扑。KCC 还会按每个域/命名上下文分别创建另一个拓扑。由于架构和配置 NC 的作用域为全林,KCC 需要跨站点链接( Site Link )复制对这些项的更改。KCC 需要为这两个 NC 一起维护一个跨越所有域的全林拓扑。但是,除非某个域设置为跨越多个站点,否则特定域的拓扑将仅由站点内连接( intrasite connection )组成。如果该域确实跨越多个站点,KCC 就需要跨这些站点创建复制拓扑。

#### KCC 自动生成站点内拓扑

对于每个命名上下文，KCC 在站点内的域控制器之间构建一个双向的复制连接环。环上的伙伴之间会创建上游和下游连接，但 KCC 也可以跨环创建额外的连接。这些连接的创建基于一条规则：站点内任何 DC 与同一站点中其他任何 DC 之间的复制跳数不得超过三跳。KCC 这样做是为了保证站点内某个 NC 的理论最大收敛时间。一般来说，在站点内部，该收敛时间大约为一分钟。如果您想修改收敛速度，请参阅侧边栏“修改复制收敛间隔”。例如，当您向站点中为某个域添加新的 DC 时，它们会被直接插入环中。由于三跳规则的限制，当您添加第八个 DC 时，KCC 必须至少添加一条跨环连接。下面让我们更详细地了解这一过程。



修改复制收敛间隔

如果您想更改站点内的默认复制间隔，可以通过修改特定域控制器上的注册表来实现，也可以在 Active Directory 中设置相应的值，使承载给定命名上下文的所有域控制器都受到影响。

如果您想在特定域控制器上设置这些值，请在 `HKLM\SYSTEM\CurrentControlSet\Services\NTDS\Parameters` 项下创建或修改以下注册表值（`REG_DWORD` 类型）：

- 要更改在通知发起写入的第一个变更通知伙伴之前的等待时间，请设置 `Replicator notify pause after modify (secs)`。默认值为 15 秒。
- 要更改在通知发起写入的每个后续变更通知伙伴之后的等待时间，请设置 `Replicator notify pause between DSAs (secs)`。默认值为 3 秒。

如果您想针对某个给定命名上下文进行全局性的时间调整，请在特定 NC 的交叉引用对象上设置以下属性：

- `msDS-Replication-Notify-First-DSA-Delay`
- `msDS-Replication-Notify-Subsequent-DSA-Delay`

这会影响所有复制该 NC 的域控制器，因此不像注册表设置那样具有针对性。

##### 两台服务器

对于两台域控制器( Domain Controller ,DC)的情况,我们一开始只有一台 DC,即服务器 A。当服务器 B 被提升为域的第二台 DC 时,*dcpromo* 过程会使用服务器 A 作为 Active Directory 信息的来源,以获取服务器 B 上的域、架构和配置命名上下文( naming context ,NC)。在提升过程中,配置容器( Configuration container )从服务器 A 复制到服务器 B,服务器 B 上的知识一致性检查器( Knowledge Consistency Checker ,KCC)会创建表示服务器 A 的相关入站连接对象( incoming connection object )。随后,服务器 B 通知服务器 A 其存在,服务器 A 相应地创建表示服务器 B 的入站连接对象。现在,使用这些连接对象对所有 NC 进行复制。虽然每个 NC 的复制是单独进行的,但此时所有三个 NC 都使用相同的连接对象。

##### 三台服务器

之后,在服务器 C 上启动 *dcpromo* 过程。服务器 C 使用 DNS 查找并选择一台现有 DC 作为提升伙伴。目前,我们假设它选择了服务器 B。在提升过程中,配置容器从服务器 B 复制到服务器 C,服务器 C 创建表示服务器 B 的相关入站连接对象。随后,服务器 C 通知服务器 B 其存在,服务器 B 相应地创建表示服务器 C 的入站连接对象。现在,使用这些连接对象对所有 NC 进行复制。

目前,服务器 A 和服务器 B 之间以及服务器 B 和服务器 C 之间存在双向链接。服务器 A 和服务器 C 之间没有链接,但 KCC 必须为复制创建环形拓扑。因此,一旦服务器 B 对服务器 C 执行完全复制,服务器 C 就会从配置 NC 中获知服务器 A。然后,服务器 C 的 KCC 会为服务器 A 创建一个入站连接对象。服务器 A 现在通过以下两种方式之一发现服务器 C:

- 服务器 A 从服务器 B 请求更新,并识别出一个新的 DC。
- 服务器 C 从服务器 A 请求更改,从而使服务器 A 能够识别出新的 DC。

服务器 A 现在为服务器 C 创建一个入站连接对象。这完成了服务器 A 到服务器 B、服务器 B 到服务器 C、服务器 C 到服务器 A 的循环。

##### 四台服务器

服务器 D 加入，提升过程随即开始。它选择服务器 C 作为连接对象。服务器 D 最终为服务器 C 创建了传入连接对象。同时，服务器 C 也为服务器 D 创建了传入连接对象。此时，你不仅拥有上一节提到的循环，还新增了服务器 C 到服务器 D 的双向连接。关于此拓扑结构，请参见图 14-1。




![Adding a fourth DC to a site](./image/14.%20Creating%20a%20Site%20Topology/httpatomoreillycomsourceoreillyimages1663492.webp)


图 14-1. 向站点添加第四台域控制器

服务器 D 的知识一致性检查器( Knowledge Consistency Checker ,KCC )现在利用从服务器 C 复制来的新数据来遍历现有拓扑。它明白必须延续环形拓扑，并且由于已与服务器 C 相连，服务器 D 需要为服务器 C 的一个伙伴创建传入连接对象。在这个场景中，它选择了服务器 B。因此，服务器 D 的 KCC 为服务器 B 创建了一个传入连接对象。接着，服务器 D 向服务器 B 请求变更。后续过程可能有多种走向，我们仅演示其中一种情景。

服务器 B 现在知道了服务器 D 的存在。服务器 B 的 KCC 运行后，意识到不再需要连接到服务器 C，于是删除了该连接，并直接创建了一个新的连接到服务器 D。最后，随着复制沿现有链接在环中传播，服务器 C 注意到它从服务器 B 收到的传入链接已失效，并将其移除。至此，你就拥有了一个简单的环形结构，如图 14-2所示。




![Ring of four DCs](./image/14.%20Creating%20a%20Site%20Topology/httpatomoreillycomsourceoreillyimages1663493.webp)


图 14-2. 四台域控制器的环形拓扑

##### 八台服务器

一旦连接在一起的服务器达到八台，如果要维持三跳规则( three-hop rule )，就需要在环上增加更多链接。查看图 14-3，即可看到这一点。如果不存在跨环链接( cross-ring link )，某些服务器之间就会相隔四跳。知识一致性检查器( Knowledge Consistency Checker ,KCC)通过让最后加入环的服务器做出初始选择，来确定希望链接哪些服务器。因此，如果服务器 H 是环中最新的服务器，它就知道服务器 D 相隔四跳，并与服务器 D 建立连接。当服务器 D 的 KCC 收到服务器 H 已链接到它的新数据时，它会做出对等响应，并创建到服务器 H 的链接。




![Ring of eight DCs](./image/14.%20Creating%20a%20Site%20Topology/httpatomoreillycomsourceoreillyimages1663494.webp)


图 14-3. 八个域控制器( Domain Controller ,DC)组成的环

然而，这并未完全解决问题。考虑服务器 B 和服务器 F：它们彼此仍然相隔四跳。现在，KCC 会在这些服务器对之间创建链接，以维持三跳规则。



##### 接下来会怎样？

现在，我们已经了解了 KCC 用于在 DC 之间进行站点内链接生成( intrasite link generation )的机制。然而，情况并非全部如此。请记住，Active Directory 可以在每个站点( site )中拥有多个域( domain )，因此，如果我们将 *contoso.com*（同一林( forest )中的新域）添加到同一站点，甚至添加 *europe.cohovines.com*（新子域( child domain )），会发生什么？两者的答案相同，并且都基于命名上下文( Naming Context ,NC )：

- 架构( Schema ) NC 和配置( Configuration ) NC 在整个企业范围内复制，并且共享同一个复制拓扑( replication topology )。尽管它们分别复制，但复制是沿着相同的链接进行的。
- 每个域仅在域范围内复制，因此两个域的域拓扑仍保持它们之前相同的环状结构。

两个域集成后，KCC 为 *cohovines.com* 和另一个域生成的拓扑保持不变。然而，分别存在于两个域上的、由 KCC 生成的配置/架构复制拓扑，将按照标准 KCC 规则形成自己的环，并涵盖这两个域。

总之，当站点中有多个域时，每个域都有自己的、由 KCC 生成的拓扑来连接其 DC，但站点中的所有 DC——无论来自哪个域——都会在一个表示架构/配置复制的独立拓扑中建立连接。

#### 站点链接：站点间拓扑的基本构建块

拥有站点固然好，但若要复制任何数据，您必须能够将它们连接起来。这种类型的站点间连接被称为*站点链接*。站点链接由管理员手动创建，用于指示两个或多个站点之间可以进行复制。如果底层物理网络已经将多个站点连接在一起，站点链接可以连接两个以上的站点；然而，如果将每个站点链接限制为两个站点，通常更容易可视化和控制复制连接。

站点不必通过物理网络连接即可进行复制。复制可以通过来自不同站点的任意两台主机之间的多条链接进行。然而，为了让Active Directory能够理解应该在这两个站点之间进行复制，您必须在它们之间创建站点链接。

我们提到过站点链接有成本（参见第6章），但这并不是它们唯一的属性。事实上，站点链接有四个重要属性：

- **名称**

  站点链接的标识名称。

- **成本**

  站点链接的整数权重，表示该链接相对于其他现有链接的优先级。成本越低越优先；成本越高越不优先。

- **计划**

  可用于开始复制的时间。复制不会在计划指定的时间窗口之外开始。

- **传输**

  沿此链接进行复制所使用的协议。

##### 成本

由于每个链接都有成本，可以通过将各个路由的成本相加来计算经过任何一条路由的总成本。如果两个站点之间存在多条路由，知识一致性检查器( Knowledge Consistency Checker ,KCC)将自动识别最低成本的路由并将其用于复制。如果任意两个站点之间只存在一条路由，则站点链接成本无关紧要。

##### 计划( Schedule )

链路( Link )上的计划表示允许通过该链路发起复制( Replication )的时间段。域控制器( Domain Controller ,DC)还会维护其允许执行复制的时间。显然，如果两个 DC 与某条链路的时间不重叠，就绝不可能进行复制。

在站点链路( Site Link )上，复制的计划开始时间和停止时间之间，服务器可以打开所谓的*窗口*( window )，以便进行复制。只要通过该链路复制的任一服务器可用于复制，该站点链路与该服务器之间就会打开一个复制窗口。只要需要彼此复制的两台服务器的窗口重叠，就可以进行复制。一旦某台服务器不再可用于复制，该服务器的窗口就会被移除。一旦站点链路不再可用，所有窗口都会关闭。

> **警告**：

计划仅定义复制何时可以开始。复制一旦开始，便不会停止，直至完成，无论站点链接( Site Link )上定义的计划如何。

##### 传输

站点链接当前可以使用两种传输机制进行复制:

- 目录服务远程过程调用( Directory Service Remote Procedure Call ,DS-RPC)
- 站点间消息传递简单邮件传输协议( Inter-Site Messaging Simple Mail Transport Protocol ,ISM-SMTP)

使用 DS-RPC 的站点链接意味着，希望通过该站点链接进行复制的服务器可以使用 RPC 跨链接建立直接的同步连接。由于传输协议是同步的，连接上的复制由两个伙伴实时进行并协商。这是实时链接的常规连接类型。在某些场景中，某些站点可能可用性难以预测，或者其 WAN 连接非常不可靠或延迟很高。在这些场景中，SMTP 复制可能更为合适。

SMTP 连接器( SMTP Connector )是使用 ISM-SMTP 传输的站点链接的称呼，它允许伙伴域控制器( Domain Controller ,DC)将各自更新加密后以电子邮件形式互相发送。在此场景中，Active Directory 假定这两个站点之间已具备底层的基于 SMTP 的连接机制。如果没有，则必须自行搭建一个，该功能才能正常工作。如果连接已就绪，SMTP 连接器会假定现有的底层邮件路由结构将负责处理邮件的传输方式。为此，使用 SMTP 连接器的站点链接会忽略计划选项卡，因为它会通过底层系统自动发送和接收更新，只要电子邮件系统自身发送和接收邮件即可。

SMTP 连接器消息使用证书进行加密，因此要加密消息，需要在将参与 SMTP 复制的域控制器上安装专用证书。如果你的组织中在 Windows 上运行有企业证书颁发机构( Enterprise Certification Authority ,CA)，则可以自动请求并安装这些证书。否则，请参阅 Microsoft 知识库文章 [321051](http://bit.ly/Y8htDl)，了解如何从第三方 CA 请求并安装证书。

> **注意**：

SMTP 复制协议不能用于域命名上下文( Domain Naming Context ,NC )复制。但它可用于复制全局编录( Global Catalog ,GC )、架构和配置信息。这意味着,使用慢速链路的多站点域必须使用 RPC 进行域复制。

##### ISTG 何时介入

为生成站点间复制拓扑,站点间拓扑生成器( Inter-Site Topology Generator ,ISTG )会主动使用站点链接开销( Site Link Cost )来确定用于复制目的的路径。如果组织中存在一系列稳定的站点链接,并且添加了一条开销更低的新路径,ISTG 将在适当情况下切换使用新链接,并删除旧的连接对象( Connection Object )。知识一致性检查器( Knowledge Consistency Checker ,KCC )创建的网络连接称为*最小开销生成树( Minimum-Cost Spanning Tree )*。

#### 站点链接桥:站点间拓扑的第二大构建块

站点链接桥( Site Link Bridge )仅在已禁用 Active Directory 中“桥接所有站点链接”选项的场景下才需要。我们已在第 6 章中讨论了可能需要站点链接桥的示例。概括而言,当您希望告知 KCC 可以在两个域控制器( Domain Controller ,DC )之间创建直接复制连接时(根据 Active Directory 中的拓扑信息,这两个域控制器并非直接相连),站点链接桥即成为必要。

考虑图 14-4中的示例拓扑,并就本次讨论而言,假设示例拓扑中已禁用“桥接所有站点链接”,且底层网络允许 Chicago 与 New York 之间通信。基于此信息,Chicago 与 New York 无法直接相互复制。相反,Chicago 必须与 Denver 复制,New York 也必须与 Denver 复制。如果 Denver 域控制器( *DC02* )发生故障,则 Chicago 与 New York 之间将不存在复制。但是,如果您定义一个包含 Chicago-Denver 与 New York-Denver 站点链接的站点链接桥,那么当 Denver 域控制器不可用时,Active Directory 将能够在 Chicago 与 New York 之间直接创建复制连接。

![Site link bridging scenario](./image/14.%20Creating%20a%20Site%20Topology/httpatomoreillycomsourceoreillyimages1663495.webp)

图 14-4. 站点链接桥场景

现在您已经了解了站点链接与站点链接桥的工作方式,接下来我们来看如何设计站点及其复制链接。

### 14.2. 为复制设计站点和链接

在为网络设计复制策略时,真正重要且具有决定性作用的因素只有一个:你会通过网络复制多少流量,以及在多长时间内完成复制?然而,创建站点并非仅仅为了复制。站点的存在还有另一个目的:将一组组计算机归类在一起,以便于定位数据、查找最近的域控制器( Domain Controller ,DC )进行身份验证、查找最近的分布式文件系统( Distributed File System ,DFS )共享装载点、定位 System Center Configuration Manager 分发点,或在 Exchange 组织中路由邮件。本节将介绍为复制设计站点和链接所涉及的步骤。



#### 步骤 1:收集网络的背景数据

在着手设计站点和广域网( Wide Area Network ,WAN )拓扑之前,你需要获取现有网络基础设施的拓扑图。该拓扑图应包含公司拥有计算机的所有物理位置,以及这些位置之间的每一条链接。此外,还应注明每条链接的速度和可靠性。

另外,你还应记录与所标注站点对应的所有子网。

#### 第 2 步：规划域控制器( Domain Controller ,DC)的位置

规划域控制器的放置相当容易，但确定要使用多少台 DC 则完全是另一回事。

##### 将域控制器放在何处

域( Domain )中的每台工作站都位于其已知的单个站点( Site )中。当用户尝试在给定工作站上登录到域时，该工作站会向本地站点中的一台 DC 进行身份验证，而该 DC 最初是通过 DNS 查询定位的。如果本地站点中没有可用的 DC，工作站会借助站点拓扑( Site Topology )查找远程站点，并经过与该站点中某台 DC 的协商过程，要么使用该 DC 进行身份验证，要么被重定向到更合适的域控制器。

这一考虑因素决定了 DC 的放置。对于满足以下任一条件的所有站点，你应为每个域放置一台用于身份验证的 DC：

- 站点到特定域的链路速度不足以满足登录需求。
- 站点的链路速度或许足以满足登录需求，但对于特定域，你不希望通过这些链路进行身份验证。
- 站点中存在需要域控制器快速响应的应用程序（如 Exchange）。
- 你有总体业务要求，需确保无论 WAN 链路状态如何，该站点中的身份验证和目录( Directory )信息始终可用。

还需要结合站点中的用户和工作站数量来考虑第一点和第二点。如果站点中的工作站数量足以产生占用大部分可用 WAN 带宽的登录流量，那么你可能不得不将本地域控制器放置在该站点。

##### 应有多少台域控制器

确定在一个站点中放置多少台 DC 从来都不是易事。如果你有一台 Windows 服务器已为 500 名重度用户提供服务，并接近其负载极限，它还能同时快速地对另外 100 名用户进行身份验证吗？性能强大的服务器可以同时验证数百或数千名用户，但即使这类服务器，如果已经负载很重，也会不堪重负。

有些情况很难准确评估，例如基于 LDAP 的应用程序使用 DC 所带来的影响。通常，你并不了解某个给定应用程序使用目录的具体方式，因此最终只能在需要多少台 DC 的问题上采取“观望”态度，并希望使用率不会高到让用户察觉到任何性能问题。

> **注意**：

Exchange 是一个应用程序示例，其随附的最佳实践指南说明了需要多少台全局编录服务器( Global Catalog Server ,GC )。Exchange 以 Exchange CPU 核心与 GC CPU 核心的比率来定义这些最佳实践。

要明确决定一个站点( Site )中需要多少台域控制器( Domain Controller ,DC )，通常唯一的方法就是先尝试最佳实践和推荐指南，然后随着模式逐渐清晰，再根据实际情况调整实际数量。这样，你应当能够自行判断可能需要多少台 DC 用于身份验证和其他用途。

在规划域控制器部署时，重要的是预先定义你将使用什么标准来判断站点中是否应增加一台域控制器。这通常取决于性能指标，例如平均 CPU 利用率或磁盘利用率。

##### 将域控制器放置在多个站点中

你提升的每台域控制器都只能属于一个站点。但在某些情况下，你可能希望将一台域控制器配置为覆盖多个站点。例如，你可能希望确保来自多个站点的工作站都使用一台 DC 进行身份验证。域控制器默认会执行一种称为*自动站点覆盖( automatic site coverage )*的行为，该行为会注册必要的 DNS 记录，以便一台域控制器为多个站点提供服务。

当站点中没有域控制器时，自动站点覆盖很重要，因为这些站点中的客户端仍然需要进行身份验证并访问 Active Directory。在分支机构场景中，通常最好修改此行为，使分支机构的域控制器不覆盖其他站点。你可以在 Windows 2003 分支机构 [部署指南](http://bit.ly/WWNO2n) 的 第 4 章 中找到有关配置此行为的详细信息。对于 Windows Server 2008 R2 及更高版本的域控制器，不再需要配置此行为。

> **注意**：

你可以通过修改注册表值，手动将域控制器( Domain Controller ,DC)配置为服务多个站点( Site )。为此，请在将覆盖多个站点的服务器上编辑注册表，并在 `HKLM\SYSTEM\CurrentControlSet\Services\Netlogon\Parameters` 项下添加一个名为 `SiteCoverage` 的 `REG_MULTI_SZ` 值。将要让该服务器覆盖的站点名称添加到此值中。

一般来说，应计划依赖自动站点覆盖；不过，此手动功能用于需要例外处理的情况。



#### 步骤 3:设计站点

根据网络图，你需要以网络图的一对一映射为起点，绘制站点结构并为每个站点命名。如果你有 50 个物理 WAN 位置，就会有 50 个站点。如果其中只有 30 个将用于 Active Directory，你可能认为没有必要在 Active Directory 中包含整组站点。但如果你确实包含了整组站点，则以后将整个网络可视化，并向这些位置添加客户端或服务器会容易得多。



> **注意**：

绘制 Active Directory 拓扑时，站点通常用椭圆形表示。

请记住，站点的定义较为宽松：它是一组连接良好的子网( Subnet )（“连接良好”通常意味着约 10 Mbps 的 LAN 速度）。站点中不必包含域控制器；它可以完全由客户端组成。如果你有两栋建筑物（或整个园区）通过 10/100 Mbps 链路连接，那么整个位置就是一个站点。

这并不是一条硬性规定。按常规规则，通过 2 Mbps 链路连接的两个位置代表两个不同的站点。但是，如果愿意，你可以将多个网络组合成单个站点。不过，你必须认识到，与创建两个站点和一个站点链接( Site Link )相比，这样会产生更多复制，因为两个物理位置中的 DC 都会维护站点内复制环形拓扑。如果创建了两个站点和一个站点链接，则只有两台桥头服务器( Bridgehead Server )会相互复制。

总而言之，我们建议默认情况下为 WAN 上的每个物理位置创建一个站点，除非你认为不需要在两个物理位置之间隔离复制。



> **注意**：

此一般建议的一个反例是数据中心( Data Center )之间的高速链路。有些组织部署了多个物理上独立的数据中心，这些数据中心在网络上是同一个逻辑位置。在这种情况下，将这些数据中心表示为单个站点可能是有意义的。

#### 步骤 4：创建站点链接

现在，所有站点已在纸面上规划完毕，接下来需要考虑链接问题。此步骤中，我们将确定站点间如何连接，以及在何种程度上需要在活动目录( Active Directory )中复制物理拓扑结构。此外，还要识别出那些需要非标准复制计划的站点链接，以及站点链接复制的频率。

首要考虑的是如何命名站点链接。建议每个站点链接仅限连接两个站点，并采用便于识别参与站点的命名约定。一个行之有效的策略是，在名称和描述属性中都包含这两个站点的名称，但顺序相反。例如，站点链接的名称可设为 *SiteA-SiteB* ，描述则为 *SiteB-SiteA* 。这样，在活动目录站点和服务中按任一字段排序时，都能轻松看出某个站点涉及哪些站点链接。

在为站点链接分配成本时，应力求在整个部署中采用统一的成本值标准体系。实现这一成本模型有多种方法，不一定存在绝对“正确”的做法。有些组织倾向于按类别分配链接成本，比如中心站点间的链接设定一种成本，中心与分支间的链接设定另一种，而两个分支间的链接则设定第三种。还有些组织选择将站点链接成本与底层广域网( WAN )连接的速度关联。请记住，无论采用哪种方式，如果到达某个站点仅有一条路径，那么成本就无关紧要了。

> **注意**：

关于利用广域网速度来填充站点链接开销值的讨论，请参阅[此网站](http://bit.ly/ZZX99C)。该博客文章还包含一个电子表格，提供了许多常见广域网链路速度的开销。

频率简单来说就是站点链接上复制发生的频次。此值以分钟为单位指定，范围从15分钟到1周。您应根据站点链接两端 Active Directory 数据必须保持的最新程度要求，以及复制将对底层广域网链路造成的负载量来选择此值。如果您的更改量不足以产生大量复制流量，那么将频率间隔设置得很长可能对您并无益处。

计划是站点链接上的最后一个可配置选项。站点链接计划定义了允许复制启动的时间窗口。“启动”在这里是个关键词，因为一旦复制开始，它将不会停止，直到完成为止，无论站点链接计划如何。在处理某些时间段内饱和或不可用的广域网链路时，站点链接计划非常有用。



#### 步骤5：创建站点链接桥

如果您选择禁用“桥接所有站点链接”选项，则需要检查您的拓扑是否需要站点链接桥来帮助站点间拓扑生成器( Inter-Site Topology Generator ,ISTG )生成站点间拓扑。在许多中心辐射型拓扑中，此步骤最终可能是不必要的，但您需要检查自己的拓扑以确认。

### 14.3. 设计示例

在考虑了这五个步骤之后，让我们再次审视上一章中的三个示例，看看它们的站点拓扑将需要哪些要素。

#### Tailspin Toys

Tailspin Toys 是一家在北美拥有约 3,000 名员工的组织。Tailspin Toys 各位置分布着约 4,000 台客户端计算机和数百台服务器。办公人员分布在美国和加拿大的多个城市以及居家办公地点。制造业务在墨西哥开展。



##### 第 1 步:收集网络背景数据

Tailspin Toys 网络相对现代化,与美国和加拿大所有办事处之间均具有快速可靠的连接。一些制造工厂的连接可靠性较低。所有制造站点均被视为业务关键型站点,并且必须能够在发生网络中断时独立运行一段时间。

该组织的主数据中心位于旧金山。灾难恢复站点位于亚特兰大。网络拓扑如图 14-5所示。




![Tailspin Toys wide area network topology](./image/14.%20Creating%20a%20Site%20Topology/httpatomoreillycomsourceoreillyimages1663496.webp)


图 14-5. Tailspin Toys 广域网( Wide Area Network ,WAN )拓扑



##### 第 2 步:规划域控制器( Domain Controller ,DC)位置

根据图 14-5中的网络图以及历史网络性能信息,Tailspin Toys 决定将可写域控制器放在其旧金山和亚特兰大数据中心,以便为美国各地办事处中的客户端以及数据中心中托管的应用程序提供服务。

鉴于制造运营的关键性、公司策略以及 WAN 可靠性,每个制造站点都放置一台只读域控制器( Read-Only Domain Controller ,RODC)。该 RODC 配置为缓存该站点中所有用户、服务帐户和计算机的密码。



##### 第 3 步:设计站点

Tailspin Toys 当前未使用任何既具有站点感知( site-aware )能力、又部署到没有域控制器的站点中的应用程序。因此,为每个托管域控制器的位置创建站点对象( Site Object )和相应子网。旧金山站点还配置了美国各个分支办事处的子网对象( Subnet Object )。

##### 步骤 4：创建站点链路( Site Link )

图 14-6 展示了 Tailspin Toys 林的站点链路拓扑。表 14-1 展示了站点链路配置。每条通往 San Francisco 的连接都配置了一条站点链路。由于每个站点只有一条路径，站点链路开销并不重要。每条站点链路都分配了标准化的开销值。数据中心之间的所有链路开销均设为 100。数据中心与分支站点之间的所有链路开销均设为 200。




![Tailspin Toys site topology](./image/14.%20Creating%20a%20Site%20Topology/httpatomoreillycomsourceoreillyimages1663497.webp)


图 14-6. Tailspin Toys 站点拓扑



表 14-1. Tailspin Toys 站点链路

| 包含的站点                  | 名称                         | 描述                          | 开销 | 频率                                    | 计划     |
| -------------------------- | ---------------------------- | ---------------------------- | ---- | --------------------------------------- | -------- |
| San FranciscoAtlanta       | San Francisco-Atlanta        | Atlanta-San Francisco        | 100  | 15 分钟（已启用更改通知）                | 始终     |
| San FranciscoMexico City   | San Francisco-Mexico City    | Mexico City-San Francisco    | 200  | 180 分钟                                | 始终     |
| San FranciscoCiudad Juárez | San Francisco- Ciudad Juárez | Ciudad Juárez -San Francisco | 200  | 180 分钟                                | 始终     |
| San FranciscoChihuahua     | San Francisco-Chihuahua      | Chihuahua-San Francisco      | 200  | 180 分钟                                | 始终     |

如表 14-1所示，San Francisco 与 Atlanta 数据中心之间的高速链路也启用了更改通知。这可确保两个数据中心中的域控制器( Domain Controller ,DC )始终保持几乎同步。由于制造站点的只读域控制器( Read-Only Domain Controller ,RODC )对数据实时性的需求不高，因此这些站点链路的复制配置为每三小时（180 分钟）执行一次。

####  Contoso College

Contoso College 是一所高等教育机构,拥有约 3,500 名员工、30,000 名学生和 5,000 台计算机。所有用户和计算机均位于同一园区内。园区设有一个由中央 IT 组织管理的中央数据中心。为了提供集中化、可持续且可分布的目录服务,中央 IT 正在部署一个 Active Directory 林,以支持自动管理的用户帐户和组,并支持委派管理员获得可自行管理其资源的组织单位( Organizational Unit ,OU)。

##### 步骤 1:收集网络背景数据

Contoso College 园区由多栋建筑组成,所有建筑均通过高速光纤电缆连接到中央数据中心。中央数据中心是一个物理安全设施,配备备用电源。

##### 步骤 2:规划域控制器位置

由于整个 Contoso College 园区实际上是一个连接良好的单一局域网( Local Area Network ,LAN),因此可写域控制器( Domain Controller ,DC)将部署在中央数据中心。网络其他位置不再部署域控制器。

##### 步骤 3:设计站点

Contoso College 的林将是一个单站点林,所有域控制器均位于默认站点中。

##### 步骤 4:创建站点链接

由于该林为单站点林,因此无需创建任何站点链接( Site Link )。

#### Fabrikam

Fabrikam 是一家全球性大型组织，在全球 100 多个站点( Site )拥有超过 250,000 名员工和计算机。公司全球总部( Headquarters ,HQ )位于芝加哥。另有四个主要站点连接到总部，而较小的分支机构( Branch Office )则连接到这些主要站点：亚太地区、北美地区、南美地区和欧洲地区。小型站点通过速率从 64 kbps 到 T1 的链路连接到枢纽站点( Hub Site )；枢纽站点本身则通过各种更高速率的链路连接到总部。一些枢纽站点之间也相互连接。



##### 第 1 步：收集网络的背景数据

图 14-7 显示了 Fabrikam 网络拓扑( Network Topology )的高层概览。数据中心( Datacenter )之间的链路可靠，但有时会饱和。欧洲、亚太和芝加哥区域数据中心之间存在多条路径。通往南美分支机构以及亚洲部分办公地点的广域网( Wide Area Network ,WAN )链路通常缓慢、饱和且不可靠。这些站点通常还包含制造运营等业务关键功能。




![Fabrikam network topology](./image/14.%20Creating%20a%20Site%20Topology/httpatomoreillycomsourceoreillyimages1663498.webp)


图 14-7. Fabrikam 网络拓扑

Fabrikam 经常开设和关闭办公地点，并且由于拥有 100 多个办公地点，网络的子网( Subnet )布局经常变化。为处理此问题，Active Directory 团队每天晚上会从网络团队收到一个包含子网及其关联位置的逗号分隔值( Comma-Separated Values ,CSV )文件。自动化脚本会处理该 CSV 文件，并确保 Active Directory 子网信息与网络团队的数据匹配。



##### 第 2 步：规划域控制器( Domain Controller ,DC )位置

Fabrikam 计划在每个区域数据中心以及总部数据中心部署可写域控制器。由于芝加哥是网络上最居中的数据中心，PDC 模拟器( PDC Emulator )灵活单主机操作( Flexible Single Master Operations ,FSMO )角色持有者将放置在芝加哥。

如果分支机构满足以下任一条件，将向其部署只读域控制器( Read-Only Domain Controller ,RODC )：

- 站点中至少有 100 台计算机。
- 站点本地托管了与 LDAP 集成的应用程序，并且 WAN 链路不够可靠，或速度不足以满足应用程序的需求。
- 站点中开展制造运营等业务关键活动。

##### 步骤 3:设计站点

Fabrikam 在整个企业中部署了大量可感知 Active Directory 的应用程序,并采用自动化流程管理子网( Subnet )对象。网络中的每个物理位置都将部署一个对应的站点( Site )对象,即使该位置本地未承载域控制器( Domain Controller ,DC)也是如此。

##### 步骤 4:创建站点链路

站点链路( Site Link )拓扑将与 图 14-7 所示的广域网( Wide Area Network ,WAN)拓扑保持一致。数据中心之间的站点链路将启用更改通知( Change Notification )。其余所有 WAN 链路将根据可靠性和需求,以不同的频率进行复制。

开销属性( Cost Attribute )将与站点链路速度直接关联,以便反映部分位置之间的多条路径。[方法 C](http://bit.ly/ZZX99C) 将用于计算站点链路开销。具体而言,图 14-8 所示公式中将使用 38 400 000 000 位/秒( bit per second ,bps)的参考带宽。




![Inverse square root site link cost formula](./image/14.%20Creating%20a%20Site%20Topology/httpatomoreillycomsourceoreillyimages1663499.webp)


图 14-8. 站点链路开销的平方根反比公式

### 14.4. 其他资源

微软为需要部署分支机构环境的客户编写了一份出色的指南。分支机构部署是指拥有大量 WAN 站点、且各站点均需托管活动目录( Active Directory )本地副本的部署场景。例如,大型零售连锁企业设有一个总部和数百家零售门店,所有门店都连接到同一个林。如果你必须部署此类基础架构,那么绝对有必要查阅《Windows Server 2003 Active Directory 分支机构指南》,可在微软[网站](http://bit.ly/WWNO2n)上找到。尽管该指南是针对 Windows Server 2003 编写的,但仍然值得一读。

### 14.5. 总结

基于本章内容，你应已充分理解如何为活动目录( Active Directory ,AD)部署设计站点拓扑( Site Topology )，以及如何判断在任意给定站点中是否需要域控制器( Domain Controller ,DC)。AD 会利用站点拓扑进行复制，各种其他应用程序（例如 DFS 和 Exchange Server）也会利用站点拓扑。客户端也依赖站点拓扑来定位域控制器以进行身份验证。

知识一致性检查器( Knowledge Consistency Checker ,KCC)是在每个域控制器上自动运行的进程，用于生成底层复制连接。站点间复制连接会在站点内一台被指定为该站点站点间拓扑生成器( Intersite Topology Generator ,ISTG)的域控制器上生成。

规划站点拓扑需要充分理解底层网络，因为你需要考虑对站点( Site )、站点链路( Site Link )和站点链路桥( Site Link Bridge )的要求。站点表示你希望隔离复制和身份验证流量的不同网络位置。站点链路表示站点之间的连接，而站点链路桥为 KCC 提供有关站点链路之间传递性的提示，以便生成复制发生所需的连接。

下一章将讨论如何更新你的设计，以反映组织中组策略对象( Group Policy Object ,GPO)的要求。

---

## 第 15 章 规划组策略

本章深入探讨组策略对象( Group Policy Object ,GPO)，重点介绍如何有效地使用组织单位( Organizational Unit ,OU)和组来构建 Active Directory 部署，以便充分利用组织中所需的 GPO。

### 15.1. 使用 GPO 辅助设计组织单位结构

在第13章中，我们描述了活动目录( Active Directory )组织单位( Organizational Unit ,OU )层次结构的设计。我们还解释了其他因素对该设计的影响。影响 OU 结构的两个关键设计问题是权限委派和 GPO 放置。如果您决定将活动目录基础设施集中管理而非分布式管理，并且只使用少量主要在域范围内实施的 GPO（而非在许多 OU 上使用大量 GPO），那么您的 OU 结构几乎可以按任意方式排列。无论是根下有 400 个分支，还是一个容器包含所有内容，都不会有太大差别。然而，如果确实需要将特定对象的权限委派给特定的管理员集合，那么以有利于此类管理的方式构建域 OU 会更加合理。这并非必须如此，但这样做会使 OU 的使用变得容易得多。

例如，如果我们有 1,000 个用户和 10 个委派管理员，每人管理 100 个用户，我们可以将 1,000 个用户放在一个 OU 中，并授予 10 个管理员每人仅修改其所属 100 个用户的权限。但显然，这不是一个高效的系统。相反，更好的做法是创建 10 个 OU，每个 OU 中放置 100 个用户，授予每个管理员对其特定 OU 的权限。这样做更加合理，因为委派管理员可以非常容易地更改，访问权限的报告也更加简便，等等。常识和减少管理开销是这里最重要的因素。两种方案都可行，只是其中一种实现和维护起来要容易得多。



> **注意**：

权限委派在第16章中有更详细的介绍。

同样的基本原理也适用于 GPO。如果您需要将多个策略应用于多组用户，那么设置多个 OU 将使管理更加容易。然而，这并不总是可行的——例如，如果您理想中的 OU 结构与权限委派所需的结构相冲突，而后者又与您希望用于组策略的结构相冲突。

#### 确定策略领域

我们假设在您的组织内部，您将编写一份文档，描述您希望在活动目录( Active Directory )环境中使用的安全功能计划以及这些功能的具体实施方式。该文档的一部分将涉及 AD 的其他安全功能，例如 Kerberos、防火墙、权限等，但此处我们关注的是组策略对象( Group Policy Object ,GPO)。

首先，您需要确定希望通过 GPO 实现的总体策略目标。此时无需深入每个 GPO 设置及其具体值的细节。相反，您关注的是诸如“部署财务应用程序”和“限制桌面设置”之类的项目。当您确定每个总体策略领域时，需要注明它是应用于站点中的所有计算机或用户、单个域中的所有计算机或用户，还是用户和计算机账户的子集。如果对某些项目不确定，请将其归入多个类别。最终您会得到诸如“向法国的会计师部署财务应用程序”和“在欧洲限制桌面设置”之类的项目。

一旦构建了总体策略领域，您需要构建一个便于实施此策略设计的组织单位( Organizational Unit ,OU)结构。此时，您开始将计算机和用户放入各个 OU 中，并决定每个容器中的所有对象是都接收该策略，还是通过访问控制列表( Access Control List ,ACL)限制策略的应用范围。在此阶段，您可以问自己许多问题。为帮助您完成此过程，下一节的示例之后附有一组宽松的指导原则。

最终，文档需要明确指定要应用哪些 GPO 设置、为权限限制设置哪些组，以及 OU 结构将是什么样子。解释您所做任何决策的理由会有所帮助。

为使指导原则更具实际意义，我们将基于第 13 章中介绍的示例，展示如何以几种方式构建 GPO。

#### 设计组策略对象( Group Policy Object ,GPO )的指导原则

本节中，我们将提供一些指导原则，帮助您达成两个关键设计目标：

- 所有策略应迅速应用，以免用户因策略处理而感到明显影响。
- 所有策略应尽可能便于管理和维护。

基于这两个目标，我们来看一下这些指导原则：

- **以您觉得舒适的方式进行设计。**

  如本章后续所示，分别考虑用户组织单位( Organizational Unit ,OU )和计算机OU结构可能会使大型设计变得更容易。如果您想同时处理它们，并且网络规模足够小，可以轻松做到，那也没问题。如果不是，尝试将它们视为独立的组策略领域。

- **尽可能限制适用的策略数量。**

  在理想情况下，这点并不重要。但在现实世界中，您拥有的策略越多，客户端除了正常的登录/启动之外，需要进行的处理就越多，完成过程所需的时间也就越长。如果有多项策略从树中的同一位置应用于一个对象，考虑将它们合并为单个对象的可能性。如果登录/启动期间应用的策略数量超过了客户端能在合理时间内处理的数量，您需要考虑减少或合并这些策略。如果您需要应用大量包含许多设置的策略，导致登录时间延长至五分钟，但您认为为了达到这种策略水平是可以接受的，那也无妨。归根结底，只有您自己知道可以接受什么，您需要在这个领域进行自己的测试以满足您的限制条件。如果必须让客户端在四秒内登录，您就必须在这个限制内工作。微软喜欢建议组织单位嵌套深度不超过10层，以确保您不会使用过多的GPO。众所周知，这并没有太大帮助。如果在一个站点应用一个GPO，在一个域应用一个，以及在五个组织单位各应用一个，那总共只有七个GPO。如果每个层级应用10个，那就是70个。因此，重要的不仅是您的组织单位结构嵌套有多深，还有您在每个层级应用了多少策略。

- **使用安全组来定制访问权限。**

虽然你可以设置访问控制列表( Access Control List ,ACL )来允许或拒绝将策略应用到单个用户或计算机，但只要能够使用组，使用组来实现这一点会更合理。使用组可以将所有策略访问权限保留在一个对象中，并使复杂系统更易于管理。为简化故障排除，请尽量避免使用拒绝功能，而应坚持显式允许组。

- **限制使用阻止继承/强制策略。**

  除非你非常确定这是解决问题的正确方法，否则应非常谨慎地在树中的位置阻止继承。简单阻止继承所造成的影响会迅速扩大，因为你会遇到需要覆盖该阻止的策略区域。如果你经常阻止并覆盖，原本精心设计的系统可能变得很难维护。这并不是说永远不应使用这些选项；只是在使用时要谨慎。

- **缩减组织单位( Organizational Unit ,OU )设计。**

  如果愿意，你可以缩减 OU 设计，并更多地使用组来控制对特定策略的访问。两者都是完全有效的解决方案，你应使用自己更习惯的那一种。请记住这条公理：在保持或增加组策略对象( Group Policy Object ,GPO )数量的同时，对 OU 结构缩减得越多，通过组进行控制的需求就越大。

- **避免使用跨域 GPO 链接。**

  如果跨域链接 GPO，客户端必须联系 GPO 所在域中的域控制器( Domain Controller ,DC )，以下载有关该 GPO 的信息。除非客户端与外部域之间的链接速度非常快且可用带宽充足，否则应在目标域中复制该 GPO 的功能，而不要依赖跨域链接。

- **确定 GPO 的优先级。**

请记住，可以在站点、域或组织单位( Organizational Unit ,OU)级别为多个组策略对象( Group Policy Object ,GPO)的应用设置优先级。这种策略应用顺序可以为管理员的工具包增添有用的选项。例如，如果需要对一组用户撤销默认作为更大设置集一部分应用的特定设置，可以创建一个带有该组访问控制列表( Access Control List ,ACL)的新 GPO，并让其在优先级列表中应用，以取消之前的所有设置。此解决方案允许你覆盖部分先前设置，而无需创建两个 GPO：一个包含适用于所有人的设置，另一个仅供该组使用。前一种解决方案允许你稍后向主 GPO 添加设置，并仍将这些设置应用于所有人，而无需再将其添加到第二个 GPO。为 GPO 设置优先级可能非常有用。

- **请谨慎使用环回模式( Loopback Mode )。**

  环回模式是一种非常有用的工具，但这也是另一项需要谨慎对待的技术。由于它可能导致将一组完全不同的策略（替换模式( Replace Mode )）或非常大量的策略（合并模式( Merge Mode )）应用到用户，因此需要格外小心，确保用户收到的策略符合预期。

- **全面测试 Windows 管理规范( Windows Management Instrumentation ,WMI) 筛选器。**

  如果使用 WMI 筛选器，请务必在将其发布到生产环境之前全面测试查询。如果使用低效查询或资源消耗非常大的查询，可能会导致 GPO 处理期间出现显著延迟。请考虑使用可从[此网站](http://bit.ly/11HCSG1)获取的免费 WMI 筛选器验证实用工具，以衡量 WMI 筛选器的影响。

- **使用测试环境验证 G

虽然我们建议将类似设置——或与特定项目相关的所有设置——保留在同一个组策略对象( Group Policy Object ,GPO)中，但这并不妨碍你只使用少数几个庞大的 GPO，而不使用许多较小的 GPO。如果采用单体式方法，处理的 GPO 会更少，这显然更快；但是，由于策略中包含大量设置，委派就不那么容易了。分段式 GPO 更便于委派，但策略数量增多可能会影响性能。请根据你的网络情况，将两者混合搭配到你觉得合适的程度。

### 15.2. 设计示例

我们来看一看第 13 章中介绍的三个示例组织。在本节中,我们将根据它们各自的需求,为每个组织探讨一种可能的组策略( Group Policy )设计方案。

#### Tailspin Toys

Tailspin Toys 是一家在北美拥有约 3,000 名员工的组织。在 Tailspin Toys 的各个位置，分布着约 4,000 台客户端计算机和数百台服务器。办公人员分布在美国和加拿大的多个城市以及家庭办公室中。制造业务在墨西哥进行。位于旧金山总部办公室的 IT 部门管理整个组织的 IT 资产。

Tailspin Toys 集中管理 Active Directory 中的几乎全部对象。由于对复杂权限委派的需求有限，Tailspin Toys 在设计其组织单位( Organizational Unit ,OU )结构时重点关注组策略( Group Policy )。在评估组织需求后，他们开发了基于位置和对象的 OU 结构。这样便可将策略定向到物理位置以及特定类型的对象(例如台式计算机与笔记本电脑)。

Tailspin 管理最终用户办公工作站的桌面体验的需求相对有限。整个组织强制实施少量全局设置，并且偶尔会出现需要在特定位置映射驱动器或安装打印机的情况。图 15-1 显示了该组织最终用户计算环境的组策略对象( Group Policy Object ,GPO )设计。该设计的基本前提在很大程度上依赖继承，即将 GPO 链接到 OU 结构中尽可能最高的点。用户设置和计算机设置被分离到不同的 GPO 中，以便于理解。除全局策略外，还可以根据需要应用特定国家/地区策略，以及在用户、计算机或计算机类型(例如台式机、笔记本电脑或自助服务终端)级别可选应用特定位置策略。每个策略的名称均以该策略所影响的一个或多个位置的标识符作为前缀。




![Tailspin Toys end user computing GPO design](./image/15.%20Planning%20for%20Group%20Policy/httpatomoreillycomsourceoreillyimages1663500.webp)


图 15-1. Tailspin Toys 最终用户计算 GPO 设计

在制造组织中，必须严格控制桌面体验，以确保用户不会对制造流程产生负面影响。此外，不同站点的需求各不相同；即使在同一个站点内，需求也会因制造车间中计算机的角色以及是否存在多条生产线而有所差异。无论哪个用户登录桌面，都必须保持严格的用户体验。策略结构还必须支持同一组织单位( Organizational Unit ,OU )内不同计算机组的多个策略配置文件。

图 15-2 展示了 Tailspin Toys 针对此问题的做法。在此设计中，一个全局计算机策略( Global Computer Policy )链接到 Manufacturing OU。该策略以替换模式( Replace Mode )启用环回处理( Loopback Processing )。利用环回处理可确保能够将用户特定的设置应用于制造计算机，而无论用户在 OU 结构中的位置如何，也无需考虑应用于该特定用户的策略。在仅有一个策略需求的站点中，一个以该站点代码命名的单一策略会链接到该站点的 OU。在如图 15-2 所示的 SFO01 站点等站点中，每个单独策略都通过安全筛选( Security Filtering )进行限制，以控制该策略应用于哪些计算机。在所有情况下，策略名称都以 *Manufacturing* 为前缀，后接该策略所影响位置的站点代码，以便轻松区分制造专用策略与应用于最终用户工作站( End User Workstations )的策略。




![Tailspin Toys manufacturing GPO design](./image/15.%20Planning%20for%20Group%20Policy/httpatomoreillycomsourceoreillyimages1663501.webp)


图 15-2. Tailspin Toys 制造组策略对象( Group Policy Object ,GPO )设计

#### Contoso College

Contoso College 是一所高等教育机构，拥有约 3,500 名员工、30,000 名学生和 5,000 台计算机。所有用户和计算机都位于单一校区。IT 资源的管理是分散式的，各部门对其区域内的计算机和资源拥有很大程度的自治权。为了提供集中式、可持续且分布式的目录服务( directory service )，中心 IT 正在部署一个 Active Directory 林( forest )，该林支持自动管理的用户账户和组，并让委派管理员( delegated administrators )能够接收组织单位( Organizational Unit ,OU )，从而可按自己的方式管理其中的资源。

在规划其 OU 结构时，Contoso 需要满足若干有时相互冲突的需求。主要需求是：域( domain )既要可由中心 IT 资源管理，又要足够灵活，以满足学院各部门委派管理员的需求。鉴于分散式结构，Contoso College 决定对组策略( Group Policy )采取相对放手的做法。在该做法中，只有为满足全组织范围要求以及安全审核与合规性要求而必须全局强制实施的设置才予以启用。为确保委派管理员不会覆盖全组织强制实施的策略设置，中心 IT 在全局策略上设置强制标志( Enforced flag )。

各部门管理员被放入组策略创建者所有者( Group Policy Creator Owners )组，并有权自行创建和管理组策略对象( Group Policy Object ,GPO )。OU 结构中的安全委派( security delegations )将委派管理员限制为只能在各自 OU 结构中链接策略。由于所有用户都位于中心 People OU，各部门管理员使用环回处理( loopback processing )，根据用户登录位置应用用户特定设置。

#### Fabrikam

Fabrikam 是一家全球性的大型企业，拥有超过 250,000 名员工和计算机，分布在全球 100 多个站点( Site )。公司全球总部位于芝加哥。另有四个主要站点，与总部相连，较小的分支机构再连接到这些主要站点：亚太区、北美区、南美区和欧洲区。小型站点通过 64 kbps 到 T1 速度的链路连接到枢纽站点；枢纽站点本身则通过各种更高速链路连接到总部。部分枢纽站点之间也互相连接。

Fabrikam 的管理结构按区域划分，每个地理单元作为全球组织的一部分独立运营业务。管理结构的顶层位于总部，总部居于四个枢纽站点之上。尽管芝加哥可被视作位于北美区域内，但该组织的结构并非如此。实际上，芝加哥的 IT 人员负责监督各枢纽站点，包括选择管理员以及确定网络结构方式。公司 IT 策略规定，人员超过 500 的分支机构需拥有自己的本地管理员、备份支持和帮助台人员。人员少于 500 的分支机构由其连接的枢纽站点的管理员管理。

Fabrikam 的组策略( Group Policy )需求由两项需求驱动：

- 安全审计与合规要求
- 站点级用户体验配置请求

除安全审计与合规要求外，Fabrikam 不需要也不希望管理开箱即用设置之外的用户体验。为此，该组织选择在全球和国家/地区级别创建组策略对象( Group Policy Object ,GPO )，以强制执行合规设置。各站点的委派管理员可以为其站点申请 GPO，同时提交策略用途简要说明、业务理由以及要向其委派策略编辑权限的安全组( Security Group )。策略获批后，Active Directory 管理员将创建并链接该策略，然后将管理权限委派给所请求的组。图 15-3 显示了 Fabrikam 的 GPO 设计。




![Fabrikam Group Policy design](./image/15.%20Planning%20for%20Group%20Policy/httpatomoreillycomsourceoreillyimages1663502.webp)


图 15-3. Fabrikam 组策略设计

### 15.3. 本章小结

组策略( Group Policy ,GPO )一直是 Active Directory 的一大卖点。在本章中,我们在第 11 章内容的基础上进行了扩展,涵盖了设计组策略部署的相关策略。
