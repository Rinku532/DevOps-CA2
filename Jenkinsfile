pipeline {
    agent any

    environment {
        // Python virtual environment path
        VENV_DIR = "${WORKSPACE}/venv"
        // GitHub repository
        REPO_URL = 'https://github.com/Rinku532/DevOps-CA2.git'
    }

    stages {

        // ── Stage 1: Checkout source code from GitHub ──────────────────────
        stage('Checkout') {
            steps {
                echo '=== Checking out source code from GitHub ==='
                git branch: 'main',
                    url: 'https://github.com/Rinku532/DevOps-CA2.git'
            }
        }

        // ── Stage 2: Set up Python virtual environment ─────────────────────
        stage('Setup Python Environment') {
            steps {
                echo '=== Setting up Python virtual environment ==='
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                '''
            }
        }

        // ── Stage 3: Install dependencies ──────────────────────────────────
        stage('Install Dependencies') {
            steps {
                echo '=== Installing Python dependencies from requirements.txt ==='
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        // ── Stage 4: Run Selenium tests ────────────────────────────────────
        stage('Run Selenium Tests') {
            steps {
                echo '=== Running Selenium test suite with pytest ==='
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pytest tests/test_feedback_form.py \
                        -v \
                        --tb=short \
                        --junit-xml=test-results/results.xml \
                        --no-header
                '''
            }
        }
    }

    // ── Post-build actions ──────────────────────────────────────────────────
    post {
        always {
            echo '=== Publishing test results ==='
            // Publish JUnit XML report in Jenkins UI
            junit allowEmptyResults: true, testResults: 'test-results/results.xml'
        }

        success {
            echo '✅ BUILD SUCCESS — All Selenium tests passed!'
        }

        failure {
            echo '❌ BUILD FAILED — One or more Selenium tests failed. Check the test report above.'
        }
    }
}
