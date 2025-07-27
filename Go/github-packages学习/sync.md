# sync

## 介绍

这里说的是 `golang.org/x/sync`。这是 golang 官方提供的扩展同步库，是标准的 `sync` 库的补充，提供了一些原本 `sync` 库中没有的东西，或者是做了增强。

## 安装

```go
go get golang.org/x/sync
```

## `errgroup`

`errgroup`：带错误处理的并发任务管理。

使用场景：同时开启多个 goroutine，其中任意失败，其他的也都取消。

```go
func main() {
	// 创建带超时的 Context（10 秒后自动取消）
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	g, ctx := errgroup.WithContext(ctx) // 关键：绑定 Context 实现级联取消

	// 模拟 3 个并发任务
	for i := 1; i <= 3; i++ {
		taskID := i
		g.Go(func() error {
			select {
			case <-ctx.Done(): // 监听取消信号
				fmt.Printf("task %d cancelled\n", taskID)
				return ctx.Err()
			case <-time.After(time.Duration(taskID) * time.Second):
				if taskID == 2 {
					// 模拟第二个任务失败
					fmt.Printf("task %d failed\n", taskID)
					return fmt.Errorf("task %d failed", taskID)
				}
				fmt.Printf("Task %d completed\n", taskID)
				return nil
			}
		})
	}

	// 等待所有任务完成或发生错误
	if err := g.Wait(); err != nil {
		fmt.Println("Error:", err) // 会收到 task2 的错误
	}
}
```

运行结果：

```go
[root@JiGeX sync-demo]# go build . && ./sync-demo 
Task 1 completed
task 2 failed
task 3 cancelled
Error: task 2 failed
```

## `singleflight`

`signleflight`：防止缓存击穿、重复请求。

使用场景：比如说服务器中有多个查询数据库的请求，有一些请求的参数是一样的，那么这些请求的查询一共只需要执行一次即可。

```go
var sf singleflight.Group

func fetchDataFromDB(key string) (string, error) {
	fmt.Printf("Query DB for %s...\n", key)
	time.Sleep(2 * time.Second) // 模拟慢查询
	return fmt.Sprintf("data_%s", key), nil
}

func main() {
	// 模拟 5 个并发请求
	for i := 0; i < 5; i++ {
		go func(id int) {
			// 相同 key 的请求会被吞并
			data, err, _ := sf.Do("user100", func() (any, error) {
				return fetchDataFromDB("user100")
			})
			fmt.Printf("Request %d: %v, %v\n", id, data, err)
		}(i)
	}

	time.Sleep(3 * time.Second) // 等待所有请求完成
}
```

执行结果：

```go
[root@JiGeX sync-demo]# go build . && ./sync-demo 
Query DB for user100...
Request 4: data_user100, <nil>
Request 3: data_user100, <nil>
Request 0: data_user100, <nil>
Request 1: data_user100, <nil>
Request 2: data_user100, <nil>
```

> 先建立一个变量 `var sf singleflight.Group`，之后要执行函数的时候，不要直接执行，而是从 `sf.Do(key, func)` 中去执行函数。
>
> 相同 `key` 的多个请求，实际上只会执行一次 `func()`，并且执行的结果是共享的。这是设计模式中的 `shared` 模式。

## `semaphore`

`semaphore`：精准控制并发数。

使用场景：比如说做爬虫或者什么事情的时候，想把实际运行的 goroutine 控制在一个范围内。

```go
func main() {
	// 创建信号量：最大允许 3 个并发
	s := semaphore.NewWeighted(3)
	var wg sync.WaitGroup

	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func(taskID int) {
			defer wg.Done()

			// 获取信号量（阻塞直到有可用资源）
			if err := s.Acquire(context.Background(), 1); err != nil {
				fmt.Printf("Task %d failed: %v\n", taskID, err)
				return
			}
			defer s.Release(1) // 任务完成后释放

			fmt.Printf("Task %d running (max 3 concurrent)\n", taskID)
			time.Sleep(1 * time.Second) // 模拟任务执行
		}(i)
	}

	wg.Wait()
}
```

执行结果：

```go
[root@JiGeX sync-demo]# go build . && ./sync-demo 
// 刚开始执行，就会立马输出这三行
Task 4 running (max 3 concurrent)
Task 0 running (max 3 concurrent)
Task 1 running (max 3 concurrent)
// 执行 1 秒之后，输出这两行
Task 2 running (max 3 concurrent)
Task 3 running (max 3 concurrent)
```

> 其实之前用 channel 也能实现，不过这种方式更简洁、更优雅。

## 总结

`golang.org/x/sync` 中最常用的三个部分：

- `errgroup`：起多个 goroutine，需要其中一个 goroutine 出错之后，其他都自动终止。
- `singleflight`：有多个参数相同的查询请求，后端只需要执行一次查询，查询的结果所有请求共享。
- `semaphore`：控制 goroutine 并发量的数量，相比使用 channel 更优雅。

此外这个包还提供了一个增强版的线程安全的 map：`sync.Map`。这个库标准版的 `sync` 中已经实现：`sync.Map`。这个库中的 `Map` 就是提供了一些增强的功能。









