# fsnotify

## 介绍

这是一个用来做文件监控的库。使用这个库中的函数去对一些文件做 `watch` 操作，之后这些文件修改了或者是增加了、删除了，这个库都会提醒，文件发生的相应的变化。

有一个应用是用来监视配置文件的变化，以此实现配置文件的热更新。

## 安装

```go
go get github.com/fsnotify/fsnotify
```

## 监听单个目录的所有事件

```go
func main() {
	// 1. 创建 Watcher 实例
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		log.Fatal("创建 Watcher 失败:", err)
	}
	defer watcher.Close()

	// 2. 添加要监视的目录（当前目录）
	dir := "."
	err = watcher.Add(dir)
	if err != nil {
		log.Fatal("添加监视路径失败:", err)
	}

	log.Println("开始监视目录:", dir)
	fmt.Println("尝试创建/修改/删除文件测试...")

	// 3. 事件处理循环（核心：监听 Events 和 Errors 通道）
	for {
		select {
		// 处理文件事件
		case event, ok := <-watcher.Events:
			if !ok {
				return
			}
			log.Println(" EVENT:", event)
		// 处理错误
		case err, ok := <-watcher.Errors:
			if !ok {
				return
			}
			log.Println("Error:", err)
		}
	}
}
```

输出：

```go
2025/07/27 09:59:07  EVENT: CREATE        "./world"
2025/07/27 09:59:07  EVENT: CHMOD         "./world"
// ...
2025/07/27 09:59:42  EVENT: REMOVE        "./.world.swp"
2025/07/27 10:00:08  EVENT: WRITE         "./world"
2025/07/27 10:00:08  EVENT: WRITE         "./world"
```

> 其中可以发现一个问题，不管是使用 VScode 的 Ctrl + S 进行保存，还是使用 vim 保存，还是使用 cat >> EOF < file 的方式进行写文件，保存一次文件之后，`EVENT WRITE` 都会出现两次，而不是一次。
>
> 这是由于操作系统的文件保存的机制，可能是实际的写入是“创建新文件，再覆盖旧文件”，也可能是“将数据写完之后再 fsync 刷盘”，或者是从 O_TRUNC 之类的块中写入，等等这些，都可能会导致系统监视到多次的 Write 操作。
>
> 针对这种情况，做一些输出的去重或者防抖处理比消除这种情况更有意义。比如说，设定逻辑“对同一个文件 100ms 内的两次修改，视为一次修改”，通过这样的防抖来消除输出可能带来的误导。。

## 过滤事件——只处理特定操作

```go
func main() {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		log.Fatal("创建 wacher 失败:", err)
	}
	defer watcher.Close()

	// 监视当前目录
	dir := "."
	err = watcher.Add(dir)
	if err != nil {
		log.Fatal("添加路径失败:", err)
	}

	log.Println("仅监视 Create/Write 事件")

	done := make(chan bool)
	go func() {
		for {
			select {
			case event, ok := <-watcher.Events:
				if !ok {
					return
				}
				// 重点: 过滤事件类型
				if event.Op&fsnotify.Create == fsnotify.Create {
					log.Println("检测到新文件:", event.Name)
				}
				if event.Op&fsnotify.Write == fsnotify.Write {
					log.Println("检测到文件修改:", event.Name)
				}
				// 其他事件（Remove/Rename）被忽略
			case err, ok := <-watcher.Errors:
				if !ok {
					return
				}
				log.Println("错误:", err)
			}
		}
	}()

	// 保持程序运行（实际项目中可用信号量控制）
	log.Println("按 Enter 键退出...")
	_, _ = os.Stdin.Read(make([]byte, 1))
	close(done)
}
```

运行结果：

```go
2025/07/27 10:14:59 仅监视 Create/Write 事件
2025/07/27 10:14:59 按 Enter 键退出...
2025/07/27 10:15:35 检测到新文件: ./hello
2025/07/27 10:15:55 检测到文件修改: ./hello
2025/07/27 10:15:59 检测到新文件: ./hello2
```

## 递归监视——自动监视子目录

```go
func main() {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		log.Fatal("创建 watcher 失败:", err)
	}
	defer watcher.Close()

	// 要监视的根目录
	rootDir := "."

	// 1. 递归添加所有子目录
	addAllDirs(watcher, rootDir)

	log.Println("递归监视目录:", rootDir)
	log.Println("尝试在子目录操作文件...")

	// 2. 事件处理
	go func() {
		for event := range watcher.Events {
			// 如果是新建目录，自动添加监视
			if event.Op&fsnotify.Create == fsnotify.Create {
				if isDir(event.Name) {
					log.Println("新建目录，自动加入监视:", event.Name)
					addAllDirs(watcher, event.Name) // 递归添加
				}
			}
			// 打印文件事件（可扩展过滤逻辑）
			log.Println("文件事件:", event)
		}
		log.Println("事件处理 go routine 结束")
	}()

	// 错误处理（独立 goroutine）
	go func() {
		for err := range watcher.Errors {
			log.Println("错误:", err)
		}
		log.Println("错误处理 go routine 结束")
	}()

	// 保持运行
	<-make(chan struct{}) // 永久阻塞
}

// 递归添加目录及其子目录到监视
func addAllDirs(watcher *fsnotify.Watcher, dir string) {
	filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() {
			err = watcher.Add(path)
			if err != nil {
				log.Printf("添加目录 %q 失败: %v", path, err)
			}
		}
		return nil
	})
}

// 判断路径是否为目录
func isDir(path string) bool {
	info, err := os.Stat(path)
	return err == nil && info.IsDir()
}
```

运行结果：

```go
[root@JiGeX fsnotify-demo]# go build . && ./fsnotify-demo 
2025/07/27 10:29:27 递归监视目录: .
2025/07/27 10:29:27 尝试在子目录操作文件...
2025/07/27 10:29:38 文件事件: REMOVE        "./hello"
2025/07/27 10:29:38 文件事件: REMOVE        "./hello2"
2025/07/27 10:29:44 新建目录，自动加入监视: ./dir2
2025/07/27 10:29:44 文件事件: CREATE        "./dir2"
2025/07/27 10:29:57 文件事件: CREATE        "dir2/hello2"
2025/07/27 10:29:57 文件事件: CHMOD         "dir2/hello2"
2025/07/27 10:30:07 文件事件: WRITE         "dir2/hello2"
```







