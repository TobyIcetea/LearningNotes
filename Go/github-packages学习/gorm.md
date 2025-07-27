# gorm

## 介绍

go 的 gorm，有点像是 java 的 jdbc。就是编程语言和数据库之间交互的接口。

GORM 表示 `go object relationship map`，就是 golang 的对象关系映射。golang 操作数据库的方式是在本地建立和表中元素结构相同的结构体，之后以修改结构体的方式来操作数据库。

以 mysql 为例，学习的时候主要是学习两个库：

- `gorm.io/gorm`：所有的增删改查的实际操作都在这里。
- `gorm.io/driver/mysql`：只是用来连接 `mysql` 的。

也就是说 `mysql` 部分就是提供了一层驱动，有 `mysql` 的库，同时也有：`gorm.io/driver/sqlite` 之类的其他数据库连接的库。

本次学习的时候，主要集中于 `mysql` 部分的数据库操作。

## mysql 登录问题

在此之前，我首先遇到了 mysql 登录的问题。比较奇怪，具体如下所示：

| 登录方式                        | 结果       |
| ------------------------------- | ---------- |
| `mysql -u root -p`              | 可以登录 ✅ |
| `mysql -h localhost -u root -p` | 可以登录 ✅ |
| `mysql -h 127.0.0.1 -u root -p` | 不能登录 ❌ |

具体原因好像是，mysql 的登录分为两种，一种是 Unix Socket 方式，一种是 TCP 方式。比如说前两种方式就是通过 Socket 方式进行登录的，指定 127 的 IP 的方式就是通过 TCP 方式来登录的。

但是 MySQL 会自动做一个解析，比如说看到了 `127.0.0.1` 之后，自动给我解析成了 `localhost`。主机名变了，但是实际使用的登录方式（TCP 方式）并没有变。此时就变成了：使用 `localhost` 通过 TCP 方式进行登录。这样是不允许的。

当时的用户表已经不记得了，搞了很多次，也不知道一开始是啥样的了。

简单说一下解决方式：

第一种，直接修改 `/etc/my.cnf` 文件。在其中加入：

```go
[mysqld]
skip-name-resolve  // 在 [mysqld] 下面加上这一行
```

这表示之后不要做域名解析了。自然就能解决问题。之后再执行：

```bash
systemctl restart mariadb
```

如果上面还没有解决，就执行：

```sql
# 完全删除 root@localhost 并且建立 root@127.0.0.1，这样 127 是解析不到 localhost 的
DROP USER 'root'@'localhost';
CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED BY 'BW021129';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

```sql
# 为了保持 mysql -u root -p 的便利性，可以再把 root@localhost 加回来
CREATE USER 'root'@'localhost' IDENTIFIED BY 'BW021129';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

此时就可以使用如下的 DSN 来在 golang 中登录 mysql：

```go
dsn := "root:BW021129@tcp(127.0.0.1:3306)/fastgo?charset=utf8mb4&parseTime=True&loc=Local"
```

## 安装

```go
go get gorm.io/gorm
go get gorm.io/driver/mysql
```

## GORM 核心

### 连接数据库

这里我提前创建了一个数据库，叫做 `testdb`。

```sql
DROP DATABASE IF EXISTS testdb;
CREATE DATABASE testdb;
ALTER DATABASE testdb CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
```

主程序代码：

```go
func main() {
	// 1. 配置 DSN（Data Source Name）
	// 格式："用户名:密码@tcp(地址:端口)/数据库名?参数"
	dsn := "root:BW021129@tcp(127.0.0.1:3306)/testdb?charset=utf8&parseTime=True&loc=Local"

	// 2. 配置 GORM 日志（开发时建议开启）
	newLogger := logger.New(
		log.New(os.Stdout, "\r\n", log.LstdFlags), // 输出到控制台
		logger.Config{
			SlowThreshold: time.Second, // 慢查询阈值
			LogLevel:      logger.Info, // 日志级别（Slient, Error, Warn, Info）
			Colorful:      true,        // 彩色输出
		},
	)

	// 3. 连接数据库
	db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{
		Logger: newLogger, // 启用日志
	})
	if err != nil {
		panic("连接数据库失败:" + err.Error())
	}

	// 4. 获取底层 *sql.DB 对象（用于设置连接池）
	sqlDB, err := db.DB()
	if err != nil {
		panic("获取底层连接失败:" + err.Error())
	}

	// 5. 配置连接池（关键！生产环境必须设置）
	sqlDB.SetMaxIdleConns(10)           // 最大空闲连接数
	sqlDB.SetMaxOpenConns(100)          // 最大打开连接数
	sqlDB.SetConnMaxLifetime(time.Hour) // 连接最大生存时间

	// 6. 验证连接
	if err := sqlDB.Ping(); err != nil {
		panic("数据库连接失败")
	}

	log.Println("✅ 数据库连接成功！")
}
```

输出：

```go
[root@JiGeX gorm-demo]# go build . && ./gorm-demo 
2025/07/27 18:51:49 ✅ 数据库连接成功！
```

### 定义 go 模型

模型和 go 结构体与数据库表的映射关系。GORM 会根据结构体自动生成表结构。

```go
// User 模型（对应 users 表）
type User struct {
	ID        uint      `gorm:"primarykey"`        // 主键（自动递增）
	Name      string    `gorm:"size:100,not null"` // NOT NULL 约束
	Email     string    `gorm:"uniqueIndex"`       // 唯一索引（自动创建）
	Age       int       `gorm:"check:age > 0"`     // 检查约束（MySQL 8.0+）
	CreatedAt time.Time // 自动管理
	UpdatedAt time.Time // 自动管理
}
```

### 迁移表结构

上面我们定义了 User 结构，接下来 GORM 可以自动生成基于 User 结构体定义的 users 表结构。

```go
func main() {
    // ...
    // 连接数据库的代码
    
    // 自动迁移（创建或更新表结构）
	err = db.AutoMigrate(&User{})
	if err != nil {
		panic("表迁移失败")
	}

	log.Println("✅ 表结构已同步！")
}
```

输出：

```go
[root@JiGeX gorm-demo]# go build . && ./gorm-demo 
2025/07/27 19:06:05 ✅ 数据库连接成功！

2025/07/27 19:06:05 /root/goProjects/package-demo/gorm-demo/main.go:66
[1.341ms] [rows:-] SELECT DATABASE()

2025/07/27 19:06:06 /root/goProjects/package-demo/gorm-demo/main.go:66
[10.073ms] [rows:1] SELECT SCHEMA_NAME from Information_schema.SCHEMATA where SCHEMA_NAME LIKE 'testdb%' ORDER BY SCHEMA_NAME='testdb' DESC,SCHEMA_NAME limit 1

2025/07/27 19:06:06 /root/goProjects/package-demo/gorm-demo/main.go:66
[7.007ms] [rows:-] SELECT count(*) FROM information_schema.tables WHERE table_schema = 'testdb' AND table_name = 'users' AND table_type = 'BASE TABLE'

2025/07/27 19:06:06 /root/goProjects/package-demo/gorm-demo/main.go:66
[49.267ms] [rows:0] CREATE TABLE `users` (`id` bigint unsigned AUTO_INCREMENT,`name` longtext,`email` longtext,`age` bigint,`created_at` datetime(3) NULL,`updated_at` datetime(3) NULL,PRIMARY KEY (`id`),UNIQUE INDEX `idx_users_email` (`email`),CONSTRAINT `chk_users_age` CHECK (age > 0))
2025/07/27 19:06:06 ✅ 表结构已同步！

// 这是第一次的输出，后面再执行的时候，输出跟这个还不一样
```

新建的表默认命名为 `users`，当然也可以通过其他的设定来改。表的结构如下：

```go
MariaDB [testdb]> desc users;
+------------+---------------------+------+-----+---------+----------------+
| Field      | Type                | Null | Key | Default | Extra          |
+------------+---------------------+------+-----+---------+----------------+
| id         | bigint(20) unsigned | NO   | PRI | NULL    | auto_increment |
| name       | longtext            | YES  |     | NULL    |                |
| email      | longtext            | YES  | UNI | NULL    |                |
| age        | bigint(20)          | YES  |     | NULL    |                |
| created_at | datetime(3)         | YES  |     | NULL    |                |
| updated_at | datetime(3)         | YES  |     | NULL    |                |
+------------+---------------------+------+-----+---------+----------------+
```

### Create 创建

```go
// 创建用户
func createUser(db *gorm.DB) User {
	user := User{Name: "张三", Email: "zhangsan@example.com", Age: 25}
	result := db.Create(&user) // 会自动设置 ID、CreateAt、UpdateAt
	if result.Error != nil {
		panic("创建失败: " + result.Error.Error())
	}
	fmt.Printf("✅ 创建成功！ID: %d, 耗时: %v\n", user.ID, result.RowsAffected)
	return user
}
```

### Query 查询

```go
// 查询用户
func queryUser(db *gorm.DB, id uint) {
	var user User

	// 主键查询
	if err := db.First(&user, id).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			log.Printf("用户 ID %d 不存在\n", id)
			return
		}
		panic("查询失败: " + err.Error())
	}

	log.Printf("主键查询结果 —— ID: %d, 姓名: %s, 邮箱: %s, 年龄: %d, 创建时间: %s\n",
		user.ID, user.Name, user.Email, user.Age, user.CreatedAt.Format("2006-01-02 15:04:05"))

	// 条件查询示例
	var users []User
	db.Where("age > ?", 18).
		Order("created_at DESC").
		Limit(5).
		Find(&users)

	log.Println("条件查询结果:")
	for _, u := range users {
		log.Printf("ID=%d, Name=%s, Email=%s, Age=%d, CreatedAt=%s\n",
			u.ID, u.Name, u.Email, u.Age, u.CreatedAt.Format("2006-01-02 15:04:05"))
	}
}
```

### Update 更新

```go
// 更新用户
func updateUser(db *gorm.DB, id uint) {
	var user User
	if err := db.First(&user, id).Error; err != nil {
		panic("用户不存在: " + err.Error())
	}

	// 方式 1：更新单个字段
	db.Model(&user).Update("age", 26)
	log.Println("更新年龄为 26！")

	// 方式 2：全量更新（使用 Save）
	user.Name = "张三-更新"
	user.Age = 27
	if err := db.Save(&user).Error; err != nil {
		panic("更新失败: " + err.Error())
	}
	log.Printf("全量更新成功: %+v\n", user)
}
```

### Delete 删除

```go
// 删除用户
func deleteUser(db *gorm.DB, id uint) {
	var user User
	if err := db.First(&user, id).Error; err != nil {
		panic("用户不存在: " + err.Error())
	}

	// 软删除（推荐）
	result := db.Delete(&user)
	log.Printf("删除结果：影响行数=%d\n", result.RowsAffected)

	// 验证是否删除（使用 Unscoped 查询软删除记录）
	var count int64
	db.Unscoped().Model(&User{}).Where("id = ?", id).Count(&count)
	log.Printf("删除后验证：记录数=%d（0 表示已删除）\n", count)
}
```

### 综合测试

首先将“连接数据库”和“迁移表结构”的代码也打包成函数：

```go
// 初始化数据库连接
func initDB() *gorm.DB {
	// 1. 配置 DSN（Data Source Name）
	// 格式："用户名:密码@tcp(地址:端口)/数据库名?参数"
	dsn := "root:BW021129@tcp(127.0.0.1:3306)/testdb?charset=utf8mb4&collation=utf8mb4_unicode_ci&parseTime=True&loc=Local"

	// 2. 配置 GORM 日志（开发时建议开启）
	newLogger := logger.New(
		log.New(os.Stdout, "\r\n", log.LstdFlags), // 输出到控制台
		logger.Config{
			SlowThreshold: time.Second, // 慢查询阈值
			LogLevel:      logger.Info, // 日志级别（Slient, Error, Warn, Info）
			Colorful:      true,        // 彩色输出
		},
	)

	// 3. 连接数据库
	db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{
		Logger: newLogger, // 启用日志
	})
	if err != nil {
		panic("连接数据库失败:" + err.Error())
	}

	// 4. 获取底层 *sql.DB 对象（用于设置连接池）
	sqlDB, err := db.DB()
	if err != nil {
		panic("获取底层连接失败:" + err.Error())
	}

	// 5. 配置连接池（关键！生产环境必须设置）
	sqlDB.SetMaxIdleConns(10)           // 最大空闲连接数
	sqlDB.SetMaxOpenConns(100)          // 最大打开连接数
	sqlDB.SetConnMaxLifetime(time.Hour) // 连接最大生存时间

	// 6. 验证连接
	err = sqlDB.Ping()
	if err != nil {
		panic("数据库连接失败")
	}

	log.Println("✅ 数据库连接成功！")

	return db
}

// 自动迁移表结构（带字符串保障）
func autoMigrate(db *gorm.DB) {
	// 自动迁移（创建或更新表结构）
	err := db.AutoMigrate(&User{})
	if err != nil {
		panic("表迁移失败")
	}

	log.Println("✅ 表结构已同步！")
}
```

之后创建 main 函数：

```go
func main() {
	// 1. 初始化数据库
	db := initDB()

	// 2. 自动迁移
	autoMigrate(db)

	// 3. ===== 测试 CRUD 操作 =====
	log.Println("===== 创建用户 =====")
	user := createUser(db)

	log.Println("===== 查询用户 =====")
	queryUser(db, user.ID)

	log.Println("===== 更新用户 =====")
	updateUser(db, user.ID)

	log.Println("===== 删除用户 =====")
	deleteUser(db, user.ID)
}
```

输出：

```go
2025/07/27 19:51:29 ===== 创建用户 =====

2025/07/27 19:51:29 /root/goProjects/package-demo/gorm-demo/main.go:84
[2.808ms] [rows:1] INSERT INTO `users` (`name`,`email`,`age`,`created_at`,`updated_at`) VALUES ('张三','zhangsan@example.com',25,'2025-07-27 19:51:29.184','2025-07-27 19:51:29.184') RETURNING `id`
✅ 创建成功！ID: 10, 耗时: 1

--------------------------------------------------------------------------------------------------

2025/07/27 19:51:29 ===== 查询用户 =====

2025/07/27 19:51:29 /root/goProjects/package-demo/gorm-demo/main.go:97
[0.696ms] [rows:1] SELECT * FROM `users` WHERE `users`.`id` = 10 ORDER BY `users`.`id` LIMIT 1
2025/07/27 19:51:29 主键查询结果 —— ID: 10, 姓名: 张三, 邮箱: zhangsan@example.com, 年龄: 25, 创建时间: 2025-07-27 19:51:29

2025/07/27 19:51:29 /root/goProjects/package-demo/gorm-demo/main.go:113
[0.631ms] [rows:1] SELECT * FROM `users` WHERE age > 18 ORDER BY created_at DESC LIMIT 5
2025/07/27 19:51:29 条件查询结果:
2025/07/27 19:51:29 ID=10, Name=张三, Email=zhangsan@example.com, Age=25, CreatedAt=2025-07-27 19:51:29

--------------------------------------------------------------------------------------------------

2025/07/27 19:51:29 ===== 更新用户 =====

2025/07/27 19:51:29 /root/goProjects/package-demo/gorm-demo/main.go:125
[0.516ms] [rows:1] SELECT * FROM `users` WHERE `users`.`id` = 10 ORDER BY `users`.`id` LIMIT 1

2025/07/27 19:51:29 /root/goProjects/package-demo/gorm-demo/main.go:130
[2.337ms] [rows:1] UPDATE `users` SET `age`=26,`updated_at`='2025-07-27 19:51:29.189' WHERE `id` = 10
2025/07/27 19:51:29 更新年龄为 26！

2025/07/27 19:51:29 /root/goProjects/package-demo/gorm-demo/main.go:136
[3.276ms] [rows:1] UPDATE `users` SET `name`='张三-更新',`email`='zhangsan@example.com',`age`=27,`created_at`='2025-07-27 19:51:29.184',`updated_at`='2025-07-27 19:51:29.191' WHERE `id` = 10
2025/07/27 19:51:29 全量更新成功: {ID:10 Name:张三-更新 Email:zhangsan@example.com Age:27 CreatedAt:2025-07-27 19:51:29.184 +0800 CST UpdatedAt:2025-07-27 19:51:29.191 +0800 CST}

--------------------------------------------------------------------------------------------------

2025/07/27 19:51:29 ===== 删除用户 =====

2025/07/27 19:51:29 /root/goProjects/package-demo/gorm-demo/main.go:145
[0.737ms] [rows:1] SELECT * FROM `users` WHERE `users`.`id` = 10 ORDER BY `users`.`id` LIMIT 1

2025/07/27 19:51:29 /root/goProjects/package-demo/gorm-demo/main.go:150
[2.248ms] [rows:1] DELETE FROM `users` WHERE `users`.`id` = 10
2025/07/27 19:51:29 删除结果：影响行数=1

2025/07/27 19:51:29 /root/goProjects/package-demo/gorm-demo/main.go:155
[3.129ms] [rows:1] SELECT count(*) FROM `users` WHERE id = 10
2025/07/27 19:51:29 删除后验证：记录数=0（0 表示已删除）
```

## 总结

TODO：总结一下 CURD 的几个核心的方法。

