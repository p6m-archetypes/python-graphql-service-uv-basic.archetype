#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TEST_SERVICE_NAME="test-validation-service"
TEST_ORG="test.example"
TEST_SOLUTION="test-python-graphql-service"
TEST_PREFIX="test"
TEST_SUFFIX="service"
MAX_STARTUP_TIME=120 # 2 minutes in seconds
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_DIR="$(mktemp -d)"
VALIDATION_LOG="$TEMP_DIR/validation.log"

# Cleanup function - DISABLED FOR DEBUGGING
cleanup() {
    echo -e "${BLUE}NOT cleaning up for debugging...${NC}"
    echo -e "${YELLOW}Generated service directory: $TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX${NC}"
    if [ -d "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX" ]; then
        cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
        if [ -f "docker-compose.yml" ]; then
            echo -e "${YELLOW}To manually clean up later, run:${NC}"
            echo -e "${YELLOW}cd $TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX && docker-compose down --volumes --remove-orphans${NC}"
        fi
    fi
    # rm -rf "$TEMP_DIR"  # DISABLED
}

# Trap cleanup on exit
trap cleanup EXIT

# Logging function
log() {
    echo -e "$1" | tee -a "$VALIDATION_LOG"
}

# Success/Failure tracking
TESTS_PASSED=0
TESTS_FAILED=0

test_result() {
    if [ $1 -eq 0 ]; then
        log "${GREEN}✅ $2${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log "${RED}❌ $2${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    log "${BLUE}Checking prerequisites...${NC}"
    
    local missing_deps=()
    
    if ! command_exists archetect; then
        missing_deps+=("archetect")
    fi
    
    if ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists docker-compose; then
        missing_deps+=("docker-compose")
    fi
    
    if ! command_exists uv; then
        missing_deps+=("uv")
    fi
    
    if ! command_exists curl; then
        missing_deps+=("curl")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log "${RED}Missing required dependencies: ${missing_deps[*]}${NC}"
        log "${YELLOW}Please install the missing dependencies and try again.${NC}"
        exit 1
    fi
    
    test_result 0 "All prerequisites available"
}

# Generate test service from archetype
generate_test_service() {
    log "\n${BLUE}Generating test service from archetype...${NC}"
    
    cd "$TEMP_DIR"
    
    # Copy the test answers file from the archetype
    if [ -f "$SCRIPT_DIR/test_answers_complete.yaml" ]; then
        cp "$SCRIPT_DIR/test_answers_complete.yaml" ./test_answers.yaml
        test_result 0 "Test answers file copied successfully"
    else
        log "${RED}Test answers file not found at $SCRIPT_DIR/test_answers_complete.yaml${NC}"
        # Create minimal answers file as fallback
        cat > test_answers.yaml << EOF
# Fallback answer file for archetype validation testing
project: "$TEST_SERVICE_NAME"
description: "Test Python GraphQL service with UV for validation testing"
version: "1.0.0"
author_full: "Validation Test Suite"
prefix-name: "$TEST_PREFIX"
suffix-name: "$TEST_SUFFIX"
org-name: "$TEST_ORG"
solution-name: "$TEST_SOLUTION"
prefix_name: "$TEST_PREFIX"
suffix_name: "$TEST_SUFFIX"
org_name: "$TEST_ORG"
solution_name: "$TEST_SOLUTION"
EOF
        test_result 1 "Using fallback test answers file"
    fi
    
    # Generate the service using render command
    if archetect render "$SCRIPT_DIR" --answer-file test_answers.yaml "$TEST_SERVICE_NAME" >> "$VALIDATION_LOG" 2>&1; then
        test_result 0 "Archetype generation successful"
    else
        test_result 1 "Archetype generation failed"
        return 1
    fi
    
    # Verify the generated structure
    if [ -d "$TEST_SERVICE_NAME" ]; then
        test_result 0 "Generated service directory exists"
    else
        test_result 1 "Generated service directory missing"
        return 1
    fi
    
    # Remove any stale lock files that came with the archetype
    log "${YELLOW}Removing any stale lock files...${NC}"
    cd "$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    find . -name "uv.lock" -delete 2>/dev/null || true
    cd ../..
}

# Run template validation
validate_template_substitution() {
    log "\n${BLUE}Validating template variable substitution...${NC}"
    
    cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    
    # Track validation issues
    local template_issues=0
    local error_details=""
    
    # Check for unreplaced template variables
    local unreplaced=$(grep -r "{{ prefix\|{{ suffix\|{{ org" . --exclude-dir=.git --exclude="*.pyc" 2>/dev/null | wc -l)
    if [ "$unreplaced" -gt 0 ]; then
        log "${RED}Found $unreplaced unreplaced template variables:${NC}"
        grep -r "{{ prefix\|{{ suffix\|{{ org" . --exclude-dir=.git --exclude="*.pyc" 2>/dev/null | head -5
        if [ "$unreplaced" -gt 5 ]; then
            log "${YELLOW}... and $((unreplaced - 5)) more${NC}"
        fi
        template_issues=1
        error_details="${error_details}- Unreplaced template variables ($unreplaced found)\n"
    fi
    
    # Check for unexpected gRPC references (allow GraphQL terms)
    local grpc_refs=$(grep -r "grpc" . --exclude-dir=.git --exclude="*.pyc" --exclude-dir=.venv 2>/dev/null | grep -v "graphql" | grep -v "# GraphQL uses protocols" | wc -l)
    if [ "$grpc_refs" -gt 0 ]; then
        log "${RED}Found $grpc_refs unexpected gRPC references (excluding GraphQL terms):${NC}"
        grep -r "grpc" . --exclude-dir=.git --exclude="*.pyc" --exclude-dir=.venv 2>/dev/null | grep -v "graphql" | grep -v "# GraphQL uses protocols" | head -3
        if [ "$grpc_refs" -gt 3 ]; then
            log "${YELLOW}... and $((grpc_refs - 3)) more${NC}"
        fi
        template_issues=1
        error_details="${error_details}- gRPC references still present ($grpc_refs found)\n"
    fi
    
    # Check for unexpected protobuf references (allow protocol terms)
    local proto_refs=$(grep -r "proto" . --exclude-dir=.git --exclude="*.pyc" --exclude-dir=.venv 2>/dev/null | grep -v "protocol" | grep -v "# GraphQL protocols allowed" | wc -l)
    if [ "$proto_refs" -gt 0 ]; then
        log "${RED}Found $proto_refs unexpected protobuf references (excluding protocol terms):${NC}"
        grep -r "proto" . --exclude-dir=.git --exclude="*.pyc" --exclude-dir=.venv 2>/dev/null | grep -v "protocol" | grep -v "# GraphQL protocols allowed" | head -3
        if [ "$proto_refs" -gt 3 ]; then
            log "${YELLOW}... and $((proto_refs - 3)) more${NC}"
        fi
        template_issues=1
        error_details="${error_details}- Protobuf references still present ($proto_refs found)\n"
    fi
    
    # Check for proper GraphQL endpoint patterns
    local graphql_endpoints=$(grep -r "/graphql\|strawberry\|GraphQL" . --exclude-dir=.git --exclude="*.pyc" 2>/dev/null | wc -l)
    if [ "$graphql_endpoints" -eq 0 ]; then
        log "${RED}Missing expected GraphQL endpoint patterns${NC}"
        template_issues=1
        error_details="${error_details}- No GraphQL endpoints found\n"
    fi
    
    # Report results with proper logic (0 = success, 1 = failure)
    if [ $template_issues -eq 0 ]; then
        test_result 0 "Template validation passed - archetype generated correctly"
    else
        log "${RED}Template validation issues found:${NC}"
        log -e "${error_details}"
        test_result 1 "Template validation failed - archetype needs fixes before use"
        return 1
    fi
}

# Test UV sync on all packages
test_uv_sync() {
    log "\n${BLUE}Testing UV sync on all packages...${NC}"
    
    cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    
    local sync_failed=0
    
    # Find all pyproject.toml files and sync each package
    while IFS= read -r -d '' pyproject_file; do
        package_dir=$(dirname "$pyproject_file")
        package_name=$(basename "$package_dir")
        
        log "${YELLOW}Syncing package: $package_name${NC}"
        
        if (cd "$package_dir" && uv sync >> "$VALIDATION_LOG" 2>&1); then
            log "${GREEN}  ✅ $package_name sync successful${NC}"
        else
            log "${RED}  ❌ $package_name sync failed${NC}"
            sync_failed=1
        fi
    done < <(find . -name "pyproject.toml" -print0)
    
    test_result $sync_failed "UV sync on all packages"
}

# Validate generated lock files are clean
validate_lock_files() {
    log "\n${BLUE}Validating generated UV lock files...${NC}"
    
    cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    
    # Count gRPC and protobuf references in lock files
    local lock_grpc_refs=0
    local lock_proto_refs=0
    
    if find . -name "uv.lock" | head -1 > /dev/null 2>&1; then
        lock_grpc_refs=$(find . -name "uv.lock" -exec grep -l "grpc" {} \; 2>/dev/null | wc -l)
        lock_proto_refs=$(find . -name "uv.lock" -exec grep -l "protobuf\|proto.*=" {} \; 2>/dev/null | wc -l)
        
        local lock_issues=0
        
        if [ "$lock_grpc_refs" -gt 0 ]; then
            log "${RED}Found gRPC dependencies in $lock_grpc_refs lock files${NC}"
            find . -name "uv.lock" -exec grep -l "grpc" {} \; 2>/dev/null | head -3
            lock_issues=1
        fi
        
        if [ "$lock_proto_refs" -gt 0 ]; then
            log "${RED}Found protobuf dependencies in $lock_proto_refs lock files${NC}"
            find . -name "uv.lock" -exec grep -l "protobuf\|proto.*=" {} \; 2>/dev/null | head -3
            lock_issues=1
        fi
        
        if [ $lock_issues -eq 0 ]; then
            test_result 0 "Generated lock files are clean (no gRPC/protobuf dependencies)"
        else
            test_result 1 "Generated lock files contain stale gRPC/protobuf dependencies"
            return 1
        fi
    else
        log "${YELLOW}No lock files found to validate${NC}"
        test_result 0 "No lock files to validate"
    fi
}

# Test Docker build and startup
test_docker_stack() {
    log "\n${BLUE}Testing Docker stack build and startup...${NC}"
    
    cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    
    # Build the Docker stack - SHOW OUTPUT TO TERMINAL
    echo -e "${YELLOW}Running: docker-compose build${NC}"
    echo -e "${YELLOW}Working directory: $(pwd)${NC}"
    if docker-compose build 2>&1 | tee -a "$VALIDATION_LOG"; then
        test_result 0 "Docker build successful"
    else
        test_result 1 "Docker build failed"
        echo -e "${RED}Docker build failed. Generated service is at: $TEMP_DIR/$TEST_SERVICE_NAME${NC}"
        return 1
    fi
    
    # Start the stack
    log "${YELLOW}Starting Docker stack...${NC}"
    echo -e "${YELLOW}Running: docker-compose up -d${NC}"
    if docker-compose up -d 2>&1 | tee -a "$VALIDATION_LOG"; then
        test_result 0 "Docker stack started"
    else
        test_result 1 "Docker stack failed to start"
        return 1
    fi
    
    # Wait for services to be ready and measure startup time
    local start_time=$(date +%s)
    local max_wait=60
    local waited=0
    
    log "${YELLOW}Waiting for services to be ready...${NC}"
    
    while [ $waited -lt $max_wait ]; do
        if docker-compose ps | grep -q "Up"; then
            local end_time=$(date +%s)
            local startup_time=$((end_time - start_time))
            log "${GREEN}Services ready in ${startup_time} seconds${NC}"
            
            if [ $startup_time -le $MAX_STARTUP_TIME ]; then
                test_result 0 "Service startup time within 2 minutes ($startup_time seconds)"
            else
                test_result 1 "Service startup time exceeded 2 minutes ($startup_time seconds)"
            fi
            break
        fi
        sleep 2
        waited=$((waited + 2))
    done
    
    if [ $waited -ge $max_wait ]; then
        test_result 1 "Services failed to start within timeout"
        return 1
    fi
}

# Test GraphQL service connectivity
test_service_connectivity() {
    log "\n${BLUE}Testing GraphQL service connectivity...${NC}"
    
    cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    
    # Test GraphQL endpoint with introspection query
    if curl -s --connect-timeout 5 -X POST http://localhost:8080/graphql \
        -H "Content-Type: application/json" \
        -d '{"query": "{ __schema { queryType { name } } }"}' | grep -q "queryType" 2>/dev/null; then
        test_result 0 "GraphQL endpoint accessible and responding"
    else
        test_result 1 "GraphQL endpoint not accessible or not responding"
    fi
    
    # Test health endpoint
    if curl -s --connect-timeout 5 http://localhost:8080/health | grep -q "healthy" 2>/dev/null; then
        test_result 0 "Health endpoint accessible"
    else
        test_result 1 "Health endpoint not accessible"
    fi
    
    # Test OpenAPI docs endpoint
    if curl -s --connect-timeout 5 http://localhost:8080/docs >/dev/null 2>&1; then
        test_result 0 "OpenAPI docs endpoint accessible"
    else
        test_result 1 "OpenAPI docs endpoint not accessible"
    fi
    
    # Test management health endpoint
    if curl -s --connect-timeout 5 http://localhost:8080/health >/dev/null 2>&1; then
        test_result 0 "Management health endpoint accessible"
    else
        test_result 1 "Management health endpoint not accessible"
    fi
    
    # Test metrics endpoint
    if curl -s --connect-timeout 5 http://localhost:8080/metrics | grep -q "python_" 2>/dev/null; then
        test_result 0 "Metrics endpoint accessible and contains metrics"
    else
        test_result 1 "Metrics endpoint not accessible or missing metrics"
    fi
}

# Test GraphQL operations
test_graphql_operations() {
    log "\n${BLUE}Testing GraphQL operations...${NC}"
    
    # Test GraphQL ping query
    if curl -s --connect-timeout 5 -X POST http://localhost:8080/graphql \
        -H "Content-Type: application/json" \
        -d '{"query": "{ ping }"}' | grep -q "pong" 2>/dev/null; then
        test_result 0 "GraphQL ping query working"
    else
        test_result 1 "GraphQL ping query not working properly"
    fi
    
    # Test GraphQL schema introspection
    if curl -s --connect-timeout 5 -X POST http://localhost:8080/graphql \
        -H "Content-Type: application/json" \
        -d '{"query": "{ __schema { types { name } } }"}' | grep -q "types" 2>/dev/null; then
        test_result 0 "GraphQL schema introspection working"
    else
        test_result 1 "GraphQL schema introspection not working"
    fi
}

# Test monitoring infrastructure
test_monitoring() {
    log "\n${BLUE}Testing monitoring infrastructure...${NC}"
    
    cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    
    # Test Prometheus
    if curl -s --connect-timeout 10 http://localhost:9090/-/healthy >/dev/null 2>&1; then
        test_result 0 "Prometheus accessible"
    else
        test_result 1 "Prometheus not accessible"
    fi
    
    # Test Grafana
    if curl -s --connect-timeout 10 http://localhost:3000/api/health | grep -q "ok" 2>/dev/null; then
        test_result 0 "Grafana accessible"
    else
        test_result 1 "Grafana not accessible"
    fi
}

# Run integration tests
run_integration_tests() {
    log "\n${BLUE}Running integration tests...${NC}"
    
    cd "$TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX"
    
    if [ -f "scripts/run-integration-tests.sh" ]; then
        # Make the script executable
        chmod +x scripts/run-integration-tests.sh
        
        if ./scripts/run-integration-tests.sh >> "$VALIDATION_LOG" 2>&1; then
            test_result 0 "Integration tests passed"
        else
            test_result 1 "Integration tests failed"
            return 1
        fi
    else
        log "${YELLOW}Integration test script not found, creating basic test...${NC}"
        
        # Create a basic integration test
        mkdir -p scripts
        cat > scripts/run-integration-tests.sh << 'EOF'
#!/bin/bash
# Basic integration test for GraphQL service
echo "Running basic GraphQL service integration test..."

# Test service is responding
if curl -s --connect-timeout 5 http://localhost:8080/health > /dev/null; then
    echo "✅ Service health check passed"
else
    echo "❌ Service health check failed"
    exit 1
fi

# Test GraphQL endpoint
if curl -s --connect-timeout 5 -X POST http://localhost:8080/graphql \
    -H "Content-Type: application/json" \
    -d '{"query": "{ ping }"}' | grep -q "pong" > /dev/null; then
    echo "✅ GraphQL endpoint accessible"
else
    echo "❌ GraphQL endpoint not accessible"
    exit 1
fi

echo "✅ Basic integration tests passed"
EOF
        chmod +x scripts/run-integration-tests.sh
        
        if ./scripts/run-integration-tests.sh >> "$VALIDATION_LOG" 2>&1; then
            test_result 0 "Basic integration tests passed"
        else
            test_result 1 "Basic integration tests failed"
            return 1
        fi
    fi
}

# Main validation workflow
main() {
    log "${BLUE}========================================${NC}"
    log "${BLUE}Python GraphQL Service Archetype Validation${NC}"
    log "${BLUE}========================================${NC}"
    log "Validation log: $VALIDATION_LOG"
    log "Temp directory: $TEMP_DIR"
    log "${YELLOW}Generated service will be at: $TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX${NC}"
    
    local overall_start_time=$(date +%s)
    
    # Run all validation steps
    check_prerequisites || exit 1
    generate_test_service || exit 1
    validate_template_substitution || exit 1
    
    # Check if we should stop after generation for debugging
    if [ "$1" = "--generate-only" ]; then
        log "\n${YELLOW}Stopping after generation as requested. Service generated at: $TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX${NC}"
        return 0
    fi
    
    log "\n${BLUE}Starting end-to-end timing measurement...${NC}"
    local e2e_start_time=$(date +%s)
    
    test_uv_sync  # Allow individual package sync failures for local dependency packages
    validate_lock_files || exit 1
    test_docker_stack || exit 1
    test_service_connectivity || exit 1
    test_graphql_operations || exit 1
    test_monitoring || exit 1
    run_integration_tests || exit 1
    
    local e2e_end_time=$(date +%s)
    local e2e_total_time=$((e2e_end_time - e2e_start_time))
    
    log "\n${BLUE}End-to-end time (sync + build + start + test): ${e2e_total_time} seconds${NC}"
    
    if [ $e2e_total_time -le $MAX_STARTUP_TIME ]; then
        test_result 0 "End-to-end workflow within 2 minutes ($e2e_total_time seconds)"
    else
        test_result 1 "End-to-end workflow exceeded 2 minutes ($e2e_total_time seconds)"
    fi
    
    local overall_end_time=$(date +%s)
    local total_time=$((overall_end_time - overall_start_time))
    
    # Final summary
    log "\n${BLUE}========================================${NC}"
    log "${BLUE}Validation Summary${NC}"
    log "${BLUE}========================================${NC}"
    log "Total tests: $((TESTS_PASSED + TESTS_FAILED))"
    log "${GREEN}Passed: $TESTS_PASSED${NC}"
    log "${RED}Failed: $TESTS_FAILED${NC}"
    log "Total validation time: $total_time seconds"
    log "End-to-end workflow time: $e2e_total_time seconds"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        log "\n${GREEN}🎉 All validation tests passed! GraphQL archetype is ready for release.${NC}"
        log "${YELLOW}Generated service directory preserved at: $TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX${NC}"
        return 0
    else
        log "\n${RED}❌ Validation failed. Please check the issues above.${NC}"
        log "${YELLOW}Validation log available at: $VALIDATION_LOG${NC}"
        log "${YELLOW}Generated service directory preserved at: $TEMP_DIR/$TEST_SERVICE_NAME/$TEST_PREFIX-$TEST_SUFFIX${NC}"
        return 1
    fi
}

# Run main function
main "$@" 