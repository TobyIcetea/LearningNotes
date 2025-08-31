# internal-apiserver 部分

## model

model 中放着 post.gen.go 文件和 user.gen.go 文件，这两部分文件都是通过 gormgen 工具直接生成的，跟数据库中记录匹配的结构体。这部分在之前的分析中已经介绍过很多次，其中的定义我们叫 model 类型的 user 和 post，是数据库友好型的。

同时还在 hook.go 中，为 user 和 post 创建了几个钩子函数：

```go
// AfterCreate 在创建数据库记录之后生成 postID
func (post *Post) AfterCreate(tx *gorm.DB) error {
	post.PostID = rid.PostID.New(uint64(post.ID))

	return tx.Save(post).Error
}
```

这部分表示在创建完一条 post 记录之后，自动调用 `AfterCreate()` 函数，通过 `post.ID`（如 20）自动生成一个 `postID`（如 `post-h40szu`）。同时，在最后调用 `tx.Save()`。

最后还执行了一个 `tx.Save()`，这数据数据库中进行 Update 操作的一部分，且 `tx.Save()` 是做了一个全量更新。这里虽然这个变量名叫做 `tx`，但是这种 `*gorm.DB` 类型的数据，在实践中我们一般还是叫做 `db`。

---

```go
// BeforeCreate 在创建数据库记录之前加密明文密码
func (m *User) BeforeCreate(tx *gorm.DB) error {
	// Encrypt the user password.
	var err error
	m.Password, err = auth.Encrypt(m.Password)
	if err != nil {
		return err
	}
	return nil
}
```

user 的 `BeforeCreate()` 表示在创建一个 User 之前，执行的函数。这里是调用了 `auth` 中的 `Encrypt()` 方法，这个函数的作用是将一段字符串生成一个密码哈希。也就是说，原密码是多少我们是不保存的，在数据库也不会出现原密码，而是直接存密码的哈希串。

---

```go
// AfterCreate 在创建数据库记录之后生成 userID
func (user *User) AfterCreate(tx *gorm.DB) error {
	user.UserID = rid.UserID.New(uint64(user.ID))

	return tx.Save(user).Error
}
```

user 的 `AfterCreate()` 方式，是在数据库中创建了 User 之后，生成一个 UserID。根据 `user.ID` 生成一个 `UserID`，类似于 `user-p86ggd` 这样的形式。

综合来看，不管是 `user` 的 `AfterCreate()` 钩子还是 `post` 的 `AfterCreate()` 钩子，做一次 Create 的操作，都会执行两次 Create。第一次是创建这一条记录，因为创建的时候没有指定，也不知道这一条记录的 ID 值。插入结束之后，才知道这一条记录的 ID 值，之后再使用这里的 ID 值，通过之前 pkg 中提供的 rid 包中的函数，生成这条记录的 `userID`/`postID`。

生成了新的 `userID`/`postID` 之后，这时候只是在程序内存的对象中做了修改，在对象中修改了这个字段。之后有通过调用了 `*gorm.DB` 的 `Save()` 方法，做了一个数据库记录的全量更新。之后就将这个字段给更新了。所以总的来说，每执行一次 Create 操作，都是要执行两次 SQL 的，一个 Create 操作，一个 Update 操作。

---

对钩子函数的理解：

创建钩子函数的时候，可以直接创建 `BeforeCreate()`、`AfterCreate()`、`BeforeSave()`、`AfterUpdate()` 之类的钩子。需要符合的标准就是这些函数要作为 gormgen 生成的 model 结构体的字段，同时方法的定义需要是 `func(*gorm.DB) error` 类型的。之后就会自动完成绑定。

这其中的原理不是接口，因为如果是接口，这些方法就是必须要实现的，一个都不能少。这其中的原理是使用 golang 的**反射**，或者说是**隐式接口**。在做实际的 gorm 操作的时候，go 会尝试通过反射去检测这个 model 对象是不是带有这样的钩子函数。如果有就执行，没有包含这个方法也不会报错。

## store

首先在 store 层中定义了 IStore 接口，这个接口的定义如下：

```go
// IStore 定义了 Store 层需要实现的方法
type IStore interface {
	// 返回 Store 层的 *gorm.DB 实例，在少数场景下会被用到
	DB(ctx context.Context, wheres ...where.Where) *gorm.DB
	TX(ctx context.Context, fn func(ctx context.Context) error) error

	User() UserStore
	Post() PostStore
}
```

其中的 `DB()` 方法好理解，就是返回一个 `*gorm.DB` 类型的数据，也就是我们前面使用的 `db` 数据。还有一个方法 `TX()`，这个方法在定义中做的事情是，在上下文中去加一个 sql 中事务的键值对，一个固定的 `transactionKey{}` 对应一个事务环境，其实事务的定义也是 `*gorm.DB` 类型。但是 `TX()` 也只是定义出来了，实际并没有使用，也不好理解，所以就不多阐述了。

理解之后的 `User()` 和 `Post()`，只用一个 IStore 接口还是太抽象了，这里结合 IStore 类型的实体 datastore 来理解：

```go
// datastore 是 IStore 的具体实现
type datastore struct {
	core *gorm.DB
}
```

之后我们对 datastore 里面实现了 `DB()`、`TX()`、`User()`、`Post()` 这几个方法，所以 datastore 和 IStore 之间的关系是：

![image-20250828093748717](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250828093748717.png)

同时这里再以 User 部分的 UserStore 和 userStore 为例，说一下这几个 Store 之间的区别：

```go
// UserStore 定义了 user 模块在 store 层所实现的方法
type UserStore interface {
	Create(ctx context.Context, obj *model.User) error
	Update(ctx context.Context, obj *model.User) error
	Delete(ctx context.Context, opts *where.Options) error
	Get(ctx context.Context, opts *where.Options) (*model.User, error)
	List(ctx context.Context, opts *where.Options) (int64, []*model.User, error)

	UserExpansion
}

// userStore 是 UserStore 接口的实现
type userStore struct {
	store *datastore
}
```

其中，`userStore` 之中包含前面定义的 `datastore` 内容。同时，在 `store.go` 代码中，还定义了 `datastore` 是全局唯一的，一个项目中只会出现一个。所以全局中，datastore 是存储的核心，其中还包含唯一的 `core *gorm.DB`，也就是说 `db` 也是全局唯一的，这是符合之前的经验的。之后再创建 userStore 和 postStore，这两个结构体中包含 datastore，但是实际上是包含了那个 datastore 的地址，它们共用的同一份数据。

几个 store 之间的关系可以简单概括如下：

![image-20250828094254369](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250828094254369.png)

这是几个 store 类型的实体之间的关系，实际理解的话，肯定还需要结合抽象接口。但是初步理解，就将接口理解为：实体必须要实现的几个方法。对于有的接口，接口和实体几乎是一一对应的，比如说 IStore 可以说就是为 datastore 准备的，UserStore 就是为 userStore 准备的，postStore 就是为 PostStore 准备的。所以在这些实例中，可以将 IStore 中的方法看作是 datastore 的方法，我们写做接口，只是为了让编译器保证我们不要忘记实现了这几个方法。

所以这三大类型之间的关系如下：

![image-20250828094647187](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250828094647187.png)

那么这时候再回来重新理解 datastore 部分的字段，就比较好理解了。首先，创建 datastore 的时候，需要传入一个 `db`，并且要保证 datastore 全局只会被初始化一次，所以就有代码：

```go
// NewStore 创建一个 IStore 类型的实例
func NewStore(db *gorm.DB) *datastore {
	// 确保 S 只被初始化一次
	once.Do(func() {
		S = &datastore{db}
	})

	return S
}
```

之后对 datastore 的 `DB()` 方法的定义中，核心部分代码是：

```go
	// 遍历所有传入的条件并逐一叠加到数据库查询对象上
	for _, whr := range wheres {
		db = whr.Where(db)
	}
```

也就是说，这里的 `DB()` 方法，相比于直接返回 `core` 中的 `db`，加上了一些 `where` 的限制条件。之后返回的内容是加上了 `where` 限制条件的 `db` 对象。

同时 datastore 实现的 `IStore` 接口中，还提到了 `User()` 方法和 `Post()` 方法。这里其实就是：通过 datastore 去构建新的 `userStore` 和 `postStore`。比如说以 `User()` 方法为例：

```go
// User 返回一个实现了 UserStore 接口的实例
func (store *datastore) User() UserStore {
	return newUserStore(store)
}
```

这里提到，`User()` 方法应该是返回一个 `UserStore` 接口的类型。

```go
// newUserStore 创建 userStore 的实例
func newUserStore(store *datastore) *userStore {
	return &userStore{store}
}
```

但是查看 `newUserStore()` 方法的定义发现，这里返回的是一个 `*userStore` 类型的数据。按照我们之前的理论，接口类型就是一个类的指针类型，这里是在声明中是要返回 UserStore 接口类型，但是实现上，我们返回的是一个实现了接口的类型数据。这有点像是 C++ 中父类指针指向子类对象的例子，在 golang 中，就是将一个实体的指针，直接赋值给它实现了的接口的类型。go 虽然是强类型语言，但是这样的转换是允许的。

那为什么 `User()` 的定义中不定义为返回 `*userStore` 类型，而是定义为返回 `UserStore` 接口类型呢？我觉得还是，golang 中一个对象虽然就是一片固定的内存数据，但是如何使用它还得看用户如何去解释它，将它作为什么内容。虽然说这里直接返回 `userStore` 也是看似可以的，但是 `userStore` 中包含的数据就是一个简单的 `datastore` 内容。我们关注的重点不是这个类型中有没有 datastore，而是想要让返回的这个类型中要实现 `Create()`、`Update()` 之类的方法。所以说从这个抽象层上来说，使用 `UserStore` 更能体现我们想要表达的意思。

---

说完了整体的 store 的层级结构，接下来以 `userStore` 为例，讲一下 `UserStore` 接口中要求实现的几个方法，看我们在 `userStore` 实体中是如何实现的：

```go
// Create 插入一条用户记录
func (s *userStore) Create(ctx context.Context, obj *model.User) error {
	if err := s.store.DB(ctx).Create(&obj).Error; err != nil {
		slog.Error("Failed to insert user into database", "err", err, "user", obj)
		return errorsx.ErrDBWrite.WithMessage(err.Error())
	}

	return nil
}
```

`Create()` 方法也比较简单，就相当于直接调用了 `db.Create(&obj)` 方法，插入了一个 user。

```go
// Update 更新用户数据库记录
func (s *userStore) Update(ctx context.Context, obj *model.User) error {
	if err := s.store.DB(ctx).Save(obj).Error; err != nil {
		slog.Error("Failed to update user in database", "err", err, "user", obj)
		return errorsx.ErrDBWrite.WithMessage(err.Error())
	}

	return nil
}
```

`Update()` 方法也是直接调用了 `db.Save(obj)` 方法，对数据库中做了一个全量更新。

之后的 `Delete()`、`Get()`、`List()` 方法也都差不多，本质上都是 SQL 语句。

所以对 store 这部分的理解还是，这部分主要就是跟数据库进行交互的，所有的部分几乎都是为了跟 SQL 做一个对应。估计是等 handler 部分和 biz 部分做完审查，给出明确的需求之后，store 部分就负责把要存的数据直接存好就行。

对外暴露的接口，或者说与 store 层交互的方法的话，我觉得还是要上一层提供一个 `core *gorm.DB`，之后再通过这个 `core` 创建出一个 `datastore`，然后再通过这个 `datastore` 去创建去 `userStore` 和 `postStore`，然后做 SQL 操作的时候就在 `userStore` 和 `postStore` 中操作就行了。

![image-20250828172946146](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250828172946146.png)

## biz

### 总体定义

![image-20250828171853544](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250828171853544.png)

这里首先是定义了一个 IBiz 接口，以及实现了 IBiz 接口的 `biz` 类。对 IBiz 接口的定义如下：

```go
// IBiz 定义了业务层需要实现的方法
type IBiz interface {
	// 获取用户业务接口
	UserV1() userv1.UserBiz
	// 获取帖子业务接口
	PostV1() postv1.PostBiz
}
```

其中定义了 `UserV1()` 方法和 `PostV1()` 方法。我们现在就以 `User` 为例，这里的 `UserV1()` 函数的返回结果是 `UserBiz` 类型，而 `UserBiz` 也是一个接口。所以就可以推断出，在后面实际的部署中，这里应该是返回了一个 `*userBiz` 对象。

之后我们看实际使用的 `userBiz`，其中有一个字段是 store，这部分与 biz 部分相同。但是可以发现 biz 中提供了方法 `UserV1()`，可以从一个 `biz` 构建一个 `userBiz`。构建的方法是调用了 `user` 中的 `New()` 函数：

```go
// UserV1 返回一个实现了 UserBiz 接口的实例
func (b *biz) UserV1() userv1.UserBiz {
	return userv1.New(b.store)
}
```

其中 `userv1.New()` 方法定义为：

```go
func New(store store.IStore) *userBiz {
	return &userBiz{store: store}
}
```

也就是调用的时候传入 biz 自己的 store，之后直接把这个 store 作为字段的值，构建一个 userBiz 对象出来。user 中是这样的，post 中也是这样的。

这样一来，虽然我们有 biz、userBiz、postBiz 这三种不同的 biz，但是三种不同的 biz 中的变量字段都是同一个 store。其中 biz 应该只是用来抽象的，作用是从中构建出实际使用的 userBiz 和 postBiz 来处理业务。

所以 biz 部分之后使用的时候，是首先通过一个 store 来构建出一个 biz 对象，之后再通过这个 biz 对象构建出 userBiz 和 postBiz 这样的对象，用这两个东西来处理业务。

还记得 IStore 的定义是在 store 包中提供的，实现的实体是 datastore，其中就包含一个 `core *gorm.DB`。所以之后构建这两层的一个顺序就是提供一个 `db` 对象，之后通过这个 `db` 去构建出 `store` 这一层的内容。然后向上提供接口的时候，就是提供这个 `datastore` 对象。上一层 biz 又可以通过这个 `datastore` 去构建出一个 biz 层的业务：由 `store` 构建出 `biz`，只有又由 `biz` 构建出 `userBiz` 和 `postBiz`，然后就可以执行 `userBiz` 和 `postBiz` 中的业务了。

从 `store` 层提供的接口来看，`store` 层中的 `userStore` 和 `postStore` 都提供了 `Create()`、`Update()` 之类的方法，这些方法不做检查，都直接面向数据库底层，直接和数据库交互。

按照这部分的分析，biz 层中提供的方法应该是基于 store 层中提供的与数据库交互的 API，或者是用到了这些 API 的。

---

### user 和 post 共有部分

在 `userBiz` 和 `postBiz` 向上提供的接口方面，首先 User 和 Post 都提供了 `Create()`、`Update()`、`Delete()`、`Get()`、`List()` 这几种方法。这里以 User 为例，解析一下这几个方法都是什么作用。

```go
// Create 实现 UserBiz 接口中的 Create 方法
func (b *userBiz) Create(ctx context.Context, rq *apiv1.CreateUserRequest) (*apiv1.CreateUserResponse, error) {
	var userM model.User
	_ = copier.Copy(&userM, rq)

	if err := b.store.User().Create(ctx, &userM); err != nil {
		return nil, err
	}

	return &apiv1.CreateUserResponse{UserID: userM.UserID}, nil
}
```

首先就可以看到，biz 层提供的 `Create()` 方法和 store 层提供的 `Create()` 方法的参数是不一样的。\

- store 层：`func (s *userStore) Create(ctx context.Context, obj *model.User) error`
- biz 层：`func(b *userBiz) Create(ctx context.Context, rq *apiv1.CreateUserRequest) (*apiv1.CreateUserResponse, error)`

Store 层的 `Create()` 方法，提供的 context 不用说，这是每一部分都需要的。其次就是提供了一个 `obj`，就是直接要在 `db` 中的 `Create()` 方法中创建这个 `obj` 了。但是 biz 层是面向 http 的 request 和 response 的。这里输入的参数中，有一个 `CreateUserRequest`，返回的参数中也有一个 `CreateUserResponse`。

之后看 `Create()` 中的实现。不出所料，这里果然是调用了 `userBiz` 中的 `IStore`，或者说是 `datastore`。然后再通过一个 `User()` 方法得到一个 `userStore`，之后调用了 `userStore` 中的 `Create()` 方法，去与数据库交互。

其中还是用了 `copier` 库，将一个 rq 类型中的数据，直接 copy 到 userM 中。这里的 userM，是一个 model 类型的 user。因为后面是要与数据库进行交互的，所以就得使用 model 类型的 user。

接下来看看 `CreateUserRequest` 这个结构体的定义：

```go
// CreateUserRequest 表示创建用户请求
type CreateUserRequest struct {
	// username 表示用户名称
	Username string `json:"username"`
	// password 表示用户密码
	Password string `json:"password"`
	// nickname 表示用户昵称
	Nickname *string `json:"nickname"`
	// email 表示用户电子邮箱
	Email string `json:"email"`
	// phone 表示用户手机号
	Phone string `json:"phone"`
}
```

以及 model 类 User 的定义：

```go
// User 用户表
type User struct {
	ID        int64     `gorm:"column:id;primaryKey;autoIncrement:true" json:"id"`
	UserID    string    `gorm:"column:userID;not null;comment:用户唯一 ID" json:"userID"`                                    // 用户唯一 ID
	Username  string    `gorm:"column:username;not null;comment:用户名（唯一）" json:"username"`                                // 用户名（唯一）
	Password  string    `gorm:"column:password;not null;comment:用户密码（加密后）" json:"password"`                              // 用户密码（加密后）
	Nickname  string    `gorm:"column:nickname;not null;comment:用户昵称" json:"nickname"`                                   // 用户昵称
	Email     string    `gorm:"column:email;not null;comment:用户电子邮箱地址" json:"email"`                                     // 用户电子邮箱地址
	Phone     string    `gorm:"column:phone;not null;comment:用户手机号" json:"phone"`                                        // 用户手机号
	CreatedAt time.Time `gorm:"column:createdAt;not null;default:current_timestamp();comment:用户创建时间" json:"createdAt"`   // 用户创建时间
	UpdatedAt time.Time `gorm:"column:updatedAt;not null;default:current_timestamp();comment:用户最后修改时间" json:"updatedAt"` // 用户最后修改时间
}
```

`copier` 的执行原理是，如果有相同名称的字段就直接 copy，名称不相同，也没有定义处理的函数，就不做 copy 的操作。所以这里进行 copy 操作的时候，是将 `Username`、`Password`、`Nickname`、`Email`、`Phone` 这几个字段做了一个 copy。其余的字段中，`ID`、`CreatedAt`、`UpdatedAt` 都是数据库中自动生成记录的，`UserID` 是在钩子函数中，数据库插入一条记录之后根据 ID 去自动更新的。

---

之后看 `Update()` 方法：

```go
// Update 实现 UserBiz 接口中的 Update 方法
func (b *userBiz) Update(ctx context.Context, rq *apiv1.UpdateUserRequest) (*apiv1.UpdateUserResponse, error) {
	userM, err := b.store.User().Get(ctx, where.F("userID", contextx.UserID(ctx)))
	if err != nil {
		return nil, err
	}

	if rq.Username != nil {
		userM.Username = *rq.Username
	}
	if rq.Email != nil {
		userM.Email = *rq.Email
	}
	if rq.Nickname != nil {
		userM.Nickname = *rq.Nickname
	}
	if rq.Phone != nil {
		userM.Phone = *rq.Phone
	}

	if err := b.store.User().Update(ctx, userM); err != nil {
		return nil, err
	}

	return &apiv1.UpdateUserResponse{}, nil
}
```

业务层做一个 Update 操作，是执行了两次 SQL，第一次是执行了 store 层中的 `Get()` 方法，就是根据一定的条件，去查找一个符合条件的记录。比如说这里就是使用 `userID` 进行了限制，查找特定的一条记录。其中 `userID` 是从 `context` 中获取的，这里是我们在 cmd 中一开始就绑定了，`user` 部分的路由，除了 `Create` 还有 `Login` 操作，都是要做 token 绑定的。绑定了 token，之后就可以在 `context` 中找到一个 `userID` 的字段了。这里就是将 `userID` 从 context 中提取出来，然后从数据库中查找到一个 userM，是一个 model 类型的 User 对象。

`UpdateUserRequest` 的定义如下：

```go
// UpdateUserRequest 表示更新用户请求
type UpdateUserRequest struct {
	// username 表示可选的用户名称
	Username *string `json:"username"`
	// nickname 表示可选的用户昵称
	Nickname *string `json:"nickname"`
	// email 表示可选的用户电子邮箱
	Email *string `json:"email"`
	// phone 表示可选的用户手机号
	Phone *string `json:"phone"`
}
```

所以之后的逻辑就是，我们首先从数据库中拿到了这一条记录，将这一条记录转换为具体的对象，之后就开始判断 `request` 中是不是都提供了这几个值，如果提供了，那就对这个具体的对象的这一个字段进行修改。

修改完之后，再调用 `store` 层的 `Update()` 方法（底层还是使用了 gorm 中的 Save 全量更新），将数据做一个更新的操作。

---

`User` 中对 `Delete()` 操作的定义如下：

```go
// Delete 实现 UserBiz 接口中的 Delete 方法
func (b *userBiz) Delete(ctx context.Context, rq *apiv1.DeleteUserRequest) (*apiv1.DeleteUserResponse, error) {
	if err := b.store.User().Delete(ctx, where.F("userID", contextx.UserID(ctx))); err != nil {
		return nil, err
	}

	return &apiv1.DeleteUserResponse{}, nil
}
```

这里的 `Delete()` 其实从功能上来说，都比较多余。首先 `DeleteUserRequest` 和 `DeleteUserResponse` 结构体的定义都是空的，里面没有内容。而且函数内部也没有什么处理的逻辑，就是直接将 `context` 中的 `userID` 作为限制条件，直接调用了 store 层中的 `Delete()` 方法。

在 biz 层中加入 `Delete()` 方法，更多是为了做一个统一。

---

`User` 中对 `Get()` 方法的定义如下：

```go
// Get 实现 UserBiz 接口中的 Get 方法
func (b *userBiz) Get(ctx context.Context, rq *apiv1.GetUserRequest) (*apiv1.GetUserResponse, error) {
	userM, err := b.store.User().Get(ctx, where.F("userID", contextx.UserID(ctx)))
	if err != nil {
		return nil, err
	}

	return &apiv1.GetUserResponse{User: conversion.UserModelToUserV1(userM)}, nil
}
```

`Get()` 部分做的操作也不多，首先是 `GetUserRequest` 的定义是空的，`GetUserResponse` 中只有一个字段，是 user 的 proto 类型。因为这里的 request 和 response 都属于业务的部分，所以这部分使用 user 都是首先选择 proto 类型的，而不是 model 类型的。

这部分在逻辑方面，也是首先通过调用 store 层的 `Get()` 方法，与数据库交互，得到一个 `user` 的 `model` 类型数据。之后就开始组装 `GetUserResponse`，其中有一个 proto 类型的 `User` 字段，这里调用之前定义好的 `conversion` 包中的 `UserModelToUserV1()` 方法，将 user 的类型从 `model` 转换为 `proto`，然后再返回。

---

`User` 中对 `List()` 方法的定义是几个方法中逻辑最复杂的。我们分析的时候就一部分一部分进行拆解。

首先在 `List()` 方法的定义中，也是使用了我们定义的结构体 `ListUserRequest`，这部分的定义如下：

```go
// ListUsreRequest 表示用户列表请求
type ListUserRequest struct {
	// offset 表示偏移量
	Offset int64 `json:"offset"`
	// limit 表示每页数量
	Limit int64 `json:"limit"`
}
```

其中 `Offset` 表示查询的时候从数据库的第多少条记录开始查，Limit 表示本次查询返回的记录条数。

为什么这部分的逻辑比较复杂，主要是因为这部分的返回值类型 `ListUserResposne` 的定义如下：

```go
// ListUserResponse 表示用户列表响应
type ListUserResponse struct {
	// totalCount 表示总用户数
	TotalCount int64 `json:"totalCount"`
	// users 表示用户列表
	Users []*User `json:"users"`
}
```

其中提到了 `User`，这部分是 reponse 业务中使用的 User，所以就要使用 `biz` 中的 `User` 的 proto 定义，而这部分的 `User` 的定义中是有一个字段叫做 `postCount` 的，也就是这个用户拥有博客的数量。在 `ListUser` 中，我们是首先通过一定的限制条件，查找出来一批的用户，之后再查找出这些用户每个用户的博客数量，这样是比较复杂的。

其实按理来说，前面的 `Get()` 方法中也应该使用到这个 `postCount`，但是可能是精简了业务还是什么原因，并没有做。

代码中，首先是根据 `ListUserRequest` 中对查询的限制，查找出我们要操作的一部分 user，并保存到一个切片 `userList` 中：

```go
	whr := where.P(int(rq.Offset), int(rq.Limit))
	count, userList, err := b.store.User().List(ctx, whr)
	if err != nil {
		return nil, err
	}
```

之后的代码中，建立了一个 errgroup，对 `userList` 中的每一个 `user` 都启动一个 goroutine，去调用 `post` 的 store 层的代码，去查询这个用户有的博客的数量：

```go
	// 使用 goroutine 提高接口性能
	for _, user := range userList {
		eg.Go(func() error {
			select {
			case <-ctx.Done():
				return nil
			default:
				postCount, _, err := b.store.Post().List(ctx, where.F("userID", user.UserID))
				if err != nil {
					return err
				}

				converted := conversion.UserModelToUserV1(user)
				converted.PostCount = postCount
				m.Store(user.ID, converted)

				return nil
			}
		})
	}
```

查找出来博客的数量 `postCount` 之后，将原本的那个 `userList` 中带有的 `model` 类型的 `user` 转换成 `proto` 类型的 `user`，然后给这个 user 赋值 `PostCount` 字段。`m` 是前面定义的一个 `sync.Map`，其实就是一个 `map`，只不过这个类型是确保线程安全的。在其中保存好每一个 `user.ID` 对应的转换好之后的 `proto` 类型的 `user`。

```go
	users := make([]*apiv1.User, 0, len(userList))
	for _, item := range userList {
		user, _ := m.Load(item.ID)
		users = append(users, user.(*apiv1.User))
	}
```

这段代码是创建了一个 `users`，长度和 `userList` 相同，但是类型是 `proto` 类型的 `user`。看其中的逻辑，其实就是将一个 `model` 类型 `user` 的切片，转换成了一个 `proto` 类型的 `user` 的切片。

```go
	return &apiv1.ListUserResponse{TotalCount: count, Users: users}, nil
```

最后就是将查询到的用户列表 `users` 和长度 `count` 组装到 `ListUserResponse` 中一起做个返回。

---

### user 专属部分

除了上面的 `Create()` 等部分的 API 是 User 和 post 共有的，user 部分还有一些专属的 API：`Login()`、`RefreshToken()` 和 `ChangePassword()`。

首先是 `Login()` 函数。从函数的输入和输出来看，这个 API 的输入输出定义如下所示：

```go
// LoginRequest 表示登录请求
type LoginRequest struct {
	// username 表示用户名称
	Username string `json:"username"`
	// password 表示用户密码
	Password string `json:"password"`
}

// LoginResponse 表示登录响应
type LoginResponse struct {
	// token 表示返回的身份验证令牌
	Token string `json:"token"`
	// expireAt 表示该 token 的过期时间
	ExpireAt time.Time `json:"expireAt"`
}
```

登录的时候，在请求中需要加入登录使用的 `username` 和 `password`。在登录的响应上，需要加入登录时使用的 `token` 令牌和 `expireAt` 过期时间。

之后我们看 `Login()` 中的处理逻辑，首先通过如下的代码，由用户请求中的 `username`，得到数据库中的这一条记录：

```go
	// 获取登录用户的所有信息
	whr := where.F("username", rq.Username)
	userM, err := b.store.User().Get(ctx, whr)
	if err != nil {
		return nil, errorsx.ErrUserNotFound
	}
```

如果说数据库中确实有这一条记录，接下来做的就是密码的匹配：

```go
	// 对比传入的明文密码和数据库中已加密过的密码是否匹配
	if err := auth.Compare(userM.Password, rq.Password); err != nil {
		slog.ErrorContext(ctx, "Failed to compare password", "err", err)
		return nil, errorsx.ErrPasswordInvalid
	}
```

匹配使用的是 `auth.Compare()` 方法。这个方法中，将一个明文和密文进行对比。在创建用户的时候，用户会提供一个密码的明文，但是我们服务器中的做法是将这个明文编码成哈希形式，然后只在服务器中保存这个密码的哈希形式。之后登录的时候，也是将用户提供的明文进行哈希编码，然后对比此处的编码之后的哈希密文和数据库中的密文是否相同。

这部分的处理逻辑，从安全上来说，肯定是比较安全的。但是也有缺点，比如说我即使作为管理员，从数据库中也无法得知一个用户的密码到底是多少。除此之外，如果发生了哈希碰撞，可能用户会通过另一种毫不相干的密码登录上自己的账户。但是这种情况只需要从原理上理解一下就行，实际应用中几乎不会发生。

如果登录的密码是正确的，接下来就可以签发 token 令牌了：

```go
	// 如果匹配成功，说明登录成功，签发 token 并返回
	tokenStr, expireAt, err := token.Sign(userM.UserID)
	if err != nil {
		slog.ErrorContext(ctx, "Failed to sign token", "err", err)
		return nil, errorsx.ErrSignToken
	}

	return &apiv1.LoginResponse{Token: tokenStr, ExpireAt: expireAt}, nil
```

这部分是调用了 `token` 包中的 `Sign()` 方法，根据 `UserID` 签发一个用户登录的令牌，然后返回 `tokenStr` 令牌字符串。

---

`RefreshToken()` 方法的定义如下：

```go
// RefreshToken 用于刷新用户的身份验证令牌
// 当用户的令牌即将过期时，可以调用此方法生成一个新的令牌
func (b *userBiz) RefreshToken(ctx context.Context, rq *apiv1.RefreshTokenRequest) (*apiv1.RefreshTokenResponse, error) {
	// 如果匹配成功，说明登录成功，签发 token 并返回
	tokenStr, expireAt, err := token.Sign(contextx.UserID(ctx))
	if err != nil {
		return nil, errorsx.ErrSignToken.WithMessage(err.Error())
	}
	return &apiv1.RefreshTokenResponse{Token: tokenStr, ExpireAt: expireAt}, nil
}
```

其中，`RefreshTokenRequest` 结构体的定义为空，其中也没有任何内容，因为做这个操作是基于 token 令牌登录上做的，这时候 context 中已经有用户的 `userID` 了。

`RefreshTokenResponse` 的定义与 `LoginResponse` 的定义相同，都是包含签发的令牌的字符串，以及令牌的过期时间：

```go
// RefreshTokenResponse 表示刷新令牌的响应
type RefreshTokenResponse struct {
	// token 表示返回的身份验证令牌
	Token string `json:"token"`
	// expireAt 表示该 token 的过期时间
	ExpireAt time.Time `json:"expireAt"`
}
```

方法执行的逻辑，其实就是简单调用了一下 `token.Sign()` 方法。只不过在 `Login()` 的时候调用这个方法之前，需要通过登录来获取 `userID` 这个字段。但是这里使用 `RefreshToken`，是建立在已经登录过，已经获取了 `token` 的前提下。所以这里登录信息是已经信任的，可以直接通过 token 中的 `userID`，调用 `token.Sign()` 方法。

---

`ChangePassword` 方法：

`ChangePasswordRequest` 请求结构体的定义如下，其中就包含两个部分，以前的老密码和要改的新密码。`ChangePasswordResponse` 就是一个空的结构体。

```go
// ChangePasswordRequest 表示修改密码的请求
type ChangePasswordRequest struct {
	// oldPassword 表示当前密码
	OldPassword string `json:"oldPassword"`
	// newPassword 表示准备修改的新密码
	NewPassword string `json:"newPassword"`
}
```

逻辑方面，首先从 token 令牌中，拿到用户的 `userID`，之后通过这个 `userID`，拿到 user 的 model 对象。

随后做了一个比较密码的操作：

```go
	if err := auth.Compare(userM.Password, rq.OldPassword); err != nil {
		slog.ErrorContext(ctx, "Failed to compare password", "err", err)
		return nil, errorsx.ErrPasswordInvalid
	}
```

这里比较的两个值，一个是来自查询数据库中的 user 的 model 对象的 `Password` 字段，另一个是 `request` 中的 `OldPassword` 字段。同时，`userM` 中的数据是一个密文，`OldPassword` 中是一个明文。明文和密文的比较逻辑已经在 `auth.Compare()` 中实现。

```go
	userM.Password, _ = auth.Encrypt(rq.NewPassword)
	if err := b.store.User().Update(ctx, userM); err != nil {
		return nil, err
	}
```

如果说比较成功了，那就需要在数据库中去更新这部分的密码。这里使用的方法是，首先将 `request` 中输入的 `password` 给编码成哈希的形式，之后将编码之后的哈希形式的密文密码，更新到 `userM` 对象中，再调用一个 `Update()` 方法，将 `userM` 写到数据库中。

## handler

Handler 部分，首先是定义了 `Handler` 的组成部分，以及 `NewHandler` 的方法：

```go
// Handler 处理博客模块的请求
type Handler struct {
	biz biz.IBiz
	val *validation.Validator
}

// NewHandler 创建新的 Handler 实例
func NewHandler(biz biz.IBiz, val *validation.Validator) *Handler {
	return &Handler{
		biz: biz,
		val: val,
	}
}
```

可以看到，其中的 handler 是包含 biz 部分的。同时 biz 部分中又包含了 store 部分，所以这部分又是一个包含的关系。从前我们首先创建了 store 部分，之后 store 部分的 datastore 作为一个成员，做了 biz 部分的组成部分。之后又让 biz 作为一个字段，做了 handler 部分的组成部分。

这样的话，从构建方式来看，只要提供 store 部分中核心的 `db`，就可以一直构建到 handler 层；从使用方面来看，只要有了 handler 对象，就可以使用 handler、biz、store 部分的所有功能。

这个包中没有复杂的变量定义，只有一个 `Handler` 结构体的定义。字段就是简单的 `biz` 和 `validation`。但是提供的很多的 api 函数，例如：

- `CreatePost()`
- `UpdatePost()`
- `CreateUser()`
- `UpdateUser()`
- `Login()`
- ……

这里再次以 user 为例，解析其中的几个函数。首先是 `CreateUser()` 方法：

```go
func (h *Handler) CreateUser(c *gin.Context) {
	slog.Info("Create user function called")
    // ...
}
```

从这一层函数的 API 接口来看，这一层函数在输入输出上，都统一为，输入就是一个简单的 `gin.Context`，输出都是空。

之后根据 `CreateUse()` 的需求，创建了一个 `CreateUserRequest` 的结构体：

```go 
	var rq v1.CreateUserRequest
	if err := c.ShouldBindJSON(&rq); err != nil {
		core.WriteResponse(c, nil, errorsx.ErrBind)
		return
	}
```

同时，这里还有一个核心函数是：`c.ShouldBindJSON()`。虽然在 biz 层中我们定义了 `CreateUserRequest` 这样的结构体，但是 handler 层中也是有 request 的，这部分就在 `c.Request` 部分中。

这里的 `ShouldBindJSON()` 就是尝试去：将 `Handler` 中的 `c.Request` 转换为 `Biz` 中的 `CreateUserRequest`。如果这里转换出错了，也就是用户访问 url 的时候提供的参数或者请求体内容不正确，就直接使用 `core.WriteResponse()` 返回了。

如果上一步 `ShouldBIndJSON()` 通过了，那就说明已经构建了一个 `CreateUserRequest` 了。根据我们的直觉，接下来就应该将这个 `CreateUserRequest` 传入给 biz 层的 `CreateUser()` 的方法了。但是这里还做了一个`validation` 的操作。这部分是使用 `Handler` 结构体中的 `validation` 部分实现的。

```go
	if err := h.val.ValidateCreateUserRequest(c.Request.Context(), &rq); err != nil {
		core.WriteResponse(c, nil, errorsx.ErrInvalidArgument.WithMessage(err.Error()))
		return
	}
```

具体来说，`ValidateCreateUserRequest()` 方法的定义为：

```go
func (v *Validator) ValidateCreateUserRequest(ctx context.Context, rq *v1.CreateUserRequest) error {
	// Validate username
	if rq.Username == "" {
		return errors.New("username cannot be empty")
	}
	if len(rq.Username) < 4 || len(rq.Username) > 32 {
		return errors.New("username must be between 4 and 32 characters")
	}
    //...
}
```

就是，`CreateUserRequest` 中有几个不同的字段，比如说 `username`、`password`、`nickname` 等。然后这里我们通过一个 `Validate()` 方法，来验证这个请求中的各个参数是不是合理的，比如说 `username` 不能为空、不能过长等问题。

`Validate()` 方法中具体是什么内容，其实还是取决于 `CreateUserRequest` 结构体中的字段内容。有一些 `Request` 的结构体定义中，就一个字段都没有，所以 `Validate()` 方法的内容也是空的。或者是后面还有一些方法，它们的 `Request` 部分并非一个字段都没有，但是后面就是比较偷懒，所以 `Validate()` 方法就只做了空实现，直接返回“Validate 通过”的结果。

在 `Validate()` 方法结束之后，就可以调用 `biz` 中的方法了：

```go
	resp, err := h.biz.UserV1().Create(c.Request.Context(), &rq)
	if err != nil {
		core.WriteResponse(c, nil, err)
		return
	}
```

这里就是将我们上面从 `handler` 中绑定出来的 `Request` 结构体，传给 `biz` 中的 `Create()` 方法。如果这里出错了，就直接返回错误的 http 信息。

```go
	core.WriteResponse(c, resp, nil)
```

如果上面的部分成功了，就可以将 biz 中返回的业务信息，放到 `WriteResponse()` 中，返回给客户端。

## 总结

总结来看，代码的 internal-apiserver 部分的总架构如图所示：

![image-20250831101820945](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250831101820945.png)

由 `handler` 层调用 `biz` 层，又由 `biz` 层调用 `store` 层。如果是从下到上分析，这是从构建方面去分析的。首先有了 `db *gorm.DB` 之后，就可以构建出 store 层中的 `datastore`。之后根据 `datastore` 构建出 `biz` 业务层中的 biz 对象，这样就可以处理业务层中的 request 和 response。同时在 biz 层上面，又根据 biz 对象构建出 `handler` 对象。这部分也是处理 request 请求的，不过是处理的 http 部分的 request，也就是 `gin.Request` 部分的内容。

如果是从上到下分析，那就是，从使用方面去分析。客户端在交互的时候，只与 `handler` 部分进行交互，并且在 curl 访问的 url 中，构建出 http 的 request 请求。之后使用 http 的 request 请求，在后端底层，会将 http 的 request 请求转换为 `biz` 层的 `request` 请求。然后 `biz` 部分的处理的时候，是要操作数据库的。在 `biz` 层确定了要如何操作数据库之后，就会使用 `biz` 对象中的 `store` 部分，执行直接与数据库交互的操作。

在照着抄代码的时候，只觉得很多设计都是复杂且没有必要的。现在来看，其实也确实可以将所有的操作全都集中到 handler 层面，用一个函数直接将某一个请求，一步到位。但是那样的话代码的维护性会很差。我这个项目还比较小，这时候分层设计所展示出来的效果好不算特别好。但是这一次仔细研究代码，第一次体会到这种设计的巧妙。之前的 java 那里也有过类似分层的设计，但是之前一直不懂每一部分都是做什么的，这一次终于算是通过这个项目搞清楚 handler、biz、store 这几个层的业务逻辑了。

这种分层的设计方式还是很有研究的必要的！

















