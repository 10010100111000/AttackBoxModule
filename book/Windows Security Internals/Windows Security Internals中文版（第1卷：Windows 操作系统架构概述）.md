---
summary: 《Windows Security Internals》第1卷：Windows操作系统架构概述。由资深安全专家 James Forshaw 编著，系统剖析底层体系结构与安全基石。涵盖：1. 基于 NtObjectManager 模块构建 PowerShell 安全测试环境；2. 内核架构与执行体模块剖析，详述对象管理器（Object Manager）、命名空间（OMNS）、系统调用分发、进程线程管理、代码完整性及 ALPC 机制；3. 用户模式与 Win32 子系统机制，涵盖 Native API 映射、DLL 加载器、DOS 设备路径、注册表底层交互、进程创建全流程以及关键系统进程（smss/csrss/lsass/services/svchost）安全防护模型。逆向工程与底层开发必备攻防指南。
---

本书内容编排

每一章都会深入剖析现代 Windows 版本中实现的核心安全功能，并配以精心编写的 PowerShell 示例，帮助你直观理解所涉及的系统调用与命令。以下为全书章节概览：

第一部分 从开发与系统交互的角度概述 Windows 操作系统架构，为你深入研读后续安全机制奠定坚实基础。

- **第 1 章：搭建 PowerShell 测试环境**  
  搭建运行后续章节示例所需的 PowerShell 实验环境，包括安装专用于与 Windows 内部安全机制交互的 NtObjectManager 模块，并简要概述 PowerShell 语法。

- **第 2 章：Windows 内核**  
  介绍 Windows 内核及其系统调用接口的核心机制，这是透彻理解 Windows 安全性的关键基石。同时详细解析负责管理内核资源生命周期与命名空间的对象管理器（Object Manager）。

- **第 3 章：用户模式应用程序**  
  大多数应用程序并不直接发起内核系统调用，而是依托更高层级的编程接口。本章探讨 Win32 子系统机制，包括文件处理、注册表交互、GUI 消息机制与控制台会话隔离。

第二部分 全面剖析 Windows 内核中最为关键的安全组件——安全参考监视器(Security Reference Monitor, SRM)（SRM，Security Reference Monitor），覆盖从构建安全主体身份到保护文件等各类具体资源的访问控制全流程。

- **第 4 章：安全访问令牌**  
  Windows 为每个运行的进程分配一个访问令牌（Access Token），代表用户在系统中的安全身份。本章深入解析令牌中用于访问检查的各种属性，包括 SID、特权（Privilege）、完整性级别以及沙箱令牌。

- **第 5 章：安全描述符(Security Descriptor)**  
  每个受保护资源都需要声明允许谁访问以及授予何种访问权限。这正是安全描述符的核心职责。本章深入探讨其二进制内部结构、控制标志、DACL、SACL 以及 ACE 结构。

- **第 6 章：读取和分配安全描述符**  
  分析系统安全性必须能够查询资源的安全描述符。本章解析针对不同资源类型的查询机制，并深入阐释 Windows 为新建资源分配安全描述符时极为精细的继承与默认映射算法。

- **第 7 章：访问检查过程**  
  Windows 依靠访问检查（Access Check）算法确定是否向请求主体授予资源的指定访问权限。该过程结合令牌与安全描述符进行严格运算。本章通过纯 PowerShell 逐步重构实现这一算法，深挖其底层设计细节。

- **第 8 章：访问检查的其他应用场景**  
  除常规资源打开授权外，访问检查还广泛应用于其他安全判定场景，例如资源枚举可见性过滤、进程特权隔离以及沙箱防护。本章剖析这些拓展应用。

- **第 9 章：安全审计**  
  访问检查过程还可以产生详尽的审计日志，记录哪些主体尝试访问了哪些敏感资源及其成败结果。本章介绍高级安全审计策略及 SACL 审计规则配置。

第三部分 聚焦 Windows 身份验证体系（Authentication），即在访问控制前判定用户真实身份的关键机制。

- **第 10 章：Windows 身份验证**  
  梳理身份验证基础架构、本地域用户数据库（SAM）、LSA 安全策略以及密码哈希存储与提取机制。

- **第 11 章：Active Directory**  
  解析 Windows 企业域架构，阐释 Active Directory 目录存储结构、LDAP 访问、架构定义、信任关系以及目录对象安全描述符保护机制。

- **第 12 章：交互式身份验证**  
  探讨用户通过键盘输入凭据登录 Windows 桌面的全生命周期，剖析 Winlogon、LogonUI、凭据提供程序、安全注意序列（SAS）以及 `LsaLogonUser` API 的交互流程。

- **第 13 章：网络身份验证**  
  探讨跨网络访问服务时的身份核验机制。重点剖析经典的 NTLM 质询/响应（Challenge/Response）协议原理、NTLMv2 机制、以及 NTLM 中继攻击与防御对策。

- **第 14 章：Kerberos**  
  深度剖析 Windows 企业域核心的 Kerberos 认证协议，涵盖 KDC、AS-REQ/AS-REP、TGS-REQ/TGS-REP、特权属性证书(Privilege Attribute Certificate, PAC)、协议委派以及 Kerberoasting 攻击原理。

- **第 15 章：协商身份验证与其他安全包**  
  介绍扩展认证协议，包括 SPNEGO 协商包（Negotiate）、Schannel（TLS/SSL）、CredSSP 以及 AppContainer / LowBox 进程内的代理认证限制。

- **附录 A：构建用于测试的 Windows 域网络**  
  提供使用 PowerShell 自动化构建实验域网络的详细步骤。

- **附录 B：SDDL SID 别名映射**  
  提供第 5 章中涉及的常用 SDDL 缩写与知名 SID 常量速查表。

---

本书中的 PowerShell 约定

所有现代 Windows 版本均默认内置 PowerShell 脚本环境。这是在无需安装额外笨重软件的前提下，灵活探索操作系统内部工作原理的最佳方式。由于 PowerShell 依托 .NET 运行时构建，本书将广泛使用我专门编写的 .NET 扩展库来与 Windows 底层 API 交互，从而大幅简化复杂脚本的编写难度。本书涉及的所有示例脚本均可从官方代码仓库下载：*[https://github.com/tyranid/windows-security-internals](https://github.com/tyranid/windows-security-internals)*。

各章中的 PowerShell 示例均遵循统一的排版规范。示例分为两类：**交互式代码清单**与**非交互式代码清单**。

**交互式代码清单**代表需要你在命令行中直接输入并观察结果的命令序列。示例如下：

```powershell
❶ PS> ls C:\
❷ Directory: C:\
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-r---               4/17  11:45 AM        Program Files
❸ --snip--
```

交互式代码清单在每个待输入的命令前都带有 PowerShell 风格的提示符（`PS>`），命令本身以粗体显示 ❶。命令下方为执行输出结果 ❷。有时输出内容较长，为节省版面，会使用 `--snip--` 表示输出已被截断 ❸。另请注意，部分示例中的输出仅供参考，具体输出可能因操作系统版本或网络配置的不同而略有差异。

大多数交互式代码清单均设计在普通用户账户下执行。但部分清单必须以管理员权限运行，以访问受保护的系统功能。如果未以管理员身份运行，将无法得到正确的结果。每个清单前的正文都会明确说明是否必须以管理员身份运行。

**非交互式代码清单**包含可复制到脚本文件中重复使用的 PowerShell 代码段，如下所示：

```powershell
function Get-Hello {
    "Hello"
}
```

非交互式代码清单不包含 `PS>` 提示符，代码也不使用粗体。

如果你编写过 PowerShell 脚本，就会知道这门语言以冗长的命令与参数名而著称，这使得书中的部分长命令很难排在单行内。以下展示了一个超长命令及其在页面排版中的折行处理方式：

```powershell
PS> Get-ChildItem -LiteralPath "C:\" -Filter "*.exe" -Recurse -Hidden
❶ -System -Depth 5 | Where-Object {
  ❷ $_.Name -eq "Hello"
}
```

第一行使用 `Get-ChildItem` 命令，由于行宽超出页面排版范围，因此折行显示到下一行 ❶。在实际命令中间不能随意添加换行符，因此在 shell 或脚本文件中输入时，应将其作为单行整行输入。判断该行是属于上一条命令还是命令输出的关键标识，在于第一列带有粗体标记符号。

PowerShell 可以在某些特定字符处（例如管道符 `|`、逗号 `,` 或大括号 `{}`）进行自然折行。在此示例中，我在左大括号 `{` 之后添加了换行符，并将后续命令放置在大括号代码块内，缩进一级 ❷。此时 shell 会自动处理折行。注意，右大括号 `}` 位于首列，虽然也可以将其移至上一行末尾，但在此处并非必须。

注意，Windows 操作系统始终处于积极迭代与更新中。虽然本书中的所有 PowerShell 示例均已在成书时可用的最新 Windows 版本上完成测试，但在你阅读本书时，微软可能已经引入了新的安全功能或废弃了旧有机制。以下为编写和测试本书示例所用的操作系统版本及主要 Build 版本号：

- Windows 11 (OS build 22631)
- Windows 10 (OS build 19045)
- Windows Server 2022 (OS build 20384)
- Windows Server 2019 (OS build 17763)

正文中提及的“最新版本”均指上述测试版本。

---

## 1. 搭建 PowerShell 测试环境

在本章中，你将配置 PowerShell，以便能够运行本书其余部分提供的代码示例。随后，我们将快速概述 PowerShell 语言，包括其类型、变量和表达式。我们还将介绍如何执行命令、如何获取帮助，以及如何导出数据以供后续使用。

### 选择 PowerShell 版本

要有效使用本书，最重要的工具是 PowerShell，自 Windows 7 起，它已默认安装在 Windows 操作系统中。然而，该工具有许多不同版本。当前受支持的 Windows 版本默认安装的版本是 5.1，尽管 Microsoft 不再完全支持它，但它仍适合我们的用途。较新版本的 PowerShell 是跨平台且开源的，但必须在 Windows 上单独安装。

本书中提供的所有代码都将在 PowerShell 5.1 和最新的开源版本中运行，因此选择哪个版本并不重要。如果你想使用开源 PowerShell，请访问该项目的 GitHub 页面 *https://github.com/PowerShell/PowerShell*，查找适用于你 Windows 版本的安装说明。

### 配置 PowerShell

在 PowerShell 中，我们需要做的第一件事是设置 *脚本执行策略*，该策略决定了 PowerShell 可以执行哪些类型的脚本。对于运行 PowerShell 5.1 的 Windows 客户端，默认策略是 Restricted，这会阻止所有脚本运行，除非它们使用受信任的证书签名。由于本书中的脚本未签名，我们将执行策略更改为 RemoteSigned。此执行策略允许我们运行本地创建的未签名 PowerShell 脚本，但不允许执行通过网页浏览器下载或附加在电子邮件中的未签名脚本。运行以下命令来设置执行策略：

```
PS> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

该命令仅更改当前用户的执行策略，而非整个系统。如果你想为所有用户更改它，则需要以管理员身份启动 PowerShell，然后重新运行该命令，并移除 Scope 参数。

如果你使用的是开源版 PowerShell 或 Windows Server 上的 5.1 版本，那么默认脚本执行策略是 RemoteSigned，你无需更改任何内容。

现在我们可以运行未签名脚本了，接下来可以安装本书将使用的 PowerShell 模块。PowerShell *模块* 是脚本和 .NET 二进制文件的包，用于导出 PowerShell 命令。每个 PowerShell 安装都预装了几个模块，用于从配置应用程序到设置 Windows Update 等任务。你可以通过复制文件手动安装模块，但最简单的方法是使用 PowerShell Gallery（*[https://www.powershellgallery.com](https://www.powershellgallery.com/)*），这是一个在线模块仓库。

要从 PowerShell Gallery 安装模块，我们使用 PowerShell 的 Install-Module 命令。对于本书，我们需要安装 NtObjectManager 模块，可以使用以下命令完成：

```
PS> Install-Module NtObjectManager -Scope CurrentUser -Force
```

如果安装程序询问你任何问题（当然，在你阅读并理解问题之后），请确保回答“是”。如果你已经安装了该模块，可以使用 Update-Module 命令确保你拥有最新版本：

```
PS> Update-Module NtObjectManager
```

安装完成后，可以使用 Import-Module 命令加载模块：

```
PS> Import-Module NtObjectManager
```

如果在导入模块后看到任何错误，请仔细检查你是否正确设置了执行策略；这是模块无法正常加载的最常见原因。作为最终测试，让我们运行一个随模块提供的命令来检查它是否正常工作。执行 代码清单 1-1 中的命令，并验证输出是否与 PowerShell 控制台中显示的内容匹配。我们将在后续章节中探讨此命令的用途。

```
PS> New-NtSecurityDescriptor
Owner DACL ACE Count SACL ACE Count Integrity Level
----- -------------- -------------- ---------------
NONE  NONE           NONE           NONE
```

*代码清单 1-1：测试 NtObjectManager 模块是否正常工作*

如果一切正常且你熟悉 PowerShell，可以继续阅读下一章。如果你需要快速回顾 PowerShell 语言，请继续阅读。

### PowerShell 语言概述

对 PowerShell 的完整介绍超出了本书的范围。然而，本节将涉及您需要熟悉的各种语言特性，以便最有效地使用本书。

#### 理解类型、变量和表达式

PowerShell 支持多种类型，从基本的整数和字符串到复杂的对象。表 1-1 展示了一些最常见的内置类型，以及它们底层的 .NET 运行时类型和一些简单示例。

| 类型      | .NET 类型                    | 示例               |
| :-------- | :--------------------------- | :----------------- |
| int       | System.Int32                 | 142, 0x8E, 0216    |
| long      | System.Int64                 | 142L, 0x8EL, 0216L |
| string    | System.String                | "Hello", 'World!'  |
| double    | System.Double                | 1.0, 1e10          |
| bool      | System.Boolean               | $true, $false      |
| array     | System.Object[]              | @(1, "ABC", $true) |
| hashtable | System.Collections.Hashtable | @{A=1; B="ABC"}    |

要对基本类型进行计算，我们可以使用众所周知的运算符，如 +、−、* 和 /。这些运算符可以被重载；例如，+ 既用于加法，也用于字符串和数组的拼接。表 1-2 提供了常用运算符的列表，并附有简单示例及其结果。您可以自行测试这些示例，以检查每个运算符的输出。

| 运算符 | 名称                      | 示例                      | 结果             |
| :----- | :------------------------ | :------------------------ | :--------------- |
| +      | 加法或拼接                | 1 + 2, "Hello" + "World!" | 3, "HelloWorld!" |
| −      | 减法                      | 2 − 1                     | 1                |
| *      | 乘法                      | 2 * 4                     | 8                |
| /      | 除法                      | 8 / 4                     | 2                |
| %      | 取模                      | 6 % 4                     | 2                |
| []     | 索引                      | @(3, 2, 1, 0)[1]          | 2                |
| -f     | 字符串格式化              | "0x{0:X} {1}" -f 42, 123  | "0x2A 123"       |
| -band  | 按位与                    | 0x1FF -band 0xFF          | 255              |
| -bor   | 按位或                    | 0x100 -bor 0x20           | 288              |
| -bxor  | 按位异或                  | 0xCC -bxor 0xDD           | 17               |
| -bnot  | 按位非                    | -bnot 0xEE                | -239             |
| -and   | 布尔与                    | $true -and $false         | $false           |
| -or    | 布尔或                    | $true -or $false          | $true            |
| -not   | 布尔非                    | -not $true                | $false           |
| -eq    | 等于                      | "Hello" -eq "Hello"       | $true            |
| -ne    | 不等于                    | "Hello" -ne "Hello"       | $false           |
| -lt    | 小于                      | 4 -lt 10                  | $true            |
| -gt    | 大于                      | 4 -gt 10                  | $false           |

```
PS> $var = 3, 2, 1, 0
PS> $var[1]
2
```

*代码清单 1-2：将数组捕获到变量中，并通过变量名进行索引*

在本书的其余部分，我们还会使用一些预定义变量。这些变量包括：

$null  表示 NULL 值，用于在比较中指示值的缺失

$pwd  包含当前工作目录

$pid  包含 shell 的进程 ID

$env  访问进程环境（例如，$env:WinDir 获取 *Windows* 目录）

您可以使用 Get-Variable 命令枚举所有变量。

在表1-1中，你可能注意到了两个字符串示例，一个使用双引号，另一个使用单引号。两者之间的一个区别是，双引号字符串支持*字符串插值*，即你可以将变量名作为占位符插入字符串中，PowerShell会在结果中包含其值。代码清单 1-3展示了在双引号和单引号字符串中执行此操作时会发生什么。

```
PS> $var = 42
PS> "The magic number is $var"
The magic number is 42

PS> 'It is not $var'
It is not $var
```

*代码清单 1-3：字符串插值示例*

首先，我们定义一个值为42的变量，以便插入到字符串中。然后，我们创建一个双引号字符串，其中包含变量名。结果是字符串中的变量名被其值替换，并格式化为字符串。（如果你需要更精确地控制格式，可以使用表1-2中定义的字符串格式化运算符。）

接下来，为了演示单引号字符串的不同行为，我们定义一个包含变量名的单引号字符串。我们可以观察到，在这种情况下，变量名被原样复制，并未被其值替换。

另一个区别是，双引号字符串可以包含字符转义，而单引号字符串则忽略这些转义。这些转义使用与C编程语言类似的语法，但PowerShell使用反引号（`）而不是反斜杠（\）。这是因为Windows使用反斜杠作为路径分隔符，如果每次都必须转义反斜杠，编写文件路径会非常麻烦。表1-3列出了PowerShell中可用的字符转义。

| 字符转义 | 名称                                |
| :--------------- | :---------------------------------- |
| `0               | NUL字符，值为零                     |
| `a               | 响铃                                |
| `b               | 退格                                |
| `n               | 换行                                |
| `r               | 回车                                |
| `t               | 水平制表符                          |
| `v               | 垂直制表符                          |
| ``               | 反引号字符                          |
| `"               | 双引号字符                          |

如果你想在双引号字符串中插入双引号字符，需要使用`"转义。要在单引号字符串中插入单引号，你需要将引号字符加倍：例如，'Hello''There'会转换为Hello'There。还要注意此表中提到的NUL字符。由于PowerShell使用.NET字符串类型，它可以包含嵌入的NUL字符。与C语言不同，添加NUL不会提前终止字符串。

因为所有值都是.NET类型，我们可以在对象上调用方法和访问属性。例如，以下代码在字符串上调用`ToCharArray`方法，将其转换为单个字符数组：

```
PS> "Hello".ToCharArray()
H
e
l
l
o
```

我们可以使用PowerShell构造几乎任何.NET类型。最简单的方法是通过在方括号中指定.NET类型来将值强制转换为该类型。强制转换时，PowerShell会尝试找到适合该类型的构造函数并调用它。例如，以下命令将字符串转换为`System.Guid`对象；PowerShell会找到一个接受字符串的构造函数并调用它：

```
PS> [System.Guid]"6c0a3a17-4459-4339-a3b6-1cdb1b3e8973"
```

你也可以通过调用类型上的`new`方法显式调用构造函数。前面的示例可以重写如下：

```
PS> [System.Guid]::new("6c0a3a17-4459-4339-a3b6-1cdb1b3e8973")
```

这种语法也可以用于创建其他类型，例如：

```
PS> [System.Guid]::NewGuid()
```

在PowerShell中，几乎所有命令都遵循一个命名模式：一个动词和一个名词，用连字符分隔。例如，考虑命令`Get-Item`。动词`Get`暗示检索现有资源，而`Item`是要返回的资源类型。

每个命令都可以接受一组参数来控制命令的行为。例如，`Get-Item`命令接受一个`Path`参数，指示要检索的现有资源，如下所示：

```
PS> Get-Item -Path "C:\Windows"
```

Path 参数是一个*位置*参数。这意味着你可以省略参数名称，PowerShell 会尽力选择最佳匹配。因此，之前的命令也可以写成如下形式：


```
PS> Get-Item "C:\Windows"
```


如果参数接受字符串值，且字符串不包含任何特殊字符或空白，则无需在字符串周围使用引号。例如，`Get-Item` 命令也可以使用以下方式工作：


```
PS> Get-Item C:\Windows
```


单个命令的输出是零个或多个值，这些值可以是基本类型或复杂对象类型。你可以使用*管道*将一个命令的输出作为输入传递给另一个命令，管道由竖线字符 `|` 表示。在本章后面讨论筛选、分组和排序时，我们会看到使用管道的示例。

你可以将整个命令或管道的输出捕获到变量中，然后与结果进行交互。例如，以下命令捕获 `Get-Item` 命令的结果并查询 `FullName` 属性：


```
PS> $var = Get-Item -Path "C:\Windows"
PS> $var.FullName
C:\Windows
```


如果你不想将结果捕获到变量中，可以将命令括在括号中，并直接访问其属性和方法：


```
PS> (Get-Item -Path "C:\Windows").FullName
C:\Windows
```


命令行的长度实际上是无限的。但是，你应尽量将长行拆分，以使命令更具可读性。Shell 会自动在管道字符处拆分行。如果需要在没有管道的情况下拆分长行，可以使用反引号字符，然后开始新行。反引号必须是该行的最后一个字符；否则，脚本解析时会出现错误。

#### 发现命令和获取帮助

默认安装的 PowerShell 有数百个命令可供选择。这意味着找到执行特定任务的命令可能很困难，即使找到了命令，也可能不清楚如何使用它。为了帮助解决这个问题，你可以使用两个内置命令：`Get-Command` 和 `Get-Help`。

`Get-Command` 命令可用于枚举所有可用的命令。在其最简单的形式中，你可以不带任何参数执行它，它将打印所有模块中的所有命令。然而，更实用的可能是根据你感兴趣的特定词进行筛选。例如，代码清单 1-4 将仅列出名称中包含 `SecurityDescriptor` 的命令。




```
PS> Get-Command -Name *SecurityDescriptor*
CommandType     Name                              Source
-----------     ----                              ------
Function        Add-NtSecurityDescriptorControl   NtObjectManager
Function        Add-NtSecurityDescriptorDaclAce   NtObjectManager
Function        Clear-NtSecurityDescriptorDacl    NtObjectManager
Function        Clear-NtSecurityDescriptorSacl    NtObjectManager
--snip--
```


*代码清单 1-4：使用 Get-Command 枚举命令*

此命令使用*通配符语法*来仅列出名称中包含指定单词的命令。通配符语法使用 `*` 字符来表示任何字符或字符序列。在这里，我们在 `SecurityDescriptor` 的两侧都放置了 `*`，以指示其前后可以有任何文本。

你还可以列出模块中可用的命令。例如，代码清单 1-5 将仅列出由 `NtObjectManager` 模块导出且以动词 `Start` 开头的命令。




```
PS> Get-Command -Module NtObjectManager -Name Start-*
CommandType     Name                             Source
-----------     ----                             ------
Function        Start-AccessibleScheduledTask    NtObjectManager
Function        Start-NtFileOplock               NtObjectManager
Function        Start-Win32ChildProcess          NtObjectManager
Cmdlet          Start-NtDebugWait                NtObjectManager
Cmdlet          Start-NtWait                     NtObjectManager
```


*代码清单 1-5：使用 Get-Command 枚举 NtObjectManager 模块中的命令*

一旦找到看起来有希望的命令，你可以使用 `Get-Help` 命令检查其参数并获取一些使用示例。在 代码清单 1-6 中，我们将 代码清单 1-5 中的 `Start-NtWait` 命令传递给 `Get-Help`。




```
PS> Get-Help Start-NtWait
NAME
  ❶ Start-NtWait
SYNOPSIS
  ❷ Wait on one or more NT objects to become signaled.
SYNTAX
  ❸ Start-NtWait [-Object] <NtObject[]> [-Alertable <SwitchParameter>]
    [-Hour <int>] [-MilliSecond <long>]
    [-Minute <int>] [-Second <int>] [-WaitAll <SwitchParameter>]
    [<CommonParameters>]

    Start-NtWait [-Object] <NtObject[]> [-Alertable <SwitchParameter>]
    [-Infinite <SwitchParameter>] [-WaitAll <SwitchParameter>]
    [<CommonParameters>]
DESCRIPTION
  ❹ This cmdlet allows you to issue a wait on one or more NT
    objects until they become signaled.
--snip--
```


*代码清单 1-6：显示 Start-NtWait 命令的帮助*

默认情况下，`Get-Help` 输出命令的名称 ❶、简短摘要 ❷、命令语法 ❸ 以及更详细的描述 ❹。在命令语法部分，你可以看到其多种可能的操作模式：在这种情况下，要么指定小时、分钟、秒和/或毫秒的时间，要么指定 `Infinite` 以无限期等待。

当语法的任何部分显示在方括号 `[]` 中时，表示它是可选的。例如，唯一必需的参数是 `Object`，它接受一个 `NtObject` 值数组。即使该参数的名称也是可选的，因为 `-Object` 在方括号中。

你可以使用 `Parameter` 命令获取有关参数的更多信息。代码清单 1-7 显示了 `Object` 参数的详细信息。




```
PS> Get-Help Start-NtWait -Parameter Object
-Object <NtObject[]>
    Specify a list of objects to wait on.

    Required?                    true
    Position?                    0
    Default value
    Accept pipeline input?       true (ByValue)
    Accept wildcard characters?  False
```


*代码清单 1-7：使用 Parameter 命令查询 Object 参数的详细信息*

你可以使用通配符语法来选择一组相似的参数名称。例如，如果你指定 `Obj*`，那么你将获得名称以 `Obj` 前缀开头的任何参数的信息。

如果你想要某个命令的用法示例，可以使用 Examples 参数，如 代码清单 1-8 所示。




```
PS> Get-Help Start-NtWait -Examples
--snip--
    ----------  EXAMPLE 1  ----------
 ❶ $ev = Get-NtEvent \BaseNamedObjects\ABC
    Start-NtWait $ev -Second 10

 ❷ Get an event and wait for 10 seconds for it to be signaled.
--snip--
```


*代码清单 1-8：展示 Start-NtWait 的示例*

每个示例应包含一行或两行的 PowerShell 脚本片段 ❶ 以及对其功能的描述 ❷。你也可以通过指定 Full 参数查看命令的完整帮助输出。若要在单独的弹出窗口中查看此输出，请使用 ShowWindow 参数。例如，尝试运行以下命令：


```
PS> Get-Help Start-NtWait -ShowWindow
```


你应该会看到如 图 1-1 所示的对话框。

![img](./image/01.%20PART%20I%20AN%20OVERVIEW%20OF%20THE%20WINDOWS%20OPERATING%20SYSTEM/Figure1-1.webp)

图 1-1: 使用 ShowWindow 参数显示 Get-Help 信息的对话框

关于命令的最后一个话题是，你可以设置 *别名*，即命令的替代名称。例如，你可以使用别名来缩短命令的输入。PowerShell 预定义了许多别名，你也可以使用 New-Alias 命令自定义别名。例如，我们可以将 Start-NtWait 命令设置为别名 swt，如下所示：


```
PS> New-Alias -Name swt -Value Start-NtWait
```


要显示所有已定义别名的列表，请使用 Get-Alias 命令。在本书中，我们将避免不必要地使用别名，因为如果你不知道别名代表什么，可能会使脚本更令人困惑。

#### 定义函数

与所有编程语言一样，在 PowerShell 中降低复杂性是有益的。降低复杂性的一种方法是将常见代码组合成函数。一旦定义了函数，PowerShell 脚本就可以调用该函数，而无需在多个位置重复相同的代码。PowerShell 中的基本函数语法很简单；代码清单 1-9 显示了一个示例。




```
PS> function Get-NameValue {
    param(
        [string]$Name = "",
        $Value
    )
    return "We've got $Name with value $Value"
}

PS> Get-NameValue -Name "Hello" -Value "World"
We've got Hello with value World

PS> Get-NameValue "Goodbye" 12345
We've got Goodbye with value 12345
```


*代码清单 1-9：定义一个名为 Get-NameValue 的简单 PowerShell 函数*

定义函数的语法以关键字 function 开头，后跟要定义的函数名称。虽然不强制要求使用标准的 PowerShell 命令命名约定（动词后跟名词），但这样做是有益的，因为它能让用户清楚地了解函数的功能。

接下来，定义函数的命名参数。与变量一样，参数使用以 $ 前缀的名称定义，如 代码清单 1-9 所示。你可以在括号中指定类型，但这是可选的；在此示例中，$Name 是字符串，但 $Value 参数可以接受调用者传递的任何值。指定命名参数不是必需的。如果未包含 param 块，则任何传递的参数都会放入 $args 数组中。第一个参数位于 $args[0]，第二个位于 $args[1]，依此类推。

Get-NameValue 函数的主体使用参数并通过字符串插值构建字符串。函数使用 return 关键字返回字符串，该关键字也会立即结束函数。在这种情况下，你可以省略 return 关键字，因为 PowerShell 会返回任何未捕获到变量中的值。

定义函数后，我们调用它。你可以显式指定参数名称。但是，如果调用是无歧义的，则不需要指定参数名称。代码清单 1-9 显示了两种方法。

如果你想运行一小段代码而不定义函数，可以创建一个脚本块。*脚本块* 是用花括号 {} 括起来的一条或多条语句。该块可以分配给变量，并在需要时使用 Invoke-Command 命令或 & 运算符执行，如 代码清单 1-10 所示。




```
PS> $script = {Write-Output "Hello"}
PS> & $script
Hello
```


*代码清单 1-10：创建脚本块并执行*

#### 显示和操作对象

如果你执行命令但未将结果捕获到变量中，结果将传递给 PowerShell 控制台。控制台将使用格式化程序显示结果，以表格或列表形式呈现（格式会根据结果中包含的对象类型自动选择）。也可以指定自定义格式化程序。例如，如果你使用内置的 Get-Process 命令检索正在运行的进程列表，PowerShell 会使用自定义格式化程序将条目显示为表格，如 代码清单 1-11 所示。




```
PS> Get-Process
Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
    476      27    25896      32044       2.97   3352   1 ApplicationFrameHost
    623      18    25096      18524     529.95  19424   0 audiodg
    170       8     6680       5296       0.08   5192   1 bash
    557      31    23888        332       0.59  10784   1 Calculator
--snip--
```

*代码清单 1-11：以表格形式输出进程列表*

如果希望减少输出中的列数，可以使用 `Select-Object` 命令仅选择所需的属性。例如，代码清单 1-12 选择了 `Id` 和 `ProcessName` 属性。




```
PS> Get-Process | Select-Object Id, ProcessName
   Id ProcessName
   -- -----------
 3352 ApplicationFrameHost
19424 audiodg
 5192 bash
10784 Calculator
--snip--
```


*代码清单 1-12：仅选择 Id 和 ProcessName 属性*

您可以通过使用 `Format-Table` 或 `Format-List` 命令来更改输出的默认行为，这两个命令分别强制使用表格或列表格式。例如，代码清单 1-13 展示了如何使用 `Format-List` 命令将输出更改为列表格式。




```
PS> Get-Process | Format-List
Id      : 3352
Handles : 476
CPU     : 2.96875
SI      : 1
Name    : ApplicationFrameHost
--snip--
```


*代码清单 1-13：使用 Format-List 以列表视图显示进程*

要查找可用属性的名称，可以对 `Get-Process` 返回的对象之一使用 `Get-Member` 命令。例如，代码清单 1-14 列出了 `Process` 对象的属性。




```
PS> Get-Process | Get-Member -Type Property
   TypeName: System.Diagnostics.Process
Name                MemberType Definition
----                ---------- ----------
BasePriority        Property   int BasePriority {get;}
Container           Property   System.ComponentModel.IContainer Container {get;}
EnableRaisingEvents Property   bool EnableRaisingEvents {get;set;}
ExitCode            Property   int ExitCode {get;}
ExitTime            Property   datetime ExitTime {get;}
--snip--
```


*代码清单 1-14：使用 Get-Member 命令列出 Process 对象的属性*

您可能会注意到输出中未包含其他属性。要显示它们，需要覆盖自定义格式。访问隐藏属性的最简单方法是使用 `Select-Object` 显式提取值，或者将属性指定给 `Format-Table` 或 `Format-List` 命令进行显示。您可以使用 `*` 作为通配符来显示所有属性，如代码清单 1-15所示。




```
PS> Get-Process | Format-List *
Name            : ApplicationFrameHost
Id              : 3352
PriorityClass   : Normal
FileVersion     : 10.0.18362.1 (WinBuild.160101.0800)
HandleCount     : 476
WorkingSet      : 32968704
PagedMemorySize : 26517504
--snip--
```


*代码清单 1-15：以列表形式显示 Process 对象的所有属性*

许多对象还具有可以调用的方法，用于对对象执行某些操作。代码清单 1-16 展示了如何使用 `Get-Member` 查询方法。




```
PS> Get-Process | Get-Member -Type Method
   TypeName: System.Diagnostics.Process

Name                MemberType Definition
----                ---------- ----------
BeginErrorReadLine  Method     void BeginErrorReadLine()
BeginOutputReadLine Method     void BeginOutputReadLine()
CancelErrorRead     Method     void CancelErrorRead()
CancelOutputRead    Method     void CancelOutputRead()
Close               Method     void Close()
--snip--
```


*代码清单 1-16：显示 Process 对象上的方法*

如果命令的输出过长，无法在屏幕上完整显示，您可以对输出进行*分页*，以便仅显示第一部分，控制台将等待您按键后再显示更多内容。您可以通过将输出通过管道传递给 `Out-Host` 命令并指定 `Paging` 参数，或使用 `more` 命令来启用分页。代码清单 1-17 展示了一个示例。




```
PS> Get-Process | Out-Host -Paging
Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
    476      27    25896      32044       2.97   3352   1 ApplicationFrameHost
    623      18    25096      18524     529.95  19424   0 audiodg
    170       8     6680       5296       0.08   5192   1 bash
    557      31    23888        332       0.59  10784   1 Calculator
<SPACE> next page; <CR> next line; Q quit
```


*代码清单 1-17：使用 Out-Host 进行分页输出*

您可以在自己的脚本中使用 `Write-Host` 命令直接写入控制台窗口。这允许您使用 `ForegroundColor` 和 `BackgroundColor` 参数更改输出的颜色以符合您的喜好。它还有一个优点，即默认情况下不会将对象插入管道，如下所示：


```
PS> $output = Write-Host "Hello"
Hello
```


这意味着，默认情况下，您无法将输出重定向到文件或管道中。但是，您可以通过使用类似以下命令将主机输出流重定向到标准输出流来重定向主机输出：


```
PS> $output = Write-Host "Hello" 6>&1
PS> $output
Hello
```


PowerShell 还支持一个基本的 GUI，用于显示对象。您可以使用 `Out-GridView` 命令将对象输出到网格视图。请注意，自定义格式仍会限制 PowerShell 显示的列。如果您想查看其他列，请在管道中使用 `Select-Object` 选择属性。以下示例在网格视图 GUI 中显示所有属性：


```
PS> Get-Process | Select-Object * | Out-GridView
```


运行此命令应会显示一个对话框，如图 1-2所示。

![img](./image/01.%20PART%20I%20AN%20OVERVIEW%20OF%20THE%20WINDOWS%20OPERATING%20SYSTEM/Figure1-2.webp)

图 1-2：在网格视图中显示 Process 对象

您可以在网格视图 GUI 中筛选和操作数据。尝试使用这些控件。您还可以为 `Out-GridView` 指定 `PassThru` 参数，这会使命令等待您在 GUI 中单击“确定”按钮。当您单击“确定”时，视图中选中的任何行都将写入命令管道。

#### 筛选、排序和分组对象

传统 shell 在命令之间传递原始文本；PowerShell 传递对象。传递对象使您能够访问对象的各个属性，并轻松筛选管道。您甚至可以轻松地对对象进行排序和分组。

你可以使用 `Where-Object` 命令来过滤对象，它有两个别名：`Where` 和 `?`。最简单的过滤方式是检查某个参数的值，如 代码清单 1-18 所示，我们过滤内置的 `Get-Process` 命令的输出，以查找 explorer 进程。

```
PS> Get-Process | Where-Object ProcessName -EQ "explorer"
Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
   2792     130   118152     158144     624.83    6584  1 explorer
```

*代码清单 1-18：使用 Where-Object 过滤进程列表*

在 代码清单 1-18 中，我们仅传递 `ProcessName` 等于（`-EQ`）"explorer" 的 `Process` 对象。你可以使用多种运算符进行过滤，其中一些在 表 1-4 中列出。

| 运算符    | 示例                          | 描述                                       |
| :-------- | :---------------------------- | :----------------------------------------- |
| -EQ       | ProcessName -EQ "explorer"    | 等于该值                                   |
| -NE       | ProcessName -NE "explorer"    | 不等于该值                                 |
| -Match    | ProcessName -Match "ex.*"     | 将字符串与正则表达式匹配                   |
| -NotMatch | ProcessName -NotMatch "ex.*"  | -Match 运算符的反向操作                    |
| -Like     | ProcessName -Like "ex*"       | 将字符串与通配符匹配                       |
| -NotLike  | ProcessName -NotLike "ex*"    | -Like 运算符的反向操作                     |
| -GT       | ProcessName -GT "ex"          | 大于比较                                   |
| -LT       | ProcessName -LT "ex"          | 小于比较                                   |

你可以通过 `Get-Help` 查看 `Where-Object` 命令支持的所有运算符。如果过滤条件比简单比较更复杂，你可以使用脚本块。脚本块应返回 `True` 以保留管道中的对象，或返回 `False` 以过滤掉它。例如，你也可以将 代码清单 1-18 写成如下形式：

```
PS> Get-Process | Where-Object {$_.ProcessName -eq "explorer"}
```

传递给脚本块的 `$_` 变量代表管道中的当前对象。通过使用脚本块，你可以在过滤中使用完整的语言功能，包括调用函数。

要对对象进行排序，请使用 `Sort-Object` 命令。如果对象本身可以排序（如字符串或数字），你只需将对象通过管道传递给该命令。否则，你需要指定一个属性来进行排序。例如，你可以按进程的句柄数（由 `Handles` 属性表示）对进程列表进行排序，如 代码清单 1-19 所示。

```
PS> Get-Process | Sort-Object Handles
Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
      0       0       60          8                 0   0 Idle
     32       9     4436       6396              1032   1 fontdrvhost
     53       3     1148       1080               496   0 smss
     59       5      804       1764               908   0 LsaIso
--snip--
```

*代码清单 1-19：按句柄数对进程进行排序*

要以降序而非升序排序，请使用 `Descending` 参数，如 代码清单 1-20 所示。

```
PS> Get-Process | Sort-Object Handles -Descending
Handles   NPM(K)    PM(K)      WS(K)     CPU(s)      Id   SI  ProcessName
-------  ------     -----      -----     ------      --   --  -----------
   5143       0       244      15916                  4    0  System
   2837     130    116844     156356     634.72    6584    1  explorer
   1461      21     11484      16384               1116    0  svchost
   1397      52     55448       2180      12.80   12452    1  Microsoft.Photos
```

*代码清单 1-20：按句柄数降序排序进程*

在此阶段，你还可以通过为 `Sort-Object` 指定 `Unique` 参数来过滤掉重复条目。

最后，你可以使用 `Group-Object` 命令根据属性名对对象进行分组。例如，你可以按 `ProcessName` 属性对进程进行分组，如 代码清单 1-21 所示。

```
PS> Get-Process | Group-Object ProcessName
Count Name                 Group
----- ----                 -----
    1 ApplicationFrameHost {System.Diagnostics.Process (ApplicationFrameHost)}
    1 Calculator           {System.Diagnostics.Process (Calculator)}
   11 conhost              {System.Diagnostics.Process (conhost)...}
--snip--
```

*代码清单 1-21：按 ProcessName 对进程对象进行分组*

或者，你也可以在单个管道中组合使用所有这些命令，如 代码清单 1-22 所示。

```
PS> Get-Process | Group-Object ProcessName |
Where-Object Count -GT 10 | Sort-Object Count
Count Name                 Group
----- ----                 -----
   11 conhost              {System.Diagnostics.Process (conhost),...}
   83 svchost              {System.Diagnostics.Process (svchost),...}
```

*代码清单 1-22：组合使用 Where-Object、Group-Object 和 Sort-Object*

#### 导出数据

一旦你获得了想要检查的理想对象集合，你可能希望将这些信息持久化到磁盘上的文件中。PowerShell 提供了多种选项，这里我将讨论其中几种。第一种选项是使用 `Out-File` 将对象以文本形式输出到文件。该命令捕获格式化后的文本输出并将其写入文件。你可以使用 `Get-Content` 再次读取该文件，如 代码清单 1-23 所示。

```
PS> Get-Process | Out-File processes.txt
PS> Get-Content processes.txt
Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
    476      27    25896      32044       2.97   3352   1 ApplicationFrameHost
    623      18    25096      18524     529.95  19424   0 audiodg
    170       8     6680       5296       0.08   5192   1 bash
    557      31    23888        332       0.59  10784   1 Calculator
--snip--
```

*代码清单 1-23：将内容写入文本文件并再次读取*

你也可以像在其他 shell 中一样，使用大于号运算符将输出发送到文件。例如：

```
PS> Get-Process > processes.txt
```

如果你想要更结构化的格式，可以使用 `Export-Csv` 将对象转换为逗号分隔值（CSV）表格格式。然后，你可以将此文件导入电子表格程序进行离线分析。代码清单 1-24 中的示例展示了这一过程。

```
PS> Get-Process | Select-Object Id, ProcessName |
Export-Csv processes.csv -NoTypeInformation
PS> Get-Content processes.csv
"Id","ProcessName"
"3352","ApplicationFrameHost"
"19424","audiodg"
"5192","bash"
"10784","Calculator"
--snip--
```

*代码清单 1-24：将对象导出为 CSV 格式*

如果你需要保留对象的完整结构，包括类型信息，那么 CLI XML 格式是更好的选择。这种格式可以序列化对象的属性和方法，并在重新导入时还原其原始状态。代码清单 1-25 展示了如何使用 `Export-CliXml` 和 `Import-CliXml` 命令以这种格式导出对象，然后重新导入它们。

```
PS> Get-Process | Select-Object Id, ProcessName | Export-CliXml processes.xml
PS> Get-Content processes.xml
<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <Obj RefId="0">
    <TNRef RefId="0" />
    <MS>
      <I32 N="Id">3352</I32>
      <S N="ProcessName">ApplicationFrameHost</S>
    </MS>
  </Obj>
--snip--
</Objs>
PS> $ps = Import-CliXml processes.xml
PS> $ps[0]
  Id ProcessName
  -- -----------
3352 ApplicationFrameHost
```

*代码清单 1-25：导出并重新导入 CLI XML 文件*

至此，我们结束了关于 PowerShell 语言的讨论。如果你有些生疏，我建议找一本关于该主题的好书来阅读，例如 Adam Bertram 所著的 *PowerShell for Sysadmins*（No Starch Press，2020年）。

### 总结

本章简要介绍了如何配置PowerShell环境，以便运行书中包含的代码示例。我们讨论了配置PowerShell以运行脚本，以及安装所需的外部PowerShell模块。

本章其余部分提供了关于PowerShell语言的一些背景知识，包括PowerShell语法的基础，以及如何使用`Get-Command`发现命令、使用`Get-Help`获取帮助，以及显示、筛选、分组和导出PowerShell对象。

掌握了PowerShell的基础知识后，我们可以开始深入探讨Windows操作系统的内部工作原理。在下一章中，我们将讨论Windows内核以及如何使用PowerShell与之交互。

## 2. Windows 内核

Windows 是一个安全的多用户操作系统。然而，它也是现代操作系统中细节最难以理解的操作系统之一。在深入探讨其安全机制之前，在本部分中，我将为您概述操作系统的结构。我们还将借此机会了解如何使用将成为本书核心的 PowerShell 模块。

我们将考虑运行中操作系统的两个部分：内核和用户模式应用程序。内核做出安全决策，决定用户可以在系统上执行哪些操作。然而，您在 Windows 机器上使用的大多数应用程序都在用户模式下运行。本章将重点介绍内核；下一章将重点介绍用户模式应用程序。

在以下各节中，我们将研究构成 Windows 内核的各种子系统。对于每个子系统，我将解释其用途以及如何使用它。我们将从对象管理器开始，在那里我们还将探讨系统调用，它允许用户模式应用程序访问内核对象。然后，我们将讨论输入/输出管理器、应用程序如何通过进程和线程管理器创建，以及内存如何通过内存管理器表示。在整个过程中，我将概述如何使用 PowerShell 检查这些子系统的行为。

### Windows 内核执行体

*Windows NTOS 内核执行体*，或简称*内核*，是 Windows 的核心。它提供操作系统所有特权功能，以及用户应用程序与硬件通信的接口。内核被划分为多个子系统，每个子系统都有专门的用途。图 2-1 显示了本书中最受关注的组件图。

![img](./image/01.%20PART%20I%20AN%20OVERVIEW%20OF%20THE%20WINDOWS%20OPERATING%20SYSTEM/Figure2-1.webp)

图 2-1：Windows 内核执行体模块

内核执行体中的每个子系统都公开 API 供其他子系统调用。如果您正在查看内核代码，可以通过其两个字符的前缀快速确定每个 API 属于哪个子系统。图 2-1 中子系统的前缀显示在表 2-1 中。

| 前缀 | 子系统 | 示例 |
| :------- | :------------------------- | :------------------------ |
| Nt 或 Zw | 系统调用接口 | NtOpenFile/ZwOpenFile |
| Se       | 安全参考监视器(Security Reference Monitor, SRM) | SeAccessCheck |
| Ob       | 对象管理器 | ObReferenceObjectByHandle |
| Ps       | 进程和线程管理器 | PsGetCurrentProcess |
| Cm       | 配置管理器 | CmRegisterCallback |
| Mm       | 内存管理器 | MmMapIoSpace |
| Io       | 输入/输出管理器 | IoCreateFile |
| Ci       | 代码完整性 | CiValidateFileObject |

我们将在以下各节中探讨所有这些子系统。

### SRM

就本书而言，*SRM* 是内核中最重要的子系统。它实现了限制哪些用户可以访问不同资源的安全机制。没有SRM，你将无法阻止其他用户访问你的文件。图2-2 展示了SRM及其相关的系统组件。

![img](./image/01.%20PART%20I%20AN%20OVERVIEW%20OF%20THE%20WINDOWS%20OPERATING%20SYSTEM/Figure2-2.webp)

图2-2：SRM的组件

系统上运行的每个进程在创建时都会分配一个*访问令牌*。这个访问令牌由SRM管理，并定义了与该进程关联的用户身份。随后，SRM可以执行一项称为*访问检查*的操作。此操作查询资源的*安全描述符(Security Descriptor)*，将其与进程的访问令牌进行比较，并计算授予的访问级别或指示调用者被拒绝访问。

SRM还负责在用户访问资源时生成*审计*事件。由于审计可能产生大量事件，默认情况下它是禁用的，因此管理员必须首先启用它。这些审计事件可用于识别系统上的恶意行为以及诊断安全配置错误。

SRM期望用户和组以称为*安全标识符(Security Identifier, SID)* 的二进制结构来表示。然而，对于用户来说，传递原始二进制SID并不方便，他们通常通过有意义的名称来引用用户和组（例如，用户*bob*或*Users*组）。这些名称需要在SRM使用之前转换为SID。名称与SID的转换任务由*本地安全机构(Local Security Authority, LSA)子系统（LSASS）* 处理，它运行在一个独立于任何已登录用户的特权进程中。

将每个可能的SID表示为名称是不可行的，因此微软定义了*安全描述符定义语言（SDDL）* 格式，将SID表示为字符串。SDDL可以表示资源的整个安全描述符，但目前我们仅用它来表示SID。在代码清单 2-1中，我们使用PowerShell通过Get-NtSid命令查找*Users*组名称；这应该会检索到该SID的SDDL字符串。




```
PS> Get-NtSid -Name "Users"
Name          Sid
----          ---
BUILTIN\Users S-1-5-32-545
```


*代码清单 2-1：使用Get-NtSid查询* Users *组的SID*

我们将*Users*组的名称传递给Get-NtSid，它返回完全限定的名称，并附加了本地域*BUILTIN*。*BUILTIN\Users*的SID在不同Windows系统之间始终相同。输出还包含SDDL格式的SID，可以分解为以下用破折号分隔的部分：

- S字符前缀。这表示后面是一个SDDL SID。
- SID结构的十进制版本。其固定值为1。
- 安全机构。机构5表示内置的NT机构。
- 两个十进制相对标识符（RID）。这里的RID（32和545）表示NT机构组。

我们还可以使用Get-NtSid执行反向操作，将SDDL SID转换回名称，如代码清单 2-2所示。


```
PS> Get-NtSid -Sddl "S-1-5-32-545"
Name          Sid
----          ---
BUILTIN\Users S-1-5-32-545
```


*代码清单 2-2：使用Get-NtSid查找与SID关联的名称*

我将在第4章至第9章中更深入地描述SRM及其功能，并在第5章讨论安全描述符时重新审视SID结构。现在，请记住SID代表用户和组，我们可以用SDDL形式的字符串来表示它们。接下来，我们将转向Windows内核执行体的另一个核心子系统——对象管理器。

### 对象管理器

在类 Unix 操作系统中，一切皆文件。而在 Windows 中，一切皆对象，这意味着每个文件、进程和线程在内核内存中都以对象结构表示。对安全而言重要的是，这些对象中的每一个都可以分配一个安全描述符，该描述符限制哪些用户可以访问该对象，并确定他们拥有的访问类型（例如，读取或写入）。

*对象管理器* 是内核中负责管理这些资源对象、其内存分配及其生命周期的组件。在本节中，我们首先讨论对象管理器支持的对象类型。然后，我们将探讨如何通过命名约定使用系统调用打开内核对象。最后，我们将研究如何使用系统调用返回的句柄来访问对象。

#### 对象类型

内核维护着其支持的所有对象类型的列表。这是必要的，因为每种对象类型具有不同的支持操作和安全属性。代码清单 2-3 展示了如何使用 Get-NtType 命令列出内核中所有支持的类型。


```
PS> Get-NtType
Name
----
Type
Directory
SymbolicLink
Token
Job
Process
Thread
--snip--
```

*代码清单 2-3：执行 Get-NtType*

我已截断了类型列表（我使用的机器支持 72 种类型），但即使在这个简短的部分中也有一些值得注意的条目。生成列表中的第一个条目是 Type；甚至内核类型的列表也是由对象构建的！其他值得注意的类型是 Process 和 Thread，它们分别代表进程和线程的内核对象。我们将在本章后面更详细地研究其他对象类型。

您可以使用 Format-List 显示类型的属性，这将返回有关该类型的附加信息。我们稍后会看一个示例，但现在的问题是，如何访问这些类型中的每一种。为了回答这个问题，我们需要讨论对象管理器命名空间。

#### 对象管理器命名空间

作为 Windows 用户，您通常会在资源管理器中看到文件系统驱动器。但在用户界面之下，还有一个专门用于内核对象的完整文件系统。对这个文件系统（称为 *对象管理器命名空间 (OMNS)*）的访问并未被很好地记录或向大多数开发者公开，这使得它更加有趣。

OMNS 由 目录对象（Directory objects）构建而成。这些对象的行为就像在文件系统中一样，因此每个目录包含其他对象，您可以将其视为文件。然而，它们与您熟悉的文件目录不同。每个目录都配置了一个安全描述符，该描述符决定哪些用户可以列出其内容，以及哪些用户可以在其中创建新的子目录和对象。您可以使用反斜杠分隔的字符串指定对象的完整路径。

我们可以通过本书 PowerShell 模块中提供的驱动器提供程序来枚举 OMNS。如 代码清单 2-4 所示，这通过列出 *NtObject* 驱动器将 OMNS 暴露为文件系统。


```
PS> ls NtObject:\ | Sort-Object Name
Name             TypeName
----             --------
ArcName          Directory
BaseNamedObjects Directory
BindFltPort      FilterConnectionPort
Callback         Directory
CLDMSGPORT       FilterConnectionPort
clfs             Device
CsrSbSyncEvent   Event
Device           Directory
Dfs              SymbolicLink
DosDevices       SymbolicLink
--snip--
```


*代码清单 2-4：列出根 OMNS 目录*

代码清单 2-4 显示了根 OMNS 目录的简短片段。默认情况下，此输出包括每个对象的名称和类型。我们可以看到一些 目录对象（Directory objects）；如果您有权限，可以列出它们。我们还可以看到另一个重要的类型，SymbolicLink。您可以使用符号链接将一个 OMNS 路径重定向到另一个。SymbolicLink 对象包含一个 SymbolicLinkTarget 属性，该属性本身包含链接的目标。




```
PS> ls NtObject:\Dfs | Select-Object SymbolicLinkTarget
SymbolicLinkTarget
------------------
\Device\DfsClient

PS> Get-Item NtObject:\Device\DfsClient | Format-Table
Name      TypeName
----      --------
DfsClient Device
```


*代码清单 2-5：显示符号链接的目标*

在此，我们列出 *NtObject* 驱动器的根目录，然后提取 SymbolicLinkTarget 属性以获取真实目标。接下来，我们检查目标路径 *Device\DfsClient*，以显示它是一个 Device 类型，这正是符号链接可用于访问的内容。

Windows 预配置了几个重要的目录对象，如 表 2-2 所示。

| 路径                     | 描述                                             |
| :----------------------- | :----------------------------------------------- |
| \BaseNamedObjects       | 用户对象的全局目录                               |
| \Device                 | 包含设备（如已挂载的文件系统）的目录             |
| \GLOBAL??               | 符号链接的全局目录，包括驱动器映射               |
| \KnownDlls              | 包含特殊、已知的 DLL 映射的目录                  |
| \ObjectTypes            | 包含命名对象类型的目录                           |
| \Sessions               | 独立控制台会话的目录                             |
| \Windows                | 与窗口管理器相关的对象的目录                     |
| \RPC Control            | 远程过程调用(Remote Procedure Call, RPC)端点的目录                           |

表 2-2中的第一个目录 *BaseNamedObjects (BNO)* 在对象管理器的上下文中非常重要。它允许任何用户创建命名内核对象。这个单一目录允许本地系统上不同用户之间共享资源。请注意，您不必在 BNO 目录中创建对象；这只是一个约定。

我将在本章后面更详细地描述其他对象目录。现在，您可以在 PowerShell 中通过给路径添加 *NtObject:* 前缀来列出它们，如 代码清单 2-5 所示。

#### 系统调用

我们如何从用户模式应用程序访问 OMNS 中的命名对象？如果我们处于用户模式应用程序中，我们需要内核来访问对象，并且我们可以使用系统调用接口在用户模式应用程序中调用内核模式代码。大多数系统调用对对象管理器公开的特定类型的内核对象执行某些操作。例如，NtCreateMutant 系统调用创建一个 Mutant 对象，这是一种用于锁定和线程同步的互斥原语。

系统调用的名称遵循常见模式。它以 Nt 或 Zw 开头。对于用户模式调用者，这两个前缀是等效的；但是，如果系统调用由在内核中执行的代码调用，则 Zw 前缀会更改安全检查过程。我们将在 第 7 章 中讨论访问模式时再回到 Zw 前缀的影响。

前缀之后是操作的动词：在 NtCreateMutant 的情况下是 Create。名称的其余部分与系统调用操作的内核对象类型相关。对内核对象执行操作的常见系统调用动词包括：

Create  创建新对象。映射到 New-Nt<Type> PowerShell 命令。

Open  打开现有对象。映射到 Get-Nt<Type> PowerShell 命令。

QueryInformation  查询对象信息和属性。

SetInformation  设置对象信息和属性。

某些系统调用执行特定于类型的操作。例如，NtQueryDirectoryFile 用于查询文件对象目录中的条目。让我们看一下 NtCreateMutant 系统调用的 C 语言原型，以了解典型调用需要传递哪些参数。如 代码清单 2-6 所示，NtCreateMutant 系统调用创建一个新的 Mutant 对象。


```
NTSTATUS NtCreateMutant(
    HANDLE* FileHandle,
    ACCESS_MASK DesiredAccess,
    OBJECT_ATTRIBUTES* ObjectAttributes,
    BOOLEAN InitialOwner
);
```


*代码清单 2-6：NtCreateMutant 的 C 原型*

系统调用的第一个参数是指向 HANDLE 的指针。在许多系统调用中很常见，此参数用于检索对象的已打开句柄（在本例中为 Mutant）。第二个参数是 DesiredAccess，它指定调用者请求的访问权限。此参数是访问检查的关键，因为对象管理器将使用它来确定调用者是否被允许访问对象。访问检查由SRM 执行，其结果取决于调用者的访问令牌和对象的安全描述符。我们将在下一节中更详细地讨论句柄和 DesiredAccess。

第三个参数是 ObjectAttributes 参数，它定义了要打开或创建的对象的属性。OBJECT_ATTRIBUTES 结构定义如 代码清单 2-7 所示。


```
struct OBJECT_ATTRIBUTES {
    ULONG           Length;
    HANDLE          RootDirectory;
    UNICODE_STRING* ObjectName;
    ULONG           Attributes;
    PVOID           SecurityDescriptor;
    PVOID           SecurityQualityOfService;
}
```


*代码清单 2-7：OBJECT_ATTRIBUTES 结构*

这个C语言结构以`Length`开头，表示结构的长度。在结构起始处指定长度是C语言中常见的习惯用法，以确保传递给系统调用的是正确的结构。

接下来是`RootDirectory`和`ObjectName`。这两个字段需结合使用，因为它们指示系统调用如何查找所访问的资源。`RootDirectory`是一个已打开内核对象的句柄，用作查找对象的基础。`ObjectName`字段是指向`UNICODE_STRING`结构的指针。这是一个计数字符串，在代码清单 2-8中定义为C语言结构。


```
struct UNICODE_STRING {
    USHORT Length;
    USHORT MaximumLength;
    WCHAR* Buffer;
};
```


*代码清单 2-8：UNICODE_STRING结构*

该结构通过`Buffer`引用字符串数据，`Buffer`是指向16位Unicode字符数组的指针。字符串以UCS-2编码表示；Windows早于Unicode的许多变更，如UTF-8和UTF-16。

`UNICODE_STRING`结构还包含两个长度字段：`Length`和`MaximumLength`。第一个长度字段表示`Buffer`指向的字符串的有效总长度，以字节为单位（而非Unicode字符数）。如果你有C编程背景，此长度不包括任何NUL终止字符。实际上，对象名称中允许包含NUL字符。

第二个长度字段表示`Buffer`指向的字符串的最大长度，以字节为单位。由于结构有两个独立的长度，可以分配一个最大长度较大但有效长度为零的空字符串，然后通过`Buffer`指针更新字符串值。请注意，长度存储为`USHORT`值，即无符号16位整数。结合以字节表示的长度，这意味着字符串最多可包含32,767个字符。

要指定对象的名称，你有两个选项：可以将`ObjectName`设置为绝对路径，例如*\BaseNamedObjects\ABC*，或者将`RootDirectory`设置为*\BaseNamedObjects*的目录对象，然后将ABC作为`ObjectName`传递。这两种操作将打开同一个对象。

回到代码清单 2-7，在`ObjectName`参数之后是`Attributes`，这是一组标志，用于修改对象名称查找过程或更改返回句柄的属性。表2-3列出了这些标志。

*表2-3：对象属性标志*

| 标志名称                     | 描述                                                         |
| :--------------------------- | :----------------------------------------------------------- |
| Inherit                      | 将句柄标记为可继承的。                                       |
| Permanent                    | 将对象标记为永久的。                                         |
| Exclusive                    | 如果创建新对象，则将其标记为独占的。只有同一进程才能打开该对象的句柄。 |
| CaseInsensitive              | 以不区分大小写的方式查找对象名称。                           |
| OpenIf                       | 如果使用Create调用，则打开现有对象的句柄（如果可用）。       |
| OpenLink                     | 如果对象是另一个对象的链接，则打开该对象；否则，跟随链接。此标志仅由配置管理器使用。 |
| KernelHandle                 | 在内核模式下使用时，将句柄作为内核句柄打开。这防止用户模式应用程序直接访问句柄。 |
| ForceAccessCheck             | 在内核模式下使用时，确保执行所有访问检查，即使调用系统调用的Zw版本也是如此。 |
| IgnoreImpersonatedDeviceMap  | 在模拟时禁用设备映射。                                       |
| DontReparse                  | 指示不跟随包含符号链接的任何路径。                           |

`OBJECT_ATTRIBUTES`结构中的最后两个字段允许调用者指定对象的安全服务质量（SQoS）和安全描述符。我们将在第4章中回到SQoS，并在第5章中讨论安全描述符。

在 代码清单 2-6 中的 `NtCreateMutant` 系统调用之后，是 `InitialOwner` 布尔参数，该参数特定于这种类型。在这种情况下，它表示创建的 Mutant 是否由调用者拥有。许多其他系统调用，尤其是针对文件的调用，具有更复杂的参数，我们将在本书后面详细讨论。

#### NTSTATUS 代码

所有系统调用都返回一个 32 位的 NTSTATUS 代码。此状态代码由多个组件打包到 32 位中组成，如 图 2-3 所示。



![img](./image/01.%20PART%20I%20AN%20OVERVIEW%20OF%20THE%20WINDOWS%20OPERATING%20SYSTEM/Figure2-3.webp)

图 2-3：NT 状态代码结构

最高的两位（第 31 和 30 位）表示状态代码的*严重性*。表 2-4 显示了可用的值。

| 严重性名称                  | 值    |
| :-------------------------- | :---- |
| STATUS_SEVERITY_SUCCESS     | 0     |
| STATUS_SEVERITY_INFORMATIONAL | 1   |
| STATUS_SEVERITY_WARNING     | 2     |
| STATUS_SEVERITY_ERROR       | 3     |

如果严重性级别表示警告或错误，则状态代码的第 31 位将被设置为 1。如果状态代码被视为有符号的 32 位整数，则该位表示负值。常见的编程实践是假设如果状态代码为负，则代表错误；如果为正，则代表成功。从表中可以看出，这种假设并不完全正确——负状态代码也可能是警告——但在实践中已经足够有效。

图 2-3 中的下一个组件 *CC* 是客户代码。这是一个单比特标志，指示状态代码是由 Microsoft 定义（值为 0）还是由第三方定义（值为 1）。第三方并没有义务严格遵循此约定，因此不能将其作为绝对的判断依据。

客户代码之后是 *R* 位，这是一个保留位，必须设置为 0。

接下来的 12 位表示*功能设施（Facility）*代码——即与该状态码关联的内核子系统或组件。微软已预先定义了约 50 个用于自身系统的功能设施代码（Facility）。第三方应定义自己的设施，并将其与客户代码结合，以区别于 Microsoft。表 2-5 显示了一些常见的设施。

| 设施名称        | 值    | 描述                                        |
| :-------------- | :---- | :------------------------------------------ |
| FACILITY_DEFAULT | 0    | 用于常见状态代码的默认设施                  |
| FACILITY_DEBUGGER | 1   | 用于与调试器关联的代码                      |
| FACILITY_NTWIN32 | 7    | 用于源自 Win32 API 的代码                   |

最后一个组件 *状态代码* 是一个 16 位数字，在其所属的功能设施（Facility）代码范围内保持唯一，由具体实现者定义每个数值的含义。PowerShell 模块包含一个示例，展示了如何从状态代码中提取信息，如 代码清单 2-9 所示。




```
PS> Get-NtStatus
Status     StatusName                Message
------     ----------                -------
00000000   STATUS_SUCCESS            STATUS_SUCCESS
00000001   STATUS_WAIT_1             STATUS_WAIT_1
00000080   STATUS_ABANDONED_WAIT_0   STATUS_ABANDONED_WAIT_0
000000C0   STATUS_USER_APC           STATUS_USER_APC
000000FF   STATUS_ALREADY_COMPLETE   The requested action was completed by...
00000100   STATUS_KERNEL_APC         STATUS_KERNEL_APC
00000101   STATUS_ALERTED            STATUS_ALERTED
00000102   STATUS_TIMEOUT            STATUS_TIMEOUT
00000103   STATUS_PENDING            The operation that was requested is p...
--snip--
```


*代码清单 2-9：从 NTSTATUS 代码中提取信息的示例*

注意一些状态值，如 STATUS_PENDING，具有人类可读的消息。此消息并未嵌入在 PowerShell 模块中；相反，它存储在 Windows 库中，可以在运行时提取。

当我们通过 PowerShell 命令调用系统调用时，其状态代码通过 .NET 异常呈现。例如，如果我们尝试打开一个不存在的目录对象，我们将在控制台中看到如 代码清单 2-10 所示的异常。




```
PS> Get-NtDirectory \THISDOESNOTEXIST
❶ Get-NtDirectory : (0xC0000034) - Object Name not found.
--snip--

PS> Get-NtStatus 0xC0000034 | Format-List
Status         : 3221225524
❷ StatusSigned   : -1073741772
StatusName     : STATUS_OBJECT_NAME_NOT_FOUND
Message        : Object Name not found.
Win32Error     : ERROR_FILE_NOT_FOUND
Win32ErrorCode : 2
Code           : 52
CustomerCode   : False
Reserved       : False
Facility       : FACILITY_DEFAULT
Severity       : STATUS_SEVERITY_ERROR
```


*代码清单 2-10：尝试打开不存在的目录时生成的 NTSTATUS 异常*

在代码清单 2-10中，我们使用`Get-NtDirectory`打开不存在的路径*THISDOESNOTEXIST*。这会生成NTSTATUS 0xC0000034异常，此处显示了解码后的消息❶。如果您想获取更多关于该状态码的信息，可以将其传递给`Get-NtStatus`，并将输出格式化为列表以查看其所有属性，包括Facility和Severity。NT状态码是一个无符号整数值；然而，通常也会看到它被（错误地）打印为有符号值❷。

#### 对象句柄

对象管理器处理指向内核内存的指针。用户模式应用程序无法直接读写内核内存，那么它如何访问对象呢？它通过系统调用返回的句柄来实现，如前一节所述。每个正在运行的进程都有一个关联的*句柄表*，其中包含三条信息：

- 句柄的数字标识符
- 授予句柄的访问权限；例如，读或写
- 指向内核内存中对象结构的指针

在内核可以使用句柄之前，系统调用实现必须通过内核API（如`ObReferenceObjectByHandle`）从句柄表中查找内核对象指针。通过间接提供此句柄，内核组件可以将句柄编号返回给用户模式应用程序，而无需直接暴露内核对象。图2-4展示了句柄查找过程。

![img](./image/01.%20PART%20I%20AN%20OVERVIEW%20OF%20THE%20WINDOWS%20OPERATING%20SYSTEM/Figure2-4.webp)

图2-4：句柄表查找过程

在图2-4中，用户进程正尝试对Mutant对象执行某些操作。当用户进程想要使用句柄时，它必须首先将句柄值传递给我们在前一节中定义的系统调用❶。然后，系统调用实现调用内核API，通过引用进程句柄表中句柄的数字值将句柄转换为内核指针❷。

为了确定是否授予访问权限，API会考虑用户为系统调用操作请求的访问类型，以及所访问对象的类型。如果请求的访问与句柄表条目中记录的授予访问不匹配，API将返回`STATUS_ACCESS_DENIED`，转换操作将失败。同样，如果对象类型不匹配❸，API将返回`STATUS_OBJECT_TYPE_MISMATCH`。

这两个检查对安全性至关重要。访问检查确保用户无法对没有访问权限的句柄执行操作（例如，对只有读访问权限的文件进行写入）。类型检查确保用户没有传递不相关的内核对象类型，这可能导致内核中的类型混淆，从而引发内存损坏等安全问题。如果转换成功，系统调用现在拥有指向对象的内核指针，可以使用它来执行用户请求的操作。

##### 访问掩码

句柄表中的授予访问值是一个32位位域，称为*访问掩码*。这与系统调用中指定的`DesiredAccess`参数使用的位域相同。我们将在第7章中更详细地讨论`DesiredAccess`和访问检查过程如何确定授予访问。

访问掩码有四个组件，如图2-5所示。

![img](./image/01.%20PART%20I%20AN%20OVERVIEW%20OF%20THE%20WINDOWS%20OPERATING%20SYSTEM/Figure2-5.webp)

图2-5：访问掩码结构

最重要的是16位*类型特定访问组件*，它定义了特定内核对象类型上允许的操作。例如，File对象可能有单独的位来指定使用句柄时是否允许读取或写入文件。相比之下，同步Event可能只有一个位，允许事件被触发。

向后看，访问掩码的*标准访问*组件定义了适用于任何对象类型的操作。这些操作包括：

- 删除  移除对象；例如，从磁盘或注册表中删除

- 读取控制  读取对象的安全描述符信息

- 写入DAC  将安全描述符的自由访问控制列表(Access Control List, ACL)写入对象

- 写入所有者  将所有者信息写入对象

- 同步等待对象；例如，等待进程退出或互斥体被解锁。


我们将在第5章和第6章中更详细地介绍与安全相关的访问。

在此之前是*保留*和*特殊访问*位。这些位大多为保留位，但包含两个访问值：

- AccessSystemSecurity  读取或写入对象的审计信息

- MaximumAllowed  在执行访问检查时请求对对象的最大访问权限


我们将在第9章中介绍AccessSystemSecurity访问，在第7章中介绍MaximumAllowed访问。

最后，访问掩码的四个高位（*通用访问*组件）仅在使用系统调用的DesiredAccess参数请求内核对象访问时使用。共有四大类访问：GenericRead、GenericWrite、GenericExecute和GenericAll。

当您请求这些通用访问权限之一时，SRM会首先将访问转换为相应的类型特定访问。这意味着您永远不会收到带有GenericRead的句柄；相反，您将获得代表该类型读操作的具体访问掩码。为便于转换，每种类型都包含一个*通用映射表*，将四个通用类别映射到类型特定访问。我们可以使用Get-NtType显示映射表，如代码清单 2-11所示。


```
PS> Get-NtType | Select-Object Name, GenericMapping
Name                            GenericMapping
----                            --------------
Type                            R:00020000 W:00020000 E:00020000 A:000F0001
Directory                       R:00020003 W:0002000C E:00020003 A:000F000F
SymbolicLink                    R:00020001 W:00020000 E:00020001 A:000F0001
Token                           R:0002001A W:000201E0 E:00020005 A:000F01FF
--snip--
```


*代码清单 2-11：显示对象类型的通用映射表*

类型数据不提供每个特定访问掩码的名称。然而，对于所有常见类型，PowerShell模块提供了一个枚举类型来表示类型特定访问。我们可以通过Get-NtTypeAccess命令访问此类型。代码清单 2-12展示了File类型的示例。


```
PS> Get-NtTypeAccess -Type File
Mask       Value                GenericAccess
----       -----                -------------
00000001   ReadData             Read, All
00000002   WriteData            Write, All
00000004   AppendData           Write, All
00000008   ReadEa               Read, All
00000010   WriteEa              Write, All
00000020   Execute              Execute, All
00000040   DeleteChild          All
00000080   ReadAttributes       Read, Execute, All
00000100   WriteAttributes      Write, All
00010000   Delete               All
00020000   ReadControl          Read, Write, Execute, All
00040000   WriteDac             All
00080000   WriteOwner           All
00100000   Synchronize          Read, Write, Execute, All
```


*代码清单 2-12：显示File对象类型的访问掩码*

Get-NtTypeAccess命令的输出显示访问掩码值、PowerShell模块已知的访问名称以及它将映射到的通用访问。请注意，某些访问类型仅授予All；这意味着即使您请求了通用读、写和执行访问，也不会获得这些权限。

软件开发工具包（SDK）名称

为提高可用性，PowerShell模块修改了Windows软件开发工具包（SDK）中访问权限的原始名称。您可以使用Get-NtTypeAccess命令的SDKName属性查看等效的SDK名称：


```
PS> Get-NtTypeAccess -Type File | Select SDKName, Value
SDKName                  Value
-------                  -----
FILE_READ_DATA        ReadData
FILE_WRITE_DATA      WriteData
FILE_APPEND_DATA    AppendData
--snip--
```


这些名称映射对于将原生代码移植到PowerShell非常有用。

您可以使用Get-NtAccessMask命令在数值访问掩码和特定对象类型之间进行转换，如代码清单 2-13所示。


```
PS> Get-NtAccessMask -FileAccess ReadData, ReadAttributes, ReadControl
Access
------
00020081

PS> Get-NtAccessMask -FileAccess GenericRead
Access
------
80000000

PS> Get-NtAccessMask -FileAccess GenericRead -MapGenericRights
Access
------
00120089

PS> Get-NtAccessMask 0x120089 -AsTypeAccess File
ReadData, ReadEa, ReadAttributes, ReadControl, Synchronize
```


*代码清单 2-13：使用Get-NtAccessMask转换访问掩码*

在代码清单 2-13中，我们为File类型指定了访问权限，该命令使用File类型的通用映射转换为特定访问掩码。最后，我们使用AsTypeAccess参数将原始访问掩码转换回类型访问，并指定要使用的内核类型。

如代码清单 2-14所示，您可以通过PowerShell对象的GrantedAccess属性查询对象句柄的已授予访问掩码。这将返回访问掩码的枚举类型格式。要检索数值，请使用GrantedAccessMask属性。


```
PS> $mut = New-NtMutant
PS> $mut.GrantedAccess
ModifyState, Delete, ReadControl, WriteDac, WriteOwner, Synchronize

PS> $mut.GrantedAccessMask
Access
------
001F0001
```


*代码清单 2-14：使用GrantedAccessMask显示访问掩码的数值*

内核通过 `NtQuerySystemInformation` 系统调用提供了一个功能，用于转储系统上所有句柄表条目。我们可以使用 PowerShell 中的 `Get-NtHandle` 命令访问句柄表，如 代码清单 2-15 所示。


```
PS> Get-NtHandle -ProcessId $pid
ProcessId  Handle     ObjectType           Object               GrantedAccess
---------  ------     ----------           ------               -------------
22460      4          Process              FFFF800224F02080     001FFFFF
22460      8          Thread               FFFF800224F1A140     001FFFFF
22460      12         SymbolicLink         FFFF9184AC639FC0     000F0001
22460      16         Mutant               FFFF800224F26510     001F0001
--snip--
```


*代码清单 2-15：使用 Get-NtHandle 显示当前进程的句柄表*

每个句柄条目包含对象的类型、内核对象在内核内存中的地址以及授予的访问掩码。

一旦应用程序使用完句柄，可以通过 `NtClose` API 关闭它。如果您从 Get 或 New 调用中收到了 PowerShell 对象，则可以调用该对象的 `Close` 方法关闭句柄。您还可以在 PowerShell 中使用 `Use-NtObject` 命令自动关闭对象句柄，该命令会调用一个脚本块，在脚本块执行完毕后自动关闭句柄。代码清单 2-16 提供了这两种方法的示例。


```
PS> $m = New-NtMutant \BaseNamedObjects\ABC
PS> $m.IsClosed
False

PS> $m.Close()
PS> $m.IsClosed
True

PS> Use-NtObject($m = New-NtMutant \BaseNamedObjects\ABC) {
    $m.FullPath
}
\BaseNamedObjects\ABC

PS> $m.IsClosed
True
```


*代码清单 2-16：关闭对象句柄*

如果您不手动关闭句柄，.NET 垃圾回收器会自动关闭未被引用（例如，保存在 PowerShell 变量中）的对象的句柄。不过，您应该养成手动关闭句柄的习惯；否则，您可能需要等待很长时间才能释放资源，因为垃圾回收器可能在任何时候运行。

如果内核对象结构不再被引用，无论是通过句柄还是内核组件，该对象也会被销毁。一旦对象被销毁，其所有分配的内存都会被清理，如果它在 OMNS 中存在名称，该名称也会被移除。

##### 永久对象

可以让内核将对象标记为永久对象，防止对象在所有句柄关闭时被销毁，并允许其名称保留在 OMNS 中。要使对象永久化，您需要在创建对象时指定 `Permanent` 属性标志，或者使用系统调用 `NtMakePermanentObject`，该调用映射到任何 Get 或 New 命令返回的对象句柄上的 `MakePermanent` 调用。您需要特殊特权 `SeCreatePermanentPrivilege` 才能执行此操作；我们将在 第 4 章 中讨论特权。

相反的操作，`NtMakeTemporaryObject`（或 PowerShell 中的 `MakeTemporary` 方法），会移除永久设置并允许对象被销毁。销毁不会发生，直到所有指向该对象的句柄都已关闭。此操作不需要任何特殊特权，但确实需要对对象具有 Delete 访问权限才能成功。

请注意，File 和 Key 对象始终具有永久名称，因为它们不存在于 OMNS 中；要移除这些类型对象的名称，您必须使用系统调用显式删除它们。

##### 句柄复制

您可以使用 `NtDuplicateObject` 系统调用复制句柄。您可能想要这样做的主要原因是允许进程对内核对象进行额外引用。内核对象在所有句柄关闭之前不会被销毁，因此创建新句柄可以维持内核对象的存在。

如果源进程和目标进程的句柄具有 `DupHandle` 访问权限，则句柄复制还可以用于在进程之间传输句柄。您还可以使用句柄复制来减少句柄上的访问权限。例如，当您将文件句柄传递给新进程时，您可以仅授予复制句柄读取访问权限，防止新进程写入该对象。但是，您不应依赖此方法来减少句柄的授予访问权限；如果拥有句柄的进程可以访问该资源，它只需重新打开即可获得访问权限。

代码清单 2-17 展示了使用 `Copy-NtObject` 命令（封装了 `NtDuplicateObject`）在同一进程内进行复制的一些示例。我们将在 第 8 章 中再次讨论句柄复制和安全检查。


```
❶ PS> $mut = New-NtMutant "\BaseNamedObjects\ABC"
PS> $mut.GrantedAccess
ModifyState, Delete, ReadControl, WriteDac, WriteOwner, Synchronize

❷ PS> Use-NtObject($dup = Copy-NtObject $mut) {
    $mut
    $dup
    Compare-NtObject $mut $dup
}
Handle Name NtTypeName Inherit ProtectFromClose
------ ---- ---------- ------- ----------------
1616   ABC  Mutant     False   False
2212   ABC  Mutant     False   False
True

❸ PS> $mask = Get-NtAccessMask -MutantAccess ModifyState
PS> Use-NtObject($dup = Copy-NtObject $mut -DesiredAccessMask $mask) {
    $dup.GrantedAccess
    Compare-NtObject $mut $dup
}
ModifyState
True
```


*代码清单 2-17：使用 Copy-NtObject 复制句柄*

首先，我们创建一个新的 Mutant 对象来测试句柄复制，并提取当前授予的访问权限，结果显示有六种访问权限 ❶。对于初始复制，我们将保持相同的授予访问权限 ❷。你可以在输出的第一列中看到句柄是不同的。然而，我们调用 `Compare-NtObject` 来确定这两个句柄是否指向相同的底层内核对象，返回结果为 `True`。接下来，我们获取 Mutant 的 `ModifyState` 访问权限的访问掩码，并复制句柄，请求该访问权限 ❸。我们可以在输出中看到，授予的访问权限现在仅为 `ModifyState`。然而，`Compare-NtObject` 的返回值仍然表明这两个句柄指向同一个对象。

与句柄复制相关的还有句柄属性 `Inherit` 和 `ProtectFromClose`。设置 `Inherit` 允许新进程在创建时继承该句柄。这允许你将句柄传递给新进程，以执行诸如将控制台输出文本重定向到文件等任务。

设置 `ProtectFromClose` 可保护句柄不被关闭。你可以通过设置对象的 `ProtectFromClose` 属性来设置此属性，这将在原生句柄上设置该属性。代码清单 2-18 展示了其使用示例。




```
PS> $mut = New-NtMutant
PS> $mut.ProtectFromClose = $true
PS> Close-NtObject -SafeHandle $mut.Handle -CurrentProcess
STATUS_HANDLE_NOT_CLOSABLE
```


*代码清单 2-18：测试 ProtectFromClose 句柄属性*

任何关闭句柄的尝试都会以 `STATUS_HANDLE_NOT_CLOSABLE` 状态码失败，并且句柄将保持打开状态。

#### 查询和设置信息系统调用

内核对象通常存储有关其状态的信息。例如，进程对象存储其创建时的时间戳。为了允许我们检索此信息，内核可能已经实现了一个特定的“获取进程创建时间”系统调用。然而，由于各种对象类型存储的信息量庞大，这种方法很快就会变得不可行。

相反，内核实现了通用的查询和设置信息系统调用，其参数遵循所有内核对象类型的通用模式。代码清单 2-19 展示了查询信息系统调用的模式，以进程类型为例；对于其他类型，只需将 `Process` 替换为内核类型的名称。


```
NTSTATUS NtQueryInformationProcess(
    HANDLE                    Handle,
    PROCESS_INFORMATION_CLASS InformationClass,
    PVOID                     Information,
    ULONG                     InformationLength,
    PULONG                    ReturnLength
)
```


*代码清单 2-19：进程类型的查询信息系统调用示例*

所有查询信息系统调用都将对象句柄作为第一个参数。第二个参数 `InformationClass` 描述了要查询的进程信息类型。信息类是一个枚举值；SDK 指定了信息类的名称，我们可以提取并在 PowerShell 中实现。查询某些类型的信息可能需要特殊权限或管理员访问权限。

对于每个信息类，我们需要指定一个不透明缓冲区来接收查询的信息，以及缓冲区的长度。系统调用还会返回一个长度值，该值有两个用途：如果系统调用成功，它指示缓冲区中有多少内容被填充；如果系统调用失败，它指示缓冲区需要多大，并返回 `STATUS_INFO_LENGTH_MISMATCH` 或 `STATUS_BUFFER_TOO_SMALL`。

然而，你应该谨慎依赖返回的长度来确定传递给查询的缓冲区大小。某些信息类和类型在提供的缓冲区过小时不会正确设置所需的长度。这使得在不预先知道数据格式的情况下查询数据变得困难。不幸的是，即使是 SDK 也很少记录所需的确切大小。

如 代码清单 2-20 所示，设置信息调用遵循类似的模式。主要区别在于没有返回长度参数，并且在这种情况下，缓冲区是系统调用的输入。




```
NTSTATUS NtSetInformationProcess(
    HANDLE                    Handle,
    PROCESS_INFORMATION_CLASS InformationClass,
    PVOID                     Information,
    ULONG                     InformationLength
)
```


*代码清单 2-20：进程类型的设置信息系统调用示例*

在 PowerShell 模块中，你可以使用 `Get-NtObjectInformation` 和 `Set-NtObjectInformation` 命令来调用这些系统调用。例如，要查询进程信息类，可以使用 `Get-NtObjectInformation` 命令，如 代码清单 2-21 所示。请注意，某些信息类名称可能从列表中缺失，因为微软并不总是记录它们。




```
PS> Get-NtObjectInformationClass Process
Key                     Value
---                     -----
ProcessBasicInformation     0
ProcessQuotaLimits          1
ProcessIoCounters           2
ProcessVmCounters           3
ProcessTimes                4
--snip--
```


*代码清单 2-21：列出进程类型的信息类*

要调用查询信息系统调用，可使用 `Get-NtObjectInformation`，并指定一个打开的对象句柄和信息类别。要调用设置信息，则使用 `Set-NtObjectInformation`。代码清单 2-22 展示了如何使用 `Get-NtObjectInformation` 的示例。




```
PS> $proc = Get-NtProcess -Current
❶ PS> Get-NtObjectInformation $proc ProcessTimes
Get-NtObjectInformation : (0xC0000023) - {Buffer Too Small}
The buffer is too small to contain the entry. No information has been written to the buffer.
--snip--

❷ PS> Get-NtObjectInformation $proc ProcessTimes -Length 32
43
231
39
138
--snip--

❸ PS> Get-NtObjectInformation $proc ProcessTimes -AsObject
CreateTime         ExitTime KernelTime UserTime
----------         -------- ---------- --------
132480295787554603 0        35937500   85312500
```


*代码清单 2-22：查询进程对象的基本信息*

`Process` 类型未为 `ProcessTimes` 信息类别设置返回长度，因此如果不指定任何长度，操作会生成 `STATUS_BUFFER_TOO_SMALL` 错误❶。然而，通过检查或暴力尝试，您可以发现数据长度为 32 字节。使用 `Length` 参数❷指定此值后，查询即可成功，并返回字节数组形式的数据。

对于许多信息类别，`Get-NtObjectInformation` 命令已知查询数据的大小和结构。如果指定 `AsObject` 参数❸，您将获得预格式化的对象，而非字节数组。

此外，对于许多信息类别，句柄对象本身已公开了用于设置或查询值的属性和方法。这些值会被解码为使用格式；例如，在代码清单 2-22中，时间采用内部格式。对象上的 `CreationTime` 属性会以人类可读的日期和时间格式呈现。




```
PS> $proc | Format-List
SessionId       : 2
ProcessId       : 5484
ParentProcessId : 8108
PebAddress      : 46725963776
--snip--

PS> $proc.CreationTime
Saturday, October 24, 17:12:58
```


*代码清单 2-23：查询句柄对象的属性并检查 `CreationTime`*

类型的 `QueryInformation` 和 `SetInformation` 类别通常具有相同的枚举值。内核可以将信息类别的枚举值限制为一种操作类型，如果值无效，则返回 `STATUS_INVALID_INFO_CLASS` 状态码。对于某些类型（如注册表键），查询和设置的信息类别有所不同，如代码清单 2-24所示。




```
PS> Get-NtObjectInformationClass Key
Key                     Value
---                     -----
KeyBasicInformation         0
--snip--

PS> Get-NtObjectInformationClass Key -Set
Key                     Value
---                     -----
KeyWriteTimeInformation     0
--snip--
```


*代码清单 2-24：检查 `Key` 类型的 `QueryInformation` 和 `SetInformation` 类别*

仅使用类型名称调用 `Get-NtObjectInformationClass` 会返回 `QueryInformation` 类别。如果指定类型名称和 `Set` 参数，则会获得 `SetInformation` 类别。请注意，显示的两个条目名称不同，因此代表不同的信息。

### 输入/输出管理器

输入/输出（I/O）管理器通过*设备驱动程序*提供对I/O设备的访问。这些驱动程序的主要目的是实现文件系统。例如，当您在计算机上打开文档时，文件通过文件系统驱动程序变得可用。I/O管理器还支持其他类型的驱动程序，例如键盘和显卡等设备，但这些驱动程序实际上只是文件系统驱动程序的变体。

您可以通过`NtLoadDriver`系统调用手动加载新驱动程序，或使用即插即用（PnP）管理器自动加载。对于每个驱动程序，I/O管理器都会在*Driver*目录中创建一个条目。只有管理员才能列出此目录的内容。幸运的是，作为普通用户，您无需访问*Driver*目录中的任何内容。相反，您可以通过通常在*Device*目录中创建的设备对象与驱动程序交互。

驱动程序负责使用`IoCreateDevice` API创建新的设备对象。一个驱动程序可以关联多个设备对象；如果不需要用户交互，它也可以关联零个设备对象。如代码清单 2-25所示，我们可以通过OMNS以普通用户身份列出*Device*目录的内容。




```
PS> ls NtObject:\Device
Name                                     TypeName
----                                     --------
_HID00000034                             Device
DBUtil_2_3                               Device
000000c7                                 Device
000000b3                                 Device
UMDFCtrlDev-0f8ff736-55d7-11ea-b5d8-2... Device
0000006a                                 Device
--snip--
```


*代码清单 2-25：显示设备对象*

在输出中，我们可以看到对象的类型名称都是Device。但是，如果您寻找名称中包含Device的系统调用，您将一无所获。这是因为我们不使用专用的系统调用与I/O管理器交互；而是使用文件对象系统调用，如`NtCreateFile`。我们可以通过`New-NtFile`和`Get-NtFile`访问这些系统调用，它们分别用于创建和打开文件，如代码清单 2-26所示。




```
PS> Use-NtObject($f = Get-NtFile "\SystemRoot\notepad.exe") {
    $f | Select-Object FullPath, NtTypeName
}
FullPath                                    NtTypeName
--------                                    ----------
❶ \Device\HarddiskVolume3\Windows\notepad.exe File

PS> Get-Item NtObject:\Device\HarddiskVolume3
Name            TypeName
----            --------
HarddiskVolume3 Device
```


*代码清单 2-26：打开设备对象并显示其卷路径*

在此示例中，我们从*Windows*目录打开*notepad.exe*。*SystemRoot*符号链接指向系统驱动器上的*Windows*目录。由于*SystemRoot*符号链接是OMNS的一部分，OMNS最初处理文件访问。通过打开的句柄，我们可以选择文件的完整路径和类型名称。

查看结果，我们可以看到完整路径以*Device\HarddiskVolume3\*开头。如果我们尝试显示设备，我们会发现它的类型是Device。一旦对象管理器找到设备对象，它就将路径的其余部分的责任移交给I/O管理器，后者调用内核驱动程序中的适当方法。

我们可以使用`Get-NtKernelModule`命令列出加载到内核中的驱动程序（代码清单 2-27）。




```
PS> Get-NtKernelModule
Name         ImageBase        ImageSize
----         ---------        ---------
ntoskrnl.exe FFFFF8053BEAA000 11231232
hal.dll      FFFFF8053BE07000 667648
kd.dll       FFFFF8053B42E000 45056
msrpc.sys    FFFFF8053B48E000 393216
ksecdd.sys   FFFFF8053B45E000 172032
--snip--
```


*代码清单 2-27：枚举所有已加载的内核驱动程序*

与其他操作系统（如Linux）不同，Windows不通过内置系统调用实现核心网络协议（如TCP/IP）。相反，Windows有一个I/O管理器驱动程序，即*辅助功能驱动程序（AFD）*，它为应用程序提供对网络服务的访问。您无需直接处理该驱动程序；Win32提供了一个BSD套接字风格的API，称为*WinSock*，用于处理对它的访问。除了标准的互联网协议套件（如TCP/IP）外，AFD还实现了其他网络套接字类型，例如Unix套接字和用于与虚拟机通信的定制Hyper-V套接字。

关于I/O管理器，我们暂时就介绍到这里。接下来，让我们转向另一个重要的子系统，进程和线程管理器。

### 进程与线程管理器

所有用户模式代码都运行在*进程*的上下文中，每个进程包含一个或多个*线程*来控制代码的执行。进程和线程都是可安全保护的资源。这很合理：如果你能访问一个进程，你就能修改其代码并以不同用户身份的上下文执行它。因此，与大多数其他内核对象不同，你不能通过名称打开进程或线程。相反，你必须通过唯一的数字*进程ID（PID）*或*线程ID（TID）*来打开它们。

要获取正在运行的进程和线程列表，你可以通过调用打开系统调用并尝试每个可能的ID来暴力枚举ID空间，但这会花费较长时间。幸运的是，`NtQuerySystemInformation`系统调用提供了`SystemProcessInformation`信息类，使我们无需访问进程对象即可枚举进程和线程。

我们可以使用`Get-NtProcess`和`Get-NtThread`命令并传入`InfoOnly`参数来访问进程和线程列表，如代码清单 2-28所示。我们也可以使用内置的`Get-Process`命令来产生类似的输出。每个返回的对象都有一个`Threads`属性，我们可以查询该属性以获取线程信息。

```
PS> Get-NtProcess -InfoOnly
PID PPID Name          SessionId
--- ---- ----          ---------
0   0    Idle          0
4   0    System        0
128 4    Secure System 0
192 4    Registry      0
812 4    smss.exe      0
920 892  csrss.exe     0
--snip--

PS> Get-NtThread -InfoOnly
TID PID ProcessName StartAddress
--- --- ----------- ------------
0   0   Idle        FFFFF8004C9CAFD0
0   0   Idle        FFFFF8004C9CAFD0
--snip--
```

*代码清单 2-28：无需高权限即可显示进程和线程*

输出中列出的前两个进程是特殊的。第一个是空闲进程，其PID为0。这个进程包含在系统空闲时执行的线程，因此得名。你通常不需要处理它。第二个是系统进程，PID为4。这个进程很重要，因为它完全在内核模式下运行。当内核或驱动程序需要执行后台线程时，该线程与系统进程关联。

要打开进程或线程，我们需要知道其PID或TID。我们可以使用`OpenProcess`或`OpenThread` API，或者使用`Get-NtProcess`和`Get-NtThread`命令。例如，代码清单 2-29展示了如何查询当前进程的命令行和可执行文件路径。

```
PS> $proc = Get-NtProcess -ProcessId $pid
PS> $proc.CommandLine
"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

PS> $proc.Win32ImagePath
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
```

*代码清单 2-29：通过进程ID打开当前进程*

当你使用ID打开进程或线程对象时，你将收到一个句柄。为方便起见，内核还支持两个*伪句柄*，分别引用当前进程和当前线程。当前进程的伪句柄是转换为句柄的值-1，当前线程的伪句柄是-2。你可以通过向`Get-NtProcess`和`Get-NtThread`命令传递`Current`参数而不是ID来访问这些伪句柄。

请注意，进程及其线程的安全性相互独立。如果你知道线程的ID，即使无法访问进程本身，也有可能访问进程内的线程句柄。

### 内存管理器

每个进程都有自己独立的虚拟内存地址空间，供开发者按需使用。32位进程最多可访问2GB的虚拟内存地址空间（在64位Windows上为4GB），而64位进程则可访问高达128TB。内核的*内存管理器*子系统负责分配这一地址空间。

你的计算机不太可能拥有128TB的物理内存，但内存管理器有办法让它看起来比实际物理内存更多。例如，它可以使用文件系统上的专用文件，称为*页面文件*，在内存暂时不需要时存储数据。由于文件系统的可用存储空间远大于计算机的物理内存，这可以营造出大内存的假象。

虚拟内存空间由内存分配共享，它存储每个进程的运行状态及其可执行代码。每个内存分配可以有一系列保护状态，如只读或读写，这些状态必须根据内存的用途来设置。例如，要执行代码，内存的保护状态必须是执行读或执行读写。

如果你对进程句柄拥有查询有限信息访问权限，可以通过调用`NtQueryVirtualMemory`查询进程的所有内存状态信息。然而，读取和写入内存数据分别需要`VmRead`和`VmWrite`访问权限，并调用`NtReadVirtualMemory`和`NtWriteVirtualMemory`。

可以使用`NtAllocateVirtualMemory`和`NtFreeVirtualMemory`在进程中分配新内存和释放内存，这两者都需要`VmOperation`访问权限。最后，你可以使用`NtProtectVirtualMemory`更改内存的保护状态，这也需要`VmOperation`访问权限。

#### NtVirtualMemory命令

PowerShell通过`Get-`、`Add-`、`Read-`、`Write-`、`Remove-`和`Set-NtVirtualMemory`命令封装了这些系统调用。请注意，这些命令都接受一个可选的`Process`参数，允许你访问不同于当前进程的内存。代码清单 2-30展示了这些命令的实际应用。

```
❶ PS> Get-NtVirtualMemory
Address          Size   Protect          Type    State   Name
-------          ----   -------          ----    -----   ----
000000007FFE0000 4096   ReadOnly         Private Commit
000000007FFEF000 4096   ReadOnly         Private Commit
000000E706390000 241664 None             Private Reserve
000000E7063CB000 12288  ReadWrite, Guard Private Commit
000000E7063CE000 8192   ReadWrite        Private Commit
000000F6583F0000 12288  ReadOnly         Mapped  Commit  powershell.exe.mui
--snip--

❷ PS> $addr = Add-NtVirtualMemory -Size 1000 -Protection ReadWrite
PS> Get-NtVirtualMemory -Address $addr
Address          Size   Protect          Type    State   Name
-------          ----   -------          ----    -----   ----
000002624A440000 4096   ReadWrite        Private Commit

❸ PS> Read-NtVirtualMemory -Address $addr -Size 4 | Out-HexDump
00 00 00 00

❹ PS> Write-NtVirtualMemory -Address $addr -Data @(1,2,3,4)
4

❺ PS> Read-NtVirtualMemory -Address $addr -Size 4 | Out-HexDump
01 02 03 04

❻ PS> Set-NtVirtualMemory -Address $addr -Protection ExecuteRead -Size 4
ReadWrite

❼ PS> Get-NtVirtualMemory -Address $addr
Address          Size   Protect          Type    State   Name
-------          ----   -------          ----    -----   ----
000002624A440000 4096   ExecuteRead      Private Commit

❽ PS> Remove-NtVirtualMemory -Address $addr
PS> Get-NtVirtualMemory -Address $addr
Address          Size   Protect          Type    State   Name
-------          ----   -------          ----    -----   ----
000002624A440000 196608 NoAccess         None    Free
```

*代码清单 2-30：对进程执行各种内存操作*

在这里，我们执行了几项操作。首先，我们使用`Get-NtVirtualMemory`列出当前进程使用的所有内存区域❶。返回的列表会很大，但这里显示的摘录应该能让你大致了解信息的呈现方式。它包括内存区域的地址、大小、保护状态和状态。有三种可能的状态值：

提交  表示虚拟内存区域已分配并可供使用。

保留  表示虚拟内存区域已分配，但目前没有后备内存。使用保留的内存区域会导致崩溃。

空闲  表示虚拟内存区域未使用。使用空闲的内存区域会导致崩溃。

你可能会好奇，如果使用保留和空闲内存区域都会导致崩溃，那么保留和空闲之间有什么区别。保留状态允许你为将来使用预留虚拟内存区域，这样其他任何东西都无法在该内存地址范围内分配内存。你可以稍后通过重新调用`NtAllocateVirtualMemory`将保留状态转换为提交状态。空闲状态表示可供分配的区域。我们将在本节稍后介绍`Type`和`Name`列的含义。

接下来，我们分配一个1000字节的读/写区域，并将地址捕获到一个变量中❷。将地址传递给`Get-NtVirtualMemory`允许我们仅查询该特定虚拟内存区域。你可能会注意到，尽管我们请求了1000字节的区域，但返回的区域大小是4096字节。这是因为内存管理器以页面为单位分配内存，页面大小通常是4096字节。

接下来，我们读取并写入刚分配的内存区域。首先，我们使用`Read-NtVirtualMemory`读取该内存区域的4个字节，发现这些字节全为零❸。然后，我们使用`Write-NtVirtualMemory`将字节1、2、3和4写入该内存区域❹。我们再次读取这些字节以确认写入操作成功❺；两个值应该匹配，如输出所示。

内存分配完成后，我们可以使用 `Set-NtVirtualMemory` 更改保护属性。在此例中，我们通过将保护属性指定为 `ExecuteRead` ❻，使分配的内存可执行。使用 `Get-NtVirtualMemory` 命令查询内存区域的当前状态 ❼，显示保护属性已从 `ReadWrite` 更改为 `ExecuteRead`。同时请注意，尽管我们仅请求更改4字节的保护属性，但整个4,096字节的区域现在都可执行。这同样是由于最小内存分配大小的限制。

最后，我们使用 `Remove-NtVirtualMemory` 释放内存，并验证内存现在处于 `Free` 状态 ❽。通过 `NtAllocateVirtualMemory` 分配的内存被视为私有内存，如 代码清单 2-30 中 `Type` 属性的值所示。

#### 节对象

分配虚拟内存的另一种方式是通过节对象。节对象是一种内核类型，用于实现内存映射文件。我们可以将节对象用于两个相关目的：

- 将文件读取或写入，如同整个文件已读入内存
- 在进程之间共享内存，使一个进程中的修改反映到另一个进程中

我们可以通过 `NtCreateSection` 系统调用或 `New-NtSection` PowerShell 命令创建节对象。我们必须指定映射的大小、内存的保护属性以及可选的文件句柄；作为回报，我们会获得一个节句柄。

然而，创建节并不会自动允许我们访问内存；我们首先需要使用 `NtMapViewOfSection` 或 `Add-NtSection` 将其映射到虚拟内存地址空间中。代码清单 2-31 提供了一个示例，其中我们创建了一个匿名节并将其映射到内存中。




```
❶ PS> $s = New-NtSection -Size 4096 -Protection ReadWrite
❷ PS> $m = Add-NtSection -Section $s -Protection ReadWrite
PS> Get-NtVirtualMemory $m.BaseAddress
Address          Size Protect   Type   State  Name
-------          ---- -------   ----   -----  ----
000001C3DD0E0000 4096 ReadWrite Mapped Commit

❸ PS> Remove-NtSection -Mapping $m
PS> Get-NtVirtualMemory -Address 0x1C3DD0E0000
Address          Size Protect   Type   State  Name
-------          ---- -------   ----   -----  ----
000001C3DD0E0000 4096 NoAccess  None   Free

❹ PS> Add-NtSection -Section $s -Protection ExecuteRead
Exception calling "Map" with "9" argument(s):
  "(0xC000004E) - A view to a section specifies a protection which is
   incompatible with the initial view's protection."
```


*代码清单 2-31：创建节并将其映射到内存*

首先，我们创建一个大小为4,096字节、保护属性为 `ReadWrite` 的节对象 ❶。我们未指定 `File` 参数，这意味着它是匿名的，不依赖于任何文件。如果我们为节对象指定一个 OMNS 路径，它代表的匿名内存就可以与其他进程共享。

然后，我们使用 `Add-NtSection` 将节映射到内存中，指定我们想要的内存保护属性，并查询映射地址以验证操作成功 ❷。请注意，`Type` 设置为 `Mapped`。当我们完成映射后，调用 `Remove-NtSection` 取消映射节，然后验证它现在处于空闲状态 ❸。

最后，我们演示了不能使用与创建节对象时不同的保护属性来映射节 ❹。当我们尝试以不兼容的读取和执行权限映射节时，会看到异常。

允许用于将节对象映射到内存的保护属性取决于两个因素。第一个是创建节对象时指定的保护属性。例如，如果节是以 `ReadOnly` 保护属性创建的，则永远不能将其映射为可写。

第二个依赖因素是对正在映射的节句柄所授予的访问权限。如果要将节映射为可读，则句柄必须具有 `MapRead` 访问权限。要将其映射为可写，则需要同时具有 `MapRead` 和 `MapWrite` 访问权限。（当然，如果原始节对象未指定可写保护属性，仅具有 `MapWrite` 访问权限也不足以将节映射为可写。）

通过向 `Add-NtSection` 指定进程句柄，可以将节映射到另一个进程中。我们不需要为 `Remove-NtSection` 指定进程，因为映射对象知道它映射在哪个进程中。在内存信息输出中，`Type` 列显示为 `Mapped`。




```
PS> Get-NtVirtualMemory -Type Mapped | Where-Object Name -ne ""
Address          Size    Protect  Type   State  Name
-------          ----    -------  ----   -----  ----
000001760DB90000 815104  ReadOnly Mapped Commit locale.nls
000001760DC60000 12288   ReadOnly Mapped Commit powershell.exe.mui
000001760DEE0000 20480   ReadOnly Mapped Commit winnlsres.dll
000001760F720000 3371008 ReadOnly Mapped Commit SortDefault.nls
--snip--
```


*代码清单 2-32：列出具有名称的映射文件*

除了 `Anonymous` 和 `Mapped` 类型外，还有第三种节类型，即 `Image` 类型。当提供指向 Windows 可执行文件的文件句柄时，内核会自动解析其格式，并生成多个子节，代表可执行文件的各种组件。要从文件创建映射映像，我们只需要文件句柄上的 `Execute` 访问权限；文件本身不需要对我们可读。

Windows广泛使用映像节来简化可执行文件到内存的映射。我们可以通过在创建Section对象时传递Image标志，或使用New-NtSectionImage命令来指定映像节，如代码清单 2-33所示。

```
PS> $sect = New-NtSectionImage -Win32Path "C:\Windows\notepad.exe"
❶ PS> $map = Add-NtSection -Section $sect -Protection ReadOnly
PS> Get-NtVirtualMemory -Address $map.BaseAddress
Address          Size   Protect     Type  State  Name
-------          ----   -------     ----  -----  ----
❷ 00007FF667150000 4096   ReadOnly    Image Commit notepad.exe

❸ PS> Get-NtVirtualMemory -Type Image -Name "notepad.exe"
Address          Size   Protect     Type  State  Name
-------          ----   -------     ----  -----  ----
00007FF667150000 4096   ReadOnly    Image Commit notepad.exe
00007FF667151000 135168 ExecuteRead Image Commit notepad.exe
00007FF667172000 36864  ReadOnly    Image Commit notepad.exe
00007FF66717B000 12288  WriteCopy   Image Commit notepad.exe
00007FF66717E000 4096   ReadOnly    Image Commit notepad.exe
00007FF66717F000 4096   WriteCopy   Image Commit notepad.exe
00007FF667180000 8192   ReadOnly    Image Commit notepad.exe

❹ PS> Out-HexDump -Buffer $map -ShowAscii -Length 128
4D 5A 90 00 03 00 00 00 04 00 00 00 FF FF 00 00  - MZ..............
B8 00 00 00 00 00 00 00 40 00 00 00 00 00 00 00  - ........@.......
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  - ................
00 00 00 00 00 00 00 00 00 00 00 00 F8 00 00 00  - ................
0E 1F BA 0E 00 B4 09 CD 21 B8 01 4C CD 21 54 68  - ........!..L.!Th
69 73 20 70 72 6F 67 72 61 6D 20 63 61 6E 6E 6F  - is program canno
74 20 62 65 20 72 75 6E 20 69 6E 20 44 4F 53 20  - t be run in DOS
6D 6F 64 65 2E 0D 0D 0A 24 00 00 00 00 00 00 00  - mode....$.......
```

*代码清单 2-33：映射notepad.exe并查看加载的映像*

如您所见，在映射映像节时，我们无需指定ExecuteRead或ExecuteReadWrite保护。任何保护，包括ReadOnly，都可以使用❶。当我们获取基于映射的地址的内存信息时，发现那里没有可执行内存，且分配大小仅为4,096字节❷，这对于*notepad.exe*来说似乎太小了。这是因为该节由多个较小的映射区域组成。如果我们过滤出映射名称的内存信息❸，就能看到可执行内存。使用Out-HexDump命令，我们可以打印映射文件缓冲区的内容❹。

### 代码完整性

一项重要的安全任务是确保计算机上运行的代码与制造商预期运行的代码一致。如果恶意用户修改了操作系统文件，您可能会遇到安全问题，如私人数据泄露。

微软认为Windows上运行代码的完整性至关重要，以至于有整个子系统专门处理此问题。这个*代码完整性*子系统通过检查代码的完整性，验证并限制哪些文件可以在内核中执行，以及可选地在用户模式下执行。当内存管理器加载映像文件时，如果需要检查可执行文件是否正确签名，它可以与代码完整性子系统协商。

在默认的Windows安装中，几乎每个可执行文件都使用称为*Authenticode*的机制进行签名。此机制允许将加密签名嵌入可执行文件中，或收集在目录文件中。代码完整性子系统可以读取此签名，验证其有效性，并基于此做出信任决策。

我们可以使用Get-AuthenticodeSignature命令查询可执行文件的签名状态，如代码清单 2-34所示。



```
PS> Get-AuthenticodeSignature "$env:WinDir\system32\notepad.exe" | Format-List
SignerCertificate : [Subject]
    CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US
--snip--
Status            : Valid
StatusMessage     : Signature verified.
Path              : C:\WINDOWS\system32\notepad.exe
SignatureType     : Catalog
IsOSBinary        : True
```


*代码清单 2-34：显示内核驱动程序的Authenticode签名*

在这里，我们查询*notepad.exe*可执行文件的签名状态，并将命令的输出格式化为列表。输出以签名者的X.509证书信息开始。这里我只显示了主题名称，它清楚地表明该文件是Microsoft Windows的一部分。

输出还显示了签名状态，即*有效*，以及签名类型，即*目录*。签名类型属性表明此签名基于目录文件，而不是嵌入在文件中。我们还可以看到此文件是操作系统二进制文件，这是由签名中嵌入的信息决定的。

代码完整性子系统最常做的信任决策是检查内核驱动程序是否可以加载。每个驱动程序文件必须具有源自Microsoft颁发密钥的签名。如果签名无效或不源自Microsoft颁发的密钥，则内核可以阻止加载该驱动程序以保持系统完整性。



### 高级本地过程调用(Advanced Local Procedure Call, ALPC)

*ALPC*子系统实现本地跨进程通信。要使用ALPC，您必须首先使用NtCreateAlpcPort系统调用创建服务器ALPC端口，并在OMNS中为其指定名称。然后，客户端可以通过调用NtConnectAlpcPort系统调用使用此名称连接到服务器端口。

在基本层面上，ALPC端口允许在服务器和客户端之间安全传输离散消息。ALPC为Windows中实现的本地RPCAPI提供底层传输。

### 配置管理器

**配置管理器（Configuration Manager）**，通常更为人熟知的名称是**注册表（Registry）**，是 Windows 操作系统中负责管理系统配置信息的重要组件。

它存储着各种各样的配置数据，其重要程度跨度很大。例如：

- 系统关键配置：**I/O 管理器（I/O Manager）可用的设备驱动程序列表**；
- 普通应用配置：例如**文本编辑器窗口上一次关闭时在屏幕上的位置**。

你可以将注册表视为一个文件系统，其中*键*类似于文件夹，*值*类似于文件。你可以通过对象管理器命名空间（OMNS）访问它，但必须使用注册表特定的系统调用。注册表的根是OMNS路径*REGISTRY*。你可以使用*NtObject*驱动器在PowerShell中列出注册表，如代码清单 2-35所示。




```
PS> ls NtObject:\REGISTRY
Name    TypeName
----    --------
A       Key
MACHINE Key
USER    Key
WC      Key
```


*代码清单 2-35：枚举注册表根键*

你可以将代码清单 2-35中的NtObject:\REGISTRY替换为NtKey:\，以简化注册表的访问。

内核在初始化时预先创建了此处显示的四个键。每个键都是一个特殊的*挂载点*，你可以在其上附加注册表配置单元。*配置单元*是单个根键下的Key对象层次结构。管理员可以从文件加载新的配置单元，并将它们附加到这些预先存在的键上。

你可以直接与注册表交互，使用Get-NtKey和New-NtKey命令分别打开和创建Key对象。你也可以使用Get-NtKeyValue和Set-NtKeyValue来获取和设置键值。要删除键或值，请使用Remove-NtKey或Remove-NtKeyValue。代码清单 2-36展示了这些命令的一些实际应用。




```
PS> $key = Get-NtKey \Registry\Machine\SOFTWARE\Microsoft\.NETFramework
PS> Get-NtKeyValue -Key $key
Name                     Type   DataObject
----                     ----   ----------
Enable64Bit              Dword  1
InstallRoot              String C:\Windows\Microsoft.NET\Framework64\
UseRyuJIT                Dword  1
DbgManagedDebugger       String "C:\Windows\system32\vsjitdebugger.exe"...
DbgJITDebugLaunchSetting Dword  16
```


*代码清单 2-36：打开注册表键并查询其值*

我们使用Get-NtKey命令打开一个Key对象。然后，我们可以使用Get-NtKeyValue命令查询存储在Key对象中的值。输出中的每个条目显示值的名称、存储的数据类型以及数据的字符串表示形式。

### 实际示例

使用PowerShell，你可以轻松修改本书中的示例脚本，以实现各种不同的功能。为了鼓励动手实验，每一章末尾都会提供一组实际示例，重新利用你所学到的各种命令。

在这些示例中，我还会重点指出我使用这些工具发现安全漏洞的时刻。这将为你作为安全研究人员在微软或第三方应用程序中寻找什么提供明确的指引；同样，对于开发人员，它也将帮助你避免一些常见的陷阱。

#### 按名称查找打开的句柄

`Get-NtHandle` 命令返回的对象具有额外的属性，允许你查询对象的名称和安全描述符。这些属性默认不显示，因为查询它们开销较大；这需要打开包含句柄的进程以获取 `DupHandle` 访问权限，将句柄复制回调用PowerShell实例，最后再查询属性。

如果你不关心性能，可以使用 代码清单 2-37 中的代码来查找所有匹配特定文件名的打开文件。




```
PS> $hs = Get-NtHandle -ObjectType File | Where-Object Name -Match Windows
PS> $hs | Select-Object ProcessId, Handle, Name
ProcessId Handle Name
--------- ------ ----
     3140     64 \Device\HarddiskVolume3\Windows\System32
     3140   1628 \Device\HarddiskVolume3\Windows\System32\en-US\KernelBase.dll.mui
     3428     72 \Device\HarddiskVolume3\Windows\System3
     3428    304 \Device\HarddiskVolume3\Windows\System32\en-US\svchost.exe.mui
     3428    840 \Device\HarddiskVolume3\Windows\System32\en-US\crypt32.dll.mui
     3428   1604 \Device\HarddiskVolume3\Windows\System32\en-US\winnlsres.dll.mui
--snip--
```


*代码清单 2-37：查找匹配特定名称的文件对象句柄*

此脚本查询所有文件对象句柄，并筛选出 `Name` 属性（表示文件路径）中包含字符串 `Windows` 的句柄。一旦查询了 `Name` 属性，它就会被缓存，因此你可以通过自定义选择将其显示到控制台。

请注意，由于该脚本会从进程中复制句柄，因此它只能显示调用者能够打开的进程中的句柄。为了获得最佳结果，请以管理员用户身份运行，这样可以打开尽可能多的进程。

#### 查找共享对象

当你使用 `Get-NtHandle` 命令查询句柄列表时，你还会获得内核内存中对象的地址。当你打开同一个内核对象时，你会得到不同的句柄，但它们仍然指向相同的内核对象地址。

你可以使用对象地址来查找共享句柄的进程。这在安全方面可能很有意义，特别是当对象在两个具有不同权限的进程之间共享时。低权限进程可能能够修改对象的属性，以绕过高权限进程中的安全检查，从而获得额外的权限。

事实上，我使用这种技术发现了Windows中的安全问题 CVE-2019-0943。问题的根源是一个特权进程——Windows字体缓存——与低权限进程共享了节（Section）句柄。低权限进程可以将共享节映射为可写，并修改特权进程认为不可修改的内容。这实际上允许低权限进程修改特权进程中的任意内存，从而导致特权代码执行。

代码清单 2-38 给出了一个查找两个进程之间共享的可写节对象的示例。




```
PS> $ss = Get-NtHandle -ObjectType Section -GroupByAddress |
Where-Object ShareCount -eq 2
PS> $mask = Get-NtAccessMask -SectionAccess MapWrite
PS> $ss = $ss | Where-Object {Test-NtAccessMask $_.AccessIntersection $mask}
PS> foreach($s in $ss) {
    $count = ($s.ProcessIds | Where-Object {
        Test-NtProcess -ProcessId $_ -Access DupHandle
    }).Count
    if ($count -eq 1) {
        $s.Handles | Select ProcessId, ProcessName, Handle
    }
}
ProcessId ProcessName Handle
--------- ----------- ------
     9100 Chrome.exe    4400
     4072 audiodg.exe   2560
```


*代码清单 2-38：查找共享的节句柄*

我们首先获取句柄，并指定 `GroupByAddress` 参数。这将返回基于内核对象地址分组的列表，而不是句柄列表。你也可以使用内置的 `Group-Object` 命令对句柄进行分组；但是，`GroupByAddress` 返回的组具有额外的属性，包括 `ShareCount`，它表示对象与多少个唯一进程共享。在这里，我们筛选出仅在两个进程之间共享的句柄。

接下来，我们要查找可以映射为可写的节对象。我们首先检查所有句柄是否具有 `MapWrite` 访问权限。如前所述，节对象的保护也必须可写，我们才能将其映射为可写。奇怪的是，我们无法查询原始保护设置，但我们可以尝试以可写方式映射节，并查看是否成功。

代码清单 2-38 中显示的结果是 Chrome 与音频设备图形进程之间共享的一个节区。该共享节区用于从浏览器播放音频，这可能不是安全问题。然而，如果你在自己的系统上运行该脚本，可能会发现一些共享节区确实存在安全问题。

请注意，一旦节区对象被映射到内存中，句柄就不再需要了。因此，你可能会遗漏一些在原始句柄关闭时已被映射的共享节区。同时，你很可能会遇到误报，例如某些节区对象被有意设置为所有人可写。这里的目标是找出 Windows 上潜在的受攻击面。然后，你必须检查这些句柄，以确定共享它们是否引入了安全问题。

#### 修改已映射的节区

如果你发现了一个有趣的节区对象需要修改，可以使用 `Add-NtSection` 将其映射到内存中。但如何修改映射的内存呢？从命令行来看，最简单的方法是使用 `Write-NtVirtualMemory` 命令，它支持传入一个已映射的节区和一个要写入的字节数组。代码清单 2-39 演示了这一技术，假设你有一个感兴趣的句柄存储在 `$handle` 变量中。




```
PS> $sect = $handle.GetObject()
PS> $map = Add-NtSection -Section $sect -Protection ReadWrite
PS> $random = Get-RandomByte -Size $map.Length
PS> Write-NtVirtualMemory -Mapping $map -Data $random
4096

PS> Out-HexDump -Buffer $map -Length 16 -ShowAddress -ShowHeader
                  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
-----------------------------------------------------------------
000001811C860000: DF 24 04 E1 AB 2A E1 76 EB 19 00 8D 79 28 9C BA
```


*代码清单 2-39：映射并修改节区对象*

我们首先对句柄调用 `GetObject` 方法，将其复制到当前进程中并返回一个节区对象。要使此操作成功，运行此命令的进程必须能够访问持有该句柄的进程。然后，我们将该句柄以 `ReadWrite` 方式映射到当前进程的内存中。

现在，我们可以创建一个大小不超过映射节区大小的随机字节数组，并使用 `Write-NtVirtualMemory` 将其写入内存区域。这是对共享内存进行快速而粗糙的模糊测试。我们的希望是，通过修改内存，特权进程会错误处理该内存区域的内容。如果特权进程崩溃，我们应该进行调查，以确定是否可以通过更有针对性的共享内存修改来控制崩溃。

我们可以使用 `Out-HexDump` 显示内存。与内置的 `Format-Hex` 相比，该命令的一个有用特性是，它会基于映射文件打印内存中的地址，而 `Format-Hex` 只是打印从 0 开始的偏移量。

你还可以使用 `Show-NtSection` 命令创建 GUI 十六进制编辑器，指定要编辑的节区对象。由于节区可以映射到任何进程中，在 GUI 十六进制编辑器中写入内容也会修改该节区的所有其他映射。以下是显示十六进制编辑器的命令：


```
PS> Show-NtSection -Section $sect
```


图 2-6 显示了运行上述命令后生成的编辑器示例。

![img](./image/01.%20PART%20I%20AN%20OVERVIEW%20OF%20THE%20WINDOWS%20OPERATING%20SYSTEM/Figure2-6.webp)

图 2-6：节区编辑器 GUI

图 2-6 中显示的 GUI 将节区映射到内存中，然后以十六进制编辑器形式显示。如果节区是可写的，你可以通过编辑器修改内存内容。

#### 查找可写且可执行的内存

在 Windows 中，进程要执行指令，内存必须标记为可执行。然而，也可以将内存同时映射为可写和可执行。攻击者有时会利用这种组合，将 shell 代码注入进程，并使用宿主进程的身份运行恶意代码。

代码清单 2-40 展示了如何检查进程中既可写又可执行的内存。找到此类内存可能表明存在恶意活动，尽管在大多数情况下，这类内存是良性的。例如，.NET 运行时会创建可写且可执行的内存，以执行 .NET 字节码的即时（JIT）编译，将其转换为本机指令。




```
PS> $proc = Get-NtProcess -ProcessId $pid -Access QueryLimitedInformation
PS> Get-NtVirtualMemory -Process $proc | Where-Object {
    $_.Protect -band "ExecuteReadWrite"
}
Address          Size  Protect          Type    State  Name
-------          ----  -------          ----    -----  ----
0000018176450000 4096  ExecuteReadWrite Private Commit
0000018176490000 8192  ExecuteReadWrite Private Commit
0000018176F60000 61440 ExecuteReadWrite Private Commit
--snip--

PS> $proc.Close()
```


*代码清单 2-40：查找进程中可执行且可写的内存*

我们首先以 `QueryLimitedInformation` 访问权限打开一个进程，这是我们枚举虚拟内存区域所需的全部权限。这里，我们打开的是当前的 PowerShell 进程；由于 PowerShell 是基于 .NET 的，我们知道它会有一些可写且可执行的内存区域，但你打开的进程可以是任何你想检查的进程。

然后，我们使用 `Get-NtVirtualMemory` 枚举所有内存区域，并筛选出 `ExecuteReadWrite` 保护类型。由于保护标志可能附加其他位，如 `Guard`（这会创建防护页，导致无法直接进行相等性检查），因此我们需要使用按位与（AND）操作来进行筛选。

### 总结

本章带领您浏览了Windows内核及其内部机制。内核由许多独立的子系统组成，如SRM、对象管理器、配置管理器（或注册表）、I/O管理器以及进程和线程管理器。

您了解了对象管理器如何管理内核资源和类型，如何通过系统调用访问内核资源，以及句柄如何以特定的访问权限进行分配。您还通过*NtObject*驱动器提供程序以及单独的命令访问了对象管理器资源。

随后，我讨论了进程和线程创建的基础知识，并演示了如何使用如`Get-NtProcess`等命令查询系统上的进程信息。我解释了如何检查进程的虚拟内存，以及一些单独的内存类型。

用户并不直接与内核交互；相反，用户模式应用程序驱动了用户体验。在下一章中，我们将更详细地讨论用户模式组件。

## 3. 用户模式应用程序

在上一章中，我们讨论了Windows内核。但用户通常不直接与内核交互，而是与面向用户的应用程序（如文字处理器和文件管理器）交互。本章将详细介绍这些用户模式应用程序是如何创建的，以及它们如何与内核接口，为用户提供服务。

我们将从讨论Win32应用程序编程接口（API）开始，然后探讨这些API如何与底层内核系统调用接口交互。接着，我们会研究文件路径必须经过的转换过程，以便与内核兼容。之后，我们将介绍Win32应用程序如何访问注册表；然后考虑Win32如何处理进程和线程的创建，并审视一些重要的系统进程。

我们首先讨论Win32应用程序编程接口（API），然后探讨这些API如何与底层内核系统调用接口交互。接着，我们会研究文件路径必须经过的转换过程，以便与内核兼容。之后，我们将介绍Win32应用程序如何访问注册表；然后考虑Win32如何处理进程和线程的创建，并审视一些重要的系统进程。

为了理解用户模式应用程序的功能，了解所提供的API如何与底层内核系统调用接口交互至关重要。我们还将研究文件路径必须经历的转换过程，以使其与内核兼容。接下来，我们将介绍Win32应用程序如何访问注册表；然后考虑Win32如何处理进程和线程的创建，并审视一些重要的系统进程。

### Win32 与用户模式 Windows API

Windows 上运行的大部分代码并不直接与系统调用交互。这是 *Windows NT* 操作系统最初设计的一个产物。微软最初将 Windows NT 开发为 IBM 的 OS/2 操作系统的更新版本，并计划使其包含多个实现不同 API 的子系统。在不同时期，它支持 POSIX、OS/2 和 Win32 API。

最终，微软与 IBM 的关系破裂，微软将其为 Windows 95 开发的 API 集 *Win32* 用于构建一个子系统来实现它。在 Windows 2000 中，不受欢迎的 OS/2 子系统被移除，而 POSIX 一直存活到 Windows 8.1。到 Windows 10 时，Win32 成为唯一保留的子系统（尽管微软随后实现了 Linux 兼容层，如适用于 Linux 的 Windows 子系统，但这些不使用旧的子系统扩展点）。

为了支持这些多种 API，Windows 内核实现了一组通用的系统调用。每个子系统特定的库和服务负责将其 API 转换为底层系统调用接口。图 3-1 展示了 Win32 子系统 API 库的概览。

![img](./image/01.%20PART%20I%20AN%20OVERVIEW%20OF%20THE%20WINDOWS%20OPERATING%20SYSTEM/Figure3-1.webp)

图 3-1：Win32 API 模块

如您所见，Win32 API 的核心在 *KERNEL32* 和 *KERNELBASE* 库中实现。这些库调用系统提供的 *NT 层动态链接库（NTDLL）* 中的方法，该库实现了系统调用分发以及执行常见底层操作的运行时库 API。

大多数用户模式应用程序并不直接包含 Windows 系统 API 的实现。相反，*NTDLL* 包含 DLL 加载器，它按需加载新库。加载过程对开发者来说大多是不透明的：在构建程序时，您会链接一组库，编译器和工具链会自动向可执行文件添加导入表以反映依赖关系。然后 DLL 加载器检查导入表，自动加载任何依赖库，并解析导入。您还可以从应用程序中指定导出函数，以便其他代码可以依赖您的 API。

#### 加载新库

可以在运行时手动访问导出的函数，而无需导入表条目。您可以使用 Win32 API `LoadLibrary` 加载新库，该 API 通过 PowerShell 的 `Import-Win32Module` 命令暴露。要查找 DLL 导出的函数的内存地址，请使用 Win32 API `GetProcAddress`，该 API 通过 PowerShell 的 `Get-Win32ModuleExport` 命令暴露（代码清单 3-1）。

```
❶ PS> $lib = Import-Win32Module -Path "kernel32.dll"
❷ PS> $lib
Name         ImageBase        EntryPoint
----         ---------        ----------
KERNEL32.DLL 00007FFA088A0000 00007FFA088B7C70

❸ PS> Get-Win32ModuleExport -Module $lib
Ordinal Name                    Address
------- ----                    -------
1       AcquireSRWLockExclusive NTDLL.RtlAcquireSRWLockExclusive
2       AcquireSRWLockShared    NTDLL.RtlAcquireSRWLockShared
3       ActivateActCtx          0x7FFA088BE640
4       ActivateActCtxWorker    0x7FFA088BA950
--snip--

❹ PS> "{0:X}" -f (Get-Win32ModuleExport -Module $lib 
-ProcAddress "AllocConsole")
7FFA088C27C0
```

*代码清单 3-1：* KERNEL32 *库的导出*

在这里，我们使用 PowerShell 加载 *KERNEL32* 库并枚举导出的和导入的 API。首先，我们使用 `Import-Win32Module` 将其加载到内存中 ❶。*KERNEL32* 库始终被加载，因此此命令只会返回已加载的地址；但对于其他库，加载将导致 DLL 被映射到内存并初始化。

警告

*`Import-Win32Module` 命令会将 DLL 加载到内存中并可能执行代码。在此示例中，这是可以接受的，因为* KERNEL32 *是受信任的系统库之一。但是，请勿对不受信任的 DLL 使用此命令，尤其是在分析恶意软件时，因为它可能导致恶意代码执行。为安全起见，请始终在恶意软件分析时使用隔离环境。*

接下来，我们转储 DLL 中的所有导出函数 ❸。在此情况下，我们为每个函数看到三条信息：序号（Ordinal）、名称（Name）和地址（Address）。序号是一个小数字，唯一标识 DLL 中导出的函数。可以按序号导入 API，这意味着无需导出名称；每当微软不希望将某个函数作为公共 API 正式支持时，您会看到 DLL 的导出表中缺少某些名称。

名称只是导出函数的名称。它不需要与原始源代码中函数的名称一致，尽管通常是一致的。最后，Address 是函数第一条指令在内存中的地址。你会注意到前两个导出项显示的是字符串而不是地址。这是*导出转发*的情况；它允许 DLL 按名称导出函数，并让加载器自动将其重定向到另一个 DLL。在这种情况下，AcquireSRWLockExclusive 在 *NTDLL* 中实现为 RtlAcquireSRWLockExclusive。我们也可以使用 Get-Win32ModuleExport 通过 GetProcAddress API ❹ 查找单个导出函数。

#### 查看导入的 API

类似地，我们可以使用 Get-Win32ModuleImport 命令查看可执行文件从其他 DLL 导入的 API，如 代码清单 3-2 所示。




```
PS> Get-Win32ModuleImport -Path "kernel32.dll"
DllName                                   FunctionCount DelayLoaded
-------                                   ------------- -----------
api-ms-win-core-rtlsupport-l1-1-0.dll     13            False
ntdll.dll                                 378           False
KERNELBASE.dll                            90            False
api-ms-win-core-processthreads-l1-1-0.dll 39            False
--snip--

PS> Get-Win32ModuleImport -Path "kernel32.dll" -DllName "ntdll.dll" |
Where-Object Name -Match "^Nt"
Name                          Address
----                          -------
NtEnumerateKey                7FFA090BC6F0
NtTerminateProcess            7FFA090BC630
NtMapUserPhysicalPagesScatter 7FFA090BC110
NtMapViewOfSection            7FFA090BC5B0
--snip--
```


*代码清单 3-2：枚举 KERNEL32 库的导入项*

我们首先调用 Get-Win32ModuleImport，指定 *KERNEL32* DLL 作为路径。当指定路径时，该命令会为你调用 Import-Win32Module 并显示所有导入项，包括要加载的 DLL 名称和导入的函数数量。最后一列指示该 DLL 是否被开发者标记为*延迟加载*。这是一种性能优化；它允许 DLL 仅在其某个导出函数被使用时才加载。这种延迟避免了在初始化期间将所有 DLL 加载到内存中，从而减少了进程启动时间，并且如果导入从未被使用，还能降低运行时内存占用。

接下来，我们转储某个 DLL 的导入函数。由于可执行文件可以从多个库导入代码，我们使用 DllName 属性指定所需的库。然后我们筛选出所有以 Nt 前缀开头的导入函数；这样我们就能确切地看到 *KERNEL32* 从 *NTDLL* 导入了哪些系统调用。

API 集

你可能会注意到 代码清单 3-2 中导入 DLL 名称列表里有些奇怪的地方。如果你在文件系统中搜索 api-ms-win-core-rtlsupport-l1-1-0.dll 文件，你找不到它。这是因为该 DLL 名称指的是一个 API 集。API 集在 Windows 7 中引入，用于模块化系统库，它们将集合名称抽象为导出该 API 的 DLL。

API 集允许可执行文件在多个不同版本的 Windows 上运行，例如客户端、服务器或嵌入式版本，并根据可用的库在运行时改变其功能。当 DLL 加载器遇到这些 API 集名称之一时，它会查阅一个加载到每个进程中的表，该表来源于 apisetschema.dll 文件，将名称映射到真实的 DLL。你可以使用 Get-NtApiSet 命令并指定 API 集的名称来查询 API 集的详细信息：


```
PS> Get-NtApiSet api-ms-win-core-rtlsupport-l1-1-0.dll
Name                               HostModule   Flags
----                               ------------ -----
api-ms-win-core-rtlsupport-l1-1-1  ntdll.dll    Sealed
```


我们可以看到在这种情况下，API 集解析为 NTDLL 库。你也可以为 Get-Win32ModuleImport 命令指定 ResolveApiSet 参数，以根据真实的 DLL 对导入项进行分组：


```
PS> Get-Win32ModuleImport -Path "kernel32.dll"  -ResolveApiSet
DllName                           FunctionCount   DelayLoaded
--------                          --------------- -------------
ntdll.dll                         392             False
KERNELBASE.dll                    867             False
ext-ms-win-oobe-query-l1-1-0.dll  1               True
RPCRT4.dll                        10              True
```


如果你将 代码清单 3-2 中的输出与此处相同命令的输出进行比较，你会注意到解析后的导入列表要短得多，并且核心库获得了额外的函数导入。还要注意未解析的 API 集名称，例如 api-ms-win-core-rtlsupport-l1-1-0，它被标记为“未解析”。这是因为该 API 集没有对应的 DLL 文件，而是由 NTDLL 直接实现。

#### 搜索 DLL

假设你将字符串 ABC.DLL 传递给 LoadLibrary API。该 API 如何知道在哪里找到该 DLL？如果文件没有指定为绝对路径，API 会实现路径搜索算法。该算法最初在 Windows NT 3.1 中实现，按以下顺序搜索文件：

  1.  当前进程可执行文件所在的目录

  2.  当前工作目录

  3.  Windows *System32* 目录

  4.  *Windows* 目录

  5.  PATH 环境变量中每个以分号分隔的位置

这种加载顺序的问题在于，它可能导致特权进程从不安全的位置加载DLL。例如，如果特权进程使用`SetCurrentDirectory` API将其当前工作目录更改为低权限用户可写的位置，那么DLL将从该位置加载，而不是从*System32*目录加载。这种攻击被称为*DLL劫持*，是Windows上一个长期存在的问题。

Vista将默认加载顺序更改为以下顺序，这更安全：

  1.  当前进程可执行文件所在的目录

  2.  Windows *System32*目录

  3.  *Windows*目录

  4.  当前工作目录

  5.  PATH环境变量中每个以分号分隔的位置

现在，我们不再在*System32*或*Windows*目录之前从当前工作目录加载。然而，如果攻击者能够写入可执行文件的目录，DLL劫持仍可能发生。因此，如果可执行文件以特权进程运行，只有管理员应能修改其目录，以防止DLL劫持的发生。

.DLL文件扩展名

另一个加载怪癖涉及DLL文件名中文件扩展名的处理。如果未指定扩展名，DLL加载器将自动添加.DLL扩展名。如果指定了任何扩展名，文件名将按原样处理。最后，如果扩展名仅由一个句点组成（例如，LIB.），加载器将移除句点并尝试加载不带扩展名的文件（此处为LIB）。

这种文件扩展名行为可能导致应用程序尝试加载的DLL与实际加载的DLL之间出现不匹配。例如，应用程序可能检查文件LIB是否有效（即，正确加密签名）；然而，DLL加载器随后会加载未检查的LIB.DLL。如果您能诱骗特权应用程序将错误的DLL加载到内存中，这可能导致安全漏洞，因为入口点将在特权上下文中执行。

虽然DLL加载器通常会转向磁盘检索库，但某些库使用频率极高，因此预先初始化它们是有意义的。这可以提高性能并防止DLL被劫持。两个明显的例子是*KERNEL32*和*NTDLL*。

在Windows上任何用户应用程序启动之前，系统会配置一个*KnownDlls* OMNS目录，其中包含预加载映像节的列表。*KnownDlls*节对象的名称只是库的文件名。DLL加载器可以在访问磁盘之前先检查*KnownDlls*。这提高了性能，因为加载器无需访问磁盘。

```
PS> ls NtObject:\KnownDlls
Name                TypeName
----                --------
kernel32.dll        Section
kernel.appcore.dll  Section
windows.storage.dll Section
ucrtbase.dll        Section
MSCTF.dll           Section
--snip--
```


*代码清单 3-3：列出*KnownDlls*对象目录的内容*

本节涵盖了Win32子系统的基础知识，以及它如何使用库来实现用户模式应用程序与操作系统交互的API。我们稍后将回到Win32 API，但首先必须讨论Windows用户界面，它与Win32子系统的功能密不可分。

### Win32 GUI

“Windows”这一名称指的是操作系统图形用户界面（GUI）的结构。该GUI由一个或多个窗口组成，用户可以通过按钮和文本输入等控件与之交互。自Windows 1.0起，GUI一直是操作系统最重要的特性，因此其模型复杂也就不足为奇了。GUI的实现分为内核模式和用户模式两部分，如图3-2所示。

![img](./image/01.%20PART%20I%20AN%20OVERVIEW%20OF%20THE%20WINDOWS%20OPERATING%20SYSTEM/Figure3-2.webp)

图3-2：Win32 GUI模块

您可能会注意到，图3-2的左侧看起来很像图3-1，后者展示了常规Win32 API的模块。然而，这里不是*NTDLL*，而是*WIN32U*，它实现了供内核调用的系统调用存根。两个库调用*WIN32U*：*USER32*和*GDI32*。*USER32*实现窗口UI元素并通常管理GUI，而*GDI32*实现绘图原语，如字体和形状。

图3-2与图3-1之间的一大区别在于，GUI实际上并非在主NTOS内核执行体内部实现。相反，其系统调用在*WIN32K*驱动程序中实现，该驱动程序与对象管理器、内核和显示驱动程序交互，以处理用户交互并显示结果。*WIN32K*驱动程序还实现了一个与内核系统调用表分离的系统调用表。

> 注意
>
> *在Windows 10之前的版本中，*WIN32U*中的系统调用分发代码直接嵌入在用户模式DLL内部。这使得应用程序难以在不编写汇编语言的情况下直接调用*WIN32K*系统调用。*

GUI API还与一个特殊的特权进程交互：*客户端服务器运行时子系统（CSRSS）*。该进程负责为低特权客户端处理某些特权操作，例如配置每用户驱动器映射、进程管理和错误处理。

#### GUI内核资源

GUI由四种类型的内核资源组成：

- **窗口站**    表示与屏幕和用户界面（如键盘和鼠标）连接的对象
- **窗口**    用于与用户交互、接受输入并显示结果的GUI元素

- **桌面**    表示可见桌面并充当窗口宿主对象的对象
- **绘图资源**    位图、字体或任何其他需要显示给用户的内容

虽然Win32内核和用户组件处理窗口，但窗口站和桌面可通过对象管理器访问。窗口站和桌面有对应的内核对象类型，如代码清单 3-4所示。

```
PS> Get-NtType WindowStation,Desktop
Name
----
WindowStation
Desktop
```

*代码清单 3-4：窗口站和桌面对象类型*

窗口站对象在进程启动时分配，或通过*NtUserSetProcessWindowStation* API分配。桌面对象在每线程基础上分配，通过*NtUserSetThreadDesktop* API分配。我们可以使用代码清单 3-5中的命令查询窗口站和桌面的名称。

```
❶ PS> Get-NtWindowStationName
WinSta0
Service-0x0-b17580b$

❷ PS> Get-NtWindowStationName -Current
WinSta0

❸ PS> Get-NtDesktopName
Default
WinLogon

❹ PS> Get-NtDesktopName -Current
Default
```

*代码清单 3-5：显示所有当前窗口站和桌面*

我们首先查询所有可用窗口站的名称❶。在此示例中，有两个：默认的WinSta0窗口站和Service-0x0-b17580b$，后者由另一个进程创建。创建独立窗口站的能力允许进程将其GUI交互与同时运行的其他进程隔离。然而，WinSta0是特殊的，因为它是唯一连接到用户控制台的对象。

接下来，我们使用Current参数检查当前窗口站名称❷。可以看到我们位于WinSta0上。

然后，我们查询当前窗口站上的桌面名称❸。我们只看到两个桌面：`Default` 和 `WinLogon`。`WinLogon` 桌面仅在以管理员身份运行 `Get-NtDesktopName` 命令时可见，因为它仅用于显示登录屏幕，普通用户应用程序不应能访问它。桌面对象必须相对于窗口站路径打开；没有专门用于桌面的对象目录。因此，桌面的名称反映了窗口站对象的名称。

最后，我们检查当前线程的桌面名称❹。我们附加到的桌面显示为 `Default`，因为这是普通用户应用程序唯一可用的桌面。我们可以使用 `Get-NtDesktop` 和 `Get-NtWindow` 枚举桌面中创建的窗口（代码清单 3-6）。




```
PS> $desktop = Get-NtDesktop -Current
PS> Get-NtWindow -Desktop $desktop
Handle ProcessId ThreadId ClassName
------ --------- -------- ---------
66104  11864     12848    GDI+ Hook Window Class
65922  23860     18536    ForegroundStaging
65864  23860     24400    ForegroundStaging
65740  23860     20836    tooltips_class32
--snip--
```


*代码清单 3-6：枚举当前桌面的窗口*

如您所见，每个窗口都有一些属性。首先是它的 *句柄*，该句柄在桌面内是唯一的。这不同于我们在前一章讨论的内核对象句柄；相反，它是由 Win32 子系统分配的值。

为了正常运行，窗口会接收来自系统的 *消息*。例如，当您在窗口上单击鼠标按钮时，系统会发送一条消息，通知窗口该点击事件以及按下了哪个鼠标按钮。窗口随后可以处理该消息并相应地更改其行为。您还可以使用 `SendMessage` 和 `PostMessage` API 手动向窗口发送消息。

每条消息由一个数字标识符（例如 `0x10`，代表关闭窗口的 `WM_CLOSE` 消息）和两个附加参数组成。这两个参数的含义取决于消息类型。例如，如果消息是 `WM_CLOSE`，则两个参数均不使用；对于其他消息，它们可能表示指向字符串的指针或整数值。

消息可以发送或发布。发送和发布消息之间的区别在于，发送会等待窗口处理消息并返回一个值，而发布只是将消息发送到窗口并立即返回。

在代码清单 3-6中，`ProcessId` 和 `ThreadId` 列标识了使用 `CreateWindowEx` 等 API 创建窗口的进程和线程。窗口具有所谓的 *线程亲和性*，这意味着只有创建线程才能操作窗口的状态并处理其消息。但是，任何线程都可以向窗口发送消息。为了处理消息，创建线程必须运行 *消息循环*，该循环调用 `GetMessage` API 接收下一条可用消息，然后使用 `DispatchMessage` API 将其分派到窗口的消息处理回调函数。当应用程序未运行消息循环时，您可能会看到 Windows 应用程序挂起，因为没有循环，GUI 无法更新。

代码清单 3-6中的最后一列是 `ClassName`。这是 *窗口类* 的名称，它充当新窗口的模板。当调用 `CreateWindowEx` 时，会指定 `ClassName`，窗口将使用模板中的默认值（例如边框样式或默认大小）进行初始化。应用程序通常注册自己的类来处理独特的窗口。或者，它可以使用系统定义的类来处理按钮和其他常见控件。

#### 窗口消息

让我们看一个简单的示例，在代码清单 3-7中，我们发送一条窗口消息来查找桌面上所有窗口的标题文本。


```
❶ PS> $ws = Get-NtWindow
❷ PS> $char_count = 2048
PS> $buf = New-Win32MemoryBuffer -Length ($char_count*2)

❸ PS> foreach($w in $ws) {
    $len = Send-NtWindowMessage -Window $w -Message 0xD -LParam $buf.DangerousGetHandle() -WParam $char_count -Wait
    $txt = $buf.ReadUnicodeString($len.ToInt32())
    if ($txt.Length -eq 0) {
        continue
    }
    "PID: $($w.ProcessId) - $txt"
}
PID: 10064 - System tray overflow window.
PID: 16168 - HardwareMonitorWindow
PID: 10064 - Battery Meter
--snip--
```


*代码清单 3-7：向桌面上的所有窗口发送 `WM_GETTEXT` 消息*

首先，我们使用 `Get-NtWindow` 命令枚举当前桌面上的所有窗口❶。接下来，我们分配一个内存缓冲区来存储 2,048 个字符❷。请记住，我们将使用此缓冲区存储 16 位 Unicode 字符，因此字符数必须乘以 2 才能确定缓冲区的大小（以字节为单位）。

在循环❸中，我们向每个窗口发送`WM_GETTEXT`消息（消息编号为0xD），以查询窗口的标题。我们需要指定两个参数：`LParam`，指向我们分配的缓冲区；`WParam`，缓冲区中Unicode字符的最大数量。这两个参数传递的值会因消息类型的不同而有所差异。我们等待消息发送的结果，该结果指示复制到缓冲区中的字符数。然后，我们可以读取标题字符串并输出到控制台，忽略任何标题为空的窗口。

窗口系统中还有更多值得探索的内容，但这些细节超出了本书的范围。如果你想了解更多关于Win32应用程序开发的知识，我推荐Charles Petzold的经典著作《Programming Windows》第5版（Microsoft Press，1998）。接下来，我们将探讨多个用户如何通过控制台会话在同一系统上使用各自的用户界面。

#### 控制台会话

Windows NT的第一个版本允许多个用户同时进行身份验证并各自运行进程。然而，在引入*远程桌面服务（RDS）*之前，不同的交互式桌面无法在同一台机器上并发运行多个用户账户。所有经过身份验证的用户需要共享一个物理控制台。Windows NT 4引入了多控制台支持，作为可选的服务器专用功能，直到Windows XP中才成为标准功能。

RDS是Windows工作站和服务器上的一项服务，允许你远程连接到图形用户界面并与系统交互。它用于远程管理，并为同一网络连接系统上的多个用户提供共享托管。此外，其功能已被重新利用，以支持在同一系统上切换用户而无需注销用户的机制。

为准备新用户登录Windows，会话管理器服务会在控制台上创建一个新会话。该会话用于组织用户的窗口站和桌面对象，使它们与同时进行身份验证的其他用户的对象分离。内核创建一个会话对象来跟踪资源，并在*KernelObjects* OMNS目录中存储对该对象的命名引用。然而，会话对象通常仅以整数形式暴露给用户。该整数没有随机性；它只是随着每个新控制台会话的创建而递增。

会话管理器在任何用户登录之前，会在新会话中启动多个进程。这些进程包括专用的CSRSS副本和Winlogon进程，它们显示*凭据*用户界面并处理新用户的身份验证。我们将在第12章中更深入地探讨身份验证过程。

控制台会话在技术上是在访问令牌中指定的，但这是第4章的主题。我们可以通过运行一些PowerShell命令来观察每个会话中运行的进程，如代码清单 3-8所示。



```
PS> Get-NtProcess -InfoOnly | Group-Object SessionId
Count Name        Group
----- ----        -----
  156 0           {, System, Secure System, Registry...}
    1 1           {csrss.exe}
    1 2           {csrss.exe}
  113 3           {csrss.exe, winlogon.exe, fontdrvhost.exe, dwm.exe...}
```


*代码清单 3-8：使用Get-NtProcess显示每个控制台会话中的进程*

Windows只有一个物理控制台，它连接到键盘、鼠标和显示器。然而，可以通过使用*远程桌面协议（RDP）*通信的客户端，通过网络创建新的远程桌面。

还可以切换登录到物理控制台的用户；这支持Windows中的*快速用户切换*功能。当物理控制台切换到新用户时，之前的用户仍然保持登录状态并在后台运行，但你无法与该用户的桌面交互。

每个控制台会话都有自己特殊的内核内存区域。拥有重复的资源确保控制台会话相互隔离；这充当了安全边界。会话编号0是特殊的，因为它仅用于特权服务和管理。在此会话中运行的进程通常无法使用图形用户界面（GUI）。

##### Shatter 攻击

在Windows Vista之前，服务和物理控制台都运行在会话0中。由于任何进程都能向同一会话中的其他进程发送窗口消息，这引入了一种被称为“Shatter 攻击”的安全缺陷。Shatter 攻击发生在普通用户能够向同一会话中权限更高的应用程序发送窗口消息以提升权限时。例如，`WM_TIMER`消息可以接受一个任意的函数指针，权限更高的应用程序在收到该消息时会调用这个指针。普通用户可以发送带有精心选择的函数指针的消息，从而在特权应用程序的上下文中执行任意代码。

Windows Vista通过两个相关的安全功能缓解了 Shatter 攻击，这些功能在最新版本的Windows中仍然存在。第一个是会话0隔离，它将物理控制台移出会话0，使得普通用户应用程序无法向服务发送消息。第二个是用户界面特权隔离（UIPI），它阻止低特权进程与高特权窗口交互。因此，即使服务在用户的桌面上创建了窗口，系统也会拒绝用户向特权服务发送的任何消息。

与控制台会话相关的另一个重要功能是命名对象的分离。在上一章中，我们讨论了`*BaseNamedObjects*`目录，它是命名对象的全局位置，为多个用户提供共享资源的手段。然而，如果多个用户可以同时登录系统，很容易出现名称冲突。Windows通过在每个控制台会话的`*\Sessions\<N>\BaseNamedObjects*`目录下创建BNO目录来解决这个问题，其中`*<N>*`是控制台会话ID。`*\Sessions*`目录还包含一个用于窗口站的目录，位于`*\Sessions\<N>\Windows*`下，这确保了窗口资源也被分离。你可以使用`*NtObjectSession*`驱动器列出当前控制台会话的BNO目录，如代码清单 3-9所示。



```
PS> ls NtObjectSession:\ | Group-Object TypeName
Count Name                Group
----- ----                -----
  246 Semaphore           {SM0:10876:304:WilStaging_02_p0h...}
  263 Mutant              {SM0:18960:120:WilError_02,...}
  164 Section             {fd8HWNDInterface:3092e,...}
  159 Event               {BrushTransitionsCom...}
    4 SymbolicLink        {AppContainerNamedObjects, Local, Session, Global}
    1 ALPC Port           {SIPC_{2819B8FF-EB1C-4652-80F0-7AB4EFA88BE4}}
    2 Job                 {WinlogonAccess, ProcessJobTracker1980}
    1 Directory           {Restricted}
```


*代码清单 3-9：会话的BNO目录内容*

会话0没有按控制台会话划分的BNO；它使用全局BNO目录。

远程桌面服务的起源

RDS功能并非源自微软。相反，一家名为Citrix的公司为Windows开发了这项技术，并将其授权给微软用于NT 4。这项技术最初被称为终端服务，因此有时会看到它使用该名称。至今，仍可以购买Citrix版本的RDS，它使用不同的网络协议——独立计算架构（ICA），而不是微软的RDP。

### 比较Win32 API与系统调用

并非所有系统调用都直接通过Win32暴露，在某些情况下，Win32 API会减少所暴露系统调用的功能。在本节中，我们将探讨系统调用与其Win32 API对应版本之间的一些常见差异。

作为案例研究，我们将考虑`CreateMutexEx` API，即我们在前一章中看到的`NtCreateMutant`系统调用的Win32版本。该API的C原型如代码清单 3-10所示。




```
HANDLE CreateMutexEx(
    SECURITY_ATTRIBUTES* lpMutexAttributes,
    const WCHAR*         lpName,
    DWORD                dwFlags,
    DWORD                dwDesiredAccess
);
```


*代码清单 3-10：CreateMutexEx Win32 API的原型*

将其与`NtCreateMutant`原型进行比较，如代码清单 3-11所示。




```
NTSTATUS NtCreateMutant(
    HANDLE*              MutantHandle,
    ACCESS_MASK          DesiredAccess,
    OBJECT_ATTRIBUTES*   ObjectAttributes,
    BOOLEAN              InitialOwner
);
```


*代码清单 3-11：NtCreateMutant系统调用的原型*

原型之间的第一个区别是，Win32 API返回内核对象的句柄，而系统调用返回NTSTATUS代码（并通过第一个参数以指针方式接收句柄）。

您可能会想：如果不是通过NTSTATUS代码，错误是如何传播回API调用者的？在这方面，Win32 API并不总是一致的。如果API返回句柄，通常返回值为NULL。然而，某些API（如文件API）返回-1。如果不返回句柄，通常返回布尔值，TRUE表示成功，FALSE表示错误。

但如果我们想知道API失败*的原因*呢？为此，API定义了一组错误代码。与NTSTATUS代码不同，这些错误代码没有结构；它们只是数字。当Windows API失败时，您可以通过调用`GetLastError` API来查询此错误代码。

*NTDLL*提供了一个`RtlNtStatusToDosError` API，用于将NTSTATUS代码转换为预定义的Win32错误代码。`CreateMutexEx` API在失败时可以将NTSTATUS代码转换为Win32错误代码，然后使用`SetLastError` API将其写入当前线程的最后错误位置。

我们可以使用PowerShell中的`Get-Win32Error`查找错误代码，如代码清单 3-12所示。




```
PS> Get-Win32Error 5
ErrorCode Name                Message
--------- ----                -------
        5 ERROR_ACCESS_DENIED Access is denied.
```


*代码清单 3-12：查找Win32错误代码5*

系统调用与Win32 API之间的第二个重大区别是，API不接受`OBJECT_ATTRIBUTES`结构。相反，它将属性拆分到两个参数中：`lpName`用于指定对象的名称，`lpMutexAttributes`是指向`SECURITY_ATTRIBUTES`结构的指针。

`lpName`参数是一个以NUL结尾的字符串，由16位Unicode字符组成。尽管对象管理器使用计数的`UNICODE_STRING`，Win32 API使用C风格的终止字符串。这意味着虽然NUL字符是对象名称的有效字符，但无法通过Win32 API指定。

另一个区别是，名称不是对象在OMNS位置的完整路径；相反，它是相对于当前会话的BNO目录的。这意味着如果名称是*ABC*，则最终使用的路径是*\Sessions\<N>\BaseNamedObjects\ABC*，其中*<N>*是控制台会话ID。如果要在全局BNO目录中创建对象，可以在名称前加上*Global*前缀（例如，*Global\ABC*）。这是因为*Global*是指向*\BaseNamedObjects*的符号链接，该链接与每个会话的BNO目录一起自动创建。如果要在PowerShell中使用`Get`和`New`命令模拟此行为，请传递`-Win32Path`选项，如代码清单 3-13所示。




```
PS> $m = New-NtMutant ABC -Win32Path
PS> $m.FullPath
\Sessions\2\BaseNamedObjects\ABC
```


*代码清单 3-13：使用-Win32Path创建新的Mutant*

代码清单 3-14显示了`SECURITY_ATTRIBUTES`结构。




```
struct SECURITY_ATTRIBUTES {
    DWORD  nLength;
    VOID*  lpSecurityDescriptor;
    BOOL   bInheritHandle;
};
```


*代码清单 3-14：SECURITY_ATTRIBUTES结构*

这允许您指定新对象的安全描述符，以及句柄是否可继承。`CreateMutexEx` Win32 API没有暴露`OBJECT_ATTRIBUTES`中的其他选项。

这引出了代码清单 3-10中的最后两个参数：`dwDesiredAccess`直接映射到`DesiredAccess`，而本地的`InitialOwner`参数通过`dwFlags`和`CREATE_MUTEX_INITIAL_OWNER`标志指定。

你可能会遇到的一个意外情况是，当你尝试在 *KERNEL32* DLL 的导出表中查找 CreateMutexEx API 的地址时（代码清单 3-15）。




```
PS> Get-Win32ModuleExport "kernel32.dll" -ProcAddress CreateMutexEx
Exception calling "GetProcAddress" with "2" argument(s):
"(0x8007007F) - The specified procedure could not be found."
```


*代码清单 3-15：从* KERNEL32 *获取 CreateMutexEx*

我们不仅没有获得地址，反而遇到了异常。是不是我们选错了库？让我们尝试通过转储所有导出项并按名称筛选来查找该 API，如 代码清单 3-16 所示。




```
PS> Get-Win32ModuleExport "kernel32.dll" | Where-Object Name -Match CreateMutexEx

Ordinal Name           Address
------- ----           -------
217     CreateMutexExA 0x7FFA088C1EB0
218     CreateMutexExW 0x7FFA088C1EC0
```


*代码清单 3-16：通过列出所有导出项来查找 CreateMutexEx API*

如你所见，CreateMutexEx API 不仅存在，而且出现了两次。每个函数都有一个后缀，要么是 A，要么是 W。这是因为 Windows 95（大多数 API 最初创建于此系统）并不原生支持 Unicode 字符串，因此这些 API 使用当前文本编码中的单字符字符串。随着 Windows NT 的引入，内核完全支持 Unicode，但为了兼容旧版 Windows 95 应用程序，每个函数都提供了两个 API。

带有 A 后缀的 API 接受单字符字符串，即 *ANSI 字符串*。这些 API 会将字符串转换为 Unicode 字符串以传递给内核，并在需要返回字符串时再转换回来。另一方面，为 Windows NT 构建的应用程序可以使用带有 W 后缀的 API，即 *宽字符串*；这些 API 无需进行任何字符串转换。当你构建原生应用程序时，具体使用哪个 API 取决于你的构建配置，而这属于另一本书的讨论范畴。

### Win32 注册表路径

在第2章中，您学习了如何使用OMNS中的路径通过原生系统调用来访问注册表的基本知识。用于访问注册表的Win32 API（如`RegCreateKeyEx`）并不直接暴露这些OMNS路径。相反，您需要相对于预定义的根键来访问注册表键。如果您曾经使用过Windows的`regedit`应用程序，您会对这些键感到熟悉，如图3-3所示。

![img](./image/01.%20PART%20I%20AN%20OVERVIEW%20OF%20THE%20WINDOWS%20OPERATING%20SYSTEM/Figure3-3.webp)

图3-3：`regedit`工具的主视图

图3-3中显示的句柄值及其对应的OMNS路径列于表3-1中。

| 预定义句柄名称       | OMNS路径                                                     |
| :------------------- | :----------------------------------------------------------- |
| HKEY_LOCAL_MACHINE   | \REGISTRY\MACHINE                                            |
| HKEY_USERS           | \REGISTRY\USER                                               |
| HKEY_CURRENT_CONFIG  | \REGISTRY\MACHINE\SYSTEM\CurrentControlSet\Hardware Profiles\Current |
| HKEY_CURRENT_USER    | \REGISTRY\USER\<SDDL SID>                                    |
| HKEY_CLASSES_ROOT    | \REGISTRY\MACHINE\SOFTWARE\Classes 和 \REGISTRY\USER\<SDDL SID>_Classes 的合并视图 |

前三个预定义句柄（HKEY_LOCAL_MACHINE、HKEY_USERS和HKEY_CURRENT_CONFIG）并不特别特殊；它们直接映射到单个OMNS注册表键路径。下一个句柄HKEY_CURRENT_USER则更有趣；它映射到为当前已认证用户加载的配置单元。该配置单元键的名称是用户SID的SDDL字符串。

最后一个键HKEY_CLASSES_ROOT存储诸如文件扩展名映射等信息，它是用户类配置单元和机器配置单元的合并视图。用户配置单元优先于机器配置单元，允许用户更改其文件扩展名而无需管理员权限。

#### 打开键

使用`Get-NtKey`和`New-NtKey`命令时，我们可以通过指定`Win32Path`参数来使用Win32路径（见代码清单 3-17）。




```
PS> Use-NtObject($key = Get-NtKey \REGISTRY\MACHINE\SOFTWARE) {
    $key.Win32Path
}
HKEY_LOCAL_MACHINE\SOFTWARE

PS> Use-NtObject($key = Get-NtKey -Win32Path "HKCU\SOFTWARE") {
    $key.FullPath
}
\REGISTRY\USER\S-1-5-21-818064985-378290696-2985406761-1002\SOFTWARE
```


*代码清单 3-17：使用Win32路径与注册表交互*

我们首先使用`Get-NtKey`命令打开一个`Key`对象。我们使用OMNS路径打开键，然后通过`Win32Path`属性将路径转换为其Win32版本。在此例中，我们看到*\REGISTRY\MACHINE\SOFTWARE*映射到*HKEY_LOCAL_MACHINE\SOFTWARE*。

然后我们反向操作，通过指定`Win32Path`参数使用Win32名称打开一个键，并打印其原生OMNS路径。这里我们使用当前用户的配置单元。请注意，我们使用了预定义键名的缩写形式：`HKCU`，而不是`HKEY_CURRENT_USER`。所有其他预定义键都有类似的缩写形式；例如，`HKLM`指的是`HKEY_LOCAL_MACHINE`。

在输出中，您可以看到表示当前用户的SDDL SID字符串。正如这个示例所示，使用Win32路径访问当前用户的配置单元比查找当前用户的SID并使用OMNS路径打开它要简单得多。

#### 列出注册表内容

在上一章中，您看到了如何使用*NtObject*或*NtKey*驱动器提供程序路径来列出注册表的内容。对于Win32注册表，您还有一些额外的选项。为了简化对当前用户配置单元的访问，您可以使用*NtKeyUser*。例如，您可以使用以下命令列出当前用户的软件键：


```
PS> ls NtKeyUser:\SOFTWARE
```


PowerShell还自带内置驱动器*HKLM*和*HKCU*，分别用于本地机器和当前用户的配置单元。例如，与上述命令等效的命令如下：


```
PS> ls HKCU:\SOFTWARE
```


为什么您会使用其中一个驱动器提供程序而不是另一个呢？嗯，PowerShell模块的驱动器提供程序的优势在于允许您查看整个注册表。它们还使用原生API，这些API使用计数字符串并支持在注册表键和值的名称中使用NUL字符。相比之下，Win32 API使用以NUL结尾的C风格字符串，无法处理嵌入的NUL字符。因此，如果名称中嵌入了NUL，内置提供程序将无法访问该键或值。代码清单 3-18演示了这一点。




```
❶ PS> $key = New-NtKey -Win32Path "HKCU\ABC`0XYZ"
❷ PS> Get-Item "NtKeyUser:\ABC`0XYZ"
Name    TypeName
----    --------
ABC XYZ Key

❸ PS> Get-Item "HKCU:\ABC`0XYZ"
Get-Item : Cannot find path 'HKCU:\ABC XYZ' because it does not exist.

PS> Remove-NtKey $key
PS> $key.Close()
```

*代码清单 3-18：添加并访问包含 NUL 字符的注册表键*

我们首先创建一个名称中包含 NUL 字符的新键，该字符由 `0 转义符 ❶ 表示。如果你通过 *NtKeyUser* 驱动器访问此路径，可以成功检索到该键 ❷。然而，如果你尝试使用内置的驱动器提供程序，则无法正常工作；它找不到该注册表键 ❸。

Win32 API 的这种行为可能导致安全问题。例如，恶意代码可以通过在名称中嵌入 NUL 字符，向任何使用 Win32 API 的软件隐藏注册表键和值。这可以防止恶意代码被检测到。我们将在本章稍后的“查找隐藏的注册表键或值”一节中了解如何检测并揭示这种隐藏技术的利用。

如果某些软件使用原生系统调用，而其他软件使用 Win32 API，也可能出现不匹配的情况。例如，如果某些代码检查 *ABC`0XYZ* 路径以确保其已正确设置，然后将此路径交给另一个应用程序，该应用程序使用 Win32 API 访问该路径，那么新应用程序将转而访问未经过检查的无关 *ABC* 键。如果 *ABC* 的内容被返回给调用者，这可能导致信息泄露问题。

内置的注册表提供程序也有一个优势：它可以在不安装外部模块的情况下使用。它还允许你创建新键并添加值，而模块的提供程序则不允许这样做。

### DOS 设备路径

Win32 API 与原生系统调用之间的另一个重大区别在于它们如何处理文件路径。在上一章中，我们了解到可以通过 *Device\<VolumeName>* 路径访问已挂载的文件系统。然而，我们无法使用 Win32 API 指定这种原生路径。相反，我们使用众所周知的路径，如 *C:\Windows*，这些路径带有驱动器号。由于驱动器号路径是 MS-DOS 的遗留物，我们将其称为 *DOS 设备路径*。

当然，Win32 API 需要向系统调用传递原生路径，以便系统调用正确工作。*NTDLL* API 中的 `RtlDosPathNameToNtPathName` 负责处理这一转换过程。该 API 接受一个 DOS 设备路径，并返回完全转换后的原生路径。最简单的转换发生在调用者提供了完整驱动器路径时，例如 *C:\Windows*。在这种情况下，转换过程仅需在路径前加上预定义路径前缀 *\??*，得到结果 *\??\C:\Windows*。

*\??* 路径，也称为 *DOS 设备映射前缀*，指示对象管理器使用两步查找过程来查找驱动器号。对象管理器首先会检查路径 *Sessions\0\DosDevices\<AUTHID>* 下的每用户 DOS 设备映射目录。由于对象管理器首先检查每用户位置，因此每个用户都可以创建自己的驱动器映射。*<AUTHID>* 组件与调用者令牌的认证会话相关；我将在第4章中对此进行描述，但目前只需知道其值对每个用户是唯一的即可。请注意，控制台会话 ID 使用 *0* 并非笔误：所有 DOS 设备映射都放置在单一位置，无论用户登录到哪个控制台会话。

如果在每用户位置未找到驱动器号，对象管理器将检查全局目录 *GLOBAL??*。如果在那里也未找到，则文件查找失败。驱动器号是一个对象管理器符号链接，指向已挂载的卷设备。我们可以通过使用 `Get-NtSymbolicLink` 命令打开驱动器号并显示其属性来观察这一过程（代码清单 3-19）。

```
PS> Use-NtObject($cdrive = Get-NtSymbolicLink "\??\C:") {
    $cdrive | Select-Object FullPath, Target
}
FullPath     Target
--------     ------
❶ \GLOBAL??\C: \Device\HarddiskVolume3

❷ PS> Add-DosDevice Z: C:\Windows
PS> Use-NtObject($zdrive = Get-NtSymbolicLink "\??\Z:") {
    $zdrive | Select-Object FullPath, Target
}
FullPath                                    Target
--------                                    ------
❸ \Sessions\0\DosDevices\00000000-011b224b\Z: \??\C:\windows

❹ PS> Remove-DosDevice Z:
```

*代码清单 3-19：显示* C: *和* Z: *驱动器的符号链接*

首先，我们打开 *C:* 驱动器符号链接并显示其 `FullPath` 和 `Target` 属性。完整路径位于 *\GLOBAL??* 目录中，目标是卷路径 ❶。然后，我们使用 `Add-DosDevice` 命令创建一个新的 *Z:* 驱动器，将其指向 *Windows* 目录 ❷。请注意，*Z:* 驱动器在任何用户应用程序中都可访问，而不仅仅是在 PowerShell 中。显示 *Z:* 驱动器的属性揭示其位于每用户 DOS 设备映射中，目标是 *Windows* 目录的原生路径 ❸。这表明驱动器号的目标不必直接指向卷，只要最终能到达那里即可（在这种情况下，通过跟随 *C:* 驱动器符号链接）。最后，为了完整性，我们使用 `Remove-DosDevice` 移除 *Z:* 驱动器 ❹。

#### 路径类型

表 3-2 显示了 Win32 API 支持的几种不同路径类型，以及转换后的示例原生路径。

| DOS 路径            | 原生路径               | 描述                        |
| :------------------ | :------------------------ | :--------------------------------- |
| some\path           | \??\C:\ABC\some\path      | 相对于当前目录的路径 |
| C:\some\path        | \??\C:\some\path          | 绝对路径                      |
| C:some\path         | \??\C:\ABC\some\path      | 驱动器相对路径                |
| \some\path          | \??\C:\some\path          | 相对于当前驱动器根目录            |
| \\.\C:\some\..\path | \??\C:\path               | 设备路径，规范化         |
| \\?\C:\some\..\path | \??\C:\some\..\path       | 设备路径，非规范化     |
| \??\C:\some\path    | \??\C:\some\path          | 设备路径，非规范化     |
| \\server\share\path | \??\UNC\server\share\path | 服务器上共享的 UNC 路径        |

由于 DOS 路径的指定方式，多个 DOS 路径可能表示相同的原生路径。为确保最终的原生路径正确，DOS 路径必须经过 *规范化* 过程，将这些不同的表示转换为相同的规范形式。

规范化处理中一个简单的操作是处理路径分隔符。对于原生路径，只有一个路径分隔符，即反斜杠（`\`）字符。如果使用正斜杠（`/`），对象管理器会将其视为另一个文件名中的字符。然而，DOS路径同时支持正斜杠和反斜杠作为路径分隔符。规范化过程通过确保所有正斜杠转换为反斜杠来处理这一点。因此，`C:\Windows` 和 `C:/Windows` 是等价的。

另一个规范化操作是解析父目录引用。在编写DOS路径时，可能会指定带有一个点（`.`）或两个点（`..`）的文件名，每个都有特殊含义。单个点表示当前目录，规范化过程会将其从路径中移除。双点表示父目录，因此父目录会被移除。因此，路径 `C:\ABC\.\XYZ` 会被转换为 `C:\ABC\XYZ`，而 `C:\ABC\..\XYZ` 会被转换为 `C:\XYZ`。与正斜杠一样，原生API不知道这些特殊文件名，会假定它们是待查找文件的名称。

> 注意
>
> *大多数其他操作系统，如Linux，在内核中处理此规范化过程。然而，由于子系统模型，Windows必须在用户模式下，在子系统特定的库中执行路径规范化。这是为了支持OS/2和POSIX环境中的行为差异。*

如果DOS路径以 `\\?\` 或 `\??\` 为前缀，则该路径不会被规范化，而是按原样使用，包括任何父目录引用或正斜杠。在某些情况下，`\??\` 前缀可能会使Win32 API混淆为当前驱动器根路径，导致打开类似 `\??\C:\??\Path` 的路径。考虑到其潜在的混淆性，微软为何添加这种DOS路径类型尚不清楚。

你可以使用 `Get-NtFilePath` 命令手动将Win32路径转换为原生路径。还可以使用 `Get-NtFilePathType` 命令检查路径类型。代码清单 3-20 展示了使用这些命令的一些示例。




```
PS> Set-Location $env:SystemRoot
PS C:\Windows> Get-NtFilePathType "."
Relative

PS C:\Windows> Get-NtFilePath "."
\??\C:\Windows

PS C:\Windows> Get-NtFilePath "..\"
\??\C:\

PS C:\Windows> Get-NtFilePathType "C:ABC"
DriveRelative

PS C:\Windows> Get-NtFilePath "C:ABC"
\??\C:\Windows\ABC

PS C:\Windows> Get-NtFilePathType "\\?\C:\abc/..\xyz"
LocalDevice

PS C:\Windows> Get-NtFilePath "\\?\C:\abc/..\xyz"
\??\C:\abc/..\xyz
```


*代码清单 3-20：Win32文件路径转换示例*

当使用 `Get-NtFile` 或 `New-NtFile` 命令时，可以使用 `Win32Path` 属性将路径视为Win32路径并自动转换。

#### 最大路径长度

Windows支持的最大文件名长度受限于 `UNICODE_STRING` 结构中可存储的最大字符数（32,767）。然而，Win32 API有更严格的要求。默认情况下，如 代码清单 3-21 所示，任何尝试传递超过 `MAX_PATH`（定义为260个字符）长度的路径都会失败。此行为在将路径从Win32转换为原生格式时，在 *NTDLL* API `RtlDosPathNameToNtPathName` 中实现。




```
PS> $path = "C:\$('A'*256)"
PS> $path.Length
259

PS> Get-NtFilePath -Path $path
\??\C:\AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...

PS> $path += "A"
PS> $path.Length
260

PS> Get-NtFilePath -Path $path
Get-NtFilePath : "(0xC0000106) - A specified name string is too long..."

PS> $path = "\\?\" + $path
PS> $path.Length
264

PS> Get-NtFilePath -Path $path
\??\C:\AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...
```


*代码清单 3-21：测试Win32 MAX_PATH路径限制*

我们通过 `Get-NtFilePath` 命令调用 `RtlDosPathNameToNtPathName` API。我们创建的第一个路径长度为259个字符，可以成功转换为原生路径。然后我们向路径添加一个字符，使路径长度为260个字符；此尝试失败并返回错误 `STATUS_NAME_TOO_LONG`。如果 `MAX_PATH` 是260，你可能会想：260个字符长的路径不应该成功吗？不幸的是，不会。API将NUL终止字符计入路径长度，因此最大路径长度实际上只有259个字符。

代码清单 3-21 还展示了一种绕过此限制的方法。如果我们在路径中添加设备前缀 `\\?\`，即使路径长度现在为264个字符，转换也会成功。这是因为前缀被替换为DOS设备前缀 `\??\`，其余路径按原样保留。虽然此技术有效，但请注意它也会禁用一些有用的功能，如路径规范化。作为另一种解决方法，在当前版本的Windows中，有一种选择启用长文件名的方法，如 代码清单 3-22 所示。




```
PS> $path = "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem"
PS> Get-NtKeyValue -Win32Path $path -Name "LongPathsEnabled"
Name             Type  DataObject
----             ----  ----------
LongPathsEnabled Dword 1

PS> (Get-Process -Id $pid).Path | Get-Win32ModuleManifest |
Select-Object LongPathAware
LongPathAware
-------------
        ❶ True

❷ PS> $path = "C:\$('A'*300)"
PS> $path.Length
303

PS> Get-NtFilePath -Path $path
\??\C:\AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...
```


*代码清单 3-22：检查并测试支持长路径的应用程序*

我们首先要验证 `LongPathsEnabled` 注册表值已设置为 1。该值必须在进程启动前设置，因为它在进程初始化期间只会被读取一次。然而，仅仅启用长路径功能还不够：进程的可执行文件必须通过指定清单属性来选择启用该功能。我们可以使用 `Get-ExecutableManifest` 命令并选择 `LongPathAware` 来查询此属性。幸运的是，PowerShell 已启用此清单选项 ❶。现在，我们可以成功转换更长的路径，如使用 303 个字符的路径所示 ❷。

长路径是否构成安全问题？安全问题通常出现在接口边界处。在这种情况下，文件系统支持超长路径的事实可能导致错误假设，即文件路径永远不会超过 260 个字符。一个潜在的问题可能出现在应用程序查询文件的完整路径，然后将该路径复制到固定大小为 260 个字符的内存缓冲区时。如果未首先检查文件路径的长度，此操作可能导致缓冲区之后的内存损坏，这可能使攻击者能够控制应用程序的执行。

### 进程创建

进程是执行用户模式组件并出于安全目的将其隔离的主要方式，因此详细探讨如何创建进程非常重要。在上一章中，我提到可以使用 `NtCreateUserProcess` 系统调用来创建进程。然而，大多数进程并不会直接通过该系统调用创建，而是通过 Win32 的 `CreateProcess` API 来创建，该 API 充当了一个包装器。

系统调用通常不直接使用，因为大多数进程需要与其他用户模式组件（尤其是 CSRSS）交互，以便与用户的桌面进行交互。`CreateProcess` API 会将系统调用创建的新进程注册到正确初始化所需的相关服务中。本书不会详细讨论进程和线程的创建，但本节我会给出一个简要概述。

#### 命令行解析

创建新进程的最简单方式是指定一个表示要运行的可执行文件的命令行字符串。`CreateProcess` API 随后会解析该命令行，以找到要传递给内核的可执行文件。

为了测试这种命令行解析，让我们使用 `New-Win32Process` PowerShell 命令创建一个新进程，该命令在底层执行 `CreateProcess`。我们可以使用内置命令（如 `Start-Process`）来完成此操作，但 `New-Win32Process` 很有用，因为它暴露了 `CreateProcess` API 的全部功能。我们可以使用以下命令启动一个进程：

```
PS> $proc = New-Win32Process -CommandLine "notepad test.txt"
```

我们提供了一条包含要运行的可执行文件名称（Notepad）和要打开的文件名称（*test.txt*）的命令行。该字符串不一定需要提供可执行文件的完整路径；`New-Win32Process` 命令会解析命令行，以尝试区分初始可执行映像文件的名称和要打开的文件。这并不像听起来那么简单。

`New-Win32Process` 首先会使用一种按空白字符分割的算法来解析命令行，除非该空白字符被双引号括起来。在这种情况下，它会将命令行解析为两个字符串：`notepad` 和 `test.txt`。然后，该命令取第一个字符串并尝试查找匹配的进程。然而，这里有一个小问题：没有名为 *notepad* 的可执行文件，只有 *notepad.exe*。虽然并非必需，但 Windows 可执行文件通常带有 *.exe* 扩展名，因此搜索算法会在没有扩展名时自动追加该扩展名。

然后，该命令会在以下位置搜索可执行文件，这类似于我们在前文“搜索 DLL”一节中讨论的 DLL 路径搜索。请注意，可执行文件的搜索路径与不安全的 DLL 搜索路径相同：

  1.  当前进程可执行文件所在的目录

  2.  当前工作目录

  3.  Windows 的 *System32* 目录

  4.  *Windows* 目录

  5.  PATH 环境变量中每个以分号分隔的位置

如果 `New-Win32Process` 找不到 *notepad.exe*，它会接着尝试查找文件 *notepad test.txt*，以防这是我们想要的结果。由于该文件名已有扩展名，因此不会将其替换为 *.exe*。如果 `New-Win32Process` 找不到该文件，则会返回错误。请注意，如果我们传递的 `notepad` 被双引号括起来，例如 `"notepad" test.txt`，那么 `New-Win32Process` 将只搜索 *notepad.exe*，而不会回退到尝试名称与空白字符的所有组合。

这种命令行解析行为有两个安全影响。首先，如果进程是由更高权限的进程创建的，而权限较低的用户可以在路径搜索列表中更早的位置写入文件，那么该进程可能会被劫持。

第二个安全影响是，如果第一个值包含路径分隔符，路径搜索算法会发生变化。在这种情况下，`New-Win32Process` 不会使用路径搜索规则，而是按空白字符分割路径，然后尝试将各个分段分别视为路径，依次搜索带有 *.exe* 扩展名或不带扩展名的文件名。

让我们看一个例子。如果我们指定命令行 `C:\Program Files\abc.exe`，那么将搜索以下路径以查找可执行文件：

- *C:\Program*
- *C:\Program.exe*
- *C:\Program Files\abc.exe*
- *C:\Program Files\abc.exe.exe*

如果用户能够写入文件 *C:\Program* 或 *C:\Program.exe*，那么他们就可以劫持执行。幸运的是，在默认的 Windows 安装中，普通用户无法写入系统驱动器根目录；然而，配置更改有时会允许这种情况。此外，可执行文件的路径可能位于允许写入根目录的其他驱动器上。

为了避免这两种安全影响，调用者可以通过在调用 `New-Win32Process` 时设置 `ApplicationName` 属性来指定可执行文件的完整路径名：

```
PS> $proc = New-Win32Process -CommandLine "notepad test.txt"
-ApplicationName "C:\windows\notepad.exe"
```

如果我们以这种方式指定路径，该命令将原样将其传递给新进程。

#### Shell API

如果你在资源管理器中双击一个非可执行文件类型（如文本文档），它会自动为你打开一个编辑器。然而，如果你尝试使用 `New-Win32Process` 运行一个文档，你会看到如下错误：

```
PS> New-Win32Process -CommandLine "document.txt"
Exception calling "CreateProcess": "%1 is not a valid Win32 application"
```

此错误表明该文本文件不是有效的 Win32 应用程序。

资源管理器之所以能启动编辑器，是因为它并未直接使用底层的 `CreateProcess` API，而是使用了 Shell API。用于为文件启动编辑器的主要 Shell API 是 `ShellExecuteEx`，它实现在 *SHELL32* 库中。该 API 及其更简单的兄弟版本 `ShellExecute` 过于复杂，无法在此详细讨论。我将仅简要概述后者。

就我们的目的而言，我们需要向 `ShellExecute` 指定三个参数：

- 要执行的文件的路径
- 对文件执行的操作（verb）
- 任何附加参数

`ShellExecute` 首先会查找要执行文件的扩展名对应的处理器。例如，如果文件是 *test.txt*，则需要查找 *.txt* 扩展名的处理器。这些处理器在注册表的 `HKEY_CLASSES_ROOT` 键下注册，正如本章前面所述，该键是机器软件和用户注册表配置单元的部分合并视图。在 代码清单 3-23 中，我们查询了该处理器。

```
PS> $base_key = "NtKey:\MACHINE\SOFTWARE\Classes"
❶ PS> Get-Item "$base_key\.txt" | Select-Object -ExpandProperty Values
Name          Type   DataObject
----          ----   ----------
Content Type  String text/plain
PerceivedType String text
            ❷ String txtfile

❸ PS> Get-ChildItem "$base_key\txtfile\Shell" | Format-Table
Name    TypeName
----    --------
open    Key
print   Key
printto Key

❹ PS> Get-Item "$base_key\txtfile\Shell\open\Command" |
Select-Object -ExpandProperty Values | Format-Table
Name Type         DataObject
---- ----         ----------
   ❺ ExpandString %SystemRoot%\system32\NOTEPAD.EXE %1
```

*代码清单 3-23：查询* .txt *文件的 Shell 处理器*

我们首先查询机器类键下的 *.txt* 扩展名 ❶。虽然我们也可以检查用户特定的键，但检查机器类键可以确保我们检查的是系统默认设置。*.txt* 注册表键并不直接包含处理器。相反，默认值（以空名称表示）指向另一个键：在本例中为 `txtfile` ❷。然后我们列出 `txtfile` 的子键，找到三个键：`open`、`print` 和 `printto` ❸。我们可以将这些操作名称传递给 `ShellExecute`。

每个操作键都可以有一个名为 `Command` 的子键，其中包含要执行的命令行 ❹。我们可以看到 *.txt* 文件的默认操作是打开记事本 ❺；`%1` 会被替换为要执行文件的路径。（命令也可以包含 `%*`，它会包含传递给 `ShellExecute` 的任何附加参数。）现在，`CreateProcess` API 可以启动可执行文件并处理该文件。

你可以向 `ShellExecute` 传递许多不同的标准操作。表 3-3 列出了你可能会遇到的一些常见操作。

| 操作      | 描述                                                         |
| :-------- | :----------------------------------------------------------- |
| open      | 打开文件；这通常是默认操作。                                 |
| edit      | 编辑文件。                                                   |
| print     | 打印文件。                                                   |
| printto   | 打印到指定打印机。                                           |
| explore   | 浏览目录；用于在资源管理器窗口中打开目录。                   |
| runas     | 以管理员身份打开文件；通常仅对可执行文件定义。               |
| runasuser | 以其他用户身份打开文件；通常仅对可执行文件定义。             |

你可能会觉得同时存在 `open` 和 `edit` 操作很奇怪。例如，如果你打开一个 *.txt* 文件，它会在记事本中打开，并且你可以编辑它。但对于批处理文件等文件，这种区分就很有用：`open` 操作会执行文件，而 `edit` 操作会在文本编辑器中打开它。

要从 PowerShell 使用 `ShellExecute`，可以运行 `Start-Process` 命令。默认情况下，`ShellExecute` 会使用 `open` 操作，但你可以使用 `Verb` 参数指定自己的操作。在以下代码中，我们使用 `print` 操作以管理员身份打印一个 *.txt* 文件：

```
PS> Start-Process "test.txt" -Verb "print"
```

操作配置还可以提高安全性。例如，扩展名为 *.ps1* 的 PowerShell 脚本注册了 `open` 操作。然而，点击脚本会在记事本中打开脚本文件，而不是执行脚本。因此，如果你在资源管理器中双击脚本文件，它不会执行。相反，你必须右键单击文件并明确选择 **使用 PowerShell 运行**。

如前所述，Shell API 的完整细节超出了本书的范围；正如你所预料的那样，完整的情况并不像我这里展示的那么简单。

### 系统进程

在本章及前一章中，我多次提到一些以比普通用户更高权限运行的进程。这是因为，即使没有用户登录操作系统，系统仍需要执行诸如等待身份验证、管理硬件以及通过网络通信等任务。

内核可以执行其中部分任务。然而，编写内核代码比编写用户模式代码更为困难，原因有多方面：内核可用的API范围较窄；资源受限，尤其是在内存方面；而且任何编码错误都可能导致系统崩溃或暴露安全漏洞。

为避免这些挑战，Windows在内核模式之外运行多种高权限进程，以提供重要功能。在本节中，我们将介绍其中一些特殊进程。

#### 会话管理器

*会话管理器子系统（SMSS）* 是内核在启动后启动的第一个用户模式进程。它负责为后续进程设置工作环境。其部分职责包括：

- 加载已知的DLL并创建节对象
- 启动子系统进程，如CSRSS
- 初始化基本DOS设备，如串行端口
- 运行自动磁盘完整性检查

#### Windows login 进程

*Windows登录*进程负责设置新的控制台会话，并显示登录用户界面（主要通过LogonUI应用程序实现）。它还负责启动*用户模式字体驱动程序（UMFD）*进程（用于在屏幕上渲染字体）以及*桌面窗口管理器（DWM）*进程（执行桌面合成操作，以实现炫酷的透明窗口和现代GUI效果）。

#### LSA子系统

我已在SRM的上下文中提到过LSASS。然而，值得强调其在身份验证中的重要作用。没有LSASS，用户将无法登录系统。我们将在第10章中更详细地介绍LSASS的角色和职责。

#### 服务控制管理器

*服务控制管理器（SCM）* 负责启动Windows上大多数特权系统进程。它管理这些被称为*服务*的进程，并可根据需要启动和停止它们。例如，SCM可以根据特定条件（如网络变为可用）启动服务。

每个服务都是可安全保护的资源，具有细粒度控制，决定哪些用户可以操作其状态。默认情况下，只有管理员才能操作服务。以下是任何Windows系统上运行的一些最重要服务：

**RPC子系统（RPCSS）**    RPCSS服务管理RPC端点的注册，将注册信息暴露给本地客户端以及通过网络暴露。此服务对运行中的系统至关重要；实际上，如果此进程崩溃，将强制Windows重新启动。

**DCOM服务器进程启动器**    DCOM服务器进程启动器是RPCSS的对应组件（曾属于同一服务）。它用于代表本地或远程客户端启动组件对象模型（COM）服务器进程。

**任务计划程序**    能够在特定时间和日期安排操作执行是操作系统的一项有用功能。例如，您可能希望确保按特定计划删除未使用的文件。您可以使用任务计划程序服务设置一个操作，按该计划运行清理工具。

**Windows安装程序**    此服务可用于安装新程序和功能。通过以特权服务身份运行，它允许在文件系统上通常受保护的位置进行安装和修改。

**Windows更新**    保持操作系统完全更新对Windows系统的安全至关重要。当Microsoft发布新的安全修复程序时，应尽快安装。为避免要求用户检查更新，此服务在后台运行，定期唤醒以检查互联网上的新补丁。

**应用程序信息**    此服务提供在同一桌面上在管理员和非管理员用户之间切换的机制。此功能通常称为*用户账户控制（UAC）*。您可以使用shell API中的runas动词启动管理员进程。我们将在下一章中介绍UAC在底层的工作原理。

我们可以使用各种工具查询由SCM控制的所有服务的状态。PowerShell内置了`Get-Service`命令；然而，本书使用的PowerShell模块提供了一个更全面的命令`Get-Win32Service`，该命令能够检查服务的配置安全性以及默认命令未公开的其他属性。代码清单 3-24展示了如何查询所有当前服务。

```
PS> Get-Win32Service
Name               Status   ProcessId
----               ------   ---------
AarSvc             Stopped  0
AESMService        Running  7440
AJRouter           Stopped  0
ALG                Stopped  0
AppIDSvc           Stopped  0
Appinfo            Running  8460
--snip--
```

*代码清单 3-24：使用Get-Win32Service显示所有服务*

输出显示服务的名称、其状态（要么是“已停止”，要么是“正在运行”），以及如果服务正在运行，则显示服务进程的进程ID。如果您使用`Format-List`列出服务的属性，您还将能够看到其他信息，例如服务的完整描述。

### 实际示例

让我们通过一些实际示例来练习使用本章中介绍的各种命令，以进行安全研究或系统分析。

#### 查找导入特定API的可执行文件

在本章开头，您看到了如何使用 `Get-Win32ModuleImport` 命令来提取可执行文件的导入API。当我试图追踪安全问题时，我发现这个命令的一个特别有用的用途是识别所有使用特定API（如 `CreateProcess`）的可执行文件，然后利用这个列表来减少需要逆向工程的文件数量。您可以使用 代码清单 3-25 中所示的基本PowerShell脚本执行此类搜索。




```
PS> $imps = ls "$env:WinDir\*.exe" | ForEach-Object {
    Get-Win32ModuleImport -Path $_.FullName
}
PS> $imps | Where-Object Names -Contains "CreateProcessW" |
Select-Object ModulePath
ModulePath
----------
C:\WINDOWS\explorer.exe
C:\WINDOWS\unins000.exe
```


*代码清单 3-25：查找导入 CreateProcess 的可执行文件*

在这里，我们首先枚举 *Windows* 目录中的所有 *.exe* 文件。对于每个可执行文件，我们调用 `Get-Win32ModuleImport` 命令。这将加载模块并解析其导入。这可能是一个耗时的过程，因此最好将结果捕获到变量中，就像我们在这里所做的那样。

接下来，我们仅选择包含 `CreateProcessW` API 的导入。`Names` 属性是一个列表，包含单个 DLL 的导入名称。要获取导入特定API的可执行文件的结果列表，我们可以选择 `ModulePath` 属性，该属性包含原始加载的路径名。

您可以使用相同的技术来枚举 DLL 文件或驱动程序，并快速发现逆向工程的目标。

#### 查找隐藏的注册表键或值

在“列出注册表内容”一节中，我提到使用原生系统调用而非 Win32 API 与注册表交互的一大优势是，它们允许您访问名称中包含 NUL 字符的键和值。能够找到这些键和值将非常有用，这样您就可以尝试检测系统中主动向用户隐藏注册表键或值的软件（某些恶意软件家族，如 Kovter 和 Poweliks，已知会使用此技术）。让我们首先查找名称中包含 NUL 字符的键（代码清单 3-26）。




```
PS> $key = New-NtKey -Win32Path "HKCU\SOFTWARE\`0HIDDENKEY"
PS> ls NtKeyUser:\SOFTWARE -Recurse | Where-Object Name -Match "`0"
Name                TypeName
----                --------
SOFTWARE\ HIDDENKEY Key

PS> Remove-NtKey $key
PS> $key.Close()
```


*代码清单 3-26：查找隐藏的注册表键*

我们首先在当前用户配置单元中创建一个名称中包含 NUL 字符的键。如果您尝试使用内置的注册表提供程序查找此键，将会失败。相反，我们递归列出当前用户配置单元，并选择名称中包含 NUL 字符的任何键。在输出中，您可以看到发现了隐藏的键。

要查找隐藏的值，我们可以通过枚举键的 `Values` 属性来查询键的值列表。每个值包含键的名称和数据值（代码清单 3-27）。




```
❶ PS> $key = New-NtKey -Win32Path "HKCU\SOFTWARE\ABC"
PS> Set-NtKeyValue -Key $key -Name "`0HIDDEN" -String "HELLO"
❷ PS> function Select-HiddenValue {
    [CmdletBinding()]
    param(
        [parameter(ValueFromPipeline)]
        $Key
    )

    Process {
      ❸ foreach($val in $Key.Values) {
            if ($val.Name -match "`0") {
                [PSCustomObject]@{
                    RelativePath = $Key.RelativePath
                    Name = $val.Name
                    Value = $val.DataObject
                }
            }
        }
    }
}
❹ PS> ls -Recurse NtKeyUser:\SOFTWARE | Select-HiddenValue | Format-Table
RelativePath Name    Value
------------ ----    -----
SOFTWARE\ABC HIDDEN  HELLO

PS> Remove-NtKey $key
PS> $key.Close()
```


*代码清单 3-27：查找隐藏的注册表值*

我们首先创建一个普通键，然后添加一个名称中包含 NUL 字符的值 ❶。接着，我们定义一个函数 `Select-HiddenValue` ❷，该函数将检查管道中的键，并选择名称中包含 NUL 字符的任何值，然后将自定义对象返回到管道 ❸。

接下来，我们递归枚举当前用户配置单元，并通过 `Select-HiddenValue` 函数过滤键 ❹。您可以在输出中看到我们发现了隐藏的值。

### 总结

本章快速浏览了Windows用户模式组件。我们从深入探讨Win32 API和DLL的加载开始。理解这一主题至关重要，因为它揭示了用户模式应用程序如何与内核通信并实现常见功能。

接下来，我概述了Win32 GUI，包括对用于*WIN32K*的独立系统调用表的描述，*WIN32K*是Win32子系统的内核模式组件。我介绍了窗口站和桌面对象类型，并概述了控制台会话的目的，以及它如何与用户所见的桌面相对应。

随后，我回到Win32 API的主题，详细说明了Win32 API（此处为CreateMutexEx）与底层系统调用（NtCreateMutant）之间的差异与相似之处。这一讨论应能让您更好地理解Win32 API如何与操作系统其余部分交互。我还介绍了DOS设备路径与系统调用所理解的原生路径之间的差异，这一主题对于理解用户模式应用程序如何与文件系统交互至关重要。

最后，我讨论了与Win32进程和线程相关的几个主题，涵盖了直接创建进程或通过shell创建进程所用的API，并概述了知名的系统进程。在后续章节中，我们将更深入地重新探讨这些主题。在接下来的三章中，我们将聚焦于Windows如何通过SRM实现安全性。