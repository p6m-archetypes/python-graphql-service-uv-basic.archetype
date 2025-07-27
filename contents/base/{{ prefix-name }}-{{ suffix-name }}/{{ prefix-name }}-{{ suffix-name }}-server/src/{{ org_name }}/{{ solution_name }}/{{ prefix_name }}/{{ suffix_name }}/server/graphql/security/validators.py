"""
GraphQL security validators for {{ PrefixName }}{{ SuffixName }}.

This module provides comprehensive validation and analysis tools
for GraphQL operations, including security rule engines and
advanced threat detection capabilities.
"""

import re
import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

from graphql import GraphQLError, DocumentNode, visit, Visitor
from graphql.language import ast

from .config import get_security_config

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels for security analysis."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityThreat:
    """Represents a detected security threat."""
    
    threat_type: str
    threat_level: ThreatLevel
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    mitigated: bool = False
    mitigation_action: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of security validation."""
    
    is_valid: bool
    threats: List[SecurityThreat] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def has_critical_threats(self) -> bool:
        """Check if there are any critical threats."""
        return any(threat.threat_level == ThreatLevel.CRITICAL for threat in self.threats)
    
    @property
    def has_high_threats(self) -> bool:
        """Check if there are any high-level threats."""
        return any(threat.threat_level == ThreatLevel.HIGH for threat in self.threats)
    
    def get_threats_by_level(self, level: ThreatLevel) -> List[SecurityThreat]:
        """Get threats by severity level."""
        return [threat for threat in self.threats if threat.threat_level == level]


class GraphQLSecurityValidator:
    """
    Comprehensive GraphQL security validator.
    
    Performs deep analysis of GraphQL queries for security threats,
    vulnerabilities, and malicious patterns.
    """
    
    def __init__(self):
        """Initialize the security validator."""
        self.config = get_security_config()
        self.threat_patterns = self._load_threat_patterns()
        self.validation_cache: Dict[str, ValidationResult] = {}
        self.cache_expiry = timedelta(minutes=5)
        
    def validate_query(
        self, 
        document: DocumentNode, 
        variables: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Perform comprehensive security validation of a GraphQL query.
        
        Args:
            document: GraphQL document to validate
            variables: Query variables
            context: Additional context for validation
            
        Returns:
            ValidationResult with threats and warnings
        """
        # Generate cache key
        cache_key = self._generate_cache_key(document, variables)
        
        # Check cache
        if cache_key in self.validation_cache:
            cached_result = self.validation_cache[cache_key]
            if datetime.utcnow() - cached_result.metadata.get("cached_at", datetime.min) < self.cache_expiry:
                return cached_result
        
        # Perform validation
        result = ValidationResult(is_valid=True)
        
        try:
            # Analyze query structure
            self._analyze_query_structure(document, result)
            
            # Check for injection patterns
            self._check_injection_patterns(document, variables, result)
            
            # Validate operation complexity
            self._validate_operation_complexity(document, result)
            
            # Check for information disclosure risks
            self._check_information_disclosure(document, result)
            
            # Analyze field access patterns
            self._analyze_field_access_patterns(document, result)
            
            # Validate against custom security rules
            self._apply_custom_security_rules(document, variables, context, result)
            
            # Determine overall validation result
            result.is_valid = not (result.has_critical_threats or result.has_high_threats)
            
            # Cache result
            result.metadata["cached_at"] = datetime.utcnow()
            result.metadata["validation_duration_ms"] = 0  # Would measure actual time
            self.validation_cache[cache_key] = result
            
        except Exception as e:
            logger.error(f"Security validation error: {e}")
            result.threats.append(SecurityThreat(
                threat_type="validation_error",
                threat_level=ThreatLevel.HIGH,
                description="Failed to complete security validation",
                details={"error": str(e)}
            ))
            result.is_valid = False
        
        return result
    
    def _analyze_query_structure(self, document: DocumentNode, result: ValidationResult):
        """Analyze the structure of the GraphQL query for suspicious patterns."""
        analyzer = QueryStructureAnalyzer()
        visit(document, analyzer)
        
        # Check for excessive nesting
        if analyzer.max_depth > 20:
            result.threats.append(SecurityThreat(
                threat_type="excessive_nesting",
                threat_level=ThreatLevel.HIGH,
                description=f"Query depth ({analyzer.max_depth}) exceeds safe limits",
                details={"max_depth": analyzer.max_depth, "safe_limit": 20}
            ))
        
        # Check for too many fields
        if analyzer.field_count > 100:
            result.threats.append(SecurityThreat(
                threat_type="excessive_fields",
                threat_level=ThreatLevel.MEDIUM,
                description=f"Query requests too many fields ({analyzer.field_count})",
                details={"field_count": analyzer.field_count, "safe_limit": 100}
            ))
        
        # Check for suspicious field patterns
        for pattern in analyzer.suspicious_patterns:
            result.threats.append(SecurityThreat(
                threat_type="suspicious_pattern",
                threat_level=ThreatLevel.LOW,
                description=f"Suspicious query pattern detected: {pattern}",
                details={"pattern": pattern}
            ))
    
    def _check_injection_patterns(
        self, 
        document: DocumentNode, 
        variables: Optional[Dict[str, Any]], 
        result: ValidationResult
    ):
        """Check for various injection attack patterns."""
        query_string = str(document)
        
        # SQL injection patterns
        sql_patterns = [
            r"\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b",
            r"['\";](\s)*(OR|AND)\s+['\"]?1['\"]?\s*=\s*['\"]?1",
            r"['\"];.*--",
            r"\bEXEC\s*\(",
            r"\bSP_\w+",
            r"/\*.*\*/"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, query_string, re.IGNORECASE):
                result.threats.append(SecurityThreat(
                    threat_type="sql_injection",
                    threat_level=ThreatLevel.CRITICAL,
                    description="Potential SQL injection pattern detected",
                    details={"pattern": pattern, "query_fragment": query_string[:100]}
                ))
        
        # NoSQL injection patterns
        nosql_patterns = [
            r"\$where",
            r"\$ne\s*:",
            r"\$gt\s*:",
            r"\$regex\s*:",
            r"this\s*\.",
            r"function\s*\("
        ]
        
        for pattern in nosql_patterns:
            if re.search(pattern, query_string, re.IGNORECASE):
                result.threats.append(SecurityThreat(
                    threat_type="nosql_injection",
                    threat_level=ThreatLevel.HIGH,
                    description="Potential NoSQL injection pattern detected",
                    details={"pattern": pattern}
                ))
        
        # Check variables for injection patterns
        if variables:
            self._check_variable_injection(variables, result)
    
    def _check_variable_injection(self, variables: Dict[str, Any], result: ValidationResult):
        """Check variables for injection patterns."""
        dangerous_patterns = [
            r"<script[^>]*>",
            r"javascript:",
            r"vbscript:",
            r"on\w+\s*=",
            r"eval\s*\(",
            r"\bUNION\b.*\bSELECT\b",
            r"['\"];.*--",
        ]
        
        def check_value(value: Any, path: str = ""):
            if isinstance(value, str):
                for pattern in dangerous_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        result.threats.append(SecurityThreat(
                            threat_type="variable_injection",
                            threat_level=ThreatLevel.HIGH,
                            description=f"Dangerous pattern in variable {path}",
                            details={"pattern": pattern, "variable_path": path, "value": value[:100]}
                        ))
            elif isinstance(value, dict):
                for key, val in value.items():
                    check_value(val, f"{path}.{key}" if path else key)
            elif isinstance(value, list):
                for i, val in enumerate(value):
                    check_value(val, f"{path}[{i}]")
        
        for var_name, var_value in variables.items():
            check_value(var_value, var_name)
    
    def _validate_operation_complexity(self, document: DocumentNode, result: ValidationResult):
        """Validate the complexity of GraphQL operations."""
        complexity_analyzer = ComplexityAnalyzer()
        visit(document, complexity_analyzer)
        
        # Check query complexity
        max_complexity = self.config.query_complexity.maximum_complexity
        if complexity_analyzer.complexity > max_complexity:
            result.threats.append(SecurityThreat(
                threat_type="excessive_complexity",
                threat_level=ThreatLevel.HIGH,
                description=f"Query complexity ({complexity_analyzer.complexity}) exceeds limit",
                details={
                    "complexity": complexity_analyzer.complexity,
                    "limit": max_complexity,
                    "complexity_breakdown": complexity_analyzer.complexity_breakdown
                }
            ))
        
        # Check for complexity bombs (exponential growth patterns)
        if complexity_analyzer.has_exponential_patterns:
            result.threats.append(SecurityThreat(
                threat_type="complexity_bomb",
                threat_level=ThreatLevel.CRITICAL,
                description="Query contains exponential complexity patterns",
                details={"exponential_patterns": complexity_analyzer.exponential_patterns}
            ))
    
    def _check_information_disclosure(self, document: DocumentNode, result: ValidationResult):
        """Check for potential information disclosure risks."""
        disclosure_analyzer = InformationDisclosureAnalyzer()
        visit(document, disclosure_analyzer)
        
        # Check for introspection queries
        if disclosure_analyzer.has_introspection:
            if not self.config.enable_introspection:
                result.threats.append(SecurityThreat(
                    threat_type="introspection_disabled",
                    threat_level=ThreatLevel.MEDIUM,
                    description="Introspection query attempted but introspection is disabled",
                    details={"introspection_fields": disclosure_analyzer.introspection_fields}
                ))
        
        # Check for sensitive field access
        for sensitive_field in disclosure_analyzer.sensitive_fields:
            result.warnings.append(f"Access to sensitive field: {sensitive_field}")
    
    def _analyze_field_access_patterns(self, document: DocumentNode, result: ValidationResult):
        """Analyze field access patterns for anomalies."""
        field_analyzer = FieldAccessAnalyzer()
        visit(document, field_analyzer)
        
        # Check for enumeration patterns
        if field_analyzer.has_enumeration_pattern:
            result.threats.append(SecurityThreat(
                threat_type="enumeration_attempt",
                threat_level=ThreatLevel.MEDIUM,
                description="Query shows signs of data enumeration attempt",
                details={"enumeration_indicators": field_analyzer.enumeration_indicators}
            ))
        
        # Check for batch query abuse
        if field_analyzer.operation_count > 10:
            result.threats.append(SecurityThreat(
                threat_type="batch_abuse",
                threat_level=ThreatLevel.HIGH,
                description=f"Excessive batch operations ({field_analyzer.operation_count})",
                details={"operation_count": field_analyzer.operation_count}
            ))
    
    def _apply_custom_security_rules(
        self, 
        document: DocumentNode, 
        variables: Optional[Dict[str, Any]], 
        context: Optional[Dict[str, Any]], 
        result: ValidationResult
    ):
        """Apply custom security rules defined in configuration."""
        # This would be expanded based on specific security requirements
        pass
    
    def _load_threat_patterns(self) -> Dict[str, List[str]]:
        """Load threat detection patterns."""
        return {
            "sql_injection": [
                r"\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP)\b",
                r"['\"];.*--",
                r"\bOR\s+1\s*=\s*1\b",
                r"\bAND\s+1\s*=\s*1\b"
            ],
            "script_injection": [
                r"<script[^>]*>",
                r"javascript:",
                r"vbscript:",
                r"on\w+\s*="
            ],
            "path_traversal": [
                r"\.\./",
                r"\.\.\\",
                r"/etc/passwd",
                r"c:\\windows"
            ]
        }
    
    def _generate_cache_key(self, document: DocumentNode, variables: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for validation result."""
        import hashlib
        
        content = str(document)
        if variables:
            content += str(sorted(variables.items()))
        
        return hashlib.sha256(content.encode()).hexdigest()


class QueryStructureAnalyzer(Visitor):
    """Analyzes GraphQL query structure for security threats."""
    
    def __init__(self):
        self.max_depth = 0
        self.current_depth = 0
        self.field_count = 0
        self.suspicious_patterns = []
        self.operation_names = []
    
    def enter_field(self, node: ast.FieldNode, *_):
        """Analyze field entry."""
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.field_count += 1
        
        field_name = node.name.value
        
        # Check for suspicious field names
        suspicious_keywords = [
            "admin", "internal", "debug", "test", "secret", 
            "password", "token", "key", "private"
        ]
        
        if any(keyword in field_name.lower() for keyword in suspicious_keywords):
            self.suspicious_patterns.append(f"Suspicious field name: {field_name}")
    
    def leave_field(self, node: ast.FieldNode, *_):
        """Handle field exit."""
        self.current_depth -= 1
    
    def enter_operation_definition(self, node: ast.OperationDefinitionNode, *_):
        """Analyze operation definition."""
        if node.name:
            self.operation_names.append(node.name.value)


class ComplexityAnalyzer(Visitor):
    """Analyzes GraphQL query complexity for DoS protection."""
    
    def __init__(self):
        self.complexity = 0
        self.complexity_breakdown = {}
        self.has_exponential_patterns = False
        self.exponential_patterns = []
        self.list_fields = []
        self.connection_fields = []
    
    def enter_field(self, node: ast.FieldNode, *_):
        """Calculate field complexity."""
        field_name = node.name.value
        field_complexity = 1
        
        # Higher complexity for list fields
        if any(pattern in field_name.lower() for pattern in ["list", "all", "many", "items"]):
            field_complexity = 5
            self.list_fields.append(field_name)
        
        # Even higher complexity for connection fields
        if any(pattern in field_name.lower() for pattern in ["connection", "edge"]):
            field_complexity = 10
            self.connection_fields.append(field_name)
        
        # Check for arguments that could cause exponential growth
        if node.arguments:
            for arg in node.arguments:
                if arg.name.value in ["first", "last", "limit", "size"]:
                    if hasattr(arg.value, 'value') and isinstance(arg.value.value, int):
                        if arg.value.value > 100:
                            self.has_exponential_patterns = True
                            self.exponential_patterns.append(f"{field_name}.{arg.name.value}={arg.value.value}")
        
        self.complexity += field_complexity
        self.complexity_breakdown[field_name] = field_complexity


class InformationDisclosureAnalyzer(Visitor):
    """Analyzes queries for information disclosure risks."""
    
    def __init__(self):
        self.has_introspection = False
        self.introspection_fields = []
        self.sensitive_fields = []
        
        # Define sensitive field patterns
        self.sensitive_patterns = [
            r".*password.*",
            r".*secret.*",
            r".*token.*",
            r".*key.*",
            r".*credential.*",
            r".*private.*"
        ]
    
    def enter_field(self, node: ast.FieldNode, *_):
        """Check for information disclosure risks."""
        field_name = node.name.value
        
        # Check for introspection
        if field_name.startswith("__"):
            self.has_introspection = True
            self.introspection_fields.append(field_name)
        
        # Check for sensitive fields
        for pattern in self.sensitive_patterns:
            if re.match(pattern, field_name, re.IGNORECASE):
                self.sensitive_fields.append(field_name)


class FieldAccessAnalyzer(Visitor):
    """Analyzes field access patterns for anomalies."""
    
    def __init__(self):
        self.has_enumeration_pattern = False
        self.enumeration_indicators = []
        self.operation_count = 0
        self.id_field_count = 0
    
    def enter_operation_definition(self, node: ast.OperationDefinitionNode, *_):
        """Count operations."""
        self.operation_count += 1
    
    def enter_field(self, node: ast.FieldNode, *_):
        """Analyze field access."""
        field_name = node.name.value
        
        # Check for ID enumeration
        if field_name.lower() in ["id", "uuid", "identifier"]:
            self.id_field_count += 1
        
        # Check for enumeration patterns
        if self.id_field_count > 5:
            self.has_enumeration_pattern = True
            self.enumeration_indicators.append(f"High ID field access count: {self.id_field_count}")


class SecurityRuleEngine:
    """
    Advanced security rule engine for custom threat detection.
    
    Allows defining custom security rules that can be applied
    to GraphQL operations for organization-specific security requirements.
    """
    
    def __init__(self):
        self.rules: List[SecurityRule] = []
        self.rule_cache: Dict[str, bool] = {}
    
    def add_rule(self, rule: 'SecurityRule'):
        """Add a security rule to the engine."""
        self.rules.append(rule)
    
    def evaluate_rules(
        self, 
        document: DocumentNode, 
        variables: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[SecurityThreat]:
        """Evaluate all rules against a GraphQL operation."""
        threats = []
        
        for rule in self.rules:
            try:
                if rule.evaluate(document, variables, context):
                    threats.append(SecurityThreat(
                        threat_type=rule.threat_type,
                        threat_level=rule.threat_level,
                        description=rule.description,
                        details=rule.get_details(document, variables, context)
                    ))
            except Exception as e:
                logger.error(f"Error evaluating security rule {rule.name}: {e}")
        
        return threats


@dataclass
class SecurityRule:
    """Base class for custom security rules."""
    
    name: str
    threat_type: str
    threat_level: ThreatLevel
    description: str
    enabled: bool = True
    
    def evaluate(
        self, 
        document: DocumentNode, 
        variables: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Evaluate the rule against a GraphQL operation.
        
        Returns:
            True if the rule is violated (threat detected)
        """
        raise NotImplementedError("Subclasses must implement evaluate method")
    
    def get_details(
        self, 
        document: DocumentNode, 
        variables: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get additional details about the threat."""
        return {"rule_name": self.name}


class QueryAnalyzer:
    """
    High-level GraphQL query analyzer that orchestrates all security checks.
    
    This is the main entry point for GraphQL security analysis.
    """
    
    def __init__(self):
        self.validator = GraphQLSecurityValidator()
        self.rule_engine = SecurityRuleEngine()
        self._setup_default_rules()
    
    def analyze(
        self, 
        document: DocumentNode, 
        variables: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Perform comprehensive analysis of a GraphQL query.
        
        Args:
            document: GraphQL document to analyze
            variables: Query variables
            context: Additional context
            
        Returns:
            ValidationResult with complete security analysis
        """
        # Run security validation
        result = self.validator.validate_query(document, variables, context)
        
        # Apply custom rules
        custom_threats = self.rule_engine.evaluate_rules(document, variables, context)
        result.threats.extend(custom_threats)
        
        # Re-evaluate overall validity
        result.is_valid = not (result.has_critical_threats or result.has_high_threats)
        
        return result
    
    def _setup_default_rules(self):
        """Setup default security rules."""
        # Add built-in security rules here
        pass


def create_security_validator() -> QueryAnalyzer:
    """Create a configured security validator instance."""
    return QueryAnalyzer() 