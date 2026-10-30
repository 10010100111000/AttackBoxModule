---

summary: 《Windows Security Internals》（Windows安全内部原理）第2卷：Windows安全参考监视器（SRM）。全面深入剖析 Windows 访问控制核心引擎 SRM 的运行机制。核心内容包含：1. 安全访问令牌（Security Access Token）机制，详述主令牌与模拟令牌、伪令牌句柄、令牌组属性（Mandatory/EnabledByDefault）、特权管理（Privilege）、受限令牌与 Lowbox AppContainer 沙箱令牌、用户账户控制（UAC）拆分令牌与提升机制；2. 安全描述符（Security Descriptor）与 SDDL 语法，解析二进制结构、SID 格式、自主访问控制列表（DACL）、系统审计控制列表（SACL）以及各类访问控制项（ACE）结构；3. 安全描述符的读取与分配继承算法；4. 访问检查（Access Check）完整算法流程重构，剖析企业中央访问策略（CAP）与动态声明（Claims）；5. 遍历检查（Bypass Traverse Checking）、句柄复制与沙箱隔离等衍生安全场景；6. 安全审计（Security Auditing）与安全事件日志监控。是挖掘 Windows 本地权限提升（LPE）与沙箱逃逸漏洞的权威指南。

---

## 4. 安全访问令牌

*安全访问令牌*，简称*令牌*，是Windows安全的核心。安全参考监视器(Security Reference Monitor, SRM)利用令牌来表示身份，如用户账户，并据此授予或拒绝其对资源的访问。Windows以Token内核对象的形式表示令牌，这些对象至少包含其所代表的具体身份、该身份所属的任何安全组，以及该身份已获得的特殊特权。

与其他内核对象一样，令牌支持查询和设置信息系统调用，允许用户检查令牌的属性并设置某些属性。尽管不太常用，一些Win32 API也暴露了这些设置和查询系统调用：例如，`GetTokenInformation` 和 `SetTokenInformation`。

让我们首先概述在分析Windows系统安全性时将会遇到的两种主要令牌类型：主令牌和模拟令牌。然后，我们将详细说明令牌所包含的许多重要属性。在讨论第7章中的访问检查之前，您需要理解这些内容。

### 主令牌

每个进程都有一个分配的令牌，用于描述其在任何资源访问操作中的身份。当SRM执行访问检查时，它会查询进程的令牌，并利用该令牌来确定授予何种访问权限。当令牌赋予进程使用时，被称为*主令牌（Primary Token）*。

你可以通过调用NtOpenProcessToken系统调用来打开进程的令牌，该调用会返回一个句柄，你可以使用该句柄查询令牌信息。由于令牌对象是一个受保护资源，调用者必须通过访问检查才能获取句柄。请注意，你还需要具有QueryLimitedInformation访问权限的进程句柄才能查询令牌。

打开令牌对象时，你可以请求以下访问权限：

- AssignPrimary  将令牌对象分配为主令牌


- Duplicate  复制令牌对象

- Impersonate  模拟令牌对象

- Query  查询令牌对象的属性，如组和特权

- QuerySource  查询令牌对象的来源

- AdjustPrivileges  调整令牌对象的特权列表

- AdjustGroups  调整令牌对象的组列表

- AdjustDefault  调整令牌对象中其他访问权限未涵盖的属性

- AdjustSessionId  调整令牌对象的会话ID


你可以通过运行PowerShell命令`Show-NtToken -All`来查看可访问的进程及其令牌列表。这应会打开令牌查看器应用程序，如图4-1所示。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure4-1.webp)

图4-1：令牌查看器列出了所有可访问的进程及其令牌。

列表视图仅提供可用令牌的简单概览。如果你想查看更多信息，请双击其中一个进程条目，以调出令牌的详细视图，如图4-2所示。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure4-2.webp)

图4-2：进程令牌对象的详细视图

让我们突出此视图中的几个重要信息。顶部是用户名和SID。令牌对象仅存储SID，但令牌视图会在可用时显示名称。下一个字段指示令牌的类型。由于我们当前检查的是主令牌，类型显示为“Primary（主令牌）”。模拟级别（位于其下方）仅用于模拟令牌，我们将在下一节讨论。主令牌不需要此字段，因此显示为“不适用”。

对话框中间列出了四个64位整数标识符：

**令牌ID**    创建令牌对象时分配的唯一值

**认证ID**    指示令牌所属登录会话的值

**来源登录ID**    父登录会话的认证标识符

**修改ID**    当某些令牌值被修改时更新的唯一值

当用户向Windows机器进行身份验证时，LSASS会创建一个*登录会话*。登录会话跟踪用户的认证相关资源；例如，它存储用户凭据的副本，以便可以重用。在登录会话创建过程中，SRM会生成一个唯一的认证标识符值，可用于引用该会话。因此，对于给定的登录会话，所有用户令牌将具有相同的认证标识符。如果用户对同一台机器进行两次身份验证，SRM将生成不同的认证标识符。

来源登录标识符指示谁创建了令牌的登录会话。如果你在桌面上对不同的用户进行身份验证（例如，通过调用带有用户名和密码的LogonUser API），则来源登录标识符将作为调用令牌的认证标识符。请注意，图4-2中的此字段显示值为00000000-000003E7。这是SRM定义的四个固定认证标识符之一，在此情况下表示*SYSTEM*登录会话。表4-1显示了这四个固定值，以及与会话关联的用户账户的SID。

| 认证标识符 | 用户SID | 登录会话用户名 |
| :------------------------ | :------- | :--------------------------- |
| 00000000-000003E4         | S-1-5-20 | NT AUTHORITY\NETWORK SERVICE |
| 00000000-000003E5         | S-1-5-19 | NT AUTHORITY\LOCAL SERVICE   |
| 00000000-000003E6         | S-1-5-7  | NT AUTHORITY\ANONYMOUS LOGON |
| 00000000-000003E7         | S-1-5-18 | NT AUTHORITY\SYSTEM          |

在详细视图中的标识符之后，是一个指示令牌*完整性级别*的字段。Windows Vista 首次添加了完整性级别，以实现简单的*强制访问控制*机制，通过该机制，系统范围的策略强制对资源的访问，而不是允许单个资源自行指定其访问权限。我们将在本章稍后的“令牌组”一节中讨论完整性级别。

接下来是会话ID，这是一个分配给进程所附加的控制台会话的编号。尽管控制台会话是进程的属性，但该值在进程的令牌中指定。

本地唯一标识符

我提到过令牌的标识符是64位整数。从技术上讲，它们是包含两个32位值的本地唯一标识符（LUID）结构。LUID是一种常见的系统类型，SRM在需要唯一值时使用它们。例如，它们用于唯一标识特权值。

您可以通过调用NtAllocateLocallyUniqueId系统调用或执行Get-NtLocallyUniqueId PowerShell命令来分配自己的LUID。当您使用系统调用时，Windows确保它有一个中央权威来生成下一个唯一ID。这一点很重要，因为重用值可能是灾难性的。例如，如果LUID被重用为令牌的认证标识符，它可能会与表4-1中定义的标识符重叠。这可能会欺骗系统，使其认为更特权的用户正在访问资源，从而导致特权提升。

如果您想手动检查令牌的信息，Token Viewer GUI非常有用。对于编程访问，您可以使用Get-NtToken命令在PowerShell中打开一个Token对象。使用以下命令获取当前进程的令牌：


```
PS> $token = Get-NtToken
```


如果您想打开特定进程的令牌，可以使用此命令，将<PID>替换为目标进程的进程ID：


```
PS> $token = Get-NtToken -ProcessId <PID>
```


Get-NtToken命令的结果是一个Token对象，您可以查询其属性。例如，您可以显示令牌的用户，如代码清单 4-1所示。


```
PS> $token.User
Name                  Attributes
----                  ----------
GRAPHITE\user         None
```


*代码清单 4-1：通过Token对象的属性显示用户*

使用Format-NtToken命令将基本信息输出到控制台，如代码清单 4-2所示。




```
PS> Format-NtToken $token -All
USER INFORMATION
----------------
Name                  Attributes
----                  ----------
GRAPHITE\user         None

GROUP SID INFORMATION
---------------------
Name                  Attributes
----                  ----------
GRAPHITE\None         Mandatory, EnabledByDefault
Everyone              Mandatory, EnabledByDefault
--snip--
```


*代码清单 4-2：使用Format-NtToken显示令牌的属性*

您可以将打开的Token对象传递给Show-NtToken，以显示与图4-2中相同的GUI。

### 模拟令牌

你将会遇到的另一种令牌类型是*模拟令牌*。模拟令牌对于系统服务最为重要，因为它们允许一个具有某种身份的进程为了访问检查的目的，临时模拟另一个身份。例如，某个服务在执行某些操作时，可能需要打开属于另一个用户的文件。通过允许该服务模拟调用用户，系统授予它访问该文件的权限，即使该服务无法直接打开该文件。

模拟令牌分配给线程，而非进程。这意味着只有在该线程中运行的代码才会采用被模拟的身份。有三种方式可以将模拟令牌分配给线程：

- 通过显式授予Token对象Impersonate访问权限和Thread对象SetThreadToken访问权限
- 通过显式授予Thread对象DirectImpersonation访问权限
- 隐式地，通过模拟RPC请求

你很可能遇到隐式令牌分配，因为这是系统服务最常见的情况，它们暴露RPC机制。例如，如果服务创建了一个命名管道服务器，它可以使用`ImpersonateNamedPipe` API模拟连接到管道的客户端。当在命名管道上进行调用时，内核会基于调用线程和进程捕获一个*模拟上下文*。这个模拟上下文用于为调用`ImpersonateNamedPipe*`的线程分配一个模拟令牌。模拟上下文可以基于线程上现有的模拟令牌，也可以是进程主令牌的副本。

#### 安全服务质量

如果你不想赋予服务模拟你身份的能力怎么办？SRM支持一个名为*安全服务质量（SQoS）*的功能，使你可以控制这一点。当你使用文件系统API打开命名管道时，可以在`OBJECT_ATTRIBUTES`结构的`SecurityQualityOfService`字段中传递一个`SECURITY_QUALITY_OF_SERVICE`结构。SQoS结构包含三个配置值：模拟级别、上下文跟踪模式和有效令牌模式。

SQoS中的*模拟级别*是控制服务能对你的身份做什么的最重要字段。它定义了服务在隐式模拟调用者时获得的访问级别。该级别可以是四个值之一，按权限升序排列：

1.  **匿名：** 阻止服务打开Token对象并查询用户身份。这是最低级别；如果调用者指定此级别，只有有限的一组服务能够正常工作。
   2.  **标识：** 允许服务打开Token对象并查询用户的身份、组和特权。但是，线程在模拟用户时不能打开任何受保护的资源。
   3.  **模拟：** 允许服务在本地系统上完全行使用户的身份。服务可以打开由用户保护的本地资源并对其进行操作。如果用户已在本地认证到系统，它还可以为用户访问远程资源。但是，如果用户通过网络连接（如通过服务器消息块（SMB）协议）进行认证，则服务不能使用Token对象访问远程资源。
   4.  **委派：** 允许服务以用户本人的身份访问本地和远程资源，是最高级别的模拟级别。不过，对于通过网络身份验证的用户，要访问远程资源，仅仅拥有这种模拟级别还不够。Windows 域还必须配置为允许这种委派。关于这一模拟级别，我们将在第 14 章“Kerberos 身份验证”中进一步讨论。

可以在 SQOS 中指定模拟级别（impersonation level）。既可以在调用服务时指定，也可以在基于现有 Token 创建副本时指定。模拟级别决定了**服务能够在多大程度上代表调用者执行操作**。如果希望限制服务使用调用者身份的能力，可以将模拟级别设置为 Anonymous 或 Identification。在 Anonymous 级别下，服务无法获得调用者的身份信息，也不能代表调用者访问资源。在 Identification 级别下，服务可以获取并查询调用者的身份信息，例如确定调用者是谁，但**不能以该调用者的身份访问受保护资源**。因此，服务可以根据调用者的身份决定是否执行某项操作，但不能仅凭这个模拟上下文获得调用者本人的资源访问权限。相比之下，Impersonation 级别允许服务在本机以调用者的身份访问资源，而 Delegation 级别则进一步允许将该身份用于远程资源访问，但远程委派还需要相应的 Windows 域和 Kerberos 配置。

让我们使用`Invoke-NtToken` PowerShell命令运行一个测试。在代码清单 4-3中，我们在两个不同级别模拟一个令牌，并尝试执行一个打开受保护资源的脚本。我们使用`ImpersonationLevel`属性指定模拟级别。

```
PS> $token = Get-NtToken
PS> Invoke-NtToken $token {
    Get-NtDirectory -Path "\"
} -ImpersonationLevel Impersonation
Name NtTypeName
---- ----------
     Directory

PS> Invoke-NtToken $token {
    Get-NtDirectory -Path "\"
} -ImpersonationLevel Identification
Get-NtDirectory : (0xC00000A5) - A specified impersonation level is invalid.
--snip--
```

*代码清单 4-3：在不同级别模拟令牌并打开受保护资源*

我们执行的第一条命令获取当前进程主令牌的句柄。接着调用 `Invoke-NtToken` 在模拟级别（Impersonation level）模拟该令牌，并运行一个脚本，该脚本调用 `Get-NtDirectory` 打开根 OMNS 目录。打开操作成功，我们将目录对象打印到控制台。

然后我们尝试在标识级别（Identification level）重复该操作，但这次收到 `STATUS_BAD_IMPERSONATION_LEVEL` 错误。（如果在开发应用程序或使用系统时看到此错误，现在你就知道原因了！）请注意，打开操作并未返回“访问拒绝”错误，因为SRM尚未进行到检查模拟用户是否有权访问资源的阶段。

Anonymous模拟级别 VS  ANONYMOUS LOGON 

指定匿名模拟级别与以 表 4-1 中引用的 ANONYMOUS LOGON 用户身份运行不同。以匿名用户身份运行并可能通过访问检查获得资源访问权限是可能的，但匿名级别的令牌无法通过任何访问检查，无论资源的安全配置如何。

内核实现了 `NtImpersonateAnonymousToken` 系统调用，它会在指定线程上模拟匿名用户。你也可以使用 `Get-NtToken` 访问匿名用户令牌：

```
PS> Get-NtToken -Anonymous | Format-NtToken
NT AUTHORITY\ANONYMOUS LOGON
```

SQoS 中的另外两个字段使用频率较低，但同样重要。*上下文跟踪模式* 决定在建立到服务的连接时是否静态捕获用户身份。如果未静态捕获身份，且调用者在调用服务前模拟了其他用户，则新的模拟身份将对服务可用，而非进程身份。请注意，模拟身份只有在模拟级别或委派级别（Delegation level）时才能传递给服务。如果模拟令牌处于标识级别或匿名级别，SRM 会生成安全错误并拒绝模拟操作。

*有效令牌模式* 以不同方式更改传递给服务器的令牌。可以在调用前禁用组和特权，如果有效令牌模式被禁用，服务器可以重新启用这些组和特权并使用它们。然而，如果有效令牌模式被启用，SRM 将剥离这些组和特权，使服务器无法重新启用或使用它们。

默认情况下，如果在打开进程间通信（IPC）通道时未指定 SQoS 结构，调用者的级别为模拟级别，采用静态跟踪和非有效令牌。如果捕获了模拟上下文且调用者已在模拟，则线程令牌的模拟级别必须大于或等于模拟级别；否则捕获将失败。即使 SQoS 请求标识级别，此规则也强制执行。这是一个重要的安全特性；它防止标识级别或更低级别的调用者通过 RPC 通道调用并冒充其他用户。

> 注意*我描述了 SQoS 如何在原生系统调用级别指定，因为 `SECURITY_QUALITY_OF_SERVICE` 结构未通过 Win32 API 直接暴露。相反，它通常通过附加标志指定；例如，`CreateFile` 通过指定 `SECURITY_SQOS_PRESENT` 标志来暴露 SQoS。*
>

#### 显式令牌模拟

有两种显式模拟令牌的方式。如果你拥有具有模拟访问权限的模拟令牌对象句柄，可以使用 `NtSetInformationThread` 系统调用和 `ThreadImpersonationToken` 信息类将其分配给线程。

如果你有一个线程想要使用直接模拟访问权限进行模拟，可以使用另一种机制。通过源线程的句柄，可以调用 `NtImpersonateThread` 系统调用，将模拟令牌分配给另一个线程。使用 `NtImpersonateThread` 是显式和隐式模拟的混合。内核会像源线程通过命名管道调用一样捕获模拟上下文。你甚至可以向系统调用指定 SQoS 结构。

你可能认为模拟会打开一个巨大的安全后门。如果我设置自己的命名管道，并说服特权进程连接到它，而调用者未设置 SQoS 来限制访问，难道我不能获得提升的特权吗？我们将在本章稍后的“令牌分配”一节中探讨如何防范此类风险。

### 在令牌类型之间转换

您可以通过复制在两种令牌类型之间进行转换。当您复制一个令牌时，内核会创建一个新的令牌对象，并深度复制该对象的所有属性。在令牌复制过程中，您可以更改其类型。

此复制操作不同于我们在第3章中讨论的句柄复制，因为复制令牌的句柄仅会创建一个指向同一令牌对象的新句柄。要复制实际的令牌对象，您需要对句柄拥有复制访问权限。

然后，您可以使用`NtDuplicateToken`系统调用或`Copy-NtToken` PowerShell命令来复制令牌。例如，要基于现有令牌创建委派级别的模拟令牌，请使用代码清单 4-4中的脚本。


```
PS> $imp_token = Copy-NtToken -Token $token -ImpersonationLevel Delegation
PS> $imp_token.ImpersonationLevel
Delegation

PS> $imp_token.TokenType
Impersonation
```


*代码清单 4-4：复制令牌以创建模拟令牌*

您可以通过再次使用`Copy-NtToken`将模拟令牌转换回主令牌，如代码清单 4-5所示。


```
PS> $pri_token = Copy-NtToken -Token $imp_token -Primary
PS> $pri_token.TokenType
Primary

PS> $pri_token.ImpersonationLevel
Delegation
```


*代码清单 4-5：将模拟令牌转换为主令牌*

请注意输出中的一个有趣现象：新的主令牌具有与原始令牌相同的模拟级别。这是因为SRM仅考虑令牌类型属性；如果令牌是主令牌，则模拟级别会被忽略。

既然我们可以将模拟令牌转换回主令牌，您可能会想：我们能否将标识级别或匿名级别的令牌转换回主令牌，创建新进程，并绕过SQoS设置？让我们在代码清单 4-6中尝试一下。


```
PS> $imp_token = Copy-NtToken -Token $token -ImpersonationLevel Identification
PS> $pri_token = Copy-NtToken -Token $imp_token -Primary
Exception: "(0xC00000A5) - A specified impersonation level is invalid."
```


*代码清单 4-6：将标识级别令牌复制回主令牌*

此清单显示，我们无法将标识级别的令牌复制回主令牌。第二行会导致异常，因为该操作会破坏SRM的安全保证（具体来说，即SQoS允许调用者控制其身份的使用方式）。

最后一点：如果您使用`Get-NtToken`打开令牌，可以通过指定`Duplicate`参数一步完成复制操作。

### 伪令牌句柄

要访问令牌，您必须打开令牌对象的句柄，并在使用后记得关闭句柄。Windows 10引入了三个*伪句柄*，允许您查询令牌信息而无需打开内核对象的完整句柄。以下是这三个句柄及其句柄值（括号内）：

- **主令牌 (-4)**    当前进程的主令牌
- **模拟令牌 (-5)**    当前线程的模拟令牌；如果线程未进行模拟，则失败
- **有效令牌 (-6)**    当前线程的模拟令牌（如果正在模拟）；否则，为主令牌


与当前进程和当前线程的伪句柄不同，您不能复制这些令牌句柄；它们仅可用于某些有限用途，如查询信息或执行访问检查。如果您指定`Pseudo`参数，`Get-NtToken`命令可以返回这些句柄，如代码清单 4-7所示。


```
PS> Invoke-NtToken -Anonymous {Get-NtToken -Pseudo -Primary | Get-NtTokenSid}
Name                         Sid
----                         ---
GRAPHITE\user                S-1-4-21-2318445812-3516008893-216915059-1002 ❶

PS> Invoke-NtToken -Anonymous {Get-NtToken -Pseudo -Impersonation | Get-NtTokenSid}
Name                         Sid
----                         ---
NT AUTHORITY\ANONYMOUS LOGON S-1-4-7 ❷

PS> Invoke-NtToken -Anonymous {Get-NtToken -Pseudo -Effective | Get-NtTokenSid}
Name                         Sid
----                         ---
NT AUTHORITY\ANONYMOUS LOGON S-1-4-7 ❸

PS> Invoke-NtToken -Anonymous {Get-NtToken -Pseudo -Effective} | Get-NtTokenSid
Name                         Sid
----                         ---
GRAPHITE\user                S-1-4-21-2318445812-3516008893-216915059-1002 ❹
```


*代码清单 4-7：查询伪令牌*

在这里，我们在模拟匿名用户时查询三种类型的伪令牌。第一个命令查询主令牌并提取其用户SID ❶。下一个命令查询模拟令牌，返回匿名用户的SID ❷。然后我们查询有效令牌，由于我们正在模拟匿名用户，它也返回匿名用户的SID ❸。最后，我们再次查询有效令牌，这次等待脚本块执行完毕后再提取用户SID。此操作返回主令牌的用户SID ❹，表明伪令牌是上下文敏感的。

### 令牌中的组（Token Groups）

如果管理员必须针对每一个可能的用户去单独配置每项资源的安全访问控制，权限管理成本将高到无法承受。*组（Groups）*机制允许用户共享一个更宽泛的安全标识身份。Windows 上的大多数访问控制操作，实际上都是将权限授予组而非单个用户。

从 SRM 的视角来看，组本质上就是另一个 SID，用于在访问检查时代定是否允许访问某项资源。我们可以在 PowerShell 控制台中使用 `Get-NtTokenGroup` 命令查看令牌中包含的所有组，如代码清单 4-8所示。


```
PS> Get-NtTokenGroup $token
Name                                     Attributes
----                                     ----------
GRAPHITE\None                            Mandatory, EnabledByDefault, Enabled
Everyone                                 Mandatory, EnabledByDefault, Enabled
BUILTIN\Users                            Mandatory, EnabledByDefault, Enabled
BUILTIN\Performance Log Users            Mandatory, EnabledByDefault, Enabled
NT AUTHORITY\INTERACTIVE                 Mandatory, EnabledByDefault, Enabled
--snip--
```


*代码清单 4-8：查询当前令牌的组*

我们还可以通过指定 `Attributes` 参数，使用 `Get-NtTokenGroup` 来筛选特定的属性标志。表 4-2 显示了可以传递给该命令的可能属性标志。

| SDK 属性名称                | PowerShell 属性名称      |
| :-------------------------- | :----------------------- |
| SE_GROUP_ENABLED            | Enabled                  |
| SE_GROUP_ENABLED_BY_DEFAULT | EnabledByDefault         |
| SE_GROUP_MANDATORY          | Mandatory                |
| SE_GROUP_LOGON_ID           | LogonId                  |
| SE_GROUP_OWNER              | Owner                    |
| SE_GROUP_USE_FOR_DENY_ONLY  | UseForDenyOnly           |
| SE_GROUP_INTEGRITY          | Integrity                |
| SE_GROUP_INTEGRITY_ENABLED  | IntegrityEnabled         |
| SE_GROUP_RESOURCE           | Resource                 |

以下各小节将详细解析这些标志在访问控制与系统安全中所代表的具体含义。

#### Enabled、EnabledByDefault 与 Mandatory 标志

最核心的属性标志是 `Enabled`。设置此标志时，SRM 在执行访问检查期间才会将该组纳入权限判定考量；否则将直接忽略该组。任何带有 `EnabledByDefault` 属性标志的组在令牌创建时都会被自动启用。

只要对令牌句柄拥有 TOKEN_ADJUST_GROUPS（AdjustGroups）访问权限，就可以通过 `NtAdjust0GroupsToken` 系统调用来禁用某个组（使其不参与后续的访问检查）；PowerShell 命令 `Set-NtTokenGroup` 正是封装了该系统调用。不过，你无法禁用标记了 `Mandatory`（强制）标志的组。在普通用户令牌中，所有组默认都会被标记为 `Mandatory`，只有某些特定的系统令牌才包含非强制组。值得注意的是，如果通过 RPC 传递模拟令牌，且在安全服务质量结构（SQoS）中设置了仅有效令牌模式标志（`EffectiveOnly`），那么若某个组处于禁用状态，服务端生成的模拟令牌将会直接剔除该组。

#### LogonId 标志

`LogonId` 标志用于标明令牌中的“登录 SID（Logon SID）”，该 SID 会赋予同一登录会话（桌面环境）下的所有令牌。例如，即使使用 `runas` 工具以另一个用户的身份启动新进程，新进程的令牌虽然属于不同的用户标识，但依然具有与调用者相同的 Logon SID。这一机制使 SRM 能够将访问权限统一授予特定会话范围内的私有资源（例如会话对象目录 `\Sessions\X\BaseNamedObjects`）。Logon SID 采用标准格式 `S-1-5-5-X-Y`（*注：原书此处误印为 S-1-4-4-X-Y*），其中 X 和 Y 分别对应创建该身份验证登录会话时所分配 LUID 的两个 32 位数值。我们将在下一章详细分析 Logon SID 的实际应用场景。

#### Owner 标志

系统中的所有安全对象（Securable Objects），其所有权（Ownership）最终都必须归属于某个用户 SID 或组 SID。访问令牌包含一个 `Owner` 属性，该属性指定了当前主体在创建新资源时默认赋给对象的拥有者 SID。为防止冒充假冒所有权，SRM 严格限制了哪些 SID 可以作为令牌的 `Owner` 属性：只能是当前令牌的主体用户 SID 本身，或者是令牌组列表中明确打上了 `Owner` 标志的组 SID（例如 Administrators 组）。

你可以使用 `Get-NtTokenSid` 或 `Set-NtTokenSid` 命令来查询或修改令牌当前的 `Owner` 属性。例如在代码清单 4-9中，我们先从当前令牌获取所有者 SID，然后尝试设置一个新的所有者：




```
PS> Get-NtTokenSid $token -Owner
Name          Sid
----          ---
GRAPHITE\user S-1-4-21-818064984-378290696-2985406761-1002

PS> Set-NtTokenSid -Owner -Sid "S-1-2-3-4"
Exception setting "Owner": "(0xC000005A) - Indicates a particular
Security ID may not be assigned as the owner of an object."
```


*代码清单 4-9：获取和设置令牌的所有者 SID*

在此测试中，我们将 `Owner` 属性修改为任意 SID `S-1-2-3-4` 时触发异常失败，因为该 SID 既不是当前令牌的用户 SID，也不属于标记有 Owner 属性的组。

#### UseForDenyOnly 标志

在 SRM 执行访问检查时，针对某个 SID 的访问控制项（ACE）要么是允许访问，要么是拒绝访问。但当某个 SID 被禁用时，它将完全不再参与允许或拒绝的判定——这会导致安全访问判定失真，甚至引发越权漏洞。

我们来看一个具体的例子：假设系统中有两个组——*Employee*（员工）和 *Remote Access*（远程访问）。某用户创建了一份敏感情报文档，希望所有员工都能阅读，但必须排除远程登录系统的员工以防数据泄露。因此，该文档的安全配置为：向 *Employee* 组的所有成员授予允许访问权限，但对 *Remote Access* 组的所有成员显式配置拒绝访问权限。

此时假设如果允许同时属于这两个组的用户在访问资源时自行禁用某个组，该用户便可以在发起访问时直接禁用 *Remote Access* 组。这样一来，系统便只会依据其 *Employee* 组的成员身份放行访问，轻而易举地绕过了拒绝远程访问的安全限制。

正因如此，系统极少允许普通用户随意禁用其名下的组。然而在某些场景下（例如沙箱化隔离运行不可信代码时），我们确实需要降权并“剥夺”某个组，防止代码借由该组的高权限去访问敏感资源。`UseForDenyOnly` 标志正是为了化解这一两难而设计的：当某个组 SID 被标记为 `UseForDenyOnly` 时，SRM 在匹配**允许访问（Access Allowed）**时会完全忽略该组；但在匹配**拒绝访问（Access Denied）**时，该组依然有效并参与检查。用户可以通过对自身令牌执行过滤（Token Filtering）操作，将某些高权组降格标记为 `UseForDenyOnly`，并使用过滤后的降权令牌启动新进程。我们将在本章稍后的“沙箱令牌”一节讨论受限令牌时，详细探讨令牌过滤机制。

#### Integrity 与 IntegrityEnabled 标志（完整性级别）

`Integrity` 和 `IntegrityEnabled` 属性标志表明该 SID 代表令牌当前的强制完整性级别（Integrity Level, IL），且该级别已处于启用生效状态。标记有 `Integrity` 属性的组 SID 将完整性级别作为 32 位无符号整数保存在其最后一个 RID（相对标识符）中。理论上 RID 可以是任意数值，但 Windows SDK 中预定义了 7 个标准级别，如表 4-3所示。其中只有前 6 个级别常见且允许从普通用户进程访问（第 7 个级别 ProtectedProcess 专属于受保护进程）。为了明确表示这是一个完整性级别的 SID，SRM 使用了专用的标识符颁发机构标识 `SECURITY_MANDATORY_LABEL_AUTHORITY`（其 Authority 编号值为 16，因此格式形如 `S-1-16-XXXX`）。

| 完整性级别 | SDK名称                                 | PowerShell名称  |
| :--------- | :-------------------------------------- | :-------------- |
| 0          | SECURITY_MANDATORY_UNTRUSTED_RID        | Untrusted       |
| 4096       | SECURITY_MANDATORY_LOW_RID              | Low             |
| 8192       | SECURITY_MANDATORY_MEDIUM_RID           | Medium          |
| 8448       | SECURITY_MANDATORY_MEDIUM_PLUS_RID      | MediumPlus      |
| 12288      | SECURITY_MANDATORY_HIGH_RID             | High            |
| 16384      | SECURITY_MANDATORY_SYSTEM_RID           | System          |
| 20480      | SECURITY_MANDATORY_PROTECTED_PROCESS_RID| ProtectedProcess|

标准普通用户的默认完整性级别为 Medium（中，8192）。管理员通常分配 High（高，12288），系统服务则分配 System（系统，16384）。我们可以使用 `Get-NtTokenSid` 查询令牌当前的完整性 SID，如代码清单 4-10所示。

```
PS> Get-NtTokenSid $token -Integrity
Name                                   Sid
----                                   ---
Mandatory Label\Medium Mandatory Level S-1-16-8192
```

*代码清单 4-10：获取令牌的完整性级别SID*

我们还可以设置新的令牌完整性级别，前提是它小于或等于当前值。也可以提高级别，但这需要特殊特权并启用`SeTcbPrivilege`。

虽然您可以设置整个SID，但通常更方便的是仅设置值。例如，代码清单 4-11中的脚本会将令牌的完整性级别设置为Low。

```
PS> Set-NtTokenIntegrityLevel Low -Token $token
PS> Get-NtTokenSid $token -Integrity
Name                                   Sid
----                                   ---
Mandatory Label\Low Mandatory Level    S-1-16-4096
```

*代码清单 4-11：将令牌完整性级别设置为Low*

如果运行此脚本，您可能会发现PowerShell控制台开始出现因文件访问被阻止而产生的错误。我们将在第7章讨论强制完整性控制时，解释为何文件访问会被阻止。

#### Resource 标志

最后一个属性标志仅需简要提及：`Resource` 属性标志表示组 SID 是*域本地组 SID（Domain Local SID）*。我们将在第10章中回到此 SID 类型。

#### 设备组（Device Groups）

令牌还可以有单独的*设备组*列表。当用户在企业环境中通过网络向服务器进行身份验证时，会添加这些组 SID，如代码清单 4-12所示。

```
PS> Get-NtTokenGroup -Device -Token $token
Name                                 Attributes
----                                 ----------
BUILTIN\Users                        Mandatory, EnabledByDefault, Enabled
AD\CLIENT1$                          Mandatory, EnabledByDefault, Enabled
AD\Domain Computers                  Mandatory, EnabledByDefault, Enabled
NT AUTHORITY\Claims Value            Mandatory, EnabledByDefault, Enabled
--snip--
```

*代码清单 4-12：使用Get-NtTokenGroup显示设备组*

您可以使用`Get-NtTokenGroup`并传递`Device`参数来查询令牌上的组。

### 特权

组允许系统管理员控制用户对特定资源的访问。相比之下，*特权* 授予用户是为了让他们能够绕过对所有类型资源的安全检查，例如通过绕过访问检查。特权也可以应用于某些特权操作，比如更改系统时钟。你可以使用 `Get-NtTokenPrivilege` 在控制台中查看令牌的特权（代码清单 4-13）。

```
PS> Get-NtTokenPrivilege $token
Name                           Luid                 Enabled
----                           ----                 -------
SeShutdownPrivilege            00000000-00000013    False
SeChangeNotifyPrivilege        00000000-00000017    True
SeUndockPrivilege              00000000-00000019    False
SeIncreaseWorkingSetPrivilege  00000000-00000021    False
SeTimeZonePrivilege            00000000-00000022    False
```

*代码清单 4-13：列出令牌特权*

输出分为三列。第一列是特权的通用名称。与 SID 一样，SRM 并不直接使用此名称；而是使用特权的 LUID 值，我们可以在第二列中看到。最后一列指示特权当前是否已启用。特权可以处于启用或禁用状态。

任何特权检查都应确保特权已启用，而不仅仅是存在。在某些情况下，例如沙箱环境中，令牌可能列出了某个特权，但沙箱限制可能阻止其被标记为已启用。`Enabled` 标志实际上是一组属性标志，类似于组 SID 的属性。我们可以通过将 `Get-NtTokenPrivilege` 的输出格式化为列表来查看这些属性（代码清单 4-14）。

```
PS> Get-NtTokenPrivilege $token -Privileges SeChangeNotifyPrivilege | Format-List
Name        : SeChangeNotifyPrivilege
Luid        : 00000000-00000017
Attributes  : EnabledByDefault, Enabled
Enabled     : True
DisplayName : Bypass traverse checking
```

*代码清单 4-14：显示 SeChangeNotifyPrivilege 特权的所有属性*

在输出中，我们现在可以看到属性，包括 `Enabled` 和 `EnabledByDefault`。`EnabledByDefault` 属性指定特权的默认状态是否为启用。我们还看到了一个额外的 `DisplayName` 属性，用于向用户提供附加信息。

要修改令牌特权的状态，你需要在令牌句柄上拥有 `AdjustPrivileges` 访问权限；然后可以使用 `NtAdjustPrivilegesToken` 系统调用来调整属性并启用或禁用特权。`Enable-NtTokenPrivilege` 和 `Disable-NtTokenPrivilege` PowerShell 命令封装了此系统调用，如 代码清单 4-15 所示。

```
PS> Enable-NtTokenPrivilege SeTimeZonePrivilege -Token $token -PassThru
Name                           Luid                 Enabled
----                           ----                 -------
SeTimeZonePrivilege            00000000-00000022    True

PS> Disable-NtTokenPrivilege SeTimeZonePrivilege -Token $token -PassThru
Name                           Luid                 Enabled
----                           ----                 -------
SeTimeZonePrivilege            00000000-00000022    False
```

*代码清单 4-15：启用和禁用 SeTimeZonePrivilege 特权*

使用 `NtAdjustPrivilegesToken` API，还可以通过指定 `Remove` 属性来完全移除特权，这可以通过 `Remove-NtTokenPrivilege` PowerShell 命令完成。移除特权确保令牌永远无法再使用它。如果仅禁用特权，则可能会被意外重新启用。代码清单 4-16 展示了如何移除特权。

```
PS> Get-NtTokenPrivilege $token -Privileges SeTimeZonePrivilege
Name                           Luid                 Enabled
----                           ----                 -------
SeTimeZonePrivilege            00000000-00000022    False

PS> Remove-NtTokenPrivilege SeTimeZonePrivilege -Token $token
PS> Get-NtTokenPrivilege $token -Privileges SeTimeZonePrivilege
WARNING: Couldn't get privilege SeTimeZonePrivilege
```

*代码清单 4-16：从令牌中移除特权*

要检查特权，用户应用程序可以调用 `NtPrivilegeCheck` 系统调用，而内核代码可以调用 `SePrivilegeCheck` API。你可能想知道是否可以手动测试特权是否已启用，而不是使用专用的系统调用。在这种情况下，可以；然而，尽可能使用系统设施总是值得的，以防在实现中出错或未考虑到某些边缘情况。`Test-NtTokenPrivilege` PowerShell 命令封装了该系统调用，如 代码清单 4-17 所示。

```
PS> Enable-NtTokenPrivilege SeChangeNotifyPrivilege
PS> Disable-NtTokenPrivilege SeTimeZonePrivilege
PS> Test-NtTokenPrivilege SeChangeNotifyPrivilege
True

PS> Test-NtTokenPrivilege SeTimeZonePrivilege, SeChangeNotifyPrivilege -All
False

PS> Test-NtTokenPrivilege SeTimeZonePrivilege, SeChangeNotifyPrivilege
-All -PassResult
EnabledPrivileges           AllPrivilegesHeld
-----------------           -----------------
{SeChangeNotifyPrivilege}   False
```

*代码清单 4-17：执行特权检查*

此清单演示了使用 `Test-NtTokenPrivilege` 进行的一些示例特权检查。我们首先启用 `SeChangeNotifyPrivilege` 并禁用 `SeTimeZonePrivilege`。这些是所有用户通常都拥有的特权，但如果你的令牌没有这些特权，你可能需要更改示例。然后我们仅测试 `SeChangeNotifyPrivilege`；它已启用，因此此测试返回 `True`。接下来，我们检查 `SeTimeZonePrivilege` 和 `SeChangeNotifyPrivilege`；我们可以看到并非所有特权都具备，因此 `Test-NtTokenPrivilege` 返回 `False`。最后，我们运行相同的命令，但指定 `-PassResult` 选项以返回完整的检查结果。在 `EnabledPrivileges` 列中，我们可以看到只有 `SeChangeNotifyPrivilege` 已启用。

以下是系统上可用的一些特权：

SeChangeNotifyPrivilege  此特权的名称具有误导性。它允许用户接收文件系统或注册表更改的通知，但也用于绕过遍历检查。我们将在第 8 章中讨论遍历检查。

SeAssignPrimaryTokenPrivilege 和 SeImpersonatePrivilege  这些特权分别允许用户绕过分配主令牌和模拟检查。与本列表中的大多数特权不同，这些特权必须在当前进程的主令牌上启用，而不是在模拟令牌上启用。

SeBackupPrivilege 和 SeRestorePrivilege  这些特权允许用户在打开特定资源（如文件或注册表键）时绕过访问检查。这使得用户无需被显式授予访问权限即可备份和恢复资源。这些特权也被重新用于其他用途：例如，恢复特权允许用户加载任意的注册表配置单元。

SeSecurityPrivilege 和 SeAuditPrivilege  这两个特权中的第一个允许用户获得对资源的 AccessSystemSecurity 访问权限。这允许用户修改资源的审计配置。SeAuditPrivilege 特权允许用户从用户应用程序生成任意的对象审计消息。我们将在第5章、第6章和第9章中讨论审计。

SeCreateTokenPrivilege  此特权应仅授予非常有限的用户群体，因为它授予使用 NtCreateToken 系统调用制作任意令牌的能力。

SeDebugPrivilege  此特权的名称暗示它是调试进程所必需的。然而，事实并非如此，因为没有它也可以调试进程。该特权确实允许用户在打开进程或线程对象时绕过任何访问检查。

SeTcbPrivilege  此特权的名称来源于*可信计算基（TCB）*，这是一个用于指代 Windows 操作系统特权核心（包括内核）的术语。这是一个包罗万象的特权，用于涵盖没有更具体特权覆盖的特权操作。例如，它允许用户绕过提升令牌完整性级别（最高至系统级别）的检查，但也允许为进程指定回退异常处理器，这两个操作几乎没有共同之处。

SeLoadDriverPrivilege  我们可以通过 NtLoadDriver 系统调用加载新的内核驱动程序，尽管更常见的是使用 SCM。此特权是成功执行该系统调用所必需的。请注意，拥有此特权并不能让你绕过内核驱动程序检查，如代码签名。

SeTakeOwnershipPrivilege 和 SeRelabelPrivilege  这两个特权具有相同的直接效果：它们允许用户获得对资源的 WriteOwner 访问权限，即使正常的访问控制不允许这样做。SeTakeOwnershipPrivilege 允许用户取得资源的所有权，因为拥有 WriteOwner 权限是实现该目的所必需的。SeRelabelPrivilege 绕过对资源强制标签的检查；通常，你只能将标签设置为等于或低于调用者的完整性级别。设置强制标签还需要对句柄具有 WriteOwner 访问权限，我们将在第6章中看到。

我们将在后续章节讨论安全描述符(Security Descriptor)和访问检查时，查看这些特权使用的具体示例。现在，让我们转向通过沙箱限制访问的方法。

### 沙盒令牌

在我们互联互通的世界中，必须处理大量不可信的数据。攻击者可能出于恶意目的构造数据，例如利用网页浏览器或文档阅读器中的安全漏洞。为了应对这一威胁，Windows 提供了一种方法，通过将处理不可信数据的进程放入沙盒中，来限制用户可访问的资源。如果进程被攻破，攻击者将只能看到系统的有限视图，无法访问用户的敏感信息。Windows 通过三种特殊的令牌类型实现沙盒：受限令牌、写受限令牌和lowbox令牌。

#### 受限令牌

**受限令牌（restricted token）** 是 Windows 中历史最久的沙盒令牌。它作为一项功能在 Windows 2000 中被引入，但直到谷歌 Chrome 浏览器问世之后，才被广泛用作沙盒机制。此后 Firefox 等其他浏览器，以及 Adobe Reader 这类文档阅读器，都复刻了 Chrome 的这套沙盒实现方案。

你可以通过 `NtFilterToken` 系统调用，或是 Win32 API `CreateRestrictedToken` 创建受限令牌。二者都允许指定一组**受限 SID**，以此限制该令牌能够访问的资源。这些 SID 不必预先存在于令牌之中。例如：Chrome 限制等级最高的沙盒，仅指定**NULL SID（S-1-0-0）**作为唯一受限 SID；NULL SID 本身不会作为普通组，被授予任何令牌。

任何访问检查都必须同时允许正常组列表和受限SID列表；否则，系统将拒绝用户访问，我们将在第7章中详细讨论。`NtFilterToken` 系统调用还可以将正常组标记为 `UseForDenyOnly` 属性标志，并删除特权。我们可以将过滤令牌的能力与受限SID结合使用，或单独使用，以创建权限较低的令牌，而无需更全面的沙盒化。

构建一个无法访问任何资源的受限令牌很容易。这种限制能产生良好的沙盒效果，但也使得该令牌无法作为进程的主令牌使用，因为进程将无法启动。这对受限令牌沙盒的有效性构成了严重限制。代码清单 4-18演示了如何创建受限令牌并提取结果。

```
PS> $token = Get-NtToken -Filtered -RestrictedSids RC -SidsToDisable WD
-Flags DisableMaxPrivileges
PS> Get-NtTokenGroup $token -Attributes UseForDenyOnly
Name                           Attributes
----                           ----------
Everyone                       UseForDenyOnly

PS> Get-NtTokenGroup $token -Restricted
Name                           Attributes
----                           ----------
NT AUTHORITY\RESTRICTED        Mandatory, EnabledByDefault, Enabled

PS> Get-NtTokenPrivilege $token
Name                           Luid                 Enabled
----                           ----                 -------
SeChangeNotifyPrivilege        00000000-00000017    True

PS> $token.Restricted
True
```

*代码清单 4-18：创建受限令牌并显示组和特权*

我们首先使用 `Get-NtToken` 命令创建一个受限令牌。我们指定一个受限SID，即 `RC`，它映射到一个特殊的 `NT AUTHORITY\RESTRICTED` SID，通常配置为允许系统资源的读取访问。我们还指定要将 *Everyone* 组（WD）转换为 `UseForDenyOnly`。最后，我们指定一个标志以禁用最大数量的特权。

接下来，我们显示令牌的属性，从所有正常组开始，使用 `UseForDenyOnly` 属性。输出显示只有 *Everyone* 组设置了该标志。然后我们显示受限SID列表，其中显示了 `NT AUTHORITY\RESTRICTED` SID。

之后，我们显示特权。请注意，即使我们要求禁用最大特权，`SeChangeNotifyPrivilege` 仍然存在。该特权不会被删除，因为没有它，访问资源可能会变得非常困难。如果你确实想移除它，可以显式地将其指定给 `NtFilterToken`，或在令牌创建后将其删除。

最后，我们查询令牌属性，以指示它是否为受限令牌。

INTERNET EXPLORER 保护模式

Windows上第一个沙盒化的网页浏览器是Internet Explorer 7，随Windows Vista引入。Internet Explorer 7利用降低进程令牌完整性级别的方法，来限制浏览器可写入的资源。Windows 8最终用新型令牌——lowbox令牌（我们将在本章稍后的“AppContainer 与 LowBox 令牌”一节中讨论）取代了这种简单的沙盒（称为保护模式）。lowbox令牌提供了更强的隔离性（称为增强保护模式）。有趣的是，尽管受限令牌自Windows 2000起就已可用，但微软并未使用它们。

#### 写受限令牌

*写受限令牌* 阻止对资源的写入访问，但允许读取和执行访问。你可以通过向 `NtFilterToken` 传递 `WRITE_RESTRICTED` 标志来创建写受限令牌。

Windows XP SP2 引入了这种令牌类型以强化系统服务。与受限令牌相比，将其用作沙箱要容易得多，因为您无需担心令牌无法读取关键资源（如DLL）。然而，它创建的沙箱功能较弱。例如，如果您能读取某个用户的文件，您可能无需逃逸沙箱就能窃取其私人信息，如网页浏览器存储的密码。

为了完整性，让我们创建一个写受限令牌并查看其属性（代码清单 4-19）。




```
PS> $token = Get-NtToken -Filtered -RestrictedSids WR -Flags WriteRestricted
PS> Get-NtTokenGroup $token -Restricted
Name                           Attributes
----                           ----------
NT AUTHORITY\WRITE RESTRICTED  Mandatory, EnabledByDefault, Enabled

PS> $token.Restricted
True

PS> $token.WriteRestricted
True
```


*代码清单 4-19：创建写受限令牌*

我们首先使用 `Get-NtToken` 命令创建令牌。我们指定一个受限SID，即WR，它映射到一个特殊的 `NT AUTHORITY\WRITE RESTRICTED` SID，该SID等同于 `NT AUTHORITY\RESTRICTED`，但被分配用于对特定系统资源的写访问。我们还指定了 `WriteRestricted` 标志，以使其成为写受限令牌而非普通受限令牌。

接下来，我们显示令牌的属性。在受限SID列表中，我们看到 `NT AUTHORITY\WRITE RESTRICTED`。显示 `Restricted` 属性表明该令牌被视为受限；然而，我们也可以看到它被标记为 `WriteRestricted`。

#### AppContainer和Lowbox令牌

Windows 8引入了AppContainer沙箱以保护新的Windows应用模型。AppContainer使用*lowbox令牌*来实现其安全性。您可以通过 `NtCreateLowBoxToken` 系统调用从现有令牌创建lowbox令牌。该系统调用没有直接对应的Win32 API，但您可以使用 `CreateProcess` API创建AppContainer进程。我们在此不详细讨论如何使用该API创建进程；而是仅关注lowbox令牌。

创建lowbox令牌时，您需要指定一个包SID和一个能力SID列表。这两种SID类型都由*应用程序包机构*（其值为15）颁发。您可以通过检查它们的第一个RID来区分包SID和能力SID，它们应分别为2和3。包SID的作用类似于普通令牌中的用户SID，而能力SID则类似于受限SID。我们将在第7章中详细讨论它们如何影响访问检查。

能力SID会修改访问检查过程，但它们也可以单独表示某些含义。例如，有些能力允许网络访问，这些由Windows防火墙特殊处理，尽管这与访问检查并不直接相关。能力SID有两种类型：

**旧版**    Windows 8中引入的一小组预定义SID

**命名**    RID从文本名称派生而来

附录B包含更全面的命名能力SID列表。表4-4显示了旧版能力。

| 能力名称                                                     | SID           |
| :----------------------------------------------------------- | :------------ |
| 您的互联网连接                                               | S-1-15-3-1    |
| 您的互联网连接，包括来自互联网的传入连接                     | S-1-15-3-2    |
| 您的家庭或工作网络                                           | S-1-15-3-3    |
| 您的图片库                                                   | S-1-15-3-4    |
| 您的视频库                                                   | S-1-15-3-5    |
| 您的音乐库                                                   | S-1-15-3-6    |
| 您的文档库                                                   | S-1-15-3-7    |
| 您的Windows凭据                                              | S-1-15-3-8    |
| 软件和硬件证书或智能卡                                       | S-1-15-3-9    |
| 可移动存储                                                   | S-1-15-3-10   |
| 您的约会                                                     | S-1-15-3-11   |
| 您的联系人                                                   | S-1-15-3-12   |
| Internet Explorer                                            | S-1-15-3-4096 |

我们可以使用 `Get-NtSid` 查询包和能力SID，如代码清单 4-20所示。




```
PS> Get-NtSid -PackageName 'my_package' -ToSddl
❶ S-1-15-2-4047469452-4024960472-3786564613-914846661-3775852572-3870680127
-2256146868

❷ PS> Get-NtSid -PackageName 'my_package' -RestrictedPackageName "CHILD" -ToSddl
S-1-15-2-4047469452-4024960472-3786564613-914846661-3775852572-3870680127 -2256146868-951732652-158068026-753518596-3921317197

❸ PS> Get-NtSid -KnownSid CapabilityInternetClient -ToSddl
S-1-15-3-1

❹ PS> Get-NtSid -CapabilityName registryRead -ToSddl
S-1-15-3-1024-1065365936-1281604716-3511738428-1654721687-432734479 -3232135806-4053264122-3456934681

❺ PS> Get-NtSid -CapabilityName registryRead -CapabilityGroup  -ToSddl
S-1-5-32-1065365936-1281604716-3511738428-1654721687-432734479-3232135806 -4053264122-3456934681
```


*代码清单 4-20：创建包和能力SID*

在这里，我们创建两个包SID和两个能力SID。我们通过向`Get-NtSid`指定其名称来生成第一个包SID，并接收生成的SID ❶。该包SID来源于名称的小写形式，并使用SHA256摘要算法进行哈希处理。256位摘要被分割成七个32位块，这些块充当RID。摘要的最后32位值被丢弃。

Windows还支持受限包SID，其设计目的是允许包创建新的安全子包，这些子包之间无法相互交互。经典的Edge浏览器使用此功能来隔离面向互联网和内网的子包，这样如果其中一个被攻破，就无法访问另一个中的数据。要创建子包，我们使用原始包族名称加上子标识符 ❷。生成的SID在原始包SID的基础上扩展了四个RID，如输出所示。

第一个能力SID ❸是用于互联网访问的旧式能力。请注意，生成的SDDL SID多了一个RID值（1）。第二个SID来源于名称，在此例中为`registryRead` ❹，用于允许对一组系统注册表键进行读取访问。与包SID一样，命名能力RID是通过对名称小写形式进行SHA256哈希生成的。为了区分旧式能力SID和命名能力SID，第二个RID设置为1024，后跟SHA256哈希。您可以使用此方法生成自己的能力SID，尽管除非某些资源配置为使用该能力，否则您无法对其执行太多操作。

Windows还支持*能力组*，这是一种组SID，可以添加到正常的组列表中 ❺。能力组将第一个RID设置为32，其余RID设置为从能力名称派生的相同SHA256哈希。

既然我们已经获得了SID，就可以创建一个lowbox令牌，如代码清单 4-21所示。




```
❶ PS> $token = Get-NtToken -LowBox -PackageSid 'my_package'
-CapabilitySid "registryRead", "S-1-15-3-1"
❷ PS> Get-NtTokenGroup $token -Capabilities | Select-Object Name
Name
----
NAMED CAPABILITIES\Registry Read
APPLICATION PACKAGE AUTHORITY\Your Internet connection

❸ PS> $package_sid = Get-NtTokenSid $token -Package -ToSddl
PS> $package_sid
S-1-15-2-4047469452-4024960472-3786564613-914846661-3775852572-3870680127 -2256146868

PS> Get-NtTokenIntegrityLevel $token
❹ Low

PS> $token.Close()
```


*代码清单 4-21：创建lowbox令牌并列出其属性*

首先，我们调用`Get-NtToken`，传入包名称（SID的SDDL形式也可以）以及要分配给lowbox令牌的能力列表 ❶。然后我们可以查询能力列表 ❷。请注意，两个能力SID的名称不同：从名称派生的SID带有`NAMED CAPABILITIES`前缀。无法将命名能力SID转换回其派生的名称；PowerShell模块必须基于大量已知能力列表生成名称。第二个SID是旧式SID，因此LSASS可以将其解析回名称。

接下来，我们查询包SID ❸。由于包SID是通过SHA256从名称派生的，因此无法将其解析回包名称。同样，PowerShell模块有一个名称列表，可以用来推断原始名称。

lowbox令牌始终设置为低完整性级别 ❹。实际上，如果特权用户将完整性级别更改为中或更高，所有lowbox属性（如包SID和能力SID）都会被移除，令牌将恢复为非沙盒令牌。

我们已经介绍了如何通过将用户的令牌转换为沙盒令牌来降低其权限。现在我们将转向另一方面，探讨是什么让用户拥有足够权限来管理Windows系统。

### 什么是管理员用户？

如果你有Unix背景，你会知道用户ID 0是管理员账户，即*root*。作为root，你可以访问任何资源，并按需配置系统。当你安装Windows时，配置的第一个账户也是管理员。然而，与root不同，该账户没有系统特殊对待的SID。那么，Windows上是什么让一个账户成为管理员呢？

基本答案是，Windows被配置为赋予某些组和特权特殊访问权限。管理员访问本质上是自主决定的，这意味着可能是管理员但仍被锁定在资源之外；没有真正的root账户等价物（尽管*SYSTEM*用户很接近）。

管理员通常具有三个特征。首先，当你将用户配置为管理员时，通常会将他们添加到*BUILTIN\Administrators*组，然后配置Windows在执行访问检查时允许该组访问。例如，系统文件夹（如*C:\Windows*）被配置为允许该组创建新文件和目录。

其次，管理员获得额外的特权，这实际上绕过了系统的安全控制。例如，SeDebugPrivilege允许用户完全访问系统上的任何其他进程或线程，无论其被分配了什么安全设置。通过完全访问进程，可以向其中注入代码以获取不同用户的特权。

第三，管理员通常以高完整性级别运行，而系统服务以系统级别运行。通过提高管理员的完整性级别，我们更难意外地将管理员资源（尤其是进程和线程）暴露给非管理员。对资源的弱访问控制是常见的错误配置；然而，如果资源也被标记为高于中等的完整性级别，那么非管理员用户将无法写入该资源。

快速验证令牌是否为管理员的方法是检查Token对象上的Elevated属性。此属性指示令牌是否具有内核中固定列表中发现的某些组和可用特权。代码清单 4-22显示了一个非管理员的示例。


```
PS> $token = Get-NtToken
PS> $token.Elevated
False
```


*代码清单 4-22：非管理员的Elevated属性*

如果令牌具有以下特权之一，则自动被视为提升：

- SeCreateTokenPrivilege
- SeTcbPrivilege
- SeTakeOwnershipPrivilege
- SeLoadDriverPrivilege
- SeBackupPrivilege
- SeRestorePrivilege
- SeDebugPrivilege
- SeImpersonatePrivilege
- SeRelabelPrivilege
- SeDelegateSessionUserImpersonatePrivilege

特权不必启用，只需在令牌中可用即可。

对于提升的组，内核没有固定的SID列表；相反，它只检查SID的最后一个RID。如果RID设置为以下值之一，则该SID被视为提升：114、498、512、516、517、518、519、520、521、544、547、548、549、550、551、553、554、556或569。例如，*BUILTIN\Administrators*组的SID是S-1-4-32-544。由于544在此列表中，该SID被视为提升。（注意，SID S-1-1-2-3-4-544也会被视为提升，即使它没有什么特别之处。）

高完整性级别不等于管理员

一个常见的误解是，如果令牌具有高完整性级别，它就是管理员令牌。然而，Elevated属性不检查令牌的完整性级别，只检查其特权和组。BUILTIN\Administrators组在较低的完整性级别下仍能正常工作，允许访问诸如Windows文件系统目录等资源。唯一的限制是，某些高级特权（如SeDebugPrivilege）在完整性级别低于高时无法启用。

非管理员也可以以高完整性级别运行，例如UI访问进程，有时以该完整性级别运行，但未获得任何特殊特权或组来使其成为管理员。

### 用户账户控制

我之前提到过，当你全新安装Windows时，创建的第一个用户总是管理员。这样配置用户至关重要；否则，将无法修改系统或安装新软件。

然而，在Windows Vista之前，这种默认行为是一个巨大的安全漏洞，因为普通消费者会安装默认账户，并且很可能永远不会更改它。这意味着大多数人使用完全管理员账户进行日常活动，如浏览网页。如果恶意攻击者能够利用用户浏览器中的安全漏洞，攻击者将获得对Windows机器的完全控制。在沙箱技术普及之前，这种威胁被证明是严重的。

在Vista中，微软通过引入*用户账户控制（UAC）*和拆分管理员令牌改变了这种默认行为。在这种模型中，默认用户仍然是管理员；然而，默认情况下，所有程序都使用一个移除了管理员组和特权的令牌运行。当用户需要执行管理任务时，系统会将进程提升为完全管理员，并显示一个提示，如图4-3所示，请求用户确认后再继续。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure4-3.webp)

图4-3：UAC权限提升的同意对话框

为了让用户更容易使用Windows，你可以配置程序在启动时强制提升。程序的提升属性存储在执行映像中嵌入的清单XML文件中。运行代码清单 4-23中的示例，获取*System32*目录中所有可执行文件的清单信息。


```
PS> ls C:\Windows\System32\*.exe | Get-Win32ModuleManifest
Name                           UiAccess   AutoElevate     ExecutionLevel
----                           --------   -----------     --------------
aitstatic.exe                  False      False           asInvoker
alg.exe                        False      False           asInvoker
appidcertstorecheck.exe        False      False           asInvoker
appidpolicyconverter.exe       False      False           asInvoker
ApplicationFrameHost.exe       False      False           asInvoker
appverif.exe                   False      False           highestAvailable
--snip--
```


*代码清单 4-23：查询可执行文件清单信息*

如果是特殊的、微软批准的程序，清单可以指定程序是否应自动且静默提升（在AutoElevate列中以True值表示）。清单还指示进程是否可以以UI访问权限运行，我们将在本章稍后的“UIAccess 应用程序”一节讨论这个主题。ExecutionLevel列有三个可能的值：

asInvoker  以创建进程的用户身份运行进程。这是默认设置。

highestAvailable  如果用户是拆分令牌管理员，则强制提升到管理员令牌。如果不是，则以创建进程的用户身份运行。

requireAdministrator  无论用户是否为拆分令牌管理员，都强制提升。如果用户不是管理员，系统将提示输入管理员账户的密码。

当某个程序以提升的执行级别被创建时，shell会调用RPC方法RAiLaunchAdminProcess。此方法检查清单并启动提升过程，包括显示同意对话框。也可以使用ShellExecute API（在第 3 章“Shell API”一节中介绍）手动提升任何应用程序，并请求runas操作。PowerShell通过Start-Process命令暴露此行为，如下所示：


```
PS> Start-Process notepad -Verb runas
```


运行此命令时，你应该会看到UAC提示。如果在同意对话框中点击“是”，*notepad.exe*应以管理员身份在桌面上运行。

#### 链接令牌与提升类型

当管理员在桌面上进行身份验证时，系统会跟踪该用户的两个令牌：

**受限**    用于大多数运行进程的未提升令牌

**完全**    完全管理员令牌，仅在提升后使用

*拆分令牌管理员*这一名称来源于这两个令牌，因为用户获得的访问权限被分割在受限和完全令牌之间。

令牌对象有一个字段用于将两个令牌链接在一起。可以使用NtQueryInformationToken系统调用和TokenLinkedToken信息类查询链接令牌。在代码清单 4-24中，我们使用PowerShell检查这些链接令牌的一些属性。


```
❶ PS> Use-NtObject($token = Get-NtToken -Linked) {
    Format-NtToken $token -Group -Privilege -Integrity -Information
}
GROUP SID INFORMATION
-----------------
Name                          Attributes
----                          ----------
❷ BUILTIN\Administrators        Mandatory, EnabledByDefault, Enabled, Owner
--snip--

PRIVILEGE INFORMATION
---------------------
Name                          Luid              Enabled
----                          ----              -------
SeIncreaseQuotaPrivilege      00000000-00000005 False
❸ SeSecurityPrivilege           00000000-00000008 False
SeTakeOwnershipPrivilege      00000000-00000009 False
--snip--

INTEGRITY LEVEL
---------------
❹ High

TOKEN INFORMATION
-----------------
❺ Type          : Impersonation
Imp Level     : Identification
Auth ID       : 00000000-0009361F
❻ Elevated      : True
❼ Elevation Type: Full
Flags         : NotLow
```

*代码清单 4-24：显示链接令牌的属性*

我们通过向Get-NtToken传递Linked参数来访问链接令牌，❶ 并格式化令牌以显示其组、特权、完整性级别和令牌信息。在组列表中，我们可以看到*BUILTIN\Administrators*组已启用 ❷。我们还可以看到特权列表包含一些高级特权，如SeSecurityPrivilege ❸。组和特权的组合确认这是一个管理员令牌。

令牌的完整性级别设置为高 ❹，正如我们之前讨论的，这可以防止令牌意外地将敏感资源暴露给非管理员用户。在令牌信息中，我们可以看到存在一个标识级别的模拟令牌 ❺。要获得能够创建新进程的令牌，调用者需要拥有 `SeTcbPrivilege` 特权，这意味着只有系统服务（如应用程序信息服务）才能获取该令牌。最后，我们可以看到该令牌被标记为已提升 ❻，并且令牌提升类型表明这是完整令牌 ❼。让我们将其与受限令牌进行比较（代码清单 4-25）。

```
❶ PS> Use-NtObject($token = Get-NtToken) {
    Format-NtToken $token -Group -Privilege -Integrity -Information
}
GROUP SID INFORMATION
-----------------
Name                          Attributes
----                          ----------
❷ BUILTIN\Administrators        UseForDenyOnly
--snip--

PRIVILEGE INFORMATION
---------------------
Name                          Luid              Enabled
----                          ----              -------
❸ SeShutdownPrivilege           00000000-00000013 False
SeChangeNotifyPrivilege       00000000-00000017 True
SeUndockPrivilege             00000000-00000019 False
SeIncreaseWorkingSetPrivilege 00000000-00000021 False
SeTimeZonePrivilege           00000000-00000022 False

INTEGRITY LEVEL
---------------
❹ Medium

TOKEN INFORMATION
-----------------
Type          : Primary
Auth ID       : 00000000-0009369B
❺ Elevated      : False
❻ Elevation Type: Limited
❼ Flags         : VirtualizeAllowed, IsFiltered, NotLow
```

*代码清单 4-25：显示受限令牌的属性*

我们首先获取当前令牌的句柄，并使用与代码清单 4-24 中相同的格式对其进行格式化 ❶。在组列表中，我们可以看到 *BUILTIN\Administrators* 已被转换为 UseForDenyOnly 组 ❷。任何其他符合提升 RID 检查的组也会以相同方式转换。

特权列表仅显示五项 ❸。这是受限令牌可以拥有的仅有的五项特权。令牌的完整性级别设置为中，从完整令牌中的高降低而来 ❹。在令牌信息中，我们可以看到该令牌未被提升 ❺，并且提升类型表明这是受限令牌 ❻。

最后，请注意标志包含值 IsFiltered ❼。此标志表示该令牌已通过 `NtFilterToken` 系统调用进行了过滤。这是因为，要创建受限令牌，LSASS 首先会创建一个新的完整令牌，以便其认证 ID 具有唯一值。（如果比较代码清单 4-24 和 4-25 中的 Auth ID 值，您会注意到它们确实不同。）这允许 SRM 将这两个令牌视为处于不同的登录会话中。然后，LSASS 将令牌传递给 `NtFilterToken`，并带有 LuaToken 参数标志，以将任何提升的组转换为 UseForDenyOnly，并删除除允许的五项之外的所有特权。不过，`NtFilterToken` 不会将完整性级别从高降低到中；这必须单独完成。最后，LSASS 调用 `NtSetInformationToken`，使用 TokenLinkedToken 信息类将两个令牌链接在一起。

还有第三种提升类型，*默认*，用于任何与拆分令牌管理员无关的令牌：

```
PS> Use-NtObject($token = Get-NtToken -Anonymous) {$token.ElevationType}
Default
```

在此示例中，匿名用户不是拆分令牌管理员，因此令牌具有默认的提升类型。

#### UI 访问

Windows Vista 中引入的另一项安全功能是 *用户界面特权隔离 (UIPI)*，它防止较低特权进程以编程方式与较高特权进程的用户界面进行交互。这是通过完整性级别强制实施的，这也是 UAC 管理员以高完整性级别运行的另一个原因。

但 UIPI 给设计用于与用户界面交互的应用程序（如屏幕阅读器和触摸键盘）带来了问题。为了绕过此限制而不授予进程过多特权，令牌可以设置 UI 访问标志。进程是否获得 UI 访问权限取决于可执行文件清单文件中的 UiAccess 设置。

此 UI 访问标志向桌面环境发出信号，表明应禁用 UIPI 检查。在代码清单 4-26 中，我们在合适的进程（屏幕键盘 (OSK)）中查询此标志。

```
PS> $process = Start-Process "osk.exe" -PassThru
PS> $token = Get-NtToken -ProcessId $process.Id
PS> $token.UIAccess
True
```

*代码清单 4-26：查询屏幕键盘主令牌中的 UI 访问标志*

我们启动 OSK 并打开其 Token 对象以查询 UI 访问标志。要设置此标志，调用者需要拥有 `SeTcbPrivilege` 特权。普通用户创建 UI 访问进程的唯一方法是使用 UAC 服务。因此，任何 UI 访问进程都需要通过 `ShellExecute` 启动，这就是我们在代码清单 4-26 中使用 `Start-Process` 的原因。当您创建 UI 访问应用程序时，这一切都在后台发生。

#### 虚拟化

Vista 中因 UAC 引入的另一个问题是如何处理旧版应用程序，这些应用程序期望能够写入仅限管理员访问的位置，例如 *Windows* 目录或本地机器注册表配置单元。Vista 实现了一种特殊的解决方法：如果主令牌上启用了虚拟化标志，它将静默地将这些位置的写入重定向到每用户存储。这使得进程看起来好像已成功将资源添加到安全位置。

默认情况下，虚拟化标志会自动在旧版应用程序上启用。不过，你也可以通过在主令牌上设置属性来手动指定它。请在非管理员shell中运行代码清单 4-27中的命令。

```
❶ PS> $file = New-NtFile -Win32Path C:\Windows\hello.txt -Access GenericWrite
New-NtFile : (0xC0000022) - {Access Denied}
A process has requested access to an object, but has not been granted those access rights.

PS> $token = Get-NtToken
❷ PS> $token.VirtualizationEnabled = $true
❸ PS> $file = New-NtFile -Win32Path C:\Windows\hello.txt -Access GenericWrite
❹ PS> $file.Win32PathName
C:\Users\user\AppData\Local\VirtualStore\Windows\hello.txt
```

*代码清单 4-27：在Token对象上启用虚拟化并在C:\Windows中创建文件*

在此清单中，我们首先尝试创建一个可写文件*C:\Windows\hello.txt*❶。此操作因拒绝访问异常而失败。接着，我们获取当前主令牌并将VirtualizationEnabled属性设置为True❷。当我们重复文件创建操作时，现在成功了❸。如果我们查询文件的位置，会发现它位于用户目录下的虚拟存储中❹。只有普通的、无特权的令牌才能启用虚拟化；系统服务和管理员令牌的虚拟化是禁用的。你可以通过查询Token对象上的VirtualizationAllowed属性来了解是否允许虚拟化。

### 安全属性

令牌的*安全属性*是提供任意数据的名称/值对列表。与令牌关联的安全属性有三种类型：*本地*、*用户声明*和*设备声明*。每个安全属性可以有一个或多个值，这些值必须全部为相同类型。表4-5显示了安全属性的有效类型。

| 类型名称      | 描述                                                         |
| :------------ | :----------------------------------------------------------- |
| Int64         | 有符号64位整数                                               |
| UInt64        | 无符号64位整数                                               |
| String        | Unicode字符串                                                |
| Fqbn          | 完全限定的二进制名称；包含版本号和Unicode字符串              |
| Sid           | 一个SID                                                      |
| Boolean       | 真或假值，存储为Int64，其中0表示假，1表示真                  |
| OctetString   | 任意字节数组                                                 |

可以给安全属性分配一组标志，以改变其行为的某些方面，例如新令牌是否可以继承它。表4-6显示了已定义的标志。

| 标志名称           | 描述                                                         |
| :----------------- | :----------------------------------------------------------- |
| NonInheritable     | 安全属性不能被子进程令牌继承。                               |
| CaseSensitive      | 如果安全属性包含字符串值，比较时应区分大小写。               |
| UseForDenyOnly     | 安全属性仅在检查拒绝访问时使用。                             |
| DisabledByDefault  | 安全属性默认情况下被禁用。                                   |
| Disabled           | 安全属性被禁用。                                             |
| Mandatory          | 安全属性是强制性的。                                         |
| Unique             | 安全属性在本地系统上应是唯一的。                             |
| InheritOnce        | 安全属性只能被子进程继承一次，然后应设置为NonInheritable。   |

几乎每个进程令牌都具有TSA://ProcUnique安全属性。此安全属性包含在进程创建期间分配的唯一LUID。我们可以使用Show-NtTokenEffective显示有效令牌的该值，如代码清单 4-28所示。

```
PS> Show-NtTokenEffective -SecurityAttributes
SECURITY ATTRIBUTES
-------------------
Name             Flags                  ValueType Values
----             -----                  --------- ------
TSA://ProcUnique NonInheritable, Unique UInt64    {133, 1592482}
```

*代码清单 4-28：查询当前进程的安全属性*

从输出中，我们可以看到属性的名称是TSA://ProcUnique。它有两个UInt64值，组合起来形成一个LUID。最后，它有两个标志：NonInheritable，表示该安全属性不会传递给新的进程令牌；以及Unique，表示内核不应尝试将系统上同名的其他安全属性与该属性合并。

要设置本地安全属性，调用者需要在调用NtSetInformationToken之前具有SeTcb Privilege特权。用户和设备声明必须在令牌创建期间设置，我们将在下一节中讨论。

### 创建令牌

通常，当用户向计算机进行身份验证时，LSASS 会创建令牌。然而，它也可以为不存在的用户创建令牌，例如用于服务的虚拟账户。这些令牌可能是交互式的，用于控制台会话，也可能是网络令牌，用于本地网络。本地认证的用户可以通过调用 Win32 API（如 `LogonUser`）来创建另一个用户的令牌，该 API 会调用 LSASS 来执行令牌创建。

我们不会在第10章之前详细讨论 LSASS。然而，了解 LSASS 如何创建令牌是值得的。为此，LSASS 调用 `NtCreateToken` 系统调用。如前所述，此系统调用需要 `SeCreateTokenPrivilege` 特权，该特权仅授予有限数量的进程。此特权几乎是最高的，因为您可以使用它创建带有任何组或用户 SID 的任意令牌，并访问本地机器上的任何资源。

虽然您通常不需要从 PowerShell 调用 `NtCreateToken`，但如果您启用了 `SeCreateTokenPrivilege`，可以通过 `New-NtToken` 命令来实现。`NtCreateToken` 系统调用接受以下参数：

**令牌类型**    主令牌或模拟令牌

**认证 ID**    LUID 认证 ID；可以设置为任意值

**过期时间**    允许令牌在设定时间后过期

**用户**    用户 SID

**组**    组 SID 列表

**特权**    特权列表

**所有者**    所有者 SID

**主组**    主组 SID

**来源**    来源信息名称

此外，Windows 8 为系统调用引入了以下新功能，您可以通过 `NtCreateTokenEx` 系统调用访问：

**设备组**    设备的附加 SID 列表

**设备声明属性**    定义设备声明的安全属性列表

**用户声明属性**    定义用户声明的安全属性列表

**强制策略**    指示令牌强制完整性策略的标志集

这两个列表之外的任何内容只能在创建新令牌后通过调用 `NtSetInformationToken` 进行配置。根据要设置的令牌属性，您可能需要不同的特权，例如 `SeTcbPrivilege`。让我们演示如何使用代码清单 4-29中的脚本创建新令牌，该脚本必须以管理员身份运行。




```
PS> Enable-NtTokenPrivilege SeDebugPrivilege
❶ PS> $imp = Use-NtObject($p = Get-NtProcess -Name lsass.exe) {
    Get-NtToken -Process $p -Duplicate
}
❷ PS> Enable-NtTokenPrivilege SeCreateTokenPrivilege -Token $imp
❸ PS> $token = Invoke-NtToken $imp {
    New-NtToken -User "S-1-0-0" -Group "S-1-1-0"
}
PS> Format-NtToken $token -User -Group
USER INFORMATION
----------------
Name     Sid
----     ---
❹ NULL SID S-1-0-0

GROUP SID INFORMATION
-----------------
Name                                   Attributes
----                                   ----------
❺ Everyone                               Mandatory, EnabledByDefault, Enabled
Mandatory Label\System Mandatory Level Integrity, IntegrityEnabled
```


*代码清单 4-29：创建新令牌*

普通管理员默认没有 `SeCreateTokenPrivilege` 特权。因此，我们需要从另一个拥有该特权的进程中借用令牌。在大多数情况下，最容易借用的进程是 LSASS。我们打开 LSASS 进程及其令牌，将其复制为模拟令牌 ❶。接下来，我们确保在令牌上启用 `SeCreateTokenPrivilege` ❷。然后，我们可以模拟该令牌并调用 `New-NtToken`，为其传递用户 SID 和单个组 ❸。最后，我们可以打印新令牌的详细信息，包括其用户 SID 集 ❹ 和组集 ❺。`New-NtToken` 命令还会添加一个默认的系统完整性级别 SID，您可以在组列表中看到。

### 令牌分配

如果一个普通用户可以随意把任意的 Primary Token（主令牌） 或 Impersonation Token（模拟令牌） 分配给进程或线程，那么他就可能直接让自己的程序使用其他用户的安全身份，从而访问原本没有权限访问的资源。

这在模拟场景下尤其成问题，因为另一个用户账户只需打开一个命名管道，就可能无意中让服务器获得模拟令牌。

因此，SRM对普通用户在没有 `SeAssignPrimaryTokenPrivilege` 和 `SeImpersonationPrivilege` 特权的情况下能做什么施加了限制。让我们看看普通用户分配令牌必须满足的标准。

#### 分配主令牌

新进程可以通过以下三种方式之一获得主令牌：

- 它可以从父进程继承令牌。
- 令牌可以在进程创建期间分配（例如，使用 `CreateProcessAsUser` API）。
- 令牌可以在进程创建后、进程启动前，通过 `NtSetInformationProcess` 设置。

从父进程继承令牌是迄今为止最常见的令牌分配方式。例如，当你从 Windows 开始菜单启动应用程序时，新进程将继承 Explorer 进程的令牌。

如果进程没有从父进程继承令牌，进程将接收一个令牌句柄，该句柄必须具有 `AssignPrimary` 访问权限。如果对令牌对象的访问获得，SRM 会对令牌施加进一步的标准，以防止分配更高权限的令牌（除非调用者的主令牌启用了 `SeAssignPrimaryTokenPrivilege`）。

内核函数 `SeIsTokenAssignableToProcess` 强制执行令牌标准。首先，它检查分配的令牌的完整性级别是否小于或等于当前进程主令牌的完整性级别。如果满足该标准，它接着检查令牌是否满足 图 4-4 中显示的任一标准：即令牌要么是调用者主令牌的子令牌，要么是其兄弟令牌。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure4-4.webp)

图 4-4：SeIsTokenAssignableToProcess 主令牌分配标准

我们先介绍子令牌的情况。用户进程可以基于现有令牌创建新令牌。发生这种情况时，新令牌内核对象中的 `ParentTokenId` 属性会被设置为父令牌的 ID。如果新令牌的 `ParentTokenId` 与当前主令牌的 ID 值匹配，则分配被允许。受限令牌就是子令牌的例子；当你使用 `NtFilterToken` 创建受限令牌时，新令牌的父令牌 ID 会被设置为原始令牌的 ID。

*兄弟令牌* 是与现有令牌在同一身份验证会话中创建的令牌。为了测试此标准，该函数会比较两个令牌的父令牌 ID 和身份验证 ID。如果它们相同，则可以分配该令牌。此检查还会测试身份验证会话是否是由内核设置的特殊兄弟会话（一种罕见的配置）。兄弟令牌的常见示例包括从当前进程令牌复制的令牌和lowbox令牌。

请注意，该函数不检查令牌所代表的用户，如果令牌符合任一标准，则有可能将其分配给新进程。如果不符合标准，则在令牌分配期间将返回 `STATUS_PRIVILEGE_NOT_HELD` 错误。

`runas` 实用程序如何在普通用户身份下，在这些限制条件下创建新进程？它使用 `CreateProcessWithLogon` API，该 API 对用户进行身份验证，并从具有绕过这些检查所需特权的系统服务启动进程。

如果我们尝试分配进程令牌，即使是为同一用户分配令牌，也会看到操作多么容易失败。以非管理员用户身份运行 代码清单 4-30 中的代码。




```
PS> $token = Get-NtToken -Filtered -Flags DisableMaxPrivileges
❶ PS> Use-NtObject($proc = New-Win32Process notepad -Token $token) {
    $proc | Out-Host
}
Process            : notepad.exe
Thread             : thread:11236 - process:9572
Pid                : 9572
Tid                : 11236
TerminateOnDispose : False
ExitStatus         : 259
ExitNtStatus       : STATUS_PENDING

❷ PS> $token = Get-NtToken -Filtered -Flags DisableMaxPrivileges -Token $token
PS> $proc = New-Win32Process notepad -Token $token
❸ Exception calling "CreateProcess" with "1" argument(s): "A required privilege
is not held by the client"
```


*代码清单 4-30：使用受限令牌创建进程*

在这里，我们创建两个受限令牌，并使用它们创建记事本实例。在第一次尝试中，我们基于当前主令牌创建令牌 ❶。新令牌中的父令牌 ID 字段被设置为主令牌的 ID，当我们在进程创建期间使用该令牌时，操作成功。

在第二次尝试中，我们创建另一个令牌，但基于之前创建的令牌 ❷。使用此令牌创建进程会因特权错误而失败 ❸。这是因为第二个令牌的父令牌 ID 被设置为已构造令牌的 ID，而不是主令牌的 ID。由于该令牌既不符合子令牌也不符合兄弟令牌的标准，此操作在分配期间将失败。

你可以通过使用 `NtSetInformationProcess` 系统调用或 `ProcessAccessToken` 在进程创建后设置令牌，PowerShell 通过 `Set-NtToken` 命令公开了此功能（如 代码清单 4-31 所示）。




```
PS> $proc = Get-NtProcess -Current
PS> $token = Get-NtToken -Duplicate -TokenType Primary
PS> Set-NtToken -Process $proc -Token $token
Set-NtToken : (0xC00000BB) - The request is not supported.
```


*代码清单 4-31：在进程启动后设置访问令牌*

此赋值操作不会绕过我们讨论过的任何赋值检查。一旦进程的初始线程开始执行，设置主令牌的选项就会被禁用，因此当我们尝试在已启动的进程上设置令牌时，会收到 `STATUS_UNSUPPORTED` 错误。

#### 分配模拟令牌

与主令牌一样，SRM 要求分配的模拟令牌满足一组特定标准；否则，它将拒绝将令牌分配给线程。有趣的是，这些标准与主令牌的分配标准并不相同。这可能导致某些情况下可以分配模拟令牌但不能分配主令牌，反之亦然。

如果显式指定令牌，则句柄必须具有模拟访问权限。如果模拟是隐式发生的，则内核已经在维护该令牌，并且不需要特定的访问权限。

内核中的 `SeTokenCanImpersonate` 函数负责检查模拟标准。如 图 4-5 所示，此检查比主令牌的分配检查复杂得多。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure4-5.webp)

图 4-5：`SeTokenCanImpersonate` 模拟令牌检查

模拟令牌既可以分配给当前进程中的线程，也可以分配给其他进程中的线程。因此，内核在进行检查时，作为比较基准的主令牌并不是调用者自己的主令牌，而是**目标线程所属进程的主令牌**。该函数执行以下验证步骤：

  1.  检查标识或匿名模拟级别。如果模拟令牌具有这些级别之一，将其分配给线程不会构成安全风险，SRM 会立即允许该分配。如果模拟令牌基于其身份验证 ID 表示匿名用户，此检查也允许分配。

  2.  检查模拟特权。如果启用了 `SeImpersonatePrivilege`，SRM 会再次立即允许该分配。

  3.  比较主令牌和模拟令牌的完整性级别。如果主令牌的完整性级别低于模拟令牌，则拒绝分配。如果相同或更高，则继续检查。

  4.  检查身份验证 ID 是否等于来源 ID。如果模拟令牌的来源登录标识符等于主令牌的身份验证标识符，SRM 允许该分配。否则，它继续进行检查。

请注意，此检查有一个有趣的后果。如本章前面所述，普通用户令牌的来源登录标识符设置为 *SYSTEM* 用户的身份验证标识符。这是因为身份验证进程以 *SYSTEM* 用户身份运行。因此，*SYSTEM* 用户可以模拟系统上的任何其他令牌，只要满足完整性级别要求，即使未启用 `SeImpersonatePrivilege` 特权也是如此。

  5.  检查用户 SID 是否相等。如果主令牌的用户 SID 不等于模拟令牌的用户 SID，SRM 拒绝分配。否则，它继续进行检查。此标准允许用户模拟自己的用户账户，但阻止他们模拟其他用户，除非他们拥有其他用户的凭据。当验证其他用户时，LSASS 返回一个模拟令牌，其来源登录标识符设置为调用者的身份验证标识符，因此令牌将通过前一个检查，用户 SID 将永远不会被比较。

  6.  检查提升标志。此检查确保调用者不能为同一用户模拟更高级别的令牌。如果模拟令牌设置了提升标志，但主令牌没有，则模拟将失败。Windows 10 之前的版本不执行此检查，因此以前可以通过先降低完整性级别来模拟 UAC 管理员令牌。

7. 检查沙箱化。此检查确保调用者无法模拟一个沙箱化程度较低的令牌。要模拟一个低沙箱令牌，新令牌必须与包SID匹配，或者是主令牌的受限包SID；否则，模拟将失败。对能力列表不进行检查。对于受限令牌，只要新令牌也是受限令牌即可，即使受限SID列表不同。这同样适用于写受限令牌。SRM具有多种加固机制，使得获取更高权限的沙箱令牌变得困难。

8. 检查控制台会话。最后一步检查控制台会话是否为会话0。这可以防止用户模拟会话0中的令牌，从而获得提升的权限（例如能够创建全局Section对象）。

你可能会认为，如果函数拒绝分配，它会返回STATUS_PRIVILEGE_NOT_HELD错误，但事实并非如此。相反，SRM会将模拟令牌复制为标识级别令牌并分配它。这意味着即使模拟分配失败，线程仍然可以检查令牌的属性。

你可以使用Test-NtTokenImpersonation PowerShell命令来检查你是否能模拟令牌。此命令模拟令牌并从线程重新打开它。然后比较原始令牌和重新打开令牌的模拟级别，并返回布尔结果。在代码清单 4-32中，我们运行一个简单的示例，该示例将因完整性级别检查而失败。请注意，最好不要在你关心的PowerShell进程中运行此脚本，因为你将无法恢复原始完整性级别。

```
PS> $token = Get-NtToken -Duplicate
PS> Test-NtTokenImpersonation $token
True

PS> Set-NtTokenIntegrityLevel -IntegrityLevel Low
PS> Test-NtTokenImpersonation $token
False

PS> Test-NtTokenImpersonation $token -ImpersonationLevel Identification
True
```

*代码清单 4-32：检查令牌模拟*

这些检查相当简单。首先，我们获取当前进程令牌的副本，并将其传递给Test-NtTokenImpersonation。结果为True，表示我们可以在模拟级别模拟该令牌。对于下一次检查，我们将当前进程主令牌的完整性级别降低到低，并再次运行测试。这次返回False，因为不再可能在模拟级别模拟该令牌。最后，我们检查是否可以在标识级别模拟该令牌，这也返回True。

### 实际示例

让我们通过一些实际示例来了解如何在本章中使用各种命令进行安全研究或系统分析。

#### 查找具有UI访问权限的进程

有时，枚举所有你可以访问的进程并检查其主令牌的属性是很有用的。这可以帮助你找到以特定用户身份运行或具有特定属性的进程。例如，你可以识别设置了UI访问标志的进程。在本章前面，我们讨论了如何单独检查UI访问标志。在代码清单 4-33中，我们将对所有可访问的进程执行此检查。




```
PS> $ps = Get-NtProcess -Access QueryLimitedInformation -FilterScript {
    Use-NtObject($token = Get-NtToken -Process $_ -Access Query) {
        $token.UIAccess
    }
}
PS> $ps
Handle Name       NtTypeName Inherit ProtectFromClose
------ ----       ---------- ------- ----------------
3120   ctfmon.exe Process    False   False
3740   TabTip.exe Process    False   False

PS> $ps.Close()
```


*代码清单 4-33：查找具有UI访问权限的进程*

我们首先调用`Get-NtProcess`命令，以`QueryLimitedInformation`访问权限打开所有进程。我们还提供了一个筛选脚本。如果脚本返回`True`，命令将返回该进程；否则，它将关闭该进程的句柄。

在脚本中，我们以`Query`访问权限打开进程的令牌，并返回`UIAccess`属性。结果将进程列表筛选为仅包含使用UI访问令牌运行的进程。我们显示找到的进程。

#### 查找可模拟的令牌句柄

有几种官方方法可以获取要模拟的令牌，例如使用远程过程调用(Remote Procedure Call, RPC)或打开进程的主令牌。另一种方法是查找现有的`Token`对象句柄，你可以复制这些句柄并用于模拟。

如果你以非管理员用户身份运行并拥有`SeImpersonatePrivilege`特权（例如`LOCAL SERVICE`等服务帐户），或者为了评估沙箱的安全性以确保沙箱无法打开并模拟更高特权的令牌，此技术可能很有用。你还可以通过等待用户连接到Windows机器（例如通过网络）来访问另一个用户的资源。如果你获取了用户的令牌，就可以重用其身份，而无需知道其密码。代码清单 4-34展示了此想法的简单实现。




```
PS> function Get-ImpersonationTokens {
  ❶ $hs = Get-NtHandle -ObjectType Token
    foreach($h in $hs) {
        try {
          ❷ Use-NtObject($token = Copy-NtObject -Handle $h) {
              ❸ if (Test-NtTokenImpersonation -Token $token) {
                    Copy-NtObject -Object $token
                }
            }
        } catch {
        }
    }
}
❹ PS> $tokens = Get-ImpersonationTokens
❺ PS> $tokens | Where-Object Elevated
```


*代码清单 4-34：查找可模拟的提升令牌句柄*

在`Get-ImpersonationTokens`函数中，我们使用`Get-NtHandle`命令获取所有`Token`类型的句柄列表❶。然后，对于每个句柄，我们尝试使用`Copy-NtObject`命令将句柄复制到当前进程❷。如果成功，我们测试是否可以成功模拟该令牌；如果可以，我们再次复制令牌，以便它不会被关闭❸。

运行`Get-ImpersonationTokens`函数将返回所有可访问且可模拟的令牌句柄❹。利用这些`Token`对象，我们可以查询感兴趣的属性。例如，我们可以检查令牌是否已提升❺，这可能表明我们可以使用该令牌通过模拟获得额外的特权组。

#### 移除管理员特权

在以管理员身份运行程序时，你可能希望暂时降低特权，以便执行某些操作而不会损坏计算机，例如意外删除系统文件。要执行此操作，你可以使用UAC创建筛选后的低特权令牌所用的相同方法。以管理员身份运行代码清单 4-35中的代码。




```
PS> $token = Get-NtToken -Filtered -Flags LuaToken
PS> Set-NtTokenIntegrityLevel Medium -Token $token
PS> $token.Elevated
False

PS> "Admin" > "$env:windir\admin.txt"
PS> Invoke-NtToken $token {"User" > "$env:windir\user.txt"}
out-file : Access to the path 'C:\WINDOWS\user.txt' is denied.

PS> $token.Close()
```


*代码清单 4-35：移除管理员特权*

我们首先筛选当前令牌并指定`LuaToken`标志。此标志会移除所有管理员组以及受限令牌不允许拥有的额外特权。`LuaToken`标志不会降低令牌的完整性级别，因此我们必须手动将其设置为`Medium`。我们可以通过检查`Elevated`属性是否为`False`来验证该令牌不再被视为管理员令牌。

为了查看实际效果，我们现在可以尝试向仅管理员可访问的位置（例如`Windows`目录）写入文件。当我们使用当前进程令牌尝试此操作时，操作会成功。然而，当我们模拟该令牌尝试执行操作时，操作会因拒绝访问错误而失败。你还可以使用`New-Win32Process` PowerShell命令配合该令牌启动一个使用较低特权令牌的新进程。

### 总结

本章介绍了两种主要类型的令牌：主令牌，它与进程相关联；以及模拟令牌，它与线程相关联，允许进程临时模拟另一个用户。我们探讨了这两种令牌的重要属性，如组、特权和完整性级别，以及这些属性如何影响令牌所暴露的安全身份。随后，我们讨论了两种沙箱令牌（受限令牌和lowbox令牌），浏览器和文档阅读器等应用程序使用它们来限制潜在远程代码执行漏洞造成的损害。

接下来，我们考虑了令牌如何用于表示管理员特权，包括Windows如何为普通桌面用户实现用户账户控制（UAC）和拆分令牌管理员。在此讨论中，我们详细探讨了操作系统认为管理员或提升令牌的具体标准。

最后，我们讨论了将令牌分配给进程和线程的步骤。我们定义了普通用户分配令牌所需满足的具体条件，以及主令牌和模拟令牌检查之间的差异。

在下一章中，我们将讨论安全描述符。这些描述符根据调用者访问令牌中的身份和组来定义对资源的访问权限。

## 5. 安全描述符

在前一章中，我们讨论了安全访问令牌，它向SRM描述了用户的身份。在本章中，您将学习*安全描述符*如何定义资源的安全性。安全描述符具有多种功能。它指定了资源的所有者，使SRM能够向访问自己数据的用户授予特定权限。它还包含*自主访问控制（DAC）*和*强制访问控制（MAC）*，用于授予或拒绝用户和组的访问权限。最后，它还可以包含生成审计事件的条目。几乎每个内核资源都有安全描述符，用户模式应用程序也可以通过安全描述符实现自己的访问控制，而无需创建内核资源。

理解安全描述符的结构对于理解Windows的安全性至关重要，因为它们用于保护每个内核对象和许多用户模式组件（如服务）的安全。您甚至会发现安全描述符被跨网络边界用于保护远程资源。在开发Windows应用程序或研究Windows安全性时，您不可避免地需要检查或创建安全描述符，因此清晰理解安全描述符包含的内容将为您节省大量时间。为帮助您理解，我将首先更详细地描述安全描述符的结构。

### 安全描述符的结构

Windows 将安全描述符以二进制结构的形式存储在磁盘或内存中。虽然你很少需要手动解析这些结构，但了解其内容仍然值得。一个安全描述符由以下七个组件组成：

- 版本号
- 可选资源管理器标志
- 控制标志
- 可选的所有者 SID
- 可选的组 SID
- 可选的自主访问控制列表(Discretionary Access Control List, DACL)
- 可选的系统访问控制列表(System Access Control List, SACL)

让我们逐一查看这些组件。任何安全描述符的第一个组件是 *版本号*，它指示安全描述符二进制格式的版本。目前只有一个版本，因此版本号始终设置为值 1。接下来是一组可选的资源管理器标志。你几乎不会遇到这些标志被设置的情况；然而，它们被 Active Directory 使用，因此我们将在 第 11 章 中进一步讨论。

资源管理器标志之后是一组 *控制标志*。它们有三个用途：定义安全描述符的哪些可选组件有效、安全描述符及其组件是如何创建的，以及在将安全描述符应用于对象时如何处理它。表 5-1 显示了有效标志及其描述的列表。我们将在下一章中更详细地介绍此表中的许多术语，例如继承。

| 名称               | 值      | 描述                                                         |
| :----------------- | :------ | :----------------------------------------------------------- |
| OwnerDefaulted     | 0x0001  | 所有者 SID 是通过默认方法分配的。                            |
| GroupDefaulted     | 0x0002  | 组 SID 是通过默认方法分配的。                                |
| DaclPresent        | 0x0004  | 安全描述符中存在 DACL。                                      |
| DaclDefaulted      | 0x0008  | DACL 是通过默认方法分配的。                                  |
| SaclPresent        | 0x0010  | 安全描述符中存在 SACL。                                      |
| SaclDefaulted      | 0x0020  | SACL 是通过默认方法分配的。                                  |
| DaclUntrusted      | 0x0040  | 当与 ServerSecurity 结合使用时，DACL 不受信任。              |
| ServerSecurity     | 0x0080  | DACL 被替换为服务器 ACL（更多关于此用途的信息请参阅 第 6 章）。 |
| DaclAutoInheritReq | 0x0100  | 请求子对象的 DACL 自动继承。                                 |
| SaclAutoInheritReq | 0x0200  | 请求子对象的 SACL 自动继承。                                 |
| DaclAutoInherited  | 0x0400  | DACL 支持自动继承。                                          |
| SaclAutoInherited  | 0x0800  | SACL 支持自动继承。                                          |
| DaclProtected      | 0x1000  | DACL 受保护，不进行继承。                                    |
| SaclProtected      | 0x2000  | SACL 受保护，不进行继承。                                    |
| RmControlValid     | 0x4000  | 资源管理器标志有效。                                         |
| SelfRelative       | 0x8000  | 安全描述符采用相对格式。                                     |

在控制标志（Control Flags）之后，是**所有者 SID（Owner SID）**，用于标识资源的所有者。通常，所有者 SID 是某个用户的 SID，但资源的所有权也可以授予某个组，例如 **Administrators（管理员）组**。成为资源的所有者后，所有者会获得某些特殊权限，其中包括**修改该资源安全描述符的能力**。这样设计的目的，是避免用户因为修改了资源的访问控制设置而将自己永久锁在资源之外。即使用户后来修改了资源的 DACL，所有者身份仍然使其能够重新修改安全描述符，从而恢复对资源的控制。

接下来是**组 SID（Group SID）**。它的作用与所有者 SID 类似，但在现代 Windows 中很少使用。Group SID 主要是为了兼容 **POSIX** 环境而保留下来的。在 Windows 曾经提供 POSIX 子系统的时期，POSIX 的文件权限模型包含“所有者、组、其他用户”这样的概念，因此安全描述符中保留了一个 Group SID 字段。

对于 Windows 应用程序使用的访问控制而言，**Group SID 不参与 Windows 的访问检查过程**。因此，在分析 Windows 安全描述符时，应重点关注 Owner SID，而不应将 Group SID 理解为类似 Linux 文件系统中“所属组”的实际访问控制机制。

安全描述符中最重要的部分是 *DACL*。DACL 包含一个 *访问控制条目（ACE）* 列表，这些条目定义了 SID 获得的访问权限。它被认为是 *自主的*，因为用户或系统管理员可以选择授予的访问级别。ACE 有许多不同类型。我们将在本章稍后的“访问控制列表(Access Control List, ACL)头与 ACE 条目”一节中进一步讨论；目前，你只需要知道每个 ACE 中的基本信息包括以下内容：

- ACE 适用的用户或组的 SID
- ACE 的类型
- 允许或拒绝 SID 访问的访问掩码

安全描述符的最后一个组件是*SACL（SACL，System Access Control List）*，它用于存储系统审计规则与强制标签。与DACL类似，SACL包含一系列ACE，但它的作用并非基于定义的SID是否匹配当前用户的SID来决定访问权限，而是确定在资源被访问时生成审计事件的规则。自Windows Vista以来，SACL也成为存储额外非审计ACE（如资源的强制标签）的首选位置。

在DACL和SACL中，还有两个最终元素需要指出，即DaclPresent和SaclPresent控制标志。这些标志分别指示DACL和SACL是否存在于安全描述符中。使用标志可以设置*NULL ACL*，即存在标志已设置，但安全描述符中的ACL字段未指定任何值。NULL ACL表示该ACL未定义任何安全策略，并导致SRM有效地忽略它。这与空ACL不同，空ACL中，存在标志已设置，且ACL字段指定了值，但该ACL不包含任何ACE。

### SID 的结构

到目前为止，我们一直将 SID 视为不透明的二进制值或数字字符串。在本节中，我们将更深入地了解 SID 包含的内容。图 5-1 中的图示展示了 SID 在内存中的存储方式。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure5-1.webp)

图 5-1：内存中的 SID 结构

二进制 SID 包含四个组成部分：

**修订版本**    一个始终设置为 1 的值，因为没有其他已定义的版本号

**相对标识符计数**    SID 中 RID 的数量

**安全机构**    表示颁发 SID 的机构的数值

**相对标识符**    零个或多个 32 位数字，代表用户或组

安全机构可以是任意值，但 Windows 已预定义了一些常用的值。所有知名机构均以五个 0 字节开头，后跟 表 5-2 中的值。

| 名称           | 最终值 | 示例名称                                               |
| :------------- | :---------- | :----------------------------------------------------- |
| Null           | 0           | NULL SID                                               |
| World          | 1           | Everyone                                               |
| Local          | 2           | CONSOLE LOGON                                          |
| Creator        | 3           | CREATOR OWNER                                          |
| Nt             | 5           | BUILTIN\Users                                          |
| Package        | 15          | APPLICATION PACKAGE AUTHORITY\Your Internet connection |
| MandatoryLabel | 16          | Mandatory Label\Medium Mandatory Level                 |
| ScopedPolicyId | 17          | N/A                                                    |
| ProcessTrust   | 19          | TRUST LEVEL\ProtectedLight-Windows                     |

安全机构之后是相对标识符。一个 SID 可以包含一个或多个 RID，其中域 RID 后跟用户 RID。

让我们逐步了解如何为知名组 *BUILTIN\Users* 构建 SID。请注意，域组件与组名之间用反斜杠分隔。在此例中，域为 *BUILTIN*。这是一个预定义的域，由单个 RID（32）表示。代码清单 5-1 使用 Get-NtSid PowerShell 命令从其组件构建 *BUILTIN* 域的域 SID，然后使用 Get-NtSidName 命令检索该 SID 的系统定义名称。




```
PS> $domain_sid = Get-NtSid -SecurityAuthority Nt -RelativeIdentifier 32
PS> Get-NtSidName $domain_sid
Domain  Name    Source  NameUse Sddl
------  ----    ------  ------- ----
BUILTIN BUILTIN Account Domain  S-1-5-32
```


*代码清单 5-1：查询* BUILTIN *域的 SID*

*BUILTIN* 域的 SID 是 Nt 安全机构的成员。我们使用 SecurityAuthority 参数指定此安全机构，并使用 RelativeIdentifier 参数指定单个 RID。

然后，我们将 SID 传递给 Get-NtSidName 命令。输出的前两列显示域名称和 SID 的名称。在此例中，这两个值相同；这只是 *BUILTIN* 域注册的一个特性。

下一列指示名称的检索来源。在此示例中，来源为 Account，表示名称是从 LSASS 检索的。如果来源为 WellKnown，则表示 PowerShell 已提前知道该名称，无需查询 LSASS。第四列 NameUse 指示 SID 的类型。在此例中，它是 Domain，这符合我们的预期。最后一列是 SID 的 SDDL 格式。

域 SID 之后指定的任何 RID 都标识特定的用户或组。对于 *Users* 组，我们使用值为 545 的单个 RID（由 Windows 预定义）。代码清单 5-2 通过将 545 RID 添加到基础域 SID 来创建新的 SID。




```
PS> $user_sid = Get-NtSid -BaseSid $domain_sid -RelativeIdentifier 545
PS> Get-NtSidName $user_sid
Domain  Name  Source  NameUse Sddl
------  ----  ------  ------- ----
BUILTIN Users Account Alias   S-1-5-32-545

PS> $user_sid.Name
BUILTIN\Users
```


*代码清单 5-2：从安全机构和 RID 构建 SID*

输出现在显示 *Users* 作为 SID 名称。同时请注意，此例中的 NameUse 设置为 Alias。这表示该 SID 代表一个本地内置组，与代表用户定义组的 Group 不同。当我们打印 SID 的 Name 属性时，它会输出完全限定名称，域和名称之间用反斜杠分隔。

你可以在微软的技术文档和其他网站上找到已知SID的列表。然而，微软有时会添加未记录的SID。因此，我鼓励你测试多种安全机构和RID值，看看还能发现哪些其他用户和组。仅仅检查不同的SID不会造成任何损害。例如，尝试将代码清单 5-2中的用户RID替换为544。这个新的SID代表*BUILTIN\Administrators*组，如代码清单 5-3所示。




```
PS> Get-NtSid -BaseSid $domain_sid -RelativeIdentifier 544
Name                   Sid
----                    ---
BUILTIN\Administrators S-1-5-32-544
```


*代码清单 5-3：查询* Administrators *组的SID*

记住特定SID的安全机构和RID可能比较棘手，你可能无法准确回忆起使用Name参数查询的确切名称，如第2章所述。因此，`Get-NtSid`实现了一种模式，可以从已知集合中查询SID。例如，要查询*Administrators*组的SID，可以使用代码清单 5-4中显示的命令。




```
PS> Get-NtSid -KnownSid BuiltinAdministrators
Name                   Sid
----                   ---
BUILTIN\Administrators S-1-5-32-544
```


*代码清单 5-4：查询已知的* Administrators *组SID*

你会在Windows操作系统中发现各种SID。理解它们的结构至关重要，这将使你能够快速评估SID可能代表什么。例如，如果你识别出一个具有Nt安全机构且第一个RID为32的SID，你可以确定它代表一个内置用户或组。了解结构还允许你在没有更好工具的情况下，从崩溃转储或内存中识别和提取SID。

### 绝对与相对安全描述符

内核支持两种安全描述符的二进制表示格式：绝对格式和相对格式。本节将逐一探讨这两种格式，并分析各自的优缺点。

两种格式均以相同的三个值开头：修订版本号、资源管理器标志和控制标志。控制标志中的“自相对”标志决定了采用哪种格式，如图5-2所示。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure5-2.webp)

图5-2：选择安全描述符格式

安全描述符头部的总大小为32位，分为两个8位值（修订版本号和Sbz1）以及16位的控制标志。安全描述符的资源管理器标志存储在Sbz1中；仅当设置了RmControlValid控制标志时这些标志才有效，但无论何种情况该值都会存在。安全描述符的其余部分紧随头部之后存储。

最简单的格式——绝对安全描述符，在未设置“自相对”标志时使用。在公共头部之后，绝对格式定义了四个指向内存中引用的指针：所有者SID、组SID、DACL和SACL，按此顺序排列，如图5-3所示。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure5-3.webp)

图5-3：绝对安全描述符的结构

每个指针引用一个绝对内存地址，数据存储在该地址处。因此，指针的大小取决于应用程序是32位还是64位。也可以将指针指定为NULL值，表示该值不存在。所有者SID和组SID的值使用前文定义的二进制格式存储。

当设置了“自相对”标志时，安全描述符则采用相对格式。相对安全描述符不是使用绝对内存地址来引用其值，而是将这些位置存储为相对于其头部起始位置的正偏移量。图5-4展示了相对安全描述符的构造方式。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure5-4.webp)

图5-4：相对安全描述符的结构

这些值存储在连续的内存中。ACL格式（我们将在下一节探讨）本身已是相对格式，因此在相对安全描述符中使用时无需特殊处理。每个偏移量始终为32位，无论系统的位数如何。如果偏移量设置为0，则表示该值不存在，类似于绝对安全描述符中的NULL情况。

绝对安全描述符的主要优势在于可以轻松更新其各个组件。例如，要替换所有者SID，您可以在内存中分配一个新的SID，并将其内存地址赋给所有者指针。相比之下，以相同方式修改相对安全描述符可能需要调整其分配的内存，如果新的所有者SID结构比旧的大。

另一方面，相对安全描述符的一大优势是它可以在单个连续内存块中构建。这使得您可以将安全描述符序列化为持久格式，例如文件或注册表键。当您需要确定资源的安全性时，可能需要从内存或持久存储中提取其安全描述符。通过理解这两种格式，您可以确定如何将安全描述符读取为可查看或操作的内容。

大多数API和系统调用接受任一格式的安全描述符，通过检查“自相对”标志的值自动确定如何处理。然而，您会发现一些例外情况，某些API仅接受一种格式；在这种情况下，如果您向API传递了错误格式的安全描述符，通常会收到诸如STATUS_INVALID_SECURITY_DESCR之类的错误。API返回的安全描述符几乎总是采用相对格式，因为其内存管理更为简单。系统提供了RtlAbsoluteToSelfRelativeSD和RtlSelfRelativeToAbsoluteSD API，以便在需要时在两种格式之间进行转换。

PowerShell模块统一使用SecurityDescriptor对象处理所有安全描述符，无论其格式如何。该对象基于.NET编写，仅在需要与原生代码交互时，才会转换为相对或绝对安全描述符。您可以通过检查SelfRelative属性，判断SecurityDescriptor对象是否由相对安全描述符生成。

### ACL头与条目

DACL和SACL构成了安全描述符中的大部分数据。尽管这些元素用途不同，但它们共享相同的基本结构。在本节中，我们将介绍它们在内存中的排列方式，而它们如何参与访问检查过程的细节将在第7章中讨论。

#### 头结构

所有ACL都由一个ACL头结构后跟零个或多个ACE组成，这些ACE位于一个连续的内存块中。图5-5展示了这一顶层格式。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure5-5.webp)

图5-5：ACL结构的顶层概览

ACL头结构包含一个修订版本号、ACL的总大小（以字节为单位）以及头结构后跟随的ACE条目数量。图5-6展示了头结构。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure5-6.webp)

图5-6：ACL头结构

ACL头结构还包含两个保留字段，Sbz1和Sbz2，它们应始终为0。在现代Windows版本中，它们没有用途，仅用于ACL结构需要扩展时。目前，Revision字段可以有三个值之一，这些值决定了ACL中有效的ACE类型。如果ACL使用了修订版本不支持的ACE，则该ACL将被视为无效。Windows支持以下修订版本：

**默认**    默认的ACL修订版本。支持所有基本ACE类型，如允许和拒绝。指定为修订值2。

**复合**    在默认ACL修订版本基础上增加了对复合ACE的支持。指定为修订值3。

**对象**    在复合修订版本基础上增加了对对象ACE的支持。指定为修订值4。

#### ACE列表

ACL头结构之后是ACE列表，它决定了SID具有的访问权限。ACE的长度可变，但始终以包含ACE类型、附加标志和ACE总大小的头结构开始。头结构之后是特定于ACE类型的数据。图5-7展示了这一结构。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure5-7.webp)

图5-7：ACE结构

ACE头结构对所有ACE类型都是通用的。这允许应用程序在处理ACL时安全地访问头结构。然后可以使用ACE类型值来确定ACE类型特定数据的确切格式。如果应用程序不理解ACE类型，它可以使用大小字段完全跳过该ACE（我们将在第7章中讨论类型如何影响访问检查）。

表5-3列出了支持的ACE类型、它们有效所需的最低ACE修订版本，以及它们是否在DACL或SACL中有效。

| ACE 类型                | 值     | 最低修订版本 | ACL  | 描述                                                         |
| :---------------------- | :----- | :----------- | :--- | :----------------------------------------------------------- |
| 允许（Allowed）         | 0x0    | 默认         | DACL | 授予对资源的访问权限                                         |
| 拒绝（Denied）          | 0x1    | 默认         | DACL | 拒绝对资源的访问权限                                         |
| 审计（Audit）           | 0x2    | 默认         | SACL | 审计对资源的访问                                             |
| 警报（Alarm）           | 0x3    | 默认         | SACL | 访问资源时触发警报；未使用                                   |
| 允许复合（AllowedCompound） | 0x4 | 复合         | DACL | 在模拟期间授予对资源的访问权限                               |
| 允许对象（AllowedObject） | 0x5  | 对象         | DACL | 授予对具有对象类型的资源的访问权限                           |
| 拒绝对象（DeniedObject） | 0x6   | 对象         | DACL | 拒绝对具有对象类型的资源的访问权限                           |
| 审计对象（AuditObject） | 0x7   | 对象         | SACL | 审计对具有对象类型的资源的访问                               |
| 警报对象（AlarmObject） | 0x8   | 对象         | SACL | 访问具有对象类型的资源时触发警报；未使用                     |
| 允许回调（AllowedCallback） | 0x9 | 默认         | DACL | 通过回调授予对资源的访问权限                                 |
| 拒绝回调（DeniedCallback） | 0xA | 默认         | DACL | 通过回调拒绝对资源的访问权限                                 |
| 允许回调对象（AllowedCallbackObject） | 0xB | 对象 | DACL | 通过回调和对象类型授予访问权限                               |
| 拒绝回调对象（DeniedCallbackObject） | 0xC | 对象 | DACL | 通过回调和对象类型拒绝访问权限                               |
| 审计回调（AuditCallback） | 0xD  | 默认         | SACL | 通过回调审计访问                                             |
| 警报回调（AlarmCallback） | 0xE  | 默认         | SACL | 通过回调访问时触发警报；未使用                               |
| 审计回调对象（AuditCallbackObject） | 0xF | 对象 | SACL | 通过回调和对象类型审计访问                                   |
| 警报回调对象（AlarmCallbackObject） | 0x10 | 对象 | SACL | 通过回调和对象类型访问时触发警报；未使用                     |
| 强制标签（MandatoryLabel） | 0x11 | 默认         | SACL | 指定强制标签                                               |
| 资源属性（ResourceAttribute） | 0x12 | 默认       | SACL | 指定资源的属性                                               |
| 作用域策略ID（ScopedPolicyId） | 0x13 | 默认     | SACL | 指定资源的中央访问策略ID                                     |
| 进程信任标签（ProcessTrustLabel） | 0x14 | 默认 | SACL | 指定进程信任标签以限制资源访问                               |
| 访问过滤器（AccessFilter） | 0x15 | 默认       | SACL | 指定资源的访问过滤器                                         |

虽然Windows官方支持所有这些ACE类型，但内核不使用警报类型。用户应用程序可以指定自己的ACE类型，但用户模式和内核模式中的各种API会检查有效类型，如果ACE类型未知，将生成错误。

ACE的类型特定数据主要分为三种格式之一：普通ACE（如允许和拒绝）、复合ACE和对象ACE。*普通ACE*在头部之后包含以下字段，括号中指示字段大小：

**访问掩码（32位）**    根据ACE类型授予或拒绝的访问掩码

**SID（可变大小）**    SID，采用本章前面描述的二进制格式

*复合ACE*用于模拟期间。这些ACE可以同时授予模拟调用者和进程用户的访问权限。它们的唯一有效类型是允许复合。尽管最新版本的Windows仍然支持复合ACE，但它们实际上未记录在案，可能已被弃用。我将其包含在本书中是为了完整性。它们的格式如下：

**访问掩码（32位）**    要授予的访问掩码

**复合ACE类型（16位）**    设置为1，表示该ACE用于模拟

**保留（16位）**    始终为0

**服务器SID（可变大小）**    二进制格式的服务器SID；与服务用户匹配

**SID（可变大小）**    二进制格式的SID；与模拟用户匹配

Microsoft引入了*对象ACE*格式以支持Active Directory域服务的访问控制。Active Directory使用128位GUID来表示目录服务对象类型；对象ACE确定特定类型对象（如计算机或用户）的访问权限。例如，使用单个安全描述符，目录可以授予SID创建一种类型对象所需的访问权限，但不授予另一种类型。对象ACE格式如下：

**访问掩码（32位）**    根据ACE类型授予或拒绝的访问掩码

**标志（32位）**    用于指示以下哪些GUID存在

**对象类型（16字节）**    ObjectType GUID；仅当第0位标志被设置时存在

**继承对象类型（16字节）**    继承的对象GUID；仅当第1位标志被设置时存在

**SID（可变大小）**    二进制格式的SID

ACE可能大于其类型定义的结构，并且可能使用额外空间来存储非结构化数据。最常见的是，它们将这些非结构化数据用于回调ACE类型，例如`AllowedCallback`，该类型定义了一个条件表达式，用于确定在访问检查期间ACE是否应处于活动状态。我们可以使用`ConvertFrom-NtAceCondition` PowerShell命令检查条件表达式生成的数据，如代码清单 5-5所示。

```
PS> ConvertFrom-NtAceCondition 'WIN://TokenId == "XYZ"' | Out-HexDump -ShowAll
          00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  - 0123456789ABCDEF
-----------------------------------------------------------------------------
00000000: 61 72 74 78 F8 1A 00 00 00 57 00 49 00 4E 00 3A  - artx.....W.I.N.:
00000010: 00 2F 00 2F 00 54 00 6F 00 6B 00 65 00 6E 00 49  - ././.T.o.k.e.n.I
00000020: 00 64 00 10 06 00 00 00 58 00 59 00 5A 00 80 00  - .d......X.Y.Z...
```

*代码清单 5-5：解析条件表达式并显示二进制数据*

我们将这些ACE称为*回调ACE*，因为在Windows 8之前，应用程序需要调用`AuthzAccessCheck` API来处理它们。该API接受一个回调函数，该函数会被调用来确定是否在访问检查中包含回调ACE。自Windows 8起，内核访问检查已内置支持代码清单 5-5所示格式的条件ACE，尽管用户应用程序可以自由指定自己的格式并手动处理这些ACE。

ACE标志的主要用途是指定ACE的继承规则。表5-4显示了已定义的ACE标志。

| ACE标志             | 值    | 描述                                                         |
| :----------------- | :---- | :----------------------------------------------------------- |
| ObjectInherit      | 0x1   | ACE可以被对象继承。                                          |
| ContainerInherit   | 0x2   | ACE可以被容器继承。                                          |
| NoPropagateInherit | 0x4   | ACE的继承标志不会传播到子对象。                              |
| InheritOnly        | 0x8   | ACE仅用于继承，不用于访问检查。                              |
| Inherited          | 0x10  | ACE是从父容器继承的。                                        |
| Critical           | 0x20  | ACE是关键的，不能被移除。仅适用于允许类型的ACE。             |
| SuccessfulAccess   | 0x40  | 应对成功访问生成审计事件。                                   |
| FailedAccess       | 0x80  | 应对失败访问生成审计事件。                                   |
| TrustProtected     | 0x40  | 当与AccessFilter ACE一起使用时，此标志防止修改。             |

继承标志仅占用低5位，将高3位留给ACE特定标志。

### 构建与操作安全描述符

既然你已经熟悉了安全描述符的结构，接下来我们看看如何使用PowerShell来构建和操作它们。最常见的需求是查看安全描述符的内容，以了解应用于资源的访问权限。另一个重要的场景是，当你需要构建一个安全描述符来锁定资源时。本书中使用的PowerShell模块旨在让构建和查看安全描述符尽可能简单。

#### 创建新的安全描述符

要创建新的安全描述符，可以使用 `New-NtSecurityDescriptor` 命令。默认情况下，它会创建一个没有所有者、组、DACL或SACL的新 `SecurityDescriptor` 对象。你可以使用命令的参数来添加这些安全描述符的部分，如 代码清单 5-6 所示。




```
PS> $world = Get-NtSid -KnownSid World
PS> $sd = New-NtSecurityDescriptor -Owner $world -Group $world -Type File
PS> $sd | Format-Table
Owner    DACL ACE Count SACL ACE Count Integrity Level
-----    -------------- -------------- ---------------
Everyone NONE           NONE           NONE
```


*代码清单 5-6：创建具有指定所有者的新安全描述符*

我们首先获取 *World* 组的SID。在调用 `New-NtSecurityDescriptor` 创建新安全描述符时，我们使用这个SID来指定其所有者和组。我们还指定了此安全描述符关联的内核对象类型名称；这一步使得后续的一些命令更易于使用。在此例中，我们假设它是一个文件对象的安全描述符。

然后我们显示安全描述符，并将输出格式化为表格。如你所见，所有者字段设置为 Everyone。组值默认不打印，因为它不是那么重要。目前安全描述符中既没有DACL也没有SACL，也没有指定完整性级别。

要添加一些ACE，我们可以使用 `Add-NtSecurityDescriptorAce` 命令。对于普通的ACE，我们需要指定ACE类型、SID和访问掩码。可选地，我们还可以指定ACE标志。代码清单 5-7 中的脚本向我们的新安全描述符添加了一些ACE。




```
❶ PS> $user = Get-NtSid
❷ PS> Add-NtSecurityDescriptorAce $sd -Sid $user -Access WriteData, ReadData
PS> Add-NtSecurityDescriptorAce $sd -KnownSid Anonymous -Access GenericAll
-Type Denied
PS> Add-NtSecurityDescriptorAce $sd -Name "Everyone" -Access ReadData
❸ PS> Add-NtSecurityDescriptorAce $sd -KnownSid World -Access Delete
-Type Audit -Flags FailedAccess
❹ PS> Set-NtSecurityDescriptorIntegrityLevel $sd Low
❺ PS> Set-NtSecurityDescriptorControl $sd DaclAutoInherited, SaclProtected
❻ PS> $sd | Format-Table
Owner    DACL ACE Count SACL ACE Count Integrity Level
-----    -------------- -------------- ---------------
Everyone 3              2              Low

❼ PS> Get-NtSecurityDescriptorControl $sd
DaclPresent, SaclPresent, DaclAutoInherited, SaclProtected

❽ PS> Get-NtSecurityDescriptorDacl $sd | Format-Table
Type    User                         Flags Mask
----    ----                         ----- ----
Allowed GRAPHITE\user                None  00000003
Denied  NT AUTHORITY\ANONYMOUS LOGON None  10000000
Allowed Everyone                     None  00000001

❾ PS> Get-NtSecurityDescriptorSacl $sd | Format-Table
Type           User                                Flags        Mask
----           ----                                -----        ----
Audit          Everyone                            FailedAccess 00010000
MandatoryLabel Mandatory Label\Low Mandatory Level None         00000001
```


*代码清单 5-7：向新安全描述符添加ACE*

我们首先使用 `Get-NtSid` 获取当前用户的SID ❶。我们使用这个SID向DACL添加一个新的允许ACE ❷。我们还通过指定 `Type` 参数为匿名用户添加一个拒绝ACE，然后为 *Everyone* 组添加另一个允许ACE。接着我们修改SACL以添加一个审计ACE ❸，并将强制标签设置为低完整性级别 ❹。为了完成安全描述符的创建，我们设置了 `DaclAutoInherited` 和 `SaclProtected` 控制标志 ❺。

现在我们可以打印刚刚创建的安全描述符的详细信息。显示安全描述符 ❻ 显示DACL现在包含三个ACE和两个SACL，完整性级别为低。我们还显示控制标志 ❼ 以及DACL ❽ 和SACL ❾ 中的ACE列表。

#### 对ACE进行排序

由于访问检查的工作方式，ACL中的ACE有一个规范顺序。例如，所有拒绝ACE应放在任何允许ACE之前，否则系统可能会根据ACE的顺序错误地授予资源访问权限。SRM不强制执行这种规范顺序；它信任任何应用程序在将ACE传递给访问检查之前已正确排序。ACL应按照以下规则对其ACE进行排序：

  1.  所有拒绝类型的ACE必须放在允许类型之前。

  2.  允许ACE必须放在允许对象ACE之前。

  3.  拒绝ACE必须放在拒绝对象ACE之前。

  4.  所有非继承的ACE必须放在设置了继承标志的ACE之前。

在 代码清单 5-7 中，我们在添加允许ACE之后向DACL添加了一个拒绝ACE，这违反了第一条排序规则。我们可以通过使用带有 `CanonicalizeDacl` 参数的 `Edit-NtSecurity` 命令来确保DACL被规范化。我们还可以使用带有 `DaclCanonical` 参数的 `Test-NtSecurityDescriptor` PowerShell命令来测试DACL是否已经是规范的。代码清单 5-8 演示了这两个命令的使用。




```
PS> Test-NtSecurityDescriptor $sd -DaclCanonical
False

PS> Edit-NtSecurityDescriptor $sd -CanonicalizeDacl
PS> Test-NtSecurityDescriptor $sd -DaclCanonical
True

PS> Get-NtSecurityDescriptorDacl $sd | Format-Table
Type    User                         Flags Mask
----    ----                         ----- ----
Denied  NT AUTHORITY\ANONYMOUS LOGON None  10000000
Allowed GRAPHITE\user                None  00000003
Allowed Everyone                     None  00000001
```


*代码清单 5-8：规范化DACL*

如果你比较 代码清单 5-8 中的ACE列表与 代码清单 5-7 中的列表，你会注意到拒绝ACE已从中间移动到ACL的开头。这确保了它将在任何允许ACE之前被处理。

#### 格式化安全描述符

你可以通过 `Format-Table` 命令手动打印安全描述符中的值，但这非常耗时。手动格式化的另一个问题是访问掩码不会被解码，例如，你看到的将是 `00000001` 而不是 `ReadData`。如果能有一种简单的方法来打印安全描述符的详细信息，并根据对象类型进行格式化，那就太好了。这正是 `Format-NtSecurityDescriptor` 的用途。你可以将安全描述符传递给它，该命令会将其打印到控制台。代码清单 5-9 提供了一个示例。




```
PS> Format-NtSecurityDescriptor $sd -ShowAll
Type: File
Control: DaclPresent, SaclPresent

<Owner>
 - Name  : Everyone
 - Sid   : S-1-1-0

<Group>
 - Name  : Everyone
 - Sid   : S-1-1-0

<DACL> (Auto Inherited)
 - Type  : Denied
 - Name  : NT AUTHORITY\ANONYMOUS LOGON
 - SID   : S-1-5-7
 - Mask  : 0x10000000
 - Access: GenericAll
 - Flags : None

 - Type  : Allowed
 - Name  : GRAPHITE\user
 - SID   : S-1-5-21-2318445812-3516008893-216915059-1002
 - Mask  : 0x00000003
 - Access: ReadData|WriteData
 - Flags : None

 - Type  : Allowed
 - Name  : Everyone
 - SID   : S-1-1-0
 - Mask  : 0x00000001
 - Access: ReadData
 - Flags : None

<SACL> (Protected)
 - Type  : Audit
 - Name  : Everyone
 - SID   : S-1-1-0
 - Mask  : 0x00010000
 - Access: Delete
 - Flags : FailedAccess

<Mandatory Label>
 - Type  : MandatoryLabel
 - Name  : Mandatory Label\Low Mandatory Level
 - SID   : S-1-16-4096
 - Mask  : 0x00000001
 - Policy: NoWriteUp
 - Flags : None
```


*代码清单 5-9：显示安全描述符*

我们向 `Format-NtSecurityDescriptor` 传递 `ShowAll` 参数，以确保它显示安全描述符的全部内容；默认情况下，它不会输出 SACL 或较不常见的 ACE（如 `ResourceAttribute`）。请注意，输出的内核对象类型与我们在 代码清单 5-6 中创建安全描述符时指定的 `File` 类型相匹配。指定内核对象类型允许格式化程序打印该类型的解码访问掩码，而不是通用的十六进制值。

输出的下一行显示当前的控制标志。这些标志是根据安全描述符的当前状态动态计算的；稍后，我们将讨论如何更改这些控制标志以改变安全描述符的行为。控制标志之后是所有者 SID、组 SID 和 DACL，它们占据了输出的大部分内容。任何特定于 DACL 的标志都会出现在标题旁边；在这种情况下，这些标志表示我们设置了 `DaclAutoInherited` 标志。接下来，输出按顺序列出 ACL 中的每个 ACE，从 ACE 的类型开始。由于命令知道对象类型，它会打印该类型的解码访问掩码以及十六进制的原始访问掩码。

接下来是 SACL，它显示了我们的单个审计 ACE 以及 `SaclProtected` 标志。最后显示的组件是强制标签。强制标签的访问掩码是强制策略，其解码方式与使用类型特定访问权限的其他 ACE 不同。强制策略可以设置为 表 5-5 中显示的一个或多个位标志。

| 名称        | 值          | 描述                                                         |
| :---------- | :---------- | :----------------------------------------------------------- |
| NoWriteUp   | 0x00000001  | 较低完整性级别的调用者无法写入此资源。                       |
| NoReadUp    | 0x00000002  | 较低完整性级别的调用者无法读取此资源。                       |
| NoExecuteUp | 0x00000004  | 较低完整性级别的调用者无法执行此资源。                       |

默认情况下，`Format-NtSecurityDescriptor` 的输出可能有些冗长。要缩短输出，请指定 `Summary` 参数，它会在保留重要信息的同时尽可能减少数据量。代码清单 5-10 演示了这一点。




```
PS> Format-NtSecurityDescriptor $sd -ShowAll -Summary
<Owner> : Everyone
<Group> : Everyone
<DACL>
<DACL> (Auto Inherited)
NT AUTHORITY\ANONYMOUS LOGON: (Denied)(None)(GenericAll)
GRAPHITE\user: (Allowed)(None)(ReadData|WriteData)
Everyone: (Allowed)(None)(ReadData)
<SACL> (Protected)
Everyone: (Audit)(FailedAccess)(Delete)
<Mandatory Label>
Mandatory Label\Low Mandatory Level: (MandatoryLabel)(None)(NoWriteUp)
```


*代码清单 5-10：以摘要格式显示安全描述符*

我在 第 2 章 中提到，为了便于使用，本书使用的 PowerShell 模块对大多数常见标志使用简单名称，但如果你愿意，也可以显示完整的 SDK 名称（例如，为了与原生代码进行比较）。在使用 `Format-NtSecurityDescriptor` 查看安全描述符内容时，要显示 SDK 名称，请使用 `SDKName` 属性，如 代码清单 5-11 所示。




```
PS> Format-NtSecurityDescriptor $sd -SDKName -SecurityInformation Dacl
Type: File
Control: SE_DACL_PRESENT|SE_SACL_PRESENT|SE_DACL_AUTO_INHERITED|SE_SACL_PROTECTED
<DACL> (Auto Inherited)
 - Type  : ACCESS_DENIED_ACE_TYPE
 - Name  : NT AUTHORITY\ANONYMOUS LOGON
 - SID   : S-1-5-7
 - Mask  : 0x10000000
 - Access: GENERIC_ALL
 - Flags : NONE

 - Type  : ACCESS_ALLOWED_ACE_TYPE
 - Name  : GRAPHITE\user
 - SID   : S-1-5-21-2318445812-3516008893-216915059-1002
 - Mask  : 0x00000003
 - Access: FILE_READ_DATA|FILE_WRITE_DATA
 - Flags : NONE

 - Type  : ACCESS_ALLOWED_ACE_TYPE
 - Name  : Everyone
 - SID   : S-1-1-0
 - Mask  : 0x00000001
 - Access: FILE_READ_DATA
 - Flags : NONE
```


*代码清单 5-11：使用 SDK 名称格式化安全描述符*

File 对象的一个特殊之处在于，它们的访问掩码有两种命名约定，一种用于文件，一种用于目录。你可以通过使用 `Container` 参数请求 `Format-NtSecurityDescriptor` 打印目录版本的访问掩码，或者更一般地，通过将安全描述符对象的 `Container` 属性设置为 `True` 来实现。代码清单 5-12 显示了设置 `Container` 参数对输出的影响。




```
PS> Format-NtSecurityDescriptor $sd -ShowAll -Summary -Container
<Owner> : Everyone
<Group> : Everyone
<DACL>
NT AUTHORITY\ANONYMOUS LOGON: (Denied)(None)(GenericAll)
❶ GRAPHITE\user: (Allowed)(None)(ListDirectory|AddFile)
Everyone: (Allowed)(None)(ListDirectory)
--snip--
```


*代码清单 5-12：将安全描述符格式化为容器*

注意输出行如何从 `ReadData|WriteData` 变为 `ListDirectory|AddFile` ❶，当我们将其格式化为容器时。`File` 类型是 Windows 中唯一具有此行为的对象类型。这对安全性至关重要，因为如果你将目录的安全描述符格式化为文件，或反之，很容易误解文件访问权限。

如果你更喜欢图形界面，可以使用以下 `Show-NtSecurityDescriptor` 命令启动查看器：


```
PS> Show-NtSecurityDescriptor $sd
```


运行该命令应会打开 图 5-8 中所示的对话框。



![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure5-8.webp)

图 5-8：显示安全描述符的图形界面

该对话框汇总了安全描述符的重要数据。顶部是解析为名称的所有者和组 SID，以及安全描述符的完整性级别和强制策略。这些与我们创建安全描述符时指定的值一致。中间是根据所选选项卡显示的 DACL（左侧）或 SACL（右侧）中的 ACE 列表，顶部是 ACL 标志。列表中的每个条目包括 ACE 类型、SID、通用形式的访问掩码以及 ACE 标志。底部是解码后的访问权限。当你在 ACL 列表中选择一个 ACE 时，该列表会填充。

#### 转换相对安全描述符

我们可以使用 `ConvertFrom-NtSecurityDescriptor` 命令将安全描述符对象转换为相对格式的字节数组。然后，我们可以打印其内容以查看底层结构的真实情况，如 代码清单 5-13 所示。




```
PS> $ba = ConvertFrom-NtSecurityDescriptor $sd
PS> $ba | Out-HexDump -ShowAll
          00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  - 0123456789ABCDEF
-----------------------------------------------------------------------------
00000000: 01 00 14 A4 98 00 00 00 A4 00 00 00 14 00 00 00  - ................
00000010: 44 00 00 00 02 00 30 00 02 00 00 00 02 80 14 00  - D.....0.........
00000020: 00 00 01 00 01 01 00 00 00 00 00 01 00 00 00 00  - ................
00000030: 11 00 14 00 01 00 00 00 01 01 00 00 00 00 00 10  - ................
00000040: 00 10 00 00 02 00 54 00 03 00 00 00 01 00 14 00  - ......T.........
00000050: 00 00 00 10 01 01 00 00 00 00 00 05 07 00 00 00  - ................
00000060: 00 00 24 00 03 00 00 00 01 05 00 00 00 00 00 05  - ..$.............
00000070: 15 00 00 00 F4 AC 30 8A BD 09 92 D1 73 DC ED 0C  - ......0.....s...
00000080: EA 03 00 00 00 00 14 00 01 00 00 00 01 01 00 00  - ................
00000090: 00 00 00 01 00 00 00 00 01 01 00 00 00 00 00 01  - ................
000000A0: 00 00 00 00 01 01 00 00 00 00 00 01 00 00 00 00  - ................
```


*代码清单 5-13：将绝对安全描述符转换为相对格式并显示其字节*

我们可以使用 `New-NtSecurityDescriptor` 和 `Byte` 参数将字节数组转换回安全描述符对象：


```
PS> New-NtSecurityDescriptor -Byte $ba
```


作为练习，我将留给你根据本章提供的描述，从十六进制输出中解析出安全描述符的各种结构。为了帮助你入门，图 5-9 标出了主要结构。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure5-9.webp)

图 5-9：相对安全描述符十六进制输出中主要结构的轮廓

你需要参考 ACL 和 SID 结构的布局，手动解码其余部分。

### 安全描述符定义语言

在第2章中，我们讨论了用于表示SID的安全描述符定义语言（SDDL）格式的基础知识。SDDL格式同样可以表示整个安全描述符。由于安全描述符的SDDL版本使用ASCII文本，因此它在一定程度上是可读的，并且与代码清单 5-13中显示的二进制数据不同，它易于复制。由于在Windows中经常看到SDDL字符串的使用，让我们来看看如何用SDDL表示安全描述符以及如何阅读它。

您可以通过指定`ToSddl`参数给`Format-NtSecurityDescriptor`来将安全描述符转换为SDDL格式。这在代码清单 5-14中得到了演示，我们传递了上一节中构建的安全描述符。您也可以使用`New-NtSecurityDescriptor`并指定`ToSddl`参数从SDDL字符串创建安全描述符。




```
PS> $sddl = Format-NtSecurityDescriptor $sd -ToSddl -ShowAll
PS> $sddl
O:WDG:WDD:AI(D;;GA;;;AN)(A;;CCDC;;;S-1-5-21-2318445812-3516008893-216915059-
1002)(A;;CC;;;WD)S:P(AU;FA;SD;;;WD)(ML;;NW;;;LW)
```


*代码清单 5-14：将安全描述符转换为SDDL*

安全描述符的SDDL版本包含四个可选组件。您可以通过查找以下前缀来识别每个组件的开始：

O:  所有者SID

G:  组SID

D:  DACL

S:  SACL

在代码清单 5-15中，我们将代码清单 5-14的输出拆分为其组件，以便更容易阅读。




```
PS> $sddl -split "(?=O:)|(?=G:)|(?=D:)|(?=S:)|(?=\()"
O:WD
G:WD
D:AI
  (D;;GA;;;AN)
  (A;;CCDC;;;S-1-5-21-2318445812-3516008893-216915059-1002)
  (A;;CC;;;WD)
S:P
  (AU;FA;SD;;;WD)
  (ML;;NW;;;LW)
```


*代码清单 5-15：拆分SDDL组件*

前两行表示SDDL格式的所有者和组SID。您可能会注意到，这些看起来不像我们通常看到的SDDL SID，因为它们不以`S-1-`开头。这是因为这些字符串是Windows为众所周知的SID使用的两个字符别名，以减少SDDL字符串的大小。例如，所有者字符串是`WD`，我们可以使用`Get-NtSid`将其转换回完整的SID（代码清单 5-16）。




```
PS> Get-NtSid -Sddl "WD"
Name     Sid
----     ---
Everyone S-1-1-0
```


*代码清单 5-16：将别名转换为名称和SID*

如您所见，`WD`别名代表*Everyone*组。表5-6显示了一些众所周知的SID的别名。您可以在附录B中找到所有支持的SDDL别名的更全面列表。

| SID别名 | 名称                             | SDDL SID     |
| :------ | :------------------------------- | :----------- |
| AU      | NT AUTHORITY\Authenticated Users | S-1-5-11     |
| BA      | BUILTIN\Administrators           | S-1-5-32-544 |
| IU      | NT AUTHORITY\INTERACTIVE         | S-1-5-4      |
| SY      | NT AUTHORITY\SYSTEM              | S-1-5-18     |
| WD      | Everyone                         | S-1-1-0      |

如果SID没有别名，`Format-NtSecurityDescriptor`将以SDDL格式输出SID，如代码清单 5-15所示。即使没有别名的SID也可以由LSASS定义名称。例如，代码清单 5-15中的SID属于当前用户，如代码清单 5-17所示。


```
PS> Get-NtSid -Sddl "S-1-5-21-2318445812-3516008893-216915059-1002" -ToName
GRAPHITE\user
```


*代码清单 5-17：查找SID的名称*

接下来在代码清单 5-15中是对DACL的表示。在`D:`前缀之后，SDDL格式的ACL如下所示：


```
ACLFlags(ACE0)(ACE1)...(ACEn)
```


ACL标志是可选的；DACL设置为`AI`，SACL设置为`P`。这些值映射到安全描述符控制标志，可以是表5-7中的一个或多个字符串。

| ACL标志字符串 | DACL控制标志      | SACL控制标志      |
| :------------ | :----------------- | :----------------- |
| P             | DaclProtected      | SaclProtected      |
| AI            | DaclAutoInherited  | SaclAutoInherited  |
| AR            | DaclAutoInheritReq | SaclAutoInheritReq |

我将在第6章中描述这三个控制标志的用途。每个ACE都括在括号内，由多个以分号分隔的字符串组成，遵循以下通用格式：

```
(Type;Flags;Access;ObjectType;InheritedObjectType;SID[;ExtraData])
```

Type是一个短字符串，映射到一种ACE类型。表5-8显示了这些映射。请注意，SDDL格式不支持某些ACE类型，因此它们未包含在表中。

| ACE类型字符串 | ACE类型              |
| :------------ | :-------------------- |
| A             | 允许                 |
| D             | 拒绝                 |
| AU            | 审核                 |
| AL            | 警报                 |
| OA            | 允许对象             |
| OD            | 拒绝对象             |
| OU            | 审核对象             |
| OL            | 警报对象             |
| XA            | 允许回调             |
| XD            | 拒绝回调             |
| ZA            | 允许回调对象         |
| XU            | 审核回调             |
| ML            | 强制标签             |
| RA            | 资源属性             |
| SP            | 作用域策略ID         |
| TL            | 进程信任标签         |
| FL            | 访问过滤器           |

下一个组件是Flags，它表示ACE标志。代码清单 5-15中SACL的审核条目显示了标志字符串FA，它代表FailedAccess。表5-9显示了其他映射。

| ACE标志字符串 | ACE标志           |
| :------------ | :---------------- |
| OI            | 对象继承          |
| CI            | 容器继承          |
| NP            | 不传播继承        |
| IO            | 仅继承            |
| ID            | 已继承            |
| CR            | 关键              |
| SA            | 成功访问          |
| FA            | 失败访问          |
| TP            | 受信任保护        |

接下来是Access，它表示ACE中的访问掩码。这可以是十六进制（0x1234）、八进制（011064）或十进制（4660）格式的数字，也可以是短访问字符串的列表。如果未指定字符串，则使用空的访问掩码。表5-10显示了访问字符串。

| 访问字符串 | 访问名称       | 访问掩码   |
| :--------- | :------------- | :--------- |
| GR         | 通用读取       | 0x80000000 |
| GW         | 通用写入       | 0x40000000 |
| GX         | 通用执行       | 0x20000000 |
| GA         | 通用所有       | 0x10000000 |
| WO         | 写入所有者     | 0x00080000 |
| WD         | 写入DAC        | 0x00040000 |
| RC         | 读取控制       | 0x00020000 |
| SD         | 删除           | 0x00010000 |
| CR         | 控制访问       | 0x00000100 |
| LO         | 列出对象       | 0x00000080 |
| DT         | 删除树         | 0x00000040 |
| WP         | 写入属性       | 0x00000020 |
| RP         | 读取属性       | 0x00000010 |
| SW         | 自写           | 0x00000008 |
| LC         | 列出子项       | 0x00000004 |
| DC         | 删除子项       | 0x00000002 |
| CC         | 创建子项       | 0x00000001 |

请注意，可用的访问字符串并未覆盖整个访问掩码范围。这是因为SDDL被设计用于表示目录服务对象的掩码，而目录服务对象未定义超出有限范围的访问掩码值。这也是为什么权限名称略显令人困惑的原因；例如，删除子项并不一定映射到任意对象类型对删除子项的概念，您可以在代码清单 5-15中看到，文件类型的特定访问映射到目录服务对象访问，尽管它与Active Directory毫无关系。

为了更好地支持其他类型，SDDL格式为常见的文件和注册表键访问掩码提供了访问字符串，如表5-11所示。如果可用的访问字符串无法表示整个掩码，唯一的选择是将其表示为数字字符串，通常采用十六进制格式。

| 访问字符串 | 访问名称         | 访问掩码    |
| :---------- | :--------------- | :---------- |
| FA          | 文件完全访问     | 0x001F01FF  |
| FX          | 文件执行         | 0x001200A0  |
| FW          | 文件写入         | 0x00120116  |
| FR          | 文件读取         | 0x00120089  |
| KA          | 键完全访问       | 0x000F003F  |
| KR          | 键读取           | 0x00020019  |
| KX          | 键执行           | 0x00020019  |
| KW          | 键写入           | 0x00020006  |

对于与对象ACE一起使用的ObjectType和InheritedObjectType组件，SDDL使用字符串格式来表示GUID。这些GUID可以是任意值。例如，表5-12列出了Active Directory中使用的一些常见GUID。

| GUID                                 | 目录对象 |
| :----------------------------------- | :------- |
| 19195a5a-6da0-11d0-afd3-00c04fd930c9 | 域       |
| bf967a86-0de6-11d0-a285-00aa003049e2 | 计算机   |
| bf967aba-0de6-11d0-a285-00aa003049e2 | 用户     |
| bf967a9c-0de6-11d0-a285-00aa003049e2 | 组       |

以下是一个设置了ObjectType的AllowedObject ACE的示例ACE字符串：

```
(OA;;CC;2f097591-a34f-4975-990f-00f0906b07e0;;WD)
```

在ACE的InheritedObjectType组件之后是SID。如本章前面所述，如果它是众所周知的SID，则可以是短别名；否则，可以是完整的SDDL格式。

在最后一个组件中（对于大多数ACE类型是可选的），如果使用回调ACE，则可以指定条件表达式；如果使用ResourceAttribute ACE，则可以指定安全属性。条件表达式定义了一个布尔表达式，用于比较令牌安全属性的值。在评估时，表达式的结果应为真或假。我们在代码清单 5-5中看到了一个简单示例：WIN://TokenId == "XYZ"，它将安全属性WIN://TokenId的值与字符串值XYZ进行比较，如果相等则评估为真。SDDL表达式语法对于要引用的安全属性有四种不同的属性名称格式：

**简单**    用于本地安全属性；例如，WIN://TokenId

**设备**    用于设备声明；例如，@Device.ABC

**用户**    用于用户声明；例如，@User.XYZ

**资源**    用于资源属性；例如，@Resource.QRS

条件表达式中的比较值也可以接受多种不同类型。当从SDDL转换为安全描述符时，条件表达式将被解析，但由于此时安全属性的类型未知，因此无法对值的类型进行验证。表5-13展示了每种条件表达式类型的示例。

| 类型                        | 示例                                                         |
| :-------------------------- | :----------------------------------------------------------- |
| 数字                        | 十进制：100, -100；八进制：0100；十六进制：0x100             |
| 字符串                      | "ThisIsAString"                                              |
| 完全限定二进制名称          | {"O=MICROSOFT CORPORATION, L=REDMOND, S=WASHINGTON",1004}    |
| SID                         | SID(BA), SID(S-1-0-0)                                        |
| 八位字节字符串              | #0011223344                                                  |

然后，语法定义运算符来评估表达式，从表5-14中的一元运算符开始。

| 运算符                           | 描述                                                         |
| :------------------------------- | :----------------------------------------------------------- |
| Exists ATTR                      | 检查安全属性ATTR是否存在                                     |
| Not_Exists ATTR                  | Exists的反向操作                                             |
| Member_of {SIDLIST}              | 检查令牌组是否包含SIDLIST中的所有SID                         |
| Not_Member_of {SIDLIST}          | Member_of的反向操作                                          |
| Device_Member_of {SIDLIST}       | 检查令牌设备组是否包含SIDLIST中的所有SID                     |
| Not_Device_Member_of {SIDLIST}   | Device_Member_of的反向操作                                   |
| Member_of_Any {SIDLIST}          | 检查令牌组是否包含SIDLIST中的任意SID                         |
| Not_Member_of_Any {SIDLIST}      | Not_Member_of_Any的反向操作                                  |
| Device_Member_of_Any {SIDLIST}   | 检查令牌设备组是否包含SIDLIST中的任意SID                     |
| Not_Device_Member_of_Any {SIDLIST} | Device_Member_of_Any的反向操作                               |
| !(EXPR)                          | 表达式的逻辑非运算                                           |

在表5-14中，ATTR是要测试的属性名称，SIDLIST是用花括号{}括起来的SID值列表，EXPR是另一个条件子表达式。表5-15展示了语法定义的中缀运算符。

| 运算符                        | 描述                                                         |
| :---------------------------- | :----------------------------------------------------------- |
| ATTR Contains VALUE           | 检查安全属性是否包含该值                                     |
| ATTR Not_Contains VALUE       | Contains的反向操作                                           |
| ATTR Any_of {VALUELIST}       | 检查安全属性是否包含值列表中的任意值                         |
| ATTR Not_Any_of {VALUELIST}   | Any_of的反向操作                                             |
| ATTR == VALUE                 | 检查安全属性是否等于该值                                     |
| ATTR != VALUE                 | 检查安全属性是否不等于该值                                   |
| ATTR < VALUE                  | 检查安全属性是否小于该值                                     |
| ATTR <= VALUE                 | 检查安全属性是否小于或等于该值                               |
| ATTR > VALUE                  | 检查安全属性是否大于该值                                     |
| ATTR >= VALUE                 | 检查安全属性是否大于或等于该值                               |
| EXPR && EXPR                  | 两个表达式之间的逻辑与运算                                   |
| EXPR \|\| EXPR                | 两个表达式之间的逻辑或运算                                   |

在表5-15中，VALUE可以是表5-13中的单个值，也可以是用花括号括起来的值列表。Any_of和Not_Any_of运算符仅适用于列表，且条件表达式在SDDL ACE中必须始终放在括号内。例如，如果您想在AccessCallback ACE中使用代码清单 5-5中展示的条件表达式，ACE字符串将如下所示：


```
(ZA;;GA;;;WD;(WIN://TokenId == "XYZ"))
```


最后一个组件表示ResourceAttribute ACE的安全属性。其一般格式如下：


```
"AttrName",AttrType,AttrFlags,AttrValue(,AttrValue...)
```


AttrName值是安全属性的名称，AttrFlags是表示安全属性标志的十六进制数，AttrValue是一个或多个特定于AttrType的值，用逗号分隔。AttrType是一个短字符串，指示安全属性中包含的数据类型。表5-16显示了定义的字符串及示例。

| 属性类型 | 类型名称   | 示例值                                               |
| :------------- | :---------- | :-------------------------------------------------- |
| TI             | Int64       | 十进制：100, -100；八进制：0100；十六进制：0x100 |
| TU             | UInt64      | 十进制：100；八进制：0100；十六进制：0x100       |
| TS             | String      | "XYZ"                                               |
| TD             | SID         | BA, S-1-0-0                                         |
| TB             | Boolean     | 0, 1                                                |
| RX             | OctetString | #0011223344                                         |

例如，以下SDDL字符串表示一个名为Classification的ResourceAttribute ACE。它包含两个字符串值TopSecret和MostSecret，并设置了CaseSensitive和NonInheritable标志：


```
S:(RA;;;;;WD;("Classification",TS,0x3,"TopSecret","MostSecret"))
```


代码清单 5-15中最后一个需要定义的是SACL。其结构与DACL相同，但支持的ACE类型有所不同。如果尝试在特定ACL中使用不允许的类型，解析字符串将失败。在代码清单 5-15的SACL示例中，唯一的ACE是强制标签。强制标签ACE有其自己的访问字符串来表示强制策略，如表5-17所示。

| 访问字符串 | 访问名称   | 访问掩码 |
| :------------ | :------------ | :---------- |
| NX            | 禁止执行提升 | 0x00000004  |
| NR            | 禁止读取提升 | 0x00000002  |
| NW            | 禁止写入提升 | 0x00000001  |

SID表示强制标签的完整性级别；同样，定义了特殊的SID别名。表5-18中列出的内容之外的任何内容都需要表示为完整的SID。

| SID别名 | 名称                       | SDDL SID     |
| :-------- | :------------------------- | :----------- |
| LW        | 低完整性级别               | S-1-16-4096  |
| ME        | 中完整性级别               | S-1-16-8192  |
| MP        | 中高完整性级别             | S-1-16-8448  |
| HI        | 高完整性级别               | S-1-16-12288 |
| SI        | 系统完整性级别             | S-1-16-16384 |

SDDL格式并不能保留安全描述符中可存储的所有信息。例如，SDDL格式无法表示OwnerDefaulted或GroupDefaulted控制标志，因此这些信息会被丢弃。SDDL也不支持某些ACE类型，因此我在表5-8中省略了这些类型。

如前所述，如果在将安全描述符转换为SDDL时遇到不支持的ACE类型，转换过程将失败。为解决此问题，ConvertFrom-NtSecurityDescriptor PowerShell命令可以将相对格式的安全描述符转换为base64，如代码清单 5-18所示。使用base64可以保留完整的安全描述符，并便于复制。




```
PS> ConvertFrom-NtSecurityDescriptor $sd -AsBase64 -InsertLineBreaks
AQAUpJgAAACkAAAAFAAAAEQAAAACADAAAgAAAAKAFAAAAAEAAQEAAAAAAAEAAAAAEQAUAAEAAAAB
AQAAAAAAEAAQAAACAFQAAwAAAAEAFAAAAAAQAQEAAAAAAAUHAAAAAAAkAAMAAAABBQAAAAAABRUA
AAD0rDCKvQmS0XPc7QzqAwAAAAAUAAEAAAABAQAAAAAAAQAAAAABAQAAAAAAAQAAAAABAQAAAAAA
AQAAAAA=
```


*代码清单 5-18：将安全描述符转换为base64表示*

要检索安全描述符，可以向New-NtSecurityDescriptor传递Base64参数。

### 实际示例

让我们用一些实际示例来结束本章，这些示例会用到你在这里学到的命令。

#### 手动解析二进制SID

PowerShell模块附带了一些命令，可用于解析以各种形式结构化的SID。其中一种形式是原始字节数组。你可以使用 `ConvertFrom-NtSid` 命令将现有SID转换为字节数组：

```
PS> $ba = ConvertFrom-NtSid -Sid "S-1-1-0"
```

你也可以使用 `Get-NtSid` 命令的 `Byte` 参数将字节数组转换回SID，如下所示。模块将解析字节数组并返回SID：

```
PS> Get-NtSid -Byte $ba
```

尽管PowerShell可以为你执行这些转换，但你会发现理解数据在底层是如何结构化的很有价值。例如，你可能会识别出解析SID不正确的代码，这可能导致内存损坏；通过这一发现，你可能会找到安全漏洞。

学习解析二进制结构的最佳方法是编写一个解析器，正如我们在代码清单 5-19中所做的那样。

```
❶ PS> $sid = Get-NtSid -SecurityAuthority Nt -RelativeIdentifier 100, 200, 300
PS> $ba = ConvertFrom-NtSid -Sid $sid
PS> $ba | Out-HexDump -ShowAll
          00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  - 0123456789ABCDEF
-----------------------------------------------------------------------------
00000000: 01 03 00 00 00 00 00 05 64 00 00 00 C8 00 00 00  -........d.......
00000010: 2C 01 00 00                                      - ,...

PS> $stm = [System.IO.MemoryStream]::new($ba)
❷ PS> $reader = [System.IO.BinaryReader]::new($stm)

PS> $revision = $reader.ReadByte()
❸ PS> if ($revision -ne 1) {
    throw "Invalid SID revision"
}

❹ PS> $rid_count = $reader.ReadByte()
❺ PS> $auth = $reader.ReadBytes(6)
PS> if ($auth.Length -ne 6) {
    throw "Invalid security authority length"
}

PS> $rids = @()
❻ PS> while($rid_count -gt 0) {
    $rids += $reader.ReadUInt32()
    $rid_count--
}

❼ PS> $new_sid = Get-NtSid -SecurityAuthorityByte $auth -RelativeIdentifier $rids
PS> $new_sid -eq $sid
True
```

*代码清单 5-19：手动解析二进制SID*

为了演示目的，我们首先创建一个任意的SID并将其转换为字节数组❶。但通常情况下，你会通过其他方式接收要解析的SID，例如从进程的内存中。我们还将SID打印为十六进制。（如果你参考图5-1中显示的SID结构，你可能已经能够识别出它的各个组成部分。）

接下来，我们创建一个 `BinaryReader` 来以结构化形式解析字节数组❷。使用读取器，我们首先检查修订值是否设置为1❸；如果不是，则抛出错误。结构中的下一个是RID计数（一个字节）❹，然后是6字节的安全机构❺。`ReadBytes` 方法可能返回较短的读取结果，因此你需要检查是否读取了全部六个字节。

我们现在进入一个循环，从二进制结构中读取RID并将它们追加到数组中❻。接下来，使用安全机构和RID，我们可以运行 `Get-NtSid` 来构造一个新的SID对象❼，并验证新SID与我们开始时的一致。

此清单为你提供了一个如何使用PowerShell手动解析SID（实际上，任何二进制结构）的示例。如果你有冒险精神，你可以为二进制安全描述符格式实现自己的解析器，但这超出了本书的范围。使用 `New-NtSecurityDescriptor` 命令来为你执行解析会更简单。

#### 枚举SID

LSASS服务没有提供公开的方法来查询它所知道的每个SID到名称的映射。虽然微软官方文档提供了已知SID的列表，但这些列表并不总是最新的，并且不会包括特定于计算机或企业网络的SID。然而，我们可以尝试使用暴力枚举来枚举映射。代码清单 5-20定义了一个函数 `Get-AccountSids`，用于暴力枚举LSASS具有名称的SID列表。

```
PS> function Get-AccountSids {
    param(
        [parameter(Mandatory)]
      ❶ $BaseSid,
        [int]$MinRid = 0,
        [int]$MaxRid = 256
    )

    $i = $MinRid

    while($i -lt $MaxRid) {
        $sid = Get-NtSid -BaseSid $BaseSid -RelativeIdentifier $i
        $name = Get-NtSidName $sid
        ❷ if ($name.Source -eq "Account") {
            [PSCustomObject]@{
                Sid = $sid;
                Name = $name.QualifiedName;
                Use = $name.NameUse
            }
        }
        $i++
    }
}

❸ PS> $sid = Get-NtSid -SecurityAuthority Nt
PS> Get-AccountSids -BaseSid $sid
Sid          Name                   Use
----         ----                   ---
S-1-5-1      NT AUTHORITY\DIALUP    WellKnownGroup
S-1-5-2      NT AUTHORITY\NETWORK   WellKnownGroup
S-1-5-3      NT AUTHORITY\BATCH     WellKnownGroup
--snip--

❹ PS> $sid = Get-NtSid -BaseSid $sid -RelativeIdentifier 32
PS> Get-AccountSids -BaseSid $sid -MinRid 512 -MaxRid 1024
Sid          Name                   Use
----         ----                   ---
S-1-5-32-544 BUILTIN\Administrators Alias
S-1-5-32-545 BUILTIN\Users          Alias
S-1-5-32-546 BUILTIN\Guests         Alias
--snip--
```

*代码清单 5-20：暴力枚举已知SID*

该函数接受一个基础SID和要测试的RID值范围❶。然后，它创建列表中的每个SID并查询其名称。如果名称的来源是 `Account`，这表示名称是从LSASS检索的，我们输出SID的详细信息❷。

为了测试该函数，我们使用包含Nt机构但没有RID的基础SID调用它❸。我们获取从LSASS检索的名称和SID列表。请注意，输出中的SID不是你可能期望的域SID，而是 `WellKnownGroup` SID。就我们的目的而言，`WellKnownGroup`、`Group` 和 `Alias` 之间的区别并不重要；它们都是组。

接下来，我们尝试暴力枚举 *BUILTIN* 域SID❹。在这种情况下，我们根据对有效范围的已有知识更改了RID范围，但你可以随意尝试任何其他范围。请注意，你可以通过检查返回对象中的 `NameUse` 属性并在其值为 `Domain` 时调用 `Get-AccountSids` 来自动化搜索。我把这留作读者的练习。

### 本章小结

本章开篇深入探讨了安全描述符的结构。我们详细介绍了其二进制结构，如SID，并考察了ACL以及构成DACL和SACL的访问控制项(Access Control Entry, ACE)。随后，我们讨论了绝对安全描述符与相对安全描述符之间的差异，以及这两种格式存在的原因。

接下来，我们探索了如何使用 `New-NtSecurityDescriptor` 和 `Add-NtSecurityDescriptorAce` 命令来创建和修改安全描述符，使其包含我们所需的任意条目。我们还了解了如何通过 `Format-NtSecurityDescriptor` 命令以便捷的形式显示安全描述符。

最后，我们涵盖了用于表示安全描述符的 SDDL 格式。我们讨论了如何表示各种类型的安全描述符值（如 ACE），以及如何自行编写这些值。本章尚未涉及的一些任务包括如何从内核对象查询安全描述符以及如何分配新的安全描述符。我们将在下一章中讨论这些主题。

## 6. 读取与分配安全描述符

在上一章中，我们讨论了构成安全描述符的各种结构。你还学习了如何在PowerShell中操作安全描述符，以及如何使用SDDL格式表示它们。在本章中，我们将讨论如何从内核对象读取安全描述符，以及向这些对象分配安全描述符这一更为复杂的过程。

我们将重点讨论分配给内核对象的安全描述符。然而，如第 5 章“绝对与自相对安全描述符”中所述，也可以将安全描述符存储在持久性存储中，例如文件或注册表键值中。在这种情况下，安全描述符必须以相对格式存储，并在我们将其转换为可检查的格式之前，作为字节流读取。

### 读取安全描述符

要访问内核对象的安全描述符，可以调用 `NtQuerySecurityObject` 系统调用。该系统调用接受一个指向内核对象的句柄，以及一组描述您希望访问的安全描述符组件的标志。`SecurityInformation` 枚举代表了这些标志。

表 6-1 列出了最新版本 Windows 中可用的标志，以及这些信息在安全描述符中的位置和查询所需的句柄访问权限。

| 标志名称           | 描述                                                         | 位置    | 所需的句柄访问权限               |
| :----------------- | :----------------------------------------------------------- | :------ | :------------------------------- |
| Owner              | 查询所有者 SID。                                             | Owner   | ReadControl                      |
| Group              | 查询组 SID。                                                 | Group   | ReadControl                      |
| Dacl               | 查询 DACL。                                                  | DACL    | ReadControl                      |
| Sacl               | 查询 SACL（仅审计 ACE）。                                    | SACL    | AccessSystemSecurity             |
| Label              | 查询强制标签。                                               | SACL    | ReadControl                      |
| Attribute          | 查询系统资源属性。                                           | SACL    | ReadControl                      |
| Scope              | 查询作用域策略 ID。                                          | SACL    | ReadControl                      |
| ProcessTrustLabel  | 查询进程信任标签。                                           | SACL    | ReadControl                      |
| AccessFilter       | 查询访问过滤器。                                             | SACL    | ReadControl                      |
| Backup             | 查询除进程信任标签和访问过滤器之外的所有内容。               | 全部    | ReadControl 和 AccessSystemSecurity |

读取大部分此类信息仅需 `ReadControl` 访问权限，但 SACL 中的审计 ACE 除外，它们需要 `AccessSystemSecurity` 访问权限。（对于存储在 SACL 中的其他 ACE，`ReadControl` 访问权限已足够。）

获取 `AccessSystemSecurity` 访问权限的唯一方法是先启用 `SeSecurityPrivilege` 特权，然后在打开内核对象时显式请求该访问权限。代码清单 6-1 展示了这一行为。您必须以管理员身份运行这些命令。




```
PS> $dir = Get-NtDirectory "\BaseNamedObjects" -Access AccessSystemSecurity
Get-NtDirectory : (0xC0000061) - A required privilege is not held by
the client.
--snip--

PS> Enable-NtTokenPrivilege SeSecurityPrivilege
PS> $dir = Get-NtDirectory "\BaseNamedObjects" -Access AccessSystemSecurity
PS> $dir.GrantedAccess
AccessSystemSecurity
```


*代码清单 6-1：请求 AccessSystemSecurity 访问权限并启用 SeSecurityPrivilege*

我们首次尝试以 `AccessSystemSecurity` 访问权限打开 BNO 目录时失败，因为我们没有所需的 `SeSecurityPrivilege` 特权。接下来，我们启用该特权并再次尝试。这次我们成功打开了目录，打印其 `GrantedAccess` 参数确认我们已获得 `AccessSystemSecurity` 访问权限。

Windows 的设计者为何决定用 `SeSecurityPrivilege` 来保护审计信息的读取，这一点并不完全清楚。虽然我们应当将修改和删除审计信息视为特权操作，但读取这些信息没有明显的理由需要特权。不幸的是，我们只能接受这种设计。

您可以使用 `Get-NtSecurityDescriptor` PowerShell 命令查询对象的安全描述符，该命令调用 `NtQuerySecurityObject`。系统调用以相对格式返回安全描述符作为字节数组，PowerShell 命令将其解析为 `SecurityDescriptor` 对象并返回给调用者。该命令接受一个对象或您要查询的资源的路径，如代码清单 6-2所示，该清单显示了 BNO 目录的安全描述符。




```
PS> Use-NtObject($d = Get-NtDirectory "\BaseNamedObjects" -Access 
ReadControl) {
    Get-NtSecurityDescriptor -Object $d
}
Owner                  DACL ACE Count SACL ACE Count Integrity Level
-----                  -------------- -------------- ---------------
BUILTIN\Administrators 4              1              Low
```


*代码清单 6-2：查询 BNO 目录的安全描述符*

在此，我们以 `ReadControl` 访问权限打开 BNO 目录，然后使用 `Get-NtSecurityDescriptor` 从打开的 `Directory` 对象中查询安全描述符。

默认情况下，`Get-NtSecurityDescriptor` 命令查询的是所有者、组、DACL、强制标签和进程信任标签。如果你想查询其他任何字段（或省略返回的部分信息），需要通过 `SecurityInformation` 参数来指定，该参数接受 表6-1 中的值。例如，代码清单 6-3 使用路径而非对象，并且仅请求所有者字段。




```
PS> Get-NtSecurityDescriptor "\BaseNamedObjects" -SecurityInformation Owner
Owner                  DACL ACE Count SACL ACE Count Integrity Level
-----                  -------------- -------------- ---------------
BUILTIN\Administrators NONE           NONE           NONE
```


*代码清单 6-3：查询BNO目录的所有者*

在输出中，你可以看到只有“所有者”列包含有效信息；其他所有列现在都显示为 `NONE`，这表示没有值存在，因为我们没有请求这些信息。

### 分配安全描述符

读取安全描述符相对简单；你只需具备对内核资源的正确访问权限，并能解析从 `NtQuerySecurityObject` 系统调用返回的相对安全描述符格式。而分配安全描述符则是一个更为复杂的操作。分配给资源的安全描述符取决于多个因素：

- 资源是否正在被创建？
- 创建者是否在创建时指定了安全描述符？
- 新资源是否存储在容器中，例如目录或注册表键？
- 新资源是容器还是对象？
- 父级或当前安全描述符上设置了哪些控制标志？
- 分配安全描述符的用户是谁？
- 现有安全描述符包含哪些 ACE？
- 正在分配的内核对象类型是什么？

从列表中可以看出，这个过程涉及许多变量，这也是 Windows 安全如此复杂的主要原因之一。

我们可以在资源创建时或通过打开的句柄来分配其安全性。让我们先处理更复杂的情况：创建时的分配。

#### 在资源创建期间分配安全描述符

创建新资源时，内核需要为其分配一个安全描述符。此外，根据所创建资源的类型，存储安全描述符的方式也会有所不同。例如，对象管理器资源是临时性的，因此内核会将其安全描述符存储在内存中。相比之下，文件系统驱动程序的安全描述符必须持久化到磁盘；否则，重启计算机后它就会消失。

尽管存储安全描述符的机制可能不同，但内核在处理它时仍必须遵循许多通用流程，例如强制执行继承规则。为了提供一致的实现，内核导出了几个 API，用于计算要分配给新资源的安全描述符。其中最常用的 API 是 `SeAssignSecurityEx`，它接受以下七个参数：

**创建者安全描述符**    一个可选的安全描述符，作为新分配安全描述符的基础

**父级安全描述符**    新资源父对象的可选安全描述符

**对象类型**    一个可选的 GUID，表示正在创建的对象类型

**容器**    一个布尔值，指示新资源是否为容器

**自动继承**    一组位标志，定义自动继承行为

**令牌**    一个句柄，指向用作创建者身份的令牌

**通用映射**    从通用访问权限到内核类型特定访问权限的映射

基于这些参数，API 会计算出一个新的安全描述符并返回给调用者。通过研究这些参数如何交互，我们可以理解内核如何为新对象分配安全描述符。

让我们以 Mutant 对象为例来考虑这个分配过程。（一旦 PowerShell 实例关闭，该对象将被删除，确保我们不会意外留下不必要的文件或注册表键。）表 6-2 提供了一个示例，展示了我们如何使用 `NtCreateMutant` 创建新 Mutant 对象时如何设置这些参数。

| 参数                     | 设置值                                                       |
| :----------------------- | :----------------------------------------------------------- |
| 创建者安全描述符         | 对象属性结构中 `SecurityDescriptor` 字段的值。               |
| 父级安全描述符           | 父目录的安全描述符；对于未命名的 Mutant，不设置。            |
| 对象类型                 | 不设置。                                                     |
| 容器                     | 设置为 False，因为 Mutant 不是容器。                         |
| 自动继承                | 如果父级安全描述符的控制标志包含 `DaclAutoInherited` 标志，且创建者 DACL 缺失或没有创建者安全描述符，则设置为 `AutoInheritDacl`；如果父级安全描述符的控制标志包含 `SaclAutoInherited` 标志，且创建者 SACL 缺失或没有创建者安全描述符，则设置为 `AutoInheritSacl`。 |
| 令牌                     | 如果调用者正在模拟，则设置为模拟令牌；否则，设置为调用者进程的主令牌。 |
| 通用映射                 | 设置为 Mutant 类型的通用映射。                               |

你可能想知道为什么表6-2中没有设置对象类型。API支持该参数，但对象管理器和I/O管理器都不使用它。其主要目的是让Active Directory控制继承，因此我们将在本章稍后的“确定对象继承”一节中单独讨论。

表6-2仅显示了两种可能的自动继承标志，但我们可以向API传递许多其他标志。表6-3列出了可用的自动继承标志，其中一些将在本章的示例中遇到。

| 标志名称                  | 描述                                                         |
| :------------------------ | :----------------------------------------------------------- |
| DaclAutoInherit            | 自动继承DACL。                                               |
| SaclAutoInherit            | 自动继承SACL。                                               |
| DefaultDescriptorForObject | 为新安全描述符使用默认安全描述符。                           |
| AvoidPrivilegeCheck        | 设置强制标签或SACL时不检查特权。                             |
| AvoidOwnerCheck            | 避免检查所有者对当前令牌是否有效。                           |
| DefaultOwnerFromParent     | 从父安全描述符复制所有者SID。                                |
| DefaultGroupFromParent     | 从父安全描述符复制组SID。                                    |
| MaclNoWriteUp              | 使用NoWriteUp策略自动继承强制标签。                          |
| MaclNoReadUp               | 使用NoReadUp策略自动继承强制标签。                           |
| MaclNoExecuteUp            | 使用NoExecuteUp策略自动继承强制标签。                        |
| AvoidOwnerRestriction      | 忽略父安全描述符对新DACL施加的限制。                         |
| ForceUserMode              | 强制执行所有检查，如同从用户模式调用（仅适用于内核调用者）。 |

SeAssignSecurityEx最重要的参数是分配给父安全描述符和创建者安全描述符的值。让我们通过几种这两个安全描述符参数的配置来理解不同的结果。

##### 仅设置创建者安全描述符

在我们将考虑的第一种配置中，我们调用NtCreateMutant，并将对象属性的SecurityDescriptor字段设置为有效的安全描述符。如果新的Mutant对象未命名，它将在没有父目录的情况下创建，相应的父安全描述符也不会被设置。如果没有父安全描述符，自动继承标志也不会被设置。

让我们测试此行为，以查看创建新Mutant对象时生成的安全描述符。我们不直接创建对象，而是使用SeAssignSecurityEx的用户模式实现，*NTDLL*将其导出为RtlNewSecurityObjectEx。我们可以使用New-NtSecurityDescriptor PowerShell命令访问RtlNewSecurityObjectEx，如代码清单 6-4所示。




```
PS> $creator = New-NtSecurityDescriptor -Type Mutant
❶ PS> Add-NtSecurityDescriptorAce $creator -Name "Everyone" -Access GenericRead 
❷ PS> Format-NtSecurityDescriptor $creator 
Type: Mutant
Control: DaclPresent
<DACL>
 - Type  : Allowed
 - Name  : Everyone
 - SID   : S-1-1-0
 - Mask  : 0x80000000
 - Access: GenericRead
 - Flags : None

PS> $token = Get-NtToken -Effective -Pseudo
❸ PS> $sd = New-NtSecurityDescriptor -Token $token -Creator $creator 
-Type Mutant 
PS> Format-NtSecurityDescriptor $sd
Type: Mutant
Control: DaclPresent
❹ <Owner>
 - Name  : GRAPHITE\user
 - Sid   : S-1-5-21-2318445812-3516008893-216915059-1002

❺ <Group>
 - Name  : GRAPHITE\None
 - Sid   : S-1-5-21-2318445812-3516008893-216915059-513

<DACL>
- Type  : Allowed
- Name  : Everyone
- SID   : S-1-1-0
- Mask  : 0x00020001
❻ - Access: ModifyState|ReadControl
- Flags : None
```


*代码清单 6-4：从创建者安全描述符创建新安全描述符*

我们首先构建一个仅包含单个ACE的创建者安全描述符，授予*Everyone*组GenericRead访问权限❶。通过格式化安全描述符❷，我们可以确认格式化输出中仅存在DACL。接下来，使用创建者安全描述符，我们调用New-NtSecurityDescriptor命令❸，传递当前有效令牌，并将最终对象类型指定为Mutant。此对象类型决定了通用映射。最后，我们格式化新的安全描述符。

您可能会注意到，在创建过程中安全描述符发生了变化：它获得了Owner❹和Group❺值，并且指定的访问掩码从GenericRead更改为ModifyState|ReadControl❻。

让我们首先考虑这些新的所有者和组值来自何处。当我们未指定Owner或Group值时，创建过程会从提供的令牌的Owner和PrimaryGroup SID中复制这些值。我们可以通过使用Format-NtToken PowerShell命令检查Token对象的属性来确认这一点，如代码清单 6-5所示。




```
PS> Format-NtToken $token -Owner -PrimaryGroup
OWNER INFORMATION
----------------
Name          Sid
----          ---
GRAPHITE\user S-1-5-21-2318445812-3516008893-216915059-1002

PRIMARY GROUP INFORMATION
-------------------------
Name          Sid
----          ---
GRAPHITE\None S-1-5-21-2318445812-3516008893-216915059-513
```


*代码清单 6-5：显示当前有效令牌的Owner和PrimaryGroup SID*

如果你将代码清单 6-5中的输出与代码清单 6-4中的安全描述符值进行比较，你会发现所有者和组SID是匹配的。

在第4章中，你了解到无法在令牌上设置任意的所有者SID；该值必须是用户的SID或标记有Owner标志的SID。你可能会想：既然令牌的SID被用来设置安全描述符的默认所有者，我们能否利用这种行为在安全描述符中指定任意的所有者SID呢？让我们来检查一下。在代码清单 6-6中，我们首先将安全描述符设置为*SYSTEM*用户的SID，然后尝试再次创建安全描述符。




```
PS> Set-NtSecurityDescriptorOwner $creator -KnownSid LocalSystem
PS> New-NtSecurityDescriptor -Token $token -Creator $creator -Type Mutant
New-NtSecurityDescriptor : (0xC000005A) - Indicates a particular Security ID
may not be assigned as the owner of an object.
```


*代码清单 6-6：将* SYSTEM *用户设置为Mutant对象的安全描述符所有者*

这次，创建操作以异常失败，状态码为STATUS_INVALID_OWNER。这是因为API会检查所分配的所有者SID是否对提供的令牌有效。它不必是Token对象的所有者SID，但必须是用户的SID或设置了Owner标志的组SID。

只有当用于创建安全描述符的令牌启用了SeRestorePrivilege特权时，你才能设置任意的所有者SID。请注意，该令牌不一定属于SeAssignSecurityEx API的调用者。你还可以通过指定AvoidOwnerCheck自动继承标志来禁用所有者检查；然而，内核在创建新对象时绝不会指定此标志，因此它总是会强制执行所有者检查。

这并不是说普通用户就没有办法设置不同的所有者。然而，你发现的任何设置任意所有者的方法都是安全漏洞，微软很可能会修复它。此类漏洞的一个例子是CVE-2018-0748，它允许用户在创建文件时设置任意的所有者。用户必须通过本地文件系统共享来创建文件，从而导致所有者检查被绕过。

组SID的值没有限制，因为组不参与访问检查。然而，对SACL有相关限制。如果你在创建者安全描述符的SACL中指定了任何审计ACE，内核将要求SeSecurityPrivilege。

还记得我们创建安全描述符时，访问掩码发生了变化吗？这是因为安全描述符分配过程使用对象类型的通用映射信息，将访问掩码中的所有通用访问权限映射为类型特定的访问权限。在这种情况下，Mutant类型的GenericRead映射将访问掩码转换为ModifyState|ReadControl。此规则有一个例外：如果ACE设置了InheritOnly标志，则通用访问权限不会被映射。稍后当我们讨论继承时，你会理解这个例外存在的原因。

我们可以通过使用New-NtSecurityDescriptor创建一个未命名的Mutant对象来确认这种映射行为，如代码清单 6-7所示。




```
PS> $creator = New-NtSecurityDescriptor -Type Mutant
PS> Add-NtSecurityDescriptorAce $creator -Name "Everyone" -Access GenericRead
PS> Use-NtObject($m = New-NtMutant -SecurityDescriptor $creator) {
    Format-NtSecurityDescriptor $m
}
Type: Mutant
Control: DaclPresent
<Owner>
 - Name  : GRAPHITE\user
 - Sid   : S-1-5-21-2318445812-3516008893-216915059-1002

<Group>
 - Name  : GRAPHITE\None
 - Sid   : S-1-5-21-2318445812-3516008893-216915059-513

<DACL>
 - Type  : Allowed
 - Name  : Everyone
 - SID   : S-1-1-0
 - Mask  : 0x00020001
 - Access: ModifyState|ReadControl
 - Flags : None
```


*代码清单 6-7：通过创建Mutant对象验证安全描述符分配规则*

如你所见，输出的安全描述符与代码清单 6-4中创建的相同。

##### 设置既无创建者也无父级安全描述符

让我们探讨另一个简单的情况。在此场景中，创建者和父级安全描述符均未设置。这种情况对应于调用NtCreateMutant时不带名称或未指定SecurityDescriptor字段。测试脚本比之前的更简单，如代码清单 6-8所示。




```
PS> $token = Get-NtToken -Effective -Pseudo
❶ PS> $sd = New-NtSecurityDescriptor -Token $token -Type Mutant
PS> Format-NtSecurityDescriptor $sd -HideHeader
❷ <Owner>
 - Name  : GRAPHITE\user
 - Sid   : S-1-5-21-2318445812-3516008893-216915059-1002

<Group>
 - Name  : GRAPHITE\None
 - Sid   : S-1-5-21-2318445812-3516008893-216915059-513

❸ <DACL>
 - Type  : Allowed
 - Name  : GRAPHITE\user
 - SID   : S-1-5-21-2318445812-3516008893-216915059-1002
 - Mask  : 0x001F0001
 - Access: Full Access
 - Flags : None

 - Type  : Allowed
 - Name  : NT AUTHORITY\SYSTEM
 - SID   : S-1-5-18
 - Mask  : 0x001F0001
 - Access: Full Access
 - Flags : None

 - Type  : Allowed
 - Name  : NT AUTHORITY\LogonSessionId_0_137918
 - SID   : S-1-5-5-0-137918
 - Mask  : 0x00120001
 - Access: ModifyState|ReadControl|Synchronize
 - Flags : None
```


*代码清单 6-8：在无创建者或父级安全描述符的情况下创建新的安全描述符*

这次对New-NtSecurityDescriptor的调用只需要令牌和内核对象类型❶。最终安全描述符中的Owner和Group字段根据令牌的Owner和PrimaryGroup属性设置为默认值❷。

但DACL ❸ 是从哪里来的呢？我们既没有指定父安全描述符，也没有指定创建者安全描述符，所以它不可能来自这两者。相反，它基于Token对象的*默认DACL*——存储在令牌中的一个ACL，当没有指定其他DACL时，它作为回退方案。你可以通过将令牌传递给带有`DefaultDacl`参数的`Format-NtToken`来显示令牌的默认DACL，如代码清单 6-9所示。




```
PS> Format-NtToken $token -DefaultDacl
DEFAULT DACL
------------
GRAPHITE\user: (Allowed)(None)(GenericAll)
NT AUTHORITY\SYSTEM: (Allowed)(None)(GenericAll)
NT AUTHORITY\LogonSessionId_0_137918: (Allowed)(None)(GenericExecute|GenericRead)
```


*代码清单 6-9：显示令牌的默认DACL*

除了Mutant特有的访问权限外，代码清单 6-9中的DACL与代码清单 6-8中的DACL匹配。我们可以得出结论：如果在创建期间既不指定父安全描述符也不指定创建者安全描述符，我们将基于令牌的所有者、主组和默认DACL创建一个新的安全描述符。然而，为了确保这一点，让我们通过创建一个不带安全描述符的未命名Mutant来验证此行为（代码清单 6-10）。




```
PS> Use-NtObject($m = New-NtMutant) {
    Format-NtSecurityDescriptor $m
}
Type: Mutant
Control: None
<NO SECURITY INFORMATION>
```


*代码清单 6-10：创建未命名Mutant以验证默认安全描述符的创建行为*

等等——新的Mutant对象根本没有安全信息！这出乎我们的意料。

问题在于，当对象没有名称时，内核允许某些对象类型不设置安全信息。你可以通过查询其`SecurityRequired`属性来了解对象是否需要安全信息，如代码清单 6-11所示。




```
PS> Get-NtType "Mutant" | Select-Object SecurityRequired
SecurityRequired
----------------
           False
```


*代码清单 6-11：查询Mutant类型的SecurityRequired属性*

如你所见，Mutant类型不要求安全信息。因此，如果在创建未命名Mutant对象时既不指定创建者安全描述符也不指定父安全描述符，内核将不会生成默认安全描述符。

为什么内核要支持创建不带安全描述符的对象呢？嗯，如果应用程序之间不会共享该对象，安全描述符就没有任何用途；它只会占用额外的内核内存。只有当你创建了一个带名称的对象以便共享时，内核才会要求安全信息。

**复制未命名对象的句柄**

你可以复制未命名资源的句柄，并在不赋予该资源名称的情况下与其他进程共享。然而，这需要谨慎操作。虽然句柄复制允许你在对象没有安全描述符时从句柄中移除访问权限，但接收进程可以轻松地重新复制句柄以恢复被移除的访问权限。

在Windows 8之前，无法为`SecurityRequired`设置为False的未命名对象分配安全信息。这一情况已经改变，如果你在创建期间指定了安全描述符，它将分配给生成的对象。Windows 8还引入了一个新的、未记录的`NtDuplicateObject`标志来单独处理此问题。在复制句柄时指定`NoRightsUpgrade`标志，会告诉内核拒绝任何请求额外访问权限的进一步复制操作。

为了验证默认安全描述符的生成，现在让我们创建一个需要安全信息的对象，例如Directory对象（代码清单 6-12）。




```
PS> Get-NtType Directory | Select-Object SecurityRequired
SecurityRequired
----------------
            True

PS> Use-NtObject($dir = New-NtDirectory) {
    Format-NtSecurityDescriptor $dir -Summary
}
GRAPHITE\user: (Allowed)(None)(Full Access)
NT AUTHORITY\SYSTEM: (Allowed)(None)(Full Access)
NT AUTHORITY\LogonSessionId_0_137918: (Allowed)(None)(Query|Traverse|ReadControl)
```


*代码清单 6-12：创建未命名Directory以验证默认安全描述符*

代码清单 6-12显示默认安全描述符与我们的假设相符。

##### 仅设置父安全描述符

我们接下来要考虑的情况要复杂得多。假设我们调用`NtCreateMutant`并指定名称，但不指定`SecurityDescriptor`字段。由于命名Mutant必须在Directory对象内创建（正如我们刚才所见，Directory对象需要安全信息），父安全描述符将被设置。

然而，当我们指定父安全描述符时，我们还引入了另一个因素：*继承*，即新安全描述符复制父安全描述符的一部分的过程。继承规则决定了父安全描述符的哪些部分传递给新安全描述符，如果父安全描述符的各个部分可以被继承，我们称其为*可继承的*。

继承的目的是为资源树定义层次化的安全配置。如果没有继承，我们就必须为层次结构中的每个新对象显式分配安全描述符，这很快就会变得难以管理。同时，这也会使资源树无法管理，因为每个应用程序可能会选择不同的行为方式。

让我们测试在创建新的内核资源时适用的继承规则。我们将重点关注DACL，但这些概念同样适用于SACL。为了减少代码重复，代码清单 6-13定义了一些函数，用于运行带有父安全描述符的测试并实现各种选项。




```
PS> function New-ParentSD($AceFlags = 0, $Control = 0) {
    $owner = Get-NtSid -KnownSid BuiltinAdministrators
  ❶ $parent = New-NtSecurityDescriptor -Type Directory -Owner $owner -Group $owner
  ❷ Add-NtSecurityDescriptorAce $parent -Name "Everyone" -Access GenericAll
    Add-NtSecurityDescriptorAce $parent -Name "Users" -Access GenericAll -Flags $AceFlags
  ❸ Add-NtSecurityDescriptorControl $parent -Control $Control
  ❹ Edit-NtSecurityDescriptor $parent -MapGeneric
    return $parent
}

PS> function Test-NewSD($AceFlags = 0,
                        $Control = 0,
                        $Creator = $null,
                        [switch]$Container) {
  ❺ $parent = New-ParentSD -AceFlags $AceFlags -Control $Control
    Write-Output "-= Parent SD =-"
    Format-NtSecurityDescriptor $parent -Summary

    if ($Creator -ne $null) {
        Write-Output "`r`n-= Creator SD =-"
        Format-NtSecurityDescriptor $creator -Summary
    }

  ❻ $auto_inherit_flags = @()
    if (Test-NtSecurityDescriptor $parent -DaclAutoInherited) {
        $auto_inherit_flags += "DaclAutoInherit"
    }
    if (Test-NtSecurityDescriptor $parent -SaclAutoInherited) {
        $auto_inherit_flags += "SaclAutoInherit"
    }
    if ($auto_inherit_flags.Count -eq 0) {
        $auto_inherit_flags += "None"
    }

    $token = Get-NtToken -Effective -Pseudo
  ❼ $sd = New-NtSecurityDescriptor -Token $token -Parent $parent -Creator $creator -Type Mutant -Container:$Container -AutoInherit $auto_inherit_flags
    Write-Output "`r`n-= New SD =-"
  ❽ Format-NtSecurityDescriptor $sd -Summary
}
```


*代码清单 6-13：New-ParentSD和Test-NewSD的测试函数定义*

New-ParentSD函数创建一个新的安全描述符，其中Owner和Group字段设置为*Administrators*组❶。这将允许我们检查从该父描述符创建的任何新安全描述符中Owner或Group字段的继承情况。我们还按照对象管理器的预期将Type设置为Directory。接下来，我们添加两个允许的ACE，一个用于*Everyone*组，一个用于*Users*组❷，通过它们的SID进行区分。我们为两个ACE分配GenericAll访问权限，并为*Users* ACE添加一些额外的标志。

然后，该函数设置一些可选的安全描述符控制标志❸。通常，当我们为父对象分配安全描述符时，通用访问权限会被映射为类型特定的访问权限。在这里，我们使用带有MapGeneric参数的Edit-NtSecurityDescriptor来为我们执行此映射❹。

在Test-NewSD函数中，我们创建父安全描述符❺并计算任何自动继承标志❻。然后，我们创建一个新的安全描述符，根据需要设置Container属性以及我们计算出的自动继承标志❼。您可以为该函数指定一个创建者安全描述符，用于创建新的安全描述符。目前，我们将此值保留为$null，但将在下一节中回到这一点。最后，我们将父描述符、创建者描述符（如果指定）以及新的安全描述符打印到控制台，以验证输入和输出❽。

让我们从测试默认情况开始：运行不带任何额外参数的Test-NewSD命令。该命令将创建一个没有设置控制标志的父安全描述符，因此在调用SeAssignSecurityEx时不应存在自动继承标志（代码清单 6-14）。




```
PS> Test-NewSD
-= Parent SD =-
<DACL>
Everyone: (Allowed)(None)(Full Access)
BUILTIN\Users: (Allowed)(None)(Full Access)

-= New SD =-
<Owner> : GRAPHITE\user ❶
<Group> : GRAPHITE\None
<DACL>
GRAPHITE\user: (Allowed)(None)(Full Access) ❷
NT AUTHORITY\SYSTEM: (Allowed)(None)(Full Access)
NT AUTHORITY\LogonSessionId_0_137918: (Allowed)(None)(ModifyState|ReadControl|...)
```


*代码清单 6-14：使用父安全描述符且无创建者安全描述符创建新安全描述符*

在输出中，我们可以看到Owner和Group并未从父安全描述符中继承❶；相反，它们是本章前面观察到的默认值。这是合理的：调用者，而不是创建父对象的用户，应该拥有新资源。

然而，新的DACL看起来并不像我们预期的那样❷。它被设置为之前看到的默认DACL，并且与我们在父安全描述符中构建的DACL无关。我们没有从父DACL中获得任何ACE的原因是，我们没有将ACE指定为可继承的。为此，我们需要设置ObjectInherit和ContainerInherit ACE标志中的一个或两个。前者仅适用于非容器对象，如Mutant对象，而后者适用于容器对象，如Directory对象。这两种类型之间的区别很重要，因为它们影响继承的ACE如何传播到子对象。

Mutant对象是非容器对象，所以让我们在父安全描述符中为ACE添加ObjectInherit标志（代码清单 6-15）。




```
PS> Test-NewSD -AceFlags "ObjectInherit" ❶
-= Parent SD =-
<Owner> : BUILTIN\Administrators
<Group> : BUILTIN\Administrators
<DACL>
Everyone: (Allowed)(None)(Full Access)
BUILTIN\Users: (Allowed)(ObjectInherit)(Full Access)

-= New SD =-
<Owner> : GRAPHITE\user ❷
<Group> : GRAPHITE\None
<DACL> ❸
BUILTIN\Users: (Allowed)(None)(ModifyState|Delete|ReadControl|WriteDac|WriteOwner)
```


*代码清单 6-15：向父安全描述符添加ObjectInherit ACE*

在此清单中，我们为测试函数指定了ObjectInherit ACE标志❶。注意，Owner和Group字段没有变化❷，但DACL不再是默认值❸。相反，它包含一个ACE，授予*Users*组ModifyState|Delete|ReadControl|WriteDac|WriteOwner访问权限。这就是我们设置为继承的ACE。

然而，您可能会注意到一个问题：父安全描述符中的ACE获得了完全访问权限，而新安全描述符中的ACE却没有。为什么访问掩码发生了变化？事实上，它并没有改变；继承过程只是将父安全描述符中ACE的原始Directory访问掩码（值0x000F000F）复制到了继承的ACE中。Mutant对象的有效访问位是0x001F0001。因此，继承过程使用了最接近的映射，即0x000F0001，如代码清单 6-16所示。




```
PS> Get-NtAccessMask (0x0001F0001 -band 0x0000F000F) -ToSpecificAccess Mutant
ModifyState, Delete, ReadControl, WriteDac, WriteOwner
```


*代码清单 6-16：检查继承的访问掩码*

这是一个相当严重的问题。例如，请注意Mutant类型缺少Synchronize访问权限，而调用者需要该权限才能等待锁。没有此权限，Mutant对象对应用程序将毫无用处。

我们可以通过在ACE中指定通用访问掩码来解决此访问掩码问题。当创建新的安全描述符时，这将映射到类型特定的访问掩码。但有一个复杂之处：我们从现有对象中获取了父安全描述符，因此在分配安全描述符时，通用访问已经被映射。我们在测试函数中通过Edit-NtSecurityDescriptor调用模拟了此行为。

要解决此问题，ACE可以设置InheritOnly标志。这样，任何通用访问在初始分配期间都将保持不变。InheritOnly标志将ACE标记为仅用于继承，从而防止通用访问对访问检查造成问题。在代码清单 6-17中，我们通过修改对测试函数的调用来检查此行为。




```
❶ PS> Test-NewSD -AceFlags "ObjectInherit, InheritOnly"
-= Parent SD =-
<Owner> : BUILTIN\Administrators
<Group> : BUILTIN\Administrators
<DACL>
Everyone: (Allowed)(None)(Full Access)
❷ BUILTIN\Users: (Allowed)(ObjectInherit, InheritOnly)(GenericAll)

-= New SD =-
<Owner> : GRAPHITE\user
<Group> : GRAPHITE\None
<DACL>
❸ BUILTIN\Users: (Allowed)(None)(Full Access)
```


*代码清单 6-17：添加InheritOnly ACE*

在此清单中，我们将ACE标志更改为ObjectInherit和InheritOnly ❶。在父安全描述符的输出中，我们可以看到访问掩码不再从GenericAll映射 ❷。因此，继承的ACE现在获得完全访问权限，正如我们所要求的 ❸。

可以推测，ContainerInherit标志的工作方式与ObjectInherit相同，对吗？并非如此。我们在代码清单 6-18中测试其行为。




```
❶ PS> Test-NewSD -AceFlags "ContainerInherit, InheritOnly" -Container
-= Parent SD =-
<Owner> : BUILTIN\Administrators
<Group> : BUILTIN\Administrators
<DACL>
Everyone: (Allowed)(None)(Full Access)
BUILTIN\Users: (Allowed)(ContainerInherit, InheritOnly)(GenericAll)

-= New SD =-
<Owner> : GRAPHITE\user
<Group> : GRAPHITE\None
<DACL>
❷ BUILTIN\Users: (Allowed)(None)(Full Access)
❸ BUILTIN\Users: (Allowed)(ContainerInherit, InheritOnly)(GenericAll)
```


*代码清单 6-18：使用ContainerInherit标志创建新的安全描述符*

在这里，我们向ACE添加ContainerInherit和InheritOnly标志，然后将Container参数传递给函数 ❶。与ObjectInherit的情况不同，我们现在在DACL中得到了两个ACE。第一个ACE ❷ 基于可继承的ACE授予新资源访问权限。第二个 ❸ 是可继承ACE的副本，具有GenericAll访问权限。

> 注意
>
> *您可能想知道，当我们使用Mutant类型时，如何为容器类型创建安全描述符。答案是API并不关心最终类型，因为它只使用通用映射；然而，在创建真正的Mutant对象时，内核永远不会指定Container标志。*

ACE的自动传播非常有用，因为它允许您构建容器层次结构，而无需手动授予它们访问权限。然而，有时您可能希望通过指定NoPropagateInherit ACE标志来禁用此自动传播，如代码清单 6-19所示。




```
PS> $ace_flags = "ContainerInherit, InheritOnly, NoPropagateInherit"
PS> Test-NewSD -AceFlags $ace_flags -Container
--snip--
-= New SD =-
<Owner> : GRAPHITE\user
<Group> : GRAPHITE\None
<DACL>
❶ BUILTIN\Users: (Allowed)(None)(Full Access)
```


*代码清单 6-19：使用NoPropagateInherit防止ACE的自动继承*

当我们指定此标志时，授予资源访问权限的ACE仍然存在，但可继承的ACE消失了 ❶。

让我们尝试另一种ACE标志配置，看看ObjectInherit ACE在被容器继承时会发生什么（代码清单 6-20）。




```
PS> Test-NewSD -AceFlags "ObjectInherit" -Container
--snip--
-= New SD =-
<Owner> : GRAPHITE\user
<Group> : GRAPHITE\None
<DACL>
❶ BUILTIN\Users: (Allowed)(ObjectInherit, InheritOnly)(ModifyState|...)
```


*代码清单 6-20：在容器上测试ObjectInherit标志*

您可能不会期望容器继承ACE，但事实上，它接收到的ACE会自动设置InheritOnly标志 ❶。这允许容器将ACE传递给非容器子对象。

表6-4总结了基于父ACE标志的容器和非容器对象的继承规则。在不发生继承的情况下，对象以粗体显示。

| 父ACE标志 | 非容器对象 | 容器对象 |
| :---------------------------------------------- | :------------------- | :---------------------------- |
| 无 | 不继承 | 不继承 |
| ObjectInherit | 无 | InheritOnlyObjectInherit |
| ContainerInherit | 不继承 | ContainerInherit |
| ObjectInheritNoPropagateInherit | 无 | 不继承 |
| ContainerInheritNoPropagateInherit | 不继承 | 无 |
| ContainerInheritObjectInherit | 无 | ContainerInheritObjectInherit |
| ContainerInheritObjectInheritNoPropagateInherit | 无 | 无 |

最后，考虑*自动继承标志*。如果你回到表6-3，可以看到如果DACL设置了`DaclAutoInherited`控制标志，内核会将`DaclAutoInherit`标志传递给`SeAssignSecurityEx`，因为没有创建者安全描述符。（SACL有对应的`SaclAutoInherit`标志，但这里我们专注于DACL。）`DaclAutoInherit`标志的作用是什么？在代码清单 6-21中，我们进行了一个测试来找出答案。

```
PS> $ace_flags = "ObjectInherit, InheritOnly"
❶ PS> Test-NewSD -AceFlags $ace_flags -Control "DaclAutoInherited"
-= Parent SD =-
<Owner> : BUILTIN\Administrators
<Group> : BUILTIN\Administrators
❷ <DACL> (Auto Inherited)
Everyone: (Allowed)(None)(Full Access)
BUILTIN\Users: (Allowed)(ObjectInherit, InheritOnly)(GenericAll)

-= New SD =-
<Owner> : GRAPHITE\user
<Group> : GRAPHITE\None
❸ <DACL> (Auto Inherited)
❹ BUILTIN\Users: (Allowed)(Inherited)(Full Access)
```

*代码清单 6-21：在父安全描述符中设置DaclAutoInherited控制标志*

我们设置父安全描述符的控制标志以包含`DaclAutoInherited`标志❶，并通过查看格式化的DACL确认其已设置❷。我们可以看到新的安全描述符也包含该标志❸；此外，继承的ACE具有`Inherited`标志❹。

自动继承标志与我们之前讨论的继承标志有何不同？微软出于兼容性原因保留了两种继承类型（因为直到Windows 2000才引入`Inherited`标志）。从内核的角度来看，这两种继承类型除了决定新安全描述符是否设置`DaclAutoInherited`标志以及任何继承的ACE是否获得`Inherited`标志外，并没有太大区别。但从用户模式的角度来看，这种继承模型指示了DACL的哪些部分是从父安全描述符继承的。这是重要信息，各种Win32 API会使用它，我们将在本章末尾的“Win32 安全 API”一节中讨论。

##### 同时设置创建者和父安全描述符

在最后一种情况下，我们使用名称调用`NtCreateMutant`并指定`SecurityDescriptor`字段，同时设置创建者和父安全描述符参数。为了观察结果行为，让我们定义一些测试代码。代码清单 6-22编写了一个函数来生成创建者安全描述符。我们将重用之前编写的`Test-NewSD`函数来运行测试。

```
PS> function New-CreatorSD($AceFlags = 0, $Control = 0, [switch]$NoDacl) {
  ❶ $creator = New-NtSecurityDescriptor -Type Mutant
  ❷ if (!$NoDacl) {
      ❸ Add-NtSecurityDescriptorAce $creator -Name "Network" -Access GenericAll
        Add-NtSecurityDescriptorAce $creator -Name "Interactive"
-Access GenericAll -Flags $AceFlags
    }
    Add-NtSecurityDescriptorControl $creator -Control $Control
    Edit-NtSecurityDescriptor $creator -MapGeneric
    return $creator
}
```

*代码清单 6-22：New-CreatorSD测试函数*

此函数与代码清单 6-13中创建的`New-ParentSD`函数在以下方面不同：我们在创建安全描述符时使用`Mutant`类型❶，允许调用者不指定DACL❷，并且如果使用DACL则设置不同的SID❸。这些更改将使我们能够区分新安全描述符中来自父级和创建者的部分。

在一些简单情况下，父安全描述符没有可继承的DACL，API遵循与仅设置创建者安全描述符时相同的规则。换句话说，如果创建者指定了DACL，新安全描述符将使用它。否则，它将使用默认DACL。

如果父安全描述符包含可继承的DACL，新安全描述符将继承它，除非创建者安全描述符也有DACL。即使是空或NULL DACL也会覆盖来自父级的继承。在代码清单 6-23中，我们验证了这种行为。

```
❶ PS> $creator = New-CreatorSD -NoDacl
❷ PS> Test-NewSD -Creator $creator -AceFlags "ObjectInherit, InheritOnly"
-= Parent SD =-
<Owner> : BUILTIN\Administrators
<Group> : BUILTIN\Administrators
<DACL>
Everyone: (Allowed)(None)(Full Access)
❸ BUILTIN\Users: (Allowed)(ObjectInherit, InheritOnly)(GenericAll)

-= Creator SD =-
❹ <NO SECURITY INFORMATION>

-= New SD =-
<Owner> : GRAPHITE\user
<Group> : GRAPHITE\None
<DACL>
❺ BUILTIN\Users: (Allowed)(None)(Full Access)
```

*代码清单 6-23：测试无创建者DACL时的父DACL继承*

我们首先构建一个没有DACL的创建者安全描述符❶，然后使用可继承的父安全描述符运行测试❷。在输出中，我们确认了*Users*组的可继承ACE❸，并且创建者没有设置DACL❹。当我们创建新安全描述符时，它接收了可继承的ACE❺。

让我们也检查一下，当我们设置创建者DACL时会发生什么（代码清单 6-24）。

```
❶ PS> $creator = New-CreatorSD
❷ PS> Test-NewSD -Creator $creator -AceFlags "ObjectInherit, InheritOnly"
-= Parent SD =-
<Owner> : BUILTIN\Administrators
<Group> : BUILTIN\Administrators
<DACL>
Everyone: (Allowed)(None)(Full Access)
BUILTIN\Users: (Allowed)(ObjectInherit, InheritOnly)(GenericAll)

-= Creator SD =-
<DACL>
NT AUTHORITY\NETWORK: (Allowed)(None)(Full Access)
NT AUTHORITY\INTERACTIVE: (Allowed)(None)(Full Access)

-= New SD =-
<Owner> : GRAPHITE\user
<Group> : GRAPHITE\None
<DACL>
❸ NT AUTHORITY\NETWORK: (Allowed)(None)(Full Access)
NT AUTHORITY\INTERACTIVE: (Allowed)(None)(Full Access)
```

*代码清单 6-24：测试创建者DACL覆盖父DACL继承的情况*

在这里，我们构建了一个带有DACL的创建者安全描述符❶，并保持与代码清单 6-23中相同的可继承父安全描述符❷。在输出中，我们看到创建者DACL中的ACE已被复制到新的安全描述符中❸。

前两个测试没有指定任何自动继承标志。如果我们在父安全描述符上指定了`DaclAutoInherited`控制标志，但不包含创建者DACL，那么继承过程与代码清单 6-24中的方式相同，只是它会设置继承的ACE标志。

然而，如果我们同时指定了创建者DACL和控制标志，就会发生一些有趣的事情（代码清单 6-25）。

```
❶ PS> $creator = New-CreatorSD -AceFlags "Inherited"
❷ PS> Test-NewSD -Creator $creator -AceFlags "ObjectInherit, InheritOnly"
-Control "DaclAutoInherited"
-= Parent SD =-
<Owner> : BUILTIN\Administrators
<Group> : BUILTIN\Administrators
<DACL> (Auto Inherited)
Everyone: (Allowed)(None)(Full Access)
BUILTIN\Users: (Allowed)(ObjectInherit, InheritOnly)(GenericAll)

-= Creator SD =-
<DACL>
NT AUTHORITY\NETWORK: (Allowed)(None)(Full Access)
NT AUTHORITY\INTERACTIVE: (Allowed)(Inherited)(Full Access)

-= New SD =-
<Owner> : GRAPHITE\user
<Group> : GRAPHITE\None
<DACL> (Auto Inherited)
❸ NT AUTHORITY\NETWORK: (Allowed)(None)(Full Access)
❹ BUILTIN\Users: (Allowed)(Inherited)(Full Access)
```

*代码清单 6-25：测试同时设置创建者DACL和`DaclAutoInherited`控制标志时的父DACL继承情况*

在此清单中，我们构建了一个创建者安全描述符，并将`INTERACTIVE` SID ACE设置为包含`Inherited`标志❶。接下来，我们在父安全描述符上使用`DaclAutoInherited`控制标志运行测试❷。在输出中，请注意有两个ACE。第一个ACE是从创建者复制过来的❸，而第二个是从父级继承的ACE❹。图6-1展示了这种自动继承行为。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure6-1.webp)

图6-1：当父和创建者安全描述符都设置时的自动继承行为

当设置了`DaclAutoInherit`时，新安全描述符的DACL会将创建者安全描述符中的非继承ACE与父级中的可继承ACE合并。这种自动继承行为允许你基于父级重建子级的安全描述符，而不会丢失用户显式添加到DACL中的任何ACE。此外，自动设置`Inherited` ACE标志使我们能够区分这些显式ACE和继承的ACE。

请注意，内核中的正常操作不会设置`DaclAutoInherit`标志，只有在父安全描述符设置了`DaclAutoInherited`控制标志且DACL不存在时，该标志才会启用。在我们的测试中，我们指定了DACL，因此自动继承标志未被设置。Win32 API会使用这种行为，我们将在本章后面讨论。

如果你想抑制显式ACE与父级可继承ACE的合并，可以设置`DaclProtected`和/或`SaclProtected`安全描述符控制标志。如果设置了受保护的控制标志，继承规则会保持相应的ACL不变，除了为ACL设置`AutoInherited`控制标志并清除任何继承的ACE标志。在代码清单 6-26中，我们测试了DACL的这种行为。

```
❶ PS> $creator = New-CreatorSD -AceFlags "Inherited" -Control "DaclProtected"
❷ PS> Test-NewSD -Creator $creator -AceFlags "ObjectInherit, InheritOnly"
-Control "DaclAutoInherited"
-= Parent SD =-
<Owner> : BUILTIN\Administrators
<Group> : BUILTIN\Administrators
<DACL> (Auto Inherited)
Everyone: (Allowed)(None)(Full Access)
BUILTIN\Users: (Allowed)(ObjectInherit, InheritOnly)(GenericAll)

-= Creator SD =-
<DACL> (Protected)
NT AUTHORITY\NETWORK: (Allowed)(None)(Full Access)
NT AUTHORITY\INTERACTIVE: (Allowed)(Inherited)(Full Access)

-= New SD =-
<Owner> : GRAPHITE\user
<Group> : GRAPHITE\None
<DACL> (Protected, Auto Inherited)
NT AUTHORITY\NETWORK: (Allowed)(None)(Full Access)
❸ NT AUTHORITY\INTERACTIVE: (Allowed)(None)(Full Access)
```

*代码清单 6-26：测试`DaclProtected`控制标志*

我们首先生成一个带有`DaclProtected`标志的创建者安全描述符，并将其中一个ACE的标志设置为`Inherited`❶。然后，我们使用自动继承的父级创建一个新的安全描述符❷。如果没有`DaclProtected`标志，新安全描述符的DACL将是创建者DACL和父级可继承ACE的合并版本。相反，我们只看到创建者DACL的ACE。此外，第二个ACE上的`Inherited`标志已被清除❸。

如果我们不知道父安全描述符是否会有可继承的ACE，并且不希望最终得到默认的DACL，该怎么办？这对于永久对象（如文件或键）可能很重要，因为默认DACL包含临时登录SID，该SID不应真正持久化到磁盘。毕竟，重用登录SID可能会最终授予不相关用户访问权限。

在这种情况下，我们不能在创建者安全描述符中设置DACL；根据继承规则，这会覆盖任何继承的ACE。相反，我们可以使用`DaclDefaulted`安全描述符控制标志来处理这种情况，该标志表示提供的DACL是默认的。代码清单 6-27演示了其用法。

```
PS> $creator = New-CreatorSD -Control "DaclDefaulted"
PS> Test-NewSD -Creator $creator -AceFlags "ObjectInherit, InheritOnly"
= Parent SD =-
<Owner> : BUILTIN\Administrators
<Group> : BUILTIN\Administrators
<DACL>
Everyone: (Allowed)(None)(Full Access)
BUILTIN\Users: (Allowed)(ObjectInherit, InheritOnly)(GenericAll)

-= Creator SD =-
<DACL> (Defaulted)
NT AUTHORITY\NETWORK: (Allowed)(None)(Full Access)
NT AUTHORITY\INTERACTIVE: (Allowed)(None)(Full Access)

-= New SD =-
<Owner> : GRAPHITE\user
<Group> : GRAPHITE\None
<DACL>
BUILTIN\Users: (Allowed)(None)(Full Access)

PS> Test-NewSD -Creator $creator
-= Parent SD =-
<Owner> : BUILTIN\Administrators
<Group> : BUILTIN\Administrators
<DACL>
Everyone: (Allowed)(None)(Full Access)
BUILTIN\Users: (Allowed)(None)(Full Access)

-= Creator SD =-
<DACL> (Defaulted)
NT AUTHORITY\NETWORK: (Allowed)(None)(Full Access)
NT AUTHORITY\INTERACTIVE: (Allowed)(None)(Full Access)

-= New SD =-
<Owner> : GRAPHITE\user
<Group> : GRAPHITE\None
<DACL>
NT AUTHORITY\NETWORK: (Allowed)(None)(Full Access)
NT AUTHORITY\INTERACTIVE: (Allowed)(None)(Full Access)
```

*代码清单 6-27：测试`DaclDefaulted`标志*

如果父对象不包含任何可继承的DACL ACE，新的安全描述符将使用创建者的DACL，而不是默认DACL。如果父对象确实包含可继承的ACE，继承过程将按照先前概述的规则覆盖DACL。

要为SACL实现类似的行为，可以使用`SaclDefaulted`控制标志。然而，令牌不包含默认SACL，因此此标志的重要性相对较低。

##### 替换CREATOR OWNER和CREATOR GROUP SID

我们已经看到，在继承过程中，继承的ACE保留与原始ACE相同的SID。在某些场景下，这并不理想。例如，您可能有一个共享目录，允许任何用户创建子目录。您应该在此共享目录上设置什么样的安全描述符，以便只有子目录的创建者才能访问它？

一种解决方案是移除所有可继承的ACE。结果，新目录将使用默认DACL。这几乎肯定能保护目录，防止其他用户访问。然而，如前所述，默认DACL是为临时资源（如对象管理器中的资源）设计的；持久性安全描述符不应使用它。

为了支持共享目录等功能，继承实现支持四个特殊的创建者SID。当安全描述符继承包含这些SID之一的ACE时，继承实现将用创建者令牌中的特定SID替换创建者SID：

***CREATOR OWNER\*** (S-1-3-0)  替换为令牌的所有者

***CREATOR GROUP\*** (S-1-3-1)  替换为令牌的主组

***CREATOR OWNER SERVER\*** (S-1-3-2)  替换为服务器的所有者

***CREATOR GROUP SERVER\*** (S-1-3-3)  替换为服务器的主组

我们仅在创建服务器安全描述符时使用服务器SID，这将在本章末尾的“服务器安全描述符与复合 ACE”一节中讨论。从创建者SID到特定SID的转换是单向过程：一旦SID被替换，您无法将其与显式设置的SID区分开来。但是，如果容器继承了ACE，它将在InheritOnly ACE中保留创建者SID。代码清单 6-28提供了一个示例。




```
PS> $parent = New-NtSecurityDescriptor -Type Directory
PS> Add-NtSecurityDescriptorAce $parent -KnownSid CreatorOwner
-Flags ContainerInherit, InheritOnly -Access GenericWrite
PS> Add-NtSecurityDescriptorAce $parent -KnownSid CreatorGroup
-Flags ContainerInherit, InheritOnly -Access GenericRead
PS> Format-NtSecurityDescriptor $parent -Summary -SecurityInformation Dacl
<DACL>
❶ CREATOR OWNER: (Allowed)(ContainerInherit, InheritOnly)(GenericWrite)
CREATOR GROUP: (Allowed)(ContainerInherit, InheritOnly)(GenericRead)

PS> $token = Get-NtToken -Effective -Pseudo
❷ PS> $sd = New-NtSecurityDescriptor -Token $token -Parent $parent
-Type Directory -Container
PS> Format-NtSecurityDescriptor $sd -Summary -SecurityInformation Dacl
<DACL>
❸ GRAPHITE\user: (Allowed)(None)(CreateObject|CreateSubDirectory|ReadControl)
CREATOR OWNER: (Allowed)(ContainerInherit, InheritOnly)(GenericWrite)
❹ GRAPHITE\None: (Allowed)(None)(Query|Traverse|ReadControl)
CREATOR GROUP: (Allowed)(ContainerInherit, InheritOnly)(GenericRead)
```


*代码清单 6-28：测试继承期间的创建者SID*

我们首先在父安全描述符中添加两个带有*CREATOR OWNER*和*CREATOR GROUP* SID的ACE，赋予这些ACE不同的访问级别以便区分❶。然后，我们基于父安全描述符创建一个新的安全描述符，指定将其用于容器❷。在格式化输出中，我们看到用户的SID已替换了*CREATOR OWNER* SID。此SID基于令牌中的所有者SID❸。我们还可以看到*CREATOR GROUP* SID已被替换为令牌中的组SID❹。

由于我们为容器创建了安全描述符，我们还看到有两个InheritOnly ACE，其创建者SID未被更改。此行为允许创建者SID传播到任何未来的子对象。

##### 分配强制标签

强制标签ACE包含资源的完整性级别。但是，当我们使用完整性级别大于或等于Medium的令牌创建新的安全描述符时，新的安全描述符默认不会接收强制标签。此行为解释了为什么到目前为止我们在测试中没有看到任何强制标签ACE。

另一方面，如果令牌的完整性级别低于Medium，则此标签会自动分配给新的安全描述符，如代码清单 6-29所示。




```
PS> $token = Get-NtToken -Duplicate -IntegrityLevel Low
PS> $sd = New-NtSecurityDescriptor -Token $token -Type Mutant
PS> Format-NtSecurityDescriptor $sd -SecurityInformation Label -Summary
<Mandatory Label>
Mandatory Label\Low Mandatory Level: (MandatoryLabel)(None)(NoWriteUp)
PS> $token.Close()
```


*代码清单 6-29：分配创建者令牌的强制标签*

在此列表中，我们复制当前令牌并为其分配Low完整性级别。当我们基于该令牌创建新的安全描述符时，我们看到它带有相同完整性级别的强制标签。

应用程序可以在通过创建者安全描述符创建新资源时显式设置强制标签ACE。但是，强制标签ACE中的完整性级别必须小于或等于令牌的完整性级别；否则，创建将失败，如代码清单 6-30所示。




```
PS> $creator = New-NtSecurityDescriptor -Type Mutant
PS> Set-NtSecurityDescriptorIntegrityLevel $creator System
PS> $token = Get-NtToken -Duplicate -IntegrityLevel Medium
PS> New-NtSecurityDescriptor -Token $token -Creator $creator -Type Mutant
❶ New-NtSecurityDescriptor : (0xC0000061) - A required privilege is not held
by the client.

❷ PS> $sd = New-NtSecurityDescriptor -Token $token -Creator $creator 
-Type Mutant -AutoInherit AvoidPrivilegeCheck
PS> Format-NtSecurityDescriptor $sd -SecurityInformation Label -Summary
<Mandatory Label>
❸ Mandatory Label\System Mandatory Level: (MandatoryLabel)(None)(NoWriteUp)

PS> $token.Close()
```


*代码清单 6-30：基于创建者安全描述符分配强制标签*

首先，我们创建一个新的创建者安全描述符，并为其添加一个带有系统完整性级别的强制标签。然后，我们获取调用者的令牌，并将其完整性级别设置为中等。由于系统完整性级别高于中等，如果我们尝试使用创建者安全描述符来创建新的安全描述符，操作将失败并返回 `STATUS_PRIVILEGE_NOT_HELD` 错误❶。

要设置更高的完整性级别，必须在创建者令牌上启用 `SeRelabelPrivilege` 特权，或者指定 `AvoidPrivilegeCheck` 自动继承标志。在本示例中，我们在创建新的安全描述符时设置了自动继承标志❷。添加此标志后，创建成功，我们可以在格式化输出中看到强制标签❸。

我们可以通过设置强制标签 ACE 的 `ObjectInherit` 或 `ContainerInherit` 标志，使其可继承。还可以指定其 `InheritOnly` 标志，这会阻止完整性级别参与访问检查，仅保留用于继承。

但请注意，完整性级别限制同样适用于继承的强制标签 ACE。继承的 ACE 必须具有小于或等于令牌的完整性级别；否则，安全描述符的分配将失败。同样，我们可以通过 `SeRelabelPrivilege` 特权或 `AvoidPrivilegeCheck` 自动继承标志来绕过此限制。代码清单 6-31 展示了一个安全描述符通过继承获取强制标签 ACE 的示例。

```
PS> $parent = New-NtSecurityDescriptor -Type Mutant
❶ PS> Set-NtSecurityDescriptorIntegrityLevel $parent Low -Flags ObjectInherit
PS> $token = Get-NtToken -Effective -Pseudo
PS> $sd = New-NtSecurityDescriptor -Token $token -Parent $parent -Type Mutant
PS> Format-NtSecurityDescriptor $sd -SecurityInformation Label -Summary
<Mandatory Label>
❷ Mandatory Label\Low Mandatory Level: (MandatoryLabel)(Inherited)(NoWriteUp)
```

*代码清单 6-31：通过继承从父安全描述符分配强制标签*

首先，我们创建一个父安全描述符，并为其分配一个带有低完整性级别和 `ObjectInherit` 标志的强制标签 ACE❶。然后，我们使用父描述符创建一个新的安全描述符。新描述符继承了强制标签，如 `Inherited` 标志所示❷。

某些内核对象类型可能会自动接收强制标签，即使调用者的令牌具有中等或更高的完整性级别。通过指定某些自动继承标志，您可以在为资源创建新的安全描述符时，始终分配调用者的完整性级别。这些标志包括 `MaclNoWriteUp`、`MaclNoReadUp` 和 `MaclNoExecuteUp`，它们分别自动继承令牌的完整性级别，并将强制策略设置为 `NoWriteUp`、`NoReadUp` 和 `NoExecuteUp`。通过组合这些标志，您可以获得所需的强制策略。

在最新版本的 Windows 中，只有四种类型注册使用这些自动继承标志，如表 6-5 所示。

| 类型名称 | 自动继承标志 |
| :-------- | :-------------------------- |
| 进程 | MaclNoWriteUp, MaclNoReadUp |
| 线程 | MaclNoWriteUp, MaclNoReadUp |
| 作业 | MaclNoWriteUp |
| 令牌 | MaclNoWriteUp |

我们可以通过在创建安全描述符时指定这些自动继承标志来测试其行为。在代码清单 6-32中，我们指定了 `MaclNoReadUp` 和 `MaclNoWriteUp` 自动继承标志。

```
PS> $token = Get-NtToken -Effective -Pseudo
PS> $sd = New-NtSecurityDescriptor -Token $token -Type Mutant
-AutoInherit MaclNoReadUp, MaclNoWriteUp
PS> Format-NtSecurityDescriptor $sd -SecurityInformation Label -Summary
<Mandatory Label>
Mandatory Label\Medium Mandatory Level: (MandatoryLabel)(None)(NoWriteUp|
NoReadUp)
```

*代码清单 6-32：通过指定自动继承标志分配强制标签*

在输出中，我们可以看到带有中等完整性级别的强制标签 ACE，尽管我在本节开头提到，中等级别通常不会被分配。我们还可以看到，强制策略已设置为 `NoWriteUp|NoReadUp`，这与我们指定的自动继承标志相匹配。

##### 确定对象继承

当我们在父安全描述符中指定对象 ACE 类型（如 `AllowedObject`）时，继承规则会略有变化。这是因为每个对象 ACE 可以包含两个可选的 GUID：`ObjectType`（用于访问检查）和 `InheritedObjectType`（用于继承）。

`SeAssignSecurityEx` API 使用 ACE 中的 `InheritedObjectType` GUID 来计算新的安全描述符是否应继承该 ACE。如果此 GUID 存在且其值与 `ObjectType` GUID 匹配，则新的安全描述符将继承该 ACE。相反，如果值不匹配，则 ACE 不会被复制。表 6-6 显示了 `ObjectType` 参数和 `InheritedObjectType` 的可能组合，以及 ACE 是否被继承。

| 指定了 ObjectType 参数？ | ACE 中的 InheritedObjectType？ | 是否继承 |
| :------------------------------ | :------------------------------- | :-------- |
| 否                              | 否                               | 是       |
| 否                              | 是                               | 否       |
| 是                              | 否                               | 是       |
| 是                              | 是（且值匹配）                   | 是       |
| 是                              | 是（且值不匹配）                 | 否       |

我在 表 6-6 中加粗了不发生继承的情况。请注意，这并不会取代其他继承决策：ACE 必须设置了 `ObjectInherit` 和/或 `ContainerInherit` 标志，才会被考虑用于继承。

在 代码清单 6-33 中，我们通过向安全描述符添加一些对象 ACE 并将其用作父级来验证此行为。

```
PS> $owner = Get-NtSid -KnownSid BuiltinAdministrators
PS> $parent = New-NtSecurityDescriptor -Type Directory -Owner $owner -Group $owner
❶ PS> $type_1 = New-Guid
PS> $type_2 = New-Guid
❷ PS> Add-NtSecurityDescriptorAce $parent -Name "SYSTEM" -Access GenericAll
-Flags ObjectInherit -Type AllowedObject -ObjectType $type_1
❸ PS> Add-NtSecurityDescriptorAce $parent -Name "Everyone" -Access GenericAll
-Flags ObjectInherit -Type AllowedObject -InheritedObjectType $type_1
❹ PS> Add-NtSecurityDescriptorAce $parent -Name "Users" -Access GenericAll
-Flags ObjectInherit -InheritedObjectType $type_2 -Type AllowedObject
PS> Format-NtSecurityDescriptor $parent -Summary -SecurityInformation Dacl
<DACL>
NT AUTHORITY\SYSTEM: (AllowedObject)(ObjectInherit)(GenericAll) (OBJ:f5ee1953...)
Everyone: (AllowedObject)(ObjectInherit)(GenericAll)(IOBJ:f5ee1953...)
BUILTIN\Users: (AllowedObject)(ObjectInherit)(GenericAll)(IOBJ:0b9ed996...)

PS> $token = Get-NtToken -Effective -Pseudo
❺ PS> $sd = New-NtSecurityDescriptor -Token $token -Parent $parent
-Type Directory -ObjectType $type_2
PS> Format-NtSecurityDescriptor $sd -Summary -SecurityInformation Dacl
<DACL>
❻ NT AUTHORITY\SYSTEM: (AllowedObject)(None)(Full Access)(OBJ:f5ee1953...)
❼ BUILTIN\Users: (Allowed)(None)(Full Access)
```

*代码清单 6-33：验证 InheritedObjectType GUID 的行为*

我们首先生成几个随机 GUID 作为我们的对象类型 ❶。接下来，我们向父安全描述符添加三个可继承的 AllowedObject ACE。在第一个 ACE 中，我们将 `ObjectType` 设置为我们创建的第一个 GUID ❷。此 ACE 表明在继承 ACE 时不考虑 `ObjectType` GUID。第二个 ACE 将 `InheritedObjectType` 设置为第一个 GUID ❸。最后一个 ACE 使用第二个 GUID ❹。

然后我们创建一个新的安全描述符，将第二个 GUID 传递给 `ObjectType` 参数 ❺。当我们检查新的安全描述符时，可以看到它继承了没有 `InheritedObjectType` 的 ACE ❻。输出中的第二个 ACE 是带有匹配的 `InheritedObjectType` GUID 的 ACE 的副本 ❼。请注意，根据输出，`InheritedObjectType` 已被移除，因为该 ACE 不再可继承。

只有一个 `ObjectType` GUID 参数有些不够灵活，因此 Windows 还提供了两个接受 GUID 列表而非单个 GUID 的 API：内核 API `SeAssignSecurityEx2` 和用户模式 API `RtlNewSecurityObjectWithMultipleInheritance`。列表中任何带有 `InheritedObjectType` 的 ACE 都将被继承；否则，继承规则与这里介绍的基本相同。

至此，我们结束了关于在创建期间分配安全描述符的讨论。如您所见，分配过程很复杂，尤其是在继承方面。我们现在将讨论向现有资源分配安全描述符，这是一个相对简单的过程。

#### 向现有资源分配安全描述符

如果资源已经存在，则无法通过调用创建系统调用（如 `NtCreateMutant`）并在对象属性中指定 `SecurityDescriptor` 字段来设置安全描述符。相反，您需要根据要修改的安全描述符的哪个部分，使用三种访问权限之一打开资源的句柄。一旦拥有此句柄，就可以调用 `NtSetSecurityObject` 系统调用来设置特定的安全描述符信息。表 6-7 显示了根据 `SecurityInformation` 枚举设置每个安全描述符字段所需的访问权限。

| 标志名称             | 描述                                                         | 位置    | 所需的句柄访问权限                         |
| :------------------- | :----------------------------------------------------------- | :------ | :----------------------------------------- |
| Owner                | 设置所有者SID。                                              | Owner   | WriteOwner                                 |
| Group                | 设置组SID。                                                  | Group   | WriteOwner                                 |
| Dacl                 | 设置DACL。                                                   | DACL    | WriteDac                                   |
| Sacl                 | 设置SACL（仅用于审计ACE）。                                  | SACL    | AccessSystemSecurity                       |
| Label                | 设置强制标签。                                               | SACL    | WriteOwner                                 |
| Attribute            | 设置系统资源属性。                                           | SACL    | WriteDac                                   |
| Scope                | 设置作用域策略ID。                                           | SACL    | AccessSystemSecurity                       |
| ProcessTrustLabel    | 设置进程信任标签。                                           | SACL    | WriteDac                                   |
| AccessFilter         | 设置访问过滤器。                                             | SACL    | WriteDac                                   |
| Backup               | 设置除进程信任标签和访问过滤器之外的所有内容。               | 全部    | WriteDac、WriteOwner和AccessSystemSecurity |

您可能会注意到，设置此信息所需的句柄访问权限比仅查询它所需的访问权限更复杂（如表6-1所述），因为它分布在三个访问权限中，而不是两个。与其尝试记住这些访问权限，您可以使用Get-NtAccessMask PowerShell命令来检索它们，并通过SecurityInformation参数指定要设置的安全描述符部分，如代码清单 6-34所示。

```
PS> Get-NtAccessMask -SecurityInformation AllBasic -ToGenericAccess
ReadControl

PS> Get-NtAccessMask -SecurityInformation AllBasic -ToGenericAccess
-SetSecurity
WriteDac, WriteOwner
```

*代码清单 6-34：发现查询或设置特定安全描述符信息所需的访问掩码*

要设置安全描述符，NtSetSecurityObject系统调用会调用类型特定的安全函数。此类型特定函数允许内核支持安全描述符的不同存储需求；例如，文件必须将其安全描述符持久化到磁盘，而对象管理器可以将安全描述符存储在内存中。

这些类型特定函数最终会调用SeSetSecurityDescriptorInfoEx内核API来构建更新后的安全描述符。用户模式将此内核API导出为RtlSetSecurityObjectEx。一旦安全描述符更新完成，类型特定函数可以使用其首选机制存储它。

SeSetSecurityDescriptorInfoEx API接受以下五个参数，并返回一个新的安全描述符：

**修改安全描述符**    传递给NtSetSecurityObject的新安全描述符

**对象安全描述符**    正在更新的对象的当前安全描述符

**安全信息**    指定要更新安全描述符哪些部分的标志，如表6-7所述

**自动继承**    定义自动继承行为的一组位标志

**通用映射**    正在创建的类型的通用映射

没有内核代码使用自动继承标志；因此，此API的行为很简单。它仅将安全信息参数中指定的安全描述符部分复制到新的安全描述符中。它还使用通用映射将任何通用访问映射到类型特定访问，不包括InheritOnly ACE。

某些安全描述符控制标志引入了特殊行为。例如，无法显式设置DaclAutoInherited，但您可以将其与DaclAutoInheritReq一起指定，以在新安全描述符上设置它。

我们可以使用Edit-NtSecurityDescriptor命令测试RtlSetSecurityObjectEx API，如代码清单 6-35所示。

```
PS> $owner = Get-NtSid -KnownSid BuiltinAdministrators
PS> $obj_sd = New-NtSecurityDescriptor -Type Mutant -Owner $owner
-Group $owner
PS> Add-NtSecurityDescriptorAce $obj_sd -KnownSid World -Access GenericAll
PS> Format-NtSecurityDescriptor $obj_sd -Summary -SecurityInformation Dacl
<DACL>
Everyone: (Allowed)(None)(Full Access)

PS> Edit-NtSecurityDescriptor $obj_sd -MapGeneric
PS> $mod_sd = New-NtSecurityDescriptor -Type Mutant
PS> Add-NtSecurityDescriptorAce $mod_sd -KnownSid Anonymous
-Access GenericRead
PS> Set-NtSecurityDescriptorControl $mod_sd DaclAutoInherited,
DaclAutoInheritReq
PS> Edit-NtSecurityDescriptor $obj_sd $mod_sd -SecurityInformation Dacl
PS> Format-NtSecurityDescriptor $obj_sd -Summary -SecurityInformation Dacl
<DACL> (Auto Inherited)
NT AUTHORITY\ANONYMOUS LOGON: (Allowed)(None)(ModifyState|ReadControl)
```

*代码清单 6-35：使用Edit-NtSecurityDescriptor修改现有安全描述符*

你可以使用 `Set-NtSecurityDescriptor` 命令为内核对象设置安全性。该命令可以接受具有所需访问权限的对象句柄，或指向资源的 OMNS 路径。例如，你可以使用以下命令尝试通过设置新的 DACL 来修改对象 *\BaseNamedObjects\ABC*：


```
PS> $new_sd = New-NtSecurityDescriptor -Sddl "D:(A;;GA;;;WD)"
PS> Set-NtSecurityDescriptor -Path "\BaseNamedObjects\ABC"
-SecurityDescriptor $new_sd -SecurityInformation Dacl
```


请注意“尝试”一词：即使你能够以设置安全描述符组件所需的访问权限（如 WriteOwner 访问权限）打开资源，这也不意味着内核会允许你这样做。关于所有者 SID 和强制标签的规则，与在创建时分配安全描述符时相同。

`SeSetSecurityDescriptorInfoEx` API 强制执行这些规则。如果未指定对象安全描述符，则该 API 返回 `STATUS_NO_SECURITY _ON_OBJECT` 状态代码。因此，你不能为 `SecurityRequired` 设置为 False 的类型设置安全描述符；该对象不会有安全描述符，因此任何修改它的尝试都会导致错误。

> 注意
>
> *我尚未提及的一个 ACE 标志是 Critical。Windows 内核包含检查 Critical 标志并阻止删除已设置该标志的 ACE 的代码。然而，哪些 ACE 应被视为 Critical 取决于分配新安全描述符的代码，而诸如 `SeSetSecurityInformationEx` 之类的 API 并不强制执行此规则。因此，不要依赖 Critical 标志来执行任何特定操作。如果你在用户模式下使用安全描述符，你可以按任何你喜欢的方式处理该标志。*

如果更改容器上的可继承 ACE，会发生什么？安全描述符中的更改会传播到所有现有子对象吗？简而言之，不会。从技术上讲，类型可以实现这种自动传播行为，但没有任何类型这样做。相反，这取决于用户模式组件来处理。接下来，我们将研究实现这种传播的用户模式 Win32 API。

### Win32 安全 API

大多数应用程序不会直接调用内核系统调用来读取或设置安全描述符。相反，它们使用一系列 Win32 API。虽然我们不会在此讨论每一个可用的 API，但我们将涵盖 API 在底层系统调用之上添加的一些额外功能。

Win32 实现了 `GetKernelObjectSecurity` 和 `SetKernelObjectSecurity` API，它们分别封装了 `NtQuerySecurityObject` 和 `NtSetSecurityObject`。同样，Win32 API `CreatePrivateObjectSecurityEx` 和 `SetPrivateObjectSecurityEx` 分别封装了 `RtlNewSecurityObjectEx` 和 `RtlSetSecurityObjectEx`。本章讨论的原生 API 的每个属性同样适用于这些 Win32 API。

然而，Win32 还提供了一些更高级的 API：最著名的是 `GetNamedSecurityInfo` 和 `SetNamedSecurityInfo`。这些 API 允许应用程序通过提供路径以及该路径引用的资源类型（而不是句柄）来查询或设置安全描述符。使用路径和类型使这些函数更具通用性；例如，这些 API 不仅支持获取和设置文件和注册表项的安全性，还支持服务、打印机以及 Active Directory 域服务（DS）条目。

要查询或设置安全描述符，API 必须打开指定的资源，然后调用适当的 API 来执行操作。例如，要查询文件的安全描述符，API 将使用 Win32 API `CreateFile` 打开文件，然后调用系统调用 `NtQuerySecurityObject`。然而，要查询打印机的安全描述符，Win32 API 需要使用打印后台处理程序 API `OpenPrinter` 打开打印机，然后在打开的打印机句柄上调用 `GetPrinter` API（因为打印机不是内核对象）。

PowerShell 已经通过 `Get-Acl` 命令使用 `GetNamedSecurityInfo` API；然而，内置命令不支持读取某些安全描述符 ACE，例如强制标签。因此，`NtObjectManager` 模块实现了 `Get-Win32SecurityDescriptor`，它调用 `GetNamedSecurityInfo` 并返回一个 `SecurityDescriptor` 对象。

如果你只想显示安全描述符，可以使用 `Format-Win32SecurityDescriptor` 命令，它接受相同的参数但不返回 `SecurityDescriptor` 对象。代码清单 6-36 提供了几个利用底层 Win32 安全 API 的命令示例。




```
PS> Get-Win32SecurityDescriptor "$env:WinDir"
Owner                       DACL ACE Count SACL ACE Count Integrity Level
-----                       -------------- -------------- ---------------
NT SERVICE\TrustedInstaller 13             NONE           NONE

PS> Format-Win32SecurityDescriptor "MACHINE\SOFTWARE" -Type RegistryKey
-Summary
<Owner> : NT AUTHORITY\SYSTEM
<Group> : NT AUTHORITY\SYSTEM
<DACL> (Protected, Auto Inherited)
BUILTIN\Users: (Allowed)(ContainerInherit)(QueryValue|...)
--snip--
```


*代码清单 6-36：`Get-Win32SecurityDescriptor` 和 `Format-Win32SecurityDescriptor` 的用法示例*

我们首先使用 `Get-Win32SecurityDescriptor` 查询 *Windows* 目录的安全描述符，此处为 `$env:WinDir`。请注意，我们未指定要查询的资源类型，因为它默认为文件。在第二个示例中，我们使用 `Format-Win32SecurityDescriptor` 显示 *MACHINE\SOFTWARE* 项的安全描述符。此键路径对应于 Win32 *HKEY_LOCAL_MACHINE\SOFTWARE* 键路径。我们需要通过指定 `Type` 参数来指示我们正在查询注册表项；否则，命令将尝试将路径作为文件打开，这很可能无法工作。

> 注意
>
> *要查找每种受支持对象类型的路径格式，请参阅 `SE_OBJECT_TYPE` 枚举的 API 文档，该枚举用于在 `GetNamedSecurityInfo` 和 `SetNamedSecurityInfo` API 中指定资源类型。*

`SetNamedSecurityInfo` API 更为复杂，因为它实现了跨层次结构（例如，跨文件目录树）的自动继承。正如我们之前讨论的，如果使用 `NtSetSecurityObject` 系统调用设置文件的安全描述符，任何新的可继承 ACE 都不会传播到现有的子对象。如果使用 `SetNamedSecurityInfo` 在文件目录上设置安全描述符，API 将枚举所有子文件和目录，并尝试更新每个子对象的安全描述符。

`SetNamedSecurityInfo` API 通过查询子对象的安全描述符并调用 `RtlNewSecurityObjectEx` 将其用作创建者安全描述符，同时从父目录获取父安全描述符，从而生成新的安全描述符。`DaclAutoInherit` 和 `SaclAutoInherit` 标志始终被设置，以将创建者安全描述符中的任何显式 ACE 合并到新的安全描述符中。

PowerShell 通过 `Set-Win32SecurityDescriptor` 命令公开 `SetNamedSecurityInfo` API，如 代码清单 6-37 所示。




```
PS> $path = Join-Path "$env:TEMP" "TestFolder"
❶ PS> Use-NtObject($f = New-NtFile $path -Win32Path -Options DirectoryFile
-Disposition OpenIf) {
    Set-NtSecurityDescriptor $f "D:AIARP(A;OICI;GA;;;WD)" Dacl
}

PS> $item = Join-Path $path test.txt
PS> "Hello World!" | Set-Content -Path $item
PS> Format-Win32SecurityDescriptor $item -Summary -SecurityInformation Dacl
<DACL> (Auto Inherited)
❷ Everyone: (Allowed)(Inherited)(Full Access)

PS> $sd = Get-Win32SecurityDescriptor $path
PS> Add-NtSecurityDescriptorAce $sd -KnownSid Anonymous -Access GenericAll
-Flags ObjectInherit,ContainerInherit,InheritOnly
❸ PS> Set-Win32SecurityDescriptor $path $sd Dacl
PS> Format-Win32SecurityDescriptor $item -Summary -SecurityInformation Dacl
<DACL> (Auto Inherited)
Everyone: (Allowed)(Inherited)(Full Access)
❹ NT AUTHORITY\ANONYMOUS LOGON: (Allowed)(Inherited)(Full Access)
```


*代码清单 6-37：使用 `Set-Win32SecurityDescriptor` 测试自动继承*

代码清单 6-37 演示了 `SetNamedSecurityInfo` 对文件的自动继承行为。我们首先在系统驱动器根目录下创建 *TestFolder* 目录，然后设置其安全描述符，使其包含一个针对 *Everyone* 组的可继承 ACE，并设置 `DaclAutoInherited` 和 `DaclProtected` 标志 ❶。接下来，我们在该目录内创建一个文本文件并打印其安全描述符。该 DACL 包含文本文件从父目录继承的单个 ACE ❷。

然后，我们从目录获取安全描述符，并为匿名用户添加一个新的可继承 ACE。我们使用此安全描述符通过 `Set-Win32SecurityDescriptor` 设置父目录的 DACL ❸。再次打印文本文件的安全描述符，我们现在看到它有两个 ACE，因为匿名用户的 ACE 已被添加 ❹。如果我们使用 `Set-NtSecurityDescriptor` 设置父目录的安全描述符，则不会发生这种继承。

由于 `SetNamedSecurityInfo` 始终使用自动继承，应用受保护的安全描述符控制标志（如 `DaclProtected` 或 `SaclProtected`）成为阻止 ACE 自动传播的重要方式。

奇怪的是，该 API 不允许您直接在安全描述符中指定 `DaclProtected` 和 `SaclProtected` 控制标志。相反，它引入了一些额外的 `SecurityInformation` 标志来处理控制标志的设置和取消设置。要设置受保护的安全描述符控制标志，您可以使用 `ProtectedDacl` 和 `ProtectedSacl` 标志作为 `SecurityInformation`。要取消设置标志，请使用 `UnprotectedDacl` 和 `UnprotectedSacl`。代码清单 6-38 提供了设置和取消设置 DACL 受保护控制标志的示例。




```
PS> $path = Join-Path "$env:TEMP\TestFolder" "test.txt"
❶ PS> $sd = New-NtSecurityDescriptor "D:(A;;GA;;;AU)"
PS> Set-Win32SecurityDescriptor $path $sd Dacl,ProtectedDacl
PS> Format-Win32SecurityDescriptor $path -Summary -SecurityInformation Dacl
❷ <DACL> (Protected, Auto Inherited)
NT AUTHORITY\Authenticated Users: (Allowed)(None)(Full Access)

❸ PS> Set-Win32SecurityDescriptor $path $sd Dacl,UnprotectedDacl
PS> Format-Win32SecurityDescriptor $path -Summary -SecurityInformation Dacl
❹ <DACL> (Auto Inherited)
NT AUTHORITY\Authenticated Users: (Allowed)(None)(Full Access)
Everyone: (Allowed)(Inherited)(Full Access)
NT AUTHORITY\ANONYMOUS LOGON: (Allowed)(Inherited)(Full Access)
```


*代码清单 6-38：测试 ProtectedDacl 和 UnprotectedDacl SecurityInformation 标志*

此脚本假定您已运行 代码清单 6-37，因为它复用了那里创建的文件。我们创建一个新的安全描述符，其中包含一个针对 *Authenticated Users* 组的单个 ACE，并使用 `ProtectedDacl` 和 `Dacl` 标志将其分配给文件 ❶。结果，DACL 的受保护控制标志现在已在文件上设置 ❷。请注意，代码清单 6-37 中继承的 ACE 已被移除；只剩下新的显式 ACE。

然后，我们使用 `UnprotectedDacl` 标志再次分配安全描述符 ❸。这次，当我们打印安全描述符时，可以看到它不再设置受保护的控制标志 ❹。此外，API 会从父目录恢复继承的 ACE，并将它们与 *Authenticated Users* 组的显式 ACE 合并。

当我们指定 `UnprotectedDacl` 标志时命令的行为向您展示了如何恢复任何文件的继承 ACE。如果您指定一个空的 DACL，以便不会合并显式 ACE，并额外指定 `UnprotectedDacl` 标志，您将把安全描述符重置为基于其父目录的版本。为简化此操作，PowerShell 模块包含 `Reset-Win32SecurityDescriptor` 命令（代码清单 6-39）。




```
PS> $path = Join-Path "$env:TEMP\TestFolder" "test.txt"
PS> Reset-Win32SecurityDescriptor $path Dacl
PS> Format-Win32SecurityDescriptor $path -Summary -SecurityInformation Dacl
<DACL> (Auto Inherited)
Everyone: (Allowed)(Inherited)(Full Access)
NT AUTHORITY\ANONYMOUS LOGON: (Allowed)(Inherited)(Full Access)
```


*代码清单 6-39：使用 Reset-Win32SecurityDescriptor 重置目录的安全性*

在此清单中，我们调用 `Reset-Win32SecurityDescriptor`，传入文件路径并请求重置 DACL。当我们显示文件的安全描述符时，现在发现它与父目录的安全描述符匹配，如 代码清单 6-37 所示。

自动继承的危险

Win32 安全 API 的自动继承功能对应用程序来说很方便，它们只需设置一个可继承的安全描述符即可将其应用于任何子资源。然而，自动继承引入了安全风险，尤其是在特权应用程序或服务使用它时。

风险在于，如果特权应用程序在恶意用户控制父安全描述符的情况下，被诱骗重置继承的安全设置。例如，CVE-2018-0983 是特权存储服务中的一个安全漏洞：它调用 `SetNamedSecurityInfo` 来重置用户指定路径文件的安全设置。通过利用一些文件系统技巧，攻击者可以将被重置的文件链接到仅管理员可写的系统文件。然而，`SetNamedSecurityInfo` API 误以为该文件位于用户控制的目录中，因此基于该目录的安全描述符重置了安全描述符，从而授予恶意用户对系统文件的完全访问权限。

微软已修复此问题，Windows 不再支持利用该漏洞所需的文件系统技巧。然而，仍存在其他可能诱骗特权服务的方式。因此，如果你编写代码来设置或重置资源的安全描述符，请特别注意路径的来源。如果路径来自非特权用户，请确保在调用任何 Win32 安全 API 之前模拟调用者。

最后一个要介绍的 API 是 `GetInheritanceSource`，它允许你识别资源继承 ACE 的来源。ACE 被标记为 `Inherited` 标志的原因之一是为了便于分析继承的 ACE。如果没有该标志，API 将无法区分继承和非继承的 ACE。

对于每个设置了 `Inherited` 标志的 ACE，API 会沿父级层次结构向上查找，直到找到一个未设置该标志但包含相同 SID 和访问掩码的可继承 ACE。当然，无法保证找到的 ACE 就是继承 ACE 的实际来源，它可能位于层次结构的更上层。因此，请将 `GetInheritanceSource` 的输出视为纯信息性内容，不要用于安全关键决策。

与其他 Win32 API 一样，`GetInheritanceSource` 支持不同类型。然而，它仅限于具有子-父关系的资源，如文件、注册表键和 DS 对象。你可以通过 `Search-Win32SecurityDescriptor` 命令访问该 API，如 代码清单 6-40 所示。

```
PS> $path = Join-Path "$env:TEMP" "TestFolder"
PS> Search-Win32SecurityDescriptor $path | Format-Table
Name                Depth User                         Access
----                ----- ----                         ------
                    0     Everyone                     GenericAll
                    0     NT AUTHORITY\ANONYMOUS LOGON GenericAll

PS> $path = Join-Path $path "new.txt"
PS> "Hello" | Set-Content $path
PS> Search-Win32SecurityDescriptor $path | Format-Table
Name                Depth User                         Access
----                ----- ----                         ------
C:\Temp\TestFolder\ 1     Everyone                     GenericAll
C:\Temp\TestFolder\ 1     NT AUTHORITY\ANONYMOUS LOGON GenericAll
```

*代码清单 6-40：使用 Search-Win32SecurityDescriptor 枚举继承的 ACE*

我们首先使用在 代码清单 6-38 中创建的目录路径调用 `Search-Win32SecurityDescriptor`。输出是资源 DACL 中 ACE 的列表，包括每个 ACE 继承自的资源名称和层次结构的深度。我们在目录上设置了两个显式 ACE。输出反映为 `Depth` 值为 0，表示该 ACE 未被继承。你还可以看到 `Name` 列为空。

然后我们在目录中创建一个新文件并重新运行命令。在这种情况下，正如你可能预期的，ACE 显示它们都是从父文件夹继承的，`Depth` 为 1。

本节涵盖了 Win32 API 的基础知识。请记住，这些 API 与底层系统调用在行为上存在明显差异，尤其是在继承方面。当你通过 GUI 与资源的安全设置交互时，几乎可以肯定它调用的是某个 Win32 API。

### 服务器安全描述符与复合ACE

让我们以之前讨论创建者SID时简要提及的一个主题来结束本章：服务器安全描述符。内核支持两个文档记录很少的安全描述符控制标志，用于服务器场景：`ServerSecurity` 和 `DaclUntrusted`。我们仅在生成新的安全描述符时使用这些标志，无论是在对象创建时还是显式分配安全描述符时。主要控制标志 `ServerSecurity` 向安全描述符生成代码指示调用者预期要模拟另一个用户。

在模拟期间创建新的安全描述符时，所有者（Owner）和组（Group）SID将默认采用模拟令牌中的值。这可能不是所期望的，因为作为资源的所有者可能授予调用者对该资源的额外访问权限。然而，调用者不能将所有者设置为任意的SID，因为该SID必须能够通过基于模拟令牌的所有者检查。

这正是 `ServerSecurity` 控制标志发挥作用的地方。如果在创建新的安全描述符时，在创建者安全描述符上设置此标志，则所有者和组SID将默认采用调用者的主令牌（Primary Token）中的值，而非模拟令牌。此标志还会将DACL中的所有允许ACE（Allowed ACE）替换为允许复合ACE（AllowedCompound ACE），其结构我们已在第5章中定义。在复合ACE中，服务器SID被设置为主令牌中的所有者SID。代码清单 6-41展示了一个示例。




```
❶ PS> $token = Get-NtToken -Anonymous
PS> $creator = New-NtSecurityDescriptor -Type Mutant
PS> Add-NtSecurityDescriptorAce $creator -KnownSid World -Access GenericAll
PS> $sd = New-NtSecurityDescriptor -Token $token -Creator $creator
PS> Format-NtSecurityDescriptor $sd -Summary -SecurityInformation Owner,Group,Dacl
❷ <Owner> : NT AUTHORITY\ANONYMOUS LOGON
<Group> : NT AUTHORITY\ANONYMOUS LOGON
<DACL>
Everyone: (Allowed)(None)(Full Access)

❸ PS> Set-NtSecurityDescriptorControl $creator ServerSecurity
PS> $sd = New-NtSecurityDescriptor -Token $token -Creator $creator
PS> Format-NtSecurityDescriptor $sd -Summary -SecurityInformation Owner,Group,Dacl
❹ <Owner> : GRAPHITE\user
<Group> : GRAPHITE\None
<DACL>
❺ Everyone: (AllowedCompound)(None)(Full Access)(Server:GRAPHITE\user)
```


*代码清单 6-41：测试ServerSecurity安全描述符控制标志*

我们首先使用匿名用户令牌创建一个新的安全描述符❶。此初始测试未设置 `ServerSecurity` 标志。如预期，所有者和组默认基于匿名用户令牌的值，我们添加的单个ACE保持不变❷。接下来，我们将 `ServerSecurity` 控制标志添加到创建者安全描述符中❸。再次调用 `New-NtSecurityDescriptor` 后，我们发现所有者和组现在被设置为主令牌的默认值，而非匿名用户令牌的值❹。此外，单个ACE已被替换为复合ACE，其服务器SID被设置为主令牌的所有者SID❺。我们将在第7章中讨论复合ACE的更改如何影响访问检查。

`DaclUntrusted` 控制标志与 `ServerSecurity` 配合使用。默认情况下，`ServerSecurity` 假定DACL中的任何复合ACE都是受信任的，并将其原样复制到输出中。当设置了 `DaclUntrusted` 控制标志时，所有复合ACE的服务器SID值都将被设置为主令牌的所有者SID。

如果在创建者安全描述符上设置了 `ServerSecurity` 控制标志，并且新的安全描述符从父级继承了ACE，我们可以将 *CREATOR OWNER SERVER* 和 *CREATOR GROUP SERVER* SID转换为其各自的主令牌值。此外，任何继承的允许ACE都将被转换为复合ACE，但默认DACL中的ACE除外。

### 继承行为总结

理解继承是一个非常重要的主题。表6-8总结了本章讨论的ACL继承规则，以帮助您理解这些规则。

| 父ACL        | 创建者ACL | 自动继承已设置   | 自动继承未设置 |
| :-------------- | :---------- | :----------------- | :------------------- |
| 无            | 无        | 默认            | 默认              |
| 无            | 存在     | 创建者            | 创建者              |
| 不可继承 | 无        | 默认            | 默认              |
| 可继承     | 无        | 父级             | 父级               |
| 不可继承 | 存在     | 创建者            | 创建者              |
| 可继承     | 存在     | 父级和创建者 | 创建者              |
| 不可继承 | 受保护   | 创建者            | 创建者              |
| 可继承     | 受保护   | 创建者            | 创建者              |
| 不可继承 | 默认   | 创建者            | 创建者              |
| 可继承     | 默认   | 父级             | 父级               |

此表的前两列描述了父ACL和创建者ACL的状态；后两列描述了根据是否设置了`DaclAutoInherit`和/或`SaclAutoInherit`标志而产生的最终ACL。需要考虑六种ACL类型：

**无**    安全描述符中不存在ACL。

**存在**    安全描述符中存在ACL（即使它是NULL或空ACL）。

**不可继承**    ACL没有可继承的ACE。

**可继承**    ACL有一个或多个可继承的ACE。

**受保护**    安全描述符设置了`DaclProtected`或`SaclProtected`控制标志。

**默认**    安全描述符设置了`DaclDefaulted`或`SaclDefaulted`控制标志。

此外，有四种可能的最终ACL：

**默认**    来自令牌的默认DACL，或对于SACL则为空

**创建者**    来自创建者ACL的所有ACE

**父级**    来自父ACL的可继承ACE

**父级和创建者**    来自父级的可继承ACE和来自创建者的显式ACE

当设置了自动继承标志时，新的安全描述符将设置相应的`DaclAutoInherited`或`SaclAutoInherited`控制标志。此外，所有从父ACL继承的ACE都将设置`Inherited` ACE标志。请注意，此表未考虑由于对象ACE、强制标签、服务器安全性和创建者SID引起的行为变化，这些因素增加了更多的复杂性。

### 实际示例

让我们通过一些实际示例来演练本章中学习的命令。

#### 查找对象管理器资源所有者

如本章所述，资源安全描述符的所有者通常是创建该资源的用户。然而，对于管理员来说，所有者通常是内置的 *Administrators* 组。要设置不同的所有者 SID，唯一的方法是使用另一个设置了 Owner 标志的令牌组 SID，或者启用 SeRestorePrivilege 特权。对于非管理员用户，这两种选项都不可用。

因此，了解资源的所有者可以表明该资源是否由更高权限的用户创建和使用。这可以帮助你识别特权应用程序中 Win32 安全 API 的潜在滥用，或者找到低权限用户可能写入的共享资源；特权用户可能会错误处理这些资源，从而引发安全问题。

代码清单 6-42 展示了一个简单示例：查找所有者 SID 与调用者不同的对象管理器资源。




```
PS> function Get-NameAndOwner {❶
     [CmdletBinding()]
     param(
         [parameter(Mandatory, ValueFromPipeline)]
         $Entry,
         [parameter(Mandatory)]
         $Root
      )

      begin {
         $curr_owner = Get-NtSid -Owner ❷
     }

     process {
        $sd = Get-NtSecurityDescriptor -Path $Entry.Name -Root $Root ❸
-TypeName $Entry.NtTypeName -ErrorAction SilentlyContinue
        if ($null -ne $sd -and $sd.Owner.Sid -ne $curr_owner) {
            [PSCustomObject] @{
                Name = $Entry.Name
                NtTypeName = $Entry.NtTypeName
                Owner = $sd.Owner.Sid.Name
                SecurityDescriptor = $sd
            }
        }
    }
}

PS> Use-NtObject($dir = Get-NtDirectory \BaseNamedObjects) {❹
     Get-NtDirectoryEntry $dir | Get-NameAndOwner -Root $dir
}
Name                       NtTypeName  Owner                   SecurityDescriptor
----                       ----------  -----                   ------------------
CLR_PerfMon_DoneEnumEvent  Event       NT AUTHORITY\SYSTEM     O:SYG:SYD:(A;;...
WAMACAPO;3_Read            Event       BUILTIN\Administrators  O:SYG:SYD:(A;;...
WAMACAPO;8_Mem             Section     BUILTIN\Administrators  O:SYG:SYD:(A;;...
--snip--
```


*代码清单 6-42：查找* BaseNamedObjects *中由不同用户拥有的对象*

我们首先定义一个函数来查询对象管理器目录条目的名称和所有者 ❶。该函数使用调用者令牌的所有者 SID 初始化 $curr_owner 变量 ❷。我们将此 SID 与资源的所有者进行比较，以仅返回由不同用户拥有的资源。

对于每个目录条目，我们使用 Get-NtSecurityDescriptor 命令查询其安全描述符 ❸。我们可以为该命令指定路径和根 Directory 对象，以避免手动打开资源。如果我们成功查询到安全描述符，并且所有者 SID 与当前用户的所有者 SID 不匹配，则返回资源的名称、对象类型和所有者 SID。

为了测试新函数，我们打开一个目录（本例中为全局 *BaseNamedObjects* 目录 ❹），并使用 Get-NtDirectoryEntry 查询所有条目，将其通过我们定义的函数进行管道处理。我们收到一个不属于当前用户的资源列表。

例如，输出中包含 WAMACAPO;8_Mem 对象，这是一个共享内存 Section 对象。如果普通用户可以写入此 Section 对象，我们应该进一步调查，因为可能诱骗特权应用程序执行操作，从而提升普通用户的权限。

我们可以使用 Get-NtGrantedAccess 命令配合对象的 SecurityDescriptor 属性来测试我们是否能够获得该 Section 对象的写入访问权限，如 代码清单 6-43 所示。




```
PS> $entry
Name            NtTypeName  Owner                   SecurityDescriptor
----            ----------  -----                   ------------------
WAMACAPO;8_Mem  Section     BUILTIN\Administrators  O:SYG:SYD:(A;;...

PS> Get-NtGrantedAccess -SecurityDescriptor $entry.SecurityDescriptor
Query, MapWrite, MapRead, ReadControl
```


*代码清单 6-43：获取 Section 对象的授予访问权限*

$entry 变量包含我们要检查的对象。我们将其安全描述符传递给 Get-NtGrantedAccess 命令，以返回该资源的最大授予访问权限。在本例中，我们可以看到 MapWrite 存在，这表明 Section 对象可以被映射为可写。

我在 代码清单 6-42 中展示的示例应该能让你了解如何查询任何资源。你可以将目录替换为文件或注册表项，然后调用 Get-NtSecurityDescriptor 并指定路径和根对象来查询每种资源类型的所有者。

然而，对于对象管理器和注册表，有一种更简单的方法来查找所有者 SID。对于注册表，我们可以使用 SecurityDescriptor 属性查找从 *NtObject* 驱动器提供程序返回的条目的安全描述符。例如，我们可以使用以下脚本选择根注册表项的名称和所有者 SID 字段：


```
PS> ls NtKey:\ | Select Name, {$_.SecurityDescriptor.Owner.Sid}
```


我们还可以指定 Recurse 参数来递归执行检查。

如果你想查询文件的所有者 SID，则不能使用此技术，因为文件提供程序不会在其条目中返回安全提供程序。相反，你需要使用内置的 Get-Acl 命令。例如，这里我们查询文件的 ACL：


```
PS> ls C:\ | Get-Acl | Select Path, Owner
```


Get-Acl 命令将所有者返回为用户名，而不是 SID。如果需要，你必须使用 Get-NtSid 命令和 Name 参数手动查找 SID。或者，你可以将 Get-Acl 命令的输出转换为 NtObjectManager 模块中使用的 SecurityDescriptor 对象，如 代码清单 6-44 所示。




```
PS> (Get-Acl C:\ | ConvertTo-NtSecurityDescriptor).Owner.Sid
Name                        Sid
----                        ---
NT SERVICE\TrustedInstaller S-1-5-80-956008885-3418522649-1831038044-...
```


*代码清单 6-44：将 Get-Acl 输出转换为 SecurityDescriptor 对象*

我们使用 ConvertTo-NtSecurityDescriptor PowerShell 命令执行转换。

#### 更改资源的所有权

管理员通常会取得资源的所有权。这使他们能够轻松修改资源的安全描述符并获得完全访问权限。Windows 提供了多种工具来实现此操作，例如 *takeown.exe*，它可以将文件的所有者设置为当前用户。然而，手动完成更改所有者的过程将有助于你深入理解其工作原理。请以管理员身份运行 代码清单 6-45 中的命令。




```
PS> $new_dir = New-NtDirectory "ABC" -Win32Path
PS> Get-NtSecurityDescriptor $new_dir | Select {$_.Owner.Sid.Name}
$_.Owner.Sid.Name
-----------------
BUILTIN\Administrators

PS> Enable-NtTokenPrivilege SeRestorePrivilege
PS> Use-NtObject($dir = Get-NtDirectory "ABC" -Win32Path -Access WriteOwner) {
    $sid = Get-NtSid -KnownSid World
    $sd = New-NtSecurityDescriptor -Owner $sid
    Set-NtSecurityDescriptor $dir $sd -SecurityInformation Owner
}

PS> Get-NtSecurityDescriptor $new_dir | Select {$_.Owner.Sid.Name}
$_.Owner.Sid.Name
-----------------
Everyone

PS> $new_dir.Close()
```


*代码清单 6-45：为目录对象设置任意所有者*

我们首先创建一个新的目录对象，以便在其上执行操作。（我们避免修改现有资源，因为这可能会破坏系统。）然后，我们查询该资源当前的所有者 SID。在此例中，由于我们以管理员身份运行此脚本，因此所有者设置为 *Administrators* 组。

接下来，我们启用 SeRestorePrivilege 特权。仅当我们希望设置任意所有者 SID 时，才需要执行此操作。如果我们希望设置允许的 SID，则可以跳过此行。然后，我们再次打开该目录，但仅请求 WriteOwner 访问权限。

现在，我们可以创建一个安全描述符，仅将所有者 SID 设置为 World SID。为此，我们调用 Set-NtSecurityDescriptor PowerShell 命令，仅指定 Owner 标志。如果你未启用 SeRestorePrivilege，此操作将失败，并返回 STATUS_INVALID_OWNER 状态代码。为了确认我们已更改所有者 SID，我们再次查询它，确认其现在设置为 Everyone（World SID 的名称）。

你可以将同一组操作应用于任何资源类型，包括注册表项和文件：只需更改用于打开资源的命令即可。是否授予你 WriteOwner 访问权限取决于访问检查过程的具体细节。在 第 7 章 中，你将了解访问检查根据某些条件自动授予 WriteOwner 访问权限的几种情况。

### 总结

本章首先概述了如何使用 `Get-NtObjectSecurity` 命令读取现有内核资源的安全描述符。我们介绍了定义该命令应读取安全描述符哪些部分的安全信息标志，并概述了访问存储在 SACL 中的审计信息所遵循的特殊规则。

随后，我们讨论了如何在资源创建过程中或通过修改现有资源来分配安全描述符。在此过程中，您了解了 ACL 继承和自动继承。我们还讨论了 Win32 API（特别是 `SetNamedSecurityInfo`）的行为，以及该 API 如何实现自动继承，尽管内核并未显式实现这一功能。最后，我们概述了文档记录较少的服务器安全描述符和复合 ACE。在下一章中，我们将（终于）讨论 Windows 如何结合令牌和安全描述符来检查用户是否有权访问资源。

## 7. 访问检查过程

我们已经介绍了SRM的前两个组成部分：安全访问令牌和安全描述符。现在，我们将定义其最后一个组成部分：访问检查过程，它接收令牌和安全描述符，并应用一套固定的规则来确定应用程序是否可以访问资源。

我们将首先讨论可用于执行访问检查的API。然后，我们将深入探讨Windows内核中访问检查的实现细节，详细说明该检查如何处理安全描述符和令牌对象的不同部分，以生成资源的最终授予访问值。在此过程中，我们将使用PowerShell脚本开发自己的基本访问检查过程实现。

### 执行访问检查

当调用者尝试打开资源时，内核会基于调用者的身份执行访问检查。用于执行访问检查的API取决于它是从内核模式还是用户模式被调用的。我们首先描述内核模式的API。

#### 内核模式访问检查

`SeAccessCheck` API 在内核模式下实现了访问检查过程。它接受以下参数：

**安全描述符**    用于检查的安全描述符；必须包含所有者和组SID

**安全主体上下文**    调用者的主令牌和模拟令牌

**期望访问**    调用者请求访问的访问掩码

**访问模式**    调用者的访问模式，设置为`UserMode`或`KernelMode`

**通用映射**    类型特定的通用映射

该API返回四个值：

**授予的访问**    用户获得访问的访问掩码

**访问状态代码**    指示访问检查结果的NT状态代码

**特权**    访问检查期间使用的任何特权

**成功代码**    布尔值；如果为TRUE，则访问检查成功

如果访问检查成功，API会将授予的访问设置为期望的访问参数，成功代码设置为true，访问状态代码设置为`STATUS_SUCCESS`。然而，如果期望访问中的任何位未获得，它会将授予的访问设置为0，成功代码设置为false，访问状态代码设置为`STATUS_ACCESS_DENIED`。

您可能想知道，如果期望访问中的所有位必须获得才能表示成功，为什么API还要费心返回授予的访问值。原因是这种行为支持`MaximumAllowed`访问掩码位，调用者可以在期望访问参数中设置该位。如果该位被设置且访问检查至少授予了一项访问，API会返回`STATUS_SUCCESS`，并将授予的访问设置为最大允许访问。

安全主体上下文参数是指向`SECURITY_SUBJECT_CONTEXT`结构的指针，该结构包含调用者的主令牌以及调用者线程的任何模拟令牌。通常，内核代码会使用内核API `SeCaptureSubjectContext`来初始化该结构并为当前调用者收集正确的令牌。如果捕获了模拟令牌，它必须处于模拟级别或以上；否则，API将失败，访问状态代码将设置为`STATUS_BAD_IMPERSONATION_LEVEL`。

请注意，对`SeAccessCheck`的调用可能不在发出原始资源请求的线程中发生。例如，检查可能已委托给系统进程中的后台线程。内核可以从原始线程捕获主体上下文，然后将该上下文传递给调用`SeAccessCheck`的线程，以确保访问检查使用正确的身份。

##### 访问模式

访问模式参数有两个可能的值：`UserMode`和`KernelMode`。如果您将此参数传递为`UserMode`，所有访问检查将正常进行。然而，如果您传递`KernelMode`，内核将禁用所有访问检查。为什么您会想要调用`SeAccessCheck`而不强制任何安全性呢？通常，您不会直接以`KernelMode`值调用该API。相反，该参数将被设置为调用线程的`PreviousMode`参数的值，该值存储在线程的内核对象结构中。当您从用户模式应用程序调用系统调用时，`PreviousMode`值被设置为`UserMode`，并传递给任何需要`AccessMode`设置的API。

因此，内核通常强制执行所有访问检查。图7-1显示了用户模式应用程序调用`NtCreateMutant`系统调用时的描述行为。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure7-1.webp)

图7-1：调用`NtCreateMutant`系统调用时线程的`PreviousMode`值

尽管图7-1中调用`SeAccessCheck`的线程正在执行内核代码，但线程的`PreviousMode`值反映了调用是从`UserMode`开始的。因此，指定给`SeAccessCheck`的`AccessMode`参数将是`UserMode`，内核将强制执行访问检查。

将线程的 `PreviousMode` 值从 `UserMode` 转换为 `KernelMode` 的最常见方式是，现有内核代码通过其 `Zw` 形式调用系统调用，例如 `ZwCreateMutant`。当进行此类调用时，系统调用分发会正确识别先前的执行发生在内核中，并将 `PreviousMode` 设置为 `KernelMode`。图 7-2 展示了线程的 `PreviousMode` 从 `UserMode` 到 `KernelMode` 的转换过程。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure7-2.webp)

图 7-2：调用 `ZwCreateMutant` 后，线程的 `PreviousMode` 值被设置为 `KernelMode`

在 图 7-2 中，用户模式应用程序调用一个假设的内核系统调用 `NtSomeOtherCall`，该调用内部调用 `ZwCreateMutant`。在 `NtSomeOtherCall` 函数中执行的代码在 `PreviousMode` 值设置为 `UserMode` 的情况下运行。然而，一旦它调用 `ZwCreateMutant`，在系统调用期间模式将变为 `KernelMode`。在这种情况下，由于 `ZwCreateMutant` 会调用 `SeAccessCheck` 来确定调用者是否有权访问 Mutant 对象，该 API 将收到设置为 `KernelMode` 的 `AccessMode`，从而禁用访问检查。

如果假设的 `NtSomeOtherCall` 允许用户模式应用程序影响 Mutant 对象的创建位置，这种行为可能会引入安全问题。一旦访问检查被禁用，就可能在该用户通常无权访问的位置创建或修改 Mutant。

##### 内存指针检查

访问模式参数还有第二个用途：当指定 `UserMode` 时，内核将检查作为参数传递给内核 API 的任何指针，以确保它们不指向内核内存位置。这是一个重要的安全限制；它防止用户模式应用程序强制内核 API 读取或写入其不应访问的内核内存。

指定 `KernelMode` 会在禁用访问检查的同时禁用这些指针检查。这种行为的混合可能会引入安全问题：内核模式驱动程序可能只想禁用指针检查，但无意中也禁用了访问检查。

调用者如何指示访问模式参数的不同用途取决于所使用的内核 API。例如，有时可以指定两个 `AccessMode` 值，一个用于指针检查，一个用于访问检查。更常见的方法是指定一个标志给调用；例如，传递给系统调用的 `OBJECT_ATTRIBUTES` 结构有一个名为 `ForceAccessCheck` 的标志，该标志禁用指针检查，但保持访问检查启用。

如果您正在分析内核驱动程序，值得注意未设置 `ForceAccessCheck` 标志的 `Zw` API 的使用情况。如果非管理员用户可以控制调用的目标对象管理器路径，那么很可能存在安全漏洞。例如，CVE-2020-17136 是负责实现 Microsoft OneDrive 远程文件系统的内核驱动程序中的一个漏洞。问题发生的原因是驱动程序向 Explorer shell 公开的 API 在创建基于云的文件时未设置 `ForceAccessCheck` 标志。因此，调用内核驱动程序中 API 的用户可以在文件系统上任意位置创建任意文件，从而允许他们获得管理员权限。

#### 用户模式访问检查

为了支持用户模式应用程序，内核通过 `NtAccessCheck` 系统调用公开其访问检查实现。该系统调用使用与 `SeAccessCheck` API 相同的访问检查算法；然而，它针对用户模式调用者的独特行为进行了调整。系统调用的参数如下：

**安全描述符**    用于检查的安全描述符；必须包含所有者组 SID

**客户端令牌**    调用者模拟令牌的句柄

**所需访问权限**    调用者请求的访问权限的访问掩码

**通用映射**    类型特定的通用映射

该 API 返回四个值：

**授予的访问权限**    用户获得的访问权限的访问掩码

**访问状态代码**    指示访问检查结果的 NT 状态代码

**特权**    访问检查期间使用的任何特权

**NT 成功代码**    指示系统调用状态的单独 NT 状态代码

你会注意到，内核API中存在的某些参数在这里缺失了。例如，没有必要指定访问模式，因为它总是会被设置为调用者的模式（对于用户模式调用者而言是UserMode）。此外，调用者的身份现在是一个模拟令牌的句柄，而不是主体上下文。这个句柄必须具有查询访问权限才能用于访问检查。如果你想针对主令牌执行访问检查，你需要先将该令牌复制为模拟令牌。

另一个区别是，用户模式下使用的模拟令牌可以低至标识级别。这种差异的原因在于，系统调用是为那些想要检查调用者权限的用户服务设计的，而调用者可能已经授予了标识级别的令牌访问权限；这种情况必须被考虑在内。

系统调用还返回一个额外的NT状态码，而不是内核API返回的布尔值。返回值指示传递给系统调用的参数是否存在问题。例如，如果安全描述符没有同时设置所有者SID和组SID，系统调用将返回STATUS_INVALID_SECURITY_DESCR。

#### Get-NtGrantedAccess PowerShell命令

我们可以使用NtAccessCheck系统调用来根据安全描述符和访问令牌确定调用者的授予访问权限。PowerShell模块通过Get-NtGrantedAccess命令封装了对NtAccessCheck的调用，如代码清单 7-1所示。




```
❶ PS> $sd = New-NtSecurityDescriptor -EffectiveToken -Type Mutant
PS> Format-NtSecurityDescriptor $sd -Summary
<Owner> : GRAPHITE\user
<Group> : GRAPHITE\None
<DACL>
GRAPHITE\user: (Allowed)(None)(Full Access)
NT AUTHORITY\SYSTEM: (Allowed)(None)(Full Access)
NT AUTHORITY\LogonSessionId_0_795805: (Allowed)(None)(ModifyState|...)

❷ PS> Get-NtGrantedAccess $sd -AsString
Full Access

❸ PS> Get-NtGrantedAccess $sd -Access ModifyState -AsString
ModifyState

❹ PS> Clear-NtSecurityDescriptorDacl $sd
PS> Format-NtSecurityDescriptor $sd -Summary
<Owner> : GRAPHITE\user
<Group> : GRAPHITE\None
<DACL> - <EMPTY>

PS> Get-NtGrantedAccess $sd -AsString
❺ ReadControl|WriteDac
```


*代码清单 7-1：确定调用者的授予访问权限*

我们首先使用EffectiveToken参数创建默认安全描述符❶，并通过格式化确认其正确性。简单来说，系统调用将检查此安全描述符的DACL，查找与令牌中的某个SID匹配的允许ACE；如果存在这样的ACE，它将授予访问掩码。由于DACL中的第一个ACE授予当前用户SID完全访问权限，我们预期检查结果也会授予完全访问权限。

然后我们调用Get-NtGrantedAccess，传入安全描述符❷。我们没有指定显式令牌，因此它使用当前的有效令牌。我们也没有指定访问掩码，这意味着命令检查MaximumAllowed访问，并将结果转换为字符串。它返回完全访问权限，正如我们基于DACL所预期的那样。

接下来，我们测试Get-NtGrantedAccess命令在提供显式访问掩码时使用Access参数❸。命令将根据安全描述符的类型计算出访问掩码枚举，以允许我们指定类型特定的值。我们请求检查ModifyState，因此只收到该访问权限。例如，如果我们正在打开一个Mutant对象的句柄，那么句柄的访问掩码将只授予ModifyState。

最后，为了测试拒绝访问的情况，我们从DACL中移除所有ACE❹。如果没有允许ACE，则不应授予任何访问权限。但当我们再次运行Get-NtGrantedAccess时，我们感到惊讶：我们获得了ReadControl和WriteDac访问权限，而不是什么都没有❺。为了理解为什么我们会收到这些访问级别，我们需要深入访问检查过程的内部机制。我们将在下一节中进行探讨。

### PowerShell 中的访问检查过程

自 Windows NT 首个版本以来，Windows 中的访问检查过程已发生显著变化。这一演变形成了一套复杂的算法，用于根据安全描述符与令牌的组合，计算用户获得的访问权限。图 7-3 中的流程图展示了访问检查过程的主要组成部分。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure7-3.webp)

图 7-3：访问检查过程

第一步是将令牌、安全描述符和所需访问掩码组合起来。随后，访问检查过程利用这些信息执行以下三项主要检查，以确定是授予还是拒绝访问：

**强制访问检查**    当令牌不符合既定策略时，拒绝其对资源的访问

**令牌访问检查**    基于令牌的所有者和特权授予访问权限

**自主访问检查**    基于 DACL 授予或拒绝访问权限

为了更详细地探讨这些步骤，让我们在 PowerShell 中编写一个访问检查过程的基本实现。此 PowerShell 实现不会取代 `Get-NtGrantedAccess` 命令，因为为简化起见，它不会检查最大允许访问权限，也可能不包含较新的功能。即便如此，拥有一个可供分析和调试的实现，有助于您更深入地理解整个流程。

访问检查的实现相当复杂；因此，我们将分阶段构建。您可以在本书示例代码附带的 *chapter7_access_check_impl.psm1* 脚本中获取完整实现。要使用该脚本，请使用以下命令将其作为模块导入：


```
PS> Import-Module .\chapter7_access_check_impl.psm1
```


#### 定义访问检查函数

该模块导出一个用于执行访问检查的顶层函数 `Get-PSGrantedAccess`，如 代码清单 7-2 所示。


```
function Get-PSGrantedAccess {
    param(
        $Token = (Get-NtToken -Effective -Pseudo),
        $SecurityDescriptor,
        $GenericMapping,
        $DesiredAccess
    )

  ❶ $context = @{
        Token = $Token
        SecurityDescriptor = $SecurityDescriptor
        GenericMapping = $GenericMapping
        RemainingAccess = Get-NtAccessMask $DesiredAccess
        Privileges = @()
    }

    ## Test-MandatoryAccess defined below.
  ❷ if (!(Test-MandatoryAccess $context)) {
        return Get-AccessResult STATUS_ACCESS_DENIED
    }

    ## Get-TokenAccess defined below.
    Resolve-TokenAccess $context
  ❸ if (Test-NtAccessMask $context.RemainingAccess -Empty) {
       ❹ return Get-AccessResult STATUS_SUCCESS $context.Privileges
$DesiredAccess
    }

  ❺ if (Test-NtAccessMask $context.RemainingAccess AccessSystemSecurity) {
        return Get-AccessResult STATUS_PRIVILEGE_NOT_HELD
    }

    Get-DiscretionaryAccess $context
  ❻ if (Test-NtAccessMask $context.RemainingAccess -Empty) {
        return Get-AccessResult STATUS_SUCCESS $context.Privileges
$DesiredAccess
    }

  ❼ return Get-AccessResult STATUS_ACCESS_DENIED
}
```


*代码清单 7-2：顶层访问检查函数*

该函数接受本章前面定义的四个参数：令牌、安全描述符、类型的通用映射以及所需访问权限。如果调用者未指定令牌，我们将使用其有效令牌进行后续的访问检查。

函数首先构建一个表示访问检查过程当前状态的上下文 ❶。此处最重要的属性是 `RemainingAccess`。我们最初将此属性设置为 `DesiredAccess` 参数，然后在访问检查过程中，随着权限获得，逐步从该属性中移除相应位。

函数的其余部分遵循 图 7-3 中的流程图。首先执行强制访问检查 ❷。我们将在下一节描述此检查的作用。如果检查失败，则函数以 `STATUS_ACCESS_DENIED` 结束。为简化代码，完整脚本定义了一个辅助函数 `Get-AccessResult` 来构建访问检查的结果。代码清单 7-3 展示了此函数的定义。




```
function Get-AccessResult {
    param(
        $Status,
        $Privileges = @(),
        $GrantedAccess = 0
    )

    $props = @{
        Status = Get-NtStatus -Name $Status -PassStatus
        GrantedAccess = $GrantedAccess
        Privileges = $Privileges
    }
    return [PSCustomObject]$props
}
```


*代码清单 7-3：实现 Get-AccessResult 辅助函数*

接下来，令牌访问检查更新上下文中的 `RemainingAccess` 属性 ❸。如果 `RemainingAccess` 变为空，则我们可以断定已获得所有访问权限，并返回 `STATUS_SUCCESS` ❹。如果非空，则进行第二次检查：如果调用者请求了 `AccessSystemSecurity` 但令牌未授予该权限，则此检查失败 ❺。

最后，执行自主访问检查。与令牌访问检查一样，我们检查 `RemainingAccess` 属性：如果为空，则调用者已获得其请求的所有访问权限 ❻；否则，拒绝访问 ❼。有了上述概述，让我们逐一深入探讨每项检查的细节。

#### 执行强制访问检查

Windows Vista 引入了一项名为 *强制完整性控制 (MIC)* 的功能，它利用令牌的完整性级别和强制标签 ACE，基于通用策略来控制资源访问。MIC 是一种强制访问检查 (MAC)。MAC 的关键行为是它不能授予对资源的访问权限；它只能拒绝访问。如果调用者请求的访问权限超出策略允许的范围，访问检查将立即拒绝访问，并且如果 MAC 拒绝访问，则永远不会检查 DACL。由于非特权用户无法绕过此检查，因此它被视为强制性的。

在最新版本的Windows中，访问检查过程除了MIC外还会执行两项额外的强制检查。这些检查实现了类似的行为，因此我们将它们归为一组。代码清单 7-4定义了我们在代码清单 7-2中调用的Test-MandatoryAccess函数。




```
function Test-MandatoryAccess {
    param($Context)

    ## Test-ProcessTrustLevel is defined below.
    if (!(Test-ProcessTrustLevel $Context)) {
        return $false
    }

    ## Test-AccessFilter is defined below.
    if (!(Test-AccessFilter $Context)) {
        return $false
    }

    ## Test-MandatoryIntegrityLevel is defined below.
    if (!(Test-MandatoryIntegrityLevel $Context)) {
        return $false
    }

    return $true
}
```


*代码清单 7-4：实现Test-MandatoryAccess函数*

此函数执行三项检查：Test-ProcessTrustLevel、Test-AccessFilter和Test-MandatoryIntegrityLevel。如果其中任何一项检查失败，则整个访问检查过程失败，返回STATUS_ACCESS_DENIED。让我们逐一详细说明每项检查。

##### 进程信任级别检查

Windows Vista引入了*受保护进程*，这些进程即使是管理员也无法操纵和破坏。受保护进程的原始目的是保护媒体内容。然而，微软此后将其扩展以覆盖一系列用途，例如保护防病毒服务和虚拟机。

令牌可以被分配一个*进程信任级别SID*。该SID取决于受保护进程的保护级别，并在创建此类进程时分配。为了限制对资源的访问，访问检查过程会确定令牌的SID是否比安全描述符中的信任级别SID具有同等或更高的信任级别。

当一个SID被认为比另一个SID具有同等或更高的信任级别时，称其*支配*另一个SID。要检查一个进程信任级别SID是否支配另一个，可以调用RtlSidDominatesForTrust API或使用带Dominates参数的Compare-NtSid命令。代码清单 7-5将检查进程信任级别的算法（存储在进程信任标签ACE中）转换为PowerShell。




```
function Test-ProcessTrustLevel {
    param($Context)

  ❶ $trust_level = Get-NtTokenSid $Token -TrustLevel
    if ($null -eq $trust_level) {
        $trust_level = Get-NtSid -TrustType None -TrustLevel None
    }

  ❷ $access = Get-NtAccessMask 0xFFFFFFFF
    $sacl = Get-NtSecurityDescriptorSacl $Context.SecurityDescriptor
    foreach($ace in $sacl) {
      ❸ if (!$ace.IsProcessTrustLabelAce -or $ace.IsInheritOnly) {
            continue
        }

      ❹ if (!(Compare-NtSid $trust_level $ace.Sid -Dominates)) {
            $access = Get-NtAccessMask $ace
        }
        break
    }

    $access = Grant-NtAccessMask $access AccessSystemSecurity
  ❺ return Test-NtAccessMask $access $Context.RemainingAccess -All
}
```


*代码清单 7-5：进程信任级别检查算法*

要检查进程信任级别，我们需要查询当前令牌的SID❶。如果令牌没有信任级别SID，则我们定义最低可能的SID。接下来，我们将访问掩码初始化为所有位均设置❷。

然后我们枚举SACL中的值，检查除InheritOnly之外的任何进程信任标签ACE❸。当我们找到相关的ACE时，我们将其SID与为令牌查询的SID进行比较❹。如果ACE的SID支配，则令牌具有较低的保护级别，访问掩码被设置为ACE中的值。

最后，我们将访问掩码与调用者请求的剩余访问权限进行比较❺。如果访问掩码中的所有位都存在于剩余访问权限中，则函数返回True，表示进程信任级别检查成功。请注意，无论ACE中的掩码如何，该检查总是添加AccessSystemSecurity。

让我们测试进程信任标签ACE的行为。我们不创建新的受保护进程，而是使用匿名用户令牌的进程信任级别SID进行访问检查。为了简化测试，我们将定义一个可重用的辅助函数。这个在代码清单 7-6中的函数将创建一个默认安全描述符，授予当前用户和匿名用户访问权限。每当我们需要测试的安全描述符时，我们可以调用此函数并使用返回的值。




```
PS> function New-BaseSD {
    $owner = Get-NtSid -KnownSid LocalSystem
    $sd = New-NtSecurityDescriptor -Owner $owner -Group $owner -Type Mutant
    Add-NtSecurityDescriptorAce $sd -KnownSid Anonymous -Access GenericAll
    $sid = Get-NtSid
    Add-NtSecurityDescriptorAce $sd -Sid $sid -Access GenericAll
    Set-NtSecurityDescriptorIntegrityLevel $sd Untrusted
    Edit-NtSecurityDescriptor $sd -MapGeneric
    return $sd
}
```


*代码清单 7-6：定义用于测试的辅助函数*

New-BaseSD函数创建一个基本安全描述符，其所有者和组设置为*SYSTEM*用户。然后它为匿名用户和当前用户SID添加一个允许ACE，授予他们完全访问权限。它还将强制标签设置为不可信完整性级别（您将在本章稍后的“强制完整性级别检查”一节中了解完整性级别的重要性）。最后，它将任何通用访问映射为Mutant类型特定访问。现在让我们测试进程信任标签，如代码清单 7-7所示。




```
❶ PS> $sd = New-BaseSD
PS> $trust_sid = Get-NtSid -TrustType ProtectedLight -TrustLevel Windows
PS> Add-NtSecurityDescriptorAce $sd -Type ProcessTrustLabel 
-Access ModifyState -Sid $trust_sid
PS> Get-NtGrantedAccess $sd -AsString
❷ ModifyState

❸ PS> $token = Get-NtToken -Anonymous
PS> $anon_trust_sid = Get-NtTokenSid -Token $token -TrustLevel
PS> Compare-NtSid $anon_trust_sid $trust_sid -Dominates
❹ True
PS> Get-NtGrantedAccess $sd -Token $token -AsString
❺ Full Access
```


*代码清单 7-7：测试进程信任标签ACE*

首先，我们创建基础安全描述符并添加一个进程信任标签，仅授予其进程信任级别不支配进程信任标签的令牌ModifyState访问权限❶。当我们运行访问检查时，我们看到有效令牌（没有任何进程信任级别）仅获得ModifyState访问权限❷，表明进程信任标签正在被强制执行。

接下来，我们使用 `Get-NtToken` 获取匿名用户的令牌句柄，查询其进程信任级别 SID，并将其与我们添加到安全描述符中的 SID 进行比较 ❸。调用 `Compare-NtSid` 返回 `True` ❹，表明令牌的进程信任级别 SID 支配了安全描述符中的 SID。为了确认这一点，我们执行访问检查，发现匿名用户的令牌获得完全访问权限 ❺，这意味着进程信任标签并未限制其访问。

您可能会想，是否可以通过模拟匿名令牌来绕过进程信任标签。请记住，在用户模式下我们调用的是 `NtAccessCheck`，它仅接受一个令牌句柄，而内核中的 `SeAccessCheck` 同时接受主令牌和模拟令牌。在内核验证进程信任标签之前，它会检查两个令牌并选择信任级别较低的那个。因此，如果模拟令牌是受信任的，但您的主令牌不受信任，则有效信任级别将是不受信任的。

当为资源分配进程信任标签 ACE 时，Windows 会执行二次安全检查。虽然您只需要 `WriteDac` 访问权限即可设置进程信任标签，但如果您的有效信任级别不支配该标签的信任级别，则无法更改或移除该 ACE。这可以防止您设置新的、任意的进程信任标签 ACE。Microsoft 利用此能力检查与 Windows 应用程序相关的某些文件是否被修改，并验证这些文件是由受保护进程创建的。

##### 访问过滤器 ACE

第二个强制访问检查是访问过滤器 ACE。它的工作方式与进程信任标签 ACE 类似，不同之处在于它不是使用进程信任级别来决定是否应用限制性访问掩码，而是使用一个条件表达式，该表达式计算结果为 `True` 或 `False`。如果条件计算结果为 `False`，则该 ACE 的访问掩码会限制访问检查的最大授予访问权限；如果计算结果为 `True`，则忽略访问过滤器。

您可以在 SACL 中拥有多个访问过滤器 ACE。每个计算结果为 `False` 的条件表达式都会进一步移除访问掩码中的权限。因此，如果您匹配了一个 ACE，但未匹配另一个限制为 `GenericRead` 的 ACE，则您获得的最大访问权限将是 `GenericRead`。我们可以用 PowerShell 函数表达此逻辑，如 代码清单 7-8 所示。

```
function Test-AccessFilter {
    param($Context)

    $access = Get-NtAccessMask 0xFFFFFFFF
    $sacl = Get-NtSecurityDescriptorSacl $Context.SecurityDescriptor
    foreach($ace in $sacl) {
        if (!$ace.IsAccessFilterAce -or $ace.IsInheritOnly) {
            continue
        }
      ❶ if (!(Test-NtAceCondition $ace -Token $token)) {
          ❷ $access = $access -band $ace.Mask
        }
    }

    $access = Grant-NtAccessMask $access AccessSystemSecurity
  ❸ return Test-NtAccessMask $access $Context.RemainingAccess -All
}
```

*代码清单 7-8：访问过滤器检查算法*

此算法类似于我们为检查进程信任级别而实现的算法。唯一的区别是我们检查的是条件表达式，而不是 SID ❶。该函数支持多个访问过滤器 ACE；对于每个匹配的 ACE，访问掩码与最终访问掩码进行按位 AND 运算，最终访问掩码初始时所有位均设置为 1 ❷。由于掩码进行 AND 运算，每个 ACE 只能移除访问权限，而不能添加访问权限。检查完所有 ACE 后，我们检查剩余的访问权限以确定检查是成功还是失败 ❸。

在 代码清单 7-9 中，我们测试访问过滤器算法的行为，以确保其按预期工作。

```
PS> $sd = New-BaseSD
❶ PS> Add-NtSecurityDescriptorAce $sd -Type AccessFilter -KnownSid World
-Access ModifyState -Condition "Exists TSA://ProcUnique" -MapGeneric
PS> Format-NtSecurityDescriptor $sd -Summary -SecurityInformation AccessFilter
<Access Filters>
Everyone: (AccessFilter)(None)(ModifyState)(Exists TSA://ProcUnique)

❷ PS> Show-NtTokenEffective -SecurityAttributes
SECURITY ATTRIBUTES
-------------------
Name             Flags                  ValueType Values
----             -----                  --------- ------
TSA://ProcUnique NonInheritable, Unique UInt64    {187, 365588953}

PS> Get-NtGrantedAccess $sd -AsString
❸ Full Access

PS> Use-NtObject($token = Get-NtToken -Anonymous) {
    Get-NtGrantedAccess $sd -Token $token -AsString
}
❹ ModifyState
```

*代码清单 7-9：测试访问过滤器 ACE*

我们向安全描述符添加访问过滤器 ACE，条件表达式为 `"Exists TSA://ProcUnique"` ❶。该表达式检查令牌中是否存在 `TSA://ProcUnique` 安全属性。对于普通用户，此检查应始终返回 `True`；但是，该属性在匿名用户的令牌中不存在。我们将掩码设置为 `ModifyState`，并将 SID 设置为 `Everyone` 组。请注意，SID 不会被验证，因此它可以具有任何值，但使用 `Everyone` 组是惯例。

我们可以使用 `Show-NtTokenEffective` 检查当前有效令牌的安全属性 ❷。获取有效令牌的最大访问权限结果为完全访问权限 ❸，这意味着访问过滤器检查通过且未限制访问。然而，当我们使用匿名用户的令牌重复此操作时，访问过滤器检查失败，访问权限被限制为仅 `ModifyState` ❹。

要设置访问过滤器，您只需要 `WriteDac` 访问权限。那么，如何防止用户移除过滤器呢？显然，访问过滤器本身不应授予 `WriteDac` 访问权限，但如果它确实授予了，您可以将任何更改限制在受保护的进程信任级别内。为此，将 ACE 的 SID 设置为进程信任级别 SID，并设置 `TrustProtected` ACE 标志。这样，具有较低进程信任级别的调用者将无法移除或修改访问过滤器 ACE。

##### 强制完整性级别检查

最后，我们将实现强制完整性级别检查。在SACL中，强制标签ACE的SID代表安全描述符的完整性级别。其掩码表达了强制策略，结合了NoReadUp、NoWriteUp和NoExecuteUp策略，以根据通用映射结构中的GenericRead、GenericWrite和GenericExecute值，确定系统可以授予调用方的最大访问权限。

为了决定是否执行该策略，检查会比较安全描述符和令牌的完整性级别SID。如果令牌的SID支配安全描述符的SID，则不执行任何策略，允许所有访问。然而，如果令牌的SID不支配安全描述符的SID，则任何超出策略值范围的访问请求都会导致访问检查失败，并返回`STATUS_ACCESS_DENIED`。

计算一个完整性级别SID是否支配另一个SID，比计算进程信任级别SID的等效值要简单得多。为此，我们从每个SID中提取最后一个RID，并将它们作为数字进行比较。如果一个完整性级别SID的RID大于或等于另一个，则它支配另一个。

然而，基于通用映射计算策略的访问掩码要复杂得多，因为它需要考虑共享访问权限。我们不会实现计算访问掩码的代码，因为我们可以使用`Get-NtAccessMask`上的一个选项来为我们计算。

在代码清单 7-10中，我们实现了强制完整性级别检查。




```
function Test-MandatoryIntegrityLevel {
    param($Context)

    $token = $Context.Token
    $sd = $Context.SecurityDescriptor
    $mapping = $Context.GenericMapping

  ❶ $policy = Get-NtTokenMandatoryPolicy -Token $token
    if (($policy -band "NoWriteUp") -eq 0) {
        return $true
    }

    if ($sd.HasMandatoryLabelAce) {
        $ace = $sd.GetMandatoryLabel()
        $sd_il_sid = $ace.Sid
      ❷ $access = Get-NtAccessMask $ace.Mask -GenericMapping $mapping
    } else {
      ❸ $sd_il_sid = Get-NtSid -IntegrityLevel Medium
        $access = Get-NtAccessMask -MandatoryLabelPolicy NoWriteUp
-GenericMapping $GenericMapping
    }

  ❹ if (Test-NtTokenPrivilege -Token $token SeRelabelPrivilege) {
        $access = Grant-NtAccessMask $access WriteOwner
    }

  ❺ $il_sid = Get-NtTokenSid -Token $token -Integrity
    if (Compare-NtSid $il_sid $sd_il_sid -Dominates) {
        return $true
    }

    return Test-NtAccessMask $access $Context.RemainingAccess -All
}
```


*代码清单 7-10：强制完整性级别检查算法*

我们首先检查令牌的强制策略❶。在这种情况下，我们检查是否设置了NoWriteUp标志。如果该标志未设置，则我们为此令牌禁用完整性级别检查并返回True。然而，该标志很少被关闭，并且需要`SeTcbPrivilege`特权才能禁用，因此在几乎所有情况下，完整性级别检查都会继续。

接下来，我们需要从强制标签ACE中捕获安全描述符的完整性级别和强制策略。如果ACE存在，我们提取这些值，并使用`Get-NtAccessMask`将策略映射到最大访问掩码❷。如果ACE不存在，算法默认使用Medium完整性级别和NoWriteUp策略❸。

如果令牌具有`SeRelabelPrivilege`特权，我们将WriteOwner访问权限添加回最大访问权限，即使策略将其移除❹。这允许具有`SeRelabelPrivilege`特权的调用方更改安全描述符的强制完整性标签ACE。

然后，我们查询令牌的完整性级别SID，并将其与安全描述符的SID进行比较❺。如果令牌的SID支配安全描述符的SID，则检查通过并允许所有访问。否则，计算出的策略访问掩码必须授予所请求的剩余访问掩码的全部。请注意，我们在此处不像在进程信任级别和访问过滤器检查中那样特殊处理`AccessSystemSecurity`。如果策略包含NoWriteUp（所有资源类型的默认设置），我们会将其移除。

让我们在真实访问检查过程中验证强制完整性级别检查的行为（代码清单 7-11）。




```
PS> $sd = New-BaseSD
PS> Format-NtSecurityDescriptor $sd -SecurityInformation Label -Summary
<Mandatory Label>
❶ Mandatory Label\Untrusted Mandatory Level: (MandatoryLabel)(None)(NoWriteUp)

PS> Use-NtObject($token = Get-NtToken -Anonymous) {
    Format-NtToken $token -Integrity
    Get-NtGrantedAccess $sd -Token $token -AsString
}
INTEGRITY LEVEL
---------------
❷ Untrusted
Full Access

❸ PS> Remove-NtSecurityDescriptorIntegrityLevel $sd
PS> Use-NtObject($token = Get-NtToken -Anonymous) {
    Get-NtGrantedAccess $sd -Token $token -AsString
}
❹ ModifyState|ReadControl|Synchronize
```


*代码清单 7-11：测试强制标签ACE*

我们首先创建一个安全描述符并检查其强制完整性标签。我们可以看到它设置为Untrusted完整性级别，这是最低级别，并且其策略为NoWriteUp❶。然后，我们获取匿名用户令牌的最大访问权限，可以看到其完整性级别为Untrusted❷。由于此完整性级别与安全描述符的完整性级别匹配，令牌被允许完全访问。

为了测试访问掩码限制，我们从安全描述符中移除强制标签ACE，以便访问检查默认使用Medium完整性级别❸。再次运行检查，我们现在得到`ModifyState|ReadControl|Synchronize`❹，这是Mutant对象的完全访问权限，但不包括GenericWrite访问掩码。

这结束了强制访问检查的实现。我们已经看到，该算法实际上由三个独立的检查组成：进程信任级别、访问过滤器和完整性级别。每个检查只能拒绝访问；它永远不会授予额外的访问权限。

#### 执行令牌访问检查

第二个主要检查，即令牌访问检查，使用调用方令牌的属性来决定是否授予某些访问权限。更具体地说，它检查任何特殊特权以及安全描述符的所有者。

与强制访问检查不同，令牌访问检查可以在从令牌的访问掩码中移除所有位后，授予对资源的访问权限。代码清单 7-12 实现了顶层的 Result-TokenAccess 函数。

```
Function Result-TokenAccess {
    param($Context)

    Resolve-TokenPrivilegeAccess $Context
    if (Test-NtAccessMask $Context.RemainingAccess -Empty) {
        return
    }
    return Resolve-TokenOwnerAccess $Context
}
```

*代码清单 7-12：令牌访问检查算法*

该检查很简单。首先，我们使用接下来将定义的函数 Resolve-TokenPrivilegeAccess 检查令牌的特权，并将当前上下文传递给它。如果某些特权已启用，此函数会修改令牌的剩余访问权限；如果剩余访问权限为空，意味着没有剩余的访问权限需要授予，我们可以立即返回。然后，我们调用 Resolve-TokenOwnerAccess，该函数检查令牌是否拥有资源，并且也可以更新 RemainingAccess。让我们深入探讨这些单独的检查。

##### 特权检查

*特权检查*（代码清单 7-13）确定 Token 对象是否启用了三种不同的特权。对于每一种特权，如果该特权已启用，我们授予一个访问掩码，并从剩余访问权限中移除相应的位。

```
function Resolve-TokenPrivilegeAccess {
    param($Context)

    $token = $Context.Token
    $access = $Context.RemainingAccess

  ❶ if ((Test-NtAccessMask $access AccessSystemSecurity) -and
        (Test-NtTokenPrivilege -Token $token SeSecurityPrivilege)) {
        $access = Revoke-NtAccessMask $access AccessSystemSecurity
        $Context.Privileges += "SeSecurityPrivilege"
    }

  ❷ if ((Test-NtAccessMask $access WriteOwner) -and
        (Test-NtTokenPrivilege -Token $token SeTakeOwnershipPrivilege)) {
        $access = Revoke-NtAccessMask $access WriteOwner
        $Context.Privileges += "SeTakeOwnershipPrivilege"
    }

  ❸ if ((Test-NtAccessMask $access WriteOwner) -and
        (Test-NtTokenPrivilege -Token $token SeRelabelPrivilege)) {
        $access = Revoke-NtAccessMask $access WriteOwner
        $Context.Privileges += "SeRelabelPrivilege"
    }

  ❹ $Context.RemainingAccess = $access
}
```

*代码清单 7-13：令牌特权访问检查算法*

首先，我们检查调用者是否请求了 AccessSystemSecurity；如果是，并且 SeSecurityPrivilege 已启用，我们从剩余访问权限中移除 AccessSystemSecurity ❶。我们还会更新已使用的特权列表，以便将其返回给调用者。

接下来，我们对 SeTakeOwnershipPrivilege ❷ 和 SeRelabelPrivilege ❸ 执行类似的检查，如果它们已启用，则从剩余访问权限中移除 WriteOwner。最后，我们使用最终的访问掩码更新 RemainingAccess 值 ❹。

从内核的角度来看，将 WriteOwner 访问权限授予 SeTakeOwnershipPrivilege 和 SeRelabelPrivilege 是合理的，因为修改所有者 SID 和完整性级别需要 WriteOwner 访问权限。然而，这种实现也意味着仅拥有 SeRelabelPrivilege 的令牌可以取得资源的所有权，这可能并非我们总是想要的。幸运的是，即使是管理员默认也不会获得 SeRelabelPrivilege，这使得这个问题影响较小。

让我们对照真实的访问检查过程来验证此函数。以管理员身份运行 代码清单 7-14 中的脚本。

```
PS> $owner = Get-NtSid -KnownSid Null
❶ PS> $sd = New-NtSecurityDescriptor -Type Mutant -Owner $owner
-Group $owner -EmptyDacl
❷ PS> Enable-NtTokenPrivilege SeTakeOwnershipPrivilege
❸ PS> Get-NtGrantedAccess $sd -Access WriteOwner -PassResult
Status               Granted Access Privileges
------               -------------- ----------
❹ STATUS_SUCCESS       WriteOwner     SeTakeOwnershipPrivilege

❺ PS> Disable-NtTokenPrivilege SeTakeOwnershipPrivilege
PS> Get-NtGrantedAccess $sd -Access WriteOwner -PassResult
Status               Granted Access Privileges
------               -------------- ----------
❻ STATUS_ACCESS_DENIED None           NONE
```

*代码清单 7-14：测试令牌特权检查*

我们首先创建一个安全描述符，该描述符不应授予当前用户任何访问权限 ❶。然后，我们启用 SeTakeOwnershipPrivilege ❷。接下来，我们请求对 WriteOwner 访问权限进行访问检查，并指定 PassResult 参数，该参数输出完整的访问检查结果 ❸。结果显示访问检查成功，授予了 WriteOwner 访问权限，但也表明检查使用了 SeTakeOwnershipPrivilege ❹。为了验证我们并非因其他原因获得 WriteOwner 访问权限，我们禁用该特权 ❺ 并重新运行检查。这次，拒绝访问 ❻。

##### 所有者检查

*所有者检查*的存在是为了授予资源所有者 ReadControl 和 WriteDac 访问权限，即使 DACL 未授予该所有者任何其他访问权限。此检查的目的是防止用户将自己锁定在自己的资源之外。如果他们意外更改了 DACL 导致自己不再拥有访问权限，他们仍然可以使用 WriteDac 访问权限将 DACL 恢复到之前的状态。

该检查将安全描述符中的所有者 SID 与所有启用的令牌组（不仅仅是令牌所有者）进行比较，如果找到匹配项则授予访问权限。我们在本章开头，即 代码清单 7-1 中演示了此行为。在 代码清单 7-15 中，我们实现了 Resolve-TokenOwnerAccess 函数。

```
function Resolve-TokenOwnerAccess {
    param($Context)

    $token = $Context.Token
    $sd = $Context.SecurityDescriptor
    $sd_owner = Get-NtSecurityDescriptorOwner $sd
  ❶ if (!(Test-NtTokenGroup -Token $token -Sid $sd_owner.Sid)) {
        return
    }

  ❷ $sids = Select-NtSecurityDescriptorAce $sd
-KnownSid OwnerRights -First -AclType Dacl
    if ($sids.Count -gt 0) {
        return
    }

    $access = $Context.RemainingAccess
  ❸ $Context.RemainingAccess = Revoke-NtAccessMask $access ReadControl,
WriteDac
}
```

*代码清单 7-15：令牌所有者访问检查算法*

我们使用 Test-NtTokenGroup 来检查安全描述符的所有者 SID 是否是令牌中已启用的成员 ❶。如果所有者 SID 不是成员，我们直接返回。如果它是成员，代码随后需要检查 DACL 中是否存在任何 *OWNER RIGHTS* SID（S-1-3-4）❷。如果存在，我们则不遵循默认流程；相反，我们依赖 DACL 检查来授予所有者访问权限。最后，如果两个检查都通过，我们可以从剩余访问权限中移除 ReadControl 和 WriteDac ❸。

在 代码清单 7-16 中，我们在真实的访问检查过程中验证此行为。

```
❶ PS> $owner = Get-NtSid -KnownSid World
PS> $sd = New-NtSecurityDescriptor -Owner $owner -Group $owner
-Type Mutant -EmptyDacl
PS> Get-NtGrantedAccess $sd
❷ ReadControl, WriteDac

❸ PS> Add-NtSecurityDescriptorAce $sd -KnownSid OwnerRights -Access ModifyState
PS> Get-NtGrantedAccess $sd
❹ ModifyState
```

*代码清单 7-16：测试令牌所有者检查*

我们首先创建一个安全描述符，其所有者和组设置为 *Everyone* ❶。同时，我们创建一个具有空DACL的安全描述符，这意味着访问检查过程在计算授予的访问权限时，将仅考虑所有者检查。当我们运行访问检查时，我们获得了ReadControl和WriteDac权限 ❷。

接着，我们添加一个包含 *OWNER RIGHTS* SID 的单一ACE ❸。这会禁用默认的所有者访问权限，并导致访问检查仅授予ACE中指定的访问权限（本例中为ModifyState）。当我们再次运行访问检查时，我们发现唯一获得的访问权限是ModifyState ❹，并且我们不再拥有ReadControl或WriteDac访问权限。

至此，令牌访问检查结束。正如我们所演示的，该算法在处理安全描述符的任何重要部分之前，就可以向调用者授予某些访问权限。这主要是为了允许用户维护对自己资源的访问，以及让管理员能够接管其他用户的文件。现在，让我们继续最后的检查。

#### 执行自主访问检查

我们在一些测试中依赖了DACL的行为。现在，我们将深入探讨DACL检查的具体工作原理。检查DACL看似简单，但细节决定成败。代码清单 7-17 实现了该算法。

```
function Get-DiscretionaryAccess {
    param($Context)

    $token = $Context.Token
    $sd = $Context.SecurityDescriptor
    $access = $Context.RemainingAccess
    $resource_attrs = $null
    if ($sd.ResourceAttributes.Count -gt 0) {
        $resource_attrs = $sd.ResourceAttributes.ResourceAttribute
    }

  ❶ if (!(Test-NtSecurityDescriptor $sd -DaclPresent)
-or (Test-NtSecurityDescriptor $sd -DaclNull)) {
        $Context.RemainingAccess = Get-NtAccessMask 0
        return
    }

    $owner = Get-NtSecurityDescriptorOwner $sd
    $dacl = Get-NtSecurityDescriptorDacl $sd
  ❷ foreach($ace in $dacl) {
      ❸ if ($ace.IsInheritOnly) {
            continue
        }
      ❹ $sid = Get-AceSid $ace -Owner $owner
        $continue_check = $true
        switch($ace.Type) {
            "Allowed" {
              ❺ if (Test-NtTokenGroup -Token $token $sid) {
                    $access = Revoke-NtAccessMask $access $ace.Mask
                }
            }
            "Denied" {
              ❻ if (Test-NtTokenGroup -Token $token $sid -DenyOnly) {
                    if (Test-NtAccessMask $access $ace.Mask) {
                        $continue_check = $false
                    }
                }
            }
            "AllowedCompound" {
                $server_sid = Get-AceSid $ace -Owner $owner
              ❼ if ((Test-NtTokenGroup -Token $token $sid)
-and (Test-NtTokenGroup -Sid $server_sid)) {
                    $access = Revoke-NtAccessMask $access $ace.Mask
                }
            }
            "AllowedCallback" {
              ❽ if ((Test-NtTokenGroup -Token $token $sid)
-and (Test-NtAceCondition $ace -Token $token
-ResourceAttributes $resource_attrs)) {
                    $access = Revoke-NtAccessMask $access $ace.Mask
                }
            }
        }

      ❾ if (!$continue_check -or (Test-NtAccessMask $access -Empty)) {
            break
        }
    }

  ❿ $Context.RemainingAccess = $access
}
```

*代码清单 7-17：自主访问检查算法*

我们首先检查DACL是否存在；如果存在，则检查它是否为NULL ACL ❶。如果没有DACL或只有NULL ACL，则没有需要强制执行的安全性，因此函数清除剩余的访问权限并返回，授予令牌对资源的任何访问权限，只要这些权限未被强制访问检查限制。

一旦确认存在需要检查的DACL，我们就可以枚举其每个ACE ❷。如果ACE是InheritOnly类型，它不会参与检查，因此我们忽略它 ❸。接下来，我们需要使用一个辅助函数（我们将在后面定义）将ACE中的SID映射到我们要检查的SID，即Get-AceSid ❹。该函数将ACE中的 *OWNER RIGHTS* SID 转换为当前安全描述符的所有者，如 代码清单 7-18 所示。

```
function Get-AceSid {
    param(
        $Ace,
        $Owner
    )

    $sid = $Ace.Sid
    if (Compare-NtSid $sid -KnownSid OwnerRights) {
        $sid = $Owner.Sid
    }

    return $sid
}
```

*代码清单 7-18：Get-AceSid 的实现*

有了SID后，我们现在可以根据每个ACE的类型对其进行评估。对于最简单的类型，即允许（Allowed），我们检查SID是否在令牌的启用组中。如果是，我们授予ACE掩码所代表的访问权限，并从剩余的访问权限中移除这些位 ❺。

对于拒绝（Denied）类型，我们也检查SID是否在令牌的组中；但是，此检查必须同时包括启用组和仅拒绝组，因此我们传递DenyOnly参数 ❻。请注意，令牌的用户SID也可能被配置为仅拒绝组，而Test-NtTokenGroup会考虑到这一点。拒绝ACE不会修改剩余的访问权限；相反，函数会将掩码与当前剩余的访问权限进行比较，如果剩余访问权限的任何位也在掩码中设置，则函数拒绝该访问并立即返回剩余的访问权限。

我们涵盖的最后两种ACE类型是允许类型的变体。第一种是允许复合（AllowedCompound），它包含额外的服务器SID。为了执行此检查，函数会比较普通SID和服务器SID与调用者令牌的组，因为这些值可能不同 ❼。（注意，如果使用了 *OWNER RIGHTS* SID，服务器SID应映射到所有者。）仅当两个SID都已启用时，ACE条件才满足。

最后，我们检查允许回调（AllowedCallback）ACE类型。为此，我们再次检查SID，并使用Test-NtAceCondition检查条件表达式是否与令牌匹配 ❽。如果表达式返回True，则ACE条件满足，我们从剩余的访问权限中移除掩码。为了完全实现条件检查，我们还需要从安全描述符中传入任何资源属性（我将在本章稍后的“中心访问策略”一节中更详细地介绍资源属性）。请注意，我们故意不检查拒绝回调（DenyCallback）。这是因为内核不支持拒绝回调ACE，尽管仅用户模式的AuthzAccessCheck API支持。

处理完ACE后，我们检查剩余的访问权限 ❾。如果剩余的访问权限为空，则我们已获得整个请求的访问权限，可以停止处理ACE。这就是为什么我们有一个规范的ACL排序，如 第5章 所讨论的；如果拒绝ACE被放置在允许ACE之后，剩余的访问权限可能变为空，循环可能在检查拒绝ACE之前就退出。

最后，该函数设置 `RemainingAccess` ❿。如果 `RemainingAccess` 的值非空，则访问检查失败并返回 `STATUS_ACCESS_DENIED`。因此，空的 DACL 会阻止所有访问；如果没有 ACE，`RemainingAccess` 永远不会改变，因此在函数结束时它不会为空。

现在我们已经涵盖了所有三种访问检查，你应该对它们的结构有了更好的理解。然而，访问检查过程还有更多内容。在下一节中，我们将讨论该过程如何支持沙箱的实现。

### 沙箱化

在第4章中，我们介绍了两种类型的沙箱令牌：受限令牌（restricted）和lowbox令牌。这些沙箱令牌通过增加额外的检查来修改访问检查过程。让我们更详细地讨论每种令牌类型，首先从受限令牌开始。

#### 受限令牌

使用受限令牌会影响访问检查过程，因为它引入了第二个所有者，并针对受限SID列表执行一次 discretionary 访问检查。在代码清单 7-19中，我们修改了`Resolve-TokenOwnerAccess`函数中的所有者SID检查，以考虑这一点。




```
❶ if (!(Test-NtTokenGroup -Token $token -Sid $sd_owner.Sid)) {
    return
}

if ($token.Restricted -and
❷ !(Test-NtTokenGroup -Token $token -Sid $sd_owner.Sid -Restricted)) {
    return
}
```


*代码清单 7-19：针对受限令牌修改的Get-TokenOwner访问检查*

我们首先执行现有的SID检查❶。如果所有者SID不在令牌组列表中，那么我们不会授予`ReadControl`或`WriteDac`访问权限。接下来是额外的检查❷：如果令牌是受限的，那么我们会检查受限SID列表中的所有者SID，并且仅当所有者SID同时存在于主组列表和受限SID列表中时，才授予令牌`ReadControl`和`WriteDac`访问权限。

我们将对 discretionary 访问检查采用相同的模式，但为了简化，我们会向`Get-DiscretionaryAccess`函数添加一个布尔类型的`Restricted`开关参数，并将其传递给任何对`Test-NtTokenGroup`的调用。例如，我们可以修改在代码清单 7-17中实现的允许ACE检查，使其看起来如代码清单 7-20所示。




```
"Allowed" {
    if (Test-NtTokenGroup -Token $token $sid -Restricted:$Restricted) {
        $access = Revoke-NtAccessMask $access $ace.Mask
    }
}
```


*代码清单 7-20：针对受限令牌修改的允许ACE类型*

在代码清单 7-20中，我们将`Restricted`参数设置为传入`Get-DiscretionaryAccess`的参数值。现在我们需要修改在代码清单 7-2中定义的`Get-PSGrantedAccess`函数，使其对受限令牌调用两次`Get-DiscretionaryAccess`（代码清单 7-21）。




```
❶ $RemainingAccess = $Context.RemainingAccess
Get-DiscretionaryAccess $Context
❷ $success = Test-NtAccessMask $Context.RemainingAccess -Empty

❸ if ($success -and $Token.Restricted) {
  ❹ if (!$Token.WriteRestricted -or
(Test-NtAccessMask $RemainingAccess -WriteRestricted $GenericMapping)) {
        $Context.RemainingAccess = $RemainingAccess
      ❺ Get-DiscretionaryAccess $Context -Restricted
        $success = Test-NtAccessMask $Context.RemainingAccess -Empty
    }
}

❻ if ($success) {
    return Get-AccessResult STATUS_SUCCESS $Context.Privileges $DesiredAccess
}
return Get-AccessResult STATUS_ACCESS_DENIED
```


*代码清单 7-21：修改后的Get-PSGrantedAccess函数以考虑受限令牌*

我们首先捕获现有的`RemainingAccess`值❶，因为 discretionary 访问检查会修改它，而我们希望重复执行该检查第二次。然后我们运行 discretionary 访问检查并将结果保存在一个变量中❷。如果第一次检查成功且令牌是受限的，我们必须执行第二次检查❸。我们还需要考虑令牌是否具有写受限属性，以及剩余的访问权限是否包含写访问❹。我们通过检查传入的通用映射来寻找写访问权限。（请注意，所有者检查不执行写检查，因此理论上它可能授予令牌`WriteDac`访问权限，这被视为一种写访问形式。）

接下来我们再次运行检查，这次使用`Restricted`参数来指示应检查受限SID❺。如果第二次检查也通过，我们将`$success`变量设置为`True`并授予对资源的访问权限❻。

请记住，受限SID检查适用于允许和拒绝两种ACE类型。这意味着如果DACL包含一个引用受限SID列表中SID的拒绝ACE，即使该SID不在普通组列表中，函数也会拒绝访问。

#### lowbox令牌

lowbox令牌的访问检查过程类似于受限令牌。lowbox令牌可以包含一组能力SID，用于执行第二次检查，就像我们使用受限SID列表执行的检查一样。同样，如果访问检查过程未通过正常和能力检查授予访问权限，则访问检查失败。然而，lowbox令牌的访问检查包含一些细微差别：

- 除了能力SID列表外，它还会考虑令牌的包SID。
- 被检查的能力SID必须设置了启用属性标志，才能被视为活动状态。
- 该检查仅适用于允许ACE类型，不适用于拒绝ACE类型。
- NULL DACL不授予完全访问权限。

此外，对于包SID检查，有两个特殊的包SID将匹配任何令牌的包SID：

- *所有应用程序包* (S-1-15-2-1)
- *所有受限应用程序包* (S-1-15-2-2)

在包SID检查期间，如果用于访问检查的令牌设置了`WIN://NOALLAPPPKG`安全属性且值为1，则可以禁用对*ALL APPLICATION PACKAGES* SID的检查。在这种情况下，包SID检查将仅考虑*ALL RESTRICTED APPLICATION PACKAGES* SID。如果该安全属性不存在或设置为0，则访问检查会同时考虑两个特殊的包SID。Microsoft将具有此安全属性的进程称为运行*受限权限AppContainer (LPAC)*。

由于设置令牌的安全属性需要`SeTcbPrivilege`特权，进程创建API提供了一个选项，用于将`WIN://NOALLAPPPKG`安全属性添加到新进程的令牌中。代码清单 7-22展示了针对允许ACE类型的lowbox访问检查的基本实现。您应将此代码添加到代码清单 7-17中的自主访问检查中，位置如注释所示。




```
## Add to start of Get-DiscretionaryAccess.
$ac_access = $context.DesiredAccess
if (!$token.AppContainer) {
    $ac_access = Get-NtAccessMask 0
}

## Replace the Allowed case in the ACE switch statement.
"Allowed" {
    if (Test-NtTokenGroup -Token $token $sid -Restricted:$Restricted) {
      ❶ $access = Revoke-NtAccessMask $access $ace.Mask
    } else {
      ❷ if ($Restricted) {
            break
        }

      ❸ if (Test-NtTokenGroup -Token $token $sid -Capability) {
          ❹ $ac_access = Revoke-NtAccessMask $ac_access $ace.Mask
        }
    }
}

## Add at end of ACE loop.
❺ $effective_access = $access -bor $ac_access
```


*代码清单 7-22：针对允许ACE的lowbox访问检查实现*

第一个测试验证SID是否在令牌的组列表中。如果在组列表中找到该SID，则从剩余的访问检查中移除该掩码❶。如果组测试失败，我们检查它是否为包或能力SID。我们必须确保不会在受限SID模式下进行检查❷，因为该模式不定义lowbox检查。

我们对能力SID的检查包括包SID和*ALL APPLICATION PACKAGES* SID❸。如果找到匹配项，我们从剩余的访问中移除该掩码❹。然而，我们需要为普通SID和AppContainer SID维护单独的剩余访问值。因此，我们创建两个变量：`$access`和`$ac_access`。我们将`$ac_access`变量初始化为原始DesiredAccess的值，而不是当前剩余的访问值，因为除非SID同时匹配允许的包或能力SID ACE，否则我们不会授予所有者权限（如WriteDac）。我们还修改了循环的退出条件，以同时考虑两个剩余访问值❺；两者都必须为空才能退出。

接下来，我们将添加一些额外的检查，以更好地将AppContainer进程与现有的低完整性级别沙箱（如Internet Explorer的保护模式）隔离。我们实施的第一个更改影响强制访问检查。如果对lowbox令牌的检查失败，我们再次检查安全描述符的完整性级别。如果完整性级别低于或等于Medium，我们假定检查成功。尽管lowbox令牌具有Low完整性级别（如第4章所示），这通常会阻止对资源的写入访问，但此行为允许更特权的应用程序授予lowbox令牌对资源的访问权限，同时阻止低完整性级别沙箱。

代码清单 7-23演示了此行为。




```
❶ PS> $sd = New-NtSecurityDescriptor -Owner "BA" -Group "BA" -Type Mutant
PS> Add-NtSecurityDescriptorAce $sd -KnownSid World -Access GenericAll
PS> Add-NtSecurityDescriptorAce $sd -KnownSid AllApplicationPackages
-Access GenericAll
PS> Edit-NtSecurityDescriptor $sd -MapGeneric
❷ PS> Set-NtSecurityDescriptorIntegrityLevel $sd Medium

PS> Use-NtObject($token = Get-NtToken -Duplicate -IntegrityLevel Low) {
    Get-NtGrantedAccess $sd -Token $token -AsString
}
❸ ModifyState|ReadControl|Synchronize

PS> $sid = Get-NtSid -PackageName "mandatory_access_lowbox_check"
PS> Use-NtObject($token = Get-NtToken -LowBox -PackageSid $sid) {
    Get-NtGrantedAccess $sd -Token $token -AsString
}
❹ Full Access
```


*代码清单 7-23：针对lowbox令牌的强制访问检查行为*

我们首先构建一个安全描述符，为*Everyone*和*ALL APPLICATION PACKAGES*组授予GenericAll访问权限❶。我们还设置了显式的Medium完整性级别❷，尽管这不是必需的，因为Medium是未包含强制标签ACE的安全描述符的默认值。然后，我们使用Low完整性级别令牌执行访问检查，仅获得对安全描述符的读取访问权限❸。接下来，我们使用lowbox令牌再次尝试访问检查；尽管令牌的完整性级别仍为Low，但令牌获得完全访问权限❹。

我们实施的第二个更改是，如果DACL包含包SID，则无论安全描述符的完整性级别或DACL如何，我们都拒绝Low完整性级别令牌的访问。此机制阻止对分配了默认DACL的资源的访问，因为在创建lowbox令牌时，包SID会被添加到默认DACL中。代码清单 7-24测试了此行为。




```
PS> $sid = Get-NtSid -PackageName 'package_sid_low_il_test'
❶ PS> $token = Get-NtToken -LowBox -PackageSid $sid
❷ PS> $sd = New-NtSecurityDescriptor -Token $token -Type Mutant
PS> Format-NtSecurityDescriptor $sd -Summary -SecurityInformation Dacl, Label
<DACL>
❸ GRAPHITE\user: (Allowed)(None)(Full Access)
NT AUTHORITY\SYSTEM: (Allowed)(None)(Full Access)
NT AUTHORITY\LogonSessionId_0_109260: (Allowed)(None)(ModifyState|...)
❹ package_sid_low_il_test: (Allowed)(None)(Full Access)
<Mandatory Label>
❺ Mandatory Label\Low Mandatory Level: (MandatoryLabel)(None)(NoWriteUp)

PS> Get-NtGrantedAccess $sd -Token $token -AsString
❻ Full Access

PS> $token.Close()
PS> $low_token = Get-NtToken -Duplicate -IntegrityLevel Low
PS> Get-NtGrantedAccess $sd -Token $low_token -AsString
❼ None
```


*代码清单 7-24：验证包SID对Low完整性级别令牌的行为*

我们首先创建一个低权限令牌❶。该令牌不包含任何附加的能力SID，仅包含包SID。接下来，我们基于低权限令牌构建一个默认安全描述符❷。检查安全描述符中的条目时，我们看到当前用户SID❸和包SID❹已获得完全访问权限。由于低权限令牌具有低完整性级别，安全描述符继承规则要求将完整性级别添加到安全描述符中❺。

随后，我们基于低权限令牌请求安全描述符的授予访问权限，并收到完全访问权限❻。接下来，我们创建当前令牌的副本，但将其完整性级别设置为低。现在，我们获得的授予访问权限为无❼，尽管我们预期根据安全描述符中的完整性级别ACE会收到完全访问权限。在这种情况下，安全描述符中包SID的存在阻止了访问。

最后需要注意的一点是：由于沙箱访问检查是正交的，可以从受限令牌创建低权限令牌，导致低权限检查和受限SID检查同时发生。最终访问权限是所有检查中最严格的，从而形成更强大的沙箱原语。

### 企业访问检查

Windows 的企业部署通常会执行一些额外的访问检查。在独立安装的 Windows 上，您通常不需要这些检查，但如果存在这些检查，您仍应了解它们如何修改访问检查过程。

#### 对象类型访问检查

为简单起见，我在自主访问检查算法中特意省略了对象 ACE 的处理。要支持对象 ACE，您必须使用不同的访问检查 API：内核模式下的 `SeAccessCheckByType` 或系统调用 `NtAccessCheckByType`。这些 API 为访问检查过程引入了两个额外的参数：

Principal  用于替换 ACE 中 *SELF* SID 的 SID

ObjectTypes  对检查有效的 GUID 列表

Principal 很容易定义：当处理 DACL 时，如果遇到 ACE 的 SID 设置为 *SELF* SID（S-1-5-10），我们会用 Principal 参数中的值替换该 SID。（Microsoft 引入 *SELF* SID 用于 Active Directory；我们将在第 11 章中更详细地讨论其用途。）代码清单 7-25 展示了考虑此情况的 `Get-AceSid` 函数的调整版本。您还需要修改 `Get-PSGrantedAccess` 函数，通过将 Principal 参数添加到 `$Context` 值中来接收它。




```
function Get-AceSid {
    Param (
        $Ace,
        $Owner,
        $Principal
    )

    $sid = $Ace.Sid
    if (Compare-NtSid $sid -KnownSid OwnerRights) {
        $sid = $Owner
    }
    if ((Compare-NtSid $sid -KnownSid Self) -and ($null -NE $Principal)) {
        $sid = $Principal
    }
    return $sid
}
```


*代码清单 7-25：将主体 SID 添加到 Get-AceSid 函数中*

代码清单 7-26 测试了 Principal SID 的行为。




```
PS> $owner = Get-NtSid -KnownSid LocalSystem
❶ PS> $sd = New-NtSecurityDescriptor -Owner $owner -Group $owner -Type Mutant
PS> Add-NtSecurityDescriptorAce $sd -KnownSid Self -Access GenericAll 
-MapGeneric
❷ PS> Get-NtGrantedAccess $sd -AsString
None

PS> $principal = Get-NtSid
❸ PS> Get-NtGrantedAccess $sd -Principal $principal -AsString
Full Access
```


*代码清单 7-26：测试 Principal SID 替换*

我们首先创建一个安全描述符，将所有者和组设置为 *SYSTEM* 用户 SID，并添加一个允许 ACE，授予 *SELF* SID GenericAll 访问权限 ❶。根据访问检查规则，这不应授予用户对该资源的任何访问权限。我们可以通过调用 `Get-NtGrantedAccess` ❷ 来确认这一点。

接下来，我们获取有效令牌的用户 SID，并将其作为 Principal 参数传递给 `Get-NtGrantedAccess` ❸。然后，DACL 检查会将 *SELF* SID 替换为 Principal SID，该 SID 与当前用户匹配，因此授予完全访问权限。此检查仅替换 DACL 和 SACL 中的 SID；将 *SELF* 设置为所有者 SID 不会授予任何访问权限。

另一个参数 ObjectTypes 的实现要复杂得多。它提供了对访问检查过程有效的 GUID 列表。每个 GUID 表示要访问的对象类型；例如，您可能有一个与计算机对象关联的 GUID，以及另一个与用户对象关联的 GUID。

每个 GUID 还有一个关联的级别，将列表转换为层次树。每个节点维护自己的剩余访问权限，初始化为主要的 RemainingAccess 值。Active Directory 使用此层次结构来实现属性和属性集的概念，如图 7-4 所示。



![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure7-4.webp)

图 7-4：Active Directory 风格的属性

图 7-4 中的每个节点显示了我们为其指定的名称、ObjectType GUID 的一部分以及当前的 RemainingAccess 值（在本例中为 GenericAll）。级别 0 对应于顶级对象，列表中只能有一个。级别 1 是属性集，此处编号为 1 和 2。在每个属性集下方，级别 2 是各个属性。

在层次结构中设置对象类型使我们能够配置安全描述符，通过设置属性集的访问权限，使用单个 ACE 授予对多个属性的访问权限。如果我们授予属性集某些访问权限，也会将该访问权限授予该集中的所有属性。相反，如果我们拒绝单个属性的访问权限，拒绝状态将沿树向上传播，并拒绝整个属性集和对象的访问权限。

让我们考虑对象类型访问的基本实现。代码清单 7-27 中的代码依赖于添加到访问上下文中的 ObjectTypes 属性。我们可以使用 `New-ObjectTypeTree` 和 `Add-ObjectTypeTree` 命令生成此参数的值，我们将在本章稍后的“对象类型层次树”部分介绍其用法。

代码清单 7-27 展示了 AllowedObject ACE 类型的访问检查实现。将其添加到 代码清单 7-17 中的 ACE 枚举代码中。




```
"AllowedObject" {
  ❶ if (!(Test-NtTokenGroup -Token $token $sid)) {
        break
    }

  ❷ if ($null -eq $Context.ObjectTypes -or $null -eq $ace.ObjectType) {
        break
    }

  ❸ $object_type = Select-ObjectTypeTree $Context.ObjectTypes
    if ($null -eq $object_type) {
       break
    }

  ❹ Revoke-ObjectTypeTreeAccess $object_type $ace.Mask
    $access = Revoke-NtAccessMask $access $ace.Mask
}
```


*代码清单 7-27：AllowedObject ACE 访问检查算法的实现*

我们首先进行 SID 检查 ❶。如果 SID 不匹配，则不处理该 ACE。接下来，我们检查上下文中是否存在 ObjectTypes 属性，以及 ACE 是否定义了 ObjectType ❷（ACE 上的 ObjectType 是可选的）。同样，如果这些检查失败，我们将忽略该 ACE。最后，我们检查 ObjectTypes 参数中是否存在对应 ObjectType GUID 的条目 ❸。

如果所有检查均通过，我们将该 ACE 纳入访问检查的考量范围。首先，我们从对象树中的条目撤销访问权限 ❹。这不仅会移除我们找到的 ObjectType 条目的访问权限，还会移除该条目所有子节点的访问权限。同时，我们也会撤销为此函数维护的访问权限。

让我们将此行为应用于 图 7-4 中所示的树。如果 AllowedObject ACE 授予属性集 1 GenericAll 访问权限，新的树将如 图 7-5 所示。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure7-5.webp)

图 7-5：向属性集 1 授予访问权限后的对象类型树

由于属性集 1 的 RemainingAccess 中已移除 GenericAll 访问权限，因此属性 X 和 Y 的 RemainingAccess 也被移除。这些节点现在具有空的 RemainingAccess。请注意，对于 Allowed ACE，只有主要的 RemainingAccess 才重要，因为树的目的是正确处理 Denied ACE。这意味着并非每个对象类型都必须具有 RemainingAccess 为 0，访问检查才能成功。

现在让我们处理 DeniedObject ACE。将 代码清单 7-28 中的代码添加到 代码清单 7-17 中现有的 ACE 枚举代码中。




```
"DeniedObject" {
  ❶ if (!(Test-NtTokenGroup -Token $token $sid -DenyOnly)) {
        break
    }

  ❷ if ($null -ne $Context.ObjectTypes) {
        if ($null -eq $ace.ObjectType) {
            break;
        }

        $object_type = Select-ObjectTypeTree $Context.ObjectTypes
$ace.ObjectType
        if ($null -eq $object_type) {
            break
        }

      ❸ if (Test-NtAccessMask $object_type.RemainingAccess $ace.Mask) {
            $continue_check = $false
            break
        }
    }
  ❹ if (Test-NtAccessMask $access $ace.Mask) {
        $continue_check = $false
    }
}
```


*代码清单 7-28：DeniedObject ACE 访问检查算法的实现*

像往常一样，我们首先检查所有类型为 DeniedObject 的 ACE ❶。如果检查通过，我们接下来检查 ObjectTypes 上下文属性 ❷。在处理 AllowedObject ACE 时，如果缺少 ObjectType 属性，我们会停止检查。但是，我们处理 DeniedObject ACE 的方式不同。如果没有 ObjectTypes 属性，检查将继续进行，就像处理普通的 Denied ACE 一样，通过考虑主要的 RemainingAccess ❹。

如果 ACE 的访问掩码包含 RemainingAccess 中的位，则我们拒绝访问 ❸。如果此检查通过，我们将该值针对主要的 RemainingAccess 进行检查。这展示了维护树的目的：如果 Denied ACE 匹配了 图 7-5 中的属性 X，则拒绝掩码将不会产生任何效果。但是，如果 Denied ACE 匹配了属性 Z，那么该对象类型，以及与之关联的属性集 2 和根对象类型，也将失败。图 7-6 演示了这一点：您可以看到这些节点现在都被拒绝，即使属性集 1 分支仍然被允许。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure7-6.webp)

图 7-6：拒绝属性 Z 的访问权限后的对象类型树

NtAccessCheckByType 系统调用为整个对象类型列表返回单个状态和授予的访问权限，反映了对象类型树根节点处指定的访问权限。因此，在 图 7-6 的情况下，整个访问检查将失败。

要确定哪些特定对象类型未通过访问检查，您可以使用 NtAccessCheckByTypeResultList 系统调用，它为对象类型列表中的每个条目返回状态和授予的访问权限。代码清单 7-29 展示了如何通过向 Get-NtGrantedAccess 指定 ResultList 参数来使用此系统调用。




```
❶ PS> $tree = New-ObjectTypeTree (New-Guid) -Name "Object" 
PS> $set_1 = Add-ObjectTypeTree $tree (New-Guid) -Name "Property Set 1" 
-PassThru
PS> $set_2 = Add-ObjectTypeTree $tree (New-Guid) -Name "Property Set 2" 
-PassThru
PS> Add-ObjectTypeTree $set_1 (New-Guid) -Name "Property X"
PS> Add-ObjectTypeTree $set_1 (New-Guid) -Name "Property Y"
PS> $prop_z = New-Guid
PS> Add-ObjectTypeTree $set_2 $prop_z -Name "Property Z"

PS> $owner = Get-NtSid -KnownSid LocalSystem
PS> $sd = New-NtSecurityDescriptor -Owner $owner -Group $owner -Type Mutant
❷ PS> Add-NtSecurityDescriptorAce $sd -KnownSid World -Access WriteOwner
-MapGeneric -Type DeniedObject -ObjectType $prop_z
PS> Add-NtSecurityDescriptorAce $sd -KnownSid World
-Access ReadControl, WriteOwner -MapGeneric
PS> Edit-NtSecurityDescriptor $sd -CanonicalizeDacl
❸ PS> Get-NtGrantedAccess $sd -PassResult -ObjectType $tree
-Access ReadControl, WriteOwner | Format-Table Status, SpecificGrantedAccess, 
Name
              Status   SpecificGrantedAccess    Name
              ------   ---------------------    ----
❹ STATUS_ACCESS_DENIED                    None    Object

❺ PS> Get-NtGrantedAccess $sd -PassResult -ResultList -ObjectType $tree
-Access ReadControl, WriteOwner | Format-Table Status, SpecificGrantedAccess, 
Name
            ❻ Status   SpecificGrantedAccess    Name
              ------   ---------------------    ----
STATUS_ACCESS_DENIED                ReadControl Object
      STATUS_SUCCESS   ReadControl, WriteOwner  Property Set 1
      STATUS_SUCCESS   ReadControl, WriteOwner  Property X
      STATUS_SUCCESS   ReadControl, WriteOwner  Property Y
STATUS_ACCESS_DENIED               ReadControl  Property Set 2
STATUS_ACCESS_DENIED               ReadControl  Property Z
```


*代码清单 7-29：展示普通结果与列表结果之间差异的示例*

我们首先构建对象类型树，以匹配图7-4中的树结构❶。除了属性Z的GUID值（在DeniedObject ACE中需要用到）外，我们不关心其他具体的GUID值，因此我们生成随机的GUID。接下来，我们构建安全描述符，创建一个拒绝属性Z的ReadControl访问权限的ACE❷。我们还包括一个非对象ACE，用于授予ReadControl和WriteOwner访问权限。

我们首先在带有对象类型树但不带ResultList参数的情况下运行访问检查，请求ReadControl和WriteOwner访问权限❸。我们使用Denied ACE，因为它匹配对象类型树中的ObjectType GUID。正如我们所预期的那样，这导致访问检查过程返回STATUS_ACCESS_DENIED，授予的访问权限为None❹。

当我们再次执行访问检查，这次带有ResultList参数时，我们会收到一个访问检查结果列表❺。顶层对象条目仍然表明拒绝访问，但属性集1及其子项获得了访问权限❻。这个结果对应于图7-6中显示的树。还要注意，被拒绝访问的条目并未显示空的授予访问权限；相反，它们表明如果请求成功，ReadControl访问权限本应获得。这是访问检查在底层实现方式的一个产物，几乎肯定不应被使用。

#### 中央访问策略

*中央访问策略*是Windows 8和Windows Server 2012中新增的一项功能，用于企业网络，是Windows功能*动态访问控制*的核心安全机制。它依赖于令牌中的设备和用户声明属性。

在第4章中讨论条件表达式格式时，我们简要提到了用户和设备声明。*用户声明*是添加到特定用户令牌中的安全属性。例如，你可能有一个表示用户受雇国家的声明。你可以将声明的值与Active Directory中存储的值同步，这样如果用户移居到另一个国家，他们的用户声明将在下次身份验证时更新。

*设备声明*属于用于访问资源的计算机。例如，设备声明可能指示计算机是否位于安全房间中，或是否运行特定版本的Windows。图7-7展示了中央访问策略的常见用途：限制企业网络中服务器上文件的访问。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure7-7.webp)

图7-7：文件服务器上的中央访问策略

此中央访问策略包含一个或多个安全描述符，访问检查除了考虑文件的安全描述符外，还会考虑这些描述符。最终授予的访问权限是访问检查结果中最具限制性的结果。虽然不是严格必需的，但额外的安全描述符可以依赖AllowedCallback ACE中的用户和设备声明来确定授予的访问权限。企业的Kerberos身份验证必须配置为支持这些声明，以便通过网络发送它们。我们将在第14章中回到Kerberos身份验证的讨论。

你可能想知道使用中央访问策略与简单配置文件安全以使用设备和用户声明有何不同。主要区别在于，中央访问策略是通过企业域组策略中的策略进行集中管理的。这意味着管理员可以在一个地方更改中央访问策略，以在整个企业中更新它。

第二个区别是，中央访问策略更像是一种强制访问控制机制。例如，用户通常可能能够修改文件的安全描述符；然而，中央访问策略可能会限制他们的访问，或者如果用户移居到新国家或使用了规则中未涵盖的不同计算机，则可能完全阻止他们的访问。

我们不会讨论如何配置中央访问策略，因为该主题更适合关于Windows企业管理的书籍。相反，我们将探讨内核的访问检查过程如何强制执行它。当计算机的组策略更新时，Windows注册表会存储中央访问策略，你可以在以下位置找到该键：*HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa\CentralizedAccessPolicies*。

可以配置多个策略，每个策略包含以下信息：

- 策略的名称和描述
- 唯一标识策略的SID
- 一个或多个策略规则

相应地，每个策略规则包含以下信息：

- 规则的名称和描述
- 确定何时执行规则的条件表达式
- 在中央访问策略访问检查中使用的安全描述符
- 用于测试新策略规则的可选暂存安全描述符

您可以使用 `Get-CentralAccessPolicy` PowerShell 命令来显示策略和规则的列表。对于大多数 Windows 系统，该命令不会返回任何信息。要查看如 代码清单 7-30 所示的结果，您需要加入一个配置了中央访问策略的域。

```
PS> Get-CentralAccessPolicy
Name               CapId                            Description
----               -----                            -----------
Secure Room Policy S-1-17-3260955821-1180564752-... Only for Secure Computers
Main Policy        S-1-17-76010919-1187351633-...

PS> $rules = Get-CentralAccessPolicy | Select-Object -ExpandProperty Rules
PS> $rules | Format-Table
Name        Description AppliesTo
----        ----------- ---------
Secure Rule Secure!     @RESOURCE.EnableSecure == 1
Main Rule   NotSecure!

PS> $sd = $rules[0].SecurityDescriptor
PS> Format-NtSecurityDescriptor $sd -Type File -SecurityInformation Dacl
<DACL> (Auto Inherit Requested)
 - Type    : AllowedCallback
 - Name    : Everyone
 - SID     : S-1-1-0
 - Mask    : 0x001F01FF
 - Access  : Full Access
 - Flags   : None
- Condition: @USER.ad://ext/clearance == "TS/ST3" &&
              @DEVICE.ad://ext/location = "Secure"
```

*代码清单 7-30：显示中央访问策略*

在这里，当我们运行 `Get-CentralAccessPolicy` 时，会看到两个策略：Secure Room Policy 和 Main Policy。每个策略都有一个 CapId SID 和一个 Rules 属性，我们可以展开该属性以查看各个规则。输出表包含以下字段：Name、Description 和 AppliesTo，其中 AppliesTo 是用于选择是否应执行该规则的条件表达式。如果 AppliesTo 字段为空，则该规则将始终执行。Secure Rule 的 AppliesTo 字段选择了一个资源属性，我们将在 代码清单 7-32 中回到这一点。

让我们显示此规则的安全描述符。DACL 包含一个 AllowedCallback ACE，如果条件匹配，则授予 *Everyone* 组完全访问权限。在这种情况下，用户声明 clearance 必须设置为 TS/ST3，设备声明 location 必须设置为 Secure。

我们将逐步实现中央访问策略访问检查的基本实现，以更好地理解该策略的用途。将 代码清单 7-31 中的代码添加到 代码清单 7-2 中 Get-PSGrantedAccess 函数的末尾。

```
❶ if (!$success) {
    return Get-AccessResult STATUS_ACCESS_DENIED
}

❷ $capid = $SecurityDescriptor.ScopedPolicyId
if ($null -eq $capid) {
    return Get-AccessResult STATUS_SUCCESS $Context.Privileges $DesiredAccess
}

❸ $policy = Get-CentralAccessPolicy -CapId $capid.Sid
if ($null -eq $policy){
    return Get-AccessResult STATUS_SUCCESS $Context.Privileges $DesiredAccess
}

❹ $effective_access = $DesiredAccess
foreach($rule in $policy.Rules) {
    if ($rule.AppliesTo -ne "") {
        $resource_attrs = $null
        if ($sd.ResourceAttributes.Count -gt 0) {
            $resource_attrs = $sd.ResourceAttributes.ResourceAttribute
        }
      ❺ if (!(Test-NtAceCondition -Token $Token -Condition $rule.AppliesTo
-ResourceAttribute $resource_attrs)) {
            continue
        }
    }
    $new_sd = Copy-NtSecurityDescriptor $SecurityDescriptor
  ❻ Set-NtSecurityDescriptorDacl $rule.Sd.Dacl

    $Context.SecurityDescriptor = $new_sd
    $Context.RemainingAccess = $DesiredAccess

  ❼ Get-DiscretionaryAccess $Context
  ❽ $effective_access = $effective_access -band (-bnot $Context.RemainingAccess)
}

❾ if (Test-NtAccessMask $effective_access -Empty) {
    return Get-AccessResult STATUS_ACCESS_DENIED
}
❹ return Get-AccessResult STATUS_SUCCESS $Context.Privileges $effective_access
```

*代码清单 7-31：中央访问策略检查*

代码清单 7-31 在自由访问检查之后立即开始。如果此检查失败，$success 变量将为 False，我们应该返回 STATUS_ACCESS_DENIED ❶。要开始执行中央访问策略，我们需要从 SACL 中查询 ScopedPolicyId ACE ❷。如果没有 ScopedPolicyId ACE，我们可以返回成功。如果不存在 CapId 与 ACE 的 SID 匹配的中央访问策略，我们也返回成功 ❸。

在中央访问策略检查中，我们首先将有效访问设置为原始的 DesiredAccess ❹。我们将使用有效访问来确定在处理所有策略规则后可以授予多少 DesiredAccess。接下来，我们检查每个规则的 AppliesTo 条件表达式。如果没有值，则该规则适用于所有资源和令牌。如果有条件表达式，我们必须使用 Test-NtAceCondition 检查它，并传递安全描述符中的任何资源属性 ❺。如果测试未通过，检查应跳到下一个规则。

我们使用原始安全描述符中的所有者、组和 SACL 构建新的安全描述符，但使用规则安全描述符中的 DACL ❻。如果规则适用，我们再次对 DesiredAccess 进行自由访问检查 ❼。在此检查之后，我们从 effective_access 变量中移除未授予的任何位 ❽。

一旦我们检查了所有适用的规则，我们测试有效访问是否为空。如果为空，则中央访问策略未授予令牌任何访问权限，因此我们返回 STATUS_ACCESS_DENIED ❾。否则，我们返回成功，但仅返回剩余的有效访问，该访问授予的权限少于第一次访问检查的结果 ❿。

虽然大多数中央访问策略设计用于检查文件，但我们可以修改任何资源类型以执行策略。要为其他资源启用它，我们需要做两件事：设置一个带有要启用策略的 SID 的作用域策略 ID ACE，并添加任何资源属性 ACE 以匹配 AppliesTo 条件（如果有）。我们在 代码清单 7-32 中执行这些任务。

```
PS> $sd = New-NtSecurityDescriptor
❶ PS> $attr = New-NtSecurityAttribute "EnableSecure" -LongValue 1
❷ PS> Add-NtSecurityDescriptorAce $sd -Type ResourceAttribute -Sid "WD"
-SecurityAttribute $attr -Flags ObjectInherit, ContainerInherit
PS> $capid = "S-1-17-3260955821-1180564752-1365479606-2616254494"
❸ PS> Add-NtSecurityDescriptorAce $sd -Type ScopedPolicyId -Sid $capid
-Flags ObjectInherit, ContainerInherit
PS> Format-NtSecurityDescriptor $sd -SecurityInformation Attribute, Scope
Type: Generic
Control: SaclPresent
<Resource Attributes>
 - Type  : ResourceAttribute
 - Name  : Everyone
 - SID   : S-1-1-0
 - Mask  : 0x00000000
 - Access: Full Access
 - Flags : ObjectInherit, ContainerInherit
 - Attribute: "EnableSecure",TI,0x0,1

<Scoped Policy ID>
 - Type  : ScopedPolicyId
 - Name  : S-1-17-3260955821-1180564752-1365479606-2616254494
 - SID   : S-1-17-3260955821-1180564752-1365479606-2616254494
 - Mask  : 0x00000000
 - Access: Full Access
 - Flags : ObjectInherit, ContainerInherit

❹ PS> Enable-NtTokenPrivilege  SeSecurityPrivilege
❺ PS> Set-Win32SecurityDescriptor $sd MACHINE\SOFTWARE\PROTECTED
-Type RegistryKey -SecurityInformation Scope, Attribute
```

*代码清单 7-32：为注册表项启用 Secure Room Policy*

首先，我们需要添加一个资源属性ACE，以满足安全规则的AppliesTo条件。我们创建一个名为EnableSecure的安全属性对象，其值为单个Int64类型的1 ❶。我们将此安全属性添加到安全描述符SACL中类型为ResourceAttribute的ACE中 ❷。然后，我们需要设置中央访问策略的SID，这可以从Get-CentralAccessPolicy命令的输出中获取，并将其放入ScopedPolicyId ACE中 ❸。我们可以格式化安全描述符以检查ACE是否正确。

接下来，我们将这两个ACE设置到资源上。在本例中，我们选择的资源是一个注册表键 ❺。请注意，您必须事先创建此注册表键，操作才能成功。SecurityInformation参数必须设置为Scope和Attribute。正如我们在第5章中观察到的，要设置ScopedPolicyId ACE，我们需要AccessSystemSecurity访问权限，这意味着我们需要先启用SeSecurityPrivilege特权 ❹。

如果您访问该注册表键，应该会发现策略已被强制执行。请注意，由于中央访问策略是为文件系统配置的，安全描述符中的访问掩码可能无法与其他资源（如注册表键）正确配合使用。如果您确实希望支持此行为，可以手动在Active Directory中配置属性。

最后要提到的一点是，中央访问策略规则支持指定暂存安全描述符以及正常的安全描述符。我们可以使用此暂存安全描述符在广泛部署之前测试即将进行的安全更改。暂存安全描述符的检查方式与正常安全描述符相同，但检查结果仅用于与实际授予的访问权限进行比较，如果两个访问掩码不同，则会生成审计日志。

### 实际示例

最后，我们通过一些实际示例来运用本章学到的命令。

#### 使用 Get-PSGrantedAccess 命令

在本章中，我们构建了自己的访问检查过程实现：`Get-PSGrantedAccess` 命令。在本节中，我们将探讨该命令的使用。你可以从本书随附的在线附加材料中的 *chapter_7_access_check_impl.psm1* 文件中获取包含该命令的模块。

由于 `Get-PSGrantedAccess` 是访问检查的简单实现，它缺少某些功能，例如支持计算最大访问权限。然而，它仍然可以帮助你理解访问检查过程。例如，你可以在 PowerShell 集成脚本环境（ISE）或 Visual Studio Code 中使用 PowerShell 调试器逐步执行访问检查，并根据不同输入观察其运行方式。

以非管理员拆分令牌用户身份运行 代码清单 7-33 中的命令。




```
❶ PS> Import-Module ".\chapter_7_access_check_impl.psm1"
❷ PS> $sd = New-NtSecurityDescriptor "O:SYG:SYD:(A;;GR;;;WD)"
-Type File -MapGeneric
PS> $type = Get-NtType File
PS> $desired_access = Get-NtAccessMask -FileAccess GenericRead 
-MapGenericRights
❸ PS> Get-PSGrantedAccess -SecurityDescriptor $sd
-GenericMapping $type.GenericMapping -DesiredAccess $desired_access
Status               Privileges                 GrantedAccess
------               ----------                 -------------
STATUS_SUCCESS       {}                         1179785

❹ PS> $desired_access = Get-NtAccessMask -FileAccess WriteOwner
PS> Get-PSGrantedAccess -SecurityDescriptor $sd
-GenericMapping $type.GenericMapping -DesiredAccess $desired_access
Status               Privileges                 GrantedAccess
------               ----------                 -------------
❺ STATUS_ACCESS_DENIED {}                         0

❻ PS> $token = Get-NtToken -Linked
❼ PS> Enable-NtTokenPrivilege -Token $token SeTakeOwnershipPrivilege
PS> Get-PSGrantedAccess -Token $token -SecurityDescriptor $sd
-GenericMapping $type.GenericMapping -DesiredAccess $desired_access
Status               Privileges                 GrantedAccess
------               ----------                 -------------
❽ STATUS_SUCCESS       {SeTakeOwnershipPrivilege} 524288
```


*代码清单 7-33：使用 Get-PSGrantedAccess 命令*

首先，我们导入包含 `Get-PSGrantedAccess` 命令的模块 ❶。导入操作假定模块文件保存在当前目录中；如果不是，请相应修改路径。然后，我们构建一个限制性安全描述符，仅授予 *Everyone* 组读取权限，不授予其他任何人 ❷。

接下来，我们调用 `Get-PSGrantedAccess`，请求 `GenericRead` 访问权限以及文件对象类型的通用映射 ❸。我们未指定 `Token` 参数，这意味着检查将使用调用者的有效令牌。命令返回 `STATUS_SUCCESS`，且授予的访问权限与我们最初传递的所需访问权限一致。

然后，我们将所需访问权限更改为仅 `WriteOwner` 访问权限 ❹。根据限制性安全描述符，只有安全描述符的所有者（设置为 *SYSTEM* 用户）应获得此访问权限。当我们重新运行访问检查时，得到 `STATUS_ACCESS_DENIED` 且未授予任何访问权限 ❺。

为了展示如何绕过这些限制，我们查询调用者的链接令牌 ❻。如 第 4 章 所述，UAC 使用链接令牌来暴露完整的管理员令牌。除非你以拆分令牌管理员身份运行脚本，否则此命令将无法工作。然而，我们可以在链接令牌上启用 `SeTakeOwnershipPrivilege` 特权 ❼，这应能绕过 `WriteOwner` 的所有者检查。访问检查现在应返回 `STATUS_SUCCESS` 并授予所需访问权限 ❽。`Privileges` 列显示 `SeTakeOwnershipPrivilege` 被用于授予访问权限。

如前所述，建议在调试器中运行此脚本并单步进入 `Get-PSGrantedAccess`，以跟随访问检查过程，从而更好地理解它。我还建议尝试在安全描述符中使用不同的值组合。

#### 计算资源的授予访问权限

如果你确实需要知道资源的授予访问权限，最好使用 `Get-NtGrantedAccess` 命令，而不是我们开发的 PowerShell 实现。让我们看看如何使用此命令获取资源列表的授予访问权限。在 代码清单 7-34 中，我们将采用 第 6 章 中使用的脚本来查找对象的所有者，并计算完整的授予访问权限。




```
PS> function Get-NameAndGrantedAccess {
    [CmdletBinding()]
    param(
        [parameter(Mandatory, ValueFromPipeline)]
        $Entry,
        [parameter(Mandatory)]
        $Root
    )

    PROCESS {
        $sd = Get-NtSecurityDescriptor -Path $Entry.Name -Root $Root
-TypeName $Entry.NtTypeName -ErrorAction SilentlyContinue
        if ($null -ne $sd) {
          ❶ $granted_access = Get-NtGrantedAccess -SecurityDescriptor $sd
            if (!(Test-NtAccessMask $granted_access -Empty)) {
                $props = @{
                    Name = $Entry.Name;
                    NtTypeName = $Entry.NtTypeName
                    GrantedAccess = $granted_access
                }

                New-Object -TypeName PSObject -Prop $props
            }
        }
    }
}

PS> Use-NtObject($dir = Get-NtDirectory \BaseNamedObjects) {
    Get-NtDirectoryEntry $dir | Get-NameAndGrantedAccess -Root $dir
}
Name                               NtTypeName  GrantedAccess
----                               ----------  -------------
SM0:8924:120:WilError_03_p0        Semaphore   QueryState, ModifyState, ...
CLR_PerfMon_DoneEnumEvent          Event       QueryState, ModifyState, ...
msys-2.0S5-1888ae32e00d56aa        Directory   Query, Traverse, ...
SyncRootManagerRegistryUpdateEvent Event       QueryState, ModifyState, ...
--snip--
```


*代码清单 7-34：枚举对象并获取其授予访问权限*

在此修改版的脚本中（基于 代码清单 6-37 创建），我们不再仅仅检查所有者 SID，而是调用带有安全描述符的 `Get-NtGrantedAccess` ❶。这应能检索调用者的授予访问权限。另一种策略是检查任何模拟令牌在标识级别（Identification level）的授予访问权限，并在句柄上具有 `Query` 访问权限，然后将其作为 `Token` 参数传递。在下一章中，我们将探讨一种更简单的方法来进行大规模访问检查，而无需编写自己的脚本。

### 总结

在本章中，我们详细阐述了Windows中访问检查过程的实现，包括操作系统的强制访问检查、令牌所有者和特权检查，以及自主访问检查。我们还构建了自己的访问检查过程实现，以便您更好地理解它。

接下来，我们探讨了两种类型的沙盒令牌（受限令牌和lowbox令牌）如何影响访问检查过程，以限制资源访问。最后，我们讨论了对象类型检查和中央访问策略，这些是Windows企业安全的重要特性。

## 8. 其他访问检查使用场景

访问检查决定了调用者在打开内核资源时应具有何种访问权限。然而，我们有时会出于其他原因执行这些检查，因为它们可以作为额外的安全机制。本章将详细介绍一些将访问检查用作辅助安全机制的示例。

我们首先探讨遍历检查，它用于确定调用者是否有权访问资源层次结构。接下来，我们将讨论在句柄复制时如何使用访问检查。我们还会考虑访问检查如何限制沙盒应用程序对内核信息（如进程列表）的访问。最后，我将介绍一些额外的PowerShell命令，用于自动化资源的访问检查。

### 遍历检查

在访问层级资源集（如对象目录树）时，用户必须遍历层级结构直至到达目标资源。对于层级中的每个目录或容器，系统都会执行一次访问检查，以确定调用者是否可以继续进入下一个容器。此检查称为*遍历检查*，每当代码在I/O管理器或对象管理器中查找路径时都会执行。例如，图8-1展示了使用路径*ABC\QRS\XYZ\OBJ*访问OMNS对象所需的遍历检查。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure8-1.webp)

图8-1：访问OBJ所需的遍历检查

如您所见，在访问*OBJ*之前必须执行三次访问检查。每次访问检查都会从容器中提取安全描述符，然后检查特定类型的访问权限以确定是否允许遍历。OMNS和文件目录都可以授予或拒绝遍历访问。例如，如果*QRS*拒绝调用者的遍历访问，遍历检查将失败，如图8-2所示。

![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure8-2.webp)

图8-2：遍历检查在QRS处被阻止

即使调用者能通过*XYZ*和*OBJ*的访问检查，由于*QRS*现在通过遍历检查拒绝访问，他们也无法再通过*ABC\QRS\XYZ\OBJ*路径访问*OBJ*。

如果任何父容器拒绝遍历访问，遍历检查将阻止用户访问其资源。这是出乎意料的行为——为什么用户不能访问自己的资源？这也带来了性能问题。如果用户必须访问每个父容器才能访问其文件，那么内核必须花费时间和精力对每个容器执行访问检查，而安全方面真正重要的只是用户是否有权访问他们想要打开的资源。

#### SeChangeNotifyPrivilege特权

为了使遍历检查行为更接近您的预期，并减少性能影响，SRM定义了SeChangeNotifyPrivilege特权，几乎所有令牌对象默认都启用了此特权。当此特权启用时，系统会完全跳过遍历检查，允许用户访问原本会被不可访问的父容器阻止的资源。在代码清单 8-1中，我们使用OMNS目录对象验证该特权的行为。




```
PS> $path = "\BaseNamedObjects\ABC\QRS\XYZ\OBJ"
❶ PS> $os = New-NtMutant $path -CreateDirectories
❷ PS> Enable-NtTokenPrivilege SeChangeNotifyPrivilege
PS> Test-NtObject $path
True

PS> $sd = New-NtSecurityDescriptor -EmptyDacl
❸ PS> Set-NtSecurityDescriptor "\BaseNamedObjects\ABC\QRS" $sd Dacl
PS> Test-NtObject $path
❹ True

❺ PS> Disable-NtTokenPrivilege SeChangeNotifyPrivilege
PS> Test-NtObject $path
False

❻ PS> Test-NtObject "OBJ" -Root $os[1]
True
```


*代码清单 8-1：测试SeChangeNotifyPrivilege以绕过遍历检查*

我们首先创建一个Mutant对象及其所有父目录，通过使用CreateDirectories属性自动创建目录❶。我们确保特权已启用❷，然后使用Test-NtObject命令检查Mutant对象是否可以被打开。在输出中，我们可以看到我们能够打开Mutant对象。

然后，我们在*QRS*目录上设置一个具有空DACL的安全描述符❸。这应该阻止对该目录对象的所有访问，包括遍历访问。但当我们再次检查访问权限时，我们看到我们仍然可以访问Mutant对象，因为我们启用了SeChangeNotifyPrivilege特权❹。

现在我们禁用该特权并再次尝试打开Mutant对象❺。这次，目录遍历失败。没有SeChangeNotifyPrivilege特权或对*QRS*目录的访问权限，我们无法再打开Mutant对象。然而，我们的最终检查表明，如果我们对*QRS*之后的父目录（如*XYZ*）具有访问权限，我们可以通过使用该目录作为Root参数进行相对打开来访问Mutant对象❻。

#### 有限检查

内核包含对遍历检查的额外性能改进。如果SeChangeNotifyPrivilege特权被禁用，内核将调用SeFastTraverseCheck函数，该函数执行更有限的检查而不是完整的访问检查。为完整起见，我在PowerShell中重新实现了SeFastTraverseCheck函数，以便更详细地探索其行为。代码清单 8-2显示了实现。




```
function Get-FastTraverseCheck {
    Param(
      ❶ $TokenFlags,
        $SecurityDescriptor,
        $AccessMask
    )

  ❷ if ($SecurityDescriptor.DaclNull) {
        return $true
    }
  ❸ if (($TokenFlags -band "IsFiltered, IsRestricted") -ne 0) {
        return $false
    }
    $sid = Get-Ntsid -KnownSid World
    foreach($ace in $SecurityDescriptor.Dacl) {
      ❹ if ($ace.IsInheritedOnly -or !$ace.IsAccessGranted($AccessMask)) {
            continue
        }
      ❺ if ($ace.IsDeniedAce) {
            return $false
        }
      ❻ if ($ace.IsAllowedAce -and $ace.Sid -eq $sid) {
            return $true
        }
    }
  ❼ return $false
}
```


*代码清单 8-2：SeFastTraverseCheck的PowerShell实现*

首先，我们定义函数所需的三个参数：令牌的标志、目录对象的安全描述符，以及要检查的遍历访问权限❶。我们指定访问权限是因为对象管理器和I/O管理器对目录和文件对象使用此函数，而遍历访问权限的值在这两种对象类型之间有所不同；将访问权限作为参数指定，使得检查函数能够处理这两种情况。

接下来，我们检查安全描述符的DACL是否为NULL，如果是，则授予访问权限❷。随后，我们检查两个令牌标志❸。如果标志指示令牌已被过滤或受限，则快速检查失败。内核从调用者的令牌对象中复制这些标志。我们可以通过用户模式使用令牌对象上的`Flags`属性获取这些标志，如代码清单 8-3所示。

```
PS> $token = Get-NtToken -Pseudo -Primary
PS> $token.Flags
VirtualizeAllowed, IsFiltered, NotLow

PS> $token.ElevationType
Limited
```

*代码清单 8-3：查询令牌标志*

请注意，标志包括`IsFiltered`。如果你不是在受限令牌沙箱中运行，为什么这个标志会被设置？查询令牌提升类型显示其为`Limited`，这意味着它是UAC管理员默认令牌。要将完整管理员令牌转换为默认令牌，LSASS使用`NtFilterToken`系统，这将设置`IsFiltered`标志但不会设置`IsRestricted`，因为它只是移除组，而不是添加受限SID。这意味着，虽然UAC管理员以默认用户身份运行代码时永远无法通过快速遍历检查，但普通用户可以。这种行为没有安全影响，但确实意味着如果`SeChangeNotifyPrivilege`被禁用，资源查找性能将受到影响。

代码清单 8-3中的最终检查包括枚举DACL的ACE。如果ACE是仅继承的或不包含所需的遍历访问掩码，则跳过它❹。如果是拒绝ACE，则快速遍历检查失败❺，并且完全不检查ACE的SID。最后，如果是允许ACE且SID等于*Everyone*组的SID，则快速检查成功❻。如果没有更多ACE，则检查失败❼。

请注意，此快速检查不考虑调用者的令牌是否启用了*Everyone*组。这是因为通常移除*Everyone*组的唯一方式是过滤令牌。最大的例外是匿名令牌，它没有任何组，但也没有以任何方式被过滤。

现在，让我们转向访问检查的另一个用途：在分配重复句柄时考虑授予的访问权限。

### 句柄复制访问检查

系统在创建或打开返回句柄的内核资源时，始终会执行访问检查。但当该句柄被复制时情况又如何呢？在最简单的情况下，如果新句柄与原始句柄具有相同的授予访问掩码，系统将不会执行任何检查。同样，如果降低授予访问掩码的部分权限，也不会触发额外的访问检查。然而，如果你想为复制的句柄增加额外的访问权限，内核将从对象中查询安全描述符，并执行新的访问检查以决定是否允许该访问。

当你复制句柄时，必须同时指定源进程和目标进程的句柄，并且访问检查是在目标进程的上下文中进行的。这意味着访问检查考虑的是目标进程的主令牌，而非源进程的令牌。如果特权进程尝试将句柄复制到权限较低的进程并附带额外访问权限，这可能会成为问题。此类操作将因拒绝访问而失败。

代码清单 8-4 演示了这种句柄复制访问检查行为。




```
PS> $sd = New-NtSecurityDescriptor -EmptyDacl
❶ PS> $m = New-NtMutant -Access ModifyState, ReadControl -SecurityDescriptor $sd
❷ PS> Use-NtObject($m2 = Copy-NtObject -Object $m) {
    $m2.GrantedAccess
}
ModifyState, ReadControl

PS> $mask = Get-NtAccessMask -MutantAccess ModifyState
❸ PS> Use-NtObject($m2 = Copy-NtObject -Object $m -DesiredAccessMask $mask) {
    $m2.GrantedAccess
}
ModifyState

❹ PS> Use-NtObject($m2 = Copy-NtObject -Object $m -DesiredAccess GenericAll) {
    $m2.GrantedAccess
}
Copy-NtObject : (0xC0000022) - {Access Denied}
A process has requested access to an object, ...
```


*代码清单 8-4：测试句柄复制访问检查行为*

我们首先创建一个具有空DACL的新Mutant对象，并仅请求句柄上的`ModifyState`和`ReadControl`访问权限❶。这将阻止所有用户访问该对象，但所有者除外，由于上一章所述的所有者检查，所有者可以获得`ReadControl`和`WriteDac`访问权限。我们通过请求相同的访问权限来测试复制，新句柄返回了该权限❷。

接下来，我们仅请求`ModifyState`访问权限❸。由于Mutant的DACL为空，在访问检查期间不会授予此访问权限，而我们在新句柄上获得了`ModifyState`，因此我们知道没有执行访问检查。最后，我们尝试通过请求`GenericAll`访问权限来增加我们的访问权限❹。由于我们请求的访问权限高于句柄当前拥有的权限，现在必须执行访问检查。此检查导致拒绝访问错误。

如果在创建Mutant时未设置安全描述符，则对象将没有关联的安全属性，最后一次检查将成功，授予完全访问权限。如第2章所述，在将未命名句柄复制到权限较低的进程时，如果降低访问权限，需要格外小心；目标进程可能能够将句柄重新复制为具有更多访问权限的句柄。在代码清单 8-5中，我们测试`NtDuplicateObject`的`NoRightsUpgrade`标志，以了解它如何影响句柄复制访问检查。




```
PS> $m = New-NtMutant -Access ModifyState
PS> Use-NtObject($m2 = Copy-NtObject -Object $m -DesiredAccess GenericAll) {
    $m2.GrantedAccess
}
ModifyState, Delete, ReadControl, WriteDac, WriteOwner, Synchronize

PS> Use-NtObject($m2 = Copy-NtObject -Object $m -NoRightsUpgrade) {
    Use-NtObject($m3 = Copy-NtObject -Object $m2 -DesiredAccess GenericAll) {}
}
Copy-NtObject : (0xC0000022) - {Access Denied}
A process has requested access to an object, ...
```


*代码清单 8-5：测试NtDuplicateObject的NoRightsUpgrade标志*

我们首先创建一个未命名的Mutant对象，该对象将没有关联的安全描述符。我们仅请求具有`ModifyState`访问权限的初始句柄。然而，我们尝试复制具有`GenericAll`访问权限的新句柄却成功了，授予我们完全访问权限。

现在我们测试`NoRightsUpgrade`标志。由于我们未指定任何访问掩码，句柄将以`ModifyState`访问权限被复制。使用新句柄，我们再次执行复制，这次请求`GenericAll`访问权限。我们可以观察到句柄复制失败。这不是由于访问检查，而是因为内核中句柄条目上设置的标志，指示任何请求更多访问权限的操作应立即失败。这防止了句柄被用于获取额外的访问权限。

复制句柄的错误处理可能导致漏洞；例如，CVE-2019-0943，这是我在Windows上一个负责缓存字体文件详细信息的特权服务中发现的问题。该服务将Section对象句柄以只读访问权限复制到沙箱进程。然而，沙箱进程可以将句柄转换回可写节句柄，并且该节可以被映射到内存中作为可写。这允许沙箱进程修改特权服务的状态并逃逸沙箱。Windows通过使用`NoRightsUpgrade`标志复制句柄来修复此漏洞。

线程进程上下文

每个线程都与一个进程相关联。通常，当发生访问检查时，内核从调用线程的对象结构中提取进程对象，并使用它来查找用于访问检查的主令牌。但线程还有第二个与之关联的进程对象：当前进程上下文，它指示线程当前正在其中执行代码的进程。

通常情况下，这些对象是相同的；然而，内核有时会将当前进程上下文切换到另一个进程，以在某些任务（如句柄或虚拟内存访问）中节省时间。当发生进程切换时，线程上的任何访问检查都会查找切换后进程的主令牌，而不是与线程关联的进程所属的令牌。句柄复制操作利用了这种进程上下文切换：内核首先查询源进程的句柄表，然后将调用线程的进程上下文切换到目标进程，以在该进程的句柄表中创建新句柄。

进程可能滥用此行为，将具有更多访问权限的句柄复制给权限较低的进程。如果在模拟自己的令牌（该令牌具有对对象的访问权限）时调用 `NtDuplicateObject` 系统调用，当访问检查运行时，它会捕获线程的 `SECURITY_SUBJECT_CONTEXT`，将主令牌设置为目标进程的令牌。但关键在于，它还会将模拟令牌设置为正在模拟的身份。结果是，访问检查将针对调用者的模拟令牌运行，而不是目标进程的主令牌。这允许复制句柄时授予额外的访问权限，即使目标进程的主令牌无法通过这些权限的访问检查。不过，在实践中，你不应依赖此行为；这是一个实现细节，可能会发生变化。

在遍历检查和句柄复制期间发生的访问检查通常对用户不可见，但两者都与单个资源的安全性相关。接下来，我们将讨论访问检查如何限制我们能够提取的信息以及针对一组资源可以执行的操作。这些限制基于调用者的令牌，而不管这些资源的单独访问集如何。

### 沙箱令牌检查

自Windows 8起，微软一直致力于通过规避沙箱令牌限制来增强系统安全性。这对于处理来自互联网不可信内容的软件（如网页浏览器和文档阅读器）尤为重要。

内核实现了两个API，通过访问检查来确定调用者是否处于沙箱中：`ExIsRestrictedCaller`（Windows 8引入）和`RtlIsSandboxToken`（Windows 10引入）。这两个API产生的结果相同；区别在于`ExIsRestrictedCaller`检查调用者的令牌，而`RtlIsSandboxToken`检查指定的令牌对象，该对象不一定是调用者的。

在内部，这些API对令牌执行访问检查，仅当令牌不在沙箱中时才授予访问权限。代码清单 8-6展示了在PowerShell中重新实现此访问检查的过程。




```
PS> $type = New-NtType -Name "Sandbox" -GenericRead 0x20000 
-GenericAll 0x1F0001
PS> $sd = New-NtSecurityDescriptor -NullDacl -Owner "SY" -Group "SY" 
-Type $type
PS> Set-NtSecurityDescriptorIntegrityLevel $sd Medium -Policy NoReadUp
PS> Get-NtGrantedAccess -SecurityDescriptor $sd -Access 0x20000 -PassResult
Status               Granted Access Privileges
------               -------------- ----------
STATUS_SUCCESS       GenericRead    NONE

PS> Use-NtObject($token = Get-NtToken -Duplicate -IntegrityLevel Low) {
    Get-NtGrantedAccess -SecurityDescriptor $sd -Access 0x20000
-Token $token -PassResult
}
Status               Granted Access Privileges
------               -------------- ----------
STATUS_ACCESS_DENIED None           NONE
```


*代码清单 8-6：沙箱令牌的访问检查*

首先，我们需要使用`New-NtType`命令定义一个虚拟的内核对象类型。这允许我们为访问检查指定通用映射。我们仅指定`GenericRead`和`GenericAll`值，因为在此上下文中写入和执行访问并不重要。请注意，新类型仅存在于PowerShell本地；内核对此一无所知。

然后，我们定义一个具有NULL DACL的安全描述符，并将所有者组SID设置为*SYSTEM*用户。如前章所述，使用NULL DACL将拒绝lowbox令牌的访问，但不会拒绝其他类型的沙箱令牌，如受限令牌。

为了处理其他令牌类型，我们添加了一个带有`NoReadUp`策略的中等强制标签ACE。因此，任何完整性级别低于中等的令牌将失败访问通用映射的`GenericRead`字段中指定的掩码。lowbox令牌忽略中等强制标签，但我们已经通过NULL DACL覆盖了这些令牌。请注意，此安全描述符不将具有中等完整性级别的受限令牌视为沙箱令牌。这是否为有意遗漏或实现中的错误尚不清楚。

现在，我们可以使用`Get-NtGrantedAccess`命令，使用当前非沙箱令牌执行访问检查。访问检查成功，授予我们`GenericRead`访问权限。如果我们使用具有低完整性级别的令牌重复检查，系统将拒绝访问，表明该令牌处于沙箱中。

在幕后，内核API调用`SeAccessCheck` API，如果调用者具有标识级模拟令牌，该API将返回错误。因此，即使代码清单 8-6中的实现可能表明相反，内核也会将某些模拟令牌视为沙箱令牌。

当任一API指示调用者处于沙箱中时，内核会改变其行为，执行以下操作：

- 仅列出可直接访问的进程和线程。
- 阻止访问已加载的内核模块。
- 枚举打开的句柄及其内核对象地址。
- 创建任意文件和对象管理器符号链接。
- 创建具有更多访问权限的新受限令牌。

例如，在代码清单 8-7中，我们在模拟低完整性级别令牌时查询句柄，但被拒绝访问。




```
PS> Invoke-NtToken -Current -IntegrityLevel Low {
    Get-NtHandle -ProcessId $pid
}
Get-NtHandle : (0xC0000022) - {Access Denied}
A process has requested access to an object, ...
```


*代码清单 8-7：模拟低完整性级别令牌时查询句柄信息*

虽然只有内核模式代码可以访问`ExIsRestrictedCaller`，但您可以在用户模式下访问`RtlIsSandboxToken`，因为它也在*NTDLL*中导出。这允许您使用令牌句柄查询内核，以了解内核是否认为它是沙箱令牌。`RtlIsSandboxToken` API将其结果暴露在令牌对象的`IsSandbox`属性中，如代码清单 8-8所示。




```
PS> Use-NtObject($token = Get-NtToken) {
    $token.IsSandbox
}
False

PS> Use-NtObject($token = Get-NtToken -Duplicate -IntegrityLevel Low) {
    $token.IsSandbox
}
True
```


*代码清单 8-8：检查令牌的沙箱状态*

`Get-NtProcess`返回的进程对象具有`IsSandboxToken`属性。在内部，此属性打开进程的令牌并调用`IsSandbox`。我们可以使用此属性轻松发现哪些进程处于沙箱中，例如使用代码清单 8-9中的脚本。




```
PS> Use-NtObject($ps = Get-NtProcess -FilterScript {$_.IsSandboxToken}) {
    $ps | ForEach-Object {Write-Host "$($_.ProcessId) $($_.Name)"}
}
7128 StartMenuExperienceHost.exe
7584 TextInputHost.exe
4928 SearchApp.exe
7732 ShellExperienceHost.exe
1072 Microsoft.Photos.exe
7992 YourPhone.exe
```


*代码清单 8-9：枚举当前用户的所有沙箱进程*

这些沙箱检查是限制信息泄露和限制危险功能（如符号链接）的重要特性，这些功能会提高攻击者逃逸沙箱并获取额外特权的机会。例如，阻止对句柄表的访问可防止泄露内核对象地址，这些地址可能被用来利用内核内存损坏漏洞。

我们现在已经涵盖了访问检查在非资源打开目的上的三种用途。本章最后将描述一些简化对一系列单个资源进行访问检查的命令。

### 自动化访问检查

上一章提供了一个示例，使用 `Get-NtGrantedAccess` 来确定一组内核对象的授予访问权限。如果您需要检查其他类型的资源（如文件），则需要修改该脚本以使用文件命令。

由于跨资源范围检查授予访问权限是一项非常实用的操作，PowerShell 模块提供了几个命令来自动化此过程。这些命令旨在让您快速评估 Windows 系统上可用资源的安全攻击面。它们都以 `Get-Accessible` 开头，您可以使用 `Get-Command` 列出它们，如 代码清单 8-10 所示。



```
PS> Get-Command Get-Accessible* | Format-Wide
Get-AccessibleAlpcPort                       Get-AccessibleDevice
Get-AccessibleEventTrace                     Get-AccessibleFile
Get-AccessibleHandle                         Get-AccessibleKey
Get-AccessibleNamedPipe                      Get-AccessibleObject
Get-AccessibleProcess                        Get-AccessibleScheduledTask
Get-AccessibleService                        Get-AccessibleToken
Get-AccessibleWindowStation                  Get-AccessibleWnf
```


*代码清单 8-10：列出 Get-Accessible\* 命令*

我们将在后续章节中回到其中一些命令。在这里，我们将重点介绍 `Get-AccessibleObject` 命令，它可用于在整个 OMNS 上自动化访问检查。该命令允许您指定要检查的 OMNS 路径，然后枚举 OMNS 并报告最大授予访问权限或是否可以授予特定访问掩码。

您还可以指定用于访问检查的令牌。该命令可以从以下列表中获取令牌：

- 令牌对象
- 进程对象
- 进程名称
- 进程 ID
- 进程命令行

如果运行命令时未指定任何选项，它将使用当前的主令牌。然后，它将基于 OMNS 路径枚举所有对象，并对每个指定的令牌执行访问检查。如果访问检查成功，该命令将生成一个包含结果详细信息的结构化对象。代码清单 8-11 显示了一个示例。



```
PS> Get-AccessibleObject -Path "\"
TokenId Access                     Name
------- ------                     ----
C5856B9 GenericExecute|GenericRead    \
```


*代码清单 8-11：从 OMNS 根获取可访问对象*

在这里，我们对 OMNS 的根运行命令，并在输出中收到三列：

TokenId  用于访问检查的令牌的唯一标识符

Access  授予的访问权限，映射到通用访问权限

Name  被检查资源的名称

我们可以使用 TokenId 来区分命令指定的不同令牌的结果。

此输出只是 `Get-AccessibleObject` 命令生成结果的一个子集。您可以使用 `Format-List` 等命令提取其余信息。您还可以使用 `Format-NtSecurityDescriptor` PowerShell 命令显示用于执行访问检查的安全描述符副本，如 代码清单 8-12 所示。



```
PS> Get-AccessibleObject -Path \ | Format-NtSecurityDescriptor -Summary
<Owner> : BUILTIN\Administrators
<Group> : NT AUTHORITY\SYSTEM
<DACL>
Everyone: (Allowed)(None)(Query|Traverse|ReadControl)
NT AUTHORITY\SYSTEM: (Allowed)(None)(Full Access)
BUILTIN\Administrators: (Allowed)(None)(Full Access)
NT AUTHORITY\RESTRICTED: (Allowed)(None)(Query|Traverse|ReadControl)
```


*代码清单 8-12：显示用于访问检查的安全描述符*

由于我们在这里对目录运行了命令，您可能想知道它是否也会列出目录中包含的对象。默认情况下不会；该命令将路径作为对象打开并执行访问检查。如果您想递归检查目录中的所有对象，则需要指定 `Recurse` 参数。`Get-AccessibleObject` 命令还接受 `Depth` 参数，您可以使用它来指定最大递归深度。如果您以非管理员用户身份运行递归检查，可能会看到许多警告，如 代码清单 8-13 所示。



```
PS> Get-AccessibleObject -Path "\" -Recurse
WARNING: Couldn't access \PendingRenameMutex - Status: STATUS_ACCESS_DENIED
WARNING: Couldn't access \ObjectTypes - Status: STATUS_ACCESS_DENIED
--snip--
```


*代码清单 8-13：递归枚举对象时的警告*

您可以通过将 `WarningAction` 参数设置为 `Ignore` 来关闭警告，但请记住，这些警告是在尝试告诉您某些信息。为了使命令正常工作，它需要打开每个对象并查询其安全描述符。从用户模式来看，这需要在打开期间通过访问检查；如果您没有权限以 `ReadControl` 访问权限打开对象，则命令无法执行访问检查。为了获得更好的结果，您可以以管理员身份运行命令，而为了获得最佳结果，请使用 `Start-Win32ChildProcess` 命令以 *SYSTEM* 用户身份启动 PowerShell shell。

默认情况下，该命令将使用调用者的令牌执行访问检查。但如果您以管理员身份运行命令，您可能不希望出现这种行为，因为几乎所有资源都允许管理员完全访问。相反，请考虑指定任意令牌来检查资源。例如，当以 UAC 管理员身份运行时，以下命令使用管理员令牌递归打开资源，但使用来自 Explorer 进程的非管理员令牌执行访问检查：


```
PS> Get-AccessibleObject -Path \ -ProcessName explorer.exe -Recurse
```

通常，我们希望筛选要检查的对象列表。你可以对所有对象运行访问检查，然后再筛选列表，但这会浪费大量工作。为了节省时间，`Get-AccessibleObject` 命令支持多个筛选参数：

TypeFilter  要检查的NT类型名称列表

Filter  用于限制打开哪些对象的名称筛选器；可包含通配符

Include  用于决定输出中包含哪些结果的名称筛选器

Exclude  用于决定输出中排除哪些结果的名称筛选器

Access  用于将输出限制为仅包含具有特定授予访问权限的对象的访问掩码

例如，以下命令将查找所有可以以`GenericAll`访问权限打开的`Mutant`对象：

```
PS> Get-AccessibleObject -Path \ -TypeFilter Mutant -Access GenericAll -Recurse
```

默认情况下，`Access`参数要求所有访问权限都获得后才输出结果。你可以通过指定`AllowPartialAccess`来修改此行为，这将输出与指定访问权限部分匹配的任何结果。如果你希望查看所有结果，无论授予的访问权限如何，请指定`AllowEmptyAccess`。

### 实际示例

让我们通过一些实际示例来总结本章中你学到的命令。

#### 简化对象的访问检查

在上一章中，我们使用了 `Get-NtGrantedAccess` 命令来自动化对内核对象的访问检查，并确定其最大授予访问权限。为此，我们首先需要查询对象的安全描述符。然后，我们将该值连同要检查的内核对象类型一起传递给命令。

如果你拥有对象的句柄，可以通过指定 `Object` 参数来简化对 `Get-NtGrantedAccess` 命令的调用，如 代码清单 8-14 所示。




```
PS> $key = Get-NtKey HKLM\Software -Win32Path -Access ReadControl
PS> Get-NtGrantedAccess -Object $key
QueryValue, EnumerateSubKeys, Notify, ReadControl
```


*代码清单 8-14：对对象执行访问检查*

使用 `Object` 参数无需手动提取对象的安全描述符，并且会自动为内核对象类型选择正确的通用映射结构。这降低了在执行对象访问检查时出错的风险。

#### 查找可写的 Section 对象

系统使用 Section 对象在进程之间共享内存。如果特权进程设置了较弱的安全描述符，那么较低权限的进程可能能够打开并修改 Section 的内容。如果该 Section 包含受信任的参数，可能会欺骗特权进程执行特权操作，从而导致安全问题。

我在 Internet Explorer 的沙箱配置中发现了此类漏洞，即 CVE-2014-6349。该配置错误地保护了共享的 Section 对象，允许沙箱化的 Internet Explorer 进程打开它并完全禁用沙箱。我通过在所有命名 Section 对象上执行 `MapWrite` 访问的访问检查发现了此问题。一旦我确定了具有此访问权限的所有 Section，我手动判断了其中是否有任何可以从沙箱中利用的。在 代码清单 8-15 中，我们使用 `Get-AccessibleObject` 命令自动化发现可写的 Section。




```
❶ PS> $access = Get-NtAccessMask -SectionAccess MapWrite -AsGenericAccess
❷ PS> $objs = Use-NtObject($token = Get-NtToken -Duplicate 
-IntegrityLevel Low) {
  ❸ Get-AccessibleObject -Win32Path "\" -Recurse -Token $token
-TypeFilter Section -Access $access
}
PS> $objs | ForEach-Object {
  ❹ Use-NtObject($sect = Get-NtSection -Path $_.Name) {
      Use-NtObject($map = Add-NtSection $sect -Protection ReadWrite 
-ViewSize 4096) {
         Write-Host "$($sect.FullPath)"
         Out-HexDump -ShowHeader -ShowAscii -HideRepeating -Buffer $map | 
Out-Host
      }
    }
}
\Sessions\1\BaseNamedObjects\windows_ie_global_counters
00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  - 0123456789ABCDEF
-------------------------------------------------------------------
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  - ................
-> REPEATED 1 LINES
00 00 00 00 00 00 00 00 00 00 00 00 1C 00 00 00  - ................
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  - ................
--snip--
```


*代码清单 8-15：枚举低完整性级别令牌的可写 Section 对象*

我们首先计算 `MapWrite` 访问的访问掩码，并将其转换为通用访问枚举 ❶。`Get-AccessibleObject` 命令只接受通用访问，因为它事先不知道你可能想要检查哪些对象。然后，我们复制当前用户的令牌并将其完整性级别设置为低，从而生成一个简单的沙箱 ❷。

我们将令牌和访问掩码传递给 `Get-AccessibleObject`，通过向 `Win32Path` 参数指定单个路径分隔符，在用户的 *BaseNamedObjects* 目录中执行递归检查 ❸。命令返回的结果应仅包含可以打开以进行 `MapWrite` 访问的 Section。

最后，我们枚举发现的 Section 列表，显示它们的名称以及任何发现的可写 Section 对象的初始内容 ❹。我们打开每个命名 Section，将最多前 4,096 字节映射到内存中，然后将内容输出为十六进制转储。我们将 Section 映射为可写，因为可能 Section 对象的安全描述符授予了 `MapWrite` 访问权限，但该 Section 是以只读方式创建的。在这种情况下，映射 `ReadWrite` 将失败并返回错误。

你可以直接使用此脚本来查找值得注意的可写 Section。你不必使用沙箱令牌；查看普通用户可用的、由特权进程拥有的 Section 可能会很有趣。你也可以将其作为模板，对任何其他内核对象类型执行相同的检查。

### 总结

在本章中，我们探讨了在打开资源之外使用访问检查的一些示例。我们首先考虑了遍历检查，它用于确定用户是否可以遍历容器层次结构，例如对象目录。然后，我们讨论了在进程之间复制句柄时如何使用访问检查，包括如果对象没有名称或安全描述符配置，这如何可能导致安全问题。

接下来，我们探讨了如何使用访问检查来确定调用者的令牌是否被沙箱化。内核这样做是为了限制对信息或某些操作的访问，从而使利用特定类别的安全漏洞变得更加困难。最后，我们看到了如何使用 `Get-Accessible` 命令自动化对各种资源类型的访问检查。我们研究了所有命令共有的基本参数，以及如何使用它们来枚举可访问的命名内核对象。

这就是我们对访问检查过程的全部探讨。在下一章中，我们将介绍 SRM 的最后一项职责：安全审计。

## 9. 安全审计

与访问检查过程紧密相连的是审计过程。管理员可以配置系统的审计机制，以生成对访问资源的日志记录。每条日志事件将包含关于打开资源的用户和应用程序的详细信息，以及访问是成功还是失败。这些信息有助于我们识别不正确的安全设置，或检测对敏感资源的恶意访问。

在本章简短的内容中，我们首先将讨论内核生成资源访问日志后，这些日志存储在哪里。接着，我们将描述系统管理员如何配置审计机制。最后，我们将详细说明如何通过SACL配置单个资源，以生成审计日志事件。

### 安全事件日志

每当访问检查成功或失败时，Windows 都会生成日志事件。内核将这些日志事件写入*安全事件日志*，该日志仅管理员可访问。

在对内核资源执行访问检查时，Windows 将生成以下类型的审计事件。安全事件日志通过括号中的事件 ID 来表示这些事件：

- 对象句柄已打开 (4656)
- 对象句柄已关闭 (4658)
- 对象已删除 (4660)
- 对象句柄已复制 (4690)
- SACL 已更改 (4717)

当我们通过内核系统调用（如 `NtCreateMutant`）访问资源时，审计机制会自动生成这些事件。但对于与对象相关的审计事件，我们必须首先配置系统的两个方面：设置系统策略以生成审计事件，并在资源的 SACL 中启用审计 ACE。让我们依次讨论这些配置要求。

#### 配置系统审计策略

大多数 Windows 用户不需要捕获内核资源的审计信息，因此审计策略默认是禁用的。企业环境通常通过*域安全策略*来配置审计策略，该策略由企业网络分发到各个设备。

不在企业网络中的用户可以手动启用审计策略。一种方法是编辑*本地安全策略*，其界面与域安全策略相同，但仅适用于当前系统。审计策略有两种类型：Windows 7 之前使用的旧版策略和高级审计策略。建议使用高级审计策略，因为它提供更细粒度的配置；我们不再讨论旧版策略。

如果在 PowerShell 中运行 `secpol.msc` 命令打开本地安全策略编辑器，可以查看高级审计策略的当前配置，如 图 9-1 所示。



![img](./image/02.PART%20II%20THE%20WINDOWS%20SECURITY%20REFERENCE%20MONITOR/Figure9-1.webp)

图 9-1：显示高级审计策略的安全策略编辑器

如您所见，审计策略中的类别当前未配置。为了探索审计事件是如何生成的，我们将使用 PowerShell 临时启用所需的审计策略并运行一些示例代码。您使用 PowerShell 所做的任何更改都不会反映在本地安全策略中，该策略将在下次同步时恢复（例如，在重启或企业网络上更新组策略时）。您可以通过在 PowerShell 或命令提示符中以管理员身份运行 `gpupdate.exe /force` 命令来强制同步设置。

高级审计策略有两个层级：顶层类别和多个子类别。您可以使用 `Get-NtAuditPolicy` 查询顶层类别，如 代码清单 9-1 所示。




```
PS> Get-NtAuditPolicy
Name               SubCategory Count
----               -----------------
System             5
Logon/Logoff       11
Object Access      14
Privilege Use      3
Detailed Tracking  6
Policy Change      6
Account Management 6
DS Access          4
Account Logon      4
```


*代码清单 9-1：顶层审计策略类别*

在输出中，您可以看到每个类别的名称及其子类别的数量。每个类别还关联一个 GUID，但该值默认是隐藏的。要查看它，请从命令输出中选择 `Id` 属性，如 代码清单 9-2 所示。




```
PS> Get-NtAuditPolicy | Select-Object Name, Id
Name               Id
----               --
System             69979848-797a-11d9-bed3-505054503030
Logon/Logoff       69979849-797a-11d9-bed3-505054503030
Object Access      6997984a-797a-11d9-bed3-505054503030
--snip--
```


*代码清单 9-2：显示类别 GUID*

您可以使用 `ExpandCategory` 参数显示子类别。在 代码清单 9-3 中，我们按名称指定 System 类别，然后展开输出以显示其子类别。




```
PS> Get-NtAuditPolicy -Category System -ExpandCategory
Name                      Policy
----                      ------
Security State Change     Unchanged
Security System Extension Unchanged
System Integrity          Unchanged
IPsec Driver              Unchanged
Other System Events       Unchanged
```


*代码清单 9-3：显示审计策略的子类别*

您还可以使用 `CategoryGuid` 参数通过指定 GUID 来选择类别。审计策略基于这些子类别。每个子类别策略可以具有以下一个或多个值：

未更改  策略未配置，不应更改。

成功  当可审计资源成功打开时，策略应生成审计事件。

失败  当可审计资源无法打开时，策略应生成审计事件。

无  策略不应生成任何审计事件。

在 代码清单 9-3 中，所有子类别都显示为“未更改”，这意味着尚未配置任何策略。我们可以通过以管理员身份运行 代码清单 9-4 中所示的命令来启用内核对象审计。




```
PS> Enable-NtTokenPrivilege SeSecurityPrivilege
PS> Set-NtAuditPolicy -Category ObjectAccess -Policy Success, 
Failure -PassThru
Name                           Policy
----                           ------
File System                    Success, Failure
Registry                       Success, Failure
Kernel Object                  Success, Failure
SAM                            Success, Failure
Certification Services         Success, Failure
Application Generated          Success, Failure
Handle Manipulation            Success, Failure
File Share                     Success, Failure
Filtering Platform Packet Drop Success, Failure
Filtering Platform Connection  Success, Failure
Other Object Access Events     Success, Failure
Detailed File Share            Success, Failure
Removable Storage              Success, Failure
Central Policy Staging         Success, Failure
```

*代码清单 9-4：设置策略并查看生成的 ObjectAccess 审核策略列表*

在这里，我们为 ObjectAccess 下的所有子类别启用了成功和失败审核策略。要进行此修改，我们需要 SeSecurityPrivilege 特权。我们可以通过使用 `SubCategoryName` 参数或使用 `SubCategoryGuid` 指定 GUID，按名称设置单个子类别，而不是整个类别。

我们通过指定 `PassThru` 参数来确认审核策略已正确配置，该参数列出了修改后的 `SubCategory` 对象。输出显示了一些重要的审核策略，包括文件系统、注册表和内核对象，这些分别对文件、注册表键和其他内核对象启用审核。

您可以以管理员身份运行以下命令，以禁用我们在 代码清单 9-4 中所做的更改：


```
PS> Set-NtAuditPolicy -Category ObjectAccess -Policy None
```


除非您出于某种原因需要启用审核策略，否则最好在完成实验后将其禁用。

#### 配置每用户审核策略

除了配置系统范围的策略外，还可以按用户配置审核策略。您可以使用此功能在系统未定义整体审核策略的情况下，为特定用户帐户添加审核。您也可以使用它来将特定用户帐户排除在审核之外。为促进此行为，每用户策略的设置略有不同：

未更改  策略未配置。设置后，策略不应更改。

成功包含  策略应在成功时生成审核事件，无论系统策略如何。

成功排除  策略绝不应在成功时生成审核事件，无论系统策略如何。

失败包含  策略应在失败时生成审核事件，无论系统策略如何。

失败排除  策略绝不应在失败时生成审核事件，无论系统策略如何。

无  策略绝不应生成审核事件。

要配置每用户策略，您可以在使用 `Set-NtAuditPolicy` 命令时，将 SID 指定给 `User` 参数。此 SID 必须代表用户帐户；它不能代表组（如 *Administrators*）或服务帐户（如 *SYSTEM*），否则在设置策略时会收到错误。

代码清单 9-5 为当前用户配置了每用户策略。您必须以管理员身份运行这些命令。




```
PS> Enable-NtTokenPrivilege SeSecurityPrivilege
PS> $sid = Get-NtSid
PS> Set-NtAuditPolicy -Category ObjectAccess -User $sid -UserPolicy 
SuccessExclude
PS> Get-NtAuditPolicy -User $sid -Category ObjectAccess -ExpandCategory
Name          User           Policy
----          ----           ------
File System   GRAPHITE\admin SuccessExclude
Registry      GRAPHITE\admin SuccessExclude
Kernel Object GRAPHITE\admin SuccessExclude
SAM           GRAPHITE\admin SuccessExclude
--snip--
```


*代码清单 9-5：配置每用户审核策略*

在这里，我们将用户的 SID 指定给 `User` 参数，然后指定 `SuccessExclude` 用户策略。这将仅为此用户排除成功审核事件。如果您想移除用户的每用户策略，可以指定 `None` 用户策略：


```
PS> Set-NtAuditPolicy -Category ObjectAccess -User $sid -UserPolicy None
```


您还可以使用 `Get-NtAuditPolicy` 的 `AllUser` 参数枚举所有已配置策略的用户，如 代码清单 9-6 所示。




```
PS> Get-NtAuditPolicy -AllUser
Name          User           SubCategory Count
----          ----           -----------------
System        GRAPHITE\admin 5
Logon/Logoff  GRAPHITE\admin 11
Object Access GRAPHITE\admin 14
--snip--
```


*代码清单 9-6：查询所有用户的每用户策略*

您现在知道如何查询和设置系统及特定用户的策略。接下来，我们将探讨如何授予用户查询和设置这些策略所需的访问权限。

### 审计策略安全性

要查询或设置策略，调用者必须在其令牌上启用 `SeSecurityPrivilege` 特权。如果未启用该特权，LSASS 将基于系统配置中的安全描述符执行访问检查。我们可以在安全描述符中配置以下访问权限，以授予用户查询或设置系统或单个用户策略的能力：

`SetSystemPolicy`  允许设置系统审计策略

`QuerySystemPolicy`  允许查询系统审计策略

`SetUserPolicy`  允许设置按用户的审计策略

`QueryUserPolicy`  允许查询按用户的审计策略

`EnumerateUsers`  允许枚举所有按用户的审计策略

`SetMiscPolicy`  允许设置杂项审计策略

`QueryMiscPolicy`  允许查询杂项审计策略

似乎没有标准的审计 API 使用 `SetMiscPolicy` 和 `QueryMiscPolicy` 访问权限，但由于它们在 Windows SDK 中已定义，我在此处将其包含以保持完整性。

作为管理员，您可以通过启用 `SeSecurityPrivilege` 并使用 `Get-NtAuditSecurity` 命令查询当前配置的安全描述符，如 代码清单 9-7 所示。



```
PS> Enable-NtTokenPrivilege SeSecurityPrivilege
PS> $sd = Get-NtAuditSecurity
PS> Format-NtSecurityDescriptor $sd -Summary -MapGeneric
<DACL>
❶ BUILTIN\Administrators: (Allowed)(None)(GenericRead)
NT AUTHORITY\SYSTEM: (Allowed)(None)(GenericRead)
```


*代码清单 9-7：查询并显示审计安全描述符*

我们将查询到的安全描述符传递给 `Format-NtSecurityDescriptor` 以显示 DACL。请注意，只有 *Administrators* 和 *SYSTEM* 可以访问该策略 ❶。此外，它们仅限于 `GenericRead` 访问权限，这允许用户查询策略但不能修改它。因此，即使是管理员也需要启用 `SeSecurityPrivilege` 来修改审计策略，因为该特权会绕过任何访问检查。

> 注意
>
> *未获得策略读取权限的用户仍然可以查询高级审计类别和子类别，这些类别会忽略安全描述符。但是，他们不会获得查询已配置设置的权限。`Get-NtAuditPolicy` 将返回 `Unchanged` 值，用于用户无法查询的审计设置。*

如果您希望允许非管理员更改高级审计策略，可以使用 `Set-NtAuditSecurity` 命令更改安全描述符。以管理员身份运行 代码清单 9-8 中的命令。



```
PS> Enable-NtTokenPrivilege SeSecurityPrivilege
PS> $sd = Get-NtAuditSecurity
PS> Add-NtSecurityDescriptorAce $sd -Sid "LA" -Access GenericAll
PS> Set-NtAuditSecurity $sd
```


*代码清单 9-8：修改审计安全描述符*

我们首先查询现有的审计策略安全描述符，并授予本地管理员所有访问权限。然后使用 `Set-NtAuditSecurity` 命令设置修改后的安全描述符。现在，本地管理员无需启用 `SeSecurityPrivilege` 即可查询和修改审计策略。

您通常不应重新配置审计策略的安全性，当然也不应授予所有用户写入权限。请注意，安全描述符不影响谁可以查询或设置安全描述符本身；只有启用了 `SeSecurityPrivilege` 的调用者才能执行此操作，无论安全描述符中的值如何。

#### 配置资源 SACL

仅启用审计策略不足以开始生成审计事件。我们还需要配置对象的 SACL 以指定要使用的审计规则。要在对象上设置 SACL，我们再次需要启用 `SeSecurityPrivilege`，这只能由管理员完成。代码清单 9-9 演示了创建带有 SACL 的 Mutant 对象的过程。



```
PS> $sd = New-NtSecurityDescriptor -Type Mutant
PS> Add-NtSecurityDescriptorAce $sd -Type Audit -Access GenericAll
-Flags SuccessfulAccess, FailedAccess -KnownSid World -MapGeneric
PS> Enable-NtTokenPrivilege SeSecurityPrivilege
PS> Clear-EventLog -LogName "Security"
PS> Use-NtObject($m = New-NtMutant "ABC" -Win32Path -SecurityDescriptor $sd) {
    Use-NtObject($m2 = Get-NtMutant "ABC" -Win32Path) {
    }
}
```


*代码清单 9-9：创建带有 SACL 的 Mutant 对象*

我们首先创建一个空的安全描述符，然后向 SACL 添加一个 Audit ACE。我们可以添加的其他 ACE 类型包括 `AuditObject` 和 `AuditCallback`。

Audit ACE 的处理过程看起来很像 第 7 章 中描述的自由访问检查。SID 必须与调用令牌中的组匹配（包括任何 `DenyOnly` SID），并且访问掩码必须与授予访问权限的一个或多个位匹配。*Everyone* 组的 SID 是一个特例；无论 SID 是否在令牌中可用，它都将始终匹配。

除了任何常见的继承 ACE 标志（如 `InheritOnly`）之外，Audit ACE 必须指定 `SuccessfulAccess` 和 `FailedAccess` 标志中的一个或两个，这些标志为审计代码提供了生成审计条目的条件。

我们将创建一个带有包含SACL的安全描述符的Mutant对象。在创建对象之前，我们需要启用SeSecurityPrivilege特权。如果不这样做，创建将失败。为了更容易看到生成的审计事件，我们还会清空安全事件日志。接下来，我们创建对象，传入我们构建的SACL，然后重新打开它以触发审计日志的生成。

现在，我们可以使用Get-WinEvent查询安全事件日志，传入事件ID 4656以查找生成的审计事件（代码清单 9-10）。




```
PS> $filter = @{logname = 'Security'; id = @(4656)}
PS> Get-WinEvent -FilterHashtable $filter | Select-Object -ExpandProperty Message
A handle to an object was requested.
Subject:
        Security ID:    S-1-5-21-2318445812-3516008893-216915059-1002
        Account Name:   user
        Account Domain: GRAPHITE
        Logon ID:       0x524D0

Object:
        Object Server:          Security
        Object Type:            Mutant
        Object Name:            \Sessions\2\BaseNamedObjects\ABC
        Handle ID:              0xfb4
        Resource Attributes:    -

Process Information:
        Process ID:     0xaac
        Process Name:   C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe

Access Request Information:
        Transaction ID:         {00000000-0000-0000-0000-000000000000}
        Accesses:               DELETE
                                READ_CONTROL
                                WRITE_DAC
                                WRITE_OWNER
                                SYNCHRONIZE
                                Query mutant state

        Access Reasons:                         -
        Access Mask:                            0x1F0001
        Privileges Used for Access Check:       -
        Restricted SID Count:                   0
```


*代码清单 9-10：查看Mutant对象的打开审计事件*

我们首先为安全事件日志和事件ID 4656设置过滤器，该事件ID对应于句柄的打开。然后，我们使用Get-WinEvent配合过滤器，并选择事件的文本消息。

输出以事件的文本描述开始，这确认了它是在句柄被打开时生成的。之后是主题（Subject），包括用户信息，如SID和用户名。为了查找用户名，内核会将审计事件发送到LSASS进程。

接下来是所打开对象的详细信息。这些包括对象服务器（Security，代表SRM）、对象类型（Mutant）、对象的本地路径，以及句柄ID（对象的句柄编号）。如果您查询从NtCreateMutant系统调用返回的句柄值，它应该与此值匹配。然后我们获得一些基本的进程信息，最后是关于授予句柄的访问权限的信息。

我们如何区分成功和失败事件？最好的方法是提取KeywordsDisplayNames属性，其中包含“Audit Success”（如果句柄被打开）或“Audit Failure”（如果句柄无法打开）。代码清单 9-11显示了一个示例。




```
PS> Get-WinEvent -FilterHashtable $filter | Select-Object KeywordsDisplayNames
KeywordsDisplayNames
--------------------
{Audit Success}
{Audit Failure}
--snip--
```


*代码清单 9-11：提取KeywordsDisplayNames以查看成功或失败状态*

当您关闭对象的句柄时，您会收到另一个审计事件，事件ID为4658，如代码清单 9-12所示。




```
PS> $filter = @{logname = 'Security'; id = @(4658)}
PS> Get-WinEvent -FilterHashtable $filter | Select-Object -ExpandProperty Message
The handle to an object was closed.
Subject :
        Security ID:    S-1-5-21-2318445812-3516008893-216915059-1002
        Account Name:   user
        Account Domain: GRAPHITE
        Logon ID:       0x524D0

Object:
        Object Server:  Security
        Handle ID:      0xfb4

Process Information:
        Process ID:     0xaac
        Process Name:   C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
```


*代码清单 9-12：查看Mutant对象句柄关闭时生成的审计事件*

您可能会注意到，关于关闭对象句柄的信息比打开句柄时生成的信息略少。您可以使用句柄ID手动关联打开和关闭句柄的事件，这些ID应该匹配。

可以从用户模式使用一些额外的系统调用手动生成对象审计事件。但是，这样做需要SeAuditPrivilege特权，该特权通常仅授予*SYSTEM*账户，而不是普通管理员。

您可以使用NtAccessCheckAndAuditAlarm系统调用在访问检查的同时生成审计事件，该系统调用具有与正常访问检查相同的所有对象ACE变体。您可以使用带有Audit参数的Get-NtGrantedAccess PowerShell命令访问它。

您还可以使用NtOpenObjectAuditAlarm和NtCloseObjectAuditAlarm系统调用手动生成事件，PowerShell通过Write-NtAudit命令公开这些调用。以*SYSTEM*用户身份运行代码清单 9-13中的命令，以手动生成审计日志事件。




```
❶ PS> Enable-NtTokenPrivilege SeAuditPrivilege -WarningAction Stop
PS> $owner = Get-NtSid -KnownSid Null
PS> $sd = New-NtSecurityDescriptor -Type Mutant -Owner $owner -Group $owner
PS> Add-NtSecurityDescriptorAce $sd -KnownSid World -Access GenericAll 
-MapGeneric
❷ PS> Add-NtSecurityDescriptorAce $sd -Type Audit -Access GenericAll
-Flags SuccessfulAccess, FailedAccess -KnownSid World -MapGeneric
❸ PS> $handle = 0x1234
❹ PS> $r = Get-NtGrantedAccess $sd -Audit -SubsystemName "SuperSecurity"
-ObjectTypeName "Badger" -ObjectName "ABC" -ObjectCreation
-HandleId $handle -PassResult
❺ PS> Write-NtAudit -Close -SubsystemName "SuperSecurity" -HandleId $handle
-GenerateOnClose:$r.GenerateOnClose
```


*代码清单 9-13：手动生成审计日志事件*

我们首先启用SeAuditPrivilege ❶，否则脚本的其余部分将失败。此特权必须在主令牌上启用；您不能模拟具有该特权的令牌，这就是为什么您必须以*SYSTEM*用户身份运行PowerShell实例。

启用所需特权后，我们构建一个带有SACL的安全描述符，以审计成功和失败的访问尝试 ❷。我们生成一个假的句柄ID ❸；在正常审计事件中，此值将是内核句柄，但当我们从用户模式生成事件时，它可以是我们喜欢的任何值。然后，我们可以运行访问检查，指定Audit参数，该参数启用其他审计参数。我们需要指定SubsystemName、ObjectTypeName和ObjectName参数，这些参数可以是完全任意的。我们还指定句柄ID ❹。

在输出中，我们收到一个访问检查结果，其中包含一个额外的属性：`GenerateOnClose`，它指示我们是否需要写入一个关闭句柄事件。调用 `Write-NtAudit` 命令并指定 `Close` 参数，将调用 `NtCloseObjectAuditAlarm` 系统调用来生成该事件。我们这样做，并指定结果中的 `GenerateOnClose` 值 ❺。如果 `GenerateOnClose` 为 `False`，我们仍然需要写入关闭事件以完成审计，但实际的关闭事件不会写入审计日志。

如果在运行 代码清单 9-13 中的命令时没有收到任何审计事件，请确保您已启用对象审计，如我们在 代码清单 9-4 中所做的那样。

神秘的警报 ACE

在 表 5-3 的 ACE 类型列表中，您可能注意到与审计相关的 Alarm 类型。我在表中提到内核不使用此类型，如果您阅读 Microsoft 关于 Alarm ACE 类型的技术文档，您会看到“SYSTEM_ALARM_ACE 结构保留供将来使用”的表述。如果它一直被保留，那它的用途是什么？

很难说。从 Windows NT 3.1 开始，内核代码检查 Alarm ACE 类型，直到 Microsoft 在 Windows XP 中移除了该检查。Windows 开发者甚至定义了 `AlarmCallback`、`AlarmObject` 和 `AlarmObjectCallback` 变体，尽管在 Windows 2000 内核（引入对象 ACE 的地方）中似乎没有代码检查这些变体。从旧内核中可以清楚地看出 Alarm ACE 类型是被处理的；不太清楚的是 Alarm ACE 是否能生成要监控的事件。即使在处理 Alarm ACE 类型的 Windows 版本文档中，它也被标记为不支持。

至于 Alarm ACE 可能做了什么，它很可能是 Windows NT 源自 VMS 的遗留物。VMS 有类似 Windows NT 的安全模型，包括使用 ACL 和 ACE。在 VMS 中，审计 ACE 被写入审计日志文件，就像在 Windows 上一样，而警报 ACE 会在用户使用 `REPLY/ENABLE=SECURITY` 命令启用警报后，在系统控制台或操作员终端上生成实时临时安全事件。很可能 Microsoft 在 Windows 内核中添加了对这种 ACE 类型的支持，但从未实现发送这些实时事件的能力。随着现代日志记录替代方案（如 Windows 事件跟踪（ETW））的出现，它提供了更全面的实时安全信息，Microsoft 未来重新引入 Alarm ACE（或实现其变体）的可能性很小。

#### 配置全局 SACL

为每个资源正确配置 SACL 可能既困难又耗时。因此，高级审计策略允许您为文件或注册表项配置全局 SACL。如果资源没有 SACL，系统将使用此全局 SACL；对于已有 SACL 的资源，系统将合并全局 SACL 和资源 SACL。由于这些广泛的审计配置可能会淹没您的日志输出并妨碍您监控事件的能力，我建议您谨慎使用全局 SACL。

您可以通过指定 `File` 或 `Key` 值到 `Get-NtAuditSecurity` PowerShell 命令的 `GlobalSacl` 参数来查询全局 SACL。您也可以使用 `Set-NtAuditSecurity` 命令修改全局 SACL，指定相同的 `GlobalSacl` 参数。要测试此行为，请以管理员身份运行 代码清单 9-14 中的命令。




```
PS> Enable-NtTokenPrivilege SeSecurityPrivilege
PS> $sd = New-NtSecurityDescriptor -Type File
PS> Add-NtSecurityDescriptorAce $sd -Type Audit -KnownSid World
-Access WriteData -Flags SuccessfulAccess
PS> Set-NtAuditSecurity -GlobalSacl File -SecurityDescriptor $sd
PS> Get-NtAuditSecurity -GlobalSacl File |
Format-NtSecurityDescriptor -SecurityInformation Sacl -Summary
<SACL>
Everyone: (Audit)(SuccessfulAccess)(WriteData)
```


*代码清单 9-14：设置和查询全局文件 SACL*

我们首先构建一个包含单个 Audit ACE 的 SACL 的安全描述符。然后调用 `Set-NtAuditSecurity` 为 File 类型设置全局 SACL。最后，我们查询全局 SACL 以确保其设置正确。

您可以通过向 `Set-NtAuditSecurity` 传递一个具有 NULL SACL 的安全描述符来移除全局 SACL。要创建此安全描述符，请使用以下命令：


```
PS> $sd = New-NtSecurityDescriptor -NullSacl
```

### 实际示例

让我们通过一些实际示例来总结本章中你学到的命令。

#### 验证审计访问安全性

当你检查恶意代码是否已入侵不受信任的Windows系统时，最好验证安全设置未被修改。你可能想要执行的一项检查是确定非管理员用户是否拥有更改系统审计策略所需的访问权限。如果非管理员用户可以更改策略，他们就可以禁用审计并隐藏其对敏感资源的访问。

我们可以手动检查审计策略的安全描述符，或者使用`Get-NtGrantedAccess` PowerShell命令来完成。以管理员身份运行代码清单 9-15中的命令。




```
PS> Enable-NtTokenPrivilege SeSecurityPrivilege
PS> $sd = Get-NtAuditSecurity
PS> Set-NtSecurityDescriptorOwner $sd -KnownSid LocalSystem
PS> Set-NtSecurityDescriptorGroup $sd -KnownSid LocalSystem
PS> Get-NtGrantedAccess $sd -PassResult
Status         Granted Access Privileges
------         -------------- ----------
STATUS_SUCCESS GenericRead    NONE

PS> Use-NtObject($token = Get-NtToken -Filtered -Flags LuaToken) {
  Get-NtGrantedAccess $sd -Token $token -PassResult
}
Status               Granted Access Privileges
------               -------------- ----------
STATUS_ACCESS_DENIED 0              NONE
```


*代码清单 9-15：对审计策略安全描述符执行访问检查*

我们首先查询审计策略的安全描述符，并设置`Owner`和`Group`字段。这些字段是访问检查过程所必需的，但`Get-NtAuditSecurity`命令返回的安全描述符中不包含它们。

然后，我们可以将安全描述符传递给`Get-NtGrantedAccess`命令，以针对当前管理员令牌进行检查。结果表明调用者具有对审计策略的`GenericRead`访问权限，这允许他们查询策略，但在未启用`SeSecurityPrivilege`特权的情况下无法设置策略。

最后，我们可以通过使用`LuaToken`标志创建过滤令牌，从令牌中移除*Administrators*组。使用过滤令牌运行访问检查表明其对审计策略没有任何授予的访问权限（甚至没有读取权限）。如果第二次检查返回的状态不是`STATUS_ACCESS_DENIED`，则可以断定默认审计策略安全描述符已被更改，值得检查这是有意还是恶意行为。

#### 查找具有审计ACE的资源

大多数资源未配置SACL，因此你可能希望枚举系统上具有SACL的资源。这有助于你了解哪些资源可能生成审计日志事件。代码清单 9-16提供了一个简单示例，用于查找这些资源。以管理员身份运行命令。




```
PS> Enable-NtTokenPrivilege SeDebugPrivilege, SeSecurityPrivilege
❶ PS> $ps = Get-NtProcess -Access QueryLimitedInformation, AccessSystemSecurity
-FilterScript {
  ❷ $sd = Get-NtSecurityDescriptor $_ -SecurityInformation Sacl
    $sd.HasAuditAce
}
❸ PS> $ps | Format-NtSecurityDescriptor -SecurityInformation Sacl
Path: \Device\HarddiskVolume3\Windows\System32\lsass.exe
Type: Process
Control: SaclPresent

<SACL>
 - Type  : Audit
 - Name  : Everyone
 - SID   : S-1-1-0
 - Mask  : 0x00000010
 ❹ - Access: VmRead
 - Flags : SuccessfulAccess, FailedAccess

PS> $ps.Close()
```


*代码清单 9-16：查找配置了SACL的进程*

我们这里专注于`Process`对象，但你可以将相同方法应用于其他资源类型。

我们首先打开所有进程以获取`QueryLimitedInformation`和`AccessSystemSecurity`访问权限❶。我们对进程应用过滤器，查询`Process`对象的SACL，然后返回`HasAuditAce`属性的值❷。该属性指示安全描述符是否至少有一个审计ACE。

然后，我们将`Get-NtProcess`命令返回的结果通过管道传递给`Format-NtSecurityDescriptor`以显示SACL❸。在这种情况下，只有一个条目，即`LSASS`进程。我们可以看到，每当`LSASS`进程被以`VmRead`访问权限打开时，审计ACE就会记录一个事件❹。

这是Windows上的默认审计配置，用于检测对`LSASS`进程的访问。`VmRead`访问权限允许调用者读取进程的虚拟内存，此ACE旨在检测对`LSASS`内存内容的提取，其中可能包含密码和其他身份验证凭据。如果进程以任何其他访问权限打开，则不会生成审计日志条目。



### 总结

在本章中，我们涵盖了安全审计的基础知识。我们首先描述了安全事件日志以及审计资源访问时可能发现的日志条目类型。接下来，我们探讨了如何配置审计策略以及使用`Set-NtAuditPolicy`命令设置高级审计策略。我们还讨论了Windows如何控制对审计策略的访问，以及`SeSecurityPrivilege`特权的重要性，该特权几乎用于所有与审计相关的配置。

要启用对象上的审计，我们必须修改SACL以定义生成策略所启用事件的规则。我们通过示例演示了如何自动生成审计事件（使用SACL）以及手动生成审计事件（在用户模式访问检查期间）。

现在我们已经涵盖了SRM的所有方面：安全访问令牌、安全描述符、访问检查和审计。在本书的其余部分，我们将探讨用于向Windows系统进行身份验证的各种机制。