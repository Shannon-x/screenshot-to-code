# Redis 部署和配置指南

本指南详细说明如何在 Screenshot to Code 项目中配置和使用 Redis 缓存系统。

## 目录

- [为什么使用 Redis](#为什么使用-redis)
- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [Redis 命令详解](#redis-命令详解)
- [性能优化](#性能优化)
- [监控和维护](#监控和维护)
- [故障排除](#故障排除)

## 为什么使用 Redis

在 Screenshot to Code 项目中使用 Redis 可以带来以下好处：

1. **减少 API 调用成本** - 缓存相同截图的生成结果，避免重复调用昂贵的 AI API
2. **提升响应速度** - 缓存命中时可以立即返回结果，无需等待 AI 处理
3. **提高系统稳定性** - 在 API 限流或故障时，可以使用缓存的结果
4. **支持分布式部署** - 多个后端实例可以共享同一个 Redis 缓存

## 快速开始

### 使用 Docker Compose（推荐）

项目的 `docker-compose.yml` 已经包含了 Redis 服务配置：

```yaml
services:
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    expose:
      - "6379"
    volumes:
      - redis-data:/data
    networks:
      - app-network
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru

  backend:
    # ... 其他配置
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
```

启动服务：
```bash
docker-compose up -d
```

### 独立部署 Redis

如果您想独立部署 Redis：

1. **使用 Docker 运行 Redis**
   ```bash
   docker run -d \
     --name screenshot-redis \
     -p 6379:6379 \
     -v redis-data:/data \
     redis:7-alpine \
     redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
   ```

2. **在系统上安装 Redis**
   
   Ubuntu/Debian:
   ```bash
   sudo apt update
   sudo apt install redis-server
   sudo systemctl enable redis-server
   sudo systemctl start redis-server
   ```
   
   macOS:
   ```bash
   brew install redis
   brew services start redis
   ```

3. **配置后端连接**
   
   在 `.env` 文件中设置：
   ```env
   REDIS_URL=redis://localhost:6379
   # 如果有密码
   REDIS_URL=redis://:password@localhost:6379
   ```

## 详细配置

### Redis 配置参数说明

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `appendonly` | 启用持久化，防止重启后数据丢失 | `yes` |
| `maxmemory` | 最大内存使用量 | `256mb` |
| `maxmemory-policy` | 内存满时的淘汰策略 | `allkeys-lru` |
| `save` | RDB 快照策略 | `900 1 300 10 60 10000` |
| `tcp-keepalive` | TCP 连接保活时间 | `300` |

### 环境变量配置

完整的 Redis 相关环境变量：

```env
# Redis 连接 URL
REDIS_URL=redis://redis:6379

# Redis 配置（可选）
REDIS_MAX_CONNECTIONS=50          # 最大连接数
REDIS_SOCKET_TIMEOUT=5            # 连接超时（秒）
REDIS_SOCKET_CONNECT_TIMEOUT=5    # 连接建立超时（秒）
REDIS_RETRY_ON_TIMEOUT=true       # 超时后是否重试
REDIS_HEALTH_CHECK_INTERVAL=30    # 健康检查间隔（秒）

# 缓存配置
CACHE_TTL=3600                    # 默认缓存时间（秒）
CACHE_SCREENSHOT_TTL=86400        # 截图分析缓存时间（秒）
CACHE_CODE_GENERATION_TTL=7200    # 代码生成缓存时间（秒）
CACHE_COMPRESSION=true            # 是否启用压缩
```

### 自定义 Redis 配置文件

创建 `redis.conf`：

```conf
# 基础配置
bind 0.0.0.0
port 6379
daemonize no
pidfile /var/run/redis/redis-server.pid
loglevel notice
logfile /var/log/redis/redis-server.log

# 持久化配置
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no

# 内存管理
maxmemory 256mb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# 性能优化
tcp-backlog 511
tcp-keepalive 300
timeout 0
databases 16

# 安全配置（生产环境建议启用）
# requirepass your_strong_password
# rename-command FLUSHDB ""
# rename-command FLUSHALL ""
# rename-command CONFIG ""
```

使用自定义配置文件：
```bash
docker run -d \
  --name screenshot-redis \
  -p 6379:6379 \
  -v $(pwd)/redis.conf:/usr/local/etc/redis/redis.conf \
  -v redis-data:/data \
  redis:7-alpine \
  redis-server /usr/local/etc/redis/redis.conf
```

## Redis 命令详解

### 缓存键规则

项目中使用的缓存键格式：

- **代码生成缓存**: `generation:{prompt_hash}:{model}`
- **截图分析缓存**: `screenshot:{image_hash}`
- **模型标签**: `tag:model:{model_name}`
- **统计信息**: `stats:{metric_name}`

### 常用命令

1. **查看所有键**
   ```bash
   redis-cli KEYS "*"
   ```

2. **查看特定模型的缓存**
   ```bash
   redis-cli KEYS "generation:*:gpt-4o"
   ```

3. **查看键的TTL**
   ```bash
   redis-cli TTL "generation:abc123:gpt-4o"
   ```

4. **手动删除缓存**
   ```bash
   # 删除单个键
   redis-cli DEL "generation:abc123:gpt-4o"
   
   # 删除所有生成缓存
   redis-cli --scan --pattern "generation:*" | xargs redis-cli DEL
   ```

5. **查看内存使用**
   ```bash
   redis-cli INFO memory
   ```

## 性能优化

### 1. 内存优化

监控内存使用：
```bash
redis-cli
> INFO memory
> MEMORY STATS
> MEMORY DOCTOR
```

优化建议：
- 设置合理的 `maxmemory` 限制
- 使用 `allkeys-lru` 淘汰策略
- 启用键过期自动删除：`CONFIG SET lazyfree-lazy-eviction yes`

### 2. 连接池优化

在代码中配置连接池：
```python
# backend/cache/redis_cache.py
self.pool = redis.ConnectionPool(
    host=redis_host,
    port=redis_port,
    db=0,
    max_connections=50,
    socket_timeout=5,
    socket_connect_timeout=5,
    socket_keepalive=True,
    socket_keepalive_options={
        1: 10,  # TCP_KEEPIDLE
        2: 3,   # TCP_KEEPINTVL
        3: 5,   # TCP_KEEPCNT
    }
)
```

### 3. 压缩优化

项目默认启用 zlib 压缩，可以显著减少内存使用：

```python
# 压缩等级配置（1-9，默认6）
COMPRESSION_LEVEL = 6

# 只压缩大于阈值的数据
COMPRESSION_THRESHOLD = 1024  # 1KB
```

## 监控和维护

### 使用 Redis 监控工具

1. **redis-cli 监控**
   ```bash
   # 实时监控命令
   redis-cli MONITOR
   
   # 查看慢查询日志
   redis-cli SLOWLOG GET 10
   
   # 查看客户端连接
   redis-cli CLIENT LIST
   ```

2. **使用 RedisInsight（推荐）**
   ```bash
   docker run -d \
     --name redisinsight \
     -p 8001:8001 \
     redis/redisinsight:latest
   ```
   访问 http://localhost:8001

3. **配置告警**
   
   监控关键指标：
   - 内存使用率 > 80%
   - 连接数 > 100
   - 命令执行时间 > 100ms
   - 键驱逐率异常增高

### 定期维护任务

1. **清理过期数据**
   ```bash
   # 强制删除过期键
   redis-cli --scan --pattern "*" | while read key; do
     ttl=$(redis-cli TTL "$key")
     if [ "$ttl" -eq -2 ]; then
       redis-cli DEL "$key"
     fi
   done
   ```

2. **备份数据**
   ```bash
   # 创建 RDB 快照
   redis-cli BGSAVE
   
   # 备份 AOF 文件
   docker exec screenshot-redis cp /data/appendonly.aof /data/backup-$(date +%Y%m%d).aof
   ```

3. **性能分析**
   ```bash
   # 分析大键
   redis-cli --bigkeys
   
   # 分析内存使用
   redis-cli --memkeys
   ```

## 故障排除

### 常见问题

1. **连接失败**
   ```
   Error: Redis connection failed: Connection refused
   ```
   解决方案：
   - 检查 Redis 服务是否运行：`docker ps | grep redis`
   - 检查网络连接：`telnet localhost 6379`
   - 检查防火墙设置

2. **内存不足**
   ```
   Error: OOM command not allowed when used memory > 'maxmemory'
   ```
   解决方案：
   - 增加 maxmemory：`CONFIG SET maxmemory 512mb`
   - 清理不必要的数据：`FLUSHDB`
   - 检查是否有内存泄漏

3. **性能下降**
   - 检查慢查询：`SLOWLOG GET 100`
   - 优化大键：使用 `--bigkeys` 找出并优化
   - 检查网络延迟：`redis-cli --latency`

### 调试命令

```bash
# 检查 Redis 状态
redis-cli ping

# 查看服务器信息
redis-cli INFO server

# 检查复制状态
redis-cli INFO replication

# 查看持久化状态
redis-cli INFO persistence

# 监控实时命令
redis-cli MONITOR

# 查看配置
redis-cli CONFIG GET "*"
```

### 日志分析

查看 Redis 日志：
```bash
# Docker 容器日志
docker logs screenshot-redis --tail 100 -f

# 系统服务日志
journalctl -u redis-server -f
```

## 生产环境建议

1. **启用密码认证**
   ```bash
   redis-cli CONFIG SET requirepass "your_strong_password"
   ```

2. **限制危险命令**
   ```conf
   rename-command FLUSHDB ""
   rename-command FLUSHALL ""
   rename-command KEYS ""
   rename-command CONFIG ""
   ```

3. **配置持久化**
   ```conf
   save 900 1
   save 300 10
   save 60 10000
   appendonly yes
   ```

4. **监控和告警**
   - 使用 Prometheus + Grafana
   - 配置 Redis Exporter
   - 设置关键指标告警

5. **高可用配置**
   - 使用 Redis Sentinel
   - 或配置 Redis Cluster
   - 定期备份数据

---

通过正确配置和使用 Redis，Screenshot to Code 项目可以显著提升性能、降低成本，并提供更好的用户体验。