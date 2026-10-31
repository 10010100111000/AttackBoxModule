---
summary: Active Directory（第5版·第4卷），深度讲解Active Directory安全权限体系、动态访问控制（DAC）与安全审核、Schema架构自定义扩展实施、目录备份灾难恢复与维护，以及域环境版本升级。
---

## 第 16 章. Active Directory 安全:权限与审核

在 Active Directory 中设置权限与为文件设置权限非常相似。尽管您可能并不在意目录中的每个用户都能读取所有用户的电话号码，但您可能需要存储更敏感的信息并限制对这些信息的访问。当然，读取并不是唯一的问题。您还需要考虑创建、修改和删除权限，而最不希望发生的事情就是心怀不满或聪明的员工找到方法删除某个组织单位中的所有用户。

管理 Active Directory 中的权限并不一定是件令人头疼的事。您可以利用关于继承和复杂性的指导原则设计合理的权限方案，从而使系统管理员的工作轻松许多。Microsoft 提供的图形用户界面( GUI )对于简单任务很有效，但在管理复杂权限时就显得较为繁琐。Active Directory 服务接口( Active Directory Service Interfaces ,ADSI )也支持对 Active Directory 权限的管理，这为您打开了大量机会，使您能够使用脚本来跟踪问题并简单有效地操控访问权限。最后，如果您更倾向于使用图形界面之外的替代方案，Windows PowerShell 和 *DSACLS* 实用工具允许管理员从命令行管理权限。

然而，权限只是故事的一半。如果您允许某个用户修改特定组织单位下某个分支中每个用户的详细信息，您可以使用审核条目来监视该分支内对象和属性的创建、删除和更改。事实上，您可以使用审核来监视 Active Directory 中任何方面的修改。系统会跟踪审核事件的日志记录，然后您可以定期检查这些记录，或使用脚本或第三方工具在出现任何问题时快速向您发出警报。

动态访问控制( Dynamic Access Control ,DAC )是 Windows Server 中的一项重要新功能，Active Directory 有助于将其付诸实现。将您的林配置为支持对资源的基于声明的授权以及复合身份和中央访问策略等新功能，这项任务需要 Active Directory 管理员与 IT 组织其他成员以及整个业务部门密切协调。

### 16.1. 权限基础

图 16-1展示了基本架构。每个对象都会在 `nTSecurityDescriptor` 属性中存储一个名为安全描述符( Security Descriptor ,SD)的值。该属性包含描述该对象安全性所需的全部信息,其中包括一个指示安全描述符是否受继承保护的标志,以及两个称为访问控制列表( Access Control List ,ACL)的重要集合,用于存储相关权限。




![Active Directory security architecture](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663503.webp)


图 16-1. Active Directory 安全架构

第一个 ACL 称为系统访问控制列表( System Access Control List ,SACL),用于定义将触发成功和失败审核消息的权限事件。第二个称为自由访问控制列表( Discretionary Access Control List ,DACL),用于定义用户对该对象、其属性及其子对象所拥有的权限。这两个 ACL 各自包含一组访问控制项( Access Control Entry ,ACE),分别对应单独的审核条目或权限条目。

审核 ACE 和权限 ACE 既可以应用于整个对象,也可以应用于对象的各个属性。这样一来,管理员便可全面控制访问和审核的各个方面。审核 ACE 将在本章后文进一步讨论,但为了便于理解前文所述的其他权限相关主题,我们将在下一节中简要说明权限 ACE。

#### 权限访问控制条目( ACE )

每个权限访问控制条目( Access Control Entry ,ACE )由以下几部分组成：

- **受信者( Trustee )**

  该 ACE 适用的用户或组的 SID，例如组 *COHOVINES\Domain Admins* 的 SID。

- **ACE 类型( ACE Type )**

  确定该 ACE 是*允许*还是*拒绝*。

- **对象类型( Object Type )**

  该 ACE 适用的属性或对象类的 `schemaIDGUID`，或者该 ACE 适用的属性集、验证写入或扩展权限的 `rightsGuid`（例如 `member` 属性、`Personal Information` 属性集、`Change Password` 扩展权限或 `user` 对象）。对于“删除”或“创建子对象”权限，`objectType` 应配置为所委派对象类的 `schemaIDGUID`。

- **继承对象类型( Inherited Object Type )**

  当指定了属性、属性集或验证权限时，或者当该 ACE 被继承时，该 ACE 所适用对象类型的 `schemaIDGUID`——例如 `user` 对象。

- **访问掩码( Access Mask )**

  一个位标志，用于描述访问类型，例如读取( Read )、写入( Write )、列出( List )、创建( Create )、删除( Delete )、控制访问( Control Access )等。有关更多详细信息，请参阅表 16-1。

- **标志( Flags )**

  标志实际上有两个不同的字段。这些标志用于指定继承设置，例如 ACE 已被继承、允许继承 ACE、ACE 不可继承等。



表 16-1. ACE 属性的内容

| 属性名称              | 要存储的示例值                                               |
| --------------------- | ------------------------------------------------------------ |
| `Trustee`             | 指定要授予权限的安全主体。                                   |
| `AccessMask`          | 授予对特定属性的写入访问权限。                               |
| `AceType`             | 这是一个允许权限。                                           |
| `AceFlags`            | 该权限仅为继承所得，不适用于此对象。子对象会继承此 ACE。     |
| `Flags`               | 同时设置了 `ObjectType` 和 `InheritedObjectType`。           |
| `ObjectType`          | 这是 `description` 属性的 `schemaIDGUID`。                    |
| `InheritedObjectType` | 这是 `User` 类的 `schemaIDGUID`。                             |

活动目录( Active Directory )中授予的每一项权限都基于这些访问控制条目( Access Control Entry ,ACE )结构。只有对对象拥有相应权限的用户才能看到这些对象和属性。任何属性如果没有一个 ACE 明确授予某个受托者所请求的访问权限,就会被隐式拒绝。安全描述符还允许管理员通过拒绝 ACE 来明确拒绝访问,但除非你试图覆盖另一个授予访问权限的更通用 ACE ,否则并不需要这样做。

这种权限机制允许不同用户或用户组对某个对象拥有完全不同且非常细粒度的访问权限。例如,所有用户可能都被授予对电话号码和电子邮件属性的读取权限,但只有一部分用户拥有修改描述的权限。

#### 属性集( Property Sets )、验证写入( Validated Writes )与扩展权限( Extended Rights )

微软引入了若干 NTFS 访问控制列表( Access Control List ,ACL )中并不存在的全新“工具”。这些工具称为属性集、验证写入和扩展权限。无需将 `schemaIDGUID` 插入访问控制项( Access Control Entry ,ACE )的“对象类型”( Object Type )字段,而是可以插入属性集、验证写入或扩展权限对象的 `rightsGuid` 属性。这些对象全部存储在配置容器( Configuration container )的 cn=`extended-rights` 子容器中。

> **注意**：属性集( Property Sets )、验证写入( Validated Writes )和扩展权限( Extended Rights )都存储为 `controlAccessRight` 对象。通过任何可查看对象所有属性值的实用工具（例如 LDP 或 ADSI Edit），查看该对象的 `validAccesses` 属性，即可确定它们具体属于哪种 `controlAccessRight` 类型。

*属性集* 的值为 `48`，验证写入的值为 `8`，扩展权限的值为 `256`。有关详细信息，请参阅[此网站](http://bit.ly/YEGdJg)。

*属性集* 是可在单个权限访问控制项( Access Control Entry ,ACE )中引用的属性集合。其最大优势在于，你可以将一个 ACE 分配给一个安全描述符( Security Descriptor ,SD )，并让它授予对 5 个、10 个、20 个或更多属性的访问权限。SD 大小的节省应显而易见：一个可替代 20 个不同 ACE 的 ACE 就是很好的数据缩减比。默认林中包含若干预定义属性集；其中一些包括个人信息( Personal Information )、公共信息( Public Information )、Web 信息( Web Information )和账户限制( Account Restrictions )。你也可以根据需要添加自己的属性集。Exchange 会添加若干属性集以简化委派，包括 Exchange-Personal-Information 和 Exchange-Information。

尽管属性集在保护目录方面是一大助力，且其方式比原本可实现的更简单，但这种实现存在一个重大缺陷。*一个属性只能属于单个属性集*。遗憾的是，许多基础架构属性已包含在现有属性集中；虽然其中大多数可以成功地从这些属性集中删除，或移动到其他属性集，但你永远无法确定这样做不会破坏某个应用程序。通常，更安全的做法是坚持管理由你添加到目录中的自定义属性所组成的属性集。

*验证写入* 是经过额外验证的写入。你无法修改验证写入，也无法创建自己的验证写入；随 AD 提供的验证写入就是可用内容。目前定义的验证写入仅有：

- 对服务主体名称( Service Principal Name ,SPN )的验证写入
- 对 DNS 主机名( DNS Host Name )的验证写入
- 添加/移除自身作为成员

*扩展权限( Extended Rights )*是用于委派特殊操作(如更改密码或重置密码)的机制。虽然可以向目录添加其他扩展权限,但无法创建由目录强制实施的扩展权限。你创建的任何新扩展权限都只是附加权限,可用于控制你编写的、知道如何使用这些权限的应用程序。这些扩展权限的主要用途通常是:借助“重置密码( Reset Password )”扩展权限,将针对用户对象设置密码的权限委派给管理员。

#### 继承权限( Inherited Permissions )与显式权限( Explicit Permissions )

许多 Windows 管理员习惯引用这句箴言:“拒绝优先于一切。”幸运的是(或者说不幸的是,具体取决于你想实现的目标),Active Directory 中的访问控制列表( Access Control List ,ACL)要比这稍复杂一些。你需要特别了解继承权限与显式权限之间的区别。*显式权限*是直接应用到对象上的权限。*继承权限*是在对象上方的目录树某一级别应用,并“向下流动”到该对象及其子对象的权限。在处理对象上的继承权限和显式权限时,*拒绝并不一定优先于允许*。

要理解一组继承和显式访问控制项( Access Control Entry ,ACE)会产生何种访问权限,按步骤来看这些规则最容易:

1. 拒绝 ACE 会覆盖与之类型相同(同为继承或同为显式)且在目录树中应用点相同的允许 ACE。
2. 显式 ACE 会覆盖继承 ACE。
3. 继承 ACE 具有层次性(例如,应用于某容器的继承拒绝 ACE,会被同一树中应用于嵌套在该容器下方的容器的继承允许 ACE 覆盖)。

最简单地说,最靠近对象的 ACE 将决定该对象的访问权限。如果你使用继承拒绝来阻止访问某个组织单位( Organizational Unit ,OU)中对象的某些属性,而该拒绝未生效,请查找在该分支更靠下位置应用的继承允许权限,或在对象自身上应用的显式允许权限。

#### 默认安全描述符

架构中定义的每个对象都具有`defaultSecurityDescriptor`属性。此属性以*安全描述符定义语言*（SDDL）格式定义了对象的默认安全描述符（SD）。当创建对象时未指定SD，系统将应用此默认值。在Active Directory中，这些默认权限相当广泛，且完全由显式访问控制条目（ACEs）组成，因此它们会覆盖任何继承的拒绝权限（这使得拒绝对特定属性的访问比预期更具挑战性）。用户对象的默认安全描述符定义的DACL列于表16-2。

表16-2. 用户对象类默认安全描述符的DACL

| 受托人                                      | 权限                                                         |
| ------------------------------------------ | ------------------------------------------------------------ |
| Domain\Domain Admins                       | 完全控制                                                     |
| Builtin\Account Operators                  | 完全控制                                                     |
| System                                     | 完全控制                                                     |
| Self                                       | 读取权限列出内容读取属性列表对象读取/写入个人信息读取/写入电话和邮件选项读取/写入Web信息更改密码发送为接收为 |
| Authenticated Users                        | 读取权限读取一般信息读取公共信息读取个人信息读取Web信息       |
| Domain\RAS and IAS Servers                 | 读取账户限制读取登录信息读取组成员身份读取远程访问信息       |
| Domain\Cert Publishers                     | 读取/写入userCertificate                                     |
| Builtin\Windows Authorization Access Group | 读取tokenGroupsGlobalAndUniversal                            |
| Builtin\Terminal Server License Servers    | 读取/写入terminalServer                                      |
| Everyone                                   | 更改密码                                                     |

#### 权限锁定( Permission Lockdown )

从表 16-2可以看出，在默认活动目录( Active Directory )安装中，经过身份验证的用户( Authenticated Users )组成员可以访问相当多的信息。如果将经过身份验证的用户添加到 Windows 2000 之前版本兼容访问( Pre-Windows 2000 Compatible Access )组，则还可获得更多信息，因为这样他们就能查看组、用户以及 `inetOrgPerson` 对象的所有属性。开放访问这些信息对许多公司来说都是一个痛点，它们不希望员工能获得这么多信息；也许它们想限制对员工电话号码、地址或其他个人信息的访问。

要移除查看这些信息的能力可能很难做到，尤其是对于那些通过显式属性集访问控制项( Access Control Entry ,ACE)授予的项。此外，所做的任何修改都需要经过全面测试，以确保不会破坏任何业务线应用程序。Microsoft Exchange 对权限锁定尤其敏感；如果取消经过身份验证的用户组对某些属性的访问权限，则可能需要将权限重新授予 Exchange 服务器。ADSI 是另一种常用工具，对默认权限的更改非常敏感。如果已移除假定的权限，你可能会发现 ADSI 调用会失败并出现难以解释的错误。

> **警告**：你无法永久地将目录锁定到让域管理员( Domain Admins )无法访问的程度。该组中的任何人在任何时候都可以取得任何对象的所有权(如果他们尚未拥有该所有权)，并重写安全描述符( Security Descriptor )，以向域管理员或任何其他安全主体( Security Principal )授予访问权限。你的林( Forest )中应只有极少数的域管理员。我们通常建议总数控制在五个或更少，*即使对于规模最大的组织也是如此*。

一旦决定继续执行锁定，下一步就是确定如何实现。具体“如何”实施以及由此产生的工作量和影响，完全取决于所涉及的属性以及访问权限的授予方式。

迄今为止，最简单的情形是访问权限通过继承授予。如果只是这一个属性，你可以移除继承的授予；也可以为希望保护的一个或多个属性添加继承的拒绝。你可能想要移除的继承权限的一个示例是对 `employeeID` 属性的读取访问权限。经过身份验证的用户( Authenticated Users )对 `employeeID` 的读取访问权限是通过一条应用于域根的访问控制项( Access Control Entry ,ACE )授予的，该 ACE 向 Windows 2000 之前兼容访问( Pre-Windows 2000 Compatible Access )组授予读取用户所有属性的权限。在域根或其他容器( Container )上为经过身份验证的用户插入可继承的拒绝读取 ACE，将有效阻止继承的授予对该属性的读取访问权限。如果需要，可以在拒绝 ACE 下方的树( Tree )中更深处重新添加读取访问权限，方法是使用额外的显式授予读取访问 ACE 或继承的授予读取访问 ACE。

如果访问权限是通过显式 ACE 授予的，则锁定会复杂得多，甚至可能困难到不可行。有多种机制可用于锁定显式授予的访问权限：

- 如果访问权限是通过属性集( Property Set )授予的，请修改所涉属性集的成员身份。
- 更改架构( Schema )中对象类定义( Object Class Definition )的默认安全设置，以删除针对经过身份验证的用户( Authenticated Users )的显式权限，或者为特定属性添加拒绝访问控制项( Access Control Entry ,ACE )，然后对目录中存在的该对象的每个实例“修复”访问控制列表( Access Control List ,ACL )。任何新对象都将使用新的安全描述符( Security Descriptor )创建。
- 从目录中该对象的每个实例中删除显式授予 ACE。每当创建新的对象实例，或者有人将任何对象的 ACL 重置为架构默认值时，都需要持续执行此操作。
- 在目录中该对象的每个实例上添加显式拒绝 ACE。与上一解决方案类似，这需要“修复”已创建或已重置为架构默认值的新对象实例。
- 您或许可以使用机密性位( Confidentiality Bit )。此功能将在下一节中介绍。

#### 机密性位( Confidentiality Bit )

在客户与前面概述的目录锁定难题周旋了五年之后，Microsoft 添加了一项称为“机密属性( Confidential Attributes )”的功能。作为该功能的一部分，新增了一个名为*机密性位*的 `searchFlags` 位。它是位 `7`，值为 `128`。启用该位后，该属性会被视为机密属性。只有对对象上的该属性同时拥有读取属性( Read Property )权限*和*控制访问( Control Access )权限的用户才能查看该属性。这意味着，任何拥有完全控制( Full Control )、所有扩展权限( All Extended Rights )（对象的控制访问），或针对该特定属性的控制访问的用户都可以查看。假设采用默认权限，这意味着访问权限将授予：

- Builtin\Administrators（继承的完全控制）
- Builtin\Account Operators（显式完全控制）
- NT Authority\System（显式完全控制）
- Domain\Domain Admins（显式完全控制）
- Domain\Enterprise Admins（继承的控制访问）
- Object Creator\Owner（显式的控制访问）

如你所见，对于前面提到的带显式权限的问题，这似乎提供了一个很棒的新解决方案。理论上，你只需将任何有问题的属性标记为机密，普通用户便无法再看到它们。这是一个很好的方案，但仍有一个挑战：你不能对类别 1 属性( Category 1 Attributes )（更通用的叫法是*基础架构属性( Base-Schema Attributes )*）设置机密性位。因此，公司可能试图锁定的许多属性无法通过此功能进行锁定。

遗憾的是，目前没有一种简单的机制可通过 GUI 工具授予控制访问权限。可用的最佳工具是 LDP。ADUC 和 ADSI Edit 中的 ACL 编辑器仅支持授予对某个对象所有属性的控制访问（通过“所有扩展权限”权限），而不支持仅针对单个属性。有关使用 LDP 管理 ACL 的详细信息，请参阅第 20 章。

#### 防止对象被意外删除

Active Directory 管理员经常面临的一个问题是，某个对象或整个组织单位(Organizational Unit, OU)树被意外删除。这通常是因为在使用 Active Directory 用户和计算机(Active Directory Users and Computers, ADUC)工具时犯下的疏忽所致。随后的恢复过程通常涉及权威还原和业务停机。较新版本的 ADUC 在微软管理控制台(Microsoft Management Console, MMC)中包含一个名为“防止对象被意外删除”的复选框。实际上，该复选框只是添加一个访问控制项(Access Control Entry, ACE)到应用该复选框的对象的访问控制列表(Access Control List, ACL)，并阻止删除。因此，由于无法删除其父对象，这也会阻止删除整个树。要删除该对象或树，管理员必须先取消选中该复选框，或手动删除该 ACE。

要看到“防止对象被意外删除”复选框，必须先在 ADUC 中选择“查看” → “高级功能”。完成此操作后，可以右键单击目录中的对象，选择“属性”，然后访问“对象”选项卡。图 16-2 显示了在 ADUC 中保护 People OU 的情况，图 16-3 显示了使用 Active Directory 管理中心(Active Directory Administrative Center, ADAC)保护 People OU 的情况。




![Protecting the People OU with ADUC](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663504.webp)


图 16-2. 使用 ADUC 保护 People OU




![Protecting the People OU with ADAC](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663505.webp)


图 16-3. 使用 ADAC 保护 People OU

如果尝试删除受意外删除保护的对象，将收到与 图 16-4 中类似的错误。要删除该对象，必须返回属性，并取消选中“防止对象被意外删除”(在 ADAC 中为“防止意外删除”)复选框。




![Error message when trying to delete a protected object](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663506.webp)


图 16-4. 尝试删除受保护对象时的错误消息

图 16-5 显示了为保护 People OU 而添加到其 ACL 的 ACE。请注意，Everyone 这一众所周知的安全主体已被拒绝删除该对象或子树的权限。




![ACE created by protecting the People OU](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663507.webp)


图 16-5. 保护 People OU 时创建的 ACE

### 16.2. 使用 GUI 检查权限

要访问任何对象的权限，请选择"Active Directory 用户和计算机"MMC 管理单元，然后右键单击该对象。从下拉菜单中选择"属性"，并在显示的属性窗口中选择"安全"选项卡。

> **注意**：若要使“安全”选项卡可见,需要选择“查看”→“高级功能”。重新打开想要为其分配权限的对象的属性窗口后,即可看到“安全”选项卡。

图 16-6所示的窗口是您接触权限设置的起点。顶部区域列出了当前所查看属性对象的全部授权组和用户的完整清单。清单下方的“权限”部分显示了所选用户或组在各项常规权限上的允许与拒绝情况。所列出的常规权限仅涵盖那些被认为最常设置的权限。每个常规权限只是一个总括性术语,其背后代表着一组复杂的、实际生效的具体权限。例如,名为“读取”的常规权限实际对应的是“读取所有属性”和“列出内容”等具体权限,稍后将会说明。




![Security properties of an object](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663508.webp)


图 16-6. 对象的安全属性

虽然图 16-7所示的高级安全设置窗口比前一窗口提供的信息仅略多一些,但它具有重要作用:它是通往某些最底层、最细粒度权限的入口。“高级”窗口允许您查看图 16-6中所设置的全局权限,以及可能为每个对象设置的高级权限的简要摘要。虽然“主体”和“访问”列实际上与图 16-6中的信息重复,但“类型”字段显示了此用户或组对该对象的权限是允许还是拒绝。如果某个组既有允许权限又有拒绝权限,则此窗口中会记录两条条目。“继承自”列允许您查看该权限是从哪个对象继承而来(如果有的话)。“应用到”列则清晰地指示了权限的应用范围:可以是仅此对象、此对象及其所有子对象,或仅某个单独属性(例如用户对象的 `telephoneNumber` 属性)。




![Advanced security Settings for an object](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663509.webp)


图 16-7. 对象的高级安全设置

> **注意**：权限对话框包含大量信息，且通常尺寸过小，难以舒适地查看其中的内容。这使得查看权限变得颇为费力，因为你不得不频繁调整各列宽度或在对话框中来回滚动。遗憾的是，我们无法修改这些对话框以更好地展示其包含的信息。

现在，你有两种方式查看原子权限。你可以点击“添加”，弹出一个窗口，允许你向已设置权限的用户或组中添加新的用户或组。另一种方式是，选中一个现有的用户或组，然后点击“编辑”按钮。无论是选中用户或组，还是通过弹出窗口添加，接下来你将看到的是权限项( Permission Entry ,PE)窗口，如图16-8所示。

![Permission Entry for an object](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663510.webp)

图16-8. 对象的权限项

> **注意**：在你完全清楚自己在权限方面要做什么之前，我们建议你先用一个测试林来试验权限设置。最不希望发生的事情，就是因为对某个内置组或用户犯了一个简单的错误，结果把自己挡在目录树之外。如果你创建两个测试用户和三个测试组，让每个用户分别属于一个独立的组，再把这两个用户都加入第三个组，就搭建起了一个测试系统的基础。

对象名称显示在权限编辑器窗口的标题中，拥有权限的用户或组名称则醒目地显示在窗口顶部的字段里。随后，通过列中的条目为该用户或组授予允许或拒绝的权限。窗口中的条目是相对的，会随“应用于”标题下下拉列表中所选的条目而变化。从这个窗口并不能一眼看出下拉框实际上能有多长。这一点在图 16-9 中得到了很好的展示。如果你看一下滚动条，就能大致了解当前还有多少项没有显示出来。

要在权限编辑器窗口中设置权限，先选择要应用该权限的位置，然后选中相应的“允许”和“拒绝”复选框，完成后单击“确定”。由于 Microsoft 没有提供“应用”按钮，你无法先为一组权限指定某个应用区域、单击“应用”，再重复这一过程，直到完成对该用户和组的全部设置。你必须单击“确定”，这意味着窗口会关闭，随后你又得再次单击“添加”，如此反复。如果你要根据一组预先准备好的设计方案实施多项更改，这确实是个令人厌烦的问题；但只要选择用图形用户界面( Graphical User Interface ,GUI )来设置权限，就只能忍受它。




![Permission Entry window showing the large number of targets to which permissions can be applied](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663511.webp)


图 16-9. “权限条目”窗口显示了可以应用权限的大量目标对象

#### 还原为默认权限

在图 16-7中，您可能已经注意到屏幕底部的“还原默认值( Restore defaults )”按钮。此按钮允许您将当前权限集还原为默认值，这些默认值由对象的 `objectClass` 的架构( Schema )定义。如果对未修改过权限的对象点击“还原默认值”，您可能会注意到列表仍然会发生变化。如果您仔细观察，会发现被移除的是继承权限( Inherited permissions )。这是因为继承权限并未定义为对象默认安全( Default security )的一部分。即使您随后点击“确定”以应用权限，只要未按下“禁用继承( Disable inheritance )”按钮，继承权限仍将适用。能够应用默认权限( Default permissions )是一项有用的功能，尤其对于试图确定默认安装( Default installation )后发生了哪些更改的管理员而言。

#### 查看用户或组的有效权限

有效访问( Effective Access )选项卡(在某些 Windows 版本中也称为有效权限( Effective Permissions ))可从对象的高级安全设置( Advanced Security Settings )界面访问(在 Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC)中查看对象属性、选择“安全”选项卡并单击“高级”按钮即可打开)。通过此界面，你可以选择一个用户或组，并在考虑组成员身份和权限继承的情况下，确定其对对象的有效(或实际)访问权限。图 16-10显示了经过身份验证的用户( Authenticated Users )对 People 组织单位( Organizational Unit ,OU)对象的有效权限。如你所见，经过身份验证的用户拥有“列出内容”、“读取所有属性”和“读取权限”权限。除非已阻止继承，否则林中的所有对象都将继承这些权限。正如你可能想到的，这是一项重要功能，可大大简化权限问题的故障排除。不过，需要注意一些限制。

![Viewing the effective permissions for Authenticated Users on the People OU object](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663512.webp)

图 16-10. 查看经过身份验证的用户( Authenticated Users )对 People OU 对象的有效权限

有效权限工具仅提供用户或组实际权限的近似值，并未考虑许多众所周知的安全主体( Well-Known Security Principal )，例如匿名登录( Anonymous Logon )和网络( Network )。另一个需要注意的潜在问题是，运行有效权限工具的用户必须有权读取目标用户或组的组成员身份。默认情况下，经过身份验证的用户组具有此权限。

#### 使用控制委派向导( Delegation of Control Wizard )

为了帮助委派 Active Directory 中对象的权限，Active Directory 用户和计算机( Active Directory Users and Computers )自带一个称为*控制委派向导*的*向导*。它旨在允许管理员将某些类型对象的管理委派给组织中的关键人员或组。通过右键单击树中的几乎任何容器( Container )，然后从弹出菜单中选择该向导即可启动它。默认情况下，该向导对 Builtin 和 LostAndFound 这两个容器不起作用。

该向导仅适用于需要明确向容器下的一个或多个对象类型应用常规允许权限( Allow Permissions )的情况。如果要指定拒绝权限( Deny Permissions )(它不支持此操作)、删除以前委派的控制、委派对单个对象的控制，或者对树的分支应用特殊权限，则它并不适用。该向导的最大优势在于，能够设置权限并同时将其应用于多个用户和组。我们使用该向导来设置这类权限，但频率远低于使用标准图形用户界面( Graphical User Interface ,GUI )，因为它的功能要有限得多。使用 Active Directory 服务接口( Active Directory Service Interfaces ,ADSI )编写脚本也提供了一种更适应管理员自身需求的解决方案。

该向导提供多个屏幕供你导航浏览。第一个是欢迎屏幕，说明该向导的作用。第二个是对象选取器( Object Picker )，用于选择要委派给哪些用户或组。第三个屏幕询问你希望为该容器中的哪项任务委派控制。图 16-11 显示了此窗口。




![Delegation of Control wizard—task selection](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663513.webp)


图 16-11. 控制委派向导——任务选择

默认选项是为特定任务委派控制，并且有多项可供选择。由于列表在图 16-11中滚出了屏幕，我们在此列出它们：

- 创建、删除和管理用户账户
- 重置用户密码,并强制用户在下次登录时更改密码
- 读取所有用户信息
- 修改组的成员身份
- 将计算机加入域
- 管理组策略链接
- 生成策略结果集( Resultant Set of Policy ,RSoP )(规划)
- 生成策略结果集(日志记录)
- 创建、删除和管理 inetOrgPerson 账户
- 重置 inetOrgPerson 密码,并强制用户在下次登录时更改密码
- 读取所有 inetOrgPerson 信息

如果选中"自定义"单选按钮并单击"下一步",将打开一个额外的页面,让你可以指定单个对象。图 16-12 展示了这一页面。




![Delegation of Control wizard—choosing objects to delegate](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663514.webp)


图 16-12. 控制委派向导( Delegation of Control Wizard )——选择要委派的对象

如果希望将某些权限委派给特定容器或分支中的计算机对象或用户对象,可以在这里完成。向导的下一个屏幕允许你指定要为所选用户/组分配哪些权限。图 16-13 展示了该屏幕。




![Delegation of Control wizard—access rights selection](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663515.webp)


图 16-13. 控制委派向导——访问权限选择

该窗口最初打开时,只有第一个复选框处于选中状态。随着你逐个选中其他复选框,可委派的具体权限列表会变得非常庞大,因为它囊括了所有可能委派的权限。最后,向导的最后一个屏幕会汇总前面的各项选择,用户可以返回、取消,或者完成并授予权限。

然而，就像对象的"安全"属性中列出的权限（参见图 16-6）会发生变化一样，访问权限框中列出的权限也会根据权限所应用到的对象而有所不同。要很好地演示这一点，可以打开任一用户的安全属性，滚动浏览显示的权限列表。接着，在任一容器上打开该向导，选择"创建自定义任务委派"（参见图 16-11 所示的界面），并仅选择用户对象（参见图 16-12）。随后，图 16-13 所示的界面应显示与图 16-6 中界面相同的权限列表。这合乎情理——单个用户可用的权限应当与所有用户可用的权限相同——不过，能亲眼看到这种对应关系，也算是件好事。

### 16.3. 使用图形界面检查审计

检查审计条目与查看权限条目几乎完全相同。如果你回到图 16-6所示的界面，并点击“审计”选项卡，将显示一个类似于图 16-14的界面。




![Advanced Security Settings window showing auditing entries](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663516.webp)


图 16-14. 显示审计条目的高级安全设置窗口

此窗口显示了已在对象上定义的审计条目( Auditing Entry ,AE )列表。不过，从这里查看它们帮助不大，因为详细信息有限。因此，正如你对权限所做的那样，你可以选择一个条目，点击“编辑”按钮，深入查看并查看单个审计条目本身。

图 16-15显示了正在被审计的成功和失败项目。




![Auditing entry for an object’s properties](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663517.webp)


图 16-15. 对象属性的审计条目

### 16.4. 设计权限方案( Permissions Schemes )

基于对多种域结构设计的经验，我们总结出了一系列规则或指南，帮助您有效构建权限设计流程。其理念在于：遵循这些规则设计权限方案，您将更有可能以最少的工作量创建出具有全局适用性的设计。

#### 权限设计的五条黄金法则

这份规则清单并非详尽无遗；我们相信您能想到其他规则。但是，如果这些规则能激发您的创造力并帮助您更有效地进行设计，那么它们就达到了目的。

规则如下：

1. 尽可能将对象权限分配给包含用户的安全组( Security Groups )，而非单个用户。
2. 设计组权限时，应尽量减少重复。
3. 尽可能全局管理权限。
4. 允许继承：不要阻止树中某些部分继承权限。
5. 记录您对树所做的每一次异常更改，尤其是当您阻止了某些部分继承权限或为特定用户应用了特殊权限时。

让我们更详细地研究这些规则。

##### 规则 1：尽可能将权限应用于组

默认情况下，您应使用组来管理用户权限。简而言之，当您需要为多个用户设置特定权限时，这条规则就很有意义。

我们并非提倡使用一个或两个组，正如我们将在下一节关于如何规划权限的内容中更详细地解释的那样。我们提倡的是，无论您选择以何种方式实现组权限，都应将用户添加到组并将权限应用于组，即使该组最初只包含一个用户。这样可以消除组织对某个特定帐户的依赖。

我们多次看到，在有些组织中，拥有大量针对各种对象权限的单个用户突然离职或更改角色。新管理员随后不得不介入，梳理该帐户上各不相同的权限设置。我们甚至见过一位管理员，面对刚离职管理员的帐户中一团乱麻的权限设置，感到非常苦恼，于是删除了自己的帐户，并重命名了离职用户的帐户，只为不必厘清混乱就能获得正确的权限集！如果旧管理员曾是（比如）五个不同组的成员，每个组都具有相关权限，那么新管理员只需用自己的新帐户替换旧帐户的组成员身份即可。这是一种简单得多的方法，我们确信，上述常识对系统管理员来说并不新鲜。

##### 规则 2：设计组权限( Group Permission )，使重复降到最低

创建具有简单、独立权限集( Permission Set )的组，远比创建多个权限重叠的组更合理。如果你决定，某些用户需要比如创建和修改权限，而另一些用户需要修改和删除权限，第三组用户只需要修改权限，那么创建三个单独的组，分别具有创建、删除和修改权限，要比创建上述权限集的三个组合理得多。让我们考虑一个例子。假设我们要创建三个组，分别名为 *Create and Modify*、*Modify and Delete* 和 *Modify*。现在假设我们向每个组添加了 10 个用户。如果这些组唯一会发生的修改只是偶尔的成员身份变更，那么该方案足够适用。然而，假设（正如每个大型组织都会发生的那样）权限要求随时间发生变化。如果 *Create and Modify* 的成员 Dave Peace 现在需要删除权限，我们该怎么办？我们是否将 Dave 的账户作为特例，仅向其账户添加删除权限？可以说，这是最简单的解决方案，但根据规则 1，我们确实应该创建一个组来管理该权限集。我们是创建一个 *Delete* 组并将 Dave 的账户添加到其中，还是创建一个 *Create, Modify, and Delete* 组，并将其成员身份从 *Create and Modify* 移到新组？两种方案都有效。

假设我们采用前者，创建一个 *Delete* 组，并将 Dave 添加为该组的成员。后来情况又变了，Mark Newell 加入组织。Mark 需要全部三种权限，因此我们将其添加到 *Create and Modify*——但还要将他添加到 *Modify and Delete*，还是仅添加到 *Delete*？无论采用哪种方式，我们现在都可能产生混淆。每当我们必须检查哪些成员可以修改和删除时，都必须检查三个组，而不是一个组。

如果我们采用第二种方法，并选择创建 *Create, Modify, and Delete* 组而不是 *Delete* 组，那么当 Mark 加入时，我们只需将他添加到 *Modify and Delete* 组，这样似乎就能正常工作。现在假设 Paul Burke 从另一个团队调来，并且只需要创建权限，因此创建了一个 *Create* 组，并将他的帐户添加到该组。后来，又有三人加入 *Create* 组，但 Paul 现在需要创建和删除权限，因此创建了 *Create and Delete* 组，并将他移到该组。现在我们有六个组：*Create*、*Modify*、*Create and Delete*、*Create and Modify*、*Modify and Delete* 和 *Create, Modify, and Delete*。遗憾的是，如果我们需要检查谁拥有创建和修改权限，就必须检查三个组：*Create*、*Modify* 和 *Create and Modify*。

所需访问控制项( Access Control Entry ,ACE)和组数量最少的解决方案是，为授予的每一项权限分别创建一个组：*Create*、*Modify* 和 *Delete*。然后可以根据需要将用户添加到这些组中。如果你更喜欢基于“角色”的方法，可以创建基于角色的组，例如 *Create and Modify* 及其他组，并将它们嵌套到目录中拥有实际权限的 *Create* 和 *Modify* 组中。

这个示例非常牵强。不过，我们希望它能说明：只要有些用户需要对某个对象或属性拥有各项独立权限，而另一些用户需要这些权限的组合，就会出现重复。正是出于这个原因，我们建议为你需要设置的最细粒度基础权限分别创建组。请牢记未来可能的增强和角色重新定义，因为通常你不会希望每当出现新需求时，就随意更改目录中的权限。

如果有些用户始终需要读取、列出和创建权限，但需要的删除和修改权限组合各不相同，那么再创建三个组——分别为读取、列出和创建各建一个组——可能就不合理。相反，你可以创建一个组，为其分配读取、列出和创建权限；再创建一个用于删除的组，以及一个用于修改的组。然后，你可以利用多个组成员身份，根据需要组合这些组权限。当然，如果以后你需要仅授予读取或创建权限，最终还是要将这些权限拆分出来。请尽量提前考虑。

最重要的一点是，我们讨论的是尽量减少并简化应用于目录的访问控制项( Access Control Entry ,ACE )数量。如果你需要为某个对象统一授予创建、修改和删除权限，那么可能并不需要创建三个组。但如果你认为需求很容易发生变化，也不要完全排除这种做法。

如果在创建了具有多个权限的组之后，你发现现在需要具有单独权限的组，那么随时可以创建更小的组并迁移用户。Active Directory 足够灵活，允许你这样做，但事后清理可能相当繁琐，并且必须以缓慢、细致的方式进行，以免影响用户。

##### 规则 3：仅在绝对必要时管理高级权限

（请注意，这里说的是“权限”而不是“审核”。审核条目只能从“高级”选项卡访问，因此此规则对审核条目不太适用。）

每当右键单击某个对象以查看其属性时，出现的安全属性窗口( Security Properties Window )上都有一个“高级”按钮。这在“使用 GUI 检查权限”一节的图 16-6中展示过（第 451 页）。安全属性窗口本身通常提供以下作为常规权限( General Permissions )的允许和拒绝选项：

- 完全控制( Full Control )
- 读取( Read )
- 写入( Write )
- 创建所有子对象( Create All Child Objects )
- 删除所有子对象( Delete All Child Objects )

不过，常规权限并不限于这五项，实际上它们会随着你查看的对象而变化。例如，任何用户对象的安全属性都会显示额外的常规权限，如重置密码( Reset Password )、修改 Web 信息( Modify Web Information )和发送为( Send As )。虽然这些常规权限对用户对象有意义，但它们并非都适用于其他对象。此规则建议尽可能经常从安全属性窗口管理对象的权限。只有当你希望针对对象的某个方面而不是整个对象允许或拒绝某项权限时，才使用“高级”按钮。例如，操作读取或修改用户对象电话号码的权限，而不是整个帐户详细信息。

虽然管理对象和属性的原子权限( Atomic Permissions )并没有错，但从更高级别管理权限要容易得多。管理员可能希望设置的主要权限放在这里正是为此目的，以便用户和组可以轻松管理目录树，而不必担心大量单个属性。

如果你选择将权限划分得非常精细，则应考虑在命令行中使用 *DSACLS* 来设置权限。*DSACLS* 能更好地显示所有权限，并且在某些情况下，对于已应用的访问控制项( Access Control Entry ,ACE )，它比 Active Directory 用户和计算机( Active Directory Users and Computers ,ADUC )处理得更智能。最后，*DSACLS* 可用于脚本，以获得一致的结果。

##### 规则 4:允许继承,不要阻止域树( Domain Tree )中的某些部分继承权限

如果为某个组或用户授予或拒绝针对容器中某一类型全部对象的权限,默认情况下,这些权限会以递归方式应用到树中所有子容器内该类型的所有对象。阻止继承是可以做到的,但我们建议保留继承(即默认设置),仅在确有充分理由时才针对单个分支进行保护。原因很简单:如果指定子对象不从父对象继承权限,就会给 Active Directory 环境增添额外的复杂性。在每个默认域中都能找到若干阻止继承的示例。你只需查看任意一个管理 ID,或者逐层展开到 System 容器,再进入 Policies 容器,查看其中任意一个 `groupPolicyContainer` 对象即可。

出于类似的安全考虑,`groupPolicyContainer` 对象同样受到了保护。如第 11 章所述,这些对象包含有关应用于域的安全策略( Security Policy )的信息。Microsoft 有充分理由决定保护这些对象,使其免遭目录中更高层级权限委派( Permission Delegation )的意外影响。一般来说,你无需直接操作这些对象,因此即便管理 Active Directory 多年也可能从未注意到它们;为保护它们而涉及的复杂性不会直接影响到你。

归根结底,将对象或树中的某些部分保护起来以免继承并无不妥。但要切记,每这么做一次,都可能为自己和其他管理员带来更多工作量和潜在的困惑。作为管理员,你应在日志中记录这些更改,以便在需要时能够轻松查阅这些特殊情况。

##### 规则 5:记录变更日志

这听起来可能显而易见,但令人惊讶的是,许多管理员都忽略了这样一个简单要求。简而言之,明智的做法始终是记录你对默认安装所做的自定义变更,以便你和他人日后可以参考。有时你可能无法在场,而又需要这类信息。以下列表展示了基本 Active Directory ACL 日志的相关字段:

- 对象的唯一名称或对象在树中的 LDAP 位置
- 正在修改的对象类
- 正在修改的对象或属性
- 被授予权限的用户或组
- 正在授予的权限
- 关于进行此变更原因的备注

除 ACL 变更之外,还有一些值得记录的额外项目,包括架构默认安全描述符变更、属性集修改、属性索引变更以及属性机密性变更。

现在让我们来看看如何在你自己的设计中实践这些规则。

#### 如何规划权限

在 Active Directory 用户和计算机( Active Directory Users and Computers )中，管理员可能需要在其组织中实现许多权限集( permission sets )。例如：

- 一组集中式团队，每个团队负责某些区域。用户可以属于多个团队：账户修改者、打印机管理员、计算机账户管理员、发布管理员等。
- 域( Domain )下每个单独的主要组织单位( Organizational Unit ,OU )的管理员。
- 域下每个单独的主要组织单位的管理员，并且该管理员能够委派树中较低层级的组织单位的职责。

虽然我们可以逐一检查每种情况并展示如何为每种情况设计权限，但每个组织各不相同。因此，最好尝试展示我们认为在为所有类型的组织设计 Active

现在,请通读你的 Active Directory 设计,开始填充允许( Allow )表和拒绝( Deny )表。第一轮应专注于设计一份全面的方案,列出你认为需要的所有权限( Permission )。打印若干份表格副本。当你手头有了清单后,就可以开始将相同的权限合并成组。你很可能需要经过多轮设计迭代,直到得到一份精简后令你满意的清单。在设计过程中,你会逐渐识别出需要应用权限的用户组( User Group )。设计组时,有两种选择,如前文规则 2 所述。你可以创建一个既应用权限又包含用户的单一组,也可以创建两个组:一个用于应用权限,另一个用于存放用户,并将后者嵌套到前者中。

决定采用单组还是双组并非总是易事。我们倾向于尽可能使用单组,除非需要额外的灵活性,或者有许多权限要分配给多个组。为了帮助你更好地理解这一决策,表 16-3 中列出了一些你可能考虑其中一种方案的理由。

表 16-3. 何时考虑用户组与权限组( Permission Group )或组合组( Combined Group )

| 符合以下情况时，应考虑使用一个组 | 符合以下情况时，应考虑使用两个组 |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| 你希望将组的数量保持在最低限度。          | 你希望获得更大的灵活性。使用一个组来应用权限，使用另一个组来容纳用户，意味着你始终能够以最小的麻烦来管理系统。 |
| 你只有一个较小或简单的树，在其中追踪问题相当容易。 | 你有一个大型或复杂的树，在其中你需要能够快速识别任何问题。 |
| 你只需要分配少量简单的权限。            | 你需要分配大量权限。 |
| 你的组成员身份几乎不会发生变化，权限也极少更改。 | 你的组成员身份或权限会定期发生变化。 |
| 你的组之间几乎没有交叉成员关系。                  | 你的组之间存在大量交叉成员关系，即一个用户可能存在于多个具有冲突权限的组中。（两个组使得在大型环境中调试问题更加容易。） |
| 你极少需要新建组。                             | 你经常需要新建组，以便容纳被分配了某项任务的现有用户的子集。 |
| 你极少需要拆分用户组，使每个用户组子集拥有与原始组不同的权限。 | 你经常需要将现有组拆分为多个组，因为每个组所需的权限集与旧组曾经使用的不同。 |

最后一点：如果你正在创建权限组和用户组，请记住从一开始就对它们进行合理的命名。例如，可以对授予 Finance OU 用户修改权限的组使用类似 *Finance – Allow User Modify* 的名称，对 Finance OU 的用户管理员角色使用 *Finance – User Admins* 的名称。如果你能够轻松识别哪些组属于哪种类型，那么管理和编写脚本就会更加容易。

#### 从混乱中建立秩序

我们遇到过有人询问：对于加入一家新公司的人，而前任目录服务管理员留下的目录树( Tree )既没有恰当的权限设计，也缺乏一致性，我们会建议他怎么做。在这种情况下，首先分析组织的需求，再以此为出发点开展工作。同时，还应分析 Active Directory 当前已分配了哪些权限，不过只把注意力集中在这方面可能有害。毕竟，如果上一任管理员能力不足或知识不够，从一开始就无法建立合理的权限方案，那么他可能也没有准确实现组织所需的权限。

分析 Active Directory 时，首先需要识别服务器上内置组( Built-in Groups )的成员，例如域管理员( Domain Admins )、备份操作员( Backup Operators )等。然后，对组织中特有的其他组执行同样的操作。完成这些之后，使用前面描述的表，列出你负责的树中第一个域( Domain )的根上的权限。接着查看该列表中第一个容器( Container )或组织单位( Organizational Unit ,OU)的权限。接下来，浏览该容器所代表的分支，依次查看子容器，并在树中持续递归。一旦根的这个第一分支的容器权限已梳理清楚，你就应该开始了解需要哪些权限。现在，遍历该分支中的所有对象，包括打印机、用户、共享等。这耗时且烦人，但一段时间后，你应该会开始了解当前状况。所有这些只是遍历 Active Directory 的一种合理方法，并不是快速修复方案。你仍然必须继续遍历你负责的所有域，才能完成整个过程。使用脚本遍历 Active Directory 并显示某个对象的所有 ACL，通常也很有帮助。

你的首要目标应该是尽可能将单个用户权限迁移到组中，并为这些组分配用户，从而使 Active Directory 更易于管理和理解。这些组的命名应基于其用途，而不是其包含哪些用户（毕竟，你首先要理解 Active Directory）。理想情况下，你可以开始将具有相同权限的用户合并到同一个组中。

你的第二个目标是删除用户或新建组不应拥有的权限。当然,这可能意味着需要将新组的成员拆分到两个或更多单独的附加组中。例如,一个对某对象拥有读取所有属性( Read All Properties )权限和写入所有属性( Write All Properties )权限的组,可能需要拆分为三个权限更受限的组:一个拥有读取所有属性权限,一个拥有写入所有属性权限,还有一个仅拥有选定的写入权限而非完整的写入访问权限。这一点可能从你的 Active Directory 分析中显而易见,也可能来自与用户或其管理者的讨论。在实施更改之前,你至少应与他们确认这些更改,以确保你的分析准确无误。

最终,在理顺了 Active Directory 权限体系之后,你的第三个目标是尝试限制对象和分支的继承阻止,并尽可能将更多高级权限转换为一般权限。你可能会认为更早执行这一步更为合理,在某些情况下确实如此。然而,如果先完成前两个目标,你将获得一棵自己能够理解的 Active Directory 树,并且它已重新符合合理的规则。一旦拥有了一棵可管理且条理清晰的树,修复继承阻止和高级权限的问题就会容易得多。你最终可能需要回头更改在实现前两个目标时已经理顺的组或权限,但请想一想,如果试图同时完成这些工作,难度将会大得多。毕竟,你本就是在一项已经够烦人的任务中尽力而为。试图一次性完成所有工作毫无意义。在遍历树以检查继承阻止时,应按照规则 5 的要求记录被阻止的对象和分支,就像你自己从头设置阻止一样。这样,你就可以利用这些表格进行分析和跟踪,在理顺树的过程中划掉那些无用的条目。

整个这一节可以归结为两个简单的词:简化和安全。你希望在满足当前需求的前提下,实现尽可能简单、委派最少的模型,从而得到一个尽可能锁定、又切实可用的目录。

### 16.5. 设计审核方案

与权限相比,设计审核方案( Auditing Scheme )相对简单。设想一下可能需要检查 Active Directory 中正在发生的情况,然后据此进行相应设置。

> **警告**：必须谨记，每一个被审核的 Active Directory 事件都会导致系统产生额外的处理开销。如果始终在根级别为任何人的每次修改启用审核，那么当这些域控制器( Domain Controller ,DC)上发生大量 Active Directory 访问时，这将是使所有 DC 变得非常缓慢的绝佳方式。

这一点值得反复强调。审核域命名上下文( Domain Naming Context ,NC)中任何对象的更改将在整个域范围内传播，并导致服务于该域 NC 的每个 DC 都将事件记录到安全事件日志中。审核配置 NC 或架构 NC 的更改将导致林中的所有 DC 开始将事件审核记录到其安全事件日志中。如果您希望查看发生的每一个安全事件，您必须拥有从多个 DC 检索日志的工具。毕竟，如果您有 100 个 DC 并且正在记录配置 NC 的更改，由于更改可能发生在任何 DC 上，您将需要收集并合并 100 个安全事件日志以获取完整的情况。

以下是一些设计审核方案可能派上用场的示例：

- 有人抱怨用户详细信息在不明原因下被修改。
- 您注意到容器中意外创建或删除了对象。
- Active Directory 层次结构已更改，但您并未收到通知。
- 您怀疑存在安全问题。

尽管上述原因都是启用审核的充分理由，但它们更是移除对目录的原生更新访问权限并通过某种配置系统( Provisioning System )推送更新的更好理由，例如 Microsoft 的 Forefront Identity Manager 产品( FIM ，前身为 ILM 和 MIIS)、Quest 的 Active Roles Directory Management 工具，甚至自研的基于 Web 的工具。借助这类工具，您可以实现 Active Directory 中严重缺失的良好、可靠的功能，例如以下各项：

- **集中式日志记录**

  使所有有关所有请求更改的信息能够轻松地汇集到一个位置，无需额外工作。

- **业务规则**

  允许您强制命名标准或明确允许/禁止属性中的特定值。

- **触发器**

  在请求某些操作时向不同人员发送通知，例如在向 Active Directory 添加新计算机时通知资产管理组。

- **自定义授权级别**

  允许您设置限制；例如，指定数据管理员每天最多只能创建五个用户。

- **预防胜于治疗**

对目录( Directory )进行审核( Auditing )，以查找本不该发生的事情，属于被动响应( Reactive )；保护目录，使这些情况从一开始就不会发生，则是主动措施( Proactive )，从长远看工作量要少得多。

在所有这些场景中，你都需要在容器( container )或叶对象( leaf object )上设置审核选项( Auditing Options )。这些审核条目( Auditing Entry )不必一直存在，因此你可以将其记录下来，再编入脚本，在出现问题的第一时间运行。这样，系统会立即更新并准备好监视情况。只有你做好准备，才能做到这一点。

你需要分析预想会出现的场景，然后将其转化为一组组确切的审核条目规范( Auditing Entry Specification )。一旦你完成每个场景的书面说明，如果发生紧急情况，你就能按照之前制定的确切说明操作，并建立适当的快速响应机制，而这正是审核的意义所在。

#### 实施审核

Windows Server 2008 引入了全新的活动目录( Active Directory ,AD)审核功能，较 Windows Server 2003 中的功能有大幅改进。在 Windows Server 2003 域控制器( Domain Controller ,DC)上，如果启用了“审核目录服务访问”设置，则每当用户成功或失败访问定义了系统访问控制列表( System access control list ,SACL)的对象时，都会记录一个通用事件。从实用性角度来看，此功能价值有限，并且很容易使域控制器上的安全日志( security log )泛滥。

活动目录现在允许您以细粒度审核目录更改，并在更改发生时查看先前值和当前值。图 16-16 展示了一个属性修改审核事件示例。已创建许多新的审核事件，当更改发生时会将这些事件记录到安全日志。这些事件的列表见表 16-4。




![Attribute change audit](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663518.webp)


图 16-16. 属性更改审核



表 16-4. Windows Server 2008 及更高版本的审核事件

| 事件 ID | 更改类型 | 说明                                                  |
| -------- | ----------- | ------------------------------------------------------------ |
| 5136     | 修改      | 当在 SACL 中设置了相关“写入属性”审核时，只要已审核对象的属性发生更改，就会记录该事件 |
| 5137     | 创建      | 当在 SACL 中设置了“创建子对象”审核时，只要在父对象下创建了对象，就会记录该事件 |
| 5138     | 取消删除    | 当在 SACL 中设置了“创建子对象”审核时，只要在父对象下恢复了对象，就会记录该事件 |
| 5139     | 移动        | 当在 SACL 中设置了“创建子对象”审核时，只要将对象移动到父对象下，就会记录该事件 |
| 5141     | 删除      | 当在 SACL 中设置了“删除自身”审核时，只要对象被删除，就会记录该事件；或者当在 SACL 中设置了“删除子对象”审核时，只要在父对象下删除对象，就会记录该事件 |

> **注意**：Windows Server 2003 和 Windows 2000 中记录的目录服务访问( Directory Service Access )事件 566 仍然存在;但事件 ID 已更改为 4662。

启用新的审核功能需要经过三到四个步骤:

1. 启用“审核目录服务访问”组策略( Group Policy )设置。
2. 配置“高级审核策略”组策略设置。
3. 在域中要审核的对象上配置 SACL。
4. 通过修改架构中的属性定义,将属性从林范围的审核中排除。

要启用“审核目录服务访问”设置,请在应用于域控制器( Domain Controller ,DC)的组策略中,浏览到*计算机配置\策略\Windows 设置\安全设置\本地策略\审核策略*,并审核*成功*尝试。

接下来,需要在组策略中配置“高级审核策略”。这些设置位于*计算机配置\策略\Windows 设置\安全设置\高级审核策略配置\审核策略\DS 访问*下。

为了记录更改审核,需要像本章前面所述那样,在要审核的对象上配置 SACL。确保启用正确的审核条目,如图 16-15所示。

通过修改 Active Directory 架构中 `attributeSchema` 对象上的 `searchFlags` 属性,可以在全局范围内禁用属性的更改审核。`searchFlags` 属性是一个位掩码,审核由第九位管理。要使用 *adfind* 和 *admod* 禁用 `info` 属性的审核,可以运行以下命令:




```
adfind -sc s:info systemFlags -adcsv | admod systemFlags::{{.:SET:256}} -upto 1
```


要启用 `info` 属性的审核,请运行以下命令:




```
adfind -sc s:info systemFlags -adcsv | admod systemFlags::{{.:CLR:256}} -upto 1
```


必须是 Schema Admins 的成员才能修改此属性。

#### 跟踪上次交互式登录信息

Active Directory 支持一系列属性,在启用这些属性后,可将用户上次成功和失败的 Ctrl-Alt-Delete 登录的日期与时间,以及发生这些登录的计算机主机名存入目录中。这些属性是目录中 `user` 类的一部分。您可能想知道,它和 `lastLogonTimeStamp` 属性有什么区别。`lastLogonTimeStamp` 属性采用特殊机制,把更新频率限制在较低的区间(大致每 10 到 14 天一次),而且它不存储与登录尝试相关联的主机名。而这些新属性则会立即更新。

在评估此功能是否适合您的环境时,需要牢记它存在若干限制。首先,该功能仅跟踪交互式登录。换言之,只有用户在 Windows Vista 或更高版本的计算机上按下 Ctrl-Alt-Delete 时发生的登录才会被跟踪。若要启用跟踪,用户所在的域必须运行在 Windows Server 2008 功能级别( Functional Level )或更高版本,并且必须在客户端和域控制器( Domain Controller ,DC)上启用某个注册表设置。

该注册表设置是名为 `DisplayLastLogonInfo` 的 `REG_DWORD`,位于 `HKLM\Sotware\Microsoft\Windows\CurrentVersion\Policies\System`。如果在域控制器上将 `DisplayLastLogonInfo` 设置为 `1`,它便会开始将登录统计信息存储到 Active Directory 中。如果在客户端上将这个值设置为 `1`,那么当用户登录时,客户端将开始报告上次登录统计信息,类似于 Figure 16-17 所示的内容。




![Displaying last interactive logon statistics](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663519.png.webp)


图 16-17。显示上次交互式登录统计信息

与其设置注册表项,我们建议您改用此功能对应的组策略( Group Policy )设置。该组策略设置位于 *Computer Configuration\Policies\Administrative Templates\Windows Components\Windows Logon Options* 下。您要启用的具体设置是"Display information about previous logons during user logon"(在用户登录期间显示有关以前登录的信息)。若要分别启用登录统计信息的存储与显示,必须在同时应用于域控制器和客户端的策略中启用此设置。

如果在客户端( Client )上启用此设置，而这些客户端上的用户所登录的域( Domain )未运行在 Windows Server 2008 或更高功能级别( Functional Level )，则客户端将收到类似于图 16-18中所示的错误，并且无法登录。如果此设置已在客户端上启用，但未在域控制器( Domain Controller ,DC )上启用，则同样会收到图 16-18中的错误。

![Last interactive logon statistics failure](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663520.png.webp)

图 16-18. 上次交互式登录统计信息失败

目录中使用以下四个属性来提供此附加登录信息功能：

- **`msDS-LastSuccessfulInteractiveLogonTime`**

  这是用户上次成功进行 Ctrl-Alt-Delete 登录的时间。

- **`msDS-LastFailedInteractiveLogonTime`**

  这是用户上次失败的 Ctrl-Alt-Delete 登录的时间。

- **`msDS-FailedInteractiveLogonCount`**

  这是自启用该功能以来，用户发生的登录失败次数。

- **`msDS-FailedInteractiveLogonCount AtLastSuccessfulLogon`**

  这是自用户上次成功进行 Ctrl-Alt-Delete 登录以来，失败的 Ctrl-Alt-Delete 登录次数。

与 `lastLogonTimeStamp` 属性不同，这些属性没有更新频率保护机制。如果启用此功能，请记住，这些属性每次更新后，都会在下一个复制周期中进行复制。在繁忙的域中，这些属性每天可能会有数千次更新。此外，在域中有多台域控制器的环境中，无法保证向用户显示的值（如图 16-17所示）实际上就是最准确的值，因为这些属性会像目录中的任何其他更改一样进行复制。

> **警告**：如果已部署只读域控制器( Read-Only Domain Controller ,RODC),它们将在本地更新这些属性,但更改不会复制到域中的其他部分。

本节讨论的上次交互式登录统计信息功能的实现,主要是为了符合通用标准( Common Criteria )([http://www.commoncriteriaportal.org](http://www.commoncriteriaportal.org/))。除非您有业务需求,或者您是在小型(例如单站点)域中启用此功能,否则我们不建议启用它。

### 16.6. 实际环境中的 Active Directory 委派( Delegation )示例

现在似乎适合将本章所阐述的内容付诸实践。我们将使用一系列在日常管理员工作中可能遇到的任务。我们提出的解决方案可能并非这些问题的唯一解决方案。Active Directory 往往就是如此；同一个问题有多种解决方式。

#### 对组隐藏组织单位( Organizational Unit ,OU )中所有用户的特定个人详细信息

在本示例中，一个名为 Hardware Support Staff 的 OU 包含内部团队人员的用户帐户，这些人员负责修复组织内损坏的计算机。每当用户遇到故障时，他会拨打中央故障热线请求支持工程师。工程师被分配该任务，该任务会添加到她现有待处理故障列表的末尾。用户会被告知将由哪位工程师来电以及她大概何时到达。与所有此类任务一样，有些任务需要更长时间，用户已经发现如何找到分配给他们的工程师的手机或寻呼机号码，并开始直接致电工程师以获取到达时间更新，而不是拨打中央服务台。管理层已决定限制哪些人可以拨打寻呼机或手机，但他们不想停止提供工程师姓名，因为他们认为这是友好服务的一部分。因此，他们要求你找到一种方法，将 Active Directory ( AD ) 中的寻呼机和手机号码对所有不应具有访问权限的用户隐藏。

我们将采用的解决方案是：移除每个用户默认查看工程师对象的 `pager` 和 `mobile` 属性的能力。首先需要弄清当前是如何向用户授予权限的。我们查看用户对象上的访问控制列表( Access Control List ,ACL )，没有看到这两个属性中的任何一个被专门列出。不过，我们看到整个对象有一项继承的读取属性( Read Property ,RP )访问权限，授予给了 Windows 2000 之前兼容访问( Pre-Windows 2000 Compatible Access )组。我们还看到，若干属性集显式授予了经过身份验证的用户( Authenticated Users ) RP 访问权限。

接下来，我们查看这两个属性的架构定义( Schema Definition )，发现两者的 `attributeSecurityGUID` 都设置为 `{77B5B886-944A-11D1-AEBD-0000F80367C1}`，这意味着这些属性位于某个属性集( Property Set )中。我们扫描 `cn=extended-rights` 容器，确定这些属性所属的属性集是个人信息属性集( Personal Information Property Set )。再次查看访问控制列表( Access Control List ,ACL )，可以看到个人信息属性集是已向经过身份验证的用户( Authenticated Users )授予 RP( Read Property )访问权限的属性集之一。我们知道该域已启用 Windows 2000 之前兼容访问( Pre-Windows 2000 Compatible Access )，因此用户通过两个不同的访问控制项( Access Control Entry ,ACE )获得对 `pager` 和 `mobile` 属性的访问权限，这两个 ACE 分别为显式 ACE 和继承 ACE。回顾前面的权限锁定( Permission Lockdown )一节可知，显式属性集 ACE 是两者中更难处理的一个。我们将首先关注它。

我们要做的第一件事是，在 Hardware Support Staff 下创建一个名为 Engineers 的子组织单位( Organizational Unit ,OU )，并将所有工程师用户对象移动到该 OU 中。我们也可以尝试在父 OU 中逐个锁定工程师用户对象，但这会引入一层不必要的复杂性，应当避免。现在所有工程师都已隔离在自己的 OU 中，我们需要决定使用前面讨论过的哪种机制来锁定对 `pager` 和 `mobile` 属性的访问。这些选项同样包括：

1. 从个人信息属性集中删除 `pager` 和 `mobile` 属性。
2. 更改用户对象类( User Object Class )的 `defaultSD`，以移除个人信息属性集。
3. 从每个工程师对象中剥离个人信息 ACE，并为 `mobile` 和 `pager` 属性添加继承的拒绝 ACE。
4. 在每个工程师对象上为 `mobile` 和 `pager` 属性添加显式拒绝 ACE。

选项 1 和 2 可以使用，但我们必须回头遍历林( Forest )中的其余部分，并为经过身份验证的用户添加继承 ACE，以授予其对 `pager` 和 `mobile` 属性的 RP 访问权限。为了达到仅对目标 OU 更改权限的最终效果，所有这些额外工作都是必要的。如果你认为还需要为更多 OU 锁定这些属性，或者可能需要为林中的所有用户锁定这些属性，那么这些选项就会变得更容易接受。

使用选项 3 时，您仅针对工程师对象。当您剥离个人信息访问控制项( Personal Information Access Control Entry ,ACE)时，不仅会影响到对 `mobile` 和 `pager` 属性的访问，还会影响到对个人信息属性集( Personal Information property set )中所有其他属性的访问，该属性集在默认的 Windows Server 2008 林( Windows Server 2008 forest )中包含 46 个属性。

对于所有这三个选项，如果域处于 Windows 2000 之前兼容模式( Pre-Windows 2000 Compatible mode )，用户仍将通过授予 Windows 2000 之前兼容访问组( Pre-Windows 2000 Compatible Access group )的继承 ACE 访问所有属性。为了锁定这两个目标属性，我们还需要在 Engineers OU 上为每个属性添加一个继承的拒绝 ACE。这样做效果很好，大家都会满意，直到后来——可能是一两年后——当您已经完全忘记这个更改时，您决定“我们不再需要处于 Windows 2000 之前兼容模式”，并将经过身份验证的用户组( Authenticated Users group )从 Windows 2000 之前兼容访问组中移除。一旦这样做，选项 1、2 和 3 中移除的权限会突然影响到您，禁止访问个人信息属性集中的所有属性。显然，这可能会非常令人意外！您可能认为这是因为您仍然需要处于 Windows 2000 之前兼容模式，但实际上这只是一个委派问题。

最后一个选项，选项 4，将仅针对工程师用户对象，并且以后不会因其他域更改而产生意外的副作用。在这种情况下，这可能是最佳解决方案，尽管它需要大量的初始工作以及随着新工程师用户的添加而进行的持续维护。最好专门构建一个脚本来执行此工作。

您可能想知道，“这不是使用机密位( confidential bit )的好地方吗？”很遗憾，不是，这不是一个好的例子，因为它会影响林中的所有用户；更重要的是，`mobile` 和 `pager` 属性都是类别 1 属性( Category 1 attributes )，因此您无法修改它们使其机密。

#### 仅允许特定用户组访问新发布的资源

财务部门创建了一个名为 *Budget_Details* 的新共享,并将其发布到树中。共享本身的权限仅允许获得正确授权的员工读取和查看其内容,但默认情况下,所有人都能看见树中描述该共享的卷对象( Volume Object )。财务部门不希望非 Finance 组成员的任何人在 Active Directory 中看到该共享。

同样,我们需要确定的第一件事是当前如何向用户授予权限。我们查看卷对象上的访问控制列表( Access Control List ,ACL ),发现授予普通用户的唯一权限是针对经过身份验证的用户( Authenticated Users )的通用读取访问控制项( Generic Read ACE )。由于这是一个单独的对象,为其创建整个组织单位( Organizational Unit ,OU )可能并不合理,因此我们打开该卷对象的权限编辑器窗口,并删除“经过身份验证的用户”组条目。然后为 Finance 组添加一个条目,并分配“读取”和“列出”权限。



#### 使用机密位限制除 HR 以外的所有人查看国家/地区 ID 号

经过多次讨论,决定将国家/地区 ID 号从专有数据库迁移并插入到 Active Directory 中。由于默认情况下只有人力资源部门和域管理员( Domain Admins )才能看到该属性,因此对其可见性存在诸多顾虑。

您使用新的国家/地区 ID 号属性扩展架构( Schema ),并将 `searchFlags` 属性设置为 `128`,以指示应使用机密属性功能保护该属性。现在,您只需创建一个名为 *HR-Confidential* 的新组,并在每个域的根处分配一个可继承的访问控制项( Access Control Entry ,ACE ),授予该组对用户对象上国家/地区 ID 号属性的控制访问权限。

以后,如果有人决定还要保护该属性免受域管理员的访问,则需要逐一为每个对象应用针对该组的显式拒绝访问控制项。然而,试图拒绝对域管理员访问目录中数据的做法实际上并不具备可执行性。无论何时,只要域管理员想要再次访问该属性,她自己就可以直接修改 ACL。如果您绝对不能允许域管理员访问这些数据,则需要寻找其他方式来保护数据,例如使用第三方加密,或将数据放置在不属于该域、因而不受域管理员控制的计算机上。

### 16.7. AdminSDHolder 进程

自 Windows 2000 以来，Active Directory 中有一个后台进程一直令管理员感到困惑，它就是 *AdminSDHolder*。该名称源自 Active Directory 中的一个对象，该对象存储了用于保护敏感对象的安全描述符。敏感对象是指属于以下组的成员的用户、组和计算机：

- 账户操作员( Account Operators )
- 管理员( Administrators )
- 备份操作员( Backup Operators )
- 域管理员( Domain Admins )
- 域控制器( Domain Controllers )
- 企业管理员( Enterprise Admins )
- 打印操作员( Print Operators )
- 只读域控制器( Read-Only Domain Controllers )
- 复制器( Replicator )
- 服务器操作员( Server Operators )
- 架构管理员( Schema Admins )

此外，以下对象无论组成员身份如何，均被显式保护：

- Administrator
- krbtgt

Active Directory 保护这些对象，是为了防止被委派了这些组成员管理权限的用户借此提升特权。这类用户通常是委派管理员，例如帮助台人员。举例来说，如果允许帮助台用户重置 Domain Admins 或 Account Operators 组成员的密码，他就可以重置该用户的密码，然后以该用户身份登录——从而大幅提升帮助台管理员自身的权限。

*AdminSDHolder* 进程默认每 60 分钟在 PDC 模拟器 FSMO 角色持有者上后台运行一次，并向范围内每个对象应用一个不继承权限的特殊 ACL。该 ACL 存储在域根下 `CN=AdminSDHolder,CN=System` 对象的 `ntSecurityDescriptor` 属性中。

> **注意**：如果要修改 *AdminSDHolder* 进程的运行频率，可以将 `HKLM\SYSTEM\CurrentControlSet\Services\NTDS\Parameters` 中的 `AdminSDProtectFrequency` 注册表设置（`REG_DWORD`）设置为 `60` 到 `7200`（秒）之间的值。建议保留默认值 `3600` 不变。

管理员通常在几种场景中首次遇到此过程。第一种情况是，某用户曾经是管理员，但后来这些权限被撤销。第二种常见场景出现在 Exchange 2010 及更高版本中。如果用户使用日常用户账户执行管理任务（不推荐），则当他们首次尝试为 ActiveSync 连接移动设备时，连接将失败，因为 Exchange 需要额外访问权限，才能在该用户账户下创建一个特殊对象来跟踪该移动设备。

当对象不再被视为受保护时，并不存在自动“撤销”过程来移除 *AdminSDHolder* 添加的保护。相反，必须手动配置该对象，使其再次继承权限。此外，应将 `adminCount` 属性的值重置为 `0`。

通过实施以下最佳实践，可以避免这里讨论的两种场景：为所有管理任务使用第二个用户账户，并将管理员的标准账户视为最小特权账户，就像普通员工账户一样。您也可以修改 *AdminSDHolder* 对象的 ACL，但这样做只会回避糟糕的安全设计。

在某些情况下，您可能希望从 *AdminSDHolder* 中排除前面列出的一些组。Active Directory 允许您将以下组（及其成员）排除在保护之外。一般而言，我们*不*建议您使用这些组，但如果您选择使用它们，并且需要将其成员排除在保护之外，也可以这样做。这些组包括：

- 账户操作员( Account Operators )
- 服务器操作员( Server Operators )
- 打印操作员( Print Operators )
- 备份操作员( Backup Operators )

> **注意**：如果某个用户是这些组之一的成员，同时也是另一个受保护组( Protected Group )的成员，则该用户将继续受 *AdminSDHolder* 保护。

若要排除这些组中的任何一组，需要按照以下步骤使用 ADSI Edit 修改 `dsHeuristics` 属性：

1. 启动 ADSI Edit（开始→运行→**`adsiedit.msc`**），然后打开配置命名上下文( Configuration Naming Context ,NC )。

2. 浏览至 `CN=Windows NT,CN=Services`。

3. 打开 `CN=Directory Service` 对象的属性。

4. 如果 `dsHeuristics` 属性未设置，请将其设置为 `000000000100000f`。如果该属性已设置，则继续下一步。

   > **警告**：如果已设置了值，请勿用步骤 4 中的默认值覆盖 `dsHeuristics` 属性。`dsHeuristics` 还控制着许多其他行为！

5. `dsHeuristics` 属性中的前四个字符分别控制着对先前列出的四个组之一的排除：

   1. 若要排除账户操作员( Account Operators )，请将 `dsHeuristics` 的第一个字符设置为 `1`（例如 `100000000100000f`）。
   2. 若要排除服务器操作员( Server Operators )，请将 `dsHeuristics` 的第二个字符设置为 `1`（例如 `010000000100000f`）。
   3. 若要排除打印操作员( Print Operators )，请将 `dsHeuristics` 的第三个字符设置为 `1`（例如 `001000000100000f`）。
   4. 若要排除备份操作员( Backup Operators )，请将 `dsHeuristics` 的第四个字符设置为 `1`（例如 `000100000100000f`）。

完成更改后，您可能需要强制运行 *AdminSDHolder* 进程，以便测试更改。您可以使用 LDP，通过一个 *操作属性( Operational Attribute )* 来调用后台进程：

1. 启动 LDP，然后绑定到主域控制器( Primary Domain Controller ,PDC )模拟器灵活单主机操作( Flexible Single Master Operation ,FSMO )角色持有者。
2. 打开浏览→修改对话框。
3. 在“属性”框中输入 `RunProtectAdminGroupsTask`，如图 16-19 所示。
4. 在“值”框中输入 `1`，然后按 Enter 键。
5. 将操作改为“替换”。
6. 单击“运行”。




![LDP attribute Modify dialog](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663521.webp)


图 16-19. LDP 属性修改对话框

### 16.8. 动态访问控制

Windows Server 2012 中最炙手可热的新功能之一便是动态访问控制( Dynamic Access Control ,DAC )。DAC 试图解决一个长期困扰 Windows 管理员的难题——管理文件系统访问控制列表和不断变化的组成员资格。NTFS ACL 结构面临的挑战之一是无法构建复合表达式。也就是说,你不能为同时属于财务用户组和经理组的用户授予对文件或文件夹的读取权限。为满足这一需求,你必须创建一个新组——比如财务经理组——并为该组授予读取权限。随着时间推移,类似这样的常见情景所产生的排列组合会导致 Active Directory 中组的数量激增、令牌膨胀问题,以及使所有这些组保持最新的 IT 管理挑战。

DAC 旨在通过为文件系统引入基于表达式的 ACL 结构来解决上述两个问题,该结构同时基于组成员资格和 AD 中用户对象的属性。这些属性以声明( Claim )的形式表示,并在用户通过 Windows Server 2012 域控制器( Domain Controller ,DC )进行身份验证时添加到用户的安全令牌中。

> **注意**：如果用户由运行 Windows Server 2012 之前版本 Windows 的域控制器( Domain Controller ,DC)进行身份验证，则 Windows Server 2012 文件服务器可以联系该文件服务器所在站点( Site )中的 Windows Server 2012 DC，并获取包含声明数据( Claims Data )的访问令牌( Access Token )。

除了用户的属性之外，Windows 8 工作站还可以通过一项称为 *复合标识*( Compound Identity )的功能参与动态访问控制( Dynamic Access Control ,DAC)。复合标识使来自用户工作站的声明可以包含在用户的令牌中，从而也包含在资源上的访问控制表达式( Access Control Expression )中。例如，借助此功能，你可以强制要求用户从公司计算机访问文件夹。

最后，文件和文件夹的属性可以包含在访问和审核表达式( Auditing Expression )中。这些属性可以来自手动最终用户分类，也可以来自 Windows Server 中的文件分类基础结构( File Classification Infrastructure ,FCI )功能。

如你所见，DAC 是一项广泛的功能，成功部署需要整个组织内 IT 部门内外的资源共同参与。我们将在此讨论此功能的 Active Directory 配置组件，以及用于验证配置步骤的快速演练。关于如何最好地部署 DAC 以及各种文件服务器特定功能的讨论，我们将留给更有资格讨论这些主题的其他出版物。

#### 为动态访问控制( Dynamic Access Control ,DAC)配置 Active Directory

部署 DAC 有几种不同的范式，这使得相关讨论更加复杂。只需组成员身份，无需任何额外配置，即可利用复合访问控制列表( Access Control List ,ACL)功能。但是，如果你希望开始基于用户（或其设备）的属性构造 ACL，则需要在 Active Directory 中配置*声明类型( claim types )*以及一些组策略( Group Policy )设置。

最后，你可以发布文件系统访问策略，这些策略根据文件自身的属性，动态地将 ACL 应用或模拟到文件系统数据。这些策略称为*中央访问策略( central access policies )*。中央访问策略由一系列*中央访问规则( central access rules )*组成，这些规则用于控制将应用于匹配文件和文件夹的 ACL。可在文件和文件夹上设置的属性通过*资源属性( resource properties )*发布。

幸运的是，Microsoft 提供了一个图形用户界面( Graphical User Interface ,GUI)，用于配置大多数 DAC 功能集。如果你尚未浏览过 Active Directory 管理中心( Active Directory Administrative Center ,ADAC)中的动态访问控制节点，请花几分钟时间了解一下。我们刚才讨论的每个组件都可在动态访问控制节点下配置。唯一必须仅通过 Windows PowerShell 配置的组件是声明转换功能，当你需要跨林信任( forest trust )传递声明时会用到该功能。

##### 配置声明类型( Claim Type )

你很可能要处理的第一个任务，是让属性( attribute )可用作声明( claim )。这可通过在 Active Directory 中创建声明类型来配置。声明类型将 Active Directory 中用户或其设备的某个属性映射为用户访问令牌( access token )中包含的声明。要创建声明类型，请启动 Active Directory 管理中心( Active Directory Administrative Center ,ADAC )，然后浏览到 *Dynamic Access Control\Claim Types*（即动态访问控制( Dynamic Access Control ,DAC )下的声明类型）。在图 16-20中，我们将创建一个名为 *Employee Type* 的声明类型。此声明来源于 `employeeType` 属性。




![Creating the Employee Type claim](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663522.webp)


图 16-20. 创建 Employee Type 声明

如果声明中将包含一组已知值，你可以在屏幕底部配置建议值( suggested value )，这些值会显示在访问控制列表( Access Control List ,ACL )编辑器的下拉列表中。图 16-21展示了如何为全职员工( full-time employee )添加建议值。值字段对应 Active Directory 属性中存储的实际数据，而显示名称( display name )字段则是 ACL 编辑器中显示的内容。创建声明类型后，它将在整个林( forest )中的 Windows Server 2012 文件服务器( file server )上可用。




![Adding a suggested value for a claim](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663523.webp)


图 16-21. 为声明添加建议值

非常重要的一点是，你必须考虑将属性发布为声明时，对属性中的数据所创建的新依赖关系。一旦将某个属性发布为声明，若不同步更新所有引用该属性格式的 ACL，就无法更改该属性中存储的数据格式。如果直接从另一个系统（例如人力资源数据库）获取属性值，则需要将此依赖关系告知源系统( source system )的所有者。若未在 Active Directory 团队和文件服务器团队之间进行协调，就无法更改源系统中的值。

##### 配置中央访问策略

中央访问策略( Central Access Policies )使组织能够基于数据的属性，从中央位置（Active Directory）对数据应用访问规则。当您有机制对数据进行分类，并且需要遵守特定的策略或法规时，此功能尤其有用。例如，您可能有一个策略，规定任何包含个人身份信息( Personally Identifiable Information ,PII )（例如，国家/地区身份证号）且分类为中等影响或更高级别的数据，只能由全职员工访问。

首先，使用 Active Directory 管理中心( Active Directory Administrative Center ,ADAC )启用个人身份信息资源属性( Resource Property )。这是一个动态访问控制( Dynamic Access Control ,DAC )开箱即用的资源属性。您可以根据需要添加任意数量的资源属性，和/或自定义包含的资源属性。

接下来，您需要使用 ADAC 定义中央访问规则( Central Access Rule )，该规则描述您想要实现的访问控制。中央访问规则由确定规则适用数据的范围条件( Scoping Criteria )以及应用于该数据的 ACL 组成。要将规则范围限定为仅适用于 PII，请编辑目标资源条件，如图 16-22所示。




![Central access rule targeting criteria](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663524.webp)


图 16-22. 中央访问规则目标条件

接下来，配置权限以仅限制具有 Employee Type 声明且值为 Full Time Employee 的 Domain Users 访问，如图 16-23所示。您可以将权限配置为以“建议”模式运行，在此模式下，权限与策略不匹配的资源将记录在事件日志中，也可以对所有匹配的资源强制执行权限。我们建议您从审核/建议模式开始，以评估策略的影响。




![Central access rule permissions editor](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663525.webp)


图 16-23. 中央访问规则权限编辑器

完成后，您的中央访问规则应类似于图 16-24。

创建好要应用到资源的规则后，需将其添加到中央访问策略( Central Access Policy )中。图 16-25 展示了一个包含刚创建规则的基本策略。策略准备好应用后，需通过组策略( Group Policy )将其提供给文件服务器。




![Central access rule configuration](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663526.webp)


图 16-24. 中央访问规则( Central Access Rule )配置

在将要应用中央访问策略的组策略中，浏览到*计算机配置\策略\Windows 设置\安全设置\文件系统\中央访问策略*节点。右键单击并选择“管理中央访问策略”，可以应用一个或多个策略。添加上一步中创建的策略。




![New central access policy](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663527.webp)


图 16-25. 新建中央访问策略

您还需要启用中央访问策略审核功能，以利用我们在中央访问规则中选择的审核/建议模式。为此，请在组策略管理编辑器中的*安全设置*下，浏览到*高级审核策略配置\审核策略\对象访问*节点。为*审核中央访问策略暂存( Audit Central Access Policy Staging )*和*审核文件系统( Audit File System )*条目启用成功和失败审核。

将中央访问策略发布到文件服务器后，必须将该策略应用到文件夹结构。只有完成此步骤，策略中的规则才会生效。要完成此步骤，请打开要应用策略的文件夹的属性，并访问“安全”选项卡。单击“高级”，切换到“中央策略”选项卡，然后应用之前创建的策略，如图 16-26 所示。




![Central access policy application](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663528.webp)


图 16-26. 中央访问策略应用

##### Kerberos 策略

如果你所在林的功能级别不是 Windows Server 2012 林功能级别( Forest Functional Level )，则可能需要调整一个或多个应用于域控制器( Domain Controller ,DC)和/或文件服务器的策略，以确保动态访问控制( Dynamic Access Control ,DAC)在 Windows Server 2012 文件服务器上可用。需要配置的第一个策略是在域控制器上启用声明( Claims )和复合身份( Compound Identity )的颁发。编辑默认域控制器策略( Default Domain Controllers Policy )（或另一个应用于 DC 的组策略对象( Group Policy Object ,GPO)），然后浏览到 *Computer Configuration\Policies\Administrative Templates\System\KDC*。将“KDC 支持声明、复合身份验证和 Kerberos 强化”( KDC support for claims, compound authentication, and Kerberos armoring )策略设置为“支持”。

如果在文件服务器上的访问控制列表( Access Control List ,ACL)中使用声明，但尚未向该文件服务器部署一个或多个中央访问策略( Central Access Policy )，则需要确保当用户的令牌( Token )不包含声明信息时，文件服务器从 Windows Server 2012 DC 代表用户请求服务票证( Service Ticket )。

如果有 Windows 8 客户端并且希望利用设备声明( Device Claims )，则需要在应用于所有客户端的 GPO 中启用复合身份。为此，请在组策略管理编辑器( Group Policy Management Editor ,GPME)中浏览到 *Computer Configuration\Policies\Administrative Templates\System\Kerberos*，并将“Kerberos 客户端支持声明、复合身份验证和 Kerberos 强化”( Kerberos client support for claims, compound authentication and Kerberos armoring )策略设置为“已启用”。还必须启用“支持复合身份验证”( Support compound authentication )策略，并使用“始终”选项配置该策略。

#### 在文件服务器上使用动态访问控制

虽然我们已经探讨了如何通过中央访问策略应用访问控制列表，但也可以直接开始使用声明以及动态访问控制带来的新 ACL 功能，而不必经过中央访问策略流程。

##### 使用组进行复合表达式配置

开箱即用，您可以在 Windows Server 2012 文件服务器上直接创建仅涉及现有组成员身份的 ACL。这项新功能的强大之处在于，您可以使用 *AND* 和 *OR* 运算符定义布尔表达式，并设置匹配条件（例如要求用户是列表中一个或多个组的成员）。

回顾之前的示例，我们需要将文件夹的访问权限限制为同时属于财务用户组和管理人员组的用户。要完成此任务，请打开文件夹的安全属性，然后单击“高级”。将财务用户组添加到 ACL 并配置权限（例如读取或写入访问权限）。接下来，添加一个条件，要求用户同时也是管理人员组的成员，如图 16-27所示。

![Compound group expression](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663529.webp)

图 16-27. 复合组表达式

虽然这只是一个仅包含两个组的简单示例，但您可以看到，利用现有的 Active Directory 组，可以轻松构建更为复杂的表达式来映射组织结构。只需在文件服务器上利用此功能，就能大幅减少某些用户所属的组数量，这完全可行。

##### 在 ACL 中使用声明

图 16-27中使用的同一个编辑器，也可用于基于用户和设备声明以及目标资源属性来构建表达式。举一个简单的例子，让我们扩展之前构建的表达式——该表达式允许财务用户和管理人员组的成员访问——增加一个要求：用户不得为供应商。

为此，添加一条规则，指明“员工类型”不等于“供应商”，如图 16-28所示。您会看到，下拉列表中已预填充了我们在创建声明类型时定义的推荐值列表。

![Excluding vendors from access to data](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663530.webp)

图 16-28. 将供应商排除在数据访问之外

##### 审核

你可以运用我们刚刚探讨过的文件访问概念来配置审核。这极大地提升了 Windows 中文件系统审核功能的实用性。以往，审核功能往往会造成信息过载，因为在配置需要审核哪些操作方面缺乏灵活性。

考虑到能够基于用户、设备和资源属性构建表达式，你可以配置一条审核规则，仅审核对包含个人身份信息( Personally Identifiable Information ,PII )的资源的访问，如图 16-29 所示。




![Configuring auditing of access to personally identifiable information](./image/16.%20Active%20Directory%20Security%20Permissions%20and%20Auditing/httpatomoreillycomsourceoreillyimages1663531.webp)


图 16-29. 配置对个人身份信息访问的审核

### 16.9. 总结

安全始终重要，而当涉及对组织网络的访问时，它更是至关重要。我们希望本章能让您理解，如何对整个域( Domain )或单个对象的各个属性( Property )允许或拒绝访问权限( Permission )。审核( Auditing )也是安全的一部分，而预先设计好相关机制——使其能够持续运行，或在需要时随时启用——是跟踪此类系统的最佳方式。

向对象分配权限和审核条目( Auditing Entry )表面上似乎很简单。然而，一旦开始深入探究设置权限和审核条目的艺术，就会很快发现需要考虑的事项非常多。全局设计( Global Design )是必要的第一步。动态访问控制( Dynamic Access Control ,DAC)使规划变得更加重要，因为它能够针对活动目录( Active Directory ,AD)中的各个属性值( Attribute Value )创建安全依赖关系( Security Dependency )。

尽管以后通过添加额外容器( Container )来扩展目录树( Tree )很少会成为问题，但在大型目录树中，制定一些总体准则或规则，以便为整个设计和重新设计过程赋予一定的结构感，是很有意义的。理想情况下，我们在此处展示的黄金规则( Golden Rule )和表格应能让您规划和实施合理的权限方案( Permission Scheme )，而这正是本章的目标。

---

## 第17章 设计和实现架构扩展

为了让 Active Directory 能够保存任何对象(如用户),它必须知道该对象具有哪些属性和特征。换言之,它需要该对象的蓝图。Active Directory 架构是所有可潜在存储在 Active Directory 中的类( Class )、属性( Attribute )和语法( Syntax )的蓝图。

在考虑扩展架构时,应牢记以下注意事项:

- Microsoft 设计 Active Directory 是为了保存您将需要的最常见对象和属性。由于它永远无法预见公司所需的每一类对象或每一个特定属性,因此 Active Directory 被设计为可扩展的。毕竟,如果这些对象和属性将日常使用,那么其设计就不应被轻视。管理员需要了解架构的重要性以及如何扩展它。扩展架构是解决各种问题的有用且简单的方案,而不了解这种潜力意味着您将很难将其识别为可能遇到的问题的解决方案。
- 设计架构扩展非常重要,部分原因在于您在架构中创建的任何新类或属性都是永久性添加。在 Windows Server 2003 及更高版本的林中,您可以禁用或重新定义架构扩展,但永远无法将其完全删除。
- 尽管扩展 Active Directory 很容易,但令人惊讶的是,许多公司由于担心对 Active Directory 的影响而不愿实施架构扩展。Windows 2000 中最大的障碍之一是,每当扩展部分属性集( Partial Attribute Set ,即向全局编录添加属性)时,都必须对所有全局编录( Global Catalog ,GC)服务器执行完全重新同步。幸运的是,Microsoft 在 Windows Server 2003 中解决了此问题,不再执行完全重新同步。

本章将引导您完成扩展架构的整个过程,从更改的初始设计到实现,并讨论如何避免可能出现的陷阱。接着,我们讨论如何分析可用的选择,以及是否可以通过其他方式获得所需的设计结果。我们显然会介绍如何从基本原理实现架构更改,但在此之前,我们会确定设计和修改类或属性的步骤。最后,我们介绍管理架构时需要注意的一些陷阱。

我们不会花太多时间介绍大量具体示例。这主要是因为，我们无法设想你可能需要的每一种架构扩展( Schema Extension )。因此，在示例中，我们只使用一个新的通用类( Generic Class )，以及对默认用户对象( Default User Object )的少量属性扩展( Attribute Extension )。在给出修改类的示例时，我们会扩展用户对象类( User Object Class )。

首先，我们来看看如何设计你可能希望在企业环境( Enterprise Environment )中进行的更改。

> **注意**：如果您尚未阅读过，我们强烈建议您参阅第 5 章，以深入了解活动目录架构( Active Directory Schema )。本章内容依赖于该章所讨论的概念。

### 17.1. 在组织中指定负责人

如果所在组织尚未有一位集中负责对象标识符( Object Identifier ,OID )命名空间的专人，就应确定这样一位负责人。该 OID 管理员负责获取 OID 命名空间，为该命名空间设计一套适合本组织的结构，通过维护结构图和已分配 OID 清单来管理该命名空间，并按需从该结构中为新类( Class )和属性( Attribute )颁发适当的 OID。每当需要向组织的架构( Schema )中添加新类或属性时，OID 管理员都会为该新增项提供一个唯一 OID。随后，OID 管理员会记录该 OID，并附上一组详细信息，说明请求原因以及该架构扩展将用于何种用途。请记住，除 Active Directory 外，IT 组织中的其他成员也可能需要 OID。其他 LDAP 目录和简单网络管理协议( Simple Network Management Protocol ,SNMP )应用程序，就是同样会使用 OID 的两类应用示例。

相比之下，Active Directory 管理员负责为林( Forest )设计和创建架构中的适当类，并负责实现第三方应用程序所需的架构扩展。他们负责根据来自组织内部的请求实际更改架构，并确保不会创建执行相同功能的冗余对象、确保以最佳方式利用继承( Inheritance )、确保为相应对象建立索引，以及确保部分属性集( Partial Attribute Set )包含正确的属性。

> **注意**：如果你正在设计将修改其他组织架构的代码，例如为某个软件产品设计代码，那么伴随该代码的文档应当明确说明到底创建了哪些类与属性以及为什么。文档还应说明，该代码需以“架构管理员”组成员的权限运行，因为在许多组织中，“架构管理员”AD 组为空。

通过编程方式处理架构变更的更好方案，是向组织提供用于架构修改的 LDIF 文件。这样组织可以审查实际变更，并将其与其他架构修改合并到批量更新流程中，从而更易于测试和生产实施。一些大型组织有严格的架构变更控制流程，要求提供描述所有变更的 LDIF 格式文件。在这些组织中未能提供所需 LDIF 文件将导致更新被拒绝。

请注意，虽然 OID 管理员的职责不一定与 Active Directory 管理员一致，但完全可能是同一人或同一批人。

### 17.2. 更改架构的考量

在考虑更改架构之前，不仅需要审视命名空间，还需充分考虑到您的 Active Directory 部署将要承载的数据。毕竟，只有了解数据，才能决定需要做出哪些更改以及这些更改可能影响哪些方面。

#### 设计数据

无论采用何种方式迁移至 Active Directory，最终都需要明确将为 Active Directory 中的对象存储哪些具体数据。您是否会使用用户对象的 `physicalDeliveryOfficeName` 属性？`telephonePager` 属性呢？迁移过程中，您是否打算合并内部员工办公地点列表与电话数据库？假如您确实需要了解每位员工掌握的语言或持有的资质，又该如何？还有他们的鞋码、衬衫尺码、子女数量，以及是否喜爱动物呢？

关键在于，其中一些属性已存在于 Active Directory 架构中，而另一些则不然。在某个阶段，您必须确定实际想要包含的数据。这是一个重要决定，因为并非所有数据都适宜加入 Active Directory。虽然在目录中记录鞋码数据或许无伤大雅，但从业务角度可能并无太大意义。您需要自问：“这些数据是否需要在给定域的所有域控制器( Domain Controller ,DC )或林中的所有全局编录( Global Catalog ,GC )上存在？”对于这类信息，应用分区( Application Partition )、Active Directory 轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS )，甚至 SQL Server 数据库可能是更合适的存储方案。当涉及的数据具有敏感性或保密性时，AD 林之外的解决方案往往尤为适用。

请记住，添加到目录中的每项数据都需要进行复制。这可能会对网络流量、存储需求以及构建新域控制器所需时间产生显著影响。如果数据频繁变更，还需考虑增加的复制负载。若复制已成为网络负担，由于额外的开销，整体复制可能会遭遇更多延迟。

#### 改，还是不改

当你在 Active Directory 架构( Active Directory Schema )中发现缺陷时，必须考虑修改该架构是否是继续处理的正确方式。发现架构缺少一整套对象( object )及多个属性( attribute )，与发现打印机对象( printer object )的 `person-who-needs-to-refill-the-printer-with-toner` 属性在架构中缺失，完全是两回事。也没有任何规则规定，一旦你希望在现有对象上创建三个额外属性，就应该修改架构。这完全取决于选择。

为帮助你做出选择，你应问自己，是否还有其他对象或属性可用来解决问题。

假设你正在寻找用户对象( user object )的某个属性，用来保存用户的员工标识号( staff identification number )。你需要问：用户对象是否已有某个现有属性可用来保存该员工 ID 号，而你原本并不打算使用它。这样，如果并非必须修改架构，就能避免修改。以莱斯特大学( Leicester University )为例：我们当时有一个庞大的用户群需要注册，并且需要为每位学生保存一个特殊 ID 号。在英国，每位大学生都有一个大学与学院招生服务系统编号( University and Colleges Administration System number ,UCAS number )，更常见的叫法是 UCAS 编号；这是 UCAS 分配的唯一字母数字字符串，独立于学生所属的具体大学。学生在最初开始了解大学时会收到 UCAS 编号。这些编号用于向潜在大学标识学生，贯穿学生的整个本科阶段，并且是检查学生详细信息有效性的良好标识符。默认情况下，架构中没有名为 `UCAS-Number` 的属性，因此我们有两种选择：找到某个名称合适但原本不打算使用的属性并加以利用，或者修改架构。

由于我们最初只是想除了默认用户信息之外再存储这一条信息，所以无论如何都谈不上是巨大的变更。我们只是查看是否可以使用其他任何架构属性来容纳该数据。我们很快找到了原本从未打算使用的 `employeeID` 用户属性，它似乎正好符合要求，因此我们决定使用它。虽然它的命名不像名为 `UCAS-Number` 的属性那样贴切，但这确实意味着在此情形下我们无需修改基础架构( base schema )。

这里的关键点在于，我们选择不修改架构( Schema )，因为已经找到了一个令我们满意的空闲属性( Spare Attribute )。我们同样有可能找不到合适的属性，于是决定着手使用自己定制的属性来完成架构更改。

> **警告**：这个将 `employeeID` 属性挪作他用的示例中，该属性被改用来保存的数据与 `employeeID` 这一名称所隐含的原始意图高度吻合。绝对不建议将基础架构( base schema )中包含的属性改变用途，用于与其原始意图毫不相关的目的。Active Directory 的后续版本完全有可能开始将基础架构中的某个属性用于其原始意图，或者第三方应用程序可能会做出这种假设。如果您已选择改变该属性的用途，那么您将需要从该属性中迁出数据，并更新所有依赖它的应用程序。

如果您已将 Microsoft Exchange 安装到林( forest )中，还有一组属性可供您随意使用，满足您的任何需求。这些属性称为扩展( `extension` )或自定义属性( `custom attributes` )，名称如 `extensionAttribute1`、`extensionAttribute2` 等。操作系统通常不使用这些属性，它们被保留下来供您随意使用。Exchange Server 2013 默认会创建 50 个此类属性，因此 Active Directory 中直接内置了备用属性容量。因此，如果我们想存储用户会说的语言数量，只要愿意，就可以将该值直接存储在 `extensionAttribute1` 中。

在少数情况下，利用扩展属性和未使用的属性效果很好。然而，如果有 20 个、30 个或更多复杂属性，每个属性都有特定语法，或者如果我们需要存储 20 个对象，每个对象有 30 个属性，我们就会遇到更多困难。当您拥有类似这样的数据时，就需要考虑全局。

#### 全局概览

那么，你已经有了所有数据的清单，并且怀疑架构( Schema )要么无法保存你的数据，要么无法以令你满意的方式保存。你现在需要考虑你组织的架构的未来，并据此进行设计。以下问题应有助于你确定如何针对每个新类( Class )或属性( Attribute )进行设计：

- 此类或属性是否已以某种形式存在于架构中？换言之，该属性是否已默认存在，或者是否已有人创建了它？如果不存在，你可以创建它。如果它已以某种形式存在，你能利用该现有属性吗？如果可以，你应考虑这样做。

  如果不能，你需要考虑修改现有属性以满足你的需求，或创建第二个实质上保存相似或相同数据的属性，而这会造成浪费。如果现有属性无用，你能否创建新属性，将现有属性的值迁移到新属性，并禁用旧属性？这些就是你需要考虑的问题类型。

- 此类或属性是仅用于非常特定用途，还是该对象( Object )可能被组织中的其他人使用（即创建、更改、修改）？如果该类或属性仅用于特定用途，提出更改的人应知道所需内容。如果该类或属性可能影响其他人，则应谨慎确保其设计能满足所有潜在用户的需求——例如，日后如有必要可以扩展它，而不会在更新架构对象时影响现有对象实例( Object Instance )。

  例如，对于属性，你应询问该属性的语法( Syntax )以及最大值/最小值（对于字符串或整数）是否有效，或者是否应使其更适用于许多人的需求。具体而言，如果你现在创建了长度介于 5 到 20 个字符之间的 `CASE_INSENSITIVE_STRING`，而日后要求该属性为长度介于 5 到 20 个字符之间的 `CASE_SENSITIVE_STRING`，则你需要创建新属性并迁移数据，因为属性一旦创建，其语法就无法更改。

- 你是否正在通过添加属性来修改现有类？如果是，那么如果不直接将该属性应用于对象，而是将其添加到辅助类( Auxiliary Class )中的一组属性，是否更好？

- 你是否要向通常通过标准 GUI 工具(如 Active Directory Users and Computers)管理的现有类( Class )添加属性( Attribute )？新属性不会自动显示在 GUI 中，并且需要更改所用的工具或扩展该工具(如果可能)。你必须意识到你的更改可能对现有工具以及你自己设计的工具产生的影响。

基本上，这些问题可归结为四个简单得多的问题：

- 需要做出的更改对此对象( Object )的所有潜在用途和用户而言是否有效且合理？
- 该更改是否会影响将来可能需要对此对象和其他对象做出的任何其他更改？
- 该更改现在或将来是否会影响其他任何人？
- 该更改是否会影响公司内部或外部人员正在开发的任何应用程序( Application )？

> **注意**：与创建有效的对象标识符( Object Identifier ,OID)命名空间时一样,请确保使用合理的名称创建类( Class )和属性( Attribute )。这些名称应具有唯一的公司前缀( Prefix ),以便于识别,并应由以连字符分隔的首字母大写单词组成。有关为名称选择前缀的详细信息,请参阅侧边栏“选择合理的命名前缀”。



选择合理的命名前缀

乍看之下,为架构扩展( Schema Extension )使用唯一前缀似乎并不重要。唯一前缀的益处会在某家公司发现另一家公司也在使用相同前缀时体现出来。如果另一家公司是应用程序供应商( Application Vendor ),这可能会变得极其棘手。

例如,假设 MyCorp Financial Services 使用“myCorp”前缀作为其架构扩展的前缀。MyCorp Financial 已使用两个新属性扩展其架构:`myCorpAttrib1` 和 `myCorpAttrib2`。现在假设 MyCorp Financial 从另一家公司 MyCorp Software Solutions 购买了一个软件包,而该公司也选择使用 `myCorpAttrib1` 和 `myCorpAttrib2` 作为属性名称。

在这种情况下,MyCorp Financial Services 将处于非常不利的境地。MyCorp Financial 唯一的选择将是更改其属性以前的所有使用方式,以便应用程序可以重用这些名称。如果 MyCorp Financial 不重命名其属性,就将无法使用已购买的应用程序。

一条重要的经验法则是:切勿修改默认系统属性。这可以确保你不会与操作系统视为默认的任何内容发生冲突,否则最终可能会在升级期间或与其他应用程序(如 Exchange)一起使用时导致问题。向类添加额外属性没有问题,但应避免修改现有属性。

### 17.3. 创建架构扩展

可通过三种方式修改架构：使用活动目录架构( Active Directory Schema )MMC 管理单元、使用 LDIF 文件，或通过 ADSI 或 LDAP 以编程方式实现。此处不会过多介绍活动目录架构管理单元，因为其使用相当直观，不过会在管理架构主机( Schema Master )FSMO 角色时涉及。通常，不建议使用活动目录架构管理单元来扩展架构。相反，应使用 LDIF 文件。LDIF 文件更易于审阅和记录，因为它们只是特殊格式的文本文件。大多数供应商都会提供 LDIF 文件，其中包含可供审阅并随后在方便时导入的架构扩展。

通过 LDIF 文件手工创建自定义架构扩展可能极为繁琐。相反，可以利用开发林( Development Forest )(或 AD LDS 实例)中的活动目录架构 MMC 管理单元来创建架构扩展。使用 MMC 创建扩展后，可通过 *ldifde* 或 AD 架构分析器将其导出为 LDIF 文件，并发布该 LDIF 文件。有关 AD LDS 和 AD 架构分析器的更多信息，请参阅第 20 章。

#### 首次运行 AD 架构管理 MMC 管理单元

架构管理 MMC 管理单元不像其他 Active Directory 管理单元那样可以从“管理工具”菜单中直接使用。要使用它，您需要先在命令提示符下键入以下命令，注册该管理单元的动态链接库( Dynamic Link Library ,DLL)文件：




```
regsvr32.exe schmmgmt.dll
```


然后，您可以通过创建一个自定义 MMC 并向其中添加 Active Directory 架构管理单元，来启动 Active Directory 架构控制台。要创建控制台，请依次单击“开始”→“运行”，键入 **`mmc.exe`**，然后单击“确定”。接着，在空白的 MMC 中，依次单击“文件”→“添加/删除管理单元”。在这里，您可以单击“添加”按钮，然后选择“Active Directory 架构”作为要添加的项。随后依次单击“添加”按钮、“关闭”按钮，再单击“确定”按钮，这样您就拥有了一个承载 Active Directory 架构管理单元的 MMC，可供使用，日后也可以根据需要将其保存。

允许在 Windows 2000 上修改架构

在 Windows 2000 下，您必须绕过一项保护措施，架构主机( Schema Master ) FSMO 角色持有者才允许您修改架构。首先，进行更改的用户必须是 Schema Admins 组的成员，该组位于林根域( Forest Root Domain )中。其次，您需要在希望进行更改的域控制器( Domain Controller ,DC)上修改注册表。

在架构主机本身上，使用 *regedt32.exe* 或 *regedit.exe* 打开注册表，然后找到以下项：`HKLM\SYSTEM\CurrentControlSet\Services\NTDS\Parameters`。

现在，创建一个名为 `Schema Update Allowed` 的新 `REG_DWORD` 值，并将其设置为 1。您需要做的就这些。这样您就可以在该域控制器上编辑架构了。

另一种进行更改的方法是将以下三行内容复制到一个扩展名为 *.reg* 的文本文件中，然后在您希望启用架构更新的 DC 上打开它(即运行该文件)：




```
REGEDIT4
[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\NTDS\Parameters]
"Schema Update Allowed"=dword:00000001
```


这会自动为您修改注册表，因此您无需手动操作。一旦您在某个特定域控制器上修改了注册表，并将要进行更改的用户帐户加入 Schema Admins 组，那么您在该域控制器上对架构所做的任何更改都将被接受。

#### 架构缓存

每个域控制器( Domain Controller ,DC )都在内存中保留一份完整的架构副本。这就是所谓的*架构缓存*。它的用途是在根据名称请求架构对象 OID 时提供非常快速的响应。

架构缓存实际上是一组哈希表，包含系统已知的所有 `classSchema` 和 `attributeSchema` 对象，以及用于快速搜索的特定索引(`attributeSchema` 对象的 `attributeID`、`mAPIId` 和 `lDAPDisplayName`，以及 `classSchema` 对象的 `governsID` 和 `lDAPDisplayName`)。

这些对象在域控制器启动时加载到架构缓存中，并在更新后五分钟再次加载。然而，如果出于某些原因需要立即更新架构缓存，例如在创建新对象或属性类之后，可以强制立即重新加载缓存。

如前所述，系统在内存中保留一份副本，纯粹是为了帮助需要快速、频繁访问架构的搜索。如果系统要保持缓存与实际 Active Directory 架构同步，在性能方面代价可能很高；对架构进行更改是一个密集的过程，因为系统在创建新对象时需要进行大量检查并设置对象默认值。因此，对底层架构所做的更改与缓存副本之间存在时间延迟。通常，架构倾向于成批更新。这很可能是因为应用程序在安装甚至正常操作期间为其自身目的创建了多个类。如果五分钟之后仍在创建类，系统会在第一次五分钟更新完成后，以五分钟为增量更新缓存。只要架构类更新持续进行，这一过程就会继续。

在中间的五分钟时间段内，当底层架构已被修改但缓存尚未更新时，无法创建新类的对象或属性实例。如果尝试创建对象，系统将返回错误。这是因为对象创建引用的是缓存，而不是底层架构。要解决这个问题，可以通过更新*RootDSE*上的一个特殊操作属性来强制立即重新加载缓存。稍后我们在考虑如何使用架构管理( Schema Management )MMC 管理单元创建和删除类时，会对此进行介绍。同理，如果将对象标记为失效，这不会生效，直到缓存被重新加载。

尽管在架构( Schema )缓存刷新之前，您无法为您已创建的新对象类型创建新实例，但可以将已创建的新属性或类添加到正在创建的其他类中。为什么？因为属性或类是通过对象标识符( Object Identifier ,OID)添加的，因此系统无需在架构缓存中执行任何查找。虽然 Active Directory 为确认数据有效而执行的所有系统检查——如“修改架构时系统执行的检查”（第 508 页）一节所述——仍会执行，但这些检查针对的是 Active Directory 中的架构，而不是缓存。若非如此，则您必须至少等待五分钟，才能将创建的任何新属性添加到新类中，这将是不可接受的。

#### 架构主机 FSMO

架构主机（Schema Master）是灵活单主机操作（Flexible Single Master Operations，FSMO）角色之一，也就是负责执行架构（Schema）更改的域控制器（Domain Controller，DC），这样多个用户或应用程序就无法同时在两台或多台不同的域控制器上修改架构。在企业中安装 Active Directory 时，林中的第一个域——即林根域（Forest Root Domain）——中的第一台服务器会被指定为架构主机 FSMO。之后，如果需要更改架构，可以在当前主机上进行。

可以通过三种方式从现有架构主机转移该角色：通过 Microsoft 管理控制台（Microsoft Management Console，MMC）中的 Active Directory 架构管理单元（Snap-in）、通过 *NTDSUTIL* 工具，或通过使用 Active Directory 服务接口（Active Directory Service Interfaces，ADSI）或轻型目录访问协议（Lightweight Directory Access Protocol，LDAP）的代码。

使用 Active Directory 架构 MMC 管理单元转移该角色很简单。首先，需要连接到将成为新主机的服务器，然后强制将该角色更改为当前已连接的服务器。要开始此过程，只需运行 MMC，然后在左侧作用域窗格（Scope Pane）中右键单击 Active Directory 架构。在出现的上下文菜单（Context Menu）中，选择“更改 Active Directory 域控制器”。

现在可以选择要连接的新服务器。在因维护等原因长时间关闭某台服务器之前，应将所有 FSMO 角色（不仅是架构主机）转移到新服务器。连接到架构主机 FSMO 角色的目标服务器后，在作用域窗格中右键单击 Active Directory 架构，然后从上下文菜单中选择“操作主机（Operations Master）”。此时将出现一个对话框，其中显示当前持有架构主机 FSMO 角色的 DC，以及将该角色更改为当前所连接服务器的选项。图 17-1 显示了此对话框。单击“更改”按钮即可转移架构主机角色。




![Transferring the schema master FSMO](./image/17.%20Designing%20and%20Implementing%20Schema%20Extensions/httpatomoreillycomsourceoreillyimages1663532.webp)


图 17-1. 转移架构主机 FSMO

如果架构主机角色的持有者永久不可用（例如硬件故障、操作系统损坏等），则需要在另一台域控制器上夺取（Seize）架构主机角色。要夺取 FSMO，必须使用 *ntdsutil* 命令行实用工具。有关夺取 FSMO 角色的详细信息，请参阅第 18 章。

#### 使用 LDIF 扩展架构

扩展架构( Schema )最常用的方法之一是使用 LDAP 数据交换格式( LDAP Data Interchange Format ,LDIF)。LDIF 在 RFC [2849](http://www.ietf.org/rfc/rfc2849.txt) 中定义，提供了一种通过人类可读的文本文件表示目录数据的方式。你可以采用 LDIF 格式从 Active Directory 导出数据，也可以使用 LDIF 添加、修改和删除数据。*ldifde* 程序随任何 Windows Server 一起安装，可用于导入和导出 LDIF 数据。若要导入 LDIF 文件的内容，请运行以下命令：




```
c:> ldifde -v -i -f import.ldf
```


将 *import.ldf* 替换为要导入的 LDIF 文件的名称。

LDIF 文件包含一个或多个条目，每个条目包含一个或多个应添加、替换或删除的属性。该格式简单明了，但非常严格。以下示例展示了一个将组对象添加到 Users 容器中的 LDIF 文件：




```
dn: cn=mygroup,cn=users,dc=mycorp,dc=com
changetype: add
objectclass: group
description: My Group
member: cn=administrator,cn=users,dc=mycorp,dc=com
member: cn=guest,cn=users,dc=mycorp,dc=com
```


第一行必须是对象的 DN。第二行是 `changetype`，其取值为 `add`、`modify`、`modrdn` 或 `delete` 之一。使用 `add` 时（如本例所示），必须指定该对象的所有必需属性。对于组对象，只需要指定 `objectClass`。`cn` 属性不是必需的，因为它已在 DN 中指定。

> **注意**：Windows 2000 Active Directory 还要求为新用户和组指定 `sAMAccountName` 属性。

使用 LDIF 文件创建可移植的架构扩展非常简单。只需创建一个包含所有必要的 `classSchema` 或 `attributeSchema` 对象添加或修改的 LDIF 文件，使用任何基于 LDIF 的客户端(例如 Windows 自带的 *ldifde*)的管理员即可轻松将其导入 Active Directory。以下 LDIF 文件展示了如何创建一个属性以及一个包含该新属性的辅助类：




```
dn: cn=myCorp-ITUserBuilding,cn=schema,cn=configuration,dc=X
changetype: add
attributeID: 1.2.3.4.111.1
attributeSyntax: 2.5.5.1
oMSyntax: 127
isSingleValued: TRUE
lDAPDisplayName: myCorp-ITUserBuilding
objectClass: attributeSchema

dn:
changetype: modify
add: schemaUpdateNow
schemaUpdateNow: 1
-

dn: cn=myCorp-ITUser,cn=schema,cn=configuration,dc=X
changetype: add
objectclass: classSchema
description: Class for MyCorp Employees
lDAPDisplayName: myCorp-ITUser
governsID: 1.2.3.4.111.2
objectClassCategory: 3
subClassOf: top
mayContain: myCorp-ITUserBuilding

dn:
changetype: modify
add: schemaUpdateNow
schemaUpdateNow: 1
-
```


要导入此示例，你需要将占位符 DN 替换为架构命名上下文( Schema Naming Context ,Schema NC )的 DN。你可以使用 *-c* 开关和 *ldifde* 的宏扩展功能轻松完成此操作：




```
>ldifde -i -f schema-extension.ldf -c "cn=schema,cn=configuration,dc=x" 
"#schemaNamingContext"
```


如前所述，`attributeSchema` 和 `classSchema` 对象的所有必需属性都必须指定。添加的顺序也很重要。由于我们希望将新属性添加到类中，因此需要先创建它。此外，在尝试通过 `lDAPDisplayName` 引用新属性之前，还需要重新加载架构缓存，否则操作将失败。为此，我们对 `RootDSE`(即空白 DN)执行修改操作，并写入 `schemaUpdateNow` 属性。



> **注意**：如果在 `myCorp-ITUser` 类的 `mayContain` 属性中使用 `attributeID` OID 1.2.3.4.111.1 来代替 `lDAPDisplayName myCorp-ITUserBuilding`，我们就可以跳过属性创建后的架构缓存刷新。由于在本示例中使用了 `lDAPDisplayName`，因此需要重新加载架构缓存，因为必须执行查找以检索正确的 OID。

使用 LDIF 实现架构扩展有双重好处。首先，由于 LDIF 具有人类可读且语法定义良好的特点，需要实施扩展的人员可以轻松了解将要执行的操作。如果使用管理员无法查看源代码的程序，他对所做更改的可见性就会大打折扣。同样地，LDIF 文件为架构扩展提供了一种简易的文档机制。由于 LDIF 文件只是基于文本的文件，架构管理员可以将其归档到服务器上，并随时准确地查看针对某些应用程序所做更改的具体内容。

#### 修改架构时系统执行的检查

创建新类或属性时，除了您提供的检查外，系统还会在 Active Directory 中执行一些基本检查以验证数据是否有效。属性的检查项见表 17-1，新类的检查项见表 17-2。



表 17-1. 创建新属性时系统执行的检查

| 属性 | 系统执行的检查 |
| ----------------- | ------------------------------------------------------------ |
| `lDAPDisplayName` | 在 Active Directory 中必须唯一。 |
| `attributeId` | 在 Active Directory 中必须唯一。 |
| `mapiId` | 如果存在，在 Active Directory 中必须唯一。 |
| `schemaIDGUID` | 在 Active Directory 中必须唯一。 |
| `attributeSyntax` | 必须与 `oMSyntax` 相关联。 |
| `oMSyntax` | 必须与 `attributeSyntax` 相关联。 |
| `rangeLower` | 如果同时存在 `rangeUpper`，则应满足以下条件：`rangeUpper > rangeLower`。 |
| `rangeUpper` | 如果同时存在 `rangeLower`，则应满足以下条件：`rangeUpper > rangeLower`。 |
| `linkID` | 在 Active Directory 中必须唯一。反向链接必须有对应的正向链接。 |
| `searchFlags` | 模糊名称解析（ Ambiguous Name Resolution ，ANR ）属性必须是 Unicode 或 Teletex。 |



表 17-2. 创建新类时系统执行的检查

| 属性                   | 执行的系统检查                                               |
| ---------------------- | ------------------------------------------------------------ |
| `lDAPDisplayName`      | 在 Active Directory 中必须唯一。                             |
| `governsId`            | 在 Active Directory 中必须唯一。                             |
| `schemaIDGUID`         | 在 Active Directory 中必须唯一。                             |
| `subClassOf`           | 检查以确保不违反 X.500 规范（即辅助类不能从结构类继承，而抽象类只能从另一个抽象类继承）。此属性中定义的所有类必须已存在。 |
| `rDNAttID`             | 其语法必须为 Unicode 字符串。                                |
| `mayContain`           | 在 `mayContain` 属性中指定类之前，该类必须已在架构中定义。   |
| `systemMayContain`     | 此属性中定义的所有类必须已存在。                             |
| `mustContain`          | 此属性中定义的所有类必须已存在。                             |
| `systemMustContain`    | 此属性中定义的所有类必须已存在。                             |
| `auxiliaryClass`       | 此属性中定义的所有类必须已存在，并且其 `objectClassCategory` 必须指示为 `88-Class` 或 `Auxiliary`。 |
| `systemAuxiliaryClass` | 此属性中定义的所有类必须已存在，并且其 `objectClassCategory` 必须指示为 `88-Class` 或 `Auxiliary`。 |
| `possSuperiors`        | 此属性中定义的所有类必须已存在，并且其 `objectClassCategory` 必须指示为 `88-Class` 或 `Structural Class`。 |
| `systemPossSuperiors`  | 此属性中定义的所有类必须已存在，并且其 `objectClassCategory` 必须指示为 `88-Class` 或 `Structural Class`。 |

#### 使类和属性废弃

Active Directory 不允许从架构中删除对象。然而，如果您的林运行在 Windows Server 2003 或更高版本的功能级别上，您可以重新定义或禁用类和属性。这使您能够纠正可能犯下的错误，或者重新利用不再使用的类或属性。

如果您创建了某种类或属性，后来决定不再需要它，可以简单地将其禁用，这通常被称为使其“废弃”。这可以通过将架构对象上的 `isDefunct` 属性设置为 TRUE，或在 Active Directory 架构 MMC 管理单元中取消勾选“属性处于活动状态”或“类处于活动状态”复选框来实现。

要使属性成功废弃，系统会确保该属性不是任何非废弃类的强制属性或可选属性，也不是任何类的 RDN 属性(`rDNAttID`)。要使类成功废弃，系统会确保该类不是任何其他非废弃类的父类，不是任何其他非废弃类的辅助类，也不是任何其他非废弃类的可能上级。如果您后来决定再次使用该架构对象，请将 `isDefunct` 的值设置为 FALSE。执行此操作时进行的检查与最初创建相应类型的新架构对象时相同。

> **注意**：若要查看 Active Directory 架构( Schema )MMC 管理单元中的失效( defunct )属性( attribute )和类( class )，必须启用这些属性和类的显示。若要显示失效的架构对象( schema object )，请单击“视图”→“失效对象”。

当属性或类被标记为失效时，Active Directory 中存储的相应数据不会被删除。考虑到这一点，在将某个类标记为失效之前，应从目录中删除该类的所有实例。同样，在将某个属性标记为失效之前，应清除所有对象上的该属性。

当架构对象失效时，尝试创建其实例会失败，就像它不存在一样。修改现有实例也是如此，无论修改的是对象上的属性还是对象本身，都会表现为它们不存在。不过，可以删除作为失效类实例的对象。搜索作为失效类实例的对象会成功，搜索包含失效属性的未失效类也会成功。所有属性，无论是否失效，都可以读取。这些都是必需的，以便管理员或应用程序作者能够清理并删除现已失效的对象实例，以及从现已失效的属性中删除所有值。

> **注意**：即使某个架构对象已失效，就其 `distinguishedName`、对象标识符( Object Identifier ,OID )和 `lDAPDisplayName` 而言，它仍然存在。不能创建具有这些值的第二个架构对象，但在大多数情况下，可以更改这些值。例外情况是，对于用作 `objectClass` 的相对可分辨名称( Relative Distinguished Name ,RDN )属性，不能重用其 OID。

#### 缓解架构冲突( Schema Conflict )

某些扩展 Active Directory 架构( Active Directory Schema )的应用程序，其扩展方式不符合本章讨论的最佳实践。在最严重的情况下，第三方使用了任意对象标识符( Object Identifier ,OID )，而这些标识符来自 Microsoft 的 OID 空间。管理员导入这些架构扩展时，导入成功，而且一切看起来都很正常。但不幸的是，Microsoft 后来使用了相同的 OID（因为这些 OID 本来就属于 Microsoft），导致升级林( Forest )时在 *adprep* 期间执行 Active Directory 架构升级等步骤失败。

在 Windows Server 2008 之前，可以编辑 *adprep* 使用的 LDIF 文件，以缓解因冲突导致的失败。虽然这缓解了眼前的问题，但会导致林的基础架构( Base Schema )偏离 Microsoft 随每个 Active Directory 版本提供的架构。为解决此问题，Microsoft 在 Windows Server 2008 中更改了 *adprep* 过程，要求对 LDIF 文件进行数字签名( Digital Signature )。数字签名可确保文件未被更改或篡改。



> **注意**：Active Directory 架构 LDIF 文件的签名通过随附的编录文件( Catalog File )进行验证。*ldifde* 包含一个 *-$* 参数，用于指定验证 LDIF 文件签名时要使用的编录文件。

由于基础 Active Directory 架构的 LDIF 文件现在已签名，因此无法在运行 *adprep* 之前直接修改这些文件来确保该过程成功。相反，你需要先将冲突的类( Class )或属性( Attribute )标记为失效( Defunct )，使用有效的 OID 重新创建它们，然后重新填充属性或重新创建对象。完成此过程后，即可成功完成 *adprep* 过程。

### 17.4. 总结

对于大型企业或应用程序开发人员而言，精心设计对 Active Directory 架构( Schema )所做的更改，其重要性再怎么强调也不为过。扩展 Active Directory 架构并不是管理员或组织应该害怕的事情，但它是你应该仔细考虑并妥善规划的事情。遵循第5章以及本章中概述的指导，将确保你的架构扩展得到妥善规划。如果某些事情确实没有规划好，你可以使用架构的失效功能来禁用并隐藏类( Class )或属性( Attribute )，以便可以重用它们的名称和唯一标识符。

希望我们不仅向你展示了修改架构的风险和陷阱，还展示了架构为何必要以及它如何支撑整个 Active Directory。虽然修改 Active Directory 时应谨慎，但明智的管理员对 Active Directory 架构应该像对 Windows 注册表一样，没什么可恐惧的。

---

## 第18章 备份、恢复和维护

维护活动目录( Active Directory ,AD)时，一个非常重要但常被忽视的方面是制定可靠的灾难恢复计划( Disaster Recovery Plan )。虽然报告的 Active Directory 损坏事件很少，但确实发生过，无论发生的可能性有多低，你都应该做好准备。你需要恢复意外删除的对象的可能性远高于处理完全损坏，因此你也应该为此做好准备。如果拥有 FSMO 角色的域控制器( Domain Controller ,DC)突然离线，且你无法将其恢复，你是否已经制定了应对计划？这些都是充满压力的场景：客户端在抱怨，或者应用程序不再正常工作，人们怨声载道。在这种时候，你不会希望手忙脚乱地寻找解决方案。拥有文档齐全且经过测试的流程来处理这些问题至关重要。

在本章中，我们将了解如何通过备份 Active Directory 来为故障做好准备。然后，我们将介绍如何从备份中恢复 Active Directory 的全部或部分内容，以及如何从活动目录回收站( Active Directory Recycle Bin )中恢复已删除的对象。接着，我们将介绍如何从 FSMO 故障中恢复。最后，我们将探讨其他可以执行的预防性维护( Preventive Maintenance )操作，以确保 Active Directory 的健康。

### 18.1. 备份 Active Directory

备份 Active Directory 是一项简单的操作。可以使用 Windows 2000 和 2003 附带的 NT Backup 实用工具、Windows Server 2008 及更高版本附带的 Windows Server Backup 实用工具或第三方备份软件包来完成。幸运的是，可以在 Active Directory 联机时对其进行备份，因此不必像某些其他系统那样为了执行备份而担心造成中断。

要备份 Active Directory，必须备份林( Forest )中每个域内一个或多个域控制器( Domain Controller ,DC)的系统状态( System State )。如果希望能够还原林中的任何域控制器，则需要备份每个域控制器。在 Windows 2000 或 Windows Server 2003 域控制器上，系统状态包含以下内容：

- **Active Directory**

  这包括 NTDS 文件夹中的文件，其中包含 Active Directory 数据库(*ntds.dit*)、检查点文件(*edb.chk*)、事务日志文件(*edb\*.log*)以及保留事务日志(*res1.log* 和 *res2.log*)。

- **启动文件**

  计算机启动所需的文件。

- **COM+ 类注册数据库**

  已注册 COM 组件的数据库。

- **注册表**

  注册表的内容。

- **SYSVOL**

  这是 *SYSVOL* 共享，包含所有基于文件的组策略对象( Group Policy Object ,GPO)信息以及 *NETLOGON* 共享，后者通常包含用户登录和注销脚本。

- **证书服务( Certificate Services )**

  这仅适用于运行证书服务的 DC。

> **注意**：尽管大多数备份软件包允许你执行增量备份或差异备份，但在 Active Directory 中，你只能对系统状态执行完整备份。

Windows Server 2008 及更高版本的域控制器( Domain Controller ,DC )系统状态备份除了包含前面列出的组件外，几乎还包含所有操作系统文件。因此，你会注意到 Windows Server 2008 及更高版本 DC 上系统状态备份的大小会大幅增加。

执行备份的用户必须是 Backup Operators 组的成员，或者具备与 Domain Admins 等效的权限。

由于 Active Directory 处理已删除对象的方式，你的备份仅在特定时间段内有效。在 Active Directory 中删除对象时，这些对象最初并不会被完全移除。如果启用了 Active Directory 回收站( Active Directory Recycle Bin )，已删除对象在已删除对象生存期( deleted object lifetime )内会继续驻留在 Active Directory 中，随后还会继续保留至墓碑生存期( tombstone lifetime )结束。已删除对象生存期决定了 Active Directory 将对象保留在回收站中以供恢复的时间长短。墓碑生存期值则决定了在已删除对象超过已删除对象生存期之后，Active Directory 在将其完全移除之前继续保留这些已删除对象的时间长短。这两个生存期均可配置。已删除对象生存期由属性 `msDS-DeletedObjectLifetime` 定义，而墓碑生存期则由以下对象上的 `tombStoneLifetime` 属性定义：




```
cn=Directory Services, cn=Windows NT, cn=Services, cn=Configuration, <ForestDN>
```


不同操作系统版本中新建林的 `tombStoneLifetime` 默认值记录在表 18-1中。默认情况下，`msDS-DeletedObjectLifetime` 属性不会被填充值，因此默认情况下它会使用与 `tombstoneLifetime` 相同的值。这两个值都可以修改，因此你应检查你所在林中的取值分别是多少。就备份而言，你不应还原早于已删除对象生存期与墓碑生存期两者中较小值的备份，否则已删除对象会被重新引入。如果由于某种原因，你无法在这两个值中较小者的时间范围内成功完成备份，请考虑增大这两个值。



表 18-1. 新建林的墓碑生存期

| 操作系统 | 墓碑生存时间( Tombstone Lifetime ,TSL ) |
| ----------------------- | ----------------------------------------- |
| Windows 2000            | 60 天                                   |
| Windows Server 2003     | 180 天                                  |
| Windows Server 2003 R2  | 60 天(R2 中的回归缺陷) |
| Windows Server 2003 SP2 | 180 天                                  |
| Windows Server 2008     | 180 天                                  |
| Windows Server 2008 R2  | 180 天                                  |
| Windows Server 2012     | 180 天                                  |

在考虑保留备份副本的时长时，还有一个需要注意的问题与密码有关。默认情况下，计算机账户( Computer Account )和托管服务账户( Managed Service Account ,MSA )每 30 天更改一次密码。域控制器( Domain Controller ,DC )会接受当前密码以及前一个密码，因此，如果从超过 60 天的备份中还原计算机对象，这些计算机很可能需要重置密码。信任关系( Trust Relationship )也可能受到影响。与计算机账户一样，信任对象中也会存储当前密码和前一个密码，但与计算机账户密码不同，信任密码每 7 天更改一次。这意味着，如果从超过 14 天的备份中以授权方式还原信任对象，则可能需要重置信任。

> **警告**：域控制器备份明确不支持磁盘映像。这涵盖了所有映像实例，从虚拟硬件磁盘备份到使用 Ghost 等磁盘映像软件，再到各种附加存储产品中提供的特殊映像功能。活动目录( Active Directory )是一个跨多个域控制器( Domain Controller ,DC)运行的分布式系统，每个域控制器都为其他域控制器维护状态。对分布式系统的各个部分进行映像并单独恢复，可能对整个目录的一致性造成灾难性后果。可能出现的问题包括 USN 回滚、残留对象以及 SID 回滚。

使用磁盘映像的唯一安全方式是关闭林中的所有域控制器，然后对磁盘进行映像。当需要恢复时，同样关闭所有域控制器，并将每个域控制器回滚到同一时间点。尽管这是一种安全的方式，但 Microsoft 仍不支持，且仅应在测试环境中使用。

有关更多详细信息，请参阅 MS 知识库文章 [875495](http://bit.ly/16IjhbM)。

#### 使用 NT 备份实用工具

NT 备份实用工具( NT Backup utility )安装在所有 Windows 2000 和 Windows Server 2003 计算机上。可以通过转到“开始”→“所有程序”→“附件”→“系统工具”→“备份”来使用它。也可以转到“开始”→“运行”，输入 **`ntbackup`**，然后单击“确定”来启动它。图 18-1 显示了 Windows Server 2003 下 NT 备份实用工具的第一个屏幕。




![NT Backup or Restore Wizard](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663533.webp)


图 18-1. NT 备份或还原向导( NT Backup or Restore Wizard )

NT 备份实用工具可用于备份系统，也可用于执行还原。我们将在本章后面介绍还原。如果在第一个屏幕上单击“高级模式”( Advanced Mode )链接，则会看到如图 18-2 所示的屏幕。




![Advanced mode NT backup](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663534.webp)


图 18-2. 高级模式 NT 备份

在本例中，我们单击了“备份”( Backup )选项卡，然后选中了“系统状态”( System State )旁边的复选框。如果需要，我们也可以备份任何其他驱动器，但在执行 Active Directory 的基本还原时，只需要系统状态。

单击“开始备份”( Start Backup )按钮，即可启动备份。在图 18-2中，我们将 *D:* 驱动器配置为存储备份文件的位置。如果需要，这也可以是远程文件服务器或其他备份介质。

还可以通过单击“开始备份”按钮，然后单击“计划”( Schedule )按钮，按我们选择的时间间隔计划备份。之后，单击“属性”( Properties )按钮，将弹出如图 18-3 所示的屏幕。




![Scheduling NT Backup](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663535.webp)


图 18-3. 计划 NT 备份

在本例中，我们将备份配置为每天上午 7:30 运行一次。图 18-3 中的屏幕实际上是计划任务( Scheduled Tasks )的一部分，计划任务是 Windows 2000 和 Windows Server 2003 中可用的作业计划系统。

#### 使用 Windows Server Backup

Windows Server 2008 引入了一个完全重构的备份和还原实用工具。如果您习惯了 NT Backup，则需要做一些调整，因为该工具已经完全重新设计，并有一些重大的新限制。为了节省篇幅，本书中我们只讨论特定于备份和还原 Active Directory 的功能。有关 Windows Server Backup (WSB) 的完整介绍，请访问[此网站](http://bit.ly/ZqhgKH)。

> **注意**：Windows Server Backup 默认情况下不会安装。要使用它，必须使用服务器管理器( Server Manager )安装该功能。

要启动 WSB，请转到“开始” → “管理工具” → “Windows Server Backup”。该工具已转换为 MMC 管理单元，如图 18-4 所示。

> **注意**：你可以直接通过“开始”→“运行”→**`wbadmin.msc`** 启动 WSB，而无需在开始菜单中查找。

![Windows Server Backup](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663536.webp)

图 18-4. Windows Server 备份

Windows Server 备份必须备份到不包含系统状态备份任何组件的卷。这意味着你不能选择包含系统文件、活动目录数据库（*ntds.dit*）、Sysvol、活动目录事务日志等的卷。备份将在指定驱动器上按 *<Drive>:\WindowsImageBackup\<HostName>\Backup <time stamp>* 的目录结构创建。有关绕过此限制的信息，请参阅即将出现的侧边栏允许系统状态备份到任意卷。如果你未启用此设置，并且指定了一个不在备份范围内的卷，你将收到类似于图 18-5的错误。你也可以指定网络路径进行备份。

![Windows Server Backup error](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663537.webp)

图 18-5. Windows Server 备份错误

允许系统状态备份到任意卷

默认情况下，你不能在包含备份文件所在卷上创建系统状态备份。然而，你可以设置一个注册表值来绕过此限制。你还需要使用两倍的空间，因为卷影复制（参见配方 18.4）将创建备份的卷影副本。

要启用此功能，请在 `HKLM\SYSTEM\CurrentControlSet\Services\wbengine\SystemStateBackup` 下创建一个名为 `AllowSSBToAnyVolume` 的 `REG_DWORD`。将 `AllowSSBToAnyVolume` 的值设置为 `1`，以启用将系统状态备份到包含在备份中的卷。

有关此注册表设置的更多信息，请参阅 http://support.microsoft.com/kb/944530。

由于进行此更改存在风险，我们建议如果你打算在域控制器上使用 Windows Server 备份，请专门设置分区方案，以便有一个单独的卷用于存储备份。

若要创建系统状态备份( System State Backup )，请在备份向导( Backup Wizard )中选择“自定义备份配置”。接下来，单击“添加项”，然后选择“系统状态”。您可能还需要选择文件，例如非 AD 集成的 DNS 区域( DNS Zone )或任何其他特定于域控制器( Domain Controller ,DC)的数据。在下一页上，选择目标位置，例如网络共享( Network Share )或另一个本地驱动器，然后完成向导。在我们的测试系统上，在 Windows Server 2008 R2 Enterprise 上新建 Active Directory 林( Active Directory Forest )时，系统状态备份总大小约为 10 GB。

如果要从命令行创建系统状态备份，该怎么办？创建存储在 *E:* 驱动器上的备份的命令为 *wbadmin start systemstatebackup -backuptarget:E: -quiet*。如果未指定 *-quiet*，系统将在备份完成前提示您继续。

#### 备注

有关 Windows Server Backup 和 Active Directory 的详细信息,请参阅[此链接](http://bit.ly/13yca7R)中的“AD DS Backup and Recovery Step-by-Step Guide”。

### 18.2. 还原域控制器

Active Directory 的优势之一是内置冗余(Redundancy)。当丢失单个域控制器(Domain Controller,DC)时，其影响通常应该微不足道。但对于许多服务（如 DHCP），其架构决定了依赖于特定服务器。当该服务器不可用时，客户端会受到影响。多年来，大多数这些服务（包括 DHCP）都已内置故障转移(Failover)或冗余。对于 Active Directory，其架构就是围绕冗余构建的。客户端不依赖于单个 DC；如果发生故障，它们可以无缝故障转移到另一个 DC。

当故障确实发生时，你应该问自己几个问题来评估影响：

- **域控制器是该域(Domain)中的唯一一个吗？**

  这是最坏的情况。Active Directory 中的冗余仅当域中有一个以上的域控制器时才适用。如果只有一个，则存在单点故障(Single Point of Failure)。除非你能让该域控制器重新上线或从备份(Backup)还原，否则可能会不可挽回地丢失该域。

- **域控制器是否拥有 FSMO 角色？**

  第 2 章中概述的五个 FSMO 角色在 Active Directory 中起着重要作用。FSMO 角色不是冗余的，因此如果 FSMO 角色所有者变为不可用，你可能需要在另一个域控制器上夺取该角色。有关更多信息，请查看 Recipe 18.6。

- **域控制器是全局编录(Global Catalog,GC)服务器吗？**

  全局编录功能可以添加到任何域控制器。但是，如果站点(Site)中只有一个全局编录服务器，并且它变得不可用，则可能影响用户的登录能力。只要客户端能够访问全局编录，即使它不在最佳位置，它们也能登录。如果某个没有全局编录的站点因某种原因与网络其余部分失去连接，这将影响用户的登录能力。在 Windows Server 2003 及更高版本中，你可以基于每个站点启用通用组缓存(Universal Group Caching)，以限制此潜在问题，但前提是用户未使用 `userPrincipalName` 进行身份验证(Authentication)。

- **从容量角度看，该域控制器是否必要？**

如果您的域控制器( Domain Controller ,DC)运行已接近容量上限,并且其中一台发生故障,就可能使其余服务器不堪重负。此时,客户端在身份验证时可能开始出现登录失败或极度缓慢的情况。

- **是否有其他服务(如 Exchange)依赖该特定域控制器?**

  Exchange 会大量使用 Active Directory,尤其是全局编录( Global Catalog ,GC)。Exchange 正在使用的域控制器发生故障时,可能会在邮件环境中造成大量问题,具体取决于所使用的 Outlook 和 Exchange 版本。较新版本的 Exchange 和 Outlook(2003 及更高版本)比旧版本更能应对中断。在中断期间,邮件传递以及客户端查找都可能受到影响。Exchange 只是一个示例,但它说明了在环境中引入启用 Active Directory 的服务时,你必须注意的一个问题。

这些问题可以帮助你评估还原域控制器的紧迫性。如果对所有问题的回答均为“否”,则域控制器可以保持停机一段时间而不会产生重大影响。

当你确定需要还原域控制器时,有两种选择:通过复制还原,或从备份还原。

#### 从复制恢复

恢复域控制器的一种方法是启动一台新安装或修复的机器，并将其提升为 Active Directory 中的域控制器。当你因硬件故障导致单个域控制器失效，且没有该机器的近期备份，或不想通过备份来恢复域控制器时，可以选择此方法。此方法允许你通过在 AD 中提升新安装的机器来替换服务器，并让复制将所有数据复制到该域控制器。以下是执行此类恢复的步骤：

1. 从 AD 中移除故障域控制器。在提升新安装的服务器之前，必须从 Active Directory 中移除旧域控制器的残留信息。我们将在稍后详细描述具体步骤。
2. 重建操作系统。重新安装操作系统及域控制器上支持的任何其他应用程序。
3. 提升服务器。在留出足够时间让域控制器移除操作在整个林内复制后，你可以将新服务器提升为 AD 中的域控制器。
4. 配置任何必要的角色。如果故障服务器曾担任任何 FSMO 角色，或是全局编录服务器或 DNS 服务器，你可以配置新服务器来承担这些角色。

> **注意**：一种可能的最佳实践是保留一台备用服务器，该服务器已安装操作系统和其他所需软件，可随时发货，或在所有位置现场备用。这样一来，如果你的一台域控制器( Domain Controller ,DC)发生重大故障，就可以直接使用该备用服务器，而无需为立即更换故障机器中的硬件而焦头烂额。另一种做法是，在故障影响最严重的主要站点( Primary Site )中额外配置域控制器容量，尤其是对 Exchange 而言。这种替代策略通常比在每个位置都保留备用硬件要常见得多。

这种方法最大的潜在缺点是还原时间。根据目录信息树( Directory Information Tree ,DIT )文件的大小，以及新 DC 与其将进行复制的服务器之间的网络连接速度，还原时间可能长达数小时甚至数天。使用媒体安装( Install from Media ,IFM)选项可以大幅缩短还原时间，该选项允许你从一个域控制器的系统状态备份( System State Backup )中提取文件，并使用这些文件快速将另一台服务器提升为域控制器。与尝试通过 WAN 复制整个 DIT 相比，压缩这些备份文件，然后通过网络将其复制到远程站点，或通过其他介质将其运送到该站点，可能会更快。有关此方法的详细信息，请参阅本章后面的 从媒体安装 一节。

##### 手动从 Active Directory 中移除域控制器

从复制恢复方法的关键步骤之一是在域控制器再次添加到 AD 之前，移除与其关联的对象。Windows Server 2008 允许您使用“Active Directory 用户和计算机”MMC 管理单元移除故障域控制器。选择代表故障域控制器的计算机对象并将其删除。您将收到类似 图 18-6 的提示，要求您确认该域控制器确实已永久离线。确认后，元数据清理步骤将自动执行。




![Windows Server 2008 removing a failed domain controller](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663538.webp)


图 18-6. Windows Server 2008 移除故障域控制器

在 Windows Server 2003 下，这是一个三步过程。第一步是使用 *ntdsutil* 实用工具移除关联的元数据。以下示例显示了从 *emea.mycorp.com* 域中移除 RTP 站点中的 *DC3* 域控制器所需的命令：




```
C:\> ntdsutil
ntdsutil: metadata cleanup
metadata cleanup: connections
```


接下来，我们需要连接到域中包含我们要移除的 DC 的现有域控制器。在本例中，我们连接到 *DC2*：




```
server connections: connect to server dc2
Binding to dc2 ...
Connected to dc2 using credentials of locally logged on user.
server connections: quit
metadata cleanup: select operation target
```


现在我们需要选择域控制器所在的域。在本例中，它是 *emea.mycorp.com*：




```
select operation target: list domains
Found 2 domain(s)
0 - DC=mycorp,DC=com
1 - DC=emea,DC=mycorp,DC=com
select operation target: select domain 1
No current site
Domain - DC=emea,DC=mycorp,DC=com
No current server
No current Naming Context
```


接下来，我们必须选择域控制器所在的站点。在本例中，它是 RTP 站点：




```
select operation target: list sites
Found 4 site(s)
0 - CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=mycorp,DC=com
1 - CN=RTP,CN=Sites,CN=Configuration,DC=mycorp,DC=com
2 - CN=SJC,CN=Sites,CN=Configuration,DC=mycorp,DC=com
3 - CN=NYC,CN=Sites,CN=Configuration,DC=mycorp,DC=com
select operation target: select site 1
Site - CN=RTP,CN=Sites,CN=Configuration,DC=mycorp,DC=com
Domain - DC=emea,DC=mycorp,DC=com
No current server
No current Naming Context
```


列出站点中的服务器后，我们必须选择要移除的服务器。在本例中，它是 *DC3*：




```
select operation target: list servers in site
Found 3 server(s)
0 - CN=DC1,CN=Servers,CN=RTP,CN=Sites,CN=Configuration,DC=mycorp,DC=com
1 - CN=DC2,CN=Servers,CN=RTP,CN=Sites,CN=Configuration,DC=mycorp,DC=com
2 - CN=DC3,CN=Servers,CN=RTP,CN=Sites,CN=Configuration,DC=mycorp,DC=com
select operation target: select server 2
Site - CN=RTP,CN=Sites,CN=Configuration, DC=mycorp,DC=com
Domain - DC=emea,DC=mycorp,DC=com
Server - CN=DC3,CN=Servers,CN=RTP,CN=Sites,CN=Configuration,DC=mycorp,DC=com
   DSA object - CN=NTDS Settings,CN=DC3,CN=Servers,CN=RTP,CN=Sites,
                CN=Configuration,DC=mycorp,DC=com
   Computer object - CN=DC3,OU=Domain Controllers,DC=emea,DC=mycorp,DC=com
No current Naming Context
select operation target: quit
```

> **注意**：在 Windows Server 2003 Service Pack 1 中，此过程已大大简化；但是，您需要知道配置容器中域控制器( Domain Controller ,DC )`server` 对象的 `distinguishedName`。建议您直接遵循前面的指导删除失效的域控制器，因为这样出错的可能性更小。

最后一步将删除所选域控制器的元数据：




```
metadata cleanup: remove selected server
```


此时，您应收到 DC 已成功删除的确认信息。如果收到“找不到对象”的错误，可能是因为您曾尝试用 *dcpromo* 降级该服务器，而它已被删除。

如果您在运行 Windows Server 2003 SP1 之前版本的域控制器上执行此过程，则还需要从 Active Directory 中手动删除少量对象。有关详细信息，请参阅 MS 知识库文章 [216498](http://support.microsoft.com/kb/216498)。无论您运行的是哪个 Windows 版本，都需要手动删除配置分区中站点下的服务器对象。

#### 从备份还原

重建发生故障的域控制器( Domain Controller ,DC )的另一个方法是使用备份还原该计算机。这种方法称为非授权还原( Nonauthoritative Restore )，不需要从 Active Directory( AD ) 中删除任何对象。当你从备份还原 DC 时，最新更改会复制过来，使其保持最新。如果时间紧迫且备份文件立即可用，这将是更快的方法，因为只需通过网络复制最新更改（自上次备份以来所做的更改），而不是整个目录树。

以下是从备份还原的步骤：

1. 重新构建操作系统。重新安装操作系统以及你在域控制器上支持的任何其他应用程序。将该服务器保留为独立服务器或成员服务器。
2. 从备份还原。使用你的备份软件包至少将系统状态( System State )还原到该计算机上。在下一节配方 18.3 中，我们将逐步介绍 NT Backup 和 Windows Server Backup 实用工具，说明如何完成此操作。
3. 重新启动服务器并允许复制完成。如果发生故障的服务器拥有任何灵活单主机操作( Flexible Single Master Operation ,FSMO )角色，或曾是全局编录( Global Catalog ,GC )服务器，你可以配置新服务器来拥有这些角色。

也可以将某台计算机的备份还原到硬件不同的计算机上。这样做时，需要注意以下问题：

- 驱动器的数量和驱动器号应相同。
- 磁盘驱动器控制器和配置应相同。
- 所附加的卡，例如网卡、视频适配器和处理器，应相同。还原后，你可以安装新卡，它们应能被即插即用( Plug and Play )识别。
- 故障计算机的 *boot.ini* 将被还原，但它可能不兼容新硬件，因此你需要进行任何必要的更改。
- 如果计算机之间的硬件抽象层( Hardware Abstraction Layer ,HAL )不同，你可能会遇到问题。例如，如果故障计算机是单处理器，而新计算机是多处理器，则会出现兼容性问题。唯一的变通方法是从旧计算机复制 *Hal.dll*（它不作为系统状态的一部分包含在内），并将其放到新计算机上。这样做有一个明显缺点：它会使新的多处理器计算机表现得像单处理器计算机。

由于恢复到不同硬件时可能会出现许多问题，我们强烈建议你彻底测试并记录整个流程；请参阅微软知识库文章 [263532](http://support.microsoft.com/kb/263532)。在你试图恢复关键域控制器时，最不希望遇到的就是还要排查硬件兼容性问题。

#### 从媒体安装( Install from Media ,IFM )

在高度分布式环境中使用 Active Directory 时，一项常见挑战是：当提升新域控制器( Domain Controller ,DC)时，复制数据库初始副本所造成的影响。若数据库很大，在缓慢的广域网( Wide Area Network ,WAN )链路上执行此操作很容易耗时数天甚至数周。此过程运行期间，还可能会给 WAN 链路带来难以承受的负载，而这些链路原本可能已经满负荷运行，根本无力再承受复制整个 Active Directory 数据库的重担。

Windows Server 2003 引入了一项名为*从媒体安装*(IFM)的新功能，允许使用域中另一台域控制器的备份来提升域控制器。为完成提升而需要进行的唯一复制，是自获取该备份以来所发生的更改。备份映像既可以通过服务器消息块( Server Message Block ,SMB )或其他协议复制到域控制器，也可以使用商业快递以带外方式运送。以这种方式运送备份可大幅减轻为提升域控制器而对 WAN 造成的负担，在某些场景中还可显著加快提升过程。

从 IFM 媒体提升域控制器的过程在 Windows Server 2003 与 Windows Server 2008 域控制器之间存在很大差异。在 Windows Server 2008 上，必须使用 *ntdsutil* 创建 IFM 媒体，然后将 dcpromo 向导指向 *ntdsutil* 创建的文件夹。Windows Server 2003 域控制器要求将以 NT Backup 创建的系统状态备份( System State Backup )还原到“备用位置”，然后将 dcpromo 向导指向此文件夹。



##### 在 Windows Server 2003 上创建和使用 IFM 媒体

在 Windows Server 2003 上使用 IFM 与在较新版本的 Windows 上使用非常相似，但有几个关键区别：

- 必须使用由 NT Backup 创建的系统状态备份来创建 IFM 媒体。
- 要使用该备份，必须使用图 18-7中所示的“将文件还原到：备用位置”选项，将其还原到目标系统上。
- 必须通过运行 *dcpromo /adv* 直接以高级模式启动 *dcpromo*。




![Restoring to an alternate location](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663539.webp)


图 18-7. 还原到备用位置

##### 在 Windows Server 2008 及更高版本上创建并使用 IFM 媒体

创建安装媒体( Install From Media ,IFM )是一个简单直接的过程,如下例所示。系统会提示您选择要创建的媒体类型:

- 完全可写域控制器(不含 Sysvol)
- 完全可写域控制器(含 Sysvol)
- 只读域控制器(不含 Sysvol)
- 只读域控制器(含 Sysvol)

完全域控制器媒体与只读域控制器媒体的区别在于,后者不包含任何密码或其他机密信息。虽然您可以包含 Sysvol 的内容,但 dcpromo 向导在升级过程中不会使用这些内容来填充本地 Sysvol 共享:




```
ntdsutil: activate instance ntds
Active instance set to "ntds".
ifm: create full c:\ifmmedia
Creating snapshot...
Snapshot set {f15b79ab-9b0b-4845-9583-eb6c7a49bee9} generated successfully.
Snapshot {b1681552-114b-44b9-b547-9a1b15104907} mounted as C:\$SNAP_200807012230
_VOLUMEC$\
Snapshot {b1681552-114b-44b9-b547-9a1b15104907} is already mounted.
Initiating DEFRAGMENTATION mode...
     Source Database: C:\$SNAP_200807012230_VOLUMEC$\Windows\NTDS\ntds.dit
     Target Database: c:\ifmmedia\Active Directory\ntds.dit

                  Defragmentation  Status (% complete)

          0    10   20   30   40   50   60   70   80   90  100
          |----|----|----|----|----|----|----|----|----|----|
          ...................................................

Copying registry files...
Copying c:\ifmmedia\registry\SYSTEM
Copying c:\ifmmedia\registry\SECURITY
Snapshot {b1681552-114b-44b9-b547-9a1b15104907} unmounted.
IFM media created successfully in c:\ifmmedia
```

> **注意**：你还可以使用 Windows Server 2008 R2 及更新版本的 Windows Server Backup，通过图 18-16中所示的“备用位置”选项,从系统状态备份创建 IFM 介质。

在前面的示例中,我们创建了用于提升完整可写域控制器( Domain Controller ,DC)的 IFM 介质,其中不包含 Sysvol 的内容。图 18-8 显示了 *c:\ifmmedia* 的内容。




![Contents of IFM media](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663540.webp)


图 18-8. IFM 介质的内容



> **注意**：你可以使用在 32 位域控制器上创建的 IFM 介质来提升 64 位域控制器,反之亦然。但是,你不能使用只读域控制器( Read-Only Domain Controller ,RODC)介质来提升完整域控制器。

创建 IFM 介质后,你可以采用最便捷的方式将其复制到新的/目标域控制器。为了使用该介质,你需要以高级模式启动 dcpromo。在向导的第一页勾选“使用高级模式安装”复选框即可进入高级模式,如图 18-9所示。你也可以运行 *dcpromo /adv*。




![Starting dcpromo in advanced mode](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663541.webp)


图 18-9. 以高级模式启动 dcpromo

继续向导操作时,你将看到一个类似于图 18-10的页面,其中提供了使用 IFM 介质的选项。




![Using Install from Media](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663542.webp)


图 18-10. 使用从介质安装

向导完成后,它将修改源域控制器上 *ntds.dit* 数据库的备份,然后复制自创建数据库备份以来所做的任何更改。

### 18.3. 还原 Active Directory

没有人希望自己处于必须还原 Active Directory 的境地，但即便如此，你仍应为这种可能性做好准备。良好的规划和准备有助于确保：在需要执行还原的灾难场景中，你遇到的意外情况尽可能少。Active Directory 还原有几种不同的类型，下面我们逐一介绍。

#### 非权威还原( Nonauthoritative Restore )

非权威还原( Nonauthoritative Restore )是一种使用备份将域控制器( Domain Controller ,DC )恢复到已知良好状态的还原。随后，让复制( Replication )重新同步内容，以反映自备份以来 Active Directory 中的最新更改。我们之前描述用于处理 DC 故障的从备份还原方法，就是非权威还原的一个示例。该场景与这里要描述的场景的唯一区别在于，此过程针对的是当前作为域控制器正常运行的计算机；无需从头重建。在某些情况下，你可能希望执行类似的还原，但服务器已配置为域控制器。一个例子是，你希望撤销在某台特定域控制器上所做的某些更改。如果你能在域控制器复制之前及时将其从网络断开，就可以执行非权威还原，将其恢复到更改发生之前的已知状态。只要这些更改尚未复制到另一台服务器，这实际上就会使这些更改失效。

非权威还原只是还原 Active Directory，而不将任何数据标记为权威。这意味着，自备份以来发生的任何更改都将复制到已还原的服务器。此外，服务器上尚未复制的任何更改都将丢失。

要执行域控制器的非权威还原，需要将 DC 启动到目录服务还原模式( Directory Services Restore Mode ,DSRM )。必须这样做的原因是，域控制器处于活动状态时，会以独占模式锁定 Active Directory 数据库( *ntds.dit* )。这意味着其他进程无法修改其内容。若要通过覆盖 *ntds.dit* 文件进行还原，必须启动到 DS 还原模式( DS Restore Mode )，这是域控制器的安全模式版本。如果尝试还原正在运行的域控制器，将收到错误并且无法继续。

可以在系统初始启动期间按 F8 键进入 DS 还原模式。这样做之后，将看到 图 18-11 所示的屏幕。




![Directory Services Restore Mode](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663543.webp)


图 18-11. 目录服务还原模式

一旦收到登录提示，必须使用目录服务还原模式( Directory Services Restore Mode ,DSRM )管理员账户和密码登录。该账户的密码是在最初使用 *dcpromo* 将计算机提升到 Active Directory 时设置的。由于在 DSRM 下 Active Directory 处于离线状态，因此必须使用存储在本地安全账户管理器( Security Account Manager ,SAM )中的本地管理员账户登录，并且该账户只能在此模式下使用。如果不知道 DSRM 密码，请参阅 Microsoft 知识库文章 [322672](http://support.microsoft.com/kb/322672) 以获取重置密码的步骤。

##### 使用 NT Backup 进行还原

登录系统后，你需要启动 NT Backup 实用程序或其他备份软件。我们将逐步介绍如何使用 NT Backup 进行还原。在初始向导界面点击“下一步”后，你将看到如图 18-12所示的界面。




![Backup or restore options](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663544.webp)


图 18-12. 备份或还原选项

选择“还原文件和设置”，然后点击“下一步”。此时将进入选择还原内容的界面。你至少应还原系统状态，如有必要，也可以还原系统驱动器及其他驱动器。图 18-13展示了选择界面。




![Restore selection](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663545.webp)


图 18-13. 还原选择

完成选择并点击“下一步”后，将显示摘要界面，列出将要还原的内容。在完成之前，你需要点击“高级”按钮并浏览高级设置界面，确保交接点将被还原，如图 18-14所示。




![Restore junction points](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663546.webp)


图 18-14. 还原交接点

点击“完成”以启动还原过程。还原完成后，你需要重启进入正常模式。此时，域控制器( Domain Controller ,DC )将与其复制伙伴进行最新更改的复制。留出足够时间让复制完成，然后监控服务器并检查事件日志，以确保其正常运行。

##### 使用 Windows Server Backup 进行还原

可以通过任务窗格中的"恢复"( Recover )选项从系统状态备份( System State Backup )执行还原。首先,在恢复向导( Recovery Wizard )中,找到包含要用于还原的备份的驱动器或网络共享。接下来,在日历中选择备份的创建日期,并在右侧的下拉列表中选择时间,如图 18-15 所示。




![Selecting a backup to restore from with Windows Server Backup](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663547.webp)


图 18-15. 选择要用于 Windows Server Backup 还原的备份

**如果需要对 Sysvol 执行权威还原( Authoritative Restore ),请选中"执行 Active Directory 文件的权威还原"( Perform an authoritative restore of Active Directory files )选项。与屏幕上显示的文本不同,该选项实际上只会对 Sysvol 执行权威还原,如图 18-16 所示。**




![System State Recovery location](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663548.webp)


图 18-16. 系统状态恢复位置

完成向导后,需要重新启动并进入正常模式。此时,域控制器( Domain Controller ,DC )将与其复制伙伴一起复制最新更改。请留出足够时间等待复制完成,然后监视服务器并检查事件日志,以确认其运行正常。如果需要执行权威还原,请在重新启动之前继续阅读本章的后续内容。

#### 部分权威还原( Partial Authoritative Restore )

在某些情况下,你可能需要还原 Active Directory 中的数据。到目前为止,我们展示的还原域控制器( Domain Controller ,DC )和执行非权威还原( Nonauthoritative Restore )的示例,其目的都只是让域控制器重新启动并运行。不过,在某些特定情况下,你可能需要执行权威还原( Authoritative Restore )。以下是几个示例:

- 意外删除了重要对象
- 意外删除了整个子树( Subtree )
- 对象或整个目录损坏
- 撤销某些对象的添加或修改

在所有这些场景中,你都可以通过部分权威还原( Partial Authoritative Restore )来撤销更改。如果整个目录损坏,则需要执行完整权威还原( Complete Authoritative Restore ),我们稍后将简要介绍。

> **警告**：无法对架构命名上下文( Schema Naming Context )执行授权还原( Authoritative Restore )。若要回滚架构，必须从头开始重建整个林( Forest )，或者使用早于架构修改的一组系统状态备份( System State Backup )来重建整个林。在几乎所有环境中，此选项的可行性都很低。

执行授权还原有两种选择。您可以找到一台具有所需数据的域控制器( Domain Controller ,DC )——这可能是因为更改尚未复制到该 DC——或者从备份还原数据。无论哪种情况，都需要按 非授权还原( Nonauthoritative Restore ) 一节所述，启动进入 DS 还原模式( DS Restore Mode )。同样，这是必要的，因为当 DC 处于运行状态时，Active Directory 数据库会被锁定，无法进行任何修改。进入 DS 还原模式后，如有必要，可按前文所述从备份还原。

此时，您需要在离线 Active Directory 数据库中将希望还原的数据标记为权威。这可通过 ntdsutil 实用工具完成。如下所示的 `authoritative restore` 菜单下有几个选项可供选择：

```
ntdsutil: authoritative restore
authoritative restore: ?
 ?                             - Show this help information
 Create ldif file(s) from %s   - Creates ldif file(s) using specified
                                 authoritatively restored objects list
                                 to recreate back-links of those objects.
 Help                          - Show this help information
 List NC CRs                   - Lists Partitions and cross-refs.  You need
                                 the cross-ref of a Application Directory
                                 Partition to restore it.
 Quit                          - Return to the prior menu
 Restore database              - Authoritatively restore entire database
 Restore database verinc %d    - ... and override version increase
 Restore object %s             - Authoritatively restore an object
 Restore object %s verinc %d   - ... and override version increase
 Restore subtree %s            - Authoritatively restore a subtree
 Restore subtree %s verinc %d  - ... and override version increase
 authoritative restore:
```

执行部分还原( Partial Restore )时，可以使用 *restore object %s* 子命令还原单个对象，或使用 *restore subtree %s* 子命令还原整个对象子树。在以下示例中，我们将还原 *jsmith* 用户对象：

```
authoritative restore: restore object cn=jsmith,ou=sales,dc=mycorp,dc=com
Opening DIT database... Done.
 The current time is 08-10-05 00:15.25.
Most recent database update occured at 08-09-05 21:48.51.
Increasing attribute version numbers by 100000.
 Counting records that need updating...
Records found: 0000000001
Done.
  Found 1 records to update.
 Updating records...
Records remaining: 0000000000
Done.
Successfully updated 1 records.
 The following text file with a list of authoritatively restored
objects has been created in the current working directory:
        ar_20050810-001525_objects.txt
 One or mofre specified objects have back-links in this domain.
The following LDIF files with link restore operations have
 been created in the current working directory:
        ar_20050810-001525_links_ad.loc.ldf
 Authoritative Restore completed successfully.
authoritative restore: quit
```

如您所见，*ntdsutil* 会将对象的版本号增加 100,000。这就是在数据库中将其标记为权威的方式。重新启动进入正常模式后，域控制器会与其复制伙伴( Replication Partner )进行核对，并确定 *jsmith* 用户对象的版本高于其伙伴上的版本。然后，它会将该对象复制到这些伙伴；同样，伙伴上已更新的所有其他对象也会复制到该服务器。

> **注意**：如果出于某种原因，100,000 的自动增量不足以满足对象需求，你可以使用备用子命令 *restoreobject %s verinc %d*，其中 *%d* 表示版本递增的量（此数值乘以自备份以来的天数）。

根据 *ntdsutil* 版本的不同，你可能会看到与此处不同的结果。该实用程序在 Windows Server 2003 SP1 版本中进行了重大更改；例如，它现在会创建一个 LDF 文件，该文件将包含同一域中附加到对象的所有链接属性值，这允许恢复组成员资格和其他链接属性。



#### 完整权威还原

还原整个 Active Directory 数据库在概念上类似于还原单个对象或子树，不同之处在于你要还原所有对象，但架构除外。应谨慎执行此操作，并且仅在极端情况下进行。我们强烈建议你在实验室环境中进行测试，以确保你正确记录了过程，并且你确实具有执行还原的经验。

同样，要运行还原命令，你必须处于目录服务还原模式(Directory Services Restore Mode, DSRM)，并且需要如前所述从备份中还原系统。以下是 *restore database* 子命令的示例输出：




```
authoritative restore: restore database
Opening DIT database... Done.
  The current time is 08-10-05 00:39.46.
Most recent database update occured at 08-09-05 21:48.51.
Increasing attribute version numbers by 100000.
 Counting records that need updating...
Records found: 0000001725
Done.
  Found 1725 records to update.
 Updating records...
Records remaining: 0000000000
Done.
  Successfully updated 1725 records.
 The following text file with a list of authoritatively
restored objects has been created in the current working directory:
        ar_20050810-003946_objects.txt
 One or more specified objects have back-links in this domain.
The following LDIF files with link restore operations have
 been created in the current working directory:
        ar_20050810-003946_links_ad.loc-Configuration.ldf
        ar_20050810-003946_links_ad.loc.ldf
 Authoritative Restore completed successfully.
 authoritative restore: quit
```


如果你必须执行完整的权威还原，那么假设域控制器上发生了灾难性事件，导致某种形式的全局、不可修复的 Active Directory 损坏。最安全的做法可能是为每个域还原一个域控制器并重建其余部分。你需要手动从 Active Directory 中删除每个重建的域控制器，然后重新提升每个域控制器。再次强调，这只是一个建议，在采取如此极端的措施之前，必须彻底考虑每种情况。如果你完全理解所涉及的过程和程序并加以实践，你肯定会更好地准备应对这种可能发生的情况。有关 Active Directory 林恢复最佳实践的 Microsoft 文档，请参阅[此网站](http://bit.ly/Yg3M8U)。

### 18.4. 使用快照

Windows Server 2008 引入的一项 Active Directory 功能便是*快照*( Snapshot )的概念。借助快照,你可以创建 Active Directory 数据库的时间点副本。此功能使用卷影复制( Volume Shadow Copy ,VSS)服务来创建快照。创建快照后,你可以使用 *dsamain* 命令行实用工具挂载它,并使用 *ldp*、活动目录用户和计算机( Active Directory Users and Computers ,ADUC)或任何其他支持 LDAP 协议的工具,像浏览实时 Active Directory 数据库一样浏览它。

这项新功能的好处数不胜数,以下仅列举一些思路:

- 在修改前查看权限或其他设置,以备需要回滚
- 导出被误修改的对象或值,然后将其重新导入生产目录
- 确定从哪个备份执行还原
- 使用第三方工具还原完整对象

使用 *ntdsutil* 命令行实用工具创建快照是一个简单的过程:




```
C:\> ntdsutil
ntdsutil: snapshot
snapshot: activate instance ntds
Active instance set to "ntds".
snapshot: create
Creating snapshot...
Snapshot set {e73b71cd-7e2b-40ee-8871-69575f4b1e66} generated successfully.
```


创建快照后,你可以挂载它并使其可供 LDAP 客户端使用。挂载快照可以通过指定上一步生成的 GUID,或者从列表中选择快照来完成。在本示例中,我们从列表中选择快照:




```
snapshot: list all
 1: 2008/06/30:22:44 {e73b71cd-7e2b-40ee-8871-69575f4b1e66}
 2:   C: {c8bc59c0-f20b-4bac-a12a-ab6eab737f0c}

snapshot: mount 1
Snapshot {c8bc59c0-f20b-4bac-a12a-ab6eab737f0c} mounted as
C:\$SNAP_200806302244_VOLUMEC$\
```


将快照挂载到文件系统后,你可以使用 *dsamain* 实用工具挂载 Active Directory 数据库的快照版本,并使其可通过 LDAP 访问。*dsamain* 要求你提供要挂载的数据库路径以及侦听端口号。如果仅指定 LDAP 端口,*dsamain* 将自动使用后续三个端口用于 LDAP over SSL (LDAPS)、全局编录( Global Catalog ,GC)以及全局编录 SSL 连接。因此,如果为 LDAP 指定端口 10389,则端口 10390、10391 和 10392 也将被使用。在此场景中挂载数据库的命令为:




```
 dsamain -dbpath C:\$SNAP_200806302244_VOLUMEC$\Windows\NTDS\ntds.dit
 -ldapport 10389
```


然后,你可以使用 LDP 或任何 LDAP 客户端连接到端口 10389,如图 18-17所示。




![Connecting to a mounted snapshot](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663549.webp)


图 18-17. 连接到已挂载的快照

你也可以使用活动目录用户和计算机连接到已挂载的快照:

1. 启动 ADUC。
2. 右键单击该域,然后选择"更改域控制器"。
3. 选择"此域控制器或 AD LDS 实例"。
4. 单击"<在此处键入目录服务器名称[:端口]>"。

5. 输入域控制器名称或本地主机名，如图 18-18 所示，然后单击“确定”。

![Connecting to a mounted snapshot with ADUC](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663550.webp)

图 18-18. 使用 ADUC 连接到已装载的快照

完成快照操作后，需停止 *dsamain* 实例并卸载快照。要停止 *dsamain* 实例，只需在命令窗口中按 Ctrl-C，它就会退出。卸载快照与装载它的过程相似：

```
C:\> ntdsutil
ntdsutil: snapshot
snapshot: list all
 1: 2008/06/30:22:44 {e73b71cd-7e2b-40ee-8871-69575f4b1e66}
 2:   C: {c8bc59c0-f20b-4bac-a12a-ab6eab737f0c} C:\$SNAP_200806302244_VOLUMEC$\

snapshot: unmount 1
Snapshot {c8bc59c0-f20b-4bac-a12a-ab6eab737f0c} unmounted.
```

总之，活动目录快照允许您在域控制器上创建活动目录数据库的时间点副本，并通过 LDAP 装载以便并行访问。有关此功能的更多信息，请参阅[此网站](http://bit.ly/15VP7PR)上的指南。

### 18.5. Active Directory 回收站( Active Directory Recycle Bin )

管理员面临的最常见 Active Directory 灾难之一，就是意外删除对象，或者更常见的是意外删除多个对象。尽管这类灾难完全可以预防，但它仍屡屡发生。长期以来，众多第三方厂商一直提供可供购买的工具，使您无需通过传统的系统状态备份( System State Backup )进行恢复，即可将对象或属性值还原到目录中。Windows Server 2008 R2 引入了 Active Directory 回收站，这是 Microsoft 针对已删除对象恢复提供的解决方案。

在 Active Directory 回收站出现之前，删除对象的一个副作用是，该对象的大部分属性都会被删除，因此对墓碑对象( tombstone object )执行取消删除或重新激活时，对象被删除时设置的多数属性都会缺失。只有那些在架构( schema )中标记为在墓碑上保留的属性才会被保留下来。虽然大多数属性值可以保留，但链接属性( linked attributes )（例如组成员身份( group membership )）无法保留在墓碑上。

#### 已删除对象生命周期

当从 Active Directory 中删除某个对象时,会发生一系列变化。最关键的一点是,为了确保删除操作在整个林( Forest )内完成复制,该对象在相当长的时间内并不会真正从 Active Directory 数据库中清除。处于这种状态的对象称为*墓碑( Tombstone )*。如果未启用 Active Directory 回收站( Active Directory Recycle Bin ),对象被删除后在数据库中保留的这段时间称为*墓碑生存时间( Tombstone Lifetime )*。一旦超过墓碑生存时间,每个域控制器( Domain Controller ,DC )上的垃圾收集( Garbage Collection )进程就会从数据库中删除这些记录。图 18-19 展示了未启用回收站时,从 Active Directory 中删除的对象的生命周期。




![Deleted object lifecycle (without Active Directory Recycle Bin)](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663551.webp)


图 18-19. 已删除对象的生命周期(未启用 Active Directory 回收站)

启用 Active Directory 回收站后,已删除对象在成为墓碑之前,会先进入*已删除对象状态( Deleted Object State )*,如图 18-20 所示。对象处于已删除状态时,其所有属性以及与对象之间的所有链接都会保留。与启用回收站之前删除对象的情形类似,`isDeleted` 属性会被设置为 `TRUE`,并且对象会被移动到 Deleted Objects 容器。

> **注意**：默认情况下，垃圾回收( Garbage Collection )每隔 12 小时在每个域控制器( Domain Controller ,DC)上运行。垃圾回收期间，会检查墓碑( Tombstone )，以确定其删除时间是否超过墓碑生存时间( Tombstone Lifetime )。如果超过，则删除这些记录。

可以通过使用 *ldp* 或 *admod* 之类的工具，在给定域控制器上将 `doGarbageCollection` 操作属性( Operational Attribute )设置为 `1`，从而按需触发垃圾回收运行。例如，可使用以下 *admod* 命令在服务器 *DC01* 上运行垃圾回收：




```
admod -h dc01 -sc gc
```





![Deleted object lifecycle with Active Directory Recycle Bin enabled](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663552.webp)


图 18-20. 启用 Active Directory 回收站( Active Directory Recycle Bin )后的已删除对象生命周期

已删除对象生存时间( Deleted Object Lifetime )过后，垃圾回收会将该对象转换为已回收对象( Recycled Object )，剥离所有未在墓碑上标记为保留的属性，并将 `isRecycled` 属性设置为 `TRUE`。已回收对象状态就是以前所谓的墓碑。最后，一旦已回收对象生存时间( Recycled Object Lifetime )（以前称为墓碑生存时间）过后，垃圾回收就会从数据库中物理删除该记录。



> **注意**：与墓碑不同，已回收对象无法重新激活。若要在对象进入已回收状态后恢复该对象，必须从备份对对象执行权威还原，而该备份是在对象仍处于已删除状态时创建的。



#### 启用回收站

Active Directory 回收站需要 Windows Server 2008 R2 林功能级别( Forest Functional Level ,FFL )（级别 4）或更高。满足林功能级别要求后，即可启用回收站可选功能( Optional Feature )。启用 Active Directory 回收站最简单的方法是使用 PowerShell。



> **警告**：启用 Active Directory 回收站后，便无法将其禁用。请确保已在测试环境中测试启用回收站的影响，包括与 Active Directory 集成的工具。通常受启用回收站影响的工具包括使用 LDAP DirSync 将 AD 中的更改与本地数据库同步的工具。

Microsoft Identity Lifecycle Manager (ILM) 和某些版本的 Office365 DirSync 是受回收站影响的两个应用程序示例。

在已安装适用于 Windows PowerShell 的 Active Directory 模块的计算机上，运行以下两个命令：




```
Enable-ADOptionalFeature -Identity 'CN=Recycle Bin Feature,
CN=Optional Features,CN=Directory Service,CN=Windows NT,
CN=Services,CN=Configuration,'<Forest Root DN>'
-Scope ForestOrConfigurationSet
-Target '<Forest DNS Name>' `'CN=Recycle Bin Feature, ` CN=Optional Features, `
CN=Directory Service,CN=Windows NT,CN=Services,CN=Configuration,
<Forest Root DN>' -Scope ForestOrConfigurationSet -Target '<Forest DNS Name>'
```





```
WARNING: Enabling 'Recycle Bin Feature' on 'CN=Partitions,CN=Configuration,
<Forest Root DN>' is anirreversible action! You will not be able to disable
'Recycle Bin Feature' on 'CN=Partitions,CN=Configuration,<Forest Root DN>'
if you proceed.
```


如果要为 *contoso.com* 林启用回收站，请将示例中的 *<Forest Root DN>* 替换为 `DC=contoso,DC=com`，并将 *<Forest DNS Name>* 替换为 `contoso.com`。

> **注意**：您也可以使用 Windows Server 2012 版本的活动目录管理中心( Active Directory Administrative Center )启用活动目录回收站( Active Directory Recycle Bin )。只需右键单击林根域，然后单击"启用回收站"。

启用回收站后，由于会为林中的每个对象更新 `isRecycled` 属性，因此环境中可能会出现一些额外的复制流量。此外，之前处于墓碑状态的对象将进入回收状态，不再支持复活。最后，启用回收站后，基础结构主机 FSMO 角色不再需要执行任何工作，因此其位置不再重要。有关 FSMO 角色的详细信息，请参阅第 2 章。

#### 恢复已删除对象

从回收站中恢复对象，即取消删除对象，可能是一个棘手的过程。如果您要恢复整个对象树，例如某个组织单位( Organizational Unit ,OU )被删除的情况，您需要按照正确的顺序取消删除对象。也就是说，在父对象恢复之前，无法恢复子对象。

幸运的是，微软提供了多种工具来简化这一过程。如果您使用的是 Windows 8 远程服务器管理工具( Remote Server Administration Tools ,RSAT )，可以使用活动目录管理中心( Active Directory Administrative Center ,ADAC )进行恢复。如果您使用的是 Windows Server 2008 R2 RSAT 工具，或者需要更精细的操作，可以使用 PowerShell。

##### 使用 ADAC

使用 ADAC 从回收站中恢复单个对象是一个非常直接的过程。一旦启用了回收站，您将在 ADAC 中域的根目录下看到一个“已删除对象”容器。找到您想要恢复的对象并右键单击它。您可以选择“还原”将对象恢复到其原始位置，或者，如果您想将对象恢复到不同的 OU，请选择“还原到”。使用 ADAC 的缺点在于它不支持树恢复的概念。如果您需要恢复 OU 层次结构，您将需要使用 PowerShell 和下一节中讨论的特殊树恢复脚本。

##### 使用 PowerShell

使用 PowerShell 从回收站恢复对象时,你最需要熟悉的 cmdlet 是 *Restore-ADObject*。要恢复一个或多个对象,首先需要识别它们并将其提供给 *Restore-ADObject* cmdlet。你可以提供要恢复的特定对象的 DN(或 GUID),也可以将 *Get-ADObject* cmdlet 的结果通过管道传递给 *Restore-ADObject*。

熟悉这些选项最简单的方法是通过几个示例。在第一个示例中,我们将恢复用户 *gwashington* 的帐户。我们能够根据先前的相对可分辨名称( Relative Distinguished Name ,RDN)定位该用户。对于用户(或计算机)而言,RDN 是对象 DN 中的 `CN=` 部分。对于组织单位( Organizational Unit ,OU)而言,RDN 是对象 DN 中的 `OU=` 部分。我们按如下方式恢复该用户对象:




```
Get-ADObject -IncludeDeletedObjects -LdapFilter `
"(&(objectClass=user)(msDS-lastKnownRDN=gwashington))" | Restore-ADObject
```


再考虑另一个示例:你不小心删除了一个包含多个对象的 OU。在这种情况下,你需要先恢复该 OU,然后再恢复其中的对象。在本示例中,我们将恢复一个名为 Presidents 的 OU,如图 18-21所示,然后恢复该 OU 中的所有对象。




![Hierarchy for object recovery](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663553.webp)


图 18-21. 对象恢复的层次结构

为了恢复已删除的 Presidents OU 及其中的所有对象,我们使用以下 PowerShell 命令(每条命令一行):




```
Get-ADObject -IncludeDeletedObjects -LdapFilter ` "(&(objectClass=organizationalUnit)
(msDS-lastKnownRDN=Presidents))" `
| Restore-ADObject

Get-ADObject -IncludeDeletedObjects -LdapFilter `
"(&(objectClass=user)(lastKnownParent=OU=Presidents,
OU=People,DC=contoso,DC=com))"
| Restore-ADObject
```


如果你在恢复对象的父对象之前尝试恢复该对象,将会收到类似如下的错误:




```
Restore-ADObject : The operation could not be performed because the object's
parent is either uninstantiated or deleted
```


幸运的是,*Restore-ADObject* cmdlet 提供了许多参数,如表 18-2所示,使你能够修改该 cmdlet 的默认行为。



表 18-2. Restore-ADObject 参数

| *Parameter*  | Description                                                  |
| ------------ | ------------------------------------------------------------ |
| *Identity*   | 指定要还原的对象。你可以提供已删除对象(位于“已删除对象”容器中)的 DN,也可以提供该对象的 GUID。 |
| *NewName*    | 指定对象还原后要使用的新 RDN。如果未提供此值,则改用 `msDS-lastKnownRDN` 值。例如,当有人手动重新创建了同名 OU 之后,你又要恢复已删除的该 OU 时,会发现此参数很有用。 |
| *TargetPath* | 指定将对象还原到目录中的哪个位置。如果对象的父级已不存在,或者你希望将对象还原到新位置,则应在此处提供该位置的 DN。如果未提供值,则改用已还原对象的 `lastKnownParent` 值。 |

与可能发生的误删除场景相比,我们目前看到的示例都微不足道——在那些场景中,复杂层次的 OU 和对象可能已被删除。此类层次结构必须自上而下进行还原。手动执行这一操作,即便再顺利也会既复杂又耗时。所幸,Microsoft 提供了一个脚本 *Restore-ADTree.ps1*,可用于恢复某一层次结构中的多个对象。此脚本可从[此链接](http://bit.ly/16iiqy7)获取。

例如,如果 图 18-21 中所示的 People OU 被意外删除,你可以使用 *Restore-ADTree.ps1* 按如下方式恢复该层次结构:




```
Restore-ADTree.ps1 -lastKnownRDN "People" -lastKnownParent "dc=contoso,dc=com"
```

> **注意**：如果运行脚本时收到类似以下错误,则需要修改 PowerShell 执行策略( Execution Policy )。




```
File C:\Restore-ADTree.ps1 cannot be loaded because the execution of 
scripts is disabled on this system. Please see 
"get-help about_signing" for more details.
```


要将执行策略设置为 `RemoteSigned`,请运行以下命令:




```
Set-ExecutionPolicy -ExecutionPolicy:RemoteSigned
```


有关执行策略的详细信息,请参阅[此网站](http://bit.ly/10af0dc)。

### 18.6. FSMO 恢复

FSMO 角色已在第 2 章中描述。这些角色在 Active Directory 中被视为特殊角色，因为它们由林或域内的单个域控制器( Domain Controller ，DC )承载。Active Directory 的架构具有高度冗余性，FSMO 角色除外。正因如此，你需要制定一项计划，以应对 FSMO 故障。

如果域控制器能够检测到自身即将关闭，并优雅地将其持有的任何 FSMO 角色转移到其他域控制器，那将是一项非常出色的功能，但现实中并非如此运作。在无法优雅转移 FSMO 角色的情况下，你必须执行手动转移。要手动转移 FSMO 角色，你需要打开相应的 Active Directory 管理单元，打开 FSMO 属性页，选择新的角色所有者，然后执行转移。以下是 FSMO 角色列表以及可用于将每个角色转移到另一台域控制器的相应管理单元：

- 架构主控( Schema Master )：Active Directory 架构
- 域命名主控( Domain Naming Master )：Active Directory 域和信任关系
- RID 主控( RID Master )：Active Directory 用户和计算机
- PDC 仿真器( PDC Emulator )：Active Directory 用户和计算机
- 基础结构主控( Infrastructure Master )：Active Directory 用户和计算机

> **注意**：你可以使用命令行工具 *netdom* 通过单条命令查询给定域的所有 FSMO：




```
netdom query fsmo /domain:domainname
```


当某个 FSMO 角色所有者宕机且无法恢复联机时，你便无法再转移该角色，而必须“强行夺取”。Windows Server 2008 及更高版本的域控制器( Domain Controller ,DC )在执行元数据清理( Metadata Cleanup )时，会自动夺取由某台域控制器持有的所有 FSMO 角色。不过，如果你希望明确指定角色的夺取目标，仍须手动执行此操作。遗憾的是，你无法像转移角色那样使用 Active Directory 管理单元( Snap-in )来夺取 FSMO 角色。要夺取 FSMO 角色，你需要使用 *ntdsutil* 实用工具。下面我们将逐步讲解用于夺取 FSMO 角色的 *ntdsutil* 命令。请注意，由于输出宽度所限，部分文本会换行显示到下一行。

首先进入 *ntdsutil* 交互模式，并查看 *roles* 命令的选项：




```
C:\> ntdsutil
ntdsutil: roles
fsmo maintenance: ?
 ?                             - Show this help information
 Connections                   - Connect to a specific domain controller
 Help                          - Show this help information
 Quit                          - Return to the prior menu
 Seize domain naming master    - Overwrite domain role on connected server
 Seize infrastructure master   - Overwrite infrastructure role on connected 
                                 server
 Seize PDC                     - Overwrite PDC role on connected server
 Seize RID master              - Overwrite RID role on connected server
 Seize schema master           - Overwrite schema role on connected server
 Select operation target       - Select sites, servers, domains, roles and
                                 naming contexts
 Transfer domain naming master - Make connected server the domain naming master
 Transfer infrastructure master - Make connected server the infrastructure master
 Transfer PDC                  - Make connected server the PDC
 Transfer RID master           - Make connected server the RID master
 Transfer schema master        - Make connected server the schema master
```


现在必须连接到我们希望夺取角色的目标域控制器。在本例中，我们将连接到 *DC1*：




```
fsmo maintenance: connections
server connections: connect to server dc1
Binding to dc1 ...
Connected to dc1 using credentials of locally logged on user.
server connections: quit
```


此时，我们可以将任何可用的 FSMO 角色转移或夺取到 *DC1* 域控制器。在下一个示例中，我们将尝试夺取架构主机( Schema Master )角色。当前架构主机为 *DC2*。如果我们尝试执行夺取，而 *DC2* 仍正常运行，实际上会以平稳方式将该角色转移到 *DC1*。如果 *DC2* 未运行，则会执行强行夺取，如下方输出所示（请注意，某些行可能因长度过长而换行）：




```
fsmo maintenance: seize schema master
Attempting safe transfer of schema FSMO before seizure.
ldap_modify_sW error 0x34(52 (Unavailable).
Ldap extended error message is 000020AF: SvcErr: DSID-03210300, problem 5002
(UNAVAILABLE), data 1753
 Win32 error returned is 0x20af(The requested FSMO operation failed. The current
FSMO holder could not be contacted.)

Depending on the error code this may indicate a connection,
ldap, or role transfer error.
Transfer of schema FSMO failed, proceeding with seizure ...
Server "dc1" knows about 5 roles
Schema - CN=NTDS Settings,
CN=DC1,CN=Servers,CN=RTP,CN=Sites,
CN=Configuration,
DC=mycorp,DC=com
Domain - CN=NTDS Settings,CN=DC1,CN=Servers,CN=RTP,CN=Configuration, 
DC=mycorp,DC=com
PDC - CN=NTDS Settings,CN=DC1,CN=Servers,CN=RTP,CN=Sites,CN=Configuration,
DC=mycorp,DC=com
RID - CN=NTDS Settings,CN=DC1,CN=Servers,CN=RTP,CN=Sites,CN=Configuration,
DC=mycorp,DC=com
Infrastructure - CN=NTDS Settings,CN=DC1,CN=Servers,CN=RTP,CN=Sites,
CN=Configuration,DC=mycorp,DC=com
```


请注意，系统会首先尝试连接当前角色所有者；如果无法连接，*ntdsutil* 便会执行强行夺取。

这个奇特的 *ntdsutil* 命令有一项不错的功能：既可像刚才所示那样以交互模式运行，也可以从单条命令行运行。若要用单条命令行完成同样的夺取操作，可以使用：




```
C:\> ntdsutil roles conn "connect to server dc1" q "seize schema master" q q
```


根据你的需求，你可以编写一个批处理脚本( Batch Script )，提示输入要夺取的角色以及要转移或夺取该角色的目标域控制器。当进入关键时刻、需要快速夺取角色，而又不想翻阅本书查找所有命令时，这会大有帮助。

### 18.7. 可重启的目录服务

Windows Server 2008 引入了像普通 Windows 服务一样启动和停止 Active Directory 的功能。这允许您在不重启域控制器的情况下执行大多数离线操作。当 Active Directory 停止时，它将不会响应登录请求。如果域控制器承载了 Active Directory 集成 DNS 区域，它也将不会响应对这些区域的查询。当 Active Directory 服务停止时，您可以执行本章中概述的所有离线任务，但从备份还原除外。还原仍然需要引导进入目录服务还原模式。

一旦您停止了 Active Directory 服务，如果另一个域控制器可用于处理请求，您可以使用域凭据登录到该域控制器。如果没有其他域控制器可用于处理请求，您将无法登录。如果您希望可以选择使用目录服务还原模式密码，则必须修改注册表。此配置更改在接下来的侧边栏“修改 DSRM 登录行为”中概述。

修改 DSRM 登录行为

默认情况下，您必须使用域帐户登录到已停止 Active Directory 服务的域控制器。

要更改此行为，您需要在 `HKLM\System\CurrentControlSet\Control\Lsa` 下创建或修改 `REG_DWORD DSRMAdminLogonBehavior` 注册表值。

此注册表值有三个可能的值：

表 18-3.

| 值   | 描述                                                         |
| ---- | ------------------------------------------------------------ |
| 0    | 您只能使用域帐户登录到域控制器，这要求另一个域控制器可用于处理请求。这是默认设置。 |
| 1    | 仅当 Active Directory 服务停止时，您可以使用域帐户或目录服务还原模式帐户登录到域控制器。 |
| 2    | 无论 Active Directory 服务是停止还是启动，您都可以使用目录服务还原模式帐户登录到域控制器。 |

如果您域中只有一个域控制器，或者预计会出现无法联系另一个域控制器的情况，则必须将此注册表值设置为 `1`，否则您将无法以 DS 还原模式登录到域控制器。通常，我们建议所有部署都使用值 `1`。

> **注意**：如果你尝试登录到一台目录服务( Directory Service )已停止的 Windows Server 2008 域控制器( Domain Controller ,DC)，并且在使用目录服务还原模式( Directory Services Restore Mode ,DSRM)凭据时登录失败，请确保你并未尝试登录到域。如果需要显式指定本地管理员账户，请在登录屏幕上单击“切换用户”，并指定用户名 *.\administrator*。

若要停止 Active Directory 服务，请转到“开始”→“运行”→**`services.msc`**，以打开“服务”MMC 管理单元，右键单击“Active Directory 域服务( Active Directory Domain Services ,AD DS)”，然后选择“停止”。系统将提示你同时停止依赖服务，如图 18-22所示。也可以在命令提示符下运行 *net stop ntds* 来停止 Active Directory。

![Stopping dependent services](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663554.webp)

图 18-22. 停止依赖服务

重新启动 AD DS 服务后，需要手动启动每个依赖服务。

### 18.8. DIT 维护

使用 *ntdsutil* 实用工具，可以检查 Active Directory 数据库的完整性和语义，并回收空白空间，这能大幅减小目录信息树( Directory Information Tree ,DIT)的大小。此外，就像应轮换林( Forest )中的管理员帐户密码一样，也应定期更改目录服务还原模式( Directory Services Restore Mode ,DSRM)的管理员密码。你甚至可能需要更频繁地执行此操作，具体取决于是否有人员离开团队后不应再知道该密码。

遗憾的是，在 Windows Server 2003 及更早版本的域控制器( Domain Controller ,DC)上完成所有这些任务（更改 DSRM 管理员密码除外）时，必须将域控制器启动到 DSRM。这意味着必须为计算机安排停机时间。此外，要使用 DSRM，需要控制台访问权限，可以是通过物理方式在计算机旁，也可以通过带外访问，例如使用 HP Integrated Lights-Out (iLO) 连接。

如果无法访问计算机的物理控制台，在修改 DC 的启动配置后，也可以通过远程桌面( Remote Desktop )连接。如果需要将 Windows Server 2008 或更高版本的域控制器配置为自动启动到 DSRM，则需要使用 *bcdedit* 命令行实用工具重新配置域控制器的启动设置。这是一个三步过程。首先，发出以下命令：

bcdedit /copy {current} /d “DC-DS Restore Mode”

该工具将输出类似下面的 GUID 响应：

```
The entry was successfully copied to {49fa7976-5065-11dd-ae21-000c291a8e6c}
```

bcdedit /set *`{49fa7976-5065-11dd-ae21-000c291a8e6c}`* safeboot dsrepair

bcdedit /default *`{49fa7976-5065-11dd-ae21-000c291a8e6c}`*

重新启动域控制器时，它将启动到 DSRM。然后，需要将域控制器的默认启动选项改回原始设置。这是一个两步过程。首先，发出以下命令：

**`bcdedit /enum`**

这将输出所有启动管理器选项的列表。找到正常 Windows 实例的 GUID，然后发出以下命令：

**`bcdedit /default`** *`<guid of normal Windows instance>`*

#### 检查目录信息树( Directory Information Tree ,DIT)的完整性

您可以对 DIT 文件执行多种检查，以确定其是否健康。我们将展示的第一项检查会验证 DIT 文件的完整性。完整性检查( Integrity Check )会在低级别检查数据库，以确定是否存在任何二进制损坏。它会扫描整个文件，因此根据 DIT 文件的大小，完成检查可能需要一段时间。虽然速度会因多种因素而有很大差异，但我们看到一些估计表明它每小时可以检查大约 

#### 回收空间

如果域控制器( Domain Controller ,DC)的磁盘空间即将耗尽,或者自提升域控制器以来删除了大量对象,您可能需要对该目录信息树( Directory Information Tree ,DIT )文件执行脱机碎片整理。您可能见过记录到目录服务( Directory Services )事件日志中的联机碎片整理事件,其中包括事件 700(表示联机碎片整理即将开始)和事件 701(表示联机碎片整理已完成)。默认情况下,联机碎片整理进程每天运行两次,用于合并 DIT 文件内的空闲空间,但它不会回收 DIT 文件占用的任何磁盘空间。若要回收磁盘空间,必须执行脱机碎片整理。有关如何确定 DIT 中可用空闲空间量的信息,请参阅下文即将介绍的侧栏配置可用数据库空间的日志记录。

> **注意**：如果将 Windows 2000 域控制器就地升级到 Windows Server 2003，*ntds.dit* 中可能会产生大量可用空间。这是因为 Windows Server 2003 的一项改进：在整个数据库中只存储一次唯一的安全描述符，而不是每次使用时都存储。部分 Active Directory 管理员在此升级后，发现其 Active Directory 数据库文件的大小缩减了多达 40%。如果希望回收磁盘上的这部分空间，需要对 *ntds.dit* 文件执行脱机碎片整理。

脱机碎片整理必须在域控制器处于目录服务还原模式时进行。随后可以使用 *ntdsutil* 命令压缩（即碎片整理）*ntds.dit* 文件。此过程实际上会在备用位置创建一份 *ntds.dit* 文件的副本。然后可以用新的压缩版本覆盖现有的 DIT 文件。

配置可用数据库空间的日志记录

如果想知道 *ntds.dit* 中还有多少可用空间，可以设置一个注册表值，让 Active Directory 在联机碎片整理完成后记录一个附加事件——事件 1646。

图 18-23 展示了 Windows Server 2008 域控制器上的此事件。在此场景中，Active Directory 数据库大小为 12 MB，数据库文件中有 1 MB 可用空间。可以利用此信息帮助判断对数据库执行脱机碎片整理是否有任何好处。

要启用此日志记录，请将 `HKLM\System\CurrentControlSet\Services\NTDS\Diagnostics` 下的 `REG_DWORD` 值 `6 Garbage Collection` 设置为 `1`。此更改无需重启即可生效。

![Available space in the database](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663555.webp)

图 18-23。数据库中的可用空间

下面展示了如何使用 *ntdsutil* 执行脱机碎片整理。进入 `files` 菜单后，需要发出 *compact to* *<directorypath>* 命令。*<directorypath>* 应为将在其中创建新的压缩后 *ntds.dit* 文件的目录。如果该目录不存在，将自动创建。执行碎片整理的方式如下：

```
ntdsutil: files
file maintenance: compact to c:\windows\ntds\compact
Opening database [Current].
Creating dir: c:\windows\ntds\compact
Executing Command: C:\WINDOWS\system32\esentutl.exe /d"C:\WINDOWS\NTDS\ntds.dit"
 /t"c:\windows\ntds\compact\ntds.dit" /p /o
Initiating DEFRAGMENTATION mode...
            Database: C:\WINDOWS\NTDS\ntds.dit
      Temp. Database: c:\windows\ntds\compact\ntds.dit
                  Defragmentation Status (% complete)
          0    10   20   30   40   50   60   70   80   90  100
          |----|----|----|----|----|----|----|----|----|----|
          ...................................................
Note:
  It is recommended that you immediately perform a full backup
  of this database. If you restore a backup made before the
  defragmentation, the database will be rolled back to the state
  it was in at the time of that backup.
Operation completed successfully in 20.961 seconds.
Spawned Process Exit code 0x0(0)
If compaction was successful you need to:
   copy "c:\windows\ntds\compact\ntds.dit" "C:\WINDOWS\NTDS\ntds.dit"
and delete the old log files:
   del C:\WINDOWS\NTDS\*.log
file maintenance: quit
```

完成压缩后，就可以决定是否要用其覆盖当前的 *ntds.dit* 文件。

对域控制器( Domain Controller ,DC)执行脱机碎片整理只影响该 DC。若要在其他域控制器上回收空间,则需要对所有其他服务器执行相同的操作。

执行脱机碎片整理后,应确保尽快进行备份。如果由于某种原因必须执行还原,而自执行脱机碎片整理后尚未进行备份,则域控制器上的 *ntds.dit* 文件将直接恢复到碎片整理前的大小。

#### 更改目录服务还原模式管理员密码

定期更改域管理员账户的密码是一种良好做法。这样做可以避免密码扩散到超出必要范围的人员手中，也能防止那些已不在相应 AD 组中的前任管理员尝试执行其本不应执行的任务。

不过，需要关注的不仅仅是域管理员账户。目录服务还原模式( Directory Services Restore Mode ,DSRM )管理员账户同样重要，因为利用它可以执行极具破坏性的操作，例如直接修改 Active Directory 数据库的内容。因此，您也应定期轮换 DSRM 管理员密码。

在域控制器( Domain Controller ,DC )联机状态下，您可以使用 *ntdsutil* 命令更改 DSRM 密码。在 `set dsrm password` 菜单中可使用 *reset password on server %s* 子命令，其中 *%s* 是要作为目标的服务器名称。若要在本地计算机上更改密码，请将 *%s* 留空。在以下示例中，我们为 *DC1* 域控制器设置密码：




```
ntdsutil: set dsrm password
Reset DSRM Administrator Password: reset password on server dc1
Please type password for DS Restore Mode Administrator Account: **********
Please confirm new password: **********
Password has been set successfully.
Reset DSRM Administrator Password: quit
```




> **警告**：如果目标计算机当前处于 DSRM 模式，则无法使用 *ntdsutil* 设置 DSRM 管理员密码。

Windows Server 2008 R2 引入的一项功能允许您使用 *ntdsutil* 将域账户的密码复制到域控制器上的 DSRM 密码。这样一来，在整个域中维护 DSRM 密码就轻松许多，因为您可以在每台 DC 上安排一项任务，定期复制该域账户的密码。



> **注意**：此功能也以修补程序的形式提供给了 Windows Server 2008 域控制器。您可以从 MS 知识库文章 [961320](http://support.microsoft.com/kb/961320) 获取此修补程序。

要使用此功能，请先在 AD 中创建一个已禁用用户账户，用于保存 DSRM 密码。接着运行以下 *ntdsutil* 命令。请务必替换为您所使用账户的用户名：




```
ntdsutil: set dsrm password
Reset DSRM Administrator Password: sync from domain account dsrm-sync-user
Password has been synchronized successfully.
Reset DSRM Administrator Password: quit
```

> **注意**：如果你的林中有多个域，则需要在每个域中创建并维护一个用户账户，用于同步 DSRM 密码。

定期轮换 DSRM 密码最简单的方法之一是使用组策略首选项( Group Policy Preferences )安排计划任务。为此，首先创建一个名为 DSRM Password Sync Policy 的组策略，并将其链接到域控制器组织单位( Domain Controllers OU )。编辑该组策略，导航到*计算机配置\\首选项\\计划任务*。创建一个新的计划任务，如图 18-24所示。使用以下输入填充任务属性：

- 名称：*DSRM Password Sync*
- 运行：*%windir%\\System32\\ntdsutil.exe*
- 参数：*“set dsrm password” “sync from domain account* *dsrm-sync-user” q q*
- 备注：*Synchronizes the DSRM Password with the* *dsrm-sync-user* *domain account.*




![Creating the scheduled task](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663556.webp)


图 18-24. 创建计划任务

在“计划”选项卡上将任务设置为定期运行（例如，每天上午 9 点运行一次）。创建策略并等待其生效后，通过检查域控制器的任务计划程序来验证任务是否已成功创建，如图 18-25所示。等待计划时间过后，将域控制器重启进入目录服务还原模式( Directory Services Restore Mode )，以确保密码确实已按预期同步。




![DSRM Password Sync scheduled task](./image/18.%20Backup,%20Recovery,%20and%20Maintenance/httpatomoreillycomsourceoreillyimages1663557.webp)


图 18-25. DSRM 密码同步计划任务

### 18.9. 本章小结

在本章中,我们回顾了制定灾难恢复计划所需的全部要素。我们介绍了如何备份 Active Directory,以及逻辑删除生存时间( Tombstone Lifetime )和密码更改周期相关的一些注意事项。随后,我们讨论了还原 Active Directory 的多种方案,包括通过复制进行还原、权威还原( Authoritative Restore )、非权威还原( Nonauthoritative Restore )以及 Active Directory 回收站( Active Directory Recycle Bin )。我们还探讨了 FSMO 角色转移流程,以及夺取 FSMO 角色所需的操作。最后,我们深入介绍了一些可针对 Active Directory 目录信息树( Directory Information Tree ,DIT )文件执行的维护任务。

---

## 第 19 章 升级 Active Directory

与其他任何服务或应用程序一样,随着 Active Directory 在 Windows 各个版本中不断演进,以及组织内信息技术团队持续向前推进,你必须为升级 Active Directory 做好准备。鉴于 Active Directory 作为核心 IT 服务的基础性地位,一旦提及升级,人们无疑会心生忐忑。

不过,只要做好规划并开展尽职调查,你就能成功升级组织的 Active Directory 环境,从而利用新功能,并持续在受支持的平台上运行。

在本章中,我们将探讨 Active Directory 各版本带来的新功能、启动升级规划所需的若干步骤,以及如何发起升级过程。最后,我们还将介绍一些已知问题,供你在规划组织内 Active Directory 升级时参考。

### 19.1. Active Directory 版本

在深入之前，有必要了解 Active Directory 每个后续版本新增的特性和功能。Active Directory 已有十多年历史，而每个版本持续创新，不断提高标准，为 Active Directory 客户带来更多价值。

阅读本节时，请查看后续各版本 Windows 附带的功能和特性。你可以利用这些信息着手为升级构建业务论证（business case）。反之，查看较新版本 Windows 中可用的功能可能会让你发现，某项变更并不会真正为你的组织带来收益，升级不值得付出成本和精力。如果是这种情况，请等待下一个 Windows 版本并重新评估。

如果你确实决定等待下一个版本，需要牢记一个考虑因素：当前运行的 Windows 版本的 Microsoft 产品支持生命周期（Product Support Lifecycle），以及下一个 Windows 版本发布时你的版本将处于生命周期中的哪个位置。产品支持生命周期定义了 Microsoft 会在多长时间内接听有关给定产品的来电、为该产品生成安全补丁，以及修复缺陷并发布修补程序（hotfix）。如果你的 Windows 版本已不再受支持，或者在下一个版本发布之前将超出支持期限，那么你应计划升级，仅仅是为了确保能够持续获得支持。

你可以在 http://support.microsoft.com/lifecycle/ 在线查找 Microsoft 的支持生命周期策略。

查看以下各节时，你会发现我们将变更分为了新特性和功能变更。我们建议你查看所有适用于本次升级的新特性，然后将它们归入以下类别：

- 我会立即使用该功能。
- 我最终会使用该功能。
- 我永远不会使用该功能，或者该功能并不重要。

> **注意**：我们所说的“功能”是指新功能，而不仅仅是对 Active Directory 在以前版本的 Windows 中工作方式的修改。从这个意义上说，功能是必须显式使用或实现的内容。

评估每个功能将有助于确定你可以从升级中获得多少好处。与新功能一样，建议你仔细查看每个差异，并将其归入以下类别：

- 对我的环境有较大程度的积极影响。
- 对我的环境有较小程度的积极影响。
- 对我的环境有负面影响。

绝大多数差异实际上是改进，应该会为你带来积极的影响，但在某些情况下，例如与安全相关的更改，其影响可能会在初期给你带来额外的工作。

#### Windows Server 2003

Windows Server 2003 是自 Windows 2000 首次发布以来对活动目录( Active Directory ,AD)的第一次升级。Active Directory 在 Windows 2000 中是一款极其可靠的产品，但 Windows Server 2003 带来了新功能、更佳的性能和增强的安全性。但愿此时您阅读本节是为了了解背景，而不是规划从 Windows 2000 升级！

##### 新功能

- **应用程序分区( Application Partitions )**

  可以创建可复制到林中任意域控制器( Domain Controller ,DC)的分区（命名上下文( Naming Context )）。有关应用程序分区的详细信息，请参阅 第 4 章。

- **并发 LDAP 绑定( Concurrent LDAP Binds )**

  并发 LDAP 绑定，也称为*快速绑定( Fast Binds )*，不会生成 Kerberos 票据和安全令牌( Security Token )，因此比简单 LDAP 绑定( Simple LDAP Binds )快得多。

- **跨林信任( Cross-Forest Trust )**

  这是一种传递信任( Transitive Trust )，允许两个不同林中的所有域通过两个林根域( Forest Root Domain )之间定义的单个信任相互信任。这需要 Windows Server 2003 林功能级别( Forest Functional Level )。

- **域控制器重命名( Domain Controller Rename )**

  域控制器的重命名过程只需一次重新启动。以前，如果不先降级域控制器，然后重命名并重新提升它，则无法重命名域控制器。

- **域重命名( Domain Rename )**

  现在可以对域进行重命名，但会对用户群产生重大影响（例如，所有成员计算机( Member Computer )必须重新启动两次）。有关详细信息，请查看以下[白皮书](http://bit.ly/XfJZXx)。这需要 Windows Server 2003 林功能级别。

- **动态辅助类( Dynamic Auxiliary Classes )**

  现在支持基于标准的动态辅助类实现。在 Windows 2000 中，辅助类被视为“静态”，因为它们在架构( Schema )中静态链接到结构类( Structural Class )。使用动态辅助类，可以在创建对象时链接动态辅助类（或在创建后添加）。辅助类不需要在架构中定义为对象 `objectClass` 的辅助类。这需要 Windows Server 2003 林功能级别。

- **动态对象( Dynamic Objects )**

  传统上，对象存储在 Active Directory 中，直到被显式删除。使用动态对象，可以创建具有生存时间( Time-to-Live ,TTL)值的对象，该值指定它们何时自动删除（除非刷新）。动态对象因过期而被删除时不会保留为

网络环境中的一个经典难题是确定用户或计算机的最后登录时间。新增的 `lastLogonTimeStamp` 属性会被复制，这意味着只需一次查询即可找出在特定时间段内未登录网络的所有用户或计算机。默认情况下，该属性大约每 10 天更新一次。这要求域运行在 Windows Server 2003 功能级别。有关该属性的更多信息，请访问 http://blog.joeware.net/2007/05/01/864/。

- **MMC 和 CLI 增强**

  活动目录用户和计算机( Active Directory Users and Computers ,ADUC )工具已增强，支持多选对象；其他工具(如 *repadmin* 和 *netdom* )也新增了选项。

- **新的 DS CLI 工具**

  一组新的命令行工具为从命令行管理 Active Directory 提供了更大的灵活性。这些工具包括 *dsadd*、*dsmod*、*dsrm*、*dsget* 和 *dsquery*。

- **组策略 RSoP**

  策略结果集( Resultant Set of Policy ,RSoP )已内置于 ADUC 中，并可通过组策略管理控制台( Group Policy Management Console ,GPMC )充分利用。RSoP 允许管理员确定组策略对象( Group Policy Object ,GPO )的哪些设置将应用于最终用户和计算机。

- **`objectClass` 更改**

  你可以将用户对象更改为 `inetOrgPerson` 对象，也可以将 `inetOrgPerson` 对象更改为用户对象。这要求 Windows Server 2003 林功能级别。

- **TLS 支持**

  在 Windows 2000 中，仅支持安全套接字层( Secure Sockets Layer ,SSL )来加密网络传输。传输层安全( Transport Layer Security ,TLS )——最新的基于标准的 LDAP 流量加密方法——现在也受到支持。

- **配额**

  在 Windows 2000 中，如果用户有权创建对象，他们可以创建任意数量的对象，且无法限制。配额允许你定义用户或用户组可以创建多少个对象。配额还可以规定可以创建某个 `objectClass` 的多少个对象。

- **重定向用户和计算机**

  你可以分别使用 *redirusr* 和 *redircmp* 命令重定向存储新用户和计算机的默认位置。

- **架构重定义**

  在发生架构冲突时，或者如果你只是想隐藏未使用的类和属性，你可以将属性和类标记为失效，然后在架构中重新定义它们。这要求 Windows Server 2003 林功能级别。

- **通用组成员身份缓存**

此功能免除了登录期间为扩展通用组而必须存在全局编录服务器( Global Catalog Server )的要求。此功能在站点级别启用,适用于登录到该站点中域控制器( Domain Controller ,DC)的任何客户端。`userPrincipalName` 身份验证仍需要全局编录。

- **GPO 的 WMI 筛选**

  除了可用于筛选组策略对象( Group Policy Object ,GPO)的 OU、站点、域和安全组条件外,现在还可以使用客户端计算机上的 Windows Management Instrumentation( Windows Management Instrumentation ,WMI)信息来确定是否应应用某个 GPO。此功能仅适用于 Windows XP/2003 及更高版本的客户端。

- **用于信任和复制监视的 WMI 提供程序**

  这些新的 WMI 提供程序支持以编程方式查询和监视信任与复制的运行状况。

##### 功能差异

- **对 \*Pre-Windows 2000 Compatible Access\* 组的更改**

  为了增强安全性，Everyone 安全主体不再等同于所有未经身份验证和经过身份验证的用户。相反，它仅代表经过身份验证的用户。若要在 Windows Server 2003 中授予等效的匿名访问权限，必须将 Anonymous Logon 安全主体添加到 Pre-Windows 2000 Compatible Access 组中。

- **分布式链接跟踪( Distributed Link Tracking ,DLT)服务默认禁用**

  DLT 服务可能会产生成千上万（甚至数百万）个嵌套在域的 System 容器内的 `linkTrackOMTEntry` 对象。默认情况下，DLT 服务在 Windows Server 2003 域控制器( Domain Controller ,DC)上处于禁用状态。注意 Microsoft 在知识库文章 [315229](http://support.microsoft.com/kb/315229) 中提供了一个脚本来清理 DLT 对象。

- **更快的全局编录( Global Catalog ,GC)删除**

  在 Windows 2000 中，当您在域控制器上禁用全局编录时，全局编录删除过程每 15 分钟只能删除 500 个对象。此行为已更改，因此该过程要快得多。

- **站点内复制( Intrasite Replication )频率更改为 15 秒**

  之前的默认站点内复制间隔为 5 分钟，现已更改为 15 秒。对于从 Windows 2000 升级的任何域控制器，这要求 Windows Server 2003 林功能级别。

- **站点间拓扑生成器( Inter-Site Topology Generator ,ISTG)和知识一致性检查器( Knowledge Consistency Checker ,KCC)的可伸缩性改进**

  用于生成站点间连接的算法已大幅改进，以至于之前 300 到 400 个站点的软限制已提高到支持大约 3,000 到 5,000 个站点。这种新的复制机制要求 Windows Server 2003 临时模式或 Windows Server 2003 林功能级别。

- **链接值复制( Link Value Replication ,LVR)**

  Active Directory 中的复制是在属性级别进行的。也就是说，当修改某个属性时，会复制整个属性。这对于某些属性来说是有问题的，例如组对象上的 `member` 属性，它只能存储大约 5,000 个成员。LVR 复制意味着链接属性（如 `member`）在更新时只会复制属性内的更改，而不会复制整个属性的内容。这要求 Windows Server 2003 临时模式或 Windows Server 2003 林功能级别。

- **添加部分属性集( Partial Attribute Set ,PAS)时无需全局编录同步**

在 Windows Server 2003 中，每当将属性添加到部分属性集( Partial Attribute Set ,PAS)时，不再像 Windows 2000 那样执行完整的全局编录( Global Catalog ,GC)重新同步。这对大型、全球分散的 Windows 2000 域的管理员来说尤其痛苦。

- **经过签名和密封的 LDAP 流量**

  不再通过 ADUC 和 ADSI Edit 等工具以明文形式在网络上发送包含用户名和密码的 LDAP 流量，而是对流量进行数字签名和加密。

- **单实例 ACL 存储**

  唯一的安全描述符( Security Descriptor )无论使用多少次，都只存储一次，而不是为每个实例单独存储。此功能可以将 *ntds.dit* 文件缩小约 20%–40%。

#### Windows Server 2008

Windows Server 2008 引入了许多引人注目的功能，包括支持在服务器核心( Server Core )上运行、只读域控制器( Read-Only Domain Controller ,RODC )以及细化密码策略( Fine-Grained Password Policy )。

##### 新增功能

- **管理角色分离( Administrative Role Separation )**

  非域管理员的用户也可以被安全地委派 RODC 的管理控制权,而无需向其授予可写 Active Directory 的访问权限(即他们除了 RODC 之外无法修改任何内容)。

- **ADMX 存储库( ADMX Repository )**

  升级后的组策略模板文件可以在每个域中仅于 Sysvol 内存储一份,从而大幅缩减许多组织的 Sysvol 体积。

- **数据库快照( Database Snapshots )**

  可以获取 Active Directory 数据库的时间点快照,作为灾难恢复以及其他对象还原和比较操作的基础。

- **DNS 服务器功能( DNS Server Features )**

  新增了对以下功能的支持:新的定位器选项、安装期间自动配置、后台区域加载以及多播 DNS。

- **DFS-R Sysvol 复制**

  现在可以使用新的 DFS-R 复制引擎复制 Sysvol,与 NTFRS 相比,其可靠性和可扩展性都大幅提升。

- **细粒度密码策略( Fine-Grained Password Policies )**

  现在可以按用户定义密码策略和帐户锁定策略。有关细粒度密码策略的详细信息,请参阅第 12 章。

- **GlobalNames DNS 区域**

  这是一种新型 DNS 区域,可通过解析非限定主机名,为摆脱 WINS 的迁移工作铺平道路。

- **组策略首选项( Group Policy Preferences )**

  组策略首选项让您可以控制此前只能通过脚本访问的众多设置和 Windows 功能。

- **上次登录统计( Last-Logon Statistics )**

  Windows Vista 和 Windows Server 2008 客户端可以将详细的上次登录成功与失败信息直接存储在目录中的用户对象上。此功能是为满足通用标准( Common Criteria )合规要求而实现的。

- **所有者访问权限( Owner Access Rights )**

  现在新增了一个众所周知的安全主体,用于表示对象的所有者。

- **语音名称索引( Phonetic Name Indexing )**

  `displayName` 属性在日语区域设置的域控制器上可按语音排序。

- **只读 DNS**

  RODC 可以承载动态 DNS 区域,并将所有更新转交给可写的域控制器处理。

- **只读域控制器**

只读域控制器( Read-Only Domain Controller ,RODC )不允许本地写入,并且即使这些域控制器被入侵,也不会复制到域中的可写域控制器。默认情况下,它们也不存储密码及其他机密信息。对于物理安全存疑的位置,此功能大大增强了域控制器的安全性。有关 RODC 的详细信息,请参阅第 9 章。

- **可重启目录服务( Restartable Directory Service )**

  可以停止 Active Directory,以便在无需以目录服务修复模式( Directory Services Repair Mode )重启域控制器的情况下执行某些离线操作。

- **Server Core 支持**

  域控制器现在可以运行在 Windows Server 2008 操作系统的某个版本上,该版本更为精简,因此更加安全。资源管理器外壳、Internet Explorer 以及其他对服务器运行并非必需的组件均已从 Server Core 中移除。

- **入门组策略**

  可以定义组策略( Group Policy )模板,管理员可基于这些模板创建新策略。

##### 功能差异

- **审核与日志记录基础结构增强**

  对 Active Directory 访问与更改以及其他各种操作的审核功能已大幅更新。

- **委派的域控制器提升**

  域控制器( Domain Controller ,DC)提升可拆分为两步流程,从而允许将提升域控制器时需现场动手操作的部分委派给非域管理员用户,例如本地站点支持技术人员。

- **域 DFS 可伸缩性增强**

  基于域的 DFS 根可承载超过 5,000 个链接,还可利用基于访问权限的枚举( Access-Based Enumeration ,ABE)。

- **ESE 单位错误纠正**

  Active Directory 使用的 JET 数据库引擎现已能够检测并纠正单位错误,从而减少因损坏而导致数据库故障的情况。

- **Kerberos AES 密钥长度升级**

  Kerberos 支持的高级加密标准( Advanced Encryption Standard ,AES)最大密钥长度已从 128 位加长至 256 位。

#### Windows Server 2008 R2

就新功能的数量而言,Windows Server 2008 R2 对 Active Directory 而言是一个相对较小的版本。其中最引人注目的是,活动目录回收站( Active Directory Recycle Bin ,ADRB )随 Windows Server 2008 R2 一同推出。

##### 新功能

- **活动目录管理中心( Active Directory Administrative Center ,ADAC )**

  ADAC 是 Microsoft 用于管理 Active Directory 的新款图形用户界面( Graphical User Interface ,GUI )。

- **活动目录 Web 服务( Active Directory Web Service )**

  这是一个额外的协议终结点,现在运行在域控制器( Domain Controller ,DC )和活动目录轻型目录服务( Active Directory Lightweight Directory Services ,AD LDS )服务器上。所有 Active Directory PowerShell cmdlet 都会调用该 Web 服务,而不再直接进行 LDAP 或 RPC 调用。尽管名称如此,它与 Internet 信息服务( Internet Information Services ,IIS )等传统 Web 服务器技术并无关联。

- **身份验证机制保证( Authentication Mechanism Assurance ,AMA )**

  借助 AMA,管理员可以定义特殊 SID,当用户使用特定类型的智能卡证书登录时,这些 SID 将被注入该用户的安全令牌中。

- **Kerberos 林搜索顺序( Kerberos Forest Search Order )**

  当 Kerberos 服务主体名称( Service Principal Name ,SPN )无法在域控制器所在的林中找到时,域控制器可以自动到受信任林中搜索该 SPN。

- **托管服务账户( Managed Service Account ,MSA )**

  服务账户是 Active Directory 环境中由来已久的安全问题。服务账户密码往往极少更改(甚至从不更改),且为多人所知。MSA 通过定期自动轮换账户密码解决了这一问题。

- **PowerShell cmdlet**

  这是适用于 Windows PowerShell 的 Active Directory 模块的第一个版本。该模块包含的 cmdlet 主要用于管理用户、组和计算机。

- **回收站( Recycle Bin )**

  ADRB 使管理员无需借助备份即可恢复已删除的对象,且不会丢失对象的任何属性。有关 ADRB 的详细信息,请参阅第 18 章。

##### 功能差异

- **桥头服务器负载均衡**

  对活动目录( Active Directory )中复制拓扑生成过程的这一改进,可确保传入的复制连接在站点中的各服务器之间实现负载均衡。

- **离线域加入**

  通过在活动目录( Active Directory )中预先暂存计算机账户信息,Windows 7 客户端无需网络连接即可加入域。

- **弱加密类型已禁用**

  默认情况下,Windows Server 2008 R2 域控制器( Domain Controller ,DC )禁用对 DES 和 3DES 加密类型的支持。可通过组策略显式启用这些加密类型来还原此设置。

#### Windows Server 2012

Windows Server 2012 为 Active Directory 提供了大量新功能，并针对长期挑战（例如安全地虚拟化域控制器( Domain Controller ,DC)）提供了解决方案。

##### 新功能

- **基于 Active Directory 的激活**

  Windows 8 和 Windows Server 2012 安装现在可以基于发布到 Active Directory 的许可数据进行激活。这消除了以前企业环境中激活所需的密钥管理服务器( Key Management Server ,KMS )。

- **域控制器克隆**

  运行在支持虚拟机代 ID( Virtual Machine Generation ID ,VM Gen ID )的虚拟机监控程序上的 Windows Server 2012 域控制器，可以通过克隆域控制器的虚拟硬盘文件进行复制。有关域控制器克隆的详细信息，请参阅第 9 章。

- **动态访问控制( Dynamic Access Control ,DAC )**

  Active Directory 中的动态访问控制功能扩展了安全令牌，使其包含声明。这些声明基于 Active Directory 中用户对象的属性以及用户登录所用工作站的属性。用于评估声明的复合表达式可应用于 Windows Server 2012 文件和文件夹权限，以代替复杂的组成员身份。有关 DAC 的详细信息，请参阅第 16 章。

- **灵活身份验证安全隧道( Flexible Authentication Secure Tunneling ,FASt )**

  域控制器实现 [RFC 6113](http://tools.ietf.org/html/rfc6113)，也称为 *Kerberos 强化*。此功能通过消除欺骗和字典攻击的途径来增强安全性。

- **组托管服务账户( Group Managed Service Account ,gMSA )**

  托管服务账户( Managed Service Account ,MSA )有一个重大限制，即当服务必须跨多台服务器运行时无法使用它们。组托管服务账户通过允许多台服务器共享 MSA 并在密码更改时获取密码，解决了此问题。

- **组策略( Group Policy )基础结构状态**

  组策略管理控制台( Group Policy Management Console ,GPMC )现在可以报告存储在 Active Directory 中的组策略信息以及域控制器上组策略信息的运行状况。

##### 功能差异

- **Active Directory 管理中心增强**

  Active Directory 管理中心( Active Directory Administrative Center ,ADAC )图形用户界面已得到增强，现支持管理回收站( Recycle Bin )和细粒度密码策略( Fine-Grained Password Policy )。用户界面也比 Windows Server 2008 R2 版本快得多。

- **跨域 Kerberos 约束委派**

  Kerberos 约束委派( Kerberos Constrained Delegation ,KCD )现在可以跨域边界执行。

- **延迟索引创建**

  Active Directory 属性的索引创建现在可以延迟到域控制器( Domain Controller ,DC )重新启动或显式请求索引时再进行。这解决了大型林( Forest )中的性能问题，此前在创建索引时，为属性编制索引可能会对所有域控制器造成显著的性能影响。

- **部署简化**

  经典的 dcpromo 向导和 *adprep* 升级准备实用工具已被淘汰，取而代之的是服务器管理器( Server Manager )中的集成部署向导，可处理域控制器提升和 Active Directory 升级的所有方面。这些步骤也可以通过新的 Windows PowerShell cmdlet 执行。

- **Kerberos 约束委派配置变更**

  KCD 现在可以在被委派*至*的服务上配置，而不是在执行委派的服务上配置。这些变更还消除了配置 KCD 时需要域管理员( Domain Admin )级别访问权限的要求。

- **离线域加入 DirectAccess 支持**

  离线域加入( Offline Domain Join )已得到增强，现在还包含计算机连接到 DirectAccess 所需的前提条件。这使计算机能够通过 Internet 加入域。

- **PowerShell 增强**

  Windows PowerShell 的 Active Directory 模块已得到增强，新增了用于管理复制和域控制器生命周期(提升、降级等)的 cmdlet。

- **RID 池消耗警告**

  全局 RID 池的大小已从约十亿个 RID 翻倍至二十亿个 RID。为防止在管理员不知情的情况下耗尽 RID 池，系统现在会在全局 RID 池使用率达到 90% 时记录事件。此外还设置了发放新 RID 的软阻止( Soft Block )，必须由管理员解除。

- **虚拟化安全性**

在支持虚拟机代 ID( VM Gen ID )的虚拟机监控程序( hypervisor )上运行的 Windows Server 2012 域控制器( Domain Controller ,DC ),能够感知到可能导致域控制器状态回滚的变更。一旦检测到此类变更,域控制器便会采取保护措施,确保复制( Replication )及其他功能不受影响。有关此变更的详细信息,请参阅第 9 章。

### 19.2. 功能级别

既然您已对 Active Directory 各版本引入的新功能充满期待，接下来我们将探讨如何实际启用这些功能。*功能级别* 决定了哪些操作系统能够运行域控制器。通过确保域或整个林中的最低操作系统版本，您可以控制哪些 Active Directory 功能可用或可被启用。

为了说明为何需要功能级别，让我们看两个示例。首先，考虑 Windows Server 2003 中新增的“最后登录时间戳属性”功能。借助此功能，当用户或计算机登录到域时，会填充一个名为 `lastLogonTimeStamp` 的新属性，并将其复制到域中的所有域控制器。与未复制的 `lastLogon` 属性相比，该属性提供了一种更简便的方法来识别用户或计算机最近是否登录过，因为 `lastLogon` 属性必须在域中的每个域控制器上查询。要使 `lastLogonTimeStamp` 发挥作用，域中的所有域控制器在接收到用户或计算机的登录请求时，都需要知道更新该属性。来自其他域的域控制器只需关注其所在域内的对象，因此此功能具有域范围。Windows 2000 域控制器不了解 `lastLogonTimeStamp`，也不会更新它。因此，为了使该属性能够一致地更新并真正发挥作用，域中的所有域控制器都必须运行 Windows Server 2003。所有域控制器必须知道其他所有域控制器都在运行 Windows Server 2003，它们可以通过查询域的功能级别来确定这一点。一旦发现域处于特定的功能级别，它们就可以开始利用该功能级别特有的功能。

同样，有时必须先让林( Forest )中的所有域控制器( Domain Controller ,DC)运行特定的操作系统，然后才能使用某一功能。Active Directory 回收站( Active Directory Recycle Bin )就是一个很好的例子。由于启用回收站后，对象的删除方式会发生变化，并且一个对象(例如组)可能引用另一个域中的对象，因此必须保证每个域控制器都以相同方式处理删除操作。为确保这一点，林中的每个域控制器必须至少运行 Windows Server 2008 R2，Active Directory 回收站才可用。一旦所有域控制器都运行 Windows Server 2008 R2，就可以提升林功能级别( Forest Functional Level ,FFL)并启用回收站。

与以前版本的 Windows 不同，Windows Server 2012 功能级别几乎没有任何益处。在 Windows Server 2012 中，Microsoft 致力于(且相当成功地)使所有新的 Active Directory 功能无需提升域或林功能级别即可使用。提升域功能级别( Domain Functional Level ,DFL)只会启用两个通过组策略( Group Policy )配置的 Kerberos 功能(“始终提供声明”(Always provide claims)[位于“KDC 支持声明、复合身份验证和 Kerberos 强化”(KDC support for claims, compound authentication and Kerberos armoring)内]以及“当 Kerberos 强化不可用时使身份验证请求失败”(Fail authentication requests when Kerberos armoring is not available))。提升林功能级别不会增加任何附加功能。

#### 提升功能级别

您可以使用几种不同的工具来提升域和林功能级别。无论您运行的是哪个版本的 Windows，Active Directory 域和信任关系( Active Directory Domains and Trusts ) MMC 管理单元都是一种选择。如果您运行的是 Windows Server 2012，还可以使用 Active Directory 管理中心( Active Directory Administrative Center ,ADAC )。

若要使用 ADAC 提升域或林功能级别，请在导航窗格中选择要修改的域，然后在任务窗格中单击“提升域功能级别”或“提升林功能级别”。该对话框将类似于图 19-1。您可以提升到的功能级别将列在下拉列表中。单击“确定”后，系统将通知您更改可能需要一些时间才能复制到整个环境，如图 19-2所示。提升功能级别的操作会像对目录的任何其他更改一样进行复制。有关与功能级别更改相关的已知问题列表，请参阅[此网站](http://bit.ly/10RdjU9)。




![Raising the domain functional level in ADAC](./image/19.%20Upgrading%20Active%20Directory/httpatomoreillycomsourceoreillyimages1663558.webp)


图 19-1. 在 ADAC 中提升域功能级别




![Domain functional level raise confirmation](./image/19.%20Upgrading%20Active%20Directory/httpatomoreillycomsourceoreillyimages1663559.webp)


图 19-2. 域功能级别提升确认

若要使用 Active Directory 域和信任关系提升域的功能级别，请打开该管理单元，浏览到要提升的域，在左侧窗格中右键单击该域，然后选择“提升域功能级别”。随后您将看到类似于图 19-3的屏幕。




![Raising the domain functional level with AD Domains and Trusts](./image/19.%20Upgrading%20Active%20Directory/httpatomoreillycomsourceoreillyimages1663560.webp)


图 19-3. 使用 AD 域和信任关系提升域功能级别

选择新的功能级别，然后单击“提升”按钮。随后您将收到操作成功的确认信息，或者指出无法提升功能级别的原因的错误信息。图 19-4显示了成功提升功能级别后返回的消息。按照相同的步骤提升林的功能级别，但在左侧窗格中右键单击 Active Directory 域和信任关系，然后选择“提升林功能级别”。




![The result of raising the domain functional level with AD Domains and Trusts](./image/19.%20Upgrading%20Active%20Directory/httpatomoreillycomsourceoreillyimages1663561.webp)

图 19-4. 使用 AD Domains and Trusts 提升域功能级别后的结果

您还可以通过其他几种方式确定域或林的功能级别。首先，对于域，可以查看域命名上下文(例如 `dc=cohovines, dc=com`)上的 `msDS-Behavior-Version` 属性；对于林，可以查看配置命名上下文中的 Partitions 容器(例如 `cn=partitions, cn=configuration, dc=cohovines, dc=com`)。表 19-1 列出了该属性的取值及其对应的功能级别。



表 19-1. 功能级别

| msDS-Behavior-Version 值 | 功能级别                    |
| --------------------------- | --------------------------- |
| `0`                         | Windows 2000                |
| `1`                         | Windows Server 2003 Interim |
| `2`                         | Windows Server 2003         |
| `3`                         | Windows Server 2008         |
| `4`                         | Windows Server 2008 R2      |
| `5`                         | Windows Server 2012         |

> **注意**：Windows 2000 没有功能级别( Functional Level )这一概念。取而代之的是,你可以选择 Windows 2000 混合模式(支持 Windows NT 4 域控制器( Domain Controller ,DC))或 Windows 2000 本机模式(仅支持 Windows 2000 域控制器)。这两种模式不会记录在 `msDS-Behavior-Version` 属性中。

此外,你也可以直接查看域控制器的 *RootDSE* 来获取此信息。*RootDSE* 包含两个描述当前功能级别的属性:

- **domainFunctionality**

  该值与域命名上下文( Domain Naming Context )上的 `msDS-Behavior-Version` 值一致。

- **forestFunctionality**

  该值与分区容器( Partitions Container )上的 `msDS-Behavior-Version` 值一致。

#### 功能级别回滚

对于实施变更控制流程的组织而言,管理员面临的挑战之一是:提升功能级别通常无法回退,除非对整个域或林( Forest )进行完整还原。这使得变更难以获得批准,因为变更申请文档中的回退计划部分基本上是空白的。

幸运的是,从 Windows Server 2008 R2 功能级别开始,如有必要,你可以回滚到上一功能级别。不过,你只能回滚到 Windows Server 2008(或更高)功能级别,并且前提是尚未启用活动目录回收站( Active Directory Recycle Bin )。

要回滚域或林功能级别,可以使用 *Set-ADDomainMode* 和 *Set-ADForestMode* PowerShell cmdlet。例如,如果要将 *cohovines.com* 域回滚到 Windows Server 2008 域功能级别,请运行以下命令:

```
Set-ADDomainMode cohovines.com -DomainMode Windows2008Domain
```

### 19.3. 开始升级

当你准备在环境中引入第一台新的域控制器( Domain Controller ,DC)时,需要先执行一些更新。这些更新包括对 Active Directory 架构的修改以及各种操作层面的调整,例如添加必要的权限以确保 Active Directory 正常运行。

如果你以前曾将 Active Directory 升级到 Windows 2000 之后的任何版本,那你一定对 Windows 安装介质上的 *adprep* 工具不陌生。首先运行 *adprep /forestprep* 升级架构,然后依次执行 *adprep /domainprep* 和 *adprep /rodcprep*。这些步骤每一步都有可能失败,而且一开始找到这个工具本身就很困难。

幸运的是,现在引入第一台 Windows Server 2012 域控制器时,升级过程会自动帮你处理好一切。

> **注意**：如果你希望手动执行 Windows Server 2012 准备步骤，或者在引入第一台 Windows Server 2012 域控制器( Domain Controller ,DC)之前提前执行这些步骤，*adprep* 仍然可用。

*adprep* 实用工具以及新的 Windows Server 2012 过程的巧妙之处之一在于，它将进度存储在 Active Directory 中。这很有用，因为这意味着它可以在执行过程中从失败中优雅地恢复。它还提供了一种快速方法来确定所有必需操作是否已完成以及 *adprep* 是否成功。将操作存储在 Active Directory 中的另一个好处是，如果你遇到问题并需要致电 Microsoft 产品支持服务( Microsoft Product Support Services ,PSS)，你可以查看此容器并列出所有已成功完成的操作。然后 PSS 将能够查找哪个操作失败。

在配置容器( Configuration container )下直接创建一个林更新容器( Forest Updates container )。在林更新容器内还有另外两个容器，一个名为 Operations，另一个名为 ActiveDirectoryUpdate。操作容器( Operations container )包含其他容器，每个容器代表 *adprep* 已完成的一项特定任务。例如，一个操作可能是创建新的 `displaySpecifier` 对象。操作容器的名称是 GUID，而这些对象本身不包含任何有意义的信息。

Forest Updates 容器内的另一个容器称为 ActiveDirectoryUpdate。此容器在林升级准备过程完成后创建和/或更新。图 19-5 显示了使用 ADSI Edit 管理单元查看时这些容器的外观。除了 ActiveDirectoryUpdate 和 Operations 容器之外，还有当你运行 Windows 2003 版本的 *adprep* 时创建的 Windows2003Update 容器，以及由 RODC 准备步骤产生的 ActiveDirectoryRodcUpdate 容器。

![Forest Updates Operations container](./image/19.%20Upgrading%20Active%20Directory/httpatomoreillycomsourceoreillyimages1663562.webp)

图 19-5. 林更新操作容器

与林更新容器类似，每个域都有一个域更新容器( Domain Updates container )，用于跟踪域的升级。你可以通过在域的根下的系统容器( System container )中浏览来找到此容器，如图 19-6所示。

![Domain Updates Operations container](./image/19.%20Upgrading%20Active%20Directory/httpatomoreillycomsourceoreillyimages1663563.webp)

图 19-6. 域更新操作容器

### 19.4. 已知问题

尽管大多数 Active Directory 升级都会顺利进行，但道路上总难免会有颠簸。在您的环境中进行妥善的规划、测试和沟通，是升级项目成功的关键。自 Windows Server 2003 问世以来，我们参与了无数 Active Directory 升级项目，每次看到项目失败，都是因为遗漏了这三个要素(规划、测试或沟通)之一。

Microsoft 在 TechNet 上维护了一份出色的文档，随着 Microsoft 支持团队处理客户在升级林时遇到的问题，该文档会频繁更新。此文档可在 [microsoft.com](http://bit.ly/11NrA73) 找到，我们强烈建议您在着手升级项目之前先行查阅。

### 19.5. 小结

在本章中,我们介绍了自 Windows Server 2003 以来各个版本的活动目录( Active Directory ,AD )新增功能及功能差异。随后,我们讨论了功能级别( Functional Level ),以及如何升级域或林的功能级别,并在必要时进行回滚。最后,我们讨论了为新域控制器( Domain Controller ,DC )准备域和林所需的前期步骤。
