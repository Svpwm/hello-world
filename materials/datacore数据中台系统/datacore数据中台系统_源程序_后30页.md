# datacore数据中台系统 V1.0 源程序代码

## 第31页

```python
# -*- coding: utf-8 -*-
"""
datacore数据中台系统 - 数据质量管理模块
Copyright (c) 2024 北京灵犀科技有限公司
文件: quality/rule_engine.py
"""

import re
import json
import hashlib
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime, date
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """规则类型枚举"""
    COMPLETENESS = "completeness"      # 完整性
    ACCURACY = "accuracy"              # 准确性
    CONSISTENCY = "consistency"        # 一致性
    TIMELINESS = "timeliness"          # 时效性
    UNIQUENESS = "uniqueness"          # 唯一性
    VALIDITY = "validity"              # 有效性
    CUSTOM = "custom"                  # 自定义


class Severity(Enum):
    """严重级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class RuleResult:
    """规则执行结果"""
    rule_id: str
    rule_name: str
    passed: bool
    severity: Severity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    affected_records: int = 0
    total_records: int = 0
    execution_time_ms: float = 0.0
```

---

## 第32页

```python
    @property
    def pass_rate(self) -> float:
        """计算通过率"""
        if self.total_records == 0:
            return 1.0
        return (self.total_records - self.affected_records) / self.total_records

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "passed": self.passed,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "affected_records": self.affected_records,
            "total_records": self.total_records,
            "pass_rate": self.pass_rate,
            "execution_time_ms": self.execution_time_ms
        }


class QualityRule(ABC):
    """质量规则基类"""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str = "",
        severity: Severity = Severity.WARNING,
        enabled: bool = True,
        config: Optional[Dict[str, Any]] = None
    ):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.severity = severity
        self.enabled = enabled
        self.config = config or {}
        self._compiled = False
    
    @abstractmethod
    def validate(self, data: Any, context: Optional[Dict] = None) -> RuleResult:
        """执行验证"""
        pass
    
    def compile(self) -> None:
        """编译规则（可选实现）"""
        self._compiled = True
    
    def get_rule_type(self) -> RuleType:
        """获取规则类型"""
        return RuleType.CUSTOM
```

---

## 第33页

```python
class CompletenessRule(QualityRule):
    """完整性规则 - 检查必填字段"""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        required_fields: List[str],
        allow_empty: bool = False,
        **kwargs
    ):
        super().__init__(rule_id, name, **kwargs)
        self.required_fields = required_fields
        self.allow_empty = allow_empty
    
    def get_rule_type(self) -> RuleType:
        return RuleType.COMPLETENESS
    
    def validate(self, data: Any, context: Optional[Dict] = None) -> RuleResult:
        start_time = datetime.now()
        missing_fields = []
        empty_fields = []
        
        if isinstance(data, dict):
            records = [data]
        elif isinstance(data, list):
            records = data
        else:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.name,
                passed=False,
                severity=self.severity,
                message="Invalid data type, expected dict or list",
                total_records=0,
                affected_records=0
            )
        
        total = len(records)
        affected = 0
        
        for idx, record in enumerate(records):
            record_issues = []
            for field in self.required_fields:
                value = self._get_nested_value(record, field)
                
                if value is None:
                    record_issues.append(f"Missing field: {field}")
                elif not self.allow_empty and self._is_empty(value):
                    record_issues.append(f"Empty field: {field}")
            
            if record_issues:
                affected += 1
                if len(missing_fields) < 10:
                    missing_fields.append({"index": idx, "issues": record_issues})
```

---

## 第34页

```python
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        passed = affected == 0
        
        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"Completeness check: {total - affected}/{total} records passed",
            details={"sample_issues": missing_fields},
            affected_records=affected,
            total_records=total,
            execution_time_ms=execution_time
        )
    
    def _get_nested_value(self, data: Dict, field_path: str) -> Any:
        """获取嵌套字段值"""
        keys = field_path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    def _is_empty(self, value: Any) -> bool:
        """检查值是否为空"""
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        if isinstance(value, (list, dict)) and len(value) == 0:
            return True
        return False


class UniquenessRule(QualityRule):
    """唯一性规则 - 检查字段值唯一性"""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        unique_fields: List[str],
        case_sensitive: bool = True,
        **kwargs
    ):
        super().__init__(rule_id, name, **kwargs)
        self.unique_fields = unique_fields
        self.case_sensitive = case_sensitive
```

---

## 第35页

```python
    def get_rule_type(self) -> RuleType:
        return RuleType.UNIQUENESS
    
    def validate(self, data: Any, context: Optional[Dict] = None) -> RuleResult:
        start_time = datetime.now()
        
        if not isinstance(data, list):
            data = [data]
        
        total = len(data)
        seen_values = {}
        duplicates = []
        
        for idx, record in enumerate(data):
            key_parts = []
            for field in self.unique_fields:
                value = self._extract_field(record, field)
                if not self.case_sensitive and isinstance(value, str):
                    value = value.lower()
                key_parts.append(str(value))
            
            composite_key = "|".join(key_parts)
            
            if composite_key in seen_values:
                duplicates.append({
                    "index": idx,
                    "duplicate_of": seen_values[composite_key],
                    "key": composite_key
                })
            else:
                seen_values[composite_key] = idx
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        affected = len(duplicates)
        passed = affected == 0
        
        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"Uniqueness check: {affected} duplicates found in {total} records",
            details={"duplicates": duplicates[:20]},
            affected_records=affected,
            total_records=total,
            execution_time_ms=execution_time
        )
    
    def _extract_field(self, record: Dict, field: str) -> Any:
        """提取字段值"""
        parts = field.split(".")
        value = record
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        return value
```

---

## 第36页

```python
class FormatRule(QualityRule):
    """格式验证规则 - 使用正则表达式验证"""
    
    BUILTIN_PATTERNS = {
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "phone": r"^1[3-9]\d{9}$",
        "id_card": r"^\d{17}[\dXx]$",
        "url": r"^https?://[^\s/$.?#].[^\s]*$",
        "ip_v4": r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$",
        "date_iso": r"^\d{4}-\d{2}-\d{2}$",
        "datetime_iso": r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}",
        "uuid": r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    }
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        field: str,
        pattern: str,
        use_builtin: bool = False,
        **kwargs
    ):
        super().__init__(rule_id, name, **kwargs)
        self.field = field
        self.use_builtin = use_builtin
        
        if use_builtin and pattern in self.BUILTIN_PATTERNS:
            self.pattern = self.BUILTIN_PATTERNS[pattern]
        else:
            self.pattern = pattern
        
        self._regex = None
    
    def compile(self) -> None:
        """预编译正则表达式"""
        self._regex = re.compile(self.pattern)
        self._compiled = True
    
    def get_rule_type(self) -> RuleType:
        return RuleType.VALIDITY
    
    def validate(self, data: Any, context: Optional[Dict] = None) -> RuleResult:
        start_time = datetime.now()
        
        if not self._compiled:
            self.compile()
        
        if not isinstance(data, list):
            data = [data]
```

---

## 第37页

```python
        total = len(data)
        invalid_records = []
        
        for idx, record in enumerate(data):
            value = self._get_field_value(record, self.field)
            
            if value is None:
                continue
            
            if not isinstance(value, str):
                value = str(value)
            
            if not self._regex.match(value):
                invalid_records.append({
                    "index": idx,
                    "field": self.field,
                    "value": value[:100],
                    "pattern": self.pattern
                })
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        affected = len(invalid_records)
        passed = affected == 0
        
        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"Format validation: {affected} invalid values in field '{self.field}'",
            details={"invalid_samples": invalid_records[:10]},
            affected_records=affected,
            total_records=total,
            execution_time_ms=execution_time
        )
    
    def _get_field_value(self, record: Dict, field: str) -> Any:
        """获取字段值"""
        parts = field.split(".")
        value = record
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        return value


class RangeRule(QualityRule):
    """范围验证规则 - 检查数值或日期范围"""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        field: str,
        min_value: Optional[Union[int, float, str]] = None,
        max_value: Optional[Union[int, float, str]] = None,
        inclusive: bool = True,
        **kwargs
    ):
        super().__init__(rule_id, name, **kwargs)
        self.field = field
        self.min_value = min_value
        self.max_value = max_value
        self.inclusive = inclusive
```

---

## 第38页

```python
    def get_rule_type(self) -> RuleType:
        return RuleType.ACCURACY
    
    def validate(self, data: Any, context: Optional[Dict] = None) -> RuleResult:
        start_time = datetime.now()
        
        if not isinstance(data, list):
            data = [data]
        
        total = len(data)
        out_of_range = []
        
        for idx, record in enumerate(data):
            value = self._get_nested_field(record, self.field)
            
            if value is None:
                continue
            
            value = self._convert_value(value)
            min_val = self._convert_value(self.min_value) if self.min_value else None
            max_val = self._convert_value(self.max_value) if self.max_value else None
            
            is_valid = True
            
            if min_val is not None:
                if self.inclusive:
                    is_valid = is_valid and value >= min_val
                else:
                    is_valid = is_valid and value > min_val
            
            if max_val is not None:
                if self.inclusive:
                    is_valid = is_valid and value <= max_val
                else:
                    is_valid = is_valid and value < max_val
            
            if not is_valid:
                out_of_range.append({
                    "index": idx,
                    "field": self.field,
                    "value": str(value),
                    "min": str(self.min_value),
                    "max": str(self.max_value)
                })
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        affected = len(out_of_range)
        passed = affected == 0
        
        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"Range check: {affected} values out of range for '{self.field}'",
            details={"out_of_range_samples": out_of_range[:10]},
            affected_records=affected,
            total_records=total,
            execution_time_ms=execution_time
        )
```

---

## 第39页

```python
    def _get_nested_field(self, record: Dict, field: str) -> Any:
        """获取嵌套字段"""
        parts = field.split(".")
        value = record
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        return value
    
    def _convert_value(self, value: Any) -> Any:
        """转换值为可比较类型"""
        if value is None:
            return None
        if isinstance(value, (int, float, Decimal)):
            return float(value)
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    return value
        if isinstance(value, (datetime, date)):
            return value
        return value


class RuleEngine:
    """规则引擎 - 管理和执行质量规则"""
    
    def __init__(self):
        self.rules: Dict[str, QualityRule] = {}
        self.rule_groups: Dict[str, List[str]] = {}
        self._execution_history: List[Dict] = []
    
    def register_rule(self, rule: QualityRule, groups: Optional[List[str]] = None) -> None:
        """注册规则"""
        self.rules[rule.rule_id] = rule
        
        if groups:
            for group in groups:
                if group not in self.rule_groups:
                    self.rule_groups[group] = []
                self.rule_groups[group].append(rule.rule_id)
        
        logger.info(f"Registered rule: {rule.rule_id} ({rule.name})")
    
    def unregister_rule(self, rule_id: str) -> bool:
        """注销规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            for group_rules in self.rule_groups.values():
                if rule_id in group_rules:
                    group_rules.remove(rule_id)
            return True
        return False
```

---

## 第40页

```python
    def execute_rule(
        self,
        rule_id: str,
        data: Any,
        context: Optional[Dict] = None
    ) -> Optional[RuleResult]:
        """执行单个规则"""
        rule = self.rules.get(rule_id)
        if not rule:
            logger.warning(f"Rule not found: {rule_id}")
            return None
        
        if not rule.enabled:
            logger.debug(f"Rule disabled: {rule_id}")
            return None
        
        try:
            result = rule.validate(data, context)
            self._record_execution(rule_id, result)
            return result
        except Exception as e:
            logger.error(f"Rule execution failed: {rule_id}, error: {str(e)}")
            return RuleResult(
                rule_id=rule_id,
                rule_name=rule.name,
                passed=False,
                severity=Severity.ERROR,
                message=f"Rule execution error: {str(e)}",
                details={"exception": str(e)}
            )
    
    def execute_all(
        self,
        data: Any,
        context: Optional[Dict] = None,
        stop_on_failure: bool = False
    ) -> List[RuleResult]:
        """执行所有启用的规则"""
        results = []
        
        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            result = self.execute_rule(rule_id, data, context)
            if result:
                results.append(result)
                
                if stop_on_failure and not result.passed:
                    logger.info(f"Stopping execution due to rule failure: {rule_id}")
                    break
        
        return results
    
    def execute_group(
        self,
        group: str,
        data: Any,
        context: Optional[Dict] = None
    ) -> List[RuleResult]:
        """执行规则组"""
        results = []
        rule_ids = self.rule_groups.get(group, [])
        
        for rule_id in rule_ids:
            result = self.execute_rule(rule_id, data, context)
            if result:
                results.append(result)
        
        return results
```

---

## 第41页

```python
    def _record_execution(self, rule_id: str, result: RuleResult) -> None:
        """记录执行历史"""
        self._execution_history.append({
            "rule_id": rule_id,
            "timestamp": datetime.now().isoformat(),
            "passed": result.passed,
            "execution_time_ms": result.execution_time_ms
        })
        
        if len(self._execution_history) > 10000:
            self._execution_history = self._execution_history[-5000:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取执行统计"""
        if not self._execution_history:
            return {"total_executions": 0}
        
        total = len(self._execution_history)
        passed = sum(1 for e in self._execution_history if e["passed"])
        avg_time = sum(e["execution_time_ms"] for e in self._execution_history) / total
        
        rule_stats = {}
        for execution in self._execution_history:
            rule_id = execution["rule_id"]
            if rule_id not in rule_stats:
                rule_stats[rule_id] = {"executions": 0, "failures": 0}
            rule_stats[rule_id]["executions"] += 1
            if not execution["passed"]:
                rule_stats[rule_id]["failures"] += 1
        
        return {
            "total_executions": total,
            "passed_executions": passed,
            "failed_executions": total - passed,
            "pass_rate": passed / total,
            "average_execution_time_ms": avg_time,
            "rule_statistics": rule_stats
        }


# -*- coding: utf-8 -*-
"""
datacore数据中台系统 - 数据血缘追踪模块
Copyright (c) 2024 北京灵犀科技有限公司
文件: lineage/tracker.py
"""

from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import json
import networkx as nx


class LineageNodeType(Enum):
    """血缘节点类型"""
    DATABASE = "database"
    SCHEMA = "schema"
    TABLE = "table"
    COLUMN = "column"
    FILE = "file"
    API = "api"
    JOB = "job"
    TRANSFORMATION = "transformation"
```

---

## 第42页

```python
class LineageEdgeType(Enum):
    """血缘边类型"""
    CONTAINS = "contains"
    DERIVES_FROM = "derives_from"
    TRANSFORMS_TO = "transforms_to"
    READS_FROM = "reads_from"
    WRITES_TO = "writes_to"
    JOINS_WITH = "joins_with"


@dataclass
class LineageNode:
    """血缘节点"""
    node_id: str
    node_type: LineageNodeType
    name: str
    qualified_name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "name": self.name,
            "qualified_name": self.qualified_name,
            "properties": self.properties,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class LineageEdge:
    """血缘边"""
    edge_id: str
    source_id: str
    target_id: str
    edge_type: LineageEdgeType
    properties: Dict[str, Any] = field(default_factory=dict)
    transformation: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type.value,
            "properties": self.properties,
            "transformation": self.transformation,
            "created_at": self.created_at.isoformat()
        }
```

---

## 第43页

```python
class LineageGraph:
    """数据血缘图"""
    
    def __init__(self):
        self._graph = nx.DiGraph()
        self._nodes: Dict[str, LineageNode] = {}
        self._edges: Dict[str, LineageEdge] = {}
        self._qualified_name_index: Dict[str, str] = {}
    
    def add_node(self, node: LineageNode) -> str:
        """添加节点"""
        self._nodes[node.node_id] = node
        self._qualified_name_index[node.qualified_name] = node.node_id
        self._graph.add_node(
            node.node_id,
            node_type=node.node_type.value,
            name=node.name,
            qualified_name=node.qualified_name
        )
        return node.node_id
    
    def add_edge(self, edge: LineageEdge) -> str:
        """添加边"""
        if edge.source_id not in self._nodes:
            raise ValueError(f"Source node not found: {edge.source_id}")
        if edge.target_id not in self._nodes:
            raise ValueError(f"Target node not found: {edge.target_id}")
        
        self._edges[edge.edge_id] = edge
        self._graph.add_edge(
            edge.source_id,
            edge.target_id,
            edge_id=edge.edge_id,
            edge_type=edge.edge_type.value
        )
        return edge.edge_id
    
    def get_node(self, node_id: str) -> Optional[LineageNode]:
        """获取节点"""
        return self._nodes.get(node_id)
    
    def get_node_by_qualified_name(self, qualified_name: str) -> Optional[LineageNode]:
        """通过限定名获取节点"""
        node_id = self._qualified_name_index.get(qualified_name)
        if node_id:
            return self._nodes.get(node_id)
        return None
    
    def get_edge(self, edge_id: str) -> Optional[LineageEdge]:
        """获取边"""
        return self._edges.get(edge_id)
    
    def remove_node(self, node_id: str) -> bool:
        """删除节点"""
        if node_id not in self._nodes:
            return False
        
        node = self._nodes[node_id]
        del self._qualified_name_index[node.qualified_name]
        del self._nodes[node_id]
        self._graph.remove_node(node_id)
        
        edges_to_remove = [
            e_id for e_id, e in self._edges.items()
            if e.source_id == node_id or e.target_id == node_id
        ]
        for e_id in edges_to_remove:
            del self._edges[e_id]
        
        return True
```

---

## 第44页

```python
    def get_upstream(
        self,
        node_id: str,
        depth: int = -1,
        edge_types: Optional[List[LineageEdgeType]] = None
    ) -> List[LineageNode]:
        """获取上游节点"""
        if node_id not in self._nodes:
            return []
        
        visited = set()
        result = []
        
        def traverse(current_id: str, current_depth: int):
            if current_id in visited:
                return
            if depth != -1 and current_depth > depth:
                return
            
            visited.add(current_id)
            
            for predecessor in self._graph.predecessors(current_id):
                edge_data = self._graph.get_edge_data(predecessor, current_id)
                
                if edge_types:
                    edge_type = LineageEdgeType(edge_data.get("edge_type"))
                    if edge_type not in edge_types:
                        continue
                
                if predecessor not in visited:
                    result.append(self._nodes[predecessor])
                    traverse(predecessor, current_depth + 1)
        
        traverse(node_id, 0)
        return result
    
    def get_downstream(
        self,
        node_id: str,
        depth: int = -1,
        edge_types: Optional[List[LineageEdgeType]] = None
    ) -> List[LineageNode]:
        """获取下游节点"""
        if node_id not in self._nodes:
            return []
        
        visited = set()
        result = []
        
        def traverse(current_id: str, current_depth: int):
            if current_id in visited:
                return
            if depth != -1 and current_depth > depth:
                return
            
            visited.add(current_id)
            
            for successor in self._graph.successors(current_id):
                edge_data = self._graph.get_edge_data(current_id, successor)
                
                if edge_types:
                    edge_type = LineageEdgeType(edge_data.get("edge_type"))
                    if edge_type not in edge_types:
                        continue
                
                if successor not in visited:
                    result.append(self._nodes[successor])
                    traverse(successor, current_depth + 1)
        
        traverse(node_id, 0)
        return result
```

---

## 第45页

```python
    def get_lineage_path(
        self,
        source_id: str,
        target_id: str
    ) -> List[List[str]]:
        """获取两个节点间的血缘路径"""
        if source_id not in self._nodes or target_id not in self._nodes:
            return []
        
        try:
            paths = list(nx.all_simple_paths(
                self._graph, source_id, target_id, cutoff=10
            ))
            return paths
        except nx.NetworkXNoPath:
            return []
    
    def get_impact_analysis(
        self,
        node_id: str,
        include_indirect: bool = True
    ) -> Dict[str, Any]:
        """影响分析"""
        downstream = self.get_downstream(node_id, depth=-1 if include_indirect else 1)
        
        impact_by_type = {}
        for node in downstream:
            node_type = node.node_type.value
            if node_type not in impact_by_type:
                impact_by_type[node_type] = []
            impact_by_type[node_type].append(node.qualified_name)
        
        return {
            "source_node": node_id,
            "total_impacted": len(downstream),
            "impact_by_type": impact_by_type,
            "impacted_nodes": [n.to_dict() for n in downstream]
        }
    
    def export_to_json(self) -> str:
        """导出为JSON"""
        return json.dumps({
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": [e.to_dict() for e in self._edges.values()]
        }, ensure_ascii=False, indent=2)
    
    @classmethod
    def import_from_json(cls, json_str: str) -> "LineageGraph":
        """从JSON导入"""
        data = json.loads(json_str)
        graph = cls()
        
        for node_data in data.get("nodes", []):
            node = LineageNode(
                node_id=node_data["node_id"],
                node_type=LineageNodeType(node_data["node_type"]),
                name=node_data["name"],
                qualified_name=node_data["qualified_name"],
                properties=node_data.get("properties", {}),
                tags=node_data.get("tags", [])
            )
            graph.add_node(node)
        
        for edge_data in data.get("edges", []):
            edge = LineageEdge(
                edge_id=edge_data["edge_id"],
                source_id=edge_data["source_id"],
                target_id=edge_data["target_id"],
                edge_type=LineageEdgeType(edge_data["edge_type"]),
                properties=edge_data.get("properties", {}),
                transformation=edge_data.get("transformation")
            )
            graph.add_edge(edge)
        
        return graph
```

---

## 第46页

```python
class LineageTracker:
    """血缘追踪器"""
    
    def __init__(self, graph: Optional[LineageGraph] = None):
        self.graph = graph or LineageGraph()
        self._parsers: Dict[str, Any] = {}
    
    def register_table(
        self,
        database: str,
        schema: str,
        table: str,
        columns: List[Dict[str, Any]],
        properties: Optional[Dict] = None
    ) -> str:
        """注册数据表"""
        db_qn = database
        db_node = self.graph.get_node_by_qualified_name(db_qn)
        if not db_node:
            db_node = LineageNode(
                node_id=str(uuid.uuid4()),
                node_type=LineageNodeType.DATABASE,
                name=database,
                qualified_name=db_qn
            )
            self.graph.add_node(db_node)
        
        schema_qn = f"{database}.{schema}"
        schema_node = self.graph.get_node_by_qualified_name(schema_qn)
        if not schema_node:
            schema_node = LineageNode(
                node_id=str(uuid.uuid4()),
                node_type=LineageNodeType.SCHEMA,
                name=schema,
                qualified_name=schema_qn
            )
            self.graph.add_node(schema_node)
            self.graph.add_edge(LineageEdge(
                edge_id=str(uuid.uuid4()),
                source_id=db_node.node_id,
                target_id=schema_node.node_id,
                edge_type=LineageEdgeType.CONTAINS
            ))
        
        table_qn = f"{database}.{schema}.{table}"
        table_node = LineageNode(
            node_id=str(uuid.uuid4()),
            node_type=LineageNodeType.TABLE,
            name=table,
            qualified_name=table_qn,
            properties=properties or {}
        )
        self.graph.add_node(table_node)
        self.graph.add_edge(LineageEdge(
            edge_id=str(uuid.uuid4()),
            source_id=schema_node.node_id,
            target_id=table_node.node_id,
            edge_type=LineageEdgeType.CONTAINS
        ))
        
        for col in columns:
            col_qn = f"{table_qn}.{col['name']}"
            col_node = LineageNode(
                node_id=str(uuid.uuid4()),
                node_type=LineageNodeType.COLUMN,
                name=col["name"],
                qualified_name=col_qn,
                properties={"data_type": col.get("type", "unknown")}
            )
            self.graph.add_node(col_node)
            self.graph.add_edge(LineageEdge(
                edge_id=str(uuid.uuid4()),
                source_id=table_node.node_id,
                target_id=col_node.node_id,
                edge_type=LineageEdgeType.CONTAINS
            ))
        
        return table_node.node_id
```

---

## 第47页

```python
    def track_transformation(
        self,
        source_tables: List[str],
        target_table: str,
        transformation_sql: Optional[str] = None,
        column_mappings: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """追踪数据转换"""
        trans_node = LineageNode(
            node_id=str(uuid.uuid4()),
            node_type=LineageNodeType.TRANSFORMATION,
            name=f"transform_to_{target_table.split('.')[-1]}",
            qualified_name=f"transformation_{uuid.uuid4().hex[:8]}",
            properties={"sql": transformation_sql} if transformation_sql else {}
        )
        self.graph.add_node(trans_node)
        
        for source_table in source_tables:
            source_node = self.graph.get_node_by_qualified_name(source_table)
            if source_node:
                self.graph.add_edge(LineageEdge(
                    edge_id=str(uuid.uuid4()),
                    source_id=source_node.node_id,
                    target_id=trans_node.node_id,
                    edge_type=LineageEdgeType.READS_FROM
                ))
        
        target_node = self.graph.get_node_by_qualified_name(target_table)
        if target_node:
            self.graph.add_edge(LineageEdge(
                edge_id=str(uuid.uuid4()),
                source_id=trans_node.node_id,
                target_id=target_node.node_id,
                edge_type=LineageEdgeType.WRITES_TO,
                transformation=transformation_sql
            ))
        
        if column_mappings:
            for mapping in column_mappings:
                source_col = mapping.get("source")
                target_col = mapping.get("target")
                
                source_col_node = self.graph.get_node_by_qualified_name(source_col)
                target_col_node = self.graph.get_node_by_qualified_name(target_col)
                
                if source_col_node and target_col_node:
                    self.graph.add_edge(LineageEdge(
                        edge_id=str(uuid.uuid4()),
                        source_id=source_col_node.node_id,
                        target_id=target_col_node.node_id,
                        edge_type=LineageEdgeType.DERIVES_FROM,
                        transformation=mapping.get("transformation")
                    ))
        
        return trans_node.node_id
    
    def get_table_lineage(self, table_qualified_name: str) -> Dict[str, Any]:
        """获取表血缘"""
        table_node = self.graph.get_node_by_qualified_name(table_qualified_name)
        if not table_node:
            return {"error": "Table not found"}
        
        upstream = self.graph.get_upstream(table_node.node_id)
        downstream = self.graph.get_downstream(table_node.node_id)
        
        return {
            "table": table_node.to_dict(),
            "upstream": [n.to_dict() for n in upstream if n.node_type == LineageNodeType.TABLE],
            "downstream": [n.to_dict() for n in downstream if n.node_type == LineageNodeType.TABLE]
        }
```

---

## 第48页

```python
# -*- coding: utf-8 -*-
"""
datacore数据中台系统 - 数据服务API模块
Copyright (c) 2024 北京灵犀科技有限公司
文件: api/data_service.py
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json
import time
import logging
from functools import wraps
import asyncio
from aiohttp import web
import aioredis

logger = logging.getLogger(__name__)


class ApiStatus(Enum):
    """API状态"""
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    DISABLED = "disabled"


class AuthType(Enum):
    """认证类型"""
    NONE = "none"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"


@dataclass
class ApiConfig:
    """API配置"""
    api_id: str
    name: str
    path: str
    method: str = "GET"
    description: str = ""
    status: ApiStatus = ApiStatus.DRAFT
    auth_type: AuthType = AuthType.API_KEY
    rate_limit: int = 100
    timeout_seconds: int = 30
    cache_ttl: int = 0
    query_template: str = ""
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    response_mapping: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
```

---

## 第49页

```python
@dataclass
class ApiCallLog:
    """API调用日志"""
    log_id: str
    api_id: str
    client_id: str
    request_path: str
    request_params: Dict[str, Any]
    response_status: int
    response_time_ms: float
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
    
    async def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int = 60
    ) -> bool:
        """检查是否允许请求"""
        current = int(time.time())
        window_start = current - window_seconds
        
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(current): current})
        pipe.zcard(key)
        pipe.expire(key, window_seconds)
        
        results = await pipe.execute()
        request_count = results[2]
        
        return request_count <= limit
    
    async def get_remaining(
        self,
        key: str,
        limit: int,
        window_seconds: int = 60
    ) -> int:
        """获取剩余请求次数"""
        current = int(time.time())
        window_start = current - window_seconds
        
        await self.redis.zremrangebyscore(key, 0, window_start)
        count = await self.redis.zcard(key)
        
        return max(0, limit - count)


class ApiCache:
    """API缓存"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
    
    def _generate_key(self, api_id: str, params: Dict) -> str:
        """生成缓存键"""
        param_str = json.dumps(params, sort_keys=True)
        hash_val = hashlib.md5(param_str.encode()).hexdigest()
        return f"api_cache:{api_id}:{hash_val}"
```

---

## 第50页

```python
    async def get(self, api_id: str, params: Dict) -> Optional[Dict]:
        """获取缓存"""
        key = self._generate_key(api_id, params)
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set(
        self,
        api_id: str,
        params: Dict,
        response: Dict,
        ttl: int
    ) -> None:
        """设置缓存"""
        if ttl <= 0:
            return
        key = self._generate_key(api_id, params)
        await self.redis.setex(key, ttl, json.dumps(response))
    
    async def invalidate(self, api_id: str) -> int:
        """使缓存失效"""
        pattern = f"api_cache:{api_id}:*"
        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0


class DataServiceManager:
    """数据服务管理器"""
    
    def __init__(
        self,
        db_executor,
        redis_client: aioredis.Redis
    ):
        self.db_executor = db_executor
        self.redis = redis_client
        self.rate_limiter = RateLimiter(redis_client)
        self.cache = ApiCache(redis_client)
        self.apis: Dict[str, ApiConfig] = {}
        self._call_logs: List[ApiCallLog] = []
    
    def register_api(self, config: ApiConfig) -> None:
        """注册API"""
        self.apis[config.api_id] = config
        logger.info(f"Registered API: {config.api_id} - {config.path}")
    
    def unregister_api(self, api_id: str) -> bool:
        """注销API"""
        if api_id in self.apis:
            del self.apis[api_id]
            return True
        return False
    
    def get_api(self, api_id: str) -> Optional[ApiConfig]:
        """获取API配置"""
        return self.apis.get(api_id)
    
    def list_apis(
        self,
        status: Optional[ApiStatus] = None
    ) -> List[ApiConfig]:
        """列出API"""
        apis = list(self.apis.values())
        if status:
            apis = [a for a in apis if a.status == status]
        return apis
```

---

## 第51页

```python
    async def execute_api(
        self,
        api_id: str,
        params: Dict[str, Any],
        client_id: str
    ) -> Dict[str, Any]:
        """执行API调用"""
        start_time = time.time()
        
        api = self.apis.get(api_id)
        if not api:
            return {"error": "API not found", "code": 404}
        
        if api.status != ApiStatus.PUBLISHED:
            return {"error": "API not available", "code": 403}
        
        rate_key = f"rate:{api_id}:{client_id}"
        if not await self.rate_limiter.is_allowed(rate_key, api.rate_limit):
            return {"error": "Rate limit exceeded", "code": 429}
        
        cached = await self.cache.get(api_id, params)
        if cached:
            return {"data": cached, "cached": True}
        
        try:
            validated_params = self._validate_params(api, params)
            query = self._build_query(api, validated_params)
            
            result = await asyncio.wait_for(
                self.db_executor.execute(query, validated_params),
                timeout=api.timeout_seconds
            )
            
            response = self._map_response(api, result)
            
            if api.cache_ttl > 0:
                await self.cache.set(api_id, params, response, api.cache_ttl)
            
            elapsed = (time.time() - start_time) * 1000
            self._log_call(api_id, client_id, api.path, params, 200, elapsed)
            
            return {"data": response, "cached": False}
            
        except asyncio.TimeoutError:
            elapsed = (time.time() - start_time) * 1000
            self._log_call(api_id, client_id, api.path, params, 504, elapsed, "Timeout")
            return {"error": "Request timeout", "code": 504}
            
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            self._log_call(api_id, client_id, api.path, params, 500, elapsed, str(e))
            logger.error(f"API execution error: {api_id}, {str(e)}")
            return {"error": "Internal error", "code": 500}
    
    def _validate_params(
        self,
        api: ApiConfig,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证参数"""
        validated = {}
        
        for param_def in api.parameters:
            name = param_def["name"]
            required = param_def.get("required", False)
            default = param_def.get("default")
            param_type = param_def.get("type", "string")
            
            if name in params:
                validated[name] = self._cast_value(params[name], param_type)
            elif required:
                raise ValueError(f"Missing required parameter: {name}")
            elif default is not None:
                validated[name] = default
        
        return validated
```

---

## 第52页

```python
    def _cast_value(self, value: Any, param_type: str) -> Any:
        """类型转换"""
        if param_type == "integer":
            return int(value)
        elif param_type == "number":
            return float(value)
        elif param_type == "boolean":
            if isinstance(value, bool):
                return value
            return value.lower() in ("true", "1", "yes")
        elif param_type == "array":
            if isinstance(value, list):
                return value
            return value.split(",")
        return str(value)
    
    def _build_query(self, api: ApiConfig, params: Dict) -> str:
        """构建查询"""
        query = api.query_template
        for key, value in params.items():
            placeholder = f":{key}"
            if placeholder in query:
                if isinstance(value, str):
                    escaped = value.replace("'", "''")
                    query = query.replace(placeholder, f"'{escaped}'")
                elif isinstance(value, list):
                    items = ", ".join(f"'{v}'" for v in value)
                    query = query.replace(placeholder, f"({items})")
                else:
                    query = query.replace(placeholder, str(value))
        return query
    
    def _map_response(
        self,
        api: ApiConfig,
        result: List[Dict]
    ) -> List[Dict]:
        """映射响应"""
        if not api.response_mapping:
            return result
        
        mapped = []
        for row in result:
            mapped_row = {}
            for target_key, source_key in api.response_mapping.items():
                if source_key in row:
                    mapped_row[target_key] = row[source_key]
            mapped.append(mapped_row)
        return mapped
    
    def _log_call(
        self,
        api_id: str,
        client_id: str,
        path: str,
        params: Dict,
        status: int,
        elapsed: float,
        error: Optional[str] = None
    ) -> None:
        """记录调用日志"""
        log = ApiCallLog(
            log_id=hashlib.md5(f"{api_id}{time.time()}".encode()).hexdigest(),
            api_id=api_id,
            client_id=client_id,
            request_path=path,
            request_params=params,
            response_status=status,
            response_time_ms=elapsed,
            error_message=error
        )
        self._call_logs.append(log)
        
        if len(self._call_logs) > 10000:
            self._call_logs = self._call_logs[-5000:]
```

---

## 第53页

```python
    def get_api_statistics(self, api_id: str) -> Dict[str, Any]:
        """获取API统计"""
        logs = [l for l in self._call_logs if l.api_id == api_id]
        
        if not logs:
            return {"api_id": api_id, "total_calls": 0}
        
        total = len(logs)
        success = sum(1 for l in logs if l.response_status == 200)
        avg_time = sum(l.response_time_ms for l in logs) / total
        
        status_distribution = {}
        for log in logs:
            status = str(log.response_status)
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        return {
            "api_id": api_id,
            "total_calls": total,
            "success_calls": success,
            "success_rate": success / total,
            "average_response_time_ms": avg_time,
            "status_distribution": status_distribution
        }


# -*- coding: utf-8 -*-
"""
datacore数据中台系统 - 数据安全与权限模块
Copyright (c) 2024 北京灵犀科技有限公司
文件: security/access_control.py
"""

from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets
import jwt
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class Permission(Enum):
    """权限枚举"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    EXPORT = "export"
    SHARE = "share"


class ResourceType(Enum):
    """资源类型"""
    DATABASE = "database"
    TABLE = "table"
    COLUMN = "column"
    API = "api"
    DASHBOARD = "dashboard"
    REPORT = "report"
```

---

## 第54页

```python
@dataclass
class Role:
    """角色"""
    role_id: str
    name: str
    description: str = ""
    permissions: Set[Permission] = field(default_factory=set)
    resource_permissions: Dict[str, Set[Permission]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def has_permission(self, permission: Permission) -> bool:
        """检查是否有权限"""
        return Permission.ADMIN in self.permissions or permission in self.permissions
    
    def has_resource_permission(
        self,
        resource_id: str,
        permission: Permission
    ) -> bool:
        """检查是否有资源权限"""
        if self.has_permission(Permission.ADMIN):
            return True
        if self.has_permission(permission):
            return True
        resource_perms = self.resource_permissions.get(resource_id, set())
        return permission in resource_perms


@dataclass
class User:
    """用户"""
    user_id: str
    username: str
    email: str
    password_hash: str
    roles: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    is_active: bool = True
    is_superuser: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def set_password(self, password: str) -> None:
        """设置密码"""
        salt = secrets.token_hex(16)
        hash_val = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            100000
        )
        self.password_hash = f"{salt}${hash_val.hex()}"
    
    def verify_password(self, password: str) -> bool:
        """验证密码"""
        if "$" not in self.password_hash:
            return False
        salt, stored_hash = self.password_hash.split("$")
        hash_val = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            100000
        )
        return hash_val.hex() == stored_hash
```

---

## 第55页

```python
@dataclass
class Group:
    """用户组"""
    group_id: str
    name: str
    description: str = ""
    roles: List[str] = field(default_factory=list)
    parent_group: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AccessToken:
    """访问令牌"""
    token_id: str
    user_id: str
    token_type: str = "bearer"
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=24))
    scopes: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


class AccessControlManager:
    """访问控制管理器"""
    
    def __init__(self, jwt_secret: str, token_expiry_hours: int = 24):
        self.jwt_secret = jwt_secret
        self.token_expiry_hours = token_expiry_hours
        self.users: Dict[str, User] = {}
        self.roles: Dict[str, Role] = {}
        self.groups: Dict[str, Group] = {}
        self._tokens: Dict[str, AccessToken] = {}
        self._username_index: Dict[str, str] = {}
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        roles: Optional[List[str]] = None
    ) -> User:
        """创建用户"""
        if username in self._username_index:
            raise ValueError(f"Username already exists: {username}")
        
        user_id = hashlib.md5(f"{username}{datetime.now()}".encode()).hexdigest()
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash="",
            roles=roles or []
        )
        user.set_password(password)
        
        self.users[user_id] = user
        self._username_index[username] = user_id
        
        logger.info(f"Created user: {username}")
        return user
```

---

## 第56页

```python
    def authenticate(
        self,
        username: str,
        password: str
    ) -> Optional[AccessToken]:
        """用户认证"""
        user_id = self._username_index.get(username)
        if not user_id:
            logger.warning(f"Authentication failed: user not found - {username}")
            return None
        
        user = self.users.get(user_id)
        if not user or not user.is_active:
            logger.warning(f"Authentication failed: user inactive - {username}")
            return None
        
        if not user.verify_password(password):
            logger.warning(f"Authentication failed: invalid password - {username}")
            return None
        
        user.last_login = datetime.now()
        token = self._generate_token(user)
        
        logger.info(f"User authenticated: {username}")
        return token
    
    def _generate_token(self, user: User) -> AccessToken:
        """生成访问令牌"""
        token_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=self.token_expiry_hours)
        
        payload = {
            "token_id": token_id,
            "user_id": user.user_id,
            "username": user.username,
            "roles": user.roles,
            "exp": expires_at.timestamp()
        }
        
        jwt_token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
        
        token = AccessToken(
            token_id=token_id,
            user_id=user.user_id,
            expires_at=expires_at,
            scopes=self._get_user_scopes(user)
        )
        
        self._tokens[token_id] = token
        return token
    
    def _get_user_scopes(self, user: User) -> List[str]:
        """获取用户权限范围"""
        scopes = set()
        
        for role_id in user.roles:
            role = self.roles.get(role_id)
            if role:
                for perm in role.permissions:
                    scopes.add(perm.value)
        
        for group_id in user.groups:
            group = self.groups.get(group_id)
            if group:
                for role_id in group.roles:
                    role = self.roles.get(role_id)
                    if role:
                        for perm in role.permissions:
                            scopes.add(perm.value)
        
        return list(scopes)
```

---

## 第57页

```python
    def verify_token(self, jwt_token: str) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            payload = jwt.decode(jwt_token, self.jwt_secret, algorithms=["HS256"])
            token_id = payload.get("token_id")
            
            token = self._tokens.get(token_id)
            if not token or token.is_expired:
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
    
    def revoke_token(self, token_id: str) -> bool:
        """撤销令牌"""
        if token_id in self._tokens:
            del self._tokens[token_id]
            return True
        return False
    
    def create_role(
        self,
        name: str,
        permissions: List[Permission],
        description: str = ""
    ) -> Role:
        """创建角色"""
        role_id = hashlib.md5(f"{name}{datetime.now()}".encode()).hexdigest()
        role = Role(
            role_id=role_id,
            name=name,
            description=description,
            permissions=set(permissions)
        )
        self.roles[role_id] = role
        logger.info(f"Created role: {name}")
        return role
    
    def assign_role(self, user_id: str, role_id: str) -> bool:
        """分配角色"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        if role_id not in self.roles:
            return False
        
        if role_id not in user.roles:
            user.roles.append(role_id)
        return True
    
    def check_permission(
        self,
        user_id: str,
        permission: Permission,
        resource_id: Optional[str] = None
    ) -> bool:
        """检查权限"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        if user.is_superuser:
            return True
        
        for role_id in user.roles:
            role = self.roles.get(role_id)
            if role:
                if resource_id:
                    if role.has_resource_permission(resource_id, permission):
                        return True
                elif role.has_permission(permission):
                    return True
        
        return False
```

---

## 第58页

```python
class DataMasking:
    """数据脱敏"""
    
    MASKING_RULES = {
        "phone": lambda v: v[:3] + "****" + v[-4:] if len(v) >= 11 else "***",
        "email": lambda v: v.split("@")[0][:2] + "***@" + v.split("@")[1] if "@" in v else "***",
        "id_card": lambda v: v[:6] + "********" + v[-4:] if len(v) >= 18 else "***",
        "name": lambda v: v[0] + "*" * (len(v) - 1) if len(v) > 1 else "*",
        "bank_card": lambda v: v[:4] + " **** **** " + v[-4:] if len(v) >= 16 else "***",
        "address": lambda v: v[:6] + "***" if len(v) > 6 else "***",
        "full": lambda v: "*" * len(str(v))
    }
    
    def __init__(self):
        self.field_rules: Dict[str, str] = {}
        self.custom_rules: Dict[str, Callable] = {}
    
    def register_field_rule(self, field_name: str, rule_type: str) -> None:
        """注册字段脱敏规则"""
        self.field_rules[field_name] = rule_type
    
    def register_custom_rule(
        self,
        rule_name: str,
        mask_func: Callable[[Any], Any]
    ) -> None:
        """注册自定义脱敏规则"""
        self.custom_rules[rule_name] = mask_func
    
    def mask_value(self, value: Any, rule_type: str) -> Any:
        """脱敏单个值"""
        if value is None:
            return None
        
        if rule_type in self.custom_rules:
            return self.custom_rules[rule_type](value)
        
        if rule_type in self.MASKING_RULES:
            return self.MASKING_RULES[rule_type](str(value))
        
        return value
    
    def mask_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """脱敏记录"""
        masked = {}
        for key, value in record.items():
            if key in self.field_rules:
                masked[key] = self.mask_value(value, self.field_rules[key])
            else:
                masked[key] = value
        return masked
    
    def mask_records(self, records: List[Dict]) -> List[Dict]:
        """批量脱敏"""
        return [self.mask_record(r) for r in records]
```

---

## 第59页

```python
class AuditLogger:
    """审计日志"""
    
    def __init__(self, storage_backend=None):
        self.storage = storage_backend
        self._logs: List[Dict] = []
    
    def log_access(
        self,
        user_id: str,
        resource_type: ResourceType,
        resource_id: str,
        action: str,
        success: bool,
        details: Optional[Dict] = None
    ) -> None:
        """记录访问日志"""
        log_entry = {
            "log_id": hashlib.md5(f"{user_id}{datetime.now()}".encode()).hexdigest(),
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "resource_type": resource_type.value,
            "resource_id": resource_id,
            "action": action,
            "success": success,
            "details": details or {}
        }
        
        self._logs.append(log_entry)
        
        if self.storage:
            self.storage.write(log_entry)
        
        if len(self._logs) > 50000:
            self._logs = self._logs[-25000:]
    
    def log_data_access(
        self,
        user_id: str,
        table_name: str,
        columns: List[str],
        row_count: int,
        query: Optional[str] = None
    ) -> None:
        """记录数据访问"""
        self.log_access(
            user_id=user_id,
            resource_type=ResourceType.TABLE,
            resource_id=table_name,
            action="data_access",
            success=True,
            details={
                "columns": columns,
                "row_count": row_count,
                "query": query[:500] if query else None
            }
        )
    
    def query_logs(
        self,
        user_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """查询日志"""
        results = self._logs
        
        if user_id:
            results = [l for l in results if l["user_id"] == user_id]
        
        if resource_type:
            results = [l for l in results if l["resource_type"] == resource_type.value]
        
        if start_time:
            results = [l for l in results if l["timestamp"] >= start_time.isoformat()]
        
        if end_time:
            results = [l for l in results if l["timestamp"] <= end_time.isoformat()]
        
        return results[-limit:]
```

---

## 第60页

```python
# -*- coding: utf-8 -*-
"""
datacore数据中台系统 - 数据资产目录模块
Copyright (c) 2024 北京灵犀科技有限公司
文件: catalog/asset_catalog.py
"""

from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class AssetType(Enum):
    """资产类型"""
    DATABASE = "database"
    TABLE = "table"
    VIEW = "view"
    COLUMN = "column"
    FILE = "file"
    API = "api"
    REPORT = "report"
    MODEL = "model"


class AssetStatus(Enum):
    """资产状态"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    PENDING = "pending"


@dataclass
class AssetMetadata:
    """资产元数据"""
    asset_id: str
    asset_type: AssetType
    name: str
    qualified_name: str
    description: str = ""
    owner: str = ""
    status: AssetStatus = AssetStatus.ACTIVE
    tags: List[str] = field(default_factory=list)
    classifications: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type.value,
            "name": self.name,
            "qualified_name": self.qualified_name,
            "description": self.description,
            "owner": self.owner,
            "status": self.status.value,
            "tags": self.tags,
            "classifications": self.classifications,
            "properties": self.properties,
            "statistics": self.statistics,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
```

人工智能生成内容：北京灵犀科技有限公司 - datacore数据中台系统 V1.0 源程序
第31-60页 / 共60页
