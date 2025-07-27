# jwt

## 介绍

JWT（Json Web Token）是一种 token 认证机制。

它主要作用于，如果我们要多次访问一个服务器，没有使用 JWT 的话，每一次都要重新认证一次，这样会造成服务器压力过大。

这时候就可以生成一个 token，并且设定一个过期的时间。在过期之前，使用这个 token 令牌来访问服务器，服务器就会让用户通行。从而减少服务器的压力。

一个 JWT 由三部分组成：

```go
xxxxxx.yyyyyy.zzzzzz
 ↑       ↑       ↑
Header.Payload.Signature
```

Header 是头部，说明这个 JWT 使用的是什么签名算法，是什么类型的，如：

```go
{
  "alg": "HS256",  // 表示使用的签名算法，比如 HS256、RS256
  "typ": "JWT"     // token 类型，固定为 JWT
}
```

Payload 是这个 JWT 携带的信息，如果将一个 JWT 比作是一个通行证，例如拿登机证举例吧，JWT 中不仅仅是写了“允许通行”四个字就完了，里面还会带着登机者的其他的信息。如：

```go
{
  "username": "alice",  // 自定义字段：用户名
  "role": "admin",		// 自定义字段：角色
  "exp": 1712345678,	// expiration：过期时间
  "iat": 1712259278		// issued at：签发时间
}
```

Signature 是签名，是一个“防伪章”，目的是保证 JWT 没有被篡改。

签名是通过 Header、Payload、secretKey 共同生成的。对于一个服务，一个服务器中只存在一个 `secretKey`，具体内容只有服务器知道，不会告诉用户。

JWT 是一个无状态的通行证，也就是说，如果我得到了一个 JWT，那么后面我把这个通行证借给我的朋友，我的朋友完全可以伪装成我，去跟服务器交互。

但是他不能修改其中的信息。因为服务器会对 JWT 进行验证。服务器接收到的 JWT，包含 `Header`、`Payload`、`Signature` 三部分信息。服务器会使用 `secret` + `Header` + `Payload` 三部分共同来计算，这个 JWT 的 `Signature` 应该是什么，之后再和用户发来的 JWT 中的 `signature` 进行比对。如果不对的话，肯定 JWT 中的信息就别篡改了，这就是一个不合格的令牌。

## 安装

```go
go get "github.com/golang-jwt/jwt/v5"
```

## demo

### 生成最简单的 JWT Token

```go
func main() {
	// 1. 定义密钥（实际项目中会从环境变量中读取）
	secretKey := []byte("abcdefghijklmnopqrstuvwxyz123456") // 至少 32 个字符

	// 2. 创建 Payload（业务数据）
	// 这部分做完，就生成了 JWT 的 payload 部分
	claims := jwt.MapClaims{
		"username": "alice",                               // 自定义字段
		"role":     "admin",                               // 自定义字段
		"exp":      time.Now().Add(time.Hour * 24).Unix(), // 24 小时过期（必须字段）
	}

	// 3. 生成 token
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims) // 指定 HS256 算法（生成 header 部分）
	signedToken, err := token.SignedString(secretKey)          // 用密钥签名（生成 signature 部分）
	if err != nil {
		panic(err)
	}

	fmt.Println("生成的 token:", signedToken)
}
```

运行结果：

```go
[root@JiGeX jwt-demo]# go build . && ./jwt-demo 
生成的 token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTM1ODIyNTEsInJvbGUiOiJhZG1pbiIsInVzZXJuYW1lIjoiYWxpY2UifQ.udbcTgPpuT4Xl8c6E_naF0xJQqYRaO6YQZx-zexeeRg
```

### 解析并验证 JWT

```go
func main() {
	// 从 HTTP 请求头拿到的 token（demo1 生成的）
	tokenString := "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTM1ODIyNTEsInJvbGUiOiJhZG1pbiIsInVzZXJuYW1lIjoiYWxpY2UifQ.udbcTgPpuT4Xl8c6E_naF0xJQqYRaO6YQZx-zexeeRg"

	// 1. 定义密钥（必须和生成时候是一致的）
	secretKey := []byte("abcdefghijklmnopqrstuvwxyz123456")

	// 2. 解析 token
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		// 验证算法是否是预期的（防止算法被篡改攻击）
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("意外的签名方法: %v", token.Header["alg"])
		}
		return secretKey, nil // 返回密钥
	})

	// 3. 检查错误
	if err != nil {
		log.Fatalf("解析失败: %v", err)
	}

	// 4. 验证 token 是否有效
	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		fmt.Println("用户名:", claims["username"])
		fmt.Println("角色:", claims["role"])
		fmt.Println("是否过期:", time.Now().Unix() > int64(claims["exp"].(float64)))
	} else {
		fmt.Println("token 无效")
	}
}
```

输出：

```go
[root@JiGeX jwt-demo]# go build . && ./jwt-demo 
用户名: alice
角色: admin
是否过期: false
```

### 在 HTTP 服务中使用 JWT（集成 Web）

```go
var secretKey = []byte("abcdefghijklmnopqrstuvwxyz123456") // 实际项目中应该使用 os.Getenv("JWT_SECRET")

// 1. 登录接口: 生成 token
func loginHandler(w http.ResponseWriter, r *http.Request) {
	username := r.URL.Query().Get("username")
	if username == "" {
		http.Error(w, "请提供 username", http.StatusBadRequest)
		return
	}

	// 生成 token
	claims := jwt.MapClaims{
		"username": username,
		"exp":      time.Now().Add(time.Hour * 1).Unix(), // 1 小时过期
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	signedToken, _ := token.SignedString(secretKey)

	w.Write([]byte("Token: " + signedToken))
}

// 2. JWT 验证中间件
func authMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 从 Header 获取 Token（格式："Bearer xxx"）
		authHeader := r.Header.Get("Authorization")
		if authHeader == "" {
			http.Error(w, "缺少 Authorization Header", http.StatusUnauthorized)
			return
		}

		// 提取 Token 字符串
		tokenString := strings.TrimPrefix(authHeader, "Bearer ")
		if tokenString == authHeader { // 没找到 "Bearer " 前缀
			http.Error(w, "Token 格式错误", http.StatusUnauthorized)
			return
		}

		// 验证 Token
		token, err := jwt.Parse(tokenString, func(token *jwt.Token) (any, error) {
			// 检查签名算法是否是 HMAC
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("签名算法错误")
			}
			return secretKey, nil
		})

		if err != nil || !token.Valid {
			http.Error(w, "无效 Token", http.StatusUnauthorized)
			return
		}

		// 将用户名存入请求上下文（后续 handler 可用）
		claims := token.Claims.(jwt.MapClaims)
		ctx := context.WithValue(r.Context(), "username", claims["username"])
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// 3. 受保护的接口
func protectedHandler(w http.ResponseWriter, r *http.Request) {
	username := r.Context().Value("username").(string)
	fmt.Fprintf(w, "欢迎回来, %s!", username)
}

func main() {
	http.HandleFunc("/login", loginHandler)
	http.Handle("/protected", authMiddleware(http.HandlerFunc(protectedHandler)))
	log.Fatal(http.ListenAndServe(":8080", nil))
}
```

验证：

```go
// 访问 /login 路由，但是没有提供 username
[root@JiGeX ~]# curl "http://localhost:8080/login"
请提供 username

// 带上 username，这次服务器就给本地签发了一个登录的 token
[root@JiGeX ~]# curl "http://localhost:8080/login?username=bob"
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTM1MDY0NzAsInVzZXJuYW1lIjoiYm9iIn0.KPqx5UkQ8BGneH4C-gS2ypJ2AdiAKMQAl_zgFOzdNL4

// 不带 token，直接访问 /protected，被拒绝
[root@JiGeX ~]# curl "http://localhost:8080/protected"
缺少 Authorization Header

// 带着 token，访问 /protected，成功登录上系统
[root@JiGeX ~]# curl "http://localhost:8080/protected" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTM1MDY0NzAsInVzZXJuYW1lIjoiYm9iIn0.KPqx5UkQ8BGneH4C-gS2ypJ2AdiAKMQAl_zgFOzdNL4"
欢迎回来, bob!
```

## 总结

JWT 就是一种 token 机制。主要分为三部分：

- `Header`
- `Payload`
- `Authorization`

这是 JWT 的结构，同时服务器中，还有保存一份 `secretKey`（对于同一个服务是唯一的，且需要绝对保密）。

用户想要一个 JWT 的时候，服务器将用户想要的 JWT 中保存的信息（用户名、角色之类的）加上服务器自己要加的信息（JWT 签发时间、过期时间）这些东西揉到一起，作为 `Payload` 部分。服务器再选定编码 JWT 的时候，使用啥样的编码算法（如 SHA256），然后将这部分作为 `Header` 部分。最后根据 `Payload`、`Header`、`secretKey` 这几部分内容，一起生成一个 `Authorization`。将 `Payload`、`Header`、`Authorization` 几部分内容组装到一起，就是一个 JWT 实体。

```bash
Header	-------
				\
Payload	---------- > 共同生成 Authorization	
				/
secretKey -----
```

之后生成的 JWT 形如：

```go
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTM1MDY0NzAsInVzZXJuYW1lIjoiYm9iIn0.KPqx5UkQ8BGneH4C-gS2ypJ2AdiAKMQAl_zgFOzdNL4
```

用 `.` 隔开的三部分，就分别是 JWT 的 `Header`、`Payload`、`Authorization`。

用户之后就直接使用生成 JWT 就行，服务器识别到这个 token 是正确的之后，就会根据 token 的 `payload` 中的信息（比如说用户名），创建出基于这个 `username` 的 `Context` 上下文（大概就是在一个上下文中带上 `username` 之类的环境变量）。之后用户就可以带着这个 `token` 在服务器中畅通无阻了。





