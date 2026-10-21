pipeline {
  agent any
  options { timestamps() }
  stages {
    stage('Python') {
      steps {
        sh '''
          python3 -m venv .venv
          . .venv/bin/activate
          pip install -e ".[dev]"
          ruff check src tests
          pytest
        '''
      }
    }
    stage('Go gateway') {
      steps {
        dir('services/mesh-gateway') {
          sh 'go test ./...'
        }
      }
    }
    stage('TypeScript MCP') {
      steps {
        dir('mcp/pipefish-mesh') {
          sh 'node --experimental-strip-types --test src/index.test.ts'
        }
      }
    }
  }
}
